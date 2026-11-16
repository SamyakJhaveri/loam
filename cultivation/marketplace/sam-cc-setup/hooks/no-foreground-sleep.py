#!/usr/bin/env python3
"""PreToolUse on Bash: refuse a foreground call that runs `sleep`, alone or in a while or until poll loop.

A poll loop waits with sleep, so finding `sleep` where the shell runs it as a command finds the loop too.
That covers commands after `;`, `&&`, `|`, `do`, `then` and the like, behind `timeout`, `env` or
`nice`, and inside a `bash -c` or `sh -c` script. Arguments of any other command are data, not code:
`bin/tmux-job start NAME -- bash -c '... sleep ...'` runs its loop detached, and `bin/tmux-job wait`
is the sanctioned foreground wait. Heredoc bodies are data too. A call with run_in_background passes.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys

SEPARATOR = set(";&|()")
KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "!", "{", "time"}
WRAPPERS = {"timeout", "env", "nice", "nohup", "command", "exec", "stdbuf", "setsid"}
SHELLS = {"bash", "sh", "zsh", "dash"}
NUMBER = re.compile(r"[0-9.]+[smhd]?")
HEREDOC = re.compile(r"(?<!<)<<-?(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

REASON = ("Refused: this Bash call waits in the foreground with sleep (a sleep or a sleep-poll loop). "
          "Run the work with run_in_background: true and act on its completion notice, "
          "wait on a recorded job with its waiter (distbench: `bin/tmux-job wait NAME SECONDS`), "
          "or watch a condition with the Monitor tool.")


def without_heredocs(script: str) -> str:
    kept, end = [], None
    for line in script.splitlines():
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        kept.append(line)
        found = HEREDOC.search(line)
        end = found.group(2) if found else None
    return "\n".join(kept)


def tokens(script: str) -> list[str]:
    one_line = without_heredocs(script.replace("\\\n", " ")).replace("\n", ";")
    lexer = shlex.shlex(one_line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def runs_sleep(script: str) -> bool:
    try:
        words = tokens(script)
    except ValueError:
        return False
    at_command = True
    i = 0
    while i < len(words):
        word = words[i]
        i += 1
        if set(word) <= SEPARATOR:
            at_command = True
            continue
        if not at_command:
            continue
        if word in KEYWORDS or re.match(r"[A-Za-z_][A-Za-z0-9_]*=", word):
            continue
        name = os.path.basename(word)
        if name in WRAPPERS:
            while i < len(words) and (words[i].startswith("-") or NUMBER.fullmatch(words[i])):
                i += 1
            continue
        at_command = False
        if name == "sleep":
            return True
        if name in SHELLS:
            while i < len(words) and not set(words[i]) <= SEPARATOR:
                flag = words[i]
                i += 1
                if flag.startswith("-") and not flag.startswith("--") and "c" in flag and i < len(words):
                    if runs_sleep(words[i]):
                        return True
                    break
    return False


def main() -> int:
    tool_input = json.load(sys.stdin).get("tool_input", {})
    if tool_input.get("run_in_background") or not runs_sleep(tool_input.get("command", "")):
        return 0
    print(REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
