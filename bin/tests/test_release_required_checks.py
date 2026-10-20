"""bin/release.sh refuses to release unless main's rules require the `verify` and `stub-sweep` CI jobs.

release.sh runs as a program in a throwaway clone whose origin is a local bare repository. A fake `gh`
on PATH answers `gh api` with a canned rules response and `gh run list` with a non-success conclusion
(or GH_RUN_CONCLUSION), so a run that passes the ruleset gate stops at the next gate. A fake `git` logs
and fails every `git push`, so no network is used and nothing is pushed.
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

# The live response on 2026-10-18, after the owner's ruleset landed.
BOTH = [{"type": "required_status_checks",
         "parameters": {"strict_required_status_checks_policy": False, "do_not_enforce_on_create": False,
                        "required_status_checks": [{"context": "verify"}, {"context": "stub-sweep"}]},
         "ruleset_source_type": "Repository", "ruleset_source": "SamyakJhaveri/loam", "ruleset_id": 25374852}]

FAKE_GH = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
case "$1" in
  api)
    [ -n "${GH_API_FAIL:-}" ] && { echo "HTTP 404: Not Found" >&2; exit 1; }
    filter=.
    while [ $# -gt 0 ]; do [ "$1" = --jq ] && filter="$2"; shift; done
    jq -r "$filter" "$RULES_JSON" ;;
  run) echo "${GH_RUN_CONCLUSION:-stubbed}" ;;
  *) exit 1 ;;
esac
"""

FAKE_GIT = """#!/usr/bin/env bash
[ "$1" = push ] && { printf '%s\\n' "$*" >> "$PUSH_LOG"; exit 1; }
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
        self.work, origin, fake = top / "work", top / "origin.git", top / "fakebin"
        (self.work / "bin").mkdir(parents=True)
        fake.mkdir()
        for name in ("release.sh", "lib.sh", "ip-sweep.sh"):
            shutil.copy2(ROOT / "bin" / name, self.work / "bin" / name)
        git("init", "-q", "--bare", str(origin), cwd=top)
        git("init", "-q", "-b", "main", cwd=self.work)
        git("add", "bin", cwd=self.work)
        git("commit", "-qm", "base", cwd=self.work)
        git("remote", "add", "origin", str(origin), cwd=self.work)
        git("push", "-q", "origin", "main", cwd=self.work)
        for name, text in (("gh", FAKE_GH), ("git", FAKE_GIT)):
            (fake / name).write_text(text, encoding="utf-8")
            (fake / name).chmod(0o755)
        self.rules, self.gh_log, self.push_log = top / "rules.json", top / "gh.log", top / "push.log"
        # Drop inherited IP_* settings so a developer's real term file or sweep flags cannot leak in.
        base = {k: v for k, v in os.environ.items() if not k.startswith("IP_")}
        self.env = {**base, "PATH": f"{fake}:{os.environ['PATH']}", "REAL_GIT": shutil.which("git"),
                    "RULES_JSON": str(self.rules), "GH_LOG": str(self.gh_log), "PUSH_LOG": str(self.push_log)}

    def release(self, rules: list[dict], **env: str) -> subprocess.CompletedProcess[str]:
        self.rules.write_text(json.dumps(rules), encoding="utf-8")
        return subprocess.run(["bash", "bin/release.sh", "9.9.9"], cwd=self.work, env={**self.env, **env},
                              capture_output=True, text=True, check=False)

    def assert_refused(self, proc: subprocess.CompletedProcess[str], missing: str) -> None:
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(f"require the status check(s) {missing};", proc.stderr)
        self.assertNotIn(NEXT_GATE, proc.stderr)  # refused at the ruleset gate, not a later one
        self.assertIn(f"api {RULES_PATH}", self.gh_log.read_text())

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

    def test_resume_checks_the_rules_before_the_push(self) -> None:
        # A rerun after a failed push: HEAD is the release commit and its tag, origin/main is its parent.
        git("commit", "-q", "--allow-empty", "-m", "release: v9.9.9", cwd=self.work)
        git("tag", "-a", "v9.9.9", "-m", "Release v9.9.9", cwd=self.work)
        self.assert_refused(self.release([]), "verify, stub-sweep")
        self.assertFalse(self.push_log.exists())

        proc = self.release(BOTH)
        self.assertIn("resuming at the push", proc.stdout)
        self.assertIn("push --atomic origin", self.push_log.read_text())

    def test_release_runs_the_full_strict_sweep_whatever_the_caller_exports(self) -> None:
        (self.work / "notes.md").write_text("zz-planted-term\n", encoding="utf-8")
        git("add", "notes.md", cwd=self.work)
        git("commit", "-qm", "notes", cwd=self.work)
        git("push", "-q", "origin", "main", cwd=self.work)
        # Pass every earlier gate: a green Test run and a clean verify-loam run of HEAD.
        run = self.top / "verify" / "run"
        run.mkdir(parents=True)
        (run / "run.json").write_text(json.dumps({
            "commit": git("rev-parse", "HEAD", cwd=self.work), "dirty": False,
            "doctor": {"ok": True}, "check": {"ok": True, "pristine": True}}), encoding="utf-8")
        terms = self.top / "ip-terms"
        terms.write_text("zz-planted-term\n", encoding="utf-8")

        proc = self.release(BOTH, GH_RUN_CONCLUSION="success", LOAM_VERIFY_ROOT=str(self.top / "verify"),
                            IP_TERMS_FILE=str(terms), IP_SWEEP_IDENTITY_ONLY="1")

        self.assertIn("foreign-IP terms found in tracked files:\nnotes.md", proc.stdout)
        self.assertIn("ip-sweep failed", proc.stderr)
        self.assertFalse(self.push_log.exists())


if __name__ == "__main__":
    unittest.main()
