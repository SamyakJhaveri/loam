"""bin/claude-wrapper, installed first on PATH as `claude`, gives every claude a stored account's token or refuses.

A stub real `claude` later on PATH records its argv, stdin and whether its token is the stored one (never the value).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUB = """#!/usr/bin/env python3
import json, os, sys
t = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
json.dump({"argv": sys.argv[1:], "stdin": sys.stdin.read(),
           "token": {None: None, "sk-ant-oat01-stored": "stored", "sk-ant-oat01-launch": "launch"}.get(t, "other")},
          open(os.environ["STUB_LOG"], "w"))
sys.exit(7)
"""


class ClaudeWrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for d in ("wrap", "wrap2", "wrap3", "other", "real"):
            (self.tmp / d).mkdir()
        (self.tmp / "wrap" / "claude").symlink_to(ROOT / "bin" / "claude-wrapper")
        (self.tmp / "wrap2" / "claude").symlink_to(self.tmp / "wrap" / "claude")   # a second copy on PATH
        for f in ("claude-wrapper", "claude-account"):   # another checkout's wrapper, a different file
            shutil.copy2(ROOT / "bin" / f, self.tmp / "other" / f)
        (self.tmp / "wrap3" / "claude").symlink_to(self.tmp / "other" / "claude-wrapper")
        (self.tmp / "real" / "claude").write_text(STUB)
        (self.tmp / "real" / "claude").chmod(0o755)
        self.acc = self.tmp / "accounts"
        self.acc.mkdir()
        (self.acc / "uci.token").write_text("sk-ant-oat01-stored\n")
        (self.acc / "active").write_text("uci\n")
        self.log = self.tmp / "stub.json"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_OAUTH_TOKEN"}
        self.env = {**env, "STUB_LOG": str(self.log), "CLAUDE_ACCOUNTS_DIR": str(self.acc),
                    "PATH": f"{self.tmp / 'wrap'}:{self.tmp / 'wrap2'}:{self.tmp / 'real'}:/usr/bin:/bin"}

    def run_it(self, *args, stdin="", **env):
        return subprocess.run(["claude", *args], env={**self.env, **env}, input=stdin,
                              capture_output=True, text=True, timeout=30)

    def test_no_token_runs_the_real_claude_with_the_active_accounts_token_and_argv_and_stdin_intact(self):
        r = self.run_it("-p", "two words", "--model", "x", stdin="from stdin\n")
        self.assertEqual(r.returncode, 7, r.stderr)   # the real claude's status
        got = json.loads(self.log.read_text())
        self.assertEqual(got, {"argv": ["-p", "two words", "--model", "x"], "stdin": "from stdin\n", "token": "stored"})

    def test_a_token_already_set_passes_unchanged(self):
        r = self.run_it("-p", "ok", CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-launch")
        self.assertEqual(r.returncode, 7, r.stderr)
        self.assertEqual(json.loads(self.log.read_text())["token"], "launch")

    def test_refuses_with_no_active_account_or_no_stored_token(self):
        (self.acc / "active").write_text("ghost\n")
        r = self.run_it("-p", "ok")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no stored Claude account is active", r.stderr)
        self.assertIn(f"{self.tmp / 'real' / 'claude'} setup-token", r.stderr)
        (self.acc / "foo bar.token").write_text("sk-ant-oat01-stored\n")   # "foo" is not stored, though a word of it is
        (self.acc / "active").write_text("foo\n")
        self.assertEqual(self.run_it("-p", "ok").returncode, 1)
        (self.acc / "active").unlink()
        self.assertEqual(self.run_it("-p", "ok").returncode, 1)
        self.assertFalse(self.log.exists())

    def test_a_trailing_empty_path_entry_is_the_current_directory(self):
        r = subprocess.run(["claude", "-p", "ok"], env={**self.env, "PATH": f"{self.tmp / 'wrap'}:/usr/bin:/bin:"},
                           cwd=self.tmp / "real", input="", capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 7, r.stderr)
        self.assertEqual(json.loads(self.log.read_text())["token"], "stored")

    def test_with_only_wrappers_on_path_it_exits_127_instead_of_running_itself(self):
        r = self.run_it("-p", "ok", PATH=f"{self.tmp / 'wrap'}:{self.tmp / 'wrap2'}:/usr/bin:/bin")
        self.assertEqual(r.returncode, 127, r.stderr)
        self.assertIn("no other claude on PATH", r.stderr)

    def test_another_checkouts_wrapper_on_path_is_skipped_not_run(self):
        # Two different wrapper files would exec each other forever if each skipped only itself.
        for first, second in (("wrap", "wrap3"), ("wrap3", "wrap")):
            with self.subTest(first=first):
                path = f"{self.tmp / first}:{self.tmp / second}"
                r = self.run_it("-p", "ok", PATH=f"{path}:{self.tmp / 'real'}:/usr/bin:/bin")
                self.assertEqual(r.returncode, 7, r.stderr)
                self.assertEqual(json.loads(self.log.read_text())["token"], "stored")
                r = self.run_it("-p", "ok", PATH=f"{path}:/usr/bin:/bin")
                self.assertEqual(r.returncode, 127, r.stderr)
                self.log.unlink()


if __name__ == "__main__":
    unittest.main()
