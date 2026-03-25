# Sprint to SC26 — ParBench 21-Day Plan

> **Deadline:** SC26 paper submission — **April 8, 2026**
> **Sprint window:** March 18 → April 8 (21 days)
> **Last updated:** 2026-03-24 (Day 7 audit — S1–S6 complete, 4-model L0 baseline done; see §1.8)
> **Authors:** Samyak, Erel, Gal (advised)
>
> **How to use this document:**
> - **Team members:** Read the full plan, then jump to your week's tasks
> - **Claude Code sessions:** Read this plan first, then execute tasks sequentially within each day
> - **Entry point:** See "Session Entry Point" at the bottom for copy-paste setup commands

---

## 1. Where We Are (March 18 Baseline)

### 1.1 Phase 1 Complete — Infrastructure Fixed

All 13 infrastructure items shipped across commits `a1ab7de` → `e878ee5`:

| Category | Items Shipped |
|----------|--------------|
| Prompt quality | Prompt enhancement, header staging, support file inclusion |
| Error capture | Head+tail build errors, run stderr/stdout, error_message field |
| Retry mechanism | `--max-retries` flag (implemented, untested live with retries > 1) |
| Spec fixes | OMP args (nw, hotspot), needle.h permanent `-I` include path |
| Batch runner | `run_eval_batch.py` with `--resume`, `--max-failures`, Markdown reports |
| Documentation | evaluation.md, known-issues.md, CLAUDE.md overhaul |
| Dashboard | Updated to 50% pass rate |

### 1.2 Pilot Results (5 kernels × 2 models, cuda→omp, L0)

> **NOTE (2026-03-19):** Claude Sonnet is REMOVED as an eval target (March 18 meeting decision).
> Claude pilot data below is kept for historical context only. All future evals use GPT-4.1 + open models.

| Kernel | Claude Sonnet 4 (archived) | Azure GPT-4.1 | Failure Root Cause |
|--------|:-:|:-:|---|
| bfs | **PASS** | **PASS** | — |
| nw | **PASS** | **PASS** | — (was infrastructure; fixed) |
| hotspot | BUILD_FAIL | **PASS** | Claude: missing `#include <cstring>` |
| srad | RUN_FAIL | RUN_FAIL | Both: LLM drops `nthreads` arg (quality) |
| backprop | BUILD_FAIL | BUILD_FAIL | Claude: dup `gettime`; Azure: `HEIGHT` undeclared |

**5-kernel pilot pass rate: 50% (5/10) for Azure GPT-4.1.** All remaining failures are LLM quality issues, not infrastructure.

> **Day 2 update:** 10-kernel pilot completed — **6/10 PASS (60%)** for Azure GPT-4.1 at L0. See §1.6 for full results. Key finding: 3/4 BUILD_FAILs are structural multi-file issues (M11).

Infrastructure baseline confirmed — continuing full evaluation sweep with GPT-4.1 (Phase 1), then open models via Groq/Modal (Phase 2).

### 1.3 Inventory

#### Specs (184 total, updated 2026-03-23)

| Suite | CUDA | OMP | OpenCL | OMP-target | Total |
|-------|:----:|:---:|:------:|:----------:|:-----:|
| Rodinia | 22 | 18 | 20 | 0 | **60** |
| XSBench | 1 | 1 | 1 | 1 | **4** |
| HeCBench | 60 | 60 | 0 | 0 | **120** |
| **Total** | **83** | **79** | **21** | **1** | **184** |

**22 unique Rodinia kernels:** backprop, bfs, bptree, cfd, dwt2d, gaussian, heartwall, hotspot, hotspot3d, huffman, hybridsort, kmeans, lavamd, lud, mummergpu, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster

> **Note (2026-03-20 — M10b):** 5 phantom specs deleted — `gaussian-omp`, `huffman-omp`,
> `huffman-opencl`, `hybridsort-omp`, `mummergpu-opencl`. These pointed to directories that
> don't exist at Rodinia commit `9c10d3ea`. See `known-issues.md` M10b section.

#### Translation Pairs Available

| Direction | Rodinia | XSBench | HeCBench | Total |
|-----------|:-------:|:-------:|:--------:|:-----:|
| cuda → omp | 21 | 1 | 60 | 82 |
| omp → cuda | 21 | 1 | 60 | 82 |
| cuda → opencl | 22 | 1 | 0 | 23 |
| opencl → cuda | 22 | 1 | 0 | 23 |
| omp → opencl | 21 | 1 | 0 | 22 |
| opencl → omp | 22 | 1 | 0 | 23 |
| **Total** | **129** | **6** | **120** | **255** |

> **Note:** XSBench omp_target spec excluded from standard eval batches (nvc dependency).
> 3 standard XSBench specs (cuda, omp, opencl) used for evaluation.

#### Hardware & Compilers (Linux, RTX 4070)

| API | Compiler | Path / Flag | Available |
|-----|----------|------------|:---------:|
| CUDA | nvcc (HPC SDK 24.3) | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc` | YES |
| OpenMP CPU | GCC 12.4 `-fopenmp` | System GCC | YES |
| OpenCL | NVIDIA runtime | `/opt/nvidia/hpc_sdk/.../cuda/{include,lib64}` | YES |
| OpenACC | nvc (HPC SDK 24.3) | `/opt/nvidia/hpc_sdk/.../compilers/bin/nvc` | YES *(compiler available; no benchmark source — see DESCOPED note at Day 10–11)* |
| OpenMP target offload | GCC `-foffload=nvptx-none` | Needs verification | UNKNOWN |
| HIP | hipcc | Not installed (NVIDIA-only machine) | NO |
| SYCL | dpcpp | Not installed | NO |

#### Models

> **UPDATED 2026-03-19 (March 18 meeting).** Model plan changed significantly.
> **FINAL MODEL SET (Gal, 2026-03-23):** All 4 models have L0 cuda-to-omp baselines. See §1.8 for full summary.

| Model | Provider | L0 cuda-to-omp | PASS/17 | % | Session |
|-------|----------|---------------|---------|---|---------|
| `azure-gpt-4.1` | Azure OpenAI | ✅ DONE | 9 | 52.9% | S2 |
| `claude-sonnet-4-6` | Anthropic API | ✅ DONE | 12 | 70.6% | S3b |
| `gemini-2.5-flash-lite` | Google AI API | ✅ DONE | 4 | 23.5% | S3b |
| `groq-llama-3.3-70b-versatile` | Groq API | ✅ DONE | 5 | 29.4% | S3 |
| ~~`claude-sonnet-4-20250514`~~ | ~~Anthropic API~~ | REMOVED | — | — | — |

**Key constraints (Gal Oren, March 18):**
- **NO reasoning models** — test inherent LLM knowledge, not search/reasoning (00:19:31)
- **NO agentic models** — too complex for this paper scope
- **Turn reasoning OFF for all models** — fair comparison (Le Chen, 00:25:43)
- Match **Power of Evolve paper** models: Gemini, GPT-4, Llama 3.3, Qwen (Gal, 00:23:47)
- Pick ~2-3 models and commit (Niranjan, 00:22:43)

#### Augmentation Pass Rates (60 Rodinia specs, seed=42)

| Level | Pass | Rate | Notes |
|-------|:----:|:----:|-------|
| L1 | 54/60 | 90% | Level-invariant |
| L2 | 54/60 | 90% | Identical to L1 — transforms are semantics-preserving |
| L3 | 54/60 | 90% | Identical to L1 — level-invariant confirmed |
| L4 | 54/60 | 90% | Identical to L1 — level-invariant confirmed |

**Note (updated 2026-03-20 post-M10b):** Full 240-task retest completed (60 specs × 4 levels, seed=42).
Erel's M9 fixes + M10b spec fixes (5 phantoms deleted, 6 spec arg/build fixes) raised pass rate from
45/60 (75%) to 54/60 (90%). Level-invariance holds across all 54 passing specs — augmentation introduces
zero correctness regressions. Results: `results/augmentation/retest_post_session2.{json,md}`.
BUILD_FAIL (4): hybridsort-cuda, kmeans-cuda, mummergpu-cuda, mummergpu-omp.
FAIL (2): kmeans-opencl, nn-opencl.

#### Current Evaluation Results on Disk (updated Day 2)

```
results/evaluation/
├── claude-sonnet-4-20250514/     (6 result JSONs — ARCHIVED, model removed)
│   ├── rodinia-{bfs,nw,hotspot,srad,backprop}-cuda-to-...-omp.json
│   └── rodinia-bfs-omp-to-rodinia-bfs-cuda.json  (reverse direction test)
├── azure-gpt-4.1/               (10 result JSONs — Day 2 pilot)
│   └── rodinia-{bfs,hotspot,lud,nn,nw,pathfinder,backprop,kmeans,srad,streamcluster}-cuda-to-...-omp.json
├── eval_summary.json             (NEW — generated by analyze_eval.py)
├── eval_summary.md               (NEW — publication-ready tables)
├── batch_cuda-to-omp_20260317_*.{json,md}  (STALE — to be cleaned up via Task 2E)
├── task2_completion_report.md
└── task2_research_report.md
```

### 1.4 Known Bugs in Evaluation Code

| # | Bug | Severity | File | Fix |
|---|-----|----------|------|-----|
| ~~**B8**~~ | ~~`--augment-levels` flag missing from batch runner~~ | ~~CRITICAL~~ | `run_eval_batch.py` | **FIXED Day 2** — flag added, wired to `evaluate_translation()`, result paths tagged `-L{n}` |
| B1 | `kernel` field missing → `?` in Markdown reports | HIGH | `llm_evaluate.py` | Add `"kernel"` field to result dict |
| B2 | Markdown stats show `0/1` instead of `0/5` | HIGH | `run_eval_batch.py` | Fix `_generate_markdown()` iteration |
| B3 | Race condition on concurrent batch runners | HIGH | `run_eval_batch.py` | File locking on result writes |
| B4 | No Azure endpoint URL validation | MEDIUM | `llm_evaluate.py` | Validate scheme+netloc on startup |
| B6 | `datetime.utcnow()` deprecated (Python 3.12+) | LOW | `llm_evaluate.py:616` | `datetime.now(timezone.utc)` |
| B7 | No `KeyboardInterrupt` handler in batch loop | MEDIUM | `run_eval_batch.py` | try/except in main loop |

---

### 1.5 March 18 Meeting — Strategic Decisions (Day 2 Update)

**Attendees:** Gal Oren, Samyak, Erel Kaplan, Niranjan Hasabnis, Le Chen, Tomer Bitan

#### New Tasks from Meeting (M1–M10)

| Task | What | Source | Priority | Effort |
|------|------|--------|----------|--------|
| **M1** | Create anonymous "ParBench" GitHub + mirror site | Gal (00:04:23) — SC26 anon submission | HIGH | 2-3h |
| **M2** | Add curation survey page to website | Gal (00:05:52) — "what pool, why this subset?" | HIGH | 3-4h |
| **M3** | Read Paraval paper (baseline comparison) | Gal (00:12:55) — differentiate clearly | HIGH | 2h |
| **M4** | Create paper outline BEFORE writing | Gal + Niranjan — structure first | CRITICAL | 3-4h |
| **M5** | Clone ExaBench/XSBench for Paraval comparison | Gal (00:34:39) — specific kernel only | MEDIUM | 3-4h |
| **M6** | Implement kernel + host-transfer timing metrics | Niranjan (00:16:18) — three-tier model | HIGH | 4-6h |
| **M7** | Set up Llama 70B + leaderboard model via Groq/Modal | Team (00:18:20) | HIGH | 3-4h |
| **M8** | Select third model from coding leaderboard | Le Chen (00:21:41) | HIGH | 1h |
| ~~**M9**~~ | ~~Cherry-pick `erel/aug` augmentation fixes → main~~ | Erel's branch analysis | ~~CRITICAL~~ | **DONE Day 2** |
| ~~**M10**~~ | ~~Verify augmentation L1–L4 after M9 merge~~ | Depends on M9 | ~~HIGH~~ | **DONE Day 2** |

#### Paper Structure (Gal + Niranjan, 00:26:54–00:33:34)

SC26 = double-column, 10 pages + appendices. Draft must exist before next meeting.

1. **Introduction** — "What should be benchmarked for LLM parallel code translation?"
2. **Related Work** — CRITICAL. Compare Paraval, ParEval, ExaBench. Show LLM perf across benchmarks.
3. **Benchmark Curation** — Survey → mapping → subset selection. WHY Rodinia + HeCBench.
4. **Framework** — ParBench schema, harness pipeline, augmentation
5. **Experimental Setup** — Non-reasoning models, augmentation levels, translation directions
6. **Results** — Pass rates, failure taxonomy, augmentation impact, self-repair
7. **Discussion / Conclusion**

#### Timing Metrics — Three-Tier Model (Niranjan, 00:16:18)

- **Tier 1:** Kernel execution time — GPU kernel only (`nvprof`/`ncu` for CUDA, `omp_get_wtime()` for OMP)
- **Tier 2:** Kernel + host memory transfer — includes `cudaMemcpy`, `cudaMalloc`
- **Tier 3:** Wall-clock — includes I/O (NOT suitable for speedup claims)

**Report Tiers 1 and 2.** Not Tier 3. Adopt ParaCodex GPU time matrix methodology.

#### Benchmark Scope (simplified, Gal 00:26:54)

- **Rodinia + HeCBench** — primary (confirmed)
- **ExaBench/XSBench** — one specific kernel for Paraval comparison ONLY (Task M5)
- **No third full suite** — "create the outline first and see where the gaps are" (Niranjan)
- Task 3F (New Benchmark Suite) → **DEPRIORITIZED**

#### Augmentation Plan (Gal, 00:11:42)

- Conservative augmentation (L1–L2) is sufficient for paper
- L3–L4: future work if bugs persist
- Bug fixes on `erel/aug` branch → cherry-pick via Task M9 **(DONE Day 2)**

#### Other Decisions

- **Omit build times** from paper (team, 00:03:03)
- **Name: "ParBench"** confirmed (not "Powerbench")
- **Next meeting goal:** Gal wants a paper draft to revise together
- Phase 1 eval estimate: ~21 kernels × 1 model × 3 levels = ~63 calls
- Phase 2 eval estimate: ~21 kernels × 3 models × 3 levels = ~189 calls

---

### 1.6 Day 2 (March 19) — Completion Summary

#### Completed Tasks

| Task | Description | Status |
|------|-------------|--------|
| **M9** | Cherry-picked Erel's `erel/aug` augmentation fixes into main: Bug A/B/C fixes, `ChangeFunctionNames` transform, `LEVEL_FRACTIONS`/`_select_fraction()`, `_greedy_valid_subset()`, `_contains_side_effects()`, `filename` param threading, OMP pragma awareness helpers, UTF-8 safety in `_source_text()`. All 11 unit tests pass. | DONE |
| **M10** | Verified augmentation L1/L3/L4 all PASS on srad-cuda and backprop-cuda (seed=42). `PointerArithmeticToArrayIndex` doesn't fire on any Rodinia CUDA spec. **DONE (spot-check only — 2/60 specs).** Full 60-spec retest planned (M10b). Pre-M9 results on disk (March 10–11) cannot be cited as post-fix evidence. | DONE (spot-check) |
| **2B** | `--augment-levels` flag added to `run_eval_batch.py`. Each level generates separate tasks with result files tagged `-L1`, `-L2`, etc. (L0 has no tag). `.cl` suffix fix applied in both `spec_loader.py` and `augment_verify.py`. | DONE |
| **2G** | `analyze_eval.py` created — aggregates all result JSONs into `eval_summary.json`, `eval_summary.md`, and `eval_results_data.js` (via `--write-dashboard`). `--show-gaps` prints missing combinations. | DONE |
| **Pilot eval** | 10-kernel pilot with `azure-gpt-4.1` at L0 cuda-to-omp. **6/10 PASS (60%).** PASS: bfs, hotspot, lud, nn, nw, pathfinder. BUILD_FAIL: backprop, kmeans, srad, streamcluster. | DONE |
| **Spec fixes** | `nn-omp`: `filelist.txt` changed to `filelist_4` (FIXED). `gaussian-omp`: `working_directory` broken — no `openmp/gaussian` in Rodinia repo (BUG FOUND, not yet fixed). | DONE |
| **Frontend** | All 9 visualization pages converted to unified light academic theme (Inter + JetBrains Mono fonts, Okabe-Ito colorblind-safe palette, Chart.js v4, print stylesheets, Option C logo). `DESIGN.md` created as canonical design spec. | DONE |
| **Repo cleanup** | Stale git worktrees removed (agent-a6f3eb01, agent-af148208). Rodinia submodule corruption fixed (backprop.c, hotspot_openmp.cpp, needle.cpp restored). Quality standards added to CLAUDE.md. | DONE |

#### Key Finding: Multi-File Structural Mismatch (M11 — RESOLVED 2026-03-22)

3 of 4 BUILD_FAILs in the 10-kernel pilot were **structural**: the LLM was asked to
replicate the OMP target's file structure, conflating translation quality with code
restructuring skill.

- **Documented in:** `docs/design_concern_multifile_translation.md` (Section 10: team decision)
- **Status:** RESOLVED — Kernel-Centric Translation + Complexity Classification
- **Architecture:** `docs/design/kernel_centric_translation.md`
- **Implementation:** Task M11-IMPL / SESSION 1.5
- **Affected kernels:** backprop (4→1 file), kmeans (8→1 file), streamcluster (2→1 file)

#### Updated Pilot Results (10 kernels, azure-gpt-4.1, L0, cuda-to-omp)

> ⚠️ **SUPERSEDED by kernel-centric v2 results (Sessions 2–3b, March 22–24).** The 4 BUILD_FAILs below were caused by the old full-project pipeline. All are now resolved under kernel-centric translation. Use `results/evaluation/eval_summary.json` for current data (68 results, 4 models, 44.1% aggregate PASS rate).

| Kernel | Result | Failure Root Cause |
|--------|:------:|-------------------|
| bfs | **PASS** | — |
| hotspot | **PASS** | — |
| lud | **PASS** | — |
| nn | **PASS** | — |
| nw | **PASS** | — |
| pathfinder | **PASS** | — |
| backprop | BUILD_FAIL | Multi-file structural mismatch (M11) |
| kmeans | BUILD_FAIL | Multi-file structural mismatch (M11) |
| srad | BUILD_FAIL | LLM drops `nthreads` arg |
| streamcluster | BUILD_FAIL | Multi-file structural mismatch (M11) |

#### Pending After Day 2

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| **M11** | CRITICAL | **RESOLVED (2026-03-22)** | Team decision: kernel-centric translation + complexity classification (Erkap: Option B, Niranjan: kernel-file-only). Architecture: `docs/design/kernel_centric_translation.md`. Implementation: SESSION 1.5. |
| **M4** | CRITICAL | Not started | Paper outline — must exist before next meeting |
| **M1** | HIGH | Not started | Anonymous ParBench GitHub — required for SC26 submission |
| **M2** | HIGH | Not started | Curation survey page for website |
| **M3** | HIGH | Not started | Read Paraval paper for differentiation |
| **M7** | HIGH | **RESOLVED (2026-03-23)** | groq-llama-3.3-70b-versatile via Groq API (Session 3 complete, 5/17 PASS) |
| **M8** | HIGH | **RESOLVED (2026-03-23)** | gemini-2.5-flash-lite selected (Session 3b complete, 4/17 PASS) |
| **M5** | MEDIUM | **DONE (2026-03-23)** | XSBench cloned (commit ba08e52), 4 specs generated, 4/4 PASS. Eval-ready: cuda, omp, opencl. |
| **M6** | HIGH | Session prompt ready (SESSION 6.5) | nsys Tier 1 kernel time for CUDA/OMP-target; session prompt in docs/session_prompts_sc26.md |
| **2A** | HIGH | Not started | Iterative repair pilot (`--max-retries 3`) |
| **2C** | HIGH | Not started | Smoke test all 22 OMP specs |
| **2D** | HIGH | Partially done | Full Rodinia cuda-to-omp eval — 10/21 kernels done |
| **HeCBench** | MEDIUM | Blocked | Not cloned locally — blocks 120 specs |

---

### 1.7 Day 3 (March 20) — Completion Summary

#### Completed Tasks

| Task | Description | Status |
|------|-------------|--------|
| **G1** | Added 4 `ChangeFunctionNames` unit tests to `test_transforms.py`. Test run exposed a bonus pre-existing bug: `_string_literals_in_file` initialized `values = []` (list) instead of `set()`, silently breaking the OpenCL kernel-name safety guard via swallowed `AttributeError`. Fixed. All 15 tests now pass. | DONE |
| **G2** | Fixed `filename` kwarg threading in 2 production call sites: `augment_dataset.py:augment_sample()` and `harness/spec_loader.py:get_prompt_payload()`. Previously, `.cu` and `.cl` files were parsed by libclang as `.cpp` (no CUDA/OpenCL language extensions), potentially misidentifying kernel entry points. `augment_verify.py` was already correct. | DONE |
| **FE** | Full website revamp: shared `theme.css`, unified nav, Okabe-Ito palette across all visualization pages. Sprint dashboard Kanban updated: G1/G2 added as done, M10b added as in-progress, burndown updated to 24 tasks. | DONE |

#### Gaps Discovered During M9 Audit

The Day 3 work was driven by a 5-agent deep audit of M9, which found two gaps:

- **G1 (ChangeFunctionNames untested)**: 260 lines of new transform code had zero unit tests. The act of writing tests exposed the `_string_literals_in_file` bug — classic "tests are a forcing function for correctness".
- **G2 (filename not threaded)**: Two of three `augment_code` call sites omitted `filename=`. The `augment_verify.py` path (the one used for M10 smoke tests) was the one that worked correctly. The harness prompt path and JSONL batch path were silently broken.

#### M10 Reassessment

M10 was previously marked DONE, but the audit found:
- Only `srad-cuda` and `backprop-cuda` were re-run post-M9 (2 of 60 specs)
- All augmentation results on disk are dated March 10–11 (8+ days before M9 merge)
- The `augment_verify.py` path passes `filename=` correctly, so those 2 re-runs were valid
- Full 60-spec retest (M10b) launched on Day 3 with seed=42 post-G2 fix

#### Pending After Day 3

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| **M10b** | HIGH | DONE | Full 65-spec retest complete (2026-03-20). 48/65 PASS (73%) at ALL levels — level-invariant. 17 failures are pre-existing spec/build issues, not transform-caused. |
| **M10b-fixes** | HIGH | DONE | Post-mortem on 17 M10b failures. 5 phantom specs deleted (65→60). 8 specs fixed: hotspot-omp/nw-omp (wrong args restored), nn-cuda (filelist_4), cfd-cuda (helper_cuda.h), cfd-opencl (C++14 NULL + OpenCL version), mummergpu-cuda/omp (unistd.h), pathfinder-opencl (data rename + OpenCL version). 4 KNOWN_FAIL documented: kmeans-cuda, hybridsort-cuda, nn-opencl, kmeans-opencl. Target: **56/60 PASS (93%).** Retest pending. |
| **G3** | LOW | Pending | Consider removing `try/except Exception: pass` in `_string_literals_in_file` (masks future bugs) |
| *(all Day 2 pending items remain)* | | | |

---

### 1.8 Days 4–7 (March 21–24) — Completion Summary

#### Completed Sessions (all verified against git history + on-disk data)

| Session | Description | Commit | Date | Key Result |
|---------|------------|--------|------|-----------|
| **S1** | Rodinia submodule reset + build-flag alternatives | `cfa1991` | 03-21 | 54/60 PASS; 6 KNOWN_FAIL documented |
| **S1.5** | Kernel-centric pipeline (M11) + translation_targets | `c2b63fd` | 03-22 | Schema + eval pipeline; 60 Rodinia specs populated |
| **S1.6** | Universal standardization (all 184 specs) | `35b9c8e` | 03-22 | All 184 specs have translation_targets; full_project removed |
| **S2** | azure-gpt-4.1 cuda-to-omp L0 | `3d43afa` | 03-22 | 9/17 PASS (52.9%) — kernel-centric clean slate |
| **S3** | groq-llama-3.3-70b-versatile cuda-to-omp L0 | `b644bc6` | 03-22 | 5/17 PASS (29.4%) |
| **S3-PM** | Post-mortem pipeline bug fixes | `dad1662` | 03-22 | 3 bugs fixed: EXTRACTION_FAIL, cross-attempt contamination, finish_reason |
| **S3b** | claude-sonnet-4-6 + gemini-2.5-flash-lite cuda-to-omp L0 | `887d681`/`f0b4f98` | 03-23/24 | Claude: 12/17 (70.6%), Gemini: 4/17 (23.5%) |
| **S4** | XSBench clone + spec generation | `78e379d` | 03-23 | 4 specs (cuda/omp/opencl/omp_target); no OpenACC |
| **S5** | XSBench harness verify | `888910f` | 03-23 | 4/4 PASS; baselines populated |
| **S6** | Paper outline (M4) | `257b992` | 03-23 | `docs/paper_outline.md` — 8 sections, F1-F6, T1-T9 |

#### Actual Evaluation Data on Disk (as of 2026-03-24)

- **68 result JSONs**: 4 models × 17 kernels × cuda-to-omp × L0 (all `translation_mode: "kernel_centric"`)
- **Zero** augmented eval results (L1/L2/L3/L4) — S7 not yet run
- **Zero** omp-to-cuda, cuda-to-opencl, or any other direction results — S9/S10 not yet run
- **Zero** XSBench eval results — S8 not yet run
- **Zero** `kernel_time_seconds` data — `--use-profiler` is a no-op stub; all results use wall_time

#### M-Tasks Status Update (as of 2026-03-24)

| Task | Status | Notes |
|------|--------|-------|
| **M4** | **DONE (2026-03-23)** | Paper outline at `docs/paper_outline.md` (S6) |
| **M5** | **DONE (2026-03-23)** | XSBench 4/4 PASS; eval-ready: cuda, omp, opencl |
| **M6** | Session prompt ready | S6.5 session prompt exists; implementation pending (Day 8) |
| **M7** | **RESOLVED (2026-03-23)** | groq-llama-3.3-70b-versatile, 5/17 PASS |
| **M8** | **RESOLVED (2026-03-23)** | gemini-2.5-flash-lite selected + implemented, 4/17 PASS |
| **M11** | **DONE (2026-03-22)** | Kernel-centric pipeline live (S1.5 + S1.6) |
| **M3** | NOT STARTED | Samyak reads Paraval paper manually (blocks S12 related work) |

---

### 1.9 Day 8 (2026-03-25) — Status Update

#### Completed This Day (verified 2026-03-25)

| Session | Description | Commit | Date | Key Result |
|---------|------------|--------|------|-----------|
| **S8** | XSBench multi-API eval (L0-L4, 12 directions) | `096a309` | 03-25 | 180/180 files; marker confirmed; 3 models × 12 dirs × 5 levels |
| **W-S12** | Paper §3–§5 (Framework, Curation, Setup) | `5b22981`→merge `155a9fe` | 03-25 | 3289 words; 4 review commits; docs/paper/paper_sections_3_4_5.md |
| **W-S14** | Publication figures F2-F6 | `e0e88b7` (merged PR #4) | 03-24 | 5 PDF+PNG figures from L0 data in docs/paper/figures/ |
| **Day 8 setup** | Updated S7+W-S11 session prompts | `155a9fe` | 03-25 | S7 prompt: L1-L4, 3 models, all decisions resolved |

#### Currently Running (as of 2026-03-25)

| Session | Status | Lane | Notes |
|---------|--------|------|-------|
| **S7** | **IN PROGRESS** | GPU main checkout | Rodinia cuda-to-omp L1-L4, 3 models, 204 tasks (~6-10h) |
| **W-S11** | **IN PROGRESS** | Worktree (`worktree/s11-dashboard`) | Dashboard refresh; 248 result files on disk |

#### Actual Evaluation Data on Disk (as of 2026-03-25)

- **68 Rodinia result JSONs**: 4 models × 17 kernels × cuda-to-omp × L0 (azure=17, others=17 each)
- **180 XSBench result JSONs**: 3 models × 12 directions × 5 levels (L0-L4) — azure excluded
- **Total: 248 result files** — all `translation_mode: "kernel_centric"`
- **Zero** Rodinia L1-L4 augmented eval results — **S7 currently running to fill this gap**
- **Zero** Rodinia omp-to-cuda, cuda-to-opencl, or other directions — S9/S10/S10b pending
- **Zero** `kernel_time_seconds` — wall_time only; S6.5 deferred (paper is correctness-focused)

#### M-Tasks Update (Day 8)

| Task | Status | Notes |
|------|--------|-------|
| **M4** | **DONE** | Paper outline + §3-§5 draft complete |
| **M5** | **DONE** | XSBench 4/4 PASS + 180 eval results |
| **M6** | **DEFERRED** | Paper framed as correctness-only; no speedup claims; skip S6.5 |
| **M3** | NOT STARTED | Samyak reads Paraval paper — #1 blocker for §1-§2 |
| **M1** | NOT STARTED | Anonymous GitHub repo — blocked on account decision |

#### azure-gpt-4.1 NOTE (2026-03-25 permanent)

Azure GPT-4.1 deployment disabled by Gal. Has 17 Rodinia L0 cuda-to-omp results (9/17 PASS).
**Excluded from all future eval batches (S7, S9, S10, S10b, XSBench additional runs).**
Data retained for paper comparison table.

---

## 2. The Plan — Three Weeks

### Week 1 (March 18–24): Scale Up Rodinia + Iterative Repair

**Goal:** 5-kernel pilot → full 21-kernel Rodinia evaluation with iterative repair and augmentation.
**Actual achievement (Day 7):** 4-model L0 cuda-to-omp baseline complete (68 results). M11 resolved. XSBench added.

### Week 2 (March 25–31): Augmented Eval + Cross-Direction + Paper Draft

**Goal (revised Day 8):** Complete Rodinia L1-L4 augmented eval (S7), run cross-direction evals (S9/S10/S10b), refresh dashboard (W-S11), write paper §1-§5 (S12 + W-S12 done), begin §6-§8.
**Original goal (superseded):** Clone HeCBench, run HeCBench evaluation. *(HeCBench deferred — paper deadline takes priority. OpenACC descoped — no source exists.)*

### Week 3 (April 1–7): Paper + Final Results + Polish

**Goal:** Final results, SC26 paper draft, publication-quality visualizations.

---

## 3. Week 1 — Detailed Task Breakdown

### Day 0 (Before Day 1): M11-IMPL — Implement Kernel-Centric Translation Pipeline

#### Task M11-IMPL — Implement Kernel-Centric Translation Pipeline (NEW — 2026-03-22)

**Prerequisite:** Session 1 complete (Rodinia submodule reset, 54 PASS specs verified)
**Session prompt:** SESSION 1.5 in `docs/session_prompts_sc26.md`
**Design doc:** `docs/design/kernel_centric_translation.md`
**Background:** M11 resolved (team decision 2026-03-22). Architecture doc contains
source-verified `translation_targets` for all 60 Rodinia specs.

**Changes required (documentation-only until SESSION 1.5):**

| File | Change | Purpose |
|------|--------|---------|
| `schema/spec_schema.json` | Add `files.translation_targets` (optional array), `metadata.translation_complexity` (enum) | Schema for new fields |
| `scripts/validate_schema.py` | Add subset validation: `translation_targets` ⊆ `prompt_payload` | Prevent stale references |
| `harness/spec_loader.py` | Add `translation_targets` to `resolve_paths()` resolved dict | Path resolution |
| `scripts/evaluation/llm_evaluate.py` | Use `translation_targets` in `build_translation_prompt()` + `evaluate_translation()`. Add "Target Infrastructure Context" section to prompt. Add `translation_mode` to result JSON | Core pipeline change |
| ~~`scripts/evaluation/populate_translation_targets.py`~~ | ~~New script: populate all 60 Rodinia specs with `translation_targets`.~~ **Superseded in Session 1.6** → replaced by `scripts/generators/standardize_specs.py` (universal, all suites). File deleted. | Spec population |
| `scripts/evaluation/classify_translation_pairs.py` | New script: compute complexity class for each translation pair → CSV | Complexity reporting |
| `scripts/evaluation/analyze_eval.py` | Add "Pass Rate by Translation Complexity" section | Stratified reporting |
| `specs/*.json` (60 Rodinia specs) | Add `translation_targets` and `translation_complexity` fields | All specs updated |
| `results/evaluation/translation_complexity.csv` | New file: kernel × src_api × tgt_api × complexity_class | Paper data |

**Deliverable:** All 60 specs have `translation_targets`. Dry-run shows reduced target files:
- `backprop`: 4 files → 1 file (`backprop.c`)
- `kmeans`: 8 files → 1 file (`kmeans_openmp/kmeans_clustering.c`)
- `hotspot-opencl`: 1 source → 2 files (`.cl` + `.c`)

**Impact on subsequent sessions:**
- SESSION 2 must delete all azure-gpt-4.1 cuda-to-omp results before re-running (clean slate)
- All eval sessions (S2, S3, S7, S9, S10) use kernel-centric pipeline
- Previous 10-kernel pilot results are obsolete (v1 data, mixed paradigm)

---

### Day 1–2 (March 18–19): Bug Fixes + Iterative Repair Pilot

#### Task 2A — Iterative Repair Pilot

**No code changes needed.** The retry mechanism is fully implemented but untested with retries > 1.

**Steps:**
1. Delete stale results for failing kernels (to force re-evaluation):
```bash
source env_parbench/bin/activate
rm results/evaluation/claude-sonnet-4-20250514/rodinia-{hotspot,srad,backprop}-cuda-to-*.json
rm results/evaluation/azure-gpt-4.1/rodinia-{srad,backprop}-cuda-to-*.json
```

2. Re-run with `--max-retries 3`:
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --kernels hotspot srad backprop \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam -v
```
> **Phase 2 (when Groq/Modal ready):** add `llama-70b <leaderboard-model>` to `--models`

3. Record self-repair outcomes:

| Failure | Expected Self-Repair Likelihood | Why |
|---------|:-------------------------------:|-----|
| hotspot-claude (missing `#include <cstring>`) | **HIGH** | Trivial compile error, LLM should add include |
| srad (both: wrong argc) | **MEDIUM** | LLM must add `nthreads` param — requires understanding OMP vs CUDA args |
| backprop (both: multi-file conflicts) | **LOW** | Complex linker issues across multiple files |

**Deliverable:** Updated result JSONs with `total_attempts > 1`. Self-repair success rate.

---

#### Task 2B — Add `--augment-levels` to Batch Runner — DONE (Day 2)

**File:** `scripts/evaluation/run_eval_batch.py` (~15 lines of changes)

**Implementation plan:**
1. Add CLI flag:
   ```python
   parser.add_argument('--augment-levels', type=int, nargs='+', default=[0],
                        help='Augmentation levels to test (default: [0])')
   ```

2. Expand task matrix in `_build_tasks()`:
   - Current: `(source, target, model)` triples
   - New: `(source, target, model, augment_level)` quadruples
   - For each existing triple, iterate over `args.augment_levels`

3. Pass augment_level to `evaluate_translation()`:
   ```python
   result = evaluate_translation(
       ...,
       augment_level=task["augment_level"],
       ...
   )
   ```

4. Update result file path to include augment level:
   - Current: `results/evaluation/{model}/{src}-to-{tgt}.json`
   - New: `results/evaluation/{model}/L{aug}/{src}-to-{tgt}.json`
   - For L0, keep existing path (backward compatible): `results/evaluation/{model}/{src}-to-{tgt}.json`

5. Add `augment_level` column to Markdown report in `_generate_markdown()`.

**Deliverable:** Working `--augment-levels` flag. Smoke test with `--augment-levels 0 2 --kernels bfs --direction cuda-to-omp`.

---

#### Task 2E — Cleanup

1. Delete stale batch summaries:
```bash
rm results/evaluation/batch_cuda-to-omp_20260317_*.json
rm results/evaluation/batch_cuda-to-omp_20260317_*.md
```

2. Delete stray HeCBench result (from cross-suite name collision — demonstrates why `--suite` is mandatory):
```bash
rm -f results/evaluation/claude-sonnet-4-20250514/hecbench-nw-cuda-to-hecbench-nw-omp.json
```

3. Add to `.gitignore`:
```
# Batch summary files (regenerated per run; per-task JSONs are the source of truth)
results/evaluation/batch_*.json
results/evaluation/batch_*.md
```

4. Delete stale task reports (superseded by session_report):
```bash
rm results/evaluation/task2_completion_report.md
rm results/evaluation/task2_research_report.md
```

---

#### Task 2F — Minor Bug Fixes (Day 1–2)

Fix these in a single commit:

| Bug | Fix | File | Lines |
|-----|-----|------|-------|
| B6 | `datetime.utcnow()` → `datetime.now(timezone.utc)` | `llm_evaluate.py` | ~1 line |
| B7 | Wrap batch loop in `try/except KeyboardInterrupt` | `run_eval_batch.py` | ~5 lines |
| B4 | Validate Azure endpoint URL on startup (check scheme + netloc) | `llm_evaluate.py` | ~5 lines |
| B1 | Add `"kernel"` field to result dict | `llm_evaluate.py` | ~1 line |
| B2 | Fix `_generate_markdown()` result iteration | `run_eval_batch.py` | ~3 lines |

---

### Day 3–4 (March 20–21): Smoke Test All 21 OMP Specs

#### Task 2C — Verify All Rodinia OMP Specs

**Goal:** Ensure every Rodinia OMP spec builds, runs, and verifies before sending to LLM evaluation.

```bash
source env_parbench/bin/activate
for k in backprop bfs bptree cfd gaussian heartwall hotspot hotspot3d \
         huffman hybridsort kmeans lavamd lud mummergpu myocyte nn nw \
         particlefilter pathfinder srad streamcluster; do
  echo "=== rodinia-${k}-omp ==="
  python3 -m harness -v verify "specs/rodinia-${k}-omp.json" 2>&1 | tail -5
  echo ""
done
```

**Budget time for debugging.** Expect 3–5 specs to need fixes. Common patterns from prior experience:
- Missing data files → create symlinks in `rodinia/rodinia-src/data/`
- Wrong run arguments → check OMP reference binary's `argc` expectation
- Build target name → `make <target>` instead of bare `make`
- Missing headers → `-I` include path like the needle.h fix
- Compiler flag issues → add `-std=c++14` or `-Wno-unused-result`

**Also smoke-test all CUDA specs** (these are the *source* for cuda→omp translation):
```bash
for k in backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d \
         huffman hybridsort kmeans lavamd lud mummergpu myocyte nn nw \
         particlefilter pathfinder srad streamcluster; do
  echo "=== rodinia-${k}-cuda ==="
  python3 -m harness -v verify "specs/rodinia-${k}-cuda.json" 2>&1 | tail -5
  echo ""
done
```

**Deliverable:** Updated spec files for any broken specs. A table of all 22 kernels × {cuda, omp} with PASS/FAIL status.

**Known failures to expect:**
- `rodinia-nn-cuda` and `rodinia-nn-omp` — reported baseline failures (runtime errors). Debug or exclude.
- Erel's 5 new specs (gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl) — source dirs may be missing (submodule at wrong commit).

---

### Day 4–5 (March 21–22): Full Rodinia cuda→omp Evaluation

#### Task 2D — Full Evaluation Matrix (Primary Direction)

**cuda→omp (primary):** All passing kernels × phased models × L0/L1/L2 × max-retries 2

```bash
# Phase 1: L0 (no augmentation) — GPT-4.1 only (Phase 1 models)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --augment-levels 0 \
  --max-retries 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v

# Phase 1: L1+L2 (augmented source) — GPT-4.1 only
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --augment-levels 1 2 \
  --max-retries 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v

# Phase 2: All levels — add open-source models once Groq/Modal set up (Task M7)
# python3 scripts/evaluation/run_eval_batch.py \
#   --suite rodinia --direction cuda-to-omp \
#   --models azure-gpt-4.1 llama-70b <leaderboard-model> \
#   --augment-levels 0 1 2 --max-retries 2 ...
```

**Estimated LLM calls:**
- Phase 1: ~21 kernels × 1 model × 3 levels × (1–2 attempts) ≈ 63–126 calls
- Phase 2: ~21 kernels × 3 models × 3 levels ≈ 189–378 calls

**Important:** Run in tmux:
```bash
tmux new-session -d -s eval_cuda_omp 'source env_parbench/bin/activate && python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp --models azure-gpt-4.1 --augment-levels 0 1 2 --max-retries 2 --project-root /home/samyak/Desktop/parbench_sam --resume -v 2>&1 | tee results/evaluation/run_cuda_omp.log'
```

---

### Day 5–6 (March 22–23): Additional Directions

#### Task 2D continued — omp→cuda and cuda→opencl

```bash
# omp→cuda
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction omp-to-cuda \
  --models azure-gpt-4.1 \
  --augment-levels 0 --max-retries 2 \
  --project-root /home/samyak/Desktop/parbench_sam --resume -v

# cuda→opencl
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-opencl \
  --models azure-gpt-4.1 \
  --augment-levels 0 --max-retries 2 \
  --project-root /home/samyak/Desktop/parbench_sam --resume -v
```
> Add open-source models to `--models` once Task M7 (Groq/Modal setup) is complete.

**Estimated calls:** ~43 pairs × 2 models × 1 level ≈ 86 calls

---

### Day 7 (March 24): Week 1 Results Analysis

1. Run `scripts/evaluation/analyze_eval.py` (created Day 2) — aggregate all result JSONs into:
   - `results/evaluation/eval_summary.md` — full results matrix
   - `results/evaluation/eval_summary.json` — machine-readable aggregate
   - `visualizations/eval_results_data.js` — dashboard data (via `--write-dashboard`)

2. Update GitHub Pages dashboard

3. Commit all results with clear commit message

4. Generate the following tables for the paper:
   - Pass rate by (model × direction × augment_level)
   - Pass rate by kernel complexity
   - Failure taxonomy (BUILD_FAIL vs RUN_FAIL vs VERIFY_FAIL counts)
   - Self-repair rate (attempt 1 vs attempt 2 pass rate)

---

## 4. Week 2 — Detailed Task Breakdown

### Day 8 (March 25): Clone HeCBench

1. Clone the repo:
```bash
cd /home/samyak/Desktop/parbench_sam
git clone https://github.com/zjin-lcf/HeCBench.git HeCBench-master
```

2. Verify `config/paths.json` — `hecbench_root` already set to project root. Check that 120 HeCBench specs now resolve:
```bash
python3 scripts/validate_schema.py --all 2>&1 | grep -c "source_dir.*not found"
# Should drop from 120 to near 0
```

3. **Do NOT commit HeCBench-master/ to git** — it's huge. Add to `.gitignore`:
```
HeCBench-master/
```

---

### Day 8–9 (March 25–26): HeCBench Smoke Tests

1. Pick 5 representative HeCBench kernels with simple CUDA code:
```bash
# Candidates (verify these exist and have both cuda + omp variants):
# atomicIntrinsics, backprop, bfs, bezier-surface, binomial
for k in atomicIntrinsics backprop bfs bezier-surface binomial; do
  echo "=== hecbench-${k}-cuda ==="
  python3 -m harness -v verify "specs/hecbench-${k}-cuda.json" 2>&1 | tail -5
  echo "=== hecbench-${k}-omp ==="
  python3 -m harness -v verify "specs/hecbench-${k}-omp.json" 2>&1 | tail -5
done
```

2. Fix build issues — HeCBench Makefiles often need:
   - `CUDA_HOME` set to `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda`
   - SM arch flag (RTX 4070 = sm_89): `-arch=sm_89`
   - Possibly `-std=c++17` or `-std=c++14`

3. **Goal:** At least 5 HeCBench kernels fully passing (cuda + omp) before batch eval.

---

### Day 9–10 (March 26–27): HeCBench cuda→omp Evaluation

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite hecbench --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --augment-levels 0 --max-retries 2 \
  --project-root /home/samyak/Desktop/parbench_sam --resume -v
```

**Estimated calls:** Up to 60 kernels × 1 model (Phase 1) = 60 calls. Add open models in Phase 2. Many may fail at baseline (not all HeCBench specs have been smoke-tested). Use `--max-failures 10` to skip persistently broken kernels.

---

### Day 10–11 (March 27–28): Create OpenACC Specs

> **DESCOPED (2026-03-23):** No OpenACC source exists in Rodinia or XSBench. OpenACC specs
> are not being created. The section below is retained for historical context only.

**Decision tree:**

1. Check if Rodinia has OpenACC source:
```bash
# Check extended Rodinia repos
ls rodinia/rodinia-src/openacc/ 2>/dev/null
# Check if gpu-rodinia fork exists with OpenACC
```

2. **If OpenACC source exists:**
   - Generate specs using `/gen-spec` skill
   - Build commands use `nvc -acc -Minfo=accel -gpu=cc89`
   - Aim for 10–15 kernels

3. **If NO OpenACC source exists:**
   - Create "translate-only" specs: CUDA source as input, OpenACC as target
   - Verification strategy: BUILD success + RUN produces same stdout as CUDA reference
   - No reference binary needed — compare against CUDA stdout captured at baseline time
   - This is still valuable data: "Can LLM translate CUDA→OpenACC?"

**Build command template for OpenACC:**
```json
{
  "build": {
    "commands": {
      "build": "nvc -acc -Minfo=accel -gpu=cc89 -o {binary} {source_files}",
      "clean": "rm -f {binary}"
    }
  }
}
```

---

### Day 11–12 (March 28–29): Verify OpenMP Target Offload

**Quick verification:**
```bash
# Test if GCC offloading works
cat > /tmp/test_omp_target.c << 'EOF'
#include <stdio.h>
#include <omp.h>
int main() {
    int x = 0;
    #pragma omp target map(tofrom: x)
    { x = 42; }
    printf("x = %d (expect 42)\n", x);
    return (x == 42) ? 0 : 1;
}
EOF
gcc -fopenmp -foffload=nvptx-none /tmp/test_omp_target.c -o /tmp/test_omp_target
/tmp/test_omp_target
```

- **If it works:** Create `omp_target` specs for Rodinia kernels. New translation direction: `cuda→omp_target`.
- **If it doesn't:** Skip. Don't spend more than 2 hours on this.

---

### Day 12–13 (March 29–30): New Benchmark Suite (Stretch)

**Priority candidates (pick 1–2):**

| Suite | Kernels | APIs | Pros | Cons |
|-------|:-------:|------|------|------|
| **PolyBench/GPU** | ~30 | CUDA, OpenCL, OpenACC | Popular in literature; small kernels | May overlap with HeCBench |
| **Parboil** | 12 | CUDA, OpenCL, OpenMP | Well-studied; diverse algorithms | Older; may need Makefile updates |
| **NAS Parallel Benchmarks** | 8 | OpenMP, MPI | Impressive for papers; well-known | Larger codes; less granular |

**For each new suite:**
1. Clone source
2. Create specs using `/gen-spec <suite>` skill
3. Smoke test baselines
4. Run LLM evaluation pilot (5 kernels × 1 model)

---

### Day 14 (March 31): Week 2 Results Analysis

1. Re-run `scripts/evaluation/analyze_eval.py` with all new results
2. Update dashboard with HeCBench + new suite data
3. Commit everything
4. Generate cross-suite comparison tables

---

## 5. Week 3 — Detailed Task Breakdown

### Day 15 (April 1): Retest Augmentation

1. Erel's augmentation fixes cherry-picked into main on Day 2 (Task M9 — DONE). Verify tests still pass:
```bash
source env_parbench/bin/activate
python3 -m pytest c_augmentation/test_transforms.py -v
python3 scripts/augmentation/augment_verify.py specs/rodinia-bfs-cuda.json \
  --augment_level 2 --seed 42 -v --project-root /home/samyak/Desktop/parbench_sam
```

2. Re-run full augmentation batch:
```bash
python3 scripts/augmentation/run_augment_batch.py \
  specs/rodinia-*-cuda.json specs/rodinia-*-omp.json specs/rodinia-*-opencl.json \
  --levels 1 2 3 4 --seed 42 \
  --out results/augmentation/retest_2026-04-01 \
  --title "Post-Fix Augmentation Retest"
```

3. If L3/L4 pass rates improve significantly (>60%), add L3/L4 to the evaluation matrix.

---

### Day 15–16 (April 1–2): Final Evaluation Sweep

Fill any gaps in the results matrix:

```bash
# Check what's missing
python3 scripts/evaluation/analyze_eval.py \
  --results-dir results/evaluation/ \
  --show-gaps
```

Priority fills:
1. Any kernel × model × direction with 0 results
2. L1/L2 augmented runs for top-performing direction (probably cuda→omp)
3. If L3/L4 augmentation is fixed, run L3/L4 augmented evals on 5 pilot kernels

---

### Day 16 (April 2): Results Analyzer Script

Finalize `scripts/evaluation/analyze_eval.py` (created Day 2 — may need updates for new result formats):

**Input:** All `results/evaluation/{model}/**/*.json` files

**Output:**
1. `results/evaluation/eval_summary.json` — machine-readable:
```json
{
  "by_model": { "claude-sonnet-4": { "pass": 45, "total": 90, "rate": 0.50 } },
  "by_direction": { "cuda-to-omp": { "pass": 30, "total": 42, "rate": 0.71 } },
  "by_kernel": { "bfs": { "pass": 6, "total": 6, "rate": 1.00 } },
  "by_augment_level": { "L0": { "pass": 40, "total": 80, "rate": 0.50 } },
  "failure_taxonomy": { "BUILD_FAIL": 25, "RUN_FAIL": 10, "VERIFY_FAIL": 5 },
  "self_repair": { "attempt_1_pass": 40, "attempt_2_pass": 8, "total_repaired": 8 }
}
```

2. `results/evaluation/eval_summary.md` — publication-ready tables

3. `visualizations/eval_results_data.js` — dashboard data

---

### Day 17 (April 3): Publication-Quality Visualizations

Create or update these visualizations (can be matplotlib/seaborn scripts or enhanced HTML):

1. **Heatmap:** Kernel × Model pass/fail for cuda→omp (primary result)
2. **Bar chart:** Pass rate by translation direction
3. **Grouped bar chart:** L0 vs L1 vs L2 pass rates by model
4. **Stacked bar:** Failure taxonomy (BUILD_FAIL / RUN_FAIL / VERIFY_FAIL) by model
5. **Line chart:** Self-repair curve (pass rate vs attempt number)
6. **Table:** Per-kernel speedup ratios for passing translations

**Script:** `scripts/evaluation/generate_paper_figures.py` → outputs to `docs/paper/figures/`

---

### Day 18–19 (April 4–5): SC26 Paper Draft

Write paper sections as Markdown in `docs/paper/` (to be transferred to Overleaf):

| Section | File | Content |
|---------|------|---------|
| 1. Introduction | `01_introduction.md` | LLM code translation needs benchmarks; existing benchmarks don't cover parallel code |
| 2. Background | `02_background.md` | Parallel programming models, LLM code generation, related work |
| 3. Benchmark Corpus | `03_benchmark_corpus.md` | Survey of 35 repos, 656 kernels, selection rationale, ParBench design |
| 4. ParBench Framework | `04_framework.md` | Schema design, harness pipeline, augmentation system |
| 5. Experimental Setup | `05_experimental_setup.md` | Models, translation directions, augmentation levels, hardware |
| 6. Evaluation Results | `06_evaluation.md` | Pass rates, speedup analysis, augmentation impact, failure taxonomy |
| 7. Discussion | `07_discussion.md` | What makes translations fail, model comparison, augmentation effectiveness |
| 8. Conclusion | `08_conclusion.md` | Summary, limitations, future work |

**Data sources for Section 6:**
- `results/evaluation/eval_summary.json` — all LLM translation results
- `results/augmentation/full_aug_results.json` — augmentation pass rates
- `analysis/data/` — survey data (35 repos, 656 kernels)
- `presentations/ParBench_Speaking_Notes.md` — prior narrative

---

### Day 20 (April 6): Review and Polish

1. Cross-check all numbers in paper against result JSONs
2. Ensure all tables are internally consistent
3. Proofread all sections
4. Add figure references and captions
5. Run final `validate_schema.py --all`
6. Final commit and push

---

### Day 21 — April 7 (April 8 = Deadline Day)

1. Transfer Markdown to Overleaf LaTeX
2. Final formatting (SC26 template)
3. Generate PDF, review
4. Submit

---

## 6. Expected Paper Data Points

By April 8, target these numbers:

| Metric | Target | Stretch |
|--------|:------:|:-------:|
| Translation pairs evaluated | 300+ | 500+ |
| Benchmark suites | 3 (Rodinia + XSBench + HeCBench) | XSBench DONE (2026-03-23, 4/4 PASS) |
| Models compared | 4 (GPT-4.1, Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, Llama 3.3 70B) | **All 4 have L0 data** (Sessions 2/3/3b, 2026-03-24) |
| Augmentation levels tested | L0, L1, L2 | + L3, L4 |
| Translation directions | 3 (cuda↔omp, cuda→opencl) | 5–6 (+omp_target, cross-API) |
| APIs covered | 3 (CUDA, OMP, OpenCL) | 4 (+OMP target, case study) |

**Key results to report:**
- Pass rate by model, direction, kernel complexity
- Augmentation impact: L0 vs L1/L2 (does augmentation help or hurt LLM translation?)
- Iterative repair: 1-attempt vs 2–3-attempt pass rates (self-repair effectiveness)
- Failure taxonomy: build vs run vs verify, with common patterns
- Speedup analysis: translated code performance vs reference implementation

---

## 7. Open Questions for Team

> Updated 2026-03-19 after March 18 meeting — resolved questions struck through.

1. ~~**Rodinia OpenACC source:** Does `gpu-rodinia` repo or Rodinia 3.1 have OpenACC implementations?~~ **RESOLVED (2026-03-23):** No OpenACC source exists in Rodinia or XSBench. OpenACC fully descoped from paper.

2. ~~**Which additional benchmarks?**~~ RESOLVED: Rodinia + HeCBench primary; ExaBench/XSBench ONE kernel for Paraval comparison (Task M5). No third full suite.

3. **HeCBench clone size/time:** HeCBench is large (~500+ benchmarks, several GB). Any subset preference, or clone all?

4. ~~**Erel's augmentation fixes:**~~ RESOLVED: Cherry-picked from `erel/aug` into main (Task M9, Day 2). All 11 tests pass. L1-L4 stable.

5. **Paper venue confirmation:** SC26 confirmed? Workshop paper or full paper track? (Gal mentioned 10 pages double-column + appendices)

6. **Overleaf:** Has Erel created the Overleaf project and shared the link?

7. **Submodule sync:** Erel's 5 new specs need Rodinia submodule at commit `b0310d8`. When can we sync?

8. ~~**Third model selection (Task M8):**~~ **RESOLVED (2026-03-23):** Final model set = GPT-4.1, Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, Llama 3.3 70B (Gal directive). Provider implemented. All 4 models have L0 cuda-to-omp baselines (68 total results).

9. ~~**Groq/Modal access (Task M7):**~~ **RESOLVED (2026-03-23):** Groq API operational. groq-llama-3.3-70b-versatile evaluated in Session 3 (5/17 PASS). No Modal GPU pool needed.

10. **Anonymous ParBench GitHub (Task M1):** Create before next meeting — required for SC26 anonymous submission.

11. **Multi-file structural mismatch (Task M11, Day 2):** 3/4 pilot BUILD_FAILs are caused by LLM inability to produce files in subdirectory paths. Three options documented in `docs/design_concern_multifile_translation.md`. Awaiting Gal/Erel Discord response. **CRITICAL for improving pass rates beyond 60%.**

---

## 8. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| HeCBench specs don't build on our hardware | HIGH | MEDIUM | Budget 2 days for Makefile fixes; accept < 100% coverage |
| Augmentation L3/L4 still broken | MEDIUM | LOW | Focus paper on L0/L1/L2; mention L3/L4 as future work |
| OpenMP target offload not available | MEDIUM | LOW | Skip; focus on CUDA/OMP/OpenCL *(OpenACC descoped 2026-03-23)* |
| LLM API rate limits or outages | LOW | HIGH | Use `--resume` flag; spread runs over days; both providers as backup |
| Paper writing takes longer than planned | MEDIUM | HIGH | Start Section 3 (corpus) and Section 4 (framework) early — they don't depend on results |
| New benchmark suite too complex to integrate | MEDIUM | LOW | Mark as stretch goal; 2 suites (Rodinia + HeCBench) is sufficient for SC26 |

---

## 9. Critical File Reference

| File | Role | Lines |
|------|------|:-----:|
| `scripts/evaluation/run_eval_batch.py` | Batch runner — add augment flag, run all evaluations | 444 |
| `scripts/evaluation/llm_evaluate.py` | Core LLM evaluation engine | 1162 |
| `scripts/evaluation/analyze_eval.py` | Results aggregator (CREATED Day 2) | — |
| `scripts/augmentation/augment_verify.py` | Augmentation pipeline | — |
| `scripts/augmentation/run_augment_batch.py` | Augmentation batch runner | — |
| `c_augmentation/augment_dataset.py` | AST transforms (5 transforms) | 1225 |
| `harness/spec_loader.py` | Spec loading, prompt payload extraction | — |
| `harness/builder.py` | Build step | — |
| `harness/runner.py` | Run step | — |
| `harness/verifier.py` | Verify step | — |
| `specs/rodinia-*-{cuda,omp,opencl}.json` | All Rodinia specs | 65 files |
| `specs/hecbench-*-{cuda,omp}.json` | All HeCBench specs | 120 files |
| `config/paths.json` | Path configuration | — |
| `manifest.jsonl` | Spec manifest (185 entries) | 185 |
| `visualizations/eval_results_data.js` | Dashboard data | — |
| `.claude/rules/evaluation.md` | Pipeline conventions and gotchas | — |
| `.claude/rules/known-issues.md` | All known bugs and workarounds | — |

---

## 10. Session Entry Point

**Copy-paste this block at the start of every Claude Code session:**

```
Read the sprint plan: docs/sprint_to_SC26.md

Then:
1. source env_parbench/bin/activate
2. git log --oneline -5  (confirm we're on main, check latest commit)
3. Check what day of the sprint we're on (March 18 = Day 1)
4. Pick up from where the last session left off
5. Follow the task sequence for that day

Environment reminders:
- Project root: /home/samyak/Desktop/parbench_sam
- Python: python3 (never bare python)
- Harness: python3 -m harness -v verify specs/<name>.json
- Batch eval: python3 scripts/evaluation/run_eval_batch.py --suite rodinia ...
- ALWAYS pass --project-root /home/samyak/Desktop/parbench_sam
- ALWAYS pass --suite to batch runner (avoid cross-suite collisions)
- NEVER run evaluations in git worktrees (submodule is empty there)
```

---

## 11. Daily Checklist Template

Use this at the end of each working day:

```markdown
## Day N (Date) — End-of-Day Status

### Completed
- [ ] Task X: description (commit: abc1234)

### Blocked
- [ ] Task Y: reason

### Tomorrow
- [ ] Task Z: first thing

### Results Update
- Total evaluations: N
- Pass rate: X% (model breakdown: Claude Y%, GPT Z%)
- New failures discovered: (list)
- Augmentation impact: (summary)
```

---

## Appendix A: 17 Good Candidate Kernels (2+ Passing APIs at Baseline)

```
backprop:       cuda ✓  omp ✓  opencl ✓
bfs:            cuda ✓  omp ✓  opencl ✓
bptree:         cuda ✓  omp ✓  opencl ✓
dwt2d:          cuda ✓         opencl ✓
gaussian:       cuda ✓         opencl ✓
heartwall:      cuda ✓  omp ✓  opencl ✓
hotspot:        cuda ✓  omp ✓  opencl ✓
hotspot3d:      cuda ✓  omp ✓  opencl ✓
lavamd:         cuda ✓  omp ✓  opencl ✓
lud:            cuda ✓  omp ✓  opencl ✓
myocyte:        cuda ✓  omp ✓  opencl ✓
nn:             cuda ✓  omp ✓  opencl ✗  (runtime failures at baseline)
nw:             cuda ✓  omp ✓  opencl ✓
particlefilter: cuda ✓  omp ✓  opencl ✓
pathfinder:     cuda ✓  omp ✓  opencl ✗
srad:           cuda ✓  omp ✓  opencl ✓
streamcluster:  cuda ✓  omp ✓  opencl ✓
```

## Appendix B: LLM Translation Failure Patterns (from Pilot)

| Pattern | Kernels | Models | Category | Self-Repair? |
|---------|---------|--------|----------|:------------:|
| Missing `#include` for standard lib | hotspot | Claude | BUILD_FAIL | HIGH |
| LLM drops CLI argument (CUDA 8-arg → OMP 9-arg) | srad | Both | RUN_FAIL | MEDIUM |
| Duplicate function across multi-file translation | backprop | Claude | BUILD_FAIL | LOW |
| Undeclared macro from un-included header | backprop | Azure | BUILD_FAIL | MEDIUM |
| Invalid OMP pragma nesting | hotspot | Azure (prior run) | BUILD_FAIL | MEDIUM |
| Incomplete implementation (token truncation) | backprop | Azure (prior run) | BUILD_FAIL | HIGH (with retry) |

## Appendix C: Augmentation Transform Reference

| Transform | What it does | L1–L2 safe? | L3–L4 bugs? |
|-----------|-------------|:-----------:|:-----------:|
| SwapCondition | `a == b` → `b == a` | YES | Bug C: assignment-in-condition |
| ChangeNames | Rename variables/functions | YES | Minor: identifier collision edge cases |
| ArithmeticTransform | `a + b` → `b + a`, `a * 1` → `a` | YES | Rare false positives |
| PointerArithmeticToArrayIndex | `arr[i]` → `*((arr)+(i))` | Mostly | Bug A: overlapping candidates; Bug B: struct member precedence |
| TypedefExpansion | Expand typedef to underlying type | Mostly | Bug D: struct pointer member access |
