"""Fixture test for ../scripts/check_tikz_prevention.py.

Each seeded fixture is clean.tex with one line changed:
- seeded_p3.tex line 6 drops `transform shape`, leaving a bare scale=0.9 (P3, reported at the
  \\begin{tikzpicture} line 5);
- seeded_p4.tex line 12 swaps `above` for `align=left`, which is not a direction (P4).
clean.tex also carries a commented-out bare scale= and bare edge label that must be ignored.
clean_linebreak_comment.tex hides a bare edge label in a comment after `\\\\`;
seeded_escaped_percent.tex has a bare edge label after an escaped `\\%` (P4).
Run from the plugin folder: python3 -m pytest tests/test_check_tikz_prevention.py -q
"""

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "check_tikz_prevention.py"
FIX = HERE / "fixtures" / "check_tikz_prevention"


def run(*names: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), *(str(FIX / n) for n in names)]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_clean_fragment_passes():
    r = run("clean.tex")
    assert r.returncode == 0, r.stderr
    assert "OK: 1 file(s) pass P3+P4 prevention checks." in r.stdout
    assert r.stderr == ""


@pytest.mark.parametrize(
    ("name", "changed_line", "expected"),
    [
        ("seeded_p3.tex", 6, "P3 @ line 5: bare scale= without node scaling"),
        ("seeded_p4.tex", 12, "P4 @ line 12: edge label without directional keyword"),
    ],
)
def test_seeded_defect_fails(name, changed_line, expected):
    clean = (FIX / "clean.tex").read_text().splitlines()
    seeded = (FIX / name).read_text().splitlines()
    assert len(clean) == len(seeded)
    diff = [i + 1 for i, (a, b) in enumerate(zip(clean, seeded, strict=True)) if a != b]
    assert diff == [changed_line]

    r = run(name)
    assert r.returncode == 1
    assert expected in r.stderr
    assert r.stderr.count(" @ line ") == 1


def test_comment_after_line_break_is_ignored():
    # `\\%` is a line break then a comment; upstream scanned the comment (false P4 at line 5).
    r = run("clean_linebreak_comment.tex")
    assert r.returncode == 0, r.stderr


def test_escaped_percent_does_not_hide_a_violation():
    r = run("seeded_escaped_percent.tex")
    assert r.returncode == 1
    assert "P4 @ line 5: edge label without directional keyword" in r.stderr
    assert r.stderr.count(" @ line ") == 1


def test_one_seeded_file_fails_a_multi_file_run():
    assert run("clean.tex", "seeded_p3.tex").returncode == 1


def test_missing_file_is_a_usage_error():
    assert run("does_not_exist.tex").returncode == 2
