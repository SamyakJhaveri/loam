"""The factory grades with the sam-cc-setup version this checkout ships, or refuses.

grader_file takes judge.md and reviewer.md from the plugin cache only at the version that
cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json names. HOME is a scratch dir holding a fake
plugin cache; `bin/factory` is sourced (FACTORY_SOURCED=1) and grader_file, precondition_lines, freeze, and
cmd_next (gh, git, tmux, and its other gates stubbed as shell functions) are called directly. No `claude`, no network.
"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIPS = json.loads((ROOT / "cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json").read_text())["version"]
OLD, NEWER = "0.9.4", "99.0.0"
STUBS = "claude() { :; }; gh() { :; }; codex() { :; }; "


class GraderVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertNotIn(SHIPS, (OLD, NEWER))
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.home = self.tmp / "home"
        self.home.mkdir()

    def cache(self, version: str) -> pathlib.Path:
        """A fake installed sam-cc-setup at `version`; returns its agents dir."""
        agents = self.home / f".claude/plugins/cache/seed-skills/sam-cc-setup/{version}/agents"
        agents.mkdir(parents=True)
        for g in ("judge", "reviewer"):
            (agents / f"{g}.md").write_text(f"# {g} {version}\n")
        return agents

    def sourced(self, script: str) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_ROOT"}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), HOME=str(self.home),
                   FACTORY_RUNS_ROOT=str(self.tmp / "runs"))
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def resolve(self, prefix: str = "") -> subprocess.CompletedProcess[str]:
        return self.sourced(prefix + 'grader_file judge; echo "rc=$?"')

    def assert_refused(self, cached: str) -> None:
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), ["rc=1"], proc.stderr)
        for text in (cached, SHIPS, "claude plugin update sam-cc-setup@seed-skills"):
            self.assertIn(text, proc.stderr)

    def test_an_older_cached_version_is_refused(self) -> None:
        self.cache(OLD)
        self.assert_refused(OLD)

    def test_status_reports_the_mismatch(self) -> None:
        self.cache(OLD)
        lines = self.sourced(STUBS + "precondition_lines").stdout.splitlines()
        fails = [x for x in lines if x.startswith("  FAIL") and OLD in x and SHIPS in x]
        self.assertEqual(len(fails), 2, "\n".join(lines))  # judge and reviewer

    def test_a_run_stops_at_freeze_naming_both_versions(self) -> None:
        self.cache(OLD)
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        proc = self.sourced(f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                            "IS_FILE=1; KEY=t; BODY=x; freeze")
        self.assertEqual(proc.returncode, 4, proc.stderr)  # stopped-environment
        self.assertEqual((run / "status").read_text().strip(), "stopped-environment")
        log = (run / "factory.log").read_text()
        self.assertIn(f"EXIT stopped-environment (4): the plugin cache holds sam-cc-setup {OLD}", log)
        self.assertIn(SHIPS, log)
        self.assertFalse((run / "frozen/judge.md").exists())

    def test_a_newer_cached_version_is_neither_preferred_nor_accepted(self) -> None:
        self.cache(NEWER)
        self.assert_refused(NEWER)
        ships = self.cache(SHIPS)
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), [str(ships / "judge.md"), "rc=0"], proc.stderr)

    def test_control_the_shipped_version_resolves_beside_an_older_one(self) -> None:
        self.cache(OLD)
        ships = self.cache(SHIPS)
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), [str(ships / "judge.md"), "rc=0"], proc.stderr)
        lines = self.sourced(STUBS + "precondition_lines").stdout.splitlines()
        self.assertFalse([x for x in lines if x.startswith("  FAIL") and "judge.md" in x], "\n".join(lines))

    def test_control_graders_dir_overrides_the_cache(self) -> None:
        self.cache(OLD)
        mine = self.tmp / "agents"
        mine.mkdir()
        (mine / "judge.md").write_text("# judge, by hand\n")
        proc = self.resolve(f"GRADERS_DIR='{mine}'; ")
        self.assertEqual(proc.stdout.splitlines(), [str(mine / "judge.md"), "rc=0"], proc.stderr)

    def tick(self, *args: str, stale_on_pull: pathlib.Path | None = None) -> tuple[subprocess.CompletedProcess[str], str]:
        """One `bin/factory next` tick over a frontier of #7; returns the run and the tmux subcommands it called.
        stale_on_pull renames that cached version dir to OLD when the tick fast-forwards the checkout."""
        calls = self.tmp / "tmux.calls"
        line = f"7 {base64.b64encode(b'a ready ticket').decode()}"
        pull = f'mv "{stale_on_pull}" "{stale_on_pull.parent / OLD}"' if stale_on_pull else ":"
        proc = self.sourced(
            "LOAM_FACTORY_TOOLCHAIN=t LOAM_FACTORY_COPIER=c; "
            "assert_toolchain_env() { :; }; claude_logged_in() { :; }; target_repo() { echo o/r; }; "
            f"gh() {{ case $1 in api) echo '{line}' ;; esac; }}; "
            f'git() {{ case "$*" in *"rev-parse --abbrev-ref HEAD") echo main ;; *"merge --ff-only"*) {pull} ;; esac; }}; '
            f'tmux() {{ echo "$1" >> "{calls}"; [ "$1" != has-session ]; }}; '
            f'cmd_next {" ".join(args)}; echo "rc=$?"')
        return proc, calls.read_text() if calls.exists() else ""

    def test_next_refuses_to_launch_when_its_pull_leaves_the_cache_stale(self) -> None:
        # A launched run assigns the issue before freeze stops it, and the frontier takes only unassigned
        # issues, so every tick would burn one more ticket. The cache matched until the pull.
        proc, tmux = self.tick(stale_on_pull=self.cache(SHIPS).parent)
        self.assertEqual(proc.stdout.splitlines(), ["rc=1"], proc.stderr)
        self.assertIn(f"the plugin cache holds sam-cc-setup {OLD}, not {SHIPS}", proc.stderr)
        self.assertNotIn("new-session", tmux)

    def test_control_next_launches_with_the_shipped_version_cached(self) -> None:
        self.cache(OLD)
        self.cache(SHIPS)
        proc, tmux = self.tick()
        self.assertEqual(proc.stdout.splitlines(), ["launched #7", "rc=0"], proc.stderr)
        self.assertIn("new-session", tmux)

    def test_control_next_dry_run_skips_the_grader_gate(self) -> None:
        # A ticket's check may run next --dry-run in a worktree whose plugin.json bump is not installed yet.
        self.cache(OLD)
        proc, _ = self.tick("--dry-run")
        self.assertEqual(proc.stdout.splitlines(), ["would launch #7", "rc=0"], proc.stderr)

    def test_control_no_install_falls_back_to_the_checkout_copy(self) -> None:
        proc = self.resolve()
        checkout = ROOT / "cultivation/marketplace/sam-cc-setup/agents/judge.md"
        self.assertEqual(proc.stdout.splitlines(), [str(checkout), "rc=0"], proc.stderr)


if __name__ == "__main__":
    unittest.main()
