#!/usr/bin/env python3
"""Tests for cross_model_comparison.py.

TDD RED phase: these tests define the expected behavior before implementation.
"""

import json
import math
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Will be importable after GREEN phase
sys.path.insert(0, str(Path(__file__).parent))


def test_cohens_h_identical_proportions():
    """Test 1: cohens_h(0.5, 0.5) == 0.0 (identical proportions)."""
    from cross_model_comparison import cohens_h
    assert cohens_h(0.5, 0.5) == 0.0


def test_cohens_h_maximum_effect():
    """Test 2: cohens_h(1.0, 0.0) > 0 (maximum positive effect)."""
    from cross_model_comparison import cohens_h
    assert cohens_h(1.0, 0.0) > 0


def test_cohens_h_reversed():
    """Test 3: cohens_h(0.0, 1.0) < 0 (reversed)."""
    from cross_model_comparison import cohens_h
    assert cohens_h(0.0, 1.0) < 0


def test_classify_effect_size():
    """Test 4: classify_effect_size thresholds."""
    from cross_model_comparison import classify_effect_size
    assert classify_effect_size(0.1) == "negligible"
    assert classify_effect_size(0.3) == "small"
    assert classify_effect_size(0.5) == "medium"
    assert classify_effect_size(0.9) == "large"


def test_output_json_has_required_keys():
    """Test 5: Output JSON has required keys."""
    from cross_model_comparison import build_comparison

    qwen_data, gpt_data = _make_test_data()
    result = build_comparison(qwen_data, gpt_data)

    assert "overall" in result
    assert "chi_squared" in result["overall"]
    assert "p_value" in result["overall"]["chi_squared"]
    assert "cohens_h" in result["overall"]
    assert "per_direction" in result
    assert "per_kernel_matrix" in result


def test_per_kernel_matrix_four_keys():
    """Test 6: per_kernel_matrix has exactly 4 classification keys."""
    from cross_model_comparison import build_comparison

    qwen_data, gpt_data = _make_test_data()
    result = build_comparison(qwen_data, gpt_data)

    km = result["per_kernel_matrix"]
    for key in ["both_pass", "both_fail", "qwen_only_pass", "gpt_only_pass"]:
        assert key in km, f"Missing key: {key}"


def test_common_directions_count():
    """Test 7: common_directions has exactly 7 entries (GPT missing omp_target-to-cuda)."""
    from cross_model_comparison import build_comparison

    qwen_data, gpt_data = _make_test_data_full_directions()
    result = build_comparison(qwen_data, gpt_data)

    assert len(result["common_directions"]) == 7


def test_missing_directions():
    """Test 8: missing_directions contains omp_target-to-cuda for GPT."""
    from cross_model_comparison import build_comparison

    qwen_data, gpt_data = _make_test_data_full_directions()
    result = build_comparison(qwen_data, gpt_data)

    assert "azure-gpt-5.3-chat" in result["missing_directions"]
    assert "omp_target-to-cuda" in result["missing_directions"]["azure-gpt-5.3-chat"]


def test_kernel_matrix_counts_sum():
    """per_kernel_matrix counts sum to total_common_kernels."""
    from cross_model_comparison import build_comparison

    qwen_data, gpt_data = _make_test_data()
    result = build_comparison(qwen_data, gpt_data)

    km = result["per_kernel_matrix"]
    total = (km["counts"]["both_pass"] + km["counts"]["both_fail"]
             + km["counts"]["qwen_only_pass"] + km["counts"]["gpt_only_pass"])
    assert total == km["total_common_kernels"]


# --- Helpers ---

def _make_dir_data(total, passed):
    return {
        "total": total,
        "pass": passed,
        "pass_rate": passed / total if total > 0 else 0.0,
        "ci_lower": 0.0,
        "ci_upper": 1.0,
        "by_status": {"PASS": passed, "BUILD_FAIL": total - passed},
    }


def _make_test_data():
    """Create minimal test data with 2 common directions and 3 kernels."""
    qwen = {
        "model": "together-qwen-3.5-397b-a17b",
        "primary_campaign": {
            "total": 100,
            "overall": {
                "total": 100, "pass": 40, "pass_rate": 0.4,
                "ci_lower": 0.3, "ci_upper": 0.5,
                "by_status": {"PASS": 40, "BUILD_FAIL": 60},
            },
            "by_direction": {
                "cuda-to-omp": _make_dir_data(50, 25),
                "omp-to-cuda": _make_dir_data(50, 15),
            },
            "by_kernel": {
                "backprop": _make_dir_data(10, 5),    # passes (pass > 0)
                "bfs": _make_dir_data(10, 0),          # fails
                "cfd": _make_dir_data(10, 3),           # passes
            },
        },
    }
    gpt = {
        "model": "azure-gpt-5.3-chat",
        "primary_campaign": {
            "total": 80,
            "overall": {
                "total": 80, "pass": 20, "pass_rate": 0.25,
                "ci_lower": 0.15, "ci_upper": 0.35,
                "by_status": {"PASS": 20, "BUILD_FAIL": 60},
            },
            "by_direction": {
                "cuda-to-omp": _make_dir_data(40, 15),
                "omp-to-cuda": _make_dir_data(40, 5),
            },
            "by_kernel": {
                "backprop": _make_dir_data(8, 4),     # passes
                "bfs": _make_dir_data(8, 2),           # passes (gpt_only_pass)
                "cfd": _make_dir_data(8, 0),           # fails (qwen_only_pass)
            },
        },
    }
    return qwen, gpt


def _make_test_data_full_directions():
    """Create test data with 8 Qwen directions and 7 GPT directions."""
    common_dirs = [
        "cuda-to-omp", "omp-to-cuda",
        "cuda-to-opencl", "opencl-to-cuda",
        "omp-to-opencl", "opencl-to-omp",
        "cuda-to-omp_target",
    ]
    qwen_dirs = {d: _make_dir_data(20, 8) for d in common_dirs}
    qwen_dirs["omp_target-to-cuda"] = _make_dir_data(20, 5)  # Qwen-only

    gpt_dirs = {d: _make_dir_data(15, 4) for d in common_dirs}

    qwen = {
        "model": "together-qwen-3.5-397b-a17b",
        "primary_campaign": {
            "total": 180,
            "overall": {
                "total": 180, "pass": 69, "pass_rate": 69 / 180,
                "ci_lower": 0.3, "ci_upper": 0.5,
                "by_status": {"PASS": 69, "BUILD_FAIL": 111},
            },
            "by_direction": qwen_dirs,
            "by_kernel": {
                "backprop": _make_dir_data(10, 5),
            },
        },
    }
    gpt = {
        "model": "azure-gpt-5.3-chat",
        "primary_campaign": {
            "total": 105,
            "overall": {
                "total": 105, "pass": 28, "pass_rate": 28 / 105,
                "ci_lower": 0.15, "ci_upper": 0.35,
                "by_status": {"PASS": 28, "BUILD_FAIL": 77},
            },
            "by_direction": gpt_dirs,
            "by_kernel": {
                "backprop": _make_dir_data(8, 4),
            },
        },
    }
    return qwen, gpt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
