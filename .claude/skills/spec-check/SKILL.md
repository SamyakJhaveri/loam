---
name: spec-check
description: Single-spec health check — verify source exists, args match source argc, run harness verify, report PASS/FAIL with diagnosis. Use when a single spec is suspected broken, after editing a spec JSON, or as a quick sanity check before adding a spec to an eval batch. For bulk spec audits use spec-auditor agent.
---

# Spec Health Check

Declarative verification for a single benchmark spec. Reads the spec, checks the
source's argument parsing, runs the harness, and reports PASS/FAIL with root cause
analysis. Inspired by Osmani's principle: specify success criteria, not steps.

**Trigger:** When user types `/spec-check <spec-name>`

## Arguments

- `$ARGUMENTS` — **required**: the spec name without `.json` extension
  (e.g., `rodinia-srad-cuda`, `xsbench-omp`, `hecbench-stencil1d-cuda`)

If no argument is provided, prompt the user for a spec name.

## Prerequisites

- Project root: `{{PROJECT_ROOT}}`
- Venv: `source {{PROJECT_ROOT}}/env_parbench/bin/activate`
- Rodinia submodule must be initialized (not in a worktree)

## KNOWN_FAIL Specs (8 — early exit)

Before doing any work, check if the spec is in the KNOWN_FAIL list:

| Spec | Reason |
|------|--------|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 |
| `rodinia-mummergpu-omp` | `texture<>` + `cuMemGetInfo_v2` signature |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found |
| `rodinia-nn-opencl` | TIMEOUT / SIGSEGV |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime |
| `hecbench-stencil1d-omp_target` | BUILD_FAIL |
| `hecbench-scan-omp_target` | VERIFY_FAIL |

If the spec matches any of these, report immediately:

```
=== SPEC CHECK: <spec-name> ===
Status: KNOWN_FAIL (excluded from eval batches)
Reason: <reason from table>
No further checks performed.
```

## Workflow

### Step 1: Locate and Read the Spec

```bash
cd {{PROJECT_ROOT}}
SPEC_FILE="specs/$ARGUMENTS.json"

if [ ! -f "$SPEC_FILE" ]; then
  echo "ERROR: Spec file not found: $SPEC_FILE"
  echo "Available specs matching pattern:"
  ls specs/*${ARGUMENTS}* 2>/dev/null || echo "  (none)"
  exit 1
fi

cat "$SPEC_FILE"
```

Read the spec JSON. Extract and note:
- `name`, `api`, `suite`, `category`
- `build.commands` — how it builds
- `run.arguments` — what args are passed
- `run.working_directory` — where it runs
- `verify.stdout_pattern` — expected output pattern
- `verify.exit_code` — expected exit code
- `outputs.executable` — the binary name
- `source.directory` — where source files live

### Step 2: Verify Source Directory Exists

```bash
cd {{PROJECT_ROOT}}
SOURCE_DIR=$(python3 -c "import json; print(json.load(open('specs/$ARGUMENTS.json'))['source']['directory'])")
echo "Source directory: $SOURCE_DIR"
ls "$SOURCE_DIR" 2>/dev/null | head -5 || echo "ERROR: Source directory not found"
```

If the source directory does not exist, report BUILD_FAIL prediction and stop.

### Step 3: Check Source Argument Parsing (Run Argument Verification Protocol)

**CRITICAL: This is the most important safety check.** The spec's `run.arguments`
must match what the source code actually expects.

```bash
cd {{PROJECT_ROOT}}
SOURCE_DIR=$(python3 -c "import json; print(json.load(open('specs/$ARGUMENTS.json'))['source']['directory'])")

# Find main source files and grep for argc parsing
echo "=== ARGUMENT PARSING IN SOURCE ==="
grep -rn "argc" "$SOURCE_DIR"/*.{c,cpp,cu,cc} 2>/dev/null | head -20
grep -rn "argv" "$SOURCE_DIR"/*.{c,cpp,cu,cc} 2>/dev/null | head -10
grep -rn "getopt\|optarg\|usage()" "$SOURCE_DIR"/*.{c,cpp,cu,cc} 2>/dev/null | head -10
```

Compare the source's expected arguments with the spec's `run.arguments`. Report any mismatch.

**NEVER suggest changing spec run args based on this check alone.** If a mismatch is found,
report it as a finding but note: "Verify against baseline stdout before changing args."

### Step 4: Run the Harness

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}

python3 -m harness -v verify "specs/$ARGUMENTS.json" 2>&1
```

Capture the full output. The harness reports:
- BUILD: success/failure (with error snippet on failure)
- RUN: success/failure (with exit code and stderr on failure)
- VERIFY: PASS/FAIL (with stdout comparison on failure)

### Step 5: Report

Generate a structured report based on the harness output:

**On PASS:**
```
=== SPEC CHECK: <spec-name> ===
Status: PASS
API:    <api>
Suite:  <suite>

Build:  OK (<compiler> <flags summary>)
Run:    OK (exit code <N>, <time>s)
Verify: PASS (stdout pattern matched: "<pattern>")

Run args: <args list>
Args match source argc check: YES / NO (details)

Spec is eligible for eval batches.
```

**On BUILD_FAIL:**
```
=== SPEC CHECK: <spec-name> ===
Status: BUILD_FAIL

Build error (first 10 lines):
  <error snippet>

Root cause analysis:
  <analysis: missing header? wrong compiler flag? CUDA version issue?>

Suggested fix:
  <concrete suggestion or "needs investigation">
```

**On RUN_FAIL:**
```
=== SPEC CHECK: <spec-name> ===
Status: RUN_FAIL

Build:  OK
Run:    FAIL (exit code <N>)

Stderr (first 10 lines):
  <stderr snippet>

Root cause analysis:
  <analysis: segfault? missing input file? wrong args? timeout?>
  
Run args in spec:     <args>
Expected args (source): <what source expects>
Args match: YES / NO
```

**On VERIFY_FAIL:**
```
=== SPEC CHECK: <spec-name> ===
Status: VERIFY_FAIL

Build:  OK
Run:    OK (exit code <N>)
Verify: FAIL

Expected pattern: "<pattern>"
Actual stdout (first 10 lines):
  <stdout snippet>

Root cause analysis:
  <analysis: wrong output format? floating-point mismatch? wrong args producing wrong output?>
```

## Context Management

This skill runs synchronously in the main session. No subagents needed — it's a
single-spec check that completes in under 30 seconds.

Total output: the structured report above (~15-25 lines). Do not paste raw build
logs or full source files into the report — summarize and reference file:line.
