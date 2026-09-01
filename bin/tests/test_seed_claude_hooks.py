"""Behavioral fixtures for the four shipped Claude hooks (evaluation E1).

Each test runs the real hook script against a disposable git repository and
asserts on exit code and output. Every gate gets a RED fixture (must block),
a GREEN fixture (must pass), and the negative controls from the evaluation
design: nonmatching input, malformed JSON, and the loop guard.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

HOOKS_DIR = pathlib.Path(__file__).resolve().parents[2] / "seed/.claude/hooks"


class HookFixtureCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.repo = pathlib.Path(self.temp_dir.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@test")
        self.git("config", "user.name", "Fixture")
        (self.repo / ".claude").mkdir()

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True
        )

    def commit_file(self, name: str, content: str) -> None:
        (self.repo / name).write_text(content, encoding="utf-8")
        self.git("add", name)
        self.git("commit", "-q", "-m", f"add {name}")

    def run_hook(
        self,
        script: str,
        payload: object,
        raw_payload: str | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        stdin = raw_payload if raw_payload is not None else json.dumps(payload)
        return subprocess.run(
            ["bash", str(HOOKS_DIR / script)],
            cwd=self.repo,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
            env=env,
        )


class StopVerifyGateTests(HookFixtureCase):
    SCRIPT = "stop-verify-gate.sh"

    def test_clean_tree_passes(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        result = self.run_hook(self.SCRIPT, {})
        self.assertEqual(0, result.returncode, result.stderr)

    def test_changed_python_with_ruff_error_blocks_then_fix_passes(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        bad = self.repo / "bad.py"
        bad.write_text("import os\n", encoding="utf-8")

        red = self.run_hook(self.SCRIPT, {})
        self.assertEqual(2, red.returncode, red.stderr)
        self.assertIn("verification gate FAILED", red.stderr)
        self.assertIn("[ruff check]", red.stderr)

        bad.write_text("import os\nprint(os.sep)\n", encoding="utf-8")
        green = self.run_hook(self.SCRIPT, {})
        self.assertEqual(0, green.returncode, green.stderr)

    def test_changed_shell_syntax_error_blocks(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "bad.sh").write_text("if [ 1 ]; then\n", encoding="utf-8")

        result = self.run_hook(self.SCRIPT, {})
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("[bash -n]", result.stderr)

    def test_trailing_whitespace_in_tracked_change_blocks(self) -> None:
        self.commit_file("notes.txt", "clean\n")
        (self.repo / "notes.txt").write_text("trailing \n", encoding="utf-8")

        result = self.run_hook(self.SCRIPT, {})
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("[git diff --check]", result.stderr)

    def test_loop_guard_passes_even_with_failing_files(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "bad.py").write_text("import os\n", encoding="utf-8")

        result = self.run_hook(self.SCRIPT, {"stop_hook_active": True})
        self.assertEqual(0, result.returncode, result.stderr)

    def test_malformed_json_payload_is_not_a_bypass(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "bad.py").write_text("import os\n", encoding="utf-8")

        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(2, result.returncode, result.stderr)

    def test_missing_ruff_notes_and_does_not_block(self) -> None:
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "clean.py").write_text("print('fine')\n", encoding="utf-8")

        shim_dir = pathlib.Path(self.temp_dir.name) / "shim"
        shim_dir.mkdir()
        shim = shim_dir / "python3"
        real_python = subprocess.run(
            ["bash", "-lc", "command -v python3"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        shim.write_text(
            "#!/bin/bash\n"
            'if [ "$1" = "-m" ] && [ "$2" = "ruff" ]; then exit 1; fi\n'
            f'exec "{real_python}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)

        env = dict(os.environ)
        env["PATH"] = f"{shim_dir}:{env['PATH']}"
        result = self.run_hook(self.SCRIPT, {}, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("ruff unavailable", result.stderr)

    def test_outside_git_repo_passes(self) -> None:
        outside = pathlib.Path(self.temp_dir.name) / "plain"
        outside.mkdir()
        result = subprocess.run(
            ["bash", str(HOOKS_DIR / self.SCRIPT)],
            cwd=outside,
            input="{}",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
            env={**os.environ, "GIT_CEILING_DIRECTORIES": self.temp_dir.name},
        )
        self.assertEqual(0, result.returncode, result.stderr)


class RuffAfterEditTests(HookFixtureCase):
    SCRIPT = "ruff-after-edit.sh"

    def test_fixes_edited_python_file(self) -> None:
        target = self.repo / "edited.py"
        target.write_text("import os\nprint('x')\n", encoding="utf-8")

        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("import os", target.read_text(encoding="utf-8"))

    def test_nonmatching_path_is_untouched(self) -> None:
        target = self.repo / "notes.md"
        target.write_text("import os\n", encoding="utf-8")

        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("import os\n", target.read_text(encoding="utf-8"))

    def test_malformed_json_is_graceful(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)


class BashAuditLogTests(HookFixtureCase):
    SCRIPT = "bash-audit-log.sh"

    def test_logs_command_with_timestamp(self) -> None:
        payload = {"tool_input": {"command": "echo fixture-run"}}
        result = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        log = (self.repo / ".claude/audit.log").read_text(encoding="utf-8")
        self.assertIn("| echo fixture-run", log)

    def test_malformed_json_logs_unparseable_and_passes(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)
        log = (self.repo / ".claude/audit.log").read_text(encoding="utf-8")
        self.assertIn("| unparseable", log)


class ConcurrentCheckoutGuardTests(HookFixtureCase):
    SCRIPT = "concurrent-checkout-guard.sh"

    def lock_path(self) -> pathlib.Path:
        git_dir = subprocess.run(
            ["git", "rev-parse", "--absolute-git-dir"],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return pathlib.Path(git_dir) / "index.lock"

    def test_fresh_lock_blocks_index_writing_git_command(self) -> None:
        self.lock_path().touch()
        result = self.run_hook(
            self.SCRIPT,
            {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}},
        )
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("BLOCKED", result.stderr)

    def test_stale_lock_allows_with_cleanup_advice(self) -> None:
        lock = self.lock_path()
        lock.touch()
        stale = os.stat(lock).st_mtime - 120
        os.utime(lock, (stale, stale))

        result = self.run_hook(
            self.SCRIPT,
            {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}},
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("stale git index.lock", result.stderr)

    def test_read_only_git_command_passes_under_fresh_lock(self) -> None:
        self.lock_path().touch()
        result = self.run_hook(
            self.SCRIPT,
            {"tool_name": "Bash", "tool_input": {"command": "git status"}},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_non_git_command_passes_under_fresh_lock(self) -> None:
        self.lock_path().touch()
        result = self.run_hook(
            self.SCRIPT,
            {"tool_name": "Bash", "tool_input": {"command": "ls -la"}},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_edit_tool_blocks_under_fresh_lock(self) -> None:
        self.lock_path().touch()
        result = self.run_hook(
            self.SCRIPT,
            {"tool_name": "Edit", "tool_input": {"file_path": "x.py"}},
        )
        self.assertEqual(2, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
