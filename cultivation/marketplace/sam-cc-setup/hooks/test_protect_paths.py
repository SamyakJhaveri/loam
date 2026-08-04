#!/usr/bin/env python3
"""Controls for protect_paths.py, in both directions.

A guard that reports zero blocks is worthless unless the positive controls
still fire. Run:  python3 test_protect_paths.py
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pp", HERE / "protect_paths.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)

def run_case(tool: str, tool_input: dict, patterns: list[str], root: str) -> str:
    return pp.verdict({"tool_name": tool, "tool_input": tool_input}, patterns, root)


def main() -> int:
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        root = os.path.realpath(td)
        os.makedirs(os.path.join(root, "results/evaluation"), exist_ok=True)
        patterns = ["results/evaluation/*", "vendor/upstream"]

        # (label, tool, tool_input, expect_block)
        cases = [
            # --- Edit/Write ---------------------------------------------------
            ("Write into protected dir", "Write",
             {"file_path": "results/evaluation/x.json"}, True),
            ("Edit file directly named by glob", "Edit",
             {"file_path": "results/evaluation/deep/y.json"}, True),
            ("Write to protected dir given as bare dir pattern", "Write",
             {"file_path": "vendor/upstream/main.c"}, True),
            ("dot-slash evasion", "Write",
             {"file_path": "./results/evaluation/x.json"}, True),
            ("parent-dir evasion", "Write",
             {"file_path": "docs/../results/evaluation/x.json"}, True),
            ("unprotected sibling", "Write",
             {"file_path": "results/analysis/x.json"}, False),
            ("outside the repo", "Write",
             {"file_path": "/etc/hosts"}, False),
            # --- Bash deletes -------------------------------------------------
            ("plain rm", "Bash",
             {"command": "rm results/evaluation/x.json"}, True),
            ("rm -rf on the dir", "Bash",
             {"command": "rm -rf results/evaluation"}, True),
            ("wrapped rm (env)", "Bash",
             {"command": "env rm results/evaluation/x.json"}, True),
            ("absolute-path rm binary", "Bash",
             {"command": "/bin/rm results/evaluation/x.json"}, True),
            ("rm in second segment", "Bash",
             {"command": "echo hi && rm results/evaluation/x.json"}, True),
            ("bash -c indirection", "Bash",
             {"command": "bash -lc 'rm results/evaluation/x.json'"}, True),
            ("path only mentioned, no delete verb", "Bash",
             {"command": "ls results/evaluation/"}, False),
            ("rm of something else, path in other segment", "Bash",
             {"command": "rm /tmp/scratch.txt && cat results/evaluation/x.json"}, False),
            # --- Bash redirects -----------------------------------------------
            ("redirect overwrite", "Bash",
             {"command": "echo '{}' > results/evaluation/x.json"}, True),
            ("append redirect", "Bash",
             {"command": "echo '{}' >> results/evaluation/x.json"}, True),
            ("redirect elsewhere", "Bash",
             {"command": "echo hi > /tmp/out.txt"}, False),
            # --- other tools --------------------------------------------------
            ("Read is never blocked", "Read",
             {"file_path": "results/evaluation/x.json"}, False),
        ]

        print(f"{'result':7} {'expect':7} {'got':7}  case")
        print("-" * 72)
        for label, tool, ti, expect in cases:
            got = run_case(tool, ti, patterns, root).startswith("block")
            ok = got == expect
            fails += not ok
            print(f"{'ok' if ok else 'FAIL':7} {str(expect):7} {str(got):7}  {label}")
        print("-" * 72)
        print(f"{len(cases) - fails}/{len(cases)} passed")
        if fails:
            print("\nA failing POSITIVE control means the guard has gone blind - a "
                  "session with zero blocks would then prove nothing.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
