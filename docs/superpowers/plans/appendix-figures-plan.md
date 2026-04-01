# Appendix Figures Writing Plan

**Status:** Ready for writer teammate
**Created:** 2026-04-01
**Author:** planner (appendix-figures team)

---

## Overview

18 PNG figures exist in `analysis/visualizations/`. The main paper draft (`docs/paper/paper_draft.md`) defines Figures 1--8, of which only 2 correspond to files in this directory (Figure 2 = `api_cooccurrence_heatmap.png`, Figure 3 = `repo_vs_kernel_comparison.png`). The remaining 16 PNGs are candidates for appendix inclusion. Some are earlier versions of the same visualization (v5, v7 variants).

Three appendix stubs exist:
- `appendix_api_selection.md` — API selection rationale (~1.5--2 pages)
- `appendix_kernel_survey.md` — Kernel survey and selection details (~2--3 pages)
- `appendix_findings.md` — Detailed evaluation findings (~3--4 pages)

---

## Figure Inventory (18 PNGs)

| # | Filename | Content | Version | Main Paper? | Appendix Target |
|---|----------|---------|---------|-------------|-----------------|
| 1 | `api_cooccurrence_heatmap.png` | 15x15 API pairwise co-occurrence matrix (35 repos), annotated cell counts | Original (35 repos) | **Yes — Figure 2** | `appendix_api_selection` (expanded version) |
| 2 | `api_cooccurrence_heatmap_v5.png` | Expanded ~30x30 API co-occurrence matrix (v5 survey, ~80 benchmarks) | v5 (larger survey) | No | `appendix_api_selection` S1 |
| 3 | `api_cooccurrence_network.png` | Force-directed graph: APIs as nodes (sized by #benchmarks), edges = co-occurrence >= 3, colored by API family | Original | No | `appendix_api_selection` S1 |
| 4 | `api_cooccurrence_network_color_v7.png` | Same concept as #3 but v7: more APIs, better coloring by family (CPU parallel, directives, message passing, etc.) | v7 | No | `appendix_api_selection` S1 |
| 5 | `api_coverage.png` | Horizontal bar chart: API coverage across 35 ParBench benchmarks (OpenMP=31, MPI=22, CUDA=20, ..., OpenCL=5) | Original (35 repos) | No | `appendix_api_selection` S1 or S3/S4 |
| 6 | `api_coverage_bar_v5.png` | Bar chart: API coverage across ~80 benchmarks (v5 survey), all 30 APIs shown | v5 | No | `appendix_api_selection` S1 |
| 7 | `repo_vs_kernel_comparison.png` | Dual panel: (left) repo-level vs kernel-level counts log scale, (right) stacked bar by suite source | Original | **Yes — Figure 3** | `appendix_kernel_survey` S1 (expanded detail) |
| 8 | `benchmark_api_bipartite_color_readable_v7.png` | Bipartite network: APIs (squares, left) connected to benchmarks (circles, right), colored by type, grouped by category | v7 (readable) | No | `appendix_kernel_survey` S1 |
| 9 | `bipartite_network.png` | Bipartite network: benchmarks (left) connected to APIs (right), simpler layout | Original | No | `appendix_kernel_survey` S1 |
| 10 | `benchmark_api_count_hist_v5.png` | Histogram: #APIs per benchmark (v5 survey), peak at 3 APIs | v5 | No | `appendix_kernel_survey` S1 |
| 11 | `benchmark_types.png` | Pie chart: benchmark type distribution (Suite=37%, Miniapp=34%, Proxy App=11%, Library=11%, Application=6%) | Original | No | `appendix_kernel_survey` S1 |
| 12 | `kernel_api_bubble.png` | Bubble chart: kernel richness (y) vs API breadth (x), bubble size = kernel count, colored by benchmark type | Original | No | `appendix_kernel_survey` S3 |
| 13 | `top_candidates.png` | Grouped bar chart: top "Rosetta Stone" candidates — kernels (scaled) vs APIs count (HeCBench=513, RAJAPerf=80, etc.) | Original | No | `appendix_kernel_survey` S3 |
| 14 | `quality_tiers.png` | Bar chart: Tier A (30, 85%) vs Tier B (5, 14%) quality distribution | Original | No | `appendix_kernel_survey` S2 |
| 15 | `heatmap.png` | 10x10 API co-occurrence matrix from earlier survey (seed v0, N=21 benchmark suites) | Seed/v0 (21 repos) | No | **Does not fit** (superseded) |
| 16 | `kernel_level_cooccurrence_heatmap.png` | 13x13 kernel-level API co-occurrence with actual kernel counts (CUDA=656, OpenMP=472, HIP=633, etc.) | Original | No | `appendix_api_selection` S1 |
| 17 | `kernel_level_cooccurrence_network.png` | Force-directed network: kernel-level API co-occurrence, edges shown if >= 20 kernel pairs | Original | No | `appendix_api_selection` S1 |
| 18 | `verification_network.png` | Network: benchmarks grouped by verification method (checksum, convergence, reference output, etc.) | Original | No | `appendix_kernel_survey` S6 |

---

## Version Disambiguation

Several figures have multiple versions. The writer should use the **latest/best version** and note alternatives:

| Concept | Versions Available | Recommended for Appendix | Rationale |
|---------|-------------------|--------------------------|-----------|
| API co-occurrence heatmap (repo-level) | `heatmap.png` (v0, 21 repos), `api_cooccurrence_heatmap.png` (35 repos), `api_cooccurrence_heatmap_v5.png` (v5, ~80 repos) | `api_cooccurrence_heatmap_v5.png` | Most comprehensive; paper Figure 2 uses the 35-repo version, so appendix should show the expanded v5 |
| API co-occurrence network | `api_cooccurrence_network.png` (original), `api_cooccurrence_network_color_v7.png` (v7) | `api_cooccurrence_network_color_v7.png` | Better coloring, more APIs, more readable |
| API coverage bar | `api_coverage.png` (35 repos), `api_coverage_bar_v5.png` (v5) | `api_coverage_bar_v5.png` | Expanded survey |
| Bipartite network | `bipartite_network.png` (simple), `benchmark_api_bipartite_color_readable_v7.png` (v7) | `benchmark_api_bipartite_color_readable_v7.png` | Colored, categorized, readable |

---

## Mapping: Figures to Appendix Sections

### Appendix A: API Selection Rationale (`appendix_api_selection.md`)

**Section 1: Full API Co-Occurrence Data**

| Order | Figure File | Appendix Figure # | Suggested Caption |
|-------|------------|-------------------|-------------------|
| 1 | `api_cooccurrence_heatmap_v5.png` | A.1 | "Expanded API co-occurrence heatmap across all surveyed repositories. Cell values indicate the number of repositories providing implementations in both row and column APIs. The concentrated cluster of CUDA/OpenMP/HIP/SYCL co-occurrence motivates the API selection for ParBench." |
| 2 | `api_cooccurrence_network_color_v7.png` | A.2 | "API co-occurrence network (v7). Node size proportional to the number of benchmarks implementing each API; edges drawn for co-occurrence >= 3. APIs colored by family: vendor GPU (cyan), open standard GPU (red), directives (orange), message passing (green), portability libs (grey), CPU parallel libs (blue), single-source C++ (yellow). Peripheral APIs (Chapel, STM/TM, HLS, Python) with co-occurrence < 3 appear as isolated nodes." |
| 3 | `api_coverage_bar_v5.png` | A.3 | "API coverage across the expanded benchmark survey. OpenMP (50), MPI (45), and CUDA (38) dominate, with OpenACC (17), HIP (15), and OpenCL (13) forming a second tier. APIs below 5 benchmarks (GSParLib, STM/TM, HMPP, UPC++, Python, HLS) were excluded from evaluation consideration." |
| 4 | `kernel_level_cooccurrence_heatmap.png` | A.4 | "Kernel-level API co-occurrence matrix. Unlike the repository-level view (Figure A.1), this counts individual kernels with verified equivalent implementations in both APIs. The CUDA--HIP (633) and CUDA--SYCL (616) pairs dominate due to HeCBench's systematic multi-API coverage. The CUDA--OpenMP pair (472) provides the deepest pool for paradigm-crossing translation evaluation." |
| 5 | `kernel_level_cooccurrence_network.png` | A.5 | "Kernel-level API co-occurrence network. Edges shown for >= 20 kernel pairs. The tight CUDA/HIP/SYCL/OpenMP cluster reflects HeCBench and RAJAPerf's uniform multi-API coverage. OpenCL's smaller node and weaker connections reflect its limited presence outside Rodinia and a few suites. RAJA, stdpar, and Thrust appear as isolated nodes with < 20 kernel-level pairs." |

**Data files for prose:** `API_pairwise_coverage_matrix__counts_.csv`, `Per-benchmark_API_availability__indicator_.csv`, `benchmarks_api_matrix_v6_with_links.xlsx`

**Section 3: HIP/SYCL Exclusion Rationale** — No additional figures needed (code examples in prose).

**Section 4: OpenACC Exclusion** — Reference Figure A.3 (api_coverage_bar_v5.png shows OpenACC at 17 benchmarks but only 3 with both OpenACC and CUDA/OpenMP co-occurrence).

**Section 5: OMP-Target Case Study** — No additional figures needed.

**Estimated content:** 5 figures + prose = ~2.5 pages IEEE double-column (slightly over stub target of 1.5--2 pages; consider trimming A.5 if space-constrained).

---

### Appendix B: Kernel Survey and Selection Details (`appendix_kernel_survey.md`)

**Section 1: Full 35-Repository Inventory Table**

| Order | Figure File | Appendix Figure # | Suggested Caption |
|-------|------------|-------------------|-------------------|
| 1 | `benchmark_types.png` | B.1 | "Distribution of benchmark types across the 35 surveyed repositories. Suites (13, 37%) and mini-applications (12, 34%) dominate, providing the richest kernel-level material for translation evaluation." |
| 2 | `benchmark_api_bipartite_color_readable_v7.png` | B.2 | "Bipartite network linking benchmarks (circles) to parallel APIs (squares). Benchmarks colored by type (suite, mini-app, proxy app, library, application); APIs colored by family. Edge color indicates verified download availability (green = verified, grey = unverified). The dense connectivity in the CUDA/OpenMP/HIP cluster demonstrates the concentration of multi-API material in a small number of large suites." |
| 3 | `benchmark_api_count_hist_v5.png` | B.3 | "Distribution of API breadth across surveyed benchmarks. The modal benchmark supports 3 APIs; a long tail extends to 12+ APIs (BabelStream, miniBUDE). Benchmarks supporting >= 3 APIs are the primary candidates for multi-direction translation evaluation." |

**Section 2: Tier A/B Classification Rubric**

| Order | Figure File | Appendix Figure # | Suggested Caption |
|-------|------------|-------------------|-------------------|
| 4 | `quality_tiers.png` | B.4 | "Quality tier distribution. 30 of 35 repositories (85%) meet Tier A criteria (documented build, automated verification, active maintenance). 5 repositories classified Tier B for partial verification or limited API coverage." |

**Section 3: HeCBench Selection Funnel Detail**

| Order | Figure File | Appendix Figure # | Suggested Caption |
|-------|------------|-------------------|-------------------|
| 5 | `kernel_api_bubble.png` | B.5 | "Benchmark kernel richness vs. API breadth. Bubble size proportional to kernel count. HeCBench (513 kernels, 4 APIs) dominates the upper region; RAJAPerf (80 kernels, 5 APIs) is second. Benchmarks in the high-kernel/moderate-API quadrant are optimal for translation evaluation corpus construction." |
| 6 | `top_candidates.png` | B.6 | "Top 'Rosetta Stone' candidates ranked by kernel count and API breadth. HeCBench provides the largest kernel pool (513) but with only 4 APIs; BabelStream and miniBUDE provide the broadest API coverage (12+ APIs) but with few kernels. The selection strategy balances kernel richness against API diversity." |

**Section 6: Exclusion Log** / Verification Methods

| Order | Figure File | Appendix Figure # | Suggested Caption |
|-------|------------|-------------------|-------------------|
| 7 | `verification_network.png` | B.7 | "Benchmarks grouped by verification method. Clusters correspond to verification approaches: checksum comparison, convergence testing, reference output file comparison, and output-to-standard comparison. Benchmarks without automated verification (isolated nodes) were excluded or downgraded to Tier B." |

**Data files for prose:** `hecbench_candidate_kernels.csv`, `hecbench_full_kernel_survey.csv`, `hecbench_batch2_20_selection.csv`, `hecbench_final_20_selection.csv`, `rodinia_survey.json`, `rodinia_api_gaps.json`, `kernel_deep_inspection.json`

**Estimated content:** 7 figures + tables + prose = ~3--3.5 pages IEEE double-column (within stub target of 2--3 pages; may push slightly over with full tables).

---

### Appendix C: Detailed Evaluation Findings (`appendix_findings.md`)

**No figures from `analysis/visualizations/` map to this appendix.**

The findings appendix covers per-kernel failure modes, self-repair transitions, augmentation transform frequencies, OpenCL false-positive forensics, pass@k breakdowns, and XSBench cross-granularity comparisons. These require **new figures** generated from `results/evaluation/` data, not from the survey visualizations in `analysis/visualizations/`.

The writer should note this gap and flag it for Samyak: the findings appendix needs its own visualization pipeline.

---

## Figures That Don't Fit Any Appendix

| Figure File | Why It Doesn't Fit |
|------------|-------------------|
| `heatmap.png` | **Superseded.** Early v0 survey (21 repos). The 35-repo version (`api_cooccurrence_heatmap.png`) is used as paper Figure 2, and the v5 version is recommended for the appendix. This figure is historical and should not be included. |
| `api_cooccurrence_heatmap.png` | **Already paper Figure 2.** The appendix should show the expanded v5 version instead to avoid duplication. Not needed in appendix. |
| `api_cooccurrence_network.png` | **Superseded by v7.** The v7 color version (`api_cooccurrence_network_color_v7.png`) is strictly better. Not needed. |
| `api_coverage.png` | **Superseded by v5.** The v5 bar (`api_coverage_bar_v5.png`) covers more APIs. Not needed. |
| `bipartite_network.png` | **Superseded by v7.** The readable color v7 (`benchmark_api_bipartite_color_readable_v7.png`) is better. Not needed. |
| `repo_vs_kernel_comparison.png` | **Already paper Figure 3.** Could be cross-referenced from appendix prose but should not be re-included as an appendix figure. |

**Summary:** 6 of 18 figures are superseded or already in the main paper. **12 figures** should be included across the two survey appendices (5 in Appendix A, 7 in Appendix B). **0 figures** map to Appendix C (findings), which needs new visualizations.

---

## Data File Reference Map

| Data File | Content | Used By Appendix |
|-----------|---------|-----------------|
| `API_pairwise_coverage_matrix__counts_.csv` | Repo-level API pair counts | A (S1) |
| `Per-benchmark_API_availability__indicator_.csv` | Binary API availability per benchmark | A (S1), B (S1) |
| `benchmarks_api_matrix_v6_with_links.xlsx` | Full survey spreadsheet with links | A (S1), B (S1) |
| `hecbench_candidate_kernels.csv` | HeCBench candidate kernel list | B (S3) |
| `hecbench_full_kernel_survey.csv` | Complete HeCBench kernel survey | B (S3) |
| `hecbench_batch2_20_selection.csv` | Second batch of 20 HeCBench selections | B (S3) |
| `hecbench_final_20_selection.csv` | Final 20 HeCBench curated selections | B (S3) |
| `rodinia_survey.json` | Rodinia kernel survey data | B (S4) |
| `rodinia_api_gaps.json` | Rodinia API gap analysis | B (S4) |
| `kernel_deep_inspection.json` | Deep inspection of candidate kernels | B (S3, S6) |
| `kernel_deep_inspection_old.json` | Earlier version of deep inspection | Not needed (superseded) |
| `wget_all_benchmarks_v6.sh` | Download script for benchmarks | Not needed (infrastructure) |

---

## Writer Instructions

1. **For Appendix A (`appendix_api_selection.md`):**
   - Replace the stub outline with full prose + 5 figures (A.1--A.5)
   - Use `api_cooccurrence_heatmap_v5.png` as the primary expanded view, noting it extends paper Figure 2
   - The network graph (A.2) provides the visual argument for API clustering that supports CUDA/OpenMP/OpenCL selection
   - The kernel-level heatmap (A.4) is the strongest quantitative evidence: 472 CUDA-OpenMP kernel pairs vs. only 27 CUDA-OpenCL pairs at kernel level
   - Reference data files for exact numbers; do not invent statistics

2. **For Appendix B (`appendix_kernel_survey.md`):**
   - Replace the stub outline with full prose + 7 figures (B.1--B.7)
   - The bipartite network (B.2) is information-dense; write a thorough caption explaining what the reader should look for
   - The bubble chart (B.5) and top candidates (B.6) together tell the HeCBench selection story
   - The verification network (B.7) supports the exclusion rationale in S6
   - Reference `hecbench_*.csv` files for funnel stage counts; `rodinia_survey.json` for kernel inventory

3. **For Appendix C (`appendix_findings.md`):**
   - **No existing figures to include** from `analysis/visualizations/`
   - Flag to Samyak: findings appendix needs new figures from eval results
   - The writer can draft prose sections that reference tables (which can be constructed from `results/evaluation/` data), but should leave figure placeholders

4. **Figure references in markdown:**
   - Use format: `![Caption](../../analysis/visualizations/filename.png)`
   - Number as Figure A.1, A.2, ... for api_selection; B.1, B.2, ... for kernel_survey
   - Include `\label{}` equivalents in comments for LaTeX conversion later

5. **Do NOT duplicate main paper figures.** The appendix should extend and expand, providing the full data behind the paper's summarized views. Cross-reference paper figures by number (e.g., "Figure 2 in the main paper shows the 35-repository subset; here we present the complete survey").
