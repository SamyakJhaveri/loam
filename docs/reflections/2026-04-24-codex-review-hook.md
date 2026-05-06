# Reflection: Codex Review Hook

**Date:** 2026-04-24
**Session work:** Implemented advisory pre-commit hook that reminds about Codex reviews via sentinel file pattern
**Files touched:** 5 files (1 new, 4 modified) in `.claude/hooks/`, `.claude/`, project root

## What Surprised Me

- **Gated TDD worked cleanly for infrastructure code.** The 3-gate protocol (INTENT/RED/GREEN) applied naturally even to a bash hook script — writing tests first for a file that doesn't exist yet (exit 127) was a clean RED state. The gates caught nothing wrong in the implementation itself, but the discipline forced explicit verification at each step rather than "it looks right."

- **Session critique convergent findings are strong signal.** Both the self-critic (Sonnet) and code-reviewer (Opus) independently flagged the same `grep -q "git commit"` false-positive bug despite working from different checklists and different file buckets. When two independent reviewers find the same issue, it's almost certainly real. The code-reviewer also caught a sentinel path mismatch in the instruction text that the advisor missed entirely.

- **The handoff doc quality was excellent but not perfect.** The HANDOFF-CODEX-REVIEW-HOOK.md specified the exact algorithm, reference files, verification commands, and anti-patterns. This made implementation fast (~15 min for the core hook). But the handoff chose `grep -q "git commit"` (simpler) over the spec's own reference to `pre-commit-gate.sh:47` which uses the stricter pattern. The "simpler" choice introduced a false-positive bug that the critique caught.

## Pattern Proposal

**Target:** `.claude/rules/workflow.md` (in the 6-Stage Session Workflow, after Stage 5 Record)

```
- After `/session-critique`, run `/codex:rescue review the uncommitted changes` for a second opinion before `/validate`.
  Workflow: do work -> /session-critique -> Codex review -> /validate -> commit.
  The pre-commit hook reminds about Codex review via `.codex_review_done` sentinel (same pattern as `.validation_passed`).
```

**Why:** The Codex review step is now wired into the commit workflow via hooks, but the canonical workflow documentation in `workflow.md` doesn't mention it. Future sessions reading the workflow won't know about the Codex step unless it's documented where the other commit-gate steps are described.

## Prompt Improvement

**Original approach:** The handoff doc said "copy the pattern from `pre-commit-gate.sh` line 47" for command detection but then wrote `grep -q "git commit"` in the pseudocode algorithm — a contradiction that led to the weaker pattern being implemented.

**Better approach:** When a handoff doc references a specific line in a reference file, the pseudocode should use the exact same pattern, not a simplified version.

```
# In HANDOFF pseudocode, use the ACTUAL pattern from the reference:
3. if $CLAUDE_TOOL_INPUT does NOT match /^\s*git\s+commit/ → exit 0
# NOT the simplified version:
3. if $CLAUDE_TOOL_INPUT does NOT contain "git commit" → exit 0
```

## Gotcha Discovered

**Symptom:** `grep -q "git commit"` matches any command containing the substring "git commit" — including `echo "git commit"`, `grep "git commit" file.txt`, and `git commit-graph`.
**Root cause:** Simple substring match (`grep -q`) vs. anchored regex (`grep -qE '^\s*git\s+commit'`). The existing `pre-commit-gate.sh` already uses the anchored version, but the new hook chose the simpler pattern.
**Fix:** Changed to `grep -qE '^\s*git\s+commit'` to match only commands that START with `git commit`.
**Status:** Fixed in this session. Not a known-issues.md item — it's a one-off implementation bug caught by session critique.
