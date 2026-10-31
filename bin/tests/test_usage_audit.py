"""bin/usage-audit on planted transcript trees: a message counts by its latest record, history copied into a
resumed session stays with the session that made the request whichever file sorts first, a message with
no final record is reported on stderr as a floor, and a path that is not a directory fails. With --codex a
session's row is its last cumulative token_count in the window less the one before start, or less a fork's
copied parent events."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/usage-audit"


def asst(mid: str, out: int, ref: str | None = None, stop: str | None = "end_turn") -> dict:
    rec = {"type": "assistant", "timestamp": "2026-10-29T10:00:00.000Z",
           "message": {"id": mid, "model": "m", "stop_reason": stop, "usage": {"input_tokens": 3, "output_tokens": out}}}
    if ref:
        rec["requestRef"] = ref
    return rec


def run(files: dict[str, list[dict]], root: str = "p") -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        for rel, recs in files.items():
            path = pathlib.Path(tmp, "p", rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
        p = subprocess.run([sys.executable, str(SCRIPT), str(pathlib.Path(tmp, root)), "2026-10-29T00:00:00Z", "h"],
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr


def rows(out: str) -> dict[str, list[str]]:
    """session -> its row's turns and output."""
    return {f[2]: [f[7], f[11]] for f in (line.split("\t") for line in out.splitlines())}


class UsageAuditTest(unittest.TestCase):
    def test_latest_record_counts(self) -> None:
        rc, out, err = run({"proj/s1111111.jsonl": [asst("m1", 5, stop=None), asst("m1", 50)]})
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(rows(out), {"s1111111": ["1", "50"]})

    def test_copied_history_stays_with_its_session(self) -> None:
        own = [{"type": "api-request", "id": "r1"}, asst("m1", 50, "r1")]
        copy = [asst("m1", 50, "r1"), {"type": "api-request", "id": "r2"}, asst("m2", 7, "r2")]
        for first, last in (("aaaaaaaa", "bbbbbbbb"), ("bbbbbbbb", "aaaaaaaa")):
            with self.subTest(original=first):
                rc, out, _ = run({f"proj/{first}.jsonl": own, f"proj/{last}.jsonl": copy})
                self.assertEqual(rc, 0)
                self.assertEqual(rows(out), {first: ["1", "50"], last: ["1", "7"]})

    def test_missing_final_record_is_a_floor_on_stderr(self) -> None:
        rc, out, err = run({"proj/s1111111.jsonl": [asst("m1", 3, stop=None), asst("m2", 9)]})
        self.assertEqual(rc, 0)
        self.assertEqual(rows(out), {"s1111111": ["2", "12"]})
        self.assertIn("1 of 2 messages have no final usage record", err)

    def test_not_a_directory_fails(self) -> None:
        rc, out, err = run({"proj/s1111111.jsonl": [asst("m1", 5)]}, root="p/proj/s1111111.jsonl")
        self.assertNotEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertIn("not a directory", err)


def tc(ts: str, inp: int, cached: int, out: int) -> dict:
    return {"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "info": {
        "total_token_usage": {"input_tokens": inp, "cached_input_tokens": cached, "output_tokens": out}}}}


def meta(ts: str, sid: str, **extra) -> dict:
    return {"timestamp": ts, "type": "session_meta", "payload": {"id": sid, **extra}}


def codex(files: dict[str, list[dict]]) -> dict[str, list[str]]:
    """session -> its row from --codex over the planted rollouts, window from 10:00."""
    with tempfile.TemporaryDirectory() as tmp:
        for rel, recs in files.items():
            pathlib.Path(tmp, rel).write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
        p = subprocess.run([sys.executable, str(SCRIPT), "--codex", tmp, "2026-10-29T10:00:00Z", "h"],
                           capture_output=True, text=True, check=True)
        return {f[2]: f for f in (line.split("\t") for line in p.stdout.splitlines())}


class CodexTest(unittest.TestCase):
    def test_cumulative_events_are_not_summed_and_prior_usage_is_subtracted(self) -> None:
        rows = codex({"rollout-a.jsonl": [meta("2026-10-29T09:00:00Z", "s1", cwd="/w/proj", source="exec"),
                                          tc("2026-10-29T09:30:00Z", 100, 20, 100),
                                          tc("2026-10-29T10:00:01Z", 250, 40, 300),
                                          tc("2026-10-29T10:00:01Z", 250, 40, 300),
                                          tc("2026-10-29T10:00:02Z", 400, 60, 500)]})
        self.assertEqual(rows["s1"], ["h", "proj", "s1", "codex", "exec", "-", "-", "2", "260", "0", "40", "400"])

    def test_fork_copies_of_parent_events_are_baseline(self) -> None:
        rows = codex({"rollout-f.jsonl": [meta("2026-10-29T11:00:00.100Z", "f1", forked_from_id="p1",
                                               source={"subagent": "review"}),
                                          tc("2026-10-29T11:00:00.101Z", 900, 0, 900),
                                          tc("2026-10-29T11:00:05Z", 1000, 50, 950)]})
        self.assertEqual(rows["f1"][4:], ["review", "-", "-", "1", "50", "0", "50", "50"])

    def test_sessions_sharing_a_prefix_stay_apart(self) -> None:
        rows = codex({f"rollout-{n}.jsonl": [meta("2026-10-29T10:00:00Z", f"01a13bd1-000{n}"),
                                             tc("2026-10-29T10:00:01Z", 10, 0, n)] for n in (1, 2)})
        self.assertEqual({k: v[11] for k, v in rows.items()}, {"01a13bd1-0001": "1", "01a13bd1-0002": "2"})


if __name__ == "__main__":
    unittest.main()
