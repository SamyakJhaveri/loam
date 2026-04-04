# Phase 2: Benchmark Characterization Data - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Compute all quantitative benchmark characterization metrics (SLoC, domain categories, API coverage, multi-file breakdown, language features, language standards) and save them as analysis artifacts ready for the paper characterization table (Phase 5) and introduction. All metrics go into a single combined output file.

</domain>

<decisions>
## Implementation Decisions

### Output organization
- **D-01:** All characterization metrics go into a single `results/analysis/benchmark_characterization.json` with companion `.md` summary. One file, one read for downstream phases. No separate files per metric.

### Multi-file classification
- **D-02:** Report both `prompt_payload` file count and `translation_targets` file count per kernel. The "multi-file translation" headline number in the paper uses `translation_targets > 1` (what the LLM must produce). Input file counts (`prompt_payload`) are reported alongside for full context.

### Language feature taxonomy
- **D-03:** Hybrid approach. Each kernel gets an API version tier classification (compact, for the paper characterization table column) plus a full list of specific features found (stored in the JSON for supplementary material or discussion). Tier goes in the table; raw feature data stays in `benchmark_characterization.json`.
  - **OpenMP tiers:** `parallel for` (1.0) -> `simd`, `taskloop` (4.5) -> `target` (4.5+)
  - **CUDA tiers:** `__global__`, `__shared__` (basic) -> `thrust`, `cub` (library) -> `cooperative_groups` (9.0+)
  - **OpenCL tiers:** `clEnqueueNDRangeKernel` (1.x) -> `SVM`, `pipes` (2.0)

### SLoC scope & presentation
- **D-04:** Source (CUDA) SLoC per kernel in the characterization table. Translation size ratio (OMP/CUDA) computed as a derived metric and reported as an aggregate statistic in prose (median, range) rather than as extra table columns.

### Category distribution presentation
- **D-05:** Category distribution as kernel counts with suite annotations. Each of the 12 categories shows total kernel count plus which suites contribute. e.g., `stencil: 5 kernels (rodinia: 3, hecbench: 2)`. Supports both breadth argument and suite complementarity narrative.

### API coverage cross-tab
- **D-06:** API coverage cross-tab uses kernel count per cell (distinct kernels with a spec for that API in each suite). Four separate API columns: CUDA, OMP, OpenCL, OMP Target — showing the full picture even though omp_target is excluded from standard eval batches.

### SLoC validation strategy
- **D-07:** Re-run `sloc_analysis.py` fresh during Phase 2, validate all 35 kernels present with correct counts, then fold the SLoC data into `benchmark_characterization.json` as a section. Existing `sloc_analysis.json` remains on disk but the combined characterization file becomes the canonical source for Phase 5.

### Claude's Discretion
- Script architecture: new standalone script vs extending existing scripts
- JSON schema structure within `benchmark_characterization.json` (sections, key names)
- Specific grep regex patterns for language feature detection (once tiers are agreed)
- Ordering of metrics within the combined file
- How to handle kernels with missing source directories (HeCBench source is local/gitignored)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Data sources
- `manifest.jsonl` — Append-only kernel registry. Source of truth for kernel names, categories, APIs, suites. 211 entries (includes 5 phantom spec entries).
- `specs/` — 206 spec JSON files. Each contains `implementation.language_standard`, `files.prompt_payload`, `files.translation_targets`, and `identity.category`.
- `results/analysis/sloc_analysis.json` — Existing SLoC analysis covering all 35 kernels. To be re-run and validated, then folded into combined characterization.

### Existing scripts
- `scripts/analysis/sloc_analysis.py` — SLoC counter covering all 35 corpus kernels. Uses `CORPUS_KERNELS` list. Produces JSON + MD output.
- `scripts/analysis/generate_paper_data.py` — Consolidates raw results into `paper_data.json`. Accepts `--project-root` and `--suite` flags.

### Source directories (for language feature grep)
- `rodinia/rodinia-src/` — Rodinia benchmark source (git submodule, commit 9c10d3ea). Contains cuda/, omp/, opencl/ subdirectories.
- `xsbench-src/` — XSBench source directory.
- `HeCBench-master/` — HeCBench source (gitignored, cloned locally, 1874 dirs). NOT available in worktrees.
- `rsbench-src/`, `mixbench-src/` — RSBench and mixbench sources (if present on disk).

### Paper
- `docs/paper/latex/paper.tex` — The paper. Characterization table goes in Section 4 (assembled in Phase 5).

### Requirements
- `.planning/REQUIREMENTS.md` — CHAR-01 through CHAR-06 define the specific characterization tasks. CHAR-07 (LaTeX table) deferred to Phase 5.

### Prior phase context
- `.planning/phases/01-data-verification-ground-truth/01-CONTEXT.md` — Phase 1 decisions. D-07 (ground truth = raw files), D-08/D-09 (regenerate analysis at end), D-10 (data freeze) carry forward.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/sloc_analysis.py`: Already covers all 35 kernels with physical SLoC counting, category, complexity class, OMP SLoC. Can be re-run and output folded into characterization JSON.
- `manifest.jsonl`: Structured JSONL with `category`, `parallel_api`, `source_suite`, `kernel_name` fields — direct source for CHAR-02 (categories) and CHAR-03 (API coverage).
- Spec JSON `implementation.language_standard` field: Direct source for CHAR-06 (language standard distribution). Values include `C++14`, `C99`, etc.
- Spec JSON `files.prompt_payload` and `files.translation_targets`: Direct source for CHAR-04 (multi-file breakdown).

### Established Patterns
- Analysis scripts accept `--project-root` flag for path resolution
- Output goes to `results/analysis/` as JSON + MD pairs
- `manifest.jsonl` is append-only — 5 phantom entries exist for deleted specs (filter by checking spec file existence)
- `CORPUS_KERNELS` in `sloc_analysis.py` defines the 35-kernel evaluation corpus

### Integration Points
- Phase 2 output (`benchmark_characterization.json`) is consumed by Phase 5 for the LaTeX characterization table and introduction numbers
- SLoC range (min-max), median, multi-file percentage, and category count become introduction headline numbers (INTRO-01)
- Translation size ratio (OMP/CUDA) becomes prose in methodology or results discussion

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for script architecture and JSON schema design.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-benchmark-characterization-data*
*Context gathered: 2026-04-03*
