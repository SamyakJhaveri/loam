"""The PR body shows the done checks failing at base and passing at the graded sha, not only the judge's summary.

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real open_pr runs on a fake run directory over a
throwaway worktree whose origin is a local bare repository. gh and notify are shell stubs; the gh stub
copies the `--body-file` it is given, so the test reads the body GitHub would get. No network.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
TICKET = "## Goal and why\n\nMake the widget work.\n\n## Merge checklist\n\n- read the diff\n"


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class PrBodyChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        origin = top / "origin.git"
        git("init", "-q", "--bare", str(origin), cwd=top)
        self.wt = top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "main", cwd=self.wt)
        git("remote", "add", "origin", str(origin), cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        self.base = git("rev-parse", "HEAD", cwd=self.wt)
        git("checkout", "-q", "-b", "factory/7", cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "ticket 7: the fix", cwd=self.wt)
        self.graded = git("rev-parse", "HEAD", cwd=self.wt)
        self.run_dir = top / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "frozen" / "issue.md").write_text("# Widget works\n")
        (self.run_dir / "base.sha").write_text(self.base + "\n")
        (self.run_dir / "started").write_text("0\n")
        (self.run_dir / "ledger.jsonl").write_text("")
        (self.run_dir / "decisions.md").write_text("- kept it small\n")
        (self.run_dir / "round-1.checks").write_text("FAIL widget: round one is not the final round\nPASS guard\n")
        (self.run_dir / "round-2.checks").write_text("PASS widget\nPASS guard\n")
        (self.run_dir / "round-2.judge.json").write_text('{"verdict": "pass", "rows": {"widget": "pass"}}\n')
        (self.run_dir / "round-2.review.json").write_text('{"verdict": "merge", "findings": []}\n')
        self.sent = top / "sent-body.md"

    def open_pr(self, existing: bool = False, ticket: str = TICKET) -> str:
        """Run the real open_pr for issue 7 at round 2 and return the body handed to GitHub.

        With existing, PR 9 is already open, so the body goes through the REST PATCH; else through `gh pr create`.
        """
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; BRANCH=factory/7; ISSUE=7; KEY=7; IS_FILE=0\n"
            f"ROUND=2; GRADED_SHA={self.graded}; LEDGER=\"$RUN/ledger.jsonl\"; DECISIONS=\"$RUN/decisions.md\"\n"
            "BODY=\"$TICKET\"\n"
            "notify() { :; }\n"
            'gh() { case "$1 $2" in\n'
            f'  "pr view") {"echo 9" if existing else "return 1"} ;;\n'
            f'  "pr create") while [ $# -gt 0 ]; do [ "$1" = --body-file ] && cp "$2" "{self.sent}"; shift; done\n'
            "    echo https://github.com/acme/widget/pull/9 ;;\n"
            f'  "api -X") while [ $# -gt 0 ]; do [ "$1" = -f ] && printf %s "${{2#body=}}" > "{self.sent}"; shift; done ;;\n'
            "esac; }\n"
            "open_pr\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                   "REPO": "acme/widget", "TICKET": ticket},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("EXIT pr-opened (0): https://github.com/acme/widget/pull/9", proc.stderr)
        return self.sent.read_text()

    def test_body_shows_checks_failing_at_base_and_passing_at_the_graded_sha(self) -> None:
        (self.run_dir / "round-0.checks").write_text("FAIL widget: the widget does not work\nPASS guard\n")
        body = self.open_pr()
        before = f"## Checks at base {self.base[:8]} (round 0)\n\n```\nFAIL widget\nPASS guard\n```\n"
        after = "## Checks at the graded sha (round 2)\n\n```\nPASS widget\nPASS guard\n```\n"
        self.assertIn(before, body)
        self.assertIn(after, body)
        self.assertLess(body.index(before), body.index(after))
        self.assertLess(body.index(after), body.index("## Judge"))
        self.assertNotIn("round one is not the final round", body)
        self.assertNotIn("the widget does not work", body)

    def test_a_long_checks_file_is_capped_with_a_pointer_to_the_run_directory(self) -> None:
        (self.run_dir / "round-0.checks").write_text("".join(f"FAIL widget-{i}: line {i}\n" for i in range(1, 81)))
        body = self.open_pr()
        self.assertNotIn("FAIL widget-51\n", body)
        self.assertIn(f"FAIL widget-50\n... 30 more lines in {self.run_dir / 'round-0.checks'}\n```\n", body)

    def test_blank_lines_before_each_result_neither_show_nor_count_toward_the_cap(self) -> None:
        # With #259, lib.sh starts each result on a fresh line, so 30 checks write 60 lines.
        (self.run_dir / "round-0.checks").write_text("".join(f"\nFAIL widget-{i}: no\n" for i in range(1, 31)))
        body = self.open_pr()
        results = "".join(f"FAIL widget-{i}\n" for i in range(1, 31))
        self.assertIn(f"(round 0)\n\n```\n{results}```\n", body)
        self.assertNotIn("more lines in", body)

    def test_only_result_words_names_and_numeric_measures_show_each_cut_to_300_characters(self) -> None:
        # Raw output can hold a secret (Loam is public), push the results past the cap, or close the fence.
        noise = "```\n@someone see this\nGH_TOKEN=ghp_not_a_real_token\n"
        noise += "".join(f"tests/test_x.py::test_{i} PASSED\n" for i in range(1, 61))
        long_name = "FAIL " + "n" * 5000
        results = (f"FAIL widget: {'x' * 5000}\n{long_name}: why\nFAIL ```: closes the fence\n"
                   "MEASURE speed 3\nMEASURE log error: ghp_measured_token\nPASS guard\n")
        (self.run_dir / "round-0.checks").write_text(noise + results)
        body = self.open_pr()
        shown = f"FAIL widget\n{long_name[:300]}\nFAIL\nMEASURE speed 3\nMEASURE log\nPASS guard\n"
        self.assertIn(f"(round 0)\n\n```\n{shown}```\n", body)
        for leaked in ("ghp_", "@someone", "test_x.py", "xxx", "why", "closes the fence", "n" * 296):
            self.assertNotIn(leaked, body)

    def test_a_fail_reason_never_reaches_the_body_on_create_or_update(self) -> None:
        # lib.sh's `fail NAME "$out"` puts captured output in the reason: here render_into's Copier stderr.
        # Loam is public and GitHub keeps every body edit, so a reason must not reach either path (H1).
        secret = "Authorization: Bearer ghp_000000000000000000000000000000000000"
        (self.run_dir / "round-0.checks").write_text(f"\nFAIL render: copier copy exit 1; {secret}\nPASS guard\n")
        for existing in (False, True):
            with self.subTest(existing=existing):
                body = self.open_pr(existing)
                for leaked in ("ghp_0000", "Bearer", "copier copy exit"):
                    self.assertNotIn(leaked, body)
                self.assertIn("```\nFAIL render\nPASS guard\n```\n", body)
                self.assertIn(f"Reasons and full output: {self.run_dir / 'round-0.checks'}\n", body)

    def test_body_opens_with_the_workers_mechanism_paragraph_or_says_there_is_none(self) -> None:
        # The owner judges the merge from the worker's own account, read before anything else (#330).
        (self.run_dir / "round-0.checks").write_text("FAIL widget\n")
        self.assertTrue(self.open_pr().startswith(
            "## How it works\n\n(the worker wrote no mechanism paragraph)\n\nCloses #7\n\n"))
        para = "The parser reads the flag before any write, so a bad flag fails with nothing on disk."
        (self.run_dir / "mechanism.md").write_text(f"\n{para}")
        self.assertTrue(self.open_pr().startswith(f"## How it works\n\n{para}\n\nCloses #7\n\n## Goal\n"))

    def test_every_merge_checklist_line_becomes_a_checkbox_whether_or_not_it_is_a_bullet(self) -> None:
        # CONTRACT.md accepts any non-blank checklist line; a prose step must not vanish from the body.
        (self.run_dir / "round-0.checks").write_text("FAIL widget\n")
        ticket = TICKET + ("Before merge, run the paid eval and commit its line.\n\n- tag the release\n"
                           "  - after the eval\n- [ ] push the tag\n")
        self.assertIn("## Merge checklist\n\n- [ ] read the diff\n- [ ] Before merge, run the paid eval and commit "
                      "its line.\n- [ ] tag the release\n  - after the eval\n- [ ] push the tag\n\n## Decisions",
                      self.open_pr(ticket=ticket))


if __name__ == "__main__":
    unittest.main()
