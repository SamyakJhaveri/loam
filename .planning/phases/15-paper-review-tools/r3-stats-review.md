# R3-STATS: Statistical Rigor and Benchmarking Methodology Review

**Reviewer:** R3-STATS (Benchmarking Methodologist / Statistician)
**Paper:** ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness
**Scope:** S6 Results (lines 662-989), S7 Discussion (lines 991-1068), cross-referenced against `statistical_analysis.json`, `paper_data.json`, `quantitative_findings.json`
**Date:** 2026-04-06

---

## 1. Summary

The paper's statistical methodology is generally sound and notably honest about its limitations. The authors correctly apply Wilson confidence intervals, Cochran-Armitage trend tests, McNemar's exact tests, and chi-squared tests for the claims they make. Numerical values have been independently verified against the data files and all check out. The principal concern is not incorrect statistics but rather *underpowered* statistics: several null results are presented alongside claims that implicitly treat non-rejection of H0 as evidence for H0, despite the authors' own power analysis revealing very large minimum detectable effect sizes. The paper would benefit from a more structured presentation of power limitations and from reporting the omp_target McNemar pair that is currently included in the Bonferroni correction but not reported in the text.

## 2. Verdict

**Minor Revision**

The statistics are correctly computed and the methodology is appropriate for the experimental design. Issues are presentational and interpretive rather than computational. Two items rise to MAJOR level: the underpowered augmentation test being used as affirmative evidence against memorization, and the omission of a tested McNemar pair from the reported results. All others are MINOR.

---

## 3. Findings Table

| # | Item | Verdict | Details |
|---|------|---------|---------|
| 1 | Confidence Intervals | PASS | Wilson CIs correctly computed; method explicitly stated (line 986). Verified: 272/710 = [0.3481, 0.4194]. Wilson is the right choice for proportions near boundaries (0%, 100%). Per-kernel CIs also use Wilson. |
| 2 | Cochran-Armitage Trend Test | MAJOR | Test is appropriate for ordered augmentation levels. z=0.0, p=1.0 verified against data (pass counts [16,14,17,14,16] on balanced n=24/level). However, the "perfect" null (z exactly 0.0) combined with MDES=34.1pp at 80% power means this test cannot detect any effect smaller than ~34pp. The paper uses this null to argue against memorization (lines 910-911), which overinterprets an underpowered result. See Section 4.2. |
| 3 | McNemar's Test | MINOR | McNemar's exact test is appropriate for paired direction comparison. All four p-values independently verified: cuda-omp/omp-cuda p=0.6875 (6 discordant), cuda-opencl/opencl-cuda p=0.6875 (6 discordant), opencl-omp/omp-opencl p=1.0 (9 discordant), cuda-omp_target/omp_target-cuda p=0.0625 (5 discordant). The fourth test is included in Bonferroni correction but NOT reported in the text body -- only three pairs are shown (line 946). This omission is problematic because the fourth pair has h=-1.37 (large) and p=0.0625, which borders on significance even after correction. See Section 4.3. |
| 4 | Bonferroni Correction | MINOR | alpha=0.05/4=0.0125 is correctly computed for 4 tests. However, the choice to include the omp_target pair (a "case study" direction per Table 4) in the family-wise correction while not reporting its individual results creates an asymmetry: the correction penalizes the three reported tests for a fourth test that readers cannot evaluate. |
| 5 | Chi-Squared Test | MINOR | chi2=82.73, p<0.001, dof=3 independently verified against contingency table in quantitative_findings.json. Min expected cell=19.0 (above the rule-of-thumb threshold of 5). The test is on a 4x2 table (4 complexity classes x pass/fail), but the paper text collapses this to a 2-group claim ("single-file 51.3% vs multi-file 22.2%"). The 4-class chi-squared overstates significance for the binary claim -- a 2x2 test on single vs. multi would still be significant but with a different test statistic. Note: n=700 not n=710 (10 unclassified tasks); this discrepancy is not flagged in the paper. |
| 6 | Effect Sizes | PASS | Cohen's h values independently verified: 0.17, 0.28, 0.12 for the three standard pairs. Interpretations (small to medium) follow Cohen's conventions. The paper correctly notes these suggest "meaningful asymmetry may exist" (line 946). The fourth pair (h=-1.37, large) is not reported. |
| 7 | Sample Size & Power | MAJOR | n=710 is reasonable for overall analyses. n=24 per level for augmentation is acknowledged as underpowered (MDES=34.1pp). McNemar tests with 5-9 discordant pairs are severely underpowered. The paper's power caveat (lines 1033-1042) is commendable but the Discussion section (line 1022) still uses the Cochran-Armitage null as "evidence against the memorization hypothesis." The power analysis should appear BEFORE the interpretive claim, not just in Threats to Validity. |
| 8 | Pass@k Methodology | PASS | The unbiased estimator from Chen et al. (HumanEval) is correctly cited and applied. n=3 samples at temperature=0.7 is modest but standard for code generation. The paper correctly states "zero-shot per sample" (max_retries=1 = no retry). The bimodal distribution finding (72.5% hard, 15.5% partial, 12.0% all-pass, 0% noisy) is a genuine insight. |
| 9 | Multiple Testing | MINOR | Bonferroni is applied for McNemar tests. No correction is applied to per-kernel CIs (31 kernels, Table 3 / Appendix), which is standard practice for descriptive CIs but should be noted if any individual kernel CI is used for inferential claims. The chi-squared augmentation test (chi2=10.34, p=0.035, dof=4, n=192) in statistical_analysis.json is NOT reported in the paper; it tests augmentation level independence across all directions for Qwen and has p=0.035 uncorrected (p=0.070 after Bonferroni for 2 tests). The associated Fisher exact test (L0 vs augmented, p=0.0037) is also unreported. These tests potentially contradict the Cochran-Armitage null and should be acknowledged. |
| 10 | Statistical Presentation | PASS | P-values, test statistics, effect sizes, and CIs are consistently reported. Wilson CI method is named. Cochran-Armitage z and p are given. McNemar p-values with Bonferroni correction are stated. Presentation follows IEEE conventions. Source provenance comments in LaTeX are exemplary. |
| 11 | Augmentation Robustness Design | MINOR | The balanced CUDA-to-OMP subset (n=24/level) is the right design choice -- it controls for direction as a confound. However, the ceiling effect concern is real: at 64.2% overall pass rate for this direction, there is substantial room for both improvement and degradation, so a ceiling/floor effect is unlikely to be masking a trend. The bigger issue is the per-level n=24 (only 14-17 passes per level), giving very wide per-level CIs. |
| 12 | Self-Repair Statistics | PASS | "70% relative increase" (22.5% to 38.3%) is arithmetically correct: (272-160)/160=0.70. The absolute increase is 15.8pp, which provides context. The 7/710 regression rate (1.0%) is appropriately small. The paper reports both first-attempt CI [19.6%, 25.8%] and final CI [34.8%, 41.9%]; the non-overlap of these CIs provides informal evidence of meaningful improvement without formal testing (which is fine here since the comparison is within-subjects and not independent). |

---

## 4. Statistical Issues (Detailed Analysis)

### 4.1 Confidence Intervals -- PASS

Wilson score intervals are the gold standard for binomial proportions, especially when rates approach 0% or 100% (as with stencil1d at 100% or xsbench at 0%). Independently verified:
- 272/710: Wilson CI = [34.81%, 41.94%] -- matches paper's [34.8%, 41.9%]
- Method is explicitly stated (line 986): "Wilson confidence intervals are preferred over Wald intervals because they provide better coverage near boundary proportions."

No issues.

### 4.2 Cochran-Armitage Trend Test -- MAJOR

**Correctness:** The test is correctly applied. Pass counts [16, 14, 17, 14, 16] on n=24/level yield z=-0.0, p=1.0. This is verified: the weighted sum of deviations from the mean proportion is exactly zero because the pass counts are symmetric around the center level (sum = 77, mean per level = 15.4, but the linear contrast weights [0,1,2,3,4] applied to deviations yield exactly 0).

**Interpretation concern:** The z=0.0, p=1.0 result is "too perfect" -- it reflects that the pass counts happen to be perfectly symmetric under the linear contrast, NOT that augmentation has zero effect. The authors correctly note this in the MDES paragraph (lines 896-908) but then the Discussion section (line 1022) states the null result provides "evidence against the memorization hypothesis." This is a logical overreach: absence of evidence is not evidence of absence, especially when MDES=34.1pp.

**Recommendation:** The memorization argument should be reframed as "consistent with" rather than "evidence against." The paper already does this partially in the Results section but reverts to the stronger framing in the Discussion.

### 4.3 McNemar's Test -- MINOR (bordering MAJOR)

**Correctness:** All four McNemar exact tests verified. The exact binomial test on discordant pairs is the appropriate method given the small discordant counts (5-9).

**Omission issue:** The paper reports three McNemar tests (line 946) but applies Bonferroni correction for four tests (line 944, "four direction pairs (including the omp_target case-study pair)"). The fourth test -- cuda-to-omp_target vs omp_target-to-cuda -- has:
- n_paired = 8, discordant = 5 (all reverse_only)
- p = 0.0625 (uncorrected), p = 0.25 (corrected)
- Cohen's h = -1.37 (large effect)
- Forward rate: 12.5%, Reverse rate: 75.0%

This is the most interesting pair statistically -- it shows a large effect that approaches significance even with n=8. The paper labels these as "case study" directions (Table 4) and doesn't report pass rates for them, but includes the test in the correction family. This should either be reported or excluded from the Bonferroni count.

### 4.4 Bonferroni Correction -- MINOR

The correction is correctly applied. The conservative choice of Bonferroni (vs. Holm-Bonferroni, which would be slightly more powerful) is reasonable given only 4 tests. However, the inclusion/exclusion asymmetry described in 4.3 should be resolved.

### 4.5 Chi-Squared Test (Multi-File Complexity) -- MINOR

**Correctness:** chi2=82.73, p<0.001, dof=3 verified. The contingency table [195/185, 49/86, 18/117, 4/46] on n=700 produces this result. Min expected cell = 19.0, comfortably above the chi-squared applicability threshold.

**Presentation issue:** The paper text (line 129) claims "single-file translations achieve 51.3% pass rate versus 22.2% for multi-file translations (chi2=82.73, p<0.001)" -- this collapses 4 complexity classes into 2 for the prose claim but uses the 4-class test statistic. A reviewer might question whether the 4-class chi-squared is the right citation for a 2-class claim. The 4-class test is strictly more informative (it shows the gradient across complexity classes), so the test is valid, but the presentation conflates the two granularities.

**Sample size note:** The test uses n=700, not n=710. Ten tasks are "unclassified" in the complexity correlation. This is not mentioned in the paper text. The discrepancy should be footnoted.

### 4.6 Effect Sizes -- PASS

Cohen's h values are correctly computed using the standard formula h = 2*arcsin(sqrt(p1)) - 2*arcsin(sqrt(p2)):
- cuda-to-omp vs omp-to-cuda: h = 0.1724 (small) -- paper says -0.17
- cuda-to-opencl vs opencl-to-cuda: h = 0.2838 (small-to-medium) -- paper says 0.28
- opencl-to-omp vs omp-to-opencl: h = 0.1157 (small) -- paper says 0.12

Note: The sign of Cohen's h for cuda-omp/omp-cuda is reported as -0.17 in the paper (line 946), reflecting the convention forward minus reverse. The JSON has 0.1724. The paper's negative sign is correct if the "forward" direction is omp-to-cuda (as labeled in the JSON: "pair": "cuda-to-omp vs omp-to-cuda" with forward_direction="cuda-to-omp"). The sign simply indicates which direction has the higher rate; magnitude is what matters for interpretation.

### 4.7 Unreported Chi-Squared Augmentation Test

The `statistical_analysis.json` file contains a chi-squared test on augmentation levels for the full Qwen model (chi2=10.34, p=0.035, dof=4, n=192). After Bonferroni correction (2 tests), p=0.070, not significant at alpha=0.05.

There is also a Fisher exact test comparing L0 (40/96 pass) vs all augmented levels combined (61/96 pass): OR=0.41, p=0.0037 (corrected p=0.0075). This IS significant at alpha=0.05 after correction.

**This is a potential contradiction:** The Cochran-Armitage finds no linear trend (z=0.0, p=1.0) in the balanced CUDA-to-OMP subset, but a Fisher exact test on a broader dataset finds L0 performs WORSE than augmented levels (p=0.0075). The reconciliation is likely that (a) these tests are on different scopes (balanced subset vs all data), and (b) Cochran-Armitage tests for a monotonic linear trend while Fisher tests for any L0 vs. non-L0 difference. But the existence of a significant L0 vs. augmented difference in the broader data should be acknowledged, as it complicates the "augmentation invariance" narrative.

**Recommendation:** Report the Fisher exact test result or explain why the broader scope is excluded from the augmentation analysis.

---

## 5. Strengths

- **Exemplary source provenance:** Every statistical claim in the LaTeX source includes a comment tracing it to a specific JSON field. This is rare and commendable.
- **Honest power analysis:** The MDES=34.1pp disclosure (lines 896-908) is a genuine strength. Many papers would simply report the null result and move on.
- **Correct CI method:** Wilson score intervals throughout, explicitly named and justified.
- **Appropriate test selection:** Cochran-Armitage for ordered trend, McNemar for paired comparisons, chi-squared for contingency tables -- all match the data structure.
- **Non-significance correctly flagged:** "All three tests fail to reject the null hypothesis of symmetry" (line 946) -- correct phrasing.
- **McNemar power caveat:** Lines 949-953 explicitly state the discordant-pair limitation.
- **Threats to Validity section:** Comprehensive and honest. Statistical power is the first threat listed.

## 6. Weaknesses

- **(MAJOR) Underpowered augmentation test used as affirmative evidence.** The Discussion (line 1022) argues the Cochran-Armitage null provides "evidence against the memorization hypothesis." Given MDES=34.1pp, this overinterprets a null result. The correction is straightforward: soften to "consistent with" rather than "evidence against."
- **(MAJOR) Unreported McNemar test included in correction.** The omp_target McNemar pair (h=-1.37, p=0.0625) is included in the Bonferroni family but not reported. This is the most statistically interesting pair (large effect, near-significant). Either report it or exclude it from the correction.
- **(MINOR) Unreported Fisher exact test contradicts narrative.** The significant L0-vs-augmented Fisher test (p=0.0075) in statistical_analysis.json is not discussed. If L0 genuinely performs worse than augmented levels, this complicates the "augmentation invariance" claim.
- **(MINOR) Chi-squared granularity mismatch.** 4-class test statistic cited for a 2-class prose claim. Not incorrect, but potentially confusing to reviewers.
- **(MINOR) n=700 vs n=710 undisclosed.** The chi-squared complexity correlation test excludes 10 tasks without explanation.
- **(MINOR) No formal test for self-repair improvement.** The first-attempt (22.5%) to final (38.3%) improvement is presented descriptively with non-overlapping CIs. A McNemar test on the 710 paired observations would formalize this.

## 7. Questions for Authors

1. **Why is the omp_target McNemar test included in the Bonferroni family but not reported?** The h=-1.37 effect size is the largest of any pair and approaches significance (p=0.0625 uncorrected). Is this omission intentional, and if so, why?

2. **Can you reconcile the Cochran-Armitage null (z=0.0, p=1.0 on balanced CUDA-to-OMP) with the Fisher exact test (L0 vs augmented, p=0.0037 on broader data)?** Both are in your data files. Does augmentation improve pass rates on non-CUDA-to-OMP directions?

3. **What is the z=0.0 result "really" telling us?** The pass counts [16,14,17,14,16] sum symmetrically under linear contrast weights. Is this a coincidence of the specific kernel set, or does it reflect a genuine structural property? Would a non-linear trend test (e.g., quadratic contrast) detect a U-shaped pattern?

4. **Can you provide a power analysis for the McNemar tests?** With 5-9 discordant pairs, what effect size (in percentage-point asymmetry) would be detectable at 80% power?

5. **What are the 10 unclassified tasks** excluded from the multi-file chi-squared (n=700 vs n=710)?

6. **Would you consider reporting pass rate CIs per augmentation level** for the balanced subset? The raw counts [16,14,17,14,16] out of 24 give point estimates of 66.7%, 58.3%, 70.8%, 58.3%, 66.7% -- these have overlapping CIs approximately [47%, 82%], making the null result unsurprising visually.

7. **The "70% relative increase" for self-repair -- is there a risk this metric is misleading?** A move from 1% to 1.7% would also be a "70% relative increase." Consider reporting both the absolute (15.8pp) and relative (70%) figures side by side, with the absolute figure first.

## 8. Recommendations

### Priority 1 (before submission)

1. **Soften the memorization argument in Discussion.** Change "evidence against the memorization hypothesis" (line 1022) to "consistent with the hypothesis that the model does not rely on memorized surface patterns." Add a parenthetical citing the MDES limitation.

2. **Report or exclude the omp_target McNemar test.** Either:
   - (a) Add a sentence reporting the fourth McNemar result (h=-1.37, p=0.0625) and note it as suggestive but not significant after correction, OR
   - (b) Remove the omp_target pair from the Bonferroni correction (changing alpha from 0.05/4 to 0.05/3=0.0167) and note it is excluded as a case-study direction.

3. **Footnote the n=700 vs n=710 discrepancy** for the chi-squared complexity correlation test.

### Priority 2 (strengthen the paper)

4. **Acknowledge the Fisher exact test result** from statistical_analysis.json (L0 vs augmented, p=0.0037). Even a brief note that "a Fisher exact test comparing L0 to pooled L1-L4 on the broader dataset yields p=0.007 after correction, but this comparison conflates augmentation level with direction composition and should be interpreted cautiously" would preempt a sharp reviewer.

5. **Add per-level CI bars** to the augmentation trend figure (Appendix). Showing the wide CIs visually reinforces the power limitation.

6. **Report the absolute self-repair improvement (15.8pp)** alongside the relative (70%) figure. The relative figure is eye-catching but can be misleading without the absolute context.

7. **Consider a non-parametric permutation test** for augmentation robustness as a sensitivity analysis alongside Cochran-Armitage. This would provide a second, assumption-free estimate.

### Priority 3 (nice to have)

8. **Post-hoc power analysis for McNemar tests.** For each pair, compute the minimum detectable rate difference at 80% power given the observed number of discordant pairs. This quantifies "how large an asymmetry would we need to detect?"

9. **Report Cramer's V** for the multi-file chi-squared alongside the chi-squared statistic. chi2=82.73 on n=700 corresponds to a moderate effect. This is already computed in the JSON (V=0.23, "small") for the augmentation chi-squared; compute the equivalent for the multi-file test.

---

*Review generated: 2026-04-06 by R3-STATS agent*
