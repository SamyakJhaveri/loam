# Reflection: Ablation Completion Commit

**Date:** 2026-04-27
**Session work:** Verified both Qwen and GPT-5.4 ablation studies complete on disk; committed 119 remaining GPT-5.4 L1–L4 result files + updated eval_summary
**Files touched:** 121 files in `results/evaluation/azure-gpt-5.4/` and `results/evaluation/`

## What Surprised Me

- The previous commit message (`2f81ce7`) said "259/396 = 65% complete," but the on-disk count was already 396 (100%). The runs had finished without a commit. The work was done — just un-committed. The gap wasn't discovered until a status check this session.
- The untracked file count was 119, not 137 (= 396 − 259). The 18-file discrepancy traces to batch log files (4 × `.json/.md` pairs for `batch_*` run logs) that were also committed in `2f81ce7` but weren't counted in the "259/396 ablation records" figure. The ablation record count and total commit count are different things.
- `eval_summary.json` and `eval_summary.md` were already regenerated on disk (showing the full 822-result picture) but weren't committed alongside the result files — they needed a separate explicit staging step.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (or `active-gotchas.md`)

```
## Ablation Run Commit Protocol

After each eval batch run that produces new ablation result files:
1. Run `python3 scripts/evaluation/analyze_eval.py --write-summary` to regenerate eval_summary.
2. Stage results AND summary together: `git add results/evaluation/<model>/ results/evaluation/eval_summary.*`
3. Commit with progress count in the message, e.g. "data: GPT-5.4 ablation (396/396, 100%)".

Never leave results un-committed past the end of a session — commit messages become
the only record of when each batch finished.
```

**Why:** The 259/396 commit message implied work was in progress; the actual completion sat un-committed until the next session's status check. Stale commit messages create false uncertainty about whether a campaign needs resuming.

## Prompt Improvement

**Original approach:** User asked "are the ablation studies done?" without specifying which model or what "done" means (all levels? all tasks? committed?).

**Better approach:**

```
Check ablation completion for both models:
- Count L1/L2/L3/L4 files per model in results/evaluation/<model>/
- Confirm counts are equal across levels (same N eligible tasks)
- List any uncommitted result files
- Report: done / in-progress / needs-rerun for each model
```

Providing this structure upfront avoids an extra round-trip to clarify whether "done" means on-disk or committed.

## Gotcha Discovered

**Symptom:** `git status` showed 119 untracked files, but arithmetic from the commit message suggested 137 should be new (396 − 259 = 137).

**Root cause:** The 259-record count in the prior commit message referred only to ablation JSON files, while the actual commit also included 4 batch run-log files (`batch_*.json/md`). The two counts (ablation records vs. files-in-commit) are different denominations.

**Fix:** Always report ablation counts and total-files-in-commit separately in the commit message, e.g. "data: GPT-5.4 ablation (396/396 ablation records, +4 batch logs)".

**Status:** NEW GOTCHA — not yet documented.
