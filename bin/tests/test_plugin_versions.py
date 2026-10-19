"""bin/plugin_versions.py over a throwaway git repo holding one local plugin."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin/plugin_versions.py"
# No user or system git config: a global commit.gpgsign or hook path must not break the fixture commits.
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}
MARKETPLACE = "cultivation/marketplace/.claude-plugin/marketplace.json"
PLUGIN = "cultivation/marketplace/p/.claude-plugin/plugin.json"
SKILL = "cultivation/marketplace/p/skills/s/SKILL.md"


class PluginVersionsTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name)
        self.git("init", "-q", "-b", "main")
        self.set_versions("1.2.9", "1.2.9")
        self.write(SKILL, "first\n")
        self.commit("base")
        self.git("checkout", "-q", "-b", "topic")

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True, capture_output=True)

    def write(self, rel: str, text: str) -> None:
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def set_versions(self, marketplace: str, plugin: str) -> None:
        # The git-subdir entry has no local plugin.json and no version; the check must leave it alone.
        external = {"name": "ext", "source": {"source": "git-subdir", "url": "https://example.invalid/x.git"}}
        manifest = {"name": "m", "plugins": [{"name": "p", "version": marketplace, "source": "./p"}, external]}
        self.write(MARKETPLACE, json.dumps(manifest, indent=2) + "\n")
        self.write(PLUGIN, json.dumps({"name": "p", "version": plugin}, indent=2) + "\n")

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def check(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--root", str(self.repo)],
            capture_output=True, text=True, env=ENV,
        )

    def test_agreeing_unchanged_plugin_passes(self) -> None:
        r = self.check()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("p: 1.2.9", r.stdout)

    def test_manifest_mismatch_fails(self) -> None:
        self.set_versions("1.2.10", "1.2.9")
        self.commit("bump only the marketplace entry")
        r = self.check()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("FAIL: p: marketplace.json says 1.2.10 but", r.stdout)

    def test_changed_file_with_unchanged_version_fails(self) -> None:
        self.write(SKILL, "second\n")
        self.commit("change the skill, keep the version")
        r = self.check()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("FAIL: p: files under cultivation/marketplace/p changed", r.stdout)
        self.assertIn("1.2.9 is not above 1.2.9", r.stdout)

    def test_changed_file_with_bumped_version_passes(self) -> None:
        self.write(SKILL, "second\n")
        # 1.2.10 sorts below 1.2.9 as a string, so this also proves the comparison is numeric.
        self.set_versions("1.2.10", "1.2.10")
        self.commit("change the skill and bump")
        r = self.check()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("p: 1.2.10", r.stdout)

    def test_no_base_ref_skips_the_bump_rule(self) -> None:
        self.write(SKILL, "second\n")
        self.commit("change the skill, keep the version")
        self.git("branch", "-m", "main", "trunk")
        r = self.check()
        self.assertEqual(3, r.returncode, r.stdout + r.stderr)
        self.assertIn("NOTE: no merge base with origin/main or main", r.stdout)
        self.assertNotIn("FAIL", r.stdout)


if __name__ == "__main__":
    unittest.main()
