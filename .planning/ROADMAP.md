# Roadmap: ParBench NeurIPS 2026

## Overview

This roadmap takes ParBench from a pilot-validated benchmark (Qwen 3.5 397B, 1,248 results) to a multi-model, peer-review-ready NeurIPS submission. The work is ordered audit-first: TDD infrastructure, then bottom-up pipeline hardening (specs, harness, eval, providers/analysis), then the paper. Every phase delivers testable correctness guarantees that compound -- so by the time new model evals run and the paper is written, every claim is defensible.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: TDD Infrastructure** - Test scaffold (conftest.py, dev deps, mock pattern) that all audit phases build on
- [ ] **Phase 2: Spec & Manifest Audit** - Verify all 96 specs, centralize exclusions, validate HeCBench L1-L4, unify analysis scripts
- [ ] **Phase 3: Harness Pipeline Audit** - Test-cover all harness failure modes, verifier semantics, and cross-API logic
- [ ] **Phase 4: Eval Pipeline & Campaign 2** - Campaign partitioning, pass@k implementation, integration tests, Campaign 2 config
- [ ] **Phase 5: Provider Integration & Analysis Audit** - AskSage adapter, dry-run auth, analysis script correctness, GPT re-run
- [ ] **Phase 6: NeurIPS Paper** - Write paper with every claim traceable to verified results; submit by May 1

## Phase Details

### Phase 1: TDD Infrastructure
**Goal**: A working test scaffold exists so every subsequent audit phase can write tests first
**Depends on**: Nothing (first phase)
**Requirements**: TDD-01, TDD-02, TDD-03
**Success Criteria** (what must be TRUE):
  1. `pytest tests/` runs successfully with conftest.py providing session-scoped fixtures for specs, result JSONs, and mock LLM providers
  2. All four dev test dependencies (pytest-mock, respx, pytest-subprocess, pytest-asyncio) are installed and importable
  3. A reference test exists demonstrating the mock-at-call_llm() boundary pattern that all eval pipeline tests will follow
**Plans**: TBD

### Phase 2: Spec & Manifest Audit
**Goal**: Every spec in the benchmark is verified correct, exclusion lists are canonical, and HeCBench augmentation levels are validated -- so new model evals run against a trusted spec set
**Depends on**: Phase 1
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05
**Success Criteria** (what must be TRUE):
  1. Every non-KNOWN_FAIL spec either has a `stdout_pattern` in its verification config or carries an explicit exemption flag
  2. `EXCLUDED_SPECS` is a single importable constant used by all analysis scripts (no stale duplicates)
  3. All 23 passing HeCBench specs pass at augmentation levels L1-L4 (M10b-protocol retest), confirming level-invariance across all 5 suites
  4. `python3 scripts/analysis/analyze_batch.py --suite hecbench` (and all other suites) works correctly
  5. Manifest integrity check passes for all 5 suites (no phantom entries beyond the 5 known deleted specs)
**Plans**: TBD

### Phase 3: Harness Pipeline Audit
**Goal**: The build-run-verify harness is test-covered so failures are caught before they pollute evaluation results
**Depends on**: Phase 1
**Requirements**: HARN-01, HARN-02, HARN-03, HARN-04
**Success Criteria** (what must be TRUE):
  1. Unit tests exist and pass for all 4 harness failure modes: BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, TIMEOUT
  2. Verifier conjunction semantics are tested -- a single strategy failure short-circuits the overall result to VERIFY_FAIL
  3. Cross-API stdout union pattern (source|target) is tested for both match and mismatch cases
  4. `_is_kernel_only_translation()` heuristic is tested for .cl detection and edge cases (non-.cl files, mixed extensions)
**Plans**: TBD

### Phase 4: Eval Pipeline & Campaign 2
**Goal**: The evaluation pipeline supports both Campaign 1 (pass@1 + self-repair) and Campaign 2 (pass@k + single-shot) with proper result partitioning -- so multi-campaign model evals can run
**Depends on**: Phase 1, Phase 2, Phase 3
**Requirements**: EVAL-01, EVAL-02, EVAL-03, EVAL-04
**Success Criteria** (what must be TRUE):
  1. `evaluate_translation()` accepts `--campaign-id c1|c2` and writes results to `results/evaluation/{model}/{c1,c2}/` (existing Qwen results land in c1/)
  2. `compute_pass_at_k(k=3)` returns correct values for known inputs (all-pass, all-fail, mixed)
  3. Integration tests cover self-repair loop, sample naming (-s0/-s1/-s2), extraction failure, and cross-API arg/verify handling
  4. Campaign 2 end-to-end config validated: temp=0.7, num_samples=3, max_retries=1, augment_level=0
**Plans**: TBD

### Phase 5: Provider Integration & Analysis Audit
**Goal**: AskSage adapter is ready for multi-model evals and analysis scripts produce correct, fair cross-model comparisons
**Depends on**: Phase 1, Phase 4
**Requirements**: PROV-01, PROV-02, PROV-03, PROV-04, ANLYS-01, ANLYS-02, ANLYS-03, ANLYS-04
**Success Criteria** (what must be TRUE):
  1. `call_llm()` dispatches to AskSage via OpenAI-compatible base_url swap when model starts with "asksage-"
  2. A dry-run API call at batch start aborts cleanly if AskSage auth fails (24-hour token expiry handled)
  3. `_kernel_from_spec()` and `_direction_from_ids()` pass parametrized tests for all 5 suite prefixes
  4. `cross_model_comparison.py` emits a warning when suite-asymmetric denominators are detected
  5. GPT-4.1 mini non-Rodinia results are re-run locally (replacing 209 invalid empty-prompt results)
**Plans**: TBD

**Note**: PROV-04 (native /server/query fallback) is blocked on external schema from researcher. Implementation will proceed when schema is provided; other PROV requirements are independent.

### Phase 6: NeurIPS Paper
**Goal**: A complete NeurIPS Datasets & Benchmarks paper where every quantitative claim is traceable to verified result files on disk
**Depends on**: Phase 2, Phase 3, Phase 4, Phase 5
**Requirements**: PAPER-01, PAPER-02
**Success Criteria** (what must be TRUE):
  1. Every quantitative claim in the paper (pass rates, model comparisons, augmentation effects) has a traceable path to specific result JSON files on disk
  2. Paper is submitted to NeurIPS 2026 Datasets & Benchmarks track by May 1, 2026
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6
(Phases 2 and 3 can execute in parallel after Phase 1 completes)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. TDD Infrastructure | 0/TBD | Not started | - |
| 2. Spec & Manifest Audit | 0/TBD | Not started | - |
| 3. Harness Pipeline Audit | 0/TBD | Not started | - |
| 4. Eval Pipeline & Campaign 2 | 0/TBD | Not started | - |
| 5. Provider Integration & Analysis Audit | 0/TBD | Not started | - |
| 6. NeurIPS Paper | 0/TBD | Not started | - |
