"""bin/rules_enforcers.py on temp repos: the done-checks' renamed step label, renamed test function
and removed test file, plus the column, suffix and table rules. The real tree resolves everything, so
only these cases keep each failure branch from silently matching nothing."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/rules_enforcers.py"
CHECK = 'step "plugin versions"\nstep "pytest"\n'
TESTS = "class T:\n    def test_kept(self) -> None:\n        pass\n"


def rules(*enforcers: str, home: str = "`bin/check`") -> str:
    rows = "".join(f"| a rule | {home} | {e} |\n" for e in enforcers)
    return f"# Rules\n\n| Rule | Home | Enforcer |\n|------|------|----------|\n{rows}"


def run(doc: str, check: str = CHECK, files: dict[str, str] | None = None,
        deleted: tuple[str, ...] = (), untracked: dict[str, str] | None = None) -> tuple[int, str]:
    """Plant docs/RULES.md, bin/check and `files`, git add them, delete `deleted` from disk, write
    `untracked` without adding it, and run the script."""
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        planted = {"docs/RULES.md": doc, "bin/check": check, "bin/tests/test_a.py": TESTS, **(files or {})}
        for rel, text in planted.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        for rel in deleted:
            (root / rel).unlink()
        for rel, text in (untracked or {}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        p = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
        return p.returncode, p.stdout


class RulesEnforcersTest(unittest.TestCase):
    def test_passes_when_every_enforcer_resolves(self) -> None:
        rc, out = run(rules(
            'check: `bin/check` step "plugin versions"',
            'check: `bin/tests/test_a.py` in `bin/check` step "pytest"',
            "`bin/tests/test_a.py` `test_kept`",
            "check: `bin/check lint x` refuses; the paragraph at `bin/tests/test_a.py:1,2`",
        ))
        self.assertEqual((rc, out), (0, ""))

    def test_flags_renamed_step_label(self) -> None:
        rc, out = run(rules('check: `bin/check` step "plugin versions"'), check='step "plugin version rule"\n')
        self.assertEqual(rc, 1)
        self.assertEqual(out, 'FAIL: docs/RULES.md:5: bin/check has no step "plugin versions"\n')

    def test_label_must_match_the_whole_step_line(self) -> None:
        rc, out = run(rules('check: `bin/check` step "plugin"'))
        self.assertEqual(rc, 1)
        self.assertIn('no step "plugin"', out)

    def test_flags_renamed_test_function_and_removed_file(self) -> None:
        rc, out = run(rules("`bin/tests/test_a.py` `test_gone`", "`bin/tests/test_b.py` `test_x`"),
                      files={"bin/tests/test_b.py": "def test_x() -> None:\n    pass\n"},
                      deleted=("bin/tests/test_b.py",))
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: docs/RULES.md:5: bin/tests/test_a.py has no def test_gone",
            "FAIL: docs/RULES.md:6: bin/tests/test_b.py is missing on disk or not tracked by git",
        ])

    def test_flags_untracked_path(self) -> None:
        rc, out = run(rules("`bin/missing.py`", "`bin/loose.py`"), untracked={"bin/loose.py": ""})
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: docs/RULES.md:5: bin/missing.py is missing on disk or not tracked by git",
            "FAIL: docs/RULES.md:6: bin/loose.py is missing on disk or not tracked by git",
        ])

    def test_flags_every_path_in_a_cell(self) -> None:
        rc, out = run(rules("`bin/tests/test_a.py` then `bin/gone.py` and `bin/lost.py`"))
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: docs/RULES.md:5: bin/gone.py is missing on disk or not tracked by git",
            "FAIL: docs/RULES.md:5: bin/lost.py is missing on disk or not tracked by git",
        ])

    def test_mid_line_step_text_is_not_a_step(self) -> None:
        rc, out = run(rules('check: `bin/check` step "plugin versions"'),
                      check='echo \'step "plugin versions"\'\nstep "pytest"\n')
        self.assertEqual((rc, out), (1, 'FAIL: docs/RULES.md:5: bin/check has no step "plugin versions"\n'))

    def test_fails_when_no_enforcer_cell_is_found(self) -> None:
        for header in ("Enforced by", "enforcer", "**Enforcer**"):
            with self.subTest(header=header):
                rc, out = run(rules("`bin/gone.py`").replace("| Enforcer |", f"| {header} |"))
                self.assertEqual((rc, out), (1, "FAIL: docs/RULES.md: no table row has an Enforcer cell\n"))

    def test_separator_and_short_rows_are_not_enforcer_cells(self) -> None:
        for doc in (rules(), rules() + "| a rule | `bin/gone.py` |\n"):
            with self.subTest(doc=doc):
                self.assertEqual(run(doc), (1, "FAIL: docs/RULES.md: no table row has an Enforcer cell\n"))

    def test_reads_an_indented_table(self) -> None:
        doc = rules('check: `bin/check` step "plugin version rule"').replace("\n|", "\n  |")
        rc, out = run(doc)
        self.assertEqual((rc, out), (1, 'FAIL: docs/RULES.md:5: bin/check has no step "plugin version rule"\n'))

    def test_line_suffix_on_a_test_file_keeps_the_def_check(self) -> None:
        rc, out = run(rules("`bin/tests/test_a.py:3` `test_gone`"))
        self.assertEqual((rc, out), (1, "FAIL: docs/RULES.md:5: bin/tests/test_a.py has no def test_gone\n"))

    def test_def_must_be_real_code(self) -> None:
        text = 'X = """\ndef test_quoted():\n"""\n\nasync def test_async() -> None:\n    """\n    def test_doc\n    """\n'
        rc, out = run(rules("`bin/tests/test_b.py` `test_quoted`", "`bin/tests/test_b.py` `test_doc`",
                            "`bin/tests/test_b.py` `test_async`"), files={"bin/tests/test_b.py": text})
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: docs/RULES.md:5: bin/tests/test_b.py has no def test_quoted",
            "FAIL: docs/RULES.md:6: bin/tests/test_b.py has no def test_doc",
        ])

    def test_unparsable_test_file_fails_without_a_traceback(self) -> None:
        rc, out = run(rules("`bin/tests/test_b.py` `test_x`"), files={"bin/tests/test_b.py": "def test_x(:\n"})
        self.assertEqual((rc, out), (1, "FAIL: docs/RULES.md:5: bin/tests/test_b.py does not parse as Python\n"))

    def test_test_file_tracked_only_as_a_template(self) -> None:
        rc, out = run(rules("`bin/tests/test_j.py` `test_x`"), files={"bin/tests/test_j.py.jinja": "def test_x(): pass\n"})
        self.assertEqual((rc, out), (1, "FAIL: docs/RULES.md:5: bin/tests/test_j.py is not on disk to read def test_x\n"))

    def test_reads_only_the_enforcer_column_of_an_enforcer_table(self) -> None:
        doc = rules("prose (judgment)", home='`bin/gone.py`; `bin/check` step "gone"') + (
            "| `x \\| y` | `bin/gone.py` | prose |\n"
            "\n| Mistake | Evidence | Issue |\n|---|---|---|\n| `cmd \\| head` | a2ec7df | `bin/gone.sh` |\n")
        self.assertEqual(run(doc), (0, ""))


if __name__ == "__main__":
    unittest.main()
