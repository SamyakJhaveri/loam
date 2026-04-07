# Phase 17: Paper Integration -- Dual-Model Results & Differentiation - Research

**Researched:** 2026-04-07
**Domain:** LaTeX paper editing, data-driven SC26 paper completion
**Confidence:** HIGH

## Summary

Phase 17 is a pure paper-editing phase: no code, no analysis scripts, no figure generation. All inputs are already on disk (verified). The task is to update `docs/paper/latex/paper.tex` and `docs/paper/latex/appendices.tex` with GPT-4.1 mini data by filling placeholder markers, writing a new cross-model comparison section, adding augmentation degradation evidence, emphasizing prompt anonymization, and wiring per-model figures.

The paper currently has 18 `\pending{...}` markers in content lines (17 to fill, 1 to keep per D-07) and 24 `\tbd` table cells (9 GPT row + 9 Aggregate row in tab:overall-pass, plus 6 GPT column cells in tab:direction-rates). All data sources are JSON files in `results/analysis/` that have been verified present. Figures F3-F6 already exist in per-model variants (`_qwen.pdf` and `_gpt.pdf`); F3/F4 `_qwen` references are already wired in paper.tex; F5/F6 are not yet referenced anywhere.

**Primary recommendation:** Execute in strict wave order (Wave 1: mechanical fills, Wave 2: new prose sections, Wave 3: figure wiring) with LaTeX syntax validation after each sub-task. Since `pdflatex` is not installed on this machine, syntax validation must use a lightweight check (e.g., grep for unmatched braces, missing `\\end`, or use a remote compilation service).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01-gate:** Gate file is `results/analysis/error_taxonomy.json` (combined dual-model), NOT `error_taxonomy_gpt41mini.json`. GPT failure data accessed via `per_model["azure-gpt-4.1-mini"]`.
- **D-01-gate-phase16:** Phase 16-04 must be fully complete (SUMMARY written, per-model figures committed) before Phase 17 starts.
- **D-02:** 7-direction cross-model comparison. `omp_target-to-cuda` GPT data absent. Check once at Phase 17 start; do not check again mid-execution.
- **D-02-footnote:** All cross-model direction tables must include footnote: "Cross-model comparison covers 7 of 8 evaluated directions; `omp_target-to-cuda` GPT-4.1 mini results were unavailable at submission."
- **D-03:** Actual `\pending{...}` count: 18 in content. Line 631 stays unfilled (D-07). 17 to fill.
- **D-04:** Actual `\tbd` cell count: 24 across two tables. tab:overall-pass: 9 GPT row + 9 Aggregate row = 18. tab:direction-rates: 6 GPT column cells.
- **D-04-aggregate:** Aggregate row is sum of counts (Qwen + GPT), NOT average of pass rates.
- **D-05:** Add ALL content, no cuts. Samyak and Le manually compress to <=10 pages.
- **D-05-appendix-main:** Per-model GPT figures in appendix do NOT count toward 10-page limit.
- **D-06:** Strict execution order: Wave 1 (17A + 17A-tbd), Wave 2 (17B, 17C, 17D sequential), Wave 3 (17E).
- **D-07:** Line 631 `\pending{GPU model...}` stays as-is with TODO comment. Only 17 of 18 markers filled.
- **D-08:** Section 6.9 content requirements: chi-squared p-value, Wilson CIs, per-direction side-by-side, failure taxonomy comparison, per-kernel agreement matrix, Cohen's h.
- **D-08-framing:** Benchmark paper framing -- two models demonstrate ParBench utility, NOT model ranking. Provider diversity framing.
- **D-09:** F3/F4/F5/F6 split into _qwen and _gpt variants. Qwen in main body, GPT in appendix. All captions include model name.
- **D-09-line-numbers:** Line numbers approximate -- executor greps for actual position before editing.

### Claude's Discretion
- Exact prose wording in Section 6.9 and 17C/17D
- Where to insert F5/F6 Qwen figures in paper.tex
- How to present four-way kernel agreement matrix (table vs prose)

### Deferred Ideas (OUT OF SCOPE)
- omp_target-to-cuda cross-model comparison (blocked on data)
- Per-kernel agreement matrix as heatmap figure
- Page budget compression (Samyak + Le manual edit post-Phase 17)
- F5/F6 may be removed from main body during compression
</user_constraints>

## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| LaTeX (IEEE format) | IEEE double-column | Paper typesetting | SC26 submission format [VERIFIED: paper.tex preamble] |
| paper.tex | 1122 lines | Primary edit target | [VERIFIED: wc -l] |
| appendices.tex | 1401 lines | Appendix edit target for GPT figures | [VERIFIED: wc -l] |

### Data Sources (all verified present on disk)
| File | Purpose | Key Data |
|------|---------|----------|
| `results/analysis/paper_data_gpt41mini.json` | GPT numbers for pending/tbd fills | Overall: 161/551 = 29.2% [25.6%, 33.2%] [VERIFIED: file read] |
| `results/analysis/cross_model_comparison.json` | Statistical comparison for Section 6.9 | chi2=10.97, p=0.000926, Cohen's h=0.1926 [VERIFIED: file read] |
| `results/analysis/error_taxonomy.json` | Failure taxonomy per model | GPT BUILD_FAIL: 514 total (missing_target_api=196, missing_header=168) [VERIFIED: file read] |
| `results/analysis/coverage_gaps.md` | Direction coverage, footnote text | 7 of 8 directions, footnote text provided [VERIFIED: file read] |

### Figure Files (all verified present)
| File | Location | Purpose |
|------|----------|---------|
| `f3_kernel_model_heatmap_qwen.pdf` | Main body (already wired, line 831) | Per-kernel heatmap Qwen |
| `f3_kernel_model_heatmap_gpt.pdf` | Appendix (to add in 17E) | Per-kernel heatmap GPT |
| `f4_failure_taxonomy_qwen.pdf` | Main body (already wired, line 712) | Failure taxonomy Qwen |
| `f4_failure_taxonomy_gpt.pdf` | Appendix (to add in 17E) | Failure taxonomy GPT |
| `f5_pass_at_k_by_direction_qwen.pdf` | Main body (to add in 17E) | Pass@k Qwen |
| `f5_pass_at_k_by_direction_gpt.pdf` | Appendix (to add in 17E) | Pass@k GPT |
| `f6_cross_suite_comparison_qwen.pdf` | Main body (to add in 17E) | Cross-suite Qwen |
| `f6_cross_suite_comparison_gpt.pdf` | Appendix (to add in 17E) | Cross-suite GPT |
| `f7_augmentation_robustness.pdf` | Main body (no change) | Unified dual-model |

## Architecture Patterns

### Paper Structure (Section Numbering for Insertion Points)
```
Section 6: Results
  6.1: Overall Pass Rates (line 674) -- tab:overall-pass here
  6.2: Failure Taxonomy (line 704)
  6.3: Per-Kernel Analysis (line 794) -- F3 heatmap here
  6.4: Self-Repair Effectiveness (line 871)
  6.5: Augmentation Robustness (line 885) -- F7 here
  6.6: Cross-Direction Analysis (line 923) -- tab:direction-rates here
  6.7: pass@k Analysis (line 971)
  6.8: Statistical Summary (line 988)
  -- INSERT Section 6.9 here (before line 998) --
Section 7: Discussion (line 1001)
Section 8: Conclusion (line 1080)
```

### Pattern 1: Source Comment Convention
**What:** Every data fill in paper.tex has an inline `% src:` comment tracing to the JSON source.
**When to use:** Every GPT number inserted.
**Example:**
```latex
GPT-4.1 mini & 161 & 316 & 43 & 31 & 0 & 0 & 551 & 29.2\% & [25.6\%, 33.2\%] \\ % src: paper_data_gpt41mini.json > primary_campaign > overall: 161/551=0.2922, CI [0.2558,0.3315]
```

### Pattern 2: Pending Marker Replacement
**What:** Replace `\pending{description}` with actual prose containing verified numbers.
**When to use:** All 17 fills.
**Example:**
```latex
% BEFORE:
\pending{Cross-model comparison awaiting GPT-4.1~mini data.}
% AFTER:
GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks ($\chi^2 = 10.97$, $p < 0.001$, Cohen's $h = 0.19$). % src: cross_model_comparison.json > overall
```

### Pattern 3: Aggregate Row Computation
**What:** Aggregate row = sum of counts from Qwen + GPT, with rate recomputed from summed totals.
**Critical rule:** NOT average of model rates.
**Example:**
```
Qwen:      272 PASS, 241 BF, 144 RF, 51 VF, 1 EF, 1 ERR = 710 total
GPT:       161 PASS, 316 BF,  43 RF, 31 VF, 0 EF, 0 ERR = 551 total
Aggregate: 433 PASS, 557 BF, 187 RF, 82 VF, 1 EF, 1 ERR = 1261 total
Rate: 433/1261 = 34.3%
```
[VERIFIED: computed from paper_data.json + paper_data_gpt41mini.json]

### Anti-Patterns to Avoid
- **Placeholder statistics:** Never write "statistically significant" without the actual p-value from cross_model_comparison.json. D-08 requires actual chi-squared p-value.
- **Average instead of sum:** Aggregate row must be sum of counts. Average of 38.3% and 29.2% = 33.75% is WRONG; correct is 433/1261 = 34.3%.
- **Model ranking framing:** Never say "Qwen outperforms GPT" -- say "Qwen achieves X% vs GPT's Y%, demonstrating ParBench's ability to differentiate model capabilities."
- **Approximate line numbers:** Always grep for actual position before editing. Line numbers drift with edits.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wilson CI computation | Manual formula | Values from paper_data_gpt41mini.json | Pre-computed with validated scipy implementation |
| Chi-squared test | Manual calculation | Values from cross_model_comparison.json | Already computed: chi2=10.97, p=0.000926 |
| Cohen's h | Manual formula | Values from cross_model_comparison.json | Overall h=0.1926, per-direction values available |
| Aggregate totals | Mental math | Script to sum Qwen + GPT JSON values | Avoids arithmetic errors in 9-column table |
| Per-kernel agreement | Manual counting | cross_model_comparison.json > per_kernel_matrix | Pre-computed: 13/5/11/2 counts with kernel names |

## Common Pitfalls

### Pitfall 1: Miscount of Pending Markers
**What goes wrong:** PLAN.md says 19, CONTEXT says 18. The actual count is 18 in content lines (2 additional `\pending` on comment-only lines 71 and 1078 do not need filling).
**Why it happens:** Different counting methodologies (grep vs manual).
**How to avoid:** The executor must grep before starting and count only non-comment, non-definition lines. Expected: 18 content-line matches. Fill 17 (skip line 631).
**Warning signs:** Count after filling should show exactly 1 remaining (line 631) plus the 2 comment-line occurrences.

### Pitfall 2: TBD Count Discrepancy
**What goes wrong:** PLAN.md says 18 tbd cells, CONTEXT.md says 24. The actual count is 24.
**Why it happens:** PLAN.md was written before tab:overall-pass structure was finalized (had fewer columns).
**How to avoid:** tab:overall-pass has 9 columns per row (PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTR_FAIL, ERROR, Total, Rate, CI). 9 GPT + 9 Aggregate = 18. Plus 6 direction-rates cells = 24 total.
**Warning signs:** If the executor fills only 18 cells, the direction table GPT column is left unfilled.

### Pitfall 3: LaTeX Compilation Not Available
**What goes wrong:** `pdflatex` is not installed on this machine. LaTeX compile checkpoints cannot be performed.
**Why it happens:** Linux GPU machine configured for CUDA/HPC, not document preparation.
**How to avoid:** Use lightweight syntax validation: (1) check matched `\begin{}`/`\end{}` pairs, (2) grep for common LaTeX errors (unescaped `%`, `&`, `_` in prose), (3) verify all `\includegraphics` paths point to existing files.
**Warning signs:** Paper may compile on Samyak's macOS machine but not on the Linux box -- this is expected and acceptable.

### Pitfall 4: Section 6.9 Insertion Point
**What goes wrong:** Inserting Section 6.9 in the wrong location breaks section numbering.
**Why it happens:** Section 6.8 (Statistical Summary) ends around line 997, and Section 7 starts at line 1001.
**How to avoid:** Insert between the end of Section 6.8 content (after line 996) and before the `%% S7 DISCUSSION` comment (line 998). Grep for `\section{Discussion}` to find the exact boundary.
**Warning signs:** If Section 6.9 appears inside the Discussion section or before Statistical Summary.

### Pitfall 5: GPT Augmentation Data Absence
**What goes wrong:** Several `\pending` markers mention "cross-model augmentation comparison" but GPT paper_data has no augmentation section.
**Why it happens:** GPT evaluation ran primary + pass@k campaigns only, no separate augmentation sweep.
**How to avoid:** For augmentation-related pending markers (lines 917, 1033), the fill text must note that GPT augmentation results cover only the primary campaign levels (L0-L4 are implicit in the direction totals) -- the dedicated augmentation analysis (Cochran-Armitage) was only performed for Qwen. The cross-model comparison can note BUILD_FAIL rate differences between models as circumstantial evidence.
**Warning signs:** If the executor fabricates GPT-specific Cochran-Armitage results that don't exist.

### Pitfall 6: omp_target-to-cuda Missing Direction
**What goes wrong:** tab:direction-rates already has omp_target-to-cuda row with `--` for all columns. The GPT column should also show `--` (not `\tbd`), which it already does.
**Why it happens:** Per D-02, this direction's GPT data hasn't arrived. The row already uses `--`.
**How to avoid:** Do NOT add a `\tbd` or number to the omp_target-to-cuda GPT column. It stays as `--`. Only the 6 standard directions (cuda-to-omp, omp-to-cuda, opencl-to-omp, omp-to-opencl, cuda-to-opencl, opencl-to-cuda) get GPT fills.

### Pitfall 7: F3/F4 Already Updated to _qwen
**What goes wrong:** Executor tries to update F3/F4 includegraphics to _qwen but they're already updated.
**Why it happens:** Phase 16-04 already changed these references.
**How to avoid:** F3 (line 831) already shows `f3_kernel_model_heatmap_qwen.pdf`. F4 (line 712) already shows `f4_failure_taxonomy_qwen.pdf`. 17E only needs to: (1) update captions with "(Qwen 3.5 397B)", (2) add F5/F6 Qwen figures in main body, (3) add all four GPT variants in appendices.tex.
**Warning signs:** Duplicate `_qwen_qwen.pdf` or missing `_qwen.pdf` in path.

## Verified Data for All Fills

### tab:overall-pass GPT Row (9 cells)
```
PASS=161, BUILD_FAIL=316, RUN_FAIL=43, VERIFY_FAIL=31, EXTR_FAIL=0, ERROR=0, Total=551, Rate=29.2%, CI=[25.6%, 33.2%]
```
[VERIFIED: paper_data_gpt41mini.json > primary_campaign > overall]

### tab:overall-pass Aggregate Row (9 cells)
```
PASS=433, BUILD_FAIL=557, RUN_FAIL=187, VERIFY_FAIL=82, EXTR_FAIL=1, ERROR=1, Total=1261, Rate=34.3%, CI=compute_wilson(433,1261)
```
[VERIFIED: sum of paper_data.json + paper_data_gpt41mini.json overall counts]

Note: Wilson CI for aggregate needs computation. 433/1261 = 0.3434.

### tab:direction-rates GPT Column (6 cells)
| Direction | GPT Rate | GPT Counts | GPT CI |
|-----------|----------|------------|--------|
| cuda-to-omp | 40.0% | 48/120 | [31.7%, 48.9%] |
| omp-to-cuda | 17.9% | 15/84 | [11.1%, 27.4%] |
| opencl-to-omp | 41.1% | 37/90 | [31.5%, 51.4%] |
| omp-to-opencl | 33.3% | 30/90 | [24.5%, 43.6%] |
| cuda-to-opencl | 30.0% | 30/100 | [21.9%, 39.6%] |
| opencl-to-cuda | 3.7% | 1/27 | [0.7%, 18.3%] |
[VERIFIED: paper_data_gpt41mini.json > primary_campaign > by_direction]

### Section 6.9 Statistical Data
| Metric | Value | Source |
|--------|-------|--------|
| Chi-squared | 10.97 | cross_model_comparison.json > overall > chi_squared > chi2 |
| p-value | 0.000926 | cross_model_comparison.json > overall > chi_squared > p_value |
| DOF | 1 | cross_model_comparison.json > overall > chi_squared > dof |
| Cohen's h (overall) | 0.1926 ("negligible") | cross_model_comparison.json > overall > cohens_h |
| Qwen rate | 38.3% (272/710) | cross_model_comparison.json > overall > qwen |
| GPT rate | 29.2% (161/551) | cross_model_comparison.json > overall > gpt |
[VERIFIED: cross_model_comparison.json read directly]

### Per-Direction Cohen's h
| Direction | h | Effect Size |
|-----------|---|-------------|
| cuda-to-omp | 0.4887 | small |
| cuda-to-omp_target | 0.8632 | large |
| cuda-to-opencl | -0.2320 | small (GPT better) |
| omp-to-cuda | 0.7482 | medium |
| omp-to-opencl | -0.1206 | negligible |
| opencl-to-cuda | 0.1078 | negligible |
| opencl-to-omp | -0.0453 | negligible |
[VERIFIED: cross_model_comparison.json > per_direction]

Notable: GPT outperforms Qwen on cuda-to-opencl (30% vs 20%) and omp-to-opencl (33.3% vs 27.8%). Qwen dominates omp-to-cuda (52.5% vs 17.9%) and cuda-to-omp (64.2% vs 40.0%).

### Per-Kernel Agreement Matrix
| Category | Count | Kernels |
|----------|-------|---------|
| Both pass | 13 | backprop, bfs, cfd, hotspot, hotspot3d, lavamd, lud, nn, nw, particlefilter, pathfinder, srad, streamcluster |
| Both fail | 5 | convolution1d, heartwall, myocyte, rsbench, xsbench |
| Qwen only pass | 11 | bptree, floydwarshall, heat2d, iso2dfd, jacobi, md, mixbench, nqueen, page-rank, scan, stencil1d |
| GPT only pass | 2 | dwt2d, gaussian |
[VERIFIED: cross_model_comparison.json > per_kernel_matrix]

### GPT Error Taxonomy (for Section 6.9 failure comparison)
| Category | Count |
|----------|-------|
| missing_target_api | 196 |
| missing_header | 168 |
| other_build | 62 |
| linker_error | 51 |
| undeclared_identifier | 29 |
| Total build_fail subcats | 507+ |
| wrong_exit_code | 57 |
| segfault | 17 |
| abort | 15 |
| wrong_numerical_output | 32 |
[VERIFIED: error_taxonomy.json > per_model > azure-gpt-4.1-mini]

GPT BUILD_FAIL rate: 316/551 = 57.3% of tasks (vs Qwen 241/710 = 33.9%).
GPT BUILD_FAIL as % of failures: 316/390 = 81.0% (vs Qwen 241/438 = 55.0%).

### Anonymization Measures (for 17D)
Verified against `scripts/evaluation/llm_evaluate.py` line 570+ (`build_translation_prompt()`):
1. **Kernel name & description:** Completely omitted from prompt (system_msg has no kernel name, line 629-636) [VERIFIED: code read]
2. **Source code comments:** `_strip_comments()` removes all comments [VERIFIED: referenced in code]
3. **Source filenames:** Genericized to "Source File 1", "Source File 2" etc. [VERIFIED: code at line 583]
4. **Target filenames:** `translated_0.ext`, `translated_1.ext` via anon_map (lines 604-610) [VERIFIED: code read]
5. **Build commands:** `_anonymize_build_cmd()` replaces kernel name in make targets (lines 556-567) [VERIFIED: code read]
6. **Header/support files:** Genericized to "Header File 1", "Code File 1" etc. (line 583) [VERIFIED: code read]
[VERIFIED: llm_evaluate.py lines 570-640 read directly]

## Code Examples

### Aggregate Row Computation (for executor reference)
```python
# Compute aggregate row values
import json

qwen = json.load(open('results/analysis/paper_data.json'))
gpt = json.load(open('results/analysis/paper_data_gpt41mini.json'))

q = qwen['primary_campaign']['overall']
g = gpt['primary_campaign']['overall']

qbs = q['by_status']
gbs = g['by_status']

agg = {
    'PASS': qbs['PASS'] + gbs['PASS'],           # 272 + 161 = 433
    'BUILD_FAIL': qbs['BUILD_FAIL'] + gbs['BUILD_FAIL'],  # 241 + 316 = 557
    'RUN_FAIL': qbs['RUN_FAIL'] + gbs['RUN_FAIL'],        # 144 + 43 = 187
    'VERIFY_FAIL': qbs['VERIFY_FAIL'] + gbs['VERIFY_FAIL'], # 51 + 31 = 82
    'EXTR_FAIL': qbs.get('EXTRACTION_FAIL', 0) + gbs.get('EXTRACTION_FAIL', 0),  # 1 + 0 = 1
    'ERROR': qbs.get('ERROR', 0) + gbs.get('ERROR', 0),   # 1 + 0 = 1
}
total = q['total'] + g['total']  # 710 + 551 = 1261
rate = agg['PASS'] / total       # 433/1261 = 0.3434

# Wilson CI (scipy)
from scipy.stats import proportion_confint
ci = proportion_confint(agg['PASS'], total, alpha=0.05, method='wilson')
# Expected: approximately [31.7%, 37.1%]
```

### Section 6.9 Template Structure
```latex
\subsection{Cross-Model Comparison}
\label{sec:cross-model}

% src: cross_model_comparison.json > overall
ParBench evaluates two models from distinct providers---Qwen~3.5 397B-A17B
(Alibaba, via Together~AI) and GPT-4.1~mini (OpenAI, via Azure)---to
demonstrate the framework's utility for cross-provider capability comparison.\footnote{Cross-model
comparison covers 7 of 8 evaluated directions; \texttt{omp\_target-to-cuda}
GPT-4.1~mini results were unavailable at submission.}

\textbf{Overall comparison.} ...chi-squared...Wilson CIs...

\textbf{Per-direction analysis.} ...table or prose with 7 directions...

\textbf{Failure taxonomy comparison.} ...BUILD_FAIL dominance...

\textbf{Per-kernel agreement.} ...13 both-pass, 5 both-fail, 11 Qwen-only, 2 GPT-only...

\textbf{Effect sizes.} ...Cohen's h overall and per-direction...
```

### LaTeX Syntax Validation (without pdflatex)
```bash
# Check matched environments
grep -c '\\begin{' docs/paper/latex/paper.tex
grep -c '\\end{' docs/paper/latex/paper.tex
# Should be equal

# Check figure file existence
for f in $(grep -oP 'includegraphics.*?\{(.*?)\}' docs/paper/latex/paper.tex | grep -oP '\{.*?\}' | tr -d '{}'); do
    ls "docs/paper/figures/$f" 2>/dev/null || echo "MISSING: $f"
done

# Check no remaining \tbd (except definition)
grep -n 'tbd' docs/paper/latex/paper.tex | grep -v 'newcommand'

# Check remaining \pending count (should be 1 at line 631 + 2 comments)
grep -n 'pending{' docs/paper/latex/paper.tex | grep -v 'newcommand'
```

## State of the Art

| Aspect | Current State | Impact |
|--------|--------------|--------|
| F3/F4 references | Already updated to `_qwen.pdf` by Phase 16-04 | 17E only needs caption updates + F5/F6 addition |
| F5/F6 references | Not in paper.tex at all | 17E must add new `\begin{figure}` environments |
| Section 6.9 | Does not exist | 17B must create entire subsection |
| tab:overall-pass GPT row | All 9 cells are `\tbd` | 17A-tbd fills these |
| tab:direction-rates GPT column | All 6 cells are `\tbd` | 17A-tbd fills these |
| Threats to Validity (line 1057) | Says "Single-model evaluation" | Must be updated to dual-model |
| Line 577 | "GPT-4.1~mini evaluation is pending" | Must be removed or updated |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Wilson CI for aggregate (433/1261) is approximately [31.7%, 37.1%] | Verified Data | LOW -- can be computed exactly by executor with scipy |
| A2 | F5 figure should go near Section 6.7 (pass@k Analysis, ~line 987) | Architecture Patterns | LOW -- executor decides per Claude's Discretion |
| A3 | F6 figure should go near Section 4.4 (Evaluation Corpus, ~line 496) or Section 6.3 | Architecture Patterns | LOW -- executor decides per Claude's Discretion |
| A4 | Line 577 ("GPT-4.1~mini evaluation is pending and marked with \tbd{} throughout") should be updated/removed | State of the Art | MEDIUM -- if left unchanged, contradicts filled data |

## Open Questions

1. **Wilson CI for Aggregate Row**
   - What we know: 433/1261 = 34.3%. Need Wilson CI.
   - What's unclear: Exact CI bounds (requires scipy computation).
   - Recommendation: Executor runs `python3 -c "from scipy.stats import proportion_confint; print(proportion_confint(433, 1261, method='wilson'))"` to get exact bounds.

2. **GPT Evaluation Cost (line 663)**
   - What we know: Line 663 has `\pending{GPT-4.1~mini evaluation costs via Azure.}`
   - What's unclear: Whether this cost data is available anywhere on disk.
   - Recommendation: Check for Azure cost data in results/. If not available, leave this pending or add a TODO comment like line 631.

3. **GPT Augmentation Data Absence**
   - What we know: paper_data_gpt41mini.json has no `augmentation` section. Primary campaign covers L0-L4 implicitly in the direction totals.
   - What's unclear: How to handle pending markers about "cross-model augmentation comparison" (lines 917, 1033).
   - Recommendation: Note that the primary campaign includes augmented levels (L0-L4) for both models, so per-direction pass rates inherently reflect augmentation response. But Cochran-Armitage trend test was only performed for Qwen. State this limitation explicitly.

4. **Line 577 Stale Text**
   - What we know: "GPT-4.1~mini evaluation is pending and marked with \tbd{} throughout" will be false after fills.
   - What's unclear: Whether to remove it entirely or update it.
   - Recommendation: Remove or replace with "Two models are evaluated: Qwen~3.5 397B-A17B and GPT-4.1~mini."

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pdflatex | LaTeX compilation checks | NO | -- | Syntax-level validation only (matched environments, file existence, grep checks) |
| python3 | Data extraction, Wilson CI computation | YES | 3.x | -- |
| scipy | Wilson CI for aggregate row | UNKNOWN | -- | Executor checks via `python3 -c "import scipy"` |
| grep/sed | Text editing and validation | YES | -- | -- |

**Missing dependencies with fallback:**
- pdflatex: Not installed. Use lightweight LaTeX syntax validation (grep-based checks for matched environments, existing figure files, unescaped special characters).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual verification + grep-based checks |
| Config file | None -- paper editing, not code |
| Quick run command | `grep -c 'pending{' docs/paper/latex/paper.tex` (expect 3 after: 1 content line 631 + 2 comments) |
| Full suite command | See validation script below |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| 17A | All pending markers filled (except 631) | grep | `grep -n 'pending{' docs/paper/latex/paper.tex \| grep -v newcommand \| grep -v '^\s*%'` -- expect 1 match (line 631) | N/A |
| 17A-tbd | All tbd cells filled | grep | `grep -c 'tbd' docs/paper/latex/paper.tex` -- expect 1 (definition only) | N/A |
| 17B | Section 6.9 exists with chi-squared | grep | `grep 'Cross-Model Comparison' docs/paper/latex/paper.tex` | N/A |
| 17C | Augmentation examples with lavamd L4=PASS | grep | `grep 'lavamd' docs/paper/latex/paper.tex` | N/A |
| 17D | Anonymization subsection exists | grep | `grep 'anonymi' docs/paper/latex/paper.tex` | N/A |
| 17E | F5/F6 qwen in main body, F3-F6 gpt in appendix | grep | `grep 'f5_.*qwen\|f6_.*qwen' docs/paper/latex/paper.tex` and `grep 'gpt.pdf' docs/paper/latex/appendices.tex` | N/A |

### Full Validation Script
```bash
#!/bin/bash
# Post-Phase-17 validation
echo "=== Pending markers ==="
PENDING=$(grep -c 'pending{' docs/paper/latex/paper.tex)
echo "Total pending occurrences: $PENDING (expect ~3: 1 content + 2 comments)"

echo "=== TBD markers ==="
TBD=$(grep 'tbd' docs/paper/latex/paper.tex | grep -v newcommand | grep -cv '^\s*%')
echo "Content tbd occurrences: $TBD (expect 0)"

echo "=== Section 6.9 ==="
grep -c 'Cross-Model\|cross-model' docs/paper/latex/paper.tex

echo "=== Figure references ==="
for f in f3 f4 f5 f6; do
    grep "${f}_.*qwen" docs/paper/latex/paper.tex && echo "$f qwen: OK" || echo "$f qwen: MISSING"
    grep "${f}_.*gpt" docs/paper/latex/appendices.tex && echo "$f gpt: OK" || echo "$f gpt: MISSING"
done

echo "=== Environment checks ==="
grep -c '\\begin{' docs/paper/latex/paper.tex
grep -c '\\end{' docs/paper/latex/paper.tex
```

### Wave 0 Gaps
None -- no test infrastructure needed for paper editing. Validation is grep-based.

## Security Domain

Not applicable -- this phase is pure paper editing (LaTeX text changes). No code execution, no API calls, no data processing, no user input handling. `security_enforcement` does not apply to document editing.

## Sources

### Primary (HIGH confidence)
- `results/analysis/paper_data_gpt41mini.json` -- all GPT numbers [read directly]
- `results/analysis/cross_model_comparison.json` -- chi-squared, Cohen's h, per-kernel matrix [read directly]
- `results/analysis/error_taxonomy.json` -- GPT failure taxonomy [read directly]
- `results/analysis/coverage_gaps.md` -- direction coverage, footnote text [read directly]
- `docs/paper/latex/paper.tex` -- current paper state, line numbers, marker counts [read directly]
- `docs/paper/latex/appendices.tex` -- appendix structure [read directly]
- `scripts/evaluation/llm_evaluate.py` -- anonymization code verification [read directly]
- `docs/paper/figures/` -- all 8 per-model PDFs + F7 confirmed present [ls verified]

### Secondary (MEDIUM confidence)
- `.planning/phases/17-paper-integration/17-CONTEXT.md` -- locked decisions D-01 through D-09 [read directly]
- `.planning/phases/17-paper-integration/PLAN.md` -- existing hand-written plan [read directly]

## Metadata

**Confidence breakdown:**
- Data availability: HIGH -- all JSON files read, all numbers extracted and cross-verified
- Marker counts: HIGH -- grep-verified against actual paper.tex (18 content pending, 24 tbd)
- Figure state: HIGH -- ls-verified all 9 PDFs present, F3/F4 references already updated
- Insertion points: HIGH -- section structure mapped with line numbers from actual file
- LaTeX compilation: LOW -- pdflatex not available, cannot verify compilation

**Research date:** 2026-04-07
**Valid until:** 2026-04-08 (hard SC26 deadline)
