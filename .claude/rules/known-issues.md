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

## Current Spec Status (as of 2026-03-28, post campaign expansion)

**Rodinia:** 60 specs total, 54 TRUE PASS, 0 FALSE_PASS, 6 KNOWN_FAIL.
**XSBench:** 4 specs total, 4 PASS, 0 KNOWN_FAIL.
**RSBench:** 4 specs (cuda, omp, opencl, omp_target), all 4 PASS — verified 2026-04-03.
**mixbench:** 3 specs (cuda, omp, opencl), all 3 PASS — verified 2026-04-03.
**HeCBench (curated):** 10 kernels, 25 specs (cuda + omp/omp_target), 23 PASS, 2 KNOWN_FAIL.
**All 65 Rodinia+XSBench+RSBench+mixbench non-KNOWN_FAIL specs verified PASS.**
**Use 54 Rodinia TRUE PASS + 3 XSBench + 4 RSBench + 3 mixbench specs for eval batches.**

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
- When reporting pass rates, exclude results where EITHER source OR target is KNOWN_FAIL
  (denominator = 1120 results where both source and target are non-KNOWN_FAIL;
  347 PASS = 31.0%). Verified against 1,248 total results on disk (72 target-KF, 88 source-KF,
  56 both-KF excluded).

## Pipeline Audit Results (2026-04-09)

Full audit of 1,248 Qwen 3.5 397B evaluation results across 156 (kernel, direction) combos.

- **1 bug found:** Regex combiner in `_build_cross_api_verify_spec()` wrapped `(?i)` patterns
  as `(?:(?i)...)`, causing Python `re.compile()` to reject the pattern. Fixed by converting
  to scoped form `(?i:...)` via `_wrap_pattern()` helper. See `scripts/analysis/reverify_regex_bug.py`.
- **9 results affected** (all nn-opencl source, KNOWN_FAIL): 3 would flip VERIFY_FAIL→PASS,
  6 still fail (stdout lacks expected pattern).
- **0 pipeline bugs in core (non-KNOWN_FAIL) evaluation set.**
- **347/1120 = 31.0% non-KNOWN_FAIL pass rate** — unaffected by the fix.

Historical details (FALSE_PASS fixes, Rodinia submodule policy, XSBench checksums, hook protection,
augmentation baseline, eval timing limitations, localStorage divergence, eval JSON schema quirk,
Gemini thinking confound, backprop anomaly, OpenCL kernel-only fix) are in `known-issues-archive.md`.
