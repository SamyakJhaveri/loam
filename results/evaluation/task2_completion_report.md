# Task 2 Completion Report — LLM Evaluation Script

**Date:** 2026-03-17
**Task:** Create LLM Evaluation Script (`scripts/evaluation/llm_evaluate.py`)
**Status:** COMPLETE — dry-run verified, ready for Task 2.2 (live LLM calls)

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/evaluation/__init__.py` | 0 | Package init |
| `scripts/evaluation/llm_evaluate.py` | 925 | Main evaluation script |
| `results/evaluation/.gitkeep` | 0 | Results directory anchor |
| `results/evaluation/task2_completion_report.md` | this file | Completion record |

---

## Design Decisions Implemented

| Decision | Description | Status |
|----------|-------------|--------|
| D1 — Timing | Wall-clock via `run_result.duration_seconds`; baseline from spec; `extract_metrics()` for HeCBench | ✅ |
| D2 — Model registry | Prefix routing: `claude-*` → Anthropic, `gpt-*/o1-*/o3-*/o4-*` → OpenAI; any model string accepted | ✅ |
| D3 — Prompt design | Build command + system deps + target filenames + source files in prompt; no target code leakage | ✅ |
| D4 — API-agnostic | API names read from `spec["identity"]["parallel_api"]`; no hardcoded API logic | ✅ |
| D5 — Iterative repair | `--max-retries` (default 1); multi-turn conversation with error feedback on retries | ✅ |

---

## Result JSON Schema

All 28 fields from the plan are present in the result dict:

```
source_spec, target_spec, model, augment_level, timestamp,
prompt_tokens, completion_tokens, llm_response_time_seconds,
build_status, build_time_seconds, build_error_snippet,
run_status, run_time_seconds, run_exit_code,
verify_status, verify_strategy,
overall_status, error_message,
metrics, baseline_wall_time_seconds, translated_wall_time_seconds, speedup_ratio,
translated_files, target_files_expected, target_files_extracted,
max_retries, total_attempts, attempts
```

---

## Harness Integration

| Function | Module | Used for |
|----------|--------|---------|
| `load_spec()` | `harness.spec_loader` | Load source + target specs |
| `resolve_paths()` | `harness.spec_loader` | Resolve absolute file paths |
| `get_prompt_payload()` | `harness.spec_loader` | Get (augmented) source code |
| `build_spec()` | `harness.builder` | Build translated code |
| `run_spec()` | `harness.runner` | Run translated executable |
| `verify_run()` | `harness.verifier` | Check correctness |
| `extract_metrics()` | `harness.verifier` | Parse stdout timing metrics |

---

## Augmentation Integration

`get_prompt_payload(source_spec, project_root, augment_level)` is called before the LLM sees the code.

- `augment_level=0` (default): raw source code — baseline evaluation
- `augment_level=2`: ~2 AST transforms applied to source (ArithmeticTransform, SwapCondition, PointerArithmeticToArrayIndex, TypedefExpansion, ChangeNames)

The LLM sees augmented source → must still produce correct target API code.
The SC26 paper key finding: **L0 vs L2 delta in Pass@1** — measures LLM robustness to code style variation.

---

## CLI Interface

```bash
# Dry run (no LLM call — verified ✅)
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run -v

# List known models
python3 scripts/evaluation/llm_evaluate.py --list-models

# Live run (Task 2.2)
export ANTHROPIC_API_KEY=sk-ant-...
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

---

## Bugs Found and Fixed (Post-Implementation Audit)

5-subagent audit (2026-03-17) found 3 bugs, all fixed:

| Bug | Root cause | Fix |
|-----|-----------|-----|
| `translated_files_preview` always `{}` | Read `.parbench_bak` after `finally` deleted them | Save `last_llm_response` inside loop before `restore_files()` runs |
| `last_response_text` always empty in zero-shot | Assistant response never appended to `messages` on final attempt | Assign `last_llm_response = response_text` inside retry loop |
| Dead `pass` block (27 lines of spaghetti) | Placeholder code with no implementation | Deleted; replaced with 3-line `extract_code_blocks()` call |

---

## Verification Summary

| Check | Result |
|-------|--------|
| `--help` | ✅ All 10 args present |
| `--list-models` | ✅ 8 models, routing rules shown |
| `--dry-run -v` (bfs CUDA→OMP) | ✅ Full prompt: 3 source files, build cmd, env, target spec |
| Source file md5 unchanged after dry-run | ✅ `aba2c53f489e5ddb24fd28446d0b8757` stable |
| Module import | ✅ All public functions importable |

---

## Task 2.2 — Next Steps

Run live LLM evaluations on the 3 smoke test specs × 2 models:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# bfs: CUDA → OMP
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json --target specs/rodinia-bfs-omp.json \
  --model claude-sonnet-4-20250514 --project-root /home/samyak/Desktop/parbench_sam -v

# hotspot: CUDA → OMP
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-hotspot-cuda.json --target specs/rodinia-hotspot-omp.json \
  --model claude-sonnet-4-20250514 --project-root /home/samyak/Desktop/parbench_sam -v

# bfs: CUDA → OpenCL
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json --target specs/rodinia-bfs-opencl.json \
  --model claude-sonnet-4-20250514 --project-root /home/samyak/Desktop/parbench_sam -v
```

Results will appear in `results/evaluation/claude-sonnet-4-20250514/*.json`.
