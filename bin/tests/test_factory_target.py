"""`bin/factory -C <repo>` works on another repository while Loam stays the factory home (F8 step 1).

Target resolution, the runs root keyed by <owner>__<repo>, the launch gate per target, the standing
do-not-touch list, lint's tree, and the timer's cron line, on throwaway repositories whose origin is a
GitHub URL that is never contacted. `bin/factory` is sourced (FACTORY_SOURCED=1) or run as `stop`;
gh and crontab are shell stubs. No network, no tmux, no `claude`.
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
# A run inside the factory exports FACTORY_ROOT, and the runner exports the toolchain; the tests set their own.
INHERITED = ("FACTORY_ROOT", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER")
STANDING = "# Standing\n\n## Standing do-not-touch list\n\n- `.claude/settings.json` and every deny list\n- `bin/check`\n\n## Other\n\n- `src/widget.py`\n"


def clean_env(**extra: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in INHERITED}
    return {**env, **extra}


def sourced(script: str, **env: str) -> subprocess.CompletedProcess[str]:
    """Run `script` in a bash that has sourced bin/factory, with ROOT pinned to this checkout."""
    return subprocess.run(
        ["bash", "-c", f". bin/factory\n{script}"],
        cwd=ROOT, env=clean_env(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), **env),
        capture_output=True, text=True, check=False,
    )


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def repo(path: pathlib.Path, origin: str | None, files: dict[str, str]) -> pathlib.Path:
    """A committed repository on main with `files`; bin/* files are executable."""
    path.mkdir(parents=True)
    git("init", "-q", "-b", "main", cwd=path)
    if origin:
        git("remote", "add", "origin", origin, cwd=path)
    for name, text in files.items():
        f = path / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
        if name.startswith("bin/"):
            f.chmod(0o755)
    git("add", "-A", cwd=path)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base", cwd=path)
    return path.resolve()


class TargetTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        self.runs = top / "runs"
        self.proj = repo(top / "widget", "git@github.com:acme/widget.git", {
            "bin/check": "#!/usr/bin/env bash\nexit 0\n", "bin/widget-tool": "#!/usr/bin/env bash\n",
            ".claude/settings.json": "{}\n", "docs/factory/STANDING.md": STANDING, "src/widget.py": "",
        })
        self.bare = repo(top / "bare", None, {"README.md": "x\n"})
        self.nocheck = repo(top / "nocheck", "https://github.com/acme/nocheck", {"README.md": "x\n"})

    def target(self, repo_dir: pathlib.Path | None, script: str = "", **env: str) -> subprocess.CompletedProcess[str]:
        pick = f'use_target "{repo_dir}" || echo use_target-failed\n' if repo_dir else ""
        return sourced(pick + script, FACTORY_RUNS_ROOT=str(self.runs), **env)

    def values(self, repo_dir: pathlib.Path | None) -> list[str]:
        proc = self.target(repo_dir, 'printf "%s\\n" "$TARGET" "$TARGET_IS_LOAM" "$RUNS_ROOT" "$MAIN_CHECKOUT"')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.splitlines()

    def test_default_target_is_loam_with_the_runs_root_unchanged(self) -> None:
        common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=ROOT)
        self.assertEqual(self.values(None), [str(ROOT), "1", str(self.runs), str(pathlib.Path(common).parent)])

    def test_another_repo_gets_its_own_runs_root(self) -> None:
        self.assertEqual(self.values(self.proj), [str(self.proj), "0", str(self.runs / "acme__widget"), str(self.proj)])

    def test_a_worktree_of_the_target_keeps_its_main_checkout(self) -> None:
        wt = self.proj.parent / "widget-12"
        git("worktree", "add", "-q", "-b", "factory/12", str(wt), cwd=self.proj)
        self.assertEqual(self.values(wt), [str(wt.resolve()), "0", str(self.runs / "acme__widget"), str(self.proj)])

    def test_slug_from_every_github_url_form(self) -> None:
        for url in ("git@github.com:acme/widget.git", "https://github.com/acme/widget.git",
                    "https://github.com/acme/widget", "ssh://git@github.com/acme/widget.git"):
            git("remote", "set-url", "origin", url, cwd=self.proj)
            self.assertEqual(self.target(self.proj, "target_slug").stdout.strip(), "acme__widget", url)

    def test_a_repo_with_no_github_origin_is_refused(self) -> None:
        self.assertIn("use_target-failed", self.target(self.bare).stdout)
        git("remote", "add", "origin", "https://gitlab.com/acme/bare.git", cwd=self.bare)
        self.assertIn("use_target-failed", self.target(self.bare).stdout)
        for where in (self.bare, self.bare.parent):  # no GitHub origin; not a git checkout at all
            proc = subprocess.run([str(ROOT / "bin/factory"), "-C", str(where), "status"], cwd=ROOT,
                                  env=clean_env(FACTORY_RUNS_ROOT=str(self.runs)), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertIn("is not a git checkout, or is another repository with no GitHub origin", proc.stderr)

    def test_dash_C_before_or_after_the_subcommand_keys_stop_by_repo(self) -> None:
        loam_run, widget_run = self.runs / "12" / "aaaaaaaa", self.runs / "acme__widget" / "12" / "bbbbbbbb"
        for d in (loam_run, widget_run):
            d.mkdir(parents=True)
        for args in (["-C", str(self.proj), "stop", "12"], ["stop", "-C", str(self.proj), "12"]):
            proc = subprocess.run([str(ROOT / "bin/factory"), *args], cwd=ROOT,
                                  env=clean_env(FACTORY_RUNS_ROOT=str(self.runs)), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((widget_run / "FACTORY_STOP").exists(), args)
            self.assertFalse((loam_run / "FACTORY_STOP").exists(), args)
            (widget_run / "FACTORY_STOP").unlink()
        proc = subprocess.run([str(ROOT / "bin/factory"), "stop", "12"], cwd=ROOT,
                              env=clean_env(FACTORY_RUNS_ROOT=str(self.runs)), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((loam_run / "FACTORY_STOP").exists())
        self.assertFalse((widget_run / "FACTORY_STOP").exists())

    def test_the_frozen_copy_gets_the_target_on_its_command_line(self) -> None:
        frozen = self.runs / "run" / "frozen"
        frozen.mkdir(parents=True)
        (frozen / "factory").write_text('#!/usr/bin/env bash\necho "args: $*"\n')
        (frozen / "factory").chmod(0o755)
        proc = self.target(self.proj, f'RUN="{frozen.parent}"; SRC=12; exec_frozen')
        self.assertEqual(proc.stdout.strip(), f"args: -C {self.proj} run 12", proc.stderr)

    def test_gate_is_the_toolchain_for_loam_and_bin_check_for_another_target(self) -> None:
        loam = self.target(None, "assert_target_ready; echo rc=$?")
        self.assertIn("rc=1", loam.stdout)
        self.assertIn("LOAM_FACTORY_TOOLCHAIN", loam.stderr)
        self.assertIn("rc=0", self.target(self.proj, "assert_target_ready; echo rc=$?").stdout)
        nocheck = self.target(self.nocheck, "assert_target_ready; echo rc=$?")
        self.assertIn("rc=1", nocheck.stdout)
        self.assertIn("has no executable bin/check", nocheck.stderr)

    def test_next_parks_by_the_targets_own_runs_without_the_toolchain(self) -> None:
        body = "the same body"
        key = hashlib.sha256(body.encode()).hexdigest()[:8]
        line = f"7 {base64.b64encode(body.encode()).decode()}"
        stubs = ("claude_logged_in() { :; }; "
                 f"gh() {{ case $1 in repo) echo acme/widget ;; api) echo '{line}' ;; esac; }}; cmd_next --dry-run")

        def status(where: pathlib.Path, text: str) -> None:
            (where / key).mkdir(parents=True)
            (where / key / "status").write_text(text + "\n")
            (where / key / "launched").write_text("1\n")

        status(self.runs / "7", "abandon")  # Loam's #7 must not park the widget's #7
        proc = self.target(self.proj, stubs)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        status(self.runs / "acme__widget" / "7", "abandon")
        proc = self.target(self.proj, stubs)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("parked #7: last run exited abandon", proc.stderr)

    def test_standing_list_comes_from_the_target(self) -> None:
        loam = self.target(None, "standing_list").stdout.split()
        self.assertIn("seed/bin/", loam)
        self.assertIn("VERSION", loam)
        # sort -u orders by the locale; compare as a sorted list.
        self.assertEqual(sorted(self.target(self.proj, "standing_list").stdout.split()), [".claude/settings.json", "bin/check"])
        self.assertEqual(self.target(self.nocheck, "standing_list; echo rc=$?").stdout.split(), ["rc=0"])

    def test_lint_paths_resolve_in_the_target(self) -> None:
        body = "BODY=$'## Do not touch\\n\\n- `bin/widget-tool`\\n'; SRC=t; ERRS=0; check_paths; echo errs=$ERRS"
        self.assertIn("errs=1", self.target(None, body).stdout)
        self.assertIn("errs=0", self.target(self.proj, body).stdout)

    def test_next_install_keeps_one_cron_line_per_target(self) -> None:
        cron = self.runs.parent / "crontab"
        stub = f'crontab() {{ if [ "$1" = -l ]; then cat "{cron}" 2> /dev/null; else cat > "{cron}.new"; mv "{cron}.new" "{cron}"; fi; }}\n'
        self.assertEqual(self.target(None, stub + "cmd_next --install").returncode, 0)
        for _ in range(2):
            proc = self.target(self.proj, stub + "cmd_next --install")
            self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = cron.read_text().splitlines()
        self.assertEqual(lines, [f"*/10 * * * * bash -lc 'cd {ROOT} && bin/factory next'",
                                 f"*/10 * * * * bash -lc 'cd {ROOT} && bin/factory -C {self.proj} next'"])


if __name__ == "__main__":
    unittest.main()
