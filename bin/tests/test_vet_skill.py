"""Threshold logic for bin/vet-skill.sh, with a mocked SkillSpector.

CI must stay deterministic and offline, so these tests put a fake
`skillspector` on PATH that emits a chosen severity, then assert the wrapper
maps it to the right verdict and exit code. No network, no real scan.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VET = ROOT / "bin/vet-skill.sh"


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
        report = {"risk_assessment": {"severity": "LOW", "score": 2}, "issues": []}
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
                  "issues": [{"title": "bad"}]}
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
