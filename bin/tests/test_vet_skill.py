"""Threshold logic for bin/vet-skill.sh, with a mocked SkillSpector.

CI must stay deterministic and offline, so these tests put a fake
`skillspector` on PATH that emits a chosen severity, then assert the wrapper
maps it to the right verdict and exit code. No network, no real scan.
"""

from __future__ import annotations

import copy
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VET = ROOT / "bin/vet-skill.sh"
# Real SkillSpector 2.9.1 reports from `skillspector scan --recursive --no-llm`,
# trimmed: skill.source made relative, per-analyzer status lists dropped.
FIXTURES = ROOT / "bin/tests/fixtures/vet-skill"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text("utf-8"))


class VetSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        # A dummy target directory to scan.
        self.target = self.root / "skill"
        self.target.mkdir()
        (self.target / "SKILL.md").write_text("---\nname: x\n---\n", "utf-8")

    def run_vet(
        self,
        *,
        severity: str | None,
        score: int = 0,
        with_scanner: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        fake_bin = self.root / "bin"
        fake_bin.mkdir(exist_ok=True)
        if with_scanner:
            report = {
                "risk_assessment": {
                    "severity": severity,
                    "score": score,
                    "recommendation": "TEST",
                },
                "issues": [{"title": "planted"}] if severity not in ("NONE", "LOW") else [],
                "execution_successful": True,
            }
            script = (
                "#!/usr/bin/env bash\n"
                'out=""\n'
                'while [ $# -gt 0 ]; do\n'
                '  if [ "$1" = "--output" ]; then out="$2"; shift; fi\n'
                "  shift\n"
                "done\n"
                f"cat > \"$out\" <<'JSON'\n{json.dumps(report)}\nJSON\n"
                "exit 0\n"
            )
            (fake_bin / "skillspector").write_text(script, "utf-8")
            (fake_bin / "skillspector").chmod(0o755)
        env = dict(os.environ)
        # Keep git/python/etc, but force our fake skillspector to win.
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        return subprocess.run(
            ["bash", str(VET), str(self.target), "--json"],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
            check=False,
        )

    def run_report(
        self, report: dict | list, *args: str
    ) -> subprocess.CompletedProcess[str]:
        """Run the wrapper with a fake scanner that writes `report` verbatim."""
        fake_bin = self.root / "bin"
        fake_bin.mkdir(exist_ok=True)
        saved = self.root / "report.json"
        saved.write_text(json.dumps(report), "utf-8")
        (fake_bin / "skillspector").write_text(
            "#!/usr/bin/env bash\n"
            'out=""\n'
            'while [ $# -gt 0 ]; do if [ "$1" = "--output" ]; then out="$2"; shift; fi; shift; done\n'
            f'cp "{saved}" "$out"\n',
            "utf-8",
        )
        (fake_bin / "skillspector").chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        return subprocess.run(
            ["bash", str(VET), str(self.target), *(args or ("--json",))],
            capture_output=True, text=True, env=env, timeout=60, check=False,
        )

    def test_real_single_skill_report(self) -> None:
        r = self.run_report(load_fixture("single-catchup.json"))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn('"verdict":"PASS","severity":"LOW","score":8,"top_issues":"RP1"', r.stdout)

    def test_real_multi_skill_report_reads_every_skill(self) -> None:
        # A recursive scan of several skills nests them under "skills".
        r = self.run_report(load_fixture("multi-seed-skills.json"))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn('"verdict":"PASS","severity":"LOW","score":8,"top_issues":"RP1"', r.stdout)

    def test_missing_or_unknown_severity_fails_closed(self) -> None:
        single = load_fixture("single-catchup.json")
        no_severity = copy.deepcopy(single)
        del no_severity["risk_assessment"]["severity"]
        no_assessment = copy.deepcopy(single)
        del no_assessment["risk_assessment"]
        unknown = copy.deepcopy(single)
        unknown["risk_assessment"]["severity"] = "SEVERE"
        multi = load_fixture("multi-seed-skills.json")
        del multi["skills"][1]["risk_assessment"]["severity"]
        cases = {
            "no severity": (no_severity, "catchup"),
            "no risk_assessment": (no_assessment, "catchup"),
            "unknown severity": (unknown, "catchup"),
            "one of three skills lacks severity": (multi, "fable-prompting"),
        }
        for label, (report, skill) in cases.items():
            with self.subTest(label):
                r = self.run_report(report)
                self.assertEqual(4, r.returncode, r.stdout + r.stderr)
                self.assertIn("risk_assessment.severity", r.stderr)
                self.assertIn(skill, r.stderr)
                self.assertNotIn('"verdict"', r.stdout)

    def test_failed_scan_fails_closed(self) -> None:
        # Real report for a skill with an unreadable file: SkillSpector rates
        # it LOW but sets execution_successful false. No verdict, no --out tree.
        report = load_fixture("failed-unreadable-file.json")
        r = self.run_report(report)
        self.assertEqual(4, r.returncode, r.stdout + r.stderr)
        self.assertIn("execution_successful", r.stderr)
        out = self.root / "stripped"
        r = self.run_report(report, "--safe", "--out", str(out))
        self.assertEqual(4, r.returncode, r.stdout + r.stderr)
        self.assertFalse(out.exists(), "a failed scan must not emit an installable tree")

    def test_missing_execution_successful_fails_closed(self) -> None:
        # Only an explicit true counts as a finished scan; a missing key does not.
        single = load_fixture("single-catchup.json")
        del single["execution_successful"]
        multi_top = load_fixture("multi-seed-skills.json")
        del multi_top["execution_successful"]
        multi_one = load_fixture("multi-seed-skills.json")
        del multi_one["skills"][1]["execution_successful"]
        cases = {
            "single report": (single, "catchup"),
            "multi report, top level": (multi_top, "multi-skill scan"),
            "multi report, one of three skills": (multi_one, "fable-prompting"),
        }
        for label, (report, where) in cases.items():
            with self.subTest(label):
                r = self.run_report(report)
                self.assertEqual(4, r.returncode, r.stdout + r.stderr)
                self.assertIn("execution_successful", r.stderr)
                self.assertIn(where, r.stderr)
                self.assertNotIn('"verdict"', r.stdout)

    def test_empty_report_fails_closed(self) -> None:
        # A report that lists no skills gives no verdict and no --out tree.
        out = self.root / "stripped"
        cases = {
            "empty list": [],
            "multi report with no skills":
                {"multi_skill": True, "execution_successful": True, "skills": []},
        }
        for label, report in cases.items():
            with self.subTest(label):
                r = self.run_report(report, "--json", "--safe", "--out", str(out))
                self.assertEqual(4, r.returncode, r.stdout + r.stderr)
                self.assertIn("lists no skills", r.stderr)
                self.assertNotIn('"verdict"', r.stdout)
                self.assertFalse(out.exists(), "an empty report must not emit an installable tree")

    def test_no_skill_found_fails_closed(self) -> None:
        # Real report for an empty directory: SkillSpector rates it LOW, but
        # total_components is 0, so nothing was scanned and there is no verdict.
        out = self.root / "stripped"
        r = self.run_report(load_fixture("empty-dir.json"), "--json", "--safe", "--out", str(out))
        self.assertEqual(4, r.returncode, r.stdout + r.stderr)
        self.assertIn("no skill found to scan", r.stderr)
        self.assertNotIn('"verdict"', r.stdout)
        self.assertFalse(out.exists(), "an empty scan must not emit an installable tree")

    def test_nested_critical_skill_rejects(self) -> None:
        # The worst skill wins wherever it sits. CRITICAL goes in the middle
        # record, so a verdict read from only the first or last skill fails.
        multi = load_fixture("multi-seed-skills.json")
        multi["skills"][1]["risk_assessment"].update(severity="CRITICAL", score=95)
        r = self.run_report(multi)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn('"verdict":"REJECT","severity":"CRITICAL","score":95', r.stdout)

    def test_low_passes(self) -> None:
        r = self.run_vet(severity="LOW")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn('"verdict":"PASS"', r.stdout)

    def test_none_passes(self) -> None:
        r = self.run_vet(severity="NONE")
        self.assertEqual(0, r.returncode, r.stderr)

    def test_medium_needs_review(self) -> None:
        r = self.run_vet(severity="MEDIUM", score=37)
        self.assertEqual(1, r.returncode)
        self.assertIn('"verdict":"REVIEW"', r.stdout)

    def test_high_rejects(self) -> None:
        r = self.run_vet(severity="HIGH", score=80)
        self.assertEqual(2, r.returncode)
        self.assertIn('"verdict":"REJECT"', r.stdout)

    def test_critical_rejects(self) -> None:
        r = self.run_vet(severity="CRITICAL", score=95)
        self.assertEqual(2, r.returncode)

    def test_safe_mode_strips_scripts_before_install(self) -> None:
        # A skill with a script and a doc; --safe must drop the script and,
        # with --out, emit a stripped tree containing only the doc.
        (self.target / "run.py").write_text("import os\n", "utf-8")
        (self.target / "guide.md").write_text("# guide\n", "utf-8")
        (self.target / "Makefile").write_text("all:\n\trm -rf x\n", "utf-8")
        out = self.root / "stripped"
        fake_bin = self.root / "bin"
        fake_bin.mkdir(exist_ok=True)
        report = {"risk_assessment": {"severity": "LOW", "score": 2}, "issues": [],
                  "execution_successful": True}
        (fake_bin / "skillspector").write_text(
            "#!/usr/bin/env bash\n"
            'out=""\n'
            'while [ $# -gt 0 ]; do if [ "$1" = "--output" ]; then out="$2"; shift; fi; shift; done\n'
            f"cat > \"$out\" <<'JSON'\n{json.dumps(report)}\nJSON\nexit 0\n",
            "utf-8",
        )
        (fake_bin / "skillspector").chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        r = subprocess.run(
            ["bash", str(VET), str(self.target), "--safe", "--out", str(out), "--json"],
            capture_output=True, text=True, env=env, timeout=60, check=False,
        )
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn('"safe":1', r.stdout)
        self.assertTrue((out / "SKILL.md").exists())
        self.assertTrue((out / "guide.md").exists())
        self.assertFalse((out / "run.py").exists(), "script must be stripped")
        self.assertFalse((out / "Makefile").exists(), "Makefile must be stripped")

    def test_safe_reject_does_not_emit_out(self) -> None:
        # A REJECT verdict must not hand the caller an installable tree.
        (self.target / "run.py").write_text("import os\n", "utf-8")
        out = self.root / "stripped2"
        fake_bin = self.root / "bin"
        fake_bin.mkdir(exist_ok=True)
        report = {"risk_assessment": {"severity": "CRITICAL", "score": 100},
                  "issues": [{"title": "bad"}], "execution_successful": True}
        (fake_bin / "skillspector").write_text(
            "#!/usr/bin/env bash\n"
            'out=""\n'
            'while [ $# -gt 0 ]; do if [ "$1" = "--output" ]; then out="$2"; shift; fi; shift; done\n'
            f"cat > \"$out\" <<'JSON'\n{json.dumps(report)}\nJSON\nexit 0\n",
            "utf-8",
        )
        (fake_bin / "skillspector").chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        r = subprocess.run(
            ["bash", str(VET), str(self.target), "--safe", "--out", str(out)],
            capture_output=True, text=True, env=env, timeout=60, check=False,
        )
        self.assertEqual(2, r.returncode)
        self.assertFalse(out.exists(), "REJECT must not emit an installable tree")

    def test_safe_out_refuses_to_clobber_nonempty_dir(self) -> None:
        # Regression (harness audit, 2026-09-01): `--out <populated dir>` must
        # not wipe it. The guard refuses and leaves the pre-existing file.
        (self.target / "guide.md").write_text("# guide\n", "utf-8")
        out = self.root / "precious"
        out.mkdir()
        keep = out / "do-not-delete.txt"
        keep.write_text("important\n", "utf-8")
        fake_bin = self.root / "bin"
        fake_bin.mkdir(exist_ok=True)
        report = {"risk_assessment": {"severity": "LOW", "score": 2}, "issues": [],
                  "execution_successful": True}
        (fake_bin / "skillspector").write_text(
            "#!/usr/bin/env bash\n"
            'out=""\n'
            'while [ $# -gt 0 ]; do if [ "$1" = "--output" ]; then out="$2"; shift; fi; shift; done\n'
            f"cat > \"$out\" <<'JSON'\n{json.dumps(report)}\nJSON\nexit 0\n",
            "utf-8",
        )
        (fake_bin / "skillspector").chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        r = subprocess.run(
            ["bash", str(VET), str(self.target), "--safe", "--out", str(out)],
            capture_output=True, text=True, env=env, timeout=60, check=False,
        )
        self.assertEqual(4, r.returncode, r.stderr)
        self.assertTrue(keep.exists(), "the guard must not delete existing contents")
        self.assertEqual("important\n", keep.read_text())

    def test_missing_scanner_is_exit_3(self) -> None:
        # PATH with only the fake bin (empty) plus coreutils, no skillspector.
        fake_bin = self.root / "empty-bin"
        fake_bin.mkdir()
        env = dict(os.environ)
        # Rebuild PATH so skillspector cannot be found but bash/git/python can.
        keep = [p for p in env["PATH"].split(":") if p and "skillspector" not in p]
        env["PATH"] = str(fake_bin) + ":" + ":".join(keep)
        # Shadow skillspector with nothing: use a PATH that lacks it entirely is
        # hard on a dev machine, so instead point HOME-installed one away by
        # overriding command resolution via a stub dir that has everything but.
        r = subprocess.run(
            ["bash", "-c", f'PATH="{fake_bin}:/usr/bin:/bin" bash {VET} {self.target}'],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(3, r.returncode, r.stdout + r.stderr)
        self.assertIn("SkillSpector not found", r.stderr)


if __name__ == "__main__":
    unittest.main()
