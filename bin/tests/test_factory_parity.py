"""bin/factory-parity prints PASS, FAIL or N/A per behaviour and ends `parity: PASS` or `parity: FAIL (<ids>)`.

Each case under fixtures/parity/ is a run folder of a few lines cut from real factory runs by
fixtures/parity/cut.py (lines it edits say so there); `pass` is a hand-written run where every behaviour passes.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin" / "factory-parity"
FIXTURES = ROOT / "bin" / "tests" / "fixtures" / "parity"

# (case folder, behaviour id, expected status), from each behaviour's rule in the script's docstring.
CASES = [
    ("p1-pass", "P1", "PASS"),  # init lists verify-distbench
    ("p1-fail", "P1", "FAIL"),  # W35: init without it
    ("p2-pass", "P2", "PASS"),  # W34: router read, then the first Write
    ("p2-fail", "P2", "FAIL"),  # W35: sed -i with no router read
    ("p3-pass", "P3", "PASS"),  # W34: three principle SKILL.md reads, the three decisions.md names
    ("p3-fail", "P3", "FAIL"),  # W34 without those reads
    ("p3-claim", "P3", "FAIL"),  # W34 reading two of the three methods decisions.md names
    ("p4-pass", "P4", "PASS"),  # bin/check result ends check: PASSED
    ("p4-fail", "P4", "FAIL"),  # W34: bin/check timed out, no check: line
    ("p4-refusal", "P4", "FAIL"),  # check: PASSED, but a result shows the sandbox refusal
    ("p4-background", "P4", "PASS"),  # background bin/check, its output file read later
    ("p4-background-other", "P4", "FAIL"),  # background bin/check, check: PASSED read from another file
    ("p5-pass", "P5", "PASS"),  # worker Opus medium, builder Opus xhigh, reviewer Fable high
    ("p5-max", "P5", "FAIL"),  # worker effort max
    ("p5-advisor", "P5", "FAIL"),  # worker advisor on Haiku
    ("p5-haiku", "P5", "FAIL"),  # a builder on Haiku
    ("p5-fable-builder", "P5", "FAIL"),  # Fable outside a reviewer
    ("p6-pass", "P6", "PASS"),  # orchestrator diff, skill read, launch and a drive
    ("p6-fail", "P6", "FAIL"),  # W13a: orchestrator diff, no proof
    ("p6-no-read", "P6", "FAIL"),  # launch and a drive, but no verify-distbench/SKILL.md read
    ("p6-help", "P6", "FAIL"),  # skill read and a drive, but only `launch --help`
    ("p6-no-drive", "P6", "FAIL"),  # skill read and launch, no agent or exec drive
    ("p6-na", "P6", "N/A"),  # W35: diff outside what the skill covers
]


def parity(run: Path, projects: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(run), "--projects-root", str(projects)],
                          capture_output=True, text=True, timeout=60)


def statuses(out: str) -> dict[str, str]:
    """Behaviour id -> status, from lines `<STATUS> <id> <name>: <evidence>`."""
    rows = {}
    for line in out.splitlines()[:-1]:
        status, pid = line.split(" ", 2)[:2]
        rows[pid] = status
    return rows


@pytest.mark.parametrize(("case", "pid", "expected"), CASES, ids=[c[0] for c in CASES])
def test_behaviour(case: str, pid: str, expected: str) -> None:
    proc = parity(FIXTURES / case / "run", FIXTURES / case / "projects")
    assert proc.returncode in (0, 1), proc.stderr
    assert statuses(proc.stdout)[pid] == expected, proc.stdout
    last = proc.stdout.splitlines()[-1]
    if expected == "FAIL":
        assert proc.returncode == 1 and last.startswith("parity: FAIL (") and pid in last[len("parity: FAIL ("):-1].split(", ")


def test_a_run_where_every_behaviour_passes_exits_zero() -> None:
    proc = parity(FIXTURES / "pass" / "run", FIXTURES / "pass" / "projects")
    assert (proc.returncode, proc.stdout.splitlines()[-1]) == (0, "parity: PASS"), proc.stdout
    assert set(statuses(proc.stdout).values()) == {"PASS"}, proc.stdout


def test_a_key_folder_holding_one_run_is_read_as_that_run(tmp_path: Path) -> None:
    shutil.copytree(FIXTURES / "pass" / "run", tmp_path / "W1-key" / "0123abcd")
    proc = parity(tmp_path / "W1-key", FIXTURES / "pass" / "projects")
    assert (proc.returncode, proc.stdout.splitlines()[-1]) == (0, "parity: PASS"), proc.stdout + proc.stderr


def test_a_folder_with_no_round_transcript_is_unusable(tmp_path: Path) -> None:
    proc = parity(tmp_path, tmp_path)
    assert (proc.returncode, proc.stdout) == (2, ""), proc.stdout
