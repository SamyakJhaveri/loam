# HANDOFF: Re-Run Ablation Study (Clean Slate)

**Date:** 2026-04-23
**Author:** Claude Code session (investigation + execution + adversarial review)
**Status:** Ready to execute — all prior cleanup DONE, ablation needs fresh re-run
**Audience:** Written for undergraduate software engineering clarity. Follow every step in order. Do not skip ahead.

---

## What Is This? (Plain English)

ParBench is a benchmark that tests how well LLMs translate parallel code (CUDA to OpenMP, etc.). We're running a Phase 3 evaluation experiment with the **Qwen 3.5 397B** model via **Together AI**. The experiment has two parts:

1. **Canonical runs** (L0): The LLM translates original source code. 3 samples per task at temperature=0.7.
2. **Ablation runs** (L1-L4): We apply cosmetic code transforms (rename variables, swap conditions, etc.) BEFORE giving the code to the LLM, to test sensitivity. 1 sample per task at temperature=0.7.

### What Already Happened (Prior Session)

A prior session found and fixed two bugs:

1. **Temperature confound (FIXED):** The batch script used `TEMPERATURE=0.0` for ablation instead of `0.7`. This was fixed and committed as `e1c6ea2`.
2. **Stale analysis outputs (DELETED):** 36 analysis files, 36 batch summaries, and all ablation result files were deleted. Committed as `72b848b`.

The prior session then attempted to re-run the ablation, but **Together AI had a sustained 500/503 outage**. The run produced 38 files (14 PASS, 24 ERROR) before being killed. **All 38 files have been deleted.** The system is now in a clean state.

### What This Session Must Do

Re-run the ablation study from scratch. That's it — no code changes, no analysis, no commits. Just:
1. Verify the system is clean
2. Confirm Together AI is healthy
3. Launch the ablation
4. Monitor until complete (with proper error escalation this time)
5. Verify the output

---

## Current State of the System

| Item | Status | Count |
|------|--------|-------|
| Canonical L0 results (`*-s0.json`, `*-s1.json`, `*-s2.json`) | CLEAN | 504 files |
| Ablation L1-L4 results (`*-L[1-4].json`) | DELETED (clean slate) | 0 files |
| L0 passers file (`.planning/eval-selections/l0_passers_*.json`) | VALID — do NOT regenerate | 51 cells |
| Temperature fix in `scripts/batch/run_phase3.sh` | COMMITTED (`e1c6ea2`) | Both lines = 0.7 |
| Stale analysis/figures/summaries | DELETED + COMMITTED (`72b848b`) | 0 files |
| Ablation batch summaries | DELETED | 0 files |
| Ablation log/done marker | DELETED | 0 files |

**Expected output:** 51 L0-passer cells × 4 augmentation levels (L1,L2,L3,L4) = **204 ablation result files**.

---

## Skills to Load at Session Start

Before doing ANY work, invoke these two skills. They guide HOW you work:

```
Skill("superpowers:test-driven-development")        — run verification checks BEFORE and AFTER each step
Skill("andrej-karpathy-skills:karpathy-guidelines")  — no unnecessary changes, surgical precision
```

---

## Working Directory

**All commands assume:**
```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
```

Run these two lines FIRST, before any other command.

---

## Step-by-Step Execution

### Step 0: Pre-Flight Verification

Verify the system is in the expected clean state. Every check must pass.

```bash
# 1. Canonical files intact (MUST be 504)
echo "Canonical: $(ls results/evaluation/together-qwen-3.5-397b-a17b/*-s[012].json | wc -l) (expect 504)"

# 2. Ablation files gone (MUST be 0)
echo "Ablation: $(ls results/evaluation/together-qwen-3.5-397b-a17b/*-L[1-4].json 2>/dev/null | wc -l) (expect 0)"

# 3. No stale ablation log or done marker (MUST be 0)
echo "Stale markers: $(ls results/evaluation/together-qwen-3_5-397b-a17b_ablation* 2>/dev/null | wc -l) (expect 0)"

# 4. L0 passers file valid — derive the expected file count
python3 -c "
import json
cells = len(json.load(open('.planning/eval-selections/l0_passers_together_qwen_3_5_397b_a17b.json')))
expected = cells * 4
print(f'L0 passers: {cells} cells x 4 levels = {expected} expected ablation files')
assert expected == 204, f'Expected 204 but got {expected} — STOP and investigate'
"

# 5. API key present
echo "TOGETHER_API_KEY length: ${#TOGETHER_API_KEY}"
# Must be > 0

# 6. Temperature fix committed (both lines must show 0.7)
grep -n '^[[:space:]]*TEMPERATURE=' scripts/batch/run_phase3.sh
# Expected:
#   142:    TEMPERATURE=0.7
#   149:    TEMPERATURE=0.7
```

**GATE:** If ANY check fails, STOP and diagnose. Do not proceed to Step 1.

---

### Step 1: Test Together AI API Health

The prior run failed because Together AI had a sustained outage. Before launching 204 tasks, confirm the API is responding.

```bash
python3 -c "
from openai import OpenAI
import os
client = OpenAI(
    api_key=os.environ['TOGETHER_API_KEY'],
    base_url='https://api.together.xyz/v1'
)
# Use the exact model ID from MODEL_REGISTRY in llm_evaluate.py line 136
r = client.chat.completions.create(
    model='Qwen/Qwen3.5-397B-A17B',
    messages=[{'role':'user','content':'Say OK'}],
    max_tokens=5
)
print(f'API response: {r.choices[0].message.content}')

# Quick burst test — 2 more calls to check rate limiting
for i in range(2):
    r2 = client.chat.completions.create(
        model='Qwen/Qwen3.5-397B-A17B',
        messages=[{'role':'user','content':'Say OK'}],
        max_tokens=5
    )
print(f'Burst test: 3/3 calls succeeded. Together AI is healthy.')
"
```

**GATE:** Must print "3/3 calls succeeded." If you get 500/503 errors, STOP — the API is still down. Wait and retry later.

---

### Step 2: Launch Ablation Re-Run

```bash
bash scripts/batch/run_phase3.sh ablation together-qwen-3.5-397b-a17b
```

**What this does:**
- Launches a tmux session named `phase3-ablation`
- Runs 30 batches across all suite/direction combinations
- Each batch calls `run_eval_batch.py` with `--temperature 0.7 --augment-levels 1 2 3 4 --num-samples 1 --thinking on --resume`
- Uses the 51-cell L0-passers file as the task list (`--task-list`)

**Verify launch by checking the first few lines of log output:**
```bash
sleep 15 && head -5 results/evaluation/together-qwen-3_5-397b-a17b_ablation.log
```

Expected: Pre-launch checks (API key OK, submodule OK, GPU info).

**Confirm parameters in the first batch header:**
```bash
sleep 30 && grep -m1 "temperature=" results/evaluation/together-qwen-3_5-397b-a17b_ablation.log
```

Expected: `temperature=0.7`

**Estimated time:** ~2-4 hours for 204 tasks (~30-90 seconds per LLM call).
**Estimated cost:** ~$2-3 (Together AI pricing for Qwen 3.5 397B).

---

### Step 3: Monitor Every 8 Minutes (With Error Escalation)

**THIS IS CRITICAL.** The prior run failed because the monitoring didn't catch a sustained API outage. This time, actively watch for consecutive errors.

Run this monitoring script every 8 minutes:

```bash
python3 -c "
import json, glob, os

# Count files and statuses
files = glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*-L[1234].json')
statuses = {}
for f in files:
    with open(f) as fh:
        s = json.load(fh).get('overall_status', 'UNKNOWN')
    statuses[s] = statuses.get(s, 0) + 1
total = len(files)

# Check done marker
done = os.path.exists('results/evaluation/together-qwen-3_5-397b-a17b_ablation_done.marker')

print(f'Progress: {total}/204 ({total*100//204}%)')
print('  '.join(f'{s}: {c}' for s, c in sorted(statuses.items())) if statuses else 'No files yet')
print(f'Done marker: {\"YES\" if done else \"no\"}')

# ERROR ESCALATION: check for high error rate
error_count = statuses.get('ERROR', 0) + statuses.get('EXTRACTION_FAIL', 0)
if total > 0 and error_count / total > 0.3:
    print(f'WARNING: {error_count}/{total} ({error_count*100//total}%) errors — check Together AI status!')
    print('Consider killing tmux and waiting for API to recover.')
"
```

Also check the log tail for consecutive errors:

```bash
tail -10 results/evaluation/together-qwen-3_5-397b-a17b_ablation.log 2>/dev/null | grep -c 'ERROR'
# If this returns 5 or more: STOP the run. The API is down.
# Kill with: tmux kill-session -t phase3-ablation
```

**Error escalation rule:** If you see 5+ consecutive ERRORs in the log tail, IMMEDIATELY:
1. Kill the tmux session: `tmux kill-session -t phase3-ablation`
2. Alert the user that Together AI is down
3. Wait for the user to say when to retry

**Expected log noise (NOT errors):**
- "warning: passer entry skipped — APIs do not match" — NORMAL. The 51-cell task list gets filtered by direction; non-matching cells are skipped.
- Some batches will show all tasks as "SKIP" — NORMAL. With `--task-list`, multiple batch calls share the same direction; `--resume` skips already-completed tasks.
- Final summary may report "WARNING: N batches still failing" — NORMAL if those are directions with zero matching cells. The definitive check is the file count (204), NOT the batch failure count.

---

### Step 4: Post-Run Verification (When Done)

When the done marker appears (`results/evaluation/together-qwen-3_5-397b-a17b_ablation_done.marker`), OR when 204 files exist, run these checks:

```bash
# 1. File count (MUST be 204)
echo "Ablation files: $(ls results/evaluation/together-qwen-3.5-397b-a17b/*-L[1-4].json | wc -l) (expect 204)"

# 2. ALL must have temperature=0.7
python3 -c "
import json, glob
files = sorted(glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*-L[1234].json'))
print(f'Ablation files: {len(files)}')
wrong = [f for f in files if json.load(open(f)).get('temperature') != 0.7]
if wrong:
    print(f'FAIL: {len(wrong)} files have wrong temperature!')
else:
    print('PASS: all files have temperature=0.7')
"

# 3. Status breakdown — check for retryable errors
python3 -c "
import json, glob
files = glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*-L[1234].json')
statuses = {}
for f in files:
    with open(f) as fh:
        s = json.load(fh).get('overall_status', 'UNKNOWN')
    statuses[s] = statuses.get(s, 0) + 1
print(f'Total: {len(files)}/204')
for s, c in sorted(statuses.items()):
    print(f'  {s}: {c}')
retryable = statuses.get('ERROR', 0) + statuses.get('EXTRACTION_FAIL', 0)
if retryable > 0:
    print(f'\n{retryable} retryable failures. Re-run the same launch command to retry them.')
    print('The --resume flag auto-retries ERROR/EXTRACTION_FAIL (skips PASS/BUILD_FAIL/etc.)')
else:
    print('\nNo retryable failures. Ablation run is COMPLETE.')
"

# 4. Verify all 51 L0-passer cells have exactly 4 levels each
python3 -c "
import json, glob, os
from collections import defaultdict

passers = json.load(open('.planning/eval-selections/l0_passers_together_qwen_3_5_397b_a17b.json'))
files = glob.glob('results/evaluation/together-qwen-3.5-397b-a17b/*-L[1234].json')

# Group by cell (source→target)
cells = defaultdict(set)
for f in files:
    r = json.load(open(f))
    key = (r.get('source_spec'), r.get('target_spec'))
    cells[key].add(r.get('augment_level'))

missing = []
for p in passers:
    key = (p['source_spec'], p['target_spec'])
    levels = cells.get(key, set())
    if levels != {1, 2, 3, 4}:
        missing.append((key, levels))

if missing:
    print(f'FAIL: {len(missing)} cells missing levels:')
    for (s,t), levels in missing[:5]:
        print(f'  {s} → {t}: has levels {sorted(levels)}')
else:
    print(f'PASS: all {len(passers)} cells have levels {{1,2,3,4}}')
"

# 5. Canonical files untouched (MUST still be 504)
echo "Canonical: $(ls results/evaluation/together-qwen-3.5-397b-a17b/*-s[012].json | wc -l) (expect 504)"
```

**If fewer than 204 files or retryable errors exist:** Re-run the same launch command:
```bash
bash scripts/batch/run_phase3.sh ablation together-qwen-3.5-397b-a17b
```
The `--resume` flag auto-retries ERROR/EXTRACTION_FAIL statuses and skips everything else.

If a specific task fails 3+ times in a row, it's a deterministic failure (not a transient API issue). Record the task name and move on.

---

### Step 5: Tmux Session Recovery (If It Dies)

If `tmux ls` shows no `phase3-ablation` session and the done marker does NOT exist, the session died (OOM, SSH disconnect, etc.).

**Recovery steps:**
```bash
# 1. Check what we have so far
ls results/evaluation/together-qwen-3.5-397b-a17b/*-L[1-4].json 2>/dev/null | wc -l

# 2. Check last log entry
tail -5 results/evaluation/together-qwen-3_5-397b-a17b_ablation.log

# 3. Re-launch — --resume picks up where it left off
bash scripts/batch/run_phase3.sh ablation together-qwen-3.5-397b-a17b
```

---

## What NOT To Do

| Don't | Why | Instead |
|-------|-----|---------|
| Use `rm` on files in `results/evaluation/` | `protect-eval-results.sh` hook will BLOCK | Use `python3 -c "import os; os.remove(...)"` |
| Change defaults in `llm_evaluate.py` or `run_eval_batch.py` | Would make all future ad-hoc runs stochastic | Only `run_phase3.sh` was fixed (already committed) |
| Regenerate `l0_passers_*.json` | Derived from canonical L0 (unchanged) | Keep existing file |
| Run analysis scripts (`analyze_eval.py`, etc.) | They still use broken campaign split logic | Defer to NEXT session |
| Commit anything | No code changes in this session | Only data generation |
| Ignore consecutive ERRORs in the log | Prior run failed this way — 24 ERROR files | Kill tmux if 5+ consecutive ERRORs |

---

## Key Files Reference

| File | Path | What It Does |
|------|------|-------------|
| Batch launch script | `scripts/batch/run_phase3.sh` | Runs ablation in tmux (already fixed) |
| L0 passers (task list) | `.planning/eval-selections/l0_passers_together_qwen_3_5_397b_a17b.json` | 51 cells to run ablation on |
| Ablation results (output) | `results/evaluation/together-qwen-3.5-397b-a17b/*-L[1-4].json` | 204 files expected |
| Run log | `results/evaluation/together-qwen-3_5-397b-a17b_ablation.log` | Monitor for errors |
| Done marker | `results/evaluation/together-qwen-3_5-397b-a17b_ablation_done.marker` | Written when all 30 batches complete |
| Eval batch runner | `scripts/evaluation/run_eval_batch.py` | `--resume` retries ERROR/EXTRACTION_FAIL |
| LLM evaluator | `scripts/evaluation/llm_evaluate.py` | MODEL_REGISTRY has `Qwen/Qwen3.5-397B-A17B` |
| Hook (blocks rm) | `.claude/hooks/protect-eval-results.sh` | Blocks `rm results/evaluation/*` |
| Project rules | `CLAUDE.md` (project root) | Critical invariants — read this |

---

## What Happened and Why (Full History)

1. **2026-04-23 Session 1:** Samyak noticed `quantitative_findings.md` reported `temperature=0.0` for the "primary experiment." Investigation revealed the analysis scripts split data by temperature (old design) instead of augment_level (Phase 3 design), inverting canonical and ablation data. Further investigation found `run_phase3.sh` hardcoded `TEMPERATURE=0.0` for ablation — a confounding variable.

2. **2026-04-23 Session 2 (this session's predecessor):** Deleted all stale outputs (36 analysis + 36 batch summaries + 204 ablation results). Fixed `run_phase3.sh` (0.0→0.7). Committed both changes. Attempted ablation re-run.

3. **Ablation re-run failure:** Together AI had a sustained 500/503 outage. The monitoring loop checked every 8 minutes but failed to catch the cascade — by the time it was noticed, 24/38 files were ERROR. The tmux session was manually killed.

4. **Cleanup:** All 38 partial ablation files (14 PASS + 24 ERROR) were deleted. System is now at clean slate.

**Lesson learned:** The monitoring was too passive. This handoff adds explicit error escalation rules (5+ consecutive ERRORs = kill and alert) and a burst API health check before launch.

---

## Deferred Work (NEXT Session, After Ablation Completes)

The analysis scripts in `scripts/analysis/` are structurally broken for Phase 3. They split data by temperature (old design) instead of augment_level. Full rewrite plan:

| Script | Key Issue |
|--------|-----------|
| `scripts/analysis/generate_paper_data.py` | `split_campaigns()` ~line 546 splits by `temperature` — must split by `augment_level` |
| `scripts/analysis/quantitative_findings.py` | Same `split_campaigns()` issue ~line 352 |
| `scripts/analysis/statistical_analysis.py` | `is_deterministic()`/`is_stochastic()` ~lines 59-62 — must become `is_canonical()`/`is_ablation()` |
| `scripts/analysis/augmentation_analysis.py` | `_is_stochastic()` ~line 160 skips `-s\d+` files, accidentally dropping all canonical data |
| `scripts/analysis/cross_consistency_audit.py` | Hardcoded `primary_campaign`/`passk_campaign` keys |
| `scripts/analysis/cross_model_comparison.py` | Reads `primary_campaign` from `paper_data.json` |

**Do NOT run these scripts until they are rewritten.** They will produce wrong numbers.
