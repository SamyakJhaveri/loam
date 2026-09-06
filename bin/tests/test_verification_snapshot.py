from __future__ import annotations

import contextlib
import io
import math
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import verification_snapshot as snapshot


class VerificationSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "source"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Snapshot Test")
        self.git("config", "user.email", "snapshot@example.invalid")
        (self.root / "input.txt").write_text("committed\n")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])

    def run_quietly(self, command, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            with contextlib.redirect_stderr(io.StringIO()):
                return snapshot.run(self.root, command, **kwargs)

    def assert_process_stopped(self, pid_file):
        pid = int(pid_file.read_text())

        def stop_if_needed():
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        self.addCleanup(stop_if_needed)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.02)
        self.fail(f"descendant process {pid} survived snapshot cleanup")

    def test_snapshot_uses_dirty_and_untracked_content_without_changing_index(self):
        (self.root / "input.txt").write_text("staged\n")
        self.git("add", "input.txt")
        (self.root / "input.txt").write_text("working\n")
        (self.root / "new file.txt").write_text("new\n")
        head_before = self.git("rev-parse", "HEAD")
        index_before = self.git("ls-files", "--stage", "-z")
        target = pathlib.Path(self.temp.name) / "snapshot"
        state = snapshot.create_snapshot(self.root, target)
        self.assertEqual("working\n", (target / "input.txt").read_text())
        self.assertEqual("new\n", (target / "new file.txt").read_text())
        self.assertEqual(head_before, self.git("rev-parse", "HEAD"))
        self.assertEqual(index_before, self.git("ls-files", "--stage", "-z"))
        self.assertEqual(state, snapshot.source_state(self.root))
        self.assertEqual(
            b"working\n",
            subprocess.check_output(
                ["git", "-C", str(target), "show", "HEAD:input.txt"]
            ),
        )

    def test_deleted_file_stays_deleted_in_snapshot(self):
        (self.root / "input.txt").unlink()
        target = pathlib.Path(self.temp.name) / "snapshot"
        snapshot.create_snapshot(self.root, target)
        self.assertFalse((target / "input.txt").exists())

    def test_preserves_relative_symlink_and_executable(self):
        (self.root / "link").symlink_to("input.txt")
        (self.root / "input.txt").chmod(0o755)
        target = pathlib.Path(self.temp.name) / "snapshot"
        snapshot.create_snapshot(self.root, target)
        self.assertTrue((target / "link").is_symlink())
        self.assertEqual("input.txt", (target / "link").readlink().as_posix())
        self.assertEqual(0o111, (target / "input.txt").stat().st_mode & 0o111)
        tree = subprocess.check_output(
            ["git", "-C", str(target), "ls-tree", "HEAD", "input.txt", "link"],
            text=True,
        )
        self.assertIn("100755 blob", tree)
        self.assertIn("120000 blob", tree)

    def test_relative_external_symlink_is_rejected_without_following(self):
        (self.root / "link").symlink_to("../private")
        with self.assertRaises(ValueError):
            snapshot.create_snapshot(
                self.root, pathlib.Path(self.temp.name) / "snapshot"
            )

    def test_absolute_internal_symlink_is_rejected(self):
        (self.root / "link").symlink_to(self.root / "input.txt")
        with self.assertRaises(ValueError):
            snapshot.create_snapshot(
                self.root, pathlib.Path(self.temp.name) / "snapshot"
            )

    def test_failed_command_is_not_masked(self):
        self.assertEqual(
            7,
            self.run_quietly([sys.executable, "-c", "raise SystemExit(7)"]),
        )

    def test_source_change_during_check_rejects_success(self):
        script = (
            "from pathlib import Path; Path("
            + repr(str(self.root / "input.txt"))
            + ").write_text('changed')"
        )
        self.assertNotEqual(0, self.run_quietly([sys.executable, "-c", script]))

    def test_transient_source_change_during_check_rejects_success(self):
        path = repr(str(self.root / "input.txt"))
        script = (
            f"from pathlib import Path; path = Path({path}); "
            "path.write_text('changed\\n'); path.write_text('committed\\n')"
        )
        self.assertNotEqual(0, self.run_quietly([sys.executable, "-c", script]))

    def test_generation_baseline_spans_snapshot_return_and_command(self):
        original_create = snapshot.create_snapshot

        def create_then_restore(*args, **kwargs):
            state = original_create(*args, **kwargs)
            path = self.root / "input.txt"
            path.write_text("changed\n")
            path.write_text("committed\n")
            return state

        with mock.patch.object(
            snapshot, "create_snapshot", side_effect=create_then_restore
        ):
            result = self.run_quietly([sys.executable, "-c", "pass"])
        self.assertNotEqual(0, result)

    def test_nonfinite_deadlines_are_rejected_before_snapshot_creation(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with mock.patch.object(snapshot, "create_snapshot") as create:
                    with mock.patch.object(snapshot, "_run_command") as run_command:
                        with self.assertRaisesRegex(ValueError, "finite and positive"):
                            snapshot.run(
                                self.root,
                                [sys.executable, "-c", "pass"],
                                timeout_seconds=value,
                            )
                create.assert_not_called()
                run_command.assert_not_called()

    def test_transient_source_change_during_snapshot_is_rejected(self):
        original_copy = snapshot.shutil.copy2

        def copy_then_restore(source, destination, **kwargs):
            result = original_copy(source, destination, **kwargs)
            source.write_text("changed\n")
            source.write_text("committed\n")
            return result

        target = pathlib.Path(self.temp.name) / "snapshot"
        with mock.patch.object(snapshot.shutil, "copy2", side_effect=copy_then_restore):
            with self.assertRaisesRegex(ValueError, "source changed while creating"):
                snapshot.create_snapshot(self.root, target)

    def test_deadline_terminates_command_and_descendant_process(self):
        pid_file = pathlib.Path(self.temp.name) / "child.pid"
        ready_file = pathlib.Path(self.temp.name) / "child.ready"
        child = (
            "import signal, time; "
            "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
            f"open({str(ready_file)!r}, 'w').write('ready'); "
            "time.sleep(60)"
        )
        script = "\n".join(
            [
                "import os, signal, subprocess, sys, time",
                "signal.signal(signal.SIGTERM, signal.SIG_IGN)",
                f"child = subprocess.Popen([sys.executable, '-c', {child!r}])",
                f"open({str(pid_file)!r}, 'w').write(str(child.pid))",
                f"ready = {str(ready_file)!r}",
                "while not os.path.exists(ready):",
                "    time.sleep(0.005)",
                "time.sleep(60)",
            ]
        )
        started = time.monotonic()
        result = self.run_quietly(
            [sys.executable, "-c", script],
            timeout_seconds=0.1,
        )
        self.assertEqual(snapshot.TIMEOUT_EXIT_CODE, result)
        self.assertLess(time.monotonic() - started, 3)
        self.assertTrue(pid_file.is_file())
        self.assert_process_stopped(pid_file)

    def test_successful_command_does_not_leave_descendants_running(self):
        pid_file = pathlib.Path(self.temp.name) / "child.pid"
        child = "import time; time.sleep(60)"
        script = (
            "import subprocess, sys; "
            f"child = subprocess.Popen([sys.executable, '-c', {child!r}]); "
            f"open({str(pid_file)!r}, 'w').write(str(child.pid))"
        )
        self.assertEqual(
            0,
            self.run_quietly([sys.executable, "-c", script], timeout_seconds=5),
        )
        self.assert_process_stopped(pid_file)

    def test_dirty_defect_is_exercised_not_stale_head(self):
        (self.root / "input.txt").write_text("BROKEN\n")
        script = (
            "from pathlib import Path; import sys; "
            "sys.exit('BROKEN' in Path('input.txt').read_text())"
        )
        self.assertNotEqual(0, self.run_quietly([sys.executable, "-c", script]))

    def test_persistent_and_restored_scratch_input_writes_reject_success(self):
        for tail in ("", "; path.write_text('committed\\n')"):
            with self.subTest(restored=bool(tail)):
                script = (
                    "from pathlib import Path; path=Path('input.txt'); path.write_text('changed')"
                    + tail
                )
                self.assertNotEqual(0, self.run_quietly([sys.executable, "-c", script]))
                self.assertEqual("committed\n", (self.root / "input.txt").read_text())

    def test_transient_new_scratch_input_rejects_success(self):
        script = "from pathlib import Path; p=Path('temporary.py'); p.write_text('influenced check'); assert p.read_text(); p.unlink()"
        self.assertNotEqual(0, self.run_quietly([sys.executable, "-c", script]))

    def test_scratch_ignored_cache_and_receipt_writes_are_allowed(self):
        (self.root / ".gitignore").write_text("cache/\n__pycache__/\n")
        script = (
            "from pathlib import Path; import os; "
            "assert os.environ['PYTHONDONTWRITEBYTECODE']=='1'; "
            "assert os.environ['GIT_OPTIONAL_LOCKS']=='0'; "
            "p=Path('cache/nested'); p.mkdir(parents=True,exist_ok=True); "
            "(p/'result').write_text('generated'); "
            "Path('.validation_passed').write_text('diagnostic receipt')"
        )
        self.assertEqual(0, self.run_quietly([sys.executable, "-c", script]))
        self.assertFalse((self.root / "cache").exists())
        self.assertFalse((self.root / ".validation_passed").exists())

    def test_public_gate_rejects_early_stage_repair_of_dirty_seed(self):
        project = pathlib.Path(__file__).resolve().parents[2]
        (self.root / "bin").mkdir()
        (self.root / "seed/.agents/lib").mkdir(parents=True)
        for relative in (
            "bin/verify-template.sh",
            "bin/verification_snapshot.py",
            "seed/.agents/lib/validation.py",
        ):
            shutil.copy2(project / relative, self.root / relative)
        broken = self.root / "seed/broken.txt"
        broken.write_text("good\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture gate")
        broken.write_text("BROKEN\n")
        stage = self.root / "bin/verify-template-stages.sh"
        stage.write_text("#!/bin/sh\nprintf 'repaired\\n' > seed/broken.txt\nexit 0\n")
        result = subprocess.run(
            ["bash", "bin/verify-template.sh"],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("verify-template: PASSED", result.stdout)
        self.assertEqual("BROKEN\n", broken.read_text())


if __name__ == "__main__":
    unittest.main()
