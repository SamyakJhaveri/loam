# GPT-5.4 Evaluation Run Plan — Canonical + Ablation for NeurIPS 2026

**Date:** 2026-04-25
**Author:** Claude Code session (brainstorming → plan-reviewer → handoff)
**Status:** Ready to implement
**Audience:** Written for undergraduate software engineering clarity. Follow every step in order.

---

## What Is This? (Plain English)

ParBench is a research project that tests how well AI models can translate code between parallel programming APIs (CUDA, OpenMP, OpenCL). We already ran **Qwen 3.5 397B** through all benchmarks and got 708 result files. Now we need to run the **second model: GPT-5.4** (via Azure AI) through the exact same benchmarks so we can compare the two models in our NeurIPS 2026 paper.

The evaluation infrastructure (`run_phase3.sh`, `run_eval_batch.py`, `llm_evaluate.py`) is battle-tested from the Qwen run. We need to make **3 small code fixes** and **update 2 environment variables** before launching.

### Key Concepts You Need

| Term | What It Means |
|------|--------------|
| **Canonical experiment** | The main evaluation: 3 random samples per task at L0 (no code perturbation), temp=0.7. Result files end in `-s0.json`, `-s1.json`, `-s2.json`. |
| **Ablation experiment** | Follow-up runs at augmentation levels L1-L4 on tasks that PASSED canonical. Tests robustness to code transforms. Result files end in `-L1.json` through `-L4.json`. |
| **L0-conditional filter** | Only tasks where ≥1 of 3 canonical samples passed get ablation runs. Saves API budget. |
| **Azure deployment** | Microsoft's hosted GPT-5.4 model. We send API requests to an Azure endpoint, and it returns translated code. |
| **`gpt-5.4-2`** | The actual Azure deployment name (NOT `gpt-5.4`). This is the name Gal's Azure resource uses. |
| **KNOWN_FAIL** | 9 benchmark specs broken on our hardware. Always excluded from eval batches. |
| **`reasoning_effort=medium`** | Tells GPT-5.4 to use medium-level thinking. Already wired in the code. |
| **`--resume`** | Skip tasks whose result files already exist. Protects against re-running expensive API calls. |
| **tmux** | Terminal multiplexer. Long eval runs execute inside tmux sessions so they survive if your SSH disconnects. |

---

## Skills to Load at Session Start

Before doing ANY implementation work, invoke these skills. They guide HOW you work:

```
Skill("andrej-karpathy-skills:karpathy-guidelines")  — Think before coding, surgical changes, simplicity first
```

At verification points:
```
Skill("validate")  — Run waves 1-3 before any git commit
```

At completion:
```
Skill("review")  — Multi-agent code review before final commit
```

---

## Working Directory

**All commands assume you start here:**
```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
```

---

## CRITICAL WARNINGS

### WARNING 1: Never modify result JSONs
Files in `results/evaluation/` are immutable. A pre-commit hook blocks any changes. Only analysis outputs in `results/analysis/` can be regenerated.

### WARNING 2: Never write the API key to any tracked file
The Azure API key must only live in environment variables (`~/.bashrc`). Never put it in code, plans, or committed files.

### WARNING 3: The HANDOFF.md file must not be replaced
An existing `HANDOFF.md` in the project root documents prior session work. Do NOT overwrite it.

### WARNING 4: All phases are idempotent
If any phase crashes mid-run, simply re-execute the same command. `--resume` skips completed tasks and retries ERROR/EXTRACTION_FAIL results. Do NOT delete result files.

---

## Findings From Exploration (What We Discovered)

### Finding 1: Azure endpoint returns 404 (BLOCKER)

The current `AZURE_OPENAI_ENDPOINT` env var points to an old Azure resource:
```
https://galor-m8yvytc2-swedencentral.cognitiveservices.azure.com/...
```
This resource has no `gpt-5.4` deployment. A smoke test confirmed: **404 Resource not found**.

**Resolution:** Gal provided new credentials on 2026-04-25:
- **New endpoint:** `https://galor-mnwjh6xx-norwayeast.cognitiveservices.azure.com/`
- **Deployment name:** `gpt-5.4-2` (NOT `gpt-5.4`)
- **New API key:** provided directly by Gal (do not commit to files)

### Finding 2: Deployment name mismatch in code

The code at `scripts/evaluation/llm_evaluate.py:917` derives the deployment name by stripping the `azure-` prefix:
```python
azure_model = model[len("azure-"):]  # produces "gpt-5.4"
```
But the actual deployment is `gpt-5.4-2`. The Together AI path already solves this with an `api_model` field in `MODEL_REGISTRY` (line 1058). We reuse that pattern for Azure.

### Finding 3: Missing KNOWN_FAIL spec in batch script

`scripts/batch/run_phase3.sh` line 166-175 lists 8 KNOWN_FAIL specs, but `harness/constants.py` has 9. Missing: `rodinia-backprop-opencl`. This would waste API calls on a known-broken spec.

### Finding 4: Environment variable persistence across tmux

`AZURE_OPENAI_ENDPOINT` is in `~/.bashrc` (line 133), but `AZURE_OPENAI_API_KEY` is NOT. The `run_phase3.sh` script launches a tmux session (line 86-89), which starts a fresh bash shell that sources `~/.bashrc`. If the API key isn't in `.bashrc`, the tmux session will crash with `FATAL: AZURE_OPENAI_API_KEY is not set` — even though the pre-launch check (line 41) passes in the calling shell.

### Finding 5: API version consideration

Code uses `api_version="2025-01-01-preview"` (line 927). Gal's sample shows `2024-12-01-preview`. Both are valid Azure OpenAI API versions. The smoke test will verify which works. Fallback instruction included in Step 3 below.

### Finding 6: Everything else is ready

- `MODEL_REGISTRY["azure-gpt-5.4"]` exists with `supports_thinking: True`
- Azure client code injects `reasoning_effort=medium` when thinking=ON (line 954-955)
- Azure client omits `temperature` and `top_p` for thinking-capable models (line 945-947)
- `openai` package v2.28.0 with `AzureOpenAI` class works
- `derive_l0_passers.py` successfully produced Qwen L0 passers
- `run_phase3.sh` canonical/derive/ablation workflow tested end-to-end with Qwen
- No existing `azure-gpt-5.4` result files on disk (no resume-skip risk)
- Analysis scripts (`generate_paper_data.py`, `augmentation_analysis.py`) use `harness/constants.py` for KNOWN_FAIL exclusion — no hardcoded lists to fix there

---

## Implementation Steps

### Step 1: Update `~/.bashrc` with new Azure credentials

**What:** Replace the old Azure endpoint and add the API key to `~/.bashrc` so tmux sessions inherit them.

**File:** `~/.bashrc` (lines 132-133 area)

**Action:** Find the existing `export AZURE_OPENAI_ENDPOINT=...` line and replace it. Add a new line for `AZURE_OPENAI_API_KEY`.

```bash
# Replace the old endpoint (line 133 of ~/.bashrc):
export AZURE_OPENAI_ENDPOINT="https://galor-mnwjh6xx-norwayeast.cognitiveservices.azure.com/"
# Add this line (currently missing from ~/.bashrc):
export AZURE_OPENAI_API_KEY="<paste key from Gal's message — never commit this>"
```

Then reload:
```bash
source ~/.bashrc
```

**Verification:**
```bash
echo "$AZURE_OPENAI_ENDPOINT" | grep -q "norwayeast" && echo "OK: endpoint updated" || echo "FAIL: still old endpoint"
[ -n "$AZURE_OPENAI_API_KEY" ] && echo "OK: API key set (${#AZURE_OPENAI_API_KEY} chars)" || echo "FAIL: API key missing"
```

**Why tmux needs this:** `run_phase3.sh` line 86-89 launches `tmux new-session -d` which starts a fresh bash shell. That shell runs `source ~/.bashrc` automatically. If the env vars aren't in `.bashrc`, the eval will crash inside tmux with `FATAL: AZURE_OPENAI_API_KEY is not set` even though your current terminal has them.

---

### Step 2: Add `api_model` field to MODEL_REGISTRY

**What:** Tell the code that the Azure deployment is named `gpt-5.4-2`, not `gpt-5.4`.

**File:** `scripts/evaluation/llm_evaluate.py` lines 110-117

**Current code:**
```python
    "azure-gpt-5.4": {
        "provider": "azure",
        "supports_thinking": True,
        "notes": "Azure OpenAI GPT-5.4 (Microsoft Foundry GA 2026-03-17; "
                 "requires AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + "
                 "gpt-5.4 deployment name; "
                 "reasoning_effort=medium when --thinking=on)",
    },
```

**Change to:**
```python
    "azure-gpt-5.4": {
        "provider": "azure",
        "supports_thinking": True,
        "api_model": "gpt-5.4-2",
        "notes": "Azure OpenAI GPT-5.4 (Microsoft Foundry GA 2026-03-17; "
                 "requires AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + "
                 "gpt-5.4-2 deployment on norwayeast; "
                 "reasoning_effort=medium when --thinking=on)",
    },
```

**What changed:** Added `"api_model": "gpt-5.4-2"` and updated the notes to reflect the actual deployment name and region.

**Why this pattern:** The Together AI model entry at line 136 already uses `api_model` to map `together-qwen-3.5-397b-a17b` → `Qwen/Qwen3.5-397B-A17B`. Same pattern, different provider.

**Verification:**
```bash
source env_parbench/bin/activate
python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print(MODEL_REGISTRY['azure-gpt-5.4'].get('api_model'))"
# Expected output: gpt-5.4-2
```

---

### Step 3: Update Azure deployment name resolution

**What:** Make the Azure code path check `api_model` first instead of always stripping the `azure-` prefix.

**File:** `scripts/evaluation/llm_evaluate.py` line 917

**Current code:**
```python
        azure_model = model[len("azure-"):]  # e.g. "azure-gpt-5.4" → "gpt-5.4"
```

**Change to:**
```python
        azure_model = MODEL_REGISTRY.get(model, {}).get("api_model") or model[len("azure-"):]
```

**What changed:** The code now checks if `api_model` is set in the registry first. If yes, it uses that (→ `gpt-5.4-2`). If no, it falls back to the old prefix-strip behavior. This is the same pattern used at line 1058 for Together AI.

**Safety note:** This change ONLY affects the `azure-` dispatch branch (which starts at line ~895 with `if provider == "azure"`). The Together/Qwen path is completely separate and untouched.

**Also update the api_version if needed:** The code at line 927 uses `api_version="2025-01-01-preview"`. Gal's sample shows `2024-12-01-preview`. **Leave it as-is for now.** The smoke test in Step 4 will verify. If the smoke test returns a 400 error mentioning `api_version`, change line 927 to:
```python
            api_version="2024-12-01-preview",
```

**Verification:**
```bash
source env_parbench/bin/activate
python3 -c "
from scripts.evaluation.llm_evaluate import MODEL_REGISTRY
model = 'azure-gpt-5.4'
azure_model = MODEL_REGISTRY.get(model, {}).get('api_model') or model[len('azure-'):]
print(f'Resolved deployment name: {azure_model}')
assert azure_model == 'gpt-5.4-2', f'FAIL: got {azure_model}'
print('OK: deployment name resolves correctly')
"
```

---

### Step 4: Add missing KNOWN_FAIL spec to run_phase3.sh

**What:** Add `rodinia-backprop-opencl` to the KNOWN_FAIL_SPECS array so it's excluded from eval batches.

**File:** `scripts/batch/run_phase3.sh` lines 166-175

**Current code (8 entries):**
```bash
KNOWN_FAIL_SPECS=(
    rodinia-kmeans-cuda
    rodinia-mummergpu-cuda
    rodinia-mummergpu-omp
    rodinia-hybridsort-cuda
    rodinia-nn-opencl
    rodinia-kmeans-opencl
    hecbench-stencil1d-omp_target
    hecbench-scan-omp_target
)
```

**Change to (9 entries):**
```bash
KNOWN_FAIL_SPECS=(
    rodinia-kmeans-cuda
    rodinia-mummergpu-cuda
    rodinia-mummergpu-omp
    rodinia-hybridsort-cuda
    rodinia-nn-opencl
    rodinia-kmeans-opencl
    rodinia-backprop-opencl
    hecbench-stencil1d-omp_target
    hecbench-scan-omp_target
)
```

**What changed:** Added `rodinia-backprop-opencl` (line after `rodinia-kmeans-opencl`). Now matches the 9 entries in `harness/constants.py` lines 8-18.

**Verification:**
```bash
# Count entries in both files — should both be 9
grep -c "rodinia-\|hecbench-" scripts/batch/run_phase3.sh | head -1
python3 -c "from harness.constants import EXCLUDED_SPECS; print(len(EXCLUDED_SPECS))"
# Both should print 9

# Verify backprop-opencl is now in the script
grep "backprop-opencl" scripts/batch/run_phase3.sh && echo "OK" || echo "MISSING"
```

---

### Step 5: Smoke test — verify Azure endpoint works end-to-end

**What:** Run a single translation task to confirm the API key, endpoint, deployment name, and reasoning_effort all work before committing to the full evaluation run.

**IMPORTANT:** Do NOT use `run_eval_batch.py` for the smoke test. Use `llm_evaluate.py` directly to avoid `--resume` silently skipping the test if a result file already exists.

**Command:**
```bash
source env_parbench/bin/activate
python3 -c "
from scripts.evaluation.llm_evaluate import call_llm

# Single API call to verify connectivity
response, prompt_tokens, completion_tokens = call_llm(
    model='azure-gpt-5.4',
    system_msg='You are a code translator.',
    messages=[{'role': 'user', 'content': 'Translate this CUDA kernel to OpenMP: __global__ void add(int *a, int *b, int *c, int n) { int i = threadIdx.x + blockIdx.x * blockDim.x; if (i < n) c[i] = a[i] + b[i]; }'}],
    temperature=0.7,
    thinking_enabled=True,
    verbose=True,
)
print(f'Response length: {len(response)} chars')
print(f'Tokens: {prompt_tokens} prompt / {completion_tokens} completion')
print(f'First 200 chars: {response[:200]}')
print('SMOKE TEST PASSED' if prompt_tokens > 0 and len(response) > 50 else 'SMOKE TEST FAILED')
"
```

**Expected output:**
- Verbose log line: `Calling Azure OpenAI deployment=gpt-5.4-2 messages=2`
- Response contains OpenMP code (e.g., `#pragma omp parallel for`)
- `prompt_tokens > 0` (confirms API was called)
- `SMOKE TEST PASSED`

**If it fails with 404:** The deployment name `gpt-5.4-2` isn't found. Double-check `api_model` in Step 2.
**If it fails with 400 mentioning `api_version`:** Change line 927 of `llm_evaluate.py` from `2025-01-01-preview` to `2024-12-01-preview`.
**If it fails with 401:** The API key is wrong. Re-check `~/.bashrc` and re-source.
**If it fails with connection error:** The endpoint URL is wrong. Check `AZURE_OPENAI_ENDPOINT`.

**Burst test (3 rapid calls) — required by monitoring protocol:**
```bash
source env_parbench/bin/activate
for i in 1 2 3; do
  python3 -c "
from scripts.evaluation.llm_evaluate import call_llm
r, pt, ct = call_llm(model='azure-gpt-5.4', system_msg='Test', messages=[{'role':'user','content':'Say OK'}], temperature=0.7, thinking_enabled=True, verbose=False)
print(f'Call $i: {pt}+{ct} tokens, {len(r)} chars')
" || echo "BURST FAIL on call $i"
done
echo "Burst test complete"
```

All 3 should succeed. If any fail, investigate before proceeding.

---

### Step 6: Commit code changes

After Steps 2-4 are verified and smoke test passes:

```bash
# Load the validate skill
# Run /validate (waves 1-3 required)
# Then commit
git add scripts/evaluation/llm_evaluate.py scripts/batch/run_phase3.sh
git commit -m "fix: azure-gpt-5.4 deployment name + backprop-opencl KNOWN_FAIL

- Add api_model='gpt-5.4-2' to MODEL_REGISTRY azure-gpt-5.4 entry
- Use api_model in Azure dispatch path (mirrors Together pattern)
- Add rodinia-backprop-opencl to run_phase3.sh KNOWN_FAIL_SPECS (9th entry)
"
```

---

### Step 7: Run the full canonical evaluation (Phase A)

**What:** Run all 87 non-KNOWN_FAIL specs × 6 directions × 3 samples = ~1,566 API calls at temp=0.7.

**Command:**
```bash
bash scripts/batch/run_phase3.sh canonical azure-gpt-5.4
```

This launches a tmux session named `phase3-canonical`. The script handles:
- 30 batch invocations (6 Rodinia dirs + 18 small-suite dirs + 6 HeCBench dirs)
- KNOWN_FAIL exclusion
- `--resume` (safe to re-run on crash)
- Retry pass for failed batches
- Post-run analysis

**Monitor:**
```bash
tmux attach -t phase3-canonical    # Watch live
# Or check from outside:
tail -5 results/evaluation/azure_gpt_5_4_canonical.log
ls results/evaluation/azure-gpt-5.4/*.json 2>/dev/null | wc -l   # Count results so far
```

**Monitoring protocol (from `.claude/rules/active-gotchas.md`):**
- Check every 5-8 minutes: `tail -10 results/evaluation/azure_gpt_5_4_canonical.log | grep -c ERROR`
- If 5+ consecutive ERRORs → kill tmux: `tmux kill-session -t phase3-canonical`
- Check error rate: if `(ERROR count / total files) > 30%` → warn about API instability
- Wait for 20+ consecutive PASSes before declaring "API stable"
- If `tmux ls` shows no session and `results/evaluation/azure_gpt_5_4_canonical_done.marker` is absent → session died

**Expected duration:** ~2-4 hours (depends on Azure API latency).

**Done marker:** `results/evaluation/azure_gpt_5_4_canonical_done.marker`

**Cost checkpoint (BEFORE proceeding to Step 8):**
After canonical completes, estimate cost:
```bash
source env_parbench/bin/activate
python3 -c "
import json, glob
files = glob.glob('results/evaluation/azure-gpt-5.4/*-s*.json')
total_prompt = total_completion = 0
for f in files:
    try:
        d = json.loads(open(f).read())
        total_prompt += d.get('prompt_tokens', 0)
        total_completion += d.get('completion_tokens', 0)
    except: pass
cost = (total_prompt * 2.50 + total_completion * 15.00) / 1_000_000
print(f'Canonical: {len(files)} files')
print(f'Tokens: {total_prompt:,} prompt + {total_completion:,} completion')
print(f'Estimated cost: \${cost:.2f}')
print(f'Projected total (canonical + ablation): ~\${cost * 2.5:.2f}')
"
```

Review the cost to track spending. There is no hard budget cap, but cost awareness is good practice.

---

### Step 8: Derive L0 passers (Phase B)

**What:** Analyze canonical results to find which (kernel, direction) cells passed at L0 (≥1 of 3 samples passed). These become the input to the ablation.

**Command:**
```bash
bash scripts/batch/run_phase3.sh derive azure-gpt-5.4
```

**Output:** `.planning/eval-selections/l0_passers_azure_gpt_5_4.json`

**Verification:**
```bash
python3 -c "
import json
passers = json.load(open('.planning/eval-selections/l0_passers_azure_gpt_5_4.json'))
print(f'L0 passers: {len(passers)} cells (out of ~522 possible)')
# Sanity: Qwen had 168 passers. GPT-5.4 should be in a similar ballpark.
assert 50 < len(passers) < 400, f'Unexpected count: {len(passers)}'
print('OK: passer count is reasonable')
"
```

---

### Step 9: Run the ablation study (Phase C)

**What:** For every L0-passer cell, run L1, L2, L3, L4 augmentation levels × 1 sample each at temp=0.7.

**Command:**
```bash
bash scripts/batch/run_phase3.sh ablation azure-gpt-5.4
```

Same monitoring protocol as Step 7. Launches tmux session `phase3-ablation`.

**Done marker:** `results/evaluation/azure_gpt_5_4_ablation_done.marker`

---

### Step 10: Verify completeness

After all three phases:

```bash
source env_parbench/bin/activate
python3 -c "
import json, glob

# Count canonical results
canonical = glob.glob('results/evaluation/azure-gpt-5.4/*-s*.json')
print(f'Canonical files: {len(canonical)}')

# Count ablation results
ablation = [f for f in glob.glob('results/evaluation/azure-gpt-5.4/*-L*.json')]
print(f'Ablation files: {len(ablation)}')

# Status breakdown
from collections import Counter
statuses = Counter()
for f in canonical + ablation:
    try:
        d = json.loads(open(f).read())
        statuses[d.get('overall_status', '?')] += 1
    except: statuses['PARSE_ERROR'] += 1

print('Status breakdown:')
for s, n in statuses.most_common():
    print(f'  {s}: {n}')
total = sum(statuses.values())
passed = statuses.get('PASS', 0)
print(f'Total: {total} | PASS: {passed} ({100*passed/total:.1f}%)')
"
```

Then run the analysis pipeline:
```bash
python3 scripts/evaluation/analyze_eval.py \
    --project-root /home/samyak/Desktop/parbench_sam \
    --write-dashboard
```

---

## Files Modified (Summary)

| File | Change | Lines |
|------|--------|-------|
| `~/.bashrc` | Update `AZURE_OPENAI_ENDPOINT`, add `AZURE_OPENAI_API_KEY` | ~132-134 |
| `scripts/evaluation/llm_evaluate.py` | Add `api_model: "gpt-5.4-2"` to registry entry | 110-117 |
| `scripts/evaluation/llm_evaluate.py` | Use `api_model` in Azure deployment name resolution | 917 |
| `scripts/batch/run_phase3.sh` | Add `rodinia-backprop-opencl` to KNOWN_FAIL_SPECS | 166-175 |

Total: 2 files modified, ~5 lines changed. No new files created.

---

## What NOT To Do

1. **Do NOT rename `azure-gpt-5.4` in MODEL_REGISTRY** — the `api_model` field handles the deployment name difference. All downstream code, analysis scripts, and result paths use `azure-gpt-5.4` as the model identifier.
2. **Do NOT modify existing Qwen results** in `results/evaluation/together-qwen-3.5-397b-a17b/`.
3. **Do NOT replace the existing HANDOFF.md** — it documents prior session work.
4. **Do NOT change `temperature=0.7`** — Azure reasoning models ignore it anyway (code silently strips it for `supports_thinking=True` models), but it's recorded in result JSONs for audit trail.
5. **Do NOT run evaluations in git worktrees** — Rodinia submodule is empty there.
6. **Do NOT change spec run args** without reading the actual source's argc check first.

---

## Experiment Parameters (Reference)

### Canonical (Phase A)
| Parameter | Value |
|-----------|-------|
| Sampling | pass@3 (3 samples per cell) |
| Temperature | 0.7 |
| Augmentation | L0 only (no perturbation) |
| Thinking | ON (reasoning_effort=medium) |
| Self-repair | OFF (max_retries=1) |
| Directions | All 6: cuda↔omp, cuda↔opencl, omp↔opencl |
| Specs | 87 non-KNOWN_FAIL |

### Ablation (Phase C)
| Parameter | Value |
|-----------|-------|
| Sampling | pass@1 (1 sample per cell) |
| Temperature | 0.7 |
| Augmentation | L1, L2, L3, L4 |
| Thinking | ON (reasoning_effort=medium) |
| Self-repair | OFF (max_retries=1) |
| Filter | L0-conditional (pass@1-of-any from canonical) |

---

## Architecture Context (How the Code Flows)

```
run_phase3.sh (orchestrator)
  ├── Pre-launch checks (API key, submodule, GPU, tmux)
  ├── Loops over 30 batch invocations
  │   └── run_eval_batch.py (per direction/suite)
  │       ├── Builds task list from manifest.jsonl
  │       ├── Filters by --suite, --kernels, --excluded-specs
  │       └── For each task:
  │           └── llm_evaluate.py:evaluate_translation()
  │               ├── Reads source spec JSON
  │               ├── Reads target spec JSON
  │               ├── Calls call_llm() with source code
  │               │   └── Azure dispatch (provider == "azure")
  │               │       ├── Resolves deployment: api_model → "gpt-5.4-2"
  │               │       ├── Injects reasoning_effort=medium
  │               │       ├── Strips temperature (thinking model)
  │               │       └── Returns translated code
  │               ├── Extracts code from LLM response
  │               ├── Writes code to disk, builds, runs
  │               └── Verifies output against oracle
  ├── Retry pass for failed batches
  ├── Post-run analyze_eval.py
  └── Writes done marker
```

---

## Estimated Timeline

| Phase | Duration | API Calls | Est. Cost |
|-------|----------|-----------|-----------|
| Steps 1-6 (setup + commit) | ~30 min | 4 (smoke + burst) | ~$0.05 |
| Step 7 (canonical) | ~2-4 hours | ~1,566 | ~$400-500 |
| Step 8 (derive) | ~1 min | 0 | $0 |
| Step 9 (ablation) | ~1-3 hours | ~670-2000* | ~$150-350 |
| Step 10 (verify) | ~5 min | 0 | $0 |

*Ablation count depends on how many L0-passer cells exist.
