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

## Red flags - put these at the TOP of the briefing

- Uncommitted changes or a detached HEAD.
- A merge or rebase in progress.
- Active tmux sessions that may be running long jobs.
- Memory files untouched for 14+ days.
- In-progress tasks from a previous session.

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
Open tasks (or: none)
=== END BRIEFING ===
```
