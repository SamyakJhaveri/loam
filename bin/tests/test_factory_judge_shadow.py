"""A judge fail on only bookkeeping rows (JUDGE_SHADOW_ROWS, `honest`) whose fixes all target decisions.md logs
judge-shadow and does not block (owner, 12 Nov 2026); a fail on a substantive row (`correct`, `verified`), with a fix that
targets a file of the change, or with no fix at all, still fails the graders. Each judge fix is an object whose `target`
names the one file it edits (judge.schema.json), so the shadow pass reads that field, never the fix's text.

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real graders, run_judge and run_review run over a throwaway git
worktree. Only the model call (call_json) is stubbed: it writes the reply named for its role and records the role, so
the test sees whether the reviewer was reached. The evidence bundle and the mutation sweep are stubbed. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS_PASS = {"correct": "pass", "verified": "pass", "honest": "pass"}
CLEAN_REVIEW = {"verdict": "merge", "findings": []}


LABEL = ("decisions.md", "label the SKIP step unverified")


def judge(rows: dict[str, str], fixes: list[tuple[str, str]]) -> dict[str, object]:
    return {"verdict": "fail", "rows": rows, "evidence": {}, "backlog": [],
            "fixes": [{"target": target, "fix": fix} for target, fix in fixes]}


class JudgeShadowTests(unittest.TestCase):
    def graders(self, judge_reply: dict[str, object] | str, stale_shadow: bool = False,
                root_decisions: bool = False) -> tuple[int, pathlib.Path, str]:
        """(graders' exit, the run dir, the log) for one round whose judge returns judge_reply.

        With stale_shadow, the round already holds a round-1.judge-shadow, as an earlier grading of it leaves.
        With root_decisions, the repository commits a decisions.md at its root.
        """
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        wt, run = top / "wt", top / "run"
        wt.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wt, check=True)
        if root_decisions:
            (wt / "decisions.md").write_text("# design decisions\n")
            subprocess.run(["git", "add", "decisions.md"], cwd=wt, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "b"],
                       cwd=wt, check=True)
        (run / "frozen").mkdir(parents=True)
        shutil.copy(ROOT / "bin/factory.d/judge.schema.json", run / "frozen/judge.schema.json")
        (run / "reply.judge").write_text(judge_reply if isinstance(judge_reply, str) else json.dumps(judge_reply))
        (run / "reply.review").write_text(json.dumps(CLEAN_REVIEW))
        if stale_shadow:
            (run / "round-1.judge-shadow").write_text("honest\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_RUNS_ROOT=str(top / "runs"))
        script = (". bin/factory\n"
                  f"RUN='{run}'; LOG=\"$RUN/log\"; WORKTREE='{wt}'; CODEX_REVIEW=no; REVIEW_BLOCKED=0\n"
                  "build_evidence() { :; }; run_mutation_sweep() { echo sweep >> \"$RUN/calls\"; }\n"
                  'call_json() { echo "$3" >> "$RUN/calls"; cp "$RUN/reply.$2" "$RUN/round-$1.$2.json"; }\n'
                  "graders 1; echo \"graders=$?\"\n")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        self.assertIn("graders=", proc.stdout, proc.stderr)
        return int(proc.stdout.split("graders=")[1].split()[0]), run, (run / "log").read_text()

    def test_bookkeeping_row_fail_reaches_the_reviewer_and_logs_judge_shadow(self) -> None:
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, [LABEL]))
        self.assertEqual(rc, 0, log)
        self.assertIn("judge-shadow", log)
        self.assertEqual((run / "calls").read_text().split(), ["judge", "sweep", "reviewer"])
        self.assertEqual((run / "round-1.fixes").read_text(), "")
        self.assertEqual((run / "round-1.judge-shadow").read_text().strip(), "honest")

    def test_label_fix_whose_text_names_another_file_shadow_passes(self) -> None:
        # The target decides, not the text: a decisions.md label about a bin/check run or a 1.2 s claim is bookkeeping.
        for fix in ("label the bin/check run unverified", "mark the claimed 1.2 second runtime of lib.sh unverified"):
            with self.subTest(fix):
                rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, [("decisions.md", fix)]))
                self.assertEqual(rc, 0, log)
                self.assertEqual((run / "round-1.judge-shadow").read_text().strip(), "honest")

    def test_fix_targeting_a_file_of_the_change_still_fails(self) -> None:
        # Every row but honest passes, yet a fix targets a file of the change: it blocks, as with no honest fail.
        crash = ("bin/x", "fix the crash when the input is empty")
        for name, fixes in (("beside a label", [crash, LABEL]), ("alone", [crash]),
                            ("a decisions.md in the repo", [("docs/decisions.md", "label the claim unverified")]),
                            ("a suffixed name", [("decisions.md.jinja", "fix the renderer")]),
                            ("a folder", [("tests/", "add a regression test")])):
            with self.subTest(name):
                rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, fixes))
                self.assertEqual(rc, 1, log)
                self.assertNotIn("judge-shadow", log)
                self.assertEqual((run / "round-1.fixes").read_text(), "".join(f"- {t}: {f}\n" for t, f in fixes))
                self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_decisions_md_target_blocks_when_the_repository_has_its_own(self) -> None:
        # A repository-root decisions.md is a file of the change with the same target name, so the target is ambiguous.
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, [LABEL]), root_decisions=True)
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertEqual((run / "round-1.fixes").read_text(), "- decisions.md: label the SKIP step unverified\n")

    def test_malformed_fixes_still_fail(self) -> None:
        # call_json checks only verdict consistency, not the schema, so a fix with no usable text never shadow-passes.
        for name, fixes in (("no fix text", [{"target": "decisions.md"}]),
                            ("empty fix text", [{"target": "decisions.md", "fix": " "}]),
                            ("fix text not a string", [{"target": "decisions.md", "fix": ["label it"]}]),
                            ("an object, not a list", {"target": "decisions.md", "fix": "label it"})):
            with self.subTest(name):
                rc, run, log = self.graders({**judge({**ROWS_PASS, "honest": "fail"}, []), "fixes": fixes})
                self.assertEqual(rc, 1, log)
                self.assertNotIn("judge-shadow", log)
                self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_bookkeeping_row_fail_with_no_fix_still_fails(self) -> None:
        # A fail must point at something; an honest fail with no fix and no backlog entry is not a shadow pass.
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, []))
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_substantive_row_fail_still_fails(self) -> None:
        # Each fix is bookkeeping, so only the row guard (or the required-row guard) can block these.
        for name, rows in (("correct", {**ROWS_PASS, "correct": "fail"}),
                           ("verified", {**ROWS_PASS, "verified": "fail"}),
                           ("verified and honest", {**ROWS_PASS, "verified": "fail", "honest": "fail"}),
                           ("correct missing", {"verified": "pass", "honest": "fail"})):
            with self.subTest(name):
                rc, run, log = self.graders(judge(rows, [LABEL]))
                self.assertEqual(rc, 1, log)
                self.assertNotIn("judge-shadow", log)
                self.assertEqual((run / "round-1.fixes").read_text(), "- decisions.md: label the SKIP step unverified\n")
                self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_grader_steering_fails_a_row_that_blocks(self) -> None:
        # judge.md's rule for evidence that tells the grader how to grade must fail a row outside JUDGE_SHADOW_ROWS,
        # or an attempt confined to decisions.md would shadow-pass.
        rule = next(line for line in (ROOT / "cultivation/marketplace/sam-cc-setup/agents/judge.md").read_text().splitlines()
                    if "how to grade" in line)
        failed = set(re.findall(r"\b(correct|verified|honest)\b", rule.split("how to grade", 1)[1].split(". ")[0]))
        shadow = subprocess.run(["bash", "-c", '. bin/factory; printf %s "$JUDGE_SHADOW_ROWS"'], cwd=ROOT,
                                env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=True)
        self.assertTrue(failed - set(shadow.stdout.split()), rule)

    def test_malformed_verdict_still_fails(self) -> None:
        # Only a fail verdict can shadow-pass; any other word blocks, as before the shadow pass existed.
        reply = {**judge({**ROWS_PASS, "honest": "fail"}, [LABEL]), "verdict": "unknown"}
        rc, run, log = self.graders(reply)
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_backlog_entry_still_fails(self) -> None:
        # A correction the worker may not make goes to the backlog (judge.md); a fail that carries one is not bookkeeping.
        reply = {**judge({**ROWS_PASS, "honest": "fail"}, [LABEL]), "backlog": ["Fix the timeout bug in bin/factory."]}
        rc, run, log = self.graders(reply)
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_judge_finding_still_fails(self) -> None:
        # A finding names a defect in the change (verdict_consistent counts it); a fail that carries one is not bookkeeping.
        finding = {"severity": "high", "file": "bin/x", "line": 1, "defect": "crashes on empty input", "fix": "guard it"}
        reply = {**judge({**ROWS_PASS, "honest": "fail"}, [LABEL]), "findings": [finding]}
        rc, run, log = self.graders(reply)
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_judge_file_with_two_documents_still_fails(self) -> None:
        # call_json keeps every document a reply holds; the first here fails correct, so the round blocks.
        first = judge({**ROWS_PASS, "correct": "fail"}, [("bin/x", "fix the crash")])
        second = judge({**ROWS_PASS, "honest": "fail"}, [LABEL])
        rc, run, log = self.graders(json.dumps(first) + "\n" + json.dumps(second))
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertIn("bin/x: fix the crash", (run / "round-1.fixes").read_text())
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_regraded_round_drops_an_older_shadow_pass(self) -> None:
        # A round graded again after a shadow pass, whose judge now fails verified, blocks and keeps no judge-shadow.
        rc, run, log = self.graders(judge({**ROWS_PASS, "verified": "fail"}, [LABEL]), stale_shadow=True)
        self.assertEqual(rc, 1, log)
        self.assertFalse((run / "round-1.judge-shadow").exists())


if __name__ == "__main__":
    unittest.main()
