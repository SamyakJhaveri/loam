#!/usr/bin/env python3
"""Cut the bin/factory.d/pstack-gate.py test fixtures from real session transcripts on jhaveris.

  python3 bin/tests/fixtures/pstack-gate/cut.py [--projects DIR]

Each `<case>.jsonl` holds, from one session transcript (what the hook's transcript_path names), its first user
message, its skill listing (the names only), and its tool calls and results up to source line `end`, trimmed to the
fields bin/factory-parity reads; each kept event carries its source line as `src`. A result keeps its first 3 lines.
A line marked EDIT differs from its source as its comment says; every em dash in a result is a plain dash (EDIT, for
Loam's no-em-dash gate). Re-running it on jhaveris rewrites the same bytes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
W34 = "-home-samyak-distbench-isc-w34-overlap-and-segmenter/"
W35 = "-home-samyak-distbench-isc-w35-tooling/"
# The headless done-check run of 12 Nov 2026: "add one line to README.md" with this hook; blocked, router, method, edit.
HEADLESS = ("-tmp-claude-1000--home-samyak-distbench-8ac7c511-0dcf-4476-8336-664057a8c693-scratchpad-hl-repo/"
            "46dbb94b-d7f7-456c-9ab5-962c8b729d9e.jsonl")
ROUTER = "/home/samyak/loam/cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md"
METHODS = "/home/samyak/.claude/plugins/cache/cursor-plugins/pstack/0.15.36/skills"
W34_R1_METHODS = "principle-sequence-verifiable-units principle-test-behavior-not-implementation principle-prove-it-works"
FULL_READS = {  # EDIT: W34 round 1 read the router and its methods with sed -n and head; here each with one plain
    114: {"command": f"cat {ROUTER}"},  # `cat` (only a call that is one simple read counts), the first method kept
    122: {"command": f"cat {METHODS}/{W34_R1_METHODS.split()[0]}/SKILL.md"},
}
# case: (source transcript, last source line kept, {source line: replacement input, or None to drop the call})
CASES = {
    "w34-r1": (W34 + "67c6a368-b22d-466b-a038-2623a8f1dccb.jsonl", 153, {}),  # sed -n reads, then Write src 153
    "w34-r1-full-reads": (W34 + "67c6a368-b22d-466b-a038-2623a8f1dccb.jsonl", 153, FULL_READS),
    # EDIT: the full router read kept, the method reads (src 122) dropped
    "w34-r1-router-only": (W34 + "67c6a368-b22d-466b-a038-2623a8f1dccb.jsonl", 153, {114: FULL_READS[114], 122: None}),
    # EDIT: the method reads (src 122, as in w34-r1-full-reads) kept, the router read (src 114) dropped
    "w34-r1-method-only": (W34 + "67c6a368-b22d-466b-a038-2623a8f1dccb.jsonl", 153, {114: None, 122: FULL_READS[122]}),
    "w34-r2": (W34 + "063fd3c3-18fd-41e6-9a7d-8a513165d2c8.jsonl", 46, {}),  # no router read; python write src 39
    "w35-r1": (W35 + "0b660039-dc31-4778-9487-1ba27002ab4a.jsonl", 64, {}),  # no router read; decisions src 53, write 63
    "w35-r2": (W35 + "34bd7380-e368-456f-a70d-f2721a94aada.jsonl", 41, {}),  # writes only worker/ files (src 33, 40)
    # EDIT: the run's scratch repo was under /tmp, which bin/factory-parity may count as scratch, not a change; both
    # Edits (src 37 blocked, src 77 run) here name a source-tree README
    "headless": (HEADLESS, 10**9, {37: {"file_path": "/home/samyak/hl-repo/README.md"},
                                   77: {"file_path": "/home/samyak/hl-repo/README.md"}}),
}
KEEP_INPUT = ("command", "file_path", "notebook_path", "skill", "offset", "limit")


def text_of(content: object) -> str:
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def cut(path: Path, end: int, edits: dict[int, dict | None]) -> list[dict]:
    out: list[dict] = []
    first_user = True
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if n > end:
            break
        ev = json.loads(raw)
        att = ev.get("attachment") or {}
        content = (ev.get("message") or {}).get("content")
        if ev.get("type") == "attachment" and att.get("type") == "skill_listing":
            out.append({"src": n, "type": "attachment", "attachment": {"type": "skill_listing", "names": att["names"]}})
        elif ev.get("type") == "user" and isinstance(content, str) and first_user:
            first_user = False
            out.append({"src": n, "type": "user", "message": {"role": "user", "content": content}})
        elif ev.get("type") == "assistant" and isinstance(content, list):
            items = []
            for it in content:
                if it.get("type") != "tool_use" or (n in edits and edits[n] is None):
                    continue
                inp = edits.get(n) or {k: v for k, v in it["input"].items() if k in KEEP_INPUT}
                items.append({"type": "tool_use", "id": it["id"], "name": it["name"], "input": inp})
            if items:
                out.append({"src": n, "type": "assistant", "message": {"model": ev["message"].get("model"),
                                                                        "content": items}})
        elif ev.get("type") == "user" and isinstance(content, list):
            items = [{"type": "tool_result", "tool_use_id": it["tool_use_id"], "is_error": bool(it.get("is_error")),
                      "content": "\n".join(text_of(it.get("content")).splitlines()[:3]).replace(chr(0x2014), "-")}
                     for it in content if isinstance(it, dict) and it.get("type") == "tool_result"]
            if items:
                out.append({"src": n, "type": "user", "message": {"role": "user", "content": items}})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", type=Path, default=Path.home() / ".claude" / "projects")
    args = ap.parse_args()
    for case, (src, end, edits) in CASES.items():
        events = cut(args.projects / src, end, edits)
        (HERE / f"{case}.jsonl").write_text(
            "".join(json.dumps(e, separators=(",", ":"), ensure_ascii=False) + "\n" for e in events), encoding="utf-8")


if __name__ == "__main__":
    main()
