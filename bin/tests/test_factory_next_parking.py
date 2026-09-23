"""`bin/factory next` parks a ticket only on a run of its current body, so a body edit relaunches it.

`bin/factory` is sourced (FACTORY_SOURCED=1) with a temp runs root. park_status is called directly,
and cmd_next --dry-run runs with gh, the login probe, and the toolchain gate stubbed as shell functions,
so the frontier line carries the body the way the real query does. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import base64
import hashlib
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def sourced(script: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run `script` in a bash that has sourced bin/factory from the repo root."""
    return subprocess.run(
        ["bash", "-c", f". bin/factory\n{script}"],
        cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1", **(env or {})},
        capture_output=True, text=True, check=False,
    )


def key(body: str) -> str:
    """The run-dir key cmd_run computes: the first 8 hex digits of the body's sha256."""
    return hashlib.sha256(body.encode()).hexdigest()[:8]


class ParkingTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs = pathlib.Path(tmp.name)

    def run_dir(self, issue: int, body: str, status: str) -> None:
        d = self.runs / str(issue) / key(body)
        d.mkdir(parents=True)
        (d / "status").write_text(status + "\n")
        (d / "launched").write_text("1\n")

    def park_status(self, issue: int, body: str) -> str:
        proc = sourced(f'park_status {issue} "$BODY_ARG"', {"FACTORY_RUNS_ROOT": str(self.runs), "BODY_ARG": body})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    def next_dry_run(self, issue: int, body: str) -> subprocess.CompletedProcess[str]:
        line = f"{issue} {base64.b64encode(body.encode()).decode()}"
        stubs = ("assert_toolchain_env() { :; }; claude_logged_in() { :; }; "
                 f"gh() {{ case $1 in repo) echo o/r ;; api) echo '{line}' ;; esac; }}; cmd_next --dry-run")
        return sourced(stubs, {"FACTORY_RUNS_ROOT": str(self.runs)})

    def test_old_body_abandon_does_not_park_a_new_body(self) -> None:
        self.run_dir(7, "the old body", "abandon")
        self.assertEqual(self.park_status(7, "the new body\n\nwith a second paragraph"), "none")
        proc = self.next_dry_run(7, "the new body\n\nwith a second paragraph")
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertNotIn("parked", proc.stderr)

    def test_same_body_abandon_parks(self) -> None:
        body = "same body\n\n- a list item"
        self.run_dir(7, body, "abandon")
        self.assertEqual(self.park_status(7, body), "abandon")
        proc = self.next_dry_run(7, body)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("parked #7: last run exited abandon", proc.stderr)

    def test_same_body_stopped_environment_relaunches(self) -> None:
        body = "same body"
        self.run_dir(7, body, "stopped-environment")
        self.assertEqual(self.park_status(7, body), "stopped-environment")
        proc = self.next_dry_run(7, body)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_trailing_newlines_strip_as_load_ticket_does(self) -> None:
        # gh returns the body raw; load_ticket's $(...) strips its trailing newlines before cmd_run keys it.
        self.run_dir(7, "body", "abandon")
        proc = self.next_dry_run(7, "body\n\n")
        self.assertIn("parked #7: last run exited abandon", proc.stderr)


if __name__ == "__main__":
    unittest.main()
