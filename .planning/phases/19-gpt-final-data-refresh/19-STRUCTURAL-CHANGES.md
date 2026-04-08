# Phase 19 Structural Changes for Phase 20

Generated: 2026-04-08. All values verified against regenerated analysis JSONs.

Phase 20 must make these structural (non-numeric) edits to paper.tex, overleaf.tex, and appendices.tex. Each entry includes the file, section, approximate line range, current text, required change, and rationale.

**Key structural shift:** The cross-model comparison now covers 7 common directions (not 6 as predicted during planning). Qwen has 8 directions, GPT has 7. The intersection is 7: cuda-to-omp, cuda-to-opencl, omp-to-cuda, omp-to-opencl, omp_target-to-cuda, opencl-to-cuda, opencl-to-omp. The only GPT-missing direction is `cuda-to-omp_target` (Qwen-only).

---

## 1. Remove/Rewrite "7 of 8 Directions" Footnote

**File:** paper.tex ~line 1047-1049 / overleaf.tex ~line 1104-1106
**Section:** 6.9 Cross-Model Comparison (`\subsection{Cross-Model Comparison}`)

**Current text:**
```latex
\footnote{Cross-model comparison covers 7 of 8 evaluated
translation directions; \texttt{omp\_target}-to-CUDA GPT-4.1~mini results
were unavailable at submission.}
```

**Required change:** Remove this footnote entirely or rewrite to:
```latex
\footnote{Cross-model comparison covers 7 of 8 evaluated
translation directions; \texttt{cuda}-to-\texttt{omp\_target} GPT-4.1~mini results
are not available (Qwen-only direction).}
```

**Rationale:** omp_target-to-cuda IS now available for GPT (30.0% pass rate, 15/50). The only missing GPT direction is cuda-to-omp_target (Qwen-only, 17.5%). The footnote's claim is now inverted.

---

## 2. Update Cross-Model Direction Table

**File:** paper.tex ~line 1069-1094 / overleaf.tex ~line 1126-1151
**Section:** 6.9, Table `tab:cross-model-direction`

**Current text:** 7 rows with `CUDA -> OMP_tgt` as the last row showing "Qwen 17.5% vs GPT 0.0%, h=0.86, large"

**Required change:** Replace the table with 7 common directions using new values:

| Direction | Qwen | GPT (all levels) | h | Effect |
|-----------|------|-------------------|---|--------|
| CUDA -> OMP | 64.2% | 60.0% | 0.09 | negligible |
| OMP -> CUDA | 52.5% | 14.9% | 0.83 | large |
| OpenCL -> OMP | 38.9% | 49.3% | -0.21 | small |
| OMP -> OpenCL | 27.8% | 40.0% | -0.26 | small |
| CUDA -> OpenCL | 20.0% | 35.3% | -0.34 | small |
| OMP_tgt -> CUDA | 78.0% | 30.0% | 1.01 | large |
| OpenCL -> CUDA | 6.0% | 1.2% | 0.28 | small |

Remove the old `CUDA -> OMP_tgt` row (0.0% GPT data was from invalid Argonne batch). Add `OMP_tgt -> CUDA` row (new valid data).

Add a note that `cuda-to-omp_target` is Qwen-only (not shown in this table).

**Source:** `cross_model_comparison.json > per_direction`

---

## 3. Rewrite Effect-Size Discussion

**File:** paper.tex ~line 1146-1156 / overleaf.tex ~line 1203-1213
**Section:** 6.9, "Effect sizes" paragraph

**Current text:**
```
Cohen's h values reveal that most individual directions show negligible
practical differences: 4 of 7 directions have |h| < 0.20. The two
largest effects are OMP-to-CUDA (h = 0.75, medium) and CUDA-to-OMP
(h = 0.49, small). At the other extreme, CUDA-to-OMP_target shows
h = 0.86 (large), driven entirely by GPT-4.1 mini's 0% pass rate on
this direction.
```

**Required change:** Rewrite with new values from 7 common directions:
- **Only 1 of 7 directions has |h| < 0.20**: cuda-to-omp (h=0.086). opencl-to-omp has |h|=0.211, which exceeds the 0.20 threshold — do NOT write "2 of 7".
- The two largest effects are now: omp_target-to-cuda (h=1.01, large) and omp-to-cuda (h=0.83, large)
- The `cuda-to-omp_target h=0.86` reference must be removed (no longer a common direction)
- New overall Cohen's h = 0.137 (negligible), down from 0.19

**CORRECTION NOTE (adversarial review 2026-04-08):** An earlier draft of this item incorrectly listed "2 of 7" (citing opencl-to-omp as borderline). The actual value is h=-0.2107 (|h|=0.2107 > 0.20). The correct count is 1 of 7 directions with |h| < 0.20.

**Source:** `cross_model_comparison.json > per_direction > [each].cohens_h`

---

## 4. Update Per-Direction Table Rows

**File:** paper.tex ~line 955-974 / overleaf.tex ~line 987-1006
**Section:** 6.6, Table `tab:direction-rates`

**Current text:** Two "case study" rows at the bottom:
```latex
cuda-to-omp\_target & -- & -- & -- & 8 & Case study \\
omp\_target-to-cuda & -- & -- & -- & 10 & Case study \\
```

**Required change:**
- `cuda-to-omp_target` row: Add Qwen data (17.5%, 7/40, [9.0%, 31.0%]). GPT column stays "--" (no GPT cuda-to-omp_target data).
- `omp_target-to-cuda` row: Add both Qwen (78.0%, 39/50) and GPT (30.0%, 15/50, [19.1%, 43.8%]) data.
- Also update the GPT column in existing rows with new GPT numbers (some totals changed due to HeCBench additions):
  - cuda-to-omp: GPT 60.0% (48/80) [49.0%, 70.0%] (was 40.0% 48/120)
  - omp-to-cuda: GPT 14.9% (16/107) [9.4%, 22.9%] (was 17.9% 15/84)
  - opencl-to-omp: GPT 49.3% (37/75) [38.3%, 60.4%] (was 41.1% 37/90)
  - omp-to-opencl: GPT 40.0% (30/75) [29.7%, 51.3%] (was 33.3% 30/90)
  - cuda-to-opencl: GPT 35.3% (30/85) [26.0%, 45.9%] (was 30.0% 30/100)
  - opencl-to-cuda: GPT 1.2% (1/85) [0.2%, 6.4%] (was 3.7% 1/27)

**Source:** `paper_data_gpt41mini.json > primary_campaign > by_direction`

---

## 5. Flag XSBench Coverage Reduction

**File:** paper.tex cross-suite analysis section and any XSBench references
**Section:** Wherever XSBench GPT coverage is referenced

**Current state:** Paper referenced 38 XSBench files for GPT (from old 897-file dataset).

**Required change:** GPT XSBench went from 38 files to 6 files (32 deleted, 0 added). The 6 remaining files are all `*-to-cuda` directions. The F6 cross-suite comparison figure already reflects this (GPT XSBench shows 0/0 in L0 figure). Phase 20 must:
- Qualify any XSBench cross-model comparison noting the coverage asymmetry (Qwen: 48 XSBench files, GPT: 6)
- If there is a per-suite GPT breakdown, update XSBench numbers
- Note that the invalid XSBench data was due to missing xsbench-src on the Argonne evaluation machine

**Source:** On-disk file counts; `paper_data_gpt41mini.json > by_suite` if present

---

## 6. Update Abstract GPT Numbers

**File:** paper.tex ~line 168 / overleaf.tex ~line 172
**Section:** 1 Introduction, "Failure taxonomy reveals API syntax as the bottleneck" paragraph

**Current text:**
```
GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks;
the difference is statistically significant ($\chi^2 = 10.97$, $p < 0.001$)
but the effect size is negligible (Cohen's $h = 0.19$)
```

**Required change:**
```
GPT-4.1~mini achieves 31.8\% [28.1\%, 35.8\%] across 557 tasks;
the difference is statistically significant ($\chi^2 = 5.54$, $p = 0.019$)
but the effect size is negligible (Cohen's $h = 0.14$)
```

**Note:** p-value changed from < 0.001 to 0.019. Still significant at alpha=0.05, but the notation must change from "$p < 0.001$" to "$p = 0.019$".

**Source:** `paper_data_gpt41mini.json > primary_campaign > overall`; `cross_model_comparison.json > overall`

---

## 7. Update Overall Pass Rates Table

**File:** paper.tex ~line 697-711 / overleaf.tex ~line 740-760
**Section:** 6.1, Table `tab:overall-pass`

**Current GPT row:**
```
GPT-4.1 mini & 161 & 316 & 43 & 31 & 0 & 0 & 551 & 29.2\% & [25.6\%, 33.2\%]
```

**Required GPT row:**
```
GPT-4.1 mini & 177 & 247 & 54 & 79 & 0 & 0 & 557 & 31.8\% & [28.1\%, 35.8\%]
```

**Required Aggregate row:** Recalculate: 272+177=449 PASS, 241+247=488 BF, 144+54=198 RF, 51+79=130 VF, 1+0=1 EF, 1+0=1 ERR, total=1267. Rate=449/1267=35.4%. Wilson CI must be recomputed.

**Also update prose at ~line 714:**
- "GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks" -> "GPT-4.1~mini achieves 31.8\% [28.1\%, 35.8\%] across 557 tasks"
- "BUILD_FAIL as its dominant failure mode at 57.4\% (316/551)" -> "BUILD_FAIL as its dominant failure mode at 44.3\% (247/557)"
- "chi-squared test ($\chi^2 = 10.97$, $df = 1$, $p < 0.001$)" -> "chi-squared test ($\chi^2 = 5.54$, $df = 1$, $p = 0.019$)"
- "Cohen's $h = 0.19$" -> "Cohen's $h = 0.14$"

**Also update the standalone chi-squared paragraph at ~line 719:**
- "$\chi^2 = 10.97$ ($df = 1$, $p < 0.001$)" -> "$\chi^2 = 5.54$ ($df = 1$, $p = 0.019$)"
- "Cohen's $h = 0.19$" -> "Cohen's $h = 0.14$"

**Source:** `paper_data_gpt41mini.json > primary_campaign > overall`

---

## 8. Update Failure Taxonomy Comparison

**File:** paper.tex ~line 1109-1126 / overleaf.tex ~line 1165-1182
**Section:** 6.9, "Failure taxonomy comparison" paragraph

**Current text:**
```
build failures dominate both models but more severely affect GPT-4.1 mini:
BUILD_FAIL accounts for 81.0% of GPT failures (316/390) versus 55.0% of
Qwen failures (241/438). As a fraction of all tasks, GPT-4.1 mini
encounters build failures on 57.4% of tasks (316/551)
```

**Required change:**
```
build failures dominate both models but more severely affect GPT-4.1 mini:
BUILD_FAIL accounts for 65.0% of GPT failures (247/380) versus 55.0% of
Qwen failures (241/438). As a fraction of all tasks, GPT-4.1 mini
encounters build failures on 44.3% of tasks (247/557)
```

Also update:
- "missing target API references (196 instances)" -> now 62 GPT instances (was inflated by invalid Argonne data)
- "missing headers (168 instances)" -> now 151 GPT instances
- "VERIFY_FAIL 7.2% for Qwen versus 5.6% for GPT" -> "7.2% for Qwen versus 14.2% for GPT (79/557)"

**Note:** The narrative structure changes: GPT BUILD_FAIL severity is now less extreme (65.0% vs 81.0% of failures). VERIFY_FAIL is now higher for GPT than Qwen (14.2% vs 7.2%), reversing the comparison. The top GPT build failure subcategory is now missing_header (151), not missing_target_api (62).

**Source:** `paper_data_gpt41mini.json > primary_campaign > overall > by_status`; `error_taxonomy.json > build_fail_categories > [cat] > by_model`

---

## 9. Update Per-Kernel Agreement

**File:** paper.tex ~line 1131-1144 / overleaf.tex ~line 1187-1200
**Section:** 6.9, "Per-kernel agreement" paragraph

**Current text:**
```
Across 31 kernels evaluated by both models, 13 are solved by both
(backprop, bfs, cfd, hotspot, hotspot3d, lavamd, lud, nn, nw,
particlefilter, pathfinder, srad, streamcluster), 5 are failed by both
(convolution1d, heartwall, myocyte, rsbench, xsbench), 11 are solved by
Qwen only (bptree, floydwarshall, heat2d, iso2dfd, jacobi, md, mixbench,
nqueen, page-rank, scan, stencil1d), and 2 are solved by GPT only (dwt2d,
gaussian).
```

**Required change:**
```
Across 29 kernels evaluated by both models, 18 are solved by both
(backprop, bfs, cfd, heat2d, hotspot, hotspot3d, jacobi, lavamd, lud, md,
mixbench, nn, nw, page-rank, particlefilter, pathfinder, srad,
streamcluster), 4 are failed by both (convolution1d, gaussian, heartwall,
myocyte), 6 are solved by Qwen only (bptree, floydwarshall, iso2dfd,
nqueen, scan, stencil1d), and 1 is solved by GPT only (dwt2d).
```

**Key changes:**
- 31 -> 29 common kernels (rsbench and xsbench no longer common due to GPT coverage reduction)
- 13 -> 18 both-pass (heat2d, jacobi, md, mixbench, page-rank moved from qwen-only to both-pass)
- 5 -> 4 both-fail (rsbench, xsbench dropped; gaussian moved from GPT-only to both-fail)
- 11 -> 6 qwen-only (heat2d, jacobi, md, mixbench, page-rank moved to both-pass)
- 2 -> 1 gpt-only (gaussian moved to both-fail)
- The "11-vs.-2 asymmetry" becomes "6-vs.-1 asymmetry"

**Source:** `cross_model_comparison.json > per_kernel_matrix`

---

## 10. Update Cross-Model Intro Paragraph (NEW — coverage gap found in adversarial review)

**File:** paper.tex ~line 1050-1060 / overleaf.tex ~line 1107-1117
**Section:** 6.9, opening paragraph after the footnote

**Current text:**
```
Across all evaluated tasks, Qwen~3.5 achieves 38.3\% (272/710) and
GPT-4.1~mini achieves 29.2\% (161/551). A chi-squared test of homogeneity
yields $\chi^2 = 10.97$ ($\mathit{df} = 1$, $p = 9.3 \times 10^{-4}$),
indicating a statistically significant difference. However, Cohen's $h = 0.19$
(negligible effect size) indicates that the practical magnitude of the
difference is modest.
```

**Required change:**
```
Across all evaluated tasks, Qwen~3.5 achieves 38.3\% (272/710) and
GPT-4.1~mini achieves 31.8\% (177/557). A chi-squared test of homogeneity
yields $\chi^2 = 5.54$ ($\mathit{df} = 1$, $p = 0.019$),
indicating a statistically significant difference. However, Cohen's $h = 0.14$
(negligible effect size) indicates that the practical magnitude of the
difference is modest.
```

**Source:** `cross_model_comparison.json > overall`

---

## 11. Update Abstract GPT Numbers (NEW — coverage gap found in adversarial review)

**File:** paper.tex ~line 82 / overleaf.tex ~line 82
**Section:** Abstract

**Current text:**
```
GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks
($\chi^2 = 10.97$, $p < 0.001$, Cohen's $h = 0.19$)
```

**Required change:**
```
GPT-4.1~mini achieves 31.8\% [28.1\%, 35.8\%] across 557 tasks
($\chi^2 = 5.54$, $p = 0.019$, Cohen's $h = 0.14$)
```

**Note:** The abstract also contains `% src: cross_model_comparison.json > overall: gpt 161/551=0.2922, chi2=10.97, p=0.000926, h=0.1926` — update the comment to reflect new values.

**Source:** `cross_model_comparison.json > overall`; `paper_data_gpt41mini.json > primary_campaign > overall`

---

## 12. Update Discussion GPT Reference (NEW — coverage gap found in adversarial review)

**File:** paper.tex ~line 1176 / overleaf.tex ~line 1233
**Section:** 7 (Discussion), "Model capability spectrum" paragraph

**Current text:**
```
GPT-4.1~mini, a smaller dense model from a different provider, achieves
29.2\% overall---demonstrating that ParBench can differentiate model
capabilities across architectures (Section~\ref{sec:cross-model}).
% src: paper_data_gpt41mini.json > overall: 161/551=0.2922
```

**Required change:**
```
GPT-4.1~mini, a smaller dense model from a different provider, achieves
31.8\% overall---demonstrating that ParBench can differentiate model
capabilities across architectures (Section~\ref{sec:cross-model}).
% src: paper_data_gpt41mini.json > overall: 177/557=0.3178
```

**Source:** `paper_data_gpt41mini.json > primary_campaign > overall`

---

## 13. Update Conclusion GPT Reference (NEW — coverage gap found in adversarial review)

**File:** paper.tex ~line 1252 / overleaf.tex ~line 1309
**Section:** 8 (Conclusion), third contribution paragraph

**Current text:**
```
GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks ($p < 0.001$),
confirming that the framework generalizes across providers.
% src: paper_data_gpt41mini.json > overall: 161/551=0.2922; cross_model_comparison.json > overall > chi_squared > p_value=0.000926
```

**Required change:**
```
GPT-4.1~mini achieves 31.8\% [28.1\%, 35.8\%] across 557 tasks ($p = 0.019$),
confirming that the framework generalizes across providers.
% src: paper_data_gpt41mini.json > overall: 177/557=0.3178; cross_model_comparison.json > overall > chi_squared > p_value=0.01859
```

**Source:** `paper_data_gpt41mini.json > primary_campaign > overall`; `cross_model_comparison.json > overall`

---

## Summary of New Cross-Model Statistics

For convenient reference, all cross-model values Phase 20 needs:

| Metric | Old Value | New Value | Source |
|--------|-----------|-----------|--------|
| GPT total tasks | 551 | 557 | paper_data_gpt41mini.json > overall.total |
| GPT pass | 161 | 177 | paper_data_gpt41mini.json > overall.pass |
| GPT pass rate | 29.2% | 31.8% | paper_data_gpt41mini.json > overall.pass_rate |
| GPT CI | [25.6%, 33.2%] | [28.1%, 35.8%] | paper_data_gpt41mini.json > overall.ci_lower/ci_upper |
| GPT BUILD_FAIL | 316 (57.4%) | 247 (44.3%) | paper_data_gpt41mini.json > overall.by_status |
| GPT RUN_FAIL | 43 | 54 | paper_data_gpt41mini.json > overall.by_status |
| GPT VERIFY_FAIL | 31 (5.6%) | 79 (14.2%) | paper_data_gpt41mini.json > overall.by_status |
| Combined total | 1,261 | 1,267 | 710 + 557 |
| Combined pass | 433 | 449 | 272 + 177 |
| Combined rate | 34.3% | 35.4% | 449/1267 |
| Chi-squared | 10.97 | 5.54 | cross_model_comparison.json > overall.chi_squared.chi2 |
| p-value | 0.000926 | 0.01859 | cross_model_comparison.json > overall.chi_squared.p_value |
| Cohen's h | 0.19 | 0.137 | cross_model_comparison.json > overall.cohens_h |
| Common directions | 7 | 7 | cross_model_comparison.json > per_direction (7 keys) |
| Missing GPT direction | omp_target-to-cuda | cuda-to-omp_target | cross_model_comparison.json > missing_directions |
| Common kernels | 31 | 29 | cross_model_comparison.json > per_kernel_matrix |
| Both-pass kernels | 13 | 18 | cross_model_comparison.json > per_kernel_matrix.counts |
| Both-fail kernels | 5 | 4 | cross_model_comparison.json > per_kernel_matrix.counts |
| Qwen-only kernels | 11 | 6 | cross_model_comparison.json > per_kernel_matrix.counts |
| GPT-only kernels | 2 | 1 | cross_model_comparison.json > per_kernel_matrix.counts |
