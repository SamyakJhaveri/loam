from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
MARKETPLACE_ROOT = ROOT / "cultivation/marketplace"
SAM_CC_ROOT = MARKETPLACE_ROOT / "sam-cc-setup"
MARKETPLACE_MANIFEST = MARKETPLACE_ROOT / ".claude-plugin/marketplace.json"
PLUGIN_MANIFEST = SAM_CC_ROOT / ".claude-plugin/plugin.json"

UPSTREAM_MIT_NOTICE = """MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

TECH_SELECTION_HANDOFF = (
    "For open-ended ideation, route to the local `brainstorming` skill."
)
BRAINSTORMING_HANDOFF = "**The terminal state is invoking writing-plans.**"


def route_contract_errors(
    tech_selection: str,
    brainstorming: str,
) -> list[str]:
    errors: list[str] = []
    if TECH_SELECTION_HANDOFF not in tech_selection:
        errors.append("tech-selection must route to local brainstorming")
    if BRAINSTORMING_HANDOFF not in brainstorming:
        errors.append("brainstorming must terminate at writing-plans")
    return errors


class MarketplaceSkillRoutesTest(unittest.TestCase):
    def load_json(self, path: pathlib.Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_sam_superpowers_is_not_an_installable_plugin(self) -> None:
        marketplace = self.load_json(MARKETPLACE_MANIFEST)
        plugin_names = {plugin["name"] for plugin in marketplace["plugins"]}

        self.assertNotIn("sam-superpowers", plugin_names)
        self.assertFalse((MARKETPLACE_ROOT / "sam-superpowers").exists())

    def test_sam_cc_setup_owns_design_and_planning_skills(self) -> None:
        for skill_name in ("brainstorming", "writing-plans"):
            with self.subTest(skill_name=skill_name):
                self.assertTrue(
                    (SAM_CC_ROOT / "skills" / skill_name / "SKILL.md").is_file()
                )

    def test_design_to_plan_routes_resolve_inside_sam_cc_setup(self) -> None:
        tech_selection_path = SAM_CC_ROOT / "skills/tech-selection/SKILL.md"
        brainstorming_path = SAM_CC_ROOT / "skills/brainstorming/SKILL.md"
        writing_plans_path = SAM_CC_ROOT / "skills/writing-plans/SKILL.md"

        self.assertTrue(tech_selection_path.is_file())
        self.assertTrue(brainstorming_path.is_file())
        self.assertTrue(writing_plans_path.is_file())

        tech_selection = tech_selection_path.read_text(encoding="utf-8")
        brainstorming = brainstorming_path.read_text(encoding="utf-8")

        self.assertEqual([], route_contract_errors(tech_selection, brainstorming))
        self.assertTrue((SAM_CC_ROOT / "skills/brainstorming/SKILL.md").is_file())
        self.assertTrue((SAM_CC_ROOT / "skills/writing-plans/SKILL.md").is_file())

    def test_route_contract_rejects_negated_tech_selection_handoff(self) -> None:
        errors = route_contract_errors(
            "For open-ended ideation, do not route to the local `brainstorming` skill.",
            "**The terminal state is invoking writing-plans.**",
        )

        self.assertIn("tech-selection must route to local brainstorming", errors)

    def test_route_contract_rejects_negated_brainstorming_handoff(self) -> None:
        errors = route_contract_errors(
            "For open-ended ideation, route to the local `brainstorming` skill.",
            "**The terminal state is not invoking writing-plans.**",
        )

        self.assertIn("brainstorming must terminate at writing-plans", errors)

    def test_design_and_planning_skills_have_no_superpowers_dependency(self) -> None:
        dependency_hits: list[str] = []
        for skill_name in ("brainstorming", "writing-plans"):
            skill_root = SAM_CC_ROOT / "skills" / skill_name
            self.assertTrue(skill_root.is_dir())
            for path in skill_root.rglob("*"):
                if path.is_file() and "superpowers:" in path.read_text(
                    encoding="utf-8"
                ):
                    dependency_hits.append(str(path.relative_to(ROOT)))

        self.assertEqual([], dependency_hits)

    def test_sam_cc_setup_manifests_use_version_0_7_0(self) -> None:
        marketplace = self.load_json(MARKETPLACE_MANIFEST)
        marketplace_version = next(
            plugin["version"]
            for plugin in marketplace["plugins"]
            if plugin["name"] == "sam-cc-setup"
        )
        plugin_version = self.load_json(PLUGIN_MANIFEST)["version"]

        self.assertEqual("0.7.0", marketplace_version)
        self.assertEqual("0.7.0", plugin_version)

    def test_upstream_mit_notice_is_preserved_verbatim(self) -> None:
        notice = SAM_CC_ROOT / "THIRD_PARTY_LICENSES/obra-superpowers.txt"

        self.assertTrue(notice.is_file())
        self.assertEqual(UPSTREAM_MIT_NOTICE, notice.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
