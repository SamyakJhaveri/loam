#!/usr/bin/env python3
"""Codex PreToolUse policy hook for this project.

This replaces direct reuse of Claude Code hook scripts. It accepts the Codex hook
JSON payload on stdin and enforces the repo's blocking policies for Bash,
Write/Edit-style file tools, and apply_patch.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


MAX_SENTINEL_AGE_SECONDS = 1800
REQUIRED_CONFIG_FIELDS = {
    "schema_version",
    "experiment_name",
    "spec_version",
    "timestamp",
    "git_commit",
    "config_hash",
    "seed",
}


def project_root() -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL
        )
        return Path(out.strip())
    except Exception:
        return Path.cwd()


ROOT = project_root()
CWD = Path.cwd()
GIT_VALUE_OPTIONS = {
    "-C",
    "-c",
    "--config-env",
    "--exec-path",
    "--git-dir",
    "--namespace",
    "--super-prefix",
    "--work-tree",
}


def load_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def tool_input(payload: dict) -> dict:
    value = payload.get("tool_input", payload.get("input", payload))
    return value if isinstance(value, dict) else {}


def tool_name(payload: dict) -> str:
    name = payload.get("tool_name") or payload.get("tool") or payload.get("name") or ""
    return str(name)


def fail(title: str, detail: str) -> None:
    print("", file=sys.stderr)
    print(f"BLOCKED: {title}", file=sys.stderr)
    print(f"  {detail}", file=sys.stderr)
    print("", file=sys.stderr)
    raise SystemExit(2)


def split_command(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


SEGMENT_SPLIT_RE = re.compile(r"\|\||&&|[;|&\n]")
REDIRECT_OPERATORS = {">", ">>", "<", "&>", "&>>", ">|", "<>", ">&", "<&"}
WRAPPER_COMMANDS = {
    "env", "nice", "nohup", "time", "command", "builtin", "exec",
    "sudo", "stdbuf", "setsid", "timeout", "xargs", "then", "do", "ifne",
}
FILE_ACCESS_VERBS = {
    "cat", "bat", "tac", "nl", "less", "more", "head", "tail", "grep", "egrep",
    "fgrep", "rg", "ag", "awk", "sed", "cut", "sort", "uniq", "xxd", "od",
    "hexdump", "strings", "source", ".", "tee", "dd", "cp", "mv", "scp", "rsync",
    "install", "ln", "vim", "vi", "nano", "emacs", "open", "wc", "base64",
    "md5", "md5sum", "shasum", "sha256sum", "truncate", "shred", "gzip",
    "gunzip", "zip", "unzip", "xz", "bzip2", "python", "python3", "node",
    "perl", "ruby", "jq", "yq",
}
RESULT_WRITE_VERBS = {
    "rm", "mv", "cp", "tee", "truncate", "shred", "dd", "install", "ln",
    "gzip", "gunzip", "zip", "xz", "bzip2", "sed", "touch", "chmod",
    "chown", "chgrp", "mkdir", "rsync", "scp", "python", "python3", "node",
    "perl", "ruby",
}
INTERPRETER_VERBS = {"python", "python3", "node", "perl", "ruby"}
SENTINEL_WRITE_VERBS = {
    "touch", "tee", "mv", "cp", "rm", "truncate", "shred", "sed", "ln",
    "python", "python3", "node", "perl", "ruby",
}
GIT_MERGE_EXIT_FLAGS = {"--abort", "--quit"}
GIT_NON_COMMIT_SEQUENCER_FLAGS = {"--abort", "--quit", "--no-commit", "-n"}
GIT_INDEX_WRITING_SUBCOMMANDS = {
    "add",
    "am",
    "apply",
    "checkout",
    "cherry-pick",
    "commit",
    "merge",
    "mv",
    "pull",
    "rebase",
    "reset",
    "restore",
    "revert",
    "rm",
    "stash",
    "switch",
}
INDEX_LOCK_FRESH_SECONDS = 30


def shell_tokens(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return split_command(command)


def redirect_targets(command: str) -> list[str]:
    """Paths that appear as the target/source of a shell redirect (`>`, `>>`, `<`)."""
    targets: list[str] = []
    tokens = shell_tokens(command)
    for index, token in enumerate(tokens[:-1]):
        if token in REDIRECT_OPERATORS:
            target = tokens[index + 1]
            if target and not target.startswith("&"):
                targets.append(target)
    return targets


def operand_candidates(token: str) -> list[str]:
    """A token plus, for `key=value` forms (e.g. `dd of=path`), the value half."""
    candidates = [token]
    if "=" in token:
        candidates.append(token.split("=", 1)[1])
    return candidates


def command_segments(command: str) -> list[tuple[str, list[str]]]:
    """Split a command into (verb, operands) per pipeline segment.

    Leading `VAR=value` assignments and benign wrappers (env, sudo, xargs, ...)
    are skipped so the *acting* verb is identified. Redirect operators are not
    returned as operands; use redirect_targets() for those. Shell-wrapped scripts
    (`bash -c '...'`) are handled by the callers via shell_script_from_argv().
    """
    segments: list[tuple[str, list[str]]] = []
    for raw in SEGMENT_SPLIT_RE.split(command):
        tokens = shell_tokens(raw)
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
                index += 1
                continue
            if Path(token).name in WRAPPER_COMMANDS:
                index += 1
                continue
            break
        if index >= len(tokens):
            continue
        verb = Path(tokens[index]).name
        operands = []
        skip_next = False
        for token in tokens[index + 1 :]:
            if skip_next:
                skip_next = False
                continue
            if token in REDIRECT_OPERATORS:
                skip_next = True
                continue
            operands.append(token)
        segments.append((verb, operands))
    return segments


def resolve_user_path(path: str) -> Path:
    p = Path(path.strip())
    return (p if p.is_absolute() else CWD / p).resolve(strict=False)


def rel_path(path: str) -> str:
    if not path:
        return ""
    try:
        resolved = resolve_user_path(path)
        path = str(resolved.relative_to(ROOT.resolve()))
    except Exception:
        path = path.strip()
    path = path.replace("\\", "/")
    return path[2:] if path.startswith("./") else path


def rel_git_path(path: str) -> str:
    path = path.strip().replace("\\", "/")
    return path[2:] if path.startswith("./") else path


def path_exists(path: str) -> bool:
    return bool(path) and resolve_user_path(path).exists()


def is_results_json(path: str) -> bool:
    return bool(re.match(r"^results/.+\.json$", rel_path(path)))


def is_results_json_git_path(path: str) -> bool:
    return bool(re.match(r"^results/.+\.json$", rel_git_path(path)))


def is_env_path(path: str) -> bool:
    # Match .env, .env.<x>, .envrc, .envrc.<x> — but NOT .environment / .envoy.
    return any(
        re.fullmatch(r"\.env(\.[^/]*)?|\.envrc(\.[^/]*)?", part)
        for part in Path(rel_path(path)).parts
    )


def is_superpowers_docs(path: str) -> bool:
    return rel_path(path).startswith("docs/superpowers/")


def is_experiment_config(path: str) -> bool:
    return bool(re.match(r"^experiments/runs/[^/]+/config\.json$", rel_path(path)))


def parse_patch(patch: str) -> list[tuple[str, str, str]]:
    """Return (operation, path, added_content) entries from an apply_patch body."""
    entries: list[tuple[str, str, str]] = []
    current_op: str | None = None
    current_path: str | None = None
    added: list[str] = []

    def flush() -> None:
        nonlocal current_op, current_path, added
        if current_op and current_path:
            entries.append((current_op, current_path, "\n".join(added)))
        current_op = None
        current_path = None
        added = []

    for line in patch.splitlines():
        match = re.match(r"^\*\*\* (Add|Update|Delete) File: (.+)$", line)
        if match:
            flush()
            current_op = match.group(1).lower()
            current_path = match.group(2).strip()
            continue
        move = re.match(r"^\*\*\* Move to: (.+)$", line)
        if move:
            flush()
            current_op = "move-to"
            current_path = move.group(1).strip()
            continue
        if current_op == "add" and line.startswith("+"):
            added.append(line[1:])

    flush()
    return entries


def validate_experiment_config(path: str, content: str) -> None:
    if path_exists(path):
        fail(
            "config.json already exists.",
            f"Experiment runs are immutable. Create a new run instead of overwriting {path}.",
        )
    try:
        config = json.loads(content)
    except json.JSONDecodeError:
        fail("config.json is not valid JSON.", path)

    missing = sorted(REQUIRED_CONFIG_FIELDS - set(config))
    if missing:
        fail("config.json is missing required fields.", f"{path}: {missing}")

    if not isinstance(config.get("schema_version"), int) or config["schema_version"] < 1:
        fail("schema_version must be a positive integer.", path)
    if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", str(config["timestamp"])):
        fail("timestamp must be ISO 8601 format.", path)
    if not re.match(r"^[0-9a-f]{7,}$", str(config["git_commit"])):
        fail("git_commit must be a hex string with at least 7 characters.", path)
    if not re.match(r"^v\d+$", str(config["spec_version"])):
        fail("spec_version must match v<N>, for example v1.", path)


def parse_git_invocation(argv: list[str]) -> tuple[str, list[str]] | None:
    if not argv or argv[0] != "git":
        return None

    index = 1
    while index < len(argv):
        arg = argv[index]
        if arg in GIT_VALUE_OPTIONS:
            index += 2
            continue
        if any(arg.startswith(f"{option}=") for option in GIT_VALUE_OPTIONS if option.startswith("--")):
            index += 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        return arg, argv[index + 1 :]

    return None


def shell_script_from_argv(argv: list[str]) -> str | None:
    if not argv:
        return None
    if Path(argv[0]).name not in {"bash", "sh", "zsh"}:
        return None

    index = 1
    while index < len(argv):
        arg = argv[index]
        if arg == "--":
            index += 1
            continue
        if arg == "-c" or (arg.startswith("-") and "c" in arg[1:]):
            return argv[index + 1] if index + 1 < len(argv) else None
        index += 1

    return None


def git_subcommands(command: str) -> list[tuple[str, list[str]]]:
    argv = split_command(command)
    found: list[tuple[str, list[str]]] = []

    script = shell_script_from_argv(argv)
    if script:
        found.extend(git_subcommands(script))

    for index, arg in enumerate(argv):
        if arg != "git":
            continue
        parsed = parse_git_invocation(argv[index:])
        if parsed:
            found.append(parsed)

    return found


def git_index_lock() -> Path | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--absolute-git-dir"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        return None
    git_dir = out.strip()
    return Path(git_dir) / "index.lock" if git_dir else None


def check_concurrent_index_lock(tool: str, command: str = "") -> None:
    lock = git_index_lock()
    if lock is None or not lock.exists():
        return

    if tool == "Bash":
        if not any(
            subcommand in GIT_INDEX_WRITING_SUBCOMMANDS
            for subcommand, _args in git_subcommands(command)
        ):
            return
    elif tool not in {"Edit", "Write", "apply_patch"}:
        return

    age = int(datetime.now(timezone.utc).timestamp() - lock.stat().st_mtime)
    if age < INDEX_LOCK_FRESH_SECONDS:
        fail(
            "another writer holds this checkout's git index.",
            f"Wait for the other session to finish, then retry. Lock: {lock} (age {age}s)",
        )

    print(
        f"NOTE: stale git index.lock found (age {age}s) — likely a crashed git process, not a live race.",
        file=sys.stderr,
    )


def git_subcommand_creates_commit(subcommand: str, args: list[str]) -> bool:
    if subcommand == "commit":
        return True
    if subcommand == "merge":
        if any(arg in GIT_MERGE_EXIT_FLAGS for arg in args):
            return False
        creates_commit = True
        for arg in args:
            if arg == "--no-commit":
                creates_commit = False
            elif arg == "--commit":
                creates_commit = True
            elif arg == "--squash":
                creates_commit = False
            elif arg == "--no-squash":
                creates_commit = True
            elif arg == "--ff-only":
                creates_commit = False
            elif arg in {"--ff", "--no-ff"}:
                creates_commit = True
        return creates_commit
    if subcommand in {"cherry-pick", "revert"}:
        return not any(arg in GIT_NON_COMMIT_SEQUENCER_FLAGS for arg in args)
    return False


def validation_sentinel() -> Path:
    override = os.environ.get("CODEX_VALIDATION_SENTINEL")
    return Path(override) if override else ROOT / ".validation_passed"


def diff_has_result_mutation() -> str | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(ROOT), "diff", "--name-status", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        paths = [rel_git_path(part) for part in parts[1:]]
        if any(is_results_json_git_path(path) for path in paths) and not status.startswith("A"):
            return line
    return None


def validate_commit_gate(command: str) -> None:
    if not any(git_subcommand_creates_commit(subcommand, args) for subcommand, args in git_subcommands(command)):
        return

    result_mutation = diff_has_result_mutation()
    if result_mutation:
        fail(
            "Existing result JSON files changed.",
            f"Result files are immutable; review this diff entry before committing: {result_mutation}",
        )

    sentinel = validation_sentinel()
    if not sentinel.exists():
        fail(
            "Post-session validation has not been run.",
            "Run full /validate before committing.",
        )

    age = int(datetime.now(timezone.utc).timestamp() - sentinel.stat().st_mtime)
    if age > MAX_SENTINEL_AGE_SECONDS:
        fail(
            "Validation sentinel is stale.",
            f"Age {age}s exceeds {MAX_SENTINEL_AGE_SECONDS}s; re-run /validate.",
        )

    waves: int | None = None
    for line in sentinel.read_text(errors="replace").splitlines():
        if line.startswith("waves_passed="):
            try:
                waves = int(line.split("=", 1)[1].strip())
            except ValueError:
                fail("Validation sentinel has malformed waves_passed.", "Run full /validate again.")
    if waves is None:
        fail("Validation sentinel is missing waves_passed.", "Run full /validate again.")
    if waves < 2:
        fail("Only part of validation passed.", "Run full /validate before committing.")

    changed = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", "HEAD"],
        text=True,
        stderr=subprocess.DEVNULL,
    ).splitlines()
    newest = 0.0
    for file_name in changed:
        path = ROOT / file_name
        if path.is_file():
            newest = max(newest, path.stat().st_mtime)
    if newest > sentinel.stat().st_mtime:
        fail("Files changed after validation passed.", "Re-run /validate.")

    print(
        f"Validation sentinel OK (age: {age}s, max: {MAX_SENTINEL_AGE_SECONDS}s).",
        file=sys.stderr,
    )


def audit_bash(command: str) -> None:
    if os.environ.get("CODEX_HOOK_AUDIT") != "1":
        return
    if not command:
        return
    log_path = Path(
        os.environ.get("CODEX_HOOK_AUDIT_LOG", str(Path.home() / ".codex" / "codex-audit.log"))
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} | {command}\n")


def is_force_push(command: str) -> bool:
    for subcommand, push_args in git_subcommands(command):
        if subcommand != "push":
            continue
        for arg in push_args:
            if arg.startswith("+"):
                return True
            if arg in {"--force", "--force-with-lease", "-f"}:
                return True
            if arg.startswith("--force=") or arg.startswith("--force-with-lease="):
                return True
            if re.match(r"^-[A-Za-z]*f[A-Za-z]*$", arg):
                return True
    return False


def _is_sentinel_path(path: str) -> bool:
    relative = rel_path(path)
    if relative in {".validation_passed", rel_path(str(validation_sentinel()))}:
        return True
    return Path(relative).name == ".validation_passed"


def mutates_validation_sentinel(command: str) -> bool:
    script = shell_script_from_argv(split_command(command))
    if script and mutates_validation_sentinel(script):
        return True
    if any(_is_sentinel_path(target) for target in redirect_targets(command)):
        return True
    for verb, operands in command_segments(command):
        if verb not in SENTINEL_WRITE_VERBS:
            continue
        for operand in operands:
            if any(_is_sentinel_path(candidate) for candidate in operand_candidates(operand)):
                return True
    return False


def _under_results(path: str) -> bool:
    relative = rel_path(path)
    return relative == "results" or relative.startswith("results/")


def mutates_results(command: str) -> bool:
    script = shell_script_from_argv(split_command(command))
    if script and mutates_results(script):
        return True
    # A redirect whose target lands under results/ overwrites or appends a result.
    if any(is_results_json(target) or _under_results(target) for target in redirect_targets(command)):
        return True
    for verb, operands in command_segments(command):
        # Interpreters embed the path inside a code string; fall back to a scan.
        if verb in INTERPRETER_VERBS and re.search(r"(?:\./)?results/[^\s'\"]*\.json", command):
            return True
        if verb == "find" and "-delete" in operands and any(_under_results(o) for o in operands):
            return True
        if verb == "sed" and any(o == "-i" or o.startswith("-i") for o in operands):
            if any(_under_results(c) for o in operands for c in operand_candidates(o)):
                return True
        if verb in RESULT_WRITE_VERBS:
            for operand in operands:
                if any(_under_results(candidate) for candidate in operand_candidates(operand)):
                    return True
    return False


def references_env_file(command: str) -> bool:
    if ".env" not in command:
        return False

    script = shell_script_from_argv(split_command(command))
    if script and references_env_file(script):
        return True

    # A redirect that reads from or writes to an env file (e.g. `> .env`, `< .env`).
    if any(is_env_path(target) for target in redirect_targets(command)):
        return True

    # An env file passed as an operand to a file-reading/writing verb (e.g. `cat .env`).
    # Bare mentions in non-file verbs (`echo`, `git commit -m "... .env ..."`) are allowed.
    for verb, operands in command_segments(command):
        if verb not in FILE_ACCESS_VERBS:
            continue
        for operand in operands:
            if any(is_env_path(candidate) for candidate in operand_candidates(operand)):
                return True
    return False


def check_bash(command: str) -> None:
    audit_bash(command)
    validate_commit_gate(command)
    if is_force_push(command):
        fail("Force pushes are blocked.", "Use a normal push or ask for a reviewed recovery plan.")
    if references_env_file(command):
        fail("Cannot access .env files via Bash.", "Use non-secret examples or ask the user for a safe path.")
    if mutates_validation_sentinel(command):
        fail("Cannot modify validation sentinel via Bash.", "Run /validate to create the sentinel.")
    if mutates_results(command):
        fail("Cannot mutate files under results/ via Bash.", "Result files are immutable.")


def check_paths(paths: list[str]) -> None:
    for path in paths:
        if is_env_path(path):
            fail("Cannot access .env files.", "Environment files may contain secrets.")
        if is_superpowers_docs(path):
            suggested = rel_path(path).replace("docs/superpowers/", ".superpowers/", 1)
            fail(
                "superpowers plans/specs belong under .superpowers/.",
                f"Re-issue the write to {suggested}.",
            )
        if is_results_json(path) and path_exists(path):
            fail("Cannot overwrite existing result JSON.", path)


def check_apply_patch(patch: str) -> None:
    for operation, path, content in parse_patch(patch):
        check_paths([path])
        if is_results_json(path) and operation in {"update", "delete", "move-to"}:
            fail("Cannot modify existing result JSON via apply_patch.", path)
        if is_experiment_config(path):
            if operation != "add":
                fail("Experiment config files are immutable.", path)
            validate_experiment_config(path, content)


def main() -> int:
    payload = load_payload()
    inputs = tool_input(payload)
    name = tool_name(payload)

    command = str(inputs.get("command", ""))
    check_concurrent_index_lock(name, command)

    if name == "Bash" or command:
        check_bash(command)

    path = rel_path(str(inputs.get("file_path") or inputs.get("path") or ""))
    if path:
        check_paths([path])
        if is_experiment_config(path):
            validate_experiment_config(path, str(inputs.get("content", "")))

    patch = str(inputs.get("patch") or payload.get("patch") or "")
    if name == "apply_patch" or patch:
        check_apply_patch(patch)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
