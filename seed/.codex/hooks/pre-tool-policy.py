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
_PUSH_LONG_OPTIONS = {
    "--all",
    "--atomic",
    "--branches",
    "--delete",
    "--dry-run",
    "--exec",
    "--follow-tags",
    "--force",
    "--force-if-includes",
    "--force-with-lease",
    "--help",
    "--ipv4",
    "--ipv6",
    "--mirror",
    "--no-all",
    "--no-atomic",
    "--no-branches",
    "--no-delete",
    "--no-dry-run",
    "--no-exec",
    "--no-follow-tags",
    "--no-force",
    "--no-force-if-includes",
    "--no-force-with-lease",
    "--no-mirror",
    "--no-porcelain",
    "--no-progress",
    "--no-prune",
    "--no-push-option",
    "--no-quiet",
    "--no-receive-pack",
    "--no-recurse-submodules",
    "--no-repo",
    "--no-set-upstream",
    "--no-signed",
    "--no-tags",
    "--no-thin",
    "--no-verbose",
    "--no-verify",
    "--porcelain",
    "--progress",
    "--prune",
    "--push-option",
    "--quiet",
    "--receive-pack",
    "--recurse-submodules",
    "--repo",
    "--set-upstream",
    "--signed",
    "--tags",
    "--thin",
    "--verbose",
    "--verify",
}
_PUSH_LONG_WITH_ARGUMENT = {
    "--exec",
    "--push-option",
    "--receive-pack",
    "--repo",
}


def _fail(reason: str) -> int:
    print(f"pre-tool-policy: {reason}", file=sys.stderr)
    return 2


def _without_shell_comments(command: str) -> str:
    uncommented: list[str] = []
    quote: str | None = None
    word_started = False
    index = 0
    while index < len(command):
        character = command[index]
        if quote == "'":
            uncommented.append(character)
            if character == "'":
                quote = None
            index += 1
            continue
        if quote == '"':
            uncommented.append(character)
            if character == '"':
                quote = None
            elif character == "\\" and index + 1 < len(command):
                uncommented.append(command[index + 1])
                index += 1
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            word_started = True
            uncommented.append(character)
            index += 1
            continue
        if character == "\\" and index + 1 < len(command):
            word_started = True
            uncommented.extend((character, command[index + 1]))
            index += 2
            continue
        if character == "#" and not word_started:
            while index < len(command) and command[index] != "\n":
                index += 1
            continue
        uncommented.append(character)
        if character in " \t\n;&|()<>":
            word_started = False
        else:
            word_started = True
        index += 1
    return "".join(uncommented)


def _normalize_line_continuations(command: str) -> str:
    normalized: list[str] = []
    quote: str | None = None
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
        normalized.append(character)
        if quote == "'":
            if character == "'":
                quote = None
        elif quote == '"':
            if character == '"':
                quote = None
            elif character == "\\" and index + 1 < len(command):
                normalized.append(command[index + 1])
                index += 1
        elif character in {"'", '"'}:
            quote = character
        elif character == "\\" and index + 1 < len(command):
            normalized.append(command[index + 1])
            index += 1
        index += 1
    return "".join(normalized)


def _literal_tokens(command: str) -> tuple[str, ...]:
    normalized = _normalize_line_continuations(command)
    lexer = shlex.shlex(
        _without_shell_comments(normalized),
        posix=True,
        punctuation_chars=";&|(){}<>\n",
    )
    lexer.commenters = ""
    lexer.whitespace = " \t"
    lexer.whitespace_split = True
    return tuple(lexer)


def _git_candidate(tokens: tuple[str, ...], start: int) -> tuple[str, ...]:
    candidate: list[str] = []
    for word in tokens[start:]:
        if candidate and word and set(word) <= _COMMAND_BOUNDARY:
            break
        candidate.append(word)
    return tuple(candidate)


def _push_arguments(words: tuple[str, ...]) -> tuple[str, ...] | None:
    if not words or words[0] != "git":
        return None
    remaining = list(words[1:])
    index = 0
    while index < len(remaining):
        word = remaining[index]
        operator_index = index + 1 if word.isdigit() else index
        operator = (
            remaining[operator_index]
            if operator_index < len(remaining)
            else ""
        )
        redirection = (
            bool(operator)
            and set(operator) <= {"<", ">", "&", "|"}
            and bool(set(operator) & {"<", ">"})
        )
        if redirection:
            index = operator_index + 1
            if operator == "<<" and index < len(remaining):
                if remaining[index] == "-":
                    index += 1
            if index >= len(remaining):
                return None
            index += 1
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


def _canonical_push_option(word: str) -> tuple[str, bool] | None:
    name, separator, _ = word.partition("=")
    if name in _PUSH_LONG_OPTIONS:
        return name, bool(separator)
    matches = [option for option in _PUSH_LONG_OPTIONS if option.startswith(name)]
    if len(matches) == 1:
        return matches[0], bool(separator)
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
            canonical, assigned = option
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
            if canonical in _PUSH_LONG_WITH_ARGUMENT:
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
