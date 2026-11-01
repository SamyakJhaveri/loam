"""Every factory Codex call runs under a CODEX_HOME of the factory's own, with the model and effort named (#543, #490).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real worker_round and run_codex_review run with a fake `codex` on
PATH that records its argv, its CODEX_HOME, and every file under that home. HOME is a fake whose ~/.codex holds an
AGENTS.md, a rules file, hooks and a config.toml naming another model, as the runner's does; none of them may reach
the call, only a link to its auth.json. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG",
             "CODEX_HOME")

FAKE_CODEX = """#!/usr/bin/env python3
import json, os, pathlib, sys
a = sys.argv[1:]
home = os.environ.get("CODEX_HOME", "")
files = sorted(str(p.relative_to(home)) for p in pathlib.Path(home).rglob("*")) if home else []
json.dump({"argv": a, "home": home, "files": files}, open(os.environ["FAKE_SEEN"], "w"))
if "-o" in a:
    open(a[a.index("-o") + 1], "w").write('{"verdict":"approve","summary":"ok","findings":[],"next_steps":[]}')
print('{"type":"turn.completed","usage":{}}')
"""


def git(*args: str, cwd: pathlib.Path) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                   capture_output=True)


class CodexHomeTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.wt = self.top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "factory/7", cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        self.run_dir = self.top / "run"
        frozen = self.run_dir / "frozen"
        frozen.mkdir(parents=True)
        (self.run_dir / "tasks").mkdir()
        for name in ("_common.md", "unattended.md"):
            (frozen / name).write_text("")
        (frozen / "worker-settings.json").write_text("{}")
        (frozen / "codex-review.prompt.md").write_text("Review the diff against <base>.\n")
        shutil.copy(ROOT / "bin/factory.d/review-output.schema.json", frozen / "review-output.schema.json")
        (self.run_dir / "base.sha").write_text("HEAD\n")
        self.home = self.top / "home"
        codex = self.home / ".codex"
        (codex / "rules").mkdir(parents=True)
        (codex / "AGENTS.md").write_text("Ask only when the task is ambiguous.\n")
        (codex / "rules" / "default.rules").write_text('prefix_rule(pattern=["rm"], decision="forbidden")\n')
        (codex / "hooks.json").write_text("{}\n")
        (codex / "config.toml").write_text('model = "operator-model"\ndefault_permissions = "loam-auto"\n')
        (codex / "auth.json").write_text("{}\n")
        self.bin = self.top / "bin"
        self.bin.mkdir()
        (self.bin / "codex").write_text(FAKE_CODEX)
        (self.bin / "codex").chmod(0o755)
        self.seen = self.top / "seen.json"

    def call(self, setup: str, call: str) -> dict:
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; LOG=\"$RUN/factory.log\"; KEY=7; IS_FILE=1\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"\n'
            'touch "$LEDGER" "$DAILY" "$DECISIONS"; date -u +%s > "$RUN/launched"\n'
            "BODY='## Worker'; apply_caps; TIMEOUT_G=(); CODEX_REVIEW_BLOCKED=0\n"
            f"CODEX_PATH='{self.bin}'; {setup}\n{call}; echo returned:$?\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        proc = subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "HOME": str(self.home),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "FAKE_SEEN": str(self.seen),
                                   "CLAUDE_CONFIG_DIR": str(self.top / "cc"), "PATH": f"{self.bin}:{env['PATH']}"},
                              capture_output=True, text=True, check=False, timeout=60)
        self.assertTrue(self.seen.exists(), proc.stderr)
        return json.loads(self.seen.read_text())

    def assert_sealed(self, seen: dict, effort: str) -> None:
        home = pathlib.Path(seen["home"])
        self.assertTrue(home.is_relative_to(self.run_dir), seen["home"])
        self.assertEqual(seen["files"], ["auth.json", "config.toml"])  # no AGENTS.md, rules, hooks or memories
        self.assertEqual((home / "auth.json").resolve(), (self.home / ".codex/auth.json").resolve())
        self.assertIn('model = "gpt-6.1-sol"', (home / "config.toml").read_text())
        a = seen["argv"]
        pairs = [a[i:i + 2] for i in range(len(a) - 1)]
        self.assertIn(["-m", "gpt-6.1-sol"], pairs)
        self.assertIn(["-c", f"model_reasoning_effort={effort}"], pairs)

    def test_codex_worker_gets_the_factory_home_and_the_ticket_effort(self) -> None:
        self.assert_sealed(self.call("WORKER_KIND=codex; WORKER_EFFORT=xhigh", "worker_round 1"), "xhigh")

    def test_codex_review_gets_the_factory_home_and_the_grader_effort(self) -> None:
        self.assert_sealed(self.call("WORKER_KIND=claude; WORKER_EFFORT=low; GRADER_EFFORT=medium",
                                     "run_codex_review 1"), "medium")


if __name__ == "__main__":
    unittest.main()
