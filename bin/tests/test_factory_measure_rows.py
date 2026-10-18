"""Rows measured: a `runs=N` row prints its median and range, an undeclared time, token, or cost row says single
sample, and a count row prints exactly as before (F9). bin/factory is sourced (FACTORY_SOURCED=1); measure_rows
runs the rows in a temporary directory.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class MeasureRowsTests(unittest.TestCase):
    def test_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp)
            # Each call of `next` prints 0, 2, 4, ... so a repeated row has a known median and range.
            rows = "\n".join([
                "files: echo 19 | 20",
                "echo 7862 | 7862 bytes and about 1970 tokens",
                "wall: echo 31 | 40 s",
                "runs=5 wall time: next | 5",
                "runs=2 cost: echo abc | 1",
                "runs=1 always-on tokens: echo 7862 | 7862",
                "disk: du -ms | 3",
                "runs=2 tokens: echo $((1000000 + $(next) / 2)) | 1000000",
            ])
            script = (f"RUN='{run}'; WORKTREE='{run}'; LEDGER=/dev/null; DAILY=/dev/null; KEY=t\n"
                      f"next() {{ n=$(cat '{run}/n' 2> /dev/null || echo 0); echo $((n + 1)) > '{run}/n'; echo $((n * 2)); }}\n"
                      "du() { echo 3; }\n"
                      "export -f next du\n"
                      f"BODY=$'## Rows measured\\n{rows}\\n\\n## Worker\\n'\n"
                      "measure_rows 1")
            proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                                  env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            lines = (run / "round-1.measure").read_text().splitlines()
            # A row with no `<row>:` label: only its value and note are pinned, not the row text it prints.
            self.assertTrue(lines.pop(1).endswith(" 7862 (baseline 7862bytesandabout1970tokens)"), lines)
            self.assertEqual(lines, [
                "MEASURE files 19 (baseline 20)",
                "MEASURE wall 31 (baseline 40s; single sample, no runs=N)",
                "MEASURE wall time 4 (median of 5 runs, range 0 to 8; baseline 5)",
                "MEASURE cost abc / abc (2 runs, not all numbers, so no median; baseline 1)",
                "MEASURE always-on tokens 7862 (baseline 7862)",
                "MEASURE disk 3 (baseline 3)",
                "MEASURE tokens 1000005.5 (median of 2 runs, range 1000005 to 1000006; baseline 1000000)",
            ])


if __name__ == "__main__":
    unittest.main()
