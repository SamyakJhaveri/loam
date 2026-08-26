---
name: catchup
description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, environment state, memory-index staleness, pending tasks, and red flags (uncommitted changes, detached HEAD, stale memory). NOT for deep code exploration or planning - it only reports state, it does not change it.
---

# Session Catchup Briefing

Use when resuming work after a break and you need a fast 30-second context refresh:
just the state of the repo and any in-flight work, no deep exploration.

**Trigger:** When user types `/catchup`.

## Iron Law

```
NO WORK WITHOUT CONTEXT - READ THE STATE BEFORE CHANGING IT
```

## Arguments

- `$ARGUMENTS` - optional: number of recent commits to show (default: 10)

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I remember what I was doing" | Memory decays; git log doesn't. 30 seconds now saves 30 minutes of confusion later |
| "I'll figure it out as I go" | Figuring it out mid-task means wasted context window on re-discovery |
| "Nothing changed since last session" | Verify that claim - auto-merges, hook updates, and background jobs run silently |
| "I just have a quick fix" | Quick fixes on stale context cause the bugs that take hours to debug |

## Red Flags - STOP and Warn User

- Uncommitted changes in the working tree (risk of losing work or committing stale state)
- Detached HEAD state (not on a named branch)
- Memory files older than 14 days with no updates (context may be stale)
- Active long-running background jobs (tmux sessions, batch runs) that could conflict
- Merge conflicts or rebase in progress

If any red flag triggers: display it prominently at the TOP of the briefing, before
the normal status report.

## Workflow

### Phase 1: Git State

Run these commands and capture output - do NOT guess or use cached data:

```bash
# Current branch and dirty state
git status

# Recent commits (default 10, or user-specified count)
git log --oneline -<N>

# Changed files since ~last session (diff stat against 10 commits back)
git diff --stat HEAD~10 2>/dev/null || git diff --stat "$(git rev-list --max-parents=0 HEAD)"
```

**Verification gate:** All three commands must execute successfully. If `git status` shows
an error (not a repo, corrupted index), STOP and report.

### Phase 2: Environment Check

```bash
# Check for running background sessions (batch jobs, long-running tasks)
tmux list-sessions 2>/dev/null || echo "No tmux sessions"

# Language runtime, if this project uses one (adjust for the stack)
python3 --version 2>/dev/null; node --version 2>/dev/null
```

**Verification gate:** If a session manager shows active sessions, flag them - the user may
have a long-running job that should not be interrupted.

### Phase 3: Memory Staleness

Claude Code keeps optional per-project memory at `~/.claude/projects/<project>/memory/`,
indexed by a `MEMORY.md` file. Check it only if it exists:

```bash
# Resolve this project's memory dir. Claude Code slugifies the PROJECT ROOT path
# (resolve the root, not the cwd) by replacing EVERY non-alphanumeric character
# with '-' - underscores and spaces included, not just '/'.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MEMORY_DIR="$HOME/.claude/projects/$(printf '%s' "$ROOT" | sed 's#[^a-zA-Z0-9]#-#g')/memory"
if [ -f "$MEMORY_DIR/MEMORY.md" ]; then
  ls -lt "$MEMORY_DIR"/*.md 2>/dev/null | head -10
else
  echo "No memory index (memory system not initialized for this project)"
fi
```

Flag any memory file not modified in 14+ days as potentially stale. If no `MEMORY.md`
exists, note that memory is not initialized and move on - it is optional.

### Phase 4: Task State

Run `TaskList` to check for any in-progress or pending tasks from a previous session.

**Verification gate:** If tasks exist from a previous session, display them - they may
represent interrupted work.

### Phase 5: Compile Briefing

Present a concise bullet-point briefing in this exact format:

```
=== CATCHUP BRIEFING ===

[RED FLAGS - only if any detected]
  ! Uncommitted changes: <N> files modified
  ! Active background session: <session name> (may be running a batch job)

Branch:    <current branch>
Status:    clean | <N> modified, <N> untracked
Last commit: <hash> <message> (<relative time>)

Recent activity (last <N> commits):
  <hash> <message>
  <hash> <message>
  ...

Changed files (since HEAD~10):
  <diffstat summary>

Environment:
  sessions: <N active | none>
  runtime:  <version(s) detected>

Memory:
  <N> files, most recent: <filename> (<date>)   | or: not initialized
  [Stale: <list of files >14 days old>]

Open tasks:
  [#<id>] <status> - <subject>
  ...
  [or: No open tasks]

=== END BRIEFING ===
```

Keep it tight. The entire briefing should fit in one screen. No explanations, no
suggestions, no preamble - just the state. The user decides what to do with it.
