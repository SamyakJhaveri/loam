"""bin/usage-audit on planted transcript trees: a message counts by its latest record, history copied into a
resumed session stays with the session that made the request whichever file sorts first, a message with
no final record is reported on stderr as a floor, and a path that is not a directory fails."""

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


if __name__ == "__main__":
    unittest.main()
