# ParBench

## What This Is

ParBench is a kernel-centric benchmark framework for evaluating LLM-based parallel code translation (CUDA ↔ OpenMP ↔ OpenCL). It provides 96 executable specs across 5 benchmark suites, a build-run-verify harness, an AST-driven augmentation engine for robustness testing, and a two-campaign evaluation protocol. The current sprint hardens the full pipeline with TDD, integrates a new LLM provider (AskSage/Argonne), and runs multi-model evaluations for NeurIPS 2026 submission.

## Core Value

Every evaluation result is reproducible and pipeline-correct — so model comparisons in the NeurIPS paper are defensible under peer review.

## Requirements

### Validated

- ✓ 96 executable specs across 5 suites (60 Rodinia, 4 XSBench, 4 RSBench, 3 mixbench, 25 HeCBench) — existing
- ✓ Build-run-verify harness (3-stage, conjunctive exit-code + stdout-pattern verification) — existing
- ✓ AST-driven augmentation engine (6 transforms, L0–L4 intensity levels, libclang-backed) — existing
- ✓ Campaign 1 eval pipeline (pass@1, self-repair up to 3 retries, L0–L4, temp=0) — existing
- ✓ LLM provider adapters: Together AI, Azure OpenAI, Anthropic (all OpenAI-compatible) — existing
- ✓ Qwen 3.5 397B pilot results (1,248 eval results, 31.0% non-KNOWN_FAIL pass rate) — existing
- ✓ Cross-API arg + verification handling (source args + union stdout pattern) — existing
- ✓ Regex combiner bug fixed (_wrap_pattern, scoped inline flags) — 2026-04-09

### Active

- [ ] Full-stack TDD coverage: spec/manifest → harness stages → eval pipeline → results analysis
- [ ] Campaign 2 eval pipeline: pass@k (k=3 default), single-shot no self-repair, L0 only, temp=0.7
- [ ] AskSage API adapter: POST /server/query, bearer-token auth, model-selectable, non-OpenAI format
- [ ] Multi-model Campaign 1 + Campaign 2 evaluations via AskSage (same 5 suites, consistent with Qwen baseline)
- [ ] Fair model comparison results analysis (Qwen as yardstick, consistent denominators)
- [ ] NeurIPS 2026 paper (Datasets & Benchmarks track)

### Out of Scope

- Repository-level (full build-system) translation — kernel isolation is a deliberate design choice
- New benchmark suites beyond current 5 — scope is fixed for NeurIPS submission
- SYCL/HIP as primary evaluation directions — case study status only, not in main results
- CI/CD for compilation or eval — all eval runs are manual on the Linux GPU machine
- Dashboard visual redesign — update only if driven by results analysis changes

## Context

- **Existing results:** Qwen 3.5 397B (1,248 files, Campaign 1 done); GPT-4.1 mini (897 files, 209 non-Rodinia invalid — empty prompts from Argonne machine, need re-run)
- **Running sessions:** tmux `qwen_hecbench` and `qwen_small` — must not be touched
- **AskSage:** API schema partially confirmed (endpoint, auth, model param); response format awaiting researcher confirmation
- **Audit status:** Regex combiner audited+fixed (2026-04-09); harness and augmentation not yet audited at same depth; results analysis not yet systematically audited
- **8 KNOWN_FAIL specs** (texture<>/CUDA12, missing GL, pre-existing runtime failures) — excluded from eval denominators
- **5 phantom specs** deleted from specs/ but entries remain in manifest.jsonl (append-only) — 15 expected schema validation errors, do not fix

## Constraints

- **Timeline:** NeurIPS 2026 deadline ~May (abstracts) / June (full papers) 2026
- **Data immutability:** Never modify existing result JSONs — use --resume to append
- **Audit-first:** Pipeline must be hardened before new model evals are trusted
- **AskSage schema:** Adapter design blocked until full response schema confirmed by researcher
- **Lean planning:** PROJECT.md stays lightweight; phases added to milestones incrementally as work is scoped

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Campaign 1 = pass@1 + self-repair + L0–L4, temp=0 | Measures robustness and model's ability to repair; deterministic | ✓ Good |
| Campaign 2 = pass@k=3 + single-shot + L0 only, temp=0.7 | Measures stochastic sampling capability independent of self-repair | — Pending |
| Audit-first before new model evals | Trust in pipeline correctness needed before paper claims | — Pending |
| Qwen 3.5 397B as baseline yardstick | Existing pilot data; most complete coverage across all 5 suites | ✓ Good |
| Kernel-centric isolation (build infrastructure provided) | Separates translation skill from build-system generation skill | ✓ Good |
| AskSage non-OpenAI adapter (separate module) | API format incompatible with current openai-SDK-based dispatch | — Pending |
| TDD for every audit stage | Tests written before/alongside auditing so regressions are caught | — Pending |

## Milestones

### Milestone 2: Benchmark Audit & Hardening
Systematic bottom-up audit + TDD hardening of the full ParBench stack:
1. Benchmark sources — spec correctness, manifest integrity, source code across all 5 suites
2. Harness pipeline — build/run/verify stages, verifier conjunction semantics, cross-API logic
3. Eval pipeline — Campaign 1 + Campaign 2 setup, AskSage adapter, prompt construction, extraction, retry
4. Results analysis — aggregation scripts, statistical methods, fair model comparison

### Milestone 3: NeurIPS 2026 Paper
Write the paper with confidence after audit. All SC26 work carries forward. NeurIPS Datasets & Benchmarks track.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-09 after initialization*
