#!/usr/bin/env python3
"""Mutation sweep of a graded round's committed tests (#618; docs/factory/LOOP.md, Mutation sweep).

Usage:
  mutation_sweep.py <worktree> <base sha> <out json> <first-run timeout>

<worktree> is a detached checkout of the graded sha. The tests are the files `git diff --name-only --diff-filter=AM
<base>...HEAD` names whose base name is test_*.py or *_test.py. The edits are on the lines that diff adds to every
other added or modified bash or Python file outside a tests or fixtures directory, on code only: never a comment, a
string or a here-document body. Operators, at most one edit each per line: flip swaps the first comparison, force-true
makes one condition always true, drop turns an assert, raise, return, exit, continue or break into a no-op; none where
the edit cannot change behavior (the main guard's force-true, a function's last bare, None or 0 return, a file's last
exit 0). An edit
after which its file no longer parses is discarded; the rest are ordered by the sha256 of path NUL operator NUL
stripped line, so an unchanged line gets the same edits every round, and the first 8 run.
The tests run unedited first, under <first-run timeout> s, then once per edit under twice that run plus 10 s; exit 0
is survived, any other exit or a timeout killed. Each run has a session of its own, whose whole process group gets
KILL when it ends, and on Linux, where the helper is the child subreaper, every child orphaned to it gets KILL too, so a
loop an edit made endless never outlives the sweep.
Writes {"tests", "baseline_sec", "timeout_sec", "mutants", "reason"} to <out json> and exits 0; reason names why no
edit ran, else null. A git failure exits 2 and writes nothing. python3 stdlib only.
"""
from __future__ import annotations

import ast
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
MAIN_GUARD = ('__name__ == "__main__"', "__name__ == '__main__'")  # its force-true cannot change a script run

SH_FLIP = {"-eq": "-ne", "-ne": "-eq", "-lt": "-ge", "-ge": "-lt", "-gt": "-le", "-le": "-gt",
           "=": "!=", "==": "!=", "!=": "="}
SH_COMPARE = re.compile(r"(?<=\s)(-eq|-ne|-lt|-ge|-gt|-le|==|=|!=)(?=\s)")
SH_HEADER = re.compile(r"\s*(if|elif|while)\s")
SH_HEADER_END = re.compile(r";\s*(then|do)(?=[\s;]|$)")
SH_TEST = re.compile(r"\s*(\[\[?)\s")
SH_DROP = re.compile(r"\s*(return|exit|continue|break)(?=[\s;&|]|$)")

CURRENT: subprocess.Popen | None = None  # the pytest run in progress, for the signal handler
SUBREAPER = False  # set at start on Linux: kill_orphans then reaches a run's children that left its group


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
    """The numbers, in the new file, of the lines `git diff -U0 <base>...HEAD` adds to path."""
    out: list[int] = []
    n = None
    for line in git(wt, "diff", "-U0", "--no-color", "--no-ext-diff", "--no-textconv", "--no-renames",
                    f"{base}...HEAD", "--", path).split("\n"):
        hunk = HUNK.match(line)
        if hunk:
            n = int(hunk.group(1))
        elif n is not None and line.startswith("+"):
            out.append(n)
            n += 1
    return out


# An edit is (line, operator, {line number: new text}); only a Python drop of a statement over several lines changes
# more than its own line, blanking the rest of the statement.

def py_edits(text: str, wanted: list[int]) -> list[tuple[int, str, dict[int, str]]]:
    """Python edits from tokenize's OP and NAME tokens, so a comment or a string's contents give none."""
    lines = text.split("\n")
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return []
    code = [t for t in toks if t.type in (tokenize.OP, tokenize.NAME, tokenize.NEWLINE)]
    # A function's last statement `return`, `return None` or `return 0`, whose drop cannot change behavior: the
    # function returns None anyway, and sys.exit(main()) exits 0 on None as on 0.
    last_returns = set()
    try:
        funcs = [f for f in ast.walk(ast.parse(text)) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
    except (SyntaxError, ValueError):
        funcs = []
    for f in funcs:
        last = f.body[-1]
        if isinstance(last, ast.Return) and (last.value is None or isinstance(last.value, ast.Constant)
                                             and type(last.value.value) in (type(None), int) and not last.value.value):
            last_returns.add(last.lineno)
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
                    if t.start[0] == n and cond not in ("True", *MAIN_GUARD):
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
            k = j
            while k < n and not text[k].isspace() and text[k] not in ";&|<>()":
                k += 1
            word = re.sub(r"[\"'\\]", "", text[j:k])
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
            stop = re.compile(r"[;&|]").search(m, drop.end())
            words = m[drop.start(1):stop.start() if stop else len(m)].rstrip()
            # The file's last statement `exit 0`: the script ends with status 0 after `:` too.
            if words.split() == ["exit", "0"] and not (m[drop.start(1) + len(words):] + "".join(masked[n:])).strip():
                continue
            out.append((n, "drop", {n: line[:drop.start(1)] + ":" + line[drop.start(1) + len(words):]}))
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


def kill_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def subreaper() -> bool:
    """On Linux, make this process the child subreaper of its descendants (prctl PR_SET_CHILD_SUBREAPER), so a test's
    child that starts a session of its own, out of the run's process group, is orphaned to the sweep, not to init."""
    if not sys.platform.startswith("linux"):
        return False
    import ctypes
    return ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0


def kill_orphans() -> None:
    """KILL and reap every child of this process left after a run's group KILL, which as subreaper are the run's
    orphans; each one killed orphans its own children to this process, so repeat until none is left, for 5 s at most."""
    end = time.monotonic() + 5
    while time.monotonic() < end:
        kids = []
        for stat in Path("/proc").glob("[0-9]*/stat"):
            try:
                s = stat.read_text()
            except OSError:
                continue
            if int(s[s.rindex(")") + 2:].split()[1]) == os.getpid():
                kids.append(int(stat.parent.name))
        if not kids:
            return
        for pid in kids:
            try:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, os.WNOHANG)
            except (ProcessLookupError, ChildProcessError):
                pass
        time.sleep(0.05)


def run(cmd: list[str], wt: Path, env: dict[str, str], timeout: float) -> tuple[int | None, float, str]:
    """(exit code, or None on a timeout; seconds; the output's last lines) of one pytest run.

    In a session of its own, whose group gets KILL however the run ends: subprocess.run's timeout kills pytest
    alone, and a child stuck in a loop an edit made endless would keep spinning after the sweep.
    """
    global CURRENT
    start = time.monotonic()
    with open(os.devnull, "rb") as stdin, tempfile.TemporaryFile() as log:
        p = subprocess.Popen(cmd, cwd=wt, env=env, stdin=stdin, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
        CURRENT = p
        try:
            rc: int | None = p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            rc = None
        finally:
            kill_group(p.pid)
            p.wait()
            if SUBREAPER:
                kill_orphans()
            CURRENT = None
        secs = time.monotonic() - start
        log.seek(0)
        tail = "\n".join(log.read().decode("utf-8", "replace").splitlines()[-20:])
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
    cmd = ["python3", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *tests]
    # No bytecode: an edit of the same size written in the same second as its source would import the source's
    # cached bytecode, and the edit would survive untested.
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if not tests:
        result["reason"] = "no committed test in the diff"
    elif not chosen:
        result["reason"] = "no added bash or Python code line outside tests and fixtures gives an edit"
    else:
        rc, secs, tail = run(cmd, wt, env, first)
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
                    rc, secs, _ = run(cmd, wt, env, limit)
                finally:
                    write(wt / p, text)
                result["mutants"].append({
                    "path": p, "line": n, "operator": op, "before": text.split("\n")[n - 1].strip(),
                    "after": new.split("\n")[n - 1].strip(), "result": "survived" if rc == 0 else "killed",
                    "timed_out": rc is None, "seconds": round(secs, 2)})
    out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


def stop(signum: int, _frame: object) -> None:
    """A TERM, INT or HUP kills the pytest run in progress; the edited file is restored on the way out."""
    if CURRENT is not None:
        kill_group(CURRENT.pid)
    raise SystemExit(128 + signum)


if __name__ == "__main__":
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, stop)
    SUBREAPER = subreaper()
    sys.exit(main(sys.argv[1:]))
