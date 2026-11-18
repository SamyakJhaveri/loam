"""Build the auto-memory index, MEMORY.md, from each note's own frontmatter, and lint the notes.

Usage: python3 memory.py index DIR | python3 memory.py lint DIR

A note is every DIR/*.md except MEMORY.md and MEMORY.header.md, in sorted file-name order, so the same notes give the
same bytes on any host. A note starts with a `---` line; its frontmatter ends at the next `---` line and holds top-level
`name:` and `description:` and, under top-level `metadata:`, an indented `type:`. A stub is a file whose whole text is
`MOVED TO [[slug]]`.

index prints MEMORY.header.md (or `# MEMORY`), then one section per type with one line per note; over 100 lines or
10,000 bytes it still prints the text, names the budget on stderr and exits 1. It writes no file: the caller does.

lint prints one `FAIL <rule> <file>[:<line>]: <reason>` line per broken rule, then one NOTE line per undated absolute
word (never, always, must) above `## History`, then a count line; it exits 1 when any FAIL was printed.
"""

import os
import re
import sys

SECTIONS = {"reference": "Tool and host facts", "feedback": "Working preferences", "project": "Project",
            "user": "About the user"}
UNSORTED = "Unsorted"
MAX_LINES, MAX_BYTES = 100, 10_000
MAX_NOTE_BYTES = 102_400
MAX_DESCRIPTION = 120
STUB = re.compile(r"MOVED TO \[\[[^\[\]]+\]\]")
LINK = re.compile(r"\[\[([^\[\]]+)\]\]")
TICKS = re.compile(r"`+")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")
QUOTE = re.compile(r"(?:[ \t]*> ?)*")
ITEM = re.compile(r"[ \t]*(?:[-+*]|\d{1,9}[.)])(?:\s|$)")
ONE_LINE_BLOCK = re.compile(r"[ \t]*(?:#{1,6}(?:\s|$)|([-*_])(?:[ \t]*\1){2,}[ \t]*$|=+[ \t]*$|-+[ \t]*$)")
BLOCK_SCALAR = re.compile(r"[>|][-+0-9]*")
ABSOLUTE = re.compile(r"\b(never|always|must)\b", re.I)
DATE_TAG = re.compile(r"\[[^\s\]]+ [0-9a-fA-F]{8} \d{4}-\d{2}-\d{2}\]")
SECRETS = [
    ("an Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}")),
    ("a GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}")),
    ("a GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("an AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("a Slack token", re.compile(r"\bxox[a-z]-[A-Za-z0-9-]{10,}")),
    ("a Slack webhook URL", re.compile(r"hooks\.slack\.com/(?:services|workflows|triggers)/\S+")),
    ("a PEM private key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")),
]


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def read_note(path: str) -> dict:
    """A note's lines, stub flag, frontmatter fields (None when it has none), index of its first body line, size."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    lines = text.splitlines()
    note = {"file": os.path.basename(path), "lines": lines, "stub": bool(STUB.fullmatch(text.strip())),
            "fields": None, "body": 0, "bytes": os.path.getsize(path)}
    if lines and lines[0].rstrip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
        if end is not None:
            fields, top = {}, None
            for line in lines[1:end]:
                key, sep, value = line.strip().partition(":")
                if not sep or not key:
                    continue
                if not line[:1].isspace():
                    top = key
                    fields[key] = unquote(value.strip())
                elif top == "metadata" and key == "type":
                    fields["metadata.type"] = unquote(value.strip())
            note["fields"], note["body"] = fields, end + 1
    return note


def unfenced(lines: list) -> list:
    """Per line, whether it is outside fenced code. As in CommonMark, a fence opens on 0-3 spaces and a run of three or
    more backticks (with no backtick after it) or tildes, and closes only on 0-3 spaces, a run of the same character at
    least as long and nothing but whitespace; an unclosed fence runs to the end."""
    out, close = [], None
    for line in lines:
        if close:
            out.append(False)
            if close.fullmatch(line):
                close = None
            continue
        m = FENCE.match(line)
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            close = re.compile(r" {0,3}%s{%d,}\s*" % (re.escape(m.group(1)[0]), len(m.group(1))))
        out.append(close is None)
    return out


def blank_code_spans(paragraph: list) -> list:
    """The paragraph's (quote prefix, content) lines, rejoined with each inline code span in the content blanked to
    spaces. As in CommonMark, a run of n backticks opens a span that the next run of exactly n backticks closes; a run
    with no such close is literal."""
    if not paragraph:
        return []
    text, out, i = "\n".join(content for _, content in paragraph), [], 0
    while m := TICKS.search(text, i):
        close = re.compile(f"(?<!`){m.group()}(?!`)").search(text, m.end())
        if close:
            out.append(text[i:m.start()] + re.sub(r"[^\n]", " ", text[m.start():close.end()]))
            i = close.end()
        else:
            out.append(text[i:m.end()])
            i = m.end()
    return [prefix + line for (prefix, _), line in zip(paragraph, ("".join(out) + text[i:]).split("\n"))]


def prose(lines: list, outside: list) -> list:
    """The lines with fenced and blank lines emptied and inline code spans blanked. As in CommonMark, a span stays in
    its paragraph, inside one quote depth; a blank or fenced line or a change of quote depth ends a paragraph, a list
    item starts one, and an ATX heading, setext underline or thematic break is a block of its own line. These match at
    any indent, so nested blocks split too: a split CommonMark would not make can only expose a link, never hide one."""
    out, paragraph, depth = [], [], 0
    for line, ok in zip(lines, outside):
        prefix = QUOTE.match(line).group() if ok else ""
        content = line[len(prefix):]
        one_line = ok and ONE_LINE_BLOCK.match(content)
        if not ok or not content.strip() or prefix.count(">") != depth or one_line or ITEM.match(content):
            out += blank_code_spans(paragraph)
            paragraph = []
        depth = prefix.count(">")
        if ok and content.strip():
            paragraph.append((prefix, content))
        else:
            out.append("")
        if one_line:
            out += blank_code_spans(paragraph)
            paragraph = []
    return out + blank_code_spans(paragraph)


def build_index(folder: str, notes: list) -> str:
    header_path = os.path.join(folder, "MEMORY.header.md")
    if os.path.isfile(header_path):
        with open(header_path, encoding="utf-8", errors="replace") as fh:
            header = fh.read().rstrip("\n")
    else:
        header = "# MEMORY"
    by_section = {h: [] for h in [*SECTIONS.values(), UNSORTED]}
    for note in notes:
        if note["stub"]:
            continue
        fields = note["fields"] or {}
        title = note["file"][:-3].replace("-", " ").replace("_", " ")
        line = f"- [{title[:1].upper() + title[1:]}]({note['file']})"
        if fields.get("description"):
            line += f" - {fields['description']}"
        by_section[SECTIONS.get(fields.get("metadata.type"), UNSORTED)].append(line)
    out = [header]
    for heading, rows in by_section.items():
        if rows:
            out += ["", f"## {heading}", *rows]
    return "\n".join(out) + "\n"


def over_budget(text: str) -> str:
    """Why the index is over its budget, or "" when it is within it."""
    n_lines, n_bytes = text.count("\n"), len(text.encode("utf-8"))
    if n_lines > MAX_LINES or n_bytes > MAX_BYTES:
        return f"{n_lines} lines and {n_bytes} bytes, over the budget of {MAX_LINES} lines and {MAX_BYTES} bytes"
    return ""


def lint_note(note: dict, stems: set) -> tuple:
    """The FAIL lines and the NOTE lines for one note."""
    f, fields, fails, notes = note["file"], note["fields"], [], []
    if fields is None and not note["stub"]:
        fails.append(f"FAIL frontmatter {f}: no frontmatter between a first `---` line and a closing `---` line")
    if fields is not None:
        if fields.get("name") != f[:-3]:
            fails.append(f"FAIL name {f}: name {fields.get('name')!r} is not the file stem {f[:-3]!r}")
        desc = fields.get("description")
        if not desc:
            fails.append(f"FAIL description {f}: description is missing or empty")
        elif BLOCK_SCALAR.fullmatch(desc):
            fails.append(f"FAIL description {f}: description is a block scalar ({desc}); write it on one line")
        elif len(desc) > MAX_DESCRIPTION:
            fails.append(f"FAIL description {f}: description is {len(desc)} characters, over {MAX_DESCRIPTION}")
        else:
            word = ABSOLUTE.search(desc)
            if word and not DATE_TAG.search(desc):
                notes.append(f"NOTE absolute {f}:description: '{word.group(1)}' with no date tag")
        if fields.get("metadata.type") not in SECTIONS:
            fails.append(f"FAIL type {f}: metadata type {fields.get('metadata.type')!r} is not one of "
                         + ", ".join(SECTIONS))
    if note["bytes"] > MAX_NOTE_BYTES:
        fails.append(f"FAIL size {f}: {note['bytes']} bytes, over {MAX_NOTE_BYTES}")
    for n, line in enumerate(note["lines"], 1):
        for label, pattern in SECRETS:
            if pattern.search(line):
                fails.append(f"FAIL secret {f}:{n}: line matches the pattern of {label}")
    body = note["lines"][note["body"]:]
    outside = unfenced(body)
    history = False
    for n, line, ok, text in zip(range(note["body"] + 1, len(note["lines"]) + 1), body, outside, prose(body, outside)):
        if not ok:
            continue
        history = history or line.rstrip() == "## History"
        for slug in LINK.findall(text):
            if slug not in stems:
                fails.append(f"FAIL link {f}:{n}: [[{slug}]] names no {slug}.md note")
        word = ABSOLUTE.search(line)
        if word and not history and not DATE_TAG.search(line):
            notes.append(f"NOTE absolute {f}:{n}: '{word.group(1)}' with no date tag")
    return fails, notes


def main(argv: list) -> int:
    if len(argv) != 2 or argv[0] not in ("index", "lint") or not os.path.isdir(argv[1]):
        print("usage: memory.py index DIR | memory.py lint DIR  (DIR: an auto-memory folder)", file=sys.stderr)
        return 2
    command, folder = argv
    names = sorted(n for n in os.listdir(folder) if n.endswith(".md") and n not in ("MEMORY.md", "MEMORY.header.md")
                   and os.path.isfile(os.path.join(folder, n)))
    notes = [read_note(os.path.join(folder, n)) for n in names]
    text = build_index(folder, notes)
    budget = over_budget(text)
    if command == "index":
        sys.stdout.buffer.write(text.encode("utf-8"))
        if budget:
            print(f"index: {budget}", file=sys.stderr)
        return 1 if budget else 0
    stems = {name[:-3] for name in names}
    fails, advisories = [], []
    for note in notes:
        note_fails, note_notes = lint_note(note, stems)
        fails += note_fails
        advisories += note_notes
    if os.path.exists(os.path.join(folder, ".consolidate-lock")):
        fails.append("FAIL autodream .consolidate-lock: Claude Code's built-in auto-dream left this lock; "
                     "turn auto-dream off so the notes have one writer")
    if budget:
        fails.append(f"FAIL budget MEMORY.md: the index would be {budget}")
    out = fails + advisories + [f"lint: {len(notes)} notes, {len(fails)} FAIL, {len(advisories)} NOTE"]
    sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
