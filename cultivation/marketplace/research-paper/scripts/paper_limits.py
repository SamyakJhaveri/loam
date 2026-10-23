#!/usr/bin/env python3
r"""Check the built paper against the length limits in `limits.*` of paper-tools.toml.

The limits come from the project's config: body pages (limits.max_pages), counted with figures
and tables up to the references heading; an appendix or supplementary heading, a failure
unless limits.appendix_allowed; abstract words (limits.max_abstract_words).

    paper-tool paper_limits                  # build.pdf and paper.abstract_tex of the config
    paper-tool paper_limits --pdf main.pdf --abstract-tex abstract.tex
    paper-tool paper_limits --text main.txt  # a pdftotext dump, a form feed after each page

The PDF is read with one `pdftotext PDF -` run, whose output has a form feed after each page;
line numbers are that dump's lines (the same as `pdftotext main.pdf main.txt`).

Checks:
1. Body pages. The body ends on the page where the references heading starts; that page counts
   as a body page when anything but a bare page number precedes the heading on it (a float
   counts: the limit includes figures and tables). With no references heading, every page is
   body. Fail above --max-pages (default limits.max_pages).
2. Appendix. Fail on any appendix or supplementary-material heading line, anywhere: the word
   alone or with a letter or number, then optionally ":", ".", or a dash and a title
   ("Appendix A: Proofs", "Appendix A - Proofs"), or a line that starts with the word and has
   every word capitalised ("Appendix A Proofs", "A PPENDIX A P ROOFS").
   With limits.appendix_allowed true, such a heading is a note, not a failure.
   Other mentions of "appendix" are notes.
   Only headings that carry the word are seen (IEEEtran's \appendix prints "APPENDIX"); a
   lettered section without it, as the article class makes, is not.
3. Abstract words, counted two ways; fail when either is above --max-words (default
   limits.max_abstract_words):
   a. the PDF text from the abstract heading to "Index Terms", "Keywords" or the first section
      heading;
   b. --abstract-tex between \begin{abstract} and \end{abstract}, with % comments dropped, the
      arguments of \cite, \ref, \label, \url and the URL of \href dropped, "\name{}" kept as one
      word (the text-macro idiom, e.g. \examplesys{}), and other command names dropped with their
      argument text kept.
   A word is a whitespace-separated token with a letter or digit in it. The PDF count runs
   high: small caps split words ("E XAMPLE S YS" is 4 tokens) and \tofill{T12} prints
   "[TOFILL T12]" (2 tokens, 1 in the .tex count).
   A missing abstract heading or end marker, or a .tex abstract with no words, fails (the check
   does not pass on what it cannot see).

Exit 0 when every check passes, 1 when a limit is exceeded or the abstract cannot be found,
2 on a usage or tool error (missing file, pdftotext absent).
anonymity_scan.py imports load_text, is_heading, REFS, run_tool, shown and die from here.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from paper_config import load


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def shown(path):
    """The path relative to the project root (paper_config) when it lies inside it."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(load()["project"]["root"].resolve()))
    except ValueError:
        return str(path)


def show(text, width=100):
    """One display line: whitespace collapsed, dashes plain (house rule: no em dash), cut."""
    s = re.sub(r"\s+", " ", text).strip().replace("\N{EM DASH}", "-").replace("\u2013", "-")
    return s if len(s) <= width else s[: width - 3] + "..."


def run_tool(cmd):
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except FileNotFoundError:
        die(f"{cmd[0]} not found (poppler provides pdftotext, pdfinfo, pdfimages)")
    if out.returncode != 0:
        die(f"{' '.join(cmd)} failed: {out.stderr.strip()}")
    return out.stdout


def load_text(pdf=None, text=None):
    """The document text with a form feed after each page."""
    if text is not None:
        try:
            return Path(text).read_text(encoding="utf-8")
        except OSError as e:
            die(f"cannot read {text}: {e}")
    if not Path(pdf).is_file():
        die(f"no PDF at {pdf} (build it first with build.command, or pass --text)")
    return run_tool(["pdftotext", "-enc", "UTF-8", str(pdf), "-"])


def text_lines(raw):
    """(page, line_no, text) per line. line_no counts newlines as grep -n does; a form feed
    starts the next page (pdftotext puts it at the start of that page's first line)."""
    rows, page = [], 1
    for no, line in enumerate(raw.split("\n"), 1):
        for k, part in enumerate(line.split("\f")):
            if k:
                page += 1
            rows.append((page, no, part))
    return rows


def page_count(raw):
    body = raw.rstrip("\n ")
    n = body.count("\f")
    return n if body.endswith("\f") else n + 1


def squash(line):
    """Heading test form: pdftotext prints small caps as "R EFERENCES", so drop every space."""
    return re.sub(r"\s+", "", line).upper()


NUM = r"(?:[IVX]+\.|[A-Z]\.|\d+(?:\.\d+)*\.?)?"
REFS = re.compile(rf"^{NUM}(?:REFERENCES|BIBLIOGRAPHY)$")
APPENDIX = re.compile(
    rf"^{NUM}(?:APPENDIX|APPENDICES|SUPPLEMENT(?:ARY|AL)(?:MATERIALS?|SECTIONS?)?)"
    r"(?:[A-Z]|[IVX]+|\d+)?(?:[:.\-\u2013\N{EM DASH}].+)?$"
)
APPENDIX_START = re.compile(rf"^{NUM}(?:APPENDIX|APPENDICES|SUPPLEMENT(?:ARY|AL))")
ABS_HEAD = re.compile(r"^\s*A\s?BSTRACT(?![a-z])", re.I)
ABS_END = re.compile(r"^\s*(?:I\s?NDEX\s?T\s?ERMS|K\s?EY\s?WORDS)(?![a-z])", re.I)
SECTION = re.compile(r"^(?:[IVX]+\.|\d+\.?)\s+(\S.*)$")
BARE_NUMBER = re.compile(r"^\s*(?:[IVX]+\.|\d+\.?)\s*$")
MINOR = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def is_heading(line, pattern):
    """A short line that starts with a capital or digit and matches pattern once squashed.
    A line ending in "." or "," is a sentence fragment, not a heading."""
    s = line.strip()
    if not s or len(s) > 80 or s[-1] in ".," or not (s[0].isupper() or s[0].isdigit()):
        return False
    return bool(pattern.match(squash(s)))


def is_appendix_heading(line):
    """APPENDIX matches, or the line starts with the word and every word is capitalised."""
    if is_heading(line, APPENDIX):
        return True
    words = line.split()
    return is_heading(line, APPENDIX_START) and all(
        not w[0].isalpha() or w[0].isupper() or w in MINOR for w in words
    )


def is_section_heading(line):
    """ "I. I NTRODUCTION", "1 Introduction", "INTRODUCTION": numbered, every word capitalised."""
    s = line.strip()
    if not s or len(s) > 60 or s.endswith("."):
        return False
    if squash(s) == "INTRODUCTION":
        return True
    m = SECTION.match(s)
    return bool(m) and all(w[0].isupper() or w in MINOR for w in m.group(1).split())


WORD = re.compile(r"[A-Za-z0-9]")


def count_words(text):
    return sum(1 for tok in text.split() if WORD.search(tok))


def body_pages(rows, n_pages):
    """(body pages, (page, line) of the references heading or None, text precedes it).
    The last heading-like line wins: a lone "References" in the body (a table header) must not
    end the body early."""
    for i in range(len(rows) - 1, -1, -1):
        page, no, t = rows[i]
        if is_heading(t, REFS):
            before = any(
                r[2].strip() and not r[2].strip().isdigit() for r in rows[:i] if r[0] == page
            )
            return (page if before else page - 1), (page, no), before
    return n_pages, None, False


def pdf_abstract(rows):
    """(words, (page, first line), last line) from the abstract heading to its end marker,
    or a string saying what was not found."""
    for i, (page, no, t) in enumerate(rows):
        m = ABS_HEAD.match(t)
        if m:
            break
    else:
        return "no abstract heading in the PDF text"
    text = t[m.end() :].lstrip(" \t:.-\u2013\N{EM DASH}")
    last = no
    rest = rows[i + 1 :]
    for j, (_, n, line) in enumerate(rest):
        numbered = False
        if BARE_NUMBER.match(line):  # pdftotext may print "1", a blank line, "Introduction"
            after = next((r[2] for r in rest[j + 1 :] if r[2].strip()), "")
            numbered = is_section_heading(f"{line.strip()} {after.strip()}")
        if ABS_END.match(line) or is_section_heading(line) or numbered:
            return count_words(text), (page, no), last
        # pdftotext keeps a hyphen that ends a line inside a compound: join without a space
        text = text + line if text.endswith("-") else text + " " + line
        if line.strip():
            last = n
    return f"no end of the abstract (Index Terms, Keywords or a section heading) after line {no}"


def tex_abstract(path):
    """(words, first line, last line) of the abstract in a .tex file (see module docstring)."""
    try:
        src = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        die(f"cannot read {path}: {e}")
    src = re.sub(r"(?<!\\)%.*", "", src)  # comments; newlines stay, so line numbers hold
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S)
    if m:
        body, first = m.group(1), src[: m.start()].count("\n") + 1
        last = src[: m.end()].count("\n") + 1
    else:
        body, first, last = src, 1, src.count("\n") + 1
    body = re.sub(r"\$[^$]*\$", " math ", body)
    body = re.sub(r"\\href\{[^}]*\}", " ", body)
    body = re.sub(
        r"\\(?:[A-Za-z]*cite[A-Za-z]*|[A-Za-z]*ref|label|url)\*?(?:\[[^\]]*\])*\{[^}]*\}",
        " ",
        body,
    )
    body = re.sub(r"\\([A-Za-z]+)\{\}", r" \1 ", body)
    body = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", body)
    body = re.sub(r"\\.", " ", body).replace("~", " ").replace("{", "").replace("}", "")
    return count_words(body), first, last


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="The venue's page, appendix and abstract limits (limits.* in paper-tools.toml)."
    )
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--pdf", type=Path, help="built PDF (default: build.pdf in paper-tools.toml)")
    src.add_argument("--text", type=Path, help="text dump with a form feed after each page")
    ap.add_argument(
        "--abstract-tex", type=Path, help="abstract source (default: paper.abstract_tex)"
    )
    ap.add_argument("--max-pages", type=int, help="body page limit (default: limits.max_pages)")
    ap.add_argument(
        "--max-words", type=int, help="abstract word limit (default: limits.max_abstract_words)"
    )
    args = ap.parse_args(argv)
    cfg = load()
    if args.abstract_tex is None:
        args.abstract_tex = cfg["paper"]["abstract_tex"]
    if args.max_pages is None:
        args.max_pages = cfg["limits"]["max_pages"]
    if args.max_words is None:
        args.max_words = cfg["limits"]["max_abstract_words"]

    pdf = None if args.text else (args.pdf or cfg["build"]["pdf"])
    raw = load_text(pdf=pdf, text=args.text)
    label = shown(args.text or pdf)
    rows = text_lines(raw)
    n_pages = page_count(raw)
    fails = 0

    def loc(page, no):
        return f"{label}:{no} (page {page})"

    def report(ok, msg):
        nonlocal fails
        fails += not ok
        print(("PASS " if ok else "FAIL ") + msg)

    how = "pdftotext lines" if pdf else "lines of the text file"
    print(f"paper_limits: {label}, {n_pages} page(s) ({how})")

    body, ref, before = body_pages(rows, n_pages)
    if ref:
        why = f"references heading at {loc(*ref)}; " + (
            "text or a float precedes it, so that page counts" if before else "top of page"
        )
    else:
        why = "no references heading, every page counted"
    report(body <= args.max_pages, f"body pages {body} (limit {args.max_pages}): {why}")

    heads = [(p, n, t) for p, n, t in rows if is_appendix_heading(t)]
    for p, n, t in heads:
        if cfg["limits"]["appendix_allowed"]:
            print(f'NOTE appendix heading at {loc(p, n)}: "{show(t)}" (limits.appendix_allowed)')
        else:
            report(False, f'appendix heading at {loc(p, n)}: "{show(t)}"')
    if not heads:
        report(True, "no appendix or supplementary heading")

    got = pdf_abstract(rows)
    if isinstance(got, str):
        report(False, f"abstract words (PDF text): {got}")
    else:
        words, (p, first), last = got
        report(
            words <= args.max_words,
            f"abstract words (PDF text) {words} (limit {args.max_words}): "
            f"{label}:{first}-{last} (page {p})",
        )
    words, first, last = tex_abstract(args.abstract_tex)
    report(
        0 < words <= args.max_words,
        f"abstract words (.tex, commands stripped) {words} (limit {args.max_words}"
        f"{'; no words found' if not words else ''}): "
        f"{shown(args.abstract_tex)}:{first}-{last}",
    )

    for p, n, t in rows:
        if re.search(r"\bappendi(?:x|ces)\b", t, re.I) and not is_appendix_heading(t):
            print(f'NOTE appendix mention at {loc(p, n)}: "{show(t)}"')

    code = 1 if fails else 0
    print(f"paper_limits: {fails} check(s) failed; exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
