---
phase: 07-full-analysis-regeneration
verified: 2026-04-04T21:15:00Z
status: passed
score: 12/12 must-haves verified
gaps: []
human_verification: []
---

# Phase 7: Full Analysis Regeneration Verification Report

**Phase Goal:** Re-run all analysis scripts against the complete 1,248-file Qwen 3.5 397B evaluation dataset to produce fresh JSON and Markdown outputs covering all 5 benchmark suites.
**Verified:** 2026-04-04T21:15:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | eval_summary.json reflects all 1,248 Qwen result files (post-KNOWN_FAIL exclusion = 1,136) | VERIFIED | `by_model.together-qwen-3.5-397b-a17b.total` = 1136, `by_status` sums to 1136, 8 directions, 31 kernels, 5 augment levels (L0-L4) |
| 2 | paper_data generated twice: Rodinia-only (480 primary) and full-dataset (710 primary) | VERIFIED | `paper_data_rodinia.json` has `suite_filter="rodinia"`, `primary_campaign=480`; `paper_data.json` has `suite_filter=null`, `primary_campaign=710` |
| 3 | error_taxonomy.json covers failure modes across ALL suites | VERIFIED | 34 total kernels in `per_kernel`, 7 non-Rodinia: convolution1d, floydwarshall, mixbench, rsbench, scan, stencil1d, xsbench |
| 4 | selfrepair_analysis.json includes cross-suite self-repair rates | VERIFIED | 34 total kernels in `by_kernel`, 7 non-Rodinia kernels present with real data |
| 5 | statistical_analysis.json includes cross-suite statistical tests | VERIFIED | 31 total kernels in `wilson_cis.by_kernel`, 7 non-Rodinia kernels present |
| 6 | sloc_analysis.json unchanged from Phase 2 (35 kernels) | VERIFIED | md5sum = `c47aed4c259cf2dedfc638bd9eded286` (matches expected), 35 kernels confirmed |
| 7 | token_analysis.json includes cost estimates for all tasks | VERIFIED | `total_results` = 1136 (post-KNOWN_FAIL exclusion) |
| 8 | benchmark_characterization.json validated with zero errors | VERIFIED | `validate_characterization.py` exits 0, 8/8 checks PASS, all 6 CHAR sections present |
| 9 | translation_complexity.csv covers all 5 suites | VERIFIED | 5 suites (hecbench=150, rodinia=110, xsbench=12, rsbench=12, mixbench=6), 290 total pairs |
| 10 | augmentation_per_kernel_matrix.json validated with real data | VERIFIED | 4 top-level keys, `primary_matrix.per_kernel` has 26 kernels with real L0-L4 data across 5 suites |
| 11 | No script errors during execution | VERIFIED | All output files contain valid computed data; all verification assertions pass; commits f4b9283, 12ed8c6, fecd748, 83c4362 verified in git log |
| 12 | All Markdown companion files regenerated | VERIFIED | 5 .md files exist: eval_summary.md (2574B), error_taxonomy.md (10542B), selfrepair_analysis.md (4554B), statistical_analysis.md (18270B), token_analysis.md (3524B) |

**Score:** 12/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `results/evaluation/eval_summary.json` | Aggregate eval summary for 1,248 files | VERIFIED | 10554 bytes, 1136 tasks, 356 PASS (31.3%) |
| `results/evaluation/eval_summary.md` | Human-readable summary | VERIFIED | 2574 bytes |
| `results/analysis/paper_data_rodinia.json` | Rodinia-only 480-task scope | VERIFIED | 44193 bytes, suite_filter="rodinia", primary=480 |
| `results/analysis/paper_data.json` | Full cross-suite 710-task scope | VERIFIED | 51690 bytes, suite_filter=null, primary=710 |
| `results/analysis/error_taxonomy.json` | Failure mode taxonomy across all suites | VERIFIED | 448398 bytes, 34 kernels, 7 non-Rodinia |
| `results/analysis/error_taxonomy.md` | Human-readable taxonomy | VERIFIED | 10542 bytes |
| `results/analysis/selfrepair_analysis.json` | Self-repair rates across all suites | VERIFIED | 12203 bytes, 34 kernels, 7 non-Rodinia |
| `results/analysis/selfrepair_analysis.md` | Human-readable self-repair | VERIFIED | 4554 bytes |
| `results/analysis/statistical_analysis.json` | Wilson CIs, McNemar, Cochran-Armitage | VERIFIED | 30279 bytes, 31 kernels, 7 non-Rodinia |
| `results/analysis/statistical_analysis.md` | Human-readable statistics | VERIFIED | 18270 bytes |
| `results/analysis/token_analysis.json` | Token cost estimates for 1,136 tasks | VERIFIED | 24006 bytes, total_results=1136 |
| `results/analysis/token_analysis.md` | Human-readable token analysis | VERIFIED | 3524 bytes |
| `results/analysis/sloc_analysis.json` | SLoC for 35 kernels (Phase 2, unchanged) | VERIFIED | 31425 bytes, md5=c47aed4c259cf2dedfc638bd9eded286, 35 kernels |
| `results/analysis/benchmark_characterization.json` | 6-metric characterization (Phase 2) | VERIFIED | 82700 bytes, 8/8 validation checks PASS |
| `results/evaluation/translation_complexity.csv` | 290 pairs across 5 suites | VERIFIED | 26331 bytes, 5 suites, 290 rows |
| `results/analysis/augmentation_per_kernel_matrix.json` | Per-kernel augmentation matrix | VERIFIED | 21634 bytes, 26 kernels in per_kernel |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| 1,248 result JSONs on disk | eval_summary.json | analyze_eval.py | WIRED | `total_tasks=1136` (1248 minus 112 KNOWN_FAIL exclusions) matches 6-status breakdown |
| 1,248 result JSONs | paper_data.json | generate_paper_data.py (no --suite) | WIRED | `total_on_disk=1248`, `primary_campaign=710` |
| 1,248 result JSONs | paper_data_rodinia.json | generate_paper_data.py --suite rodinia | WIRED | `suite_filter="rodinia"`, `primary_campaign=480` |
| 1,248 result JSONs | error_taxonomy.json | build_error_taxonomy.py | WIRED | All 1248 results classified (no KNOWN_FAIL exclusion) |
| 1,248 result JSONs | selfrepair_analysis.json | selfrepair_analysis.py | WIRED | All 1248 results analyzed |
| 1,248 result JSONs | statistical_analysis.json | statistical_analysis.py | WIRED | 1136 results (KNOWN_FAIL excluded via analyze_eval import) |
| 1,248 result JSONs | token_analysis.json | token_analysis.py | WIRED | `total_results=1136` |
| specs/*.json + manifest.jsonl | translation_complexity.csv | classify_translation_pairs.py | WIRED | 290 pairs across 5 suites |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| eval_summary.json | by_model.*.total | 1,248 result JSON files | Yes: 1136 tasks with 6-way status breakdown summing correctly | FLOWING |
| paper_data.json | file_counts.primary_campaign | 1,248 result JSON files | Yes: 710 primary tasks with real pass rates | FLOWING |
| error_taxonomy.json | per_kernel | 1,248 result JSON files | Yes: 34 kernels with real failure classifications | FLOWING |
| statistical_analysis.json | wilson_cis.by_kernel | 1,248 result JSON files | Yes: 31 kernels with real CI calculations | FLOWING |
| token_analysis.json | total_results | 1,248 result JSON files | Yes: 1136 results with $39.03 cost estimate | FLOWING |
| augmentation_per_kernel_matrix.json | primary_matrix.per_kernel | Result JSON files | Yes: 26 kernels with L0-L4 status data | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| eval_summary total matches disk files minus exclusions | `1248 - 112 = 1136` vs `eval_summary.total=1136` | Match | PASS |
| by_status sums to total | `459+66+356+233+21+1 = 1136` | Match | PASS |
| paper_data Rodinia preserves 480-task scope | `paper_data_rodinia.json primary_campaign` | 480 | PASS |
| paper_data full has more tasks than Rodinia | `710 > 480` | True | PASS |
| validate_characterization exits 0 | Script run | 8/8 checks PASS, exit=0 | PASS |
| sloc_analysis md5 unchanged | `md5sum` comparison | c47aed4c259cf2dedfc638bd9eded286 matches | PASS |
| translation_complexity 5 suites | CSV suite column Counter | 5 distinct suites, 290 rows | PASS |
| augmentation matrix 26 kernels at correct path | `primary_matrix.per_kernel` length | 26 | PASS |

### Requirements Coverage

Phase 7 requirements (REGEN-01 through REGEN-10) are defined in the ROADMAP and PLAN frontmatter. They are not listed in REQUIREMENTS.md (which tracks v1 requirements from the broader sprint).

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| REGEN-01 | 07-01 | eval_summary total > 1000 | SATISFIED | total=1136 |
| REGEN-02 | 07-01 | Dual paper_data (Rodinia 480 + full 710) | SATISFIED | Both files exist with correct scopes |
| REGEN-03 | 07-01 | error_taxonomy cross-suite | SATISFIED | 7 non-Rodinia kernels |
| REGEN-04 | 07-01 | selfrepair cross-suite | SATISFIED | 7 non-Rodinia kernels |
| REGEN-05 | 07-01 | statistical cross-suite | SATISFIED | 7 non-Rodinia kernels |
| REGEN-06 | 07-02 | sloc_analysis unchanged | SATISFIED | md5 match confirmed |
| REGEN-07 | 07-02 | token_analysis total > 1000 | SATISFIED | total_results=1136 |
| REGEN-08 | 07-02 | characterization validation 0 errors | SATISFIED | 8/8 PASS, exit=0 |
| REGEN-09 | 07-02 | translation_complexity 5 suites | SATISFIED | 5 suites, 290 pairs |
| REGEN-10 | 07-02 | augmentation matrix validated | SATISFIED | 26 kernels in primary_matrix.per_kernel |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | No anti-patterns found in analysis scripts or output files |

All 8 analysis scripts scanned for TODO/FIXME/PLACEHOLDER/stub patterns: zero matches. All output JSON files contain real computed values, not empty arrays or placeholder data.

### Human Verification Required

No human verification items identified. All truths are verifiable programmatically through file existence checks, JSON field validation, md5sum comparison, and script exit code verification. The phase produces data files (not UI components), so no visual or behavioral testing is needed.

### Gaps Summary

No gaps found. All 12 ROADMAP success criteria are met, all 10 REGEN requirements are satisfied, all 16 artifacts exist with real data, all 8 key links are wired, and all data flows produce real computed values from the 1,248-file Qwen evaluation dataset.

**Note on REGEN-10 PLAN verification assertion:** The 07-02-PLAN.md contains `len(d['primary_matrix']) >= 10` which checks top-level structural keys (8 keys) rather than the per-kernel count. The actual data is correct -- 26 kernels reside at `primary_matrix.per_kernel`. This verification used the correct nested path and confirmed 26 kernels.

---

_Verified: 2026-04-04T21:15:00Z_
_Verifier: Claude (gsd-verifier)_
