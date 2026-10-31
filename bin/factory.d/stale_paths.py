#!/usr/bin/env python3
"""List the stale paths of one worker round: a Read that failed on a path the ticket or a doc names (#403).

Usage:
  stale_paths.py <stream.jsonl> <ticket.md> [doc...]

<stream.jsonl> is the round's `claude -p --output-format stream-json` output. Each Read tool_use is
paired with its tool_result by id; a result with is_error true is a failed Read. Its path, relative to
the current directory (the worktree), is printed when the ticket or a doc names it and it still does
not exist, so a file the round created after a failed first Read is not stale. One path per line,
once, sorted. A missing doc is skipped, and so is a stream line that is not JSON (a killed call can
leave a truncated last line). Exit 0 whatever it finds: the list informs, it does not grade.
"""

import json
import os
import re
import sys


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
            path = (b.get("input") or {}).get("file_path")
            if isinstance(path, str) and path:
                reads[b.get("id")] = path
        elif b.get("type") == "tool_result" and b.get("is_error") is True:
            failed.add(b.get("tool_use_id"))
    return {reads[i] for i in failed if i in reads}


def named(path, text):
    # A whole path, not part of a longer one: docs/a.md does not match docs/a.md.bak or x/docs/a.md.
    return re.search(r"(?<![\w./-])" + re.escape(path) + r"(?![\w/-]|\.\w)", text) is not None


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    text = ""
    for doc in argv[2:]:
        if doc == argv[2] or os.path.isfile(doc):
            with open(doc, encoding="utf-8", errors="replace") as f:
                text += f.read() + "\n"
    root = os.path.realpath(os.getcwd())
    stale = set()
    for path in failed_reads(argv[1]):
        full = os.path.realpath(os.path.join(root, path))
        if os.path.exists(full):
            continue
        rel = os.path.relpath(full, root)
        shown = full if rel == ".." or rel.startswith("../") else rel
        if named(shown, text):
            stale.add(shown)
    for path in sorted(stale):
        print(path)


if __name__ == "__main__":
    main(sys.argv)
