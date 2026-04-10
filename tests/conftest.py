"""
pytest configuration for the ParBench test suite.

Auto-skips tests marked @pytest.mark.integration when the benchmark source
directories are not present on disk (e.g., macOS dev machine, CI).

On the Linux GPU machine where benchmark sources exist, integration tests
run as normal. Separate them explicitly with:

    pytest tests/ -m "not integration"   # unit only
    pytest tests/ -m integration          # integration only
    pytest tests/                          # all (integration auto-skips if dirs missing)
"""

from __future__ import annotations

from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).parent.parent
_RODINIA_SRC = _PROJECT_ROOT / "rodinia" / "rodinia-src"
_HECBENCH_SRC = _PROJECT_ROOT / "HeCBench-master"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip integration tests when benchmark source directories are absent."""
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
