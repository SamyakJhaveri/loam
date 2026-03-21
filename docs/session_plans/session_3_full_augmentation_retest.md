# Session 3: Full 60-Spec Batch Retest at L1–L4

> **Depends on:** Session 2 (8 M10b specs verified PASS)
> **Blocks:** Session 5 (dashboard refresh)
> **Estimated time:** 60–90 minutes (240 tasks: 60 specs × 4 levels)
> **Thinking level:** use ultrathink.
> **USE 8 subagents**

---

## Objective

Run the augmentation batch retest across all 60 Rodinia specs at levels 1–4 to confirm
the 56/60 PASS claim. This produces the definitive results file for the SC26 paper.
The previous retest (`retest_post_m9`) was run on 65 specs (before phantom deletion)
and before the Session 1 `ChangeFunctionNames` harness fix.

---

## Claude Code Prompt

```
I need to complete Session 3 of the Sprint Audit Fix Plan: full 60-spec augmentation retest.

**Pre-checks:**
1. Confirm Session 2 is committed:
```bash
git log --oneline -5
```
Should show Session 2 commit (M10b targeted retest).

2. Confirm spec count is 60:
```bash
ls specs/rodinia-*.json | wc -l
```
Should be 60 (65 original - 5 phantom deletions).

3. Confirm the 5 phantom specs are deleted:
```bash
ls specs/rodinia-gaussian-omp.json specs/rodinia-huffman-omp.json specs/rodinia-huffman-opencl.json specs/rodinia-hybridsort-omp.json specs/rodinia-mummergpu-opencl.json 2>&1
```
All should show "No such file or directory".

## Phase 1: Activate environment and read the batch script

```bash
source env_parbench/bin/activate
```

Read `scripts/augmentation/run_augment_batch.py` to confirm the exact CLI args.
The script expects:
- Positional: spec file paths (glob ok)
- `--levels` / `-l`: augmentation levels (space-separated ints)
- `--seed` / `-s`: random seed
- `--config`: run configuration name (default "correctness")
- `--out`: output prefix (creates .json + .md)
- `--title`: markdown title
- `-v` / `--verbose`: show subprocess output

## Phase 2: Run the full batch

```bash
python3 scripts/augmentation/run_augment_batch.py \
  specs/rodinia-*.json \
  --levels 1 2 3 4 \
  --seed 42 \
  --config correctness \
  --out results/augmentation/retest_post_session2 \
  --title "Post-Session 2 Full Retest: 60 Rodinia specs × L1-L4 (seed=42)" \
  -v
```

**IMPORTANT:** This will take 60-90 minutes. Run it in background if needed.
It creates 240 tasks (60 specs × 4 levels), executed sequentially.
Progress prints to stdout: `[done/total] spec_id L{level} ✓/✗ (elapsed_time)`

**Expected results:**
- 56 specs PASS at all levels (level-invariant — this is a key paper claim)
- 4 KNOWN_FAIL specs fail at all levels (kmeans-cuda, hybridsort-cuda, nn-opencl, kmeans-opencl)
- Total: 224/240 PASS, 16/240 FAIL (4 specs × 4 levels)

## Phase 3: Analyze results

Once the batch completes:

1. Read the generated markdown: `results/augmentation/retest_post_session2.md`
2. Read the JSON for machine-parseable data: `results/augmentation/retest_post_session2.json`
3. Confirm level-invariance: every spec that passes at L1 also passes at L2, L3, L4
4. Confirm the 4 KNOWN_FAIL specs fail at all levels

Create a summary table:
```
| Level | PASS | BUILD_FAIL | FAIL | ERROR | Total |
|-------|------|-----------|------|-------|-------|
| L1    | ??   | ??        | ??   | ??    | 60    |
| L2    | ??   | ??        | ??   | ??    | 60    |
| L3    | ??   | ??        | ??   | ??    | 60    |
| L4    | ??   | ??        | ??   | ??    | 60    |
```

## Phase 4: Investigate unexpected failures

**If any of the 56 expected-PASS specs fail:**
- This is a regression. Investigate immediately.
- Read the per-spec result from the JSON file
- Check if it's a build failure (missing header? compiler flag?) or run failure (wrong args? missing data?)
- Fix the issue in this session
- Re-run ONLY the failing spec to confirm the fix:
  ```bash
  python3 scripts/augmentation/augment_verify.py specs/<failing-spec>.json \
    --augment_level 2 --seed 42 -v \
    --project-root /home/samyak/Desktop/parbench_sam
  ```

**If a KNOWN_FAIL spec unexpectedly PASSES:**
- Document this — it means a previous fix resolved an unknown dependency
- Remove from KNOWN_FAIL list in known-issues.md

## Phase 5: Compare with previous retest

Compare new results against `results/augmentation/retest_post_m9.md`:
- Previous: 48/65 PASS (73%) — but that was 65 specs including 5 phantoms
- Expected now: 56/60 PASS (93%) — phantoms removed + 8 M10b fixes

The improvement from 73% to 93% is entirely explained by:
1. Removing 5 phantom specs (were ERROR → gone)
2. Fixing 8 specs (were BUILD_FAIL/FAIL → PASS)
3. 4 remaining KNOWN_FAIL specs account for the 7%

## Phase 6: Update known-issues.md

Update the M10 section with new results:
```
## Post-Session 2 Full Retest (2026-03-2X)

60-spec retest (post-phantom-deletion, post-M10b fixes), seed=42.
Results: `results/augmentation/retest_post_session2.json` / `.md`

| Level | PASS | BUILD_FAIL | FAIL | ERROR |
|-------|------|-----------|------|-------|
| L1    | N/60 | ...       | ...  | ...   |
...

Results are level-invariant. Augmentation transforms introduce zero new failures.
```

## Phase 7: Commit and Push

Commit ONLY after ALL verification passes. Then push immediately:

```
Post-Session 2 full retest: N/60 PASS at L1-L4 (seed=42)

- 60 Rodinia specs tested at augmentation levels 1-4
- N/60 PASS at all levels (level-invariant)
- 4 KNOWN_FAIL specs confirmed failing
- Results: results/augmentation/retest_post_session2.{json,md}
```

```bash
git push origin main
```
```

---

## Script Reference

### `run_augment_batch.py` CLI

```
usage: run_augment_batch.py [-h] [--levels LEVELS [LEVELS ...]] [--seed SEED]
                            [--config CONFIG] --out OUT [--title TITLE] [-v]
                            specs [specs ...]

positional arguments:
  specs                 One or more spec JSON files (glob-expanded by shell)

optional arguments:
  --levels, -l          Augmentation levels to test (default: [2])
  --seed, -s            Random seed (default: 42)
  --config              Run configuration name (default: "correctness")
  --out                 Output prefix — creates {out}.json + {out}.md
  --title               Markdown report title
  -v, --verbose         Show subprocess output
```

### `augment_verify.py` CLI (for individual re-runs)

```
usage: augment_verify.py [-h] [-l {0,1,2,3,4}] [-s SEED] [--config CONFIG]
                         [--project-root PROJECT_ROOT] [--keep-temp] [-v] [--json]
                         spec_file

positional arguments:
  spec_file             Path to spec JSON

optional arguments:
  -l, --augment_level   Aggressiveness 0-4 (default: 1)
  -s, --seed            Random seed
  --config              Run configuration (default: "correctness")
  --project-root        Path to parbench_sam/ (ALWAYS pass this)
  --keep-temp           Retain temp build directory for debugging
  -v, --verbose         Show subprocess output
  --json                Print machine-readable JSON result
```

### Output File Format

**JSON** (array of result objects):
```json
[
  {
    "spec_id": "rodinia-backprop-cuda",
    "augment_level": 2,
    "seed": 42,
    "config": "correctness",
    "transforms_applied": {"filename.cu": ["SwapCondition", "ArithmeticTransform"]},
    "transforms_summary": ["SwapCondition", "ArithmeticTransform"],
    "files_changed": ["filename.cu"],
    "build_status": "pass",
    "run_status": "pass",
    "verify_status": "pass",
    "overall_status": "PASS",
    "wall_time_seconds": 0.146,
    "exit_code": 0
  }
]
```

**Markdown** (human-readable tables):
- Results matrix: Spec × Level columns with PASS/FAIL status
- Summary stats per level
- Transform frequency table

## Previous Retest Baseline (for comparison)

From `results/augmentation/retest_post_m9.md` (65 specs, pre-Session 1/2 fixes):

| Level | PASS | BUILD_FAIL | FAIL | ERROR |
|-------|------|-----------|------|-------|
| L1 | 48/65 (73%) | 7 | 5 | 5 |
| L2 | 48/65 (73%) | 7 | 5 | 5 |
| L3 | 48/65 (73%) | 7 | 5 | 5 |
| L4 | 48/65 (73%) | 7 | 5 | 5 |

Transform frequency: SwapCondition=162, ArithmeticTransform=69, ChangeNames=55,
TypedefExpansion=7, PointerArithmeticToArrayIndex=6, ChangeFunctionNames=2

## The 4 KNOWN_FAIL Specs (expect failure)

| Spec | Expected Failure | Root Cause |
|------|-----------------|------------|
| `rodinia-kmeans-cuda` | BUILD_FAIL | `texture<>` removed in CUDA 12 |
| `rodinia-hybridsort-cuda` | BUILD_FAIL | `GL/glew.h` not found |
| `rodinia-nn-opencl` | RUN_FAIL (SIGSEGV) | OpenCL runtime crash |
| `rodinia-kmeans-opencl` | RUN_FAIL (exit -11) | OpenCL runtime crash |

## Success Criteria

- [ ] Batch run completed for all 240 tasks (60 × 4)
- [ ] 56/60 PASS at all levels (or clear explanation of any deviation)
- [ ] Level-invariance confirmed (same specs pass/fail at L1 through L4)
- [ ] 4 KNOWN_FAIL specs confirmed still failing
- [ ] Results files committed: `.json` + `.md`
- [ ] known-issues.md updated with new retest results
- [ ] Verified, committed, and pushed to remote
