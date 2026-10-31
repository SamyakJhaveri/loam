"""The ledger records the models that served each call, and status warns on an unexpected one (#390).

`bin/factory` is sourced (FACTORY_SOURCED=1): the real record writes ledger lines from fake result files, and the
real cmd_status reads hand-written ledgers, with gh and precondition_lines stubbed. No network, no `claude`.
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


def sourced(script: str, **env: str) -> subprocess.CompletedProcess[str]:
    base = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_") and k not in ("REPO", "RUN", "LOG")}
    return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                          env={**base, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), **env},
                          capture_output=True, text=True, check=False)


class ServedModelsTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)

    def record(self, result: object | None) -> dict:
        """The ledger line record writes for `result` (None: no result file, so the jq -n fallback)."""
        res = self.top / "result.json"
        if result is not None:
            res.write_text(json.dumps(result))
        led = self.top / "ledger.jsonl"
        led.unlink(missing_ok=True)
        proc = sourced(f"RUN='{self.top}'; LOG=/dev/null; LEDGER='{led}'; DAILY='{self.top}/daily.jsonl'; KEY=7\n"
                       f"record 1 worker {OPUS} '{res}'")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(led.read_text())

    def test_record_writes_the_sorted_modelusage_keys(self) -> None:
        usage = {OPUS: {"outputTokens": 9}, "claude-haiku-4-5": {"outputTokens": 3}}
        line = self.record({"type": "result", "total_cost_usd": 1, "modelUsage": usage})
        self.assertEqual(line["served_models"], ["claude-haiku-4-5", OPUS])
        self.assertEqual(self.record({"type": "result", "total_cost_usd": 1})["served_models"], [])
        self.assertEqual(self.record(None)["served_models"], [])
        # A modelUsage that is not an object must not drop the line to the zeroed fallback.
        line = self.record({"type": "result", "total_cost_usd": 2, "modelUsage": "x"})
        self.assertEqual((line["served_models"], line["cost_usd"]), ([], 2))

    def status_warns(self, runs: dict[str, list[str]], **env: str) -> list[str]:
        """The WARN lines cmd_status prints for runs named `ticket` with ledger `lines`."""
        root = self.top / "runs"
        for ticket, lines in runs.items():
            d = root / ticket / "aaaaaaaa"
            d.mkdir(parents=True)
            (d / "status").write_text("pr-opened\n")
            (d / "ledger.jsonl").write_text("".join(x + "\n" for x in lines))
        proc = sourced(f"precondition_lines() {{ :; }}; gh() {{ return 1; }}; RUNS_ROOT='{root}'; "
                       f"MAIN_CHECKOUT='{self.top}'; cmd_status", FACTORY_RUNS_ROOT=str(root), **env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return [x.strip() for x in proc.stdout.splitlines() if "WARN" in x]

    def test_status_warns_only_on_a_model_nothing_asked_for(self) -> None:
        def line(model: str | None, served: list | None) -> str:
            row: dict = {"round": 1, "role": "worker", "model": model, "cost_usd": 1}
            if served is not None:
                row["served_models"] = served
            return json.dumps(row)

        haiku = [line(OPUS, [OPUS, "claude-haiku-4-5"])]
        runs = {
            "haiku": haiku,
            "opus": [line(OPUS, [OPUS])],
            "onem": [line(OPUS, [f"{OPUS}[1m]"])],
            "old": [line(OPUS, None)],
            # A launch-time override: the line's own requested model served it.
            "override": [line("claude-fable-5-1", ["claude-fable-5-1"]), line(None, [])],
            # A grader line (model null) served by the worker row's model still warns: no union across lines.
            "leak": [line("claude-fable-5-1", ["claude-fable-5-1"]), line(None, ["claude-fable-5-1"])],
            "malformed": ["not json{", *haiku],
        }
        self.assertEqual(self.status_warns(runs), [
            "WARN haiku/aaaaaaaa served by claude-haiku-4-5",
            "WARN leak/aaaaaaaa served by claude-fable-5-1",
            "WARN malformed/aaaaaaaa served by claude-haiku-4-5",
        ])

    def test_an_empty_advisor_still_warns(self) -> None:
        warns = self.status_warns({"haiku": [json.dumps({"model": OPUS, "served_models": ["claude-haiku-4-5"]})]},
                                  FACTORY_WORKER_ADVISOR="")
        self.assertEqual(warns, ["WARN haiku/aaaaaaaa served by claude-haiku-4-5"])


if __name__ == "__main__":
    unittest.main()
