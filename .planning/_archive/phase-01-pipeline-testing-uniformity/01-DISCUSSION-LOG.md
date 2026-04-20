# Phase 1: Pipeline Testing & Uniformity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 01-pipeline-testing-uniformity
**Areas discussed:** Build/run/verify tests, EXCLUDED_SPECS home, analyze_rodinia_batch.py fate, Campaign tests scope

---

## Build/Run/Verify Tests

| Option | Description | Selected |
|--------|-------------|----------|
| Sample — 1 spec per suite | 1 representative spec per suite, fast (~1-2 min), @pytest.mark.integration | ✓ |
| Full — all non-KNOWN_FAIL specs | All ~87 specs, slow (~15-30 min), impractical for routine runs | |
| Separate script, not pytest | Shell/Python batch script, results logged to file | |

**User's choice:** Sample (1 spec per suite)

| Option | Description | Selected |
|--------|-------------|----------|
| tests/test_harness_integration.py | New file, consistent with existing test structure | ✓ |
| tests/test_spec_loader_integration.py | Extend existing file | |
| You decide | Claude picks | |

**User's choice:** New file `tests/test_harness_integration.py`

| Option | Description | Selected |
|--------|-------------|----------|
| Full pipeline: build → run → verify | Complete harness pipeline, matches REQUIREMENTS | ✓ |
| Build only | Faster but misses run/verify correctness | |

**User's choice:** Full pipeline (build → run → verify)

| Option | Description | Selected |
|--------|-------------|----------|
| Skip via pytest.mark.skip using EXCLUDED_SPECS | Self-documenting, correct test count | ✓ |
| Exclude from parametrization | Simpler but less visible | |
| You decide | Claude picks | |

**User's choice:** Skip via `pytest.mark.skip` using EXCLUDED_SPECS constant

| Option | Description | Selected |
|--------|-------------|----------|
| Same specs as spec_loader_integration.py | Reuse rodinia-bfs-cuda, xsbench-xsbench-cuda, rsbench-rsbench-cuda, mixbench-mixbench-cuda, hecbench-bezier-surface-cuda | ✓ |
| Pick a different set | Optimize for build speed or coverage | |

**User's choice:** Same 5 specs as existing integration tests

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-detect from conftest.py | Uses existing PROJECT_ROOT constant | ✓ |
| Explicit env var or fixture | More explicit, requires setup | |

**User's choice:** Auto-detect from conftest.py

---

## EXCLUDED_SPECS Home

| Option | Description | Selected |
|--------|-------------|----------|
| harness/constants.py | New file in harness package; all 4 importers converge on one trusted package | ✓ |
| harness/models.py | Add to existing models file; no new file but mixes domain concepts | |
| scripts/constants.py | Top-level scripts module; harness would need its own copy | |

**User's choice:** `harness/constants.py` (new file)

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — code is authoritative | known-issues.md explains WHY; harness/constants.py enforces | ✓ |
| No — keep independent | Allow divergence | |

**User's choice:** harness/constants.py is the single source of truth; known-issues.md is documentation

---

## analyze_rodinia_batch.py Fate

| Option | Description | Selected |
|--------|-------------|----------|
| Replace with suite-agnostic version | New analyze_harness_batch.py with --suite flag; delete old file | ✓ |
| Generalize in-place | Refactor existing file; rename | |
| Keep + add parallel per-suite files | One file per suite; more duplication | |

**User's choice:** Replace entirely with `scripts/analysis/analyze_harness_batch.py`

| Option | Description | Selected |
|--------|-------------|----------|
| results/harness/{suite}/ | New top-level namespace, separates harness from eval results | ✓ |
| results/{suite}/logs/ | Suite-namespaced, consistent with existing Rodinia pattern | |

**User's choice:** `results/harness/{suite}/` (new namespace)

| Option | Description | Selected |
|--------|-------------|----------|
| Leave old results/rodinia/logs/ alone | Historical data stays; new runs use new path | ✓ |
| Migrate to results/harness/rodinia/ | Consistency but risk of breaking scripts | |
| Support both with fallback | Complex, not worth it | |

**User's choice:** Leave old Rodinia results in place; no migration

| Option | Description | Selected |
|--------|-------------|----------|
| JSON summary | results/harness/{suite}/{suite}_results.json | ✓ |
| Markdown matrix | results/harness/{suite}/results_matrix_{suite}.md | ✓ |
| Console summary | Print to stdout only | |

**User's choice:** Both JSON summary and markdown matrix

| Option | Description | Selected |
|--------|-------------|----------|
| No — those are analysis scripts, not pipeline | Keep intentional Rodinia-specific sections | |
| Yes — clean them too | Per-suite counters / --suite filter | ✓ |

**User's choice:** Clean up analysis scripts too (per-suite counters, --suite filter)

| Option | Description | Selected |
|--------|-------------|----------|
| Per-suite counters / --suite filter | quantitative_findings.py: per-suite dict; classify_translation_pairs.py: --suite flag | ✓ |
| Remove the Rodinia-specific sections | Delete spot-checks; simpler but loses analysis breadth | |
| You decide | Claude picks | |

**User's choice:** Generalize to per-suite (not delete)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete immediately | No dead code; new script handles all suites | ✓ |
| Keep as thin wrapper | Calls new script with --suite rodinia | |
| Keep deprecated but unused | Leave with deprecation notice | |

**User's choice:** Delete `analyze_rodinia_batch.py` immediately

---

## Campaign Tests Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Write TDD tests now, skip until Phase 2 | tests/test_campaign_classification.py with @pytest.mark.skip; Phase 2 removes skip | ✓ |
| Defer entirely to Phase 2 | Phase 2 writes both implementation and tests | |
| Test existing logic only | Test temperature + sample_id fields in existing JSONs | |

**User's choice:** TDD tests now with skip marker

| Option | Description | Selected |
|--------|-------------|----------|
| campaign_for(record: dict) -> str | Takes full dict, reads temperature + sample_id | ✓ |
| campaign_for(temperature, sample_id) -> str | Explicit fields; easier to unit test but requires unpacking | |

**User's choice:** `campaign_for(record: dict) -> str`

| Option | Description | Selected |
|--------|-------------|----------|
| scripts/evaluation/campaign_utils.py | New module in evaluation package; co-located with run_eval_batch.py | ✓ |
| harness/constants.py | Alongside EXCLUDED_SPECS | |
| You decide | Claude picks | |

**User's choice:** `scripts/evaluation/campaign_utils.py` (Phase 2 creates)

| Option | Description | Selected |
|--------|-------------|----------|
| temperature != 0.0 OR sample_id is not None | Either signal → C2. Matches actual Qwen C2 data | ✓ |
| Only temperature check | Simpler but misses sample_id-only cases | |
| Only sample_id check | Handles pass@k regardless of temp | |

**User's choice:** `temperature != 0.0 OR sample_id is not None`

**Test cases selected:**
- `{temperature: 0.0, sample_id: None}` → `'c1'` ✓
- `{temperature: 0.7, sample_id: 's1'}` → `'c2'` ✓

**Notes:** Edge cases (temp=0.0 + sample_id present; temp=0.7 + no sample_id) deferred — user chose minimal test set.

---

## Claude's Discretion

- Test fixture structure in `test_harness_integration.py` (parameterization approach)
- Whether `analyze_harness_batch.py` uses argparse or click
- Internal structure of per-suite dict in `quantitative_findings.py`
- Exact contents of `harness/constants.py` beyond EXCLUDED_SPECS

## Deferred Ideas

- Portability (compiler path templating) — deferred post-NeurIPS
- Migration of old `results/rodinia/logs/` data
- Campaign edge case tests (Phase 2 can extend the test set)
