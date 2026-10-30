"""The worker call's model pins hold over user settings, and an old Claude Code is refused (#379).

Claude Code copies each settings tier's env over the launch env, user settings first and `--settings` after, so
freeze adds the four pins to the source env in the frozen worker-settings.json that the worker call loads with
`--settings`.
CLAUDE_CODE_SUBAGENT_MODEL_FORCE exists from 2.1.257, so claude_version_ok refuses an older or unreadable
`claude --version`. `bin/factory` is sourced (FACTORY_SOURCED=1); freeze reads the checkout's graders through
GRADERS_DIR and `claude` is a stub on PATH. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
PINS = ("CLAUDE_CODE_SUBAGENT_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL")


class WorkerPinTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        (self.tmp / "bin").mkdir()

    def sourced(self, script: str, **extra: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in ("RUN", "LOG")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.tmp / "runs"),
                   PATH=f"{self.tmp / 'bin'}:{env['PATH']}", **extra)
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def frozen_env(self, **extra: str) -> tuple[dict[str, str], dict[str, str]]:
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        proc = self.sourced(f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                            f"DECISIONS=\"$RUN/decisions.md\"; GRADERS_DIR='{GRADERS}'; IS_FILE=1; KEY=t; BODY=x; "
                            "freeze && check_frozen && echo frozen", **extra)
        self.assertEqual(proc.stdout.strip(), "frozen", proc.stderr)
        settings = json.loads((run / "frozen/worker-settings.json").read_text())
        source = json.loads((ROOT / "bin/factory.d/worker-settings.json").read_text())
        source_env = source.pop("env", {})
        self.assertEqual({k: v for k, v in settings.items() if k != "env"}, source)  # deny list and hook kept
        return settings["env"], source_env

    def test_freeze_pins_the_default_worker_model_in_the_frozen_settings_env(self) -> None:
        env, source_env = self.frozen_env()
        self.assertEqual(env, {**source_env, **dict.fromkeys(PINS, "claude-opus-5-5"),
                               "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})

    def test_freeze_follows_factory_worker_model(self) -> None:
        env, source_env = self.frozen_env(FACTORY_WORKER_MODEL="claude-other-1")
        self.assertEqual(env, {**source_env, **dict.fromkeys(PINS, "claude-other-1"),
                               "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})

    def version(self, reported: str) -> subprocess.CompletedProcess[str]:
        stub = self.tmp / "bin/claude"
        stub.write_text(f"#!/usr/bin/env bash\n[ \"$1\" = --version ] && printf '%s\\n' '{reported}'\n")
        stub.chmod(0o755)
        return self.sourced('claude_version_ok; echo " rc=$?"')

    def test_claude_version_gate(self) -> None:
        for reported, rc in (("2.1.256 (Claude Code)", 1), ("2.1.257 (Claude Code)", 0),
                             ("2.1.312 (Claude Code)", 0), ("2.2.0 (Claude Code)", 0), ("3.0.1 (Claude Code)", 0),
                             ("2.0.999 (Claude Code)", 1), ("1.9.300 (Claude Code)", 1), ("Claude Code", 1), ("", 1)):
            with self.subTest(reported=reported):
                proc = self.version(reported)
                self.assertEqual(proc.stdout, f"{reported or 'no output'} rc={rc}\n", proc.stderr)

    def test_status_and_next_refuse_an_old_claude(self) -> None:
        self.version("2.1.256 (Claude Code)")
        status = self.sourced("precondition_lines").stdout
        self.assertIn("FAIL claude --version reports '2.1.256 (Claude Code)'; the worker call needs Claude Code "
                      "2.1.257+", status)
        nxt = self.sourced("assert_target_ready() { :; }; claude_logged_in() { :; }; cmd_next --dry-run; echo rc=$?")
        self.assertEqual(nxt.stdout.strip(), "rc=1", nxt.stderr)
        self.assertIn("claude --version reports '2.1.256 (Claude Code)'", nxt.stderr)
        run = self.sourced("assert_target_ready() { :; }; cmd_run nothing; echo rc=$?")
        self.assertEqual(run.returncode, 4, run.stderr)
        self.assertIn("factory run: claude --version reports '2.1.256 (Claude Code)'", run.stderr)
        self.version("2.1.312 (Claude Code)")
        self.assertIn("PASS claude version 2.1.312 (Claude Code)", self.sourced("precondition_lines").stdout)


if __name__ == "__main__":
    unittest.main()
