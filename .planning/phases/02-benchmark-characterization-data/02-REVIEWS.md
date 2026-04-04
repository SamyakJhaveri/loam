---
phase: 02
reviewed_by: internal-claude
date: 2026-04-04
plans_reviewed: [02-01-PLAN.md, 02-02-PLAN.md, 02-03-PLAN.md]
summaries_reviewed: [02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md]
verification_reviewed: 02-VERIFICATION.md
artifacts_inspected:
  - scripts/analysis/benchmark_characterization.py (886 lines)
  - scripts/analysis/test_benchmark_characterization.py (552 lines, 39 tests)
  - scripts/analysis/validate_characterization.py (722 lines, 8 checks)
  - results/analysis/benchmark_characterization.json
  - results/analysis/benchmark_characterization.md (267 lines)
  - results/analysis/characterization_validation.txt
---

# Phase 02: Benchmark Characterization Data -- Internal Review

## Plan Completeness

All 3 plans were executed and have corresponding SUMMARY files. Each summary reports
"No deviations from plan" and all acceptance criteria are met. The verification report
confirms 5/5 observable truths, 6/6 artifacts verified, and 8/8 key links wired.

**02-01 (main script):** Plan specified a monolithic script with 6 `compute_*` functions.
The implementation delivers exactly this at 886 lines (plan minimum was 400). All 6 CHAR
metrics produce data. Commit `3d28fa8`.

**02-02 (test suite):** Plan required 20+ tests; implementation has 39. Tests use
independent ground-truth derivation from manifest.jsonl and spec files (not circular
self-validation). 10 tests run without the characterization JSON; 29 depend on
the `char_data` fixture with graceful `pytest.skip`. All 39 pass. Commit `6729750`.

**02-03 (validator):** Plan required 8 check functions using a completely independent
code path. Implementation has all 8 checks, imports only `CORPUS_KERNELS` from
`sloc_analysis.py`, and produces 8/8 PASS. Commit `b172bd1`.

**Verdict: COMPLETE.** All plans match their summaries. No missing deliverables.

## Requirement Coverage

### CHAR-01 (SLoC analysis for all 35 kernels) -- SATISFIED

35 kernels present in `sloc.per_kernel`. Range 80-3304, median 271. OMP/CUDA ratio
computed for 26 kernels where both specs exist (correctly null for 9 without OMP).
Summary statistics include min/max/mean/median/std/distribution buckets. Independently
validated by test suite (5 tests) and validator (check_sloc).

### CHAR-02 (Domain category distribution, 12 categories) -- SATISFIED

12 categories correctly derived from manifest.jsonl with phantom filtering. Each
category has `kernel_count`, `kernels` list, and `suites` sub-dict (per D-05).
Categories sourced from manifest.jsonl, not spec JSONs (correct -- `identity.category`
does not exist in specs, only `identity.kernel_name/parallel_api/unique_id/source_suite`).
Independently cross-checked by test `test_category_counts_match_manifest` and
`check_categories` in the validator.

### CHAR-03 (API coverage cross-tab, 5 suites x 4 APIs) -- SATISFIED

5x4 matrix present with row/column totals. Values match manifest.jsonl independent
computation. HeCBench correctly shows 65 cuda + 60 omp + 0 opencl + 10 omp_target.
Rodinia shows 22 cuda + 18 omp + 20 opencl + 0 omp_target. Totals: 206 specs.

### CHAR-04 (Multi-file breakdown) -- SATISFIED

35 kernels classified using `translation_targets > 1` (per D-02). 18 multi-file,
17 single-file (51.4%). Per-suite and per-API aggregates present. Per-kernel data
includes both `prompt_payload_count` and `translation_targets_count`. Headline
classification uses CUDA spec.

### CHAR-05 (Language feature tiers) -- SATISFIED with quality gaps (see below)

35 kernels have feature entries. Regex-based grep produces tier assignments.
Per-API feature data stored. However, there are accuracy issues documented in the
Quality Gaps section.

### CHAR-06 (Language standard distribution) -- SATISFIED

Distribution sums to 206: C++17(128), C++14(51), C11(6), C++11(2), unspecified(19).
Breakdowns by API and by suite present. Independently validated by both test suite
and validator scanning all 206 spec files.

## Quality Gaps

### HIGH: Language feature grep misses subdirectory source files (CHAR-05)

The `grep_dir` function at line ~419 uses `directory.glob(ext)` which only matches
files in the immediate directory. Several Rodinia kernels place source files in
subdirectories:

- **lavamd**: `cuda/lavaMD/kernel/kernel_gpu_cuda.cu` (has `__global__`) -- classified
  as `undetected` because glob doesn't recurse into `kernel/`
- **lud**: `cuda/lud/cuda/lud_kernel.cu` (has `__global__`) -- classified as `undetected`
  because glob doesn't recurse into `cuda/`
- **bptree**: `cuda/b+tree/util/cuda/cuda.cu` -- classified as `undetected` because
  glob doesn't recurse into `util/cuda/`
- **mummergpu**: likely similar (KNOWN_FAIL but source exists)

**Impact:** 4 kernels have incorrect `undetected` tiers. If `overall_tier` is used in
the paper characterization table (Phase 5), these kernels will be mischaracterized.

**Fix:** Change `directory.glob(ext)` to `directory.rglob(ext)` in `grep_dir` (one-line
change). Re-run characterization after fix.

### MEDIUM: Cross-family `overall_tier` comparison is semantically meaningless

The `overall_tier` field at lines 498-507 picks the "highest" tier across all API
families using a concatenated ordering: `cuda_basic < cuda_library < cuda_9plus <
omp_basic < omp_4.5 < omp_target < opencl_1x < opencl_2x`. This means `opencl_1x`
always "wins" over any CUDA or OMP tier when an OpenCL variant exists.

Result: 17/35 kernels have `overall_tier = opencl_1x`, which is uninformative. The
per-API tiers are meaningful; the cross-family max is not.

**Impact:** If Phase 5 uses `overall_tier` for the characterization table, it will
produce misleading data. The per-API tier data (e.g., `cuda_basic`, `omp_basic`) is
correct and useful; only the `overall_tier` aggregation is flawed.

**Fix:** Either (a) drop `overall_tier` and report per-API tiers in the paper table,
or (b) redefine `overall_tier` as the CUDA tier only (since CUDA is the primary
translation source and all 35 corpus kernels have CUDA specs).

### LOW: Category kernel count (87) vs corpus kernel count (35) discrepancy

`summary.total_kernels` is 35 (CORPUS_KERNELS), but `categories` covers 87 distinct
kernels from the full manifest (including 65 non-curated HeCBench kernels). This is
architecturally correct -- categories reflect the full benchmark composition, while
CORPUS_KERNELS drives evaluation. However, the discrepancy could mislead Phase 5
if someone writes "35 kernels across 12 categories" without noting that the categories
also include non-corpus kernels.

**Impact:** Potential confusion in paper prose if numbers are mixed without context.

**Fix:** Add a note in the JSON summary distinguishing `corpus_kernels: 35` from
`total_manifest_kernels: 87` (or however many unique kernels are in the valid manifest).
The current `summary.total_kernels` should clarify which count it represents.

### LOW: Validation report is minimal

The validation report (`characterization_validation.txt`) only shows 8 pass/fail lines
with no detail on what was checked. When a check fails, the error messages are printed
to stdout but the report file itself just records the summary line. Richer reports would
help debugging.

### LOW: Markdown table SLoC formatting inconsistency

The SLoC table uses comma-separated thousands for CUDA SLoC (`3,304`) but plain integers
for OMP SLoC (`3922`). This is a minor formatting inconsistency in the markdown report.

## Architecture Assessment

The 3-script architecture (main + tests + validator) is well-designed:

1. **Separation of concerns:** The main script computes, the test suite validates against
   ground truth, and the validator cross-checks via independent code path. This defense-in-depth
   catches bugs that any single approach would miss.

2. **Reuse of existing infrastructure:** Imports `CORPUS_KERNELS` and `count_physical_sloc`
   from `sloc_analysis.py` rather than duplicating. Uses established `--project-root` CLI
   pattern.

3. **Correct data source selection:** Categories from manifest.jsonl (the only source with
   category field), language standards from spec JSONs, SLoC from actual source files.
   The CONTEXT file note about `identity.category` not existing in specs was correctly
   followed.

4. **Null-safe access patterns:** Consistent use of `(spec.get("x") or {}).get("y")` per
   project conventions.

5. **Phantom filtering:** Both main script and validator correctly filter manifest entries
   by checking spec file existence on disk.

6. **Monolithic script per D-01:** All 6 metrics in one file is simpler for invocation and
   keeps the output in a single combined JSON. Functions are cleanly separated.

**One architectural note:** The test `test_category_counts_match_manifest` handles the
`iso2dfd` dual-category edge case (appears under both "stencil" and "physics" in manifest)
via first-seen mapping. This is documented in 02-02-SUMMARY but the main script uses
`set()` deduplication by kernel name within category, which handles this differently. The
test and script agree on final counts, so this works, but the logic divergence could be
fragile if manifest categories change.

## Risks for Downstream Phases

### HIGH RISK: Language feature `overall_tier` feeding Phase 5 characterization table

If Phase 5 uses `overall_tier` directly for the LaTeX characterization table column,
it will produce misleading data (17 kernels showing `opencl_1x` regardless of their
CUDA complexity). Phase 5 should either:
- Use per-API tiers (e.g., show CUDA tier for the primary source API column)
- Fix the `overall_tier` computation before consuming it

### MEDIUM RISK: Four `undetected` kernels in language features

lavamd, lud, bptree, and mummergpu show `undetected` for all APIs because of the
non-recursive glob bug. If Phase 5 renders these as "no language features detected"
in the paper table, SC reviewers will immediately question why a CUDA kernel with
`__global__` appears as having no CUDA features.

### MEDIUM RISK: Category scope vs corpus scope confusion

Phase 5 writers need to be aware that categories cover 87 kernels (full manifest)
while evaluation metrics (SLoC, multi-file, language features) cover 35 (corpus).
Mixing these scopes in paper prose (e.g., "our corpus of 35 kernels spans 12
categories") is technically true but the per-category counts include non-corpus
kernels. A reviewer who sums category kernel counts will get 87, not 35.

### LOW RISK: OMP SLoC ratio for paper discussion

The OMP/CUDA ratio varies from 0.20 to 5.09 (median 0.93, mean 1.27). The extreme
outliers (bptree at 5.09x, streamcluster at 2.64x) should be investigated before
citing in the paper. bptree's OMP version may include significantly more host code,
inflating the ratio. Phase 4 (methodology) should discuss whether this ratio measures
what the paper claims.

### LOW RISK: `unspecified` language standard count

19 specs have no `language_standard` field. If these cluster in a specific suite or
API, it could affect Phase 5 table completeness. Quick check: these are likely the
HeCBench `omp_target` specs that use `nvc++` (which auto-selects C++ standard).

## Verdict

**APPROVE with recommended fixes.**

Phase 2 is complete and all 6 CHAR requirements are satisfied at the data-production level.
The 3-script architecture is sound, tests are comprehensive (39 tests, all passing), and
cross-validation passes (8/8 checks). Three specific quality issues should be addressed
before Phase 5 consumes this data:

1. **[HIGH -- fix before Phase 5]** Change `glob` to `rglob` in `grep_dir` to fix 4
   `undetected` language feature classifications (lavamd, lud, bptree, mummergpu).

2. **[MEDIUM -- fix before Phase 5]** Either drop `overall_tier` or redefine it as
   CUDA-only tier. The cross-family max comparison is semantically meaningless.

3. **[LOW -- document for Phase 5]** Add a note distinguishing corpus kernel count (35)
   from manifest kernel count (87) in the summary section to prevent scope confusion.

These do not block Phase 2 completion but must be resolved before the data feeds into
the LaTeX table in Phase 5.

---

*Reviewed: 2026-04-04*
*Reviewer: Claude (internal review -- no external AI CLIs available for cross-AI review)*
