"""Alerts reach Samyak in plain words: bin/alert's Slack text and event-log line, and bin/factory's notify, exit
words (docs/factory/LOOP.md, Notify).

bin/alert runs for real with HOME a temp dir and a local HTTP server as the Slack webhook. The factory tests
source bin/factory (FACTORY_SOURCED=1) and point ROOT at a temp dir whose bin/alert only records its arguments,
so finish and notify run their real code with no network.
"""

from __future__ import annotations

import http.server
import json
import os
import pathlib
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALERT = ROOT / "bin" / "alert"
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "REPO", "RUN", "LOG")

FAKE_ALERT = """#!/usr/bin/env python3
import json, os, signal, sys, time
with open(os.environ["FAKE_ALERT_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_ALERT_TERM"):   # the operator's signal lands while the post is in flight
    os.kill(int(os.environ.pop("FAKE_ALERT_TERM")), signal.SIGTERM)
    time.sleep(0.3)
sys.exit(int(os.environ.get("FAKE_ALERT_EXIT", "0")))
"""


class Webhook(http.server.BaseHTTPRequestHandler):
    posts: list[dict] = []

    def do_POST(self) -> None:  # noqa: N802 - the http.server hook name
        Webhook.posts.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args: object) -> None:
        pass


class AlertScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name)
        self.conf = self.home / ".config" / "loam" / "alerts"
        self.conf.mkdir(parents=True)
        server = http.server.HTTPServer(("127.0.0.1", 0), Webhook)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)
        self.url = f"http://127.0.0.1:{server.server_port}/hook"
        Webhook.posts = []

    def hook(self, name: str, url: str, mode: int = 0o600) -> None:
        (self.conf / name).write_text(url + "\n")
        (self.conf / name).chmod(mode)

    def alert(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(ALERT), *args], env={**os.environ, "HOME": str(self.home)},
                              capture_output=True, text=True, check=False)

    def events(self) -> list[dict]:
        return [json.loads(x) for x in (self.home / ".local/state/loam/alerts.jsonl").read_text().splitlines()]

    def test_needs_you_posts_loud_plain_line_and_logs_it_sent(self) -> None:
        self.hook("slack-distbench", self.url + "/distbench")
        done = self.alert("--level", "needs-you", "--source", "factory", "--project", "distbench",
                          "--run", "issue 7", "issue 7 (Fix <the> grader & co)\nopened a pull request")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(Webhook.posts, [{"text": "<!channel> distbench factory: "
                                                  "issue 7 (Fix &lt;the&gt; grader &amp; co) opened a pull request"}])
        (event,) = self.events()
        self.assertEqual({k: event[k] for k in ("project", "source", "run", "level", "slack", "text")},
                         {"project": "distbench", "source": "factory", "run": "issue 7", "level": "needs-you",
                          "slack": "sent", "text": "issue 7 (Fix <the> grader & co) opened a pull request"})
        self.assertRegex(event["t"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_info_is_quiet_and_an_unknown_project_uses_the_shared_webhook(self) -> None:
        self.hook("slack", self.url)
        done = self.alert("--project", "loam", "--source", "factory", "started")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(Webhook.posts, [{"text": "loam factory: started"}])

    def test_a_readable_webhook_file_is_refused_logged_and_never_printed(self) -> None:
        self.hook("slack", self.url, mode=0o644)
        done = self.alert("--level", "fail", "run died")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(Webhook.posts, [])
        self.assertNotIn(str(self.url.split("//")[1]), done.stderr)
        (event,) = self.events()
        self.assertTrue(event["slack"].startswith("failed: ") and "mode 644" in event["slack"], event["slack"])

    def test_a_dotted_repository_name_is_a_project(self) -> None:
        self.hook("slack", self.url)
        self.assertEqual(self.alert("--project", "foo.bar", "hi").returncode, 0)
        self.assertEqual(self.alert("--project", "../x", "hi").returncode, 2)

    def test_no_webhook_still_logs_the_event_and_fails(self) -> None:
        done = self.alert("--level", "fail", "run died")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(self.events()[0]["text"], "run died")

    def test_ping_without_a_check_is_a_no_op_and_a_bad_url_fails_without_printing_it(self) -> None:
        self.assertEqual(self.alert("--ping", "beat").returncode, 0)
        self.hook("hc-ping-url", "http://hc-ping.example/secret-check-id")
        done = self.alert("--ping", "beat")
        self.assertEqual(done.returncode, 1)
        self.assertNotIn("secret-check-id", done.stderr)


class FactoryAlertTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        self.fake = top / "fake"
        (self.fake / "bin").mkdir(parents=True)
        (self.fake / "bin" / "alert").write_text(FAKE_ALERT)
        (self.fake / "bin" / "alert").chmod(0o755)
        self.runs = top / "runs"
        self.run_dir = self.runs / "7" / "20261027T000000Z"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "frozen" / "issue.md").write_text("# Widget works\n\nbody\n")
        self.alert_log = top / "alert-calls.jsonl"
        self.home = top / "home"
        self.home.mkdir()

    def factory(self, script: str, **env: str) -> list[list[str]]:
        """Source bin/factory for issue 7 of acme/Widget, swap ROOT for the recording bin/alert, run script."""
        setup = (f"ROOT='{self.fake}'; RUNS_BASE='{self.runs}'; RUN='{self.run_dir}'; ISSUE=7; KEY=7; IS_FILE=0\n"
                 "gh() { cat > /dev/null; echo comment >> \"$RUN/gh-called\"; return ${FAKE_GH_EXIT:-0}; }\n")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{setup}{script}"], cwd=ROOT,
                              env={**base, "FACTORY_SOURCED": "1", "REPO": "acme/Widget", "HOME": str(self.home),
                                   "FAKE_ALERT_LOG": str(self.alert_log), "LOG": str(self.run_dir / "factory.log"),
                                   **env},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        self.proc = proc
        return [json.loads(x) for x in self.alert_log.read_text().splitlines()] if self.alert_log.exists() else []

    def test_each_exit_reads_as_plain_words_at_its_level(self) -> None:
        # Every status finish can write: no raw status token reaches Samyak, and the level sets the @channel.
        want = {"pr-opened": "info", "ticket-defect": "needs-you", "abandon": "needs-you", "stopped": "info",
                "stopped-cap": "fail", "stuck": "fail", "no-change": "fail", "stopped-environment": "fail"}
        for status, level in want.items():
            with self.subTest(status=status):
                self.alert_log.unlink(missing_ok=True)
                calls = self.factory(f"finish {status} 'the detail'")
                self.assertEqual(calls[-1][:2], ["--level", level])
                args = calls[-1]
                self.assertEqual(args[args.index("--project") + 1], "widget")
                self.assertEqual(args[args.index("--run") + 1], "issue 7")
                text = args[-1]
                self.assertTrue(text.startswith("issue 7 (Widget works) "), text)
                self.assertTrue(text.endswith(". the detail"), text)
                if "-" in status:
                    self.assertNotIn(status, text)

    def test_pr_opened_message_is_exact(self) -> None:
        # Loam's own PR goes to the overnight driver, so the alert is info and says so.
        calls = self.factory("finish pr-opened 'https://github.com/acme/widget/pull/9 after 2 rounds, 3.1 usd'")
        self.assertEqual(calls[-1][:2], ["--level", "info"])
        self.assertEqual(calls[-1][-1], "issue 7 (Widget works) opened a pull request; the overnight driver reviews, "
                                        "fixes and merges it, and alerts you if it leaves it open. "
                                        "https://github.com/acme/widget/pull/9 after 2 rounds, 3.1 usd")

    def test_pr_opened_on_another_target_waits_for_its_owner(self) -> None:
        calls = self.factory("TARGET_IS_LOAM=0; finish pr-opened 'https://github.com/acme/widget/pull/9'")
        self.assertEqual(calls[-1][:2], ["--level", "needs-you"])
        self.assertEqual(calls[-1][-1], "issue 7 (Widget works) opened a pull request; it waits for your review "
                                        "and merge. https://github.com/acme/widget/pull/9")

    def test_a_file_ticket_pr_opened_alert_is_left_to_a_launcher_that_asks_for_it(self) -> None:
        # distbench's factory-isc may land the branch itself, so it, not bin/factory, names the next step.
        script = "TARGET_IS_LOAM=0; IS_FILE=1; KEY=W1-x; finish pr-opened 'pr-body.md'"
        self.assertEqual([c[:2] for c in self.factory(script)], [["--level", "needs-you"]])
        self.alert_log.unlink()
        self.assertEqual(self.factory(script, FACTORY_PR_ALERT="launcher"), [])
        self.assertIn("its launcher alerts the next step", (self.run_dir / "factory.log").read_text())

    def test_an_issue_is_named_by_its_frozen_github_title(self) -> None:
        # An issue's frozen body has no '# ' line; freeze writes frozen/title from GitHub.
        (self.run_dir / "frozen" / "issue.md").write_text("Brief:\nbody\n")
        (self.run_dir / "frozen" / "title").write_text("factory: widgets work\n")
        calls = self.factory("finish stopped 'x'")
        self.assertTrue(calls[-1][-1].startswith("issue 7 (factory: widgets work) "), calls[-1][-1])

    def test_slack_failure_falls_back_to_the_ticket_comment(self) -> None:
        self.factory("notify fail 'issue 7 stopped' 'detail'", FAKE_ALERT_EXIT="1")
        self.assertTrue((self.run_dir / "gh-called").exists())
        self.assertFalse((self.run_dir / "notify.failed").exists())

    def test_slack_and_comment_both_failing_writes_notify_failed(self) -> None:
        self.factory("notify fail 'issue 7 stopped' 'detail'", FAKE_ALERT_EXIT="1", FAKE_GH_EXIT="1")
        self.assertIn("issue 7 stopped: detail", (self.run_dir / "notify.failed").read_text())

    def test_notify_scrubs_alert_secrets(self) -> None:
        # A worker's error text can quote a webhook or ping URL, or the API key from the config files.
        conf = self.home / ".config" / "loam" / "alerts"
        conf.mkdir(parents=True)
        (conf / "hc-api-key").write_text("Kq" * 16 + "\n")
        hook = "https://hooks.slack.com/services/T00/B00/" + "Zx" * 12
        calls = self.factory(f"notify fail 'issue 7 stopped' 'saw {hook} and {'Kq' * 16} and https://hc-ping.com/abc'")
        self.assertNotIn("Zx" * 12, calls[-1][-1])
        self.assertNotIn("Kq" * 16, calls[-1][-1])
        self.assertNotIn("hc-ping.com/abc", calls[-1][-1])

    def test_notify_scrubs_before_slack(self) -> None:
        key = "sk-ant-api03-" + "Q0" * 20
        calls = self.factory(f"notify fail 'issue 7 stopped' 'ANTHROPIC_API_KEY={key}'")
        self.assertNotIn(key[14:], calls[-1][-1])
        self.assertIn("[redacted]", calls[-1][-1])

    def test_a_file_ticket_alerts_on_needs_you_fail_and_every_stop_never_on_github(self) -> None:
        # A file ticket (every distbench factory run) has no issue: needs-you, fail and every stopped* exit reach
        # bin/alert as `ticket <name>` under the target's project; its quiet non-stop events stay in the log, and a
        # failed post never falls back to a GitHub comment.
        file_ticket = "ISSUE=; KEY=F9-widget; IS_FILE=1; "
        distbench = {"REPO": "SamyakJhaveri/distbench"}
        alerted = {"ticket-defect": "needs-you", "abandon": "needs-you", "stopped": "info", "stopped-cap": "fail",
                   "stuck": "fail", "no-change": "fail", "stopped-environment": "fail",
                   "stopped-other": "fail"}
        for status, level in alerted.items():
            with self.subTest(status=status):
                self.alert_log.unlink(missing_ok=True)
                (call,) = self.factory(f"{file_ticket}finish {status} 'the detail'", **distbench)
                self.assertEqual(call[:2], ["--level", level])
                self.assertEqual(call[call.index("--project") + 1], "distbench")
                self.assertEqual(call[call.index("--run") + 1], "ticket F9-widget")
                self.assertTrue(call[-1].endswith(". the detail"), call[-1])
        with self.subTest(status="pr-opened on distbench"):
            self.alert_log.unlink(missing_ok=True)
            (call,) = self.factory(f"{file_ticket}TARGET_IS_LOAM=0; finish pr-opened x", **distbench)
            self.assertEqual((call[:2], call[call.index("--run") + 1]), (["--level", "needs-you"], "ticket F9-widget"))
        quiet = {"finish pr-opened x": "opened a pull request", "notify info 'F9 started' 'Branch b'": "F9 started",
                 "notify info 'F9: checks still fail after round 2' 'FAIL lint'": "checks still fail after round 2"}
        for script, logged in quiet.items():
            with self.subTest(info=script):
                self.alert_log.unlink(missing_ok=True)
                self.assertEqual(self.factory(file_ticket + script, **distbench), [])
                last = [x for x in (self.run_dir / "factory.log").read_text().splitlines() if "[notify] " in x][-1]
                self.assertIn(logged, last)
        with self.subTest("an empty REPO resolves from the target's origin"):
            target = self.run_dir.parent / "target"
            subprocess.run(["git", "init", "-q", str(target)], check=True)
            subprocess.run(["git", "-C", str(target), "remote", "add", "origin",
                            "git@github.com:SamyakJhaveri/distbench.git"], check=True)
            self.alert_log.unlink(missing_ok=True)
            (call,) = self.factory(f"{file_ticket}TARGET='{target}'; notify fail 'F9 stopped' x", REPO="")
            self.assertEqual(call[call.index("--project") + 1], "distbench")
        with self.subTest("a failed post writes notify.failed, never a comment"):
            self.factory(f"{file_ticket}notify fail 'F9 stopped' 'detail'", FAKE_ALERT_EXIT="1", **distbench)
            self.assertFalse((self.run_dir / "gh-called").exists())
            self.assertIn("F9 stopped: detail", (self.run_dir / "notify.failed").read_text())
        with self.subTest("an issue ticket still alerts on info, as `issue <n>`"):
            self.alert_log.unlink(missing_ok=True)
            (call,) = self.factory("notify info 'issue 7 started' 'Branch b'")
            self.assertEqual((call[:2], call[call.index("--run") + 1]), (["--level", "info"], "issue 7"))

    def test_a_killed_supervisor_alerts_fail_once_and_records_the_stop(self) -> None:
        # `tmux kill-session` sends the supervisor HUP; once run_traps armed it, the run ends as stopped-killed with
        # one fail alert as `ticket <name>`, exit 129, and no learn step. A call's own traps hand back to it.
        file_ticket = "ISSUE=; KEY=F9-widget; IS_FILE=1; REVIEW_LOADED=1; learn_run() { echo learn >> \"$RUN/learned\"; }; "
        for sig, code in (("HUP", 129), ("TERM", 143)):
            with self.subTest(signal=sig):
                self.alert_log.unlink(missing_ok=True)
                (call,) = self.factory(f"{file_ticket}run_traps; kill -{sig} $$; echo not-reached",
                                       REPO="SamyakJhaveri/distbench")
                self.assertEqual(self.proc.returncode, code)
                self.assertNotIn("not-reached", self.proc.stdout)
                self.assertEqual(call[:2], ["--level", "fail"])
                self.assertEqual(call[call.index("--run") + 1], "ticket F9-widget")
                self.assertIn(f"SIG{sig}", call[-1])
                self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-killed")
                self.assertFalse((self.run_dir / "learned").exists())
        with self.subTest("call_end re-arms the run's traps"):
            self.alert_log.unlink(missing_ok=True)
            (call,) = self.factory(f"{file_ticket}run_traps; trap - HUP; CALL_PID=; CALL_TAG=t.0.0; CALL_STUCK=; "
                                   "call_end worker > /dev/null 2>&1; kill -HUP $$", REPO="SamyakJhaveri/distbench")
            self.assertEqual(self.proc.returncode, 129)
        with self.subTest("a `| tee` launch whose pipe died: the child's Hangup job line raises no SIGPIPE first"):
            self.alert_log.unlink(missing_ok=True)
            (call,) = self.factory(f"{file_ticket}run_traps; exec 2> >(:) 1>&2; sleep 0.5; "
                                   "bash -c 'kill -HUP $PPID; kill -HUP $$'; echo not-reached",
                                   REPO="SamyakJhaveri/distbench")
            self.assertEqual(self.proc.returncode, 129)
            self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-killed")
        with self.subTest("before run_traps a signal is the shell's default"):
            self.alert_log.unlink(missing_ok=True)
            self.assertEqual(self.factory(f"{file_ticket}kill -HUP $$"), [])

    def test_a_signal_after_the_exit_is_decided_cannot_replace_it(self) -> None:
        # distbench's factory-isc lands a run only on `pr-opened`; a TERM during finish's alert, or one reaching the
        # learn step finish leaves behind, must not turn it into stopped-killed with a false fail alert.
        file_ticket = "ISSUE=; KEY=F9-widget; IS_FILE=1; REVIEW_LOADED=1; "
        with self.subTest("a signal while finish posts its alert"):
            calls = self.factory("run_traps; export FAKE_ALERT_TERM=$$; finish pr-opened 'https://github.com/acme/widget/pull/9'")
            self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
            self.assertEqual([c[:2] for c in calls], [["--level", "info"]])
            self.assertEqual((self.run_dir / "status").read_text().strip(), "pr-opened")
            self.assertIn("EXIT pr-opened (0)", (self.run_dir / "factory.log").read_text())
        with self.subTest("the HUP also took the launcher's `| tee`: finish still logs its EXIT line"):
            (self.run_dir / "factory.log").unlink(missing_ok=True)
            self.factory("run_traps; exec 2> >(:); sleep 0.5; finish pr-opened 'https://github.com/acme/widget/pull/9'")
            self.assertEqual(self.proc.returncode, 0)
            self.assertIn("EXIT pr-opened (0)", (self.run_dir / "factory.log").read_text())
        # The learn step as review_claude drives it, signalled before its first call and after one (the real call_end).
        learn = self.run_dir / "learn.pid"
        for when, before in (("before its first call", ""),
                             ("after one of its calls", "CALL_PID=; CALL_TAG=t.0.0; CALL_STUCK=; call_end learn-writer; ")):
            with self.subTest(f"a signal to the learn step {when}"):
                self.alert_log.unlink(missing_ok=True)
                learn.unlink(missing_ok=True)
                (self.run_dir / "learned").unlink(missing_ok=True)
                (self.run_dir / "status").unlink(missing_ok=True)
                (self.run_dir / "factory.log").unlink(missing_ok=True)
                calls = self.factory(file_ticket + f"TARGET_IS_LOAM=0; learn_run() {{ {before}echo $BASHPID > '{learn}'; "
                                     "kill -TERM $BASHPID; sleep 1; echo survived >> \"$RUN/learned\"; }; "
                                     "run_traps; finish pr-opened pr-body.md", REPO="SamyakJhaveri/distbench")
                self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
                for _ in range(100):
                    if learn.exists() and not pathlib.Path(f"/proc/{learn.read_text().strip()}").exists():
                        break
                    time.sleep(0.05)
                self.assertTrue(learn.exists(), "finish starts the learn step")
                self.assertFalse((self.run_dir / "learned").exists(), "the TERM must still end the learn step")
                calls = [json.loads(x) for x in self.alert_log.read_text().splitlines()] if self.alert_log.exists() else []
                self.assertEqual([c[:2] for c in calls], [["--level", "needs-you"]])
                self.assertEqual((self.run_dir / "status").read_text().strip(), "pr-opened")
                self.assertNotIn("stopped-killed", (self.run_dir / "factory.log").read_text())

    def test_a_dead_stderr_reader_before_run_traps_still_records_the_stop_and_alerts(self) -> None:
        # The launcher's `| tee` can die alone before cmd_run arms run_traps; the first stderr write must fail, not end
        # the run by SIGPIPE with its status left `running` and no alert.
        calls = self.factory("exec 2> >(:); wait $!; finish stopped-environment 'the worker call returned no result event'")
        self.assertEqual(self.proc.returncode, 4)
        self.assertEqual([c[:2] for c in calls], [["--level", "fail"]])
        self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-environment")
        self.assertIn("EXIT stopped-environment (4)", (self.run_dir / "factory.log").read_text())
        # A log in a command substitution or pipeline, where bash resets the PIPE handler, must not end that subshell.
        self.factory("exec 2> >(:); wait $!; echo \"$(log 'in a substitution'; echo survived)\"")
        self.assertEqual(self.proc.stdout, "survived\n")

    def test_a_run_end_never_pauses_the_check(self) -> None:
        # The next timer's ticks are the check's only beats (cmd_next); a pause at a run's end would outlive a timer
        # that then refuses every tick, so the check could never go red.
        for status in ("stopped", "pr-opened", "stopped-environment"):
            with self.subTest(status=status):
                self.alert_log.unlink(missing_ok=True)
                calls = self.factory(f"finish {status} x")
                self.assertEqual(self.proc.returncode != 0, status != "pr-opened", self.proc.stderr)
                self.assertFalse([c for c in calls if c[:1] == ["--ping"]], calls)
        # And a refusing tick after it sends nothing either, so the check is left beating, then goes red.
        self.alert_log.unlink(missing_ok=True)
        self.factory("claude_logged_in() { return 1; }; assert_target_ready() { :; }; cmd_next")
        self.assertEqual(self.proc.returncode, 1, self.proc.stderr)
        self.assertFalse(self.alert_log.exists())

if __name__ == "__main__":
    unittest.main()
