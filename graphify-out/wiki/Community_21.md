# Community 21

> 32 nodes

## Key Concepts

- **test_cross_model_comparison.py** (12 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **build_comparison()** (10 connections) — `scripts/analysis/cross_model_comparison.py`
- **_make_test_data()** (6 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **_make_test_data_full_directions()** (5 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **cross_model_comparison.py** (4 connections) — `scripts/analysis/cross_model_comparison.py`
- **classify_effect_size()** (4 connections) — `scripts/analysis/cross_model_comparison.py`
- **test_output_json_has_required_keys()** (4 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_per_kernel_matrix_four_keys()** (4 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_common_directions_count()** (4 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_missing_directions()** (4 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_kernel_matrix_counts_sum()** (4 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **cohens_h()** (3 connections) — `scripts/analysis/cross_model_comparison.py`
- **test_cohens_h_identical_proportions()** (3 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_cohens_h_maximum_effect()** (3 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_cohens_h_reversed()** (3 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **test_classify_effect_size()** (3 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **_make_dir_data()** (3 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **main()** (2 connections) — `scripts/analysis/cross_model_comparison.py`
- **Cohen's h effect size for two proportions.      Clamp inputs to [0, 1] to handle** (1 connections) — `scripts/analysis/cross_model_comparison.py`
- **Classify |h| per Cohen's conventions.      |h| < 0.2: negligible     0.2 <= |h|** (1 connections) — `scripts/analysis/cross_model_comparison.py`
- **Build the full cross-model comparison dict.      Args:         qwen_data: Parsed** (1 connections) — `scripts/analysis/cross_model_comparison.py`
- **Test 1: cohens_h(0.5, 0.5) == 0.0 (identical proportions).** (1 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **Test 2: cohens_h(1.0, 0.0) > 0 (maximum positive effect).** (1 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **Test 3: cohens_h(0.0, 1.0) < 0 (reversed).** (1 connections) — `scripts/analysis/test_cross_model_comparison.py`
- **Test 4: classify_effect_size thresholds.** (1 connections) — `scripts/analysis/test_cross_model_comparison.py`
- *... and 7 more nodes in this community*

## Relationships

- [[Community 2]] (3 shared connections)

## Source Files

- `scripts/analysis/cross_model_comparison.py`
- `scripts/analysis/test_cross_model_comparison.py`

## Audit Trail

- EXTRACTED: 80 (84%)
- INFERRED: 15 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*