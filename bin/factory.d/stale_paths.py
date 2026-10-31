#!/usr/bin/env python3
"""List the stale paths of one worker round: a Read that failed on a path the ticket or a doc names (#403).

Usage:
  stale_paths.py <stream.jsonl> <ticket.md> [doc...]

<stream.jsonl> is the round's `claude -p --output-format stream-json` output. Each Read tool_use is
paired with its tool_result by id; a result with is_error true is a failed Read. Its path, relative to
the current directory (the worktree), is printed when the ticket or a doc names it and it still does
not exist, so a file the round created after a failed first Read is not stale. A path is named when a
word of the text, or a backticked span with its spaces, resolves to the same file as the Read: `~`
expanded, a relative word joined to the worktree, symlinks followed, so `.claude/x.md`,
`./seed/.claude/x.md` and the absolute path all name one file, while `x.md.bak` or `x.md~` do not name
`x.md`. One path per line, once per file, sorted. A missing doc is skipped, and so is a stream line
that is not JSON (a killed call can leave a truncated last line). Exit 0 whatever it finds: the list
informs, it does not grade.
"""

import json
import os
import re
import sys

WORD = re.compile(r"[\w.~/+@$-]+")  # quotes, brackets, colons and spaces end a bare path
CODE = re.compile(r"`([^`\n]+)`")  # a backticked span is one path, spaces and brackets included


def blocks(stream):
    with open(stream, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            message = event.get("message") if isinstance(event, dict) else None
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, list):
                yield from (b for b in content if isinstance(b, dict))


def failed_reads(stream):
    reads, failed = {}, set()
    for b in blocks(stream):
        if b.get("type") == "tool_use" and b.get("name") == "Read":
            path = b.get("input", {}).get("file_path") if isinstance(b.get("input"), dict) else None
            if isinstance(path, str) and path:
                reads[b.get("id")] = path
        elif b.get("type") == "tool_result" and b.get("is_error") is True:
            failed.add(b.get("tool_use_id"))
    return {reads[i] for i in failed if i in reads}


def resolve(path, root):
    return os.path.realpath(os.path.join(root, os.path.expanduser(path)))


def inside(path, root):
    # Relative to the ancestor that is the worktree, even when the Read spells that ancestor through a
    # symlink (macOS /var is /private/var); None when no ancestor is.
    up = path
    while os.path.realpath(up) != root:
        if os.path.dirname(up) == up:
            return None
        up = os.path.dirname(up)
    return os.path.relpath(path, up)


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    text = ""
    for doc in argv[2:]:
        if doc == argv[2] or os.path.isfile(doc):
            with open(doc, encoding="utf-8", errors="replace") as f:
                text += f.read() + "\n"
    root = os.path.realpath(os.getcwd())
    words = [w.rstrip(".") for w in WORD.findall(text)] + [w.strip() for w in CODE.findall(text)]
    named = {resolve(w, root) for w in words if w}
    stale = {}  # resolved file -> the spellings it was read by
    for path in failed_reads(argv[1]):
        full = resolve(path, root)
        if os.path.exists(full) or full not in named:
            continue
        # Show the Read's own spelling (.claude/x, not seed/.claude/x) when it sits in the worktree, unless
        # it holds a `..`, which normpath would collapse before the symlink it follows (.claude/../x).
        lexical = os.path.normpath(os.path.join(root, os.path.expanduser(path)))
        dots = ".." in path.split(os.sep)
        shown = None if dots else inside(lexical, root)
        stale.setdefault(full, set()).add(shown or inside(full, root) or (full if dots else lexical))
    for path in sorted(min(spellings) for spellings in stale.values()):
        print(path)


if __name__ == "__main__":
    main(sys.argv)
