#!/usr/bin/env python3
# Idea only, no text copied: read the pdfinfo Author field and list rasters with pdfimages -list,
# as sohan-shingade/paper-reviewer scripts/extract_pdf.sh:38,44 does (commit 6a5c484, no license).
r"""Scan the built paper for anything that discloses the authors (double-anonymous review).

A double-anonymous venue asks that the submission name no author or affiliation and not
otherwise disclose who the authors are.

    paper-tool anonymity_scan                  # build.pdf and paper.figures_dir of the config
    paper-tool anonymity_scan --text main.txt --figures DIR
    paper-tool anonymity_scan --baseline anonymity_baseline.txt   # known hits do not fail

Terms:
- the citation file (paper.citation_cff, default CITATION.cff), read at run time: each author's
  family name, each given name of 4 or more letters ("Le", "Tom", "Gal" alone match ordinary
  words; their family names still match), each affiliation whole and each comma-separated part
  of it.
- the terms file (terms.anonymity; keep it private, it names real people): one "<kind>: <term>"
  per line, kinds affiliation, lab, org, host, path, url, title, arxiv, phrase, venue, system.
A missing citation file or terms file named by the config gives no terms from it, with a note;
a file named by --citation or --terms must exist, and the scan stops when it has no term at all.
Matching ignores case. Line breaks may fall between the words of a term, and inside URLs and
paths after "/", ".", "_", ":" and "-". Except for hosts, paths, URLs and the arXiv id, a single
space may split a word, as pdftotext prints small caps ("E XAMPLE S YS").

Scanned:
- the PDF text (pdftotext; with --text, the given dump, a form feed after each page);
- the PDF metadata: a non-empty pdfinfo Author field is a hit; Title, Subject, Keywords and any
  XMP stream (pdfinfo -meta) are scanned for terms;
- the raster images inside each PDF (pdfimages -list): listed, not scanned;
- every file under --figures (default paper.figures_dir; "" in the config skips it with a
  note): a PDF as above; a raster file listed, not scanned; any other file (TikZ, draw.io
  source) scanned as text, its matches notes, since source text does not render.

Classes:
- HIT: an author name or the earlier venue outside a third-person citation; any affiliation,
  lab, organisation, host, path, URL, arXiv title or id, or self-revealing phrase, anywhere, the
  references included.
- NOTE: an author name followed by "et al.", or an author name or the earlier venue inside the
  references section (from the references heading to the end: a cited paper's authors, venue or
  proceedings URL); the system name (a note, not a hit); rasters;
  figure-source matches. A match inside a longer match (the system name inside the title) is
  reported once, as the longer one, unless it is a hit inside a note.

Baseline (--baseline FILE, default terms.anonymity_baseline when that file exists): one known
hit per line: its identity "<kind>: <term>" (the term as the terms list holds it, not the
matched text or its line; kind "name" for an author name; "metadata: Author" for a filled
Author field), a tab, and the id of the owner decision or ticket that keeps it. Blank lines and
lines starting with "#" are ignored. A hit whose identity is in the file prints as KNOWN with
that reason and does not fail; any other hit prints as HIT with its identity. A row without a
reason is a usage error.

Exit 0 with no hit (with --baseline, none outside it), 1 on any other hit, 2 on a usage or tool
error.
Needs paper_limits.py and paper_config.py (same directory): the text loader, the heading test
and the config.
"""

import argparse
import bisect
import re
import sys
from pathlib import Path

from paper_config import load
from paper_limits import REFS, die, is_heading, load_text, page_count, run_tool, show, shown

HIT_KINDS = set("affiliation lab org host path url title arxiv phrase venue".split())
FILE_KINDS = HIT_KINDS | {"system"}
STRICT = {"host", "path", "url", "arxiv"}  # no small-caps splits inside words
RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
ET_AL = re.compile(r"[\s,]*et\s*al\b", re.I)
SYSTEM_WHY = "system name (a note, not a hit)"


def parse_cff(path):
    """(people as (given, family), affiliations) from every `authors:` list in CITATION.cff.
    Reads the YAML subset the Citation File Format uses: block lists of `key: value` maps."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        die(f"cannot read {path}: {e}")
    entries, indent, cur = [], None, None
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        if re.match(r"authors:\s*$", s):
            indent, cur = ind, None
            continue
        if indent is None:
            continue
        if ind < indent or (ind == indent and not s.startswith("-")):
            indent = cur = None
            continue
        if s.startswith("-"):
            cur = {}
            entries.append(cur)
            s = s[1:].strip()
        m = re.match(r"(given-names|family-names|name-particle|name|affiliation):\s*(.+)$", s)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip().strip("\"'")
    people, affs = [], []
    for e in entries:
        family = " ".join(x for x in (e.get("name-particle"), e.get("family-names")) if x)
        person = (e.get("given-names", ""), family)
        if any(person) and person not in people:
            people.append(person)
        for org in (e.get("name"), e.get("affiliation")):  # `name` is an organisation author
            if org and org not in affs:
                affs.append(org)
    return people, affs


def term_regex(kind, term):
    loose = kind not in STRICT
    out = []
    for i, ch in enumerate(term):
        nxt = term[i + 1] if i + 1 < len(term) else ""
        if ch.isspace():
            if not out or out[-1] != r"\s+":
                out.append(r"\s+")
        elif ch == "-":
            out.append(r"(?:-\s*|\s+)?")
        elif ch in "/._:":
            out.append((r"\s?" if ch == ":" else "") + re.escape(ch) + r"\s*")
        else:
            out.append(re.escape(ch))
            if loose and ch.isalpha() and nxt.isalpha():
                out.append(" ?")
    lead = r"(?<![A-Za-z0-9])" if term[0].isalnum() else ""
    tail = r"(?![A-Za-z0-9])" if term[-1].isalnum() and kind != "path" else ""
    return re.compile(lead + "".join(out) + tail, re.I)


def build_terms(cff, terms_file):
    """[(kind, term, regex)] and a one-line account of where they came from; a source that is
    None gives no terms, and no term at all is a usage error."""
    people, affs = parse_cff(cff) if cff is not None else ([], [])
    if cff is not None and not people:
        die(f"no authors found in {cff}")
    pairs = []
    for given, family in people:
        pairs += [("name", family)] if family else []
        pairs += [("name", given)] if len(given) >= 4 else []
    for a in affs:
        parts = [p.strip() for p in a.split(",")]
        pairs += [("affiliation", a)] + [("affiliation", p) for p in parts if len(parts) > 1 and p]
    n_cff = len(pairs)
    lines = []
    if terms_file is not None:
        try:
            lines = Path(terms_file).read_text(encoding="utf-8").splitlines()
        except OSError as e:
            die(f"cannot read {terms_file}: {e}")
    for no, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        kind, sep, term = s.partition(":")
        kind, term = kind.strip(), term.strip()
        if not sep or kind not in FILE_KINDS or not term:
            die(f"{terms_file}:{no}: expected '<kind>: <term>' with kind in {sorted(FILE_KINDS)}")
        pairs.append((kind, term))
    seen, terms = set(), []
    for kind, term in pairs:
        if (kind, term.lower()) not in seen:
            seen.add((kind, term.lower()))
            terms.append((kind, term, term_regex(kind, term)))
    if not terms:
        die("no terms to scan for: name a citation file (paper.citation_cff) or a terms file")
    from_cff, from_file = "no citation file", "no terms file"
    if cff is not None:
        from_cff = f"{len(people)} authors and {len(affs)} affiliations ({n_cff} terms) from "
        from_cff += shown(cff)
    if terms_file is not None:
        from_file = f"{len(terms) - n_cff} terms from {shown(terms_file)}"
    return terms, f"{from_cff}; {from_file}"


def refs_offset(raw):
    """Character offset of the last references heading line, or None. The last one wins: a lone
    "References" in the body (a table header) must not turn later names into notes."""
    pos, found = 0, None
    for line in raw.split("\n"):
        if is_heading(line.replace("\f", ""), REFS):
            found = pos
        pos += len(line) + 1
    return found


def load_baseline(path):
    """{identity: reason} from a baseline file (see the module docstring)."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        die(f"cannot read {path}: {e}")
    rows = {}
    for no, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        ident, _, reason = line.partition("\t")
        if not ident.strip() or not reason.strip():
            die(
                f"{path}:{no}: baseline row has no reason: expected '<kind>: <term>', a tab, "
                "and the owner decision or ticket that keeps it"
            )
        rows[ident.strip()] = reason.strip()
    return rows


def scan_text(raw, terms, refs_at=None, source=False):
    """[(start, end, cls, why, matched, identity)] for every term match in raw, nested matches
    merged; the identity "<kind>: <term>" is what a baseline row names."""
    found = []
    for kind, term, rx in terms:
        for m in rx.finditer(raw):
            if kind == "system":
                cls, why = "NOTE", SYSTEM_WHY
            elif source:
                cls, why = "NOTE", f"{kind} in a figure source (source text does not render)"
            elif kind in ("name", "venue") and refs_at is not None and m.start() >= refs_at:
                what = "author name" if kind == "name" else "venue"
                cls, why = "NOTE", f"{what} in the references (third-person citation)"
            elif kind == "name" and ET_AL.match(raw, m.end()):
                cls, why = "NOTE", "author name followed by et al. (third-person citation)"
            else:
                cls, why = "HIT", "author name" if kind == "name" else kind
            found.append((m.start(), m.end(), cls, why, m.group(0), f"{kind}: {term}"))
    found.sort(key=lambda f: (f[0], f[0] - f[1]))
    kept = []
    for f in found:
        inside = [k for k in kept if k[0] <= f[0] and f[1] <= k[1]]
        if not any(k[2] == "HIT" or f[2] == "NOTE" for k in inside):
            kept.append(f)
    return kept


class Report:
    def __init__(self, baseline=None):
        self.hits = self.notes = self.known = 0
        self.baseline = baseline  # {identity: reason} with --baseline, else None

    def emit(self, cls, why, where, matched=None, context=None, ident=None):
        if cls == "HIT" and self.baseline is not None and ident in self.baseline:
            cls = "KNOWN"
        if cls == "HIT":
            self.hits += 1
        elif cls == "KNOWN":
            self.known += 1
        else:
            self.notes += 1
        tail = f': "{show(matched)}"' if matched is not None else ""
        if context is not None and show(context) != show(matched or ""):
            tail += f' in "{show(context, 140)}"'
        if cls == "KNOWN":
            tail += f" (baseline: {self.baseline[ident]})"
        elif cls == "HIT" and self.baseline is not None:
            tail += f' (not in the baseline; identity "{ident}")'
        print(f"{cls} {why}: {where}{tail}")

    def text_findings(self, label, raw, found, paged=True):
        """Print findings as file:line, with (page n) when raw is a paged dump, and 40 characters
        of context on each side within the match's lines; system-name notes one line per file."""
        nl = [i for i, c in enumerate(raw) if c == "\n"]
        ff = [i for i, c in enumerate(raw) if c == "\f"]
        system = []
        for start, end, cls, why, matched, ident in found:
            line = bisect.bisect_left(nl, start) + 1
            if why == SYSTEM_WHY:
                system.append(line)
                continue
            first = raw.rfind("\n", 0, start) + 1
            stop = raw.find("\n", end) % (len(raw) + 1)  # -1 (no newline) becomes len(raw)
            a, b = max(first, start - 40), min(stop, end + 40)
            ctx = ("..." if a > first else "") + raw[a:b] + ("..." if b < stop else "")
            where = f"{label}:{line}" + (
                f" (page {bisect.bisect_left(ff, start) + 1})" if paged else ""
            )
            self.emit(cls, why, where, matched, ctx.replace("\f", ""), ident)
        if system:
            lines = ", ".join(str(n) for n in sorted(set(system)))
            self.emit("NOTE", SYSTEM_WHY, f"{label}: {len(system)} occurrence(s), lines {lines}")


def pdf_info(pdf):
    fields = {}
    for line in run_tool(["pdfinfo", "-enc", "UTF-8", str(pdf)]).splitlines():
        key, sep, val = line.partition(":")
        if sep:
            fields.setdefault(key.strip(), val.strip())
    return fields


def raster_pages(pdf):
    """Page of each raster image in the PDF (pdfimages -list rows of type "image")."""
    rows = run_tool(["pdfimages", "-list", str(pdf)]).splitlines()[2:]
    return [int(c[0]) for c in (r.split() for r in rows) if len(c) > 2 and c[2] == "image"]


def scan_pdf(pdf, terms, rep, figure=False):
    label = shown(pdf)
    raw = load_text(pdf=pdf)
    refs_at = None if figure else refs_offset(raw)
    rep.text_findings(label, raw, scan_text(raw, terms, refs_at))
    info = pdf_info(pdf)
    if info.get("Author"):
        where, author = f"{label} metadata Author", info["Author"]
        rep.emit("HIT", "metadata Author is not empty", where, author, ident="metadata: Author")
    for field in ("Title", "Subject", "Keywords"):
        for _, _, cls, why, matched, ident in scan_text(info.get(field, ""), terms):
            rep.emit(cls, why, f"{label} metadata {field}", matched, info[field], ident)
    xmp = run_tool(["pdfinfo", "-meta", str(pdf)])
    if xmp.strip():
        rep.text_findings(f"{label} XMP metadata", xmp, scan_text(xmp, terms), paged=False)
    pages = raster_pages(pdf)
    if pages:
        where = f"{label} pages {', '.join(str(p) for p in sorted(set(pages)))}"
        rep.emit("NOTE", f"{len(pages)} raster image(s) not scanned", where)
    refs = "none" if refs_at is None else f"line {raw[:refs_at].count(chr(10)) + 1}"
    filled = [f for f in ("Author", "Title", "Subject", "Keywords") if info.get(f)]
    print(
        f"SCANNED {label}: text of {page_count(raw)} page(s) "
        f"(references heading: {refs}); metadata fields set: {', '.join(filled) or 'none'}; "
        f"XMP: {'scanned' if xmp.strip() else 'none'}; raster images: {len(pages)}"
    )


def scan_figures(root, terms, rep):
    files = sorted(p for p in Path(root).rglob("*") if p.is_file() and not p.name.startswith("."))
    counts = {"PDF": 0, "raster": 0, "source": 0, "binary": 0}
    for f in files:
        ext = f.suffix.lower()
        if ext == ".pdf":
            counts["PDF"] += 1
            scan_pdf(f, terms, rep, figure=True)
        elif ext in RASTER:
            counts["raster"] += 1
            rep.emit("NOTE", "raster image not scanned", shown(f))
        else:
            try:
                raw = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                counts["binary"] += 1
                rep.emit("NOTE", "binary file not scanned", shown(f))
                continue
            counts["source"] += 1
            rep.text_findings(shown(f), raw, scan_text(raw, terms, source=True), paged=False)
    summary = ", ".join(f"{n} {k}" for k, n in counts.items())
    print(f"SCANNED {shown(root)}: {len(files)} file(s): {summary}")


def config_file(flag, value, key, why, notes):
    """The file a flag names; else the config's file when it exists, else None and a note."""
    if flag is not None:
        return flag
    if value is not None and value.is_file():
        return value
    notes.append((why, f"{key} ({'empty' if value is None else f'no file at {shown(value)}'})"))
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Double-anonymous scan of the built paper.")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--pdf", type=Path, help="built PDF (default: build.pdf in paper-tools.toml)")
    src.add_argument("--text", type=Path, help="text dump with a form feed after each page")
    ap.add_argument(
        "--citation",
        type=Path,
        help="citation file (default: paper.citation_cff in paper-tools.toml)",
    )
    ap.add_argument("--terms", type=Path, help="terms file (default: terms.anonymity)")
    ap.add_argument("--figures", type=Path, help="figures folder (default: paper.figures_dir)")
    ap.add_argument(
        "--baseline",
        type=Path,
        help="known hits, one per line (see the docstring; default: terms.anonymity_baseline)",
    )
    args = ap.parse_args(argv)
    cfg = load()
    figures = args.figures if args.figures is not None else cfg["paper"]["figures_dir"]
    if figures is not None and not figures.is_dir():
        die(f'no figures directory at {figures} (paper.figures_dir; "" for none)')
    notes = []
    citation = config_file(
        args.citation,
        cfg["paper"]["citation_cff"],
        "paper.citation_cff",
        "no citation file, so no author or affiliation terms",
        notes,
    )
    terms_file = config_file(
        args.terms, cfg["terms"]["anonymity"], "terms.anonymity", "no terms file", notes
    )
    baseline_file = config_file(
        args.baseline,
        cfg["terms"]["anonymity_baseline"],
        "terms.anonymity_baseline",
        "no baseline, so every hit fails",
        notes,
    )

    baseline = load_baseline(baseline_file) if baseline_file else None
    rep = Report(baseline)
    for why, where in notes:
        rep.emit("NOTE", why, where)
    terms, account = build_terms(citation, terms_file)
    print(f"anonymity_scan: terms: {account}")
    if args.text:
        raw = load_text(text=args.text)
        refs_at = refs_offset(raw)
        rep.text_findings(shown(args.text), raw, scan_text(raw, terms, refs_at))
        refs = "none" if refs_at is None else f"line {raw[:refs_at].count(chr(10)) + 1}"
        print(
            f"SCANNED {shown(args.text)}: text (references heading: {refs}); no metadata (--text)"
        )
    else:
        pdf = args.pdf or cfg["build"]["pdf"]
        if pdf is None:
            die("no PDF: pass --pdf or --text, or set build.pdf in paper-tools.toml")
        scan_pdf(pdf, terms, rep)
    if figures is None:
        rep.emit("NOTE", "figures not scanned", "paper.figures_dir (empty)")
    else:
        scan_figures(figures, terms, rep)
    code = 1 if rep.hits else 0
    hits = f"{rep.hits} hit(s)"
    if baseline is not None:
        hits = f"{rep.hits} new hit(s), {rep.known} known hit(s) from {shown(baseline_file)}"
    print(f"anonymity_scan: {hits}, {rep.notes} note(s); exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
