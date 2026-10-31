"""A ticket's `skills:` names lint against skills.txt and skill_file, and a Claude worker reads each by path (#385).

`bin/factory lint` runs with FACTORY_ROOT at a temp copy of bin/factory.d (its skills.txt rewritten) and HOME at a
temp tree holding fake plugin caches, so the real allowlist and plugins are never read. The prompt test sources
bin/factory (FACTORY_SOURCED=1) and calls the real build_worker_prompt with a Claude worker.
"""

from __future__ import annotations

import json
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

    def test_pstack_skill_that_writes_under_home_lints_with_a_warning(self) -> None:
        proc = self.lint("pstack:setup-pstack")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("lint: OK", proc.stdout)
        self.assertIn("warning: pstack:setup-pstack writes under ~/", proc.stderr)

    def test_pstack_skill_that_stays_in_the_worktree_lints_without_a_warning(self) -> None:
        self.skill(self.pstack, "how")
        proc = self.lint("pstack:how")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("lint: OK", proc.stdout)
        self.assertNotIn("warning", proc.stderr)

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

    def sourced(self, script: str, *args: str) -> str:
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}", "_", *args], cwd=ROOT,
                              env={**self.env(), "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def test_skills_called_leaves_out_a_skill_call_refused_with_an_error(self) -> None:
        def use(i: str, name: str, inp: dict) -> dict:
            return {"type": "tool_use", "id": i, "name": name, "input": inp}
        events = [
            {"type": "assistant", "message": {"content": [
                use("t1", "Skill", {"skill": "pstack:sharpen"}),
                use("t2", "Read", {"file_path": str(self.tdd)}),
                use("t3", "Skill", {"skill": "rigor"}),
                use("t4", "Skill", {"skill": "pstack:setup-pstack"})]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t1", "is_error": True,
                 "content": "cannot be used with Skill tool due to disable-model-invocation"},
                {"type": "tool_result", "tool_use_id": "t3", "content": "ok"}]}},
        ]
        stream = self.tmp / "s.jsonl"
        stream.write_text("not json\n" + "".join(json.dumps(e) + "\n" for e in events))
        out = self.sourced('skills_called "$@"', str(stream), "pstack:tdd", "pstack:sharpen", "rigor",
                           "pstack:setup-pstack", "pstack:principle-fix-root-causes")
        self.assertEqual(out.strip(), "pstack:setup-pstack,pstack:tdd,rigor")

    def test_record_writes_skills_called_on_a_line_given_it_and_no_other(self) -> None:
        res = self.tmp / "result.json"
        res.write_text(json.dumps({"type": "result", "total_cost_usd": 1}))
        led = self.tmp / "ledger.jsonl"
        self.sourced('RUN=$1; LOG=/dev/null; LEDGER=$2; DAILY=$1/daily.jsonl; KEY=7\n'
                     'record 1 worker m "$3" 0 0 0 0 0 pstack:tdd,rigor; record 1 worker m "$3" 0 0 0 0 0 ""\n'
                     'record 1 worker m "$1/none.json" 0 0 0 0 0 rigor; record 1 judge m "$3"',
                     str(self.tmp), str(led), str(res))
        lines = [json.loads(x) for x in led.read_text().splitlines()]
        self.assertEqual([x.get("skills_called") for x in lines], [["pstack:tdd", "rigor"], [], ["rigor"], None])
        self.assertNotIn("skills_called", lines[3])


if __name__ == "__main__":
    unittest.main()
