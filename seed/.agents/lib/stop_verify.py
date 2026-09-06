#!/usr/bin/env python3
"""Fast changed-file checks and content-bound local verification evidence.

Transcript evidence is deliberately conservative: simple check commands only,
in the current turn, with no subsequent potential edit. A current validation
receipt can be reused across turns, but never proves remote CI success.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from types import SimpleNamespace


EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch"}
DELEGATE_TOOLS = {"Agent", "Task", "Workflow"}
GOOD = re.compile(r"\b(?:PASS(?:ED)?|OK|success(?:ful)?|exit[ =]0)\b", re.I)
BAD = re.compile(r"\b(?:[1-9]\d* failed|FAIL(?:ED|URE)?|Traceback|error)\b|\bexit[ =][1-9]\d*\b", re.I)
SUBJECT = r"(?:tests?|checks?|suite|build|validation|pytest|ruff)"
SUCCESS = r"(?:pass(?:ed|es)?|succeed(?:ed|s)?|successful|green|verified)"


def claim_kind(message):
    if not isinstance(message, str) or "not verified" in message.lower():
        return None
    remote = False
    local = False
    for sentence in re.split(r"[.!?;\n]|\band\b", message, flags=re.I):
        if re.search(r"\b(?:CI|GitHub Actions|remote checks)\b", sentence, re.I):
            remote |= bool(re.search(r"\b" + SUCCESS + r"\b", sentence, re.I))
        elif re.search(r"\b" + SUBJECT + r"\b.*\b" + SUCCESS + r"\b|\b"
                       + SUCCESS + r"\b.*\b" + SUBJECT + r"\b", sentence, re.I):
            local = True
    return "both" if remote and local else "remote" if remote else "local" if local else None


def command_kind(command):
    """Classify single invocations without executing or trusting printed text."""
    if not isinstance(command, str) or any(c in command for c in "\n`$"):
        return None
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        return None
    if not words or any(w and all(c in ";&|()<>" for c in w) for w in words):
        return None
    if any(w in {"--version", "-V", "--help", "-h", "--collect-only", "--co",
                 "--fix", "--fix-only", "--unsafe-fixes", "format"} for w in words):
        return None
    name = Path(words[0]).name
    if name == "gh" and words[1:3] in (["run", "view"], ["run", "watch"], ["pr", "checks"]):
        return "remote"
    if name in {"uv", "poetry"} and words[1:2] == ["run"]:
        words = words[2:]
        if not words:
            return None
        name = Path(words[0]).name
    if name in {"python", "python3"} and words[1:2] == ["-m"]:
        return "local" if words[2:3] in (["pytest"], ["unittest"], ["ruff"]) else None
    if name in {"pytest", "unittest", "ruff", "mypy", "shellcheck"}:
        return "local"
    if name in {"npm", "pnpm", "yarn", "cargo", "go"} and words[1:2] == ["test"]:
        return "local"
    if name in {"bash", "sh"} and words[1:2] == ["-n"]:
        return "local"
    # Project check scripts are allowed; arbitrary scripts and shell snippets
    # are not evidence simply because they print a success token.
    if re.fullmatch(r"(?:test|check|verify|validate|probe)(?:[-_].*)?\.(?:sh|py)", name):
        return "local"
    return None


def text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(item.get("text", "") for item in content
                         if isinstance(item, dict) and item.get("type") == "text"
                         and isinstance(item.get("text"), str))
    return ""


def analyze_transcript(lines, payload, dirty, root=None):
    """Consume JSONL once for session paths, final text, and turn evidence."""
    root = Path(root or payload.get("cwd") or Path.cwd()).resolve()
    edited, pending = set(), {}
    evidence = {"local": False, "remote": False}
    generation = 0
    message = ""
    for line in lines:
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(event, dict) or not isinstance(event.get("message"), dict):
            continue
        content = event["message"].get("content")
        blocks = [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []
        role = event.get("type")
        if role == "user" and (isinstance(content, str) or
                               isinstance(content, list) and
                               not any(b.get("type") == "tool_result" for b in blocks)):
            pending.clear()
            evidence = {"local": False, "remote": False}
        if role == "assistant":
            message = text_content(content)
            for block in blocks:
                if block.get("type") != "tool_use":
                    continue
                name, identifier = block.get("name"), block.get("id")
                args = block.get("input")
                args = args if isinstance(args, dict) else {}
                kind = None
                mutates = name in EDIT_TOOLS or name in DELEGATE_TOOLS
                if name in EDIT_TOOLS:
                    path = args.get("file_path", args.get("notebook_path"))
                    if isinstance(path, str):
                        try:
                            edited.add(str((root / path).resolve().relative_to(root)))
                        except (ValueError, OSError):
                            pass
                elif name == "Bash":
                    command = args.get("command", "")
                    if isinstance(command, str):
                        edited.update(path for path in dirty if path in command)
                    kind = command_kind(command)
                    # Unknown commands may write even without naming a file.
                    mutates = kind is None
                # Delegated summaries are prose, not observed command results.
                # Delegation may edit files; a receipt or later check is needed.
                if mutates:
                    generation += 1
                    evidence = {"local": False, "remote": False}
                if isinstance(identifier, str) and kind:
                    pending[identifier] = (kind, generation)
        elif role == "user":
            for block in blocks:
                if block.get("type") != "tool_result":
                    continue
                invocation = pending.pop(block.get("tool_use_id"), None)
                if invocation is None:
                    continue
                kind, started = invocation
                output = text_content(block.get("content"))
                if started == generation:
                    evidence[kind] = bool(GOOD.search(output) and not BAD.search(output)
                                          and not block.get("is_error"))
    return SimpleNamespace(edited=edited, evidence=evidence,
                           claim_kind=claim_kind(payload.get("last_assistant_message") or message))


def run(root, argv):
    return subprocess.run(argv, cwd=root, capture_output=True, text=True, errors="replace")


def git_paths(root, *args):
    result = subprocess.run(["git", *args, "-z"], cwd=root, capture_output=True)
    if result.returncode:
        raise RuntimeError("Cannot enumerate changed Git paths")
    return {os.fsdecode(path) for path in result.stdout.split(b"\0") if path}


def receipt_valid(root):
    module_path = root / ".agents/lib/validation.py"
    if not module_path.is_file():
        module_path = root / "seed/.agents/lib/validation.py"
    if not module_path.is_file() or not (root / ".validation_passed").is_file():
        return False
    spec = importlib.util.spec_from_file_location("stop_validation", module_path)
    module = importlib.util.module_from_spec(spec)
    # Importing the checker must not create a new source input in projects
    # which do not ignore bytecode. Receipt reuse is read-only.
    bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = bytecode
    try:
        data = module.check(root)
        return not data.get("plan", {}).get("not_applicable")
    except (module.ValidationError, OSError, ValueError, TypeError):
        return False


def stop(payload):
    if payload.get("stop_hook_active") is True:
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    located = run(cwd, ["git", "rev-parse", "--show-toplevel"])
    if located.returncode:
        return 0
    root = Path(located.stdout.rstrip("\n"))
    base = "HEAD"
    if run(root, ["git", "rev-parse", "--verify", "HEAD"]).returncode:
        base = run(root, ["git", "hash-object", "-t", "tree", "/dev/null"]).stdout.strip()
    dirty = git_paths(root, "diff", "--name-only", base) | git_paths(root, "ls-files", "--others", "--exclude-standard")
    transcript = payload.get("transcript_path")
    if isinstance(transcript, str) and transcript:
        try:
            with (root / transcript).open(encoding="utf-8", errors="replace") as lines:
                analysis = analyze_transcript(lines, payload, dirty, root)
        except OSError:
            analysis = analyze_transcript((), payload, dirty, root)
    else:
        analysis = analyze_transcript((), payload, dirty, root)
    changed = sorted(dirty & analysis.edited if analysis.edited else dirty)
    failures = []
    if changed:
        result = run(root, ["git", "--literal-pathspecs", "diff", "--check", base, "--", *changed])
        if result.returncode:
            failures.append("[git diff --check]\n" + result.stdout + result.stderr)
    python_files = [str(root / p) for p in changed if p.endswith(".py") and (root / p).is_file()]
    if python_files:
        result = run(root, ["python3", "-m", "ruff", "check", "--", *python_files])
        if result.returncode and "No module named ruff" in result.stdout + result.stderr:
            binary = shutil.which("ruff")
            if binary:
                result = run(root, [binary, "check", "--", *python_files])
            else:
                print("NOTE: ruff unavailable; the stop gate skipped its ruff leg.", file=sys.stderr)
                result = None
        if result is not None and result.returncode:
            failures.append("[ruff check]\n" + result.stdout + result.stderr)
    for path in changed:
        if path.endswith(".sh") and (root / path).is_file():
            result = run(root, ["bash", "-n", "--", str(root / path)])
            if result.returncode:
                failures.append("[bash -n] " + repr(path) + ":\n" + result.stdout + result.stderr)
    if analysis.claim_kind:
        needed = {"local", "remote"} if analysis.claim_kind == "both" else {analysis.claim_kind}
        if "local" in needed and not analysis.evidence["local"]:
            analysis.evidence["local"] = receipt_valid(root)
        # An explicit payload claim is enforceable even without a transcript.
        # With neither a payload message nor transcript text, there is no claim.
        if not all(analysis.evidence[kind] for kind in needed):
            failures.append("[unverified claim]\nFinal message claims verification without command output in this turn. "
                            "Run the check or reuse a matching local validation receipt; remote CI requires remote evidence. "
                            "Otherwise write 'not verified'.")
    if failures:
        print("Turn-end verification gate FAILED — fix these before ending the turn:\n\n" +
              "\n".join(failures), file=sys.stderr)
        return 2
    return 0


def main():
    try:
        try:
            payload = json.load(sys.stdin)
        except ValueError:
            payload = {}
        return stop(payload if isinstance(payload, dict) else {})
    except Exception as error:
        print("Turn-end verification gate FAILED: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
