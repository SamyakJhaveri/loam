"""Behavior of bin/loam-attach.sh.

Runs the real script (it reads the seed harness and marketplace from this
checkout) against a throwaway target directory, and checks what it writes,
the refusal without --force, that settings.local.json is never clobbered, and
that the seed's sandbox placeholder ignore lines reach new and earlier attaches.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATTACH = ROOT / "bin/loam-attach.sh"
MARKER = "# Loam harness (added by loam-attach.sh)"
# The empty read-only files the Claude Code sandbox leaves on Linux to mask
# protected paths (seed/.gitignore.jinja, #473).
PLACEHOLDERS = (
    ".bash_profile .bashrc .gitconfig .gitmodules .idea .profile .ripgreprc"
    " .vscode .zprofile .zshrc .claude/.cc-writes .claude/scheduled_tasks.json"
    " .claude/agents .claude/commands .claude/output-styles .claude/routines"
    " .claude/workflows"
).split()


class LoamAttachTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dst = pathlib.Path(self.tmp.name) / "target"
        self.dst.mkdir()

    def attach(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(ATTACH), str(self.dst), *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def git(self, *args: str) -> str:
        r = subprocess.run(
            ["git", "-c", "core.excludesFile=/dev/null", "-C", str(self.dst), *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
        return r.stdout

    def commit_and_plant_placeholders(self) -> str:
        """Commit the attach, plant every placeholder, return the porcelain status."""
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "attach")
        for name in PLACEHOLDERS:
            path = self.dst / name
            path.write_text("")
            path.chmod(0o444)
        return self.git("status", "--porcelain")

    def test_writes_the_harness(self) -> None:
        r = self.attach()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue((self.dst / ".claude/settings.json").is_file())
        hooks = list((self.dst / ".claude/hooks").glob("*.sh"))
        self.assertTrue(hooks, "no hook scripts copied")
        slj = self.dst / ".claude/settings.local.json"
        data = json.loads(slj.read_text())
        self.assertTrue(data["enabledPlugins"]["sam-cc-setup@seed-skills"])
        src = data["extraKnownMarketplaces"]["seed-skills"]["source"]
        self.assertEqual(str(ROOT / "cultivation/marketplace"), src["path"])
        gi = (self.dst / ".gitignore").read_text()
        self.assertIn("# Loam harness (added by loam-attach.sh)", gi)
        self.assertIn(".claude/settings.local.json", gi)
        self.assertIn(".validation_passed", gi)

    def test_refuses_without_force(self) -> None:
        self.assertEqual(0, self.attach().returncode)
        r = self.attach()
        self.assertEqual(1, r.returncode)
        self.assertIn("re-run with --force", r.stderr)

    def test_force_keeps_settings_local_and_gitignore_stays_idempotent(self) -> None:
        self.assertEqual(0, self.attach().returncode)
        slj = self.dst / ".claude/settings.local.json"
        slj.write_text('{"mine": true}\n')
        r = self.attach("--force")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual('{"mine": true}\n', slj.read_text())
        gi = (self.dst / ".gitignore").read_text()
        self.assertEqual(1, gi.count("# Loam harness (added by loam-attach.sh)"))

    def test_force_keeps_foreign_hooks(self) -> None:
        hooks = self.dst / ".claude/hooks"
        hooks.mkdir(parents=True)
        foreign = hooks / "my-own-hook.sh"
        body = "#!/usr/bin/env bash\necho mine\n"
        foreign.write_text(body)
        r = self.attach("--force")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(foreign.is_file(), "foreign hook was removed")
        self.assertEqual(body, foreign.read_text(), "foreign hook was mutated")
        self.assertTrue(list(hooks.glob("*.sh")), "seed hooks not copied alongside")

    def test_refuses_when_hooks_dir_exists_without_settings(self) -> None:
        hooks = self.dst / ".claude/hooks"
        hooks.mkdir(parents=True)
        (hooks / "my-own-hook.sh").write_text("#!/usr/bin/env bash\n")
        r = self.attach()
        self.assertEqual(1, r.returncode)
        self.assertIn("re-run with --force", r.stderr)

    def test_gitignore_without_trailing_newline(self) -> None:
        gi = self.dst / ".gitignore"
        gi.write_text("node_modules/")  # no trailing newline
        self.assertEqual(0, self.attach().returncode)
        self.assertEqual(0, self.attach("--force").returncode)
        lines = gi.read_text().splitlines()
        self.assertEqual(1, lines.count("# Loam harness (added by loam-attach.sh)"))
        self.assertIn("node_modules/", lines)

    def test_placeholders_ignored_after_attach(self) -> None:
        self.git("init", "-q")
        r = self.attach()
        self.assertEqual(0, r.returncode, r.stderr)
        # Ten harness lines, each placeholder, and the five directory
        # re-includes: a read that runs past the block's blank line would add
        # the seed's Jinja and secrets lines.
        self.assertIn(f"{10 + len(PLACEHOLDERS) + 5} ignore lines appended", r.stdout)
        self.assertNotIn("{%", (self.dst / ".gitignore").read_text())
        self.assertEqual("", self.commit_and_plant_placeholders())

    def test_force_rerun_appends_only_missing_lines(self) -> None:
        self.git("init", "-q")
        self.assertEqual(0, self.attach().returncode)
        gi = self.dst / ".gitignore"
        gi.write_text(MARKER + "\n.codex_review_done\n")  # an attach from before #559
        r = self.attach("--force")
        self.assertEqual(0, r.returncode, r.stderr)
        once = gi.read_bytes()
        r = self.attach("--force")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("ignore lines already present", r.stdout)
        self.assertEqual(once, gi.read_bytes(), "a second --force run changed .gitignore")
        lines = gi.read_text().splitlines()
        self.assertEqual(1, lines.count(MARKER))
        self.assertIn("/.bashrc", lines)
        self.assertIn(".claude/audit.log", lines)
        rules = [ln for ln in lines if ln and not ln.startswith("#")]
        self.assertEqual(len(rules), len(set(rules)), "a rule is there twice")
        self.assertEqual("", self.commit_and_plant_placeholders())

    def test_shared_config_stays_visible(self) -> None:
        self.git("init", "-q")
        self.assertEqual(0, self.attach().returncode)
        (self.dst / ".mcp.json").write_text('{"mcpServers": {}}\n')
        (self.dst / ".claude/loop.md").write_text("x\n")
        (self.dst / ".claude/agents").mkdir()
        (self.dst / ".claude/agents/a.md").write_text("x\n")
        out = self.git("status", "--porcelain", "--untracked-files=all").splitlines()
        for name in (".mcp.json", ".claude/loop.md", ".claude/agents/a.md"):
            self.assertIn(f"?? {name}", out)

    def test_reworded_seed_block_fails_loudly(self) -> None:
        loam = pathlib.Path(self.tmp.name) / "loam"
        (loam / "bin").mkdir(parents=True)
        for rel in ("bin/loam-attach.sh", "bin/lib.sh", "seed/.gitignore.jinja"):
            (loam / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, loam / rel)
        shutil.copytree(ROOT / "seed/.claude/hooks", loam / "seed/.claude/hooks")
        shutil.copy2(ROOT / "seed/.claude/settings.json", loam / "seed/.claude/settings.json")
        (loam / "cultivation/marketplace").mkdir(parents=True)
        seed_gi = loam / "seed/.gitignore.jinja"
        seed_gi.write_text(
            seed_gi.read_text().replace(
                "Empty read-only files the Claude Code sandbox creates",
                "Read-only files that the sandbox leaves",
            )
        )
        r = subprocess.run(
            ["bash", str(loam / "bin/loam-attach.sh"), str(self.dst)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("no sandbox placeholder block", r.stderr)
        self.assertEqual([], list(self.dst.iterdir()), "the target was written before the seed read failed")


if __name__ == "__main__":
    unittest.main()
