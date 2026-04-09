# Requirements: ParBench

**Defined:** 2026-04-09
**Core Value:** Every evaluation result is reproducible and pipeline-correct — so model comparisons in the NeurIPS paper are defensible under peer review.

## v1 Requirements

### TDD Foundation

- [ ] **TDD-01**: `tests/conftest.py` exists with session-scoped fixtures for specs, result JSONs, and mock LLM providers
- [ ] **TDD-02**: `pytest-mock`, `respx`, `pytest-subprocess`, `pytest-asyncio` installed as dev deps
- [ ] **TDD-03**: Mock-at-`call_llm()` boundary pattern used consistently across all eval pipeline tests

### Spec/Manifest Audit

- [ ] **SPEC-01**: Every spec has `stdout_pattern` in verification OR carries an explicit exemption flag (prevents S-VERIFY false-positive recurrence)
- [ ] **SPEC-02**: `EXCLUDED_SPECS` centralized as one importable constant shared by all analysis scripts (currently duplicated and stale in `analyze_eval.py` and `generate_paper_data.py` — missing 2 HeCBench KNOWN_FAILs)
- [ ] **SPEC-03** *(high priority — prerequisite for new model evals)*: HeCBench 23 passing specs verified PASS at augmentation levels L1–L4 via M10b-protocol retest (validates level-invariance claim for all 5 suites, not just Rodinia+XSBench)
- [ ] **SPEC-04**: Manifest integrity verified across all 5 suites (no phantom entries, all live specs present)
- [ ] **SPEC-05**: `scripts/analysis/analyze_batch.py` accepts `--suite <name>` parameter and works for all 5 suites (replaces Rodinia-only `analyze_rodinia_batch.py`)

### Harness Pipeline Audit

- [ ] **HARN-01**: Unit tests cover all 4 harness failure modes: BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, TIMEOUT
- [ ] **HARN-02**: Verifier conjunction semantics tested — ALL strategies must pass, single failure short-circuits
- [ ] **HARN-03**: Cross-API stdout union pattern (`source_pattern|target_pattern`) tested for both match and mismatch cases
- [ ] **HARN-04**: `_is_kernel_only_translation()` heuristic tested for `.cl` detection and edge cases

### Eval Pipeline + Campaign 2 Infrastructure

- [ ] **EVAL-01**: `evaluate_translation()` accepts `--campaign-id c1|c2` CLI flag; results written to `results/evaluation/{model}/{c1,c2}/` directory partition (existing Qwen results in `c1/` by convention)
- [ ] **EVAL-02**: `compute_pass_at_k()` implements pass@k=n (pass@3 = 1 iff all 3 samples pass, else 0) and is tested against known values
- [ ] **EVAL-03**: Integration tests for `evaluate_translation()` covering: self-repair loop (max retries), sample naming (`-s0/-s1/-s2`), extraction failure (malformed/truncated response), cross-API arg/verify handling
- [ ] **EVAL-04**: Campaign 2 configuration validated end-to-end (temp=0.7, num_samples=3, max_retries=1, augment_level=0)

### Provider Integration (AskSage)

- [ ] **PROV-01**: AskSage `elif model.startswith("asksage-")` branch added to `call_llm()` at line 764 with MODEL_REGISTRY entry
- [ ] **PROV-02**: OpenAI-compatible `base_url` swap path (`https://api.asksage.anl.gov/server/openai/v1/`) implemented and dry-run validated against live endpoint
- [ ] **PROV-03**: Dry-run API call at batch start — aborts before any tasks run if auth fails (handles 24-hour token expiry when token not refreshed)
- [ ] **PROV-04**: Native `/server/query` fallback path (`x-access-tokens` header, `{"query": "..."}` format) if OpenAI-compat path unavailable at Argonne *(blocked on full response schema from researcher)*

### Results Analysis Audit

- [ ] **ANLYS-01**: `_kernel_from_spec()` and `_direction_from_ids()` parametrized tests cover all 5 suite prefixes (rodinia, xsbench, rsbench, mixbench, hecbench)
- [ ] **ANLYS-02**: Suite-asymmetric denominator warning emitted by `cross_model_comparison.py` when intersection collapses to fewer than all expected suites
- [ ] **ANLYS-03**: GPT-4.1 mini non-Rodinia eval results re-run locally (replaces 209 invalid empty-prompt results from Argonne machine)
- [ ] **ANLYS-04**: `generate_paper_data.py` emits warning when `--suite` filter is applied asymmetrically across models in a comparison

### NeurIPS Paper

- [ ] **PAPER-01**: Paper written with every quantitative claim traceable to verified result files on disk
- [ ] **PAPER-02**: Submitted to NeurIPS 2026 Datasets & Benchmarks track by **May 1, 2026**

## v2 Requirements

### Visualization

- **VIZ-01**: Dashboard updated to show multi-model comparison across all 5 suites
- **VIZ-02**: per-suite pass rate breakdown in GitHub Pages dashboard

### Extended Provider Support

- **PROV-05**: AskSage thinking/reasoning mode disable confirmed and enforced (needed for fair cross-model comparison — currently blocked on researcher confirmation)
- **PROV-06**: AskSage completion token ceiling confirmed and enforced (prevents EXTRACTION_FAIL on multi-file kernels — same class of bug as Groq-llama heartwall/myocyte)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Repository-level (full build-system) translation | Kernel isolation is deliberate design — fixing this is a different paper |
| New benchmark suites beyond current 5 | Scope fixed for NeurIPS submission |
| SYCL/HIP as primary evaluation directions | Case study status only; not in main paper claims |
| CI/CD for compilation or eval runs | All evals are manual on the Linux GPU machine by design |
| Real-time eval dashboard | Only update if driven by results analysis changes |
| VCR cassettes for LLM test mocking | Non-deterministic responses cause cassette rot; mock `call_llm()` directly |

## Traceability

*(Populated by roadmapper)*

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDD-01 | — | Pending |
| TDD-02 | — | Pending |
| TDD-03 | — | Pending |
| SPEC-01 | — | Pending |
| SPEC-02 | — | Pending |
| SPEC-03 | — | Pending |
| SPEC-04 | — | Pending |
| SPEC-05 | — | Pending |
| HARN-01 | — | Pending |
| HARN-02 | — | Pending |
| HARN-03 | — | Pending |
| HARN-04 | — | Pending |
| EVAL-01 | — | Pending |
| EVAL-02 | — | Pending |
| EVAL-03 | — | Pending |
| EVAL-04 | — | Pending |
| PROV-01 | — | Pending |
| PROV-02 | — | Pending |
| PROV-03 | — | Pending |
| PROV-04 | — | Pending |
| ANLYS-01 | — | Pending |
| ANLYS-02 | — | Pending |
| ANLYS-03 | — | Pending |
| ANLYS-04 | — | Pending |
| PAPER-01 | — | Pending |
| PAPER-02 | — | Pending |

**Coverage:**
- v1 requirements: 26 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 26 ⚠️

---
*Requirements defined: 2026-04-09*
*Last updated: 2026-04-09 after initial definition*
