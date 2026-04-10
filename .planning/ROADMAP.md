# Roadmap: ParBench NeurIPS 2026

## Overview

This roadmap takes ParBench from a pilot-validated benchmark (Qwen 3.5 397B, 1,248 results) to a multi-model, peer-review-ready NeurIPS submission. Four phases: verify the pipeline with real data, test end-to-end evaluation, run full campaigns, write the paper.

## Phases

- [ ] **Phase 1: Pipeline Testing & Uniformity** -- Test and fix the full spec-build-run-verify pipeline across all 5 suites
- [ ] **Phase 2: LLM Eval Testing** -- Test evaluation pipeline end-to-end with real LLM calls
- [ ] **Phase 3: Full Evaluation Runs** -- Run complete Campaign 1 + Campaign 2 with all models
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

**Goal:** Can run `run_eval_batch.py --campaign c1` and `--campaign c2` for 1 kernel per suite with Qwen, get correct result JSONs, and `campaign_for()` correctly classifies them.

**Depends on:** Phase 1

**Deliverables:**
- `campaign_for(record)` helper: returns `"c1"` or `"c2"` based on `temperature` + `sample_id` fields
- `--campaign c1|c2` convenience flag on `run_eval_batch.py` (sets correct defaults)
- Prompt construction verified for each suite via `--dry-run`
- Real LLM calls tested: 1 program per suite, cuda-to-omp direction, via Qwen/Together AI
- Campaign 2 verified: `pass_at_k()` produces correct results for k=3 with actual C2 data
- AskSage adapter: BLOCKED until Le provides API docs -- do not build speculatively

**Success Criteria:**
1. `campaign_for()` correctly classifies existing C1 and C2 results
2. End-to-end eval works for 1 kernel per suite with Qwen
3. Result JSONs contain correct fields (prompt_tokens, completion_tokens, overall_status, attempts[])
4. `pass_at_k(k=3)` returns correct values for known inputs
5. Campaign 2 config validated: temp=0.7, num_samples=3, max_retries=1, augment_level=0

### Phase 3: Full Evaluation Runs

**Goal:** Complete Campaign 1 and Campaign 2 runs for all suites and directions with Qwen (+ AskSage when unblocked).

**Depends on:** Phase 2

**Deliverables:**
- Campaign 1: temp=0, max_retries=3, L0-L4, all suites, all directions (including cuda<->omp_target for XSBench/RSBench)
- Campaign 2: temp=0.7, num_samples=3, max_retries=1, L0-only, same directions
- Qwen: use `--resume` to fill gaps in existing 1,248 results
- AskSage: new runs when unblocked
- Analysis: `analyze_eval.py` regenerated for each model + campaign

**Success Criteria:**
1. All Campaign 1 + Campaign 2 Qwen runs complete (no gaps)
2. Pass rates, status distributions, per-suite breakdowns verified
3. AskSage runs complete (when unblocked)

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

**Execution Order:** Phase 1 -> Phase 2 -> Phase 3 -> Phase 4

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Pipeline Testing & Uniformity | In progress | - |
| 2. LLM Eval Testing | Not started | - |
| 3. Full Evaluation Runs | Not started | - |
| 4. NeurIPS Paper | Not started | - |
