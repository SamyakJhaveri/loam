"""A ticket's `skills:` names lint against skills.txt and skill_file, and a Claude worker reads each by path (#385).

`bin/factory lint` runs with FACTORY_ROOT at a temp copy of bin/factory.d (its skills.txt rewritten) and HOME at a
temp tree holding fake plugin caches, so the real allowlist and plugins are never read. The prompt test sources
bin/factory (FACTORY_SOURCED=1) and calls the real build_worker_prompt with a Claude worker.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = """# fixture
Brief:
A fixture.
Blocked by: none

## Goal and why
A fixture.

## Do not touch
The standing list.

## Out of scope
Nothing.

## Done checks
```done-checks
[ -f x ] && pass a || fail a "no x"
```

## Worker
worker: claude
codex-review: no
effort: high
goal: the done-checks block prints no FAIL line, or stop after 60 turns
skills: {skill}

## Decisions
None.
"""


class FactorySkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root = self.tmp / "root"
        shutil.copytree(ROOT / "bin/factory.d", self.root / "bin/factory.d")
        (self.root / "bin/factory.d/skills.txt").write_text("other:missing\n")
        self.home = self.tmp / "home"
        self.pstack = self.home / ".claude/plugins/cache/m/pstack/9.9.9"
        self.tdd = self.skill(self.pstack, "tdd")
        self.skill(self.pstack, "principle-fix-root-causes")
        for name in ("setup-pstack", "sharpen"):
            self.skill(self.pstack, name)
        self.skill(self.home / ".claude/plugins/cache/m/other/1.0.0", "tdd")

    @staticmethod
    def skill(plugin: pathlib.Path, name: str) -> pathlib.Path:
        f = plugin / "skills" / name / "SKILL.md"
        f.parent.mkdir(parents=True)
        f.write_text(f"---\nname: {name}\n---\nA fixture skill.\n")
        return f

    def env(self) -> dict[str, str]:
        return {**os.environ, "FACTORY_ROOT": str(self.root), "HOME": str(self.home)}

    def ticket(self, skill: str) -> pathlib.Path:
        t = self.tmp / "t.md"
        t.write_text(TICKET.format(skill=skill))
        return t

    def lint(self, skill: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(ROOT / "bin/factory"), "lint", str(self.ticket(skill))], cwd=ROOT, env=self.env(),
                              capture_output=True, text=True, check=False)

    def assert_refused(self, skill: str, message: str) -> None:
        proc = self.lint(skill)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(message, proc.stdout + proc.stderr)

    def test_resolving_pstack_name_lints_without_a_skills_txt_line(self) -> None:
        proc = self.lint("pstack:tdd")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_resolving_principle_name_lints(self) -> None:
        proc = self.lint("pstack:principle-fix-root-causes")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_unresolved_worker_pstack_name_is_refused(self) -> None:
        self.assert_refused("pstack:how", "skill 'pstack:how' resolves to no SKILL.md")

    def test_unresolved_pstack_name_is_refused(self) -> None:
        self.assert_refused("pstack:no-such-x", "skill 'pstack:no-such-x' resolves to no SKILL.md")

    def test_pstack_glob_is_refused(self) -> None:
        self.assert_refused("pstack:*", "skill 'pstack:*': a pstack name must be")

    def test_malformed_pstack_name_is_refused(self) -> None:
        for skill in ("pstack:", "pstack:../x", "pstack:a/b"):
            with self.subTest(skill=skill):
                self.assert_refused(skill, f"skill '{skill}': a pstack name must be")

    def test_resolving_human_only_pstack_name_lints(self) -> None:
        # Any installed pstack skill may be named (owner ruling, 30 Oct 2026), not only the worker ones.
        for name in ("setup-pstack", "sharpen"):
            with self.subTest(name=name):
                proc = self.lint(f"pstack:{name}")
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_resolving_name_outside_skills_txt_is_refused(self) -> None:
        self.assert_refused("other:tdd", "unknown skill 'other:tdd': not a line of bin/factory.d/skills.txt")

    def test_allowlisted_name_that_resolves_to_nothing_is_refused(self) -> None:
        self.assert_refused("other:missing", "skill 'other:missing' resolves to no SKILL.md")

    def prompt(self) -> str:
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True, exist_ok=True)
        (run / "frozen/_common.md").write_text("")
        script = '. bin/factory; RUN=$1; WORKER_KIND=claude; BODY=$(cat "$2"); round=1; build_worker_prompt 1'
        proc = subprocess.run(["bash", "-c", script, "_", str(run), str(self.ticket("pstack:tdd"))], cwd=ROOT,
                              env={**self.env(), "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return pathlib.Path(proc.stdout.strip()).read_text()

    def test_claude_prompt_names_the_skill_path_not_the_skill_tool(self) -> None:
        text = self.prompt()
        self.assertIn(f"Before the first edit, read {self.tdd} and follow its steps.", text)
        self.assertNotIn("Skill tool", text)

    def test_claude_prompt_names_the_pstack_adapter_once_when_it_exists(self) -> None:
        self.assertNotIn("claude-code.md", self.prompt())
        adapter = self.pstack / "docs/harness/claude-code.md"
        adapter.parent.mkdir(parents=True)
        adapter.write_text("An adapter.\n")
        text = self.prompt()
        self.assertEqual(text.count(str(adapter)), 1)
        self.assertLess(text.index(str(adapter)), text.index(str(self.tdd)))


if __name__ == "__main__":
    unittest.main()
