"""Fixture test for the step 1 command of agents/claim-ref-alignment.md.

The agent file carries a Python command that lists every \\cite of the build with cite_check.py's
scanner. This test takes that command from the agent file as written, puts the plugin folder in
place of ${CLAUDE_PLUGIN_ROOT}, and runs it on fixtures/claim_ref_alignment/ (main.tex inputs
sections/background.tex, four citing sentences, synthetic sources):
- the clean copy lists the four rows expected.json records;
- a seeded copy with the S4 \\cite line behind a % comment lists three;
- a seeded copy whose \\input names a missing file prints a PROBLEM line and no row;
- a seeded copy with a second \\cite of the same key on one line lists two identical rows.
It also checks that each expected paper_line starts its sentence in paper.txt.
It does not run the agent: labels need the web and a model.
Run from the repository root: python3 -m pytest <this file> -q
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
AGENT = PLUGIN / "agents" / "claim-ref-alignment.md"
FIX = HERE / "fixtures" / "claim_ref_alignment"
ROW = re.compile(r"^\S+\.tex:\d+ \S+$")


def run(main, cwd):
    fence = re.search(
        r"```\ncd <ROOT> && python3 - (\$\{CLAUDE_PLUGIN_ROOT\}/scripts) <MAIN> <<'EOF'\n"
        r"(.*?)\nEOF\n```",
        AGENT.read_text(),
        re.S,
    )
    assert fence, "step 1 command not found in the agent file"
    scripts = fence.group(1).replace("${CLAUDE_PLUGIN_ROOT}", str(PLUGIN))
    return subprocess.run(
        [sys.executable, "-", scripts, str(main)],
        input=fence.group(2),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def rows(stdout):
    return [line for line in stdout.splitlines() if ROW.match(line)]


def seeded(tmp_path, name, old, new):
    copy = tmp_path / "fx"
    shutil.copytree(FIX, copy)
    path = copy / name
    text = path.read_text()
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    return copy


def test_clean_fixture_lists_the_expected_rows():
    expected = json.loads((FIX / "expected.json").read_text())
    rel = FIX.relative_to(PLUGIN)
    r = run(rel / "main.tex", PLUGIN)
    assert r.returncode == 0, r.stderr
    assert rows(r.stdout) == [f"{rel}/{row['tex']} {row['key']}" for row in expected["rows"]]
    assert "PROBLEM" not in r.stdout
    assert r.stdout.splitlines()[-1].startswith(
        f"{expected['step1_citations']} citations in 2 files:"
    )


def test_commented_cite_is_not_listed(tmp_path):
    copy = seeded(tmp_path, "sections/background.tex", "\nOn a suite", "\n% On a suite")
    r = run("main.tex", copy)
    assert r.returncode == 0, r.stderr
    listed = rows(r.stdout)
    assert len(listed) == 3
    assert not any(line.startswith("sections/background.tex:6 ") for line in listed)


def test_missing_input_is_a_problem_line(tmp_path):
    copy = seeded(tmp_path, "main.tex", r"\input{sections/background}", r"\input{sections/missing}")
    r = run("main.tex", copy)
    assert r.returncode == 0, r.stderr
    assert rows(r.stdout) == []
    assert r"PROBLEM main.tex:12 \input{sections/missing} not found" in r.stdout


def test_same_key_twice_on_a_line_gives_two_rows(tmp_path):
    copy = seeded(
        tmp_path,
        "sections/background.tex",
        r"fewer than 15\% of cases~\cite{Beta2024}.",
        r"fewer than 15\% of cases~\cite{Beta2024}. Again~\cite{Beta2024}.",
    )
    r = run("main.tex", copy)
    assert r.returncode == 0, r.stderr
    assert rows(r.stdout).count("sections/background.tex:6 Beta2024") == 2
    assert r.stdout.splitlines()[-1].startswith("5 citations in 2 files:")


def test_paper_lines_start_their_sentences():
    expected = json.loads((FIX / "expected.json").read_text())
    paper = (FIX / "paper.txt").read_text().split("\n")  # pdftotext form feeds: not splitlines()
    tex = (FIX / "sections" / "background.tex").read_text().split("\n")
    for row in expected["rows"]:
        head = " ".join(tex[int(row["tex"].rsplit(":", 1)[1]) - 1].split()[:3])
        assert head in paper[row["paper_line"] - 1], row["sentence"]
