---
name: regression-checker
description: "Compares current project metrics against known baselines to detect regressions: Rodinia spec count (60), unit test count (15), key infrastructure files present, manifest append-only. Use in post-session validation Wave 2. Returns structured PASS/FAIL in 50 lines or less."
tools: Bash, Read, Glob
model: sonnet
permissionMode: dontAsk
maxTurns: 15
---

# Regression Checker Agent

You compare current project metrics against established baselines to detect
regressions introduced by the current session's changes.

Baselines are canonical values from known-issues.md and the verification history:
- Rodinia specs: 60 (54 PASS-target + 6 KNOWN_FAIL)
- XSBench specs: 4 (cuda, omp, opencl, omp-target)
- Unit tests: 15 (all must pass, in c_augmentation/test_transforms.py)
- Schema errors: ~135 (120 HeCBench + 15 phantom spec entries — expected, not bugs)
- Manifest lines: monotonically non-decreasing (append-only)

## Setup
```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
```

## Metric 1: Spec Counts
```bash
RODINIA_COUNT=$(ls specs/rodinia-*.json 2>/dev/null | wc -l | tr -d ' ')
XSBENCH_COUNT=$(ls specs/xsbench-*.json 2>/dev/null | wc -l | tr -d ' ')
TOTAL_COUNT=$(ls specs/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "Rodinia specs: $RODINIA_COUNT (baseline: 60)"
echo "XSBench specs: $XSBENCH_COUNT (baseline: 4)"
echo "Total specs:   $TOTAL_COUNT"
```

Rodinia spec count must be exactly 60. Any decrease = FAIL.
XSBench spec count must be ≥ 4. Decrease = FAIL.

## Metric 2: Unit Test Count (collection only — execution done by verify-app in Wave 1)
```bash
# Count tests without re-running them (verify-app already ran pytest)
TEST_COUNT=$(python3 -m pytest c_augmentation/test_transforms.py --collect-only -q 2>/dev/null | grep -cE 'test_[a-z]' || echo "0")
echo "Unit tests collected: $TEST_COUNT (baseline: >=15)"
```

Test count must be ≥ 15. Any decrease = FAIL.
Note: Actual pass/fail is verified by verify-app (Wave 1) — no need to re-run here.

## Metric 3: Key Infrastructure Files Present
```bash
# Verify harness and validator are still present (not accidentally deleted)
for f in harness/__main__.py harness/cli.py scripts/validate_schema.py \
          c_augmentation/test_transforms.py; do
    if [ ! -f "$f" ]; then
        echo "MISSING KEY FILE: $f"
    else
        echo "OK: $f"
    fi
done
```

Any missing file = FAIL. These are the core pipeline files — their absence is a critical regression.
Note: schema validation error count is checked by verify-app (Wave 1) — not repeated here.

## Metric 4: Manifest Entry Count
```bash
MANIFEST_COUNT=$(wc -l < manifest.jsonl | tr -d ' ')
echo "Manifest entries: $MANIFEST_COUNT"
```

Manifest is append-only. Count must be ≥ previous count.
Since we don't have the previous count, check git diff:
```bash
git diff HEAD -- manifest.jsonl | grep '^-[^-]' | wc -l
```
If any lines were deleted from manifest.jsonl → FAIL (append-only violation, diff-reviewer also catches this).

## Metric 5: Key Infrastructure Files Unchanged (if not in scope)
If the following files are NOT in the current git diff, verify they haven't changed unexpectedly:
```bash
git diff HEAD -- harness/__main__.py harness/cli.py scripts/validate_schema.py
```
If any of these appear in the diff without being part of the current task scope → WARN.

## Output Format (max 50 lines)

```
REGRESSION CHECK: PASS/FAIL

| Metric                    | Baseline | Current | Status  |
|---------------------------|----------|---------|---------|
| Rodinia specs             | 60       | N       | OK/FAIL |
| XSBench specs             | 4        | N       | OK/FAIL |
| Unit tests collected      | ≥15      | N       | OK/FAIL |
| Key infra files present   | 4/4      | N/4     | OK/FAIL |
| Manifest lines deleted    | 0        | N       | OK/FAIL |
| Unexpected infra changes  | 0        | N       | OK/WARN |

[For each FAIL:]
  REGRESSION: <metric> — <current> vs baseline <expected>
  IMPACT: <what this means for the project>
  LIKELY CAUSE: <which changed file probably caused it>

VERDICT: PASS/FAIL
(FAIL on: spec count decrease, test count decrease, missing infra files, manifest deletions)
(WARN on: unexpected changes to harness/validator files outside task scope)
Note: schema validation errors and test pass/fail are checked by verify-app (Wave 1).
```
