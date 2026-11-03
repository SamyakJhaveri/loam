"""Give every test under bin/tests a scratch HOME (#498), and mark the factory tests not run off Linux (#577).

A test that sources bin/factory and lets `finish` run reaches bin/alert, which reads the
healthchecks ping URL and API key under ~/.config/loam/alerts and pauses the owner's monitor.
Pointing HOME at a fresh directory at import time, before any test module loads, covers every
subprocess that copies os.environ and every pytest-xdist worker. A test that sets its own HOME
is unaffected.

bin/factory's run, next, status and status --criteria refuse off Linux (jhaveris is the only factory runner), and
many factory tests drive them, so on a Mac every test_factory*.py item is marked not run and bin/check stays green;
lint and the portable commands still run there. On Linux the mark's condition is false and every factory test runs.
"""

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# A worker inherits the controller's scratch HOME; reuse it only when HOME still names it, so a
# run started with HOME pointing elsewhere (test_scratch_home.py does that) gets its own.
_SCRATCH_VAR = "LOAM_TEST_SCRATCH_HOME"

if not os.environ.get(_SCRATCH_VAR) or os.environ.get("HOME") != os.environ[_SCRATCH_VAR]:
    _start = Path(os.path.expanduser("~"))
    _scratch = Path(tempfile.mkdtemp(prefix="loam-test-home-"))
    atexit.register(shutil.rmtree, str(_scratch), True)
    # CI sets its git identity with `git config --global`, which this HOME hides, and tests commit.
    (_scratch / ".gitconfig").write_text(
        "[user]\n\tname = loam-tests\n\temail = loam-tests@example.invalid\n", encoding="utf-8"
    )
    # A host ruff wrapper on PATH may exec $HOME/.local/bin/ruff. Link nothing else: never
    # .config (bin/alert's secrets) or .local/state.
    if (_start / ".local" / "bin").is_dir():
        (_scratch / ".local").mkdir()
        (_scratch / ".local" / "bin").symlink_to(_start / ".local" / "bin")
    os.environ["HOME"] = os.environ[_SCRATCH_VAR] = str(_scratch)


def pytest_collection_modifyitems(config, items):
    off_linux = pytest.mark.skipif(sys.platform != "linux",
                                   reason="the factory runs only on Linux: bin/factory run, next and status refuse here")
    for item in items:
        if item.path.name.startswith("test_factory"):
            item.add_marker(off_linux)
