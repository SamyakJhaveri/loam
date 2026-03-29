#!/usr/bin/env python3
"""
scripts/analysis/selfrepair_analysis.py

Self-repair breakdown by failure type, model, and kernel.

Reads the attempts[] array from each result JSON to classify repair outcomes:
  - full_repair:    first attempt failed, final attempt PASS
  - partial_repair: status improved but final is not PASS
  - no_repair:      status unchanged across attempts
  - regression:     status worsened (e.g., RUN_FAIL → BUILD_FAIL)

Status ordering (lower is worse):
  EXTRACTION_FAIL < BUILD_FAIL < RUN_FAIL < VERIFY_FAIL < PASS

Output: results/analysis/selfrepair_analysis.json + .md (4 tables)

Usage:
    python3 scripts/analysis/selfrepair_analysis.py \\
        --project-root /home/samyak/Desktop/parbench_sam
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

# Status ordering: higher = further in pipeline = better
STATUS_ORDER = {
    "EXTRACTION_FAIL": 0,
    "BUILD_FAIL": 1,
    "RUN_FAIL": 2,
    "VERIFY_FAIL": 3,
    "PASS": 4,
    "ERROR": -1,
    "OTHER": -1,
}

MODEL_DISPLAY = {
    "together-qwen-3.5-397b-a17b": "Qwen 3.5 397B (Together)",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    # Legacy models (kept for historical result analysis)
    "claude-sonnet-4-6": "Claude Sonnet 4",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite",
    "groq-llama-3.3-70b-versatile": "Groq Llama 3.3 70B",
    "azure-gpt-4.1": "Azure GPT-4.1",
}


def classify_attempt_status(attempt: dict) -> str:
    """Determine the status of a single attempt."""
    if attempt.get("extraction_fail"):
        return "EXTRACTION_FAIL"
    bs = attempt.get("build_status")
    rs = attempt.get("run_status")
    vs = attempt.get("verify_status")
    if bs == "fail" or (bs is None and rs is None and vs is None and not attempt.get("extraction_fail")):
        # Build failed or nothing happened (likely build issue)
        if bs == "fail":
            return "BUILD_FAIL"
        # If all statuses are None and no extraction_fail, check for error
        return "OTHER"
    if rs in ("fail", "timeout"):
        return "RUN_FAIL"
    if vs == "fail":
        return "VERIFY_FAIL"
    if vs == "pass":
        return "PASS"
    # Fallback
    return "OTHER"


def classify_repair(first_status: str, final_status: str) -> str:
    """Classify the repair outcome."""
    if final_status == "PASS":
        return "full_repair"
    first_ord = STATUS_ORDER.get(first_status, -1)
    final_ord = STATUS_ORDER.get(final_status, -1)
    if final_ord > first_ord:
        return "partial_repair"
    if final_ord < first_ord:
        return "regression"
    return "no_repair"


def load_all_results(project_root: Path) -> list[dict]:
    """Load all result JSONs."""
    results = []
    eval_dir = project_root / "results" / "evaluation"
    for model_dir in sorted(eval_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        for json_file in sorted(model_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                if "overall_status" not in data:
                    continue
                data["_file"] = str(json_file.relative_to(project_root))
                results.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    output_dir = args.output_dir or (project_root / "results" / "analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = load_all_results(project_root)
    print(f"Loaded {len(results)} results")

    # Separate single-attempt and multi-attempt
    single_attempt = [r for r in results if r.get("total_attempts", 1) == 1]
    multi_attempt = [r for r in results if r.get("total_attempts", 1) > 1]
    print(f"Single-attempt (first try success or max_retries=0): {len(single_attempt)}")
    print(f"Multi-attempt (needed retry): {len(multi_attempt)}")

    # Analyze each multi-attempt result
    repairs = []
    for r in multi_attempt:
        attempts = r.get("attempts", [])
        if len(attempts) < 2:
            continue

        first_attempt = attempts[0]
        final_attempt = attempts[-1]

        first_status = classify_attempt_status(first_attempt)
        final_status = classify_attempt_status(final_attempt)
        overall = r.get("overall_status", final_status)

        # Use overall_status as authoritative final status (per known-issues.md)
        repair_class = classify_repair(first_status, overall)

        repair_info = {
            "kernel": r.get("kernel", "unknown"),
            "model": r.get("model", "unknown"),
            "direction": f"{r.get('source_spec', '').split('-')[-1]}-to-{r.get('target_spec', '').split('-')[-1]}",
            "augment_level": r.get("augment_level", 0),
            "total_attempts": r.get("total_attempts", len(attempts)),
            "first_status": first_status,
            "final_status": overall,
            "repair_class": repair_class,
            # Token overhead from repair
            "attempt1_prompt_tokens": first_attempt.get("prompt_tokens", 0),
            "attempt1_completion_tokens": first_attempt.get("completion_tokens", 0),
            "total_prompt_tokens": r.get("prompt_tokens", 0),
            "total_completion_tokens": r.get("completion_tokens", 0),
        }
        repairs.append(repair_info)

    # ── Aggregate statistics ──────────────────────────────────────────
    repair_counts = defaultdict(int)
    for rep in repairs:
        repair_counts[rep["repair_class"]] += 1

    full_repair_count = repair_counts.get("full_repair", 0)
    partial_repair_count = repair_counts.get("partial_repair", 0)
    no_repair_count = repair_counts.get("no_repair", 0)
    regression_count = repair_counts.get("regression", 0)

    print(f"\nRepair outcomes:")
    print(f"  Full repair (→ PASS):  {full_repair_count}")
    print(f"  Partial repair:        {partial_repair_count}")
    print(f"  No repair (same):      {no_repair_count}")
    print(f"  Regression (worse):    {regression_count}")

    # ── Per-model breakdown ───────────────────────────────────────────
    by_model: dict[str, dict] = {}
    model_groups = defaultdict(list)
    for rep in repairs:
        model_groups[rep["model"]].append(rep)

    for model_id, model_repairs in sorted(model_groups.items()):
        counts = defaultdict(int)
        for rep in model_repairs:
            counts[rep["repair_class"]] += 1

        # Also count by initial failure type
        by_initial = defaultdict(lambda: defaultdict(int))
        for rep in model_repairs:
            by_initial[rep["first_status"]][rep["repair_class"]] += 1

        by_model[model_id] = {
            "display_name": MODEL_DISPLAY.get(model_id, model_id),
            "total_multi_attempt": len(model_repairs),
            "full_repair": counts.get("full_repair", 0),
            "partial_repair": counts.get("partial_repair", 0),
            "no_repair": counts.get("no_repair", 0),
            "regression": counts.get("regression", 0),
            "repair_rate": round(counts.get("full_repair", 0) / len(model_repairs), 4) if model_repairs else 0,
            "any_improvement_rate": round(
                (counts.get("full_repair", 0) + counts.get("partial_repair", 0)) / len(model_repairs),
                4,
            ) if model_repairs else 0,
            "by_initial_failure": {k: dict(v) for k, v in sorted(by_initial.items())},
        }

    # ── Per-initial-failure breakdown ─────────────────────────────────
    by_initial_failure: dict[str, dict] = {}
    initial_groups = defaultdict(list)
    for rep in repairs:
        initial_groups[rep["first_status"]].append(rep)

    for initial_status, ireps in sorted(initial_groups.items()):
        counts = defaultdict(int)
        for rep in ireps:
            counts[rep["repair_class"]] += 1

        by_initial_failure[initial_status] = {
            "total": len(ireps),
            "full_repair": counts.get("full_repair", 0),
            "partial_repair": counts.get("partial_repair", 0),
            "no_repair": counts.get("no_repair", 0),
            "regression": counts.get("regression", 0),
            "repair_rate": round(counts.get("full_repair", 0) / len(ireps), 4) if ireps else 0,
        }

    # ── Per-kernel breakdown ──────────────────────────────────────────
    by_kernel: dict[str, dict] = {}
    kernel_groups = defaultdict(list)
    for rep in repairs:
        kernel_groups[rep["kernel"]].append(rep)

    for kernel, kreps in sorted(kernel_groups.items()):
        counts = defaultdict(int)
        for rep in kreps:
            counts[rep["repair_class"]] += 1

        by_kernel[kernel] = {
            "total_multi_attempt": len(kreps),
            "full_repair": counts.get("full_repair", 0),
            "partial_repair": counts.get("partial_repair", 0),
            "no_repair": counts.get("no_repair", 0),
            "regression": counts.get("regression", 0),
            "repair_rate": round(counts.get("full_repair", 0) / len(kreps), 4) if kreps else 0,
        }

    # ── Token overhead from repair ────────────────────────────────────
    # How many extra tokens did retries consume?
    total_extra_prompt = sum(
        r["total_prompt_tokens"] - r["attempt1_prompt_tokens"]
        for r in repairs
    )
    total_extra_completion = sum(
        r["total_completion_tokens"] - r["attempt1_completion_tokens"]
        for r in repairs
    )

    # For full repairs: was the extra cost worth it?
    full_repairs = [r for r in repairs if r["repair_class"] == "full_repair"]
    fr_extra_prompt = sum(r["total_prompt_tokens"] - r["attempt1_prompt_tokens"] for r in full_repairs) if full_repairs else 0
    fr_extra_completion = sum(r["total_completion_tokens"] - r["attempt1_completion_tokens"] for r in full_repairs) if full_repairs else 0

    token_overhead = {
        "total_extra_prompt_tokens": total_extra_prompt,
        "total_extra_completion_tokens": total_extra_completion,
        "total_extra_tokens": total_extra_prompt + total_extra_completion,
        "full_repair_extra_prompt_tokens": fr_extra_prompt,
        "full_repair_extra_completion_tokens": fr_extra_completion,
        "mean_extra_tokens_per_retry": round(
            (total_extra_prompt + total_extra_completion) / len(repairs), 1
        ) if repairs else 0,
    }

    # ── Repair trajectory patterns ─────────────────────────────────────
    trajectories: dict[str, int] = defaultdict(int)
    for r in multi_attempt:
        attempts = r.get("attempts", [])
        if len(attempts) < 2:
            continue
        statuses = [classify_attempt_status(a) for a in attempts]
        trajectory = " → ".join(statuses)
        trajectories[trajectory] += 1
    sorted_trajectories = sorted(trajectories.items(), key=lambda x: -x[1])

    # ── Build output ──────────────────────────────────────────────────
    output = {
        "analysis": "self_repair_breakdown",
        "total_results": len(results),
        "single_attempt_count": len(single_attempt),
        "total_multi_attempt": len(repairs),
        "full_repair_count": full_repair_count,
        "partial_repair_count": partial_repair_count,
        "no_repair_count": no_repair_count,
        "regression_count": regression_count,
        "overall_repair_rate": round(full_repair_count / len(repairs), 4) if repairs else 0,
        "overall_any_improvement_rate": round(
            (full_repair_count + partial_repair_count) / len(repairs), 4
        ) if repairs else 0,
        "by_model": by_model,
        "by_initial_failure": by_initial_failure,
        "by_kernel": by_kernel,
        "token_overhead": token_overhead,
        "repair_trajectories": [
            {"trajectory": t, "count": c} for t, c in sorted_trajectories
        ],
    }

    json_path = output_dir / "selfrepair_analysis.json"
    json_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {json_path}")

    # ── Markdown report ───────────────────────────────────────────────
    md_lines = [
        "# Self-Repair Analysis — ParBench Evaluation",
        "",
        f"**{len(results)} total results**: {len(single_attempt)} single-attempt, "
        f"{len(repairs)} multi-attempt (needed retry).",
        "",
        f"Of {len(repairs)} retried translations:",
        f"- **{full_repair_count}** ({full_repair_count/len(repairs):.1%}) achieved full repair (reached PASS)",
        f"- **{partial_repair_count}** ({partial_repair_count/len(repairs):.1%}) showed partial improvement",
        f"- **{no_repair_count}** ({no_repair_count/len(repairs):.1%}) showed no change",
        f"- **{regression_count}** ({regression_count/len(repairs):.1%}) regressed to a worse status",
        "",
        "## Table 1: Per-Model Self-Repair",
        "",
        "| Model | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate | Improvement Rate |",
        "|-------|-------------:|------------:|--------:|----------:|-----------:|------------:|-----------------:|",
    ]

    for model_id in MODEL_DISPLAY:
        m = by_model.get(model_id)
        if not m:
            continue
        md_lines.append(
            f"| {m['display_name']} | {m['total_multi_attempt']} | "
            f"{m['full_repair']} | {m['partial_repair']} | "
            f"{m['no_repair']} | {m['regression']} | "
            f"{m['repair_rate']:.1%} | {m['any_improvement_rate']:.1%} |"
        )

    md_lines.extend([
        "",
        "## Table 2: By Initial Failure Type",
        "",
        "| Initial Failure | Count | Full Repair | Partial | No Change | Regression | Repair Rate |",
        "|-----------------|------:|------------:|--------:|----------:|-----------:|------------:|",
    ])

    for status in ["EXTRACTION_FAIL", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "OTHER"]:
        f = by_initial_failure.get(status)
        if not f:
            continue
        md_lines.append(
            f"| {status} | {f['total']} | {f['full_repair']} | "
            f"{f['partial_repair']} | {f['no_repair']} | "
            f"{f['regression']} | {f['repair_rate']:.1%} |"
        )

    md_lines.extend([
        "",
        "## Table 3: Per-Kernel Self-Repair (sorted by repair rate)",
        "",
        "| Kernel | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate |",
        "|--------|-------------:|------------:|--------:|----------:|-----------:|------------:|",
    ])

    for kernel in sorted(by_kernel, key=lambda k: by_kernel[k]["repair_rate"], reverse=True):
        k = by_kernel[kernel]
        md_lines.append(
            f"| {kernel} | {k['total_multi_attempt']} | "
            f"{k['full_repair']} | {k['partial_repair']} | "
            f"{k['no_repair']} | {k['regression']} | {k['repair_rate']:.1%} |"
        )

    md_lines.extend([
        "",
        "## Table 4: Token Overhead from Self-Repair",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Total extra prompt tokens | {token_overhead['total_extra_prompt_tokens']:,} |",
        f"| Total extra completion tokens | {token_overhead['total_extra_completion_tokens']:,} |",
        f"| Total extra tokens (all retries) | {token_overhead['total_extra_tokens']:,} |",
        f"| Mean extra tokens per retry | {token_overhead['mean_extra_tokens_per_retry']:,.0f} |",
        f"| Full-repair extra prompt tokens | {token_overhead['full_repair_extra_prompt_tokens']:,} |",
        f"| Full-repair extra completion tokens | {token_overhead['full_repair_extra_completion_tokens']:,} |",
        "",
        "## Table 5: Repair Trajectory Patterns",
        "",
        "| Trajectory | Count | % of Multi-Attempt |",
        "|------------|------:|-------------------:|",
    ])

    for trajectory, count in sorted_trajectories[:15]:
        pct = count / len(repairs) * 100
        md_lines.append(f"| {trajectory} | {count} | {pct:.1f}% |")

    md_lines.extend([
        "",
        "## Interpretation",
        "",
        "Self-repair (retry with error feedback) converts failing translations to PASS.",
        "The repair rate varies by initial failure type: BUILD_FAIL errors are generally",
        "more amenable to repair than RUN_FAIL (which often indicates deeper algorithmic",
        "issues). EXTRACTION_FAIL can be repaired by reformatting the response.",
        "",
        "Partial repairs (e.g., BUILD_FAIL → RUN_FAIL) show the LLM understood the",
        "build error and fixed it, but introduced a runtime issue. This demonstrates",
        "iterative improvement capability even when full repair isn't achieved.",
        "",
    ])

    md_path = output_dir / "selfrepair_analysis.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
