"""bin/release.sh tags the merge commit of the merged `release/X.Y.Z` PR and pushes only the tag.

release.sh runs as a program in a throwaway clone whose origin is a local bare repository. The clone's
`release/9.9.9` branch bumps VERSION from 9.9.8 and is merged into main with `--no-ff`; main then moves
one commit past the merge and is pushed, and release.sh runs with HEAD detached at the merge commit, as
the owner runs it. A fake `gh` on PATH answers `gh api` with a canned rules response, `gh pr list` from
a canned PR list, and `gh run list` with a non-success conclusion (or GH_RUN_CONCLUSION), so a run that
passes the earlier gates stops at the Test run gate. A fake `git` logs every `git push` and fails it while
the PUSH_FAIL file exists, and fake `copier` and `uvx` exit 0, so nothing reaches GitHub or renders.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RULES_PATH = "repos/{owner}/{repo}/rules/branches/main"
NEXT_GATE = "latest Test run on HEAD is 'stubbed'"
TAG = "refs/tags/v9.9.9"

# The live response on 2026-10-18, after the owner's ruleset landed.
BOTH = [{"type": "required_status_checks",
         "parameters": {"strict_required_status_checks_policy": False, "do_not_enforce_on_create": False,
                        "required_status_checks": [{"context": "verify"}, {"context": "stub-sweep"}]},
         "ruleset_source_type": "Repository", "ruleset_source": "SamyakJhaveri/loam", "ruleset_id": 25374852}]

FAKE_GH = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
filter=. state= head= prev=
for a in "$@"; do
  case "$prev" in --jq) filter=$a ;; --state) state=$a ;; --head) head=$a ;; esac
  prev=$a
done
case "$1" in
  api)
    [ -n "${GH_API_FAIL:-}" ] && { echo "HTTP 404: Not Found" >&2; exit 1; }
    jq -r "$filter" "$RULES_JSON" ;;
  pr)
    [ "$2" = list ] || exit 1
    jq --arg st "$state" --arg head "$head" \\
      'map(select(.headRefName == $head and ($st != "merged" or .state == "MERGED")))' "$PRS_JSON" \\
      | jq -r "$filter" ;;
  run) echo "${GH_RUN_CONCLUSION:-stubbed}" ;;
  *) exit 1 ;;
esac
"""

FAKE_GIT = """#!/usr/bin/env bash
if [ "$1" = push ]; then
  printf '%s\\n' "$*" >> "$PUSH_LOG"
  [ -e "$PUSH_FAIL" ] && exit 1
fi
exec "$REAL_GIT" "$@"
"""


def git(*args: str, cwd: pathlib.Path) -> str:
    # A noreply identity, so the release's identity sweep passes on the fixture's commits.
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@users.noreply.github.com", *args],
                          cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class ReleaseRequiredChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = top = pathlib.Path(tmp.name)
        fake = top / "fakebin"
        fake.mkdir()
        for name, text in (("gh", FAKE_GH), ("git", FAKE_GIT), ("copier", "#!/bin/sh\nexit 0\n"),
                           ("uvx", "#!/bin/sh\nexit 0\n")):
            (fake / name).write_text(text, encoding="utf-8")
            (fake / name).chmod(0o755)
        self.rules, self.prs, self.gh_log = top / "rules.json", top / "prs.json", top / "gh.log"
        self.push_log, self.push_fail = top / "push.log", top / "push.fail"
        # Drop inherited IP_* settings so a developer's real term file or sweep flags cannot leak in.
        base = {k: v for k, v in os.environ.items() if not k.startswith("IP_")}
        self.env = {**base, "PATH": f"{fake}:{os.environ['PATH']}", "REAL_GIT": shutil.which("git"),
                    "RULES_JSON": str(self.rules), "PRS_JSON": str(self.prs), "GH_LOG": str(self.gh_log),
                    "PUSH_LOG": str(self.push_log), "PUSH_FAIL": str(self.push_fail)}
        self.make_repo("9.9.9")

    def make_repo(self, bump: str, extra: dict[str, str] | None = None) -> None:
        """A clone whose release/9.9.9 branch sets VERSION to `bump` and is merged; main is one commit past it."""
        repo = self.top / f"repo-{bump}-{len(list(self.top.glob('repo-*')))}"
        self.work, self.origin = repo / "work", repo / "origin.git"
        (self.work / "bin").mkdir(parents=True)
        for name in ("release.sh", "lib.sh", "ip-sweep.sh"):
            shutil.copy2(ROOT / "bin" / name, self.work / "bin" / name)
        (self.work / "VERSION").write_text("9.9.8\n", encoding="utf-8")
        git("init", "-q", "--bare", str(self.origin), cwd=repo)
        git("init", "-q", "-b", "main", cwd=self.work)
        git("add", "-A", cwd=self.work)
        git("commit", "-qm", "base", cwd=self.work)
        git("remote", "add", "origin", str(self.origin), cwd=self.work)
        git("switch", "-qc", "release/9.9.9", cwd=self.work)
        (self.work / "VERSION").write_text(f"{bump}\n", encoding="utf-8")
        for name, text in (extra or {}).items():
            (self.work / name).write_text(text, encoding="utf-8")
        git("add", "-A", cwd=self.work)
        git("commit", "-qm", "bump", cwd=self.work)
        git("switch", "-q", "main", cwd=self.work)
        git("merge", "-q", "--no-ff", "-m", "Merge pull request #1 from t/release/9.9.9", "release/9.9.9",
            cwd=self.work)
        self.merge = git("rev-parse", "HEAD", cwd=self.work)
        git("commit", "-q", "--allow-empty", "-m", "later", cwd=self.work)
        git("push", "-q", "origin", "main", cwd=self.work)
        self.later = git("rev-parse", "HEAD", cwd=self.work)
        git("switch", "-q", "--detach", self.merge, cwd=self.work)
        self.set_prs([{"number": 1, "headRefName": "release/9.9.9", "state": "MERGED",
                       "mergeCommit": {"oid": self.merge}}])

    def set_prs(self, prs: list[dict]) -> None:
        self.prs.write_text(json.dumps(prs), encoding="utf-8")

    def green(self) -> dict[str, str]:
        """The env that passes the gates after the PR's: a green Test run, a clean verify-loam run, a clean IP sweep."""
        run = self.top / "verify" / self.merge[:8]
        run.mkdir(parents=True, exist_ok=True)
        (run / "run.json").write_text(json.dumps({
            "commit": self.merge, "dirty": False,
            "doctor": {"ok": True}, "check": {"ok": True, "pristine": True}}), encoding="utf-8")
        terms = self.top / "ip-terms"
        terms.write_text("zz-no-such-term-q7\n", encoding="utf-8")
        return {"GH_RUN_CONCLUSION": "success", "LOAM_VERIFY_ROOT": str(self.top / "verify"),
                "IP_TERMS_FILE": str(terms)}

    def release(self, rules: list[dict], **env: str) -> subprocess.CompletedProcess[str]:
        self.rules.write_text(json.dumps(rules), encoding="utf-8")
        return subprocess.run(["bash", "bin/release.sh", "9.9.9"], cwd=self.work, env={**self.env, **env},
                              capture_output=True, text=True, check=False)

    def tags(self, repo: pathlib.Path) -> list[str]:
        return git("for-each-ref", "--format=%(refname)", "refs/tags", cwd=repo).split()

    def pushes(self) -> list[str]:
        return self.push_log.read_text().splitlines() if self.push_log.exists() else []

    def assert_refused(self, proc: subprocess.CompletedProcess[str], missing: str) -> None:
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(f"require the status check(s) {missing};", proc.stderr)
        self.assertNotIn(NEXT_GATE, proc.stderr)  # refused at the ruleset gate, not a later one
        self.assertIn(f"api {RULES_PATH}", self.gh_log.read_text())

    def assert_nothing_released(self, proc: subprocess.CompletedProcess[str]) -> None:
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(self.tags(self.work), [])
        self.assertEqual(self.tags(self.origin), [])
        self.assertEqual(self.pushes(), [])
        self.assertEqual(git("rev-parse", "main", cwd=self.origin), self.later)

    def test_both_contexts_required_passes_the_gate(self) -> None:
        proc = self.release(BOTH)
        self.assertIn(NEXT_GATE, proc.stderr)
        self.assertNotIn("require the status check(s)", proc.stderr)

    def test_one_context_missing_refuses(self) -> None:
        only_verify = json.loads(json.dumps(BOTH))
        only_verify[0]["parameters"]["required_status_checks"] = [{"context": "verify"}]
        self.assert_refused(self.release(only_verify), "stub-sweep")

    def test_no_rules_refuses(self) -> None:
        self.assert_refused(self.release([]), "verify, stub-sweep")

    def test_unreadable_rules_refuses(self) -> None:
        proc = self.release(BOTH, GH_API_FAIL="1")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("cannot read the rules on main", proc.stderr)
        self.assertNotIn(NEXT_GATE, proc.stderr)

    def test_full_release_tags_the_merge_commit_and_pushes_only_the_tag(self) -> None:
        proc = self.release(BOTH, **self.green())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("released v9.9.9", proc.stdout)
        self.assertEqual(git("rev-parse", f"{TAG}^{{commit}}", cwd=self.origin), self.merge)
        self.assertEqual(git("cat-file", "-t", TAG, cwd=self.origin), "tag")
        self.assertEqual(self.tags(self.origin), [TAG])
        # No commit of its own, and main untouched on origin and locally.
        self.assertEqual(git("rev-parse", "main", cwd=self.origin), self.later)
        self.assertEqual(git("rev-parse", "main", cwd=self.work), self.later)
        self.assertEqual(git("rev-parse", "HEAD", cwd=self.work), self.merge)
        self.assertEqual(self.pushes(), [f"push origin {TAG}"])

    def test_closed_earlier_attempt_is_passed_over(self) -> None:
        self.set_prs([{"number": 2, "headRefName": "release/9.9.9", "state": "CLOSED", "mergeCommit": None},
                      {"number": 1, "headRefName": "release/9.9.9", "state": "MERGED",
                       "mergeCommit": {"oid": self.merge}}])
        self.assertIn(NEXT_GATE, self.release(BOTH).stderr)

    def test_unmerged_pr_refuses(self) -> None:
        self.set_prs([{"number": 1, "headRefName": "release/9.9.9", "state": "OPEN", "mergeCommit": None}])
        proc = self.release(BOTH, **self.green())
        self.assertIn("release/9.9.9", proc.stderr)
        self.assert_nothing_released(proc)

    def test_head_past_the_merge_commit_refuses(self) -> None:
        git("switch", "-q", "main", cwd=self.work)
        proc = self.release(BOTH, **self.green())
        self.assertIn(self.merge, proc.stderr)
        self.assertIn(f"git checkout --detach {self.merge}", proc.stderr)
        self.assert_nothing_released(proc)

    def test_merged_pr_with_another_version_refuses(self) -> None:
        self.make_repo("9.9.7")
        proc = self.release(BOTH, **self.green())
        self.assertIn("VERSION", proc.stderr)
        self.assertIn("'9.9.7', not 9.9.9", proc.stderr)
        self.assert_nothing_released(proc)

    def test_resume_after_a_failed_tag_push_pushes_only_the_tag(self) -> None:
        green = self.green()
        self.push_fail.touch()
        proc = self.release(BOTH, **green)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("tag push failed", proc.stderr)
        self.assertEqual(git("rev-parse", f"{TAG}^{{commit}}", cwd=self.work), self.merge)
        self.assertEqual(self.tags(self.origin), [])
        self.push_fail.unlink()
        self.push_log.unlink()

        # The rerun checks the rules again before the push.
        self.assert_refused(self.release([], **green), "verify, stub-sweep")
        self.assertEqual(self.pushes(), [])

        proc = self.release(BOTH, **green)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("resuming at the push", proc.stdout)
        self.assertEqual(self.pushes(), [f"push origin {TAG}"])
        self.assertEqual(git("rev-parse", f"{TAG}^{{commit}}", cwd=self.origin), self.merge)
        self.assertEqual(git("rev-parse", "main", cwd=self.origin), self.later)

        # Once origin has the tag it is public: a further run refuses.
        proc = self.release(BOTH, **green)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("already on origin", proc.stderr)

    def test_release_runs_the_full_strict_sweep_whatever_the_caller_exports(self) -> None:
        self.make_repo("9.9.9", {"notes.md": "zz-planted-term\n"})
        terms = self.top / "ip-terms-planted"
        terms.write_text("zz-planted-term\n", encoding="utf-8")

        proc = self.release(BOTH, **{**self.green(), "IP_TERMS_FILE": str(terms), "IP_SWEEP_IDENTITY_ONLY": "1"})

        self.assertIn("foreign-IP terms found in tracked files:\nnotes.md", proc.stdout)
        self.assertIn("ip-sweep failed", proc.stderr)
        self.assert_nothing_released(proc)


if __name__ == "__main__":
    unittest.main()
