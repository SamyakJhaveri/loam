# Session S-VERFIXV2: Direction-Aware Verification Fix

**Date:** 2026-03-29
**Priority:** P0 — blocks all evaluation campaigns
**Estimated effort:** 1-2 hours
**Prerequisite:** Qwen campaign stopped (done). Old results may exist in `results/evaluation/together-qwen-3.5-397b-a17b/` — delete before re-running.

---

## Problem Statement

54 mismatched verification directions across 16 Rodinia kernels cause incorrect VERIFY_FAIL for correct LLM translations. When translating CUDA→OMP, the pipeline verifies against the OMP spec's `stdout_pattern`, but the LLM translated from CUDA source code, so its output matches CUDA patterns — not OMP patterns.

**Example:** `nn-cuda` prints `"Distance="`. When LLM translates to OMP, the translated code also prints `"Distance="`. But the OMP spec's `stdout_pattern` is `"total time"` (from the hand-written OMP reference). The verifier looks for `"total time"`, doesn't find it, and reports VERIFY_FAIL — even though the translation is correct.

**Root cause:** Rodinia's CUDA, OMP, and OpenCL implementations print different strings. All 16 mismatched kernels have NO common pattern across APIs. The 4 clean kernels (hotspot3d, heartwall, myocyte, xsbench) have identical patterns and are unaffected.

---

## Agent Team Specification

Use `/agent-team` to create the team, or create manually following these specs:

### Team: verfix-v2

```
## MANDATORY DIRECTIVES
- Samyak is the PRIMARY DECISION MAKER — all decisions go through him via team lead.
- Use ultrathink for ALL analysis and implementation.
- Be conservative with context — delegate bulk reads to subagents.
- Cross-reference facts against 2+ sources before stating them.
- Plan first, get approval, then implement.
- Be honest, transparent. Tell Samyak where he might be wrong.
```

| Teammate | Role | Agent Type | Scope |
|----------|------|-----------|-------|
| **planner** | Verify the 54-mismatch claim against actual specs + source code; produce implementation plan | Explore (read-only) | Read specs, source code, verifier.py, llm_evaluate.py |
| **pipeline-dev** | Implement `_build_cross_api_verify_spec()` and integrate into `evaluate_translation()` | general-purpose | Edits `scripts/evaluation/llm_evaluate.py` ONLY |
| **test-writer** | Write unit test for the new function + integration test simulating cross-API verification | general-purpose | Creates test file in `/tmp/`, runs pytest |
| **pilot-runner** | Run baseline verification (58 specs) + 5-kernel Qwen pilot | general-purpose | Runs harness verify and eval batch commands |
| **critic** | Adversarial review: check no regressions, verify all 58 TRUE PASS still pass, review code quality | general-purpose | Read-only review + runs `/validate` |

### Task Dependency Graph
```
1. planner verifies claim + produces plan → Samyak approves
2. pipeline-dev implements fix (BLOCKED on plan approval)
3. test-writer writes + runs tests (BLOCKED on implementation)
4. pilot-runner runs baseline + pilot (BLOCKED on tests passing)
5. critic reviews everything (BLOCKED on pilot)
6. /validate → commit → push
7. Delete old Qwen results → relaunch campaign
```

---

## The Fix: Direction-Aware Verification

### Architecture

**File:** `scripts/evaluation/llm_evaluate.py`
**Location:** Line ~1412 in `evaluate_translation()` where `verify_run(target_spec, run_result)` is called.

**Current flow:**
```
source_spec → build prompt → LLM → extract code → build → run → verify(TARGET_spec) → result
```

**Fixed flow:**
```
source_spec → build prompt → LLM → extract code → build → run → verify(CROSS_API_spec) → result
                                                                        ↑
                                                            Uses SOURCE stdout_pattern
                                                            + TARGET exit_code
```

### Implementation

**Step 1:** Add helper function (place near other helper functions, around line 1050-1060):

```python
def _build_cross_api_verify_spec(target_spec: dict, source_spec: dict) -> dict:
    """Build verification spec for cross-API translation.

    For cross-API translations (e.g., CUDA→OMP), the LLM's translated code
    produces stdout matching the SOURCE implementation's patterns, not the
    TARGET's. This function creates a hybrid verification spec that uses:
    - SOURCE spec's stdout_pattern (matches what the LLM actually produces)
    - TARGET spec's exit_code (binary runs in the target environment)

    Same-API translations (augmentation-only) should NOT use this function —
    they use the target spec directly.
    """
    import copy
    verify_spec = copy.deepcopy(target_spec)

    source_verification = source_spec.get("verification") or {}
    source_strategies = source_verification.get("strategies", [])
    target_verification = verify_spec.get("verification") or {}
    target_strategies = target_verification.get("strategies", [])

    # Extract source's stdout_pattern strategies
    source_stdout = [s for s in source_strategies if s.get("type") == "stdout_pattern"]

    if source_stdout:
        # Keep target's non-stdout strategies (exit_code, etc.)
        non_stdout = [s for s in target_strategies if s.get("type") != "stdout_pattern"]
        # Source stdout_pattern first (more informative failure), then exit_code
        verify_spec["verification"]["strategies"] = source_stdout + non_stdout

    return verify_spec
```

**Step 2:** Modify the verification call site (line ~1412):

```python
# --- Direction-aware verification ---
# For cross-API translations, the LLM's output matches the SOURCE
# implementation's stdout patterns, not the TARGET's.
source_api = source_spec.get("parallel_api", "")
target_api = target_spec.get("parallel_api", "")

if source_api != target_api:
    verify_spec = _build_cross_api_verify_spec(target_spec, source_spec)
    if verbose:
        logger.info("Cross-API (%s→%s): using source stdout_pattern for verification",
                     source_api, target_api)
else:
    verify_spec = target_spec

verify_result = verify_run(verify_spec, run_result)
```

**Step 3:** Add to result JSON metadata for traceability:

```python
# In the result dict construction (wherever overall_result is built):
"verification_mode": "cross_api_source_pattern" if source_api != target_api else "same_api_target_pattern",
```

### Key Design Decisions

1. **Why swap stdout_pattern but keep exit_code?** The translated binary runs in the TARGET environment (compiled with OMP flags, linked against OMP runtime). Its exit code behavior depends on the target build. But its stdout content comes from the source code's print statements, which the LLM preserves.

2. **Why not modify the verifier itself?** The verifier (`harness/verifier.py`) is a general-purpose tool also used by `harness verify` CLI. Adding translation-direction awareness would couple it to the eval pipeline. Better to keep the verifier stateless and handle direction logic in the caller.

3. **Why deepcopy?** The spec dicts may be reused across retries or augmentation levels. Mutating the target_spec would corrupt subsequent attempts.

---

## Complete Mismatch Table (54 directions across 16 kernels)

For planner/critic verification — every row should be fixed by the pipeline change:

| # | Source Spec | Target Spec | Source stdout_pattern | Target stdout_pattern | In Source Code? |
|---|-------------|-------------|----------------------|----------------------|-----------------|
| 1 | nn-cuda | nn-omp | `Distance=` | `total time` | NO |
| 2 | nn-omp | nn-cuda | `total time` | `Distance=` | NO |
| 3 | nn-cuda | nn-opencl | `Distance=` | `(?i)(pass\|correct\|match\|verified)` | NO |
| 4 | nn-omp | nn-opencl | `total time` | `(?i)(pass\|correct\|match\|verified)` | NO |
| 5 | nn-opencl | nn-omp | `(?i)(pass\|correct\|match\|verified)` | `total time` | NO |
| 6 | pathfinder-cuda | pathfinder-omp | `pyramidHeight:` | `timer:` | NO |
| 7 | pathfinder-omp | pathfinder-cuda | `timer:` | `pyramidHeight:` | NO |
| 8 | pathfinder-cuda | pathfinder-opencl | `pyramidHeight:` | `Total: [\d.]+` | NO |
| 9 | pathfinder-omp | pathfinder-opencl | `timer:` | `Total: [\d.]+` | NO |
| 10 | pathfinder-opencl | pathfinder-cuda | `Total: [\d.]+` | `pyramidHeight:` | NO |
| 11 | pathfinder-opencl | pathfinder-omp | `Total: [\d.]+` | `timer:` | NO |
| 12 | streamcluster-cuda | streamcluster-omp | `time =` | `loops=` | NO |
| 13 | streamcluster-cuda | streamcluster-opencl | `time =` | `Total:` | NO |
| 14 | streamcluster-omp | streamcluster-opencl | `loops=` | `Total:` | NO |
| 15 | streamcluster-opencl | streamcluster-cuda | `Total:` | `time =` | NO |
| 16 | streamcluster-opencl | streamcluster-omp | `Total:` | `loops=` | NO |
| 17 | backprop-cuda | backprop-opencl | `Training done` | `Finish the training for one iteration` | NO |
| 18 | backprop-omp | backprop-opencl | `Training done` | `Finish the training for one iteration` | NO |
| 19 | backprop-opencl | backprop-cuda | `Finish the training for one iteration` | `Training done` | NO |
| 20 | backprop-opencl | backprop-omp | `Finish the training for one iteration` | `Training done` | NO |
| 21 | bfs-cuda | bfs-opencl | `Result stored in` | `passed` | NO |
| 22 | bfs-omp | bfs-opencl | `Result stored in` | `passed` | NO |
| 23 | bfs-opencl | bfs-cuda | `passed` | `Result stored in` | NO |
| 24 | bfs-opencl | bfs-omp | `passed` | `Result stored in` | NO |
| 25 | bptree-opencl | bptree-cuda | `Total:` | `Total time:` | NO |
| 26 | bptree-opencl | bptree-omp | `Total:` | `Total time:` | NO |
| 27 | cfd-cuda | cfd-opencl | `Saving solution\|Done\.\.\.` | `nel=\d+, nelr=\d+` | NO |
| 28 | cfd-omp | cfd-opencl | `Saving solution\|Done\.\.\.` | `nel=\d+, nelr=\d+` | NO |
| 29 | gaussian-cuda | gaussian-opencl | `Time total\|Time for CUDA` | `Total:` | NO |
| 30 | gaussian-opencl | gaussian-cuda | `Total:` | `Time total\|Time for CUDA` | NO |
| 31 | hotspot-cuda | hotspot-opencl | `Ending simulation` | `Total:` | NO |
| 32 | hotspot-omp | hotspot-opencl | `Ending simulation` | `Total:` | NO |
| 33 | hotspot-opencl | hotspot-cuda | `Total:` | `Ending simulation` | NO |
| 34 | hotspot-opencl | hotspot-omp | `Total:` | `Ending simulation` | NO |
| 35 | hybridsort-cuda | hybridsort-opencl | `(?i)(PASS\|passed\|SUCCESS\|correct)` | `Total:` | NO |
| 36 | kmeans-cuda | kmeans-omp | `(?i)(pass\|correct\|match\|verified)` | `number of Clusters` | NO |
| 37 | kmeans-omp | kmeans-cuda | `number of Clusters` | `(?i)(pass\|correct\|match\|verified)` | NO |
| 38 | kmeans-omp | kmeans-opencl | `number of Clusters` | `(?i)(PASS\|passed\|SUCCESS\|correct)` | NO |
| 39 | kmeans-opencl | kmeans-omp | `(?i)(PASS\|passed\|SUCCESS\|correct)` | `number of Clusters` | NO |
| 40 | lavamd-opencl | lavamd-cuda | `Total:` | `Total time:` | NO |
| 41 | lavamd-opencl | lavamd-omp | `Total:` | `Total time:` | NO |
| 42 | lud-cuda | lud-opencl | `Time consumed` | `Total:` | NO |
| 43 | lud-omp | lud-opencl | `Time consumed` | `Total:` | NO |
| 44 | nw-cuda | nw-omp | `Processing bottom-right matrix` | `Total time:` | NO |
| 45 | nw-cuda | nw-opencl | `Processing bottom-right matrix` | `Processing lower-right matrix\|Computation Done` | NO |
| 46 | nw-omp | nw-opencl | `Total time:` | `Processing lower-right matrix\|Computation Done` | NO |
| 47 | nw-opencl | nw-cuda | `Processing lower-right matrix\|Computation Done` | `Processing bottom-right matrix` | NO |
| 48 | nw-opencl | nw-omp | `Processing lower-right matrix\|Computation Done` | `Total time:` | NO |
| 49 | particlefilter-cuda | particlefilter-opencl | `ENTIRE PROGRAM TOOK` | `Total:` | NO |
| 50 | particlefilter-omp | particlefilter-opencl | `ENTIRE PROGRAM TOOK` | `Total:` | NO |
| 51 | srad-cuda | srad-opencl | `Computation Done` | `Iterations Progress` | NO |
| 52 | srad-omp | srad-opencl | `Computation Done` | `Iterations Progress` | NO |
| 53 | srad-opencl | srad-cuda | `Iterations Progress` | `Computation Done` | NO |
| 54 | srad-opencl | srad-omp | `Iterations Progress` | `Computation Done` | NO |

**Unaffected (identical patterns across all APIs):** hotspot3d (`Accuracy:`), heartwall (`frame progress:`), myocyte (`Time spent in different stages`), xsbench (`Verification checksum: \d+ \(Valid\)`)

---

## Verification Plan

### 1. Baseline Check (CRITICAL — must not regress)

All 58 TRUE PASS specs (54 Rodinia + 4 XSBench) must still pass `harness verify`. The pipeline change should NOT affect native verification (same-API), only cross-API eval translations.

```bash
source env_parbench/bin/activate

# Quick spot-check of 5 diverse specs:
for spec in rodinia-bfs-cuda rodinia-hotspot-omp rodinia-nn-opencl xsbench-xsbench-cuda rodinia-heartwall-opencl; do
    echo "--- $spec ---"
    python3 -m harness -v verify specs/${spec}.json
done

# Full baseline (if time permits):
# Use rodinia-verifier agent to run all 58
```

**Note:** `harness verify` runs native code (same-API), so the `source_api == target_api` path is taken. This path uses target_spec unchanged — no regression possible if the conditional is correct.

### 2. Unit Test for `_build_cross_api_verify_spec()`

```python
# /tmp/test_cross_api_verify.py
import sys
sys.path.insert(0, '/home/samyak/Desktop/parbench_sam')

def test_cross_api_swaps_stdout_pattern():
    from scripts.evaluation.llm_evaluate import _build_cross_api_verify_spec

    source = {
        "parallel_api": "cuda",
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "Distance="},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    target = {
        "parallel_api": "omp",
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "total time"},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }

    result = _build_cross_api_verify_spec(target, source)

    strategies = result["verification"]["strategies"]
    stdout_strats = [s for s in strategies if s["type"] == "stdout_pattern"]
    exit_strats = [s for s in strategies if s["type"] == "exit_code"]

    # Source's stdout_pattern should be used
    assert len(stdout_strats) == 1
    assert stdout_strats[0]["pattern"] == "Distance="

    # Target's exit_code should be preserved
    assert len(exit_strats) == 1
    assert exit_strats[0]["expected"] == 0

    # Original target_spec should be unchanged (deepcopy)
    assert target["verification"]["strategies"][0]["pattern"] == "total time"

def test_same_api_not_called():
    """Same-API translations should NOT use _build_cross_api_verify_spec."""
    # This is enforced by the caller (evaluate_translation), not the function itself.
    # The test documents the intent: same-API → use target_spec directly.
    pass

def test_missing_source_stdout_pattern():
    """If source has no stdout_pattern, keep target's strategies unchanged."""
    from scripts.evaluation.llm_evaluate import _build_cross_api_verify_spec

    source = {
        "parallel_api": "cuda",
        "verification": {
            "strategies": [
                {"type": "exit_code", "expected": 0}
            ]
        }
    }
    target = {
        "parallel_api": "omp",
        "verification": {
            "strategies": [
                {"type": "stdout_pattern", "pattern": "total time"},
                {"type": "exit_code", "expected": 0}
            ]
        }
    }

    result = _build_cross_api_verify_spec(target, source)

    # Should keep target's stdout_pattern since source has none
    strategies = result["verification"]["strategies"]
    stdout_strats = [s for s in strategies if s["type"] == "stdout_pattern"]
    assert len(stdout_strats) == 1
    assert stdout_strats[0]["pattern"] == "total time"

if __name__ == "__main__":
    test_cross_api_swaps_stdout_pattern()
    test_missing_source_stdout_pattern()
    print("All tests passed!")
```

### 3. Pilot Test (5 kernels × cuda-to-omp × L0)

```bash
# Delete any old Qwen results first
rm results/evaluation/together-qwen-3.5-397b-a17b/*.json 2>/dev/null

# Run pilot with 5 representative kernels:
# - nn, pathfinder, streamcluster: fully mismatched (all 3 APIs differ)
# - backprop: partial mismatch (CUDA/OMP match, OpenCL differs)
# - bfs: partial mismatch + known LLM paraphrasing issue
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --kernels nn pathfinder streamcluster backprop bfs \
    --direction cuda-to-omp \
    --models together-qwen-3.5-397b-a17b \
    --augment-levels 0 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam -v
```

**What to look for:**
- nn, pathfinder, streamcluster: should no longer get VERIFY_FAIL from pattern mismatch (may still fail for other reasons — BUILD_FAIL, RUN_FAIL are legitimate)
- backprop cuda→omp: CUDA/OMP patterns match, so fix shouldn't change behavior
- bfs: may still VERIFY_FAIL if LLM paraphrases the print string (that's a legitimate LLM failure, not a benchmark bug)

### 4. Full Validation

```bash
# Run /validate (all 4 waves) before committing
```

### 5. Commit + Relaunch Campaign

```bash
# Commit the fix
git add scripts/evaluation/llm_evaluate.py
git commit -m "Add direction-aware verification for cross-API translations

When translating between different parallel APIs (e.g., CUDA→OMP), the LLM's
translated code produces stdout matching the SOURCE implementation's patterns,
not the TARGET's. The verifier now uses the source spec's stdout_pattern for
cross-API translations while keeping the target spec's exit_code check.

Fixes 54 mismatched verification directions across 16 Rodinia kernels that
caused incorrect VERIFY_FAIL for algorithmically correct translations.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

git push origin main

# Delete old Qwen results and relaunch
rm results/evaluation/together-qwen-3.5-397b-a17b/*.json 2>/dev/null
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b
```

---

## Impact on Existing Results

The 3 existing model results (claude-sonnet, gemini-flash-lite, groq-llama) were run with OLD verification. Their VERIFY_FAIL counts in cross-API directions may include false negatives from pattern mismatches. Options:
1. **Re-run all 3 models** — cleanest but expensive (~3 × 790 tasks)
2. **Targeted re-verification** — re-run only VERIFY_FAIL results in cross-API directions
3. **Document as limitation** — note in paper that existing results used target-pattern verification

**Decision for Samyak:** Choose after seeing Qwen pilot results.

---

## Success Criteria

- [ ] `_build_cross_api_verify_spec()` implemented and unit-tested
- [ ] All 58 TRUE PASS baseline specs still pass native `harness verify`
- [ ] Pilot: 5 kernels show no false VERIFY_FAIL from pattern mismatch
- [ ] `verification_mode` field added to result JSON for traceability
- [ ] `/validate` passes (all 4 waves)
- [ ] Committed, pushed, Erel can use it
- [ ] Qwen campaign relaunched with fixed verification
