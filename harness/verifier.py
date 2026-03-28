"""harness.verifier — Verify kernel output against spec strategies."""

from __future__ import annotations

import logging
import re
from typing import Any

from harness.models import MetricResult, RunResult, Status, VerificationResult

log = logging.getLogger(__name__)


def verify_run(
    spec: dict[str, Any],
    run_result: RunResult,
) -> VerificationResult:
    """Apply ALL verification strategies; every non-SKIP strategy must PASS.

    Returns PASS only when every implemented strategy passes.  Returns FAIL
    on the first strategy that fails (with that strategy's details).  SKIP
    strategies (unimplemented types like numeric_comparison) are ignored —
    they neither block a PASS nor cause a FAIL.

    Supported strategy types
    ------------------------
    * **exit_code** — check ``run_result.exit_code == strategy["expected"]``
    * **stdout_pattern** — ``re.search(pattern, stdout)``
    * **numeric_comparison** — *TODO* (returns SKIP)
    * **file_diff** — *TODO* (returns SKIP)
    * **custom_script** — *TODO* (returns SKIP)

    Parameters
    ----------
    spec:
        Parsed spec dict.
    run_result:
        The :class:`RunResult` to verify.

    Returns
    -------
    VerificationResult
    """
    verification = spec.get("verification", {})
    strategies: list[dict[str, Any]] = verification.get("strategies", [])

    if not strategies:
        return VerificationResult(
            status=Status.SKIP,
            strategy_used="(none)",
            details="No verification strategies defined in spec",
        )

    passed_strategies: list[str] = []

    for strategy in strategies:
        stype = strategy.get("type", "")

        if stype == "exit_code":
            result = _check_exit_code(strategy, run_result)
        elif stype == "stdout_pattern":
            result = _check_stdout_pattern(strategy, run_result)
        elif stype == "numeric_comparison":
            result = _stub_strategy(stype)
        elif stype == "file_diff":
            result = _stub_strategy(stype)
        elif stype == "custom_script":
            result = _stub_strategy(stype)
        else:
            log.warning("Unknown verification strategy type: %s", stype)
            result = _stub_strategy(stype)

        if result.status in (Status.FAIL, Status.ERROR):
            return result
        if result.status == Status.PASS:
            passed_strategies.append(stype)
        # SKIP: ignore and continue to next strategy

    if passed_strategies:
        return VerificationResult(
            status=Status.PASS,
            strategy_used="+".join(passed_strategies),
            details=f"All {len(passed_strategies)} strategies passed: {', '.join(passed_strategies)}",
        )

    # If we exhausted all strategies without a PASS/FAIL, report overall
    return VerificationResult(
        status=Status.SKIP,
        strategy_used="(all skipped)",
        details="No strategy produced a definitive PASS or FAIL",
    )


def extract_metrics(
    spec: dict[str, Any],
    run_result: RunResult,
) -> list[MetricResult]:
    """Extract performance metrics from run output using spec definitions.

    Parameters
    ----------
    spec:
        Parsed spec dict.
    run_result:
        The :class:`RunResult` whose stdout is scanned.

    Returns
    -------
    list[MetricResult]
    """
    perf = spec.get("performance") or {}
    metric_defs: list[dict[str, Any]] = perf.get("metrics", [])

    results: list[MetricResult] = []
    for mdef in metric_defs:
        name = mdef.get("name", "unknown")
        unit = mdef.get("unit", "")
        extraction = mdef.get("extraction", {})

        if extraction.get("type") != "regex":
            log.debug("Skipping non-regex metric extraction: %s", name)
            continue

        pattern = extraction.get("pattern", "")
        capture_group = extraction.get("capture_group", 1)

        try:
            match = re.search(pattern, run_result.stdout)
            if match:
                value = float(match.group(capture_group))
                results.append(MetricResult(name=name, value=value, unit=unit))
            else:
                log.debug("Metric '%s' pattern did not match stdout", name)
        except (ValueError, IndexError, re.error) as exc:
            log.warning("Failed to extract metric '%s': %s", name, exc)

    return results


# ---------------------------------------------------------------------------
# Strategy implementations
# ---------------------------------------------------------------------------


def _check_exit_code(
    strategy: dict[str, Any],
    run_result: RunResult,
) -> VerificationResult:
    """Verify ``exit_code == expected``."""
    expected = strategy.get("expected", 0)
    desc = strategy.get("description", "")

    if run_result.exit_code == expected:
        return VerificationResult(
            status=Status.PASS,
            strategy_used="exit_code",
            details=f"exit_code={run_result.exit_code} == expected {expected}. {desc}",
        )
    return VerificationResult(
        status=Status.FAIL,
        strategy_used="exit_code",
        details=(f"exit_code={run_result.exit_code} != expected {expected}. {desc}"),
    )


def _check_stdout_pattern(
    strategy: dict[str, Any],
    run_result: RunResult,
) -> VerificationResult:
    """Verify stdout matches a regex pattern."""
    pattern = strategy.get("pattern", "")
    desc = strategy.get("description", "")

    if not pattern:
        return VerificationResult(
            status=Status.SKIP,
            strategy_used="stdout_pattern",
            details="Empty pattern",
        )

    flags = re.MULTILINE if strategy.get("multiline") else 0

    try:
        if re.search(pattern, run_result.stdout, flags):
            return VerificationResult(
                status=Status.PASS,
                strategy_used="stdout_pattern",
                details=f"Pattern '{pattern}' matched. {desc}",
            )
        return VerificationResult(
            status=Status.FAIL,
            strategy_used="stdout_pattern",
            details=f"Pattern '{pattern}' NOT found in stdout. {desc}",
        )
    except re.error as exc:
        return VerificationResult(
            status=Status.ERROR,
            strategy_used="stdout_pattern",
            details=f"Invalid regex '{pattern}': {exc}",
        )


def _stub_strategy(stype: str) -> VerificationResult:
    """Placeholder for unimplemented strategy types."""
    return VerificationResult(
        status=Status.SKIP,
        strategy_used=stype,
        details=f"Strategy '{stype}' is not yet implemented (TODO)",
    )
