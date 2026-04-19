# Spec Oracle Design — 5-Bucket Decision Tree

Purpose: classify each in-scope spec into one of 5 oracle-strength buckets and
pick the minimum-risk verification strategy. This is a decision guide, not a
full contributor rubric — the paper Methodology section owns the rest.

Scope: the 53 Tier 2 in-scope specs (18 confirmed-weak Rodinia + 35 unknown).
Already-strong HeCBench/XSBench/RSBench specs are out of scope.

## Decision tree

| # | Bucket | Signal | Action |
|---|--------|--------|--------|
| 1 | **already-strong** | Binary already prints under a correctness self-check, e.g. `if (correct) printf(...)`. | Keep strategies; set `oracle_strength: "strong"`. |
| 2 | **strong-after-regex-tighten** | Existing `stdout_pattern` fires but is too loose (matches even on garbage output). Tightening to require a numeric field closes the gap. | 1-line spec edit: narrow the `pattern` regex. Set `oracle_strength: "strong"`. |
| 3 | **needs-file_hash** | Binary writes a deterministic output file (result file, dump, binary blob) and produces bit-identical bytes across repeated runs with the same args. | Run `_capture_baseline.py`, commit reference file + spec edit. Set `oracle_strength: "strong"`. |
| 4 | **needs-numeric_comparison** | Binary prints a timing-independent numeric value (accuracy, checksum, residual) in stdout. | Add `numeric_comparison` strategy with `extract_regex` + `expected` + `tolerance`. Set `oracle_strength: "medium"` (or strong if tolerance is tight). |
| 5 | **truly-weak** | No output file, no numeric stdout metric, no self-check — OR output is non-deterministic (Rule 12: `_capture_baseline` reports SHA mismatch across two runs with identical args). | Set `oracle_strength: "weak"` + `# TODO(paper-threats)` comment on the spec. Record in paper Threats-to-Validity. |

## Determinism pre-flight (Rule 12, campaign-wide)

Before promoting any spec to bucket 3, run the binary twice with exactly
`run.input_configurations.correctness.arguments` and compare output-file
SHA-256s. `_capture_baseline.py` does this automatically and emits a loud
warning on mismatch. Non-deterministic specs MUST drop to bucket 4 (if a
timing-independent numeric exists) or bucket 5. Never `file_hash` on
non-deterministic output — the eval-time verify will false-FAIL every time.

## Worked example — `rodinia-bfs-omp` (bucket 3)

Source print site: `rodinia/rodinia-src/openmp/bfs/bfs.cpp:183`
```
printf("Result stored in result.txt\n");
```
The print is **unconditional** — the existing `stdout_pattern: "Result stored in"`
fires even when traversal output is garbage. But the binary also writes a
deterministic `result.txt` (confirmed via `_capture_baseline`), so the spec
upgrades to `file_hash`.

### Before
```json
"verification": {
  "method": "self_checking",
  "strategies": [
    { "type": "stdout_pattern", "pattern": "Result stored in", ... },
    { "type": "exit_code", "expected": 0, ... }
  ]
}
```

### After (paste from `_capture_baseline`)
```json
"verification": {
  "method": "reference_comparison",
  "oracle_strength": "strong",
  "strategies": [
    { "type": "file_hash", "path": "result.txt",
      "expected_sha256": "f57afc01ed133df945d453b6be22968448b29dad6e53a1dd27d3c9a7de39c5a0" },
    { "type": "exit_code", "expected": 0 }
  ],
  "reference_files": [
    { "path": "specs/references/bfs/result.txt",
      "sha256": "f57afc01ed133df945d453b6be22968448b29dad6e53a1dd27d3c9a7de39c5a0",
      "description": "Reference result.txt from _capture_baseline" }
  ]
}
```

### Terminal excerpt that produced the hash
```
$ python3 scripts/spec_tools/_capture_baseline.py specs/rodinia-bfs-omp.json \
      --project-root /home/samyak/Desktop/parbench_sam
--- candidate outputs (diff vs prompt_payload exclusion) ---
  result.txt   size=14908455B
    run1 sha256: f57afc01ed133df945d453b6be22968448b29dad6e53a1dd27d3c9a7de39c5a0
    run2 sha256: f57afc01ed133df945d453b6be22968448b29dad6e53a1dd27d3c9a7de39c5a0
```

## Escape hatch

If `_capture_baseline` shows no deterministic output AND no numeric stdout
is available, see `.planning/HANDOFF.md` §4 — author a short Python
post-processor at `scripts/spec_tools/postprocess_{kernel}.py` invoked via
`custom_script` strategy. Invoke only if buckets 3 and 4 are both infeasible.
Otherwise the spec drops to bucket 5 (`oracle_strength: "weak"`).
