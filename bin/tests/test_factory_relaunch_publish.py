"""A relaunch whose last round passed the graders at HEAD opens the PR with no worker round (#383).

`bin/factory` is sourced (FACTORY_SOURCED=1) and cmd_run runs a file ticket over a throwaway repository, twice.
The first launch's worker commits the marker, the real checks pass, the stub graders write their files, and a
stub open_pr fails as a lost push does. The second launch's worker only counts its calls; its open_pr is the
real one, which for a file ticket writes the body and exits pr-opened with no GitHub call. No network, no `claude`.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
TICKET = """# Relaunch fixture

## Goal and why
fixture

## Done checks

```done-checks
[ -f marker ] && pass has-marker || fail has-marker "no marker"
```
"""
STUBS = ("assert_target_ready() { :; }; claude_version_ok() { :; }; exec_frozen() { :; }; "
         "heartbeat_start() { :; }; heartbeat_stop() { :; }")
JUDGE_PASS = """run_judge() { echo '{"verdict":"pass","rows":{}}' > "$RUN/round-$1.judge.json"; }"""
JUDGE_FAIL = """run_judge() { echo '{"verdict":"fail","rows":{"a":"fail"}}' > "$RUN/round-$1.judge.json"; return 1; }"""
REVIEW_CLEAN = """run_review() { echo '{"findings":[]}' > "$RUN/round-$1.review.json"; }"""
# A high finding past the reviewer's one block: the graders pass and the PR would open as a draft.
REVIEW_BLOCKING = ("""run_review() { echo '{"findings":[{"severity":"high","file":"f","line":1,"defect":"d","fix":"x"}]}'"""
                   """ > "$RUN/round-$1.review.json"; }""")
FIRST = ("""worker_round() { [ -e "$WORKTREE/marker" ] && return 0; touch "$WORKTREE/marker"; git -C "$WORKTREE" add marker; """
         """git -C "$WORKTREE" -c user.name=t -c user.email=t@t commit -q -m work; }; """
         """open_pr() { finish stopped-environment "git push of $BRANCH failed (stub)"; }""")
SECOND = """worker_round() { echo worker >> "$RUN/../relaunch-worker-calls"; }"""


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class RelaunchPublishTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.main, self.runs = self.top / "main", self.top / "runs"
        self.ticket = self.top / "rl.md"
        self.ticket.write_text(TICKET)
        self.main.mkdir()
        git("init", "-q", "-b", "main", cwd=self.main)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.main)

    def launch(self, *stubs: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.runs),
                   FACTORY_WORKTREE=str(self.top / "wt"), FACTORY_WORKER_ADVISOR="")
        script = (f". bin/factory\n{STUBS}\n" + "\n".join(stubs)
                  + f"\nMAIN_CHECKOUT='{self.main}'; GRADERS_DIR='{GRADERS}'\ncmd_run '{self.ticket}'")
        return subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True, check=False)

    def relaunch(self, judge: str, review: str, move_head: bool = False, edit_frozen: bool = False) -> tuple[str, int]:
        """The status and worker-call count after a first launch with these graders and one relaunch."""
        first = self.launch(judge, review, FIRST)
        self.assertNotEqual(first.returncode, 0, first.stderr)
        if move_head:  # a commit on the branch after grading, as a hand fix between launches would leave
            (branch,) = git("for-each-ref", "--format=%(refname)", "refs/heads/factory/", cwd=self.main).splitlines()
            git("update-ref", branch, git("commit-tree", "-p", branch, "-m", "moved", f"{branch}^{{tree}}",
                                          cwd=self.main), cwd=self.main)
        if edit_frozen:  # the frozen ticket body edited between launches
            (issue,) = (self.runs / "rl").glob("*/frozen/issue.md")
            issue.chmod(0o644)
            issue.write_text(issue.read_text() + "EDITED-FROZEN\n")
        self.launch(judge, review, SECOND)
        (run,) = (self.runs / "rl").glob("*/status")
        calls = self.runs / "rl" / "relaunch-worker-calls"
        return run.read_text().strip(), len(calls.read_text().splitlines()) if calls.exists() else 0

    def test_pass_at_head_publishes_with_no_worker_round(self) -> None:
        status, calls = self.relaunch(JUDGE_PASS, REVIEW_CLEAN)
        self.assertEqual((status, calls), ("pr-opened", 0))
        (run,) = (self.runs / "rl").iterdir()
        sha = (run / "round-1.graded.sha").read_text().strip()
        self.assertIn(f"graded at {sha}", (run / "pr-body.md").read_text())

    def test_edited_frozen_set_stops_before_publishing(self) -> None:
        status, calls = self.relaunch(JUDGE_PASS, REVIEW_CLEAN, edit_frozen=True)
        self.assertEqual((status, calls), ("stopped-environment", 0))
        (run,) = (self.runs / "rl").iterdir()
        body = run / "pr-body.md"
        self.assertFalse(body.exists() and "EDITED-FROZEN" in body.read_text())

    def test_judge_fail_resumes_into_a_worker_round(self) -> None:
        self.assertGreater(self.relaunch(JUDGE_FAIL, REVIEW_CLEAN)[1], 0)

    def test_blocking_finding_resumes_into_a_worker_round(self) -> None:
        self.assertGreater(self.relaunch(JUDGE_PASS, REVIEW_BLOCKING)[1], 0)

    def test_moved_head_resumes_into_a_worker_round(self) -> None:
        self.assertGreater(self.relaunch(JUDGE_PASS, REVIEW_CLEAN, move_head=True)[1], 0)


if __name__ == "__main__":
    unittest.main()
