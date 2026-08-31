from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class IpSweepTest(unittest.TestCase):
    def test_tracked_cultivation_wip_content_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            (repo / "bin").mkdir()
            (repo / "cultivation/wip").mkdir(parents=True)
            shutil.copy2(ROOT / "bin/ip-sweep.sh", repo / "bin/ip-sweep.sh")
            (repo / "bin/.ip-terms").write_text("forbidden-term\n", encoding="utf-8")
            asset = repo / "cultivation/wip/asset.md"
            asset.write_text("contains forbidden-term\n", encoding="utf-8")

            self.run_git(repo, "init", "-q")
            self.run_git(repo, "config", "user.name", "Test User")
            self.run_git(
                repo,
                "config",
                "user.email",
                "test@users.noreply.github.com",
            )
            self.run_git(repo, "add", "bin/ip-sweep.sh", "cultivation/wip/asset.md")
            self.run_git(repo, "commit", "-qm", "fixture")

            result = subprocess.run(
                ["bash", "bin/ip-sweep.sh"],
                cwd=repo,
                env={**os.environ, "IP_TERMS_FILE": "bin/.ip-terms"},
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("cultivation/wip/asset.md", result.stdout)

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
