"""Tests for extracted utility functions in generate_paper_figures.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_aggregate_status_counts_by_model():
    from scripts.generate_paper_figures import aggregate_status_counts
    records = [
        {"model": "claude", "overall_status": "PASS"},
        {"model": "claude", "overall_status": "FAIL"},
        {"model": "gpt", "overall_status": "PASS"},
    ]
    result = aggregate_status_counts(records, "model")
    assert result["claude"]["PASS"] == 1
    assert result["claude"]["FAIL"] == 1
    assert result["gpt"]["PASS"] == 1


def test_aggregate_status_counts_missing_status_defaults_unknown():
    from scripts.generate_paper_figures import aggregate_status_counts
    records = [{"model": "m", "overall_status": None}]
    result = aggregate_status_counts(records, "model")
    assert result["m"]["UNKNOWN"] == 1


def test_constants_exist():
    import scripts.generate_paper_figures as gpf
    assert gpf.FIGURE_DPI == 600
    assert gpf.PDF_FONTTYPE == 42
    assert isinstance(gpf.REPO_KERNEL_PAIRS, list)
    assert isinstance(gpf.HECBENCH_FUNNEL_STAGES, list)
    assert len(gpf.HECBENCH_FUNNEL_STAGES) == 5


def test_create_status_legend_returns_patches():
    from scripts.generate_paper_figures import create_status_legend
    from matplotlib.patches import Patch
    statuses = ["PASS", "BUILD_FAIL"]
    patches = create_status_legend(statuses)
    assert len(patches) == 2
    assert all(isinstance(p, Patch) for p in patches)
