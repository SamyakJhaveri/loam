"""seed/.claude/hooks/fable-session-brief.sh: the injection advice is measured for Fable 5.2 only.

The fable-prompting skill's "Never paste these" list comes from a Fable 5.2 capture. Another Fable version gets the
common judgment rules and a line saying its injection was not measured; a non-Fable model gets nothing.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import unittest

HOOK = pathlib.Path(__file__).resolve().parents[2] / "seed/.claude/hooks/fable-session-brief.sh"


def brief(payload: dict[str, str]) -> str:
    proc = subprocess.run(["bash", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
                          check=True, timeout=30)
    return proc.stdout


class FableSessionBriefTests(unittest.TestCase):
    def test_fable_5_2_gets_the_measured_do_not_paste_line(self) -> None:
        out = brief({"hook_event_name": "SessionStart", "model": "claude-fable-5-2"})
        self.assertIn("Do not paste the finishing block", out)
        self.assertNotIn("not measured", out)

    def test_another_fable_version_gets_the_rules_but_no_injection_claim(self) -> None:
        out = brief({"hook_event_name": "PostModelSwitch", "to_model": "claude-fable-5-1"})
        self.assertIn("Judgment rules this harness does not inject", out)
        self.assertNotIn("Do not paste", out)
        self.assertIn("not measured", out)

    def test_a_non_fable_model_gets_nothing(self) -> None:
        self.assertEqual(brief({"hook_event_name": "SessionStart", "model": "claude-opus-5-5"}), "")


if __name__ == "__main__":
    unittest.main()
