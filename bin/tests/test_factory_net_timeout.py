"""A gh call cut off at NET_TIMEOUT_SEC in the frozen pass ends the run it owns stopped-environment (#382).

Since #422 cmd_run writes `owner` and `running` before it execs the frozen copy, whose load_ticket reads the issue
again with FACTORY_ROOT set. Each test writes a run dir with status `running`, puts a `gh` that hangs first on PATH,
and calls load_ticket from a sourced bin/factory with FACTORY_FROZEN naming the run. When the owner line names this
process, the cut-off call ends through finish (status, alert, exit 4); when it names another, load_ticket only exits 4.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "FACTORY_FROZEN", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER",
             "REPO", "RUN", "LOG")


class NetTimeoutTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "runs" / "7" / "abcd1234"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "status").write_text("running\n")
        (self.run_dir / "frozen" / "issue.md").write_text("# Net fixture\n")
        self.alerts = self.top / "alerts.txt"
        alert = self.run_dir / "frozen" / "alert"
        alert.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> '{self.alerts}'\n")
        alert.chmod(0o755)
        (self.top / "bin").mkdir()
        gh = self.top / "bin" / "gh"
        gh.write_text("#!/usr/bin/env bash\nexec sleep 600\n")
        gh.chmod(0o755)

    def load(self, owner: str) -> tuple[subprocess.CompletedProcess, float]:
        script = f"printf '%s x\\n' {owner} > '{self.run_dir}/owner'\n. bin/factory\nload_ticket 7"
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        env = {**base, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FACTORY_RUNS_ROOT": str(self.top / "runs"),
               "FACTORY_FROZEN": str(self.run_dir / "frozen" / "factory"), "FACTORY_NET_TIMEOUT_SEC": "2",
               "PATH": f"{self.top / 'bin'}:{os.environ['PATH']}"}
        start = time.monotonic()
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        return proc, time.monotonic() - start

    def test_owned_run_ends_stopped_environment(self) -> None:
        proc, took = self.load('"$$"')
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertLess(took, 30)
        self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-environment")
        alerts = self.alerts.read_text()
        self.assertIn("stopped on a machine or tool problem", alerts)
        self.assertIn("gh issue view #7", alerts)
        self.assertIn("EXIT stopped-environment (4): gh issue view #7", (self.run_dir / "factory.log").read_text())

    def test_run_owned_by_another_process_is_left_alone(self) -> None:
        proc, took = self.load("1")
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertLess(took, 30)
        self.assertIn("could not read issue #7", proc.stderr)
        self.assertEqual((self.run_dir / "status").read_text().strip(), "running")
        self.assertFalse(self.alerts.exists())


if __name__ == "__main__":
    unittest.main()
