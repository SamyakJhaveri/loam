# Known Issues & Gotchas

> Always loaded. Contains active guardrails that prevent recurring mistakes.
> Historical fix details are in `known-issues-archive.md` (conditional, loads on augmentation/harness files).

## Schema Validation Errors (pre-existing — ignore)

~15 errors from `validate_schema.py --all` are expected (updated 2026-04-03):
- HeCBench-master/ IS cloned locally (1874 benchmark dirs) — source_dir errors no longer fire.
- 15 errors from the 5 deleted phantom Rodinia specs still referenced in manifest.jsonl
  (each generates 2 manifest errors + 1 "spec file not found" = 3 × 5 = 15).
  This is correct behavior — manifest.jsonl is append-only; spec files were deleted.
Do NOT try to fix any of these errors.

## Current Spec Status (as of 2026-04-19, post S4a+S4b+S5+S6 oracle campaign)

**Rodinia:** 60 specs total, 54 TRUE PASS, 0 FALSE_PASS, 6 KNOWN_FAIL.
**XSBench:** 4 specs total, 4 PASS, 0 KNOWN_FAIL.
**RSBench:** 4 specs (cuda, omp, opencl, omp_target), all 4 PASS.
**mixbench:** 3 specs (cuda, omp, opencl), all 3 PASS.
**HeCBench (curated):** 10 kernels, 25 specs (cuda + omp/omp_target), 23 PASS, 2 KNOWN_FAIL.
**All 88 curated non-KNOWN_FAIL specs verified PASS.**
**Use 54 Rodinia TRUE PASS + 3 XSBench + 4 RSBench + 3 mixbench + 23 HeCBench curated = 87 specs (plus 1 HeCBench cross-API pair) = 88 for eval batches.**

**Oracle strength distribution (206 total specs, post-S7b audit 2026-04-19):**
- 7 strong (`oracle_strength: "strong"` label) — of which 2 carry `file_hash` with matching cross-API hashes (bptree×2) and 5 are mis-labeled (hotspot3d×3, hecbench-md×2 are effectively weak; label correction deferred to post-NeurIPS cleanup)
- 0 medium
- 46 weak (stdout_pattern + exit_code only)
- 153 untagged — 35 curated specs (HeCBench/XSBench/RSBench/mixbench remainder) + ~118 HeCBench bulk specs outside the curated 88-spec corpus. Post-NeurIPS S6.5 may bulk-tag them.

**2026-04-19 S7 BUG-3 downgrade (bfs):** `rodinia-bfs-cuda` + `rodinia-bfs-omp` dropped from strong (file_hash) to weak. Root cause: Rodinia's CUDA and OMP implementations diverge in source-node selection (`cuda/bfs/bfs.cu:130` hardcodes `source=0` as debug leftover; `openmp/bfs/bfs.cpp:87` has it commented out, labeled "tesing code line"). CUDA baseline hashes to `3c5eeb...`, OMP to `f57afc...`. Faithful LLM translations cannot satisfy both.

**2026-04-19 S7b audit downgrades (8 specs):** cross-API divergence or synthesis-asymmetry applies the same bfs pattern. Full report: `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md`.

| Spec | Reason | Replacement oracle |
|------|--------|--------------------|
| `rodinia-cfd-cuda`, `rodinia-cfd-omp` | FP reduction-order divergence over 2000 RK3 iterations (CUDA=`ab07aa0c`, OMP=`4283a12d`) | `stdout_pattern: "Saved solution\\.\\.\\."` + `exit_code` |
| `rodinia-hotspot-cuda`, `rodinia-hotspot-omp` | FP reduction-order divergence in transient-temperature solver (CUDA=`06b21039`, OMP=`f90474ff`) | `stdout_pattern: "Ending simulation"` + `exit_code` |
| `rodinia-myocyte-cuda`, `rodinia-myocyte-opencl` | FP reduction-order divergence in ODE integration across API runtimes (CUDA=`1e329f02`, OpenCL=`59efddcb`) | `stdout_pattern: "Time spent in different stages..."` + `exit_code` |
| `rodinia-nw-omp` | Synthesis-asymmetric: CUDA `needle.cu:194` has `//#define TRACEBACK` commented out; only OMP writes `result.txt` | `stdout_pattern: "Processing bottom-right matrix"` + `exit_code` |
| `rodinia-nn-cuda` | Synthesis-asymmetric: `nn_cuda.cu:185` emits `Distance=`; `nn_openmp.c` has no equivalent print | `stdout_pattern: "Distance="` + `exit_code` (numeric_comparison removed) |

Downgrade checklist applied per spec: file_hash/numeric_comparison strategy removed, stdout_pattern added/retained, reference_files cleared, `oracle_strength: "weak"` set, description updated, reference artifacts deleted under `specs/references/{cfd,myocyte,nw}/`. Bptree pair retains file_hash (cross-API hashes match). Post-downgrade sweep: 88/88 PASS. Tests in `tests/test_oracle_divergence.py` (6 PASS) document the audit evidence.

**S6 sweep (2026-04-19):** 88/88 PASS via `scripts/spec_tools/run_verify_sweep.py`.
Log: `.planning/phases/03-oracle-framework/03-S6-SWEEP.log`.
One transient regression surfaced (`rodinia-myocyte-omp` BUILD_FAIL) and was traced to an undocumented dirty file in `rodinia/rodinia-src/openmp/myocyte/main.c` (2731 lines vs canonical 375); restored via `git -C rodinia/rodinia-src checkout HEAD -- openmp/myocyte/main.c` before the second sweep pass.

## KNOWN_FAIL Specs (8 — exclude from eval batches)

| Spec | Error | Why deferred |
|------|-------|-------------|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 | Texture reference → object rewrite needed |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 | Same rewrite in `mummergpu_kernel.cu` |
| `rodinia-mummergpu-omp` | `texture<>` + `cuMemGetInfo_v2` signature | OMP version also uses CUDA kernel |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found | Needs `libglew-dev` + display server |
| `rodinia-nn-opencl` | TIMEOUT / SIGSEGV | Pre-existing; never passed |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime | Pre-existing; never passed |
| `hecbench-stencil1d-omp_target` | BUILD_FAIL | omp_target compile issue |
| `hecbench-scan-omp_target` | VERIFY_FAIL | Output mismatch on CPU target |

## OMP Spec Run Arg Rules (CRITICAL)

**Never change spec run args without reading the actual source's argc check.**
This rule exists because "fixes" based on documentation caused 2 specs to silently fail for weeks.

- **`rodinia-nw-omp`**: Source (`needle.cpp:249`) checks `argc == 4` → 3 args required.
  Correct: `["2048","10","4"]` (correctness), `["8192","10","4"]` (performance).
- **`rodinia-hotspot-omp`**: Source (`hotspot_openmp.cpp:282`) checks `argc != 8` → 7 args required.
  Correct: `["512","512","2","4","temp_512","power_512","output.out"]` (correctness).

## Key Build/Run Rules

- **needle.h**: `rodinia-nw-omp` build uses `-I../../cuda/nw` (needle.h lives in cuda/nw only).
- **SRAD binary**: May be stale — always rebuild before using: `cd .../srad_v2 && make`.
- **Spec-executable names**: Always verify `outputs.executable` matches the actual Makefile output
  (e.g., `euler3d.out` not `euler3d`, `pathfinder.out` not `pathfinder`).
- **Run arg format**: Always check source's `init()`/`argc` parsing before writing spec run args
  (e.g., pathfinder-opencl uses `-c/-r/-h` flags, not positional args).

## Deleted Phantom Specs (5)

gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl — all pointed
to non-existent Rodinia directories at commit `9c10d3ea`. Deleted from `specs/`, manifest
entries remain (append-only). Use streamcluster or backprop as replacement for batches.

## Git Worktrees and Submodules

Git worktrees do NOT initialize submodules. The `rodinia/` submodule will be empty
in any worktree. **Never run LLM evaluations in worktrees.** Only use worktrees for code review.

## KNOWN_FAIL Inclusion Policy for Evaluation Statistics

- Results where KNOWN_FAIL spec is the SOURCE: Exclude from the standard denominator.
  Rationale: source correctness is unverified on the KNOWN_FAIL platform, making it
  unclear whether a PASS reflects genuine translation quality.
- Results where KNOWN_FAIL spec is the TARGET: Exclude from statistics. The target
  build/run infrastructure is broken, making evaluation unfair.
- When reporting pass rates, exclude cells where EITHER source OR target is KNOWN_FAIL.
  Denominator math (`N_total − N_target_KF − N_source_KF + N_both_KF`) to be recomputed
  against the Phase 3 canonical + ablation result corpus once those runs complete.

## Pre-Phase-3 evaluation data decommissioned (2026-04-20)

The 1,248 Qwen 3.5 397B results (780 C1 + 468 C2) and 905 GPT-4.1 mini results that
previously backed the "31.0% non-KNOWN_FAIL pass rate" / "backprop anomaly" / "347/1120"
numbers in this file were **purged from `results/evaluation/` per user directive**. The
two-campaign design (C1 temp=0 L0-L4 + C2 temp=0.7 -s0/s1/s2) was superseded by the
Gal-approved canonical + L0-conditional ablation experiment plan. NeurIPS evaluation
numbers now source exclusively from Phase 3 runs on `together-qwen-3.5-397b-a17b` +
`azure-gpt-5.4`.

- Historical regex-combiner bug (`_build_cross_api_verify_spec()` → `_wrap_pattern()` helper)
  still stands as a code-level fact; the 9-results-affected analysis is archived in
  `known-issues-archive.md` for provenance.
- Do NOT cite the 31.0% / 347/1120 / 1,248 figures in new docs or paper prose. Phase 3
  data reconstitutes these statistics from scratch.

Historical details (FALSE_PASS fixes, Rodinia submodule policy, XSBench checksums, hook protection,
augmentation baseline, eval timing limitations, localStorage divergence, eval JSON schema quirk,
Gemini thinking confound, backprop anomaly, OpenCL kernel-only fix) are in `known-issues-archive.md`.
