#!/usr/bin/env python3
"""Block recognizable literal force-push commands before Codex runs Bash.

Also deny apply_patch envelopes that touch .env secrets, sealed run results, or
generated outputs.
"""

from __future__ import annotations

import json
import posixpath
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
# apply_patch deny families, checked in this order. Each entry is a
# (name, reason) pair; the reason is the permissionDecisionReason returned when a
# patched path matches the family. Kept as one literal tuple; the rendered
# harness contract probes each family with a fixed patch and expects these
# exact reasons.
_PATCH_DENY_FAMILIES = (
    ("secrets", "Patches to .env files are blocked by repository policy."),
    ("sealed", "Patches to sealed run results are blocked by repository policy."),
    ("generated", "Patches to generated outputs are blocked by repository policy."),
)
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
    "--attr-source",
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
    nul_terminated = False
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
        if nul_terminated:
            index += 2 if character == "\\" and index + 1 < len(command) else 1
            continue
        if character != "\\" or index + 1 >= len(command):
            decoded.append(character)
            index += 1
            continue
        escaped = command[index + 1]
        if escaped in escapes:
            decoded.append(escapes[escaped])
            index += 2
            continue
        if escaped == "c" and index + 2 < len(command):
            control_character = command[index + 2]
            control_byte = control_character.encode("utf-8")[0]
            if control_byte & 0x1F == 0:
                nul_terminated = True
                index += 3
                continue
            if not control_character.isascii():
                decoded.append(_OPAQUE_ANSI_C_CHARACTER)
                index += 3
                continue
        if escaped in "01234567":
            end = index + 2
            while end < min(index + 4, len(command)):
                if command[end] not in "01234567":
                    break
                end += 1
            value = int(command[index + 1 : end], 8) & 0xFF
            if value == 0:
                nul_terminated = True
            else:
                decoded.append(chr(value))
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
                if codepoint == 0:
                    nul_terminated = True
                else:
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
    command = command.replace("\0", "")
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


def _substitution_bodies(command: str) -> tuple[str, ...]:
    """Extract command/process-substitution bodies that Bash would execute.

    Single-quoted text never expands, so it is skipped. Double-quoted text
    expands `$(...)` and backticks, so those are extracted. `<(...)`/`>(...)`
    only work unquoted. `$((...))` is arithmetic, not a substitution.
    """
    bodies: list[str] = []
    quote: str | None = None
    index = 0
    length = len(command)
    while index < length:
        character = command[index]
        if quote == "'":
            if character == "'":
                quote = None
            index += 1
            continue
        if character == "\\" and index + 1 < length:
            index += 2
            continue
        if character == '"':
            quote = None if quote == '"' else '"'
            index += 1
            continue
        if character == "'":
            quote = "'"
            index += 1
            continue
        if character == "`":
            end = index + 1
            body: list[str] = []
            while end < length and command[end] != "`":
                if command[end] == "\\" and end + 1 < length:
                    body.append(command[end + 1])
                    end += 2
                    continue
                body.append(command[end])
                end += 1
            bodies.append("".join(body))
            index = end + 1
            continue
        opener: int | None = None
        if command.startswith("$(", index) and not command.startswith(
            "$((", index
        ):
            opener = index + 2
        elif quote is None and (
            command.startswith("<(", index)
            or command.startswith(">(", index)
        ):
            opener = index + 2
        if opener is not None:
            depth = 1
            end = opener
            inner_quote: str | None = None
            while end < length and depth:
                inner = command[end]
                if inner_quote == "'":
                    if inner == "'":
                        inner_quote = None
                elif inner == "\\" and end + 1 < length:
                    end += 1
                elif inner_quote == '"':
                    if inner == '"':
                        inner_quote = None
                elif inner in {"'", '"'}:
                    inner_quote = inner
                elif inner == "(":
                    depth += 1
                elif inner == ")":
                    depth -= 1
                end += 1
            bodies.append(command[opener : end - 1 if depth == 0 else end])
            index = end
            continue
        index += 1
    return tuple(bodies)


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
        # Unrecognized OPTION before `push`. Fail safe for a deny policy: an
        # unknown leading global (e.g. `--no-literal-pathspecs`, or any `--opt=val`
        # form) must not make the command invisible. Skip it and keep scanning so
        # a force flag cannot hide behind it. A non-option token here is a real
        # subcommand (help, config, log), so it is genuinely not a push.
        if word.startswith("-"):
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
    mirror = False
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
            elif canonical == "--mirror":
                mirror = True
            elif canonical == "--no-mirror":
                mirror = False
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
    return not dry_run and (force or force_with_lease or mirror or plus_refspec)


_SHELL_INTERPRETERS = {"sh", "bash", "dash", "zsh", "ksh"}
_SEGMENT_OPERATORS = set(";&|\n")
_GROUPING_TOKENS = {"(", "{"}
_RECURSION_LIMIT = 10


def _segments(tokens: tuple[str, ...]) -> list[list[str]]:
    """Split a token stream into command segments on `;`, `&`, `|`, and
    newline only. Grouping tokens `(){}` stay inside a segment - they are
    either subshell grouping or the shattered pieces of a `${...}`/`$(...)`
    head, which the head parser reassembles."""
    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token and set(token) <= _SEGMENT_OPERATORS:
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    return segments


_WRAPPER_COMMANDS = {"command", "env", "nice", "nohup", "setsid", "ionice"}


def _resolve_head(segment: list[str]) -> tuple[str, str, list[str]] | None:
    """Return (kind, head, args) for a command segment, or None if empty.

    kind is one of 'git', 'shell', 'eval', 'opaque', 'other'. 'opaque' marks a
    head whose value cannot be resolved statically - a variable ($NAME/${NAME})
    or a command substitution ($( ) / backtick) - which a deny policy must still
    treat as a possible `git` when `push` follows it. Leading wrapper commands
    (`command`, `env`, ...) and their options are unwrapped so the real head is
    resolved.
    """
    index = 0
    while index < len(segment):
        token = segment[index]
        # Skip grouping tokens, NAME=value assignments, wrapper options.
        if token in _GROUPING_TOKENS:
            index += 1
            continue
        name, separator, _ = token.partition("=")
        if separator and name.isidentifier():
            index += 1
            continue
        # Unwrap a leading wrapper command and its dash-options so the wrapped
        # command's head is resolved (`command ${GIT} push`, `env bash -c ...`).
        if token.rsplit("/", 1)[-1] in _WRAPPER_COMMANDS:
            index += 1
            while index < len(segment) and segment[index].startswith("-") and (
                segment[index] != "-"
            ):
                index += 1
            continue
        break
    if index >= len(segment):
        return None

    token = segment[index]
    # Reassemble a shattered ${ ... } or $( ... ) head into an opaque marker.
    if token == "$" and index + 1 < len(segment) and segment[index + 1] == "{":
        end = index + 2
        while end < len(segment) and segment[end] != "}":
            end += 1
        return "opaque", "${...}", segment[end + 1 :]
    if token == "$" and index + 1 < len(segment) and segment[index + 1] == "(":
        depth = 1
        end = index + 2
        while end < len(segment) and depth:
            if segment[end] == "(":
                depth += 1
            elif segment[end] == ")":
                depth -= 1
            end += 1
        return "opaque", "$(...)", segment[end:]
    # A spaced backtick head (`` `command -v git` push ``) tokenizes with the
    # backticks attached to the first and last words of the substitution.
    if token.startswith("`"):
        end = index
        while end < len(segment) and not segment[end].endswith("`"):
            end += 1
        return "opaque", "`...`", segment[end + 1 :]

    args = segment[index + 1 :]
    if (len(token) > 1 and token[0] == "$") or "`" in token or "$(" in token:
        return "opaque", token, args

    base = token.rsplit("/", 1)[-1]
    if base == "git":
        return "git", token, args
    if base in _SHELL_INTERPRETERS:
        return "shell", token, args
    if base == "eval":
        return "eval", token, args
    return "other", token, args


def _drop_trailing_noise(args: list[str]) -> tuple[str, ...]:
    end = len(args)
    while end and args[end - 1] and set(args[end - 1]) <= (
        _SEGMENT_OPERATORS | {"(", ")", "{", "}"}
    ):
        end -= 1
    return tuple(args[:end])


def _command_denied(command: str, depth: int = 0) -> bool:
    # Fail closed: past the recursion limit the command is too deeply nested
    # (stacked `sh -c`/substitutions) to clear, so a deny policy blocks it.
    if depth > _RECURSION_LIMIT:
        return True
    try:
        tokens = _literal_tokens(command)
    except ValueError:
        return False

    # (a) Conservative literal scan: a visible `git` (or path-prefixed git)
    # token followed by force-push arguments anywhere in the command. This is
    # intentionally broad - it denies force-push token sequences inside `env`
    # prefixes, `case` bodies, and function bodies too.
    for index, word in enumerate(tokens):
        if word.rsplit("/", 1)[-1] == "git" and _is_force_push(
            ("git",) + _git_candidate(tokens, index)[1:]
        ):
            return True

    # (b) Forms where the force push is hidden from the literal scan: an opaque
    # command head, or a string argument executed by a shell interpreter / eval.
    for segment in _segments(tokens):
        resolved = _resolve_head(segment)
        if resolved is None:
            continue
        kind, _head, args = resolved
        clean = _drop_trailing_noise(args)
        # Opaque head ($VAR / ${VAR} / $( ) / backtick) with a literal `push`
        # and a force flag: the head may resolve to git, so block it.
        if (
            kind == "opaque"
            and clean
            and clean[0] == "push"
            and _is_force_push(("git", "push") + clean[1:])
        ):
            return True
        # A shell interpreter executes a string argument as a command
        # (`sh -c '<text>'`, `bash -O extglob -c '<text>'`,
        # `bash -c -- '-x; <text>'`). Recurse into every argument - a leading
        # dash cannot be assumed to be an option, and recursing an actual option
        # is harmless because it contains no force-push sequence.
        if kind == "shell":
            for argument in clean:
                if _command_denied(argument, depth + 1):
                    return True
        if kind == "eval" and clean and _command_denied(
            " ".join(clean), depth + 1
        ):
            return True

    # (c) Command/process substitution bodies execute too.
    return any(
        _command_denied(body, depth + 1)
        for body in _substitution_bodies(command)
    )


_PATCH_PATH_PREFIXES = (
    "*** Add File: ",
    "*** Update File: ",
    "*** Delete File: ",
    "*** Move to: ",
)
_GENERATED_SEGMENTS = {"build", "dist", "htmlcov", "__pycache__", ".pytest_cache"}
_SEALED_ANCESTORS = {"runs", "experiments"}


def _patch_paths(patch: str) -> list[str]:
    """Return normalized target paths declared in an apply_patch envelope."""
    paths: list[str] = []
    for line in patch.splitlines():
        for prefix in _PATCH_PATH_PREFIXES:
            if line.startswith(prefix):
                raw = line[len(prefix) :].rstrip()
                if not raw:
                    break
                normalized = posixpath.normpath(raw)
                if normalized.startswith("./"):
                    normalized = normalized[2:]
                paths.append(normalized)
                break
    return paths


def _is_secret_path(segments: list[str], basename: str) -> bool:
    for segment in segments:
        if segment in {".env", ".envrc"}:
            return True
        if segment.startswith(".env.") or segment.startswith(".envrc."):
            return True
    return basename.startswith(".env")


def _is_sealed_path(segments: list[str]) -> bool:
    for index, segment in enumerate(segments):
        if segment == "results" and any(
            ancestor in _SEALED_ANCESTORS for ancestor in segments[:index]
        ):
            return True
    return False


def _is_generated_path(segments: list[str], basename: str) -> bool:
    for segment in segments:
        if segment in _GENERATED_SEGMENTS or segment.endswith(".egg-info"):
            return True
    return basename == ".coverage"


def _patch_denial_reason(patch: str) -> str | None:
    for path in _patch_paths(patch):
        segments = path.split("/")
        basename = segments[-1]
        if _is_secret_path(segments, basename):
            return _PATCH_DENY_FAMILIES[0][1]
        if _is_sealed_path(segments):
            return _PATCH_DENY_FAMILIES[1][1]
        if _is_generated_path(segments, basename):
            return _PATCH_DENY_FAMILIES[2][1]
    return None


def _patch_denial(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            **_DENIAL["hookSpecificOutput"],
            "permissionDecisionReason": reason,
        }
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeError):
        return _fail("stdin must contain valid JSON")
    if not isinstance(payload, dict):
        return _fail("hook envelope must be a JSON object")
    if payload.get("hook_event_name") != "PreToolUse":
        return _fail("hook_event_name must be PreToolUse")
    tool_name = payload.get("tool_name")
    if tool_name not in {"Bash", "apply_patch"}:
        return _fail("tool_name must be Bash or apply_patch")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return _fail("tool_input must be a JSON object")
    command = tool_input.get("command")
    if not isinstance(command, str):
        return _fail("tool_input.command must be a string")

    if tool_name == "apply_patch":
        reason = _patch_denial_reason(command)
        if reason is not None:
            json.dump(_patch_denial(reason), sys.stdout)
            sys.stdout.write("\n")
        return 0

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
        _literal_tokens(command)
    except ValueError:
        return _fail("tool_input.command is not valid shell text")
    if _command_denied(command):
        json.dump(_DENIAL, sys.stdout)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
