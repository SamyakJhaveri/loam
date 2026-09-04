#!/usr/bin/env python3
"""Measure the always-loaded skill-listing token weight.

Every model-invocable skill spends its `name` + `description` in the skill
listing on *every* request, whether or not it is invoked (Claude Code docs:
"Low (descriptions every request)"). Every agent spends its `name` +
`description` in the Agent tool listing the same way, on every request. Every
workflow spends its `meta.name` + `meta.description` in the workflow listing on
every request. This script sums that weight per source so a budget can gate
listing growth, and so the harness smoke rig has a Score B.

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

# Sources whose listing weight we report. A "gated" source is budget-checked;
# the seed is reported but not gated. `agents`/`workflows` are None if absent.
_MP = "cultivation/marketplace"
SOURCES = {
    "seed": {"skills": "seed/.agents/skills", "agents": None, "workflows": None,
             "gated": False},
    "sam-cc-setup": {"skills": f"{_MP}/sam-cc-setup/skills",
                     "agents": f"{_MP}/sam-cc-setup/agents",
                     "workflows": f"{_MP}/sam-cc-setup/workflows", "gated": True},
    "impeccable": {"skills": f"{_MP}/impeccable/skills", "agents": None,
                   "workflows": None, "gated": False},
}

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_NAME = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DESC = re.compile(r"^description:\s*(.+?)(?=^[A-Za-z0-9_-]+:|\Z)", re.DOTALL | re.MULTILINE)
_MANUAL = re.compile(r"^disable-model-invocation:\s*true\s*$", re.MULTILINE)
_META = re.compile(r"export const meta\s*=\s*\{(.*?)^\}", re.DOTALL | re.MULTILINE)
_META_NAME = re.compile(r"""\bname:\s*(['"])(.*?)(?<!\\)\1""")
_META_DESC = re.compile(r"""\bdescription:\s*(['"])(.*?)(?<!\\)\1""")


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


def _workflow_listing(workflows_dir: str) -> tuple[int, int]:
    """Return (count, chars) of meta name+description over every `*.js` file."""
    count = chars = 0
    for path in sorted(glob.glob(os.path.join(workflows_dir, "*.js"))):
        with open(path, encoding="utf-8") as handle:
            meta = _META.search(handle.read())
        if not meta:
            continue
        name = _META_NAME.search(meta.group(1))
        desc = _META_DESC.search(meta.group(1))
        count += 1
        chars += len(name.group(2)) if name else 0
        chars += len(desc.group(2)) if desc else 0
    return count, chars


def summarize_source(root: str, source: dict) -> dict:
    """Return the listing report for one source, resolved against `root`."""
    pattern = os.path.join(root, source["skills"], "**", "SKILL.md")
    skills = sorted(glob.glob(pattern, recursive=True))
    model, manual, skills_chars = _frontmatter_chars(skills, honor_manual=True)
    agents = agents_chars = 0
    if source["agents"]:
        paths = sorted(glob.glob(os.path.join(root, source["agents"], "*.md")))
        agents, _manual, agents_chars = _frontmatter_chars(paths, honor_manual=False)
    workflows = workflows_chars = 0
    if source["workflows"]:
        workflows, workflows_chars = _workflow_listing(os.path.join(root, source["workflows"]))
    listing_chars = skills_chars + agents_chars + workflows_chars
    return {
        "model_invocable": model,
        "manual_only": manual,
        "agents": agents,
        "workflows": workflows,
        "skills_chars": skills_chars,
        "agents_chars": agents_chars,
        "workflows_chars": workflows_chars,
        "listing_chars": listing_chars,
        "listing_tokens": listing_chars // CHARS_PER_TOKEN,
        "gated": source["gated"],
    }


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
    for label, source in SOURCES.items():
        if not os.path.isdir(os.path.join(args.root, source["skills"])):
            continue
        data = summarize_source(args.root, source)
        report[label] = data
        tokens = data["listing_tokens"]
        if data["gated"] and args.budget_tokens is not None and tokens > args.budget_tokens:
            over_budget.append((label, tokens))

    if args.json:
        print(json.dumps(report, indent=2))
    elif not args.quiet:
        for label, data in report.items():
            flag = " [gated]" if data["gated"] else ""
            plural = "" if data["workflows"] == 1 else "s"
            print(
                f"{label}{flag}: {data['listing_tokens']} tokens "
                f"({data['model_invocable']} skills listed, "
                f"{data['manual_only']} manual, {data['agents']} agents, "
                f"{data['workflows']} workflow{plural})"
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
