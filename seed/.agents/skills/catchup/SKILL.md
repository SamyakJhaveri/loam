---
name: catchup
description: Read-only session bootstrap briefing of git state, commits, handoff, tasks and red flags. Use when resuming work, starting a fresh session, or unsure of project state.
---

# Session Catchup Briefing

Read the state before changing it. Report it; do not act on it.
Run everything fresh - never answer from cached or remembered state.
An optional numeric argument sets how many recent commits to show (default 10).

## Gather

1. Fixed checks: run `red-flags.sh`, which sits beside this file, from inside the repo. It prints one `FLAG:` line per red flag, a `Handoff:` line naming the handoff note to read, and a `Loam pin:` verdict line.
2. Git: `git status`, `git log --oneline -<N>`, and `git diff --stat HEAD~<N>` (fall back to the first commit if history is short).
3. Environment: active tmux sessions (`tmux list-sessions`), python/venv presence if the project uses one.
4. Memory: list the project's auto-memory directory under `~/.claude/projects/<encoded-cwd>/memory/` by modification time.
5. Tasks: check the task list for anything left in progress by a previous session.
6. Handoff and state: read the file on the `Handoff:` line (`docs/WORKERS.md` owns the handoff format), and `STATE.md` at the repo root if the project keeps one.
   When there is neither, find the file the project says owns the next action: `grep -i -n 'next action' AGENTS.md CLAUDE.md` and any orientation file they point to, and resolve a bare file name with `git ls-files '*<name>'`. Read that file and report the next action it marks as current, with its path.

## Red flags - put these at the TOP of the briefing

- Every `FLAG:` line from `red-flags.sh`: uncommitted changes, a detached HEAD, a merge or rebase in progress, work in only one copy (commits no remote-tracking ref reaches, uncommitted changes in another worktree), active tmux sessions, a stale handoff or `STATE.md`, and Loam pin drift.
  The script matches words, not meaning: drop a status-word flag whose quoted line does not claim that state (for example "not pushed").
  The one-copy check does not fetch and compares commits, not content: a squash-merged branch or a pushed tag off every remote branch still counts.
- Memory files untouched for 14+ days.
- In-progress tasks from a previous session.

Report the drift; the repository state overrides the handoff, never the reverse.

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
Handoff / State: next single action + the handoff's path, or the next action from the project's state file + its path (or: none; or: STALE - hash / mtime / status words disagree with git)
Loam pin: the `Loam pin:` line from red-flags.sh
Open tasks (or: none)
=== END BRIEFING ===
```
