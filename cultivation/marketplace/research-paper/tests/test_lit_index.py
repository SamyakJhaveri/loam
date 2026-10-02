"""Fixture test for ../scripts/lit_index.py. No network.

Fixtures in fixtures/lit_index/: refs.bib (Alpha2024 with a DOI, cited; Gamma2023 with an
arXiv id, cited only inside a % comment), main.tex (inputs sections/intro.tex), and notes.md,
whose "## Kept" section names Alpha three ways (a table row matched by DOI, a list item
matched by title only, a backticked key) and Beta (a table row, in no bib), and whose
"## Skipped" section names Epsilon.
So with notes.md::## Kept: Alpha is in both, Beta only in the notes, Gamma only in the bib.
Fixtures in fixtures/lit_index_self/ (literature.self_names and --self-name): paper-tools.toml
lists a synthetic project's self names (its system name ExampleSys, its preprint id
2901.00001, three prior works by bib key and by system name) and literature.notes; refs.bib
holds the three self keys under titles that do not name them, plus Other2024; notes.md holds
a preprint known only by the arXiv id 2901.00001 and a record whose title holds ExampleSys;
notes_only.md with refs_other.bib names three self works that no bib entry holds (a
backticked key and two table rows by system name).
Run from the repository root: python3 -m pytest <this file> -q
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "lit_index.py"
FIX = HERE / "fixtures" / "lit_index"
SELF = HERE / "fixtures" / "lit_index_self"


def call(args, cwd, config=None):
    """Run the script with the project root at cwd and, when given, a fixture config."""
    env = {**os.environ, "PAPER_TOOLS_ROOT": str(cwd)}
    env.pop("PAPER_TOOLS_CONFIG", None)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def run(*args):
    return call(["--bib", "refs.bib", "--main", "main.tex", *args], FIX)


def index(tmp_path, notes="notes.md::## Kept"):
    out = tmp_path / "index.json"
    proc = run("--notes", notes, "--out", str(out))
    assert proc.returncode == 0, proc.stderr
    return {(p["keys"] or p["names"])[0]: p for p in json.loads(out.read_text())["papers"]}


def test_paper_in_both_bib_and_notes(tmp_path):
    alpha = index(tmp_path)["Alpha2024"]
    assert alpha["has_bib_key"] and alpha["cited_in_build"]
    assert alpha["bib"][0]["cite_locations"] == ["sections/intro.tex:2"]
    assert alpha["doi"][0] == "10.5555/alpha.2024"
    assert [(m["file"], m["line"], m["kind"]) for m in alpha["mentions"]] == [
        ("notes.md", 7, "table-row"),
        ("notes.md", 10, "list-item"),
        ("notes.md", 12, "key"),
    ]
    assert all(m["has_bib_key"] for m in alpha["mentions"])
    assert {"doi", "title", "key"} <= set(alpha["matched_by"])


def test_paper_only_in_notes(tmp_path):
    beta = index(tmp_path)["Beta"]
    assert beta["keys"] == [] and not beta["has_bib_key"] and not beta["cited_in_build"]
    assert beta["title"] == "Beta: A Survey of GPU Porting"
    assert beta["arxiv"] == ["2402.00002"]
    assert [(m["file"], m["line"], m["has_bib_key"]) for m in beta["mentions"]] == [
        ("notes.md", 8, False)
    ]


def test_paper_only_in_bib(tmp_path):
    papers = index(tmp_path)
    gamma = papers["Gamma2023"]
    assert gamma["has_bib_key"] and gamma["mentions"] == []
    assert not gamma["cited_in_build"], "a \\cite behind % must not count"
    assert gamma["arxiv"] == ["2301.00001"] and gamma["arxiv_only"] is True
    assert sorted(papers) == ["Alpha2024", "Beta", "Gamma2023"]


def test_heading_selector_limits_the_notes(tmp_path):
    assert "Epsilon" in index(tmp_path, "notes.md")
    proc = run("--notes", "notes.md::## Missing", "--out", str(tmp_path / "x.json"))
    assert proc.returncode == 2 and "no heading starts with" in proc.stderr


def test_search_ranks_the_matching_paper_first(tmp_path):
    proc = run(
        "--notes",
        "notes.md::## Kept",
        "--out",
        str(tmp_path / "i.json"),
        "--search",
        "stencil kernels",
    )
    assert proc.returncode == 0, proc.stderr
    first = proc.stdout.splitlines()[0]
    assert "keys=Gamma2023" in first and " 2/2 " in first


def test_sentences_mode_flags_cites():
    proc = call(["--sentences", "--main", "main.tex", "--sections", "sections"], FIX)
    assert proc.returncode == 0, proc.stderr
    rows = [line.split("\t") for line in proc.stdout.splitlines()[:-1]]
    assert rows == [
        ["sections/intro.tex:2", "cite", "Alpha checks kernels~\\cite{Alpha2024}."],
        ["sections/intro.tex:2", "nocite", "Most porting tools miss races, e.g. Stencil codes."],
        ["sections/intro.tex:4", "nocite", "We present a benchmark."],
    ]
    assert proc.stdout.splitlines()[-1].startswith(
        "lit_index: 3 sentences (2 without \\cite) in 1 files"
    )


def test_sentences_mode_takes_the_sections_folder_from_the_config(tmp_path):
    """No --sections: paper.sections_dir (absolute after loading) still matches the build
    files, which the scan reaches through the relative --main."""
    config = tmp_path / "paper-tools.toml"
    config.write_text('[paper]\nsections_dir = "sections"\n')
    proc = call(["--sentences", "--main", "main.tex"], FIX, config)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.splitlines()[-1].startswith(
        "lit_index: 3 sentences (2 without \\cite) in 1 files: sections/intro.tex"
    )


def doi_index(tmp_path):
    """fixtures/lit_index_doi/: each note names a bib paper only by a DOI URL, under a name
    that shares no word with the bib entry, so only the DOI can join them."""
    out = tmp_path / "doi.json"
    proc = call(
        ["--bib", "refs.bib", "--main", "main.tex", "--notes", "notes.md", "--out", str(out)],
        HERE / "fixtures" / "lit_index_doi",
    )
    assert proc.returncode == 0, proc.stderr
    papers = json.loads(out.read_text())["papers"]
    return {(p["keys"] or p["names"])[0]: p for p in papers}


def test_doi_inside_a_publisher_url_in_the_bib_joins_the_note(tmp_path):
    papers = doi_index(tmp_path)
    baz = papers["Baz2022"]
    assert baz["doi"] == ["10.1145/5555555.6666666"] and "doi" in baz["matched_by"]
    assert [m["line"] for m in baz["mentions"]] == [5]
    assert "Poe et al. offload study" not in papers


def test_doi_url_with_a_query_string_joins_the_bib(tmp_path):
    papers = doi_index(tmp_path)
    qux = papers["Qux2021"]
    assert qux["doi"] == ["10.1016/j.future.2021.01.001"] and "doi" in qux["matched_by"]
    assert [m["line"] for m in qux["mentions"]] == [6]
    assert sorted(papers) == ["Baz2022", "Qux2021"]


SELF_KEYS = ["PriorSysA2018", "PriorSysB2019", "PriorSysC2016"]


def self_index(tmp_path, *self_args):
    """fixtures/lit_index_self/ with its config (which names notes.md), keyed by bib key,
    else arXiv id, else DOI."""
    out = tmp_path / "self.json"
    proc = call(
        ["--bib", "refs.bib", "--main", "main.tex", "--out", str(out), *self_args],
        SELF,
        SELF / "paper-tools.toml",
    )
    assert proc.returncode == 0, proc.stderr
    papers = json.loads(out.read_text())["papers"]
    return {(p["keys"] or p["arxiv"] or p["doi"])[0]: p for p in papers}


def test_config_self_names_mark_the_authors_own_works(tmp_path):
    papers = self_index(tmp_path)
    for key in SELF_KEYS:
        assert papers[key]["self_citation"] and papers[key]["self_match"][0] == key, key
    assert papers["2901.00001"]["self_match"] == ["2901.00001"]
    assert papers["10.5555/notes.2030"]["self_match"] == ["ExampleSys"]
    other = papers["Other2024"]
    assert not other["self_citation"] and other["self_match"] == []


def test_self_name_is_repeatable_and_replaces_the_config_list(tmp_path):
    papers = self_index(tmp_path, "--self-name", "Other2024", "--self-name", "2901.00001")
    marked = sorted(k for k, p in papers.items() if p["self_citation"])
    assert marked == ["2901.00001", "Other2024"]


def test_no_config_marks_no_self_work(tmp_path):
    """Without a config, literature.self_names and literature.notes are empty."""
    out = tmp_path / "bare.json"
    proc = call(["--bib", "refs.bib", "--main", "main.tex", "--out", str(out)], SELF)
    assert proc.returncode == 0, proc.stderr
    index = json.loads(out.read_text())
    assert index["notes"] == [] and index["self_names"] == []
    assert not any(p["self_citation"] for p in index["papers"])


def test_self_work_named_only_in_the_notes_is_marked(tmp_path):
    """notes_only.md names three self works that refs_other.bib lacks: a backticked key, and
    two table rows by system name."""
    out = tmp_path / "only.json"
    proc = call(
        ["--bib", "refs_other.bib", "--main", "main.tex"]
        + ["--notes", "notes_only.md", "--out", str(out)],
        SELF,
        SELF / "paper-tools.toml",
    )
    assert proc.returncode == 0, proc.stderr
    papers = {(p["keys"] or p["names"])[0]: p for p in json.loads(out.read_text())["papers"]}
    assert {k: p["self_match"] for k, p in papers.items()} == {
        "Other2024": [],
        "PriorSysC": ["PriorSysC"],
        "PriorSysB": ["PriorSysB"],
        "PriorSysA": ["PriorSysA"],
    }
