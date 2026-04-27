#!/usr/bin/env python3
"""Cross-model comparison: Qwen 3.5 397B vs azure-gpt-5.4.

Produces statistical comparison for NeurIPS 2026 paper using Phase 3 canonical+ablation corpus.
Reads paper_data.json (Qwen) and paper_data_azure_gpt54.json (GPT).

Output: results/analysis/cross_model_comparison.json

Statistical tests:
  - Chi-squared test on 2x2 contingency table (model x pass/fail)
  - Cohen's h effect sizes (overall + per-direction)
  - Per-direction paired comparison for common directions only
  - Per-kernel agreement matrix with four-way classification
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for two proportions.

    Clamp inputs to [0, 1] to handle edge cases.
    Positive when p1 > p2.
    """
    p1 = max(0.0, min(1.0, p1))
    p2 = max(0.0, min(1.0, p2))
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


def classify_effect_size(h: float) -> str:
    """Classify |h| per Cohen's conventions.

    |h| < 0.2: negligible
    0.2 <= |h| < 0.5: small
    0.5 <= |h| < 0.8: medium
    |h| >= 0.8: large
    """
    ah = abs(h)
    if ah < 0.2:
        return "negligible"
    elif ah < 0.5:
        return "small"
    elif ah < 0.8:
        return "medium"
    else:
        return "large"


def build_comparison(qwen_data: dict, gpt_data: dict) -> dict:
    """Build the full cross-model comparison dict.

    Args:
        qwen_data: Parsed paper_data.json (Qwen model)
        gpt_data: Parsed paper_data_azure_gpt54.json (GPT model)

    Returns:
        Dict with overall, per_direction, per_kernel_matrix sections.
    """
    qwen_pc = qwen_data.get("passk_campaign") or qwen_data["primary_campaign"]
    gpt_pc = gpt_data.get("passk_campaign") or gpt_data["primary_campaign"]

    # --- Determine common directions (intersection) ---
    qwen_dirs = set(qwen_pc["by_direction"].keys())
    gpt_dirs = set(gpt_pc["by_direction"].keys())
    common_dirs = sorted(qwen_dirs & gpt_dirs)

    missing = {}
    qwen_only = sorted(qwen_dirs - gpt_dirs)
    gpt_only = sorted(gpt_dirs - qwen_dirs)
    if qwen_only:
        missing[gpt_data["model"]] = qwen_only  # GPT is missing these directions
    if gpt_only:
        missing[qwen_data["model"]] = gpt_only

    # --- Overall comparison ---
    qwen_overall = qwen_pc["overall"]
    gpt_overall = gpt_pc["overall"]

    qwen_pass = qwen_overall["pass"]
    qwen_total = qwen_overall["total"]
    qwen_fail = qwen_total - qwen_pass
    gpt_pass = gpt_overall["pass"]
    gpt_total = gpt_overall["total"]
    gpt_fail = gpt_total - gpt_pass

    # Chi-squared on 2x2 contingency table
    table = np.array([[qwen_pass, qwen_fail],
                      [gpt_pass, gpt_fail]])
    chi2, p_value, dof, expected = sp_stats.chi2_contingency(table)

    qwen_rate = qwen_overall["pass_rate"]
    gpt_rate = gpt_overall["pass_rate"]
    h_overall = cohens_h(qwen_rate, gpt_rate)

    overall = {
        "contingency_table": table.tolist(),
        "chi_squared": {
            "chi2": round(float(chi2), 4),
            "p_value": round(float(p_value), 6),
            "dof": int(dof),
        },
        "qwen": {
            "pass": int(qwen_pass),
            "total": int(qwen_total),
            "rate": round(float(qwen_rate), 4),
        },
        "gpt": {
            "pass": int(gpt_pass),
            "total": int(gpt_total),
            "rate": round(float(gpt_rate), 4),
        },
        "cohens_h": round(float(h_overall), 4),
        "effect_size": classify_effect_size(h_overall),
    }

    # --- Per-direction comparison (common directions only) ---
    per_direction = {}
    for d in common_dirs:
        qd = qwen_pc["by_direction"][d]
        gd = gpt_pc["by_direction"][d]
        qr = qd["pass_rate"]
        gr = gd["pass_rate"]
        h = cohens_h(qr, gr)
        per_direction[d] = {
            "qwen": {
                "pass": int(qd["pass"]),
                "total": int(qd["total"]),
                "rate": round(float(qr), 4),
            },
            "gpt": {
                "pass": int(gd["pass"]),
                "total": int(gd["total"]),
                "rate": round(float(gr), 4),
            },
            "cohens_h": round(float(h), 4),
            "effect_size": classify_effect_size(h),
        }

    # --- Per-kernel agreement matrix (four-way per D-04) ---
    # A kernel "passes" for a model if it has any passing task (pass > 0)
    qwen_bk = qwen_pc.get("by_kernel", {})
    gpt_bk = gpt_pc.get("by_kernel", {})
    qwen_kernels = set(qwen_bk.keys())
    gpt_kernels = set(gpt_bk.keys())
    common_kernels = sorted(qwen_kernels & gpt_kernels)

    both_pass = []
    both_fail = []
    qwen_only_pass = []
    gpt_only_pass = []

    for kernel in common_kernels:
        qk = qwen_bk[kernel]
        gk = gpt_bk[kernel]
        q_passes = qk["pass"] > 0
        g_passes = gk["pass"] > 0
        if q_passes and g_passes:
            both_pass.append(kernel)
        elif not q_passes and not g_passes:
            both_fail.append(kernel)
        elif q_passes and not g_passes:
            qwen_only_pass.append(kernel)
        else:
            gpt_only_pass.append(kernel)

    per_kernel_matrix = {
        "total_common_kernels": len(common_kernels),
        "both_pass": sorted(both_pass),
        "both_fail": sorted(both_fail),
        "qwen_only_pass": sorted(qwen_only_pass),
        "gpt_only_pass": sorted(gpt_only_pass),
        "counts": {
            "both_pass": len(both_pass),
            "both_fail": len(both_fail),
            "qwen_only_pass": len(qwen_only_pass),
            "gpt_only_pass": len(gpt_only_pass),
        },
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models": [qwen_data["model"], gpt_data["model"]],
        "common_directions": common_dirs,
        "missing_directions": missing,
        "overall": overall,
        "per_direction": per_direction,
        "per_kernel_matrix": per_kernel_matrix,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-model comparison for NeurIPS 2026 paper (Phase 3 canonical+ablation corpus).",
    )
    parser.add_argument(
        "--qwen-data",
        type=Path,
        default=Path("results/analysis/paper_data_together-qwen-3.5-397b-a17b.json"),
        help="Path to Qwen paper_data JSON",
    )
    parser.add_argument(
        "--gpt-data",
        type=Path,
        default=Path("results/analysis/paper_data_azure_gpt54.json"),
        help="Path to azure-gpt-5.4 paper_data.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/analysis/cross_model_comparison.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
    )
    args = parser.parse_args()

    # Resolve paths
    qwen_path = args.qwen_data if args.qwen_data.is_absolute() else Path.cwd() / args.qwen_data
    gpt_path = args.gpt_data if args.gpt_data.is_absolute() else Path.cwd() / args.gpt_data
    output_path = args.output if args.output.is_absolute() else Path.cwd() / args.output

    # Load data
    if not qwen_path.exists():
        print(f"ERROR: Qwen data not found: {qwen_path}", file=sys.stderr)
        sys.exit(1)
    if not gpt_path.exists():
        print(f"ERROR: GPT data not found: {gpt_path}", file=sys.stderr)
        sys.exit(1)

    qwen_data = json.loads(qwen_path.read_text())
    gpt_data = json.loads(gpt_path.read_text())

    # Build comparison
    result = build_comparison(qwen_data, gpt_data)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {output_path}")

    if args.verbose:
        o = result["overall"]
        print(f"\n=== Cross-Model Comparison ===")
        print(f"Qwen: {o['qwen']['pass']}/{o['qwen']['total']} ({o['qwen']['rate']:.1%})")
        print(f"GPT:  {o['gpt']['pass']}/{o['gpt']['total']} ({o['gpt']['rate']:.1%})")
        print(f"Chi-squared: chi2={o['chi_squared']['chi2']:.4f}, "
              f"p={o['chi_squared']['p_value']:.6f}")
        print(f"Cohen's h: {o['cohens_h']:.4f} ({o['effect_size']})")
        print(f"\nCommon directions: {len(result['common_directions'])}")
        print(f"Missing: {result['missing_directions']}")
        km = result["per_kernel_matrix"]
        print(f"\nPer-kernel matrix ({km['total_common_kernels']} kernels):")
        print(f"  Both pass: {km['counts']['both_pass']}")
        print(f"  Both fail: {km['counts']['both_fail']}")
        print(f"  Qwen only: {km['counts']['qwen_only_pass']}")
        print(f"  GPT only:  {km['counts']['gpt_only_pass']}")
        print(f"\nPer-direction breakdown:")
        for d in result["common_directions"]:
            dd = result["per_direction"][d]
            print(f"  {d}: Qwen {dd['qwen']['rate']:.1%} vs GPT {dd['gpt']['rate']:.1%} "
                  f"(h={dd['cohens_h']:.4f}, {dd['effect_size']})")


if __name__ == "__main__":
    main()
