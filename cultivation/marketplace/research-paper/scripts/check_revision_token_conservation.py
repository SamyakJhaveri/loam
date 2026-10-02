#!/usr/bin/env python3
# Source: https://github.com/imbad0202/academic-research-skills
# Commit: e79085d0d38609984ef8cfe0faf2d254aac9e0a9
# Path:   scripts/check_revision_token_conservation.py, lines 1-156 and 220-263 (the whole
#         file except its patch mode, lines 157-219)
# License: CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu,
#          https://creativecommons.org/licenses/by-nc/4.0/ (non-commercial research use only).
# Changes made in this copy (a private research-paper project, 2026-09-29; change 14 for the
# research-paper plugin):
#   1. This header, and "# fmt: off" below it, so ruff keeps the upstream layout and a diff
#      against upstream shows only these changes.
#   2. Pair mode only. Removed: patch mode (upstream L157-219: _op_texts, _summarize_delta,
#      audit_patch; and the "patch" subcommand, the subcommand loop and the mode branch in
#      main, upstream L232-257), and the sys.path insert and "import sys" it needed for
#      scripts._block_parser (upstream L42, L47-48). The docstring's first paragraph says so.
#   3. The em dash (U+2014) is banned in this repository: in comments and the docstring it is
#      written "-"; in _DASH_FOLD it is the escape "\u2014", which Python reads as the same
#      character, so folding is unchanged. The docstring is a raw string (it holds backslashes).
#   4. LaTeX input: read_text drops the % comments of a .tex file (a % after an even number of
#      backslashes starts a comment; \% is a percent sign and stays; TEX_COMMENT_RE is
#      COMMENT_PATTERN of check_consistency.py next to this file, made multi-line). _prose
#      also folds \% to % and {,} to ",", so 80\% is the token 80% and 24{,}994 is 24,994, as
#      in the built PDF text. main reads both files through read_text.
#   5. New delta latex_keys_delta: the keys of \cite, \citep and \citet (one token "\cite{key}"
#      per key, whatever the variant, star or optional arguments) and the targets of \ref and
#      \label ("\ref{x}", "\label{x}"). _prose blanks these commands but keeps the text of a
#      \cite's optional arguments, so digits in a key are never read as numbers, a key is never
#      read as an author-year citation, and a changed locator (Sec.~3 to Sec.~4) is still a
#      number delta, as upstream reports it.
#   6. Placeholders: \pending{Pn} and \pendingcell{Pn} (defined in the paper's macros) and the
#      built-text form "[PENDING Pn]". audit_pair aligns the ordered numbers and placeholders
#      of both texts (difflib); where the revision puts a number in place of a placeholder
#      that it no longer has (a moved placeholder is not filled), it records a fill
#      {"placeholder": "Pn", "value": "<number>"} in the new "fills" list, and that
#      placeholder and that number enter no delta, so a pass that only fills placeholders
#      is conserved. A number replaced by a different number stays a change (removed and added
#      in numbers_delta). A placeholder dropped, added or renamed without a fill goes to the new
#      placeholders_delta. New code: PLACEHOLDER_RE, VALUE_RE, _values, extract_placeholders
#      and find_fills. extract_numbers now takes the numbers from _values (the same NUMBER_RE,
#      matched in one pass with the placeholders), so a placeholder id is never a number.
#   7. "conserved" also requires empty latex_keys_delta and placeholders_delta, and no
#      placeholder filled with two different values (the new "fill_conflicts", {"Pn": [values]});
#      "fills" and "fill_conflicts" are added to the report after the deltas.
#   8. main: --source and --revision get help text ("the old file", "the new file").
#   9. Number words (2026-09-29): zero to twenty, thirty to ninety by tens, hundred, thousand,
#      dozen, half and twice, each with an optional "percent" after it, are number tokens
#      (NUMBER_WORD_RE: whole words, any case, lowercased, "\half" is no word); extract_numbers
#      adds them to the digit numbers. They are not in _values, so a fill is a digit number.
#  10. New delta strength_delta: whole-word counts of STRONG_WORDS (rung 6 of the ladder in
#      docs/CLAIM_DRIFT_GUARD.md section 1, and the qualifiers always, never, cannot, all, every,
#      first, only) and HEDGE_WORDS; "strong_added" lists strong words the revision adds and
#      "hedges_removed" the hedges it drops. New code: _words_re, _word_tokens, strength_delta.
#  11. Checked fills: audit_pair takes "verified", the tokens of passing claims: rows, and lists
#      every other fill in the new "unverified_fills". "conserved" also requires an empty
#      strength_delta and no unverified fill, so without --authorize a fill is not conserved.
#  12. main: --authorize FILE (a TSV of token, authority and an optional note; # lines are
#      comments), --findings and --decisions (repeatable). New code: read_rows, _plain_number,
#      _claims_problem, check_rows, claims_tokens and authorize. Every delta needs a passing
#      row with its token (a claims: row counts only for an added number) and every fill a
#      passing claims: row with its value; the report gets "authorization" and the exit code
#      is 0 only when it is authorized (--strict is then ignored).
#  13. Dotted member names (2026-09-29): _claims_problem walks the key from the left, and in an
#      object each step takes the longest run of dotted parts that names a member, so a model
#      name such as vendor-model-1.5 is one step (models.vendor-model-1.5.score.value); a list
#      still takes one integer index per part. Before, each part was one step and such a key
#      had "no key".
#  14. Plugin port: the project name, a model name in change 13 and a source path in change 6
#      are made generic, the ladder is docs/CLAIM_DRIFT_GUARD.md of the plugin, and the
#      author-year example in the comment above _NARRATIVE_AUTHOR names other surnames.
# fmt: off
r"""Deterministic token-conservation audit between revision rounds (#570).

Compares the multisets of numeric tokens, citation tokens
(`<!--ref:-->` / `<!--anchor:-->` markers, bracketed groups, author-year
parentheticals), and optional protected terms between a source text and
its revision, as a plain pair of drafts (this copy has no patch mode).
This copy also compares LaTeX \cite, \citep and \citet keys and \ref and
\label targets, reads a .tex file without its % comments, and reports a
placeholder (\pending{Pn}, [PENDING Pn]) replaced by a number as a fill,
not as a delta. Number words (six, twenty percent) are numbers, a fixed
list of strong words and hedges gives strength_delta, and a fill stays
unverified unless a claims: row of --authorize matches its value.
--authorize (a TSV of token, authority, note) makes the check a gate:
exit 0 only when every delta has a row whose authority holds and a
claims: row checks every fill.

Contract boundaries (issue #570):

  - **Advisory, not a gate.** A delta is not a violation - the Revision
    Roadmap may authorize it. The checker surfaces every delta with its
    claimed roadmap items so the round checkpoint can judge; default exit
    is 0 regardless of deltas (`--strict` exits 1 on any delta, for
    fixtures and tests).
  - **Necessary but not sufficient.** Exact-token conservation cannot see
    negation, comparison direction, modality, causal strength, citation
    attachment, or paraphrase-level meaning change. Those stay with the
    LLM/human audit layers; a conserved result must never be presented as
    a semantic-fidelity guarantee.
  - **Fold before split.** The whole text is Unicode-normalized (NFKC +
    dash/minus folding) BEFORE any tokenization, so a fullwidth or
    homoglyph respelling can neither smuggle a changed value past the
    comparison nor false-flag an unchanged one (the #524 ordering
    lesson).
  - Tokens are compared verbatim after folding: `612,418` → `612418` is
    a reported delta, not a silent reformat - formatting changes are for
    the checkpoint to wave through, not for the checker to forgive.

Mechanism shape borrowed from Yila-AI/sci-ssci-skills
(`sci-ssci-polishing`, `scripts/check_invariants.py`), extended with
marker-aware citation tokens, patch-mode attribution, and fold-before-
split normalization.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Canonical ref-marker grammar (scripts/verify_submission_package.py,
# pipeline_orchestrator_agent.md L3-1): the finalizer resolves a bare
# <!--ref:slug--> into 0/1/2-status-token + optional policy_hash forms, and
# revision reruns run on already-resolved drafts. Key the citation multiset on
# the SLUG alone - status/suffix tokens are derived metadata, not writer
# content - so bare↔resolved churn is not a spurious delta and a DROPPED
# resolved marker still surfaces (matching only the bare shape would let it
# vanish under COMMENT_RE, the exact miss this checker exists to prevent).
REF_MARKER_RE = re.compile(r"<!--ref:([A-Za-z][A-Za-z0-9_:-]*)(?:\s[^>]*)?-->")
ANCHOR_MARKER_RE = re.compile(r"<!--(anchor:[^>]+?)-->")
# Sign attaches only when preceded by start/whitespace/([/=/:/,/; - never
# between digits, so `0.58-0.92` stays two unsigned range endpoints while
# `β = -0.45`, `CI [-0.45, ...]`, and a comma-led `-1.3` keep their sign.
# Letter-adjacent embedded digits (H2, Model-A7, T0, v2.7.10a) are identifier
# fragments - entity-layer tokens for `--protected-terms`, not prose numbers -
# so the unsigned branch excludes them with an explicit [A-Za-z] guard (NOT
# \w: CJK-adjacent numbers like 共612名 must still count). A scientific
# exponent (`6.02e23`, `1.2E-5`) is part of the token, so `6.02e23`→`6.02e24`
# is a delta, not a truncation to a conserved `6.02`.
_MANTISSA = r"(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)"
_EXPONENT = r"(?:[eE][-+]?\d+)?"
NUMBER_RE = re.compile(
    rf"(?:(?<=[\s(\[=:,;])|^)-?{_MANTISSA}{_EXPONENT}%?"
    rf"|(?<![A-Za-z\d.]){_MANTISSA}{_EXPONENT}%?"
)
SQUARE_CITATION_RE = re.compile(r"\[(?:\d+[-,;\s]*)+\]")
# Parenthetical author-year: `(Li & Park, 2023)`. Also capture an optional
# NARRATIVE author phrase immediately preceding a bare `(year)` -
# `Smith (2020)`, `Okonkwo and Vidal (2021)`, `Al-Masri et al. (2019)` - so a
# `Smith`→`Jones` swap that keeps the same year and the same ref marker still
# surfaces as a citation delta. The author phrase is capitalized-word runs
# joined by `&` / `and` / `et al.`; the year alone is the parenthetical form.
_NARRATIVE_AUTHOR = (
    r"(?:[A-Z][\w'’-]+(?:\s+(?:&|and|et\s+al\.?)\s*)?)+"
    r"(?:\s+et\s+al\.?)?\s+"
)
AUTHOR_YEAR_RE = re.compile(
    rf"(?:{_NARRATIVE_AUTHOR})?\((?:[^()]*\b(?:19|20)\d{{2}}[a-z]?\b[^()]*|(?:19|20)\d{{2}}[a-z]?)\)"
)

_DASH_FOLD = str.maketrans({"–": "-", "\u2014": "-", "−": "-"})


# Additions of this copy (header changes 4 to 6).
# A LaTeX comment starts at a % after an even number of backslashes; group 1 keeps them.
TEX_COMMENT_RE = re.compile(r"(?<!\\)((?:\\\\)*)%.*$", re.MULTILINE)
# \cite, \citep, \citet (a star, up to two optional arguments) and \ref, \label.
LATEX_KEY_RE = re.compile(
    r"\\(?:(?P<cite>cite[pt]?)\*?(?P<opts>(?:\s*\[[^\]]*\]){0,2})|(?P<target>ref|label))"
    r"\s*\{(?P<keys>[^{}]*)\}"
)
# \pending{Pn} and \pendingcell{Pn} in the sources, [PENDING Pn] in the built text.
PLACEHOLDER_RE = re.compile(
    r"\\pending(?:cell)?\s*\{\s*(?P<tex_id>[^{}]*?)\s*\}"
    r"|\[PENDING\s+(?P<text_id>[^\]]*?)\s*\]"
)
# Placeholders and numbers in one left-to-right pass, so both keep their reading order.
VALUE_RE = re.compile(rf"{PLACEHOLDER_RE.pattern}|(?P<number>{NUMBER_RE.pattern})")


def _words_re(phrases, suffix: str = "") -> re.Pattern:
    """Whole words or phrases in any case and spacing; a \\command name is not a word."""
    alternatives = "|".join(r"\s+".join(map(re.escape, p.split())) for p in phrases)
    return re.compile(rf"(?<![\\\w])(?:{alternatives}){suffix}(?!\w)", re.IGNORECASE)


# Number words (header change 9); a "percent" after one is part of its token.
NUMBER_WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen"
    " fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy"
    " eighty ninety hundred thousand dozen half twice"
).split()
NUMBER_WORD_RE = _words_re(NUMBER_WORDS, r"(?:\s+percent)?")
# Strength words (header change 10), a fixed list: docs/CLAIM_DRIFT_GUARD.md section 1, rung 6 in
# both columns (with base and -s forms where the ladder names a verb) plus the qualifiers
# always, never, cannot, all, every, first and only; hedges from the lower rungs.
STRONG_WORDS = (
    "prove", "proves", "proven", "demonstrate that", "demonstrates that", "shows that",
    "causes", "determines", "guarantee", "guarantees", "establish", "establishes", "confirm",
    "confirms", "always", "never", "cannot", "all", "every", "first", "only",
)
HEDGE_WORDS = (
    "suggest", "suggests", "may", "might", "indicate", "indicates", "at least", "at most",
    "about", "approximately",
)
STRONG_RE = _words_re(STRONG_WORDS)
HEDGE_RE = _words_re(HEDGE_WORDS)


def normalize_text(text: str) -> str:
    """NFKC + dash/minus folding over the WHOLE text, before any split."""
    return unicodedata.normalize("NFKC", text).translate(_DASH_FOLD)


def read_text(path: Path) -> str:
    """The file's text; a .tex file loses its % comments (a \\% stays)."""
    text = path.read_text(encoding="utf-8")
    return TEX_COMMENT_RE.sub(r"\1", text) if path.suffix.lower() == ".tex" else text


def _optional_arguments(m: re.Match) -> str:
    """A \\cite's optional arguments stay prose (without brackets); keys and targets go."""
    return " " + " ".join(re.findall(r"\[([^\]]*)\]", m.group("opts") or "")) + " "


def _prose(normalized: str) -> str:
    prose = LATEX_KEY_RE.sub(_optional_arguments, COMMENT_RE.sub(" ", normalized))
    return prose.replace("\\%", "%").replace("{,}", ",")


def _values(text: str) -> list[tuple[str, str]]:
    """("placeholder", id) and ("number", token) items in reading order."""
    values = []
    for m in VALUE_RE.finditer(_prose(normalize_text(text))):
        if m.group("number") is not None:
            values.append(("number", m.group("number")))
        elif m.group("tex_id") is not None:
            values.append(("placeholder", m.group("tex_id")))
        else:
            values.append(("placeholder", m.group("text_id")))
    return values


def _word_tokens(pattern: re.Pattern, text: str) -> Counter:
    """Matches of pattern in the prose of text, lowercased and single-spaced."""
    prose = _prose(normalize_text(text))
    return Counter(" ".join(m.group(0).lower().split()) for m in pattern.finditer(prose))


def extract_numbers(text: str) -> Counter:
    numbers = Counter(value for kind, value in _values(text) if kind == "number")
    return numbers + _word_tokens(NUMBER_WORD_RE, text)


def extract_placeholders(text: str) -> Counter:
    return Counter(value for kind, value in _values(text) if kind == "placeholder")


def extract_latex_keys(text: str) -> Counter:
    """One "\\cite{key}" per \\cite, \\citep or \\citet key; "\\ref{x}" and "\\label{x}"."""
    tokens: Counter = Counter()
    for m in LATEX_KEY_RE.finditer(normalize_text(text)):
        command = "cite" if m.group("cite") else m.group("target")
        keys = m.group("keys").split(",") if m.group("cite") else [m.group("keys")]
        for key in (key.strip() for key in keys):
            if key:
                tokens[f"\\{command}{{{key}}}"] += 1
    return tokens


def find_fills(source: str, revision: str) -> list[dict]:
    """Placeholders the revision no longer has and replaces, in place, by a number."""
    old, new = _values(source), _values(revision)
    gone = extract_placeholders(source) - extract_placeholders(revision)
    fills = []
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "replace":
            continue
        for (old_kind, old_value), (new_kind, new_value) in zip(
            old[i1:i2], new[j1:j2], strict=False
        ):
            if old_kind == "placeholder" and new_kind == "number" and gone[old_value] > 0:
                gone[old_value] -= 1
                fills.append({"placeholder": old_value, "value": new_value})
    return fills


def extract_citation_tokens(text: str) -> Counter:
    normalized = normalize_text(text)
    tokens: Counter = Counter()
    for m in REF_MARKER_RE.finditer(normalized):
        tokens[f"ref:{m.group(1)}"] += 1  # keyed on slug, status tokens ignored
    for m in ANCHOR_MARKER_RE.finditer(normalized):
        tokens[m.group(1)] += 1
    prose = _prose(normalized)
    for pattern in (SQUARE_CITATION_RE, AUTHOR_YEAR_RE):
        for m in pattern.finditer(prose):
            tokens[re.sub(r"\s+", " ", m.group(0))] += 1
    return tokens


def protected_term_counts(text: str, protected_terms) -> Counter:
    """Case-sensitive counts with word boundaries on alphanumeric edges."""
    normalized = normalize_text(text)
    counts: Counter = Counter()
    for term in protected_terms:
        pattern = re.escape(normalize_text(term))
        if term and term[0].isalnum():
            pattern = r"(?<!\w)" + pattern
        if term and term[-1].isalnum():
            pattern = pattern + r"(?!\w)"
        counts[term] = len(re.findall(pattern, normalized))
    return counts


def _counter_delta(source: Counter, revision: Counter) -> dict:
    return {"removed": dict(source - revision), "added": dict(revision - source)}


def strength_delta(source: str, revision: str) -> dict:
    """Strong words the revision adds and hedges it drops (header change 10)."""
    return {
        "strong_added": dict(_word_tokens(STRONG_RE, revision) - _word_tokens(STRONG_RE, source)),
        "hedges_removed": dict(_word_tokens(HEDGE_RE, source) - _word_tokens(HEDGE_RE, revision)),
    }


def audit_pair(source: str, revision: str, protected_terms=(), verified=()) -> dict:
    """verified: fill values that a passing claims: row checked (header change 11)."""
    fills = find_fills(source, revision)
    filled_numbers = Counter(fill["value"] for fill in fills)
    filled_placeholders = Counter(fill["placeholder"] for fill in fills)
    result = {
        "numbers_delta": _counter_delta(
            extract_numbers(source), extract_numbers(revision) - filled_numbers
        ),
        "citations_delta": _counter_delta(
            extract_citation_tokens(source), extract_citation_tokens(revision)
        ),
        "protected_terms_delta": _counter_delta(
            protected_term_counts(source, protected_terms),
            protected_term_counts(revision, protected_terms),
        ),
        "latex_keys_delta": _counter_delta(
            extract_latex_keys(source), extract_latex_keys(revision)
        ),
        "placeholders_delta": _counter_delta(
            extract_placeholders(source) - filled_placeholders,
            extract_placeholders(revision),
        ),
        "strength_delta": strength_delta(source, revision),
    }
    values_by_placeholder: dict = {}
    for fill in fills:
        values_by_placeholder.setdefault(fill["placeholder"], set()).add(fill["value"])
    fill_conflicts = {
        placeholder: sorted(values)
        for placeholder, values in values_by_placeholder.items()
        if len(values) > 1
    }
    unverified_fills = [fill for fill in fills if fill["value"] not in verified]
    result["conserved"] = not fill_conflicts and not unverified_fills and all(
        not entries
        for delta in result.values()
        for entries in delta.values()
    )
    result["fills"] = fills
    result["fill_conflicts"] = fill_conflicts
    result["unverified_fills"] = unverified_fills
    return result


# --authorize (header change 12).
def read_rows(path: Path) -> list[dict]:
    """Tab-separated token, authority and an optional note; blank and # lines are skipped."""
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip() and not line.lstrip().startswith("#"):
            token, authority, note = ([f.strip() for f in line.split("\t", 2)] + ["", ""])[:3]
            rows.append({"line": number, "token": normalize_text(token),
                         "authority": authority, "note": note})
    return rows


def _plain_number(value) -> str:
    """A token or JSON value without % and thousands separators."""
    return re.sub(r"(?<=\d),(?=\d{3})", "", str(value).strip()).removesuffix("%")


def _claims_problem(token: str, target: str) -> str | None:
    """None when the JSON value at <path>#<dotted.key> equals token, else the reason."""
    path, _, key = target.rpartition("#")
    if not path or not key:
        return "a claims: authority is claims:<path>#<dotted.json.key>"
    try:
        node = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return f"cannot read {path}: {error}"
    # Header change 13: an object member is the longest run of dotted parts that names one.
    parts = key.split(".")
    while parts:
        taken = 1
        if isinstance(node, dict):
            taken = next((n for n in range(len(parts), 0, -1)
                          if ".".join(parts[:n]) in node), 1)
        try:
            step = ".".join(parts[:taken])
            node = node[int(step)] if isinstance(node, list) else node[step]
        except (KeyError, IndexError, ValueError, TypeError):
            return f"{path} has no key {key}"
        parts = parts[taken:]
    plain_token, plain_value = _plain_number(token), _plain_number(node)
    try:
        equal = float(plain_token) == float(plain_value)
    except ValueError:
        equal = plain_token == plain_value
    return None if equal else f"{path}#{key} holds {json.dumps(node)}, not {token}"


def check_rows(rows: list[dict], findings: str, decisions: str) -> tuple[list, list]:
    """The rows whose authority holds, and the failing rows with a reason."""
    passing, failing = [], []
    for row in rows:
        kind, _, target = row["authority"].partition(":")
        if kind == "finding" and not re.fullmatch(r"[0-9a-f]{8}", target):
            reason = f"finding id {target!r} is not 8 lowercase hex digits"
        elif kind in ("finding", "decision"):
            text = findings if kind == "finding" else decisions
            found = target and protected_term_counts(text, [target])[target]
            reason = None if found else f"{kind} id {target!r} is not in any --{kind}s file"
        elif kind == "claims":
            reason = _claims_problem(row["token"], target)
        else:
            reason = f"authority {row['authority']!r} is not finding:, decision: or claims:"
        if reason:
            failing.append({**row, "reason": reason})
        else:
            passing.append(row)
    return passing, failing


def claims_tokens(passing: list[dict]) -> set:
    return {row["token"] for row in passing if row["authority"].startswith("claims:")}


def authorize(report: dict, passing: list[dict], failing: list[dict]) -> dict:
    """Every delta needs a passing row with its token (a claims: row counts only for an
    added number), and every fill a passing claims: row with its value."""
    claims = claims_tokens(passing)
    others = {row["token"] for row in passing} - claims
    unauthorized = []
    for name, delta in report.items():
        if not name.endswith("_delta"):
            continue
        for side, tokens in delta.items():
            allowed = others | claims if (name, side) == ("numbers_delta", "added") else others
            unauthorized += [{"delta": name, "side": side, "token": token}
                             for token in tokens if token not in allowed]
    unauthorized += [{"delta": "fills", "placeholder": fill["placeholder"], "token": fill["value"]}
                     for fill in report["unverified_fills"]]
    return {
        "authorized": not (unauthorized or failing or report["fill_conflicts"]),
        "unauthorized": unauthorized,
        "failing_rows": failing,
    }


def _split_terms(raw: str | None) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    pair = sub.add_parser("pair", help="audit two full drafts")
    pair.add_argument("--source", type=Path, required=True, help="the old file")
    pair.add_argument("--revision", type=Path, required=True, help="the new file")
    pair.add_argument("--protected-terms", help="comma-separated protected terms")
    pair.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on any delta (advisory default: always exit 0)",
    )
    pair.add_argument(
        "--authorize",
        type=Path,
        help="TSV rows: token, authority (finding:<id>, decision:<id> or "
        "claims:<path>#<key>), note; exit 0 only when every delta has a passing row "
        "and every fill a passing claims: row (replaces --strict)",
    )
    pair.add_argument("--findings", type=Path, action="append", default=[],
                      help="a file holding the finding: ids (repeatable)")
    pair.add_argument("--decisions", type=Path, action="append", default=[],
                      help="a file holding the decision: ids (repeatable)")

    args = parser.parse_args(argv)
    terms = _split_terms(args.protected_terms)
    rows = read_rows(args.authorize) if args.authorize else []
    passing, failing = check_rows(
        rows,
        "\n".join(path.read_text(encoding="utf-8") for path in args.findings),
        "\n".join(path.read_text(encoding="utf-8") for path in args.decisions),
    )
    report = audit_pair(
        read_text(args.source), read_text(args.revision), terms, claims_tokens(passing)
    )
    if args.authorize:
        report["authorization"] = authorize(report, passing, failing)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.authorize:
        return 0 if report["authorization"]["authorized"] else 1
    return 1 if (args.strict and not report["conserved"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
