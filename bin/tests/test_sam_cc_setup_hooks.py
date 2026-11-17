"""sam-cc-setup's hooks, run as Claude Code runs them: the hook JSON on stdin, exit 2 and stderr to refuse."""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parents[2] / "cultivation/marketplace/sam-cc-setup"
HOOKS = PLUGIN / "hooks"


def run(script: str, event: dict, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(HOOKS / script)], input=json.dumps(event), capture_output=True,
                          text=True, check=False, timeout=30, env={**os.environ, **(env or {})})


class Home(unittest.TestCase):
    """A temporary HOME and CLAUDE_CONFIG_DIR, so no test reads the real user's agents or plugins."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name)
        self.env = {"HOME": str(self.home), "CLAUDE_CONFIG_DIR": str(self.home / ".claude"),
                    "CLAUDE_PROJECT_DIR": str(self.home / "project")}

    def write(self, rel: str, text: str = "x\n") -> pathlib.Path:
        path = self.home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class AgentRouteTest(Home):
    def spawn(self, **tool_input: str) -> subprocess.CompletedProcess[str]:
        return run("agent-route.py", {"hook_event_name": "PreToolUse", "tool_name": "Agent",
                                      "tool_input": {"prompt": "p", **tool_input}}, self.env)

    def test_builtins_refused_naming_the_owner_agent(self) -> None:
        self.write(".claude/agents/worker.md")
        self.write(".claude/agents/scout.md")
        for asked, agent in (("general-purpose", "worker"), ("Explore", "scout")):
            r = self.spawn(subagent_type=asked)
            self.assertEqual(r.returncode, 2, asked)
            self.assertIn(f"`{agent}`", r.stderr)
        self.assertEqual(self.spawn().returncode, 2, "an omitted subagent_type starts general-purpose")

    def test_project_agent_counts(self) -> None:
        self.write("project/.claude/agents/scout.md")
        self.assertEqual(self.spawn(subagent_type="Explore").returncode, 2)

    def test_other_agents_and_missing_replacements_pass(self) -> None:
        self.write(".claude/agents/worker.md")
        for asked in ("worker", "scout", "fork", "claude-code-guide"):
            self.assertEqual(self.spawn(subagent_type=asked).returncode, 0, asked)
        self.assertEqual(self.spawn(subagent_type="Explore").returncode, 0, "no scout defined: keep Explore")


class ForegroundSleepTest(unittest.TestCase):
    REFUSED = (
        "sleep 30",
        "make && sleep 5 && curl x",
        "until [ -f done ]; do sleep 10; done",
        "while ! grep -q ok log; do\n  sleep 5\ndone",
        "timeout 600 bash -c 'until test -f x; do sleep 5; done'",
        "x=$(sleep 2; echo hi)",
        "env A=1 nice -n 5 /bin/sleep 1",
        "cd /tmp && \\\n  sleep 3",
        "ssh-keygen -l -f k; sleep 1 # wait",
    )
    ALLOWED = (
        "bin/tmux-job wait cx-1-abc 1200",
        "~/distbench/bin/tmux-job start J -- bash -c 'until heavy-count --gate-due; do sleep 120; done; exec run'",
        "git grep -n 'sleep [0-9]' -- bin",
        'echo "sleep 5" > note.txt',
        "while read -r f; do wc -l \"$f\"; done < list",
        "cat > s.sh <<'EOF'\nuntil ready; do sleep 5; done\nEOF\nbash -n s.sh",
        "jq . <<<'{\"sleep\": 1}'",
        "python3 -c 'print(1)'",
    )

    def bash(self, command: str, **extra: object) -> subprocess.CompletedProcess[str]:
        return run("no-foreground-sleep.py", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                              "tool_input": {"command": command, **extra}})

    def test_foreground_sleeps_and_poll_loops_refused(self) -> None:
        for command in self.REFUSED:
            r = self.bash(command)
            self.assertEqual(r.returncode, 2, command)
            self.assertIn("run_in_background", r.stderr)
            self.assertIn("tmux-job wait", r.stderr)

    def test_data_detached_jobs_and_job_waits_pass(self) -> None:
        for command in self.ALLOWED:
            self.assertEqual(self.bash(command).returncode, 0, command)

    def test_background_call_passes(self) -> None:
        self.assertEqual(self.bash("sleep 30", run_in_background=True).returncode, 0)

    def assert_refused(self, *commands: str) -> None:
        for command in commands:
            self.assertEqual(self.bash(command).returncode, 2, command)

    def assert_allowed(self, *commands: str) -> None:
        for command in commands:
            self.assertEqual(self.bash(command).returncode, 0, command)

    def test_sleep_in_command_substitution_refused(self) -> None:
        self.assert_refused('echo "$(sleep 1)"', 'echo "x `sleep 1`"', "diff <(sleep 1; echo a) b")
        self.assert_allowed("echo '$(sleep 1)'", 'echo "\\$(sleep 1)"')

    def test_arithmetic_expansion_is_not_a_command(self) -> None:
        self.assert_allowed("printf '%s\\n' \"$((sleep + 1))\"", "n=$(( (sleep * 2) + 1 ))")
        self.assert_refused("n=$((1)); $( (sleep 1) )")

    def test_sleep_behind_leading_redirection_refused(self) -> None:
        self.assert_refused(">out sleep 1", "2>/dev/null sleep 1", "make && </dev/null sleep 1")

    def test_sleep_as_timeout_operand_with_options_refused(self) -> None:
        self.assert_refused("timeout -s TERM 10 sleep 1", "timeout --kill-after 5 --signal KILL 10 sleep 1",
                            "timeout -k 5s --preserve-status 10 sleep 1")

    def test_sleep_only_in_heredoc_data_passes(self) -> None:
        self.assert_allowed("cat <<A <<'B'\nx\nA\nuntil ready; do sleep 5; done\nB\nwc -l f",
                            "cat <<A; cat <<-B\nx\nA\n\tsleep 5\n\tB\nwc -l f")
        self.assert_refused("cat <<A <<B\nx\nA\ny\nB\nsleep 1")

    def test_sleep_in_data_of_a_delimiter_with_non_word_characters_passes(self) -> None:
        self.assert_allowed("cat > s.sh <<'END-X'\nuntil ready; do sleep 5; done\nEND-X\nbash -n s.sh",
                            'cat <<"EOF.1"\nsleep 5\nEOF.1')


class PromptContextTest(Home):
    def prompt(self, text: str) -> str:
        r = run("prompt-context.py", {"hook_event_name": "UserPromptSubmit", "prompt": text}, self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_message_time_is_now_in_utc(self) -> None:
        out = self.prompt("hello")
        stamp = re.search(r"\((\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\)", out)
        self.assertIsNotNone(stamp, out)
        sent = datetime.datetime.strptime(stamp.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        self.assertLess(abs((datetime.datetime.now(datetime.timezone.utc) - sent).total_seconds()), 60)

    def test_pstack_names_map_to_installed_skill_paths(self) -> None:
        pstack = self.home / "pstack-cache"
        skill = self.write("pstack-cache/skills/tdd/SKILL.md")
        installed = {"plugins": {"pstack@cursor-plugins": [{"installPath": str(pstack)}]}}
        self.write(".claude/plugins/installed_plugins.json", json.dumps(installed))
        out = self.prompt("run /pstack:tdd, then /pstack:nope and /pstack:tdd again")
        self.assertEqual(out.count(f"read {skill} now"), 1, out)
        self.assertIn("/pstack:nope: no such pstack skill", out)

    def test_pstack_found_through_config_dir_outside_home(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        config = pathlib.Path(tmp.name)
        skill = self.write("pstack-cache/skills/tdd/SKILL.md")
        installed = {"plugins": {"pstack@cursor-plugins": [{"installPath": str(self.home / "pstack-cache")}]}}
        (config / "plugins").mkdir()
        (config / "plugins/installed_plugins.json").write_text(json.dumps(installed), encoding="utf-8")
        self.env["CLAUDE_CONFIG_DIR"] = str(config)
        self.assertIn(f"read {skill} now", self.prompt("/pstack:tdd"))

    def test_no_pstack_install_reads_nothing_by_path(self) -> None:
        self.assertNotIn(" now, in full", self.prompt("/pstack:tdd"))


class HooksJsonTest(unittest.TestCase):
    def test_registers_each_script_on_its_event(self) -> None:
        hooks = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        wired = {(event, group.get("matcher", ""), re.search(r"hooks/([\w-]+\.py)", h["command"]).group(1))
                 for event, groups in hooks.items() for group in groups for h in group["hooks"]}
        self.assertEqual(wired, {("PreToolUse", "Agent", "agent-route.py"),
                                 ("PreToolUse", "Bash", "no-foreground-sleep.py"),
                                 ("UserPromptSubmit", "", "prompt-context.py")})
        for _, _, script in wired:
            self.assertTrue((HOOKS / script).is_file(), script)


if __name__ == "__main__":
    unittest.main()
