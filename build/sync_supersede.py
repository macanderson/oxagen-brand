"""Close the sync PRs a new one supersedes, and carry any commit a person added.

    python3 build/sync_supersede.py --repo oxageninc/product --branch brand/sync-abc1234 \
        --url https://github.com/oxageninc/product/pull/123 [--dry-run]

The fan-out workflow (`.github/workflows/fan-out.yml`) runs this in a
consumer's checkout, right after it pushes a new `brand/sync-<sha>` branch
and opens its PR. Each older open `brand/sync-*` PR is superseded:

- If its branch holds only the commits the fan-out wrote, the PR closes and
  its branch is deleted, as before.
- If a person or an agent pushed a fix to it, those commits are cherry-picked
  onto the new branch, in order, and pushed. Both PRs get a comment that names
  each carried commit, and the old PR closes.
- If a cherry-pick conflicts, nothing is carried: the old PR and its branch
  stay open, and both PRs get a comment with the commit list and the reason.

On 2026-10-03 the fan-out closed product #5314 for #5323 and deleted its
branch, which held two fixes an agent had pushed by hand. Both were lost.
This script is why that cannot happen again.

The PR's commits come from the GitHub API, which lists the commits on the
branch that its base does not hold, so a shallow checkout is enough. A commit
is the fan-out's own when the bot wrote it with the message the workflow
uses, `Sync the brand from oxagen-brand@<sha>`. Every other commit is carried.
Merges are left out: a merge of the default branch brings nothing the new
branch lacks.

`--dry-run` reads the PRs and the commits, prints what it would do, and
changes nothing. Standard library only, plus `git` and `gh` on the PATH.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass

#: The identity and the message the fan-out commits with.
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BOT_MESSAGE = re.compile(r"^Sync the brand from oxagen-brand@[0-9a-f]{7,40}$")
SYNC_PREFIX = "brand/sync-"


@dataclass(frozen=True)
class Commit:
    sha: str
    email: str
    subject: str

    @property
    def short(self) -> str:
        return self.sha[:7]


def fanout_wrote(commit: Commit) -> bool:
    """Whether the fan-out wrote this commit: the bot, with the workflow's message."""
    return commit.email == BOT_EMAIL and bool(BOT_MESSAGE.match(commit.subject))


def to_carry(commits: list[Commit]) -> list[Commit]:
    """The commits a person or an agent added, oldest first."""
    return [c for c in commits if not fanout_wrote(c)]


def git(*args: str, check: bool = True, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=check, capture_output=True, text=True, cwd=cwd)


def pr_commits(rows: list[dict]) -> list[Commit]:
    """A PR's commits from `GET /repos/{repo}/pulls/{n}/commits`, oldest first, merges left out."""
    out = []
    for r in rows:
        if len(r.get("parents", [])) > 1:
            continue
        message = r["commit"]["message"]
        out.append(Commit(r["sha"], r["commit"]["author"]["email"], message.splitlines()[0] if message else ""))
    return out


def cherry_pick(commits: list[Commit], cwd: str | None = None) -> str | None:
    """Cherry-pick `commits` onto HEAD in order. Returns None, or the reason it stopped; HEAD is then unchanged."""
    if not commits:
        return None
    start = git("rev-parse", "HEAD", cwd=cwd).stdout.strip()
    for c in commits:
        done = git("cherry-pick", "-x", c.sha, check=False, cwd=cwd)
        if done.returncode != 0:
            git("cherry-pick", "--abort", check=False, cwd=cwd)
            git("reset", "--hard", start, cwd=cwd)
            detail = (done.stderr or done.stdout).strip().splitlines()
            return f"{c.short} ({c.subject}) does not apply: {detail[-1] if detail else 'cherry-pick failed'}"
    return None


def listing(commits: list[Commit]) -> str:
    return "\n".join(f"- {c.short} {c.subject}" for c in commits)


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def superseded(repo: str, branch: str) -> list[tuple[int, str]]:
    """The open sync PRs other than the new one, as (number, branch)."""
    rows = json.loads(gh("pr", "list", "--repo", repo, "--state", "open", "--json", "number,headRefName", "--limit", "100"))
    return [(r["number"], r["headRefName"]) for r in rows
            if r["headRefName"].startswith(SYNC_PREFIX) and r["headRefName"] != branch]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="the consumer, owner/name")
    ap.add_argument("--branch", required=True, help="the new sync branch, already pushed and checked out")
    ap.add_argument("--url", required=True, help="the new sync PR's URL")
    ap.add_argument("--dry-run", action="store_true", help="print what would happen and change nothing")
    a = ap.parse_args(argv)

    def act(*args: str) -> None:
        if a.dry_run:
            print("would run: gh", " ".join(args))
        else:
            gh(*args)

    carried_any = False
    for number, old in superseded(a.repo, a.branch):
        rows = json.loads(gh("api", "--paginate", "--slurp", f"repos/{a.repo}/pulls/{number}/commits"))
        commits = to_carry(pr_commits([r for page in rows for r in page]))
        if not commits:
            print(f"#{number} ({old}) holds only fan-out commits: closing it and deleting its branch.")
            act("pr", "close", str(number), "--repo", a.repo, "--delete-branch", "--comment", f"Superseded by {a.url}.")
            continue
        print(f"#{number} ({old}) holds {len(commits)} commit(s) the fan-out did not write:\n{listing(commits)}")
        reason = None
        if not a.dry_run:
            # The checkout is shallow. A sync branch is short, so its last 100
            # commits hold every commit to carry and the parent each applies on.
            git("fetch", "-q", "--depth=100", "origin", f"{old}:refs/remotes/origin/{old}")
            reason = cherry_pick(commits)
        if reason:
            note = (
                f"<!-- fan-out -->\nThe fan-out did not close #{number} for {a.url}, because its branch `{old}` holds "
                f"commits the fan-out did not write, and they do not apply to `{a.branch}`:\n\n{listing(commits)}\n\n"
                f"Reason: {reason}\n\nCarry them by hand, then close #{number}."
            )
            print(f"::warning::{reason}. #{number} stays open.")
            act("pr", "comment", str(number), "--repo", a.repo, "--body", note)
            act("pr", "comment", a.url, "--repo", a.repo, "--body", note)
            continue
        if not a.dry_run:
            git("push", "-q", "origin", f"HEAD:{a.branch}")
        carried_any = True
        note = (
            f"<!-- fan-out -->\nThe fan-out carried these commits from #{number} (`{old}`) onto `{a.branch}`, "
            f"in order, before closing #{number}:\n\n{listing(commits)}"
        )
        act("pr", "comment", a.url, "--repo", a.repo, "--body", note)
        act("pr", "close", str(number), "--repo", a.repo, "--delete-branch", "--comment",
            f"Superseded by {a.url}, which carries this branch's commits:\n\n{listing(commits)}")
    if carried_any:
        print("Carried commits onto the new sync branch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
