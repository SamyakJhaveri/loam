"""`bin/factory.d/heldout-serve` runs the candidate's code in a boundary that shows only /usr and /etc of the host.

No /run, /var or /home inside, so no host socket is reachable (a read-only mount still lets a process connect to a
socket): not the held-out user's systemd manager under /run/user, which could start a process outside the boundary.
The fixture worktree sits outside the service's temp folder and is made with `git worktree add`, so the export finds
the worktree's git folders through its `.git` file. Skipped where bwrap cannot start.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVE = ROOT / "bin/factory.d/heldout-serve"
SLUG, KEY = "o__r", "k"
# The candidate's probe.sh reports what the boundary shows; the block runs it, and its output stays in the round record.
PROBE = """for p in /run /run/user /var /home /root /tmp/escape; do [ -e "$p" ] && echo "seen $p"; done
[ -e "/run/user/$(id -u)/bus" ] && echo "seen bus"
touch "$1/escaped" 2> /dev/null && echo "wrote outside"
echo probed
"""


def bwrap_starts() -> bool:
    if shutil.which("bwrap") is None:
        return False
    r = subprocess.run(["bwrap", "--unshare-all", "--ro-bind", "/", "/", "true"], capture_output=True, check=False)
    return r.returncode == 0


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


@unittest.skipUnless(bwrap_starts(), "bwrap cannot start here")
class HeldoutBoundary(unittest.TestCase):
    def setUp(self) -> None:
        self.dirs = [pathlib.Path(tempfile.mkdtemp(prefix="heldout-test.")) for _ in range(3)]
        self.fix, self.tmp, self.svc = self.dirs
        self.spool, self.root = self.svc / "spool", self.svc / "heldout"
        for d in (self.spool / "requests", self.spool / "replies", self.root / SLUG / KEY):
            d.mkdir(parents=True)
        (self.root / SLUG / KEY / "checks.sh").write_text(
            f'sh probe.sh "{self.fix}"\n[ -f probe.sh ] && pass probed || fail probed "no probe.sh"\n')
        main = self.fix / "main"
        main.mkdir()
        git("init", "-q", "-b", "main", cwd=main)
        (main / "probe.sh").write_text(PROBE)
        git("add", "probe.sh", cwd=main)
        git("commit", "-q", "-m", "probe", cwd=main)
        self.wt = self.fix / "wt"
        git("worktree", "add", "-q", "--detach", str(self.wt), cwd=main)

    def tearDown(self) -> None:
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def ask(self, rid: str, kind: str, wt: pathlib.Path) -> str:
        sha = git("rev-parse", "HEAD", cwd=self.wt)
        (self.spool / "requests" / rid).write_text(
            f"slug={SLUG}\nkey={KEY}\nworktree={wt}\nsha={sha}\nround=1\nkind={kind}\n")
        env = {**os.environ, "TMPDIR": str(self.tmp)}
        subprocess.run([str(SERVE), str(self.spool), str(self.root)], env=env, capture_output=True, check=False)
        reply = self.spool / "replies" / rid
        return reply.read_text().strip() if reply.exists() else ""

    def test_candidate_sees_no_host_socket_folder(self) -> None:
        self.assertEqual(self.ask("a-probe", "probe", self.wt), "ready 0")
        self.assertEqual(self.ask("b-check", "check", self.wt), "pass 1")
        out = (self.root / SLUG / KEY / "out/1/round-1").read_text()
        self.assertIn("probed", out)
        self.assertNotIn("seen", out)
        self.assertNotIn("wrote outside", out)
        self.assertFalse((self.fix / "escaped").exists())

    def test_git_folder_inside_the_root_is_never_shown(self) -> None:
        # A worktree whose .git file names a folder under the held-out root stays pending: no mount, no reply.
        forged = self.fix / "forged"
        forged.mkdir()
        (forged / ".git").write_text(f"gitdir: {self.root / SLUG}\n")
        self.assertEqual(self.ask("a-probe", "probe", self.wt), "ready 0")
        self.assertEqual(self.ask("b-check", "check", forged), "")
        self.assertFalse((self.root / SLUG / KEY / "out/1/round-1").exists())


if __name__ == "__main__":
    unittest.main()
