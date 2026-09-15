# Delivery rules and reference coverage: work/check sequence

Critical point: required cross-model reviews must come from the actual model and cover the exact plan or candidate advanced to main.

1. Preserve current records and inspect source/reference maps plus existing Claude infrastructure. Check: SHA-256 comparison against `consolidated-plan-checkpoint.json` and Git status. Expected and observed: `Delivery baseline: PASSED`; runtime source unchanged.
2. Record accepted worktree/review/merge rules, source-reading obligations and cookbook pattern destinations. Update the consolidated plan and handoff. Check: `python3 /private/tmp/loam-delivery-check.py`. Expected: `Delivery records: PASSED`, working links, mandatory opposite-model review rules, current-main progression and source/pattern coverage.
3. Obtain bounded correctness review, repair confirmed gaps, record review provenance and limitations, then verify preservation/checkpoint. Checks: document checker, changed Markdown scan, `git diff --check`, `delivery-checkpoint.json` digest verification. Expected: PASS. No runtime code, dependency, service, GPU run, commit or merge.
