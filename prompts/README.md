# ParBench Pipeline Prompts

These prompts are designed to be used with **Claude Code in VSCode** on the remote Linux PC (with NVIDIA RTX 4070 GPU) to expand the ParBench dataset from 5 pilot kernels to 20 kernels across 4 APIs.

## Phase Overview

| Phase | What It Does | Input | Output |
|-------|-------------|-------|--------|
| **Phase 0** | Environment setup | Fresh machine | HeCBench downloaded, paths configured, compiler inventory |
| **Phase 1** | Kernel selection | HeCBench source tree | 15 new kernel candidates (approved by you) |
| **Phase 2** | Spec generation | Approved kernel list | 60 new JSON specs + updated manifest (80 total) |
| **Phase 3** | Build & run (available compilers) | 80 specs | Build/run/verify results for CUDA + OpenMP |
| **Phase 4** | Install compilers & remaining APIs | Phase 3 results | HIP + SYCL installed, all 80 specs tested |
| **Phase 5** | Baseline population & validation | All test results | Specs with baseline_results, final report |

## How to Use

1. Open the remote PC in VSCode with Claude Code
2. Copy-paste the content of each phase prompt into Claude Code
3. **Wait for each phase to complete before starting the next**
4. Phase 1 requires your approval of kernel selection before proceeding to Phase 2
5. Phases 3–4 may require spec fixes — review the results before moving on

## Key Paths

- **Project**: `~/Desktop/parbench_sam/`
- **HeCBench**: `~/Desktop/downloads/HeCBench-master/`
- **Config**: `~/Desktop/parbench_sam/config/paths.json`
- **Results**: `~/Desktop/parbench_sam/results/phase{N}/`

## Target Scale

- **20 kernels** × **4 APIs** (CUDA, HIP, SYCL, OpenMP) = **80 specs**
- **240 directed translation pairs** (20 × 12 per kernel)
- All sourced from HeCBench (kernels must exist in all 4 API variants)
