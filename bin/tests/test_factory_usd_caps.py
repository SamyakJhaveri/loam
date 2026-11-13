"""No dollar figure stops, caps or cuts a run, on any billing route (Samyak, 13 Nov 2026).

"there should be no spending cap at all": this widens Decision 6 (12 Nov, no cap on subscription work) to runs whose
calls bill an API key. The distbench F103 proof run had stopped `stopped-cap` at a notional "ticket budget: spent 6.86
of 6 usd". Here `bin/factory` is sourced (FACTORY_SOURCED=1) and the real assert_caps and worker_cmd run over a ledger
past every dollar cap a ticket written before then names, with no API key, with one in the environment, and with one
in the user settings. The wall-clock cap still binds. notify is stubbed, so nothing alerts. No network, no model call.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BILLING = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
# The proof run's old Worker caps, read as a ticket section, and a ledger past each: 6.86 of 6, and a spent day.
CAPS = ("BODY=$'## Worker\\n\\nTICKET_BUDGET_USD=6\\nDAILY_BUDGET_USD=9.5\\nROUND_BUDGET_USD=2.5\\nGRADER_BUDGET_USD=1.5\\n'; "
        "apply_caps\n")


class UsdCapTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "frozen" / "unattended.md").write_text("")
        (self.run_dir / "launched").write_text(f"{int(time.time())}\n")
        (self.run_dir / "ledger.jsonl").write_text(json.dumps({"role": "worker", "cost_usd": 6.8636804}) + "\n")
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        (self.top / "daily.jsonl").write_text(json.dumps({"date": today, "ticket": "t", "cost_usd": 8.0}) + "\n")
        self.settings = self.top / "settings.json"
        self.settings.write_text("{}")

    def sourced(self, script: str, **extra: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in BILLING}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), CLAUDE_SETTINGS_FILE=str(self.settings), **extra)
        prelude = (f"RUN='{self.run_dir}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                   f"DAILY='{self.top}/daily.jsonl'; KEY=t; IS_FILE=1\nnotify() {{ :; }}\n{CAPS}")
        return subprocess.run(["bash", "-c", f". bin/factory\n{prelude}{script}"], cwd=ROOT, env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=60)

    def status(self) -> str:
        path = self.run_dir / "status"
        return path.read_text().strip() if path.exists() else ""

    def test_a_run_past_every_old_dollar_cap_is_not_stopped_on_any_billing_route(self) -> None:
        for name, extra, settings in (("subscription", {}, {}),
                                      ("API key in the environment", {"ANTHROPIC_API_KEY": "sk-ant-test"}, {}),
                                      ("API key in the user settings", {}, {"env": {"ANTHROPIC_API_KEY": "sk-ant-test"}})):
            with self.subTest(name):
                self.settings.write_text(json.dumps(settings))
                proc = self.sourced("assert_caps; echo NOT-STOPPED", **extra)
                self.assertIn("NOT-STOPPED", proc.stdout, proc.stderr)
                self.assertEqual(self.status(), "")

    def test_the_wall_clock_cap_still_binds_a_subscription_run(self) -> None:
        (self.run_dir / "launched").write_text(f"{int(time.time()) - 3 * 3600}\n")
        proc = self.sourced("MAX_HOURS=2; assert_caps; echo NOT-STOPPED")
        self.assertNotIn("NOT-STOPPED", proc.stdout)
        self.assertEqual(self.status(), "stopped-cap")
        self.assertIn("wall clock: 3h of 2h", (self.run_dir / "factory.log").read_text())

    def test_the_worker_call_carries_no_dollar_ceiling_on_an_api_key(self) -> None:
        script = "worker_cmd; printf '%s\\n' \"${WORKER_CMD[@]}\"\n"
        billed = self.sourced(script, ANTHROPIC_API_KEY="sk-ant-test").stdout.splitlines()
        self.assertIn("--max-turns", billed, billed)
        self.assertNotIn("--max-budget-usd", billed)


if __name__ == "__main__":
    unittest.main()
