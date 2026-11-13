#!/usr/bin/env python3
"""pstack-gate.py - Claude Code PreToolUse hook: no file change before the pstack router and a method are read.

Requirement (c) of docs/research/2026-11-12-distbench-priming/design-pick.md, enforced in the round instead of graded after it.
Reads the hook payload on stdin. A call that bin/factory-parity's changes() calls a file change is blocked
(exit 2, one stderr line naming the fix) unless parity's P2 (router) and P3 (method) pass for the calling transcript
so far with this call as its next one. Any other call, and any change once they pass, exits 0.

The calling transcript is the payload's transcript_path, or for a subagent (agent_id set)
`<transcript_path without .jsonl>/subagents/**/agent-<agent_id>.jsonl` (a Workflow agent's is under
workflows/<run>/), read beside the main one (whose skill listing names the pstack methods). A call an earlier run of this hook blocked never ran, so it is left out: its tool result
holds BLOCKED. The rules (what a change is, what a router or method read is, decisions.md) are parity's alone:
factory-parity is loaded from this file's folder (a run's frozen/) or its parent (bin/ in a checkout).
In a run's frozen/ folder the run is the parent folder: P3 reads its worker/decisions.md, and the calling round is one
more than its highest finished round-N.jsonl. Elsewhere there is no run and no decisions.md part.

Fails open: when the transcript or parity cannot be read, or this host has no pstack method file or no router (no
change could ever pass), one stderr line says so and the call goes ahead (exit 0), so a hook bug or a host without
pstack never wedges a run; parity grades the round afterwards either way.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
BLOCKED = "pstack-gate: blocked"
FIX = ("call the sam-cc-setup:pstack router and read the chosen SKILL.md in full before your first change; "
       "log it as `pstack: ...` in decisions.md")


def load_parity():
    for path in (HERE / "factory-parity", HERE.parent / "factory-parity"):
        if path.is_file():
            loader = importlib.machinery.SourceFileLoader("factory_parity", str(path))
            module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
            loader.exec_module(module)
            return module
    raise FileNotFoundError(f"no factory-parity in {HERE} or {HERE.parent}")


def missing_pstack(run: Path | None) -> str | None:
    """What of pstack this host lacks, or None: a method file under an installed pstack plugin's skills/, and the
    router where bin/factory's router_file finds it (the run's frozen/plugin-dir, else under the seed-skills
    marketplace's installLocation)."""
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")

    def read(name: str) -> dict:
        try:
            data = json.loads((config / "plugins" / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    plugins = read("installed_plugins.json").get("plugins") or {}
    methods = [Path(e["installPath"]) / "skills" for key, v in plugins.items() if key.startswith("pstack@")
               for e in v if isinstance(e, dict) and isinstance(e.get("installPath"), str)]
    if not any(next(d.glob("*/SKILL.md"), None) for d in methods):
        return f"no pstack plugin with a skills/<name>/SKILL.md in {config}/plugins/installed_plugins.json"
    plugin_dir = run / "frozen" / "plugin-dir" if run else None
    if plugin_dir and plugin_dir.is_file():
        router = Path(plugin_dir.read_text(encoding="utf-8").strip()) / "skills" / "pstack" / "SKILL.md"
    else:
        loc = (read("known_marketplaces.json").get("seed-skills") or {}).get("installLocation") or ""
        router = Path(loc) / "sam-cc-setup" / "skills" / "pstack" / "SKILL.md"
    if not (router.is_absolute() and router.is_file()):
        return f"no pstack router at {router}"
    return None


def so_far(fp, path: Path, label: str, top: bool, projects: Path, pending: tuple[str, str, dict] | None = None):
    """Parity's Transcript of path without the calls this hook blocked, ending in pending (id, name, input) when
    given: at PreToolUse the file does not hold the pending call yet (Claude Code 2.1.322)."""
    t = fp.Transcript(path, label, top, projects)
    keep = [i for i, tid in enumerate(t.ids) if BLOCKED not in (t.results.get(tid) or (0, ""))[1]]
    t.calls, t.ids = [t.calls[i] for i in keep], [t.ids[i] for i in keep]
    if pending:
        t.calls.append((0, pending[1], pending[2]))
        t.ids.append(pending[0])
    return t


def verdict(payload: dict, fp, run: Path | None) -> str | None:
    """The block message for this call, or None to let it run."""
    name, inp = str(payload.get("tool_name", "")), payload.get("tool_input") or {}
    what = fp.changes(name, inp)
    if not what:
        return None
    missing = missing_pstack(run)
    if missing:
        print(f"pstack-gate: not gating this call, {missing}", file=sys.stderr)
        return None
    main = Path(payload["transcript_path"])
    projects = main.parent.parent
    pending = (str(payload.get("tool_use_id", "")), name, inp)
    agent = payload.get("agent_id")
    if agent:
        sub = main.with_suffix("") / "subagents" / f"agent-{agent}.jsonl"
        sub = next(main.with_suffix("").glob(f"subagents/**/agent-{agent}.jsonl"), sub)  # a Workflow's: workflows/<run>/
        caller = so_far(fp, sub, sub.name, False, projects, pending)
        top = so_far(fp, main, main.name, True, projects)
        transcripts = [caller, top]
    else:
        caller = top = so_far(fp, main, main.name, True, projects, pending)
        transcripts = [caller]
    # The round being run: worker_round's last `Round N` header in decisions.md, written before each call. A relaunch
    # reruns a round whose round-N.jsonl already exists, so the highest round file + 1 is only the fallback.
    decisions = run / "worker" / "decisions.md" if run else None
    headers = re.findall(r"(?m)^Round (\d+)$", decisions.read_text(encoding="utf-8", errors="replace")) \
        if decisions and decisions.is_file() else []
    finished = [int(m.group(1)) for p in run.glob("round-*.jsonl") if (m := fp.ROUND_FILE.fullmatch(p.name))] if run else []
    n = int(headers[-1]) if headers else max(finished, default=0) + 1
    rnd = SimpleNamespace(n=n, top=top, subs=transcripts[1:], transcripts=transcripts)
    names = top.skills[1] if top.skills else []
    view = SimpleNamespace(rounds=[rnd], path=run or HERE / "no-run", attended=run is None, ticket="", gate=True,
                           pstack={s.split(":", 1)[1] for s in names if s.startswith("pstack:")})
    for check in (fp.p2, fp.p3):
        status, evidence = check(view)
        if status == "FAIL":
            return f"{BLOCKED} {what}: {FIX}. Parity: {' '.join(evidence.split())[:400]}"
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        fp = load_parity()
        message = verdict(payload, fp, HERE.parent if HERE.name == "frozen" else None)
    except Exception as e:  # fail open: a hook bug or an unreadable transcript never stops the call
        print(f"pstack-gate: not gating this call, could not read the transcript or parity ({type(e).__name__}: {e})",
              file=sys.stderr)
        return 0
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
