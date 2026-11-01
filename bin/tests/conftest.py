"""Give every test under bin/tests a scratch HOME (#498).

A test that sources bin/factory and lets `finish` run reaches bin/alert, which reads the
healthchecks ping URL and API key under ~/.config/loam/alerts and pauses the owner's monitor.
Pointing HOME at a fresh directory at import time, before any test module loads, covers every
subprocess that copies os.environ and every pytest-xdist worker. A test that sets its own HOME
is unaffected.
"""

import atexit
import os
import shutil
import tempfile
from pathlib import Path

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
