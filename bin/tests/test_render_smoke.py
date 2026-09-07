"""Render the template once, then assert the rendered harness is well formed.

Replaces test_rendered_harness_contract.py, test_seed_claude_hooks.py and
test_agent_parity.py with one cheap smoke that renders once per class.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

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

    def test_settings_parse_and_two_hooks(self):
        s = self.settings()
        cmds = [
            h["command"]
            for block in s["hooks"].values()
            for entry in block
            for h in entry["hooks"]
        ]
        names = sorted({c.rsplit("/", 1)[-1] for c in cmds})
        self.assertEqual(names, ["fable-session-brief.sh", "post-compact-reinject.sh"])
        self.assertNotIn("allow", s["permissions"])
        self.assertNotIn("ask", s["permissions"])
        self.assertNotIn("defaultMode", s["permissions"])
        self.assertNotIn("defaultMode", s)
        self.assertIs(s["sandbox"]["enabled"], True)
        self.assertIn(".env", s["sandbox"]["filesystem"]["denyRead"])

    def test_only_the_two_hooks_ship(self):
        shipped = sorted(p.name for p in (self.out / ".claude/hooks").glob("*"))
        self.assertEqual(
            shipped, ["fable-session-brief.sh", "post-compact-reinject.sh"]
        )

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

    def test_each_hook_runs_and_exits_zero(self):
        hooks = sorted((self.out / ".claude/hooks").glob("*.sh"))
        self.assertTrue(hooks, "no hooks rendered")
        for hook in hooks:
            r = subprocess.run(
                ["bash", str(hook)],
                input='{"model":"opus"}',
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(r.returncode, 0, f"{hook.name}: {r.stderr}")

    def test_deny_and_rules_share_forbidden_families(self):
        deny = self.settings()["permissions"]["deny"]
        rules = (self.out / ".codex/rules/loam.rules").read_text()
        for fam in FORBIDDEN_FAMILIES:
            self.assertTrue(any(fam in d for d in deny), f"deny missing {fam}")
            self.assertIn(fam, rules, f"loam.rules missing {fam}")

    def test_rendered_check_exists(self):
        check = self.out / "bin/check"
        self.assertTrue(check.exists())
        r = subprocess.run(["bash", "-n", str(check)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

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
    def test_update_from_v230_leaves_no_orphan_hook(self):
        cmd = _copier()
        with tempfile.TemporaryDirectory() as d:
            proj = pathlib.Path(d) / "p"
            _render(proj, ref="v2.3.0")
            subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
            subprocess.run(["git", "add", "-A"], cwd=proj, check=True)
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
            )
            subprocess.run(
                cmd + ["update", "--trust", "--defaults", "--vcs-ref=HEAD", str(proj)],
                check=True,
                capture_output=True,
                cwd=proj,
            )
            settings = json.loads((proj / ".claude/settings.json").read_text())
            for block in settings["hooks"].values():
                for entry in block:
                    for h in entry["hooks"]:
                        # removeprefix, not lstrip: lstrip("./") would eat
                        # the leading dot of ".claude/..." as well.
                        rel = h["command"].removeprefix("./")
                        script = proj / rel
                        self.assertTrue(
                            script.exists(), f"orphan hook wiring: {h['command']}"
                        )


if __name__ == "__main__":
    unittest.main()
