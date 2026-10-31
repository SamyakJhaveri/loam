"""bin/hook_lint.py on temp hook dirs: the done-checks' planted hook, quoting cases, and the event rule."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin/hook_lint.py"

PLANTED = '#!/bin/bash\ninput=$(cat)\nrm -rf $DIR/cache\neval "$input"\necho "{\\"decision\\": \\"block\\"}"\n'
# Lines 2 to 6 and the heredoc body on line 11 must not count; lines 7 to 9 and 13 must.
RM_CASES = """#!/bin/bash
rm -rf "$DIR"/cache
rm -f "${X}"
rm -f '$X'
rm -f \\$X
echo "rm $X"
x="$(rm $y)"
rm -f $X
rm -f ${X}
cat <<'DOC'
rm $after 2>/dev/null; rm "$ok"
DOC
rm $after 2>/dev/null; rm "$ok"
"""


def lint(script: str, events: list[str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as d:
        (pathlib.Path(d) / "h.sh").write_text(script, encoding="utf-8")
        hooks = {e: [{"hooks": [{"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/h.sh -x"}]}]
                 for e in events}
        (pathlib.Path(d) / "settings.json").write_text(json.dumps({"hooks": hooks}), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), f"{d}/settings.json", d],
                              capture_output=True, text=True, check=False)


def found(out: str) -> list[str]:
    return [line.split()[1].rsplit("/", 1)[-1] + " " + line.split()[2] for line in out.splitlines()]


class HookLintTest(unittest.TestCase):
    def test_flags_planted_hook(self) -> None:
        r = lint(PLANTED, ["SessionEnd"])
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(found(r.stdout), ["h.sh:3 unquoted-rm", "h.sh:4 eval-input", "h.sh:5 block-on-nonblocking"])

    def test_block_allowed_where_any_event_can_block(self) -> None:
        r = lint(PLANTED, ["SessionEnd", "Stop"])
        self.assertNotIn("block-on-nonblocking", r.stdout)

    def test_eval_without_stdin_passes(self) -> None:
        r = lint('#!/bin/bash\neval "$(ssh-agent -s)"\n', ["SessionStart"])
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_rm_quoting_cases(self) -> None:
        r = lint(RM_CASES, ["Stop"])
        self.assertEqual(found(r.stdout), [f"h.sh:{n} unquoted-rm" for n in (7, 8, 9, 13)])

    def test_seed_hooks_pass(self) -> None:
        r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT / "seed/.claude/settings.json"),
                            str(ROOT / "seed/.claude/hooks")], capture_output=True, text=True, check=False)
        self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
