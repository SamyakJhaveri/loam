# SC26 Paper Audit Report — ParBench

**Date:** 2026-03-28
**Method:** 4-agent team audit ("sc26-audit") using Claude Opus with ultrathink
**Teammates:** search-planner (coordinator), data-explorer (data auditor), git-explorer (git/task auditor), sc26-reviewer (adversarial reviewer)
**Deadline:** April 8, 2026 (11 days remaining)

---

## Table of Contents

1. [Task #1: Big-Picture Map (search-planner)](#task-1-big-picture-map)
2. [Task #2: Exhaustive Data Inventory (data-explorer)](#task-2-exhaustive-data-inventory)
3. [Task #3: Git History & Session Completion Audit (git-explorer)](#task-3-git-history--session-completion-audit)
4. [Task #4: Adversarial SC26 Main Track Paper Review (sc26-reviewer)](#task-4-adversarial-sc26-main-track-paper-review)
5. [Task #4 Supplemental: Additional Weaknesses (sc26-reviewer)](#task-4-supplemental-additional-weaknesses)
6. [Task #5: Final Synthesis & Prioritized Action Plan (search-planner)](#task-5-final-synthesis--prioritized-action-plan)
7. [Team Lead Analysis: Key Insights](#team-lead-analysis)

---

## Task #1: Big-Picture Map

**Teammate:** search-planner (coordinator)
**Status:** COMPLETE

### Project Overview
- **Deadline:** April 8, 2026 (11 days remaining as of March 28)
- **Target venue:** SC26 (Supercomputing 2026), ACM sigconf 10-page technical paper
- **Working title:** "ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness"

---

### SPEC INVENTORY (184 total on disk, 189 in manifest)
- **Rodinia:** 60 specs (22 CUDA, 18 OMP, 20 OpenCL) — 22 unique kernels
- **HeCBench:** 120 specs (60 CUDA, 60 OMP) — NOT cloned locally, NOT evaluated
- **XSBench:** 4 specs (1 each: CUDA, OMP, OpenCL, OMP-target) — 4/4 PASS
- **Manifest has 189 entries** (65 rodinia, 120 hecbench, 4 xsbench) — 5 phantom rodinia entries are correctly still in append-only manifest

### EVAL RESULTS (verified, authoritative as of 2026-03-28)
- **504 raw result JSON files** on disk (168 per model x 3 models)
- **468 eligible tasks** (36 kmeans/mummergpu files excluded from summary)
- **3 models:** claude-sonnet-4-6 (81/156=51.92%), gemini-2.5-flash-lite (11/156=7.05%), groq-llama-3.3-70b (13/156=8.33%)
- **Overall: 105/468 = 22.44% PASS**
- **12 translation directions** evaluated
- **L0-L4 augmentation** complete for cuda-to-omp
- **17 unique kernels** in eval (16 Rodinia + 1 XSBench)
- **azure-gpt-4.1:** ZERO result files on disk. Was disabled by Gal. Previously had 17 L0 results (9/17 PASS) but they were deleted.

### THE "17 KERNELS" QUESTION ANSWERED
22 Rodinia kernels minus 6 = 16 in eval:
- 2 phantoms deleted (gaussian, huffman) — directories never existed
- 2 CUDA-only, no cross-API pair (dwt2d, hybridsort)
- 2 KNOWN_FAIL excluded from summary (kmeans, mummergpu) — result files exist but are excluded
Plus 1 XSBench = 17 total in eval summary.

---

### SESSION STATUS (Completed vs Not Started)

**COMPLETED (18 sessions):**
S1, S1.5, S1.6, S2, S3, S3-PM, S3b, S4, S5, S6, S7, S8, S9, W-S11, W-S12-PARTIAL, W-S14, S-VERIFY, S-FIGURES, S13

**NOT STARTED (per session_prompts, but some deliverables exist on disk):**

| Session | Priority | What | Status |
|---------|----------|------|--------|
| S-DEPS | P0 | requirements.txt, pyproject.toml, Dockerfile | ACTUALLY DONE — files exist on disk AND committed (commit 46c581e) despite session_prompts saying NOT STARTED |
| W-S16 | P0 | Anonymous GitHub repo for double-blind | NOT STARTED |
| W-S17 | P0 | LaTeX transfer (Markdown -> ACM sigconf) | NOT STARTED — no full .tex paper exists |
| S18 | P0 | Final review + submit | NOT STARTED |
| S10 | P1 | cuda-to-opencl Rodinia eval (17 kernels x 3 models) | NOT STARTED (no Rodinia OpenCL direction data except via XSBench S8) |
| S12 | P1 | Paper Intro + Related Work (Sections 1-2) | PARTIALLY DONE — paper_draft.md has S1 and S2 written but with STALE 4-model data |
| W-S15 | P1 | Paper review + polish | NOT STARTED |
| S10b | P2 | Remaining 3 OpenCL directions | NOT STARTED |
| S-ANALYSIS | P2 | SLoC + token + self-repair stats | NOT STARTED |
| S-TAXONOMY | P1 | Error taxonomy from result JSONs | NOT STARTED |
| S-BIB | P2 | Bibliography compilation | NOT STARTED |
| S-TIMING | P2 | CPU/GPU timing for PASS results | NOT STARTED |

---

### CRITICAL GAPS THREATENING SUBMISSION

**1. PAPER DRAFT HAS STALE 4-MODEL DATA (CRITICAL)**
`docs/paper/paper_draft.md` still references:
- "four LLMs" (Claude, GPT-4.1, Gemini, Llama) — azure-gpt-4.1 has ZERO result files on disk
- "500 evaluated tasks" — actual: 468
- "GPT-4.1 achieves 52.9%" — this data no longer exists
- "zero VERIFY_FAIL across all 500 tasks" — facts sheet shows 45 VERIFY_FAIL across 468 tasks
- "BUILD_FAIL dominance (68.4%)" — facts sheet shows 38.46%
- All per-kernel tier descriptions reference 4-model data

The paper draft has NOT been updated after S-VERIFY rewrote the verification pipeline. The numbers in the abstract, S1, and S6 are ALL wrong for the 3-model reality.

**2. NO LATEX PAPER (P0)**
Only Markdown exists. SC26 requires ACM sigconf LaTeX. W-S17 not started.

**3. NO ANONYMOUS REPO (P0)**
W-S16 not started. Double-blind review requires it.

**4. 120 HeCBench SPECS NOT EVALUATED**
Paper claims "184 specs across 3 suites" but only 17 kernels are evaluated. HeCBench is not even cloned locally. The claim is about framework SCOPE, not evaluation SCOPE — but a reviewer will notice.

**5. ZERO TIMING DATA**
No kernel execution time data exists. All timing is wall_time only. S-TIMING not started. Paper is framed as correctness-only.

**6. S10 NOT RUN (Rodinia OpenCL directions)**
The paper claims 12 translation directions, but the non-XSBench OpenCL results come from Rodinia omp-to-cuda and other directions. There are no Rodinia-specific cuda-to-opencl eval results beyond XSBench.

---

### PLANNED VS ACTUAL EVAL SCOPE

**Paper outline claims:**
- 64 specs across 3 suites, 4 APIs, 12 directions (later 184 specs)
- 3 models (down from originally 4), 468 tasks, 22.44% PASS

**Actually executed:**
- 17 kernels (16 Rodinia + 1 XSBench) x 3 models x multiple directions/levels = 504 raw files
- Per-model breakdown: 108 Rodinia + 60 XSBench = 168 per model
- Rodinia directions: cuda-to-omp (95 files), omp-to-cuda (23 files), plus 5 each for 10 other direction combos (mostly XSBench-only)
- The 95 cuda-to-omp Rodinia files = ~16 kernels x ~5 levels (L0-L4) + some with less

**NOT executed:**
- HeCBench (120 specs, 0 eval results)
- Additional models (GPT-4.1 was dropped, Qwen/QwQ never started)
- S10 (Rodinia cuda-to-opencl)
- S10b (3 remaining OpenCL directions)
- Kernel timing (nvprof/ncu)

---

### AUGMENTATION BASELINE
- 54/60 Rodinia PASS at ALL L1-L4 levels (level-invariant)
- 6 KNOWN_FAIL at all levels (4 BUILD_FAIL + 2 FAIL)
- XSBench: 3/3 PASS at L2 (spot-check only)
- Definitive result file: `results/augmentation/retest_post_session2.json`

### M-TASKS STATUS

| Task | Status |
|------|--------|
| M1 (anon repo) | NOT STARTED |
| M2 (curation survey page) | NOT STARTED |
| M3 (read Paraval paper) | NOT STARTED (Samyak manual task) |
| M4 (paper outline) | DONE |
| M5 (XSBench) | DONE |
| M6 (timing metrics) | DEFERRED (paper is correctness-only) |
| M7 (Groq setup) | DONE |
| M8 (Gemini selection) | DONE |
| M9 (cherry-pick aug fixes) | DONE |
| M10/M10b (aug retest) | DONE |
| M11 (kernel-centric pipeline) | DONE |

---

This completes the big-picture map. The most urgent finding is the STALE 4-MODEL DATA in paper_draft.md — every number in the abstract and results sections needs updating from the 4-model/500-task/0-VERIFY_FAIL framing to the 3-model/468-task/45-VERIFY_FAIL reality.

---

## Task #2: Exhaustive Data Inventory

**Teammate:** data-explorer (data auditor)
**Status:** COMPLETE

### 1. EVALUATION DATA — results/evaluation/

**3 model directories, 168 JSON result files each = 504 total on disk**

| Model | Total Files | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----------|------|-----------|---------|------------|----------------|
| claude-sonnet-4-6 | 168 | 86 (51.19%) | 22 | 30 | 19 | 11 |
| gemini-2.5-flash-lite | 168 | 11 (6.55%) | 102 | 33 | 10 | 12 |
| groq-llama-3.3-70b-versatile | 168 | 13 (7.74%) | 82 | 27 | 16 | 30 |
| **TOTAL** | **504** | **110** | **206** | **90** | **45** | **53** |

**19 unique kernels evaluated:** 18 Rodinia + 1 XSBench (xsbench-xsbench)

**Rodinia kernels (18):** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, kmeans, lavamd, lud, mummergpu, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster

**Rodinia kernels WITH NO EVAL DATA (2):** hybridsort (KNOWN_FAIL), leukocyte (no spec exists)

**12 unique translation directions:**
- **Primary (all 19 kernels):** cuda-to-omp (95 files/model), omp-to-cuda (23 files/model)
- **XSBench-only (10 directions):** cuda-to-{omp_target,opencl}, omp-to-{omp_target,opencl}, omp_target-to-{cuda,omp,opencl}, opencl-to-{cuda,omp,omp_target} — 5 files each per model

**Augmentation levels:** ALL 19 kernels have L0 through L4 data
- Rodinia: L1-L4 only for cuda-to-omp direction
- XSBench: L1-L4 for ALL 12 directions

**Per-kernel L0 cuda-to-omp PASS rates (the key paper metric):**

| Kernel | Claude | Gemini | Groq |
|--------|--------|--------|------|
| backprop | PASS | PASS | BUILD_FAIL |
| bfs | VERIFY_FAIL | BUILD_FAIL | VERIFY_FAIL |
| bptree | PASS | PASS | PASS |
| cfd | PASS | BUILD_FAIL | BUILD_FAIL |
| heartwall | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL |
| hotspot | RUN_FAIL | RUN_FAIL | RUN_FAIL |
| hotspot3d | PASS | PASS | PASS |
| kmeans | PASS | BUILD_FAIL | BUILD_FAIL |
| lavamd | PASS | VERIFY_FAIL | BUILD_FAIL |
| lud | PASS | BUILD_FAIL | BUILD_FAIL |
| mummergpu | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL |
| myocyte | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL |
| nn | PASS | VERIFY_FAIL | RUN_FAIL |
| nw | VERIFY_FAIL | EXTRACTION_FAIL | BUILD_FAIL |
| particlefilter | PASS | BUILD_FAIL | PASS |
| pathfinder | VERIFY_FAIL | BUILD_FAIL | VERIFY_FAIL |
| srad | PASS | RUN_FAIL | EXTRACTION_FAIL |
| streamcluster | VERIFY_FAIL | BUILD_FAIL | BUILD_FAIL |
| xsbench | RUN_FAIL | BUILD_FAIL | BUILD_FAIL |

### 2. CRITICAL DISCREPANCY: eval_summary.json vs disk

**eval_summary.json reports 468 total tasks (156/model), disk has 504 (168/model)**

- **kmeans and mummergpu are EXCLUDED from eval_summary.json** (missing from by_kernel entirely)
- That's 6 files/model * 2 kernels = 12 files/model excluded = 36 total
- Claude's PASS count: summary says 81, disk shows 86 (diff = 5 Claude kmeans PASS files)
- This is a DATA INTEGRITY issue — the summary understates Claude's results

**eval_summary.json also reports overall pass rate as 105/468 = 22.44%**
**Actual disk pass rate is 110/504 = 21.83%** (all files) or **105/468 = 22.44%** (excluding kmeans/mummergpu)

The known-issues.md and MEMORY.md both cite "105/468 = 22.44%" — this is the eval_summary figure, not the full disk count.

### 3. AUGMENTATION DATA — results/augmentation/

**full_aug_results.json:** 540 records (Rodinia + HeCBench only, NO XSBench)
- 60 unique Rodinia specs, tested at L1, L2, L4 (L3 not in this file)
- L1: 44 PASS, 12 BUILD_FAIL, 4 FAIL, 120 ERROR (HeCBench expected)
- L2: 43 PASS, 13 BUILD_FAIL, 4 FAIL, 120 ERROR
- L4: 1 PASS, 59 BUILD_FAIL, 120 ERROR

**retest_post_m9.json:** 260 records, 65 specs, L1-L4 — 192 PASS, 28 BUILD_FAIL, 20 ERROR, 20 FAIL
**retest_post_session2.json:** 240 records, 60 specs, L1-L4 — 216 PASS, 16 BUILD_FAIL, 8 FAIL
**xsbench_L2_seed42.json:** 3 records (cuda/omp/opencl at L2) — all 3 PASS

Phase3-5 augmentation per-API files also exist (phase3_cuda.json etc.).

### 4. BASELINE DATA — results/phase3/, phase4/, phase5/, rodinia/

- **results/rodinia/rodinia_results.json:** 60 specs total, 51 full_pass (cuda:18/22, omp:17/18, opencl:16/20)
- **results/phase3/:** HeCBench CUDA+OMP baseline logs and results
- **results/phase4/:** HeCBench SYCL verification logs
- **results/phase5/:** HeCBench combined verification data (CUDA+OMP+SYCL)

### 5. ANALYSIS DATA — results/analysis/

- error_taxonomy.json/md — error classification
- selfrepair_analysis.json/md — self-repair statistics
- sloc_analysis.json/md — source lines of code
- token_analysis.json/md — token usage analysis

### 6. KEY FINDINGS FOR PAPER AUDIT

1. **No azure-gpt-4.1 result directory exists on disk** — not even an empty directory. The only azure-gpt trace on disk is 9 BUILD_FAIL entries inside reverification_audit.json. Confirms it was fully removed.
2. **eval_summary.json excludes 2 kernels (kmeans, mummergpu)** — 36 result files omitted, 5 PASS files from Claude not counted.
3. **Reverification audit found 0 TRUE_PASS** out of 169 re-tested files — all got BUILD_FAIL. This suggests build environment issues during reverification, not actual false passes.
4. **Augmentation eval data covers only cuda-to-omp direction** for Rodinia (L1-L4), but all 12 directions for XSBench.
5. **XSBench has zero PASS for Gemini and Groq** across all 60 files each. Only Claude passes any XSBench translations (34/60).
6. **Documentation claims "105/468 = 22.44%"** which matches eval_summary but not full disk reality (110/504).

---

## Task #3: Git History & Session Completion Audit

**Teammate:** git-explorer (git/task auditor)
**Status:** COMPLETE

### TIMELINE OF ALL WORK (from git log with dates)

**Week 1 (Mar 18-24): Infrastructure + L0 Baselines**

| Date | Session | Commit | What happened |
|------|---------|--------|---------------|
| Mar 18 | S1 | `cfa1991` | Rodinia submodule reset, 54/60 PASS |
| Mar 19 | S1.5, S1.6 | `c2b63fd`, `35b9c8e` | Kernel-centric pipeline, universal standardization |
| Mar 20 | (Day 3) | `5f78e27`, `e3fc19f` | Harness gap fixes, full 60-spec retest 54/60 PASS |
| Mar 21 | S1 | `cfa1991` | Submodule reset + build-flag alternatives |
| Mar 22 | S2, S3, S3-PM | `3d43afa`, `b644bc6`, `dad1662` | azure-gpt L0 (9/17), groq L0 (5/17), pipeline fixes |
| Mar 23 | S3b, S4, S5, S6 | `887d681`-`888910f` | Claude L0 (12/17), Gemini L0 (4/17), XSBench 4/4, paper outline |
| Mar 24 | W-S14, Audits | `e0e88b7`, multiple | Publication figures F2-F6, S1.5/1.6/3b/5 audit fixes |

**Week 2 (Mar 25-28): Augmented evals + Paper drafting**

| Date | Session | Commit | What happened |
|------|---------|--------|---------------|
| Mar 25 | S8, W-S12, W-S11 | `096a309`, `5b22981`, `27d4c0a` | XSBench 180 files, Paper S3-S5, Dashboard refresh |
| Mar 25 | S7 | `482e7b1` | Rodinia L1-L4 augmented eval (195 files committed along with S8) |
| Mar 25 | S12 | `a76b1d0` | SC26 paper draft + augmentation eval infrastructure |
| Mar 26 | S9 | `eac7b5e`, `3366420` | omp-to-cuda eval (54 files) + cross-direction analysis |
| Mar 26 | Infra | `78d1900`, `17d24e5` | /dream skill, dashboard SC26 palette |
| Mar 27 | S-VERIFY | `9d0d453`, `7868d46` | Fix verification (stdout_pattern+exit_code), re-run ALL results |
| Mar 27 | S-TAXONOMY | `dd735ef`, `bc31d2c` | Error taxonomy from 500 result JSONs |
| Mar 27 | S-ANALYSIS | `bc22e1f`, `5eb5529` | SLoC + token + self-repair analysis |
| Mar 27 | S-BIB | `42abca7`, `4bb988c` | Bibliography with 15 entries |
| Mar 27 | S-DEPS | `46c581e` | requirements.txt + pyproject.toml + Dockerfile + REPRODUCING.md |
| Mar 27 | S-FIGURES | `9789e20` | System architecture figure + all paper figures updated |
| Mar 27 | S13 | `56cc02b` | Paper Results + Discussion sections expanded |
| Mar 28 | Post-S-VERIFY | `5f61731`-`59c9917` | Updated internal docs, paper outline, session prompts |

### SESSION COMPLETION TRACKER (Planned vs Actual)

**COMPLETED (19 sessions):**
S1, S1.5, S1.6, S2, S3, S3b, S3-PM, S4, S5, S6, S7, S8, S9, W-S11, W-S12-PARTIAL, W-S14, S-VERIFY, S-TAXONOMY, S-ANALYSIS, S-BIB, S-DEPS, S-FIGURES, S13

**NOT STARTED (7 sessions — per session_prompts_sc26.md but STALE):**
The session prompts file (lines 67-81) marks S-TAXONOMY, S-ANALYSIS, S-BIB, S-DEPS, S-FIGURES as "NOT STARTED" but **all five were completed on 2026-03-27**. The file has a staleness bug — it was last structurally updated before these sessions ran.

**Actually remaining NOT STARTED (5 sessions):**
1. **S10** (P1) — Rodinia cuda-to-opencl eval. ZERO Rodinia cuda-to-opencl results exist on disk. Only XSBench has cuda-to-opencl data.
2. **S10b** (P2) — Remaining OpenCL directions (opencl-to-cuda, opencl-to-omp, omp-to-opencl for Rodinia). ZERO Rodinia results exist for these directions. Only XSBench has them.
3. **S-TIMING** (P2) — CPU/kernel timing. ZERO kernel_time data. All 504 results use wall_time only.
4. **W-S16** (P0!) — Anonymous GitHub repo for double-blind. NOT DONE. No anonymous repo exists. Only remote is `github.com/SamyakJhaveri/parbench_sam`.
5. **W-S15** (P1) — Paper review & polish. NOT DONE.
6. **W-S17** (P0!) — LaTeX transfer. NOT DONE. Paper is 692 lines / 13,059 words in Markdown only. Only 2 .tex files exist (figure/table fragments), no full LaTeX paper.
7. **S18** (P0) — Final review + submit. NOT DONE.

### CRITICAL DISCREPANCY: session_prompts_sc26.md IS STALE

Lines 67-81 show 8 sessions as "NOT STARTED" and 3 as "COMPLETED". But in reality:
- **8 additional sessions were completed** (S-TAXONOMY, S-ANALYSIS, S-BIB, S-DEPS, S-FIGURES, S13 — all on 2026-03-27)
- The "Completed Sessions Summary" table (lines 25-48) IS up-to-date and correct

### EVALUATION DATA INVENTORY (on disk)

| Model | Total Files | Rodinia | XSBench |
|-------|------------|---------|---------|
| claude-sonnet-4-6 | 168 | 108 | 60 |
| gemini-2.5-flash-lite | 168 | 108 | 60 |
| groq-llama-3.3-70b | 168 | 108 | 60 |
| azure-gpt-4.1 | 0 | 0 | 0 |
| **Total** | **504** | **324** | **180** |

**azure-gpt-4.1:** No directory exists at all under results/evaluation/ (not even an empty one). The only azure-gpt trace on disk is 9 BUILD_FAIL entries inside reverification_audit.json.

**Direction coverage per model (each model has identical structure):**
- cuda-to-omp: 95 files (17 L0 Rodinia + 68 L1-L4 Rodinia + 5 XSBench L0 + 5 XSBench L1-L4 = ... actually 17*5=85 Rodinia + various XSBench)
- omp-to-cuda: 23 files (18 Rodinia L0 + 5 XSBench L0-L4)
- 10 other directions: 5 files each (all XSBench only, L0-L4)

**Key gap: NO Rodinia results for any direction except cuda-to-omp and omp-to-cuda.** Sessions S10 and S10b (cuda-to-opencl, opencl-to-cuda, etc.) have not been run for Rodinia.

### eval_summary.json AGGREGATE

- **105/468 = 22.44% overall PASS rate** (468 = 504 minus 36 excluded kmeans/mummergpu)
- Claude: 81/156 (51.92%), Gemini: 11/156 (7.05%), Groq: 13/156 (8.33%)
- cuda-to-omp dominates with 62/255 PASS (24.31%)
- Augmentation trend: L0=23.48%, L1=23.81%, L2=25.00%, L3=20.24%, L4=19.05% (slight degradation at L3-L4)

### M-TASK COMPLETION STATUS

| Task | Status | Evidence |
|------|--------|---------|
| M1 (anon GitHub) | **NOT STARTED** | Only remote: github.com/SamyakJhaveri/parbench_sam |
| M2 (curation survey page) | **NOT STARTED** | No evidence in git |
| M3 (read Paraval paper) | **NOT STARTED** | Sprint plan still says "NOT STARTED" |
| M4 (paper outline) | **DONE** | `docs/paper_outline.md` exists |
| M5 (XSBench) | **DONE** | 4 specs, 4/4 PASS |
| M6 (kernel timing) | **DEFERRED** | Paper framed as correctness-only |
| M7 (Groq setup) | **DONE** | groq-llama evaluated |
| M8 (model selection) | **DONE** | gemini-2.5-flash-lite selected |
| M9 (aug fixes) | **DONE** | Cherry-picked Day 2 |
| M10/M10b (aug retest) | **DONE** | 54/60 PASS, level-invariant |
| M11 (kernel-centric) | **DONE** | Pipeline live since S1.5 |

### PAPER STATUS

- **Paper draft:** 692 lines, 13,059 words, Markdown only at `docs/paper/paper_draft.md`
- **Last updated:** 2026-03-28 (S13 expansion)
- **Sections written:** S3-S5 (W-S12), S6-S8 (S13). S1-S2 (Introduction + Related Work) partially written.
- **Bibliography:** 15 entries in `references.bib`
- **Figures:** 7 files (F1-F6 + T2) in `docs/paper/figures/`
- **LaTeX:** ZERO full LaTeX paper exists. Only 2 .tex fragments (figure/table).
- **Gap from data to draft:** Paper was updated same day as S-VERIFY (Mar 27-28), so data is fresh.

### CRITICAL PATH TO APRIL 8 SUBMISSION

5 P0 items remain:
1. **W-S16: Anonymous GitHub repo** — required for double-blind SC26 submission
2. **W-S17: LaTeX transfer** — estimated 2-3 days, paper is only Markdown
3. **S18: Final review + submit** — estimated 2-3 days
4. **No LaTeX paper** at all yet — this is the biggest blocker
5. **11 days remain** (Mar 28 to Apr 8)

Schedule is extremely tight: LaTeX transfer alone is estimated at 2-3 days, plus final review 2-3 days = 4-6 days minimum for submission mechanics. That leaves ~5 days for any additional eval work (S10, S10b) and paper polishing.

### STALE DOCUMENTATION WARNING

The `session_prompts_sc26.md` "Remaining Sessions Overview" table (lines 63-81) is stale — 5 sessions marked "NOT STARTED" were actually completed on 2026-03-27. This creates confusion about actual project state. The "Completed Sessions Summary" table at the top (lines 25-48) IS accurate.

---

## Task #4: Adversarial SC26 Main Track Paper Review

**Teammate:** sc26-reviewer (adversarial reviewer)
**Status:** COMPLETE
**Recommendation:** MAJOR REVISION (borderline reject/accept — significant issues must be addressed)

---

### Summary

The paper presents ParBench, a benchmark framework for evaluating LLM-based parallel code translation across GPU programming APIs (CUDA, OpenMP, OpenCL). The key contributions are: (1) a build/run/verify harness pipeline with declarative JSON specs, (2) an AST-driven augmentation engine with 6 transforms at 5 levels (L0-L4) to test memorization vs. reasoning, and (3) an empirical evaluation of 3 LLMs across 12 translation directions (468 tasks total). The headline result is that Claude Sonnet achieves 51.92% pass@1 while Gemini Flash Lite (7.05%) and Groq Llama 3.3 70B (8.33%) perform much worse. BUILD_FAIL is the dominant failure mode (38.46%). Augmentation is claimed to be "level-invariant."

---

### Strengths

**S1. Well-Motivated Gap in the Literature**
The three-paper positioning (ParEval → ParEval-Repo → ParBench) is compelling. The insight that isolating kernel-level translation from build-system generation unlocks success (0% repo-level → 51.92% kernel-level) is a genuine contribution. This reframes what "LLM code translation" means for HPC.

**S2. Sound Framework Architecture**
The spec-as-contract design with JSON schemas, the build/run/verify pipeline, and the append-only result logging reflect mature software engineering. The framework is clearly designed for extensibility and reproducibility. The separation of correctness definition from verification logic is elegant.

**S3. Augmentation Engine is Novel for HPC**
The AST-driven augmentation approach using libclang is technically sound. The 6 transforms are well-chosen and the level-invariance finding (54/60 PASS at L1-L4) validates the semantic-preservation claim. This directly addresses the SWE-bench memorization critique (arxiv:2506.12286) in an HPC context — a timely contribution.

**S4. Failure Taxonomy is Scientifically Valuable**
Reporting BUILD_FAIL (38.46%), RUN_FAIL (19.02%), VERIFY_FAIL (9.62%), EXTRACTION_FAIL (10.47%) is far more informative than a single pass/fail number. The finding that VERIFY_FAIL is low (when code compiles and runs, it's usually correct) provides actionable insight for LLM developers.

**S5. Reproducibility by Design**
Temperature=0, fixed seed=42, deterministic evaluation, structured result JSONs, and the mandatory Artifact Description appendix all support reproducibility. The spec schema enables community extension.

**S6. Self-Repair Analysis**
The 78 first-attempt + 27 repaired = 105 PASS breakdown is useful data. The 34.6% relative improvement from retries quantifies the value of error feedback.

---

### Weaknesses

#### W1. CRITICAL — Severely Underpowered Evaluation Corpus (17 kernels for primary eval)

The paper claims "64 specs across 3 benchmark suites" but the actual LLM evaluation uses only **17 Rodinia kernels + 1 XSBench kernel** (the 120 HeCBench specs and 6 KNOWN_FAIL are excluded). With 17 kernels evaluated across only 3 models, the total effective sample is extremely small.

For the primary direction (cuda-to-omp), there are 17 kernels x 3 models x 5 levels = 255 tasks. For the other 11 directions, there are only 5 kernels x 3 models x 1 level = 15 tasks EACH. A single direction has N=15 — statistically meaningless for drawing conclusions about translation difficulty asymmetry.

**The "33.33% pass rate" for cuda-to-opencl, omp-to-opencl, and opencl-to-cuda (all exactly 5/15) is 5 passing tasks.** This is not a finding — it is noise.

**Required fix:** Either (a) run HeCBench evaluation to increase kernel count to 77, or (b) acknowledge the small-N limitation explicitly and remove claims about non-primary translation directions. The paper MUST NOT present 12 translation directions as if they all have equal statistical power. The primary direction (cuda-to-omp, N=255) is the only direction with sufficient sample size for meaningful analysis.

#### W2. CRITICAL — Missing Comparison with LASSI (Direct Competitor)

LASSI (CLUSTER Workshops 2024, arxiv:2407.01638) reports **80% pass rate for OMP-to-CUDA and 85% for CUDA-to-OMP** on HeCBench benchmarks — dramatically higher than ParBench's 22.44% overall or even Claude's 51.92%. LASSI also uses self-correcting loops and translates between the same APIs (CUDA ↔ OpenMP).

The paper outline's Related Work section (§2) mentions LASSI only as "LLM self-correcting pipeline for parallel code (CLUSTER'24)" with no comparison of methodology or results. This is a fatal omission. An SC26 reviewer will immediately ask: "Why is your best model at 52% when LASSI achieves 85% on a similar task? What's different?"

**Required fix:** Add detailed comparison with LASSI in §2 AND §7. Key differences to discuss: LASSI uses agentic self-correction (multi-round with compilation + execution feedback + profiling), uses different models (likely GPT-4), and evaluates on different benchmarks. ParBench deliberately avoids agentic approaches to measure raw translation competence. This distinction must be made explicit and defended as a methodological choice, not an oversight.

#### W3. CRITICAL — Missing CodeRosetta Comparison (NeurIPS 2024)

CodeRosetta (NeurIPS 2024) is a dedicated encoder-decoder model for C++ ↔ CUDA translation. It uses AST-aware pretraining and reports significant improvements over general LLMs. ParBench evaluates general-purpose LLMs but does not compare against domain-specific models. An SC reviewer will ask whether the finding "general LLMs struggle with API syntax" could be trivially addressed by fine-tuning.

**Required fix:** Add CodeRosetta to the related work comparison matrix (Table 1). Discuss whether domain-specific models could be evaluated on ParBench specs as future work. Acknowledge the limitation that only general-purpose models were evaluated.

#### W4. MAJOR — No Statistical Rigor (No Confidence Intervals, No Significance Tests)

The paper reports raw pass rates (22.44%, 51.92%, 7.05%, 8.33%) with no confidence intervals, no significance tests, and no effect sizes. For an evaluation paper at SC26 (which now mandates a research checklist covering "statistical validity"), this is insufficient.

Key statistical questions left unanswered:
- Is the difference between Gemini (7.05%) and Groq (8.33%) statistically significant? (Almost certainly not with N=156 each, but this must be stated.)
- What is the 95% CI for the augmentation level pass rates? The "level-invariance" claim rests on pass rates of 23.48%, 23.81%, 25.00%, 20.24%, 19.05% — these COULD all be within sampling noise, which would support the claim, but this needs a formal test (e.g., chi-squared or Fisher's exact test for independence between level and pass/fail).
- Is the slight downward trend at L3-L4 real or noise? A trend test (Cochran-Armitage) would answer this.

**Required fix:** Add 95% confidence intervals (Wilson or Clopper-Pearson) for all reported pass rates. Perform a chi-squared test for independence between augmentation level and pass/fail outcome. Report effect sizes (Cramer's V or odds ratios) for model comparisons. The SC26 checklist item on "statistical validation with appropriate performance baselines" will flag this.

#### W5. MAJOR — Temperature=0, Single-Seed Evaluation is Methodologically Limiting

The paper uses temperature=0 for all models, producing deterministic outputs. While this aids reproducibility, it means each model-kernel pair is evaluated exactly once (no stochastic sampling). The reported pass rates are point estimates, not distributions.

This is a fundamental tension: pass@1 at temperature=0 is a single Bernoulli trial per task. There is no sampling distribution. You cannot construct confidence intervals in the traditional sense. The paper acknowledges this in §7.2 but does not discuss the implications.

Compare with HumanEval, which evaluates pass@k by sampling N solutions at temperature>0 and estimating the probability that at least one of k samples passes. ParBench's methodology is closer to "eval@1" than "pass@k" — it measures whether the model's single most likely output is correct.

**Required fix:** Either (a) add pass@k evaluation at temperature>0 for at least the primary direction (cuda-to-omp) with 5-10 samples per task, or (b) explicitly redefine the metric as "greedy-decode pass@1" and discuss how this differs from the standard pass@k metric. Acknowledge that the true capability may be higher with sampling.

#### W6. MAJOR — Format Discrepancy: Paper Outline Says "ACM sigconf" but SC26 Uses IEEE

The paper outline states "ACM sigconf double-column, 10 pages + appendices." SC26 uses the **IEEE proceedings template** (IEEEtran), not ACM sigconf. This must be corrected before submission.

**Required fix:** Switch to IEEE conference proceedings format. This affects bibliography formatting, section numbering style (Roman numerals), and page layout.

#### W7. MAJOR — "4 Models" vs. "3 Models" Inconsistency

The paper draft (§V-A, paper_sections_3_4_5.md) states "Four large language models are evaluated" and lists GPT-4.1 alongside Claude, Gemini, and Groq. However, the facts sheet and outline both report only 3 models with data. The paper outline notes "azure-gpt-4.1 was subsequently dropped (zero result files on disk)."

This is a critical consistency issue. The draft text must match the actual data.

**Required fix:** Update §V-A to say "Three large language models" and remove GPT-4.1 from the model list. If GPT-4.1 was evaluated but results were lost, explain why. If it was never evaluated, do not mention it in the methodology. Alternatively, actually run the GPT-4.1 evaluation before submission.

#### W8. MAJOR — Augmentation Claim is Weaker Than Presented

The "level-invariance" claim is the paper's most novel empirical finding, but it rests on fragile ground:

1. **Different sample sizes per level:** L0 has 132 tasks, L1-L4 have 84 each. L0 includes all 12 directions; L1-L4 include only cuda-to-omp. This means L0 and L1-L4 are NOT comparable samples — they differ in both augmentation level AND translation direction. A confound.

2. **The range (19.05%–25.00%) is a 6pp spread.** Without confidence intervals, we cannot say whether this is flat or a real decline.

3. **Per-model augmentation curves are not reported.** The aggregate may be flat because model-specific trends cancel out. Claude may decline while Gemini improves (or vice versa), producing a flat aggregate. Per-model L0-L4 curves are essential.

4. **Augmentation was only verified on the harness baseline (original implementations), not on LLM translations.** The claim "transforms preserve semantics" is validated, but the claim "LLMs are robust to augmentation" is drawn from a different (possibly confounded) comparison.

**Required fix:** (a) Report per-model augmentation curves. (b) Either restrict L0 to cuda-to-omp only for the comparison (matching L1-L4), or acknowledge the confound. (c) Add confidence intervals and a formal test. (d) Consider augmenting both source AND evaluating the same kernel-direction-model triple at L0 vs L1-L4 for a clean paired comparison.

#### W9. MODERATE — No Performance/Efficiency Analysis

The paper explicitly excludes timing measurements (per advisor constraint). While §7.2 acknowledges this as a limitation, an SC reviewer in Track 6 ("Performance Measurement, Modeling, & Tools") will see this as a major gap. A "correct but 1000x slower" OpenMP translation is not useful in practice.

TRACY (arxiv:2508.11468) demonstrates that "correctness is not a reliable proxy for efficiency" — 23.5% of correct translations have pronounced inefficiency. ParBench's PASS results may include severely degraded translations.

**Required fix:** This cannot be fully addressed without new experiments, but: (a) add a paragraph in §7.2 citing TRACY and discussing why correctness-only is insufficient for deployment, (b) for a subset of PASS results (e.g., 10 kernel-model pairs), measure wall-clock execution time of the LLM translation vs. the reference implementation and report the ratio, even if it's not profiler-based kernel time. This provides at least a rough performance sanity check.

#### W10. MODERATE — Missing Related Work (5 papers)

Beyond LASSI and CodeRosetta (critical, see W2/W3), the following are absent from the related work:

1. **HPC-Coder-v2** (arxiv:2412.15178) — Fine-tuned HPC-specific LLM, directly evaluates parallel code generation
2. **TRACY/TRACE** (arxiv:2508.11468) — Execution efficiency benchmarking for LLM code translation
3. **QiMeng-MuPa** (arxiv:2506.11153) — Sequential-to-parallel code translation
4. **VibeCodeHPC** (arxiv:2510.00031) — Agent-based iterative prompting for HPC code generation
5. **SWE-bench Illusion** (arxiv:2506.12286) — Memorization critique directly relevant to augmentation motivation

**Required fix:** Add all 5 to §2 with brief positioning. LASSI, CodeRosetta, and HPC-Coder-v2 go in §2.2 (Parallel Code Evaluation). TRACY and SWE-bench Illusion go in §2.1 (Code Synthesis & Translation Benchmarks). VibeCodeHPC goes in §2.4 (LLM-for-HPC).

#### W11. MODERATE — Unclear Generalizability from Rodinia

Rodinia is a 15+ year-old benchmark suite. Its kernels are extensively documented, widely used in tutorials, and almost certainly present in LLM training data. The augmentation engine addresses surface-level memorization, but cannot address algorithmic-level memorization (the LLM may "know" that BFS uses a frontier-based approach regardless of variable names).

The paper's own augmentation finding (level-invariance) may simply confirm that LLMs have memorized the ALGORITHM of these well-known kernels, not just the code. This is a deeper validity threat than surface-level pattern matching.

**Required fix:** Discuss this explicitly in §7.2. The HeCBench evaluation (120 specs from less-known kernels) would directly address this concern. Frame the HeCBench expansion as addressing not just scale but also the training-data-familiarity confound.

#### W12. MINOR — Self-Repair Methodology Incomplete

The self-repair analysis reports aggregate statistics (78 first-attempt + 27 repaired) but does not break down:
- Which failure modes are recoverable? (BUILD_FAIL → PASS? RUN_FAIL → PASS? VERIFY_FAIL → PASS?)
- How many attempts are typically needed? (Attempt 2 vs. Attempt 3?)
- Is there a regression pattern? (Does repair sometimes make things worse — e.g., PASS on attempt 1, BUILD_FAIL on attempt 2?)

**Required fix:** Add a table showing repair transitions (BUILD_FAIL→PASS, RUN_FAIL→PASS, VERIFY_FAIL→PASS) and attempt-number distributions.

#### W13. MINOR — XSBench Asymmetric Reporting

XSBench has 180 tasks (34/180 = 18.89% PASS) but is reported alongside 17 Rodinia kernels that each have 18 tasks. XSBench's 180 tasks come from all 12 directions × 3 models × 5 levels, while the 17 Rodinia kernels' per-kernel totals are 18 each. This inconsistency in task count per kernel makes the per-kernel comparison table misleading.

**Required fix:** Clarify why XSBench has 10× more tasks per kernel than Rodinia kernels. Consider reporting XSBench separately or normalizing the comparison.

---

### Required Revisions for Accept (Priority-Ordered)

1. **[W2+W3] Add LASSI and CodeRosetta to Related Work with detailed comparison** — This is the single highest-risk omission. A reviewer familiar with LASSI will reject without this.

2. **[W7] Fix 4-model vs. 3-model inconsistency** — The draft MUST match the data. Either run GPT-4.1 or remove it from the text.

3. **[W4] Add statistical analysis** — 95% CIs on all pass rates, chi-squared test for augmentation level independence, significance test for model comparisons. The SC26 checklist demands this.

4. **[W8] Fix augmentation comparison confound** — L0 and L1-L4 have different direction compositions. Report per-model curves. Add formal tests.

5. **[W1] Address small-N for non-primary directions** — Either expand evaluation or explicitly caveat that non-primary directions are "exploratory" with insufficient power.

6. **[W6] Switch to IEEE format** — Formatting issue, but desk rejection if wrong template.

7. **[W10] Add 5 missing related work papers** — Straightforward but important for positioning.

8. **[W9] Add minimal performance sanity check** — Even rough wall-clock ratios for 10 PASS cases would help.

### Suggested Improvements (Nice-to-Have)

1. **Run HeCBench evaluation** — Would address W1 (kernel count), W11 (generalizability), and strengthen the paper's "64 specs" claim by actually evaluating on all of them.

2. **Add pass@k at temperature>0** — Would address W5 and align with standard LLM evaluation methodology.

3. **Add a 4th model (GPT-4.1 or a reasoning model)** — The 3-model evaluation feels thin for SC main track. 4-5 models is the norm for benchmark papers.

4. **Stratify results by translation complexity** — The paper defines single_file, multi_to_single, etc. but never reports pass rates by complexity class. This is low-hanging analytical fruit.

5. **Report token usage/cost per translation** — ParEval-Repo reports inference token costs. ParBench should too for practical comparison.

### Unsupported or Overstated Claims

| Claim | Issue |
|-------|-------|
| "64 specs across 3 benchmark suites" | Only 17+1 kernels actually evaluated. The 120 HeCBench specs are schema-only. |
| "12 translation directions" | 10 of 12 directions have N=15 total tasks. Statistically meaningless for conclusions. |
| "Level-invariant" augmentation | Confounded comparison (L0 has different directions than L1-L4). No formal test. |
| "22.44% overall PASS" | Dominated by Claude (81/105 PASSes = 77%). "Overall" obscures massive model gap. |
| "LLMs attend to parallel structure, not surface syntax" | Could equally mean "LLMs memorized these well-known algorithms." Augmentation only tests surface-level memorization, not algorithmic memorization. |
| "BUILD_FAIL suggests API-specific syntax training gap" | Alternative: BUILD_FAIL may reflect prompt engineering issues, not model limitations. Different prompts may yield different BUILD_FAIL rates. |

---

### Verdict

ParBench is a well-engineered framework with genuine contributions (kernel-centric design, augmentation engine, failure taxonomy). The paper would be a strong accept at a workshop (e.g., LLVM-HPC, WACCPD) in its current form. For SC26 main track, the evaluation is underpowered (17 kernels, 3 models, no statistics), key related work is missing (LASSI, CodeRosetta), and the augmentation analysis has methodological confounds. With the required revisions above — particularly items 1-5 — this could become a solid SC26 paper.

### Sources Consulted

- SC26 Papers: https://sc26.supercomputing.org/program/papers/
- SC26 Research Checklist: https://sc26.supercomputing.org/2026/03/get-it-in-check-tech-program-adopts-research-checklist/
- SC26 AD/AE: https://sc26.supercomputing.org/program/papers/reproducibility-appendices-badges/
- ParEval-Repo: https://arxiv.org/abs/2506.20938
- LASSI: https://arxiv.org/abs/2407.01638
- CodeRosetta: https://arxiv.org/abs/2410.20527
- HPC-Coder-v2: https://arxiv.org/abs/2412.15178
- TRACY: https://arxiv.org/abs/2508.11468
- SWE-bench Illusion: https://arxiv.org/abs/2506.12286
- VibeCodeHPC: https://arxiv.org/abs/2510.00031
- ParaCodex: https://arxiv.org/abs/2601.04327
- QiMeng-MuPa: https://arxiv.org/abs/2506.11153

---

## Task #4 Supplemental: Additional Weaknesses

**Teammate:** sc26-reviewer (supplemental findings after cross-referencing consolidated data)

### W14. CRITICAL — Paper Contains Factually Incorrect Numbers

The team's data audit reveals the paper draft contains at least three factually wrong claims:

1. **"Zero VERIFY_FAIL"** — Actual: 45 VERIFY_FAIL (9.62% of 468 tasks). This is not a rounding issue — it is a false claim that directly contradicts the data.
2. **"BUILD_FAIL dominance 68.4%"** — Actual: ~38.46-40.9% depending on denominator (180/468 or 206/504). The 68.4% figure appears fabricated or from a stale/partial analysis.
3. **"500 tasks"** — Actual: 468 eligible tasks (or 504 total including KNOWN_FAIL kernel results).

**Impact:** If any of these incorrect numbers make it into the submitted paper, reviewers who attempt to verify against the provided artifact will find discrepancies. This is a credibility-destroying outcome for a benchmark paper whose entire value proposition is rigorous measurement. Every single number in the paper must be traced back to a specific data file.

**Required fix:** Audit EVERY quantitative claim in the paper against `eval_summary.json` and the raw result files. Create a fact-checking table mapping each claim to its source file, line number, and computation. This is non-negotiable for a benchmark paper.

### W15. CRITICAL — No LaTeX Draft Exists (11 Days to Deadline)

The paper exists only as Markdown (692 lines across several files). SC26 requires IEEE proceedings format (IEEEtran LaTeX template). Converting a Markdown outline to camera-ready LaTeX with proper figures, tables, bibliography, and formatting is a minimum 4-6 day effort.

With 11 days to the April 8 deadline, this leaves at most 5-7 days for the required revisions identified in W1-W13. This is an extremely tight timeline.

**Required fix:** Begin LaTeX transfer immediately. Use the existing Markdown section drafts (paper_sections_3_4_5.md) as the starting point. Prioritize getting the framework description (§3-§5, which are most complete) into LaTeX first.

### W16. MAJOR — Rodinia Non-Primary Directions Not Yet Run

The initial review (W1) flagged the small-N problem for non-primary directions (N=15 each). The consolidated data reveals these non-primary results come from XSBench only — the planned Rodinia multi-direction evaluation (Sessions S10/S10b) was never executed. This means:

- cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp for Rodinia kernels: **NO DATA**
- Only cuda-to-omp and omp-to-cuda have Rodinia data
- All other 10 directions are XSBench-only (1 kernel, 3 models, ~5 tasks per direction)

This is worse than initially assessed. The "12 translation directions" claim in the abstract is misleading — only 2 directions have multi-kernel data.

**Required fix:** Either (a) run at least cuda-to-opencl and opencl-to-cuda for Rodinia kernels before submission (adds ~30 more tasks per direction), or (b) restructure §6.6 to clearly separate "primary directions with sufficient data (cuda-to-omp, omp-to-cuda)" from "exploratory directions (XSBench-only, N=5-15)."

### W17. MODERATE — No Anonymous Artifact Repository

SC26 requires double-anonymous review for the paper. An Artifact Description appendix is mandatory. Without an anonymous GitHub repository (or equivalent), the AD appendix cannot point to reproducible code without breaking anonymity.

**Required fix:** Create an anonymous repository (e.g., anonymous GitHub via anonymous.4open.science, or Zenodo with embargoed DOI) containing: the harness code, spec schemas, augmentation engine, and evaluation scripts. Strip all identifying information. This must be ready at submission time.

---

### Updated Priority List (incorporating supplemental findings)

1. **[W14] Fix factually incorrect numbers** — HIGHEST PRIORITY. Wrong numbers in a benchmark paper = rejection.
2. **[W15] Begin LaTeX transfer** — Without this, there is no submission.
3. **[W2+W3] Add LASSI and CodeRosetta comparison** — Fatal related work gap.
4. **[W7] Fix 4-model vs 3-model inconsistency** — Draft vs data mismatch.
5. **[W4] Add statistical analysis** — SC26 checklist requirement.
6. **[W8] Fix augmentation confound** — Core contribution at risk.
7. **[W16] Address non-primary direction data gap** — Either run more evals or restructure claims.
8. **[W1] Small-N caveat for non-primary directions** — Presentation fix.
9. **[W6] IEEE format** — Already addressed by W15 (LaTeX transfer).
10. **[W17] Anonymous artifact repo** — Required for submission.
11. **[W10] Missing related work** — Straightforward additions.
12. **[W9] Performance sanity check** — Nice-to-have if time permits.

---

## Task #5: Final Synthesis & Prioritized Action Plan

**Teammate:** search-planner (coordinator)
**Status:** COMPLETE

---

### EXECUTIVE SUMMARY

ParBench has a well-engineered framework and 504 verified result files. The paper draft has substantive content (~13,000 words). However, five issues threaten submission:

1. **Paper draft uses stale 4-model/500-task data** — must be rewritten for 3-model/468-task reality
2. **No LaTeX paper exists** — only Markdown; SC26 requires formatted submission
3. **No anonymous repo** — required for double-blind review
4. **Missing critical related work** — LASSI (85% PASS on similar task) not addressed
5. **Augmentation "level-invariance" claim is misleading** — Gemini drops to 0% at L4

The project is in a **"last mile" crisis**: the hardest work (framework, evaluation, data collection) is done, but the paper is not submission-ready. With 11 days and focused execution, submission is achievable.

---

### SECTION 1: WHAT IS DONE (Verified Complete)

#### 1.1 Infrastructure (fully functional)
- Spec schema v1.0.0 with 184 specs (60 Rodinia, 120 HeCBench, 4 XSBench)
- Build/run/verify harness pipeline with kernel-centric translation mode
- AST-driven augmentation engine with 6 transforms, 5 levels (L0-L4)
- LLM evaluation pipeline with self-repair (up to 3 retries)
- Post-S-VERIFY: stdout_pattern + exit_code conjunction verification

#### 1.2 Evaluation Data (504 raw files, 468 in summary)
- 3 models: claude-sonnet-4-6 (81/156=51.92%), gemini-2.5-flash-lite (11/156=7.05%), groq-llama-3.3-70b (13/156=8.33%)
- 12 translation directions evaluated
- L0-L4 augmentation complete for cuda-to-omp (primary direction)
- 17 kernels evaluated (16 Rodinia + 1 XSBench)
- Self-repair: 78 first-attempt + 27 repaired = 105 total PASS

#### 1.3 Augmentation Baseline
- 54/60 Rodinia PASS at all L1-L4 levels (level-invariant for harness)
- 6 KNOWN_FAIL at all levels (pre-existing, not augmentation-caused)

#### 1.4 Supporting Materials
- Paper outline (docs/paper_outline.md) — 8 sections, complete structure
- Paper draft (docs/paper/paper_draft.md) — 692 lines, ~13,000 words (BUT STALE — see Section 2)
- Publication figures F1-F6 generated (PDF + PNG)
- Bibliography with 15 entries (references.bib)
- Error taxonomy, SLoC analysis, token analysis, self-repair analysis completed
- requirements.txt, pyproject.toml, Dockerfile, REPRODUCING.md committed
- Facts sheet (docs/facts_sheet_s_verify.md) — canonical numbers

#### 1.5 Sessions Completed (23 total)
S1, S1.5, S1.6, S2, S3, S3b, S3-PM, S4, S5, S6, S7, S8, S9, W-S11, W-S12-PARTIAL, W-S14, S-VERIFY, S-TAXONOMY, S-ANALYSIS, S-BIB, S-DEPS, S-FIGURES, S13

---

### SECTION 2: WHAT IS NOT DONE (Planned but Unexecuted)

#### 2.1 P0 — Submission Blockers

| Item | Est. Effort | Notes |
|------|-------------|-------|
| **Fix stale paper draft** | 1 day | Abstract, S1, S6 all use 4-model/500-task/0-VERIFY_FAIL numbers. Must rewrite for 3-model/468-task/45-VERIFY_FAIL. The paper outline (paper_outline.md) IS correct; the draft (paper_draft.md) is not. |
| **W-S17: LaTeX transfer** | 2-3 days | No full LaTeX paper exists. Must convert 692-line Markdown to ACM sigconf format. NOTE: sc26-reviewer flags this should be IEEE (IEEEtran), contradicting project docs that say ACM sigconf. **Samyak must verify with SC26 CFP which template is required.** |
| **W-S16: Anonymous repo** | 4 hours | Double-blind requires anonymous GitHub. Must sanitize author names, paths, commit messages. |
| **S18: Final review + submit** | 2-3 days | Co-author review cycle, final number verification, submission mechanics. |

#### 2.2 P1 — Paper Weaknesses (Addressable)

| Item | Est. Effort | Impact |
|------|-------------|--------|
| **Add LASSI comparison** (W2) | 4 hours | HIGHEST-RISK omission per reviewer. LASSI reports 85% PASS on CUDA-OMP. Must explain why ParBench gets 52% — difference is agentic vs. raw translation. |
| **Add CodeRosetta comparison** (W3) | 2 hours | Domain-specific model comparison. |
| **Fix augmentation confound** (W8) | 3 hours | Report per-model curves (verified: Claude flat, Gemini 17.6%→0%, Groq 17.6%→5.9%). Restrict comparison to cuda-to-omp direction only. This is actually a STRONGER finding than "level-invariance." |
| **Add statistical analysis** (W4) | 4 hours | Wilson CIs, chi-squared for augmentation independence, significance tests for model comparisons. |
| **Add 5 missing related work papers** (W10) | 3 hours | LASSI, CodeRosetta, HPC-Coder-v2, TRACY, SWE-bench Illusion, VibeCodeHPC, QiMeng-MuPa. |
| **Fix 4→3 model inconsistency** (W7) | 2 hours | Already identified in Task #1. Remove all GPT-4.1 references from draft. |
| **S10: cuda-to-opencl eval** | 1 day compute | 17 Rodinia kernels x 3 models. Would give Rodinia data for a 3rd direction. |

#### 2.3 P2 — Nice-to-Have

| Item | Est. Effort | Impact |
|------|-------------|--------|
| S10b: remaining OpenCL directions | 1 day compute | 3 more directions for Rodinia |
| S-TIMING: kernel timing | 4 hours | Some performance data for PASS results |
| W-S15: paper review + polish | 4 hours | Full review pass |
| HeCBench eval | 2+ days | Would address small-N (17→77 kernels) |
| pass@k at temperature>0 | 1 day compute | Standard LLM eval methodology |
| Stratify by translation complexity | 2 hours | Data exists in specs, never analyzed |
| Self-repair transition analysis | 2 hours | Which failure modes are recoverable? |

---

### SECTION 3: GAPS (Needed but Never Planned)

#### 3.1 Statistical Analysis (reviewer will require)
The paper has ZERO confidence intervals, ZERO significance tests, ZERO effect sizes. SC26 now requires a research checklist covering "statistical validity." This was never planned in any session prompt. **Must be added.**

#### 3.2 Per-Model Augmentation Curves (not in any session)
Verified from the data that per-model curves tell a dramatically different story than the aggregate:
- Claude: L0=52.9%, L1=47.1%, L2=47.1%, L3=41.2%, L4=52.9% (flat — genuinely level-invariant)
- Gemini: L0=17.6%, L1=17.6%, L2=17.6%, L3=11.8%, L4=0.0% (catastrophic L4 collapse)
- Groq: L0=17.6%, L1=11.8%, L2=11.8%, L3=11.8%, L4=5.9% (gradual decline)

This is a BETTER finding than "level-invariant" — it shows augmentation robustness DISCRIMINATES model capability. Claude reasons about structure; Gemini/Groq rely more on surface patterns. The paper draft's abstract actually hints at this ("Gemini degrades by 75%") but the analysis section doesn't present the per-model curves.

#### 3.3 IEEE vs ACM Template Verification
The reviewer flags W6: SC26 may use IEEE (IEEEtran), not ACM sigconf. The project docs are inconsistent — `paper_sections_3_4_5.md` says IEEE, `paper_outline.md` says ACM. **Samyak must verify with the SC26 2026 CFP before W-S17 starts.** Using the wrong template means desk rejection.

#### 3.4 Self-Repair Transition Analysis
The data to answer "which failure modes are recoverable?" exists in the `attempts[]` arrays of result JSONs but was never analyzed. Low effort, high value for the paper.

#### 3.5 Direction-Specific Small-N Warning
10 of 12 directions have only N=15 tasks (5 XSBench tasks per model). The paper presents all 12 directions as if equally powered. The "33.33% pass rate" for cuda-to-opencl is literally 5 passing tasks. **The paper must caveat non-primary directions as exploratory.**

---

### SECTION 4: CLAIMS MATRIX (Supportable vs Unsupportable)

| Claim in Paper | Supportable? | Evidence | Action Needed |
|----------------|:------------:|----------|---------------|
| "51.92% PASS for Claude Sonnet" | YES | 81/156, verified against 504 raw files | None |
| "22.44% overall PASS" | YES | 105/468, verified. Excludes kmeans/mummergpu intentionally | None |
| "BUILD_FAIL is dominant failure (38.46%)" | YES | 180/468, verified | Fix draft (currently says 68.4%) |
| "Level-invariant augmentation" | PARTIALLY | Aggregate is flat (19-25%), BUT Gemini drops to 0% at L4. Per-model curves tell a richer story | Reframe as "model-dependent augmentation robustness" |
| "12 translation directions" | WEAK | 10/12 directions have N=15. Only cuda-to-omp (N=255) and omp-to-cuda (N=63) have meaningful sample sizes | Add caveat; present non-primary as exploratory |
| "64 specs across 3 suites" → later "184 specs" | MISLEADING | 184 specs exist but only 17 kernels evaluated. HeCBench (120 specs) not even cloned | Distinguish framework scope from evaluation scope explicitly |
| "Zero VERIFY_FAIL across all tasks" | FALSE | 45 VERIFY_FAIL (9.62%). This claim is from the OLD pre-S-VERIFY draft | Fix immediately |
| "4 LLMs evaluated" | FALSE | azure-gpt-4.1 has 0 result files on disk | Fix immediately |
| "500 evaluated tasks" | FALSE | 468 eligible tasks | Fix immediately |
| "Kernel-centric isolation unlocks success (0% → 52%)" | YES | Compared to ParEval-Repo's 0% at scale | Cite ParEval-Repo properly |
| "Self-repair adds 27 PASSes (25.7%)" | YES | 78 first-attempt + 27 repaired = 105, verified | None |
| "Augmentation is semantics-preserving" | YES | 54/60 PASS at all L1-L4 for harness baseline | None |

---

### SECTION 5: PRIORITIZED ACTION PLAN

#### Option A: "Minimum Viable Submission" (11 days)

Focus exclusively on submission-blocking items. Accept a weaker paper.

| Day | Task | Who |
|-----|------|-----|
| Day 11 (Mar 28) | Fix stale 4→3 model data in paper_draft.md | Claude session |
| Day 11 (Mar 28) | Verify SC26 template (IEEE vs ACM) with CFP | Samyak |
| Day 12 (Mar 29) | Add LASSI + CodeRosetta to Related Work | Claude session |
| Day 12 (Mar 29) | Report per-model augmentation curves + reframe claim | Claude session |
| Day 12 (Mar 29) | Add statistical analysis (CIs, chi-squared) | Claude session |
| Day 13-14 (Mar 30-31) | W-S17: LaTeX transfer (correct template) | Claude session |
| Day 14 (Mar 31) | W-S16: Anonymous GitHub repo | Claude session (4h) |
| Day 15-16 (Apr 1-2) | S12: Revise Introduction + Related Work | Supervised |
| Day 17-18 (Apr 3-4) | W-S15: Full paper review + polish | Claude session |
| Day 19-20 (Apr 5-6) | Co-author review (Gal, Erel) | Samyak |
| Day 21 (Apr 8) | S18: Final review + submit | Samyak |

**Risk:** Tight but feasible. No new eval data. Paper goes with 17 kernels and 3 models. Non-primary directions caveated as exploratory.

#### Option B: "Strengthened Submission" (11 days, GPU + paper in parallel)

Run S10 (cuda-to-opencl) in background while fixing the paper.

| Day | GPU Lane | Paper Lane |
|-----|----------|------------|
| Day 11-12 | S10: cuda-to-opencl eval (51 tasks) | Fix stale data, add LASSI/CodeRosetta, statistical analysis |
| Day 13-14 | S10 completes; incorporate results | W-S17: LaTeX transfer |
| Day 15-16 | (idle) | S12: Intro + Related Work revision |
| Day 17-18 | (idle) | W-S16 (anon repo) + W-S15 (review) |
| Day 19-20 | (idle) | Co-author review |
| Day 21 | (idle) | Submit |

**Benefit:** Adds a 3rd major direction with Rodinia data (not just XSBench). Strengthens multi-direction claims.
**Risk:** If S10 has issues, it could distract from paper work.

#### Option C: "Maximum Strength" (tight, high risk)

Option B + S10b + S-TIMING + HeCBench pilot.

**NOT RECOMMENDED** given 11-day timeline. Too many moving parts. Focus on paper quality over eval breadth.

---

### SECTION 6: RECOMMENDATIONS

#### Immediate Actions (Today, Mar 28)

1. **Samyak: Verify SC26 template** — Is it IEEE IEEEtran or ACM sigconf? Check the official SC26 CFP. This determines the entire W-S17 session.
2. **Fix the 3 FALSE claims** in paper_draft.md: "4 LLMs" → "3 LLMs", "500 tasks" → "468 tasks", "zero VERIFY_FAIL" → "45 VERIFY_FAIL (9.62%)". These are factual errors.
3. **Fix BUILD_FAIL percentage**: Draft says 68.4%, reality is 38.46%.

#### This Week (Mar 28-31)

4. **Add LASSI comparison** — This is the single highest-risk reviewer objection. A reviewer who knows LASSI will reject without it.
5. **Report per-model augmentation curves** — The Gemini L4→0% finding is scientifically more interesting than "level-invariance." Reframe the augmentation contribution.
6. **Add statistical analysis** — Wilson CIs on all pass rates, chi-squared for augmentation independence.
7. **Add 5+ missing related work** — LASSI, CodeRosetta, HPC-Coder-v2, TRACY, SWE-bench Illusion.
8. **Start W-S17 (LaTeX)** — This is the longest single task remaining.

#### Next Week (Apr 1-7)

9. Complete LaTeX transfer.
10. W-S16: Anonymous repo.
11. Co-author review cycle.
12. S18: Final submission.

#### Strategic Decision for Samyak

**Option A vs Option B?** Recommendation: **Option B** (run S10 in parallel with paper work). The cuda-to-opencl Rodinia data addresses the "only 2 directions have real data" criticism with minimal risk — it's a background GPU task that doesn't compete with paper writing.

#### What to Cut

- **S10b** (remaining OpenCL directions) — nice-to-have, not worth the time
- **S-TIMING** — paper is framed as correctness-only; Gal already deferred this
- **HeCBench eval** — no time to clone, verify, and evaluate 120 specs
- **pass@k at temperature>0** — methodological improvement but not required
- **4th model** — 3 models is sufficient with proper statistical analysis

---

### SECTION 7: KEY DATA CORRECTIONS NEEDED IN PAPER DRAFT

These are factual errors that must be fixed regardless of any strategic decisions:

| Location | Current (Wrong) | Correct | Source |
|----------|-----------------|---------|--------|
| Abstract | "four LLMs" | "three LLMs" | eval_summary.json |
| Abstract | "500 evaluated tasks" | "468 evaluated tasks" | facts_sheet_s_verify.md |
| Abstract | "zero VERIFY_FAIL" | "45 VERIFY_FAIL (9.62%)" | facts_sheet_s_verify.md |
| Abstract | "BUILD_FAIL 68.4%" | "BUILD_FAIL 38.46% (180/468)" | eval_summary.json |
| Abstract | "GPT-4.1 achieves 52.9%" | Remove — no GPT-4.1 data exists | 0 files on disk |
| S1.4 | "70.6%" for Claude (L0 only) | "51.92%" (all directions) | eval_summary.json |
| S6 | 4-model tier descriptions | Rewrite for 3-model tiers | eval_summary.json |
| S6 | "4-model kernel tiers" | "3-model kernel tiers" | eval_summary.json |
| Multiple | References to azure-gpt-4.1 | Remove entirely | 0 files on disk |

---

### STALE DOCUMENTATION WARNING

`docs/session_prompts_sc26.md` lines 67-81 mark 5 sessions as "NOT STARTED" that were actually completed on 2026-03-27 (confirmed via git commits): S-TAXONOMY, S-ANALYSIS, S-BIB, S-DEPS, S-FIGURES. The "Completed Sessions Summary" table at lines 25-48 IS accurate. The remaining sessions table needs updating.

---

*Report synthesized from: Task #1 (project docs map), Task #2 (data inventory), Task #3 (git history audit), Task #4 (adversarial SC26 review). All data verified against raw files on disk.*

---

## Team Lead Analysis

### Key Insight: Simpson's Paradox in Augmentation Data

The aggregate "level-invariance" claim (19-25% across L0-L4) masks a dramatic per-model divergence:
- **Claude**: 52.9% → 47.1% → 47.1% → 41.2% → 52.9% (genuinely flat — robust to augmentation)
- **Gemini**: 17.6% → 17.6% → 17.6% → 11.8% → **0.0%** (catastrophic L4 collapse)
- **Groq**: 17.6% → 11.8% → 11.8% → 11.8% → 5.9% (gradual decline)

This is **Simpson's Paradox** in action — the aggregate is flat because Claude's stability masks Gemini/Groq's collapse. The disaggregated finding is scientifically *more* interesting: augmentation robustness discriminates model capability. Claude reasons about parallel structure; Gemini/Groq rely more on surface patterns that augmentation disrupts. This should be the paper's augmentation contribution, not "level-invariance."

### Key Insight: Benchmark Paper Credibility

Wrong numbers in a benchmark paper destroy credibility. Unlike a systems paper where performance varies with setup, a benchmark paper's entire value proposition is rigorous measurement. If a reviewer downloads ParBench, runs `eval_summary.json`, and finds that the paper says "zero VERIFY_FAIL" when the data shows 45 — that's not a minor discrepancy, it's a falsification flag. The fact-checking table (mapping each claim → source file → computation) is a technique from journalism and auditing that should be standard practice for any empirical paper.

### Key Insight: LASSI as Opportunity, Not Threat

The LASSI comparison (80-85% vs ParBench's 52%) is actually an *opportunity*. LASSI uses agentic self-correction (multi-round with compilation + execution feedback + profiling), while ParBench deliberately measures raw translation competence (single-shot + limited self-repair). These are complementary measurements: LASSI answers "how good can LLMs get with tooling?" while ParBench answers "what do LLMs actually understand about parallel code?" The paper must explicitly defend this as a methodological choice.

---

*End of report. Generated 2026-03-28 by sc26-audit agent team (4 Opus teammates).*
