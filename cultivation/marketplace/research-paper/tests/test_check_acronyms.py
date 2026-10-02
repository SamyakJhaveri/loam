"""Fixture tests for ../scripts/check_acronyms.py on LaTeX input.

fixtures/check_acronyms/clean/ is a two-file LaTeX document in which every acronym is
defined before use, and each construct the LaTeX reader skips (a comment, math, a
citation, a cross-reference, a label, verbatim, a listing, \\verb, \\texttt, a heading,
a caption, a figure path, a tabular) holds an acronym that would be a finding if read.
fixtures/check_acronyms/seeded/ is the same document plus one undefined acronym on
sections/body.tex line 29.
fixtures/check_acronyms/allowlist/ tests --allow-file with allow.txt: clean.tex uses only
allowlisted acronyms, undefined; seeded.tex adds SLoC, which the allowlist leaves out.
fixtures/check_acronyms/baseline/ tests --baseline: known.tex has one undefined acronym
(SLoC), the one row of baseline.txt; new.tex adds AST, which the baseline does not list;
baseline_no_reason.txt holds the SLoC row with no reason.
Every subprocess run sets PAPER_TOOLS_ROOT, so the config defaults of paper-tools.toml come
from a fixture or a temporary folder, never from the repository the tests sit in.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))  # the script imports paper_config
SCRIPT = PLUGIN / "scripts" / "check_acronyms.py"
FIXTURES = Path(__file__).parent / "fixtures" / "check_acronyms"
SPEC = importlib.util.spec_from_file_location("check_acronyms", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)

# Acronyms that sit only inside constructs the reader skips.
HIDDEN = {"XYZ", "TPU", "RDMA", "HBM", "NVLink", "RMSE", "MAE", "SNR", "PSNR", "LD", "FPGA"}
HIDDEN |= {"ASIC", "CPU", "COUNT", "VHDL", "DSP", "NPU", "SRAM", "DRAM", "LUT", "PENDING"}


def env_for(root: Path, config: Path | None = None) -> dict[str, str]:
    """The environment with the project root (and config file) set for paper_config."""
    env = {k: v for k, v in os.environ.items() if k != "PAPER_TOOLS_CONFIG"}
    env["PAPER_TOOLS_ROOT"] = str(root)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    return env


def run_in(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the script from cwd, with the fixtures folder as the project root."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        env=env_for(FIXTURES),
        capture_output=True,
        text=True,
        check=False,
    )


def run(copy: str, *flags: str) -> subprocess.CompletedProcess[str]:
    """Run the script on one fixture copy from its own directory."""
    return run_in(FIXTURES / copy, "--input", "main.tex", "--scopes", "body,abstract_en", *flags)


def finding_rows(stdout: str) -> list[str]:
    return [
        line for line in stdout.splitlines() if line.startswith("| Body") or line.startswith("| EN")
    ]


def test_clean_copy_passes() -> None:
    result = run("clean", "--fail-on-findings")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Coverage: body, English abstract (complete)" in result.stdout
    assert "No findings." in result.stdout


def test_seeded_defect_fails_with_its_file_and_line() -> None:
    result = run("seeded", "--fail-on-findings")
    assert result.returncode == 1, result.stdout + result.stderr
    assert finding_rows(result.stdout) == [
        "| Body | sections/body.tex:29 | Not defined | TPU | 1 |"
    ]


def test_findings_leave_exit_zero_without_the_flag() -> None:
    result = run("seeded")
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(finding_rows(result.stdout)) == 1


def test_skipped_constructs_are_blank_and_lines_keep_their_source() -> None:
    text, where = CHECKER.read_latex(FIXTURES / "clean" / "main.tex")
    words = set(re.findall(r"[A-Za-z]+", text))
    assert not words & HIDDEN
    assert {"GPU", "GPUs", "ExampleSys", "MPI", "P1"} <= set(re.findall(r"[A-Za-z0-9]+", text))
    lines = text.split("\n")
    assert len(lines) == len(where)
    body = str(FIXTURES / "clean" / "sections" / "body.tex")
    assert (body, 3) in where
    assert "(MPI)" in lines[where.index((body, 3))]
    assert lines.count("# Abstract") == 1 and lines.count("# Main text") == 1


@pytest.mark.parametrize(
    ("line", "kept"),
    [
        (r"80\% of runs % a comment", r"80\% of runs "),
        (r"a line break\\% a comment", r"a line break\\"),
        (
            r"a line break and a percent sign \\\% stay",
            r"a line break and a percent sign \\\% stay",
        ),
        ("% a whole-line comment", ""),
    ],
)
def test_comment_starts_after_an_even_number_of_backslashes(line: str, kept: str) -> None:
    assert CHECKER._tex_strip_comment(line) == kept


# Fixes made in review (each seeded copy fails, each clean copy passes):
# 1. a comment-only line inside a paragraph is no paragraph break, so a definition
#    wrapped around it is read; 2. the label of \hyperref[label]{text} is skipped and its
#    text is read; 3. an \input without braces fails closed (exit 2), never silently skipped.
@pytest.mark.parametrize(
    ("name", "status", "rows"),
    [
        ("comment_line_clean.tex", 0, []),
        (
            "comment_line_seeded.tex",
            1,
            ["| Body | comment_line_seeded.tex:4 | Defined after first use | MPI | 2 |"],
        ),
        ("hyperref_clean.tex", 0, []),
        ("hyperref_seeded.tex", 1, ["| Body | hyperref_seeded.tex:4 | Not defined | TPU | 1 |"]),
        ("bare_input.tex", 2, []),
    ],
)
def test_review_fixes(name: str, status: int, rows: list[str]) -> None:
    result = run_in(
        FIXTURES / "latex_fixes", "--input", name, "--scopes", "body", "--fail-on-findings"
    )
    assert result.returncode == status, result.stdout + result.stderr
    assert finding_rows(result.stdout) == rows
    if status == 0:
        assert "Coverage: body (complete)" in result.stdout


ALLOW = FIXTURES / "allowlist" / "allow.txt"
TEMPLATE = PLUGIN / "templates" / "acronym_allow.txt"
# Terms allow.txt leaves out on purpose; its header gives each one's reason.
LEFT_OUT = {"SLoC", "AST"}


def run_allowlist(name: str, *flags: str) -> subprocess.CompletedProcess[str]:
    return run_in(
        FIXTURES / "allowlist", "--input", name, "--scopes", "body", "--fail-on-findings", *flags
    )


def test_allowlist_silences_an_allowed_term() -> None:
    bare = run_allowlist("clean.tex")
    assert bare.returncode == 1, bare.stdout + bare.stderr
    assert {row.split("|")[4].strip() for row in finding_rows(bare.stdout)} == {
        "CUDA",
        "FAIL",
        "GPU",
        "OpenMP",
        "PASS",
    }
    allowed = run_allowlist("clean.tex", "--allow-file", str(ALLOW))
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert "No findings." in allowed.stdout


def test_allowlist_still_reports_a_left_out_term() -> None:
    result = run_allowlist("seeded.tex", "--allow-file", str(ALLOW))
    assert result.returncode == 1, result.stdout + result.stderr
    assert finding_rows(result.stdout) == ["| Body | seeded.tex:5 | Not defined | SLoC | 1 |"]


def test_allowlist_leaves_out_the_terms_its_header_names() -> None:
    allowed = CHECKER._read_allowlist(ALLOW)
    assert not allowed & LEFT_OUT
    header = ALLOW.read_text(encoding="utf-8")
    assert all(f"#   {term} " in header for term in LEFT_OUT)


def test_shipped_allowlist_template_holds_acronyms_not_built_in() -> None:
    allowed = CHECKER._read_allowlist(TEMPLATE)
    assert allowed and all(CHECKER.is_candidate(term) for term in allowed)
    assert not allowed & CHECKER.DEFAULT_ALLOWLIST


BASELINE_DIR = FIXTURES / "baseline"
BASELINE = BASELINE_DIR / "baseline.txt"
KNOWN_REASON = "fixture ticket T-1 (#1, defined in a later rewrite)"


def run_baseline(name: str, *flags: str) -> subprocess.CompletedProcess[str]:
    return run_in(BASELINE_DIR, "--input", name, "--scopes", "body", *flags)


def test_baseline_only_paper_passes(tmp_path: Path) -> None:
    bare = run_baseline("known.tex", "--fail-on-findings")
    assert bare.returncode == 1, bare.stdout + bare.stderr  # without the baseline SLoC fails
    out = tmp_path / "report.json"
    result = run_baseline("known.tex", "--baseline", "baseline.txt", "--json-out", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    assert finding_rows(result.stdout) == []
    assert f"- KNOWN Body, known.tex:4: SLoC (Not defined; {KNOWN_REASON})" in result.stdout
    assert "No findings outside the baseline." in result.stdout
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["findings"] == []
    assert [(k["acronym"], k["reason"]) for k in report["known"]] == [("SLoC", KNOWN_REASON)]


# --baseline fails on a new finding with or without --fail-on-findings.
@pytest.mark.parametrize("flags", [(), ("--fail-on-findings",)])
def test_new_finding_fails_with_the_baseline(flags: tuple[str, ...]) -> None:
    result = run_baseline("new.tex", "--baseline", "baseline.txt", *flags)
    assert result.returncode == 1, result.stdout + result.stderr
    assert finding_rows(result.stdout) == ["| Body | new.tex:5 | Not defined | AST | 1 |"]
    assert f"- KNOWN Body, new.tex:4: SLoC (Not defined; {KNOWN_REASON})" in result.stdout


@pytest.mark.parametrize(
    "row",
    [
        None,  # baseline_no_reason.txt: no tab
        "SLoC\t",  # a tab, then nothing
        "\tfixture ticket T-1",  # a reason, no acronym
    ],
)
def test_baseline_row_without_reason_fails(tmp_path: Path, row: str | None) -> None:
    baseline = BASELINE_DIR / "baseline_no_reason.txt"
    if row is not None:
        baseline = tmp_path / "baseline.txt"
        baseline.write_text(row + "\n", encoding="utf-8")
    result = run_baseline("known.tex", "--baseline", str(baseline))
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Not checked: a baseline row has no reason" in result.stdout


def test_baseline_rows_have_reasons_and_are_not_allowed() -> None:
    rows = CHECKER._read_baseline(BASELINE)
    assert rows and all(rows.values())
    assert not set(rows) & CHECKER._read_allowlist(ALLOW)  # an allowed term is never a finding


def write_config(tmp_path: Path, main: Path, allow: Path, baseline: Path) -> Path:
    config = tmp_path / "paper-tools.toml"
    config.write_text(
        f'[paper]\nmain_tex = "{main}"\n'
        f'[terms]\nacronym_allow = "{allow}"\nacronym_baseline = "{baseline}"\n',
        encoding="utf-8",
    )
    return config


def run_config(tmp_path: Path, config: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--scopes", "body", *flags],
        cwd=tmp_path,
        env=env_for(tmp_path, config),
        capture_output=True,
        text=True,
        check=False,
    )


def test_config_names_the_input_allowlist_and_baseline(tmp_path: Path) -> None:
    config = write_config(tmp_path, BASELINE_DIR / "new.tex", ALLOW, BASELINE)
    result = run_config(tmp_path, config)
    assert result.returncode == 1, result.stdout + result.stderr  # the baseline gates
    assert finding_rows(result.stdout) == [
        f"| Body | {BASELINE_DIR / 'new.tex'}:5 | Not defined | AST | 1 |"
    ]
    assert f"SLoC (Not defined; {KNOWN_REASON})" in result.stdout
    flagged = run_config(
        tmp_path, config, "--baseline", str(BASELINE_DIR / "baseline_no_reason.txt")
    )
    assert flagged.returncode == 2  # a flag wins over the config


def test_missing_configured_allowlist_and_baseline_are_notes(tmp_path: Path) -> None:
    config = write_config(
        tmp_path, BASELINE_DIR / "new.tex", tmp_path / "a.txt", tmp_path / "b.txt"
    )
    result = run_config(tmp_path, config)
    assert result.returncode == 0, result.stdout + result.stderr  # no baseline, no gate
    assert len(finding_rows(result.stdout)) == 2
    assert result.stderr.count("NOTE: no file at") == 2


def test_no_input_and_no_main_tex_is_a_usage_error(tmp_path: Path) -> None:
    config = tmp_path / "paper-tools.toml"
    config.write_text('[paper]\nmain_tex = ""\n', encoding="utf-8")
    result = run_config(tmp_path, config)
    assert result.returncode == 2
    assert "required: --input" in result.stderr
