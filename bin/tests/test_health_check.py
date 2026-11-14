"""bin/health-check rulings keeps only drafts in Samyak's exact words, and his `yes <id>` accepts one without a model call.

A stub stands in for `claude -p` (HEALTH_CLAUDE): it records each call's role and prints the envelope the test wrote.
"""

import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
GPU = "every GPU ticket says GPU: yes in its header"
CAP = "There is no spending cap of any kind"


def fixture(tmp: Path) -> Path:
    """A transcript with one message from Samyak, a rules repo that records CAP, and a config; returns the config."""
    (tmp / "p" / "proj").mkdir(parents=True)
    (tmp / "st").mkdir()
    repo = tmp / "r"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "APPROVALS.md").write_text(f"# Approvals\n\n## No spending cap\n\n{CAP}.\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", "commit", "-qm", "a"], check=True)
    records = [
        {"type": "assistant", "sessionId": "s1", "uuid": "a1", "timestamp": "2026-11-14T00:59:00.000Z",
         "message": {"role": "assistant", "content": [{"type": "text", "text": "Should GPU tickets say so?"}]}},
        {"type": "user", "sessionId": "s1", "uuid": "u1", "parentUuid": "a1", "timestamp": "2026-11-14T01:00:00.000Z",
         "message": {"role": "user", "content": f"From now on {GPU}. {CAP}, as before."}},
    ]
    (tmp / "p" / "proj" / "s1.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    stub = tmp / "stub"
    stub.write_text('#!/bin/sh\necho "$HEALTH_ROLE" >> "$T/calls"\ncat "$T/$HEALTH_ROLE.json"\n')
    stub.chmod(0o755)
    cfg = tmp / "c.json"
    cfg.write_text(json.dumps({"state": str(tmp / "st"), "loam": str(ROOT), "hosts": {"mac": {"transcripts": [f"{tmp}/p/*"]}},
                               "rules": {"repo": str(repo), "ref": "HEAD", "path": "APPROVALS.md"}}))
    return cfg


def reply(tmp: Path, result: str) -> None:
    (tmp / "rulings.json").write_text(json.dumps({"type": "result", "subtype": "success", "is_error": False,
                                                  "result": result}))


def draft(quote: str, audience: str = "worker") -> dict:
    return {"quote": quote, "ref": "mac:s1:u1", "rule": f"rule for {quote}", "audience": audience,
            "supersedes": "none", "why_ruling": "w"}


def run(tmp: Path, cfg: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "T": str(tmp), "HEALTH_CLAUDE": str(tmp / "stub")}
    return subprocess.run([str(ROOT / "bin" / "health-check"), "--config", str(cfg), "rulings"], env=env,
                          capture_output=True, text=True)


def store(tmp: Path) -> list:
    p = tmp / "st" / "rulings.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def test_only_his_exact_unrecorded_words_become_a_draft(tmp_path):
    cfg = fixture(tmp_path)
    mmdd = dt.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m%d")
    seeded = {"id": f"R{mmdd}-3", "status": "pending", "quote": "an earlier ruling",
              "ref": {"id": "mac:s0:u0", "host": "mac", "session": "s0", "record": "u0", "file": "/x/s0.jsonl",
                      "line": 1, "ts": "2026-11-13T00:00:00Z"},
              "kind": "typed", "question": None, "rule": "r", "audience": "lead", "supersedes": "none",
              "repeat_of": "none", "why_ruling": "w"}
    (tmp_path / "st" / "rulings.jsonl").write_text(json.dumps(seeded) + "\n")

    # A limit line returned as a success is a failed call: no record, and the message is read again next run.
    reply(tmp_path, "You've hit your 5-hour limit, resets 9:20pm (America/Los_Angeles)")
    assert run(tmp_path, cfg).returncode != 0
    assert store(tmp_path) == [seeded]

    reply(tmp_path, json.dumps({"drafts": [draft(GPU), draft(CAP), draft("GPU tickets must declare the GPU")],
                                "repeats": []}))
    assert run(tmp_path, cfg).returncode == 0
    new = store(tmp_path)[1:]
    assert [(r["id"], r["status"], r["quote"], r["ref"]["id"], r["ref"]["line"]) for r in new] == \
        [(f"R{mmdd}-4", "pending", GPU, "mac:s1:u1", 2)]
    listing = (tmp_path / "st" / "rulings-pending.md").read_text().splitlines()
    assert f"  - Reply: yes R{mmdd}-3" in listing and f"  - Reply: yes R{mmdd}-4" in listing


def test_yes_accepts_a_draft_without_a_model_call_and_queues_its_lesson_once(tmp_path):
    cfg = fixture(tmp_path)
    reply(tmp_path, json.dumps({"drafts": [draft(GPU)], "repeats": []}))
    assert run(tmp_path, cfg).returncode == 0
    [rec] = store(tmp_path)
    yes = {"type": "user", "sessionId": "s1", "uuid": "u2", "parentUuid": "u1", "timestamp": "2026-11-14T02:00:00.000Z",
           "message": {"role": "user", "content": f"YES {rec['id'].lower()}"}}
    with open(tmp_path / "p" / "proj" / "s1.jsonl", "a") as fh:
        fh.write(json.dumps(yes) + "\n")

    assert run(tmp_path, cfg).returncode == 0
    assert run(tmp_path, cfg).returncode == 0
    assert (tmp_path / "calls").read_text().split() == ["rulings"]
    assert [r["status"] for r in store(tmp_path)] == ["accepted"]
    queue = [json.loads(line) for line in (tmp_path / "st" / "lessons-queue.jsonl").read_text().splitlines()]
    assert queue == [{"key": rec["id"], "provenance": "ruling, mac s1 line 2", "text": f"rule for {GPU}"}]
    listing = (tmp_path / "st" / "rulings-pending.md").read_text()
    assert "## Accepted: record in APPROVALS" in listing and f"Reply: yes {rec['id']}" not in listing
