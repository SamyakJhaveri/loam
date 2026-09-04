"""Behavioral fixtures for the shipped Claude hooks (evaluation E1).

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


if __name__ == "__main__":
    unittest.main()
