#!/usr/bin/env python3
"""Cut the bin/factory-parity test fixtures from real factory runs and transcripts on jhaveris.

  python3 bin/tests/fixtures/parity/cut.py [--runs DIR] [--projects DIR] [--distbench DIR] [--exp FILE] [--pstack DIR]

Each case folder `<case>/run` (plus `<case>/projects` when it has subagents) holds a few lines cut from the files
named in its comment, trimmed to the fields bin/factory-parity reads. A line marked EDIT differs from its source
as the comment says, so a behaviour has a passing case where no real run passes yet. A skill read keeps the result
lines that show its `name:` line, the evidence parity reads. Re-running it on jhaveris rewrites the same bytes. The `pass` folder is hand-written (every behaviour passing at once) and not cut here.
`--exp` is the auto-mode probe transcript of the 12 Nov design experiments (design-pick.md, "Doubts settled by
experiment" 1), kept in the lead session's scratchpad: the only real transcript with a classifier denial.
`<case>/session.jsonl` cases (with `<case>/session/subagents/`) are attended sessions for --attended.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
W24, W34, W35, W13A = ("W24-statistics/5930e9bf", "W34-overlap-and-segmenter/c9751598", "W35-tooling/65a16a39",
                       "W13a-wall-clock/f758a028")
W24_WF = ("-home-samyak-distbench-isc-w24-statistics/859605d2-94ba-4ede-aa5b-28cde02950be/subagents/workflows/"
          "wf_1071d9b3-9d3")
BUILDER, PLAN = "agent-a25ee32888ed2a901", "agent-a4132ece75e9d33e8"
LEAD_AGENT = "-home-samyak-distbench-lead/2dc42e84-8c33-470b-8aa9-4873c730522b/subagents/agent-adcdc722db83bd416.jsonl"
W24_BUILDER = "agent-a3dc47e8267f928a2"
ATTENDED_PASS = "-home-samyak-distbench/4114e7c2-4b6f-4f6b-a014-2c87309a1685/subagents/agent-a9868070169571e78.jsonl"
ATTENDED_HEAD = "-home-samyak-distbench/4114e7c2-4b6f-4f6b-a014-2c87309a1685/subagents/agent-a478c9735034119e3.jsonl"
ATTENDED_LEAD = "-home-samyak-distbench/fb454b64-643d-4ead-8d5a-1db32cd3a1a9.jsonl"
ATTENDED_RUNNER = "-home-samyak-distbench/fb454b64-643d-4ead-8d5a-1db32cd3a1a9/subagents/agent-a564fcc527ebaa284.jsonl"
EXP = Path("/tmp/claude-1000/-home-samyak-distbench/8ac7c511-0dcf-4476-8336-664057a8c693/scratchpad/exp-pick/run1.jsonl")
PSTACK = Path.home() / ".claude/plugins/cache/cursor-plugins/pstack/0.15.36"
KEEP_SKILLS = {"sam-cc-setup:pstack", "pstack:tdd", "pstack:principle-sequence-verifiable-units",
               "pstack:principle-test-behavior-not-implementation", "pstack:principle-prove-it-works",
               "pstack:blast-radius"}
PLUGIN = "sam-cc-setup"
PROOF_PLUGIN = "/home/samyak/.local/state/loam/worktrees/factory-distbench-test/cultivation/marketplace/sam-cc-setup"
VIEW = "# Factory lessons\n\nPurpose line.\n"


def line(path: Path, n: int) -> str:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[n - 1]


def event(path: Path, n: int) -> dict:
    return json.loads(line(path, n))


def dump(events: list[dict]) -> str:
    return "".join(json.dumps(e, separators=(",", ":"), ensure_ascii=False) + "\n" for e in events)


def init(ev: dict, add: tuple[str, ...] = ()) -> dict:
    return {"type": "system", "subtype": "init", "cwd": ev["cwd"], "session_id": ev["session_id"], "model": ev["model"],
            "permissionMode": ev["permissionMode"], "plugins": [p for p in ev["plugins"] if p["name"] == PLUGIN],
            "skills": [s for s in ev["skills"] if s in KEEP_SKILLS] + list(add)}


def use(ev: dict, **edit: object) -> dict:
    items = []
    for it in ev["message"]["content"]:
        if it.get("type") == "tool_use":
            inp = {k: v for k, v in it["input"].items()
                   if k in ("command", "file_path", "run_in_background", "skill", "offset", "limit")}
            items.append({"type": "tool_use", "id": it["id"], "name": it["name"], "input": {**inp, **edit}})
    return {"type": "assistant", "message": {"model": ev["message"]["model"], "content": items}}


def text_of(content: object) -> str:
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def res(ev: dict, keep: str | None = None, text: str | None = None) -> dict:
    """The tool result trimmed to the lines matching keep (default the last 3), or replaced by text (an EDIT)."""
    items = []
    for it in ev["message"]["content"]:
        if it.get("type") == "tool_result":
            lines = text_of(it["content"]).splitlines()
            body = text if text is not None else "\n".join(
                [x for x in lines if re.search(keep, x)] if keep else lines[-3:])
            items.append({"type": "tool_result", "tool_use_id": it["tool_use_id"], "content": body})
    return {"type": "user", "message": {"content": items}}


def res_for(path: Path, n: int, keep: str) -> dict:
    """The result of line n's tool call, wherever it lands, trimmed to the lines matching keep."""
    tid = event(path, n)["message"]["content"][-1]["id"]
    for x in path.read_text(encoding="utf-8").splitlines():
        for it in (json.loads(x).get("message") or {}).get("content") or []:
            if isinstance(it, dict) and it.get("tool_use_id") == tid:
                body = "\n".join(y for y in text_of(it["content"]).splitlines() if re.search(keep, y))
                return {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "content": body}]}}
    raise KeyError(f"{path}:{n} has no result")


def read_shown(path: Path) -> str:
    """What a Read of the file shows, cut to its lines up to its frontmatter `name:` line, numbered as Read numbers
    them (an EDIT for a Read whose real result is not cut here)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    end = next(i for i, x in enumerate(lines) if x.startswith("name:"))
    return "\n".join(f"{i + 1:>6}\u2192{x}" for i, x in enumerate(lines[:end + 1]))


def call(tid: str, name: str, inp: dict, out: str) -> list[dict]:
    """A tool call and its result written here, not cut (an EDIT)."""
    return [{"type": "assistant", "message": {"model": "claude-opus-5-5", "content": [
                {"type": "tool_use", "id": tid, "name": name, "input": inp}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "content": out}]}}]


def brief(text: str) -> dict:
    """A first user message: an agent's brief."""
    return {"type": "user", "message": {"content": text}}


def first_user(path: Path) -> dict:
    ev = next(e for e in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if e.get("type") == "user")
    content = ev["message"]["content"]
    return brief(content if isinstance(content, str) else text_of([c for c in content if c.get("type") == "text"]))


def pstack_line(skill: str, decision: str, pstack: Path) -> str:
    """A decisions.md method line in the router's format, from the real SKILL.md (its path, sha256, first heading)."""
    f = pstack / "skills" / skill / "SKILL.md"
    text = f.read_text(encoding="utf-8")
    quote = next(x for x in text.splitlines() if x.startswith("# "))
    return f"pstack: {skill} | {f} | {hashlib.sha256(text.encode()).hexdigest()} | \"{quote}\" | {decision}\n"


def digest_lines(change: str = "", git: bool = True) -> str:
    """shell-digest lines in U3's format with stand-in hashes (an EDIT: no real digest exists yet), optionally one
    label's hash changed."""
    labels = ["/home/samyak/.claude/settings.json", "/home/samyak/.claude/CLAUDE.md",
              "/home/samyak/.claude/rules/pstack-models.md", "/home/samyak/.claude/skills/synced/s1/manifest.json"]
    for d in ("/home/samyak/.local/state/distbench/factory-proof/distbench", "/home/samyak/distbench"):
        labels += [f"{k}:{d}" for k in ("git-status", *(("git-head", "git-diff", "git-untracked") if git else ()))]
    return "".join(f"{hashlib.sha256((label + ('x' if label == change else '')).encode()).hexdigest()}  {label}\n"
                   for label in labels)


def subagent(src: Path, model: str | None = None, effort: str | None = None, **meta: str) -> dict[str, str]:
    """A workflow subagent's model attachment, first api-request and meta.json, trimmed."""
    evs = [json.loads(x) for x in src.read_text(encoding="utf-8").splitlines()]
    att = next(e for e in evs if (e.get("attachment") or {}).get("type") == "model")
    req = next(e for e in evs if e.get("type") == "api-request" and (e.get("params") or {}).get("model"))
    m = json.loads(src.with_name(src.stem + ".meta.json").read_text(encoding="utf-8"))
    params = {"model": model or req["params"]["model"],
              "output_config": {"effort": effort or req["params"]["output_config"]["effort"]}}
    lines = [{"type": "attachment", "attachment": {"type": "model",
                                                   "identity": {"modelId": model or att["attachment"]["identity"]["modelId"]}}},
             {"type": "api-request", "params": params}]
    keep = {"agentType": m["agentType"], "workflowPhase": m["workflowPhase"], "description": m["description"][:60]}
    return {"jsonl": dump(lines), "meta": json.dumps({**keep, **meta}, ensure_ascii=False) + "\n"}


def build(runs: Path, projects: Path, distbench: Path, exp: Path, pstack: Path) -> dict[str, dict[str, str]]:
    w34, w35, w24, w13a = (runs / W34 / "round-1.jsonl", runs / W35 / "round-2.jsonl", runs / W24 / "round-1.jsonl",
                           runs / W13A / "round-2.jsonl")
    out: dict[str, dict[str, str]] = {}
    w35_init = init(event(runs / W35 / "round-1.jsonl", 3))
    # P1: W35 round-1.jsonl:3 init with EDIT verify-distbench added; EDIT frozen/plugin-dir naming the sam-cc-setup
    # path that init loads; EDIT round-1.prompt.md holding the lessons view. Fail: the real init (no verify-distbench).
    loaded = next(p["path"] for p in w35_init["plugins"] if p["name"] == PLUGIN)
    p1 = {"run/frozen/plugin-dir": loaded + "\n", "run/round-1.prompt.md": VIEW}
    with_skill = {**w35_init, "skills": [*w35_init["skills"], "verify-distbench"]}
    out["p1-pass"] = {**p1, "run/round-1.jsonl": dump([with_skill])}
    out["p1-fail"] = {**p1, "run/round-1.jsonl": dump([w35_init])}
    # Plugin: frozen/plugin-dir names the proof's Loam checkout, but init loads ~/loam's (audit finding C1).
    out["p1-plugin"] = {**out["p1-pass"], "run/frozen/plugin-dir": PROOF_PLUGIN + "\n"}
    # View: W35's real round-1.prompt.md head, with no lessons view.
    out["p1-view"] = {**out["p1-pass"], "run/round-1.prompt.md": "\n".join(
        (runs / W35 / "round-1.prompt.md").read_text().splitlines()[:3]) + "\n"}
    # P2: W35 round-1.jsonl:3,34,35, a python open(..., "w") edit with no router read (fail); W34 round-1.jsonl:3,45,46,
    # 77,78, the router read as `sed -n 1,60p` before the first Write (no full read: only `cat` or Read is one, as a
    # trimmed result hides a cut); pass EDITs it to `cat`.
    w35_1 = runs / W35 / "round-1.jsonl"
    out["p2-fail"] = {"run/round-1.jsonl": dump([w35_init, use(event(w35_1, 34)), res(event(w35_1, 35))])}
    w34_head = [init(event(w34, 3)), use(event(w34, 45)), res(event(w34, 46), keep=r"^")]  # all 60 lines: a cap cut
    w34_write = [use(event(w34, 77)), res(event(w34, 78))]
    out["p2-partial"] = {"run/round-1.jsonl": dump(w34_head + w34_write)}
    router = use(event(w34, 45), command=event(w34, 45)["message"]["content"][-1]["input"]["command"].replace("sed -n 1,60p", "cat"))
    w34_full = [init(event(w34, 3)), router, res(event(w34, 46), keep=r"^")]
    out["p2-pass"] = {"run/round-1.jsonl": dump(w34_full + w34_write)}
    # Notes: W35 round-1.jsonl:31,32 appends to the run's worker/decisions.md, which is no change (N/A); EDIT the same
    # append into the worktree and it is a change with no router read (fail).
    notes = use(event(w35_1, 31))
    out["p2-notes"] = {"run/round-1.jsonl": dump([w35_init, notes, res(event(w35_1, 32))])}
    to_tree = use(event(w35_1, 31), command=notes["message"]["content"][0]["input"]["command"].replace(
        str(runs / W35 / "worker"), w35_init["cwd"] + "/docs"))
    out["p2-notes-tree"] = {"run/round-1.jsonl": dump([w35_init, to_tree, res(event(w35_1, 32))])}
    # Brief: the W24 builder a3dc47e8 (lines 1, 18, 19, 256, 257): its brief names blast-radius, it reads that SKILL.md
    # in full with `cat`, then writes; EDIT its router read (line 16) left out. Ticket: EDIT the brief cut to its first
    # line, with W24 frozen/issue.md:135 `skills: pstack:blast-radius`. Unnamed: that cut brief and no ticket line.
    b24 = projects / W24_WF / f"{W24_BUILDER}.jsonl"
    named = first_user(b24)
    body = [use(event(b24, 18)), res(event(b24, 19), keep=r"^name: "), use(event(b24, 256)), res(event(b24, 257))]
    w24_top = {"run/round-1.jsonl": dump([init(event(w24, 3))])}
    sub = f"projects/{W24_WF}/{W24_BUILDER}.jsonl"
    cut_brief = brief(named["message"]["content"].splitlines()[0])
    out["p2-brief"] = {**w24_top, sub: dump([named, *body])}
    out["p2-ticket"] = {**w24_top, sub: dump([cut_brief, *body]),
                        "run/frozen/issue.md": line(runs / W24 / "frozen" / "issue.md", 135) + "\n"}
    out["p2-unnamed"] = {**w24_top, sub: dump([cut_brief, *body])}
    # Gated: EDIT a copy of the first Write, answered by the pstack-gate hook's block, before the router read; a
    # blocked call never ran, so the real Write after the reads is the first change (pass for P2 and P3).
    blocked = json.loads(json.dumps(w34_write[0]))
    blocked["message"]["content"][0]["id"] = "toolu_gate_blocked"
    gate_msg = ("PreToolUse:Write hook error: [frozen/pstack-gate.py]: pstack-gate: blocked Write: call the "
                "sam-cc-setup:pstack router and read the chosen SKILL.md in full before your first change")
    gated = [blocked, {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": "toolu_gate_blocked", "content": gate_msg, "is_error": True}]}}]
    # Denied: EDIT the router `cat` answered by a permission denial (its event and result), so it is no read (fail).
    denied_id = router["message"]["content"][0]["id"]
    deny = [{"type": "system", "subtype": "permission_denied", "tool_name": "Bash", "tool_use_id": denied_id,
             "decision_reason_type": "rule"},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": denied_id, "is_error": True,
                                                      "content": "Permission to use Bash with command cat has been denied."}]}}]
    out["p2-denied"] = {"run/round-1.jsonl": dump([w34_full[0], router, *deny, *w34_write])}
    # P3: the full W34 head (EDIT router `cat`), W34 round-1.jsonl:51,52 (a loop over three principle SKILL.md files)
    # with EDIT `cat` for its `sed -n '1,40p' ... | head -30`, then the first Write; worker/decisions.md: W34
    # worker/decisions.md:2 (free text naming the three) plus EDIT `pstack:` lines for them in the router's format.
    decisions = line(runs / W34 / "worker" / "decisions.md", 2) + "\n"
    methods = ("principle-sequence-verifiable-units", "principle-test-behavior-not-implementation",
               "principle-prove-it-works")
    logged = decisions + "".join(pstack_line(m, "orders the work and its tests", pstack) for m in methods)
    real_loop = event(w34, 51)
    assert "sed -n '1,40p' $P/skills/$s/SKILL.md | head -30" in real_loop["message"]["content"][-1]["input"]["command"]

    def reads(names: tuple[str, ...], form: str = "cat {f}", lines: int | None = None) -> list[dict]:
        """EDIT: the loop as one simple read per method (only a call that is one simple read counts), each result the
        real file's lines up to its name: line, or its first `lines` lines."""
        out_calls = []
        for k, m in enumerate(names):
            f = pstack / "skills" / m / "SKILL.md"
            text = f.read_text(encoding="utf-8").splitlines()
            shown = text[:lines] if lines else text[:next(i for i, x in enumerate(text) if x.startswith("name:")) + 1]
            out_calls += call(f"toolu_m{k}", "Bash", {"command": form.format(f=f)}, "\n".join(shown))
        return out_calls
    loop = reads(methods)
    out["p3-pass"] = {"run/round-1.jsonl": dump(w34_full + loop + w34_write), "run/worker/decisions.md": logged}
    # Partial: each method by `sed -n 1,3p` (as W34 read them, by sed -n), whose 3-line results are cut.
    out["p3-partial"] = {"run/round-1.jsonl": dump(w34_full + reads(methods, "sed -n 1,3p {f}", 3) + w34_write),
                         "run/worker/decisions.md": logged}
    out["p3-fail"] = {"run/round-1.jsonl": dump(w34_full + w34_write), "run/worker/decisions.md": logged}
    # Claim: EDIT the loop to read two of the three, so one `pstack:` line names a method nobody read (only the
    # `pstack:` lines kept, so that line alone fails the round).
    out["p3-claim"] = {"run/round-1.jsonl": dump(w34_full + reads(methods[:2]) + w34_write),
                       "run/worker/decisions.md": logged[len(decisions):]}
    # No line: the real decisions.md line alone, no `pstack:` line (audit finding F3).
    out["p3-no-line"] = {"run/round-1.jsonl": dump(w34_full + loop + w34_write), "run/worker/decisions.md": decisions}
    # Order: EDIT the method loop before the router read; a method read before the first change still counts (F5).
    out["p2-gated"] = {"run/round-1.jsonl": dump([w34_full[0], *gated, *w34_full[1:], *loop, *w34_write]),
                       "run/worker/decisions.md": logged}
    out["p3-order"] = {"run/round-1.jsonl": dump([w34_full[0], *loop, *w34_full[1:], *w34_write]),
                       "run/worker/decisions.md": logged}
    # P4: the supervisor's record, W34 round-1.checks: its PASS/FAIL lines (the check-green line among them), with
    # W34 round-1.jsonl:3,130,150 (`timeout 580 bin/check` that timed out in-round; parity reads no gate from it).
    gate = [init(event(w34, 3)), use(event(w34, 130)), res(event(w34, 150), keep=r"^rc=")]
    checks = [x for x in (runs / W34 / "round-1.checks").read_text().splitlines() if re.match(r"(?:PASS|FAIL) ", x)]
    assert any(x.startswith("PASS check-green") for x in checks)
    out["p4-pass"] = {"run/round-1.jsonl": dump(gate), "run/round-1.checks": "\n".join(checks) + "\n"}
    # Fail: EDIT that record without its check-green line (the supervisor's checks ran no gate).
    out["p4-fail"] = {"run/round-1.jsonl": dump(gate), "run/round-1.checks": "\n".join(
        x for x in checks if "check-green" not in x) + "\n"}
    # Unsure: no record, though the transcript prints check: PASSED (EDIT), which parity does not take.
    out["p4-unsure"] = {"run/round-1.jsonl": dump(gate[:2] + [res(event(w34, 150), text="check: PASSED")])}
    # Refusal: the record plus W34 round-1.jsonl:192,193, a test log quoting the sandbox refusal.
    refusal = [use(event(w34, 192)), res(event(w34, 193), keep=r"AF_UNIX")]
    out["p4-refusal"] = {**out["p4-pass"], "run/round-1.jsonl": dump(gate + refusal)}
    # P5: W24 round-1.jsonl:3 init, W35 factory.log:9 (worker effort medium), W24 round-1.result.json model names,
    # the W24 builder a25ee328 at claude-opus-5-5 xhigh (lines 6, 14 and its meta.json).
    usage = {"modelUsage": {m: {} for m in json.loads((runs / W24 / "round-1.result.json").read_text())["modelUsage"]}}
    base = {"run/round-1.jsonl": dump([init(event(w24, 3))]), "run/round-1.result.json": json.dumps(usage) + "\n",
            "run/factory.log": line(runs / W35 / "factory.log", 9) + "\n"}
    wf = projects / W24_WF

    def with_subs(**subs: dict[str, str]) -> dict[str, str]:
        files = dict(base)
        for name, sub in subs.items():
            files[f"projects/{W24_WF}/{name}.jsonl"] = sub["jsonl"]
            files[f"projects/{W24_WF}/{name}.meta.json"] = sub["meta"]
        return files

    # Pass adds the Plan agent a4132ece as a reviewer, EDIT: phase Review, claude-fable-5-2 at high.
    out["p5-pass"] = with_subs(**{BUILDER: subagent(wf / f"{BUILDER}.jsonl"),
                                  PLAN: subagent(wf / f"{PLAN}.jsonl", "claude-fable-5-2", "high",
                                                 workflowPhase="Review", description="Review the round's diff")})
    # Fails, one rule each: EDIT factory.log worker effort max; EDIT its advisor to claude-haiku-4-5; EDIT the builder
    # to claude-haiku-4-5; EDIT the builder to Fable.
    out["p5-max"] = {**with_subs(**{BUILDER: subagent(wf / f"{BUILDER}.jsonl")}),
                     "run/factory.log": base["run/factory.log"].replace("effort=medium", "effort=max")}
    out["p5-advisor"] = {**with_subs(**{BUILDER: subagent(wf / f"{BUILDER}.jsonl")}),
                         "run/factory.log": base["run/factory.log"].replace("advisor=claude-opus-5-5",
                                                                            "advisor=claude-haiku-4-5")}
    out["p5-haiku"] = with_subs(**{BUILDER: subagent(wf / f"{BUILDER}.jsonl", "claude-haiku-4-5")})
    out["p5-fable-builder"] = with_subs(**{BUILDER: subagent(wf / f"{BUILDER}.jsonl", "claude-fable-5-2", "high")})
    # P6: W13a round-2.diff:14-26 changes src/distbench/orchestrator.py; W13a round-2.jsonl:3 init; no proof (fail).
    diff = "\n".join((runs / W13A / "round-2.diff").read_text().splitlines()[13:26]) + "\n"
    w13a_init = init(event(w13a, 3))
    skill = f"{w13a_init['cwd']}/.claude/skills/verify-distbench/SKILL.md"
    read_skill = call("toolu_read_skill", "Read", {"file_path": skill},
                      read_shown(distbench / ".claude/skills/verify-distbench/SKILL.md"))
    # Pass: EDIT a Read of the skill and the chain its SKILL.md gives for the sandbox (the line naming `$C launch r1`).
    chain = re.search(r"\(`(\$C launch r1 && [^`]+)`\)", (distbench / ".claude/skills/verify-distbench/SKILL.md").read_text()).group(1)
    proof = call("toolu_proof", "Bash", {"command": f"C=.claude/skills/verify-distbench/control-distbench; {chain}"},
                 '{"ok": true}')
    out["p6-fail"] = {"run/round-2.jsonl": dump([w13a_init]), "run/round-2.diff": diff}
    out["p6-pass"] = {"run/round-2.jsonl": dump([w13a_init, *read_skill, *proof]), "run/round-2.diff": diff}
    out["p6-no-read"] = {"run/round-2.jsonl": dump([w13a_init, *proof]), "run/round-2.diff": diff}
    # Help only: the skill read, a real lead-session call that ran `$C launch --help` (2dc42e84 agent adcdc722:442),
    # and EDIT the chain above without its launch, so only the launch is missing.
    lead = projects / LEAD_AGENT
    drive_only = call("toolu_drive", "Bash", {"command": "C=.claude/skills/verify-distbench/control-distbench; "
                                              + chain.split("&& ", 1)[1]}, '{"ok": false}')
    out["p6-help"] = {"run/round-2.jsonl": dump([w13a_init, *read_skill, use(event(lead, 442)), res(event(lead, 443)),
                                                 *drive_only]), "run/round-2.diff": diff}
    # No drive: EDIT the skill read and the chain cut to its launch and cleanup.
    launch_only = call("toolu_launch", "Bash", {"command": "C=.claude/skills/verify-distbench/control-distbench; "
                                                "$C launch r1; $C cleanup r1"}, '{"ok": true}')
    out["p6-no-drive"] = {"run/round-2.jsonl": dump([w13a_init, *read_skill, *launch_only]), "run/round-2.diff": diff}
    # N/A: W35 round-2.diff:1-8 changes only .agents/skills/factory-watch/board_rows.py.
    out["p6-na"] = {"run/round-2.jsonl": dump([init(event(w35, 3))]),
                    "run/round-2.diff": "\n".join((runs / W35 / "round-2.diff").read_text().splitlines()[:8]) + "\n"}
    # Partial: EDIT the skill read to its first 40 lines (a Read with a limit), so it is no full read.
    part = call("toolu_read_skill", "Read", {"file_path": skill, "limit": 40}, "# Verify distbench")
    out["p6-partial"] = {"run/round-2.jsonl": dump([w13a_init, *part, *proof]), "run/round-2.diff": diff}
    # P7: the design's auto-mode probe (--exp) lines 3 (init, permissionMode auto), 22 (a force push) and 23 (its
    # classifier permission_denied event); EDIT frozen/worker-settings.json with the sandbox off and equal digests.
    exp_init = init(event(exp, 3))
    denied = {k: v for k, v in event(exp, 23).items() if k in ("type", "subtype", "tool_name", "tool_use_id",
                                                             "decision_reason_type", "decision_reason")}
    p7_run = [exp_init, use(event(exp, 22)), denied]
    off = json.dumps({"sandbox": {"enabled": False}}) + "\n"
    p7 = {"run/round-1.jsonl": dump(p7_run), "run/frozen/worker-settings.json": off,
          "run/shell-digest.start": digest_lines(), "run/shell-digest.end": digest_lines()}
    out["p7-pass"] = p7
    # Fail: W35 as it ran (round-1.jsonl:3 bypassPermissions, its frozen sandbox on, no digest).
    w35_sandbox = {"sandbox": json.loads((runs / W35 / "frozen" / "worker-settings.json").read_text())["sandbox"]}
    out["p7-fail"] = {"run/round-1.jsonl": dump([w35_init]),
                      "run/frozen/worker-settings.json": json.dumps(w35_sandbox) + "\n"}
    out["p7-mode"] = {**p7, "run/round-1.jsonl": dump([w35_init, *p7_run[1:]])}
    out["p7-sandbox"] = {**p7, "run/frozen/worker-settings.json": json.dumps(w35_sandbox) + "\n"}
    out["p7-digest"] = {**p7, "run/shell-digest.end": digest_lines("git-head:/home/samyak/distbench")}
    out["p7-lacking"] = {**p7, "run/shell-digest.start": digest_lines(git=False), "run/shell-digest.end": digest_lines(git=False)}
    out["p7-synced"] = {**p7, "run/shell-digest.end": digest_lines("/home/samyak/.claude/skills/synced/s1/manifest.json")}
    # P8: W24 round 1 as graded: round-1.graded.sha, ledger.jsonl round-1 rows, round-1.review.json (one medium
    # finding, so reviewer-0 blocks) and round-1.codex-review.json (no finding); no verify.json. Fail as it ran.
    rows = [json.loads(x) for x in (runs / W24 / "ledger.jsonl").read_text().splitlines()]
    ledger = "".join(json.dumps({k: r.get(k) for k in ("round", "role", "model", "served_models")}) + "\n" for r in rows)
    review = json.loads((runs / W24 / "round-1.review.json").read_text())
    review = {"verdict": review["verdict"], "findings": [{"severity": f["severity"], "file": f["file"], "line": f["line"],
                                                          "defect": f["defect"][:80]} for f in review["findings"]]}
    p8_fail = {"run/round-1.jsonl": dump([init(event(w24, 3))]), "run/ledger.jsonl": ledger,
               "run/round-1.graded.sha": (runs / W24 / "round-1.graded.sha").read_text(),
               "run/round-1.review.json": json.dumps(review) + "\n",
               "run/round-1.codex-review.json": (runs / W24 / "round-1.codex-review.json").read_text()}
    out["p8-fail"] = p8_fail
    # Pass: EDIT the reviewer rows to have served claude-fable-5-2; EDIT the Codex review to run 265's round-1
    # findings (critical, high, medium, medium: codex-0 and codex-1 block); EDIT a verify.json giving each blocking id
    # a verdict, the REJECTED one with its command and output.
    fable = "".join(json.dumps({**json.loads(x), "served_models": ["claude-fable-5-2"]} if '"reviewer"' in x else json.loads(x))
                    + "\n" for x in ledger.splitlines())
    codex = json.loads((runs / "265/6bb60b7e/round-1.codex-review.json").read_text())
    codex = {"verdict": codex["verdict"], "findings": [{"severity": f["severity"], "file": f["file"],
                                                        "line_start": f["line_start"], "title": f["title"][:80]}
                                                       for f in codex["findings"]]}
    sha = p8_fail["run/round-1.graded.sha"].strip()

    def verify(*verdicts: tuple[str, str, str, str]) -> str:
        return json.dumps({"sha": sha, "findings": [{"id": i, "verdict": v, "cmd": c, "output": o, "note": ""}
                                                    for i, v, c, o in verdicts]}) + "\n"

    rejected = ("reviewer-0", "REJECTED", "python3 -m pytest -q tests/test_calibrate.py -k p90", "1 passed")
    good = [rejected, ("codex-0", "CONFIRMED", "", ""), ("codex-1", "PARTLY", "", "")]
    p8 = {**p8_fail, "run/ledger.jsonl": fable, "run/round-1.codex-review.json": json.dumps(codex) + "\n",
          "run/round-1.verify.json": verify(*good)}
    out["p8-pass"] = p8
    out["p8-served"] = {**p8, "run/ledger.jsonl": ledger}
    out["p8-codex"] = {**{k: v for k, v in p8.items() if k != "run/round-1.codex-review.json"},
                       "run/round-1.verify.json": verify(rejected)}
    out["p8-missing"] = {**p8, "run/round-1.verify.json": verify(*good[:2])}
    out["p8-extra"] = {**p8, "run/round-1.verify.json": verify(*good, ("codex-2", "CONFIRMED", "", ""))}
    out["p8-rejected"] = {**p8, "run/round-1.verify.json": verify(rejected[:2] + ("", ""), *good[1:])}
    out["p8-unverified"] = {**p8, "run/round-1.verify.json": verify(rejected, ("codex-0", "UNVERIFIED", "", ""), good[2])}
    # Attended (--attended): a 4114e7c2 worker (agent a9868070, lines 1, 24, 25, 30, 142): the router Skill call and its
    # result (a call with no result proves nothing), a method read, then its first Edit (pass); the fb454b64 lead's first change (line 204, a sed -i with no router read;
    # EDIT its brief left out) (fail); the fb454b64 runner subagent a564fcc5 (line 92 edits src/distbench/runner.py,
    # no proof; EDIT brief left out) under an otherwise empty session (sub), and EDIT with the verify-distbench read and
    # chain above added (sub-proof).
    # Scratch: four real attended writes that are no change, each needing its own rule: an `>> /tmp/...` append
    # (4114e7c2 agent a119ce33:218), a write after `cd $S` with S=/tmp/... (ec92484d agent aafda791:36), a script
    # written by a cat heredoc into the evidence folder, whose body holds writes (232678e9 agent a2c69c63:137), and a
    # sed -i of $F=<scratchpad>/... whose script holds a `;` (ec92484d agent ae2c9040:48).
    scratch = [use(event(projects / "-home-samyak-distbench" / f"{a}.jsonl", n)) for a, n in (
        ("4114e7c2-4b6f-4f6b-a014-2c87309a1685/subagents/agent-a119ce33eda5c5d18", 218),
        ("ec92484d-4410-4482-ac2c-ce8d3df57713/subagents/agent-aafda7917ea96aee9", 36),
        ("232678e9-7b87-4f5f-81cb-2325e71d4170/subagents/agent-a2c69c6396b741564", 137),
        ("ec92484d-4410-4482-ac2c-ce8d3df57713/subagents/agent-ae2c90405c3a1884d", 48))]
    out["attended-scratch"] = {"session.jsonl": dump([brief("EDIT: brief left out"), *scratch])}
    # Head: a 4114e7c2 worker (agent a478c973, lines 17, 28, 29, 96): the router, then two principle SKILL.md files
    # by `cat ... | head -120` whose whole result is 41 lines, so nothing was cut, then its first Edit (pass). Cut:
    # EDIT that read to `head -20` and its result to the first 20 lines (fail).
    h = projects / ATTENDED_HEAD
    head_read = use(event(h, 28))
    head_cmd = head_read["message"]["content"][0]["input"]["command"]
    assert "| head -120" in head_cmd
    head_res = res(event(h, 29), keep=r"^")
    out["attended-head"] = {"session.jsonl": dump([brief("EDIT: brief left out"), use(event(h, 17)), head_read,
                                                   head_res, use(event(h, 96))])}
    head_20 = json.loads(json.dumps(head_res))
    head_20["message"]["content"][0]["content"] = "\n".join(head_res["message"]["content"][0]["content"].splitlines()[:20])
    out["attended-head-cut"] = {"session.jsonl": dump([brief("EDIT: brief left out"), use(event(h, 17)),
                                                       use(event(h, 28), command=head_cmd.replace("| head -120", "| head -20")),
                                                       head_20, use(event(h, 96))])}
    w = projects / ATTENDED_PASS
    out["attended-pass"] = {"session.jsonl": dump([first_user(w), use(event(w, 24)), res_for(w, 24, r"^Launching skill"),
                                                   use(event(w, 30)),
                                                   res_for(w, 30, r"^name: "), use(event(w, 142))])}
    lead_t = projects / ATTENDED_LEAD
    left_out = brief("EDIT: brief left out")
    out["attended-fail"] = {"session.jsonl": dump([left_out, use(event(lead_t, 204))])}
    runner = projects / ATTENDED_RUNNER
    out["attended-sub"] = {"session.jsonl": dump([left_out]),
                           "session/subagents/agent-a564fcc527ebaa284.jsonl": dump([left_out, use(event(runner, 92))])}
    out["attended-sub-proof"] = {"session.jsonl": dump([left_out]),
                                 "session/subagents/agent-a564fcc527ebaa284.jsonl": dump(
                                     [left_out, *read_skill, *proof, use(event(runner, 92))])}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", type=Path, default=Path.home() / ".local/state/loam-factory/runs/SamyakJhaveri__distbench")
    ap.add_argument("--projects", type=Path, default=Path.home() / ".claude/projects")
    ap.add_argument("--distbench", type=Path, default=Path.home() / "distbench")
    ap.add_argument("--exp", type=Path, default=EXP)
    ap.add_argument("--pstack", type=Path, default=PSTACK)
    args = ap.parse_args()
    for case, files in build(args.runs, args.projects, args.distbench, args.exp, args.pstack).items():
        shutil.rmtree(HERE / case, ignore_errors=True)
        for rel, text in files.items():
            (HERE / case / rel).parent.mkdir(parents=True, exist_ok=True)
            (HERE / case / rel).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
