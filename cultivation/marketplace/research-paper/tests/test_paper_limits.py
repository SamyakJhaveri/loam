"""Fixture tests for ../scripts/paper_limits.py (the venue's page, appendix and abstract limits).

Run from the plugin folder:
    python3 -m pytest tests/test_paper_limits.py -q

Fixtures in fixtures/paper_limits/ (text dumps with a form feed after each page):
- clean.txt: 10 body pages, the references heading on page 10 after body text, one appendix
  mention in running text, a 44-token abstract ("E XAMPLE S YS" is 4 tokens, "[PENDING P3]" 2);
- refs_top.txt: 10 body pages, the references heading at the top of page 11 after a bare page
  number (page 11 must not count);
- clean_abstract.tex: 23 words once comments, \\cite, the \\href URL and command names are gone;
- seeded defects: seeded_pages.txt (11 body pages), seeded_refs_in_body.txt (the same with a
  lone "References" table header on page 2, which must not end the body),
  seeded_appendix.txt (an "A PPENDIX A" heading after the references), seeded_abstract.txt (501-word PDF abstract),
  seeded_abstract.tex (501 words).
Every run sets PAPER_TOOLS_ROOT to the fixture folder, which has no config file, so the limits
are the defaults (10 pages, 500 words, no appendix) unless a test passes PAPER_TOOLS_CONFIG.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "paper_limits.py"
FIX = HERE / "fixtures" / "paper_limits"
CLEAN_TEX = FIX / "clean_abstract.tex"


def run(*args, config=None):
    cmd = [sys.executable, str(SCRIPT), *map(str, args)]
    env = {k: v for k, v in os.environ.items() if k != "PAPER_TOOLS_CONFIG"}
    env["PAPER_TOOLS_ROOT"] = str(FIX)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_clean_copy_passes():
    r = run("--text", FIX / "clean.txt", "--abstract-tex", CLEAN_TEX)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS body pages 10 (limit 10)" in r.stdout
    assert "that page counts" in r.stdout
    assert "PASS abstract words (PDF text) 44 " in r.stdout
    assert "PASS abstract words (.tex, commands stripped) 23 " in r.stdout
    assert "NOTE appendix mention" in r.stdout
    assert "FAIL" not in r.stdout


def test_references_heading_at_page_top_does_not_count():
    r = run("--text", FIX / "refs_top.txt", "--abstract-tex", CLEAN_TEX)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS body pages 10 (limit 10)" in r.stdout
    assert "(page 11); top of page" in r.stdout


@pytest.mark.parametrize(
    "text, tex, expect",
    [
        ("seeded_pages.txt", "clean_abstract.tex", "FAIL body pages 11 (limit 10)"),
        ("seeded_refs_in_body.txt", "clean_abstract.tex", "FAIL body pages 11 (limit 10)"),
        ("seeded_appendix.txt", "clean_abstract.tex", "FAIL appendix heading at"),
        ("seeded_abstract.txt", "clean_abstract.tex", "FAIL abstract words (PDF text) 501 "),
        ("clean.txt", "seeded_abstract.tex", "FAIL abstract words (.tex, commands stripped) 501 "),
    ],
)
def test_seeded_defect_fails(text, tex, expect):
    r = run("--text", FIX / text, "--abstract-tex", FIX / tex)
    assert r.returncode == 1, r.stdout + r.stderr
    assert expect in r.stdout
    assert r.stdout.count("\nFAIL ") == 1, r.stdout  # only the seeded defect fails


@pytest.mark.parametrize(
    "heading",
    [
        "Appendix A Proofs",
        "Appendix A - Proofs",
        "Appendix A \u2013 Proofs",
        "A PPENDIX A P ROOFS",
        "Supplemental Material",
    ],
)
def test_titled_appendix_heading_fails(tmp_path, heading):
    txt = tmp_path / "paper.txt"
    clean = (FIX / "clean.txt").read_text(encoding="utf-8").rstrip("\f\n")
    txt.write_text(f"{clean}\n{heading}\nProof text goes here.\n\f", encoding="utf-8")
    r = run("--text", txt, "--abstract-tex", CLEAN_TEX)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "FAIL appendix heading at" in r.stdout


def test_empty_tex_abstract_fails_closed(tmp_path):
    tex = tmp_path / "abstract.tex"
    tex.write_text("\\begin{abstract}\n% placeholder\n\\end{abstract}\n")
    r = run("--text", FIX / "clean.txt", "--abstract-tex", tex)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "no words found" in r.stdout


def test_abstract_limit_is_inclusive(tmp_path):
    tex = tmp_path / "abstract.tex"
    tex.write_text("\\begin{abstract}\n" + "word " * 500 + "\n\\end{abstract}\n")
    assert run("--text", FIX / "clean.txt", "--abstract-tex", tex).returncode == 0
    tex.write_text("\\begin{abstract}\n" + "word " * 501 + "\n\\end{abstract}\n")
    assert run("--text", FIX / "clean.txt", "--abstract-tex", tex).returncode == 1


def test_missing_abstract_fails_closed(tmp_path):
    txt = tmp_path / "paper.txt"
    txt.write_text("A Title\nI. I NTRODUCTION\nBody text.\n\f")
    r = run("--text", txt, "--abstract-tex", CLEAN_TEX)
    assert r.returncode == 1
    assert "no abstract heading in the PDF text" in r.stdout


def test_missing_input_is_a_usage_error(tmp_path):
    r = run("--text", tmp_path / "absent.txt", "--abstract-tex", CLEAN_TEX)
    assert r.returncode == 2


def test_limits_come_from_the_config(tmp_path):
    config = tmp_path / "paper-tools.toml"
    config.write_text("[limits]\nmax_pages = 9\nmax_abstract_words = 40\n")
    r = run("--text", FIX / "clean.txt", "--abstract-tex", CLEAN_TEX, config=config)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "FAIL body pages 10 (limit 9)" in r.stdout
    assert "FAIL abstract words (PDF text) 44 (limit 40)" in r.stdout
    r = run("--text", FIX / "clean.txt", "--abstract-tex", CLEAN_TEX, "--max-pages", "10")
    assert "PASS body pages 10 (limit 10)" in r.stdout  # a flag wins over the config


def test_appendix_allowed_turns_the_heading_into_a_note(tmp_path):
    config = tmp_path / "paper-tools.toml"
    config.write_text("[limits]\nappendix_allowed = true\n")
    r = run("--text", FIX / "seeded_appendix.txt", "--abstract-tex", CLEAN_TEX, config=config)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "NOTE appendix heading at" in r.stdout and "FAIL" not in r.stdout


def test_default_paths_come_from_the_config(tmp_path):
    (tmp_path / "paper" / "sections").mkdir(parents=True)
    shutil.copy(CLEAN_TEX, tmp_path / "paper" / "sections" / "abstract.tex")
    env = {k: v for k, v in os.environ.items() if k != "PAPER_TOOLS_CONFIG"}
    env["PAPER_TOOLS_ROOT"] = str(tmp_path)
    cmd = [sys.executable, str(SCRIPT), "--text", str(FIX / "clean.txt")]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "paper/sections/abstract.tex:2-6" in r.stdout  # paper.abstract_tex, shown root-relative
    r = subprocess.run(cmd[:2], capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "no PDF at" in r.stderr and "paper/build/main.pdf" in r.stderr


DOC = r"""\documentclass{article}
\begin{document}
\title{A Neutral Title}
\author{Anonymous}
\maketitle
\begin{abstract}
one two three four five six seven eight nine ten
\end{abstract}
\section{Introduction}
Body text.
BODY
\begin{thebibliography}{1}
\bibitem{a} A. Writer, ``A work,'' 2026.
\end{thebibliography}
\end{document}
"""


def build_pdf(tmp_path, name, body=""):
    (tmp_path / f"{name}.tex").write_text(DOC.replace("BODY", body))
    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"]
    r = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
    return tmp_path / f"{name}.pdf"


@pytest.mark.skipif(
    not (shutil.which("pdflatex") and shutil.which("pdftotext")),
    reason="needs pdflatex and pdftotext on PATH to build and read a fixture PDF",
)
def test_pdf_path(tmp_path):
    tex = tmp_path / "abstract.tex"
    tex.write_text(
        "\\begin{abstract}\none two three four five six seven eight nine ten\n\\end{abstract}\n"
    )
    r = run("--pdf", build_pdf(tmp_path, "clean"), "--abstract-tex", tex)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS body pages 1 (limit 10)" in r.stdout
    assert "PASS abstract words (PDF text) 10 " in r.stdout
    seeded = build_pdf(tmp_path, "seeded", r"\section*{Appendix A: Proofs}Proof text.")
    r = run("--pdf", seeded, "--abstract-tex", tex)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "FAIL appendix heading" in r.stdout
