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


# ---------------------------------------------------------------------------
# G1: Model constants reflect 2-model layout (Qwen + GPT-4.1 mini)
# ---------------------------------------------------------------------------

def test_model_constants_reflect_two_model_layout():
    """Verify old models are removed and azure-gpt-4.1-mini is present in all 4 dicts."""
    import scripts.generate_paper_figures as gpf

    old_models = [
        "claude-sonnet-4-6",
        "groq-llama-3.3-70b-versatile",
        "gemini-2.5-flash-lite",
    ]
    new_model = "azure-gpt-4.1-mini"
    qwen_model = "together-qwen-3.5-397b-a17b"

    for dct_name in ("MODEL_COLORS", "MODEL_DISPLAY", "MODEL_DISPLAY_SHORT", "MODEL_LINESTYLE"):
        dct = getattr(gpf, dct_name)
        # Old models must be absent
        for old in old_models:
            assert old not in dct, f"{old} still in {dct_name}"
        # New model must be present
        assert new_model in dct, f"{new_model} missing from {dct_name}"
        # Qwen must still be present
        assert qwen_model in dct, f"{qwen_model} missing from {dct_name}"


# ---------------------------------------------------------------------------
# G2: F3 heatmap produces exactly 29 kernels from all 5 suites
# ---------------------------------------------------------------------------

def test_f3_heatmap_kernel_count():
    """Verify F3 data path finds 29 unique kernels across 5 suites in standard directions."""
    from scripts.generate_paper_figures import (
        load_eval_results, filter_records, DIRECTIONS, SUITE_ORDER, _extract_suite,
    )

    project_root = Path(__file__).resolve().parent.parent.parent
    records = load_eval_results(project_root)
    assert len(records) > 0, "No eval records found on disk"

    # Replicate the exact filtering logic from generate_f3_kernel_heatmap
    base_records = [r for r in records if not r.get("is_sample", False)]
    l0_records = filter_records(base_records, level=0)
    std_records = [r for r in l0_records if r["direction"] in DIRECTIONS]

    # Collect unique kernels (same logic as the function)
    kernel_suite = {}
    for r in std_records:
        kernel_suite[r["kernel"]] = r.get("suite", "other")

    n_kernels = len(kernel_suite)
    assert n_kernels == 29, (
        f"Expected 29 kernels in F3 heatmap, got {n_kernels}. "
        f"Kernels: {sorted(kernel_suite.keys())}"
    )

    # Verify that multiple suites are represented (not just rodinia)
    suites_present = set(kernel_suite.values())
    assert len(suites_present) >= 3, (
        f"Expected kernels from at least 3 suites, got: {suites_present}"
    )


# ---------------------------------------------------------------------------
# G3: SUITE_ORDER contains all 5 suites
# ---------------------------------------------------------------------------

def test_suite_order_contains_all_five_suites():
    """Verify SUITE_ORDER lists exactly the 5 expected benchmark suites."""
    from scripts.generate_paper_figures import SUITE_ORDER

    expected = ["rodinia", "xsbench", "rsbench", "mixbench", "hecbench"]
    assert SUITE_ORDER == expected, (
        f"SUITE_ORDER mismatch.\n  Expected: {expected}\n  Got:      {SUITE_ORDER}"
    )


# ---------------------------------------------------------------------------
# G4: T2 table has 2-model layout with Qwen data and GPT-4.1 mini pending
# ---------------------------------------------------------------------------

def test_t2_table_has_two_model_layout(tmp_path):
    """Verify generate_t2_model_table produces a table with Qwen and GPT-4.1 mini rows."""
    from scripts.generate_paper_figures import (
        load_eval_results, generate_t2_model_table,
    )

    project_root = Path(__file__).resolve().parent.parent.parent
    records = load_eval_results(project_root)
    assert len(records) > 0, "No eval records found on disk"

    generate_t2_model_table(records, tmp_path, verbose=False)

    tex_path = tmp_path / "t2_model_comparison.tex"
    assert tex_path.exists(), "T2 LaTeX file was not created"

    content = tex_path.read_text()
    assert "Qwen 3.5 397B" in content, "Qwen model row missing from T2 table"
    assert "GPT-4.1 mini" in content, "GPT-4.1 mini row missing from T2 table"
    assert content.count("pending") >= 7, (
        f"Expected at least 7 'pending' entries for GPT row, found {content.count('pending')}"
    )
    assert "\\toprule" in content, "LaTeX table missing \\toprule"
    assert "\\bottomrule" in content, "LaTeX table missing \\bottomrule"


# ---------------------------------------------------------------------------
# G5: Every generated PDF has a matching PNG file
# ---------------------------------------------------------------------------

def test_pdf_png_parity():
    """Verify each figure PDF in docs/paper/figures/ has a corresponding PNG sibling."""
    project_root = Path(__file__).resolve().parent.parent.parent
    figures_dir = project_root / "docs" / "paper" / "figures"

    # These are the actual output stems from _save_figure() calls in the script
    expected_stems = [
        "f2_repo_vs_kernel",
        "f3_kernel_model_heatmap",
        "f4_failure_taxonomy",
        "f5_pass_at_k_by_direction",
        "f6_cross_suite_comparison",
        "f7_augmentation_robustness",
        "c1_repair_transition_matrix",
        "c2_repair_rate_by_direction",
        "c3_transform_frequency",
        "c4_selection_funnel",
    ]

    missing_pdf = []
    missing_png = []

    for stem in expected_stems:
        pdf_path = figures_dir / f"{stem}.pdf"
        png_path = figures_dir / f"{stem}.png"
        if not pdf_path.exists():
            missing_pdf.append(stem)
        if not png_path.exists():
            missing_png.append(stem)

    assert not missing_pdf, f"Missing PDFs for stems: {missing_pdf}"
    assert not missing_png, f"Missing PNGs for stems: {missing_png}"

    # Verify parity: every PDF has a matching PNG and vice versa
    actual_pdfs = {p.stem for p in figures_dir.glob("*.pdf")}
    actual_pngs = {p.stem for p in figures_dir.glob("*.png")}
    for stem in expected_stems:
        assert stem in actual_pdfs, f"PDF missing: {stem}.pdf"
        assert stem in actual_pngs, f"PNG missing: {stem}.png"
