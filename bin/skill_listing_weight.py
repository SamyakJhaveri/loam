#!/usr/bin/env python3
"""Measure the always-loaded skill-listing token weight.

Every model-invocable skill spends its `name` + `description` in the skill
listing on *every* request, whether or not it is invoked (Claude Code docs:
"Low (descriptions every request)"). Every agent spends its `name` +
`description` in the Agent tool listing the same way, on every request. This
script sums that weight per source so a budget can gate listing growth, and so
the harness smoke rig has a Score B.

A skill with `disable-model-invocation: true` is not in the listing and costs
nothing here (docs: "Description not in context").

Token estimate: characters / 4. It is uncalibrated: no `/context` reading has
been recorded against it, so treat a budget as a no-growth ceiling on this
estimate, not as a real token count.

Exit status: 0 if every budgeted source is within its budget,
1 if any budgeted source exceeds it.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

CHARS_PER_TOKEN = 4

# Sources whose listing weight we report. `agents` is None if absent.
_MP = "cultivation/marketplace"
SOURCES = {
    "seed": {"skills": "seed/.agents/skills", "agents": None},
    "sam-cc-setup": {"skills": f"{_MP}/sam-cc-setup/skills",
                     "agents": f"{_MP}/sam-cc-setup/agents"},
}

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_NAME = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DESC = re.compile(r"^description:\s*(.+?)(?=^[A-Za-z0-9_-]+:|\Z)", re.DOTALL | re.MULTILINE)
_MANUAL = re.compile(r"^disable-model-invocation:\s*true\s*$", re.MULTILINE)


def _frontmatter_chars(paths: list[str], honor_manual: bool) -> tuple[int, int, int]:
    """Return (counted, manual, chars) of name+description over frontmatter files."""
    counted = manual = chars = 0
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            match = _FRONTMATTER.match(handle.read())
        if not match:
            continue
        fm = match.group(1)
        if honor_manual and _MANUAL.search(fm):
            manual += 1
            continue
        counted += 1
        name = _NAME.search(fm)
        desc = _DESC.search(fm)
        chars += len(name.group(1).strip()) if name else 0
        chars += len(desc.group(1).strip()) if desc else 0
    return counted, manual, chars


def summarize_source(root: str, source: dict) -> dict:
    """Return the listing report for one source, resolved against `root`."""
    pattern = os.path.join(root, source["skills"], "**", "SKILL.md")
    skills = sorted(glob.glob(pattern, recursive=True))
    model, manual, skills_chars = _frontmatter_chars(skills, honor_manual=True)
    agents = agents_chars = 0
    if source["agents"]:
        paths = sorted(glob.glob(os.path.join(root, source["agents"], "*.md")))
        agents, _manual, agents_chars = _frontmatter_chars(paths, honor_manual=False)
    listing_chars = skills_chars + agents_chars
    return {
        "model_invocable": model,
        "manual_only": manual,
        "agents": agents,
        "skills_chars": skills_chars,
        "agents_chars": agents_chars,
        "listing_chars": listing_chars,
        "listing_tokens": listing_chars // CHARS_PER_TOKEN,
    }


def _budget(text: str) -> tuple[str, int]:
    label, _, tokens = text.partition("=")
    if label not in SOURCES or not tokens.isdigit():
        raise argparse.ArgumentTypeError(f"expected SOURCE=TOKENS with SOURCE in {sorted(SOURCES)}")
    return label, int(tokens)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--budget",
        type=_budget,
        action="append",
        default=[],
        metavar="SOURCE=TOKENS",
        help="Fail if SOURCE's listing exceeds TOKENS. Repeat once per source.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    budgets = dict(args.budget)

    report = {}
    over_budget = []
    for label, source in SOURCES.items():
        if not os.path.isdir(os.path.join(args.root, source["skills"])):
            continue
        data = summarize_source(args.root, source)
        data["budget"] = budgets.get(label)
        report[label] = data
        if data["budget"] is not None and data["listing_tokens"] > data["budget"]:
            over_budget.append(label)

    if args.json:
        print(json.dumps(report, indent=2))
    elif not args.quiet:
        for label, data in report.items():
            budget = "" if data["budget"] is None else f" [budget {data['budget']}]"
            print(
                f"{label}{budget}: {data['listing_tokens']} tokens "
                f"({data['model_invocable']} skills listed, "
                f"{data['manual_only']} manual, {data['agents']} agents)"
            )

    for label in over_budget:
        print(
            f"FAIL: {label} listing is {report[label]['listing_tokens']} tokens, over the "
            f"{report[label]['budget']}-token budget.",
            file=sys.stderr,
        )
    return 1 if over_budget else 0


if __name__ == "__main__":
    raise SystemExit(main())
