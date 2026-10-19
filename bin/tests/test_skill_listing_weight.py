from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "skill_listing_weight", ROOT / "bin/skill_listing_weight.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


slw = _load_module()


class SummarizeSourceTest(unittest.TestCase):
    def test_counts_skills_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)

            skill_a = root / "skills/a"
            skill_a.mkdir(parents=True)
            (skill_a / "SKILL.md").write_text(
                "---\nname: a\ndescription: alpha desc\n---\nbody\n",
                encoding="utf-8",
            )

            skill_b = root / "skills/b"
            skill_b.mkdir(parents=True)
            (skill_b / "SKILL.md").write_text(
                "---\nname: b\ndisable-model-invocation: true\n"
                "description: beta desc\n---\nbody\n",
                encoding="utf-8",
            )

            agents = root / "agents"
            agents.mkdir()
            (agents / "x.md").write_text(
                "---\nname: x\ndescription: agent desc\n---\nbody\n",
                encoding="utf-8",
            )

            source = {"skills": "skills", "agents": "agents"}
            data = slw.summarize_source(str(root), source)

        self.assertEqual(1, data["model_invocable"])
        self.assertEqual(1, data["manual_only"])
        self.assertEqual(1, data["agents"])
        expected = len("a") + len("alpha desc") + len("x") + len("agent desc")
        self.assertEqual(expected, data["listing_chars"])


class RealRepoTest(unittest.TestCase):
    def test_sam_cc_setup_agent_count(self) -> None:
        source = slw.SOURCES["sam-cc-setup"]
        data = slw.summarize_source(str(ROOT), source)

        agents_dir = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
        self.assertEqual(len(list(agents_dir.glob("*.md"))), data["agents"])
        self.assertEqual(data["skills_chars"] + data["agents_chars"], data["listing_chars"])


class BudgetGateTest(unittest.TestCase):
    def test_budget_fails_only_when_exceeded(self) -> None:
        script = [sys.executable, str(ROOT / "bin/skill_listing_weight.py"), "--root", str(ROOT), "--quiet"]
        over = subprocess.run(script + ["--budget", "seed=0"], capture_output=True, text=True)
        self.assertEqual(1, over.returncode)
        self.assertIn("FAIL: seed listing", over.stderr)
        under = subprocess.run(script + ["--budget", "seed=100000"], capture_output=True, text=True)
        self.assertEqual(0, under.returncode, under.stderr)


if __name__ == "__main__":
    unittest.main()
