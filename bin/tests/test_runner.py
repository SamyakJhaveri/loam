"""bin/runner runs commands from ~/loam on the runner and syncs the factory tree to loam/ there (#642).

The repo moved to ~/loam on jhaveris; ~/Desktop/loam was a symlink that goes away. Stub ssh and rsync
come first on PATH and write their argv to a log, so nothing reaches the runner.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

RUNNER = pathlib.Path(__file__).resolve().parents[2] / "bin" / "runner"
STUB = '#!/bin/sh\nprintf "%s\\n" "$@" > "$STUB_LOG"\n'


class Runner(unittest.TestCase):
    def argv(self, tool: str, *args: str) -> list[str]:
        """Run bin/runner with a stub `tool` on PATH and LOOP_HOST unset; return the argv the stub saw."""
        scratch = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))
        stub = scratch / tool
        stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
        log = scratch / "argv.log"
        env = {k: v for k, v in os.environ.items() if k != "LOOP_HOST"}
        env.update(STUB_LOG=str(log), PATH=f"{scratch}{os.pathsep}{env.get('PATH', '')}")
        subprocess.run([str(RUNNER), *args], env=env, check=True, capture_output=True, text=True)
        return log.read_text(encoding="utf-8").splitlines()

    def test_command_runs_from_loam(self) -> None:
        self.assertEqual(self.argv("ssh", "echo hi-1"), ["jhaveris", "bash", "-lc", "'cd ~/loam && echo hi-1'"])

    def test_dash_c_replaces_the_directory(self) -> None:
        self.assertEqual(self.argv("ssh", "-C", "~/distbench", "echo hi-2"),
                         ["jhaveris", "bash", "-lc", "'cd ~/distbench && echo hi-2'"])

    def test_sync_mirrors_to_loam(self) -> None:
        self.assertEqual(self.argv("rsync", "sync"),
                         ["-az", "--delete", "--exclude", "__pycache__", "--exclude", "runs",
                          ".superpowers/factory/", "jhaveris:loam/.superpowers/factory/"])


if __name__ == "__main__":
    unittest.main()
