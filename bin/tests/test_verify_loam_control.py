"""run.json bookkeeping in verify-loam's control-loam, with fake copier and claude on PATH.

bin/release.sh tags a commit only when a run of that commit records doctor ok and a check on a pristine render.
No network, no model calls.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTROL = ROOT / "seed/.claude/skills/verify-loam/control-loam"


class ControlLoamRunRecord(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        for tool in ("copier", "claude"):
            (fake_bin / tool).write_text("#!/bin/sh\nexit 0\n")
            (fake_bin / tool).chmod(0o755)
        self.env = {**os.environ, "LOAM_VERIFY_ROOT": str(self.root / "runs"),
                    "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}"}
        self.run_dir = self.root / "runs/r"
        (self.run_dir / "render").mkdir(parents=True)
        (self.run_dir / "evidence").mkdir()
        subprocess.run(["git", "init", "-q", str(self.run_dir / "render")], check=True)
        self.meta = {"run": "r", "ref": "v0", "commit": "0" * 40, "dirty": False, "kind": "python", "source": str(ROOT),
                     "sessions": [{"name": "s1", "session_id": None}],
                     "doctor": {"ok": True}, "check": {"ok": True, "pristine": True}}
        (self.run_dir / "run.json").write_text(json.dumps(self.meta))

    def control(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(CONTROL), *args], capture_output=True, text=True, env=self.env, timeout=60)

    def test_update_drops_the_old_doctor_and_check(self):
        # Kept records would let bin/release.sh take an updated, unchecked render as a check of the new commit.
        r = self.control("update", "r", "--ref", "HEAD")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        meta = json.loads((self.run_dir / "run.json").read_text())
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(meta["commit"], head)
        self.assertNotIn("doctor", meta)
        self.assertNotIn("check", meta)

    def test_resume_of_a_session_without_an_id_is_a_json_error(self):
        r = self.control("session", "r", "hi", "--resume", "s1")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
