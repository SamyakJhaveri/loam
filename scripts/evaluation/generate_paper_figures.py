#!/usr/bin/env python3
"""Generate publication-quality figures for the SC26 paper.

Reads eval results from results/evaluation/ and generates figures F1-F9
plus a LaTeX table T2. Designed to be rerun as more data arrives.

Figures F2-F4 are survey data visualizations (API co-occurrence, repo vs
kernel counts, HeCBench selection funnel). Figures F5-F9 are evaluation
result visualizations (heatmaps, taxonomy, augmentation, cross-direction).

Usage:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam

    # Generate only specific figures:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam --figures f1,f2,f3
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
from matplotlib.patches import Patch, FancyBboxPatch, FancyArrowPatch  # noqa: E402
import numpy as np  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# SC26 Outfit-Derived Palette
# ---------------------------------------------------------------------------
# Rose Pink, Saffron Amber, Teal, Gold, Charcoal, Slate, Warm Linen

PALETTE = {
    "rose":      "#C8607A",
    "rose_tint":  "#F8E0E5",
    "rose_dark":  "#9E4860",
    "saffron":    "#D48A35",
    "saffron_tint": "#FBF0DD",
    "saffron_dark": "#A66B28",
    "teal":       "#2E8E9E",
    "teal_tint":  "#D8F0F4",
    "teal_dark":  "#1B6573",
    "gold":       "#E6A84D",
    "gold_tint":  "#FDF5E3",
    "gold_dark":  "#B5843B",
    "charcoal":   "#2D3436",
    "slate":      "#636e72",
    "linen":      "#F5F0EB",
}

# Status → color mapping (SC26 palette)
STATUS_COLORS: dict[str, str] = {
    "PASS":            PALETTE["teal"],       # #2E8E9E
    "BUILD_FAIL":      PALETTE["rose"],       # #C8607A
    "RUN_FAIL":        PALETTE["saffron"],    # #D48A35
    "VERIFY_FAIL":     PALETTE["gold"],       # #E6A84D
    "EXTRACTION_FAIL": PALETTE["slate"],      # #636e72
}

# Model → color mapping (SC26 palette)
MODEL_COLORS: dict[str, str] = {
    "together-qwen-3.5-397b-a17b":  PALETTE["saffron"],    # #D48A35
    "claude-sonnet-4-6":            PALETTE["teal"],       # #2E8E9E
    "azure-gpt-4.1":                PALETTE["gold"],       # #E6A84D
    "groq-llama-3.3-70b-versatile": PALETTE["rose"],       # #C8607A
    "gemini-2.5-flash-lite":        PALETTE["slate"],      # #636e72
}

# Model → line style for print-safe rendering
MODEL_LINESTYLE: dict[str, tuple[str, str]] = {
    "together-qwen-3.5-397b-a17b":  ("D-.", "dashdot"),
    "claude-sonnet-4-6":            ("o-", "solid"),
    "gemini-2.5-flash-lite":        ("s--", "dashed"),
    "groq-llama-3.3-70b-versatile": ("^:", "dotted"),
}

STATUS_HATCH: dict[str, str] = {
    "PASS":            "",
    "BUILD_FAIL":      "///",
    "RUN_FAIL":        "\\\\\\\\",
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

MODEL_DISPLAY: dict[str, str] = {
    "together-qwen-3.5-397b-a17b": "Qwen 3.5\n397B",
    "claude-sonnet-4-6": "Claude\nSonnet 4",
    "azure-gpt-4.1": "GPT-4.1",
    "groq-llama-3.3-70b-versatile": "Llama 3.3\n70B",
    "gemini-2.5-flash-lite": "Gemini\nFlash-Lite",
}

MODEL_DISPLAY_SHORT: dict[str, str] = {
    "together-qwen-3.5-397b-a17b": "Qwen 3.5 397B-A17B",
    "claude-sonnet-4-6": "Claude Sonnet 4",
    "azure-gpt-4.1": "GPT-4.1",
    "groq-llama-3.3-70b-versatile": "Llama 3.3 70B",
    "gemini-2.5-flash-lite": "Gemini Flash-Lite",
}

# Canonical stacking order (bottom to top in bar charts)
STATUS_ORDER: list[str] = [
    "PASS", "BUILD_FAIL", "RUN_FAIL", "EXTRACTION_FAIL", "VERIFY_FAIL",
]

# N/A color for missing cells in heatmaps
NA_COLOR = "#E0E0E0"

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _text_color_for_bg(hex_color: str) -> str:
    """Return 'white' or 'black' for readable text on the given background."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 145 else "black"


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
    "claude-sonnet-4-6":              [12, 12, 12, 12, 12],  # L0..L4 PASS / 17 tasks
    "gemini-2.5-flash-lite":          [4,  4,  4,  3,  1],
    "groq-llama-3.3-70b-versatile":   [5,  6,  6,  4,  4],
}
AUG_TOTAL = 17  # Rodinia cuda-to-omp kernels evaluated


# Verified XSBench L0 cross-direction data (individual files, 2026-03-25)
XSBENCH_L0: dict[str, dict[str, str]] = {
    "cuda-to-omp":          {"claude": "RUN_FAIL",    "gemini": "BUILD_FAIL",   "groq": "EXTRACTION_FAIL"},
    "cuda-to-opencl":       {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "RUN_FAIL"},
    "cuda-to-omp_target":   {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp-to-cuda":          {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "PASS"},
    "omp-to-opencl":        {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "EXTRACTION_FAIL"},
    "omp-to-omp_target":    {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp_target-to-cuda":   {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "omp_target-to-omp":    {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "BUILD_FAIL"},
    "omp_target-to-opencl": {"claude": "PASS",        "gemini": "RUN_FAIL",     "groq": "RUN_FAIL"},
    "opencl-to-cuda":       {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "RUN_FAIL"},
    "opencl-to-omp":        {"claude": "RUN_FAIL",    "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
    "opencl-to-omp_target": {"claude": "PASS",        "gemini": "BUILD_FAIL",   "groq": "BUILD_FAIL"},
}

_XS_MODELS = ["claude", "gemini", "groq"]
_XS_MODEL_DISPLAY = {
    "claude": "Claude Sonnet 4",
    "gemini": "Gemini Flash-Lite",
    "groq":   "Llama 3.3 70B",
}

def _augment_level_from_stem(stem: str) -> int:
    """Return the augmentation level encoded in a result filename stem."""
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
            data["augment_level"] = _augment_level_from_stem(result_file.stem)
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
# F1: System Architecture Diagram (matplotlib fallback)
# ---------------------------------------------------------------------------


def generate_f1_architecture(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F1: ParBench system architecture diagram using matplotlib."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")

    def _draw_box(ax, x, y, w, h, color, title, subtitle="", alpha=0.15):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor=color,
            alpha=alpha, linewidth=2,
        )
        ax.add_patch(box)
        # Dark border
        border = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor="none", edgecolor=color,
            linewidth=2,
        )
        ax.add_patch(border)
        ax.text(
            x + w / 2, y + h / 2 + (0.12 if subtitle else 0),
            title, ha="center", va="center",
            fontsize=11, fontweight="bold", color=PALETTE["charcoal"],
            fontfamily="sans-serif",
        )
        if subtitle:
            ax.text(
                x + w / 2, y + h / 2 - 0.22,
                subtitle, ha="center", va="center",
                fontsize=8, color=PALETTE["slate"],
                fontfamily="sans-serif",
            )

    def _draw_small_box(ax, x, y, w, h, label):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.05",
            facecolor=PALETTE["linen"], edgecolor=PALETTE["slate"],
            linewidth=1,
        )
        ax.add_patch(box)
        ax.text(
            x + w / 2, y + h / 2, label,
            ha="center", va="center",
            fontsize=8, color=PALETTE["charcoal"],
            fontfamily="sans-serif",
        )

    def _arrow(ax, x1, y1, x2, y2, color=PALETTE["charcoal"], style="-",
               lw=1.5):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>", color=color, lw=lw,
                linestyle=style, shrinkA=0, shrinkB=0,
            ),
        )

    def _label(ax, x, y, text, color=PALETTE["slate"]):
        ax.text(
            x, y, text, ha="center", va="center",
            fontsize=7, color=color, fontfamily="sans-serif",
            fontstyle="italic",
        )

    # === Component boxes ===

    # Source Code (top-left)
    _draw_box(ax, 0.3, 4.2, 2.0, 1.0, PALETTE["slate"],
              "Source Code", "Kernel Files")

    # Augmentation Engine (top-center)
    _draw_box(ax, 3.4, 4.2, 2.4, 1.0, PALETTE["saffron"],
              "Augmentation", "6 AST Transforms, L0\u2013L4")

    # Spec JSON (left)
    _draw_box(ax, 0.3, 1.8, 2.0, 1.2, PALETTE["teal"],
              "Spec JSON", "Correctness Contracts")

    # Evaluation Pipeline (center)
    _draw_box(ax, 3.4, 1.8, 2.8, 1.2, PALETTE["rose"],
              "Evaluation Pipeline", "LLM Prompt \u2192 Response \u2192 Extract")

    # Harness Pipeline (right)
    _draw_box(ax, 7.2, 1.8, 3.0, 1.2, PALETTE["teal"],
              "Harness Pipeline", "")

    # Harness sub-stages
    _draw_small_box(ax, 7.35, 1.9, 0.8, 0.5, "Build")
    _draw_small_box(ax, 8.3, 1.9, 0.7, 0.5, "Run")
    _draw_small_box(ax, 9.15, 1.9, 0.9, 0.5, "Verify")

    # Sub-stage arrows
    _arrow(ax, 8.15, 2.15, 8.3, 2.15, color=PALETTE["slate"], lw=1.0)
    _arrow(ax, 9.0, 2.15, 9.15, 2.15, color=PALETTE["slate"], lw=1.0)

    # Result JSON (far right)
    _draw_box(ax, 10.6, 1.8, 1.2, 1.2, PALETTE["gold"],
              "Result", "PASS / FAIL")

    # === Arrows ===

    # Source -> Augmentation
    _arrow(ax, 2.3, 4.7, 3.4, 4.7)
    _label(ax, 2.85, 4.9, "original source")

    # Augmentation -> Evaluation Pipeline
    _arrow(ax, 4.6, 4.2, 4.6, 3.0)
    _label(ax, 5.35, 3.6, "augmented source")

    # Spec -> Evaluation Pipeline
    _arrow(ax, 2.3, 2.4, 3.4, 2.4)
    _label(ax, 2.85, 2.6, "prompt config")

    # Spec -> Harness (verification config — goes below)
    ax.annotate(
        "", xy=(7.2, 1.8), xytext=(1.3, 1.8),
        arrowprops=dict(
            arrowstyle="-|>", color=PALETTE["charcoal"], lw=1.5,
            connectionstyle="arc3,rad=-0.25",
            shrinkA=0, shrinkB=0,
        ),
    )
    _label(ax, 4.3, 1.15, "build / run / verify config")

    # Evaluation -> Harness
    _arrow(ax, 6.2, 2.4, 7.2, 2.4)
    _label(ax, 6.7, 2.6, "translated files")

    # Harness -> Result
    _arrow(ax, 10.2, 2.4, 10.6, 2.4)
    _label(ax, 10.4, 2.6, "verdict")

    # Self-repair loop: Verify -> Evaluation Pipeline (dashed, rose)
    ax.annotate(
        "", xy=(5.0, 1.8), xytext=(9.6, 1.9),
        arrowprops=dict(
            arrowstyle="-|>", color=PALETTE["rose"], lw=1.5,
            linestyle="dashed",
            connectionstyle="arc3,rad=0.35",
            shrinkA=2, shrinkB=2,
        ),
    )
    _label(ax, 7.5, 0.85, "self-repair (on FAIL)", color=PALETTE["rose_dark"])

    _save_figure(fig, output_dir, "f1_system_architecture", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F2: API Co-occurrence Heatmap (survey data)
# ---------------------------------------------------------------------------


def generate_f2_api_cooccurrence(
    project_root: Path,
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F2: API co-occurrence heatmap across 35 surveyed HPC repos.

    Data source: analysis/data/API_pairwise_coverage_matrix__counts_.csv
    """
    csv_path = project_root / "analysis" / "data" / "API_pairwise_coverage_matrix__counts_.csv"
    if not csv_path.exists():
        print(f"  ERROR: {csv_path} not found — skipping F2", file=sys.stderr)
        return

    # Read the CSV into a matrix
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        apis = [h.strip() for h in header[1:] if h.strip()]
        matrix = []
        row_labels = []
        for row in reader:
            if not row or not row[0].strip():
                continue
            row_labels.append(row[0].strip())
            matrix.append([int(x.strip()) for x in row[1:] if x.strip()])

    n = len(apis)
    data = np.array(matrix, dtype=float)

    if verbose:
        print(f"  Loaded {n}x{n} co-occurrence matrix from {csv_path}")
        print(f"  APIs: {apis}")

    # Build a sequential colormap from linen (low) to teal (high)
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "sc26_cooccurrence",
        [PALETTE["linen"], PALETTE["teal_tint"], PALETTE["teal"], PALETTE["teal_dark"]],
        N=256,
    )

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(data, cmap=cmap, aspect="equal", vmin=0, vmax=data.max())

    # Annotate each cell with count
    for i in range(n):
        for j in range(n):
            val = int(data[i, j])
            # Determine text color based on background intensity
            norm_val = data[i, j] / data.max()
            text_color = "white" if norm_val > 0.55 else PALETTE["charcoal"]
            fontweight = "bold"
            fontsize = 10
            # Highlight CUDA-OpenMP cell (row=0/CUDA, col=1/OpenMP or row=1/OpenMP, col=0/CUDA)
            is_cuda_omp = (
                (row_labels[i] == "CUDA" and apis[j] == "OpenMP")
                or (row_labels[i] == "OpenMP" and apis[j] == "CUDA")
            )
            if is_cuda_omp:
                fontsize = 12
                fontweight = "extra bold"
                # Draw a rectangle border to highlight
                rect = plt.Rectangle(
                    (j - 0.5, i - 0.5), 1, 1,
                    linewidth=2.5, edgecolor=PALETTE["rose"],
                    facecolor="none", zorder=3,
                )
                ax.add_patch(rect)
            ax.text(
                j, i, str(val),
                ha="center", va="center",
                fontsize=fontsize, fontweight=fontweight,
                color=text_color,
            )

    # Axis labels
    ax.set_xticks(range(n))
    ax.set_xticklabels(
        [a.replace("OpenMP_Target", "OMP\nTarget") for a in apis],
        rotation=45, ha="right", fontsize=9,
    )
    ax.set_yticks(range(n))
    ax.set_yticklabels(
        [a.replace("OpenMP_Target", "OMP Target") for a in row_labels],
        fontsize=9,
    )

    # Grid lines
    for i in range(n + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1.5)
        ax.axvline(i - 0.5, color="white", linewidth=1.5)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Number of Repositories", fontsize=10)

    ax.set_title(
        "API Co-occurrence Across 35 HPC Benchmark Repositories",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, "f2_api_cooccurrence_survey", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F3: Repository-Level vs Kernel-Level Counts
# ---------------------------------------------------------------------------


def generate_f3_repo_vs_kernel(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F3: Grouped bar chart comparing repo-level vs kernel-level counts.

    Data sources: analysis/data/API_pairwise_coverage_matrix__counts_.csv (repo counts)
                  analysis/reports/kernel_level_analysis.md (kernel counts)
    Pairs: CUDA-OpenMP (6 repos, 472 kernels), CUDA-HIP (3 repos, 633 kernels),
           CUDA-SYCL (2 repos, 616 kernels).
    """
    # Repo counts from API_pairwise_coverage_matrix__counts_.csv (authoritative)
    # Kernel counts from kernel_level_analysis.md (verified)
    pairs = [
        ("CUDA\u2013OpenMP",  6, 472),
        ("CUDA\u2013HIP",     3, 633),
        ("CUDA\u2013SYCL",    2, 616),
    ]
    labels = [p[0] for p in pairs]
    repo_counts = np.array([p[1] for p in pairs], dtype=float)
    kernel_counts = np.array([p[2] for p in pairs], dtype=float)
    multipliers = [f"{int(k / r)}x" for r, k in zip(repo_counts, kernel_counts)]

    if verbose:
        for lbl, r, k, m in zip(labels, repo_counts, kernel_counts, multipliers):
            print(f"  {lbl}: {int(r)} repos -> {int(k)} kernels ({m})")

    x = np.arange(len(labels))
    bar_width = 0.32

    fig, ax = plt.subplots(figsize=(8, 5))

    bars_repo = ax.bar(
        x - bar_width / 2, repo_counts, bar_width,
        color=PALETTE["teal_tint"], edgecolor=PALETTE["teal"],
        linewidth=1.2, label="Repository Count",
    )
    bars_kernel = ax.bar(
        x + bar_width / 2, kernel_counts, bar_width,
        color=PALETTE["teal"], edgecolor=PALETTE["teal_dark"],
        linewidth=1.2, label="Kernel Count",
    )

    # Log scale
    ax.set_yscale("log")
    ax.set_ylim(5, 2500)

    # Annotate bars with exact counts
    for i, (r, k) in enumerate(zip(repo_counts, kernel_counts)):
        ax.text(
            x[i] - bar_width / 2, r * 1.15, str(int(r)),
            ha="center", va="bottom", fontsize=9, fontweight="bold",
            color=PALETTE["teal_dark"],
        )
        ax.text(
            x[i] + bar_width / 2, k * 1.15, str(int(k)),
            ha="center", va="bottom", fontsize=9, fontweight="bold",
            color=PALETTE["charcoal"],
        )

    # Multiplier labels above each pair
    for i, mult in enumerate(multipliers):
        max_val = max(repo_counts[i], kernel_counts[i])
        ax.text(
            x[i], max_val * 2.2, mult,
            ha="center", va="bottom", fontsize=13, fontweight="bold",
            color=PALETTE["rose"],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Count (log scale)", fontsize=11)
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)
    ax.set_title(
        "Repository-Level vs. Kernel-Level Translation Pair Counts",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, "f3_repo_vs_kernel", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F4: HeCBench Kernel Selection Funnel
# ---------------------------------------------------------------------------


def generate_f4_selection_funnel(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F4: HeCBench kernel selection pipeline funnel diagram.

    Data source: analysis/reports/kernel_selection_candidates.md and
    analysis/reports/kernel_level_analysis.md.
    Stages: 506 total -> 327 (4-API) -> 325 (Makefiles) -> 242 (self-checking)
            -> 60 final (complexity, deps, diversity filters).
    """
    # Data verified against source files
    stages = [
        ("HeCBench kernels total",                           506, None),
        ("All 4 API variants\n(CUDA, HIP, SYCL, OMP)",      327, "\u2212179: missing API variants"),
        ("With Makefiles",                                   325, "\u22122: no Makefile"),
        ("With self-checking\n(PASS/FAIL/verify patterns)",  242, "\u221283: no verification"),
        ("Final selected\n(complexity, deps, diversity)",      60, "\u2212182: complexity/deps/diversity"),
    ]

    labels = [s[0] for s in stages]
    values = [s[1] for s in stages]
    exclusions = [s[2] for s in stages]

    if verbose:
        for lbl, val, exc in stages:
            exc_str = f" ({exc})" if exc else ""
            print(f"  {lbl.replace(chr(10), ' ')}: {val}{exc_str}")

    n = len(stages)
    fig, ax = plt.subplots(figsize=(10, 5))

    max_val = max(values)
    y_positions = list(range(n - 1, -1, -1))  # bottom to top

    # Color gradient from teal_tint (widest) to teal_dark (narrowest)
    stage_colors = [
        PALETTE["teal_tint"],
        PALETTE["teal_tint"],
        PALETTE["teal"],
        PALETTE["teal"],
        PALETTE["teal_dark"],
    ]

    for i, (label, value, exc) in enumerate(stages):
        y = y_positions[i]
        bar_width = value / max_val * 0.85  # normalized width
        ax.barh(
            y, bar_width, height=0.65,
            left=(1 - bar_width) / 2,  # center the bar
            color=stage_colors[i],
            edgecolor=PALETTE["charcoal"],
            linewidth=0.8,
        )
        # Value label inside bar
        text_color = _text_color_for_bg(stage_colors[i])
        ax.text(
            0.5, y, f"{value}",
            ha="center", va="center",
            fontsize=14, fontweight="bold",
            color=text_color,
        )
        # Stage label on the left
        ax.text(
            -0.02, y, label,
            ha="right", va="center",
            fontsize=9, color=PALETTE["charcoal"],
        )
        # Exclusion reason on the right
        if exc:
            ax.text(
                1.02, y, exc,
                ha="left", va="center",
                fontsize=8, color=PALETTE["rose_dark"],
                fontstyle="italic",
            )

    # Draw connecting arrows between stages
    for i in range(n - 1):
        y_from = y_positions[i]
        y_to = y_positions[i + 1]
        ax.annotate(
            "", xy=(0.5, y_to + 0.35), xytext=(0.5, y_from - 0.35),
            arrowprops=dict(
                arrowstyle="-|>", color=PALETTE["slate"],
                lw=1.2, shrinkA=0, shrinkB=0,
            ),
        )

    ax.set_xlim(-0.45, 1.45)
    ax.set_ylim(-0.6, n - 0.4)
    ax.axis("off")
    ax.set_title(
        "HeCBench Kernel Selection Pipeline",
        fontsize=12, fontweight="bold", pad=12,
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, "f4_selection_funnel", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F5: Kernel x Model Heatmap (dual-panel: cuda-to-omp + omp-to-cuda)
# ---------------------------------------------------------------------------


def _draw_heatmap_panel(
    ax: plt.Axes,
    kernels: list[str],
    models: list[str],
    lookup: dict[tuple[str, str], str],
    title: str,
    show_y_labels: bool = True,
) -> set[str]:
    """Draw a single heatmap panel. Returns set of statuses present."""
    n_k = len(kernels)
    n_m = len(models)
    status_to_idx = {s: i for i, s in enumerate(STATUS_ORDER)}
    na_idx = len(STATUS_ORDER)

    matrix = np.full((n_k, n_m), na_idx, dtype=int)
    present: set[str] = set()

    for i, kernel in enumerate(kernels):
        for j, model in enumerate(models):
            status = lookup.get((kernel, model))
            if status and status in status_to_idx:
                matrix[i, j] = status_to_idx[status]
                present.add(status)

    # Build colormap including N/A
    colors = [STATUS_COLORS[s] for s in STATUS_ORDER] + [NA_COLOR]
    cmap = mcolors.ListedColormap(colors)
    bounds = list(range(len(colors) + 1))
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    # Annotate cells
    for i, kernel in enumerate(kernels):
        for j, model in enumerate(models):
            status = lookup.get((kernel, model))
            if status and status in STATUS_ABBREV:
                abbrev = STATUS_ABBREV[status]
                bg = STATUS_COLORS.get(status, "#FFFFFF")
                ax.text(
                    j, i, abbrev,
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color=_text_color_for_bg(bg),
                )
            elif not status:
                ax.text(
                    j, i, "\u2014",  # em dash for N/A
                    ha="center", va="center",
                    fontsize=8, color="#999999",
                )

    # Axis labels
    ax.set_xticks(range(n_m))
    ax.set_xticklabels(
        [MODEL_DISPLAY.get(m, m) for m in models],
        rotation=0, ha="center", fontsize=8,
    )
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    if show_y_labels:
        ax.set_yticks(range(n_k))
        ax.set_yticklabels(kernels, fontsize=9)
    else:
        ax.set_yticks(range(n_k))
        ax.set_yticklabels([""] * n_k)

    # Grid lines
    for i in range(n_k + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1)
    for j in range(n_m + 1):
        ax.axvline(j - 0.5, color="white", linewidth=1)

    ax.set_title(title, fontsize=11, pad=45, fontweight="bold")
    return present


def generate_f5_heatmap(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F5: Triple-panel kernel heatmap (cuda-to-omp + omp-to-cuda + cuda-to-opencl)."""
    c2o_kernels, c2o_models, c2o_lookup = build_kernel_model_matrix(
        records, level=0, suite="rodinia", direction="cuda-to-omp",
    )
    o2c_kernels, o2c_models, o2c_lookup = build_kernel_model_matrix(
        records, level=0, suite="rodinia", direction="omp-to-cuda",
    )
    c2ocl_kernels, c2ocl_models, c2ocl_lookup = build_kernel_model_matrix(
        records, level=0, suite="rodinia", direction="cuda-to-opencl",
    )

    if verbose:
        print(f"  cuda-to-omp: {len(c2o_kernels)} kernels x {len(c2o_models)} models")
        print(f"  omp-to-cuda: {len(o2c_kernels)} kernels x {len(o2c_models)} models")
        print(f"  cuda-to-opencl: {len(c2ocl_kernels)} kernels x {len(c2ocl_models)} models")

    # Unified kernel list for c2o + o2c (same kernels)
    all_kernels_main = sorted(set(c2o_kernels) | set(o2c_kernels))
    kernel_pass = defaultdict(int)
    for k in all_kernels_main:
        for m in c2o_models:
            if c2o_lookup.get((k, m)) == "PASS":
                kernel_pass[k] += 1
        for m in o2c_models:
            if o2c_lookup.get((k, m)) == "PASS":
                kernel_pass[k] += 1
    kernels_main = sorted(all_kernels_main, key=lambda k: (-kernel_pass[k], k))

    # c2ocl kernels sorted by PASS count
    c2ocl_pass = defaultdict(int)
    for k in c2ocl_kernels:
        for m in c2ocl_models:
            if c2ocl_lookup.get((k, m)) == "PASS":
                c2ocl_pass[k] += 1
    kernels_ocl = sorted(c2ocl_kernels, key=lambda k: (-c2ocl_pass[k], k))

    n_c2o = max(len(c2o_models), 1)
    n_o2c = max(len(o2c_models), 1)
    n_c2ocl = max(len(c2ocl_models), 1)

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(8, 9),
        gridspec_kw={"width_ratios": [n_c2o, n_o2c, n_c2ocl], "wspace": 0.4},
    )

    present1 = _draw_heatmap_panel(
        ax1, kernels_main, c2o_models, c2o_lookup,
        f"CUDA \u2192 OMP (L0)\n{len(c2o_kernels)} kernels", show_y_labels=True,
    )
    present2 = _draw_heatmap_panel(
        ax2, kernels_main, o2c_models, o2c_lookup,
        f"OMP \u2192 CUDA (L0)\n{len(o2c_kernels)} kernels", show_y_labels=False,
    )
    present3 = _draw_heatmap_panel(
        ax3, kernels_ocl, c2ocl_models, c2ocl_lookup,
        f"CUDA \u2192 OpenCL (L0)\n{len(c2ocl_kernels)} kernels", show_y_labels=True,
    )

    # Shared legend at bottom
    all_present = sorted(
        present1 | present2 | present3,
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = [
        Patch(
            facecolor=STATUS_COLORS[s], edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in all_present
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.02),
        ncol=len(legend_handles), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f5_kernel_model_heatmap", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F6: Failure Taxonomy (dual-direction stacked bar)
# ---------------------------------------------------------------------------


def _draw_taxonomy_panel(
    ax: plt.Axes,
    records: list[dict],
    models: list[str],
    title: str,
) -> None:
    """Draw a stacked bar panel for failure taxonomy."""
    n_models = len(models)
    x = np.arange(n_models)
    bar_width = 0.6

    # Build per-model status counts
    model_status: dict[str, dict[str, int]] = {}
    for r in records:
        m = r["model"]
        if m not in models:
            continue
        if m not in model_status:
            model_status[m] = defaultdict(int)
        status = r.get("overall_status", "UNKNOWN")
        model_status[m][status] += 1

    bottoms = np.zeros(n_models)
    for status in STATUS_ORDER:
        counts = np.array([
            model_status.get(m, {}).get(status, 0) for m in models
        ], dtype=float)
        ax.bar(
            x, counts, bar_width,
            bottom=bottoms,
            color=STATUS_COLORS[status],
            hatch=STATUS_HATCH[status],
            edgecolor="black", linewidth=0.5,
            label=status.replace("_", " "),
        )
        for i, (count, bottom) in enumerate(zip(counts, bottoms)):
            if count > 0:
                ax.text(
                    x[i], bottom + count / 2, str(int(count)),
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color=_text_color_for_bg(STATUS_COLORS[status]),
                )
        bottoms += counts

    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_DISPLAY.get(m, m) for m in models], fontsize=8)
    ax.set_ylabel("Number of Tasks")
    ax.set_ylim(0, max(bottoms) * 1.08 if max(bottoms) > 0 else 1)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_title(title, fontsize=10, fontweight="bold")


def generate_f6_taxonomy(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F6: Failure taxonomy — dual-direction stacked bar chart."""
    c2o_records = filter_records(records, level=0, suite="rodinia", direction="cuda-to-omp")
    o2c_records = filter_records(records, level=0, suite="rodinia", direction="omp-to-cuda")

    # Models present in cuda-to-omp (4 models)
    c2o_models_set = sorted({r["model"] for r in c2o_records})
    c2o_models = sorted(
        c2o_models_set,
        key=lambda m: -sum(1 for r in c2o_records if r["model"] == m and r.get("overall_status") == "PASS"),
    )
    # Models present in omp-to-cuda (3 models)
    o2c_models_set = sorted({r["model"] for r in o2c_records})
    o2c_models = sorted(
        o2c_models_set,
        key=lambda m: -sum(1 for r in o2c_records if r["model"] == m and r.get("overall_status") == "PASS"),
    )

    if verbose:
        print(f"  cuda-to-omp: {len(c2o_records)} tasks, {len(c2o_models)} models")
        print(f"  omp-to-cuda: {len(o2c_records)} tasks, {len(o2c_models)} models")

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11, 5),
        gridspec_kw={"width_ratios": [len(c2o_models), len(o2c_models)], "wspace": 0.3},
    )

    n_c2o = len(set(r["kernel"] for r in c2o_records))
    n_o2c = len(set(r["kernel"] for r in o2c_records))
    _draw_taxonomy_panel(ax1, c2o_records, c2o_models, f"CUDA \u2192 OpenMP (L0, {n_c2o} kernels)")
    _draw_taxonomy_panel(ax2, o2c_records, o2c_models, f"OpenMP \u2192 CUDA (L0, {n_o2c} kernels)")

    # Shared legend at top
    # Include all statuses that appear in the data
    all_statuses = set()
    for r in c2o_records + o2c_records:
        s = r.get("overall_status", "UNKNOWN")
        if s in STATUS_COLORS:
            all_statuses.add(s)
    handles = [
        Patch(
            facecolor=STATUS_COLORS[s], hatch=STATUS_HATCH[s],
            edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in STATUS_ORDER
        if s in all_statuses
    ]
    fig.legend(
        handles=handles,
        loc="upper center", bbox_to_anchor=(0.5, 1.04),
        ncol=len(handles), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f6_failure_taxonomy", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F7: Augmentation Robustness Line Chart
# ---------------------------------------------------------------------------


def generate_f7_augmentation(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F7: Augmentation robustness — pass rate vs. augmentation level."""
    levels = [0, 1, 2, 3, 4]
    level_labels = ["L0\n(original)", "L1", "L2", "L3", "L4\n(max)"]

    # Compute from records if available
    c2o_all = [r for r in records if r.get("suite") == "rodinia" and r.get("direction") == "cuda-to-omp"]
    if c2o_all:
        # Derive per-model, per-level pass counts
        model_level_pass: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        model_level_total: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        for r in c2o_all:
            m = r["model"]
            lvl = r.get("augment_level", 0)
            model_level_total[m][lvl] += 1
            if r.get("overall_status") == "PASS":
                model_level_pass[m][lvl] += 1
        aug_data = {}
        for m in model_level_pass:
            aug_data[m] = [model_level_pass[m].get(lvl, 0) for lvl in levels]
        aug_total = max(model_level_total[m].get(0, 0) for m in model_level_total) if model_level_total else AUG_TOTAL
    else:
        aug_data = AUG_ROBUSTNESS
        aug_total = AUG_TOTAL

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for model, pass_counts in aug_data.items():
        if model not in MODEL_LINESTYLE:
            continue
        rates = [c / aug_total * 100 for c in pass_counts]
        marker_ls, ls = MODEL_LINESTYLE[model]
        color = MODEL_COLORS[model]
        label = MODEL_DISPLAY_SHORT.get(model, model)
        ax.plot(
            levels, rates,
            marker_ls,
            color=color,
            linewidth=1.8,
            markersize=7,
            label=label,
        )
        ax.annotate(
            f"{rates[-1]:.0f}%",
            xy=(4, rates[-1]),
            xytext=(4.15, rates[-1]),
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
    ax.axvline(0, color="grey", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    ax.set_title(
        f"Augmentation Robustness: Pass Rate across L0\u2013L4\n"
        f"(Rodinia CUDA\u2192OpenMP, {aug_total} kernels, seed=42)",
        fontsize=10,
    )

    _save_figure(fig, output_dir, "f7_augmentation_robustness", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F8: Cross-Direction Comparison (Rodinia)
# ---------------------------------------------------------------------------


def generate_f8_cross_direction(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F8: Cross-direction comparison — status breakdown per direction."""
    directions = ["cuda-to-omp", "omp-to-cuda", "cuda-to-opencl"]
    dir_labels = ["CUDA \u2192 OMP", "OMP \u2192 CUDA", "CUDA \u2192 OpenCL"]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(directions))
    bar_width = 0.5

    # Compute per-direction status counts from L0 Rodinia records
    dir_status: dict[str, dict[str, int]] = {}
    dir_totals: dict[str, int] = {}
    for d in directions:
        filtered = filter_records(records, level=0, suite="rodinia", direction=d)
        counts: dict[str, int] = defaultdict(int)
        for r in filtered:
            status = r.get("overall_status", "UNKNOWN")
            counts[status] += 1
        dir_status[d] = counts
        dir_totals[d] = len(filtered)

    if verbose:
        for d, lbl in zip(directions, dir_labels):
            print(f"  {lbl}: {dir_totals[d]} tasks, {dir_status[d]}")

    bottoms = np.zeros(len(directions))
    for status in STATUS_ORDER:
        counts = np.array([dir_status[d].get(status, 0) for d in directions], dtype=float)
        if counts.sum() == 0:
            continue
        ax.bar(
            x, counts, bar_width,
            bottom=bottoms,
            color=STATUS_COLORS[status],
            hatch=STATUS_HATCH[status],
            edgecolor="black", linewidth=0.5,
            label=status.replace("_", " "),
        )
        for i, (count, bottom) in enumerate(zip(counts, bottoms)):
            if count > 0:
                ax.text(
                    x[i], bottom + count / 2, str(int(count)),
                    ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color=_text_color_for_bg(STATUS_COLORS[status]),
                )
        bottoms += counts

    # Annotate pass rate above each bar
    for i, d in enumerate(directions):
        total = dir_totals[d]
        passed = dir_status[d].get("PASS", 0)
        rate = passed / total * 100 if total else 0
        ax.text(
            x[i], bottoms[i] + 0.5, f"{rate:.0f}%",
            ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=PALETTE["charcoal"],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(dir_labels, fontsize=11)
    ax.set_ylabel("Number of Tasks (L0)")
    max_y = max(bottoms) * 1.15 if max(bottoms) > 0 else 1
    ax.set_ylim(0, max_y)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)

    handles = [
        Patch(
            facecolor=STATUS_COLORS[s], hatch=STATUS_HATCH[s],
            edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in STATUS_ORDER
        if any(dir_status[d].get(s, 0) > 0 for d in directions)
    ]
    ax.legend(handles=handles, loc="upper right", frameon=True, framealpha=0.9, fontsize=9)

    n_kernels_c2o = dir_totals.get("cuda-to-omp", 0)
    n_kernels_o2c = dir_totals.get("omp-to-cuda", 0)
    n_kernels_c2ocl = dir_totals.get("cuda-to-opencl", 0)
    ax.set_title(
        f"Cross-Direction Status Breakdown (L0, Rodinia)\n"
        f"C\u2192O: {n_kernels_c2o} kernels | O\u2192C: {n_kernels_o2c} kernels | C\u2192OCL: {n_kernels_c2ocl} kernels",
        fontsize=10, fontweight="bold",
    )

    _save_figure(fig, output_dir, "f8_cross_direction_comparison", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F9: XSBench Direction x Model Heatmap
# ---------------------------------------------------------------------------


def generate_f9_xsbench(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F9: XSBench 12-direction x 3-model status heatmap (L0)."""
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
    ax.set_xticklabels(
        [_XS_MODEL_DISPLAY[m] for m in models], rotation=20, ha="right",
    )
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    dir_labels = [
        d.replace("-to-", "\u2192").replace("_target", "-Target")
        for d in directions
    ]
    ax.set_yticks(range(len(directions)))
    ax.set_yticklabels(dir_labels)

    for i in range(len(directions) + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1)
    for j in range(len(models) + 1):
        ax.axvline(j - 0.5, color="white", linewidth=1)

    present_statuses = sorted(
        {
            XSBENCH_L0[d][m]
            for d in directions
            for m in models
            if XSBENCH_L0[d].get(m) in STATUS_COLORS
        },
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = [
        Patch(
            facecolor=STATUS_COLORS[s], edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in present_statuses
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.08),
        ncol=len(present_statuses), frameon=False, fontsize=8,
    )
    ax.set_title(
        "XSBench: 12-Direction \u00d7 3-Model Results (L0)",
        fontsize=10, pad=40,
    )

    _save_figure(fig, output_dir, "f9_xsbench_heatmap", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# T2: Model Comparison LaTeX Table
# ---------------------------------------------------------------------------


def generate_t2_latex(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """Generate T2: Model comparison LaTeX table — both directions."""
    lines = [
        r"\begin{tabular}{llrrrrrrr}",
        r"\toprule",
        r"Direction & Model & PASS & Total & Rate (\%) & BUILD\_FAIL & RUN\_FAIL & VERIFY\_FAIL & EXTR\_FAIL \\",
        r"\midrule",
    ]

    for direction, dir_label in [
        ("cuda-to-omp", r"CUDA$\to$OMP"),
        ("omp-to-cuda", r"OMP$\to$CUDA"),
        ("cuda-to-opencl", r"CUDA$\to$OCL"),
    ]:
        filtered = filter_records(records, level=0, suite="rodinia", direction=direction)
        model_stats: dict[str, dict] = {}
        for r in filtered:
            m = r["model"]
            if m not in model_stats:
                model_stats[m] = {"pass": 0, "total": 0, "by_status": defaultdict(int)}
            status = r.get("overall_status", "UNKNOWN")
            model_stats[m]["by_status"][status] += 1
            model_stats[m]["total"] += 1
            if status == "PASS":
                model_stats[m]["pass"] += 1

        models_sorted = sorted(
            model_stats.keys(),
            key=lambda m: -model_stats[m]["pass"] / max(model_stats[m]["total"], 1),
        )
        for i, m in enumerate(models_sorted):
            info = model_stats[m]
            display = MODEL_DISPLAY_SHORT.get(m, m)
            p = info["pass"]
            t = info["total"]
            rate = p / t * 100 if t else 0
            bf = info["by_status"].get("BUILD_FAIL", 0)
            rf = info["by_status"].get("RUN_FAIL", 0)
            vf = info["by_status"].get("VERIFY_FAIL", 0)
            ef = info["by_status"].get("EXTRACTION_FAIL", 0)
            d_label = dir_label if i == 0 else ""
            lines.append(
                f"{d_label} & {display} & {p} & {t} & {rate:.1f} & {bf} & {rf} & {vf} & {ef} \\\\"
            )
        if direction != "cuda-to-opencl":
            lines.append(r"\midrule")

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
        help="Comma-separated figure IDs to generate (default: all). E.g., f1,f2,f3",
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
        requested = {
            "f1", "f2", "f3", "f4",
            "f5", "f6", "f7", "f8",
            "t2",
        }

    # Determine whether eval data is needed (F5-F9, T2)
    eval_figures = {"f5", "f6", "f7", "f8", "f9", "t2"}
    needs_eval = requested & eval_figures

    records: list[dict] = []
    has_eval_data = False
    if needs_eval:
        records = load_individual_results(results_dir)
        summary_path = results_dir / "eval_summary.json"
        if not records or not summary_path.exists():
            print(
                f"WARNING: Eval data not found in {results_dir} — "
                f"skipping figures {sorted(needs_eval)}",
                file=sys.stderr,
            )
            requested -= eval_figures
        else:
            has_eval_data = True
            summary = json.loads(summary_path.read_text())

            c2o_records = filter_records(records, level=0, suite="rodinia", direction="cuda-to-omp")
            o2c_records = filter_records(records, level=0, suite="rodinia", direction="omp-to-cuda")

            print(f"Loaded {len(records)} total results")
            print(f"  L0 Rodinia cuda-to-omp: {len(c2o_records)}")
            print(f"  L0 Rodinia omp-to-cuda: {len(o2c_records)}")

    print(f"Output: {output_dir}")
    print(f"Formats: {formats}")
    print()

    # F1: Architecture diagram (matplotlib fallback — TikZ .tex also provided)
    if "f1" in requested:
        print("Generating F1: System Architecture Diagram...")
        generate_f1_architecture(output_dir, formats, args.verbose)
        print()

    # F2: API co-occurrence heatmap (survey data)
    if "f2" in requested:
        print("Generating F2: API Co-occurrence Heatmap (survey)...")
        generate_f2_api_cooccurrence(project_root, output_dir, formats, args.verbose)
        print()

    # F3: Repository vs kernel-level counts (survey data)
    if "f3" in requested:
        print("Generating F3: Repo vs Kernel-Level Counts...")
        generate_f3_repo_vs_kernel(output_dir, formats, args.verbose)
        print()

    # F4: HeCBench kernel selection funnel (survey data)
    if "f4" in requested:
        print("Generating F4: HeCBench Selection Funnel...")
        generate_f4_selection_funnel(output_dir, formats, args.verbose)
        print()

    # F5: Dual-panel heatmap (cuda-to-omp + omp-to-cuda)
    if "f5" in requested:
        print("Generating F5: Kernel x Model Heatmap (triple-panel)...")
        generate_f5_heatmap(records, output_dir, formats, args.verbose)
        print()

    # F6: Failure taxonomy (dual-direction stacked bars)
    if "f6" in requested:
        print("Generating F6: Failure Taxonomy (dual-direction)...")
        generate_f6_taxonomy(records, output_dir, formats, args.verbose)
        print()

    # F7: Augmentation robustness line chart
    if "f7" in requested:
        print("Generating F7: Augmentation Robustness (L0-L4)...")
        generate_f7_augmentation(records, output_dir, formats, args.verbose)
        print()

    # F8: Cross-direction comparison (Rodinia)
    if "f8" in requested:
        print("Generating F8: Cross-Direction Comparison (Rodinia)...")
        generate_f8_cross_direction(records, output_dir, formats, args.verbose)
        print()

    # F9: XSBench direction x model heatmap
    if "f9" in requested:
        print("Generating F9: XSBench Direction x Model Heatmap (L0)...")
        generate_f9_xsbench(output_dir, formats, args.verbose)
        print()

    # T2: LaTeX table (both directions)
    if "t2" in requested:
        print("Generating T2: Model Comparison LaTeX Table (both directions)...")
        generate_t2_latex(records, output_dir, args.verbose)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
