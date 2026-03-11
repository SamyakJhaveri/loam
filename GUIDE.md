# ParBench — Complete Guide

This guide explains the full ParBench pipeline: what each component does, how the pieces fit together, how to run every step, and how to add new benchmarks.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Core Concepts](#3-core-concepts)
4. [The Two-Level Metadata System](#4-the-two-level-metadata-system)
5. [The Harness: Build, Run, Verify](#5-the-harness-build-run-verify)
6. [Adding a New Benchmark](#6-adding-a-new-benchmark)
7. [Validation](#7-validation)
8. [Generating Reports](#8-generating-reports)
9. [End-to-End Workflow: LLM Translation Evaluation](#9-end-to-end-workflow-llm-translation-evaluation)
10. [Command Reference](#10-command-reference)
11. [File Security Model](#11-file-security-model)
12. [Folder Descriptions](#12-folder-descriptions)

---

## 1. Overview

ParBench is a meta-benchmark for evaluating how well LLMs translate parallel source code across different programming APIs (CUDA, HIP, SYCL, OpenMP). It aggregates kernels from existing benchmark suites (like HeCBench) and wraps each one in a machine-readable specification that drives automated build, run, verification, and evaluation workflows.

The key idea: given a kernel written in API **A** (e.g., CUDA), ask an LLM to translate it to API **B** (e.g., SYCL), then automatically build, run, and verify the translated code against known-good baselines.

### What makes it a "meta-benchmark"

ParBench doesn't contain benchmark source code itself. Instead, it provides structured metadata (specs) that point to existing benchmarks and describe exactly how to compile, execute, and verify them. This means adding a new kernel from any benchmark suite only requires writing a JSON spec file — no code changes to ParBench itself.

---

## 2. Project Structure

```
parbench_sam/
├── GUIDE.md                    # This file
├── README.md                   # Project overview
├── HANDOVER.md                 # Handover documentation
├── CLAUDE.md                   # Claude Code instructions
├── manifest.jsonl              # Level 1: Master index of all kernel variants
│
├── schema/                     # JSON Schema definitions (draft-07)
│   ├── manifest_schema.json    #   Schema for manifest.jsonl entries
│   ├── spec_schema.json        #   Schema for Level 2 kernel specs
│   └── reference_platform.json #   Shared hardware reference platform
│
├── specs/                      # Level 2: One spec file per kernel variant
│   └── <suite>-<kernel>-<api>.json
│
├── templates/
│   └── spec_template.json      # Blank spec template for new benchmarks
│
├── harness/                    # Python harness for build/run/verify
│   ├── __init__.py
│   ├── __main__.py             #   Entry point: python -m harness
│   ├── cli.py                  #   Command-line interface (--augment_level flag)
│   ├── builder.py              #   Compilation logic
│   ├── runner.py               #   Execution logic
│   ├── verifier.py             #   Output verification strategies
│   ├── spec_loader.py          #   JSON loading and path resolution
│   ├── reporter.py             #   Output formatting (text and JSON)
│   └── models.py               #   Data classes for results
│
├── c_augmentation/             # AST-driven augmentation transforms (libclang)
│   ├── augment_dataset.py      #   Core augmentation engine
│   ├── transforms.py           #   5 transform types (PointerArith, SwapCond, etc.)
│   └── test_transforms.py      #   Unit tests: python -m pytest c_augmentation/test_transforms.py
│
├── scripts/                    # Utility scripts (organized by purpose)
│   ├── validate_schema.py      #   JSON schema + cross-cutting validator
│   ├── generators/             #   Spec generation scripts
│   ├── survey/                 #   Codebase surveying scripts
│   ├── analysis/               #   Results analysis & reporting
│   ├── baselines/              #   Baseline population scripts
│   ├── augmentation/           #   augment_verify.py, run_augment_batch.py, combine_aug_results.py
│   ├── batch/                  #   Shell batch runners (.sh files)
│   └── archive/                #   One-time fix scripts
│
├── docs/                       # Design documents and planning
│   ├── design/                 #   json_schema_design.md, integrate_augmentation.md
│   └── plans/                  #   hecbench pilot plan, phase5 plan, workflow docs
│
├── presentations/              # Team deliverables (pptx, xlsx, speaking notes)
│
├── prompts/                    # Phase prompts and batch prompt docs
│
├── examples/
│   └── example_178_kernels.json # Reference: 178 kernels in single-file format
│
├── analysis/                   # All analysis outputs
│   ├── visualizations/         #   PNG charts and network graphs
│   ├── reports/                #   Markdown reports, augmentation bug report
│   └── data/                   #   CSV matrices, JSON surveys
│
├── results/                    # Test results by phase
│   ├── phase3/                 #   CUDA/OMP results
│   ├── phase5/                 #   HeCBench results
│   ├── rodinia/                #   Rodinia batch results
│   └── augmentation/           #   Augmentation test results and reports
│
├── rodinia/                    # Rodinia benchmark suite (git submodule)
│   └── rodinia-src/            #   Source at commit 9c10d3ea
│
└── config/                     # Machine-specific config (git-ignored)
    └── paths.json              #   Maps downloads_root to local path
```

---

## 3. Core Concepts

### Kernel
A single computational routine (e.g., nearest-neighbor search, radix sort, prefix scan) that exists in multiple API implementations. Each implementation is a separate "kernel variant."

### Kernel Variant
One specific implementation of a kernel in one API. For example, `nn` (nearest neighbor) has four variants: `hecbench-nn-cuda`, `hecbench-nn-hip`, `hecbench-nn-sycl`, `hecbench-nn-omp`.

### Translation Pair
An ordered pair of kernel variants for the same kernel in different APIs. For example, (CUDA → SYCL) means: give the LLM the CUDA source and ask it to produce SYCL. With 4 APIs per kernel, each kernel yields 4×3 = 12 ordered translation pairs.

### Prompt Payload
The specific source files shown to the LLM for translation. These are carefully curated — the LLM sees only the files it needs, never the verification/test harness code.

### Verification Strategy
How to check if a translated kernel produced correct output. Strategies include: checking exit codes, matching stdout patterns, comparing floating-point results within tolerance, and running custom verification scripts.

---

## 4. The Two-Level Metadata System

### Level 1: manifest.jsonl (Discovery Index)

The manifest is a line-delimited JSON file where each line indexes one kernel variant. It answers: "What kernels exist and where are their specs?"

**Fields:**

| Field          | Type   | Required | Description                              |
|----------------|--------|----------|------------------------------------------|
| `kernel_name`  | string | Yes      | Logical kernel name (pairing key)        |
| `parallel_api` | enum   | Yes      | API: cuda, hip, sycl, omp, serial        |
| `source_suite` | string | Yes      | Origin benchmark suite (e.g., hecbench)  |
| `spec_file`    | string | Yes      | Relative path to Level 2 spec JSON       |
| `source_dir`   | string | Yes      | Relative path to kernel source files     |
| `category`     | enum   | No       | Domain: ml, graph, physics, financial... |

**Example entry:**
```json
{"kernel_name":"nn","parallel_api":"cuda","source_suite":"hecbench","category":"graph","spec_file":"specs/hecbench-nn-cuda.json","source_dir":"HeCBench-master/src/nn-cuda"}
```

### Level 2: Spec Files (specs/*.json)

Each spec is a comprehensive JSON file that drives the entire evaluation pipeline for one kernel variant. It answers: "How do I build, run, and verify this specific kernel?"

**Top-level sections:**

| Section            | Purpose                                                    |
|--------------------|------------------------------------------------------------|
| `identity`         | Unique ID, kernel name, API, source suite                  |
| `provenance`       | Repository URL, pinned commit, license                     |
| `files`            | File classification: prompt_payload, support, verification |
| `implementation`   | Language, API details                                      |
| `build`            | Dependencies, build system, commands, output executable    |
| `run`              | Executable path, arguments, timeout, input configs         |
| `verification`     | Method, strategies, floating-point tolerance               |
| `performance`      | Metric extraction patterns (regex), warmup/measurement     |
| `hardware`         | Target device (GPU/CPU), requirements, reference platform  |
| `baseline_results` | Known-good results from reference platform (populated after benchmarking) |
| `metadata`         | Description, domain, complexity tags                       |

The `unique_id` follows the convention: `{source_suite}-{kernel_name}-{api}` (e.g., `hecbench-nn-cuda`).

---

## 5. The Harness: Build, Run, Verify

The harness is a Python module (`harness/`) that automates the full evaluation pipeline. It reads a spec file and executes each stage.

### 5.1 Build

**What it does:** Compiles the kernel source code using the spec's build commands.

**How it works:**
1. Resolves the working directory from `build.working_directory` relative to `provenance.repo_root`
2. Substitutes variables (e.g., `${ARCH}`) with values from `build.variables`
3. Runs `build.commands.configure` (if set), then `build.commands.build`
4. Checks that `build.outputs.executable` was produced

**Command:**
```bash
python -m harness build specs/hecbench-nn-cuda.json
python -m harness build specs/hecbench-nn-cuda.json -v  # verbose
```

### 5.2 Run

**What it does:** Executes the compiled kernel binary with a specified input configuration.

**How it works:**
1. Locates the executable from `build.outputs.executable`
2. Selects an input configuration (e.g., "correctness" or "performance") from `run.input_configurations`
3. Runs the executable with the configuration's arguments
4. Captures stdout, stderr, exit code, and wall-clock time
5. Enforces `run.timeout_seconds`

**Command:**
```bash
python -m harness run specs/hecbench-nn-cuda.json                    # default: correctness
python -m harness run specs/hecbench-nn-cuda.json --config performance
```

### 5.3 Verify

**What it does:** Runs the full pipeline (build → run → verify) and checks the output.

**How it works:**
1. Builds the kernel
2. Runs it with the specified configuration
3. Applies each verification strategy in order:
   - `exit_code`: Checks the process exit code matches `expected` (typically 0)
   - `stdout_pattern`: Matches a regex pattern against stdout (e.g., "PASS")
   - `numeric_comparison`: Compares extracted numeric values within floating-point tolerance
   - `file_diff`: Compares output files against reference files
   - `custom_script`: Runs an external verification script
4. Extracts performance metrics using regex patterns from `performance.metrics`
5. Reports PASS/FAIL with details

**Command:**
```bash
python -m harness verify specs/hecbench-nn-cuda.json
python -m harness verify specs/hecbench-nn-cuda.json --config performance --json
```

### 5.4 Other Commands

**View the prompt payload** (what the LLM would see):
```bash
python -m harness prompt specs/hecbench-nn-cuda.json
```

**Print spec summary** (no build/run):
```bash
python -m harness info specs/hecbench-nn-cuda.json
```

**List all translation pairs** from the manifest:
```bash
python -m harness pairs
```

---

## 6. Adding a New Benchmark

This is the step-by-step process for adding a new kernel to ParBench.

### Step 1: Obtain the Source Code

Download or clone the benchmark repository. Place it in the downloads directory (configured in `config/paths.json`). Pin to a specific commit for reproducibility.

### Step 2: Create the Spec File

Copy the template and fill in every section:

```bash
cp templates/spec_template.json specs/<suite>-<kernel>-<api>.json
```

**Naming convention:** `{source_suite}-{kernel_name}-{parallel_api}.json`

Fill in these critical sections:

**identity:** Set `unique_id` to match the filename (minus `.json`).
```json
{
  "kernel_name": "my-kernel",
  "parallel_api": "cuda",
  "unique_id": "mysuite-my-kernel-cuda",
  "source_suite": "mysuite"
}
```

**provenance:** Pin the exact repository commit.
```json
{
  "repository": {
    "url": "https://github.com/org/repo",
    "commit": "abc123",
    "branch": "main"
  },
  "repo_root": "repo-name/",
  "source_path": "src/my-kernel-cuda",
  "license": "MIT"
}
```

**files:** Classify every file in the source directory.
```json
{
  "prompt_payload": ["kernel.cu", "kernel.h"],
  "support_files": ["Makefile", "utils.h"],
  "verification_only": ["reference_output.txt"]
}
```

**build:** Specify how to compile.
```json
{
  "build_system": "make",
  "working_directory": "src/my-kernel-cuda",
  "commands": {
    "build": "make ARCH=sm_89",
    "clean": "make clean"
  },
  "outputs": { "executable": "main" }
}
```

**run:** Specify how to execute and which input configurations to support.

**verification:** Define how to check correctness.

**hardware:** Specify target device and requirements.

### Step 3: Add the Manifest Entry

Append one line to `manifest.jsonl`:

```json
{"kernel_name":"my-kernel","parallel_api":"cuda","source_suite":"mysuite","category":"sort","spec_file":"specs/mysuite-my-kernel-cuda.json","source_dir":"repo-name/src/my-kernel-cuda"}
```

### Step 4: Validate

```bash
# Validate just your new spec
python scripts/validate_schema.py --spec specs/mysuite-my-kernel-cuda.json

# Validate everything (manifest + all specs + cross-checks)
python scripts/validate_schema.py --all
```

### Step 5: Run the Baseline

```bash
# Build, run, and verify on your reference hardware
python -m harness verify specs/mysuite-my-kernel-cuda.json --json

# Capture the output and populate baseline_results in your spec
```

### Step 6: Repeat for Other APIs

Create one spec file per API implementation of the same kernel (e.g., CUDA, HIP, SYCL, OpenMP). Add each to the manifest.

---

## 7. Validation

The validator (`scripts/validate_schema.py`) performs comprehensive checks:

**Schema checks:**
- JSON Schema draft-07 conformance for both manifest entries and spec files

**Cross-cutting checks:**
- `unique_id` matches the spec filename
- `unique_id` format matches `{source_suite}-{kernel_name}-{api}`
- `implementation.api` matches `identity.parallel_api`
- All files in `files.*` exist on disk
- No file appears in both `prompt_payload` and `verification_only`
- Build working directory exists
- Build command variables are defined
- Manifest `kernel_name` and `parallel_api` match the linked spec
- Every spec in `specs/` has a manifest entry (and vice versa)

**Pairing checks:**
- Each kernel has at least 2 API implementations (otherwise it can't be used for translation)
- Reports total number of translation pairs

**Commands:**
```bash
# Validate manifest only
python scripts/validate_schema.py --manifest manifest.jsonl

# Validate a single spec
python scripts/validate_schema.py --spec specs/hecbench-nn-cuda.json

# Validate everything
python scripts/validate_schema.py --all
```

---

## 8. Generating Reports

### Pilot Report

Generate a markdown summary of all kernels and their status:

```bash
python scripts/analysis/generate_report.py
```

This reads `manifest.jsonl` and all spec files, collects statistics (kernels per API, domains, verification methods), and writes `analysis/reports/pilot_report.md`.

### Pilot Spec Generation

To regenerate the 20 pilot spec files (5 HeCBench kernels × 4 APIs):

```bash
python scripts/generators/generate_pilot_specs.py
```

This overwrites files in `specs/` and `manifest.jsonl` with the pilot configuration.

---

## 9. End-to-End Workflow: LLM Translation Evaluation

Here is the complete workflow for evaluating an LLM's ability to translate parallel code:

```
┌──────────────────────────────────────────────────────────┐
│  1. DISCOVER: Load manifest.jsonl                        │
│     → Find all kernel variants and their APIs            │
├──────────────────────────────────────────────────────────┤
│  2. SELECT PAIR: e.g., CUDA → SYCL for kernel "nn"      │
│     → Load source spec (hecbench-nn-cuda.json)           │
│     → Load target spec (hecbench-nn-sycl.json)           │
├──────────────────────────────────────────────────────────┤
│  3. EXTRACT PROMPT: Get prompt_payload from source spec  │
│     → Only the curated source files (kernel.cu, kernel.h)│
│     → Never verification_only or support_files           │
├──────────────────────────────────────────────────────────┤
│  4. SEND TO LLM: Provide source code + translation task  │
│     → "Translate this CUDA kernel to SYCL"               │
│     → LLM produces translated source files               │
├──────────────────────────────────────────────────────────┤
│  5. BUILD: Use target spec's build commands               │
│     → Compile the LLM's translated code                  │
│     → Check: did it compile?                             │
├──────────────────────────────────────────────────────────┤
│  6. RUN: Use target spec's run configuration              │
│     → Execute the compiled binary                        │
│     → Capture stdout, stderr, exit code                  │
├──────────────────────────────────────────────────────────┤
│  7. VERIFY: Apply target spec's verification strategies   │
│     → Check exit code, stdout patterns, numeric results  │
│     → Compare against baseline_results                   │
├──────────────────────────────────────────────────────────┤
│  8. METRICS: Extract performance measurements             │
│     → Kernel time, offloading time, etc.                 │
│     → Compare against baseline performance               │
├──────────────────────────────────────────────────────────┤
│  9. REPORT: Aggregate results across all pairs            │
│     → Pass rate, compilation rate, performance ratios    │
└──────────────────────────────────────────────────────────┘
```

### Viewing the prompt payload

To see exactly what the LLM would receive:
```bash
python -m harness prompt specs/hecbench-nn-cuda.json
```

### Listing all translation pairs

```bash
python -m harness pairs
```

This reads the manifest, groups by kernel name, and lists all source→target API pairs.

---

## 10. Command Reference

### Harness Commands

| Command | Description | Example |
|---------|-------------|---------|
| `build` | Compile a kernel from its spec | `python -m harness build specs/hecbench-nn-cuda.json` |
| `run` | Run a compiled kernel | `python -m harness run specs/hecbench-nn-cuda.json --config correctness` |
| `verify` | Full pipeline: build → run → verify | `python -m harness verify specs/hecbench-nn-cuda.json --json` |
| `prompt` | Print what the LLM would see | `python -m harness prompt specs/hecbench-nn-cuda.json` |
| `info` | Print spec summary (no build/run) | `python -m harness info specs/hecbench-nn-cuda.json` |
| `pairs` | List all translation pairs | `python -m harness pairs` |

### Global Flags

| Flag | Description |
|------|-------------|
| `--project-root PATH` | Path to parbench_sam/ root (default: cwd) |
| `--manifest FILE` | Manifest filename (default: manifest.jsonl) |
| `-v, --verbose` | Show subprocess stdout/stderr |
| `--json` | Also output machine-readable JSON |

### Validation Commands

| Command | Description |
|---------|-------------|
| `python scripts/validate_schema.py --manifest manifest.jsonl` | Validate manifest entries |
| `python scripts/validate_schema.py --spec specs/<file>.json` | Validate a single spec |
| `python scripts/validate_schema.py --all` | Validate everything + cross-checks |

### Report Generation

| Command | Description |
|---------|-------------|
| `python scripts/analysis/generate_report.py` | Generate pilot summary report |
| `python scripts/generators/generate_pilot_specs.py` | Regenerate all 20 pilot specs |

---

## 11. File Security Model

The file classification system is critical for fair LLM evaluation:

| Classification       | Who sees it?         | Purpose                                    |
|----------------------|----------------------|--------------------------------------------|
| `prompt_payload`     | LLM + build system   | Source files the LLM must translate         |
| `support_files`      | Build system only     | Makefiles, shared headers for compilation   |
| `verification_only`  | Verifier only         | Reference outputs, test harnesses           |

**Rules:**
- A file CANNOT appear in both `prompt_payload` and `verification_only` (this would leak answers to the LLM)
- A file CAN appear in both `prompt_payload` and `support_files` (e.g., a header used by both the kernel and the build)
- Every file in the source directory SHOULD be classified in at least one list (orphan files trigger a warning)

---

## 12. Folder Descriptions

| Folder | Contents |
|--------|----------|
| `schema/` | JSON Schema definitions that validate manifest and spec files |
| `specs/` | One JSON spec file per kernel variant (the heart of the benchmark) |
| `templates/` | Blank spec template for creating new benchmarks |
| `harness/` | Python build/run/verify automation framework |
| `scripts/` | Utility scripts: validation, spec generation, report generation |
| `examples/` | Reference data (e.g., 178-kernel single-file format example) |
| `analysis/visualizations/` | PNG charts: coverage heatmaps, network graphs, bar charts |
| `analysis/reports/` | Markdown reports, pilot summaries, presentation materials |
| `analysis/data/` | CSV matrices, Excel workbooks, download scripts |
| `config/` | Machine-specific configuration (git-ignored) |

---

## Prerequisites

- Python 3.10+
- `jsonschema` package: `pip install jsonschema`
- For building kernels: CUDA Toolkit, ROCm, oneAPI, or GCC (depending on target API)
- For running kernels: appropriate GPU or multi-core CPU

## Quick Start

```bash
# 1. Install dependencies
pip install jsonschema

# 2. Validate all specs
python scripts/validate_schema.py --all

# 3. List available translation pairs
python -m harness pairs

# 4. View what the LLM would see for a CUDA kernel
python -m harness prompt specs/hecbench-nn-cuda.json

# 5. Build and verify a kernel (requires appropriate hardware)
python -m harness verify specs/hecbench-nn-cuda.json -v
```
