# AGENTS.md

## Local execution

Mac set this on 2026-09-26 for every repository on this machine. Local builds, test runs, dev servers, and git hooks ran the laptop out of memory and killed agent runs partway through, and every killed run costs money. CI is the only place code is built, checked, or tested.

- Do not run the gate, a build, a typecheck, a lint, or any test, not even one test file. Push the branch and read the CI result. Read a failed job with `gh run view --job <id> --log-failed`.
- Do not start a dev server: no `next dev`, `next start`, `pnpm dev`, a server under `cargo run`, or anything else that listens on a port.
- Do not start Docker or Colima, and do not run anything that needs them.
- Do not run Biome in any form.
- Git hooks are off on this machine. `LEFTHOOK=0` and `HUSKY=0` are set for every shell and every Claude Code session. Do not reinstall a hook, turn one back on, or run a hook's commands by hand.
- Code generators and small integrity scripts that only read and write files are allowed, such as regenerating a checksum, a schema index, or a message catalogue.
- Put this rule, word for word, in the prompt of every subagent you start.

## Issue fields and reflection

Mac set this on 2026-09-28 for every repository. Every issue in Mac's repositories belongs on the `All issues` project board in the `macanderson` account. The board carries six fields. Keep all six correct on every issue you work on.

| Field | Values | Meaning |
|---|---|---|
| Prompt | Text | The prompt that starts an agent on the work |
| Model Tier | Ultra, Pro, Standard, Lite | The model tier the work needs |
| Size | XS, S, M, L, XL | The size of the change |
| `agent_mins_est` | Number | Agent minutes the work should take |
| `agent_mins` | Number | Agent minutes the work took |
| Resolution | Shipped, Won't ship, Duplicate | How the issue closed |

- **Add the issue to the board when you file it.** Set Prompt, Model Tier, and `agent_mins_est` at the same time. Set Size too, unless a triage rule in this repository gives sizing to the triage agent.
- **Stamp your minutes when your run ends.** Add the minutes your run spent on the issue to `agent_mins`. Add to the value already there, because several runs can share one issue.
- **Write a reflection when your run ends.** Post it as a comment on the issue. Give your run's minutes, say what shipped, compare `agent_mins` with `agent_mins_est`, and say what the next agent should know. The reflections are the record of minutes. If two runs write `agent_mins` at once and one value is lost, rebuild the sum from the reflections.
- **Set Resolution when the issue closes.**
- **Fix any field you find wrong** on any issue you touch.
- **Use the reflection until the board exists.** If `gh project list` shows no `All issues` board, or your token lacks the `project` scope, write the six values in the reflection instead. Copy them to the board once it exists.

These commands find the board and set a field:

```sh
gh project list --owner macanderson                                  # the board titled "All issues"
gh project field-list <number> --owner macanderson --format json     # field and option ids
gh project item-add <number> --owner macanderson --url <issue-url> --format json --jq .id   # the item id
gh project item-edit --project-id <project-id> --id <item-id> --field-id <field-id> --number 42
```
## Agent-monitored pull requests

Mac set this on 2026-09-26 for every repository. The `agent-monitored-pr` label marks a PR that an agent watches until it merges or closes. A labelled PR comes before other work, and its fixes run in parallel wherever that is safe.

- **Label every PR an agent opens.** Pass `--label agent-monitored-pr` to `gh pr create`. If the repository has no such label, create it first: `gh label create agent-monitored-pr --color fd0880 --description "Agent polls every 60 seconds fixes CI, comments, conflicts."`
- **Poll the PR every 60 seconds.** Each poll reads the PR's state, its mergeability, and the checks on the head commit. It reads every review thread with no inline reply after the reviewer's last comment. `gh pr view --json` does not return review threads, so read them with `gh api graphql` (`pullRequest.reviewThreads`). It also reads review bodies and top-level comments, because a finding there has no thread. Answer each finding there once, with a PR comment that quotes it, and record the id of the comment you answered. Start every comment a watcher posts with `<!-- pr-watch -->`. Skip comments that start with that marker or with `<!-- pr-claim -->`, so a watcher does not answer its own comments.
- **Fix by review pass.** Pass N is the Nth review one reviewer submits on the PR. On pass 1, fix every P0, P1, and P2 finding. On pass 2, fix P0 and P1. From pass 3 on, fix P0 only. A P0 blocks the PR at every pass.
- **File one residue issue.** Carry every P1 and P2 finding left unfixed into a single issue for the PR. Its title ends with `(residue #<PR>)`, and its body links the PR. Reply inline on every thread you handle, with the commit that fixed it or a link to the residue issue.
- **Let the pass rule govern review findings.** On a labelled PR, the pass rule decides which review findings get fixed, in place of any repository rule on review rounds or on fixing every finding in the PR. Residue goes to one issue, even where a repository files each finding alone. Where a repository allows one change per issue, residue from unrelated changes splits into one issue per change. A defect you notice yourself still follows fix over file. A P3 finding follows the repository's usual rules.
- **Clear conflicts and CI failures as they appear.** When the PR conflicts, merge the base branch in, resolve it, and push. When a job fails, read its failing step with `gh run view --job <id> --log-failed`, fix it, and push without waiting for the rest of the run.
- **Dispatch subagents.** Give each independent fix its own subagent when no two fixes touch the same file. Stay active until the PR merges or closes.
- **Search for the label every 60 seconds.** A session that watches PRs runs `gh search prs --owner macanderson --owner oxageninc --label agent-monitored-pr --state open --limit 1000` every 60 seconds. Mac's repositories can sit under either owner, and a search of one owner misses the other's PRs. Without `--limit`, gh returns 30 results, and GitHub search returns at most 1000. The session takes each labelled PR that no live claim holds.
- **Claim a PR before the first write.** A PR has one writer. Two writers on one branch restart each other's CI and reject each other's pushes. To claim, post a PR comment whose first line is `<!-- pr-claim --> <login> <session-word> <runtime> <session name>`, then read the PR's comments again. The session word is one word that names your session, such as a job id. A claim holds for 90 minutes after it is posted. The oldest claim that still holds owns the PR. If that claim is not yours, delete your comment and message the owner instead of pushing. Before your claim lapses, post a new one and delete the old one. Delete your claim when you stop watching the PR. Agents chose this claim on 2026-09-26 to answer review findings, in the format of stella's `scripts/pr-claim.sh`, and Mac has not ruled on it.
