# Phase 5 (Revised): End-to-End Testing on Linux LC

## Prerequisites

- Phases 1-4 completed on Mac, pushed to git
- SSH access to Linux LC from Mac
- Linux LC has: NVIDIA RTX 4070, Ryzen 9 7900X, Ubuntu 22.04

## Pre-Phase: One-Time Setup on Linux LC

Before running the Phase 5 prompt in Claude Code, do these steps manually on the Linux LC (via SSH):

```bash
# 1. Clone your parbench repo
cd ~
git clone <your-parbench-repo-url> parbench
cd parbench

# 2. Download HeCBench
mkdir -p downloads
cd downloads
git clone https://github.com/zjin-lcf/HeCBench.git
# Note the exact directory name created (likely "HeCBench")
ls -d HeCBench*
cd ..

# 3. Create local paths config
mkdir -p config
cat > config/paths.json << 'EOF'
{
  "project_root": "/home/<YOUR_USERNAME>/parbench",
  "downloads_root": "/home/<YOUR_USERNAME>/parbench/downloads",
  "hecbench_root": "/home/<YOUR_USERNAME>/parbench/downloads/HeCBench"
}
EOF
# Edit the file to put in your actual username and the actual HeCBench directory name

# 4. Install Python dependency for validation
pip install jsonschema --user
```

---

## Claude Code Prompt — Phase 5

```
PROJECT CONTEXT:
I'm building ParBench, a meta-benchmark for evaluating LLM-based parallel code translation.
This is running on a LINUX workstation (NOT Mac). The development was done on Mac and synced here via git.

Machine specs:
- GPU: NVIDIA GeForce RTX 4070 (12GB VRAM, sm_89, Ada Lovelace)
- CPU: AMD Ryzen 9 7900X (12 cores / 24 threads)
- OS: Ubuntu 22.04 LTS

Project layout on this machine:
- ParBench project root: read from config/paths.json -> project_root
- Downloads (benchmark repos): read from config/paths.json -> downloads_root
- HeCBench repo: read from config/paths.json -> hecbench_root

Phases 1-4 are complete:
- Phase 1: Schema files in schema/, validation script in scripts/
- Phase 2: 20 HeCBench spec files in specs/ (5 kernels × 4 APIs), manifest.jsonl
- Phase 3: Enhanced validation script + report generator
- Phase 4: Python harness in harness/ (cli.py, builder.py, runner.py, verifier.py, etc.)

The 5 pilot kernels: nn, scan, particle-diffusion, binomial, radixsort
The 4 APIs per kernel: cuda, hip, sycl, omp

TASK: End-to-end testing and verification on real hardware. Test everything, fix everything, report everything. Do NOT assume anything works.

IMPORTANT PATH HANDLING:
- First read config/paths.json to get actual paths on this machine
- The specs were authored on Mac and may have repo_root paths that don't match this machine
- All spec repo_root values should be RELATIVE to downloads_root from config/paths.json
- If specs have absolute Mac paths (e.g., /Users/samyakjhaveri/...), they need to be fixed to relative paths
- The harness spec_loader.py must use config/paths.json to resolve paths
  If it doesn't already, add this capability now.

═══════════════════════════════════════════════════════
STAGE 1: ENVIRONMENT VERIFICATION
═══════════════════════════════════════════════════════

1a) Read and print the local paths config:
    cat config/paths.json

1b) Check every path in the config actually exists:
    For each path in config/paths.json, run: ls -d <path>
    If any path doesn't exist, STOP and report. The pre-phase setup was not completed.

1c) Check system tools and record versions:
    Run each of these and capture the output:
    - nvcc --version
    - gcc --version  
    - g++ --version
    - make --version
    - cmake --version
    - python3 --version
    - nvidia-smi (confirm GPU model and driver version)
    - hipcc --version 2>/dev/null || echo "hipcc: NOT AVAILABLE"
    - icpx --version 2>/dev/null || echo "icpx (SYCL): NOT AVAILABLE"
    - echo "OpenMP: $(echo | gcc -fopenmp -dM -E - 2>/dev/null | grep _OPENMP)"

1d) Determine which APIs we can test:
    - CUDA: available if nvcc exists
    - OpenMP: available if gcc supports -fopenmp
    - HIP: available if hipcc exists (likely NOT on this system)
    - SYCL: available if icpx exists (likely NOT on this system)

1e) Save environment report:
    Write all the above to reports/environment_check.txt

═══════════════════════════════════════════════════════
STAGE 2: FIX PATHS IN SPECS AND HARNESS
═══════════════════════════════════════════════════════

2a) Read config/paths.json and determine:
    - DOWNLOADS_ROOT = value of "downloads_root"
    - HECBENCH_ROOT = value of "hecbench_root"

2b) Find the EXACT HeCBench directory name:
    ls $DOWNLOADS_ROOT/ | grep -i hec
    Record the exact name (e.g., "HeCBench", "HeCBench-master", etc.)

2c) Check what repo_root values the specs currently use:
    grep -h '"repo_root"' specs/hecbench-*.json | sort -u
    
    These should be relative paths like "HeCBench/" or "HeCBench-master/"
    that can be resolved against DOWNLOADS_ROOT.

2d) If specs have ABSOLUTE paths or wrong relative paths:
    Fix every spec file:
    For each file in specs/hecbench-*.json:
      - repo_root should be the exact HeCBench directory name + "/" (relative to downloads_root)
      - Example: if HeCBench dir is "HeCBench", then repo_root should be "HeCBench/"
    
    Use sed or python to batch-fix if needed:
    ```python
    import json, glob
    actual_hecbench_dir = "HeCBench"  # or whatever it actually is
    for spec_path in glob.glob("specs/hecbench-*.json"):
        with open(spec_path) as f:
            spec = json.load(f)
        spec["provenance"]["repo_root"] = f"{actual_hecbench_dir}/"
        with open(spec_path, "w") as f:
            json.dump(spec, f, indent=2)
    ```

2e) Fix source_dir in manifest.jsonl to match:
    Each line's source_dir should be: "{hecbench_dir}/src/{kernel}-{api}/"

2f) Update the harness spec_loader.py to use config/paths.json:
    The resolve_paths function should:
    1. Load config/paths.json
    2. For any spec, resolve full paths as:
       full_source_path = downloads_root / repo_root / source_path
    3. For files in files.prompt_payload etc:
       full_file_path = downloads_root / repo_root / source_path / filename
    
    If spec_loader.py already handles this, verify it works.
    If not, add this capability now. It should accept project_root as a parameter
    or read config/paths.json automatically.
    
    Add a function: load_config(project_root) -> dict
    ```python
    def load_config(project_root: Path) -> dict:
        config_path = project_root / "config" / "paths.json"
        with open(config_path) as f:
            return json.load(f)
    ```

2g) Verify the 5 pilot kernel directories exist for each API:
    For each kernel in [nn, scan, particle-diffusion, binomial, radixsort]:
      For each api in [cuda, hip, sycl, omp]:
        FULL_PATH = $HECBENCH_ROOT/src/${kernel}-${api}
        ls $FULL_PATH/ 2>/dev/null && echo "EXISTS: ${kernel}-${api}" || echo "MISSING: ${kernel}-${api}"
    
    Print a matrix showing which directories exist.

2h) If ANY expected directory is MISSING:
    - Check for naming variations:
      ls $HECBENCH_ROOT/src/ | grep -i {kernel}
    - HeCBench sometimes uses different suffixes (e.g., "omp" vs "openmp")
    - If the directory genuinely doesn't exist for that kernel-API combo:
      Remove the spec from specs/ and its manifest.jsonl entry
    - If the directory exists but with a different name:
      Update source_path in the spec to match the actual directory name

═══════════════════════════════════════════════════════
STAGE 3: STRUCTURAL VALIDATION
═══════════════════════════════════════════════════════

3a) Run schema validation:
    cd <project_root>
    python3 scripts/validate_schema.py --all

3b) This time, path resolution checks should PASS because we're on the machine
    that has the actual HeCBench repo. If any path doesn't resolve:
    - Check the actual directory listing
    - Fix the spec's source_path or files lists
    - Re-run validation

3c) Iterate until ALL specs pass:
    - Fix each error
    - Re-run validation after each fix
    - Do NOT proceed until validation is fully clean

3d) Run the report generator:
    python3 scripts/generate_report.py
    Save output to reports/pilot_report.md

═══════════════════════════════════════════════════════
STAGE 4: HARNESS DRY RUN
═══════════════════════════════════════════════════════

Test each harness CLI command without building.

4a) Test info command on every spec:
    for spec in specs/hecbench-*.json; do
      echo "=== $spec ==="
      python3 -m harness.cli info "$spec"
      echo "Exit: $?"
    done
    
    Every one must succeed. Fix crashes.

4b) Test prompt command on 2 specs (one CUDA, one OpenMP):
    python3 -m harness.cli prompt specs/hecbench-nn-cuda.json
    python3 -m harness.cli prompt specs/hecbench-nn-omp.json
    
    Verify:
    - It prints actual source code from the files
    - It does NOT print verification_only file contents
    - It does NOT crash

4c) Test pairs command:
    python3 -m harness.cli pairs
    Count the output lines. Should be 5 kernels × N(N-1) pairs per kernel
    where N = number of APIs with existing specs for that kernel.

4d) Fix any Python errors. Common issues:
    - Config path not found (needs config/paths.json loading)
    - Import errors
    - Relative vs absolute path resolution

═══════════════════════════════════════════════════════
STAGE 5: MANUAL BUILD — CUDA KERNELS
═══════════════════════════════════════════════════════

5a) Read the actual Makefile for EACH CUDA kernel:
    for kernel in nn scan particle-diffusion binomial radixsort; do
      echo "=== ${kernel}-cuda Makefile ==="
      cat $HECBENCH_ROOT/src/${kernel}-cuda/Makefile 2>/dev/null || echo "NO MAKEFILE"
      echo ""
    done

    For each Makefile, note:
    - The default build target
    - How ARCH is specified (some use ARCH=, some use GPU_ARCH=, some hardcode it)
    - The output executable name
    - Any dependencies on other directories (../../common, ../include, etc.)
    - Whether it uses nvcc, g++, or a mix

5b) Attempt to build each CUDA kernel manually:
    for kernel in nn scan particle-diffusion binomial radixsort; do
      echo "=========================================="
      echo "BUILDING: ${kernel}-cuda"
      echo "=========================================="
      cd $HECBENCH_ROOT/src/${kernel}-cuda/
      make clean 2>/dev/null
      make ARCH=sm_89 2>&1
      BUILD_EXIT=$?
      echo "Exit code: $BUILD_EXIT"
      if [ $BUILD_EXIT -eq 0 ]; then
        echo "Executable:"
        ls -la main 2>/dev/null || ls -la *.out 2>/dev/null || ls -la $(grep -oP 'TARGET\s*=\s*\K\S+' Makefile 2>/dev/null) 2>/dev/null || echo "CANNOT FIND EXECUTABLE — check Makefile for target name"
      fi
      echo ""
      cd -
    done

5c) For EACH kernel, record:
    - Build status: PASS / FAIL
    - If FAIL: the full error message
    - If PASS: the exact executable name

5d) For each BUILD FAILURE, diagnose:
    - Read the error message fully
    - Common issues:
      * "ARCH not recognized" → Try: make SM=89 or check Makefile for variable name
      * Missing header → Check if there's a common/ or include/ directory needed
        ls $HECBENCH_ROOT/src/common/ or similar
      * Undefined reference → Missing library, check Makefile LDFLAGS
      * nvcc not found → Check PATH, try: export PATH=/usr/local/cuda/bin:$PATH
    - Try to fix by adjusting the make command (NOT by editing HeCBench source)
    - If the build command differs from what's in the spec, UPDATE THE SPEC

5e) For each BUILD SUCCESS:
    - Compare the actual executable name with spec.build.outputs.executable
    - Compare the actual build command with spec.build.commands.build
    - Fix any discrepancies in the spec

5f) If MORE THAN 2 of the 5 CUDA kernels fail to build:
    Find replacements:
    ```bash
    # List some simple CUDA kernels in HeCBench
    for dir in $HECBENCH_ROOT/src/*-cuda; do
      kernel=$(basename $dir | sed 's/-cuda$//')
      # Check it also has an omp variant
      if [ -d "$HECBENCH_ROOT/src/${kernel}-omp" ]; then
        # Check it has a simple Makefile (not cmake-only)
        if [ -f "$dir/Makefile" ]; then
          # Try a quick build
          cd "$dir"
          make clean 2>/dev/null
          if make ARCH=sm_89 2>/dev/null; then
            echo "BUILDS OK: $kernel (has cuda + omp)"
            make clean 2>/dev/null
          fi
          cd - > /dev/null
        fi
      fi
    done | head -20
    ```
    Pick replacements from the list above.
    Create new specs for them (follow the same pattern as existing specs).
    Update manifest.jsonl.

═══════════════════════════════════════════════════════
STAGE 6: MANUAL BUILD — OPENMP KERNELS
═══════════════════════════════════════════════════════

6a) Read the OpenMP Makefiles:
    for kernel in nn scan particle-diffusion binomial radixsort; do
      echo "=== ${kernel}-omp Makefile ==="
      cat $HECBENCH_ROOT/src/${kernel}-omp/Makefile 2>/dev/null || echo "NO MAKEFILE"
      echo ""
    done

6b) Build each OpenMP kernel:
    for kernel in nn scan particle-diffusion binomial radixsort; do
      echo "=========================================="
      echo "BUILDING: ${kernel}-omp"
      echo "=========================================="
      cd $HECBENCH_ROOT/src/${kernel}-omp/
      make clean 2>/dev/null
      make 2>&1
      BUILD_EXIT=$?
      echo "Exit code: $BUILD_EXIT"
      if [ $BUILD_EXIT -eq 0 ]; then
        echo "Executable:"
        ls -la main 2>/dev/null || ls -la *.out 2>/dev/null || echo "CANNOT FIND EXECUTABLE"
      fi
      echo ""
      cd -
    done

6c) Same process as Stage 5: diagnose failures, fix specs, find replacements if needed.

═══════════════════════════════════════════════════════
STAGE 7: RUN + VERIFY — ALL BUILDABLE KERNELS
═══════════════════════════════════════════════════════

For each kernel that built successfully (CUDA and OpenMP):

7a) First, figure out what arguments each program expects:
    For each built kernel:
      cd $HECBENCH_ROOT/src/{kernel}-{api}/
      # Try running with no arguments to see usage message
      ./{executable} 2>&1 | head -20
      # Also check the source for argv parsing
      grep -n "argc\|argv\|atoi\|atof\|strtol" main.* 2>/dev/null | head -10

7b) Run each kernel with reasonable arguments:
    For each built kernel:
      cd $HECBENCH_ROOT/src/{kernel}-{api}/
      echo "=== RUNNING: {kernel}-{api} ==="
      time ./{executable} {arguments} 2>&1
      echo "Exit code: $?"
    
    Start with the arguments from the spec's run.input_configurations.correctness
    If those don't work, try:
    - No arguments
    - Arguments from the Makefile's "run" target (grep "run:" Makefile)
    - Small numeric arguments (100, 1000)

7c) For each successful run, check verification:
    - Does it print "PASS" or "pass" or "Passed" or "PASSED"?
    - Does it print "FAIL" or "Error"?
    - What does the actual output look like?
    - Does the exit code indicate success (0)?
    
    Compare actual output with the spec's verification.strategies patterns.
    If the pattern doesn't match reality, FIX THE SPEC:
    - Update the stdout_pattern regex
    - Update expected exit code
    - Add new strategy if needed

7d) For each successful run, check performance output:
    - Does it print timing information?
    - What format? (e.g., "Time: 1.23 ms", "kernel time: 0.456 (s)")
    - Compare with spec's performance.metrics[].extraction.pattern
    - If the regex doesn't match, fix it in the spec

7e) Update input_configurations in each spec with arguments that ACTUALLY WORK:
    After testing, each spec should have:
    - correctness config with arguments that produce a PASS
    - performance config with arguments that produce timing output

7f) NOW test through the harness CLI:
    For each CUDA spec that builds:
      python3 -m harness.cli verify specs/hecbench-{kernel}-cuda.json -v 2>&1
      echo "Harness exit: $?"
    
    For each OpenMP spec that builds:
      python3 -m harness.cli verify specs/hecbench-{kernel}-omp.json -v 2>&1
      echo "Harness exit: $?"
    
    Expected harness output:
      [hecbench-nn-cuda] BUILD: PASS (2.3s) | RUN: PASS (0.5s) | VERIFY: PASS (stdout_pattern)
    
    If the harness crashes or gives wrong results:
    - Compare with the manual results from 7a-7d
    - Is it a harness bug (builder.py, runner.py, verifier.py)?
    - Or a spec data error?
    - Fix the appropriate file
    - Re-run

═══════════════════════════════════════════════════════
STAGE 8: COLLECT BASELINE RESULTS
═══════════════════════════════════════════════════════

For each spec that passed build + run + verify:

8a) Run the correctness configuration and record results:
    ```python
    # For each buildable spec, record:
    import json, time, subprocess
    # ... run the kernel, capture timing and output
    ```
    
    Or do it manually for each kernel:
    cd $HECBENCH_ROOT/src/{kernel}-{api}/
    time ./{executable} {correctness_args} 2>&1 | tee /tmp/output.txt
    # Record: exit code, wall time, first 200 chars of stdout

8b) Run the performance configuration 3 times and average:
    for i in 1 2 3; do
      echo "Run $i:"
      time ./{executable} {performance_args} 2>&1 | grep -i "time\|kernel\|elapsed\|throughput"
    done

8c) Update each spec's baseline_results section:
    ```json
    "baseline_results": {
      "reference_platform": "rtx4070-r9-7900x",
      "timestamp": "2026-02-10T...:00Z",
      "configurations": {
        "correctness": {
          "status": "pass",
          "exit_code": 0,
          "stdout_snippet": "<actual first 200 chars>",
          "wall_time_seconds": <actual>
        },
        "performance": {
          "status": "pass",
          "wall_time_seconds": <average of 3 runs>,
          "metrics": {
            "<metric_name>": <extracted value>
          }
        }
      }
    }
    ```

8d) For HIP and SYCL specs (compiler not available):
    ```json
    "baseline_results": {
      "reference_platform": "rtx4070-r9-7900x",
      "timestamp": "2026-02-10T...:00Z",
      "configurations": {
        "correctness": {
          "status": "skip",
          "exit_code": null,
          "stdout_snippet": null,
          "wall_time_seconds": null,
          "skip_reason": "hipcc/icpx not available on reference platform"
        }
      }
    }
    ```

═══════════════════════════════════════════════════════
STAGE 9: FULL RE-VALIDATION
═══════════════════════════════════════════════════════

9a) Run schema validation on everything:
    python3 scripts/validate_schema.py --all
    MUST pass with zero errors.

9b) Run the harness verify on ALL buildable specs one more time:
    for spec in specs/hecbench-*-cuda.json specs/hecbench-*-omp.json; do
      echo "=== $spec ==="
      python3 -m harness.cli verify "$spec" 2>&1
    done
    
    All must complete without Python crashes.
    Individual PASS/FAIL for build/run/verify is fine as long as it matches reality.

9c) Generate final report:
    python3 scripts/generate_report.py > reports/pilot_report.md

═══════════════════════════════════════════════════════
STAGE 10: FINAL TEST REPORT
═══════════════════════════════════════════════════════

Create reports/phase5_test_report.md with ALL of the following:

10a) ENVIRONMENT SUMMARY
    - Exact GPU model, driver version, CUDA toolkit version
    - CPU model and specs
    - OS version
    - Compiler versions (gcc, nvcc, etc.)
    - Available APIs: CUDA ✓/✗, OpenMP ✓/✗, HIP ✓/✗, SYCL ✓/✗

10b) PATH CONFIGURATION
    - Contents of config/paths.json
    - Actual HeCBench directory name and path
    - Any path fixes that were needed from the Mac-authored specs

10c) BUILD RESULTS MATRIX
    | Kernel              | CUDA   | HIP    | SYCL   | OpenMP |
    |---------------------|--------|--------|--------|--------|
    | nn                  | ?      | SKIP   | SKIP   | ?      |
    | scan                | ?      | SKIP   | SKIP   | ?      |
    | particle-diffusion  | ?      | SKIP   | SKIP   | ?      |
    | binomial            | ?      | SKIP   | SKIP   | ?      |
    | radixsort           | ?      | SKIP   | SKIP   | ?      |
    
    Replace ? with PASS, FAIL, or the actual result.

10d) RUN + VERIFICATION RESULTS MATRIX (same format)

10e) BASELINE PERFORMANCE TABLE
    | Kernel              | API  | Correctness | Wall Time (s) | Key Metric         |
    |---------------------|------|-------------|---------------|---------------------|
    | nn                  | cuda | PASS/FAIL   | X.XX          | kernel_time: X.X ms |
    | nn                  | omp  | PASS/FAIL   | X.XX          | kernel_time: X.X ms |
    | ...                 |      |             |               |                     |

10f) ISSUES FOUND AND FIXED
    For each issue:
    - What was wrong
    - Which file was affected
    - How it was fixed
    List issues in categories:
    - Path issues (Mac→Linux)
    - Spec data errors
    - Harness Python bugs
    - Build issues
    - Runtime issues

10g) REMAINING ISSUES
    - Any specs that don't work and why
    - Any harness limitations
    - Recommendations for next steps

10h) KERNEL STATUS SUMMARY
    For each of the 5 pilot kernels:
    - Final status: fully working / partially working / replaced
    - If replaced: what was it replaced with and why

10i) GIT COMMIT SUMMARY
    List all files changed during Phase 5 testing.

═══════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════

1. DO NOT ASSUME. Run every command and check its output.
2. DO NOT SKIP ERRORS. Diagnose and fix before moving on.
3. DO NOT MODIFY HeCBench source code. Only modify ParBench specs and harness code.
4. RECORD EVERYTHING in the final report.
5. If a kernel genuinely won't build, replace it.
6. All paths must work relative to config/paths.json.
7. After fixing specs, ALWAYS re-run validation.
8. Use -v (verbose) on all harness commands.
9. At the end: git add, commit, push all changes so they sync back to the Mac.
10. The HECBENCH_ROOT variable must come from config/paths.json, not be hardcoded.
```
