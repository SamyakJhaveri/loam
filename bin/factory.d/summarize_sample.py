#!/usr/bin/env python3
"""Summarize one `claude -p --output-format stream-json --verbose --include-hook-events` run.

Usage: python3 summarize_sample.py sample.jsonl [--check "command"]

Prints elapsed seconds, token usage, tool calls, hook events, permission denials,
models seen, and (optionally) whether a check command passes afterwards.
Measurement only. Not shipped with the template.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    check = None
    if "--check" in sys.argv:
        check = sys.argv[sys.argv.index("--check") + 1]

    tools: Counter[str] = Counter()
    models: Counter[str] = Counter()
    hook_events = 0
    denials = 0
    result: dict = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        kind = str(event.get("type", ""))
        sub = str(event.get("subtype", ""))
        if "hook" in kind.lower() or "hook" in sub.lower():
            hook_events += 1
        if sub == "permission_denied" or "denied" in sub.lower():
            denials += 1
        message = event.get("message")
        if isinstance(message, dict):
            if isinstance(message.get("model"), str):
                models[message["model"]] += 1
            for block in message.get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tools[str(block.get("name"))] += 1
        if kind == "result":
            result = event

    usage = result.get("usage", {}) if isinstance(result.get("usage"), dict) else {}
    print(f"elapsed_seconds: {result.get('duration_ms', 0) / 1000:.1f}")
    print(f"api_seconds: {result.get('duration_api_ms', 0) / 1000:.1f}")
    print(f"turns: {result.get('num_turns')}")
    print(f"cost_usd: {result.get('total_cost_usd')}")
    for key in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
        if key in usage:
            print(f"{key}: {usage[key]}")
    print(f"tool_calls: {sum(tools.values())} " + " ".join(f"{k}={v}" for k, v in tools.most_common()))
    print(f"hook_events: {hook_events}")
    # The result message carries the authoritative denial list; prefer it over the
    # streamed permission_denied messages, which appear only in some permission modes.
    pd = result.get("permission_denials")
    if isinstance(pd, list):
        denials = len(pd)
    print(f"denials: {denials}")
    print("models: " + " ".join(f"{k}={v}" for k, v in models.most_common()))
    if check:
        proc = subprocess.run(check, shell=True, capture_output=True, text=True)
        print(f"check_exit: {proc.returncode}")
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-1:]
        print("check_last_line: " + (tail[0] if tail else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
