from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
NOREPLY = "test@users.noreply.github.com"


class IpSweepTest(unittest.TestCase):
    def test_tracked_cultivation_wip_content_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"cultivation/wip/asset.md": "contains forbidden-term\n"})
            (repo / "bin/.ip-terms").write_text("forbidden-term\n", encoding="utf-8")

            result = self.sweep(repo)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("cultivation/wip/asset.md", result.stdout)

    def test_clean_tree_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})
            (repo / "bin/.ip-terms").write_text("zz-planted-term\n", encoding="utf-8")

            result = self.sweep(repo, IP_SWEEP_STRICT="1")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("ip-sweep: PASS (strict)", result.stdout)

    def test_strict_fails_without_term_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})

            result = self.sweep(repo, IP_SWEEP_STRICT="1")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("strict mode requires a term file", result.stdout)

    def test_strict_reports_identity_and_term_failures_together(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n", "notes.md": "contains forbidden-term\n"})
            self.commit_edu(repo)
            (repo / "bin/.ip-terms").write_text("forbidden-term\n", encoding="utf-8")

            result = self.sweep(repo, IP_SWEEP_STRICT="1")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("someone@example.edu", result.stdout)
            self.assertIn("foreign-IP terms found in tracked files:\nnotes.md", result.stdout)

    def test_identity_only_fails_on_non_noreply_author(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})
            (repo / "README.md").write_text("edited\n", encoding="utf-8")
            self.run_git(repo, "commit", "-qam", "edit", "--author", "Someone <someone@example.edu>")

            result = self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("non-noreply author", result.stdout)
            self.assertIn("someone@example.edu", result.stdout)

    def test_identity_only_passes_noreply_author_without_term_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})

            result = self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual("ip-sweep: PASS (identity only)\n", result.stdout)

    def test_identity_only_checks_every_commit_when_no_sha_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})
            self.commit_edu(repo)
            self.set_accepted(repo, "")

            result = self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("someone@example.edu", result.stdout)

    def test_identity_only_skips_exactly_the_accepted_sha(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})
            sha = self.commit_edu(repo)
            self.set_accepted(repo, sha)

            result = self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.set_accepted(repo, sha[:12])
            self.assertEqual(1, self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1").returncode)

    def test_identity_only_fails_when_awk_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as bin_dir:
            repo = self.make_repo(temp_dir, {"README.md": "nothing to see\n"})
            fake_awk = pathlib.Path(bin_dir) / "awk"
            fake_awk.write_text("#!/bin/sh\nexit 2\n", encoding="utf-8")
            fake_awk.chmod(0o755)

            result = self.sweep(repo, IP_SWEEP_IDENTITY_ONLY="1", PATH=f"{bin_dir}:{os.environ['PATH']}")

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("PASS", result.stdout)

    def commit_edu(self, repo: pathlib.Path) -> str:
        (repo / "README.md").write_text("edited\n", encoding="utf-8")
        self.run_git(repo, "commit", "-qam", "edit", "--author", "Someone <someone@example.edu>")
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True,
                              capture_output=True, check=True).stdout.strip()

    def set_accepted(self, repo: pathlib.Path, shas: str) -> None:
        script = repo / "bin/ip-sweep.sh"
        text = script.read_text(encoding="utf-8")
        start = text.index('IDENTITY_ACCEPTED="')
        end = text.index('"', start + len('IDENTITY_ACCEPTED="')) + 1
        script.write_text(text[:start] + f'IDENTITY_ACCEPTED="{shas}"' + text[end:], encoding="utf-8")

    def make_repo(self, temp_dir: str, files: dict[str, str]) -> pathlib.Path:
        repo = pathlib.Path(temp_dir)
        (repo / "bin").mkdir()
        shutil.copy2(ROOT / "bin/ip-sweep.sh", repo / "bin/ip-sweep.sh")
        for name, text in files.items():
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (repo / name).write_text(text, encoding="utf-8")
        self.run_git(repo, "init", "-q")
        self.run_git(repo, "config", "user.name", "Test User")
        self.run_git(repo, "config", "user.email", NOREPLY)
        self.run_git(repo, "add", "bin/ip-sweep.sh", *files)
        self.run_git(repo, "commit", "-qm", "fixture")
        return repo

    def sweep(self, repo: pathlib.Path, **env: str) -> subprocess.CompletedProcess[str]:
        # Drop inherited IP_* settings so a developer's real term file or strict flag cannot leak in.
        base = {k: v for k, v in os.environ.items() if not k.startswith("IP_")}
        return subprocess.run(
            ["bash", "bin/ip-sweep.sh"],
            cwd=repo,
            env={**base, "IP_TERMS_FILE": "bin/.ip-terms", **env},
            text=True,
            capture_output=True,
            check=False,
        )

    def run_git(self, repo: pathlib.Path, *arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=repo,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
