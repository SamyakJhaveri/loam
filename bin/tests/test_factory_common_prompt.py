"""The worker prompt asks the worker to carry each behavior done check into a committed test (#466), and a Claude
worker to read the pstack router at the path bin/factory resolves from the seed-skills marketplace.

Done checks run only inside the factory round; after merge only committed tests and bin/check guard the
behavior. The test sources bin/factory (FACTORY_SOURCED=1), copies the real bin/factory.d/_common.md to the
run's frozen/_common.md, and calls the real build_worker_prompt, so it reads the prompt a Claude worker gets.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TICKET = """# fixture
Brief:
A fixture.
Blocked by: none

## Goal and why
A fixture.

## Done checks
```done-checks
[ -f x ] && pass a || fail a "no x"
```

## Worker
worker: claude
"""


class CommonPromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def prompt(self) -> str:
        run = self.tmp / "run"
        shutil.rmtree(run, ignore_errors=True)
        (run / "frozen").mkdir(parents=True)
        shutil.copy(ROOT / "bin/factory.d/_common.md", run / "frozen/_common.md")
        ticket = self.tmp / "t.md"
        ticket.write_text(TICKET)
        script = '. bin/factory; RUN=$1; WORKER_KIND=claude; BODY=$(cat "$2"); round=1; build_worker_prompt 1'
        proc = subprocess.run(["bash", "-c", script, "_", str(run), str(ticket)], cwd=ROOT,
                              env={**os.environ, "FACTORY_SOURCED": "1", "HOME": str(self.tmp)},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return pathlib.Path(proc.stdout.strip()).read_text()

    def test_prompt_asks_for_a_committed_test_of_each_behavior_done_check(self) -> None:
        lines = [line for line in self.prompt().splitlines() if re.search(r"committed test", line, re.I)]
        self.assertEqual(len(lines), 1, lines)
        line = lines[0]
        self.assertRegex(line, re.compile(r"done check", re.I))
        self.assertRegex(line, re.compile(r"behavior", re.I))
        self.assertIn("bin/tests/", line)

    def router(self) -> pathlib.Path:
        # The seed-skills marketplace as Claude Code records a directory source, with the router under it.
        market = self.tmp / "market"
        router = market / "sam-cc-setup/skills/pstack/SKILL.md"
        router.parent.mkdir(parents=True)
        router.write_text("A router.\n")
        known = self.tmp / ".claude/plugins/known_marketplaces.json"
        known.parent.mkdir(parents=True)
        known.write_text(json.dumps({"seed-skills": {"source": {"source": "directory", "path": str(market)},
                                                     "installLocation": str(market)}}))
        return router

    def test_prompt_names_the_resolved_router_once_for_a_claude_worker(self) -> None:
        router = self.router()
        text = self.prompt()
        self.assertNotIn("<router>", text)
        lines = [line for line in text.splitlines() if str(router) in line]
        self.assertEqual(len(lines), 1, lines)
        line = lines[0]
        self.assertRegex(line, re.compile(r"Claude worker.*before a task.*follows the method it picks", re.I))
        self.assertRegex(line, re.compile(r"Codex worker skips", re.I))
        self.assertRegex(line, re.compile(r"subagent rule wins", re.I))

    def test_a_missing_router_tells_the_worker_to_skip_the_line(self) -> None:
        text = self.prompt()
        self.assertNotIn("<router>", text)
        (line,) = [line for line in text.splitlines() if "pstack router" in line]
        self.assertIn("missing on this host, so skip this line", line)
        self.router().unlink()  # a marketplace that no longer holds the router
        self.assertIn("missing on this host, so skip this line", self.prompt())


if __name__ == "__main__":
    unittest.main()
