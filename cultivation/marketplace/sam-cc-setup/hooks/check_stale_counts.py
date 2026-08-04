#!/usr/bin/env python3
"""Fail when prose asserts a number that disagrees with its declared source of truth.

Why this exists (Boris, "Automation as infrastructure"): an agent that fixes a
stale number every time it appears burns tokens and misses cases. In the source
repo a single session hand-corrected the same class of stale count in THIRTEEN
files. The class recurs because the numbers live in prose and the truth lives in
code. So: the truth is read from code, and prose that disagrees is a failure.

Generalized 2026-08-04: truths and checks come from repo-local config instead of
a hardcoded constants module.

Config: .claude/stale-counts.json
{
  "truths":  {"kf_total": "python3 -c 'from mypkg.constants import EXCLUDED; print(len(EXCLUDED))'"},
  "checks":  [{"pattern": "(\\d+)\\s+KNOWN_FAIL\\s+specs",
               "truth": "kf_total",
               "message": "project-wide KNOWN_FAIL count"}],
  "search":  ["CLAUDE.md", "AGENTS.md", "README.md", ".claude", "docs"],
  "skip":    ["worktrees", "plans", ".git", "node_modules"],
  "exempt_markers": ["until 2026-01-01"]
}

- Each truth is a shell command, run once from the repo root, that must print an
  integer. A truth command that fails or prints a non-integer aborts the run
  (exit 3): a screen with a broken truth must never report clean.
- Each check is a regex whose FIRST capture group is compared to the named
  truth; a mismatch is a finding. `message` names what the number is.
- "search" mixes files and directories (directories are scanned recursively for
  .md/.sh/.py/.json/.js); "skip" entries are matched against any path part.
- The marker "stale-counts: allow" always exempts, on the line itself or within
  4 lines above it (a dated correction usually introduces the old value on the
  NEXT line, which a line-scoped exemption misses). "exempt_markers" adds more.

Deliberately NOT a fixer. It reports file:line and the correct value; a human or
an agent decides whether the doc is stale or the doc is history. Dated
historical records are legitimate - add a marker rather than rewriting the record.

    python3 check_stale_counts.py [--root DIR] [--quiet]

Exit: 0 clean or no config, 1 findings, 3 broken truth command.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

ALWAYS_EXEMPT = ("stale-counts: allow",)
CONTEXT_LINES = 4
SUFFIXES = {".md", ".sh", ".py", ".json", ".js"}


def load_config(root: pathlib.Path) -> dict | None:
    path = root / ".claude" / "stale-counts.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def resolve_truths(cfg: dict, root: pathlib.Path) -> dict[str, int]:
    truths = {}
    for name, cmd in cfg.get("truths", {}).items():
        try:
            out = subprocess.run(
                cmd, shell=True, cwd=root, capture_output=True, text=True,
                timeout=60, check=True,
            ).stdout.strip()
            truths[name] = int(out.splitlines()[-1])
        except Exception as e:
            print(f"BROKEN TRUTH '{name}': {cmd!r} -> {e}", file=sys.stderr)
            print("A screen with a broken truth must never report clean.", file=sys.stderr)
            sys.exit(3)
    return truths


def build_checks(cfg: dict, truths: dict[str, int]):
    checks = []
    for c in cfg.get("checks", []):
        rx = re.compile(c["pattern"], re.I)
        if rx.groups < 1:
            print(f"CHECK WITHOUT CAPTURE GROUP: {c['pattern']!r}", file=sys.stderr)
            sys.exit(3)
        if c["truth"] not in truths:
            print(f"CHECK NAMES UNDECLARED TRUTH: {c['truth']!r}", file=sys.stderr)
            sys.exit(3)
        checks.append((rx, truths[c["truth"]], c.get("message", c["truth"])))
    return checks


def targets(cfg: dict, root: pathlib.Path):
    self_names = {"check_stale_counts.py", "test_check_stale_counts.py",
                  "stale-counts.json"}
    skip = set(cfg.get("skip", [])) | {".git"}
    for entry in cfg.get("search", []):
        base = root / entry
        if not base.exists():
            continue
        paths = [base] if base.is_file() else (
            p for p in base.rglob("*") if p.suffix in SUFFIXES
        )
        for p in paths:
            if p.name in self_names:
                continue
            if any(part in skip for part in p.relative_to(root).parts):
                continue
            yield p


def exempt(lines: list[str], i: int, markers: tuple[str, ...]) -> bool:
    for j in range(max(0, i - CONTEXT_LINES), i + 1):
        if any(m in lines[j] for m in markers):
            return True
    return False


def scan(cfg: dict, checks, root: pathlib.Path):
    markers = ALWAYS_EXEMPT + tuple(cfg.get("exempt_markers", []))
    findings = []
    seen = set()
    for path in targets(cfg, root):
        if path in seen:
            continue
        seen.add(path)
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if exempt(lines, i, markers):
                continue
            for rx, truth, msg in checks:
                # finditer, not search: one line can assert the same count twice
                # and the second assertion is just as capable of being stale.
                for m in rx.finditer(line):
                    if int(m.group(1)) != truth:
                        findings.append(
                            (path.relative_to(root), i + 1, m.group(0).strip(), truth, msg)
                        )
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    ap.add_argument("--quiet", action="store_true", help="exit code only")
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()

    cfg = load_config(root)
    if cfg is None:
        if not args.quiet:
            print("no .claude/stale-counts.json - nothing declared, nothing checked")
        return 0

    # A config that exists but declares nothing is a mistake, not a clean run:
    # someone intended checks and got silence.
    for key in ("truths", "checks", "search"):
        if not cfg.get(key):
            print(f"INVALID CONFIG: .claude/stale-counts.json has no usable '{key}'.",
                  file=sys.stderr)
            print("Declare it or delete the file; an empty screen must not report clean.",
                  file=sys.stderr)
            return 3

    truths = resolve_truths(cfg, root)
    findings = scan(cfg, build_checks(cfg, truths), root)

    if not args.quiet:
        print("ground truth: " + ", ".join(f"{k}={v}" for k, v in truths.items()) + "\n")
        if not findings:
            print("no stale counts found")
        for path, n, text, truth, msg in findings:
            print(f"{path}:{n}\n    found:   {text}\n    truth:   {msg} = {truth}\n")
        if findings:
            print(f"{len(findings)} stale assertion(s). If a line is a dated "
                  f"historical record, add an exempt marker instead of rewriting "
                  f"the number - see this file's docstring.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
