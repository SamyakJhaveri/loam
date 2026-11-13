"""bin/factory.d/pstack-gate.py blocks a worker's first file change until parity's P2 and P3 would pass.

Each fixture under fixtures/pstack-gate/ is a session transcript cut by fixtures/pstack-gate/cut.py (lines it edits say
so there). A replay of the call at source line S hands the hook the transcript up to S, without the call, as Claude
Code 2.1.322 does at PreToolUse, and the call itself as the payload.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "bin" / "factory.d" / "pstack-gate.py"
PARITY = ROOT / "bin" / "factory-parity"
HOOKS = ROOT / "bin" / "factory.d" / "pstack-gate.hooks.json"
FIXTURES = ROOT / "bin" / "tests" / "fixtures" / "pstack-gate"
FIX = "call the sam-cc-setup:pstack router and read the chosen SKILL.md in full before your first change"
_loader = importlib.machinery.SourceFileLoader("factory_parity", str(PARITY))
fp = importlib.util.module_from_spec(importlib.util.spec_from_loader(_loader.name, _loader))
_loader.exec_module(fp)


@pytest.fixture(autouse=True)
def host(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A Claude config dir with a pstack plugin holding a method and the seed-skills marketplace holding the router,
    as on jhaveris, so these tests do not depend on the host's own plugins; returns the config dir."""
    root = tmp_path_factory.mktemp("host")
    for rel in ("pstack/skills/tdd/SKILL.md", "marketplace/sam-cc-setup/skills/pstack/SKILL.md"):
        (root / rel).parent.mkdir(parents=True)
        (root / rel).write_text("# skill\n", encoding="utf-8")
    plugins = root / "config" / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "installed_plugins.json").write_text(json.dumps(
        {"version": 2, "plugins": {"pstack@cursor-plugins": [{"scope": "user", "installPath": str(root / "pstack")}]}}))
    (plugins / "known_marketplaces.json").write_text(json.dumps(
        {"seed-skills": {"installLocation": str(root / "marketplace")}}))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(root / "config"))
    return root / "config"


def events(case: str) -> list[dict]:
    return [json.loads(x) for x in (FIXTURES / f"{case}.jsonl").read_text(encoding="utf-8").splitlines()]


def calls(case: str) -> list[tuple[int, dict]]:
    """(source line, tool_use) for each call in the fixture, in order."""
    return [(e["src"], it) for e in events(case) if e["type"] == "assistant" for it in e["message"]["content"]]


def write(path: Path, evs: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(e) + "\n" for e in evs), encoding="utf-8")
    return path


def session(tmp: Path, case: str, before: int = 10**9, sid: str = "s1") -> Path:
    """The fixture's events before source line `before`, as session sid's transcript under tmp/projects."""
    return write(tmp / "projects" / "-scratch" / f"{sid}.jsonl", [e for e in events(case) if e["src"] < before])


def hook(payload: dict, gate: Path = GATE) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(gate)], input=json.dumps(payload), capture_output=True, text=True,
                          timeout=60)


def payload(transcript: Path, use: dict, **extra: str) -> dict:
    return {"hook_event_name": "PreToolUse", "transcript_path": str(transcript), "tool_name": use["name"],
            "tool_input": use["input"], "tool_use_id": use["id"], **extra}


def replay(tmp: Path, case: str, src: int, gate: Path = GATE, **extra: str) -> subprocess.CompletedProcess[str]:
    use = next(u for s, u in calls(case) if s == src)
    return hook(payload(session(tmp, case, src), use, **extra), gate)


def assert_blocked(r: subprocess.CompletedProcess[str]) -> None:
    assert r.returncode == 2, r.stderr
    assert r.stderr.startswith("pstack-gate: blocked") and FIX in r.stderr and len(r.stderr.strip().splitlines()) == 1


def frozen_run(tmp: Path, decisions: str, finished_rounds: int) -> Path:
    """A run folder laid out as bin/factory freezes it; returns its frozen copy of the gate."""
    run = tmp / "run"
    (run / "frozen").mkdir(parents=True)
    shutil.copy(GATE, run / "frozen" / "pstack-gate.py")
    shutil.copy(PARITY, run / "frozen" / "factory-parity")
    for n in range(1, finished_rounds + 1):
        (run / f"round-{n}.jsonl").write_text("{}\n", encoding="utf-8")
    (run / "worker").mkdir()
    (run / "worker" / "decisions.md").write_text(decisions, encoding="utf-8")
    return run / "frozen" / "pstack-gate.py"


@pytest.mark.parametrize("case", ["w34-r1", "w34-r2", "w35-r1"])
def test_a_real_round_without_a_full_router_and_method_read_is_blocked_at_its_first_change(tmp_path, case):
    """W34 and W35 round 1, W34 round 2: every call before the first change runs; the first change is blocked."""
    first = next((s for s, u in calls(case) if fp.changes(u["name"], u["input"])), None)
    assert first is not None
    for src, _ in calls(case):
        if src > first:
            break
        r = replay(tmp_path / str(src), case, src)
        if src == first:
            assert_blocked(r)
        else:
            assert r.returncode == 0 and not r.stderr, (src, r.stderr)


def test_a_round_that_writes_only_notes_runs_every_call(tmp_path):
    """W35 round 2 writes only to the run's notes: none of its calls is a change, and the gate lets each run."""
    assert not [s for s, u in calls("w35-r2") if fp.changes(u["name"], u["input"])]
    for src, _ in calls("w35-r2"):
        r = replay(tmp_path / str(src), "w35-r2", src)
        assert r.returncode == 0 and not r.stderr, (src, r.stderr)


HIDDEN = {"type": "tool_use", "id": "toolu_hidden", "name": "Bash"}


@pytest.mark.parametrize("command", [
    "F=src/distbench/grader.py; sed -i 's/a/b/' $F; F=/tmp/scratch.py",  # PR 713 Codex 3: reassigned after the write
    "false && F=/tmp/s.py; sed -i 's/a/b/' $F",  # an assignment that may not run
    "sed -i 's/a/b/' $F; F=/tmp/s.py",  # set only after the write
    "cd /tmp/; cd -; sed -i 's/a/b/' src/distbench/grader.py",  # PR 713 Codex 4: back from scratch
    "cd /tmp/x; cd ../..; sed -i 's/a/b/' work/src/distbench/grader.py",
    "x=$(cd /tmp/ && pwd); sed -i 's/a/b/' src/distbench/grader.py",  # a cd in a substitution moves nothing
    "TMPDIR=/tmp/s; TMPDIR=/work/db; sed -i 's/a/b/' \"$TMPDIR/src/distbench/grader.py\"",  # Codex delta D1
    "if true; then TMPDIR=/work/db; fi; sed -i 's/a/b/' \"$TMPDIR/src/distbench/grader.py\"",
    "cd /tmp/; eval 'cd /work/db'; sed -i 's/a/b/' src/distbench/grader.py",  # D2: a cd parity cannot see
    "cd /tmp/; source ./back.sh; sed -i 's/a/b/' src/distbench/grader.py",
])
def test_a_source_write_behind_a_scratch_path_or_dir_is_blocked(tmp_path, command):
    assert_blocked(hook(payload(session(tmp_path, "w34-r1", calls("w34-r1")[0][0]), {**HIDDEN, "input": {"command": command}})))


@pytest.mark.parametrize("command", ["F=/tmp/s.py; sed -i 's/a/b/' $F", "cd /tmp/x && cd sub && sed -i 's/a/b/' f.py"])
def test_a_write_that_stays_in_scratch_runs(tmp_path, command):
    r = hook(payload(session(tmp_path, "w34-r1", calls("w34-r1")[0][0]), {**HIDDEN, "input": {"command": command}}))
    assert r.returncode == 0 and not r.stderr


@pytest.mark.parametrize(("case", "src"), [("w34-r2", 39), ("w35-r1", 63)])
def test_the_first_source_tree_write_of_a_round_with_no_router_read_is_blocked(tmp_path, case, src):
    """W34 round 2's python write to overlap.py and W35 round 1's write to a ticket file."""
    assert_blocked(replay(tmp_path, case, src))


def test_a_full_router_read_then_a_full_method_read_lets_the_change_run(tmp_path):
    r = replay(tmp_path, "w34-r1-full-reads", 153)
    assert r.returncode == 0 and not r.stderr


def test_a_router_read_without_a_method_read_is_blocked(tmp_path):
    assert_blocked(replay(tmp_path, "w34-r1-router-only", 153))


def test_a_method_read_without_a_router_read_is_blocked(tmp_path):
    assert_blocked(replay(tmp_path, "w34-r1-method-only", 153))


def test_a_blocked_change_does_not_count_once_the_router_and_a_method_are_read(tmp_path):
    """The headless run: Edit blocked (src 37), router Skill call, full Read of a method, the same Edit runs (src 77)."""
    assert_blocked(replay(tmp_path / "a", "headless", 37))
    r = replay(tmp_path / "b", "headless", 77)
    assert r.returncode == 0 and not r.stderr


def test_a_subagent_payload_is_judged_on_its_own_transcript(tmp_path):
    """agent_id names <session>/subagents/agent-<id>.jsonl; the main transcript only adds its reads to the round."""
    # A subagent with no router read under a main session that read both: blocked.
    main = session(tmp_path / "a", "headless")
    use = next(u for s, u in calls("w34-r2") if s == 39)
    write(main.with_suffix("") / "subagents" / "agent-x1.jsonl", [e for e in events("w34-r2") if e["src"] < 39])
    assert_blocked(hook(payload(main, use, agent_id="x1")))
    # A subagent that read both under a main session that read nothing and changed nothing: runs.
    main = session(tmp_path / "b", "w34-r2", 39)
    use = next(u for s, u in calls("headless") if s == 77)
    write(main.with_suffix("") / "subagents" / "agent-x2.jsonl", [e for e in events("headless") if e["src"] < 77])
    r = hook(payload(main, use, agent_id="x2"))
    assert r.returncode == 0 and not r.stderr
    # The same subagent under a main session that itself changed a file with no reads (an attended lead before the
    # gate was installed): the lead's change is not the subagent's, so the subagent's change runs.
    main = session(tmp_path / "c", "w34-r2")
    write(main.with_suffix("") / "subagents" / "agent-x4.jsonl", [e for e in events("headless") if e["src"] < 77])
    r = hook(payload(main, use, agent_id="x4"))
    assert r.returncode == 0 and not r.stderr


def test_a_workflow_builder_payload_is_judged_on_its_own_transcript(tmp_path):
    """audit3 F5: a Workflow agent's transcript sits under subagents/workflows/<run>/; with no router read, blocked."""
    main = session(tmp_path, "headless")
    use = next(u for s, u in calls("w34-r2") if s == 39)
    write(main.with_suffix("") / "subagents" / "workflows" / "wf_x" / "agent-x1.jsonl",
          [e for e in events("w34-r2") if e["src"] < 39])
    assert_blocked(hook(payload(main, use, agent_id="x1")))


METHOD = "/home/samyak/.claude/plugins/cache/cursor-plugins/pstack/0.15.36/skills/principle-prove-it-works/SKILL.md"
LOGGED = f"pstack: principle-prove-it-works | {METHOD} | {'0' * 64} | \"Verify every task output\" | proof by git diff\n"
UNREAD = ("pstack: principle-fix-root-causes | /home/samyak/.claude/plugins/cache/cursor-plugins/pstack/0.15.36/skills/"
          f"principle-fix-root-causes/SKILL.md | {'0' * 64} | \"Fix the cause\" | none\n")


@pytest.mark.parametrize(("decisions", "blocked"), [
    (f"{UNREAD}Round 2: the README line.\n{LOGGED}", False),  # the unread method belongs to round 1
    (f"Round 2: the README line.\n{LOGGED}{UNREAD}", True),  # round 2 names a method no round-2 transcript read
    (f"{UNREAD}Round 2: {LOGGED}", False),  # audit3 F2: the pstack: line on the Round line is round 2's
    (f"{UNREAD}Round 2\n{LOGGED}", False),  # the supervisor's header line (worker_round), then the worker's line
])
def test_decisions_md_is_read_for_the_round_being_run(tmp_path, decisions, blocked):
    """In a run's frozen/ copy, P3 reads worker/decisions.md for round 1 + the highest finished round-N.jsonl."""
    gate = frozen_run(tmp_path, decisions, finished_rounds=1)
    r = replay(tmp_path, "headless", 77, gate)
    if blocked:
        assert_blocked(r)
    else:
        assert r.returncode == 0 and not r.stderr


def test_a_relaunched_round_is_the_one_its_header_names(tmp_path):
    """A stop after round-1.jsonl is written but before round-1.checks reruns round 1 on relaunch: worker_round adds
    no second header, so the round is the last `Round N` header, not the highest round-N.jsonl + 1."""
    gate = frozen_run(tmp_path, f"Round 1\n{LOGGED}", finished_rounds=1)
    r = replay(tmp_path, "headless", 77, gate)
    assert r.returncode == 0 and not r.stderr


def test_a_call_that_changes_nothing_runs_while_p3_fails(tmp_path):
    """The Read that would fix a failing P3 (headless src 64, the method's SKILL.md) is never blocked."""
    gate = frozen_run(tmp_path, f"Round 2: the README line.\n{LOGGED}{UNREAD}", finished_rounds=1)
    r = replay(tmp_path, "headless", 64, gate)
    assert r.returncode == 0 and not r.stderr


def test_a_subagent_change_counts_the_methods_its_main_session_read(tmp_path):
    """decisions.md names a method only the main session read; the subagent read the router and another method."""
    sequence = METHOD.replace("principle-prove-it-works", "principle-sequence-verifiable-units")
    gate = frozen_run(tmp_path, f"Round 2: the README line.\npstack: principle-sequence-verifiable-units | {sequence} "
                                f"| {'0' * 64} | \"Order work as a sequence\" | one line, one check\n", finished_rounds=1)
    main = session(tmp_path, "w34-r1-full-reads", 153)
    use = next(u for s, u in calls("headless") if s == 77)
    write(main.with_suffix("") / "subagents" / "agent-x3.jsonl", [e for e in events("headless") if e["src"] < 77])
    r = hook(payload(main, use, agent_id="x3"), gate)
    assert r.returncode == 0 and not r.stderr


@pytest.mark.parametrize("content", [None, "not json\n"])
def test_an_unreadable_transcript_lets_the_change_run_and_says_so(tmp_path, content):
    transcript = tmp_path / "projects" / "-scratch" / "s1.jsonl"
    if content is not None:
        transcript.parent.mkdir(parents=True)
        transcript.write_text(content, encoding="utf-8")
    use = next(u for s, u in calls("w34-r2") if s == 39)
    r = hook(payload(transcript, use))
    assert r.returncode == 0
    assert r.stderr.startswith("pstack-gate: not gating this call")


def test_the_hooks_fragment_runs_the_frozen_gate_and_runs_nothing_without_one(tmp_path):
    """The fragment's PreToolUse command finds pstack-gate.py beside $LOAM_CHECKS (the run's frozen/checks.sh)."""
    entry = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
    assert [e["matcher"] for e in entry] == ["Edit|Write|NotebookEdit|MultiEdit|Bash"]
    command = entry[0]["hooks"][0]["command"]
    gate = frozen_run(tmp_path, "", finished_rounds=0)
    use = next(u for s, u in calls("w34-r2") if s == 39)
    body = json.dumps(payload(session(tmp_path, "w34-r2", 39), use))

    def run(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", "-c", command], input=body, capture_output=True, text=True, timeout=60,
                              env=env)

    base = {k: v for k, v in os.environ.items() if k != "LOAM_CHECKS"}
    assert_blocked(run({**base, "LOAM_CHECKS": str(gate.parent / "checks.sh")}))
    r = run(base)
    assert r.returncode == 0 and "pstack-gate:" in r.stderr and "missing" in r.stderr


@pytest.mark.parametrize("gone", ["installed_plugins.json", "known_marketplaces.json"])
def test_a_host_without_pstack_lets_the_change_run_and_says_so(tmp_path, host, gone):
    """audit3 F4: with no pstack method file or no router on the host, no change could ever pass: fail open."""
    (host / "plugins" / gone).unlink()
    r = replay(tmp_path, "w34-r1-router-only", 153)
    assert r.returncode == 0, r.stderr
    assert r.stderr.startswith("pstack-gate: not gating this call") and len(r.stderr.strip().splitlines()) == 1, r.stderr
