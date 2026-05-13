#!/usr/bin/env python3
"""Merge flavor hook registrations into .claude/settings.json.

Usage: python3 _copier_merge_hooks.py <fragment.json> <target.json>

Appends hook entries from fragment into target without replacing existing entries.
"""
import json, sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <fragment.json> <target.json>", file=sys.stderr)
    sys.exit(1)

fragment_path, target_path = sys.argv[1], sys.argv[2]

try:
    with open(fragment_path) as f:
        fragment = json.load(f)
    with open(target_path) as f:
        target = json.load(f)

    for event, entries in fragment.get("hooks", {}).items():
        if event not in target.setdefault("hooks", {}):
            target["hooks"][event] = entries
        else:
            existing = target["hooks"][event]
            for entry in entries:
                matcher = entry.get("matcher", "")
                match_obj = next(
                    (e for e in existing if e.get("matcher") == matcher), None
                )
                if match_obj is None:
                    existing.append(entry)
                else:
                    existing_cmds = {
                        h.get("command") for h in match_obj.get("hooks", [])
                    }
                    for hook in entry.get("hooks", []):
                        if hook.get("command") not in existing_cmds:
                            match_obj["hooks"].append(hook)

    with open(target_path, "w") as f:
        json.dump(target, f, indent=2)
        f.write("\n")

    print("[copier] Hooks merged into settings.json")
except Exception as e:
    print(f"[copier] Warning: settings merge failed: {e}", file=sys.stderr)
