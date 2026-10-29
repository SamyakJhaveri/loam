#!/usr/bin/env python3
"""Log research-gap step 3 searches and pool them into rerank.tsv, in the schemas SKILL.md defines.

Usage:
  searchlog.py log GAP --qid Q --index INDEX --kind KIND --query TEXT [--hits FILE.json | --failed REASON]
  searchlog.py pool GAP

GAP is one idea's `gap/<idea>/` folder. The worker runs each search itself and saves its hits.

`log` appends one query to GAP/searches.tsv: the top 10 hits (every hit for kind citations),
ranked from 1 in the order given, and the query as sent (tabs and line breaks become spaces).
FILE.json is a list of {"id", "title", "year"}; an empty id (no arXiv id or DOI) is logged as the
title key `title:<normalized title>`. No hits (an empty list, or no --hits) or --failed logs one
rank-0 row with the reason in the title column.

`pool` pools every hit in searches.tsv under its canonical id from GAP/aliases.tsv (alias,
canonical, optional note; chains are followed) and rewrites GAP/rerank.tsv with one row per
pooled paper and the qids that found it. Facet marks, read flags and any columns a worker added
after the schema's six are kept for papers still pooled. Rows under ids that now pool together
merge into one: each field keeps its non-empty value, read is `yes` if any row says so, and
where two rows hold different marks the canonical id's row wins and a `mark-conflict` line goes
to stderr. A new paper gets empty marks and read `no`. Rows sort by facets matched, then partial.
It prints the pooled count and each read-list paper (read `yes`) that only seed or citation
queries found.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

SEARCHES = ["qid", "index", "kind", "query", "rank", "paper_id", "title", "year"]
RERANK = ["paper_id", "title", "facets_matched", "facets_partial", "qids", "read"]
KINDS = ("seed", "topic", "kill", "citations")


LINE_BREAKS = re.compile(r"[\t\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]")  # tab, and what splitlines() splits on


def clean(value):
    return " ".join(str("" if value is None else value).split())


def flat(value):
    """The value as given, with only tabs and line breaks turned into spaces."""
    return LINE_BREAKS.sub(" ", str("" if value is None else value))


def title_key(title):
    """`title:` plus the casefolded title, accents dropped from Latin letters, other scripts kept,
    and each run of non-word characters made one `-`. A title with no word characters keys on its
    raw text, which no word key can equal."""
    kept, base = [], ""
    for c in unicodedata.normalize("NFKD", title.casefold()):
        if not unicodedata.combining(c):
            base = c
        elif base.isascii():  # an accent on an ASCII letter: drop it
            continue
        kept.append(c)
    text = unicodedata.normalize("NFC", "".join(kept))
    words = "".join(c if c.isalnum() or unicodedata.category(c)[0] == "M" else " " for c in text).split()
    return "title:" + ("-".join(words) or clean(title))


def read_tsv(path):
    """Rows of a TSV with a header line, as dicts; [] when the file is absent."""
    if not path.exists():
        return []
    lines = [line.split("\t") for line in path.read_text().splitlines() if line.strip()]
    if not lines:
        return []
    head = lines[0]
    return [dict(zip(head, fields + [""] * (len(head) - len(fields)))) for fields in lines[1:]]


def write_rows(path, header, rows, append, verbatim=()):
    """Write rows with each field cleaned, or only flattened for the columns named in verbatim."""
    new = not append or not path.exists() or not path.read_text().strip()
    with path.open("w" if new else "a") as out:
        if new:
            out.write("\t".join(header) + "\n")
        for row in rows:
            out.write("\t".join(flat(x) if name in verbatim else clean(x) for name, x in zip(header, row)) + "\n")


def log(args):
    gap = Path(args.gap)
    base = [args.qid, args.index, args.kind, args.query]
    if args.failed is not None:
        rows = [base + [0, "", args.failed or "failed", ""]]
    else:
        hits = json.loads(Path(args.hits).read_text()) if args.hits else []
        if args.kind != "citations":
            hits = hits[:10]
        rows = [
            base + [rank, clean(h.get("id")) or title_key(clean(h.get("title"))), h.get("title"), h.get("year")]
            for rank, h in enumerate(hits, 1)
        ] or [base + [0, "", "no hits", ""]]
    write_rows(gap / "searches.tsv", SEARCHES, rows, append=True, verbatim=("query",))
    print(f"{args.qid}: {len(rows)} row(s) to {gap / 'searches.tsv'}")


def canonical(paper, aliases):
    seen = set()
    while paper in aliases and paper not in seen:
        seen.add(paper)
        paper = aliases[paper]
    return paper


def merge(paper, first, second):
    """One rerank row from two that pool under paper: per field the non-empty value, read `yes` if
    either is, and on two different marks the canonical id's row (else the first)."""
    if second.get("paper_id") == paper and first.get("paper_id") != paper:
        first, second = second, first
    merged, conflicts = dict(first), []
    for column, value in second.items():
        mine, theirs = merged.get(column, "").strip(), value.strip()
        if column == "read":
            merged[column] = "yes" if "yes" in (mine, theirs) else mine or theirs
        elif not mine:
            merged[column] = value
        elif theirs and theirs != mine and column not in ("paper_id", "title", "qids"):
            conflicts.append(f"{column} {mine!r} over {theirs!r}")
    if conflicts:
        print(f"mark-conflict\t{paper}\tkept {first.get('paper_id')}'s marks over {second.get('paper_id')}'s: "
              + "; ".join(conflicts), file=sys.stderr)
    return merged


def count(marks):
    return len([m for m in re.split(r"[,\s]+", marks) if m not in ("", "-")])


def pool(args):
    gap = Path(args.gap)
    aliases = {}
    alias_path = gap / "aliases.tsv"
    if alias_path.exists():
        for line in alias_path.read_text().splitlines():
            fields = line.split("\t")
            if len(fields) >= 2 and fields[0].strip() and fields[0] != "alias" and not line.startswith("#"):
                aliases[fields[0].strip()] = fields[1].strip()
    papers = {}  # canonical id -> {"title", "qids", "kinds"}
    for row in read_tsv(gap / "searches.tsv"):
        if row["rank"] in ("", "0"):
            continue
        logged = row["paper_id"] if row["paper_id"] not in ("", "title:") else title_key(row["title"])
        paper = canonical(logged, aliases)
        entry = papers.setdefault(paper, {"title": row["title"], "own": False, "qids": [], "kinds": set()})
        if logged == paper and not entry["own"]:  # the title logged under the canonical id wins
            entry["title"], entry["own"] = row["title"], True
        if row["qid"] not in entry["qids"]:
            entry["qids"].append(row["qid"])
        entry["kinds"].add(row["kind"])
    kept, old_rows = {}, read_tsv(gap / "rerank.tsv")
    extra = [column for column in (old_rows[0] if old_rows else {}) if column not in RERANK]
    for row in old_rows:
        paper = canonical(row["paper_id"], aliases)
        if paper in papers:
            kept[paper] = merge(paper, kept[paper], row) if paper in kept else row
    rows = []
    for paper, entry in papers.items():
        old = kept.get(paper, {})
        matched, partial = old.get("facets_matched", ""), old.get("facets_partial", "")
        read = old.get("read") or "no"
        rows.append([paper, entry["title"], matched, partial, ",".join(entry["qids"]), read]
                    + [old.get(column, "") for column in extra])
    rows.sort(key=lambda r: (-count(r[2]), -count(r[3]), r[0]))
    write_rows(gap / "rerank.tsv", RERANK + extra, rows, append=False)
    linked = [r for r in rows if r[5] == "yes" and papers[r[0]]["kinds"] <= {"seed", "citations"}]
    print(f"{len(rows)} pooled papers in {gap / 'rerank.tsv'}; {len(linked)} read-list papers found only by seed or citation queries:")
    for row in linked:
        print(f"seed-or-citation-only\t{row[0]}\t{clean(row[1])}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_log = sub.add_parser("log", help="append one query's hits to searches.tsv")
    p_log.add_argument("gap")
    p_log.add_argument("--qid", required=True)
    p_log.add_argument("--index", required=True)
    p_log.add_argument("--kind", required=True, choices=KINDS)
    p_log.add_argument("--query", required=True)
    result = p_log.add_mutually_exclusive_group()
    result.add_argument("--hits", metavar="FILE.json")
    result.add_argument("--failed", metavar="REASON")
    p_pool = sub.add_parser("pool", help="pool searches.tsv into rerank.tsv")
    p_pool.add_argument("gap")
    args = parser.parse_args(argv)
    if not Path(args.gap).is_dir():
        parser.error(f"no gap folder {args.gap}")
    {"log": log, "pool": pool}[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
