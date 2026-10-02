# Tests for ../scripts/check_consistency.py.
# Lines from "from __future__" through "class ConsistencyCheckerTests" and its five tests are
# taken from https://github.com/yuan1z0825/nature-skills, commit
# 84880815fb37317b3766bff2c2abba395b8993c3, skills/nature-shared/tests/test_check_consistency.py,
# lines 1-59 (the file without its "__main__" block), Apache License 2.0.
# Changes made in this copy (the research-paper plugin): this header; SCRIPT is
# ../scripts/check_consistency.py and scripts/ is put on sys.path (the script imports
# paper_config); imports json, os, subprocess and pytest; the "__main__" block is dropped (pytest
# runs the file); everything after ConsistencyCheckerTests is new (fixture tests with fixtures in
# fixtures/check_consistency/, tests of the two fixes, and tests of the config defaults at the
# end); subprocess runs set PAPER_TOOLS_ROOT; the fixtures and the hash test hold synthetic text.
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "check_consistency.py"
SPEC = importlib.util.spec_from_file_location("check_consistency", SCRIPT)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class ConsistencyCheckerTests(unittest.TestCase):
    def run_text(
        self,
        text: str,
        groups: dict[str, tuple[str, ...]] | None = None,
    ) -> list[object]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manuscript.tex"
            path.write_text(text, encoding="utf-8")
            return CHECKER.run_checks([path], groups)

    def test_clean_text_has_no_findings(self) -> None:
        findings = self.run_text(
            "This study used a 35 mm specimen and obtained values of 8.26 and 9.14.",
            CHECKER.DEFAULT_TERM_GROUPS,
        )
        self.assertEqual([], findings)

    def test_term_variants_are_reported(self) -> None:
        findings = self.run_text(
            "This study defines the task. Later, this work reports the results.",
            CHECKER.DEFAULT_TERM_GROUPS,
        )
        self.assertIn("TERM_VARIANTS_PRESENT", {item.code for item in findings})

    def test_numeric_precision_variants_are_reported(self) -> None:
        findings = self.run_text("The score was 8.26 in Table 1 and 8.260 in the abstract.")
        self.assertIn("NUMERIC_PRECISION_VARIANT", {item.code for item in findings})

    def test_equivalent_length_units_are_reported(self) -> None:
        findings = self.run_text("The cover was 35 mm in Methods and 3.5 cm in the caption.")
        self.assertIn(
            "EQUIVALENT_LENGTH_UNIT_VARIANT",
            {item.code for item in findings},
        )

    def test_custom_term_group_is_supported(self) -> None:
        findings = self.run_text(
            "The test specimen was loaded. Each sample was then measured.",
            {"test-object": ("specimen", "sample")},
        )
        self.assertIn("TERM_VARIANTS_PRESENT", {item.code for item in findings})


FIXTURES = Path(__file__).parent / "fixtures" / "check_consistency"


def run_script(*args: str, root: Path = FIXTURES, config: Path | None = None):
    """The script run with the project root (and config file) given by environment."""
    env = {k: v for k, v in os.environ.items() if k != "PAPER_TOOLS_CONFIG"}
    env["PAPER_TOOLS_ROOT"] = str(root)
    if config is not None:
        env["PAPER_TOOLS_CONFIG"] = str(config)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=root,
        env=env,
    )


def run_fixture(name: str) -> tuple[int, list[str]]:
    """Exit status and sorted finding codes of the script on one fixture."""
    result = run_script("--fail-on-findings", "--json", str(FIXTURES / name))
    return result.returncode, sorted(item["code"] for item in json.loads(result.stdout))


@pytest.mark.parametrize(
    ("name", "codes"),
    [
        ("clean.tex", []),
        ("seeded.tex", ["TERM_VARIANTS_PRESENT"]),
        ("percent_clean.tex", []),
        ("percent_seeded.tex", ["NUMERIC_PRECISION_VARIANT"]),
        ("units_clean.tex", []),
        (
            "units_seeded.tex",
            [
                "EQUIVALENT_DATA_UNIT_VARIANT",
                "EQUIVALENT_DATA_UNIT_VARIANT",
                "EQUIVALENT_LENGTH_UNIT_VARIANT",
                "EQUIVALENT_TIME_UNIT_VARIANT",
            ],
        ),
    ],
)
def test_fixture_exit_status(name: str, codes: list[str]) -> None:
    status, found = run_fixture(name)
    assert found == codes
    assert status == (1 if codes else 0)


@pytest.mark.parametrize(
    ("line", "visible"),
    [
        (r"65\% of loans % a comment", r"65\% of loans "),
        (r"a line break\\% a comment", r"a line break\\"),
        (
            r"a line break and a percent sign \\\% stay",
            r"a line break and a percent sign \\\% stay",
        ),
        ("% a whole-line comment", ""),
    ],
)
def test_comments_drop_but_escaped_percent_stays(line: str, visible: str) -> None:
    assert list(CHECKER.visible_lines(line)) == [(1, visible)]


@pytest.mark.parametrize(
    ("spelling", "reading"),
    [
        ("mm", ("length", "mm")),
        ("µm", ("length", "um")),
        ("μs", ("time", "us")),
        ("ms", ("time", "ms")),
        ("MB", ("data", "MB")),
        ("Mb", ("data", "Mb")),
        ("KB", ("data", "kB")),
        ("kB", ("data", "kB")),
        ("kiB", ("data", "KiB")),
        ("mM", None),
        ("Mm", None),
        ("M", None),
        ("Ms", None),
        ("MS", None),
        ("S", None),
        ("mb", None),
        ("B", ("data", "B")),
        ("b", None),
    ],
)
def test_unit_case_rule(spelling: str, reading: tuple[str, str] | None) -> None:
    match = CHECKER.UNIT_PATTERN.fullmatch(f"5 {spelling}")
    assert (CHECKER.normalized_unit(match.group(2)) if match else None) == reading


def test_hash_and_subfigure_letters_are_not_bits() -> None:
    line = r"ExampleSys~\texttt{7e21f0ad}; BaselineSys~\texttt{12b90577}; see Figure 3b."
    assert not list(CHECKER.UNIT_PATTERN.finditer(line))


def write_project(root: Path, config: str) -> Path:
    """A project with an abstract and two sections, and its paper-tools.toml."""
    sections = root / "paper" / "sections"
    sections.mkdir(parents=True)
    (sections / "abstract.tex").write_text("ExampleSys checks each job twice.\n", encoding="utf-8")
    (sections / "intro.tex").write_text("The Example system runs 8.26 jobs.\n", encoding="utf-8")
    (sections / "results.tex").write_text("It runs 8.260 jobs.\n", encoding="utf-8")
    path = root / "paper-tools.toml"
    path.write_text(config, encoding="utf-8")
    return path


GROUP = '[consistency.term_groups]\nsystem-name = ["ExampleSys", "Example system"]\n'


def test_config_names_the_files_and_the_term_groups(tmp_path: Path) -> None:
    config = write_project(tmp_path, '[paper]\nsections = ["intro", "missing"]\n' + GROUP)
    result = run_script("--json", "--fail-on-findings", root=tmp_path, config=config)
    assert result.returncode == 1, result.stdout + result.stderr
    findings = json.loads(result.stdout)
    assert [item["code"] for item in findings] == ["TERM_VARIANTS_PRESENT"]  # results.tex unread
    assert "term group 'system-name'" in findings[0]["message"]
    assert "NOTE: no file at" in result.stderr and "missing.tex" in result.stderr


def test_empty_section_list_reads_every_section_file(tmp_path: Path) -> None:
    config = write_project(tmp_path, GROUP)
    result = run_script("--json", root=tmp_path, config=config)
    assert result.returncode == 0, result.stdout + result.stderr
    codes = sorted(item["code"] for item in json.loads(result.stdout))
    assert codes == ["NUMERIC_PRECISION_VARIANT", "TERM_VARIANTS_PRESENT"]


def test_a_path_on_the_command_line_wins_over_the_config(tmp_path: Path) -> None:
    config = write_project(tmp_path, GROUP)
    result = run_script("--json", str(FIXTURES / "clean.tex"), root=tmp_path, config=config)
    assert result.returncode == 0 and json.loads(result.stdout) == [], result.stdout


def test_no_path_and_no_configured_file_is_a_usage_error(tmp_path: Path) -> None:
    result = run_script(root=tmp_path)
    assert result.returncode == 2
    assert "required: paths" in result.stderr
