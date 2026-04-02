#!/usr/bin/env python3
"""Generate all publication-quality figures for the SC26 paper.

Unified script combining main-body figures (F2--F7), appendix figures
(C.1--C.4), and the LaTeX model-comparison table (T2).

Usage:
    python3 scripts/generate_paper_figures.py \
      --project-root /home/samyak/Desktop/parbench_sam \
      --figure all \
      --output-dir docs/paper/figures

    # Single figure:
    python3 scripts/generate_paper_figures.py \
      --project-root /home/samyak/Desktop/parbench_sam \
      --figure F3 \
      --output-dir docs/paper/figures
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.colors as mcolors  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import numpy as np  # noqa: E402
import scienceplots  # noqa: E402, F401

plt.style.use(["science", "ieee", "no-latex"])

# ---------------------------------------------------------------------------
# Okabe-Ito Colorblind-Safe Palette (Okabe & Ito, 2008)
# ---------------------------------------------------------------------------
OKABE_ITO = {
    "orange":     "#E69F00",
    "sky_blue":   "#56B4E9",
    "green":      "#009E73",
    "yellow":     "#F0E442",
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "purple":     "#CC79A7",
    "black":      "#000000",
}

STATUS_COLORS: dict[str, str] = {
    "PASS":            "#009E73",
    "BUILD_FAIL":      "#D55E00",
    "RUN_FAIL":        "#E69F00",
    "VERIFY_FAIL":     "#0072B2",
    "EXTRACTION_FAIL": "#CC79A7",
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

STATUS_ORDER: list[str] = [
    "PASS", "BUILD_FAIL", "RUN_FAIL", "EXTRACTION_FAIL", "VERIFY_FAIL",
]

MODEL_COLORS: dict[str, str] = {
    "together-qwen-3.5-397b-a17b":  OKABE_ITO["orange"],
    "claude-sonnet-4-6":            OKABE_ITO["blue"],
    "groq-llama-3.3-70b-versatile": OKABE_ITO["vermillion"],
    "gemini-2.5-flash-lite":        OKABE_ITO["purple"],
}

MODEL_DISPLAY: dict[str, str] = {
    "together-qwen-3.5-397b-a17b": "Qwen 3.5\n397B",
    "claude-sonnet-4-6":            "Claude\nSonnet 4",
    "groq-llama-3.3-70b-versatile": "Llama 3.3\n70B",
    "gemini-2.5-flash-lite":        "Gemini 2.5\nFlash-Lite",
}

MODEL_DISPLAY_SHORT: dict[str, str] = {
    "together-qwen-3.5-397b-a17b":  "Qwen 3.5 397B-A17B",
    "claude-sonnet-4-6":            "Claude Sonnet 4",
    "groq-llama-3.3-70b-versatile": "Llama 3.3 70B",
    "gemini-2.5-flash-lite":        "Gemini 2.5 Flash-Lite",
}

MODEL_LINESTYLE: dict[str, tuple[str, str]] = {
    "together-qwen-3.5-397b-a17b":  ("D-.", "dashdot"),
    "claude-sonnet-4-6":            ("o-", "solid"),
    "gemini-2.5-flash-lite":        ("s--", "dashed"),
    "groq-llama-3.3-70b-versatile": ("^:", "dotted"),
}

# Legacy palette references for survey figures (F2, C.4)
PALETTE = {
    "rose":         OKABE_ITO["vermillion"],
    "rose_tint":    "#F5D5C8",
    "rose_dark":    "#A34A00",
    "saffron":      OKABE_ITO["orange"],
    "saffron_tint": "#FBF0DD",
    "saffron_dark": "#B37D00",
    "teal":         OKABE_ITO["blue"],
    "teal_tint":    "#C8E0F0",
    "teal_dark":    "#004A75",
    "gold":         OKABE_ITO["yellow"],
    "gold_tint":    "#FDF5E3",
    "gold_dark":    "#B5A23B",
    "charcoal":     OKABE_ITO["black"],
    "slate":        "#636e72",
    "linen":        "#F5F0EB",
}

NA_COLOR = "#E0E0E0"
FIGURE_DPI: int = 600
FONT_SIZE_DEFAULT: int = 10
PDF_FONTTYPE: int = 42

# Canonical 6 directions for multi-direction figures
DIRECTIONS = [
    "cuda-to-omp", "omp-to-cuda",
    "cuda-to-opencl", "opencl-to-cuda",
    "omp-to-opencl", "opencl-to-omp",
]

DIRECTION_LABELS = {
    "cuda-to-omp": "CUDA\u2192OMP",
    "omp-to-cuda": "OMP\u2192CUDA",
    "cuda-to-opencl": "CUDA\u2192OCL",
    "opencl-to-cuda": "OCL\u2192CUDA",
    "omp-to-opencl": "OMP\u2192OCL",
    "opencl-to-omp": "OCL\u2192OMP",
}

SUITE_ORDER = ["rodinia", "xsbench", "hecbench"]

# F2: Repository-level vs kernel-level API pair counts (survey data)
REPO_KERNEL_PAIRS: list[tuple[str, int, int]] = [
    ("CUDA\u2013OpenMP", 6, 472),
    ("CUDA\u2013HIP", 3, 633),
    ("CUDA\u2013SYCL", 2, 616),
]

# C.4: HeCBench kernel selection pipeline funnel stages (survey data)
HECBENCH_FUNNEL_STAGES: list[tuple[str, int, str | None]] = [
    ("HeCBench kernels total", 506, None),
    ("All 4 API variants\n(CUDA, HIP, SYCL, OMP)", 327, "\u2212179: missing API variants"),
    ("With Makefiles", 325, "\u22122: no Makefile"),
    ("With self-checking\n(PASS/FAIL/verify patterns)", 242, "\u221283: no verification"),
    ("Final selected\n(complexity, deps, diversity)", 60, "\u2212182: complexity/deps/diversity"),
]

# Verified augmentation robustness data (fallback when no result files)
AUG_ROBUSTNESS: dict[str, list[int]] = {
    "claude-sonnet-4-6":              [12, 12, 12, 12, 12],
    "gemini-2.5-flash-lite":          [4,  4,  4,  3,  1],
    "groq-llama-3.3-70b-versatile":   [5,  6,  6,  4,  4],
}
AUG_TOTAL = 17

# Verified XSBench L0 cross-direction data (fallback)
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


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def setup_rcparams() -> None:
    """Configure matplotlib for publication-quality output (IEEE SC26)."""
    plt.rcParams.update({
        "font.size": FONT_SIZE_DEFAULT,
        "axes.titlesize": 11,
        "axes.labelsize": FONT_SIZE_DEFAULT,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": FIGURE_DPI,
        "savefig.dpi": FIGURE_DPI,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
        "pdf.fonttype": PDF_FONTTYPE,
        "ps.fonttype": PDF_FONTTYPE,
    })


def _text_color_for_bg(hex_color: str) -> str:
    """Return 'white' or 'black' for readable text on the given background."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 145 else "black"


def _save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    """Save figure as both PNG (300 DPI) and vector PDF."""
    for fmt in ("png", "pdf"):
        path = output_dir / f"{stem}.{fmt}"
        fig.savefig(path, format=fmt, dpi=300 if fmt == "png" else None)
        print(f"  Saved: {path}")


def aggregate_status_counts(
    records: list[dict], group_key: str,
) -> dict[str, dict[str, int]]:
    """Aggregate overall_status counts grouped by a record key."""
    result: dict[str, dict[str, int]] = {}
    for r in records:
        key = r.get(group_key, "UNKNOWN")
        if key not in result:
            result[key] = defaultdict(int)
        status = r.get("overall_status") or "UNKNOWN"
        result[key][status] += 1
    return result


def create_status_legend(
    statuses: list[str], *, include_hatch: bool = False,
) -> list[Patch]:
    """Create matplotlib Patch handles for a status legend."""
    patches = []
    for s in statuses:
        if s not in STATUS_COLORS:
            continue
        kwargs: dict = {
            "facecolor": STATUS_COLORS[s],
            "edgecolor": "black",
            "linewidth": 0.5,
            "label": s.replace("_", " "),
        }
        if include_hatch:
            kwargs["hatch"] = STATUS_HATCH[s]
        patches.append(Patch(**kwargs))
    return patches


def _extract_api(spec_name: str) -> str:
    """Extract API suffix from a spec name like 'rodinia-bfs-cuda' -> 'cuda'."""
    if spec_name.endswith("-omp_target"):
        return "omp_target"
    parts = spec_name.rsplit("-", 1)
    return parts[1] if len(parts) == 2 else "unknown"


def _extract_suite(spec_name: str) -> str:
    """Extract suite prefix from a spec name."""
    for prefix in ("rodinia", "xsbench", "hecbench", "rsbench", "mixbench"):
        if spec_name.startswith(prefix + "-"):
            return prefix
    return "other"


def _classify_initial_status(attempt: dict) -> str:
    """Classify the initial failure status from an attempt record."""
    if attempt.get("extraction_fail"):
        return "EXTRACTION_FAIL"
    bs = attempt.get("build_status", "")
    if bs and bs.lower() == "fail":
        return "BUILD_FAIL"
    rs = attempt.get("run_status")
    if rs is not None and str(rs).lower() not in ("pass", "none", ""):
        return "RUN_FAIL"
    vs = attempt.get("verify_status")
    if vs is not None and str(vs).lower() not in ("pass", "none", ""):
        return "VERIFY_FAIL"
    if bs and bs.lower() == "pass":
        return "PASS"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_eval_results(
    project_root: Path, file_filter: str | None = None,
) -> list[dict]:
    """Load all per-task result JSONs from results/evaluation/{model}/*.json.

    Adds ``is_sample`` field to every record based on filename pattern
    (the ``-sN`` suffix), NOT the ``sample_id`` JSON field.

    Args:
        project_root: Project root path.
        file_filter: One of 'samples', 'augmented', 'base', or None (all).
    """
    results_dir = project_root / "results" / "evaluation"
    records: list[dict] = []
    if not results_dir.exists():
        return records

    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model = model_dir.name

        for result_file in sorted(model_dir.glob("*.json")):
            stem = result_file.stem

            # Determine is_sample from filename pattern, NOT sample_id field
            is_sample = bool(re.search(r"-s\d+", stem))
            is_augmented = bool(re.search(r"-L\d+$", stem))
            is_base = not is_sample and not is_augmented

            if file_filter == "samples" and not is_sample:
                continue
            if file_filter == "augmented" and not is_augmented:
                continue
            if file_filter == "base" and not is_base:
                continue

            try:
                data = json.loads(result_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            source_spec = data.get("source_spec", "")
            target_spec = data.get("target_spec", "")
            if not source_spec or not target_spec:
                continue

            # Augment level from filename
            m_lvl = re.search(r"-L([1-4])$", stem)
            augment_level = int(m_lvl.group(1)) if m_lvl else 0

            src_api = _extract_api(source_spec)
            tgt_api = _extract_api(target_spec)

            kernel = data.get("kernel", "")
            if not kernel:
                parts = source_spec.split("-")
                kernel = "-".join(parts[1:-1]) if len(parts) >= 3 else source_spec

            records.append({
                "kernel": kernel,
                "suite": _extract_suite(source_spec),
                "direction": f"{src_api}-to-{tgt_api}",
                "model": data.get("model", model),
                "overall_status": data.get("overall_status", "UNKNOWN"),
                "sample_id": data.get("sample_id"),
                "augment_level": augment_level,
                "total_attempts": data.get("total_attempts", 1),
                "attempts": data.get("attempts", []),
                "source_spec": source_spec,
                "target_spec": target_spec,
                "is_sample": is_sample,
            })

    return records


def load_augmentation_eval_results(project_root: Path) -> list[dict]:
    """Load augmentation eval_*.json files (contain transform data)."""
    aug_dir = project_root / "results" / "augmentation"
    records = []
    for api in ("cuda", "omp", "opencl"):
        fpath = aug_dir / f"eval_{api}.json"
        if not fpath.exists():
            continue
        data = json.loads(fpath.read_text())
        for entry in data:
            entry["api"] = api
            records.append(entry)
    return records


def filter_records(
    records: list[dict],
    level: int = 0,
    suite: str | None = None,
    direction: str | None = None,
    *,
    samples_only: bool = False,
) -> list[dict]:
    """Filter result records by augmentation level, suite, direction, and sample flag."""
    out = [r for r in records if r.get("augment_level", 0) == level]
    if suite:
        out = [r for r in out if r.get("suite", "") == suite]
    if direction:
        out = [r for r in out if r.get("direction", "") == direction]
    if samples_only:
        out = [r for r in out if r.get("is_sample", False)]
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


# ===================================================================
# F2: Repository-Level vs Kernel-Level Counts (survey data)
# ===================================================================


def generate_f2_repo_vs_kernel(
    output_dir: Path, verbose: bool,
) -> None:
    """F2: Grouped bar chart comparing repo-level vs kernel-level counts."""
    pairs = REPO_KERNEL_PAIRS
    labels = [p[0] for p in pairs]
    repo_counts = np.array([p[1] for p in pairs], dtype=float)
    kernel_counts = np.array([p[2] for p in pairs], dtype=float)
    multipliers = [f"{int(k / r)}x" for r, k in zip(repo_counts, kernel_counts)]

    if verbose:
        for lbl, r, k, m in zip(labels, repo_counts, kernel_counts, multipliers):
            print(f"  {lbl}: {int(r)} repos -> {int(k)} kernels ({m})")

    x = np.arange(len(labels))
    bar_width = 0.32

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    ax.bar(
        x - bar_width / 2, repo_counts, bar_width,
        color=PALETTE["teal_tint"], edgecolor=PALETTE["teal"],
        linewidth=1.2, hatch="///", label="Repository Count",
    )
    ax.bar(
        x + bar_width / 2, kernel_counts, bar_width,
        color=PALETTE["teal"], edgecolor=PALETTE["teal_dark"],
        linewidth=1.2, hatch="\\\\", label="Kernel Count",
    )

    ax.set_yscale("log")
    ax.set_ylim(5, 2500)

    for i, (r, k) in enumerate(zip(repo_counts, kernel_counts)):
        ax.text(
            x[i] - bar_width / 2, r * 1.15, str(int(r)),
            ha="center", va="bottom", fontsize=8, fontweight="bold",
            color=PALETTE["teal_dark"],
        )
        ax.text(
            x[i] + bar_width / 2, k * 1.15, str(int(k)),
            ha="center", va="bottom", fontsize=8, fontweight="bold",
            color=PALETTE["charcoal"],
        )

    for i, mult in enumerate(multipliers):
        max_val = max(repo_counts[i], kernel_counts[i])
        ax.text(
            x[i], max_val * 2.2, mult,
            ha="center", va="bottom", fontsize=10, fontweight="bold",
            color=PALETTE["rose"],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Count (log scale)")
    ax.legend(loc="lower right", frameon=True, framealpha=0.9, fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.3, linewidth=0.6)
    ax.set_title(
        "Repo vs. Kernel Translation Pair Counts",
        fontsize=9, fontweight="bold", pad=8,
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, "f2_repo_vs_kernel")
    plt.close(fig)


# ===================================================================
# F3: Kernel x Model Heatmap (triple-panel)
# ===================================================================


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

    colors = [STATUS_COLORS[s] for s in STATUS_ORDER] + [NA_COLOR]
    cmap = mcolors.ListedColormap(colors)
    bounds = list(range(len(colors) + 1))
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    for i, kernel in enumerate(kernels):
        for j, model in enumerate(models):
            status = lookup.get((kernel, model))
            if status and status in STATUS_ABBREV:
                bg = STATUS_COLORS.get(status, "#FFFFFF")
                ax.text(
                    j, i, STATUS_ABBREV[status],
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color=_text_color_for_bg(bg),
                )
            elif not status:
                ax.text(
                    j, i, "\u2014",
                    ha="center", va="center",
                    fontsize=8, color="#999999",
                )

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

    for i in range(n_k + 1):
        ax.axhline(i - 0.5, color="white", linewidth=1)
    for j in range(n_m + 1):
        ax.axvline(j - 0.5, color="white", linewidth=1)

    ax.set_title(title, fontsize=11, pad=45, fontweight="bold")
    return present


def generate_f3_kernel_heatmap(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """F3: Triple-panel kernel x model heatmap (cuda-to-omp + omp-to-cuda + cuda-to-opencl).

    IMPORTANT: Uses only non-sample, non-augmented (L0 base) records.
    """
    # Filter to base records only (not samples)
    base_records = [r for r in records if not r.get("is_sample", False)]

    c2o_kernels, c2o_models, c2o_lookup = build_kernel_model_matrix(
        base_records, level=0, suite="rodinia", direction="cuda-to-omp",
    )
    o2c_kernels, o2c_models, o2c_lookup = build_kernel_model_matrix(
        base_records, level=0, suite="rodinia", direction="omp-to-cuda",
    )
    c2ocl_kernels, c2ocl_models, c2ocl_lookup = build_kernel_model_matrix(
        base_records, level=0, suite="rodinia", direction="cuda-to-opencl",
    )

    if verbose:
        print(f"  cuda-to-omp: {len(c2o_kernels)} kernels x {len(c2o_models)} models")
        print(f"  omp-to-cuda: {len(o2c_kernels)} kernels x {len(o2c_models)} models")
        print(f"  cuda-to-opencl: {len(c2ocl_kernels)} kernels x {len(c2ocl_models)} models")

    # Unified kernel list for c2o + o2c
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
        1, 3, figsize=(7.16, 3.5),
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

    all_present = sorted(
        present1 | present2 | present3,
        key=lambda s: STATUS_ORDER.index(s),
    )
    legend_handles = create_status_legend(all_present)
    fig.legend(
        handles=legend_handles,
        loc="lower center", bbox_to_anchor=(0.5, -0.02),
        ncol=len(legend_handles), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f3_kernel_model_heatmap")
    plt.close(fig)


# ===================================================================
# F4: Failure Taxonomy (dual-direction stacked bar)
# ===================================================================


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

    filtered = [r for r in records if r["model"] in models]
    model_status = aggregate_status_counts(filtered, "model")

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


def generate_f4_failure_taxonomy(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """F4: Failure taxonomy -- dual-direction stacked bar chart."""
    base_records = [r for r in records if not r.get("is_sample", False)]

    c2o_records = filter_records(base_records, level=0, suite="rodinia", direction="cuda-to-omp")
    o2c_records = filter_records(base_records, level=0, suite="rodinia", direction="omp-to-cuda")

    c2o_models = sorted(
        {r["model"] for r in c2o_records},
        key=lambda m: -sum(1 for r in c2o_records if r["model"] == m and r.get("overall_status") == "PASS"),
    )
    o2c_models = sorted(
        {r["model"] for r in o2c_records},
        key=lambda m: -sum(1 for r in o2c_records if r["model"] == m and r.get("overall_status") == "PASS"),
    )

    if verbose:
        print(f"  cuda-to-omp: {len(c2o_records)} tasks, {len(c2o_models)} models")
        print(f"  omp-to-cuda: {len(o2c_records)} tasks, {len(o2c_models)} models")

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(7.16, 3.0),
        gridspec_kw={"width_ratios": [max(len(c2o_models), 1), max(len(o2c_models), 1)], "wspace": 0.3},
    )

    n_c2o = len(set(r["kernel"] for r in c2o_records))
    n_o2c = len(set(r["kernel"] for r in o2c_records))
    _draw_taxonomy_panel(ax1, c2o_records, c2o_models, f"CUDA \u2192 OpenMP (L0, {n_c2o} kernels)")
    _draw_taxonomy_panel(ax2, o2c_records, o2c_models, f"OpenMP \u2192 CUDA (L0, {n_o2c} kernels)")

    all_statuses = set()
    for r in c2o_records + o2c_records:
        s = r.get("overall_status", "UNKNOWN")
        if s in STATUS_COLORS:
            all_statuses.add(s)
    present_ordered = [s for s in STATUS_ORDER if s in all_statuses]
    handles = create_status_legend(present_ordered, include_hatch=True)
    fig.legend(
        handles=handles,
        loc="upper center", bbox_to_anchor=(0.5, 1.04),
        ncol=len(handles), frameon=False, fontsize=9,
    )

    _save_figure(fig, output_dir, "f4_failure_taxonomy")
    plt.close(fig)


# ===================================================================
# F5: pass@k by Direction (BUG FIX: uses is_sample from filename)
# ===================================================================


def generate_f5_pass_at_k(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """F5: pass@k by translation direction.

    CRITICAL: Filters to true sample files using the ``is_sample`` field
    (determined by filename ``-sN`` pattern), NOT the ``sample_id`` JSON field.
    """
    # Only true sample files in the 6 standard directions
    sample_records = [
        r for r in records
        if r.get("is_sample", False) and r["direction"] in DIRECTIONS
    ]

    if not sample_records:
        print("  WARNING: No sample records for pass@k -- skipping F5.")
        return

    if verbose:
        print(f"  Sample records for pass@k: {len(sample_records)}")

    # Group by (kernel, direction), collect pass/fail per sample
    kernel_dir_samples: dict[tuple[str, str], list[int]] = defaultdict(list)
    for r in sample_records:
        key = (r["kernel"], r["direction"])
        kernel_dir_samples[key].append(1 if r["overall_status"] == "PASS" else 0)

    # Compute pass@k per direction
    dir_pass1: dict[str, list[float]] = defaultdict(list)
    dir_pass3: dict[str, list[float]] = defaultdict(list)

    for (kernel, direction), results in kernel_dir_samples.items():
        n = len(results)
        c = sum(results)

        # pass@1: unbiased estimator = c/n
        p1 = 1 - comb(n - c, 1) / comb(n, 1) if n >= 1 else 0

        # pass@k where k = min(n, 3)
        k = min(n, 3)
        if n >= k and comb(n, k) > 0:
            pk = 1 - comb(n - c, k) / comb(n, k) if comb(n - c, k) <= comb(n, k) else 1.0
        else:
            pk = 1.0 if c > 0 else 0.0

        dir_pass1[direction].append(p1)
        dir_pass3[direction].append(pk)

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    x_dirs = [d for d in DIRECTIONS if d in dir_pass1]
    x_pos = np.arange(len(x_dirs))
    width = 0.35

    avg_pass1 = [np.mean(dir_pass1[d]) for d in x_dirs]
    avg_pass3 = [np.mean(dir_pass3[d]) for d in x_dirs]

    bars1 = ax.bar(x_pos - width / 2, avg_pass1, width,
                   label="pass@1", color=STATUS_COLORS["BUILD_FAIL"],
                   edgecolor="white")
    bars3 = ax.bar(x_pos + width / 2, avg_pass3, width,
                   label="pass@3", color=STATUS_COLORS["VERIFY_FAIL"],
                   edgecolor="white")

    for bars in [bars1, bars3]:
        for bar in bars:
            h = bar.get_height()
            if h > 0.01:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.01,
                        f"{h:.2f}", ha="center", va="bottom",
                        fontsize=8, color=PALETTE["charcoal"])

    ax.set_xticks(x_pos)
    ax.set_xticklabels([DIRECTION_LABELS.get(d, d) for d in x_dirs],
                       fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Average pass@k")
    ax.set_ylim(0, 1.15)
    ax.set_title("pass@k by Translation Direction",
                 fontsize=10, fontweight="bold", pad=8)
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    _save_figure(fig, output_dir, "f5_pass_at_k_by_direction")
    plt.close(fig)


# ===================================================================
# F6: XSBench Cross-Granularity Comparison
# ===================================================================


def generate_f6_xsbench_comparison(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """F6: XSBench ParBench vs ParEval-Repo pass rate comparison."""
    # Filter to xsbench results in standard directions
    xsbench = [r for r in records
                if r["suite"] == "xsbench"
                and r["direction"] in DIRECTIONS]

    if not xsbench:
        print("  WARNING: No XSBench eval results found -- skipping F6.")
        return

    dir_results: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "pass": 0})
    for r in xsbench:
        d = r["direction"]
        dir_results[d]["total"] += 1
        if r["overall_status"] == "PASS":
            dir_results[d]["pass"] += 1

    active_dirs = [d for d in DIRECTIONS if dir_results[d]["total"] > 0]

    if verbose:
        for d in active_dirs:
            s = dir_results[d]
            print(f"  {d}: {s['pass']}/{s['total']}")

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    x_pos = np.arange(len(active_dirs))
    width = 0.35

    pareval_rates = [0.0] * len(active_dirs)
    parbench_rates = [
        dir_results[d]["pass"] / dir_results[d]["total"]
        if dir_results[d]["total"] > 0 else 0
        for d in active_dirs
    ]

    ax.bar(x_pos - width / 2, pareval_rates, width,
           label="ParEval-Repo (0%)", color="#b2bec3", edgecolor="white")
    bars_bench = ax.bar(x_pos + width / 2, parbench_rates, width,
                        label="ParBench (kernel-level)", color=STATUS_COLORS["PASS"],
                        edgecolor="white")

    for bar, d in zip(bars_bench, active_dirs):
        h = bar.get_height()
        s = dir_results[d]
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                f"{s['pass']}/{s['total']}", ha="center", va="bottom",
                fontsize=8, color=PALETTE["charcoal"])

    ax.set_xticks(x_pos)
    ax.set_xticklabels([DIRECTION_LABELS.get(d, d) for d in active_dirs],
                       fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Pass Rate")
    ax.set_ylim(0, 1.2)
    ax.set_title("XSBench: Kernel-Level vs Repository-Level",
                 fontsize=10, fontweight="bold", pad=8)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    _save_figure(fig, output_dir, "f6_xsbench_comparison")
    plt.close(fig)


# ===================================================================
# F7: Augmentation Robustness Line Chart
# ===================================================================


def generate_f7_augmentation(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """F7: Augmentation robustness -- pass rate vs. augmentation level."""
    levels = [0, 1, 2, 3, 4]
    level_labels = ["L0\n(original)", "L1", "L2", "L3", "L4\n(max)"]

    # Compute from records if available
    base_records = [r for r in records if not r.get("is_sample", False)]
    c2o_all = [r for r in base_records
               if r.get("suite") == "rodinia" and r.get("direction") == "cuda-to-omp"]

    if c2o_all:
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
        aug_total = max(
            (model_level_total[m].get(0, 0) for m in model_level_total),
            default=AUG_TOTAL,
        )
    else:
        aug_data = AUG_ROBUSTNESS
        aug_total = AUG_TOTAL

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

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

    _save_figure(fig, output_dir, "f7_augmentation_robustness")
    plt.close(fig)


# ===================================================================
# C.1: Self-Repair Transition Matrix (was c-series C.2a)
# ===================================================================


def generate_c1_repair_transitions(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """C.1: Transition matrix -- initial failure -> final outcome."""
    multi = [r for r in records if r["total_attempts"] > 1 and r["attempts"]]

    if not multi:
        print("  WARNING: No multi-attempt results found -- skipping C.1.")
        return

    initial_statuses = ["BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL"]
    final_statuses = ["PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL"]

    transitions: Counter = Counter()
    for r in multi:
        initial = _classify_initial_status(r["attempts"][0])
        final = r["overall_status"]
        if initial in initial_statuses:
            transitions[(initial, final)] += 1

    if not transitions:
        print("  WARNING: No transitions found -- skipping C.1.")
        return

    active_initial = [s for s in initial_statuses
                      if any(transitions.get((s, f), 0) > 0 for f in final_statuses)]
    active_final = [s for s in final_statuses
                    if any(transitions.get((i, s), 0) > 0 for i in initial_statuses)]

    if not active_initial or not active_final:
        print("  WARNING: Empty transition matrix -- skipping C.1.")
        return

    matrix = np.zeros((len(active_initial), len(active_final)))
    for i, init in enumerate(active_initial):
        for j, fin in enumerate(active_final):
            matrix[i, j] = transitions.get((init, fin), 0)

    if verbose:
        print(f"  Transition matrix: {len(active_initial)} x {len(active_final)}")
        print(f"  Total multi-attempt records: {len(multi)}")

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "yor", ["#FFFDE7", OKABE_ITO["orange"], OKABE_ITO["vermillion"]], N=256,
    )
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(active_final)))
    ax.set_xticklabels([s.replace("_", "\n") for s in active_final], fontsize=8)
    ax.set_yticks(range(len(active_initial)))
    ax.set_yticklabels([s.replace("_", "\n") for s in active_initial], fontsize=8)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = int(matrix[i, j])
            if val > 0:
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if matrix[i, j] > matrix.max() * 0.5 else PALETTE["charcoal"])

    ax.set_xlabel("Final Status", fontsize=9)
    ax.set_ylabel("Initial Status (Attempt 1)", fontsize=9)
    ax.set_title("Self-Repair Transition Matrix", fontsize=10, fontweight="bold", pad=8)
    plt.colorbar(im, ax=ax, label="Count", shrink=0.8)

    fig.tight_layout()
    _save_figure(fig, output_dir, "c1_repair_transition_matrix")
    plt.close(fig)


# ===================================================================
# C.2: Self-Repair Rate by Direction (was c-series C.2b)
# ===================================================================


def generate_c2_repair_rate(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """C.2: Self-repair rate by translation direction."""
    multi = [r for r in records if r["total_attempts"] > 1 and r["attempts"]]

    dir_stats: dict[str, dict] = defaultdict(
        lambda: {"initially_failing": 0, "repaired": 0, "attempts_to_success": []}
    )

    for r in multi:
        d = r["direction"]
        if d not in DIRECTIONS:
            continue
        initial = _classify_initial_status(r["attempts"][0])
        if initial != "PASS":
            dir_stats[d]["initially_failing"] += 1
            if r["overall_status"] == "PASS":
                dir_stats[d]["repaired"] += 1
                dir_stats[d]["attempts_to_success"].append(r["total_attempts"])

    if not dir_stats:
        print("  WARNING: No multi-attempt directional data found -- skipping C.2.")
        return

    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    x_dirs = [d for d in DIRECTIONS if d in dir_stats]
    x_pos = np.arange(len(x_dirs))
    repair_rates = []
    avg_attempts = []

    for d in x_dirs:
        s = dir_stats[d]
        rate = s["repaired"] / s["initially_failing"] if s["initially_failing"] > 0 else 0
        repair_rates.append(rate)
        avg = np.mean(s["attempts_to_success"]) if s["attempts_to_success"] else 0
        avg_attempts.append(avg)

    if verbose:
        for d, rate in zip(x_dirs, repair_rates):
            s = dir_stats[d]
            print(f"  {d}: {s['repaired']}/{s['initially_failing']} = {rate:.1%}")

    bars = ax.bar(x_pos, repair_rates, color=STATUS_COLORS["PASS"],
                  edgecolor="white", linewidth=0.5, width=0.6)

    for i, (bar, avg, d) in enumerate(zip(bars, avg_attempts, x_dirs)):
        s = dir_stats[d]
        label = f"{s['repaired']}/{s['initially_failing']}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                label, ha="center", va="bottom", fontsize=7, color=PALETTE["charcoal"])
        if avg > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                    f"avg {avg:.1f}\nattempts", ha="center", va="center",
                    fontsize=6, color="white", fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels([DIRECTION_LABELS.get(d, d) for d in x_dirs],
                       fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Repair Rate")
    ax.set_ylim(0, 1.15)
    ax.set_title("Self-Repair Rate by Translation Direction",
                 fontsize=10, fontweight="bold", pad=8)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    _save_figure(fig, output_dir, "c2_repair_rate_by_direction")
    plt.close(fig)


# ===================================================================
# C.3: Transform Frequency Heatmap (was c-series C.3)
# ===================================================================


def generate_c3_transform_frequency(
    project_root: Path,
    output_dir: Path,
    verbose: bool,
) -> None:
    """C.3: Heatmap of transform frequency per kernel."""
    aug_records = load_augmentation_eval_results(project_root)

    kernel_transform_counts: dict[str, Counter] = defaultdict(Counter)

    for entry in aug_records:
        spec_id = entry.get("spec_id", "")
        parts = spec_id.split("-")
        suite = _extract_suite(spec_id)
        if suite in ("rodinia", "xsbench", "hecbench", "rsbench", "mixbench"):
            kernel = "-".join(parts[1:-1]) if len(parts) > 2 else parts[-1]
        else:
            kernel = spec_id

        transforms_applied = entry.get("transforms_applied", {})
        for filename, transform_list in transforms_applied.items():
            for transform_name in transform_list:
                kernel_transform_counts[kernel][transform_name] += 1

    if not kernel_transform_counts:
        print("  WARNING: No transform data found -- skipping C.3.")
        return

    all_transforms = sorted(set(
        t for counts in kernel_transform_counts.values() for t in counts
    ))
    if not all_transforms:
        print("  WARNING: No transforms applied in any entry -- skipping C.3.")
        return

    sorted_kernels = sorted(kernel_transform_counts.keys())

    matrix = np.zeros((len(sorted_kernels), len(all_transforms)))
    for i, kernel in enumerate(sorted_kernels):
        for j, transform in enumerate(all_transforms):
            matrix[i, j] = kernel_transform_counts[kernel].get(transform, 0)

    if verbose:
        print(f"  {len(sorted_kernels)} kernels x {len(all_transforms)} transforms")

    fig_height = max(4, len(sorted_kernels) * 0.3 + 2)
    fig, ax = plt.subplots(figsize=(5, fig_height))

    saffron_cmap = mcolors.LinearSegmentedColormap.from_list(
        "white_saffron", ["white", OKABE_ITO["orange"]], N=256,
    )

    im = ax.imshow(matrix, cmap=saffron_cmap, aspect="auto")

    # Abbreviate long transform names
    transform_abbrevs = {
        "ArithmeticTransform": "Arith\nTransform",
        "PointerArithmeticToArrayIndex": "PtrArith\n\u2192ArrIdx",
        "ChangeFunctionNames": "Change\nFuncNames",
        "ChangeNames": "Change\nNames",
        "SwapCondition": "Swap\nCondition",
        "TypedefExpansion": "Typedef\nExpansion",
    }
    x_labels = [transform_abbrevs.get(t, t) for t in all_transforms]

    ax.set_xticks(range(len(all_transforms)))
    ax.set_xticklabels(x_labels, fontsize=7, rotation=45, ha="right")
    ax.set_yticks(range(len(sorted_kernels)))
    ax.set_yticklabels(sorted_kernels, fontsize=7)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] > 0:
                ax.text(j, i, f"{int(matrix[i, j])}", ha="center",
                        va="center", fontsize=6,
                        color="white" if matrix[i, j] > matrix.max() * 0.6 else PALETTE["charcoal"])

    ax.set_title("Transform Frequency Per Kernel",
                 fontsize=10, fontweight="bold", pad=8)
    plt.colorbar(im, ax=ax, label="Candidate Sites", shrink=0.8)

    fig.tight_layout()
    _save_figure(fig, output_dir, "c3_transform_frequency")
    plt.close(fig)


# ===================================================================
# C.4: HeCBench Kernel Selection Funnel (was f-series F4)
# ===================================================================


def generate_c4_selection_funnel(
    output_dir: Path, verbose: bool,
) -> None:
    """C.4: HeCBench kernel selection pipeline funnel diagram."""
    stages = HECBENCH_FUNNEL_STAGES
    labels = [s[0] for s in stages]
    values = [s[1] for s in stages]
    exclusions = [s[2] for s in stages]

    if verbose:
        for lbl, val, exc in stages:
            exc_str = f" ({exc})" if exc else ""
            print(f"  {lbl.replace(chr(10), ' ')}: {val}{exc_str}")

    n = len(stages)
    fig, ax = plt.subplots(figsize=(3.5, 3.0))

    max_val = max(values)
    y_positions = list(range(n - 1, -1, -1))

    stage_colors = [
        PALETTE["teal_tint"],
        PALETTE["teal_tint"],
        PALETTE["teal"],
        PALETTE["teal"],
        PALETTE["teal_dark"],
    ]

    for i, (label, value, exc) in enumerate(stages):
        y = y_positions[i]
        bar_width = value / max_val * 0.85
        ax.barh(
            y, bar_width, height=0.65,
            left=(1 - bar_width) / 2,
            color=stage_colors[i],
            edgecolor=PALETTE["charcoal"],
            linewidth=0.8,
        )
        text_color = _text_color_for_bg(stage_colors[i])
        ax.text(
            0.5, y, f"{value}",
            ha="center", va="center",
            fontsize=9, fontweight="bold", color=text_color,
        )
        ax.text(
            -0.02, y, label,
            ha="right", va="center",
            fontsize=8, color=PALETTE["charcoal"],
        )
        if exc:
            ax.text(
                1.02, y, exc,
                ha="left", va="center",
                fontsize=8, color=PALETTE["rose_dark"], fontstyle="italic",
            )

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
        fontsize=9, fontweight="bold", pad=8,
    )

    fig.tight_layout()
    _save_figure(fig, output_dir, "c4_selection_funnel")
    plt.close(fig)


# ===================================================================
# T2: Model Comparison LaTeX Table
# ===================================================================


def generate_t2_model_table(
    records: list[dict],
    output_dir: Path,
    verbose: bool,
) -> None:
    """T2: Model comparison LaTeX table -- both directions."""
    base_records = [r for r in records if not r.get("is_sample", False)]

    lines = [
        r"\begin{tabular}{llrrrrrrr}",
        r"\toprule",
        r"Direction & Model & PASS & Total & Rate (\%) & BUILD\_FAIL & RUN\_FAIL & VERIFY\_FAIL & EXTR\_FAIL \\",
        r"\midrule",
    ]

    direction_specs = [
        ("cuda-to-omp", r"CUDA$\to$OMP"),
        ("omp-to-cuda", r"OMP$\to$CUDA"),
        ("cuda-to-opencl", r"CUDA$\to$OCL"),
    ]

    for idx, (direction, dir_label) in enumerate(direction_specs):
        filtered = filter_records(base_records, level=0, suite="rodinia", direction=direction)
        by_model = aggregate_status_counts(filtered, "model")
        model_stats: dict[str, dict] = {}
        for m, status_counts in by_model.items():
            total = sum(status_counts.values())
            pass_count = status_counts.get("PASS", 0)
            model_stats[m] = {"pass": pass_count, "total": total, "by_status": status_counts}

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
        if idx < len(direction_specs) - 1:
            lines.append(r"\midrule")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    path = output_dir / "t2_model_comparison.tex"
    path.write_text("\n".join(lines) + "\n")
    print(f"  Saved: {path}")


# ===================================================================
# Figure registry and CLI
# ===================================================================

FIGURE_REGISTRY: dict[str, str] = {
    "F2":  "f2_repo_vs_kernel",
    "F3":  "f3_kernel_heatmap",
    "F4":  "f4_failure_taxonomy",
    "F5":  "f5_pass_at_k",
    "F6":  "f6_xsbench_comparison",
    "F7":  "f7_augmentation",
    "C.1": "c1_repair_transitions",
    "C.2": "c2_repair_rate",
    "C.3": "c3_transform_frequency",
    "C.4": "c4_selection_funnel",
    "T2":  "t2_model_table",
}

# Which figures need eval data loaded
EVAL_FIGURES = {"F3", "F4", "F5", "F6", "F7", "C.1", "C.2", "T2"}


def _normalize_figure_id(raw: str) -> str | None:
    """Normalize user input to a figure registry key, or None if unknown."""
    s = raw.strip().upper()
    if s in FIGURE_REGISTRY:
        return s
    # Try adding "C." prefix for appendix
    if s.startswith("C") and not s.startswith("C."):
        candidate = "C." + s[1:]
        if candidate in FIGURE_REGISTRY:
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate publication-quality figures for the SC26 paper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Figure IDs: " + ", ".join(FIGURE_REGISTRY.keys()),
    )
    parser.add_argument(
        "--project-root", type=Path, required=True,
        help="Absolute path to project root",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: {project-root}/docs/paper/figures/)",
    )
    parser.add_argument(
        "--figure", default="all",
        help="Figure ID to generate (F2, C.1, T2, etc.) or 'all' (default: all)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
    )
    args = parser.parse_args()

    setup_rcparams()

    project_root = args.project_root.resolve()
    output_dir = (
        args.output_dir or (project_root / "docs" / "paper" / "figures")
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which figures to generate
    if args.figure.strip().lower() == "all":
        requested = set(FIGURE_REGISTRY.keys())
    else:
        fig_id = _normalize_figure_id(args.figure)
        if fig_id is None:
            print(
                f"ERROR: Unknown figure '{args.figure}'. "
                f"Valid: {', '.join(FIGURE_REGISTRY.keys())}, or 'all'",
                file=sys.stderr,
            )
            sys.exit(1)
        requested = {fig_id}

    # Load eval data if needed
    needs_eval = requested & EVAL_FIGURES
    records: list[dict] = []
    if needs_eval:
        print("Loading evaluation results...")
        records = load_eval_results(project_root)
        if not records:
            print(
                f"WARNING: No eval data found in {project_root / 'results' / 'evaluation'} -- "
                f"skipping figures {sorted(needs_eval)}",
                file=sys.stderr,
            )
            requested -= EVAL_FIGURES

    # Filter out sample records for figures that need only base records
    base_count = sum(1 for r in records if not r.get("is_sample", False))
    sample_count = sum(1 for r in records if r.get("is_sample", False))
    if records:
        print(f"  Total: {len(records)} records ({base_count} base, {sample_count} sample)")

    print(f"Output: {output_dir}")
    print(f"Generating: {sorted(requested)}")
    print()

    v = args.verbose

    # --- Main body figures ---

    if "F2" in requested:
        print("Generating F2: Repo vs Kernel-Level Counts...")
        generate_f2_repo_vs_kernel(output_dir, v)
        print()

    if "F3" in requested:
        print("Generating F3: Kernel x Model Heatmap (triple-panel)...")
        generate_f3_kernel_heatmap(records, output_dir, v)
        print()

    if "F4" in requested:
        print("Generating F4: Failure Taxonomy (dual-direction)...")
        generate_f4_failure_taxonomy(records, output_dir, v)
        print()

    if "F5" in requested:
        print("Generating F5: pass@k by Direction...")
        generate_f5_pass_at_k(records, output_dir, v)
        print()

    if "F6" in requested:
        print("Generating F6: XSBench Cross-Granularity Comparison...")
        generate_f6_xsbench_comparison(records, output_dir, v)
        print()

    if "F7" in requested:
        print("Generating F7: Augmentation Robustness (L0-L4)...")
        generate_f7_augmentation(records, output_dir, v)
        print()

    # --- Appendix figures ---

    if "C.1" in requested:
        print("Generating C.1: Self-Repair Transition Matrix...")
        generate_c1_repair_transitions(records, output_dir, v)
        print()

    if "C.2" in requested:
        print("Generating C.2: Self-Repair Rate by Direction...")
        generate_c2_repair_rate(records, output_dir, v)
        print()

    if "C.3" in requested:
        print("Generating C.3: Transform Frequency Heatmap...")
        generate_c3_transform_frequency(project_root, output_dir, v)
        print()

    if "C.4" in requested:
        print("Generating C.4: HeCBench Selection Funnel...")
        generate_c4_selection_funnel(output_dir, v)
        print()

    # --- Table ---

    if "T2" in requested:
        print("Generating T2: Model Comparison LaTeX Table...")
        generate_t2_model_table(records, output_dir, v)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
