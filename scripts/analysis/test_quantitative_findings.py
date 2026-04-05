#!/usr/bin/env python3
"""Tests for quantitative_findings.py — TDD RED phase.

Covers:
  Test 1: KNOWN_FAIL exclusion removes all 8 specs (6 Rodinia + 2 HeCBench)
  Test 2: Campaign split produces C1 (temp=0.0) and C2 (temp=0.7) with no overlap
  Test 3: Wilson CI returns dict with value, ci_lower, ci_upper, ci_level=0.95, n fields
  Test 4: Provenance wrapper includes value, source, files_matched, derivation fields
  Test 5: Suite extraction from source_spec correctly parses all 5 suites
  Test 6: Direction extraction handles omp_target correctly (not merged with omp)
  Test 7: Augment level extraction: no suffix->0, -L1->1, -L4->4, -s0->0 (seed, not level)
  Test 8: Error taxonomy classifies BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL
  Test 9: McNemar test pairs on (suite, kernel) for forward/reverse directions
  Test 10: Cochran-Armitage computed per-direction AND aggregate
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the analysis scripts directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import quantitative_findings as qf  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — synthetic result records
# ---------------------------------------------------------------------------

def _make_record(
    source_spec: str = "rodinia-bfs-cuda",
    target_spec: str = "rodinia-bfs-omp",
    overall_status: str = "PASS",
    temperature: float = 0.0,
    augment_level: int = 0,
    sample_id: int | None = None,
    direction: str | None = None,
    build_error_snippet: str | None = None,
    run_exit_code: int | None = None,
    run_stderr_snippet: str | None = None,
    run_stdout_snippet: str | None = None,
    error_message: str | None = None,
    verify_status: str | None = None,
    attempts: list | None = None,
) -> dict:
    """Create a synthetic result record for testing."""
    stem_parts = f"{source_spec}-to-{target_spec}"
    if augment_level > 0:
        stem_parts += f"-L{augment_level}"
    if sample_id is not None:
        stem_parts += f"-s{sample_id}"

    rec = {
        "source_spec": source_spec,
        "target_spec": target_spec,
        "overall_status": overall_status,
        "temperature": temperature,
        "augment_level": augment_level,
        "sample_id": sample_id,
        "build_error_snippet": build_error_snippet,
        "run_exit_code": run_exit_code,
        "run_stderr_snippet": run_stderr_snippet,
        "run_stdout_snippet": run_stdout_snippet,
        "error_message": error_message,
        "verify_status": verify_status,
        "attempts": attempts or [],
        "_filename": f"{stem_parts}.json",
        "_stem": stem_parts,
    }
    if direction is None:
        rec["direction"] = qf._direction_from_data(rec)
    else:
        rec["direction"] = direction
    rec["kernel"] = qf._kernel_from_spec(source_spec)
    rec["_suite"] = qf._suite_from_spec(source_spec)
    return rec


# ---------------------------------------------------------------------------
# Test 1: KNOWN_FAIL exclusion removes all 8 specs
# ---------------------------------------------------------------------------

def test_known_fail_exclusion():
    """All 8 KNOWN_FAIL specs (6 Rodinia + 2 HeCBench) are excluded."""
    records = [
        _make_record(source_spec="rodinia-bfs-cuda", target_spec="rodinia-bfs-omp"),
        _make_record(source_spec="rodinia-kmeans-cuda", target_spec="rodinia-kmeans-omp"),
        _make_record(source_spec="rodinia-mummergpu-cuda", target_spec="rodinia-mummergpu-omp"),
        _make_record(source_spec="rodinia-mummergpu-omp", target_spec="rodinia-mummergpu-cuda"),
        _make_record(source_spec="rodinia-hybridsort-cuda", target_spec="rodinia-hybridsort-omp"),
        _make_record(source_spec="rodinia-nn-opencl", target_spec="rodinia-nn-cuda"),
        _make_record(source_spec="rodinia-kmeans-opencl", target_spec="rodinia-kmeans-cuda"),
        _make_record(source_spec="hecbench-stencil1d-omp_target", target_spec="hecbench-stencil1d-cuda"),
        _make_record(source_spec="hecbench-scan-omp_target", target_spec="hecbench-scan-cuda"),
        _make_record(source_spec="rodinia-hotspot-cuda", target_spec="rodinia-hotspot-omp"),
    ]
    filtered = qf.exclude_known_fail(records)
    # Only 2 records survive: bfs and hotspot
    assert len(filtered) == 2
    specs_remaining = {r["source_spec"] for r in filtered}
    assert "rodinia-bfs-cuda" in specs_remaining
    assert "rodinia-hotspot-cuda" in specs_remaining

    # Verify the constant has exactly 8 entries
    assert len(qf.EXCLUDED_SPECS) == 8
    assert "hecbench-stencil1d-omp_target" in qf.EXCLUDED_SPECS
    assert "hecbench-scan-omp_target" in qf.EXCLUDED_SPECS


# ---------------------------------------------------------------------------
# Test 2: Campaign split produces C1/C2 with no overlap
# ---------------------------------------------------------------------------

def test_campaign_split():
    """Campaign split: C1=temp 0.0, C2=temp 0.7, no overlap."""
    records = [
        _make_record(temperature=0.0),
        _make_record(temperature=0.0),
        _make_record(temperature=0.7),
    ]
    c1, c2 = qf.split_campaigns(records)
    assert len(c1) == 2
    assert len(c2) == 1
    assert all(r["temperature"] == 0.0 for r in c1)
    assert all(r["temperature"] > 0.0 for r in c2)


# ---------------------------------------------------------------------------
# Test 3: Wilson CI returns dict with required fields
# ---------------------------------------------------------------------------

def test_wilson_ci_fields():
    """Wilson CI dict has value, ci_lower, ci_upper, ci_level, n."""
    result = qf.wilson_ci(7, 10)
    assert "value" in result
    assert "ci_lower" in result
    assert "ci_upper" in result
    assert "ci_level" in result
    assert "n" in result
    assert result["ci_level"] == 0.95
    assert result["n"] == 10
    assert 0 <= result["ci_lower"] <= result["value"] <= result["ci_upper"] <= 1.0


def test_wilson_ci_zero():
    """Wilson CI with zero total returns zeros."""
    result = qf.wilson_ci(0, 0)
    assert result["value"] == 0.0
    assert result["n"] == 0


# ---------------------------------------------------------------------------
# Test 4: Provenance wrapper
# ---------------------------------------------------------------------------

def test_make_finding_fields():
    """Provenance wrapper returns dict with required fields."""
    finding = qf.make_finding(
        value=0.362,
        source="paper_data.json",
        files_matched=710,
        derivation="PASS count / total primary campaign records",
    )
    assert finding["value"] == 0.362
    assert finding["source"] == "paper_data.json"
    assert finding["files_matched"] == 710
    assert finding["derivation"] == "PASS count / total primary campaign records"


def test_make_finding_with_ci():
    """Provenance wrapper with CI fields."""
    finding = qf.make_finding(
        value=0.362,
        source="computed",
        files_matched=710,
        derivation="wilson_ci(passes, total)",
        ci_lower=0.32,
        ci_upper=0.41,
        n=710,
    )
    assert finding["ci_lower"] == 0.32
    assert finding["ci_upper"] == 0.41
    assert finding["ci_level"] == 0.95
    assert finding["n"] == 710


# ---------------------------------------------------------------------------
# Test 5: Suite extraction
# ---------------------------------------------------------------------------

def test_suite_from_spec():
    """Suite extraction parses all 5 suites correctly."""
    assert qf._suite_from_spec("rodinia-bfs-cuda") == "rodinia"
    assert qf._suite_from_spec("hecbench-stencil1d-cuda") == "hecbench"
    assert qf._suite_from_spec("xsbench-xsbench-omp") == "xsbench"
    assert qf._suite_from_spec("rsbench-rsbench-cuda") == "rsbench"
    assert qf._suite_from_spec("mixbench-mixbench-cuda") == "mixbench"


# ---------------------------------------------------------------------------
# Test 6: Direction extraction with omp_target
# ---------------------------------------------------------------------------

def test_direction_from_data_omp_target():
    """omp_target directions are distinct from omp."""
    rec = {"source_spec": "rodinia-bfs-cuda", "target_spec": "hecbench-stencil1d-omp_target"}
    direction = qf._direction_from_data(rec)
    assert direction == "cuda-to-omp_target"
    assert "omp_target" in direction
    assert direction != "cuda-to-omp"


def test_direction_from_data_standard():
    """Standard directions parse correctly."""
    rec = {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp"}
    assert qf._direction_from_data(rec) == "cuda-to-omp"


# ---------------------------------------------------------------------------
# Test 7: Augment level extraction
# ---------------------------------------------------------------------------

def test_augment_level_from_filename():
    """Augment level parsing from filename stems."""
    assert qf._augment_level_from_filename("rodinia-bfs-cuda-to-rodinia-bfs-omp") == 0
    assert qf._augment_level_from_filename("rodinia-bfs-cuda-to-rodinia-bfs-omp-L1") == 1
    assert qf._augment_level_from_filename("rodinia-bfs-cuda-to-rodinia-bfs-omp-L4") == 4
    assert qf._augment_level_from_filename("rodinia-bfs-cuda-to-rodinia-bfs-omp-L2-s0") == 2
    # -s0 alone means sample_id, NOT augment level
    assert qf._augment_level_from_filename("rodinia-bfs-cuda-to-rodinia-bfs-omp-s0") == 0


# ---------------------------------------------------------------------------
# Test 8: Error taxonomy classification
# ---------------------------------------------------------------------------

def test_failure_taxonomy_classification():
    """Failure taxonomy counts BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL."""
    records = [
        _make_record(overall_status="PASS"),
        _make_record(overall_status="BUILD_FAIL", build_error_snippet="undefined reference to foo"),
        _make_record(overall_status="BUILD_FAIL", build_error_snippet="cudaMalloc not found"),
        _make_record(overall_status="RUN_FAIL", run_exit_code=-11),
        _make_record(overall_status="VERIFY_FAIL", verify_status="fail"),
        _make_record(overall_status="EXTRACTION_FAIL", error_message="did not contain parseable code"),
    ]
    result = qf.compute_failure_taxonomy(records)
    assert result["total_failures"] == 5
    assert result["by_status"]["BUILD_FAIL"]["count"] == 2
    assert result["by_status"]["RUN_FAIL"]["count"] == 1
    assert result["by_status"]["VERIFY_FAIL"]["count"] == 1
    assert result["by_status"]["EXTRACTION_FAIL"]["count"] == 1
    # Subcategories for BUILD_FAIL
    assert "subcategories" in result["by_status"]["BUILD_FAIL"]


# ---------------------------------------------------------------------------
# Test 9: McNemar pairs on (suite, kernel) for forward/reverse
# ---------------------------------------------------------------------------

def test_direction_asymmetry_pairs_on_suite_kernel():
    """McNemar pairs on (suite, kernel) to avoid cross-suite false pairs."""
    # Same kernel name "bfs" in two suites — they should NOT be paired
    records = [
        _make_record(source_spec="rodinia-bfs-cuda", target_spec="rodinia-bfs-omp",
                     overall_status="PASS", augment_level=0),
        _make_record(source_spec="rodinia-bfs-omp", target_spec="rodinia-bfs-cuda",
                     overall_status="FAIL", augment_level=0),
        _make_record(source_spec="hecbench-bfs-cuda", target_spec="hecbench-bfs-omp",
                     overall_status="FAIL", augment_level=0),
        _make_record(source_spec="hecbench-bfs-omp", target_spec="hecbench-bfs-cuda",
                     overall_status="PASS", augment_level=0),
    ]
    result = qf.compute_direction_asymmetry(records)
    # Should have a test for the cuda-to-omp / omp-to-cuda pair (key order may vary)
    matching_keys = [k for k in result if "cuda-to-omp" in k and "omp-to-cuda" in k]
    assert len(matching_keys) == 1, f"Expected 1 matching key, got {matching_keys}"
    key = matching_keys[0]
    # The result is a provenance-wrapped finding; extract test_result from value
    finding = result[key]
    test_result = finding["value"]["test_result"]
    # Two paired observations: (rodinia, bfs) and (hecbench, bfs) — separate suites
    assert test_result["n_paired"] == 2


# ---------------------------------------------------------------------------
# Test 10: Cochran-Armitage computed per-direction AND aggregate
# ---------------------------------------------------------------------------

def test_augmentation_trends_per_direction_and_aggregate():
    """Cochran-Armitage trend computed per-direction and aggregate."""
    records = []
    for level in range(5):  # L0-L4
        for i in range(10):  # 10 per level
            status = "PASS" if i < (5 + level) else "BUILD_FAIL"
            records.append(_make_record(
                source_spec="rodinia-bfs-cuda",
                target_spec="rodinia-bfs-omp",
                overall_status=status,
                augment_level=level,
            ))

    result = qf.compute_augmentation_trends(records)
    # Should have aggregate
    assert "aggregate" in result
    assert "cochran_armitage" in result["aggregate"]
    # Should have per_direction
    assert "per_direction" in result
    assert "cuda-to-omp" in result["per_direction"]
    assert "cochran_armitage" in result["per_direction"]["cuda-to-omp"]
    # Should have cohens_h between adjacent levels
    assert "cohens_h_adjacent" in result["aggregate"]
