# Session S-OCLFIX: Fix OpenCL Kernel-Only Translation Pipeline

**Date:** 2026-03-30
**Priority:** P0 — all OpenCL eval results are invalid until fixed
**Estimated effort:** 1-2 hours
**Prerequisite:** Qwen omp-to-opencl batch may still be running. Kill it or let it finish — those results will be deleted anyway.

---

## Problem Statement

Three bugs in `scripts/evaluation/llm_evaluate.py` cause 0% pass rate on ALL OpenCL-target translations, regardless of model quality. The root cause: the cross-API run/verify logic assumes "full-program translation" (correct for CUDA↔OMP where `main()` is rewritten) but X-to-OpenCL is "kernel-only translation" (only `.cl` kernel files are translated, host code is untouched).

**Discovery:** Independent investigation by 3 agent teammates (spec-checker, pipeline-auditor, root-cause) on 2026-03-30. Confirmed the same bugs independently.

**Impact:** 0/154 Qwen OpenCL results are valid. ~65% of failures are pipeline-caused. After fix, estimated true OpenCL pass rate: 5-15%.

### Bug 1: Wrong run arguments for kernel-only translations
**Location:** `_build_cross_api_run_spec()` (~line 1239-1258)
**Problem:** Sends SOURCE spec run args (CUDA/OMP positional style) to OpenCL binary, but the OpenCL host code is untouched and expects TARGET (OpenCL flag-style) args.
**Example:** `backprop` — CUDA gives `["65536"]`, OpenCL host expects `["-n", "65536"]`.
**Affected:** 11 of 20 OpenCL specs have mismatched args → guaranteed RUN_FAIL.

### Bug 2: Wrong stdout verification patterns
**Location:** `_build_cross_api_verify_spec()` (~line 1196-1236)
**Problem:** Uses SOURCE stdout patterns for verification, but OpenCL host code (untouched) prints its own patterns.
**Example:** `hotspot` — pipeline looks for `"Ending simulation"` (CUDA) but OpenCL host prints `"Total:"`.
**Affected:** 15 of 20 OpenCL specs have pattern mismatches → guaranteed VERIFY_FAIL.

### Bug 3: Dead code — `expected_pattern` vs `pattern` key mismatch
**Location:** Same verify function, lines ~1224-1225 AND ~1229
**Problem:** Reads `s.get("expected_pattern")` but specs use key `"pattern"` (confirmed in `harness/verifier.py:171`). Combined-pattern logic is dead code. Output dict on line ~1229 also writes `"expected_pattern"` but verifier reads `"pattern"`.
**Impact:** The "combine source+target patterns" feature never fires. Falls back to using source strategies directly.

---

## CRITICAL SAFETY CONSTRAINT

**CUDA↔OMP results MUST NOT change.** The fix is ADDITIVE — it adds a kernel-only branch that returns early. The existing full-program path (CUDA↔OMP) must remain identical. Verify this by:
1. Running 5 diverse baseline specs through `harness verify` before and after
2. Confirming `_is_kernel_only_translation()` returns `False` for ALL non-OpenCL target specs
3. The existing code path is completely unchanged when the predicate is False

---

## Agent Team Specification

Use `/agent-team` to create the team, or create manually following these specs:

### Team: oclfix

```
## MANDATORY DIRECTIVES
- Samyak is the PRIMARY DECISION MAKER — all decisions go through him via team lead.
- Use ultrathink for ALL analysis and implementation.
- Be conservative with context — delegate bulk reads to subagents.
- Cross-reference facts against 2+ sources before stating them.
- Plan first, get approval, then implement.
- Be honest, transparent. Tell Samyak where he might be wrong.
- The SC26 paper uses ONLY 2 models: Qwen 3.5 397B and Gemini 2.5 Flash.
  Do NOT reference claude-sonnet, gemini-flash-lite, groq-llama, or azure-gpt.
```

| Teammate | Role | Agent Type | Scope |
|----------|------|-----------|-------|
| **planner** | Verify bugs exist in current code, confirm line numbers, produce implementation plan | Explore (read-only) | Read `llm_evaluate.py`, `harness/verifier.py`, 5 OpenCL specs, 5 CUDA/OMP specs |
| **pipeline-dev** | Implement all 3 bug fixes in `llm_evaluate.py` | general-purpose | Edits `scripts/evaluation/llm_evaluate.py` ONLY |
| **test-writer** | Write unit tests + run them | general-purpose | Creates test file in `/tmp/`, runs pytest |
| **regression-checker** | Verify CUDA↔OMP results unaffected, run baseline specs | general-purpose | Runs `harness verify` on 5+ specs |
| **critic** | Adversarial review of all changes, then `/validate` | general-purpose | Read-only review + validation |

### Task Dependency Graph
```
1. planner verifies bugs + confirms fix locations → Samyak approves plan
2. pipeline-dev implements fix (BLOCKED on plan approval)
3. test-writer writes + runs tests (BLOCKED on implementation)
4. regression-checker verifies no regressions (PARALLEL with test-writer)
5. critic reviews everything (BLOCKED on test-writer + regression-checker)
6. /validate → commit
```

---

## The Fix: Kernel-Only Translation Detection

### Architecture

**Core idea:** Add a predicate `_is_kernel_only_translation()` that checks if all `translation_targets` end in `.cl`. When True, both `_build_cross_api_run_spec()` and `_build_cross_api_verify_spec()` return the TARGET spec unchanged (because the host code is untouched).

**File:** `scripts/evaluation/llm_evaluate.py` (ONE file, ~30 lines changed)

### Implementation

**Step 0: Add helper predicate** (place near other cross-API helpers, around line ~1193):

```python
def _is_kernel_only_translation(target_spec: dict) -> bool:
    """Check if this is a kernel-only translation (e.g., OpenCL .cl files).

    For kernel-only translations, the host code is untouched — only compute
    kernel files are translated. This means the translated binary uses the
    TARGET's argc parsing and stdout format, not the SOURCE's.

    Currently this applies to OpenCL targets where translation_targets are
    all .cl files. CUDA (.cu) and OMP (.c/.cpp) targets contain host code
    and are full-program translations.
    """
    targets = target_spec.get("files", {}).get("translation_targets", [])
    if not targets:
        return False
    return all(t.endswith(".cl") for t in targets)
```

**Step 1: Fix `_build_cross_api_run_spec()`** (~line 1239):

Add kernel-only early return at the top of the function:

```python
def _build_cross_api_run_spec(target_spec: dict, source_spec: dict) -> dict:
    """Build run spec for cross-API translation.

    For full-program translations (e.g., CUDA→OMP), LLMs preserve the SOURCE
    code's argc/argv parsing. Use source run args.

    For kernel-only translations (e.g., X→OpenCL .cl files), the host binary
    is untouched and expects its own (target) run args. Use target unchanged.
    """
    import copy

    # Kernel-only: host code untouched, use target's run args
    if _is_kernel_only_translation(target_spec):
        return copy.deepcopy(target_spec)

    # Full-program: LLM rewrites host code, use source's run args
    # ... (existing code unchanged) ...
```

**Step 2: Fix `_build_cross_api_verify_spec()`** (~line 1196):

Add kernel-only early return AND fix the `expected_pattern` → `pattern` key:

```python
def _build_cross_api_verify_spec(target_spec: dict, source_spec: dict) -> dict:
    """Build verification spec for cross-API translation.

    For full-program translations, LLM output matches SOURCE patterns.
    Combine source + target patterns with source first.

    For kernel-only translations, host code is untouched — stdout matches
    TARGET patterns. Return target spec unchanged.
    """
    import copy

    # Kernel-only: host code untouched, stdout matches target patterns
    if _is_kernel_only_translation(target_spec):
        return copy.deepcopy(target_spec)

    # Full-program: combine source + target stdout patterns
    verify_spec = copy.deepcopy(target_spec)

    source_verification = source_spec.get("verification") or {}
    source_strategies = source_verification.get("strategies", [])
    target_verification = verify_spec.get("verification") or {}
    target_strategies = target_verification.get("strategies", [])

    source_stdout = [s for s in source_strategies if s.get("type") == "stdout_pattern"]

    if source_stdout:
        target_stdout = [s for s in target_strategies if s.get("type") == "stdout_pattern"]
        non_stdout = [s for s in target_strategies if s.get("type") != "stdout_pattern"]

        # BUG FIX: was "expected_pattern", specs use "pattern"
        source_patterns = [s.get("pattern", "") for s in source_stdout if s.get("pattern")]
        target_patterns = [s.get("pattern", "") for s in target_stdout if s.get("pattern")]

        all_patterns = source_patterns + [p for p in target_patterns if p not in source_patterns]

        if all_patterns:
            combined_pattern = "|".join(f"(?:{p})" for p in all_patterns)
            # BUG FIX: was "expected_pattern", verifier reads "pattern"
            combined_stdout = [{"type": "stdout_pattern", "pattern": combined_pattern}]
            verify_spec["verification"] = verify_spec.get("verification") or {}
            verify_spec["verification"]["strategies"] = combined_stdout + non_stdout
        else:
            verify_spec["verification"] = verify_spec.get("verification") or {}
            verify_spec["verification"]["strategies"] = source_stdout + non_stdout

    return verify_spec
```

**Step 3: Update logging in `evaluate_translation()`:**

Where the cross-API run spec is built (~line 1611):
```python
if source_api != target_api:
    cross_run = _build_cross_api_run_spec(target_spec_resolved, source_spec)
    if verbose:
        mode = "kernel-only (target args)" if _is_kernel_only_translation(target_spec) else "full-program (source args)"
        logger.info("Cross-API (%s→%s): %s", source_api, target_api, mode)
```

Similarly for the verify section (~line 1646):
```python
if source_api != target_api:
    verify_spec = _build_cross_api_verify_spec(target_spec_resolved, source_spec)
    if verbose:
        mode = "kernel-only (target patterns)" if _is_kernel_only_translation(target_spec) else "full-program (combined patterns)"
        logger.info("Cross-API verify (%s→%s): %s", source_api, target_api, mode)
```

**Step 4: Add `translation_type` to result JSON** (in result dict construction):
```python
"translation_type": "kernel_only" if _is_kernel_only_translation(target_spec) else "full_program",
```

---

## Edge Cases (planner MUST verify these)

| Edge Case | Expected Behavior | Why |
|-----------|-------------------|-----|
| CUDA→OMP | `_is_kernel_only_translation()` = False | OMP targets are `.c`/`.cpp`, not `.cl` |
| OMP→CUDA | False | CUDA targets are `.cu` |
| CUDA→OpenCL | **True** | All OpenCL targets are `.cl` |
| OMP→OpenCL | **True** | Same |
| OpenCL→CUDA | False | CUDA targets are `.cu` — LLM rewrites full host |
| OpenCL→OMP | False | OMP targets are `.c`/`.cpp` — LLM rewrites full host |
| Same-API (augmentation) | Never called | `source_api == target_api` branch skips cross-API functions |
| XSBench OpenCL | **True** | `translation_targets: ["kernel.cl"]` |
| Empty `translation_targets` | False | Safety check in predicate |
| Mixed .c + .cl targets | False | `all()` returns False if any non-.cl file |

---

## Test Plan

### Unit Tests (test-writer creates in `/tmp/test_oclfix.py`):

```python
import sys, copy
sys.path.insert(0, '/home/samyak/Desktop/parbench_sam')

from scripts.evaluation.llm_evaluate import (
    _is_kernel_only_translation,
    _build_cross_api_run_spec,
    _build_cross_api_verify_spec,
)

def test_kernel_only_opencl():
    """OpenCL specs with .cl targets are kernel-only."""
    spec = {"files": {"translation_targets": ["kernel.cl"]}}
    assert _is_kernel_only_translation(spec) is True

def test_kernel_only_multiple_cl():
    """Multiple .cl files are still kernel-only."""
    spec = {"files": {"translation_targets": ["kernel1.cl", "kernel2.cl"]}}
    assert _is_kernel_only_translation(spec) is True

def test_full_program_cuda():
    """CUDA .cu targets are full-program."""
    spec = {"files": {"translation_targets": ["main.cu"]}}
    assert _is_kernel_only_translation(spec) is False

def test_full_program_omp():
    """OMP .c targets are full-program."""
    spec = {"files": {"translation_targets": ["main.c"]}}
    assert _is_kernel_only_translation(spec) is False

def test_mixed_targets():
    """Mixed .c + .cl targets are full-program (conservative)."""
    spec = {"files": {"translation_targets": ["host.c", "kernel.cl"]}}
    assert _is_kernel_only_translation(spec) is False

def test_empty_targets():
    """Empty targets returns False."""
    assert _is_kernel_only_translation({"files": {"translation_targets": []}}) is False
    assert _is_kernel_only_translation({"files": {}}) is False
    assert _is_kernel_only_translation({}) is False

def test_run_spec_kernel_only_uses_target_args():
    """Kernel-only translations use TARGET run args."""
    target = {
        "files": {"translation_targets": ["kernel.cl"]},
        "run": {"input_configurations": {"correctness": {"arguments": ["-n", "65536"]}}}
    }
    source = {
        "run": {"input_configurations": {"correctness": {"arguments": ["65536"]}}}
    }
    result = _build_cross_api_run_spec(target, source)
    args = result["run"]["input_configurations"]["correctness"]["arguments"]
    assert args == ["-n", "65536"], f"Expected target args, got {args}"

def test_run_spec_full_program_uses_source_args():
    """Full-program translations use SOURCE run args."""
    target = {
        "files": {"translation_targets": ["main.c"]},
        "run": {"input_configurations": {"correctness": {"arguments": ["target_arg"]}}}
    }
    source = {
        "run": {"input_configurations": {"correctness": {"arguments": ["source_arg"]}}}
    }
    result = _build_cross_api_run_spec(target, source)
    args = result["run"]["input_configurations"]["correctness"]["arguments"]
    assert args == ["source_arg"], f"Expected source args, got {args}"

def test_verify_spec_kernel_only_uses_target_patterns():
    """Kernel-only translations use TARGET verify patterns."""
    target = {
        "files": {"translation_targets": ["kernel.cl"]},
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "Total:"},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    source = {
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "Ending simulation"},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    result = _build_cross_api_verify_spec(target, source)
    stdout = [s for s in result["verification"]["strategies"] if s["type"] == "stdout_pattern"]
    assert stdout[0]["pattern"] == "Total:", f"Expected target pattern, got {stdout[0]}"

def test_verify_spec_full_program_combines_patterns():
    """Full-program translations combine source+target patterns."""
    target = {
        "files": {"translation_targets": ["main.c"]},
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "total time"},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    source = {
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "Distance="},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    result = _build_cross_api_verify_spec(target, source)
    stdout = [s for s in result["verification"]["strategies"] if s["type"] == "stdout_pattern"]
    # Combined pattern should have source first, then target
    assert "Distance=" in stdout[0]["pattern"]
    assert "total time" in stdout[0]["pattern"]
    # Must use "pattern" key, not "expected_pattern"
    assert "expected_pattern" not in stdout[0]

def test_verify_spec_pattern_key_not_expected_pattern():
    """Output must use 'pattern' key, not 'expected_pattern' (Bug 3 fix)."""
    target = {
        "files": {"translation_targets": ["main.c"]},
        "verification": {
            "strategies": [{"type": "stdout_pattern", "pattern": "target_pat"}]
        }
    }
    source = {
        "verification": {
            "strategies": [{"type": "stdout_pattern", "pattern": "source_pat"}]
        }
    }
    result = _build_cross_api_verify_spec(target, source)
    stdout = [s for s in result["verification"]["strategies"] if s["type"] == "stdout_pattern"]
    for s in stdout:
        assert "pattern" in s, "Must use 'pattern' key"
        assert "expected_pattern" not in s, "Must NOT use 'expected_pattern' key"

def test_deepcopy_no_mutation():
    """Original specs must not be mutated."""
    target = {
        "files": {"translation_targets": ["kernel.cl"]},
        "run": {"input_configurations": {"correctness": {"arguments": ["-n", "1"]}}},
        "verification": {"strategies": [{"type": "stdout_pattern", "pattern": "ok"}]}
    }
    source = {
        "run": {"input_configurations": {"correctness": {"arguments": ["1"]}}},
        "verification": {"strategies": [{"type": "stdout_pattern", "pattern": "done"}]}
    }
    original_target = copy.deepcopy(target)
    _build_cross_api_run_spec(target, source)
    _build_cross_api_verify_spec(target, source)
    assert target == original_target, "Target spec was mutated!"

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests passed!")
```

### Regression Checks (regression-checker runs):

```bash
source env_parbench/bin/activate

# 1. Verify 5 diverse baseline specs still pass harness verify (same-API, untouched path)
for spec in rodinia-bfs-cuda rodinia-hotspot-omp rodinia-nn-opencl xsbench-xsbench-cuda rodinia-heartwall-opencl; do
    echo "=== $spec ==="
    python3 -m harness -v verify specs/${spec}.json
done

# 2. Verify predicate returns False for non-OpenCL targets
python3 -c "
import json, glob
for f in sorted(glob.glob('specs/rodinia-*-cuda.json'))[:5]:
    spec = json.load(open(f))
    targets = spec.get('files', {}).get('translation_targets', [])
    is_cl = all(t.endswith('.cl') for t in targets) if targets else False
    print(f'{f}: targets={targets}, kernel_only={is_cl}')
for f in sorted(glob.glob('specs/rodinia-*-opencl.json'))[:5]:
    spec = json.load(open(f))
    targets = spec.get('files', {}).get('translation_targets', [])
    is_cl = all(t.endswith('.cl') for t in targets) if targets else False
    print(f'{f}: targets={targets}, kernel_only={is_cl}')
"

# 3. Verify ALL CUDA specs → kernel_only=False, ALL OpenCL specs → kernel_only=True
python3 -c "
import json, glob
cuda_ok = omp_ok = ocl_ok = 0
for f in glob.glob('specs/rodinia-*-cuda.json'):
    spec = json.load(open(f))
    t = spec.get('files', {}).get('translation_targets', [])
    if not (t and all(x.endswith('.cl') for x in t)):
        cuda_ok += 1
for f in glob.glob('specs/rodinia-*-omp.json'):
    spec = json.load(open(f))
    t = spec.get('files', {}).get('translation_targets', [])
    if not (t and all(x.endswith('.cl') for x in t)):
        omp_ok += 1
for f in glob.glob('specs/rodinia-*-opencl.json'):
    spec = json.load(open(f))
    t = spec.get('files', {}).get('translation_targets', [])
    if t and all(x.endswith('.cl') for x in t):
        ocl_ok += 1
print(f'CUDA specs: {cuda_ok} correctly identified as full-program')
print(f'OMP specs: {omp_ok} correctly identified as full-program')
print(f'OpenCL specs: {ocl_ok} correctly identified as kernel-only')
"
```

---

## Mismatch Table: OpenCL Run Args (11 broken specs)

These specs will get correct args after the fix:

| Kernel | Source (CUDA) args | Target (OpenCL) args | Current result |
|--------|--------------------|----------------------|----------------|
| backprop | `["65536"]` | `["-n","65536"]` | RUN_FAIL |
| dwt2d | `["rgb.bmp","-d","1024x1024",...]` | `["rgb.bmp","-i","../../data/dwt2d","-D","1024x1024",...]` | RUN_FAIL |
| heartwall | `["test.avi","20"]` | `["-f","test.avi","-i","input.txt","-n","20","-p","0"]` | RUN_FAIL |
| hotspot3d | `["512","8","100","power","temp","out"]` | `["-n","512","-l","8","-i","100","-f","power","temp","out","-p","0"]` | RUN_FAIL |
| hybridsort | `[]` | `["r","-p","0"]` | RUN_FAIL |
| myocyte | `["100","1","0"]` | `["-time","100","-r","../../data/myocyte"]` | RUN_FAIL |
| nn | `["filelist_4","-r","5",...]` | `["filelist.txt","-r","5",...,"-f","../../data/nn"]` | RUN_FAIL |
| nw | `["2048","10"]` | `["2048","10","./nw.cl"]` | RUN_FAIL |
| pathfinder | `["100000","100","20"]` | `["-c","100000","-r","100","-h","20"]` | RUN_FAIL |
| srad | `["512","512","0","127",...]` | `["-s","502","458","-n","2",...]` | RUN_FAIL |
| streamcluster | `["10","20",...,"1"]` | `["10","20",...,"1","-p","0"]` | RUN_FAIL |

---

## Post-Fix Actions

### 1. Delete invalid OpenCL results
```bash
# Delete ALL Qwen OpenCL-involving results (they're all invalid)
# Matches: *-to-*-opencl* and *-opencl-to-*
cd results/evaluation/together-qwen-3.5-397b-a17b/
ls *opencl* | wc -l  # should be ~154 files
rm *opencl*
cd -
```

### 2. Re-run Qwen OpenCL directions
```bash
# Re-run all 4 OpenCL-involving directions
for direction in cuda-to-opencl omp-to-opencl opencl-to-cuda opencl-to-omp; do
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction $direction \
        --models together-qwen-3.5-397b-a17b \
        --augment-levels 0 1 2 3 4 \
        --max-retries 3 --temperature 0.0 --resume -v \
        --project-root /home/samyak/Desktop/parbench_sam
done
```

### 3. Keep CUDA↔OMP results
The existing 180 CUDA↔OMP Qwen results (90 cuda-to-omp + 90 omp-to-cuda) are VALID and should NOT be deleted. The fix does not change their code path.

---

## Success Criteria

- [ ] `_is_kernel_only_translation()` implemented and returns correct values for all API types
- [ ] `_build_cross_api_run_spec()` uses target args for kernel-only, source args for full-program
- [ ] `_build_cross_api_verify_spec()` uses target patterns for kernel-only, combined for full-program
- [ ] `expected_pattern` → `pattern` key bug fixed (both read and write sides)
- [ ] All 13 unit tests pass
- [ ] 5+ baseline specs still pass `harness verify` (regression check)
- [ ] ALL CUDA and OMP target specs confirmed as `kernel_only=False`
- [ ] ALL OpenCL target specs confirmed as `kernel_only=True`
- [ ] `translation_type` field added to result JSON metadata
- [ ] `/validate` passes (all 4 waves)
- [ ] Committed with descriptive message
- [ ] 180 existing CUDA↔OMP Qwen results untouched
- [ ] Invalid OpenCL results deleted, ready for re-run

---

## Commit Message Template

```
Fix kernel-only translation pipeline for OpenCL targets

Three bugs in cross-API run/verify logic caused 0% pass rate on all
OpenCL-target translations regardless of model quality:

1. _build_cross_api_run_spec() sent source (CUDA/OMP) args to OpenCL
   binaries whose host code was untouched and expected target args.
   Fixed: detect kernel-only translations (.cl targets) and use target
   run args.

2. _build_cross_api_verify_spec() checked source stdout patterns
   against OpenCL host output that prints its own patterns. Fixed:
   use target verify patterns for kernel-only translations.

3. Dead code: pattern extraction used key "expected_pattern" but specs
   use "pattern". Combined-pattern logic never fired. Fixed key in
   both read (line ~1224) and write (line ~1229) locations.

Adds _is_kernel_only_translation() predicate and translation_type
field in result JSON for traceability. Zero impact on CUDA↔OMP
results (predicate returns False for all non-.cl targets).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
