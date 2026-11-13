"""Lint rejects a Do not touch `Except:` line that names no path (CONTRACT.md, Lint rules).

freeze reads the paths after `Except:` into exempt.txt with ticket_paths, so prose such as "the files on the
header's Edit line" excepts nothing and the do-not-touch check then fails every edit to a fenced path (distbench
L01 run 1, 2026-11-13). bin/factory is sourced (FACTORY_SOURCED=1) and the real lint_body reads the S1 fixture
body under a non-fixture name, with its Except line swapped.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
S1 = (ROOT / "bin/factory.d/fixtures/S1.md").read_text()
EXCEPT = re.compile(r"Except: .*$", re.M)
ERROR = "names no path"


def lint_errors(except_tail: str) -> str:
    """stderr of the real lint_body over S1 with its Except line replaced."""
    body = EXCEPT.sub(lambda _: except_tail, S1, count=1)
    proc = subprocess.run(["bash", "-c", '. bin/factory; TARGET=$ROOT; SRC=t.md; ERRS=0; BODY=$1; lint_body', "_", body],
                          cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT)},
                          capture_output=True, text=True, check=False)
    return proc.stderr


class ExceptPathsTests(unittest.TestCase):
    def test_prose_except_line_is_rejected(self) -> None:
        line = "Except: the files on the header's Edit line."
        errors = [e for e in lint_errors(line).splitlines() if ERROR in e]
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(line, errors[0])

    def test_except_line_with_paths_passes(self) -> None:
        for line in ("Except: bin/check, docs/factory/LOOP.md (this ticket edits them).",
                     "Except: `bin/check`, `bin/factory`."):
            self.assertNotIn(ERROR, lint_errors(line), line)


if __name__ == "__main__":
    unittest.main()
