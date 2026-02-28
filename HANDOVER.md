# ParBench Dataset Handover & Research Guide

**Version**: 1.0 (Phase 5 Complete)  
**Date**: 2026-02-16  
**Target Audience**: Research Teammates, LLM Evaluators  

This document provides a comprehensive guide to the **ParBench** dataset, a curated meta-benchmark for evaluating LLM-based parallel code translation. It explains the dataset architecture, file formats, and the exact workflow for conducting API-to-API translation experiments (e.g., CUDA $\to$ SYCL).

---

## 1. The Mental Model: How ParBench Works

ParBench is **not** just a folder of source code. It is a **meta-benchmark**—a structured layer of metadata wrapping existing high-performance computing (HPC) kernels.

### 1.1. Architecture
The dataset is organized into two levels of abstraction:

1.  **Level 1: The Manifest (`manifest.jsonl`)**
    *   The "Master Index."
    *   Contains high-level metadata for every kernel variant (API, name, file paths).
    *   Used for fast filtering and selecting benchmarks (e.g., "Find all CUDA kernels").

2.  **Level 2: The Specs (`specs/*.json`)**
    *   The "Source of Truth."
    *   Each JSON file represents **one specific kernel** implemented in **one specific API** (e.g., `hecbench-nbody-cuda.json`).
    *   It defines *everything* needed to handle that code: where the files are, how to build it, how to run it, and what the correct output looks like.

### 1.2. Anatomy of a Spec File
Every file in `specs/` follows a strict schema (`schema/spec_schema.json`). Key sections for your research:

*   **`identity`**: Unique ID (e.g., `hecbench-aes-sycl`) and original source suite.
*   **`files`**: Lists the source files utilized by the kernel:
    *   `prompt_payload`: The core logic files you typically feed to the LLM.
    *   `support_files`: Headers/Makefiles needed for compilation but often not translated.
    *   `verification_only`: Reference implementations used only for checking correctness.
*   **`build` & `run`**: exact shell commands and arguments to compile and execute the benchmark.
*   **`baseline_results`**: **CRITICAL**. This object contains the verified ground truth (stdout, exit code, performance metrics) collected on the reference hardware. You use this to validate if the LLM's translation is correct.

---

## 2. Directory Structure

| Path | Purpose |
|------|---------|
| `specs/` | **The Core Dataset**. 80 JSON spec files (20 kernels $\times$ 4 APIs). |
| `manifest.jsonl` | Master index / catalog. |
| `harness/` | The Python automation tool to build, run, and verify specs. |
| `schema/` | JSON schemas (draft-07) for validation. |
| `scripts/` | Helper scripts (reports, baseline population). |
| `analysis/reports/` | Final validation reports and performance summaries. |

---

## 3. Workflow for API-to-API Translation

Your primary task is to evaluate how well an LLM translates code from Source API (e.g., CUDA) to Target API (e.g., SYCL).

### Step 1: Select a Translation Pair
Use the harness to identify valid source-target pairs:

```bash
# List all 240+ valid directed translation pairs
python -m harness pairs
```
*Output Example:*
```
Kernel       Source -> Target
aes          cuda   -> sycl
nbody        omp    -> hip
...
```

### Step 2: Prepare the Prompt
For a given pair (e.g., `hecbench-nbody-cuda` $\to$ `hecbench-nbody-sycl`):

1.  **Read the Source Spec** (`specs/hecbench-nbody-cuda.json`).
2.  Extract files listed in `files.prompt_payload`.
3.  Construct your LLM prompt:
    > "Translate the following CUDA code to SYCL. Use the Intel oneAPI DPC++ extension..."
    > [Content of kernel.cu]

### Step 3: Get the Baseline (The "Target")
To verify the translation, you need the **Target Spec** (`specs/hecbench-nbody-sycl.json`). This file provides the ground truth:
1.  **Build Command**: How to compile the SYCL code.
2.  **Verification Logic**: What output string `Pass` or `0.002s` to look for.
3.  **Baseline Results**: The `baseline_results` field contains the actual output captured on the reference platform.

### Step 4: Evaluate the LLM Output
Save the LLM's generated code to a file (e.g., `nbody.sycl`). Then, use the spec's build/run instructions to compile and verify it.

**Manual Method:**
Read `specs/hecbench-nbody-sycl.json`, look at the `"build"` section, and run those shell commands manually on the generated file.

**Automated Method:**
The `harness` tool is designed for this. You can check the `harness/runner.py` logic to see how it executes the spec's commands.

---

## 4. Setup Instructions

### 4.1. Prerequisites
*   Linux Environment (Ubuntu 20.04+ recommended)
*   Python 3.8+
*   Compilers for target APIs (e.g., `nvcc` for CUDA, `icpx` for SYCL, `hipcc` for HIP)

### 4.2. Installation
```bash
# 1. Unzip the dataset
unzip parbench_dataset.zip
cd parbench_sam

# 2. Create virtual environment
python3 -m venv env_parbench
source env_parbench/bin/activate

# 3. Install Python dependencies
pip install jsonschema psutil rich
```

### 4.3. Validation
Ensure the dataset is intact before starting:
```bash
python scripts/validate_schema.py --all
```

---

## 5. Dataset Statistics (Phase 5)

*   **Total Kernels**: 20 (covering domains like encryption, physics, linear algebra)
*   **Total Specs**: 80
    *   20 CUDA
    *   20 HIP
    *   20 OpenMP
    *   20 SYCL
*   **Validated Baselines**: 47 specs have verified performance data on the Reference Platform (RTX 4070 + Ryzen 9).
    *   *Note*: HIP kernels currently have `baseline_results: null` as the reference platform lacks AMD hardware.

## 6. Known Limitations
1.  **HIP Support**: HIP specs are valid definitions but strictly "translation targets" on NVIDIA hardware—you cannot run them natively without `hip-on-cuda` or AMD hardware.
2.  **OpenMP Offload**: Some OpenMP kernels require specific GPU offloading flags which may need tuning depending on your compiler (GCC vs oneAPI).
