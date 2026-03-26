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
import re
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

# Verified augmentation robustness data (Rodinia cuda-to-omp, seed=42)
# Source: individual result files, verified 2026-03-25
AUG_ROBUSTNESS: dict[str, list[int]] = {
    "claude-sonnet-4-6":          [12, 12, 12, 12, 12],  # L0..L4 PASS / 17 tasks
    "gemini-2.5-flash-lite":      [4,  4,  4,  3,  1],
    "groq-llama-3.3-70b-versatile": [5, 6,  6,  4,  4],
}
AUG_TOTAL = 17  # Rodinia cuda-to-omp kernels evaluated


def _augment_level_from_stem(stem: str) -> int:
    """Return the augmentation level encoded in a result filename stem.

    L0 files have no level suffix: ``rodinia-bfs-cuda-to-rodinia-bfs-omp``.
    L1-L4 files end with ``-L{n}``:   ``...-omp-L1``.
    """
    m = re.search(r"-L([1-4])$", stem)
    return int(m.group(1)) if m else 0


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
            # Detect augmentation level from filename (L0 = no suffix)
            data["augment_level"] = _augment_level_from_stem(result_file.stem)
            # Detect suite and API direction from spec IDs
            src_spec = data.get("source_spec", "")
            tgt_spec = data.get("target_spec", "")
            data["suite"] = src_spec.split("-")[0] if src_spec else ""
            src_api = src_spec.rsplit("-", 1)[-1] if src_spec else ""
            tgt_api = tgt_spec.rsplit("-", 1)[-1] if tgt_spec else ""
            data["direction"] = f"{src_api}-to-{tgt_api}"
            if not data.get("kernel"):
                parts = src_spec.split("-")
                data["kernel"] = "-".join(parts[1:-1]) if len(parts) >= 3 else src_spec
            records.append(data)
    return records


def load_eval_summary(results_dir: Path) -> dict:
    """Load eval_summary.json."""
    path = results_dir / "eval_summary.json"
    if not path.exists():
        print(f"ERROR: {path} not found. Run analyze_eval.py first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def filter_records(
    records: list[dict],
    level: int = 0,
    suite: str | None = None,
    direction: str | None = None,
) -> list[dict]:
    """Filter result records by augmentation level, suite, and/or direction."""
    out = [r for r in records if r.get("augment_level", 0) == level]
    if suite:
        out = [r for r in out if r.get("suite", "") == suite]
    if direction:
        out = [r for r in out if r.get("direction", "") == direction]
    return out


def build_kernel_model_matrix(
    records: list[dict],
    level: int = 0,
    suite: str | None = "rodinia",
    direction: str | None = "cuda-to-omp",
) -> tuple[list[str], list[str], dict[tuple[str, str], str]]:
    """Build (kernel, model) -> overall_status lookup.

    Defaults to L0 Rodinia cuda-to-omp to avoid mixing augmented levels
    or cross-direction results into the primary heatmap.

    Returns:
        kernels: sorted by total PASS count descending, then alphabetical
        models:  sorted by pass rate descending, then alphabetical
        lookup:  {(kernel, model_dir_name): overall_status}
    """
    filtered = filter_records(records, level=level, suite=suite, direction=direction)
    lookup: dict[tuple[str, str], str] = {}
    kernel_pass: dict[str, int] = defaultdict(int)
    model_pass: dict[str, int] = defaultdict(int)
    model_total: dict[str, int] = defaultdict(int)

    for r in filtered:
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
# F4: Augmentation Robustness Line Chart
# ---------------------------------------------------------------------------


def generate_f4_augmentation(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F4: Augmentation robustness — pass rate vs. augmentation level.

    Uses AUG_ROBUSTNESS verified data (Rodinia cuda-to-omp, seed=42, 17 kernels).
    """
    levels = [0, 1, 2, 3, 4]
    level_labels = ["L0\n(original)", "L1", "L2", "L3", "L4\n(max)"]

    # Line style per model for print-safe rendering
    line_styles = {
        "claude-sonnet-4-6":           ("o-", "#009E73", "solid"),
        "gemini-2.5-flash-lite":        ("s--", "#E69F00", "dashed"),
        "groq-llama-3.3-70b-versatile": ("^:", "#CC79A7", "dotted"),
    }

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for model, pass_counts in AUG_ROBUSTNESS.items():
        rates = [c / AUG_TOTAL * 100 for c in pass_counts]
        marker_ls, color, ls = line_styles[model]
        label = MODEL_DISPLAY.get(model, model)
        ax.plot(
            levels, rates,
            marker_ls,
            color=color,
            linewidth=1.8,
            markersize=7,
            label=label,
        )
        # Annotate endpoint
        ax.annotate(
            f"{rates[-1]:.0f}%",
            xy=(4, rates[-1]),
            xytext=(4.08, rates[-1]),
            fontsize=8, va="center", color=color,
        )

    ax.set_xticks(levels)
    ax.set_xticklabels(level_labels)
    ax.set_xlabel("Augmentation Level")
    ax.set_ylabel("Pass Rate (%)")
    ax.set_ylim(-2, 85)
    ax.set_xlim(-0.2, 4.7)
    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
    ax.grid(axis="y", linestyle="--", alpha=0.4, linewidth=0.6)

    # Highlight L0 baseline
    ax.axvline(0, color="grey", linewidth=0.8, linestyle="--", alpha=0.5)

    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    ax.set_title(
        "Augmentation Robustness: Pass Rate across L0–L4\n"
        "(Rodinia CUDA→OpenMP, 17 kernels, seed=42)",
        fontsize=10,
    )

    _save_figure(fig, output_dir, "f4_augmentation_robustness", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F5: Cross-Direction Comparison (XSBench, L0, 3 models)
# ---------------------------------------------------------------------------

# Verified XSBench L0 cross-direction data (individual files, 2026-03-25)
XSBENCH_L0: dict[str, dict[str, str]] = {
    "cuda-to-omp":         {"claude": "RUN_FAIL",    "gemini": "BUILD_FAIL",   "groq": "EXTRACTION_FAIL"},
    "cuda-to-opencl":      {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "RUN_FAIL"},
    "cuda-to-omp_target":  {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp-to-cuda":         {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "PASS"},
    "omp-to-opencl":       {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "EXTRACTION_FAIL"},
    "omp-to-omp_target":   {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp_target-to-cuda":  {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp_target-to-omp":   {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "BUILD_FAIL"},
    "omp_target-to-opencl":{"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "RUN_FAIL"},
    "opencl-to-cuda":      {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "RUN_FAIL"},
    "opencl-to-omp":       {"claude": "RUN_FAIL",    "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "opencl-to-omp_target":{"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
}

_XS_MODELS = ["claude", "gemini", "groq"]
_XS_MODEL_DISPLAY = {
    "claude": "Claude Sonnet 4",
    "gemini": "Gemini Flash-Lite",
    "groq":   "Llama 3.3 70B",
}
_XS_MODEL_COLORS = {
    "claude": "#009E73",
    "gemini": "#E69F00",
    "groq":   "#CC79A7",
}


def generate_f5_cross_direction(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F5: XSBench cross-direction pass/fail grouped bar chart (L0, 3 models)."""
    directions = list(XSBENCH_L0.keys())
    n_dirs = len(directions)
    n_models = len(_XS_MODELS)
    bar_width = 0.22
    x = np.arange(n_dirs)

    fig, ax = plt.subplots(figsize=(12, 4.5))

    for i, model in enumerate(_XS_MODELS):
        is_pass = np.array([
            1 if XSBENCH_L0[d][model] == "PASS" else 0
            for d in directions
        ], dtype=float)
        offset = (i - n_models / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset, is_pass, bar_width,
            color=_XS_MODEL_COLORS[model],
            edgecolor="black", linewidth=0.5,
            label=_XS_MODEL_DISPLAY[model],
        )
        # Mark failures with status abbreviation below bar
        for j, (d, v) in enumerate(zip(directions, is_pass)):
            if v == 0:
                status = XSBENCH_L0[d][model]
                abbrev = STATUS_ABBREV.get(status, "?")
                ax.text(
                    x[j] + offset, 0.02, abbrev,
                    ha="center", va="bottom",
                    fontsize=6, color="#444444", rotation=90,
                )

    ax.set_xticks(x)
    dir_labels = [d.replace("-to-", "→").replace("_target", "-T") for d in directions]
    ax.set_xticklabels(dir_labels, rotation=35, ha="right", fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["FAIL", "PASS"])
    ax.set_ylabel("Result")
    ax.set_ylim(-0.1, 1.25)
    ax.set_title(
        "XSBench Cross-Direction Results (L0, 12 directions, 3 models)\n"
        "Claude: 10/12 PASS  |  Gemini: 0/12 PASS  |  Llama: 1/12 PASS",
        fontsize=10,
    )
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)

    _save_figure(fig, output_dir, "f5_xsbench_cross_direction", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F6: XSBench Direction x Model Heatmap
# ---------------------------------------------------------------------------


def generate_f6_xsbench(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F6: XSBench 12-direction × 3-model status heatmap (L0)."""
    directions = list(XSBENCH_L0.keys())
    models = _XS_MODELS

    status_to_idx = {s: i for i, s in enumerate(STATUS_ORDER)}
    matrix = np.zeros((len(directions), len(models)), dtype=int)

    for i, d in enumerate(directions):
        for j, m in enumerate(models):
            status = XSBENCH_L0[d].get(m, "UNKNOWN")
            matrix[i, j] = status_to_idx.get(status, len(STATUS_ORDER))

    colors = [STATUS_COLORS[s] for s in STATUS_ORDER]
    cmap = mcolors.ListedColormap(colors)
    bounds = list(range(len(STATUS_ORDER) + 1))
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(6, 7))
    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    for i, d in enumerate(directions):
        for j, m in enumerate(models):
            status = XSBENCH_L0[d].get(m, "UNKNOWN")
            abbrev = STATUS_ABBREV.get(status, "?")
            bg = STATUS_COLORS.get(status, "#FFFFFF")
            ax.text(
                j, i, abbrev,
                ha="center", va="center",
                fontsize=9, fontweight="bold",
                color=_text_color_for_bg(bg),
            )

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([_XS_MODEL_DISPLAY[m] for m in models], rotation=20, ha="right")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    dir_labels = [d.replace("-to-", "→").replace("_target", "-Target") for d in directions]
    ax.set_yticks(range(len(directions)))
    ax.set_yticklabels(dir_labels)

    for i in range(len(directions) + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1)
    for j in range(len(models) + 1):
        ax.axvline(j - 0.5, color="white", linewidth=1)

    present_statuses = sorted(
        {XSBENCH_L0[d][m] for d in directions for m in models if XSBENCH_L0[d].get(m) in STATUS_COLORS},
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = [
        Patch(facecolor=STATUS_COLORS[s], edgecolor="black", linewidth=0.5, label=s.replace("_", " "))
        for s in present_statuses
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.08),
        ncol=len(present_statuses), frameon=False, fontsize=8,
    )
    ax.set_title("XSBench: 12-Direction × 3-Model Results (L0)", fontsize=10, pad=40)

    _save_figure(fig, output_dir, "f6_xsbench_heatmap", formats)
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
        "--level", type=int, default=0,
        help="Augmentation level to use for F2/F3/T2 (default: 0 = L0 unmodified source)",
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

    # Build Rodinia cuda-to-omp L0 matrix for primary figures
    kernels, models, lookup = build_kernel_model_matrix(
        records, level=args.level, suite="rodinia", direction="cuda-to-omp",
    )

    l0_records = filter_records(records, level=args.level, suite="rodinia", direction="cuda-to-omp")
    l0_total = len(l0_records)

    print(f"Loaded {len(records)} total results; {l0_total} L{args.level} Rodinia cuda-to-omp")
    print(f"Models: {[MODEL_DISPLAY.get(m, m) for m in models]}")
    print(f"Kernels: {len(kernels)}")
    print(f"Output: {output_dir}")
    print(f"Formats: {formats}")
    print()

    # F2: Heatmap (L0 Rodinia cuda-to-omp, 4 models x 17 kernels)
    if "f2" in requested:
        print("Generating F2: Kernel x Model Heatmap (L0 Rodinia cuda-to-omp)...")
        generate_f2_heatmap(kernels, models, lookup, output_dir, formats, args.verbose)
        print()

    # F3: Failure taxonomy (L0 Rodinia cuda-to-omp, per-model breakdown)
    if "f3" in requested:
        print("Generating F3: Failure Taxonomy Stacked Bar (L0 Rodinia cuda-to-omp)...")
        # Build per-model status counts from filtered L0 records
        l0_summary: dict = {"by_model": {}}
        for r in l0_records:
            m = r["model"]
            if m not in l0_summary["by_model"]:
                l0_summary["by_model"][m] = {"pass": 0, "total": 0, "rate": 0.0, "by_status": {}}
            entry = l0_summary["by_model"][m]
            status = r.get("overall_status", "UNKNOWN")
            entry["by_status"][status] = entry["by_status"].get(status, 0) + 1
            entry["total"] += 1
            if status == "PASS":
                entry["pass"] += 1
        for m, entry in l0_summary["by_model"].items():
            entry["rate"] = entry["pass"] / entry["total"] if entry["total"] else 0.0
        generate_f3_taxonomy(l0_summary, models, output_dir, formats, args.verbose)
        print()

    # F4: Augmentation robustness — real line chart
    if "f4" in requested:
        print("Generating F4: Augmentation Robustness (verified data, 3 models)...")
        generate_f4_augmentation(output_dir, formats, args.verbose)
        print()

    # F5: XSBench cross-direction bar chart
    if "f5" in requested:
        print("Generating F5: XSBench Cross-Direction Comparison (L0, 12 directions)...")
        generate_f5_cross_direction(output_dir, formats, args.verbose)
        print()

    # F6: XSBench direction x model heatmap
    if "f6" in requested:
        print("Generating F6: XSBench Direction x Model Heatmap (L0)...")
        generate_f6_xsbench(output_dir, formats, args.verbose)
        print()

    # T2: LaTeX table (L0 Rodinia cuda-to-omp, per-model stats)
    if "t2" in requested:
        print("Generating T2: Model Comparison LaTeX Table (L0 Rodinia cuda-to-omp)...")
        l0_sum_for_t2 = l0_summary if "f3" in requested else {"by_model": {}}
        if "f3" not in requested:
            for r in l0_records:
                m = r["model"]
                if m not in l0_sum_for_t2["by_model"]:
                    l0_sum_for_t2["by_model"][m] = {"pass": 0, "total": 0, "rate": 0.0, "by_status": {}}
                entry = l0_sum_for_t2["by_model"][m]
                status = r.get("overall_status", "UNKNOWN")
                entry["by_status"][status] = entry["by_status"].get(status, 0) + 1
                entry["total"] += 1
                if status == "PASS":
                    entry["pass"] += 1
            for m, entry in l0_sum_for_t2["by_model"].items():
                entry["rate"] = entry["pass"] / entry["total"] if entry["total"] else 0.0
        generate_t2_latex(l0_sum_for_t2, models, output_dir, args.verbose)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
