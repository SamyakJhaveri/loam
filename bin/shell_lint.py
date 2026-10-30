#!/usr/bin/env python3
"""Fail on a pipe into `grep -q` in a tracked shell file that sets pipefail (#279).

`grep -q` exits at its first match. A writer still printing then dies of SIGPIPE, and
under `set -o pipefail` that failure is the pipeline's status, so a match reads as a miss.
The fix is to capture the output first, then grep it: out=$(cmd); grep -q pat <<<"$out".

Shell files are the ones `scripts()` in bin/check picks: tracked `.sh` files and tracked
files with a bash or sh shebang, less templates, cultivation/parked/ and docs/archive/.
Each line is split into words and operators with shlex, so a `| grep -q` inside a quoted
string is one word and is not a pipe. Heredoc bodies are skipped.

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
# Tokens that end grep's argument list: the next pipeline stage, list operator or group end.
ENDS = {"|", "|&", "||", "&&", ";", ";;", "&", ")", "(", "{", "}"}
GREPS = {"grep", "egrep", "fgrep"}
QUIET = re.compile(r"-[A-Za-z0-9]*q")
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
FIX = "capture the output first, then grep it: out=$(cmd); grep -q pat <<<\"$out\""


def blank_ansi_c(line: str) -> str:
    """Replace each $'...' string with '' : shlex has no backslash escapes inside it."""
    out, i, quote = [], 0, ""
    while i < len(line):
        c = line[i]
        if quote == "'":
            quote = "" if c == "'" else quote
        elif c == "\\":
            out.append(line[i : i + 2])
            i += 2
            continue
        elif quote == '"':
            quote = "" if c == '"' else quote
        elif line.startswith("$'", i):
            j = i + 2
            while j < len(line) and line[j] != "'":
                j += 2 if line[j] == "\\" else 1
            out.append("''")
            i = j + 1
            continue
        elif c in "'\"":
            quote = c
        out.append(c)
        i += 1
    return "".join(out)


def words(line: str) -> list[str]:
    """Split one line into shell words and operators; drop a trailing comment."""
    lex = shlex.shlex(blank_ansi_c(line), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""  # shlex would end a word at `${#x}`; cut comments by word below
    toks: list[str] = []
    try:
        for tok in lex:
            toks.append(tok)
    except ValueError:  # an open quote: a multi-line string or `$'...'`; keep the words before it
        pass
    for i, tok in enumerate(toks):
        if tok.startswith("#"):
            return toks[:i]
    return toks


def quiet_grep(args: list[str]) -> bool:
    """True when this grep's own arguments include -q, --quiet or --silent."""
    skip = False
    for arg in args:
        if arg in ENDS or arg == "--":
            break
        if skip:
            skip = False
        elif arg in ("--quiet", "--silent") or QUIET.match(arg) and not arg.startswith("--"):
            return True
        elif arg in ("-e", "-f", "--regexp", "--file"):
            skip = True  # the next word is a pattern or a file, not a flag
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
    pipefail, found = False, []
    heredocs: list[tuple[str, bool]] = []  # pending (delimiter, strip leading tabs)
    carry: tuple[str, int] | None = None  # a pipe that ended the line before, and its line
    for n, line in enumerate(text.splitlines(), 1):
        if heredocs:
            delim, tabs = heredocs[0]
            if (line.lstrip("\t") if tabs else line) == delim:
                heredocs.pop(0)
            continue
        toks = words(line.rstrip().removesuffix("\\"))
        pipefail = pipefail or sets_pipefail(toks)
        if hits(toks):
            found.append(n)
        elif carry and toks and hits([carry[0], *toks]):
            found.append(carry[1])
        if toks:
            carry = (toks[-1], n) if toks[-1] in PIPES else None
        for i, tok in enumerate(toks[:-1]):
            if tok == "<<" and toks[:i].count("((") <= toks[:i].count("))"):  # not a shift in $(( ))
                delim = toks[i + 1]
                if delim == "-" and i + 2 < len(toks):
                    delim = "-" + toks[i + 2]
                heredocs.append((delim.lstrip("-"), delim.startswith("-")))
    return pipefail, found


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
