# Requirements: ParBench

**Defined:** 2026-04-09
**Core Value:** Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.

> ⚠️ **`azure-gpt-5.4` is a placeholder** in all Phase 2/3 requirement rows below. As of 2026-04-16, no GPT-5 variant exists in `scripts/evaluation/llm_evaluate.py:MODEL_REGISTRY` (only `azure-gpt-4.1`). The Phase 2 requirement "`MODEL_REGISTRY` entry added for `azure-gpt-5.4`" must be completed — using the exact Azure deployment name confirmed by Le — before the Phase 3 canonical streams can satisfy their success criteria.
> ⚠️ **Budget-related success criteria (e.g., "Actual GPT cost ≤ $600") are grounded in an estimated 55% L0-pass rate, not a measurement** — see `docs/neurips2026-experiment-plan.md` §2.4 for the full assumption chain. Closest observed datapoint is ~31% Qwen first-sample pass. Budget bound may need revision once Phase A provides real numbers.

## Phase 1: Pipeline Testing & Uniformity

- [ ] Spec loading works for all 5 suites (paths resolve, source files exist, prompt payloads correct)
- [ ] Build works for 1+ program per suite per API (cuda, omp, opencl)
- [ ] Run + verify works for all non-KNOWN_FAIL specs
- [ ] `EXCLUDED_SPECS` centralized as one importable constant (no stale duplicates)
- [ ] Suite-specific analysis code generalized (`analyze_rodinia_batch.py` replaced or generalized)
- [ ] No `if suite == "rodinia"` special-casing in pipeline code
- [ ] Unit tests (synthetic data) cover: path resolution, EXCLUDED_SPECS filtering, campaign classification
- [ ] Integration smoke tests (real builds) cover: 1+ spec per suite builds, runs, verifies
- [ ] Portability audit documented: hardcoded compiler paths acknowledged, `config/paths.json` usage verified

## Phase 2: LLM Eval Testing

Design revised 2026-04-16: two-campaign structure replaced with canonical + L0-conditional ablation. See `.planning/PROJECT.md` Key Decisions.

- [ ] `MODEL_REGISTRY` entry added for `azure-gpt-5.4` in `scripts/evaluation/llm_evaluate.py`
- [ ] `reasoning_effort="medium"` passed on Azure API calls for reasoning-capable models (guarded by capability check)
- [ ] Qwen `enable_thinking` flipped to `True`; new `--thinking on|off` CLI flag (default `on`)
- [ ] `gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini` purged from scripts/docs (result JSONs stay on disk for audit)
- [ ] New `scripts/evaluation/derive_l0_passers.py` — emits `l0_passers_{model}.json` with cells where ≥1 of 3 canonical samples passed (pass@1-of-any)
- [ ] New `--task-list <json>` flag on `run_eval_batch.py` — consumes passer JSON instead of enumerating from manifest
- [ ] Prompt construction verified for each suite (via `--dry-run`)
- [ ] End-to-end canonical eval tested with real LLM calls (1 program per suite, cuda-to-omp) for Qwen AND Azure GPT-5.4
- [ ] `pass_at_k()` verified with actual canonical data (do NOT reimplement — already exists at `scripts/analysis/statistical_analysis.py:706`)
- [ ] AskSage adapter — **BLOCKED** until Le provides API docs/credentials; deferred to post-submission

## Phase 3: Full Evaluation Runs

Three-phase launch: canonical → derive → ablation. Canonical must complete before ablation can launch (ablation depends on passer-set derivation).

### Phase A (canonical, parallel)
- [ ] `qwen_canonical` complete: pass@3, L0, temp=0.7, thinking=ON, self-repair=OFF, all 87 × 6 cells
- [ ] `gpt_canonical` complete: same config, Azure GPT-5.4 + reasoning_effort=medium, all 87 × 6 cells

### Phase B (derive)
- [ ] `l0_passers_qwen.json` committed to `.planning/eval-selections/`
- [ ] `l0_passers_gpt5.json` committed to `.planning/eval-selections/`

### Phase C (ablation, parallel)
- [ ] `qwen_ablation` complete: pass@1, L1-L4, all L0-passer cells, thinking=ON, self-repair=OFF
- [ ] `gpt_ablation` complete: pass@1, L1-L4, all L0-passer cells, thinking=ON, self-repair=OFF

### Analysis
- [ ] `analyze_eval.py` regenerated for canonical + ablation per model
- [ ] Actual GPT cost ≤ $600 (tracks against Samyak-approved overshoot; abort if >50% over projection)

## Phase 4: NeurIPS Paper

- [ ] Rewrite sections of `docs/paper/latex/overleaf_main.tex`
- [ ] Every quantitative claim traceable to specific result JSON files on disk
- [ ] Submit to NeurIPS 2026 Datasets & Benchmarks track by **May 1, 2026**

## Out of Scope

| Feature | Reason |
|---------|--------|
| Repository-level (full build-system) translation | Kernel isolation is deliberate design -- different paper |
| New benchmark suites beyond current 5 | Scope fixed for NeurIPS submission |
| SYCL/HIP as primary evaluation directions | Case study status only; not in main paper claims |
| CI/CD for compilation or eval runs | All evals are manual on the Linux GPU machine by design |
| Real-time eval dashboard redesign | Only update if driven by results analysis changes |
| Full spec portability (compiler path templating) | Deferred to post-NeurIPS; document machine config in paper |
| GPT-4.1 mini re-runs | All GPT results botched -- ignore entirely |
| Two-campaign structure (C1 self-repair + C2 pass@k) | Superseded 2026-04-16 by canonical + L0-conditional ablation |
| Speculative AskSage adapter | BLOCKED until Le provides API docs; deferred to post-submission |

---
*Requirements defined: 2026-04-09*
*Last updated: 2026-04-16 after Gal-approved + Samyak-confirmed revision from two-campaign to canonical + L0-conditional ablation*
