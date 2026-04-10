# ParBench

## What This Is

ParBench is a kernel-centric benchmark framework for evaluating LLM-based parallel code translation (CUDA <-> OpenMP <-> OpenCL). It provides 96 executable specs across 5 benchmark suites, a build-run-verify harness, an AST-driven augmentation engine for robustness testing, and a two-campaign evaluation protocol. The current milestone verifies every pipeline component with real data, runs full evaluations, and writes the NeurIPS 2026 paper.

## Core Value

Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.

## Requirements

### Validated

- Pipeline (harness, spec_loader, llm_evaluate.py) is already suite-agnostic -- zero `if suite == "rodinia"` in core code
- 96 executable specs across 5 suites (60 Rodinia, 4 XSBench, 4 RSBench, 3 mixbench, 25 HeCBench)
- Build-run-verify harness (3-stage, conjunctive exit-code + stdout-pattern verification)
- AST-driven augmentation engine (6 transforms, L0-L4 intensity levels, libclang-backed)
- Campaign 1 eval pipeline (pass@1, self-repair up to 3 retries, L0-L4, temp=0)
- LLM provider adapters: Together AI, Azure OpenAI, Anthropic (all OpenAI-compatible)
- Qwen 3.5 397B results (1,248 eval results spanning both campaigns)
- Cross-API arg + verification handling (source args + union stdout pattern)
- Regex combiner bug fixed (_wrap_pattern, scoped inline flags) -- 2026-04-09
- `pass_at_k()` implemented in `statistical_analysis.py` and `quantitative_findings.py`
- `run_eval_campaign.sh` handles all 5 suites

### Active (by Phase)

- [ ] **Phase 1:** Pipeline testing and uniformity across all 5 suites (spec loading, build, run, verify)
- [ ] **Phase 2:** LLM eval testing with real calls -- campaign separation via `campaign_for()`, prompt verification, end-to-end eval
- [ ] **Phase 3:** Full evaluation runs -- Campaign 1 + Campaign 2 for Qwen and AskSage model (when unblocked)
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
| Campaign separation via `campaign_for()` helper | Existing results already have `temperature` + `sample_id` fields. No folder restructuring needed. `--resume` preserved. | Decided |
| AskSage marked BLOCKED | Zero code/docs in codebase. Cannot speculatively build adapter without API schema from Le. | Decided |
| Portability deferred | Hardcoded `/opt/nvidia/hpc_sdk/...` paths in specs. Full spec templating deferred to post-NeurIPS unless time permits. Document machine config in paper. | Decided |
| Campaign 1 = pass@1 + self-repair + L0-L4, temp=0 | Measures robustness and model's ability to repair; deterministic | Good |
| Campaign 2 = pass@k=3 + single-shot + L0 only, temp=0.7 | Measures stochastic sampling capability independent of self-repair | Pending |
| Qwen 3.5 397B as baseline yardstick | Existing pilot data; most complete coverage across all 5 suites | Good |
| Kernel-centric isolation (build infrastructure provided) | Separates translation skill from build-system generation skill | Good |
| 4 phases instead of 6 | Removed separate TDD Infrastructure phase (tests alongside real testing), folded Provider Integration into Phase 2, Analysis into Phase 3 | Decided |

## Milestones

### Milestone 2: Pipeline Audit & Full Eval Runs (4 Phases)

1. **Pipeline Testing & Uniformity** -- test each pipeline component with real programs from all 5 suites, fix suite-specific code
2. **LLM Eval Testing** -- test eval pipeline end-to-end with real LLM calls, add campaign separation infrastructure
3. **Full Evaluation Runs** -- run complete Campaign 1 + Campaign 2 with Qwen (+ AskSage when unblocked)
4. **NeurIPS Paper** -- rewrite sections of `overleaf_main.tex`, every claim traceable to verified results

### Milestone 3: NeurIPS 2026 Submission
Submit by May 1, 2026. Datasets & Benchmarks track.

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-04-09 after plan simplification to 4 phases*
