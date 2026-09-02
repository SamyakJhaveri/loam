#!/usr/bin/env python3
"""Measure the always-loaded skill-listing token weight.

Every model-invocable skill spends its `name` + `description` in the skill
listing on *every* request, whether or not it is invoked (Claude Code docs:
"Low (descriptions every request)"). This script sums that weight per source so
a budget can gate listing growth, and so the harness smoke rig has a Score B.

A skill with `disable-model-invocation: true` is not in the listing and costs
nothing here (docs: "Description not in context").

Token estimate: characters / 4. Calibrate the budget against `/context` once;
the ratio is stable enough for a regression gate.

Exit status: 0 if every gated source is within budget (or no budget given),
1 if any gated source exceeds its budget.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

CHARS_PER_TOKEN = 4

# Sources whose listing weight we report. A "gated" source is checked against
# the budget; the seed is reported but not gated (it ships one tiny skill).
SOURCES = {
    "seed": ("seed/.agents/skills", False),
    "sam-cc-setup": ("cultivation/marketplace/sam-cc-setup/skills", True),
    "impeccable": ("cultivation/marketplace/impeccable/skills", False),
}

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)
_NAME = re.compile(r"^name:\s*(.+)$", re.M)
_DESC = re.compile(r"^description:\s*(.+?)(?=^[A-Za-z0-9_-]+:|\Z)", re.S | re.M)
_MANUAL = re.compile(r"^disable-model-invocation:\s*true\s*$", re.M)


def _listing_chars(skill_dir: str) -> tuple[int, int, int]:
    """Return (model_invocable_count, manual_count, listing_chars)."""
    model = manual = chars = 0
    for path in sorted(glob.glob(os.path.join(skill_dir, "**", "SKILL.md"), recursive=True)):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        match = _FRONTMATTER.match(text)
        if not match:
            continue
        frontmatter = match.group(1)
        if _MANUAL.search(frontmatter):
            manual += 1
            continue
        model += 1
        name = _NAME.search(frontmatter)
        desc = _DESC.search(frontmatter)
        chars += len(name.group(1).strip()) if name else 0
        chars += len(desc.group(1).strip()) if desc else 0
    return model, manual, chars


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--budget-tokens",
        type=int,
        default=None,
        help="Fail if a gated source's listing exceeds this token count.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    report = {}
    over_budget = []
    for label, (rel, gated) in SOURCES.items():
        skill_dir = os.path.join(args.root, rel)
        if not os.path.isdir(skill_dir):
            continue
        model, manual, chars = _listing_chars(skill_dir)
        tokens = chars // CHARS_PER_TOKEN
        report[label] = {
            "model_invocable": model,
            "manual_only": manual,
            "listing_chars": chars,
            "listing_tokens": tokens,
            "gated": gated,
        }
        if gated and args.budget_tokens is not None and tokens > args.budget_tokens:
            over_budget.append((label, tokens))

    if args.json:
        print(json.dumps(report, indent=2))
    elif not args.quiet:
        for label, data in report.items():
            flag = " [gated]" if data["gated"] else ""
            print(
                f"{label}{flag}: {data['listing_tokens']} tokens "
                f"({data['model_invocable']} listed, {data['manual_only']} manual)"
            )
        if args.budget_tokens is not None:
            print(f"budget: {args.budget_tokens} tokens per gated source")

    if over_budget:
        for label, tokens in over_budget:
            print(
                f"FAIL: {label} listing is {tokens} tokens, over the "
                f"{args.budget_tokens}-token budget.",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
