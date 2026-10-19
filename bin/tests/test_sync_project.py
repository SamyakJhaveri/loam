"""Behavior of bin/sync-project.

Builds a tiny Copier template (tag v1.0.0, then one untagged commit that edits a
line the project also edited and a file the project left alone), renders a project from v1.0.0 the way Loam v3.0.0
left it (_gh_setup.sh tracked), and keeps it in a bare repo that stands in for
GitHub. Stubs for `claude` and `gh` on PATH log every call; the claude stub
resolves the conflict hunks in every copy a prompt names by keeping the project's side.
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
import json, os, pathlib, re, subprocess, sys
prompt = sys.stdin.read()
with open(os.environ["SYNC_STUB_LOG"], "a") as log:
    log.write(json.dumps({"argv": sys.argv[1:], "LOAM_MEMSTORE": os.environ.get("LOAM_MEMSTORE"),
                          "LOAM_MEMSTORE_REMOTE": os.environ.get("LOAM_MEMSTORE_REMOTE"),
                          "TMPDIR": os.environ.get("TMPDIR"), "prompt": prompt}) + "\n")
files = re.findall(r"`([^`\n]+)`[^`\n]* is at `([^`\n]+)`", prompt)
if not files:
    if os.environ.get("SYNC_STUB_MODE") == "commit":
        pathlib.Path("stray.txt").write_text("stray\n")
        subprocess.run(["git", "add", "stray.txt"], check=True)
        subprocess.run(["git", "commit", "-q", "-m", "stray commit by the verify agent"], check=True)
    elif os.environ.get("SYNC_STUB_MODE") == "edit":
        with open("notes.md", "a") as f:
            f.write("stray edit by the verify agent\n")
    print("VERIFY: PASS")
    sys.exit(0)
print("Choices:")
for path, copy in files:
    copy = pathlib.Path(copy)
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
        elif os.environ.get("SYNC_STUB_MODE") == "base":
            out.append("||||||| last update\n")
        copy.write_text("".join(out))
    print(f"### {path}\n- hunk 1: kept the project's line in {path}, because the stub always does")
if os.environ.get("SYNC_STUB_MODE") == "redirect":  # point any path record it can reach outside the clone
    for meta in pathlib.Path(sys.argv[sys.argv.index("--add-dir") + 1]).glob("**/path"):
        meta.write_text(os.path.join(os.environ["SYNC_STUB_OUTSIDE"], os.path.basename(meta.read_text().strip())) + "\n")
print("Notes:\n- the stub read no other file\n- for the reviewer:\n  - a nested note")
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
        (tpl / "seed/plain.md").write_text("plain v1\n")
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
        (tpl / "seed/plain.md").write_text("plain v2\n")
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

    def sync(self, *flags: str, project: str | None = None, mode: str = "",
             loam: pathlib.Path | None = None, sha: str | None = None,
             env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        # The project is named on GitHub, as a real sync needs; git's insteadOf points both names
        # at the local bare repo. github_repo in the answers is example/demo.
        env = {**GIT_ENV, "PATH": f"{self.stubs}:{os.environ['PATH']}", "TMPDIR": str(self.base),
               "GIT_CONFIG_COUNT": "4",
               "GIT_CONFIG_KEY_2": f"url.{self.remote}.insteadOf",
               "GIT_CONFIG_VALUE_2": "https://github.com/example/demo.git",
               "GIT_CONFIG_KEY_3": f"url.{self.remote}.insteadOf",
               "GIT_CONFIG_VALUE_3": "https://github.com/example/renamed.git",
               "SYNC_STUB_LOG": str(self.claude_log), "SYNC_GH_LOG": str(self.gh_log),
               "SYNC_STUB_MODE": mode, **(env or {})}
        return run(["bash", str(SYNC), "--loam", str(loam or self.tpl), "--work", str(self.work), *flags,
                    project or "example/demo", sha or self.sha], env=env, check=False)

    def fixture(self, name: str, v1: dict[str, str], edits: dict[str, str], v2: dict[str, str],
                *data: str) -> tuple[pathlib.Path, pathlib.Path, str]:
        """Return a template with tag v1.0.0 holding the files v1 and a later commit holding v2,
        a bare repo of a project rendered from v1.0.0 with the `data` answers and the `edits`,
        and the template's later commit."""
        tpl, proj, remote = (self.base / f"{name}-{p}" for p in ("tpl", "proj", "remote.git"))

        def write(root: pathlib.Path, files: dict[str, str]) -> None:
            for path, text in files.items():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text(text)

        write(tpl, {"copier.yml": "_subdirectory: seed\nproject_kind:\n  type: str\n  default: python\n",
                    "seed/.copier-answers.yml.jinja": "{{ _copier_answers|to_nice_yaml -}}\n",
                    **{f"seed/{p}": t for p, t in v1.items()}})
        git("init", "-q", "-b", "main", cwd=tpl)
        git("add", "-A", cwd=tpl)
        git("commit", "-q", "-m", "v1", cwd=tpl)
        git("tag", "v1.0.0", cwd=tpl)
        run(self.copier + ["copy", "--trust", "--defaults", "--vcs-ref", "v1.0.0", *data, str(tpl), str(proj)])
        write(proj, edits)
        git("init", "-q", "-b", "main", cwd=proj)
        git("add", "-A", cwd=proj)
        git("commit", "-q", "-m", "init", cwd=proj)
        git("clone", "-q", "--bare", str(proj), str(remote), cwd=self.base)
        write(tpl, {f"seed/{p}": t for p, t in v2.items()})
        git("add", "-A", cwd=tpl)
        git("commit", "-q", "-m", "v2", cwd=tpl)
        return tpl, remote, git("rev-parse", "HEAD", cwd=tpl)

    def claude_calls(self) -> list[dict]:
        if not self.claude_log.exists():
            return []
        return [json.loads(line) for line in self.claude_log.read_text().splitlines()]

    def remote_branches(self) -> str:
        return git("branch", "--list", "loam-sync/*", cwd=self.remote)

    def show(self, rev: str, path: str) -> str:
        return git("show", f"{rev}:{path}", cwd=self.remote)

    def test_opens_a_pr_with_copier_and_port_commits(self) -> None:
        r = self.sync("--draft", env={"LOAM_MEMSTORE_REMOTE": str(self.base / "shared-memstore.git")})
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        subjects = git("log", "--format=%s", f"main..{self.branch}", cwd=self.remote).splitlines()
        self.assertEqual(2, len(subjects), subjects)
        copier_commit, port_commit = f"{self.branch}~1", self.branch
        self.assertIn("<<<<<<< before updating", self.show(copier_commit, "notes.md"))
        self.assertEqual("line one\nshared line (project)\nline three", self.show(port_commit, "notes.md"))
        self.assertEqual("new in v2", self.show(copier_commit, "new.md"))
        self.assertEqual("plain v2", self.show(copier_commit, "plain.md"))
        answers = self.show(port_commit, ".copier-answers.yml")
        self.assertIn("_src_path: gh:example/loam", answers)
        self.assertIn(f"_commit: v1.0.0-1-g{self.sha[:7]}", answers)
        tree = git("ls-tree", "-r", "--name-only", copier_commit, cwd=self.remote).splitlines()
        self.assertNotIn("_gh_setup.sh", tree)
        self.assertFalse(self.task_log.exists(), "a copier task ran during the sync")
        self.assertEqual('{"a": 3}', self.show(port_commit, "conf.json"))
        calls = self.claude_calls()
        self.assertEqual(2, len(calls), calls)  # one over both conflicted files, then the verify skill
        for call in calls:
            self.assertIn("claude-opus-5-5", call["argv"])
            self.assertTrue(call["LOAM_MEMSTORE"].startswith(str(self.work)), call)
            self.assertIsNone(call["LOAM_MEMSTORE_REMOTE"], call)  # the scratch store must not push
            self.assertTrue(call["TMPDIR"].startswith(str(self.work)), call)
        gh = self.gh_log.read_text()
        self.assertIn("pr create", gh)
        self.assertIn("--draft", gh)
        self.assertIn("--repo example/demo", gh)
        body = (self.work / "pr-body.md").read_text()
        for needle in ("- `conf.json`\n  - hunk 1: kept the project's line in conf.json,",
                       "- `notes.md`\n  - hunk 1: kept the project's line in notes.md,",
                       "- the stub read no other file",
                       "- for the reviewer:\n  - a nested note", "check: PASSED", "VERIFY: PASS", self.sha):
            self.assertIn(needle, body)
        message = git("log", "-1", "--format=%B", port_commit, cwd=self.remote)
        self.assertIn("notes.md\n- hunk 1: kept the project's line in notes.md,", message)

    def test_opens_the_pr_in_the_repo_it_pushed_to(self) -> None:
        # A renamed or forked project: github_repo in the answers still says example/demo.
        r = self.sync(project="example/renamed")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(self.branch, self.remote_branches())
        gh = self.gh_log.read_text()
        self.assertIn("--repo example/renamed", gh)
        self.assertNotIn("example/demo", gh)

    def test_refuses_a_project_with_no_github_repo_before_any_model_call(self) -> None:
        r = self.sync(project=str(self.remote))
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("no GitHub repo", r.stderr)
        self.assertEqual([], self.claude_calls())
        self.assertFalse((self.work / "project").exists())
        self.assertEqual("", self.remote_branches())
        self.assertFalse(self.gh_log.exists())

    def test_a_conflicted_file_may_share_a_name_with_the_port_bookkeeping(self) -> None:
        # Each conflicted file's port dir also holds path, old, new and template.diff.
        names = ("a/path", "b/old", "c/new", "d/template.diff")
        tpl, remote, sha = self.fixture("names", dict.fromkeys(names, "v1\n"), dict.fromkeys(names, "project\n"),
                                        dict.fromkeys(names, "v2\n"))
        r = self.sync("--dry-run", project=str(remote), loam=tpl, sha=sha)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        for name in names:
            self.assertEqual("project\n", (self.work / "project" / name).read_text(), name)
        self.assertEqual(4, self.claude_calls()[0]["prompt"].count("\n-v1\n+v2\n"))

    def test_the_port_cannot_redirect_the_copy_back(self) -> None:
        # The model can edit anything under the port dir it is given.
        outside = self.base / "outside"
        outside.mkdir()
        r = self.sync("--dry-run", mode="redirect", env={"SYNC_STUB_OUTSIDE": str(outside)})
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([], list(outside.iterdir()))
        self.assertEqual('{"a": 3}', git("show", "HEAD:conf.json", cwd=self.work / "project"))

    def test_the_pr_body_names_the_rulings_when_nothing_conflicts(self) -> None:
        tpl, remote, sha = self.fixture("clean", {"a.md": "v1\n"}, {}, {"a.md": "v2\n"})
        trial = self.base / "trial-rulings.md"
        trial.write_text("- a.md: keep ours.\n")
        blob = run(["git", "hash-object", str(trial)]).stdout.strip()
        r = self.sync("--dry-run", "--rulings", str(trial), project=str(remote), loam=tpl, sha=sha)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([], self.claude_calls())
        body = (self.work / "pr-body.md").read_text()
        self.assertTrue(any(str(trial) in line and blob in line for line in body.splitlines()), body)

    def test_a_typescript_project_keeps_the_pyright_strip_without_a_conflict(self) -> None:
        # copier.yml task 1 strips the pyright-lsp plugin for a non-Python kind in all three
        # renders. With tasks skipped, the strip in the project conflicts with the template's new
        # key beside it, and the template's side of that hunk re-adds the plugin.
        def dump(d: dict) -> str:
            return json.dumps(d, indent=2) + "\n"

        plugin = {"pyright-lsp@claude-plugins-official": True}
        v1 = {"enabledPlugins": plugin, "permissions": {"deny": ["Bash(rm -rf:*)"]}}
        v2 = {"enabledPlugins": plugin, "cleanupPeriodDays": 365, "permissions": {"deny": ["Bash(rm -rf:*)"]}}
        path = ".claude/settings.json"
        tpl, remote, sha = self.fixture("ts", {path: dump(v1)}, {path: dump({**v1, "enabledPlugins": {}})},
                                        {path: dump(v2)}, "-d", "project_kind=typescript")
        r = self.sync("--dry-run", project=str(remote), loam=tpl, sha=sha)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([], self.claude_calls())  # nothing left for the port
        self.assertEqual(dump({**v2, "enabledPlugins": {}}), (self.work / "project" / path).read_text())

    def commit_rulings(self, text: str) -> str:
        clone = self.base / "rulings-clone"
        git("clone", "-q", str(self.remote), str(clone), cwd=self.base)
        (clone / ".loam").mkdir()
        (clone / ".loam/sync-rulings.md").write_text(text)
        git("add", "-A", cwd=clone)
        git("commit", "-q", "-m", "rulings", cwd=clone)
        git("push", "-q", "origin", "main", cwd=clone)
        return git("rev-parse", "main:.loam/sync-rulings.md", cwd=self.remote)

    def test_tracked_rulings_reach_the_port_prompt(self) -> None:
        blob = self.commit_rulings("- conf.json: the tracked ruling.\n")
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        prompt = self.claude_calls()[0]["prompt"]
        self.assertIn("- conf.json: the tracked ruling.", prompt)
        self.assertIn("Follow every ruling; if a ruling does not cover a hunk, use the brief.", prompt)
        body = (self.work / "pr-body.md").read_text()
        self.assertTrue(any(".loam/sync-rulings.md" in line and blob in line for line in body.splitlines()), body)

    def test_rulings_flag_overrides_the_tracked_file(self) -> None:
        self.commit_rulings("- conf.json: the tracked ruling.\n")
        trial = self.base / "trial-rulings.md"
        trial.write_text("- notes.md: the trial ruling.\n")
        blob = run(["git", "hash-object", str(trial)]).stdout.strip()
        r = self.sync("--dry-run", "--rulings", str(trial))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        prompt = self.claude_calls()[0]["prompt"]
        self.assertIn("- notes.md: the trial ruling.", prompt)
        self.assertNotIn("the tracked ruling", prompt)
        body = (self.work / "pr-body.md").read_text()
        self.assertTrue(any(str(trial) in line and blob in line for line in body.splitlines()), body)

    def test_copier_flags_in_the_rulings_keep_paths_out_of_the_update(self) -> None:
        # The first test is the control: without flags notes.md conflicts, plain.md takes v2,
        # and new.md renders.
        self.commit_rulings("# Rulings\n\n- notes.md: keep ours.\n\n## Copier flags\n\n```text\n"
                            "--skip /notes.md\n--skip /plain.md\n\n--exclude /new.md\n```\n")
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        project = self.work / "project"
        self.assertEqual("line one\nshared line (project)\nline three", git("show", "HEAD~1:notes.md", cwd=project))
        self.assertEqual("plain v1", git("show", "HEAD~1:plain.md", cwd=project))
        self.assertNotIn("new.md", git("ls-tree", "-r", "--name-only", "HEAD", cwd=project).splitlines())
        prompt = self.claude_calls()[0]["prompt"]
        self.assertIn("`conf.json` is at", prompt)
        self.assertNotIn("`notes.md` is at", prompt)
        self.assertIn("passed the lines under `## Copier flags` to Copier", prompt)
        flags = "--skip /notes.md --skip /plain.md --exclude /new.md"
        self.assertIn(flags, (self.work / "pr-body.md").read_text())
        self.assertIn(flags, git("log", "-1", "--format=%B", "HEAD~1", cwd=project))

    def test_refuses_a_bad_copier_flag_line_before_any_model_call(self) -> None:
        self.commit_rulings("## Copier flags\n\n```text\n--skip /notes.md\n--keep /conf.json\n```\n")
        r = self.sync("--dry-run")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("--keep /conf.json", r.stderr)
        self.assertEqual([], self.claude_calls())

    def test_refuses_copier_flags_that_could_drop_a_ruling(self) -> None:
        section = "## Copier flags\n\n```text\n--skip /notes.md\n```\n"
        cases = {
            "double-quoted pattern": ('## Copier flags\n\n```text\n--skip "/notes.md"\n```\n', '"/notes.md"'),
            "single-quoted pattern": ("## Copier flags\n\n```text\n--skip '/notes.md'\n```\n", "'/notes.md'"),
            "second heading": (section + "\n" + section.replace("notes", "plain"), "second"),
            "second fence": (section + "\n```text\n--skip /plain.md\n```\n", "```text"),
            "flag line below the fence": (section + "--skip /plain.md\n", "--skip /plain.md"),
            "other case": (section.replace("flags", "Flags"), "## Copier Flags"),
            "other level": ("#" + section, "### Copier flags"),
            "extra words": (section.replace("flags", "flags (keep ours)"), "keep ours"),
            "quoted example above": ("````markdown\n" + section.replace("notes", "conf") + "````\n\n" + section,
                                     "````"),
            "fence under a subheading": ("## Copier flags\n\n### Keep ours\n\n```text\n--skip /notes.md\n```\n",
                                         "no flag lines"),
            "heading only": ("## Copier flags\n\n## Other\n", "no flag lines"),
            "empty fence": ("## Copier flags\n\n```text\n```\n", "no flag lines"),
        }
        for i, (name, (text, needle)) in enumerate(cases.items()):
            with self.subTest(name):
                rulings = self.base / f"rulings-{i}.md"
                rulings.write_text(text)
                self.work, self.claude_log = self.base / f"work-{i}", self.base / f"claude-{i}.log"
                r = self.sync("--dry-run", "--rulings", str(rulings))
                self.assertEqual(1, r.returncode, r.stdout + r.stderr)
                self.assertIn(needle, r.stderr)
                self.assertEqual([], self.claude_calls())

    def test_exclude_keeps_a_file_the_project_changed_with_crlf_rulings(self) -> None:
        # The first test is the control: without the flag conf.json conflicts. CRLF line ends
        # would otherwise leave a carriage return in the pattern, which then matches nothing.
        self.commit_rulings("## Copier flags\r\n\r\n```text\r\n--exclude /conf.json\r\n```\r\n")
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual('{"a": 3}', git("show", "HEAD~1:conf.json", cwd=self.work / "project"))
        prompt = self.claude_calls()[0]["prompt"]
        self.assertIn("`notes.md` is at", prompt)
        self.assertNotIn("`conf.json` is at", prompt)

    def test_without_rulings_the_prompt_has_no_rulings_section(self) -> None:
        # The two tests above are the control: with a rulings file this sentence is in the prompt.
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("Follow every ruling", self.claude_calls()[0]["prompt"])
        self.assertNotIn("owner's rulings", (self.work / "pr-body.md").read_text())

    def test_a_long_change_list_still_reaches_the_verify_skill(self) -> None:
        # Over 64 KiB of `git diff --name-status`: a reader that stops early sends git SIGPIPE,
        # and pipefail would then end the run before the verify skill.
        tpl = self.base / "tpl-big"
        git("clone", "-q", str(self.tpl), str(tpl), cwd=self.base)
        (tpl / "seed/many").mkdir()
        for i in range(800):
            (tpl / "seed/many" / f"{i:03d}-{'x' * 200}.md").write_text(f"{i}\n")
        git("add", "-A", cwd=tpl)
        git("commit", "-q", "-m", "v3", cwd=tpl)
        r = self.sync("--dry-run", loam=tpl, sha=git("rev-parse", "HEAD", cwd=tpl))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        calls = self.claude_calls()
        self.assertEqual(2, len(calls), calls)
        self.assertEqual(200, sum("\t" in line for line in calls[1]["prompt"].splitlines()))
        self.assertIn("VERIFY: PASS", (self.work / "pr-body.md").read_text())

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

    def test_refuses_when_the_port_leaves_a_base_marker(self) -> None:
        r = self.sync(mode="base")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("conflict markers remain in conf.json notes.md", r.stderr)
        self.assertEqual("", self.remote_branches())

    def test_a_diff3_conflict_style_still_gives_two_sided_hunks(self) -> None:
        # git merge-file follows merge.conflictStyle; under diff3 each hunk also carries a
        # `||||||| last update` section with the old template text.
        config = self.base / "diff3.gitconfig"
        config.write_text("[merge]\n\tconflictStyle = diff3\n")
        r = self.sync("--dry-run", env={"GIT_CONFIG_GLOBAL": str(config)})
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        project = self.work / "project"
        self.assertNotIn("|||||||", git("show", "HEAD~1:notes.md", cwd=project))
        self.assertEqual("line one\nshared line (project)\nline three", git("show", "HEAD:notes.md", cwd=project))

    def test_refuses_to_push_what_the_verify_agent_commits(self) -> None:
        r = self.sync(mode="commit")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("changed after the port", r.stderr)
        self.assertEqual("", self.remote_branches())
        self.assertFalse(self.gh_log.exists())

    def test_refuses_to_push_after_the_verify_agent_edits_a_tracked_file(self) -> None:
        r = self.sync(mode="edit")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("changed after the port", r.stderr)
        self.assertEqual("", self.remote_branches())
        self.assertFalse(self.gh_log.exists())

    def test_refuses_a_taken_branch_before_any_model_call(self) -> None:
        git("branch", self.branch, "main", cwd=self.remote)
        r = self.sync()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{self.branch} already exists", r.stderr)
        self.assertEqual([], self.claude_calls())
        self.assertFalse((self.work / "project").exists())
        self.assertFalse(self.gh_log.exists())

    def test_runs_when_src_path_already_names_the_loam_checkout(self) -> None:
        # The throwaway _src_path commit then changes nothing.
        clone = self.base / "local-src"
        git("clone", "-q", str(self.remote), str(clone), cwd=self.base)
        answers = clone / ".copier-answers.yml"
        answers.write_text(answers.read_text().replace("gh:example/loam", str(self.tpl)))
        git("commit", "-q", "-am", "local src", cwd=clone)
        git("push", "-q", "origin", "main", cwd=clone)
        r = self.sync("--dry-run")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        answers = (self.work / "project/.copier-answers.yml").read_text()
        self.assertIn(f"_src_path: {self.tpl}\n", answers)
        self.assertIn(f"_commit: v1.0.0-1-g{self.sha[:7]}", answers)

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
