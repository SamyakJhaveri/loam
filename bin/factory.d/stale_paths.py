#!/usr/bin/env python3
"""List the stale paths of one worker round: a Read that failed on a path the ticket or a doc names (#403).

Usage:
  stale_paths.py <stream.jsonl> <ticket.md> [doc...]

<stream.jsonl> is the round's `claude -p --output-format stream-json` output. Each Read tool_use is
paired with its tool_result by id; a result with is_error true is a failed Read. Its path, relative to
the current directory (the worktree), is printed when the ticket or a doc names it and it still does
not exist, so a file the round created after a failed first Read is not stale. A path is named when a
word of the text resolves to the same file as the Read: `~` expanded, a relative word joined to the
worktree, symlinks followed, so `.claude/x.md`, `./seed/.claude/x.md` and the absolute path all name
one file, while `x.md.bak` or `x.md~` do not name `x.md`. One path per line, once, sorted. A missing
doc is skipped, and so is a stream line that is not JSON (a killed call can leave a truncated last
line). Exit 0 whatever it finds: the list informs, it does not grade.
"""

import json
import os
import re
import sys

WORD = re.compile(r"[\w.~/+-]+")  # backticks, quotes, brackets, colons and spaces end a path


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
    rel = os.path.relpath(path, root)
    return None if rel == ".." or rel.startswith("../") else rel


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    text = ""
    for doc in argv[2:]:
        if doc == argv[2] or os.path.isfile(doc):
            with open(doc, encoding="utf-8", errors="replace") as f:
                text += f.read() + "\n"
    root = os.path.realpath(os.getcwd())
    named = {resolve(word.rstrip("."), root) for word in WORD.findall(text) if word.rstrip(".")}
    stale = set()
    for path in failed_reads(argv[1]):
        full = resolve(path, root)
        if os.path.exists(full) or full not in named:
            continue
        # Show the Read's own spelling (.claude/x, not seed/.claude/x) when it sits in the worktree.
        lexical = os.path.normpath(os.path.join(root, os.path.expanduser(path)))
        stale.add(inside(lexical, root) or inside(full, root) or lexical)
    for path in sorted(stale):
        print(path)


if __name__ == "__main__":
    main(sys.argv)
