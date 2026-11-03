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
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
# A run inside the factory exports FACTORY_ROOT, and the runner exports the toolchain; the tests set their own.
INHERITED = ("FACTORY_ROOT", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER")
STANDING = "# Standing\n\n## Standing do-not-touch list\n\n- `.claude/settings.json` and every deny list\n- `bin/check`\n\n## Other\n\n- `src/widget.py`\n"
# next reads every candidate's last editor in one GraphQL call (#598): #7, never edited.
GQL = '{"data": {"repository": {"i7": {"editor": null, "lastEditedAt": null}}}}'


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
        # bin/check but no STANDING.md; the tests below write an empty or untracked-only one into it.
        self.nolist = repo(top / "nolist", "https://github.com/acme/nolist.git", {"bin/check": "#!/usr/bin/env bash\n"})
        self.gh_log = top / "gh.log"
        # A fork: gh's default repository would be the parent, so any call that reaches it without -R is caught.
        self.gh_stub = (f'gh() {{ printf "%s\\n" "$*" >> "{self.gh_log}"; '
                        'case "$1 $2" in "repo view") echo parent/widget ;; "issue view") echo "# t" ;; '
                        '"api graphql") echo \'{"data": {"repository": {"issue": {"body": "# t", '
                        '"author": {"login": "SamyakJhaveri"}, "editor": null}}}}\' ;; esac; }\n')

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

    def test_the_frozen_copy_gets_another_target_on_its_command_line_and_loam_none(self) -> None:
        frozen = self.runs / "run" / "frozen"
        frozen.mkdir(parents=True)
        (frozen / "factory").write_text('#!/usr/bin/env bash\necho "args: $*"\n')
        (frozen / "factory").chmod(0o755)
        proc = self.target(self.proj, f'RUN="{frozen.parent}"; SRC=12; exec_frozen')
        self.assertEqual(proc.stdout.strip(), f"args: -C {self.proj} run 12", proc.stderr)
        # A Loam run re-execs as before F8, so a resumed run's pre-F8 frozen copy never sees -C.
        proc = self.target(None, f'RUN="{frozen.parent}"; SRC=12; exec_frozen')
        self.assertEqual(proc.stdout.strip(), "args: run 12", proc.stderr)

    def test_gate_is_the_toolchain_for_loam_and_bin_check_for_another_target(self) -> None:
        loam = self.target(None, "assert_target_ready; echo rc=$?")
        self.assertIn("rc=1", loam.stdout)
        self.assertIn("LOAM_FACTORY_TOOLCHAIN", loam.stderr)
        self.assertIn("rc=0", self.target(self.proj, "assert_target_ready; echo rc=$?").stdout)
        nocheck = self.target(self.nocheck, "assert_target_ready; echo rc=$?")
        self.assertIn("rc=1", nocheck.stdout)
        self.assertIn("has no executable bin/check", nocheck.stderr)

    def test_another_target_without_standing_entries_is_refused_and_status_fails(self) -> None:
        standing = self.nolist / "docs/factory/STANDING.md"
        status = "claude() { :; }; gh() { :; }; codex() { :; }; precondition_lines"
        for text in (None, "## Standing do-not-touch list\n\nNothing yet.\n",
                     "## Standing do-not-touch list\n\n- `nowhere/` is not tracked\n"):
            if text is not None:
                standing.parent.mkdir(parents=True, exist_ok=True)
                standing.write_text(text)
            gate = self.target(self.nolist, "assert_target_ready; echo rc=$?")
            self.assertIn("rc=1", gate.stdout, text)
            self.assertIn(f"{standing} is missing or has no tracked path", gate.stderr, text)
            self.assertIn(f"FAIL {standing} is missing or has no tracked path", self.target(self.nolist, status).stdout, text)
        self.assertIn("PASS standing do-not-touch list: 2 paths", self.target(self.proj, status).stdout)

    def test_every_gh_call_names_the_origin_repository(self) -> None:
        # next's two frontier listings print the same fields: number, author, body (`-` if empty), blockers, assignees.
        fields = ('"\\(.number) \\(.user.login) \\(.body // "" | @base64 | if . == "" then "-" else . end) '
                  '\\(.issue_dependencies_summary.blocked_by // "?") '
                  '\\([(.assignees // [])[].login] | join(",") | if . == "" then "-" else . end)"')
        self.target(self.proj, self.gh_stub + "lint 5")  # the stub body fails lint; only its gh call matters
        load = self.target(self.proj, self.gh_stub + "load_ticket 5; echo REPO=$REPO")
        self.assertIn("REPO=acme/widget", load.stdout, load.stderr)
        stat = self.target(self.proj, self.gh_stub + "precondition_lines() { :; }; cmd_status > /dev/null")
        nxt = self.target(self.proj, self.gh_stub + "claude_logged_in() { :; }; claude_version_ok() { :; }; cmd_next --dry-run")
        for proc in (stat, nxt):
            self.assertEqual(proc.returncode, 0, proc.stderr)
        calls = self.gh_log.read_text().splitlines()
        self.assertEqual(calls, [
            "issue view 5 -R acme/widget --json body -q .body",
            # load_ticket reads the body with its author and editor in one call, owner and name from the origin (#389).
            "api graphql -f owner=acme -f name=widget -F number=5 -f query=query($owner: String!, $name: String!, "
            "$number: Int!) { repository(owner: $owner, name: $name) { issue(number: $number) { body author { login } "
            "editor { login } lastEditedAt } } }",
            "pr list -R acme/widget --json number,headRefName,title --jq "
            '.[] | select(.headRefName | startswith("factory/")) | "  #\\(.number) \\(.headRefName) \\(.title)"',
            # Every ready issue, assigned or blocked too, so next can name why it passes one over (#617).
            "api repos/acme/widget/issues?labels=ready-for-agent&state=open&per_page=100 --paginate --jq "
            'sort_by(.number)[] | select(.pull_request == null) | ' + fields,
            # /issues has no repository in its path; the runner's own issues are kept to this one by the filter.
            "api /issues?filter=assigned&labels=ready-for-agent&state=open&per_page=100 --paginate --jq "
            '.[] | select(.pull_request == null) | select((.repository.full_name // "" | ascii_downcase) == "acme/widget")'
            ' | ' + fields])

    def test_next_parks_by_the_targets_own_runs_without_the_toolchain(self) -> None:
        # next launches only a body that passes lint (#314); gh returns the body with no trailing newline.
        body = (ROOT / "bin/tests/fixtures/clean-ticket.md").read_text().rstrip("\n")
        key = hashlib.sha256(body.encode()).hexdigest()[:8]
        line = f"7 SamyakJhaveri {base64.b64encode(body.encode()).decode()}"
        stubs = ("claude_logged_in() { :; }; claude_version_ok() { :; }; "
                 f"gh() {{ case $1$2 in apigraphql) echo '{GQL}' ;; api*) echo '{line}' ;; esac; }}; cmd_next --dry-run")

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

    def cron_stub(self) -> tuple[pathlib.Path, str]:
        cron = self.runs.parent / "crontab"
        return cron, f'crontab() {{ if [ "$1" = -l ]; then cat "{cron}" 2> /dev/null; else cat > "{cron}.new"; mv "{cron}.new" "{cron}"; fi; }}\n'

    def install(self, repo_dir: pathlib.Path | None, home: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
        """`next --install` over the stub crontab, with a scratch HOME, since install creates its state directory."""
        return self.target(repo_dir, self.cron_stub()[1] + "cmd_next --install", HOME=str(home or self.runs.parent / "home"))

    def cron_line(self, cmd: str, slug: str = "") -> str:
        """The live line's shape (jhaveris's), for the scratch HOME `install` runs with."""
        state = f"{self.runs.parent}/home/.local/state/loam-factory"
        tag = f"-{slug}" if slug else ""
        return (f"*/10 * * * * bash -lc 'cd {ROOT} && FACTORY_DAILY_BUDGET_USD=1000000 FACTORY_GRADER_BUDGET_USD=1000000 "
                f"FACTORY_MAX_PARALLEL=2 flock -n -o {state}/next{tag}.lock {cmd}' >> {state}/next{tag}.log 2>&1")

    def test_next_install_keeps_one_cron_line_per_target(self) -> None:
        cron, _ = self.cron_stub()
        cron.write_text("*/10 * * * * bash -lc 'cd /srv/old/loam && bin/factory next'\n")
        self.assertEqual(self.install(None).returncode, 0)
        once = cron.read_text()
        self.assertEqual(self.install(None).returncode, 0)
        self.assertEqual(cron.read_text(), once)
        for _ in range(2):
            proc = self.install(self.proj)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        first = cron.read_text()
        self.assertEqual(first.splitlines(), [self.cron_line("bin/factory next"),
                                              self.cron_line(f"bin/factory -C {self.proj} next", "acme__widget")])
        self.assertEqual(self.install(None).returncode, 0)
        self.assertEqual(cron.read_text().splitlines(), first.splitlines()[1:] + first.splitlines()[:1])

    def test_next_install_keeps_comments_and_other_lines(self) -> None:
        cron, _ = self.cron_stub()
        before = ["# disabled 2026-10-25: */10 * * * * bash -lc 'cd /srv/old && bin/factory next'", "0 4 * * * /usr/bin/true",
                  "*/10 * * * * bash -lc 'cd /srv/widget && bin/factory -C /srv/widget next'"]
        cron.write_text("\n".join(before) + "\n")
        self.assertEqual(self.install(None).returncode, 0)
        self.assertEqual(cron.read_text().splitlines(), [*before, self.cron_line("bin/factory next")])

    def test_next_install_two_targets_keep_each_other_and_loam(self) -> None:
        cron, _ = self.cron_stub()
        gadget = repo(self.runs.parent / "gadget", "https://github.com/acme/gadget.git", {"README.md": "x\n"})
        loam = self.cron_line("bin/factory next")
        cron.write_text(f"0 4 * * * /usr/bin/true\n{loam}\n")
        for d in (self.proj, gadget, self.proj, gadget):
            proc = self.install(d)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(cron.read_text().splitlines(), [
            "0 4 * * * /usr/bin/true", loam,
            self.cron_line(f"bin/factory -C {self.proj} next", "acme__widget"),
            self.cron_line(f"bin/factory -C {gadget} next", "acme__gadget")])

    def test_next_install_refuses_a_path_the_cron_line_cannot_carry(self) -> None:
        cron, _ = self.cron_stub()
        before = "*/10 * * * * bash -lc 'cd /srv/old/loam && bin/factory next'\n"
        for ch in "|&% '(":
            cron.write_text(before)
            home = self.runs.parent / f"h{ch}x"
            proc = self.install(None, home)
            self.assertNotEqual(proc.returncode, 0, ch)
            self.assertIn("cannot carry", proc.stderr)
            self.assertEqual(cron.read_text(), before, ch)

    def test_next_install_creates_the_state_directory(self) -> None:
        proc = self.install(None)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.runs.parent / "home/.local/state/loam-factory").is_dir())

    def test_next_crontab_caps_and_lock_match_the_driver(self) -> None:
        driver = (ROOT / "bin/overnight/driver.sh").read_text()
        caps = re.search(r"(FACTORY_DAILY_BUDGET_USD=\S+ .*?) flock -n -o ", driver)
        lock = re.search(r"^LOCK=(\S+)$", driver, re.M)
        self.assertTrue(caps and lock)
        tmpl = (ROOT / "bin/factory.d/next.crontab").read_text()
        self.assertIn(f"{caps.group(1)} flock -n -o {lock.group(1)} bin/factory next'", tmpl)


if __name__ == "__main__":
    unittest.main()
