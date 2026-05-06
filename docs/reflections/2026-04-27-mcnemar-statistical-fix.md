# Reflection: McNemar Statistical Fix

**Date:** 2026-04-27
**Session work:** Replaced unpaired chi-squared with Yates-corrected McNemar's test for cross-model comparison; strengthened confound language; added oracle downgrade discussion
**Files touched:** 4 files in scripts/analysis/, results/analysis/, docs/paper/

## What Surprised Me

- **The Yates correction changed the p-value bound.** Uncorrected McNemar gave chi²=47.1 (p<10⁻¹¹), but Yates-corrected gives chi²=45.2 (p=1.80e-11), which is NOT <10⁻¹¹. The paper would have claimed a tighter bound than warranted. Caught by the Opus self-critic, not by me. Lesson: when replacing a statistical test, always check whether the existing codebase has a convention for correction factors before implementing the textbook formula.

- **The HANDOFF.md said "8 specs" but the actual count is 10.** The S7b audit table has 8 rows, but the earlier S7 BUG-3 downgrade added 2 more bfs specs for the same category of issue. Lesson: HANDOFF docs are human-written summaries that can have counting errors. Always verify against the authoritative source (known-issues.md).

- **Codex caught a unit-of-analysis mismatch that the Opus self-critic missed.** The paper mixed sample-level pass@1 rates with task-level McNemar. Different models catch different things — the cross-model review protocol is genuinely valuable, not ceremony.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (append to "Key Build/Run Rules" section or new section)

```
## Statistical Test Convention

All paired McNemar tests in this codebase use Yates continuity correction when
discordant pairs >= 25 (see statistical_analysis.py:586, generate_paper_data.py:185,
cross_model_comparison.py:83). When adding a new McNemar computation, always use
the corrected formula: (|b-c| - 1)^2 / (b+c). Below 25 discordant pairs, use
exact binomial test (scipy binomtest).
```

**Why:** Without this, a future contributor (or Claude) will write the uncorrected McNemar from a textbook, creating an internal inconsistency that a reviewer could flag. The Yates convention is already present in 3 scripts but was not documented.

## Prompt Improvement

**Original approach:** "implement P0 from the HANDOFF.md file" — relied on HANDOFF.md numbers being correct.

**Better approach:** Add a verification step to the prompt:

```
implement P0 from HANDOFF.md. Before implementing any numeric claim from the
HANDOFF, verify the count/value against the authoritative source file
(known-issues.md for spec counts, raw JSON for statistics). HANDOFF docs
are summaries that may have counting errors.
```

## Gotcha Discovered

**Symptom:** Yates-corrected McNemar p-value (1.80e-11) barely exceeds 10⁻¹¹, making "p < 10⁻¹¹" incorrect while uncorrected "p < 10⁻¹¹" was fine.
**Root cause:** The continuity correction reduces the chi² from 47.1 to 45.2, shifting p from 6.82e-12 to 1.80e-11 — just past the 10⁻¹¹ threshold.
**Fix:** Updated paper to "p < 10⁻¹⁰" which holds with comfortable margin.
**Status:** NEW GOTCHA — not previously documented. The boundary sensitivity of p-value reporting with/without Yates correction should be noted when writing paper claims.
