# Reflection: Data Integrity Audit

**Date:** 2026-04-24
**Session work:** Deep analysis of 708 Qwen eval results across 14 dimensions; discovered and fixed 2 data integrity bugs (pass@k ablation contamination, backprop false PASS); added stdout_exclude_pattern verifier strategy.
**Files touched:** 12 files in harness/, scripts/analysis/, tests/, specs/, .claude/rules/

## What Surprised Me

- **The pass@k calculation was contaminated by ablation records.** `compute_pass_at_k()` grouped by (source_spec, target_spec) without filtering by augment_level, so 50 tasks had 7 "seeds" (3 canonical + 4 ablation) instead of 3. This deflated pass@3 from 13.0% to 7.5% — a 5.5 pp error. The bug existed since the function was written but was invisible until someone compared seed counts to expectations. The fix was 2 lines.

- **Rodinia's backprop-opencl baseline has always been silently broken.** The original Rodinia code has a `clEnqueueReadBuffer` error at runtime, but the program gracefully handles it, prints the expected output, and exits 0. The weak oracle (stdout_pattern + exit_code) couldn't catch this. Five LLM translations inherited the same pattern and were falsely marked PASS. Nobody noticed because the test "passed."

- **Stale count propagation is insidious.** Adding backprop-opencl as the 9th KNOWN_FAIL required updating counts in 10+ locations across CLAUDE.md, known-issues.md, constants.py, quantitative_findings.py (3 string literals), test comments, and architecture.md. The session critique found 8 missed locations after the initial commit. Hardcoded counts rot silently.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (add to Key Build/Run Rules section)

```
## Count Propagation Rule

When adding or removing a KNOWN_FAIL spec:
1. Update `harness/constants.py` EXCLUDED_SPECS
2. Update `.claude/rules/known-issues.md` KNOWN_FAIL table + spec status counts
3. Update `CLAUDE.md` KNOWN_FAIL count and curated spec count
4. Grep for the OLD count: `grep -rn "N KNOWN_FAIL\|N KF\|N specs" scripts/ .claude/ CLAUDE.md`
5. Replace hardcoded counts with `len(EXCLUDED_SPECS)` where possible
```

**Why:** The session critique found 8 stale "8 KNOWN_FAIL" references after adding the 9th spec. Three were in string literals that generate user-facing output. Future KNOWN_FAIL additions will hit the same problem unless there's a checklist.

## Prompt Improvement

**Original approach:** "Read HANDOFF-QWEN-DEEP-ANALYSIS.md and execute the plan starting from Phase A" — a broad directive covering 5 phases of analysis.

**Better approach:** The handoff was excellent for orientation but Phase A was already complete (all analysis files existed). Starting with a verification step ("are Phase A outputs current?") saved re-running 10 scripts. The session's real value came from Phase B interpretation, which surfaced the bugs. A better prompt would have been:

```
Verify Phase A outputs exist and are current. Then do Phase B: read each
analysis JSON and extract per-dimension findings. Focus on data integrity —
cross-check aggregates against file-by-file recounts. Flag any inconsistencies
before moving to interpretation.
```

This front-loads the rigor check (Phase D) into Phase B, which is where the bugs were actually found.

## Gotcha Discovered

**Symptom:** `compute_pass_at_k` reported 51 warnings about tasks having 7 seeds instead of 3, and pass@3 was implausibly low (7.5% vs pass@1 34.9% = 4.6x ratio).
**Root cause:** The function groups by `(source_spec, target_spec)` without filtering by `augment_level`. Ablation L1-L4 records share the same source/target as canonical s0/s1/s2 records, so they were counted as extra "seeds."
**Fix:** Filter to `augment_level == 0` before grouping: `canonical = [r for r in records if r.get("augment_level", 0) == 0]`
**Status:** FIXED in commit 6fce616. Test `test_pass_at_k_excludes_ablation_levels` guards against regression.

**Symptom 2:** 5 backprop-omp-to-opencl results marked PASS despite `ERROR: 1 clEnqueueReadBuffer` in stdout.
**Root cause:** Weak oracle (stdout_pattern + exit_code) can't catch runtime errors that the program handles gracefully. The baseline Rodinia code itself has this bug.
**Fix:** Added `stdout_exclude_pattern` verifier strategy (inverse of stdout_pattern). Applied to backprop-opencl spec. Marked as KNOWN_FAIL since baseline is broken.
**Status:** FIXED in commit fd55456. New strategy documented in architecture.md and spec_schema.json.
