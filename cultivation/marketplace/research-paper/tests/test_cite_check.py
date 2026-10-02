"""Fixture test for ../scripts/cite_check.py. Canned replies only; no test touches the network.

Fixtures in fixtures/cite_check/: refs.bib (good2020 plus four seeded defects), good.bib
(good2020 alone), main.tex (reaches shared/part.tex through \\input@path and holds a cite in
a % comment), sections/extra.tex (read only through --scan), good.tex, and responses.json
(canned Crossref and arXiv replies for every lookup). Verifier cases: multiline.tex (a cite
key list over two lines), braced_others.bib, bad_arxiv_doi.bib, url_doi_wrong.bib and
url_doi_good.bib (a DOI given only as a doi.org url). The config cases write a
paper-tools.toml at run time (paper.*, cite.warn_only).
Run from the repository root: python3 -m pytest <this file> -q
"""

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "cite_check.py"
FIX = HERE / "fixtures" / "cite_check"
GOOD_URL = "https://api.crossref.org/works/10.5555/good.2020"
DEFECT = re.compile(r"^DEFECT (\S+) (\S+) ")


def run(*args, config=None):
    """Run the script with the project root at FIX (which has no config) or a given config."""
    env = {**os.environ, "PAPER_TOOLS_ROOT": str(FIX)}
    env.pop("PAPER_TOOLS_CONFIG", None)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    found = {m.groups() for m in map(DEFECT.match, proc.stdout.splitlines()) if m}
    return proc, found


def good_run(*extra):
    return run("--bib", FIX / "good.bib", "--main", FIX / "good.tex", "--scan", *extra)


def good_reply(**changes):
    """The canned Crossref reply for good2020, with message fields changed (None deletes)."""
    reply = copy.deepcopy(json.loads((FIX / "responses.json").read_text())[GOOD_URL])
    message = reply["body"]["message"]
    for name, value in changes.items():
        name = name.replace("_", "-")
        if value is None:
            message.pop(name, None)
        else:
            message[name] = value
    return reply


def test_seeded_defects_fail():
    proc, found = run(
        "--bib", FIX / "refs.bib",
        "--main", FIX / "main.tex",
        "--scan", FIX / "sections" / "*.tex",
        "--responses", FIX / "responses.json",
    )  # fmt: skip
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {
        ("wrongtitle2021", "title-mismatch"),
        ("deaddoi2019", "unresolved"),
        ("arxivonly2024", "arxiv-only"),
        ("etal2022", "authors"),
    }, proc.stdout
    assert "5 cited keys in 3 tex files" in proc.stdout


def test_config_defaults_and_warn_only(tmp_path):
    """--bib, --main and --scan come from paper.*; cite.warn_only turns two checks into WARN."""
    config = tmp_path / "paper-tools.toml"
    config.write_text(
        '[paper]\nbib = "refs.bib"\nmain_tex = "main.tex"\nsections_dir = "sections"\n'
        '[cite]\nwarn_only = ["authors", "arxiv-only"]\n'
    )
    proc, found = run("--responses", FIX / "responses.json", config=config)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {("wrongtitle2021", "title-mismatch"), ("deaddoi2019", "unresolved")}
    assert re.search(r"^WARN etal2022 authors ", proc.stdout, re.M), proc.stdout
    assert re.search(r"^WARN arxivonly2024 arxiv-only ", proc.stdout, re.M), proc.stdout
    assert "5 cited keys in 3 tex files" in proc.stdout


def test_warn_only_rejects_a_check_that_is_not_a_venue_rule(tmp_path):
    config = tmp_path / "paper-tools.toml"
    config.write_text('[cite]\nwarn_only = ["unresolved"]\n')
    proc, _ = run(
        "--bib", FIX / "good.bib", "--main", FIX / "good.tex", "--scan", "--offline", config=config
    )
    assert proc.returncode == 2 and "cite.warn_only names unknown checks" in proc.stderr


def test_good_entry_passes():
    proc, found = good_run("--responses", FIX / "responses.json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert found == set(), proc.stdout


@pytest.mark.parametrize(
    "reply, check",
    [
        ({"error": "timeout"}, "unresolved"),
        ({"status": 503, "body": ""}, "unresolved"),
        ({"status": 200, "body": "not json"}, "unresolved"),
        (good_reply(DOI=None), "retraction-unknown"),
        (
            good_reply(
                updated_by=[
                    {
                        "type": "retraction",
                        "label": "Retraction",
                        "DOI": "10.5555/notice.2021",
                        "updated": {"date-parts": [[2021, 3, 1]]},
                    }
                ]
            ),
            "retracted",
        ),
        (
            good_reply(published_print=None, issued={"date-parts": [[2018, 1]]}),
            "year-mismatch",
        ),
    ],
    ids=["timeout", "http-503", "bad-json", "no-record-doi", "retraction", "year"],
)
def test_lookup_fails_closed(tmp_path, reply, check):
    responses = tmp_path / "responses.json"
    responses.write_text(json.dumps({GOOD_URL: reply}))
    proc, found = good_run("--responses", responses)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {("good2020", check)}, proc.stdout


def test_offline_is_unresolved():
    proc, found = good_run("--offline")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {("good2020", "unresolved")}, proc.stdout


def test_duplicates_and_missing_key(tmp_path):
    text = (FIX / "good.bib").read_text()
    bib = tmp_path / "dup.bib"
    bib.write_text(text + "\n" + text.replace("{good2020,", "{GOOD2020,"))
    tex = tmp_path / "dup.tex"
    tex.write_text("\\cite{good2020,absent2000}\n")
    proc, found = run("--bib", bib, "--main", tex, "--scan", "--responses", FIX / "responses.json")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {
        ("good2020", "duplicate-key"),
        ("GOOD2020", "duplicate-key"),
        ("good2020", "duplicate-doi"),
        ("GOOD2020", "duplicate-doi"),
        ("absent2000", "missing-entry"),
    }, proc.stdout
    assert re.search(r"^WARN GOOD2020 uncited ", proc.stdout, re.M), proc.stdout


def test_cite_spanning_lines():
    """A \\cite key list broken over two lines still counts every key."""
    proc, found = run(
        "--bib", FIX / "good.bib",
        "--main", FIX / "multiline.tex",
        "--scan", "--responses", FIX / "responses.json",
    )  # fmt: skip
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert found == {("absent2000", "missing-entry")}, proc.stdout
    assert "uncited" not in proc.stdout, proc.stdout


@pytest.mark.parametrize(
    "bib, want",
    [
        ("braced_others.bib", {("good2020", "authors")}),
        ("bad_arxiv_doi.bib", {("good2020", "unresolved")}),
        ("url_doi_wrong.bib", {("good2020", "title-mismatch")}),
        ("url_doi_good.bib", set()),
    ],
    ids=["braced-others", "bad-arxiv-doi", "doi-only-in-url", "doi-only-in-url-clean"],
)
def test_verifier_cases(bib, want):
    proc, found = run(
        "--bib", FIX / bib,
        "--main", FIX / "good.tex",
        "--scan", "--responses", FIX / "responses.json",
    )  # fmt: skip
    assert proc.returncode == (1 if want else 0), proc.stdout + proc.stderr
    assert found == want, proc.stdout
    if bib.startswith("url_doi"):
        assert "1 lookups" in proc.stdout, proc.stdout
