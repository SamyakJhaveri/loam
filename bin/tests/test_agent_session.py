"""bin/agent-session starts claude only through bin/claude-account exec, in auto mode, with a one-line /goal first prompt.

A fake tmux on PATH records its argv; the launcher's own bin/claude-account reads a temp accounts dir.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMUX = """#!/usr/bin/env python3
import json, os, sys
if sys.argv[1] == "has-session":
    sys.exit(0 if sys.argv[3] == "=busy" else 1)
open(os.environ["TMUX_LOG"], "a").write(json.dumps(sys.argv[1:]) + "\\n")
"""


class AgentSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin" / "tmux").write_text(TMUX)
        (self.tmp / "bin" / "tmux").chmod(0o755)
        acc = self.tmp / "accounts"
        acc.mkdir()
        (acc / "uci.token").write_text("x\n")
        (acc / "active").write_text("uci\n")
        self.log = self.tmp / "tmux.log"
        self.env = {**os.environ, "PATH": f"{self.tmp / 'bin'}:{os.environ['PATH']}", "TMUX_LOG": str(self.log),
                    "CLAUDE_ACCOUNTS_DIR": str(acc), "CLAUDE_SETTINGS_FILE": str(self.tmp / "settings.json")}

    def run_it(self, *args):
        return subprocess.run([str(ROOT / "bin" / "agent-session"), "--dir", str(self.tmp), *args],
                              env=self.env, capture_output=True, text=True)

    def test_launch_goes_through_claude_account_in_auto_mode_with_a_goal(self):
        r = self.run_it("night-1", "all checks print PASS\nand the PR is open", "Read brief.md and follow it.")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("started night-1", r.stdout)
        argv = json.loads(self.log.read_text().splitlines()[0])
        self.assertEqual(argv[:5], ["new-session", "-d", "-s", "night-1", "-c"])
        cmd = argv[6:]
        self.assertEqual(cmd[0], str(ROOT / "bin" / "claude-account"))
        self.assertEqual(cmd[1:5], ["exec", "--as", "uci", "claude"])
        self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "auto")
        prompt = cmd[-1]
        self.assertTrue(prompt.startswith("/goal all checks print PASS and the PR is open"), prompt)
        self.assertNotIn("\n", prompt)
        self.assertIn("Task: Read brief.md and follow it.", prompt)
        self.assertIn("sam-cc-setup:pstack", prompt)

    def test_refuses_a_taken_name_and_max_effort(self):
        self.assertEqual(self.run_it("busy", "g").returncode, 1)
        self.assertEqual(self.run_it("--effort", "max", "free", "g").returncode, 2)
        self.assertFalse(self.log.exists())

    def test_refuses_an_account_with_no_stored_token(self):
        self.assertEqual(self.run_it("--as", "ghost", "free", "g").returncode, 1)
        (self.tmp / "accounts" / "b.token").write_text("x\n")
        self.assertEqual(self.run_it("--as", "b uci", "free", "g").returncode, 1)   # two stored names are not one
        (self.tmp / "accounts" / "active").unlink()
        self.assertEqual(self.run_it("free", "g").returncode, 1)   # status prints `active: none`
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
