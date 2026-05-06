# 03-B1-AUDIT — Oracle Framework: 53 In-Scope Spec Classification

**Session:** S3 (2026-04-18)
**Scope:** 18 weak + 35 unknown = 53 specs requiring audit
**Not in scope:** 23 already-strong HeCBench-curated, 4 XSBench, 4 RSBench, 8 KNOWN_FAIL
**Input log:** `/tmp/b1_inscope.log`

## Bucket Definitions

1. **bucket1 (already-strong):** print site inside correctness self-check block (e.g., `if (correct) printf(...)`). No spec edit required. `oracle_strength: "strong"`.
2. **bucket2 (regex-tighten):** existing `stdout_pattern` fires on garbage; narrowing to require a numeric field makes it strong. One-line spec pattern edit. `oracle_strength: "strong"` post-fix.
3. **bucket3 (needs-file_hash):** binary writes a deterministic output file; upgrade to `file_hash` strategy. S4 `_capture_baseline.py` pre-flight must confirm determinism (two runs identical SHA-256). `oracle_strength: "strong"` after confirm.
4. **bucket4 (needs-numeric_comparison):** binary prints a timing-independent numeric value in stdout (accuracy, checksum, residual — **NOT** wall-clock); upgrade to `numeric_comparison`. `oracle_strength: "medium"` (or `"strong"` if tolerance tight).
5. **bucket5 (truly-weak):** no output file, no numeric stdout, no self-check — OR stdout numeric is a timing value (wall-clock seconds). `oracle_strength: "weak"` + `recommended_fix: "paper Threats"`.

## Oracle Strength Enum

Source: `schema/spec_schema.json:615-620` (enum array; values at 616-619). Values: `"strong"` | `"medium"` | `"weak"` | `"unknown"`. No other spellings valid.

## Citation Discipline

Every row cites exact `benchmark/path:line`. A row without a source citation is invalid. Variant specs (e.g., `bfs-cuda` + `bfs-omp`) cite separate source files. Same kernel ≠ same bucket.

## Classification Matrix

| spec_id | source_file:line | gating_expression | bucket | oracle_strength | recommended_fix |
|---|---|---|---|---|---|
| rodinia-backprop-cuda | rodinia/rodinia-src/cuda/backprop/facetrain.c:27 | printf("Training done\n") — unconditional after bpnn_free(net), no file write, no correctness gate | bucket5 | weak | paper Threats — completion signal only, no correctness evidence |
| rodinia-backprop-omp | rodinia/rodinia-src/openmp/backprop/facetrain.c:24 | printf("Training done\n") — unconditional after bpnn_free(net), no file write, no correctness gate | bucket5 | weak | paper Threats — completion signal only, no correctness evidence |
| rodinia-backprop-opencl | rodinia/rodinia-src/opencl/backprop/facetrain.c:27 | printf("\nFinish the training for one iteration\n") — unconditional after bpnn_free(net), no file write, no correctness gate | bucket5 | weak | paper Threats — completion signal only, no correctness evidence |
| rodinia-bfs-cuda | rodinia/rodinia-src/cuda/bfs/bfs.cu:266 | printf("Result stored in result.txt\n") — immediately after fopen("result.txt","w")+fprintf loop (unconditional) | bucket3 | strong | file_hash on result.txt |
| rodinia-bfs-omp | rodinia/rodinia-src/openmp/bfs/bfs.cpp:183 | printf("Result stored in result.txt\n") — immediately after fopen("result.txt","w")+fprintf loop (unconditional) | bucket3 | strong | file_hash on result.txt |
| rodinia-bptree-cuda | rodinia/rodinia-src/cuda/b+tree/kernel/kernel_gpu_cuda_wrapper.cu:277 | printf("Total time:\n") — pure wall-clock timing block, no correctness check or file write | bucket5 | weak | paper Threats — wall-clock timer only, no correctness evidence |
| rodinia-bptree-omp | rodinia/rodinia-src/openmp/b+tree/kernel/kernel_cpu.c:136 | printf("Total time:\n") — pure wall-clock timing block, no correctness check or file write | bucket5 | weak | paper Threats — wall-clock timer only, no correctness evidence |
| rodinia-cfd-cuda | rodinia/rodinia-src/cuda/cfd/euler3d.cu:591 | std::cout << "Saving solution..." — immediately before dump() which writes density+momentum files via std::ofstream (unconditional) | bucket3 | strong | file_hash on density |
| rodinia-cfd-omp | rodinia/rodinia-src/openmp/cfd/euler3d_cpu.cpp:498 | std::cout << "Saving solution..." — immediately before dump() which writes density+momentum files via std::ofstream (unconditional) | bucket3 | strong | file_hash on density |
| rodinia-hotspot-cuda | rodinia/rodinia-src/cuda/hotspot/hotspot.cu:330 | printf("Ending simulation\n") — unconditional, immediately before writeoutput() writes output.out via fopen+fprintf | bucket3 | strong | file_hash on output.out |
| rodinia-hotspot-omp | rodinia/rodinia-src/openmp/hotspot/hotspot_openmp.cpp:314 | printf("Ending simulation\n") — unconditional, immediately before writeoutput() writes output.out via fopen+fprintf | bucket3 | strong | file_hash on output.out |
| rodinia-lavamd-cuda | rodinia/rodinia-src/cuda/lavaMD/kernel/kernel_gpu_cuda_wrapper.cu:237 | printf("Total time:\n") — pure wall-clock timing block, no correctness check or file write | bucket5 | weak | paper Threats — wall-clock timer only, no correctness evidence |
| rodinia-lavamd-omp | rodinia/rodinia-src/openmp/lavaMD/kernel/kernel_cpu.c:211 | printf("Total time:\n") — pure wall-clock timing block, no correctness check or file write | bucket5 | weak | paper Threats — wall-clock timer only, no correctness evidence |
| rodinia-nn-omp | rodinia/rodinia-src/openmp/nn/nn_openmp.c:156 | printf("total time : %15.12f s", ...) — pure wall-clock, no file write, no correctness gate | bucket5 | weak | paper Threats — wall-clock timer only, no correctness evidence |
| rodinia-nw-omp | rodinia/rodinia-src/openmp/nw/needle.cpp:314 | `#define TRACEBACK` active at line 314 → `fopen("result.txt","w")` at line 317 writes NW alignment traceback unconditionally (deterministic output) | bucket3 | strong | file_hash on result.txt (S4 determinism pre-flight required) |
| rodinia-nw-opencl | rodinia/rodinia-src/opencl/nw/nw.c:393 | printf("Processing lower-right matrix\n") — unconditional progress message before kernel2 enqueue; TRACEBACK file write at line 421 is disabled (//#define TRACEBACK); Computation Done at line 483 also unconditional | bucket5 | weak | paper Threats — progress\|completion signals only, TRACEBACK disabled so no file output |
| rodinia-srad-cuda | rodinia/rodinia-src/cuda/srad/srad_v2/srad.cu:253 | printf("Computation Done\n") — unconditional after main loop; OUTPUT block at lines 242-251 is #ifdef-gated and not active; no file write | bucket5 | weak | paper Threats — completion signal only, no correctness evidence |
| rodinia-srad-omp | rodinia/rodinia-src/openmp/srad/srad_v2/srad.cpp:208 | printf("Computation Done\n") — unconditional after main loop; OUTPUT block at lines 197-206 is #ifdef-gated and not active; no file write | bucket5 | weak | paper Threats — completion signal only, no correctness evidence |
| rodinia-bptree-opencl | rodinia/rodinia-src/opencl/b+tree/kernel/kernel_gpu_opencl_wrapper.c:697 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or upgrade to exit_code only |
| rodinia-gaussian-cuda | rodinia/rodinia-src/cuda/gaussian/gaussian.cu:203 | printf("\nTime total (including memory transfers)\t%f sec\n", time_total * 1e-6) unconditional, wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-gaussian-opencl | rodinia/rodinia-src/opencl/gaussian/gaussianElim.cpp:199 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-heartwall-cuda | rodinia/rodinia-src/cuda/heartwall/main.cu:641 | printf("frame progress: ") unconditional progress label, no numeric; write_data("result.txt") is inside #ifdef OUTPUT (not set by default build) | bucket5 | weak | stdout_pattern on frame progress or exit_code only |
| rodinia-heartwall-omp | rodinia/rodinia-src/openmp/heartwall/main.c:522 | printf("frame progress: ") unconditional progress label, no numeric; write_data("result.txt") inside #ifdef OUTPUT (not set by default build) | bucket5 | weak | stdout_pattern on frame progress or exit_code only |
| rodinia-heartwall-opencl | rodinia/rodinia-src/opencl/heartwall/kernel/kernel_gpu_opencl_wrapper.c:1224 | printf("frame progress: ") unconditional progress label, no numeric; write_data inside #ifdef OUTPUT (not set by default build) | bucket5 | weak | stdout_pattern on frame progress or exit_code only |
| rodinia-hotspot-opencl | rodinia/rodinia-src/opencl/hotspot/hotspot.c:385 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-hotspot3d-cuda | rodinia/rodinia-src/cuda/hotspot3D/3D.cu:199 | printf("Accuracy: %e\n", acc) unconditional; acc = accuracy(tempOut, answer, N) compares GPU vs CPU reference; `writeoutput(tempOut, ..., ofile)` also called unconditionally at line 200 → latent bucket3 alternative | bucket4 | medium | numeric_comparison on Accuracy tol=1e-3 (or bucket3 file_hash on ofile) |
| rodinia-hotspot3d-omp | rodinia/rodinia-src/openmp/hotspot3D/3D.c:265 | printf("Accuracy: %e\n", acc) unconditional; acc = accuracy(tempOut, answer, N) compares OMP vs CPU reference; `writeoutput(tempOut, ..., ofile)` also called unconditionally at line 266 → latent bucket3 alternative | bucket4 | medium | numeric_comparison on Accuracy tol=1e-3 (or bucket3 file_hash on ofile) |
| rodinia-hotspot3d-opencl | rodinia/rodinia-src/opencl/hotspot3D/3D.c:398 | printf("Accuracy: %e\n", acc) unconditional, outside #ifdef TIMING block; acc = accuracy(tempOut, answer, N); `writeoutput(tempOut, ..., ofile)` also called unconditionally at line 400 → latent bucket3 alternative | bucket4 | medium | numeric_comparison on Accuracy tol=1e-3 (or bucket3 file_hash on ofile) |
| rodinia-hybridsort-opencl | rodinia/rodinia-src/opencl/hybridsort/hybridsort.c:249 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-kmeans-omp | rodinia/rodinia-src/openmp/kmeans/kmeans_openmp/kmeans.c:223 | printf("number of Clusters %d\n", nclusters) unconditional; nclusters echoes the -k input arg (default 5), not a computed result | bucket5 | weak | stdout_pattern on completion sentinel; nclusters is input echo not result |
| rodinia-lavamd-opencl | rodinia/rodinia-src/opencl/lavaMD/kernel/kernel_gpu_opencl_wrapper.c:566 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-lud-cuda | rodinia/rodinia-src/cuda/lud/cuda/lud.cu:169 | printf("Time consumed(ms): %lf\n", 1000*get_interval_by_sec(&sw)) unconditional, wall-clock; -v verify not set in spec args so lud_verify() not called | bucket5 | weak | add -v to run args and match ">>>Verify<<<<" or lud_verify mismatch absence |
| rodinia-lud-omp | rodinia/rodinia-src/openmp/lud/omp/lud.c:123 | printf("Time consumed(ms): %lf\n", 1000*get_interval_by_sec(&sw)) unconditional, wall-clock; -v verify not set in spec args so lud_verify() not called | bucket5 | weak | add -v to run args and match ">>>Verify<<<<" or lud_verify mismatch absence |
| rodinia-lud-opencl | rodinia/rodinia-src/opencl/lud/ocl/lud.cpp:385 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | add -v to run args and match ">>>Verify<<<<" |
| rodinia-myocyte-cuda | rodinia/rodinia-src/cuda/myocyte/work.cu:233 | printf("Time spent in different stages of the application:\n") unconditional timing header; work.cu:169 writes output.txt unconditionally with y[i][j][k] ODE state vectors | bucket3 | strong | file_hash on output.txt (ODE state vector, deterministic) |
| rodinia-myocyte-omp | rodinia/rodinia-src/openmp/myocyte/main.c:2667 | printf("Time spent in different stages of the application:\n") unconditional timing header; main.c:2436 writes output.txt unconditionally with y[i][j][k] ODE state vectors | bucket3 | strong | file_hash on output.txt (ODE state vector, deterministic) |
| rodinia-myocyte-opencl | rodinia/rodinia-src/opencl/myocyte/kernel/kernel_gpu_opencl_wrapper.c:454 | printf("Time spent in different stages of the application:\n") unconditional timing header; main.c:309 writes output.txt unconditionally with y[i][j][k] ODE state vectors | bucket3 | strong | file_hash on output.txt (ODE state vector, deterministic) |
| rodinia-nn-cuda | rodinia/rodinia-src/cuda/nn/nn_cuda.cu:185 | printf("%s --> Distance=%f\n", records[i].recString, records[i].distance) gated on !quiet; spec has no -q flag so quiet=0 → always prints; Distance is computed float result | bucket4 | medium | numeric_comparison on Distance= tol=1e-3 |
| rodinia-nw-cuda | rodinia/rodinia-src/cuda/nw/needle.cu:177 | printf("Processing bottom-right matrix\n") unconditional progress label, no numeric; TRACEBACK file write is commented out (#define TRACEBACK commented) | bucket5 | weak | stdout_pattern on progress label; no result oracle available |
| rodinia-particlefilter-cuda | rodinia/rodinia-src/cuda/particlefilter/ex_particle_CUDA_naive_seq.cu:693 | printf("ENTIRE PROGRAM TOOK %f\n", elapsed_time(start, endParticleFilter)) unconditional, wall-clock float; XE\|YE position prints available per iteration | bucket5 | weak | upgrade to numeric_comparison on XE or YE (object position per frame) |
| rodinia-particlefilter-omp | rodinia/rodinia-src/openmp/particlefilter/ex_particle_OPENMP_seq.c:596 | printf("ENTIRE PROGRAM TOOK %f\n", elapsed_time(start, endParticleFilter)) unconditional, wall-clock float; XE\|YE position prints available per iteration | bucket5 | weak | upgrade to numeric_comparison on XE or YE (object position per frame) |
| rodinia-particlefilter-opencl | rodinia/rodinia-src/opencl/particlefilter/ex_particle_OCL_double_seq.cpp:1034 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float | bucket5 | weak | stdout_pattern on completion sentinel or exit_code only |
| rodinia-pathfinder-cuda | rodinia/rodinia-src/cuda/pathfinder/pathfinder.cu:213 | printf("pyramidHeight: %d\ngridSize: [%d]...\n") unconditional, echoes input configuration parameters not computation result | bucket5 | weak | no result oracle; stdout_pattern on config print confirms invocation only |
| rodinia-pathfinder-omp | rodinia/rodinia-src/openmp/pathfinder/pathfinder.cpp:110 | pin_stats_dump(cycles) expands to printf("timer: %Lu\n", cycles) unconditional, wall-clock CPU cycle count | bucket5 | weak | stdout_pattern on timer: confirms run completion; no result oracle |
| rodinia-srad-opencl | rodinia/rodinia-src/opencl/srad/kernel/kernel_gpu_opencl_wrapper.c:894 | printf("Iterations Progress: hidden") unconditional constant string with no numeric value, no output file written | bucket5 | weak | stdout_pattern on constant string confirms execution; no result oracle |
| rodinia-streamcluster-cuda | rodinia/rodinia-src/cuda/streamcluster/streamcluster_cuda_cpu.cpp:932 | printf("time = %lfs\n", t2-t1) unconditional, wall-clock float; output.txt written via outcenterIDs() but lrand48() with no fixed seed → non-deterministic | bucket5 | weak | stdout_pattern on time = confirms run completion; output non-deterministic |
| rodinia-streamcluster-omp | rodinia/rodinia-src/openmp/streamcluster/streamcluster_omp.cpp:1287 | printf("loops=%d\n", d) unconditional; d counts local search iterations driven by lrand48() with no fixed seed → non-deterministic iteration count | bucket5 | weak | stdout_pattern on loops= confirms run completion; value non-deterministic |
| rodinia-streamcluster-opencl | rodinia/rodinia-src/opencl/streamcluster/streamcluster.cpp:988 | printf("Total: %f\n", total_time) inside #ifdef TIMING (Makefile passes -DTIMING), wall-clock float; output.txt non-deterministic | bucket5 | weak | stdout_pattern on Total: confirms run completion; no deterministic result oracle |
| hecbench-md-cuda | HeCBench-master/src/md-cuda/reference.h:66 | `std::cout << "Max error between host and device: " << max_error << "\n"` (unconditional numeric print; max_error computed by host-vs-device force comparison over all atoms; no if-gate on tolerance) | bucket4 | medium | numeric_comparison on max_error with tol=1e-4 (single precision); pattern `Max error between host and device: ([0-9.eE+-]+)` |
| hecbench-md-omp_target | HeCBench-master/src/md-cuda/reference.h:66 | `std::cout << "Max error between host and device: " << max_error << "\n"` (unconditional numeric print; md-omp Makefile: `-I../md-cuda` reuses md-cuda/reference.h for both variants) | bucket4 | medium | numeric_comparison on max_error with tol=1e-4; pattern `Max error between host and device: ([0-9.eE+-]+)` |
| mixbench-mixbench-cuda | mixbench/mixbench-src/mixbench-cuda/mix_kernels_cuda.cu:177 | `printf("--- CSV data ---\n")` (unconditional header before throughput CSV rows; no correctness self-check; output is GFLOPS/GB/s timing data) | bucket5 | weak | paper Threats — oracle measures throughput (GFLOPS\|GB/s), not translation correctness; `CSV data` only confirms execution completed |
| mixbench-mixbench-omp | mixbench/mixbench-src/mixbench-cpu/mix_kernels_cpu.cpp:283 | `std::cout << "--- CSV data ---" << std::endl` (unconditional header before throughput CSV rows; no correctness self-check; output is GFLOPS/GB/s timing data) | bucket5 | weak | paper Threats — oracle measures throughput (GFLOPS\|GB/s), not translation correctness; `CSV data` only confirms execution completed |
| mixbench-mixbench-opencl | mixbench/mixbench-src/mixbench-opencl/mix_kernels_ocl.cpp:418 | `printf("--- CSV data ---\n")` (unconditional header before throughput CSV rows; no correctness self-check; output is GFLOPS/GB/s timing data) | bucket5 | weak | paper Threats — oracle measures throughput (GFLOPS\|GB/s), not translation correctness; `CSV data` only confirms execution completed |

## Bucket Counts

- **bucket1 (already-strong):** 0
- **bucket2 (regex-tighten):** 0
- **bucket3 (needs-file_hash):** 10 — bfs-cuda, bfs-omp, cfd-cuda, cfd-omp, hotspot-cuda, hotspot-omp, nw-omp, myocyte-cuda, myocyte-omp, myocyte-opencl
- **bucket4 (needs-numeric_comparison):** 6 — hotspot3d-cuda, hotspot3d-omp, hotspot3d-opencl, nn-cuda, hecbench-md-cuda, hecbench-md-omp_target
- **bucket5 (truly-weak):** 37
- **Total:** 53

## S4/S5 Upgrade Scope Implications

**S4a+S4b (Rodinia weak, 18 specs → 7 upgrades expected):**
- bucket3 candidates (7): bfs-cuda, bfs-omp, cfd-cuda, cfd-omp, hotspot-cuda, hotspot-omp, nw-omp
- bucket5 (11, no upgrade): backprop×3, bptree-cuda, bptree-omp, lavamd-cuda, lavamd-omp, nn-omp, nw-opencl, srad-cuda, srad-omp — ship `oracle_strength: "weak"` + Threats note

**S5 (35 unknown, 9 upgrades expected — exceeds the ≤5 genuine-implementation hard cap per HANDOFF §5 S5):**
- bucket3 candidates (3): myocyte-cuda, myocyte-omp, myocyte-opencl — same upgrade pattern (file_hash on `output.txt`)
- bucket4 candidates (6): hotspot3d-cuda, hotspot3d-omp, hotspot3d-opencl, nn-cuda, hecbench-md-cuda, hecbench-md-omp_target
- bucket5 (26, no upgrade): all opencl `Total:` (≥7 specs share identical #ifdef TIMING print pattern), heartwall×3 (OUTPUT macro off), lud×3 (-v not set), nw-cuda, pathfinder×2, srad-opencl, streamcluster×3 (non-deterministic seeds), gaussian×2, hybridsort-opencl, kmeans-omp, lavamd-opencl, particlefilter×3, bptree-opencl, hotspot-opencl, mixbench×3

**Hard-cap compliance:** 3 bucket3 (myocyte) + 6 bucket4 = 9 genuine-implementation upgrades from the 35 unknowns. HANDOFF §5 S5 hard cap is ≤5. **This exceeds the cap.** Options per HANDOFF §5 S5: (a) defer bucket4 numeric_comparison upgrades to camera-ready and mark 6 specs `oracle_strength: "weak"` now; (b) split S5 across an additional session; (c) fast-path myocyte (3 file_hash specs share identical filename+pattern, so they are one logical upgrade not three); (d) reclassify hotspot3d×3 + md×2 as bucket2 (tighten `stdout_pattern` from `Accuracy:`/`Max error` to require a numeric field — 1-line spec edit each) — drops genuine upgrades to 3 bucket3 (myocyte) + 1 bucket4 (nn-cuda) = 4, comfortably under the cap.

## Non-Determinism Flags (require S4 pre-flight before `file_hash`)

Per HANDOFF §3 Rule 12, every `file_hash` candidate must pass a two-run SHA-256 determinism check before oracle upgrade. Specs to pre-flight:

- bfs-cuda, bfs-omp, cfd-cuda, cfd-omp, hotspot-cuda, hotspot-omp, nw-omp (S4)
- myocyte-cuda, myocyte-omp, myocyte-opencl (S5)

If any fails determinism → demote to `oracle_strength: "weak"` + Threats note; do **NOT** ship `file_hash`.

## Pre-Identified Non-Deterministic Specs

- streamcluster (cuda, omp, opencl): `lrand48()` with no fixed seed → non-deterministic even across identical runs. bucket5 independent of any file_hash consideration.

## Shared Infrastructure Observations

- **Rodinia OpenCL `#ifdef TIMING` family:** 7+ opencl specs share the same `printf("Total: %f\n", total_time)` pattern inside a timing guard enabled by `-DTIMING` in Makefiles. Any future regex-tightening or upgrade here would apply uniformly.
- **Rodinia Heartwall `#ifdef OUTPUT`:** all 3 heartwall variants gate `write_data("result.txt")` on `#ifdef OUTPUT`, disabled in default build. Enabling OUTPUT would flip all 3 to bucket3 — out of S3 scope (no benchmark-source edits).
- **md-cuda `reference.h` shared:** md-omp re-uses md-cuda's reference.h via `-I../md-cuda`. Both specs cite the same source line (md-cuda/reference.h:66).

## Provenance

- Audit executed S3 (2026-04-18) by `s3-audit-team` (Opus advisor + 3 Sonnet workers: `s3-weak-worker`, `s3-rodinia-unknown`, `s3-other-unknown`).
- Per-worker scratch files: `/tmp/s3-rows/weak.md`, `rodinia-unknown.md`, `other-unknown.md`.
- Advisor spot-check: 6 citations re-verified against source (bfs-cuda:266, cfd-cuda:591, hotspot3d-cuda:199, hotspot3d-omp:265, myocyte-cuda:233, nn-cuda:185, md-cuda/reference.h:66, nw-omp:312→314, mixbench-cuda:177). All line numbers accurate.
- Advisor corrections: (1) fixed doubled `rodinia-src/rodinia-src/` path prefix in rodinia-unknown rows; (2) corrected mixbench `oracle_strength` from `strong` to `weak` (bucket5 required per bucket defs); (3) reclassified nw-omp from bucket5 to bucket3 (worker noted `#define TRACEBACK` active but wrote the classification against current wall-clock pattern rather than available upgrade path — bucket3 reflects the upgrade target per audit contract).
- Drives S4a/S4b/S5 upgrade scope per HANDOFF §5.
- Cross-checked by `s3-review` team (self-critic + code-reviewer + code-simplifier) before commit.
