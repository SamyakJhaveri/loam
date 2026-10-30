#!/usr/bin/env python3
"""Gate the prose that loads into every Loam session at a no-growth byte cap.

The set: the root CLAUDE.md (or .claude/CLAUDE.md) and AGENTS.md, every
.claude/rules/ file without `paths:` frontmatter, and every file those
@-import, recursively. Claude Code skips an @path inside a code span or a
fenced block, and so does this. Files outside --root, such as ~/.claude and
an @~/ import, are not counted. Only files git tracks count, so a local
untracked rule or CLAUDE.local.md cannot fail bin/check where CI passes.

Exit status: 0 at exactly --cap bytes, 1 over it or under it. Failing
under it makes a shrink lower the cap, so later growth must edit the cap.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ENTRY = ("CLAUDE.md", ".claude/CLAUDE.md", "AGENTS.md")
IMPORT = re.compile(r"(?<!\S)@(\S+)")
SPAN = re.compile(r"`[^`\n]*`")
FRONTMATTER = re.compile(r"---\n(.*?)\n---", re.S)
PATHS = re.compile(r"^paths:", re.M)


def _imports(text: str) -> list[str]:
    refs, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced:
            refs += IMPORT.findall(SPAN.sub("", line))
    return refs


def _scoped(path: pathlib.Path) -> bool:
    fm = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    return bool(fm and PATHS.search(fm.group(1)))


def measure(root: pathlib.Path) -> list[tuple[str, int, int]]:
    """Return (path relative to root, bytes, lines) for each always-loaded file."""
    root = root.resolve()
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True).stdout
    tracked = {(root / name).resolve() for name in listed.decode("utf-8").split("\0") if name}
    rules = sorted((root / ".claude/rules").rglob("*.md"))
    queue = [root / name for name in ENTRY]
    queue += [p for p in rules if not _scoped(p)]
    seen, files = set(), []
    while queue:
        path = queue.pop(0)
        real = path.resolve()
        if real in seen or real not in tracked or not real.is_file() or not real.is_relative_to(root):
            continue
        seen.add(real)
        data = real.read_bytes()
        files.append((real.relative_to(root).as_posix(), len(data), data.count(b"\n")))
        queue += [path.parent / pathlib.Path(ref).expanduser() for ref in _imports(data.decode("utf-8"))]
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--cap", type=int, required=True, help="The measured total in bytes; any other total fails.")
    args = parser.parse_args()

    files = measure(pathlib.Path(args.root))
    total = sum(size for _, size, _ in files)
    lines = sum(n for _, _, n in files)
    listing = ", ".join(f"{name} {size}" for name, size, _ in files)
    if total > args.cap:
        print(
            f"FAIL: always-loaded prose is {total} bytes ({lines} lines), over the {args.cap}-byte cap. "
            f"Files: {listing}. If you cut text to fit, name each cut (file and what it said) in the commit message "
            f"and the PR body; or raise the cap in bin/check in the same PR and say why.",
            file=sys.stderr,
        )
        return 1
    if total < args.cap:
        print(
            f"FAIL: always-loaded prose is {total} bytes, under the {args.cap}-byte cap. "
            f"In this PR, lower the cap in bin/check to {total}.",
            file=sys.stderr,
        )
        return 1
    print(f"always-loaded prose: {total} bytes, {lines} lines (cap {args.cap}): {listing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
