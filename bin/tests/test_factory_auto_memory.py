"""Worker and grader calls load and write no auto memory (#380).

Claude Code keeps one auto memory folder per repository, filled by interactive sessions, and `--setting-sources
user` does not turn it off. Both factory settings files set `autoMemoryEnabled: false`, and pin
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 in their env because that variable, from the launch env or a user-tier env, beats
the key, while the `--settings` env is applied last. Reads the source files only; no network.
"""

from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class AutoMemoryOffTests(unittest.TestCase):
    def test_worker_and_role_settings_turn_auto_memory_off(self) -> None:
        for name in ("worker-settings.json", "role-settings.json"):
            with self.subTest(name=name):
                settings = json.loads((ROOT / "bin/factory.d" / name).read_text())
                self.assertIs(settings.get("autoMemoryEnabled"), False)
                self.assertEqual(settings.get("env", {}).get("CLAUDE_CODE_DISABLE_AUTO_MEMORY"), "1")


if __name__ == "__main__":
    unittest.main()
