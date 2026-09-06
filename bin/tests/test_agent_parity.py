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
    return sorted(
        path
        for disposition in ("unimplemented_adapter", "unsupported")
        for path in data["hooks"][disposition]
        if path.startswith(".claude/hooks/")
    )


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

    def test_missing_hook_adapter_target_fails(self) -> None:
        base = self._clean_base()
        (base / ".claude/hooks/stop-verify-gate.sh").unlink()
        result = _run(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("hook adapter target is missing", result.stderr)

    def test_unimplemented_hook_adapter_is_not_reported_as_host_unsupported(self) -> None:
        data = tomllib.loads((SEED / "agent-parity.toml").read_text(encoding="utf-8"))
        unimplemented = data["hooks"]["unimplemented_adapter"]
        unsupported = data["hooks"]["unsupported"]
        adapters = data["hooks"]["native_adapter"]
        self.assertIn(".claude/hooks/bash-audit-log.sh", unimplemented)
        self.assertNotIn(".claude/hooks/bash-audit-log.sh", unsupported)
        self.assertEqual(
            adapters[".claude/hooks/stop-verify-gate.sh"],
            ".claude/hooks/stop-verify-gate.sh",
        )
        self.assertTrue(
            all(reason.startswith("Adapter missing:") for reason in unimplemented.values())
        )
        self.assertTrue(
            all(reason.startswith("Host gap:") for reason in unsupported.values())
        )

    def test_shared_validation_contract_is_declared(self) -> None:
        data = tomllib.loads((SEED / "agent-parity.toml").read_text(encoding="utf-8"))
        self.assertEqual(
            data["validation"],
            {
                "shared_module": ".agents/lib/validation.py",
                "commands": ["run", "check", "fingerprint", "pre-commit"],
            },
        )

    def test_missing_shared_validation_module_fails(self) -> None:
        base = self._clean_base()
        (base / ".agents/lib/validation.py").unlink()
        result = _run(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("shared validation module is missing", result.stderr)

    def test_missing_shared_validation_command_fails(self) -> None:
        base = self._clean_base()
        module = base / ".agents/lib/validation.py"
        source = module.read_text(encoding="utf-8")
        changed = source.replace(
            '("run", "check", "fingerprint", "pre-commit")',
            '("run", "check", "pre-commit")',
        )
        self.assertNotEqual(source, changed)
        module.write_text(changed, encoding="utf-8")
        result = _run(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("validation command missing: fingerprint", result.stderr)

    def test_active_guidance_uses_content_bound_validation_once(self) -> None:
        agents = (ROOT / "seed/AGENTS.md.jinja").read_text(encoding="utf-8")
        claude = (ROOT / "seed/CLAUDE.md.jinja").read_text(encoding="utf-8")
        validate = (
            ROOT / "cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md"
        ).read_text(encoding="utf-8")
        combined = "\n".join((agents, claude, validate))
        self.assertIn("validation.py check", combined)
        self.assertIn("content", combined.lower())
        self.assertNotIn("failing test lands in its own commit", agents)
        self.assertNotIn("preceded in the same turn", agents)
        self.assertNotIn("older than an edited file", claude)

    def test_shipping_stages_intended_inputs_before_validation(self) -> None:
        validate = (
            ROOT / "cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md"
        ).read_text(encoding="utf-8")
        ship = (
            ROOT / "cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("intended source changes are staged", validate)
        self.assertLess(ship.index("git add <paths>"), ship.index("Invoke `/validate`."))
        self.assertLess(ship.index("Invoke `/validate`."), ship.index("git commit"))

    def test_expensive_review_workflows_are_conditional_and_bounded(self) -> None:
        team = (
            ROOT / "cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md"
        ).read_text(encoding="utf-8")
        scenarios = (
            ROOT / "cultivation/marketplace/sam-cc-setup/skills/agent-team/scenarios.md"
        ).read_text(encoding="utf-8")
        teammate = (
            ROOT
            / "cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md"
        ).read_text(encoding="utf-8")
        critique = (
            ROOT
            / "cultivation/marketplace/sam-cc-setup/skills/session-critique/SKILL.md"
        ).read_text(encoding="utf-8")
        fanout = (
            ROOT
            / "cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js"
        ).read_text(encoding="utf-8")
        codex_plan = (
            ROOT
            / "cultivation/marketplace/sam-cc-setup/skills/codex-plan-review/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("one validation owner", team.lower())
        self.assertIn("fixed diff", critique.lower())
        self.assertIn("durable", critique.lower())
        self.assertNotIn("Every teammate runs Opus", team)
        self.assertLessEqual(fanout.count("prompt:"), 6)
        self.assertNotIn("2 skeptics each", fanout)
        self.assertNotIn("3 grounding thunks", fanout)
        self.assertNotIn("validation gate -> commit -> independent review", fanout)
        self.assertIn("Critic rows are conditional", scenarios)
        self.assertNotIn("Once the lead confirms", teammate)
        self.assertNotIn("same-model reviewer", codex_plan)
        self.assertNotIn("cross-model", codex_plan.lower())
        self.assertIn("fresh context", codex_plan.lower())


if __name__ == "__main__":
    unittest.main()
