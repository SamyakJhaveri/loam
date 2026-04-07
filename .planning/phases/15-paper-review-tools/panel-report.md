# SC26 Review Panel Report: ParBench

**Paper:** ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness
**Panel Date:** 2026-04-06
**Panel Composition:** 5 reviewers (HPC domain, ML methodology, statistics, reproducibility, adversary)
**Phase:** Post-cross-talk synthesis

---

## Panel Verdict: MINOR REVISION (conditional)

**Vote tally:** 4 Minor Revision, 1 Major Revision (conditional)
**Consensus:** Minor Revision — achievable before April 8 deadline if the 3 must-fix items are executed.

The panel unanimously finds the core contribution (kernel-centric isolation framework + spec engineering) to be sound and valuable. The paper's principal weaknesses are presentational and completeness gaps, not methodological flaws. R5's conditional Major Revision becomes Minor Revision if the 3 must-fix items below are addressed.

**Estimated acceptance probability:**
- Current state: 30-40%
- After must-fix items: 65-75%

---

## Must-Fix Items (3) — Required Before Submission

### FIX-1: Resolve GPT-4.1 mini data [CRITICAL]
**Flagged by:** R2-ML (CRITICAL), R4-REPRO (MAJOR), R5-ADVERSARY (CRITICAL)
**Cross-talk consensus:** Unanimous

The paper promises two-model evaluation but delivers one. 15+ `\pending{}` macros and blank `\tbd` table cells permeate the abstract, tables, discussion, and conclusion. Duplicate `\newcommand` definitions for `\pending` (lines 36-37) and `\parbench` (lines 28, 53) will cause LaTeX compilation errors.

**Resolution (choose one):**
- **(a) Deliver GPT-4.1 mini data** and fill all placeholders, OR
- **(b) Reframe as single-model** — remove ALL GPT references, `\pending{}` macros, blank table rows, and cross-provider comparison framing. Fix duplicate `\newcommand` definitions.

Option (b) is strongly recommended if data cannot arrive by April 7. A clean single-model benchmark validation paper is dramatically stronger than a two-model paper with 50% missing data. HumanEval and SWE-bench both launched with single-model evaluations.

**Effort:** Option (a): depends on eval completion. Option (b): ~4-6 hours of LaTeX editing.

---

### FIX-2: Fix augmentation narrative and report all statistical tests [MAJOR]
**Flagged by:** R3-STATS (MAJOR x2), R5-ADVERSARY (MAJOR), R2-ML (MINOR, upgraded in cross-talk)
**Cross-talk consensus:** Unanimous agreement that all conducted tests must be reported

Four specific actions:

**(a) Report the Fisher exact test** (L0 vs pooled L1-L4, p=0.0037 corrected to p=0.0075). Cross-talk clarified this is NOT contradictory — it tests a different scope (all directions, n=192) than the Cochran-Armitage (balanced CUDA-to-OMP, n=120), and augmented code passing MORE than L0 actually strengthens the anti-memorization case (the opposite of what memorization would predict). But the test must be reported and the scope difference explained.

**(b) Report or exclude the omp_target McNemar test** (Cohen's h=-1.37, p=0.0625). This is the most statistically interesting direction pair — large effect approaching significance — yet it's included in the Bonferroni correction family without being reported in the text. Either report it or exclude it from the correction count (changing alpha from 0.05/4 to 0.05/3).

**(c) Soften the augmentation claim language.** Change:
- Abstract line 84: "confirming benchmark validity against training-data memorization concerns" 
- Discussion line 1022: "evidence against the memorization hypothesis"

To: "consistent with the hypothesis that model failures are structural rather than surface-dependent, though the test is underpowered for moderate effects (MDES = 34.1pp)"

**(d) Acknowledge transform frequency skew.** Note that SwapCondition (162) and ArithmeticTransform (69) account for ~96% of applied transforms, and that ChangeFunctionNames fires only 2 times. The augmentation is primarily expression-level, not parallel-structure-level.

**Effort:** ~4-6 hours (LaTeX text changes + one paragraph explaining Fisher test scope).

---

### FIX-3: Add prompt template as appendix [MAJOR]
**Flagged by:** R2-ML (MAJOR), R4-REPRO (MAJOR in cross-talk upgrade), R5-ADVERSARY (MAJOR)
**Cross-talk consensus:** Unanimous

The translation prompt — the actual experiment — is not shown in the paper. The system message, user message structure, and anonymization protocol (kernel-name stripping, comment removal, filename genericization) exist in `llm_evaluate.py` but are invisible to reviewers.

**Resolution:** Add an appendix listing showing:
1. The full system message template
2. A representative user message with anonymization applied
3. A brief description (2-3 sentences) of the anonymization protocol in S3.4 or S5.1

The anonymization protocol is a genuine anti-contamination measure that strengthens the paper — it should be prominently described, not hidden in source code.

**Effort:** ~2 hours. Cost: ~0.5 pages in appendix.

---

## Should-Fix Items (8) — Strengthen Before Submission

### SF-1: Report API costs and evaluation time [MAJOR → data exists]
**Source:** R4-REPRO, R5-ADVERSARY
Data exists in `token_analysis.json`: $145.37 total, ~$0.13/task, 120M tokens, ~6 days. Add a paragraph in S5.5 or appendix table.

### SF-2: Fix HeCBench version pinning in specs [MAJOR → metadata fix]
**Source:** R4-REPRO
Update 25 `hecbench-*.json` specs: change `"commit": "archive-download"` to `"commit": "22785cd"`. Add HeCBench acquisition instructions in README.

### SF-3: Clarify unbalanced design in abstract/intro [MINOR]
**Source:** R5-ADVERSARY (MISS-2), R3-STATS, R1-HPC, R2-ML (all agreed in cross-talk)
The abstract implies full factorial (710 / 5 / 6 = 23.67, not 31). State explicitly that the design is unbalanced because not all kernels have all API implementations.

### SF-4: Add XSBench caveat to abstract/intro [MINOR]
**Source:** R5-ADVERSARY (MISS-3), R1-HPC (cross-talk nuance)
The kernel-isolation success narrative needs a caveat: XSBench achieves 0% translation even with isolation, marking the complexity boundary. The paper handles this honestly in S6 (lines 852-860) but the abstract/intro don't caveat.

### SF-5: Footnote n=700 vs n=710 discrepancy [MINOR]
**Source:** R3-STATS
The chi-squared multi-file test uses n=700 (10 unclassified tasks excluded). This is not mentioned.

### SF-6: Report absolute self-repair improvement alongside relative [MINOR]
**Source:** R3-STATS
"70% relative increase" should be accompanied by "15.8 percentage points" (22.5% → 38.3%).

### SF-7: Add LICENSE file at project root [MINOR]
**Source:** R4-REPRO
No project-level license. Needed for ACM artifact evaluation.

### SF-8: Reference requirements-lock.txt in paper [MINOR]
**Source:** R4-REPRO
The excellent dependency pinning (30+ exact versions) is invisible to paper readers.

---

## Nice-to-Have Items (7) — Camera-Ready or Future Work

| # | Item | Source | Notes |
|---|------|--------|-------|
| NH-1 | Implement `numeric_comparison` verification | R1-HPC | 3 strategies stubbed as SKIP in verifier.py |
| NH-2 | Add "translatability matrix" table | R1-HPC | Which kernel-direction pairs are theoretically impossible |
| NH-3 | Justify excluding BLEU/CodeBLEU | R2-ML | One-sentence justification suffices |
| NH-4 | Remove MoE architecture claim | R2-ML | "sparse activation" claim unsupported by single-model data |
| NH-5 | Add prompt sensitivity threat to validity | R2-ML | Results from single prompt template at T=0 |
| NH-6 | Expand pass@k to k=5 | R2-ML | 22 partial-success tasks need more samples |
| NH-7 | Add per-level CI bars to augmentation figure | R3-STATS | Visual reinforcement of wide CIs |

---

## Strengths (Panel Consensus)

1. **Kernel-centric isolation is the key insight** — 38.3% (64.2% CUDA-to-OMP) vs 0% repository-level. This is a genuine, well-demonstrated contribution with three converging evidence lines. (All 5 reviewers)

2. **Spec schema is a reproducibility gold standard** — complete build-run-verify recipes with provenance pinning, file partitioning, baseline results. Better than most benchmark papers. (R1, R4, R5)

3. **Statistical honesty above venue norm** — MDES disclosure, power caveats, Wilson CIs, explicit "failure to reject ≠ evidence for H0." Unusually transparent for SC. (R3, R5)

4. **Failure taxonomy provides genuine diagnostic value** — BUILD_FAIL/RUN_FAIL/VERIFY_FAIL with subcategories, spectrum framing, three case studies. Goes well beyond binary pass/fail. (R2, R5)

5. **Three-axis orthogonal design** — self-repair × sampling variance × augmentation robustness as independent experiments. Exemplary experimental design. (R2)

6. **Pass@k bimodal finding is novel** — 72.5% hard failures with 0% noisy failures characterizes deterministic translation capability boundaries. (R2, R5)

7. **Source provenance in LaTeX** — every numerical claim traced to a specific JSON field via comments. Exceptional. (R3, R4)

---

## Weaknesses (Panel Consensus)

### Critical (1)
| ID | Issue | Reviewers | Fix Effort |
|----|-------|-----------|------------|
| W-C1 | GPT-4.1 mini data absent, 15+ \pending{} macros, paper oscillates between 1-model and 2-model framing | R2, R4, R5 | 4-6h (reframe) or depends (deliver data) |

### Major (5)
| ID | Issue | Reviewers | Fix Effort |
|----|-------|-----------|------------|
| W-M1 | Augmentation claim overclaimed + 2 unreported significant/near-significant tests | R3, R5, R2 | 4-6h |
| W-M2 | Prompt template missing from paper | R2, R4, R5 | 2h |
| W-M3 | HeCBench specs record "archive-download" not commit hash | R4 | 1h |
| W-M4 | API costs/time unreported (data exists) | R4, R5 | 1h |
| W-M5 | Missing baselines (no rule-based translator, no model scaling) | R5, R1 | Future work framing, 1h |

### Minor (14)
Floating-point verification gap, no performance evaluation, augmentation transform skew, SYCL omission, multi-file asymmetry discussion, abstract overstatement, BLEU exclusion unjustified, MoE claim unsupported, kernel-only confound, pass@k sample size, unbalanced design presentation, n=700/710 discrepancy, no formal self-repair test, missing LICENSE file.

---

## Questions for Authors (Top 10 — Hardest SC PC Questions)

1. **"This is a test harness with JSON configs. What is the intellectual contribution beyond engineering?"** The kernel-centric isolation insight, failure taxonomy, and augmentation robustness instrument are the science. Prepare a 2-sentence answer.

2. **"XSBench gets 0% in ParBench too. Doesn't this undermine kernel-isolation?"** Answer: isolation removes the build-system confound but doesn't guarantee translation of arbitrarily complex kernels. XSBench marks the complexity boundary.

3. **"Your own Fisher exact test (p=0.0075) shows augmented code passes more. Why is this unreported?"** Answer: different scope (all directions vs balanced CUDA-to-OMP). If anything, augmentation helping translation strengthens the anti-memorization case.

4. **"With MDES=34.1pp, your augmentation test misses a 33pp memorization effect. How is this 'confirming benchmark validity'?"** Answer: softened language acknowledges this. The flat pass counts [16,14,17,14,16] rule out catastrophic memorization.

5. **"The prompt template isn't in the paper. How can we evaluate prompt fairness?"** Answer: will be added as appendix.

6. **"What happens when Together AI updates Qwen weights?"** Answer: acknowledge as threat, note model weights are publicly available for local serving.

7. **"You claim 96 specs but only 31 kernels are evaluated."** Answer: 96 is the framework corpus, 31 is the evaluation footprint. Both are clearly stated.

8. **"TRACY shows 23.5% of correct translations are grossly inefficient. How many of your 272 PASS are useful?"** Answer: acknowledge correctness-only limitation, note runner captures wall-clock time for future performance analysis.

9. **"Single model. How do you know difficulty tiers aren't Qwen-specific?"** Answer: benchmark paper, not model evaluation. Framework validated; multi-model evaluation is future work.

10. **"Two transforms account for 96% of augmentation applications. Is this really testing six transforms?"** Answer: acknowledge skew, note it reflects available transform sites in HPC code, not a design flaw.

---

## Cross-Talk Summary

The cross-talk round produced meaningful shifts:

- **R5 self-corrected** on 3 arguments: Fisher test is scope mismatch (not smoking gun), "96 specs" is accurate (just needs dual framing), XSBench is honestly handled (just needs abstract caveat)
- **R1-HPC** made a key insight: Fisher showing augmented > L0 actually *strengthens* anti-memorization, since memorization would predict augmented < L0
- **R2-ML** clarified: Cochran-Armitage (degradation trend) and Fisher (any L0/augmented difference) test different hypotheses — not contradictory
- **R3-STATS** confirmed: selective reporting of nulls while omitting significant tests is the strongest statistical criticism, but fixable
- **R4-REPRO** upgraded prompt missing from MINOR to MAJOR after R5's framing

**Post-cross-talk severity adjustments:**
- ARG-2 (augmentation): downgraded from "potentially devastating" to "overclaimed but fixable"
- ARG-5 (96 specs): downgraded from MAJOR to presentational MINOR
- ARG-8 (XSBench): downgraded from "internal contradiction" to "needs abstract caveat"
- ARG-9 (selective reporting): confirmed as strongest statistical criticism, fixable

---

## Priority-Ordered Fix List (April 7 Action Plan)

| Priority | Fix | Effort | Impact on Acceptance |
|----------|-----|--------|---------------------|
| P0 | Resolve GPT data (reframe as single-model recommended) | 4-6h | +20pp |
| P1 | Fix augmentation narrative (report Fisher, soften claims, report McNemar) | 4-6h | +10pp |
| P2 | Add prompt template appendix + describe anonymization | 2h | +5pp |
| P3 | Fix HeCBench spec commit hashes (25 files) | 1h | +3pp |
| P4 | Add API cost paragraph ($145.37, ~$0.13/task) | 1h | +2pp |
| P5 | Fix LaTeX compilation errors (duplicate \newcommand) | 15min | Required |
| P6 | Clarify unbalanced design in abstract | 30min | +2pp |
| P7 | Add XSBench caveat to abstract/intro | 30min | +2pp |
| P8 | Add LICENSE file | 5min | ACM AE requirement |

**Total effort for P0-P5 (must-fix): ~12-18 hours**
**Total effort for P0-P8 (all): ~14-20 hours**

---

## Individual Review Files

| Reviewer | File | Verdict |
|----------|------|---------|
| R1-HPC | `.planning/phases/15-paper-review-tools/r1-hpc-review.md` | Minor Revision |
| R2-ML | `.planning/phases/15-paper-review-tools/r2-ml-review.md` | Minor Revision* |
| R3-STATS | `.planning/phases/15-paper-review-tools/r3-stats-review.md` | Minor Revision |
| R4-REPRO | `.planning/phases/15-paper-review-tools/r4-repro-review.md` | Minor Revision |
| R5-ADVERSARY | `.planning/phases/15-paper-review-tools/r5-adversary-review.md` | Major Revision (conditional) |

*Borderline Major without GPT data.

---

*Panel report synthesized 2026-04-06 by team lead from 5 independent reviews + cross-talk deliberation.*
