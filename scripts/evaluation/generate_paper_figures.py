#!/usr/bin/env python3
"""Generate publication-quality figures for the SC26 paper.

Reads eval results from results/evaluation/ and generates figures F1-F6
plus a LaTeX table T2. Designed to be rerun as more data arrives.

Usage:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam

    # Generate only specific figures:
    python3 scripts/evaluation/generate_paper_figures.py \\
      --project-root /home/samyak/Desktop/parbench_sam --figures f1,f2,f3
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
    "claude-sonnet-4-6":            PALETTE["teal"],       # #2E8E9E
    "azure-gpt-4.1":                PALETTE["gold"],       # #E6A84D
    "groq-llama-3.3-70b-versatile": PALETTE["rose"],       # #C8607A
    "gemini-2.5-flash-lite":        PALETTE["saffron"],    # #D48A35
}

# Model → line style for print-safe rendering
MODEL_LINESTYLE: dict[str, tuple[str, str]] = {
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
    "claude-sonnet-4-6": "Claude\nSonnet 4",
    "azure-gpt-4.1": "GPT-4.1",
    "groq-llama-3.3-70b-versatile": "Llama 3.3\n70B",
    "gemini-2.5-flash-lite": "Gemini\nFlash-Lite",
}

MODEL_DISPLAY_SHORT: dict[str, str] = {
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

# Verified S9 Rodinia direction comparison data (L0, 16 shared kernels, 3 models)
# Source: results/evaluation/s9_direction_comparison.txt, verified 2026-03-26
RODINIA_DIRECTION: dict[str, dict[str, int]] = {
    "claude-sonnet-4-6":              {"c2o": 11, "o2c": 7, "total": 16},
    "gemini-2.5-flash-lite":          {"c2o": 4,  "o2c": 1, "total": 16},
    "groq-llama-3.3-70b-versatile":   {"c2o": 5,  "o2c": 3, "total": 16},
}

# S9 failure taxonomy by direction (L0, 16 kernels × 3 models = 48 tasks each)
RODINIA_DIR_TAXONOMY: dict[str, dict[str, int]] = {
    "cuda-to-omp": {"PASS": 20, "BUILD_FAIL": 20, "RUN_FAIL": 6, "EXTRACTION_FAIL": 2},
    "omp-to-cuda": {"PASS": 11, "BUILD_FAIL": 28, "RUN_FAIL": 7, "EXTRACTION_FAIL": 2},
}

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
_XS_MODEL_COLORS = {
    "claude": PALETTE["teal"],
    "gemini": PALETTE["saffron"],
    "groq":   PALETTE["rose"],
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
# F2: Kernel x Model Heatmap (dual-panel: cuda-to-omp + omp-to-cuda)
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


def generate_f2_heatmap(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F2: Dual-panel kernel x model heatmap (cuda-to-omp + omp-to-cuda)."""
    # Build both matrices
    c2o_kernels, c2o_models, c2o_lookup = build_kernel_model_matrix(
        records, level=0, suite="rodinia", direction="cuda-to-omp",
    )
    o2c_kernels, o2c_models, o2c_lookup = build_kernel_model_matrix(
        records, level=0, suite="rodinia", direction="omp-to-cuda",
    )

    if verbose:
        print(f"  cuda-to-omp: {len(c2o_kernels)} kernels x {len(c2o_models)} models")
        print(f"  omp-to-cuda: {len(o2c_kernels)} kernels x {len(o2c_models)} models")

    # Unified kernel list sorted by total PASS count across both panels
    all_kernels = sorted(set(c2o_kernels) | set(o2c_kernels))
    kernel_pass = defaultdict(int)
    for k in all_kernels:
        for m in c2o_models:
            if c2o_lookup.get((k, m)) == "PASS":
                kernel_pass[k] += 1
        for m in o2c_models:
            if o2c_lookup.get((k, m)) == "PASS":
                kernel_pass[k] += 1
    kernels = sorted(all_kernels, key=lambda k: (-kernel_pass[k], k))

    # Create dual-panel figure
    n_c2o = len(c2o_models)
    n_o2c = len(o2c_models)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 9),
        gridspec_kw={"width_ratios": [n_c2o, n_o2c], "wspace": 0.15},
        sharey=True,
    )

    present1 = _draw_heatmap_panel(
        ax1, kernels, c2o_models, c2o_lookup,
        "CUDA \u2192 OpenMP (L0)", show_y_labels=True,
    )
    present2 = _draw_heatmap_panel(
        ax2, kernels, o2c_models, o2c_lookup,
        "OpenMP \u2192 CUDA (L0)", show_y_labels=False,
    )

    # Shared legend at bottom
    all_present = sorted(
        present1 | present2,
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = [
        Patch(
            facecolor=STATUS_COLORS[s], edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in all_present
    ]
    # Add N/A entry if any cells are missing
    has_na = any(
        (k, m) not in o2c_lookup
        for k in kernels
        for m in o2c_models
    )
    if has_na:
        legend_handles.append(
            Patch(facecolor=NA_COLOR, edgecolor="black", linewidth=0.5, label="N/A"),
        )

    fig.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.02),
        ncol=len(legend_handles), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f2_kernel_model_heatmap", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F3: Failure Taxonomy (dual-direction stacked bar)
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


def generate_f3_taxonomy(
    records: list[dict],
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F3: Failure taxonomy — dual-direction stacked bar chart."""
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

    _draw_taxonomy_panel(ax1, c2o_records, c2o_models, "CUDA \u2192 OpenMP (L0, 17 kernels)")
    _draw_taxonomy_panel(ax2, o2c_records, o2c_models, "OpenMP \u2192 CUDA (L0, 16 kernels)")

    # Shared legend at top
    handles = [
        Patch(
            facecolor=STATUS_COLORS[s], hatch=STATUS_HATCH[s],
            edgecolor="black", linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in STATUS_ORDER
        if s != "VERIFY_FAIL"  # Always 0, omit from legend
    ]
    fig.legend(
        handles=handles,
        loc="upper center", bbox_to_anchor=(0.5, 1.04),
        ncol=len(handles), frameon=False, fontsize=9,
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

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for model, pass_counts in AUG_ROBUSTNESS.items():
        rates = [c / AUG_TOTAL * 100 for c in pass_counts]
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
        # Annotate endpoint
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

    # Highlight L0 baseline
    ax.axvline(0, color="grey", linewidth=0.8, linestyle="--", alpha=0.5)

    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    ax.set_title(
        "Augmentation Robustness: Pass Rate across L0\u2013L4\n"
        "(Rodinia CUDA\u2192OpenMP, 17 kernels, seed=42)",
        fontsize=10,
    )

    _save_figure(fig, output_dir, "f4_augmentation_robustness", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F5: Cross-Direction Comparison (Rodinia + XSBench)
# ---------------------------------------------------------------------------


def generate_f5_cross_direction(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F5: Cross-direction comparison — Rodinia asymmetry + XSBench."""
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 8),
        gridspec_kw={"height_ratios": [1, 1.2], "hspace": 0.4},
    )

    # --- Panel A: Rodinia direction asymmetry (3 models + aggregate) ---
    dir_models = list(RODINIA_DIRECTION.keys())
    n = len(dir_models) + 1  # +1 for aggregate
    x = np.arange(n)
    bar_width = 0.32

    c2o_rates = [
        RODINIA_DIRECTION[m]["c2o"] / RODINIA_DIRECTION[m]["total"] * 100
        for m in dir_models
    ]
    o2c_rates = [
        RODINIA_DIRECTION[m]["o2c"] / RODINIA_DIRECTION[m]["total"] * 100
        for m in dir_models
    ]
    # Aggregate
    agg_c2o = sum(RODINIA_DIRECTION[m]["c2o"] for m in dir_models)
    agg_o2c = sum(RODINIA_DIRECTION[m]["o2c"] for m in dir_models)
    agg_total = sum(RODINIA_DIRECTION[m]["total"] for m in dir_models)
    c2o_rates.append(agg_c2o / agg_total * 100)
    o2c_rates.append(agg_o2c / agg_total * 100)

    labels = [MODEL_DISPLAY_SHORT.get(m, m) for m in dir_models] + ["Aggregate"]

    bars_c2o = ax1.bar(
        x - bar_width / 2, c2o_rates, bar_width,
        color=PALETTE["teal"], edgecolor="black", linewidth=0.5,
        label="CUDA \u2192 OpenMP",
    )
    bars_o2c = ax1.bar(
        x + bar_width / 2, o2c_rates, bar_width,
        color=PALETTE["rose"], edgecolor="black", linewidth=0.5,
        label="OpenMP \u2192 CUDA",
    )

    # Annotate bars with values and gap
    for i in range(n):
        ax1.text(
            x[i] - bar_width / 2, c2o_rates[i] + 1.5,
            f"{c2o_rates[i]:.1f}%", ha="center", va="bottom",
            fontsize=7, fontweight="bold", color=PALETTE["teal_dark"],
        )
        ax1.text(
            x[i] + bar_width / 2, o2c_rates[i] + 1.5,
            f"{o2c_rates[i]:.1f}%", ha="center", va="bottom",
            fontsize=7, fontweight="bold", color=PALETTE["rose_dark"],
        )
        gap = c2o_rates[i] - o2c_rates[i]
        if gap > 0:
            mid_y = max(c2o_rates[i], o2c_rates[i]) + 8
            ax1.text(
                x[i], mid_y, f"+{gap:.1f}pp",
                ha="center", va="bottom",
                fontsize=7, color=PALETTE["charcoal"],
                fontstyle="italic",
            )

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylabel("Pass Rate (%)")
    ax1.set_ylim(0, 90)
    ax1.yaxis.set_major_locator(plt.MultipleLocator(10))
    ax1.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    ax1.set_title(
        "Rodinia Direction Asymmetry (L0, 16 shared kernels, 3 models)\n"
        "CUDA\u2192OMP is consistently easier than OMP\u2192CUDA (+18.8pp aggregate)",
        fontsize=10, fontweight="bold",
    )
    # Vertical separator before aggregate
    ax1.axvline(x[-1] - 0.5, color=PALETTE["slate"], linewidth=0.8,
                linestyle="--", alpha=0.4)

    # --- Panel B: XSBench cross-direction bar chart ---
    directions = list(XSBENCH_L0.keys())
    n_dirs = len(directions)
    n_models = len(_XS_MODELS)
    xs_bar_width = 0.22
    x2 = np.arange(n_dirs)

    for i, model in enumerate(_XS_MODELS):
        is_pass = np.array([
            1 if XSBENCH_L0[d][model] == "PASS" else 0
            for d in directions
        ], dtype=float)
        offset = (i - n_models / 2 + 0.5) * xs_bar_width
        ax2.bar(
            x2 + offset, is_pass, xs_bar_width,
            color=_XS_MODEL_COLORS[model],
            edgecolor="black", linewidth=0.5,
            label=_XS_MODEL_DISPLAY[model],
        )
        for j, (d, v) in enumerate(zip(directions, is_pass)):
            if v == 0:
                status = XSBENCH_L0[d][model]
                abbrev = STATUS_ABBREV.get(status, "?")
                ax2.text(
                    x2[j] + offset, 0.02, abbrev,
                    ha="center", va="bottom",
                    fontsize=5, color="#555555", rotation=90,
                )

    ax2.set_xticks(x2)
    dir_labels = [d.replace("-to-", "\u2192").replace("_target", "-T") for d in directions]
    ax2.set_xticklabels(dir_labels, rotation=35, ha="right", fontsize=7)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["FAIL", "PASS"])
    ax2.set_ylabel("Result")
    ax2.set_ylim(-0.1, 1.3)
    ax2.set_title(
        "XSBench Cross-Direction Results (L0, 12 directions, 3 models)\n"
        "Claude: 10/12 PASS  |  Gemini: 0/12 PASS  |  Llama: 1/12 PASS",
        fontsize=10, fontweight="bold",
    )
    ax2.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=8)
    ax2.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)

    _save_figure(fig, output_dir, "f5_cross_direction_comparison", formats)
    plt.close(fig)


# ---------------------------------------------------------------------------
# F6: XSBench Direction x Model Heatmap
# ---------------------------------------------------------------------------


def generate_f6_xsbench(
    output_dir: Path,
    formats: list[str],
    verbose: bool,
) -> None:
    """Generate F6: XSBench 12-direction x 3-model status heatmap (L0)."""
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

    _save_figure(fig, output_dir, "f6_xsbench_heatmap", formats)
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
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Direction & Model & PASS & Total & Rate (\%) & BUILD\_FAIL & RUN\_FAIL & EXTR\_FAIL \\",
        r"\midrule",
    ]

    for direction, dir_label in [
        ("cuda-to-omp", r"CUDA$\to$OMP"),
        ("omp-to-cuda", r"OMP$\to$CUDA"),
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
            ef = info["by_status"].get("EXTRACTION_FAIL", 0)
            d_label = dir_label if i == 0 else ""
            lines.append(
                f"{d_label} & {display} & {p} & {t} & {rate:.1f} & {bf} & {rf} & {ef} \\\\"
            )
        if direction == "cuda-to-omp":
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
        requested = {"f1", "f2", "f3", "f4", "f5", "f6", "t2"}

    # Load data
    records = load_individual_results(results_dir)
    if not records:
        print("ERROR: No result files found in", results_dir, file=sys.stderr)
        sys.exit(1)
    summary = load_eval_summary(results_dir)

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

    # F2: Dual-panel heatmap (cuda-to-omp + omp-to-cuda)
    if "f2" in requested:
        print("Generating F2: Kernel x Model Heatmap (dual-panel)...")
        generate_f2_heatmap(records, output_dir, formats, args.verbose)
        print()

    # F3: Failure taxonomy (dual-direction stacked bars)
    if "f3" in requested:
        print("Generating F3: Failure Taxonomy (dual-direction)...")
        generate_f3_taxonomy(records, output_dir, formats, args.verbose)
        print()

    # F4: Augmentation robustness line chart
    if "f4" in requested:
        print("Generating F4: Augmentation Robustness (3 models, L0-L4)...")
        generate_f4_augmentation(output_dir, formats, args.verbose)
        print()

    # F5: Cross-direction comparison (Rodinia + XSBench)
    if "f5" in requested:
        print("Generating F5: Cross-Direction Comparison (Rodinia + XSBench)...")
        generate_f5_cross_direction(output_dir, formats, args.verbose)
        print()

    # F6: XSBench direction x model heatmap
    if "f6" in requested:
        print("Generating F6: XSBench Direction x Model Heatmap (L0)...")
        generate_f6_xsbench(output_dir, formats, args.verbose)
        print()

    # T2: LaTeX table (both directions)
    if "t2" in requested:
        print("Generating T2: Model Comparison LaTeX Table (both directions)...")
        generate_t2_latex(records, output_dir, args.verbose)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
