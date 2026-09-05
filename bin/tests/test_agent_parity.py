"""Tests for bin/agent_parity/parity.py, the Claude/Codex parity BOM gate.

The tool is a script, not an importable package, so each case runs it as a
subprocess. The drift cases build a fully-classified copy of the seed (the live
seed plus any hook files the manifest declares but that have not landed yet) so
the injected drift is the sole reported error.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PARITY = ROOT / "bin/agent_parity/parity.py"
SEED = ROOT / "seed"


def _run(target: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PARITY), "check", "--root", str(target)],
        capture_output=True,
        text=True,
        check=False,
    )


def _declared_hook_files(seed: pathlib.Path) -> list[str]:
    data = tomllib.loads((seed / "agent-parity.toml").read_text(encoding="utf-8"))
    return [
        path
        for path in data["hooks"]["unsupported"]
        if path.startswith(".claude/hooks/")
    ]


class AgentParityTests(unittest.TestCase):
    def _clean_base(self) -> pathlib.Path:
        """A seed copy where every manifest-declared hook file exists."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        base = pathlib.Path(tmp) / "seed"
        shutil.copytree(SEED, base, symlinks=True)
        for relative in _declared_hook_files(base):
            path = base / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        return base

    def test_real_seed_check_passes(self) -> None:
        # The live seed must be fully classified. This is red only while a
        # manifest-declared hook file has not yet landed on disk.
        result = _run(SEED)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("parity check passed", result.stdout)

    def test_clean_base_passes(self) -> None:
        result = _run(self._clean_base())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("parity check passed", result.stdout)

    def test_unclassified_hook_fails(self) -> None:
        base = self._clean_base()
        (base / ".claude/hooks/x-unlisted.sh").write_text(
            "#!/usr/bin/env bash\n", encoding="utf-8"
        )
        result = _run(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("unclassified", result.stderr)

    def test_missing_shared_symlink_fails(self) -> None:
        base = self._clean_base()
        (base / ".claude/skills/catchup").unlink()
        result = _run(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("is not a symlink", result.stderr)


if __name__ == "__main__":
    unittest.main()
