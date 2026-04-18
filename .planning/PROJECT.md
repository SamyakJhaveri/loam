# ParBench

> ⚠️ **`azure-gpt-5.3-chat` is a placeholder model identifier throughout this document.** As of 2026-04-16, the `MODEL_REGISTRY` in `scripts/evaluation/llm_evaluate.py` contains only `azure-gpt-4.1`; there is no GPT-5 variant registered yet. Phase 2 Task 7 must register the exact Azure deployment name (confirmed with Le) before Phase A launches. Do not treat the model identifier as runnable in the current codebase.
> ⚠️ **Budget numbers quoted below (e.g., "$559", "287 L0-passers", "55% pass rate") are estimates built on a working assumption, not measurements.** See `docs/neurips2026-experiment-plan.md` §2.4 for the full caveat — the closest in-repo datapoint is ~31% Qwen first-sample pass, from which 55% pass@1-of-any is extrapolated.
> ⚠️ **Gal's sign-off on the GPT budget overshoot ($559 vs $400 target) is PENDING.** Where rows say "accepted" below, read it as "Samyak's scope choice, not a bilateral agreement." Do NOT launch Phase A until Gal signs off.

## What This Is

ParBench is a kernel-centric benchmark framework for evaluating LLM-based parallel code translation (CUDA <-> OpenMP <-> OpenCL). It provides 96 executable specs across 5 benchmark suites, a build-run-verify harness, an AST-driven augmentation engine for robustness testing, and — as of 2026-04-16 — a canonical + L0-conditional ablation evaluation protocol (replacing the earlier two-campaign structure). The current milestone verifies every pipeline component with real data, runs the canonical + ablation evaluations for Qwen 3.5 397B + Azure GPT-5.3 Chat, and writes the NeurIPS 2026 paper.

## Core Value

Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.

## Requirements

### Validated

- Pipeline (harness, spec_loader, llm_evaluate.py) is already suite-agnostic -- zero `if suite == "rodinia"` in core code
- 96 executable specs across 5 suites (60 Rodinia, 4 XSBench, 4 RSBench, 3 mixbench, 25 HeCBench)
- Build-run-verify harness (3-stage, conjunctive exit-code + stdout-pattern verification)
- AST-driven augmentation engine (6 transforms, L0-L4 intensity levels, libclang-backed)
- Prior Campaign 1 / Campaign 2 eval infrastructure retained as building blocks; superseded by canonical + L0-conditional ablation (2026-04-16)
- LLM provider adapters: Together AI, Azure OpenAI, Anthropic (all OpenAI-compatible)
- Qwen 3.5 397B results (1,248 eval results from the earlier two-campaign structure; kept on disk for audit but not used as the NeurIPS headline)
- Cross-API arg + verification handling (source args + union stdout pattern)
- Regex combiner bug fixed (_wrap_pattern, scoped inline flags) -- 2026-04-09
- `pass_at_k()` implemented in `statistical_analysis.py` and `quantitative_findings.py`
- `run_eval_campaign.sh` handles all 5 suites

### Active (by Phase)

- [x] **Phase 1:** Pipeline testing and uniformity across all 5 suites (spec loading, build, run, verify) — completed 2026-04-10
- [ ] **Phase 2:** LLM eval testing with real calls — add `azure-gpt-5.3-chat` model entry, `reasoning_effort=medium` param, Qwen thinking flag, `derive_l0_passers.py`, `--task-list` flag on `run_eval_batch.py`; purge `gpt-4.1-mini` from scripts/docs
- [ ] **Phase 3:** Full evaluation runs — 3-phase launch: canonical (pass@3 L0 temp=0.7 thinking=ON self-repair=OFF) → derive L0-passers (pass@1-of-any) → L0-conditional ablation (pass@1 L1-L4 on all L0-passers), for Qwen 3.5 397B + Azure GPT-5.3 Chat
- [ ] **Phase 4:** NeurIPS 2026 paper -- every claim traceable to verified result files

### Out of Scope

- Repository-level (full build-system) translation -- kernel isolation is a deliberate design choice
- New benchmark suites beyond current 5 -- scope is fixed for NeurIPS submission
- SYCL/HIP as primary evaluation directions -- case study status only, not in main results
- CI/CD for compilation or eval -- all eval runs are manual on the Linux GPU machine
- Dashboard visual redesign -- update only if driven by results analysis changes
- VCR cassettes for LLM test mocking -- mock `call_llm()` directly with real data

## Context

- **Qwen results:** 1,248 files -- C1 (780, temp=0.0, L0-L4) + C2 (468, temp=0.7, -s0/-s1/-s2). Every result JSON has `temperature` and `sample_id` fields.
- **GPT results:** ALL BOTCHED -- ignore entirely (empty prompts from Argonne machine)
- **AskSage:** BLOCKED -- zero code, zero documentation in codebase. Integration blocked until Le provides API docs/credentials. Do not speculatively build.
- **tmux sessions:** `qwen_hecbench` and `qwen_small` deleted (2026-04-09)
- **8 KNOWN_FAIL specs** (texture<>/CUDA12, missing GL, pre-existing runtime failures) -- excluded from eval denominators
- **5 phantom specs** deleted from specs/ but entries remain in manifest.jsonl (append-only) -- 15 expected schema validation errors, do not fix

## Constraints

- **Timeline:** NeurIPS 2026 deadline **May 1, 2026** (Datasets & Benchmarks track)
- **Data immutability:** Never modify existing result JSONs -- use --resume to append
- **Audit-first:** Pipeline must be hardened before new model evals are trusted
- **AskSage:** BLOCKED until Le provides API docs -- do not speculatively build adapter
- **Lean planning:** PROJECT.md stays lightweight; phases added to milestones incrementally

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Campaign separation via `campaign_for()` helper | Existing results already have `temperature` + `sample_id` fields. No folder restructuring needed. `--resume` preserved. | Superseded 2026-04-16 |
| AskSage marked BLOCKED | Zero code/docs in codebase. Cannot speculatively build adapter without API schema from Le. | Decided |
| Portability deferred | Hardcoded `/opt/nvidia/hpc_sdk/...` paths in specs. Full spec templating deferred to post-NeurIPS unless time permits. Document machine config in paper. | Decided |
| Campaign 1 = pass@1 + self-repair + L0-L4, temp=0 | Measures robustness and model's ability to repair; deterministic | Superseded 2026-04-16 |
| Campaign 2 = pass@k=3 + single-shot + L0 only, temp=0.7 | Measures stochastic sampling capability independent of self-repair | Superseded 2026-04-16 |
| Qwen 3.5 397B as baseline yardstick | Existing pilot data; most complete coverage across all 5 suites | Good |
| Kernel-centric isolation (build infrastructure provided) | Separates translation skill from build-system generation skill | Good |
| 4 phases instead of 6 | Removed separate TDD Infrastructure phase (tests alongside real testing), folded Provider Integration into Phase 2, Analysis into Phase 3 | Decided |
| **[2026-04-16]** Replace two-campaign design with canonical + L0-conditional ablation | Gal + meeting 2026-04-15 reasoning: two-campaign confounds temperature × augmentation × sampling × self-repair in a single estimator, reviewer-fragile for NeurIPS D&B. Canonical isolates best-effort capability (pass@3 L0 thinking=ON self-repair=OFF); ablation isolates source robustness (pass@1 L1-L4, thinking=ON). | Decided |
| **[2026-04-16]** Ablation filter = pass@1-of-any from canonical | A cell is scientifically informative for robustness only if the model can translate it at L0 at least once. Stricter filters (pass@2-of-3, pass@3) shrink coverage too aggressively for per-direction breakdown statistics. Implication: Δpass@1(L_k) must be computed on the L0-passer subset for BOTH terms (pass@1_canonical derived from canonical first sample restricted to passer cells, AND pass@1_L_k) — see `docs/neurips2026-experiment-plan.md` §2.4 estimator-denominator clarification. | Decided |
| **[2026-04-16]** Ablation scope = all 4 levels (L1+L2+L3+L4) on ALL L0-passers, no subset | Rejected Gal's middle-level subset fallback to preserve the full degradation curve. Cost (at 55% L0-pass-rate midpoint, 287 L0-passer cells per model): $237 GPT ablation for full L1–L4 vs ~$118 GPT for outer-only L1+L4, or ~$78 GPT for outer-only L1+L4 on a ~190-cell subset — chose the first. Reviewer value: can report monotonic degradation across levels, not just two endpoints. | Decided |
| **[2026-04-16]** No audit sample of L0-failers | Simplicity over reversal visibility. **COMMITMENT (not yet fulfilled):** paper's threats-to-validity section **must** acknowledge L0-failers were not evaluated under perturbation — that subsection is an outstanding Phase 4 deliverable, not a completed mitigation. If reviewers pushback, a small audit sample (~20 cells × L1+L4) can be added in a revision for ~$8. | Decided; threats-to-validity subsection TODO |
| **[2026-04-16]** Budget overshoot accepted: GPT ≈ $559 vs Gal's $400 target | Chose full-curve ablation over tight budget adherence. Savings vs original $843 still ~$220. Requires Gal sign-off before Phase A launch. Fallback: raise filter to pass@2-of-3 (~22% → $94 ablation → $416 GPT total). | Pending Gal sign-off |
| **[2026-04-16]** Models: Qwen 3.5 397B + Azure GPT-5.3 Chat (both thinking=ON, reasoning_effort=medium) | Open-source + proprietary two-track per meeting 2026-04-15. Drops gpt-4.1 variants (botched GPT-4.1 mini results + gpt-4.1 non-mini not run). Reflects "best-effort capability" norm under test-time compute scaling. **Caveat:** `azure-gpt-5.3-chat` is NOT yet in `scripts/evaluation/llm_evaluate.py:MODEL_REGISTRY` (only `azure-gpt-4.1` is registered); Task 7 adds it. Exact Azure deployment name pending Le's confirmation. | Decided (implementation pending) |

## Milestones

### Milestone 2: Pipeline Audit & Full Eval Runs (4 Phases)

1. **Pipeline Testing & Uniformity** -- test each pipeline component with real programs from all 5 suites, fix suite-specific code [completed 2026-04-10]
2. **LLM Eval Testing** -- add `azure-gpt-5.3-chat` model, `reasoning_effort` param, Qwen thinking flag, `derive_l0_passers.py`, `--task-list` flag; end-to-end dry-run for 1 kernel per suite with both models
3. **Full Evaluation Runs** -- 3-phase launch: canonical (pass@3 L0) → derive L0-passers → L0-conditional ablation (pass@1 L1-L4) for Qwen 3.5 397B + Azure GPT-5.3 Chat
4. **NeurIPS Paper** -- rewrite sections of `overleaf_main.tex`, every claim traceable to verified results

### Milestone 3: NeurIPS 2026 Submission
Submit by May 1, 2026. Datasets & Benchmarks track.

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-04-16 after Gal + Samyak confirmed canonical + L0-conditional ablation design (supersedes two-campaign structure)*
