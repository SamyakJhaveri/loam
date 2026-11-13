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

First, and before any of that: with LOAM_WORKER_GATE=supervisor (worker-settings-native.json sets it, so only a non-Loam
target's native worker has it) a Bash call that runs bin/check or the full test suite is blocked (exit 2, one stderr
line): the supervisor runs the full gate once after the graders pass, and a worker that runs it itself loses its 36
minutes and a gate slot (L01 run 2 round 1, 13 Nov: 73 min in two direct calls and 36 more polling a done-check script
that ran it). A call runs bin/check when bin/check (any path ending in it) is a command word: at the start of a line,
after `;` `&` `|` `(` `$(` or a backtick, after `timeout N`, `nohup`, `env X=Y`, `X=Y`, `guard` (a done-check's
wrapper), `time`, `exec`, `command`, `nice`, `then`, `do`, `else`, `if`, `!` or `{`, outside quotes and comments (a
double-quoted `$( )` or backtick part counts, and so does one in a heredoc with an unquoted delimiter); or inside `bash
-c`/`sh -c` text; or in a heredoc fed to a shell; or in a shell script file the call runs (`bash f`, `bash -o pipefail
f`, `sh f`, `source f`, `. f`, `./f.sh`; not `bash -n f`). The script path has its quotes dropped and its variables
filled in from the hook's environment and the call's own earlier `NAME=value` assignments (`W=...; bash
$W/done-checks.sh`); a path still holding a `$` counts as a run (fail closed), and so does any `.../frozen/checks.sh`
run without LOAM_HOOK. A relative path is read against the payload's cwd, each folder an earlier `cd` names, and the
folder of each script it runs inside, three files deep. A script run with a non-empty LOAM_HOOK (`LOAM_HOOK=1 bash f`,
or after `export LOAM_HOOK=1`) does not run its `guard bin/check` lines when it holds lib.sh's guard, which skips
exactly that form under LOAM_HOOK, so a worker may run the frozen done-checks block that way (PR 738); a gate call in
any other form there still counts. The full suite is pytest (`pytest`, `python -m pytest`) naming no test path but
`tests`, except `--co`. A heredoc fed to anything else is a file's text, not commands, so writing such a script runs;
running it is blocked. Reading bin/check (cat, sed, grep, git show) runs, as does every call when the variable is unset
(a Loam target's worker, any session outside the factory), and so does a quoted mention (`pgrep -af "pytest|bin/check"`,
a commit message). It is a pattern check on the command text, not a shell parser.
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
       "log it as `pstack: ...` in decisions.md (a read counts when it is the Read tool, or a Bash call that is only "
       "`cat <file>`, and its result shows the file)")


FULL_GATE = "BLOCKED: the supervisor runs bin/check once after the graders pass; prove the change with focused pytest"
_WRAP = (r"(?:(?:timeout|nohup|guard|time|exec|command|nice|env|then|do|else|if|!|\{)(?:\s+(?:-\S+|\d[\d.]*[smhd]?))*"
         r"|[A-Za-z_]\w*=[^\s()`;&|]*)\s+")
_START = r"(?:^|[;&|(`])[ \t]*(?:" + _WRAP + r")*"
RUNS_GATE = re.compile(_START + r"(?:[\w.~${}/-]*/)?bin/check(?![\w.-])", re.M)
PYTEST = re.compile(_START + r"(?:[\w.~/-]*/)?(?:python[\d.]*\s+(?:-\w+\s+)*-m\s+)?pytest(?![\w.-])([^;&|)\n]*)", re.M)
SHELL = r"(?:[\w./-]*/)?(?:ba|da|k|z)?sh"
OPTS = r"((?:\s+(?:[-+]\w*[oO]\s+\w+|-[\w-]+))*)"  # shell options, `-o pipefail` with its argument
SHELL_C = re.compile(r"(?<![\w.-])" + SHELL + r"(?:\s+(?:[-+]\w*[oO]\s+\w+|-\w+))*?\s+-\w*c\w*\s+"
                     r"(?:'([^']*)'|\"((?:[^\"\\]|\\.)*)\"|([^\s;&|]+))")
SCRIPT = re.compile(_START + r"(?:(?:" + SHELL + OPTS + r"|source|\.)"
                    r"\s+([^\s;&|<>()`]+)"
                    r"|((?:[\w.~/-]*/)?[\w.-]+\.sh)(?![\w.-]))", re.M)
HEREDOC_OPEN = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_]\w*)\1")
FED_TO_SHELL = re.compile(r"(?<![\w.-])" + SHELL + OPTS + r"\s*$")
HOOK_ON = r"LOAM_HOOK=(?!''|\"\"|[\s;&|)]|$)"  # a non-empty LOAM_HOOK
GUARDED_GATE = re.compile(r"(?<![\w.-])guard[ \t]+bin/check(?![\w./-])")  # the one form lib.sh's guard skips under it
LIB_GUARD = re.compile(r'LOAM_HOOK.*"\$\{1:-\}" = bin/check \] && return 0')  # lib.sh's skip, as criteria.py reads it
ASSIGN = re.compile(r"(?:^|[\s;&|])([A-Za-z_]\w*)=([^\s;&|]*)")  # each NAME=value, `X=1 W=..` and `export W=..` too
QUOTED = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
COMMENT = re.compile(QUOTED.pattern + r"|(?<![^\s;&|(])#[^\n]*")  # a quote, or a comment outside quotes
SUBST = r"\$\([^()]*\)|`[^`]*`"  # a command substitution, which runs inside double quotes and expanding heredocs
CD = re.compile(r"(?:^|[;&|(\n])\s*cd\s+([^\s;&|)]+)")


def unquoted(text: str) -> str:
    """text with quoted strings blanked to x's, keeping a double-quoted one's $( ) and backtick parts, which run."""
    def blank(q: re.Match[str]) -> str:
        s = q.group(0)
        if s[0] == "'":
            return "'" + "x" * (len(s) - 2) + "'"
        keep = [m.span() for m in re.finditer(SUBST, s)]
        return "".join(c if any(a <= i < b for a, b in keep) or i in (0, len(s) - 1) else "x" for i, c in enumerate(s))
    return QUOTED.sub(blank, text)


def commands(text: str) -> str:
    """text without comments (an apostrophe there would pair with a later quote) and the bodies of heredocs fed to
    anything but a shell, which are a file's text, not commands, except an expanding one's command substitutions."""
    text = text.replace("\\\n", " ")  # a continued line is one command
    text = COMMENT.sub(lambda q: q.group(0) if q.group(0)[0] in "'\"" else "", text)
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC_OPEN.finditer(line):
            body = []
            while i < len(lines) and lines[i].strip() != m.group(2):
                body.append(lines[i])
                i += 1
            i += 1
            if FED_TO_SHELL.search(line[:m.start()]):
                out.extend(body)
            elif not m.group(1):
                out.extend(re.findall(SUBST, "\n".join(body)))
    return "\n".join(out)


def expand(word: str, before: str) -> str:
    """word unquoted, with ~ and each $NAME or ${NAME} set in the environment or assigned in the text before it filled
    in; a name set nowhere keeps its $."""
    env = {**os.environ, **{k: v.strip("'\"") for k, v in ASSIGN.findall(before)}}
    word = os.path.expanduser(word.strip("'\""))
    return re.sub(r"\$(?:\{(\w+)\}|(\w+))", lambda v: env.get(v[1] or v[2], v[0]), word)


def runs_full_gate(command: str, dirs: tuple[Path, ...], depth: int = 0, hook: bool = False) -> bool:
    """True when command (Bash text, or a script file's text, run with LOAM_HOOK set when hook) runs bin/check or
    the full suite; a
    relative script path is read against each of dirs (the call's cwd, then each enclosing script's folder, which a
    script may cd to); see the module docstring."""
    if depth > 3:
        return False
    text = commands(command)
    scan = unquoted(text)
    if RUNS_GATE.search(GUARDED_GATE.sub("guard x", scan) if hook and LIB_GUARD.search(text) else scan):
        return True
    for m in PYTEST.finditer(scan):  # naming no test path but tests/, pytest runs the full suite, as long as the gate
        if re.search(r"\bcommand\s+-[vV]\b|\s--co(?:llect-only)?(?!\S)", m.group(0)):
            continue  # `command -v pytest` only looks it up; --co only lists the tests
        words = [w.strip("'\"") for w in re.sub(r"\d*[<>]+&?\s*\S*", " ", text[m.start(1):m.end(1)]).split()]
        targets = [re.sub(r"^(?:\./)+|/+$", "", w) for w in words if not w.startswith("-") and (  # not /tmp/x.xml, a=b
            re.search(r"\.py|::|\$", w) or "/" in w and not w.startswith("/") and "=" not in w or w == "tests")]
        if all(t == "tests" for t in targets):
            return True
    for m in SHELL_C.finditer(text):
        body = m.group(1) if m.group(1) is not None else m.group(2) if m.group(2) is not None else m.group(3)
        if m.group(2) is not None:  # the calling shell fills in a double-quoted body's variables
            body = expand(re.sub(r"\\(.)", r"\1", body), text[:m.start()])
        if runs_full_gate(body, dirs, depth + 1, hook):
            return True
    for m in SCRIPT.finditer(text):
        if re.search(r"(?<![\w-])-[a-z]*[cn]", m.group(1) or ""):
            continue  # `bash -n f` only parses f; `bash -c` runs text, read above
        hooked = hook or bool(re.search(r"(?<![\w-])" + HOOK_ON, m.group(0))
                              or re.search(r"(?<![\w-])export\s+" + HOOK_ON, text[:m.start()]))
        before = text[:m.start()]
        name = expand(m.group(2) or m.group(3), before)
        if "$" in name:
            return True  # a script path the hook cannot resolve: fail closed
        here = dirs
        for cd in (expand(cd, before) for cd in CD.findall(before)):
            here += tuple(d / cd for d in here) if "$" not in cd else ()  # each cd from every folder reached so far
        for path in [Path(name)] if name.startswith("/") else [d / name for d in here]:
            if re.search(r"(?:^|/)bin/check$", path.as_posix()) or not hooked and name.endswith("/frozen/checks.sh"):
                return True
            try:
                if path.is_file() and path.stat().st_size < 1 << 20 and runs_full_gate(
                        path.read_text(encoding="utf-8", errors="replace"), (*dirs, path.parent), depth + 1, hooked):
                    return True
            except OSError:
                continue
    return False


def full_gate(payload: dict) -> str | None:
    """The block message when this worker may not run bin/check and the call runs it, else None."""
    if os.environ.get("LOAM_WORKER_GATE") != "supervisor" or payload.get("tool_name") != "Bash":
        return None
    command = str((payload.get("tool_input") or {}).get("command", ""))
    return FULL_GATE if runs_full_gate(command, (Path(payload.get("cwd") or os.getcwd()),)) else None


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
        message = full_gate(payload) or verdict(payload, load_parity(), HERE.parent if HERE.name == "frozen" else None)
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
