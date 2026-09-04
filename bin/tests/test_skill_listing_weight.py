from __future__ import annotations

import importlib.util
import pathlib
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
    def test_counts_skills_agents_and_workflows(self) -> None:
        wf_desc = "a description, with a comma and an apostrophe's"
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

            workflows = root / "workflows"
            workflows.mkdir()
            (workflows / "w.js").write_text(
                "export const meta = {\n  name: 'w',\n"
                f'  description: "{wf_desc}",\n}}\n',
                encoding="utf-8",
            )

            source = {
                "skills": "skills",
                "agents": "agents",
                "workflows": "workflows",
                "gated": True,
            }
            data = slw.summarize_source(str(root), source)

        self.assertEqual(1, data["model_invocable"])
        self.assertEqual(1, data["manual_only"])
        self.assertEqual(1, data["agents"])
        self.assertEqual(1, data["workflows"])
        expected = (
            len("a") + len("alpha desc")
            + len("x") + len("agent desc")
            + len("w") + len(wf_desc)
        )
        self.assertEqual(expected, data["listing_chars"])


class RealRepoTest(unittest.TestCase):
    def test_sam_cc_setup_agents_and_workflows_counts(self) -> None:
        source = slw.SOURCES["sam-cc-setup"]
        data = slw.summarize_source(str(ROOT), source)

        agents_dir = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
        workflows_dir = ROOT / "cultivation/marketplace/sam-cc-setup/workflows"
        self.assertEqual(len(list(agents_dir.glob("*.md"))), data["agents"])
        self.assertEqual(len(list(workflows_dir.glob("*.js"))), data["workflows"])
        self.assertEqual(
            data["skills_chars"] + data["agents_chars"] + data["workflows_chars"],
            data["listing_chars"],
        )


if __name__ == "__main__":
    unittest.main()
