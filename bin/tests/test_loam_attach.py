"""Behavior of bin/loam-attach.sh.

Runs the real script (it reads the seed harness and marketplace from this
checkout) against a throwaway target directory, and checks what it writes,
the refusal without --force, and that settings.local.json is never clobbered.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATTACH = ROOT / "bin/loam-attach.sh"


class LoamAttachTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dst = pathlib.Path(self.tmp.name) / "target"
        self.dst.mkdir()

    def attach(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(ATTACH), str(self.dst), *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def test_writes_the_harness(self) -> None:
        r = self.attach()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue((self.dst / ".claude/settings.json").is_file())
        hooks = list((self.dst / ".claude/hooks").glob("*.sh"))
        self.assertTrue(hooks, "no hook scripts copied")
        slj = self.dst / ".claude/settings.local.json"
        data = json.loads(slj.read_text())
        self.assertTrue(data["enabledPlugins"]["sam-cc-setup@seed-skills"])
        src = data["extraKnownMarketplaces"]["seed-skills"]["source"]
        self.assertEqual(str(ROOT / "cultivation/marketplace"), src["path"])
        gi = (self.dst / ".gitignore").read_text()
        self.assertIn("# Loam harness (added by loam-attach.sh)", gi)
        self.assertIn(".claude/settings.local.json", gi)
        self.assertIn(".validation_passed", gi)

    def test_refuses_without_force(self) -> None:
        self.assertEqual(0, self.attach().returncode)
        r = self.attach()
        self.assertEqual(1, r.returncode)
        self.assertIn("re-run with --force", r.stderr)

    def test_force_keeps_settings_local_and_gitignore_stays_idempotent(self) -> None:
        self.assertEqual(0, self.attach().returncode)
        slj = self.dst / ".claude/settings.local.json"
        slj.write_text('{"mine": true}\n')
        r = self.attach("--force")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual('{"mine": true}\n', slj.read_text())
        gi = (self.dst / ".gitignore").read_text()
        self.assertEqual(1, gi.count("# Loam harness (added by loam-attach.sh)"))


if __name__ == "__main__":
    unittest.main()
