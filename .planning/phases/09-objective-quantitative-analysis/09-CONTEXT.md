# Phase 9: Objective Quantitative Analysis - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a comprehensive, structured quantitative findings document (`results/analysis/quantitative_findings.json` + `quantitative_findings.md`) that extracts every publishable number from the Phase 7 analysis outputs and raw result JSONs. This document becomes the single source of truth for paper claims — every number in paper.tex must trace to a specific field in this file. The analysis covers 14 dimensions: per-suite, per-direction, per-level, per-kernel, per-complexity-class, and cross-cutting comparisons. Two evaluation campaigns (deterministic + pass@k) are analyzed separately.

</domain>

<decisions>
## Implementation Decisions

### Script Architecture
- **D-01:** Single monolithic script `scripts/analysis/quantitative_findings.py` — consistent with Phase 2 (benchmark_characterization.py) and Phase 3 (augmentation_analysis.py) patterns.
- **D-02:** Compute directly from raw result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/`. Do NOT depend on intermediate analysis files (paper_data.json, etc.) as primary data source — raw files are ground truth per Phase 1 D-07.
- **D-03:** After computing from raw, cross-check against existing analysis JSONs (paper_data.json, statistical_analysis.json, etc.) and warn on discrepancies >0.1%. This catches stale derived files.
- **D-04:** In practice, compute ALL eval-derived metrics fresh from raw result JSONs (per D-02). The only planned exception: SLoC data reads from existing `benchmark_characterization.json` / `sloc_analysis.json` (verified in Phase 2 — SLoC is a static source property, not an eval result). Claude may pull additional static metadata from existing analysis if justified, but eval pass rates, failure counts, and statistical tests must come from raw.

### Two-Campaign Separation (CRITICAL)
- **D-05:** Two evaluation campaigns must be analyzed SEPARATELY, never pooled:
  - **Campaign 1 (Deterministic):** Augmentation levels L0–L4, 3 max retries (self-repair), temperature=0.0, 1 sample per task. All suites, all API directions.
  - **Campaign 2 (pass@k):** L0 only, 1 max try (no self-repair), temperature=0.7, 3 samples per task (pass@k where k=3). All suites, all API directions.
- **D-06:** File discrimination by filename suffix: `-s{0,1,2}` suffix → Campaign 2 (seed variants). No suffix or `-L{1-4}` suffix → Campaign 1. Both live in the same directory.
- **D-07:** Campaign 1 feeds 12+ dimensions (aggregate, direction, asymmetry, augmentation, failure taxonomy, self-repair, per-kernel tiers, complexity, cross-suite, token cost, SLoC correlation, OpenCL effect). Campaign 2 feeds pass@k dimension. Provenance (dim 14) applies to both. Claude has discretion on exact dimension-to-campaign mapping.
- **D-08:** No cross-campaign comparison. Campaigns stay completely separate to avoid confounding temperature/retry effects with translation capability.

### Data Scope
- **D-09:** Analyze the full 1,248-file dataset across all 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench) with per-suite breakdowns.
- **D-10:** Auto-exclude the 8 KNOWN_FAIL specs (6 Rodinia + 2 HeCBench) by default — they have no valid results.
- **D-11:** No `--suite` filter. Full dataset always. Per-suite breakdowns handle separation.
- **D-12:** omp_target directions go in a dedicated "case-study" section, separate from the 6 standard directions. Matches existing convention (known-issues.md, XSBench SESSION 8 notes).

### File Discovery & Classification
- **D-13:** Glob `results/evaluation/together-qwen-3.5-397b-a17b/*.json`, parse each filename to extract source spec, target spec, augmentation level, seed number. Same approach as existing `generate_paper_data.py`.
- **D-14:** Complexity classes derived from spec JSON fields (`translation_targets`, `prompt_payload`): single_file, multi_to_single, single_to_multi, multi_to_multi. Chi-squared test (or Fisher's exact for small cell counts) for pass rate differences across complexity classes (per ROADMAP SC-9).

### pass@k Method
- **D-15:** Simple fraction per task: count passing seeds / total seeds (0/3, 1/3, 2/3, 3/3), then aggregate. No extrapolation beyond k=3. Note: ROADMAP SC-7 mentions k=1,3,5,10 but only k=3 is computable from 3 seeds without extrapolation — report pass@1 (any seed passes) and pass@3 (all seeds pass) as the two extremes.
- **D-16:** Campaign 2 gets full per-direction + per-suite pass@k breakdowns (not just aggregate).

### Output & Diagnostics
- **D-17:** Quiet output with final summary line (files processed, dimensions computed, cross-check warnings). `-v` flag for verbose debugging mode.

### Output Structure
- **D-18:** Campaign-first JSON layout: top-level keys `metadata`, `campaign_1` (12+ dimension subsections), `campaign_2` (pass@k subsections), `cross_checks`.
- **D-19:** Provenance per finding: `{ "value": 0.362, "source": "computed from 1248 raw JSONs", "files_matched": 480, "derivation": "PASS count / total tasks" }`. Auditable without overwhelming.
- **D-20:** Confidence intervals as separate numeric fields: `{ "value": 0.362, "ci_lower": 0.321, "ci_upper": 0.406, "ci_level": 0.95 }`. Machine-readable. 95% Wilson CIs throughout.
- **D-21:** All internal numeric values stored as decimals 0-1 (e.g., 0.362 not 36.2). Display formatting happens in markdown and paper.
- **D-22:** Dedicated `paper_claims` section mapping each paper.tex claim to a specific JSON field (claim_id, paper_location, field path, display value). Enables Phase 11 audit.
- **D-23:** Both output files in `results/analysis/`: `quantitative_findings.json` + `quantitative_findings.md`.

### Markdown Companion
- **D-24:** Paper-ready tables, copy-pasteable into Phase 10/11 drafting. One table per dimension.
- **D-25:** Separate campaign sections mirroring JSON structure (Campaign 1 tables, then Campaign 2 tables).
- **D-26:** Per-kernel tables ordered by pass rate (easiest or hardest first) to make difficulty tiers visible.
- **D-27:** Brief 1-line objective observations after each table (e.g., "cuda-to-omp has 2.1x higher pass rate than omp-to-cuda"). Directs attention without subjective interpretation.
- **D-28:** Error taxonomy: top-level failure type counts (BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL) plus top-3 most common build error subcategories.
- **D-29:** Self-repair: compute from raw `attempts[]` arrays in Campaign 1 result JSONs. Consistent with raw-first principle.

### Statistical Methods
- **D-30:** McNemar's test for direction asymmetry computed from raw paired data (same kernel, opposite directions). Not read from existing analysis.
- **D-31:** Cochran-Armitage trend test computed for ALL directions separately AND aggregate. Tests whether augmentation null result holds across all directions. Cohen's h effect sizes between adjacent augmentation levels (per ROADMAP SC-4).
- **D-32:** Per-kernel difficulty tiers: quartile-based by L0 pass rate, plus explicit top-5 easiest and top-5 hardest kernel lists.
- **D-33:** OpenCL kernel-only effect: compare all X-to-OpenCL (kernel-only) pass rates vs all X-to-OMP (full program) pass rates. Statistical test: Claude's discretion (Fisher's exact test or Chi-squared, whichever is appropriate for the sample sizes).
- **D-34:** SLoC correlation method: Claude's discretion (Spearman and/or Pearson with p-values).
- **D-35:** Token cost: Together AI pricing for Qwen 3.5 397B, stored as constants in script.
- **D-36:** Exactly the 14 roadmap dimensions — no extras. 95% Wilson CIs matching existing conventions.

### Validation & Spot-Checks
- **D-37:** `--validate` flag performs automated spot-checks of 10+ critical paper claim numbers by independently counting raw files. Reports PASS/FAIL per check.
- **D-38:** Validation also runs cross-check comparison (raw-computed vs existing analysis JSONs) and includes discrepancies in the report. Warn-only policy — discrepancies never cause validation failure.
- **D-39:** Validation includes internal consistency checks: CI_lower <= value <= CI_upper, per-suite weighted averages match aggregate, file counts sum correctly, no NaN/null in required fields.
- **D-40:** Validation includes paper claims pre-audit: parse paper.tex for claim locations listed in `paper_claims`, compare values, report which claims need updating. Pre-feeds Phase 11.
- **D-41:** Validation output: print to stdout AND write `results/analysis/quantitative_findings_validation.json`.
- **D-42:** No `--dry-run` mode. Script is deterministic from static files — just run it.

### Claude's Discretion
- JSON metadata content (file counts, timestamps, git hash — whatever aids reproducibility)
- SLoC correlation method selection (Spearman vs Pearson vs both)
- Dimension-to-campaign mapping for edge cases
- Exact kernel ordering direction (ascending vs descending pass rate)
- Spot-check target selection (critical paper claims, Claude picks the specific numbers)
- How to handle edge cases in complexity classification (e.g., multi-file specs with only one translation target)
- Statistical test selection for OpenCL kernel-only effect (Fisher's exact vs Chi-squared — see D-33)
- Statistical test selection for complexity correlation (Chi-squared vs Fisher's exact for small cells — see D-14)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Raw result data (primary source of truth)
- `results/evaluation/together-qwen-3.5-397b-a17b/` — ALL raw result JSONs (Campaign 1: `{src}-to-{tgt}.json`, `{src}-to-{tgt}-L{1-4}.json`; Campaign 2: `{src}-to-{tgt}-s{0,1,2}.json`). Each JSON has `overall_status`, `attempts[]`, `augmentation_level`, `total_input_tokens`, `total_output_tokens`.

### Spec files (for complexity classification and KNOWN_FAIL list)
- `specs/*.json` — Kernel spec JSONs. Fields `translation_targets`, `prompt_payload` determine complexity class. `identity.status` or known-issues.md for KNOWN_FAIL list.
- `manifest.jsonl` — Kernel registry for enumerating all kernel pairs.

### Existing analysis files (for cross-check comparison)
- `results/analysis/paper_data.json` — Aggregate and per-direction pass rates (Phase 7 output)
- `results/analysis/statistical_analysis.json` — Wilson CIs, Cochran-Armitage, McNemar results
- `results/analysis/error_taxonomy.json` — Failure taxonomy with subcategories
- `results/analysis/selfrepair_analysis.json` — Self-repair rates and attempt analysis
- `results/analysis/token_analysis.json` — Token counts and cost estimates
- `results/analysis/augmentation_per_kernel_matrix.json` — Per-kernel augmentation data
- `results/analysis/benchmark_characterization.json` — SLoC, categories, multi-file breakdown
- `results/analysis/sloc_analysis.json` — Per-kernel SLoC counts (read for SLoC correlation)

### Existing analysis scripts (for reference patterns)
- `scripts/analysis/generate_paper_data.py` — Reference for glob + filename parsing pattern
- `scripts/analysis/statistical_analysis.py` — Reference for Wilson CI, Cochran-Armitage, McNemar implementations
- `scripts/analysis/selfrepair_analysis.py` — Reference for attempts[] parsing
- `scripts/analysis/build_error_taxonomy.py` — Reference for error subcategory extraction

### Paper (for claim mapping and pre-audit)
- `docs/paper/latex/paper.tex` — The paper. Claim locations referenced in `paper_claims` section.

### Known issues
- `.claude/rules/known-issues.md` — KNOWN_FAIL spec list (8 specs), campaign conventions, eval result schema quirks

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/generate_paper_data.py` — Glob + filename parsing pattern for result JSONs. Can be used as reference for Campaign 1/2 file discrimination logic.
- `scripts/analysis/statistical_analysis.py` — Wilson CI, Cochran-Armitage, McNemar implementations already exist. Can reference these for algorithm correctness even though the script computes from raw.
- `scripts/analysis/benchmark_characterization.py` — Single-file monolithic pattern that Phase 9 follows.

### Established Patterns
- All analysis scripts in `scripts/analysis/` use `argparse`, `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`, and write to `results/analysis/`.
- Result JSONs use `overall_status` as authoritative verdict (not `run_status`).
- `or {}` guard for nullable JSON fields: `(spec.get("field") or {}).get("subfield", default)`.

### Integration Points
- Output files consumed by Phase 10 (qualitative narrative) and Phase 11 (paper TeX integration).
- `paper_claims` section consumed by Phase 11 for automated claim audit.
- Validation report consumed by Phase 11 to identify stale paper.tex numbers.

</code_context>

<specifics>
## Specific Ideas

- The two-campaign separation is a critical user requirement. Campaign 1 (deterministic, self-repair, augmentation) and Campaign 2 (stochastic, pass@k) answer fundamentally different research questions and must never be pooled.
- The `paper_claims` mapping section should enable a mechanical audit: iterate each claim, check if the paper.tex value matches the findings value. This is the provenance backbone for the paper.
- Brief observations in the markdown companion should be objective and quantitative (e.g., "2.1x difference") not interpretive (e.g., "surprisingly high"). Interpretation is Phase 10's job.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-objective-quantitative-analysis*
*Context gathered: 2026-04-04*
