"""Tests for ../scripts/skim_extract.py (the four skim-pass extracts of a paper).

Run from the plugin folder:
    python3 -m pytest tests/test_skim_extract.py -q

fixtures/skim_extract/ is a small synthetic paper (preamble, abstract, three sections with one
figure and one table) with its own paper-tools.toml.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import paper_config  # noqa: E402
import skim_extract  # noqa: E402

SCRIPT = HERE.parent / "scripts" / "skim_extract.py"
FIX = HERE / "fixtures" / "skim_extract"
MACROS = {r"\examplesys{}": "ExampleSys"}


def fixture_config(root=FIX):
    return paper_config.load(root=root, config=root / "paper-tools.toml")


def test_first_sentence_keeps_the_run_in_header_and_stops_at_the_sentence_end():
    block = (
        "\\textbf{Fetch, rank, and serve.} Three steps take a request to a reply "
        "(Figure X). \\texttt{fetch} reads it from the origin."
    )
    assert skim_extract.first_sentence(block) == (
        "[Fetch, rank, and serve.] Three steps take a request to a reply (Figure X)."
    )
    assert skim_extract.first_sentence("We evaluate three caches: A; B; and C. Each ran once.") == (
        "We evaluate three caches: A; B; and C."
    )
    assert skim_extract.first_sentence("Station 4.2 logged 17.25% of the rain. Then it froze.") == (
        "Station 4.2 logged 17.25% of the rain."
    )


def test_spell_out_drops_comments_and_names_the_macros():
    text = "% a comment\n\\examplesys{} serves~\\cite{X2029} 59.25\\% (Table~\\ref{tab:a})."
    assert skim_extract.spell_out(text, MACROS) == "ExampleSys serves [cite] 59.25% (Table X)."


def test_the_paper_gives_four_extracts_with_every_display():
    out = skim_extract.extracts(fixture_config())
    assert sorted(out) == ["pass1.txt", "pass2.txt", "pass3.txt", "pass4.txt"]
    assert out["pass1.txt"].startswith("TITLE\nExampleSys: Caching Requests Near the Edge\n")
    assert "\nABSTRACT\n" in out["pass1.txt"]
    assert out["pass2.txt"].count("--- TABLE") == 1 and out["pass2.txt"].count("--- FIGURE") == 1
    assert "contributions" in out["pass2.txt"].split("FIGURES AND TABLES")[0]
    for heading in ("FIRST PARAGRAPH OF THE INTRODUCTION", "LAST PARAGRAPH OF THE DISCUSSION"):
        assert heading in out["pass3.txt"]
    assert "## Introduction" in out["pass4.txt"] and "[Limitations.]" in out["pass4.txt"]
    for text in out.values():
        assert "\\cite" not in text and "\\examplesys" not in text


def test_without_the_word_contributions_the_last_paragraph_stands_in(tmp_path):
    shutil.copytree(FIX, tmp_path, dirs_exist_ok=True)
    intro = tmp_path / "paper" / "sections" / "introduction.tex"
    intro.write_text(intro.read_text().replace("three contributions", "three parts"))
    last = skim_extract.extracts(fixture_config(tmp_path))["pass2.txt"].split("FIGURES")[0]
    assert "three parts" in last and "Approach." not in last


def test_the_command_writes_the_four_files(tmp_path):
    env = {**os.environ, "PAPER_TOOLS_ROOT": str(FIX)}
    env["PAPER_TOOLS_CONFIG"] = str(FIX / "paper-tools.toml")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True, env=env
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert sorted(p.name for p in tmp_path.iterdir()) == [f"pass{n}.txt" for n in (1, 2, 3, 4)]
