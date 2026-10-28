#!/usr/bin/env python3
"""Check every Verified quote in the research notes against the text of the paper it cites.

Usage:
  quotecheck.py [--repo DIR] [--papers DIR ...] [--matches] [NOTE ...]

NOTE defaults to every `docs/research/**/notes/**/*.md` under `--repo` (default: the git top level
of the current directory, else the current directory); a note outside the repo is named by the
path given. `--papers` names a folder of PDFs and may repeat (default `<repo>/papers`); a file
name seen in an earlier folder is not read again.

A Verified line is one carrying a V mark (`[V]`, `[V, p.3]`, `**V**`, `**[V]**`, `(V)`, or the
word `Verified`), or one under a heading so marked that carries no I mark (`[I]`, `**I**`, `(I)`,
`Inferred`). Each double-quoted span on it (straight or curly quotes) of at least MIN_QUOTE letters
and digits is a quote; a shorter span is a label, printed as SKIP and not checked. `...`, `…` and
`[...]` split a quote into parts; every part must be found, in the quoted order and without
overlap, and a part under MIN_PART letters and digits must lie within NEAR of the part before or
after it.

The cited paper is every paper id on the quote's line (arXiv id, DOI, `paper_<hash>` or a hash
prefix of at least 6 hex digits, 4 after `paper_`); if the line names none, the ids of the nearest
heading that names any; if none does, the ids in the note's preamble (the lines before its first
`##`). A line that names no id but carries a non-arXiv URL quotes that page, and is not checked. A
quote with no paper id is counted as "cites no paper" and not checked.

A PDF is found for an id by its file name (`<arXiv id>[vN]...pdf`, `paper_<hash>.pdf`, or
`doi-<DOI with its first / as _>.pdf`, such as `doi-10.1145_2807591.2807644.pdf`) or by the
arXiv stamp or first DOI on its first page. Text comes from poppler's `pdftotext`, in reading
order and in `-raw` content order
(tables and two-column pages break one or the other). Both sides are compared as lowercase letters
and digits only, after Unicode NFKD (ligatures, accents), with a decimal point kept between digits,
a minus sign kept before a number (`-0.85` is not `0.85`) and the comparisons `<`, `>`, `=`, `≤`,
`≥` and `≠` kept: spacing, line-end hyphenation, other dashes, quote marks and other punctuation
never cause a miss. A quote part the PDF text holds only split once by MIN_SPLIT to MAX_SPLIT
letters of other text that start and end at line breaks (a figure, table or footnote placed
mid-sentence, or prose the quote leaves out) is a SPLIT: it names the omitted text and fails like a
miss, so the note trims the quote to one side, marks the gap with `...`, or relabels it. A shorter
insertion, such as a dropped word, or one inside a line, is not found.

A page marker (`p.N`, `pp.N-M`) on a Verified line belongs to the quoted span nearest it, the later
one on a tie, as in `[V, p.3] "..."` or `"..." (p.3)`. A quote no marker on its line belongs to,
on a line that names no paper id, takes the markers of the nearest heading above it that has any,
as in `### Case studies (Appendix G, p.35-36) (Verified)`, but no higher than the nearest heading
that names a paper. A quote with markers must touch one of their pages; one with none is not
page-checked. N is the PDF page index (1 for the PDF's first page, as a PDF viewer counts;
pdftotext ends each page with a form feed), not the number printed on the page.
A quote found only on other pages is a page mismatch, a miss; if it is found there only split,
the reason names the omitted text too.

Prints one SKIP line per label, one SPLIT line per split quote with the omitted text's length and
first words, and one MISS line per quote not found, with the reason: no PDF found, PDF text
unreadable, page mismatch (the pages cited and found), or not found plus the closest passage, its
page, its similarity and the words that differ.
`--matches` also prints each MATCH. Exits 1 if any quote is a SPLIT or a MISS, 2 if no Verified
quote cites a paper (a zero count proves nothing: check the note paths and `--papers`), else 0.
"""

import argparse
import bisect
import difflib
import functools
import re
import subprocess
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

MIN_QUOTE = 20  # letters and digits in a whole quote; shorter spans are labels, not quotes
MIN_PART = 8  # letters and digits a quote part needs to be checked on its own
NEAR = 100  # letters and digits a shorter part may lie from the part before or after it (a clause)
MIN_TEXT = 2000  # letters and digits below which a PDF's text counts as unreadable
MIN_SPLIT, MAX_SPLIT = 40, 4000  # letters of other text allowed inside a quote part
GRAM = 10  # k-gram length used to locate the closest passage

ARXIV = re.compile(r"(?<![\d.])(\d{2}(?:0[1-9]|1[0-2])\.\d{4,5})(v\d+)?(?!\d)")
ARXIV_STAMP = re.compile(r"arXiv:(\d{4}\.\d{5})(v\d+)?")  # papers/make-index.py's first-page rule
DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>()\[\]`|]+)")
HEX = re.compile(r"(?<![0-9a-zA-Z])(?:paper_([0-9a-f]{4,32})|([0-9a-f]{6,32}))(?![0-9a-zA-Z])")
URL = re.compile(r"https?://\S+")
V_MARK = re.compile(r"\*\*\[?V\]?\*\*|\[V[\],;\s]|\(V[),;\s]|(?<![\w-])(?<!bench )Verified\b(?!-)")
I_MARK = re.compile(r"\*\*\[?I\]?\*\*|\[I[\],;\s]|\(I[),;\s]|\bInferred\b")
HEADING = re.compile(r"^(#{1,6})\s")
QUOTE = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')
GAP = re.compile(r"\.\.\.|…|\[[^\]]*\]")
SPACE = re.compile(r"\s+")
PAGE = re.compile(r"\bpp?\.\s?(\d+)(?:\s?[-\u2013]\s?(\d+))?(?![\d.])")
DOI_NAME = re.compile(r"doi-(10\.\d{4,9})_(.+)")  # doi-<DOI with its first / as _>.pdf
DASHES = dict.fromkeys([*range(0x2010, 0x2016), 0x2212], "-")  # hyphens, dashes, minus
MINUS = "-\u2212\u2013"  # a minus sign as typed, as typeset, and as some PDFs render it
COMPARE = {"<": "<", ">": ">", "=": "=", "≤": "<=", "⩽": "<=", "≥": ">=", "⩾": ">=", "≠": "!="}


def canon(text):
    """Lowercase letters and digits of `text`, with the index in `text` of each kept character.

    NFKD splits ligatures and strips accents; a "." between two digits is kept so that 1.25 and
    12.5 stay different; a minus sign before a digit and after no letter or digit is kept as "-"
    so that -0.85 and 0.85 stay different (GPT-4 and 3-5 lose theirs); the comparisons <, >, =,
    "<=" (also "≤", "⩽"), ">=" (also "≥", "⩾") and "!=" (also "≠") are kept; "×" counts as "x".
    Everything else (spaces, hyphens, quotes) is dropped.
    """
    out, where = [], []
    for i, ch in enumerate(text):
        nxt = text[i + 1 : i + 2]
        if ch == "." and out and out[-1].isdigit() and nxt.isdigit():
            kept = "."
        elif ch in MINUS and nxt.isdigit() and not text[i - 1 : i].isalnum():
            kept = "-"
        elif ch == "!" and nxt == "=":
            kept = "!"
        elif ch in COMPARE:
            kept = COMPARE[ch]
        else:
            kept = "".join(
                COMPARE.get(c, c)
                for c in unicodedata.normalize("NFKD", "x" if ch == "×" else ch).lower()
                if (c.isalnum() and not unicodedata.combining(c)) or c in COMPARE
            )
        out += kept
        where += [i] * len(kept)
    return "".join(out), where


def key(text):
    return canon(text)[0]


class View:
    """One pdftotext rendering of a PDF: its raw text and the canonical form of it."""

    def __init__(self, raw):
        self.raw = raw
        self.text, self.where = canon(raw)
        self.feeds = [i for i, ch in enumerate(raw) if ch == "\f"]  # page ends

    def found(self, part):
        return next(self.spans(part), None) is not None

    def spans(self, part, split=True):
        """Each (start, end, cut) of `part` in this text: whole, with cut None, then, if `split`,
        split once by an insertion whose (start, end) is cut.

        The insertion is MIN_SPLIT..MAX_SPLIT letters long and starts and ends at a line break,
        as a figure, table or footnote placed mid-sentence does; a dropped word does not.
        """
        text = self.text
        at = text.find(part)
        while at != -1:
            yield at, at + len(part), None
            at = text.find(part, at + 1)
        if not split:
            return
        for cut in range(MIN_PART, len(part) - MIN_PART + 1):
            head, tail = part[:cut], part[cut:]
            at = text.find(head)
            while at != -1:
                end = at + cut
                if self.breaks(end):
                    hi = end + MAX_SPLIT + len(tail)
                    t = text.find(tail, end + MIN_SPLIT, hi)
                    while t != -1:
                        if self.breaks(t):
                            yield at, t + len(tail), (end, t)
                        t = text.find(tail, t + 1, hi)
                at = text.find(head, at + 1)

    def breaks(self, i):
        """Whether a line break lies between canonical characters i - 1 and i."""
        return 0 < i < len(self.where) and "\n" in self.raw[self.where[i - 1] : self.where[i]]

    def page(self, i):
        """The PDF page index (1 for the first page) of canonical character i."""
        return bisect.bisect(self.feeds, self.where[i]) + 1

    def chain(self, parts, split, pages=()):
        """One (start, end, cut) per part of a quote, in the quoted order and not overlapping, with
        some part touching one of the (first, last) PDF page ranges `pages` if any are given; None
        if there is none. A part under MIN_PART lies within NEAR of the part before or after it.
        `split` allows a part split by an insertion, as `spans` finds."""
        occ = [sorted(self.spans(x, split), key=lambda o: o[:2]) for x in parts]
        starts = [[o[0] for o in os] for os in occ]

        def touches(s, e):
            return any(self.page(s) <= hi and self.page(e - 1) >= lo for lo, hi in pages)

        @functools.cache
        def walk(i, pos, touched, loose):
            """The rest of a chain from part i at or after `pos`; `loose`: part i - 1 is short and
            not yet within NEAR of a neighbour, so part i must start within NEAR of `pos`."""
            if i == len(parts):
                return () if (touched or not pages) and not loose else None
            for o in occ[i][bisect.bisect_left(starts[i], pos) :]:
                s, e, _ = o
                if loose and s - pos > NEAR:
                    break
                near = i > 0 and s - pos <= NEAR
                rest = walk(
                    i + 1, e, touched or touches(s, e), len(parts[i]) < MIN_PART and not near
                )
                if rest is not None:
                    return (o, *rest)
            return None

        return walk(0, 0, False, False)

    def omitted(self, chain):
        """Each insertion a chain's parts were split by: its length and first words."""
        return "; ".join(
            f"{t - s} letters starting '{' '.join(self.passage(s, t).split()[:8])}'"
            for _, _, cut in chain
            if cut
            for s, t in [cut]
        )

    def passage(self, s, e):
        return SPACE.sub(" ", self.raw[self.where[s] : self.where[e - 1] + 1].translate(DASHES))


@dataclass(eq=False)
class Paper:
    path: Path
    ids: set  # "arXiv:2607.07744", "doi:10.1145/...", "hash:<32 hex>"
    views: list

    @property
    def id(self):
        """The paper's arXiv id, else its DOI, else its file stem."""
        for prefix in ("arXiv:", "doi:"):
            if ids := sorted(i for i in self.ids if i.startswith(prefix)):
                return ids[0]
        return self.path.stem

    @property
    def readable(self):
        return len(self.views[0].text) >= MIN_TEXT


def default_repo():
    """The git top level of the current directory, else the current directory."""
    git = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(git.stdout.strip()) if git.returncode == 0 else Path.cwd()


def pdf_text(path, mode=()):
    try:
        run = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", *mode, str(path), "-"], capture_output=True, check=False
        )
    except FileNotFoundError:
        sys.exit("quotecheck: needs poppler's pdftotext on PATH")
    return run.stdout.decode("utf-8", "replace") if run.returncode == 0 else ""


def load_papers(dirs):
    """Every PDF in `dirs` (first folder wins on a repeated file name), with its text and ids."""
    seen, paths = set(), []
    for d in dirs:
        for p in sorted(Path(d).glob("*.pdf")):
            if p.name not in seen:
                seen.add(p.name)
                paths.append(p)
    with ThreadPoolExecutor(8) as pool:
        texts = list(pool.map(pdf_text, paths))
        raws = list(pool.map(lambda p: pdf_text(p, ["-raw"]), paths))
    papers = []
    for path, text, raw in zip(paths, texts, raws):
        ids = set()
        if m := ARXIV.match(path.stem):
            ids.add(f"arXiv:{m.group(1)}")
        if m := re.fullmatch(r"paper_([0-9a-f]{32})", path.stem):
            ids.add(f"hash:{m.group(1)}")
        if m := DOI_NAME.fullmatch(path.stem):
            ids.add(f"doi:{m.group(1)}/{m.group(2)}".lower())
        first = text.split("\f", 1)[0]
        if not any(i.startswith("arXiv:") for i in ids) and (m := ARXIV_STAMP.search(first)):
            ids.add(f"arXiv:{m.group(1)}")
        if m := DOI.search(first):
            ids.add(f"doi:{m.group(1).rstrip('.,;:').lower()}")
        papers.append(Paper(path, ids, [View(text), View(raw)]))
    return papers


@dataclass
class Ref:
    label: str  # the arXiv id or DOI the note wrote, or for a hash prefix the PDF's own id
    papers: list  # local PDFs for it, empty if none


def refs_in(text, papers):
    """Paper ids named in `text`, each with the local PDFs that carry it."""
    refs = {}
    for m in ARXIV.finditer(text):
        ident = f"arXiv:{m.group(1)}"
        refs.setdefault(ident, [p for p in papers if ident in p.ids])
    for m in DOI.finditer(text):
        ident = f"doi:{m.group(1).rstrip('.,;:').lower()}"
        refs.setdefault(ident, [p for p in papers if ident in p.ids])
    for m in HEX.finditer(text):
        prefix = f"hash:{m.group(1) or m.group(2)}"
        hits = [p for p in papers if any(i.startswith(prefix) for i in p.ids)]
        if len(hits) == 1:  # an unknown hex run is a commit or a colour, not a paper
            refs.setdefault(hits[0].id, hits)
    return [Ref(label, hits) for label, hits in refs.items()]


@dataclass
class Claim:
    """One Verified line of a note."""

    note: str
    line: int
    text: str
    refs: list
    quotes: list
    pages: list  # for each quote, the (first, last) PDF page ranges it may cite; [] if none
    short: list  # quoted spans under MIN_QUOTE letters and digits, skipped as labels
    web: bool  # quotes a web page named by URL, not a paper
    section: str  # the headings above the line, outermost first


def claims(note, body, papers):
    """Every Verified line of the note `body`, with the papers it cites and its quotes."""
    lines = body.splitlines()
    first = next((i for i, s in enumerate(lines) if re.match(r"##+\s", s)), len(lines))
    preamble = refs_in("\n".join(lines[:first]), papers)
    chain = []  # (level, heading line, refs, page ranges)
    for n, line in enumerate(lines, 1):
        if m := HEADING.match(line):
            level = len(m.group(1))
            head = (level, line, refs_in(line, papers), markers(line))
            chain = [h for h in chain if h[0] < level] + [head]
            continue
        inherited = any(V_MARK.search(h[1]) for h in chain) and not I_MARK.search(line)
        if not V_MARK.search(line) and not inherited:
            continue
        spans = [(m.start(), m.end(), m.group(1) or m.group(2)) for m in QUOTE.finditer(line)]
        quotes = [(s, e, q) for s, e, q in spans if len(key(q)) >= MIN_QUOTE]
        short = [q for _, _, q in spans if len(key(q)) < MIN_QUOTE]
        refs = own = refs_in(line, papers)
        web = not refs and any("arxiv.org" not in u for u in URL.findall(line))
        if not refs and not web:
            refs = next((h[2] for h in reversed(chain) if h[2]), preamble)
        pages = cited_pages(line, spans, quotes)
        if not own:  # a quote no marker on its line belongs to takes the nearest heading's
            pages = [pg or heading_pages(chain) for pg in pages]
        section = "\n".join(h[1] for h in chain)
        yield Claim(note, n, line, refs, [q for *_, q in quotes], pages, short, web, section)


def heading_pages(chain):
    """The page ranges of the nearest heading in `chain` that has page markers, looking no higher
    than the nearest heading that names a paper (a higher heading's pages are another paper's)."""
    for _, _, refs, pages in reversed(chain):
        if pages or refs:
            return pages
    return []


def markers(line):
    """The (first, last) PDF page ranges the page markers on `line` cite, outside quoted spans."""
    quoted = [m.span() for m in QUOTE.finditer(line)]
    return [
        (int(m.group(1)), int(m.group(2) or m.group(1)))
        for m in PAGE.finditer(line)
        if not any(s <= m.start() < e for s, e in quoted)
    ]


def cited_pages(line, spans, quotes):
    """For each quote, the (first, last) PDF page ranges the page markers on `line` cite for it.

    A marker (`p.N`, `pp.N-M`) belongs to the quoted span nearest it, the later one on a tie, so
    `[V, p.3] "..."` and `"..." (p.3)` both cite p.3 for that quote. Markers inside quoted spans are
    ignored; a quote no marker belongs to cites no page.
    """
    own = {s: [] for s, _, _ in spans}
    for m in PAGE.finditer(line):
        if not spans or any(s <= m.start() < e for s, e, _ in spans):
            continue
        s, _, _ = min(
            spans,
            key=lambda sp: (sp[0] - m.end(), 0) if sp[0] >= m.end() else (m.start() - sp[1], 1),
        )
        own[s].append((int(m.group(1)), int(m.group(2) or m.group(1))))
    return [own[s] for s, _, _ in quotes]


@dataclass
class Result:
    status: str  # "match"; "split" (found only with other text removed from inside it); for a
    # miss "no PDF found", "PDF text unreadable", "not found" or "page mismatch" (found, but not on
    # the page the note cites)
    reason: str = ""
    paper: str = ""  # file name of the PDF that matched


def closest(part, papers):
    """(similarity, view, start, end) of the passage that best lines up with `part`."""
    best = (0.0, None, 0, 0)
    for v in (v for p in papers for v in p.views):
        votes = {}
        for k in range(0, max(1, len(part) - GRAM + 1), GRAM // 2):
            gram, at = part[k : k + GRAM], -1
            while (at := v.text.find(gram, at + 1)) != -1:
                votes[at - k] = votes.get(at - k, 0) + 1
        for start in sorted(votes, key=votes.get, reverse=True)[:5]:
            lo, hi = max(0, start - 20), min(len(v.text), start + len(part) + 20)
            sm = difflib.SequenceMatcher(None, part, v.text[lo:hi], autojunk=False)
            blocks = [b for b in sm.get_matching_blocks() if b.size]
            if not blocks:
                continue
            s, e = lo + blocks[0].b, lo + blocks[-1].b + blocks[-1].size
            ratio = difflib.SequenceMatcher(None, part, v.text[s:e], autojunk=False).ratio()
            if ratio > best[0]:
                best = (ratio, v, s, e)
    return best


def word_diff(note, pdf):
    a, b = note.split(), pdf.split()
    sm = difflib.SequenceMatcher(None, [key(w) for w in a], [key(w) for w in b], autojunk=False)
    out = [
        f"note '{' '.join(a[i1:i2])}' / pdf '{' '.join(b[j1:j2])}'"
        for op, i1, i2, j1, j2 in sm.get_opcodes()
        if op != "equal"
    ]
    return "; ".join(out[:4]) + ("; ..." if len(out) > 4 else "")


def check(quote, refs, pages=()):
    """Whether `quote` is in one of the PDFs `refs` name, touching one of the (first, last) PDF
    page ranges `pages` when any are given, and if not, why."""
    segments = [s for s in GAP.split(quote) if key(s)] or [quote]  # a quote all in [...]
    parts = [key(s) for s in segments]
    local = list(dict.fromkeys(p for r in refs for p in r.papers))
    if not local:
        return Result("no PDF found", "no PDF found for " + ", ".join(r.label for r in refs))
    readable = [p for p in local if p.readable]
    if not readable:
        names = ", ".join(p.path.name for p in local)
        return Result("PDF text unreadable", f"PDF text unreadable: {names}")
    pv = [(p, v) for p in readable for v in p.views]
    for split in (False, True):
        for p, v in pv:
            if c := v.chain(parts, split, pages):
                if not split:
                    return Result("match", paper=p.path.name)
                reason = f"found only with other text removed from inside it: {v.omitted(c)}"
                return Result("split", reason, paper=p.path.name)
    for split in (False, True) if pages else ():
        for p, v in pv:
            if c := v.chain(parts, split):
                cited = ", ".join(f"p.{lo}" if lo == hi else f"pp.{lo}-{hi}" for lo, hi in pages)
                where = ", ".join(f"p.{n}" for n in sorted({v.page(s) for s, _, _ in c}))
                reason = f"cited {cited}, found on {where}"
                if split:
                    reason += f", and only with other text removed from inside it: {v.omitted(c)}"
                return Result("page mismatch", reason, paper=p.path.name)
    views = [v for _, v in pv]
    unfound = [i for i, x in enumerate(parts) if not any(v.found(x) for v in views)]
    if not unfound:
        reason = f"every part found in {', '.join(p.path.name for p in readable)}, but not in the"
        reason += f" quoted order, or a part under {MIN_PART} letters is not within {NEAR} of"
        reason += " the part before or after it"
        return Result("not found", reason)
    i = max(unfound, key=lambda j: len(parts[j]))
    ratio, v, s, e = closest(parts[i], readable)
    reason = "not found in " + ", ".join(p.path.name for p in readable)
    if v is not None:
        passage = v.passage(s, e)
        reason += f"; closest p.{v.page(s)} ({ratio:.2f}): '{passage}'"
        if diff := word_diff(segments[i], passage):
            reason += f"; differs: {diff}"
    if missing := [r.label for r in refs if not r.papers]:
        reason += "; also cites " + ", ".join(missing) + " (no PDF found)"
    return Result("not found", reason)


def notes_in(repo):
    return sorted((repo / "docs/research").glob("**/notes/**/*.md"))


def default_papers(repo):
    return [repo / "papers"]


def note_name(path, repo):
    """`path` from the repo root, or as given for a note outside the repo."""
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def run(repo, paper_dirs, note_paths):
    """The PDFs; the claims that cite a paper; [(Claim, quote, Result)] for their quotes; and the
    claims that cite none."""
    papers = load_papers(paper_dirs)
    cited, checked, uncited = [], [], []
    for path in note_paths:
        for c in claims(note_name(path, repo), path.read_text(encoding="utf-8"), papers):
            if not c.refs or c.web:
                uncited.append(c)
                continue
            cited.append(c)
            checked += [(c, q, check(q, c.refs, pg)) for q, pg in zip(c.quotes, c.pages)]
    return papers, cited, checked, uncited


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repo", type=Path, default=None)
    ap.add_argument("--papers", type=Path, action="append")
    ap.add_argument("--matches", action="store_true", help="also print each MATCH line")
    ap.add_argument("notes", type=Path, nargs="*")
    args = ap.parse_args()
    args.repo = args.repo or default_repo()
    paper_dirs = args.papers or default_papers(args.repo)
    papers, cited, checked, uncited = run(args.repo, paper_dirs, args.notes or notes_in(args.repo))
    short = [(c, q) for c in cited + uncited for q in c.short]
    for c, q in short:
        print(
            f'SKIP\t{c.note}:{c.line}\t-\t"{q}"\tunder {MIN_QUOTE} letters and digits; not checked'
        )
    misses = {}
    for c, q, r in checked:
        if r.status != "match":
            misses[r.status] = misses.get(r.status, 0) + 1
        if r.status != "match" or args.matches:
            status = {"match": "MATCH", "split": "SPLIT"}.get(r.status, "MISS")
            line = f'{status}\t{c.note}:{c.line}\t{r.paper or "-"}\t"{q}"'
            print(line + (f"\t{r.reason}" if r.reason else ""))
    total = sum(misses.values())
    kinds = ", ".join(f"{n} {k}" for k, n in sorted(misses.items()))
    print(
        f"{len(papers)} PDFs read from {', '.join(map(str, paper_dirs))}; "
        f"{len(checked)} Verified quotes cite a paper: {len(checked) - total} match, {total} miss"
        + (f" ({kinds})" if kinds else "")
        + f"; {sum(len(c.quotes) for c in uncited)} Verified quotes cite no paper"
        " (web page, repo or none) and are not checked"
        f"; {len(short)} quoted spans under {MIN_QUOTE} letters and digits skipped"
    )
    if not checked:
        print("no Verified quote cites a paper: check the note paths and --papers", file=sys.stderr)
    sys.exit(1 if total else 0 if checked else 2)


if __name__ == "__main__":
    main()
