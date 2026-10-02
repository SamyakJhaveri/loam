#!/usr/bin/env python3
# Source: https://github.com/yuan1z0825/nature-skills
# Commit: 84880815fb37317b3766bff2c2abba395b8993c3
# Path:   skills/nature-shared/scripts/check_consistency.py, lines 1-273 (the whole file)
# License: Apache License 2.0, https://www.apache.org/licenses/LICENSE-2.0
#          (no NOTICE file and no named copyright holder upstream).
# Changes made in this copy (the research-paper plugin):
#   1. This header, and "# fmt: off" below it, so ruff keeps the upstream layout and a diff
#      against upstream shows only these changes.
#   2. LaTeX comments (upstream L61): COMMENT_PATTERN drops a comment from a % that follows
#      an even number of backslashes, and keeps those backslashes. Upstream already kept a
#      lone \% (a percent sign in text) but kept the comment after \\% (a line break, then
#      a comment) as text.
#   3. Units (upstream L20-25, L158-202 and L222): upstream matched um, mm, cm and m with
#      re.IGNORECASE, so 5 mM (millimolar), 5 Mm, 5 M and 5 uM were read as lengths. Rule
#      chosen: a unit symbol matches only in its exact case, because case is part of an SI
#      symbol (m milli or metre, M mega; s second, S siemens; b bit, B byte), so ms is not
#      Ms and Mb is not MB. Case carries no meaning in one place, the kilo prefix: SI has
#      no capital-K prefix, so KB and kB, Kb and kb, KiB and kiB each name one unit and
#      match in either case. The micro sign has three spellings (u, U+00B5, U+03BC).
#      To apply the rule to the brief's examples, the unit table gains time (ns, us, ms, s)
#      and data size (B, and b and B after the k, M, G, T, Ki, Mi, Gi and Ti prefixes; no
#      bare b, which reads subfigure and hash letters such as 3b and 12b90577 as bits) next
#      to length; each quantity is compared only with itself. LENGTH_FACTORS_METRES,
#      LENGTH_PATTERN and check_equivalent_length_units become UNIT_FACTORS, UNIT_PATTERN
#      and check_equivalent_units; normalized_unit returns (quantity, symbol); the length
#      finding keeps its code EQUIVALENT_LENGTH_UNIT_VARIANT, and time and data use
#      EQUIVALENT_TIME_UNIT_VARIANT and EQUIVALENT_DATA_UNIT_VARIANT.
#   4. Config defaults (paper_config.py, imported here): with no path given, the files are
#      paper.abstract_tex and the paper.sections files of paper-tools.toml (every .tex file in
#      paper.sections_dir but the abstract when the list is empty); a configured file that does
#      not exist is skipped with a note on stderr, and none at all is a usage error. The term
#      groups of consistency.term_groups come after the built-in groups and before
#      --term-group. The hash in the comment of change 3 is an invented one.
# fmt: off
"""Find mechanically detectable consistency risks in manuscript text files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence

from paper_config import load


DEFAULT_TERM_GROUPS = {
    "self-reference": ("this study", "this work", "this paper", "this article"),
    "standard-deviation": ("standard deviation", "SD", "Std"),
}

# Size of each unit symbol in its quantity's base unit (metre, second, byte).
DATA_PREFIXES = {
    "": 1, "k": 10**3, "M": 10**6, "G": 10**9, "T": 10**12,
    "Ki": 2**10, "Mi": 2**20, "Gi": 2**30, "Ti": 2**40,
}
UNIT_FACTORS = {
    "length": {
        "um": Decimal("0.000001"),
        "mm": Decimal("0.001"),
        "cm": Decimal("0.01"),
        "m": Decimal("1"),
    },
    "time": {
        "ns": Decimal("0.000000001"),
        "us": Decimal("0.000001"),
        "ms": Decimal("0.001"),
        "s": Decimal("1"),
    },
    "data": {
        prefix + base: size * factor
        for prefix, factor in DATA_PREFIXES.items()
        for base, size in (("b", Decimal("0.125")), ("B", Decimal("1")))
        if prefix or base == "B"  # a bare b is a subfigure or hash letter ("3b", "12b90577")
    },
}
BASE_UNITS = {"length": "m", "time": "s", "data": "B"}


def unit_spellings() -> dict[str, tuple[str, str]]:
    """Every spelling a unit symbol matches, with its quantity and symbol:
    the exact symbol, the micro sign's three spellings, and the kilo prefix in
    either case (see the header for the rule)."""
    spellings: dict[str, tuple[str, str]] = {}
    for quantity, symbols in UNIT_FACTORS.items():
        for symbol in symbols:
            variants = {symbol}
            if symbol.startswith("u"):
                variants |= {"μ" + symbol[1:], "µ" + symbol[1:]}
            if symbol.startswith("k"):
                variants.add("K" + symbol[1:])
            if symbol.startswith("Ki"):
                variants.add("ki" + symbol[2:])
            spellings.update(dict.fromkeys(variants, (quantity, symbol)))
    return spellings


UNIT_SPELLINGS = unit_spellings()


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class Occurrence:
    path: Path
    line: int
    value: str

    def label(self) -> str:
        return f"{self.path}:{self.line}: {self.value}"


def read_sources(paths: Sequence[Path]) -> dict[Path, str]:
    return {
        path: path.read_text(encoding="utf-8", errors="replace")
        for path in paths
    }


# A LaTeX comment starts at a % after an even number of backslashes: none, or
# escaped backslashes such as the line break \\. Group 1 keeps those backslashes.
# \% (an odd number) is a percent sign in text and stays.
COMMENT_PATTERN = re.compile(r"(?<!\\)((?:\\\\)*)%.*$")


def visible_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield lines after removing Markdown fences and unescaped LaTeX comments."""
    in_fence = False
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*```", raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = COMMENT_PATTERN.sub(r"\1", raw_line)
        yield line_number, line


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    prefix = r"(?<![\w-])" if phrase[0].isalnum() else ""
    suffix = r"(?![\w-])" if phrase[-1].isalnum() else ""
    return re.compile(prefix + escaped + suffix, re.IGNORECASE)


def find_phrase_occurrences(
    sources: dict[Path, str], phrase: str
) -> list[Occurrence]:
    pattern = phrase_pattern(phrase)
    occurrences: list[Occurrence] = []
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in pattern.finditer(line):
                occurrences.append(Occurrence(path, line_number, match.group(0)))
    return occurrences


def check_term_groups(
    sources: dict[Path, str], groups: dict[str, tuple[str, ...]]
) -> list[Finding]:
    findings: list[Finding] = []
    for group_name, variants in groups.items():
        present: list[tuple[str, list[Occurrence]]] = []
        for variant in variants:
            occurrences = find_phrase_occurrences(sources, variant)
            if occurrences:
                present.append((variant, occurrences))
        if len(present) < 2:
            continue
        counts = ", ".join(f"{variant}={len(items)}" for variant, items in present)
        evidence = tuple(
            occurrence.label()
            for _, items in present
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code="TERM_VARIANTS_PRESENT",
                message=f"term group '{group_name}' uses multiple variants: {counts}",
                evidence=evidence,
            )
        )
    return findings


NUMBER_PATTERN = re.compile(r"(?<![\w.])([+-]?(?:\d+\.\d+|\d+))(?![\w.])")


def decimal_places(token: str) -> int:
    unsigned = token.lstrip("+-")
    return len(unsigned.partition(".")[2]) if "." in unsigned else 0


def check_numeric_precision(sources: dict[Path, str]) -> list[Finding]:
    values: dict[Decimal, dict[int, list[Occurrence]]] = {}
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in NUMBER_PATTERN.finditer(line):
                token = match.group(1)
                try:
                    value = Decimal(token)
                except InvalidOperation:
                    continue
                places = decimal_places(token)
                values.setdefault(value, {}).setdefault(places, []).append(
                    Occurrence(path, line_number, token)
                )

    findings: list[Finding] = []
    for value, precision_groups in values.items():
        if len(precision_groups) < 2:
            continue
        precision_summary = ", ".join(
            f"{places} decimal place(s)={len(items)}"
            for places, items in sorted(precision_groups.items())
        )
        evidence = tuple(
            occurrence.label()
            for _, items in sorted(precision_groups.items())
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code="NUMERIC_PRECISION_VARIANT",
                message=f"numeric value {value} appears at multiple precisions: {precision_summary}",
                evidence=evidence,
            )
        )
    return findings


# Case-sensitive: see the header for the case rule.
UNIT_PATTERN = re.compile(
    r"(?<![\w.])([+-]?(?:\d+\.\d+|\d+))\s*(?:\\,\s*)?"
    r"(?:\\(?:mathrm|text)\s*\{\s*)?("
    + "|".join(sorted(map(re.escape, UNIT_SPELLINGS), key=len, reverse=True))
    + r")(?:\s*\})?"
    r"(?![A-Za-z])",
)


def normalized_unit(unit: str) -> tuple[str, str]:
    """The quantity and symbol a matched unit spelling stands for."""
    return UNIT_SPELLINGS[unit]


def check_equivalent_units(sources: dict[Path, str]) -> list[Finding]:
    values: dict[tuple[str, Decimal], dict[str, list[Occurrence]]] = {}
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in UNIT_PATTERN.finditer(line):
                number, raw_unit = match.groups()
                quantity, unit = normalized_unit(raw_unit)
                size = Decimal(number) * UNIT_FACTORS[quantity][unit]
                values.setdefault((quantity, size), {}).setdefault(unit, []).append(
                    Occurrence(path, line_number, match.group(0))
                )

    findings: list[Finding] = []
    for (quantity, size), unit_groups in values.items():
        if len(unit_groups) < 2:
            continue
        counts = ", ".join(
            f"{unit}={len(items)}" for unit, items in sorted(unit_groups.items())
        )
        evidence = tuple(
            occurrence.label()
            for _, items in sorted(unit_groups.items())
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code=f"EQUIVALENT_{quantity.upper()}_UNIT_VARIANT",
                message=(
                    f"equivalent {quantity} {size} {BASE_UNITS[quantity]} "
                    f"appears in multiple units: {counts}"
                ),
                evidence=evidence,
            )
        )
    return findings


def parse_term_group(value: str) -> tuple[str, tuple[str, ...]]:
    name, separator, raw_variants = value.partition("=")
    variants = tuple(item.strip() for item in raw_variants.split("|") if item.strip())
    if not separator or not name.strip() or len(variants) < 2:
        raise argparse.ArgumentTypeError(
            "term groups must use NAME=variant one|variant two with at least two variants"
        )
    return name.strip(), variants


def run_checks(
    paths: Sequence[Path],
    term_groups: dict[str, tuple[str, ...]] | None = None,
) -> list[Finding]:
    sources = read_sources(paths)
    findings = check_term_groups(sources, term_groups or {})
    findings.extend(check_numeric_precision(sources))
    findings.extend(check_equivalent_units(sources))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find terminology, numeric-precision, and equivalent-unit variants."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="files to read (default: paper.abstract_tex and the paper.sections files)",
    )
    parser.add_argument(
        "--term-group",
        action="append",
        default=[],
        type=parse_term_group,
        metavar="NAME=TERM|VARIANT",
        help="Add a manuscript-specific terminology group. Repeat as needed.",
    )
    parser.add_argument(
        "--no-default-term-groups",
        action="store_true",
        help="Disable the built-in self-reference and standard-deviation groups.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return exit status 1 when warnings are found.",
    )
    return parser


def config_paths(paper: dict) -> list[Path]:
    """paper.abstract_tex and the paper.sections files (every .tex file in paper.sections_dir
    but the abstract when the list is empty); a configured file that does not exist is noted."""
    folder, abstract = paper["sections_dir"], paper["abstract_tex"]
    if folder is None:
        sections = []
    elif paper["sections"]:
        sections = [folder / f"{name}.tex" for name in paper["sections"]]
    else:
        sections = sorted(path for path in folder.glob("*.tex") if path != abstract)
    paths = []
    for path in (abstract, *sections):
        if path is not None and path.is_file():
            paths.append(path)
        elif path is not None:
            print(f"NOTE: no file at {path} (paper-tools.toml); not read", file=sys.stderr)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load()
    paths = args.paths or config_paths(cfg["paper"])
    if not paths:
        parser.error("the following arguments are required: paths (paper.abstract_tex and "
                     "paper.sections in paper-tools.toml name no file)")
    groups = {} if args.no_default_term_groups else dict(DEFAULT_TERM_GROUPS)
    for name, variants in cfg["consistency"]["term_groups"].items():
        if (not isinstance(variants, list) or len(variants) < 2
                or not all(isinstance(item, str) and item.strip() for item in variants)):
            parser.error(f"consistency.term_groups.{name} in paper-tools.toml must list at least "
                         "two terms")
        groups[name] = tuple(item.strip() for item in variants)
    groups.update(dict(args.term_group))
    findings = run_checks(paths, groups)

    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding.code}\t{finding.message}")
            for item in finding.evidence:
                print(f"  {item}")
    else:
        print("No mechanical consistency warnings found.")

    return 1 if findings and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
