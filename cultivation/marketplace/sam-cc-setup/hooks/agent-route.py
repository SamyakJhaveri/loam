#!/usr/bin/env python3
"""PreToolUse on Agent: refuse the built-in general-purpose and Explore agents when the owner's own agents exist.

general-purpose (also what an omitted subagent_type starts) goes to `worker`; Explore goes to `scout`.
A refusal is made only when the replacement is defined as a user or project agent, so a machine
without those agents keeps the built-ins. Exit 2 blocks the call and shows the reason to the model.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

REPLACEMENT = {
    "general-purpose": ("worker", "for edits; `scout` for a read-only search"),
    "Explore": ("scout", "for a read-only search"),
}


def defined(agent: str, project: str) -> bool:
    user = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or pathlib.Path.home() / ".claude")
    return any((d / "agents" / f"{agent}.md").is_file() for d in (user, pathlib.Path(project) / ".claude"))


def main() -> int:
    event = json.load(sys.stdin)
    asked = event.get("tool_input", {}).get("subagent_type") or "general-purpose"
    if asked not in REPLACEMENT:
        return 0
    agent, use = REPLACEMENT[asked]
    if not defined(agent, os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."):
        return 0
    print(f"Refused: subagent_type {asked}. Spawn subagent_type `{agent}` instead ({agent} {use}); "
          "the owner's routing rule maps general-purpose to worker and Explore to scout.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
