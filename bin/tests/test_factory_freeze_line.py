"""Lint fails a distbench ticket that lost its FREEZE or "For this ticket: pstack" line (distbench PR 514).

A recut dropped both lines from seven distbench tickets and lint passed them; a factory worker reads only its
ticket, so the lines must stay in each one. bin/factory is sourced (FACTORY_SOURCED=1) and the real lint_body
runs on a throwaway repository whose GitHub origin is never contacted. The assertions read only these two
rules' messages, since a minimal body fails other rules too.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FREEZE = ("FREEZE: never open, grep or print experiments/*/runs.jsonl, any regrade.jsonl, analysis outputs, "
          "docs/research/2026-11-05-replan/reports/runs-known.md, docs/research/2026-10-30-redesign/reports/"
          "surprise-isc.md or docs/research/2026-10-30-redesign/reports/failure-analysis.md.")
METHOD = "For this ticket: pstack tdd (rulings-log RULING 2026-11-11 21:55 PT (pstack habit)): new code with its tests."
BODY = "# W99: a ticket\nBrief: x.\n\n## Goal and why\nWhy.\n{lines}\n## Do not touch\nThe standing list.\n"


def lint_errors(repo_dir: pathlib.Path, body: str) -> str:
    """stderr of the real lint_body over `body`, with `repo_dir` as the target."""
    env = {k: v for k, v in os.environ.items() if k != "FACTORY_ROOT" and not k.startswith("LOAM_FACTORY_")}
    proc = subprocess.run(["bash", "-c", '. bin/factory; use_target "$1" || exit 9; SRC=t; ERRS=0; BODY=$2; lint_body',
                           "_", str(repo_dir), body],
                          cwd=ROOT, env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT)},
                          capture_output=True, text=True, check=False, timeout=60)
    assert proc.returncode != 9, proc.stderr
    return proc.stderr


def repo(path: pathlib.Path, origin: str) -> pathlib.Path:
    path.mkdir(parents=True)
    for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", origin]):
        subprocess.run(["git", *args], cwd=path, check=True, capture_output=True)
    return path.resolve()


class FreezeLineTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        self.distbench = repo(top / "distbench", "git@github.com:SamyakJhaveri/distbench.git")
        self.other = repo(top / "widget", "https://github.com/acme/widget.git")

    def test_a_distbench_ticket_without_freeze_or_method_line_fails(self) -> None:
        err = lint_errors(self.distbench, BODY.format(lines=""))
        self.assertIn("LINT t: a distbench ticket needs its FREEZE line", err)
        self.assertIn("LINT t: a distbench ticket needs its 'For this ticket: pstack", err)

    def test_a_freeze_line_that_drops_a_frozen_file_fails(self) -> None:
        cut = FREEZE.replace("docs/research/2026-11-05-replan/reports/runs-known.md, ", "")
        err = lint_errors(self.distbench, BODY.format(lines=f"{METHOD}\n{cut}\n"))
        self.assertIn("the FREEZE line must name runs-known.md", err)
        self.assertNotIn("needs its", err)

    def test_both_lines_pass_bare_or_as_a_quoted_bullet(self) -> None:
        for freeze in (FREEZE, f"> - {FREEZE}"):
            err = lint_errors(self.distbench, BODY.format(lines=f"{METHOD}\n{freeze}\n"))
            self.assertNotIn("FREEZE", err)
            self.assertNotIn("For this ticket", err)

    def test_another_target_needs_neither_line(self) -> None:
        err = lint_errors(self.other, BODY.format(lines=""))
        self.assertNotIn("FREEZE", err)
        self.assertNotIn("For this ticket", err)


if __name__ == "__main__":
    unittest.main()
