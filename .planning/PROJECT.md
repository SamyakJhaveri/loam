# ParBench

## What This Is

A build-run-verify benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. ParBench provides 96 specs across 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench) with 35 unique kernels spanning 12 domain categories and SLoC range 80-3304. The framework includes a 5-level augmentation engine for robustness probing, provenance-tracked analysis pipelines, and publication-quality figure generation.

## Core Value

Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

## Current State

**Shipped:** v1.0 SC26 Paper Completion Sprint (2026-04-06)

The SC26 paper (`docs/paper/latex/overleaf.tex`) is submission-ready with:
- 39/39 requirements satisfied (35 with 3-source cross-reference, 4 via SUMMARY+VALIDATION for phases 11, 12.1, 13, 14 which lack VERIFICATION.md)
- 1,287 evaluation tasks across 2 models (710 Qwen 3.5 397B + 577 GPT-4.1 mini)
- Cross-model statistical comparison: chi2=7.83, p=0.005, Cohen's h=0.16
- 13 publication-quality figures wired into paper.tex + appendices.tex
- 14-dimension quantitative analysis with provenance tracking (197 `% src:` comments)
- 10 simulated SC26 reviewer items addressed
- 9 non-blocking tech debt items documented
- Phase 20 complete — all GPT-4.1 mini numbers updated with expanded XSBench dataset (942 result files)

**Completed (previously pending):**
- ✓ GPT-4.1 mini results integration (577 tasks, 30.7% pass rate)
- ✓ Cross-model statistical comparison (30 common kernels, 7 translation directions)
- ✓ All three LaTeX files synced with fresh analysis data

**Remaining (v2 scope):**
- Performance/timing analysis with kernel-level profiling

## Requirements

### Validated

- ✓ ParBench framework (harness, specs, augmentation engine) — pre-existing
- ✓ 96 specs across 5 suites — pre-existing
- ✓ Qwen 3.5 397B primary campaign (710 tasks, 38.0% pass rate) — v1.0
- ✓ Data verification pipeline (VERIFY-01 through VERIFY-06) — v1.0
- ✓ Benchmark characterization (CHAR-01 through CHAR-07) — v1.0
- ✓ Introduction & positioning (INTRO-01 through INTRO-04) — v1.0
- ✓ Augmentation story (AUG-01 through AUG-04) — v1.0
- ✓ Methodology & reviewer defense (METHOD-01 through METHOD-04) — v1.0
- ✓ Quantitative analysis (QUANT-01 through QUANT-14) — v1.0
- ✓ Analysis pipeline regeneration (REGEN-01 through REGEN-10) — v1.0
- ✓ Figure regeneration (FIG-01 through FIG-07) — v1.0
- ✓ Paper TeX integration (TEX-01 through TEX-09) — v1.0

### Active

- [ ] GPT-4.1 mini results integrated into all tables and analysis
- [ ] Cross-model statistical comparison (chi-squared, effect sizes)
- [ ] Augmentation trend graphs with second model overlay

### Out of Scope

- Mobile app or web interface — CLI benchmark tool
- Performance/timing analysis — wall-clock times unreliable; kernel profiling not yet done
- Offline/cached LLM evaluation — requires live API access

## Context

**Tech stack:** Python 3, libclang (AST transforms), matplotlib (figures), scipy/statsmodels (statistics)
**Codebase:** ~350 files modified in v1.0 sprint (74,714 insertions)
**Team:** Samyak Jhaveri (primary), Le Chen (ANL, GPT evals), Niranjan Hasabnis (advisor)
**Key artifacts:** paper_data.json, quantitative_findings.json, 13 figure PDFs, paper.tex

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Replaced Gemini with GPT-4.1 mini | Le running GPT evals via Azure OpenAI | ✓ Done |
| "Provider diversity" framing | GPT-4.1 mini architecture undocumented | ✓ Good |
| Focus pre-results sections first | Results depend on pending campaigns | ✓ Good |
| Augmentation null result as strength | z=0.0, p=1.0 — augmentation safe | ✓ Good |
| Kernel isolation as differentiator | ParEval-Repo 0% vs ParBench 68.8% | ✓ Good |
| Drop Phase 6 (RSBench re-spec) | Multi-file hypothesis proven by data | ✓ Good |
| Drop Phase 10 (narrative doc) | Write directly from quantitative data | ✓ Good |
| Insert Phase 12.1 (P0 fixes) | Urgent factual fixes before integration | ✓ Good |
| Dual-scope Section 6 | Rodinia 480 primary + 710 all-suite cross-comparison | ✓ Good |
| PNG architecture diagram | No draw.io PDF export on Linux | ⚠️ Revisit |

## Constraints

- **Deadline**: April 8, 2026 — hard SC26 submission deadline
- **Page limit**: ~10 pages IEEE double-column format
- **Framing**: Benchmark paper, not model evaluation paper
- **Result immutability**: Never modify existing result JSONs
- **HeCBench source**: Cloned locally (gitignored, 1874 dirs) — no version pinning

---
*Last updated: 2026-04-08 after Phase 20 completion*
