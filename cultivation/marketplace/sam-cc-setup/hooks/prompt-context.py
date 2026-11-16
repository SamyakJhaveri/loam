#!/usr/bin/env python3
"""UserPromptSubmit: add the message's time, and a read-by-path line for each `/pstack:<name>` it names.

The model sees no message times, so it guesses them; this prints the time the message was submitted,
local and in the UTC form a transcript record's `timestamp` uses. pstack skills cannot
be loaded through the Skill tool, so each `/pstack:<name>` becomes "read <pstack>/skills/<name>/SKILL.md
now", using the router's own pstack-path.sh lookup. Printed text is added to the model's context.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PSTACK_NAME = re.compile(r"/pstack:([a-z0-9][a-z0-9-]*)")


def pstack_folder() -> pathlib.Path | None:
    out = subprocess.run(["bash", str(ROOT / "skills/pstack/pstack-path.sh")],
                         capture_output=True, text=True, check=False).stdout.strip()
    return pathlib.Path(out) if out else None


def main() -> int:
    prompt = json.load(sys.stdin).get("prompt", "")
    now = datetime.datetime.now().astimezone()
    utc = now.astimezone(datetime.timezone.utc)
    print(f"This message was submitted at {now:%a %d %b %Y %H:%M:%S %Z} local ({utc:%Y-%m-%dT%H:%M:%SZ}). "
          "An earlier message's time is its `timestamp` (UTC) in the session transcript; never guess one.")
    names = dict.fromkeys(PSTACK_NAME.findall(prompt))
    folder = pstack_folder() if names else None
    for name in names:
        skill = folder / "skills" / name / "SKILL.md" if folder else None
        if skill and skill.is_file():
            print(f"/pstack:{name} names a pstack skill the Skill tool cannot load: read {skill} now, in full, "
                  "and follow it.")
        else:
            print(f"/pstack:{name}: no such pstack skill is installed; say so instead of guessing its method.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
