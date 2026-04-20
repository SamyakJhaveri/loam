# S7b Strong-Oracle Audit

**Date:** 2026-04-19
**HEAD at audit start:** `9b1a1f5`
**Audit scope:** All specs carrying `"type": "file_hash"` or `"type": "numeric_comparison"` at HEAD.
**Method:** Cross-API hash comparison (using spec-embedded `expected_sha256` captured during S6 sweep 88/88 PASS) + source-level asymmetry review (argc/print/feature flags).
**Result:** 2/10 clean, 8/10 downgraded to weak oracle.

---

## Scope (10 specs)

At HEAD `9b1a1f5` the strong-oracle inventory:

| Spec | Type | Reference files | oracle_strength |
|------|------|-----------------|------------------|
| `rodinia-bptree-cuda` | `file_hash` on `output.txt` | 1 | strong |
| `rodinia-bptree-omp`  | `file_hash` on `output.txt` | 1 | strong |
| `rodinia-cfd-cuda`    | `file_hash` on `density`    | 1 | strong |
| `rodinia-cfd-omp`     | `file_hash` on `density`    | 1 | strong |
| `rodinia-hotspot-cuda`| `file_hash` on `output.out` | 0 (3.6 MiB, Zenodo-deferred) | strong |
| `rodinia-hotspot-omp` | `file_hash` on `output.out` | 0 (3.6 MiB, Zenodo-deferred) | strong |
| `rodinia-myocyte-cuda`| `file_hash` on `output.txt` | 1 | strong |
| `rodinia-myocyte-opencl`| `file_hash` on `output.txt` | 1 | strong |
| `rodinia-nw-omp`      | `file_hash` on `result.txt` | 1 | strong |
| `rodinia-nn-cuda`     | `numeric_comparison` on `Distance=` | 0 | medium |

**Out of scope but flagged for follow-up:** `hecbench-md-{cuda,omp_target}` and `rodinia-hotspot3d-{cuda,omp,opencl}` carry `oracle_strength: "strong"` as a label but use only `stdout_pattern + exit_code` strategies. Label mismatch — should be `weak`. Documented here; fix deferred to post-NeurIPS cleanup.

---

## Verdict table

| Kernel | Pair/Singleton | Cuda hash | Omp/Opencl hash | Match? | Verdict | Reason |
|--------|----------------|-----------|------------------|--------|---------|--------|
| bptree | pair (cuda,omp) | `b22b08c5...` | `b22b08c5...` | ✅ | **CLEAN — keep strong** | Deterministic B+tree range+lookup on sorted integer keys; no FP reduction; output.txt is byte-identical across APIs. |
| cfd | pair (cuda,omp) | `ab07aa0c...` | `4283a12d...` | ❌ | **DOWNGRADE** | 2000 RK3 iterations; OMP parallel reductions accumulate flux contributions in different order than CUDA block reductions. FP non-associativity produces divergent `density` bytes. |
| hotspot | pair (cuda,omp) | `06b21039...` | `f90474ff...` | ❌ | **DOWNGRADE** | Transient-temperature iterative solver; OMP/CUDA thermal flux accumulation order differs per thread/block; FP non-associativity. |
| myocyte | pair (cuda,opencl) | `1e329f02...` | `59efddcb...` | ❌ | **DOWNGRADE** | ODE integration across ECM parameters; CUDA and OpenCL runtimes produce different FP reduction order; output.txt bytes differ. |
| nw | singleton (omp) | — | `912879cb...` | n/a | **DOWNGRADE** | `cuda/nw/needle.cu:194` comments out `#define TRACEBACK`; CUDA variant does not produce `result.txt`. OMP `needle.cpp:314` has TRACEBACK active. file_hash on omp target punishes both directions: omp→cuda translator faithfully drops TRACEBACK (cannot write file); cuda→omp translator faithfully preserves the comment-out (also cannot write file). Synthesis-unfair. |
| nn | singleton (cuda) | — (numeric) | — | n/a | **DOWNGRADE** | `cuda/nn/nn_cuda.cu:185` emits `printf("%s --> Distance=%f\n", ...)` per record. `openmp/nn/nn_openmp.c` emits only `"The %d nearest neighbors are:"` with no per-record `Distance=`. numeric_comparison on `Distance=` punishes a faithful omp→cuda translator that does not synthesize the cuda-only print. |

---

## Downgrade actions taken

For each of the 8 downgraded specs (cfd×2, hotspot×2, myocyte×2, nw-omp, nn-cuda):

1. Removed `file_hash` (or `numeric_comparison`) strategy from `verification.strategies[]`.
2. Added/retained `stdout_pattern` strategy with kernel-completion banner:
   - cfd: `"Saved solution\\.\\.\\."`
   - hotspot: `"Ending simulation"`
   - myocyte: `"Time spent in different stages of the application"`
   - nw-omp: `"Processing bottom-right matrix"`
   - nn-cuda: `"Distance="` (retained; sentinel already present)
3. Kept `exit_code: 0` strategy.
4. Cleared `verification.reference_files[]` where present (cfd×2, myocyte×2, nw-omp).
5. Set `verification.oracle_strength` from `strong`/`medium` → `weak`.
6. Updated strategy `description` to cite this audit.
7. Deleted `specs/references/{cfd,myocyte,nw}/*` reference artifacts (5 files, 3 directories).
8. Divergence tests in `tests/test_oracle_divergence.py` (6 tests, all PASS).

`specs/references/bptree/{cuda_output.txt,omp_output.txt}` retained (bptree stays strong).

---

## Post-S7b oracle_strength tally

| Strength | Count | Delta | Specs |
|----------|-------|-------|-------|
| strong | 14 → 7 | −7 | bptree×2 (file_hash, valid) + hotspot3d×3 + hecbench-md×2 (mis-labeled, see Out-of-scope) |
| medium | 1 → 0  | −1 | (was nn-cuda; downgraded) |
| weak   | 38 → 46 | +8 | +cfd×2, +hotspot×2, +myocyte×2, +nw-omp, +nn-cuda |
| unknown | 153 → 153 | 0 | — |
| **Total** | **206** | **0** | — |

After follow-up correction of mis-labeled hotspot3d×3 + hecbench-md×2, true `strong` count will fall to 2 (bptree only).

---

## Sweep regression check

`python3 scripts/spec_tools/run_verify_sweep.py --project-root ... --exclude-known-fail --jobs 4` → **88/88 PASS** after downgrades. Downgraded specs now pass via the weaker `stdout_pattern + exit_code` conjunction, which every sibling kernel baseline already satisfied.

---

## Precedent and consistency with S7

S7 commit `851a29d` downgraded `rodinia-bfs-{cuda,omp}` for identical reasons: CUDA `bfs.cu:130` hardcodes `source=0;` while OMP `bfs.cpp:87` reads from input (commented-out override labeled "tesing code line"). S7b extends the same principle to the remaining CUDA/OMP divergent pairs (`cfd`, `hotspot`) and to the two synthesis-asymmetric singletons (`nw-omp`, `nn-cuda`).

**Scope note (myocyte pair):** The myocyte downgrade is a `(cuda, opencl)` pair, not the usual `(cuda, omp)` pair. `rodinia-myocyte-omp` was already `oracle_strength: weak` prior to S7b — downgraded in S5 Batch 4 (commit `255bf0d`) as part of the bucket5 weak-tag pass because its OMP GCC-12 BUILD_FAIL blocked a deterministic two-run pre-flight. S7b therefore considers only the two still-strong myocyte variants (cuda, opencl) and finds that their output.txt hashes diverge across CUDA and OpenCL runtimes — this is the first CUDA↔OpenCL divergence surfaced in this sprint and establishes that FP reduction-order divergence is not exclusive to the CUDA↔OMP pattern. Downstream analysis for paper-time narrative should distinguish FP-reduction divergence (which applies across any cross-runtime pair) from source-asymmetry divergence (bfs, nw, nn — applies specifically when benchmark source code embeds API-specific flags or prints).

---

## Follow-up work (NOT in S7b)

1. Correct `oracle_strength` labeling for `hotspot3d-{cuda,omp,opencl}` and `hecbench-md-{cuda,omp_target}` — currently labeled `strong` but have only `stdout_pattern + exit_code`. True strength is `weak`.
2. Explore numeric_comparison with per-API tolerance for cfd/hotspot/myocyte as Zenodo-camera-ready alternative (would require FP-tolerance extraction from density/output.out — non-trivial).
3. Consider algorithm-level equivalence oracles (e.g., max relative error < ε over the density field) as a paper-time methodological contribution.
