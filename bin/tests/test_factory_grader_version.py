"""The factory grades with the sam-cc-setup version this checkout ships, or refuses.

grader_file takes judge.md and reviewer.md from the plugin cache only at the version that
cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json names. HOME is a scratch dir holding a fake
plugin cache; `bin/factory` is sourced (FACTORY_SOURCED=1) and grader_file, precondition_lines, and freeze
are called directly. No `claude`, no network.
"""

from __future__ import annotations

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

    def test_control_no_install_falls_back_to_the_checkout_copy(self) -> None:
        proc = self.resolve()
        checkout = ROOT / "cultivation/marketplace/sam-cc-setup/agents/judge.md"
        self.assertEqual(proc.stdout.splitlines(), [str(checkout), "rc=0"], proc.stderr)


if __name__ == "__main__":
    unittest.main()
