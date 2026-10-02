"""Offline tests for ../scripts/codex_seat.py: no test calls Codex, a model or the network."""

import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
import codex_seat  # noqa: E402
import paper_config  # noqa: E402


@pytest.fixture(autouse=True)
def no_env(monkeypatch):
    monkeypatch.delenv("PAPER_TOOLS_CONFIG", raising=False)
    monkeypatch.delenv("PAPER_TOOLS_ROOT", raising=False)


def fake_companion(home, version):
    script = home / codex_seat.CODEX_CACHE / version / "scripts" / "codex-companion.mjs"
    script.parent.mkdir(parents=True)
    script.write_text("")
    return script


def test_argument_parsing():
    p = codex_seat.parser()
    a = p.parse_args(["exemplar", "intro", "examplebench", "a.tex", "b.tex"])
    assert (a.fn, a.type, a.paper, a.ours) == (
        codex_seat.cmd_exemplar,
        "intro",
        "examplebench",
        ["a.tex", "b.tex"],
    )
    assert (a.model, a.effort) == (None, "high")  # None: main() takes codex.model
    a = p.parse_args(["whole", "all", "--model", "fable", "--effort", "xhigh"])
    assert (a.papers, a.ours, a.model, a.effort) == (["all"], None, "fable", "xhigh")
    with pytest.raises(SystemExit):
        p.parse_args(["exemplar", "abstract", "examplebench", "a.tex"])  # not a section type
    with pytest.raises(SystemExit):
        p.parse_args(["blind", "a.tex"])  # --venue is required


def test_codex_config_defaults_and_manifest_template(tmp_path):
    root = tmp_path.resolve()
    assert paper_config.load(root=tmp_path)["codex"] == {
        "corpus_dir": root / "paper/exemplars",
        "manifest": root / "paper/exemplars/manifest.tsv",
        "companion": None,
        "model": "gpt-6.1-sol",
    }
    config = tmp_path / "paper-tools.toml"
    config.write_text(f"[codex]\nmanifest = '{PLUGIN / 'templates' / 'exemplar_manifest.tsv'}'\n")
    papers = codex_seat.manifest(paper_config.load(root=tmp_path, config=config))
    assert list(papers) == ["examplebench"]
    assert papers["examplebench"]["url"].startswith("https://")


def test_companion_is_configured_or_the_newest_installed(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = paper_config.load(root=tmp_path)
    with pytest.raises(SystemExit) as exit_info:
        codex_seat.companion(cfg)
    assert "install the Codex plugin" in str(exit_info.value.code)
    for version in ("1.0.9", "1.0.2"):
        fake_companion(tmp_path, version)
    newest = fake_companion(tmp_path, "1.0.10")  # newer than 1.0.9, though it sorts first as text
    (tmp_path / codex_seat.CODEX_CACHE / "2.0.0").mkdir()  # a version folder without the script
    assert codex_seat.companion(cfg) == newest
    cfg["codex"]["companion"] = tmp_path / "pinned.mjs"
    assert codex_seat.companion(cfg) == tmp_path / "pinned.mjs"


def test_exemplar_questions_come_from_section_2_of_the_section_loop_doc():
    # section 3 of the doc has a "Method" row too; the questions are the cells of the section 2 row
    lines = codex_seat.GUIDE.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("## 2."))
    end = next(i for i, line in enumerate(lines) if line.startswith("## 3."))
    for row in codex_seat.SECTION_TYPES.values():
        cells = [line.split(" | ") for line in lines[start:end] if line.startswith(f"| {row} | ")]
        assert len(cells) == 1, row
        assert codex_seat.question_row(row) == (cells[0][1], cells[0][2].removesuffix(" |"))


def test_blind_reader_edits_apply_to_the_plugin_agent(tmp_path, monkeypatch, capsys):
    body = codex_seat.blind_body()
    assert "Read exactly one text, once," in body
    assert "the text pasted at the end of this message" in body
    assert "run no shell command, web search or other tool" in body
    assert "the path the lead gives you" not in body
    assert "## How the lead uses this seat" not in body

    # the whole blind command, offline: a fake home with a companion, a synthetic section and config
    monkeypatch.setenv("HOME", str(tmp_path))
    companion = fake_companion(tmp_path, "1.0.0")
    monkeypatch.setenv("PAPER_TOOLS_ROOT", str(tmp_path))
    monkeypatch.setattr(codex_seat, "WORK", tmp_path / "work")
    (tmp_path / "paper/tools").mkdir(parents=True)
    (tmp_path / "paper/tools/paper-tools.toml").write_text(
        "[paper.macros]\n'\\examplesys{}' = \"ExampleSys\"\n"
    )
    section = tmp_path / "intro.tex"
    section.write_text("% a comment\n\\examplesys{} checks each run.\n")
    codex_seat.main(["blind", str(section), "--venue", "Example Conference 2030 (systems)"])
    prompt = (tmp_path / "work/blind_intro_gpt-6.1-sol/prompt.md").read_text()
    assert "Venue and field: Example Conference 2030 (systems)" in prompt
    assert '\\examplesys{} prints "ExampleSys"' in prompt
    assert "   1  \\examplesys{} checks each run." in prompt
    assert "a comment" not in prompt
    command = capsys.readouterr().out.splitlines()[-1]
    assert command.startswith(f"node {companion} task --model gpt-6.1-sol --effort high ")
