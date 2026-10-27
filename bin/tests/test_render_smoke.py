"""Render the template once, then assert the rendered harness is well formed.

Replaces test_rendered_harness_contract.py, test_seed_claude_hooks.py and
test_agent_parity.py with one cheap smoke that renders once per class.
"""

from __future__ import annotations

import gzip
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Disable git's automatic background maintenance for every git process these
# tests spawn or cause (directly, and inside the copier tasks that inherit this
# env). Git 2.47+ detaches `git maintenance run --auto` after a commit before
# deciding whether work is needed; that child keeps writing under .git (packs,
# multi-pack-index) after the parent returns, and TemporaryDirectory cleanup
# then races it -> "OSError: [Errno 39] Directory not empty: .../render/.git" in
# CI. GIT_CONFIG_COUNT injects the two disabling keys without touching any repo
# config (honoured by git >= 2.31; both keys exist in modern git).
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "gc.auto",
    "GIT_CONFIG_VALUE_0": "0",
    "GIT_CONFIG_KEY_1": "maintenance.auto",
    "GIT_CONFIG_VALUE_1": "false",
}

# The destructive families the Claude deny list must keep. This is the parity
# check that replaced agent-parity.toml: the families are asserted against the
# deny list, then every deny spelling is asserted against the Codex rules file.
FORBIDDEN_FAMILIES = (
    "rm -rf",
    "git push --force",
    "git reset --hard",
    "git clean -f",
    "git checkout .",
    "git restore .",
    "git stash clear",
    "git stash drop",
    "ssh-keygen",
)


def _copier():
    for cmd in (["copier"], ["uvx", "copier"]):
        try:
            subprocess.run(cmd + ["--version"], capture_output=True, check=True)
            return cmd
        except (OSError, subprocess.CalledProcessError):
            continue
    raise unittest.SkipTest("copier not available")


def _render(dest: pathlib.Path, ref: str = "HEAD") -> None:
    subprocess.run(
        _copier()
        + [
            "copy",
            "--trust",
            "--defaults",
            "--vcs-ref=" + ref,
            "--data",
            "project_name=smoke",
            "--data",
            "github_repo=",
            str(ROOT),
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


class RenderSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls._tmp.name) / "render"
        _render(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def settings(self) -> dict:
        return json.loads((self.out / ".claude/settings.json").read_text())

    def bash_deny_spellings(self) -> list[list[str]]:
        # "Bash(rm -r -f:*)" -> ["rm", "-r", "-f"]
        return [
            shlex.split(d[len("Bash(") : -1].removesuffix(":*"))
            for d in self.settings()["permissions"]["deny"]
            if d.startswith("Bash(")
        ]

    def test_settings_parse_and_hooks(self):
        s = self.settings()
        cmds = [
            h["command"]
            for block in s["hooks"].values()
            for entry in block
            for h in entry["hooks"]
        ]
        # split()[0] drops the Stop entry's `--throttle 600` argument.
        names = sorted({c.rsplit("/", 1)[-1].split()[0] for c in cmds})
        self.assertEqual(
            names,
            [
                "fable-session-brief.sh",
                "mem-capture.sh",
                "mem-recall.sh",
                "post-compact-reinject.sh",
            ],
        )
        self.assertNotIn("allow", s["permissions"])
        self.assertNotIn("ask", s["permissions"])
        self.assertNotIn("defaultMode", s["permissions"])
        self.assertNotIn("defaultMode", s)
        self.assertIs(s["sandbox"]["enabled"], True)
        self.assertIn(".env", s["sandbox"]["filesystem"]["denyRead"])

    def test_sandbox_excludes_gh_but_not_git(self):
        # P8: gh fails TLS inside the macOS sandbox; git push, fetch and pull stay in.
        self.assertEqual(
            self.settings()["sandbox"]["excludedCommands"],
            ["ssh *", "scp *", "rsync *", "gh *"],
        )

    def test_only_the_expected_hooks_ship(self):
        shipped = sorted(p.name for p in (self.out / ".claude/hooks").glob("*"))
        self.assertEqual(
            shipped,
            [
                "fable-session-brief.sh",
                "mem-capture.sh",
                "mem-recall.sh",
                "post-compact-reinject.sh",
            ],
        )

    def test_verify_loam_skill_does_not_render(self):
        # Loam-only skill kept out by a copier.yml _exclude line.
        self.assertFalse((self.out / ".claude/skills/verify-loam").exists())

    def test_gitignore_ignores_the_memory_symlink(self):
        lines = (self.out / ".gitignore").read_text().splitlines()
        self.assertIn(".loam/memory", lines)

    def test_mem_inspect_renders_executable(self):
        script = self.out / "bin/mem-inspect"
        self.assertTrue(script.exists(), "bin/mem-inspect not rendered")
        self.assertTrue(os.access(script, os.X_OK), "bin/mem-inspect not executable")

    def test_third_party_notices_render_with_full_license_texts(self):
        notices = (self.out / "THIRD_PARTY_NOTICES").read_text()
        for adapted in ("bin/mem-weekly.sh", ".claude/hooks/mem-capture.sh", "bin/mem-inspect"):
            self.assertIn(adapted, notices)
            self.assertIn("THIRD_PARTY_NOTICES", (self.out / adapted).read_text())
        # Two Apache-2.0 upstreams and two MIT upstreams, each carried in full.
        self.assertEqual(notices.count("TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION"), 2)
        self.assertEqual(notices.count("Permission is hereby granted, free of charge"), 2)

    def test_codex_config_parses(self):
        config = (self.out / ".codex/config.toml").read_text()
        data = tomllib.loads(config)
        self.assertEqual(data["default_permissions"], "loam")
        # A legacy sandbox_mode key would silently disable the named profile.
        self.assertNotIn("sandbox_mode", data)
        # default_permissions must sit above the first [table] header, or TOML
        # binds it to that table and the profile is never selected.
        lines = config.splitlines()
        first_table = next(
            i for i, ln in enumerate(lines) if ln.strip().startswith("[")
        )
        key = next(
            i
            for i, ln in enumerate(lines)
            if ln.strip().startswith("default_permissions")
        )
        self.assertLess(key, first_table)

    def test_codex_hooks_json_registers_the_four_events(self):
        hooks = json.loads((self.out / ".codex/hooks.json").read_text())["hooks"]
        self.assertEqual(
            sorted(hooks),
            ["PreCompact", "SessionEnd", "SessionStart", "Stop"],
        )

    def test_memory_hooks_capture_then_recall(self):
        # Both hooks always exit 0, so the exit code proves nothing: assert what they write and print.
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            transcript = tmp / "transcript.jsonl"
            transcript.write_text(
                json.dumps({"type": "user", "message": {"role": "user", "content": "Probe the smoke capture"}})
                + "\n"
                + json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Done."}]}})
                + "\n"
            )
            # A temp store, and no remote, so the hooks never touch the developer's real ~/memstore.
            env = {**GIT_ENV, "LOAM_MEMSTORE": str(tmp / "store")}
            env.pop("LOAM_MEMSTORE_REMOTE", None)

            def hook(name: str, payload: dict) -> subprocess.CompletedProcess:
                return subprocess.run(
                    ["bash", str(self.out / ".claude/hooks" / name)],
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.out,
                    env=env,
                )

            hook(
                "mem-capture.sh",
                {
                    "hook_event_name": "SessionEnd",
                    "transcript_path": str(transcript),
                    "session_id": "smoke123-capture",
                    "cwd": str(self.out),
                },
            )
            traces = tmp / "store/traces" / self.out.name
            self.assertTrue(list(traces.glob("*-smoke123-capture.jsonl.gz")), "mem-capture wrote no trace")
            index = (traces / "INDEX.md").read_text() if (traces / "INDEX.md").exists() else ""
            self.assertIn(" | smoke123-capture | ", index, "mem-capture wrote no INDEX line")

            r = hook(
                "mem-recall.sh",
                {
                    "hook_event_name": "SessionStart",
                    "source": "startup",
                    "session_id": "smoke456-recall",
                    "cwd": str(self.out),
                },
            )
            self.assertIn(f"## Memory ({self.out.name})", r.stdout)
            self.assertIn("Probe the smoke capture", r.stdout)

    # Codex thread ids are time-ordered UUIDv7, so sessions started within about 65 s
    # share their first 8 characters.
    CODEX_PROMPTS = {
        "01a15274-5d2e-7c41-9a3b-2f1e0d9c8b7a": "first codex session prompt",
        "01a15274-e8f0-7a12-8c4d-6b5a49382716": "second codex session prompt",
    }

    def _codex_capture(self, store: pathlib.Path, sid: str, rollout: pathlib.Path) -> None:
        env = {**GIT_ENV, "LOAM_MEMSTORE": str(store)}
        env.pop("LOAM_MEMSTORE_REMOTE", None)
        payload = {"hook_event_name": "Stop", "session_id": sid, "transcript_path": str(rollout), "cwd": str(self.out)}
        subprocess.run(
            ["bash", str(self.out / ".claude/hooks/mem-capture.sh")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30,
            cwd=self.out,
            env=env,
        )

    def _codex_rollout(self, tmp: pathlib.Path, sid: str, prompt: str) -> pathlib.Path:
        # The record shapes `codex exec` 0.153 writes: the prompt is a response_item and
        # an item_completed UserMessage, with no user_message event.
        records = [
            {"type": "session_meta", "payload": {"id": sid, "source": "exec", "originator": "codex_exec"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "<environment_context>probe</environment_context>"}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": prompt}]}},
            {"type": "event_msg", "payload": {"type": "item_completed", "thread_id": sid, "item": {
                "type": "UserMessage", "id": "u1", "content": [{"type": "text", "text": prompt, "text_elements": []}]}}},
        ]
        rollout = tmp / f"rollout-{sid}.jsonl"
        rollout.write_text("".join(json.dumps(r) + "\n" for r in records))
        return rollout

    def test_codex_sessions_sharing_an_id_prefix_keep_their_own_trace(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            rollouts = {sid: self._codex_rollout(tmp, sid, p) for sid, p in self.CODEX_PROMPTS.items()}
            for sid, rollout in rollouts.items():
                self._codex_capture(tmp / "store", sid, rollout)
            # A repeat capture of the same session updates its trace and adds no INDEX line.
            first = next(iter(rollouts))
            with rollouts[first].open("a") as fh:
                fh.write(json.dumps({"type": "event_msg", "payload": {"type": "task_complete"}}) + "\n")
            self._codex_capture(tmp / "store", first, rollouts[first])

            traces = tmp / "store/traces" / self.out.name
            bodies = [gzip.decompress(p.read_bytes()).decode() for p in sorted(traces.glob("*.jsonl.gz"))]
            self.assertEqual(len(bodies), 2, "one Codex session's capture overwrote the other's trace")
            for sid in rollouts:
                self.assertEqual(sum(sid in b for b in bodies), 1, f"session {sid} has no trace of its own")
            self.assertIn("task_complete", next(b for b in bodies if first in b), "the repeat capture did not update")
            lines = (traces / "INDEX.md").read_text().splitlines()
            self.assertEqual(len(lines), 2, lines)
            for sid in rollouts:
                r = subprocess.run(
                    [str(self.out / "bin/mem-inspect"), sid, "--json"],
                    capture_output=True,
                    text=True,
                    env={**os.environ, "LOAM_MEMSTORE": str(tmp / "store")},
                )
                self.assertEqual(r.returncode, 0, f"mem-inspect cannot resolve {sid}: {r.stderr}")

    def test_codex_capture_indexes_the_rollout_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            sid, prompt = next(iter(self.CODEX_PROMPTS.items()))
            self._codex_capture(tmp / "store", sid, self._codex_rollout(tmp, sid, prompt))
            index = tmp / "store/traces" / self.out.name / "INDEX.md"
            lines = index.read_text().splitlines() if index.exists() else []
            self.assertEqual(len(lines), 1, lines)
            self.assertTrue(lines[0].endswith(" | " + prompt), f"INDEX prompt column lacks {prompt!r}: {lines}")

    def test_every_claude_deny_spelling_has_a_codex_rule(self):
        deny = self.settings()["permissions"]["deny"]
        for fam in FORBIDDEN_FAMILIES:
            self.assertTrue(any(fam in d for d in deny), f"deny missing {fam}")
        rules = (self.out / ".codex/rules/loam.rules").read_text()
        patterns = [json.loads(p) for p in re.findall(r"pattern = (\[[^\]]*\])", rules)]
        # A prefix_rule matches every command whose leading tokens equal its pattern.
        missing = [
            " ".join(s) for s in self.bash_deny_spellings() if not any(s[: len(p)] == p for p in patterns)
        ]
        self.assertEqual(missing, [], "loam.rules has no prefix_rule for these Claude deny spellings")

    def test_rendered_check_passes_then_fails_on_a_planted_defect(self):
        def check(project: pathlib.Path) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["bash", "bin/check"], capture_output=True, text=True, cwd=project, env=GIT_ENV, timeout=300
            )

        r = check(self.out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(r.stdout.strip().splitlines()[-1].startswith("check: PASSED"), r.stdout)
        with tempfile.TemporaryDirectory() as d:
            project = pathlib.Path(d) / "planted"
            shutil.copytree(self.out, project, symlinks=True)
            settings = json.loads((project / ".claude/settings.json").read_text())
            settings["hooks"]["SessionStop"] = settings["hooks"].pop("Stop")
            (project / ".claude/settings.json").write_text(json.dumps(settings, indent=2) + "\n")
            r = check(project)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("'SessionStop' is not a Claude Code hook event", r.stdout)

    def test_factory_runtime_does_not_render(self):
        # Ruling R6 (2026-10-25) parked the native factory: no render ships its runtime or its docs.
        self.assertTrue((self.out / "docs").is_dir(), "render has no docs/ to check")
        for path in (".loam/runtime", "docs/runtime"):
            self.assertFalse((self.out / path).exists(), f"{path} rendered")

    def test_codex_execpolicy_forbids_every_claude_deny_spelling(self):
        if not shutil.which("codex"):
            self.skipTest("codex CLI absent")
        rules = str(self.out / ".codex/rules/loam.rules")
        allowed = []
        for cmd in self.bash_deny_spellings():
            r = subprocess.run(
                ["codex", "execpolicy", "check", "--rules", rules, "--"] + cmd,
                capture_output=True,
                text=True,
            )
            if json.loads(r.stdout).get("decision") != "forbidden":
                allowed.append(" ".join(cmd))
        self.assertEqual(allowed, [], "codex execpolicy does not forbid these Claude deny spellings")


class UpdateSmoke(unittest.TestCase):
    def test_update_from_latest_release_leaves_no_orphan_hook(self):
        cmd = _copier()
        # Existing projects update from the latest release. HEAD^ keeps the base a real older
        # release on the release commit itself, where HEAD carries the new tag.
        tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "HEAD^"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if tag.returncode != 0:
            self.skipTest("no release tag reachable from HEAD^ (shallow or tagless clone)")
        with tempfile.TemporaryDirectory() as d:
            # resolve(): macOS puts tmp under /var -> /private/var, and copier update rejects the unresolved path
            proj = pathlib.Path(d).resolve() / "p"
            _render(proj, ref=tag.stdout.strip())
            subprocess.run(["git", "init", "-q"], cwd=proj, check=True, env=GIT_ENV)
            subprocess.run(["git", "add", "-A"], cwd=proj, check=True, env=GIT_ENV)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=t@t",
                    "-c",
                    "user.name=t",
                    "commit",
                    "-qm",
                    "base",
                ],
                cwd=proj,
                check=True,
                env=GIT_ENV,
            )
            subprocess.run(
                cmd + ["update", "--trust", "--defaults", "--vcs-ref=HEAD", str(proj)],
                check=True,
                capture_output=True,
                cwd=proj,
                env=GIT_ENV,
            )
            settings = json.loads((proj / ".claude/settings.json").read_text())
            for block in settings["hooks"].values():
                for entry in block:
                    for h in entry["hooks"]:
                        # removeprefix, not lstrip: lstrip("./") would eat
                        # the leading dot of ".claude/..." as well. split()[0]
                        # drops any argument (the Stop entry's `--throttle 600`).
                        rel = h["command"].removeprefix("./").split()[0]
                        script = proj / rel
                        self.assertTrue(
                            script.exists(), f"orphan hook wiring: {h['command']}"
                        )


class UpdateTasks(unittest.TestCase):
    """`copier update` also runs _tasks in two temp renders that have no .git and no origin.

    A first-render task there commits "Initial commit from loam" and runs _gh_setup.sh, which
    pushes and posts a ruleset to the real repo. Stub gh and git push, and log what runs.
    """

    def test_update_runs_no_first_render_task(self):
        cmd = _copier()
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d).resolve()
            tpl, stubs, log, proj = tmp / "tpl", tmp / "stubs", tmp / "calls.log", tmp / "p"
            env = {
                **GIT_ENV,
                "PATH": f"{stubs}{os.pathsep}{os.environ['PATH']}",
                # A push the stub misses goes to a missing local path, never to GitHub.
                "GIT_CONFIG_COUNT": "3",
                "GIT_CONFIG_KEY_2": f"url.{tmp}/offline/.insteadOf",
                "GIT_CONFIG_VALUE_2": "https://github.com/",
            }
            stubs.mkdir()
            (stubs / "gh").write_text(f'#!/bin/sh\necho "gh $* (in $PWD)" >> "{log}"\n')
            (stubs / "git").write_text(
                "#!/bin/sh\n"
                f'case "$1" in push|commit) echo "git $* (in $PWD)" >> "{log}";; esac\n'
                '[ "$1" = push ] && exit 0\n'
                f'exec "{shutil.which("git")}" "$@"\n'
            )
            for stub in stubs.iterdir():
                stub.chmod(0o755)

            def git(cwd: pathlib.Path, *args: str) -> str:
                return subprocess.run(
                    ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                    cwd=cwd, check=True, capture_output=True, text=True, env=env,
                ).stdout

            def copier(*args: str) -> None:
                r = subprocess.run(cmd + [*args, "--trust", "--defaults"], capture_output=True, text=True, env=env)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

            # Both template versions carry this checkout's tasks: copier runs the old
            # version's tasks in the old temp render, so a real older tag would test that tag.
            listed = git(ROOT, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "copier.yml", "seed")
            for rel in filter(None, listed.split("\0")):
                if os.path.lexists(ROOT / rel):
                    (tpl / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / rel, tpl / rel, follow_symlinks=False)
            git(tpl, "init", "-q")
            git(tpl, "add", "-A")
            git(tpl, "commit", "-qm", "old")
            git(tpl, "tag", "v1.0.0")
            git(tpl, "commit", "-q", "--allow-empty", "-m", "new")
            git(tpl, "tag", "v1.0.1")

            copier("copy", "--vcs-ref=v1.0.0", "--data", "project_name=smoke",
                   "--data", "github_repo=loam-test/never-created", str(tpl), str(proj))
            # The copy path still runs every task in the new project.
            calls = log.read_text()
            self.assertEqual(git(proj, "log", "--format=%s"), "Initial commit from loam\n")
            self.assertIn(f"gh repo view loam-test/never-created (in {proj})", calls)
            self.assertIn(f"git push -u origin main (in {proj})", calls)
            self.assertFalse((proj / "_gh_setup.sh").exists())
            self.assertEqual(git(proj, "status", "--porcelain"), "")

            log.unlink()
            copier("update", "--vcs-ref=v1.0.1", str(proj))
            calls = log.read_text() if log.exists() else ""
            bad = [
                ln for ln in calls.splitlines()
                if ln.startswith(("gh ", "git push")) or "Initial commit from loam" in ln
            ]
            if bad:
                self.fail("first-render tasks ran during copier update:\n" + "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
