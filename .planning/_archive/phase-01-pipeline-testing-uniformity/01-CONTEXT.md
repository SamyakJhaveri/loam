# Phase 1: Pipeline Testing & Uniformity - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Verify every pipeline component works correctly and uniformly across all 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench). Deliver:
1. Build/run/verify integration tests covering all 5 suites
2. `EXCLUDED_SPECS` centralized as a single importable constant in `harness/constants.py`
3. `analyze_harness_batch.py` replacing the Rodinia-specific batch analyzer
4. Suite-specific hardcoding eliminated from analysis scripts
5. TDD tests for `campaign_for()` (locked interface contract for Phase 2)

Phase 1a (spec loading, 184 tests) is already complete. Phase 1b–1e remain.

</domain>

<decisions>
## Implementation Decisions

### Build/Run/Verify Integration Tests

- **D-01:** Test scope is **sampling** — 1 representative spec per suite. Use the same 5 specs already chosen in `tests/test_spec_loader_integration.py`: `rodinia-bfs-cuda`, `xsbench-xsbench-cuda`, `rsbench-rsbench-cuda`, `mixbench-mixbench-cuda`, `hecbench-bezier-surface-cuda`.
- **D-02:** Tests live in a **new file** `tests/test_harness_integration.py`. Do not extend `test_spec_loader_integration.py`.
- **D-03:** Each test runs the **full pipeline**: `build → run → verify`. If build fails, mark test as failed (not just skipped). Test corresponds to `python3 -m harness verify <spec>` end-to-end.
- **D-04:** KNOWN_FAIL specs are **skipped via `pytest.mark.skip`** using the `EXCLUDED_SPECS` constant (once centralized). Skip message should name the spec and link to KNOWN_FAIL reason.
- **D-05:** Project root is **auto-detected from `conftest.py`** (existing `PROJECT_ROOT` constant). No new env var or CLI flag required.
- **D-06:** Tests are **`@pytest.mark.integration`** to allow skipping on machines without GPU/compilers (matches existing conftest skip mechanism).

### EXCLUDED_SPECS Centralization

- **D-07:** Single source of truth lives in **`harness/constants.py`** (new file). This is the authoritative enforcement point for the 8 KNOWN_FAIL specs.
- **D-08:** All 4 current duplicate definitions are **replaced with imports** from `harness.constants`: `scripts/evaluation/analyze_eval.py`, `scripts/analysis/quantitative_findings.py`, `scripts/analysis/generate_paper_data.py`, `scripts/analysis/token_analysis.py`.
- **D-09:** `harness/constants.py` is **the single source of truth** for the KNOWN_FAIL list. `known-issues.md` documents WHY each spec fails; the code enforces. Both must stay in sync.

### analyze_harness_batch.py (Replaces analyze_rodinia_batch.py)

- **D-10:** Write **`scripts/analysis/analyze_harness_batch.py`** — suite-agnostic, accepts `--suite` flag. **Delete `analyze_rodinia_batch.py` immediately** once the replacement exists. No wrapper, no deprecated stub.
- **D-11:** Output directory: **`results/harness/{suite}/`** (new namespace, separate from existing `results/rodinia/logs/`). Old Rodinia results in `results/rodinia/logs/` are left untouched — they are historical.
- **D-12:** Output files per run:
  - `results/harness/{suite}/{suite}_results.json` — structured JSON summary
  - `results/harness/{suite}/results_matrix_{suite}.md` — kernel × API matrix (same format as existing Rodinia matrix)

### Suite-Specific Cleanup in Analysis Scripts

- **D-13:** `scripts/analysis/quantitative_findings.py` — replace `rodinia_c1_total`/`rodinia_c1_pass` counters (line ~3064) with a **per-suite dict** (e.g. `suite_c1_counts: dict[str, int]`). Spot-checks should work for all suites, not just Rodinia.
- **D-14:** `scripts/analysis/classify_translation_pairs.py` — replace the hardcoded Rodinia-only direction breakdown (line ~167) with a **`--suite` filter flag** (default: all suites combined; pass `--suite rodinia` to get Rodinia-only behavior).
- **D-15:** Evaluation pipeline files (`harness/`, `scripts/evaluation/`) — already have no suite-specific hardcoding. Verify, do not change.

### Campaign Classification Tests (TDD for Phase 2)

- **D-16:** Write **`tests/test_campaign_classification.py`** with the locked interface contract for `campaign_for()`. Mark all tests `@pytest.mark.skip(reason="campaign_for() not yet implemented — Phase 2")`. Phase 2 removes the skip when implementing.
- **D-17:** Interface contract (locked): `campaign_for(record: dict) -> str` where `record` is a result JSON dict. Returns `'c1'` or `'c2'`.
- **D-18:** C2 classification logic: `temperature != 0.0 OR sample_id is not None`. Either signal → C2.
- **D-19:** Minimum test cases to cover:
  - `{temperature: 0.0, sample_id: None}` → `'c1'`
  - `{temperature: 0.7, sample_id: 's1'}` → `'c2'`
- **D-20:** `campaign_for()` will ultimately live in **`scripts/evaluation/campaign_utils.py`** (Phase 2 creates this file). The TDD tests should import from that path.

### Claude's Discretion

- Test fixture structure in `test_harness_integration.py` (parameterization approach, fixture names)
- Exact content/docstring of `harness/constants.py` beyond `EXCLUDED_SPECS`
- Whether `analyze_harness_batch.py` uses `argparse` or `click`
- Internal structure of per-suite dict in `quantitative_findings.py` cleanup

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Project Context
- `.planning/REQUIREMENTS.md` §Phase 1 — Authoritative acceptance criteria checklist for Phase 1
- `.planning/PROJECT.md` — Key decisions table, architecture, out-of-scope items

### Active Guardrails
- `.claude/rules/known-issues.md` — KNOWN_FAIL spec list (8 specs), OMP run arg rules, EXCLUDED_SPECS policy
- `.claude/rules/spec-conventions.md` — Spec naming, categories, run arg verification protocol

### Existing Code to Extend/Replace
- `tests/conftest.py` — Existing skip mechanism (integration test guard) to extend
- `tests/test_spec_loader_integration.py` — Reference for the 5 sample specs per suite (reuse exact same set) and integration test structure
- `harness/models.py` — Existing harness types (Status, BuildResult, etc.) — `harness/constants.py` should not duplicate these
- `scripts/analysis/analyze_rodinia_batch.py` — File to replace; read for output format reference before writing the new version
- `scripts/analysis/quantitative_findings.py` lines ~3055-3085 — Rodinia-specific spot-check counter to generalize
- `scripts/analysis/classify_translation_pairs.py` lines ~162-180 — Rodinia-only direction breakdown to generalize with --suite flag
- `scripts/evaluation/analyze_eval.py` lines ~49-58 — One of 4 EXCLUDED_SPECS definitions to replace with import

### EXCLUDED_SPECS (all 4 copies to replace with import)
- `scripts/analysis/generate_paper_data.py` lines ~43-60
- `scripts/analysis/token_analysis.py` lines ~44-60
- `scripts/analysis/quantitative_findings.py` lines ~51-70
- `scripts/evaluation/analyze_eval.py` lines ~49-58

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/conftest.py`: `PROJECT_ROOT` constant + `pytest.mark.integration` skip guard — extend this for `test_harness_integration.py`
- `tests/test_spec_loader_integration.py`: The 5-suite sample dict (`SUITE_SAMPLE_SPECS`) and fixture pattern — use identical spec set for harness tests
- `harness/cli.py`: `verify` subcommand = the equivalent of `build → run → verify`; the integration test should invoke the harness via Python API not subprocess
- `harness/builder.py`, `harness/runner.py`, `harness/verifier.py`: The 3 pipeline stages to call in sequence

### Established Patterns
- Integration tests use `@pytest.mark.integration` + conftest skip to protect CI (no GPU) from expensive tests
- All harness functions take `(spec: dict, project_root: Path)` — consistent, no global state
- `EXCLUDED_SPECS` is `frozenset[str]` in all 4 current copies — keep this type in `harness/constants.py`

### Integration Points
- `harness/__init__.py` will need to export `EXCLUDED_SPECS` from the new `constants.py` (or callers import `from harness.constants import EXCLUDED_SPECS` directly)
- `analyze_harness_batch.py` will read from `results/harness/{suite}/` — this directory does not exist yet; script should create it on first run
- `tests/test_campaign_classification.py` imports `from scripts.evaluation.campaign_utils import campaign_for` (Phase 2 path) — the skip decorator prevents failures until Phase 2 implements it

</code_context>

<specifics>
## Specific Ideas

- Use the same 5 spec filenames already in `tests/test_spec_loader_integration.py` (line ~36-39) so there is one canonical list of "sample specs" across both test files
- `harness/constants.py` should include a comment pointing to `known-issues.md` for the WHY behind each excluded spec
- The markdown matrix from `analyze_harness_batch.py` should match the existing `results_matrix_rodinia.md` format exactly (kernel rows, API columns) so comparison is easy

</specifics>

<deferred>
## Deferred Ideas

- Full portability (compiler path templating via `config/paths.json`) — deferred post-NeurIPS per PROJECT.md
- Migrating existing `results/rodinia/logs/` to `results/harness/rodinia/` — not worth the risk; old data stays in place
- Campaign edge case tests (temp=0.0 + sample_id present; temp=0.7 + no sample_id) — user chose minimal test set; Phase 2 can extend

</deferred>

---

*Phase: 01-pipeline-testing-uniformity*
*Context gathered: 2026-04-10*
