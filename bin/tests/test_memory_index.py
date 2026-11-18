"""bin/health.d/memory.py: `index DIR` prints the same MEMORY.md bytes for the same notes, one line per note under the
section its type picks, within 100 lines and 10,000 bytes; `lint DIR` FAILs each broken rule by name and NOTEs undated
absolute words without failing.

Every case builds its folder in tmp_path and drives the command line, as the dream gates and sync runs will.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "bin" / "health.d" / "memory.py"
TAG = "[mac 1a2b3c4d 2026-11-13]"
BODY = f"- a fact; see [[hosts]] and `[[:space:]]` {TAG}\n```\n[[in-a-fence]] you must\n```\n## History\n- never do X\n"


def note(folder: Path, stem: str, description: str = "d", type_: str = "feedback", body: str = BODY) -> Path:
    path = folder / f"{stem}.md"
    path.write_text(f"---\nname: {stem}\ndescription: {description}\nmetadata:\n  node_type: memory\n  type: {type_}\n"
                    f"---\n{body}")
    return path


def folder(tmp: Path) -> Path:
    """A clean memory folder: a header, a stale hand-written MEMORY.md, a stub and one note of each type."""
    d = tmp / "memory"
    d.mkdir()
    (d / "MEMORY.header.md").write_text("# MEMORY - t\n\n> Purpose.\n\n\n")
    (d / "MEMORY.md").write_text("old hand index\n")
    (d / "old-traps.md").write_text("MOVED TO [[git-traps]]\n")
    note(d, "git-traps", "Git facts", "reference")
    note(d, "hosts", '"Host facts"', "reference")
    note(d, "plain_words", "'Plain words'", "feedback")
    note(d, "the-project", "Project note", "project")
    note(d, "about-him", "Who he is", "user")
    (d / "attic.md").mkdir()  # a folder is not a note
    return d


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True)


def fail_rules(out: bytes) -> set:
    return set(re.findall(r"^FAIL (\S+) ", out.decode(), re.M))


WANT = b"""# MEMORY - t

> Purpose.

## Tool and host facts
- [Git traps](git-traps.md) - Git facts
- [Hosts](hosts.md) - Host facts

## Working preferences
- [Plain words](plain_words.md) - Plain words

## Project
- [The project](the-project.md) - Project note

## About the user
- [About him](about-him.md) - Who he is
"""


def test_index_lists_each_note_once_under_its_type(tmp_path):
    r = run("index", folder(tmp_path))
    assert (r.returncode, r.stdout, r.stderr) == (0, WANT, b"")


def test_index_puts_other_types_last_and_drops_an_empty_description(tmp_path):
    d = folder(tmp_path)
    (d / "MEMORY.header.md").unlink()
    note(d, "odd", "Odd one", "musing")
    (d / "bare.md").write_text("---\nname: bare\nmetadata:\n  type: user\n---\n")
    (d / "loose.md").write_text("no frontmatter\n")
    (d / "spaced.md").write_text("---\nname: spaced\nmetadata:\n\n  type: user\n---\n")
    r = run("index", d)
    assert r.returncode == 0
    assert r.stdout.startswith(b"# MEMORY\n\n## Tool and host facts\n")
    assert r.stdout.endswith(b"- [About him](about-him.md) - Who he is\n- [Bare](bare.md)\n- [Spaced](spaced.md)\n\n"
                             b"## Unsorted\n- [Loose](loose.md)\n- [Odd](odd.md) - Odd one\n")


def test_index_strips_only_trailing_newlines_from_the_header(tmp_path):
    (tmp_path / "MEMORY.header.md").write_text("# M\n\n> Last line ends in a hard break." + " " * 2 + "\n\n")
    assert run("index", tmp_path).stdout == b"# M\n\n> Last line ends in a hard break.  \n"


def test_index_is_the_same_bytes_whatever_the_write_order_or_file_times(tmp_path):
    a = folder(tmp_path)
    b = tmp_path / "copy"
    b.mkdir()
    for f in sorted(a.iterdir(), reverse=True):
        (b / f.name).mkdir() if f.is_dir() else shutil.copy(f, b / f.name)
    (b / "hosts.md").touch()
    assert run("index", a).stdout == run("index", a).stdout == run("index", b).stdout == WANT


@pytest.mark.parametrize("notes, rc", [(97, 0), (98, 1)])
def test_index_line_budget(tmp_path, notes, rc):
    d = tmp_path / "m"
    d.mkdir()
    for i in range(notes):
        note(d, f"n{i:03}", body="")
    r = run("index", d)
    assert r.returncode == rc
    assert r.stdout.count(b"\n") == notes + 3 and b"- [N096](n096.md) - d\n" in r.stdout
    assert (b"100 lines" in r.stderr and b"10000 bytes" in r.stderr) == bool(rc)


@pytest.mark.parametrize("size, rc", [(9_999, 0), (10_000, 1)])
def test_index_byte_budget(tmp_path, size, rc):
    (tmp_path / "MEMORY.header.md").write_text("x" * size)
    r = run("index", tmp_path)
    assert (r.returncode, len(r.stdout)) == (rc, size + 1)
    assert (b"10000 bytes" in r.stderr) == bool(rc)


def test_lint_passes_a_clean_folder(tmp_path):
    r = run("lint", folder(tmp_path))
    assert (r.returncode, r.stdout) == (0, b"lint: 6 notes, 0 FAIL, 0 NOTE\n")


def big(d: Path, size: int) -> None:
    path = note(d, "hosts", "Host facts", "reference", body="")
    path.write_text(path.read_text() + "x" * (size - path.stat().st_size - 1) + "\n")


# Each case plants one fault in a clean folder.
FAULTS = {
    "frontmatter": lambda d: (d / "loose.md").write_text("just text\n"),
    "frontmatter-empty": lambda d: (d / "empty.md").write_text(""),
    "frontmatter-unclosed": lambda d: (d / "open.md").write_text("---\nname: open\n"),
    "name": lambda d: (d / "hosts.md").write_text((d / "hosts.md").read_text().replace("name: hosts", "name: host")),
    "description-missing": lambda d: (d / "bare.md").write_text("---\nname: bare\nmetadata:\n  type: user\n---\n"),
    "description-empty": lambda d: note(d, "hosts", '""', "reference"),
    "description-block": lambda d: note(d, "hosts", ">-", "reference"),
    "description-long": lambda d: note(d, "hosts", "x" * 121, "reference"),
    "type-missing": lambda d: (d / "hosts.md").write_text((d / "hosts.md").read_text().replace("  type: reference\n", "")),
    "type-top-level": lambda d: (d / "top.md").write_text("---\nname: top\ndescription: d\ntype: user\n---\n"),
    "type-other-key": lambda d: (d / "top.md").write_text("---\nname: top\ndescription: d\ntags:\n  type: user\n---\n"),
    "type-other": lambda d: note(d, "hosts", "Host facts", "musing"),
    "size": lambda d: big(d, 102_401),
    "link-body": lambda d: note(d, "hosts", "Host facts", "reference", body=f"## History\n- see [[nowhere]] {TAG}\n"),
    "link-stub": lambda d: (d / "older.md").write_text("MOVED TO [[nowhere]]\n"),
    "link-index": lambda d: note(d, "hosts", "Host facts", "reference", body="- see [[MEMORY]]\n"),
    "autodream": lambda d: (d / ".consolidate-lock").touch(),
    "budget": lambda d: [note(d, f"n{i}", body="") for i in range(100)],
}


@pytest.mark.parametrize("case", FAULTS)
def test_lint_fails_a_planted_fault_by_its_rule_only(tmp_path, case):
    d = folder(tmp_path)
    FAULTS[case](d)
    r = run("lint", d)
    assert r.returncode == 1
    assert fail_rules(r.stdout) == {case.split("-")[0]}


# A [[link]] inside code is no link, so the note lints clean.
IN_CODE = {
    "nested-fence": "````\n```bash\n[[in-code]]\n```\n````\n",
    "backticks-in-tildes": "~~~\n```\n[[in-code]]\n~~~\n",
    "longer-close": "```\n[[in-code]]\n`````  \n",
    "text-after-ticks-is-no-close": "```\n``` text\n[[in-code]]\n```\n",
    "unclosed-fence": "```\n[[in-code]]\n",
    "multiline-span": "Example: `line one\n[[in-code]]\nline three`.\n",
    "quoted-multiline-span": "> Example: `line one\n> [[in-code]]\n>line three`.\n",
    "lazy-quote-line": "> Example `a\nb [[in-code]]`\n",
    "indented-dash-continues-a-paragraph": "foo `x\n    - b [[in-code]]`\n",
    "item-2-continues-a-paragraph": "run `x\n2. see [[in-code]] `\n",
    "empty-item-continues-a-paragraph": "run `x\n*\nsee [[in-code]] `\n",
    "span-in-heading": "## See `[[in-code]]`\n",
    "sibling-number-opens-an-item": "- a\n2. b `x\n    - see` [[in-code]] `c`\n",
    "double-tick-span": "``a ` [[in-code]]``\n",
    "longer-run-is-no-close": "`a ``` [[in-code]] `\n",
}


@pytest.mark.parametrize("case", IN_CODE)
def test_lint_skips_a_link_in_code(tmp_path, case):
    d = folder(tmp_path)
    note(d, "hosts", "Host facts", "reference", body=IN_CODE[case])
    r = run("lint", d)
    assert (r.returncode, r.stdout) == (0, b"lint: 6 notes, 0 FAIL, 0 NOTE\n")


# A broken [[link]] after something that only looks like code, or after code that has closed, still FAILs on its line.
AFTER_CODE = {
    "tildes-in-backticks": ("```text\n~~~\n```\n[[nowhere]]\n", 11),
    "short-close": ("````\n```\n````\n[[nowhere]]\n", 11),
    "ticks-in-info-string": ("```cmd``` text\n[[nowhere]]\n", 9),
    "span-stops-at-blank-line": ("`open\n\n[[nowhere]] `\n", 10),
    "unmatched-tick-run": ("``a` [[nowhere]]\n", 8),
    "span-stops-at-bullet": ("- use the ` key\n- see [[nowhere]]\n- and `x`\n", 9),
    "span-stops-at-numbered-item": ("run `x\n1. see [[nowhere]] `\n", 9),
    "span-stops-at-heading": ("run `x\n## Links\n[[nowhere]] `\n", 10),
    "span-stops-after-heading": ("## Run `x\nsee [[nowhere]] `\n", 9),
    "span-stops-after-setext-heading": ("Example `key\n===\nsee [[nowhere]] and `x`\n", 10),
    "span-stops-at-setext-dashes": ("run `x\n--\n[[nowhere]] `\n", 10),
    "span-stops-at-thematic-break": ("run `x\n_ _ _\n[[nowhere]] `\n", 10),
    "span-stops-after-quoted-heading": ("> # Run `x\n> see [[nowhere]] `\n", 9),
    "span-stops-at-nested-item": ("- a\n  - b `x\n    - see [[nowhere]] `\n", 10),
    "span-closes-before-indented-dash": ("foo `x\n    - b` [[nowhere]] `c`\n", 9),
    "item-continues-after-blank": ("- a\n\n  b `x\n    - see [[nowhere]] `\n", 11),
    "wide-gap-item-content-column": ("-      a `x\n       - b` [[nowhere]] `c`\n", 9),
    "quote-ends-an-item-paragraph": ("- a `x\n> see [[nowhere]] `\n", 9),
    "heading-ends-an-item-paragraph": ("- a `x\n# see [[nowhere]] `\n", 9),
    "thematic-break-ends-an-item-paragraph": ("- a `x\n***\n[[nowhere]] `\n", 10),
    "heading-then-closed-span": ("# Example: `key\nSee [[nowhere]] and `x`\n", 9),
    "span-stops-at-sibling-item": ("1. a `x\n2. see [[nowhere]] `\n", 9),
    "span-stops-at-quote": ("run `x\n> see [[nowhere]] `\n", 9),
    "span-stops-at-fence": ("run `x\n```\ncode\n```\n[[nowhere]] `\n", 12),
}


@pytest.mark.parametrize("case", AFTER_CODE)
def test_lint_fails_a_broken_link_outside_code(tmp_path, case):
    body, line = AFTER_CODE[case]
    d = folder(tmp_path)
    note(d, "hosts", "Host facts", "reference", body=body)
    r = run("lint", d)
    assert (r.returncode, re.findall(rb"^FAIL (\S+ \S+):", r.stdout, re.M)) == (1, [f"link hosts.md:{line}".encode()])


def test_lint_rule_limits_are_inclusive(tmp_path):
    d = folder(tmp_path)
    note(d, "git-traps", "x" * 120, "reference")
    big(d, 102_400)
    r = run("lint", d)
    assert (r.returncode, r.stdout) == (0, b"lint: 6 notes, 0 FAIL, 0 NOTE\n")


# Built at run time, so no credential-shaped literal sits in this file.
SECRETS = ["sk-ant-" + "api03-" + "a" * 24, "gh" + "p_" + "b" * 30, "gh" + "s_" + "c" * 30, "github" + "_pat_" + "d" * 30,
           "AK" + "IA" + "E" * 16, "xo" + "xb-" + "1234567890-abc", "https://hooks." + "slack.com/services/T0/B0/xyz",
           "-----BEGIN " + "OPENSSH PRIVATE KEY-----"]


@pytest.mark.parametrize("secret", SECRETS)
def test_lint_fails_a_credential_without_printing_it(tmp_path, secret):
    d = folder(tmp_path)
    note(d, "hosts", "Host facts", "reference", body=f"- a fact {TAG}\n- token {secret}\n")
    r = run("lint", d)
    assert r.returncode == 1
    assert re.findall(rb"^FAIL (\S+ \S+):", r.stdout, re.M) == [b"secret hosts.md:9"]
    assert secret.encode() not in r.stdout + r.stderr


def test_lint_passes_a_bare_credential_prefix(tmp_path):
    d = folder(tmp_path)
    note(d, "hosts", "Host facts", "reference", body="- keys start with sk-ant- and ghp_\n")
    assert run("lint", d).returncode == 0


def test_lint_notes_undated_absolute_words_without_failing(tmp_path):
    d = folder(tmp_path)
    note(d, "rule", body=f"- you MUST always run X\n- never skip Y {TAG}\n```\n- always Z\n```\n## History\n- always W\n")
    note(d, "plain_words", "Never guess", "feedback")
    note(d, "dated", f"Always ask {TAG}", "user")
    r = run("lint", d)
    assert (r.returncode, r.stdout) == (0, b"NOTE absolute plain_words.md:description: 'Never' with no date tag\n"
                                           b"NOTE absolute rule.md:8: 'MUST' with no date tag\n"
                                           b"lint: 8 notes, 0 FAIL, 2 NOTE\n")


def test_lint_prints_fails_before_notes(tmp_path):
    d = folder(tmp_path)
    note(d, "about-him", "You must", "user")
    note(d, "hosts", "Host facts", "musing")
    out = run("lint", d).stdout.decode().splitlines()
    assert [line.split()[0] for line in out] == ["FAIL", "NOTE", "lint:"]


@pytest.mark.parametrize("args", [[], ["index"], ["lint", "missing"], ["frob", "."], ["index", ".", "extra"]])
def test_bad_arguments_print_usage_and_exit_2(tmp_path, args):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, cwd=tmp_path)
    assert (r.returncode, r.stdout) == (2, b"")
    assert r.stderr.startswith(b"usage:")
