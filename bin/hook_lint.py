#!/usr/bin/env python3
"""Fail on three hook defects: a block on an event that cannot block, an unquoted variable in rm, and eval of hook input.

Usage: hook_lint.py <settings.json> <hooks-dir>

The settings' `hooks` block gives each script its events: any word of a command whose basename names a
file in hooks-dir registers that file on the event. Each registered script is then linted:

- block-on-nonblocking: every event the script is registered on is in NONBLOCKING, and a line that is
  not a comment prints a "decision": "block" key or exits 2. Claude Code ignores both there, so the hook
  guards nothing while it reads as a guard.
- unquoted-rm: an `rm` argument holds a $VAR or ${VAR} outside quotes; an empty or spaced value then
  deletes the wrong path.
- eval-input: the script reads stdin (`read`, /dev/stdin, or a `cat` or `jq` given no file and not fed by
  a pipe or <, where an output redirect such as 2>/dev/null is not a file and a loop fed by `done <` or a
  pipe does not read stdin) and runs `eval`, so the hook input can run as code.

The shell rules reuse bin/shell_lint.py's quote walk, so text inside a multi-line string or a heredoc
is not read as code.
Each finding prints as `HOOKLINT <file>:<line> <rule>`. Exit status: 0 when nothing is found, 1 otherwise.
"""

from __future__ import annotations

import json
import pathlib
import re
import shlex
import sys

from shell_lint import ASSIGN, ENDS, RUNS, commands, heredocs_in, split, words

# Events that can neither honor exit 2 nor take a JSON decision, per code.claude.com/docs/en/hooks
# (2026-10-30). An event not named here may block, so the lint never flags on a guess.
NONBLOCKING = {"SessionStart", "SessionEnd", "PostModelSwitch", "PostCompact", "Notification", "SubagentStart",
               "Setup", "CwdChanged", "DirectoryAdded", "FileChanged", "InstructionsLoaded", "StopFailure",
               "PermissionDenied", "MessageDisplay"}
BLOCKS = re.compile(r"""\\?["']decision\\?["']\s*:\s*\\?["']block\\?["']|\bexit\s*\(?\s*2\b""")
VAR = re.compile(r"\$[A-Za-z_0-9@*{]")
REDIRECT = re.compile(r"\d*>>?")
LOOPS = {"while", "until", "for", "select"}
HINTS = {
    "block-on-nonblocking": "registered only on events that cannot block, so the block is ignored",
    "unquoted-rm": 'quote the variable: rm -rf "$DIR"/cache',
    "eval-input": "eval in a script that reads its hook input from stdin; parse the input, never run it",
}


def tokens(code: str) -> list[str]:
    """Split code into words and the operator characters ;|&(), keeping each word's quotes."""
    toks, cur, quote, i = [], "", "", 0
    while i < len(code):
        c = code[i]
        if quote:
            cur += c
            if c == "\\" and quote == '"':
                cur, i = cur + code[i + 1 : i + 2], i + 1
            elif c == quote:
                quote = ""
        elif c == "\\":
            cur, i = cur + code[i : i + 2], i + 1
        elif c in "'\"":
            cur, quote = cur + c, c
        elif c.isspace() or c in ";|&()":
            toks += [cur] if cur else []
            toks += [] if c.isspace() else [c]
            cur = ""
        else:
            cur += c
        i += 1
    return toks + ([cur] if cur else [])


def unquoted_var(word: str) -> bool:
    quote, i = "", 0
    while i < len(word):
        c = word[i]
        if c == "\\" and quote != "'":
            i += 1
        elif quote and c == quote:
            quote = ""
        elif not quote and c in "'\"":
            quote = c
        elif not quote and VAR.match(word, i):
            return True
        i += 1
    return False


def args(toks: list[str], i: int) -> list[str]:
    end = next((j for j in range(i, len(toks)) if toks[j] in ENDS), len(toks))
    return toks[i:end]


def reads_stdin(name: str, own: list[str], piped: bool) -> bool:
    """True when this command reads the script's own stdin: no pipe into it and no < redirect, and a `read`,
    a `cat` with no file operand, or a `jq` with no file operand after its filter and no -n."""
    if piped or any(a.startswith("<") for a in own):
        return False
    operands, skip = [], False
    for a in own:
        if skip or REDIRECT.match(a):  # an output redirect and its target are not file operands
            skip = not skip and REDIRECT.fullmatch(a) is not None
        elif a == "-" or not a.startswith("-"):
            operands.append(a)
    if name == "cat":
        return all(a == "-" for a in operands)
    if name == "jq":
        return len(operands) <= 1 and not {"-n", "--null-input"} & set(own)
    return name == "read"


def piped(toks: list[str], j: int) -> bool:
    """True when the command named at toks[j] is fed by a pipe: walking back past assignments and words such
    as `while` or `!`, the token before it is a lone `|` (tokens() splits `||` into two)."""
    while j > 0 and (ASSIGN.match(toks[j - 1]) or toks[j - 1] in RUNS):
        j -= 1
    return j > 0 and toks[j - 1] == "|" and (j < 2 or toks[j - 2] != "|")


def code_pieces(text: str) -> list[tuple[int, str]]:
    """Each (line, code) of a shell file: top-level code and substitution bodies, less comments, strings
    and heredoc bodies."""
    out, stack, heredocs = [], [], []
    for n, line in enumerate(text.splitlines(), 1):
        if heredocs:
            delim, tabs = heredocs[0]
            if (line.lstrip("\t") if tabs else line) == delim:
                heredocs.pop(0)
            continue
        in_code = not stack or stack[-1] not in ("'", '"')
        top, bodies, head, tail, stack = split(line.rstrip().removesuffix("\\"), stack)
        out += [(n, code) for code in (top, *bodies, head, tail) if code]
        heredocs += heredocs_in(words(top)) + (heredocs_in(words(tail)) if tail and in_code else [])
    return out


def lint(path: pathlib.Path, events: set[str]) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    found = []
    if events <= NONBLOCKING:
        found += [(n, "block-on-nonblocking") for n, line in enumerate(text.splitlines(), 1)
                  if not line.lstrip().startswith("#") and BLOCKS.search(line)][:1]
    # A `read` inside a loop reads the script's stdin only if the loop's `done` has no < redirect, so each
    # open loop holds its reads until its `done` is seen.
    evals, reads, loops = [], False, []
    for n, code in code_pieces(text):
        toks = tokens(code)
        reads = reads or any("/dev/stdin" in t for t in toks)
        names = {i - 1: name for name, i in commands(toks)}
        for j, tok in enumerate(toks):
            head = j == 0 or toks[j - 1] in ENDS or toks[j - 1] in RUNS
            if tok in LOOPS and head:
                loops.append(False)
            elif tok == "done" and (j == 0 or toks[j - 1] in ENDS) and loops:
                held = loops.pop() and not any(a.startswith("<") for a in args(toks, j + 1))
                if loops:
                    loops[-1] = loops[-1] or held
                else:
                    reads = reads or held
            name = names.get(j)
            if name is None:
                continue
            own = args(toks, j + 1)
            if name == "rm" and any(unquoted_var(a) for a in own):
                found.append((n, "unquoted-rm"))
            elif name == "eval":
                evals.append(n)
            elif reads_stdin(name, own, piped(toks, j)):
                if loops:
                    loops[-1] = True
                else:
                    reads = True
    found += [(n, "eval-input") for n in evals if reads]
    return sorted(set(found))


def registered(settings: dict, hooks_dir: pathlib.Path) -> dict[str, set[str]]:
    """Each hook script in hooks_dir that a command hook runs, with the events it is registered on."""
    events: dict[str, set[str]] = {}
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                if hook.get("type") != "command":
                    continue
                try:
                    cmd = shlex.split(hook.get("command", ""))
                except ValueError:
                    cmd = hook.get("command", "").split()
                for word in cmd:
                    name = pathlib.PurePath(word).name
                    if name and (hooks_dir / name).is_file():
                        events.setdefault(name, set()).add(event)
    return events


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    settings, hooks_dir = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")), pathlib.Path(sys.argv[2])
    bad = 0
    for name, events in sorted(registered(settings, hooks_dir).items()):
        for n, rule in lint(hooks_dir / name, events):
            print(f"HOOKLINT {hooks_dir / name}:{n} {rule} - {HINTS[rule]}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
