#!/usr/bin/env python3
"""PreToolUse on Bash: refuse an ssh, scp or gh call whose shape makes the sandbox run it, and print the bare rewrite.

A program in settings `sandbox.excludedCommands` runs outside the sandbox only when every part of the
command is itself an excluded program. Otherwise the whole command runs sandboxed, where ssh fails with
"Could not resolve hostname" and gh with "tls: failed to verify certificate"; piped into grep, that error
can read as "no failures". Measured on Claude Code with ssh, scp and gh excluded (17 Nov 2026):
`ssh h a && scp h:f g` and `ssh h a; ssh h b` run bare; any local pipe, redirect or heredoc, `$(`,
backticks, `<(`, a loop, or a part such as `cd` or `echo` runs sandboxed, and so does `$(`, `$((` or a
backtick inside the quoted remote string. A multi-line quoted remote script and a `'"'"'` escape run bare.

The hook acts only when the sandbox is enabled and an excluded pattern names the program; it reads the
managed, user (`$CLAUDE_CONFIG_DIR`, else `~/.claude`) and project (`$CLAUDE_PROJECT_DIR`) settings.
This is a scan for the shapes an agent writes, not a shell parser; ssh run through `eval`, `xargs` or a
variable is not seen.
"""

from __future__ import annotations

import fnmatch
import json
import os
import pathlib
import re
import sys

TARGETS = {"ssh", "scp", "gh"}
CHAIN = {"&&", "||", ";", ";;"}
OPERATORS = sorted(["&&", "||", ";;", "|&", ">>", "<<<", "<<-", "<<", "&>>", "&>", ">&", "<&", ">|", "<>",
                    "|", "&", ";", ">", "<", "(", ")"], key=len, reverse=True)
KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "!", "{", "}", "time", "for", "in", "done", "fi"}
WRAPPERS = {"timeout", "env", "nice", "nohup", "command", "exec", "stdbuf", "setsid", "caffeinate"}
SHELLS = {"bash", "sh", "zsh", "dash"}
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
NUMBER = re.compile(r"[0-9.]+[smhd]?")
# Shapes the sandbox check treats as expansions even inside quotes; `=name` is zsh's command-path expansion.
BRACE = re.compile(r"\{[^{}]*(?:,|\.\.)[^{}]*\}")
QUOTED_EXPANSION = re.compile(r"\$\(|`|[<>]\(|(?:^|[\s'\"])=[A-Za-z_]")


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


def program(part: list[tuple[str, str]]) -> tuple[str, list[tuple[str, str]]]:
    """The command a simple command runs, past keywords, assignments and wrappers, and its arguments."""
    i = 0
    while i < len(part):
        word = part[i][1]
        name = os.path.basename(word)
        if word in KEYWORDS or ASSIGNMENT.match(word):
            i += 1
        elif name in WRAPPERS:
            i += 1
            while i < len(part) and (part[i][1].startswith("-") or NUMBER.fullmatch(part[i][1])):
                i += 1
        else:
            return name, part[i + 1:]
    return "", []


def settings_files() -> list[pathlib.Path]:
    """Lowest precedence first: user, project, local project, managed."""
    config = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or pathlib.Path.home() / ".claude")
    project = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / ".claude"
    return [config / "settings.json", project / "settings.json", project / "settings.local.json",
            pathlib.Path("/Library/Application Support/ClaudeCode/managed-settings.json"),
            pathlib.Path("/etc/claude-code/managed-settings.json")]


def sandbox_exclusions() -> list[str]:
    """The merged `sandbox.excludedCommands`, or none when no settings file enables the sandbox."""
    enabled, patterns = False, []
    for path in settings_files():
        try:
            sandbox = json.loads(path.read_text(encoding="utf-8")).get("sandbox") or {}
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(sandbox.get("enabled"), bool):
            enabled = sandbox["enabled"]
        patterns += [p for p in sandbox.get("excludedCommands") or [] if isinstance(p, str)]
    return patterns if enabled else []


def excluded(text: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith(" *") and (text == pattern[:-2] or text.startswith(pattern[:-1])):
            return True
        if fnmatch.fnmatchcase(text, pattern) or text == pattern:
            return True
    return False


def runs_target(scan: Scan, targets: set[str]) -> bool:
    for part in scan.parts:
        name, args = program(part)
        if name in targets:
            return True
        if name in SHELLS:
            for k, (_, flag) in enumerate(args[:-1]):
                if flag.startswith("-") and not flag.startswith("--") and "c" in flag:
                    if runs_target(Scan(args[k + 1][1]), targets):
                        return True
                    break
    return any(runs_target(Scan(body), targets) for body in scan.bodies)


SHAPE_WORDS = {"pipe": "a local pipe", "redirect": "a local redirect or heredoc",
               "subst": "a local `$(`, backtick or `<(`", "brace": "a local `{a,b}` brace expansion", "background": "a local `&`", "subshell": "a subshell"}


def problems(command: str, patterns: list[str]) -> tuple[list[str], list[str]]:
    """What makes the command sandboxed, and the bare calls it holds; both empty when it runs bare."""
    targets = {t for t in TARGETS if excluded(t + " x", patterns)}
    scan = Scan(command)
    if not targets or not runs_target(scan, targets):
        return [], []
    found = [SHAPE_WORDS[s] for s in sorted(scan.shapes) if s in SHAPE_WORDS]
    bare = []
    for part in scan.parts:
        text = " ".join(cooked for _, cooked in part)
        name, args = program(part)
        if not excluded(text, patterns):
            found.append(f"`{' '.join(raw for raw, _ in part)[:60]}` is not an excluded program")
        if name in targets:
            if any(QUOTED_EXPANSION.search(raw) for raw, _ in args):
                found.append(f"`$(`, `$((`, a backtick, `<(` or a word starting `=name` inside {name}'s "
                             "arguments, even quoted")
            bare.append(" ".join(raw for raw, _ in part))
    return found, bare


def main() -> int:
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    found, bare = problems(command, sandbox_exclusions())
    if not found:
        return 0
    rewrite = "\n".join(f"  {call}" for call in bare) or "  (none: the ssh, scp or gh call is inside a substitution)"
    print("Refused: this Bash call runs ssh, scp or gh in a shape the sandbox does not exempt, so it would run "
          "sandboxed and fail (ssh: \"Could not resolve hostname\"; gh: \"tls: failed to verify certificate\").\n"
          f"Found: {'; '.join(found)}.\n"
          f"Bare rewrite, each its own Bash call, with nothing else in it:\n{rewrite}\n"
          "Put filtering, `cd`, `$VAR` logic and redirects inside the single-quoted remote string, or in their own "
          "local call; write `$VAR` or `printenv` there instead of `$(`, `$((` or backticks, or ship a script "
          "with scp and run it with one ssh; for gh use --json/--jq or --body-file instead of a pipe or `$(`.",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
