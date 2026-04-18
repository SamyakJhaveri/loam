# Phase 2: LLM Eval Testing — Context

**Gathered:** 2026-04-16
**Status:** Approved by user; ready for `/gsd-plan-phase 2`

## Context

Phase 1 (Pipeline Testing & Uniformity) is complete. The 4-phase NeurIPS 2026 roadmap now moves to Phase 2, which prepares the **evaluation pipeline** for the Gal-approved canonical + L0-conditional ablation design (`docs/neurips2026-experiment-plan.md §2.4`). Phase 2 is **code + tests only** — it does not launch any evaluation run. Launch (Phase A of Phase 3) is gated on Gal's GPT budget sign-off (verified at $559 at pre-refresh pricing, 2026-04-17) and Le's Azure `gpt-5.3-chat` deployment/TPM confirmation; the deployment name was resolved 2026-04-17 (placeholder `gpt-5.4` → `gpt-5.3-chat`), TPM quota still to be confirmed by Le.

**Goal (from ROADMAP.md):** `run_eval_batch.py` can execute end-to-end for 1 kernel per suite with both `together-qwen-3.5-397b-a17b` and `azure-gpt-5.3-chat` under the canonical config (pass@3, L0, temp=0.7, thinking=ON, reasoning_effort=medium, self-repair=OFF), and the L0-conditional ablation launcher can consume a task list produced by `derive_l0_passers.py`.

**Why now:** Launching canonical streams against an un-verified `azure-gpt-5.3-chat` registry entry, or launching ablation without a tested passer-derivation script, is the failure mode the roadmap is designed to prevent. Phase 2 is the dry-run that makes Phase 3 launch-safe.

---

## Phase Boundary (domain)

Additive, non-redesigning changes to the evaluation pipeline that enable the new experiment design without touching harness, augmentation, pass@k estimator, result schema, manifest, or spec JSONs. Deliverables:

1. `MODEL_REGISTRY` entry for `azure-gpt-5.3-chat` in `scripts/evaluation/llm_evaluate.py`
2. `supports_thinking: bool` capability field added to every `MODEL_REGISTRY` entry (schema extension)
3. New `--thinking on|off` CLI flag on `llm_evaluate.py` and `run_eval_batch.py`, default `on`. For Qwen: flips `extra_body.chat_template_kwargs.enable_thinking`. For Azure reasoning models: maps to `reasoning_effort="medium"` (on) / omitted (off). Non-thinking-capable models: flag is a no-op.
4. Purge of `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` from `MODEL_REGISTRY` and all ParBench-owned scripts/docs/tests (result JSONs on disk stay untouched per `feedback_protect_cuda_omp_results` memory).
5. New `scripts/evaluation/derive_l0_passers.py` — ingests canonical result dir, emits `l0_passers_{model}.json` with cells where ≥1 of 3 samples passed at L0 (pass@1-of-any).
6. New `--task-list <json>` flag on `run_eval_batch.py` — consumes passer JSON, runs only listed cells (bypasses manifest enumeration).
7. End-to-end smoke verification: `--dry-run` for all 5 suites, then real LLM calls on 1 kernel per suite × 2 models × cuda-to-omp direction (≈30 real samples, <$5).

---

## Implementation Decisions (decisions)

### MODEL_REGISTRY (azure-gpt-5.3-chat entry)

- **D-01:** New entry key is `azure-gpt-5.3-chat`. Deployment name is resolved by the existing prefix-strip pattern at `llm_evaluate.py:877` (`model[len("azure-"):]` → `"gpt-5.3-chat"`). The placeholder `"gpt-5.4"` was replaced with the verified deployment name `"gpt-5.3-chat"` on 2026-04-17. Do **not** introduce an `api_model` override for Azure (Azure already uses prefix-strip resolution; matching the existing `azure-gpt-4.1` entry). Note: `api_model` exists elsewhere in the registry (e.g. Together-AI Qwen at `llm_evaluate.py:112`, where the displayed key and API model ID differ); symmetry here is scoped to the Azure entries only.
- **D-02:** Entry fields: `{"provider": "azure", "supports_thinking": True, "notes": "Azure OpenAI GPT-5.3 Chat reasoning deployment (Le) — requires AZURE_OPENAI_API_KEY+AZURE_OPENAI_ENDPOINT"}`. No secret values in the registry.
- **D-03:** The entry is added **before** the `gpt-4.1` purge (D-11) so the registry is never empty of Azure entries mid-commit. Order: 02-01 (add gpt-5.3-chat, originally placeholder gpt-5.4) → 02-04 (purge gpt-4.1).

### `supports_thinking` capability schema

- **D-04:** New required field `supports_thinking: bool` added to every MODEL_REGISTRY entry. Marked `True` for: `azure-gpt-5.3-chat`, `o3-2025-04-16`, `o4-mini-2025-04-16`, `together-qwen-3.5-397b-a17b`. Marked `False` for: Claude models, `gpt-4o`, `gemini-2.5-*` (Flash-Lite confirmed no thinking; Flash uses `reasoning_effort=none` as belt-and-suspenders per `known-issues-archive.md`), `groq-llama-3.3-70b-versatile`. **Ordering note:** Plan 02-02 (capability field) runs **before** plan 02-04 (purge), so at the moment of 02-02 the purged entries (`gpt-4.1-2025-04-14`, `azure-gpt-4.1`) still exist in the registry — they must receive `supports_thinking=False` in 02-02 and are then removed by 02-04. The enumeration above lists only post-purge survivors; the transient 02-02 entries for gpt-4.1-* are implied by "every entry" and are cleaned up in 02-04.
- **D-05:** The capability field is the **single source of truth** for "can we toggle thinking." `model.startswith(...)` string checks for thinking-related branching are disallowed — all branches consult `MODEL_REGISTRY[model]["supports_thinking"]`.

### `--thinking on|off` CLI flag

- **D-06:** Flag lives on both `llm_evaluate.py` (single-task) and `run_eval_batch.py` (batch). `run_eval_batch.py` passes the value through to each `evaluate_translation()` call.
- **D-07:** Default: `on` (matches canonical config; flipping Qwen's prior default of `enable_thinking=False` → `True`).
- **D-08:** Semantics:
  - Qwen (`supports_thinking=True`, provider=together): on → `extra_body={"chat_template_kwargs": {"enable_thinking": True}}`; off → `enable_thinking: False`.
  - Azure reasoning (`supports_thinking=True`, provider=azure): on → inject `reasoning_effort="medium"` kwarg into `client_az.chat.completions.create(...)` at `llm_evaluate.py:905`; off → omit the kwarg.
  - Other (`supports_thinking=False`): flag is a no-op; log at DEBUG level that the flag was ignored.
- **D-09:** Result JSONs gain **two new top-level fields**: `thinking_enabled: bool` (resolved thinking state, derived at call time from the flag × capability) and `num_samples: int` (the k in pass@k for the batch that produced this result). Existing top-level fields (`sample_id`, `temperature`, `augment_level`, `model`, `overall_status`, etc.) are unchanged. The schema bump is documented in `.claude/rules/evaluation.md` as part of 02-03. Rationale: `thinking_enabled` enables thinking-state filtering without re-reading flags; `num_samples` enables pass@k reconstruction from a single file without grouping.
- **D-10:** The Gemini `reasoning_effort="none"` line at `llm_evaluate.py:979` is **unrelated** to the new flag and is not touched. It is a Gemini-specific safety measure per `known-issues-archive.md`.

### `gpt-4.1-*` purge

- **D-11:** Delete three MODEL_REGISTRY entries: `gpt-4.1-2025-04-14` (lines 82–85), `azure-gpt-4.1` (lines 94–97), and any `gpt-4.1-mini` reference.
- **D-12:** Purge references from these ParBench-owned files (Appendix B of experiment plan):
  - `scripts/analysis/selfrepair_analysis.py`
  - `scripts/analysis/test_cross_model_comparison.py`
  - `scripts/analysis/token_analysis.py`
  - `scripts/evaluation/analyze_eval.py`
  - `scripts/evaluation/llm_evaluate.py`
  - `scripts/evaluation/run_eval_batch.py`
  - `scripts/evaluation/test_generate_paper_figures.py`
  - `scripts/generate_paper_figures.py`
  - `scripts/batch/archive/rerun_conjunction_eval.sh`
- **D-13:** **Skip** `le_code/example_query.py` (external/untracked per `.planning/.continue-here.md` Infrastructure State, lines 116–119).
- **D-14:** Test fixtures that hardcode `gpt-4.1-mini` as a model ID get rewritten to use `azure-gpt-5.3-chat` or `gpt-4o` (whichever matches the test's intent — reasoning-capable vs standard). Test behavior (what is being asserted) does not change.
- **D-15:** Result JSONs on disk in `results/evaluation/azure-gpt-4.1/` and `results/evaluation/gpt-4.1-mini/` are **not** touched (protected per `feedback_protect_cuda_omp_results` memory and `known-issues.md` "append-only" principle). They remain for audit.

### `derive_l0_passers.py`

- **D-16:** Location: `scripts/evaluation/derive_l0_passers.py`. CLI: `python3 -m scripts.evaluation.derive_l0_passers --canonical-dir <path> --model <id> --out <path>`.
- **D-17:** Input contract: `--canonical-dir` points to a directory of per-task result JSONs (e.g. `results/evaluation/qwen_canonical/`). Script filters to files where `model == --model` and `augment_level == 0`.
- **D-18:** Filter semantics: **pass@1-of-any** — cell (source_spec, target_spec) is a passer if the set of samples for that cell contains ≥1 result with `overall_status == "PASS"`. Samples are identified by the per-task JSON naming convention `{src}-to-{tgt}[-s{n}].json` (existing pass@k convention).
- **D-19:** Output schema (flat list of task tuples — per user selection):
  ```json
  [
    {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "augment_level": 0},
    ...
  ]
  ```
  `augment_level: 0` is included as a placeholder — the **consuming** `run_eval_batch.py --task-list` invocation overrides via `--augment-levels 1 2 3 4`.
- **D-20:** Output path default: `.planning/eval-selections/l0_passers_{model}.json`. The directory already exists (per `.planning/` listing).
- **D-21:** Error handling: if < 3 samples exist for a cell, include the cell only if ≥1 sample passed (permissive — matches "pass@1-of-any" exactly, treating missing samples as non-passes). Emit a warning to stderr listing cells with incomplete sample counts.
- **D-22:** Tests live in `tests/test_derive_l0_passers.py` with synthetic fixtures (no real result JSONs). Cases:
  - 3/3 PASS → included
  - 1/3 PASS → included
  - 0/3 PASS → excluded
  - 2 samples, 1 PASS → included + warning
  - 0 samples for a cell → excluded + warning

### `--task-list <json>` flag on `run_eval_batch.py`

- **D-23:** New argument added to the existing `argparse` surface in `run_eval_batch.py:main()`. **Lock:** Implement via `parser.add_mutually_exclusive_group()` (argparse-native) so the CLI rejects `--task-list + --kernels` or `--task-list + --suite` with argparse's standard `error: argument ... not allowed with argument ...` message. Runtime-check fallback is not permitted — D-26 test case 3 asserts the argparse-native error shape. **(Lifted 2026-04-17 — plan 02-10):** The 3-way argparse-native mutex was over-scoped: `--suite` and `--kernels` are meant to compose (narrow-to-suite then filter-by-kernel), and the lock broke 12/12 Qwen real-API tests at argparse. Post-lift: `--suite`/`--kernels` are plain args, `--task-list ⊥ {--suite, --kernels}` is enforced at runtime via `parser.error()` after `parse_args()`. Both error paths still exit with code 2, so D-26 case 3's `SystemExit(2)` assertion remains the valid contract.
- **D-24:** Compatible with `--models`, `--direction`, `--augment-levels`, `--num-samples`, `--temperature`, `--thinking`, `--max-retries`, `--resume`. `--direction` is still **required** even with `--task-list` (passer JSON does not encode direction — passer JSON is per (source, target) pair and the direction is implicit in their APIs; the flag redundantly confirms it and filters).
- **D-25:** Semantics: `--task-list l0_passers_qwen.json` loads the JSON, builds task list from the entries (respecting `--augment-levels` override), and proceeds through the existing `_build_tasks()` → evaluate loop.
- **D-26:** Tests live in `tests/test_run_eval_batch_task_list.py` with synthetic passer JSON + mocked `evaluate_translation()`. Cases:
  - Valid passer JSON + `--augment-levels 1 2 3 4` → task list has `4 × len(passers)` tasks
  - Passer JSON with an entry whose source/target specs are not in manifest → task skipped with warning
  - `--task-list` + `--kernels` → argparse `SystemExit` (exit code 2); test asserts `pytest.raises(SystemExit)` + exit code, not the exact error-message text (robust to argparse-wording changes across Python versions)
  - `--task-list` without `--direction` → argparse `SystemExit` (existing `required=True` is preserved)

### End-to-end smoke test

- **D-27:** Kernel set: reuse Phase 1's `SUITE_SPECS` from `tests/test_spec_loader_integration.py:34` — `rodinia-bfs-cuda`, `xsbench-xsbench-cuda`, `rsbench-rsbench-cuda`, `mixbench-mixbench-cuda`, `hecbench-bezier-surface-cuda`. Single canonical list across all integration tests.
- **D-28:** Test harness lives in `tests/test_eval_e2e_smoke.py`, marked `@pytest.mark.integration` and `@pytest.mark.llm` (new marker — skipped unless `PARBENCH_RUN_LLM_TESTS=1` is set). This protects CI (no API keys) and prevents accidental spend.
- **D-29:** Smoke test flow per (suite_sample, model) pair:
  1. `--dry-run` invocation of `run_eval_batch.py` — asserts the prompt is built, no API call.
  2. One real invocation — asserts `overall_status` is one of {PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL} (functional smoke — not a correctness claim); asserts result JSON has all seven schema-guardrail fields: `thinking_enabled`, `num_samples`, `sample_id`, `temperature`, `augment_level`, `model`, `overall_status`. The two new fields (`thinking_enabled`, `num_samples`) are the primary regression guardrails; the remaining five are existing fields re-asserted to catch accidental schema removals.
- **D-30:** Budget: 5 kernels × 2 models × 3 samples = 30 samples. Pricing verified 2026-04-17 against live provider pages:
  - `azure-gpt-5.3-chat` (GPT-5.3 Chat Global SKU via Azure, `reasoning_effort=medium`, <272K context): **$1.75/1M input, $14.00/1M output** (verified 2026-04-17 at azure.microsoft.com/en-us/pricing/details/azure-openai/). At 5k prompt + 20k output per sample → **$0.28875/sample**. Historical: placeholder pricing was $2.50/$15 ($0.3125/sample) — superseded by verified rates.
  - `together-qwen-3.5-397b-a17b` (serverless): **$0.60/1M input, $3.60/1M output** (source: together.ai). Same assumption → **$0.075/sample**.
  - Smoke cost = 15 × $0.28875 + 15 × $0.075 = $4.33 + $1.13 = **$5.46**. Revised ceiling is **$6**. Reasoning tokens bill as output tokens on both providers — if `reasoning_effort=medium` doubles output tokens (20k → 40k), worst-case smoke cost ≈ $9.78.
  - `docs/neurips2026-experiment-plan.md §3.1` pricing is reconciled separately (follow-up PR).
  - Note: "GPT-5.3 Chat" is the resolved Azure deployment name (`gpt-5.3-chat`); the Azure SKU is "GPT-5.3 Chat Global".

### Integration smoke + handoff (02-08 addendum — 2026-04-17)

**D-31 — Dry-run matrix enumeration.** The 02-08 dry-run matrix parametrizes over: (a) the 5 suite names from `SUITE_SPECS` at `tests/test_spec_loader_integration.py:34` (rodinia, xsbench, rsbench, mixbench, hecbench), (b) the 6 translation directions `cuda-to-omp`, `omp-to-cuda`, `cuda-to-opencl`, `opencl-to-cuda`, `omp-to-opencl`, `opencl-to-omp`, and (c) the 2 models `together-qwen-3.5-397b-a17b` and `azure-gpt-5.3-chat`. Total nominal = 60 cases; skips are derived at collection time. Marker: `@pytest.mark.integration` only (no `llm`), so the matrix exercises every default `pytest tests/` run at zero API cost.

**D-32 — KNOWN_FAIL + missing-target skip semantics.** 02-08 parses `.claude/rules/known-issues.md` §"KNOWN_FAIL Specs (8 — exclude from eval batches)" at test-**collection** time (not hard-coded in the test module). Any dry-run or real-API case whose source OR target spec is in that 8-entry set calls `pytest.skip(...)` with the spec id in the reason. Separately, 02-08 loads `manifest.jsonl` at collection time and skips combinations whose target-API spec does not exist (e.g. mixbench has no `omp_target` spec, so any mixbench `*-to-omp_target` pair is skipped — this specific example is illustrative; the real skip set is derived from `manifest.jsonl` at test-collection time). Rationale: the KNOWN_FAIL list drifts — hard-coding it in the test module creates a second source of truth that will rot.

**D-33 — Ablation-slice candidate-kernel rule.** The 02-08 real-API `test_real_e2e_canonical_to_ablation` test picks `rodinia-bfs-cuda → rodinia-bfs-omp` as a **candidate** (small runtime, small source, historically stable build) — NOT as a "known passer for model X". The canonical step (pass@3, L0, temp=0.7, thinking=on) decides pass/fail empirically. If `derive_l0_passers.py` returns zero passers for the (candidate, model) cell, the test calls `pytest.fail(...)` with guidance to pick a different candidate or investigate. An empty-passer smoke is NOT acceptable as "green light" — it IS the signal this test exists to catch before Phase 3 spends real money. Defines "pass@1-of-any" (on first use) per D-18: a cell is a passer iff ≥1 of its 3 canonical samples has `overall_status == PASS`. All real-API tests use `tmp_path` as `--project-root` to avoid touching `results/evaluation/`.

**D-34 — GPT-5.3 Chat handoff runbook + two-track Phase 3 execution split.** Phase 3 execution splits across two machines: **Phase A (canonical)** and **Phase C (ablation)** for `azure-gpt-5.3-chat` run on Le's own clone of the repo (Azure account ownership + throughput) per `docs/neurips2026-gpt5-handoff.md`; the equivalent `together-qwen-3.5-397b-a17b` streams run on the Linux GPU machine. **Phase B (`derive_l0_passers.py`)** runs on the machine that produced each canonical set. Deliverable is a clone + result-JSON-tarball handback: Le tars `results/evaluation/azure-gpt-5.3-chat/` and sends it; Samyak extracts, runs `/validate`, commits to `main`. No named branches, no cross-repo merges. The runbook (`docs/neurips2026-gpt5-handoff.md`) documents: context, repo setup, secrets checklist (`AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, deployment name `gpt-5.3-chat`), pre-flight verification, exact stage commands for canonical/derive/ablation, output layout + schema, cost model at **$1.75/1M input + $14.00/1M output** (verified 2026-04-17 against azure.microsoft.com; historical placeholder was $2.50/$15), Gal-approved $559 ceiling (signed off 2026-04-17 at pre-refresh pricing; refreshed estimate ~$784 — see `docs/neurips2026-gpt5-handoff.md §7`), $600 soft tripwire (ROADMAP Phase 3 SC-5), and tarball delivery.

### Claude's Discretion

- Fixture layout in `tests/test_derive_l0_passers.py` (tempfile-per-test vs module-scoped).
- Log verbosity for D-08 no-op branches (DEBUG vs INFO).
- Whether to add a `--filter` parameter to `derive_l0_passers.py` for the Gal fallback (`pass@2-of-3`) now, or defer until Gal requests. Recommendation: defer — not in the critical path per D-21 (pass@1-of-any is authoritative per PROJECT.md decision table).

---

## Canonical References (canonical_refs)

Downstream agents MUST read these before planning or implementing.

### Requirements & Design Authority
- `.planning/REQUIREMENTS.md` §Phase 2 — authoritative acceptance criteria
- `.planning/ROADMAP.md` §Phase 2 — deliverables + success criteria table
- `docs/neurips2026-experiment-plan.md §2.4` — AUTHORITATIVE design (canonical + L0-conditional ablation). Supersedes §§2.1–2.3 where they conflict.
- `.planning/PROJECT.md` — Key Decisions table (budget overshoot, ablation filter, model set)

### Active Guardrails
- `.claude/rules/known-issues.md` — 8 KNOWN_FAIL specs, `--suite` filter requirement
- `.claude/rules/evaluation.md` — Kernel-centric translation, result JSON schema, `--suite` critical
- `.claude/rules/python.md` — `python3`, harness CLI flag ordering
- Memory: `feedback_protect_cuda_omp_results`, `feedback_protect_qwen_results` — inviolable result JSON rules
- Memory: `feedback_no_primary_benchmark` — pipeline must not special-case any suite

### Existing Code to Extend
- `scripts/evaluation/llm_evaluate.py:68–115` — MODEL_REGISTRY (add `azure-gpt-5.3-chat`, purge gpt-4.1, add `supports_thinking`)
- `scripts/evaluation/llm_evaluate.py:905–910` — Azure call site (inject `reasoning_effort` conditionally)
- `scripts/evaluation/llm_evaluate.py:1000–1002` — Qwen `enable_thinking` flag site
- `scripts/evaluation/run_eval_batch.py:362–473` — argparse block inside `main()` (add `--task-list`, `--thinking`)
- `scripts/evaluation/run_eval_batch.py:_build_tasks()` — task list builder (branch on `--task-list`)
- `tests/conftest.py` — `_PROJECT_ROOT` (private, module-local) + `@pytest.mark.integration` skip mechanism (extend with `llm` marker). Plan 02-07 promotes `_PROJECT_ROOT` → `PROJECT_ROOT` (public) so downstream tests can `from tests.conftest import PROJECT_ROOT` instead of replicating the `Path(__file__).parent.parent` idiom.
- `tests/test_spec_loader_integration.py` — `SUITE_SPECS` (reuse exact set for D-27)

### New Files Created
- `scripts/evaluation/derive_l0_passers.py`
- `tests/test_model_registry.py` (plan 02-02)
- `tests/test_thinking_flag.py` (plan 02-03)
- `tests/test_derive_l0_passers.py` (plan 02-05)
- `tests/test_run_eval_batch_task_list.py` (plan 02-06)
- `tests/test_eval_e2e_smoke.py` (plan 02-07)
- `.planning/eval-selections/l0_passers_{qwen,gpt5}.json` (generated by Phase 3 Phase B, not Phase 2; directory exists)

---

## Existing Code Insights (code_context)

### Reusable Assets
- **Azure deployment name resolution** at `llm_evaluate.py:877` already uses prefix-strip — new `azure-gpt-5.3-chat` entry inherits this for free (D-01).
- **Qwen `extra_body` passthrough** at `llm_evaluate.py:995–1002` is the existing hook for `enable_thinking` — flag wiring is one kwarg change, no new Together SDK call pattern.
- **Result JSON schema** existing fields (`overall_status`, `augment_level`, `model`, `sample_id`, `temperature`, etc.) are unchanged. Two new top-level fields are added: `thinking_enabled` and `num_samples` (D-09).
- **Phase 1 integration test pattern** (`tests/conftest.py` + `@pytest.mark.integration` + `_PROJECT_ROOT`, to be promoted to public `PROJECT_ROOT` in 02-07) is the template for D-28.
- **`analyze_eval.py` complexity lookup pattern** (`_load_complexity_lookup()` in `scripts/evaluation/analyze_eval.py`) is the closest existing pattern for robust file reading. Mirror its *try/except-and-warn-continue* idiom for per-result-JSON parsing in `derive_l0_passers.py` (skip unparseable files with a stderr warning). **Not** a `{}` fallback for the whole input — `derive_l0_passers.py` ingests a directory of per-task result JSONs, so per-file resilience is the analogue, not a single-CSV empty default.

### Established Patterns
- MODEL_REGISTRY uses `dict[str, dict[str, str]]` — extending each entry with `supports_thinking: bool` widens the value type to `dict[str, str | bool]`. Type annotation on line 61 needs `dict[str, dict[str, Any]]` or `TypedDict`. Prefer `TypedDict` for schema clarity.
- All CLI flags use `argparse`, not `click`. Keep this.
- `run_eval_batch.py:_build_tasks()` returns a list of task dicts consumed by the evaluate loop. `--task-list` should produce the same shape so the downstream loop is unchanged.

### Integration Points
- `run_eval_batch.py --task-list` bypasses `--suite`/`--kernels` filters but **must** still honor `--models`, `--direction`, `--augment-levels`, `--thinking` — these are per-run config, not task selection.
- `derive_l0_passers.py` reads `results/evaluation/{model}/*.json`. If the canonical run writes to a differently-named directory (e.g. `results/evaluation/qwen_canonical/`), the script's `--canonical-dir` accepts any path — do not hardcode.
- `tests/` does not yet have an `llm` pytest marker. Register it in `pyproject.toml` `[tool.pytest.ini_options].markers` (verified 2026-04-16 — no `pytest.ini` exists in this repo; markers are configured via pyproject).

---

## Specific Ideas (specifics)

- **Register Phase 2 decisions in `.planning/PROJECT.md` Key Decisions table** before launching Phase 3. Prevents the Phase 1 → Phase 2 drift that `.continue-here.md` warns about.
- **Commit 02-01 (MODEL_REGISTRY azure-gpt-5.3-chat entry) first**, separately from 02-02 (capability schema), so `git bisect` across the purge + schema extension is clean.
- **Unit tests use synthetic fixtures** (tempdir + `json.dump` of fake result shapes) — no dependency on real evaluation results. Matches Phase 1's `test_campaign_classification.py` TDD pattern (D-16 through D-20 in Phase 1 CONTEXT.md).
- **Smoke test is opt-in via `PARBENCH_RUN_LLM_TESTS=1`** — the normal `pytest tests/` run stays API-free and cheap.
- **Document the `--thinking` flag in `.claude/rules/evaluation.md`** as part of 02-03. Otherwise future sessions will grep for `enable_thinking` in the source and miss the CLI surface.
- **Line-discipline for 02-03 (defensive):** Do **NOT** modify `llm_evaluate.py:979` — that is Gemini's `reasoning_effort="none"` safety line (D-10), unrelated to the new flag. The Azure `reasoning_effort` injection point is `llm_evaluate.py:905` (inside `client_az.chat.completions.create(...)`). A prior incident (2026-04-16) saw `:879` "fixed" to `:956`, which silently moved the patch to the Gemini call site. Downstream plan 02-03 must call out "modify line 905 (Azure), not line 979 (Gemini)" explicitly in its step list.

---

## Deferred Ideas (deferred)

- **Gal-fallback `pass@2-of-3` filter** on `derive_l0_passers.py` — not needed unless Gal declines the $559 budget overshoot. Deferred; add a `--filter` flag later only if required.
- **AskSage provider integration** — BLOCKED per PROJECT.md, not on May 1 critical path.
- **Per-model cost-tracking dashboard** — nice to have for Phase 3 monitoring; deferred to Phase 3 or post-NeurIPS.
- **Retroactive purge of `results/evaluation/azure-gpt-4.1/` and `gpt-4.1-mini/` directories** — forbidden by `feedback_protect_cuda_omp_results`; not considered.
- **Removing the `reasoning_effort="none"` line at `llm_evaluate.py:956`** (Gemini) — out of scope; see D-10.

---

## Plan Decomposition (8 atomic plans)

Per user selection. Each plan is one atomic commit.

| Plan | Subject | Files touched | Tests |
|------|---------|---------------|-------|
| 02-01 | Add `azure-gpt-5.3-chat` to MODEL_REGISTRY | `scripts/evaluation/llm_evaluate.py` | None (schema change only; 02-02 gates testing) |
| 02-02 | Add `supports_thinking: bool` capability field to MODEL_REGISTRY; type as TypedDict | `scripts/evaluation/llm_evaluate.py` | `tests/test_model_registry.py` (new; asserts every entry has the field) |
| 02-03 | Add `--thinking on\|off` CLI flag; wire to Qwen + Azure call sites; add `thinking_enabled` to result JSON | `scripts/evaluation/llm_evaluate.py`, `scripts/evaluation/run_eval_batch.py`, `.claude/rules/evaluation.md` | `tests/test_thinking_flag.py` (new; mocked SDK calls assert kwargs) |
| 02-04 | Purge `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` | 9 files (Appendix B minus le_code/) | Existing tests updated (D-14) |
| 02-05 | New `scripts/evaluation/derive_l0_passers.py` | new file | `tests/test_derive_l0_passers.py` (new; synthetic fixtures, D-22) |
| 02-06 | New `--task-list <json>` flag on `run_eval_batch.py` | `scripts/evaluation/run_eval_batch.py` | `tests/test_run_eval_batch_task_list.py` (new; mocked evaluate_translation, D-26) |
| 02-07 | End-to-end smoke test (5 suites × 2 models × cuda-to-omp) | `tests/test_eval_e2e_smoke.py` (new), `tests/conftest.py` (register `llm` marker) | The smoke test IS the test; gated by `PARBENCH_RUN_LLM_TESTS=1` |
| 02-08 | Integration smoke + GPT-5.3 Chat handoff runbook (dry-run matrix + real E2E canonical→derive→ablation slice + omp-to-cuda cell + handoff runbook) | `tests/test_eval_integration_smoke.py` (new), `docs/neurips2026-gpt5-handoff.md` (new) | Dry-run matrix (zero API) + real-API tests gated by `PARBENCH_RUN_LLM_TESTS=1` |

**Total estimated effort:** 1–1.5 days of focused work (excludes smoke-test wall clock, which is ~10 min for 30 real LLM calls).

**Blockers:** None for Phase 2 code + tests. Phase 3 launch remains blocked on Gal sign-off + Le TPM confirmation (out of scope for this phase).

---

## Verification

Phase 2 is complete when:

1. `pytest tests/` passes (all new tests + existing tests updated post-purge).
2. `PARBENCH_RUN_LLM_TESTS=1 pytest tests/test_eval_e2e_smoke.py -v` passes — 10 result JSONs produced (5 suites × 2 models), each with `thinking_enabled=True`, `temperature=0.7`, `num_samples=3`, `augment_level=0`.
3. Live-code grep returns zero live model-ID references:
   ```bash
   grep -rn "gpt-4\.1" scripts/ tests/ --include='*.py' --include='*.sh' \
     | grep -v 'results/evaluation/' \
     | grep -v 'batch_.*\.json'
   ```
   Acceptance rule: zero live model-ID references in Python/shell source under `scripts/` and `tests/`. Markdown files in `docs/` and `.planning/` (including this CONTEXT doc, PROJECT.md, ROADMAP.md, `.continue-here.md`, experimental_decisions_log.md, codebase snapshots, historical guides) may legitimately mention the purged IDs as historical context and are **not** expected to be empty.
4. `python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; print(MODEL_REGISTRY['azure-gpt-5.3-chat']['supports_thinking'])"` prints `True`.
5. `python3 scripts/evaluation/derive_l0_passers.py --help` shows the expected CLI.
6. `python3 scripts/evaluation/run_eval_batch.py --help` shows `--task-list` and `--thinking` flags.
7. `.planning/phases/02-llm-eval-testing/02-CONTEXT.md` exists with the content of this plan file.
8. `.planning/STATE.md` updated: Phase 2 status → "In progress" (to be updated by `/gsd-plan-phase 2` after this discuss phase is approved).

9. 02-08 plan file exists with frontmatter `depends_on: [02-01, 02-02, 02-03, 02-05, 02-06, 02-07]`, non-empty `must_haves.truths` + `must_haves.artifacts`, and `<verify>` blocks with real commands (pytest/grep/python3/ls).
10. `docs/neurips2026-gpt5-handoff.md` exists with required pins: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `reasoning_effort=medium`, `pre-flight`, `$1.75`, `derive_l0_passers`, `--task-list`.

No evaluation streams are launched in Phase 2.

---

## Open Questions Resolved

| Question | Answer | Source |
|----------|--------|--------|
| CLI surface for thinking/reasoning? | Universal `--thinking on\|off`, capability-gated | User AskUserQuestion 2026-04-16 |
| `l0_passers_*.json` schema? | Flat list of task tuples | User AskUserQuestion 2026-04-16 |
| `gpt-4.1-*` purge scope? | MODEL_REGISTRY + ParBench scripts/docs; le_code/ and result JSONs untouched | User AskUserQuestion 2026-04-16 |
| Plan decomposition? | 7 atomic plans | User AskUserQuestion 2026-04-16 |
| Azure gpt-5.3-chat deployment name? | Resolved 2026-04-17 — placeholder `gpt-5.4` → `gpt-5.3-chat` via existing prefix-strip at `llm_evaluate.py:877`; no new field | D-01 (Claude's discretion, matches existing azure-gpt-4.1 pattern) |
| Smoke test kernel set? | Reuse Phase 1's `SUITE_SPECS` | D-27 (Claude's discretion, keeps one canonical list) |

---

## Next Step

Invoke `/gsd-plan-phase 2` to generate the seven 02-0N-PLAN.md files under `.planning/phases/02-llm-eval-testing/`.

---

*Phase: 02-llm-eval-testing*
*Context gathered: 2026-04-16*
