#!/usr/bin/env python3
"""Print a Claude Code transcript's owner words and auto-mode classifier refusals, with line numbers.

Usage: words-and-refusals.py TRANSCRIPT.jsonl [SUBAGENT.jsonl ...]

Owner words are the `user` entries whose `origin.kind` is exactly "human". An entry with no origin is not
counted: those are skill bodies, hook and command output, and other text the harness wrote in the user's
turn. Peer messages and task notifications carry their own kind.
A refusal is a `tool_result` with `is_error` true whose text holds "auto mode classifier", printed with the
line and input of the `tool_use` whose id it answers.
"""

from __future__ import annotations

import json
import sys

LIMIT = 400  # characters of a tool input or refusal reason; owner words print whole


def text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(text_of(block.get("text", block.get("content", ""))) for block in content
                         if isinstance(block, dict))
    return ""


def one_line(text: str, limit: int = LIMIT) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " ..."


def report(path: str) -> None:
    uses: dict[str, tuple[int, str, object]] = {}
    with open(path, encoding="utf-8") as transcript:
        for number, line in enumerate(transcript, 1):
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            message = entry.get("message") if isinstance(entry, dict) else None
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            origin = entry.get("origin")
            if entry.get("type") == "user" and isinstance(origin, dict) and origin.get("kind") == "human":
                print(f"{number}: owner {entry.get('timestamp', '')}: " + text_of(content).replace("\n", "\n    "))
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    uses[block.get("id", "")] = (number, block.get("name", ""), block.get("input"))
                elif (block.get("type") == "tool_result" and block.get("is_error") is True
                      and "auto mode classifier" in (reason := text_of(block.get("content")))):
                    used, name, tool_input = uses.get(block.get("tool_use_id", ""), (0, "?", None))
                    if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
                        tool_input = tool_input["command"]
                    asked = tool_input if isinstance(tool_input, str) else json.dumps(tool_input)
                    print(f"{number}: refused {name} (tool_use line {used or '?'}): {one_line(asked)}\n"
                          f"    reason: {one_line(reason)}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    for path in sys.argv[1:]:
        if len(sys.argv) > 2:
            print(f"== {path}")
        report(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
