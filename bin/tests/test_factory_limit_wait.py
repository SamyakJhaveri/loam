"""limit_wait sleeps until the reset a usage-limit reply names, with GNU date or BSD date (macOS).

Each case sources bin/factory (FACTORY_SOURCED=1) with sleep, log, set_status and limit_switch stubbed, feeds
limit_wait a reply that resets about two hours ahead, and reads the seconds it would sleep; the fallback is 1200.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import tempfile
import time
import unittest
import zoneinfo

import bsd_shapes

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
ZONE = "America/Los_Angeles"


class LimitWaitTests(unittest.TestCase):
    def slept(self, reset: str, path: str, top: pathlib.Path) -> int:
        result = top / "result.json"
        reply = f"You've hit your session limit - resets {reset} ({ZONE})"
        result.write_text(json.dumps({"is_error": True, "result": reply}))
        (top / "launched").write_text(f"{int(time.time())}\n")
        script = (f". bin/factory\nRUN='{top}'; LOG='{top}/factory.log'; MAX_HOURS=9\n"
                  "limit_switch() { return 1; }; set_status() { :; }; log() { :; }; sleep() { echo \"slept $1\"; }\n"
                  f"limit_wait '{result}'")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env={**base, "FACTORY_SOURCED": "1", "PATH": path},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        self.assertTrue(proc.stdout.startswith("slept "), proc.stdout + proc.stderr)
        return int(proc.stdout.split()[1])

    def test_sleeps_until_the_named_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            target = (datetime.datetime.now(zoneinfo.ZoneInfo(ZONE)) + datetime.timedelta(hours=2)).replace(
                second=0, microsecond=0)
            hour, ap = target.hour % 12 or 12, target.strftime("%p").lower()
            for name, path in (("host date", os.environ["PATH"]), ("BSD date", bsd_shapes.path(top / "bin"))):
                for reset, at in ((f"{hour}:{target:%M}{ap}", target), (f"{hour}{ap}", target.replace(minute=0))):
                    with self.subTest(date=name, reset=reset):
                        want = int(at.timestamp() - time.time()) + 60
                        self.assertAlmostEqual(self.slept(reset, path, top), want, delta=5)


if __name__ == "__main__":
    unittest.main()
