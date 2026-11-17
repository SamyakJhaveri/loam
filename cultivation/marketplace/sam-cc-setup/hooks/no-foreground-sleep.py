#!/usr/bin/env python3
"""PreToolUse on Bash: refuse a foreground call that runs `sleep`, alone or in a while or until poll loop.

A poll loop waits with sleep, so finding `sleep` where the shell runs it as a command finds the loop too.
That covers commands after `;`, `&&`, `|`, `do`, `then` and the like, behind a leading redirection,
behind `timeout` (with its options), `env` or `nice`, inside `$(...)`, backticks or `<(...)` outside
single quotes, and inside a `bash -c` or `sh -c` script. Arguments of any other command are data, not code:
`bin/tmux-job start NAME -- bash -c '... sleep ...'` runs its loop detached, and `bin/tmux-job wait`
is the sanctioned foreground wait. Heredoc bodies are data too. A call with run_in_background passes.

This is a scan for the forms an agent plausibly writes, not a shell parser. Known gaps, all allowed:
`eval`, `xargs`, `find -exec` or a variable running sleep; a substitution inside an unquoted heredoc
body; a redirection glued to a separator (`true;>x sleep 1`); sleep run by another language.
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
OPTION_ARGS = {"-s", "--signal", "-k", "--kill-after", "-n", "--adjustment", "-u", "--unset"}
REDIRECT = {"<", ">", "<<", ">>", "<<<", "<&", ">&", "&>", "&>>", "<>", ">|"}
SHELLS = {"bash", "sh", "zsh", "dash"}
NUMBER = re.compile(r"[0-9.]+[smhd]?")
HEREDOC = re.compile(r"(?<!<)<<-?(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

REASON = ("Refused: this Bash call waits in the foreground with sleep (a sleep or a sleep-poll loop). "
          "Run the work with run_in_background: true and act on its completion notice, "
          "wait on a recorded job with its waiter (distbench: `bin/tmux-job wait NAME SECONDS`), "
          "or watch a condition with the Monitor tool.")


def without_heredocs(script: str) -> str:
    kept, ends = [], []
    for line in script.splitlines():
        if ends:
            if line.strip() == ends[0]:
                ends.pop(0)
            continue
        kept.append(line)
        ends = [found.group(2) for found in HEREDOC.finditer(line)]
    return "\n".join(kept)


def substitutions(script: str) -> list[str]:
    """The bodies of `$(...)`, `<(...)`, `>(...)` and backticks outside single quotes, outermost only."""
    bodies, i, quoted = [], 0, False
    while i < len(script):
        char = script[i]
        if char == "\\":
            i += 2
            continue
        if char == '"':
            quoted = not quoted
        elif char == "'" and not quoted:
            end = script.find("'", i + 1)
            i = len(script) if end < 0 else end + 1
            continue
        elif char == "`":
            end = script.find("`", i + 1)
            end = len(script) if end < 0 else end
            bodies.append(script[i + 1:end])
            i = end + 1
            continue
        elif char in "$<>" and script.startswith("(", i + 1):
            depth, j = 1, i + 2
            while j < len(script) and depth:
                depth += {"(": 1, ")": -1}.get(script[j], 0)
                j += 1
            bodies.append(script[i + 2:j - 1])
            i = j
            continue
        i += 1
    return bodies


def tokens(script: str) -> list[str]:
    one_line = script.replace("\n", ";")
    lexer = shlex.shlex(one_line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def runs_sleep(script: str) -> bool:
    script = without_heredocs(script.replace("\\\n", " "))
    if any(runs_sleep(body) for body in substitutions(script)):
        return True
    try:
        words = tokens(script)
    except ValueError:
        return False
    at_command = True
    i = 0
    while i < len(words):
        word = words[i]
        i += 1
        if word and set(word) <= SEPARATOR:
            at_command = True
            continue
        if not at_command:
            continue
        if word in KEYWORDS or re.match(r"[A-Za-z_][A-Za-z0-9_]*=", word):
            continue
        if word.isdigit() and i < len(words) and words[i] in REDIRECT:
            continue  # the descriptor of a redirection such as 2>/dev/null
        if word in REDIRECT:
            i += 1  # its target; a command may follow
            continue
        name = os.path.basename(word)
        if name in WRAPPERS:
            while i < len(words) and (words[i].startswith("-") or NUMBER.fullmatch(words[i])):
                i += 2 if words[i] in OPTION_ARGS else 1
            continue
        at_command = False
        if name == "sleep":
            return True
        if name in SHELLS:
            while i < len(words) and not (words[i] and set(words[i]) <= SEPARATOR):
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
