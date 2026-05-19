---
name: augment-test
description: >
  Data augmentation testing workflow. Use when testing a new augmentation transform,
  diagnosing transform failures on a specific input, or validating transforms against
  known-good baselines. Runs augmentation pipeline and reports pass/fail per transform.
---

# Augmentation Testing Workflow

Structured workflow for testing data augmentation or transformation pipelines
on specific inputs.

## Arguments
- `$ARGUMENTS` — input identifier or path to test

## Workflow

### Phase 1: Run Augmentation

Execute the project's augmentation pipeline on the specified input:
```bash
python3 <augmentation-script> <input> \
  --level <N> --seed 42 -v
```

### Phase 2: Analyze Results

Check exit status and output for:
- **BUILD_FAIL** — augmented output doesn't compile/parse
- **TRANSFORM_FAIL** — transform itself errored
- **RUN_FAIL** — compiled but crashed at runtime
- **VERIFY_FAIL** — ran but produced wrong output
- **PASS** — all good

### Phase 3: Diagnose Failures

If the run failed, check against known bugs in `.claude/rules/known-issues.md`:
- Cross-reference with documented failure patterns
- Check if the input is in a known-failing list
- Identify whether the failure is in the transform or the input

### Phase 4: Report

```
Input:          <name>
Augment Level:  <N>
Seed:           <N>
Result:         PASS / FAIL (<type>)
Diagnosis:      <known bug reference or new finding>
Transforms Applied: <list or "none">
```

### Phase 5: Escalate (if new bug)

If the failure doesn't match any known bug:
1. Document the new bug with reproduction steps
2. Add it to `.claude/rules/known-issues.md`
3. Create a minimal reproduction case
