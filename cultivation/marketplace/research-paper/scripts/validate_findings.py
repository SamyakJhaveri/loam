#!/usr/bin/env python3
# Source: https://github.com/pedrohcgs/claude-code-my-workflow, scripts/validate-findings.py,
# commit ae72617 (ae726177e23426b665e0a1eef5fb5bd83bd5b831), MIT license.
#
# MIT License
#
# Copyright (c) 2026 Pedro H. C. Sant'Anna
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Patches for a private research-paper project, kept in the research-paper plugin. Our use:
# reviewer seats quote PAPER, a pdftotext dump of the built PDF or a .tex section, and this
# script gates the quotes. Defects are the ones measured when that project reviewed the
# upstream script and probed it with fixtures.
# Applied:
#   P1 SCHEMA is finding_schema.json next to this script (was ../.claude/references/;
#      the script failed with exit 2 when copied alone, and .claude/ edits need bypass mode).
#   P2 --require-quotes (with --check-quotes): a finding whose evidence has no double-quoted
#      span of 12+ characters fails unless its locus starts with "absence:". Measured: such a
#      finding passed unchecked (the old "if not quotes: continue").
#   P3 A .tex file loses its % comments before any view is built. Measured false accept: a
#      quote that exists only in a comment of abstract.tex passed, via the non-LaTeX view.
#   P4 Small caps: pdftotext extracts \textsc{ExampleSys} as "E XAMPLE S YS"; both sides now
#      map each name in paper.smallcaps_names (paper-tools.toml) from that split form back to
#      the name. Measured false reject for a quote that names the system in a sentence.
#   P5 The closest-line hint needs difflib similarity 0.55 (was 0.0). Measured: invented
#      quotes scored 0.47 and 0.49 against unrelated lines; real near misses scored 0.59
#      to 0.97. The contract tells a seat to copy from that line, so noise there is harmful.
#   P6 The "array" type and string "items" are checked: finding_schema.json has merged_ids
#      (array of strings), a type the source subset did not check.
#   P7 Em dashes in the docstring and messages replaced with "-" (house writing rule).
#   P8 For this review, quotes must come from the finding's `file` only (was: also any file
#      the evidence names by path). With --root at the repository root, a seat could quote
#      a project planning file, which contract section 1 forbids.
#   P9 The first quote must start within 3 lines of the finding's `line`. Measured: fixture
#      A with a line number past the end of the file passed, and `line` is part of the id.
# Declined:
#   D1 Two-column layout text (pdftotext -layout) gives false rejects: an input choice, not a
#      script defect. The script's own PDF path runs pdftotext without -layout; pass a
#      reading-order dump or the PDF, never -layout output.
#   D2 A .tex quote of rendered macro text ("ExampleSys" for \examplesys{}) is rejected: the
#      script cannot expand macros defined elsewhere. The contract says copy PAPER exactly, and
#      a quote copied from .tex source (with its backslash) matches as written.
#   D3 No --help flag: does not affect quote checking; the seats run the two contract
#      commands verbatim, and usage stays in this docstring.
#   D4 Ids shift when a revised draft moves line numbers: the id is defined as
#      sha1(file:line:locus) by finding_schema.json; cross-round matching belongs to the
#      adjudicator (locus and quote), not to a changed id.
#   D5 The lens enum rejected non-econ lenses: fixed in finding_schema.json, no script change.
r"""Validate a review-findings array against finding_schema.json (next to this script).

Turns the FINDING contract from prose into a gate with an exit code.

    echo '[]' | python3 validate_findings.py            # smoke test
    python3 validate_findings.py report.json
    python3 validate_findings.py --id FILE LINE LOCUS        # compute a finding id
    python3 validate_findings.py --fill-ids in.json > out.json  # add ids, then validate
    python3 validate_findings.py --check-quotes [--require-quotes] report.json [--root DIR]

--fill-ids computes every id from file:line:locus and overwrites any id present; it prints
the array only if it then validates.

--check-quotes catches the most damaging reviewer error: an invented quotation. Every
double-quoted span of 12+ characters in a finding's `evidence` ("…" or “…”, read left to
right) must occur in the finding's `file`, and the first must start within 3 lines of the
finding's `line`. Comparison is after normalisation:
Unicode NFKC, curly quotes and dashes unified, whitespace collapsed, case folded, line-end
hyphenation joined; for a quote with no backslash also LaTeX markup, `` '' quotes, \% and
-- stripped, so "significant effect" matches \emph{significant} effect. A quote containing a
backslash was copied from source and must match it as written. An elision (..., …, […])
splits a quote into fragments that must occur in order, close together. Backticked code
outside a quotation is not checked. A PDF is read through pdftotext; a file that cannot be
read as text leaves its quotes unchecked (reported, not failed). Each miss is printed with
the closest line of the file. Paths resolve against --root (default: the current directory).
A .tex file's % comments are dropped before matching, and each name in paper.smallcaps_names
(paper-tools.toml) matches its small-caps form as pdftotext extracts it ("E XAMPLE S YS"
matches "ExampleSys").

--require-quotes (with --check-quotes) also fails a finding whose evidence has no
double-quoted span of 12+ characters, unless its locus starts with "absence:".

Exit: 0 valid, 1 invalid, 2 internal error.
"""

import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata

from paper_config import load

SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finding_schema.json")


def finding_id(file, line, locus, lens=None):
    # lens is deliberately NOT in the identity: the same defect found by two
    # lenses must dedup to one finding.
    return hashlib.sha1(f"{file}:{line}:{locus}".encode()).hexdigest()


def validate(data, schema):
    errs = []
    if not isinstance(data, list):
        return [
            "top level must be an ARRAY of findings, not an object "
            '(reports are arrays, not {"findings": [...]} wrappers)'
        ]
    req = schema["required"]
    props = schema["properties"]
    seen = {}
    for i, f in enumerate(data):
        w = f"findings[{i}]"
        if not isinstance(f, dict):
            errs.append(f"{w}: not an object")
            continue
        for k in req:
            if k not in f:
                errs.append(f"{w}: missing required field '{k}'")
        for k in f:
            if k not in props:
                errs.append(f"{w}: unknown field '{k}' (additionalProperties: false)")
        for k, v in f.items():
            spec = props.get(k)
            if not spec:
                continue
            if "enum" in spec and v not in spec["enum"]:
                errs.append(f"{w}.{k}: {v!r} not in {spec['enum']}")
            t = spec.get("type")
            # NB: isinstance(True, int) is True in Python; JSON Schema treats
            # boolean and integer as distinct types.
            if t == "integer" and (isinstance(v, bool) or not isinstance(v, int)):
                errs.append(f"{w}.{k}: must be integer (boolean is not)")
            if t == "string" and not isinstance(v, str):
                errs.append(f"{w}.{k}: must be string")
            if t == "boolean" and not isinstance(v, bool):
                errs.append(f"{w}.{k}: must be boolean")
            if t == "array" and not isinstance(v, list):
                errs.append(f"{w}.{k}: must be array")
            if (
                t == "array"
                and isinstance(v, list)
                and spec.get("items", {}).get("type") == "string"
                and not all(isinstance(x, str) for x in v)
            ):
                errs.append(f"{w}.{k}: every item must be string")
            if "pattern" in spec and isinstance(v, str) and not re.fullmatch(spec["pattern"], v):
                errs.append(f"{w}.{k}: {v!r} does not match {spec['pattern']}")
            if (
                "minimum" in spec
                and isinstance(v, int)
                and not isinstance(v, bool)
                and v < spec["minimum"]
            ):
                errs.append(f"{w}.{k}: below minimum {spec['minimum']}")
        # id must be reproducible from its own coordinates. Guard on type:
        # a non-string id already failed the type check above, and slicing or
        # hashing it here would crash the validator instead of reporting.
        if isinstance(f.get("id"), str):
            if all(k in f for k in ("file", "line", "locus")):
                want = finding_id(f["file"], f["line"], f["locus"])
                if f["id"] != want:
                    errs.append(f"{w}.id: {f['id'][:12]}… != sha1(file:line:locus) {want[:12]}…")
            if f["id"] in seen:
                errs.append(f"{w}.id: duplicate of findings[{seen[f['id']]}]")
            seen[f["id"]] = i
    return errs


QUOTE_MIN = 12  # shorter quoted spans are terms, not quotations
ELISION = re.compile(r"\s*(?:\[(?:\.\.\.|\u2026)\]|\.\.\.|\u2026)\s*")
ELISION_WINDOW = 1500  # characters allowed between two fragments of one elided quotation
PATHLIKE = re.compile(
    r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:tex|qmd|md|rmd|R|r|py|do|jl|bib|txt|csv|html|yml|yaml|json|pdf))(?::\d+)?"
)
_UNIFY = str.maketrans(
    {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
    }
)


def extract_quotes(evidence):
    """Double-quoted spans of QUOTE_MIN+ characters, read left to right.

    Every pair of straight quotes is consumed whatever its length, so a short quoted
    term cannot shift the pairing onto the prose between two quotations. Code in
    backticks outside a quotation is skipped; backticks inside one belong to it.
    """
    out, i, n = [], 0, len(evidence)
    while i < n:
        c = evidence[i]
        if c == "`":
            tick = re.match(r"`+", evidence[i:]).group(0)
            end = evidence.find(tick, i + len(tick))
            i = n if end < 0 else end + len(tick)
        elif c in '"\u201c':
            end = evidence.find('"' if c == '"' else "\u201d", i + 1)
            if end < 0:
                break
            if end - i - 1 >= QUOTE_MIN:
                out.append(evidence[i + 1 : end])
            i = end + 1
        else:
            i += 1
    return out


_SMALLCAPS = ()  # P4: (pattern, name) pairs; check_quotes fills it from paper.smallcaps_names


def _smallcaps(names):
    """P4: for each name, a pattern for its casefolded form with one optional space between
    two letters ("e xample s ys"), paired with the casefolded name it maps back to."""
    out = []
    for name in names:
        name = unicodedata.normalize("NFKC", name).translate(_UNIFY).casefold()
        body = "".join(
            re.escape(c) + (" ?" if c.isalpha() and nxt.isalpha() else "")
            for c, nxt in zip(name, name[1:] + " ")
        )
        out.append((re.compile(rf"(?<!\w){body}(?!\w)"), name.replace("\\", "\\\\")))
    return tuple(out)


def _norm(text, latex, dehyphen, quote=False):
    """dehyphen: 0 leave line-end hyphens, 1 join keeping the hyphen (well-known),
    2 join dropping it (a word broken by hyphenation: statis-tics)."""
    t = unicodedata.normalize("NFKC", text).translate(_UNIFY)
    if dehyphen:
        t = re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1-\2" if dehyphen == 1 else r"\1\2", t)
    if latex:
        if not quote:
            t = re.sub(r"(?<!\\)%.*", "", t)  # comments: the file's, never the quote's
        t = t.replace("\\%", "%").replace("``", '"').replace("''", '"')
        t = re.sub(r"\\\\|\\ ", " ", t)  # forced line break, control space
        t = re.sub(r"-{2,3}", "-", t)  # -- and --- are dashes
        t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)  # command names; arguments stay
        t = re.sub(r"[{}$~]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().casefold()
    for split, name in _SMALLCAPS:  # P4: small caps as pdftotext extracts them
        t = split.sub(name, t)
    return t


def _in_order(frags, hay):
    """Every fragment occurs in order, each within ELISION_WINDOW of the one before."""
    start = hay.find(frags[0])
    while start >= 0:
        pos, ok = start + len(frags[0]), True
        for f in frags[1:]:
            nxt = hay.find(f, pos)
            if nxt < 0 or nxt - pos > ELISION_WINDOW:
                ok = False
                break
            pos = nxt + len(f)
        if ok:
            return True
        start = hay.find(frags[0], start + 1)
    return False


def _found(quote, views):
    r"""True if the quotation occurs in one normalised view of the text.

    A quote containing a backslash was copied from source, so it must match the source
    as written: stripping LaTeX commands would let \hat\alpha stand in for \hat\beta.
    """
    for latex in (False,) if "\\" in quote else (False, True):
        frags = [_norm(f, latex, 0, quote=True) for f in ELISION.split(quote) if f.strip()]
        if frags and any(_in_order(frags, views[(latex, d)]) for d in (0, 1, 2)):
            return True
    return False


def _near_line(quote, txt, line):
    """P9: the quote's first 40 normalised characters occur within 3 lines of `line`."""
    window = "\n".join(txt.splitlines()[max(0, line - 4) : line + 5])
    first = next(f for f in ELISION.split(quote) if f.strip())
    for latex in (False,) if "\\" in quote else (False, True):
        head = _norm(first, latex, 0, quote=True)[:40]
        if any(head in _norm(window, latex, d) for d in (0, 1, 2)):
            return True
    return False


def load_text(path):
    """(text, None), or (None, why) when the file cannot be read as text."""
    if path.lower().endswith(".pdf"):
        try:
            r = subprocess.run(
                ["pdftotext", "-q", path, "-"], capture_output=True, text=True, timeout=60
            )
        except (OSError, subprocess.TimeoutExpired):
            return None, "a PDF, and pdftotext (poppler) is not available to read it"
        return (
            (r.stdout, None) if r.returncode == 0 else (None, "a PDF that pdftotext could not read")
        )
    try:
        raw = open(path, "rb").read()
    except OSError:
        return None, "missing"
    if b"\x00" in raw[:8192]:
        return None, "a binary file"
    return raw.decode("utf-8", "replace"), None


def check_quotes(args):
    root = os.getcwd()
    require = "--require-quotes" in args
    args = [a for a in args if a != "--require-quotes"]
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            print(
                "usage: --check-quotes [--require-quotes] REPORT.json [--root DIR]", file=sys.stderr
            )
            return 2
        root = args[i + 1]
        args = args[:i] + args[i + 2 :]
    try:
        data = json.loads(open(args[0]).read() if args else sys.stdin.read())
    except Exception as e:
        print(f"validate-findings: cannot read findings: {e}", file=sys.stderr)
        return 2
    if not isinstance(data, list):
        print("validate-findings: findings must be a JSON array", file=sys.stderr)
        return 2
    global _SMALLCAPS
    _SMALLCAPS = _smallcaps(load()["paper"]["smallcaps_names"])  # once, before any _norm
    cache = {}

    def text_of(rel):
        path = os.path.join(root, rel)
        if path not in cache:
            txt, why = load_text(path)
            if txt is not None and path.lower().endswith(".tex"):
                txt = re.sub(r"(?<!\\)%.*", "", txt)  # P3: a comment is not the paper's text
            cache[path] = (
                txt,
                why,
                None
                if txt is None
                else {
                    (latex, d): _norm(txt, latex, d) for latex in (False, True) for d in (0, 1, 2)
                },
            )
        return cache[path]

    misses, unchecked, checked = [], [], 0
    for i, f in enumerate(data):
        if not isinstance(f, dict) or not isinstance(f.get("evidence"), str):
            continue
        quotes = extract_quotes(f["evidence"])
        where = f"findings[{i}] ({f.get('file')}:{f.get('line')}, {f.get('locus', '')})"
        if not quotes:
            if require and not str(f.get("locus", "")).startswith("absence:"):
                misses.append(
                    f"{where}: evidence has no double-quoted span of {QUOTE_MIN}+ "
                    "characters, and the locus does not start with 'absence:'"
                )
            continue
        own = str(f.get("file", ""))
        txt, why, _ = text_of(own)
        if why == "missing":
            misses.append(f"{where}: cannot check {len(quotes)} quote(s) - file not found: {own}")
            continue
        sources = [own]  # P8: for this review, quotes must come from `file` only
        readable = [text_of(src) for src in sources if text_of(src)[0] is not None]
        if not readable:
            unchecked.append(f"{where}: {len(quotes)} quote(s) left unchecked - {own} is {why}")
            continue
        line = f.get("line")
        for k, q in enumerate(quotes):
            checked += 1
            if any(_found(q, views) for _, _, views in readable):
                if (
                    k == 0
                    and isinstance(line, int)
                    and not isinstance(line, bool)
                    and not _near_line(q, txt, line)
                ):
                    misses.append(f"{where}: quote not within 3 lines of line {line}")
                continue
            lines = [ln.strip() for ln in (txt or readable[0][0]).splitlines() if ln.strip()]
            near = difflib.get_close_matches(q, lines, n=1, cutoff=0.55)  # P5: was 0.0
            misses.append(
                f'{where}: quote not in {" or ".join(sources)}: "{q}"'
                + (f'\n      closest line: "{near[0][:160]}"' if near else "")
            )
    for u in unchecked:
        print(f"  unchecked: {u}")
    if misses:
        print(
            f"validate-findings: {len(misses)} quotation problem(s) - a quote must be the file's own text"
        )
        for m in misses:
            print(f"  {m}")
        return 1
    print(
        f"validate-findings: quotes OK ({checked} quote(s) checked"
        + (f"; {len(unchecked)} finding(s) with quotes left unchecked" if unchecked else "")
        + ")"
    )
    return 0


def main():
    a = sys.argv[1:]
    if a and a[0] == "--check-quotes":
        return check_quotes(a[1:])
    if a and a[0] == "--id":
        if len(a) not in (4, 5):
            print("usage: --id FILE LINE LOCUS", file=sys.stderr)
            return 2
        print(finding_id(a[1], a[2], a[3]))
        return 0
    fill = bool(a) and a[0] == "--fill-ids"
    if fill:
        a = a[1:]
    try:
        schema = json.load(open(SCHEMA))
    except Exception as e:
        print(f"validate-findings: cannot read schema: {e}", file=sys.stderr)
        return 2
    try:
        raw = open(a[0]).read() if a else sys.stdin.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"validate-findings: invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"validate-findings: cannot read input: {e}", file=sys.stderr)
        return 2
    if fill and isinstance(data, list):
        for f in data:
            if isinstance(f, dict) and all(k in f for k in ("file", "line", "locus")):
                f["id"] = finding_id(f["file"], f["line"], f["locus"])
    errs = validate(data, schema)
    out = sys.stderr if fill else sys.stdout
    if errs:
        print(f"validate-findings: {len(errs)} error(s)", file=out)
        for e in errs:
            print(f"  {e}", file=out)
        return 1
    if fill:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"validate-findings: OK ({len(data)} finding(s), ids filled)", file=sys.stderr)
        return 0
    print(f"validate-findings: OK ({len(data)} finding(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
