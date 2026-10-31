#!/usr/bin/env python3
"""Fail on a dead backticked path or a dead relative link in Loam's live docs (#281).

Live docs are the `.md` files tracked under `docs/`, less `docs/archive/`, `docs/research/` and
`docs/specs/` (frozen text, or text about other repos), and every tracked file under `seed/docs/`.

A backticked path follows the rule of bin/check's "skill and agent frontmatter + references" step:
a lone `...` span that is a slash path, ends in `/`, names a file type, or starts with a directory
that exists, must exist from the root, from `seed/`, or from a directory above the doc, itself or
as a `.jinja` template. Lines inside a ``` or ~~~ fence are skipped. Unlike that step, "exists"
means on disk and tracked by git once symlinks are resolved (a file, a directory holding one, or a
tracked symlink), so an ignored or local file such as `.superpowers/` neither passes a hit nor turns
a baseline line stale in one checkout only, and a tracked file deleted on disk fails.

A relative markdown link [text](target), outside code, must name a file or directory that exists
the same way from the doc's own directory (or as a `.jinja` template); `#anchor` and `?query` are
dropped and %-escapes decoded first.

bin/doc_paths_baseline.txt (missing means empty) holds one `<doc> <path>` pair per line: a backticked
hit it lists passes, and a pair that no longer hits fails as stale, so the list only shrinks.
Dead links have no baseline.

Exit status: 0 when nothing fails, 1 otherwise.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import posixpath
import re
import subprocess
import sys
import urllib.parse

EXCLUDE = ("docs/archive/", "docs/research/", "docs/specs/")
BASELINE = "bin/doc_paths_baseline.txt"
# Paths a skill or agent writes, or reads only if present, in the project it runs in.
OPTIONAL = {".claude/rules/", ".claude/codex-reviews/", "docs/hypothesis_tree.md"}
SPAN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
PATH = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_.-]*(/[A-Za-z0-9_.-]+)+/?")
CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
# A destination is <anything but > or newline>, or a bare run with one level of balanced parentheses.
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]*)>|((?:[^()\s]|\([^()\s]*\))+))(?:\s+[\"'(][^)]*)?\)")
FENCE = re.compile(r"\s*(`{3,}|~{3,})")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


class Tree:
    """The tracked files of a checkout, and every directory that holds one, as paths from the root."""

    def __init__(self, root: pathlib.Path) -> None:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, check=True)
        self.root = os.path.realpath(root)
        self.files = set(out.stdout.split("\0")) - {""}
        self.dirs = {str(d) for f in self.files for d in pathlib.PurePosixPath(f).parents}

    def real(self, path: str) -> str | None:
        """The path from the root once symlinks resolve, or None when nothing is on disk there."""
        full = os.path.join(self.root, path)
        return os.path.relpath(os.path.realpath(full), self.root) if os.path.exists(full) else None

    def has(self, path: str) -> bool:
        """On disk and tracked: itself, or its resolved path, or that as a `.jinja` template."""
        return any((r := self.real(p)) is not None and (p in self.files or r in self.files or r in self.dirs)
                   for p in (path, path + ".jinja"))

    def is_dir(self, path: str) -> bool:
        """A tracked directory or symlink entry, on disk or not, or a path resolving to a tracked directory."""
        return path in self.dirs or path in self.files or self.real(path) in self.dirs


def dead_paths(tree: Tree, doc: str, line: str) -> list[str]:
    """The backticked paths on one line that exist nowhere: the skill and agent step's rule."""
    bases = [".", "seed", *map(str, pathlib.PurePosixPath(doc).parents)]
    def exists(span: str) -> bool:
        return any(tree.has(posixpath.normpath(posixpath.join(b, span))) for b in bases)
    out = []
    for span in SPAN.findall(line):
        if not PATH.fullmatch(span) or span in OPTIONAL:
            continue
        # A file path names a file type, a directory, or a directory that exists; `origin/main` does none.
        first, last = span.split("/")[0], span.rstrip("/").rsplit("/", 1)[-1]
        if not (span.endswith("/") or "." in last.lstrip(".")
                or any(tree.is_dir(posixpath.normpath(posixpath.join(b, first))) for b in bases)):
            continue
        if not exists(span):
            out.append(span)
    return out


def dead_links(tree: Tree, doc: str, line: str) -> list[str]:
    """The relative link targets on one line, outside code spans, that name no file or directory."""
    out = []
    for angled, bare in LINK.findall(CODE.sub("", line)):
        target = angled or bare
        if not target or SCHEME.match(target) or target.startswith(("/", "#")):
            continue
        rel = urllib.parse.unquote(re.split(r"[#?]", target, maxsplit=1)[0])
        if not tree.has(posixpath.normpath(posixpath.join(posixpath.dirname(doc), rel))):
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
    baseline, fails, hit = {}, [], set()
    if base_file.exists():
        for n, raw in enumerate(base_file.read_text(encoding="utf-8").splitlines(), 1):
            if not (entry := raw.strip()):
                continue
            pair = tuple(entry.split(None, 1))
            if pair in baseline:
                fails.append(f"{BASELINE}:{n}: {entry} duplicates line {baseline[pair]}; delete the line")
            else:
                baseline[pair] = n
    tree = Tree(root)
    for doc in live_docs(tree.files):
        fence = ""  # the opening run of ` or ~ while inside a fence
        for n, line in enumerate((root / doc).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = FENCE.match(line)
            if fence:
                # A closing fence repeats the opener's character at least as long, with nothing after it.
                if m and m[1][0] == fence[0] and len(m[1]) >= len(fence) and not line[m.end():].strip():
                    fence = ""
                continue
            if m:
                fence = m[1]
                continue
            for path in dead_paths(tree, doc, line):
                if (doc, path) in baseline:
                    hit.add((doc, path))
                else:
                    fails.append(f"{doc}:{n}: {path} is not tracked by git (fix the path, or git add the file)")
            fails += [f"{doc}:{n}: {t} is a dead relative link (no tracked file or directory)" for t in dead_links(tree, doc, line)]
    for pair, n in baseline.items():
        if pair not in hit:
            fails.append(f"{BASELINE}:{n}: {' '.join(pair)} no longer hits; delete the line")
    for f in fails:
        print("FAIL:", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
