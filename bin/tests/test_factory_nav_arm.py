"""Every ledger line carries `nav_arm`: the launch's arm, else `base` (#166, kept by #613 when nav01-metrics.py went).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real record writes ledger lines from a fake result file.
No network, no `claude`.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OPUS = "claude-opus-5-5"


class NavArmTests(unittest.TestCase):
    def test_record_writes_the_launch_arm_else_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            res, led = top / "res.json", top / "ledger.jsonl"
            res.write_text(json.dumps({"total_cost_usd": 0.5, "duration_ms": 1000, "num_turns": 5,
                                       "permission_denials": [], "subtype": "success",
                                       "usage": {"input_tokens": 10, "output_tokens": 20}}))
            base = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in ("REPO", "RUN", "LOG")}
            script = (f". bin/factory\nRUN='{top}'; LOG=/dev/null; LEDGER='{led}'; DAILY='{top}/daily.jsonl'; KEY=7\n"
                      f"FACTORY_NAV_ARM=C record 1 worker {OPUS} '{res}'\nrecord 2 judge {OPUS} '{res}'")
            proc = subprocess.run(["bash", "-c", script], cwd=ROOT, capture_output=True, text=True, check=False,
                                  env={**base, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT)})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            arms = {x["role"]: x["nav_arm"] for x in map(json.loads, led.read_text().splitlines())}
            self.assertEqual(arms, {"worker": "C", "judge": "base"})


if __name__ == "__main__":
    unittest.main()
