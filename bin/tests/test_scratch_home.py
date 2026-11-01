"""conftest.py hides the starting HOME's bin/alert config from every test (#498).

Each case starts pytest in a subprocess with HOME set to a directory that holds a planted alert
config, over a probe beside a copy of conftest.py. The probe checks, from module import, from
test code and from a shell subprocess, that the planted config is not reachable through HOME.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CONFTEST = Path(__file__).with_name("conftest.py")
MARKER = ".config/loam/alerts/planted-498"

PROBE = f"""
import os
import subprocess
from pathlib import Path

MARKER = {MARKER!r}
AT_IMPORT = [(Path.home() / MARKER).exists(), Path(os.path.expanduser("~"), MARKER).exists()]


def shell_sees_marker():
    return subprocess.run(["sh", "-c", '[ -e "$HOME/{MARKER}" ]']).returncode == 0


def test_import_does_not_see_the_planted_config():
    assert AT_IMPORT == [False, False]


def test_code_does_not_see_the_planted_config():
    assert not (Path.home() / MARKER).exists()
    assert not Path(os.path.expanduser("~"), MARKER).exists()
    assert not (Path.home() / ".config/loam/alerts/hc-api-key").exists()


def test_subprocess_does_not_see_the_planted_config():
    assert not shell_sees_marker()


def test_git_identity_is_set():
    out = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
    assert out.stdout.strip()
"""


def has_xdist():
    return subprocess.run([sys.executable, "-c", "import xdist"], capture_output=True).returncode == 0


@pytest.mark.parametrize("workers", [None, "2"], ids=["serial", "xdist"])
def test_planted_alert_config_is_unreachable(tmp_path, workers):
    if workers and not has_xdist():
        pytest.skip("pytest-xdist is not installed")
    home = tmp_path / "home"
    alerts = home / ".config/loam/alerts"
    alerts.mkdir(parents=True)
    (alerts / "hc-ping-url").write_text("https://hc-ping.com/x\n")
    (alerts / "hc-api-key").write_text("k\n")
    (home / MARKER).touch()
    run = tmp_path / "run"
    run.mkdir()
    (run / "test_probe.py").write_text(PROBE)
    if CONFTEST.exists():
        shutil.copy(CONFTEST, run / "conftest.py")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST_") and not k.startswith("LOAM_TEST_")}
    env["HOME"] = str(home)
    args = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--rootdir={run}", str(run)]
    if workers:
        args[3:3] = ["-n", workers]
    out = subprocess.run(args, cwd=run, env=env, capture_output=True, text=True)
    assert out.returncode == 0 and "4 passed" in out.stdout, out.stdout + out.stderr
