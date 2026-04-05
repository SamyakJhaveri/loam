#!/usr/bin/env python3
"""Quantitative Findings — SC26 ParBench paper.

Computes 14 quantitative dimensions from the full 1,248-file Qwen evaluation
dataset. This plan covers dimensions 1-5 (aggregate pass rates, per-direction
rates, direction asymmetry, augmentation trends, failure taxonomy) plus the
provenance framework (dimension 14).

Produces:
  results/analysis/quantitative_findings.json
  results/analysis/quantitative_findings.md

Usage:
    python3 scripts/analysis/quantitative_findings.py \\
        --project-root /home/samyak/Desktop/parbench_sam -v
    python3 scripts/analysis/quantitative_findings.py \\
        --project-root . --validate
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# All 8 KNOWN_FAIL specs: 6 Rodinia + 2 HeCBench
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
    "hecbench-stencil1d-omp_target",
    "hecbench-scan-omp_target",
})

STANDARD_DIRECTIONS: list[str] = [
    "cuda-to-omp", "omp-to-cuda",
    "cuda-to-opencl", "opencl-to-cuda",
    "omp-to-opencl", "opencl-to-omp",
]

CASE_STUDY_DIRECTIONS: list[str] = [
    "cuda-to-omp_target", "omp_target-to-cuda",
]

# Together AI pricing (Qwen 3.5 397B)
TOGETHER_INPUT_PRICE_PER_M = 0.60
TOGETHER_OUTPUT_PRICE_PER_M = 3.60

ALPHA = 0.05

# Valid overall_status values
STATUS_VALUES = ("PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL")


# ---------------------------------------------------------------------------
# Provenance helper (Dimension 14)
# ---------------------------------------------------------------------------

def make_finding(
    value,
    source: str,
    files_matched: int,
    derivation: str,
    ci_lower=None,
    ci_upper=None,
    ci_level: float = 0.95,
    n=None,
) -> dict:
    """Wrap a computed value with provenance metadata.

    All numeric rates stored as decimals 0-1.
    """
    finding: dict = {
        "value": value,
        "source": source,
        "files_matched": files_matched,
        "derivation": derivation,
    }
    if ci_lower is not None:
        finding["ci_lower"] = ci_lower
    if ci_upper is not None:
        finding["ci_upper"] = ci_upper
    if ci_lower is not None or ci_upper is not None:
        finding["ci_level"] = ci_level
    if n is not None:
        finding["n"] = n
    return finding


# ---------------------------------------------------------------------------
# Wilson score CI
# ---------------------------------------------------------------------------

def wilson_ci(passes: int, total: int, alpha: float = ALPHA) -> dict:
    """Wilson score confidence interval for a binomial proportion."""
    if total == 0:
        return {"value": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "n": 0, "ci_level": 0.95}

    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom

    return {
        "value": round(p_hat, 4),
        "ci_lower": round(max(0.0, center - spread), 4),
        "ci_upper": round(min(1.0, center + spread), 4),
        "n": total,
        "ci_level": 0.95,
    }


# ---------------------------------------------------------------------------
# Cohen's h effect size
# ---------------------------------------------------------------------------

def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for two proportions."""
    return 2 * math.asin(math.sqrt(max(0.0, min(1.0, p1)))) - \
           2 * math.asin(math.sqrt(max(0.0, min(1.0, p2))))


# ---------------------------------------------------------------------------
# Cochran-Armitage trend test
# ---------------------------------------------------------------------------

def cochran_armitage_trend(
    pass_counts: list[int],
    total_counts: list[int],
    scores: list[int] | None = None,
) -> dict:
    """Cochran-Armitage test for trend in binomial proportions."""
    k = len(pass_counts)
    if scores is None:
        scores = list(range(k))
    n = np.array(total_counts, dtype=float)
    r = np.array(pass_counts, dtype=float)
    s = np.array(scores, dtype=float)
    N = n.sum()
    R = r.sum()

    if N == 0:
        return {"z": 0.0, "p_value": 1.0, "trend_direction": "none"}

    p_bar = R / N
    t_bar = np.sum(n * s) / N

    numerator = np.sum(s * (r - n * p_bar))
    denominator_sq = p_bar * (1 - p_bar) * (np.sum(n * s**2) - N * t_bar**2)

    if denominator_sq <= 0:
        return {"z": 0.0, "p_value": 1.0, "trend_direction": "none"}

    denominator = math.sqrt(float(denominator_sq))
    z = float(numerator / denominator)
    p_value = float(2 * sp_stats.norm.sf(abs(z)))

    return {
        "z": round(z, 4),
        "p_value": round(p_value, 6),
        "trend_direction": "decreasing" if z < 0 else "increasing" if z > 0 else "none",
    }


# ---------------------------------------------------------------------------
# McNemar exact test
# ---------------------------------------------------------------------------

def mcnemar_exact(pairs: list[tuple[bool, bool]]) -> dict:
    """McNemar's exact test on paired boolean observations.

    pairs: list of (forward_pass, reverse_pass) tuples.
    """
    a = sum(1 for (f, r) in pairs if f and r)       # both pass
    b = sum(1 for (f, r) in pairs if not f and r)    # reverse only
    c = sum(1 for (f, r) in pairs if f and not r)    # forward only
    d = sum(1 for (f, r) in pairs if not f and not r)  # both fail
    discordant = b + c

    if discordant == 0:
        p_value = 1.0
        method = "exact"
    elif discordant < 25:
        binom_result = sp_stats.binomtest(b, discordant, 0.5, alternative="two-sided")
        p_value = float(binom_result.pvalue)
        method = "exact"
    else:
        chi2_val = (abs(b - c) - 1) ** 2 / discordant if discordant > 0 else 0
        p_value = float(1 - sp_stats.chi2.cdf(chi2_val, df=1))
        method = "chi-squared"

    n_p = len(pairs)
    fwd_pass_count = a + c
    rev_pass_count = a + b
    fwd_rate = fwd_pass_count / n_p if n_p > 0 else 0
    rev_rate = rev_pass_count / n_p if n_p > 0 else 0

    h = cohens_h(fwd_rate, rev_rate)
    abs_h = abs(h)
    effect = "small" if abs_h < 0.20 else "medium" if abs_h < 0.80 else "large"

    return {
        "n_paired": n_p,
        "forward_pass_rate": round(fwd_rate, 4),
        "reverse_pass_rate": round(rev_rate, 4),
        "table": {"both_pass": a, "reverse_only": b, "forward_only": c, "both_fail": d},
        "discordant": discordant,
        "method": method,
        "p_value": round(p_value, 6),
        "cohens_h": round(h, 4),
        "effect_size": effect,
    }


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def _augment_level_from_filename(stem: str) -> int:
    """Extract augmentation level from result file stem.

    Convention: {src_id}-to-{tgt_id}-L{N}.json       -> N
                {src_id}-to-{tgt_id}-L{N}-s{M}.json  -> N
                {src_id}-to-{tgt_id}.json             -> 0
                {src_id}-to-{tgt_id}-s{M}.json        -> 0
    """
    m = re.search(r"-L(\d+)(?:-s\d+)?$", stem)
    return int(m.group(1)) if m else 0


def _sample_id_from_filename(stem: str) -> int | None:
    """Extract sample_id from result file stem (-s{N} suffix), or None."""
    m = re.search(r"-s(\d+)$", stem)
    return int(m.group(1)) if m else None


def _direction_from_data(data: dict) -> str:
    """Infer translation direction from source_spec/target_spec fields."""
    src = data.get("source_spec", "")
    tgt = data.get("target_spec", "")
    src_api = src.rsplit("-", 1)[-1] if src else "unknown"
    tgt_api = tgt.rsplit("-", 1)[-1] if tgt else "unknown"
    return f"{src_api}-to-{tgt_api}"


def _kernel_from_spec(spec_name: str) -> str:
    """Extract kernel name from spec ID like 'rodinia-bfs-cuda' -> 'bfs'."""
    parts = spec_name.split("-")
    if len(parts) < 3:
        return spec_name
    return "-".join(parts[1:-1])


def _suite_from_spec(spec_name: str) -> str:
    """Extract suite from spec ID like 'rodinia-bfs-cuda' -> 'rodinia'."""
    parts = spec_name.split("-")
    return parts[0] if parts else spec_name


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_results(results_dir: Path, verbose: bool = False) -> list[dict]:
    """Load all result JSONs from a single model directory."""
    records = []
    skipped = 0

    for json_file in sorted(results_dir.glob("*.json")):
        basename = json_file.name
        # Skip non-result files
        if basename.startswith("batch_") or basename == "eval_summary.json":
            continue

        try:
            with open(json_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            if verbose:
                print(f"  WARNING: Could not read {json_file}: {e}", file=sys.stderr)
            skipped += 1
            continue

        # Enrich with parsed metadata
        stem = json_file.stem
        data["_filename"] = basename
        data["_stem"] = stem

        # Ensure augment_level is set (from file or filename)
        if "augment_level" not in data or data["augment_level"] is None:
            data["augment_level"] = _augment_level_from_filename(stem)

        # Ensure sample_id is set
        if "sample_id" not in data or data.get("sample_id") is None:
            data["sample_id"] = _sample_id_from_filename(stem)

        # Ensure direction is set
        if "direction" not in data or not data.get("direction"):
            data["direction"] = _direction_from_data(data)

        # Ensure kernel is set
        if "kernel" not in data or not data.get("kernel"):
            data["kernel"] = _kernel_from_spec(data.get("source_spec", ""))

        # Ensure _suite is set
        data["_suite"] = _suite_from_spec(data.get("source_spec", ""))

        # Ensure temperature is set
        if "temperature" not in data or data["temperature"] is None:
            data["temperature"] = 0.0

        records.append(data)

    if verbose:
        print(f"  Loaded {len(records)} result files ({skipped} skipped)")

    return records


def exclude_known_fail(records: list[dict]) -> list[dict]:
    """Remove records involving KNOWN_FAIL specs (all 8)."""
    return [
        r for r in records
        if r.get("source_spec") not in EXCLUDED_SPECS
        and r.get("target_spec") not in EXCLUDED_SPECS
    ]


def split_campaigns(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split records into Campaign 1 (temp=0.0) and Campaign 2 (temp>0).

    Campaign 1: Primary evaluation (deterministic, temp=0.0)
    Campaign 2: pass@k evaluation (temp=0.7)
    """
    c1 = []
    c2 = []
    for r in records:
        temp = r.get("temperature", 0.0) or 0.0
        if temp == 0.0:
            c1.append(r)
        else:
            c2.append(r)
    return c1, c2


# ---------------------------------------------------------------------------
# BUILD_FAIL regex patterns (priority order, first match wins)
# ---------------------------------------------------------------------------

_BUILD_FAIL_PATTERNS: list[tuple[str, re.Pattern, object]] = [
    (
        "retained_cuda_api",
        re.compile(
            r"cudaMalloc|cudaFree|cudaMemcpy|cudaMemset|cudaDeviceSynchronize"
            r"|__global__|__device__|__shared__"
            r"|<<<|>>>"
            r"|cudaGetLastError|cudaSetDevice|cudaGetDevice"
            r"|cuda_runtime\.h|cudaError_t|cudaSuccess"
            r"|blockIdx|threadIdx|blockDim|gridDim"
            r"|__syncthreads|atomicAdd\b|atomicSub\b|atomicExch\b"
            r"|atomicMin\b|atomicMax\b|atomicCAS\b"
            r"|calling a __device__ function.*from a __host__",
            re.IGNORECASE,
        ),
        lambda direction: not direction.endswith("-to-cuda"),
    ),
    (
        "retained_cuda_types",
        re.compile(
            r"\bfloat3\b|\bfloat4\b|\bint3\b|\bint4\b|\bdouble3\b|\bdouble4\b"
            r"|\bdim3\b|cudaStream_t|cudaEvent_t"
            r"|texture<|surf<|__constant__",
            re.IGNORECASE,
        ),
        lambda direction: not direction.endswith("-to-cuda"),
    ),
    (
        "retained_opencl_api",
        re.compile(
            r"clCreateBuffer|clEnqueueWriteBuffer|clEnqueueReadBuffer"
            r"|clBuildProgram|clCreateKernel|clSetKernelArg"
            r"|clEnqueueNDRangeKernel|clReleaseMemObject"
            r"|get_global_id|get_local_id|__kernel\b|cl_mem\b",
            re.IGNORECASE,
        ),
        lambda direction: not direction.endswith("-to-opencl"),
    ),
    (
        "missing_header",
        re.compile(
            r"No such file or directory"
            r"|fatal error:.*not found"
            r"|cannot find.*include",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "linker_error",
        re.compile(
            r"undefined reference to"
            r"|multiple definition of"
            r"|collect2:.*error"
            r"|ld returned \d+ exit",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "undeclared_identifier",
        re.compile(
            r"\bundeclared\b"
            r"|was not declared in this scope"
            r"|identifier.*is undefined"
            r"|does not name a type"
            r"|unknown type name"
            r"|has no member named",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "type_mismatch",
        re.compile(
            r"cannot convert"
            r"|incompatible type"
            r"|no matching function"
            r"|conflicting types"
            r"|array subscript is not an integer"
            r"|no viable conversion"
            r"|no instance of overloaded"
            r"|invalid.*operands? to binary"
            r"|cannot be used to initialize",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "syntax_error",
        re.compile(
            r"expected.*before"
            r"|expected.*token"
            r"|expected a [\"'(]|expected a declaration"
            r"|stray.*in program"
            r"|parse error"
            r"|unterminated"
            r"|invalid.*form.*pragma"
            r"|is not valid for.*#pragma"
            r"|must be closely nested"
            r"|too few arguments to function"
            r"|too many arguments (?:to function|in function call)"
            r"|no storage class or type specifier"
            r"|missing closing quote",
            re.IGNORECASE,
        ),
        None,
    ),
    (
        "implicit_declaration",
        re.compile(r"implicit declaration of function", re.IGNORECASE),
        None,
    ),
    (
        "redefinition",
        re.compile(
            r"redefinition of"
            r"|redeclaration of"
            r"|duplicate member"
            r"|previously declared here",
            re.IGNORECASE,
        ),
        None,
    ),
]

# RUN_FAIL classification checks
_RUN_FAIL_CHECKS: list[tuple[str, object]] = [
    (
        "wrong_checksum",
        lambda ec, se, so: bool(
            re.search(r"INAVALID CHECKSUM|INVALID CHECKSUM", so or "", re.IGNORECASE)
        ),
    ),
    (
        "wrong_args",
        lambda ec, se, so: bool(
            re.search(r"[Uu]sage:", se or "")
            or re.search(r"[Uu]sage:", so or "")
            or re.search(r"<grid_rows|<sim_time|<temp_file|<power_file|<penalty>", se or "")
            or re.search(r"<inputfile>|<num of frames>", so or "")
        ),
    ),
    (
        "opencl_jit_error",
        lambda ec, se, so: bool(
            re.search(r"\d+\s+errors? generated", se or "")
        ),
    ),
    (
        "simulation_mode_unsupported",
        lambda ec, se, so: bool(
            re.search(
                r"not implemented.*OpenMP|History-based simulation not implemented",
                so or "",
            )
        ),
    ),
    (
        "gpu_memory_error",
        lambda ec, se, so: bool(
            re.search(r"illegal memory access|GPUassert", se or "")
            or re.search(r"illegal memory access|GPUassert", so or "")
        ),
    ),
    (
        "segfault",
        lambda ec, se, so: ec == -11
        or bool(re.search(r"Segmentation fault|SIGSEGV|signal 11", se or "")),
    ),
    (
        "abort",
        lambda ec, se, so: ec == -6
        or bool(re.search(r"stack smashing|SIGABRT|Aborted|signal 6", se or "")),
    ),
    (
        "timeout",
        lambda ec, se, so: bool(
            re.search(r"TIMEOUT|exceeded timeout|killed.*timeout", se or "")
            or re.search(r"TIMEOUT", so or "")
        ),
    ),
    (
        "data_file_missing",
        lambda ec, se, so: bool(
            re.search(r"error opening|file not found|cannot open", so or "")
            or re.search(r"error opening|file not found|cannot open", se or "")
        ),
    ),
    (
        "wrong_exit_code",
        lambda ec, se, so: ec is not None and ec != 0,
    ),
]

# EXTRACTION_FAIL patterns
_EXTRACTION_FAIL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("no_code_blocks", re.compile(r"did not contain parseable code", re.IGNORECASE)),
    ("missing_files", re.compile(
        r"expected file|not found in output|missing.*file|could not find|no .* file",
        re.IGNORECASE,
    )),
]


def _classify_build_fail(data: dict) -> str:
    """Return primary BUILD_FAIL subcategory."""
    snippet = data.get("build_error_snippet") or ""
    direction = data.get("direction") or _direction_from_data(data)

    # Use final attempt's snippet if available
    attempts = data.get("attempts") or []
    if attempts:
        last_snippet = attempts[-1].get("build_error_snippet")
        if last_snippet:
            snippet = last_snippet

    for cat_name, pattern, direction_filter in _BUILD_FAIL_PATTERNS:
        if direction_filter is not None and not direction_filter(direction):
            continue
        if pattern.search(snippet):
            return cat_name

    return "other_build"


def _classify_run_fail(data: dict) -> str:
    """Return primary RUN_FAIL subcategory."""
    exit_code = data.get("run_exit_code")
    stderr = data.get("run_stderr_snippet") or ""
    stdout = data.get("run_stdout_snippet") or ""

    for cat_name, check_fn in _RUN_FAIL_CHECKS:
        if check_fn(exit_code, stderr, stdout):
            return cat_name

    return "other_runtime"


def _classify_extraction_fail(data: dict) -> str:
    """Return primary EXTRACTION_FAIL subcategory."""
    error_msg = data.get("error_message") or ""

    for cat_name, pattern in _EXTRACTION_FAIL_PATTERNS:
        if pattern.search(error_msg):
            return cat_name

    return "malformed_output"


def _classify_verify_fail(data: dict) -> str:
    """Return primary VERIFY_FAIL subcategory."""
    verify_status = data.get("verify_status") or ""
    stdout = data.get("run_stdout_snippet") or ""

    if verify_status == "pass":
        return "pass_overall_mislabel"
    elif verify_status == "error":
        return "verification_error"
    elif verify_status == "fail":
        if not stdout.strip():
            return "missing_output"
        return "wrong_numerical_output"
    return "other_verify"


# ---------------------------------------------------------------------------
# Dimension 1: Aggregate pass rates
# ---------------------------------------------------------------------------

def compute_aggregate_pass_rates(records: list[dict]) -> dict:
    """Compute aggregate pass rates by suite and overall.

    Returns dict with 'overall' and 'per_suite' keys.
    """
    total = len(records)
    passes = sum(1 for r in records if r.get("overall_status") == "PASS")
    ci = wilson_ci(passes, total)

    overall = make_finding(
        value=ci["value"],
        source="computed",
        files_matched=total,
        derivation="wilson_ci(PASS count, total valid records)",
        ci_lower=ci["ci_lower"],
        ci_upper=ci["ci_upper"],
        n=total,
    )

    # Per suite
    by_suite: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_suite[r.get("_suite", "unknown")].append(r)

    per_suite = {}
    for suite_name, recs in sorted(by_suite.items()):
        s_total = len(recs)
        s_passes = sum(1 for r in recs if r.get("overall_status") == "PASS")
        s_ci = wilson_ci(s_passes, s_total)
        per_suite[suite_name] = make_finding(
            value=s_ci["value"],
            source="computed",
            files_matched=s_total,
            derivation=f"wilson_ci(PASS count, total) for suite={suite_name}",
            ci_lower=s_ci["ci_lower"],
            ci_upper=s_ci["ci_upper"],
            n=s_total,
        )

    return {"overall": overall, "per_suite": per_suite}


# ---------------------------------------------------------------------------
# Dimension 2: Per-direction pass rates
# ---------------------------------------------------------------------------

def compute_direction_pass_rates(records: list[dict]) -> dict:
    """Compute pass rates per direction (L0 only).

    Separates standard vs case_study directions.
    """
    # L0 records only
    l0 = [r for r in records if r.get("augment_level", 0) == 0]

    by_dir: dict[str, list[dict]] = defaultdict(list)
    for r in l0:
        by_dir[r.get("direction", "unknown")].append(r)

    standard = {}
    case_study = {}

    for d, recs in sorted(by_dir.items()):
        d_total = len(recs)
        d_passes = sum(1 for r in recs if r.get("overall_status") == "PASS")
        d_ci = wilson_ci(d_passes, d_total)
        finding = make_finding(
            value=d_ci["value"],
            source="computed",
            files_matched=d_total,
            derivation=f"wilson_ci(PASS count, total) for direction={d}, L0 only",
            ci_lower=d_ci["ci_lower"],
            ci_upper=d_ci["ci_upper"],
            n=d_total,
        )

        if d in STANDARD_DIRECTIONS:
            standard[d] = finding
        elif d in CASE_STUDY_DIRECTIONS:
            case_study[d] = finding
        else:
            # Unknown direction, add to standard
            standard[d] = finding

    return {"standard": standard, "case_study": case_study}


# ---------------------------------------------------------------------------
# Dimension 3: Direction asymmetry (McNemar at L0)
# ---------------------------------------------------------------------------

def compute_direction_asymmetry(records: list[dict]) -> dict:
    """McNemar exact test for direction asymmetry at L0 only.

    Pairs on (suite, kernel) to avoid cross-suite false pairs.
    """
    # Only L0 records
    l0 = [r for r in records if r.get("augment_level", 0) == 0]

    # Build lookup: (suite, kernel, direction) -> passed
    lookup: dict[tuple[str, str, str], bool] = {}
    for r in l0:
        suite = r.get("_suite", "unknown")
        kernel = r.get("kernel", "?")
        direction = r.get("direction", "unknown")
        passed = r.get("overall_status") == "PASS"
        lookup[(suite, kernel, direction)] = passed

    # Identify direction pairs
    directions = {r.get("direction", "") for r in l0 if r.get("direction")}
    pair_map: dict[tuple[str, str], tuple[str, str]] = {}
    for d in directions:
        parts = d.split("-to-")
        if len(parts) == 2:
            reverse = f"{parts[1]}-to-{parts[0]}"
            if reverse in directions:
                key = tuple(sorted([d, reverse]))
                if key not in pair_map:
                    pair_map[key] = (d, reverse)

    n_tests = max(len(pair_map), 1)
    alpha_corrected = ALPHA / n_tests

    results = {}
    for (d_fwd, d_rev) in pair_map.values():
        pairs: list[tuple[bool, bool]] = []

        # Find (suite, kernel) combos present in forward direction
        fwd_keys = {(s, k) for (s, k, d) in lookup if d == d_fwd}
        for (suite, kernel) in fwd_keys:
            fwd_pass = lookup.get((suite, kernel, d_fwd))
            rev_pass = lookup.get((suite, kernel, d_rev))
            if fwd_pass is not None and rev_pass is not None:
                pairs.append((fwd_pass, rev_pass))

        if not pairs:
            continue

        test = mcnemar_exact(pairs)
        test["alpha_corrected"] = round(alpha_corrected, 6)
        test["significant"] = test["p_value"] < alpha_corrected

        finding = make_finding(
            value={
                "forward": d_fwd,
                "reverse": d_rev,
                "test_result": test,
            },
            source="computed",
            files_matched=test["n_paired"] * 2,
            derivation=f"mcnemar_exact paired on (suite, kernel) for {d_fwd} vs {d_rev}, L0 only",
        )
        results[f"{d_fwd} vs {d_rev}"] = finding

    return results


# ---------------------------------------------------------------------------
# Dimension 4: Augmentation trends
# ---------------------------------------------------------------------------

def compute_augmentation_trends(records: list[dict]) -> dict:
    """Cochran-Armitage trend test per-direction and aggregate.

    Includes Cohen's h between adjacent levels.
    """
    result = {}

    # --- Aggregate ---
    agg = _compute_augmentation_for_subset(records, "all records")
    result["aggregate"] = agg

    # --- Per direction ---
    by_dir: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_dir[r.get("direction", "unknown")].append(r)

    per_direction = {}
    for d, recs in sorted(by_dir.items()):
        per_direction[d] = _compute_augmentation_for_subset(recs, f"direction={d}")

    result["per_direction"] = per_direction

    return result


def _compute_augmentation_for_subset(records: list[dict], label: str) -> dict:
    """Compute augmentation trend for a subset of records."""
    by_level: dict[int, list[dict]] = defaultdict(list)
    for r in records:
        by_level[r.get("augment_level", 0)].append(r)

    levels_sorted = sorted(by_level.keys())
    if not levels_sorted:
        return {"error": f"No records for {label}"}

    # Per-level pass rates
    per_level = {}
    for lv in levels_sorted:
        recs = by_level[lv]
        passes = sum(1 for r in recs if r.get("overall_status") == "PASS")
        ci = wilson_ci(passes, len(recs))
        per_level[f"L{lv}"] = ci

    # Adequate sample size check (n >= 10 per level)
    adequate = all(len(by_level[lv]) >= 10 for lv in levels_sorted)

    # Cochran-Armitage trend test
    pass_counts = [
        sum(1 for r in by_level[lv] if r.get("overall_status") == "PASS")
        for lv in levels_sorted
    ]
    total_counts = [len(by_level[lv]) for lv in levels_sorted]

    ca = cochran_armitage_trend(pass_counts, total_counts, scores=levels_sorted)
    ca["significant"] = ca["p_value"] < ALPHA
    ca["levels"] = levels_sorted
    ca["pass_counts"] = pass_counts
    ca["total_counts"] = total_counts

    # Cohen's h between adjacent levels
    rates = [p / t if t > 0 else 0 for p, t in zip(pass_counts, total_counts)]
    cohens_h_adjacent = {}
    for i in range(len(levels_sorted) - 1):
        lv_a = levels_sorted[i]
        lv_b = levels_sorted[i + 1]
        h = cohens_h(rates[i + 1], rates[i])
        cohens_h_adjacent[f"L{lv_a}_to_L{lv_b}"] = round(h, 4)

    return {
        "per_level": per_level,
        "adequate_sample_size": adequate,
        "cochran_armitage": ca,
        "cohens_h_adjacent": cohens_h_adjacent,
    }


# ---------------------------------------------------------------------------
# Dimension 5: Failure taxonomy
# ---------------------------------------------------------------------------

def compute_failure_taxonomy(records: list[dict]) -> dict:
    """Classify failure types with subcategories.

    Groups by overall_status, then subcategorizes BUILD_FAIL, RUN_FAIL,
    VERIFY_FAIL, and EXTRACTION_FAIL.
    """
    total = len(records)
    failures = [r for r in records if r.get("overall_status") != "PASS"]
    total_failures = len(failures)

    # Count by status
    status_counts: dict[str, int] = Counter()
    for r in records:
        status_counts[r.get("overall_status", "UNKNOWN")] += 1

    # Classify each failure type
    by_status: dict[str, dict] = {}

    # BUILD_FAIL
    build_fails = [r for r in records if r.get("overall_status") == "BUILD_FAIL"]
    bf_subcats: dict[str, int] = Counter()
    for r in build_fails:
        bf_subcats[_classify_build_fail(r)] += 1
    by_status["BUILD_FAIL"] = {
        "count": len(build_fails),
        "subcategories": dict(bf_subcats),
    }

    # RUN_FAIL
    run_fails = [r for r in records if r.get("overall_status") == "RUN_FAIL"]
    rf_subcats: dict[str, int] = Counter()
    for r in run_fails:
        rf_subcats[_classify_run_fail(r)] += 1
    by_status["RUN_FAIL"] = {
        "count": len(run_fails),
        "subcategories": dict(rf_subcats),
    }

    # VERIFY_FAIL
    verify_fails = [r for r in records if r.get("overall_status") == "VERIFY_FAIL"]
    vf_subcats: dict[str, int] = Counter()
    for r in verify_fails:
        vf_subcats[_classify_verify_fail(r)] += 1
    by_status["VERIFY_FAIL"] = {
        "count": len(verify_fails),
        "subcategories": dict(vf_subcats),
    }

    # EXTRACTION_FAIL
    extraction_fails = [r for r in records if r.get("overall_status") == "EXTRACTION_FAIL"]
    ef_subcats: dict[str, int] = Counter()
    for r in extraction_fails:
        ef_subcats[_classify_extraction_fail(r)] += 1
    by_status["EXTRACTION_FAIL"] = {
        "count": len(extraction_fails),
        "subcategories": dict(ef_subcats),
    }

    # Per-suite failure taxonomy
    per_suite: dict[str, dict] = {}
    by_suite: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_suite[r.get("_suite", "unknown")].append(r)
    for suite_name, recs in sorted(by_suite.items()):
        suite_counts: dict[str, int] = Counter()
        for r in recs:
            suite_counts[r.get("overall_status", "UNKNOWN")] += 1
        per_suite[suite_name] = {
            "total": len(recs),
            "status_counts": dict(suite_counts),
        }

    # Top-3 build error subcategories
    top_3_build = sorted(bf_subcats.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "total_records": total,
        "total_failures": total_failures,
        "status_counts": dict(status_counts),
        "by_status": by_status,
        "per_suite": per_suite,
        "top_3_build_subcategories": [
            {"subcategory": name, "count": count} for name, count in top_3_build
        ],
    }


# ---------------------------------------------------------------------------
# Output assembly
# ---------------------------------------------------------------------------

def build_metadata(
    all_records: list[dict],
    valid_records: list[dict],
    c1: list[dict],
    c2: list[dict],
    args: argparse.Namespace,
) -> dict:
    """Build metadata section with file counts, timestamps, git hash."""
    # Git hash
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(args.project_root),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_hash = "unknown"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_hash": git_hash,
        "project_root": str(args.project_root),
        "model": "together-qwen-3.5-397b-a17b",
        "excluded_specs": sorted(EXCLUDED_SPECS),
        "excluded_specs_count": len(EXCLUDED_SPECS),
        "file_counts": {
            "total_on_disk": len(all_records),
            "excluded_known_fail": len(all_records) - len(valid_records),
            "valid_after_exclusion": len(valid_records),
            "campaign_1_valid": len(c1),
            "campaign_2_valid": len(c2),
        },
        "campaign_1_description": "Primary evaluation (temperature=0.0, deterministic)",
        "campaign_2_description": "pass@k evaluation (temperature=0.7, stochastic sampling)",
    }


def build_paper_claims(c1_results: dict, c2_results: dict, project_root: Path) -> list[dict]:
    """Build stub paper claims list.

    Fully populated in Plan 02 after all 14 dimensions computed.
    """
    return [
        {
            "claim_id": "CLAIM-STUB-001",
            "paper_location": "TBD",
            "json_path": "TBD",
            "scope": "dimensions_1_through_5",
            "note": "Paper claims will be fully populated in Plan 02",
        }
    ]


# ---------------------------------------------------------------------------
# Cross-check against existing analysis files
# ---------------------------------------------------------------------------

def cross_check(
    c1_results: dict,
    c2_results: dict,
    project_root: Path,
    verbose: bool,
) -> dict:
    """Cross-check computed values against existing analysis JSONs.

    Compares against paper_data.json, statistical_analysis.json, error_taxonomy.json.
    Returns dict with warnings list and pass/fail status.
    """
    warnings = []
    checks_run = 0

    analysis_dir = project_root / "results" / "analysis"

    # --- Check against paper_data.json ---
    paper_data_path = analysis_dir / "paper_data.json"
    if paper_data_path.exists():
        try:
            pd = json.loads(paper_data_path.read_text())
            checks_run += 1

            # File count check (note: paper_data.json uses 6 excluded, we use 8)
            pd_total = (pd.get("file_counts") or {}).get("total_on_disk", 0)
            our_total = c1_results.get("_metadata", {}).get("total_on_disk", 0)
            if pd_total != our_total and pd_total > 0 and our_total > 0:
                warnings.append(
                    f"INFO: paper_data.json total_on_disk={pd_total}, "
                    f"our total={our_total} (expected match)"
                )

            # Campaign 1 overall pass rate (paper_data.json uses 6 exclusions = 710 records)
            pd_c1_rate = (pd.get("primary_campaign") or {}).get("overall", {}).get("pass_rate")
            our_c1_overall = c1_results.get("aggregate_pass_rates", {}).get("overall", {})
            our_c1_rate = our_c1_overall.get("value")

            if pd_c1_rate is not None and our_c1_rate is not None:
                checks_run += 1
                diff = abs(pd_c1_rate - our_c1_rate)
                if diff > 0.05:
                    warnings.append(
                        f"WARNING: C1 overall pass rate mismatch: paper_data={pd_c1_rate}, "
                        f"ours={our_c1_rate} (diff={diff:.4f}, >5%). "
                        f"Note: different KNOWN_FAIL exclusion count (6 vs 8)."
                    )
                elif diff > 0.001:
                    warnings.append(
                        f"INFO: C1 overall pass rate minor diff: paper_data={pd_c1_rate}, "
                        f"ours={our_c1_rate} (diff={diff:.4f}). "
                        f"Expected due to 8 vs 6 KNOWN_FAIL exclusions."
                    )

        except (json.JSONDecodeError, OSError) as e:
            warnings.append(f"WARNING: Could not read paper_data.json: {e}")

    # --- Check against error_taxonomy.json ---
    taxonomy_path = analysis_dir / "error_taxonomy.json"
    if taxonomy_path.exists():
        try:
            et = json.loads(taxonomy_path.read_text())
            checks_run += 1

            # Total results check (error_taxonomy.json includes KNOWN_FAIL)
            et_total = et.get("total_results", 0)
            if verbose:
                print(f"  Cross-check: error_taxonomy.json total_results={et_total}")

        except (json.JSONDecodeError, OSError) as e:
            warnings.append(f"WARNING: Could not read error_taxonomy.json: {e}")

    # --- Check against statistical_analysis.json ---
    stat_path = analysis_dir / "statistical_analysis.json"
    if stat_path.exists():
        try:
            sa = json.loads(stat_path.read_text())
            checks_run += 1

            if verbose:
                print(f"  Cross-check: statistical_analysis.json total_records={sa.get('total_records')}")

        except (json.JSONDecodeError, OSError) as e:
            warnings.append(f"WARNING: Could not read statistical_analysis.json: {e}")

    return {
        "checks_run": checks_run,
        "warnings": warnings,
        "status": "pass" if not any(w.startswith("WARNING") for w in warnings) else "warn",
    }


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def write_markdown(output: dict, path: Path) -> None:
    """Write quantitative findings as markdown."""
    lines = []
    lines.append("# Quantitative Findings — SC26 ParBench")
    lines.append("")
    lines.append(f"Generated: {output.get('metadata', {}).get('generated_at', 'unknown')}")
    lines.append(f"Git hash: {output.get('metadata', {}).get('git_hash', 'unknown')}")
    lines.append("")

    meta = output.get("metadata", {})
    fc = meta.get("file_counts", {})
    lines.append("## File Counts")
    lines.append("")
    lines.append(f"- Total on disk: {fc.get('total_on_disk', '?')}")
    lines.append(f"- Excluded (KNOWN_FAIL, 8 specs): {fc.get('excluded_known_fail', '?')}")
    lines.append(f"- Valid after exclusion: {fc.get('valid_after_exclusion', '?')}")
    lines.append(f"- Campaign 1 (temp=0.0): {fc.get('campaign_1_valid', '?')}")
    lines.append(f"- Campaign 2 (temp=0.7): {fc.get('campaign_2_valid', '?')}")
    lines.append("")

    # Campaign 1
    c1 = output.get("campaign_1", {})
    lines.append("---")
    lines.append("")
    lines.append("## Campaign 1: Primary Evaluation (temperature=0.0)")
    lines.append("")

    # Dimension 1: Aggregate pass rates
    agg = c1.get("aggregate_pass_rates", {})
    lines.append("### Dimension 1: Aggregate Pass Rates")
    lines.append("")
    overall = agg.get("overall", {})
    lines.append(f"**Overall:** {_pct(overall.get('value'))} "
                 f"[{_pct(overall.get('ci_lower'))}, {_pct(overall.get('ci_upper'))}] "
                 f"(n={overall.get('n', '?')})")
    lines.append("")

    per_suite = agg.get("per_suite", {})
    if per_suite:
        lines.append("| Suite | Pass Rate | 95% CI | n |")
        lines.append("|-------|-----------|--------|---|")
        for suite, data in sorted(per_suite.items()):
            lines.append(f"| {suite} | {_pct(data.get('value'))} | "
                         f"[{_pct(data.get('ci_lower'))}, {_pct(data.get('ci_upper'))}] | "
                         f"{data.get('n', '?')} |")
        lines.append("")

    # Dimension 2: Per-direction pass rates
    dir_rates = c1.get("direction_pass_rates", {})
    lines.append("### Dimension 2: Per-Direction Pass Rates (L0 only)")
    lines.append("")

    std = dir_rates.get("standard", {})
    if std:
        lines.append("**Standard directions:**")
        lines.append("")
        lines.append("| Direction | Pass Rate | 95% CI | n |")
        lines.append("|-----------|-----------|--------|---|")
        for d, data in sorted(std.items()):
            lines.append(f"| {d} | {_pct(data.get('value'))} | "
                         f"[{_pct(data.get('ci_lower'))}, {_pct(data.get('ci_upper'))}] | "
                         f"{data.get('n', '?')} |")
        lines.append("")

    cs = dir_rates.get("case_study", {})
    if cs:
        lines.append("**Case study directions (omp_target):**")
        lines.append("")
        lines.append("| Direction | Pass Rate | 95% CI | n |")
        lines.append("|-----------|-----------|--------|---|")
        for d, data in sorted(cs.items()):
            lines.append(f"| {d} | {_pct(data.get('value'))} | "
                         f"[{_pct(data.get('ci_lower'))}, {_pct(data.get('ci_upper'))}] | "
                         f"{data.get('n', '?')} |")
        lines.append("")

    # Observation
    if std:
        rates = [(d, data.get("value", 0)) for d, data in std.items()]
        rates.sort(key=lambda x: x[1], reverse=True)
        if len(rates) >= 2:
            best_d, best_r = rates[0]
            worst_d, worst_r = rates[-1]
            ratio = best_r / worst_r if worst_r > 0 else float("inf")
            lines.append(f"*Observation: {best_d} has {ratio:.1f}x higher pass rate than {worst_d}.*")
            lines.append("")

    # Dimension 3: Direction asymmetry
    asym = c1.get("direction_asymmetry", {})
    lines.append("### Dimension 3: Direction Asymmetry (McNemar, L0)")
    lines.append("")
    if asym:
        lines.append("| Pair | Fwd Rate | Rev Rate | p-value | Cohen's h | Effect | Sig? |")
        lines.append("|------|----------|----------|---------|-----------|--------|------|")
        for pair_name, finding in sorted(asym.items()):
            tr = finding.get("value", {}).get("test_result", {}) if isinstance(finding.get("value"), dict) else {}
            lines.append(
                f"| {pair_name} | {_pct(tr.get('forward_pass_rate'))} | "
                f"{_pct(tr.get('reverse_pass_rate'))} | "
                f"{tr.get('p_value', '?')} | {tr.get('cohens_h', '?')} | "
                f"{tr.get('effect_size', '?')} | "
                f"{'Yes' if tr.get('significant') else 'No'} |"
            )
        lines.append("")
    else:
        lines.append("No direction pairs found for McNemar test.")
        lines.append("")

    # Dimension 4: Augmentation trends
    aug = c1.get("augmentation_trends", {})
    lines.append("### Dimension 4: Augmentation Trends")
    lines.append("")

    agg_trend = aug.get("aggregate", {})
    if agg_trend:
        ca = agg_trend.get("cochran_armitage", {})
        lines.append(f"**Aggregate Cochran-Armitage:** z={ca.get('z', '?')}, "
                     f"p={ca.get('p_value', '?')}, "
                     f"trend={ca.get('trend_direction', '?')}, "
                     f"significant={'Yes' if ca.get('significant') else 'No'}")
        lines.append("")

        per_level = agg_trend.get("per_level", {})
        if per_level:
            lines.append("| Level | Pass Rate | 95% CI | n |")
            lines.append("|-------|-----------|--------|---|")
            for lv_key in sorted(per_level.keys()):
                data = per_level[lv_key]
                lines.append(f"| {lv_key} | {_pct(data.get('value'))} | "
                             f"[{_pct(data.get('ci_lower'))}, {_pct(data.get('ci_upper'))}] | "
                             f"{data.get('n', '?')} |")
            lines.append("")

        cohens_adj = agg_trend.get("cohens_h_adjacent", {})
        if cohens_adj:
            lines.append("**Cohen's h (adjacent levels):**")
            for pair, h_val in sorted(cohens_adj.items()):
                lines.append(f"- {pair}: h={h_val}")
            lines.append("")

    # Dimension 5: Failure taxonomy
    tax = c1.get("failure_taxonomy", {})
    lines.append("### Dimension 5: Failure Taxonomy")
    lines.append("")

    sc = tax.get("status_counts", {})
    if sc:
        lines.append("| Status | Count | % |")
        lines.append("|--------|-------|---|")
        total_recs = tax.get("total_records", 1)
        for status in ["PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL", "ERROR"]:
            count = sc.get(status, 0)
            pct = count / total_recs * 100 if total_recs > 0 else 0
            lines.append(f"| {status} | {count} | {pct:.1f}% |")
        lines.append("")

    top3 = tax.get("top_3_build_subcategories", [])
    if top3:
        lines.append("**Top-3 BUILD_FAIL subcategories:**")
        lines.append("")
        lines.append("| Subcategory | Count |")
        lines.append("|-------------|-------|")
        for entry in top3:
            lines.append(f"| {entry['subcategory']} | {entry['count']} |")
        lines.append("")

    # Campaign 2 (brief summary)
    c2 = output.get("campaign_2", {})
    lines.append("---")
    lines.append("")
    lines.append("## Campaign 2: pass@k Evaluation (temperature=0.7)")
    lines.append("")
    c2_agg = c2.get("aggregate_pass_rates", {})
    c2_overall = c2_agg.get("overall", {})
    lines.append(f"**Overall:** {_pct(c2_overall.get('value'))} "
                 f"[{_pct(c2_overall.get('ci_lower'))}, {_pct(c2_overall.get('ci_upper'))}] "
                 f"(n={c2_overall.get('n', '?')})")
    lines.append("")

    # Cross-check summary
    xc = output.get("cross_check", {})
    if xc:
        lines.append("---")
        lines.append("")
        lines.append("## Cross-Check Results")
        lines.append("")
        lines.append(f"Checks run: {xc.get('checks_run', 0)}")
        lines.append(f"Status: {xc.get('status', 'unknown')}")
        warnings = xc.get("warnings", [])
        if warnings:
            lines.append("")
            for w in warnings:
                lines.append(f"- {w}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def _pct(val) -> str:
    """Format a decimal as percentage string."""
    if val is None:
        return "?"
    return f"{val * 100:.1f}%"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quantitative findings for SC26 ParBench paper"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root directory",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks (deferred to Plan 03)",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    results_dir = project_root / "results" / "evaluation" / "together-qwen-3.5-397b-a17b"
    output_dir = project_root / "results" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Load ---
    if args.verbose:
        print("Loading result files...")
    all_records = load_results(results_dir, verbose=args.verbose)

    # --- Exclude KNOWN_FAIL ---
    if args.verbose:
        print(f"Excluding {len(EXCLUDED_SPECS)} KNOWN_FAIL specs...")
    valid = exclude_known_fail(all_records)
    excluded_count = len(all_records) - len(valid)
    if args.verbose:
        print(f"  Excluded {excluded_count} records ({len(valid)} remaining)")

    # --- Split campaigns ---
    c1, c2 = split_campaigns(valid)
    if args.verbose:
        print(f"Campaign 1 (temp=0.0): {len(c1)} records")
        print(f"Campaign 2 (temp>0):   {len(c2)} records")

    # --- Compute dimensions 1-5 for Campaign 1 ---
    if args.verbose:
        print("\nComputing dimensions 1-5 for Campaign 1...")

    c1_results: dict = {}
    c1_results["_metadata"] = {"total_on_disk": len(all_records)}

    if args.verbose:
        print("  Dimension 1: Aggregate pass rates...")
    c1_results["aggregate_pass_rates"] = compute_aggregate_pass_rates(c1)

    if args.verbose:
        print("  Dimension 2: Per-direction pass rates...")
    c1_results["direction_pass_rates"] = compute_direction_pass_rates(c1)

    if args.verbose:
        print("  Dimension 3: Direction asymmetry...")
    c1_results["direction_asymmetry"] = compute_direction_asymmetry(c1)

    if args.verbose:
        print("  Dimension 4: Augmentation trends...")
    c1_results["augmentation_trends"] = compute_augmentation_trends(c1)

    if args.verbose:
        print("  Dimension 5: Failure taxonomy...")
    c1_results["failure_taxonomy"] = compute_failure_taxonomy(c1)

    # --- Compute dimensions 1-5 for Campaign 2 ---
    if args.verbose:
        print("\nComputing dimensions 1-5 for Campaign 2...")

    c2_results: dict = {}

    c2_results["aggregate_pass_rates"] = compute_aggregate_pass_rates(c2)
    c2_results["direction_pass_rates"] = compute_direction_pass_rates(c2)
    c2_results["direction_asymmetry"] = compute_direction_asymmetry(c2)
    c2_results["augmentation_trends"] = compute_augmentation_trends(c2)
    c2_results["failure_taxonomy"] = compute_failure_taxonomy(c2)

    # --- Cross-check ---
    if args.verbose:
        print("\nRunning cross-checks...")
    xc = cross_check(c1_results, c2_results, project_root, args.verbose)
    if args.verbose:
        for w in xc.get("warnings", []):
            print(f"  {w}")

    # --- Build output ---
    metadata = build_metadata(all_records, valid, c1, c2, args)
    paper_claims = build_paper_claims(c1_results, c2_results, project_root)

    output = {
        "metadata": metadata,
        "campaign_1": c1_results,
        "campaign_2": c2_results,
        "cross_check": xc,
        "paper_claims": paper_claims,
    }

    # Remove internal metadata from campaign results
    output["campaign_1"].pop("_metadata", None)

    # --- Write JSON ---
    json_path = output_dir / "quantitative_findings.json"
    json_path.write_text(
        json.dumps(output, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    if args.verbose:
        print(f"\nWrote: {json_path}")

    # --- Write markdown ---
    md_path = output_dir / "quantitative_findings.md"
    write_markdown(output, md_path)
    if args.verbose:
        print(f"Wrote: {md_path}")

    # --- Summary ---
    c1_overall = c1_results.get("aggregate_pass_rates", {}).get("overall", {})
    print(
        f"Quantitative findings: {len(all_records)} total files, "
        f"{len(valid)} valid ({len(c1)} C1 + {len(c2)} C2), "
        f"C1 pass rate = {_pct(c1_overall.get('value'))} "
        f"[{_pct(c1_overall.get('ci_lower'))}, {_pct(c1_overall.get('ci_upper'))}]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
