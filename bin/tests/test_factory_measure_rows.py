"""Rows measured: a `runs=N` row prints its median and range, an undeclared time, token, or cost row says single
sample, and a count row prints exactly as before (F9); after the rows the worktree and its index are back at HEAD
(#608). bin/factory is sourced (FACTORY_SOURCED=1); measure_rows runs the rows in a scratch git repository.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                          capture_output=True, text=True, check=True).stdout


def scratch_repo(path: pathlib.Path, files: dict[str, str]) -> None:
    """A git repository at path with one commit holding files."""
    path.mkdir()
    git(path, "init", "-q")
    for name, text in files.items():
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text)
    git(path, "add", "-A")
    git(path, "commit", "-qm", "base")


def measure(run: pathlib.Path, worktree: pathlib.Path, rows: str, prelude: str = "") -> subprocess.CompletedProcess:
    script = (f"RUN='{run}'; WORKTREE='{worktree}'; LEDGER=/dev/null; DAILY=/dev/null; KEY=t\n{prelude}"
              f"BODY=$'## Rows measured\\n{rows}\\n\\n## Worker\\n'\n"
              "measure_rows 1")
    return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                          env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)


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
            # The rows run in a git repository apart from RUN, so the restore after them leaves round-1.measure.
            worktree = run / "wt"
            scratch_repo(worktree, {"README": "r\n"})
            prelude = (f"next() {{ n=$(cat '{run}/n' 2> /dev/null || echo 0); echo $((n + 1)) > '{run}/n'; echo $((n * 2)); }}\n"
                       "du() { echo 3; }\n"
                       "export -f next du\n")
            proc = measure(run, worktree, rows, prelude)
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

    def test_rows_leave_worktree_at_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run, worktree = pathlib.Path(tmp) / "run", pathlib.Path(tmp) / "wt"
            run.mkdir()
            scratch_repo(worktree, {"evals/scores.jsonl": '{"seed":1}\n', "gone.txt": "g\n", ".gitignore": "keep.log\n"})
            (worktree / "keep.log").write_text("kept\n")
            head = git(worktree, "rev-parse", "HEAD")
            # The first row appends to and stages a tracked file; the second creates untracked files, stages a new
            # file and a deletion, and reads the first row's line count. grep -c, not wc -l: macOS wc pads its count.
            rows = "\n".join([
                "scores: echo x >> evals/scores.jsonl && git add evals/scores.jsonl; grep -c . evals/scores.jsonl | 1",
                "junk: mkdir -p out && touch out/a junk.txt staged.txt && git add staged.txt && git rm -q gone.txt;"
                " grep -c . evals/scores.jsonl | 1",
            ])
            proc = measure(run, worktree, rows)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((run / "round-1.measure").read_text().splitlines(),
                             ["MEASURE scores 2 (baseline 1)", "MEASURE junk 2 (baseline 1)"])
            self.assertEqual(git(worktree, "status", "--porcelain"), "")
            self.assertEqual((worktree / "evals/scores.jsonl").read_text(), '{"seed":1}\n')
            self.assertEqual((worktree / "gone.txt").read_text(), "g\n")
            self.assertFalse((worktree / "staged.txt").exists())
            self.assertFalse((worktree / "out").exists())
            self.assertEqual((worktree / "keep.log").read_text(), "kept\n")
            self.assertEqual(git(worktree, "rev-parse", "HEAD"), head)


if __name__ == "__main__":
    unittest.main()
