# Roadmap: ParBench NeurIPS 2026

> ⚠️ **`azure-gpt-5.4` is a placeholder model identifier throughout this roadmap.** As of 2026-04-16, `scripts/evaluation/llm_evaluate.py:MODEL_REGISTRY` contains only `azure-gpt-4.1`; no GPT-5 variant is registered. Phase 2's first deliverable (`MODEL_REGISTRY` entry) must land — with the exact Azure deployment name confirmed by Le — before any Phase A success criterion can be met. Do not plan work assuming the identifier resolves today.
> ⚠️ **Pass-rate and budget numbers cited below (e.g., "$559", "287 L0-passers", "55%") are estimates, not measurements.** See `docs/neurips2026-experiment-plan.md` §2.4. The closest in-repo datapoint is ~31% Qwen first-sample pass; 55% pass@1-of-any is an extrapolation. Real numbers only knowable after Phase A completes.
> ⚠️ **Gal's sign-off on the GPT budget overshoot ($559 vs $400 target) is PENDING as of 2026-04-16** — it is a Phase A launch prerequisite.

## Overview

This roadmap takes ParBench from a pilot-validated benchmark (Qwen 3.5 397B, 1,248 results) to a multi-model, peer-review-ready NeurIPS submission. Four phases: verify the pipeline with real data, test end-to-end evaluation with the revised experiment design, run canonical + L0-conditional ablation, write the paper.

Experiment design was revised on 2026-04-16 from a two-campaign structure to a canonical + L0-conditional ablation structure (see `.planning/PROJECT.md` Key Decisions for full rationale; pre-approval snapshot at `~/.claude/plans/gsd-context-goal-i-cached-finch.md`).

## Phases

- [x] **Phase 1: Pipeline Testing & Uniformity** -- Test and fix the full spec-build-run-verify pipeline across all 5 suites
- [x] **Phase 2: LLM Eval Testing** -- Test evaluation pipeline end-to-end with real LLM calls; add azure-gpt-5.4 registry entry, reasoning_effort param, Qwen thinking flag, L0-passer derivation script, `--task-list` flag (COMPLETE 2026-04-17)
- [ ] **Phase 3: Full Evaluation Runs** -- Canonical (pass@3 L0) then L0-conditional ablation (pass@1 L1-L4) for Qwen 3.5 397B + Azure GPT-5.4
- [ ] **Phase 4: NeurIPS Paper** -- Write paper with every claim traceable to verified results

## Phase Details

### Phase 1: Pipeline Testing & Uniformity

**Goal:** Every non-KNOWN_FAIL spec builds, runs, and verifies across all 5 suites. No suite-specific special-casing in pipeline code. Pipeline is portable via config.

**Depends on:** Nothing (first phase)

**Deliverables:**
- Spec loading tested: 1+ spec per suite loads correctly, paths resolve, source files readable
- Build tested: 1+ program per suite per API builds successfully
- Run + verify tested: built executables run and verify correctly
- Suite-specific code fixed: `analyze_rodinia_batch.py` generalized, `EXCLUDED_SPECS` centralized, `if suite == "rodinia"` removed
- Portability audit: compiler paths, include paths documented; hardcoded paths acknowledged and deferred
- Unit tests (synthetic data) + integration smoke tests (real builds) written alongside testing
- Test programs: bfs (Rodinia), xsbench, rsbench, mixbench, bezier-surface or bilateral (HeCBench)

**Success Criteria:**
1. Every non-KNOWN_FAIL spec builds, runs, and verifies across all 5 suites
2. Tests prove it -- `pytest tests/` passes
3. No suite-specific special-casing in pipeline code
4. `EXCLUDED_SPECS` is a single importable constant (no stale duplicates)
5. Pipeline is portable via `config/paths.json` (not hardcoded paths in Python code)

### Phase 2: LLM Eval Testing

**Goal:** Can run the eval batch launcher end-to-end for 1 kernel per suite with both Qwen and Azure GPT-5.4 under the canonical config (pass@3, L0, temp=0.7, thinking=ON, reasoning_effort=medium, self-repair=OFF), and separately run the L0-conditional ablation launcher with a task list from `derive_l0_passers.py`.

**Depends on:** Phase 1

**Deliverables:**
- `MODEL_REGISTRY` entry for `azure-gpt-5.4` in `scripts/evaluation/llm_evaluate.py`
- `reasoning_effort="medium"` passed on Azure API calls for reasoning-capable models (guarded by capability check)
- Qwen `enable_thinking` flipped to `True`; new `--thinking on|off` CLI flag (default `on`)
- `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` purged from scripts/docs (result JSONs stay on disk for audit)
- New `scripts/evaluation/derive_l0_passers.py`: takes canonical result dir + model, emits `l0_passers_{model}.json` with cells where ≥1 of 3 samples passed (pass@1-of-any)
- New `--task-list <json>` flag on the eval batch launcher: consumes passer JSON instead of enumerating from manifest
- Prompt construction verified for each suite via `--dry-run`
- Real LLM calls tested: 1 program per suite, cuda-to-omp direction, via Qwen and GPT-5.4
- Integration smoke + GPT-5.4 handoff runbook: `tests/test_eval_integration_smoke.py` covers zero-API dry-run matrix (5 suites × 6 directions × 2 models), real-API E2E canonical→derive→ablation slice on a candidate kernel (pass/fail decided empirically; zero-passer → `pytest.fail`), and one omp-to-cuda cell to prove direction independence. `docs/neurips2026-gpt5-handoff.md` is the runbook for Le to run GPT-5.4 on his own clone and hand back result JSONs as a tarball.

**Success Criteria:**
1. End-to-end canonical eval works for 1 kernel per suite with both models (result JSONs contain `temperature=0.7`, `num_samples=3`, `augment_level=0`, thinking=ON markers)
2. `derive_l0_passers.py` correctly partitions synthetic canonical fixtures into passers/failers (pass@1-of-any semantics)
3. Eval batch launcher `--task-list` consumes the passer JSON and runs only listed cells
4. All gpt-4.1 model IDs absent from scripts/docs (per `grep -rn "gpt-4\.1" scripts/ docs/ .planning/`)
5. `pass_at_k(k=3)` returns correct values for known inputs (existing test unchanged)

**Plans:** 8/8 plans executed (Phase 2 COMPLETE 2026-04-17)
- [x] 02-01-add-azure-gpt54-registry-PLAN.md — Add `azure-gpt-5.4` to MODEL_REGISTRY
- [x] 02-02-supports-thinking-capability-PLAN.md — Add `supports_thinking: bool` capability field + TypedDict schema
- [x] 02-03-thinking-cli-flag-PLAN.md — `--thinking on|off` CLI flag wired to Qwen (currently :1034) + Azure (currently :915); result JSON schema bump (thinking_enabled, num_samples)
- [x] 02-04-purge-gpt41-PLAN.md — Purge `gpt-4.1-*` from 9 ParBench-owned files
- [x] 02-05-derive-l0-passers-PLAN.md — New `scripts/evaluation/derive_l0_passers.py` (pass@1-of-any)
- [x] 02-06-task-list-flag-PLAN.md — New `--task-list <json>` flag on eval batch launcher with argparse mutex group
- [x] 02-07-eval-e2e-smoke-PLAN.md — End-to-end smoke test (5 suites × 2 models × cuda-to-omp, gated by `PARBENCH_RUN_LLM_TESTS=1`); `llm` pytest marker registered + `PROJECT_ROOT` promoted public on tests/conftest.py
- [x] 02-08-integration-smoke-and-handoff-PLAN.md — Integration smoke + GPT-5.4 handoff runbook (dry-run matrix 5×6×2 + real E2E canonical→derive→ablation slice + omp-to-cuda cell + `docs/neurips2026-gpt5-handoff.md` 8-section runbook)

### Phase 3: Full Evaluation Runs

**Goal:** Complete canonical + L0-conditional ablation runs for Qwen 3.5 397B and Azure GPT-5.4 across all 5 suites, all 6 directions (including omp_target case studies where available), using a 3-phase launch sequence.

**Execution split (two-track):**
Phase A (canonical) and Phase C (ablation) run on **two machines**: `azure-gpt-5.4` streams are executed by Le on his own clone of the repo per `docs/neurips2026-gpt5-handoff.md`; result JSONs are delivered back to Samyak as a tarball and committed to `main`. `together-qwen-3.5-397b-a17b` streams run on the Linux GPU machine. Phase B (`derive_l0_passers.py`) runs on the machine that produced each canonical set. No named branches; no cross-repo merges. (See decision D-34 in `.planning/phases/02-llm-eval-testing/02-CONTEXT.md`.)

**Depends on:** Phase 2

**Deliverables:**
- **Phase A (canonical)**: 2 parallel streams on 2 machines
  - `qwen_canonical`: pass@3, L0, temp=0.7, thinking=ON, self-repair=OFF (~17h wall clock)
  - `gpt_canonical`: same config, Azure GPT-5.4 with `reasoning_effort=medium` (~17h wall clock)
- **Phase B (derive)**: Run `derive_l0_passers.py` for each model → `l0_passers_{qwen,gpt5}.json` committed to `.planning/eval-selections/`
- **Phase C (ablation)**: 2 parallel streams on 2 machines
  - `qwen_ablation --task-list l0_passers_qwen.json --augment-levels 1 2 3 4` (pass@1, all 4 levels on all L0-passers)
  - `gpt_ablation --task-list l0_passers_gpt5.json --augment-levels 1 2 3 4` (same config)
- Analysis: `analyze_eval.py` regenerated for canonical + ablation per model
- AskSage: still BLOCKED, not on May 1 critical path; deferred to post-submission if Le unblocks

**Success Criteria:**
1. Canonical streams complete for both models across all 87 × 6 cells (no gaps)
2. `l0_passers_{qwen,gpt5}.json` exist, committed to `.planning/eval-selections/`, with non-zero cell counts
3. Ablation streams complete for all L0-passer cells × 4 levels for both models
4. Pass rates, status distributions, per-suite breakdowns regenerated from `analyze_eval.py`
5. Actual GPT-side cost ≤ $600 (tracks against Samyak-approved overshoot; abort if >50% over projection)

### Phase 4: NeurIPS Paper

**Goal:** A complete NeurIPS Datasets & Benchmarks paper where every quantitative claim is traceable to verified result files on disk.

**Depends on:** Phase 3

**Deliverables:**
- Rewrite sections of `docs/paper/latex/overleaf_main.tex`
- Every quantitative claim traceable to specific result JSON files
- Submit by May 1, 2026

**Success Criteria:**
1. Every quantitative claim has a traceable path to result files on disk
2. Paper submitted to NeurIPS 2026 Datasets & Benchmarks track by May 1, 2026

## Progress

**Execution Order:** Phase 1 -> Phase 2 -> Phase 3 (A -> B -> C) -> Phase 4

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Pipeline Testing & Uniformity | Complete | 2026-04-10 |
| 2. LLM Eval Testing | Complete | 2026-04-17 |
| 3. Full Evaluation Runs (canonical + L0-conditional ablation) | Not started | - |
| 4. NeurIPS Paper | Not started | - |
