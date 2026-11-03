"""A `bin/factory next` tick that completes beats the host's healthchecks check; one that refuses does not.

The last run of the day used to pause the check, so the check heard nothing while the cron tick refused for
hours on a precondition (1 Nov 2026). Now every real tick that returns 0 beats, which also resumes a paused
check, a refusing tick stays silent, and no run pauses it, so the check goes red after its grace.

`bin/factory` is sourced (FACTORY_SOURCED=1); `alert` records its arguments, and gh, git, the gates and the
probes are shell functions. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# A tick with an empty frontier: every gate passes, the pull is refused (git prints no branch), gh lists nothing.
STUBS = ("assert_target_ready() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; "
         "pr_closed_events() { :; }; target_repo() { echo o/r; }; git() { :; }; gh() { :; }; "
         'alert() { echo "$*" >> "$ALERTS"; }; ')

# gh for a tick over $GH_TAB: {"ready": the frontier's issues, written by the owner with a body lint fails, "editor": a
# login per issue (none: never edited), "closed": the PRs read closed, "omit": numbers GitHub cannot resolve, "fail":
# every GraphQL read fails with no reply}. GraphQL answers one alias per `<alias>: issue|pullRequest(number: <N>)`; a
# number in omit reads null with an errors entry, and then, as real gh does, the raw body is printed whatever --jq asks,
# the message goes to stderr, and gh exits 1. Any other call exits 2. Each call is one line in $GH_CALLS.
GH = r'''#!/usr/bin/env python3
import json, os, re, subprocess, sys
a = sys.argv[1:]
tab = json.load(open(os.environ["GH_TAB"]))
with open(os.environ["GH_CALLS"], "a") as f:
    f.write(" ".join(a) + "\n")
jq = a[a.index("--jq") + 1] if "--jq" in a else "."
fields = dict(a[i + 1].split("=", 1) for i in range(len(a) - 1) if a[i] == "-f")
path = a[1] if a[:1] == ["api"] and len(a) > 1 else ""
if path == "graphql":
    aliases = re.findall(r"(\w+): (?:issue|pullRequest)\(number: (\d+)\)", fields.get("query", ""))
    if not aliases:
        sys.exit(2)
    if tab.get("fail"):
        sys.exit(1)
    def node(n):
        login = tab["editor"].get(n)
        return {"editor": login and {"login": login}, "lastEditedAt": login and "2026-11-01T00:00:00Z",
                "closed": n in tab["closed"]}
    omit = tab.get("omit", [])
    doc = {"data": {"repository": {k: None if n in omit else node(n) for k, n in aliases}}}
    errors = [{"message": "Could not resolve to an Issue with the number of %s." % n} for k, n in aliases if n in omit]
    if errors:
        print(json.dumps({**doc, "errors": errors}))
        sys.stderr.write("gh: " + errors[0]["message"] + "\n")
        sys.exit(1)
elif path.startswith("repos/") and "/issues?" in path:
    doc = [{"number": int(n), "user": {"login": "SamyakJhaveri"}, "body": "x", "pull_request": None,
            "issue_dependencies_summary": {"blocked_by": 0}} for n in tab["ready"]]
elif path.startswith("/issues?"):
    doc = []
else:
    sys.exit(2)
r = subprocess.run(["jq", "-r", jq], input=json.dumps(doc), capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.exit(r.returncode)
'''

# A real tick against the gh above: the PR phase and the frontier run, and only owner_events, the gates and git are stubbed.
GH_STUBS = ("assert_target_ready() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; "
            "target_repo() { echo o/r; }; git() { :; }; owner_events() { :; }; "
            'alert() { echo "$*" >> "$ALERTS"; }; ')


class NextBeatTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs = pathlib.Path(tmp.name) / "runs"
        self.runs.mkdir()
        self.alerts = pathlib.Path(tmp.name) / "alerts"
        self.alerts.touch()

    def tick(self, pre: str = "", *flags: str, slots: int = 1) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        proc = subprocess.run(
            ["bash", "-c", f". bin/factory\n{STUBS}{pre}cmd_next {' '.join(flags)}"],
            cwd=ROOT, capture_output=True, text=True, check=False,
            env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FACTORY_MAX_PARALLEL": str(slots),
                 "FACTORY_RUNS_ROOT": str(self.runs), "ALERTS": str(self.alerts)},
        )
        return proc, self.alerts.read_text().splitlines()

    def test_a_tick_with_nothing_to_launch_beats(self) -> None:
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_a_paused_timer_beats(self) -> None:
        # FACTORY_STOP is the owner's own pause of the timer, not a fault, so the check stays green.
        (self.runs / "FACTORY_STOP").touch()
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "paused"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_a_refusing_tick_does_not_beat(self) -> None:
        for name, pre in (("login", "claude_logged_in() { return 1; }; "),
                          ("frontier", "gh() { return 1; }; ")):
            with self.subTest(refusal=name):
                self.alerts.write_text("")
                proc, sent = self.tick(pre)
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertEqual(sent, [])

    def test_a_failed_beat_does_not_fail_the_tick(self) -> None:
        proc, _ = self.tick('alert() { echo "$*" >> "$ALERTS"; return 1; }; ')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("healthchecks beat failed", proc.stderr)

    def run_dir(self) -> pathlib.Path:
        d = self.runs / "7" / "abcd1234"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def held_slot(self, status: str, owner: int | None = None) -> pathlib.Path:
        d = self.run_dir()
        (d / "status").write_text(status + "\n")
        (d / "launched").write_text("1\n")
        if owner is not None:
            lstart = subprocess.run(["ps", "-o", "lstart=", "-p", str(owner)], capture_output=True, text=True,
                                    env={**os.environ, "TZ": "UTC", "LC_ALL": "C"}, check=True).stdout.strip()
            (d / "owner").write_text(f"{owner} {lstart}\n")
        return d

    def test_full_slots_held_by_a_suspended_run_do_not_beat(self) -> None:
        # A run stopped whole keeps its lease and owner, so it holds the only slot with no progress; the old run
        # heartbeat stopped with it, and now the tick refuses instead. Continued, the same slot is an idle tick again.
        # The supervisor holds the lease itself, then execs sleep, so the owner pid run_stopped reads is the holder.
        # It touches a marker once it holds the lease, so the wait below never competes with it for the lock.
        lease, held = self.run_dir() / "lease", self.runs.parent / "held"
        sup = subprocess.Popen(["bash", "-c", 'exec 9>> "$1" && flock -n 9 && touch "$2" && exec sleep 60', "_",
                                str(lease), str(held)], start_new_session=True)
        self.addCleanup(sup.wait)
        self.addCleanup(sup.kill)
        for _ in range(100):
            if held.exists():
                break
            self.assertIsNone(sup.poll(), "the supervisor could not take the lease")
            time.sleep(0.05)
        else:
            self.fail("the supervisor never took the lease")
        self.held_slot("running", sup.pid)
        os.kill(sup.pid, signal.SIGSTOP)
        for _ in range(50):
            stat = subprocess.run(["ps", "-o", "stat=", "-p", str(sup.pid)], capture_output=True, text=True).stdout
            if stat.strip().startswith("T"):
                break
            time.sleep(0.1)
        else:
            self.fail("the supervisor never showed as stopped after SIGSTOP")
        for slots in (1, 2):   # a free slot left beside the stopped run must not mask it
            with self.subTest(slots=slots):
                self.alerts.write_text("")
                proc, sent = self.tick(slots=slots)
                self.assertEqual((proc.returncode, proc.stdout.strip()), (1, "nothing to launch"), proc.stderr)
                self.assertIn("is stopped (SIGSTOP or a stopped job)", proc.stderr)
                self.assertEqual(sent, [])
        self.alerts.write_text("")
        os.kill(sup.pid, signal.SIGCONT)
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_full_slots_held_by_a_pr_awaiting_review_beat(self) -> None:
        # A pr-opened run holds its slot while its ticket worktree stands, with no process; that is a normal wait.
        self.held_slot("pr-opened")
        checkout = self.runs.parent / "checkout"
        pathlib.Path(f"{checkout}-7").mkdir()
        proc, sent = self.tick(f"MAIN_CHECKOUT='{checkout}'; ")
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_dry_run_and_frontier_do_not_beat(self) -> None:
        for flag in ("--dry-run", "--frontier"):
            with self.subTest(flag=flag):
                proc, sent = self.tick("", flag)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(sent, [])

    # The tick's GitHub reads do not grow with the candidates it passes over or the pr-opened runs that wait: one
    # GraphQL read gives every candidate's last editor, one every waiting PR's state (#598). Each read may take up to
    # NET_TIMEOUT_SEC, so a count that grew with either let an ok tick outrun the check's 30-minute window.

    def gh_tick(self, tab: dict, prs: tuple[int, ...] = ()) -> tuple[subprocess.CompletedProcess[str], list[str], list[str]]:
        """One real tick against the GH stand-in over `tab`, with a pr-opened run waiting on each PR in `prs`;
        returns the run, the beats sent, and gh's calls, one per line."""
        top = pathlib.Path(tempfile.mkdtemp(dir=self.runs.parent))
        (top / "gh").write_text(GH)
        (top / "gh").chmod(0o755)
        (top / "tab.json").write_text(json.dumps(tab))
        for n in prs:
            d = self.runs / str(n) / "k"
            d.mkdir(parents=True, exist_ok=True)
            (d / "status").write_text("pr-opened\n")
            (d / "factory.log").write_text(f"2026-11-01T00:00:00Z EXIT pr-opened (1): https://github.com/o/r/pull/{n}\n")
        self.alerts.write_text("")
        proc = subprocess.run(
            ["bash", "-c", f". bin/factory\n{GH_STUBS}cmd_next"], cwd=ROOT, capture_output=True, text=True, check=False,
            env={**os.environ, "PATH": f"{top}:{os.environ['PATH']}", "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                 "FACTORY_MAX_PARALLEL": "1", "FACTORY_RUNS_ROOT": str(self.runs), "ALERTS": str(self.alerts),
                 "GH_TAB": str(top / "tab.json"), "GH_CALLS": str(top / "calls")})
        calls = (top / "calls").read_text().splitlines() if (top / "calls").exists() else []
        return proc, self.alerts.read_text().splitlines(), calls

    def test_a_ticks_reads_do_not_grow_with_candidates_or_waiting_prs(self) -> None:
        proc, sent, few = self.gh_tick({"ready": ["11"], "editor": {}, "closed": []}, prs=(9901,))
        self.assertEqual((proc.returncode, proc.stdout, sent), (0, "nothing to launch\n", ["--ping beat"]), proc.stderr)
        for d in self.runs.iterdir():
            shutil.rmtree(d)
        tab = {"ready": ["11", "12", "13", "14", "15", "16"], "editor": {"11": "mallory", "12": "SamyakJhaveri"},
               "closed": ["9903"]}
        proc, sent, many = self.gh_tick(tab, prs=(9901, 9902, 9903, 9904))
        self.assertEqual((proc.returncode, proc.stdout, sent), (0, "nothing to launch\n", ["--ping beat"]), proc.stderr)
        # The two frontier queries, one editor read, one PR-state read, however many of each.
        self.assertEqual((len(few), len(many)), (4, 4), many)
        # Every candidate still gets its own verdict, and only the closed PR's run is marked.
        self.assertIn("not owner #11: written or last edited by mallory", proc.stderr)
        for n in range(12, 17):
            self.assertIn(f"lint failed #{n}: ", proc.stderr)
        self.assertEqual(sorted(d.parent.parent.name for d in self.runs.glob("*/k/pr-closed")), ["9903"])

    def test_a_failed_editor_read_refuses(self) -> None:
        # No reply at all: every candidate is unreadable, so none is linted, and the tick refuses with no beat.
        proc, sent, _ = self.gh_tick({"ready": ["12", "13"], "editor": {}, "closed": [], "fail": True}, prs=(9901,))
        self.assertEqual((proc.returncode, proc.stdout, sent), (1, "nothing to launch\n", []), proc.stderr)
        for n in (12, 13):
            self.assertIn(f"not owner #{n}: could not read the last editor with gh", proc.stderr)
        self.assertNotIn("lint failed", proc.stderr)
        self.assertEqual(list(self.runs.glob("*/k/pr-closed")), [])

    def test_a_candidate_the_editor_read_leaves_out_is_passed_over(self) -> None:
        # GitHub resolves #12 and #14 but not #13 (transferred or deleted since the frontier read): gh exits 1 and
        # prints the raw body, so only #13 is unreadable; the rest are still judged, and the tick refuses with no beat.
        proc, sent, _ = self.gh_tick({"ready": ["12", "13", "14"], "editor": {}, "closed": [], "omit": ["13"]})
        self.assertEqual((proc.returncode, proc.stdout, sent), (1, "nothing to launch\n", []), proc.stderr)
        self.assertIn("not owner #13: could not read the last editor with gh", proc.stderr)
        self.assertNotIn("lint failed #13", proc.stderr)
        for n in (12, 14):
            self.assertIn(f"lint failed #{n}: ", proc.stderr)

    def test_a_pr_the_state_read_leaves_out_waits_while_the_rest_are_marked(self) -> None:
        # GitHub resolves #9901 and #9903 but not #9902: gh exits 1 with the raw body, and only #9902 waits a tick.
        tab = {"ready": [], "editor": {}, "closed": ["9901", "9902", "9903"], "omit": ["9902"]}
        proc, sent, _ = self.gh_tick(tab, prs=(9901, 9902, 9903))
        self.assertEqual((proc.returncode, proc.stdout, sent), (0, "nothing to launch\n", ["--ping beat"]), proc.stderr)
        self.assertEqual(sorted(d.parent.parent.name for d in self.runs.glob("*/k/pr-closed")), ["9901", "9903"])


if __name__ == "__main__":
    unittest.main()
