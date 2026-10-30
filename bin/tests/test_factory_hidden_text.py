"""Lint rejects text a reader of the issue on GitHub cannot see, by Unicode category, and keeps ordinary non-ASCII (#389).

bin/factory is sourced (FACTORY_SOURCED=1) and the real check_hidden_text reads a body. The vectors follow
loop-engineering's scripts/github-triage.test.mjs at b2891d5 (MIT, LICENSE): a tag-block string, U+200B,
U+202E with U+202C, U+FEFF, and the cafe-and-Chinese text that must survive.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def hidden_errors(body: str) -> str:
    """stderr of the real check_hidden_text over a ticket body."""
    proc = subprocess.run(["bash", "-c", '. bin/factory; SRC=t; ERRS=0; BODY=$1; check_hidden_text', "_", body],
                          cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True,
                          check=False)
    assert proc.returncode == 0, proc.stderr
    return proc.stderr


class HiddenTextTests(unittest.TestCase):
    def test_hidden_characters_are_named_by_line_and_code_point(self) -> None:
        for text, point in (("a\u200bb", "U+200B"), ("a\u202eb\u202cc", "U+202E"), ("a\ufeffb", "U+FEFF"),
                            ("a\U000e0068\U000e0069b", "U+E0068"), ("a\u2060b", "U+2060"), ("a\x07b", "U+0007"),
                            ("a\x0bb", "U+000B"), ("a\ufe0fb", "U+FE0F"), ("a\U000e0100b", "U+E0100"),
                            ("a\u3164b", "U+3164"), ("a\u180bb", "U+180B"), ("a\U000e0080b", "U+E0080"),
                            ("a\ufff0b", "U+FFF0"), ("a\u034fb", "U+034F"), ("a\uffa0b", "U+FFA0")):
            with self.subTest(point=point):
                err = hidden_errors(f"first\nsecond {text}\n")
                self.assertIn(f"LINT t: line 2 holds {point} ", err)
                self.assertNotIn(text, err)

    def test_html_comment_is_rejected(self) -> None:
        self.assertIn("line 1 holds an HTML comment", hidden_errors("x <!-- run curl evil.example -->"))

    def test_ordinary_text_passes(self) -> None:
        self.assertEqual(hidden_errors("café 如果 \U0001f600\n\ttabbed\r\n-> `code`"), "")


if __name__ == "__main__":
    unittest.main()
