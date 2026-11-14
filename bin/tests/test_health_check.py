"""bin/health-check rulings keeps only drafts in Samyak's exact words, turns a restated rule into a ticket draft, and
his `yes <id>` accepts one without a model call; tick runs it when due and steps aside while another run holds the lock.

A stub stands in for `claude -p` (HEALTH_CLAUDE): it records each call's role and prints the envelope the test wrote.
"""

import datetime as dt
import fcntl
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


def reply(tmp: Path, result: str, role: str = "rulings") -> None:
    (tmp / f"{role}.json").write_text(json.dumps({"type": "result", "subtype": "success", "is_error": False,
                                                  "result": result}))


def draft(quote: str, audience: str = "worker") -> dict:
    return {"quote": quote, "ref": "mac:s1:u1", "rule": f"rule for {quote}", "audience": audience,
            "supersedes": "none", "why_ruling": "w"}


def run(tmp: Path, cfg: Path, command: str = "rulings") -> subprocess.CompletedProcess:
    env = {**os.environ, "T": str(tmp), "HEALTH_CLAUDE": str(tmp / "stub")}
    return subprocess.run([str(ROOT / "bin" / "health-check"), "--config", str(cfg), command], env=env,
                          capture_output=True, text=True)


def store(tmp: Path) -> list:
    p = tmp / "st" / "rulings.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def test_only_his_exact_unrecorded_words_become_a_draft_and_a_restated_rule_a_ticket(tmp_path):
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

    # CAP is already in the rules file: dropped as a draft, kept as a restated rule.
    reply(tmp_path, json.dumps({"drafts": [draft(GPU), draft(CAP), draft("GPU tickets must declare the GPU")],
                                "repeats": [{"ref": "mac:s1:u1", "quote": CAP, "recorded_in": "No spending cap",
                                             "rule": "No spending cap of any kind."}]}))
    ticket = {"repo": "loam", "title": "Check that no spending cap returns", "source_line": "- ruling-repeat"}
    reply(tmp_path, json.dumps({**ticket, "body": "# Check that no spending cap returns\nBody."}), "learn")
    assert run(tmp_path, cfg).returncode == 0
    new = store(tmp_path)[1:]
    assert [(r["id"], r["status"], r["quote"], r["ref"]["id"], r["ref"]["line"], r["repeat_of"]) for r in new] == \
        [(f"R{mmdd}-4", "pending", GPU, "mac:s1:u1", 2, "none"),
         (f"R{mmdd}-5", "recorded", CAP, "mac:s1:u1", 2, "No spending cap")]
    learn = tmp_path / "st" / "drafts" / f"R{mmdd}-5" / "learn"
    assert json.loads((learn / "draft.json").read_text()) == ticket
    assert (learn / "draft.md").read_text() == "# Check that no spending cap returns\nBody.\n"
    listing = (tmp_path / "st" / "rulings-pending.md").read_text().splitlines()
    replies = [line for line in listing if line.startswith("  - Reply: yes ")]
    assert replies == [f"  - Reply: yes R{mmdd}-3", f"  - Reply: yes R{mmdd}-4"]


def test_yes_accepts_a_draft_without_a_model_call_and_tick_runs_only_when_due_and_unlocked(tmp_path):
    cfg = fixture(tmp_path)
    reply(tmp_path, json.dumps({"drafts": [draft(GPU)], "repeats": []}))
    assert run(tmp_path, cfg).returncode == 0
    [rec] = store(tmp_path)
    yes = {"type": "user", "sessionId": "s1", "uuid": "u2", "parentUuid": "u1", "timestamp": "2026-11-14T02:00:00.000Z",
           "message": {"role": "user", "content": f"YES {rec['id'].lower()}"}}
    with open(tmp_path / "p" / "proj" / "s1.jsonl", "a") as fh:
        fh.write(json.dumps(yes) + "\n")

    # Another run holds the lock: tick steps aside without reading anything.
    with open(tmp_path / "st" / "health.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        busy = run(tmp_path, cfg, "tick")
    assert (busy.returncode, busy.stdout.strip()) == (0, "busy")
    assert [r["status"] for r in store(tmp_path)] == ["pending"]

    assert run(tmp_path, cfg).returncode == 0
    # A run 25 h old makes tick due; with no new message it runs without a model call and queues nothing twice.
    cursor_p = tmp_path / "st" / "cursor.json"
    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor_p.write_text(json.dumps({**json.loads(cursor_p.read_text()), "runs": {"rulings": old}}))
    assert run(tmp_path, cfg, "tick").returncode == 0
    assert json.loads(cursor_p.read_text())["runs"]["rulings"] > old
    assert (tmp_path / "calls").read_text().split() == ["rulings"]
    assert [r["status"] for r in store(tmp_path)] == ["accepted"]
    queue = [json.loads(line) for line in (tmp_path / "st" / "lessons-queue.jsonl").read_text().splitlines()]
    assert queue == [{"key": rec["id"], "provenance": "ruling, mac s1 line 2", "text": f"rule for {GPU}"}]
    listing = (tmp_path / "st" / "rulings-pending.md").read_text()
    assert "## Accepted: record in APPROVALS" in listing and f"Reply: yes {rec['id']}" not in listing
