---
paths:
  - "harness/**"
  - "scripts/evaluation/**"
  - "scripts/analysis/**"
  - "visualizations/**"
---

# Active Gotchas

> Load-bearing rules rescued from the deleted `known-issues-archive.md`.
> These are NOT historical fix records (those are in git log) — they are live rules
> that still govern how pipeline code should behave.

## 1. Result Protection (post hook-deletion 2026-04-21)

`protect-cuda-omp-results.sh` was **deleted** on 2026-04-21 because it guarded
`results/phase[3-9]/` but Phase 3 results actually land in `results/evaluation/`.

**Current protection layers:**
- `result-immutability.sh` (PreToolUse on Edit|Write) — blocks overwriting existing
  `results/evaluation/*.json` files. Does NOT protect against `rm` or shell redirects.
- Global deny rule in `.claude/settings.json` — blocks `rm -rf` and `rm -fr` but NOT
  targeted `rm` on individual files (e.g., `rm results/evaluation/some-file.json`).
- `--resume` discipline — always use `--resume` with `run_eval_batch.py` to skip existing.

**Known gap:** Targeted `rm` on individual result files is NOT blocked by any hook.
Mitigation: always ask Samyak before deleting any file under `results/evaluation/`.

Benchmark source protection: `protect-benchmark-sources.sh` (PreToolUse on Edit|Write)
still active — protects `/(rodinia|rodinia-src|HeCBench-master|hecbench|xsbench-src)/`.

## 2. Rodinia Submodule Patch Policy

**Current state:** 10 files modified from pristine commit `9c10d3ea`.
- 9 Makefile/config patches (toolchain adaptation — safe)
- 1 source exception: `opencl/cfd/euler3d.cpp:276` — `if(file==NULL)` → `if(!file)` (C++11 portability, not a benchmark logic change)

**Patch file:** `docs/rodinia_toolchain_patches.diff` — regenerated after each submodule reset.

Build-flag alternative for pathfinder: spec passes `-std=c++14` in `CXXFLAGS` instead of editing source. mummergpu `unistd.h` edits reverted — both specs are KNOWN_FAIL regardless.

## 3. XSBench Checksum Asymmetry

- OMP binary prints `history` checksum = **941535**
- CUDA / OpenCL / OMP-target binaries print `event` checksum = **945990**

Do not assume a single value across APIs. Verification specs must use the API-appropriate checksum.

## 4. Result JSON: use `overall_status`, not `run_status`

Top-level `run_status`, `run_time_seconds`, `run_exit_code` fields can contain stale data from a non-final attempt when a multi-attempt evaluation regresses to a build failure.

**Rule:** Always use `overall_status` as the authoritative verdict. The `attempts[]` array is the canonical per-attempt record.

This was a pipeline bug in `llm_evaluate.py` (fixed prospectively). Legacy result JSONs are not retroactively corrected; analysis code must not trust top-level `run_status`.

## 5. Do NOT use `speedup_ratio` from result JSONs

All existing PASS results use `timing_method: "wall_time"`. `translated_cpu_time_seconds` and `translated_kernel_time_seconds` are `null` in legacy files.

Sub-millisecond baseline wall times (0.001s) produce unreliable ratios (e.g., nn=16.0x, bfs=0.002x). Wall-clock time includes OS scheduling noise, I/O, and memory allocation — it is not kernel time.

**For valid performance numbers:** use `nvprof`/`ncu` for CUDA kernel time, `perf` or `omp_get_wtime()` around the parallel region for OMP.

## 6. OpenCL Kernel-Only Translation Predicate

`llm_evaluate.py` uses `_is_kernel_only_translation(target_spec)` — returns `True` when ALL `translation_targets` end with `.cl`.

- When True (kernel-only): `_build_cross_api_run_spec()` and `_build_cross_api_verify_spec()` return `copy.deepcopy(target_spec)` (target args and patterns unchanged)
- When False (full-program, CUDA/OMP targets): existing cross-API logic applies

**Result JSON fields:**
- `translation_type`: `"kernel_only"` | `"full_program"`
- `run_args_mode`: `"kernel_only_target_args"` | `"cross_api_source_args"` | `"same_api_target_args"`
- `verification_mode`: `"kernel_only_target_pattern"` | `"cross_api_combined_pattern"` | `"same_api_target_pattern"`

**Rule:** When adding new cross-API targets, check if kernel-only (host untouched) or full-program (host rewritten). The `.cl` heuristic works for OpenCL but may need extension for future APIs with separate kernel files.

## 7. Dashboard localStorage Divergence (if editing `visualizations/sprint_dashboard.html`)

`sprint_dashboard.html` uses browser localStorage as overlay on hardcoded `DEFAULT_TASKS` JS array. Edits via the kanban board write to browser localStorage — the git-tracked HTML is NOT updated.

**Rule:** After any dashboard session, grep the HTML directly for values you changed — do not trust browser view:

```bash
grep -n "M11\|Rodinia Specs\|stat-value" visualizations/sprint_dashboard.html | head -20
grep -n "status: 'blocked'\|status: 'todo'" visualizations/sprint_dashboard.html | grep -v "//\|kh-\|dropdown\|column\|label"
```

If grep shows stale values, edit `DEFAULT_TASKS` before committing.
