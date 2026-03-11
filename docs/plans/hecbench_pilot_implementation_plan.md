# ParBench Implementation Plan — HeCBench Pilot

## Overview

This plan breaks the HeCBench pilot into 4 phases. Each phase has a detailed prompt you can paste directly into Claude Code in VS Code.

**Pilot kernels (5 kernels × 4 APIs = 20 specs):**
- `nn` — nearest neighbor (classic GPU, simple)
- `scan` — prefix sum (fundamental parallel primitive)
- `particle-diffusion` — physics simulation
- `binomial` — financial computing (binomial options)
- `radixsort` — parallel sorting

**Two-machine workflow:**
- **Mac (M1):** Development, spec authoring, harness code (Phases 1-4)
- **Linux LC (Ryzen 9 + RTX 4070):** Build, run, verify, collect baselines (Phase 5)
- **Sync:** Git repo (push from Mac, pull on Linux)
- **SSH:** Mac → Linux LC for remote work

**Mac paths:**
- Working directory: `/Users/samyakjhaveri/Desktop/ParBench/parbench_sam/`
- Downloaded repos (for inspection): `/Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads/`

**Linux LC paths (set up in Phase 5):**
- Working directory: `~/parbench/` (git clone)
- Downloaded repos: `~/parbench/downloads/` (cloned fresh on Linux)

**Path strategy:** All specs use RELATIVE paths. A `config/paths.json` file (gitignored) maps logical names to machine-specific absolute paths. The harness reads this config to resolve paths.

---

## Phase 1: Project Scaffolding + JSON Schema Definition

**Goal:** Create the project directory structure, a Python-importable JSON schema (as a Python dict/jsonschema), and template files.

**What gets created:**
- Directory tree
- `schema/manifest_schema.json` — formal JSON Schema for manifest entries
- `schema/spec_schema.json` — formal JSON Schema for Level 2 specs
- `schema/reference_platform.json` — shared hardware reference (DRY)
- `templates/spec_template.json` — empty template for filling in specs
- `scripts/validate_schema.py` — validates any spec against the schema

### Claude Code Prompt — Phase 1

```
PROJECT CONTEXT:
I'm building ParBench, a meta-benchmark for evaluating LLM-based parallel code translation. 
Working directory: /Users/samyakjhaveri/Desktop/ParBench/parbench_sam/
Downloaded benchmark repos are at: /Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads/

TASK: Create the project scaffolding and formal JSON schemas.

1. Create this directory structure:
```
parbench_sam/
├── schema/
│   ├── manifest_schema.json
│   ├── spec_schema.json
│   └── reference_platform.json
├── specs/
│   └── (empty, will be populated in Phase 2)
├── manifest.jsonl              (empty file)
├── templates/
│   └── spec_template.json
├── scripts/
│   ├── validate_schema.py
│   └── __init__.py
├── config/
│   └── paths.example.json
├── reports/
│   └── (empty, will be populated later)
├── .gitignore
└── README.md
```

ALSO create `.gitignore` with:
```
# Machine-specific config (each machine has its own)
config/paths.json

# Downloaded benchmark repos (too large for git)
downloads/

# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store
```

ALSO create `config/paths.example.json` — template for machine-specific config:
```json
{
  "_comment": "Copy this to paths.json and edit for your machine. paths.json is gitignored.",
  "project_root": "/path/to/parbench",
  "downloads_root": "/path/to/parbench/downloads",
  "hecbench_root": "/path/to/parbench/downloads/HeCBench"
}
```

ALSO create `config/paths.json` for the Mac:
```json
{
  "project_root": "/Users/samyakjhaveri/Desktop/ParBench/parbench_sam",
  "downloads_root": "/Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads",
  "hecbench_root": "/Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads/HeCBench-master"
}
```
NOTE: The hecbench_root value should match the ACTUAL directory name on disk. Check with:
  ls /Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads/ | grep -i hec

2. Create `schema/manifest_schema.json` — a JSON Schema (draft-07) for manifest.jsonl entries:
Required fields:
  - kernel_name (string): logical kernel name, used as pairing key
  - parallel_api (string, enum): one of [serial, cuda, hip, sycl, opencl, omp, omp_target, openacc, kokkos, raja, mpi, omp_mpi, tbb, stdpar, thrust]
  - source_suite (string): origin benchmark (lowercase)
  - spec_file (string): relative path to Level 2 spec JSON
  - source_dir (string): relative path to directory with all relevant source files
Optional fields:
  - category (string, enum): [ml, graph, physics, linear_algebra, stencil, reduction, sort, molecular_dynamics, image, crypto, financial, other]

3. Create `schema/spec_schema.json` — a JSON Schema (draft-07) for Level 2 spec files.
The spec has these top-level sections (all details below):

  "spec_version": "1.0.0" (string, required)

  "identity" (required object):
    - kernel_name (string, required)
    - parallel_api (string, required, same enum as manifest)
    - unique_id (string, required): format "{source_suite}-{kernel_name}-{api}"
    - source_suite (string, required)

  "provenance" (required object):
    - repository.url (string, required): git URL
    - repository.commit (string, required): pinned commit hash
    - repository.branch (string, optional)
    - repo_root (string, required): RELATIVE path from downloads_root (in config/paths.json) to the cloned repo directory. Example: "HeCBench/" (NOT an absolute path)
    - source_path (string, required): path from repo_root to kernel directory. Example: "src/adam-cuda/"
    - license (string, optional)
    
    Path resolution: full_path = config.downloads_root / spec.repo_root / spec.source_path

  "files" (required object) — THIS IS CRITICAL for LLM evaluation security:
    - prompt_payload (array of strings, required, minItems 1): files the LLM receives for translation. ONLY these go in the prompt.
    - support_files (array of strings, optional, default []): build files, shared headers needed for compilation but NOT sent to LLM
    - verification_only (array of strings, optional, default []): reference implementations, test harnesses. NEVER shown to LLM.

  "implementation" (required object):
    - api (string, required)
    - api_version (string, optional)
    - language (string, required): C++, C, Fortran
    - language_standard (string, optional): C++17, C++14, etc.

  "build" (required object):
    - environment.preferred (string, required): "conda" or "system"
    - environment.conda (object, optional): {environment_file, channels[], packages[]}
    - environment.system (object, required): {dependencies[]}
    - build_system (string, required): make, cmake, cmake+make, autotools
    - working_directory (string, required): relative to repo_root
    - commands.configure (string or null, optional)
    - commands.build (string, required)
    - commands.clean (string, optional)
    - variables (object, optional): template variables with {description, default, detection}
    - outputs.executable (string, required)

  "run" (required object):
    - executable (string, required)
    - default_arguments (array of strings, required)
    - timeout_seconds (integer, required, default 300)
    - environment_variables (object, optional)
    - input_configurations (object, required): keyed by config name, each has:
        - arguments (array of strings, required)
        - description (string, required)
        - input_files (array of strings, optional, default [])
        - expected_results (object or null, optional): {stdout_pattern, reference_output_file}

  "verification" (required object):
    - method (string, required): self_checking, reference_comparison, external_script
    - strategies (array, required, minItems 1): each has:
        - type (string, required): exit_code, stdout_pattern, numeric_comparison, file_diff, custom_script
        - Plus type-specific fields (pattern, expected, tolerance, etc.)
    - floating_point (object, optional): {tolerance, tolerance_type, note}

  "performance" (optional object):
    - metrics (array): each has {name, extraction.type, extraction.pattern, extraction.capture_group, unit}
    - warmup_runs (integer)
    - measurement_runs (integer)

  "hardware" (required object):
    - target (string, required): gpu, cpu, both
    - requirements.gpu (object, optional): {vendor, min_compute_capability, min_memory_gb}
    - requirements.cpu (object, optional): {min_cores, min_memory_gb}
    - reference_platform (object, required): use the shared reference from reference_platform.json via $ref or just inline it

  "baseline_results" (object or null): starts as null, populated after benchmarking:
    - reference_platform (string): platform_id
    - timestamp (string): ISO 8601
    - configurations (object): keyed by input_configuration name, each has:
        - status (string): pass, fail, error, timeout
        - exit_code (integer)
        - stdout_snippet (string)
        - wall_time_seconds (number)
        - metrics (object, optional): key-value pairs of extracted metrics

  "metadata" (optional object):
    - description (string)
    - domain (string)
    - complexity (string)
    - tags (array of strings)
    - multi_file (boolean)

4. Create `schema/reference_platform.json` — the shared hardware reference:
```json
{
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
```

5. Create `templates/spec_template.json` — a blank spec with all fields present, placeholder values, and comments explaining each field. Use null for optional fields, empty strings/arrays for required ones.

6. Create `scripts/validate_schema.py`:
  - Uses `jsonschema` library (pip install jsonschema)
  - Loads config/paths.json for path resolution
  - Has two functions:
    - validate_manifest_entry(entry_dict) -> list of errors
    - validate_spec(spec_dict) -> list of errors
  - Has a CLI mode: `python validate_schema.py --manifest manifest.jsonl` validates all entries
  - And: `python validate_schema.py --spec specs/some-spec.json` validates one spec
  - And: `python validate_schema.py --all` validates manifest + all linked specs
  - And: `python validate_schema.py --schema-only` validates schema structure WITHOUT checking file paths on disk (useful on Mac where repos may not be at the same location)
  - When --schema-only is NOT set, also checks: unique_id matches filename, all file paths in files.* actually exist on disk (resolved via config/paths.json), no file appears in both prompt_payload and verification_only
  - Path resolution uses: config.downloads_root / spec.provenance.repo_root / spec.provenance.source_path / filename

7. Create a minimal README.md explaining the project structure and schema.

IMPORTANT NOTES:
- Use jsonschema draft-07 format
- All paths in the schema should be relative to the parbench_sam/ project root
- The downloaded repos are at ../ParBench/downloads/ relative to parbench_sam/
- Python 3.10+ is fine
- Keep the code clean and well-commented
```

---

## Phase 2: Inspect HeCBench Pilot Kernels + Create Specs

**Goal:** Look at the actual source files for the 5 pilot kernels across all 4 APIs, then create the 20 JSON spec files + manifest entries.

**Runs on:** Mac (inspecting local copy of HeCBench for file contents, creating specs)

**What gets created:**
- 20 spec files in `specs/` (5 kernels × 4 APIs)
- 20 lines in `manifest.jsonl`
- A populated and validated dataset

### Claude Code Prompt — Phase 2

```
PROJECT CONTEXT:
I'm building ParBench, a meta-benchmark for LLM parallel code translation evaluation.
Working directory: /Users/samyakjhaveri/Desktop/ParBench/parbench_sam/
Downloaded HeCBench repo (for inspection): read hecbench_root from config/paths.json

TWO-MACHINE NOTE: Specs are authored here on Mac but will run on a Linux LC.
All paths in specs must be RELATIVE:
- repo_root: relative to downloads_root (e.g., "HeCBench-master/" not "/Users/.../HeCBench-master/")
- source_path: relative to repo_root (e.g., "src/nn-cuda/")
- files: relative to repo_root/source_path (e.g., "main.cu")
The harness resolves full paths using config/paths.json at runtime.

Phase 1 is complete — the schema files, templates, and validation script exist in the project.

TASK: Inspect 5 HeCBench kernels and create their JSON specs.

STEP 1 — INSPECT SOURCE DIRECTORIES

For each of the 5 kernels below, inspect ALL 4 API variants in the HeCBench repo.
HeCBench follows the pattern: src/{kernel_name}-{api}/ where api is one of: cuda, hip, sycl, omp

The 5 pilot kernels are:
  1. nn (nearest neighbor)
  2. scan (prefix sum)
  3. particle-diffusion
  4. binomial (binomial options pricing)
  5. radixsort

For each of the 20 directories (5 kernels × 4 APIs), do:
  a) List all files: ls -la /Users/samyakjhaveri/Desktop/ParBench/ParBench/downloads/HeCBench*/src/{kernel}-{api}/
  b) Read the main source file (main.cu, main.cpp, etc.) — note the structure
  c) Read the Makefile or CMakeLists.txt to understand build commands
  d) Identify:
     - Which file(s) are the kernel code (-> prompt_payload)
     - Which file(s) are headers/build files (-> support_files)  
     - Which file(s) are reference/verification implementations (-> verification_only)
       HINT: files named reference.h, verify.h, *_reference.*, *_cpu.* are often verification
     - What arguments/inputs the program expects (look at main() argv parsing)
     - How verification works (look for "PASS"/"FAIL" prints, tolerance checks, etc.)
     - What performance output it prints (look for timing prints)

STEP 2 — CREATE SPEC FILES

For each of the 20 kernel-API combinations, create a spec JSON file at:
  specs/hecbench-{kernel_name}-{api}.json

Follow the schema defined in schema/spec_schema.json.

Key field values to use:

identity:
  - unique_id: "hecbench-{kernel_name}-{api}"
  - source_suite: "hecbench"

provenance:
  - repo_root: Use the RELATIVE directory name only (e.g., "HeCBench-master/" or "HeCBench/"). 
    Find it: read config/paths.json, then basename of hecbench_root + "/"
    This must NOT be an absolute path. It is relative to downloads_root.
  - source_path: "src/{kernel_name}-{api}/"
  - repository.url: "https://github.com/zjin-lcf/HeCBench"
  - repository.commit: check with `cd <hecbench_root> && git rev-parse HEAD` or if not a git repo, use "archive-download" as placeholder
  - repository.branch: "master"

files:
  - prompt_payload: the main source file(s) that contain the kernel logic
  - support_files: Makefile, CMakeLists.txt, utility headers
  - verification_only: reference.h or any CPU reference implementation files
  CRITICAL: A file must NOT appear in both prompt_payload and verification_only

implementation:
  - For cuda: api="cuda", language="C++", language_standard="C++17"
  - For hip: api="hip", language="C++", language_standard="C++17"
  - For sycl: api="sycl", language="C++", language_standard="C++17"
  - For omp: api="omp", language="C++", language_standard="C++17" (or "C" if it's .c files)

build:
  - environment.preferred: "system"
  - environment.system.dependencies: 
    - cuda: ["CUDA Toolkit >= 11.0", "GCC >= 9.0"]
    - hip: ["ROCm >= 5.0", "hipcc"]
    - sycl: ["oneAPI >= 2023.0", "icpx"]
    - omp: ["GCC >= 9.0"]
  - build_system: check Makefile vs CMakeLists.txt
  - working_directory: "src/{kernel_name}-{api}/"
  - commands.build: extract from Makefile (typically "make" or "make ARCH=sm_89")
    - For CUDA kernels: look at the Makefile for the ARCH variable, use "make ARCH=sm_89"
    - Read the actual Makefile to get the correct build command
  - commands.clean: "make clean" (usually)
  - outputs.executable: check what the Makefile produces (usually "main" or the kernel name)

run:
  - executable: usually "./main" — check Makefile
  - default_arguments: extract from main() argv parsing or Makefile run target
  - timeout_seconds: 300
  - input_configurations:
    - "correctness": smaller arguments for quick validation
    - "performance": larger arguments for benchmarking
    - Determine appropriate sizes by reading the source code's argument parsing

verification:
  - method: look at the source code
    - If it prints "PASS"/"FAIL": method="self_checking", strategy type="stdout_pattern"
    - If it compares against a reference: method="reference_comparison"
  - strategies: create appropriate strategy entries based on what you find
  - Always include exit_code check as first strategy

performance:
  - metrics: look for timing output patterns in the source code
    - Common patterns: "Average time:", "kernel time", "elapsed", "Total time"
    - Create regex patterns to extract these values
  - warmup_runs: 1
  - measurement_runs: 5

hardware:
  - target: "gpu" for cuda/hip/sycl, "cpu" for omp
  - requirements: appropriate for each API
  - reference_platform: load and inline from schema/reference_platform.json

baseline_results: null (will be populated later when we actually run them)

metadata:
  - description: brief description of what the kernel does
  - domain: appropriate category
  - tags: relevant tags
  - multi_file: true if prompt_payload has more than one file

STEP 3 — CREATE MANIFEST ENTRIES

Append 20 lines to manifest.jsonl (one per kernel-API combination):
```json
{"kernel_name": "nn", "parallel_api": "cuda", "source_suite": "hecbench", "category": "graph", "spec_file": "specs/hecbench-nn-cuda.json", "source_dir": "HeCBench-master/src/nn-cuda/"}
```
Use the ACTUAL repo directory name (e.g., "HeCBench-master" or "HeCBench") — check config/paths.json.
source_dir is RELATIVE to downloads_root, same as repo_root + source_path.

Categories for the 5 kernels:
  - nn: "graph"
  - scan: "reduction"  
  - particle-diffusion: "physics"
  - binomial: "financial"
  - radixsort: "sort"

STEP 4 — VALIDATE

Run the validation script from Phase 1:
  python scripts/validate_schema.py --all

Fix any validation errors. All 20 specs and all 20 manifest entries should pass validation.

IMPORTANT NOTES:
- READ THE ACTUAL FILES before creating specs. Do not guess at file contents, build commands, or arguments.
- The HeCBench repo directory name under downloads/ may not be exactly "HeCBench-master" — check the actual name.
- Some kernels may have slightly different directory structures — adapt accordingly.
- If a kernel directory doesn't exist for a particular API, note it and skip that spec.
- Pay special attention to identifying verification_only files — these are critical for the LLM evaluation security boundary.
```

---

## Phase 3: Validation Script Enhancement + Path Checking

**Goal:** Enhance the validation script to do deep checks — verify all paths resolve, check for file classification conflicts, and produce a summary report.

**Runs on:** Mac (schema + structural validation; path checks work if HeCBench is also on Mac)

### Claude Code Prompt — Phase 3

```
PROJECT CONTEXT:
I'm building ParBench, a meta-benchmark for LLM parallel code translation evaluation.
Working directory: /Users/samyakjhaveri/Desktop/ParBench/parbench_sam/
Phase 1 (scaffolding) and Phase 2 (HeCBench pilot specs) are complete.

TWO-MACHINE NOTE: This runs on Mac. Path resolution checks depend on config/paths.json.
If the HeCBench repo is also present on this Mac (at the path in config/paths.json), 
file-existence checks will work. If not, use --schema-only mode for structural validation,
and full path validation will happen in Phase 5 on the Linux LC.

TASK: Enhance the validation script and create a summary report tool.

1. Update `scripts/validate_schema.py` to add these deep validation checks:

  a) PATH RESOLUTION: For each spec, load config/paths.json and resolve:
     full_path = config.downloads_root / spec.provenance.repo_root / spec.provenance.source_path / filename
     Check that every file in files.prompt_payload, files.support_files, and files.verification_only exists on disk.
     If config/paths.json doesn't exist or paths don't resolve, skip path checks and report a warning (they'll be checked on Linux in Phase 5).
     
  b) FILE CLASSIFICATION INTEGRITY:
     - No file appears in both prompt_payload and verification_only
     - No file appears in both prompt_payload and support_files (warn, don't error — some overlap might be intentional)
     - All files in the source directory are accounted for in at least one of the three lists (warn if orphan files found)
  
  c) MANIFEST-SPEC CONSISTENCY:
     - Every spec_file in manifest.jsonl points to an existing file
     - The kernel_name and parallel_api in the manifest entry match those in the linked spec
     - The source_dir in manifest matches repo_root + source_path in the spec
     - Every spec file in specs/ has a corresponding manifest entry
  
  d) CROSS-KERNEL PAIRING CHECK:
     - For each unique kernel_name, list all available APIs
     - Warn if a kernel has fewer than 2 APIs (not useful for translation)
     - Report the total number of valid translation pairs
  
  e) BUILD COMMAND SANITY:
     - Check that build.working_directory exists under repo_root
     - Check that build.outputs.executable name is non-empty
     - Warn if build.commands.build contains undefined variables (${VAR} where VAR is not in build.variables)

2. Create `scripts/generate_report.py`:
  - Reads manifest.jsonl and all specs
  - Produces a summary report (printed to stdout AND saved to reports/pilot_report.md):
    - Total kernels, total specs, total translation pairs
    - Per-kernel: which APIs available, all file classifications
    - Per-API: count of kernels
    - Validation status: all checks pass/fail
    - Table: kernel × API matrix showing which specs exist

  Example output:
  ```
  ParBench Pilot Report
  =====================
  Total kernels: 5
  Total specs: 20
  Total translation pairs: 60 (5 kernels × 12 pairs each)

  Kernel Coverage:
  | Kernel              | cuda | hip | sycl | omp | APIs | Pairs |
  |---------------------|------|-----|------|-----|------|-------|
  | nn                  |  ✓   |  ✓  |  ✓   |  ✓  |  4   |  12   |
  | scan                |  ✓   |  ✓  |  ✓   |  ✓  |  4   |  12   |
  | particle-diffusion  |  ✓   |  ✓  |  ✓   |  ✓  |  4   |  12   |
  | binomial            |  ✓   |  ✓  |  ✓   |  ✓  |  4   |  12   |
  | radixsort           |  ✓   |  ✓  |  ✓   |  ✓  |  4   |  12   |

  API Distribution:
    cuda: 5 kernels
    hip: 5 kernels
    sycl: 5 kernels
    omp: 5 kernels

  Validation: 20/20 specs pass all checks
  ```

3. Create the `reports/` directory.

4. Run both scripts and fix any issues found.

IMPORTANT NOTES:
- Path resolution uses config/paths.json: downloads_root / repo_root / source_path / filename
- If HeCBench is on this Mac, path checks will work. If not, use --schema-only mode.
- Use pathlib for all path operations.
- Python 3.10+, use type hints.
```

---

## Phase 4: Harness Skeleton — Build + Run + Verify for a Single Spec

**Goal:** Create a Python CLI that can take a spec file, build the code, run it, and verify the output. This is the foundation of the evaluation harness.

**Runs on:** Mac (writing code only; actual builds happen in Phase 5 on Linux LC)

### Claude Code Prompt — Phase 4

```
PROJECT CONTEXT:
I'm building ParBench, a meta-benchmark for LLM parallel code translation evaluation.
Working directory: /Users/samyakjhaveri/Desktop/ParBench/parbench_sam/
Phases 1-3 are complete. We have 20 validated HeCBench specs and a manifest.

TASK: Create a Python harness skeleton that can build, run, and verify a single kernel from its spec.

1. Create `harness/` directory with this structure:
```
harness/
├── __init__.py
├── cli.py              # CLI entry point
├── spec_loader.py      # Load and resolve specs
├── builder.py          # Build operations
├── runner.py           # Run operations  
├── verifier.py         # Verification operations
├── reporter.py         # Results formatting
└── models.py           # Data classes for results
```

2. `harness/models.py` — Data classes:
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Status(Enum):
    PASS = "pass"
    FAIL = "fail"  
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIP = "skip"

@dataclass
class BuildResult:
    status: Status
    duration_seconds: float
    stdout: str
    stderr: str
    executable_path: Optional[str] = None

@dataclass  
class RunResult:
    status: Status
    configuration: str  # e.g., "correctness", "performance"
    duration_seconds: float
    exit_code: int
    stdout: str
    stderr: str

@dataclass
class VerificationResult:
    status: Status
    strategy_used: str  # which strategy matched
    details: str

@dataclass
class MetricResult:
    name: str
    value: float
    unit: str

@dataclass
class SpecResult:
    spec_id: str
    build: BuildResult
    runs: dict  # config_name -> RunResult
    verification: Optional[VerificationResult] = None
    metrics: list[MetricResult] = field(default_factory=list)
```

3. `harness/spec_loader.py`:
  - load_config(project_root) -> dict: reads config/paths.json
  - load_manifest(manifest_path) -> list of manifest entries
  - load_spec(spec_path) -> dict (the full spec)
  - resolve_paths(spec, config) -> spec with all paths resolved to absolute paths
    Uses config["downloads_root"] / spec.provenance.repo_root / spec.provenance.source_path
    Resolves: all files in files.*, working_directory, executable
  - get_prompt_payload(spec, config) -> dict mapping filename to file content
    - This is what would be sent to the LLM
    - Reads each file in files.prompt_payload and returns {filename: content}
  - find_translation_pairs(manifest) -> list of (kernel_name, source_api, target_api) tuples

4. `harness/builder.py`:
  - build_spec(spec, config) -> BuildResult
  - Implementation:
    a) Resolve working_directory to absolute path using config["downloads_root"] / repo_root / working_directory
    b) Run commands.clean if it exists (ignore errors)
    c) If commands.configure exists, run it first
    d) Substitute any ${VARIABLE} in commands.build using spec.build.variables defaults
    e) Run commands.build via subprocess
    f) Check if outputs.executable exists after build
    g) Return BuildResult with status, timing, stdout/stderr
  - Use subprocess.run with timeout, capture output
  - Set environment variables from run.environment_variables if present
  - IMPORTANT: Build commands run with cwd set to the resolved working directory

5. `harness/runner.py`:
  - run_spec(spec, config, configuration="correctness") -> RunResult
  - Implementation:
    a) Look up the configuration in run.input_configurations
    b) Resolve executable path using config["downloads_root"] / repo_root / working_directory / executable
    c) Build the full command: [executable] + arguments
    d) Run via subprocess with timeout from run.timeout_seconds
    e) Capture stdout, stderr, exit code
    f) Return RunResult
  - Also: run_all_configurations(spec, config) -> dict of config_name -> RunResult

6. `harness/verifier.py`:
  - verify_run(spec, run_result) -> VerificationResult
  - Implementation — apply strategies in order, first match wins:
    a) "exit_code": check run_result.exit_code == strategy.expected
    b) "stdout_pattern": regex match against run_result.stdout
       - Use re.MULTILINE if strategy.multiline is true
    c) "numeric_comparison": parse numbers from stdout, compare with tolerance
       - This one is more complex; for now, just implement the stdout_pattern approach
       - Mark numeric_comparison as TODO
    d) "file_diff": compare output file against reference (TODO for now)
    e) "custom_script": run external script (TODO for now)
  - Return VerificationResult with which strategy matched and details

7. `harness/reporter.py`:
  - format_result(spec_result: SpecResult) -> str (human-readable summary)
  - format_json(spec_result: SpecResult) -> dict (machine-readable)
  - Print a clean summary like:
    ```
    [hecbench-nn-cuda] BUILD: PASS (2.3s) | RUN: PASS (0.5s) | VERIFY: PASS (stdout_pattern)
    ```

8. `harness/cli.py` — CLI entry point using argparse:

  Commands:
  
  a) `python -m harness.cli build <spec_file>` 
     - Loads spec, runs build, reports result
  
  b) `python -m harness.cli run <spec_file> [--config correctness|performance_small|performance_large]`
     - Loads spec, runs with specified config, reports result
  
  c) `python -m harness.cli verify <spec_file> [--config correctness]`
     - Full pipeline: build -> run -> verify, reports all results
  
  d) `python -m harness.cli prompt <spec_file>`
     - Extracts and prints the prompt_payload (what the LLM would see)
     - Prints: source API, file contents
     - Does NOT print verification_only files
  
  e) `python -m harness.cli info <spec_file>`
     - Prints spec summary without building/running
  
  f) `python -m harness.cli pairs`
     - Reads manifest, lists all valid translation pairs
  
  All commands accept:
    --config-file (default: config/paths.json) — machine-specific path config
    --manifest (default: manifest.jsonl)
    --verbose / -v

9. Create `harness/__main__.py` that imports and runs cli.main()

IMPORTANT NOTES:
- This harness must work on Ubuntu 22.04 with CUDA toolkit installed
- subprocess calls should use shell=True for build commands (they may contain pipes, &&, etc.)
- subprocess calls for run should NOT use shell=True (security, proper argument handling)
- All subprocess calls should have sensible timeouts
- Log stdout/stderr to debug output when --verbose is set
- For Phase 4, we are NOT running the actual builds — just creating the harness code. We will test it in a later phase.
- Do NOT install any compilers or CUDA toolkit — assume they are already on the system
- Use standard library only (subprocess, json, pathlib, re, argparse, dataclasses, enum, typing). No external dependencies.
- Python 3.10+, use type hints throughout
- Error handling: catch subprocess errors gracefully, never crash the harness on a single spec failure
```

---

## Execution Order

```
Phase 1  →  Phase 2  →  Phase 3  →  Phase 4
scaffold    inspect &    validate    harness
& schema    create       & report    skeleton
            specs

Time est:   ~20 min     ~30 min     ~15 min     ~30 min
```

After Phase 4, you'll have:
- 20 validated HeCBench specs (5 kernels × 4 APIs)
- A manifest with 20 entries representing 60 translation pairs
- A Python harness that can build/run/verify any spec
- Validation and reporting tools

The NEXT thing after these 4 phases would be to actually run the harness on your RTX 4070 machine against the real HeCBench code to:
1. Confirm all 20 specs build successfully
2. Collect baseline_results
3. Fix any spec errors discovered during real execution

## Phase 5: End-to-End Testing on Linux LC

See separate file: `phase5_testing_verification.md`

**Runs on:** Linux LC (Ryzen 9 + RTX 4070) via SSH from Mac

**Pre-phase setup (manual, one-time):**
1. Clone parbench git repo on Linux LC
2. `git clone https://github.com/zjin-lcf/HeCBench.git` into `downloads/`
3. Create `config/paths.json` with Linux-specific paths
4. `pip install jsonschema --user`

Phase 5 has 10 stages:
1. **Environment verification** — check what compilers are available (nvcc, hipcc, icpx, gcc)
2. **Project structure verification** — confirm all Phase 1-4 artifacts exist
3. **Structural validation** — run validate_schema.py, fix all errors
4. **Harness dry run** — test CLI commands (info, prompt, pairs) without building
5. **CUDA build test** — manually build each CUDA kernel, fix specs
6. **OpenMP build test** — manually build each OpenMP kernel, fix specs
7. **Run + verify test** — execute each built kernel, verify output, fix specs
8. **Baseline collection** — populate baseline_results in each spec
9. **Bug cleanup** — systematic re-validation of everything
10. **Final report** — comprehensive test report with matrices and metrics

```
Execution Order (all 5 phases):

Phase 1  →  Phase 2  →  Phase 3  →  Phase 4  →  Phase 5
scaffold    inspect &    validate    harness      real
& schema    create       & report    skeleton     testing
            specs

Time est:   ~20 min     ~30 min     ~15 min     ~30 min     ~60-90 min
```

After all 5 phases complete, you'll have a fully tested, validated pilot with real baseline results on your RTX 4070.
