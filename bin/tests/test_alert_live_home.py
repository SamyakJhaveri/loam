"""bin/alert sends nothing when a sourced bin/factory (a test) calls it with the account's own HOME.

A bare `python3 -m unittest` run skips conftest.py's scratch HOME, and tests that source bin/factory reached the live
Slack and alerts.jsonl that way. The account's home can be faked only in-process, so bin/alert is loaded as a module
with HOME and the passwd lookup both naming a temp dir that has no Slack config: a broken guard cannot reach the
network or the real log.
"""

from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ALERT = pathlib.Path(__file__).resolve().parents[2] / "bin" / "alert"


class LiveHomeTests(unittest.TestCase):
    def run_alert(self, sourced: bool) -> tuple[int, str, pathlib.Path]:
        """bin/alert's main for one fail alert, with HOME and the account's home a temp dir; (exit, stderr, log)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        home = pathlib.Path(tmp.name)
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_SOURCED"}
        env["HOME"] = str(home)
        if sourced:
            env["FACTORY_SOURCED"] = "1"
        argv = ["bin/alert", "--level", "fail", "--source", "factory", "--project", "loam", "issue 7 stopped"]
        err = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(sys, "argv", argv), \
                contextlib.redirect_stderr(err):
            loader = importlib.machinery.SourceFileLoader("alert_under_test", str(ALERT))
            mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
            loader.exec_module(mod)
            self.assertEqual(mod.EVENTS, home / ".local/state/loam/alerts.jsonl")  # never the real log
            with mock.patch.object(mod.pwd, "getpwuid", return_value=mock.Mock(pw_dir=str(home))):
                code = mod.main()
        return code, err.getvalue(), mod.EVENTS

    def test_sourced_factory_with_the_account_home_sends_and_writes_nothing(self) -> None:
        code, err, log = self.run_alert(sourced=True)
        self.assertEqual(code, 0, err)
        self.assertIn("not sent", err)
        self.assertFalse(log.exists())

    def test_without_factory_sourced_the_same_home_alerts(self) -> None:
        code, err, log = self.run_alert(sourced=False)
        self.assertEqual(code, 1, err)  # no Slack config in the temp home, so the post fails; the line is logged
        self.assertEqual(len(log.read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
