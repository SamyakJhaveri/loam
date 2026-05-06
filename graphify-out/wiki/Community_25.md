# Community 25

> 25 nodes

## Key Concepts

- **verify_run()** (31 connections) — `harness/verifier.py`
- **test_verifier_numeric_comparison.py** (12 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_verifier_file_hash.py** (12 connections) — `tests/test_verifier_file_hash.py`
- **_make_run()** (11 connections) — `tests/test_verifier_numeric_comparison.py`
- **_make_run()** (10 connections) — `tests/test_verifier_file_hash.py`
- **_spec_with_file_hash()** (9 connections) — `tests/test_verifier_file_hash.py`
- **_spec_with_numeric()** (8 connections) — `tests/test_verifier_numeric_comparison.py`
- **_sha256_of()** (7 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_correct_sha_passes()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_wrong_sha_fails()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_absolute_path_fails()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_parent_traversal_fails()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_symlink_outside_fails()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_uppercase_sha_passes()** (5 connections) — `tests/test_verifier_file_hash.py`
- **test_numeric_match_within_tolerance_passes()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_outside_tolerance_fails()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_missing_extract_regex_fails()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_no_regex_match_fails()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_unparseable_capture_fails()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_zero_tolerance_exact_match_passes()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_invalid_regex_errors()** (4 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_file_hash_missing_file_fails()** (4 connections) — `tests/test_verifier_file_hash.py`
- **test_file_hash_none_working_dir_errors()** (4 connections) — `tests/test_verifier_file_hash.py`
- **test_numeric_tolerance_null_errors()** (3 connections) — `tests/test_verifier_numeric_comparison.py`
- **test_numeric_expected_non_numeric_errors()** (3 connections) — `tests/test_verifier_numeric_comparison.py`

## Relationships

- [[Community 0]] (18 shared connections)

## Source Files

- `harness/verifier.py`
- `tests/test_verifier_file_hash.py`
- `tests/test_verifier_numeric_comparison.py`

## Audit Trail

- EXTRACTED: 129 (75%)
- INFERRED: 43 (25%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*