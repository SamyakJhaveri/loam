# NeurIPS 2026 Simulated Review Panel — 2026-04-27

## Summary

| Reviewer | Score | Verdict |
|----------|-------|---------|
| R1 (HPC) | 72 | Technically sound, but weak oracles and missing FP divergence discussion |
| R2 (ML/AI) | 68 | Useful harness, but temperature confound undermines cross-model comparison |
| R3 (Stats) | 68 | Honest stats, but chi-squared invalid and directions underpowered |
| R4 (Repro) | 82 | Strong reproducibility with pinned sources; needs reproduction script |
| R5 (Devil) | 48 | Too small, too biased toward Rodinia, rapidly obsolete |
| **AVG** | **67.6** | **BORDERLINE (weak accept)** |

## P0 — Must Fix Before Submission

### P0-1: Fix cross-model chi-squared test (R3)
**Location:** discussion.tex, cross-model comparison paragraph
**Problem:** Uses unpaired chi-squared on 142 tasks evaluated by both models. Should be McNemar's test on 142 paired outcomes. Report concordance table (both-pass, both-fail, discordant).
**Data needed:** Already have per-task pass/fail for both models in paper_data files. Just need to compute McNemar.
**Fix:** Replace chi-squared (128.6, p<10^-6) with McNemar test + concordance table. Keep Cohen's h (0.80).

### P0-2: Strengthen temperature confound language (R1, R2, R3)
**Location:** discussion.tex Section 5.4, abstract.tex
**Problem:** Current hedging ("may partly reflect") is insufficient. The cross-model gap cannot be attributed to model capability alone when GPT-5.4's effective temperature is unknown.
**Fix:** Replace chi-squared p-value framing with: "The observed gap is large (Cohen's h = 0.80) but we cannot fully attribute it to model capability given unmatched sampling conditions." Remove or heavily qualify the p-value.

### P0-3: Discuss FP divergence and 8 downgraded specs (R1)
**Location:** Should be in discussion.tex limitations, or framework.tex verification section
**Problem:** 8 specs were downgraded from strong/medium to weak oracles due to cross-API FP reduction-order divergence (cfd, hotspot, myocyte, nw, nn, bfs). This is never mentioned in the paper. It's a fundamental challenge for cross-API correctness verification.
**Fix:** Add 2-3 sentences in the verification subsection or limitations discussing FP divergence as an inherent challenge. Reference the downgrade evidence.

## P1 — Strongly Recommended

### P1-1: Scope augmentation robustness claim (R3, R5)
**Location:** abstract.tex — "pass rates remain stable (75–83%)"
**Problem:** Based on 12 kernels on the easiest direction. Overstates evidence.
**Fix:** Reword to "no evidence of memorization-dependent degradation on the tested subset" or similar.

### P1-2: Add per-direction GPT-5.4 rates to Table 3 (R2, R3)
**Location:** results.tex Table 3 (tab:direction-rates)
**Problem:** Only aggregate GPT-5.4 row; direction effects can't be compared cross-model.
**Data:** Available in quantitative_findings_gpt54.json > canonical > direction_pass_rates

### P1-3: Report GPT-5.4 within-task variance (R2)
**Problem:** If GPT-5.4's 3 samples are nearly identical, it confirms low effective temperature.
**Data:** Compute from paper_data_azure_gpt54.json > passk_campaign > passk_estimates (variance of c across tasks)

### P1-4: Acknowledge benchmark longevity (R5)
**Location:** discussion.tex
**Problem:** 62.7% pass@1 suggests saturation in ~1 year.
**Fix:** Add 1-2 sentences discussing augmentation + harder tasks as longevity strategy.

## P2 — Nice to Have

- Add reproduction script/Makefile target (R4)
- Classify VERIFY_FAIL subtypes: numerical/race-condition/logic (R1)
- Report ICC / effective degrees of freedom for Wilson CIs (R3)
- Make HeCBench a submodule or document clone (R4)
- Note OMP-target's SPMD model in API characteristics table (R1)
- Remove Cochran-Armitage test entirely since authors already dismiss it (R1, R3)

## Rebuttal Prep Questions

1. "If someone had LASSI + Rodinia/XSBench, what do they still need ParBench for?" — Answer: 10-direction coverage, 5-suite corpus, augmentation engine, structured failure taxonomy, spec-driven reproducibility
2. "False-positive rate from weak oracles?" — Could test by intentionally breaking a passing translation
3. "Why unpaired chi-squared instead of McNemar?" — Fix this (P0-1)
4. "GPT-5.4 within-task variance?" — Compute this (P1-3)
5. "Won't the benchmark saturate in a year?" — Augmentation levels, harder kernels, performance measurement as extensions

## Full Reviewer Reports

See individual reviewer transcripts in the Claude Code session log (2026-04-27).
- R1: HPC domain — technically accurate semantics, good exclusion rationale; wants FP divergence, race condition diagnosis, multi-GPU discussion
- R2: ML/AI — clean design choice for kernel isolation; wants temperature resolution, more models, prompt anonymization clarification
- R3: Stats — transparent limitations; wants McNemar for cross-model, ICC for CIs, corrected per-direction comparisons
- R4: Repro — strong infrastructure; wants one-command reproduction, HeCBench submodule, API key docs
- R5: Devil — engineering is solid but contribution is thin; benchmark too small, Rodinia-dominated, rapidly obsolete
