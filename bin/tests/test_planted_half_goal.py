"""mutate.py's half-goal mutants stay states the supervisor lets through (#233).

Each drops one file from the Diff; its done checks, Checks output and decisions.md must agree with the tree left,
or the supervisor stops the run before a grader sees it, or a careful judge also fails verified or honest.
Runs the real mutate.py over the frozen evals/clean bases.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MUTATE = ROOT / "bin/factory.d/mutate.py"
FENCE = "~~~~~~~~~~~~ evidence"


def section(text: str, head: str) -> list[str]:
    """The lines inside the evidence fence under the first `## ` heading that starts with head."""
    m = re.search(rf"^{re.escape(head)}.*?\n{FENCE}\n(.*?)\n{FENCE}", text, re.M | re.S)
    return m.group(1).split("\n") if m else []


def stat_paths(text: str) -> set[str]:
    return set(re.findall(r"^ (\S+) +\| ", "\n".join(section(text, "## Diff")), re.M))


class HalfGoalTests(unittest.TestCase):
    def test_half_goal_mutants_agree_with_the_tree_left(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "out"
            subprocess.run([sys.executable, str(MUTATE), str(ROOT / "evals/clean"), str(out)],
                           check=True, capture_output=True)
            mutants = sorted((out / "judge").glob("*--half-goal"))
            self.assertGreaterEqual(len(mutants), 8)
            for d in mutants:
                with self.subTest(case=d.name):
                    text = (d / "prompt.md").read_text(encoding="utf-8")
                    clean = (d.parent / d.name.replace("--half-goal", "--clean") / "prompt.md").read_text(encoding="utf-8")
                    gone = stat_paths(clean) - stat_paths(text)
                    self.assertEqual(len(gone), 1)
                    path = gone.pop()
                    names = re.compile("|".join(rf"(?<![\w.-]){re.escape(t)}(?![\w/-]|\.\w)"
                                                for t in (path, path.rsplit("/", 1)[-1])))
                    ticket = section(text, "## Ticket")
                    checks = ticket[ticket.index("```done-checks") + 1:]
                    checks = checks[:checks.index("```")]
                    for line in checks + section(text, "## decisions.md") + section(text, "## Rows measured"):
                        self.assertIsNone(names.search(line), f"names the dropped {path}: {line[:120]}")
                    # One PASS line per done check left, and none for a check that left.
                    passed = {line[5:] for line in section(text, "## Checks output") if re.fullmatch(r"PASS \S+", line)}
                    named = [set(re.findall(r"\bpass ([\w.-]+)", line)) for line in checks if line.strip()]
                    self.assertTrue(all(n & passed for n in named), "a done check left has no PASS line")
                    self.assertLessEqual(passed, set().union(*named), "a PASS line outlived its done check")
                    # The summary line counts the hunks left, as git prints it.
                    diff = section(text, "## Diff")
                    summary = next(line for line in diff if re.match(r" \d+ files? changed", line))
                    files = ins = dels = 0
                    in_hunk = False
                    for line in diff:
                        if line.startswith("diff --git "):
                            files, in_hunk = files + 1, False
                        elif line.startswith("@@ "):
                            in_hunk = True
                        elif in_hunk:
                            ins, dels = ins + line.startswith("+"), dels + line.startswith("-")
                    self.assertEqual([int(n) for n in re.findall(r"\d+", summary)], [n for n in (files, ins, dels) if n])

    def test_listed_bases_yield_no_mutant_of_their_class(self) -> None:
        """A base on a skip list would plant a state the supervisor stops, or a label a careful judge contradicts."""
        spec = importlib.util.spec_from_file_location("mutate", MUTATE)
        mutate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mutate)
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "out"
            subprocess.run([sys.executable, str(MUTATE), str(ROOT / "evals/clean"), str(out)],
                           check=True, capture_output=True)
            for cls, bases in (("logic-bug", mutate.LOGIC_BUG_TRIPS), ("vacuous-check", mutate.CLOSED_SCOPE),
                               ("out-of-scope", mutate.CLOSED_SCOPE)):
                for base in bases:
                    with self.subTest(cls=cls, base=base):
                        self.assertTrue((ROOT / "evals/clean/judge" / base).is_dir(), "the list names no clean base")
                        self.assertEqual(sorted(out.glob(f"*/{base}--{cls}")), [])


if __name__ == "__main__":
    unittest.main()
