# Phase 2: Generate JSON Specs for 15 New Kernels × 4 APIs = 60 New Specs

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

**Prerequisites**: Phase 0 and Phase 1 are complete. You have an approved list of 15 new kernels. HeCBench is downloaded. The existing 5 kernels × 4 APIs = 20 specs in `specs/` serve as templates.

### Context

You are working in `~/Desktop/parbench_sam/`. The project uses a two-level metadata system:
- **Level 1**: `manifest.jsonl` — one JSON line per kernel variant (discovery index)
- **Level 2**: `specs/<suite>-<kernel>-<api>.json` — detailed spec for each variant

You need to create 60 new spec files (15 kernels × 4 APIs) and add 60 new lines to `manifest.jsonl`.

### Reference: Existing Spec Structure

Study the existing specs carefully before generating new ones. Read these files:

```bash
cat ~/Desktop/parbench_sam/specs/hecbench-binomial-cuda.json   # has verification_only files
cat ~/Desktop/parbench_sam/specs/hecbench-nn-cuda.json         # has input data files in support
cat ~/Desktop/parbench_sam/specs/hecbench-radixsort-cuda.json  # multi-file prompt_payload
cat ~/Desktop/parbench_sam/templates/spec_template.json        # blank template
cat ~/Desktop/parbench_sam/schema/spec_schema.json             # the JSON schema definition
```

### Critical File Classification Rules

For EACH kernel variant, you must inspect the source directory and classify every file into exactly one of:

| Classification | Rule | Example |
|---|---|---|
| `prompt_payload` | Source files containing the parallel kernel logic that an LLM would need to translate. These are `.cu`, `.cpp`, or `.c` files with GPU/parallel API calls. | `kernel.cu`, `main.cu` |
| `support_files` | Build files (Makefile, CMakeLists.txt), shared headers that are API-agnostic and identical across variants, input data files. These are needed to compile but NOT shown to the LLM. | `Makefile`, `types.h`, `filelist.txt` |
| `verification_only` | Reference implementations, CPU gold-standard code, expected output files. NEVER shown to the LLM — used only to verify the LLM's translation. | `reference.cu`, `gold_output.txt` |

**CRITICAL CONSTRAINT**: A file MUST NOT appear in both `prompt_payload` and `verification_only`. This would leak the answer to the LLM.

**How to decide**: For each `.cu`/`.cpp` file, ask: "Does this file contain the parallel GPU/API code that the LLM needs to translate?" If YES → `prompt_payload`. "Does this file contain a CPU reference implementation used only for correctness checking?" If YES → `verification_only`. "Is this a build file, shared constant header, or input data?" If YES → `support_files`.

### Step-by-Step Process

For EACH of the 15 approved kernels, do the following for ALL 4 APIs (cuda, hip, sycl, omp):

#### Step 1: Inspect the source directory

```bash
KERNEL="<kernel_name>"
API="cuda"  # then hip, sycl, omp
SRC_DIR=~/Desktop/downloads/HeCBench-master/src/${KERNEL}-${API}

ls -la ${SRC_DIR}/
cat ${SRC_DIR}/Makefile
# Read each source file to understand its role
```

#### Step 2: Classify files

For each file in the directory, determine its classification. Pay special attention to:
- Files named `reference.*` → almost always `verification_only`
- Files named `kernel.*` or `main.*` → usually `prompt_payload`
- Files ending in `.h` → check if they contain API-specific code (→ prompt_payload) or just constants/structs (→ support_files)
- `Makefile`, `CMakeLists.txt` → always `support_files`

#### Step 3: Determine verification strategy

Read the source code to find how the kernel verifies correctness:
- Does it print "PASS" or "FAIL"? → `stdout_pattern` strategy
- Does it exit with code 0 on success? → `exit_code` strategy
- Does it print numeric results to compare? → `numeric_comparison` strategy
- Does it have a `reference.cu` file? → `reference_comparison` method

#### Step 4: Identify performance metrics

Look for timing output in the source:
```bash
grep -n "time\|Time\|kernel\|elapsed\|duration\|seconds\|msec\|us\b" ${SRC_DIR}/*.cu ${SRC_DIR}/*.cpp 2>/dev/null
```

Create regex extraction patterns for each metric (see existing specs for examples).

#### Step 5: Determine run arguments

```bash
# Check if the program takes command-line arguments
grep -n "argc\|argv\|atoi\|atof\|strtol" ${SRC_DIR}/*.cu ${SRC_DIR}/*.cpp 2>/dev/null
# Check the Makefile for run targets
grep -A5 "run:" ${SRC_DIR}/Makefile 2>/dev/null
```

#### Step 6: Generate the spec JSON

Create `specs/hecbench-<kernel>-<api>.json` following the exact schema. Use these values:

```json
{
    "spec_version": "1.0.0",
    "identity": {
        "kernel_name": "<KERNEL_NAME>",
        "parallel_api": "<API>",
        "unique_id": "hecbench-<KERNEL_NAME>-<API>",
        "source_suite": "hecbench"
    },
    "provenance": {
        "repository": {
            "url": "https://github.com/zjin-lcf/HeCBench",
            "commit": "archive-download",
            "branch": "master"
        },
        "repo_root": "HeCBench-master/",
        "source_path": "src/<KERNEL_NAME>-<API>",
        "license": "MIT"
    },
    "files": {
        "prompt_payload": ["<classified files>"],
        "support_files": ["<classified files>"],
        "verification_only": ["<classified files>"]
    },
    "implementation": {
        "api": "<API>",
        "api_version": null,
        "language": "C++",
        "language_standard": "C++17"
    },
    "build": {
        "environment": {
            "preferred": "system",
            "conda": null,
            "system": {
                "dependencies": ["<appropriate toolkit>"]
            }
        },
        "build_system": "make",
        "working_directory": "src/<KERNEL_NAME>-<API>",
        "commands": {
            "configure": null,
            "build": "<build command with ARCH=sm_89 for CUDA/HIP>",
            "clean": "make clean"
        },
        "variables": null,
        "outputs": {
            "executable": "main"
        }
    },
    ...
}
```

**Build commands by API:**
- CUDA: `"make ARCH=sm_89"` (dependencies: `["CUDA Toolkit >= 11.0", "GCC >= 9.0"]`)
- HIP: `"make ARCH=sm_89"` (dependencies: `["ROCm HIP >= 5.0", "GCC >= 9.0"]`)
- SYCL: `"make"` (dependencies: `["Intel oneAPI DPC++/C++ Compiler", "GCC >= 9.0"]`)
- OpenMP: `"make"` (dependencies: `["GCC >= 9.0 with OpenMP support"]`)

**Hardware section** — use this for ALL specs (matches the RTX 4070 on this machine):
```json
"hardware": {
    "target": "gpu",
    "requirements": {
        "gpu": {
            "vendor": "NVIDIA",
            "min_compute_capability": "sm_60",
            "min_memory_gb": 2
        }
    },
    "reference_platform": {
        "platform_id": "rtx4070-r9-7900x",
        "gpu": {
            "model": "NVIDIA GeForce RTX 4070",
            "architecture": "Ada Lovelace",
            "compute_capability": "sm_89",
            "vram_gb": 12,
            "memory_bandwidth_gbps": 504,
            "cuda_cores": 5888
        },
        "cpu": {
            "model": "AMD Ryzen 9 7900X",
            "cores": 12,
            "threads": 24,
            "base_clock_ghz": 4.7
        },
        "software": {
            "os": "Ubuntu 22.04 LTS",
            "cuda_toolkit": "12.x",
            "gcc": "11+",
            "driver": "525.x+"
        }
    }
}
```

For OpenMP kernels, change `"target": "cpu"` and adjust requirements accordingly.

#### Step 7: Add manifest entries

Append one line per variant to `manifest.jsonl`. Follow the exact format of existing entries:

```json
{"kernel_name":"<NAME>","parallel_api":"<API>","source_suite":"hecbench","category":"<DOMAIN>","spec_file":"specs/hecbench-<NAME>-<API>.json","source_dir":"HeCBench-master/src/<NAME>-<API>"}
```

Group entries by kernel (all 4 APIs together), matching the existing pattern.

#### Step 8: Validate

After generating ALL 60 specs and updating the manifest:

```bash
cd ~/Desktop/parbench_sam
python scripts/validate_schema.py --all
```

**Expected**: 80 specs pass (20 existing + 60 new). Fix any errors before proceeding.

### Deliverables

1. 60 new JSON spec files in `specs/` (15 kernels × 4 APIs)
2. Updated `manifest.jsonl` with 80 total entries (20 existing + 60 new)
3. `python scripts/validate_schema.py --all` passes with no errors
4. A summary log `analysis/phase2_spec_generation_log.md` listing each kernel, its file classifications, and any decisions made

### Do NOT

- Do NOT modify any of the 20 existing spec files
- Do NOT modify harness Python code or the schema
- Do NOT build or run anything (that's Phase 3)
- Do NOT set `baseline_results` — leave it as `null` (that's Phase 5)
- Do NOT guess file classifications — actually read each source file to understand its role
