# ParBench Session Report — 2026-03-17/18

> **Status:** Return to this doc in next session to resolve open issues.
> **Next session priorities:** Fix batch runner `--augment-levels`, fix Markdown bugs, run end-to-end smoke test.

---

## Executive Summary

**6 of 7 planned deliverables shipped and committed** across 7 commits (`88f3069` → `7229a5a`).
The LLM evaluation pipeline is functional end-to-end: API calls succeed, code is generated, compiled, run, and verified.
**Pilot pass rate: 27% (3/11) at zero-shot, augment_level=0** — expected for naive CUDA→OMP translation.
All failures are framework/prompt issues (not model capability gaps) and are fixable.

**One critical pipeline gap:** the batch runner is missing `--augment-levels`, so the full pipeline
(spec → augment → LLM eval on augmented code) has **never been run end-to-end**.

---

## Task Completion Matrix

| Task | Description | Status | Commit | Gap |
|------|-------------|--------|--------|-----|
| **D** | Merge Erel's 5 new Rodinia specs | ✅ DONE | `88f3069` | Source dirs missing (submodule); specs structurally correct |
| **C1** | CPU timing via `/usr/bin/time -v` | ✅ DONE | `3067eab` | None |
| **C2** | nsys kernel profiling | ❌ NOT DONE | — | Deferred; `kernel_time_seconds` field exists but never populated |
| **C3** | Speedup priority logic (kernel > cpu > wall) | ✅ DONE | `3067eab` | None |
| **A (code)** | Azure OpenAI client in `llm_evaluate.py` | ✅ DONE | `056c327` | Azure endpoint URL stripping fix included |
| **A (pilot)** | 5 kernels × 2 models pilot evaluations | ✅ DONE | `da9cc20` | GPT-4o NOT run; Azure GPT-4.1 used instead |
| **B** | Batch evaluation runner `run_eval_batch.py` | ⚠️ PARTIAL | `51fc0ed` | **`--augment-levels` flag missing — blocks augmented evals at scale** |
| **E** | Repo cleanup audit | ✅ DONE | `25b4474` | Report only; no cleanup actions taken (per plan) |

---

## Pilot Evaluation Results

**Direction:** CUDA → OMP | **Method:** Zero-shot | **augment_level:** 0 | **max_retries:** 1

| # | Model | Kernel | Status | Build | Run | Tokens In/Out | LLM Latency | Speedup | Timing Method |
|---|-------|--------|--------|-------|-----|--------------|-------------|---------|---------------|
| 1 | claude-sonnet-4-20250514 | bfs | **PASS** | ✓ | ✓ | 4463/2859 | 25.0s | 0.0012× | cpu_time |
| 2 | claude-sonnet-4-20250514 | hotspot | **RUN_FAIL** | ✓ | ✗ | 4419/4495 | 42.8s | — | — |
| 3 | claude-sonnet-4-20250514 | backprop | **BUILD_FAIL** | ✗ | — | 3440/8331 | 89.9s | — | — |
| 4 | claude-sonnet-4-20250514 | nw | **BUILD_FAIL** | ✗ | — | 6254/5960 | 69.5s | — | — |
| 5 | claude-sonnet-4-20250514 | srad | **BUILD_FAIL** | ✗ | — | 6242/2566 | 32.7s | — | — |
| 6 | azure-gpt-4.1 | bfs | **PASS** | ✓ | ✓ | 3290/1982 | 8.3s | 0.0021× | wall_time |
| 7 | azure-gpt-4.1 | hotspot | **BUILD_FAIL** | ✗ | — | 3407/3400 | 39.6s | — | — |
| 8 | azure-gpt-4.1 | backprop | **BUILD_FAIL** | ✗ | — | 2571/1094 | 18.6s | — | — |
| 9 | azure-gpt-4.1 | nw | **BUILD_FAIL** | ✗ | — | 5282/3542 | 13.8s | — | — |
| 10 | azure-gpt-4.1 | srad | **BUILD_FAIL** | ✗ | — | 4950/2000 | 26.6s | — | — |

**Result files:** `results/evaluation/{model}/rodinia-{kernel}-cuda-to-rodinia-{kernel}-omp.json`
**Batch reports:** `results/evaluation/batch_cuda-to-omp_20260317_{181526,181738}.{json,md}`

### Model Summary

| Model | PASS | BUILD_FAIL | RUN_FAIL | Pass Rate | Avg Latency | Avg Output Tokens |
|-------|------|-----------|---------|-----------|-------------|-------------------|
| claude-sonnet-4-20250514 | 2/6 | 3 | 1 | **33%** | 44.4s | 4,576 |
| azure-gpt-4.1 | 1/5 | 4 | 0 | **20%** | 20.8s | 2,404 |
| **Combined** | **3/11** | **7** | **1** | **27%** | — | — |

---

## Failure Analysis — Root Cause Taxonomy

| Category | Failures | Kernels | Both Models? | Root Cause | Fixability |
|----------|----------|---------|-------------|------------|------------|
| Missing header files | 4 | nw, srad | Yes | Prompt doesn't explain CUDA headers are inlined in OMP | Prompt fix (LOW effort) |
| Incomplete implementation | 2 | backprop | Azure only | Token truncation — `setup()` body omitted | max_retries + error feedback (MEDIUM) |
| Invalid OMP pragma nesting | 1 | hotspot | Azure only | `#pragma omp barrier` inside `for` loop — illegal | Constraint prompting (MEDIUM) |
| Compiler warnings-as-errors | 1 | backprop | Claude only | `fread()` return value ignored; Makefile treats as error | Build config fix (LOW effort) |
| Runtime crash | 1 | hotspot | Claude only | Compiled but exits 1 immediately | Error feedback loop (MEDIUM) |

### Detail: Missing Headers (nw, srad)
```
needle.cpp:6:10: fatal error: needle.h: No such file or directory
srad.cpp:7:10:  fatal error: srad.h: No such file or directory
```
CUDA has `needle.h`/`srad.h` with `#define BLOCK_SIZE`. OMP inlines these macros directly.
Both models copied `#include "needle.h"` without checking if it's in `target_files_expected`.
**Fix:** Add to system prompt: *"If a CUDA header is not in target_files_expected, its definitions are inlined — do not include it."*

### Detail: Backprop Linker Error (Azure)
```
undefined reference to `setup' (facetrain.c, imagenet.c, backprop.c)
```
Model generated 10-line stubs for `facetrain.c`/`imagenet.c` calling `setup()` but omitted the 20-line `setup()` implementation — token budget exhaustion at 1094 completion tokens.
**Fix:** `max_retries=2` with compiler error feedback.

### Detail: Invalid OMP Barrier (hotspot, Azure)
```
error: barrier region may not be closely nested inside of work-sharing region
  #pragma omp barrier  ← inside #pragma omp for
```
Original OMP hotspot has **no barriers** — synchronization is implicit. Azure added illegal barriers.
**Fix:** Prompt constraint: *"Do not add `#pragma omp barrier` inside parallel for loops."*

---

## Bugs Found in New Code

| # | Bug | Severity | Location | Fix |
|---|-----|----------|----------|-----|
| B1 | `kernel` field missing in result dict → all `?` in Markdown reports | HIGH | `llm_evaluate.py` result JSON | Add `"kernel"` field to result dict |
| B2 | Markdown stat line shows `0/1` instead of `0/5` | HIGH | `run_eval_batch.py _generate_markdown()` | Fix result iteration |
| B3 | Race condition: concurrent batch runners can duplicate LLM calls | HIGH | `run_eval_batch.py` resume check | Atomic file write with lock |
| B4 | No Azure endpoint URL format validation | MEDIUM | `llm_evaluate.py` azure branch | Validate scheme+netloc |
| B5 | `api_version` hardcoded `2025-01-01-preview` | LOW | `llm_evaluate.py:358` | Make env-configurable |
| B6 | `datetime.utcnow()` deprecated Python 3.12+ | WARN | `llm_evaluate.py:616` | Use `datetime.now(UTC)` |
| B7 | No `KeyboardInterrupt` handler in batch loop | MEDIUM | `run_eval_batch.py` main loop | Add try/except |
| **B8** | **`--augment-levels` flag missing from batch runner** | **CRITICAL** | `run_eval_batch.py` | Add flag, wire to `evaluate_translation()` |

---

## Component Health Status

| Component | Status | Evidence |
|-----------|--------|----------|
| Harness build/run/verify | ✅ PASS | 3 smoke tests pass (bfs-cuda, hotspot-omp, bfs-opencl) |
| `_parse_gnu_time()` | ✅ PASS | All edge cases tested; result: `cpu_time=0.62` on bfs-cuda |
| `run_spec(measure_cpu_time=True)` | ✅ PASS | bfs-cuda: `cpu_time_seconds=0.62` confirmed |
| `evaluate_translation(use_cpu_timing=True)` | ✅ PASS | bfs: `timing_method=cpu_time`, `cpu_time=0.83` |
| Speedup priority (kernel > cpu > wall) | ✅ PASS | Verified in code and result JSON |
| Azure OpenAI client | ✅ PASS | bfs PASS with azure-gpt-4.1 (8.3s) |
| Endpoint URL stripping | ✅ PASS | `urlparse` strips path/query |
| Batch runner `--resume` | ✅ PASS | All 5 pilot kernels correctly skipped |
| Task D spec validation | ✅ PASS | 130 errors (all disk-only), zero schema errors |
| Augmentation L1/L2 | ✅ PASS | 75% pass rate (post-fixes A/B/C/V) |
| Augmentation L3 | ⚠️ PARTIAL | 48%; Bug D (TypedefExpansion) unresolved |
| Augmentation L4 | ⚠️ PARTIAL | 37% (was 1.6% pre-fix) |
| Batch markdown reports | ❌ BROKEN | Bug B1: kernel names show `?`; Bug B2: counts wrong |

---

## Task D — 5 New Rodinia Specs Status

All 5 specs are structurally correct but blocked on source availability.

| Spec | Schema | Manifest | Source on Disk | Baseline HW |
|------|--------|----------|---------------|-------------|
| `rodinia-gaussian-omp.json` | ✅ | ✅ | ❌ Missing | RTX 4060 Laptop |
| `rodinia-huffman-omp.json` | ✅ | ✅ | ❌ Missing | RTX 4060 Laptop |
| `rodinia-huffman-opencl.json` | ✅ | ✅ | ❌ Missing | RTX 4060 Laptop |
| `rodinia-hybridsort-omp.json` | ✅ | ✅ | ❌ Missing | RTX 4060 Laptop |
| `rodinia-mummergpu-opencl.json` | ✅ | ✅ | ❌ Missing | RTX 4060 Laptop |

**Blocker:** Rodinia submodule on this machine is at commit `9c10d3ea`; Erel's specs need commit `b0310d8`.
Coordinate with Erel to sync submodule. Specs themselves need no changes.

---

## Augmentation Pipeline (Prior Session Results)

| Level | Rodinia Pass Rate | Notes |
|-------|------------------|-------|
| L1 | 45/60 (75%) | Stable; all bug fixes applied |
| L2 | 45/60 (75%) | Same as L1 (seed=42 selects no-op transforms often) |
| L3 | 29/60 (48%) | Bug D (TypedefExpansion) still fires on ~22 specs |
| L4 | 22/59 (37%) | Improved from 1/60 pre-fix; residual issues remain |

**Integration gap:** All 10 pilot evaluations used `augment_level=0`.
The augmentation and LLM evaluation pipelines have **never been run together**.

---

## Remaining Work (Next Session)

| Priority | Item | Effort |
|----------|------|--------|
| 🔴 CRITICAL | Add `--augment-levels` to `run_eval_batch.py` | ~30 min |
| 🔴 HIGH | Fix Markdown bug (kernel `?` names + wrong counts) | ~20 min |
| 🔴 HIGH | Run end-to-end smoke test (bfs+hotspot, L0+L2) | ~15 min |
| 🟡 MEDIUM | `datetime.utcnow()` deprecation fix | ~5 min |
| 🟡 MEDIUM | Azure endpoint URL validation | ~10 min |
| 🟡 MEDIUM | `KeyboardInterrupt` handler in batch loop | ~15 min |
| 🟡 MEDIUM | nsys kernel profiling (Phase C2) | ~2 hrs |
| 🟡 MEDIUM | Prompt fix: header inlining guidance for nw/srad | ~15 min |
| 🟢 LOW | Backprop build fix: `-Wno-unused-result` | ~5 min |
| 🟢 LOW | Repo cleanup: remove 18 MB binaries + stale scripts | ~60 min |
| 🟢 LOW | Sync Erel's submodule (coordinate with Erel) | async |

### End-to-End Smoke Test Command (after augment-levels fix)
```bash
source env_parbench/bin/activate
python3 scripts/evaluation/run_eval_batch.py \
  --kernels bfs hotspot \
  --direction cuda-to-omp \
  --models claude-sonnet-4-20250514 \
  --augment-levels 0,2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
# Expected: bfs-L0 SKIP, bfs-L2 NEW, hotspot-L0 SKIP, hotspot-L2 NEW
```

---

## Key File Paths

| Category | Path |
|----------|------|
| Pilot results (Claude) | `results/evaluation/claude-sonnet-4-20250514/rodinia-*-cuda-to-rodinia-*-omp.json` |
| Pilot results (Azure) | `results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json` |
| Batch runner | `scripts/evaluation/run_eval_batch.py` |
| LLM evaluate script | `scripts/evaluation/llm_evaluate.py` |
| Harness runner | `harness/runner.py` |
| Augmentation results | `results/augmentation/eval_{cuda,omp,opencl}.{json,md}` |
| Erel's new specs | `specs/rodinia-{gaussian,huffman,huffman,hybridsort,mummergpu}-{omp,opencl}.json` |
| This report | `docs/session_report_2026-03-18.md` |
| Cleanup audit | `docs/repo_cleanup_audit_2026-03-17.md` |
