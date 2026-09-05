---
name: catchup
description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, environment state, memory-index staleness, pending tasks, and red flags (uncommitted changes, detached HEAD, stale memory). NOT for deep code exploration or planning - it only reports state, it does not change it.
---

# Session Catchup Briefing

Read the state before changing it. Report it; do not act on it.
Run everything fresh - never answer from cached or remembered state.
An optional numeric argument sets how many recent commits to show (default 10).

## Gather

1. Git: `git status`, `git log --oneline -<N>`, and `git diff --stat HEAD~<N>` (fall back to the first commit if history is short).
2. Environment: active tmux sessions (`tmux list-sessions`), python/venv presence if the project uses one.
3. Memory: list the project's auto-memory directory under `~/.claude/projects/<encoded-cwd>/memory/` by modification time.
4. Tasks: check the task list for anything left in progress by a previous session.
5. Handoff and state: read `HANDOFF.md`, and `STATE.md` if the project keeps one, at the repo root. `HANDOFF.md` uses seven headings, in order: Goal; Files touched; Commands run (each with its exit code); Tried and failed; Open assumptions; Next single action; Written at (the output of `git rev-parse HEAD`). The verify command that proves the work sits under Commands run. Note each file's modification time and its status words so freshness can be checked against git (see Red flags).
6. Loam pin: only when `.copier-answers.yml` exists at the repo root (the project was seeded from Loam). Read its `_commit`. It is a red flag when `_commit` does not match `^v[0-9]+\.[0-9]+\.[0-9]+$` (a bare SHA, or a `git describe` string such as `v2.1.0-39-g0d0cb03`, is not a release tag), or when it is not the newest tag. Find the newest tag with `git ls-remote --tags https://github.com/samyakjhaveri/loam` sorted by version, ignore lines ending in `^{}` (the `gh:` shorthand is Copier-only and fails in git). When that fails within a few seconds (offline), compare against `VERSION` in the template checkout (strip the leading v before comparing) only if `_src_path` points to a reachable local Loam checkout; otherwise print `pin check skipped: offline`.

## Red flags - put these at the TOP of the briefing

- Uncommitted changes or a detached HEAD.
- A merge or rebase in progress.
- Active tmux sessions that may be running long jobs.
- Memory files untouched for 14+ days.
- In-progress tasks from a previous session.
- A stale `HANDOFF.md` or `STATE.md`. Flag either file when any of these hold:
  - its modification time is older than the last commit: `git log -1 --format=%ct` versus the file's mtime (`stat -f %m <file>` on macOS, `stat -c %Y <file>` on Linux);
  - its status words contradict git: it says "uncommitted" or "dirty" while `git status --porcelain` is empty; or "clean" or "committed" while `git status --porcelain` is non-empty; or "pushed" while `git status -sb` shows the branch ahead of its upstream; or its "Written at" hash is not `git rev-parse HEAD`.
  Report the drift; the repository state overrides the handoff, never the reverse.
- Loam pin drift: print `Loam pin <commit> is not the latest release <tag>; run uvx copier update --trust` when the pin is behind the newest tag, or `Loam pin <commit> is not a release tag` when `_commit` is not a `vX.Y.Z` tag.

## Briefing format

Keep it to one screen. State only - the user decides what to do with it.

```
=== CATCHUP BRIEFING ===
[red flags, if any]
Branch / status / last commit
Recent commits (N)
Changed files since HEAD~N (diffstat)
Environment: tmux / venv / python
Memory: file count, most recent, stale list
Handoff / State: next single action + verify command (or: none; or: STALE - hash / mtime / status words disagree with git)
Loam pin: _commit + verdict (latest / not the latest / not a release tag / offline) - or: not a Loam project
Open tasks (or: none)
=== END BRIEFING ===
```
