"""`bin/factory next` sends one needs-you alert when real ticks have read a ready issue, launched none and found no
slot held for over an hour, and no other until the idle spell ends (#619).

Real `cmd_next` ticks run over a gh stand-in on PATH (the repository listing, the runner's assigned listing and the
GraphQL editor read), with `tmux`, `alert` and `date -u +%s` stubbed as shell functions. No network, no `claude`.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLEAN = ROOT / "bin/tests/fixtures/clean-ticket.md"

# Answers next's three reads from the STORE json, {number: {"as": [assignees], "bl": blockers, "body": path}}.
GH = r'''#!/usr/bin/env python3
import json, os, re, subprocess, sys
a = sys.argv[1:]; S = json.load(open(os.environ["STORE"]))
jq = a[a.index("--jq") + 1] if "--jq" in a else "."
p = a[1] if len(a) > 1 else ""
kv = dict(a[i + 1].split("=", 1) for i in range(len(a) - 1) if a[i] in ("-f", "-F"))
d = lambda n, i: {"number": int(n), "user": {"login": "SamyakJhaveri"}, "body": open(i["body"]).read().rstrip("\n") if "body" in i else "x", "pull_request": None, "assignees": [{"login": x} for x in i["as"]], "issue_dependencies_summary": {"blocked_by": i["bl"]}, "repository": {"full_name": "o/r"}}
if p == "graphql":
    ns = re.findall(r"(\w+)\s*:\s*(?:issue|pullRequest)\s*\(\s*number\s*:\s*(\d+)", kv.get("query", ""))
    doc = {"data": {"repository": {k: {"editor": None, "lastEditedAt": None, "closed": False, "state": "OPEN"} for k, n in ns}}}
elif re.match(r"repos/[^/]+/[^/]+/issues\?", p):
    doc = [d(n, i) for n, i in sorted(S.items()) if not ("assignee=none" in p and i["as"])]
elif p.startswith("/issues?"):
    doc = [d(n, i) for n, i in sorted(S.items()) if "SamyakJhaveri" in i["as"]]
elif re.fullmatch(r"repos/[^/]+/[^/]+/issues/\d+", p):
    doc = {"state": "open"}
else:
    sys.exit(2)
r = subprocess.run(["jq", "-r", jq], input=json.dumps(doc), capture_output=True, text=True); sys.stdout.write(r.stdout); sys.exit(r.returncode)
'''

# One tick: every alert but the beat is appended to $T/alerts; $T/alert-fail fails the next one, $T/tmux-fail the launch,
# and $T/has-session makes the pick's tmux session exist already. git is stubbed, so the pull step is refused (no branch)
# and never fetches or fast-forwards the checkout under test.
TICK = r'''. bin/factory; MAIN_CHECKOUT="$T/co"
assert_target_ready() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; git() { :; }
if [ -n "$OTHER" ]; then target_is_loam() { return 1; }; target_repo() { echo Acme/WidGet; }; else target_repo() { echo o/r; }; fi
alert() { [ "$1" = --ping ] && return 0; echo "$*" >> "$T/alerts"; [ -f "$T/alert-fail" ] && { rm -f "$T/alert-fail"; return 1; }; return 0; }
tmux() { case $1 in new-session) [ -f "$T/tmux-fail" ] && return 1; echo "$*" >> "$T/tmux"; return 0 ;; has-session) [ -f "$T/has-session" ] ;; *) return 1 ;; esac; }
date() { if [ "$*" = "-u +%s" ]; then echo "$NOW"; else command date "$@"; fi; }
cmd_next "$@"'''

T0 = 2000000000
BLOCKED = {"99041": {"as": [], "bl": 1}}
LAUNCHABLE = {**BLOCKED, "99042": {"as": [], "bl": 0, "body": str(CLEAN)}}


# The runner exports FACTORY_<CAP> overrides (FACTORY_DAILY_BUDGET_USD=1000000000 on jhaveris), and
# apply_caps lets them beat the defaults these tests rely on, so the ticks start without them (#676).
CAP_NAMES = re.search(r'^CAP_NAMES="([^"]*)"', (ROOT / "bin/factory").read_text(), re.MULTILINE).group(1).replace("\\", " ").split()
RUNNER_FREE_ENV = {k: v for k, v in os.environ.items()
                   if not (k.startswith("FACTORY_") and k[8:] in CAP_NAMES) and k != "FACTORY_JUDGE"}


class IdleAlertTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.t = pathlib.Path(tmp.name)
        (self.t / "gh").write_text(GH)
        (self.t / "gh").chmod(0o755)
        self.runs = self.t / "runs"
        self.runs.mkdir()

    def tick(self, now: int, *flags: str, store: dict | None = None, maxp: int = 1,
             other: bool = False, billed: bool = False, judge: str | None = None) -> subprocess.CompletedProcess[str]:
        """One tick; billed puts an API key in its environment, since only an API-billed runner has a daily budget."""
        (self.t / "store.json").write_text(json.dumps(BLOCKED if store is None else store))
        env = {**RUNNER_FREE_ENV, "PATH": f"{self.t}:{os.environ['PATH']}", "T": str(self.t),
               "STORE": str(self.t / "store.json"), "NOW": str(now), "OTHER": "1" if other else "",
               "FACTORY_SOURCED": "1",
               "FACTORY_ROOT": str(ROOT), "FACTORY_RUNS_ROOT": str(self.runs), "FACTORY_MAX_PARALLEL": str(maxp)}
        env.pop("ANTHROPIC_API_KEY", None)
        if billed:
            env["ANTHROPIC_API_KEY"] = "sk-ant-test"
        if judge is not None:
            env["FACTORY_JUDGE"] = judge
        return subprocess.run(["bash", "-c", TICK, "tick", *flags], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def alerts(self) -> list[str]:
        f = self.t / "alerts"
        return f.read_text().splitlines() if f.exists() else []

    def hold_slot(self) -> None:
        """A pr-opened run with its ticket worktree: it holds a slot until the merge removes the worktree."""
        d = self.runs / "99043" / "k"
        d.mkdir(parents=True)
        (d / "status").write_text("pr-opened\n")
        (d / "factory.log").write_text(
            "2026-11-01T00:00:00Z EXIT pr-opened (0): https://github.com/o/r/pull/99143 after 1 rounds\n")
        (self.t / "co-99043").mkdir()

    def free_slot(self) -> None:
        for p in (self.runs / "99043", self.t / "co-99043"):
            subprocess.run(["rm", "-rf", str(p)], check=True)

    def spell_alerts_after(self, start: int) -> list[int]:
        """Alert counts at 3540 s and 3660 s into a spell whose first idle tick is at `start`."""
        self.tick(start)
        counts = []
        for d in (3540, 3660):
            self.tick(start + d)
            counts.append(len(self.alerts()))
        return counts

    def test_one_alert_after_an_hour_with_its_flags_and_none_at_two_hours(self) -> None:
        counts = []
        for d in (0, 3540, 3660, 7200):
            proc = self.tick(T0 + d)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
            counts.append(len(self.alerts()))
        self.assertEqual(counts, [0, 0, 1, 1])
        a = self.alerts()[0]
        self.assertTrue(a.startswith("--level needs-you --source factory --project loam factory idle: 1 ready-for-agent"), a)
        self.assertTrue((self.runs / "idle-alerted").exists())

    def test_the_count_carries_no_padding_from_a_bsd_wc(self) -> None:
        """macOS wc left-pads its count; the alert text names the bare number."""
        (self.t / "wc").write_text('#!/bin/sh\nprintf \'%8s\\n\' "$(command -p wc "$@" | tr -d \' \')"\n')
        (self.t / "wc").chmod(0o755)
        self.tick(T0)
        self.tick(T0 + 3660)
        self.assertEqual(len(self.alerts()), 1)
        self.assertIn(" factory idle: 1 ready-for-agent", self.alerts()[0])

    def test_another_target_names_its_repository(self) -> None:
        self.tick(T0, other=True)
        self.tick(T0 + 3660, other=True)
        self.assertEqual(len(self.alerts()), 1)
        self.assertIn("--source factory --project widget ", self.alerts()[0])

    def test_a_tick_that_reads_no_issue_ends_the_spell(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3660)
        self.tick(T0 + 7300, store={})
        self.assertFalse((self.runs / "idle-since").exists())
        self.assertEqual(self.spell_alerts_after(T0 + 7400), [1, 2])

    def test_a_launch_ends_the_spell(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3660)
        proc = self.tick(T0 + 3700, store=LAUNCHABLE)
        self.assertEqual(proc.stdout.strip(), "launched #99042", proc.stderr)
        self.assertEqual(self.spell_alerts_after(T0 + 3800), [1, 2])

    def test_a_launch_forwards_the_judge_switch_even_unset(self) -> None:
        # tmux runs the session in its server's environment, so next passes FACTORY_JUDGE with -e, empty when unset.
        self.assertEqual(self.tick(T0, store=LAUNCHABLE, judge="off").stdout.strip(), "launched #99042")
        self.assertEqual(self.tick(T0 + 60, store=LAUNCHABLE).stdout.strip(), "launched #99042")
        first, second = (self.t / "tmux").read_text().splitlines()
        self.assertIn(" -e FACTORY_JUDGE=off ", first)
        self.assertIn(" -e FACTORY_JUDGE= ", second)

    def test_a_paused_tick_ends_the_spell(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3660)
        (self.runs / "FACTORY_STOP").touch()
        self.assertEqual(self.tick(T0 + 3700).stdout.strip(), "paused")
        (self.runs / "FACTORY_STOP").unlink()
        self.assertEqual(self.spell_alerts_after(T0 + 3800), [1, 2])

    def test_a_tick_stopped_at_the_slot_count_ends_the_spell(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3660)
        self.hold_slot()
        self.assertEqual(self.tick(T0 + 3700).stdout.strip(), "nothing to launch")
        self.free_slot()
        self.assertEqual(self.spell_alerts_after(T0 + 3800), [1, 2])

    def test_the_daily_budget_wait_ends_the_spell(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3660)
        today = subprocess.run(["date", "-u", "+%Y-%m-%d"], capture_output=True, text=True, check=True).stdout.strip()
        (self.runs / "ledger-daily.jsonl").write_text(json.dumps({"date": today, "cost_usd": 2000000}) + "\n")
        d = self.runs / "99044" / "k"
        d.mkdir(parents=True)
        (d / "status").write_text("stopped-daily\n")
        proc = self.tick(T0 + 3700, store=LAUNCHABLE, billed=True)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("today's daily budget", proc.stderr)
        self.assertFalse((self.runs / "idle-since").exists())
        (self.runs / "ledger-daily.jsonl").unlink()
        subprocess.run(["rm", "-rf", str(self.runs / "99044")], check=True)
        self.assertEqual(self.spell_alerts_after(T0 + 3800), [1, 2])

    def test_a_candidate_waiting_on_its_own_daily_stop_ends_the_spell(self) -> None:
        self.tick(T0)
        key = hashlib.sha256(CLEAN.read_text().rstrip("\n").encode()).hexdigest()[:8]
        d = self.runs / "99042" / key
        d.mkdir(parents=True)
        (d / "status").write_text("stopped-daily\n")
        proc = self.tick(T0 + 3660, store=LAUNCHABLE, billed=True)
        self.assertIn("waiting #99042: daily budget spent", proc.stderr)
        self.assertEqual(self.alerts(), [])
        self.assertFalse((self.runs / "idle-since").exists())

    def test_ticks_while_a_run_holds_one_of_two_slots_never_count(self) -> None:
        self.hold_slot()
        self.tick(T0, maxp=2)
        self.tick(T0 + 3660, maxp=2)
        self.assertEqual(self.alerts(), [])
        self.free_slot()
        self.assertEqual(self.spell_alerts_after(T0 + 3700), [0, 1])
        self.hold_slot()
        self.tick(T0 + 7400, maxp=2)
        self.assertFalse((self.runs / "idle-since").exists())
        self.free_slot()
        self.assertEqual(self.spell_alerts_after(T0 + 7500), [1, 2])

    def test_a_failed_alert_is_sent_again_once(self) -> None:
        self.tick(T0)
        (self.t / "alert-fail").touch()
        proc = self.tick(T0 + 3660)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("the idle alert failed", proc.stderr)
        self.assertFalse((self.runs / "idle-alerted").exists())
        counts = []
        for d in (3720, 3780):
            self.tick(T0 + d)
            counts.append(len(self.alerts()))
        self.assertEqual(counts, [2, 2])

    def test_a_failed_launch_keeps_the_spell(self) -> None:
        self.tick(T0)
        (self.t / "tmux-fail").touch()
        self.assertEqual(self.tick(T0 + 1800, store=LAUNCHABLE).returncode, 1)
        (self.t / "tmux-fail").unlink()
        self.tick(T0 + 3660)
        self.assertEqual(len(self.alerts()), 1)

    def test_an_existing_tmux_session_keeps_the_spell(self) -> None:
        self.tick(T0)
        (self.t / "has-session").touch()
        self.assertEqual(self.tick(T0 + 1800, store=LAUNCHABLE).stdout.strip(), "nothing to launch")
        (self.t / "has-session").unlink()
        self.tick(T0 + 3660)
        self.assertEqual(len(self.alerts()), 1)

    def test_dry_ticks_neither_alert_nor_move_the_clock(self) -> None:
        self.tick(T0)
        self.tick(T0 + 3700, "--dry-run")
        self.tick(T0 + 5500, "--frontier")
        (self.runs / "FACTORY_STOP").touch()
        self.assertEqual(self.tick(T0 + 6000, "--dry-run").stdout.strip(), "paused")
        (self.runs / "FACTORY_STOP").unlink()
        self.hold_slot()
        self.tick(T0 + 6500, "--dry-run")
        self.free_slot()
        self.tick(T0 + 7360, "--dry-run")
        self.assertEqual(self.alerts(), [])
        self.assertEqual((self.runs / "idle-since").read_text().strip(), str(T0))
        self.tick(T0 + 7420)
        self.assertEqual(len(self.alerts()), 1)


if __name__ == "__main__":
    unittest.main()
