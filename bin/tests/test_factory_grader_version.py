"""The factory grades with the grader prompts this checkout ships, whatever the plugin cache holds.

grader_file returns the checkout's cultivation/marketplace/sam-cc-setup/agents/<name>.md, or --graders-dir's copy; an
older sam-cc-setup in the plugin cache neither wins nor blocks a launch (#532). HOME is a scratch dir holding a fake
plugin cache; `bin/factory` is sourced (FACTORY_SOURCED=1) and grader_file and cmd_next (gh, git, tmux, and its other
gates stubbed as shell functions) are called directly. No `claude`, no network.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
OLD = "0.9.4"


class GraderVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.home = self.tmp / "home"
        self.home.mkdir()

    def stale_cache(self, matching: bool = True) -> None:
        """A fake plugin cache: an older sam-cc-setup whose prompts differ from the checkout's, and a newer one whose
        prompts are byte-identical to it (unless matching=False), so neither is preferred to the checkout."""
        cache = self.home / ".claude/plugins/cache/seed-skills/sam-cc-setup"
        versions = [(OLD, "\nA grader prompt this checkout no longer ships.\n")] + ([("9.9.9", "")] if matching else [])
        for version, extra in versions:
            agents = cache / version / "agents"
            agents.mkdir(parents=True)
            for g in ("judge", "reviewer"):
                shutil.copyfile(SHIPPED / f"{g}.md", agents / f"{g}.md")
                with (agents / f"{g}.md").open("a") as f:
                    f.write(extra)

    def sourced(self, script: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_ROOT"}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), HOME=str(self.home),
                   FACTORY_RUNS_ROOT=str(self.tmp / "runs"))
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def test_the_checkout_copy_grades_beside_a_stale_cache(self) -> None:
        # freeze writes this path and its sha256 to the ledger's grader event.
        self.stale_cache()
        proc = self.sourced('grader_file judge; grader_file reviewer; echo "rc=$?"')
        self.assertEqual(proc.stdout.splitlines(), [str(SHIPPED / "judge.md"), str(SHIPPED / "reviewer.md"), "rc=0"],
                         proc.stderr)

    def test_graders_dir_replaces_the_checkout_dir(self) -> None:
        mine = self.tmp / "agents"
        mine.mkdir()
        (mine / "judge.md").write_text("# judge, by hand\n")
        proc = self.sourced(f'GRADERS_DIR=\'{mine}\'; grader_file judge; echo "rc=$?"')
        self.assertEqual(proc.stdout.splitlines(), [str(mine / "judge.md"), "rc=0"], proc.stderr)

    def test_a_replay_records_the_sha_of_the_bytes_it_graded(self) -> None:
        # `next` can fast-forward the checkout while an eval replays: the fake claude edits the grader file during
        # the call, and the scores.jsonl line must still name the bytes whose rubric the grader read.
        mine = self.tmp / "agents"
        mine.mkdir()
        shutil.copyfile(SHIPPED / "judge.md", mine / "judge.md")
        before = (mine / "judge.md").read_bytes()
        case = self.tmp / "evals/judge/c1"
        case.mkdir(parents=True)
        (case / "prompt.md").write_text("## Ticket\n")
        (case / "expected.json").write_text('{"verdict": "pass"}')
        fake = self.tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                        "open(os.environ['STDIN_LOG'], 'w').write(sys.stdin.read())\n"
                        "open(os.environ['GRADER_SRC'], 'a').write('\\nAn edit that landed mid-replay.\\n')\n"
                        "print(json.dumps({'type': 'result', 'is_error': False, 'total_cost_usd': 0,"
                        " 'result': json.dumps({'verdict': 'pass'})}))\n")
        fake.chmod(0o755)
        stdin_log = self.tmp / "stdin.txt"
        env = {k: v for k, v in os.environ.items() if k not in ("FACTORY_ROOT", "FACTORY_LEDGER", "EVAL_OUT")}
        env.update(FACTORY_SOURCED="1", HOME=str(self.home), PATH=f"{fake.parent}:{os.environ['PATH']}",
                   STDIN_LOG=str(stdin_log), GRADER_SRC=str(mine / "judge.md"))
        # $0 is bin/factory, as for `bin/factory eval`, so schema_for and the settings path resolve from bin/.
        proc = subprocess.run(["bash", "-c", f". \"$0\"; EVALS_DIR='{self.tmp / 'evals'}'; GRADERS_DIR='{mine}'; "
                               'run_eval judge; echo "rc=$?"', "bin/factory"],
                              cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        self.assertIn("rc=0", proc.stdout, proc.stderr)
        self.assertNotEqual((mine / "judge.md").read_bytes(), before, "the fake claude did not edit the source")
        rubric = self.sourced(f"grader_rubric '{SHIPPED / 'judge.md'}'").stdout
        self.assertTrue(stdin_log.read_text().startswith(rubric), "the replay graded another rubric")
        score = json.loads((self.tmp / "evals/scores.jsonl").read_text().splitlines()[-1])
        self.assertEqual(score["sha256"], hashlib.sha256(before).hexdigest())

    def tick(self, env: str = "") -> tuple[subprocess.CompletedProcess[str], str]:
        """One `bin/factory next` tick over a frontier of #7; returns the run and the tmux calls it made, one per line.
        env is shell code run first, such as an export the tick reads."""
        calls = self.tmp / "tmux.calls"
        body = (ROOT / "bin/tests/fixtures/clean-ticket.md").read_text().rstrip("\n")
        line = f"7 SamyakJhaveri {base64.b64encode(body.encode()).decode()}"
        proc = self.sourced(
            env + "LOAM_FACTORY_TOOLCHAIN=t LOAM_FACTORY_COPIER=c; "
            "assert_toolchain_env() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; target_repo() { echo o/r; }; "
            f"gh() {{ case $1$2 in apigraphql) ;; api*) echo '{line}' ;; esac; }}; "
            f'git() {{ case "$*" in *"rev-parse --abbrev-ref HEAD") echo main ;; esac; }}; '
            f'tmux() {{ echo "$*" >> "{calls}"; [ "$1" != has-session ]; }}; '
            'cmd_next; echo "rc=$?"')
        return proc, calls.read_text() if calls.exists() else ""

    def test_next_launches_with_a_stale_cache(self) -> None:
        # On 1 Nov 2026 a grader edit left the cache one version behind, and next refused every tick for about
        # 11 hours while next --dry-run said "would launch".
        self.stale_cache(matching=False)
        proc, tmux = self.tick()
        self.assertEqual(proc.stdout.splitlines(), ["launched #7", "rc=0"], proc.stderr)
        self.assertIn("new-session", tmux)

    def test_next_passes_its_caps_to_the_run_it_launches(self) -> None:
        # tmux gives a session the server's environment, so without -e the run fell back to MAX_PARALLEL=1 and
        # stopped at once beside a live run (48 false machine-problem pages on jhaveris, 30-31 Oct).
        # Every cap travels once, an unset or empty one as empty, so a cap in the server's environment is overridden
        # (#573); tmux keeps the last -e for a name, so a second one would drop next's value.
        names = ("MAX_ROUNDS ROUND_BUDGET_USD GRADER_BUDGET_USD TICKET_BUDGET_USD DAILY_BUDGET_USD "
                 "MAX_HOURS MAX_TURNS CALL_TIMEOUT_SEC NET_TIMEOUT_SEC").split()
        unset = " ".join(f"FACTORY_{n}" for n in names if n != "MAX_HOURS")
        proc, tmux = self.tick(env=f"unset {unset}; export FACTORY_MAX_PARALLEL=2 FACTORY_MAX_HOURS=; ")
        self.assertEqual(proc.stdout.splitlines(), ["launched #7", "rc=0"], proc.stderr)
        launch = [x for x in tmux.splitlines() if x.startswith("new-session")]
        self.assertEqual(len(launch), 1, tmux)
        caps = re.findall(rf"-e (FACTORY_(?:{'|'.join(names)}|MAX_PARALLEL)=\S*)", launch[0])
        self.assertEqual(sorted(caps), sorted(["FACTORY_MAX_PARALLEL=2"] + [f"FACTORY_{n}=" for n in names]),
                         launch[0])


if __name__ == "__main__":
    unittest.main()
