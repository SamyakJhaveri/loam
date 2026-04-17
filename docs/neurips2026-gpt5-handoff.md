# NeurIPS 2026 — GPT-5.4 Campaign Handoff Runbook (Le)

**Audience:** Le (external collaborator running the GPT-5.4 evaluation stream)
**Last updated:** 2026-04-17
**Status:** Phase 2 complete; Phase 3 launch pending Gal sign-off on budget overshoot

---

## 1. Context

ParBench is a benchmark framework for evaluating LLM-based parallel code translation
(CUDA ↔ OpenMP ↔ OpenCL). The NeurIPS 2026 submission (Datasets & Benchmarks track,
deadline May 1, 2026) uses a **canonical + L0-conditional ablation** experiment design:

- **Canonical (Phase 3A):** For each (source, target) kernel pair across all 5 benchmark
  suites and 6 directions, run 3 independent samples at L0 (no augmentation), temperature 0.7,
  thinking ON. This is pass@3 to estimate translation success rate.
- **L0-conditional ablation (Phase 3C):** For cells where ≥1 of 3 canonical samples
  passed ("pass@1-of-any"), run 1 sample at each augmentation level L1–L4 to measure
  robustness degradation under progressively aggressive AST transforms.

**Why Le runs GPT-5.4 on his own machine:**
Le has Azure account ownership and dedicated throughput (TPM quota) for GPT-5.4.
Running on Le's machine avoids quota conflicts with Samyak's Azure account and lets both
model streams (Qwen on Samyak's Linux GPU machine, GPT-5.4 on Le's machine) run in
parallel, halving Phase 3 wall-clock time.

**Two-track execution:**
- Track A (Le): GPT-5.4 (`azure-gpt-5.4`) — canonical + ablation on Le's clone of this repo.
- Track B (Samyak): Qwen 3.5 397B (`together-qwen-3.5-397b-a17b`) — canonical + ablation
  on the Linux GPU machine at `/home/samyak/Desktop/parbench_sam`.
- Phase B (`derive_l0_passers.py`) runs on whichever machine produced each canonical set.

**Cost ceiling:** $559 tentative ceiling for the full GPT-5.4 campaign (pending Gal sign-off
during Phase 3 kickoff). Hard abort threshold: $600 (ROADMAP Phase 3 SC-5). Monitor spend
against the cost model in Section 7 after each canonical batch.

---

## 2. Repo Setup

No local CUDA compilation is required — GPT-5.4 inference happens on Azure; Le's machine
only runs the Python evaluation pipeline. No submodule initialization needed.

```bash
git clone https://github.com/SamyakJhaveri/parbench_sam.git
cd parbench_sam
python3 -m venv env_parbench
source env_parbench/bin/activate
pip install -r requirements-lock.txt
```

Verify the install:

```bash
python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print('registry OK')"
```

---

## 3. Secrets Checklist

The pipeline reads Azure credentials from environment variables. Set these before running
any evaluation command:

```bash
export AZURE_OPENAI_API_KEY="..."          # Le's Azure OpenAI API key (do NOT share)
export AZURE_OPENAI_ENDPOINT="https://..." # Le's Azure OpenAI endpoint URL
# The deployment name must be "gpt-5.4" — this matches the MODEL_REGISTRY key "azure-gpt-5.4"
# via the existing prefix-strip convention (azure- is stripped to get the deployment name).
```

**Security rules:**
- Never commit these values to the repo.
- Never hardcode them in any script.
- Verify they are set before running any paid command: `echo $AZURE_OPENAI_API_KEY | head -c 8` (shows first 8 chars only).

---

## 4. Pre-Flight Verification

Run ALL of these commands before making any paid API call. Each must exit 0.
If any fails, the runbook is stale — pull `main` and retry.

```bash
# 4a. Verify CLI surface: --thinking, --task-list, --dry-run flags exist
python3 scripts/evaluation/run_eval_batch.py --help | grep -Eq -- '--thinking|--task-list|--dry-run' \
  && echo "CLI flags OK" || echo "FAIL: pull main and retry"

# 4b. Verify azure-gpt-5.4 is in MODEL_REGISTRY with supports_thinking=True
python3 -c "
from scripts.evaluation.llm_evaluate import MODEL_REGISTRY
assert 'azure-gpt-5.4' in MODEL_REGISTRY, 'azure-gpt-5.4 missing from registry'
assert MODEL_REGISTRY['azure-gpt-5.4']['supports_thinking'] is True, 'supports_thinking must be True'
print('MODEL_REGISTRY OK')
"

# 4c. Verify derive_l0_passers.py is available
python3 scripts/evaluation/derive_l0_passers.py --help && echo "derive_l0_passers OK"

# 4d. Zero-cost dry-run smoke (one direction, one kernel — no API call)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-omp \
  --models azure-gpt-5.4 \
  --augment-levels 0 --num-samples 1 \
  --temperature 0.7 --thinking on \
  --dry-run --project-root . \
  && echo "dry-run smoke OK"
```

If step 4d exits non-zero, do NOT proceed. Diagnose before spending any budget.

---

## 5. Phase 3 Stage Commands

Run each stage in order. Use `--resume` so interrupted runs can be continued without
re-running completed tasks. Result JSONs are append-only and never overwritten.

### Stage A — Canonical (per suite × per direction)

Repeat for each `<suite>` ∈ {rodinia, xsbench, rsbench, mixbench, hecbench} and
each `<dir>` ∈ {cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp}.

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite <suite> \
  --direction <dir> \
  --models azure-gpt-5.4 \
  --thinking on \
  --temperature 0.7 \
  --augment-levels 0 \
  --num-samples 3 \
  --project-root . \
  --resume -v
```

**Note on `--thinking on`:** This flag sets `reasoning_effort=medium` in the Azure API
call (D-08 in `.planning/phases/02-llm-eval-testing/02-CONTEXT.md`). It is hardcoded as
`reasoning_effort=medium` inside the pipeline — this is NOT a user-tunable parameter.
Do not attempt to pass `reasoning_effort` directly; use `--thinking on`.

Results land in: `results/evaluation/azure-gpt-5.4/`

### Stage B — Derive L0 Passers

After ALL canonical batches complete across all suites and directions, run:

```bash
python3 scripts/evaluation/derive_l0_passers.py \
  --canonical-dir results/evaluation/azure-gpt-5.4/ \
  --model azure-gpt-5.4 \
  --out l0_passers_azure-gpt-5.4.json
```

This produces `l0_passers_azure-gpt-5.4.json` — a flat list of (source_spec, target_spec)
pairs where ≥1 of 3 canonical samples passed (pass@1-of-any filter, D-18). Only these
cells proceed to ablation.

### Stage C — Ablation (per direction)

Repeat for each `<dir>` used in Stage A:

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --task-list l0_passers_azure-gpt-5.4.json \
  --models azure-gpt-5.4 \
  --thinking on \
  --temperature 0.7 \
  --augment-levels 1 2 3 4 \
  --num-samples 1 \
  --direction <dir> \
  --project-root . \
  --resume -v
```

The `--task-list` flag bypasses manifest enumeration and runs only the L0-passing cells.
The `--augment-levels 1 2 3 4` override replaces the `augment_level: 0` placeholder in
the passer JSON.

---

## 6. Output Layout + Result JSON Schema

### File paths

| Stage | Pattern |
|-------|---------|
| Canonical L0 (sample n of 3) | `results/evaluation/azure-gpt-5.4/{src}-to-{tgt}-s{n}.json` |
| Ablation L1–L4 | `results/evaluation/azure-gpt-5.4/{src}-to-{tgt}-L{level}.json` |
| Passer list | `l0_passers_azure-gpt-5.4.json` (at repo root, not in results/) |

### Key result JSON fields

| Field | Type | Description |
|-------|------|-------------|
| `overall_status` | str | `PASS` / `BUILD_FAIL` / `RUN_FAIL` / `VERIFY_FAIL` / `ERROR` / `SKIP` |
| `model` | str | `"azure-gpt-5.4"` |
| `augment_level` | int | 0 for canonical; 1–4 for ablation |
| `num_samples` | int | 3 for canonical; 1 for ablation |
| `sample_id` | int | Sample index (0-based) within the pass@k batch |
| `temperature` | float | 0.7 |
| `thinking_enabled` | bool | `true` (always ON for Phase 3) |
| `prompt_tokens` | int | LLM input token count (for cost tracking) |
| `completion_tokens` | int | LLM output token count including reasoning tokens |
| `source_spec` | str | e.g. `"rodinia-bfs-cuda"` |
| `target_spec` | str | e.g. `"rodinia-bfs-omp"` |

Full schema reference: `.claude/rules/evaluation.md §"Result File Layout"`

### Passer JSON schema (D-19)

```json
[
  {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "augment_level": 0},
  ...
]
```

`augment_level: 0` is a placeholder; Stage C overrides it via `--augment-levels 1 2 3 4`.
Full schema reference: `.planning/phases/02-llm-eval-testing/02-CONTEXT.md D-19`

---

## 7. Cost Model

**Azure GPT-5 standard tier** (Azure deployment name: `gpt-5.4`, `reasoning_effort=medium`):

| Metric | Rate | Source |
|--------|------|--------|
| Input tokens (< 272K context) | **$2.50 per 1M tokens** | azure.microsoft.com/pricing/details/azure-openai/ |
| Output tokens (incl. reasoning) | **$15.00 per 1M tokens** | Same (verified 2026-04-17) |
| Batch API input | $1.25 / 1M | Not used in Phase 3 |
| Batch API output | $7.50 / 1M | Not used in Phase 3 |

**Important:** Reasoning tokens at `reasoning_effort=medium` are billed as output tokens
(no separate rate). Reasoning can inflate output tokens 2–5× depending on problem difficulty.
ParBench prompts are ~5k tokens, well under the 272K threshold — the $2.50/$15.00 tier applies.

**Per-sample cost estimate** (5k prompt + 20k output, no reasoning inflation):
- Input: 5,000 × $2.50/1M = $0.0125
- Output: 20,000 × $15.00/1M = $0.30
- **Total per sample ≈ $0.3125**

**Worst-case per sample** (reasoning doubles output → 40k output tokens):
- Output: 40,000 × $15.00/1M = $0.60
- **Worst-case ≈ $0.6125 per sample**

**Budget:**
- Tentative campaign ceiling: **$559** (pending Gal sign-off during Phase 3 kickoff)
- Hard abort threshold: **$600** (ROADMAP Phase 3 SC-5 — stop immediately if estimated spend reaches $600)

**Monitoring:** After each canonical batch, compute running spend:
```bash
python3 -c "
import json, glob
total = 0.0
for f in glob.glob('results/evaluation/azure-gpt-5.4/*.json'):
    d = json.load(open(f))
    total += (d.get('prompt_tokens', 0) or 0) * 2.50 / 1_000_000
    total += (d.get('completion_tokens', 0) or 0) * 15.00 / 1_000_000
print(f'Estimated spend so far: \${total:.2f}')
"
```

**Resume protocol:** `--resume` skips tasks whose result JSONs already exist (append-only).
Result JSONs are never overwritten. If throttled on TPM quota, wait and retry — the launcher
handles backoff automatically.

---

## 8. Artifact Delivery

After all three stages complete (Canonical + Derive + Ablation), tar the result directory
and send it to Samyak:

```bash
tar czf azure-gpt-5.4-results-$(date +%Y%m%d).tar.gz results/evaluation/azure-gpt-5.4/
```

Send `azure-gpt-5.4-results-YYYYMMDD.tar.gz` to Samyak (email or file share).

**Samyak's receive protocol:**
1. Extract into the main machine's repo: `tar xzf azure-gpt-5.4-results-*.tar.gz`
2. Run `/validate` waves 1–3 to verify no schema violations.
3. Commit to `main` with message referencing the date and model.

**No named branches. No cross-repo merges.** Delivery is the tarball only.
Samyak pastes the result directory tree into the main repo and commits it.

---

*This runbook is generated by Plan 02-08 of the ParBench NeurIPS 2026 Phase 2 plan sequence.*
*For pipeline questions, consult `.planning/phases/02-llm-eval-testing/02-CONTEXT.md`.*
*For experiment design questions, consult `docs/neurips2026-experiment-plan.md §2.4`.*
