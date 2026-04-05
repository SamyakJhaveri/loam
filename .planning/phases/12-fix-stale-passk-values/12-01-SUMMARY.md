---
phase: 12-fix-stale-passk-values
plan: 01
subsystem: paper
tags: [paper, numerical-audit, provenance, latex]
dependency_graph:
  requires: [results/analysis/paper_data.json]
  provides: [docs/paper/latex/paper.tex updated Abstract-S6.5]
  affects: [Plan 12-02 (remaining sections)]
tech_stack:
  added: []
  patterns: [provenance comments tracing every number to paper_data.json field path]
key_files:
  created: []
  modified:
    - docs/paper/latex/paper.tex
decisions:
  - "Added ERROR column to tab:overall-pass table (1 task) rather than merging with EXTRACTION_FAIL"
  - "Reordered BUILD_FAIL subcategories by count (undeclared_identifier=56 now first, was missing_header=55)"
  - "Added UNKNOWN row to tab:repair-transitions for 1 ERROR-status task"
  - "Self-repair comparison paragraph uses 'final pass rate (38.3%)' instead of 'repair rate (36.2%)' for LASSI comparison"
metrics:
  duration: 7min
  completed: 2026-04-05
  tasks: 3
  files: 1
---

# Phase 12 Plan 01: Update Abstract-S6.5 to 710-task All-Suite Scope Summary

Updated all numerical claims in paper.tex Abstract, Section 1, Sections 5.2-5.3, and Sections 6.1-6.2, 6.4-6.5 from stale Rodinia-only 480-task scope to 710-task all-suite scope using paper_data.json as ground truth, with provenance comments on every updated value.

## What Changed

### Task 1: Abstract + Section 1 + Sections 5.2-5.3
- **Abstract**: 700->710 tasks, 31 eval kernels (was "35 kernels" in campaign context), 38.3% [34.8%, 41.9%] (was 38.0% [34.5%, 41.6%]), z=0.0/p=1.0 (was z=-0.77/p=0.44), 7.2% VERIFY_FAIL (was 7.3%)
- **Section 1 Contributions**: 710 tasks (was 700), 426 pass@k tasks (was 420), 7.2% VERIFY_FAIL (was 7.3%)
- **Section 1 Key Findings**: 38.3% overall (was 38.0%), 6.0% OpenCL-to-CUDA (was 10.0%), 22.5% first-attempt (was 22.1%), 112/550 repaired (was 111/544), 7 regressions 1.0% (was 4 at 0.7%), 70% relative increase (was 72%), z=0.0/p=1.0 Cochran-Armitage
- **Section 5.2**: 142 L0 task pairs (was 96), 710 tasks per model (was 480)
- **Section 5.3**: 142 unique translation pairs at L0 (was 96)

### Task 2: Section 6.1 + Section 6.2
- **S6 preamble**: 1,136 total tasks (was 906), 710 primary (was 480)
- **tab:overall-pass**: Added ERROR column; row: 272/241/144/51/1/1/710/38.3% (was 174/148/110/47/1/480/36.2%)
- **S6.1 prose**: 38.3% [34.8%, 41.9%] across 710 (was 36.2% across 480); 33.9% BUILD_FAIL (was 30.8%); 20.3% RUN_FAIL (was 22.9%); 7.2% VERIFY_FAIL (was 9.8%); 64.2% CUDA-to-OMP (was 65.0%)
- **S6.2 failure distribution**: 438 failures (was 306); BUILD_FAIL 55.0% of failures (was 48.4%); subcategories updated
- **tab:repair-transitions**: Updated all rows; added UNKNOWN row; BUILD_FAIL 72/346=20.8% (was 55/229=24.0%)
- **S6.2 post-table**: 112 repaired (was 90), 22.5% to 38.3% (was 17.5% to 36.2%), 7 regressions (was 5)

### Task 3: Section 6.4 + Section 6.5
- **tab:self-repair**: 710 total, 160 first-attempt (22.5%), 112 repaired (15.8%), 272 total PASS (38.3%), +70.0% relative improvement (was +107.1%), 392 persistent fail, 7 regressions
- **S6.4 prose**: "raises...70.0% relative increase" replaces "doubles"; 22.5% [19.6%, 25.8%] to 38.3% [34.8%, 41.9%]; 550 initially-failing (was 396); 112 repaired at 20.4% (was 90 at 22.7%)
- **tab:augmentation-rates**: n=142 per level (was 96), n=24 C->OMP (was 16); all 10 cells updated
- **S6.5 prose**: n=24 kernels (was 16), z=0.0/p=1.0 (was z=-0.17/p=0.87), pass counts [16,14,17,14,16] (was [11,10,11,9,11])

## Deviations from Plan

None -- plan executed exactly as written.

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| grep -c "38.0\\%" | 0 | 0 | PASS |
| grep -c "z=-0.77" | 0 | 0 | PASS |
| grep -c "710" | 5+ | 40 | PASS |
| grep -c "src: paper_data.json" | many | 77 | PASS |
| grep -c "doubles" | 0 | 0 | PASS |
| grep -c "107.1" | 0 | 0 | PASS |
| grep "z=0.0" in S6.5 | present | present | PASS |
| grep "n=142" in aug table | present | present | PASS |
| Sections 6.3, 6.6-8 unchanged | stale values remain | confirmed | PASS |

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1-3 | b47119d | fix(paper): update Abstract-S6.5 to 710-task all-suite scope |

## Known Stubs

None -- all values in scope are derived from paper_data.json. Remaining stale values in Sections 6.3, 6.6-6.8, 7, and 8 are intentionally deferred to Plan 12-02.

## Self-Check: PASSED

- [x] docs/paper/latex/paper.tex exists and was modified
- [x] Commit b47119d exists in git log
- [x] No stale values (38.0%, z=-0.77, "doubles", 107.1%) remain in covered sections
- [x] 77 provenance comments trace to paper_data.json
