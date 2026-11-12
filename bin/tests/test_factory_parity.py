"""bin/factory-parity prints PASS, FAIL or N/A per behaviour and ends `parity: PASS` or `parity: FAIL (<ids>)`.

Each case under fixtures/parity/ is a run folder of a few lines cut from real factory runs by
fixtures/parity/cut.py (lines it edits say so there); `pass` is a hand-written run where every behaviour passes.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin" / "factory-parity"
FIXTURES = ROOT / "bin" / "tests" / "fixtures" / "parity"

# (case folder, behaviour id, expected status), from each behaviour's rule in the script's docstring.
CASES = [
    ("p1-pass", "P1", "PASS"),  # init lists verify-distbench, loads sam-cc-setup from frozen/plugin-dir, view in prompt
    ("p1-fail", "P1", "FAIL"),  # W35: init without verify-distbench
    ("p1-plugin", "P1", "FAIL"),  # W35: init loads ~/loam's sam-cc-setup, not frozen/plugin-dir's
    ("p1-view", "P1", "FAIL"),  # W35: round-1.prompt.md without the memory view
    ("p2-pass", "P2", "PASS"),  # W34: router read in full (cat), then the first Write
    ("p2-partial", "P2", "FAIL"),  # W34: router read only by sed -n 1,60p
    ("p2-fail", "P2", "FAIL"),  # W35: open(..., "w") with no router read
    ("p2-notes", "P2", "N/A"),  # W35: an append to the run's worker/decisions.md is no change
    ("p2-notes-tree", "P2", "FAIL"),  # W35: the same append into the worktree is a change
    ("p2-brief", "P2", "PASS"),  # W24 builder: no router, but a full read of blast-radius, which its brief names
    ("p2-brief", "P3", "PASS"),  # ... and no pstack: line is needed then
    ("p2-ticket", "P2", "PASS"),  # the ticket's skills: line names it
    ("p2-ticket", "P3", "PASS"),
    ("p2-unnamed", "P2", "FAIL"),  # neither brief nor ticket names it
    ("p2-unnamed", "P3", "FAIL"),
    ("p2-gated", "P2", "PASS"),  # a Write the pstack-gate hook blocked never ran, so it is not the first change
    ("p2-gated", "P3", "PASS"),
    ("p2-denied", "P2", "FAIL"),  # the router `cat` was denied, so it is no read
    ("p3-pass", "P3", "PASS"),  # W34: three principle SKILL.md files read in full; pstack: lines name them
    ("p3-partial", "P3", "FAIL"),  # W34: those reads by sed -n | head
    ("p3-fail", "P3", "FAIL"),  # W34 without those reads
    ("p3-claim", "P3", "FAIL"),  # a pstack: line names a method no transcript read
    ("p3-no-line", "P3", "FAIL"),  # W34's real decisions.md: a change but no pstack: line
    ("p3-order", "P3", "PASS"),  # the method read before the router read still counts
    ("p4-pass", "P4", "PASS"),  # bin/check result ends check: PASSED
    ("p4-fail", "P4", "FAIL"),  # W34: bin/check timed out, no check: line
    ("p4-refusal", "P4", "FAIL"),  # check: PASSED, but a result shows the sandbox refusal
    ("p4-background", "P4", "PASS"),  # background bin/check, its output file read later
    ("p4-background-other", "P4", "FAIL"),  # background bin/check, check: PASSED read from another file
    ("p5-pass", "P5", "PASS"),  # worker Opus medium, builder Opus xhigh, reviewer Fable high
    ("p5-max", "P5", "FAIL"),  # worker effort max
    ("p5-advisor", "P5", "FAIL"),  # worker advisor on Haiku
    ("p5-haiku", "P5", "FAIL"),  # a builder on Haiku
    ("p5-fable-builder", "P5", "FAIL"),  # Fable outside a reviewer
    ("p6-pass", "P6", "PASS"),  # orchestrator diff, skill read, launch and a drive
    ("p6-fail", "P6", "FAIL"),  # W13a: orchestrator diff, no proof
    ("p6-no-read", "P6", "FAIL"),  # launch and a drive, but no verify-distbench/SKILL.md read
    ("p6-partial", "P6", "FAIL"),  # the skill read with a limit, so not in full
    ("p6-help", "P6", "FAIL"),  # skill read and a drive, but only `launch --help`
    ("p6-no-drive", "P6", "FAIL"),  # skill read and launch, no agent or exec drive
    ("p6-na", "P6", "N/A"),  # W35: diff outside what the skill covers
    ("p7-pass", "P7", "PASS"),  # auto-mode probe init, sandbox off, equal digests
    ("p7-fail", "P7", "FAIL"),  # W35 as it ran: bypassPermissions, sandbox on, no digest
    ("p7-mode", "P7", "FAIL"),  # W35's bypassPermissions init
    ("p7-sandbox", "P7", "FAIL"),  # W35's frozen sandbox, on
    ("p7-digest", "P7", "FAIL"),  # a checkout's HEAD moved between launch and finish
    ("p7-lacking", "P7", "FAIL"),  # git-status lines only: no git-head, git-diff, git-untracked
    ("p7-synced", "P7", "PASS"),  # only ~/.claude/skills/synced/ changed, which any session start does
    ("p8-pass", "P8", "PASS"),  # reviewer served Fable; a verdict per blocking id, the REJECTED one with evidence
    ("p8-fail", "P8", "FAIL"),  # W24 round 1 as graded: reviewer served Opus, no verify.json
    ("p8-served", "P8", "FAIL"),  # W24's reviewer rows: served claude-opus-5-5
    ("p8-codex", "P8", "FAIL"),  # no round-1.codex-review.json (verify.json covers the reviewer's id only)
    ("p8-missing", "P8", "FAIL"),  # verify.json lacks blocking codex-1
    ("p8-extra", "P8", "FAIL"),  # verify.json adds codex-2, a medium Codex finding, which does not block
    ("p8-rejected", "P8", "FAIL"),  # a REJECTED verdict with no cmd or output
    ("p8-unverified", "P8", "FAIL"),  # an UNVERIFIED verdict
]

# --attended cases: (case, behaviour id, expected status), each a session.jsonl with optional session/subagents/.
ATTENDED_CASES = [
    ("attended-pass", "P2", "PASS"),  # 4114e7c2 worker: router Skill call, then its first Edit
    ("attended-pass", "P3", "PASS"),  # ... with a full method read before it
    ("attended-fail", "P2", "FAIL"),  # fb454b64 lead: sed -i with no router read
    ("attended-fail", "P3", "FAIL"),
    ("attended-sub", "P2", "FAIL"),  # a subagent under session/subagents/ edits with no router read
    ("attended-sub", "P6", "FAIL"),  # ... src/distbench/runner.py, with no verify-distbench proof
    ("attended-sub-proof", "P6", "PASS"),  # ... with the skill read and the launch-and-drive chain
    ("attended-scratch", "P2", "N/A"),
    ("attended-head", "P3", "PASS"),  # cat of two SKILL.md files | head -120, result 41 lines: nothing cut
    ("attended-head-cut", "P3", "FAIL"),  # the same read by head -20, which cut it  # four writes to scratch or notes (via >>, cd $S, a cat heredoc, sed -i $F)
]


def parity(run: Path, projects: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(run), "--projects-root", str(projects)],
                          capture_output=True, text=True, timeout=60)


def statuses(out: str) -> dict[str, str]:
    """Behaviour id -> status, from lines `<STATUS> <id> <name>: <evidence>`."""
    rows = {}
    for line in out.splitlines()[:-1]:
        status, pid = line.split(" ", 2)[:2]
        rows[pid] = status
    return rows


@pytest.mark.parametrize(("case", "pid", "expected"), CASES, ids=[c[0] for c in CASES])
def test_behaviour(case: str, pid: str, expected: str) -> None:
    proc = parity(FIXTURES / case / "run", FIXTURES / case / "projects")
    assert proc.returncode in (0, 1), proc.stderr
    assert statuses(proc.stdout)[pid] == expected, proc.stdout
    last = proc.stdout.splitlines()[-1]
    if expected == "FAIL":
        assert proc.returncode == 1 and last.startswith("parity: FAIL (") and pid in last[len("parity: FAIL ("):-1].split(", ")


def test_a_run_where_every_behaviour_passes_exits_zero() -> None:
    proc = parity(FIXTURES / "pass" / "run", FIXTURES / "pass" / "projects")
    assert (proc.returncode, proc.stdout.splitlines()[-1]) == (0, "parity: PASS"), proc.stdout
    assert set(statuses(proc.stdout).values()) == {"PASS"}, proc.stdout


def test_a_key_folder_holding_one_run_is_read_as_that_run(tmp_path: Path) -> None:
    shutil.copytree(FIXTURES / "pass" / "run", tmp_path / "W1-key" / "0123abcd")
    proc = parity(tmp_path / "W1-key", FIXTURES / "pass" / "projects")
    assert (proc.returncode, proc.stdout.splitlines()[-1]) == (0, "parity: PASS"), proc.stdout + proc.stderr


def test_a_folder_with_no_round_transcript_is_unusable(tmp_path: Path) -> None:
    proc = parity(tmp_path, tmp_path)
    assert (proc.returncode, proc.stdout) == (2, ""), proc.stdout


def test_classifier_denials_are_listed_with_their_command_and_reason() -> None:
    proc = parity(FIXTURES / "p7-pass" / "run", FIXTURES / "p7-pass" / "projects")
    p7 = next(x for x in proc.stdout.splitlines() if x.startswith("PASS P7 "))
    assert "classifier denials: round-1.jsonl:3 Bash `git -C " in p7 and "push --force origin HEAD:main` [Git Destructive]" in p7, p7


@pytest.mark.parametrize(("case", "pid", "expected"), ATTENDED_CASES, ids=[f"{c[0]}-{c[1]}" for c in ATTENDED_CASES])
def test_attended(case: str, pid: str, expected: str) -> None:
    proc = subprocess.run([sys.executable, str(SCRIPT), "--attended", str(FIXTURES / case / "session.jsonl")],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode in (0, 1), proc.stderr
    lines = proc.stdout.splitlines()
    assert lines[0] == f"== {FIXTURES / case / 'session.jsonl'}" and {x.split(" ", 2)[1] for x in lines[1:-1]} == {"P2", "P3", "P6"}
    assert statuses("\n".join(lines[1:]))[pid] == expected, proc.stdout
    assert proc.returncode == (1 if lines[-1].startswith("parity: FAIL") else 0)


def edit_events(path: Path, fn: Callable[[dict], None]) -> None:
    """Rewrite path's JSON lines, each tool_use or tool_result item passed to fn to edit in place."""
    events = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") in ("tool_use", "tool_result"):
                fn(item)
    path.write_text("".join(json.dumps(e) + "\n" for e in events))


def failed_skill_reads(run: Path) -> None:
    """Every call that names a SKILL.md failed (the file was missing); the Write after them still succeeded."""
    ids: set[str] = set()

    def mark(item: dict) -> None:
        if item["type"] == "tool_use" and "SKILL.md" in json.dumps(item["input"]):
            ids.add(item["id"])
        elif item["type"] == "tool_result" and item["tool_use_id"] in ids:
            item.update(is_error=True, content="Exit code 1\ncat: /x/skills/x/SKILL.md: No such file or directory")
    edit_events(run / "round-1.jsonl", mark)


def guarded_gate(run: Path) -> None:
    """The gate spelled as a done-checks line spells it, after sourcing lib.sh; its result still shows check: PASSED."""
    def edit(item: dict) -> None:
        if item["type"] == "tool_use" and item["name"] == "Bash":
            item["input"]["command"] = "source /r/abcdef12/frozen/lib.sh && guard bin/check"
    edit_events(run / "round-1.jsonl", edit)


def failed_launch(run: Path) -> None:
    """The proof chain failed at its launch, so the drive never ran."""
    def edit(item: dict) -> None:
        if item["type"] == "tool_result" and item["tool_use_id"] == "toolu_proof":
            item.update(is_error=True, content="Exit code 1\nError: runner failed to launch; drive never executed")
    edit_events(run / "round-2.jsonl", edit)


def stale_verify(run: Path) -> None:
    """verify.json names a commit other than the graded one."""
    v = json.loads((run / "round-1.verify.json").read_text())
    (run / "round-1.verify.json").write_text(json.dumps({**v, "sha": "0" * 40}) + "\n")


def unparseable_review(run: Path) -> None:
    """The supervisor's fallback for a reviewer reply it could not parse (bin/factory call_json), and verify.json as
    verify_round writes it then: review_findings drops the fallback (review.sh), so no reviewer id."""
    (run / "round-1.review.json").write_text(json.dumps({"verdict": "fix", "unparseable": True, "findings": [
        {"severity": "high", "file": "-", "line": 0, "defect": "reviewer output unparseable", "fix": "rerun"}]}) + "\n")
    v = json.loads((run / "round-1.verify.json").read_text())
    v["findings"] = [f for f in v["findings"] if not f["id"].startswith("reviewer-")]
    (run / "round-1.verify.json").write_text(json.dumps(v) + "\n")


def round_two_on_its_round_line(run: Path) -> None:
    """A round 2 that reads the router and tdd/SKILL.md, then writes; decisions.md logs tdd on its `Round 2:` line."""
    r1 = (run / "round-1.jsonl").read_text().splitlines()
    tdd = "/home/samyak/.claude/plugins/cache/cursor-plugins/pstack/0.15.36/skills/tdd/SKILL.md"
    write = next(json.loads(x) for x in r1 if '"Write"' in x)["message"]["content"][0]["input"]
    calls = [("r2a", "Bash", {"command": "cat /home/samyak/loam/cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md"}),
             ("r2b", "Read", {"file_path": tdd}), ("r2c", "Write", write)]
    events = [json.loads(r1[0])] + [e for i, name, inp in calls for e in (
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": i, "name": name, "input": inp}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": "ok"}]}})]
    (run / "round-2.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    with (run / "worker" / "decisions.md").open("a") as f:
        f.write(f"Round 2: pstack: tdd | {tdd} | {'0' * 64} | \"TDD Bug Fix\" | red first\n")


# Audit 3 repros (the verifier's audit3-verify.md): (name, committed case, edit of its run folder, id, expected).
VARIANTS = [
    ("c2-failed-reads", "p3-pass", failed_skill_reads, "P2", "FAIL"),  # a read whose result is an error read nothing
    ("c2-failed-reads", "p3-pass", failed_skill_reads, "P3", "FAIL"),
    ("c3-guard", "p4-pass", guarded_gate, "P4", "PASS"),  # `guard bin/check` runs the gate
    ("c4-failed-launch", "p6-pass", failed_launch, "P6", "FAIL"),  # a proof call that failed proves nothing
    ("c6-stale-verify", "pass", stale_verify, "P8", "FAIL"),  # verify.json is for another commit
    ("f2-round-line", "p3-pass", round_two_on_its_round_line, "P3", "PASS"),  # `Round 2: pstack: ...` is round 2's
]


def test_an_unparseable_review_is_named_as_no_review(tmp_path: Path) -> None:
    # audit3 F8: the FAIL is right (no review happened); the message names the fallback, not an id mismatch.
    shutil.copytree(FIXTURES / "pass", tmp_path / "f8")
    unparseable_review(tmp_path / "f8" / "run")
    proc = parity(tmp_path / "f8" / "run", tmp_path / "f8" / "projects")
    p8 = next(x for x in proc.stdout.splitlines() if " P8 " in x)
    assert p8.startswith("FAIL P8 ") and "round-1.review.json is the supervisor's unparseable fallback: no review" in p8, p8
    assert "not the blocking ids" not in p8, p8


@pytest.mark.parametrize(("name", "case", "edit", "pid", "expected"), VARIANTS, ids=[f"{v[0]}-{v[3]}" for v in VARIANTS])
def test_variant(tmp_path: Path, name: str, case: str, edit: Callable[[Path], None], pid: str, expected: str) -> None:
    shutil.copytree(FIXTURES / case, tmp_path / name)
    edit(tmp_path / name / "run")
    proc = parity(tmp_path / name / "run", tmp_path / name / "projects")
    assert proc.returncode in (0, 1), proc.stderr
    assert statuses(proc.stdout)[pid] == expected, proc.stdout
