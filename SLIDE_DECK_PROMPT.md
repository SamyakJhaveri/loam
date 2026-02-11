# Claude Co Work Prompt: ParBench Slide Deck

## COPY EVERYTHING BELOW THIS LINE INTO CLAUDE CO WORK

---

Create a **PowerPoint slide deck** (25-35 slides) presenting **ParBench**, a meta-benchmark framework for evaluating LLM-based parallel code translation across GPU/CPU programming APIs.

## Context

This is for a **1-on-1 progress meeting with my advisor** and to **get the rest of the research team up to speed** on my work. The tone should be professional-academic but not overly formal — it's a lab/working group presentation, not a defense. Emphasize schema design, architecture, the harness pipeline, and the end-to-end test results. Earlier survey/inventory phases get lighter coverage.

## Project Overview

ParBench curates kernels from existing benchmark suites (HeCBench, Rodinia, RAJAPerf, etc.) and wraps each in a machine-readable JSON specification that drives automated build → run → verify → LLM evaluation workflows. The key insight is that HeCBench alone contains 506 kernels with CUDA/HIP/SYCL/OpenMP variants — yielding thousands of translation pairs for LLM evaluation.

The project progressed through 5 phases:
1. **Benchmark Survey & Inventory** — surveyed 35 parallel benchmark repos, classified by tier/type/API coverage
2. **Kernel-Level Analysis** — discovered that kernel-level counts are 20-60× higher than repo-level (e.g., 472 CUDA↔OpenMP kernel pairs from just 21 repos)
3. **Schema Design** — designed a two-level metadata system (manifest.jsonl + Level-2 spec JSON files) with JSON Schema draft-07 validation
4. **Harness Implementation** — built a Python CLI harness (1366 lines) that reads spec files and automates build/run/verify/prompt workflows
5. **End-to-End Testing** — full E2E test on real hardware (RTX 4070 + Ryzen 9 7900X), building and running 10 kernels, collecting baselines

## Slide Structure (suggested)

### Opening (2-3 slides)
- Title slide: "ParBench: A Meta-Benchmark for LLM-Based Parallel Code Translation"
- Problem statement: LLMs can translate code, but how do we systematically evaluate translation quality across parallel APIs (CUDA ↔ HIP ↔ SYCL ↔ OpenMP)?
- Motivation: Existing benchmarks exist in isolation; no unified framework connects them for LLM evaluation

### Phase 1-2: Survey & Analysis (3-4 slides)
- 35 benchmark repos surveyed, classified into tiers (30 Tier-A, 5 Tier-B)
- Types: suites, miniapps, proxy apps, libraries, microbenchmarks
- Key finding: kernel-level analysis reveals massive translation pair counts
  - CUDA↔HIP: 633 kernels, CUDA↔SYCL: 616, CUDA↔OpenMP: 472
  - HeCBench dominates with 506 kernels (325 have all 4 APIs)
- **Use the visualization PNGs I'm attaching** (heatmaps, network graphs, bipartite charts, bar charts) on these slides

### Phase 3: Schema Design (5-6 slides) — KEY SECTION
- Two-level metadata architecture diagram:
  - Level 1: `manifest.jsonl` — one line per kernel-variant for discovery & pairing
  - Level 2: `specs/*.json` — comprehensive execution specification
- Show the Level-2 spec structure (identity → provenance → files → implementation → build → run → verification → performance → hardware → baseline_results → metadata)
- **File Security Model** — critical for LLM evaluation integrity:
  - `prompt_payload`: files the LLM receives for translation
  - `support_files`: build infrastructure (Makefiles, headers) NOT shown to LLM
  - `verification_only`: reference implementations NEVER shown to LLM
- Validation system: JSON Schema draft-07 + custom cross-cutting checks (unique_id format, file existence, no file in both prompt_payload and verification_only)
- Translation pair enumeration: same `kernel_name` across different `parallel_api` values = translation pair. 5 kernels × 4 APIs = 20 specs → 60 translation pairs

### Phase 4: Harness Architecture (4-5 slides) — KEY SECTION
- Architecture diagram: CLI → spec_loader → builder → runner → verifier → reporter
- Module breakdown (1366 lines total):
  - `spec_loader.py` (197 lines): loads JSON specs, resolves paths via config/paths.json
  - `builder.py` (262 lines): variable substitution, clean/configure/build pipeline
  - `runner.py` (173 lines): executes with timeout, captures stdout/stderr
  - `verifier.py` (194 lines): exit_code + stdout_pattern strategies, metric extraction
  - `reporter.py` (138 lines): formatted output, JSON export
  - `cli.py` (326 lines): commands — build, run, verify, prompt, info, pairs
  - `models.py` (69 lines): Status enum (PASS/FAIL/ERROR/TIMEOUT/SKIP), result dataclasses
- CLI workflow example: `python -m harness.cli verify specs/hecbench-nn-cuda.json -v`
  - → BUILD: PASS (1.5s) → RUN(correctness): PASS (0.09s) → VERIFY: PASS (exit_code) → METRICS: kernel_time=57.31μs
- `prompt` command: extracts only `prompt_payload` files for LLM evaluation (enforcing the security model)

### Phase 5: E2E Test Results (6-8 slides) — KEY SECTION
- Test platform: RTX 4070 (sm_89, 12GB) + Ryzen 9 7900X (12c/24t) + Ubuntu 22.04
- 5 pilot kernels from HeCBench: nn, scan, particle-diffusion, binomial, radixsort
- 4 APIs each: CUDA, HIP, SYCL, OpenMP → 20 specs, 60 translation pairs
- APIs available: CUDA ✓, OpenMP ✓, HIP ✗, SYCL ✗
- Build results matrix (table): all 10 executables (5 CUDA + 5 OMP) built successfully
- Correctness verification matrix (table):
  - CUDA: 5/5 PASS
  - OMP: 2/5 PASS (nn, scan*), 3/5 FAIL (particle-diffusion, radixsort, binomial)
  - *scan-omp requires OMP_NUM_THREADS=1024 workaround
- **OMP Failure Root-Cause Analysis** (important slide):
  - scan-omp: Blelloch scan needs exact N/2 threads per team; CPU caps at nproc
  - particle-diffusion-omp: `map(alloc:)` aliases host memory on CPU (GPU memory model assumption)
  - radixsort-omp: warp-synchronous scan races with ≥2 CPU threads → SEGFAULT
  - binomial-omp: hangs >10min (hardcoded iteration count × serial tree traversal)
  - All failures are inherent GPU→CPU portability defects in HeCBench source, NOT our build
- Baseline performance metrics (table): 3-run averages for 7 passing specs
- Schema validation: 0 errors, 10 warnings (build artifacts only), all 20 specs valid

### Closing (2-3 slides)
- Current state: working E2E pipeline for 5 pilot kernels, proven on real hardware
- Next steps: scale to full HeCBench (506 kernels), add HIP/SYCL toolchains, begin LLM evaluation experiments
- Architecture enables: automated LLM translation evaluation at scale with correctness guarantees

## Design Notes for Slides

- Use a clean, professional template (dark blue / white / accent color)
- Tables should be prominent — the build/verify matrices are the most valuable visuals
- Use the attached PNG visualizations on the survey/analysis slides
- Include a simplified architecture diagram for the harness (box-and-arrow style)
- Include a simplified diagram showing the two-level metadata system
- Code snippets should be minimal — show just enough JSON to illustrate the spec structure (maybe 10-15 lines of a spec file, not the full 200+ lines)
- Each slide should have a clear takeaway or title that makes the point

## Files Attached for Reference

### MUST-READ (primary content sources):
1. `parbench_sam/README.md` — project overview and structure
2. `parbench_sam/reports/phase5_checkpoint.md` — FINAL E2E test report with all matrices and results
3. `parbench_sam/reports/pilot_report.md` — pilot report with kernel coverage and file classifications
4. `JSON_Schema_for_ParBench.md` — schema design rationale and two-level architecture diagram
5. `parbench_sam/kernel_level_analysis.md` — kernel-level API co-occurrence analysis

### Architecture reference (skim for structure):
6. `parbench_sam/schema/spec_schema.json` — the actual JSON Schema (shows all fields)
7. `parbench_sam/specs/hecbench-nn-cuda.json` — example CUDA spec (representative)
8. `parbench_sam/specs/hecbench-scan-omp.json` — example OMP spec (shows OMP_NUM_THREADS workaround)
9. `parbench_sam/specs/hecbench-radixsort-omp.json` — example failed OMP spec (shows fail_reason)
10. `parbench_sam/manifest.jsonl` — the manifest file
11. `parbench_sam/harness/cli.py` — harness CLI (shows commands and workflow)
12. `parbench_sam/harness/verifier.py` — verification strategies implementation

### Inventory & survey data:
13. `parbench_sam/benchmark_inventory_complete_v3.md` — full benchmark inventory (35 repos)
14. `parbench_sam/kernel_api_inventory.csv` — kernel-level API inventory data
15. `benchmarks_api_matrix_v6_with_links.xlsx - Benchmarks_API_Matrix.csv` — benchmark×API matrix

### Visualizations (INSERT THESE AS IMAGES ON RELEVANT SLIDES):
16. `ParBench/api_cooccurrence_heatmap_v5.png` — API co-occurrence heatmap
17. `ParBench/api_cooccurrence_network_color_v7.png` — API network graph (colored)
18. `ParBench/benchmark_api_bipartite_color_readable_v7.png` — benchmark↔API bipartite graph
19. `ParBench/api_coverage_bar_v5.png` — API coverage bar chart
20. `ParBench/benchmark_api_count_hist_v5.png` — benchmark API count histogram

### Environment:
21. `parbench_sam/reports/environment_check.txt` — hardware/software details

---
END OF PROMPT
