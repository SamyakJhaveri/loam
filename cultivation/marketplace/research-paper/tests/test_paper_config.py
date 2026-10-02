"""Tests for ../scripts/paper_config.py and the ../bin/paper-tool dispatcher."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
import paper_config  # noqa: E402

TEMPLATE = PLUGIN / "templates" / "paper-tools.toml"


@pytest.fixture(autouse=True)
def no_env(monkeypatch):
    monkeypatch.delenv("PAPER_TOOLS_CONFIG", raising=False)
    monkeypatch.delenv("PAPER_TOOLS_ROOT", raising=False)


def test_defaults_without_a_config_file(tmp_path):
    cfg = paper_config.load(root=tmp_path)
    root = tmp_path.resolve()
    assert cfg["project"] == {"root": root, "config": None}
    assert cfg["paper"]["main_tex"] == root / "paper/main.tex"
    assert cfg["build"]["pdf"] == root / "paper/build/main.pdf"
    assert cfg["limits"] == {
        "max_pages": 12,
        "max_abstract_words": 250,
        "appendix_allowed": False,
    }
    assert cfg["paper"]["sections"] == []
    assert cfg["literature"]["self_names"] == []


def test_root_is_the_git_top_level(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    sub = tmp_path / "paper" / "sections"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)
    assert paper_config.find_root() == tmp_path.resolve()
    monkeypatch.setenv("PAPER_TOOLS_ROOT", str(sub))
    assert paper_config.find_root() == sub.resolve()


def test_config_file_from_the_environment(tmp_path, monkeypatch):
    config = tmp_path / "fixture.toml"
    text = '[limits]\nmax_pages = 8\n[paper]\nsections = ["intro", "eval"]\n'
    config.write_text(text)
    monkeypatch.setenv("PAPER_TOOLS_CONFIG", str(config))
    cfg = paper_config.load(root=tmp_path)
    assert cfg["project"]["config"] == config
    assert cfg["limits"]["max_pages"] == 8
    assert cfg["limits"]["max_abstract_words"] == 250
    assert cfg["paper"]["sections"] == ["intro", "eval"]


def test_default_location_is_read(tmp_path):
    tools = tmp_path / "paper" / "tools"
    tools.mkdir(parents=True)
    (tools / "paper-tools.toml").write_text("[limits]\nmax_abstract_words = 150\n")
    cfg = paper_config.load(root=tmp_path)
    assert cfg["limits"]["max_abstract_words"] == 150


def test_relative_paths_resolve_against_the_root(tmp_path):
    config = tmp_path / "c.toml"
    config.write_text(
        '[paper]\nmain_tex = "doc/x.tex"\nbib = "/abs/refs.bib"\ncitation_cff = ""\n'
        '[literature]\nnotes = ["notes/a.md", "notes/b.md::## 2."]\n'
    )
    cfg = paper_config.load(root=tmp_path, config=config)
    root = tmp_path.resolve()
    assert cfg["paper"]["main_tex"] == root / "doc/x.tex"
    assert cfg["paper"]["bib"] == Path("/abs/refs.bib")
    assert cfg["paper"]["citation_cff"] is None
    assert cfg["literature"]["notes"] == [
        f"{root / 'notes/a.md'}",
        f"{root / 'notes/b.md'}::## 2.",
    ]


@pytest.mark.parametrize(
    "text, message",
    [
        ("[paper]\nmain = 'x.tex'\n", "unknown key paper.main"),
        ("[venue]\nname = 'x'\n", "unknown table [venue]"),
        ("[limits]\nmax_pages = '12'\n", "limits.max_pages must be a TOML int"),
        ("[limits\n", "cannot read"),
    ],
)
def test_bad_config_exits_2(tmp_path, capsys, text, message):
    config = tmp_path / "bad.toml"
    config.write_text(text)
    with pytest.raises(SystemExit) as exit_info:
        paper_config.load(root=tmp_path, config=config)
    assert exit_info.value.code == 2
    assert message in capsys.readouterr().err


def test_missing_named_config_exits_2(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        paper_config.load(root=tmp_path, config=tmp_path / "absent.toml")
    assert exit_info.value.code == 2


def test_template_loads_and_names_every_key(tmp_path):
    cfg = paper_config.load(root=tmp_path, config=TEMPLATE)
    assert cfg["paper"]["macros"]["\\examplesys{}"] == "ExampleSys"
    with open(TEMPLATE, "rb") as handle:
        raw = paper_config.tomllib.load(handle)
    for table, keys in paper_config.DEFAULTS.items():
        assert set(raw.get(table, {})) == set(keys), table


def run(cmd, root):
    """cmd with a bare environment: this Python first on PATH, the root pinned."""
    path = f"{Path(sys.executable).parent}:/usr/bin:/bin"
    env = {"PATH": path, "PAPER_TOOLS_ROOT": str(root)}
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def test_command_line_prints_json_and_one_value(tmp_path):
    script = str(PLUGIN / "scripts" / "paper_config.py")
    whole = run([sys.executable, script], tmp_path)
    assert whole.returncode == 0, whole.stderr
    assert json.loads(whole.stdout)["limits"]["max_pages"] == 12
    one = run([sys.executable, script, "build.pdf"], tmp_path)
    assert one.stdout.strip() == str(tmp_path.resolve() / "paper/build/main.pdf")
    assert run([sys.executable, script, "build.nope"], tmp_path).returncode == 2


def test_dispatcher_lists_runs_and_refuses(tmp_path):
    tool = str(PLUGIN / "bin" / "paper-tool")
    listing = run(["bash", tool], tmp_path)
    assert listing.returncode == 0
    assert "  paper_config" in listing.stdout.splitlines()
    value = run(["bash", tool, "paper_config", "limits.max_pages"], tmp_path)
    assert (value.returncode, value.stdout.strip()) == (0, "12")
    for name in ("no_such_script", "../scripts/paper_config"):
        bad = run(["bash", tool, name], tmp_path)
        assert bad.returncode == 2
        assert "no script named" in bad.stderr
