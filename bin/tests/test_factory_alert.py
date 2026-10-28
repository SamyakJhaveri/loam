"""Alerts reach Samyak in plain words: bin/alert's Slack text and event-log line, and bin/factory's notify, exit
words and healthchecks pause (docs/factory/LOOP.md, Notify).

bin/alert runs for real with HOME a temp dir and a local HTTP server as the Slack webhook. The factory tests
source bin/factory (FACTORY_SOURCED=1) and point ROOT at a temp dir whose bin/alert only records its arguments,
so finish, notify and heartbeat_stop run their real code with no network.
"""

from __future__ import annotations

import http.server
import json
import os
import pathlib
import subprocess
import tempfile
import threading
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALERT = ROOT / "bin" / "alert"
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")

FAKE_ALERT = """#!/usr/bin/env python3
import json, os, pathlib, sys
with open(os.environ["FAKE_ALERT_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
if sys.argv[1:] == ["--ping", "pause"] and os.environ.get("LAUNCH_ON_PAUSE"):  # a run launches mid-pause
    pathlib.Path(os.environ["LAUNCH_ON_PAUSE"], "launched").write_text("1\\n")
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
        want = {"pr-opened": "needs-you", "ticket-defect": "needs-you", "abandon": "needs-you", "stopped": "info",
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
        calls = self.factory("finish pr-opened 'https://github.com/acme/widget/pull/9 after 2 rounds, 3.1 usd'")
        self.assertEqual(calls[-1][-1], "issue 7 (Widget works) opened a pull request; it waits for your review "
                                        "and merge. https://github.com/acme/widget/pull/9 after 2 rounds, 3.1 usd")

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

    def test_the_last_live_run_pauses_the_check_and_another_live_run_keeps_it(self) -> None:
        self.assertIn(["--ping", "pause"], self.factory("finish stopped x"))
        other = self.runs / "acme__other" / "3" / "20261027T010000Z"
        other.mkdir(parents=True)
        (other / "status").write_text("running\n")
        self.alert_log.unlink()
        self.assertNotIn(["--ping", "pause"], self.factory("finish stopped x"))

    def test_a_run_launched_during_the_pause_gets_a_beat_after_it(self) -> None:
        # A fresh run directory, and a relaunch whose status still holds its last exit.
        for status in (None, "stopped-cap"):
            with self.subTest(status=status):
                other = self.runs / "acme__other" / "3" / f"run-{status}"
                other.mkdir(parents=True)
                if status:
                    (other / "status").write_text(status + "\n")
                self.alert_log.unlink(missing_ok=True)
                calls = self.factory("finish stopped x", LAUNCH_ON_PAUSE=str(other))
                self.assertEqual(calls[-3:-1], [["--ping", "pause"], ["--ping", "beat"]], calls)
                (other / "launched").unlink()
                if status:
                    other.joinpath("status").unlink()
                other.rmdir()

    def test_finish_stops_the_heartbeat(self) -> None:
        self.factory("heartbeat_start; echo $HEARTBEAT > \"$RUN/hb\"; finish stopped x")
        self.assertEqual(self.proc.returncode, 2, self.proc.stderr)
        pid = int((self.run_dir / "hb").read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)


if __name__ == "__main__":
    unittest.main()
