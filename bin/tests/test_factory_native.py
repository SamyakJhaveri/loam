"""The worker's shell per target, the run's plugin dir, the reviewer model, and the review and learn hooks (U3).

docs/research/2026-11-12-distbench-priming/design-pick.md, requirement (a) and unit U3. A Loam target keeps today's sandboxed
worker: its frozen settings and its worker and grader argv are compared with what the pre-U3 bin/factory (BASE, read
from git) writes and passes, so the only differences are the ones every target gets (--plugin-dir, availableModels).
Another target gets the native shell: auto mode over its user, project and local tiers, a flag tier with the sandbox
off, no user tier merged in, skills resolved through the user tier's enabledPlugins. Each factory home is a scratch
copy (bin/ and the sam-cc-setup plugin) sourced with FACTORY_SOURCED=1; `claude` is a stub on PATH that records its
argv and answers, so no model is called. No network.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = "83b59cf2"  # the commit U3 branched from: today's bin/factory, the Loam-target reference
HOME_PATHS = ("bin/factory", "bin/factory.d", "bin/claude-account", "bin/alert", "bin/factory-parity",
              "cultivation/marketplace/sam-cc-setup")
GATE = json.loads((ROOT / "bin/factory.d/pstack-gate.hooks.json").read_text())["hooks"]["PreToolUse"]
PLUGIN = "cultivation/marketplace/sam-cc-setup"
TOKEN_VALUE = "sk-ant-fixture-never-printed"

STUB_CLAUDE = r"""#!/usr/bin/env python3
import json, os, pathlib, sys
if "--version" in sys.argv:
    print("2.1.322 (Claude Code)"); sys.exit(0)
cap = pathlib.Path(os.environ["CAPTURE"])
cap.mkdir(exist_ok=True)
stdin = sys.stdin.read()
keys = ("LOAM_CHECKS", "CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE", "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL", "CLAUDE_CONFIG_DIR")
rec = {"argv": sys.argv[1:], "env": {k: os.environ.get(k) for k in keys}, "stdin": stdin}
(cap / ("%02d.json" % len(list(cap.glob("*.json"))))).write_text(json.dumps(rec))
model = sys.argv[sys.argv.index("--model") + 1]
if "stream-json" in sys.argv:
    print(json.dumps({"type": "system", "subtype": "init", "permissionMode": "x"}))
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "num_turns": 1,
                      "modelUsage": {model: {}}}))
else:
    reply = stdin.rsplit("REPLY ", 1)[1].splitlines()[0] if "REPLY " in stdin else '{"verdict": "merge", "findings": []}'
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply,
                      "modelUsage": {model: {}}}))
"""

TICKET = "# t\n\n## Goal and why\n\ng\n\n## Worker\nworker: claude\n{skills}\n## Decisions\nnone\n"
USER = {"attribution": {"commit": ""},
        "env": {"USER_ONLY": "u", "CLAUDE_CODE_SUBAGENT_MODEL": "claude-user-1"},
        "permissions": {"allow": ["Bash(*)", "WebFetch(*)"], "deny": ["Bash(user-rule:*)"], "additionalDirectories": ["~/y"]},
        "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "true"}]}]},
        "sandbox": {"excludedCommands": ["python3 *"]},
        "enabledPlugins": {"pstack@cursor-plugins": True}}
JUDGE_PASS = {"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "evidence": {},
              "fixes": [], "backlog": []}
REVIEW_HIGH = {"verdict": "fix", "findings": [{"severity": "high", "file": "a", "line": 1, "defect": "planted defect",
                                               "fix": "x"}]}


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def without_plugin_dir(argv: list[str]) -> tuple[list[str], list[str]]:
    """(argv with each `--plugin-dir X` pair removed, the X values)."""
    out, dirs, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--plugin-dir":
            dirs.append(argv[i + 1])
            i += 2
        else:
            out.append(argv[i])
            i += 1
    return out, dirs


class Home:
    """A scratch layout: a factory home, a fake HOME, a target repository and its worktree, one run directory."""

    def __init__(self, top: pathlib.Path) -> None:
        self.top = top
        self.home, self.bin, self.cap = top / "home", top / "stub", top / "capture"
        self.home.mkdir()
        self.bin.mkdir()
        (self.bin / "claude").write_text(STUB_CLAUDE)
        (self.bin / "claude").chmod(0o755)
        self.user(USER)
        # pstack:tdd resolves only through an enabled pstack@... key's user-scope installPath.
        self.pstack = top / "pstack"
        (self.pstack / "skills/tdd").mkdir(parents=True)
        (self.pstack / "skills/tdd/SKILL.md").write_text("tdd\n")
        plugins = self.home / ".claude/plugins"
        plugins.mkdir(parents=True, exist_ok=True)
        (plugins / "installed_plugins.json").write_text(json.dumps(
            {"plugins": {"pstack@cursor-plugins": [{"scope": "user", "installPath": str(self.pstack)}]}}))
        self.target = top / "target"
        self.target.mkdir()
        git("init", "-q", "-b", "main", cwd=self.target)
        git("remote", "add", "origin", "https://github.com/o/r.git", cwd=self.target)
        (self.target / "a").write_text("a\n")
        git("add", "a", cwd=self.target)
        git("commit", "-q", "-m", "base", cwd=self.target)
        self.base = git("rev-parse", "HEAD", cwd=self.target)
        self.wt = top / "wt"
        git("worktree", "add", "-q", "-b", "factory/t", str(self.wt), cwd=self.target)
        self.run = top / "run"

    def user(self, settings: dict) -> None:
        (self.home / ".claude").mkdir(exist_ok=True)
        (self.home / ".claude/settings.json").write_text(json.dumps(settings))

    def factory(self, name: str, rev: str | None = None) -> pathlib.Path:
        """A factory home holding HOME_PATHS from this checkout, or from commit rev."""
        dst = self.top / name
        dst.mkdir()
        if rev:
            arch = subprocess.run(["git", "-C", str(ROOT), "archive", rev, *HOME_PATHS], check=True,
                                  capture_output=True).stdout
            subprocess.run(["tar", "-x", "-C", str(dst)], input=arch, check=True)
        else:
            for p in HOME_PATHS:
                (dst / p).parent.mkdir(parents=True, exist_ok=True)
                if (ROOT / p).is_dir():
                    shutil.copytree(ROOT / p, dst / p)
                else:
                    shutil.copy(ROOT / p, dst / p)
        return dst

    def env(self, factory: pathlib.Path, **extra: str) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("FACTORY_", "CLAUDE")) and k not in ("RUN", "LOG", "REPO")}
        env.update(HOME=str(self.home), PATH=f"{self.bin}{os.pathsep}{env['PATH']}", CAPTURE=str(self.cap),
                   CLAUDE_ACCOUNTS_DIR=str(self.top / "accounts"), FACTORY_ROOT=str(factory),
                   FACTORY_RUNS_ROOT=str(self.top / "runs"), GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                   **extra)
        return env

    def sourced(self, factory: pathlib.Path, script: str, loam: bool, skills: str = "",
                **extra: str) -> subprocess.CompletedProcess[str]:
        """Source factory's bin/factory, point it at the target (another target unless loam), set up the run, then
        run script."""
        if self.run.exists():
            subprocess.run(["chmod", "-R", "u+w", str(self.run)], check=True)
            shutil.rmtree(self.run)
        shutil.rmtree(self.cap, ignore_errors=True)
        setup = (("" if loam else f"use_target '{self.target}' || exit 7\n")
                 + f"RUN='{self.run}'; WORKTREE='{self.wt}'; MAIN_CHECKOUT='{self.target}'\n"
                 'LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/worker/decisions.md"\n'
                 'mkdir -p "$RUN/frozen" "$RUN/worker" "$RUN/tasks"; touch "$LEDGER" "$DAILY" "$DECISIONS"\n'
                 'date -u +%s > "$RUN/launched"; date -u +%s > "$RUN/started"\n'
                 f"printf '%s\\n' '{self.base}' > \"$RUN/base.sha\"; : > \"$RUN/round-1.checks\"\n"
                 'IS_FILE=1; KEY=t; BODY="$TICKET_BODY"; TIMEOUT_G=(); ROUND=1\n')
        return subprocess.run(["bash", "-c", f". bin/factory\n{setup}{script}", "bin/factory"], cwd=factory,
                              env=self.env(factory, FACTORY_SOURCED="1", TICKET_BODY=TICKET.format(skills=skills), **extra),
                              capture_output=True, text=True, check=False)

    def calls(self) -> list[dict]:
        return [json.loads(p.read_text()) for p in sorted(self.cap.glob("*.json"))]

    def round_one(self, factory: pathlib.Path, loam: bool, skills: str = "", **extra: str) -> dict:
        """freeze, one worker round and one reviewer call; the frozen files and the two calls."""
        proc = self.sourced(factory, 'freeze && worker_round 1 && run_review 1; echo "done:$?"', loam, skills, **extra)
        assert "done:" in proc.stdout, proc.stdout + proc.stderr + (self.run / "factory.log").read_text()
        worker, grader = self.calls()
        return {"worker": worker, "grader": grader, "proc": proc,
                "settings": (self.run / "frozen/worker-settings.json").read_bytes(),
                "role": (self.run / "frozen/role-settings.json").read_bytes()}


class NativeShellTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.h = Home(pathlib.Path(tmp.name).resolve())
        self.new = self.h.factory("loam-new")

    def test_loam_target_settings_and_argv_match_the_pre_u3_factory(self) -> None:
        if subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", BASE], capture_output=True).returncode:
            self.skipTest(f"{BASE} is not in this clone (shallow)")
        # Both API-billed: the reference's calls always carried --max-budget-usd, which a subscription run drops (Decision 6).
        old = self.h.round_one(self.h.factory("loam-old", BASE), loam=True, ANTHROPIC_API_KEY="sk-ant-test")
        new = self.h.round_one(self.new, loam=True, ANTHROPIC_API_KEY="sk-ant-test")
        # Every target's worker settings gain the pstack gate (U5), the sandboxed shell the DistBench locks grant (owner
        # N25) and the Bash output cap (test_factory_output_cap.py), and nothing else; the rest is the same bytes as jq
        # writes them.
        settings = json.loads(new["settings"])
        self.assertEqual(settings["hooks"].pop("PreToolUse"), GATE)
        self.assertEqual(settings["sandbox"]["filesystem"]["allowWrite"].pop(0), "~/.local/state/distbench/locks")
        self.assertEqual(settings.pop("bashOutputMaxChars"), 20000)
        self.assertEqual(json.dumps(settings, indent=2).encode() + b"\n", old["settings"])
        self.assertIn(b'"sandbox"', old["settings"])  # the reference really is the sandboxed shell
        # Every target's calls load the factory home's sam-cc-setup; nothing else in either argv or env moved.
        for call in ("worker", "grader"):
            argv, dirs = without_plugin_dir(new[call]["argv"])
            self.assertEqual(argv, old[call]["argv"], call)
            self.assertEqual(dirs, [str(self.new / PLUGIN)], call)
            self.assertEqual(new[call]["env"], old[call]["env"], call)
        # The reviewer reads the same evidence, but for the supervisor's `Round 1` header in decisions.md (audit3 F2).
        # (The worker's prompt names the router in the run's plugin dir now.)
        self.assertEqual(new["grader"]["stdin"].replace("\nRound 1\n", "\n", 1), old["grader"]["stdin"])
        # The role settings gain only availableModels, so a Fable reviewer is served Fable.
        role_old, role_new = json.loads(old["role"]), json.loads(new["role"])
        self.assertEqual(role_new.pop("availableModels"), ["claude-opus-5-5", "claude-fable-5-2"])
        self.assertEqual(role_new, role_old)
        # No FACTORY_MEMORY_DIR, no memory view.
        self.assertFalse((self.h.run / "frozen/memory-view.md").exists())
        self.assertNotIn("Memory view", (self.h.run / "round-1.prompt.md").read_text())

    def test_another_target_gets_the_native_shell(self) -> None:
        r = self.h.round_one(self.new, loam=False, skills="skills: pstack:tdd")
        settings = json.loads(r["settings"])
        self.assertEqual(settings["sandbox"], {"enabled": False})
        env = settings["env"]
        for k, v in {"BASH_DEFAULT_TIMEOUT_MS": "5400000", "BASH_MAX_TIMEOUT_MS": "5400000",
                     "DISTBENCH_GATE_CLASS": "factory", "GIT_SSH_COMMAND": "false", "GH_CONFIG_DIR": "/nonexistent",
                     "CLAUDE_CODE_SUBAGENT_MODEL": "claude-opus-5-5", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"}.items():
            self.assertEqual(env.get(k), v, k)
        deny = settings["permissions"]["deny"]
        for rule in ("Bash(rm -rf:*)", "Bash(git push *)", "Bash(git -C * push *)", "Bash(gh:*)", "Bash(pkill:*)",
                     "Bash(killall:*)", "Bash(ssh:*)", "Bash(scp:*)", "Bash(crontab:*)", "WebFetch",
                     "Edit(~/.claude/**)", "Monitor"):
            self.assertIn(rule, deny)
        # The user tier loads natively, so none of it is copied into the flag tier.
        self.assertNotIn("USER_ONLY", env)
        for key in ("attribution", "enabledPlugins", "hooks"):
            self.assertNotEqual(settings.get(key), USER[key], key)
        self.assertNotIn("Bash(user-rule:*)", deny)
        self.assertNotIn("allow", settings["permissions"])
        self.assertEqual(len(settings["hooks"]["Stop"]), 1)  # worker-settings.json's own gate hook
        self.assertEqual(settings["hooks"]["PreToolUse"], GATE)  # the pstack gate (U5), which finds its script by
        self.assertEqual(r["worker"]["env"]["LOAM_CHECKS"], str(self.h.run / "frozen/checks.sh"))  # LOAM_CHECKS
        for name in ("pstack-gate.py", "factory-parity"):
            self.assertTrue((self.h.run / "frozen" / name).is_file(), name)
            self.assertIn(f"  {name}\n", (self.h.run / "frozen/sha256").read_text())
        self.assertEqual(settings["autoCompactWindow"], 450000)
        argv = r["worker"]["argv"]
        pairs = dict(zip(argv, argv[1:]))
        self.assertEqual(pairs["--permission-mode"], "auto")
        self.assertEqual(pairs["--setting-sources"], "user,project,local")
        self.assertEqual(pairs["--settings"], str(self.h.run / "frozen/worker-settings.json"))
        self.assertEqual(pairs["--plugin-dir"], str(self.new / PLUGIN))
        self.assertNotIn("bypassPermissions", argv)
        self.assertEqual((self.h.run / "frozen/plugin-dir").read_text(), f"{self.new / PLUGIN}\n")
        # The skill resolves through the user tier's enabledPlugins, which the frozen file no longer carries.
        self.assertIn(f"read {self.h.pstack}/skills/tdd/SKILL.md", r["worker"]["stdin"])

    def test_native_skill_resolution_reads_the_user_tier(self) -> None:
        # The same ticket with pstack disabled in the user tier names a skill no SKILL.md backs: the run stops.
        self.h.user({**USER, "enabledPlugins": {"pstack@cursor-plugins": False}})
        proc = self.h.sourced(self.new, "freeze && worker_round 1; echo after", loam=False, skills="skills: pstack:tdd")
        self.assertNotIn("after", proc.stdout)
        self.assertIn("ticket-defect", (self.h.run / "status").read_text())
        self.assertEqual(self.h.calls(), [])

    def test_reviewer_model_and_effort_come_from_the_launch(self) -> None:
        r = self.h.round_one(self.new, loam=False, FACTORY_REVIEWER_MODEL="claude-fable-5-2",
                             FACTORY_REVIEWER_EFFORT="high")
        pairs = dict(zip(r["grader"]["argv"], r["grader"]["argv"][1:]))
        self.assertEqual((pairs["--model"], pairs["--effort"]), ("claude-fable-5-2", "high"))
        self.assertEqual(pairs["--plugin-dir"], str(self.new / PLUGIN))
        self.assertIn("claude-fable-5-2", json.loads(r["role"])["availableModels"])
        rows = [json.loads(x) for x in (self.h.run / "ledger.jsonl").read_text().splitlines() if '"role"' in x]
        self.assertEqual([(x["role"], x["model"]) for x in rows if x.get("round") == 1],
                         [("worker", "claude-opus-5-5"), ("reviewer", "claude-fable-5-2")])
        # A reviewer served the model it asked for raises no off-model alert.
        self.assertNotIn("off-model", (self.h.run / "factory.log").read_text())

    def test_memory_view_is_frozen_and_appended_to_each_prompt(self) -> None:
        mem = self.h.top / "memory"
        mem.mkdir()
        (mem / "MEMORY.md").write_text("# MEMORY\n- [Traps](traps.md) - x\n- [Site](https://example.com/a.md) - y\n")
        r = self.h.round_one(self.new, loam=False, FACTORY_MEMORY_DIR=str(mem))
        view = (self.h.run / "frozen/memory-view.md").read_text().splitlines()
        self.assertEqual(view[0], "# Memory view (written for the lead)")
        self.assertRegex(view[1], r"push, merge, rent .* `!` command do not apply")
        self.assertIn(f"- [Traps]({mem}/traps.md) - x", view)
        self.assertIn("- [Site](https://example.com/a.md) - y", view)
        self.assertTrue(r["worker"]["stdin"].rstrip("\n").endswith("\n".join(view).rstrip("\n")))
        self.assertIn("memory-view.md", (self.h.run / "frozen/sha256").read_text())

    def test_another_target_worker_leaves_the_full_gate_to_the_supervisor(self) -> None:
        # L01 (distbench, 13 Nov): a worker spent 109 of 117 min running the full bin/check the supervisor runs anyway.
        prompt = self.h.round_one(self.new, loam=False)["worker"]["stdin"]
        (line,) = [line for line in prompt.splitlines() if "full gate" in line]
        self.assertRegex(line, r"never run `bin/check` yourself")
        self.assertIn(f"`LOAM_HOOK=1 bash {self.h.run}/frozen/checks.sh`", line)
        self.assertIn("focused tests", line)
        # It overrides _common.md's "exactly as the supervisor will", and covers a gate call guard does not skip.
        self.assertIn("this replaces running the done-checks block exactly as the supervisor will", line)
        self.assertIn("calls `bin/check` in any other form, run its other check lines by hand", line)
        self.assertNotIn("full gate", self.h.round_one(self.new, loam=True)["worker"]["stdin"])
        # A large ticket's fan-out integrator gets the same rule through the Workflow args.
        for loam, want in ((False, True), (True, False)):
            proc = self.h.sourced(self.new, 'freeze && WORKER_KIND=claude round=1 && cat "$(build_worker_prompt 1)"', loam,
                                  WORKER_SIZE="large")
            (args,) = re.findall(r"and args `(\{.*\})`\.", proc.stdout)
            self.assertIs(json.loads(args).get("supervisorGate", False), want, proc.stderr)


class LaunchTests(unittest.TestCase):
    """`bin/factory -C <target> run <file>` from a scratch factory home, as the operator launches it."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.h = Home(pathlib.Path(tmp.name).resolve())
        self.new = self.h.factory("loam-new")
        (self.h.target / "bin").mkdir()
        (self.h.target / "bin/check").write_text("#!/bin/sh\n")
        (self.h.target / "bin/check").chmod(0o755)
        (self.h.target / "docs/factory").mkdir(parents=True)
        (self.h.target / "docs/factory/STANDING.md").write_text("## Standing do-not-touch list\n\n- `bin/check`\n")
        git("add", "bin/check", "docs", cwd=self.h.target)
        git("commit", "-q", "-m", "gate", cwd=self.h.target)
        self.ticket = self.h.top / "t1.md"
        self.ticket.write_text(TICKET.format(skills=""))
        claude = self.h.home / ".claude"
        (claude / "rules").mkdir(parents=True)
        (claude / "rules/r.md").write_text("rule\n")
        (claude / "skills/s").mkdir(parents=True)
        (claude / "skills/s/SKILL.md").write_text("s\n")
        (claude / "skills/s/helper.py").write_text("x\n")
        (claude / "skills/synced").mkdir()
        (claude / "skills/synced/manifest.md").write_text("changes every session start\n")
        (claude / "CLAUDE.md").write_text("user rules\n")

    def launch(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(self.new / "bin/factory"), "-C", str(self.h.target), "run", str(self.ticket)],
                              cwd=self.h.top, env=self.h.env(self.new), capture_output=True, text=True, check=False)

    def test_a_user_tier_token_refuses_a_native_launch_and_the_digests_bracket_it(self) -> None:
        self.h.user({**USER, "env": {**USER["env"], "CLAUDE_CODE_OAUTH_TOKEN": TOKEN_VALUE}})
        proc = self.launch()
        self.assertEqual(proc.returncode, 4, proc.stderr)
        (run,) = (self.h.top / "runs/o__r/t1").iterdir()
        self.assertEqual((run / "status").read_text().strip(), "stopped-environment")
        log = (run / "factory.log").read_text()
        self.assertIn("CLAUDE_CODE_OAUTH_TOKEN", log)
        self.assertNotIn(TOKEN_VALUE, log + proc.stdout + proc.stderr)
        self.assertEqual([c for c in self.h.calls() if "-p" in c["argv"]], [])  # no model call
        self.assertFalse((run / "frozen/worker-settings.json").exists())  # refused before the worktree and freeze
        start, end = (run / "shell-digest.start").read_text(), (run / "shell-digest.end").read_text()
        self.assertEqual(start, end)
        lines = dict(reversed(line.split("  ", 1)) for line in start.splitlines())
        claude = self.h.home / ".claude"

        def sha(data: bytes) -> str:
            return hashlib.sha256(data).hexdigest()

        files = {k: v for k, v in lines.items() if k.startswith("/")}
        self.assertEqual(files, {str(p): sha(p.read_bytes()) for p in (
            claude / "settings.json", claude / "CLAUDE.md", claude / "rules/r.md", claude / "skills/s/SKILL.md")})
        t = str(self.h.target)
        status = subprocess.run(["git", "-C", t, "status", "--porcelain"], capture_output=True, check=True).stdout
        self.assertEqual(lines[f"git-status:{t}"], sha(status))
        self.assertEqual(lines[f"git-head:{t}"], git("rev-parse", "HEAD", cwd=self.h.target))
        self.assertEqual(lines[f"git-diff:{t}"], sha(b""))
        self.assertEqual(lines[f"git-untracked:{t}"], sha(b""))
        for kind in ("status", "head", "diff", "untracked"):
            self.assertIn(f"git-{kind}:{self.new}", lines)  # the factory home's four lines, here not a checkout
        self.assertEqual({k for k in lines if k.startswith("checkout:")}, {f"checkout:{t}", f"checkout:{self.new}"})

    def test_the_digest_moves_with_each_change_it_covers(self) -> None:
        claude = self.h.home / ".claude"
        script = ("MAIN_CHECKOUT=$1; shell_digest > \"$2/a\"\n"
                  "echo changed >> \"$1/a\"; echo new > \"$1/untracked\"; echo edited >> \"$HOME/.claude/CLAUDE.md\"\n"
                  "echo x >> \"$HOME/.claude/skills/synced/manifest.md\"; shell_digest > \"$2/b\"")
        subprocess.run(["bash", "-c", f". bin/factory\n{script}", "bin/factory", str(self.h.target), str(self.h.top)],
                       cwd=self.new, env=self.h.env(self.new, FACTORY_SOURCED="1"), check=True)
        a = dict(reversed(x.split("  ", 1)) for x in (self.h.top / "a").read_text().splitlines())
        b = dict(reversed(x.split("  ", 1)) for x in (self.h.top / "b").read_text().splitlines())
        t = str(self.h.target)
        self.assertEqual({k for k in a if a[k] != b[k]},
                         {str(claude / "CLAUDE.md"), f"git-status:{t}", f"git-diff:{t}", f"git-untracked:{t}"})


class ReviewHookTests(unittest.TestCase):
    """graders hands the reviews to verify_round, and a file ticket's run calls learn_run once on its way out; both
    are review.sh's (U4), stubbed here."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.h = Home(pathlib.Path(tmp.name).resolve())
        self.new = self.h.factory("loam-new")

    def graders(self, verify_rc: int) -> tuple[str, str]:
        (self.h.top / "reply.judge").write_text(json.dumps(JUDGE_PASS))
        (self.h.top / "reply.reviewer").write_text(json.dumps(REVIEW_HIGH))
        script = (f"freeze || exit 9; build_evidence() {{ printf 'REPLY %s\\n' \"$(cat '{self.h.top}'/reply.$(basename \"$1\" .md))\"; }}\n"
                  'verify_round() { printf "verify_round %s review=%s fixes=%s\\n" "$1" "$(jq -r ".findings[0].defect" "$RUN/round-$1.review.json")" '
                  f'"$(cat "$RUN/round-$1.fixes" 2> /dev/null)" >> "$RUN/hooks"; return {verify_rc}; }}\n'
                  'graders 1; echo "graders:$?"')
        proc = self.h.sourced(self.new, script, loam=False)
        self.assertIn("graders:", proc.stdout, proc.stderr)
        return proc.stdout.split("graders:")[1].strip(), (self.h.run / "hooks").read_text()

    def test_graders_route_the_reviews_through_verify_round(self) -> None:
        # The reviewer's high finding reaches verify_round in review.json, and run_review queues no fix itself.
        rc, hooks = self.graders(verify_rc=1)
        self.assertEqual((rc, hooks), ("1", "verify_round 1 review=planted defect fixes=\n"))
        # verify_round decides the round: queuing nothing passes it, the reviewer's finding notwithstanding.
        rc, hooks = self.graders(verify_rc=0)
        self.assertEqual((rc, hooks), ("0", "verify_round 1 review=planted defect fixes=\n"))

    def finish_run(self, script: str, is_file: int = 1) -> tuple[subprocess.CompletedProcess[str], str]:
        stub = ('verify_round() { return 0; }\n'
                'learn_run() { printf "learn_run %s|%s status=%s\\n" "$1" "$2" "$(cat "$RUN/status" 2> /dev/null)" >> "$RUN/hooks"; }\n')
        script = (f"freeze || exit 9; chmod u+w \"$RUN/frozen/review.sh\"; printf '%s' '{stub}' > \"$RUN/frozen/review.sh\"\n"
                  f"IS_FILE={is_file}; set_status running; FACTORY_FROZEN=\"$RUN/frozen/factory\" exec_frozen\n{script}")
        proc = self.h.sourced(self.new, script, loam=False)
        hooks = self.h.run / "hooks"
        return proc, hooks.read_text() if hooks.exists() else ""

    def test_a_file_ticket_run_calls_learn_run_on_every_exit_before_its_status(self) -> None:
        for status in ("stuck", "no-change", "stopped-cap", "stopped-environment", "abandon"):
            with self.subTest(status):
                proc, hooks = self.finish_run(f'finish {status} "why it stopped"')
                self.assertEqual(hooks, f"learn_run {status}|why it stopped status=running\n")
                self.assertEqual((self.h.run / "status").read_text().strip(), status)

    def test_a_file_ticket_pr_calls_learn_run_once(self) -> None:
        proc, hooks = self.finish_run('GRADED_SHA=$(git -C "$WORKTREE" rev-parse HEAD); open_pr')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(hooks.count("learn_run pr-opened|file ticket"), 1, hooks)
        self.assertEqual(hooks.count("learn_run"), 1, hooks)

    def test_an_issue_run_and_a_run_before_its_frozen_review_sh_call_no_learn_run(self) -> None:
        self.assertEqual(self.finish_run('finish stuck "x"', is_file=0)[1], "")
        proc = self.h.sourced(self.new, 'freeze; learn_run() { echo called >> "$RUN/hooks"; }; finish stuck "x"',
                              loam=False)
        self.assertFalse((self.h.run / "hooks").exists(), proc.stderr)


if __name__ == "__main__":
    unittest.main()
