"""Behavior of bin/sync-project.

Builds a tiny Copier template (tag v1.0.0, then one untagged commit that edits a
line the project also edited), renders a project from v1.0.0 the way Loam v3.0.0
left it (_gh_setup.sh tracked), and keeps it in a bare repo that stands in for
GitHub. Stubs for `claude` and `gh` on PATH log every call; the claude stub
resolves conflict hunks by keeping the project's side.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SYNC = ROOT / "bin/sync-project"

# Same reason as test_render_smoke.py: keep git maintenance from racing cleanup.
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "gc.auto",
    "GIT_CONFIG_VALUE_0": "0",
    "GIT_CONFIG_KEY_1": "maintenance.auto",
    "GIT_CONFIG_VALUE_1": "false",
    "GIT_AUTHOR_NAME": "Sync Test",
    "GIT_AUTHOR_EMAIL": "sync@example.invalid",
    "GIT_COMMITTER_NAME": "Sync Test",
    "GIT_COMMITTER_EMAIL": "sync@example.invalid",
}

CLAUDE_STUB = r"""#!/usr/bin/env python3
import json, os, pathlib, re, sys
prompt = sys.stdin.read()
with open(os.environ["SYNC_STUB_LOG"], "a") as log:
    log.write(json.dumps({"argv": sys.argv[1:], "LOAM_MEMSTORE": os.environ.get("LOAM_MEMSTORE"),
                          "TMPDIR": os.environ.get("TMPDIR")}) + "\n")
m = re.search(r"is at `([^`]+)`", prompt)
if not m:
    print("VERIFY: PASS")
    sys.exit(0)
copy = pathlib.Path(m.group(1))
if os.environ.get("SYNC_STUB_MODE") != "leave":
    out, keep = [], True
    for line in copy.read_text().splitlines(keepends=True):
        if line.startswith("<<<<<<< "):
            keep = True
        elif line.rstrip("\n") == "=======":
            keep = False
        elif line.startswith(">>>>>>> "):
            keep = True
        elif keep:
            out.append(line)
    if os.environ.get("SYNC_STUB_MODE") == "badjson":
        out.append("not json\n")
    copy.write_text("".join(out))
print("Choices:\n- hunk 1: kept the project's line, because the stub always does")
"""

GH_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$SYNC_GH_LOG"
echo https://example.invalid/pull/1
"""


def run(cmd, cwd=None, env=None, check=True):
    return subprocess.run(cmd, cwd=cwd, env=env or GIT_ENV, capture_output=True, text=True,
                          timeout=180, check=check)


def git(*args, cwd):
    return run(["git", *args], cwd=cwd).stdout.strip()


def copier():
    for cmd in (["copier"], ["uvx", "copier"]):
        try:
            subprocess.run(cmd + ["--version"], capture_output=True, check=True)
            return cmd
        except (OSError, subprocess.CalledProcessError):
            continue
    raise unittest.SkipTest("copier not available")


class SyncProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.copier = copier()
        cls.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(cls.tmp.name)
        cls.task_log = base / "task.log"
        tpl = cls.tpl = base / "tpl"
        (tpl / "seed").mkdir(parents=True)
        (tpl / "copier.yml").write_text(
            '_subdirectory: seed\n'
            f'_tasks:\n  - "echo task ran in $PWD >> {cls.task_log}"\n'
            'project_name:\n  type: str\n  default: demo\n'
            'github_repo:\n  type: str\n  default: example/demo\n'
        )
        (tpl / "seed/.copier-answers.yml.jinja").write_text("{{ _copier_answers|to_nice_yaml -}}\n")
        (tpl / "seed/notes.md").write_text("line one\nshared line v1\nline three\n")
        (tpl / "seed/_gh_setup.sh").write_text("#!/bin/sh\necho v1\n")
        (tpl / "seed/conf.json").write_text('{"a": 1}\n')
        git("init", "-q", "-b", "main", cwd=tpl)
        git("add", "-A", cwd=tpl)
        git("commit", "-q", "-m", "v1", cwd=tpl)
        git("tag", "v1.0.0", cwd=tpl)

        proj = base / "proj"
        run(cls.copier + ["copy", "--trust", "--defaults", "--skip-tasks", "--vcs-ref", "v1.0.0",
                          str(tpl), str(proj)])
        answers = proj / ".copier-answers.yml"
        # A _src_path this machine cannot read, as in a project rendered on another machine.
        answers.write_text("\n".join(
            "_src_path: gh:example/loam" if line.startswith("_src_path:") else line
            for line in answers.read_text().splitlines()) + "\n")
        (proj / "notes.md").write_text("line one\nshared line (project)\nline three\n")
        (proj / "conf.json").write_text('{"a": 3}\n')
        (proj / "bin").mkdir()
        (proj / "bin/check").write_text("#!/usr/bin/env bash\necho 'check: PASSED'\n")
        (proj / "bin/check").chmod(0o755)
        skill = proj / ".claude/skills/verify-demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: verify-demo\ndescription: demo\n---\n")
        git("init", "-q", "-b", "main", cwd=proj)
        git("add", "-A", cwd=proj)  # tracks _gh_setup.sh, as Loam v3.0.0's first commit did
        git("commit", "-q", "-m", "init", cwd=proj)
        cls.pristine = base / "pristine.git"
        git("clone", "-q", "--bare", str(proj), str(cls.pristine), cwd=base)

        (tpl / "seed/notes.md").write_text("line one\nshared line v2\nline three\n")
        (tpl / "seed/_gh_setup.sh").write_text("#!/bin/sh\necho v2\n")
        (tpl / "seed/new.md").write_text("new in v2\n")
        (tpl / "seed/conf.json").write_text('{"a": 2}\n')
        git("add", "-A", cwd=tpl)
        git("commit", "-q", "-m", "v2", cwd=tpl)
        cls.sha = git("rev-parse", "HEAD", cwd=tpl)
        cls.branch = "loam-sync/" + cls.sha[:8]

        cls.stubs = base / "stubs"
        cls.stubs.mkdir()
        for name, body in (("claude", CLAUDE_STUB), ("gh", GH_STUB)):
            (cls.stubs / name).write_text(body)
            (cls.stubs / name).chmod(0o755)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.task_log.unlink(missing_ok=True)
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.base = pathlib.Path(t.name)
        self.remote = self.base / "remote.git"
        git("clone", "-q", "--bare", str(self.pristine), str(self.remote), cwd=self.base)
        self.work = self.base / "work"
        self.claude_log = self.base / "claude.log"
        self.gh_log = self.base / "gh.log"

    def sync(self, *flags: str, project: str | None = None, mode: str = "") -> subprocess.CompletedProcess:
        env = {**GIT_ENV, "PATH": f"{self.stubs}:{os.environ['PATH']}", "TMPDIR": str(self.base),
               "SYNC_STUB_LOG": str(self.claude_log), "SYNC_GH_LOG": str(self.gh_log),
               "SYNC_STUB_MODE": mode}
        return run(["bash", str(SYNC), "--loam", str(self.tpl), "--work", str(self.work), *flags,
                    project or str(self.remote), self.sha], env=env, check=False)

    def claude_calls(self) -> list[dict]:
        if not self.claude_log.exists():
            return []
        return [json.loads(line) for line in self.claude_log.read_text().splitlines()]

    def remote_branches(self) -> str:
        return git("branch", "--list", "loam-sync/*", cwd=self.remote)

    def show(self, rev: str, path: str) -> str:
        return git("show", f"{rev}:{path}", cwd=self.remote)

    def test_opens_a_pr_with_copier_and_port_commits(self) -> None:
        r = self.sync("--draft")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        subjects = git("log", "--format=%s", f"main..{self.branch}", cwd=self.remote).splitlines()
        self.assertEqual(2, len(subjects), subjects)
        copier_commit, port_commit = f"{self.branch}~1", self.branch
        self.assertIn("<<<<<<< before updating", self.show(copier_commit, "notes.md"))
        self.assertEqual("line one\nshared line (project)\nline three", self.show(port_commit, "notes.md"))
        self.assertEqual("new in v2", self.show(copier_commit, "new.md"))
        answers = self.show(port_commit, ".copier-answers.yml")
        self.assertIn("_src_path: gh:example/loam", answers)
        self.assertIn(f"_commit: v1.0.0-1-g{self.sha[:7]}", answers)
        tree = git("ls-tree", "-r", "--name-only", copier_commit, cwd=self.remote).splitlines()
        self.assertNotIn("_gh_setup.sh", tree)
        self.assertFalse(self.task_log.exists(), "a copier task ran during the sync")
        self.assertEqual('{"a": 3}', self.show(port_commit, "conf.json"))
        calls = self.claude_calls()
        self.assertEqual(3, len(calls), calls)  # one per conflicted file, then the verify skill
        for call in calls:
            self.assertIn("claude-opus-5-5", call["argv"])
            self.assertTrue(call["LOAM_MEMSTORE"].startswith(str(self.work)), call)
            self.assertTrue(call["TMPDIR"].startswith(str(self.work)), call)
        gh = self.gh_log.read_text()
        self.assertIn("pr create", gh)
        self.assertIn("--draft", gh)
        self.assertIn("--repo example/demo", gh)
        body = (self.work / "pr-body.md").read_text()
        for needle in ("notes.md", "kept the project's line", "check: PASSED", "VERIFY: PASS", self.sha):
            self.assertIn(needle, body)

    def test_dry_run_stops_before_the_push(self) -> None:
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual("", self.remote_branches())
        self.assertFalse(self.gh_log.exists())
        self.assertTrue((self.work / "pr-body.md").is_file())

    def test_no_port_refuses_on_a_conflict(self) -> None:
        r = self.sync("--no-port")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("conflict markers remain in conf.json notes.md", r.stderr)
        self.assertEqual([], self.claude_calls())
        self.assertEqual("", self.remote_branches())

    def test_refuses_when_the_port_leaves_markers(self) -> None:
        r = self.sync(mode="leave")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("conflict markers remain in conf.json notes.md", r.stderr)
        self.assertEqual("", self.remote_branches())
        self.assertFalse(self.gh_log.exists())

    def test_refuses_when_the_port_breaks_json(self) -> None:
        r = self.sync(mode="badjson")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("invalid JSON in conf.json", r.stderr)
        self.assertEqual("", self.remote_branches())

    def test_refuses_to_push_into_a_working_checkout(self) -> None:
        checkout = self.base / "checkout"
        git("clone", "-q", str(self.remote), str(checkout), cwd=self.base)
        r = self.sync(project=str(checkout))
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("working checkout", r.stderr)
        self.assertEqual("", git("branch", "--list", "loam-sync/*", cwd=checkout))

    def test_control_a_plain_update_runs_the_task(self) -> None:
        # The task-log assertion above is only meaningful if a task that runs leaves a log.
        clone = self.base / "plain"
        git("clone", "-q", str(self.remote), str(clone), cwd=self.base)
        answers = clone / ".copier-answers.yml"
        answers.write_text(answers.read_text().replace("gh:example/loam", str(self.tpl)))
        git("commit", "-q", "-am", "local src", cwd=clone)
        run(self.copier + ["update", "--trust", "--defaults", "--vcs-ref", self.sha], cwd=clone)
        self.assertTrue(self.task_log.exists())


if __name__ == "__main__":
    unittest.main()
