# Phase 12: Fix Stale Pass@k Values in Paper.tex - Research

**Researched:** 2026-04-05
**Domain:** LaTeX paper numerical claims audit and correction against JSON ground truth
**Confidence:** HIGH

## Summary

Phase 12 requires updating every numerical claim in paper.tex (Abstract, Section 1, Sections 6.1-6.8, Section 7, and Section 8) from stale Rodinia-only 480-task scope to the all-suite 710-task scope in `results/analysis/paper_data.json`. The scope change affects approximately 150+ individual numbers across prose, tables, provenance comments, and derived ratios. The discrepancy arose because Phase 1 Plan 05 regenerated analysis files with `--suite rodinia` (480 tasks), while the Abstract and Introduction were later updated in Phase 5 to reference `quantitative_findings.json` (700 tasks, a different exclusion list). The ground truth per D-01 is `paper_data.json` (710 tasks, 6 Rodinia KNOWN_FAIL excluded).

Three distinct numerical scopes currently coexist in the paper:
1. **Sections 6-8**: Rodinia-only from `paper_data_rodinia.json` (480 tasks, 96 L0 pairs, 18 kernels)
2. **Abstract/Intro**: From `quantitative_findings.json` (700 tasks, 140 L0 pairs, 35 kernels with 8 KNOWN_FAIL excluded)
3. **Ground truth**: `paper_data.json` (710 tasks, 142 L0 pairs, 31 evaluated kernels with 6 Rodinia KNOWN_FAIL excluded)

All sections must converge on scope 3. The pass@k campaign data (426 tasks, 142 pairs) is UNCHANGED -- it was always Rodinia-only and remains correct. The only pass@k change is the reference to greedy pass@1 (36.2% -> 38.3%).

**Primary recommendation:** Execute a systematic section-by-section update of paper.tex, working through the complete discrepancy map below, updating both numerical values and provenance comments. Each section should be independently verifiable against paper_data.json.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The single source of truth is `results/analysis/paper_data.json` (all 5 suites: Rodinia, XSBench, RSBench, mixbench, HeCBench). NOT `paper_data_rodinia.json`.
- **D-02:** The paper should present data from all benchmark suites -- Rodinia-only scope is rejected. The 710-task primary campaign and all derived statistics come from the all-suite file.
- **D-03:** Full audit of ALL numerical claims in Sections 6.1-6.8 and Section 7.1-7.5. Not limited to the 8 originally-identified stale pass@k values.
- **D-04:** Intro/abstract numbers also updated in this phase (from 700 tasks/38.0% to 710 tasks/38.3%), not deferred to Phase 11.
- **D-05:** All LaTeX provenance comments (`% src: ...`) updated to reference `paper_data.json` with correct field paths. Comments that currently say `paper_data.json` but cite Rodinia-only numbers (480 tasks) are fixed to cite the all-suite numbers (710 tasks).
- **D-06:** Every updated number gets a provenance comment tracing to the exact JSON field and value.
- **D-07:** Section 7 (Discussion) is included in the same update pass as Section 6. All repeated numbers (direction rates, augmentation stats, pass@k references) are updated to match Section 6's corrected values.

### Claude's Discretion
- Rounding conventions for percentages (1 decimal place consistent with existing style)
- How to handle the new ERROR status (1 task) in failure taxonomy -- likely group with EXTRACTION_FAIL or note separately
- Paragraph rewrites needed when numbers change direction ranking order

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VERIFY-01 | Every numerical claim in Sections 1-5 cross-checked against ground truth JSON files | Complete discrepancy map below provides exact old->new values for every numerical claim in the paper |
</phase_requirements>

## Standard Stack

This phase requires no libraries or code changes. It is a pure LaTeX text-editing phase operating on a single file (`docs/paper/latex/paper.tex`) with data from a single ground truth file (`results/analysis/paper_data.json`). [VERIFIED: direct file reads]

## Architecture Patterns

### Source File Structure

```
docs/paper/latex/paper.tex       -- The paper (1226 lines, single file)
results/analysis/paper_data.json -- Ground truth (710-task all-suite scope)
results/analysis/quantitative_findings.json -- Secondary reference (700-task scope, NOT the ground truth)
```

### Provenance Comment Convention

Established in Phase 1, every numerical claim in paper.tex is annotated with a provenance comment:
```latex
% src: paper_data.json > primary_campaign > overall: 272/710=38.3%; CI [0.3481,0.4194]
Qwen~3.5 achieves an overall pass rate of 38.3\% [34.8\%, 41.9\%]...
```

Comments trace to the exact JSON field path, value, and computation. Phase 12 must update both the comment and the prose value. [VERIFIED: paper.tex contains ~50 provenance comments]

### Rounding Convention
- Percentages: 1 decimal place (e.g., 38.3%, not 38.31%)
- Confidence intervals: 1 decimal place (e.g., [34.8%, 41.9%])
- Counts: exact integers (e.g., 272, not ~270)
- Cohen's h: 2 decimal places (e.g., 0.28)
- p-values: 2-4 significant figures (e.g., p=1.0, p=0.6875)
- z-statistics: 1-2 decimal places (e.g., z=0.0, z=-0.77)
[VERIFIED: existing paper.tex formatting]

## Complete Discrepancy Map

This section provides the COMPLETE mapping from current stale values to correct values. Every value was verified by reading `paper_data.json` directly. [VERIFIED: all values extracted via Python from paper_data.json]

### Scope Change Summary

| Property | Stale (S6-S8) | Stale (Abstract/S1) | Correct (paper_data.json) |
|----------|---------------|---------------------|---------------------------|
| Source file | paper_data_rodinia.json | quantitative_findings.json | paper_data.json |
| Suites | Rodinia only | All 5 (8 excl.) | All 5 (6 excl.) |
| Primary tasks | 480 | 700 | 710 |
| L0 pairs | 96 | 140 | 142 |
| Eval kernels | 18 | 35 | 31 |
| pass@k tasks | 426 | 420 | 426 |
| pass@k pairs | 142 | -- | 142 |
| KNOWN_FAIL excluded | 6 Rodinia | 8 (6R+2H) | 6 Rodinia |

### Key Number: Why 710, not 700?

`paper_data.json` excludes only 6 Rodinia KNOWN_FAIL specs (112 files excluded from 1248).
`quantitative_findings.json` excludes 8 specs including 2 HeCBench omp_target (128 files excluded).
The 10-task difference (710-700) comes from including hecbench-stencil1d-omp_target and hecbench-scan-omp_target results. Per D-01, paper_data.json is authoritative. [VERIFIED: paper_data.json file_counts]

### Abstract (lines 56-73)

| Claim | Current | Correct | JSON Path |
|-------|---------|---------|-----------|
| Task count | 700 | 710 | file_counts.primary_campaign |
| Overall rate | 38.0% [34.5%, 41.6%] | 38.3% [34.8%, 41.9%] | primary_campaign.overall |
| Overall count | 266/700 | 272/710 | primary_campaign.overall.pass/total |
| BUILD_FAIL % | 33.9% (237/700) | 33.9% (241/710) | primary_campaign.overall.by_status.BUILD_FAIL |
| VERIFY_FAIL % | 7.3% (51/700) | 7.2% (51/710) | 51/710=7.18% rounds to 7.2% |
| Cochran-Armitage | z=-0.77, p=0.44 | z=0.0, p=1.0 | augmentation.cochran_armitage |
| CUDA-to-OMP all-level | 64.2% | 64.2% | by_direction.cuda-to-omp.pass_rate (UNCHANGED) |
| CUDA-to-OMP L0 | 66.7% at L0 | 66.7% at L0 | augmentation.cuda_to_omp_balanced.L0 (UNCHANGED) |
| Augmentation n_kernels | 16 kernels (implicit) | 24 kernels | augmentation.cochran_armitage.n_kernels |

**NOTE on Cochran-Armitage:** The abstract currently uses the quantitative_findings.json ALL-DIRECTION aggregate (z=-0.77, p=0.44, n=140/level). paper_data.json provides the CUDA-to-OMP balanced test (z=0.0, p=1.0, n=24/level). The planner must decide which to present. The CONTEXT.md D-01 says paper_data.json is ground truth. The z=0.0, p=1.0 result is STRONGER evidence for the null hypothesis.

### Section 1 - Key Findings Preview (lines 146-159)

| Claim | Current | Correct | JSON Path |
|-------|---------|---------|-----------|
| Overall rate | 38.0% [34.5%, 41.6%] | 38.3% [34.8%, 41.9%] | primary_campaign.overall |
| Task count | 700 tasks | 710 tasks | file_counts.primary_campaign |
| BUILD_FAIL % of tasks | 33.9% | 33.9% | 241/710 (UNCHANGED at 1dp) |
| VERIFY_FAIL % of tasks | 7.3% | 7.2% | 51/710 |
| CUDA-to-OMP | 64.2% | 64.2% | (UNCHANGED) |
| OpenCL-to-CUDA | 10.0% | 6.0% | by_direction.opencl-to-cuda.pass_rate |
| First-attempt | 22.1% (155/700) | 22.5% (160/710) | self_repair.first_attempt_pass_rate |
| Repaired | 111 of 544 (20.4%) | 112 of 550 (20.4%) | self_repair.repaired / initially_failing |
| Regressions | 4 (0.7%) | 7 (1.0%) | self_repair.regression |
| Relative increase | 72% | 70.0% | (272-160)/160=0.70 |
| Cochran-Armitage | z=-0.77, p=0.44 | z=0.0, p=1.0 | augmentation.cochran_armitage |
| McNemar h range | 0.12-0.28 | See direction asymmetry data | direction_asymmetry |

### Section 1 - Contributions (lines 124-135)

| Claim | Current | Correct |
|-------|---------|---------|
| 700 primary tasks | 710 | file_counts.primary_campaign |
| 420 pass@k tasks | 426 | file_counts.passk_campaign |
| 33.9% BUILD_FAIL | 33.9% | (UNCHANGED at 1dp) |
| 7.3% VERIFY_FAIL | 7.2% | 51/710 |

### Section 5.2 - Augmentation Protocol (line 688)

| Claim | Current | Correct |
|-------|---------|---------|
| 96 L0 task pairs | 142 L0 task pairs | 710/5=142 |
| 480 tasks per model | 710 tasks per model | primary_campaign.total |

### Section 5.3 - Evaluation Corpus (line 555)

| Claim | Current | Correct |
|-------|---------|---------|
| 96 unique translation pairs at L0 | 142 unique translation pairs at L0 | 710/5=142 |

### Section 6 - Results intro (line 752)

| Claim | Current | Correct |
|-------|---------|---------|
| 906 total tasks | 1136 total (710+426) | file_counts |
| 480 primary campaign | 710 | primary_campaign.total |
| pending expand to 960 | Update to ~1420 (710*2) | Estimate |

### Section 6.1 - Overall Pass Rates (lines 754-782)

**Table tab:overall-pass (line 769):**

| Column | Current | Correct |
|--------|---------|---------|
| PASS | 174 | 272 |
| BUILD_FAIL | 148 | 241 |
| RUN_FAIL | 110 | 144 |
| VERIFY_FAIL | 47 | 51 |
| EXTR_FAIL | 1 | 1 |
| (new) ERROR | -- | 1 |
| Total | 480 | 710 |
| Rate | 36.2% | 38.3% |
| CI | [32.1%, 40.6%] | [34.8%, 41.9%] |

**Prose (lines 776-780):**

| Claim | Current | Correct |
|-------|---------|---------|
| 36.2% [32.1%, 40.6%] across 480 | 38.3% [34.8%, 41.9%] across 710 |
| BUILD_FAIL 30.8% (148/480) | 33.9% (241/710) |
| RUN_FAIL 22.9% (110/480) | 20.3% (144/710) |
| VERIFY_FAIL 9.8% (47/480) | 7.2% (51/710) |
| EXTRACTION_FAIL 0.2% (1/480) | 0.1% (1/710) + ERROR 0.1% (1/710) |
| 65.0% [54.1%, 74.6%] CUDA-to-OMP | 64.2% [55.3%, 72.2%] |
| 36.2% overall and 65.0% | 38.3% overall and 64.2% |

### Section 6.2 - Failure Taxonomy (lines 784-830)

**Failure distribution prose (line 787-788):**

| Claim | Current | Correct |
|-------|---------|---------|
| 306 total failures | 438 total failures | 710-272=438 |
| 148/306=48.4% BUILD_FAIL | 241/438=55.0% |
| 110/306=35.9% RUN_FAIL | 144/438=32.9% |
| 47/306=15.4% VERIFY_FAIL | 51/438=11.6% |
| 1/306=0.3% EXTRACTION_FAIL | 1/438=0.2% + 1/438 ERROR=0.2% |

**BUILD_FAIL subcategories (line 797-798):**

| Claim | Current | Correct |
|-------|---------|---------|
| 148/480=30.8% and 48.4% of failures | 241/710=33.9% and 55.0% of 438 failures |
| missing_header=55 (37.2% of 148) | missing_header=55 (22.8% of 241) |
| undeclared_identifier=47 (31.8%) | undeclared_identifier=56 (23.2%) |
| linker_error=30 (20.3%) | linker_error=49 (20.3%) |
| 132 of 148 | Top 3 sum: 55+56+49=160 of 241 |

**VERIFY_FAIL subcategories (line 800-801):**

| Claim | Current | Correct |
|-------|---------|---------|
| 47/480=9.8% and 15.4% of failures | 51/710=7.2% and 11.6% of 438 |
| wrong_numerical=42 (89.4%) | wrong_numerical=46 (90.2%) |
| missing_output=5 (10.6%) | missing_output=5 (9.8%) |
| 42+5=47 | 46+5=51 |

**RUN_FAIL subcategories (line 803-804):**

| Claim | Current | Correct |
|-------|---------|---------|
| 110/480=22.9% and 35.9% of failures | 144/710=20.3% and 32.9% of 438 |
| opencl_jit=50 (45.5% of 110) | opencl_jit=52 (36.1% of 144) |

**Self-repair transitions table (lines 812-827, tab:repair-transitions):**

| Row | Current | Correct |
|-----|---------|---------|
| BUILD_FAIL | 55/229=24.0% [18.9%, 30.0%] | 72/346=20.8% [16.9%, 25.4%] |
| RUN_FAIL | 14/114=12.3% [7.5%, 19.6%] | 17/148=11.5% [7.3%, 17.6%] |
| VERIFY_FAIL | 6/26=23.1% [11.0%, 42.1%] | 8/28=28.6% [15.2%, 47.1%] |
| EXTR_FAIL | 15/27=55.6% [37.3%, 72.4%] | 15/27=55.6% [37.3%, 72.4%] (UNCHANGED) |
| (new) UNKNOWN | -- | 0/1=0.0% |

**Prose after table (line 829-830):**

| Claim | Current | Correct |
|-------|---------|---------|
| 90 tasks total repaired | 112 tasks total |
| 17.5% first-attempt to 36.2% final | 22.5% to 38.3% |
| 5 regressions | 7 regressions |

### Section 6.3 - Per-Kernel (lines 832-890)

**Table tab:per-kernel (lines 840-868):**
Currently shows 18 Rodinia kernels only. Must expand to 31 kernels across 5 suites (all evaluable kernels with data in paper_data.json). Sorted by pass_rate descending:

| Suite | Kernel | Total | PASS | Rate | CI |
|-------|--------|-------|------|------|-----|
| HeCBench | stencil1d | 15 | 15 | 100.0% | [79.6%, 100.0%] |
| HeCBench | floydwarshall | 20 | 16 | 80.0% | [58.4%, 91.9%] |
| HeCBench | heat2d | 20 | 15 | 75.0% | [53.1%, 88.8%] |
| HeCBench | iso2dfd | 20 | 15 | 75.0% | [53.1%, 88.8%] |
| Rodinia | hotspot | 30 | 21 | 70.0% | [52.1%, 83.3%] |
| Rodinia | nn | 10 | 7 | 70.0% | [39.7%, 89.2%] |
| Rodinia | hotspot3d | 30 | 19 | 63.3% | [45.5%, 78.1%] |
| HeCBench | jacobi | 10 | 6 | 60.0% | [31.3%, 83.2%] |
| HeCBench | md | 10 | 6 | 60.0% | [31.3%, 83.2%] |
| HeCBench | nqueen | 10 | 6 | 60.0% | [31.3%, 83.2%] |
| HeCBench | page-rank | 10 | 6 | 60.0% | [31.3%, 83.2%] |
| Rodinia | particlefilter | 30 | 17 | 56.7% | [39.2%, 72.6%] |
| Rodinia | bfs | 30 | 16 | 53.3% | [36.1%, 69.8%] |
| Rodinia | cfd | 30 | 16 | 53.3% | [36.1%, 69.8%] |
| Rodinia | lud | 30 | 15 | 50.0% | [33.1%, 66.8%] |
| Rodinia | nw | 30 | 15 | 50.0% | [33.1%, 66.8%] |
| Rodinia | pathfinder | 30 | 15 | 50.0% | [33.1%, 66.8%] |
| Rodinia | backprop | 30 | 13 | 43.3% | [27.4%, 60.8%] |
| Rodinia | srad | 30 | 12 | 40.0% | [24.6%, 57.7%] |
| HeCBench | scan | 15 | 5 | 33.3% | [15.2%, 58.3%] |
| mixbench | mixbench | 30 | 8 | 26.7% | [14.2%, 44.5%] |
| Rodinia | bptree | 30 | 4 | 13.3% | [5.3%, 29.7%] |
| Rodinia | lavamd | 30 | 2 | 6.7% | [1.8%, 21.3%] |
| Rodinia | streamcluster | 30 | 2 | 6.7% | [1.8%, 21.3%] |
| HeCBench | convolution1d | 10 | 0 | 0.0% | [0.0%, 27.8%] |
| Rodinia | dwt2d | 10 | 0 | 0.0% | [0.0%, 27.8%] |
| Rodinia | gaussian | 10 | 0 | 0.0% | [0.0%, 27.8%] |
| Rodinia | heartwall | 30 | 0 | 0.0% | [0.0%, 11.3%] |
| Rodinia | myocyte | 30 | 0 | 0.0% | [0.0%, 11.3%] |
| RSBench | rsbench | 30 | 0 | 0.0% | [0.0%, 11.3%] |
| XSBench | xsbench | 30 | 0 | 0.0% | [0.0%, 11.3%] |

**Tier boundaries change:**

| Tier | Current (18 Rodinia) | Correct (31 all-suite) |
|------|---------------------|------------------------|
| Easy (>=50%) | 9 kernels | 17 kernels (stencil1d through pathfinder) |
| Medium (1-49%) | 5 kernels | 6 kernels (backprop through bptree) |
| Hard (0%) | 4 kernels | 8 kernels (convolution1d through xsbench) |

**Prose implications:** Tier descriptions need rewriting. HeCBench kernels dominate the top of the easy tier. XSBench and RSBench are 0% (hard tier) -- notable because XSBench demonstrates kernel-centric success in BASELINE verification but 0% LLM translation. The tier narrative changes significantly.

### Section 6.4 - Self-Repair (lines 892-924)

**Table tab:self-repair (lines 900-917):**

| Metric | Current | Correct |
|--------|---------|---------|
| Total tasks | 480 | 710 |
| First-attempt PASS | 84 (17.5%) | 160 (22.5%) |
| Repaired | 90 (18.8%) | 112 (15.8%) |
| Total PASS | 174 (36.2%) | 272 (38.3%) |
| Relative improvement | +107.1% | +70.0% |
| Persistent fail | 271 | 392 |
| Regression | 5 (1.0%) | 7 (1.0%) |

**Prose (lines 920-924):**

| Claim | Current | Correct |
|-------|---------|---------|
| "doubles" pass rate | FALSE -- 70% increase, not 107% | Rewrite to "70% relative increase" |
| 17.5% [14.4%, 21.2%] | 22.5% [19.6%, 25.8%] |
| 36.2% [32.1%, 40.6%] | 38.3% [34.8%, 41.9%] |
| 107.1% | 70.0% |
| 396 initially-failing | 550 |
| 90 repaired (22.7% [18.9%, 27.1%]) | 112 repaired (20.4% [17.2%, 23.9%]) |
| 5 regressions, 1.0% | 7 regressions, 1.0% (7/710) |
| "doubles" claim | MUST be rewritten: "raises...by 70%" |

### Section 6.5 - Augmentation Robustness (lines 926-963)

**Table tab:augmentation-rates (lines 935-951):**

| Cell | Current | Correct |
|------|---------|---------|
| Header: n=96 per level | n=142 per level | primary_campaign.by_level (142/level) |
| Header: n=16 C->OMP | n=24 C->OMP | augmentation.cuda_to_omp_balanced (24/level) |
| L0 all: 39.6% [30.4%, 49.6%] | 40.1% [32.4%, 48.4%] | by_level.L0 |
| L1 all: 34.4% [25.6%, 44.3%] | 37.3% [29.8%, 45.5%] | by_level.L1 |
| L2 all: 37.5% [28.5%, 47.5%] | 40.1% [32.4%, 48.4%] | by_level.L2 |
| L3 all: 38.5% [29.4%, 48.5%] | 39.4% [31.8%, 47.6%] | by_level.L3 |
| L4 all: 31.3% [22.9%, 41.1%] | 34.5% [27.2%, 42.6%] | by_level.L4 |
| L0 C->OMP: 68.8% [44.4%, 85.8%] | 66.7% [46.7%, 82.0%] | cuda_to_omp_balanced.L0 |
| L1 C->OMP: 62.5% [38.6%, 81.5%] | 58.3% [38.8%, 75.5%] | cuda_to_omp_balanced.L1 |
| L2 C->OMP: 68.8% [44.4%, 85.8%] | 70.8% [50.8%, 85.1%] | cuda_to_omp_balanced.L2 |
| L3 C->OMP: 56.3% [33.2%, 76.9%] | 58.3% [38.8%, 75.5%] | cuda_to_omp_balanced.L3 |
| L4 C->OMP: 68.8% [44.4%, 85.8%] | 66.7% [46.7%, 82.0%] | cuda_to_omp_balanced.L4 |

**Prose (line 960-963):**

| Claim | Current | Correct |
|-------|---------|---------|
| n=16 kernels per level | n=24 kernels per level |
| z=-0.17, p=0.87 | z=0.0, p=1.0 |
| pass counts [11,10,11,9,11] | pass counts [16,14,17,14,16] |

### Section 6.6 - Direction Analysis (lines 965-1004)

**Table tab:direction-rates (lines 970-991):**

| Direction | Current L0 | Correct L0 | Current all-level | Correct all-level | N(L0) old | N(L0) new |
|-----------|-----------|------------|-------------------|-------------------|-----------|-----------|
| cuda-to-omp | 68.8% (11/16) | 66.7% (16/24) | 65.0% (52/80) [54.1%, 74.6%] | 64.2% (77/120) [55.3%, 72.2%] | 16 | 24 |
| omp-to-cuda | 56.2% (9/16) | 58.3% (14/24) | 50.0% (40/80) [39.3%, 60.7%] | 52.5% (63/120) [43.6%, 61.2%] | 16 | 24 |
| opencl-to-omp | 46.7% (7/15) | 38.9% (7/18) | 46.7% (35/75) [35.8%, 57.8%] | 38.9% (35/90) [29.5%, 49.2%] | 15 | 18 |
| omp-to-opencl | 33.3% (5/15) | 33.3% (6/18) | 29.3% (22/75) [20.2%, 40.4%] | 27.8% (25/90) [19.6%, 37.8%] | 15 | 18 |
| cuda-to-opencl | 23.5% (4/17) | 20.0% (4/20) | 22.4% (19/85) [14.8%, 32.3%] | 20.0% (20/100) [13.3%, 28.9%] | 17 | 20 |
| opencl-to-cuda | 11.8% (2/17) | 10.0% (2/20) | 7.1% (6/85) [3.3%, 14.6%] | 6.0% (6/100) [2.8%, 12.5%] | 17 | 20 |

**Direction asymmetry prose (lines 993-998):**

| Claim | Current | Correct |
|-------|---------|---------|
| 65.0%-50.0%=15.0pp gap | 64.2%-52.5%=11.7pp gap |
| Task sum 80+80+75+75+85+85=480 | 120+120+90+90+100+100=620 (std only) + 40+50=90 (case study) = 710 |

**McNemar tests (line 997-998):**

| Test | Current | Correct |
|------|---------|---------|
| CUDA-OMP | n=16, p=0.625, h=0.26 | n=24, p=0.6875, h=-0.17 |
| CUDA-OpenCL | n=17, p=0.688, h=0.31 | n=20, p=0.6875, h=0.28 |
| OMP-OpenCL | n=15, p=0.727, h=0.27 | n=18, p=1.0, h=0.12 |

**OpenCL direction prose (lines 1002-1004):**

| Claim | Current | Correct |
|-------|---------|---------|
| cuda-to-opencl 22.4% | 20.0% |
| opencl-to-cuda 7.1% | 6.0% |
| BUILD_FAIL 66/85=77.6% | opencl-to-cuda BUILD_FAIL 81/100=81.0% |
| 15.3pp asymmetry | 14.0pp asymmetry |

### Section 6.7 - pass@k (lines 1006-1045)

pass@k campaign data is UNCHANGED (426 tasks, 142 pairs, 19.7% macro pass@1, 27.5% macro pass@3). The only change is the cross-reference to the primary campaign greedy pass@1:

| Claim | Current | Correct |
|-------|---------|---------|
| greedy pass@1=36.2% (primary) | 38.3% | primary_campaign.overall.pass_rate |

### Section 6.8 - Statistical Summary (lines 1047-1074)

**Table tab:stats-summary:**

| Row | Current | Correct |
|-----|---------|---------|
| Cochran-Armitage | z=-0.17, p=0.87 | z=0.0, p=1.0 |
| McNemar cuda-omp | n=16, p=0.625, h=0.26 | n=24, p=0.6875, h=-0.17 |
| McNemar cuda-opencl | n=17, p=0.688, h=0.31 | n=20, p=0.6875, h=0.28 |
| McNemar omp-opencl | n=15, p=0.727, h=0.27 | n=18, p=1.0, h=0.12 |

**Bonferroni note:** Correction is 0.05/4=0.0125 (4 tests including omp_target). This is UNCHANGED.

### Section 7 - Discussion (lines 1079-1183)

Every number in Section 7 is a repetition of a Section 6 number. After updating S6, S7 must be updated to match.

| Section | Claim | Current | Correct |
|---------|-------|---------|---------|
| 7.1 | CUDA-to-OMP | 65.0% [54.1%, 74.6%] | 64.2% [55.3%, 72.2%] |
| 7.2 | BUILD_FAIL of failures | 148/306=48.4% | 241/438=55.0% |
| 7.2 | 480 tasks | 710 tasks |
| 7.2 | VERIFY_FAIL of failures | 47/306=15.4% | 51/438=11.6% |
| 7.3 | Overall | 36.2% [32.1%, 40.6%] across 480 | 38.3% [34.8%, 41.9%] across 710 |
| 7.3 | CUDA-to-OMP | 65.0% | 64.2% |
| 7.3 | pass@1 floor | 19.7% | 19.7% (UNCHANGED) |
| 7.3 | self-repair | 36.2% | 38.3% |
| 7.4 | Direction gaps | 65.0%-7.1%=57.9pp | 64.2%-6.0%=58.2pp |
| 7.4 | 15.0pp CUDA/OMP | 11.7pp |
| 7.4 | 17.3pp OMP/OpenCL | 11.1pp (38.9%-27.8%) |
| 7.4 | 15.3pp CUDA/OpenCL | 14.0pp (20.0%-6.0%) |
| 7.5 | z=-0.17, p=0.87 | z=0.0, p=1.0 |
| 7.5 | L0-L4 rates | 68.8%/62.5%/68.8%/56.3%/68.8% | 66.7%/58.3%/70.8%/58.3%/66.7% |
| 7.5 | 72.5% hard failures | 72.5% (UNCHANGED, pass@k scope) |
| 7.7 | 65.0% | 64.2% |
| 7.7 | 148/480=30.8% | 241/710=33.9% |
| 7.7 | 148/306=48.4% | 241/438=55.0% |

### Section 8 - Conclusion (lines 1187-1212)

| Claim | Current | Correct |
|-------|---------|---------|
| 480 primary campaign tasks | 710 |
| 426 pass@k tasks | 426 (UNCHANGED) |
| 36.2% [32.1%, 40.6%] | 38.3% [34.8%, 41.9%] |
| 65.0% [54.1%, 74.6%] | 64.2% [55.3%, 72.2%] |
| 48.4% of failures | 55.0% |
| 15.4% VERIFY_FAIL of failures | 11.6% |
| z=-0.17, p=0.87 | z=0.0, p=1.0 |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Verification of updated values | Manual re-reading | Python script to extract all numbers from paper.tex and cross-check against paper_data.json | 150+ numbers to verify; manual checking is error-prone |
| Consistency across sections | Section-by-section review | Grep-based audit for known stale values (480, 36.2%, 65.0%, etc.) after update | Same number appears 3-5 times across sections |

## Common Pitfalls

### Pitfall 1: Inconsistent Scope Across Sections
**What goes wrong:** Updating Section 6 but leaving Section 7 or the Abstract with old numbers.
**Why it happens:** The same number (e.g., 65.0% CUDA-to-OMP) appears in Abstract, S1, S6.1, S6.6, S7.1, S7.3, S7.4, S7.7, S8. Missing one creates an internal contradiction.
**How to avoid:** After all updates, grep for every instance of each stale value (480, 36.2%, 65.0%, 148, 306, etc.) to confirm no orphans remain.
**Warning signs:** Any instance of "480" (except in provenance comments about the old scope) or "36.2%" remaining after the update.

### Pitfall 2: Cochran-Armitage Source Confusion
**What goes wrong:** Using the wrong Cochran-Armitage test result.
**Why it happens:** Three different values exist: (1) quantitative_findings.json all-direction aggregate z=-0.77, p=0.44, n=140/level; (2) paper_data.json CUDA-to-OMP balanced z=0.0, p=1.0, n=24/level; (3) old Rodinia-only z=-0.17, p=0.87, n=16/level.
**How to avoid:** CONTEXT.md D-01 says paper_data.json is ground truth. Use z=0.0, p=1.0 for the primary analysis. If the all-direction aggregate is also desired, it must be computed from paper_data.json (not quantitative_findings.json).
**Warning signs:** Mismatched n values between Cochran-Armitage and the augmentation table.

### Pitfall 3: Self-Repair "Doubles" Language
**What goes wrong:** Leaving the word "doubles" in the self-repair section when the relative improvement is now 70%, not 107%.
**Why it happens:** With 480-task scope, first-attempt was 17.5% and final was 36.2% (107% increase, roughly "doubles"). With 710-task scope, first-attempt is 22.5% and final is 38.3% (70% increase).
**How to avoid:** Search for "double" in the self-repair section and rewrite to "70% relative increase."
**Warning signs:** Any instance of "double" or "107" in the self-repair text.

### Pitfall 4: Per-Kernel Table Expansion
**What goes wrong:** Only updating existing 18-row table cells without expanding to 31 rows.
**Why it happens:** The table must grow from 18 Rodinia kernels to 31 kernels across 5 suites (adding 13 HeCBench, XSBench, RSBench, mixbench kernels). This is a structural change, not just a number update.
**How to avoid:** Rebuild the entire table from paper_data.json by_kernel data. Include suite column.
**Warning signs:** Table caption still says "18 Rodinia kernels" or "480 primary campaign tasks."

### Pitfall 5: Direction Ranking Order Changes
**What goes wrong:** Prose says "OpenCL-to-CUDA achieves 10.0%" but correct value is 6.0%.
**Why it happens:** Direction pass rates change with the expanded scope. While ranking ORDER is preserved (cuda-to-omp is still highest, opencl-to-cuda still lowest), the gaps change.
**How to avoid:** Re-derive all direction gap claims from the updated direction rates table.
**Warning signs:** Any "10.0%" reference to opencl-to-cuda.

### Pitfall 6: ERROR Status Not Handled
**What goes wrong:** Table sums don't add up because 1 ERROR task is not accounted for.
**Why it happens:** paper_data.json has a new ERROR status (1 task) that didn't exist in the Rodinia-only scope. The tab:overall-pass table needs an ERROR column or it must be merged with EXTRACTION_FAIL.
**How to avoid:** Add ERROR column to tab:overall-pass, or note in text that 1 ERROR task exists and is grouped with EXTRACTION_FAIL for analysis.
**Warning signs:** Row sum of 709 instead of 710.

### Pitfall 7: Provenance Comments Left Stale
**What goes wrong:** Numbers updated in prose but provenance comments still say "paper_data.json: 480 tasks" or "174/480=36.2%".
**Why it happens:** Comments are easy to overlook when editing prose.
**How to avoid:** Update every `% src:` comment to match the new values. Every updated number must have a matching updated comment.
**Warning signs:** Provenance comment values disagreeing with adjacent prose values.

## Code Examples

### Provenance Comment Pattern (correct format)
```latex
% src: paper_data.json > primary_campaign > overall: pass=272, total=710, rate=0.3831, CI=[0.3481, 0.4194]
Qwen~3.5 397B-A17B achieves an overall pass rate of 38.3\% [34.8\%, 41.9\%] across 710 translation tasks
```

### Table Cell Pattern
```latex
Qwen 3.5 397B-A17B & 272 & 241 & 144 & 51 & 1 & 1 & 710 & 38.3\% & [34.8\%, 41.9\%] \\
% src: row sum 272+241+144+51+1+1=710; 272/710=38.3%; CI [0.3481,0.4194]
```

### Verification Grep After Update
```bash
# Check for any remaining stale 480 references (excluding comments about old scope)
grep -n "480" docs/paper/latex/paper.tex | grep -v "^[0-9]*:%"

# Check for stale Rodinia-only rates
grep -n "36\.2\%" docs/paper/latex/paper.tex
grep -n "65\.0\%" docs/paper/latex/paper.tex
grep -n "17\.5\%" docs/paper/latex/paper.tex
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Rodinia-only 480-task scope | All-suite 710-task scope | Phase 12 | Every numerical claim changes |
| quantitative_findings.json (700 tasks) | paper_data.json (710 tasks) | Phase 12 | Abstract/Intro numbers change |
| Cochran-Armitage z=-0.17 (16 kernels) | z=0.0, p=1.0 (24 kernels) | Phase 12 | STRONGER null result |
| Self-repair "doubles" (107%) | 70% relative increase | Phase 12 | Narrative rewrite needed |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The ERROR status (1 task) should be handled by adding a column to tab:overall-pass rather than merging with EXTRACTION_FAIL | S6.1 table | Table formatting issue only; easily reversible |
| A2 | The Cochran-Armitage value to use is from paper_data.json (z=0.0, p=1.0, n=24) not from quantitative_findings.json (z=-0.77, p=0.44, n=140) | S6.5, S6.8, S7.5, Abstract | Using the wrong test invalidates the augmentation robustness claim; D-01 resolves this |
| A3 | Per-kernel table should include all 31 evaluable kernels, not just 18 Rodinia | S6.3 | Table size may exceed page limit; but D-02 requires all-suite presentation |
| A4 | Direction analysis table should show all 8 directions (6 standard + 2 case study) as currently structured | S6.6 | Table already has case study rows; structure is preserved |

## Open Questions

1. **Cochran-Armitage: balanced-subset vs all-direction?**
   - What we know: paper_data.json provides the balanced CUDA-to-OMP test (z=0.0, p=1.0, n=24). quantitative_findings.json provides the all-direction aggregate (z=-0.77, p=0.44, n=140).
   - What's unclear: Should the paper present the balanced CUDA-to-OMP test only (as currently structured with the table showing balanced subset), or also the all-direction aggregate?
   - Recommendation: Use paper_data.json per D-01. Present z=0.0, p=1.0 as the primary augmentation result. If the all-direction aggregate is desired, note it as a secondary finding. The z=0.0 result is STRONGER evidence for the null hypothesis.

2. **Per-kernel table formatting**
   - What we know: Table must expand from 18 to 31 rows. IEEE double-column format has strict space constraints.
   - What's unclear: Whether 31 rows fit in one table, or whether it needs to be split/summarized.
   - Recommendation: Keep the full table (it's the same format, just more rows). If space is tight, consider moving to an appendix or reducing to top/bottom-5 with a "full table in appendix" note.

3. **ERROR status handling**
   - What we know: 1 task has ERROR status. This is new (didn't exist in Rodinia-only scope).
   - What's unclear: Root cause of the ERROR (likely a pipeline/infrastructure error, not a model failure).
   - Recommendation: Add ERROR column to tab:overall-pass. In prose, note "1 ERROR (infrastructure failure, excluded from failure taxonomy)" or group with EXTRACTION_FAIL.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual grep + Python verification script |
| Config file | none -- ad-hoc verification |
| Quick run command | `grep -n "480\|36\.2\%\|65\.0\%\|17\.5\%" docs/paper/latex/paper.tex` |
| Full suite command | Python script comparing all numbers in paper.tex against paper_data.json |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VERIFY-01 | All numerical claims match ground truth | manual + grep | `grep -cP '(480\|36\.2\%\|65\.0\%)' docs/paper/latex/paper.tex` should return 0 | N/A |
| VERIFY-01 | Provenance comments updated | manual | `grep -n 'src:.*480\|src:.*174/480' docs/paper/latex/paper.tex` should return 0 | N/A |
| VERIFY-01 | Cross-section consistency | manual | Compare Abstract numbers against S6 against S7 against S8 | N/A |

### Sampling Rate
- **Per task commit:** Grep for stale values
- **Per wave merge:** Full section-by-section read-through
- **Phase gate:** Zero instances of stale values remaining

### Wave 0 Gaps
- None -- no test infrastructure needed for a LaTeX text-editing phase

## Security Domain

Security enforcement is not applicable to this phase (pure text editing of a LaTeX paper).

## Sources

### Primary (HIGH confidence)
- `results/analysis/paper_data.json` -- All numerical values verified by direct Python extraction [VERIFIED: read + parsed in this session]
- `docs/paper/latex/paper.tex` -- All current values verified by direct file reading [VERIFIED: read in this session]
- `results/analysis/quantitative_findings.json` -- Cross-referenced for scope differences [VERIFIED: read + parsed in this session]

### Secondary (MEDIUM confidence)
- `.planning/phases/12-fix-stale-passk-values/12-CONTEXT.md` -- User decisions constraining scope [VERIFIED: read in this session]

## Metadata

**Confidence breakdown:**
- Discrepancy map: HIGH -- every old and new value verified by reading source files directly
- Architecture: HIGH -- single file edit against single ground truth file
- Pitfalls: HIGH -- based on direct observation of actual inconsistencies in paper.tex

**Research date:** 2026-04-05
**Valid until:** 2026-04-08 (paper submission deadline)
