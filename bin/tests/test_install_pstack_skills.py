"""The pstack skill installer against a temp HOME holding a fake pstack cache. No pstack install needed."""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "cultivation/marketplace/sam-cc-setup/skills/install-pstack-skills/install-pstack-skills"
SKILLS = re.search(r'^SKILLS="([^"]*)"', SCRIPT.read_text(encoding="utf-8"), re.M).group(1).split()
VERSION = "0.0.1"
SKILL_MD = """---
name: {name}
description: "A fake pstack skill."
disable-model-invocation: true
---

# {name}

Read [the adapter](../../docs/harness/claude-code.md) and [the other skill](../other/SKILL.md).
"""


class InstallPstackSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name)
        self.pstack = self.home / ".claude/plugins/cache/cursor-plugins/pstack" / VERSION
        (self.pstack / "docs/harness").mkdir(parents=True)
        (self.pstack / "docs/harness/claude-code.md").write_text("adapter\n", encoding="utf-8")
        for name in [*SKILLS, "other"]:
            (self.pstack / "skills" / name).mkdir(parents=True)
            (self.pstack / "skills" / name / "SKILL.md").write_text(SKILL_MD.format(name=name), encoding="utf-8")
        self.skills = self.home / ".claude/skills"

    def run_script(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "HOME": str(self.home)}
        return subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True)

    def assert_installed(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(sorted(p.parent.name for p in self.skills.glob("*/.pstack-install")), sorted(SKILLS))
        self.assertEqual(sorted(p.name for p in self.skills.iterdir()), sorted(SKILLS))

    def test_fresh_install_rerun_and_stale_staging(self) -> None:
        stale = self.skills / ".pstack-staging/how.stale"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text("stale\n", encoding="utf-8")
        result = self.run_script()
        self.assert_installed(result)
        self.assertEqual(result.stdout.count(": installed from pstack 0.0.1"), len(SKILLS))
        self.assertFalse((self.skills / ".pstack-staging").exists())
        for name in SKILLS:
            text = (self.skills / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("disable-model-invocation", text, name)
            links = re.findall(r"\]\(([^)]+)\)", text)
            self.assertEqual(len(links), 2, name)
            for link in links:
                self.assertTrue(link.startswith(str(self.pstack) + "/"), link)
                self.assertTrue(pathlib.Path(link).is_file(), link)
        rerun = self.run_script()
        self.assert_installed(rerun)
        self.assertEqual(rerun.stdout.count(": refreshed, pstack 0.0.1 to 0.0.1"), len(SKILLS))

    def test_unmarked_folder_is_refused_and_left_alone(self) -> None:
        self.assert_installed(self.run_script())
        mine = self.skills / "how"
        for child in mine.iterdir():
            child.unlink()
        (mine / "mine.txt").write_text("keep\n", encoding="utf-8")
        result = self.run_script()
        self.assertEqual(result.returncode, 1)
        self.assertIn("how: REFUSED", result.stdout)
        self.assertEqual([p.name for p in mine.iterdir()], ["mine.txt"])
        self.assertEqual(result.stdout.count(": refreshed"), len(SKILLS) - 1)
        self.assertFalse((self.skills / ".pstack-staging").exists())
        self.assertFalse((self.skills / ".pstack-install.lock").exists())


if __name__ == "__main__":
    unittest.main()
