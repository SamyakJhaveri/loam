"""A ticket's `skills:` names lint against skills.txt and skill_file, and a Claude worker reads each by path (#385).

`bin/factory lint` runs with FACTORY_ROOT at a temp copy of bin/factory.d (its skills.txt rewritten) and HOME at a
temp tree holding fake plugin caches and an installed_plugins.json naming each plugin's installPath, so the real
allowlist and plugins are never read. The prompt test sources
bin/factory (FACTORY_SOURCED=1) and calls the real build_worker_prompt with a Claude worker; the fan-out test
then runs the real factory-round.js under node with stub workflow globals.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import secrets
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
        self.install({"pstack@m": self.pstack, "other@m": self.home / ".claude/plugins/cache/m/other/1.0.0"})

    def install(self, paths: dict[str, pathlib.Path]) -> None:
        plugins = {k: [{"scope": "user", "installPath": str(v)}] for k, v in paths.items()}
        (self.home / ".claude/plugins/installed_plugins.json").write_text(json.dumps({"version": 2, "plugins": plugins}))

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

    def prompt(self, skill: str = "pstack:tdd", size: str = "small") -> str:
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True, exist_ok=True)
        (run / "frozen/_common.md").write_text("")
        script = ('. bin/factory; RUN=$1; WORKER_KIND=claude; DECISIONS=$1/worker/decisions.md; BODY=$(cat "$2"); '
                  'round=1; build_worker_prompt 1')
        proc = subprocess.run(["bash", "-c", script, "_", str(run), str(self.ticket(skill))], cwd=ROOT,
                              env={**self.env(), "FACTORY_SOURCED": "1", "WORKER_SIZE": size},
                              capture_output=True, text=True, check=False)
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

    def builder_prompts(self, args: str) -> list[str]:
        # factory-round.js under node, its workflow globals stubbed: the planner splits two tasks, every other agent
        # returns at once, and each Build agent's prompt is collected.
        script = """
const [f, a] = process.argv.slice(1); const seen = [];
Object.assign(globalThis, {args: JSON.parse(a), phase() {}, log() {}, parallel: (fs) => Promise.all(fs.map((g) => g())),
  agent: async (p, o) => {
    if (o.phase === "Plan") return {solo: false, goal: "g", tasks: [
      {objective: "a", owns: ["a/**"], check: "true"}, {objective: "b", owns: ["b/**"], check: "true"}]};
    if (o.phase === "Build") seen.push(p);
    return {solo: false, checks: ""};
  }});
await import("file://" + f);
console.log(JSON.stringify(seen));"""
        proc = subprocess.run(["node", "--no-warnings", "--input-type=module", "-e", script,
                               str(ROOT / "bin/factory.d/factory-round.js"), args],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_each_fan_out_builder_gets_the_lead_skill_lines_in_order(self) -> None:
        # The #523 done check: a large round's Workflow args carry the lead's skill lines and factory-round.js appends
        # them, unchanged and in order, to every builder prompt. Names are fresh per run, so no side can rebuild them.
        a1, a2, a3 = (f"{c}{secrets.token_hex(4)}" for c in "kmq")
        bare = []
        for name in (a1, a2):
            f = self.home / ".claude/skills" / name / "SKILL.md"
            f.parent.mkdir(parents=True)
            f.write_text("A fixture skill.\n")
            bare.append(f)
        s3 = self.skill(self.pstack, a3)
        adapter = self.pstack / "docs/harness/claude-code.md"
        adapter.parent.mkdir(parents=True)
        adapter.write_text("An adapter.\n")
        want = "\n".join([f"Before the first edit, read {bare[0]} and follow its steps.",
                          f"Before the first pstack skill, read {adapter}, which maps its tool names to Claude Code.",
                          f"Before the first edit, read {s3} and follow its steps.",
                          f"Before the first edit, read {bare[1]} and follow its steps."])
        text = self.prompt(f"{a1}, pstack:{a3}, {a2}", size="large")
        self.assertIn(want, text)
        (args,) = re.findall(r"and args `(\{.*\})`\.", text)
        builders = self.builder_prompts(args)
        self.assertEqual(len(builders), 2)
        for p in builders:
            self.assertIn(want, p)

    def test_builder_prompt_with_no_skill_lines_adds_nothing(self) -> None:
        args = json.dumps({"ticket": "t", "run": "r"})
        for p in self.builder_prompts(args):
            self.assertIn("}\n\nDo:\n", p)
        self.assertEqual(self.builder_prompts(json.dumps({"ticket": "t", "run": "r", "skills": []})),
                         self.builder_prompts(args))

    def sourced(self, script: str, *args: str) -> str:
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}", "_", *args], cwd=ROOT,
                              env={**self.env(), "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def skill_file(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", "-c", '. bin/factory; skill_file "$1"', "_", name], cwd=ROOT,
                              env={**self.env(), "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)

    def test_plugin_skill_resolves_at_its_install_path_not_the_newest_cache_folder(self) -> None:
        for folder in ("m/pstack/10.0.0", "zz/pstack/99.0.0"):
            self.skill(self.home / ".claude/plugins/cache" / folder, "tdd")
        self.assertEqual(self.skill_file("pstack:tdd").stdout, f"{self.tdd}\n")

    def test_plugin_with_no_installed_entry_resolves_to_nothing(self) -> None:
        self.skill(self.home / ".claude/plugins/cache/m/gone/1.0.0", "tdd")
        proc = self.skill_file("gone:tdd")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(proc.stdout, "")

    def test_plugin_skill_resolves_to_nothing_without_installed_plugins_json(self) -> None:
        # Fails closed, no cache-search fallback (owner ruling, 30 Oct 2026, #437).
        (self.home / ".claude/plugins/installed_plugins.json").unlink()
        proc = self.skill_file("pstack:tdd")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(proc.stdout, "")

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

    def skills(self, home: pathlib.Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(ROOT / "bin/factory"), "skills"], cwd=ROOT, env={**os.environ, "HOME": str(home)},
                              capture_output=True, text=True, check=False)

    def test_skills_lists_home_and_asks_lines_of_the_resolved_copy_only(self) -> None:
        # The #472 done check: a writer of ~/.cursor/rules/, an asker, and a plain skill whose older cached copy
        # names ~/, which a listing of every cached version, not the copy skill_file resolves, would print.
        home = self.tmp / "skills-home"
        cache = home / ".claude/plugins/cache/cursor-plugins/pstack"
        (cache / "1.0.0/skills").mkdir(parents=True)
        bodies = {"writer": "Step 1.\nWrite `~/.cursor/rules/x.mdc` with the budget.\n",
                  "asker": "Use the AskQuestion tool to pick a budget.\n",
                  "plain": "Read the diff and name each defect.\n"}
        for name, body in bodies.items():
            f = cache / "1.0.0/skills" / name / "SKILL.md"
            f.parent.mkdir()
            f.write_text(f"---\nname: {name}\n---\n{body}")
        # The older writer copy also matches, so a listing that resolved a name once per cached version prints it twice.
        for name in ("plain", "writer"):
            old = cache / "0.9.0/skills" / name / "SKILL.md"
            old.parent.mkdir(parents=True)
            old.write_text(f"---\nname: {name}\n---\nWrite `~/.old/x` first.\n")
        (home / ".claude/plugins/installed_plugins.json").write_text(
            json.dumps({"version": 2, "plugins": {"pstack@cursor-plugins": [{"installPath": str(cache / "1.0.0")}]}}))
        proc = self.skills(home)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        skill = cache / "1.0.0/skills"
        self.assertEqual(proc.stdout.splitlines(), [
            f"asker\tasks\t{skill}/asker/SKILL.md:4: Use the AskQuestion tool to pick a budget.",
            f"writer\thome\t{skill}/writer/SKILL.md:5: Write `~/.cursor/rules/x.mdc` with the budget.",
        ])

    def test_skills_lists_every_matching_line_cut_to_160_characters(self) -> None:
        f = self.pstack / "skills/sharpen/SKILL.md"
        long = "Write $HOME/.cursor/x then ask with AskUserQuestion. " + "x" * 200
        f.write_text(f"---\nname: sharpen\n---\nRead `~/.a` first.\n{long}\n")
        lines = [x for x in self.skills(self.home).stdout.splitlines() if x.startswith("sharpen\t")]
        self.assertEqual(lines, [f"sharpen\thome\t{f}:4: Read `~/.a` first.", f"sharpen\thome\t{f}:5: {long[:160]}",
                                 f"sharpen\tasks\t{f}:5: {long[:160]}"])

    def test_skills_with_no_pstack_installed_says_so_and_exits_0(self) -> None:
        home = self.tmp / "empty-home"
        home.mkdir()
        proc = self.skills(home)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(len(proc.stdout.splitlines()), 1, proc.stdout)
        self.assertIn("no installed pstack skill", proc.stdout)

    def test_skills_refuses_an_argument(self) -> None:
        proc = subprocess.run([str(ROOT / "bin/factory"), "skills", "x"], cwd=ROOT, env={**os.environ, "HOME": str(self.home)},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage: bin/factory skills", proc.stderr)


if __name__ == "__main__":
    unittest.main()
