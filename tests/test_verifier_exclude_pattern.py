"""Tests for stdout_exclude_pattern verification strategy."""
from __future__ import annotations

from harness.models import RunResult, Status
from harness.verifier import verify_run


def _make_run_result(stdout: str = "", exit_code: int = 0) -> RunResult:
    return RunResult(
        status=Status.PASS,
        configuration="correctness",
        duration_seconds=0.2,
        exit_code=exit_code,
        stdout=stdout,
        stderr="",
    )


def _make_spec(*strategies: dict) -> dict:
    return {"verification": {"strategies": list(strategies)}}


def test_stdout_exclude_pattern_fails_on_match():
    """stdout_exclude_pattern FAILS when the pattern IS found in stdout."""
    run_result = _make_run_result(
        stdout="Random seed: 7\nERROR: 1 clEnqueueReadBuffer: input_ocl\nFinish the training\n",
    )
    spec = _make_spec(
        {"type": "stdout_exclude_pattern", "pattern": "ERROR.*cl",
         "description": "No OpenCL errors"},
    )
    result = verify_run(spec, run_result)
    assert result.status == Status.FAIL
    assert "stdout_exclude_pattern" in result.strategy_used


def test_stdout_exclude_pattern_passes_when_no_match():
    """stdout_exclude_pattern PASSES when the pattern is NOT found."""
    run_result = _make_run_result(
        stdout="Random seed: 7\nFinish the training for one iteration\n",
    )
    spec = _make_spec(
        {"type": "stdout_exclude_pattern", "pattern": "ERROR.*cl",
         "description": "No OpenCL errors"},
    )
    result = verify_run(spec, run_result)
    assert result.status == Status.PASS


def test_stdout_exclude_pattern_combined_with_positive():
    """Both stdout_pattern and stdout_exclude_pattern must pass together."""
    run_result = _make_run_result(
        stdout="Finish the training\nERROR: 1 clEnqueueReadBuffer\n",
    )
    spec = _make_spec(
        {"type": "stdout_pattern", "pattern": "Finish the training",
         "description": "Expected output present"},
        {"type": "stdout_exclude_pattern", "pattern": "ERROR.*cl",
         "description": "No OpenCL errors"},
    )
    result = verify_run(spec, run_result)
    assert result.status == Status.FAIL
