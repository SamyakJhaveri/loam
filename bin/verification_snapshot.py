#!/usr/bin/env python3
"""Run a gate against a frozen copy of the intended, non-secret source tree.

The source repository and its index are read-only. Only the scratch repository
receives a commit. A changed source state invalidates an otherwise green run.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
LIB = Path(__file__).resolve().parents[1] / "seed/.agents/lib"
sys.path.insert(0, str(LIB))
from validation import (  # noqa: E402
    ValidationError,
    source_generation,
    source_paths,
    source_state,
)


DEFAULT_TIMEOUT_SECONDS = 14 * 60
TERMINATION_GRACE_SECONDS = 1
TIMEOUT_EXIT_CODE = 124


def _validate_timeout(timeout_seconds: float) -> None:
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout must be finite and positive")


def _source_is_unchanged(root: Path, state: dict, generation: list) -> bool:
    return source_state(root) == state and source_generation(root) == generation


def _process_group_exists(group: int) -> bool:
    try:
        os.killpg(group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _signal_process_group(group: int, requested_signal: signal.Signals) -> bool:
    try:
        os.killpg(group, requested_signal)
    except (PermissionError, ProcessLookupError):
        return False
    return True


def _stop_process_group(process: subprocess.Popen) -> None:
    """Bound cleanup for the command and descendants in its process group."""
    group = process.pid
    if _process_group_exists(group):
        _signal_process_group(group, signal.SIGTERM)
    try:
        process.wait(timeout=TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        if not _signal_process_group(group, signal.SIGKILL):
            process.kill()
        process.wait(timeout=TERMINATION_GRACE_SECONDS)

    deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
    while _process_group_exists(group) and time.monotonic() < deadline:
        time.sleep(0.01)
    if _process_group_exists(group):
        _signal_process_group(group, signal.SIGKILL)


def _run_command(
    command: list[str], cwd: Path, environment: dict[str, str], timeout_seconds: float
) -> tuple[int, bool]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        start_new_session=True,
    )
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        returncode = TIMEOUT_EXIT_CODE
    finally:
        _stop_process_group(process)
    return returncode, timed_out


def create_snapshot(
    root: Path, target: Path, *, generation: list | None = None
) -> dict:
    root = root.resolve()
    if generation is None:
        generation = source_generation(root)
    before = source_state(root)
    if source_generation(root) != generation:
        raise ValueError("source changed while creating the verification snapshot")
    target.mkdir()
    for relative in source_paths(root):
        source = root / relative
        destination = target / relative
        if source.is_symlink():
            # Do not follow a link into private material or another checkout.
            if not source.resolve().is_relative_to(root):
                raise ValueError(f"external symlink cannot be frozen: {relative}")
            if os.path.isabs(os.readlink(source)):
                raise ValueError(f"absolute symlink cannot be frozen: {relative}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(os.readlink(source))
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination, follow_symlinks=False)
        elif source.exists():
            raise ValueError(f"unsupported snapshot input: {relative}")
        # A tracked deletion belongs to the identity but not the copied tree.
    if not _source_is_unchanged(root, before, generation):
        raise ValueError("source changed while creating the verification snapshot")
    commands = [
        ["init", "-q"],
        ["add", "--all", "--force", "--", "."],
        [
            "-c",
            "user.name=Loam Snapshot",
            "-c",
            "user.email=snapshot@example.invalid",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "--allow-empty",
            "-m",
            "Frozen verification input",
        ],
    ]
    # Ambient Git overrides must not redirect scratch commands into the source.
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    for command in commands:
        subprocess.run(
            ["git", "-C", str(target), *command],
            env=environment,
            check=True,
            capture_output=True,
            timeout=30,
        )
    if not _source_is_unchanged(root, before, generation):
        raise ValueError("source changed while creating the verification snapshot")
    return before


def _prewarm_scratch_outputs(target: Path) -> None:
    """Create declared output directories before freezing scratch generations.

    Literal directory rules in source .gitignore files provide a bounded cache
    prewarm list. Glob rules are not guessed. New unplanned directory entries
    remain conservative failures; existing ignored trees can change freely.
    """
    candidates = set()
    for relative in source_paths(target):
        if Path(relative).name != ".gitignore":
            continue
        ignore_file = target / relative
        if ignore_file.is_symlink():
            continue
        for line in ignore_file.read_text().splitlines():
            if not line.endswith("/") or any(char in line for char in "!#*?[]\\"):
                continue
            name = line.strip("/")
            if (
                not name
                or ".." in Path(name).parts
                or "__pycache__" in Path(name).parts
            ):
                continue
            candidate = ignore_file.parent / name
            if any(
                parent.is_symlink()
                for parent in [candidate, *candidate.parents]
                if parent.is_relative_to(target)
            ):
                continue
            candidates.add(candidate)
    for candidate in sorted(candidates):
        relative = str(candidate.relative_to(target))
        ignored = subprocess.run(
            ["git", "-C", str(target), "check-ignore", "-q", "--", relative + "/"],
            capture_output=True,
        )
        if ignored.returncode not in {0, 1}:
            raise ValueError("cannot establish scratch output exclusions")
        if ignored.returncode == 0:
            candidate.mkdir(parents=True, exist_ok=True)
    # These controlled root outputs never count as intended source. Reserving
    # their entries permits ordinary writes without hiding root-directory churn.
    for name in (".validation_passed", ".codex_review_done"):
        (target / name).touch(exist_ok=True)


def run(
    root: Path, command: list[str], timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
) -> int:
    _validate_timeout(timeout_seconds)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="loam-verify-") as directory:
        target = Path(directory) / "source"
        generation = source_generation(root)
        before = create_snapshot(root, target, generation=generation)
        _prewarm_scratch_outputs(target)
        scratch_before = source_state(target)
        scratch_generation = source_generation(target)
        print(f"verification source: {before['digest']}", flush=True)
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        returncode, timed_out = _run_command(
            command, target, environment, timeout_seconds
        )
        unchanged = _source_is_unchanged(root, before, generation)
        scratch_unchanged = _source_is_unchanged(
            target, scratch_before, scratch_generation
        )
        print(f"verification elapsed: {time.monotonic() - started:.3f}s", flush=True)
        if not unchanged:
            print(
                "FAIL: source changed during verification; this result cannot approve the current tree.",
                file=sys.stderr,
            )
            return 1
        if not scratch_unchanged:
            print(
                "FAIL: scratch source changed during verification; stages did not use one frozen input.",
                file=sys.stderr,
            )
            return 1
        if timed_out:
            print(
                f"FAIL: verification command exceeded {timeout_seconds:g}s deadline.",
                file=sys.stderr,
            )
        return returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    arguments = parser.parse_args()
    try:
        _validate_timeout(arguments.timeout_seconds)
    except ValueError as error:
        parser.error(str(error))
    command = arguments.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("a check command is required after --")
    try:
        return run(arguments.root, command, arguments.timeout_seconds)
    except (ValidationError, ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL: verification snapshot: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
