"""Render the template once, then assert the rendered harness is well formed.

Replaces test_rendered_harness_contract.py, test_seed_claude_hooks.py and
test_agent_parity.py with one cheap smoke that renders once per class.
"""

from __future__ import annotations

import json
import os
import pathlib
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

# The destructive families both harnesses must forbid. This is the parity check
# that replaced agent-parity.toml: one list, asserted against the Claude deny
# list and against the Codex rules file.
FORBIDDEN_FAMILIES = (
    "rm -rf",
    "git push --force",
    "git reset --hard",
    "git clean -f",
    "git checkout .",
    "git restore .",
    "git stash clear",
    "git stash drop",
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

    def test_gitignore_ignores_the_memory_symlink(self):
        lines = (self.out / ".gitignore").read_text().splitlines()
        self.assertIn(".loam/memory", lines)

    def test_mem_inspect_renders_executable(self):
        script = self.out / "bin/mem-inspect"
        self.assertTrue(script.exists(), "bin/mem-inspect not rendered")
        self.assertTrue(os.access(script, os.X_OK), "bin/mem-inspect not executable")

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
            self.assertTrue(list(traces.glob("*-smoke123.jsonl.gz")), "mem-capture wrote no trace")
            index = (traces / "INDEX.md").read_text() if (traces / "INDEX.md").exists() else ""
            self.assertIn(" | smoke123 | ", index, "mem-capture wrote no INDEX line")

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

    def test_deny_and_rules_share_forbidden_families(self):
        deny = self.settings()["permissions"]["deny"]
        rules = (self.out / ".codex/rules/loam.rules").read_text()
        for fam in FORBIDDEN_FAMILIES:
            self.assertTrue(any(fam in d for d in deny), f"deny missing {fam}")
            self.assertIn(fam, rules, f"loam.rules missing {fam}")

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

    def test_codex_execpolicy_forbids_the_force_families(self):
        if not shutil.which("codex"):
            self.skipTest("codex CLI absent")
        rules = str(self.out / ".codex/rules/loam.rules")
        for cmd in (
            ["rm", "-rf", "x"],
            ["git", "push", "--force", "origin", "main"],
            ["git", "checkout", "."],
        ):
            r = subprocess.run(
                ["codex", "execpolicy", "check", "--rules", rules, "--"] + cmd,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(r.stdout).get("decision"), "forbidden", " ".join(cmd)
            )


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


if __name__ == "__main__":
    unittest.main()
