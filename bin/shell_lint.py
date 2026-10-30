#!/usr/bin/env python3
"""Fail on a pipe into `grep -q` in a tracked shell file that sets pipefail (#279).

`grep -q` exits at its first match. A writer still printing then dies of SIGPIPE, and
under `set -o pipefail` that failure is the pipeline's status, so a match reads as a miss.
The fix is to capture the output first, then grep it: out=$(cmd); grep -q pat <<<"$out".

Shell files are the ones `scripts()` in bin/check picks: tracked `.sh` files and tracked
files with a bash or sh shebang, less templates, cultivation/parked/ and docs/archive/.
A quote-aware scan of each line finds its comment, carries open quotes across lines and
pulls out each "$(...)" or `...` inside double quotes, over all its lines, as code of its own
scanned the same way; the enclosing code holds one word in its place. Each piece of code
is then split into words and operators with shlex, so a `| grep -q` inside a quoted string is
one word and is not a pipe. Heredoc bodies are skipped.

Exit status: 0 when no file has a hit, 1 otherwise.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shlex
import subprocess
import sys

SHEBANG = re.compile(r"^#!.*[/ ](bash|sh)(\s|$)")
EXCLUDE = ("cultivation/parked/", "docs/archive/")
PIPES = {"|", "|&"}
SUBS = ("$(", "`")
CASE = re.compile(r"case\s+\S+\s+in(?=[\s;]|$)")
ESAC = re.compile(r"esac(?=[\s;&|)]|$)")
# Tokens that end grep's argument list: the next pipeline stage, list operator or group end.
ENDS = {"|", "|&", "||", "&&", ";", ";;", "&", ")", "(", "{", "}"}
GREPS = {"grep", "egrep", "fgrep"}
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
FIX = "capture the output first, then grep it: out=$(cmd); grep -q pat <<<\"$out\""


def split(line: str, stack: list[str]) -> tuple[str, list[str], str | None, str | None, list[str]]:
    """Walk one line's quotes; return its top-level code, the bodies of each outermost "$(...)" or
    `...` inside double quotes that opens and closes on it, the rest of one open from the line
    before up to its close (head), the start of one still open at its end (tail), and the quotes and
    substitutions still open at its end. A line wholly inside a substitution is its tail.

    `stack` holds those left open by the lines before: text still inside a quote is skipped, so
    a multi-line string is not read as code, and each substitution is one word in the top-level code.
    A $'...' string becomes '' (shlex has no backslash escapes inside it), an unquoted # at a word
    start ends the code, so '# x' is not a comment, and a case inside a substitution is on the stack,
    so a pattern's ) does not close it.
    """
    stack = list(stack)
    outer = next((d for d, k in enumerate(stack) if k in SUBS), None)  # outermost substitution
    begin, head, bodies = 0 if outer is not None else None, None, []
    carried, top, reopen = bool(stack), [], outer is not None  # reopen: a substitution from before
    i = 0
    while i < len(line):
        c, kind, n = line[i], stack[-1] if stack else "", 1
        text, was_carried, inside = None, carried, begin is not None
        start = i == 0 or line[i - 1] in " \t;|&("  # a word start
        if kind == "'":
            if c == "'":
                stack.pop()
        elif c == "\\":
            n = 2
        elif kind == '"':
            if c == '"':
                stack.pop()
            elif line.startswith("$(", i) or c == "`":
                n = 2 if c == "$" else 1
                stack.append(line[i : i + n])
                if begin is None:
                    outer, begin, text = len(stack) - 1, i + n, "_"
        elif kind == "`" and c == "`" or kind in ("$(", "(") and c == ")":
            stack.pop()
        elif c == "#" and start:
            break  # a comment: the rest of the line is not code
        elif kind == "case" and start and ESAC.match(line, i):
            stack.pop()
            n = 4
        elif kind in ("$(", "(", "case") and start and CASE.match(line, i):
            stack.append("case")
            n = 4
        elif kind and c == "(":
            stack.append("(")
        elif line.startswith("$'", i):
            j = i + 2
            while j < len(line) and line[j] != "'":
                j += 2 if line[j] == "\\" else 1
            n, text = j + 1 - i, "''" if not stack else None
        elif c in "'\"":
            stack.append(c)
        if outer is not None and len(stack) <= outer:  # the outermost substitution closed
            if reopen:
                head, reopen = line[begin:i], False
            else:
                bodies.append(line[begin:i])
            begin = outer = None
        if was_carried and not stack:
            carried = False
            top.append("''")  # the end of a string begun on a line before
        elif not was_carried and not inside:
            top.append(line[i : i + n] if text is None else text)
        i += n
    tail = line[begin:i] if begin is not None else None
    return "".join(top), bodies, head, tail, stack


def words(src: str) -> list[str]:
    """Split code into shell words and operators."""
    lex = shlex.shlex(src, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""  # split already cut the comment; shlex would end a word at `${#x}`
    toks: list[str] = []
    try:
        for tok in lex:
            toks.append(tok)
    except ValueError:  # a quote left open to the next line; keep the words before it
        pass
    return toks


def quiet_grep(args: list[str]) -> bool:
    """True when this grep's own arguments include -q, --quiet or --silent."""
    skip = False
    for arg in args:
        if arg in ENDS or arg == "--":
            break
        if skip:
            skip = False
        elif arg in ("--quiet", "--silent"):
            return True
        elif arg in ("--regexp", "--file"):
            skip = True  # the next word is a pattern or a file, not a flag
        elif arg.startswith("-") and not arg.startswith("--"):
            for k, c in enumerate(arg[1:], 2):  # a short-option cluster, in order
                if c == "q":
                    return True
                if c in "ef":  # -e and -f take the rest of the word, or else the next word
                    skip = k == len(arg)
                    break
    return False


def hits(toks: list[str]) -> bool:
    for i, tok in enumerate(toks):
        if tok not in PIPES:
            continue
        j = i + 1
        while j < len(toks) and (ASSIGN.match(toks[j]) or toks[j] in ("command", "!")):
            j += 1
        if j < len(toks) and toks[j].rsplit("/", 1)[-1] in GREPS and quiet_grep(toks[j + 1 :]):
            return True
    return False


def sets_pipefail(toks: list[str]) -> bool:
    for i, tok in enumerate(toks[1:], 1):
        if tok == "pipefail" and re.fullmatch(r"-[A-Za-z]*o", toks[i - 1]) and "set" in toks[:i]:
            return True
    return False


def scan(text: str) -> tuple[bool, list[int]]:
    """Return whether the file sets pipefail, and the lines that pipe into grep -q."""
    pipefail, found = False, set()
    heredocs: list[tuple[str, bool]] = []  # pending (delimiter, strip leading tabs)
    carry: tuple[str, int] | None = None  # a pipe that ended the line before, and its line
    stack: list[str] = []  # quotes and substitutions left open by the line before
    pending: list[str] = []  # the lines so far of a substitution left open, from line opened
    opened = 0
    for n, line in enumerate(text.splitlines(), 1):
        if heredocs:
            delim, tabs = heredocs[0]
            if (line.lstrip("\t") if tabs else line) == delim:
                heredocs.pop(0)
            continue
        top, bodies, head, tail, stack = split(line.rstrip().removesuffix("\\"), stack)
        subs = [(n, body) for body in bodies]
        if head is not None:
            subs.insert(0, (opened, "\n".join([*pending, head])))
            pending = []
        if tail is not None:
            opened = opened if pending else n
            pending.append(tail)
        for first, body in subs:  # a substitution's body is code of its own, carry and all
            found.update(first + k - 1 for k in scan(body)[1])
        toks = words(top)
        pipefail = pipefail or sets_pipefail(toks)
        if hits(toks):
            found.add(n)
        elif carry and toks and hits([carry[0], *toks]):
            found.add(carry[1])
        if toks:
            carry = (toks[-1], n) if toks[-1] in PIPES else None
        for i, tok in enumerate(toks[:-1]):
            before = "".join(toks[:i])
            if tok == "<<" and before.count("((") <= before.count("))"):  # not a shift in $(( ))
                delim = toks[i + 1]
                if delim == "-" and i + 2 < len(toks):
                    delim = "-" + toks[i + 2]
                heredocs.append((delim.lstrip("-"), delim.startswith("-")))
    return pipefail, sorted(found)


def shell_files(root: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                         capture_output=True, text=True, check=True).stdout
    files = []
    for rel in sorted(filter(None, out.split("\0"))):
        path = root / rel
        if rel.endswith(".jinja") or rel.startswith(EXCLUDE) or path.is_symlink() or not path.is_file():
            continue
        if rel.endswith(".sh"):
            files.append(rel)
            continue
        with path.open(encoding="utf-8", errors="replace") as f:
            if SHEBANG.match(f.readline()):
                files.append(rel)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="a git checkout (default: .)")
    root = pathlib.Path(ap.parse_args().root)
    bad = 0
    for rel in shell_files(root):
        pipefail, found = scan((root / rel).read_text(encoding="utf-8", errors="replace"))
        if not pipefail:
            continue
        for n in found:
            print(f"FAIL: {rel}:{n}: pipe into grep -q under pipefail; a writer killed by SIGPIPE "
                  f"fails the pipeline, so {FIX}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
