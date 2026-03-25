# Session Bootstrap

Bootstrap a ParBench SC26 sprint session: extract the session prompt, check git
state, verify prerequisites, surface blockers, and report readiness.

**Trigger:** When user types `/session-start <N>`. Does NOT auto-execute the session —
orient and present only. The user initiates execution after reviewing the report.

## Arguments

- `$ARGUMENTS` — session identifier, e.g.: `7`, `6.5`, `3b`, `3-PM`, `S-HeCBench`.
  Numeric sessions may include an `S` prefix (e.g., `S7` is treated as `7`).
  Named sessions with `S-` prefix (e.g., `S-HeCBench`) keep the full name.
  If omitted, prompt the user.

## Workflow

### Phase 1: Identify

1. Normalize the session identifier from `$ARGUMENTS`:
   - Strip leading `S` for pure numeric sessions: `S7` → `7`, `S1.5` → `1.5`
   - Keep suffix sessions as-is: `3b`, `3-PM`, `10b`
   - Keep named sessions as-is: `S-HeCBench`

2. Search `docs/session_prompts_sc26.md` for the session heading:
   ```bash
   grep -n "## SESSION.*\b<IDENTIFIER>\b" docs/session_prompts_sc26.md
   ```
   If no match, try without word boundaries, or try the `S`-prefixed form.
   If still no match, list all session headings and ask the user to clarify.

3. Read the full session block (from its heading to the line before the next `## SESSION`).

4. Check the **STATUS** line:
   - Contains `COMPLETE` → warn: "⚠ Session <N> is marked COMPLETE. Continuing anyway."
   - Contains `NOT STARTED` → normal proceed

### Phase 2: Orient

Launch a single subagent to gather orientation data (keeps main context clean):

```bash
# In the subagent:
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Git state
git branch --show-current
git log --oneline -10
git status --short

# Python environment
python3 -c "import sys; print(sys.prefix)"

# Sprint progress (count COMPLETE sessions)
grep -c "STATUS:.*COMPLETE" docs/session_prompts_sc26.md

# Relevant results (infer directory from session content)
# e.g., for eval sessions: ls results/evaluation/ | wc -l
# e.g., for spec sessions: ls specs/ | wc -l
```

The subagent returns: git branch, last 10 commits, dirty files, venv status,
complete session count, and any relevant results counts.

**Prerequisite check:** Parse the session block's `# Prerequisites` section. For each
prerequisite session listed, check whether it appears as `STATUS: COMPLETE` in
`docs/session_prompts_sc26.md`.

**Sprint deadline:** April 8, 2026. Compute days remaining from today's date.
Total sprint sessions: 25.

### Phase 3: Report

Display structured readiness report:

```
=== SESSION <N>: <title> ===
Status:     NOT STARTED  [or: ⚠ COMPLETE — already done]

SPRINT:     <X>/25 sessions complete | <Y> days until April 8, 2026

GIT STATE:
  Branch:   main  ✓  [or: <unexpected-branch> ✗]
  Clean:    yes  ✓  [or: <N> uncommitted changes  ✗]
  Last:     <hash> <message>

PREREQUISITES:
  ✓ Session <X> — COMPLETE
  ✗ Session <Y> — NOT STARTED  ← BLOCKER

RESULTS STATE:
  <relevant check with count and ✓/✗>

BEFORE YOU START:
  DECISIONS:
    [ ] <item>
  DATA/INFO:
    [ ] <item>
  EXTERNAL DEPS:
    [ ] <item>

VERDICT: ✅ READY TO EXECUTE
    [or: 🔴 BLOCKED — resolve above before starting]
```

Omit any section (PREREQUISITES, RESULTS STATE, BEFORE YOU START) if empty.

### Phase 4: Handoff

Display the full session prompt (the `ultrathink` block and numbered steps) for the
user to review. Then remind:

> Run `/clear` for a clean context before executing, or proceed here if this context
> has budget remaining. Always run `/validate` before committing at the end of the session.
