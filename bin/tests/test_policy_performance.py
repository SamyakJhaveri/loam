#!/usr/bin/env python3
"""Focused regression tests for the Codex pre-tool policy cost bounds."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import shlex
import subprocess
import sys
import types
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[2]
POLICY_SCRIPT = ROOT / "seed/.codex/hooks/pre-tool-policy.py"
OVERSIZED_DENIAL = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Command input exceeds the policy analysis limit."
        ),
    }
}
FORCE_PUSH_DENIAL = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Force pushes are blocked by repository policy."
        ),
    }
}


def load_policy() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("policy_performance", POLICY_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load policy: {POLICY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def policy_payload(command: str) -> str:
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
    )


def command_at_depth(depth: int) -> str:
    command = "echo safe"
    for _ in range(depth):
        command = "sh -c " + shlex.quote(command)
    return command


def run_main(module: types.ModuleType, payload: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with (
        mock.patch.object(sys, "stdin", io.StringIO(payload)),
        contextlib.redirect_stdout(stdout),
        contextlib.redirect_stderr(stderr),
    ):
        return module.main(), stdout.getvalue(), stderr.getvalue()


class PolicyPerformanceTest(unittest.TestCase):
    def test_maximum_accepted_command_finishes_before_hook_deadline(self) -> None:
        module = load_policy()
        limit = module._MAX_COMMAND_BYTES
        force_push = "; git push --force origin main"
        command = "x" * (limit - len(force_push)) + force_push

        self.assertLess(len(command_at_depth(11).encode("utf-8")), limit)
        self.assertEqual(limit, len(command.encode("utf-8")))
        try:
            process = subprocess.run(
                [sys.executable, str(POLICY_SCRIPT)],
                input=policy_payload(command),
                text=True,
                capture_output=True,
                timeout=8,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.fail("maximum accepted command exceeded the 8-second test budget")

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(FORCE_PUSH_DENIAL, json.loads(process.stdout))

    def test_oversized_command_is_denied_before_shell_work(self) -> None:
        module = load_policy()
        shell_checks: list[bool] = []

        def record_shell_check(*args: object, **kwargs: object) -> object:
            shell_checks.append(True)
            return subprocess.CompletedProcess(args[0], 0, "", "")

        with mock.patch.object(
            module.subprocess,
            "run",
            side_effect=record_shell_check,
        ):
            code, stdout, stderr = run_main(
                module,
                policy_payload("x" * 400_001),
            )

        self.assertEqual([], shell_checks)
        self.assertEqual(0, code, stderr)
        self.assertEqual(OVERSIZED_DENIAL, json.loads(stdout))
        self.assertEqual("", stderr)

    def test_outer_command_is_tokenized_once(self) -> None:
        module = load_policy()
        original_literal_tokens = module._literal_tokens
        tokenized: list[str] = []

        def counted_literal_tokens(command: str) -> tuple[str, ...]:
            tokenized.append(command)
            return original_literal_tokens(command)

        module._literal_tokens = counted_literal_tokens
        command = "echo safe"
        code, stdout, stderr = run_main(module, policy_payload(command))

        self.assertEqual(0, code, stderr)
        self.assertEqual("", stdout)
        self.assertEqual("", stderr)
        self.assertEqual([command], tokenized)

    def test_recursion_guard_causes_boundary_denial(self) -> None:
        module = load_policy()
        command = command_at_depth(11)

        self.assertTrue(module._command_denied(command))
        module._RECURSION_LIMIT = 11
        self.assertFalse(module._command_denied(command))


if __name__ == "__main__":
    unittest.main()
