# ParBench — LLM Evaluation Pipeline: Task 2 Progress Report

**To:** Gal (Research Lead)
**From:** Samyak
**Date:** 2026-03-17
**Re:** Task 2 — LLM Code Translation Evaluation Infrastructure (SC26)

---

## Summary

The LLM evaluation pipeline for parallel code translation is implemented and dry-run verified. The system is ready for live LLM calls (Task 2.2) pending API key setup.

---

## What Was Built

A single-script evaluation pipeline (`scripts/evaluation/llm_evaluate.py`) that:

1. Takes a **source spec** (e.g., BFS in CUDA) and a **target spec** (e.g., BFS in OpenMP)
2. Sends the source code to an LLM asking it to translate to the target parallel API
3. Runs the existing ParBench harness (build → run → verify) on the LLM's translated code
4. Records all metrics needed for the SC26 paper into a structured JSON result

---

## Research Metrics Captured

These map directly to the gold-standard metrics from ParEval (HPDC 2024), BabelTower (ICML 2022), and LASSI-EE:

| Metric | How measured | SC26 usage |
|--------|-------------|------------|
| **Compilation rate** | `build_status == pass` | Primary: % of translations that compile |
| **Pass@1 (functional correctness)** | `overall_status == PASS` | Primary: % that pass harness verification |
| **Speedup ratio** | `baseline_wall_time / translated_wall_time` | Primary: performance preservation |
| **Token efficiency** | `completion_tokens` per result | Secondary: API cost analysis |
| **Per-direction rates** | Group by `(source_api, target_api)` | Which translation directions are harder |
| **Per-kernel rates** | Group by `kernel_name` | Which kernels are harder to translate |
| **L0 vs L2 augmentation delta** | Compare `augment_level=0` vs `2` | Key finding: does augmentation affect LLM translation quality? |

---

## Augmentation Integration

The pipeline has a built-in `--augment-level` flag that mutates the **source code** the LLM sees before translation:

- `--augment-level 0` (default): LLM sees original source — baseline
- `--augment-level 2`: LLM sees semantically-equivalent but syntactically transformed source (e.g., `x += 1` → `x = x + 1`, `a < b` → `b > a`, `arr[i]` → `*(arr+i)`)

**Hypothesis tested:** If Pass@1 drops from L0 → L2, LLMs are pattern-matching on surface syntax rather than understanding semantics. If it holds steady, LLMs are robust to style variation. This L0 vs L2 delta is a novel finding for the SC26 paper.

---

## Model Support

| Provider | Models supported |
|----------|-----------------|
| Anthropic | claude-sonnet-4-20250514, claude-opus-4-6, claude-haiku-4-5 |
| OpenAI | gpt-4o, gpt-4.1, o3, o4-mini |
| ParaCodex *(planned)* | Same interface — plug in when ready |

Any model ID is accepted; no hardcoded allowlist. ParaCodex will slot in as a provider adapter with identical prompt-in / code-out interface, enabling apples-to-apples comparison.

---

## Iterative Repair (LASSI-EE style)

The `--max-retries N` flag enables LLM self-repair:

- N=1 (default): zero-shot — LLM gets one attempt
- N>1: if build/run/verify fails, the error is fed back to the LLM for another attempt

LASSI-EE achieves 81% pass rate with repair vs ~30% zero-shot. We have this capability built in from day one so we can measure the repair effect on Rodinia.

---

## Dry Run Output (Verified 2026-03-17)

Ran `--dry-run` on `rodinia-bfs-cuda → rodinia-bfs-omp`:

```
SYSTEM MESSAGE:
"You are a parallel programming expert specializing in CUDA to OpenMP translation..."

USER MESSAGE includes:
  - Kernel: bfs, CUDA → OpenMP
  - Target file to produce: bfs.cpp
  - Build command: make bfs
  - Build environment: gcc>=9.0 (with OpenMP support)
  - Full source code: bfs.cu (266 lines), kernel.cu, kernel2.cu
```

Source files were not modified (md5 verified stable). The prompt is correct and complete.

---

## What's Next: Task 2.2

Run live evaluations on the 3 smoke-test specs (those known to PASS in the harness) × 2 models:

| Spec pair | Direction |
|-----------|-----------|
| `rodinia-bfs-cuda → rodinia-bfs-omp` | CUDA → OpenMP |
| `rodinia-bfs-cuda → rodinia-bfs-opencl` | CUDA → OpenCL |
| `rodinia-hotspot-cuda → rodinia-hotspot-omp` | CUDA → OpenMP |

**Expected output:** Per-spec JSON files in `results/evaluation/<model>/` with all metrics above.
**Requires:** `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` set in environment.

This will give us the first real Pass@1 and speedup numbers to include in the SC26 draft.

---

## Code Location

- Script: `scripts/evaluation/llm_evaluate.py`
- Results will go to: `results/evaluation/<model>/<source>-to-<target>.json`
- GitHub: pushed to `main` at commit `9cc8211`
