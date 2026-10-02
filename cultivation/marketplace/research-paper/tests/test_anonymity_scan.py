"""Fixture tests for ../scripts/anonymity_scan.py (double-anonymous check).

Run from the plugin folder:
    python3 -m pytest tests/test_anonymity_scan.py -q

Fixtures in fixtures/anonymity_scan/ (invented people and places):
- CITATION.cff: two authors (one repeated under preferred-citation, which also names a
  conference that must not become a term), three affiliations' worth of terms;
- terms.txt: one term per kind; clean.txt: a two-page dump whose names appear only as
  "et al." citations or in the references, with the system name in small caps and plain;
- figures/: raster.png (listed, not scanned) and diagram.tex (a host in a comment: a note);
- baseline.txt: the fixture title as a known hit, with a reason; baseline_no_reason.txt: the
  same row with no reason.
Each seeded defect is clean.txt with one replacement, made in the test.
The shipped template ../templates/anonymity_terms.txt holds one synthetic term per kind.
Every run sets PAPER_TOOLS_ROOT (the fixture folder unless a test gives another), so the config
defaults never come from the repository the tests sit in.
The PDF cases build a one-page PDF with pdflatex and are skipped when it or poppler is missing.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "anonymity_scan.py"
TEMPLATE_TERMS = HERE.parent / "templates" / "anonymity_terms.txt"
FIX = HERE / "fixtures" / "anonymity_scan"
CFF, TERMS, FIGS, CLEAN = (
    FIX / "CITATION.cff",
    FIX / "terms.txt",
    FIX / "figures",
    FIX / "clean.txt",
)
BASELINE, NO_REASON = FIX / "baseline.txt", FIX / "baseline_no_reason.txt"


def run(*args, root=FIX, config=None):
    env = {k: v for k, v in os.environ.items() if k != "PAPER_TOOLS_CONFIG"}
    env["PAPER_TOOLS_ROOT"] = str(root)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    cmd = [sys.executable, str(SCRIPT), *map(str, args)]
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def scan(source, *extra, figures=FIGS, terms=TERMS, flag="--text"):
    return run(flag, source, "--citation", CFF, "--terms", terms, "--figures", figures, *extra)


def hit_lines(stdout):
    return [line for line in stdout.splitlines() if line.startswith("HIT ")]


def test_clean_copy_passes_with_notes():
    r = scan(CLEAN)
    assert r.returncode == 0, r.stdout + r.stderr
    assert hit_lines(r.stdout) == []
    assert "2 authors and 2 affiliations (7 terms)" in r.stdout  # conference name not a term
    out = r.stdout
    assert "followed by et al. (third-person citation): " in out
    assert 'clean.txt:7 (page 1): "Quillon"' in out
    assert 'clean.txt:7 (page 1): "Stroud"' in out  # "Stroud" then "et al." on the next line
    assert "in the references (third-person citation): " in out
    assert 'clean.txt:13 (page 2): "Quillon"' in out
    assert "system name (a note, not a hit)" in out
    assert "clean.txt: 2 occurrence(s), lines 5, 9" in out  # "E XAMPLE S YS" and "ExampleSys"
    assert "NOTE raster image not scanned" in out and "raster.png" in out
    assert "NOTE host in a figure source (source text does not render)" in out


SEEDS = [
    ("author name", "Anonymous Author(s)", "Ada Quillon"),
    ("author name", "names no machine.", "follows what Stroud showed."),
    ("author name", "names no machine.", "thanks Bartholomew."),
    # a lone "References" table header in the body must not make later names citations
    ("author name", "names no machine.", "names no machine.\nReferences\nIt follows Stroud."),
    ("affiliation", "Anonymous Institution(s)", "Northfield University"),
    ("affiliation", "[2] B. Stroud,", "[2] B. Stroud, Acme Research Lab,"),
    ("lab", "names no machine.", "comes from the Quillon Systems Lab."),
    ("host", "names no machine.", "ran on testbox07."),
    ("path", "names no machine.", "reads /home/ada/runs."),
    ("url", "names no machine.", "is at https://github.com/Example-\nLab/ExampleSys."),
    (
        "title",
        "A Neutral Title for the Anonymity Fixture",
        "ExampleSys: A Fixture Title for\nAnonymity Scanning",
    ),
    (
        "title",
        "A Neutral Title for the Anonymity Fixture",
        "E XAMPLE S YS: A Fixture Title for Anonymity Scanning",
    ),
    ("arxiv", "names no machine.", "follows arXiv:9999.00001."),
    ("phrase", "The method section", "As we showed before, the method section"),
]


@pytest.mark.parametrize("kind, old, new", SEEDS, ids=[f"{s[0]}-{i}" for i, s in enumerate(SEEDS)])
def test_seeded_defect_fails(tmp_path, kind, old, new):
    text = CLEAN.read_text(encoding="utf-8")
    assert text.count(old) == 1
    seeded = tmp_path / "seeded.txt"
    seeded.write_text(text.replace(old, new), encoding="utf-8")
    r = scan(seeded)
    assert r.returncode == 1, r.stdout + r.stderr
    hits = hit_lines(r.stdout)
    assert len(hits) == 1, r.stdout  # nested matches (org in URL, name in lab) reported once
    assert hits[0].startswith(f"HIT {kind}"), hits


def test_conference_name_is_not_an_author(tmp_path):
    seeded = tmp_path / "seeded.txt"
    seeded.write_text(
        CLEAN.read_text().replace("names no machine.", "appeared at the Conference on Testing.")
    )
    assert scan(seeded).returncode == 0


def test_template_terms_file():
    text = TEMPLATE_TERMS.read_text(encoding="utf-8")
    assert "PRIVATE" in text and "public repository" in text
    kinds = [line.split(":", 1)[0] for line in text.splitlines() if line and line[0] != "#"]
    assert sorted(kinds) == sorted(
        "affiliation lab org host path url title arxiv phrase venue system".split()
    )  # one synthetic example per kind
    r = scan(CLEAN, terms=TEMPLATE_TERMS)  # it parses; the fixture holds none of its hit terms
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("venue", ["Example Conference 2029", "E XAMPLE C ONFERENCE 2029"])
def test_template_terms_flag_the_earlier_venue(tmp_path, venue):
    seeded = tmp_path / "seeded.txt"
    text = CLEAN.read_text(encoding="utf-8")
    seeded.write_text(text.replace("names no machine.", f"appeared at {venue}."), encoding="utf-8")
    r = scan(seeded, terms=TEMPLATE_TERMS)
    assert r.returncode == 1, r.stdout + r.stderr
    hits = hit_lines(r.stdout)
    assert len(hits) == 1 and hits[0].startswith("HIT venue: "), r.stdout


def test_missing_figures_dir_is_a_usage_error(tmp_path):
    assert scan(CLEAN, figures=tmp_path / "absent").returncode == 2


def test_missing_default_figures_dir_is_a_note(tmp_path):
    r = run("--text", CLEAN, "--citation", CFF, "--terms", TERMS, root=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NOTE figures not scanned: paper.figures_dir (default; no folder at " in r.stdout
    config = config_project(tmp_path, figures_dir=tmp_path / "absent")
    r = run("--text", CLEAN, "--citation", CFF, "--terms", TERMS, root=tmp_path, config=config)
    assert r.returncode == 2, r.stdout + r.stderr  # a folder the config names must exist


def known_lines(stdout):
    return [line for line in stdout.splitlines() if line.startswith("KNOWN ")]


def known_paper(tmp_path, title="ExampleSys: A Fixture Title for Anonymity Scanning", extra=None):
    """clean.txt with the fixture title (baseline.txt's one row) and, with extra, one new hit."""
    text = CLEAN.read_text(encoding="utf-8").replace(
        "A Neutral Title for the Anonymity Fixture", title
    )
    paper = tmp_path / "known.txt"
    paper.write_text(text.replace("names no machine.", extra) if extra else text, encoding="utf-8")
    return paper


# The identity is the term, not the matched text: the small-caps title is the same known hit.
@pytest.mark.parametrize(
    "title",
    [
        "ExampleSys: A Fixture Title for Anonymity Scanning",
        "E XAMPLE S YS: A Fixture Title for\nAnonymity Scanning",
    ],
)
def test_baseline_only_paper_passes(tmp_path, title):
    paper = known_paper(tmp_path, title)
    assert scan(paper).returncode == 1  # without the baseline the title is a hit
    r = scan(paper, "--baseline", BASELINE)
    assert r.returncode == 0, r.stdout + r.stderr
    assert hit_lines(r.stdout) == []
    known = known_lines(r.stdout)
    assert len(known) == 1 and known[0].startswith("KNOWN title: "), r.stdout
    assert known[0].endswith("(baseline: fixture decision T-1 (#1, title kept until renamed))")
    assert "0 new hit(s), 1 known hit(s) from " in r.stdout


def test_new_hit_fails_with_the_baseline(tmp_path):
    r = scan(known_paper(tmp_path, extra="ran on testbox07."), "--baseline", BASELINE)
    assert r.returncode == 1, r.stdout + r.stderr
    hits = hit_lines(r.stdout)
    assert len(hits) == 1 and hits[0].startswith("HIT host: "), r.stdout
    assert hits[0].endswith('(not in the baseline; identity "host: testbox07")')
    assert len(known_lines(r.stdout)) == 1
    assert "1 new hit(s), 1 known hit(s) from " in r.stdout


@pytest.mark.parametrize(
    "row",
    [
        None,  # baseline_no_reason.txt: no tab
        "title: ExampleSys: A Fixture Title for Anonymity Scanning\t",  # a tab, then nothing
        "\tfixture decision T-1",  # a reason, no identity
    ],
)
def test_baseline_row_without_reason_fails(tmp_path, row):
    baseline = NO_REASON
    if row is not None:
        baseline = tmp_path / "baseline.txt"
        baseline.write_text(row + "\n", encoding="utf-8")
    r = scan(known_paper(tmp_path), "--baseline", baseline)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "baseline row has no reason" in r.stderr


def config_project(tmp_path, **paths):
    """A paper-tools.toml in tmp_path that names the given [paper] and [terms] paths."""
    tables = {
        "paper": ("citation_cff", "figures_dir"),
        "terms": ("anonymity", "anonymity_baseline"),
    }
    lines = []
    for table, keys in tables.items():
        lines.append(f"[{table}]")
        lines += [f'{key} = "{paths[key]}"' for key in keys if key in paths]
    config = tmp_path / "paper-tools.toml"
    config.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config


def test_config_supplies_every_default(tmp_path):
    config = config_project(
        tmp_path, citation_cff=CFF, figures_dir=FIGS, anonymity=TERMS, anonymity_baseline=BASELINE
    )
    r = run("--text", known_paper(tmp_path), root=tmp_path, config=config)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "2 authors and 2 affiliations (7 terms)" in r.stdout
    assert "0 new hit(s), 1 known hit(s) from " in r.stdout
    assert "NOTE raster image not scanned" in r.stdout  # the figures folder was scanned


def test_missing_configured_sources_are_notes(tmp_path):
    r = run("--text", CLEAN, "--terms", TERMS, "--figures", FIGS, root=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (
        "NOTE no citation file, so no author or affiliation terms: paper.citation_cff" in r.stdout
    )
    assert "NOTE no baseline, so every hit fails: terms.anonymity_baseline" in r.stdout
    assert "terms: no citation file; 9 terms from " in r.stdout


def test_no_terms_at_all_is_a_usage_error(tmp_path):
    r = run("--text", CLEAN, "--figures", FIGS, root=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "no terms to scan for" in r.stderr


def test_empty_figures_dir_skips_the_figures(tmp_path):
    config = tmp_path / "paper-tools.toml"
    config.write_text('[paper]\nfigures_dir = ""\n', encoding="utf-8")
    r = run("--text", CLEAN, "--citation", CFF, "--terms", TERMS, root=tmp_path, config=config)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NOTE figures not scanned: paper.figures_dir (empty)" in r.stdout
    assert "raster" not in r.stdout


needs_tex = pytest.mark.skipif(
    not all(shutil.which(t) for t in ("pdflatex", "pdftotext", "pdfinfo", "pdfimages")),
    reason="needs pdflatex and poppler (pdftotext, pdfinfo, pdfimages) on PATH",
)

DOC = r"""\documentclass{article}
\usepackage{graphicx}
INFO
\begin{document}
BODY
\end{document}
"""


def build_pdf(tmp_path, name, info="", body="A neutral fixture page."):
    (tmp_path / f"{name}.tex").write_text(DOC.replace("INFO", info).replace("BODY", body))
    shutil.copy(FIGS / "raster.png", tmp_path / "raster.png")
    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"]
    r = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
    return tmp_path / f"{name}.pdf"


@needs_tex
@pytest.mark.parametrize(
    "info, code, expect",
    [
        ("", 0, "metadata fields set: none"),
        (r"\pdfinfo{/Author (Ada Quillon)}", 1, "HIT metadata Author is not empty"),
        (
            r"\pdfinfo{/Title (ExampleSys: A Fixture Title for Anonymity Scanning)}",
            1,
            "metadata Title",
        ),
        (r"\pdfinfo{/Keywords (testbox07)}", 1, "HIT host"),
    ],
)
def test_pdf_metadata(tmp_path, info, code, expect):
    empty = tmp_path / "figures"
    empty.mkdir()
    r = scan(build_pdf(tmp_path, "paper", info), figures=empty, flag="--pdf")
    assert r.returncode == code, r.stdout + r.stderr
    assert expect in r.stdout


@needs_tex
def test_pdf_rasters_listed_not_scanned(tmp_path):
    empty = tmp_path / "figures"
    empty.mkdir()
    pdf = build_pdf(tmp_path, "paper", body=r"A page. \includegraphics[width=1cm]{raster.png}")
    r = scan(pdf, figures=empty, flag="--pdf")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NOTE 1 raster image(s) not scanned" in r.stdout


@needs_tex
def test_figure_pdf_text_and_metadata_are_scanned(tmp_path):
    figures = tmp_path / "figures"
    figures.mkdir()
    pdf = build_pdf(tmp_path, "fig", r"\pdfinfo{/Author (Ada Quillon)}", "Measured on testbox07.")
    shutil.move(pdf, figures / "fig.pdf")
    r = scan(CLEAN, figures=figures)
    assert r.returncode == 1, r.stdout + r.stderr
    assert any(h.startswith("HIT host") and "fig.pdf:1" in h for h in hit_lines(r.stdout))
    assert any(h.startswith("HIT metadata Author") for h in hit_lines(r.stdout))
