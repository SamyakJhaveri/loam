"""bin/check's "shell syntax + whitespace" step reads untracked, non-ignored files, as CI will once they are added (#282).

The step runs on its own in a temp repo: the bin/check prelude, then the step up to the next one.
"""

from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECK = ROOT / "bin/check"
STEP = 'step "shell syntax + whitespace"'


def ws_step(check: str) -> str:
    """The prelude above the first step, then the whitespace step, then its exit status."""
    lines = check.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith('step "'))
    start = lines.index(STEP)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('step "'))
    return "\n".join(lines[:first] + lines[start:end] + ['exit "$FAIL"']) + "\n"


class UntrackedWhitespace(unittest.TestCase):
    def run_step(self, committed: dict[str, str], untracked: dict[str, str]) -> subprocess.CompletedProcess[str]:
        repo = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / "bin").mkdir()
        (repo / "bin/ws-step").write_text(ws_step(CHECK.read_text(encoding="utf-8")), encoding="utf-8")
        for name, text in committed.items():
            (repo / name).write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "base"],
                       cwd=repo, check=True)
        for name, text in untracked.items():
            (repo / name).write_text(text, encoding="utf-8")
        return subprocess.run(["bash", "bin/ws-step"], cwd=repo, capture_output=True, text=True)

    def test_untracked_trailing_whitespace_fails(self) -> None:
        r = self.run_step({"kept.txt": "clean\n"}, {"new.txt": "trailing   \n"})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("new.txt:1: trailing whitespace", r.stdout + r.stderr)

    def test_clean_untracked_patch_and_ignored_pass(self) -> None:
        r = self.run_step({".gitignore": "ignored.txt\n"},
                          {"new.txt": "clean\n", "new.patch": "x  \n", "ignored.txt": "x  \n"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
