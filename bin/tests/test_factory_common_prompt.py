"""The worker prompt asks the worker to carry each behavior done check into a committed test (#466).

Done checks run only inside the factory round; after merge only committed tests and bin/check guard the
behavior. The test sources bin/factory (FACTORY_SOURCED=1), copies the real bin/factory.d/_common.md to the
run's frozen/_common.md, and calls the real build_worker_prompt, so it reads the prompt a Claude worker gets.
"""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
