"""A run on subscription auth has no dollar cap; a run whose calls bill an API key keeps every one (Decision 6).

Samyak, 2026-11-12: no cost gate or cap on subscription building work. The distbench F103 proof run, on a subscription
token, stopped `stopped-cap` at a notional "ticket budget: spent 6.86 of 6 usd" after its round 3 checks passed. Here
`bin/factory` is sourced (FACTORY_SOURCED=1) and the real assert_caps and worker_cmd run over a ledger past every dollar
cap, once with no API key in the environment or the user settings (subscription), once with one in each. The wall-clock
cap still binds a subscription run. notify is stubbed, so nothing alerts. No network, no model call.
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
# The proof run's caps, and a ledger past each: the ticket's 6.86 of 6, and a day with no room for one more round.
CAPS = "TICKET_BUDGET_USD=6; DAILY_BUDGET_USD=9.5; ROUND_BUDGET_USD=2.5; GRADER_BUDGET_USD=1.5; MAX_HOURS=1000\n"


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

    def test_a_subscription_run_past_every_dollar_cap_is_not_stopped(self) -> None:
        proc = self.sourced("assert_caps; echo NOT-STOPPED")
        self.assertIn("NOT-STOPPED", proc.stdout, proc.stderr)
        self.assertEqual(self.status(), "")

    def test_an_api_key_run_past_the_ticket_budget_stops_stopped_cap(self) -> None:
        proc = self.sourced("assert_caps; echo NOT-STOPPED", ANTHROPIC_API_KEY="sk-ant-test")
        self.assertNotIn("NOT-STOPPED", proc.stdout)
        self.assertEqual(self.status(), "stopped-cap")
        self.assertIn("ticket budget: spent 6.8636804 of 6 usd", (self.run_dir / "factory.log").read_text())

    def test_an_api_key_in_the_user_settings_env_keeps_the_caps(self) -> None:
        # A native worker loads the user tier, whose env beats the launch env, so a key there bills the run.
        self.settings.write_text(json.dumps({"env": {"ANTHROPIC_API_KEY": "sk-ant-test"}}))
        proc = self.sourced("assert_caps; echo NOT-STOPPED")
        self.assertNotIn("NOT-STOPPED", proc.stdout)
        self.assertEqual(self.status(), "stopped-cap")

    def test_the_wall_clock_cap_still_binds_a_subscription_run(self) -> None:
        (self.run_dir / "launched").write_text(f"{int(time.time()) - 3 * 3600}\n")
        proc = self.sourced("MAX_HOURS=2; assert_caps; echo NOT-STOPPED")
        self.assertNotIn("NOT-STOPPED", proc.stdout)
        self.assertEqual(self.status(), "stopped-cap")
        self.assertIn("wall clock: 3h of 2h", (self.run_dir / "factory.log").read_text())

    def test_the_worker_call_carries_a_dollar_ceiling_only_on_an_api_key(self) -> None:
        script = "worker_cmd; printf '%s\\n' \"${WORKER_CMD[@]}\"\n"
        sub = self.sourced(script).stdout.splitlines()
        self.assertIn("--max-turns", sub, sub)
        self.assertNotIn("--max-budget-usd", sub)
        billed = self.sourced(script, ANTHROPIC_API_KEY="sk-ant-test").stdout.splitlines()
        self.assertEqual(billed[billed.index("--max-budget-usd") + 1], "2.5")


if __name__ == "__main__":
    unittest.main()
