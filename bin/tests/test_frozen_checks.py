"""seed/bin/frozen-checks verify fails when a worker branch changes what the owner signed on main (#407).

Each test copies the seed script into a temp git repo, signs and commits on main as the owner, switches to a
worker branch, then runs the script as a subprocess. Git reads no host config.
SignedSignOff covers the opt-in owner sign-off on a branch (#511): throwaway ssh-keygen keys in the temp dir,
and a stand-in gpg.program for the OpenPGP case, so no case needs gpg-agent.
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


def git(*args: str, cwd: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, capture_output=True, check=True, timeout=30)


class Project(unittest.TestCase):
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


class FrozenChecks(Project):
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


# Stands in for gpg: signs with a fixed OpenPGP armor and reports any signature good and ultimately trusted,
# as a worker key in the host's keyring would be.
FAKE_GPG = """#!/bin/sh
cat > /dev/null
case " $* " in
*" --verify "*)
  printf '[GNUPG:] NEWSIG\\n[GNUPG:] GOODSIG 0123456789ABCDEF w <w@x>\\n'
  printf '[GNUPG:] VALIDSIG 0123456789ABCDEF0123456789ABCDEF01234567 2026-11-02 0 4 0 22 8 00 0123456789ABCDEF0123456789ABCDEF01234567\\n'
  printf '[GNUPG:] TRUST_ULTIMATE 0 pgp\\n' ;;
*)
  printf -- '-----BEGIN PGP SIGNATURE-----\\n\\niQ==\\n-----END PGP SIGNATURE-----\\n'
  printf '[GNUPG:] BEGIN_SIGNING\\n[GNUPG:] SIG_CREATED D 22 8 00 0 0123456789ABCDEF\\n' >&2 ;;
esac
"""


@unittest.skipUnless(shutil.which("ssh-keygen"), "needs ssh-keygen")
class SignedSignOff(Project):
    """A list that differs from main's passes only from a commit in main..HEAD that holds it and carries an SSH
    signature from a key in main's .github/allowed_signers."""

    def setUp(self) -> None:
        super().setUp()
        self.keys = self.top.parent / (self.top.name + "-keys")
        self.keys.mkdir()
        self.addCleanup(shutil.rmtree, self.keys)
        for name in ("owner", "worker"):
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", name, "-f", str(self.keys / name)],
                           capture_output=True, check=True, timeout=30)

    def signers(self, *names: str) -> None:
        (self.proj / ".github").mkdir(exist_ok=True)
        lines = [f"{n[0]}@x {(self.keys / (n + '.pub')).read_text().strip()}\n" for n in names]
        (self.proj / ".github/allowed_signers").write_text("".join(lines))

    def ssh_commit(self, key: str, msg: str) -> None:
        git("add", "-A", cwd=self.top)
        git("-c", "gpg.format=ssh", "-c", f"user.signingkey={self.keys / key}", "commit", "-qS", "-m", msg,
            cwd=self.top)

    def resign(self, line: str = "true") -> None:
        with open(self.proj / "checks/accept.sh", "a") as f:
            f.write(line + "\n")
        self.assertEqual(self.run_fc("sign", "checks/accept.sh").returncode, 0)

    def opt_in(self) -> None:
        """main holds allowed_signers listing the owner key and a signed list; the worker branch starts."""
        self.signers("owner")
        self.sign_on_main()

    def first_sign_off(self, key: str) -> None:
        """main holds allowed_signers but no list; the branch adds checks and signs them with key."""
        self.signers("owner")
        self.commit("signers")
        git("switch", "-qc", "worker", cwd=self.top)
        (self.proj / "checks").mkdir()
        (self.proj / "checks/accept.sh").write_text("test 1 = 1\n")
        self.assertEqual(self.run_fc("sign", "checks/accept.sh").returncode, 0)
        self.ssh_commit(key, "first")

    def test_owner_signed_passes(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("owner", "signoff")
        self.assert_passes()

    def test_first_sign_off_passes(self) -> None:
        self.first_sign_off("owner")
        self.assert_passes()

    def test_a_later_unsigned_commit_passes(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("owner", "signoff")
        git("commit", "-q", "--allow-empty", "-m", "later", cwd=self.top)
        self.assert_passes()

    def test_an_unsigned_merge_commit_passes(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("owner", "signoff")
        git("switch", "-q", "--detach", "main", cwd=self.top)
        git("merge", "-q", "--no-ff", "--no-edit", "worker", cwd=self.top)
        parents = git("rev-list", "--parents", "-1", "HEAD", cwd=self.top).stdout.split()
        self.assertEqual(len(parents), 3)
        self.assert_passes()

    def test_an_unsigned_resign_fails(self) -> None:
        self.opt_in()
        self.resign()
        self.commit("resign")
        self.assert_fails_naming("FROZEN.sha256")

    def test_an_unlisted_key_fails(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("worker", "resign")
        self.assert_fails_naming("FROZEN.sha256")

    def test_a_key_the_branch_adds_fails(self) -> None:
        self.opt_in()
        self.resign()
        self.signers("owner", "worker")
        self.ssh_commit("worker", "resign")
        self.assert_fails_naming("FROZEN.sha256")

    def test_a_first_sign_off_by_an_unlisted_key_fails(self) -> None:
        self.first_sign_off("worker")
        self.assert_fails_naming("FROZEN.sha256")

    def test_an_openpgp_signature_the_host_trusts_fails(self) -> None:
        fake = self.keys / "gpg"
        fake.write_text(FAKE_GPG)
        fake.chmod(0o755)
        git("config", "gpg.program", str(fake), cwd=self.top)
        self.opt_in()
        self.resign()
        git("add", "-A", cwd=self.top)
        git("-c", "gpg.format=openpgp", "-c", "user.signingkey=w@x", "commit", "-qS", "-m", "resign", cwd=self.top)
        self.assertIn(b"BEGIN PGP SIGNATURE", git("cat-file", "commit", "HEAD", cwd=self.top).stdout)
        # The hole the SSH check closes: an ssh-format verify-commit hands this signature to gpg and accepts it.
        git("-c", "gpg.format=ssh", "-c", f"gpg.ssh.allowedSignersFile={self.proj / '.github/allowed_signers'}",
            "-c", "gpg.minTrustLevel=fully", "verify-commit", "HEAD", cwd=self.top)
        self.assert_fails_naming("FROZEN.sha256")

    def test_an_unsigned_resign_after_an_owner_sign_off_fails(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("owner", "signoff")
        self.resign("false")
        self.commit("tamper")
        self.assert_fails_naming("FROZEN.sha256")

    def test_an_edit_after_an_owner_sign_off_fails_naming_the_file(self) -> None:
        self.opt_in()
        self.resign()
        self.ssh_commit("owner", "signoff")
        with open(self.proj / "checks/accept.sh", "a") as f:
            f.write("false\n")
        self.commit("edit")
        self.assert_fails_naming("checks/accept.sh")

    def test_a_ref_without_signers_fails_as_today(self) -> None:
        self.sign_on_main()
        self.resign()
        self.ssh_commit("owner", "signoff")
        self.assert_fails_naming("FROZEN.sha256 differs from its copy on main")

    def test_a_branch_cannot_opt_in(self) -> None:
        self.sign_on_main()
        self.resign()
        self.signers("worker")
        self.ssh_commit("worker", "signoff")
        self.assert_fails_naming("FROZEN.sha256 differs from its copy on main")


if __name__ == "__main__":
    unittest.main()
