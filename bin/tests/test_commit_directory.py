"""Real receipt checks for explicit target selection; never execute a commit."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[2] / "seed/.agents/lib/validation.py"
SPEC = importlib.util.spec_from_file_location("commit_directory_validation", MODULE)
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


class CommitDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.session = Path(self.temp.name) / "session"
        self.target = Path(self.temp.name) / "target with spaces"
        for root in (self.session, self.target):
            root.mkdir()
            self.git(root, "init", "-q")
            (root / "source.txt").write_text(root.name + "\n")
            (root / ".agents").mkdir()
            (root / ".agents/validation.json").write_text(json.dumps({
                "schema": 1, "checks": [{"name": "content", "argv": [
                    sys.executable, "-c", "from pathlib import Path; assert Path('source.txt').read_text()"
                ]}]
            }))
            (root / "subdir").mkdir()
            self.git(root, "add", ".")

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def validate(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            validation.run(root, "directory-fixture")

    def command(self, target=None):
        return "git -C " + shlex.quote(str(target or self.target)) + " commit -m fixture"

    def gate(self, command, **extra):
        payload = {"cwd": str(self.session), "tool_input": {"command": command, **extra}}
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            result = validation.pre_commit(payload)
        return result, errors.getvalue()

    def test_missing_workdir_metadata_reproduces_observed_denial(self):
        self.validate(self.target)
        result, error = self.gate("git commit -m fixture")
        self.assertEqual(result, 2)
        self.assertIn("receipt missing", error)

    def test_absolute_target_uses_its_own_receipt(self):
        self.validate(self.target)
        self.assertEqual(self.gate(self.command())[0], 0)
        self.assertFalse((self.session / validation.RECEIPT).exists())

    def test_target_subdirectory_resolves_git_root(self):
        self.validate(self.target)
        self.assertEqual(self.gate(self.command(self.target / "subdir"))[0], 0)

    def test_absolute_target_is_independent_of_hook_process_cwd(self):
        self.validate(self.target)
        before = Path.cwd()
        try:
            os.chdir(self.session)
            self.assertEqual(self.gate(self.command())[0], 0)
        finally:
            os.chdir(before)

    def test_session_receipt_never_authorizes_missing_target_receipt(self):
        self.validate(self.session)
        result, error = self.gate(self.command())
        self.assertEqual(result, 2)
        self.assertIn("receipt missing", error)

    def test_stale_target_receipt_fails(self):
        self.validate(self.target)
        (self.target / "source.txt").write_text("changed\n")
        self.git(self.target, "add", "source.txt")
        self.assertEqual(self.gate(self.command())[0], 2)

    def test_target_index_mismatch_fails(self):
        (self.target / "source.txt").write_text("unstaged\n")
        self.validate(self.target)
        result, error = self.gate(self.command())
        self.assertEqual(result, 2)
        self.assertIn("Staged contents differ", error)

    def test_target_untracked_input_fails(self):
        (self.target / "extra.txt").write_text("untracked\n")
        self.validate(self.target)
        result, error = self.gate(self.command())
        self.assertEqual(result, 2)
        self.assertIn("Untracked validation inputs", error)

    def test_plain_session_commit_preserves_existing_behavior(self):
        self.validate(self.session)
        self.assertEqual(self.gate("git commit -m fixture")[0], 0)

    def test_unquoted_glob_cannot_select_an_unvalidated_sibling(self):
        literal = self.target / "[a]"
        expanded = self.target / "a"
        for root in (literal, expanded):
            shutil.copytree(self.session, root)
        self.validate(literal)
        # Quote only the parent, leaving the basename glob active. This probe
        # prints Bash's real argument expansion without executing any commit.
        shell_path = shlex.quote(str(self.target)) + "/[a]"
        result = subprocess.run(["bash", "-c", "printf '%s' " + shell_path],
                                text=True, check=True, capture_output=True)
        self.assertEqual(result.stdout, str(expanded))
        self.assertFalse((expanded / validation.RECEIPT).exists())
        self.assertEqual(self.gate("git -C " + shell_path + " commit -m fixture")[0], 2)

    def test_new_directory_form_conservatively_rejects_glob_and_brace_paths(self):
        for name in ("[a]", "?", "*", "{a,b}"):
            root = self.target / name
            shutil.copytree(self.session, root)
            self.validate(root)
            with self.subTest(name=name):
                self.assertEqual(self.gate(self.command(root))[0], 2)

    def test_new_directory_form_rejects_trailing_shell_operators(self):
        self.validate(self.target)
        for operator in ("&", ";", "|", "&&", "||", ">", "<"):
            with self.subTest(operator=operator):
                self.assertEqual(self.gate(self.command() + " " + operator)[0], 2)

    def test_quoted_semicolon_directory_is_literal(self):
        root = self.target / "semi;colon"
        shutil.copytree(self.session, root)
        self.validate(root)
        self.assertEqual(self.gate(self.command(root))[0], 0)

    def test_unsupported_context_and_syntax_remain_denied(self):
        self.validate(self.session)
        self.validate(self.target)
        target = shlex.quote(str(self.target))
        commands = [
            "git -C relative commit -m fixture", "git -C '' commit -m fixture",
            "git -C commit -m fixture", "git -C /missing-target commit -m fixture",
            "git -C " + target + " -C /tmp commit -m fixture",
            "git -C" + target + " commit -m fixture",
            "git --git-dir " + target + "/.git commit -m fixture",
            "git --work-tree " + target + " commit -m fixture",
            "git -c core.hooksPath=/tmp commit -m fixture",
            "git --no-pager -C " + target + " commit -m fixture",
            "git -C " + target + " commit -a -m fixture",
            "git -C " + target + " commit --only source.txt -m fixture",
            "git -C " + target + " commit --no-verify -m fixture",
            "env git -C " + target + " commit -m fixture",
            "GIT_DIR=/tmp git -C " + target + " commit -m fixture",
            "cd " + target + " && git commit -m fixture",
            "git -C " + target + " commit -m fixture; true",
            "git -C \"$(pwd)\" commit -m fixture",
            "git -C /tmp/\0bad commit -m fixture",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.gate(command)[0], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
