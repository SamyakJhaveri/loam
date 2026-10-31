"""seed/bin/frozen-checks verify fails when a worker branch changes what the owner signed on main (#407).

Each test copies the seed script into a temp git repo, signs and commits on main as the owner, switches to a
worker branch, then runs the script as a subprocess. Git reads no host config.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "seed/bin/frozen-checks"

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "owner", "GIT_AUTHOR_EMAIL": "o@localhost",
    "GIT_COMMITTER_NAME": "owner", "GIT_COMMITTER_EMAIL": "o@localhost",
}
GIT_ENV.pop("FROZEN_REF", None)


def git(*args: str, cwd: pathlib.Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, capture_output=True, check=True, timeout=30)


class FrozenChecks(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name).resolve()
        git("init", "-q", "-b", "main", cwd=self.top)
        self.project(self.top)

    def project(self, proj: pathlib.Path) -> None:
        self.proj = proj
        (proj / "bin").mkdir(parents=True)
        shutil.copy(SCRIPT, proj / "bin/frozen-checks")
        (proj / "README").write_text("x\n")

    def run_fc(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([str(self.proj / "bin/frozen-checks"), *args], cwd=self.proj,
                              env={**GIT_ENV, **(env or {})}, capture_output=True, text=True, timeout=30)

    def commit(self, msg: str) -> None:
        git("add", "-A", cwd=self.top)
        git("commit", "-qm", msg, cwd=self.top)

    def sign_on_main(self, *files: str) -> None:
        """The owner writes checks/accept.sh, signs the files, commits on main, and a worker branch starts."""
        (self.proj / "checks").mkdir(exist_ok=True)
        (self.proj / "checks/accept.sh").write_text("test 1 = 1\n")
        self.assertEqual(self.run_fc("sign", *(files or ("checks/accept.sh",))).returncode, 0)
        self.commit("sign")
        git("switch", "-qc", "worker", cwd=self.top)

    def assert_fails_naming(self, text: str, env: dict[str, str] | None = None) -> None:
        r = self.run_fc("verify", env=env)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(text, r.stdout)

    def assert_passes(self) -> None:
        r = self.run_fc("verify")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_signed_passes(self) -> None:
        self.sign_on_main()
        self.assert_passes()

    def test_editing_a_listed_file_fails_naming_it(self) -> None:
        self.sign_on_main()
        with open(self.proj / "checks/accept.sh", "a") as f:
            f.write("true\n")
        self.assert_fails_naming("checks/accept.sh")

    def test_removing_the_list_fails(self) -> None:
        self.sign_on_main()
        (self.proj / "checks/FROZEN.sha256").unlink()
        self.assert_fails_naming("FROZEN.sha256")

    def test_resigning_on_the_worker_branch_fails(self) -> None:
        self.sign_on_main()
        with open(self.proj / "checks/accept.sh", "a") as f:
            f.write("true\n")
        self.assertEqual(self.run_fc("sign", "checks/accept.sh").returncode, 0)
        self.commit("resign")
        self.assert_fails_naming("FROZEN.sha256")

    def test_deleting_checks_on_the_worker_branch_fails(self) -> None:
        self.sign_on_main()
        shutil.rmtree(self.proj / "checks")
        self.commit("delete checks")
        self.assert_fails_naming("FROZEN.sha256")

    def test_an_explicit_frozen_ref_that_does_not_resolve_fails(self) -> None:
        self.commit("init")
        self.assert_fails_naming("FROZEN_REF=refs/heads/nope does not resolve", env={"FROZEN_REF": "refs/heads/nope"})

    def test_no_checks_and_no_list_passes(self) -> None:
        self.assert_passes()  # a fresh render: main is unborn and no origin exists
        self.commit("init")
        self.assert_passes()

    def test_a_project_nested_in_a_larger_repo_passes_after_sign_off(self) -> None:
        shutil.rmtree(self.proj / "bin")
        self.project(self.top / "sub/proj")
        self.sign_on_main()
        self.assert_passes()
        shutil.rmtree(self.proj / "checks")
        self.commit("delete checks")
        self.assert_fails_naming("FROZEN.sha256")

    def test_replacing_a_signed_symlink_with_another_file_fails(self) -> None:
        (self.proj / "checks").mkdir()
        (self.proj / "checks/real.sh").write_text("test 1 = 1\n")
        (self.proj / "checks/link.sh").symlink_to("real.sh")
        self.sign_on_main("checks/link.sh")
        (self.proj / "checks/link.sh").unlink()
        (self.proj / "checks/link.sh").write_text("true\n")
        self.assert_fails_naming("checks/link.sh")


if __name__ == "__main__":
    unittest.main()
