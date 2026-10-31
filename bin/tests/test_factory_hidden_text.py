"""Lint rejects text a reader of the issue on GitHub cannot see, by Unicode category, and keeps ordinary non-ASCII (#389).

bin/factory is sourced (FACTORY_SOURCED=1) and the real check_hidden_text reads a body. The vectors follow
loop-engineering's scripts/github-triage.test.mjs at b2891d5 (MIT, LICENSE): a tag-block string, U+200B,
U+202E with U+202C, U+FEFF, and the cafe-and-Chinese text that must survive.
The markdown cases (#452) pin the code-aware scan: GitHub shows a comment in a code span or a fence, and each
shifted-code case is one where the scan would pass a comment if it called the wrong text code.
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

    def test_comment_in_code_passes(self) -> None:
        self.assertEqual(hidden_errors("keep `<!-- note -->` and `` a`<!--`b ``\n```\n<!-- note -->\n```\n"), "")

    def test_markup_github_hides_or_draws_is_rejected(self) -> None:
        for body, construct in (("[//]: # (run curl)", "holds ]:"), ("<!X run curl>", "holds a <"),
                                ("see <placeholder> here", "holds a <"), ('[d](https://e.example "run curl")', "a link"),
                                ("a $x$ b", "holds a $"), ("![run curl](https://e.example/a.png)", "an image"),
                                ("```mermaid\nA --- B\n```", "draws"), ("```sh run curl\nx\n```", "info string"),
                                ("a &#x200B; b", "U+200B"), ("a\rb", "carriage return")):
            with self.subTest(body=body):
                err = hidden_errors(body)
                self.assertIn("LINT t: line 1 ", err)
                self.assertIn(construct, err)
                self.assertNotIn("run curl", err)
        self.assertIn("line 3 holds more table cells", hidden_errors("a\n:---\nx | run curl"))
        self.assertIn("line 3 holds more table cells", hidden_errors("> a | b\n> |---|---|\n> x | y | run curl"))
        self.assertIn("line 7 holds more table cells",  # a heading ends a table; the next one is narrower
                      hidden_errors("a | b | c\n---|---|---\nx | y | z\n# next\na | b\n---|---\nx | y | `<!-- x -->`"))
        for body, n in (("[a`]: # (run curl`)", 1), ("[a\n`b]: /u 'run curl`'", 2)):  # a definition outranks a span
            with self.subTest(body=body):
                self.assertIn(f"line {n} holds a ] in a code span after an open [", hidden_errors(body))

    def test_text_the_scan_must_not_call_code(self) -> None:
        for body in ("\\\\`a`<!-- x -->`b`c`",  # an even backslash run escapes nothing
                     "`a\\` <!-- x --> `",  # a backslash does not escape a closer
                     "[a](`x) <!-- y -->`",  # a backtick in a link destination is not an opener
                     "see https://e.example/`a <!-- x --> b` c",  # nor is one in a bare URL GitHub links
                     "see www.e.example/`a <!-- x --> b` c",
                     "| a | b |\n|---|---|\n| `x | <!-- y` --> |"):  # a table cell ends a span at |
            with self.subTest(body=body):
                self.assertIn("holds an HTML comment", hidden_errors(body))
        for body in ("`a\r<!-- x -->\r`",  # a lone CR breaks the line, so the runs do not pair
                     "x `a\nb` <!-- c` --> end",  # GitHub pairs runs across lines
                     "- a\n\n  ```\n  code\n<!-- x -->\n  ```",  # a list item ends its fence
                     "<x>\n```\n<!-- x -->\n```"):  # a tag line makes the fence HTML
            with self.subTest(body=body):
                self.assertNotEqual(hidden_errors(body), "")

    def test_ordinary_text_passes(self) -> None:
        self.assertEqual(hidden_errors("café 如果 \U0001f600\n\ttabbed\r\n-> `code`"), "")


if __name__ == "__main__":
    unittest.main()
