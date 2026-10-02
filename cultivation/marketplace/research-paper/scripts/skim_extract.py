#!/usr/bin/env python3
r"""Extract what a skimming reader sees, one file per reading pass (the skim test of docs/section-loop.md).

    paper-tool skim_extract OUT_DIR

Reads, from the working tree, the title macro (paper.title_macro) in paper.preamble_tex, the
abstract in paper.abstract_tex and the sections named in paper.sections (files in
paper.sections_dir), and writes four text files, comments stripped and the paper's macros
(paper.macros) spelled out:

- pass1.txt: the title and the abstract.
- pass2.txt: the last paragraph of the introduction (the contribution list with its lead-in), then
  every figure and table with its caption, as LaTeX source, in paper order.
- pass3.txt: the first paragraph of the introduction, then the first and the last paragraph of the
  discussion.
- pass4.txt: the section headings and the first sentence of every paragraph; a bold run-in header
  is kept in [brackets] before its sentence.

Each file is what one fresh `blind-reader` gets for its pass, with the files of the passes before
it. The reading order is that of "How I read a scientific paper in 20 minutes" and of McGill's
"The 5 pivotal paragraphs in a paper" (sources in the skim test of docs/section-loop.md).
"""

import re
import sys
from pathlib import Path

from paper_config import load

FLOAT = re.compile(r"\\begin\{(table\*?|figure\*?)\}.*?\\end\{\1\}", re.S)
FORMAT = re.compile(r"\\(?:textbf|emph|texttt|textsc|textit)\{([^{}]*)\}")
HEADER = re.compile(r"\\textbf\{([^{}]*\.)\}\s*")
SENTENCE = re.compile(r"(.*?[.?])(?:\s+(?=[A-Z\\])|$)", re.S)


def spell_out(text: str, macros: dict | None = None) -> str:
    """Comments, macros, citations, cross-references and escapes out; formatting commands stay."""
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("%"))
    for macro, name in (macros or {}).items():
        text = text.replace(macro, name)
    text = re.sub(r"~?\\cite\{[^}]*\}", " [cite]", text)
    text = re.sub(r"(Sections?|Table|Figure|Fig\.)~\\ref\{[^}]*\}", r"\1 X", text)
    text = re.sub(r"~?\\ref\{[^}]*\}", " X", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    for escaped, plain in (("~", " "), (r"\%", "%"), (r"\_", "_"), (r"\,", " "), ("{,}", ",")):
        text = text.replace(escaped, plain)
    return text.replace(r"\&", "&")


def plain(text: str) -> str:
    """Formatting commands out, nested once."""
    return FORMAT.sub(r"\1", FORMAT.sub(r"\1", text))


def paragraphs(text: str) -> list[str]:
    """The blank-line-separated blocks of a section, floats removed."""
    return [block.strip() for block in re.split(r"\n\s*\n", FLOAT.sub("", text)) if block.strip()]


def first_sentence(block: str) -> str:
    """The first sentence of a paragraph, after its run-in header if it has one."""
    block = " ".join(block.split())
    header = HEADER.match(block)
    rest = block[header.end() :] if header else block
    sentence = SENTENCE.match(rest)
    text = plain(sentence.group(1) if sentence else rest)
    return f"[{header.group(1)}] {text}" if header else text


def extracts(cfg: dict) -> dict[str, str]:
    """The four pass files, from the paper.* keys of a loaded config (paper_config.load())."""
    p = cfg["paper"]
    names = p["sections"] or [
        f.stem for f in sorted(p["sections_dir"].glob("*.tex")) if f != p["abstract_tex"]
    ]
    for key in ("intro_section", "discussion_section"):
        if p[key] not in names:
            sys.exit(f"skim_extract: paper.{key} {p[key]!r} is not one of the sections {names}")
    macros = p["macros"]
    tex = {
        name: spell_out((p["sections_dir"] / f"{name}.tex").read_text(), macros) for name in names
    }
    title = re.search(
        r"\\newcommand\{\\" + re.escape(p["title_macro"]) + r"\}\{(.*?)\}\s*$",
        p["preamble_tex"].read_text(),
        re.M,
    )
    if not title:
        sys.exit(
            f"skim_extract: no \\newcommand{{\\{p['title_macro']}}} line in {p['preamble_tex']}"
        )
    abstract = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        spell_out(p["abstract_tex"].read_text(), macros),
        re.S,
    )
    if not abstract:
        sys.exit(f"skim_extract: no abstract environment in {p['abstract_tex']}")
    intro = [b for b in paragraphs(tex[p["intro_section"]]) if not b.startswith("\\section")]
    discussion = [
        b for b in paragraphs(tex[p["discussion_section"]]) if not b.startswith("\\section")
    ]
    # The contribution list ends the introduction; without the word, its last paragraph stands in.
    last_intro = max(
        (k for k, block in enumerate(intro) if "contributions" in block), default=len(intro) - 1
    )
    floats = []
    for name in names:
        for match in FLOAT.finditer(tex[name]):
            kind = "FIGURE" if match.group(1).startswith("figure") else "TABLE"
            body = re.sub(
                r"\\input\{figures/[^}]*\}",
                "[a drawn diagram; its text labels are not reproduced here]",
                match.group(0),
            )
            floats.append(f"--- {kind} (in section file {name}) ---\n{plain(body)}\n")
    lines = []
    for name in names:
        for block in paragraphs(tex[name]):
            for sub, heading in re.findall(r"\\(sub)?section\{(.*?)\}", block):
                lines.append(("\n### " if sub else "\n## ") + plain(heading))
            block = re.sub(r"\\(sub)?section\{.*?\}\s*", "", block).strip()
            if "\\item" in block:
                lines += [
                    f"- (list item) {first_sentence(i)}" for i in re.findall(r"\\item (.*)", block)
                ]
            elif block and not block.startswith(("\\begin", "\\end")):
                lines.append("- " + first_sentence(block))
    return {
        "pass1.txt": f"TITLE\n{plain(spell_out(title.group(1), macros))}\n\nABSTRACT\n{plain(abstract.group(1).strip())}\n",
        "pass2.txt": "LAST PARAGRAPH OF THE INTRODUCTION\n"
        + plain("\n".join(intro[last_intro:]))
        + "\n\nFIGURES AND TABLES WITH THEIR CAPTIONS, IN PAPER ORDER (LaTeX source of each)\n\n"
        + "\n".join(floats),
        "pass3.txt": "FIRST PARAGRAPH OF THE INTRODUCTION\n"
        + plain(intro[0])
        + "\n\nFIRST PARAGRAPH OF THE DISCUSSION SECTION\n"
        + plain(discussion[0])
        + "\n\nLAST PARAGRAPH OF THE DISCUSSION SECTION\n"
        + plain(discussion[-1])
        + "\n",
        "pass4.txt": "SECTION HEADINGS AND THE FIRST SENTENCE OF EVERY PARAGRAPH, IN PAPER ORDER\n"
        "(a phrase in [brackets] is the paragraph's bold run-in header)\n"
        + "\n".join(lines)
        + "\n",
    }


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, text in extracts(load()).items():
        (out / name).write_text(text)
        print(f"{out / name}: {len(text.split())} words")


if __name__ == "__main__":
    main()
