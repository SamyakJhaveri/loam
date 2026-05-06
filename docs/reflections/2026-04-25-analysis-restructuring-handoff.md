# Reflection: Analysis Document Restructuring Handoff

**Date:** 2026-04-25
**Session work:** Brainstormed, designed, plan-reviewed, and wrote a 942-line HANDOFF for 4 analysis document fixes (augmentation matrix, error taxonomy, pass@k, self-repair deletion)
**Files touched:** 1 primary file (HANDOFF.md), 2 memory files updated

## What Surprised Me

- **pass@k had TWO independent bugs, not one.** The `quantitative_findings.py` bug (ad-hoc "any pass"/"all pass" counting mislabeled as pass@1/pass@3) was the obvious one. But the plan-reviewer caught a subtler bug in `generate_paper_data.py` — it includes ablation L1-L4 records in the pass@k grouping, inflating some tasks from n=3 to n=7. The Chen formula produces numerically different values when n varies (23.1%/31.5% vs 23.9%/35.2%). I initially assumed the 35.2% "any pass" fraction equaled Chen pass@3 — it does, but ONLY because all L0 tasks have exactly n=3 seeds. If I hadn't verified this with actual computation, the handoff would have contained a latent error.

- **The `build_error_taxonomy.py` extract_direction() function has a longstanding omp_target parsing bug** (line 339: `rsplit("-", 1)` turns "omp_target" into "target"). This was hiding in plain sight — the error taxonomy has been generating corrupt direction labels for omp_target results this entire time. The correct pattern (check for omp_target before splitting) already exists in `augmentation_analysis.py:_extract_api()`. Two scripts solving the same problem differently, one wrong.

- **The augmentation matrix L0 blank was caused by an overly broad stochastic skip.** The `_is_stochastic()` function matches `-s\d+$` in filenames. Since ALL 504 canonical L0 results use seed suffixes (-s0, -s1, -s2), the function skips every single L0 result. The fix is simple (don't skip stochastic at L0, apply consensus), but the root cause was non-obvious — you'd have to know that all canonical results have seed suffixes AND that the skip was applied before checking the augment level.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (new section)

```
## Analysis Script Consistency — Two Pass@k Implementations

Two scripts compute pass@k independently:
- `quantitative_findings.py:compute_pass_at_k()` — filters to L0 only, uses ad-hoc counting (BUG: not Chen formula)
- `generate_paper_data.py:analyze_passk()` — uses correct Chen formula but includes ablation records (BUG: not L0-only)

After both bugs are fixed, add a cross-validation assertion to the analysis pipeline:
assert abs(paper_data["pass@1_macro_avg"] - quantitative_findings["pass_at_1"]) < 0.001

More broadly: any metric computed by two independent scripts MUST have a cross-check.
The `cross_consistency_audit.py` script exists for this purpose — add pass@k cross-validation to it.
```

**Why:** Two scripts computing the same metric with different bugs is how papers get retracted. The cross-consistency audit already exists as infrastructure; it just needs this specific check added. Without it, a future change to one script could silently diverge from the other.

## Prompt Improvement

**Original approach:** The user listed 4 issues in a single brainstorming prompt, mixing questions ("where is the data for other directions?"), instructions ("split the error taxonomy"), and research requests ("go through research papers on pass@k").

**Better approach:** Separate the research question from the implementation plan. The pass@k research question consumed significant tokens (spawning a research agent, computing ground truth values, reconciling two scripts) and should have been its own session or pre-work.

```
Improved prompt fragment:

"I need 4 changes to analysis documents. Before planning, verify the pass@k 
ground truth by running the Chen formula on L0-only results (n=3, 142 tasks). 
The current labels are wrong — pass@1 and pass@3 are swapped relative to 
Chen et al. 2021. Compute the correct values, then plan all 4 changes."
```

This front-loads the verification step that ended up being the most time-consuming part of the session.

## Gotcha Discovered

**Symptom:** `generate_paper_data.py` reports pass@1=23.1%, pass@3=31.5%, while the L0-only ground truth is pass@1=23.9%, pass@3=35.2%.

**Root cause:** `split_campaigns()` (line 545-555) puts ALL temp=0.7 records into `passk` — including ablation L1-L4 records. When `analyze_passk()` groups by (kernel, direction), tasks that passed canonically get n=7 (3 seeds + 4 ablation levels) while failing tasks get n=3. The Chen formula with variable n produces different macro-averages.

**Fix:** Add `records = [r for r in records if r.get("augment_level", 0) == 0]` at the top of `analyze_passk()`. Ablation records are not i.i.d. samples — they're different augmentation levels.

**Status:** NEW GOTCHA — not yet documented. Added to HANDOFF.md as Step 3.6b. Should be added to `known-issues.md` after the fix is implemented.
