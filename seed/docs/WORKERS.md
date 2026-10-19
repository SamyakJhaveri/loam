# Parallel workers and handoffs

Read on demand. None of this is loaded in a normal session.

## Worktrees

Give each parallel worker its own worktree (`claude --worktree <name>`). One
checkout is safe only for disjoint files. For a shared GPU or database, wrap the
command in `flock /tmp/<resource>.lock <cmd>` (util-linux; absent on stock
macOS). Build no other lock.

## Roles

Parallel work has one integration owner and one independent verifier per merge.
Each worker runs `bin/check` on its own unit before it reports; a fresh project's
check takes under a second. Once the suite takes minutes, workers run focused
checks and only the verifier runs the full `bin/check` on a source snapshot.
Reviewers inspect one fixed diff and do not rerun an unchanged suite unless they
name a concrete unresolved risk.

## Handoff

Before stopping mid-task, commit uncommitted edits as one `wip:` commit on the
current branch; if the tree is broken, say so in one line of the commit body.
`.loam/memory` is the link to the memory store that the first session capture
makes. If it does not exist yet, make the link first; a plain directory there
hides the note from recall and stops capture from ever linking it:

    mkdir -p "${LOAM_MEMSTORE:-$HOME/memstore}" .loam && ln -s "${LOAM_MEMSTORE:-$HOME/memstore}" .loam/memory

Then write `.loam/memory/handoff/<repo>.md` with these seven headings, in this
order:

1. Goal
2. Files touched
3. Commands run (each with its exit code, including the `bin/check` run)
4. Tried and failed
5. Open assumptions
6. Next single action
7. Written at (the output of `git rev-parse HEAD`, after the `wip:` commit)

The next session on any machine injects it once at startup and archives it
under `.loam/memory/handoff/<repo>/archive/`; `docs/HARNESS.md` (The handoff)
names the repo key. Treat it as stale when that hash is no longer HEAD or its
status words contradict git.

Keep it under 1500 bytes, the most recall injects: cite file sections and
command summaries instead of pasting whole files or logs. The repository state
wins over the handoff.

A worker brief and its report use the same seven headings, so an interrupted
worker's findings are read from its report, never rebuilt from a transcript.

## Project checks

`bin/check` carries a Project checks stage for the checks this project adds. Add
a check at the second recurrence of a pattern the docs already ban, so the
correction becomes a failure the agent cannot argue with. Keep each check one
line, deterministic, and named. Never add a check that cannot fail. A check that
only restates prose is a duplicate; remove it.
