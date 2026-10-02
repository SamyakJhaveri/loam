"""Fixture test for the step 8 leak check of agents/citation-finder.md. No network.

The agent file carries a Python command that checks the query log before any Consensus query
is sent. This test takes that command from the agent file as written, puts the plugin folder
in place of ${CLAUDE_PLUGIN_ROOT}, and runs it on fixtures/citation_finder/: build.tsv (two
build sentences, as lit_index.py --sentences prints them), paper.txt (PAPER, whose title the
build sets by macro, so build.tsv lacks it), paper-tools.toml (literature.self_names: the
system name ExampleSys and the preprint id 2901.00001), queries_ok.tsv (a keyword query, a
title search, an arXiv fetch: all clean), queries_leak.tsv (seven seeded breaches: a 4-word
run of a sentence, a number from the paper, the system name in a Consensus query, a 1-word
query, an unknown tool, the system name in a WebSearch query, a row whose origin is the "-"
placeholder) and queries_title.tsv (a Consensus query holding a 4-word run of the title).
A row whose origin field is empty, blank or a padded "-" ends in whitespace, which git diff
--check rejects in a committed fixture, so test_empty_origin_field_is_flagged writes those rows
at run time.
Run from the repository root: python3 -m pytest <this file> -q
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
AGENT = PLUGIN / "agents" / "citation-finder.md"
FIX = HERE / "fixtures" / "citation_finder"


def leak_check(log, build=FIX / "build.tsv", paper=FIX / "paper.txt"):
    fence = re.search(
        r"```\ncd <ROOT> && python3 - <OUT>/query_log\.tsv \$TMPDIR/cf_build\.tsv <PAPER> "
        r"(\$\{CLAUDE_PLUGIN_ROOT\}/scripts) <<'EOF'\n(.*?)\nEOF\n```",
        AGENT.read_text(),
        re.S,
    )
    assert fence, "step 8 command not found in the agent file"
    scripts = fence.group(1).replace("${CLAUDE_PLUGIN_ROOT}", str(PLUGIN))
    env = {
        **os.environ,
        "PAPER_TOOLS_ROOT": str(FIX),
        "PAPER_TOOLS_CONFIG": str(FIX / "paper-tools.toml"),
    }
    return subprocess.run(
        [sys.executable, "-", str(log), str(build), str(paper), scripts],
        input=fence.group(2),
        cwd=FIX,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_clean_log_passes():
    proc = leak_check(FIX / "queries_ok.tsv")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "leak check: 3 queries, 0 flagged"


def test_each_seeded_breach_is_flagged():
    proc = leak_check(FIX / "queries_leak.tsv")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    flagged = {int(m) for m in re.findall(r"^LEAK\? line (\d+)", proc.stdout, re.M)}
    assert flagged == {1, 2, 3, 4, 5, 6, 7}, proc.stdout
    assert "4-word runs of the build" in proc.stdout and "a number" in proc.stdout
    assert "self name ['examplesys']" in proc.stdout
    assert proc.stdout.splitlines()[-1] == "leak check: 7 queries, 7 flagged"


def test_preprint_id_in_a_fetch_is_flagged(tmp_path):
    log = tmp_path / "preprint.tsv"
    log.write_text("1\tcurl\thttps://export.arxiv.org/api/query?id_list=2901.00001\tN1\n")
    proc = leak_check(log)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "self name ['2901 00001']" in proc.stdout


@pytest.mark.parametrize("origin", ["", " ", " - "])
def test_empty_origin_field_is_flagged(tmp_path, origin):
    log = tmp_path / "empty_origin.tsv"
    log.write_text(f"1\tcurl\thttps://api.crossref.org/works/10.5555/x\t{origin}\n")
    proc = leak_check(log)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert proc.stdout.splitlines() == [
        "LEAK? line 1: not <n> <tool> <query> <origin>, all filled, with a known tool",
        "leak check: 1 queries, 1 flagged",
    ]


def test_missing_build_sentences_fail_closed(tmp_path):
    empty = tmp_path / "empty.tsv"
    empty.write_text("")
    assert leak_check(FIX / "queries_ok.tsv", empty).returncode == 1


def test_title_run_in_a_consensus_query_is_flagged():
    proc = leak_check(FIX / "queries_title.tsv")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "4-word runs of the build or PAPER: ['sparse graph partitioning quality']" in proc.stdout
    assert proc.stdout.splitlines()[-1] == "leak check: 1 queries, 1 flagged"
