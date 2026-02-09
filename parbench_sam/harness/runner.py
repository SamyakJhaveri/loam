"""harness.runner — Execute a compiled kernel."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from harness.models import RunResult, Status
from harness.spec_loader import resolve_paths

log = logging.getLogger(__name__)


def run_spec(
    spec: dict[str, Any],
    project_root: Path,
    configuration: str = "correctness",
    *,
    verbose: bool = False,
) -> RunResult:
    """Run a compiled kernel for a single input configuration.

    Parameters
    ----------
    spec:
        Parsed spec dict.
    project_root:
        Absolute path to the *parbench_sam/* project root.
    configuration:
        Name of the entry in ``run.input_configurations`` to use
        (e.g. ``"correctness"`` or ``"performance"``).
    verbose:
        If *True*, log stdout/stderr.

    Returns
    -------
    RunResult
    """
    resolved = resolve_paths(spec, project_root)["_resolved"]
    working_dir: Path = resolved["working_dir"]

    run_section = spec.get("run", {})
    input_configs = run_section.get("input_configurations", {})
    timeout_seconds = run_section.get("timeout_seconds", 300)

    # Look up the requested configuration
    config = input_configs.get(configuration)
    if config is None:
        available = list(input_configs.keys())
        return RunResult(
            status=Status.ERROR,
            configuration=configuration,
            duration_seconds=0.0,
            exit_code=-1,
            stdout="",
            stderr=(
                f"Configuration '{configuration}' not found in spec. "
                f"Available: {available}"
            ),
        )

    # Build the command as a list (no shell=True for run)
    executable = run_section.get("executable", "./main")
    exe_path = working_dir / executable

    arguments: list[str] = config.get("arguments", [])
    cmd: list[str] = [str(exe_path)] + [str(a) for a in arguments]

    # Environment
    env = os.environ.copy()
    env_vars = run_section.get("environment_variables") or {}
    env.update(env_vars)

    log.debug("Running: %s  (cwd=%s, timeout=%ds)", cmd, working_dir, timeout_seconds)

    start = time.monotonic()

    try:
        proc = subprocess.run(
            cmd,
            shell=False,
            cwd=str(working_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        elapsed = time.monotonic() - start

        if verbose:
            if proc.stdout:
                log.info("[stdout] %s", proc.stdout.rstrip())
            if proc.stderr:
                log.info("[stderr] %s", proc.stderr.rstrip())

        status = Status.PASS if proc.returncode == 0 else Status.FAIL

        return RunResult(
            status=status,
            configuration=configuration,
            duration_seconds=round(elapsed, 3),
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return RunResult(
            status=Status.TIMEOUT,
            configuration=configuration,
            duration_seconds=round(elapsed, 3),
            exit_code=-1,
            stdout="",
            stderr=f"Execution timed out after {timeout_seconds}s",
        )
    except FileNotFoundError:
        elapsed = time.monotonic() - start
        return RunResult(
            status=Status.ERROR,
            configuration=configuration,
            duration_seconds=round(elapsed, 3),
            exit_code=-1,
            stdout="",
            stderr=f"Executable not found: {exe_path}",
        )
    except Exception as exc:
        elapsed = time.monotonic() - start
        return RunResult(
            status=Status.ERROR,
            configuration=configuration,
            duration_seconds=round(elapsed, 3),
            exit_code=-1,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
        )


def run_all_configurations(
    spec: dict[str, Any],
    project_root: Path,
    *,
    verbose: bool = False,
) -> dict[str, RunResult]:
    """Run every input configuration defined in the spec.

    Parameters
    ----------
    spec:
        Parsed spec dict.
    project_root:
        Absolute path to the project root.
    verbose:
        Forward to :func:`run_spec`.

    Returns
    -------
    dict[str, RunResult]:
        Mapping of ``configuration_name`` → ``RunResult``.
    """
    run_section = spec.get("run", {})
    input_configs = run_section.get("input_configurations", {})

    results: dict[str, RunResult] = {}
    for config_name in input_configs:
        results[config_name] = run_spec(
            spec, project_root, configuration=config_name, verbose=verbose
        )
    return results
