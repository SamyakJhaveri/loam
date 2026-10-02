"""Tests for the pure parts of ../scripts/section_gate.py (lost tokens, banned terms, page slack).

Run from the plugin folder:
    python3 -m pytest tests/test_section_gate.py -q
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import section_gate  # noqa: E402


def test_lost_tokens_separates_lost_from_mentioned_less():
    revision = (
        "The archive scans 35 of 80 maps (43.75\\%).\n% 64 appears only in a comment\n"
        "See \\ref{sec:a}."
    )
    removed = {"80": 1, "64": 1, "43.75%": 1, "two": 1, "\\ref{sec:b}": 1, "\\ref{sec:a}": 1}
    assert section_gate.lost_tokens(removed, revision) == ["64", "\\ref{sec:b}"]


def test_lost_tokens_does_not_match_inside_a_longer_number():
    assert section_gate.lost_tokens({"20": 1, "0.5": 1}, "We ran 9208 runs at 10.5 and 0.55.") == [
        "20",
        "0.5",
    ]


def test_lost_tokens_keeps_a_number_rewritten_without_thousands_separators():
    assert (
        section_gate.lost_tokens({"2,500": 1, "4,750": 1}, "Of the 2500 requests, 4{,}750 ran.")
        == []
    )
    assert section_gate.lost_tokens({"2,500": 1}, "Of the 25000 requests.") == ["2,500"]


def test_banned_hits_skip_comments_and_report_lines():
    patterns = section_gate.read_patterns(HERE / "fixtures" / "section_gate" / "banned_terms.txt")
    revision = "% RT12 in a comment is fine\nBus RT40 leaves at noon.\nThe river line runs hourly.\nBays B2 to B7 stay open.\n  % RT55 in an indented comment is fine"
    hits = section_gate.banned_hits(revision, patterns)
    assert [number for number, _, _ in hits] == [2]


def test_strip_comments_drops_indented_comment_lines():
    assert section_gate.strip_comments("a\n  % note\n%x\nb % keep") == "a\nb % keep"


def test_slack_finds_references_page_and_section_pages():
    text = "I. I NTRODUCTION\nbody\n\fVI. R ESULTS\nbody\n\fmore\nVII. D ISCUSSION\nend\nR EFERENCES\n[1] A\n[1] B\n\f[2] C"
    info = section_gate.slack(text, "Results")
    assert info == {"refs_page": 3, "lines_after_refs": 2, "section_pages": [2, 3]}


def test_slack_accepts_a_bibliography_heading():
    text = "I. I NTRODUCTION\nbody\n\fend\nB IBLIOGRAPHY\n[1] A"
    assert section_gate.slack(text, "Introduction")["refs_page"] == 2
