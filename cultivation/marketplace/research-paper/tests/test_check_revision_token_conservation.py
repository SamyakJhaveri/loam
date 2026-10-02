# Source: https://github.com/imbad0202/academic-research-skills
# Commit: e79085d0d38609984ef8cfe0faf2d254aac9e0a9
# Path:   scripts/test_check_revision_token_conservation.py, lines 1-206, 332-367 and 396-398
#         (the whole file except its patch-mode tests, lines 208-330 and 369-394)
# License: CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu,
#          https://creativecommons.org/licenses/by-nc/4.0/ (non-commercial research use only).
# Changes made in this copy (a private research-paper project, 2026-09-29; change 10 for the
# research-paper plugin):
#   1. This header, and "# fmt: off" below it, so ruff keeps the upstream layout.
#   2. Docstring: the patch-mode clause is gone, the cases of this copy are listed, and the run
#      command names this path. The em dash (banned in this repository) is written "-".
#   3. Imports: the script is loaded by path from ../check_revision_token_conservation.py
#      (importlib), not from a scripts package; REPO_ROOT and its sys.path insert are gone;
#      audit_patch and the unused main are no longer imported.
#   4. Removed with patch mode: PATCH_BASE, _patch, AuditPatchTests and
#      test_patch_mode_cli_reports_op_rows.
#   5. CliTests._run runs the script by its absolute path, not "scripts/..." from REPO_ROOT.
#   6. New in this copy, after CliTests: LaTeX comments and \%, \cite, \citep, \citet keys,
#      \ref and \label targets, placeholder fills, and the fixture pairs under
#      fixtures/check_revision_token_conservation/ through the CLI with --strict.
#   7. A \cite locator (optional argument) is a number, and one placeholder filled with two
#      values is a fill conflict (script header changes 5 and 7); changed_locator.tex added.
#   8. Number words, strength_delta, unverified fills and --authorize (script header changes 9
#      to 12, 2026-09-29): filled.tex now exits 1 (its fills are unverified without
#      --authorize); base.tex's "one-sided" gives the number word "one"; the audit_pair calls
#      that expect a conserved fill pass verified; run_cli takes a source and extra arguments
#      and runs in the fixture directory; new words_*.tex pairs, claims.json, findings.md,
#      decisions.md and the --authorize cases (their TSV rows are written by the test).
#   9. Dotted member names (script header change 13, 2026-09-29): claims_dotted.json, two
#      --authorize cases whose claims: row names models.vendor-model-1.5 (one passes, one names a
#      missing member), and test_claims_key_walks_the_longest_dotted_member_name.
#  10. Plugin port: SCRIPT is ../scripts/check_revision_token_conservation.py; the fixtures,
#      the tokens the tests expect from them, the claims keys and the model name are synthetic;
#      the author-year examples of CitationExtractionTests name other surnames.
# fmt: off
r"""Mutation tests for check_revision_token_conservation.py (#570).

Covers: numeric-token multiset conservation (decimals, percentages,
thousands separators, signs, en-dash ranges), Unicode fold-before-split
ordering (fullwidth digits, U+2212 minus - the #524 lesson: normalize the
whole value BEFORE any split/extract), citation-token conservation
(<!--ref:-->/<!--anchor:--> markers, bracketed groups, author-year),
comment exclusion from prose numbers, protected-term word boundaries,
and CLI exit semantics (advisory exit 0 / --strict exit 1).
Cases added in this copy: % comments in .tex (a \% stays), LaTeX \cite/\citep/\citet
keys and \ref/\label targets, placeholder fills versus number changes,
number words, strong words and hedges, unverified fills, --authorize rows
(finding:, decision:, claims:), and the fixture pairs in
fixtures/check_revision_token_conservation/.

Run from the plugin folder:
    python3 -m pytest tests/test_check_revision_token_conservation.py -q
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_revision_token_conservation.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "check_revision_token_conservation"
SPEC = importlib.util.spec_from_file_location("check_revision_token_conservation", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)

audit_pair = CHECKER.audit_pair
extract_citation_tokens = CHECKER.extract_citation_tokens
extract_numbers = CHECKER.extract_numbers
protected_term_counts = CHECKER.protected_term_counts


class NumberExtractionTests(unittest.TestCase):
    def test_decimal_percentage_is_one_token(self):
        numbers = extract_numbers("Accuracy was 87.08% in 612 participants.")
        self.assertEqual(dict(numbers), {"87.08%": 1, "612": 1})

    def test_thousands_separator_number_is_one_token(self):
        numbers = extract_numbers("We analyzed 612,418 moderation decisions.")
        self.assertEqual(dict(numbers), {"612,418": 1})

    def test_fullwidth_digits_normalized_before_split(self):
        # Fold-before-split: NFKC runs on the whole text BEFORE tokenization,
        # so a fullwidth respelling cannot smuggle a changed value past the
        # multiset comparison (nor false-flag an unchanged one).
        self.assertEqual(
            extract_numbers("准确率为８７.０８％。"),
            extract_numbers("准确率为87.08%。"),
        )

    def test_unicode_minus_normalized_to_ascii(self):
        self.assertEqual(
            extract_numbers("β = −0.45 in the adjusted model."),
            extract_numbers("β = -0.45 in the adjusted model."),
        )

    def test_sign_attaches_after_equals_but_not_inside_range(self):
        numbers = extract_numbers("β = -0.45; 95% CI: 0.58–0.92.")
        self.assertEqual(
            dict(numbers), {"-0.45": 1, "95%": 1, "0.58": 1, "0.92": 1}
        )

    def test_endash_range_conserved_against_hyphen_respelling(self):
        self.assertEqual(
            extract_numbers("(HR = 0.73, 95% CI: 0.58–0.92)"),
            extract_numbers("(HR = 0.73, 95% CI: 0.58-0.92)"),
        )

    def test_sign_inside_brackets_and_after_comma_is_kept(self):
        # A CI lower bound or a comma-separated negative must keep its sign:
        # [-0.45, 0.12] flipping to [0.45, 0.12] is a real change, not conserved.
        numbers = extract_numbers("CI [-0.45, 0.12] and slope of -1.3, 0.7")
        self.assertEqual(
            dict(numbers), {"-0.45": 1, "0.12": 1, "-1.3": 1, "0.7": 1}
        )

    def test_scientific_exponent_is_part_of_the_token(self):
        # 6.02e23 must not truncate to 6.02 (which would let 6.02e23 -> 6.02e24
        # pass as conserved).
        self.assertEqual(dict(extract_numbers("Avogadro 6.02e23 units")), {"6.02e23": 1})
        self.assertEqual(dict(extract_numbers("p = 1.2E-5 overall")), {"1.2E-5": 1})
        self.assertFalse(audit_pair("6.02e23 units", "6.02e24 units")["conserved"])

    def test_letter_adjacent_identifier_digits_are_not_prose_numbers(self):
        numbers = extract_numbers("Contrary to H2, Model-A7 held at T0.")
        self.assertEqual(dict(numbers), {})

    def test_cjk_adjacent_numbers_still_count(self):
        numbers = extract_numbers("本研究共612名受試者，準確率87.08%。")
        self.assertEqual(dict(numbers), {"612": 1, "87.08%": 1})

    def test_marker_comments_excluded_from_prose_numbers(self):
        numbers = extract_numbers(
            "The effect held.<!--ref:li2023--><!--anchor:page:12-->"
        )
        self.assertEqual(dict(numbers), {})


class CitationExtractionTests(unittest.TestCase):
    def test_ref_and_anchor_markers_counted(self):
        tokens = extract_citation_tokens(
            "Claim.<!--ref:smith2024--><!--anchor:quote:stable%20terms-->"
        )
        self.assertEqual(
            dict(tokens),
            {"ref:smith2024": 1, "anchor:quote:stable%20terms": 1},
        )

    def test_author_year_reorder_conserved(self):
        source = "In 612 adults, Model-A7 improved accuracy (Li & Park, 2023)."
        revision = "Model-A7 improved accuracy in 612 adults (Li & Park, 2023)."
        self.assertEqual(
            extract_citation_tokens(source), extract_citation_tokens(revision)
        )

    def test_narrative_author_swap_with_same_slug_is_a_delta(self):
        # A narrative citation carries the author OUTSIDE the parenthesized year;
        # swapping "Smith (2020)" -> "Jones (2020)" while keeping the same
        # <!--ref:smith2020--> slug must not read as conserved (the visible
        # attribution changed even though the marker and year did not).
        result = audit_pair(
            "Smith (2020)<!--ref:smith2020--> found X.",
            "Jones (2020)<!--ref:smith2020--> found X.",
        )
        self.assertFalse(result["conserved"])

    def test_narrative_author_year_token_includes_author(self):
        tokens = extract_citation_tokens("As Okonkwo and Vidal (2021) showed,")
        self.assertIn("Okonkwo and Vidal (2021)", dict(tokens))

    def test_resolved_ref_marker_keys_on_slug(self):
        # The finalizer resolves <!--ref:slug--> into 0/1/2-status-token forms
        # (<!--ref:slug ok-->, <!--ref:slug LOW-WARN CONTAMINATED-PREPRINT-->,
        # ... policy_hash=...). Revision reruns run on already-resolved drafts,
        # so the checker must key the citation multiset on the SLUG alone -
        # status/suffix tokens are derived metadata, idempotently recomputed,
        # never writer content. Bare vs resolved must NOT read as a delta.
        bare = extract_citation_tokens("Claim.<!--ref:smith2024-->")
        resolved = extract_citation_tokens(
            "Claim.<!--ref:smith2024 LOW-WARN CONTAMINATED-PREPRINT-->"
        )
        self.assertEqual(bare, resolved)
        self.assertEqual(dict(bare), {"ref:smith2024": 1})

    def test_dropped_resolved_ref_marker_is_a_delta(self):
        # The regression the checker exists to catch: a resolved marker deleted
        # during revision must surface, not vanish under COMMENT_RE stripping.
        result = audit_pair(
            "The effect held.<!--ref:li2023 ok policy_hash=abc123-->",
            "The effect held.",
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["citations_delta"]["removed"], {"ref:li2023": 1})

    def test_bracketed_group_change_flagged(self):
        self.assertNotEqual(
            extract_citation_tokens("The score rose [17]."),
            extract_citation_tokens("The score rose [18]."),
        )

    def test_markdown_link_is_not_a_citation(self):
        tokens = extract_citation_tokens("See [the appendix](https://x.test).")
        self.assertEqual(dict(tokens), {})


class ProtectedTermTests(unittest.TestCase):
    def test_short_term_uses_word_boundaries(self):
        counts = protected_term_counts("AI evidence, as they SAID, is limited.", ["AI"])
        self.assertEqual(counts["AI"], 1)

    def test_case_change_counts_as_loss(self):
        source = protected_term_counts("Normalized to GAPDH.", ["GAPDH"])
        revision = protected_term_counts("Normalized to Gapdh.", ["GAPDH"])
        self.assertNotEqual(source, revision)


class AuditPairTests(unittest.TestCase):
    def test_reordering_with_identical_tokens_is_conserved(self):
        result = audit_pair(
            "In 612 participants, Model-A7 reached 87.08% (Li, 2023).",
            "Model-A7 reached 87.08% among 612 participants (Li, 2023).",
            protected_terms=["Model-A7"],
        )
        self.assertTrue(result["conserved"])
        self.assertEqual(result["numbers_delta"], {"removed": {}, "added": {}})

    def test_changed_decimal_reports_removed_and_added(self):
        result = audit_pair(
            "The hazard ratio was 0.73.", "The hazard ratio was 0.75."
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["numbers_delta"]["removed"], {"0.73": 1})
        self.assertEqual(result["numbers_delta"]["added"], {"0.75": 1})

    def test_dropped_ref_marker_reports_citation_delta(self):
        result = audit_pair(
            "The effect held.<!--ref:li2023-->", "The effect held."
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["citations_delta"]["removed"], {"ref:li2023": 1})


class CliTests(unittest.TestCase):
    def _run(self, *argv):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *argv],
            capture_output=True,
            text=True,
        )

    def test_pair_mode_advisory_exit_zero_despite_delta(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.md"
            rev = Path(td) / "rev.md"
            src.write_text("Accuracy was 87.08%.", encoding="utf-8")
            rev.write_text("Accuracy was 88.00%.", encoding="utf-8")
            proc = self._run("pair", "--source", str(src), "--revision", str(rev))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["conserved"])

    def test_pair_mode_strict_exit_one_on_delta_zero_when_conserved(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.md"
            rev = Path(td) / "rev.md"
            src.write_text("Accuracy was 87.08%.", encoding="utf-8")
            rev.write_text("Accuracy was 88.00%.", encoding="utf-8")
            same = Path(td) / "same.md"
            same.write_text("Accuracy was 87.08%, unchanged.", encoding="utf-8")
            drifted = self._run(
                "pair", "--source", str(src), "--revision", str(rev), "--strict"
            )
            conserved = self._run(
                "pair", "--source", str(src), "--revision", str(same), "--strict"
            )
        self.assertEqual(drifted.returncode, 1)
        self.assertEqual(conserved.returncode, 0, conserved.stderr)


# Cases of this copy (header change 6). Each fixture pair runs through the CLI with --strict:
# exit 0 when every token is conserved or only placeholders were filled, exit 1 otherwise.

EMPTY = {"removed": {}, "added": {}}
EMPTY_STRENGTH = {"strong_added": {}, "hedges_removed": {}}
DELTAS = ("numbers_delta", "citations_delta", "protected_terms_delta", "latex_keys_delta",
          "placeholders_delta", "strength_delta")


def run_cli(revision: str, *extra: str, source: str = "base.tex") -> tuple[int, dict]:
    """Runs in FIXTURES, so a claims: row can name claims.json by a relative path."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "pair", "--source", str(FIXTURES / source),
         "--revision", str(FIXTURES / revision), "--strict", *extra],
        capture_output=True, text=True, check=False, cwd=FIXTURES,
    )
    assert proc.stderr == "", proc.stderr
    return proc.returncode, json.loads(proc.stdout)


def check_deltas(report: dict, deltas: dict) -> None:
    for key in DELTAS:
        empty = EMPTY_STRENGTH if key == "strength_delta" else EMPTY
        assert report[key] == deltas.get(key, empty), key


@pytest.mark.parametrize(
    ("revision", "status", "deltas", "fills"),
    [
        ("reworded.tex", 0, {}, []),
        # Without --authorize no fill is verified, so a fill-only pass exits 1 (change 8).
        ("filled.tex", 1, {}, [{"placeholder": "P40", "value": "180"},
                               {"placeholder": "P96", "value": "120"},
                               {"placeholder": "P100", "value": "2.5%"}]),
        ("dropped_number.tex", 1, {"numbers_delta": {"removed": {"312": 1}, "added": {}}}, []),
        ("changed_number.tex", 1,
         {"numbers_delta": {"removed": {"70%": 1}, "added": {"75%": 1}}}, []),
        ("dropped_cite.tex", 1,
         {"latex_keys_delta": {"removed": {"\\cite{Beta2022}": 1}, "added": {}}}, []),
        ("changed_locator.tex", 1, {"numbers_delta": {"removed": {"3": 1}, "added": {"4": 1}}}, []),
    ],
)
def test_fixture_pairs(revision: str, status: int, deltas: dict, fills: list) -> None:
    returncode, report = run_cli(revision)
    assert returncode == status, report
    assert report["conserved"] is (status == 0)
    assert report["fills"] == fills
    assert report["unverified_fills"] == fills
    assert report["fill_conflicts"] == {}
    check_deltas(report, deltas)


def test_base_fixture_tokens() -> None:
    text = CHECKER.read_text(FIXTURES / "base.tex")
    assert dict(extract_numbers(text)) == {
        "312": 1, "70%": 1, "0%": 1, "1": 1, "150": 1, "48,512": 1, "95": 1, "3": 1, "one": 1,
    }
    assert dict(CHECKER.extract_placeholders(text)) == {"P40": 1, "P96": 1, "P100": 1}
    assert dict(CHECKER.extract_latex_keys(text)) == {
        "\\label{sec:results}": 1, "\\ref{tab:filter}": 1, "\\cite{Alpha2021}": 1,
        "\\cite{Beta2022}": 1, "\\cite{Gamma2027Example}": 1, "\\cite{Delta2028}": 1,
    }
    assert dict(extract_citation_tokens(text)) == {}


@pytest.mark.parametrize(
    ("line", "kept"),
    [
        ("80\\% of runs % a comment", "80\\% of runs "),
        ("a line break\\\\% a comment", "a line break\\\\"),
        ("a line break, then a percent sign \\\\\\% stay",
         "a line break, then a percent sign \\\\\\% stay"),
        ("% a whole-line comment", ""),
    ],
)
def test_tex_comment_starts_after_an_even_number_of_backslashes(line: str, kept: str) -> None:
    assert CHECKER.TEX_COMMENT_RE.sub(r"\1", line) == kept


def test_comments_are_stripped_only_from_tex_files(tmp_path: Path) -> None:
    for suffix, numbers in ((".tex", {"80%": 1}), (".txt", {"80%": 1, "75": 1, "1": 1})):
        path = tmp_path / f"a{suffix}"
        path.write_text("80\\% of runs % 75 in draft 1\n", encoding="utf-8")
        assert dict(extract_numbers(CHECKER.read_text(path))) == numbers


def test_cite_variants_ref_and_label() -> None:
    keys = CHECKER.extract_latex_keys(
        "\\citep*[e.g.][p.~5]{a, b} \\citet{c} \\cite{a} Section~\\ref{sec:x}\\label{sec:x} "
        "\\labelindent=0pt \\pageref{sec:y} \\citeauthor{d}"
    )
    assert dict(keys) == {"\\cite{a}": 2, "\\cite{b}": 1, "\\cite{c}": 1,
                          "\\ref{sec:x}": 1, "\\label{sec:x}": 1}


def test_digits_in_keys_are_not_numbers_but_locators_are() -> None:
    text = "as shown~\\cite{smith-2020} in Section~\\ref{sec:v2-3}~\\citep[p.~5]{lee-2019}."
    assert dict(extract_numbers(text)) == {"5": 1}
    assert dict(extract_citation_tokens(text)) == {}


def test_changed_ref_target_and_dropped_label_are_deltas() -> None:
    result = audit_pair("See Table~\\ref{tab:a}.\\label{sec:r}", "See Table~\\ref{tab:b}.")
    assert not result["conserved"]
    assert result["latex_keys_delta"] == {
        "removed": {"\\ref{tab:a}": 1, "\\label{sec:r}": 1}, "added": {"\\ref{tab:b}": 1},
    }


def test_built_text_placeholder_fill_is_a_fill_not_a_loss() -> None:
    result = audit_pair("pass@1 ranges from [PENDING P3] to [PENDING P4].",
                        "pass@1 ranges from 12.5% to 31.0%.", verified={"12.5%", "31.0%"})
    assert result["conserved"]
    assert result["fills"] == [{"placeholder": "P3", "value": "12.5%"},
                               {"placeholder": "P4", "value": "31.0%"}]
    assert result["numbers_delta"] == EMPTY and result["placeholders_delta"] == EMPTY
    unchecked = audit_pair("from [PENDING P3] to [PENDING P4].", "from 12.5% to 31.0%.",
                           verified={"12.5%"})
    assert not unchecked["conserved"]
    assert unchecked["unverified_fills"] == [{"placeholder": "P4", "value": "31.0%"}]


def test_fill_next_to_a_changed_number_reports_both() -> None:
    result = audit_pair("\\pending{P40} of the 204 pairs", "180 of the 205 pairs")
    assert not result["conserved"]
    assert result["fills"] == [{"placeholder": "P40", "value": "180"}]
    assert result["numbers_delta"] == {"removed": {"204": 1}, "added": {"205": 1}}


def test_dropped_placeholder_is_a_loss_not_a_fill() -> None:
    result = audit_pair("Kept \\pending{P40} of 204. Dropped \\pending{P41}.", "Kept 180 of 204.")
    assert not result["conserved"]
    assert result["fills"] == [{"placeholder": "P40", "value": "180"}]
    assert result["placeholders_delta"] == {"removed": {"P41": 1}, "added": {}}


def test_one_placeholder_filled_with_two_values_is_a_conflict() -> None:
    result = audit_pair("Keep \\pending{P40} pairs; later \\pending{P40} pairs.",
                        "Keep 180 pairs; later 181 pairs.")
    assert not result["conserved"]
    assert result["fill_conflicts"] == {"P40": ["180", "181"]}
    same = audit_pair("Keep \\pending{P40} pairs; later \\pending{P40} pairs.",
                      "Keep 180 pairs; later 180 pairs.", verified={"180"})
    assert same["conserved"] and same["fill_conflicts"] == {}


def test_moved_placeholder_is_not_a_fill() -> None:
    result = audit_pair("\\pending{P1} then 5 and 6.", "7 then 5 and \\pending{P1}.")
    assert result["fills"] == []
    assert result["numbers_delta"] == {"removed": {"6": 1}, "added": {"7": 1}}
    assert result["placeholders_delta"] == EMPTY


# Number words, strength words and --authorize (change 8).


def test_number_words_are_number_tokens() -> None:
    text = ("Six channels, twenty percent of runs, half of them and twice as many; "
            "seventy-one sixty. On behalf of \\half none; sixes stay words.")
    assert dict(extract_numbers(text)) == {
        "six": 1, "twenty percent": 1, "half": 1, "twice": 1, "seventy": 1, "one": 1, "sixty": 1,
    }


def test_a_number_word_in_place_of_a_placeholder_is_not_a_fill() -> None:
    result = audit_pair("\\pending{P5} channels", "six channels")
    assert result["fills"] == []
    assert result["placeholders_delta"] == {"removed": {"P5": 1}, "added": {}}
    assert result["numbers_delta"] == {"removed": {}, "added": {"six": 1}}


def test_strong_word_added_is_a_delta_and_a_move_down_is_not() -> None:
    result = audit_pair("The audit bounds the rate.", "The audit proves the rate.")
    assert not result["conserved"]
    assert result["strength_delta"] == {"strong_added": {"proves": 1}, "hedges_removed": {}}
    down = audit_pair("The audit proves the rate.", "The audit suggests the rate.")
    assert down["conserved"] and down["strength_delta"] == EMPTY_STRENGTH


def test_words_base_fixture_tokens() -> None:
    text = CHECKER.read_text(FIXTURES / "words_base.tex")
    assert dict(extract_numbers(text)) == {"six": 1, "four": 1, "80": 1}
    assert dict(CHECKER._word_tokens(CHECKER.STRONG_RE, text)) == {}
    assert dict(CHECKER._word_tokens(CHECKER.HEDGE_RE, text)) == {"suggests": 1, "at least": 1}


@pytest.mark.parametrize(
    ("revision", "status", "deltas", "fills"),
    [
        ("words_reworded.tex", 0, {}, []),
        ("words_dropped_six.tex", 1,
         {"numbers_delta": {"removed": {"six": 1}, "added": {}}}, []),
        ("words_proves.tex", 1,
         {"strength_delta": {"strong_added": {"proves": 1}, "hedges_removed": {"suggests": 1}}},
         []),
        ("words_no_at_least.tex", 1,
         {"strength_delta": {"strong_added": {}, "hedges_removed": {"at least": 1}}}, []),
        ("words_filled.tex", 1, {}, [{"placeholder": "P100", "value": "2.5%"}]),
    ],
)
def test_words_fixture_pairs(revision: str, status: int, deltas: dict, fills: list) -> None:
    returncode, report = run_cli(revision, source="words_base.tex")
    assert returncode == status, report
    assert report["conserved"] is (status == 0)
    assert report["fills"] == report["unverified_fills"] == fills
    check_deltas(report, deltas)


CLAIMS = "claims:claims.json#audit."


@pytest.mark.parametrize(
    ("revision", "rows", "status", "unauthorized", "failing"),
    [
        pytest.param("words_filled.tex", "# no row for the fill\nsix\tdecision:D13",
                     1, ["2.5%"], 0, id="invented-fill-no-row-fails"),
        pytest.param("words_filled.tex", "2.5%\tdecision:D13",
                     1, ["2.5%"], 0, id="fill-with-a-decision-row-only-fails"),
        pytest.param("words_filled.tex", f"2.5%\t{CLAIMS}error_bound_pct\tP100 fill",
                     0, [], 0, id="fill-claims-value-matches-passes"),
        pytest.param("words_filled.tex", "2.5%\tclaims:claims.json#claims.0.value",
                     0, [], 0, id="fill-claims-list-index-string-value-passes"),
        pytest.param("words_filled.tex", f"2.5%\t{CLAIMS}jobs_reviewed\tP100 fill",
                     1, ["2.5%"], 1, id="fill-claims-wrong-value-fails"),
        pytest.param("words_filled.tex", "2.5%\tclaims:missing.json#audit.x",
                     1, ["2.5%"], 1, id="fill-claims-missing-file-fails"),
        pytest.param("words_filled.tex",
                     "2.5%\tclaims:claims_dotted.json#models.vendor-model-1.5.score_pct\tP100 fill",
                     0, [], 0, id="fill-claims-dotted-model-name-passes"),
        pytest.param("words_filled.tex",
                     "2.5%\tclaims:claims_dotted.json#models.vendor-model-1.5.recall_pct",
                     1, ["2.5%"], 1, id="fill-claims-dotted-model-name-missing-member-fails"),
        pytest.param("words_dropped_six.tex", "six\tfinding:1a2b3c4d\tthe count was wrong",
                     0, [], 0, id="finding-present-passes"),
        pytest.param("words_dropped_six.tex", "six\tfinding:0badc0de",
                     1, ["six"], 1, id="finding-absent-fails"),
        pytest.param("words_dropped_six.tex", "six\tfinding:D13",
                     1, ["six"], 1, id="finding-not-8-hex-fails"),
        pytest.param("words_dropped_six.tex", "six\tdecision:D13",
                     0, [], 0, id="decision-present-passes"),
        pytest.param("words_dropped_six.tex", "six\tdecision:D99",
                     1, ["six"], 1, id="decision-absent-fails"),
        pytest.param("words_dropped_six.tex", "six\towner:yes",
                     1, ["six"], 1, id="unknown-authority-fails"),
        pytest.param("words_proves.tex", "proves\tdecision:D13\nsuggests\tdecision:D13",
                     0, [], 0, id="strength-words-authorized-pass"),
        pytest.param("changed_number.tex", f"75%\t{CLAIMS}catch_pct\n70%\t{CLAIMS}old_catch_pct",
                     1, ["70%"], 0, id="claims-row-cannot-authorize-a-removed-number"),
        pytest.param("changed_number.tex", f"75%\t{CLAIMS}catch_pct\n70%\tdecision:D13",
                     0, [], 0, id="added-number-by-claims-removed-by-decision-passes"),
        pytest.param("dropped_cite.tex", "\\cite{Beta2022}\tdecision:D13",
                     0, [], 0, id="cite-key-authorized-passes"),
    ],
)
def test_authorize(tmp_path: Path, revision: str, rows: str, status: int,
                   unauthorized: list, failing: int) -> None:
    tsv = tmp_path / "authorize.tsv"
    tsv.write_text(rows + "\n", encoding="utf-8")
    returncode, report = run_cli(
        revision, "--authorize", str(tsv), "--findings", str(FIXTURES / "findings.md"),
        "--decisions", str(FIXTURES / "decisions.md"),
        source="words_base.tex" if revision.startswith("words_") else "base.tex",
    )
    authorization = report["authorization"]
    assert returncode == status, authorization
    assert authorization["authorized"] is (status == 0)
    assert [entry["token"] for entry in authorization["unauthorized"]] == unauthorized
    assert len(authorization["failing_rows"]) == failing, authorization["failing_rows"]


@pytest.mark.parametrize(
    ("token", "value", "equal"),
    [("180", 180, True), ("180", 180.0, True), ("2.5%", 2.5, True), ("2.5%", "2.5%", True),
     ("24,994", 24994, True), ("1,200", "1,200", True), ("20.3%", 0.2034, False),
     ("2.5%", True, False), ("six", 6, False)],
)
def test_claims_value_equals_token_without_percent_and_separators(
    tmp_path: Path, token: str, value, equal: bool
) -> None:
    path = tmp_path / "claims.json"
    path.write_text(json.dumps({"a": {"v": value}}), encoding="utf-8")
    assert (CHECKER._claims_problem(token, f"{path}#a.v") is None) is equal


@pytest.mark.parametrize(
    ("key", "token", "problem"),
    [
        # The member vendor-model-1.5 is longer than the decoy vendor-model-1 -> 5 (9.9).
        ("models.vendor-model-1.5.score_pct", "2.5", None),
        ("models.vendor-model-1.5.score_pct", "9.9", "holds 2.5, not 9.9"),
        ("models.vendor-model-1.5.runs.0.value", "2.5%", None),
        ("a.b.c", "2.5", None),
        ("models.vendor-model-1.score_pct", "9.9", "has no key models.vendor-model-1.score_pct"),
        ("models.vendor-model-1.5.runs.1.value", "2.5%", "has no key"),
    ],
)
def test_claims_key_walks_the_longest_dotted_member_name(
    key: str, token: str, problem: str | None
) -> None:
    reason = CHECKER._claims_problem(token, f"{FIXTURES / 'claims_dotted.json'}#{key}")
    if problem is None:
        assert reason is None
    else:
        assert reason is not None and problem in reason, reason


if __name__ == "__main__":
    unittest.main()
