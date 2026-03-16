# Augmentation Testing Workflow

Structured workflow for testing augmentation transforms on a ParBench spec.

## Arguments
- `$ARGUMENTS` — spec name or path (e.g., "rodinia-bfs-cuda" or "specs/rodinia-bfs-cuda.json")

## Workflow

### Phase 1: Run Augmentation
```bash
python3 scripts/augmentation/augment_verify.py specs/<spec>.json \
  --augment_level 2 --seed 42 -v \
  --project-root /Users/samyakjhaveri/Desktop/parbench_sam
```

**IMPORTANT:** Always include `--project-root` — auto-detection is broken.

### Phase 2: Analyze Results
- Check exit status and output for:
  - `BUILD_FAIL` — augmented code doesn't compile
  - `TRANSFORM_FAIL` — transform itself errored
  - `RUN_FAIL` — compiled but crashed at runtime
  - `VERIFY_FAIL` — ran but produced wrong output
  - `PASS` — all good

### Phase 3: Diagnose Failures
If the run failed, check against known bugs in `.claude/rules/known-issues.md`:
- **Level 3-4 BUILD_FAIL** → likely Bug A, B, or C
- **Level 1-2 no transforms** → expected with seed=42 (no candidates)
- **`.cl` file issues** → check the `.cl` inconsistency note

### Phase 4: Report
```
Spec:           <name>
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
3. Update `analysis/reports/augmentation_bug_report.md`
