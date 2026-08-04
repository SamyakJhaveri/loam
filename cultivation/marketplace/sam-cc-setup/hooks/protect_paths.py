#!/usr/bin/env python3
"""Verdict engine for protect-paths.sh - deny writes/deletes to a declared path set.

Generalized 2026-08-04 from three upstream-project hooks (protect-eval-results,
result-immutability, protect-benchmark-sources): the pattern travels, the path
set is repo-local config.

Config: .claude/protected-paths.txt - one glob per line, '#' comments, paths
relative to the repo root. Dormant when the config is absent (the shell wrapper
never calls this without it).

Reads the PreToolUse hook JSON on stdin. Prints one line:
    allow
    block\t<reason>

Blocks:
  - Edit/Write whose file_path matches a protected glob
  - Bash commands where a delete verb (rm, rmdir, shred, unlink) and a
    protected path appear in the SAME command segment (tokenized, not regexed:
    a regex cannot tell a shell separator from the same byte inside a quoted
    argument - this design survived five adversarial review rounds in the
    source repo's protect-eval-results.sh)
  - Bash redirects (> or >>) onto a protected path

Testable directly:  python3 protect_paths.py --config FILE  < hook.json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import sys

SEPS = {"&&", "||", "|", ";", "&", "\n"}
DELETERS = {"rm", "rmdir", "shred", "unlink"}
SHELLS = {"bash", "sh", "dash", "zsh", "ksh"}
# Constructs whose real content a static tokenizer cannot resolve: a shell fed
# from stdin, command substitution, or ANSI-C quoting. When present, fall back
# to the conservative whole-command match so an unresolvable command can never
# be quieter than a resolvable one.
INDIRECT = re.compile(
    r"<<<|<<|\$\(|`|\$'|\|\s*(?:/\S*/)?(?:" + "|".join(sorted(SHELLS)) + r")\b"
)


def load_patterns(config_path: str) -> list[str]:
    patterns = []
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line.rstrip("/"))
    return patterns


def path_matches(rel: str, patterns: list[str]) -> bool:
    """Does repo-relative path `rel` fall under any protected glob?"""
    return any(
        fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p + "/*") or rel == p
        for p in patterns
    )


def _prefixes(patterns: list[str]) -> list[str]:
    """Static prefix of each glob, for substring matching inside command tokens."""
    out = []
    for p in patterns:
        pref = re.split(r"[*?\[]", p)[0].rstrip("/")
        if pref:
            out.append(pref)
    return out


def _tokenize(cmd: str) -> list[str]:
    # punctuation_chars makes shlex emit ; & | && || as their own tokens even
    # when unspaced, while a literal ';' inside a quoted argument stays part of
    # that argument.
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def _segments(tokens: list[str]):
    current: list[str] = []
    for tok in tokens:
        if tok in SEPS:
            yield current
            current = []
        else:
            current.append(tok)
    yield current


def _loose(cmd: str, prefixes: list[str]) -> bool:
    """Last resort (unbalanced quotes, nesting past the depth cap): err toward blocking."""
    return bool(re.search(r"\brm\b", cmd)) and any(p in cmd for p in prefixes)


def bash_delete_hits(cmd: str, prefixes: list[str], depth: int = 0) -> bool:
    if depth > 4:  # cheap cycle guard on nested -c strings
        return _loose(cmd, prefixes)
    try:
        tokens = _tokenize(cmd)
    except ValueError:
        return _loose(cmd, prefixes)

    for segment in _segments(tokens):
        names = [t.rsplit("/", 1)[-1] for t in segment]
        if any(n in DELETERS for n in names) and any(
            p in t for t in segment for p in prefixes
        ):
            return True
        # Indirection: the delete verb is inside a quoted string, so the
        # tokenizer sees only the wrapper. Recurse into what a shell re-parses.
        for i, name in enumerate(names):
            arg = None
            if name in SHELLS and i + 2 < len(segment) and segment[i + 1].startswith("-"):
                arg = segment[i + 2]  # bash -c '...', combined flags like -lc
            elif name == "eval":
                arg = " ".join(segment[i + 1:])
            if arg and bash_delete_hits(arg, prefixes, depth + 1):
                return True

    # Backstop: the deletion may hide in something we cannot statically read.
    return bool(INDIRECT.search(cmd)) and _loose(cmd, prefixes)


def bash_redirect_hits(cmd: str, patterns: list[str]) -> str | None:
    """Return the redirect target if the command redirects onto a protected path."""
    for m in re.finditer(r">>?\s*([^\s;&|<>]+)", cmd):
        target = m.group(1).strip("'\"").lstrip("./")
        if path_matches(target, patterns):
            return target
    return None


def verdict(hook_input: dict, patterns: list[str], root: str) -> str:
    tool = hook_input.get("tool_name", "")
    ti = hook_input.get("tool_input", hook_input)

    if tool in ("Edit", "Write"):
        p = ti.get("file_path", "")
        if not p:
            return "allow"
        # Normalize, never prefix-strip: ./x, a/../x, //x and symlinks all
        # evaded a plain "${FILE#$ROOT/}" strip in an earlier hook.
        real_root = os.path.realpath(root)
        rel = os.path.relpath(os.path.realpath(os.path.join(real_root, p)), real_root)
        if rel.startswith("..") or os.path.isabs(rel):
            return "allow"  # outside the repo - not ours
        if path_matches(rel, patterns):
            return f"block\t{rel} is protected (.claude/protected-paths.txt)"
        return "allow"

    if tool == "Bash":
        cmd = ti.get("command", "")
        if not cmd:
            return "allow"
        if bash_delete_hits(cmd, _prefixes(patterns)):
            return "block\tdelete verb and a protected path in the same command segment"
        target = bash_redirect_hits(cmd, patterns)
        if target:
            return f"block\tredirect onto protected path {target}"
        return "allow"

    return "allow"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    args = ap.parse_args()

    try:
        patterns = load_patterns(args.config)
        hook_input = json.loads(sys.stdin.read())
    except Exception:
        print("allow")  # fail-open on infrastructure, like every hook in this set
        return 0

    if not patterns:
        print("allow")
        return 0
    print(verdict(hook_input, patterns, args.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
