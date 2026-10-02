#!/usr/bin/env python3
# cite_check.py - reference checker for a paper's BibTeX file and citations.
#
# Sources. The logic named here was read and rewritten; nothing imports the sources, and no
# other file or line range of either repository was used.
#   [A] https://github.com/K-Dense-AI/scientific-agent-skills, commit 065b734
#       (065b734670d7d990627dbc06a05b5a99be33f1f1), MIT License (text below),
#       Copyright (c) 2025 K-Dense Inc.
#       skills/citation-management/scripts/_common.py L45-182: brace-depth BibTeX parser.
#       skills/citation-management/scripts/validate_citations.py L57-67 and L105-124 (required
#         fields per entry type; a book takes author or editor), L138-147 (4-digit year),
#         L157-167 (DOI form), L182-191 (author separators), L194-238 (Crossref lookup),
#         L252-282 (duplicate DOIs and keys), L323-329 (\cite scan), L477-496 (missing and
#         unused keys).
#       skills/citation-management/scripts/extract_metadata.py L60-67 and L94-98 (arXiv id
#         forms), L245-313 (arXiv Atom query and parse), L440-449 (Crossref year fields).
#   [B] https://github.com/imbad0202/academic-research-skills, commit e79085d
#       (e79085d0d38609984ef8cfe0faf2d254aac9e0a9), CC BY-NC 4.0
#       (https://creativecommons.org/licenses/by-nc/4.0/), Copyright (c) 2026 Cheng-I Wu.
#       scripts/retraction_status.py L152-229: the retraction verdict rule. A resolver that did
#         not answer gives "unknown"; a checked record gives a verdict only from what it
#         states; when no verdict is known the result is "unknown", never clean.
#
# Changes made:
#   C1  [A] parser records each entry's line. An unterminated entry, an entry without a key,
#       or an unreadable field is the defect "bib-parse" (source: skipped or stopped quietly).
#   C2  [A] validate_citations.py L233-238 called a DOI valid on any Crossref status other
#       than 200 or 404 and on any transport error. Here every non-200 status, timeout,
#       transport error or unreadable reply is the defect "unresolved" (fail closed).
#   C3  [A] validate_citations.py L406 dropped the fetched title and year. Here both are
#       compared with the entry: difflib ratio of the normalized titles must be at least
#       TITLE_THRESHOLD (0.90); the entry year must equal one of the fetched years.
#   C4  [A] no DataCite fallback: only api.crossref.org and export.arxiv.org are contacted.
#       A 10.48550/arXiv.<id> DOI (DataCite) is checked as that arXiv id instead; one with no
#       readable id is "unresolved". A DOI given only as a doi.org url is looked up too.
#   C5  [A] arXiv query over https with id_list only (source: http plus max_results). An
#       arXiv error entry, a reply without exactly one entry, or another id is "unresolved".
#   C6  [A] Crossref year: any of published-print, published-online, issued, published
#       (source: print, else online). arXiv year: published or updated.
#   C7  [A] duplicate keys compared case-insensitively; DOIs compared after dropping a
#       https://doi.org/ or doi: prefix and case.
#   C8  [A] cite scan follows \input and \include recursively from the main file, honours its
#       \input@path, drops % comments, and reads natbib optional arguments, starred forms and
#       \nocite, and key lists that span lines (source: one file, no optional arguments,
#       comments counted).
#   C9  Reference checks added here: full author list ("and others", "and {others}", "et al.",
#       empty or missing), a DOI or URL per entry, arXiv-only entries; which of them fail comes
#       from the project's config (cite.warn_only in paper-tools.toml lowers each to WARN);
#       unknown entry types are defects.
#   C10 [A] requests replaced by urllib (standard library only). The User-Agent carries no
#       email; only the identifier is sent. Canned replies (--responses) and --offline.
#   C11 [B] one resolver (Crossref) instead of OpenAlex plus Crossref. Retraction events are
#       read from the record's "updated-by" list, written here from the Crossref REST API
#       schema (fields "type", "label", "updated", "DOI"); the source's own event reader
#       (L93-150) lies outside the named range and was not used. A record whose DOI is missing
#       or differs from the entry's, or whose "updated-by" is malformed, gives "unknown",
#       reported as the defect "retraction-unknown".
#
# MIT License (covers the parts taken from [A])
#
# Copyright (c) 2025 K-Dense Inc.
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
"""Check a BibTeX file against the venue's reference rules and the paper's citations.

Usage (from the project root):
  cite_check.py [--bib FILE] [--main FILE]
                [--scan GLOB ...] [--responses FILE.json | --offline]
Defaults come from paper-tools.toml: --bib paper.bib, --main paper.main_tex, --scan every
.tex file in paper.sections_dir. The checks named in cite.warn_only (any of "authors",
"no-link", "arxiv-only") print WARN instead of DEFECT.

Prints one line per defect: DEFECT <key> <check> <file>:<line>: <detail>. Warnings start
with WARN. Exit 1 when any defect exists, 0 when none, 2 on a usage error.

--responses FILE.json maps a request URL to {"status": <int>, "body": <str or JSON>} or to
{"error": "<reason>"}; a URL missing from the file is unresolved. The network is never used
in that mode. --offline makes every lookup unresolved.
"""

from __future__ import annotations

import argparse
import difflib
import glob
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict

from paper_config import load

TITLE_THRESHOLD = 0.90
TIMEOUT_S = 20
USER_AGENT = "cite_check/1.0 (bibliography check)"
CROSSREF = "https://api.crossref.org/works/"
ARXIV = "https://export.arxiv.org/api/query?id_list="
GAP_S = {"export.arxiv.org": 3.0, "api.crossref.org": 0.5}  # live mode, per host
RETRY_STATUS = {429, 500, 502, 503, 504}
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

# Required fields per entry type ([A] validate_citations.py L57-67). "a|b" means either.
REQUIRED = {
    "article": ["author", "title", "journal", "year"],
    "book": ["author|editor", "title", "publisher", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "conference": ["author", "title", "booktitle", "year"],
    "incollection": ["author", "title", "booktitle", "publisher", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "misc": ["title", "year"],
}
VENUE_FIELDS = (
    "journal",
    "booktitle",
    "publisher",
    "school",
    "institution",
    "organization",
    "howpublished",
)
PREPRINT = re.compile(r"arxiv|\bcorr\b|preprint", re.I)
ARXIV_WORD = re.compile(r"arxiv|\bcorr\b", re.I)
ARXIV_ID = r"(?:\d{4}\.\d{4,5}|[a-z][a-z-]*(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?"
ARXIV_IN_TEXT = re.compile(r"(?:(?i:arxiv\.org)/(?:abs|pdf)/|(?i:arxiv)[:.]\s*)(" + ARXIV_ID + ")")
DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
RETRACT_KIND = {
    "retraction": "retraction",
    "retracted": "retraction",
    "partial retraction": "retraction",
    "withdrawal": "retraction",
    "removal": "retraction",
    "reinstatement": "reinstatement",
    "reinstated": "reinstatement",
}
# Retraction verdicts that are defects ([B] rule: "unknown" is never clean).
RETRACTION_CHECK = {
    "retracted": "retracted",
    "disputed": "retraction-disputed",
    "unknown": "retraction-unknown",
}
# Venue rule checks (C9) that cite.warn_only may lower to WARN.
VENUE_CHECKS = ("authors", "no-link", "arxiv-only")

# ---------------------------------------------------------------- BibTeX ([A] _common.py)
NON_ENTRY = {"string", "comment", "preamble"}
FIELD = re.compile(r"\s*([A-Za-z][A-Za-z0-9_+:.-]*)\s*=\s*(.*)$", re.DOTALL)


def _outer_braced(value):
    if not (value.startswith("{") and value.endswith("}")):
        return False
    depth = 0
    for index, char in enumerate(value):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index == len(value) - 1
    return False


def _unwrap(value):
    value = value.strip()
    if _outer_braced(value):
        return value[1:-1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def _split_top_level(body):
    parts, buf, depth, in_quote = [], [], 0, False
    for char in body:
        if char == '"' and depth == 0:
            in_quote = not in_quote
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if char == "," and depth == 0 and not in_quote:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    parts.append("".join(buf))
    return parts


def parse_bib(text):
    """Return (entries, errors). Entry: type, key, fields, line. Error: (line, message)."""
    entries, errors = [], []
    length, position = len(text), 0
    while True:
        at = text.find("@", position)
        if at < 0:
            break
        line = text.count("\n", 0, at) + 1
        cursor = at + 1
        while cursor < length and text[cursor].isalpha():
            cursor += 1
        entry_type = text[at + 1 : cursor].lower()
        while cursor < length and text[cursor].isspace():
            cursor += 1
        if not entry_type or cursor >= length or text[cursor] not in "{(":
            position = at + 1
            continue
        opener = text[cursor]
        closer = "}" if opener == "{" else ")"
        depth, end = 0, -1
        for scan in range(cursor, length):
            if text[scan] == opener:
                depth += 1
            elif text[scan] == closer:
                depth -= 1
                if depth == 0:
                    end = scan
                    break
        if end < 0:
            errors.append((line, f"@{entry_type} entry is never closed"))
            break
        position = end + 1
        if entry_type in NON_ENTRY:
            continue
        chunks = _split_top_level(text[cursor + 1 : end])
        key = chunks[0].strip()
        if not key or "=" in key:
            errors.append((line, f"@{entry_type} entry has no citation key"))
            continue
        fields = OrderedDict()
        for chunk in chunks[1:]:
            if not chunk.strip():
                continue
            match = FIELD.match(chunk)
            if not match:
                errors.append((line, f"{key}: unreadable field text {chunk.strip()[:40]!r}"))
                continue
            fields[match.group(1).lower()] = _unwrap(match.group(2))
        entries.append({"type": entry_type, "key": key, "fields": fields, "line": line})
    return entries, errors


# ---------------------------------------------------------------- LaTeX citation scan
INPUT = re.compile(r"\\(?:input|include)\s*\{([^{}]*)\}")
INPUT_PATH = re.compile(r"\\def\\input@path\s*\{((?:\s*\{[^{}]*\})+)\s*\}")
CITE = re.compile(
    r"\\(?:[Cc]ite(?:t|p|alt|alp|author|year|yearpar|num)?|nocite|[Pp]arencite|[Tt]extcite"
    r"|[Aa]utocite|[Ff]ootcite|fullcite)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^{}]*)\}"
)


def strip_comment(line):
    """Drop everything from the first % that a backslash does not escape."""
    out, index = [], 0
    while index < len(line):
        if line[index] == "\\":
            out.append(line[index : index + 2])
            index += 2
            continue
        if line[index] == "%":
            break
        out.append(line[index])
        index += 1
    return "".join(out)


class TexScan:
    """Collects cite keys with locations, following \\input and \\include."""

    def __init__(self, cwd, search):
        self.cwd, self.search = cwd, search
        self.seen, self.files = set(), []
        self.cites = defaultdict(list)  # key -> [(path, line)]
        self.problems = []  # (path, line, message)

    def resolve(self, name):
        for base in [self.cwd, *self.search]:
            path = os.path.normpath(os.path.join(base, name))
            for cand in [path] if path.endswith(".tex") else [path + ".tex", path]:
                if os.path.isfile(cand):
                    return cand
        return None

    def scan(self, path):
        real = os.path.realpath(path)
        if real in self.seen:
            return
        self.seen.add(real)
        self.files.append(path)
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            self.problems.append((path, 0, f"cannot read: {exc}"))
            return
        stripped = [strip_comment(raw) for raw in lines]
        text = "\n".join(stripped)  # a \cite key list may span lines
        for match in CITE.finditer(text):
            number = text.count("\n", 0, match.start()) + 1
            for key in match.group(1).split(","):
                if key.strip():
                    self.cites[key.strip()].append((path, number))
        for number, line in enumerate(stripped, 1):
            for match in INPUT.finditer(line):
                target = self.resolve(match.group(1).strip())
                if target is None:
                    self.problems.append((path, number, f"\\input{{{match.group(1)}}} not found"))
                else:
                    self.scan(target)


# ---------------------------------------------------------------- lookups
class Fetcher:
    """GET a URL once per run: live, canned (--responses), or offline. Fails closed."""

    def __init__(self, mode, responses=None):
        self.mode, self.responses = mode, responses or {}
        self.cache, self.last = {}, {}
        self.calls = 0

    def fetch(self, url):
        """Return (body, "") on HTTP 200, else (None, reason)."""
        if url not in self.cache:
            self.calls += 1
            self.cache[url] = self._fetch(url)
        return self.cache[url]

    def _fetch(self, url):
        if self.mode == "offline":
            return None, "offline mode"
        if self.mode == "canned":
            canned = self.responses.get(url)
            if not isinstance(canned, dict):
                return None, "no canned response for this URL"
            if "error" in canned:
                return None, str(canned["error"])
            status, body = canned.get("status"), canned.get("body", "")
            if status != 200:
                return None, f"HTTP {status}"
            return (body if isinstance(body, str) else json.dumps(body)), ""
        host = urllib.parse.urlsplit(url).hostname or ""
        reason = "no attempt made"
        for attempt in range(3):
            wait = self.last.get(host, 0.0) + GAP_S.get(host, 1.0) - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.last[host] = time.monotonic()
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT_S) as reply:
                    if reply.status != 200:
                        return None, f"HTTP {reply.status}"
                    return reply.read().decode("utf-8"), ""
            except urllib.error.HTTPError as exc:
                reason = f"HTTP {exc.code}"
                if exc.code not in RETRY_STATUS:
                    return None, reason
            except Exception as exc:  # any transport or decode failure: unresolved
                reason = f"{type(exc).__name__}: {exc}"
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
        return None, reason


def norm_doi(value):
    doi = DOI_PREFIX.sub("", value.strip()).rstrip(".")
    return doi if re.fullmatch(r"10\.\d{4,}/\S+", doi) else None


def norm_title(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))  # Crossref JATS or MathML tags
    text = re.sub(r"\\[`'^\"~=.uvHtcdbrk]\s*\{?([A-Za-z])\}?", r"\1", text)  # TeX accents
    text = re.sub(r"\\[A-Za-z]+\*?", " ", text)  # other TeX commands; arguments stay
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^0-9a-z]+", " ", text.lower()).split())


def title_score(bib_title, candidates):
    wanted, best, best_text = norm_title(bib_title), 0.0, ""
    for cand in candidates:
        ratio = difflib.SequenceMatcher(None, wanted, norm_title(cand), autojunk=False).ratio()
        if ratio > best:
            best, best_text = ratio, cand
    return best, best_text


def short(text, limit=90):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def compare(add, source, bib_title, bib_year, titles, years):
    """Add title-mismatch and year-mismatch defects for one fetched record."""
    if bib_title:
        ratio, fetched = title_score(bib_title, titles)
        if ratio < TITLE_THRESHOLD:
            add(
                "title-mismatch",
                f"title similarity {ratio:.2f} < {TITLE_THRESHOLD:.2f}: bib "
                f"{short(bib_title)!r}, {source} {short(fetched)!r}",
            )
    if bib_year is not None and bib_year not in years:
        add("year-mismatch", f"bib year {bib_year}, {source} years {sorted(years)}")


def _event_kind(event):
    for raw in (event.get("type"), event.get("label")):
        if isinstance(raw, str):
            kind = raw.strip().lower().replace("_", " ").replace("-", " ")
            if kind in RETRACT_KIND:
                return RETRACT_KIND[kind]
    return None


def _event_date(event):
    updated = event.get("updated")
    parts = updated.get("date-parts") if isinstance(updated, dict) else None
    if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
        if all(isinstance(part, int) for part in parts[0]):
            return tuple(parts[0])
    return None


def retraction_verdict(message, doi):
    """[B] L152-229 rule for one resolver. Returns (verdict, detail)."""
    record = message.get("DOI")
    record_doi = norm_doi(record) if isinstance(record, str) else None
    if record_doi is None or record_doi.lower() != doi.lower():
        return "unknown", f"Crossref record DOI {record!r} is not {doi}; retraction status unknown"
    raw = message.get("updated-by", [])
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        return "unknown", "Crossref updated-by is unreadable; retraction status unknown"
    events = [
        (kind, _event_date(item), item.get("DOI"))
        for item in raw
        if (kind := _event_kind(item)) is not None
    ]
    if not events:
        return "not_retracted", ""
    if len({kind for kind, _, _ in events}) > 1 and any(date is None for _, date, _ in events):
        return "disputed", "retraction and reinstatement notices, not all dated"
    kind, date, notice = max(events, key=lambda event: event[1] or ())
    when = "-".join(str(part) for part in date) if date else "undated"
    verdict = "reinstated" if kind == "reinstatement" else "retracted"
    return verdict, f"latest {kind} notice {notice} ({when})"


def check_crossref(add, doi, bib_title, bib_year, fetcher):
    url = CROSSREF + urllib.parse.quote(doi, safe="/")
    body, why = fetcher.fetch(url)
    if body is None:
        add("unresolved", f"DOI {doi}: {why} from {url}; title, year, retraction unknown")
        return
    try:
        data = json.loads(body)
        message = data["message"]
        if data.get("status") != "ok" or not isinstance(message, dict):
            raise ValueError("reply is not a Crossref work")
        titles = [t for t in message.get("title") or [] if isinstance(t, str) and t.strip()]
        subtitles = [s for s in message.get("subtitle") or [] if isinstance(s, str)]
    except (ValueError, KeyError, TypeError) as exc:
        add("unresolved", f"DOI {doi}: unreadable Crossref reply ({exc})")
        return
    years = set()
    for name in ("published-print", "published-online", "issued", "published"):
        stamp = message.get(name)
        parts = stamp.get("date-parts") if isinstance(stamp, dict) else None
        if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
            if isinstance(parts[0][0], int):
                years.add(parts[0][0])
    if not titles or not years:
        add("unresolved", f"DOI {doi}: Crossref record has no title or no year")
    else:
        candidates = titles + [f"{t}: {s}" for t in titles for s in subtitles]
        compare(add, "Crossref", bib_title, bib_year, candidates, years)
    verdict, detail = retraction_verdict(message, doi)
    if verdict in RETRACTION_CHECK:
        add(RETRACTION_CHECK[verdict], f"DOI {doi}: {detail}")
    elif verdict == "reinstated":
        add("reinstated", f"DOI {doi}: {detail}", level="WARN")


def check_arxiv(add, aid, bib_title, bib_year, fetcher):
    """Return what arXiv says about publication (journal_ref, doi) for the arxiv-only hint."""
    url = ARXIV + urllib.parse.quote(aid, safe="/")
    body, why = fetcher.fetch(url)
    if body is None:
        add("unresolved", f"arXiv {aid}: {why} from {url}")
        return {}
    try:
        root = ET.fromstring(body.encode("utf-8"))
    except ET.ParseError as exc:
        add("unresolved", f"arXiv {aid}: unreadable reply ({exc})")
        return {}
    items = root.findall("a:entry", ATOM)
    if len(items) != 1:
        add("unresolved", f"arXiv {aid}: reply holds {len(items)} entries, expected 1")
        return {}
    item = items[0]
    record_id = (item.findtext("a:id", "", ATOM) or "").strip()
    base = re.sub(r"v\d+$", "", aid)
    title = " ".join((item.findtext("a:title", "", ATOM) or "").split())
    stamps = (item.findtext("a:published", "", ATOM), item.findtext("a:updated", "", ATOM))
    years = {int(s.strip()[:4]) for s in stamps if s and s.strip()[:4].isdigit()}
    if "/api/errors" in record_id or f"/abs/{base}" not in record_id:
        add("unresolved", f"arXiv {aid}: reply is for id {record_id!r}")
        return {}
    if not title or not years:
        add("unresolved", f"arXiv {aid}: record has no title or no date")
        return {}
    compare(add, "arXiv", bib_title, bib_year, [title], years)
    info = {}
    for name in ("journal_ref", "doi"):
        value = " ".join((item.findtext(f"arxiv:{name}", "", ATOM) or "").split())
        if value:
            info[name] = value
    return info


# ---------------------------------------------------------------- per-entry checks
def has_link(fields):
    if fields.get("doi", "").strip() or fields.get("url", "").strip():
        return True
    return any(re.search(r"https?://", fields.get(name, "")) for name in ("howpublished", "note"))


def author_problems(author):
    if not re.sub(r"[{}\s]", "", author):
        return ["author field is empty"]
    problems = []
    if re.search(r"\band\s+\{?others\}?(?![\w])", author, re.I):
        problems.append('author list ends in "and others"; list every author')
    if re.search(r"\bet\.?\s*al\b", author, re.I):
        problems.append('author list contains "et al."; list every author')
    if re.search(r"(?<!\\)[;&]", author):
        problems.append('authors separated by ";" or "&", not " and "')
    return problems


def arxiv_ids(fields):
    found = []
    eprint = re.sub(r"^(?i:arxiv):\s*", "", fields.get("eprint", "").strip())
    if re.fullmatch(ARXIV_ID, eprint):
        found.append(eprint)
    for name in ("doi", "url", "journal", "howpublished", "note", "booktitle"):
        found += ARXIV_IN_TEXT.findall(fields.get(name, ""))
    out, bases = [], set()
    for aid in found:
        base = re.sub(r"v\d+$", "", aid)
        if base not in bases:
            bases.add(base)
            out.append(aid)
    return out


def check_entry(entry, fetcher, warn_only=()):
    """Return findings (level, check, detail) for one bib entry."""
    found = []

    def add(check, detail, level="DEFECT"):
        found.append(("WARN" if check in warn_only else level, check, detail))

    fields, entry_type = entry["fields"], entry["type"]
    required = REQUIRED.get(entry_type)
    if required is None:
        add("entry-type", f"@{entry_type} is not one of {', '.join(sorted(REQUIRED))}")
    else:
        missing = [
            name
            for name in required
            if not any(fields.get(alt, "").strip() for alt in name.split("|"))
        ]
        if missing:
            add("required-fields", f"@{entry_type} lacks {', '.join(missing)}")
    year_text = fields.get("year", "").strip()
    bib_year = int(year_text) if re.fullmatch(r"\d{4}", year_text) else None
    if year_text and bib_year is None:
        add("required-fields", f"year {year_text!r} is not four digits")

    author = fields.get("author")
    if author is None:
        needs_author = required is not None and any("author" in n.split("|") for n in required)
        if not needs_author and not fields.get("editor", "").strip():
            add("authors", "no author field")
    else:
        for problem in author_problems(author):
            add("authors", problem)

    if not has_link(fields):
        add("no-link", "no doi, no url, and no http link in howpublished or note")

    raw_doi = fields.get("doi", "").strip()
    doi = norm_doi(raw_doi) if raw_doi else None
    if raw_doi and doi is None:
        add("doi-form", f"doi {raw_doi!r} is not of the form 10.<registrant>/<suffix>")
    elif doi and doi != raw_doi:
        add("doi-form", f"doi field holds {raw_doi!r}; store the bare DOI {doi}", level="WARN")
    url = fields.get("url", "").strip()
    if not raw_doi and DOI_PREFIX.match(url):  # a DOI given only as a doi.org url
        doi = norm_doi(urllib.parse.unquote(url))

    bib_title = fields.get("title", "").strip()
    ids = arxiv_ids(fields)
    if doi and re.match(r"10\.48550/arxiv\.", doi, re.I):
        if not ARXIV_IN_TEXT.findall(doi):
            add("unresolved", f"DOI {doi}: arXiv DOI without a readable arXiv id; not looked up")
    elif doi:
        check_crossref(add, doi, bib_title, bib_year, fetcher)
    published = {}
    for aid in ids:
        published.update(check_arxiv(add, aid, bib_title, bib_year, fetcher))

    venues = [
        n for n in VENUE_FIELDS if fields.get(n, "").strip() and not PREPRINT.search(fields[n])
    ]
    arxiv_evidence = (
        bool(ids)
        or fields.get("archiveprefix", "").strip().lower() == "arxiv"
        or any(ARXIV_WORD.search(fields.get(n, "")) for n in VENUE_FIELDS)
    )
    if arxiv_evidence and not venues:
        hint = "; ".join(f"arXiv lists {k} {v!r}" for k, v in sorted(published.items()))
        add("arxiv-only", "no venue beyond arXiv" + (f" ({hint})" if hint else ""))
    return found


# ---------------------------------------------------------------- driver
def run(bib_path, entries, parse_errors, scan, fetcher, warn_only=()):
    """Return findings as (level, key, check, location, detail, cited)."""
    out = []
    for line, message in parse_errors:
        out.append(("DEFECT", "-", "bib-parse", f"{bib_path}:{line}", message, True))
    for path, line, message in scan.problems:
        out.append(("DEFECT", "-", "tex-input", f"{path}:{line}", message, True))

    keys = {entry["key"] for entry in entries}
    folded = defaultdict(list)
    for entry in entries:
        folded[entry["key"].lower()].append(entry)
    cite_all = "*" in scan.cites
    for key, places in scan.cites.items():
        if key == "*" or key in keys:
            continue
        variants = [e["key"] for e in folded.get(key.lower(), [])]
        note = f"; the bib has only {variants}" if variants else ""
        path, line = places[0]
        detail = f"cited ({len(places)}x) but not in {bib_path}{note}"
        out.append(("DEFECT", key, "missing-entry", f"{path}:{line}", detail, True))

    dois = defaultdict(list)
    for entry in entries:
        doi = norm_doi(entry["fields"].get("doi", ""))
        if doi:
            dois[doi.lower()].append(entry)

    for entry in entries:
        key, where = entry["key"], f"{bib_path}:{entry['line']}"
        cited = cite_all or key in scan.cites
        twins = [e for e in folded[key.lower()] if e is not entry]
        if twins:
            lines = ", ".join(f"{e['key']} at line {e['line']}" for e in twins)
            out.append(("DEFECT", key, "duplicate-key", where, f"same key as {lines}", cited))
        doi = norm_doi(entry["fields"].get("doi", ""))
        others = [e for e in dois.get(doi.lower(), []) if e is not entry] if doi else []
        if others:
            names = ", ".join(f"{e['key']} (line {e['line']})" for e in others)
            out.append(("DEFECT", key, "duplicate-doi", where, f"DOI {doi} also in {names}", cited))
        for level, check, detail in check_entry(entry, fetcher, warn_only):
            out.append((level, key, check, where, detail, cited))
        if not cited:
            detail = "never cited in the build or the scanned files"
            out.append(("WARN", key, "uncited", where, detail, False))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--bib", help="BibTeX file (default: paper.bib in paper-tools.toml)")
    parser.add_argument(
        "--main", help="main .tex file of the build (default: paper.main_tex in paper-tools.toml)"
    )
    parser.add_argument(
        "--scan",
        nargs="*",
        metavar="GLOB",
        help="more .tex files to read for citations (default: every .tex file in "
        "paper.sections_dir; give --scan with no GLOB to read only the build)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--responses", metavar="JSON", help="canned replies keyed by URL")
    mode.add_argument("--offline", action="store_true", help="every lookup is unresolved")
    args = parser.parse_args(argv)
    cfg = load()
    if args.bib is None:
        args.bib = str(cfg["paper"]["bib"])
    if args.main is None:
        args.main = str(cfg["paper"]["main_tex"])
    if args.scan is None:
        sections = cfg["paper"]["sections_dir"]
        args.scan = [str(sections / "*.tex")] if sections else []
    warn_only = cfg["cite"]["warn_only"]
    unknown = sorted(set(warn_only) - set(VENUE_CHECKS))
    if unknown:
        print(f"cite_check: cite.warn_only names unknown checks {unknown}", file=sys.stderr)
        return 2

    try:
        with open(args.bib, encoding="utf-8") as handle:
            bib_text = handle.read()
        with open(args.main, encoding="utf-8") as handle:
            main_text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cite_check: {exc}", file=sys.stderr)
        return 2
    responses = None
    if args.responses:
        try:
            with open(args.responses, encoding="utf-8") as handle:
                responses = json.load(handle)
            if not isinstance(responses, dict):
                raise ValueError("top level must be an object keyed by URL")
        except (OSError, ValueError) as exc:
            print(f"cite_check: --responses {args.responses}: {exc}", file=sys.stderr)
            return 2
    extra = []
    for pattern in args.scan:
        matched = sorted(glob.glob(pattern))
        if not matched:
            print(f"cite_check: --scan {pattern!r} matches no file", file=sys.stderr)
            return 2
        extra += matched

    cwd = os.path.dirname(args.main) or "."
    search = []
    path_def = INPUT_PATH.search("\n".join(strip_comment(ln) for ln in main_text.splitlines()))
    if path_def:
        search = [os.path.join(cwd, p) for p in re.findall(r"\{([^{}]*)\}", path_def.group(1))]
    scan = TexScan(cwd, search)
    scan.scan(args.main)
    for path in extra:
        scan.scan(path)

    mode_name = "offline" if args.offline else "canned" if responses is not None else "live"
    fetcher = Fetcher(mode_name, responses)
    entries, parse_errors = parse_bib(bib_text)
    findings = run(args.bib, entries, parse_errors, scan, fetcher, warn_only)

    defects = [f for f in findings if f[0] == "DEFECT"]
    warnings = [f for f in findings if f[0] != "DEFECT"]
    for level, key, check, where, detail, cited in defects + warnings:
        tag = "" if cited else " (not cited)"
        print(f"{level} {key} {check} {where}: {detail}{tag}")
    unresolved = sum(1 for f in findings if f[2] == "unresolved")
    print(
        f"cite_check: {len(entries)} entries, {len(scan.cites)} cited keys in "
        f"{len(scan.files)} tex files, {fetcher.calls} lookups ({mode_name}, {unresolved} "
        f"unresolved); {len(defects)} defects in {len({f[1] for f in defects})} keys, "
        f"{len(warnings)} warnings"
    )
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
