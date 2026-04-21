---
name: catchup
description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, env state, memory staleness, pending tasks, and red flags (uncommitted changes, detached HEAD, stale memory).
---

# Session Catchup Briefing

Use when resuming work after a break and you need a fast 30-second context refresh.
Lighter than `/session-start` — no prerequisite checks, no sprint context, just the
state of the repo and any in-flight work.

**Trigger:** When user types `/catchup`.

## Iron Law

```
NO WORK WITHOUT CONTEXT — READ THE STATE BEFORE CHANGING IT
```

## Arguments

- `$ARGUMENTS` — optional: number of recent commits to show (default: 10)

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I remember what I was doing" | Memory decays; git log doesn't. 30 seconds now saves 30 minutes of confusion later |
| "I'll figure it out as I go" | Figuring it out mid-task means wasted context window on re-discovery |
| "Nothing changed since last session" | Verify that claim — auto-merges, hook updates, and eval batches run silently |
| "I just have a quick fix" | Quick fixes on stale context cause the bugs that take hours to debug |

## Red Flags — STOP and Warn User

- Uncommitted changes in the working tree (risk of losing work or committing stale state)
- Detached HEAD state (not on a named branch)
- Memory files older than 14 days with no updates (context may be stale)
- Active tmux sessions that may be running eval batches (avoid conflicts)
- Merge conflicts or rebase in progress

If any red flag triggers: display it prominently at the TOP of the briefing, before
the normal status report.

## Project Context

- **Project root:** `{{PROJECT_ROOT}}`
- **Venv:** `source {{PROJECT_ROOT}}/env_parbench/bin/activate`
- **Memory directory:** `/home/samyak/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/`
- **Results directory:** `results/evaluation/` — eval campaign results by model
- **Spec counts:** 60 Rodinia (54 PASS, 6 KNOWN_FAIL), 4 XSBench (4 PASS)
- **Models:** claude-sonnet, gemini-2.5-flash-lite, groq-llama-3.3-70b, together-qwen-3.5

## Workflow

### Phase 1: Git State

Run these commands and capture output — do NOT guess or use cached data:

```bash
# Current branch and dirty state
cd {{PROJECT_ROOT}} && git status

# Recent commits (default 10, or user-specified count)
git log --oneline -<N>

# Changed files since ~last session (diff stat against 10 commits back)
git diff --stat HEAD~10 2>/dev/null || git diff --stat $(git rev-list --max-parents=0 HEAD)
```

**Verification gate:** All three commands must execute successfully. If `git status` shows
an error (not a repo, corrupted index), STOP and report.

### Phase 2: Environment Check

```bash
# Check for running tmux sessions (eval batches, overnight runs)
tmux list-sessions 2>/dev/null || echo "No tmux sessions"

# Check if venv is active or needs activation
python3 --version 2>/dev/null
which python3 2>/dev/null
```

**Verification gate:** If tmux shows active sessions, flag them — the user may have an
eval batch running that should not be interrupted.

### Phase 3: Memory Staleness

Read the memory index at the memory directory path and check dates:

```bash
# List memory files with modification times
ls -lt /home/samyak/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/*.md 2>/dev/null | head -10
```

Flag any memory file not modified in 14+ days as potentially stale.

**Verification gate:** Memory index file must exist. If not, note that memory system
needs initialization.

### Phase 4: Task State

Run `TaskList` to check for any in-progress or pending tasks from a previous session.

**Verification gate:** If tasks exist from a previous session, display them — they may
represent interrupted work.

### Phase 5: Compile Briefing

Present a concise bullet-point briefing in this exact format:

```
=== CATCHUP BRIEFING ===

[RED FLAGS — only if any detected]
  ! Uncommitted changes: <N> files modified
  ! Active tmux session: <session name> (may be running eval batch)

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
  tmux:   <N sessions active | none>
  venv:   <active | needs activation>
  python: <version>

Memory:
  <N> files, most recent: <filename> (<date>)
  [Stale: <list of files >14 days old>]

Open tasks:
  [#<id>] <status> — <subject>
  ...
  [or: No open tasks]

=== END BRIEFING ===
```

Keep it tight. The entire briefing should fit in one screen. No explanations, no
suggestions, no preamble — just the state. The user decides what to do with it.
