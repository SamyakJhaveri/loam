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
# A real ticket's line (distbench lean plan, tickets/factory-weekly-reset.md): prose around one backticked path.
REAL_LINE = "Edit: Loam `bin/factory` (limit_wait and its reset parser)."
GATE = "\nEdit-scope: gate"   # the header line a ticket opts in with; without it the fence only reports
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
        for name in ("src/a.py", "src/b.py", "tests/test_a.py", "README.md", "seed/.claude/skills/x/SKILL.md"):
            (self.wt / name).parent.mkdir(parents=True, exist_ok=True)
            (self.wt / name).write_text("base\n")
        (self.wt / ".claude").symlink_to("seed/.claude")   # as in Loam, where .claude is a link to seed/.claude
        (self.wt / "seed/.claude/skills/y").symlink_to("x")   # a tracked link to a directory, as seed/.claude/skills has
        (self.top / "outside").mkdir()
        (self.wt / "ext").symlink_to(self.top / "outside")   # a link out of the repository
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
        (self.run_dir / "round-1.checks").unlink(missing_ok=True)
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
        checks = self.round_checks("Edit: `src/a.py`, `tests/`", "echo x >> src/a.py && echo x > tests/test_new.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")

    def test_a_real_ticket_line_fences_its_backticked_paths_only(self) -> None:
        checks = self.round_checks(REAL_LINE + GATE, "mkdir -p bin && echo x > bin/factory")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        self.assertEqual((self.run_dir / "frozen" / "edit.txt").read_text(), "bin/factory\n")

    def test_in_shadow_a_path_off_the_line_is_reported_and_the_checks_run(self) -> None:
        checks = self.round_checks(REAL_LINE, "mkdir -p bin && echo x > bin/factory && echo x >> src/b.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        self.assertEqual((self.run_dir / "round-1.edit-scope").read_text().splitlines(), [
            "SHADOW edit-scope: the round changed src/b.py but the ticket's Edit: line lists only bin/factory; "
            "revert those paths"])
        self.assertIn("SHADOW edit-scope: the round changed src/b.py", (self.run_dir / "factory.log").read_text())

    def test_a_ticket_that_opts_in_fails_the_round_off_its_real_line(self) -> None:
        checks = self.round_checks(REAL_LINE + GATE, "mkdir -p bin && echo x > bin/factory && echo x >> src/b.py")
        self.assertEqual(checks.splitlines(), [
            "FAIL edit-scope: the round changed src/b.py but the ticket's Edit: line lists only bin/factory; "
            "revert those paths"])
        self.assertFalse((self.run_dir / "round-1.edit-scope").exists())

    def test_in_shadow_a_line_the_fence_cannot_read_sets_no_fence(self) -> None:
        checks = self.round_checks("Edit: src/*.py", "echo x >> src/b.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        self.assertFalse((self.run_dir / "frozen" / "edit.txt").exists())
        self.assertIn("SHADOW edit-scope: the Edit: line holds src/*.py", (self.run_dir / "factory.log").read_text())

    def test_adjacent_entries_and_a_leading_dot_slash_are_paths(self) -> None:
        # `src/a.py,tests/` is two entries, not `src/a.pytests/`; `./src/a.py` is git's `src/a.py`.
        for line in ("Edit: src/a.py,tests/", "Edit: ./src/a.py,./tests/", "Edit: `./src/a.py`,`tests/`."):
            with self.subTest(line):
                git("reset", "-q", "--hard", (self.run_dir / "base.sha").read_text().strip(), cwd=self.wt)
                (self.run_dir / "frozen" / "edit.txt").unlink(missing_ok=True)
                checks = self.round_checks(line, "echo x >> src/a.py && echo x > tests/test_new.py")
                self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
                self.assertEqual((self.run_dir / "frozen" / "edit.txt").read_text(), "src/a.py\ntests/\n")

    def test_an_entry_reads_as_git_spells_its_path(self) -> None:
        # git prints seed/.claude/... for a change made through the .claude link, and never a `.` segment.
        checks = self.round_checks("Edit: .claude/skills/x/SKILL.md, src/./a.py",
                                   "echo x >> .claude/skills/x/SKILL.md && echo x >> src/a.py")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        self.assertEqual((self.run_dir / "frozen" / "edit.txt").read_text(), "seed/.claude/skills/x/SKILL.md\nsrc/a.py\n")

    def test_a_listed_symlink_covers_itself_and_its_target(self) -> None:
        # Deleting or retargeting the link changes the link's own path; a change through it changes its target's.
        cases = {"deleted": "git rm -q seed/.claude/skills/y",
                 "retargeted": "ln -sfn ../../../src seed/.claude/skills/y",
                 "written through": "echo x >> seed/.claude/skills/y/SKILL.md"}
        for why, change in cases.items():
            with self.subTest(why):
                git("reset", "-q", "--hard", (self.run_dir / "base.sha").read_text().strip(), cwd=self.wt)
                (self.run_dir / "frozen" / "edit.txt").unlink(missing_ok=True)
                checks = self.round_checks("Edit: seed/.claude/skills/y", change)
                self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
                self.assertEqual((self.run_dir / "frozen" / "edit.txt").read_text(),
                                 "seed/.claude/skills/x\nseed/.claude/skills/y\n")

    def test_a_name_git_would_quote_is_read_as_written(self) -> None:
        # With core.quotePath (git's default) a plain --name-only prints "tests/na\303\257ve.py", quotes included.
        checks = self.round_checks("Edit: src/a.py, tests/", "echo x > tests/naïve.py && echo x > 'tests/a\"b.py'")
        self.assertEqual(checks, "PASS x\n\nCHECKS-END\n")
        git("reset", "-q", "--hard", (self.run_dir / "base.sha").read_text().strip(), cwd=self.wt)
        (self.run_dir / "frozen" / "edit.txt").unlink()
        checks = self.round_checks("", "echo x > tests/naïve.py",
                                   before="printf 'tests/\\n' > \"$RUN/frozen/protected.txt\"")
        self.assertEqual(checks, "FAIL do-not-touch tests/naïve.py \n")

    def test_a_path_list_git_cannot_give_ends_the_run_before_the_checks(self) -> None:
        # A failed `git diff` (exit 128 on a base it cannot read) never reads as no path off the line.
        out = self.round_checks("Edit: src/a.py", "echo x >> src/a.py",
                                before=f"echo {'0' * 40} > \"$RUN/base.sha\"")
        self.assertTrue(out.startswith("FINISH stopped-environment: could not list the paths round 1 changed"), out)
        self.assertFalse((self.run_dir / "round-1.checks").exists())

    def test_freeze_refuses_an_edit_line_that_is_not_all_paths(self) -> None:
        for line, why in (("Edit:", "the Edit: line lists no path"),
                          ("Edit: src/a.py (new)", "the Edit: line holds (new, which is not a path"),
                          ("Edit: src/*.py", "the Edit: line holds src/*.py, which is not a path"),
                          ("Edit: src/a.py, ../x.py", "the Edit: line holds ../x.py, whose .. segment climbs a directory"),
                          ("Edit: src/..", "the Edit: line holds src/.., whose .. segment climbs a directory"),
                          ("Edit: ext/a.py", "the Edit: line names ext/a.py, which is not a path inside the repository")):
            with self.subTest(line):
                out = self.round_checks(line + GATE, "echo x >> src/a.py")
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
                checks = self.round_checks("Edit: src/a.py, tests/" + GATE, change)
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

    def lint(self, edit_line: str, gate: str = GATE) -> tuple[int, str]:
        """Exit code and output of `bin/factory lint` over a whole body whose header holds edit_line."""
        body = (f"# Lint fixture\nBrief:\nfixture\nBlocked by: none\n{edit_line}{gate}\n\n## Goal and why\nfixture\n\n"
                "## Do not touch\nThe standing list.\n\n## Out of scope\nnothing\n\n"
                f"## Done checks\n```done-checks\npredict greet test -f g.txt\n{GREET}\nguard true && pass g || fail g \"guard\"\n```\n\n"
                "## Worker\nworker: claude\ncodex-review: no\neffort: high\ncontract: 2\n"
                "goal: the done-checks block prints no FAIL line, or stop after 60 turns\n\n## Decisions\nnone\n")
        path = self.tmp / "ticket.md"
        path.write_text(body)
        proc = subprocess.run(["bin/factory", "lint", str(path)], cwd=ROOT, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout + proc.stderr

    def cmd_run(self, stem: str, edit_line: str, status: str) -> pathlib.Path:
        """The new run dir of the real cmd_run over a file ticket whose header holds edit_line."""
        before = set((self.tmp / "runs" / stem).glob("*"))
        ticket = self.tmp / f"{stem}.md"
        ticket.write_text(f"# Fixture\n\n{edit_line}\n\n## Done checks\n\n```done-checks\n{GREET}\n```\n")
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.tmp / "runs"),
                   FACTORY_WORKER_ADVISOR="")
        script = (f". bin/factory\n{STUBS}\nMAIN_CHECKOUT='{self.tmp}/repo'; GRADERS_DIR='{GRADERS}'\n"
                  f"cmd_run '{ticket}'")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        (run,) = set((self.tmp / "runs" / stem).iterdir()) - before
        self.assertEqual((run / "status").read_text().strip(), status, proc.stdout + proc.stderr)
        return run

    def test_lint_rejects_an_edit_line_with_no_path_or_a_word_the_fence_drops(self) -> None:
        for line, why in (("Edit:", "the Edit: line lists no path"),
                          ("Edit: ``", "the Edit: line lists no path"),
                          ("Edit: `src/a.py`, tests/ (new)",
                           "the Edit: line holds tests/ outside backticks, where the fence reads no path"),
                          ("Edit: bin/*.sh, docs/", "the Edit: line holds bin/*.sh, which is not a path"),
                          ("Edit: bin/factory, docs/..", "the Edit: line holds docs/.., whose .. segment climbs a directory")):
            with self.subTest(line):
                rc, out = self.lint(line)
                self.assertEqual(rc, 1, out)
                self.assertIn(f": {why}", out)

    def test_lint_accepts_paths_split_by_commas_and_spaces(self) -> None:
        for line in ("", "Edit: bin/factory,docs/factory/ ./NOTES.md", "Edit: bin/factory, bin/tests/.", REAL_LINE):
            with self.subTest(line):
                rc, out = self.lint(line)
                self.assertEqual(rc, 0, out)

    def test_lint_in_shadow_reports_an_unreadable_line_without_failing(self) -> None:
        rc, out = self.lint("Edit: bin/*.sh, docs/", gate="")
        self.assertEqual(rc, 0, out)
        self.assertIn("SHADOW edit-scope (not an error until the fence leaves shadow): the Edit: line holds bin/*.sh", out)

    def test_freeze_writes_edit_txt_into_the_hashed_frozen_set(self) -> None:
        run = self.cmd_run("scoped", "Edit: g.txt, docs/", "stopped-environment")
        self.assertEqual((run / "frozen/edit.txt").read_text(), "docs/\ng.txt\n")
        hashed = [line.split()[-1] for line in (run / "frozen/sha256").read_text().splitlines()]
        self.assertIn("edit.txt", hashed)

    def test_freeze_ends_a_run_whose_edit_line_lint_rejects(self) -> None:
        run = self.cmd_run("bad", "Edit: (none)" + GATE, "ticket-defect")
        self.assertFalse((run / "frozen/edit.txt").exists())
        self.assertFalse((run / "round-0.checks").exists())
        # The worktree is removed as at any other exit, so the corrected body's run gets its own branch.
        repo = self.tmp / "repo"
        self.assertFalse((self.tmp / "repo-bad").exists())
        fixed = self.cmd_run("bad", "Edit: g.txt", "stopped-environment")
        self.assertEqual((fixed / "frozen/edit.txt").read_text(), "g.txt\n")
        branches = git("for-each-ref", "--format=%(refname:short)", "refs/heads/factory/", cwd=repo).splitlines()
        self.assertEqual(sorted(branches), sorted([f"factory/bad-{run.name}", f"factory/bad-{fixed.name}"]))
        self.assertNotEqual(run.name, fixed.name)


if __name__ == "__main__":
    unittest.main()
