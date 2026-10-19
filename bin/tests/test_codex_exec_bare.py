#!/usr/bin/env python3
"""A shipped Codex call is one bare `codex exec` command.

Claude Code honors a sandbox exclusion such as `codex exec *` only for that bare command. A pipe,
a prefix, or any redirect (even `< /dev/null`) puts Codex back inside Claude's sandbox, and a `<`
anywhere, even quoted, leaves Codex waiting on an open stdin. A command substitution (`$(...)` or
backticks), even quoted, runs a second command in the call, so it is not bare either.
`<name>` placeholders are filled in.
"""

from __future__ import annotations

import pathlib
import re
import shlex
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CODEX_EXEC = re.compile(r"\bcodex\s+exec\b")
PLACEHOLDER = re.compile(r"<[a-z]+>")


def fenced_commands(text: str):
    """Yield (line, command) for each command in a fenced block, with continuations joined."""
    fenced, start, parts = False, 0, []
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced, parts = not fenced, []
            continue
        if not fenced:
            continue
        start = start if parts else n
        parts.append(line.strip())
        if not line.endswith("\\"):
            yield start, " ".join(p.rstrip("\\") for p in parts)
            parts = []


def is_bare(cmd: str) -> bool:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    tokens = list(lex)
    return (tokens[:2] == ["codex", "exec"] and "<" not in PLACEHOLDER.sub("", cmd)
            and "$(" not in cmd and "`" not in cmd
            and not any(set(t) <= set("();<>|&") for t in tokens))


class CodexExecBare(unittest.TestCase):
    def test_every_shipped_codex_exec_is_bare(self):
        files = subprocess.run(["git", "ls-files", "--", "seed", "cultivation/marketplace"], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.splitlines()
        calls, bad = 0, []
        for f in files:
            if not f.endswith((".md", ".md.jinja")):
                continue
            for n, cmd in fenced_commands((ROOT / f).read_text(encoding="utf-8")):
                if not CODEX_EXEC.search(cmd):
                    continue
                calls += 1
                if not is_bare(cmd):
                    bad.append(f"{f}:{n}: {cmd[:100]}")
        self.assertGreater(calls, 0, "no shipped codex exec call found; the scan is broken")
        self.assertEqual([], bad)

    def test_is_bare_rejects_pipes_prefixes_and_redirects(self):
        self.assertTrue(is_bare('codex exec -o "<out>" "Review <scope>; map a -> b; no preamble."'))
        for cmd in ('git diff | codex exec "x"', 'OUT=a codex exec "x"', 'mkdir -p d && codex exec "x"',
                    'codex exec "x" < /dev/null', 'codex exec "x" > log 2>&1', 'codex exec "x"; echo done',
                    'codex exec "Respond in <=60 lines."', 'codex exec "$(git diff)"', 'codex exec "`git diff`"'):
            self.assertFalse(is_bare(cmd), cmd)


if __name__ == "__main__":
    unittest.main()
