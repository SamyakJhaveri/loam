# Overnight Eval Campaign

Use when launching a long-running LLM evaluation batch that will take more than
5 minutes, needs tmux deployment, or should run unattended (overnight, weekend).

**Trigger:** When user types `/overnight-eval` with optional arguments.

## Arguments

- `$ARGUMENTS` --- shorthand `<suite> <direction> [--models <m1> <m2> ...]` or
  explicit flags matching `run_eval_batch.py`. If omitted, prompt interactively.

Optional flags:
- `--dry-run` --- run pre-flight only, do not launch
- `--session-name <name>` --- tmux session name (default: `parbench-eval`)
- `--alert-threshold <N>` --- error rate % that triggers desktop alert (default: 50)

## Iron Law

```
NO EVAL CAMPAIGN WITHOUT PRE-FLIGHT VERIFICATION.
Every API key, GPU device, submodule, venv, and spec eligibility check MUST pass
before the batch command is issued. No exceptions. No "I'll check later."
```

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll check the API keys later" | A failed key means wasted hours of wall time and zero results. 5 seconds to check. |
| "GPU is probably fine" | nvidia-smi takes 1 second. A busy GPU means queued kernels and wrong timing data. |
| "The submodule is probably initialized" | Empty submodule = every build fails. 2 seconds to verify. |
| "I can run it in the foreground" | Terminal disconnect = killed process = partial results. Always tmux. |
| "Resume will catch anything I miss" | Resume skips existing results. If pre-flight was wrong, resume perpetuates the error. |
| "I'll analyze tomorrow" | Tomorrow you won't remember what parameters you used. Log everything now. |

## Red Flags --- STOP

If any of these occur, abort the launch and investigate:

- nvidia-smi shows another process using >1GB GPU memory
- Any API key check fails
- `rodinia/rodinia-src/` is empty (submodule not initialized)
- Venv activation fails or key packages missing (anthropic, google-generativeai, groq)
- Previous eval results exist for the same model+direction+level without `--resume`
- Running in a git worktree (submodules won't work)

## Workflow

### Phase 1: Pre-Flight Verification

Run ALL checks. Every check must pass before proceeding.

#### 1a. Environment

```bash
# Activate venv
source {{PROJECT_ROOT}}/env_parbench/bin/activate

# Verify Python
python3 --version  # Must be 3.12.x

# Verify key packages
python3 -c "import anthropic; print('anthropic OK')"
python3 -c "import google.generativeai; print('google-genai OK')"
python3 -c "import groq; print('groq OK')"

# Verify NOT in a worktree
cd {{PROJECT_ROOT}} && git rev-parse --is-inside-work-tree
# Must NOT see ".git file" (that indicates worktree)
```

#### 1b. GPU Availability

```bash
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu \
  --format=csv,noheader
# Expect: NVIDIA GeForce RTX 4070, low memory usage, low utilization
```

If GPU memory usage >1GB or utilization >10%, warn and ask user to confirm.

#### 1c. API Keys (check only for selected models)

```bash
# Claude (if using claude-sonnet-4-6)
python3 -c "import os; k=os.environ.get('ANTHROPIC_API_KEY',''); print(f'ANTHROPIC_API_KEY: {\"SET (\" + str(len(k)) + \" chars)\" if k else \"MISSING\"}')"

# Groq (if using groq-llama-3.3-70b-versatile)
python3 -c "import os; k=os.environ.get('GROQ_API_KEY',''); print(f'GROQ_API_KEY: {\"SET (\" + str(len(k)) + \" chars)\" if k else \"MISSING\"}')"

# Google (if using gemini-2.5-flash-lite)
python3 -c "import os; k=os.environ.get('GOOGLE_AI_API_KEY',''); print(f'GOOGLE_AI_API_KEY: {\"SET (\" + str(len(k)) + \" chars)\" if k else \"MISSING\"}')"

# Together (if using together-qwen-3.5)
python3 -c "import os; k=os.environ.get('TOGETHER_API_KEY',''); print(f'TOGETHER_API_KEY: {\"SET (\" + str(len(k)) + \" chars)\" if k else \"MISSING\"}')"
```

#### 1d. Submodule and Source Verification

```bash
# Check Rodinia submodule is populated
ls {{PROJECT_ROOT}}/rodinia/rodinia-src/cuda/ | head -5
# Must show directories (bfs, backprop, etc.), not empty

# Check XSBench if needed
ls {{PROJECT_ROOT}}/xsbench/xsbench-src/ | head -3
```

#### 1e. Spec Eligibility

Verify eligible specs for the requested suite and direction. Exclude KNOWN_FAIL:

**KNOWN_FAIL specs (8 --- always exclude):**
- rodinia-kmeans-cuda, rodinia-mummergpu-cuda, rodinia-mummergpu-omp
- rodinia-hybridsort-cuda, rodinia-nn-opencl, rodinia-kmeans-opencl
- hecbench-stencil1d-omp_target, hecbench-scan-omp_target

**Rodinia eligible kernels by direction:**
- `cuda-to-omp` (17): backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster
- `omp-to-cuda` (16): same minus kmeans (CUDA is KNOWN_FAIL)
- `cuda-to-opencl` (17): backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster

#### 1f. Pre-Flight Summary

Display and **wait for user confirmation**:

```
=== OVERNIGHT EVAL PRE-FLIGHT ===

Environment:
  Python:      3.12.x
  Venv:        ACTIVE
  GPU:         NVIDIA GeForce RTX 4070 (memory: X/12GB, util: X%)
  Worktree:    NO (safe to proceed)
  Submodule:   POPULATED

API Keys:
  ANTHROPIC_API_KEY:   SET (XX chars) / MISSING
  GROQ_API_KEY:        SET (XX chars) / MISSING
  GOOGLE_AI_API_KEY:   SET (XX chars) / MISSING
  TOGETHER_API_KEY:    SET (XX chars) / MISSING

Campaign:
  Suite:       <suite>
  Direction:   <direction>
  Models:      <model1>, <model2>, ...
  Levels:      L<N>, ...
  Kernels:     <N> eligible
  Resume:      yes
  Max retries: 2
  Total tasks: <N models> x <N kernels> x <N levels> = <total>
  Est. time:   ~<N> minutes (rough: 1-2 min/task for API models)

tmux:
  Session:     <session-name>
  Alert at:    <threshold>% error rate

Proceed? (yes / no / modify)
```

If `--dry-run` was specified, stop here after displaying the summary.

**Verification gate:** ALL pre-flight checks pass. User confirms.

### Phase 2: Launch in tmux

Create a tmux session and launch the eval batch:

```bash
# Create tmux session
tmux new-session -d -s <session-name> -c {{PROJECT_ROOT}}

# Send the eval command
tmux send-keys -t <session-name> "source env_parbench/bin/activate && python3 scripts/evaluation/run_eval_batch.py \
  --suite <suite> \
  --direction <direction> \
  --models <model1> <model2> ... \
  --augment-levels <levels> \
  --max-retries 2 \
  --resume \
  --project-root {{PROJECT_ROOT}} \
  -v 2>&1 | tee results/evaluation/campaign_$(date +%Y%m%d_%H%M%S).log" Enter
```

**IMPORTANT:** Always pass `--project-root` (auto-detection broken) and `--suite`
(prevents cross-suite name collisions).

**Verification gate:** tmux session exists and eval command is running.
```bash
tmux has-session -t <session-name> && echo "Session running"
```

### Phase 3: Monitor (Periodic)

Set up monitoring. The user can check progress at any time:

```bash
# Check tmux session is still alive
tmux has-session -t <session-name> 2>/dev/null && echo "RUNNING" || echo "FINISHED"

# Count completed results
find {{PROJECT_ROOT}}/results/evaluation/ -name "*.json" \
  -newer /tmp/eval_start_marker 2>/dev/null | wc -l

# Check for recent errors (last 20 lines of log)
tmux capture-pane -t <session-name> -p | tail -20

# Running pass rate
python3 -c "
import json, glob, os
files = glob.glob('{{PROJECT_ROOT}}/results/evaluation/*/*.json')
statuses = {}
for f in files:
    try:
        d = json.load(open(f))
        s = d.get('overall_status', 'UNKNOWN')
        statuses[s] = statuses.get(s, 0) + 1
    except: pass
total = sum(statuses.values())
print(f'Results so far: {total}')
for s, c in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f'  {s}: {c} ({100*c/total:.1f}%)')
"
```

#### Error Spike Detection

If error rate exceeds the alert threshold:

```bash
# Desktop notification (Linux)
notify-send "ParBench Eval Alert" "Error rate exceeds <threshold>%! Check tmux session <session-name>" --urgency=critical

# Also log the alert
echo "[$(date)] ALERT: Error rate exceeded <threshold>%" >> results/evaluation/campaign_alerts.log
```

**Verification gate:** If monitored, pass rate and error rate are within expected bounds.

### Phase 4: Post-Flight Analysis

After the batch completes (tmux session ends or manual check confirms completion):

#### 4a. Generate Analysis

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate

python3 scripts/evaluation/analyze_eval.py \
  --project-root {{PROJECT_ROOT}} \
  --write-dashboard \
  --show-gaps \
  --expected-models <model1> <model2> ... \
  --expected-directions <direction> \
  --expected-levels <levels>
```

#### 4b. Generate Campaign Log

Write a structured campaign log to `results/evaluation/campaign_log_<date>.md`:

```markdown
# Campaign Log: <suite> <direction> <date>

## Parameters
- Suite: <suite>
- Direction: <direction>
- Models: <list>
- Levels: <list>
- Kernels: <N> eligible
- Start: <timestamp>
- End: <timestamp>
- Duration: <HH:MM>

## Results Summary
| Model | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | Total |
|-------|------|------------|----------|-------------|-------|

## Notable Findings
- <any unexpected failures, new error patterns, anomalies>

## Files Generated
- results/evaluation/<model>/*.json (N new files)
- results/evaluation/eval_summary.json (updated)

## Next Steps
- [ ] Run /paper-review-sim if paper claims need updating
- [ ] Run dashboard-refresher agent
- [ ] Commit results
```

#### 4c. Desktop Notification

```bash
notify-send "ParBench Eval Complete" \
  "Campaign finished: <suite> <direction>. Check campaign_log." \
  --urgency=normal
```

**Verification gate:** campaign_log written. analyze_eval.py ran without errors.
Result count matches expected (N models x N kernels x N levels).

### Phase 5: Handoff

Present results summary to user and recommend next steps:

1. Review `campaign_log_<date>.md` for anomalies
2. Run `dashboard-refresher` agent to update visualizations
3. Commit results: `"Session N: <suite> <direction> L<levels> --- N/M PASS"`
4. If paper-relevant: run `/paper-review-sim` to verify claims still hold

## Project Context (Self-Contained)

- **Project root:** `{{PROJECT_ROOT}}`
- **Venv:** `source env_parbench/bin/activate`
- **GPU:** NVIDIA GeForce RTX 4070 (12GB)
- **nvcc:** `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
- **Eval script:** `scripts/evaluation/run_eval_batch.py`
- **Analysis script:** `scripts/evaluation/analyze_eval.py`
- **Results dir:** `results/evaluation/{model}/`
- **Models:** claude-sonnet-4-6, gemini-2.5-flash-lite, groq-llama-3.3-70b-versatile, together-qwen-3.5
- **KNOWN_FAIL (8):** kmeans-cuda, mummergpu-cuda, mummergpu-omp, hybridsort-cuda, nn-opencl, kmeans-opencl, hecbench-stencil1d-omp_target, hecbench-scan-omp_target
- **Timing caveat:** Wall-clock times unreliable for speedup. Use nvprof/ncu for CUDA, omp_get_wtime for OMP.
- **Result JSON truth:** `overall_status` is authoritative, not top-level `run_status`
- **Git worktrees:** NEVER run evals in worktrees (submodules won't initialize)
