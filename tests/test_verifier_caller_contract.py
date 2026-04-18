"""Contract tests: all production callers of verify_run() must pass working_dir.

S1 introduced a `working_dir` kwarg on `verify_run()` so file_hash strategies can
SHA-256 output files relative to the run's working directory. Any production
caller that omits it will ERROR on every file_hash spec. These tests statically
check each caller's source file to ensure the kwarg is passed, so a future
regression (e.g. a refactor dropping the kwarg) is caught at test time.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Regex catches `verify_run(...)` calls and checks for `working_dir=` within
# the argument list (single- or multi-line).
_VERIFY_RUN_CALL = re.compile(r"verify_run\s*\((?P<args>.*?)\)", re.DOTALL)

_CALLERS = [
    "harness/cli.py",
    "scripts/evaluation/llm_evaluate.py",
    "scripts/evaluation/reverify_pass_results.py",
    "scripts/augmentation/augment_verify.py",
]


def _caller_passes_working_dir(caller_path: Path) -> bool:
    """Return True iff every verify_run(...) call in `caller_path` passes a
    `working_dir=` kwarg."""
    source = caller_path.read_text()
    calls = list(_VERIFY_RUN_CALL.finditer(source))
    assert calls, f"no verify_run() call found in {caller_path}"
    return all("working_dir=" in m.group("args") for m in calls)


@pytest.mark.parametrize("rel_path", _CALLERS)
def test_caller_passes_working_dir(rel_path: str) -> None:
    caller = PROJECT_ROOT / rel_path
    assert _caller_passes_working_dir(caller), (
        f"{caller} calls verify_run() without working_dir=; "
        f"file_hash specs will ERROR under this caller"
    )
