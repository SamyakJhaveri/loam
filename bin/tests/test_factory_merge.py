"""bin/factory merge merges a PR only at the head whose checks passed (#405).

A `gh` program first on PATH logs its arguments and prints a fixed `gh pr view` reply. Each refusal must exit 1 with a
`merge: refused:` line and no `gh pr merge` call; the all-passed reply must call `gh pr merge <pr> -R <repo> --merge
--match-head-commit <sha>` and exit with that call's status. The target is a temporary repository with a GitHub
origin, through -C, so the -R value is known.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "FACTORY_FROZEN", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER",
             "REPO", "RUN", "LOG")
HEAD = "1" * 40
OK_RUN = {"__typename": "CheckRun", "name": "verify", "status": "COMPLETED", "conclusion": "SUCCESS"}
OK_STATUS = {"__typename": "StatusContext", "context": "ci", "state": "SUCCESS"}


class MergeTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        self.proj = top / "widget"
        self.proj.mkdir()
        for args in (["init", "-q"], ["remote", "add", "origin", "git@github.com:acme/widget.git"]):
            subprocess.run(["git", *args], cwd=self.proj, check=True, capture_output=True)
        self.log = top / "gh.log"
        self.view = top / "view.json"
        self.merge_rc = top / "merge-rc"
        (top / "bin").mkdir()
        gh = top / "bin" / "gh"
        gh.write_text("#!/usr/bin/env bash\n"
                      f"printf '%s\\n' \"$*\" >> '{self.log}'\n"
                      'case "$1 $2" in\n'
                      f"  'pr view') cat '{self.view}' ;;\n"
                      f"  'pr merge') exit \"$(cat '{self.merge_rc}' 2> /dev/null || echo 0)\" ;;\n"
                      "  *) exit 1 ;;\n"
                      "esac\n")
        gh.chmod(0o755)
        self.env = {**{k: v for k, v in os.environ.items() if k not in INHERITED},
                    "FACTORY_RUNS_ROOT": str(top / "runs"), "PATH": f"{top / 'bin'}:{os.environ['PATH']}"}

    def merge(self, reply: object, pr: str = "12", sha: str = HEAD) -> subprocess.CompletedProcess[str]:
        self.log.write_text("")
        self.view.write_text(reply if isinstance(reply, str) else json.dumps(reply))
        return subprocess.run([str(ROOT / "bin" / "factory"), "-C", str(self.proj), "merge", pr, sha],
                              cwd=ROOT, env=self.env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              check=False, timeout=60)

    def calls(self) -> list[str]:
        return self.log.read_text().splitlines()

    def assert_refused(self, proc: subprocess.CompletedProcess[str], why: str) -> None:
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("merge: refused:", proc.stderr)
        self.assertIn(why, proc.stderr)
        self.assertFalse([c for c in self.calls() if c.startswith("pr merge")], self.calls())

    def test_every_unchecked_reply_is_refused_without_a_merge(self) -> None:
        pending = {**OK_RUN, "name": "ci", "status": "IN_PROGRESS", "conclusion": ""}
        cases = {
            "another head": ({"headRefOid": "2" * 40, "statusCheckRollup": [OK_RUN]}, "not " + HEAD),
            "no checks": ({"headRefOid": HEAD, "statusCheckRollup": []}, "no check reported"),
            "null rollup": ({"headRefOid": HEAD, "statusCheckRollup": None}, "no check reported"),
            "pending run": ({"headRefOid": HEAD, "statusCheckRollup": [OK_RUN, pending]}, "ci IN_PROGRESS"),
            "skipped run": ({"headRefOid": HEAD, "statusCheckRollup": [{**OK_RUN, "conclusion": "SKIPPED"}]},
                            "verify COMPLETED/SKIPPED"),
            "failed status": ({"headRefOid": HEAD, "statusCheckRollup": [OK_RUN, {**OK_STATUS, "state": "FAILURE"}]},
                              "ci FAILURE"),
            "pending status": ({"headRefOid": HEAD, "statusCheckRollup": [{**OK_STATUS, "state": "PENDING"}]},
                               "ci PENDING"),
            "unknown entry": ({"headRefOid": HEAD, "statusCheckRollup": [OK_RUN, {"__typename": "Other"}]},
                              "Other entry"),
            "object rollup": ({"headRefOid": HEAD, "statusCheckRollup": {"verify": OK_RUN}}, "unreadable"),
            "number entry": ({"headRefOid": HEAD, "statusCheckRollup": [1]}, "unreadable"),
            "not JSON": ("warning: something\n", "printed no JSON"),
        }
        for name, (reply, why) in cases.items():
            with self.subTest(name):
                self.assert_refused(self.merge(reply), why)

    def test_a_failed_view_is_refused(self) -> None:
        self.view.unlink(missing_ok=True)
        self.log.write_text("")
        proc = subprocess.run([str(ROOT / "bin" / "factory"), "-C", str(self.proj), "merge", "12", HEAD],
                              cwd=ROOT, env=self.env, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              check=False, timeout=60)
        self.assert_refused(proc, "gh pr view 12 failed")

    def test_a_bad_pr_or_sha_is_refused_before_any_gh_call(self) -> None:
        # gh drops an empty --match-head-commit, so an empty sha against a reply with no head would merge unguarded.
        no_head = {"statusCheckRollup": [OK_RUN]}
        for pr, sha, why in (("12", "", "not a full lowercase commit sha"),
                             ("12", HEAD[:7], "not a full lowercase commit sha"),
                             ("12", "A" * 40, "not a full lowercase commit sha"),
                             ("https://github.com/other/repo/pull/12", HEAD, "not a PR number"),
                             ("factory/405", HEAD, "not a PR number")):
            with self.subTest(pr=pr, sha=sha):
                self.assert_refused(self.merge(no_head, pr, sha), why)
                self.assertEqual(self.calls(), [])

    def test_all_passed_merges_at_the_checked_head_and_keeps_the_merge_status(self) -> None:
        reply = {"headRefOid": HEAD, "statusCheckRollup": [OK_RUN, {**OK_RUN, "conclusion": "NEUTRAL"}, OK_STATUS]}
        proc = self.merge(reply)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.calls(), [
            "pr view 12 -R acme/widget --json headRefOid,statusCheckRollup",
            f"pr merge 12 -R acme/widget --merge --match-head-commit {HEAD}",
        ])
        self.merge_rc.write_text("7\n")
        self.assertEqual(self.merge(reply).returncode, 7)


if __name__ == "__main__":
    unittest.main()
