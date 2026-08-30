#!/usr/bin/env python3
"""Block literal force-push commands before Codex runs Bash."""

from __future__ import annotations

import json
import re
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
_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)
_PROTECTED_PUNCTUATION = {
    ";": "\ue000",
    "&": "\ue001",
    "|": "\ue002",
    "\n": "\ue003",
    "#": "\ue004",
    "{": "\ue005",
    "}": "\ue006",
    "(": "\ue007",
    ")": "\ue008",
}
_RESTORED_PUNCTUATION = {
    protected: literal for literal, protected in _PROTECTED_PUNCTUATION.items()
}
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


def _protect_quoted_punctuation(command: str) -> str:
    if any(marker in command for marker in _RESTORED_PUNCTUATION):
        raise ValueError("command contains reserved parser characters")
    protected: list[str] = []
    quote: str | None = None
    comment = False
    word_started = False
    index = 0
    while index < len(command):
        character = command[index]
        if comment:
            protected.append(character)
            if character == "\n":
                comment = False
                word_started = False
                protected.append(";")
            index += 1
            continue
        if quote == "'":
            if character == "'":
                quote = None
                protected.append(character)
            else:
                protected.append(_PROTECTED_PUNCTUATION.get(character, character))
            index += 1
            continue
        if quote == '"':
            if character == '"':
                quote = None
                protected.append(character)
            elif character == "\\" and index + 1 < len(command):
                escaped = command[index + 1]
                protected.append(character)
                protected.append(
                    _PROTECTED_PUNCTUATION.get(escaped, escaped)
                )
                index += 1
            else:
                protected.append(_PROTECTED_PUNCTUATION.get(character, character))
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            word_started = True
            protected.append(character)
            index += 1
            continue
        if character == "#":
            if word_started:
                protected.append(_PROTECTED_PUNCTUATION[character])
            else:
                comment = True
                protected.append(character)
            index += 1
            continue
        if character == "\\" and index + 1 < len(command):
            escaped = command[index + 1]
            if escaped in _PROTECTED_PUNCTUATION:
                protected.append(_PROTECTED_PUNCTUATION[escaped])
            else:
                protected.extend((character, escaped))
            word_started = True
            index += 2
            continue
        protected.append(character)
        if character in " \t;&|\n":
            word_started = False
        else:
            word_started = True
        index += 1
    return "".join(protected)


def _segments(command: str) -> tuple[tuple[str, ...], ...]:
    normalized = command.replace("\\\r\n", "").replace("\\\n", "")
    protected = _protect_quoted_punctuation(normalized)
    lexer = shlex.shlex(protected, posix=True, punctuation_chars=";&|")
    lexer.commenters = "#"
    lexer.whitespace = " \t"
    lexer.wordchars += "+" + "".join(_RESTORED_PUNCTUATION)
    tokens = tuple(lexer)
    segments: list[tuple[str, ...]] = []
    current: list[str] = []
    for token in tokens:
        if token == "\n" or (token and set(token) <= set(";&|")):
            if current:
                segments.append(tuple(current))
                current = []
        else:
            current.append(token)
    if current:
        segments.append(tuple(current))
    return tuple(
        tuple(
            "".join(_RESTORED_PUNCTUATION.get(char, char) for char in token)
            for token in segment
        )
        for segment in _top_level_segments(tuple(segments))
    )


def _function_body_start(segment: tuple[str, ...]) -> int | None:
    if (
        len(segment) >= 4
        and segment[1:4] == ("(", ")", "{")
    ):
        return 3
    if len(segment) < 3 or segment[0] != "function":
        return None
    if segment[2] == "{":
        return 2
    if len(segment) >= 5 and segment[2:5] == ("(", ")", "{"):
        return 4
    return None


def _function_header_waits_for_body(segment: tuple[str, ...]) -> bool:
    return (
        len(segment) == 3
        and segment[1:] == ("(", ")")
    ) or (
        segment[:1] == ("function",)
        and (len(segment) == 2 or segment[2:] == ("(", ")"))
    )


def _top_level_segments(
    segments: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    top_level: list[tuple[str, ...]] = []
    function_depth = 0
    waiting_for_body = False
    for segment in segments:
        if function_depth:
            function_depth += segment.count("{") - segment.count("}")
            function_depth = max(function_depth, 0)
            continue
        if waiting_for_body:
            waiting_for_body = False
            function_depth = max(segment.count("{") - segment.count("}"), 0)
            continue
        body_start = _function_body_start(segment)
        if body_start is not None:
            body = segment[body_start:]
            function_depth = max(body.count("{") - body.count("}"), 0)
            continue
        if _function_header_waits_for_body(segment):
            waiting_for_body = True
            continue
        top_level.append(segment)
    return tuple(top_level)


def _strip_assignments(words: list[str]) -> None:
    while words and _ASSIGNMENT.fullmatch(words[0]):
        words.pop(0)


def _strip_literal_prefixes_and_wrappers(words: tuple[str, ...]) -> list[str]:
    remaining = list(words)
    prefixes = {"!", "if", "elif", "while", "until", "then", "do", "else"}
    while remaining:
        if remaining[0] in prefixes:
            remaining.pop(0)
            continue
        if remaining[0] == "time":
            remaining.pop(0)
            if remaining and remaining[0] == "-p":
                remaining.pop(0)
            if remaining and remaining[0] == "--":
                remaining.pop(0)
            continue
        break
    _strip_assignments(remaining)

    if remaining and remaining[0] == "command":
        remaining.pop(0)
        if remaining and remaining[0] == "--":
            remaining.pop(0)
        _strip_assignments(remaining)

    if remaining and remaining[0] in {"env", "/usr/bin/env"}:
        remaining.pop(0)
        while remaining:
            word = remaining[0]
            if word == "--":
                remaining.pop(0)
                break
            if word in {"-i", "--ignore-environment"}:
                remaining.pop(0)
                continue
            if word in {"-u", "--unset"}:
                if len(remaining) < 2:
                    return []
                del remaining[:2]
                continue
            if word.startswith("--unset=") or _ASSIGNMENT.fullmatch(word):
                remaining.pop(0)
                continue
            break
        _strip_assignments(remaining)

    return remaining


def _push_arguments(words: tuple[str, ...]) -> tuple[str, ...] | None:
    remaining = _strip_literal_prefixes_and_wrappers(words)
    if not remaining or remaining.pop(0) != "git":
        return None

    index = 0
    while index < len(remaining):
        word = remaining[index]
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
        segments = _segments(command)
    except ValueError:
        return _fail("tool_input.command is not valid shell text")
    if any(_is_force_push(segment) for segment in segments):
        json.dump(_DENIAL, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
