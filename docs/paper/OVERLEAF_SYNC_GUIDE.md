# Overleaf Sync Guide: GPT-5.3-codex Integration

**Date:** 2026-05-01
**Purpose:** Exact instructions for manually applying all local changes to the Overleaf document.

---

## Overview

This session integrated GPT-5.3-codex as a third model into the NeurIPS 2026 paper. Changes span 10 files + 8 new figure files + 1 updated figure + 1 regenerated table. Every change below is listed in the order you should apply it.

**Total files modified:** 10 LaTeX/bib files, 1 Python script
**New files to upload:** 8 codex figure PDFs/PNGs
**Updated files to re-upload:** f7_augmentation_robustness.pdf, f7_augmentation_robustness.png, t2_model_comparison.tex

---

## PART 1: Files to Upload to Overleaf

### 1A. NEW Figure Files (upload to `figures/` directory)

Upload these 8 files from `docs/paper/NeurIPS_ready_version/figures/`:

| File | What it is |
|------|-----------|
| `f3_kernel_model_heatmap_codex.pdf` | Per-kernel heatmap (Codex) |
| `f3_kernel_model_heatmap_codex.png` | PNG version |
| `f4_failure_taxonomy_codex.pdf` | Failure taxonomy (Codex) |
| `f4_failure_taxonomy_codex.png` | PNG version |
| `f5_pass_at_k_by_direction_codex.pdf` | pass@k by direction (Codex) |
| `f5_pass_at_k_by_direction_codex.png` | PNG version |
| `f6_cross_suite_comparison_codex.pdf` | Cross-suite comparison (Codex) |
| `f6_cross_suite_comparison_codex.png` | PNG version |

### 1B. UPDATED Figure Files (re-upload, replacing existing)

| File | What changed |
|------|-------------|
| `f7_augmentation_robustness.pdf` | Now has 3 lines (added Codex) instead of 2 |
| `f7_augmentation_robustness.png` | Same |

### 1C. UPDATED Table File (re-upload, replacing existing)

| File | What changed |
|------|-------------|
| `t2_model_comparison.tex` | Now has 3 model rows (added Codex) instead of 2 |

---

## PART 2: macros.tex

**Location:** `sections/macros.tex`

**Add these 2 lines** after line 8 (after `\newcommand{\gptprovider}{Azure~OpenAI}`):

```latex
\newcommand{\codex}{GPT-5.3-codex}
\newcommand{\codexshort}{Codex}
```

---

## PART 3: references.bib

**Location:** `references.bib`

**Add this entry** at the end of the file:

```bibtex
@misc{GPT53Codex2026,
  title   = {{GPT}-5.3-Codex System Card},
  author  = {{OpenAI}},
  year    = {2026},
  url     = {https://openai.com/index/gpt-5-3-codex-system-card/},
  note    = {Accessed 2026-05-01}
}
```

---

## PART 4: abstract.tex

**Location:** `sections/abstract.tex`

**REPLACE** the paragraph starting with "Under stochastic sampling..." (the entire second paragraph, after the corpus description). The old text mentions only Qwen and GPT-5.4 separately.

**New text (entire second paragraph):**

```latex
% src: paper_data_*.json > passk_campaign > aggregate_passk; statistical_analysis.json > model_comparison > pairwise[0]
Under stochastic sampling (temperature~0.7, three independent attempts per task), pass@1 ranges from 23.9\% (\qwenshort{}) to 62.7\% (shared by \gptnew{} and \codexshort{}) over 142~unique source-target pairs, with the code-specialized \codexshort{} performing indistinguishably from the general-purpose \gptnew{} ($p = 1.0$, OR\,=\,0.93). Build-stage adaptation failures account for 50.0\% of \qwenshort{} L0 outcomes, making incomplete API-surface mapping the dominant bottleneck. On L0-conditional augmentation subsets, pass rates show no evidence of memorization-dependent degradation for the GPT models. \parbench{} exposes both current capability and the structural barriers---direction asymmetry, multi-file coordination, and incomplete API adaptation---that remain for reliable parallel code translation.
```

---

## PART 5: 1-introduction.tex

**Location:** `sections/1-introduction.tex`

### 5A. Outline comment (around line 23)

**Find:**
```
%   3. Empirical characterization: 1,448 records, two models, key findings
```

**Replace with:**
```
%   3. Empirical characterization: 2,262 records, three models, key findings
%      (a) real capability revealed, (b) build-stage adaptation dominant,
%      (c) direction dependence, (d) augmentation stability, (e) code-specialized ≈ general-purpose
```

### 5B. Contribution #3 (inside the `\begin{enumerate}`)

**Find** the `\item \textbf{Empirical characterization.}` paragraph that starts with "Across two models and 1,448 valid translation records..."

**Replace the entire item with:**

```latex
% src: quantitative_findings_*.json > metadata > file_counts > valid_after_exclusion (626+822+814=2262)
\item \textbf{Empirical characterization.} Across three models and 2,262 valid translation records, we report the first multi-suite, multi-direction evaluation of LLM-based parallel code translation under stochastic sampling with pass@$k$ analysis. Pass@1 ranges from 23.9\% (\qwenshort{}) to 62.7\% (\gptnew{} and \codexshort{}) on 142 unique no-augmentation (L0) tasks, with the code-specialized \codexshort{} statistically indistinguishable from the general-purpose \gptnew{}. Key findings include build-stage API adaptation as the main bottleneck, strong direction and file-boundary effects, broad stability under augmentation, and limited gains from repeated sampling.
```

---

## PART 6: experimental-setup.tex

**Location:** `sections/experimental-setup.tex`

### 6A. Models paragraph

**Find** the paragraph starting `\textbf{Models:} We evaluate two models:...`

**Replace the entire paragraph with:**

```latex
\textbf{Models:} We evaluate three models: \qwen{}, a 397B-parameter MoE open weights and open-source model accessed via Together AI; \gptnew{}, a general-purpose proprietary model accessed via \gptprovider{}; and \codex{}, a code-specialized model optimized via reinforcement learning on software engineering tasks~\cite{GPT53Codex2026}, also accessed via \gptprovider{}. All three expose provider-specific reasoning modes, configured at recommended settings (\texttt{enable\_thinking} for \qwenshort{}, \texttt{reasoning\_effort=medium} for \gptnew{} and \codexshort{}). Because these thinking modes differ in mechanism, observed performance differences reflect both base capability and reasoning-mode effects. Detailed model configurations, hardware specs, and cost accounting are provided in Appendix~\ref{sec:appendix-framework-extended}.
```

### 6B. Evaluation Phases paragraph

**Find:** `The canonical campaign (L0) evaluates all 142 unique pairs from unmodified source code, using $n=3$ independent samples per task (temperature 0.7 for \qwenshort{}; internally controlled for \gptnew{}).`

**Replace with:**

```latex
The canonical campaign (L0) evaluates all 142 unique pairs from unmodified source code for each of the three models (1,278 total L0 records), using $n=3$ independent samples per task (temperature 0.7 for \qwenshort{}; internally controlled for \gptnew{} and \codexshort{}).
```

---

## PART 7: results.tex (HEAVIEST CHANGES)

**Location:** `sections/results.tex`

### 7A. Table 1 caption

**Find** the `\caption{Overall pass rates...}` line.

**Replace with:**

```latex
\caption{Overall pass rates across three models and 2,262 valid translation records. \qwenshort{} covers 626 valid records (426 L0 + 200 ablation) after excluding 82 records involving 9 \knownfail{} specs. \gptnew{} covers 822 valid records (426 L0 + 396 ablation) and \codexshort{} covers 814 valid records (426 L0 + 388 ablation); \knownfail{} specs were pre-excluded from both GPT evaluation batches.}
```

### 7B. Table 1 data — add Codex row

**After** the GPT-5.4 data row (`\gptnew{} & 621 & 123 & ...`), **add this row before `\bottomrule`:**

```latex
% src: quantitative_findings_azure-gpt-5.3-codex.json > canonical > failure_taxonomy > status_counts
\codex{} & 604 & 139 & 44 & 27 & 0 & 814 & 74.2\% [71.1\%, 77.1\%] \\
```

### 7C. Section 5.1 Overall Performance prose

**After** the sentence `...while \gptnew{} passes 75.5\%.`, **add:**

```latex
% src: statistical_analysis.json > model_comparison > pairwise[0] (Bonferroni-corrected p)
\codexshort{}, a code-specialized model, passes 74.2\% of its valid records---statistically indistinguishable from \gptnew{} (Fisher's exact $p = 1.0$, OR\,=\,0.93 [0.74, 1.16], Cohen's $h = -0.031$). Code-specialized reinforcement learning training does not measurably improve parallel translation success at this task difficulty.
```

### 7D. Section 5.2 pass@k Analysis

**After** `...23.9\% pass@1 and 35.2\% pass@3 (detailed in Appendix~\ref{sec:appendix-c-extended}).`, **add:**

```latex
% src: paper_data_azure-gpt-5.3-codex.json > passk_campaign > aggregate_passk
\codexshort{} achieves pass@1\,=\,62.7\% and pass@3\,=\,68.3\%, matching \gptnew{}'s pass@1 exactly with a slightly narrower pass@1-to-pass@3 gap (5.6\,pp versus 7.0\,pp).
```

(Keep the existing "Additional stochastic samples provide diminishing returns." sentence after this.)

### 7E. Direction Table (Table 2) — add Codex column

**Replace the entire table** (from `\begin{tabular}` to `\end{tabular}`) with this 4-column version wrapped in `\resizebox`:

```latex
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lrrrc@{}}
\toprule
Direction & \qwenshort{} & \gptnew{} & \codexshort{} & $n$ \\
\midrule
% src: quantitative_findings_*.json > canonical > direction_pass_rates > standard
CUDA$\to$OMP & 40.3\% [29.7\%, 51.8\%] & 83.3\% [73.1\%, 90.2\%] & 76.4\% [65.4\%, 84.7\%] & 72 \\
OMP$\to$OpenCL & 33.3\% [22.0\%, 47.0\%] & 72.5\% [59.1\%, 82.9\%] & 82.3\% [69.8\%, 90.4\%] & 51 \\
OMP$\to$CUDA & 25.0\% [16.4\%, 36.1\%] & 55.6\% [44.1\%, 66.5\%] & 55.6\% [44.1\%, 66.5\%] & 72 \\
OpenCL$\to$OMP & 9.8\% [4.3\%, 21.0\%] & 41.2\% [28.8\%, 54.8\%] & 39.2\% [27.0\%, 52.9\%] & 51 \\
CUDA$\to$OpenCL & 7.0\% [2.8\%, 16.7\%] & 59.7\% [46.7\%, 71.4\%] & 57.9\% [45.0\%, 69.8\%] & 57 \\
OpenCL$\to$CUDA & 0.0\% [0.0\%, 6.3\%] & 19.3\% [11.1\%, 31.3\%] & 19.3\% [11.1\%, 31.3\%] & 57 \\
\midrule
% src: quantitative_findings_*.json > canonical > direction_pass_rates > standard (omp_target) + case_study
OMP-target$\to$OMP ($m{=}3$) & 100\% [70.1\%, 100\%] & 100\% [70.1\%, 100\%] & 100\% [70.1\%, 100\%] & 9 \\
OMP-target$\to$CUDA ($m{=}8$) & 66.7\% [46.7\%, 82.0\%] & 95.8\% [79.8\%, 99.3\%] & 100\% [86.2\%, 100\%] & 24 \\
OMP$\to$OMP-target ($m{=}3$) & 44.4\% [18.9\%, 73.3\%] & 100\% [70.1\%, 100\%] & 100\% [70.1\%, 100\%] & 9 \\
CUDA$\to$OMP-target ($m{=}8$) & 0.0\% [0.0\%, 13.8\%] & 95.8\% [79.8\%, 99.3\%] & 100\% [86.2\%, 100\%] & 24 \\
\bottomrule
\end{tabular}%
}
```

### 7F. Section 5.3 Direction Dependence prose

**After** the sentence ending `...leading to 0\% success for OpenCL-to-CUDA under \qwenshort{}.`, **add:**

```latex
\codexshort{}'s direction profile nearly mirrors \gptnew{} across all six standard directions (within 2--10\,pp), reinforcing that direction difficulty is a property of the task, not the model.
```

### 7G. Failure taxonomy figure caption

**Find** the `\caption{` for Figure 4 (failure taxonomy).

**Replace with:**

```latex
\caption{\qwenshort{} outcome taxonomy across 626 valid records. Build-stage failures are the largest non-pass category. \gptnew{} taxonomy (822 records) is in Appendix~\ref{sec:appendix-gpt-figures}; \codexshort{} taxonomy (814 records) is in Appendix~\ref{sec:appendix-codex-figures}.}
```

### 7H. Section 5.4 Failure Taxonomy prose

**After** the paragraph ending `...OpenCL JIT compilation errors occurring at runtime.`, **add:**

```latex
% src: quantitative_findings_azure-gpt-5.3-codex.json > canonical > failure_taxonomy > status_counts
\codexshort{}'s failure distribution is intermediate: \buildfail{} accounts for 17.1\% of records, between \qwenshort{}'s 39.1\% and \gptnew{}'s 15.0\%.
```

### 7I. Section 5.5 Augmentation Robustness

**Replace the entire subsection content** (after `\label{sec:augmentation-robustness}`) with:

```latex
To assess whether baseline success is driven primarily by surface-form memorization, we evaluated augmented source variants (L1--L4) on L0-conditional subsets (detailed in Appendix~\ref{sec:appendix-c-extended}).
% src: statistical_analysis.json > augmentation_curves > azure-gpt-5.3-codex; azure-gpt-5.4; together-qwen-3.5-397b-a17b
\codexshort{} shows the same plateau pattern as \gptnew{}: 86.6\%--88.7\% at L1--L4 ($\chi^2$ independence test, $p = 1.0$ after Bonferroni correction), in contrast to \qwenshort{}'s peak-then-decline (74.0\% at L1 to 56.0\% at L4, $p = 0.005$). This stability across both GPT models is compatible with robustness to surface-form perturbation, though survivorship bias (L0-conditional filtering) prevents ruling out deeper structural memorization entirely.
```

---

## PART 8: discussion.tex

**Location:** `sections/discussion.tex`

### 8A. Opening paragraph (entire first paragraph)

**Replace the entire first paragraph** (from `\parbench{} establishes...` to the end of the `% src:` comment) with:

```latex
% src: statistical_analysis.json > omnibus_chi2; cross_model_comparison_*.json
\parbench{} establishes that LLMs can perform non-trivial parallel code translation when evaluation isolates the kernel and preserves executable correctness. The benchmark surfaces three structural properties of this task: strong direction dependence (CUDA-to-OpenMP passes at 40--83\% while OpenCL-to-CUDA yields 0--19\%), build-stage API adaptation as the dominant failure mode, and preliminary robustness to surface-form augmentation on the tested subset. An omnibus chi-squared test across all 2,262 records confirms significant model differences ($\chi^2(2) = 287.27$, $p < 10^{-10}$, Cram\'{e}r's $V = 0.356$). However, pairwise analysis on the 142 balanced L0 tasks reveals two distinct tiers: \gptnew{} and \codexshort{} are statistically indistinguishable (Fisher's exact $p = 1.0$, OR\,=\,0.93 [0.74, 1.16], Cohen's $h = -0.031$; McNemar concordance: 94 both-pass, 40 both-fail, 5 \gptnew{}-only, 3 \codexshort{}-only), while both surpass \qwenshort{} by approximately 5$\times$ odds ratio (Cohen's $h \approx 0.8$). Because the two providers use unmatched sampling conditions (Section~\ref{sec:sampling-config}), the Qwen--GPT gap cannot be causally attributed to model capability alone; the within-provider \gptnew{}--\codexshort{} comparison controls for this confound and suggests that code-specialized training does not measurably improve parallel translation. % src: statistical_analysis.json > model_comparison > pairwise; cross_model_comparison_gpt54_vs_codex.json > mcnemar
```

### 8B. Second paragraph (deterministic outcomes)

**Replace the entire second paragraph** (from `The gap is concentrated...` to `...across five augmentation levels.`) with:

```latex
The gap is concentrated in deterministic outcomes: 53.5\% of \gptnew{} tasks pass all three samples versus 13.4\% for \qwenshort{}, and hard failures (0/3) account for 30.3\% versus 64.8\%, yielding a smaller pass@1-to-pass@3 gap (7.0\,pp versus 11.3\,pp). \codexshort{} mirrors \gptnew{}: 57.0\% always-pass, 31.7\% hard-fail, 5.6\,pp pass@1-to-pass@3 gap. All three models share the same dominant failure mode, incomplete API-surface adaptation at build time, but the GPT models reduce build failures from 50.0\% (\qwenshort{}) to 22.8\% (\gptnew{}) and 25.1\% (\codexshort{}) of L0 records. Direction-level results are consistent across all three models: CUDA-to-OpenMP is the most tractable standard direction (\gptnew{} 83.3\%, \codexshort{} 76.4\%, \qwenshort{} 40.3\%), while OpenCL-to-CUDA remains the hardest (\gptnew{} and \codexshort{} 19.3\%, \qwenshort{} 0\%). Augmentation robustness analysis on L0-conditional subsets shows stable pass rates for both GPT models (87--91\% for \gptnew{}, 86--89\% for \codexshort{} at L1--L4), while \qwenshort{} peaks at L1 (74\%) then declines to 56\% at L4.
```

### 8C. Limitations paragraph — replace last 2 sentences

**Find** the two sentences starting `The two models use different reasoning mechanisms...` through `...it reflects an unknown mixture of model strength and provider-side differences.`

**Replace with:**

```latex
The three models use different reasoning mechanisms and sampling configurations (Section~\ref{sec:sampling-config}). The Qwen--GPT gap is large (Cohen's $h = 0.80$) but cannot be fully attributed to model capability given unmatched sampling conditions. The within-provider \gptnew{}--\codexshort{} comparison controls for provider-side differences but both share the same Azure OpenAI infrastructure, limiting generalizability beyond this provider. \codexshort{}'s code specialization targets general software engineering tasks; the null result for parallel translation may not generalize to models specifically fine-tuned on HPC code.
```

### 8D. Future work — first sentence

**Find:** `\gptnew{} passes 62.7\% at L0`

**Replace with:** `Both GPT models achieve pass@1\,=\,62.7\%`

---

## PART 9: appendices_neurips.tex

### 9A. Sampling Configuration label (around line 121)

**Find:** `\paragraph{Sampling Configuration.}`

**Replace with:** `\paragraph{Sampling Configuration.}\label{sec:sampling-config}`

### 9B. L0 record total (around line 126)

**Find:** `852 total`

**Replace with:** `1,278 total`

### 9C. Ablation qualifying pairs (around line 127)

**Find:** `for \gptnew{}, 99~pairs qualify (70\%).`

**Replace with:** `for \gptnew{}, 99~pairs qualify (70\%); for \codexshort{}, 97~pairs qualify (68\%).`

### 9D. Model config table — add Codex row

**Find the table with `\label{tab:model-config}`.** After the GPT-5.4 row, **add:**

```latex
GPT-5.3-codex & Azure OpenAI & undisclosed & undisclosed & N/A$^\dagger$ \\
```

### 9E. Augmentation rates table — replace entirely

**Find the table with `\label{tab:augmentation-rates}`.** Replace the entire table (caption through `\end{table}`) with:

```latex
\begin{table}[htbp]
\centering
% src: statistical_analysis.json > augmentation_curves > *; augmentation_per_kernel_matrix_*.json
\caption{LLM pass rates across augmentation levels. L0 covers all 142 direction--kernel pairs ($n=426$ tasks). L1--L4 are evaluated only for pairs where $\geq$1 of 3 L0 samples passed (Qwen: 50 pairs, GPT-5.4: 99 pairs, Codex: 97 pairs).}
\label{tab:augmentation-rates}
\small
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}ccccccc@{}}
\toprule
Level & \makecell{Qwen 3.5\\(all dirs)} & \makecell{Qwen 3.5\\(C$\to$OMP)} & \makecell{GPT-5.4\\(all dirs)} & \makecell{GPT-5.4\\(C$\to$OMP)} & \makecell{Codex\\(all dirs)} & \makecell{Codex\\(C$\to$OMP)} \\
\midrule
L0 & 23.9\% ($n$=426) & 40.3\% ($n$=72) & 62.7\% ($n$=426) & 83.3\% ($n$=72) & 62.7\% ($n$=426) & 76.4\% ($n$=72) \\
L1 & 74.0\% ($n$=50) & 75.0\% ($n$=12) & 88.9\% ($n$=99) & 90.9\% ($n$=22) & 86.6\% ($n$=97) & 85.0\% ($n$=20) \\
L2 & 64.0\% ($n$=50) & 83.3\% ($n$=12) & 90.9\% ($n$=99) & 95.5\% ($n$=22) & 88.7\% ($n$=97) & 85.0\% ($n$=20) \\
L3 & 62.0\% ($n$=50) & 75.0\% ($n$=12) & 86.9\% ($n$=99) & 81.8\% ($n$=22) & 86.6\% ($n$=97) & 85.0\% ($n$=20) \\
L4 & 56.0\% ($n$=50) & 83.3\% ($n$=12) & 90.9\% ($n$=99) & 90.9\% ($n$=22) & 85.6\% ($n$=97) & 90.0\% ($n$=20) \\
\bottomrule
\end{tabular}%
}
\end{table}
```

### 9F. pass@k table — add Codex row

**Find the table with `\label{tab:pass-at-k}`.** After the GPT-5.4 row, **add:**

```latex
% src: paper_data_azure-gpt-5.3-codex.json > passk_campaign > aggregate_passk + task_classification
GPT-5.3-codex & 142 & 62.7\% & 68.3\% & 45/142 (31.7\%) & 16/142 (11.3\%) & 81/142 (57.0\%) \\
```

### 9G. NEW SECTION — Codex Per-Model Figures

**After the GPT-5.4 Per-Model Figures section** (after the `\label{fig:f6-gpt}` figure's `\end{figure}`), **add this entire new section BEFORE `\section{Evaluation Cost Summary}`:**

```latex
\section{GPT-5.3-codex Per-Model Figures}
\label{sec:appendix-codex-figures}

The following figures present GPT-5.3-codex evaluation results using the same visualization format as the main-body counterparts.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f3_kernel_model_heatmap_codex.pdf}
\caption{Per-kernel pass rates across all translation directions (GPT-5.3-codex).}
\label{fig:f3-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f4_failure_taxonomy_codex.pdf}
\caption{Failure taxonomy distribution (GPT-5.3-codex). Compare with Figure~\ref{fig:failure-taxonomy} in main body (Qwen~3.5 397B).}
\label{fig:f4-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f5_pass_at_k_by_direction_codex.pdf}
\caption{Pass@$k$ rates by translation direction (GPT-5.3-codex).}
\label{fig:f5-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f6_cross_suite_comparison_codex.pdf}
\caption{Cross-suite pass rate comparison (GPT-5.3-codex).}
\label{fig:f6-codex}
\end{figure}
```

### 9H. NEW TABLE — Codex Cost Summary

**After the GPT-5.4 cost table** (`\label{tab:eval-cost-gpt}`), **add:**

```latex
% src: raw result files in results/evaluation/azure-gpt-5.3-codex/ (814 files, verified 2026-05-01)
\begin{table}[h]
\centering
\caption{GPT-5.3-codex evaluation campaign cost summary (April 30 -- May 1, 2026).}
\label{tab:eval-cost-codex}
\begin{tabular}{lr}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
Total tokens & 13.2M (9.2M in, 4.0M out) \\
Avg.\ tokens per task & 16{,}204 (11{,}347 in, 4{,}857 out) \\
Total LLM wall time & 11.9 hours \\
Campaign duration & 2 days (814 tasks) \\
\bottomrule
\end{tabular}
\end{table}
```

### 9I. NeurIPS Checklist — Claims justification

**Find:** `(Qwen 23.9\%, GPT-5.4 62.7\%)`

**Replace with:** `(Qwen 23.9\%, GPT-5.4 62.7\%, Codex 62.7\%)`

### 9J. NeurIPS Checklist — Limitations justification

**Find:** `two-model scope`

**Replace with:** `three-model scope`

### 9K. NeurIPS Checklist — Model disclosure

**Find:** `LLMs (Qwen~3.5 397B-A17B and GPT-5.4)`

**Replace with:** `LLMs (Qwen~3.5 397B-A17B, GPT-5.4, and GPT-5.3-codex)`

---

## PART 10: Drawio Architecture Diagram (MANUAL)

**File:** `figures/parbench_architecture.drawio` (open in draw.io or diagrams.net)

**Find** the text box that says:
- `× 2 models` → change to `× 3 models`
- `1448 records` → change to `2262 records`

---

## Verification Checklist (after all changes applied)

1. Compile the document — no `??` references should appear
2. Search for `two models` — should return 0 results in all .tex files
3. Search for `1,448` or `1448` — should return 0 results in all .tex files
4. Count codex references — should be 49+ across all files
5. Verify Table 1 has 3 data rows (Qwen, GPT-5.4, Codex)
6. Verify Table 2 has 4 data columns (Direction, Qwen, GPT-5.4, Codex, n)
7. Verify augmentation table has 6 data columns (3 models × 2 directions)
8. Verify pass@k table has 3 data rows
9. Verify model-config table has 3 data rows
10. Verify appendix has Codex figures section with 4 figures
11. Verify F7 augmentation robustness figure shows 3 lines
