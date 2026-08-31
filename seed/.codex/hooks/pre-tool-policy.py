#!/usr/bin/env python3
"""Block recognizable literal force-push commands before Codex runs Bash."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys


_DENIAL = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Force pushes are blocked by repository policy."
        ),
    }
}
_COMMAND_BOUNDARY = set(";&|(){}\n")
_OPAQUE_ANSI_C_CHARACTER = "\ufffd"
_GIT_GLOBAL_NO_ARGUMENT = {
    "--bare",
    "--glob-pathspecs",
    "--help",
    "--icase-pathspecs",
    "--literal-pathspecs",
    "--no-advice",
    "--no-lazy-fetch",
    "--no-optional-locks",
    "--no-pager",
    "--no-replace-objects",
    "--noglob-pathspecs",
    "--paginate",
    "--version",
    "-P",
    "-p",
}
_GIT_GLOBAL_TERMINAL = {
    "--help",
    "--html-path",
    "--info-path",
    "--man-path",
    "--version",
    "-h",
    "-v",
}
_GIT_GLOBAL_WITH_ARGUMENT = {
    "--config-env",
    "--exec-path",
    "--git-dir",
    "--namespace",
    "--super-prefix",
    "--work-tree",
    "-C",
    "-c",
}
_PUSH_LONG_OPTION_ARITY = {
    "--all": 0,
    "--atomic": 0,
    "--branches": 0,
    "--delete": 0,
    "--dry-run": 0,
    "--exec": 1,
    "--follow-tags": 0,
    "--force": 0,
    "--force-if-includes": 0,
    "--force-with-lease": 0,
    "--help": 0,
    "--ipv4": 0,
    "--ipv6": 0,
    "--mirror": 0,
    "--no-all": 0,
    "--no-atomic": 0,
    "--no-branches": 0,
    "--no-delete": 0,
    "--no-dry-run": 0,
    "--no-exec": 0,
    "--no-follow-tags": 0,
    "--no-force": 0,
    "--no-force-if-includes": 0,
    "--no-force-with-lease": 0,
    "--no-mirror": 0,
    "--no-porcelain": 0,
    "--no-progress": 0,
    "--no-prune": 0,
    "--no-push-option": 0,
    "--no-quiet": 0,
    "--no-receive-pack": 0,
    "--no-recurse-submodules": 0,
    "--no-repo": 0,
    "--no-set-upstream": 0,
    "--no-signed": 0,
    "--no-tags": 0,
    "--no-thin": 0,
    "--no-verbose": 0,
    "--no-verify": 0,
    "--porcelain": 0,
    "--progress": 0,
    "--prune": 0,
    "--push-option": 1,
    "--quiet": 0,
    "--receive-pack": 1,
    "--recurse-submodules": 0,
    "--repo": 1,
    "--set-upstream": 0,
    "--signed": 0,
    "--tags": 0,
    "--thin": 0,
    "--verbose": 0,
    "--verify": 0,
}


def _fail(reason: str) -> int:
    print(f"pre-tool-policy: {reason}", file=sys.stderr)
    return 2


def _read_ansi_c_word(command: str, start: int) -> tuple[str, int]:
    decoded: list[str] = []
    escapes = {
        "a": "\a",
        "b": "\b",
        "e": "\x1b",
        "E": "\x1b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    index = start
    while index < len(command) and command[index] != "'":
        character = command[index]
        if character != "\\" or index + 1 >= len(command):
            decoded.append(character)
            index += 1
            continue
        escaped = command[index + 1]
        if escaped in escapes:
            decoded.append(escapes[escaped])
            index += 2
            continue
        if escaped in "01234567":
            end = index + 2
            while end < min(index + 4, len(command)):
                if command[end] not in "01234567":
                    break
                end += 1
            decoded.append(chr(int(command[index + 1 : end], 8) & 0xFF))
            index = end
            continue
        widths = {"x": 2, "u": 4, "U": 8}
        if escaped in widths:
            end = index + 2
            limit = min(end + widths[escaped], len(command))
            while end < limit and command[end] in "0123456789abcdefABCDEF":
                end += 1
            if end > index + 2:
                codepoint = int(command[index + 2 : end], 16)
                decoded.append(
                    chr(codepoint)
                    if codepoint <= sys.maxunicode
                    else _OPAQUE_ANSI_C_CHARACTER
                )
                index = end
                continue
        decoded.extend(("\\", escaped))
        index += 2
    return "".join(decoded), index + 1


def _quote_posix_word(word: str) -> str:
    return "'" + word.replace("'", "'\"'\"'") + "'"


def _prepare_shell_text(command: str) -> str:
    prepared: list[str] = []
    quote: str | None = None
    word_started = False
    index = 0
    while index < len(command):
        character = command[index]
        if quote != "'" and character == "\\":
            if command.startswith("\\\r\n", index):
                index += 3
                continue
            if command.startswith("\\\n", index):
                index += 2
                continue
        if quote == "'":
            prepared.append(character)
            if character == "'":
                quote = None
            index += 1
            continue
        if quote == '"':
            prepared.append(character)
            if character == '"':
                quote = None
            elif character == "\\" and index + 1 < len(command):
                prepared.append(command[index + 1])
                index += 1
            index += 1
            continue
        if command.startswith("$'", index):
            ansi_word, index = _read_ansi_c_word(command, index + 2)
            prepared.append(_quote_posix_word(ansi_word))
            word_started = True
            continue
        if command.startswith('$"', index):
            prepared.append('"')
            quote = '"'
            word_started = True
            index += 2
            continue
        if character in {"'", '"'}:
            quote = character
            word_started = True
            prepared.append(character)
            index += 1
            continue
        if character == "\\" and index + 1 < len(command):
            word_started = True
            prepared.extend((character, command[index + 1]))
            index += 2
            continue
        if character == "#" and not word_started:
            while index < len(command) and command[index] != "\n":
                index += 1
            continue
        prepared.append(character)
        if character in " \t\n;&|()<>":
            word_started = False
        else:
            word_started = True
        index += 1
    return "".join(prepared)


def _literal_tokens(command: str) -> tuple[str, ...]:
    lexer = shlex.shlex(
        _prepare_shell_text(command),
        posix=True,
        punctuation_chars=";&|(){}<>\n",
    )
    lexer.commenters = ""
    lexer.whitespace = " \t"
    lexer.whitespace_split = True
    return tuple(lexer)


def _redirection_end(tokens: tuple[str, ...], start: int) -> int | None:
    operator_index = start
    named_operator: str | None = None
    if tokens[start].isdigit():
        operator_index += 1
    elif tokens[start] == "{" and start + 2 < len(tokens):
        closing = tokens[start + 2]
        if closing.startswith("}") and len(closing) > 1:
            operator_index += 2
            named_operator = closing[1:]
        elif closing == "}" and start + 3 < len(tokens):
            operator_index += 3
    if operator_index >= len(tokens):
        return None
    operator = named_operator or tokens[operator_index]
    if not (
        operator
        and set(operator) <= {"<", ">", "&", "|"}
        and set(operator) & {"<", ">"}
    ):
        return None
    target_index = operator_index + 1
    if operator == "<<" and target_index < len(tokens):
        if tokens[target_index] == "-":
            target_index += 1
    if target_index >= len(tokens):
        return None
    return target_index + 1


def _git_candidate(tokens: tuple[str, ...], start: int) -> tuple[str, ...]:
    candidate: list[str] = []
    index = start
    while index < len(tokens):
        redirection_end = _redirection_end(tokens, index)
        if redirection_end is not None:
            candidate.extend(tokens[index:redirection_end])
            index = redirection_end
            continue
        word = tokens[index]
        if candidate and word and set(word) <= _COMMAND_BOUNDARY:
            break
        candidate.append(word)
        index += 1
    return tuple(candidate)


def _push_arguments(words: tuple[str, ...]) -> tuple[str, ...] | None:
    if not words or words[0] != "git":
        return None
    remaining = words[1:]
    index = 0
    while index < len(remaining):
        word = remaining[index]
        redirection_end = _redirection_end(remaining, index)
        if redirection_end is not None:
            index = redirection_end
            continue
        if word == "push":
            return tuple(remaining[index + 1 :])
        if word in _GIT_GLOBAL_TERMINAL:
            return None
        if word in _GIT_GLOBAL_NO_ARGUMENT:
            index += 1
            continue
        if word in _GIT_GLOBAL_WITH_ARGUMENT:
            if index + 1 >= len(remaining):
                return None
            index += 2
            continue
        if any(
            word.startswith(f"{option}=")
            for option in _GIT_GLOBAL_WITH_ARGUMENT
            if option.startswith("--")
        ):
            index += 1
            continue
        if (word.startswith("-C") or word.startswith("-c")) and len(word) > 2:
            index += 1
            continue
        return None
    return None


def _canonical_push_option(word: str) -> tuple[str, bool, int] | None:
    name, separator, _ = word.partition("=")
    if name in _PUSH_LONG_OPTION_ARITY:
        return name, bool(separator), _PUSH_LONG_OPTION_ARITY[name]
    matches = [
        option for option in _PUSH_LONG_OPTION_ARITY if option.startswith(name)
    ]
    if len(matches) == 1:
        canonical = matches[0]
        return (
            canonical,
            bool(separator),
            _PUSH_LONG_OPTION_ARITY[canonical],
        )
    return None


def _is_force_push(words: tuple[str, ...]) -> bool:
    arguments = _push_arguments(words)
    if arguments is None:
        return False
    dry_run = False
    force = False
    force_with_lease = False
    repository_from_option = False
    positionals: list[str] = []
    index = 0
    options = True
    while index < len(arguments):
        word = arguments[index]
        if options and word == "--":
            options = False
            index += 1
            continue
        if not options or not word.startswith("-") or word == "-":
            positionals.append(word)
            index += 1
            continue
        if word.startswith("--"):
            option = _canonical_push_option(word)
            if option is None:
                index += 1
                continue
            canonical, assigned, arity = option
            if canonical == "--help":
                return False
            if canonical == "--dry-run":
                dry_run = True
            elif canonical == "--no-dry-run":
                dry_run = False
            elif canonical == "--force":
                force = True
            elif canonical == "--no-force":
                force = False
            elif canonical == "--force-with-lease":
                force_with_lease = True
            elif canonical == "--no-force-with-lease":
                force_with_lease = False
            if arity:
                if canonical == "--repo":
                    repository_from_option = True
                if not assigned:
                    if index + 1 >= len(arguments):
                        return False
                    index += 1
            index += 1
            continue

        cluster = word[1:]
        cluster_index = 0
        while cluster_index < len(cluster):
            option = cluster[cluster_index]
            if option == "h":
                return False
            if option == "f":
                force = True
            elif option == "n":
                dry_run = True
            elif option in {"o", "r"}:
                if cluster_index + 1 == len(cluster):
                    if index + 1 >= len(arguments):
                        return False
                    index += 1
                break
            cluster_index += 1
        index += 1

    refspecs = positionals if repository_from_option else positionals[1:]
    plus_refspec = any(len(word) > 1 and word.startswith("+") for word in refspecs)
    return not dry_run and (force or force_with_lease or plus_refspec)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeError):
        return _fail("stdin must contain valid JSON")
    if not isinstance(payload, dict):
        return _fail("hook envelope must be a JSON object")
    if payload.get("hook_event_name") != "PreToolUse":
        return _fail("hook_event_name must be PreToolUse")
    if payload.get("tool_name") != "Bash":
        return _fail("tool_name must be Bash")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return _fail("tool_input must be a JSON object")
    command = tool_input.get("command")
    if not isinstance(command, str):
        return _fail("tool_input.command must be a string")

    try:
        syntax = subprocess.run(
            ["bash", "-n", "-s"],
            input=command,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _fail("tool_input.command syntax could not be checked")
    if syntax.returncode != 0:
        return _fail("tool_input.command has invalid Bash syntax")

    try:
        tokens = _literal_tokens(command)
    except ValueError:
        return _fail("tool_input.command is not valid shell text")
    for index, word in enumerate(tokens):
        if word == "git" and _is_force_push(_git_candidate(tokens, index)):
            json.dump(_DENIAL, sys.stdout)
            sys.stdout.write("\n")
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
