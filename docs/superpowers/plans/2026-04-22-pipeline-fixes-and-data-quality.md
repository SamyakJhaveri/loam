# Phase 3 Pipeline Fixes & Data Quality Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the two confirmed pipeline bugs affecting ablation data integrity, harden the batch runner retry logic, investigate the opencl→cuda prompt gap, and perform a targeted ablation rerun to patch the ~1–4 cells corrupted by the de-anonymization bug.

**Architecture:** Three independent code fixes (llm_evaluate.py de-anon, run_phase3.sh retry, KNOWN_FAIL run-time exclusion) followed by a verification rerun of the ablation using `--resume` to overwrite only the corrupted cells. The opencl→cuda prompt audit is a read-only investigation that gates a decision on a follow-up canonical run.

**Tech Stack:** Python 3.12, Bash, pytest, `source env_parbench/bin/activate`, `python3` (never bare `python`).

---

## Background & Issue Inventory

Identified by 5-agent post-ablation audit (2026-04-22). Issues ranked by data impact:

| ID | Severity | Where | What |
|----|----------|-------|------|
| BUG-1 | **Data integrity** | `llm_evaluate.py:1666` | De-anonymization maps file dict-keys but not `#include` references inside code bodies → ~1–4 L3/L4 BUILD_FAILs are pipeline-induced, not model failures |
| BUG-2 | **Operational** | `run_phase3.sh:275–285` | Retry pass hardcodes `--suite` alongside `--task-list`, triggering argparse mutual-exclusion → every ablation retry fails immediately with exit 2, masking truly transient failures |
| OPT-1 | **Cost/ops** | `run_phase3.sh:175` | KNOWN_FAIL specs are run in canonical and wasted 66 API calls (correctly excluded at analysis time, but never at run time) |
| INV-1 | **Paper claim** | opencl→cuda prompt | ~25% of opencl→cuda BUILD_FAILs are "missing main()"; unclear whether the CUDA host driver is surfaced as Infrastructure Context to the model — if absent, this is a fixable prompt issue worth a follow-up run |

**What is NOT here:** paper writing, framing/stats corrections, temperature confound discussion (those are writing-phase tasks). The `make clean` issue is already handled by `harness/builder.py:124` (`ignore_errors=True`) — it is cosmetic stderr noise, not a real bug.

---

## File Map

| File | Action | Why |
|------|--------|-----|
| `scripts/evaluation/llm_evaluate.py` | Modify line 1666 | Fix de-anonymization to also patch code body content |
| `tests/test_deanonymization_body.py` | Create | Unit test proving the fix |
| `scripts/batch/run_phase3.sh` | Modify lines 274–285 | Fix retry logic to exclude `--suite` when `--task-list` is in use |
| `tests/test_run_phase3_retry_logic.sh` | Create | Smoke test for the retry command shape |

---

## Task 1: Fix de-anonymization bug in `llm_evaluate.py`

**Files:**
- Modify: `scripts/evaluation/llm_evaluate.py:1666`
- Create: `tests/test_deanonymization_body.py`

The bug: `extracted = {anon_map[gf]: code for gf, code in anon_extracted.items()}` renames the dict key (generic → real filename) but leaves `#include "translated_1.cu"` strings inside the code body unchanged. At L3/L4, multi-file kernels that cross-include each other (e.g., `needle.cu` includes `needle_kernel.cu`) get a generic `#include "translated_1.cu"` in the written file, which fails to resolve at build time because `translated_1.cu` was never written to disk.

- [ ] **Step 1: Write the failing test**

Create `tests/test_deanonymization_body.py`:

```python
"""Test that de-anonymization patches generic filenames inside code bodies."""
from __future__ import annotations


def _deanonymize(anon_map: dict[str, str], anon_extracted: dict[str, str]) -> dict[str, str]:
    """Replicate the de-anonymization logic from llm_evaluate.py evaluate_translation()."""
    # Import the real function once it's refactored; for now mirror the current logic + fix.
    extracted = {}
    for gf, code in anon_extracted.items():
        real_name = anon_map[gf]
        for gen_fn, real_fn in anon_map.items():
            code = code.replace(f'"{gen_fn}"', f'"{real_fn}"')
            code = code.replace(f"'{gen_fn}'", f"'{real_fn}'")
        extracted[real_name] = code
    return extracted


def test_include_reference_is_patched() -> None:
    """Generic #include in code body must be replaced with the real filename."""
    anon_map = {"translated_0.cu": "needle.cu", "translated_1.cu": "needle_kernel.cu"}
    anon_extracted = {
        "translated_0.cu": '#include "translated_1.cu"\n__global__ void kernel() {}',
        "translated_1.cu": "// kernel impl",
    }
    result = _deanonymize(anon_map, anon_extracted)
    assert '#include "needle_kernel.cu"' in result["needle.cu"], (
        "Generic #include not patched in code body"
    )
    assert "translated_1.cu" not in result["needle.cu"], (
        "Generic filename still present in code body"
    )


def test_single_quoted_include_is_patched() -> None:
    anon_map = {"translated_0.c": "bfs.c", "translated_1.h": "bfs.h"}
    anon_extracted = {
        "translated_0.c": "#include 'translated_1.h'\nint main() {}",
        "translated_1.h": "// header",
    }
    result = _deanonymize(anon_map, anon_extracted)
    assert "#include 'bfs.h'" in result["bfs.c"]


def test_non_include_content_is_unchanged() -> None:
    """Code that does not reference generic names must be bit-identical after patching."""
    anon_map = {"translated_0.cu": "hotspot.cu"}
    anon_extracted = {"translated_0.cu": "__global__ void kernel(float* a) { a[0] = 1.0f; }"}
    result = _deanonymize(anon_map, anon_extracted)
    assert result["hotspot.cu"] == "__global__ void kernel(float* a) { a[0] = 1.0f; }"


def test_keys_still_de_anonymized() -> None:
    """File keys must still map to real filenames (regression guard)."""
    anon_map = {"translated_0.cpp": "srad.cpp"}
    anon_extracted = {"translated_0.cpp": "// code"}
    result = _deanonymize(anon_map, anon_extracted)
    assert "translated_0.cpp" not in result
    assert "srad.cpp" in result
```

- [ ] **Step 2: Run the test to confirm it fails** (the helper mirrors the buggy current logic)

```bash
source env_parbench/bin/activate
python3 -m pytest tests/test_deanonymization_body.py -v
```

Expected: `test_include_reference_is_patched` FAIL — `AssertionError: Generic #include not patched in code body`

- [ ] **Step 3: Refactor de-anonymization in `llm_evaluate.py` into a helper and fix it**

In `scripts/evaluation/llm_evaluate.py`, replace the single line at line 1666:

```python
# BEFORE (line 1666 — only renames keys, not code body)
extracted = {anon_map[gf]: code for gf, code in anon_extracted.items()}
```

with:

```python
# After: rename keys AND patch generic filename references inside code bodies
extracted = _deanonymize_extracted(anon_map, anon_extracted)
```

And add the helper function near the `extract_code_blocks` function (~line 1143), after the existing helpers:

```python
def _deanonymize_extracted(
    anon_map: dict[str, str], anon_extracted: dict[str, str]
) -> dict[str, str]:
    """De-anonymize extracted code: rename dict keys AND patch filenames in code bodies.

    The LLM sees generic filenames (translated_0.cu) and may emit cross-file
    #include "translated_1.cu" references. These must be replaced with real
    filenames so the code compiles correctly after extraction.
    """
    result: dict[str, str] = {}
    for generic_fname, code in anon_extracted.items():
        real_fname = anon_map[generic_fname]
        for gen_fn, real_fn in anon_map.items():
            code = code.replace(f'"{gen_fn}"', f'"{real_fn}"')
            code = code.replace(f"'{gen_fn}'", f"'{real_fn}'")
        result[real_fname] = code
    return result
```

Also update the test helper in `tests/test_deanonymization_body.py` to import the real function:

```python
# Replace the local _deanonymize helper with an import of the real one:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "evaluation"))
from llm_evaluate import _deanonymize_extracted as _deanonymize
```

(Remove the local `_deanonymize` definition after adding the import.)

- [ ] **Step 4: Run all tests — expect 4/4 PASS**

```bash
python3 -m pytest tests/test_deanonymization_body.py -v
```

Expected output:
```
tests/test_deanonymization_body.py::test_include_reference_is_patched PASSED
tests/test_deanonymization_body.py::test_single_quoted_include_is_patched PASSED
tests/test_deanonymization_body.py::test_non_include_content_is_unchanged PASSED
tests/test_deanonymization_body.py::test_keys_still_de_anonymized PASSED
4 passed in 0.XXs
```

- [ ] **Step 5: Run the full test suite to check for regressions**

```bash
python3 -m pytest tests/ -v --tb=short -q 2>&1 | tail -20
```

Expected: all existing tests pass. If `test_deanonymization_body.py` import path fails, adjust `sys.path.insert` to the actual module path.

- [ ] **Step 6: Commit**

```bash
git add scripts/evaluation/llm_evaluate.py tests/test_deanonymization_body.py
git commit -m "fix(eval): patch generic filenames in code bodies during de-anonymization

When LLMs produce multi-file translations at L3/L4, cross-file #include
references use the anonymized generic names (translated_1.cu). The
de-anonymization step previously renamed dict keys but left these
references inside code bodies unchanged, causing BUILD_FAIL when the
real filename was written to disk but the include still asked for
translated_1.cu.

Refactors the de-anonymization into _deanonymize_extracted() helper
that replaces both dict keys and quoted filename occurrences in code bodies.
Affects ~1-4 L3/L4 result cells; a --resume rerun of ablation L3/L4 will
overwrite those cells with clean results.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Fix ablation retry logic in `run_phase3.sh`

**Files:**
- Modify: `scripts/batch/run_phase3.sh:274–285`

The bug: the `RETRY` array is constructed with `--suite "$SUITE"` unconditionally, then `TASK_LIST_ARGS` (containing `--task-list ...`) is appended when in ablation phase. `run_eval_batch.py` enforces mutual exclusion between `--suite`/`--kernels` and `--task-list` at runtime (line 616), so every ablation retry immediately exits 2. Transient failures cannot be recovered.

- [ ] **Step 1: Read the current retry block to understand context**

```bash
sed -n '265,295p' scripts/batch/run_phase3.sh
```

Expected: the block starting with `if [[ ${#FAILED_BATCHES[@]} -gt 0 ]]; then`.

- [ ] **Step 2: Apply the fix**

Replace lines 274–286 in `scripts/batch/run_phase3.sh`. The current block:

```bash
        RETRY=(python3 scripts/evaluation/run_eval_batch.py
            --suite "$SUITE" --direction "$DIR"
            --models "$MODEL"
            --augment-levels $AUGMENT_LEVELS
            --temperature $TEMPERATURE
            --num-samples $NUM_SAMPLES
            --max-retries $MAX_RETRIES
            --thinking on
            --resume -v
            --project-root "$PROJECT_ROOT")
        [[ ${#TASK_LIST_ARGS[@]} -gt 0 ]] && RETRY+=("${TASK_LIST_ARGS[@]}")
        [[ ${#KERNEL_ARGS[@]} -gt 0 ]] && RETRY+=(--kernels "${KERNEL_ARGS[@]}")
```

Replace with:

```bash
        if [[ ${#TASK_LIST_ARGS[@]} -gt 0 ]]; then
            # Ablation phase: --task-list is mutually exclusive with --suite/--kernels
            RETRY=(python3 scripts/evaluation/run_eval_batch.py
                --direction "$DIR"
                --models "$MODEL"
                --augment-levels $AUGMENT_LEVELS
                --temperature $TEMPERATURE
                --num-samples $NUM_SAMPLES
                --max-retries $MAX_RETRIES
                --thinking on
                --resume -v
                --project-root "$PROJECT_ROOT"
                "${TASK_LIST_ARGS[@]}")
        else
            # Canonical phase: --suite is required, no --task-list
            RETRY=(python3 scripts/evaluation/run_eval_batch.py
                --suite "$SUITE" --direction "$DIR"
                --models "$MODEL"
                --augment-levels $AUGMENT_LEVELS
                --temperature $TEMPERATURE
                --num-samples $NUM_SAMPLES
                --max-retries $MAX_RETRIES
                --thinking on
                --resume -v
                --project-root "$PROJECT_ROOT")
            [[ ${#KERNEL_ARGS[@]} -gt 0 ]] && RETRY+=(--kernels "${KERNEL_ARGS[@]}")
        fi
```

- [ ] **Step 3: Verify the fix visually**

```bash
sed -n '265,305p' scripts/batch/run_phase3.sh
```

Confirm the ablation branch has no `--suite "$SUITE"` and has `"${TASK_LIST_ARGS[@]}"`, and the canonical branch has `--suite "$SUITE"` and no `TASK_LIST_ARGS`.

- [ ] **Step 4: Dry-run syntax check**

```bash
bash -n scripts/batch/run_phase3.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/batch/run_phase3.sh
git commit -m "fix(batch): ablation retry must not include --suite alongside --task-list

run_eval_batch.py enforces mutual exclusion between --suite/--kernels and
--task-list. The retry pass was unconditionally building the command with
--suite, then conditionally appending --task-list, causing every ablation
retry to fail with argparse exit 2. Transient API failures in ablation
batches could never be recovered.

Fix: branch the RETRY command construction on whether TASK_LIST_ARGS is
set. Ablation retries use --task-list only; canonical retries use --suite.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Add KNOWN_FAIL run-time exclusion to canonical phase (cost optimization)

**Files:**
- Modify: `scripts/batch/run_phase3.sh` (canonical batch invocations)

Currently KNOWN_FAIL specs (8 total) are run in the canonical phase, wasting 66 API calls, and excluded only at analysis time. This task adds `--excluded-specs` (or equivalent) filtering at run time. **Note:** This only matters for future re-runs — the existing Qwen canonical data is already correct (66 records excluded in analysis).

First, check if `run_eval_batch.py` already supports exclusion:

- [ ] **Step 1: Check for existing exclusion support**

```bash
grep -n "excluded\|EXCLUDED\|known.fail\|KNOWN_FAIL" scripts/evaluation/run_eval_batch.py | head -20
```

- [ ] **Step 2a: If `--excluded-specs` flag already exists** — add it to the canonical batches in `run_phase3.sh`. Find the `run_batch` function definition and append `--excluded-specs` with the 8 spec IDs.

- [ ] **Step 2b: If the flag does NOT exist** — add it to `run_eval_batch.py` as an optional list argument and wire it into `_build_tasks()` to skip pairs where source or target is in the excluded set:

```python
# In run_eval_batch.py argparse section:
parser.add_argument(
    "--excluded-specs",
    nargs="*",
    default=[],
    metavar="SPEC_ID",
    help="Spec IDs to exclude as source or target (e.g. KNOWN_FAIL specs)",
)
```

And in `_build_tasks()` (or equivalent task-builder function), add after building the pairs list:

```python
if args.excluded_specs:
    excluded = set(args.excluded_specs)
    pairs = [(src, tgt) for src, tgt in pairs
             if src not in excluded and tgt not in excluded]
```

- [ ] **Step 3: Add exclusion to the canonical phase in `run_phase3.sh`**

After the `KNOWN_FAIL_SPECS` variable is defined (or define it at the top of the config block after line 146), add it to the canonical `run_batch` invocations. The 8 KNOWN_FAIL spec IDs are:

```bash
KNOWN_FAIL_SPECS=(
    rodinia-kmeans-cuda
    rodinia-mummergpu-cuda
    rodinia-mummergpu-omp
    rodinia-hybridsort-cuda
    rodinia-nn-opencl
    rodinia-kmeans-opencl
    hecbench-stencil1d-omp_target
    hecbench-scan-omp_target
)
```

Pass `--excluded-specs "${KNOWN_FAIL_SPECS[@]}"` to each batch invocation in the canonical phase.

- [ ] **Step 4: Write a test for the exclusion flag**

```bash
source env_parbench/bin/activate
# dry-run a batch with --excluded-specs and verify KNOWN_FAIL pairs are absent
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction cuda-to-omp \
    --models together-qwen-3.5-397b-a17b \
    --excluded-specs rodinia-kmeans-cuda rodinia-mummergpu-cuda \
    --dry-run \
    --project-root /home/samyak/Desktop/parbench_sam 2>&1 | grep -E "kmeans|mummergpu|Task"
```

Expected: No output lines containing `kmeans` or `mummergpu`.

- [ ] **Step 5: Commit**

```bash
git add scripts/evaluation/run_eval_batch.py scripts/batch/run_phase3.sh
git commit -m "feat(batch): add --excluded-specs flag to run_eval_batch.py; apply to canonical phase

KNOWN_FAIL specs (8 total) were previously run in canonical and wasted 66
API calls before being excluded at analysis time. --excluded-specs filters
them at task-build time. Canonical phase in run_phase3.sh now passes the
full KNOWN_FAIL list via KNOWN_FAIL_SPECS array.

No effect on existing Qwen data (already correctly excluded in analysis).
Saves 66 x 3-sample canonical calls on future model runs (~200 API calls
at 3 samples each).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Investigate opencl→cuda prompt gap (read-only)

**Files:** Read-only. No edits unless confirmed gap found.

The opencl→cuda direction has 0/60 PASS. ~25% of failures are "missing main()" — the model generates kernel-only CUDA without a host driver. This could be a model limitation OR a prompt gap (CUDA host driver not included as Infrastructure Context).

Per `evaluation.md`: "## Target Infrastructure Context (DO NOT MODIFY)" section is added to the prompt when `targets != prompt_payload`. For CUDA targets, `translation_targets = prompt_payload` (Family 3), so by design there is NO Infrastructure Context section — the model must produce everything.

- [ ] **Step 1: Confirm translation_targets for a CUDA target spec**

```bash
source env_parbench/bin/activate
python3 -c "
import json
spec = json.load(open('specs/rodinia-bfs-cuda.json'))
print('translation_targets:', spec['files']['translation_targets'])
print('prompt_payload:', spec['files'].get('prompt_payload', 'N/A'))
"
```

- [ ] **Step 2: Inspect the actual prompt for an opencl→cuda pair**

```bash
python3 -m harness prompt \
    --source specs/rodinia-bfs-opencl.json \
    --target specs/rodinia-bfs-cuda.json \
    --project-root /home/samyak/Desktop/parbench_sam 2>&1 | head -80
```

Check: Does the prompt include the CUDA host driver (`bfs.cu` or `main.cu`) as readable context? Or does the LLM see only the OpenCL source files?

- [ ] **Step 3: Check a result JSON to confirm the gap**

```bash
source env_parbench/bin/activate
python3 -c "
import json, glob
files = glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*opencl*cuda*.json')
for f in files[:3]:
    r = json.load(open(f))
    if r.get('overall_status') == 'BUILD_FAIL':
        print('---', f)
        for att in r.get('attempts', []):
            snippet = att.get('build_error_snippet', '')
            if 'main' in snippet.lower():
                print(snippet[:300])
                break
"
```

- [ ] **Step 4: Decision gate**

**If** the prompt does NOT include the CUDA host driver as context, AND the BUILD_FAILs are consistently "missing main()" → this is a fixable prompt issue. In that case, add a task to pipe the CUDA target's full prompt_payload as Infrastructure Context (read-only reference) and run a 5-kernel spot check (`--kernels bfs nw srad backprop hotspot --suite rodinia --direction opencl-to-cuda --num-samples 1`).

**If** the prompt DOES include the CUDA host driver as context → this is a model capability limitation. No pipeline fix needed; document the finding.

- [ ] **Step 5: Write findings to `docs/analysis/opencl_to_cuda_prompt_audit.md`**

Record: what the prompt contains, whether host context is present, what the model generated (with error snippet), and the recommendation (fix or defer).

---

## Task 5: Targeted ablation rerun to fix BUG-1 corrupted cells

**Context:** Task 1 (de-anonymization fix) must be completed and committed before this task. With the fix in place, a `--resume` rerun of L3 and L4 ablation batches will skip already-correct results and only rerun the ~1–4 cells where the generic-filename BUILD_FAIL occurred.

L3 and L4 are the only levels using anonymization in multi-file kernels. The fix is safe to apply with `--resume` because:
- `--resume` checks for the existence of the per-task JSON file and skips if present
- For the ~1–4 corrupted cells: the existing JSON will be **overwritten** because `--resume` is based on file presence, not correctness
  
Wait — actually `--resume` **skips** if the file exists. This means the corrupted BUIlD_FAIL results will NOT be overwritten. We must **delete the affected files** first, then rerun.

- [ ] **Step 1: Identify the corrupted files**

The corrupted files are L3/L4 ablation results that are BUILD_FAIL AND involve multi-file kernels with cross-includes. The confirmed case is `rodinia-nw-omp-to-cuda-L4`. Search for others:

```bash
source env_parbench/bin/activate
python3 -c "
import json, glob

# Multi-file kernels known to have cross-includes: nw, heartwall, myocyte, bptree
MULTI_CROSS = ['nw', 'heartwall', 'myocyte']

results_dir = 'results/evaluation/together-qwen-3.5-397b-a17b'
for f in sorted(glob.glob(f'{results_dir}/*-L3.json') + glob.glob(f'{results_dir}/*-L4.json')):
    r = json.load(open(f))
    kernel = r.get('source_spec', '')
    if r.get('overall_status') == 'BUILD_FAIL':
        for mc in MULTI_CROSS:
            if mc in kernel:
                snippet = ''
                for att in r.get('attempts', []):
                    snippet = att.get('build_error_snippet', '')
                # Look for 'translated_' in stderr (the unpatched generic filename)
                if 'translated_' in snippet:
                    print('CORRUPTED:', f)
                    print('  Error snippet:', snippet[:200])
"
```

- [ ] **Step 2: Delete only the confirmed corrupted files**

For each file identified in Step 1 (confirm by reading the snippet — only delete if `translated_N.ext` appears in the build error):

```bash
# Example — replace with actual file paths from Step 1
rm results/evaluation/together-qwen-3.5-397b-a17b/rodinia-nw-omp-to-rodinia-nw-cuda-L4.json
# Repeat for each confirmed corrupted file
```

Do NOT use wildcards. Delete only files explicitly listed from Step 1.

- [ ] **Step 3: Rerun only L3 and L4 ablation using --task-list and --resume**

```bash
source env_parbench/bin/activate
python3 scripts/evaluation/run_eval_batch.py \
    --task-list .planning/eval-selections/l0_passers_together_qwen_3_5_397b_a17b.json \
    --direction all \
    --models together-qwen-3.5-397b-a17b \
    --augment-levels 3 4 \
    --temperature 0.0 \
    --num-samples 1 \
    --max-retries 1 \
    --thinking on \
    --resume -v \
    --project-root /home/samyak/Desktop/parbench_sam
```

This will skip all existing (correct) L3/L4 cells via `--resume` and only produce results for the deleted corrupted files.

**Expected:** 1–4 new results produced. Total runtime: a few minutes at most.

- [ ] **Step 4: Verify new results are not BUILD_FAIL on `translated_` errors**

```bash
source env_parbench/bin/activate
python3 -c "
import json, glob
for f in sorted(glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*nw*-L4.json')):
    r = json.load(open(f))
    print(f, '->', r.get('overall_status'))
"
```

Expected: the previously-corrupted file now shows a real result (PASS or BUILD_FAIL without `translated_` in the error), not a pipeline-induced failure.

- [ ] **Step 5: Regenerate eval_summary**

```bash
source env_parbench/bin/activate
python3 scripts/evaluation/analyze_eval.py \
    --project-root /home/samyak/Desktop/parbench_sam \
    2>&1 | tail -10
```

The `eval_summary.json` and `eval_summary.md` will be regenerated with corrected counts. Verify the L3/L4 counts change slightly (at most +1–4 PASS or -1–4 BUILD_FAIL relative to the prior summary).

- [ ] **Step 6: Commit the new result files and updated summary**

```bash
git add results/evaluation/together-qwen-3.5-397b-a17b/ \
        results/evaluation/eval_summary.json \
        results/evaluation/eval_summary.md
git commit -m "data: rerun corrupted L3/L4 ablation cells after de-anonymization fix

BUG-1 (generic filename in code body) caused ~1-4 BUILD_FAILs that were
pipeline-induced, not model failures. After fixing _deanonymize_extracted()
in Task 1, the corrupted result files were deleted and the affected cells
were rerun with temperature=0.0 --resume. Only the deleted cells were
regenerated; all other 204 ablation results are unchanged.

eval_summary regenerated to reflect corrected counts.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Do We Need to Rerun the Full Ablation?

**Short answer: No. Only the ~1–4 corrupted cells (Task 5).**

| Concern | Needs rerun? | Reason |
|---------|-------------|--------|
| BUG-1 de-anonymization (~1–4 L3/L4 cells) | **Yes — targeted** | Pipeline-induced BUILD_FAIL; fix + `--resume` covers it. Task 5. |
| BUG-2 retry logic | **No** | Retry never ran successfully, but the original batch results are correct. The bug only affected the retry pass, not first-attempt data. |
| KNOWN_FAIL specs in canonical | **No** | 66 records correctly excluded in analysis. Data is valid. |
| opencl→cuda 0% | **No (investigate first)** | If prompt audit (Task 4) confirms missing context, a targeted 5-kernel opencl→cuda canonical run + new L0-passer derivation + ablation would be a **new experiment**, not a correction to existing data. Decision gate at Task 4 Step 4. |
| omp_target→omp 100% (N=3 kernels) | **No** | Statistically valid; just narrow. No data error. |
| RSBench/XSBench 0% | **No** | Correct model failure; not a pipeline issue. |
| L0 vs L1–L4 temperature difference (0.7 vs 0.0) | **No data fix needed** | A design choice; affects paper framing (which you're rewriting), not data correctness. If you want a temperature-matched comparison in the future, that's a new experiment. |

**Canonical runs: completely solid.** 438 records (146 cells × 3 samples) after KNOWN_FAIL exclusion. No rerun needed.

**Ablation runs: 99.5%+ solid.** Only ~1–4 of 204 ablation records need correction via Task 5.

---

## Verification

After completing all 5 tasks:

```bash
# 1. Full test suite
source env_parbench/bin/activate
python3 -m pytest tests/ -q 2>&1 | tail -10

# 2. Validate specs and schema (expect ~15 known phantom errors, no new ones)
python3 scripts/validate_schema.py --all 2>&1 | tail -5

# 3. Final eval_summary check
python3 scripts/evaluation/analyze_eval.py \
    --project-root /home/samyak/Desktop/parbench_sam 2>&1 | tail -15

# 4. Confirm no translated_N strings in any L3/L4 BUILD_FAIL stderr
python3 -c "
import json, glob
bad = []
for f in glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*-L[34].json'):
    r = json.load(open(f))
    if r.get('overall_status') == 'BUILD_FAIL':
        for att in r.get('attempts', []):
            if 'translated_' in att.get('build_error_snippet', ''):
                bad.append(f)
print('Corrupted L3/L4 cells remaining:', len(bad))
for b in bad: print(' ', b)
"
# Expected: Corrupted L3/L4 cells remaining: 0
```
