"""Tests for build/sync_supersede.py, which the fan-out runs before it closes an older sync PR.

    python3 -m unittest discover -s build -p "test_*.py"

CI runs these in the `check` job of `.github/workflows/ui.yml`. The git
cases build a throwaway repository in a temporary folder.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sync_supersede as S

BOT = S.BOT_EMAIL
#: A fixed identity and no user or system git config, for the throwaway repository.
GIT_ENV = {
    "GIT_AUTHOR_NAME": "Agent",
    "GIT_AUTHOR_EMAIL": "agent@example.com",
    "GIT_COMMITTER_NAME": "Agent",
    "GIT_COMMITTER_EMAIL": "agent@example.com",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def row(sha: str, email: str, message: str, parents: int = 1) -> dict:
    """A commit as `GET /repos/{repo}/pulls/{n}/commits` returns it."""
    return {
        "sha": sha,
        "commit": {"author": {"email": email}, "message": message},
        "parents": [{"sha": f"p{i}"} for i in range(parents)],
    }


class Classify(unittest.TestCase):
    def test_the_fanout_commit_is_its_own(self) -> None:
        self.assertTrue(S.fanout_wrote(S.Commit("a" * 40, BOT, "Sync the brand from oxagen-brand@187e871")))

    def test_a_person_or_another_message_is_carried(self) -> None:
        self.assertFalse(S.fanout_wrote(S.Commit("a" * 40, "agent@example.com", "Sync the brand from oxagen-brand@187e871")))
        self.assertFalse(S.fanout_wrote(S.Commit("a" * 40, BOT, "Read the type utilities in cn()")))

    def test_pr_commits_keep_order_and_drop_merges(self) -> None:
        rows = [
            row("1" * 40, BOT, "Sync the brand from oxagen-brand@187e871"),
            row("2" * 40, "agent@example.com", "Read the type utilities in cn()\n\nBody."),
            row("3" * 40, "agent@example.com", "Merge branch 'main' into brand/sync-187e871", parents=2),
            row("4" * 40, "agent@example.com", "Fix the type-scale test"),
        ]
        carried = S.to_carry(S.pr_commits(rows))
        self.assertEqual([c.subject for c in carried], ["Read the type utilities in cn()", "Fix the type-scale test"])
        self.assertEqual(carried[0].short, "2222222")

    def test_the_listing_names_each_commit(self) -> None:
        commits = [S.Commit("abcdef0123", "a@x", "One"), S.Commit("1234567890", "a@x", "Two")]
        self.assertEqual(S.listing(commits), "- abcdef0 One\n- 1234567 Two")


class CherryPick(unittest.TestCase):
    def setUp(self) -> None:
        # The script's own git calls inherit the environment, so patch it for
        # the test and restore it after.
        env = mock.patch.dict(os.environ, GIT_ENV)
        env.start()
        self.addCleanup(env.stop)
        self.dir = tempfile.TemporaryDirectory()
        self.root = self.dir.name
        self.git("init", "-q", "-b", "main")
        self.write("a.txt", "one\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Start")

    def tearDown(self) -> None:
        self.dir.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True).stdout

    def write(self, name: str, text: str) -> None:
        (Path(self.root) / name).write_text(text)

    def commit(self, name: str, text: str, message: str) -> S.Commit:
        self.write(name, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return S.Commit(self.git("rev-parse", "HEAD").strip(), "agent@example.com", message)

    def test_carried_commits_land_in_order(self) -> None:
        self.git("switch", "-q", "-c", "old")
        first = self.commit("b.txt", "fix\n", "First fix")
        second = self.commit("b.txt", "fix\nmore\n", "Second fix")
        self.git("switch", "-q", "main")
        self.git("switch", "-q", "-c", "new")
        self.commit("a.txt", "one\ntwo\n", "Sync the brand from oxagen-brand@0000000")
        self.assertIsNone(S.cherry_pick([first, second], cwd=self.root))
        log = self.git("log", "--format=%s", "-3").splitlines()
        self.assertEqual(log, ["Second fix", "First fix", "Sync the brand from oxagen-brand@0000000"])
        self.assertEqual((Path(self.root) / "b.txt").read_text(), "fix\nmore\n")

    def test_a_conflict_carries_nothing_and_leaves_head(self) -> None:
        self.git("switch", "-q", "-c", "old")
        fix = self.commit("a.txt", "one\nfrom the fix\n", "Fix a.txt")
        self.git("switch", "-q", "main")
        self.git("switch", "-q", "-c", "new")
        self.commit("a.txt", "one\nfrom the sync\n", "Sync the brand from oxagen-brand@0000000")
        head = self.git("rev-parse", "HEAD").strip()
        reason = S.cherry_pick([fix], cwd=self.root)
        self.assertIsNotNone(reason)
        self.assertIn(fix.short, reason or "")
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_nothing_to_carry_is_a_no_op(self) -> None:
        self.assertIsNone(S.cherry_pick([], cwd=self.root))


if __name__ == "__main__":
    unittest.main()
