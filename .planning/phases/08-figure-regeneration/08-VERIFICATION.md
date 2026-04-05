---
phase: 08-figure-regeneration
verified: 2026-04-05T00:50:00Z
status: human_needed
score: 9/10 must-haves verified
gaps: []
deferred: []
human_verification:
  - test: "Visually inspect F3 heatmap for readability: 29 kernel labels legible, suite divider lines visible, status colors distinguishable, suite labels on left margin correctly positioned"
    expected: "29 rows grouped by suite (Rodinia 21, XSBench 1, RSBench 1, mixbench 1, HeCBench 5) with black divider lines at suite boundaries and rotated suite labels"
    why_human: "Visual layout quality (font overlap, spacing, color contrast) cannot be verified programmatically"
  - test: "Visually inspect F6 cross-suite bar chart: 5 bars visible with error bars, pass/total annotations readable, y-axis goes to 1.0"
    expected: "5 bars for Rodinia (34.5%), XSBench (0%), RSBench (0%), mixbench (33.3%), HeCBench (90.0%) with Wilson CI error bars and pass/total text above each bar"
    why_human: "Bar chart readability and annotation positioning cannot be verified programmatically"
  - test: "Visually inspect F4 failure taxonomy: stacked bars for 6 directions, status colors with hatch patterns distinguishable"
    expected: "6 stacked bars (26, 26, 23, 23, 20, 20 tasks) with PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL segments, count labels inside segments"
    why_human: "Hatch pattern visibility and label legibility at publication size need human eye"
  - test: "Export parbench_architecture.drawio to PDF manually (ROADMAP SC #10)"
    expected: "parbench_architecture.pdf exists in docs/paper/figures/"
    why_human: "Requires draw.io application; explicitly designated as manual user task in D-11/D-12"
  - test: "Verify T2 table renders correctly in LaTeX compilation"
    expected: "2-row table (Qwen populated, GPT-4.1 mini pending) with proper column alignment and percentages"
    why_human: "LaTeX rendering and IEEE column width fit require actual compilation"
---

# Phase 8: Figure Regeneration Verification Report

**Phase Goal:** Re-run figure generation against refreshed analysis outputs to produce fresh publication-quality figures (PDF + PNG) for the SC26 paper. All 6 main-body figures (F2-F7) and 4 appendix figures (C.1-C.4) plus the T2 LaTeX table must reflect the complete 1,248-task Qwen 3.5 397B dataset across 5 suites.
**Verified:** 2026-04-05T00:50:00Z
**Status:** human_needed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 6 main-body figure PDFs exist and are non-empty | VERIFIED | f2 (15.7KB), f3 (49KB), f4 (42.8KB), f5 (13.1KB), f6 (13.3KB), f7 (11.6KB) -- all regenerated Apr 4 20:46 |
| 2 | All 4 appendix figure PDFs exist and are non-empty | VERIFIED | c1 (18.8KB), c2 (14.5KB), c3 (88.3KB), c4 (21.1KB) -- all regenerated Apr 4 20:46 |
| 3 | T2 LaTeX table exists with 2-row layout (Qwen populated, GPT-4.1 mini pending) | VERIFIED | t2_model_comparison.tex (395 bytes): Qwen 49/138 (35.5%) fully populated, GPT-4.1 mini shows "pending" x7 |
| 4 | Every PDF has a matching PNG file | VERIFIED | All 10 PDFs have matching PNGs confirmed present and non-empty |
| 5 | F3 heatmap includes ALL suites' kernels (29 kernels, not just Rodinia 18) | VERIFIED | Pipeline output: "Total kernels in standard directions: 29" (rodinia:21, xsbench:1, rsbench:1, mixbench:1, hecbench:5) |
| 6 | F4 failure taxonomy covers failure modes across ALL suites | VERIFIED | Pipeline output: 138 tasks across 6 directions (26+26+23+23+20+20) with no suite filter in code |
| 7 | F7 augmentation robustness uses fresh L0-L4 data | VERIFIED | Pipeline output: L0:61.5%, L1:53.8%, L2:65.4%, L3:53.8%, L4:61.5% (26 kernels each). Data loaded directly from result JSONs per D-07 decision (not paper_data.json as ROADMAP SC7 stated, but equivalent source) |
| 8 | Script changes are minimal and tested | VERIFIED | Single file modified (scripts/generate_paper_figures.py). Script parses without syntax errors. All 11 figures generate without errors. |
| 9 | No matplotlib warnings, missing data placeholders, or empty subplots | VERIFIED | Full pipeline run (`--figure all -v`) produced zero warnings, zero "skip" messages, zero errors |
| 10 | parbench_architecture.drawio exported to PDF | NOT MET | .drawio source exists but no PDF export. Per D-11/D-12, this is a manual user task outside the script. |

**Score:** 9/10 truths verified (1 requires manual user action)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/generate_paper_figures.py` | Updated with 2-model layout, 5-suite coverage | VERIFIED | Old models removed, GPT-4.1 mini added, SUITE_ORDER has 5 suites, F3/F4/F6/F7 redesigned |
| `docs/paper/figures/f2_repo_vs_kernel.pdf` | F2 figure | VERIFIED | 15,682 bytes, Apr 4 20:46 |
| `docs/paper/figures/f3_kernel_model_heatmap.pdf` | F3 29-kernel heatmap | VERIFIED | 49,000 bytes, Apr 4 20:46, 29 kernels across 5 suites |
| `docs/paper/figures/f4_failure_taxonomy.pdf` | F4 failure taxonomy all suites | VERIFIED | 42,768 bytes, Apr 4 20:46, 138 tasks |
| `docs/paper/figures/f5_pass_at_k_by_direction.pdf` | F5 pass@k | VERIFIED | 13,142 bytes, Apr 4 20:46, 414 sample records |
| `docs/paper/figures/f6_cross_suite_comparison.pdf` | F6 cross-suite comparison | VERIFIED | 13,324 bytes, Apr 4 20:46, 5 suites with Wilson CIs |
| `docs/paper/figures/f7_augmentation_robustness.pdf` | F7 augmentation Qwen-only | VERIFIED | 11,621 bytes, Apr 4 20:46, L0-L4 rates |
| `docs/paper/figures/c1_repair_transition_matrix.pdf` | C.1 transition matrix | VERIFIED | 18,768 bytes, 624 multi-attempt records |
| `docs/paper/figures/c2_repair_rate_by_direction.pdf` | C.2 repair rate | VERIFIED | 14,486 bytes, 6 directions |
| `docs/paper/figures/c3_transform_frequency.pdf` | C.3 transform frequency | VERIFIED | 88,279 bytes, 22 kernels x 5 transforms |
| `docs/paper/figures/c4_selection_funnel.pdf` | C.4 HeCBench funnel | VERIFIED | 21,097 bytes, 506->60 pipeline |
| `docs/paper/figures/t2_model_comparison.tex` | T2 LaTeX table | VERIFIED | 395 bytes, 2-row layout, Qwen populated + GPT pending |
| `docs/paper/figures/parbench_architecture.pdf` | Architecture diagram PDF | NOT FOUND | .drawio source exists; PDF export is manual user task per D-11 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `generate_paper_figures.py` | `results/evaluation/together-qwen-3.5-397b-a17b/*.json` | `load_eval_results()` | WIRED | 1,248 records loaded (780 base, 468 sample) |
| `t2_model_comparison.tex` | `docs/paper/latex/paper.tex` | `\input{}` | NOT WIRED | T2 table file exists but is not yet `\input`-ed in paper.tex. Paper has its own tab:model-config table. Integration is a paper-writing concern, not a figure-generation concern. |
| `generate_paper_figures.py` | FIGURE_REGISTRY | function dispatch | WIRED | All 11 entries in FIGURE_REGISTRY map to existing functions. Main dispatch tested via `--figure all`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| F3 heatmap PDF | `std_records` from `load_eval_results()` | 1,248 result JSONs | Yes: 29 kernels x 6 directions rendered | FLOWING |
| F4 taxonomy PDF | `std_records` filtered L0 | result JSONs | Yes: 138 tasks, 6 directions | FLOWING |
| F6 cross-suite PDF | `std_records` grouped by suite | result JSONs | Yes: 5 suites with pass/total counts | FLOWING |
| F7 augmentation PDF | `c2o_all` filtered by direction | result JSONs | Yes: L0-L4, 26 kernels each level | FLOWING |
| T2 LaTeX table | `qwen_records` from filtered records | result JSONs | Yes: 49/138 overall with per-direction breakdown | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Script parses without syntax errors | `python3 -c "import ast; ast.parse(...)"` | "SYNTAX OK" | PASS |
| No old model references | `grep "claude-sonnet\|groq-llama\|gemini-2.5"` | 0 matches | PASS |
| No old fallback data | `grep "AUG_ROBUSTNESS\|XSBENCH_L0\|_XS_MODELS"` | 0 matches | PASS |
| GPT-4.1 mini present in constants | `grep "azure-gpt-4.1-mini"` | 4 matches (MODEL_COLORS, MODEL_DISPLAY, MODEL_DISPLAY_SHORT, MODEL_LINESTYLE) | PASS |
| SUITE_ORDER has 5 suites | `grep "SUITE_ORDER"` | Contains rodinia, xsbench, rsbench, mixbench, hecbench | PASS |
| Full pipeline runs without warnings | `python3 generate_paper_figures.py --figure all -v` | 11 figures generated, 0 warnings, 0 errors | PASS |
| build_kernel_model_matrix default suite=None | `grep "def build_kernel_model_matrix"` | `suite: str \| None = None` | PASS |
| F6 function renamed | `grep "generate_f6_xsbench"` | 0 matches (old function removed) | PASS |
| Old helpers removed | `grep "_draw_heatmap_panel\|_draw_taxonomy_panel"` | 0 matches | PASS |
| No TODO/FIXME/PLACEHOLDER | `grep -i "TODO\|FIXME\|PLACEHOLDER"` | 0 matches | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-----------|-------------|--------|----------|
| FIG-01 | 08-01, 08-02 | Figure generation script updated | SATISFIED | Script modernized with 2-model layout, 5-suite coverage |
| FIG-02 | 08-02 | All PDFs and PNGs generated | SATISFIED | 10 PDFs + 10 PNGs + 1 LaTeX table, all non-empty |
| FIG-03 | 08-02 | T2 table restructured | SATISFIED | 2-row layout, Qwen populated, GPT pending |
| FIG-04 | 08-02 | Pipeline runs without errors | SATISFIED | Zero warnings, zero skipped figures |
| FIG-05 | 08-01 | F3 heatmap redesigned for all suites | SATISFIED | 29 kernels x 6 directions, grouped by suite |
| FIG-06 | 08-01 | F4 taxonomy uses all suites | SATISFIED | 138 tasks across 6 directions, no suite filter |
| FIG-07 | 08-02 | Appendix figures regenerated | SATISFIED | C.1-C.4 all regenerated with fresh data |

**Note:** FIG-01 through FIG-07 are referenced in ROADMAP.md but were never formally defined in REQUIREMENTS.md. The descriptions above are inferred from the ROADMAP success criteria and PLAN frontmatter. This is a requirements documentation gap, not a code gap.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| docs/paper/figures/f6_xsbench_comparison.pdf | N/A | Stale artifact from old F6 design | Info | Old file still on disk alongside new f6_cross_suite_comparison.pdf. Not a code issue; cleanup optional. |

### Human Verification Required

### 1. F3 Heatmap Visual Quality

**Test:** Open `docs/paper/figures/f3_kernel_model_heatmap.pdf` and inspect the 29-kernel heatmap at publication size (IEEE double-column width).
**Expected:** 29 kernel labels legible on y-axis; 5 suite groups separated by thick black horizontal lines; suite labels (Rodinia, XSBench, RSBench, mixbench, HeCBench) visible on left margin rotated 90 degrees; status cell colors distinguishable; status abbreviations (P, BF, RF, VF, EF) readable in cells.
**Why human:** Font sizing, label overlap, color contrast, and overall visual composition quality at print size cannot be verified programmatically.

### 2. F6 Cross-Suite Bar Chart Readability

**Test:** Open `docs/paper/figures/f6_cross_suite_comparison.pdf` and check bar chart layout.
**Expected:** 5 bars with distinct colors, Wilson CI error bars visible, "pass/total" annotations above each bar readable, y-axis labeled "Pass Rate" from 0 to ~1.15.
**Why human:** Annotation positioning relative to error bars and bar heights, and overall readability at IEEE single-column width.

### 3. F4 Failure Taxonomy Readability

**Test:** Open `docs/paper/figures/f4_failure_taxonomy.pdf` and verify stacked bar legibility.
**Expected:** 6 direction bars with stacked status segments, count labels inside segments visible, hatch patterns distinguishable in print.
**Why human:** Hatch pattern visibility and count label legibility within small segments require visual inspection.

### 4. Architecture Diagram PDF Export

**Test:** Export `docs/paper/figures/parbench_architecture.drawio` to PDF using draw.io.
**Expected:** `parbench_architecture.pdf` generated in `docs/paper/figures/`.
**Why human:** Requires draw.io application; explicitly designated as manual user task per context decisions D-11 and D-12.

### 5. T2 Table LaTeX Compilation

**Test:** Compile paper.tex and verify T2 table renders correctly (once integrated).
**Expected:** 2-row table fits IEEE column width, percentages display correctly, "pending" entries render as expected.
**Why human:** LaTeX rendering, column width fitting, and visual alignment require actual compilation.

### Gaps Summary

No automated gaps were found. All 9 programmatically verifiable success criteria are met:

- All 10 figure files (6 main + 4 appendix) generated as PDF + PNG pairs with substantive file sizes
- T2 LaTeX table generated with correct 2-model layout
- Script constants cleaned: only Qwen + GPT-4.1 mini, no old models, no fallback data
- SUITE_ORDER expanded to 5 suites, reflected in F3, F4, F6, F7
- Full pipeline runs with 1,248 records, zero warnings
- F3 shows 29 kernels grouped by suite; F4 covers 138 tasks across all suites; F6 shows 5-suite comparison; F7 shows Qwen-only L0-L4

The one unmet success criterion (architecture drawio PDF export) is explicitly a manual user task per the implementation decisions (D-11, D-12). The 5 human verification items are all visual quality checks that cannot be automated.

---

_Verified: 2026-04-05T00:50:00Z_
_Verifier: Claude (gsd-verifier)_
