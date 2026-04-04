# SC26 Paper Completion Sprint

## What This Is

A focused sprint to complete and strengthen the SC26 ParBench paper (`docs/paper/latex/paper.tex`) before the April 8, 2026 submission deadline. The paper presents ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. This sprint covers all tasks achievable with existing Qwen 3.5 397B evaluation data, focusing on pre-results sections (Sections 1-5) and quantitative rigor.

## Core Value

Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

## Requirements

### Validated

- [x] ParBench framework implemented (harness, specs, augmentation engine) -- existing
- [x] 96 specs across 5 suites (Rodinia 60, XSBench 4, RSBench 4, mixbench 3, HeCBench 25) -- existing
- [x] Qwen 3.5 397B primary campaign: 480 tasks, 36.2% [32.1%, 40.6%] overall pass rate -- verified against paper_data.json
- [x] Augmentation engine: 6 transforms, 5 levels (L0-L4), 68/88 non-KNOWN_FAIL specs PASS at all levels -- existing
- [x] pass@k campaign: 426 tasks at temperature 0.7 -- existing
- [x] Self-repair analysis: 17.5% first-attempt -> 36.2% final (22.7% repair rate) -- existing
- [x] Statistical analysis: Cochran-Armitage z=-0.17, p=0.87 (augmentation null result) -- existing
- [x] Session C1 (Gemini -> GPT-4.1 mini text replacement) -- commit 28b510a
- [x] Analysis pipeline: paper_data.json, statistical_analysis.json, selfrepair_analysis.json, error_taxonomy.json -- existing
- [x] Related work section with 10-paper comparison table -- existing
- [x] Cross-check all numerical claims in Sections 1-5 against ground truth data files -- Validated in Phase 1
- [x] Verify/update augmentation level definitions table against actual LEVEL_FRACTIONS in code -- Validated in Phase 1
- [x] Verify suite-summary table (35 kernels, 96 specs) against manifest.jsonl + specs/ count -- Validated in Phase 1
- [x] Verify model config table post-C1 (Qwen + GPT-4.1 mini descriptions coherent) -- Validated in Phase 1
- [x] Verify hardware/software table against actual system (nvcc, gcc versions) -- Validated in Phase 1
- [x] Benchmark characterization table (SLoC, categories, multi-file, API coverage, language features) -- Validated in Phase 2
- [x] Extend SLoC analysis from 18 to all 35 kernels -- Validated in Phase 2 (35 kernels, range 80-3304)
- [x] Language feature grep (OpenMP 1.0-4.5, CUDA basic-9.0+, OpenCL 1.x-2.0) in source dirs -- Validated in Phase 2
- [x] Language standard distribution from spec JSONs -- Validated in Phase 2 (206 specs)
- [x] Domain category distribution from manifest.jsonl -- Validated in Phase 2 (12 categories)

### Active

- [ ] Quantitative highlights woven into Introduction (not bullet lists)
- [ ] Multi-file translation emphasis (36.9% of specs) in intro + Section 4
- [ ] LASSI differentiation beyond build-run-verify (augmentation, multi-suite, survey-grounded curation)
- [ ] Augmentation motivating examples (per-kernel x per-level matrix, 2-3 degradation examples or strengthened null-result interpretation)
- [ ] Strengthen "reviewer defense" for kernel isolation methodology
- [x] Re-run analysis scripts against complete 1,248-file dataset (all 10 REGEN requirements verified) -- Validated in Phase 7
- [ ] Augmentation trend graphs (per-kernel + aggregate, publication quality)

### Out of Scope

- GPT-4.1 mini data integration -- blocked on Le's eval runs completing
- Non-Rodinia Qwen eval data analysis -- UNBLOCKED: 1,248 results across 5 suites, analyzed in Phase 7
- Results section (Section 6+) data updates -- depends on completed campaigns
- Performance/timing analysis -- wall-clock times unreliable per known-issues.md
- New eval runs or re-runs -- DO NOT TOUCH running tmux sessions
- Any modification to existing result JSONs -- results are immutable
- New spec creation or modification -- benchmark is frozen for paper

## Context

**Deadline:** April 8, 2026 (SC26 paper submission)

**Team:**
- Samyak Jhaveri: primary author, running Qwen evals on Linux GPU machine
- Le Chen (ANL collaborator): running GPT-4.1 mini evals on separate infrastructure
- Niranjan Hasabnis: advisor, provided direction at April 2 meeting

**Current eval state (as of 2026-04-04):**
- 1,248 Qwen result files on disk across 5 suites (Rodinia, HeCBench, XSBench, RSBench, mixbench)
- tmux sessions COMPLETE (qwen_hecbench, qwen_small) -- safe to close
- Le running GPT-4.1 mini campaigns in parallel
- All analysis files regenerated in Phase 7 (eval_summary, paper_data, error_taxonomy, selfrepair, statistical, token)

**Key meeting directives (Niranjan, 2026-04-02):**
- FRAMING RULE: This is a BENCHMARK paper, not an LLM evaluation paper
- Augmentation motivating examples are "most important task"
- Benchmark characterization table with concrete numbers
- Multi-file translation handling as key differentiator
- Quantitative highlights in introduction

**LASSI differentiation challenge:** LASSI also does build-run-verify on HPC kernels (10 HeCBench, 80-85% with agentic self-correction). ParBench differentiates via: (1) augmentation robustness probing, (2) 5 suites vs 1, (3) 6 directions vs 2, (4) survey-grounded curation, (5) raw model capability vs agentic pipeline, (6) 96 specs vs 10 kernels.

## Constraints

- **Deadline**: April 8, 2026 -- hard SC26 submission deadline
- **Data availability**: Only existing Qwen Rodinia data is complete; non-Rodinia and GPT data pending
- **Running evals**: Two tmux sessions MUST NOT be touched (qwen_hecbench, qwen_small)
- **Result immutability**: Never modify existing result JSONs
- **Page limit**: ~10 pages IEEE double-column format
- **Framing**: Benchmark paper, not model evaluation paper
- **HeCBench source**: Cloned locally (gitignored, 1874 dirs) — not a git submodule, so no version pinning

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Replaced Gemini 2.5 Flash with GPT-4.1 mini | Le running GPT evals via Azure OpenAI | Done (28b510a) |
| "MoE vs dense" framing -> "provider diversity" | GPT-4.1 mini architecture not publicly documented | Done (28b510a) |
| Focus pre-results sections first | Results section depends on pending campaign data | -- Pending |
| Augmentation null result as strength | z=-0.17, p=0.87 means augmentation is safe, models fail structurally | -- Pending |
| Kernel isolation as key differentiator | ParEval-Repo 0% vs ParBench 68.8% on same kernel (XSBench) | -- Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check -- still the right priority?
3. Audit Out of Scope -- reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-03 after initialization*
