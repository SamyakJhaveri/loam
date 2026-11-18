"""sam-cc-setup reflect/words-and-refusals.py, run on a small transcript the way reflect and audit run it."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (pathlib.Path(__file__).resolve().parents[2]
          / "cultivation/marketplace/sam-cc-setup/skills/reflect/words-and-refusals.py")
REFUSAL = "Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Destructive]."


def entry(kind: str | None, content: object, role: str = "user") -> dict:
    line = {"type": role, "timestamp": "2026-11-17T01:00:00Z", "message": {"role": role, "content": content}}
    if kind:
        line["origin"] = {"kind": kind}
    return line


class WordsAndRefusalsTest(unittest.TestCase):
    def test_prints_only_human_entries_and_classifier_refusals_joined_to_their_call(self) -> None:
        lines = [
            entry("human", "please fix the hook"),                                  # 1
            entry(None, "Base directory for this skill: ... (a skill body)"),       # 2
            entry("peer", "a message from another session"),                        # 3
            entry(None, [{"type": "tool_use", "id": "t1", "name": "Bash",
                          "input": {"command": "tmux kill-session -t =w"}}], "assistant"),  # 4
            entry(None, [{"type": "tool_result", "tool_use_id": "t1", "is_error": True,
                          "content": [{"type": "text", "text": REFUSAL}]}]),        # 5
            entry(None, [{"type": "tool_result", "tool_use_id": "t1", "is_error": False,
                          "content": "grep found: auto mode classifier"}]),          # 6
            entry("human", [{"type": "text", "text": "first line\nsecond line"}]),  # 7
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "t.jsonl"
            path.write_text("".join(json.dumps(x) + "\n" for x in lines) + "not json\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True,
                               check=False, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([line.split(":")[0] for line in r.stdout.splitlines() if line[:1].isdigit()],
                         ["1", "5", "7"], r.stdout)
        self.assertIn("1: owner 2026-11-17T01:00:00Z: please fix the hook", r.stdout)
        self.assertIn("5: refused Bash (tool_use line 4): tmux kill-session -t =w", r.stdout)
        self.assertIn("first line\n    second line", r.stdout)
        for absent in ("skill body", "another session", "grep found"):
            self.assertNotIn(absent, r.stdout)


if __name__ == "__main__":
    unittest.main()
