"""Behavioral fixtures for the shipped Claude hooks (evaluation E1).

Each test runs the real hook script against a disposable git repository and
asserts on exit code and output. Every gate gets a RED fixture (must block),
a GREEN fixture (must pass), and the negative controls from the evaluation
design: nonmatching input, malformed JSON, and the loop guard.
"""

from __future__ import annotations

import hashlib
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

        # The fixed version must be clean under any ruff default rule set
        # (older ruff flags only F401 here; newer ruff also flags I001 import
        # sorting), so drop the import entirely rather than "using" it.
        bad.write_text('print("ok")\n', encoding="utf-8")
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

    def _ruffless_path(self) -> pathlib.Path:
        """Build a PATH dir with the tools the hook needs, a python3 shim whose
        `-m ruff` fails, and no `ruff` binary anywhere on the PATH."""
        shim_dir = pathlib.Path(self.temp_dir.name) / "shim"
        shim_dir.mkdir(exist_ok=True)
        real_python = subprocess.run(
            ["bash", "-lc", "command -v python3"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        shim = shim_dir / "python3"
        shim.write_text(
            "#!/bin/bash\n"
            'if [ "$1" = "-m" ] && [ "$2" = "ruff" ]; then echo "No module named ruff" >&2; exit 1; fi\n'
            f'exec "{real_python}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)
        for tool in ("bash", "git", "cat", "grep", "xargs"):
            real = subprocess.run(
                ["bash", "-lc", f"command -v {tool}"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            link = shim_dir / tool
            if not link.exists():
                link.symlink_to(real)
        return shim_dir

    def test_missing_ruff_notes_and_does_not_block(self) -> None:
        # Neither `python3 -m ruff` nor a PATH `ruff` binary exists: the gate
        # must note the skipped leg and pass, not block or silently no-op.
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "clean.py").write_text("print('fine')\n", encoding="utf-8")

        shim_dir = self._ruffless_path()
        env = dict(os.environ)
        env["PATH"] = str(shim_dir)
        result = self.run_hook(self.SCRIPT, {}, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("ruff unavailable", result.stderr)

    def test_path_ruff_binary_is_used_when_module_is_missing(self) -> None:
        # Regression (harness audit, 2026-09-01): uv/brew installs ship ruff
        # as a PATH binary only. The gate previously probed `python3 -m ruff`,
        # printed a NOTE, and silently skipped linting on such machines.
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "bad.py").write_text("import os\n", encoding="utf-8")

        shim_dir = self._ruffless_path()
        fake_ruff = shim_dir / "ruff"
        fake_ruff.write_text(
            "#!/bin/bash\n"
            'echo "bad.py:1:1: F401 unused import"\n'
            "exit 1\n",
            encoding="utf-8",
        )
        fake_ruff.chmod(0o755)

        env = dict(os.environ)
        env["PATH"] = str(shim_dir)
        result = self.run_hook(self.SCRIPT, {}, env=env)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("[ruff check]", result.stderr)
        self.assertNotIn("ruff unavailable", result.stderr)

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

    def test_repo_with_no_commits_is_gated_against_empty_tree(self) -> None:
        # setUp runs `git init` but never commits, so the repo has no HEAD.
        # The gate diffs against git's empty tree: a clean file passes, a
        # broken one still blocks, and git's own "ambiguous HEAD" error never
        # leaks into the findings.
        (self.repo / "fine.sh").write_text("echo ok\n", encoding="utf-8")
        passed = self.run_hook(self.SCRIPT, {})
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertNotIn("ambiguous", passed.stderr)

        (self.repo / "bad.sh").write_text("if [ 1 ]; then\n", encoding="utf-8")
        blocked = self.run_hook(self.SCRIPT, {})
        self.assertEqual(2, blocked.returncode, blocked.stderr)
        self.assertIn("[bash -n]", blocked.stderr)
        self.assertNotIn("ambiguous", blocked.stderr)

    def test_bash_mutated_file_counts_as_session_edit(self) -> None:
        # The transcript has no Edit for b.sh, only a Bash command naming it.
        # A file written through the shell must still be gated.
        self.commit_file("ok.py", "print('ok')\n")
        b = self.repo / "b.sh"
        b.write_text("if [ 1 ]; then\n", encoding="utf-8")
        transcript = pathlib.Path(self.temp_dir.name) / "bash.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Bash",
                                "input": {"command": "printf 'x' > b.sh"},
                            }
                        ]
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        result = self.run_hook(self.SCRIPT, {"transcript_path": str(transcript)})
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("[bash -n]", result.stderr)

    def test_whitespace_error_in_untouched_file_does_not_block(self) -> None:
        # git diff --check is scoped to the session's files, so trailing
        # whitespace in an untouched dirty file is not this session's problem.
        self.commit_file("other.txt", "clean\n")
        self.commit_file("mine.sh", "echo ok\n")
        (self.repo / "other.txt").write_text("trailing \n", encoding="utf-8")
        mine = self.repo / "mine.sh"
        mine.write_text("echo still ok\n", encoding="utf-8")
        transcript = self._transcript_editing(mine)
        result = self.run_hook(self.SCRIPT, {"transcript_path": str(transcript)})
        self.assertEqual(0, result.returncode, result.stderr)

    def _transcript_editing(self, *paths: pathlib.Path) -> pathlib.Path:
        """Write a JSONL transcript recording an Edit tool_use for each path."""
        transcript = pathlib.Path(self.temp_dir.name) / "session.jsonl"
        lines = [
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Edit",
                                "input": {"file_path": str(p)},
                            }
                        ]
                    },
                }
            )
            for p in paths
        ]
        transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return transcript

    def test_transcript_scopes_gate_to_session_edited_files(self) -> None:
        # The transcript records an edit to a.sh only. A syntax error in the
        # untouched-but-dirty b.sh must not block; one in a.sh must.
        # bash -n keeps this deterministic without depending on ruff.
        self.commit_file("ok.py", "print('ok')\n")
        a = self.repo / "a.sh"
        b = self.repo / "b.sh"
        transcript = self._transcript_editing(a)
        payload = {"transcript_path": str(transcript)}

        a.write_text("echo ok\n", encoding="utf-8")
        b.write_text("if [ 1 ]; then\n", encoding="utf-8")
        passed = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, passed.returncode, passed.stderr)

        a.write_text("if [ 1 ]; then\n", encoding="utf-8")
        blocked = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(2, blocked.returncode, blocked.stderr)
        self.assertIn("[bash -n]", blocked.stderr)

    def _claim_transcript(self, entries: list[tuple[str, object]]) -> pathlib.Path:
        """Write a JSONL transcript from (role, content) tuples, where content
        is the message content verbatim: a string for a human turn, or a list
        of blocks (tool_use / tool_result / text) otherwise."""
        transcript = pathlib.Path(self.temp_dir.name) / "claim.jsonl"
        lines = [
            json.dumps({"type": role, "message": {"content": content}})
            for role, content in entries
        ]
        transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return transcript

    def test_claim_with_same_turn_bash_result_passes(self) -> None:
        # A verification claim backed by a Bash tool_result ("3 passed") in the
        # same turn is honored: exit 0.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "run the tests"),
                (
                    "assistant",
                    [{"type": "tool_use", "id": "t1", "name": "Bash",
                      "input": {"command": "pytest"}}],
                ),
                (
                    "user",
                    [{"type": "tool_result", "tool_use_id": "t1",
                      "content": "3 passed"}],
                ),
                ("assistant", [{"type": "text", "text": "All tests pass."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "All tests pass."},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_claim_without_bash_result_blocks(self) -> None:
        # A verification claim with no Bash output in the turn blocks with the
        # exact gate sentence.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "run the tests"),
                ("assistant", [{"type": "text", "text": "All tests pass."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "All tests pass."},
        )
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(
            "Final message claims verification without command output in this turn.",
            result.stderr,
        )

    def test_claim_backed_only_before_last_human_message_blocks(self) -> None:
        # The only passing tool_result sits before the last human message, so it
        # is not this turn's evidence: the claim still blocks.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                (
                    "assistant",
                    [{"type": "tool_use", "id": "t1", "name": "Bash",
                      "input": {"command": "pytest"}}],
                ),
                (
                    "user",
                    [{"type": "tool_result", "tool_use_id": "t1",
                      "content": "3 passed"}],
                ),
                ("user", "now summarize"),
                ("assistant", [{"type": "text", "text": "All tests pass."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "All tests pass."},
        )
        self.assertEqual(2, result.returncode, result.stderr)

    def test_claim_with_not_verified_disclaimer_passes(self) -> None:
        # "not verified" anywhere in the message skips the claim leg: exit 0.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "run the tests"),
                ("assistant",
                 [{"type": "text", "text": "Tests pass; not verified."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "Tests pass; not verified."},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_claim_without_transcript_path_passes(self) -> None:
        # No transcript_path: the claim leg cannot read the turn, so it skips
        # rather than blocking. Clean tree keeps the other legs quiet.
        self.commit_file("ok.py", "print('ok')\n")
        result = self.run_hook(
            self.SCRIPT, {"last_assistant_message": "All tests pass."}
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_claim_with_list_tool_result_text_passes(self) -> None:
        # A tool_result whose content is a list of text items ("everything OK")
        # is read like a string result: the "OK" token backs the claim.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "run the tests"),
                (
                    "assistant",
                    [{"type": "tool_use", "id": "t1", "name": "Bash",
                      "input": {"command": "pytest"}}],
                ),
                (
                    "user",
                    [{"type": "tool_result", "tool_use_id": "t1",
                      "content": [{"type": "text", "text": "everything OK"}]}],
                ),
                ("assistant", [{"type": "text", "text": "Confirmed."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "Confirmed."},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_claim_evidence_matches_whole_words_only(self) -> None:
        # "broken pipe" embeds "ok" but is not evidence: the word-boundary match
        # blocks it, while a real "OK" summary line still backs the claim.
        self.commit_file("ok.py", "print('ok')\n")

        def transcript_with(output: str) -> pathlib.Path:
            return self._claim_transcript(
                [
                    ("user", "run the tests"),
                    (
                        "assistant",
                        [{"type": "tool_use", "id": "t1", "name": "Bash",
                          "input": {"command": "pytest"}}],
                    ),
                    (
                        "user",
                        [{"type": "tool_result", "tool_use_id": "t1",
                          "content": output}],
                    ),
                    ("assistant", [{"type": "text", "text": "All tests pass."}]),
                ]
            )

        blocked = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript_with("error: broken pipe")),
             "last_assistant_message": "All tests pass."},
        )
        self.assertEqual(2, blocked.returncode, blocked.stderr)
        self.assertIn("Final message claims verification", blocked.stderr)

        passed = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript_with("Ran 3 tests\n\nOK")),
             "last_assistant_message": "All tests pass."},
        )
        self.assertEqual(0, passed.returncode, passed.stderr)

    def test_claim_falls_back_to_last_assistant_text_block(self) -> None:
        # With no last_assistant_message field, the gate reads the claim from
        # the transcript's last assistant text block ("Verified.") and blocks
        # when no result backs it.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "run the tests"),
                ("assistant", [{"type": "text", "text": "Verified."}]),
            ]
        )
        result = self.run_hook(self.SCRIPT, {"transcript_path": str(transcript)})
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(
            "Final message claims verification without command output in this turn.",
            result.stderr,
        )

    def test_message_without_claim_word_passes(self) -> None:
        # No claim word in the final message: the leg never fires, exit 0.
        self.commit_file("ok.py", "print('ok')\n")
        transcript = self._claim_transcript(
            [
                ("user", "update the readme"),
                ("assistant", [{"type": "text", "text": "Edited the README."}]),
            ]
        )
        result = self.run_hook(
            self.SCRIPT,
            {"transcript_path": str(transcript),
             "last_assistant_message": "Edited the README."},
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_path_ruff_binary_clean_file_passes_when_module_missing(self) -> None:
        # Binary-fallback happy path: `python3 -m ruff` is missing and a PATH
        # `ruff` binary exits 0 on a clean changed file, so the gate passes with
        # no "ruff unavailable" note. (The failing-binary path is covered by
        # test_path_ruff_binary_is_used_when_module_is_missing.)
        self.commit_file("ok.py", "print('ok')\n")
        (self.repo / "clean.py").write_text("print('fine')\n", encoding="utf-8")

        shim_dir = self._ruffless_path()
        fake_ruff = shim_dir / "ruff"
        fake_ruff.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
        fake_ruff.chmod(0o755)

        env = dict(os.environ)
        env["PATH"] = str(shim_dir)
        result = self.run_hook(self.SCRIPT, {}, env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("ruff unavailable", result.stderr)


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

    def _fallback_path(self) -> pathlib.Path:
        """PATH dir where `python3 -m ruff` fails, but a fake `ruff` binary
        (which strips `import os`) stands in, so the binary fallback must run."""
        shim_dir = pathlib.Path(self.temp_dir.name) / "shim"
        shim_dir.mkdir(exist_ok=True)
        real_python = subprocess.run(
            ["bash", "-lc", "command -v python3"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        shim = shim_dir / "python3"
        shim.write_text(
            "#!/bin/bash\n"
            'if [ "$1" = "-m" ] && [ "$2" = "ruff" ]; then echo "No module named ruff" >&2; exit 1; fi\n'
            f'exec "{real_python}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)
        real_bash = subprocess.run(
            ["bash", "-lc", "command -v bash"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        link = shim_dir / "bash"
        if not link.exists():
            link.symlink_to(real_bash)
        fake_ruff = shim_dir / "ruff"
        fake_ruff.write_text(
            "#!/bin/bash\n"
            'f="${@: -1}"\n'
            "python3 - \"$f\" <<'PY'\n"
            "import sys\n"
            "p = sys.argv[1]\n"
            'lines = [l for l in open(p) if l.strip() != "import os"]\n'
            'open(p, "w").writelines(lines)\n'
            "PY\n",
            encoding="utf-8",
        )
        fake_ruff.chmod(0o755)
        return shim_dir

    def test_ruff_binary_fallback_fixes_file_when_module_missing(self) -> None:
        # uv/brew installs ship ruff as a PATH binary only. When `python3 -m
        # ruff` is unavailable the hook must fall back to that binary and still
        # apply the fix, not silently no-op.
        target = self.repo / "edited.py"
        target.write_text("import os\nprint('x')\n", encoding="utf-8")

        shim_dir = self._fallback_path()
        env = dict(os.environ)
        env["PATH"] = str(shim_dir)
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}, env=env
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("import os", target.read_text(encoding="utf-8"))


class BashAuditLogTests(HookFixtureCase):
    SCRIPT = "bash-audit-log.sh"

    def _post(self, command: str = "echo fixture-run", exit_code: int = 0) -> dict:
        return {
            "cwd": str(self.repo),
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "tool_response": {"exit_code": exit_code, "stdout": "", "stderr": ""},
        }

    def _audit(self) -> str:
        return (self.repo / ".claude/audit.log").read_text(encoding="utf-8")

    def test_post_tool_use_logs_exit_and_command(self) -> None:
        result = self.run_hook(self.SCRIPT, self._post())
        self.assertEqual(0, result.returncode, result.stderr)
        log = self._audit()
        self.assertIn("| exit=0 |", log)
        self.assertIn("| echo fixture-run", log)

    def test_post_tool_use_failure_records_exit_code(self) -> None:
        payload = {
            "cwd": str(self.repo),
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "false"},
            "error": "Exit code 1\nboom",
            "is_interrupt": False,
        }
        result = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("exit=1", self._audit())

    def test_malformed_json_logs_unparseable_and_passes(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("unparseable", self._audit())

    def test_active_experiment_mirrors_line_into_run_folder(self) -> None:
        (self.repo / "experiments/demo").mkdir(parents=True)
        env = dict(os.environ, EXPERIMENT_ACTIVE="demo")
        result = self.run_hook(self.SCRIPT, self._post(), env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("| demo |", self._audit())
        cmd_dir = self.repo / "experiments/demo/logs/commands"
        logs = list(cmd_dir.glob("*.log"))
        self.assertEqual(1, len(logs), logs)
        content = logs[0].read_text(encoding="utf-8")
        self.assertIn("echo fixture-run", content)
        self.assertIn("| demo |", content)

    def test_active_experiment_without_folder_logs_only_audit(self) -> None:
        env = dict(os.environ, EXPERIMENT_ACTIVE="demo")
        result = self.run_hook(self.SCRIPT, self._post(), env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("| demo |", self._audit())
        self.assertFalse((self.repo / "experiments").exists())

    def test_cwd_field_directs_log_to_that_repo(self) -> None:
        other = pathlib.Path(self.temp_dir.name) / "repo2"
        other.mkdir()
        (other / ".claude").mkdir()
        payload = self._post()
        payload["cwd"] = str(other)
        result = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(
            "| echo fixture-run",
            (other / ".claude/audit.log").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.repo / ".claude/audit.log").exists())

    def test_multiline_quoted_command_lands_intact(self) -> None:
        # NUL-separated parsing must carry an embedded newline and double
        # quotes through unchanged: two lines in the log, quotes preserved.
        command = 'echo "first"\necho "second"'
        result = self.run_hook(self.SCRIPT, self._post(command=command))
        self.assertEqual(0, result.returncode, result.stderr)
        log = self._audit()
        self.assertIn('| echo "first"\necho "second"\n', log)
        self.assertEqual(2, len(log.rstrip("\n").split("\n")))


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


class WriteRewriteGuardTests(HookFixtureCase):
    SCRIPT = "write-rewrite-guard.sh"

    def _write_lines(self, name: str, count: int) -> pathlib.Path:
        target = self.repo / name
        target.write_text("x\n" * count, encoding="utf-8")
        return target

    def test_file_at_threshold_triggers(self) -> None:
        target = self._write_lines("big.txt", 80)
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("80 lines", context)
        self.assertEqual("PreToolUse", payload["hookSpecificOutput"]["hookEventName"])

    def test_file_below_threshold_is_silent(self) -> None:
        target = self._write_lines("small.txt", 79)
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_missing_file_is_silent(self) -> None:
        result = self.run_hook(
            self.SCRIPT,
            {"tool_input": {"file_path": str(self.repo / "nope.txt")}},
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_custom_threshold_env_triggers(self) -> None:
        target = self._write_lines("ten.txt", 10)
        env = dict(os.environ, REWRITE_GUARD_LINES="10")
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"file_path": str(target)}}, env=env
        )
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("10 lines", context)

    def test_malformed_json_is_silent(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_relative_path_resolved_via_cwd(self) -> None:
        self._write_lines("big.txt", 80)
        result = self.run_hook(
            self.SCRIPT,
            {"tool_input": {"file_path": "big.txt"}, "cwd": str(self.repo)},
        )
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("80 lines", context)


class BashLengthAdvisoryTests(HookFixtureCase):
    SCRIPT = "bash-length-advisory.sh"

    def test_long_command_triggers(self) -> None:
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"command": "a" * 401}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("(401 chars)", context)

    def test_boundary_command_is_silent(self) -> None:
        result = self.run_hook(
            self.SCRIPT, {"tool_input": {"command": "a" * 400}}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_malformed_json_is_silent(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())


class PostCompactReinjectTests(HookFixtureCase):
    SCRIPT = "post-compact-reinject.sh"

    def test_emits_reminders(self) -> None:
        result = self.run_hook(self.SCRIPT, {"source": "compact"})
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(result.stdout.startswith("Post-compaction reminders:"))
        self.assertIn("5. Re-read HANDOFF.md", result.stdout)

    def test_empty_stdin_still_emits(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(result.stdout.startswith("Post-compaction reminders:"))
        self.assertIn("5. Re-read HANDOFF.md", result.stdout)


class HarnessHygieneTests(HookFixtureCase):
    SCRIPT = "harness-hygiene.sh"

    CLAUDE_MD = (
        "# Fixture agent doc\n\n"
        "- `bin/real.sh`\n"
        "- `bin/gone.sh`\n"
        "- `git status --short`\n"
        "- `nonexistent-cmd-xyz --flag`\n"
        "- `/catchup`\n"
        "- `.env*`\n"
        "- `HANDOFF.md`\n"
        "- `real.sh`\n"
        "- `{{ project_name }}`\n"
    )

    def _payload(self) -> dict:
        return {"cwd": str(self.repo)}

    def test_reports_only_dead_paths_and_missing_commands(self) -> None:
        (self.repo / "bin").mkdir()
        (self.repo / "bin/real.sh").write_text("echo real\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text(self.CLAUDE_MD, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture docs")

        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)
        out = result.stdout
        self.assertIn("bin/gone.sh", out)
        self.assertIn("missing path", out)
        self.assertIn("nonexistent-cmd-xyz", out)
        self.assertIn("command not found", out)
        for absent in ("real.sh", "catchup", ".env", "HANDOFF.md", "project_name"):
            self.assertNotIn(absent, out)

    def test_clean_doc_is_silent(self) -> None:
        (self.repo / "CLAUDE.md").write_text(
            "# Clean doc\n\nNo dead references here.\n", encoding="utf-8"
        )
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_no_agent_docs_is_silent(self) -> None:
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout.strip())

    def test_malformed_json_passes(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)

    INNOCENT_MD = (
        "# Fixture agent doc\n\n"
        "- `v2.0.0`\n"
        "- `1.2.3`\n"
        "- `asyncio.gather`\n"
        "- `this.state`\n"
        "- `docs.example.com`\n"
        "- `Node.js`\n"
        "- `strict.mode`\n"
        "- `gone.md`\n"
    )

    def test_dotted_non_paths_are_not_flagged(self) -> None:
        # Innocent-prose control: version strings and dotted names carry a dot
        # but are not paths. Only the real missing file may be reported.
        (self.repo / "CLAUDE.md").write_text(self.INNOCENT_MD, encoding="utf-8")

        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)
        out = result.stdout
        self.assertIn("1 stale reference(s)", out)
        self.assertIn("gone.md (missing path)", out)
        for absent in (
            "v2.0.0",
            "1.2.3",
            "asyncio.gather",
            "this.state",
            "docs.example.com",
            "Node.js",
            "strict.mode",
        ):
            self.assertNotIn(absent, out)


class SkillUsageLogTests(HookFixtureCase):
    SCRIPT = "skill-usage-log.sh"

    def test_logs_skill_name(self) -> None:
        payload = {
            "cwd": str(self.repo),
            "tool_input": {"skill": "catchup", "args": ""},
        }
        result = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        log = (self.repo / ".claude/skill-usage.log").read_text(encoding="utf-8")
        self.assertIn("catchup", log)

    def test_malformed_json_logs_unparseable(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)
        log = (self.repo / ".claude/skill-usage.log").read_text(encoding="utf-8")
        self.assertIn("unparseable", log)

    def test_no_claude_dir_writes_nothing(self) -> None:
        other = pathlib.Path(self.temp_dir.name) / "noclaude"
        other.mkdir()
        payload = {"cwd": str(other), "tool_input": {"skill": "catchup"}}
        result = self.run_hook(self.SCRIPT, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse((other / ".claude").exists())


class TestTamperScanTests(HookFixtureCase):
    SCRIPT = "test-tamper-scan.sh"

    SKIP_TEST = (
        "import pytest\n\n\n"
        '@pytest.mark.skip(reason="flaky")\n'
        "def test_a():\n    assert True\n"
    )

    def _payload(self, command: str = "git commit -m msg") -> dict:
        return {
            "cwd": str(self.repo),
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def _stage(self, name: str, content: str) -> None:
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.git("add", name)

    def test_non_commit_command_passes(self) -> None:
        self._stage("test_x.py", self.SKIP_TEST)
        result = self.run_hook(self.SCRIPT, self._payload("pytest -q"))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_escape_hatch_passes(self) -> None:
        self._stage("test_x.py", self.SKIP_TEST)
        cmd = "git commit -m msg -m 'Test-changes: net flaky'"
        result = self.run_hook(self.SCRIPT, self._payload(cmd))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_no_staged_test_files_passes(self) -> None:
        self._stage("main.py", "def main():\n    return 0\n")
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)

    def test_clean_staged_test_passes(self) -> None:
        self._stage("test_clean.py", "def test_add():\n    assert 1 + 1 == 2\n")
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stderr)

    def test_added_skip_blocks(self) -> None:
        self._stage("test_skip.py", self.SKIP_TEST)
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("new skip/xfail", result.stderr)

    def test_added_mock_blocks(self) -> None:
        self._stage(
            "test_mock.py",
            "from unittest.mock import patch\n\n\n"
            "def test_a():\n"
            '    with patch("os.getcwd"):\n'
            "        assert True\n",
        )
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("new mock/patch", result.stderr)

    def test_loosened_tolerance_blocks(self) -> None:
        self.commit_file(
            "test_tol.py",
            "import pytest\n\n\ndef test_close():\n    x = 1.0\n    y = 1.0\n"
            "    assert x == pytest.approx(y, rel=1e-9)\n",
        )
        (self.repo / "test_tol.py").write_text(
            "import pytest\n\n\ndef test_close():\n    x = 1.0\n    y = 1.0\n"
            "    assert x == pytest.approx(y, rel=1e-2)\n",
            encoding="utf-8",
        )
        self.git("add", "test_tol.py")
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("loosened tolerance", result.stderr)

    def test_asserted_literal_from_new_return_blocks(self) -> None:
        self._stage("calc.py", "def answer():\n    return 42\n")
        self._stage(
            "test_calc.py",
            "from calc import answer\n\n\n"
            "def test_answer():\n    assert answer() == 42\n",
        )
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("expected literal", result.stderr)
        self.assertIn("calc.py", result.stderr)

    def test_malformed_json_passes(self) -> None:
        result = self.run_hook(self.SCRIPT, None, raw_payload="{not json")
        self.assertEqual(0, result.returncode, result.stderr)

    def test_comment_mentioning_skip_passes(self) -> None:
        # A trailing "# skip the header row" is prose, not a pytest skip.
        self._stage(
            "test_comment.py",
            "def test_rows():\n"
            "    data = [1, 2, 3]\n"
            "    rows = data[1:]  # skip the header row\n"
            "    assert rows == [2, 3]\n",
        )
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_trivial_return_literal_passes(self) -> None:
        # `return 0` and `== 0` coincide in every codebase; only a distinctive
        # literal (see test_asserted_literal_from_new_return_blocks) is a tell.
        self._stage("main.py", "def main():\n    return 0\n")
        self._stage(
            "test_main.py",
            "from main import main\n\n\ndef test_main():\n    assert main() == 0\n",
        )
        result = self.run_hook(self.SCRIPT, self._payload())
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_git_grep_commit_is_not_a_commit(self) -> None:
        # The trigger must read the git subcommand, not the word "commit".
        self._stage("test_skip.py", self.SKIP_TEST)
        result = self.run_hook(self.SCRIPT, self._payload("git grep commit"))
        self.assertEqual(0, result.returncode, result.stderr)


class MutationGateTests(HookFixtureCase):
    SCRIPT = "mutation-gate.sh"

    def setUp(self) -> None:
        super().setUp()
        # The gate runs cosmic-ray in a linked worktree detached at HEAD, so
        # the fixture repo needs a commit to detach from, exactly as a real
        # repo taking a commit does.
        self.commit_file("README.md", "fixture\n")

    # One cosmic-ray dump job per line, in the two-element [work_item, result]
    # shape the hook's parser reads: a survivor (worker normal, test survived)
    # and a killed mutant (which the parser must drop).
    SURVIVOR = (
        '[{"mutations":[{"module_path":"calc.py","start_pos":[3,0],'
        '"operator_name":"core/NumberReplacer","occurrence":0}]},'
        '{"worker_outcome":"normal","test_outcome":"survived"}]'
    )
    KILLED = (
        '[{"mutations":[{"module_path":"calc.py","start_pos":[4,0],'
        '"operator_name":"core/NumberReplacer","occurrence":1}]},'
        '{"worker_outcome":"normal","test_outcome":"killed"}]'
    )

    def _shim(
        self, *, cosmic_ray: bool = True, exec_exit: int = 0
    ) -> tuple[pathlib.Path, pathlib.Path]:
        """Isolated PATH: real tools the hook shells out to, plus fake
        cosmic-ray / cr-filter-git that log their calls and emit a dump."""
        shim_dir = pathlib.Path(self.temp_dir.name) / "mgshim"
        shim_dir.mkdir(exist_ok=True)
        tools = (
            "bash", "sh", "git", "python3", "cat", "grep", "mktemp", "sed",
            "awk", "tr", "wc", "dirname", "basename", "head", "tail", "rm",
            "mkdir", "env",
        )
        for tool in tools:
            real = subprocess.run(
                ["bash", "-lc", f"command -v {tool}"],
                capture_output=True,
                text=True,
            ).stdout.strip()
            if not real:
                continue
            link = shim_dir / tool
            if not link.exists():
                link.symlink_to(real)
        calls_log = shim_dir / "cr-calls.log"
        if cosmic_ray:
            cr = shim_dir / "cosmic-ray"
            cr.write_text(
                "#!/bin/bash\n"
                'echo "cosmic-ray $*" >> "' + str(calls_log) + '"\n'
                'case "$1" in\n'
                "  dump)\n"
                "    printf '%s\\n' '" + self.SURVIVOR + "'\n"
                "    printf '%s\\n' '" + self.KILLED + "'\n"
                "    ;;\n"
                "  exec)\n"
                "    exit " + str(exec_exit) + "\n"
                "    ;;\n"
                "esac\n"
                "exit 0\n",
                encoding="utf-8",
            )
            cr.chmod(0o755)
            crf = shim_dir / "cr-filter-git"
            crf.write_text(
                "#!/bin/bash\n"
                'echo "cr-filter-git $*" >> "' + str(calls_log) + '"\n'
                "exit 0\n",
                encoding="utf-8",
            )
            crf.chmod(0o755)
        return shim_dir, calls_log

    def _env(self, shim_dir: pathlib.Path) -> dict:
        return dict(os.environ, PATH=str(shim_dir))

    def _payload(self, command: str = "git commit -m msg") -> dict:
        return {
            "cwd": str(self.repo),
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def _stage(self, name: str, content: str) -> None:
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.git("add", name)

    def _pyproject(self) -> None:
        (self.repo / "pyproject.toml").write_text(
            '[project]\nname = "fixture"\nversion = "0"\n', encoding="utf-8"
        )

    def test_non_commit_command_passes_without_tools(self) -> None:
        shim_dir, calls_log = self._shim()
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        result = self.run_hook(
            self.SCRIPT, self._payload("pytest -q"), env=self._env(shim_dir)
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(calls_log.exists())

    def test_no_pyproject_notes_and_passes(self) -> None:
        shim_dir, calls_log = self._shim()
        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("no pyproject.toml", result.stderr)
        self.assertFalse(calls_log.exists())

    def test_no_cosmic_ray_notes_and_passes(self) -> None:
        shim_dir, _ = self._shim(cosmic_ray=False)
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("cosmic-ray not installed", result.stderr)

    def test_only_staged_tests_skips_the_gate(self) -> None:
        shim_dir, calls_log = self._shim()
        self._pyproject()
        self._stage("tests/test_x.py", "def test_a():\n    assert True\n")
        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("no staged non-test", result.stderr)
        self.assertFalse(calls_log.exists())

    def test_surviving_mutant_blocks(self) -> None:
        shim_dir, calls_log = self._shim()
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("Mutation gate: 1 surviving", result.stderr)
        self.assertIn("calc.py:", result.stderr)
        self.assertTrue(calls_log.exists())

    def test_mutants_escape_hatch_passes(self) -> None:
        shim_dir, calls_log = self._shim()
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        cmd = "git commit -m msg -m 'Mutants: justified'"
        result = self.run_hook(self.SCRIPT, self._payload(cmd), env=self._env(shim_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(calls_log.exists())

    def test_broken_exec_step_notes_and_passes(self) -> None:
        shim_dir, _ = self._shim(exec_exit=1)
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("mutation gate skipped", result.stderr)
        self.assertIn("cosmic-ray exec", result.stderr)

    def test_run_leaves_no_worktree_and_no_mutated_source(self) -> None:
        # cosmic-ray mutates a module in place, so the run must happen in a
        # throwaway worktree: after a blocking run the project's source file
        # is byte-identical and no scratch worktree survives.
        shim_dir, _ = self._shim()
        self._pyproject()
        self._stage("calc.py", "def answer():\n    return 42\n")
        source = self.repo / "calc.py"
        before = hashlib.sha256(source.read_bytes()).hexdigest()

        result = self.run_hook(self.SCRIPT, self._payload(), env=self._env(shim_dir))
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())

        listed = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().splitlines()
        self.assertEqual(1, len(listed), listed)


if __name__ == "__main__":
    unittest.main()
