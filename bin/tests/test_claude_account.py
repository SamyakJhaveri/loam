"""bin/claude-account keeps each account's token in its 0600 file only (#644): `use` names the account active and drops a
token key it finds in the settings file, and `exec <cmd>` runs the command with the active account's token in its
environment, printing nothing. A settings `env` value beats the launch environment for a shell `claude` (LESSONS.md,
PR #418), so every Loam launcher starts its claude call through `exec` once `use` has emptied the settings tier.

The helper runs for real on scratch accounts directories and settings files. The launcher cases run the factory's eval
replay, its login check and advisor probe, the overnight driver's run() and limit-alarm's default LAUNCH in a scratch
HOME, with a stub `claude` that logs the token Claude Code's settings precedence would pick: the launch env, then the
user tier unless --setting-sources leaves it out, then the --settings file's env. All tokens are fakes.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HELPER = ROOT / "bin/claude-account"
TOKEN = "CLAUDE_CODE_OAUTH_TOKEN"  # by name, so no token assignment appears for the merge secret grep
SCRUB = ("CLAUDE_ACCOUNTS_DIR", "CLAUDE_SETTINGS_FILE", "CLAUDE_CONFIG_DIR", "LAUNCH", TOKEN)
LINUX_ONLY = unittest.skipUnless(sys.platform.startswith("linux"), "the launchers need Linux prctl, /proc and GNU timeout")
PRINT_TOKEN = ["sh", "-c", 'printf %s "${' + TOKEN + '-unset}"']

# Logs the winning token to STUB_OUT for every call but --version and --help, which spend nothing.
STUB_CLAUDE = r"""#!/bin/bash
case " $* " in *" --version "*) echo 2.1.999; exit 0;; *" --help "*) exit 0;; esac
src=user; sf=; p=; for x in "$@"; do case $p in --setting-sources) src=$x;; --settings) sf=$x;; esac; p=$x; done
t=${CLAUDE_CODE_OAUTH_TOKEN-unset}
case ",$src," in *,user,*) u=$(jq -r '.env.CLAUDE_CODE_OAUTH_TOKEN // empty' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json" 2>/dev/null); t=${u:-$t};; esac
s=$(jq -r '.env.CLAUDE_CODE_OAUTH_TOKEN // empty' "$sf" 2>/dev/null); t=${s:-$t}
printf '%s\n' "$t" >> "$STUB_OUT"
[ -t 0 ] || cat > /dev/null
echo '{"type":"result","subtype":"success","is_error":false,"num_turns":1,"total_cost_usd":0,"usage":{},"result":"{}","loggedIn":true}'
"""


def scrubbed() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k not in SCRUB and not k.startswith("FACTORY_")}


class Scratch(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.d = pathlib.Path(tmp.name)
        self.acc = self.d / "acc"
        self.acc.mkdir()
        self.settings = self.d / "settings.json"
        for n in ("a", "b"):
            (self.acc / f"{n}.token").write_text(f"sk-ant-oat01-fake-{n}\n")
        (self.acc / "active").write_text("a\n")

    def helper(self, *args: str, settings: pathlib.Path | None = None, **extra: str
               ) -> subprocess.CompletedProcess[str]:
        env = {**scrubbed(), "CLAUDE_ACCOUNTS_DIR": str(self.acc),
               "CLAUDE_SETTINGS_FILE": str(settings or self.settings), **extra}
        return subprocess.run([str(HELPER), *args], env=env, capture_output=True, text=True, check=False)


class UseTests(Scratch):
    def test_use_names_the_account_and_drops_the_settings_token(self) -> None:
        self.settings.write_text(json.dumps({"env": {TOKEN: "sk-ant-oat01-fake-a", "KEEP": "1"}, "model": "m"}))
        self.settings.chmod(0o644)
        proc = self.helper("use", "b")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.acc / "active").read_text(), "b\n")
        self.assertEqual((self.acc / "active").stat().st_mode & 0o777, 0o600, "active took the caller's umask")
        self.assertNotIn("sk-ant-oat01", self.settings.read_text())
        self.assertEqual(json.loads(self.settings.read_text()), {"env": {"KEEP": "1"}, "model": "m"})
        self.assertEqual(self.settings.stat().st_mode & 0o777, 0o600)
        self.assertNotIn("sk-ant-oat01", proc.stdout + proc.stderr)

    def test_use_leaves_a_token_free_settings_file_alone_and_never_creates_one(self) -> None:
        self.settings.write_text('{"model": "m"}\n')
        self.settings.chmod(0o644)
        self.assertEqual(self.helper("use", "b").returncode, 0)
        self.assertEqual((self.settings.read_text(), self.settings.stat().st_mode & 0o777), ('{"model": "m"}\n', 0o644))
        none = self.d / "none.json"
        self.assertEqual(self.helper("use", "a", settings=none).returncode, 0)
        self.assertFalse(none.exists())
        self.assertEqual(self.helper("status").stdout, "active: a; stored: a b\n")

    def test_use_of_a_missing_account_changes_nothing(self) -> None:
        self.settings.write_text(json.dumps({"env": {TOKEN: "sk-ant-oat01-fake-a"}}))
        before = self.settings.read_text()
        proc = self.helper("use", "c")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no stored token for 'c'", proc.stderr)
        self.assertEqual(((self.acc / "active").read_text(), self.settings.read_text()), ("a\n", before))

    def test_use_with_a_settings_file_jq_cannot_parse_changes_nothing(self) -> None:
        self.settings.write_text('{"env": {"' + TOKEN + '": "sk-ant-oat01-fake-a",\n')
        before = self.settings.read_text()
        proc = self.helper("use", "b")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(str(self.settings), proc.stderr)
        self.assertEqual(((self.acc / "active").read_text(), self.settings.read_text()), ("a\n", before))


class ExecTests(Scratch):
    def test_exec_hands_the_command_the_active_token_and_prints_nothing(self) -> None:
        self.settings.write_text(json.dumps({"env": {"KEEP": "1"}}))
        before = self.settings.read_text()
        (self.acc / "active").write_text("b\n")
        proc = self.helper("exec", *PRINT_TOKEN, **{TOKEN: "launch-x"})
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "sk-ant-oat01-fake-b", ""))
        self.assertEqual(self.settings.read_text(), before)
        quiet = self.helper("exec", "true")
        self.assertEqual((quiet.returncode, quiet.stdout, quiet.stderr), (0, "", ""))

    def test_exec_reads_a_token_file_with_no_trailing_newline(self) -> None:
        (self.acc / "c.token").write_text("sk-ant-oat01-fake-c")
        (self.acc / "active").write_text("c\n")
        self.assertEqual(self.helper("exec", *PRINT_TOKEN).stdout, "sk-ant-oat01-fake-c")

    def test_exec_without_an_active_account_or_its_token_file_keeps_the_launch_value(self) -> None:
        (self.acc / "active").unlink()
        self.assertEqual(self.helper("exec", *PRINT_TOKEN, **{TOKEN: "launch-x"}).stdout, "launch-x")
        self.assertEqual(self.helper("exec", *PRINT_TOKEN).stdout, "unset")
        (self.acc / "active").write_text("gone\n")
        self.assertEqual(self.helper("exec", *PRINT_TOKEN, **{TOKEN: "launch-x"}).stdout, "launch-x")

    @unittest.skipIf(os.geteuid() == 0, "root reads a mode 000 file")
    def test_exec_with_an_unreadable_token_file_fails_without_the_launch_value(self) -> None:
        (self.acc / "a.token").chmod(0)
        proc = self.helper("exec", *PRINT_TOKEN, **{TOKEN: "launch-x"})
        self.assertEqual((proc.returncode, proc.stdout), (1, ""))
        self.assertIn("could not read the token of 'a'", proc.stderr)

    def test_exec_with_a_blank_first_line_in_the_token_file_fails(self) -> None:
        (self.acc / "c.token").write_text("\nsk-ant-oat01-fake-c\n")
        (self.acc / "active").write_text("c\n")
        proc = self.helper("exec", *PRINT_TOKEN, **{TOKEN: "launch-x"})
        self.assertEqual((proc.returncode, proc.stdout), (1, ""))
        self.assertIn("could not read the token of 'c'", proc.stderr)

    def test_exec_passes_the_exit_status_and_needs_a_command(self) -> None:
        self.assertEqual(self.helper("exec", "sh", "-c", "exit 7").returncode, 7)
        proc = self.helper("exec")
        self.assertEqual(proc.returncode, 2)
        self.assertRegex(proc.stderr, r"^usage: bin/claude-account exec \[--as <name>\] <command>")

    def test_exec_as_hands_the_named_account_token_and_an_empty_name_reads_active(self) -> None:
        (self.acc / "active").write_text("b\n")
        show = ("sh", "-c", 'printf %s "${CLAUDE_CODE_OAUTH_TOKEN-unset}"')
        self.assertEqual(self.helper("exec", "--as", "a", *show).stdout, "sk-ant-oat01-fake-a")
        self.assertEqual(self.helper("exec", "--as", "", *show).stdout, "sk-ant-oat01-fake-b")
        self.assertEqual(self.helper("exec", "--as").returncode, 2)

    def test_exec_as_a_name_with_no_stored_token_runs_nothing(self) -> None:
        proc = self.helper("exec", "--as", "ghost", *PRINT_TOKEN, **{TOKEN: "launch-x"})
        self.assertEqual((proc.returncode, proc.stdout), (1, ""))
        self.assertIn("could not read the token of 'ghost'", proc.stderr)

    @LINUX_ONLY
    def test_exec_as_reads_the_named_token_with_no_file_test_first(self) -> None:
        # A FIFO holding the token is no regular file, so a read gated on `[ -f ]` (where a token removed between a
        # caller's check and the read slips past to the launch value or the host /login) would skip it or refuse. Linux
        # opens a FIFO read-write without blocking, so the token waits in it for exec's read.
        fifo = self.acc / "piped.token"
        os.mkfifo(fifo)
        fd = os.open(fifo, os.O_RDWR)
        self.addCleanup(os.close, fd)
        os.write(fd, b"sk-ant-oat01-fake-piped\n")
        proc = self.helper("exec", "--as", "piped", *PRINT_TOKEN, **{TOKEN: "launch-x"})
        self.assertEqual((proc.returncode, proc.stdout), (0, "sk-ant-oat01-fake-piped"), proc.stderr)

    @LINUX_ONLY
    def test_exec_puts_no_token_on_a_command_line(self) -> None:
        # An `env` shim first on PATH logs its argv, which `exec env TOKEN=... cmd` would hold and /proc no longer shows.
        shims, log = self.d / "shims", self.d / "env-argv"
        shims.mkdir()
        (shims / "env").write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\nexec {shutil.which("env")} "$@"\n')
        (shims / "env").chmod(0o755)
        proc = self.helper("exec", "sh", "-c", 'cat /proc/$$/cmdline | tr "\\0" " "',
                           PATH=f"{shims}:{os.environ['PATH']}")
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("sk-ant-oat01", proc.stdout)
        self.assertNotIn("sk-ant-oat01", log.read_text() if log.exists() else "")


@LINUX_ONLY
class LauncherTests(unittest.TestCase):
    """After `use b`, each launcher's claude call gets b's token under settings precedence, not a's or the launch value."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.s = pathlib.Path(tmp.name)
        self.h = h = self.s / "home"
        for d in ("bin", "home/.claude", "home/.config/claude-accounts", "home/loam/bin", "home/.local/bin",
                  "home/distbench-lead"):
            (self.s / d).mkdir(parents=True)
        (h / "loam/bin/claude-account").symlink_to(HELPER)
        (h / ".local/bin/claude-account").symlink_to(HELPER)
        for name, text in (("claude", STUB_CLAUDE), ("gh", "#!/bin/sh\nexit 0\n")):
            (self.s / "bin" / name).write_text(text)
            (self.s / "bin" / name).chmod(0o755)
        acc = h / ".config/claude-accounts"
        for n in ("a", "b"):
            (acc / f"{n}.token").write_text(f"sk-ant-oat01-fake-{n}\n")
        (acc / "active").write_text("a\n")
        self.user = h / ".claude/settings.json"
        self.user.write_text(json.dumps({"env": {TOKEN: "sk-ant-oat01-fake-a", "KEEP": "1"}}))
        self.env = {**scrubbed(), TOKEN: "launch-x", "HOME": str(h), "PATH": f"{self.s / 'bin'}:{h / '.local/bin'}:"
                    + os.environ["PATH"]}
        use = subprocess.run([str(HELPER), "use", "b"], env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(use.returncode, 0, use.stderr)
        self.assertEqual(json.loads(self.user.read_text()), {"env": {"KEEP": "1"}})

    def tokens(self, name: str, script: str, *args: str, **extra: str) -> list[str]:
        out = self.s / f"out.{name}"
        proc = subprocess.run(["bash", "-c", script, *args], cwd=ROOT, env={**self.env, "STUB_OUT": str(out), **extra},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=120)
        self.assertTrue(out.exists(), f"{name}: no claude call reached the stub\n{proc.stdout}{proc.stderr}")
        return out.read_text().splitlines()

    def assert_active(self, name: str, got: list[str]) -> None:
        self.assertTrue(got, name)
        self.assertEqual(set(got), {"sk-ant-oat01-fake-b"}, f"{name} did not get the active account's token")

    def test_eval_replay(self) -> None:
        case = self.s / "evals/judge/c1"
        case.mkdir(parents=True)
        (case / "prompt.md").write_text("## Ticket\n\nx\n")
        (case / "expected.json").write_text('{"verdict": "pass"}\n')
        got = self.tokens("eval", '. bin/factory; EVALS_DIR=$1; run_eval judge', "bin/factory", str(self.s / "evals"),
                          FACTORY_SOURCED="1")
        self.assert_active("the eval replay", got)

    def test_login_check_and_advisor_probe(self) -> None:
        got = self.tokens("probe", ". bin/factory; precondition_lines", "bin/factory", FACTORY_SOURCED="1",
                          FACTORY_RUNS_ROOT=str(self.s / "runs"), FACTORY_STATUS_PROBE="1",
                          FACTORY_WORKER_ADVISOR="claude-opus-5-5")
        self.assertEqual(len(got), 2, "the login check and the advisor probe")
        self.assert_active("the login check and the advisor probe", got)

    def test_overnight_driver_call(self) -> None:
        text = (ROOT / "bin/overnight/driver.sh").read_text()
        wrap = re.search(r"^WRAP='.*?'$", text, re.M | re.S)
        run = re.search(r"^run\(\) \{.*?^\}$", text, re.M | re.S)
        assert wrap and run
        (self.s / "driver-run.sh").write_text(wrap.group(0) + "\n" + run.group(0) + "\n")
        got = self.tokens("driver", '. "$1/driver-run.sh"; grader_window() { :; }; watch() { :; }; account() { :; }; '
                          'O=$1/o; D=$PWD/bin/overnight; before=0; run "Read $D/protocol.md"', "_", str(self.s))
        self.assert_active("the overnight driver's call", got)
        # The account run() records is the one whose token the call gets: a switch to a after that read moves neither.
        got = self.tokens("driver-as", '. "$1/driver-run.sh"; grader_window() { :; }; watch() { :; }; account() { :; }; '
                          'active_account() { echo b; echo a > "$HOME/.config/claude-accounts/active"; }; '
                          'O=$1/o; D=$PWD/bin/overnight; before=0; run "Read $D/protocol.md"', "_", str(self.s))
        self.assert_active("the overnight driver's call after a switch past its account read", got)

    def test_limit_alarm_default_launch(self) -> None:
        line = next(x for x in (ROOT / "bin/limit-alarm").read_text().splitlines() if x.startswith("LAUNCH="))
        got = self.tokens("alarm", 'eval "$1"; eval "$LAUNCH --resume s1"', "_", line)
        self.assert_active("limit-alarm's relaunch", got)


if __name__ == "__main__":
    unittest.main()
