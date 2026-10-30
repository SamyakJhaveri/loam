"""The no-growth cap on Loam's always-loaded prose, run on a temp tree."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin/always_loaded_prose.py"

FILES = {
    "CLAUDE.md": "# CLAUDE.md\n\n@AGENTS.md\n",
    "AGENTS.md": "# AGENTS.md\n\nRead @docs/extra.md first.\n",
    "docs/extra.md": "extra\n",
    ".claude/rules/always.md": "always\n",
    ".claude/rules/scoped.md": "---\npaths:\n  - src/**\n---\nscoped\n",
    "docs/fenced.md": "fenced\n",
    "docs/spanned.md": "spanned\n",
    "docs/unreached.md": "unreached\n",
}
COUNTED = ["CLAUDE.md", "AGENTS.md", ".claude/rules/always.md", "docs/extra.md"]


class AlwaysLoadedProseCapTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        for name, text in FILES.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        with (self.root / "CLAUDE.md").open("a", encoding="utf-8") as handle:
            handle.write("```\n@docs/fenced.md\n```\nNot `see @docs/spanned.md here` either.\n")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        self.total = sum((self.root / name).stat().st_size for name in COUNTED)

    def run_cap(self, cap: int) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--cap", str(cap)],
            capture_output=True, text=True,
        )

    def test_at_cap_passes(self) -> None:
        result = self.run_cap(self.total)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"{self.total} bytes", result.stdout)
        for name in COUNTED:
            self.assertIn(name, result.stdout)
        for name in ("scoped.md", "fenced.md", "spanned.md", "unreached.md"):
            self.assertNotIn(name, result.stdout)

    def test_one_byte_over_in_an_imported_file_fails(self) -> None:
        # docs/extra.md is reached only through AGENTS.md's @import, so this fails only if imports are followed.
        with (self.root / "docs/extra.md").open("a", encoding="utf-8") as handle:
            handle.write("x")
        result = self.run_cap(self.total)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"{self.total + 1} bytes", result.stderr)
        self.assertIn(f"{self.total}-byte cap", result.stderr)
        self.assertIn("docs/extra.md", result.stderr)
        self.assertIn("raise the cap", result.stderr)
        self.assertIn("name each cut (file and what it said) in the commit message and the PR body", result.stderr)

    def test_one_byte_under_fails(self) -> None:
        # A cap left above a shrunk total would let a later PR regrow the prose with no cap edit in its diff.
        result = self.run_cap(self.total + 1)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"lower the cap in bin/check to {self.total}", result.stderr)

    def test_untracked_rules_file_does_not_count(self) -> None:
        # Root .claude is a symlink into seed/, so a local untracked rule would fail bin/check here but not on CI.
        (self.root / ".claude/rules/local.md").write_text("local only\n", encoding="utf-8")
        result = self.run_cap(self.total)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("local.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
