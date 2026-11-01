"""No process a model call started outlives the call (#384).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real call_json, run_codex_review, and worker_round run with a
fake `claude` or `codex` first on PATH. Each fake backgrounds a writer that appends to a marker file every 0.2 s and
then exits 0 with a usable reply, so the call ends normally and only call_end can stop the writer. The done-checks
cover the worker call; these cover the grader and Codex review calls, a writer that ignores TERM, one in a session of
its own, that the worker call still gets its prompt on stdin and its env pins, that the live account token
reaches the worker call but not the supervisor after it, and that the call starts with INT and QUIT at their defaults
in a session of its own while the wrapper keeps an ignored QUIT (#468). No network.
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
# A writer in a session of its own is found only by the FACTORY_CALL_TAG sweep, which reads /proc (none on a Mac), and
# one that also clears its environment only by the call's subreaper wrapper, which finds its children in /proc.
NEEDS_PROC = unittest.skipUnless(os.path.exists("/proc/self/environ"), "the tag sweep and the wrapper read /proc")
TOKEN = "CLAUDE_CODE_OAUTH_TOKEN"  # by name, so no token assignment appears for the merge secret grep
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG",
             "CLAUDE_SETTINGS_FILE", TOKEN)

# FAKE_IGNORE_TERM makes the writer ignore TERM, so only KILL stops it. FAKE_OWN_SESSION starts it in a session of its
# own, out of the call's group, as Claude Code starts each Bash tool shell, so only the FACTORY_CALL_TAG sweep finds it.
# FAKE_ENV_CLEARED starts it in a session of its own with a cleared environment, so neither finds it and only the
# call's subreaper wrapper does (#434). FAKE_HANG keeps the call running after the writer starts.
WRITER = """w="[ -z '${FAKE_IGNORE_TERM:-}' ] || trap '' TERM; while :; do echo x >> '$FAKE_DIR/mark'; sleep 0.2; done"
if [ -n "${FAKE_ENV_CLEARED:-}" ]; then perl -MPOSIX -e 'setsid; exec @ARGV' env -i bash -c "$w" > /dev/null 2>&1 &
elif [ -n "${FAKE_OWN_SESSION:-}" ]; then perl -MPOSIX -e 'setsid; exec @ARGV' bash -c "$w" > /dev/null 2>&1 &
else ( eval "$w" ) > /dev/null 2>&1 &
fi
sleep 0.5
[ -z "${FAKE_HANG:-}" ] || while :; do sleep 0.2; done
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
        (frozen / "issue.md").write_text("# Ticket 7\n")  # run_codex_review sends the frozen ticket with its prompt
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
        self.addCleanup(subprocess.run, ["pkill", "-f", str(self.top)], check=False)

    def call_cmd(self, call: str, **extra: str) -> dict:
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; LOG=\"$RUN/factory.log\"; KEY=7; IS_FILE=1\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"\n'
            'touch "$LEDGER" "$DAILY" "$DECISIONS"; date -u +%s > "$RUN/launched"\n'
            "BODY='## Worker'; apply_caps; TIMEOUT_G=()\n"
            'command -v timeout > /dev/null 2>&1 && TIMEOUT_G=(timeout -k 5 "$CALL_TIMEOUT_SEC")\n'
            f"WORKER_KIND=claude; CODEX_PATH='{self.bin}'; CODEX_REVIEW_BLOCKED=0\n"
            f"{call}; echo returned:$?\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        return {"args": ["bash", "-c", '. "$0"\n' + script, "bin/factory"], "cwd": ROOT,
                "env": {**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                        "FACTORY_RUNS_ROOT": str(self.top / "runs"), "FAKE_DIR": str(self.top),
                        "FACTORY_WORKER_ADVISOR": "", "CLAUDE_CONFIG_DIR": str(self.top / "cc"),
                        "PATH": f"{self.bin}:{env['PATH']}", **extra},
                "text": True}

    def run_call(self, call: str, **extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(**self.call_cmd(call, **extra), capture_output=True, check=False, timeout=60)

    def assert_no_survivor(self, proc: subprocess.CompletedProcess[str]) -> None:
        self.assertIn("returned:0", proc.stdout, proc.stderr)
        mark = self.top / "mark"
        self.assertTrue(mark.exists(), "the fake's writer never ran")
        before = mark.stat().st_size
        time.sleep(1)
        self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the call returned")
        left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True, check=False).stdout
        self.assertEqual(left, "", "a process the call started is still running")
        self.assertFalse((self.run_dir / "call").exists(), "call_end left the run's call file")

    def test_grader_call_leaves_no_child(self) -> None:
        proc = self.run_call('call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"')
        self.assert_no_survivor(proc)
        self.assertIn("left processes behind", (self.run_dir / "factory.log").read_text())

    def test_codex_review_call_leaves_no_child(self) -> None:
        proc = self.run_call("run_codex_review 1")
        self.assert_no_survivor(proc)
        self.assertIn("codex review verdict: approve", proc.stderr)

    def test_writer_that_ignores_term_is_killed(self) -> None:
        proc = self.run_call('call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"',
                             FAKE_IGNORE_TERM="1")
        self.assert_no_survivor(proc)
        self.assertIn("outlived TERM by 5 s; sending KILL", (self.run_dir / "factory.log").read_text())

    @NEEDS_PROC
    def test_writer_in_its_own_session_is_killed(self) -> None:
        proc = self.run_call("worker_round 1", FAKE_OWN_SESSION="1")
        self.assert_no_survivor(proc)
        self.assertIn("left processes behind", (self.run_dir / "factory.log").read_text())

    @NEEDS_PROC
    def test_env_cleared_writer_is_killed(self) -> None:
        # A tool child that calls setsid and clears its environment is in neither the call's group nor the tag sweep;
        # the wrapper, a subreaper, becomes its parent once the call exits and ends it (#434).
        for call in ("worker_round 1", 'call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"'):
            with self.subTest(call=call):
                (self.top / "mark").unlink(missing_ok=True)
                proc = self.run_call(call, FAKE_ENV_CLEARED="1")
                self.assert_no_survivor(proc)
                self.assertIn("left processes behind", (self.run_dir / "factory.log").read_text())

    @NEEDS_PROC
    def test_group_kill_reaches_the_call_group_after_the_wrapper_dies(self) -> None:
        # The call runs in a group of its own under the wrapper. With the wrapper killed (call_abort's KILL, OOM), that
        # group must still hold the slot and call_end's group kill (#384) must still reach it, where a call without
        # the tag is found by nothing else.
        call = self.top / "call.sh"
        call.write_text(f"""#!/usr/bin/env bash
exec env -u FACTORY_CALL_TAG bash -c 'while :; do echo x >> {self.top}/mark; sleep 0.2; done' > /dev/null 2>&1
""")
        call.chmod(0o755)
        proc = self.run_call(f'call_start "$WORKTREE" {call}; until [ -s "$FAKE_DIR/mark" ]; do sleep 0.1; done; '
                             'kill -KILL "$CALL_PID"; call_live "$RUN" && echo live:1; call_end judge')
        self.assertIn("live:1", proc.stdout, "the call's group no longer holds the slot")
        self.assertIn("returned:137", proc.stdout, proc.stderr)
        mark = self.top / "mark"
        before = mark.stat().st_size
        time.sleep(1)
        self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the call returned")
        left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True, check=False).stdout
        self.assertEqual(left, "", "a process in the call's group outlived the call")
        self.assertFalse((self.run_dir / "call").exists(), "call_end left the run's call file")

    @NEEDS_PROC
    def test_signalled_supervisor_ends_an_env_cleared_writer(self) -> None:
        # The supervisor's TERM starts the wrapper's own TERM and KILL; the supervisor's KILL comes later, so it never
        # kills the wrapper during its grace and leaves a writer that ignores TERM to init.
        mark = self.top / "mark"
        proc = subprocess.Popen(**self.call_cmd("worker_round 1", FAKE_ENV_CLEARED="1", FAKE_HANG="1",
                                                FAKE_IGNORE_TERM="1"),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.time() + 20
        while not mark.exists() and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.5)
        os.killpg(proc.pid, signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 143)
        before = mark.stat().st_size
        time.sleep(1)
        self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the supervisor exited")
        left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True, check=False).stdout
        self.assertEqual(left, "", "a process the call started outlived the supervisor")

    @NEEDS_PROC
    def test_signalled_supervisor_ends_the_call(self) -> None:
        # Ctrl-C, TERM or HUP reaches the supervisor's group (a terminal signals its foreground group), not a call in
        # its own session; the supervisor ends the call's group and tagged processes before it exits, so none
        # outlives it to race the EXIT trap's worktree removal.
        for sig, status in ((signal.SIGINT, 130), (signal.SIGTERM, 143), (signal.SIGHUP, 129)):
            with self.subTest(sig=sig.name):
                mark = self.top / "mark"
                mark.unlink(missing_ok=True)
                proc = subprocess.Popen(**self.call_cmd("worker_round 1", FAKE_OWN_SESSION="1", FAKE_HANG="1"),
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                deadline = time.time() + 20
                while not mark.exists() and time.time() < deadline:
                    time.sleep(0.1)
                time.sleep(0.5)
                os.killpg(proc.pid, sig)
                self.assertEqual(proc.wait(timeout=30), status)
                before = mark.stat().st_size
                time.sleep(1)
                self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the supervisor exited")
                left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True,
                                      check=False).stdout
                self.assertEqual(left, "", "a process the call started outlived the supervisor")
                self.assertIn(f"got {sig.name[3:]} during a model call", (self.run_dir / "factory.log").read_text())
                for name in ("call", "call.tmp", "call.group", "call.group.tmp"):
                    self.assertFalse((self.run_dir / name).exists(), f"the signalled supervisor left {name}")

    @NEEDS_PROC
    def test_second_ctrl_c_waits_for_the_kill(self) -> None:
        # A writer that ignores TERM dies only by the KILL 5 s in; a second Ctrl-C before then must not end the
        # supervisor first.
        mark = self.top / "mark"
        proc = subprocess.Popen(**self.call_cmd("worker_round 1", FAKE_OWN_SESSION="1", FAKE_HANG="1",
                                                FAKE_IGNORE_TERM="1"),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        deadline = time.time() + 20
        while not mark.exists() and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.5)
        os.killpg(proc.pid, signal.SIGINT)
        time.sleep(1)
        os.killpg(proc.pid, signal.SIGINT)
        self.assertEqual(proc.wait(timeout=30), 130)
        before = mark.stat().st_size
        time.sleep(1)
        self.assertEqual(mark.stat().st_size, before, "the writer kept writing after the supervisor exited")
        left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True, check=False).stdout
        self.assertEqual(left, "", "a process the call started outlived the supervisor")

    def test_stuck_call_is_recorded_before_the_run_stops(self) -> None:
        # A process that outlives KILL cannot be faked, so call_gone is stubbed to never see the call gone. The run
        # stops stopped-environment only after the call's ledger row is written.
        for call, role in (("worker_round 1", "worker"), ("run_codex_review 1", "codex-review"),
                           ('call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json"', "judge")):
            with self.subTest(role=role):
                proc = self.run_call("call_gone() { return 1; }; " + call)
                self.assertEqual(proc.returncode, 4, proc.stderr)
                self.assertNotIn("returned:", proc.stdout)
                rows = (self.run_dir / "ledger.jsonl").read_text().splitlines()
                self.assertIn(f'"role":"{role}"', rows[-1])
                log = (self.run_dir / "factory.log").read_text().splitlines()
                self.assertRegex(log[-1], "EXIT stopped-environment .*still alive 5 s after KILL")
                subprocess.run(["pkill", "-KILL", "-f", str(self.top)], check=False)

    def test_call_reads_int_and_quit_as_default(self) -> None:
        # Bash 3.2 (a Mac) keeps the INT and QUIT it ignores in a background command ignored across exec, and GNU
        # timeout catches both, so on a Mac without it ignored=False fails on base (#468). A supervisor whose parent
        # ignores them starts with them ignored on any bash, so ignored=True with no timeout fails on base here too.
        probe = 'perl -e "print join(q( ), map { \\$SIG{\\$_} || q(DEFAULT) } qw(INT QUIT))"'
        wraps = [""] + (["timeout 60 "] if shutil.which("timeout") else [])
        for ignored in (False, True):
            for wrap in wraps:
                with self.subTest(ignored=ignored, wrap=wrap):
                    out = self.top / "sig"
                    cmd = self.call_cmd(f'call_start "$WORKTREE" {wrap}{probe} > {out}; call_end probe')
                    if ignored:
                        cmd["args"] = ["perl", "-e", '$SIG{INT} = $SIG{QUIT} = "IGNORE"; exec @ARGV', *cmd["args"]]
                    proc = subprocess.run(**cmd, capture_output=True, check=False, timeout=60)
                    self.assertIn("returned:0", proc.stdout, proc.stderr)
                    self.assertEqual(out.read_text(), "DEFAULT DEFAULT")

    def test_wrapper_keeps_an_ignored_quit(self) -> None:
        # The reset is the call's own, before its exec: a wrapper that QUIT could end would leave the call's escaped
        # children to no one. Bash 5 hands the wrapper the supervisor's QUIT, so the supervisor starts with it ignored,
        # and the QUIT waits for call.group, which the call writes after the wrapper's first statements have run.
        cmd = self.call_cmd('call_start "$WORKTREE" sleep 30; until [ -s "$RUN/call.group" ]; do sleep 0.05; done; '
                            'kill -QUIT "$CALL_PID"; sleep 0.3; kill -TERM "$CALL_PID"; call_end probe')
        cmd["args"] = ["perl", "-e", '$SIG{INT} = $SIG{QUIT} = "IGNORE"; exec @ARGV', *cmd["args"]]
        proc = subprocess.run(**cmd, capture_output=True, check=False, timeout=60)
        self.assertIn("returned:143", proc.stdout, proc.stderr)

    def test_call_runs_in_a_session_of_its_own(self) -> None:
        out = self.top / "sid"
        # The call's first process calls setpgid itself, so only the session id shows a dropped setsid.
        probe = "python3 -c 'import os; print(os.getpid(), os.getpgid(0), os.getsid(0))'"
        proc = self.run_call(f'call_start "$WORKTREE" {probe} > {out}; call_end probe')
        self.assertIn("returned:0", proc.stdout, proc.stderr)
        pid, pgid, sid = out.read_text().split()
        self.assertEqual(pid, pgid, "the call does not lead its own process group")
        self.assertNotEqual(sid, str(os.getsid(0)), "the call shares the test's session")

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

    def test_worker_call_gets_the_live_token_and_the_supervisor_keeps_its_launch_value(self) -> None:
        # bin/claude-account rewrites the user tier's token on a switch, so each worker call reads it; the supervisor
        # keeps its launch value, so a later call whose read finds no token never reuses an earlier call's.
        settings = self.top / "cc/settings.json"
        settings.parent.mkdir()
        for launch, live, child, after in ((None, "live-1", "live-1", "unset"),
                                           ("launch-0", "live-1", "live-1", "launch-0"),
                                           ("launch-0", None, "launch-0", "launch-0"), (None, None, None, "unset")):
            with self.subTest(launch=launch, live=live):
                settings.write_text(json.dumps({"env": {TOKEN: live}} if live else {}))
                proc = self.run_call(f'worker_round 1; echo "after:${{{TOKEN}-unset}}"',
                                     **({TOKEN: launch} if launch else {}))
                self.assertIn(f"after:{after}\n", proc.stdout, proc.stderr)
                env = dict(line.split("=", 1) for line in (self.top / "env").read_text().splitlines() if "=" in line)
                self.assertEqual(env.get(TOKEN), child)


if __name__ == "__main__":
    unittest.main()
