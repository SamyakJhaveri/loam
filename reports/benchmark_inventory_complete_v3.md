# ParBench Complete Benchmark Inventory v3
## Validation and Normalization Report — Augmented with Run Commands

---

## Executive Summary

This document provides a comprehensive inventory of 35 parallel computing benchmark repositories analyzed for the "Rosetta Stone" meta-benchmark project aimed at evaluating LLM-based code translation systems.

**Version 3 Additions:**
- Reference Platform Specification
- Explicit run commands for all benchmarks
- Correctness test configurations
- Performance benchmark configurations
- Standardized input configurations
- Systematic dependency capture

### Overview Statistics

| Metric | Count |
|--------|-------|
| Total archives downloaded | 40 |
| Successfully extracted | 35 |
| Failed downloads | 3 |
| Tier A (High Quality) | 30 |
| Tier B (Medium Quality) | 5 |

### Quality Distribution by Type

| Type | Count | Examples |
|------|-------|----------|
| Suite | 13 | HeCBench, PRK, Rodinia, RAJAPerf, NPB |
| Miniapp | 12 | BabelStream, CloverLeaf, LULESH, miniBUDE |
| Proxy App | 4 | SW4lite, CoMD, Kripke, PENNANT |
| Application | 4 | LAMMPS, GROMACS |
| Library | 4 | Kokkos Kernels, AMReX, MFEM, Trilinos |
| Microbenchmark | 3 | STREAM, OSU OMB |

---

## Reference Platform Specification

### Primary GPU Target
- **GPU Model:** NVIDIA GeForce RTX 4070
- **VRAM:** 12GB GDDR6X
- **Architecture:** Ada Lovelace (sm_89)
- **CUDA Cores:** 5,888
- **Memory Bandwidth:** ~504 GB/s
- **CUDA Toolkit:** 11.8+ or 12.x (with sm_89 support)
- **Driver Version:** 525.x or newer

### CPU Configuration
- **CPU Model:** AMD Ryzen 9 7900X
- **Cores/Threads:** 12 cores / 24 threads
- **Base Clock:** 4.7 GHz
- **Memory:** System RAM (assumed 32-64GB)

### Software Environment
- **Operating System:** Ubuntu 22.04 LTS
- **Compiler Suite:** GCC 11+, Clang 14+, NVCC (CUDA Toolkit)
- **MPI Implementation:** OpenMPI 4.x (CUDA-aware recommended)
- **CMake Version:** 3.20+

### Build Configuration Notes
- CUDA architecture flag: `-arch=sm_89` or `-DCUDA_ARCH=sm_89`
- For CMake: `-DCMAKE_CUDA_ARCHITECTURES=89`
- Optimization: `-O3 -march=native` for host code
- Memory constraint: 12GB VRAM limits some problem sizes

---

## Master Benchmark Table

| # | Benchmark | Type | APIs | Kernels | Build | Verification | Tier |
|---|-----------|------|------|---------|-------|--------------|------|
| 1 | BabelStream | Microbench | 16+ | 5 | CMake | Self-check | A |
| 2 | miniBUDE | Miniapp | 14 | 1 | CMake | Catch2+CI | A |
| 3 | CloverLeaf | Miniapp | 13 | 23 | CMake | Reference values | A |
| 4 | LULESH | Miniapp | 2 (MPI+OMP) | 10+ | CMake/Make | Symmetry check | A |
| 5 | PRK | Suite | 25+ | 12 | Make | Checksum | A |
| 6 | TeaLeaf | Miniapp | 8 | 15 | CMake | Test problems | A |
| 7 | miniMD | Miniapp | 4 | 7 | Make/CMake | Reference output | A |
| 8 | Neutral | Mini-app | 5 | 7 | Make | Tolerance check | A |
| 9 | miniWeather | Miniapp | 5 | 6 | CMake | Conservation | A |
| 10 | HeCBench | Suite | 4 | 513 | CMake | Reference impl | A |
| 11 | Rodinia | Suite | 3 | 24 | Make | Selective | A |
| 12 | PENNANT | Mini-app | 3 | 26 | Make | Energy cons. | A |
| 13 | SW4lite | Proxy App | 4 | 13 | Make/CMake | Analytical | A |
| 14 | Kokkos Kernels | Library | 7 | 50+ | CMake | GoogleTest | A |
| 15 | RAJAPerf | Suite | 7+ | 80 | CMake | Checksum | A |
| 16 | RAJAProxies | Suite | 5 | 3 apps | CMake | FOM metrics | A |
| 17 | ExaMiniMD | Miniapp | 6 | 12 | CMake | Binary snapshot | A |
| 18 | CoMD | Proxy App | 3 | 7 | Make | Energy cons. | A |
| 19 | Kripke | Miniapp | 8 | 6 | CMake | Convergence | A |
| 20 | PARSEC | Suite | 4 | 13 apps | Make | Output compare | A |
| 21 | OpenDwarfs | Suite | 1 (OpenCL) | 13 | Autotools | CPU reference | B |
| 22 | STAMP | Suite | 4 (TM) | 9 | Make | Assertion | A |
| 23 | NAS NPB | Suite | 2 | 11 | Make | Reference values | A |
| 24 | OSU OMB | Microbench | 6 | 87+ | Autotools | Data validation | A |
| 25 | miniAMR | Miniapp | 2 | 8 | Make | Checksum | A |
| 26 | miniFE | Miniapp | 10 | 6 | Make | Gold files | A |
| 27 | miniGhost | Miniapp | 3 | 7 | Make | Grid sum | A |
| 28 | HPCCG | Miniapp | 3 | 7 | Make | Convergence | B |
| 29 | HPCG | Benchmark | 3 | 8 | CMake/Make | V&V suite | A |
| 30 | HPL | Benchmark | 2 | 8 | Make | Residual | A |
| 31 | STREAM | Microbench | 1 | 4 | Make | Self-check | A |
| 32 | LAMMPS | Application | 5 | 40+ | CMake | GoogleTest | A |
| 33 | AMReX | Library | 5 | Many | CMake | CI/CD | A |
| 34 | MFEM | Library | 7 | Many | CMake/Make | Catch2 | A |
| 35 | GROMACS | Application | 7 | 6 major | CMake | GoogleTest | A |

---

## Detailed Benchmark Inventory

### 1. BabelStream
**Type:** Microbenchmark | **Tier:** A | **APIs:** 16+
**Repository:** https://github.com/UoB-HPC/BabelStream

**Kernels:** Copy, Mul, Add, Triad, Dot (memory bandwidth)

**APIs:** Serial, OpenMP, CUDA, HIP, OpenCL, OpenACC, Kokkos, RAJA, SYCL (accessor/USM), Thrust, C++ PSTL (data/indices/ranges), TBB, Futhark, Fortran, Rust, Java, Julia, Scala

**Dependencies:**
- Required: CMake >= 3.13.0, C++17 compiler
- CUDA Backend: CUDA Toolkit 11.0+ with sm_89 support
- Optional: Kokkos, RAJA, SYCL runtime (for respective backends)

**Build Commands:**
```bash
# CUDA build for RTX 4070
cmake -Bbuild -H. -DMODEL=cuda -DCUDA_ARCH=sm_89
cmake --build build

# OpenMP build
cmake -Bbuild -H. -DMODEL=omp
cmake --build build
```

**Run Commands:**
```bash
# CUDA execution (default)
./build/cuda-stream

# With custom array size and iterations
./build/cuda-stream -s 268435456 -n 100

# OpenMP execution
./build/omp-stream -s 134217728 -n 100
```

**Input Configurations:**
- Correctness Test: `-s 1048576 -n 10` (~seconds, validates numerical accuracy)
- Performance Benchmark: `-s 268435456 -n 100` (2^28 elements = ~6.4GB, ~minutes)
- Input Files: None required (internally generated)

**Key Options:**
- `-s, --arraysize`: Number of elements (default: 33,554,432)
- `-n, --numtimes`: Kernel iterations (default: 100)
- `--device`: GPU device index (default: 0)
- `--float`: Use single precision instead of double
- `--csv`: Output as CSV format

**Expected Output:**
```
BabelStream
Version: 5.0
Implementation: CUDA
Function    MBytes/sec  Min (sec)   Max         Average
Copy        500.234     0.00624     0.00639     0.00625
Triad       480.125     0.00417     0.00433     0.00419
```

**Verification:** Self-check with reference computation (epsilon × 100 tolerance)

---

### 2. miniBUDE
**Type:** Miniapp | **Tier:** A | **APIs:** 14
**Repository:** https://github.com/UoB-HPC/miniBUDE

**Kernels:** fasten (molecular docking energy calculation)

**APIs:** CUDA, HIP, OpenMP, OpenACC, SYCL, Kokkos, RAJA, OpenCL, TBB, Thrust, C++ std::indices/ranges, Serial, Julia

**Dependencies:**
- Required: CMake >= 3.14, C++17 compiler
- CUDA Backend: CUDA Toolkit with sm_89 support
- Optional: Catch2 (for unit tests)

**Build Commands:**
```bash
# CUDA build for RTX 4070
cmake -Bbuild -H. -DMODEL=cuda -DCUDA_ARCH=sm_89 -DCXX_EXTRA_FLAGS=-march=native
cmake --build build -j$(nproc)

# OpenMP build
cmake -Bbuild -H. -DMODEL=omp -DPPWI=4
cmake --build build
```

**Run Commands:**
```bash
# Basic execution
./build/cuda-bude --deck ./data/bm1 -i 8 -n 1024

# Performance benchmark
./build/cuda-bude --deck ./data/bm2 -i 8 -p 1,2,4,8,16,32,64,128 -w 32,64,128,256 --csv
```

**Input Configurations:**
- Correctness Test: `--deck ./data/bm1 -i 2 -n 1024` (~seconds)
- Performance Benchmark: `--deck ./data/bm2 -i 16 -p 1,2,4,8,16,32,64 -w 64,128,256` (~minutes)
- Input Files: `./data/bm1/`, `./data/bm2/` (forcefield.in, ligand.in, protein.in, poses.in)

**Key Options:**
- `-i, --iter`: Kernel iterations (default: 8)
- `-n, --poses`: Number of poses (0 = use deck maximum)
- `-p, --ppwi`: Poses-per-work-item values
- `-w, --wgsize`: Work-group/thread-block sizes
- `--deck`: Input deck directory path

**Expected Output:**
```
ppwi,wgsize,sum_ms,avg_ms,min_ms,max_ms,stddev_ms,interactions/s,gflops/s
1,128,156.28,19.535,18.92,21.43,0.89,5.2e+10,2.34e+02
```

**Verification:** Catch2 unit tests + CI compilation testing

---

### 3. CloverLeaf
**Type:** Miniapp | **Tier:** A | **APIs:** 13
**Repository:** https://github.com/UoB-HPC/CloverLeaf

**Kernels:** accelerate, advec_cell, advec_mom, calc_dt, flux_calc, generate_chunk, ideal_gas, PdV, reset_field, revert, update_halo, viscosity, field_summary (23 source files per API)

**APIs:** Serial, OpenMP, OpenMP Target, CUDA, HIP, Kokkos, SYCL (accessor/USM), C++ PSTL, TBB, OpenACC

**Dependencies:**
- Required: CMake >= 3.13.0, C++17 compiler
- CUDA Backend: CUDA Toolkit with sm_89 support
- Optional: MPI (for distributed runs)

**Build Commands:**
```bash
# CUDA build for RTX 4070
cmake -Bbuild -H. -DMODEL=cuda -DCUDA_ARCH=sm_89 -DENABLE_MPI=ON -DENABLE_PROFILING=ON
cmake --build build

# OpenMP build
cmake -Bbuild -H. -DMODEL=omp -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

**Run Commands:**
```bash
# Basic run with benchmark input
./build/cuda-cloverleaf --file InputDecks/clover_bm16.in

# Quick test
./build/cuda-cloverleaf --file InputDecks/clover_bm_short.in --profile

# List devices
./build/cuda-cloverleaf --list
```

**Input Configurations:**
- Correctness Test: `--file InputDecks/clover_bm_short.in` (960×960, 87 steps, ~seconds)
- Performance Benchmark: `--file InputDecks/clover_bm16.in` (3840×3840, 2955 steps, ~minutes)
- Input Files: `InputDecks/` directory (clover_bm*.in files)

**Key Options:**
- `--file, --in`: Input deck file (default: clover.in)
- `--out`: Output file destination
- `--device`: GPU device selection
- `--profile`: Enable kernel profiling

**Expected Output:**
```
Step 2955 Time 1.56E+01 timestep 4.0E-02
        Volume    Mass      Density   Pressure  Internal energy  Kinetic energy
   0    1.0E+02   2.0E+01   2.0E-01   8.79E-01  2.5E+00          4.85E+00

Test PASSED
```

**Verification:** Hardcoded reference values (kinetic energy) with < 0.001% tolerance

**Reference Verification Values:**
| Test Problem | Expected KE | Tolerance |
|--------------|-------------|-----------|
| Test 5 | 4.85350315783719 | < 0.001% |

---

### 4. LULESH
**Type:** Miniapp | **Tier:** A | **APIs:** 2 (MPI+OpenMP)
**Repository:** https://github.com/LLNL/LULESH

**Kernels:** CalcElemVolume, TimeIncrement, LagrangeLeapFrog, CalcForceForNodes, CalcHourglassControlForElems, CalcQForElems, ApplyMaterialPropertiesForElems, EvalEOSForElems, CalcEnergyForElems, CalcPressureForElems

**APIs:** MPI, OpenMP, Serial (Additional variants in RAJAProxies)

**Dependencies:**
- Required: C++ compiler, CMake or Make
- Optional: MPI implementation, OpenMP support

**Build Commands:**
```bash
# CMake build with MPI and OpenMP
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DWITH_MPI=On -DWITH_OPENMP=On ..
make -j8

# Makefile build
make CXX=mpig++ CXXFLAGS="-g -O3 -fopenmp -I. -Wall"
```

**Run Commands:**
```bash
# Serial execution
./lulesh2.0 -i 10 -s 30

# MPI + OpenMP
mpirun -np 8 ./lulesh2.0 -i 10 -s 45 -p

# Larger problem
./lulesh2.0 -i 100 -s 60
```

**Input Configurations:**
- Correctness Test: `-i 10 -s 30` (30³ mesh, 10 cycles, ~seconds)
- Performance Benchmark: `-i 100 -s 60` (60³ mesh, 100 cycles, ~minutes)
- Input Files: None required (internally generated)

**Key Options:**
- `-i <iterations>`: Number of cycles (default: 10)
- `-s <size>`: Mesh length per side (default: 30)
- `-r <regions>`: Number of distinct regions (default: 11)
- `-p`: Print progress per cycle
- `-q`: Quiet mode

**Expected Output:**
```
Run completed:
   Problem size        =  30
   MPI tasks           =  1
   Iteration count     =  10
   Final Origin Energy = 3.293936e+05
   Time = 0.234567 (Grind Time = 0.234567 us/zone/cycle)
   FOM  = 4265.32 (z/s)
```

**Verification:** Symmetry checking + FOM metrics (GrindTime, zones/second)

---

### 5. Parallel Research Kernels (PRK)
**Type:** Suite | **Tier:** A | **APIs:** 25+
**Repository:** https://github.com/ParRes/Kernels

**Kernels:** nstream, transpose, stencil, sparse, dgemm, p2p, synch_global, reduce, branch, random, pic, amr

**APIs:** Serial, OpenMP, MPI1, FG_MPI, MPIOPENMP, MPIRMA, MPISHM, SHMEM, UPC, AMPI, Charm++, GRAPPA, FENIX, Legion, Modern C++ (Cxx11), C1z, Fortran, Python, Julia, Rust, Go, Java, Chapel, Ada, Octave, Lua, Ruby, Scala, C#

**Dependencies:**
- Required: Make, C/C++ compiler
- Backend-specific: MPI, OpenMP, CUDA toolkit, etc.

**Build Commands:**
```bash
# Configure for CUDA
cp common/make.defs.cuda common/make.defs
# Edit common/make.defs: NVCC=/usr/local/cuda/bin/nvcc, GPU_ARCHITECTURE=sm_89

# Build all C++ implementations
make allcxx

# Build specific kernel
make -C CXX11/Stencil
```

**Run Commands:**
```bash
# Stencil (10 iterations, 1000×1000 grid)
./CXX11/Stencil/stencil 10 1000

# Transpose (10 iterations, 1024×32 matrix)
./CXX11/Transpose/transpose 10 1024 32

# Nstream (10 iterations, 16M elements)
./CXX11/Nstream/nstream 10 16777216

# Run validation suite
./scripts/small/runall
```

**Input Configurations:**
- Correctness Test: `./scripts/small/runall` (~seconds, validates checksums)
- Performance Benchmark: Individual kernels with larger sizes (~minutes)
- Input Files: None required (internally generated)

**Key Options:**
- Parameter 1: Number of iterations
- Parameter 2: Problem size (matrix dimension or array length)
- Parameter 3: Optional (element size, stencil radius)

**Expected Output:**
```
Parallel Research Kernels version
Stencil time= 0.123456 checksum= 1.234567e+10 ref_checksum= 1.234567e+10
```

**Verification:** Checksum-based (epsilon = 1e-8 relative error)

---

### 6. TeaLeaf
**Type:** Miniapp | **Tier:** A | **APIs:** 8
**Repository:** https://github.com/UoB-HPC/TeaLeaf

**Kernels:** CG, Jacobi, Chebyshev, PPCG solvers + kernel_initialise, set_chunk_data, local_halos, pack_halos, store_energy, field_summary, copy_u, calculate_residual, calculate_2norm, finalise

**APIs:** CUDA, HIP, OpenMP, Kokkos, SYCL (accessor/USM), C++ Parallel STL, Serial

**Dependencies:**
- Required: CMake >= 3.13.0, C++17 compiler
- CUDA Backend: CUDA Toolkit with sm_89 support
- Optional: MPI for distributed runs

**Build Commands:**
```bash
# CUDA build
cmake -Bbuild -H. -DMODEL=cuda -DENABLE_MPI=ON
cmake --build build

# OpenMP build
cmake -Bbuild -H. -DMODEL=omp
cmake --build build
```

**Run Commands:**
```bash
# With default tea.in file
./build/cuda-tealeaf

# With custom configuration
./build/cuda-tealeaf < tea_custom.in
```

**Input Configurations:**
- Correctness Test: Small `tea.in` with 128×128 grid, 20 steps (~seconds)
- Performance Benchmark: 512×512 grid, test_problem=5 (~minutes)
- Input Files: `tea.in` configuration file

**Example tea.in:**
```
*tea
state 1 density=100.0 energy=0.0001
state 2 density=0.1 energy=25.0 geometry=rectangle xmin=0.0 xmax=1.0 ymin=1.0 ymax=2.0
x_cells=512
y_cells=512
initial_timestep=0.004
end_step=20
use_cg
eps=1.0e-15
test_problem=5
*endtea
```

**Key Options (in tea.in):**
- `x_cells`, `y_cells`: Grid dimensions
- `use_cg/use_jacobi/use_chebyshev`: Solver selection
- `tl_max_iters`: Max solver iterations
- `tl_eps`: Convergence tolerance

**Expected Output:**
```
Step 20 time 0.0800 control timestep 0.004 dt 0.004
Temperature 0.1234567E+02 min/max 0.1000000E-03 0.2500000E+02
```

**Verification:** Test problems with reference solutions (6 test problems, 1e-15 convergence)

---

### 7. miniMD
**Type:** Miniapp | **Tier:** A | **APIs:** 4
**Repository:** https://github.com/Mantevo/miniMD

**Kernels:** Force (LJ/EAM), Neighbor List, Velocity Verlet Integration, Thermodynamic Properties, Communication/Exchange

**APIs:** Reference (MPI+OpenMP), Kokkos (multi-backend), MPI-Spec, Target (Intel)

**Dependencies:**
- Required: Make, C++ compiler
- Optional: MPI, OpenMP, CUDA toolkit

**Build Commands:**
```bash
# Standard build
make

# OpenMPI build
make openmpi -j 16

# CUDA build
make CUDA=yes -j 16
```

**Run Commands:**
```bash
# Serial execution
./miniMD

# MPI execution
mpirun -np 16 ./miniMD

# With custom parameters
./miniMD --half_neigh 0 -s 60
```

**Input Configurations:**
- Correctness Test: Default parameters (~seconds)
- Performance Benchmark: `-s 60` (larger system, ~minutes)
- Input Files: None required (internally generated)

**Key Options:**
- `-s <size>`: System size parameter
- `--half_neigh`: Neighbor list type (0=full, 1=half)

**Expected Output:**
Simulation statistics with energy, temperature, and timing information

**Verification:** Reference output comparison (18 reference files, tolerance-adjusted)

---

### 8. Neutral
**Type:** Mini-app | **Tier:** A | **APIs:** 5
**Repository:** https://github.com/UoB-HPC/Neutral

**Kernels:** solve_transport_2d, handle_particles, facet_event, collision_event, census_event, update_tallies, inject_particles

**APIs:** OpenMP 3.0, OpenMP 4.0, OpenACC, CUDA, RAJA

**Dependencies:**
- Required: Make, C/Fortran compiler
- Backend-specific: MPI, OpenMP, CUDA toolkit, OpenACC compiler

**Build Commands:**
```bash
# OpenMP 3 build
make KERNELS=omp3 COMPILER=GNU

# CUDA build
make KERNELS=cuda COMPILER=GNU

# OpenACC build
make KERNELS=oacc COMPILER=PGI
```

**Run Commands:**
```bash
# Scatter problem
./neutral.omp3 problems/scatter

# Stream problem
./neutral.cuda problems/stream

# CSP problem
./neutral.omp3 problems/csp
```

**Input Configurations:**
- Correctness Test: `problems/scatter` (~seconds)
- Performance Benchmark: `problems/stream` or `problems/csp` (~minutes)
- Input Files: `problems/` directory (scatter, stream, csp, split)

**Key Options:**
- `OPTIONS=-DVISIT_DUMP`: Enable visualization dumps
- `OPTIONS=-DENABLE_PROFILING`: Enable profiling
- `MPI=no`: Disable MPI

**Expected Output:**
Neutron transport simulation results with energy deposition metrics

**Verification:** Numerical tolerance comparison (1e-3 relative error on energy deposition)

---

### 9. miniWeather
**Type:** Miniapp | **Tier:** A | **APIs:** 5
**Repository:** https://github.com/mrnorman/miniWeather

**Kernels:** Compute Tendencies (X/Z-direction), Apply Tendencies, Set Halo Values, Reductions, Semi-Discrete Step

**APIs:** MPI (C/Fortran/C++), OpenMP, OpenMP 4.5+ Offload, OpenACC, YAKL (C++ portability for CUDA/HIP)

**Dependencies:**
- Required: CMake 3.0+, C/C++/Fortran compiler
- Optional: MPI, OpenMP, OpenACC compiler, CUDA toolkit

**Build Commands:**
```bash
cd c/build
source cmake_summit_gnu.sh  # or appropriate config
cmake ../
make -j
make test
```

**Run Commands:**
```bash
# Serial execution
./serial

# MPI execution
mpirun -n 4 ./mpi

# OpenMP execution
./openmp

# OpenACC/GPU
./openacc
```

**Input Configurations:**
- Correctness Test: Default parameters with `make test` (~seconds)
- Performance Benchmark: `-DNX=400 -DNZ=200 -DSIM_TIME=1000` (~minutes)
- Input Files: None required (compile-time configuration)

**CMake Options:**
- `-DNX=<cells>`: X-direction cells
- `-DNZ=<cells>`: Z-direction cells
- `-DSIM_TIME=<seconds>`: Simulation duration
- `-DDATA_SPEC=DATA_SPEC_THERMAL`: Initial condition type

**Expected Output:**
Weather simulation with timing and conservation metrics

**Verification:** Conservation laws (mass <= 1e-13, energy dissipation bounds)

---

### 10. HeCBench
**Type:** Suite | **Tier:** A | **APIs:** 4
**Repository:** https://github.com/zjin-lcf/HeCBench

**Kernels:** 513 unique kernel base names across 18 domains (ML, Simulation, Math, Image Processing, etc.)

**APIs:** CUDA (508 impl), HIP (505 impl), SYCL (489 impl), OpenMP (325 impl)

**Dependencies:**
- Required: CMake 3.21+, C++17 compiler
- CUDA Backend: CUDA Toolkit with sm_89 support
- Optional: HIP, SYCL runtime, OpenMP 4.5+

**Build Commands:**
```bash
# CMake preset for RTX 4070
cmake --preset cuda-sm89
cmake --build build/cuda-sm89 --parallel

# Single benchmark with Makefile
cd src/blas-gemm-cuda
make ARCH=sm_89 run
```

**Run Commands:**
```bash
# Single benchmark
cd src/backprop-cuda
make ARCH=sm_89 clean run

# Automated batch run
./autohecbench.py cuda -o cuda_results.csv

# Specific benchmark with parameters
cd src/blas-gemm-cuda
./main 4096 4096 4096 100
```

**Input Configurations:**
- Correctness Test: Single benchmark with `make ARCH=sm_89 run` (~seconds)
- Performance Benchmark: `./autohecbench.py cuda -o results.csv` (all benchmarks, ~hours)
- Input Files: Benchmark-specific in `data/` directories

**Key Options:**
- `ARCH=sm_89`: GPU compute capability
- `OPTIMIZE=yes`: Enable -O3 optimization
- Parameters vary by benchmark (size, iterations, etc.)

**Expected Output:**
```
Running with single precision data type:
    PASS
    Time: 1.567 seconds
    Kernel GFLOPS: 45678.90
```

**Verification:** Reference implementation comparison (CPU vs GPU with tolerance)

---

### 11. Rodinia
**Type:** Suite | **Tier:** A | **APIs:** 3
**Repository:** https://github.com/yuhc/gpu-rodinia

**Kernels:** backprop, bfs, b+tree, cfd, dwt2d, gaussian, heartwall, hotspot, hotspot3D, hybridsort, kmeans, lavaMD, leukocyte, lud, mummergpu, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster (24 total)

**APIs:** CUDA (24), OpenCL (21), OpenMP (19)

**Dependencies:**
- Required: Make, C/C++ compiler
- CUDA Backend: CUDA Toolkit
- OpenCL Backend: OpenCL SDK
- Data files: Separate download required

**Build Commands:**
```bash
# Configure paths in common/make.config
# Set CUDA_DIR, OPENCL_DIR

# Build all CUDA benchmarks
make -C cuda

# Build specific benchmark
cd cuda/backprop
make clean && make
```

**Run Commands:**
```bash
# Backprop (neural network)
cd cuda/backprop
./backprop 65536

# BFS (graph traversal)
cd cuda/bfs
./bfs ../data/bfs_graph1MW_6.txt

# Hotspot (thermal simulation)
cd cuda/hotspot
./hotspot 512 512 2 2 100 ../data/temp_1024

# KMeans (clustering)
cd cuda/kmeans
./kmeans -i ../data/kdd_cup -n 94326 -f 34 -c 5
```

**Input Configurations:**
- Correctness Test: Small problem sizes (~seconds each)
- Performance Benchmark: Full problem sizes from data files (~minutes)
- Input Files: `data/` directory (requires separate download)

**Expected Output:**
Benchmark-specific timing and results

**Verification:** Selective output validation, timing instrumentation

---

### 12. PENNANT
**Type:** Mini-app | **Tier:** A | **APIs:** 3
**Repository:** https://github.com/lanl/PENNANT

**Kernels:** advPosHalf, advPosFull, calcCrnrMass, sumCrnrForce, calcAccel, calcRho, calcWork, calcWorkRate, calcEnergy, sumEnergy, calcDtCourant, calcDtVolume, calcDtHydro, calcStateAtHalf, calcEOS, calcForce (PolyGas/QCS/TTS), calcCtrs, calcVols, calcSideFracs, calcSurfVecs, calcEdgeLen, calcCharLen, initRadialVel, doCycle (26 total)

**APIs:** MPI, OpenMP, Serial

**Dependencies:**
- Required: Make, C++ compiler
- Optional: MPI, OpenMP

**Build Commands:**
```bash
cd PENNANT
make
```

**Run Commands:**
```bash
# Small Sedov blast wave
./build/pennant test/sedov/sedov.pnt

# Sedov small variant
./build/pennant test/sedovsmall/sedov.pnt

# Leblanc problem
./build/pennant test/leblanc/leblanc.pnt

# MPI execution
mpirun -np 4 ./build/pennant test/sedov/sedov.pnt
```

**Input Configurations:**
- Correctness Test: `test/sedovsmall/sedov.pnt` (45×45 mesh, ~seconds)
- Performance Benchmark: `test/sedov/sedov.pnt` (full Sedov, ~minutes)
- Input Files: `test/*/` directories (.pnt configuration files)

**Expected Output:**
```
End cycle 100, time = 1.80646e-01, dt = 1.50494e-03, wall = 6.74631e-01
```

**Verification:** Energy conservation check (total, internal, kinetic)

---

### 13. SW4lite
**Type:** Proxy App | **Tier:** A | **APIs:** 4
**Repository:** https://github.com/geodynamics/sw4lite

**Kernels:** rhs4sg, rhs4sg_rev, rhs4sgcurv, rhs4sgcurv_rev, addsgd4, addsgd6, bcfortsg, freesurfcurvisg, dpdmt, forcing, pred/corr, HaloToBufferKernel, BufferToHaloKernel

**APIs:** MPI, OpenMP, CUDA (50+ device kernels), Fortran

**Dependencies:**
- Required: Make, C/C++ and Fortran compilers
- CUDA Backend: CUDA Toolkit
- Optional: MPI

**Build Commands:**
```bash
# OpenMP build
make -j4

# CUDA build
make -f Makefile.cuda -j4

# Serial build
make openmp=no -j4
```

**Run Commands:**
```bash
# Point source benchmark
export OMP_NUM_THREADS=4
mpirun -np 4 ./optimize_mp_hostname/sw4lite pointsource.in

# CUDA execution
./optimize_cuda_hostname/sw4lite pointsource.in
```

**Input Configurations:**
- Correctness Test: `pointsource.in` with small grid (~seconds)
- Performance Benchmark: Larger grid configurations (~minutes)
- Input Files: `.in` configuration files

**Expected Output:**
```
Linf = 0.569416 (error tolerance check)
L2 = 0.0245361
```

**Verification:** Analytical solution comparison for point source problem

---

### 14. Kokkos Kernels
**Type:** Library/Suite | **Tier:** A | **APIs:** 7
**Repository:** https://github.com/kokkos/kokkos-kernels

**Kernels:**
- BLAS1: dot, nrm2, nrm1, iamax, scal, axpby, etc.
- BLAS2: gemv, ger, syr
- BLAS3: gemm, trmm, trsm
- Sparse: spmv, spgemm, sptrsv, spadd
- Graph: coloring, coarsen, triangle_counting, rcb, rcm, mis2
- Batched: gemm, gesv, qr, lu, svd
- ODE: RungeKutta, BDF, Newton

**APIs:** Serial, OpenMP, Threads, CUDA, HIP, OpenMP Target, SYCL

**Dependencies:**
- Required: CMake 3.16+, C++17 compiler, Kokkos library
- CUDA Backend: CUDA Toolkit, Kokkos with CUDA backend

**Build Commands:**
```bash
cmake -Bbuild -H. \
  -DKokkosKernels_REQUIRE_DEVICES=CUDA \
  -DCMAKE_BUILD_TYPE=Release

cmake --build build -j$(nproc)
```

**Run Commands:**
```bash
# SPMV performance test
./build/perf_test/sparse/KokkosSparse_spmv.exe -s 110503 --test kk-kernels -l 100

# SPGEMM test
./build/perf_test/sparse/KokkosSparse_spgemm.exe --amtx matrix.mtx --algorithm KKDEFAULT --repeat 10

# Graph coloring
./build/perf_test/graph/KokkosGraph_color.exe -s 100000
```

**Input Configurations:**
- Correctness Test: GoogleTest unit tests
- Performance Benchmark: perf_test executables with scalable sizes
- Input Files: Matrix Market format (.mtx) or generated matrices

**Key Options:**
- `-s [N]`: Matrix size NxN
- `--test`: Algorithm choice (kk, kk-kernels, mkl, cusparse)
- `-l [LOOP]`: Iteration count

**Expected Output:**
```
NNZ NumRows NumCols ProblemSize(MB) AveBandwidth(GB/s) AveGFlop
```

**Verification:** GoogleTest unit tests + performance tests

---

### 15. RAJA Performance Suite (RAJAPerf)
**Type:** Suite | **Tier:** A | **APIs:** 7+
**Repository:** https://github.com/LLNL/RAJAPerf

**Kernels:**
- Basic: DAXPY, INIT3, MAT_MAT_SHARED, PI_REDUCE, etc. (20)
- Lcals: DIFF_PREDICT, EOS, HYDRO_1D, etc. (11)
- Polybench: 2MM, 3MM, GEMM, etc. (13)
- Stream: ADD, COPY, DOT, MUL, TRIAD (5)
- Apps: CONVECTION3DPA, LTIMES, MASS3DPA, etc. (20)
- Algorithm: ATOMIC, HISTOGRAM, REDUCE_SUM, SORT, etc. (8)

**APIs:** RAJA Sequential, OpenMP, OpenMP Target, CUDA, HIP, SYCL, Kokkos, MPI

**Dependencies:**
- Required: CMake 3.23+, C++17 compiler
- Submodules: RAJA, BLT (use `--recursive` clone)
- CUDA Backend: CUDA Toolkit with sm_89 support

**Build Commands:**
```bash
git clone --recursive https://github.com/LLNL/RAJAPerf.git
cd RAJAPerf && mkdir build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_CUDA=ON \
  -DRAJA_PERFSUITE_TUNING_CUDA_ARCH=89 \
  -DENABLE_OPENMP=ON

make -j
```

**Run Commands:**
```bash
# Full suite
./rajaperf-driver

# CUDA variants only
./rajaperf-driver -b cuda-block -b cuda-global

# Specific kernel group
./rajaperf-driver -k basic -k lcals

# With custom size
./rajaperf-driver -s 10000000 -n 5 -o results/
```

**Input Configurations:**
- Correctness Test: `-s 100000 -n 1 -k basic` (~seconds)
- Performance Benchmark: `-s 10000000 -n 5` (~minutes)
- Input Files: None required

**Key Options:**
- `-k <kernel-group>`: Select kernel groups (basic, lcals, algorithm, app, polybench, stream)
- `-b <backend>`: Choose variants (cuda-block, cuda-global, openmp, sequential)
- `-s <size>`: Problem size
- `-n <count>`: Kernel iterations
- `-o <dir>`: Output directory

**Expected Output:**
CSV files: timing.csv, speedup.csv, fom.csv, checksum.csv, kernels.csv

**Verification:** Checksum-based with GoogleTest harness

---

### 16. RAJAProxies
**Type:** Suite | **Tier:** A | **APIs:** 5
**Repository:** https://github.com/LLNL/RAJAProxies

**Kernels:**
- LULESH v1.0/v2.0: CalcKinematicsForElems, CalcQForElems, etc.
- CoMD: ljForce, haloExchange, timestep, linkCells
- Kripke: (referenced as submodule)

**APIs:** Sequential, OpenMP, CUDA, HIP, SIMD

**Dependencies:**
- Required: CMake, C++11 compiler, BLT
- Submodules: RAJA, BLT (included)
- CUDA Backend: CUDA Toolkit

**Build Commands:**
```bash
git clone --recursive https://github.com/LLNL/RAJAProxies.git
mkdir build && cd build
cmake -DENABLE_OPENMP=On -DENABLE_CUDA=On -DCUDA_ARCH=70 ../
make
```

**Run Commands:**
```bash
# LULESH v1.0 OpenMP
./lulesh-v1.0-RAJA-omp.exe

# LULESH v1.0 CUDA
./lulesh-v1.0-RAJA-cuda.exe

# LULESH v2.0 Sequential
./lulesh-v2.0-RAJA-seq.exe
```

**Input Configurations:**
- Correctness Test: Default parameters (~seconds)
- Performance Benchmark: Larger mesh sizes (~minutes)
- Input Files: None required

**Expected Output:**
LULESH-style FOM metrics and timing

**Verification:** Sedov problem + FOM metrics

---

### 17. ExaMiniMD
**Type:** Miniapp | **Tier:** A | **APIs:** 6
**Repository:** https://github.com/ECP-copa/ExaMiniMD

**Kernels:** Force LJ Cell/Neighbor List (Full/Half), Force SNAP, Neighbor List 2D/CSR, Binning, NVE Integrator (Initial/Final), Kinetic/Potential Energy Reduce, Temperature Compute

**APIs:** Serial, OpenMP, CUDA, HIP, SYCL, MPI

**Dependencies:**
- Required: CMake, Kokkos library
- CUDA Backend: Kokkos with CUDA backend

**Build Commands:**
```bash
cd ExaMiniMD/src
export KOKKOS_PATH=${HOME}/kokkos
make -j KOKKOS_ARCH=Ampere89 KOKKOS_DEVICES=Cuda CXX=mpicxx MPI=1
```

**Run Commands:**
```bash
# Serial CUDA
./ExaMiniMD -il ../input/in.lj --kokkos-threads=1 --kokkos-ndevices=1

# MPI + GPU
mpirun -np 2 ./ExaMiniMD -il ../input/in.lj --comm-type MPI --kokkos-ndevices=2
```

**Input Configurations:**
- Correctness Test: `../input/in.lj` with small system (~seconds)
- Performance Benchmark: Larger systems, more timesteps (~minutes)
- Input Files: `input/` directory (LAMMPS-style input files)

**Key Options:**
- `-il <filename>`: Input LAMMPS file
- `--comm-type`: Communication model (SERIAL, MPI)
- `--kokkos-threads=<N>`: OpenMP threads
- `--kokkos-ndevices=<N>`: Number of GPUs

**Expected Output:**
Timestep information, energy per atom, temperature, performance statistics

**Verification:** Binary snapshot comparison with reference run

---

### 18. CoMD
**Type:** Proxy App | **Tier:** A | **APIs:** 3
**Repository:** https://github.com/exmatex/CoMD

**Kernels:** LJ Force, EAM Force, Link Cell Management, Halo Exchange, Leapfrog Integration, Kinetic Energy Reduction, Domain Decomposition

**APIs:** OpenMP, MPI, Serial

**Dependencies:**
- Required: Make, C compiler
- Optional: MPI, OpenMP

**Build Commands:**
```bash
cd src-openmp
cp Makefile.vanilla Makefile
make
```

**Run Commands:**
```bash
# EAM potential, 20x20x20 atoms
../bin/CoMD-openmp-mpi -e -i 1 -j 1 -k 1 -x 20 -y 20 -z 20

# Larger system
../bin/CoMD-openmp-mpi -e -i 1 -j 1 -k 1 -x 40 -y 40 -z 40

# MPI scaling
mpirun -np 8 ../bin/CoMD-openmp-mpi -e -i 2 -j 2 -k 2 -x 40 -y 40 -z 40
```

**Input Configurations:**
- Correctness Test: `-x 20 -y 20 -z 20` (~seconds)
- Performance Benchmark: `-x 40 -y 40 -z 40` (~minutes)
- Input Files: None required

**Key Options:**
- `-e`: Use EAM potential
- `-i, -j, -k`: MPI domain decomposition
- `-x, -y, -z`: Local problem size per rank
- `-n`: Number of timesteps (default: 100)

**Expected Output:**
```
Performance:
  Total atom-steps/s: 1.23e+09
  Atom rate (atoms/us): 12345.67
```

**Verification:** Energy conservation check (eFinal/eInitial ratio)

---

### 19. Kripke
**Type:** Miniapp | **Tier:** A | **APIs:** 8
**Repository:** https://github.com/LLNL/Kripke

**Kernels:** LTimes, LPlusTimes, Scattering, SweepSubdomain, Source, Population

**APIs:** RAJA, CHAI, Umpire, MPI, OpenMP, CUDA, HIP, Caliper

**Dependencies:**
- Required: CMake 3.20+, C++14 compiler
- Submodules: RAJA, CHAI, Umpire, BLT
- CUDA Backend: CUDA Toolkit

**Build Commands:**
```bash
git submodule update --init --recursive
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_CUDA=On \
  -DENABLE_MPI=On \
  -DCMAKE_CUDA_ARCHITECTURES=89
cmake --build . -j8
```

**Run Commands:**
```bash
# Default problem
./bin/kripke.exe

# CUDA with custom size
./bin/kripke.exe --arch CUDA --zones 32,32,32 --groups 16 --quad 96

# Larger problem
./bin/kripke.exe --arch CUDA --zones 64,64,64 --groups 32 --legendre 4 --quad 48
```

**Input Configurations:**
- Correctness Test: Default parameters (~seconds)
- Performance Benchmark: `--zones 64,64,64` (~minutes)
- Input Files: None required

**Key Options:**
- `--zones <x,y,z>`: Domain dimensions (default: 16,16,16)
- `--groups <n>`: Energy groups (default: 32)
- `--legendre <l>`: Legendre order (default: 4)
- `--quad <n>`: Quadrature directions (default: 96)
- `--arch`: Sequential, OpenMP, or CUDA

**Expected Output:**
Timing summary for kernels, convergence data

**Verification:** Convergence testing via population integral

---

### 20. PARSEC
**Type:** Suite | **Tier:** A | **APIs:** 4
**Repository:** https://github.com/bamos/parsec-benchmark

**Kernels/Apps:** canneal, dedup, streamcluster, blackscholes, bodytrack, facesim, ferret, fluidanimate, freqmine, raytrace, swaptions, vips, x264

**APIs:** Pthreads (12/13 apps), OpenMP (3 apps), TBB (6 apps), Serial

**Dependencies:**
- Required: parsecmgmt tool, GCC
- Build time: 30-60 minutes

**Build Commands:**
```bash
# Build all
parsecmgmt -a build

# Build specific package
parsecmgmt -a build -p x264 blackscholes -c gcc-pthreads
```

**Run Commands:**
```bash
# Minimal test
parsecmgmt -a run

# Performance measurement (32 threads)
parsecmgmt -a run -p vips kernels -c gcc-hooks -n 32

# Specific input size
parsecmgmt -a run -p x264 -i native -c gcc
```

**Input Configurations:**
- Correctness Test: `parsecmgmt -a run` (~seconds)
- Performance Benchmark: `-i native -n 32` (~minutes per app)
- Input Files: Included with benchmark

**Key Options:**
- `-a`: Action (build, run, info, status)
- `-p`: Package selection
- `-c`: Build configuration (gcc, gcc-hooks, gcc-pthreads, gcc-openmp, gcc-tbb)
- `-i`: Input size (test, simsmall, simmedium, simlarge, native)
- `-n`: Thread count

**Expected Output:**
Benchmark timing with thread scaling results

**Verification:** Output-based comparison with reference outputs

---

### 21. OpenDwarfs
**Type:** Suite | **Tier:** B | **APIs:** 1 (OpenCL)
**Repository:** https://github.com/vtsynergy/OpenDwarfs

**Kernels:** lud, kmeans, csr, fft, srad, cfd, bfs, gem, nw, swat, crc, bwa_hmm, nqueens, tdm (13 dwarfs)

**APIs:** OpenCL 1.0+ (CPU/GPU/MIC/FPGA targets)

**Dependencies:**
- Required: Autotools, OpenCL SDK
- Build requirements: autoconf >= 2.63, automake, libtool

**Build Commands:**
```bash
./autogen.sh
mkdir build && cd build
../configure
make

# Specific applications
../configure --with-apps=srad,gem,cfd
make
```

**Run Commands:**
```bash
# General format
./<executable> [-p <platform> -d <device> | -t <type>] [options]

# Examples
./astar -p 0 -d 0 --
./gem
./nw -p 0 -d 0 -o --
```

**Input Configurations:**
- Correctness Test: Default parameters per dwarf (~seconds)
- Performance Benchmark: Larger problem sizes (~minutes)
- Input Files: Application-specific

**Key Options:**
- `-p <platform>`: Platform ID
- `-d <device>`: Device ID
- `-t <type>`: Device type (0=CPU, 1=GPU, 2=MIC, 3=FPGA)
- `-o`: Use optimized kernels

**Expected Output:**
Dwarf-specific results with timing

**Verification:** CPU reference implementations with tolerance comparison

---

### 22. STAMP
**Type:** Suite | **Tier:** A | **APIs:** 4 (TM variants)
**Repository:** https://github.com/kozyraki/stamp

**Kernels/Apps:** bayes, genome, intruder, kmeans, labyrinth, ssca2, vacation, yada

**APIs:** Original TM API, Hardware TM (HTM), Software TM (STM), Hybrid HTM-STM, OpenMP (OTM)

**Dependencies:**
- Required: Make, C compiler
- TM support: HTM hardware or STM library

**Build Commands:**
```bash
cd [benchmark_directory]
make                    # Default
make sequential         # Sequential flavor
make stm               # STM flavor
```

**Run Commands:**
```bash
# Example: Vacation benchmark
./vacation -n 262144 -q 100 -u 70 -r 0 -t 10485760
```

**Input Configurations:**
- Correctness Test: Small parameters (~seconds)
- Performance Benchmark: Native parameters per app (~minutes)
- Input Files: None required

**Expected Output:**
Transaction statistics and performance metrics

**Verification:** Assertion-based + convergence metrics

---

### 23. NAS Parallel Benchmarks (NPB)
**Type:** Suite | **Tier:** A | **APIs:** 2
**Repository:** https://www.nas.nasa.gov/software/npb.html

**Kernels:** BT, SP, LU, CG, MG, FT, IS, EP, DT, UA, DC (11 benchmarks)

**APIs:** MPI (NPB3.4-MPI), OpenMP (NPB3.4-OMP)

**Dependencies:**
- Required: Make, Fortran and C compilers
- Optional: MPI implementation

**Build Commands:**
```bash
# Configure make.def with compiler paths
cp config/make.def.template config/make.def

# Build single benchmark
make BT CLASS=D

# Build suite
make suite
```

**Run Commands:**
```bash
# Serial execution
./bin/bt.D.x

# MPI execution
mpirun -np 4 ./bin/bt.D.x
```

**Input Configurations:**
- Correctness Test: CLASS=S or CLASS=W (~seconds)
- Performance Benchmark: CLASS=C or CLASS=D (~minutes)
- Input Files: None required

**Problem Classes:**
- S: Small (quick testing)
- W: Workstation
- A, B, C, D, E: Increasing sizes

**Expected Output:**
Execution time, MFLOPS, verification status

**Verification:** Reference value comparison (epsilon = 1e-8), NaN detection

---

### 24. OSU Micro-Benchmarks (OMB)
**Type:** Microbenchmark Suite | **Tier:** A | **APIs:** 6
**Repository:** https://mvapich.cse.ohio-state.edu/benchmarks/

**Kernels:**
- pt2pt: latency, bibw, bw, multi_lat, etc.
- collective: allgather, allreduce, barrier, bcast, etc.
- one-sided: put/get latency/bw, atomics
- startup: hello, init

**APIs:** MPI, OpenSHMEM, UPC, UPC++, XCCL (NCCL/RCCL), GPU (CUDA/HIP/SYCL/OpenACC)

**Dependencies:**
- Required: Autotools, MPI implementation
- CUDA Backend: CUDA-aware MPI, CUDA Toolkit

**Build Commands:**
```bash
./configure CC=/path/to/mpicc CXX=/path/to/mpicxx \
  --enable-cuda \
  --with-cuda-include=/usr/local/cuda/include \
  --with-cuda-libpath=/usr/local/cuda/lib64
make && make install
```

**Run Commands:**
```bash
# Latency test (host to device)
mpirun -np 2 ./osu_latency H D

# Bandwidth test (device to device)
mpirun -np 2 ./osu_bw D D

# AllReduce collective
mpirun -np 4 ./osu_allreduce -d
```

**Input Configurations:**
- Correctness Test: pt2pt latency (~seconds)
- Performance Benchmark: Full collective suite (~minutes)
- Input Files: None required

**Key Options:**
- `H`: Host buffer
- `D`: Device buffer
- `-d`: Use device memory for collectives

**Expected Output:**
```
# Size    Latency (us)
1         1.23
2         1.25
4         1.28
```

**Verification:** Data correctness validation with buffer comparison

---

### 25. miniAMR
**Type:** Miniapp | **Tier:** A | **APIs:** 2
**Repository:** https://github.com/Mantevo/miniAMR

**Kernels:** Stencil (7-pt, 27-pt, variable), Block Refinement, Block Coarsening, Mesh Rebalancing (RCB/SFC), Ghost Exchange, Checksum

**APIs:** MPI, OpenMP

**Dependencies:**
- Required: Make, C compiler
- Optional: MPI, OpenMP

**Build Commands:**
```bash
cd openmp  # or ref/
make
```

**Run Commands:**
```bash
# Expanding sphere
mpirun -np 64 ./miniAMR.x \
  --num_refine 4 \
  --max_blocks 6000 \
  --init_x 1 --init_y 1 --init_z 1 \
  --npx 4 --npy 4 --npz 4 \
  --nx 8 --ny 8 --nz 8 \
  --num_objects 1 \
  --object 2 0 -0.01 -0.01 -0.01 0.0 0.0 0.0 0.0 0.0 0.0 0.0009 0.0009 0.0009 \
  --num_tsteps 200 \
  --comm_vars 2
```

**Input Configurations:**
- Correctness Test: Small grid, few timesteps (~seconds)
- Performance Benchmark: Full refinement study (~minutes)
- Input Files: Command-line parameters

**Key Options:**
- `--nx, --ny, --nz`: Block size (must be even, default 10)
- `--num_refine`: Refinement iterations
- `--max_blocks`: Maximum allowed blocks
- `--num_tsteps`: Number of timesteps

**Expected Output:**
Block counts, distribution, performance metrics, checksum

**Verification:** Checksum-based (10^-8 tolerance)

---

### 26. miniFE
**Type:** Miniapp | **Tier:** A | **APIs:** 10
**Repository:** https://github.com/Mantevo/miniFE

**Kernels:** WAXPY, DOT, MATVEC (SpMV), Matrix Assembly, Matrix Structure, Exchange

**APIs:** MPI, OpenMP (standard/optimized/4.5), CUDA, Kokkos, TBB, TPI, Cilk, Qthreads, MKL

**Dependencies:**
- Required: Make, C++ compiler
- Optional: MPI, OpenMP, CUDA toolkit

**Build Commands:**
```bash
cd ref/basic
make -f makefile
```

**Run Commands:**
```bash
# Basic execution
./miniFE.x -nx 100 -ny 100 -nz 100

# Smaller test
./miniFE.x -nx 50 -ny 50 -nz 50

# MPI execution
mpirun -np 4 ./miniFE.x -nx 100 -ny 100 -nz 100
```

**Input Configurations:**
- Correctness Test: `-nx 50 -ny 50 -nz 50` (~seconds)
- Performance Benchmark: `-nx 130 -ny 130 -nz 130` (~minutes)
- Input Files: Command-line parameters

**Key Options:**
- `-nx, -ny, -nz`: Problem dimensions (default: 30)

**Expected Output:**
YAML summary with CG solver MFLOP/s, assembly time, total time

**Verification:** Analytical solution comparison + gold file regression

---

### 27. miniGhost
**Type:** Miniapp | **Tier:** A | **APIs:** 3
**Repository:** https://github.com/Mantevo/miniGhost

**Kernels:** Stencil_2D5PT, Stencil_2D9PT, Stencil_3D7PT, Stencil_3D27PT, Flux_Accumulate, Boundary_Conditions, Pack/Unpack

**APIs:** MPI, OpenMP, Serial (+ MPI-IO, H5Part for checkpoint)

**Dependencies:**
- Required: Make, C/Fortran compiler
- Optional: MPI, OpenMP

**Build Commands:**
```bash
make -f makefile.mpi
# or
make openmp=no  # Serial
```

**Run Commands:**
```bash
# Basic run
./mg

# MPI parallel
mpirun -np 16 ./mg

# With custom grid
OMP_NUM_THREADS=4 mpirun -np 16 ./mg --gx 64 --gy 64 --gz 64
```

**Input Configurations:**
- Correctness Test: Small grid (~seconds)
- Performance Benchmark: Larger grid (~minutes)
- Input Files: Command-line parameters

**Key Options:**
- `--gx, --gy, --gz`: Global grid dimensions
- `--num_variables`: Number of field variables
- `--num_tsteps`: Number of time steps
- `--stencil`: 5, 7, 9, or 27-point

**Expected Output:**
Performance metrics (GFlops, bandwidth), timing breakdown

**Verification:** Global summation + heat flux conservation

---

### 28. HPCCG
**Type:** Miniapp | **Tier:** B | **APIs:** 3
**Repository:** https://github.com/Mantevo/HPCCG

**Kernels:** SpMV, DDOT, WAXPBY, Residual, CG Solver, Matrix Generation, Exchange

**APIs:** MPI (optional), OpenMP (optional), Serial

**Dependencies:**
- Required: Make, C++ compiler
- Optional: MPI, OpenMP

**Build Commands:**
```bash
make
# or without MPI
make USE_MPI=
```

**Run Commands:**
```bash
# Serial
./test_HPCCG 100 100 100

# Parallel
mpirun -np 16 ./test_HPCCG 50 50 50

# With OpenMP
OMP_NUM_THREADS=4 mpirun -np 16 ./test_HPCCG 50 50 50
```

**Input Configurations:**
- Correctness Test: `50 50 50` (~seconds)
- Performance Benchmark: `100 100 100` (~minutes)
- Input Files: Command-line parameters (nx ny nz)

**Expected Output:**
Total flops, solution time, GFlops achieved

**Verification:** Convergence tolerance-based

---

### 29. HPCG
**Type:** Benchmark | **Tier:** A | **APIs:** 3
**Repository:** https://github.com/hpcg-benchmark/hpcg

**Kernels:** SpMV, SYMGS (Symmetric Gauss-Seidel), Multigrid V-cycle, Dot Product, WAXPBY, Residual, Prolongation/Restriction

**APIs:** MPI, OpenMP, C++ STL

**Dependencies:**
- Required: CMake or Make, C++ compiler
- Optional: MPI, CUDA toolkit

**Build Commands:**
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DHPCG_ENABLE_MPI=ON ..
make
```

**Run Commands:**
```bash
# Basic run (official requires 1800+ seconds)
mpirun -np 1 ./xhpcg --nx 192 --ny 192 --nz 192 --rt 1800

# Multi-GPU
mpirun -np 4 ./xhpcg --nx 256 --ny 256 --nz 256 --rt 1800
```

**Input Configurations:**
- Correctness Test: Short runtime (~seconds)
- Performance Benchmark: `--rt 1800` (official requirement, ~30 minutes)
- Input Files: Command-line parameters or hpcg.dat

**Key Options:**
- `--nx, --ny, --nz`: Local problem dimensions
- `--rt`: Runtime in seconds (min 1800 for official)

**Expected Output:**
Residual values, GFlops achieved, timing statistics

**Verification:** Comprehensive V&V suite (TestCG, TestSymmetry, TestNorms)

---

### 30. HPL (High-Performance Linpack)
**Type:** Benchmark | **Tier:** A | **APIs:** 2
**Repository:** https://netlib.org/benchmark/hpl/

**Kernels:** DGEMM, DTRSM, DTRSV, DLASWP, DSWAP, DGETRF, DLACPY, DLATCPY, DGEMV, DGER, DAXPY, DCOPY, IDAMAX, DSCAL

**APIs:** MPI, BLAS (Level 1-3)

**Dependencies:**
- Required: Make, MPI, optimized BLAS library
- Recommended: NVIDIA cuBLAS for GPU

**Build Commands:**
```bash
# Configure for architecture
cp setup/Make.Linux_Intel64 .
# Edit Make.Linux_Intel64 with paths
make arch=Linux_Intel64
```

**Run Commands:**
```bash
# Single GPU
./hpl.sh --dat ./HPL-1GPU.dat

# Multi-GPU
mpirun -np 4 ./xhpl < HPL.dat
```

**Input Configurations:**
- Correctness Test: Small matrix (~seconds)
- Performance Benchmark: Large matrix filling most memory (~minutes to hours)
- Input Files: HPL.dat configuration file

**Expected Output:**
GFLOPS achieved, residual error, timing

**Verification:** Residual error checking (||AX - B||/||A||*||X||)

---

### 31. STREAM
**Type:** Microbenchmark | **Tier:** A | **APIs:** 1
**Repository:** https://www.cs.virginia.edu/stream/

**Kernels:** Copy, Scale, Add, Triad

**APIs:** OpenMP, Standard C

**Dependencies:**
- Required: C compiler
- Optional: OpenMP

**Build Commands:**
```bash
gcc -O3 -fopenmp -march=native stream.c -o stream_omp

# Large array
gcc -O3 -fopenmp -DSTREAM_ARRAY_SIZE=400000000 -march=native stream.c -o stream_large
```

**Run Commands:**
```bash
# Single-threaded
./stream_omp

# Multi-threaded
OMP_NUM_THREADS=16 ./stream_omp

# Large problem
OMP_NUM_THREADS=16 OMP_SCHEDULE=static ./stream_large
```

**Input Configurations:**
- Correctness Test: Default array size (~seconds)
- Performance Benchmark: Large array (400M+ elements, ~seconds)
- Input Files: None required (compile-time config)

**Key Parameters (in source):**
- `STREAM_ARRAY_SIZE`: Default 10,000,000

**Expected Output:**
```
Function    Best Rate MB/s  Avg time     Min time     Max time
Copy:           500000.0     0.001234     0.001200     0.001300
Triad:          480000.0     0.001567     0.001500     0.001700
```

**Verification:** checkSTREAMresults() with epsilon tolerance

---

### 32. LAMMPS
**Type:** Application | **Tier:** A | **APIs:** 5
**Repository:** https://github.com/lammps/lammps

**Kernels:** Pair force (40+ styles), Neighbor list, Bond/Angle/Dihedral, KSpace/PPPM, Integration, Domain decomposition

**APIs:** MPI, OpenMP, CUDA, Kokkos, SYCL

**Dependencies:**
- Required: CMake 3.20+, C++ compiler
- CUDA Backend: CUDA Toolkit
- Optional: Many packages (GPU, KOKKOS, etc.)

**Build Commands:**
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DPKG_GPU=yes \
  -DGPUPackage_GPU_COMPUTE_CAPABILITY=89 \
  ../cmake
make -j8 install
```

**Run Commands:**
```bash
# GPU execution
mpirun -np 1 lmp_gpu -sf gpu -in in.lj.gpu

# Multi-GPU
mpirun -np 4 lmp_gpu -sf gpu -pk gpu 1 -in ../examples/in.lj.gpu
```

**Input Configurations:**
- Correctness Test: Small LJ example (~seconds)
- Performance Benchmark: Larger systems (~minutes)
- Input Files: LAMMPS input scripts (examples/ directory)

**Key Options:**
- `-sf gpu`: GPU suffix
- `-pk gpu N`: GPU package with N GPUs
- `-in <file>`: Input script

**Expected Output:**
Timestep, temperature, energy, performance (timesteps/second)

**Verification:** GoogleTest unit tests + benchmark suite

---

### 33. AMReX
**Type:** Library/Framework | **Tier:** A | **APIs:** 5
**Repository:** https://github.com/AMReX-Codes/amrex

**Kernels:** ParallelFor/ParallelReduce, MLMG (multi-level multi-grid), Embedded boundary, FFT Poisson, Particle support, SDC time stepping

**APIs:** MPI, OpenMP, Hybrid MPI/OpenMP, CUDA, HIP, SYCL, Python

**Dependencies:**
- Required: CMake 3.18+, C++ compiler
- CUDA Backend: CUDA Toolkit

**Build Commands:**
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DAMReX_GPU_BACKEND=CUDA \
  -DAMReX_CUDA_ARCH=89 \
  -DAMReX_MPI=yes \
  ..
make -j8
```

**Run Commands:**
```bash
# Example application
cd Examples/*/
make -j8 USE_CUDA=TRUE
./executable inputs
```

**Input Configurations:**
- Correctness Test: Small example (~seconds)
- Performance Benchmark: Larger grids (~minutes)
- Input Files: Application-specific inputs files

**Expected Output:**
Iteration info, performance metrics (zones/second)

**Verification:** Extensive CI/CD (35+ test modules)

---

### 34. MFEM
**Type:** Library | **Tier:** A | **APIs:** 7
**Repository:** https://github.com/mfem/mfem

**Kernels:** Bilinear/linear/nonlinear forms, Diffusion/mass/elasticity integrators, DG, mixed FE, partial assembly, mesh refinement

**APIs:** MPI, OpenMP, CUDA, HIP, RAJA, OCCA, libCEED

**Dependencies:**
- Required: CMake 3.17+ or Make, C++ compiler
- CUDA Backend: CUDA Toolkit
- Optional: HYPRE, METIS

**Build Commands:**
```bash
# CUDA with Make
make cuda CUDA_ARCH=sm_89 -j4

# CMake
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DMFEM_USE_CUDA=YES \
  -DCUDA_ARCH=sm_89 \
  -DMFEM_USE_MPI=YES \
  ..
make -j4 install
```

**Run Commands:**
```bash
# Check build
make check

# Parallel example
mpirun -np 4 ./ex1p -m ../data/square-disc.mesh
```

**Input Configurations:**
- Correctness Test: Small mesh examples (~seconds)
- Performance Benchmark: Larger meshes (~minutes)
- Input Files: Mesh files in data/ directory

**Expected Output:**
Mesh info, FE space dimensions, assembly time, solution metrics

**Verification:** Catch2 unit tests (136 test files)

---

### 35. GROMACS
**Type:** Application | **Tier:** A | **APIs:** 7
**Repository:** https://gitlab.com/gromacs/gromacs

**Kernels:** NBNXM (nonbonded), PME (Particle Mesh Ewald), LINCS/SHAKE/SETTLE (constraints), Listed forces, Domain decomposition, Load balancing

**APIs:** MPI, OpenMP, CUDA, HIP, SYCL, OpenCL, Thread-MPI

**Dependencies:**
- Required: CMake 3.28+, C++ compiler
- CUDA Backend: CUDA Toolkit
- Optional: MPI, FFT libraries

**Build Commands:**
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
  -DGMX_GPU=CUDA \
  -DGMX_MPI=ON \
  -DGMX_OPENMP=ON \
  -DGMX_SIMD=AVX2_256 \
  -DCMAKE_INSTALL_PREFIX=$HOME/gromacs \
  ..
make -j8 install
```

**Run Commands:**
```bash
# Prepare system
gmx editconf -f input.pdb -o box.gro -c -d 1.0 -bt cubic
gmx solvate -cp box.gro -cs spc216.gro -o solvated.gro

# Run dynamics
gmx mdrun -deffnm simulation -v -ntmpi 1 -ntomp 8 -gpu_id 0

# Multi-GPU
gmx mdrun -deffnm simulation -v -ntmpi 4 -ntomp 8 -gpu_id 0123
```

**Input Configurations:**
- Correctness Test: Small system, few steps (~seconds)
- Performance Benchmark: Production system (~minutes to hours)
- Input Files: PDB/GRO structures, MDP parameter files

**Key Options:**
- `-ntmpi`: Number of thread-MPI ranks
- `-ntomp`: OpenMP threads per rank
- `-gpu_id`: GPU device IDs
- `-nsteps`: Number of simulation steps

**Expected Output:**
Simulation time, performance (ns/day), energy conservation

**Verification:** GoogleTest (440+ tests) + regression suite

---

## API Coverage Matrix (Top 20 Benchmarks)

| Benchmark | Serial | OpenMP | MPI | CUDA | HIP | SYCL | OpenCL | Kokkos | RAJA |
|-----------|--------|--------|-----|------|-----|------|--------|--------|------|
| BabelStream | ✓ | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| miniBUDE | ✓ | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CloverLeaf | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ | - |
| HeCBench | - | ✓ | - | ✓ | ✓ | ✓ | - | - | - |
| PRK | ✓ | ✓ | ✓ | - | - | - | - | - | - |
| Rodinia | - | ✓ | - | ✓ | - | - | ✓ | - | - |
| RAJAPerf | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✓ |
| Kokkos Kernels | ✓ | ✓ | - | ✓ | ✓ | ✓ | - | ✓ | - |
| NPB | - | ✓ | ✓ | - | - | - | - | - | - |
| LAMMPS | - | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ | - |

---

## Recommendations for Rosetta Stone Project

### Tier 1: Prime Candidates (Best Translation Corpus)

1. **BabelStream** — Simple kernels, 16+ APIs, straightforward verification
2. **HeCBench** — 513 kernels × 4 APIs = massive corpus, reference implementations
3. **RAJAPerf** — 80 kernels × 7+ APIs, checksum verification, production quality

### Tier 2: Good Multi-API Coverage

4. **miniBUDE** — Single kernel, 14 APIs, comprehensive CI
5. **CloverLeaf** — 23 kernels × 13 APIs, strong verification
6. **Rodinia** — 24 kernels × 3 APIs, established benchmark

### Tier 3: Specialized Value

7. **Kokkos Kernels** — Math kernel library, 7 backends
8. **PRK** — 12 kernels × 25+ language/API variants
9. **TeaLeaf** — Heat conduction, 8 APIs with solvers

### Gaps Identified

1. **MPI+GPU combinations** — Limited in many benchmarks
2. **SYCL coverage** — Growing but still less than CUDA/HIP
3. **Verification standardization** — Methods vary widely

---

## Failed Downloads (Require Manual Resolution)

| Archive | Issue | Suggested Action |
|---------|-------|------------------|
| Parboil.zip | 0 bytes | Manual download from UIUC |
| HPC_Challenge_HPCC.zip | 0 bytes | Manual download from hpcchallenge.org |
| SHOC.zip | 0 bytes | Manual download from github.com/vetter/shoc |
| Trilinos.zip | Skipped (200MB) | Download separately if needed |

---

## Document Metadata

- **Version:** 3.0
- **Created:** January 2026
- **Reference Platform:** NVIDIA RTX 4070 (12GB), AMD Ryzen 9 7900X, Ubuntu 22.04
- **Total Benchmarks:** 35
- **Run Commands Documented:** 35/35 (100%)
