"""
TDD validation tests for the Qwen primary campaign result JSONs.

Tests validate that the non-Rodinia suites (xsbench, rsbench, mixbench, hecbench)
have the expected number of result files at all augmentation levels (L0-L4),
correct schema fields, and valid status values.

Run:  python3 -m pytest tests/test_campaign_results.py -v
"""

import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")
MODEL_DIR = PROJECT_ROOT / "results" / "evaluation" / "together-qwen-3.5-397b-a17b"

SUITES = ["xsbench", "rsbench", "mixbench", "hecbench"]

# Expected L0 translation pairs per suite (before augmentation levels multiply them)
EXPECTED_L0_PAIRS = {
    "xsbench": 6,   # 3 APIs x 2 directions = 6
    "rsbench": 6,   # 3 APIs x 2 directions = 6
    "mixbench": 6,  # 3 APIs x 2 directions = 6
    "hecbench": 28,  # cuda-to-omp:5 + omp-to-cuda:5 + cuda-to-omp_target:8 + omp_target-to-cuda:10
}

VALID_STATUSES = {"PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "ERROR", "SKIP", "EXTRACTION_FAIL"}

REQUIRED_FIELDS = {"overall_status", "source_spec", "target_spec", "augment_level", "temperature", "model"}

AUGMENT_LEVELS = {0, 1, 2, 3, 4}


def _load_primary_results(suite: str) -> list[dict]:
    """Load only primary (temp=0.0) result JSONs for a given suite.

    Primary results have no -s[0-9] suffix in the filename.
    Filters to files whose name starts with the suite prefix.
    """
    results = []
    if not MODEL_DIR.is_dir():
        return results
    for path in sorted(MODEL_DIR.glob(f"{suite}-*.json")):
        # Skip pass@k samples (filenames with -s0, -s1, -s2 suffix)
        if re.search(r"-s\d+\.json$", path.name):
            continue
        with open(path) as f:
            data = json.load(f)
        # Double-check temperature
        if data.get("temperature", 0.0) == 0.0:
            data["_path"] = str(path)
            results.append(data)
    return results


# ---------------------------------------------------------------------------
# TestPrimaryCampaignExists
# ---------------------------------------------------------------------------

class TestPrimaryCampaignExists:
    """Verify that the expected number of primary result files exist per suite."""

    @pytest.mark.parametrize("suite", SUITES)
    def test_suite_has_primary_results(self, suite: str):
        """Each suite should have L0_pairs * 5 levels = total primary results."""
        results = _load_primary_results(suite)
        expected = EXPECTED_L0_PAIRS[suite] * len(AUGMENT_LEVELS)
        assert len(results) == expected, (
            f"{suite}: expected {expected} primary results "
            f"({EXPECTED_L0_PAIRS[suite]} L0 pairs x {len(AUGMENT_LEVELS)} levels), "
            f"got {len(results)}"
        )

    @pytest.mark.parametrize("suite", SUITES)
    def test_all_levels_present(self, suite: str):
        """All 5 augmentation levels (0-4) must be represented."""
        results = _load_primary_results(suite)
        if not results:
            pytest.skip(f"No primary results for {suite} yet")
        levels_found = {r.get("augment_level") for r in results}
        assert levels_found == AUGMENT_LEVELS, (
            f"{suite}: expected levels {AUGMENT_LEVELS}, got {levels_found}"
        )


# ---------------------------------------------------------------------------
# TestResultSchema
# ---------------------------------------------------------------------------

class TestResultSchema:
    """Validate the schema/content of each primary result JSON."""

    @pytest.fixture(params=SUITES)
    def suite_results(self, request) -> tuple[str, list[dict]]:
        suite = request.param
        results = _load_primary_results(suite)
        if not results:
            pytest.skip(f"No primary results for {suite} yet")
        return suite, results

    def test_temperature_is_zero(self, suite_results):
        """All primary results must have temperature=0.0."""
        suite, results = suite_results
        for r in results:
            assert r["temperature"] == 0.0, (
                f"{r['_path']}: expected temperature=0.0, got {r['temperature']}"
            )

    def test_has_required_fields(self, suite_results):
        """Each result must contain all required top-level fields."""
        suite, results = suite_results
        for r in results:
            missing = REQUIRED_FIELDS - set(r.keys())
            assert not missing, (
                f"{r['_path']}: missing fields {missing}"
            )

    def test_attempts_array_exists(self, suite_results):
        """Each result must have 1-3 attempts."""
        suite, results = suite_results
        for r in results:
            attempts = r.get("attempts")
            assert attempts is not None and isinstance(attempts, list), (
                f"{r['_path']}: 'attempts' field is missing or not a list"
            )
            assert 1 <= len(attempts) <= 3, (
                f"{r['_path']}: expected 1-3 attempts, got {len(attempts)}"
            )

    def test_no_passk_filename_suffix(self, suite_results):
        """Files with -s[0-9] suffix must NOT have temp=0.0.

        This is the inverse check: if we loaded a file (temp=0.0)
        it must NOT have a sample suffix in its filename.
        """
        suite, results = suite_results
        for r in results:
            path = r["_path"]
            assert not re.search(r"-s\d+\.json$", path), (
                f"{path}: has sample suffix but temperature is 0.0"
            )


# ---------------------------------------------------------------------------
# TestAugmentationEffect
# ---------------------------------------------------------------------------

class TestAugmentationEffect:
    """Validate augmentation-level specific properties."""

    @pytest.fixture(params=SUITES)
    def suite_results(self, request) -> tuple[str, list[dict]]:
        suite = request.param
        results = _load_primary_results(suite)
        if not results:
            pytest.skip(f"No primary results for {suite} yet")
        return suite, results

    def test_augmentation_levels_have_valid_status(self, suite_results):
        """Every result must have an overall_status from the known set."""
        suite, results = suite_results
        for r in results:
            status = r.get("overall_status")
            assert status in VALID_STATUSES, (
                f"{r['_path']}: overall_status={status!r} not in {VALID_STATUSES}"
            )
