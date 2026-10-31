#!/usr/bin/env python3
"""Fail on a dead backticked path or a dead relative link in Loam's live docs (#281).

Live docs are the `.md` files tracked under `docs/`, less `docs/archive/`, `docs/research/` and
`docs/specs/` (frozen text, or text about other repos), and every tracked file under `seed/docs/`.

A backticked path follows the rule of bin/check's "skill and agent frontmatter + references" step:
a lone `...` span that is a slash path, ends in `/`, names a file type, or starts with a directory
that exists, must exist from the root, from `seed/`, or from a directory above the doc, itself or
as a `.jinja` template. Lines inside a ``` fence are skipped. Unlike that step, "exists" means
tracked by git (a file, or a directory holding one), so an ignored or local file such as
`.superpowers/` neither passes a hit nor turns a baseline line stale in one checkout only.

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
import posixpath
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


def tracked(root: pathlib.Path) -> tuple[set[str], set[str]]:
    """The tracked files and every directory that holds one, as paths from the root."""
    files = set(subprocess.run(["git", "-C", str(root), "ls-files"],
                               capture_output=True, text=True, check=True).stdout.splitlines())
    return files, {str(d) for f in files for d in pathlib.PurePosixPath(f).parents}


def dead_paths(files: set[str], dirs: set[str], doc: str, line: str) -> list[str]:
    """The backticked paths on one line that exist nowhere: the skill and agent step's rule."""
    bases = [".", "seed", *map(str, pathlib.PurePosixPath(doc).parents)]
    def exists(span: str) -> bool:
        return any(p in files or p in dirs or p + ".jinja" in files
                   for p in (posixpath.normpath(posixpath.join(b, span)) for b in bases))
    out = []
    for span in SPAN.findall(line):
        if not PATH.fullmatch(span) or span in OPTIONAL:
            continue
        # A file path names a file type, a directory, or a directory that exists; `origin/main` does none.
        first, last = span.split("/")[0], span.rstrip("/").rsplit("/", 1)[-1]
        if not (span.endswith("/") or "." in last.lstrip(".")
                or any(posixpath.normpath(posixpath.join(b, first)) in dirs for b in bases)):
            continue
        if not exists(span):
            out.append(span)
    return out


def dead_links(files: set[str], dirs: set[str], doc: str, line: str) -> list[str]:
    """The relative link targets on one line, outside code spans, that name no file or directory."""
    out = []
    for target in LINK.findall(CODE.sub("", line)):
        if SCHEME.match(target) or target.startswith(("/", "#")):
            continue
        rel = re.split(r"[#?]", target, maxsplit=1)[0]
        path = posixpath.normpath(posixpath.join(posixpath.dirname(doc), rel))
        if not (path in files or path in dirs or path + ".jinja" in files):
            out.append(target)
    return out


def live_docs(files: set[str]) -> list[str]:
    return sorted(f for f in files if f.startswith("seed/docs/")
                  or (f.startswith("docs/") and f.endswith(".md") and not f.startswith(EXCLUDE)))


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
    files, dirs = tracked(root)
    fails, hit = [], set()
    for doc in live_docs(files):
        fenced = False
        for n, line in enumerate((root / doc).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("```"):
                fenced = not fenced
            if fenced:
                continue
            for path in dead_paths(files, dirs, doc, line):
                if (doc, path) in baseline:
                    hit.add((doc, path))
                else:
                    fails.append(f"{doc}:{n}: {path} does not exist (fix it, or name a path that exists)")
            fails += [f"{doc}:{n}: {t} is a dead relative link" for t in dead_links(files, dirs, doc, line)]
    for pair, n in baseline.items():
        if pair not in hit:
            fails.append(f"{BASELINE}:{n}: {' '.join(pair)} no longer hits; delete the line")
    for f in fails:
        print("FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
