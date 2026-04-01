"""
Tests for token_analysis.py — EXCLUDED_SPECS filtering.

Verifies that load_all_results() correctly filters out results
involving specs listed in EXCLUDED_SPECS.
"""

import json
import tempfile
from pathlib import Path

import pytest

from token_analysis import EXCLUDED_SPECS, load_all_results


def _make_result(source_spec: str, target_spec: str, status: str = "PASS",
                 model: str = "test-model") -> dict:
    """Create a minimal result JSON matching the fields load_all_results checks."""
    return {
        "overall_status": status,
        "source_spec": source_spec,
        "target_spec": target_spec,
        "model": model,
        "kernel": source_spec.rsplit("-", 1)[0],
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "llm_response_time_seconds": 2.5,
        "augment_level": 0,
    }


def _write_results(tmpdir: Path, model: str, results: list[dict]) -> None:
    """Write result JSONs into tmpdir/results/evaluation/{model}/."""
    model_dir = tmpdir / "results" / "evaluation" / model
    model_dir.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(results):
        (model_dir / f"result_{i}.json").write_text(
            json.dumps(r), encoding="utf-8"
        )


class TestExcludedSpecsDefinition:
    """Verify EXCLUDED_SPECS is correctly defined in token_analysis.py."""

    def test_excluded_specs_is_frozenset(self):
        assert isinstance(EXCLUDED_SPECS, frozenset)

    def test_excluded_specs_has_six_entries(self):
        assert len(EXCLUDED_SPECS) == 6

    def test_excluded_specs_matches_canonical(self):
        """Must match the canonical list from analyze_eval.py."""
        expected = frozenset({
            "rodinia-kmeans-cuda",
            "rodinia-mummergpu-cuda",
            "rodinia-mummergpu-omp",
            "rodinia-hybridsort-cuda",
            "rodinia-nn-opencl",
            "rodinia-kmeans-opencl",
        })
        assert EXCLUDED_SPECS == expected


class TestLoadAllResultsFiltering:
    """Verify load_all_results() filters out excluded specs."""

    def test_excludes_source_spec(self):
        """Results where source_spec is in EXCLUDED_SPECS should be filtered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            results = [
                _make_result("rodinia-bfs-cuda", "rodinia-bfs-omp"),
                _make_result("rodinia-kmeans-cuda", "rodinia-kmeans-omp"),  # excluded source
                _make_result("rodinia-nw-cuda", "rodinia-nw-omp"),
            ]
            _write_results(tmpdir, "test-model", results)
            loaded = load_all_results(tmpdir)
            assert len(loaded) == 2
            specs = {r["source_spec"] for r in loaded}
            assert "rodinia-kmeans-cuda" not in specs

    def test_excludes_target_spec(self):
        """Results where target_spec is in EXCLUDED_SPECS should be filtered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            results = [
                _make_result("rodinia-bfs-cuda", "rodinia-bfs-omp"),
                _make_result("rodinia-bfs-omp", "rodinia-nn-opencl"),  # excluded target
                _make_result("rodinia-nw-cuda", "rodinia-nw-omp"),
            ]
            _write_results(tmpdir, "test-model", results)
            loaded = load_all_results(tmpdir)
            assert len(loaded) == 2
            targets = {r["target_spec"] for r in loaded}
            assert "rodinia-nn-opencl" not in targets

    def test_keeps_non_excluded_specs(self):
        """Results for non-excluded specs should all be kept."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            results = [
                _make_result("rodinia-bfs-cuda", "rodinia-bfs-omp"),
                _make_result("rodinia-nw-cuda", "rodinia-nw-omp"),
                _make_result("rodinia-hotspot-cuda", "rodinia-hotspot-omp"),
            ]
            _write_results(tmpdir, "test-model", results)
            loaded = load_all_results(tmpdir)
            assert len(loaded) == 3

    def test_filters_all_excluded_specs(self):
        """Every spec in EXCLUDED_SPECS should be filtered when it appears as source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            # One valid result + one per excluded spec
            results = [_make_result("rodinia-bfs-cuda", "rodinia-bfs-omp")]
            for excluded in sorted(EXCLUDED_SPECS):
                results.append(_make_result(excluded, "rodinia-bfs-omp"))
            _write_results(tmpdir, "test-model", results)
            loaded = load_all_results(tmpdir)
            assert len(loaded) == 1
            assert loaded[0]["source_spec"] == "rodinia-bfs-cuda"

    def test_empty_directory(self):
        """No results directory should return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "results" / "evaluation").mkdir(parents=True)
            loaded = load_all_results(tmpdir)
            assert loaded == []


class TestPassRateUsesFilteredTotal:
    """Verify that pass_rate denominator uses filtered (not raw) count."""

    def test_pass_rate_excludes_excluded_specs(self):
        """Pass rate should be computed over filtered results only.

        Setup: 3 results total, 1 excluded.
        - 2 non-excluded: 1 PASS + 1 BUILD_FAIL
        - 1 excluded: PASS (should not count)

        Expected pass_rate = 1/2 = 0.5, NOT 2/3 = 0.6667
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            results = [
                _make_result("rodinia-bfs-cuda", "rodinia-bfs-omp", "PASS"),
                _make_result("rodinia-nw-cuda", "rodinia-nw-omp", "BUILD_FAIL"),
                _make_result("rodinia-kmeans-cuda", "rodinia-kmeans-omp", "PASS"),  # excluded
            ]
            _write_results(tmpdir, "test-model", results)
            loaded = load_all_results(tmpdir)
            # Only 2 results should remain
            assert len(loaded) == 2
            pass_count = sum(1 for r in loaded if r["overall_status"] == "PASS")
            pass_rate = pass_count / len(loaded)
            assert pass_rate == pytest.approx(0.5)
