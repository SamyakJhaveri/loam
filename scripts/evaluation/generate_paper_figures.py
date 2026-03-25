#!/usr/bin/env python3
"""Generate publication-quality figures for the SC26 paper.

Reads eval results from results/evaluation/ and generates figures F2-F6
plus a LaTeX table T2. Designed to be rerun as more data arrives.

Usage:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam

    # Generate only the heatmap and taxonomy bar:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam --figures f2,f3
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.colors as mcolors  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import numpy as np  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_DISPLAY: dict[str, str] = {
    "claude-sonnet-4-6": "Claude Sonnet 4",
    "azure-gpt-4.1": "GPT-4.1",
    "groq-llama-3.3-70b-versatile": "Llama 3.3 70B",
    "gemini-2.5-flash-lite": "Gemini Flash-Lite",
}

# Okabe-Ito colorblind-safe palette (paper-optimized: green = PASS)
STATUS_COLORS: dict[str, str] = {
    "PASS":            "#009E73",
    "BUILD_FAIL":      "#E69F00",
    "RUN_FAIL":        "#CC79A7",
    "VERIFY_FAIL":     "#0072B2",
    "EXTRACTION_FAIL": "#D55E00",
}

STATUS_HATCH: dict[str, str] = {
    "PASS":            "",
    "BUILD_FAIL":      "///",
    "RUN_FAIL":        "\\\\",
    "VERIFY_FAIL":     "xxx",
    "EXTRACTION_FAIL": "...",
}

STATUS_ABBREV: dict[str, str] = {
    "PASS": "P",
    "BUILD_FAIL": "BF",
    "RUN_FAIL": "RF",
    "VERIFY_FAIL": "VF",
    "EXTRACTION_FAIL": "EF",
}

# Canonical stacking order (bottom to top in bar charts)
STATUS_ORDER: list[str] = [
    "PASS", "BUILD_FAIL", "RUN_FAIL", "EXTRACTION_FAIL", "VERIFY_FAIL",
]

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _text_color_for_bg(hex_color: str) -> str:
    """Return 'white' or 'black' for readable text on the given background."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 150 else "black"


def _save_figure(
    fig: plt.Figure, output_dir: Path, stem: str, formats: list[str],
) -> None:
    """Save figure in all requested formats."""
    for fmt in formats:
        path = output_dir / f"{stem}.{fmt}"
        fig.savefig(path, format=fmt)
        print(f"  Saved: {path}")


def setup_rcparams() -> None:
    """Configure matplotlib for publication-quality output."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
        "pdf.fonttype": 42,  # TrueType (required by ACM/IEEE venues)
        "ps.fonttype": 42,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
    })


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_individual_results(results_dir: Path) -> list[dict]:
    """Load all per-task result JSONs from results/evaluation/{model}/*.json."""
    records: list[dict] = []
    if not results_dir.exists():
        return records
    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model = model_dir.name
        if model not in MODEL_DISPLAY:
            continue
        for result_file in sorted(model_dir.glob("*.json")):
            try:
                data = json.loads(result_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if not data.get("model"):
                data["model"] = model
            if not data.get("kernel"):
                src = data.get("source_spec", "")
                parts = src.split("-")
                data["kernel"] = "-".join(parts[1:-1]) if len(parts) >= 3 else src
            records.append(data)
    return records


def load_eval_summary(results_dir: Path) -> dict:
    """Load eval_summary.json."""
    path = results_dir / "eval_summary.json"
    if not path.exists():
        print(f"ERROR: {path} not found. Run analyze_eval.py first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def build_kernel_model_matrix(
    records: list[dict],
) -> tuple[list[str], list[str], dict[tuple[str, str], str]]:
    """Build (kernel, model) -> overall_status lookup.

    Returns:
        kernels: sorted by total PASS count descending, then alphabetical
        models:  sorted by pass rate descending, then alphabetical
        lookup:  {(kernel, model_dir_name): overall_status}
    """
    lookup: dict[tuple[str, str], str] = {}
    kernel_pass: dict[str, int] = defaultdict(int)
    model_pass: dict[str, int] = defaultdict(int)
    model_total: dict[str, int] = defaultdict(int)

    for r in records:
        k = r["kernel"]
        m = r["model"]
        status = r.get("overall_status", "UNKNOWN")
        lookup[(k, m)] = status
        if status == "PASS":
            kernel_pass[k] += 1
            model_pass[m] += 1
        model_total[m] += 1

    all_kernels = sorted({k for k, _ in lookup})
    kernels = sorted(all_kernels, key=lambda k: (-kernel_pass.get(k, 0), k))

    all_models = sorted({m for _, m in lookup})
    models = sorted(
        all_models,
        key=lambda m: (-model_pass.get(m, 0) / max(model_total.get(m, 1), 1), m),
    )

    return kernels, models, lookup


# ---------------------------------------------------------------------------
# F2: Kernel x Model Heatmap
# ---------------------------------------------------------------------------


def generate_f2_heatmap(
    kernels: list[str],
    models: list[str],
    lookup: dict[tuple[str, str], str],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F2: Kernel x Model result heatmap."""
    n_kernels = len(kernels)
    n_models = len(models)

    # Map statuses to integer indices
    status_to_idx = {s: i for i, s in enumerate(STATUS_ORDER)}
    matrix = np.zeros((n_kernels, n_models), dtype=int)

    for i, kernel in enumerate(kernels):
        for j, model in enumerate(models):
            status = lookup.get((kernel, model), "UNKNOWN")
            matrix[i, j] = status_to_idx.get(status, len(STATUS_ORDER))

    # Build categorical colormap
    colors = [STATUS_COLORS[s] for s in STATUS_ORDER]
    cmap = mcolors.ListedColormap(colors)
    bounds = list(range(len(STATUS_ORDER) + 1))
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    # Annotate cells
    for i, kernel in enumerate(kernels):
        for j, model in enumerate(models):
            status = lookup.get((kernel, model), "UNKNOWN")
            abbrev = STATUS_ABBREV.get(status, "?")
            bg_color = STATUS_COLORS.get(status, "#FFFFFF")
            text_color = _text_color_for_bg(bg_color)
            ax.text(
                j, i, abbrev,
                ha="center", va="center",
                fontsize=9, fontweight="bold", color=text_color,
            )

    # Axis labels
    ax.set_xticks(range(n_models))
    ax.set_xticklabels(
        [MODEL_DISPLAY.get(m, m) for m in models],
        rotation=30, ha="right",
    )
    ax.set_yticks(range(n_kernels))
    ax.set_yticklabels(kernels)

    # Move x-axis to top for readability
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Grid lines between cells
    for i in range(n_kernels + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1)
    for j in range(n_models + 1):
        ax.axvline(j - 0.5, color="white", linewidth=1)

    # Legend (only statuses present in data)
    present = sorted(
        {lookup[k] for k in lookup if lookup[k] in STATUS_COLORS},
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = [
        Patch(
            facecolor=STATUS_COLORS[s], edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in present
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.06),
        ncol=len(present), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f2_kernel_model_heatmap", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F3: Failure Taxonomy Stacked Bar
# ---------------------------------------------------------------------------


def generate_f3_taxonomy(
    summary: dict,
    models: list[str],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F3: Failure taxonomy stacked bar chart."""
    n_models = len(models)
    x = np.arange(n_models)
    bar_width = 0.6

    fig, ax = plt.subplots(figsize=(8, 6))
    bottoms = np.zeros(n_models)

    for status in STATUS_ORDER:
        counts = np.array([
            summary["by_model"][m]["by_status"].get(status, 0)
            for m in models
        ], dtype=float)
        bars = ax.bar(
            x, counts, bar_width,
            bottom=bottoms,
            color=STATUS_COLORS[status],
            hatch=STATUS_HATCH[status],
            edgecolor="black", linewidth=0.5,
            label=status.replace("_", " "),
        )
        # Annotate non-zero segments
        for i, (count, bottom) in enumerate(zip(counts, bottoms)):
            if count > 0:
                ax.text(
                    x[i], bottom + count / 2, str(int(count)),
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                )
        bottoms += counts

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_DISPLAY.get(m, m) for m in models])
    ax.set_ylabel("Number of Kernels")
    ax.set_ylim(0, max(bottoms) + 1)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Legend at top
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, 1.12),
        ncol=len(STATUS_ORDER), frameon=False, fontsize=8,
    )

    _save_figure(fig, output_dir, "f3_failure_taxonomy", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F4, F5, F6: Placeholder figures
# ---------------------------------------------------------------------------


def generate_placeholder(
    figure_id: str,
    title: str,
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate a placeholder figure with centered text."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(
        0.5, 0.5,
        f"Figure {figure_id.upper()}: {title}\n(data pending)",
        ha="center", va="center",
        fontsize=14, color="#666666", style="italic",
        transform=ax.transAxes,
    )
    ax.set_axis_off()
    slug = title.lower().replace(" ", "_").replace("-", "_")
    _save_figure(fig, output_dir, f"{figure_id}_{slug}", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# T2: Model Comparison LaTeX Table
# ---------------------------------------------------------------------------


def generate_t2_latex(
    summary: dict,
    models: list[str],
    output_dir: Path,
    verbose: bool,
) -> None:
    """Generate T2: Model comparison LaTeX table (.tex file)."""
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Model & PASS & Total & Rate (\%) & BUILD\_FAIL & RUN\_FAIL & EXTR\_FAIL \\",
        r"\midrule",
    ]

    for m in models:
        info = summary["by_model"][m]
        display = MODEL_DISPLAY.get(m, m)
        p = info["pass"]
        t = info["total"]
        rate = info["rate"] * 100
        bf = info["by_status"].get("BUILD_FAIL", 0)
        rf = info["by_status"].get("RUN_FAIL", 0)
        ef = info["by_status"].get("EXTRACTION_FAIL", 0)
        lines.append(
            f"{display} & {p} & {t} & {rate:.1f} & {bf} & {rf} & {ef} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    path = output_dir / "t2_model_comparison.tex"
    path.write_text("\n".join(lines) + "\n")
    print(f"  Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate publication-quality figures for the SC26 paper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-root", type=Path, default=PROJECT_ROOT,
        help="Absolute path to project root",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: {project-root}/docs/paper/figures/)",
    )
    parser.add_argument(
        "--format", default="pdf,png",
        help="Comma-separated output formats (default: pdf,png)",
    )
    parser.add_argument(
        "--figures", default=None,
        help="Comma-separated figure IDs to generate (default: all). E.g., f2,f3",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
    )
    args = parser.parse_args()

    setup_rcparams()

    project_root = args.project_root.resolve()
    results_dir = project_root / "results" / "evaluation"
    output_dir = (
        args.output_dir or (project_root / "docs" / "paper" / "figures")
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    formats = [f.strip() for f in args.format.split(",")]

    requested: set[str]
    if args.figures:
        requested = {f.strip().lower() for f in args.figures.split(",")}
    else:
        requested = {"f2", "f3", "f4", "f5", "f6", "t2"}

    # Load data
    records = load_individual_results(results_dir)
    if not records:
        print("ERROR: No result files found in", results_dir, file=sys.stderr)
        sys.exit(1)
    summary = load_eval_summary(results_dir)

    kernels, models, lookup = build_kernel_model_matrix(records)

    print(f"Loaded {len(records)} results from {results_dir}")
    print(f"Models: {[MODEL_DISPLAY.get(m, m) for m in models]}")
    print(f"Kernels: {len(kernels)}")
    print(f"Output: {output_dir}")
    print(f"Formats: {formats}")
    print()

    # F2: Heatmap
    if "f2" in requested:
        print("Generating F2: Kernel x Model Heatmap...")
        generate_f2_heatmap(kernels, models, lookup, output_dir, formats, args.verbose)
        print()

    # F3: Failure taxonomy
    if "f3" in requested:
        print("Generating F3: Failure Taxonomy Stacked Bar...")
        generate_f3_taxonomy(summary, models, output_dir, formats, args.verbose)
        print()

    # F4: Augmentation robustness (placeholder)
    if "f4" in requested:
        print("Generating F4: Augmentation Robustness (placeholder)...")
        generate_placeholder(
            "f4", "Augmentation Robustness", output_dir, formats, args.verbose,
        )
        print()

    # F5: Cross-direction comparison (placeholder)
    if "f5" in requested:
        print("Generating F5: Cross-Direction Comparison (placeholder)...")
        generate_placeholder(
            "f5", "Cross-Direction Comparison", output_dir, formats, args.verbose,
        )
        print()

    # F6: XSBench multi-API (placeholder)
    if "f6" in requested:
        print("Generating F6: XSBench Multi-API (placeholder)...")
        generate_placeholder(
            "f6", "XSBench Multi-API", output_dir, formats, args.verbose,
        )
        print()

    # T2: LaTeX table
    if "t2" in requested:
        print("Generating T2: Model Comparison LaTeX Table...")
        generate_t2_latex(summary, models, output_dir, args.verbose)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
