---
phase: 20-paper-final-update
plan: "01"
subsystem: paper-latex
tags: [paper, gpt-numbers, latex, cross-model, numeric-update]
dependency_graph:
  requires: ["19-01"]
  provides: ["overleaf.tex updated", "paper.tex updated", "appendices.tex updated"]
  affects: ["docs/paper/latex/overleaf.tex", "docs/paper/latex/appendices.tex", "docs/paper/latex/paper.tex"]
tech_stack:
  added: []
  patterns: ["grep-anchor-then-edit", "json-to-latex provenance tracking"]
key_files:
  created: []
  modified:
    - docs/paper/latex/overleaf.tex
    - docs/paper/latex/appendices.tex
    - docs/paper/latex/paper.tex
decisions:
  - "Replaced cuda-to-omp_target row with omp_target-to-cuda in cross-model direction table (GPT now has this direction)"
  - "Removed stale '7 of 8 directions' footnote since all 7 common directions now available"
  - "Updated VERIFY_FAIL prose from 'comparable' to 'non-trivial rates' since GPT VF rose from 5.6% to 13.7%"
  - "Pass@k GPT hard_fail/noisy/always_pass columns set to '--' since aggregate_passk no longer contains these keys"
  - "Error taxonomy order swapped: missing_header (151) now exceeds missing_target_api (92) for GPT"
metrics:
  duration: "14 minutes"
  completed: "2026-04-09T02:35:00Z"
  tasks_completed: 5
  tasks_total: 5
  files_modified: 3
---

# Phase 20 Plan 01: Update All GPT-4.1-mini Numbers in Paper Summary

All GPT-4.1-mini numbers in overleaf.tex, appendices.tex, and paper.tex updated to match freshly regenerated analysis JSONs with 942 GPT files (32 new XSBench results).

## One-liner

GPT 177/577=30.7% (was 161/551=29.2%), chi2=7.83 p=0.005 h=0.16, cross-model table restructured with omp_target-to-cuda, per-kernel 18/5/6/1

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update overleaf.tex -- numeric and structural GPT updates | 8a9f71d | docs/paper/latex/overleaf.tex |
| 2 | Update appendices.tex -- self-repair, augmentation, pass@k tables | 317586b | docs/paper/latex/appendices.tex |
| 3 | Apply same numeric edits to paper.tex | 6adae2d | docs/paper/latex/paper.tex |
| 4 | Final verification -- spot-check 10 numbers | (verification only) | -- |
| 5 | Commit final paper update | (covered by Tasks 1-3 atomic commits) | -- |

## Key Changes

### Overall GPT Stats
- **Pass rate**: 30.7% [27.1%, 34.6%] (was 29.2% [25.6%, 33.2%])
- **Total tasks**: 577 (was 551)
- **Pass count**: 177 (was 161)
- **BUILD_FAIL**: 267 (was 316), now 46.3% of tasks (was 57.4%)
- **RUN_FAIL**: 54 (was 43)
- **VERIFY_FAIL**: 79 (was 31), now 13.7% (was 5.6%)

### Cross-Model Statistics
- **Chi-squared**: 7.83 (was 10.97)
- **p-value**: 0.005 (was <0.001)
- **Cohen's h**: 0.16 (was 0.19)
- **Effect size**: negligible (unchanged)
- **Common kernels**: 30 (was 31)

### Structural Changes
- Cross-model direction table: replaced cuda-to-omp_target (0% GPT, invalid) with omp_target-to-cuda (30.0% GPT)
- Per-kernel agreement: 18 both_pass, 5 both_fail, 6 qwen_only, 1 gpt_only (was 13/5/11/2)
- Effect sizes: 2 large (omp-to-cuda h=0.83, omp_target-to-cuda h=1.01), 3 small, 2 negligible
- Error taxonomy: missing_header (151) now top GPT category, missing_target_api (92) second
- Table 1 caption: "campaign in progress" replaced with completed task counts

### Appendices Updates
- Self-repair table: 134 first-attempt pass (was 119), 43 repaired (was 42), +32.1% improvement (was +35.3%)
- Augmentation L0-L4: rates updated (29.3%--33.0%), sample sizes increased (n=115-116)
- Cochran-Armitage: z=0.62, p=0.54 (was z=0.53, p=0.60)
- Pass@k: 25.6% pass@1, 31.5% pass@3, n=90 (was 23.1%, 28.4%, n=88)
- Statistical summary: chi2=7.83, Cramer's V=0.08

### Aggregate
- Combined: 449/1,287 = 34.9% [32.3%, 37.5%] (was 433/1,261 = 34.3%)

## Verification Results

### Spot Checks (10/10 passed)
- GPT total tasks (577): present in overleaf.tex
- GPT pass count (177): present
- GPT pass rate (30.7%): present
- Chi-squared (7.83): present
- Cohen's h (0.16): present
- BUILD_FAIL count (267): present
- Combined total (1,287): present
- Combined pass (449): present
- Per-kernel both_pass=18: present
- OMP_target-to-CUDA h=1.01: present

### LaTeX Structure
- overleaf.tex: begin=30, end=30 (BALANCED)
- paper.tex: begin=28, end=28 (BALANCED)
- appendices.tex: begin=73, end=72, diff=1 (EXPECTED)

### Stale Data Removal
- Old rate 29.2%: 0 occurrences (CLEAN)
- Old total 551 tasks: 0 occurrences (CLEAN)
- Old chi2 10.97: 0 occurrences (CLEAN)
- Old h 0.19: 0 occurrences (CLEAN)
- cuda-to-omp_target: 0 occurrences (CLEAN)
- "campaign in progress": 0 occurrences (CLEAN)
- "7 of 8 evaluated": 0 occurrences (CLEAN)

### Pending Markers
- 0 content-line \pending markers (2 total: both in comment/newcommand lines)
- Hardware GPU model pending marker intentionally retained

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] VERIFY_FAIL prose updated**
- **Found during:** Task 1, Step 8e
- **Issue:** Old text said VERIFY_FAIL "comparable: 7.2% for Qwen versus 5.6% for GPT" but new data shows GPT VERIFY_FAIL jumped to 13.7% (79/577), making "comparable" inaccurate
- **Fix:** Changed prose to "7.2% for Qwen versus 13.7% for GPT, suggesting that both models encounter semantic translation errors at non-trivial rates"
- **Files modified:** overleaf.tex, paper.tex

**2. [Rule 2 - Missing Critical] Error taxonomy order swapped**
- **Found during:** Task 1, Step 8e
- **Issue:** Old text had "missing target API references (196) and missing headers (168)" but new data shows missing_header=151 is now top, missing_target_api=92 is second
- **Fix:** Swapped order: "missing headers (151 instances) and missing target API references (92 instances)"
- **Files modified:** overleaf.tex, paper.tex

**3. [Rule 1 - Bug] Pass@k hard_fail/noisy/always_pass unavailable**
- **Found during:** Task 2, Step 4
- **Issue:** aggregate_passk in new JSON only has pass@1_macro_avg, pass@3_macro_avg, n_tasks, total_samples -- no hard_fail/noisy/always_pass keys
- **Fix:** Set GPT pass@k table cells to '--' for those columns with explanatory % src comment
- **Files modified:** appendices.tex

## Known Stubs

None -- all data values are wired to source JSONs.

## Self-Check: PASSED
