"""
pytest configuration for the ParBench test suite.

Auto-skips tests marked @pytest.mark.integration when the benchmark source
directories are not present on disk (e.g., macOS dev machine, CI).

On the Linux GPU machine where benchmark sources exist, integration tests
run as normal. Separate them explicitly with:

    pytest tests/ -m "not integration"   # unit only
    pytest tests/ -m integration          # integration only
    pytest tests/                          # all (integration auto-skips if dirs missing)

Also gates @pytest.mark.llm tests behind PARBENCH_RUN_LLM_TESTS=1 (plan 02-07).
LLM-marked tests cost real money — they are SKIPPED unless the env var is set.

Plan 02-07 also promoted `_PROJECT_ROOT` → public `PROJECT_ROOT` so downstream
tests can `from tests.conftest import PROJECT_ROOT` instead of replicating the
`Path(__file__).parent.parent` idiom.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Public alias — promoted from `_PROJECT_ROOT` per plan 02-07 (D-28 / F-02 fix).
PROJECT_ROOT = Path(__file__).parent.parent
_PROJECT_ROOT = PROJECT_ROOT  # retained for backward-compat with pre-02-07 tests

_RODINIA_SRC = PROJECT_ROOT / "rodinia" / "rodinia-src"
_HECBENCH_SRC = PROJECT_ROOT / "HeCBench-master"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip integration tests when benchmark source directories are absent.

    Also skips llm-marked tests unless PARBENCH_RUN_LLM_TESTS=1 (plan 02-07).
    """
    # llm gate (plan 02-07) — applies regardless of integration status.
    run_llm = os.environ.get("PARBENCH_RUN_LLM_TESTS") == "1"
    skip_llm = pytest.mark.skip(
        reason="llm tests require PARBENCH_RUN_LLM_TESTS=1 (real API calls cost money)"
    )
    for item in items:
        if item.get_closest_marker("llm") and not run_llm:
            item.add_marker(skip_llm)

    # integration gate — skip when benchmark source dirs are missing.
    benchmark_dirs_present = _RODINIA_SRC.is_dir() and _HECBENCH_SRC.is_dir()
    if benchmark_dirs_present:
        return

    skip_marker = pytest.mark.skip(
        reason=(
            "Integration tests require benchmark source dirs on disk "
            f"(missing: {_RODINIA_SRC} or {_HECBENCH_SRC}). "
            "Run on the Linux GPU machine, or use -m 'not integration' to run unit tests only."
        )
    )
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip_marker)
