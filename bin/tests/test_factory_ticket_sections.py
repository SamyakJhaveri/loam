"""Lint accepts a trailing `## Comments` section and rejects one that another section follows (CONTRACT.md, item 11).

bin/factory is sourced (FACTORY_SOURCED=1) and the real check_sections reads the S1 fixture, which lint accepts,
with a Comments section added at the end or before Worker.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
S1 = (ROOT / "bin/factory.d/fixtures/S1.md").read_text()
COMMENTS = "## Comments\n\nAn answer.\n"


def section_errors(body: str) -> str:
    """stderr of the real check_sections over a ticket body."""
    proc = subprocess.run(["bash", "-c", '. bin/factory; SRC=t; ERRS=0; BODY=$1; check_sections', "_", body],
                          cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True,
                          check=False)
    assert proc.returncode == 0, proc.stderr
    return proc.stderr


class TicketSectionTests(unittest.TestCase):
    def test_trailing_comments_passes(self) -> None:
        self.assertEqual(section_errors(f"{S1}\n{COMMENTS}"), "")

    def test_comments_before_another_section_is_rejected(self) -> None:
        self.assertIn("## Worker\n", S1)
        body = S1.replace("## Worker\n", f"{COMMENTS}\n## Worker\n")
        self.assertIn("section '## Worker' is duplicated or out of contract order", section_errors(body))


if __name__ == "__main__":
    unittest.main()
