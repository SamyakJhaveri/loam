#!/usr/bin/env python3
"""PreToolUse on Bash: refuse a command that a `Bash(...)` deny rule names once it is written the plain way.

Claude Code matches a Bash deny rule against each part's text, after stripping `timeout`, `nice` and a few
other wrappers, so another spelling of the same command passes the rule. On 17 Nov 2026 an agent ran
`git -C <dir> push --force-with-lease=<branch>:<sha> origin <branch>` past `Bash(git push --force-with-lease:*)`:
git's global options came before the subcommand, and `--opt=value` is not `--opt value`.
The hook rewrites each part to its plain form and refuses when that form matches a deny rule the part as
written does not: git's global options (`-C`, `-c`, `--git-dir`, `--work-tree`, `--no-pager` and the rest)
dropped, `--opt=value` split, quotes removed, a program path cut to its name, and keywords, assignments and
wrappers (`env`, `sudo`, `exec` and Claude Code's own) dropped. It also checks the scripts inside
`$(...)`, backticks and `bash -c`, where the rule never looks.
It reads `permissions.deny` from the user (`$CLAUDE_CONFIG_DIR`, else `~/.claude`), project
(`$CLAUDE_PROJECT_DIR`), local project and managed settings.

This is a scan for the spellings an agent writes, not a shell parser. Known gaps, all allowed: option
order (`git push origin b --force`), joined short flags (`git clean -fd`), a `+refspec` push, a wrapper
option with an operand (`sudo -u x`, `env -C dir`), and `eval`, `xargs` with flags, `find -exec` or a
variable running the command.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys

CHAIN = {"&&", "||", ";", ";;"}
OPERATORS = sorted(["&&", "||", ";;", "|&", ">>", "<<<", "<<-", "<<", "&>>", "&>", ">&", "<&", ">|", "<>",
                    "|", "&", ";", ">", "<", "(", ")"], key=len, reverse=True)
KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "!", "{", "}", "time", "for", "in", "done", "fi"}
# Claude Code strips timeout, time, nice, nohup, stdbuf, command, builtin, noglob and bare xargs; the rest it does not.
WRAPPERS = {"timeout", "nice", "nohup", "stdbuf", "command", "builtin", "noglob", "xargs", "env", "exec", "sudo",
            "doas", "setsid", "caffeinate"}
SHELLS = {"bash", "sh", "zsh", "dash"}
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
NUMBER = re.compile(r"[0-9.]+[smhd]?")
BRACE = re.compile(r"\{[^{}]*(?:,|\.\.)[^{}]*\}")
# git's global options that take the next word as their value (git(1)); every other leading option takes none.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix",
                     "--attr-source"}
MANAGED = [pathlib.Path("/Library/Application Support/ClaudeCode"), pathlib.Path("/etc/claude-code")]


def closing(text: str, i: int) -> int:
    """Index just past the `)` matching the `(` at text[i]."""
    depth = 0
    while i < len(text):
        depth += {"(": 1, ")": -1}.get(text[i], 0)
        i += 1
        if not depth:
            break
    return i


class Scan:
    """The command split into simple commands, each a list of (raw, cooked) words, plus the local shapes seen."""

    def __init__(self, text: str) -> None:
        self.parts: list[list[tuple[str, str]]] = []
        self.shapes: set[str] = set()
        self.bodies: list[str] = []  # the scripts inside $(...), <(...), >(...) and backticks
        words: list[tuple[str, str]] = []
        raw = cooked = unquoted = ""
        started = False
        heredocs: list[str] = []
        target = ""  # "file" or "heredoc" when the next word is a redirection's target, not part of the command

        def end_word() -> None:
            nonlocal raw, cooked, unquoted, started, target
            if BRACE.search(unquoted):
                self.shapes.add("brace")
            if started:
                if target == "heredoc":
                    heredocs.append(cooked)
                elif not target:
                    words.append((raw, cooked))
                target = ""
            raw = cooked = unquoted = ""
            started = False

        def end_part() -> None:
            nonlocal words
            end_word()
            if words:
                self.parts.append(words)
            words = []

        i = 0
        while i < len(text):
            char = text[i]
            if char == "\\":
                if text.startswith("\n", i + 1):
                    i += 2
                    continue
                raw, cooked, started = raw + text[i:i + 2], cooked + text[i + 1:i + 2], True
                i += 2
            elif char == "'":
                end = text.find("'", i + 1)
                end = len(text) if end < 0 else end
                raw, cooked, started = raw + text[i:end + 1], cooked + text[i + 1:end], True
                i = end + 1
            elif char == '"':
                j = i + 1
                while j < len(text) and text[j] != '"':
                    if text[j] == "\\":
                        j += 1
                    elif text.startswith("$(", j):
                        self.shapes.add("subst")
                        self.bodies.append(text[j + 2:closing(text, j + 1) - 1])
                        j = closing(text, j + 1) - 1
                    elif text[j] == "`":
                        end = text.find("`", j + 1)
                        end = len(text) if end < 0 else end
                        self.shapes.add("subst")
                        self.bodies.append(text[j + 1:end])
                        j = end
                    j += 1
                raw, cooked, started = raw + text[i:j + 1], cooked + text[i + 1:j], True
                i = j + 1
            elif char == "`" or (char in "$<>" and text.startswith("(", i + 1)):
                end = text.find("`", i + 1) + 1 if char == "`" else closing(text, i + 1)
                end = len(text) if end <= 0 else end
                self.shapes.add("subst")
                self.bodies.append(text[i + 1:end - 1] if char == "`" else text[i + 2:end - 1])
                raw, cooked, started = raw + text[i:end], cooked + text[i:end], True
                i = end
            elif char == "#" and not started:
                i = text.find("\n", i)
                i = len(text) if i < 0 else i
            elif char in " \t":
                end_word()
                i += 1
            elif char == "\n":
                end_part()
                i += 1
                while heredocs:  # skip each pending heredoc body, which is data
                    delimiter = heredocs.pop(0)
                    while i < len(text):
                        line_end = text.find("\n", i)
                        line_end = len(text) if line_end < 0 else line_end
                        line, i = text[i:line_end], line_end + 1
                        if line.strip() == delimiter:
                            break
            elif char in "|&;<>()":
                op = next(o for o in OPERATORS if text.startswith(o, i))
                if op[0] in "<>&" and started and cooked.isdigit():
                    raw = cooked = ""  # the descriptor of a redirection such as 2>&1
                    started = False
                if op in CHAIN or op in {"|", "|&", "&", "(", ")"}:
                    end_part()
                    self.shapes.add({"|": "pipe", "|&": "pipe", "&": "background", "(": "subshell",
                                     ")": "subshell"}.get(op, "chain"))
                elif op in {">&", "<&"} and text[i + len(op):i + len(op) + 1].isdigit():
                    end_word()
                    i += 1  # 2>&1 joins two descriptors; that alone keeps a call bare
                else:
                    end_word()
                    self.shapes.add("redirect")
                    target = "heredoc" if op in {"<<", "<<-"} else "file"
                i += len(op)
            else:
                raw, cooked, unquoted, started = raw + char, cooked + char, unquoted + char, True
                i += 1
        end_part()




def plain(part: list[tuple[str, str]]) -> list[str]:
    """The part's words as a deny rule expects them: no keywords, assignments, wrappers, program path,
    git global options or `--opt=value` joins."""
    words = [cooked for _, cooked in part]
    i = 0
    while i < len(words):
        if words[i] in KEYWORDS or ASSIGNMENT.match(words[i]):
            i += 1
        elif os.path.basename(words[i]) in WRAPPERS:
            i += 1
            while i < len(words) and (words[i].startswith("-") or NUMBER.fullmatch(words[i])):
                i += 1  # the wrapper's options and timeout's duration
        else:
            break
    if i == len(words):
        return []
    name, args = os.path.basename(words[i]), words[i + 1:]
    if name == "git":
        while args and args[0].startswith("-"):
            args = args[2:] if args[0] in GIT_VALUE_OPTIONS else args[1:]
    split = []
    for word in args:
        option, equals, value = word.partition("=")
        split += [option, value] if equals and option.startswith("--") and len(option) > 2 else [word]
    return [name, *split]


def scripts(scan: Scan) -> list[str]:
    """The scripts a part runs that a deny rule never sees: `$(...)`, backticks and `bash -c '...'`."""
    found = list(scan.bodies)
    for part in scan.parts:
        words = plain(part)
        if words and words[0] in SHELLS:
            found += [words[k + 1] for k, flag in enumerate(words[1:-1], 1)
                      if flag.startswith("-") and not flag.startswith("--") and "c" in flag][:1]
    return found


def deny_rules() -> list[str]:
    """Every `Bash(...)` rule in `permissions.deny`, from the settings files Claude Code reads."""
    config = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or pathlib.Path.home() / ".claude")
    project = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / ".claude"
    files = [config / "settings.json", project / "settings.json", project / "settings.local.json"]
    for managed in MANAGED:
        files += [managed / "managed-settings.json", *sorted((managed / "managed-settings.d").glob("*.json"))]
    rules = []
    for path in files:
        try:
            deny = json.loads(path.read_text(encoding="utf-8")).get("permissions", {}).get("deny") or []
        except (OSError, ValueError, AttributeError):
            continue
        rules += [r for r in deny if isinstance(r, str) and r.startswith("Bash(") and r.endswith(")")]
    return rules


def pattern(rule: str) -> re.Pattern[str]:
    """Claude Code's reading of `Bash(<text>)`: `*` is any text, `:*` at the end is ` *`, and a lone trailing
    ` *` also matches the bare command."""
    text = rule[5:-1]
    text = text[:-2] + " *" if text.endswith(":*") else text
    if text.endswith(" *") and text.count("*") == 1:
        return re.compile(re.escape(text[:-2]) + "(?: .*)?", re.S)
    return re.compile(".*".join(map(re.escape, text.split("*"))), re.S)


def refusal(command: str, rules: list[tuple[str, re.Pattern[str]]], nested: bool = False) -> str:
    """The first part whose plain form a deny rule names and its written form does not, explained; else ""."""
    scan = Scan(command)
    for part in scan.parts:
        written, words = " ".join(raw for raw, _ in part), plain(part)
        for rule, regex in rules:
            if words and regex.fullmatch(" ".join(words)) and (nested or not regex.fullmatch(written)):
                return (f"Refused: `{written[:200]}` runs `{' '.join(words)[:200]}`, which the deny rule `{rule}` "
                        "names. The rule matches command text, so this spelling slipped past it, but it still "
                        "means no. Do not respell the command; if the step is needed, ask the owner to run it.")
    for script in scripts(scan):
        found = refusal(script, rules, nested=True)
        if found:
            return found
    return ""


def main() -> int:
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    rules = [(rule, pattern(rule)) for rule in deny_rules()]
    found = refusal(command, rules) if rules else ""
    if found:
        print(found, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
