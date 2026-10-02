#!/usr/bin/env python3
r"""Index the literature already saved in the project, for agents/citation-finder.md.

Usage (from the project root):
  lit_index.py [--bib FILE] [--main FILE]
               [--notes FILE[::HEADING] ...] [--self-name NAME ...] [--out PATH]
               [--search WORDS [--top N]]
  lit_index.py --sentences [--main FILE] [--sections DIR]
               [--only GLOB ...]
Defaults come from paper-tools.toml: --bib paper.bib, --main paper.main_tex, --notes
literature.notes, --self-name literature.self_names, --sections paper.sections_dir.

Index mode (the default):
- reads every entry of --bib and marks the keys the build cites, following \input from
  --main exactly as cite_check.py does (its parser and scanner are imported, not copied);
- reads every paper named in the --notes files: a row of a Markdown table that has a
  "Paper" or "Work" column, a list item that holds a DOI or an arXiv id, and a bib-key
  token (a key of --bib anywhere in a line, or a key-shaped token such as `Kaizen2026`
  inside backticks or quotes). FILE::HEADING reads only the section under the first
  heading whose text starts with HEADING (for example "## 8."), up to the next heading of
  the same or a higher level;
- groups the records into papers by DOI, arXiv id, normalized title, or normalized short
  name (a title's part before ":" of at most three words, a bib key without its year, the
  name in a notes table cell);
- marks a paper self_citation when a --self-name (repeatable; any one replaces the list
  literature.self_names: this paper's names and preprint id and the authors' prior works)
  equals one of its bib keys or arXiv ids, or is part of its title or a name; self_match
  lists the names that matched;
- writes one JSON file to --out (default $TMPDIR/lit_index.json) and prints a summary.
--search WORDS also prints the papers whose text holds the most of the words, best first.
No network is used.

Sentences mode prints every sentence of the build files under --sections, in build order,
as FILE:LINE<TAB>cite|nocite<TAB>TEXT, with % comments dropped and tabular, tikzpicture,
equation, align and verbatim bodies skipped; LINE is where the sentence starts. --only
limits it to files matching a glob. The last line gives the counts.

Exit 0 on success, 2 on a usage or input error.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cite_check as cc  # noqa: E402
from paper_config import load  # noqa: E402

ARXIV_ID = r"\d{4}\.\d{4,5}(?:v\d+)?"
ARXIV_TEXT = re.compile(r"(?:arxiv\.org/(?:abs|pdf|html)/|\barxiv[:.]?\s*)(" + ARXIV_ID + ")", re.I)
DOI_TEXT = re.compile(r"(?<![\w.])(10\.\d{4,9}/[^\s\"'<>|()\[\]]+)")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]*)\)")
QUOTED = re.compile(r"[\"\u201c]([^\"\u201d]{8,})[\"\u201d]")
KEY_QUOTED = re.compile(r"[`'\"]([A-Za-z][A-Za-z0-9-]*?(?:19|20)\d{2}[A-Za-z]?)[`'\"]")
YEAR_TAIL = re.compile(r"(?:19|20)\d{2}[A-Za-z]?$")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
SEPARATOR = re.compile(r"^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?$")
HEADING_MD = re.compile(r"^(#{1,6})\s")


# ---------------------------------------------------------------- small helpers
def plain(text):
    """Markdown cell text without links' URLs, bold marks or backticks."""
    return " ".join(LINK.sub(r"\1", text).replace("**", "").replace("`", "").split())


def name_norm(text):
    return cc.norm_title(text.replace("→", " to ")).replace(" ", "")


def arxiv_base(aid):
    return re.sub(r"v\d+$", "", aid)


def ids_in(text):
    """(DOIs, arXiv ids) found in raw text; an arXiv DOI counts as its arXiv id."""
    dois, aids = [], []
    for raw in DOI_TEXT.findall(text):
        doi = re.sub(r"[?#].*", "", raw).rstrip(".,;:")  # a URL's query or fragment is not the DOI
        match = re.match(r"10\.48550/arxiv\.(" + ARXIV_ID + ")$", doi, re.I)
        if match:
            aids.append(arxiv_base(match.group(1)))
        elif doi.lower() not in dois:
            dois.append(doi.lower())
    for aid in ARXIV_TEXT.findall(text):
        if arxiv_base(aid) not in aids:
            aids.append(arxiv_base(aid))
    return dois, aids


def split_top(text, sep=";"):
    """Split on sep outside parentheses and brackets."""
    parts, buf, depth = [], [], 0
    for char in text:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        if char == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    parts.append("".join(buf))
    return [part for part in parts if part.strip()]


def cell_papers(segment):
    """Papers named by one segment of a Paper cell: list of (names, title, paren_text)."""
    text = plain(segment)
    quoted = QUOTED.search(text)
    title = quoted.group(1).strip() if quoted else ""
    paren = re.search(r"\(([^()]*)\)", text)
    paren_text = paren.group(1).strip() if paren else ""
    head = re.split(r"[(\"\u201c]", text, maxsplit=1)[0].strip().rstrip(",").strip()
    pieces = [piece.strip() for piece in head.split(",")]
    if not title and len(pieces) > 1 and all(piece and " " not in piece for piece in pieces):
        return [([piece], "", paren_text) for piece in pieces]  # "TRACE, RepoTransBench"
    names = [name.strip() for name in head.split(" / ") if name.strip()]
    return [(names, title, paren_text)]


# ---------------------------------------------------------------- inputs
def read_notes(spec):
    """Return (path, [(line_number, text)]) for FILE or FILE::HEADING."""
    path, _, heading = spec.partition("::")
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    numbered = list(enumerate(lines, 1))
    if not heading:
        return path, numbered
    start = next((i for i, line in numbered if line.startswith(heading)), None)
    if start is None:
        raise ValueError(f"{path}: no heading starts with {heading!r}")
    level = len(HEADING_MD.match(lines[start - 1]).group(1))
    out = []
    for number, line in numbered[start - 1 :]:
        found = HEADING_MD.match(line)
        if out and found and len(found.group(1)) <= level:
            break
        out.append((number, line))
    return path, out


def scan_build(main):
    """cite_check's TexScan run from main, honouring its \\input@path."""
    with open(main, encoding="utf-8") as handle:
        text = "\n".join(cc.strip_comment(line) for line in handle.read().splitlines())
    cwd = os.path.dirname(main) or "."
    found = cc.INPUT_PATH.search(text)
    search = (
        [os.path.join(cwd, p) for p in re.findall(r"\{([^{}]*)\}", found.group(1))] if found else []
    )
    scan = cc.TexScan(cwd, search)
    scan.scan(main)
    return scan


def bib_records(bib_path, scan):
    with open(bib_path, encoding="utf-8") as handle:
        entries, errors = cc.parse_bib(handle.read())
    records = []
    for entry in entries:
        fields = entry["fields"]
        doi = cc.norm_doi(fields.get("doi", "")) or ""
        if not doi and cc.DOI_PREFIX.match(fields.get("url", "")):
            doi = cc.norm_doi(fields["url"]) or ""
        if not doi:  # a publisher URL that holds the DOI, such as dl.acm.org/doi/10.1145/...
            doi = next(iter(ids_in(fields.get("url", ""))[0]), "")
        aids = [arxiv_base(a) for a in cc.arxiv_ids(fields)]
        match = re.match(r"10\.48550/arxiv\.(" + ARXIV_ID + ")$", doi, re.I)
        if match:
            aids = aids or [arxiv_base(match.group(1))]
            doi = ""
        venues = [fields[n] for n in cc.VENUE_FIELDS if fields.get(n, "").strip()]
        peer = [v for v in venues if not cc.PREPRINT.search(v)]
        arxiv_evidence = (
            bool(aids)
            or fields.get("archiveprefix", "").strip().lower() == "arxiv"
            or any(cc.ARXIV_WORD.search(v) for v in venues)
        )
        title = re.sub(r"[{}]", "", fields.get("title", "")).strip()
        stem = YEAR_TAIL.sub("", entry["key"])
        names = [stem]
        prefix = title.split(":", 1)[0] if ":" in title else ""
        if prefix and len(prefix.split()) <= 3:
            names.append(prefix)
        places = sorted({f"{os.path.normpath(p)}:{n}" for p, n in scan.cites.get(entry["key"], [])})
        records.append(
            {
                "kind": "bib",
                "key": entry["key"],
                "type": entry["type"],
                "line": entry["line"],
                "title": title,
                "authors": " ".join(re.sub(r"[{}]", "", fields.get("author", "")).split()),
                "year": fields.get("year", "").strip(),
                "venue": " ".join(re.sub(r"[{}]", "", (peer or venues or [""])[0]).split()),
                "doi": doi.lower(),
                "arxiv": aids,
                "url": fields.get("url", "").strip(),
                "arxiv_only": arxiv_evidence and not peer,
                "cited_in_build": bool(places) or "*" in scan.cites,
                "cite_locations": places,
                "names": names,
            }
        )
    return records, errors


def note_records(path, lines, bib_keys):
    """Mentions of papers in one notes file (or one section of it)."""
    records, header, cols, seen_keys = [], None, {}, set()
    key_re = (
        re.compile(
            r"(?<![A-Za-z0-9])(" + "|".join(map(re.escape, sorted(bib_keys))) + r")(?![A-Za-z0-9])"
        )
        if bib_keys
        else None
    )
    for index, (number, line) in enumerate(lines):
        stripped = line.strip()
        nxt = lines[index + 1][1].strip() if index + 1 < len(lines) else ""
        if stripped.startswith("|") and SEPARATOR.match(nxt):
            header = [plain(c).lower() for c in stripped.strip("|").split("|")]
            cols = {
                "paper": next(
                    (i for i, c in enumerate(header) if re.match(r"(paper|work)\b", c)), None
                ),
                "venue": next((i for i, c in enumerate(header) if c.startswith("venue")), None),
                "url": [i for i, c in enumerate(header) if c.startswith("url")],
            }
        elif stripped.startswith("|") and SEPARATOR.match(stripped):
            pass
        elif stripped.startswith("|") and header is not None:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            paper_col = cols["paper"]
            if paper_col is not None and paper_col < len(cells) and plain(cells[paper_col]):
                url_text = " ".join(cells[i] for i in cols["url"] if i < len(cells))
                venue_cell = (
                    plain(cells[cols["venue"]])
                    if cols["venue"] is not None and cols["venue"] < len(cells)
                    else ""
                )
                segments = split_top(cells[paper_col])
                found = [(seg, paper) for seg in segments for paper in cell_papers(seg)]
                for seg, (names, title, paren_text) in found:
                    raw = seg + (" " + url_text if len(found) == 1 else "")
                    dois, aids = ids_in(raw)
                    records.append(
                        {
                            "kind": "table-row",
                            "file": path,
                            "line": number,
                            "names": names,
                            "title": title,
                            "venue": venue_cell or paren_text,
                            "doi": dois,
                            "arxiv": aids,
                            "text": plain(stripped.strip("|").replace("|", " ; ")),
                        }
                    )
        else:
            header = None if not stripped.startswith("|") else header
            if BULLET.match(line):
                dois, aids = ids_in(line)
                if dois or aids:
                    quoted = QUOTED.search(plain(line))
                    records.append(
                        {
                            "kind": "list-item",
                            "file": path,
                            "line": number,
                            "names": [],
                            "title": quoted.group(1).strip() if quoted else "",
                            "venue": "",
                            "doi": dois,
                            "arxiv": aids,
                            "text": plain(BULLET.sub("", line)),
                        }
                    )
        tokens = [m.group(1) for m in KEY_QUOTED.finditer(line)]
        tokens += [m.group(1) for m in key_re.finditer(line)] if key_re else []
        for token in tokens:
            if (number, token) in seen_keys:
                continue
            seen_keys.add((number, token))
            records.append(
                {
                    "kind": "key",
                    "file": path,
                    "line": number,
                    "key": token,
                    "names": [YEAR_TAIL.sub("", token)],
                    "title": "",
                    "venue": "",
                    "doi": [],
                    "arxiv": [],
                    "text": plain(line),
                }
            )
    return records


# ---------------------------------------------------------------- grouping
def link_tokens(record, bib_keys):
    tokens = []
    dois = [record["doi"]] if record["kind"] == "bib" and record["doi"] else []
    dois += record["doi"] if isinstance(record["doi"], list) else []
    tokens += [("doi", d.lower()) for d in dois]
    tokens += [("arxiv", a) for a in record["arxiv"]]
    title = cc.norm_title(record.get("title", ""))
    if len(title) >= 15:
        tokens.append(("title", title))
    if record["kind"] in ("bib", "key") and record.get("key") in bib_keys:
        tokens.append(("key", record["key"]))
    else:
        tokens += [("name", n) for n in map(name_norm, record["names"]) if len(n) >= 3]
    if record["kind"] == "bib":
        tokens += [("name", n) for n in map(name_norm, record["names"]) if len(n) >= 3]
    return tokens


def group(records, bib_keys):
    parent = list(range(len(records)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    owner, shared = {}, {}
    for index, record in enumerate(records):
        for token in set(link_tokens(record, bib_keys)):
            if token in owner:
                parent[find(index)] = find(owner[token])
                shared[token] = True
            else:
                owner[token] = index
    clusters = {}
    for index in range(len(records)):
        clusters.setdefault(find(index), []).append(index)
    out = []
    for members in clusters.values():
        types = set()
        for token, first in owner.items():
            if shared.get(token) and find(first) == find(members[0]):
                types.add(token[0])
        out.append(([records[i] for i in members], sorted(types)))
    return out


def paper_of(members, matched_by, self_names):
    bibs = sorted((r for r in members if r["kind"] == "bib"), key=lambda r: r["line"])
    notes = sorted((r for r in members if r["kind"] != "bib"), key=lambda r: (r["file"], r["line"]))
    names = []
    for record in bibs + notes:
        for name in record["names"]:
            if name and name not in names:
                names.append(name)
    first = bibs[0] if bibs else None
    title = first["title"] if first else next((r["title"] for r in notes if r["title"]), "")
    dois = [first["doi"]] if first and first["doi"] else []
    aids = list(first["arxiv"]) if first else []
    for record in notes:
        dois += [d for d in record["doi"] if d not in dois]
        aids += [a for a in record["arxiv"] if a not in aids]
    text = " ".join([title, *names]).lower()
    ids = {r["key"].lower() for r in bibs} | set(aids)
    self_match = [n for n in self_names if n and (n.lower() in ids or n.lower() in text)]
    return {
        "keys": [r["key"] for r in bibs],
        "has_bib_key": bool(bibs),
        "cited_in_build": any(r["cited_in_build"] for r in bibs),
        "title": title,
        "names": names,
        "authors": first["authors"] if first else "",
        "year": first["year"] if first else "",
        "venue": first["venue"] if first else next((r["venue"] for r in notes if r["venue"]), ""),
        "doi": dois,
        "arxiv": aids,
        "url": first["url"] if first else "",
        "arxiv_only": first["arxiv_only"] if first else None,
        "self_citation": bool(self_match),
        "self_match": self_match,
        "matched_by": matched_by,
        "bib": [
            {k: r[k] for k in ("key", "type", "line", "cited_in_build", "cite_locations")}
            for r in bibs
        ],
        "mentions": [
            {
                "file": r["file"],
                "line": r["line"],
                "kind": r["kind"],
                "name": ", ".join(r["names"]) or r["title"],
                "title": r["title"],
                "venue": r["venue"],
                "doi": r["doi"],
                "arxiv": r["arxiv"],
                "has_bib_key": bool(bibs),
                "text": r["text"],
            }
            for r in notes
        ],
    }


def build(args):
    scan = scan_build(args.main)
    bibs, errors = bib_records(args.bib, scan)
    bib_keys = {r["key"] for r in bibs}
    notes, specs = [], args.notes
    for spec in specs:
        path, lines = read_notes(spec)
        notes += note_records(path, lines, bib_keys)
    self_names = args.self_name
    papers = [paper_of(m, t, self_names) for m, t in group(bibs + notes, bib_keys)]
    papers.sort(
        key=lambda p: (
            not p["has_bib_key"],
            p["bib"][0]["line"] if p["bib"] else 0,
            min(((m["file"], m["line"]) for m in p["mentions"]), default=("", 0)),
        )
    )
    for number, paper in enumerate(papers, 1):
        paper["id"] = f"L{number:03d}"
    index = {
        "bib": args.bib,
        "main": args.main,
        "notes": specs,
        "self_names": self_names,
        "bib_errors": [f"{args.bib}:{line}: {msg}" for line, msg in errors],
        "counts": {
            "papers": len(papers),
            "with_bib_key": sum(p["has_bib_key"] for p in papers),
            "cited_in_build": sum(p["cited_in_build"] for p in papers),
            "only_in_notes": sum(not p["has_bib_key"] for p in papers),
            "bib_only": sum(p["has_bib_key"] and not p["mentions"] for p in papers),
            "mentions": len(notes),
        },
        "papers": [{"id": p.pop("id"), **p} for p in papers],
    }
    return index


def search(index, words, top):
    terms = [t for t in (cc.norm_title(w) for w in words.split()) if t]
    hits = []
    for paper in index["papers"]:
        hay = " ".join(
            [paper["title"], *paper["names"], *paper["keys"], paper["venue"]]
            + [m["text"] for m in paper["mentions"]]
        )
        hay = " " + cc.norm_title(hay) + " "
        found = [t for t in terms if f" {t}" in hay]
        if found:
            hits.append((len(found), paper))
    hits.sort(key=lambda h: (-h[0], not h[1]["has_bib_key"], h[1]["id"]))
    lines = []
    for score, paper in hits[:top]:
        where = paper["mentions"][0] if paper["mentions"] else None
        lines.append(
            f"{paper['id']} {score}/{len(terms)} keys={','.join(paper['keys']) or '-'} "
            f"cited={'yes' if paper['cited_in_build'] else 'no'} | "
            f"{paper['title'] or ', '.join(paper['names'])} | {paper['year'] or '-'} | "
            f"{paper['venue'] or '-'} | doi={','.join(paper['doi']) or '-'} | "
            f"arxiv={','.join(paper['arxiv']) or '-'} | "
            + (f"{where['file']}:{where['line']}" if where else "bib only")
        )
    return lines


# ---------------------------------------------------------------- sentences
SKIP_ENV = {"tabular", "tabularx", "tikzpicture", "equation", "align", "verbatim", "lstlisting"}
DEFINITION = re.compile(
    r"^\s*\\(?:newcommand|renewcommand|providecommand|def|let|usepackage|RequirePackage"
    r"|DeclareMathOperator|newenvironment|makeatletter|makeatother|graphicspath"
    r"|bibliographystyle|bibliography|documentclass)\b"
)
BREAK = re.compile(
    r"\\(?:part|chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?"
    r"\s*(?:\[[^\]]*\])?\s*\{[^{}]*\}"
    r"|\\(?:begin|end)\s*\{[^{}]*\}(?:\s*\[[^\]]*\])?"
    r"|\\item\b(?:\s*\[[^\]]*\])?"
    r"|\\(?:label|input|include)\s*\{[^{}]*\}|\\(?:maketitle|centering)\b"
)
END = re.compile(r"[.?!][)\"'}\]]*(?=\s+[A-Z\\(\[])")
ABBREV = re.compile(
    r"(?:\be\.g|\bi\.e|\bet al|\betc|\bvs|\bcf|\bFigs?|\bSecs?|\bEqs?|\bTab|\bNo|\b[A-Z])$"
)


def file_sentences(path):
    with open(path, encoding="utf-8") as handle:
        raw = handle.read().split("\n")
    out, text, where, skip = [], [], [], 0

    def flush():
        joined = "".join(text)
        chunks, start = [], 0
        for match in re.finditer("\x00", joined):
            chunks.append((start, match.start()))
            start = match.end()
        chunks.append((start, len(joined)))
        for begin, end in chunks:
            cut = begin
            for match in END.finditer(joined, begin, end):
                if joined[match.start()] == "." and ABBREV.search(joined[cut : match.start()]):
                    continue
                pieces.append((cut, match.end()))
                cut = match.end()
            pieces.append((cut, end))
        for begin, end in pieces:
            sentence = " ".join(joined[begin:end].split())
            if len(sentence.split()) < 3 or not re.search(r"[A-Za-z]", sentence):
                continue
            first = begin + len(joined[begin:end]) - len(joined[begin:end].lstrip())
            out.append((where[first], sentence))
        text.clear()
        where.clear()
        pieces.clear()

    pieces = []
    for number, line in enumerate(raw, 1):
        body = cc.strip_comment(line)
        envs = re.findall(r"\\(begin|end)\s*\{([^{}]*)\}", body)
        if skip:
            skip += sum(
                1 if kind == "begin" else -1 for kind, env in envs if env.rstrip("*") in SKIP_ENV
            )
            continue
        if any(kind == "begin" and env.rstrip("*") in SKIP_ENV for kind, env in envs):
            flush()
            skip = sum(
                1 if kind == "begin" else -1 for kind, env in envs if env.rstrip("*") in SKIP_ENV
            )
            continue
        if not body.strip() or DEFINITION.match(body):
            flush()
            continue
        body = BREAK.sub("\x00", body) + "\n"
        text.append(body)
        where.extend([number] * len(body))
    flush()
    return out


def sentences(args):
    scan = scan_build(args.main)
    root = os.path.abspath(args.sections) + os.sep  # a config default is absolute, a flag not
    rows, files = [], []
    for path in scan.files:
        norm = os.path.normpath(path)
        chosen = (
            any(fnmatch.fnmatch(norm, g) for g in args.only)
            if args.only
            else os.path.abspath(path).startswith(root)
        )
        if not chosen:
            continue
        files.append(norm)
        for line, sentence in file_sentences(path):
            flag = "cite" if cc.CITE.search(sentence) else "nocite"
            rows.append(f"{norm}:{line}\t{flag}\t{sentence}")
    return rows, files


# ---------------------------------------------------------------- driver
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--bib", help="BibTeX file (default: paper.bib in paper-tools.toml)")
    parser.add_argument(
        "--main", help="main .tex file of the build (default: paper.main_tex in paper-tools.toml)"
    )
    parser.add_argument(
        "--notes",
        nargs="*",
        metavar="FILE[::HEADING]",
        help="default: literature.notes in paper-tools.toml",
    )
    parser.add_argument(
        "--out",
        default=os.path.join(os.environ.get("TMPDIR") or tempfile.gettempdir(), "lit_index.json"),
    )
    parser.add_argument(
        "--self-name",
        action="append",
        metavar="NAME",
        help="repeatable; a paper whose bib key or arXiv id equals NAME, or whose title or name "
        "holds it, is flagged self_citation; default: literature.self_names in paper-tools.toml",
    )
    parser.add_argument(
        "--search", metavar="WORDS", help="print the papers holding the most of these words"
    )
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--sentences", action="store_true", help="print the build's sentences instead"
    )
    parser.add_argument(
        "--sections", help="section folder (default: paper.sections_dir in paper-tools.toml)"
    )
    parser.add_argument("--only", nargs="*", metavar="GLOB", default=[])
    args = parser.parse_args(argv)
    cfg = load()
    if args.bib is None:
        args.bib = str(cfg["paper"]["bib"])
    if args.main is None:
        args.main = str(cfg["paper"]["main_tex"])
    if args.sections is None:
        args.sections = str(cfg["paper"]["sections_dir"])
    args.notes = args.notes or cfg["literature"]["notes"]
    args.self_name = args.self_name or cfg["literature"]["self_names"]

    try:
        if args.sentences:
            rows, files = sentences(args)
            for row in rows:
                print(row)
            bare = sum("\tnocite\t" in row for row in rows)
            print(
                f"lit_index: {len(rows)} sentences ({bare} without \\cite) in {len(files)} files: {' '.join(files)}"
            )
            return 0 if files else 2
        index = build(args)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"lit_index: {exc}", file=sys.stderr)
        return 2
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    if args.search:
        for line in search(index, args.search, args.top):
            print(line)
    c = index["counts"]
    print(
        f"lit_index: {c['papers']} papers ({c['with_bib_key']} with a bib key, {c['cited_in_build']} cited "
        f"in the build, {c['only_in_notes']} only in notes, {c['bib_only']} only in the bib), "
        f"{c['mentions']} note mentions; wrote {args.out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
