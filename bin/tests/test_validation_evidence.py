"""Exercise validation receipts against real temporary repositories and commands."""

from __future__ import annotations

import json
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[2] / "seed/.agents/lib/validation.py"
RUNNER = MODULE.parents[2] / ".claude/hooks/run-validate-waves.sh"
SPEC = importlib.util.spec_from_file_location("validation_evidence_module", MODULE)
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


class ValidationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@test")
        self.git("config", "user.name", "Fixture")
        (self.root / "source.txt").write_text("original\n")
        (self.root / ".gitignore").write_text("ignored/\n")
        self.configure()
        self.git("add", ".")
        self.git("commit", "-qm", "initial")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def configure(self, code="print('fixture check passed')"):
        config = self.root / ".agents/validation.json"
        config.parent.mkdir(exist_ok=True)
        config.write_text(json.dumps({"schema": 1, "checks": [
            {"name": "fixture", "argv": [sys.executable, "-c", code]}
        ]}))

    def cli(self, action, env=None):
        self.assertTrue(MODULE.is_file(), "shared content-bound validation module is missing")
        return subprocess.run([sys.executable, str(MODULE), action, "--root", str(self.root)],
                              text=True, capture_output=True, env=env, timeout=30)

    def passed(self, env=None):
        result = self.cli("run", env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.cli("check", env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def invalid(self, env=None):
        result = self.cli("check", env)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def receipt(self):
        return self.root / ".validation_passed"

    def test_success_receipt_is_complete_and_atomic(self):
        self.configure("from pathlib import Path; assert not Path('.validation_passed').exists()")
        self.passed()
        data = json.loads(self.receipt().read_text())
        self.assertEqual(data["schema"], 1)
        self.assertIs(data["production"], True)
        self.assertEqual(data["status"], "passed")
        self.assertIn("digest", data["source"])
        self.assertIn("python", data["runtime"])
        self.assertTrue(data["checks"])
        for check in data["checks"]:
            self.assertEqual(check["status"], "passed")
            self.assertEqual(check["exit_code"], 0)
            self.assertGreaterEqual(check["elapsed_seconds"], 0)
            self.assertTrue(check["argv"])
        self.assertEqual(list(self.root.glob('.validation_passed.tmp.*')), [])

    def test_changed_content_with_preserved_mtime_invalidates(self):
        self.passed()
        source = self.root / "source.txt"
        before = source.stat()
        source.write_text("modified\n")
        os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.invalid()

    def test_mtime_alone_and_old_receipt_do_not_invalidate(self):
        self.passed()
        os.utime(self.root / "source.txt", (1, 1))
        os.utime(self.receipt(), (1, 1))
        self.assertEqual(self.cli("check").returncode, 0)

    def test_repaired_input_rerun_does_not_refresh_index(self):
        env = dict(os.environ)
        env.pop("GIT_OPTIONAL_LOCKS", None)
        self.passed(env)
        source = self.root / "source.txt"
        source.write_text("broken\n")
        self.invalid(env)
        source.write_text("original\n")
        os.utime(source, (1, 1))
        index = self.root / ".git/index"
        before = index.read_bytes()
        self.passed(env)
        self.assertEqual(index.read_bytes(), before)

    def test_deletion_invalidates(self):
        self.passed()
        (self.root / "source.txt").unlink()
        self.invalid()

    def test_rename_invalidates(self):
        self.passed()
        (self.root / "source.txt").rename(self.root / "renamed.txt")
        self.invalid()

    def test_staging_change_without_worktree_change_invalidates(self):
        (self.root / "source.txt").write_text("modified\n")
        self.passed()
        self.git("add", "source.txt")
        self.invalid()

    def test_untracked_input_invalidates(self):
        self.passed()
        (self.root / "extra.txt").write_text("new\n")
        self.invalid()

    def test_stale_head_invalidates(self):
        self.passed()
        self.git("commit", "--allow-empty", "-qm", "new head")
        self.invalid()

    def test_ignored_artifact_does_not_invalidate(self):
        self.passed()
        (self.root / "ignored").mkdir()
        (self.root / "ignored/log").write_text("output")
        self.assertEqual(self.cli("check").returncode, 0)

    def test_failure_removes_old_success(self):
        self.passed()
        self.configure("raise SystemExit(9)")
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_required_missing_executable_blocks(self):
        config = self.root / ".agents/validation.json"
        config.write_text(json.dumps({"schema": 1, "checks": [
            {"name": "missing", "argv": ["loam-nonexistent-check-tool"]}]}))
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_no_project_checks_cannot_pass(self):
        (self.root / ".agents/validation.json").unlink()
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_justified_not_applicable_is_explicit(self):
        (self.root / ".agents/validation.json").write_text(json.dumps({
            "schema": 1, "not_applicable": "Text-only notes; no executable tests."}))
        self.passed()
        data = json.loads(self.receipt().read_text())
        self.assertIn("Text-only notes", data["plan"]["not_applicable"])

    def test_empty_checks_or_blank_justification_cannot_pass(self):
        for value in ({"schema": 1, "checks": []}, {"schema": 1, "not_applicable": " "}):
            with self.subTest(value=value):
                (self.root / ".agents/validation.json").write_text(json.dumps(value))
                self.assertNotEqual(self.cli("run").returncode, 0)

    def test_override_seams_never_create_evidence(self):
        self.passed()
        env = dict(os.environ, RUN_VALIDATE_WAVE1_CMD="true", RUN_VALIDATE_WAVE2_CMD="true")
        self.assertNotEqual(self.cli("run", env).returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_mutation_during_check_invalidates_success(self):
        self.configure("from pathlib import Path; Path('source.txt').write_text('changed by check')")
        self.assertNotEqual(self.cli("run").returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_mutation_restored_before_check_exit_still_invalidates(self):
        self.configure("from pathlib import Path; p=Path('source.txt'); original=p.read_bytes(); p.write_text('transient change'); p.write_bytes(original)")
        self.assertNotEqual(self.cli("run").returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_transient_new_input_invalidates(self):
        for location in ("transient.py", "new/subdir/transient.py"):
            with self.subTest(location=location):
                self.configure("from pathlib import Path; import shutil; p=Path(" + repr(location) + "); "
                               "p.parent.mkdir(parents=True, exist_ok=True); p.write_text('temporary input'); "
                               "assert p.read_text(); p.unlink(); "
                               "shutil.rmtree('new', ignore_errors=True)")
                result = self.cli("run")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(self.receipt().exists())

    def test_ignored_cache_creation_during_checks_is_allowed(self):
        # Prewarm the ignored cache root; its contents do not enter generations.
        (self.root / "ignored").mkdir()
        self.configure("from pathlib import Path; p=Path('ignored/cache'); "
                       "p.mkdir(parents=True); (p/'result').write_text('cache'); "
                       "(p/'result').unlink()")
        self.passed()

    def test_new_ignored_cache_directory_requires_prewarming(self):
        self.configure("from pathlib import Path; Path('ignored').mkdir(exist_ok=True)")
        self.assertNotEqual(self.cli("run").returncode, 0)
        self.assertFalse(self.receipt().exists())
        self.passed()

    def test_restored_index_transition_invalidates(self):
        self.configure("from pathlib import Path; import subprocess; p=Path('.git/index'); "
                       "original=p.read_bytes(); subprocess.run(['git','update-index','--force-remove','source.txt'], check=True); "
                       "p.write_bytes(original)")
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.receipt().exists())

    def test_restored_head_transition_invalidates(self):
        self.configure("import subprocess; head=subprocess.check_output(['git','rev-parse','HEAD']).strip(); "
                       "subprocess.run(['git','commit','--allow-empty','-qm','temporary'],check=True); "
                       "subprocess.run(['git','update-ref','HEAD',head],check=True)")
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.receipt().exists())

    def test_post_publication_read_failure_removes_receipt(self):
        replace = os.replace
        for reader in ("source_state", "source_generation"):
            with self.subTest(reader=reader):
                reader_patch = None
                def publish_then_break_reads(*args):
                    nonlocal reader_patch
                    replace(*args)
                    reader_patch = patch.object(validation, reader, side_effect=OSError("post-publication read failed"))
                    reader_patch.start()
                try:
                    with patch.object(validation.os, "replace", side_effect=publish_then_break_reads):
                        with self.assertRaisesRegex(OSError, "post-publication read failed"):
                            validation.run(self.root, "fixture")
                finally:
                    if reader_patch:
                        reader_patch.stop()
                self.assertFalse(self.receipt().exists())

    def selected_shebang_package_change(self, runtime_directory, env_shebang=False):
        (self.root / ".agents/validation.json").unlink()
        (self.root / "pyproject.toml").write_text("[project]\nname='fixture'\nversion='0.0.0'\n")
        (self.root / ".gitignore").write_text(".venv/\nignored/\n")
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(self.root / runtime_directory)], check=True)
        python = self.root / runtime_directory / "bin/python"
        site = Path(subprocess.check_output([str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"], text=True).strip())
        metadata = site / "fixture_runtime-1.0.dist-info"
        metadata.mkdir()
        info = metadata / "METADATA"
        info.write_text("Metadata-Version: 2.1\nName: fixture-runtime\nVersion: 1.0\n")
        bin_directory = self.root / ".venv/bin"
        bin_directory.mkdir(parents=True, exist_ok=True)
        shebang = "#!/usr/bin/env -S " + str(python) if env_shebang else "#!" + str(python)
        for name, body in (("ruff", "#!/bin/sh\nexit 0\n"), ("pytest", shebang + "\nimport importlib.metadata\nassert importlib.metadata.version('fixture-runtime') == '1.0'\n")):
            executable = bin_directory / name
            executable.write_text(body)
            executable.chmod(0o755)
        self.passed()
        info.write_text("Metadata-Version: 2.1\nName: fixture-runtime\nVersion: 2.0\n")
        self.invalid()
        self.assertNotEqual(subprocess.run([str(bin_directory / "pytest")], capture_output=True).returncode, 0)

    def test_selected_venv_shebang_package_change_invalidates(self):
        self.selected_shebang_package_change(".venv")

    def test_selected_nonstandard_shebang_runtime_change_invalidates(self):
        self.selected_shebang_package_change("ignored/runtime")

    def test_selected_env_shebang_runtime_change_invalidates(self):
        self.selected_shebang_package_change("ignored/runtime", env_shebang=True)

    def test_executable_shell_commit_syntax_fails_closed(self):
        commands = ["if true; then git commit -m test; fi", "echo `git commit -m test`",
                    "git com\\\nmit -m test", "command -- git commit -m test",
                    "env -u SOMETHING git commit -m test", 'echo "$(git commit -m test)"',
                    "while true; do git commit -m test; break; done",
                    "/usr/bin/env -u SOMETHING git commit -m test",
                    "time git commit -m x", "nice git commit -m x", "timeout 10 git commit -m x",
                    "nice -n 10 git commit -m x", "timeout -s TERM 10 git commit -m x",
                    "nohup git commit -m x", "env --split-string='git commit -m x'",
                    "env -Sgit commit -m x", "eval git commit -m test",
                    "printf test | xargs git commit -m"]
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(validation.commit_command(command), (True, False))
                self.assertEqual(validation.pre_commit({"cwd": str(self.root), "tool_input": {"command": command}}), 2)

    def test_literal_commit_text_is_not_executable(self):
        for command in ['echo "git commit"', "grep -r 'git commit' .", "git grep commit",
                        "echo '`git commit`'", "echo '$(git commit)'", 'echo "\\`git commit\\`"']:
            with self.subTest(command=command):
                self.assertEqual(validation.commit_command(command), (False, False))

    def test_python_requires_ruff_and_pytest_without_silent_skip(self):
        (self.root / ".agents/validation.json").unlink()
        (self.root / "pyproject.toml").write_text("[project]\nname='fixture'\nversion='0.0.0'\n")
        shim = self.root.parent / "tools"
        shim.mkdir()
        (shim / "git").symlink_to(shutil.which("git"))
        result = subprocess.run([sys.executable, "-S", str(MODULE), "run", "--root", str(self.root)],
                                env=dict(os.environ, PATH=str(shim)), text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required Python check unavailable", result.stderr)
        self.assertFalse(self.receipt().exists())

    def test_python_empty_test_suite_exit_is_failure(self):
        (self.root / ".agents/validation.json").unlink()
        (self.root / "pyproject.toml").write_text("[project]\nname='fixture'\nversion='0.0.0'\n")
        (self.root / ".gitignore").write_text(".venv/\n")
        bindir = self.root / ".venv/bin"
        bindir.mkdir(parents=True)
        for name, code in (("ruff", 0), ("pytest", 5)):
            executable = bindir / name
            executable.write_text("#!/bin/sh\nexit " + str(code) + "\n")
            executable.chmod(0o755)
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pytest (exit 5)", result.stderr)
        self.assertFalse(self.receipt().exists())

    def test_missing_failed_or_altered_check_evidence_rejected(self):
        self.passed()
        valid = self.receipt().read_text()
        for alteration in ("missing", "failed", "command", "runtime", "production", "elapsed"):
            with self.subTest(alteration=alteration):
                data = json.loads(valid)
                if alteration == "missing":
                    data["checks"].pop()
                if alteration == "failed":
                    data["checks"][0]["exit_code"] = 1
                if alteration == "command":
                    data["checks"][0]["argv"] = ["true"]
                if alteration == "runtime":
                    data.pop("runtime")
                if alteration == "production":
                    data["production"] = False
                if alteration == "elapsed":
                    data["checks"][0].pop("elapsed_seconds")
                self.receipt().write_text(json.dumps(data))
                self.invalid()

    def test_legacy_and_malformed_receipts_rejected(self):
        for text in ("waves_passed=2\n", "{}", "[]", "null", "{"):
            self.receipt().write_text(text)
            self.invalid()

    def test_external_symlink_is_not_followed(self):
        outside = self.root.parent / "outside"
        outside.write_text("private outside contents")
        (self.root / "external").symlink_to(outside)
        self.passed()
        outside.write_text("private contents changed")
        self.assertEqual(self.cli("check").returncode, 0)
        (self.root / "external").unlink()
        (self.root / "external").symlink_to("elsewhere")
        self.invalid()

    def test_receipt_symlink_never_overwrites_target(self):
        outside = self.root.parent / "outside"
        outside.write_text("preserve")
        self.receipt().symlink_to(outside)
        self.invalid()
        self.passed()
        self.assertEqual(outside.read_text(), "preserve")
        self.assertFalse(self.receipt().is_symlink())

    def test_sensitive_input_blocks_without_reading_content(self):
        (self.root / ".env.private").write_text("DO_NOT_PRINT_THIS")
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("DO_NOT_PRINT_THIS", result.stdout + result.stderr)

    def loam_fixture(self):
        (self.root / "copier.yml").write_text("{}")
        (self.root / "seed").mkdir()
        (self.root / "bin").mkdir()
        gate = self.root / "bin/verify-template.sh"
        gate.write_text("#!/bin/sh\nclaude && codex && copier\n")
        gate.chmod(0o755)
        tools = self.root.parent / "runtime-tools"
        tools.mkdir()
        for name in ("claude", "codex", "copier", "uvx", "ruff"):
            executable = tools / name
            executable.write_text("#!" + sys.executable + "\nprint('fixture 1.0')\n")
            executable.chmod(0o755)
        for name in ("git", "python3", "bash"):
            (tools / name).symlink_to(shutil.which(name))
        return tools, dict(os.environ, PATH=str(tools))

    def test_loam_uses_full_gate_once_without_generic_pytest(self):
        _, env = self.loam_fixture()
        self.passed(env)
        data = json.loads(self.receipt().read_text())
        self.assertEqual([c["name"] for c in data["checks"]].count("loam-full"), 1)
        self.assertFalse(any("pytest" in c["name"] for c in data["checks"]))

    def test_loam_native_and_copier_upgrade_or_removal_invalidates(self):
        tools, env = self.loam_fixture()
        for name in ("claude", "codex", "copier", "ruff"):
            with self.subTest(tool=name):
                self.passed(env)
                tool = tools / name
                original = tool.read_bytes()
                try:
                    tool.write_text("#!" + sys.executable + "\nraise SystemExit(1)\n")
                    self.invalid(env)
                    tool.write_bytes(original)
                    self.passed(env)
                    tool.unlink()
                    self.invalid(env)
                finally:
                    tool.write_bytes(original)
                    tool.chmod(0o755)

    def test_npm_runtime_refuses_secret_paths_before_hashing(self):
        package = self.root.parent / "npm-package"
        package.mkdir()
        (package / "package.json").write_text('{"name":"@openai/codex","version":"1"}')
        launcher = package / "codex.js"
        launcher.write_text("// harmless fixture")
        secret = package / ".env.private"
        secret.write_text("fixture value, not a real secret")
        with patch.object(validation, "file_identity", wraps=validation.file_identity) as reader:
            with self.assertRaises(validation.ValidationError):
                validation.npm_runtime_identity(launcher, "@openai/codex")
            self.assertNotIn(secret, [call.args[0] for call in reader.call_args_list])

    def test_loam_uvx_runtime_requires_resolved_copier(self):
        tools, env = self.loam_fixture()
        (tools / "copier").unlink()
        result = self.cli("run", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Copier runtime", result.stderr)
        self.assertFalse(self.receipt().exists())

    def test_loam_missing_native_override_cannot_mint_or_reuse(self):
        tools, env = self.loam_fixture()
        self.passed(env)
        override = dict(env, LOAM_ALLOW_MISSING_AGENT_CLIS="1")
        self.invalid(override)
        (tools / "claude").unlink()
        (self.root / "bin/verify-template.sh").write_text("#!/bin/sh\nexit 0\n")
        self.assertNotEqual(self.cli("run", override).returncode, 0)
        self.assertFalse(self.receipt().exists())

    def test_loam_unknown_native_shell_launcher_refuses_evidence(self):
        tools, env = self.loam_fixture()
        (tools / "claude").write_text("#!/bin/sh\nexit 0\n")
        result = self.cli("run", env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("launcher", result.stderr)

    def test_loam_uv_python_trampoline_binds_sibling_interpreter(self):
        tools, env = self.loam_fixture()
        for name in ("dirname", "realpath"):
            (tools / name).symlink_to(shutil.which(name))
        (tools / "python").symlink_to(sys.executable)
        trampoline = "#!/bin/sh\n'''exec' \"$(dirname -- \"$(realpath -- \"$0\")\")\"/'python' \"$0\" \"$@\"\n' '''\n"
        (tools / "copier").write_text(trampoline + "print('fixture Copier 1.0')\n")
        self.passed(env)
        (tools / "python").unlink()
        self.invalid(env)

    def test_configured_shell_wrapper_requires_runtime_declaration(self):
        helper = self.root.parent / "helper"
        helper.write_text("#!" + sys.executable + "\nprint('helper')\n")
        helper.chmod(0o755)
        wrapper = self.root / "check.sh"
        wrapper.write_text("#!/bin/sh\nexec '" + str(helper) + "'\n")
        wrapper.chmod(0o755)
        check = {"name": "wrapped", "argv": [str(wrapper)]}
        config = self.root / ".agents/validation.json"
        config.write_text(json.dumps({"schema": 1, "checks": [check]}))
        result = self.cli("run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime_dependencies", result.stderr)
        check["runtime_dependencies"] = [str(helper)]
        config.write_text(json.dumps({"schema": 1, "checks": [check]}))
        self.passed()
        helper.write_text("#!" + sys.executable + "\nraise SystemExit(1)\n")
        self.invalid()

    def test_configured_shell_builtins_can_declare_no_external_runtime(self):
        config = self.root / ".agents/validation.json"
        config.write_text(json.dumps({"schema": 1, "checks": [
            {"name": "builtins", "argv": ["sh", "-c", "printf checked"], "runtime_dependencies": []}]}))
        self.passed()

    def test_loam_codex_npm_payload_and_node_changes_invalidate(self):
        tools, env = self.loam_fixture()
        package = tools / "node_modules/@openai/codex"
        (package / "bin").mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"name": "@openai/codex", "version": "1.0",
                                                       "optionalDependencies": {"@openai/codex-fixture": "1.0"}}))
        payload = tools / "node_modules/@openai/codex-fixture/vendor/codex"
        payload.parent.mkdir(parents=True)
        payload.write_text("native fixture implementation")
        (payload.parents[1] / "package.json").write_text('{"name":"@openai/codex-fixture","version":"1.0"}')
        launcher = package / "bin/codex.js"
        launcher.write_text("#!/usr/bin/env node\n// fixture launcher\n")
        launcher.chmod(0o755)
        (tools / "codex").unlink()
        (tools / "codex").symlink_to(launcher)
        (tools / "node").write_text("#!" + sys.executable + "\nprint('fixture node 1.0')\n")
        (tools / "node").chmod(0o755)
        self.passed(env)
        payload.write_text("replacement implementation")
        self.invalid(env)
        self.passed(env)
        payload.unlink()
        self.invalid(env)
        payload.write_text("restored implementation")
        self.passed(env)
        (tools / "node").write_text("#!" + sys.executable + "\nprint('fixture node 2.0')\n")
        self.invalid(env)


if __name__ == "__main__":
    unittest.main()
