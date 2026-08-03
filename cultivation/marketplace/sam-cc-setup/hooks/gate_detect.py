#!/usr/bin/env python3
"""Decide whether a Bash command string performs a `git commit`.

Reads the raw command text on stdin, prints GATE or PASS.
Used by pre-commit-gate.sh. Extracted to its own file 2026-08-02 so the logic
is directly testable and so no shell escaping sits between it and the tokenizer.

Design principle, from the hook it serves: a spurious block costs one rephrase,
a miss costs an unvalidated commit. So every ambiguous case resolves to GATE.

Revision history of the detection strategy:
  v1  '^\\s*git\\s+commit'  — start-anchored, FAILED OPEN on `cd X && git commit`,
      `git -c k=v commit`, `/usr/bin/git commit`.
  v2  a command-position regex — closed those, but FAILED CLOSED on any command
      whose *text* merely contained the phrase, because a regex cannot see shell
      quoting (`echo "a; git commit"`, heredocs, `python3 -c` scripts).
  v3  shlex tokenizing — fixed the quoting, but FAILED OPEN again on wrapper
      commands that push git past argv[0]: `env A=1 git commit`, `nice git commit`,
      `command git commit`, `sh -c "git commit"`.
  v4  tokenize, then apply three independent detectors. Any one gates.
  v5  (this) close `eval` and backslash-newline continuation; anchor the
      substitution check on a word boundary so `git commit-tree` is not gated.

KNOWN AND ACCEPTED LIMITATIONS — do not re-litigate these as bugs.

Text-level detection cannot see through indirection, because the word `git`
never appears in the command:

    G=git; $G commit -m x               not gated (variable holds the name)
    alias g='git'; g commit -m x        not gated (alias holds the name)
    x=$(printf commit); git $x -m x     not gated (variable holds the SUBcommand)
    ln -sf $(which git) ~/bin/g; g commit   not gated (symlink under another name)
    printf commit | xargs -I{} git {}   not gated (placeholder separates the words)

The symlink case is the most reachable of these — it needs no special shell
state and persists across sessions. It is still not closable from a static
string: knowing that `~/bin/g` resolves to git requires resolving the name on
the filesystem, and by then it is a different problem than reading a command.

Closing the xargs case would mean matching a `git` token and a `commit` token
ANYWHERE in the command rather than within one segment. That was considered and
rejected: it would gate `git log --oneline | grep commit`, an ordinary command,
and the forms it closes are ones no realistic caller emits. This gate exists to
stop an agent from forgetting `/validate`, not to resist a determined bypass —
anyone wanting to dodge it can simply delete the sentinel check. Accepting the
five exotic gaps above to keep everyday commands unblocked is the right trade.

ACCEPTED FALSE POSITIVES — these gate although nothing is committed:

    echo git commit                 unquoted mention (quoted ones are fine)
    grep -e git -e commit file      two unrelated patterns
    ls git commit                   literal filenames
    git help commit                 a real but harmless git subcommand
    cat <<'EOF' ... git commit      heredoc body; shlex has no heredoc concept
    echo sh -c "git commit"         mention of a nested-shell invocation

All are the same trade in the other direction: the detector deliberately ignores
command position, which is what lets it catch `env A=1 nice git commit` and
`env bash -c "git commit"` without enumerating wrappers. Restoring
position-awareness would cut these but reopen that whole class. Six odd-looking
commands costing one rephrase each is cheaper than one unvalidated commit.
"""

import os
import re
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "\n"}
# Commands whose string arguments are themselves shell code, so the check has
# to recurse into them. `eval` belongs here for the same reason `sh -c` does.
INTERPRETERS = {"sh", "bash", "zsh", "dash", "ksh", "eval"}


def _normalise(cmd):
    """One quote-aware pass that makes the text mean to shlex what it means to bash.

    Three jobs, all of which MUST happen together and in this order, because
    doing any one of them separately has already caused a real bug:

    1. **Backslash-newline continuations are deleted.** shlex does not do this;
       it leaves the newline inside the next token, so `git \\<nl>commit` used to
       yield the token '\\ncommit' and never match. Doing it char-by-char also
       fixes backslash parity for free (`git \\\\<nl>commit` is a literal
       backslash, not a continuation, and bash agrees).

    2. **`#` comments are dropped to end of physical line, when unquoted.** Doing
       this AFTER a blind continuation-join merged a comment line into the next
       command, and shlex then swallowed both, giving zero tokens and a total
       bypass:  `# note \\` / `git commit -m x`.  Doing it with a blunt split
       instead of quote-tracking cuts `git commit -m "fix #42"` mid-string.

    3. **Real newlines become `;`.** `_segments` splits on separator TOKENS, but
       shlex treats a newline as ordinary whitespace and never emits one, so
       every line of a multi-line command collapsed into a single segment. That
       gated wholly unrelated lines -- `git status` on one line and
       `grep commit CHANGELOG.md` on the next was enough. Newlines INSIDE quotes
       are left alone, so multi-line strings still parse.

    Findings 2 and 3 both came from the security re-scan, 2026-08-02.
    """
    out = []
    quote = None
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if quote:
            # inside a quoted string: only the matching quote (and, in double
            # quotes, a backslash escape) is special. '#' and newline are not.
            if c == "\\" and quote == '"' and i + 1 < n:
                out.append(c)
                out.append(cmd[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            out.append(c)
            i += 1
            continue
        if c in "'\"":
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n and cmd[i + 1] == "\n":
            i += 2                      # line continuation: delete both
            continue
        if c == "\\" and i + 2 < n and cmd[i + 1] == "\r" and cmd[i + 2] == "\n":
            i += 3                      # ... and the CRLF form
            continue
        if c == "\\" and i + 1 < n:
            out.append(c)               # any other escape: keep the pair intact
            out.append(cmd[i + 1])
            i += 2
            continue
        if c == "#" and (i == 0 or cmd[i - 1] in " \t\n"):
            while i < n and cmd[i] != "\n":
                i += 1                  # comment runs to end of PHYSICAL line
            continue
        if c in "\n\r":
            out.append(";")             # a real line break IS a separator
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _tokenize(cmd):
    """Shell-aware tokens, or None if the string cannot be parsed."""
    try:
        lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return None  # unbalanced quotes


def _segments(tokens):
    """Split a token list on shell operators into individual command segments."""
    out, current = [], []
    for t in tokens:
        if t in SEPARATORS:
            out.append(current)
            current = []
        else:
            current.append(t)
    out.append(current)
    return [s for s in out if s]


def _has_git_then_commit(seg):
    """Detector 1: a bare `git` token followed by a bare `commit` token.

    Catches both the plain forms (`git commit`, `git -c user.email=x commit`)
    and every transparent-wrapper form, without having to enumerate wrappers:
    `env A=1 git commit`, `nice git commit`, `command git commit`,
    `sudo git commit`, `timeout 5 git commit`, `find . -exec git commit ;`.

    An earlier revision also carried a stricter "git in command position with
    commit as its immediate subcommand" detector. It was removed 2026-08-02 as
    provably dead: it required `seg[j] == "commit"` for some j > i, which this
    membership test already covers, so it could never change the verdict.

    It stays quiet on quoted mentions because shlex collapses a quoted phrase
    into ONE token, so `echo 'git commit'` yields no bare `git` token at all.
    Segment scoping keeps `git log | grep commit` out: those are two segments.
    Known benign false positive: `git help commit`. Fails in the safe direction.
    """
    for i, tok in enumerate(seg):
        if os.path.basename(tok) == "git":
            if "commit" in seg[i + 1:]:
                return True
    return False


def _interpreter_payloads(seg):
    """Detector 2: strings handed to a nested shell, e.g. sh -c "git commit".

    Scans the WHOLE segment for an interpreter token rather than only the
    command position. An earlier revision checked position 0 (after skipping
    VAR=value prefixes) and so missed every wrapped form -- `env bash -c
    "git commit"`, `nice sh -c ...`, `sudo bash -c ...` -- because the wrapper
    occupied the position it looked at. Found by Codex Sol review, 2026-08-02.

    Scanning everywhere also gates `echo sh -c "git commit"`, which is a
    mention rather than an invocation. That is the safe direction and consistent
    with the rest of this module.
    """
    payloads = []
    for i, tok in enumerate(seg):
        if os.path.basename(tok) in INTERPRETERS:
            payloads.extend(seg[i + 1:])
    return payloads


# `(?![-\w])` not `(?:\s|$)`: the subcommand must not continue into
# `commit-tree` / `commit-graph` / `commitmsg`, but it may legitimately be
# followed by a quote or a backslash, as in `printf 'git commit\n' | bash`.
GIT_COMMIT_TEXT = re.compile(r"git\s+commit(?![-\w])")
# `sh`/`bash` reading its script from a PIPE rather than from -c: there is no
# argv payload for _interpreter_payloads to recurse into, so the whole thing is
# invisible to token analysis. Found by test-synthesis, 2026-08-02.
PIPED_INTERPRETER = re.compile(r"\|\s*(?:\w+\s+)*(?:sh|bash|zsh|dash|ksh)\b")


def gates(cmd, _depth=0):
    cmd = _normalise(cmd)

    # Two shapes that hide an invocation from the tokenizer entirely. Both are
    # handled bluntly on the raw text, because by definition the tokens cannot
    # show them.
    #
    # `commit` must END where it is matched. Note \b is NOT enough: it matches
    # between the 't' and the '-' of `git commit-tree $(git write-tree)`, so
    # that plumbing command was gated as if it were a commit.
    if GIT_COMMIT_TEXT.search(cmd):
        if "$(" in cmd or "`" in cmd:       # command substitution
            return True
        if PIPED_INTERPRETER.search(cmd):   # printf '...' | bash
            return True

    tokens = _tokenize(cmd)
    if tokens is None:
        return True  # unparseable, so do not let it through

    for seg in _segments(tokens):
        if _has_git_then_commit(seg):
            return True
        if _depth < 3:  # bounded: sh -c "sh -c '...'" is already absurd
            for payload in _interpreter_payloads(seg):
                if gates(payload, _depth + 1):
                    return True
    return False


if __name__ == "__main__":
    print("GATE" if gates(sys.stdin.read()) else "PASS")
