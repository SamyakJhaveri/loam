from __future__ import annotations

import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECK = ROOT / "bin/check"


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
    script = [sys.executable, str(ROOT / "bin/skill_listing_weight.py"), "--root", str(ROOT), "--quiet"]

    def _measured(self, label: str) -> int:
        return slw.summarize_source(str(ROOT), slw.SOURCES[label])["listing_tokens"]

    def test_budget_fails_when_exceeded(self) -> None:
        over = subprocess.run(self.script + ["--budget", "seed=0"], capture_output=True, text=True)
        self.assertEqual(1, over.returncode)
        self.assertIn("FAIL: seed listing", over.stderr)
        self.assertIn("over the 0-token budget", over.stderr)

    def test_budget_above_listing_fails_with_measured_number(self) -> None:
        n = self._measured("seed")
        under = subprocess.run(self.script + ["--budget", f"seed={n + 1}"], capture_output=True, text=True)
        self.assertEqual(1, under.returncode)
        self.assertIn(f"FAIL: seed listing is {n} tokens, under the {n + 1}-token budget.", under.stderr)
        self.assertIn(f"In this PR, lower its budget in bin/check to {n}.", under.stderr)

    def test_budget_equal_to_listing_passes(self) -> None:
        budgets = ["--budget", f"seed={self._measured('seed')}",
                   "--budget", f"sam-cc-setup={self._measured('sam-cc-setup')}"]
        equal = subprocess.run(self.script + budgets, capture_output=True, text=True)
        self.assertEqual(0, equal.returncode, equal.stderr)
        self.assertEqual("", equal.stderr)

    def test_budget_for_missing_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT / slw.SOURCES["seed"]["skills"], pathlib.Path(tmp) / slw.SOURCES["seed"]["skills"])
            budgets = ["--root", tmp, "--budget", f"seed={self._measured('seed')}", "--budget", "sam-cc-setup=365"]
            missing = subprocess.run(self.script + budgets, capture_output=True, text=True)
        self.assertEqual(1, missing.returncode)
        self.assertIn("FAIL: sam-cc-setup has a budget but cultivation/marketplace/sam-cc-setup/skills is missing.",
                      missing.stderr)


STEP = 'step "skill-listing token weight"'


def listing_step(check: str) -> str:
    """The prelude above the first step, then the skill-listing step, then its exit status."""
    lines = check.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('step "'))
    start = lines.index(STEP)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('step "'))
    return "\n".join(lines[:first] + lines[start:end] + ['exit "$FAIL"']) + "\n"


class CheckStepTest(unittest.TestCase):
    """bin/check's step itself, run on a copy of the listed sources: its budgets equal the measured
    weights, and a shrink with the budget left alone fails the step (#313)."""

    def run_step(self, shrink: bool) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "bin").mkdir()
            shutil.copy(ROOT / "bin/skill_listing_weight.py", root / "bin")
            (root / "bin/check").write_text(listing_step(CHECK.read_text(encoding="utf-8")), encoding="utf-8")
            for source in slw.SOURCES.values():
                for rel in filter(None, (source["skills"], source["agents"])):
                    shutil.copytree(ROOT / rel, root / rel)
            if shrink:  # cut 40 characters from the first listed seed skill's description
                for path in sorted((root / slw.SOURCES["seed"]["skills"]).glob("*/SKILL.md")):
                    text = path.read_text(encoding="utf-8")
                    if not slw._MANUAL.search(text):
                        path.write_text(re.sub(r"(description: )(.{40})", r"\1", text, count=1), encoding="utf-8")
                        break
            return subprocess.run(["bash", "bin/check"], cwd=root, capture_output=True, encoding="utf-8")

    def test_budgets_equal_measured_listings(self) -> None:
        result = self.run_step(shrink=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_shrink_without_lowering_budget_fails(self) -> None:
        result = self.run_step(shrink=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertRegex(result.stderr, r"FAIL: seed listing is (\d+) tokens, under the \d+-token budget\. "
                                        r"In this PR, lower its budget in bin/check to \1\.")
        self.assertIn("FAIL: skill-listing weight not at its budget", result.stdout)


if __name__ == "__main__":
    unittest.main()
