#!/usr/bin/env python3
"""Fail on a dead backticked path or a dead relative link in Loam's live docs (#281).

Live docs are the `.md` files tracked under `docs/`, less `docs/archive/`, `docs/research/` and
`docs/specs/` (frozen text, or text about other repos), and every tracked file under `seed/docs/`.

A backticked path follows the rule of bin/check's "skill and agent frontmatter + references" step:
a lone `...` span that is a slash path, ends in `/`, names a file type, or starts with a directory
that exists, must exist from the root, from `seed/`, or from a directory above the doc, itself or
as a `.jinja` template. Lines inside a ``` fence are skipped.

A relative markdown link [text](target), outside code, must name a file or directory that exists
from the doc's own directory (or as a `.jinja` template); `#anchor` and `?query` are dropped first.

bin/doc_paths_baseline.txt (missing means empty) holds one `<doc> <path>` pair per line: a backticked
hit it lists passes, and a pair that no longer hits fails as stale, so the list only shrinks.
Dead links have no baseline.

Exit status: 0 when nothing fails, 1 otherwise.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

EXCLUDE = ("docs/archive/", "docs/research/", "docs/specs/")
BASELINE = "bin/doc_paths_baseline.txt"
# Paths a skill or agent writes, or reads only if present, in the project it runs in.
OPTIONAL = {".claude/rules/", ".claude/codex-reviews/", "docs/hypothesis_tree.md"}
SPAN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
PATH = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_.-]*(/[A-Za-z0-9_.-]+)+/?")
CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\)")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


def exists(path: pathlib.Path) -> bool:
    return path.exists() or path.with_name(path.name + ".jinja").exists()


def dead_paths(root: pathlib.Path, doc: str, line: str) -> list[str]:
    """The backticked paths on one line that exist nowhere: the skill and agent step's rule."""
    bases = [root, root / "seed", *[root / p for p in pathlib.PurePath(doc).parents]]
    out = []
    for span in SPAN.findall(line):
        if not PATH.fullmatch(span) or span in OPTIONAL:
            continue
        # A file path names a file type, a directory, or a directory that exists; `origin/main` does none.
        first, last = span.split("/")[0], span.rstrip("/").rsplit("/", 1)[-1]
        if not (span.endswith("/") or "." in last.lstrip(".") or any((b / first).is_dir() for b in bases)):
            continue
        if not any(exists(b / span) for b in bases):
            out.append(span)
    return out


def dead_links(root: pathlib.Path, doc: str, line: str) -> list[str]:
    """The relative link targets on one line, outside code spans, that name no file or directory."""
    out = []
    for target in LINK.findall(CODE.sub("", line)):
        if SCHEME.match(target) or target.startswith(("/", "#")):
            continue
        rel = re.split(r"[#?]", target, maxsplit=1)[0]
        if not exists(root / pathlib.PurePath(doc).parent / rel):
            out.append(target)
    return out


def live_docs(root: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "--", "docs", "seed/docs"],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    return [f for f in out if f.startswith("seed/docs/")
            or (f.endswith(".md") and not f.startswith(EXCLUDE))]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="a git checkout (default: .)")
    root = pathlib.Path(ap.parse_args().root)
    base_file = root / BASELINE
    baseline = {}
    if base_file.exists():
        for n, raw in enumerate(base_file.read_text(encoding="utf-8").splitlines(), 1):
            if raw.strip():
                baseline[tuple(raw.split(None, 1))] = n
    fails, hit = [], set()
    for doc in live_docs(root):
        fenced = False
        for n, line in enumerate((root / doc).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("```"):
                fenced = not fenced
            if fenced:
                continue
            for path in dead_paths(root, doc, line):
                if (doc, path) in baseline:
                    hit.add((doc, path))
                else:
                    fails.append(f"{doc}:{n}: {path} does not exist (fix it, or name a path that exists)")
            fails += [f"{doc}:{n}: {t} is a dead relative link" for t in dead_links(root, doc, line)]
    for pair, n in baseline.items():
        if pair not in hit:
            fails.append(f"{BASELINE}:{n}: {' '.join(pair)} no longer hits; delete the line")
    for f in fails:
        print("FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
