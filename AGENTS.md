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

## Agent-monitored pull requests

Mac set this on 2026-09-26 for every repository. The `agent-monitored-pr` label marks a PR that an agent watches until it merges or closes. A labelled PR comes before other work, and its fixes run in parallel wherever that is safe.

- **Label every PR an agent opens.** Pass `--label agent-monitored-pr` to `gh pr create`. If the repository has no such label, create it first: `gh label create agent-monitored-pr --color fd0880 --description "Agent polls every 60 seconds fixes CI, comments, conflicts."`
- **Poll the PR every 60 seconds.** Each poll reads the PR's state, its mergeability, the checks on the head commit, and every review thread with no inline reply after the reviewer's last comment. `gh pr view --json` does not return review threads, so read them with `gh api graphql` (`pullRequest.reviewThreads`).
- **Fix by review pass.** Pass N is the Nth review one reviewer submits on the PR. On pass 1, fix every P0, P1, and P2 finding. On pass 2, fix P0 and P1. From pass 3 on, fix P0 only. A P0 blocks the PR at every pass.
- **File one residue issue.** Carry every P1 and P2 finding left unfixed into a single issue for the PR. Its title ends with `(residue #<PR>)`, and its body links the PR. Reply inline on every thread you handle, with the commit that fixed it or a link to the residue issue.
- **Clear conflicts and CI failures as they appear.** When the PR conflicts, merge the base branch in, resolve it, and push. When a job fails, read its failing step with `gh run view --job <id> --log-failed`, fix it, and push without waiting for the rest of the run.
- **Dispatch subagents.** Give each independent fix its own subagent when no two fixes touch the same file. Stay active until the PR merges or closes.
- **Search for the label every 60 seconds.** A session that watches PRs runs `gh search prs --owner macanderson --label agent-monitored-pr --state open` every 60 seconds and takes each labelled PR that no live session owns. A PR has one writer. Two writers on one branch restart each other's CI and reject each other's pushes, so check `~/.claude/jobs/*/state.json` for an owner first, and message that session instead of pushing to its branch.
