"""A round that changes a path off the ticket's `Edit:` line fails without running the checks (lean plan S2-02b).

`bin/factory` is sourced (FACTORY_SOURCED=1). Each case freezes a ticket header's `Edit:` line as freeze does
(freeze_edit_line), commits a round in a scratch worktree, and runs the real round_checks with run_checks stubbed to
print one PASS, so the checks file shows whether the fence stopped the round or the checks ran. A ticket with no
`Edit:` line keeps the old behaviour: only Do not touch fences paths.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "REPO", "RUN", "LOG")
HEADER = "# F41: a ticket\n\nBrief: x\nBlocked by: none\n{edit}\n## Goal and why\n\nEdit: not/this/one.py\n"


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class EditScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.wt = self.top / "wt"
        for name in ("src/a.py", "src/b.py", "tests/test_a.py", "README.md"):
            (self.wt / name).parent.mkdir(parents=True, exist_ok=True)
            (self.wt / name).write_text("base\n")
        git("init", "-q", "-b", "factory/7", cwd=self.wt)
        git("add", "-A", cwd=self.wt)
        git("commit", "-q", "-m", "base", cwd=self.wt)
        self.run_dir = self.top / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        for name in ("protected.txt", "exempt.txt"):
            (self.run_dir / "frozen" / name).write_text("")
        (self.run_dir / "base.sha").write_text(git("rev-parse", "HEAD", cwd=self.wt) + "\n")

    def round_checks(self, edit_line: str, change: str) -> str:
        """Freeze a header holding edit_line, commit the round `change` (shell, in the worktree) makes, and return
        round-1.checks."""
        body = HEADER.format(edit=edit_line)
        script = (f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; TARGET='{self.wt}'; LOG=\"$RUN/factory.log\"; ROUND=1\n"
                  f"BODY=$(cat <<'TICKET'\n{body}TICKET\n)\nfreeze_edit_line\n"
                  f"( cd \"$WORKTREE\" && {change} && git add -A && git -c user.name=t -c user.email=t@t commit -qm round )\n"
                  "run_checks() { printf 'PASS x\\n\\nCHECKS-END\\n' > \"$2\"; }; method_evidence() { :; }\n"
                  'round_checks "$RUN/round-1.checks"\n')
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env={**env, "FACTORY_SOURCED": "1"},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return (self.run_dir / "round-1.checks").read_text()

    def test_a_round_inside_the_edit_line_runs_the_checks(self) -> None:
        # Backticks and commas as a ticket writes them; a directory covers what sits under it.
        checks = self.round_checks("Edit: `src/a.py`, tests/", "echo x >> src/a.py && echo x > tests/test_new.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")

    def test_a_path_off_the_edit_line_fails_the_round_and_names_it(self) -> None:
        cases = {"an edited file": "echo x >> src/a.py && echo x >> src/b.py",
                 "a deleted file": "git rm -q src/b.py",
                 "a file renamed onto the line": "git mv src/b.py tests/b.py"}
        for why, change in cases.items():
            with self.subTest(why):
                git("reset", "-q", "--hard", (self.run_dir / "base.sha").read_text().strip(), cwd=self.wt)
                (self.run_dir / "frozen" / "edit.txt").unlink(missing_ok=True)
                checks = self.round_checks("Edit: src/a.py, tests/", change)
                self.assertEqual(checks.splitlines(), [
                    "FAIL edit-scope: the round changed src/b.py but the ticket's Edit: line lists only src/a.py, tests/; "
                    "revert those paths"])

    def test_a_new_top_level_file_on_the_edit_line_counts(self) -> None:
        checks = self.round_checks("Edit: NOTES.md", "echo x > NOTES.md")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")

    def test_a_ticket_with_no_edit_line_keeps_the_old_behaviour(self) -> None:
        # The `Edit:` line under `## Goal and why` is prose, not the header's line.
        checks = self.round_checks("", "echo x >> src/b.py && echo x >> README.md")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        self.assertFalse((self.run_dir / "frozen" / "edit.txt").exists())


if __name__ == "__main__":
    unittest.main()
