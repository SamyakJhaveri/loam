"""bin/check's pytest step rebuilds .venv/check when the checkout moved (#321).

After a move the venv's bin/python3 still imports xdist, but each console script keeps a shebang naming
the old path. The step runs on its own: the bin/check prelude, then the pytest step up to PYTEST_ARGS=.
A python3 -S shim on PATH hides any installed xdist so the venv branch runs, and the requirements file
names a local stub wheel (module xdist, console script copier), so pip never reaches the network.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECK = ROOT / "bin/check"
WHEEL = "xdist_stub-0-py3-none-any.whl"
ENV = {**os.environ, "PIP_NO_INDEX": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"}


def venv_step(check: str) -> str:
    """The prelude above the first step, then the pytest step up to PYTEST_ARGS=, then the python it chose."""
    lines = check.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('step "'))
    start = lines.index('step "pytest"')
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("PYTEST_ARGS="))
    return "\n".join(lines[:first] + lines[start:end] + ['echo "PY=$PYTEST_PY"']) + "\n"


def write_wheel(path: pathlib.Path) -> None:
    info = "xdist_stub-0.dist-info"
    files = {
        "xdist/__init__.py": "def main():\n    print('stub copier')\n",
        f"{info}/METADATA": "Metadata-Version: 2.1\nName: xdist-stub\nVersion: 0\n",
        f"{info}/WHEEL": "Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        f"{info}/entry_points.txt": "[console_scripts]\ncopier = xdist:main\n",
    }
    files[f"{info}/RECORD"] = "".join(f"{name},,\n" for name in [*files, f"{info}/RECORD"])
    with zipfile.ZipFile(path, "w") as whl:
        for name, text in files.items():
            whl.writestr(name, text)


class MovedVenvTest(unittest.TestCase):
    def test_moved_checkout_rebuilds_venv(self) -> None:
        """Build through a symlink to a/; keep it by either path; rebuild a copy and a move; copier runs."""
        if importlib.util.find_spec("ensurepip") is None:  # Debian without python3-venv cannot build any venv
            self.skipTest("this python3 has no ensurepip, so python3 -m venv cannot build .venv/check")
        # resolved: on macOS /var is /private/var; the link case below covers a logical root that differs
        tmp = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        shim, old, new, link, copy = tmp / "shim", tmp / "a", tmp / "b", tmp / "link", tmp / "c"
        shim.mkdir()
        (shim / "python3").write_text(f'#!/bin/sh\nexec "{sys.executable}" -S "$@"\n', encoding="utf-8")
        (shim / "python3").chmod(0o755)
        (old / "bin").mkdir(parents=True)
        (old / "bin/venv-step").write_text(venv_step(CHECK.read_text(encoding="utf-8")), encoding="utf-8")
        (old / "wheels").mkdir()
        write_wheel(old / "wheels" / WHEEL)
        (old / ".github/ci").mkdir(parents=True)
        (old / ".github/ci/python-requirements.txt").write_text(f"./wheels/{WHEEL}\n", encoding="utf-8")
        env = {**ENV, "PATH": f"{shim}{os.pathsep}{ENV['PATH']}"}

        def run(root: pathlib.Path) -> str:
            # PWD makes bash keep the logical root, so the link case reaches the step as a symlinked path
            r = subprocess.run(["bash", "bin/venv-step"], cwd=root, env={**env, "PWD": str(root)},
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn(f"PY={root}/.venv/check/bin/python3", r.stdout)
            return r.stdout

        link.symlink_to(old)
        self.assertIn("NOTE:", run(link))  # built through a symlinked root
        self.assertNotIn("NOTE:", run(old))  # an unmoved venv is kept, by either path
        self.assertNotIn("NOTE:", run(link))
        link.unlink()  # the scripts must not name the symlink
        copier = subprocess.run([old / ".venv/check/bin/copier"], capture_output=True, text=True)
        self.assertEqual((0, "stub copier\n"), (copier.returncode, copier.stdout), copier.stderr)
        shutil.copytree(old, copy, symlinks=True)
        self.assertIn("NOTE:", run(copy))  # a copy whose original still exists is rebuilt
        shutil.move(old, new)
        self.assertIn("NOTE:", run(new))
        copier = subprocess.run([new / ".venv/check/bin/copier"], capture_output=True, text=True)
        self.assertEqual((0, "stub copier\n"), (copier.returncode, copier.stdout), copier.stderr)


if __name__ == "__main__":
    unittest.main()
