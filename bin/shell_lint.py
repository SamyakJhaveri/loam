#!/usr/bin/env python3
"""Fail on a pipe into `grep -q` under pipefail (#279), or a bash 4 or GNU-only form (#280), in a tracked shell file.

`grep -q` exits at its first match. A writer still printing then dies of SIGPIPE, and
under `set -o pipefail` that failure is the pipeline's status, so a match reads as a miss.
The fix is to capture the output first, then grep it: out=$(cmd); grep -q pat <<<"$out".

Shell files are the ones `scripts()` in bin/check picks: tracked `.sh` files and tracked
files with a bash or sh shebang, less templates, cultivation/parked/ and docs/archive/.
A quote-aware scan of each line finds its comment, carries open quotes across lines and
pulls out each "$(...)" or `...` inside double quotes, over all its lines, as code of its own
scanned the same way; the enclosing code holds one word in its place. Each piece of code
is then split into words and operators with shlex, so a `| grep -q` inside a quoted string is
one word and is not a pipe. Heredoc bodies are skipped, also inside a substitution, so a quote
in one is text. A file that ends with a quote, substitution or heredoc still open fails, naming
the line that opened it, since the lint could not read past it.

macOS ships bash 3.2 and BSD tools, so the words of each command (top level and every substitution
body) must not run `mapfile` or `readarray`, `xargs -r`, `grep -P`, or `stat -c` without a
`stat -f` fallback in the same code, or compare file times with `-nt` or `-ot` as the operator of a `[`,
`[[` or `test` (bash 3.2 compares them in whole seconds), and a file that runs `timeout` must check
`command -v timeout`.

Exit status: 0 when no file has a hit or an open end, 1 otherwise.
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
CASE = re.compile(r"""case\s+(?:"[^"]*"|'[^']*'|\S+)\s+in(?=[\s;]|$)""")
ESAC = re.compile(r"esac(?=[\s;&|)]|$)")
# Tokens that end grep's argument list: the next pipeline stage, list operator or group end.
ENDS = {"|", "|&", "||", "&&", ";", ";;", "&", ")", "(", "{", "}"}
GREPS = {"grep", "egrep", "fgrep"}
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
FIX = "capture the output first, then grep it: out=$(cmd); grep -q pat <<<\"$out\""
# Words before a command name that leave the next word in command position.
RUNS = {"!", "command", "exec", "builtin", "env", "nohup", "time", "if", "then", "else", "elif", "while",
        "until", "do"}
GREP_VALUES = ("e", "f", "--regexp", "--file")  # options whose value is the next word, or the rest of the word
XARGS_VALUES = tuple("adEIJLnPRsS")
TESTS = {"[": "]", "[[": "]]", "test": None}  # test commands and the word that closes each
STRING_OPS = {"=", "==", "!=", "=~", "<", ">"}  # a word after one of these is a string operand
MTIME = ("macOS bash 3.2 compares -nt and -ot in whole seconds, so two files written in the same second "
         "compare equal; order events by a counter or a status line, not by file times")
LOOP = "read lines in a loop: while IFS= read -r x; do a+=(\"$x\"); done < file"
FORMS = {
    "mapfile": f"mapfile is bash 4 and macOS has bash 3.2; {LOOP}",
    "readarray": f"readarray is bash 4 and macOS has bash 3.2; {LOOP}",
    "xargs -r": "xargs -r (--no-run-if-empty) is GNU-only and macOS xargs rejects it; drop it and make an empty "
                "input harmless or test the input first (c29ef01)",
    "grep -P": "grep -P is GNU-only and BSD grep has no PCRE; use grep -E",
    "stat -c": "stat -c is GNU-only; carry the BSD form in the same code: stat -c %Y f 2>/dev/null || stat -f %m f",
    "timeout": "timeout is GNU coreutils and stock macOS lacks it, and no line of this file checks "
               "command -v timeout; guard it: command -v timeout >/dev/null && timeout ...",
    "-nt": MTIME,
    "-ot": MTIME,
}


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


def opt_set(args: list[str], short: str, longs: tuple[str, ...] = (), values: tuple[str, ...] = (),
            operands: bool = True) -> bool:
    """True when a command's own arguments set the option -<short> or a long name in longs.

    A short option in values takes the rest of its word, or else the next word, as its value; a long
    one takes the next word unless it has =. operands=False stops at the first word that is not an option.
    """
    skip, depth = False, 0
    for arg in args:
        if arg in ("<(", ">("):  # a process substitution is one argument (a value, if one is due); its words
            depth, skip = depth + 1, False  # are its own command's
        elif depth:
            depth += 1 if arg == "(" else -len(arg) if arg and not arg.strip(")") else 0  # `))` is one word
        elif arg in ENDS or arg == "--":
            break
        elif skip:
            skip = False
        elif arg.startswith("--"):
            name = arg.split("=", 1)[0]
            if name in longs:
                return True
            skip = name in values and "=" not in arg
        elif arg.startswith("-"):
            for k, c in enumerate(arg[1:], 2):  # a short-option cluster, in order
                if c == short:
                    return True
                if c in values:
                    skip = k == len(arg)
                    break
        elif not operands:
            break
    return False


def quiet_grep(args: list[str]) -> bool:
    """True when this grep's own arguments include -q, --quiet or --silent."""
    return opt_set(args, "q", ("--quiet", "--silent"), GREP_VALUES)


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


def commands(toks: list[str]) -> list[tuple[str, int]]:
    """Each command name (its last path part) with the index of its first argument: the first word of each
    command, past assignments and words such as `!`, `then` or `env` that run the word after them."""
    found, at = [], True
    for i, tok in enumerate(toks):
        if at and (ASSIGN.match(tok) or tok in RUNS):
            continue
        if at and tok not in ENDS:
            found.append((tok.rsplit("/", 1)[-1], i + 1))
        at = tok in ENDS or tok in ("<(", ">(")  # a process substitution starts a command
    return found


def file_times(name: str, args: list[str]) -> set[str]:
    """The -nt and -ot operators of this [, [[ or test: its own words up to the closing ] or ]] (for [ and test
    also the next list operator), where the operator stands between two operands and does not follow a string
    operator, so [ "$x" = -nt ] is a string compare."""
    expr = []
    for arg in args:
        if arg == TESTS[name] or name != "[[" and arg in ENDS:
            break
        expr.append(arg)
    return {w for k, w in enumerate(expr[1:-1], 1) if w in ("-nt", "-ot") and expr[k - 1] not in STRING_OPS}


def forms(toks: list[str]) -> set[str]:
    """The bash 4 and GNU-only forms these words run, as keys of FORMS."""
    cmds, out = commands(toks), set()
    bsd_stat = any(name == "stat" and opt_set(toks[i:], "f", values=("c", "t")) for name, i in cmds)
    for name, i in cmds:
        args = toks[i:]
        if name in ("mapfile", "readarray", "timeout"):
            out.add(name)
        elif name == "xargs" and opt_set(args, "r", ("--no-run-if-empty",), XARGS_VALUES, operands=False):
            out.add("xargs -r")
        elif name in GREPS and opt_set(args, "P", ("--perl-regexp",), GREP_VALUES):
            out.add("grep -P")
        elif name == "stat" and opt_set(args, "c", ("--format", "--printf")) and not bsd_stat:
            out.add("stat -c")
        elif name in TESTS:
            out |= file_times(name, args)
    return out


def guards_timeout(toks: list[str]) -> bool:
    return any(toks[i : i + 3] == ["command", "-v", "timeout"] for i in range(len(toks)))


def sets_pipefail(toks: list[str]) -> bool:
    for i, tok in enumerate(toks[1:], 1):
        if tok == "pipefail" and re.fullmatch(r"-[A-Za-z]*o", toks[i - 1]) and "set" in toks[:i]:
            return True
    return False


def heredocs_in(toks: list[str]) -> list[tuple[str, bool]]:
    """The heredocs these words open, as (delimiter, strip leading tabs)."""
    docs = []
    for i, tok in enumerate(toks[:-1]):
        before = "".join(toks[:i])
        if tok == "<<" and before.count("((") <= before.count("))"):  # not a shift in $(( ))
            delim = toks[i + 1]
            if delim == "-" and i + 2 < len(toks):
                delim = "-" + toks[i + 2]
            docs.append((delim.lstrip("-"), delim.startswith("-")))
    return docs


def scan(text: str) -> tuple[bool, list[int], list[tuple[int, str]], bool, int | None]:
    """Return whether the file sets pipefail, the lines that pipe into grep -q, each (line, form) of a bash 4
    or GNU-only form, whether it checks command -v timeout, and the line that opened a quote, substitution or
    heredoc still open at the end (None when all closed)."""
    pipefail, found, gnu, guarded = False, set(), set(), False
    heredocs: list[tuple[str, bool]] = []  # pending (delimiter, strip leading tabs)
    carry: tuple[list[str], int] | None = None  # an unfinished command's words, and its first line
    stack: list[str] = []  # quotes and substitutions left open by the line before
    pending: list[str] = []  # the lines so far of a substitution left open, from line opened
    opened = open_at = doc_at = 0
    inner: int | None = None  # the first open line a substitution's own scan reported
    for n, line in enumerate(text.splitlines(), 1):
        if heredocs:
            if pending:  # the body belongs to the open substitution, whose own scan skips it
                pending.append(line)
            delim, tabs = heredocs[0]
            if (line.lstrip("\t") if tabs else line) == delim:
                heredocs.pop(0)
            continue
        in_code = not stack or stack[-1] not in ("'", '"')  # the line does not begin inside a quote
        if not stack:
            open_at = n
        cont = line.rstrip().endswith("\\")  # an escaped newline: the command goes on
        top, bodies, head, tail, stack = split(line.rstrip().removesuffix("\\"), stack)
        if tail is not None and cont:
            tail += "\\"  # the substitution's own scan joins the next line too
        subs = [(n, body) for body in bodies]
        if head is not None:
            subs.insert(0, (opened, "\n".join([*pending, head])))
            pending = []
        if tail is not None:
            opened = opened if pending else n
            pending.append(tail)
        for first, body in subs:  # a substitution's body is code of its own, carry and all
            _, lines, sub_gnu, sub_guarded, gap = scan(body)
            found.update(first + k - 1 for k in lines)
            gnu.update((first + k - 1, key) for k, key in sub_gnu)
            guarded = guarded or sub_guarded
            if gap is not None and inner is None:
                inner = first + gap - 1
        toks = words(top)
        pipefail = pipefail or sets_pipefail(toks)
        guarded = guarded or guards_timeout(toks)
        gnu.update((n, key) for key in forms(toks))
        if carry and toks:  # a form the continued command makes, not either part alone
            gnu.update((carry[1], key) for key in forms([*carry[0], *toks]) - forms(carry[0]) - forms(toks))
        if hits(toks):
            found.add(n)
        elif carry and toks and hits([*carry[0], *toks]):
            found.add(carry[1])
        if toks and cont:
            carry = ([*carry[0], *toks], carry[1]) if carry else (toks, n)
        elif toks:
            carry = ([toks[-1]], n) if toks[-1] in PIPES else None
        docs = heredocs_in(toks)
        if tail is not None and in_code:  # a heredoc opened inside a substitution left open
            docs += heredocs_in(words(tail))
        if docs and not heredocs:
            doc_at = n
        heredocs += docs
    if heredocs:
        return pipefail, sorted(found), sorted(gnu), guarded, doc_at
    return pipefail, sorted(found), sorted(gnu), guarded, open_at if stack else inner


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
        pipefail, found, gnu, guarded, gap = scan((root / rel).read_text(encoding="utf-8", errors="replace"))
        if gap is not None:  # fail closed: a parsing gap must be loud, never a silent skip
            print(f"FAIL: {rel}:{gap}: the lint could not find the end of the quote, substitution "
                  f"or heredoc opened here, so it could not read the lines after it")
            bad += 1
        fails = [(n, f"pipe into grep -q under pipefail; a writer killed by SIGPIPE fails the pipeline, "
                     f"so {FIX}") for n in found if pipefail]
        fails += [(n, FORMS[key]) for n, key in gnu if not (key == "timeout" and guarded)]
        for n, msg in sorted(fails):
            print(f"FAIL: {rel}:{n}: {msg}")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
