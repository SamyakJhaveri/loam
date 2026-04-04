# Phase 3: Augmentation Analysis & Story - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the per-kernel augmentation evidence from raw Qwen eval results, identify motivating examples (or strengthen the null-result interpretation), produce publication-quality graphs, and write LASSI positioning paragraphs in paper.tex. This phase produces the augmentation narrative and supporting data artifacts for the SC26 paper.

</domain>

<decisions>
## Implementation Decisions

### Matrix data scope (AUG-01)
- **D-01:** Primary matrix covers cuda-to-omp L0-L4 (as specified in AUG-01). This is the primary evaluation direction and has the most data (33 kernel pairs × 5 levels).
- **D-02:** Secondary matrix covers ALL 7 directions with augmented data (624 total L1-L4 files across cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp, omp_target-to-cuda). Store in same JSON file as a separate section. Use secondary data to strengthen claims about direction-independence of the null result.
- **D-03:** L0 data comes from the standard (unaugmented) eval results — same kernel pairs, no `-L` suffix in filename. Matrix must include L0 as the baseline column.

### Narrative framing (AUG-02)
- **D-04:** "Mostly null with interesting exceptions" narrative. The Cochran-Armitage test (z=-0.17, p=0.87) already establishes the aggregate null result. Per-kernel evidence should STRENGTHEN this by showing the vast majority of kernels are stable, while calling out specific exceptions (e.g., backprop L3/L4 BUILD_FAIL) as localized phenomena, not systematic degradation.
- **D-05:** Investigate each exception to determine root cause — is it a transform artifact (augmentation breaks compilation) or genuine model brittleness? This distinction matters for the paper claim. The backprop L3=BUILD_FAIL, L4=BUILD_FAIL pattern needs explanation.
- **D-06:** If exceptions are transform artifacts (augmentation engine issue, not model issue), note them as such and further strengthen the null-result interpretation. If genuine model brittleness, use as motivating examples per Niranjan's directive.

### LASSI positioning (AUG-03)
- **D-07:** Complementary framing, not adversarial. LASSI = agentic self-correction pipeline (80-85% on 10 HeCBench kernels). ParBench augmentation = robustness probing (does surface variation affect model capability?). These answer different research questions.
- **D-08:** Keep LASSI positioning brief — 1-2 paragraphs in the augmentation discussion, not a full comparison table. The related work table already covers LASSI. Focus word budget on the per-kernel evidence, which is the novel contribution.

### Graph design (AUG-04)
- **D-09:** Two figures total for augmentation (tight page budget):
  1. Per-kernel × per-level heatmap (cuda-to-omp): rows=kernels, columns=L0-L4, cells colored by status (PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL). This is the primary evidence figure.
  2. Aggregate trend line: pass rate (%) at each level L0-L4, with Wilson 95% CI error bars. Shows the flat trend that supports the null result.
- **D-10:** Okabe-Ito color palette for all status categories. PDF + PNG output. Publication quality (matplotlib, no interactive).
- **D-11:** Figures go in `docs/paper/figures/` alongside existing paper figures. Generation script goes in `scripts/analysis/`.

### Output organization
- **D-12:** All augmentation analysis data goes into `results/analysis/augmentation_per_kernel_matrix.json` (as specified in AUG-01). Companion `.md` summary file alongside it.
- **D-13:** Follow Phase 2 pattern: single analysis script that computes all metrics and writes the combined JSON. Script in `scripts/analysis/augmentation_analysis.py`.

### Claude's Discretion
- JSON schema structure within the matrix file (section names, key organization)
- Exact matplotlib styling details beyond Okabe-Ito palette
- How to present secondary (non-cuda-to-omp) direction data in the summary
- Ordering of kernels in the heatmap (alphabetical, by pass rate, by SLoC)
- Whether to include confidence intervals on per-kernel cells or only on aggregates

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Raw augmented eval data (primary source of truth)
- `results/evaluation/together-qwen-3.5-397b-a17b/` — Contains ALL augmented result JSONs. Naming: `{src_id}-to-{tgt_id}-L{1-4}.json`. L0 results have no `-L` suffix. Each JSON has `overall_status`, `augmentation_level` (or inferred from filename), and `attempts[]` array.
- 624 augmented files total: 156 per level (L1-L4), across 7 directions
- 33 cuda-to-omp kernel pairs with L1-L4 data (primary matrix)

### Augmentation engine (for understanding levels)
- `c_augmentation/augment_dataset.py` — `LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0}` at line 111. Six transforms: ArithmeticTransform, SwapCondition, PointerArithmeticToArrayIndex, TypedefExpansion, ChangeNames, ChangeFunctionNames.

### Existing augmentation baseline data
- `results/augmentation/rodinia_aug_results.json` — 60 entries, harness-level (not LLM eval). Schema: `spec_id`, `augment_level`, `overall_status`, `transforms_applied`, etc. This is the "augmentation engine is sound" evidence, NOT the LLM eval evidence.

### Statistical analysis
- `results/analysis/statistical_analysis.json` — Has NO augmentation key currently. Cochran-Armitage result (z=-0.17, p=0.87) was computed separately and is in paper.tex lines ~68, ~139.

### Paper
- `docs/paper/latex/paper.tex` — Augmentation engine described in Section 4.3 (line ~313). Augmentation protocol in Section 5 (~line 628). Cochran-Armitage result in abstract (~line 68) and Section 6.1 (~line 139). LASSI referenced in related work table (~line 170).

### Existing analysis scripts (patterns to follow)
- `scripts/analysis/generate_paper_data.py` — Pattern for `--project-root` flag, JSON+MD output
- `scripts/analysis/statistical_analysis.py` — Pattern for statistical computations
- `scripts/generate_paper_figures.py` — Pattern for matplotlib figure generation

### Requirements
- `.planning/REQUIREMENTS.md` — AUG-01 through AUG-04 define the specific tasks

### Prior phase context
- `.planning/phases/01-data-verification-ground-truth/01-CONTEXT.md` — D-07: ground truth = raw result JSONs
- `.planning/phases/02-benchmark-characterization-data/02-CONTEXT.md` — D-01: single combined JSON pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/statistical_analysis.py`: Pattern for computing statistics from raw result JSONs. Follow its `--project-root` convention.
- `scripts/generate_paper_figures.py`: Existing figure generation script. New augmentation figures should follow its matplotlib patterns.
- `results/augmentation/rodinia_aug_results.json`: Harness-level augmentation data (60 entries). Useful as supplementary evidence that the augmentation engine itself is sound.

### Established Patterns
- Analysis scripts accept `--project-root` flag for path resolution
- Output goes to `results/analysis/` as JSON + MD pairs
- Figure output goes to `docs/paper/figures/` as PDF + PNG pairs
- `overall_status` is the authoritative verdict in result JSONs (not `run_status`)
- Result JSONs have `augmentation_level` field (integer 1-4, or absent for L0)

### Integration Points
- Phase 3 output (matrix JSON + figures) feeds Phase 5 for introduction numbers and augmentation discussion
- LASSI positioning paragraphs go directly into paper.tex (Phase 3 writes to the paper)
- Aggregate pass rates from the matrix feed the existing Cochran-Armitage claim validation

### Key Data Inventory
- 33 Rodinia cuda-to-omp kernel pairs with L1-L4 augmented eval data
- 18 unique Rodinia kernels in cuda-to-omp augmented results: backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, kmeans, lavamd, lud, mummergpu, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster
- Backprop shows degradation: L1=PASS, L2=PASS, L3=BUILD_FAIL, L4=BUILD_FAIL
- 7 directions with augmented data total (156 files per level)

</code_context>

<specifics>
## Specific Ideas

- Niranjan (advisor, April 2 meeting): Augmentation motivating examples are "most important task"
- Existing paper already claims Cochran-Armitage z=-0.17, p=0.87 — Phase 3 must provide the per-kernel evidence that backs this aggregate claim
- Backprop is already flagged in known-issues.md as an anomaly (per-kernel capability anomaly) — its augmentation degradation may be related

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-augmentation-analysis-story*
*Context gathered: 2026-04-03*
