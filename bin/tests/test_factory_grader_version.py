"""The factory grades with the grader prompts this checkout ships, or refuses.

grader_file takes judge.md and reviewer.md from the plugin cache only when the cached file's sha256 equals the
checkout's cultivation/marketplace/sam-cc-setup/agents/ copy; the version string does not count. HOME is a scratch
dir holding a fake plugin cache; `bin/factory` is sourced (FACTORY_SOURCED=1) and grader_file, precondition_lines, freeze, and
cmd_next (gh, git, tmux, and its other gates stubbed as shell functions) are called directly. No `claude`, no network.
"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIPS = json.loads((ROOT / "cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json").read_text())["version"]
SHIPPED = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
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

    def cache(self, version: str, edited: bool = False) -> pathlib.Path:
        """A fake installed sam-cc-setup at `version` holding the checkout's judge.md and reviewer.md, or copies
        that differ from them when `edited`; returns its agents dir."""
        agents = self.home / f".claude/plugins/cache/seed-skills/sam-cc-setup/{version}/agents"
        agents.mkdir(parents=True)
        for g in ("judge", "reviewer"):
            shutil.copyfile(SHIPPED / f"{g}.md", agents / f"{g}.md")
            if edited:
                with (agents / f"{g}.md").open("a") as f:
                    f.write("\nA grader edit this checkout does not ship.\n")
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
        for text in (f"sam-cc-setup {cached}", str(SHIPPED / "judge.md"),
                     "claude plugin update sam-cc-setup@seed-skills"):
            self.assertIn(text, proc.stderr)

    def test_an_older_cached_prompt_is_refused(self) -> None:
        self.cache(OLD, edited=True)
        self.assert_refused(OLD)

    def test_a_prompt_edit_not_yet_cached_is_refused_at_the_same_version(self) -> None:
        # The version string matches, but the checkout's judge.md changed and the cache has not caught up.
        self.cache(SHIPS, edited=True)
        self.assert_refused(SHIPS)

    def test_a_version_bump_that_leaves_the_prompts_alone_still_resolves(self) -> None:
        # The checkout ships a newer plugin.json, but the cached judge.md and reviewer.md are byte-identical.
        old = self.cache(OLD)
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), [str(old / "judge.md"), "rc=0"], proc.stderr)
        lines = self.sourced(STUBS + "precondition_lines").stdout.splitlines()
        self.assertFalse([x for x in lines if x.startswith("  FAIL") and f"sam-cc-setup {OLD}" in x], "\n".join(lines))

    def test_status_reports_the_mismatch(self) -> None:
        self.cache(OLD, edited=True)
        lines = self.sourced(STUBS + "precondition_lines").stdout.splitlines()
        fails = [x for x in lines if x.startswith("  FAIL") and f"sam-cc-setup {OLD}" in x and "differs" in x]
        self.assertEqual(len(fails), 2, "\n".join(lines))  # judge and reviewer

    def test_a_run_stops_at_freeze_naming_the_cached_version_and_the_checkout_file(self) -> None:
        self.cache(OLD, edited=True)
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        proc = self.sourced(f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                            "IS_FILE=1; KEY=t; BODY=x; freeze")
        self.assertEqual(proc.returncode, 4, proc.stderr)  # stopped-environment
        self.assertEqual((run / "status").read_text().strip(), "stopped-environment")
        log = (run / "factory.log").read_text()
        self.assertIn(f"EXIT stopped-environment (4): judge.md in the plugin cache (sam-cc-setup {OLD}) differs", log)
        self.assertIn(str(SHIPPED / "judge.md"), log)
        self.assertFalse((run / "frozen/judge.md").exists())

    def test_a_newer_cached_version_with_other_prompts_is_neither_preferred_nor_accepted(self) -> None:
        self.cache(NEWER, edited=True)
        self.assert_refused(NEWER)
        ships = self.cache(SHIPS)
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), [str(ships / "judge.md"), "rc=0"], proc.stderr)

    def test_control_the_shipped_version_resolves_beside_an_older_one(self) -> None:
        self.cache(OLD, edited=True)
        ships = self.cache(SHIPS)
        proc = self.resolve()
        self.assertEqual(proc.stdout.splitlines(), [str(ships / "judge.md"), "rc=0"], proc.stderr)
        lines = self.sourced(STUBS + "precondition_lines").stdout.splitlines()
        self.assertFalse([x for x in lines if x.startswith("  FAIL") and "judge.md" in x], "\n".join(lines))

    def test_control_graders_dir_overrides_the_cache(self) -> None:
        self.cache(OLD, edited=True)
        mine = self.tmp / "agents"
        mine.mkdir()
        (mine / "judge.md").write_text("# judge, by hand\n")
        proc = self.resolve(f"GRADERS_DIR='{mine}'; ")
        self.assertEqual(proc.stdout.splitlines(), [str(mine / "judge.md"), "rc=0"], proc.stderr)

    def tick(self, *args: str, stale_on_pull: pathlib.Path | None = None) -> tuple[subprocess.CompletedProcess[str], str]:
        """One `bin/factory next` tick over a frontier of #7; returns the run and the tmux subcommands it called.
        stale_on_pull is a cached agents dir whose prompts stop matching the checkout's when the tick fast-forwards
        it. A real pull changes the checkout's copy; the stub edits the cached one, the same mismatch, so the
        test never writes to the real checkout."""
        calls = self.tmp / "tmux.calls"
        body = (ROOT / "bin/tests/fixtures/clean-ticket.md").read_text().rstrip("\n")
        line = f"7 SamyakJhaveri {base64.b64encode(body.encode()).decode()}"
        pull = f'for f in "{stale_on_pull}"/*.md; do echo edit >> "$f"; done' if stale_on_pull else ":"
        proc = self.sourced(
            "LOAM_FACTORY_TOOLCHAIN=t LOAM_FACTORY_COPIER=c; "
            "assert_toolchain_env() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; target_repo() { echo o/r; }; "
            f"gh() {{ case $1$2 in apigraphql) ;; api*) echo '{line}' ;; esac; }}; "
            f'git() {{ case "$*" in *"rev-parse --abbrev-ref HEAD") echo main ;; *"merge --ff-only"*) {pull} ;; esac; }}; '
            f'tmux() {{ echo "$1" >> "{calls}"; [ "$1" != has-session ]; }}; '
            f'cmd_next {" ".join(args)}; echo "rc=$?"')
        return proc, calls.read_text() if calls.exists() else ""

    def test_next_refuses_to_launch_when_its_pull_leaves_the_cache_stale(self) -> None:
        # A launched run assigns the issue before freeze stops it, and the frontier takes only unassigned
        # issues, so every tick would burn one more ticket. The cache matched until the pull.
        proc, tmux = self.tick(stale_on_pull=self.cache(SHIPS))
        self.assertEqual(proc.stdout.splitlines(), ["rc=1"], proc.stderr)
        self.assertIn(f"judge.md in the plugin cache (sam-cc-setup {SHIPS}) differs", proc.stderr)
        self.assertNotIn("new-session", tmux)

    def test_next_launches_after_a_version_bump_that_leaves_the_prompts_alone(self) -> None:
        self.cache(OLD)
        proc, tmux = self.tick()
        self.assertEqual(proc.stdout.splitlines(), ["launched #7", "rc=0"], proc.stderr)
        self.assertIn("new-session", tmux)

    def test_control_next_launches_with_the_shipped_version_cached(self) -> None:
        self.cache(OLD, edited=True)
        self.cache(SHIPS)
        proc, tmux = self.tick()
        self.assertEqual(proc.stdout.splitlines(), ["launched #7", "rc=0"], proc.stderr)
        self.assertIn("new-session", tmux)

    def test_control_next_dry_run_skips_the_grader_gate(self) -> None:
        # A ticket's check may run next --dry-run in a worktree whose grader edit is not installed yet.
        self.cache(OLD, edited=True)
        proc, _ = self.tick("--dry-run")
        self.assertEqual(proc.stdout.splitlines(), ["would launch #7", "rc=0"], proc.stderr)

    def test_control_no_install_falls_back_to_the_checkout_copy(self) -> None:
        proc = self.resolve()
        checkout = ROOT / "cultivation/marketplace/sam-cc-setup/agents/judge.md"
        self.assertEqual(proc.stdout.splitlines(), [str(checkout), "rc=0"], proc.stderr)


if __name__ == "__main__":
    unittest.main()
