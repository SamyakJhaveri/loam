"""The full gate runs once, last (docs/factory/LOOP.md, step 6; ASK-KARPATHY item B).

`bin/factory -C <target> run` on a file ticket whose done-checks block has a `guard bin/check` line, with a scripted
`claude`: round 0 and each round's checks defer bin/check, and the supervisor runs the whole block once the graders
pass. Round 0 at base never runs it; a round the judge fails costs no bin/check run; a gate that goes red after the
graders hands its FAIL lines to the next worker round, and the PR opens only after a green gate. The target's bin/check
logs each run to a file.
A ticket no round could pass ends ticket-defect before any worker call: a guard that FAILs on base (Loam issue 726),
or an Edit: path the Do not touch section fences off and no Except: frees (distbench L01 run 1).
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

from test_factory_mutation_sweep import ENVELOPE, git, learn_done, scratch_env

ROOT = pathlib.Path(__file__).resolve().parents[2]
# The scripted claude: a worker that copies $d/round-<n>/ into its worktree, runs $d/round-<n>.sh there, and commits;
# a judge whose n-th call replies $d/judge-<n>.json when it exists, else $d/judge.json; a reviewer with no finding.
CLAUDE = r"""#!/bin/sh
[ "$1" = --version ] && { echo "2.1.300 (Claude Code)"; exit 0; }
[ "$1" = -p ] || exit 1
d=$(dirname "$0")/..
case "$*" in
  *json-schema*rows*)
    cat > "$d/judge-prompt-last.txt"
    j=$(( $(cat "$d/judge-calls" 2> /dev/null || echo 0) + 1 )); echo "$j" > "$d/judge-calls"
    if [ -f "$d/judge-$j.json" ]; then cat "$d/judge-$j.json"; else cat "$d/judge.json"; fi; exit 0 ;;
  *json-schema*) cat > /dev/null; cat "$d/review.json"; exit 0 ;;
esac
n=$(( $(cat "$d/rounds" 2> /dev/null || echo 0) + 1 )); echo "$n" > "$d/rounds"
cat > "$d/prompt-$n.txt"
[ -d "$d/round-$n" ] && cp -R "$d/round-$n/." .
[ -f "$d/round-$n.sh" ] && sh "$d/round-$n.sh"
git add -A > /dev/null 2>&1; git commit -qm "round $n" > /dev/null 2>&1
cat "$d/worker.json"
"""
PASS = {"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": [],
        "backlog": [], "evidence": {}}
FAIL = {"verdict": "fail", "rows": {"correct": "fail", "verified": "pass", "honest": "pass"},
        "fixes": ["add more"], "backlog": [], "evidence": {}}
TICKET = """# gate probe
Brief: x
Blocked by: none

## Goal and why
g

## Do not touch
The standing list.

## Out of scope
o

## Done checks
```done-checks
[ -f note.txt ] && pass note || fail note "no note.txt"
out=$(guard bin/check 2>&1); rc=$?; last=$(tail -n 1 <<<"$out"); [ "$rc" = 0 ] && [ "$last" = "check: PASSED" ] && pass check-green || fail check-green "rc $rc, last line: $last"
```

## Worker
worker: claude
codex-review: no
effort: low
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 5 turns

## Decisions
none
"""


class GateLastTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        env = scratch_env(self.top)
        co = self.top / "co"
        origin = self.top / "github.com/o/r.git"
        origin.mkdir(parents=True)
        git(origin, env, "init", "-q", "--bare")
        (co / "bin").mkdir(parents=True)
        (co / "docs/factory").mkdir(parents=True)
        # bin/check logs each run with the tree it ran on; red.txt in the tree makes it red.
        (co / "bin/check").write_text(f'#!/bin/sh\necho "$(ls | tr "\\n" " ")" >> {self.top}/gate-runs\n'
                                      '[ -f red.txt ] && { echo "check: FAILED"; exit 1; }\necho "check: PASSED"\n')
        (co / "bin/check").chmod(0o755)
        (co / "docs/factory/STANDING.md").write_text("## Standing do-not-touch list\n\n- bin/check\n")
        git(co, env, "init", "-q", "-b", "main")
        git(co, env, "remote", "add", "origin", str(origin))
        git(co, env, "add", "-A")
        git(co, env, "commit", "-qm", "base")
        git(co, env, "push", "-q", "-u", "origin", "main")
        stubs = self.top / "bin"
        stubs.mkdir()
        (stubs / "claude").write_text(CLAUDE)
        (stubs / "claude").chmod(0o755)
        for name, reply in (("judge", json.dumps(PASS)), ("review", '{"verdict":"merge","findings":[]}'),
                            ("worker", "CLAIM: done")):
            (self.top / f"{name}.json").write_text(json.dumps({**ENVELOPE, "result": reply}) + "\n")
        (self.top / "gprobe.md").write_text(TICKET)
        env["PATH"] = f"{stubs}:{ROOT / 'bin/tests/fixtures/systemd'}:{env['PATH']}"
        self.env = env
        self.co = co

    def worker_round(self, n: int, files: dict[str, str], script: str = "") -> None:
        d = self.top / f"round-{n}"
        d.mkdir()
        for name, text in files.items():
            (d / name).write_text(text)
        if script:
            (self.top / f"round-{n}.sh").write_text(script)

    def launch(self, ok: bool = True) -> str:
        r = subprocess.run([str(ROOT / "bin/factory"), "-C", str(self.co), "run", str(self.top / "gprobe.md")],
                           cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=300, check=False)
        learn_done(self.top)
        if ok:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (run,) = (self.top / "h/.local/state/loam-factory/runs/o__r/gprobe").glob("*/")
        self.run = run
        return (run / "factory.log").read_text()

    def gate_runs(self) -> list[str]:
        return (self.top / "gate-runs").read_text().splitlines()

    def test_a_judge_fail_round_costs_no_gate_run(self) -> None:
        (self.top / "judge-1.json").write_text(json.dumps({**ENVELOPE, "result": json.dumps(FAIL)}) + "\n")
        self.worker_round(1, {"note.txt": "1\n"})
        self.worker_round(2, {"more.txt": "2\n"})
        log = self.launch()
        self.assertEqual((self.top / "rounds").read_text().strip(), "2")
        # one run, after round 2's graders passed; none in round 0, round 1 or round 2's own checks
        self.assertEqual(len(self.gate_runs()), 1, self.gate_runs())
        self.assertIn("more.txt", self.gate_runs()[0])
        self.assertEqual(log.count(" full gate at "), 1, log)
        self.assertEqual(log.count("checks: all pass, bin/check deferred until the graders pass"), 2, log)
        self.assertLess(log.index("judge verdict: pass"), log.index(" full gate at "))
        self.assertIn("Supervisor note: this round deferred the full gate.",
                      (self.top / "judge-prompt-last.txt").read_text())
        self.assertIn("DEFERRED: bin/check", (self.run / "round-2.cheap.checks").read_text())
        checks = (self.run / "round-2.checks").read_text()
        self.assertNotIn("DEFERRED", checks)
        self.assertIn("check: PASSED\n\nPASS check-green\n", checks)
        self.assertFalse((self.run / "pr-body.md").read_text().startswith("Draft:"))

    def test_a_red_gate_after_the_graders_goes_to_the_next_worker_round(self) -> None:
        self.worker_round(1, {"note.txt": "1\n", "red.txt": "red\n"})
        self.worker_round(2, {}, "git rm -q red.txt\n")
        log = self.launch()
        self.assertEqual((self.top / "rounds").read_text().strip(), "2")
        self.assertEqual(log.count(" full gate at "), 2, log)
        self.assertIn("full gate failing: check-green,", log)
        self.assertIn("full gate: all pass", log)
        self.assertIn("FAIL check-green: rc 1, last line: check: FAILED", (self.top / "prompt-2.txt").read_text())
        self.assertFalse((self.run / "pr-body.md").read_text().startswith("Draft:"))
        self.assertEqual(subprocess.run(["git", "-C", str(self.co), "worktree", "list"], capture_output=True,
                                        text=True, env=self.env, check=True).stdout.count("\n"), 1)

    def test_a_guard_line_after_unterminated_output_still_gets_the_full_gate(self) -> None:
        # The DEFERRED marker starts a fresh line, so text the block printed before it cannot hide it from gate_last.
        (self.top / "gprobe.md").write_text(TICKET.replace(
            'out=$(guard bin/check 2>&1); rc=$?; last=$(tail -n 1 <<<"$out"); [ "$rc" = 0 ] && [ "$last" = "check: PASSED" ]',
            "rc=; last=; printf 'checking gate...'; guard bin/check > /dev/null"))
        self.worker_round(1, {"note.txt": "1\n", "red.txt": "red\n"})
        self.worker_round(2, {}, "git rm -q red.txt\n")
        log = self.launch()
        self.assertIn("full gate failing: check-green,", log)
        self.assertEqual((self.top / "rounds").read_text().strip(), "2")

    def test_a_relaunch_after_a_cap_stop_before_the_checks_grades_that_round_with_no_new_worker_call(self) -> None:
        # Round 1's worker call ends past the 4 h cap, so the run stops before its checks; the relaunch runs them and
        # grades the round instead of paying for its worker call again.
        self.worker_round(1, {"note.txt": "1\n"}, 'for f in "$HOME"/.local/state/loam-factory/runs/o__r/gprobe/*/launched; do '
                          'echo $(( $(date -u +%s) - 5 * 3600 )) > "$f"; done\n')
        self.env["FACTORY_MAX_HOURS"] = "4"
        self.launch(ok=False)
        self.assertEqual((self.run / "status").read_text().strip(), "stopped-cap")
        self.assertFalse((self.run / "round-1.checks").exists())
        self.launch()
        self.assertEqual((self.top / "rounds").read_text().strip(), "1")
        self.assertEqual((self.run / "status").read_text().strip(), "pr-opened")

    def test_a_relaunch_of_an_abandoned_round_abandons_again_without_grading(self) -> None:
        self.worker_round(1, {"note.txt": "1\n"}, 'for f in "$HOME"/.local/state/loam-factory/runs/o__r/gprobe/*/worker/decisions.md; do '
                          'echo "ABANDON note owner must rewrite this ticket" >> "$f"; done\n')
        for _ in range(2):
            self.launch(ok=False)
            self.assertEqual((self.run / "status").read_text().strip(), "abandon")
        self.assertEqual((self.top / "rounds").read_text().strip(), "1")
        self.assertFalse((self.top / "judge-calls").exists())

    def test_round_zero_still_ends_on_a_non_guard_check_that_passes_on_base(self) -> None:
        (self.co / "note.txt").write_text("base\n")
        git(self.co, self.env, "add", "note.txt")
        git(self.co, self.env, "commit", "-qm", "note on base")
        git(self.co, self.env, "push", "-q")
        # round 0 still stops a check that passes on base, before any round and without running bin/check
        self.launch(ok=False)
        self.assertEqual((self.run / "status").read_text().strip(), "ticket-defect")
        self.assertFalse((self.top / "rounds").exists())
        self.assertFalse((self.top / "gate-runs").exists(), "round 0 ran bin/check")

    def test_round_zero_ends_on_a_guard_that_fails_on_base(self) -> None:
        # A guard may pass on base, but one that FAILs there fails in every round (W44a run 319b2cfc paid a round for it).
        (self.top / "gprobe.md").write_text(TICKET.replace(
            "```\n\n## Worker", 'guard test -f base.txt && pass base-file || fail base-file "no base.txt"\n```\n\n## Worker'))
        self.worker_round(1, {"note.txt": "1\n", "base.txt": "1\n"})
        log = self.launch(ok=False)
        self.assertEqual((self.run / "status").read_text().strip(), "ticket-defect")
        self.assertIn("guard check base-file fails on", log)
        self.assertFalse((self.top / "rounds").exists(), "a worker ran")

    def edit_ticket(self, do_not_touch: str) -> None:
        (self.top / "gprobe.md").write_text(TICKET.replace("Blocked by: none", "Blocked by: none\nEdit: `bin/check`.")
                                            .replace("The standing list.", do_not_touch))

    def test_freeze_ends_on_an_edit_path_do_not_touch_fences_off(self) -> None:
        # The worker must edit bin/check, and every round's do-not-touch check would fail it (L01 run 1 lost 83 min).
        self.edit_ticket("The standing list.\nExcept: the files on the header's Edit line.")
        log = self.launch(ok=False)
        self.assertEqual((self.run / "status").read_text().strip(), "ticket-defect")
        self.assertIn("the Edit line names bin/check, which Do not touch fences off", log)
        self.assertFalse((self.run / "round-0.out").exists(), "round 0 ran")
        self.assertFalse((self.top / "rounds").exists(), "a worker ran")
        # no ticket worktree left for the corrected body to reuse
        self.assertEqual(subprocess.run(["git", "-C", str(self.co), "worktree", "list"], capture_output=True,
                                        text=True, env=self.env, check=True).stdout.count("\n"), 1)

    def test_an_edit_path_an_except_line_frees_proceeds(self) -> None:
        self.edit_ticket("The standing list.\nExcept: `bin/check`.")
        self.worker_round(1, {"note.txt": "1\n"})
        self.launch()
        self.assertEqual((self.top / "rounds").read_text().strip(), "1")
        self.assertEqual((self.run / "status").read_text().strip(), "pr-opened")


if __name__ == "__main__":
    unittest.main()
