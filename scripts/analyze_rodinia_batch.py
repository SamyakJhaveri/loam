#!/usr/bin/env python3
"""Analyze Rodinia batch harness results and produce a results matrix.

Reads individual .json files from results/rodinia/logs/ and produces:
  1. results/rodinia/rodinia_results.json      — structured JSON summary
  2. results/rodinia/results_matrix_rodinia.md — kernel × API matrix

Usage:
    cd /home/samyak/Desktop/parbench_sam
    source env_parbench/bin/activate
    python3 scripts/analyze_rodinia_batch.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")
LOG_DIR = PROJECT_ROOT / "results" / "rodinia" / "logs"
OUT_JSON = PROJECT_ROOT / "results" / "rodinia" / "rodinia_results.json"
OUT_MATRIX = PROJECT_ROOT / "results" / "rodinia" / "results_matrix_rodinia.md"

APIS = ["cuda", "omp", "opencl"]

# All unique kernel slugs (derived from spec filenames)
def get_all_slugs():
    slugs = set()
    for f in LOG_DIR.glob("rodinia-*.json"):
        parts = f.stem.split("-")  # rodinia, slug..., api
        if len(parts) >= 3 and parts[-1] in APIS:
            slug = "-".join(parts[1:-1])
            slugs.add(slug)
    return sorted(slugs)


def load_json_result(slug: str, api: str) -> dict | None:
    path = LOG_DIR / f"rodinia-{slug}-{api}.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  WARNING: Failed to parse {path}: {e}", file=sys.stderr)
        return None


def load_log_text(slug: str, api: str) -> str:
    path = LOG_DIR / f"rodinia-{slug}-{api}.log"
    if not path.exists():
        return ""
    return path.read_text()


def classify_result(slug: str, api: str) -> dict:
    data = load_json_result(slug, api)
    log_text = load_log_text(slug, api)

    result = {
        "spec_id": f"rodinia-{slug}-{api}",
        "slug": slug,
        "api": api,
        "build_status": "MISSING",
        "build_time": 0.0,
        "build_stderr": "",
        "run_status": "MISSING",
        "run_time": 0.0,
        "run_exit_code": None,
        "run_stdout": "",
        "run_stderr": "",
        "verify_status": "MISSING",
        "verify_strategy": "",
        "verify_details": "",
        "metrics": [],
        "failure_category": None,
        "failure_details": None,
    }

    if data is None:
        if log_text:
            result["failure_category"] = "NO_JSON_OUTPUT"
            result["failure_details"] = f"No JSON output. Log: {log_text[:300]}"
        # else: spec not run at all, stays MISSING
        return result

    build = data.get("build", {})
    result["build_status"] = build.get("status", "unknown").upper()
    result["build_time"] = build.get("duration_seconds", 0.0)
    result["build_stderr"] = build.get("stderr", "")

    runs = data.get("runs", {})
    correctness = runs.get("correctness", {})
    result["run_status"] = correctness.get("status", "unknown").upper()
    result["run_time"] = correctness.get("duration_seconds", 0.0)
    result["run_exit_code"] = correctness.get("exit_code")
    result["run_stdout"] = correctness.get("stdout", "")
    result["run_stderr"] = correctness.get("stderr", "")

    ver = data.get("verification", {})
    result["verify_status"] = ver.get("status", "unknown").upper()
    result["verify_strategy"] = ver.get("strategy_used", "")
    result["verify_details"] = ver.get("details", "")

    result["metrics"] = data.get("metrics", [])

    # Failure classification (priority: BUILD > TIMEOUT > RUN > VERIFY)
    if result["build_status"] not in ("PASS", "MISSING"):
        result["failure_category"] = "BUILD_FAIL"
        lines = result["build_stderr"].strip().split("\n")
        errs = [l for l in lines if "error" in l.lower() or "fatal" in l.lower()]
        result["failure_details"] = "\n".join((errs or lines)[-5:])
    elif result["run_status"] == "TIMEOUT":
        result["failure_category"] = "RUN_TIMEOUT"
        result["failure_details"] = result["run_stderr"][:200]
    elif result["run_status"] not in ("PASS", "MISSING"):
        code = result["run_exit_code"]
        stderr = result["run_stderr"]
        if code == -11 or "segfault" in stderr.lower():
            cat = "RUN_SEGFAULT"
        elif code == -6 or "abort" in stderr.lower():
            cat = "RUN_ABORT"
        else:
            cat = f"RUN_FAIL(exit={code})"
        result["failure_category"] = cat
        result["failure_details"] = f"exit={code} | stderr: {stderr[:200]}"
    elif result["verify_status"] not in ("PASS", "MISSING"):
        result["failure_category"] = "VERIFY_FAIL"
        result["failure_details"] = result["verify_details"]

    return result


def build_matrix(all_results: list[dict]) -> str:
    """Build a Kernel × API results matrix in Markdown."""
    # Group by slug
    by_slug: dict[str, dict[str, dict]] = {}
    for r in all_results:
        by_slug.setdefault(r["slug"], {})[r["api"]] = r

    slugs = sorted(by_slug.keys())

    def icon(status: str) -> str:
        return {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏱", "ERROR": "⚠"}.get(status, "❓")

    def cell_build(r: dict | None) -> str:
        if r is None:
            return "—"
        if r["build_status"] == "MISSING":
            return "—"
        ic = icon(r["build_status"])
        t = f"{r['build_time']:.1f}s"
        return f"{ic} {t}"

    def cell_run(r: dict | None) -> str:
        if r is None:
            return "—"
        if r["run_status"] == "MISSING":
            return "—"
        ic = icon(r["run_status"])
        t = f"{r['run_time']:.1f}s"
        return f"{ic} {t}"

    def cell_verify(r: dict | None) -> str:
        if r is None:
            return "—"
        if r["verify_status"] == "MISSING":
            return "—"
        ic = icon(r["verify_status"])
        strat = r["verify_strategy"] or "?"
        return f"{ic} {strat}"

    lines = []
    lines.append("# Rodinia Full Batch — Results Matrix")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
    lines.append(f"**Platform**: Linux x86_64, NVIDIA GeForce RTX 4070 (sm_89), AMD Ryzen 9 7900X")
    lines.append(f"**Total specs**: 60 (22 kernels × CUDA/OMP/OpenCL, some kernels not in all APIs)")
    lines.append("")
    lines.append("Legend: ✅ PASS | ❌ FAIL | ⏱ TIMEOUT | ⚠ ERROR | ❓ UNKNOWN | — not applicable")
    lines.append("")

    # Header
    lines.append("| # | Kernel | CUDA Build | CUDA Run | CUDA Verify | OMP Build | OMP Run | OMP Verify | OCL Build | OCL Run | OCL Verify |")
    lines.append("|---|--------|-----------|----------|-------------|-----------|---------|------------|-----------|---------|------------|")

    for i, slug in enumerate(slugs, 1):
        api_results = by_slug[slug]
        cuda = api_results.get("cuda")
        omp = api_results.get("omp")
        opencl = api_results.get("opencl")

        row = (
            f"| {i} | `{slug}` "
            f"| {cell_build(cuda)} | {cell_run(cuda)} | {cell_verify(cuda)} "
            f"| {cell_build(omp)} | {cell_run(omp)} | {cell_verify(omp)} "
            f"| {cell_build(opencl)} | {cell_run(opencl)} | {cell_verify(opencl)} |"
        )
        lines.append(row)

    lines.append("")

    # Per-API summary footer
    lines.append("## API Summary")
    lines.append("")
    lines.append("| API | Total | Build PASS | Run PASS | Verify PASS | Full PASS |")
    lines.append("|-----|-------|-----------|----------|-------------|-----------|")

    for api in APIS:
        api_results = [r for r in all_results if r["api"] == api and r["build_status"] != "MISSING"]
        total = len(api_results)
        build_pass = sum(1 for r in api_results if r["build_status"] == "PASS")
        run_pass = sum(1 for r in api_results if r["run_status"] == "PASS")
        verify_pass = sum(1 for r in api_results if r["verify_status"] == "PASS")
        full_pass = sum(1 for r in api_results if r["failure_category"] is None and r["build_status"] != "MISSING")
        lines.append(f"| {api.upper()} | {total} | {build_pass}/{total} | {run_pass}/{total} | {verify_pass}/{total} | {full_pass}/{total} |")

    lines.append("")

    # Failures list
    failures = [r for r in all_results if r["failure_category"] is not None]
    if failures:
        lines.append(f"## Failures ({len(failures)} specs)")
        lines.append("")
        lines.append("| Spec | Category | Details |")
        lines.append("|------|----------|---------|")
        for r in sorted(failures, key=lambda x: (x["failure_category"], x["spec_id"])):
            details = (r["failure_details"] or "").replace("\n", " ").replace("|", "\\|")[:150]
            lines.append(f"| `{r['spec_id']}` | {r['failure_category']} | {details} |")
        lines.append("")

    return "\n".join(lines)


def main():
    print(f"Analyzing results from: {LOG_DIR}")

    done_marker = LOG_DIR / "_done.marker"
    if done_marker.exists():
        print(f"  Batch completed: {done_marker.read_text().strip()}")
    else:
        print("  WARNING: Batch may still be running (_done.marker not found)")

    # Discover all slugs from log files
    slugs = get_all_slugs()
    if not slugs:
        # Fall back to discovering from spec files
        for f in sorted((PROJECT_ROOT / "specs").glob("rodinia-*.json")):
            parts = f.stem.split("-")
            if len(parts) >= 3 and parts[-1] in APIS:
                slug = "-".join(parts[1:-1])
                slugs = list(set(list(slugs) + [slug])) if isinstance(slugs, list) else [slug]
        slugs = sorted(set(slugs))

    all_results = []
    for slug in slugs:
        for api in APIS:
            # Check if spec exists (some kernels not in all APIs)
            spec_path = PROJECT_ROOT / "specs" / f"rodinia-{slug}-{api}.json"
            if not spec_path.exists():
                continue
            r = classify_result(slug, api)
            all_results.append(r)

    total = len(all_results)
    full_pass = sum(1 for r in all_results if r["failure_category"] is None and r["build_status"] != "MISSING")
    ran = sum(1 for r in all_results if r["build_status"] != "MISSING")

    # Per-API stats
    by_api = {}
    for api in APIS:
        api_rs = [r for r in all_results if r["api"] == api and r["build_status"] != "MISSING"]
        by_api[api] = {
            "total": len(api_rs),
            "pass": sum(1 for r in api_rs if r["failure_category"] is None),
            "fail": sum(1 for r in api_rs if r["failure_category"] is not None),
            "build_pass": sum(1 for r in api_rs if r["build_status"] == "PASS"),
            "run_pass": sum(1 for r in api_rs if r["run_status"] == "PASS"),
            "verify_pass": sum(1 for r in api_rs if r["verify_status"] == "PASS"),
        }

    # Save JSON
    json_data = {
        "generated": datetime.now().isoformat(),
        "total": total,
        "ran": ran,
        "full_pass": full_pass,
        "by_api": by_api,
        "results": all_results,
    }
    OUT_JSON.write_text(json.dumps(json_data, indent=2, default=str))
    print(f"  JSON: {OUT_JSON}")

    # Save matrix
    matrix_md = build_matrix(all_results)
    OUT_MATRIX.write_text(matrix_md)
    print(f"  Matrix: {OUT_MATRIX}")

    # Console summary
    print(f"\nResults: {full_pass}/{ran} FULL PASS (of {total} specs, {ran} run)")
    for api in APIS:
        s = by_api[api]
        print(f"  {api.upper():6s}: {s['pass']}/{s['total']} pass  "
              f"(build={s['build_pass']}, run={s['run_pass']}, verify={s['verify_pass']})")

    failures = [r for r in all_results if r["failure_category"] is not None]
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for r in failures:
            print(f"  {r['spec_id']}: {r['failure_category']} — {(r['failure_details'] or '')[:80]}")


if __name__ == "__main__":
    main()
