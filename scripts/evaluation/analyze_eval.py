#!/usr/bin/env python3
"""scripts/evaluation/analyze_eval.py — Aggregate LLM evaluation results for paper tables.

Reads all per-task result JSONs under results/evaluation/{model}/*.json and produces:
  - results/evaluation/eval_summary.json   — machine-readable aggregate
  - results/evaluation/eval_summary.md     — publication-ready tables
  - visualizations/eval_results_data.js    — dashboard data (optional)

Usage:
    python3 scripts/evaluation/analyze_eval.py \\
      --project-root /home/samyak/Desktop/parbench_sam

    # Show which (kernel, model, direction, level) combos are missing
    python3 scripts/evaluation/analyze_eval.py --show-gaps --project-root ...

    # Filter to one model
    python3 scripts/evaluation/analyze_eval.py --model azure-gpt-4.1 ...
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Specs to exclude from aggregation — KNOWN_FAIL specs whose eval results
# exist but should not count toward pass rates or failure taxonomies.
# Exclusion is spec-level (not kernel-level) to avoid accidentally excluding
# valid translations of kernels that are only partially KNOWN_FAIL.
# E.g. kmeans-cuda is KNOWN_FAIL but kmeans-omp is valid — kernel-level
# exclusion of "kmeans" would wrongly drop kmeans-omp-to-kmeans-cuda results.
#
# Full KNOWN_FAIL list (from .claude/rules/known-issues.md):
#   kmeans-cuda:    texture<> removed in CUDA 12
#   mummergpu-cuda: texture<> removed in CUDA 12
#   mummergpu-omp:  texture<> + cuMemGetInfo_v2 signature
#   hybridsort-cuda: GL/glew.h not found
#   nn-opencl:      TIMEOUT / SIGSEGV (pre-existing)
#   kmeans-opencl:  SIGSEGV in OpenCL runtime (pre-existing)
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
})


# --------------------------------------------------------------------------- #
# Loading                                                                      #
# --------------------------------------------------------------------------- #

def _augment_level_from_filename(stem: str) -> int:
    """Extract augmentation level from result file stem.

    Convention: {src_id}-to-{tgt_id}-L{N}.json  →  N
                {src_id}-to-{tgt_id}.json         →  0
    """
    m = re.search(r"-L(\d+)$", stem)
    return int(m.group(1)) if m else 0


def _direction_from_ids(src_id: str, tgt_id: str) -> str:
    """Infer translation direction from spec IDs, e.g. 'cuda-to-omp'."""
    src_api = src_id.rsplit("-", 1)[-1]
    tgt_api = tgt_id.rsplit("-", 1)[-1]
    return f"{src_api}-to-{tgt_api}"


def load_results(results_dir: Path, model_filter: str | None = None) -> list[dict]:
    """Walk results_dir/{model}/*.json and return all result dicts."""
    records: list[dict] = []
    if not results_dir.exists():
        return records

    for model_dir in sorted(results_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model = model_dir.name
        if model_filter and model != model_filter:
            continue
        # Skip non-model directories (batch summaries live at top level)
        for result_file in sorted(model_dir.rglob("*.json")):
            try:
                data = json.loads(result_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            # Ensure model field is populated
            if "model" not in data or not data["model"]:
                data["model"] = model
            # Enrich with augment_level if not stored in the JSON
            if "augment_level" not in data:
                data["augment_level"] = _augment_level_from_filename(result_file.stem)
            # Enrich with direction if not stored
            if "direction" not in data:
                src = data.get("source_spec", "")
                tgt = data.get("target_spec", "")
                if src and tgt:
                    data["direction"] = _direction_from_ids(src, tgt)
            # Skip results where source or target is a KNOWN_FAIL spec
            src_spec = data.get("source_spec", "")
            tgt_spec = data.get("target_spec", "")
            if src_spec in EXCLUDED_SPECS or tgt_spec in EXCLUDED_SPECS:
                continue
            records.append(data)

    return records


# --------------------------------------------------------------------------- #
# Aggregation helpers                                                          #
# --------------------------------------------------------------------------- #

def _kernel_from_spec(spec_id: str) -> str:
    """Extract kernel name from spec ID like 'rodinia-bfs-cuda' → 'bfs'."""
    parts = spec_id.split("-")
    if len(parts) < 3:
        return spec_id
    return "-".join(parts[1:-1])


def _pass_fail_counts(records: list[dict]) -> dict:
    total = len(records)
    by_status: dict[str, int] = defaultdict(int)
    for r in records:
        by_status[r.get("overall_status", "UNKNOWN")] += 1
    passes = by_status.get("PASS", 0)
    return {
        "pass": passes,
        "total": total,
        "rate": round(passes / total, 4) if total else 0.0,
        "by_status": dict(by_status),
    }


def _self_repair_stats(records: list[dict]) -> dict:
    """Compute self-repair effectiveness from attempts[] field."""
    attempt1_pass = 0
    repaired = 0
    total_with_attempts = 0
    for r in records:
        attempts = r.get("attempts", [])
        if not attempts:
            continue
        total_with_attempts += 1
        final_status = r.get("overall_status", "")
        total_attempts = r.get("total_attempts", len(attempts))
        if final_status == "PASS" and total_attempts == 1:
            attempt1_pass += 1
        elif final_status == "PASS" and total_attempts > 1:
            repaired += 1
    return {
        "attempt_1_pass": attempt1_pass,
        "total_repaired_by_retry": repaired,
        "total_with_attempts": total_with_attempts,
    }


def _load_complexity_lookup(project_root: Path) -> dict[tuple[str, str], str]:
    """Load translation_complexity.csv → {(source_id, target_id): complexity_class} lookup."""
    csv_path = project_root / "results" / "evaluation" / "translation_complexity.csv"
    if not csv_path.exists():
        return {}
    lookup: dict[tuple[str, str], str] = {}
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            lookup[(row["source_spec"], row["target_spec"])] = row["complexity_class"]
    return lookup


def build_summary(records: list[dict], complexity_lookup: dict | None = None) -> dict:
    """Build the machine-readable summary dict."""
    by_model: dict[str, list] = defaultdict(list)
    by_direction: dict[str, list] = defaultdict(list)
    by_kernel: dict[str, list] = defaultdict(list)
    by_level: dict[str, list] = defaultdict(list)
    by_complexity: dict[str, list] = defaultdict(list)
    # Pre-populate all failure verdict types so zero-count entries appear in the taxonomy
    # (e.g., VERIFY_FAIL: 0 should be explicit, not absent, for downstream consumers).
    failure_counts: dict[str, int] = defaultdict(int)
    for _vt in ("BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL"):
        failure_counts[_vt] = 0

    for r in records:
        model = r.get("model", "unknown")
        direction = r.get("direction", "unknown")
        src_id = r.get("source_spec", "")
        kernel = r.get("kernel") or (_kernel_from_spec(src_id) if src_id else "?")
        level = r.get("augment_level", 0)
        status = r.get("overall_status", "UNKNOWN")

        by_model[model].append(r)
        by_direction[direction].append(r)
        by_kernel[kernel].append(r)
        by_level[f"L{level}"].append(r)

        if complexity_lookup is not None:
            tgt_id = r.get("target_spec", "")
            cls = complexity_lookup.get((src_id, tgt_id), "unknown")
            by_complexity[cls].append(r)

        if status not in ("PASS", "SKIP", "ERROR"):
            failure_counts[status] += 1

    return {
        "generated_at": datetime.now().isoformat(),
        "total_tasks": len(records),
        "by_model": {k: _pass_fail_counts(v) for k, v in sorted(by_model.items())},
        "by_direction": {k: _pass_fail_counts(v) for k, v in sorted(by_direction.items())},
        "by_kernel": {k: _pass_fail_counts(v) for k, v in sorted(by_kernel.items())},
        "by_augment_level": {k: _pass_fail_counts(v) for k, v in sorted(by_level.items())},
        "failure_taxonomy": dict(failure_counts),
        "self_repair": _self_repair_stats(records),
        "by_complexity": {k: _pass_fail_counts(v) for k, v in sorted(by_complexity.items())} if complexity_lookup is not None else {},
    }


# --------------------------------------------------------------------------- #
# Markdown report                                                              #
# --------------------------------------------------------------------------- #

def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def build_markdown(summary: dict, records: list[dict], complexity_lookup: dict | None = None) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# ParBench Evaluation Summary",
        f"**Generated:** {now}  |  **Total tasks:** {summary['total_tasks']}",
        "",
    ]

    # --- By model ---
    lines += ["## Pass Rates by Model", ""]
    lines += ["| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |",
              "|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|"]
    for model, stats in summary["by_model"].items():
        bk = stats["by_status"]
        lines.append(
            f"| {model} | {stats['pass']} | {stats['total']} | {_pct(stats['rate'])} "
            f"| {bk.get('BUILD_FAIL', 0)} | {bk.get('RUN_FAIL', 0)} | {bk.get('VERIFY_FAIL', 0)} "
            f"| {bk.get('EXTRACTION_FAIL', 0)} |"
        )
    lines.append("")

    # --- By direction ---
    lines += ["## Pass Rates by Translation Direction", ""]
    lines += ["| Direction | PASS | Total | Rate |",
              "|-----------|-----:|------:|-----:|"]
    for direction, stats in summary["by_direction"].items():
        lines.append(
            f"| {direction} | {stats['pass']} | {stats['total']} | {_pct(stats['rate'])} |"
        )
    lines.append("")

    # --- By augment level ---
    lines += ["## Pass Rates by Augmentation Level", ""]
    lines += ["| Level | PASS | Total | Rate |",
              "|-------|-----:|------:|-----:|"]
    for level, stats in summary["by_augment_level"].items():
        lines.append(
            f"| {level} | {stats['pass']} | {stats['total']} | {_pct(stats['rate'])} |"
        )
    lines.append("")

    # --- By translation complexity class ---
    by_comp = summary.get("by_complexity", {})
    if by_comp:
        classes = sorted(by_comp.keys())
        lines += ["## Pass Rates by Translation Complexity", ""]
        lines += [
            "| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |",
            "|-----------------|-----:|------:|-----:|----------:|--------:|------------:|",
        ]
        for cls in classes:
            stats = by_comp[cls]
            bk = stats["by_status"]
            lines.append(
                f"| {cls} | {stats['pass']} | {stats['total']} | {_pct(stats['rate'])} "
                f"| {bk.get('BUILD_FAIL', 0)} | {bk.get('RUN_FAIL', 0)} "
                f"| {bk.get('VERIFY_FAIL', 0)} |"
            )
        lines.append("")

        # Model × complexity cross-tab (when multiple models have results)
        if complexity_lookup and len(summary.get("by_model", {})) > 1:
            models = sorted(summary["by_model"].keys())
            lines += ["### Model × Complexity Cross-Tab", ""]
            model_header = " | ".join(models)
            lines.append(f"| Complexity Class | {model_header} |")
            lines.append("|-----------------|" + "|".join(["---:"] * len(models)) + "|")
            comp_model: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
            for r in records:
                src = r.get("source_spec", "")
                tgt = r.get("target_spec", "")
                cls = complexity_lookup.get((src, tgt))
                if cls is None:
                    continue
                model = r.get("model", "unknown")
                comp_model[cls][model].append(r)
            for cls in classes:
                if cls == "unknown":
                    continue
                cells = []
                for model in models:
                    recs = comp_model[cls].get(model, [])
                    if recs:
                        c = _pass_fail_counts(recs)
                        cells.append(f"{c['pass']}/{c['total']} ({_pct(c['rate'])})")
                    else:
                        cells.append("—")
                lines.append(f"| {cls} | {' | '.join(cells)} |")
            lines.append("")

    # --- Per-kernel matrix (cuda→omp only for primary table) ---
    cuda_omp = [r for r in records if r.get("direction", "").startswith("cuda-to-omp")]
    if cuda_omp:
        models = sorted({r.get("model", "?") for r in cuda_omp})
        kernels = sorted({_kernel_from_spec(r.get("source_spec", "?")) for r in cuda_omp})
        lines += ["## Kernel × Model Matrix (cuda→omp, L0)", ""]
        col_header = " | ".join(models)
        lines.append(f"| Kernel | {col_header} |")
        lines.append("|--------|" + "|".join(["---"] * len(models)) + "|")
        # Build lookup: (kernel, model) → status for L0
        lookup: dict[tuple, str] = {}
        for r in cuda_omp:
            if r.get("augment_level", 0) == 0:
                k = _kernel_from_spec(r.get("source_spec", "?"))
                m = r.get("model", "?")
                lookup[(k, m)] = r.get("overall_status", "?")
        for kernel in kernels:
            cells = []
            for model in models:
                s = lookup.get((kernel, model), "—")
                sym = "✓" if s == "PASS" else ("!" if s == "ERROR" else ("—" if s == "—" else "✗"))
                cells.append(f"{sym} {s}" if s != "—" else "—")
            lines.append(f"| {kernel} | {' | '.join(cells)} |")
        lines.append("")

    # --- Failure taxonomy ---
    lines += ["## Failure Taxonomy", ""]
    tax = summary["failure_taxonomy"]
    if tax:
        lines += ["| Status | Count |", "|--------|------:|"]
        for status, count in sorted(tax.items(), key=lambda x: -x[1]):
            lines.append(f"| {status} | {count} |")
    else:
        lines.append("No failures recorded.")
    lines.append("")

    # --- Self-repair ---
    sr = summary["self_repair"]
    if sr["total_with_attempts"] > 0:
        lines += ["## Self-Repair (Iterative Retry) Effectiveness", ""]
        lines += [
            f"- Tasks with recorded attempts: **{sr['total_with_attempts']}**",
            f"- Passed on first attempt: **{sr['attempt_1_pass']}**",
            f"- Repaired by retry: **{sr['total_repaired_by_retry']}**",
            "",
        ]

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Gap analysis                                                                 #
# --------------------------------------------------------------------------- #

def show_gaps(records: list[dict], expected_models: list[str],
              expected_directions: list[str], expected_levels: list[int]) -> None:
    """Print (kernel, model, direction, level) combos that have no result yet."""
    have: set[tuple] = set()
    all_kernels: set[str] = set()

    for r in records:
        kernel = _kernel_from_spec(r.get("source_spec", "?"))
        model = r.get("model", "?")
        direction = r.get("direction", "?")
        level = r.get("augment_level", 0)
        have.add((kernel, model, direction, level))
        all_kernels.add(kernel)

    print("\n=== Gap Analysis ===")
    print(f"Kernels with at least one result: {sorted(all_kernels)}")
    print()

    gaps = []
    for kernel in sorted(all_kernels):
        for model in expected_models:
            for direction in expected_directions:
                for level in expected_levels:
                    if (kernel, model, direction, level) not in have:
                        gaps.append((kernel, model, direction, f"L{level}"))

    if not gaps:
        print("No gaps found — matrix is complete.")
    else:
        print(f"{len(gaps)} missing (kernel, model, direction, level) combinations:")
        for g in gaps:
            print(f"  MISSING: kernel={g[0]}  model={g[1]}  direction={g[2]}  level={g[3]}")


# --------------------------------------------------------------------------- #
# Dashboard data writer                                                        #
# --------------------------------------------------------------------------- #

def write_dashboard_js(summary: dict, output_path: Path) -> None:
    """Update eval_results_data.js with fresh summary stats."""
    js_data = {
        "generatedAt": summary["generated_at"],
        "totalTasks": summary["total_tasks"],
        "byModel": summary["by_model"],
        "byDirection": summary["by_direction"],
        "byKernel": summary["by_kernel"],
        "byAugmentLevel": summary["by_augment_level"],
        "failureTaxonomy": summary["failure_taxonomy"],
        "selfRepair": summary["self_repair"],
        "byComplexity": summary.get("by_complexity", {}),
    }
    content = f"// Auto-generated by analyze_eval.py — do not edit manually\n"
    content += f"const EVAL_SUMMARY = {json.dumps(js_data, indent=2)};\n"
    output_path.write_text(content)
    print(f"Dashboard data written: {output_path}")


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate ParBench LLM evaluation results for paper tables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Path to parbench_sam root (default: auto-detected).",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=None,
        help="Override results directory (default: {project_root}/results/evaluation/).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Filter to a specific model name.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Output path for eval_summary.json (default: results/evaluation/eval_summary.json).",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Output path for eval_summary.md (default: results/evaluation/eval_summary.md).",
    )
    parser.add_argument(
        "--write-dashboard",
        action="store_true",
        default=False,
        help="Also write visualizations/eval_results_data.js.",
    )
    parser.add_argument(
        "--show-gaps",
        action="store_true",
        default=False,
        help="Print missing (kernel, model, direction, level) combinations.",
    )
    parser.add_argument(
        "--expected-models",
        nargs="+",
        default=[
            "together-qwen-3.5-397b-a17b",
            "gemini-2.5-flash",
        ],
        metavar="MODEL",
        help="Models expected in the full matrix (used by --show-gaps).",
    )
    parser.add_argument(
        "--expected-directions",
        nargs="+",
        default=["cuda-to-omp"],
        metavar="DIR",
        help="Directions expected in the full matrix (used by --show-gaps).",
    )
    parser.add_argument(
        "--expected-levels",
        nargs="+",
        type=int,
        default=[0],
        metavar="LEVEL",
        help="Augmentation levels expected in the full matrix (used by --show-gaps).",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    results_dir = args.results_dir or (project_root / "results" / "evaluation")
    out_json = args.out_json or (results_dir / "eval_summary.json")
    out_md = args.out_md or (results_dir / "eval_summary.md")

    print(f"Loading results from: {results_dir}")
    records = load_results(results_dir, model_filter=args.model)
    print(f"Loaded {len(records)} result records.")

    if not records:
        print("No results found. Run some evaluations first.")
        sys.exit(0)

    complexity_lookup = _load_complexity_lookup(project_root)
    if complexity_lookup:
        print(f"Loaded complexity lookup: {len(complexity_lookup)} translation pairs.")
    else:
        print("No complexity CSV found — complexity analysis will be skipped.")

    summary = build_summary(records, complexity_lookup=complexity_lookup)

    # Write JSON summary
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2))
    print(f"Summary JSON written: {out_json}")

    # Write Markdown report
    md = build_markdown(summary, records, complexity_lookup=complexity_lookup)
    out_md.write_text(md)
    print(f"Summary Markdown written: {out_md}")

    # Optionally write dashboard JS
    if args.write_dashboard:
        dash_path = project_root / "visualizations" / "eval_results_data.js"
        write_dashboard_js(summary, dash_path)

    # Gap analysis
    if args.show_gaps:
        show_gaps(records, args.expected_models, args.expected_directions, args.expected_levels)

    # Print quick summary to console
    print("\n=== Quick Summary ===")
    for model, stats in summary["by_model"].items():
        print(f"  {model}: {stats['pass']}/{stats['total']} PASS ({_pct(stats['rate'])})")
    print(f"\nFailure taxonomy: {summary['failure_taxonomy']}")


if __name__ == "__main__":
    main()
