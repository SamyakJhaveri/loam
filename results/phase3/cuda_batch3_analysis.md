# CUDA Batch 2+3 — Full Harness Analysis Report

**Generated**: 2026-03-03T10:10:24
**Platform**: Linux x86_64, NVIDIA GeForce RTX 4070 (sm_89, Ada Lovelace, 12 GB)
**Compiler**: nvcc 12.3, gcc 12.4.0
**Kernels tested**: 40 (Batch 2: 20, Batch 3: 20)

## Summary

| Metric | Batch 2 | Batch 3 | Total |
|--------|---------|---------|-------|
| Kernels tested | 20 | 20 | 40 |
| BUILD PASS | 20 | 20 | 40 |
| BUILD FAIL | 0 | 0 | 0 |
| RUN PASS | 20 | 20 | 40 |
| RUN FAIL | 0 | 0 | 0 |
| RUN TIMEOUT | 0 | 0 | 0 |
| RUN ERROR | 0 | 0 | 0 |
| VERIFY PASS | 20 | 20 | 40 |
| VERIFY FAIL | 0 | 0 | 0 |
| **Full PASS** | 20 | 20 | 40 |

## Timing Statistics

- **Build times**: min=0.56s, max=126.19s, avg=4.38s, total=175.2s
- **Run times**: min=0.062s, max=195.036s, avg=7.404s, total=296.2s
- **Total wall time**: ~471s (build+run, excludes clean)

## Detailed Results

Legend: ✅ PASS | ❌ FAIL | ⏱ TIMEOUT | 🚫 BUILD FAIL | ⚠ ERROR | ❓ MISSING

| # | Kernel | Batch | Build | Build Time | Run | Run Time | Exit | Verify | Strategy | Stdout (first line) |
|---|--------|-------|-------|------------|-----|----------|------|--------|----------|---------------------|
| 1 | babelstream | B2 | ✅ | 1.50s | ✅ | 1.489s | 0 | ✅ | stdout_pattern | Running kernels 100 times |
| 2 | backprop | B2 | ✅ | 2.04s | ✅ | 0.090s | 0 | ✅ | stdout_pattern | Random number generator seed: 7 |
| 3 | ccsd-trpdrv | B2 | ✅ | 3.66s | ✅ | 1.073s | 0 | ✅ | stdout_pattern | Test driver for cbody with nocc=160, nvir=400, maxiter=1, nkpass=1 |
| 4 | deredundancy | B2 | ✅ | 2.53s | ✅ | 13.615s | 0 | ✅ | stdout_pattern | input:	../deredundancy-sycl/testData.fasta |
| 5 | feynman-kac | B2 | ✅ | 0.65s | ✅ | 195.036s | 0 | ✅ | stdout_pattern | FEYNMAN_KAC_2D: |
| 6 | fpc | B2 | ✅ | 0.64s | ✅ | 0.415s | 0 | ✅ | stdout_pattern | fpc: average device offload time 0.002544 (s) |
| 7 | ga | B2 | ✅ | 0.70s | ✅ | 0.089s | 0 | ✅ | stdout_pattern | Total kernel execution time 0.000273 (s) |
| 8 | keccaktreehash | B2 | ✅ | 2.46s | ✅ | 7.420s | 0 | ✅ | stdout_pattern | Number of threads per block             NB_THREADS           64  |
| 9 | laplace3d | B2 | ✅ | 0.68s | ✅ | 0.279s | 0 | ✅ | stdout_pattern | Grid dimensions: 128 x 128 x 128 |
| 10 | lulesh | B2 | ✅ | 3.31s | ✅ | 0.181s | 0 | ✅ | stdout_pattern | Running problem size 45^3 per domain until completion |
| 11 | maxpool3d | B2 | ✅ | 0.61s | ✅ | 3.245s | 0 | ✅ | stdout_pattern | input image width 2048 Hstride 2 |
| 12 | md5hash | B2 | ✅ | 1.08s | ✅ | 0.356s | 0 | ✅ | stdout_pattern | Searching keys of length 7 bytes and 10 values per byte |
| 13 | pathfinder | B2 | ✅ | 0.83s | ✅ | 0.071s | 0 | ✅ | exit_code | Total kernel execution time: 0.000061 (s) |
| 14 | pso | B2 | ✅ | 0.90s | ✅ | 0.075s | 0 | ✅ | stdout_pattern | Number of particles is 30 |
| 15 | rmsnorm | B2 | ✅ | 0.67s | ✅ | 0.062s | 0 | ✅ | stdout_pattern | Checking block size 32. |
| 16 | secp256k1 | B2 | ✅ | 126.19s | ✅ | 0.083s | 0 | ✅ | stdout_pattern | Average kernel execution time: 0.002539 (s) |
| 17 | softmax-online | B2 | ✅ | 3.12s | ✅ | 19.096s | 0 | ✅ | stdout_pattern | Using kernel baseline 1 |
| 18 | thomas | B2 | ✅ | 1.55s | ✅ | 1.541s | 0 | ✅ | stdout_pattern | Average serial execution time: 103.030937 (ms) |
| 19 | tissue | B2 | ✅ | 0.64s | ✅ | 12.253s | 0 | ✅ | stdout_pattern | PASS |
| 20 | tsp | B2 | ✅ | 0.66s | ✅ | 0.099s | 0 | ✅ | stdout_pattern | 2-opt TSP CUDA GPU code v2.3 |
| 21 | bezier-surface | B3 | ✅ | 1.01s | ✅ | 0.081s | 0 | ✅ | stdout_pattern | Read data from file input/control.txt |
| 22 | convolution3d | B3 | ✅ | 0.96s | ✅ | 0.090s | 0 | ✅ | stdout_pattern | 3D convolution (FP32) |
| 23 | crc64 | B3 | ✅ | 1.43s | ✅ | 0.256s | 0 | ✅ | stdout_pattern | Running 1 tests with seed 1 |
| 24 | floydwarshall | B3 | ✅ | 0.61s | ✅ | 0.740s | 0 | ✅ | stdout_pattern | Average kernel execution time 0.006570 (s) |
| 25 | gaussian | B3 | ✅ | 1.42s | ✅ | 0.076s | 0 | ✅ | stdout_pattern | Workgroup size of kernel 1 = 256, Workgroup size of kernel 2= 16 X 16 |
| 26 | geglu | B3 | ✅ | 1.07s | ✅ | 18.674s | 0 | ✅ | stdout_pattern | PASS |
| 27 | heat2d | B3 | ✅ | 0.56s | ✅ | 0.231s | 0 | ✅ | stdout_pattern | Ly,Lx = 4096,4096 |
| 28 | iso2dfd | B3 | ✅ | 1.02s | ✅ | 0.138s | 0 | ✅ | stdout_pattern | Initializing ...  |
| 29 | jenkins-hash | B3 | ✅ | 0.62s | ✅ | 0.759s | 0 | ✅ | stdout_pattern | input string: Four score and seven years ago hash is cd628161 |
| 30 | knn | B3 | ✅ | 0.62s | ✅ | 7.279s | 0 | ✅ | stdout_pattern | Number of reference points      :   4096 |
| 31 | mandelbrot | B3 | ✅ | 0.99s | ✅ | 0.231s | 0 | ✅ | stdout_pattern | No Print() output due to size too large |
| 32 | mis | B3 | ✅ | 0.65s | ✅ | 0.066s | 0 | ✅ | exit_code | ECL-MIS v1.3 (main.cu) |
| 33 | murmurhash3 | B3 | ✅ | 0.63s | ✅ | 0.573s | 0 | ✅ | stdout_pattern | Average kernel execution time 0.004432 (s) |
| 34 | myocyte | B3 | ✅ | 1.08s | ✅ | 0.090s | 0 | ✅ | exit_code | Total kernel execution time 0.018142 (s) |
| 35 | nw | B3 | ✅ | 0.80s | ✅ | 1.955s | 0 | ✅ | stdout_pattern | WG size of kernel = 16  |
| 36 | perplexity | B3 | ✅ | 0.72s | ✅ | 0.237s | 0 | ✅ | stdout_pattern | Average kernel execution time: 0.007938 (s) |
| 37 | popcount | B3 | ✅ | 0.65s | ✅ | 1.926s | 0 | ✅ | exit_code | Average kernel execution time (pc1): 586.778000 (us) |
| 38 | sobol | B3 | ✅ | 2.79s | ✅ | 5.405s | 0 | ✅ | stdout_pattern | Allocating CPU memory... |
| 39 | stencil1d | B3 | ✅ | 0.60s | ✅ | 0.619s | 0 | ✅ | stdout_pattern | Average kernel execution time: 0.002435 (s) |
| 40 | triad | B3 | ✅ | 2.55s | ✅ | 0.184s | 0 | ✅ | stdout_pattern | >> Executing Triad with vectors of length 4194304 and block size of 16384 elemen |

## Passing Kernels (40/40)

- **babelstream**: build=1.50s, run=1.489s, verify=stdout_pattern — triad_bandwidth=466191.873MB/s, copy_bandwidth=484183.951MB/s
- **backprop**: build=2.04s, run=0.090s, verify=stdout_pattern
- **ccsd-trpdrv**: build=3.66s, run=1.073s, verify=stdout_pattern
- **deredundancy**: build=2.53s, run=13.615s, verify=stdout_pattern — offload_time=13.557056s
- **feynman-kac**: build=0.65s, run=195.036s, verify=stdout_pattern — kernel_time=194.969857s
- **fpc**: build=0.64s, run=0.415s, verify=stdout_pattern
- **ga**: build=0.70s, run=0.089s, verify=stdout_pattern — kernel_time=0.000273s
- **keccaktreehash**: build=2.46s, run=7.420s, verify=stdout_pattern
- **laplace3d**: build=0.68s, run=0.279s, verify=stdout_pattern — kernel_time=5.8e-05s
- **lulesh**: build=3.31s, run=0.181s, verify=stdout_pattern — elapsed_time=0.14s, grind_time=0.039485322us/z/c
- **maxpool3d**: build=0.61s, run=3.245s, verify=stdout_pattern
- **md5hash**: build=1.08s, run=0.356s, verify=stdout_pattern
- **pathfinder**: build=0.83s, run=0.071s, verify=exit_code — kernel_time=6.1e-05s
- **pso**: build=0.90s, run=0.075s, verify=stdout_pattern
- **rmsnorm**: build=0.67s, run=0.062s, verify=stdout_pattern — kernel_time=0.0151ms
- **secp256k1**: build=126.19s, run=0.083s, verify=stdout_pattern
- **softmax-online**: build=3.12s, run=19.096s, verify=stdout_pattern — kernel_time=16.1743ms
- **thomas**: build=1.55s, run=1.541s, verify=stdout_pattern — kernel_time=2.78282ms
- **tissue**: build=0.64s, run=12.253s, verify=stdout_pattern — kernel_time=0.064317s
- **tsp**: build=0.66s, run=0.099s, verify=stdout_pattern
- **bezier-surface**: build=1.01s, run=0.081s, verify=stdout_pattern — kernel_time=1.0ms
- **convolution3d**: build=0.96s, run=0.090s, verify=stdout_pattern — kernel_time_s1=7.454094us, kernel_time_s2=7.514458us, kernel_time_s3=7.536409us
- **crc64**: build=1.43s, run=0.256s, verify=stdout_pattern
- **floydwarshall**: build=0.61s, run=0.740s, verify=stdout_pattern — kernel_time=0.00657s
- **gaussian**: build=1.42s, run=0.076s, verify=stdout_pattern — kernel_time=874.0us
- **geglu**: build=1.07s, run=18.674s, verify=stdout_pattern — kernel_time=134.652008us
- **heat2d**: build=0.56s, run=0.231s, verify=stdout_pattern — throughput=449.641GB/s
- **iso2dfd**: build=1.02s, run=0.138s, verify=stdout_pattern — kernel_time=147.852us
- **jenkins-hash**: build=0.62s, run=0.759s, verify=stdout_pattern — kernel_time=0.00241s
- **knn**: build=0.62s, run=7.279s, verify=stdout_pattern — total_time=3.597176s
- **mandelbrot**: build=0.99s, run=0.231s, verify=stdout_pattern — kernel_time=0.125955s
- **mis**: build=0.65s, run=0.066s, verify=exit_code — compute_time=0.000154s, node_throughput=807.487247Mnodes/s
- **murmurhash3**: build=0.63s, run=0.573s, verify=stdout_pattern — kernel_time=0.004432s
- **myocyte**: build=1.08s, run=0.090s, verify=exit_code — kernel_time=0.018142s
- **nw**: build=0.80s, run=1.955s, verify=stdout_pattern — kernel_time=0.021946s
- **perplexity**: build=0.72s, run=0.237s, verify=stdout_pattern — kernel_time=0.007938s
- **popcount**: build=0.65s, run=1.926s, verify=exit_code — kernel_time_pc1=586.778us, kernel_time_pc2=470.09us
- **sobol**: build=2.79s, run=5.405s, verify=stdout_pattern — kernel_time=0.0104468s
- **stencil1d**: build=0.60s, run=0.619s, verify=stdout_pattern — kernel_time=0.002435s
- **triad**: build=2.55s, run=0.184s, verify=stdout_pattern — triad_gflops=2.57618GFLOPS/s

## Verification Strategies Used

- **stdout_pattern**: 36 kernels
- **exit_code**: 4 kernels

## Performance Metrics (from correctness runs)

| Kernel | Metric | Value | Unit |
|--------|--------|-------|------|
| babelstream | triad_bandwidth | 466191.873 | MB/s |
| babelstream | copy_bandwidth | 484183.951 | MB/s |
| deredundancy | offload_time | 13.557056 | s |
| feynman-kac | kernel_time | 194.969857 | s |
| ga | kernel_time | 0.000273 | s |
| laplace3d | kernel_time | 5.8e-05 | s |
| lulesh | elapsed_time | 0.14 | s |
| lulesh | grind_time | 0.039485322 | us/z/c |
| pathfinder | kernel_time | 6.1e-05 | s |
| rmsnorm | kernel_time | 0.0151 | ms |
| softmax-online | kernel_time | 16.1743 | ms |
| thomas | kernel_time | 2.78282 | ms |
| tissue | kernel_time | 0.064317 | s |
| bezier-surface | kernel_time | 1.0 | ms |
| convolution3d | kernel_time_s1 | 7.454094 | us |
| convolution3d | kernel_time_s2 | 7.514458 | us |
| convolution3d | kernel_time_s3 | 7.536409 | us |
| floydwarshall | kernel_time | 0.00657 | s |
| gaussian | kernel_time | 874.0 | us |
| geglu | kernel_time | 134.652008 | us |
| heat2d | throughput | 449.641 | GB/s |
| iso2dfd | kernel_time | 147.852 | us |
| jenkins-hash | kernel_time | 0.00241 | s |
| knn | total_time | 3.597176 | s |
| mandelbrot | kernel_time | 0.125955 | s |
| mis | compute_time | 0.000154 | s |
| mis | node_throughput | 807.487247 | Mnodes/s |
| murmurhash3 | kernel_time | 0.004432 | s |
| myocyte | kernel_time | 0.018142 | s |
| nw | kernel_time | 0.021946 | s |
| perplexity | kernel_time | 0.007938 | s |
| popcount | kernel_time_pc1 | 586.778 | us |
| popcount | kernel_time_pc2 | 470.09 | us |
| sobol | kernel_time | 0.0104468 | s |
| stencil1d | kernel_time | 0.002435 | s |
| triad | triad_gflops | 2.57618 | GFLOPS/s |
