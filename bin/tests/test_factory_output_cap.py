"""The worker's Bash output is capped at 20,000 characters inline (ASK-KARPATHY item D).

Claude Code's `bashOutputMaxChars` setting sizes how much of a command's output reaches the model inline; a larger
result arrives as the path of a file saved in the session directory with a preview of its first 2,000 characters
(https://code.claude.com/docs/en/tools-reference.md#output-limits; default about 30,000, maximum 128,000). The key
beats the BASH_MAX_OUTPUT_LENGTH env var, so it is the one the factory sets. Checks the source settings and the real
freeze path over a user tier that raises the cap, sourced with FACTORY_SOURCED=1 as in test_factory_auto_memory.py.
No network or Claude call.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
CAP = 20000


class OutputCapTests(unittest.TestCase):
    def test_worker_settings_cap_bash_output(self) -> None:
        settings = json.loads((ROOT / "bin/factory.d/worker-settings.json").read_text())
        self.assertEqual(settings.get("bashOutputMaxChars"), CAP)

    def test_frozen_worker_settings_keep_the_cap_over_a_user_tier(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        user = top / "user-settings.json"
        user.write_text(json.dumps({"bashOutputMaxChars": 128000}))
        run = top / "run"
        (run / "frozen").mkdir(parents=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in ("RUN", "LOG")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(top / "runs"),
                   CLAUDE_SETTINGS_FILE=str(user))
        script = (f"RUN='{run}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                  f"DECISIONS=\"$RUN/decisions.md\"; GRADERS_DIR='{GRADERS}'; IS_FILE=1; KEY=t; BODY=x; "
                  "freeze && check_frozen && echo frozen")
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.stdout.strip(), "frozen", proc.stderr)
        settings = json.loads((run / "frozen" / "worker-settings.json").read_text())
        self.assertEqual(settings.get("bashOutputMaxChars"), CAP)


if __name__ == "__main__":
    unittest.main()
