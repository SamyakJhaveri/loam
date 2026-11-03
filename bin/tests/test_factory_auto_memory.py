"""Worker and grader calls load and write no auto memory (#380).

Claude Code keeps one auto memory folder per repository, filled by interactive sessions, and no settings source
turns it off. Both factory settings files set `autoMemoryEnabled: false`, and pin CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
in their env because that variable, from the launch env or a user-tier env, beats the key, while the `--settings`
env is applied last. Neither sets `claudeMdExcludes`: both calls load no settings tier (`--setting-sources ''`), so
no user CLAUDE.md or rules load, whatever the config dir (#505). Both turn compaction on at 450K tokens over the user
tier's `autoCompactEnabled: false`, so a long call compacts instead of failing (#348). Checks the source settings and
the real freeze path, sourced with FACTORY_SOURCED=1 as in test_factory_worker_pins.py. No network or Claude call.
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


class AutoMemoryOffTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)

    def sourced(self, script: str, **extra: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in ("RUN", "LOG")}
        env.update(extra)
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.tmp / "runs"))
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def test_worker_and_role_settings_turn_auto_memory_off(self) -> None:
        for name in ("worker-settings.json", "role-settings.json"):
            with self.subTest(name=name):
                settings = json.loads((ROOT / "bin/factory.d" / name).read_text())
                self.assertIs(settings.get("autoMemoryEnabled"), False)
                self.assertEqual(settings.get("env", {}).get("CLAUDE_CODE_DISABLE_AUTO_MEMORY"), "1")

    def test_worker_and_role_settings_set_no_claude_md_excludes(self) -> None:
        for name in ("worker-settings.json", "role-settings.json"):
            with self.subTest(name=name):
                settings = json.loads((ROOT / "bin/factory.d" / name).read_text())
                self.assertNotIn("claudeMdExcludes", settings)

    def test_frozen_worker_and_role_settings_set_no_claude_md_excludes(self) -> None:
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        proc = self.sourced(f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                            f"DECISIONS=\"$RUN/decisions.md\"; GRADERS_DIR='{GRADERS}'; IS_FILE=1; KEY=t; BODY=x; "
                            "freeze && check_frozen && echo frozen")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "frozen", proc.stderr)
        for name in ("worker-settings.json", "role-settings.json"):
            with self.subTest(name=name):
                settings = json.loads((run / "frozen" / name).read_text())
                self.assertNotIn("claudeMdExcludes", settings)

    def test_frozen_settings_compact_at_450k_over_a_user_off_switch(self) -> None:
        user = self.tmp / "user-settings.json"
        user.write_text(json.dumps({"autoCompactEnabled": False, "autoCompactWindow": 200000,
                                   "modelSettings": {"claude-opus-5-5": {"autoCompactWindow": 900000, "effortLevel": "high"}}}))
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        proc = self.sourced(f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                            f"DECISIONS=\"$RUN/decisions.md\"; GRADERS_DIR='{GRADERS}'; IS_FILE=1; KEY=t; BODY=x; "
                            "freeze && check_frozen && echo frozen", CLAUDE_SETTINGS_FILE=str(user))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "frozen", proc.stderr)
        for name in ("worker-settings.json", "role-settings.json"):
            with self.subTest(name=name):
                settings = json.loads((run / "frozen" / name).read_text())
                self.assertIs(settings.get("autoCompactEnabled"), True)
                self.assertEqual(settings.get("autoCompactWindow"), 450000)
                for model, ms in (settings.get("modelSettings") or {}).items():
                    self.assertNotIn("autoCompactWindow", ms, f"{name}: {model} keeps a per-model window over 450K")


if __name__ == "__main__":
    unittest.main()
