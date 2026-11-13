"""FACTORY_JUDGE=off leaves the judge out of every round (docs/factory/LOOP.md, Graders).

`bin/factory -C <target> run` on a file ticket with a scripted `claude` whose judge always fails: with the switch off,
no judge call is made, factory.log says so in one line, the reviewer and sweep still grade, and the PR opens ready after
one worker round with a Judge section that says the judge was off. A value other than on or off is refused.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

from test_factory_mutation_sweep import CLAUDE, ENVELOPE, TICKET, git, scratch_env

ROOT = pathlib.Path(__file__).resolve().parents[2]
JUDGE_FAIL = {"verdict": "fail", "rows": {"correct": "fail", "verified": "pass", "honest": "pass"},
              "fixes": ["fix the thing"], "backlog": [], "evidence": {}}
# The scripted claude, with each judge call counted in $d/judge-calls.
COUNTING = CLAUDE.replace('*json-schema*rows*) cat > /dev/null;',
                          '*json-schema*rows*) cat > /dev/null; echo x >> "$d/judge-calls";')


class JudgeOffTests(unittest.TestCase):
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
        (co / "bin/check").write_text("#!/bin/sh\nexit 0\n")
        (co / "bin/check").chmod(0o755)
        (co / "docs/factory/STANDING.md").write_text("## Standing do-not-touch list\n\n- bin/check\n")
        git(co, env, "init", "-q", "-b", "main")
        git(co, env, "remote", "add", "origin", str(origin))
        git(co, env, "add", "-A")
        git(co, env, "commit", "-qm", "base")
        git(co, env, "push", "-q", "-u", "origin", "main")
        stubs = self.top / "bin"
        stubs.mkdir()
        (stubs / "claude").write_text(COUNTING)
        (stubs / "claude").chmod(0o755)
        for name, reply in (("judge", json.dumps(JUDGE_FAIL)), ("review", '{"verdict":"merge","findings":[]}'),
                            ("worker", "CLAIM: done")):
            (self.top / f"{name}.json").write_text(json.dumps({**ENVELOPE, "result": reply}) + "\n")
        (self.top / "mprobe.md").write_text(TICKET)
        env["PATH"] = f"{stubs}:{ROOT / 'bin/tests/fixtures/systemd'}:{env['PATH']}"
        self.env = env
        self.co = co

    def launch(self, judge: str) -> int:
        r = subprocess.run([str(ROOT / "bin/factory"), "-C", str(self.co), "run", str(self.top / "mprobe.md")],
                           cwd=ROOT, env={**self.env, "FACTORY_JUDGE": judge}, capture_output=True, text=True,
                           timeout=300, check=False)
        self.out = r.stdout + r.stderr
        return r.returncode

    def run_dir(self) -> pathlib.Path:
        (run,) = (self.top / "h/.local/state/loam-factory/runs/o__r/mprobe").glob("*/")
        return run

    def test_judge_off_makes_no_judge_call_and_opens_a_ready_pr(self) -> None:
        self.assertEqual(self.launch("off"), 0, self.out)
        self.assertFalse((self.top / "judge-calls").exists(), "the judge was called")
        self.assertEqual((self.top / "rounds").read_text().strip(), "1")
        log = (self.run_dir() / "factory.log").read_text()
        self.assertEqual(sum(" judge: off (FACTORY_JUDGE=off)" in ln for ln in log.splitlines()), 1, log)
        self.assertNotIn("judge call", log)
        self.assertNotIn("judge verdict", log)
        self.assertIn("reviewer verdict", log)
        body = (self.run_dir() / "pr-body.md").read_text()
        self.assertFalse(body.startswith("Draft:"), body.splitlines()[0])
        self.assertIn("\n## Judge\n\noff (FACTORY_JUDGE=off): no judge graded this run.\n", body)

    def test_a_value_other_than_on_or_off_is_refused(self) -> None:
        self.assertEqual(self.launch("no"), 2, self.out)
        self.assertIn("FACTORY_JUDGE=no: it must be on or off", self.out)


if __name__ == "__main__":
    unittest.main()
