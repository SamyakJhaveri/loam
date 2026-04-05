---
status: complete
phase: 09-objective-quantitative-analysis
source: [09-01-SUMMARY.md, 09-02-SUMMARY.md, 09-03-SUMMARY.md]
started: 2026-04-04T12:00:00Z
updated: 2026-04-04T12:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Script Runs Successfully
expected: Run `python3 scripts/analysis/quantitative_findings.py --project-root /home/samyak/Desktop/parbench_sam`. Script exits 0, produces quantitative_findings.json and quantitative_findings.md, no errors.
result: pass

### 2. Data Pipeline Counts Are Correct
expected: Run the script and check output JSON. total_files=1248, campaign_1 n=700, campaign_2 n=420, known_fail_excluded=128. These counts come from 1248 result JSONs minus 128 KNOWN_FAIL spec matches.
result: pass

### 3. All 14 Quantitative Dimensions Present
expected: Output JSON contains all 14 dimensions in campaign_1: aggregate_pass_rates, per_direction_rates, direction_asymmetry, augmentation_trend, failure_taxonomy, self_repair, per_kernel_tiers, complexity_correlation, cross_suite, token_cost, sloc_correlation, opencl_kernel_only_effect. Campaign_2 contains pass_at_k.
result: pass

### 4. Unit Tests Pass
expected: Run `python3 -m pytest scripts/analysis/test_quantitative_findings.py -v`. All 23 tests pass with exit code 0.
result: pass

### 5. Validation Gate Passes
expected: Run `python3 scripts/analysis/quantitative_findings.py --project-root /home/samyak/Desktop/parbench_sam --validate`. Reports 52 checks, 0 FAIL. All 11 spot-checks PASS, all 7 consistency checks PASS.
result: pass

### 6. Paper Claims Mapping Complete
expected: Output JSON has a paper_claims section with 20 entries. Each entry has claim_id, json_path, scope, and description fields. At least 8 claims should be MATCH against paper.tex.
result: pass

### 7. Provenance Framework Intact
expected: Spot-check any finding in the output JSON (e.g., campaign_1.aggregate_pass_rates.overall). It should contain provenance fields: value, source, files_matched, derivation. CI fields (ci_lower, ci_upper, ci_level) present for rate-type findings.
result: pass

### 8. Markdown Output Readable and Complete
expected: results/analysis/quantitative_findings.md contains readable tables for all dimensions. Has sections for Campaign 1 (all 12 L0 dimensions), Campaign 2 (pass@k), and Per-Kernel Difficulty. File is 300+ lines.
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
