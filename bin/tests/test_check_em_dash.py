"""bin/check's "no em dash in Loam-owned text" step fails closed (#237, #288).

The step runs on its own in a temp repo: the bin/check prelude, then the step up to the next one.
Each case runs under /bin/bash (3.2 on macOS) and again with LC_ALL=C.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECK = ROOT / "bin/check"
STEP = 'step "no em dash in Loam-owned text"'
# Built at run time, so this file passes the step it tests.
EM = chr(0x2014)
ESCAPED = "\\" + "u2014"
UNREAD = "the em-dash search did not read every file"


def em_step(check: str) -> str:
    """The prelude above the first step, then the em-dash step, then its exit status."""
    lines = check.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('step "'))
    start = lines.index(STEP)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('step "'))
    return "\n".join(lines[:first] + lines[start:end] + ['exit "$FAIL"']) + "\n"


class EmDashStep(unittest.TestCase):
    def run_step(self, untracked: dict[str, str], mode: int | None = None,
                 env: dict[str, str] | None = None) -> list[subprocess.CompletedProcess[str]]:
        """Commit a clean base, write the untracked files, run the step with and without LC_ALL=C."""
        repo = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / "bin").mkdir()
        (repo / "bin/em-step").write_text(em_step(CHECK.read_text(encoding="utf-8")), encoding="utf-8")
        (repo / "kept.txt").write_text("plain - dash\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "base"],
                       cwd=repo, check=True)
        for name, text in untracked.items():
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (repo / name).write_text(text, encoding="utf-8")
            if mode is not None:
                (repo / name).chmod(mode)
                self.addCleanup((repo / name).chmod, 0o644)
        runs = []
        for extra in ({}, {"LC_ALL": "C"}):
            r = subprocess.run(["/bin/bash", "bin/em-step"], cwd=repo, capture_output=True, text=True,
                               env={**os.environ, **(env or {}), **extra})
            runs.append(r)
        return runs

    def assert_fails(self, runs: list[subprocess.CompletedProcess[str]], *needles: str) -> None:
        for r in runs:
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            for needle in needles:
                self.assertIn(needle, r.stdout + r.stderr)

    def test_untracked_raw_dash_fails(self) -> None:
        self.assert_fails(self.run_step({"new.txt": f"a {EM} b\n"}), "new.txt:1:", "FAIL: em dash")

    def test_json_escaped_dash_fails(self) -> None:
        self.assert_fails(self.run_step({"hook.json": f'{{"msg": "a {ESCAPED} b"}}\n'}), "hook.json:1:", "FAIL: em dash")

    def test_unreadable_file_fails(self) -> None:
        # git grep prints an error for a file it cannot open and still exits 1, "nothing matched".
        if os.geteuid() == 0:
            self.skipTest("root reads a mode-000 file")
        self.assert_fails(self.run_step({"locked.txt": "plain\n"}, mode=0), "locked.txt", UNREAD)

    def test_bogus_git_dir_fails(self) -> None:
        self.assert_fails(self.run_step({}, env={"GIT_DIR": "/nonexistent/.git"}), UNREAD)

    def test_exempt_path_and_clean_text_pass(self) -> None:
        for r in self.run_step({"docs/archive/old.md": f"a {EM} b\n", "evals/p.json": f'"{ESCAPED}"\n',
                                "new.txt": "plain - dash\n"}):
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_claude_md_before_plain_dash_fails(self) -> None:
        # c0f630f replaced the em dash in CLAUDE.md's title; the file before it must fail the step.
        old = subprocess.run(["git", "show", "c0f630f^:CLAUDE.md"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
        self.assert_fails(self.run_step({"CLAUDE.md": old.stdout}), "CLAUDE.md:1:", "FAIL: em dash")


if __name__ == "__main__":
    unittest.main()
