# Phase 3 Launch Manifest

**Version:** S7b (finalized 2026-04-19)
**HEAD at launch-manifest freeze:** `9b1a1f5` + S7b commits (spec downgrades, audit, manifest, review)
**Pipeline validation:** S7 live-smoke v3 (4/4 PASS, $0.63, artifacts at `/tmp/s7-artifacts-v3/`)
**Oracle audit:** `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md` (8 specs downgraded, 88/88 sweep PASS)

> Authoritative command sheet for Phase 3 canonical + L0-conditional ablation across `together-qwen-3.5-397b-a17b` (Track A) and `azure-gpt-5.4` (Track B). Do **not** modify command text below without re-running the verifier (`/tmp/s7b-manifest-verify.py`).

---

## 1. Entry gate (MUST be satisfied before any command in §4–§7 runs)

| Precondition | Verification |
|---|---|
| HEAD contains S7b commits | `git log --oneline -6` |
| `/validate` waves 1-3 PASS at HEAD | `.validation_passed` sentinel present, <30 min old |
| Spec sweep clean | `python3 scripts/spec_tools/run_verify_sweep.py --project-root $PWD --exclude-known-fail --jobs 4` → `PASS 88/88` |
| Divergence tests PASS | `python3 -m pytest tests/test_oracle_divergence.py -q` → 6 passed |
| Smoke artifacts intact (optional) | `ls /tmp/s7-artifacts-v3/` → 6 basetemp dirs present; if missing, fallback recipe in §10 |
| Gal budget re-approval received | PHASE-3-BLOCKER — see `.planning/STATE.md` Launch Blockers |
| Le's `azure-gpt-5.4` deployment provisioned on Le's node | PHASE-3-BLOCKER |
| TPM quota sufficient | PHASE-3-BLOCKER |

If any row is not satisfied, stop. Do not run Phase 3 commands.

---

## 2. Decision blocks (binding; override the `run_eval_batch.py` defaults)

### D-RESUME — `--resume` contract and mixed-temperature resume guardrail

The `run_eval_batch.py` resume key is `results/evaluation/{model}/{src}-to-{tgt}-L{n}-s{k}.json`. **Temperature, seed, `thinking`, and `num_samples` are NOT in the key.** `--resume` skips any task whose result file already exists regardless of the flags that produced it.

Mixed-temperature corpus risk: resuming a canonical stream (temp=0.7) over files written by a greedy run (temp=0.0) silently leaves greedy samples in a canonical corpus. Before any `--resume` invocation over pre-existing files:

```bash
# Guardrail: confirm the existing corpus matches the temperature you are about to resume at.
jq -r '.temperature' results/evaluation/{MODEL}/**/*.json 2>/dev/null | sort -u
# Canonical stream must print exactly:  0.7
# Greedy ablation must print exactly:    0.0
# If you see two values, the corpus is mixed — stop and investigate.
```

Hook-level enforcement: `.claude/hooks/protect-cuda-omp-results.sh:65-76` blocks `run_eval_batch.py` in `cuda-to-omp` or `omp-to-cuda` directions without `--resume`. All §4–§7 commands therefore always carry `--resume`.

### D-RETRIES — `--max-retries 1` is mandatory, not default-implicit

`run_eval_batch.py --max-retries` defaults to `1`. Always state `--max-retries 1` explicitly in Phase 3 commands so the assumption is audit-visible and drift-resistant. `1` = zero-shot-with-one-attempt — no iterative repair, which preserves pass@k semantics. Do **not** raise this value for Phase 3.

### D-DIRECTIONS — one direction per `run_eval_batch.py` invocation

`run_eval_batch.py` accepts a single `--direction SRC-to-TGT`. Launch cuda-to-omp and omp-to-cuda as separate tmux sessions (§4, §5, §7). Each direction has its own completion log and failure playbook.

### D-BUDGET — recomputation, not restatement

Gal's approval for gpt-5.3-chat baseline was **$559 at pre-refresh pricing (2026-04-17)**. After retargeting to `azure-gpt-5.4` (commit `44c6222`) and Azure Foundry price-sheet refresh, the recomputed Phase 3 budget is **~$848** (gpt-5.4 at $2.50 input / $15 output per 1M tokens). This is a **recomputation requiring fresh sign-off** per `feedback_no_silent_budget_restatement`. Do not phrase as "Gal approved $848". Treat the prior $559 as a ceiling for gpt-5.3-chat only.

---

## 3. Reusable shell variables (copy once at the top of every tmux session)

```bash
PROJECT_ROOT=/home/samyak/Desktop/parbench_sam
cd "$PROJECT_ROOT" && source env_parbench/bin/activate
QWEN=together-qwen-3.5-397b-a17b
AZURE=azure-gpt-5.4
```

Verify before continuing:

```bash
python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; assert '$QWEN' in MODEL_REGISTRY and '$AZURE' in MODEL_REGISTRY; print('registry OK')"
```

---

## 4. Track A — Qwen canonical (pass@3, L0, temp=0.7, thinking on)

**Rationale:** D-EXP-01 (canonical = pass@3 at L0 with temp=0.7 and thinking=on) per memory `project_neurips_experiment_design`. Qwen is on Together AI; `--thinking on` flips `enable_thinking=True` in `extra_body.chat_template_kwargs`. Seed is deterministic per `(source,target,sample_id)` via `_derive_llm_seed` at `llm_evaluate.py:312-323` — no `--seeds` flag is required or accepted.

### 4.1 cuda-to-omp

```bash
tmux new-session -d -s phase3-qwen-c2o "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction cuda-to-omp \
    --models together-qwen-3.5-397b-a17b \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a .planning/phases/03-oracle-framework/phase3-qwen-c2o.log"
tmux attach -t phase3-qwen-c2o    # detach with C-b d
```

### 4.2 omp-to-cuda

```bash
tmux new-session -d -s phase3-qwen-o2c "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction omp-to-cuda \
    --models together-qwen-3.5-397b-a17b \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a .planning/phases/03-oracle-framework/phase3-qwen-o2c.log"
tmux attach -t phase3-qwen-o2c
```

Swap `--suite rodinia` for `--suite hecbench`, `--suite xsbench`, `--suite rsbench`, `--suite mixbench` to extend Track A to the remaining four suites. One invocation per (suite × direction). Directions with no eligible spec pairs in a suite exit fast.

---

## 5. Track B — Azure gpt-5.4 canonical (pass@3, L0, temp=0.7, thinking on)

**Rationale:** Same experiment cell as Track A, different model. `azure-gpt-5.4` has `supports_thinking=True` in `MODEL_REGISTRY`. The caller passes `--temperature 0.7` and `--thinking on`; the wrapper at `llm_evaluate.py:940-942` strips `temperature` and `top_p` from the Azure Responses-API call and instead injects `reasoning_effort="medium"` at `:945-950` (landed in commit `54dc988`). This manifest states the behavior; it does not re-document the fix.

### 5.1 cuda-to-omp

```bash
tmux new-session -d -s phase3-azure-c2o "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction cuda-to-omp \
    --models azure-gpt-5.4 \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a .planning/phases/03-oracle-framework/phase3-azure-c2o.log"
```

### 5.2 omp-to-cuda

```bash
tmux new-session -d -s phase3-azure-o2c "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction omp-to-cuda \
    --models azure-gpt-5.4 \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a .planning/phases/03-oracle-framework/phase3-azure-o2c.log"
```

Extend to other suites by swapping `--suite`, as in §4.

---

## 6. Ablation — L0-passers × augment levels 0-4 (pass@1, greedy, thinking on)

**Rationale:** D-16..D-21 (`project_ablation_filter` memory) — pass@1-of-any filter: the cell `(source,target)` qualifies for the ablation set iff `≥1` of the 3 canonical samples passes at L0. Per-cell, pass@1 at each of L0..L4 is then run with `--num-samples 1 --temperature 0.0`. Greedy + single sample so every augmentation level produces exactly one comparable data point.

### 6.1 Derive passer set per model × direction

`derive_l0_passers.py` gained a `--direction` filter on 2026-04-19 (S7c; commit pending). The flag extracts source/target API from the last hyphen-delimited segment of each `unique_id` (safe: no `parallel_api` value in `manifest.jsonl` contains a `-`). When provided, the output passer file is scoped to one direction; the legacy mixed-direction behavior (`--direction` omitted) is preserved but **no longer recommended** for Phase 3 — use one passer file per `(model, direction)` cell to keep the ablation batch explicit. `run_eval_batch.py:190-197` (`_build_tasks_from_task_list`) retains its direction-suffix filter as a safety net; with direction-scoped passer files it becomes a no-op.

```bash
# Four passer files: model × direction.
python3 -m scripts.evaluation.derive_l0_passers \
    --canonical-dir results/evaluation/together-qwen-3.5-397b-a17b \
    --model together-qwen-3.5-397b-a17b \
    --direction cuda-to-omp \
    --out .planning/eval-selections/l0_passers_qwen_c2o.json

python3 -m scripts.evaluation.derive_l0_passers \
    --canonical-dir results/evaluation/together-qwen-3.5-397b-a17b \
    --model together-qwen-3.5-397b-a17b \
    --direction omp-to-cuda \
    --out .planning/eval-selections/l0_passers_qwen_o2c.json

python3 -m scripts.evaluation.derive_l0_passers \
    --canonical-dir results/evaluation/azure-gpt-5.4 \
    --model azure-gpt-5.4 \
    --direction cuda-to-omp \
    --out .planning/eval-selections/l0_passers_azure_c2o.json

python3 -m scripts.evaluation.derive_l0_passers \
    --canonical-dir results/evaluation/azure-gpt-5.4 \
    --model azure-gpt-5.4 \
    --direction omp-to-cuda \
    --out .planning/eval-selections/l0_passers_azure_o2c.json
```

**Pre-consumption sanity checks:**

```bash
# D-21: cells with <3 samples warn; non-fatal but must be reviewed before ablation runs.
for f in l0_passers_qwen_c2o.json l0_passers_qwen_o2c.json \
         l0_passers_azure_c2o.json l0_passers_azure_o2c.json; do
    echo "=== $f ==="
    jq -r '.[] | (.source_spec|split("-")|.[-1]) + "-to-" + (.target_spec|split("-")|.[-1])' \
        ".planning/eval-selections/$f" | sort | uniq -c
done
```

### 6.2 Run ablation (L0..L4 × --task-list passers)

```bash
# Qwen cuda-to-omp — consumes direction-scoped passer file.
tmux new-session -d -s phase3-qwen-abl-c2o "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
python3 scripts/evaluation/run_eval_batch.py \
    --task-list .planning/eval-selections/l0_passers_qwen_c2o.json \
    --direction cuda-to-omp \
    --models together-qwen-3.5-397b-a17b \
    --augment-levels 0 1 2 3 4 \
    --num-samples 1 \
    --temperature 0.0 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a .planning/phases/03-oracle-framework/phase3-qwen-abl-c2o.log"
```

Mirror for the remaining three cells: flip `--direction`, swap the `--task-list` path (`l0_passers_qwen_o2c.json`, `l0_passers_azure_c2o.json`, `l0_passers_azure_o2c.json`), rename tmux session + log, and swap `--models` for azure. `--suite` is **not** passed with `--task-list` — the task list itself enumerates cells (mutex per argparse `:477-499`). With direction-scoped passer files the `_build_tasks_from_task_list` direction guard is a no-op safety net; no skip warnings are expected.

---

## 7. Analyze + dashboard refresh (after each suite × direction finishes)

```bash
python3 scripts/evaluation/analyze_eval.py \
    --project-root $PROJECT_ROOT \
    --output-dir results/evaluation
python3 scripts/generate_viz_data.py --project-root $PROJECT_ROOT
```

Produces `results/evaluation/eval_summary.{json,md}`, updated dashboard JS. `analyze_eval.py` already tolerates the new `translation_type`, `verification_mode`, `seed`, `top_p`, `thinking_enabled`, `num_samples` top-level fields (per `known-issues.md` 2026-04-17/18 bumps).

---

## 8. Paste-readiness verifier (run BEFORE launch)

The manifest ships with a committed static checker that asserts every `--<flag>` appears in `run_eval_batch.py`'s argparse, every model ID is in `MODEL_REGISTRY`, every `cuda-to-omp`/`omp-to-cuda` command carries `--resume`, and every `run_eval_batch.py` block explicitly states `--max-retries 1`.

Location: `.planning/phases/03-oracle-framework/tools/verify_launch_manifest.py` (committed in S7b).

```bash
python3 .planning/phases/03-oracle-framework/tools/verify_launch_manifest.py   # exits 0 on PASS
```

If it exits non-zero, fix the manifest before launching.

---

## 9. Budget recomputation (PHASE-3-BLOCKER tier — not a restatement)

Per `feedback_no_silent_budget_restatement`:

| Line | Value | Source |
|---|---|---|
| Gal-approved ceiling (gpt-5.3-chat, pre-refresh pricing, 2026-04-17) | **$559** | Memory `project_budget_overshoot` |
| Recomputation after `azure-gpt-5.4` retarget + Foundry price refresh | **~$848** | Memory `project_budget_math_2026_04_17` — superseded by gpt-5.3-chat at $784, now superseded by gpt-5.4 at $848 |
| Approval status for $848 | **Pending** | Needs fresh Gal sign-off before Track B launches |
| Sample inventory assumed | ~1566 canonical + ~1148 ablation (Track A+B combined) | Derived from NeurIPS experiment design × 5-suite scope; revalidate when Track A finishes and ablation passer counts are final |

Action: Do not launch Track B until fresh approval is recorded against the `$848` figure.

---

## 10. Failure / abort / resume playbook

### Mid-run abort

1. `tmux attach -t <session>` → `C-c` to abort the Python process cleanly (writes any partial result file in progress).
2. `tmux kill-session -t <session>` once aborted.
3. Inspect last completed task:

```bash
ls -lt results/evaluation/together-qwen-3.5-397b-a17b/*.json | head -5
```

### Resume (same flags, same model, same direction)

Re-run the original `tmux new-session -d -s <session> "..."` line from §4/§5/§6 unchanged. `--resume` will skip existing result files. Before re-launching, run the D-RESUME mix-temp guardrail (§2).

### Token-burn audit (after each session)

```bash
jq '.prompt_tokens, .completion_tokens' results/evaluation/{MODEL}/*.json \
    | awk 'NR%2{p+=$0;next}{c+=$0} END{print "prompt:",p,"completion:",c}'
```

### Smoke artifacts wiped from `/tmp/`

Fallback per S7b plan-reviewer ADV-2: re-run smoke v3 (~10 min, ~$0.63) or consult `.planning/phases/03-oracle-framework/04-S7-LIVE-v3.log` live-smoke summary (already captured on disk).

---

## 11. Source-of-truth references

| What | Where |
|------|------|
| argparse flags | `scripts/evaluation/run_eval_batch.py:465-606` (`_build_parser`) |
| `MODEL_REGISTRY` | `scripts/evaluation/llm_evaluate.py:69-134` (azure-gpt-5.4 at `:105-112`, qwen at `:128-133`) |
| Seed derivation | `scripts/evaluation/llm_evaluate.py:312-323` (`_derive_llm_seed`; no `--seeds` flag) |
| Azure reasoning temp gate | `scripts/evaluation/llm_evaluate.py:940-942` (landed 54dc988) |
| Ablation filter tool | `scripts/evaluation/derive_l0_passers.py` |
| CUDA↔OMP hook | `.claude/hooks/protect-cuda-omp-results.sh:65-76` |
| Canonical config doc | `docs/neurips2026-experiment-plan.md §2.4` + memory `project_neurips_experiment_design` |
| Oracle audit | `.planning/phases/03-oracle-framework/04-S7b-ORACLE-AUDIT.md` |
| Live smoke v3 | `.planning/phases/03-oracle-framework/04-S7-LIVE-v3.log` |
| Phase blockers | `.planning/STATE.md` Launch Blockers section |
