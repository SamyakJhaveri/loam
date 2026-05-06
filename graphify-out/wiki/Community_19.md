# Community 19

> 36 nodes

## Key Concepts

- **derive_passers()** (15 connections) — `scripts/evaluation/derive_l0_passers.py`
- **test_derive_l0_passers.py** (15 connections) — `tests/test_derive_l0_passers.py`
- **_write_result()** (13 connections) — `tests/test_derive_l0_passers.py`
- **derive_l0_passers.py** (4 connections) — `scripts/evaluation/derive_l0_passers.py`
- **test_three_of_three_pass_included()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_one_of_three_pass_included()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_zero_of_three_pass_excluded()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_two_samples_one_pass_included_with_warning()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_zero_samples_vacuous()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_model_filter_excludes_other_models()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_augment_level_filter_excludes_non_L0()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_unparseable_json_is_skipped()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_main_writes_default_out_path()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_direction_filter_keeps_matching_entries()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_direction_filter_drops_non_matching_entries()** (4 connections) — `tests/test_derive_l0_passers.py`
- **test_direction_none_preserves_legacy_behavior()** (4 connections) — `tests/test_derive_l0_passers.py`
- **_load_result()** (3 connections) — `scripts/evaluation/derive_l0_passers.py`
- **test_missing_canonical_dir_returns_1()** (3 connections) — `tests/test_derive_l0_passers.py`
- **main()** (2 connections) — `scripts/evaluation/derive_l0_passers.py`
- **Derive L0 passer-set for a given model from a canonical eval directory.  Phase 2** (1 connections) — `scripts/evaluation/derive_l0_passers.py`
- **Load a result JSON, mirroring analyze_eval.py:_load_complexity_lookup's     try/** (1 connections) — `scripts/evaluation/derive_l0_passers.py`
- **Return sorted passer list. Pure function — no filesystem writes.      Per D-18:** (1 connections) — `scripts/evaluation/derive_l0_passers.py`
- **Phase 2 / Plan 02-05 tests: derive_l0_passers filter semantics (D-22).** (1 connections) — `tests/test_derive_l0_passers.py`
- **D-22 case 1: 3/3 PASS -> included, no warning.** (1 connections) — `tests/test_derive_l0_passers.py`
- **D-22 case 2: 1/3 PASS -> included, no warning.** (1 connections) — `tests/test_derive_l0_passers.py`
- *... and 11 more nodes in this community*

## Relationships

- [[Community 0]] (2 shared connections)

## Source Files

- `scripts/evaluation/derive_l0_passers.py`
- `tests/test_derive_l0_passers.py`

## Audit Trail

- EXTRACTED: 96 (80%)
- INFERRED: 24 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*