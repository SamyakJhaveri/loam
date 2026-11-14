#!/usr/bin/env python3
"""Mutation sweep of a graded round's committed tests (#618; docs/factory/LOOP.md, Mutation sweep).

Usage:
  mutation_sweep.py <worktree> <base sha> <out json> <first-run timeout>

<worktree> is a detached checkout of the graded sha. The tests are the files `git diff --name-only --diff-filter=AM
<base>...HEAD` names whose base name is test_*.py or *_test.py. The edits are on the lines that diff adds to every
other added or modified bash or Python file outside a tests or fixtures directory, on code only: never a comment, a
string or a here-document body. Operators, at most one edit each per line: flip swaps the first comparison, force-true
makes one condition always true, drop turns an assert, raise, return, exit, continue or break into a no-op; none where
the edit cannot change behavior (the main guard's force-true, a function's last bare or None return, or 0 return when
its every call is the argument of sys.exit or SystemExit, a file's last exit 0). An edit
after which its file no longer parses is discarded; the rest are ordered by the sha256 of path NUL operator NUL
stripped line, so an unchanged line gets the same edits every round, and the first 8 run.
The tests run unedited first, under <first-run timeout> s, then once per edit under twice that run plus 10 s; exit 0
is survived, any other exit or a timeout killed. Each run is a fresh container of the image FACTORY_SWEEP_IMAGE names,
with a PID namespace, filesystem, /tmp and HOME of its own and no network, into which docker cp copies <worktree>; no
host path is mounted, so a test signals or deletes only what is in its container, and removing the container ends every
process the run started. With FACTORY_SWEEP_IMAGE unset or empty no test runs (#768: a mutant run on the host
SIGKILLed every process of its user on 13 Nov 2026); set, a docker create or cp that fails, or no docker, exits 1 and
writes nothing, so the tests never run on the host.
Writes {"tests", "baseline_sec", "timeout_sec", "mutants", "reason"} to <out json> and exits 0; reason names why no
edit ran, else null. A git failure exits 2 and writes nothing. python3 stdlib only.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import tokenize
import warnings
from pathlib import Path

MAX_EDITS = 8
TEST_NAME = re.compile(r"test_.*\.py|.*_test\.py")
SHEBANG_PY = re.compile(r"#!.*[/ ]python[0-9.]*(\s|$)")
SHEBANG_SH = re.compile(r"#!.*[/ ](bash|sh)(\s|$)")
HUNK = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

PY_FLIP = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
PY_HEADER = ("if", "elif", "while")
PY_DROP = ("assert", "raise", "return", "continue", "break")

SH_FLIP = {"-eq": "-ne", "-ne": "-eq", "-lt": "-ge", "-ge": "-lt", "-gt": "-le", "-le": "-gt",
           "=": "!=", "==": "!=", "!=": "="}
SH_COMPARE = re.compile(r"(?<=\s)(-eq|-ne|-lt|-ge|-gt|-le|==|=|!=)(?=\s)")
SH_HEADER = re.compile(r"\s*(if|elif|while)\s")
SH_HEADER_END = re.compile(r";\s*(then|do)(?=[\s;]|$)")
SH_TEST = re.compile(r"\s*(\[\[?)\s")
SH_DROP = re.compile(r"\s*(return|exit|continue|break)(?=[\s;&|]|$)")
SH_DROP_END = re.compile(r";|(?<![<>])&(?!>)|(?<!>)\|")  # not the & or | of >&, <&, &> or >|
SH_REDIR = re.compile(r"(?<=\s)(\d*[<>]|&>)")  # a redirection's start: [n]< [n]> &>


def git(wt: Path, *args: str) -> str:
    return subprocess.run(["git", "--literal-pathspecs", "-C", str(wt), *args],
                          capture_output=True, text=True, check=True).stdout


def language(path: Path) -> str | None:
    if path.suffix == ".py":
        return "py"
    if path.suffix == ".sh":
        return "sh"
    with path.open("rb") as f:
        first = f.readline().decode("utf-8", "replace")
    return "py" if SHEBANG_PY.match(first) else "sh" if SHEBANG_SH.match(first) else None


def added_lines(wt: Path, base: str, path: str) -> list[int]:
    """The numbers, in the new file, of the lines `git diff -U0 <base>...HEAD` adds to path.

    --inter-hunk-context=0 overrides a diff.interHunkContext, whose merged hunks hold context lines this count skips.
    """
    out: list[int] = []
    n = None
    for line in git(wt, "diff", "-U0", "--inter-hunk-context=0", "--no-color", "--no-ext-diff", "--no-textconv",
                    "--no-renames", f"{base}...HEAD", "--", path).split("\n"):
        hunk = HUNK.match(line)
        if hunk:
            n = int(hunk.group(1))
        elif n is not None and line.startswith("+"):
            out.append(n)
            n += 1
    return out


# An edit is (line, operator, {line number: new text}); only a Python drop of a statement over several lines changes
# more than its own line, blanking the rest of the statement.

def main_side(x: ast.expr) -> str | None:
    """Which side of `__name__ == "__main__"` x is, if either."""
    if isinstance(x, ast.Name) and x.id == "__name__":
        return "name"
    return "main" if isinstance(x, ast.Constant) and x.value == "__main__" else None


def py_edits(text: str, wanted: list[int]) -> list[tuple[int, str, dict[int, str]]]:
    """Python edits from tokenize's OP and NAME tokens, so a comment or a string's contents give none."""
    lines = text.split("\n")
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return []
    code = [t for t in toks if t.type in (tokenize.OP, tokenize.NAME, tokenize.NEWLINE)]
    # A function's last statement whose drop cannot change behavior: `return` or `return None`, since the function
    # returns None anyway, and `return 0` when every call of it in the file is the argument of sys.exit(...) or a
    # raised SystemExit(...), which exit 0 on None as on 0.
    try:
        body = ast.parse(text).body
    except (SyntaxError, ValueError):
        body = []
    nodes = [n for b in body for n in ast.walk(b)]
    # A module-level `if __name__ == "__main__":`, in either order: its force-true cannot change a script run.
    main_guards = {b.lineno for b in body if isinstance(b, ast.If) and isinstance(b.test, ast.Compare)
                   and [type(o) for o in b.test.ops] == [ast.Eq]
                   and {main_side(x) for x in (b.test.left, *b.test.comparators)} == {"name", "main"}}
    calls = [c for c in nodes if isinstance(c, ast.Call)]
    raised = {id(r.exc) for r in nodes if isinstance(r, ast.Raise)}  # SystemExit(...) exits only when raised
    exits = {id(a) for c in calls for a in c.args if isinstance(c.func, ast.Name) and c.func.id == "SystemExit"
             and id(c) in raised
             or isinstance(c.func, ast.Attribute) and c.func.attr == "exit"
             and isinstance(c.func.value, ast.Name) and c.func.value.id == "sys"}
    last_returns = set()
    for f in nodes:
        if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) or not isinstance(f.body[-1], ast.Return):
            continue
        value = f.body[-1].value
        if isinstance(value, ast.Constant) and type(value.value) is int and value.value == 0:
            mine = [c for c in calls if isinstance(c.func, ast.Name) and c.func.id == f.name]
            if not mine or any(id(c) not in exits for c in mine):
                continue
        elif not (value is None or isinstance(value, ast.Constant) and value.value is None):
            continue
        last_returns.add(f.body[-1].lineno)
    flips: dict[int, tuple[int, int, str]] = {}  # line -> its first comparison: start col, end col, swap
    starts: dict[int, int] = {}  # line -> index in code of the first token of a statement that starts it
    depth, fors, new_stmt = 0, set(), True
    for i, t in enumerate(code):
        row = t.start[0]
        if t.type == tokenize.NEWLINE:
            depth, fors, new_stmt = 0, set(), True
            continue
        if new_stmt:
            starts[row], new_stmt = i, False
        nxt = code[i + 1] if i + 1 < len(code) else None
        swap = None
        if t.type == tokenize.OP:
            if t.string in "([{":
                depth += 1
            elif t.string in ")]}":
                depth -= 1
                fors = {d for d in fors if d <= depth}
            elif t.string in PY_FLIP:
                swap = (t.end[1], PY_FLIP[t.string])
        elif t.string == "for":
            fors.add(depth)
        elif t.string == "in":
            if depth in fors:  # the `in` of a for clause, not a comparison
                fors.discard(depth)
            elif not (i and code[i - 1].string == "not" and code[i - 1].start[0] == row):
                swap = (t.end[1], "not in")
        elif t.string == "not" and nxt is not None and nxt.string == "in" and nxt.start[0] == row:
            swap = (nxt.end[1], "in")
        elif t.string == "is":
            two = nxt is not None and nxt.string == "not" and nxt.start[0] == row
            swap = (nxt.end[1], "is") if two else (t.end[1], "is not")
        if swap and row not in flips:
            flips[row] = (t.start[1], *swap)
    out = []
    for n in wanted:
        line = lines[n - 1]
        if n in flips:
            s, e, rep = flips[n]
            out.append((n, "flip", {n: line[:s] + rep + line[e:]}))
        if n not in starts:
            continue
        i = starts[n]
        first = code[i]
        if first.type == tokenize.NAME and first.string in PY_HEADER:
            d = 0
            for t in code[i + 1:]:
                if t.type == tokenize.NEWLINE:
                    break
                if t.type == tokenize.OP and t.string in "([{":
                    d += 1
                elif t.type == tokenize.OP and t.string in ")]}":
                    d -= 1
                elif t.type == tokenize.OP and t.string == ":" and d == 0:
                    cond = line[first.end[1]:t.start[1]].strip()
                    if t.start[0] == n and cond != "True" and n not in main_guards:
                        new = f"{line[:first.end[1]]} ({cond}) or True{line[t.start[1]:]}"
                        out.append((n, "force-true", {n: new}))
                    break
        if first.type == tokenize.NAME and first.string in PY_DROP and n not in last_returns:
            end = next((t.start[0] for t in code[i:] if t.type == tokenize.NEWLINE), n)
            change = {n: line[:first.start[1]] + "pass"}
            change.update({k: "" for k in range(n + 1, end + 1)})
            out.append((n, "drop", change))
    return out


def sh_scan(text: str) -> tuple[list[str], set[int]]:
    """The lines with quoted text and comments blanked at the same columns, and the here-document lines.

    A context stack tracks double quotes and the code inside $( ), $(( )), (( )) and backquotes, which can nest in
    double quotes; single-quoted and $'...' text is skipped whole. A here-document body, from the line after a
    <<WORD outside quotes and arithmetic to the line WORD, is blanked and its lines (the WORD line too) returned.
    """
    out = list(text)
    stack: list[list] = [["code"]]  # ["code"], ["dq"], ["tick"], or ["paren", open parens, arithmetic]
    pending: list[tuple[str, bool]] = []  # here-documents whose bodies start after this line: word, strip tabs
    body: set[int] = set()
    i, n = 0, len(text)

    def blank(a: int, b: int) -> None:
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c, top = text[i], stack[-1]
        two = text[i:i + 2]
        if c == "\n":
            i += 1
            if top[0] == "dq" or not pending:
                continue
            row = text.count("\n", 0, i) + 1
            for word, tabs in pending:
                while i < n:
                    j = text.find("\n", i)
                    j = n if j < 0 else j
                    line = text[i:j]
                    blank(i, j)
                    body.add(row)
                    i, row = j + 1, row + 1
                    if (line.lstrip("\t") if tabs else line) == word:
                        break
            pending = []
            continue
        if top[0] == "dq":
            if c == "\\":
                blank(i, i + 2)
                i += 2
            elif c == '"':
                stack.pop()
                i += 1
            elif text.startswith("$((", i):
                stack.append(["paren", 2, True])
                i += 3
            elif two == "$(":
                stack.append(["paren", 1, False])
                i += 2
            elif c == "`":
                stack.append(["tick"])
                i += 1
            else:
                blank(i, i + 1)
                i += 1
            continue
        if c == "\\":
            blank(i + 1, i + 2)
            i += 2
        elif c == "'" or two == "$'":
            j = i + (2 if c == "$" else 1)
            while j < n and text[j] != "'":
                j += 2 if c == "$" and text[j] == "\\" else 1
            blank(i + (2 if c == "$" else 1), min(j, n))
            i = j + 1
        elif c == '"':
            stack.append(["dq"])
            i += 1
        elif c == "#" and (i == 0 or text[i - 1] in " \t\n;&|()"):
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif c == "`":
            if top[0] == "tick":
                stack.pop()
            else:
                stack.append(["tick"])
            i += 1
        elif text.startswith("$((", i) or (two == "((" and (i == 0 or text[i - 1] != "$")):
            stack.append(["paren", 2, True])
            i += 3 if c == "$" else 2
        elif two == "$(":
            stack.append(["paren", 1, False])
            i += 2
        elif c in "()" and top[0] == "paren":
            top[1] += 1 if c == "(" else -1
            if top[1] == 0:
                stack.pop()
            i += 1
        elif text.startswith("<<<", i):
            i += 3
        elif two == "<<" and not (top[0] == "paren" and top[2]):
            j = i + 2
            tabs = text[j:j + 1] == "-"
            j += tabs
            while j < n and text[j] in " \t":
                j += 1
            k, word = j, ""  # the word as the shell reads it: quotes removed, escapes applied
            while k < n and not text[k].isspace() and text[k] not in ";&|<>()":
                if text[k] == "'":  # all literal to the next '
                    e = text.find("'", k + 1)
                    e = n if e < 0 else e
                    word, k = word + text[k + 1:e], e + 1
                elif text[k] == '"':  # a backslash escapes only $ ` " \ and a newline
                    k += 1
                    while k < n and text[k] != '"':
                        if text[k] == "\\" and text[k + 1:k + 2] in ("$", "`", '"', "\\", "\n"):
                            k += 1
                        word, k = word + text[k:k + 1].replace("\n", ""), k + 1
                    k += 1
                else:  # unquoted, a backslash escapes the next character
                    k += text[k] == "\\"
                    word, k = word + text[k:k + 1].replace("\n", ""), k + 1
            if word:
                pending.append((word, tabs))
            i = k
        else:
            i += 1
    return "".join(out).split("\n"), body


def sh_edits(text: str, wanted: list[int]) -> list[tuple[int, str, dict[int, str]]]:
    lines = text.split("\n")
    masked, body = sh_scan(text)
    out = []
    for n in wanted:
        line, m = lines[n - 1], masked[n - 1]
        if n in body or not m.strip():
            continue
        flip = SH_COMPARE.search(m) if "[" in m else None
        if flip:
            out.append((n, "flip", {n: line[:flip.start()] + SH_FLIP[flip.group()] + line[flip.end():]}))
        at = None
        head = SH_HEADER.match(m)
        if head:
            end = SH_HEADER_END.search(m, head.end())
            if end and m[head.end():end.start()].strip() not in ("true", ":"):
                at = len(line[:end.start()].rstrip())
        else:
            test = SH_TEST.match(m)
            close = re.compile(r"\s\]\]" if test and test.group(1) == "[[" else r"\s\]")
            shut = close.search(m, test.end() - 1) if test else None
            if shut and re.match(r"\s*(&&|\|\|)", m[shut.end():]):
                at = shut.end()
        if at is not None:
            out.append((n, "force-true", {n: line[:at] + " || true" + line[at:]}))
        drop = SH_DROP.match(m)
        if drop:
            # The words up to the statement's end, of which the redirections stay, so only the exit or jump changes.
            stop = SH_DROP_END.search(m, drop.end())
            end = len(m[:stop.start() if stop else len(m)].rstrip())
            # A < or > inside a substitution is no redirection: such a statement drops whole, as before.
            redir = None if re.search(r"\$\(|`", m[drop.end():end]) else SH_REDIR.search(m, drop.end(), end)
            cut = len(m[:redir.start() if redir else end].rstrip())
            # The file's last statement `exit 0`, with only `;` after it: the script ends with status 0 after `:` too.
            if m[drop.start(1):cut].split() == ["exit", "0"] and not re.sub(r"[;\s]", "", m[end:]
                                                                            + "".join(masked[n:])):
                continue
            out.append((n, "drop", {n: line[:drop.start(1)] + ":" + line[cut:]}))
    return out


def edited(text: str, change: dict[int, str]) -> str:
    lines = text.split("\n")
    for k, v in change.items():
        lines[k - 1] = v
    return "\n".join(lines)


def parses(lang: str, path: str, text: str) -> bool:
    if lang == "sh":
        return subprocess.run(["bash", "-n"], input=text.encode(), capture_output=True).returncode == 0
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            compile(text, path, "exec", dont_inherit=True)
    except (SyntaxError, ValueError):
        return False
    return True


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def remove(name: str) -> None:
    """Remove the container, killing every process in it; its exit is ignored, as for no such container, and no docker
    is left for the docker create after it to report."""
    with contextlib.suppress(OSError):
        subprocess.run(["docker", "rm", "-f", name], stdin=subprocess.DEVNULL, capture_output=True, check=False)


def docker(*args: str, timeout: float) -> None:
    try:
        r = subprocess.run(["docker", *args], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise SystemExit(f"mutation_sweep: docker {args[0]} failed: {e}") from None
    if r.returncode:
        raise SystemExit(f"mutation_sweep: docker {args[0]} exited {r.returncode}: {r.stderr.strip()}")


def run(image: str, tests: list[str], wt: Path, timeout: float) -> tuple[int | None, float, str]:
    """(exit code, or None on a timeout; seconds; the output's last lines) of one pytest run in a fresh container.

    The tree is copied to /sweep, absent until then, with -a, so the directory and its files keep the uid that --user
    runs as and a test can write them. --init reaps the orphans a test leaves, as init does on the host. The name is fixed
    per worktree, so a sweep killed mid-run leaves a container the next one removes, and only by that name, never by a
    filter an edit of this file could widen.
    """
    name = "loam-sweep-" + hashlib.sha256(str(wt.resolve()).encode()).hexdigest()[:12]
    start = time.monotonic()
    remove(name)
    try:
        docker("create", "--name", name, "--init", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
               "--pids-limit", "4096", "--memory", "8g", "--memory-swap", "8g",
               # No bytecode: an edit of the same size written in the same second as its source would import the
               # source's cached bytecode, and the edit would survive untested.
               "-e", "HOME=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1", image, "sh", "-c", 'cd /sweep && exec "$@"', "sh",
               "python3", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *tests, timeout=timeout)
        docker("cp", "-a", str(wt.resolve()), f"{name}:/sweep", timeout=timeout)
        with tempfile.TemporaryFile() as log:
            try:
                rc: int | None = subprocess.run(["docker", "start", "-a", name], stdin=subprocess.DEVNULL,
                                                stdout=log, stderr=subprocess.STDOUT, check=False,
                                                timeout=max(start + timeout - time.monotonic(), 0)).returncode
            except subprocess.TimeoutExpired:
                rc = None
            secs = time.monotonic() - start
            log.seek(0)
            tail = "\n".join(log.read().decode("utf-8", "replace").splitlines()[-20:])
    finally:
        remove(name)
    return rc, secs, tail


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    wt, base, out, first = Path(argv[0]), argv[1], Path(argv[2]), float(argv[3])
    result: dict = {"tests": [], "baseline_sec": None, "timeout_sec": None, "mutants": [], "reason": None}
    try:
        names = [p for p in git(wt, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=AM",
                                f"{base}...HEAD").split("\0") if p]
        tests = [p for p in names if TEST_NAME.fullmatch(Path(p).name)]
        result["tests"] = tests
        cands = []
        for p in names if tests else []:
            path = wt / p
            parts = Path(p).parts[:-1]
            if p in tests or "tests" in parts or "fixtures" in parts or path.is_symlink() or not path.is_file():
                continue
            lang = language(path)
            if lang is None:
                continue
            try:
                text = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
            lines = text.split("\n")
            for n, op, change in (py_edits if lang == "py" else sh_edits)(text, added_lines(wt, base, p)):
                key = hashlib.sha256(f"{p}\0{op}\0{lines[n - 1].strip()}".encode()).hexdigest()
                cands.append((key, p, n, op, change, lang, text))
    except subprocess.CalledProcessError as e:
        print(f"mutation_sweep: git {' '.join(e.cmd[4:])} failed: {e.stderr.strip()}", file=sys.stderr)
        return 2
    chosen = []
    for _key, p, n, op, change, lang, text in sorted(cands, key=lambda c: c[:3]):
        if len(chosen) == MAX_EDITS:
            break
        new = edited(text, change)
        if parses(lang, p, new):
            chosen.append((p, n, op, text, new))
    image = os.environ.get("FACTORY_SWEEP_IMAGE", "")
    if not image:
        result["reason"] = "FACTORY_SWEEP_IMAGE is unset; the sweep never runs tests on the host"
    elif not tests:
        result["reason"] = "no committed test in the diff"
    elif not chosen:
        result["reason"] = "no added bash or Python code line outside tests and fixtures gives an edit"
    else:
        rc, secs, tail = run(image, tests, wt, first)
        result["baseline_sec"] = round(secs, 2)
        if rc is None:
            result["reason"] = f"the committed tests did not finish unedited within {argv[3]} s"
        elif rc != 0:
            result["reason"] = f"the committed tests fail unedited (pytest exit {rc})"
        if rc != 0:
            print(f"mutation_sweep: {result['reason']}; the run's last lines:\n{tail}", file=sys.stderr)
        else:
            limit = result["timeout_sec"] = round(2 * result["baseline_sec"] + 10, 2)
            for p, n, op, text, new in chosen:
                write(wt / p, new)
                try:
                    rc, secs, _ = run(image, tests, wt, limit)
                finally:
                    write(wt / p, text)
                result["mutants"].append({
                    "path": p, "line": n, "operator": op, "before": text.split("\n")[n - 1].strip(),
                    "after": new.split("\n")[n - 1].strip(), "result": "survived" if rc == 0 else "killed",
                    "timed_out": rc is None, "seconds": round(secs, 2)})
    out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


def stop(signum: int, _frame: object) -> None:
    """A TERM, INT or HUP exits through run's finally, which removes the container, and main's, which restores the
    edited file."""
    raise SystemExit(128 + signum)


if __name__ == "__main__":
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, stop)
    sys.exit(main(sys.argv[1:]))
