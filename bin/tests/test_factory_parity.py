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
    ("p2-partial", "P2", "FAIL"),  # W34: the router by sed -n 1,60p: only a plain cat or Read is a full read
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
    ("p4-pass", "P4", "PASS"),  # W34 round-1.checks, the supervisor's record, holds PASS check-green
    ("p4-fail", "P4", "FAIL"),  # that record without its check-green line: no gate ran
    ("p4-unsure", "P4", "UNSURE"),  # no record; the transcript's printed check: PASSED is not taken
    ("p4-refusal", "P4", "FAIL"),  # the record, but a result shows the sandbox refusal
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
    ("attended-pass", "P3", "UNSURE"),  # ... its method read is `P=...; cat a b`, compound: not seen as a read
    ("attended-fail", "P2", "FAIL"),  # fb454b64 lead: sed -i with no router read
    ("attended-fail", "P3", "FAIL"),
    ("attended-sub", "P2", "FAIL"),  # a subagent under session/subagents/ edits with no router read
    ("attended-sub", "P6", "FAIL"),  # ... src/distbench/runner.py, with no verify-distbench proof
    ("attended-sub-proof", "P6", "PASS"),  # ... with the skill read and the launch-and-drive chain
    ("attended-scratch", "P2", "N/A"),
    ("attended-head", "P3", "UNSURE"),  # cat of two SKILL.md files | head -120: compound, not seen as a read
    ("attended-head-cut", "P3", "UNSURE"),  # the same by head -20  # four writes to scratch or notes (via >>, cd $S, a cat heredoc, sed -i $F)
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


@pytest.mark.parametrize(("frozen", "expected"), [(True, "FAIL"), (False, "PASS")])
def test_a_principle_named_only_by_common_md_is_no_brief_named_read(tmp_path: Path, frozen: bool, expected: str) -> None:
    # p3-order without its router read: the round fully reads principle-test-behavior-not-implementation, then writes.
    # Its prompt names that principle only in _common.md's line, which every round gets, so the read stands in for no
    # router read (FAIL); the same line in a prompt with no frozen _common.md is the brief's own (PASS).
    run = tmp_path / "run"
    shutil.copytree(FIXTURES / "p3-order" / "run", run)
    events = (run / "round-1.jsonl").read_text().splitlines()
    (run / "round-1.jsonl").write_text("\n".join(e for e in events if "toolu_01SgvVXQekBErfzUfb8VmLsB" not in e) + "\n")
    common = (ROOT / "bin" / "factory.d" / "_common.md").read_text()
    skills = "/home/samyak/.claude/plugins/cache/cursor-plugins/pstack/0.15.36/skills"  # where p3-order read it
    (run / "round-1.prompt.md").write_text("# A ticket\n\n" + common.replace("<pstack>", skills))
    if frozen:
        (run / "frozen").mkdir()
        (run / "frozen" / "_common.md").write_text(common)
    proc = parity(run, tmp_path / "projects")
    assert statuses(proc.stdout)["P2"] == expected, proc.stdout


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
    assert proc.returncode == (0 if lines[-1] == "parity: PASS" else 1)


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


def reads_then_a_failing_command(run: Path, drop: str = "") -> None:
    """audit4 1: each SKILL.md cat is followed by `; false`, so its Bash result is is_error, yet it printed each file
    in full (its frontmatter name: line shows); `drop` removes one file's name line from the result."""
    ids: set[str] = set()

    def mark(item: dict) -> None:
        if item["type"] == "tool_use" and "SKILL.md" in json.dumps(item["input"]):
            item["input"]["command"] += "; false"
            ids.add(item["id"])
        elif item["type"] == "tool_result" and item["tool_use_id"] in ids:
            text = item["content"] if "name: " in item["content"] else f"---\nname: pstack\n---\n{item['content']}"
            item.update(is_error=True, content="Exit code 1\n" + (text.replace(f"name: {drop}\n", "") if drop else text))
    edit_events(run / "round-1.jsonl", mark)


def failed_launch(run: Path) -> None:
    """The proof chain failed at its launch, so the drive never ran."""
    def edit(item: dict) -> None:
        if item["type"] == "tool_result" and item["tool_use_id"] == "toolu_proof":
            item.update(is_error=True, content="Exit code 1\nError: runner failed to launch; drive never executed")
    edit_events(run / "round-2.jsonl", edit)


def retried_reviewer(served: bool) -> Callable[[Path], None]:
    """audit4 (Fable 2): a killed reviewer attempt books a no-result row (served nothing) before the retry's row;
    with served False the retry's row is gone too, so no reviewer call of the round served anything."""
    def edit(run: Path) -> None:
        rows = [json.loads(x) for x in (run / "ledger.jsonl").read_text().splitlines()]
        killed = {"round": 1, "role": "reviewer", "model": "claude-fable-5-2", "cost_usd": 5, "subtype": "no-result",
                  "served_models": []}
        rows = [r for r in rows if served or r["role"] != "reviewer"]
        rows.insert(1, killed)
        (run / "ledger.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return edit


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
    calls = [("r2a", "Bash", {"command": "cat /home/samyak/loam/cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md"},
              "---\nname: pstack"), ("r2b", "Read", {"file_path": tdd}, "     1\u2192---\n     2\u2192name: tdd"),
             ("r2c", "Write", write, "ok")]
    events = [json.loads(r1[0])] + [e for i, name, inp, out in calls for e in (
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": i, "name": name, "input": inp}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": out}]}})]
    (run / "round-2.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    with (run / "worker" / "decisions.md").open("a") as f:
        f.write(f"Round 2: pstack: tdd | {tdd} | {'0' * 64} | \"TDD Bug Fix\" | red first\n")


def redirected_skill_reads(run: Path) -> None:
    """PR 713 Codex 3: every SKILL.md `cat` sends its output to /dev/null, so the results show none of the files."""
    ids: set[str] = set()

    def mark(item: dict) -> None:
        if item["type"] == "tool_use" and "SKILL.md" in json.dumps(item["input"]):
            item["input"]["command"] = item["input"]["command"].replace("SKILL.md", "SKILL.md > /dev/null")
            ids.add(item["id"])
        elif item["type"] == "tool_result" and item["tool_use_id"] in ids:
            item["content"] = ""
    edit_events(run / "round-1.jsonl", mark)


def skill_commands(change: Callable[[str], str], result: str | None = None) -> Callable[[Path], None]:
    """Each SKILL.md Bash command rewritten by change; with result, each such call's result replaced by it."""
    def edit(run: Path) -> None:
        ids: set[str] = set()

        def mark(item: dict) -> None:
            if item["type"] == "tool_use" and item["name"] == "Bash" and "SKILL.md" in item["input"]["command"]:
                item["input"]["command"] = change(item["input"]["command"])
                ids.add(item["id"])
            elif item["type"] == "tool_result" and item["tool_use_id"] in ids and result is not None:
                item["content"] = result
        edit_events(run / "round-1.jsonl", mark)
    return edit


def no_result(tool_id: str) -> Callable[[Path], None]:
    """The tool_result of call tool_id is gone from every round, as when a run is cut off mid-call."""
    def edit(run: Path) -> None:
        for f in run.glob("round-*.jsonl"):
            keep = [x for x in f.read_text().splitlines() if not any(
                isinstance(c, dict) and c.get("tool_use_id") == tool_id
                for c in (json.loads(x).get("message") or {}).get("content") or [] if not isinstance(c, str))]
            f.write_text("".join(x + "\n" for x in keep))
    return edit


def first_call(command: str) -> Callable[[Path], None]:
    """A Bash call of command, with an empty result, before every other call of round 1."""
    def edit(run: Path) -> None:
        f = run / "round-1.jsonl"
        lines = f.read_text().splitlines()
        new = [{"type": "assistant", "message": {"content": [
                   {"type": "tool_use", "id": "t0", "name": "Bash", "input": {"command": command}}]}},
               {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t0", "content": ""}]}}]
        f.write_text("".join(x + "\n" for x in [lines[0], *map(json.dumps, new), *lines[1:]]))
    return edit


# PR 713 Codex 3 and 4: a write to the source tree that a scratch path or directory seemed to cover. Each fails
# closed: an assignment parity cannot place in the call, or a cd it cannot resolve, leaves the write a change.
HIDDEN_WRITES = [
    ("reassigned", "F=src/distbench/grader.py; sed -i 's/a/b/' $F; F=/tmp/scratch.py"),
    ("used-before-set", "sed -i 's/a/b/' $F; F=/tmp/scratch.py"),
    ("conditional-assign", "false && F=/tmp/s.py; sed -i 's/a/b/' $F"),
    ("cd-back", "cd /tmp/; cd -; sed -i 's/a/b/' src/distbench/grader.py"),
    ("cd-up", "cd /tmp/x; cd ../..; sed -i 's/a/b/' work/db/src/distbench/grader.py"),
    ("cd-in-substitution", "x=$(cd /tmp/ && pwd); sed -i 's/a/b/' src/distbench/grader.py"),
    # PR 713 Codex delta D1: a $TMPDIR set in the call that parity cannot place is no scratch path
    ("tmpdir-reassigned", "TMPDIR=/tmp/s; TMPDIR=/work/db; sed -i 's/a/b/' \"$TMPDIR/src/distbench/grader.py\""),
    ("tmpdir-conditional", "if true; then TMPDIR=/work/db; fi; sed -i 's/a/b/' \"$TMPDIR/src/distbench/grader.py\""),
    # D2: eval, source or . can run a cd parity cannot see, so it ends the scratch exemption
    ("cd-in-eval", "cd /tmp/; eval 'cd /work/db'; sed -i 's/a/b/' src/distbench/grader.py"),
    ("cd-in-source", "cd /tmp/; . ./back.sh; sed -i 's/a/b/' src/distbench/grader.py"),
]


def logged_paths(old: str, new: str) -> Callable[[Path], None]:
    """Each decisions.md path with old replaced by new: the method name stays, the file read is another."""
    def edit(run: Path) -> None:
        f = run / "worker" / "decisions.md"
        f.write_text(f.read_text().replace(old, new))
    return edit


def checkout_lines(drop: str = "") -> Callable[[Path], None]:
    """Both digests get the checkout:<dir> lines shell_digest now writes; drop removes that checkout's git-* lines."""
    def edit(run: Path) -> None:
        for name in ("shell-digest.start", "shell-digest.end"):
            f = run / name
            lines = f.read_text().splitlines()
            dirs = [x.split("  git-status:", 1)[1] for x in lines if "  git-status:" in x]
            keep = [x for x in lines if not (drop and x.endswith(f":{drop}") and "  git-" in x)]
            f.write_text("".join(x + "\n" for x in keep + [f"{'0' * 64}  checkout:{d}" for d in dirs]))
    return edit


# One rewrite of each SKILL.md read per construct class parity does not model (factory-parity `unsure`).
UNMODELLED: dict[str, Callable[[str], str]] = {
    "group-after-command": lambda c: f"true && {{ {c}; }} > /dev/null",  # PR 713 reviewer
    "subshell": lambda c: f"( {c} )",
    "loop-redirect": lambda c: f"{c} > /dev/null" if c.endswith("done") else f"for x in 1; do {c}; done > /dev/null",
    "fd-to-stderr": lambda c: c.replace("SKILL.md", "SKILL.md 2>/dev/null 1>&2"),  # PR 713 Codex
    "here-doc": lambda c: f"python3 - <<'EOF'\nprint(1)\nEOF\n{c}",
    "here-string": lambda c: f"cat <<< x; {c}",
    "eval": lambda c: f"eval {c}",
    "source": lambda c: f"source ~/env.sh; {c}",
    "process-substitution": lambda c: f"diff <(true) /dev/null; {c}",
}


def errored_skill_reads(run: Path) -> None:
    """Each SKILL.md call's result marked is_error (killed mid-output, say), its text, name: line included, kept."""
    ids: set[str] = set()

    def mark(item: dict) -> None:
        if item["type"] == "tool_use" and "SKILL.md" in json.dumps(item["input"]):
            ids.add(item["id"])
        elif item["type"] == "tool_result" and item["tool_use_id"] in ids:
            item["is_error"] = True
    edit_events(run / "round-1.jsonl", mark)


def read_result(text: str) -> Callable[[Path], None]:
    """Every Read call's result replaced by text."""
    def edit(run: Path) -> None:
        ids: set[str] = set()

        def mark(item: dict) -> None:
            if item["type"] == "tool_use" and item["name"] == "Read":
                ids.add(item["id"])
            elif item["type"] == "tool_result" and item["tool_use_id"] in ids:
                item["content"] = text
        for f in run.glob("round-*.jsonl"):
            edit_events(f, mark)
    return edit


def advisor_off(run: Path) -> None:
    """The worker ran with FACTORY_WORKER_ADVISOR= (no advisor), which worker_round logs as advisor=off."""
    log = run / "factory.log"
    log.write_text(log.read_text().replace("advisor=claude-opus-5-5", "advisor=off"))


def no_checkout_digest(run: Path) -> None:
    """PR 713 Codex 7: both digests lose every git-* line; only the ~/.claude file digests are left, and equal."""
    for name in ("shell-digest.start", "shell-digest.end"):
        f = run / name
        f.write_text("".join(x + "\n" for x in f.read_text().splitlines() if "  git-" not in x))


# Audit 3 repros (the verifier's audit3-verify.md): (name, committed case, edit of its run folder, id, expected).
VARIANTS = [
    ("r-redirected-reads", "p3-pass", redirected_skill_reads, "P2", "UNSURE"),  # cat > /dev/null is compound
    ("r-redirected-reads", "p3-pass", redirected_skill_reads, "P3", "UNSURE"),
    ("r-no-checkout-digest", "p7-pass", no_checkout_digest, "P7", "FAIL"),
    # PR 713 Codex re-check: a group or an fd redirect is not modelled, so the read is UNSURE; a comment holding `>`
    # is modelled and stays a read
    ("r2-group-redirect", "p3-pass", skill_commands(lambda c: f"{{ {c}; }} > /dev/null", ""), "P2", "UNSURE"),
    ("r2-group-redirect", "p3-pass", skill_commands(lambda c: f"{{ {c}; }} > /dev/null", ""), "P3", "UNSURE"),
    ("r2-fd-redirect", "p3-pass", skill_commands(lambda c: c.replace("SKILL.md", "SKILL.md 3>/dev/null 1>&3"), ""),
     "P2", "UNSURE"),
    ("r2-comment", "p3-pass", skill_commands(lambda c: f"{c} # stdout > terminal"), "P2", "PASS"),
    ("r2-comment", "p3-pass", skill_commands(lambda c: f"{c} # stdout > terminal"), "P3", "PASS"),
    # ... and P7 needs every checkout shell_digest names, not only the ones whose lines survived
    ("r2-checkout-lines", "p7-pass", checkout_lines(), "P7", "PASS"),
    ("r2-checkout-missing", "p7-pass", checkout_lines("/home/samyak/distbench"), "P7", "FAIL"),
    ("r3-advisor-off", "p5-pass", advisor_off, "P5", "PASS"),  # no advisor is no off-model advisor
    # PR 713 lead ruling: each construct parity does not model makes the check UNSURE, never PASS
    *[(f"r3-{name}", "p3-pass", skill_commands(change, ""), "P2", "UNSURE") for name, change in UNMODELLED.items()],
    # PR 713 lead ruling: a read counts only when its own result shows the file's name: line
    ("r4-untaken-branch", "p3-pass", skill_commands(lambda c: f"if false; then {c}; fi", ""), "P2", "UNSURE"),
    ("r4-untaken-branch", "p3-pass", skill_commands(lambda c: f"if false; then {c}; fi", ""), "P3", "UNSURE"),
    ("r4-exec-redirect", "p3-pass", skill_commands(lambda c: f"exec > /dev/null; {c}", ""), "P2", "UNSURE"),
    ("r4-loop-pipe", "p3-pass", skill_commands(lambda c: f"for x in 1; do {c}; done | head -3"), "P3", "UNSURE"),
    # PR 713 lead ruling: only a call that is one simple read counts, and compound reads are UNSURE (the reviewer's
    # and Codex's examples: the name: line printed by another command of the same call)
    ("r5-copy-then-head", "p3-pass", skill_commands(lambda c: f"{c} > /tmp/s.md && head -3 /tmp/s.md"), "P2", "UNSURE"),
    ("r5-grep-name", "p3-pass", skill_commands(lambda c: f"false && {c}; grep -m1 name: {c.split()[-1]}"), "P3",
     "UNSURE"),
    ("r5-null-then-sed", "p3-pass", skill_commands(lambda c: f"{c} > /dev/null; sed -n 2p {c.split()[-1]}"), "P3",
     "UNSURE"),
    ("r5-errored-read", "p3-pass", errored_skill_reads, "P3", "FAIL"),  # an errored call reads nothing, shown or not
    ("r5-cat-not-shown", "p3-pass", skill_commands(lambda c: c, ""), "P3", "FAIL"),  # a plain cat that showed nothing
    # PR 713 reviewer High: Claude Code trims a Bash result's trailing blank lines, so a head or sed that cut the file
    # on a blank line looks uncut; neither is ever a full read, whatever its result shows
    ("r5-head-uncut", "p3-pass", skill_commands(lambda c: c.replace("cat ", "head -n 500 ", 1)), "P3", "FAIL"),
    ("r6-sed-uncut", "p3-pass", skill_commands(lambda c: c.replace("cat ", "sed -n 1,500p ", 1)), "P3", "FAIL"),
    ("r6-sed-uncut", "p3-pass", skill_commands(lambda c: c.replace("cat ", "sed -n 1,500p ", 1)), "P2", "FAIL"),
    ("r5-head-cut", "p3-pass", skill_commands(lambda c: c.replace("cat ", "head -n 2 ", 1)), "P3", "FAIL"),
    ("r4-read-not-shown", "p6-pass", read_result("# Verify distbench"), "P6", "FAIL"),
    ("c2-failed-reads", "p3-pass", failed_skill_reads, "P2", "FAIL"),  # a read whose result is an error read nothing
    ("c2-failed-reads", "p3-pass", failed_skill_reads, "P3", "FAIL"),
    ("a4-read-then-false", "p3-pass", reads_then_a_failing_command, "P2", "UNSURE"),  # cat; false is compound
    ("a4-read-then-false", "p3-pass", reads_then_a_failing_command, "P3", "UNSURE"),
    ("a4-name-missing", "p3-pass", lambda run: reads_then_a_failing_command(run, "principle-sequence-verifiable-units"),
     "P3", "UNSURE"),  # compound, so not seen as a read
    ("c4-failed-launch", "p6-pass", failed_launch, "P6", "FAIL"),  # a proof call that failed proves nothing
    ("c6-stale-verify", "pass", stale_verify, "P8", "FAIL"),
    ("a4-retried-reviewer", "pass", retried_reviewer(True), "P8", "PASS"),  # the killed attempt's row is no review
    ("a4-killed-reviewer", "pass", retried_reviewer(False), "P8", "FAIL"),  # ... but some reviewer row must serve  # verify.json is for another commit
    ("f2-round-line", "p3-pass", round_two_on_its_round_line, "P3", "PASS"),  # `Round 2: pstack: ...` is round 2's
    # PR 713 Codex at ffef0f02
    ("r6-proof-no-result", "pass", no_result("t5"), "P6", "FAIL"),  # 1: a proof call with no result proved nothing
    *[(f"r6-{name}", "pass", first_call(cmd), pid, "FAIL") for name, cmd in HIDDEN_WRITES for pid in ("P2", "P3")],
    ("r6-scratch-write", "pass", first_call("F=/tmp/s.py; sed -i 's/a/b/' $F; cd /tmp/x && cd sub && sed -i 's/a/b/' f.py"),
     "P2", "PASS"),  # ... while a write that stays in scratch is still no change
    ("r6-logged-path", "pass", logged_paths("/pstack/0.15.36/", "/pstack/0.99.0/"), "P3", "FAIL"),  # 5
]


def spawned(agent: str) -> Callable[[Path], None]:
    """A second Agent call whose stream-json result names agentId `agent`, as Claude Code's tool_use_result does."""
    def edit(run: Path) -> None:
        with (run / "round-1.jsonl").open("a") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "t8", "name": "Agent", "input": {"description": "d", "prompt": "p"}}]}}) + "\n")
            f.write(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t8",
                                "content": "done"}]}, "tool_use_result": {"status": "completed", "agentId": agent}}) + "\n")
    return edit


@pytest.mark.parametrize(("agent", "code"), [("a2", 2), ("a1", 0)])
def test_a_spawned_agent_without_its_transcript_is_unusable(tmp_path: Path, agent: str, code: int) -> None:
    """PR 713 Codex 2: agent a1's transcript is there, a2's is not; a count of loaded transcripts would hide it."""
    shutil.copytree(FIXTURES / "pass", tmp_path / "s")
    spawned(agent)(tmp_path / "s" / "run")
    proc = parity(tmp_path / "s" / "run", tmp_path / "s" / "projects")
    assert proc.returncode == code, proc.stdout + proc.stderr
    assert code == 0 or ("agent-a2.jsonl" in proc.stderr and proc.stdout == ""), proc.stderr


def test_an_unsure_check_makes_parity_unsure_not_pass(tmp_path: Path) -> None:
    shutil.copytree(FIXTURES / "pass", tmp_path / "u")
    skill_commands(lambda c: f"true && {{ {c}; }}")(tmp_path / "u" / "run")
    proc = parity(tmp_path / "u" / "run", tmp_path / "u" / "projects")
    assert statuses(proc.stdout)["P2"] == "UNSURE" and "holds a { } or ( ) group" in proc.stdout, proc.stdout
    assert (proc.returncode, proc.stdout.splitlines()[-1]) == (1, "parity: UNSURE (P2, P3)"), proc.stdout


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
