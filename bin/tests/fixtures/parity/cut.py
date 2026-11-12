#!/usr/bin/env python3
"""Cut the bin/factory-parity test fixtures from real factory runs and transcripts on jhaveris.

  python3 bin/tests/fixtures/parity/cut.py [--runs DIR] [--projects DIR] [--distbench DIR]

Each case folder `<case>/run` (plus `<case>/projects` when it has subagents) holds a few lines cut from the files
named in its comment, trimmed to the fields bin/factory-parity reads. A line marked EDIT differs from its source
as the comment says, so a behaviour has a passing case where no real run passes yet. Re-running it on jhaveris
rewrites the same bytes. The `pass` folder is hand-written (every behaviour passing at once) and not cut here.
"""
from __future__ import annotations

import argparse
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
KEEP_SKILLS = {"sam-cc-setup:pstack", "pstack:tdd", "pstack:principle-sequence-verifiable-units",
               "pstack:principle-test-behavior-not-implementation", "pstack:principle-prove-it-works"}


def line(path: Path, n: int) -> str:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[n - 1]


def event(path: Path, n: int) -> dict:
    return json.loads(line(path, n))


def dump(events: list[dict]) -> str:
    return "".join(json.dumps(e, separators=(",", ":"), ensure_ascii=False) + "\n" for e in events)


def init(ev: dict, add: tuple[str, ...] = ()) -> dict:
    return {"type": "system", "subtype": "init", "cwd": ev["cwd"], "session_id": ev["session_id"], "model": ev["model"],
            "skills": [s for s in ev["skills"] if s in KEEP_SKILLS] + list(add)}


def use(ev: dict, **edit: object) -> dict:
    items = []
    for it in ev["message"]["content"]:
        if it.get("type") == "tool_use":
            inp = {k: v for k, v in it["input"].items() if k in ("command", "file_path", "run_in_background")}
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


def call(tid: str, name: str, inp: dict, out: str) -> list[dict]:
    """A tool call and its result written here, not cut (an EDIT)."""
    return [{"type": "assistant", "message": {"model": "claude-opus-5-5", "content": [
                {"type": "tool_use", "id": tid, "name": name, "input": inp}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "content": out}]}}]


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


def build(runs: Path, projects: Path, distbench: Path) -> dict[str, dict[str, str]]:
    w34, w35, w24, w13a = (runs / W34 / "round-1.jsonl", runs / W35 / "round-2.jsonl", runs / W24 / "round-1.jsonl",
                           runs / W13A / "round-2.jsonl")
    out: dict[str, dict[str, str]] = {}
    w35_init = init(event(runs / W35 / "round-1.jsonl", 3))
    # P1: W35 round-1.jsonl:3, the init line with no verify-distbench; pass: EDIT verify-distbench added.
    out["p1-fail"] = {"run/round-1.jsonl": dump([w35_init])}
    out["p1-pass"] = {"run/round-1.jsonl": dump([{**w35_init, "skills": [*w35_init["skills"], "verify-distbench"]}])}
    # P2: W35 round-2.jsonl:3,8,9, a sed -i with no router read; pass: W34 round-1.jsonl:3,45,46,77,78, the router
    # read (sed -n 1,60p of its SKILL.md) before the first Write.
    out["p2-fail"] = {"run/round-1.jsonl": dump([init(event(w35, 3)), use(event(w35, 8)), res(event(w35, 9))])}
    w34_head = [init(event(w34, 3)), use(event(w34, 45)), res(event(w34, 46))]
    w34_write = [use(event(w34, 77)), res(event(w34, 78))]
    out["p2-pass"] = {"run/round-1.jsonl": dump(w34_head + w34_write)}
    # P3: W34 round-1.jsonl:3,45,46,51,52,77,78, router, a loop reading three principle SKILL.md files, then the
    # first Write; W34 worker/decisions.md:2 names those three. Fail: the same lines without 51-52 (the loop).
    decisions = line(runs / W34 / "worker" / "decisions.md", 2) + "\n"
    loop = [use(event(w34, 51)), res(event(w34, 52), keep=r"^name: ")]
    out["p3-pass"] = {"run/round-1.jsonl": dump(w34_head + loop + w34_write), "run/worker/decisions.md": decisions}
    out["p3-fail"] = {"run/round-1.jsonl": dump(w34_head + w34_write), "run/worker/decisions.md": decisions}
    # Claim: EDIT the loop to read two of the three, so only decisions.md's third name has no read.
    two = use(event(w34, 51))
    two["message"]["content"][0]["input"]["command"] = two["message"]["content"][0]["input"]["command"].replace(
        " principle-prove-it-works", "")
    out["p3-claim"] = {"run/round-1.jsonl": dump(w34_head + [two, res(event(w34, 52), keep=r"^name: ")] + w34_write),
                       "run/worker/decisions.md": decisions}
    # P4: W34 round-1.jsonl:3,130,150, `timeout 580 bin/check` that timed out (rc=124, no check: line).
    gate = use(event(w34, 130))
    out["p4-fail"] = {"run/round-1.jsonl": dump([init(event(w34, 3)), gate, res(event(w34, 150), keep=r"^rc=")])}
    # Pass: EDIT the result to bin/check's own last lines (distbench bin/check:162-166).
    passed = res(event(w34, 150), text="rc=0\nSKIPPED: none\ncheck: PASSED")
    out["p4-pass"] = {"run/round-1.jsonl": dump([init(event(w34, 3)), gate, passed])}
    # Refusal: the passing gate plus W34 round-1.jsonl:192,193, a test log quoting the sandbox refusal.
    refusal = [use(event(w34, 192)), res(event(w34, 193), keep=r"AF_UNIX")]
    out["p4-refusal"] = {"run/round-1.jsonl": dump([init(event(w34, 3)), gate, passed, *refusal])}
    # Background: EDIT the W34 gate to run in the background, with the harness reply of run 288 round-2.jsonl:49,
    # then an EDIT Read of that output file showing check: PASSED.
    bg = res(event(runs / "288/27f76148/round-2.jsonl", 49))
    bg["message"]["content"][0]["tool_use_id"] = gate["message"]["content"][0]["id"]
    bg_path = re.search(r"written to: (\S+?)\.?(?=\s|$)", bg["message"]["content"][0]["content"]).group(1)
    bg_head = [init(event(w34, 3)), use(event(w34, 130), command="bin/check", run_in_background=True), bg]
    out["p4-background"] = {"run/round-1.jsonl": dump(
        bg_head + call("toolu_read_bg", "Read", {"file_path": bg_path}, "SKIPPED: none\ncheck: PASSED"))}
    # Fail: the same background gate, but the later check: PASSED is read from another file, not its output.
    out["p4-background-other"] = {"run/round-1.jsonl": dump(
        bg_head + call("toolu_read_old", "Read", {"file_path": "/tmp/old-check.log"}, "SKIPPED: none\ncheck: PASSED"))}
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
    read_skill = call("toolu_read_skill", "Read", {"file_path": skill}, "# Verify distbench")
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
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", type=Path, default=Path.home() / ".local/state/loam-factory/runs/SamyakJhaveri__distbench")
    ap.add_argument("--projects", type=Path, default=Path.home() / ".claude/projects")
    ap.add_argument("--distbench", type=Path, default=Path.home() / "distbench")
    args = ap.parse_args()
    for case, files in build(args.runs, args.projects, args.distbench).items():
        shutil.rmtree(HERE / case, ignore_errors=True)
        for rel, text in files.items():
            (HERE / case / rel).parent.mkdir(parents=True, exist_ok=True)
            (HERE / case / rel).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
