"""No process a model call started outlives the call (#384).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real call_json, run_codex_review, and worker_round run with a
fake `claude` or `codex` first on PATH. Each fake backgrounds a writer that appends to a marker file every 0.2 s and
then exits 0 with a usable reply, so the call ends normally and only call_end's group kill can stop the writer. The
done-checks cover the worker call; these cover the grader and Codex review calls, a writer that ignores TERM, and
that the worker call still gets its prompt on stdin and its env pins. No network.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")

# FAKE_IGNORE_TERM makes the writer ignore TERM, so only KILL stops it.
WRITER = """( [ -z "${FAKE_IGNORE_TERM:-}" ] || trap '' TERM; while :; do echo x >> "$FAKE_DIR/mark"; sleep 0.2; done ) > /dev/null 2>&1 &
sleep 0.5
"""
FAKE_CLAUDE = """#!/usr/bin/env bash
cat > "$FAKE_DIR/stdin"
env > "$FAKE_DIR/env"
""" + WRITER + """echo '{"type":"result","subtype":"success","is_error":false,"num_turns":1,"duration_ms":1,"total_cost_usd":0,"usage":{},"result":"{\\"verdict\\":\\"pass\\",\\"rows\\":{},\\"evidence\\":{},\\"fixes\\":[],\\"backlog\\":[],\\"findings\\":[]}"}'
"""
FAKE_CODEX = """#!/usr/bin/env bash
while [ $# -gt 0 ]; do [ "$1" = -o ] && o=$2; shift; done
""" + WRITER + """echo '{"verdict":"approve","summary":"ok","findings":[],"next_steps":[]}' > "$o"
echo '{"type":"turn.completed","usage":{}}'
"""


class CallGroupTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.wt = self.top / "wt"
        self.wt.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "factory/7", str(self.wt)], check=True)
        subprocess.run(["git", "-C", str(self.wt), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "base"], check=True)
        self.run_dir = self.top / "run"
        frozen = self.run_dir / "frozen"
        frozen.mkdir(parents=True)
        (self.run_dir / "tasks").mkdir()
        for name in ("_common.md", "unattended.md"):
            (frozen / name).write_text("")
        (frozen / "worker-settings.json").write_text("{}")
        (frozen / "codex-review.prompt.md").write_text("Review the diff against <base>.\n")
        shutil.copy(ROOT / "bin/factory.d/role-settings.json", frozen / "role-settings.json")
        shutil.copy(ROOT / "bin/factory.d/judge.schema.json", frozen / "judge.schema.json")
        shutil.copy(ROOT / "bin/factory.d/review-output.schema.json", frozen / "review-output.schema.json")
        (self.run_dir / "base.sha").write_text("HEAD\n")
        (self.run_dir / "prompt.md").write_text("## Ticket\n")
        self.bin = self.top / "bin"
        self.bin.mkdir()
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)
        self.addCleanup(subprocess.run, ["pkill", "-f", str(self.bin)], check=False)

    def run_call(self, call: str, **extra: str) -> subprocess.CompletedProcess[str]:
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; LOG=\"$RUN/factory.log\"; KEY=7; IS_FILE=1\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"\n'
            'touch "$LEDGER" "$DAILY" "$DECISIONS"; date -u +%s > "$RUN/launched"\n'
            "BODY='## Worker'; apply_caps; TIMEOUT_G=(timeout -k 5 \"$CALL_TIMEOUT_SEC\")\n"
            f"WORKER_KIND=claude; CODEX_PATH='{self.bin}'; CODEX_REVIEW_BLOCKED=0\n"
            f"{call}; echo returned:$?\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        return subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "FAKE_DIR": str(self.top),
                                   "FACTORY_WORKER_ADVISOR": "", "CLAUDE_CONFIG_DIR": str(self.top / "cc"),
                                   "PATH": f"{self.bin}:{env['PATH']}", **extra},
                              capture_output=True, text=True, check=False, timeout=60)

    def assert_no_survivor(self, proc: subprocess.CompletedProcess[str]) -> None:
        self.assertIn("returned:0", proc.stdout, proc.stderr)
        mark = self.top / "mark"
        self.assertTrue(mark.exists(), "the fake's writer never ran")
        before = mark.stat().st_size
        time.sleep(1)
        self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the call returned")
        left = subprocess.run(["pgrep", "-f", str(self.bin)], capture_output=True, text=True, check=False).stdout
        self.assertEqual(left, "", "a process the call started is still running")

    def test_grader_call_leaves_no_child(self) -> None:
        proc = self.run_call('call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"')
        self.assert_no_survivor(proc)
        self.assertIn("left processes in its group", (self.run_dir / "factory.log").read_text())

    def test_codex_review_call_leaves_no_child(self) -> None:
        proc = self.run_call("run_codex_review 1")
        self.assert_no_survivor(proc)
        self.assertIn("codex review verdict: approve", proc.stderr)

    def test_writer_that_ignores_term_is_killed(self) -> None:
        proc = self.run_call('call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"',
                             FAKE_IGNORE_TERM="1")
        self.assert_no_survivor(proc)
        self.assertIn("outlived TERM by 5 s; sending KILL", (self.run_dir / "factory.log").read_text())

    def test_worker_call_keeps_its_prompt_and_env(self) -> None:
        proc = self.run_call("worker_round 1", FACTORY_WORKER_MODEL="claude-pin-1")
        self.assert_no_survivor(proc)
        prompt = (self.run_dir / "round-1.prompt.md").read_text()
        self.assertTrue(prompt)
        self.assertEqual((self.top / "stdin").read_text(), prompt)
        env = (self.top / "env").read_text().splitlines()
        for line in (f"LOAM_CHECKS={self.run_dir}/frozen/checks.sh", "CLAUDE_CODE_SUBAGENT_MODEL=claude-pin-1",
                     "CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1", "ANTHROPIC_DEFAULT_SONNET_MODEL=claude-pin-1",
                     "ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-pin-1"):
            self.assertIn(line, env)


if __name__ == "__main__":
    unittest.main()
