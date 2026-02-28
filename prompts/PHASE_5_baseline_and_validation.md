# Phase 5: Populate Baseline Results & Full Validation

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

**Prerequisites**: Phases 0–4 are complete. You have build/run/verify results for as many kernel-API combinations as possible.

### Context

You are working in `~/Desktop/parbench_sam/`. Each spec JSON has a `baseline_results` field that is currently `null` for all 60 new specs. This field records the known-good results on the reference hardware — it's critical for the paper because it establishes ground truth.

### Your Task

For every spec that passed verification (BUILD: PASS, RUN: PASS, VERIFY: PASS), populate the `baseline_results` field with actual measured data from this machine.

### Step-by-Step Process

#### Step 1: Identify passing specs

From `results/phase4/full_results_matrix.md`, extract the list of specs that fully passed:

```bash
cd ~/Desktop/parbench_sam
grep "| PASS | PASS | PASS |" results/phase4/full_results_matrix.md | awk -F'|' '{print $2"-"$3}' | sed 's/ //g'
```

#### Step 2: Run each passing spec with JSON output and capture results

For each passing spec, run the verify pipeline with JSON output to get structured results:

```bash
mkdir -p results/phase5

for spec in specs/hecbench-*-*.json; do
    spec_id=$(python3 -c "import json; print(json.load(open('$spec'))['identity']['unique_id'])")

    echo "=== Running $spec_id ==="

    # Run verify with JSON output
    python -m harness verify "$spec" --config correctness --json -v 2>&1 > "results/phase5/${spec_id}.log"

    # Extract just the JSON part (after the summary line)
    python3 -c "
import json, re

with open('results/phase5/${spec_id}.log') as f:
    content = f.read()

# Find JSON block in output
json_match = re.search(r'\{[\s\S]*\}', content)
if json_match:
    result = json.loads(json_match.group())
    with open('results/phase5/${spec_id}.json', 'w') as out:
        json.dump(result, out, indent=2)
    print(f'Saved JSON for ${spec_id}')
else:
    print(f'No JSON found for ${spec_id}')
" 2>&1

    echo ""
done
```

#### Step 3: Populate baseline_results in each spec

For each spec that has a successful result JSON, update its `baseline_results` field:

```python
#!/usr/bin/env python3
"""populate_baselines.py — Fill baseline_results from Phase 3/4 results."""

import json
import glob
import re
from pathlib import Path
from datetime import datetime, timezone

SPECS_DIR = Path("specs")
RESULTS_DIR = Path("results/phase5")
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for spec_path in sorted(SPECS_DIR.glob("hecbench-*.json")):
    spec_id = spec_path.stem
    result_path = RESULTS_DIR / f"{spec_id}.json"
    log_path = RESULTS_DIR / f"{spec_id}.log"

    if not log_path.exists():
        print(f"SKIP {spec_id}: no results log")
        continue

    with open(log_path) as f:
        log_content = f.read()

    # Check if verification passed
    if "VERIFY: PASS" not in log_content and "BUILD: PASS" not in log_content:
        print(f"SKIP {spec_id}: did not pass verification")
        continue

    # Load the spec
    with open(spec_path) as f:
        spec = json.load(f)

    # Extract stdout from the log (between [stdout] markers)
    stdout_match = re.search(r'\[stdout\]\n(.*?)(?:\n\[stderr\]|\Z)', log_content, re.DOTALL)
    stdout_snippet = stdout_match.group(1).strip()[:500] if stdout_match else ""

    # Extract wall time if available
    time_match = re.search(r'wall[_\s]?time[:\s]+([0-9.]+)', log_content, re.IGNORECASE)
    wall_time = float(time_match.group(1)) if time_match else None

    # Extract exit code
    exit_match = re.search(r'exit[_\s]?code[:\s]+(\d+)', log_content, re.IGNORECASE)
    exit_code = int(exit_match.group(1)) if exit_match else 0

    # Extract performance metrics using spec's regex patterns
    metrics = {}
    perf = spec.get("performance")
    if perf and perf.get("metrics"):
        for metric_def in perf["metrics"]:
            name = metric_def["name"]
            pattern = metric_def.get("extraction", {}).get("pattern", "")
            capture = metric_def.get("extraction", {}).get("capture_group", 1)
            unit = metric_def.get("unit", "")
            if pattern and stdout_snippet:
                m = re.search(pattern, stdout_snippet)
                if m:
                    try:
                        metrics[f"{name}_{unit}"] = float(m.group(capture))
                    except (ValueError, IndexError):
                        pass

    # Build baseline_results
    baseline = {
        "reference_platform": "rtx4070-r9-7900x",
        "timestamp": TIMESTAMP,
        "configurations": {
            "correctness": {
                "status": "pass",
                "exit_code": exit_code,
                "stdout_snippet": stdout_snippet,
                "wall_time_seconds": wall_time
            }
        }
    }

    if metrics:
        baseline["configurations"]["performance"] = {
            "status": "pass",
            "wall_time_seconds": wall_time,
            "metrics": metrics
        }

    # Update spec
    spec["baseline_results"] = baseline

    with open(spec_path, 'w') as f:
        json.dump(spec, f, indent=2)
        f.write('\n')

    print(f"OK {spec_id}: baseline populated ({len(metrics)} metrics)")

print("\nDone. Run validate_schema.py --all to verify.")
```

Save this script as `scripts/populate_baselines.py` and run it:

```bash
cd ~/Desktop/parbench_sam
python scripts/populate_baselines.py
```

#### Step 4: Final validation

Run the full validation suite:

```bash
cd ~/Desktop/parbench_sam
python scripts/validate_schema.py --all
```

**Expected**: All 80 specs pass validation, all manifest entries are consistent, and cross-kernel pairing shows 20 kernels × 4 APIs with the correct number of translation pairs.

#### Step 5: Generate final statistics

```bash
cd ~/Desktop/parbench_sam
python -m harness pairs > results/phase5/all_translation_pairs.txt
wc -l results/phase5/all_translation_pairs.txt
```

Expected: 20 kernels × C(4,2) × 2 = 20 × 12 = **240 directed translation pairs**.

#### Step 6: Create final summary report

Generate `analysis/reports/phase5_final_report.md` with:

1. Total kernels: 20
2. Total API variants: 80 specs
3. Total translation pairs: 240
4. Pass rates by API (how many of 20 kernels built/ran/verified for each API)
5. Domain distribution (how many kernels per domain category)
6. Any specs with `baseline_results: null` (not yet testable)
7. List of any known issues or limitations

### Deliverables

1. All passing specs updated with `baseline_results` populated from actual runs
2. `scripts/populate_baselines.py` — reusable script for future baseline population
3. `results/phase5/` — individual JSON result files for each spec
4. `results/phase5/all_translation_pairs.txt` — complete list of 240 translation pairs
5. `analysis/reports/phase5_final_report.md` — summary statistics
6. `python scripts/validate_schema.py --all` passes cleanly

### Do NOT

- Do NOT modify baseline_results for the existing 5 pilot kernels unless re-running improves accuracy
- Do NOT modify harness Python code
- Do NOT change file classifications (prompt_payload/support_files/verification_only)
- Do NOT commit/push to git unless I explicitly ask
