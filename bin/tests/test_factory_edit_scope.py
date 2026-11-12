"""A round that changes a path off the ticket's `Edit:` line fails without running the checks (lean plan S2-02b).

`bin/factory` is sourced (FACTORY_SOURCED=1). Each case freezes a ticket header's `Edit:` line as freeze does
(freeze_edit_line), commits a round in a scratch worktree, and runs the real round_checks with run_checks stubbed to
print one PASS, so the checks file shows whether the fence stopped the round or the checks ran. A ticket with no
`Edit:` line keeps the old behaviour: only Do not touch fences paths. Lint runs as `bin/factory lint` over a whole
body, and the freeze cases run the real cmd_run on a file ticket through freeze and round 0, stubbed as in
test_factory_predict.py.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "REPO", "RUN", "LOG")
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
GREET = 'test -f g.txt && grep -q hello g.txt && pass greet || fail greet "g.txt lacks hello"'
STUBS = ("assert_target_ready() { :; }; claude_version_ok() { :; }; exec_frozen() { :; }; "
         'main_loop() { finish stopped-environment "stub worker round"; }')
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

    def round_checks(self, edit_line: str, change: str, before: str = "") -> str:
        """Freeze a header holding edit_line, commit the round `change` (shell, in the worktree) makes, run `before`
        (shell), and return round-1.checks, or what a `finish` printed when the round ended the run."""
        body = HEADER.format(edit=edit_line)
        script = (f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; TARGET='{self.wt}'; LOG=\"$RUN/factory.log\"; ROUND=1\n"
                  'finish() { echo "FINISH $1: $2"; exit 0; }\n'
                  f"BODY=$(cat <<'TICKET'\n{body}TICKET\n)\nfreeze_edit_line\n"
                  f"( cd \"$WORKTREE\" && {change} && git add -A && git -c user.name=t -c user.email=t@t commit -qm round )\n"
                  "run_checks() { printf 'PASS x\\n\\nCHECKS-END\\n' > \"$2\"; }; method_evidence() { :; }\n"
                  f'{before}\nround_checks "$RUN/round-1.checks"\n')
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env={**env, "FACTORY_SOURCED": "1"},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        if proc.stdout.startswith("FINISH"):
            return proc.stdout
        return (self.run_dir / "round-1.checks").read_text()

    def test_a_round_inside_the_edit_line_runs_the_checks(self) -> None:
        # Backticks and commas as a ticket writes them; a directory covers what sits under it.
        checks = self.round_checks("Edit: `src/a.py`, tests/", "echo x >> src/a.py && echo x > tests/test_new.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")

    def test_adjacent_entries_and_a_leading_dot_slash_are_paths(self) -> None:
        # `src/a.py,tests/` is two entries, not `src/a.pytests/`; `./src/a.py` is git's `src/a.py`.
        for line in ("Edit: src/a.py,tests/", "Edit: ./src/a.py,./tests/", "Edit: `./src/a.py`,`tests/`."):
            with self.subTest(line):
                git("reset", "-q", "--hard", (self.run_dir / "base.sha").read_text().strip(), cwd=self.wt)
                (self.run_dir / "frozen" / "edit.txt").unlink(missing_ok=True)
                checks = self.round_checks(line, "echo x >> src/a.py && echo x > tests/test_new.py")
                self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
                self.assertEqual((self.run_dir / "frozen" / "edit.txt").read_text(), "src/a.py\ntests/\n")

    def test_a_path_list_git_cannot_give_ends_the_run_before_the_checks(self) -> None:
        # A failed `git diff` (exit 128 on a base it cannot read) never reads as no path off the line.
        out = self.round_checks("Edit: src/a.py", "echo x >> src/a.py",
                                before=f"echo {'0' * 40} > \"$RUN/base.sha\"")
        self.assertTrue(out.startswith("FINISH stopped-environment: could not list the paths round 1 changed"), out)
        self.assertFalse((self.run_dir / "round-1.checks").exists())

    def test_freeze_refuses_an_edit_line_that_is_not_all_paths(self) -> None:
        for line, why in (("Edit:", "the Edit: line lists no path"),
                          ("Edit: src/a.py (new)", "the Edit: line holds (new, which is not a path"),
                          ("Edit: src/*.py", "the Edit: line holds src/*.py, which is not a path")):
            with self.subTest(line):
                out = self.round_checks(line, "echo x >> src/a.py")
                self.assertTrue(out.startswith(f"FINISH ticket-defect: {why}"), out)
                self.assertFalse((self.run_dir / "round-1.checks").exists())

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


class EditLineLintAndFreezeTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        repo = self.tmp / "repo"
        repo.mkdir()
        (repo / "g.txt").write_text("bye\n")
        for args in (["init", "-q"], ["add", "g.txt"], ["commit", "-qm", "base"]):
            git(*args, cwd=repo)

    def lint(self, edit_line: str) -> tuple[int, str]:
        """Exit code and output of `bin/factory lint` over a whole body whose header holds edit_line."""
        body = (f"# Lint fixture\nBrief:\nfixture\nBlocked by: none\n{edit_line}\n\n## Goal and why\nfixture\n\n"
                "## Do not touch\nThe standing list.\n\n## Out of scope\nnothing\n\n"
                f"## Done checks\n```done-checks\npredict greet test -f g.txt\n{GREET}\nguard true && pass g || fail g \"guard\"\n```\n\n"
                "## Worker\nworker: claude\ncodex-review: no\neffort: high\ncontract: 2\n"
                "goal: the done-checks block prints no FAIL line, or stop after 60 turns\n\n## Decisions\nnone\n")
        path = self.tmp / "ticket.md"
        path.write_text(body)
        proc = subprocess.run(["bin/factory", "lint", str(path)], cwd=ROOT, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout + proc.stderr

    def cmd_run(self, stem: str, edit_line: str, status: str) -> pathlib.Path:
        """The run dir of the real cmd_run over a file ticket whose header holds edit_line."""
        ticket = self.tmp / f"{stem}.md"
        ticket.write_text(f"# Fixture\n\n{edit_line}\n\n## Done checks\n\n```done-checks\n{GREET}\n```\n")
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.tmp / "runs"),
                   FACTORY_WORKER_ADVISOR="")
        script = (f". bin/factory\n{STUBS}\nMAIN_CHECKOUT='{self.tmp}/repo'; GRADERS_DIR='{GRADERS}'\n"
                  f"cmd_run '{ticket}'")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        (run,) = (self.tmp / "runs" / stem).iterdir()
        self.assertEqual((run / "status").read_text().strip(), status, proc.stdout + proc.stderr)
        return run

    def test_lint_rejects_an_edit_line_with_no_path_or_a_word_the_fence_drops(self) -> None:
        for line, why in (("Edit:", "the Edit: line lists no path"),
                          ("Edit: ``", "the Edit: line lists no path"),
                          ("Edit: Loam `bin/factory` (limit_wait and its reset parser).",
                           "the Edit: line holds (limit_wait, which is not a path"),
                          ("Edit: bin/*.sh, docs/", "the Edit: line holds bin/*.sh, which is not a path")):
            with self.subTest(line):
                rc, out = self.lint(line)
                self.assertEqual(rc, 1, out)
                self.assertIn(f": {why}", out)

    def test_lint_accepts_paths_split_by_commas_and_spaces(self) -> None:
        for line in ("", "Edit: `bin/factory`,docs/factory/ ./NOTES.md", "Edit: bin/factory, bin/tests/."):
            with self.subTest(line):
                rc, out = self.lint(line)
                self.assertEqual(rc, 0, out)

    def test_freeze_writes_edit_txt_into_the_hashed_frozen_set(self) -> None:
        run = self.cmd_run("scoped", "Edit: g.txt, docs/", "stopped-environment")
        self.assertEqual((run / "frozen/edit.txt").read_text(), "docs/\ng.txt\n")
        hashed = [line.split()[-1] for line in (run / "frozen/sha256").read_text().splitlines()]
        self.assertIn("edit.txt", hashed)

    def test_freeze_ends_a_run_whose_edit_line_lint_rejects(self) -> None:
        run = self.cmd_run("bad", "Edit: (none)", "ticket-defect")
        self.assertFalse((run / "frozen/edit.txt").exists())
        self.assertFalse((run / "round-0.checks").exists())


if __name__ == "__main__":
    unittest.main()
