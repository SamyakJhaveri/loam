"""bin/factory run, next, status and status --criteria refuse off Linux, as their first step (#577).

jhaveris (Ubuntu) is the only factory runner. Each gated command reads `uname -s` and nothing else, so a `uname` on
PATH that prints Darwin fakes a Mac: the command prints one line saying the factory runs only on Linux and exits 2,
before any run dir, ticket or gh call. The portable commands (lint here) stay ungated, and the real host is not
refused.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG",
             "FACTORY_RUNS_ROOT", "FACTORY_FROZEN")
UNAME = '#!/bin/sh\nif [ "$1" = -s ]; then echo Darwin; else exec /usr/bin/uname "$@"; fi\n'
LINE = "the factory runs only on Linux"


class LinuxOnlyTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        (self.top / "bin").mkdir()
        (self.top / "bin" / "uname").write_text(UNAME)
        (self.top / "bin" / "uname").chmod(0o755)
        # The programs the gated commands would reach after the gate log their call, so a refusal that comes late shows.
        self.calls = self.top / "calls"
        for name in ("gh", "claude", "jq", "python3", "tmux", "crontab"):
            (self.top / "bin" / name).write_text(f'#!/bin/sh\necho {name} >> "{self.calls}"\nexit 1\n')
            (self.top / "bin" / name).chmod(0o755)
        self.runs = self.top / "runs"

    def factory(self, *args: str, mac: bool = True) -> subprocess.CompletedProcess[str]:
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        path = f"{self.top / 'bin'}{os.pathsep}{base['PATH']}" if mac else base["PATH"]
        return subprocess.run(["bash", str(ROOT / "bin/factory"), *args], cwd=ROOT,
                              env={**base, "PATH": path, "FACTORY_RUNS_ROOT": str(self.runs), "HOME": str(self.top)},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=60)

    def test_gated_commands_refuse_off_linux_as_their_first_step(self) -> None:
        ticket = self.top / "ticket.md"
        ticket.write_text((ROOT / "bin/tests/fixtures/clean-ticket.md").read_text())
        for args in (("run", str(ticket)), ("next",), ("next", "--dry-run"), ("next", "--install"), ("status",),
                     ("status", "--criteria")):
            with self.subTest(args=args):
                proc = self.factory(*args)
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertEqual(proc.stdout, "")
                self.assertEqual(len(proc.stderr.splitlines()), 1, proc.stderr)
                self.assertIn(LINE, proc.stderr)
                self.assertIn("Darwin", proc.stderr)
                self.assertIn("bin/runner", proc.stderr)
                self.assertFalse(self.runs.exists(), "a refused command wrote a run dir")
                self.assertFalse(self.calls.exists(), self.calls.read_text() if self.calls.exists() else "")

    def test_portable_commands_are_not_refused_off_linux(self) -> None:
        proc = self.factory("lint", str(ROOT / "bin/tests/fixtures/clean-ticket.md"))
        self.assertNotIn(LINE, proc.stderr)
        proc = self.factory("stop")
        self.assertNotIn(LINE, proc.stderr)
        self.assertIn("usage: bin/factory [-C <repo>] stop", proc.stderr)

    def test_linux_is_not_refused(self) -> None:
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        for cmd in ("run", "next", "status", "status --criteria"):
            with self.subTest(cmd=cmd):
                proc = subprocess.run(["bash", "-c", f'. bin/factory\nlinux_only "{cmd}"; echo passed'], cwd=ROOT,
                                      env={**base, "FACTORY_SOURCED": "1"}, stdin=subprocess.DEVNULL,
                                      capture_output=True, text=True, check=False)
                self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "passed"), proc.stderr)
                self.assertNotIn(LINE, proc.stderr)


if __name__ == "__main__":
    unittest.main()
