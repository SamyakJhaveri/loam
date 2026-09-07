# Parallel workers and handoffs

Read on demand. None of this is loaded in a normal session.

## Worktrees

Give each parallel worker its own worktree (`claude --worktree <name>`). One
checkout is safe only for disjoint files. For a shared GPU or database, wrap the
command in `flock /tmp/<resource>.lock <cmd>` (util-linux; absent on stock
macOS). Build no other lock.

## Roles

Parallel work has one integration owner and one validation owner. Workers run
focused checks and return bounded reports; only the validation owner runs
`bin/check` on a given source snapshot. Reviewers inspect one fixed diff and do
not rerun an unchanged suite unless they name a concrete unresolved risk.

## HANDOFF.md

Before stopping mid-task, write `HANDOFF.md` at the repo root with these seven
headings, in this order:

1. Goal
2. Files touched
3. Commands run (each with its exit code, including the `bin/check` run)
4. Tried and failed
5. Open assumptions
6. Next single action
7. Written at (the output of `git rev-parse HEAD`)

`/catchup` reads it on resume and calls it stale when that hash is no longer
HEAD, when its mtime predates the last commit, or when its status words
contradict git. It is gitignored and local-only; delete it when the task ends.

Keep it bounded: cite file sections and command summaries instead of pasting
whole files or logs. The repository state wins over the handoff.

A worker brief and its report use the same seven headings, so an interrupted
worker's findings are read from its report, never rebuilt from a transcript.
