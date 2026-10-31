#!/usr/bin/env python3
"""Fail when an enforcer that docs/RULES.md names does not resolve (#290).

Only the Enforcer column of a table whose header has one is read; finding no such cell fails. In that cell:
- `bin/check` step "<label>" needs a line `step "<label>"` in bin/check, word for word;
- a backticked span starting with `bin/` (its first word, less a `:line` suffix) must exist, on disk
  and tracked by git once symlinks resolve (bin/doc_paths.py's Tree.has);
- a backticked `test_*` name right after a backticked test file (less a `:line` suffix) names a function
  or method that file defines, at any depth.

Exit status: 0 when every enforcer resolves, 1 otherwise.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

from doc_paths import Tree

RULES = "docs/RULES.md"
CELL = re.compile(r"(?<!\\)\|")
SEPARATOR = re.compile(r":?-+:?")
STEP = re.compile(r'`bin/check` step "([^"]+)"')
SPAN = re.compile(r"`(bin/[^`]+)`")
TEST = re.compile(r"`(bin/[^`\s]+\.py)(?::[0-9,-]+)?`\s+`(test_\w+)`")


def enforcer_cells(text: str) -> list[tuple[int, str]]:
    """(line number, Enforcer cell) for each body row of a table whose header names an Enforcer column."""
    out, col = [], None
    for n, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            col = None
            continue
        cells = [c.strip() for c in CELL.split(line.strip().strip("|"))]
        if col is None:
            col = cells.index("Enforcer") if "Enforcer" in cells else -1
        elif col >= 0 and col < len(cells) and not all(SEPARATOR.fullmatch(c) for c in cells):
            out.append((n, cells[col]))
    return out


def defs(path: pathlib.Path) -> set[str] | None:
    """Every function and method name a Python file defines, or None when it does not parse."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="a git checkout (default: .)")
    root = pathlib.Path(ap.parse_args().root)
    tree = Tree(root)
    steps = {line.strip() for line in (root / "bin/check").read_text(encoding="utf-8").splitlines()}
    cells = enforcer_cells((root / RULES).read_text(encoding="utf-8"))
    fails = [] if cells else [f"{RULES}: no table row has an Enforcer cell"]
    for n, cell in cells:
        where = f"{RULES}:{n}"
        for label in STEP.findall(cell):
            if f'step "{label}"' not in steps:
                fails.append(f'{where}: bin/check has no step "{label}"')
        for span in SPAN.findall(cell):
            path = re.sub(r":[0-9,-]+$", "", span.split()[0])
            if not tree.has(path):
                fails.append(f"{where}: {path} is missing on disk or not tracked by git")
        for path, name in TEST.findall(cell):
            if not tree.has(path):
                continue
            if not (root / path).is_file():
                fails.append(f"{where}: {path} is not on disk to read def {name}")
            elif (names := defs(root / path)) is None:
                fails.append(f"{where}: {path} does not parse as Python")
            elif name not in names:
                fails.append(f"{where}: {path} has no def {name}")
    for f in fails:
        print("FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
