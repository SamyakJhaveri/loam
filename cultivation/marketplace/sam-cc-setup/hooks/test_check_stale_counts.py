#!/usr/bin/env python3
"""Controls for check_stale_counts.py, in both directions.

A screen that reports zero findings is worthless unless you can show it still
fires. Builds a throwaway repo with a config whose truths are `printf` commands,
seeds correct and stale prose, and checks both directions plus the exemption and
broken-truth paths.

    python3 test_check_stale_counts.py
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "check_stale_counts.py"

CONFIG = {
    "truths": {"kf_total": "printf 10", "spec_total": "printf 60"},
    "checks": [
        {"pattern": r"(\d+)\s+KNOWN_FAIL\s+specs", "truth": "kf_total",
         "message": "project-wide KNOWN_FAIL count"},
        {"pattern": r"(\d+)\s+specs\s+total", "truth": "spec_total",
         "message": "spec total"},
    ],
    "search": ["README.md", "docs"],
    "skip": ["archive"],
    "exempt_markers": ["kept as history"],
}


def run(root: pathlib.Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True, text=True,
    )


def build_repo(td: str, readme: str, cfg: dict = CONFIG) -> pathlib.Path:
    root = pathlib.Path(td)
    (root / ".claude").mkdir()
    (root / ".claude" / "stale-counts.json").write_text(json.dumps(cfg))
    (root / "README.md").write_text(readme)
    (root / "docs").mkdir()
    (root / "docs" / "archive").mkdir()
    (root / "docs" / "archive" / "old.md").write_text("8 KNOWN_FAIL specs\n")
    return root


def main() -> int:
    fails = 0

    def check(label: str, ok: bool, detail: str = ""):
        nonlocal fails
        fails += not ok
        print(f"{'ok' if ok else 'FAIL':5} {label}" + (f"  [{detail}]" if detail and not ok else ""))

    # POSITIVE control: a stale number must be found.
    with tempfile.TemporaryDirectory() as td:
        r = run(build_repo(td, "There are 8 KNOWN_FAIL specs here.\n"))
        check("stale count flagged (exit 1)", r.returncode == 1, r.stdout + r.stderr)
        check("finding names file:line", "README.md:1" in r.stdout)

    # NEGATIVE control: the correct number must not flag.
    with tempfile.TemporaryDirectory() as td:
        r = run(build_repo(td, "There are 10 KNOWN_FAIL specs and 60 specs total.\n"))
        check("correct counts pass (exit 0)", r.returncode == 0, r.stdout + r.stderr)

    # Exemption: inline marker, and a marker up to 4 lines above.
    with tempfile.TemporaryDirectory() as td:
        r = run(build_repo(
            td,
            "8 KNOWN_FAIL specs  <!-- stale-counts: allow -->\n"
            "kept as history:\n"
            "\n"
            "the old count was 8 KNOWN_FAIL specs\n",
        ))
        check("exempt markers honoured", r.returncode == 0, r.stdout + r.stderr)

    # Skip list: the stale line in docs/archive/ must not be scanned.
    with tempfile.TemporaryDirectory() as td:
        r = run(build_repo(td, "clean file\n"))
        check("skip dirs honoured", r.returncode == 0, r.stdout + r.stderr)

    # Second check pattern also fires.
    with tempfile.TemporaryDirectory() as td:
        r = run(build_repo(td, "Rodinia: 59 specs total\n"))
        check("second truth flagged", r.returncode == 1, r.stdout + r.stderr)

    # No config: dormant, exit 0.
    with tempfile.TemporaryDirectory() as td:
        r = run(pathlib.Path(td))
        check("no config is dormant (exit 0)", r.returncode == 0, r.stdout + r.stderr)

    # Broken truth command: must abort loudly, never report clean.
    with tempfile.TemporaryDirectory() as td:
        bad = dict(CONFIG, truths={"kf_total": "false", "spec_total": "printf 60"})
        r = run(build_repo(td, "clean\n", bad))
        check("broken truth aborts (exit 3)", r.returncode == 3, r.stdout + r.stderr)

    print(f"\n{'all passed' if not fails else f'{fails} FAILED'}")
    if fails:
        print("A failing POSITIVE control means the screen has gone blind - a clean "
              "run of check_stale_counts.py would then prove nothing.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
