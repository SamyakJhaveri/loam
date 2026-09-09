## Ticket

~~~~~~~~~~~~ evidence
# S3: the hot-path cut

Part of #14

Execution ticket. Blocked on S1 and S2 merging and on the sandbox-and-Codex-keys research. Spec: `02-IMPLEMENTATION-SPEC.md` commit 2, plus the `copier.yml` line from commit 4 and the release script from commit 6. Runs alone. This is the largest session; it is one ticket by decision (2026-09-06). If it cannot finish in one context, use the S3a/S3b split recipe in the Risks section of `04-SESSION-PLAN.md`; the naive split is not green-separable.

## Goal and why

The hot-path cut. Delete every hook on a tool matcher and all free-text safety parsing; replace them with native deny rules, a Codex rules file, and the sandbox; one render smoke test replaces the contract and parity checkers. `DESIGN.md` L0, L2, L3, L4, laws 1 to 3. The session edits its own live harness through the `.claude` symlink and must not depend on any hook it deletes.

## Files owned

- `seed/.claude/settings.json` (exact deny list and sandbox block from `DESIGN.md` L0; no allow, no ask, no defaultMode; two hooks only)
- `seed/.claude/hooks/`: delete 13, keep `fable-session-brief.sh` and `post-compact-reinject.sh`
- `seed/.agents/lib/` (delete `validation.py`, `stop_verify.py`, and the directory)
- `seed/.codex/`: delete `hooks.json` and `hooks/pre-tool-policy.py`; add `rules/loam.rules` (about 14 forbidden lines) and the new `config.toml` (`approval_policy = "never"`, one profile extending `:workspace`, `.env*` deny globs, network enabled, no `sandbox_mode` key, `default_permissions` above the first table)
- `seed/agent-parity.toml` (delete); `copier.yml` (drop the dead `agent-parity.toml` `_exclude` line only)
- `seed/bin/check.jinja` and `seed/.github/workflows/check.yml.jinja` (new)
- `bin/`: delete `verify-template.sh`, `verify-template-stages.sh`, `harness-smoke-stages.sh`, `verification_snapshot.py`, `rendered_harness_contract.py`, `agent_parity/`; rewrite `bin/release.sh` (under 40 lines, spec commit 6); add `bin/hygiene`; do not touch `bin/check`
- `bin/tests/`: add `test_render_smoke.py`; delete `test_rendered_harness_contract.py`, `test_seed_claude_hooks.py`, `test_validation_evidence.py`, `test_verification_snapshot.py`, `test_commit_directory.py`, `test_policy_performance.py`, `test_agent_parity.py` (seven; `test_marketplace_skill_routes.py` was S2's); do not touch `test_ci_configuration.py`

Do not touch `CLAUDE.md.jinja`, `AGENTS.md.jinja`, `docs/`, or any `SKILL.md` (S4). Every deletion travels with its importers and tests in the same commit (`grep -rn` the module name first).

### Addendum (2026-09-07, after round 4 stopped stuck on the "correct" row)

Done check 4 (`grep -rn verify-template bin .github` prints nothing) conflicts with the two "do not touch" lines above. Resolution: S3 owns the following minimal edits, which are part of "every deletion travels with its importers":

- `bin/check`: the one comment line that names `verify-template-stages.sh` (comment only, no behaviour change).
- `bin/tests/test_ci_configuration.py`: the two `assertNotIn("verify-template", ...)` guards may be replaced by guards that do not spell the retired name. Nothing else in that file.
- `bin/lib.sh`: comment lines that name a deleted script.
- `bin/harness-smoke.sh`: delete (it is the wrapper for `harness-smoke-stages.sh`).
- `seed/.codex/rules/default.rules`: delete (named in the DELETE block of spec commit 2).
- `seed/.gitignore.jinja`: drop the ignore lines for artefacts of deleted hooks.

These six are in scope. The judge scores "correct" on this list, not on the original "do not touch" lines. Any other path outside this section is still out of scope.

## Rows measured

- Added latency per Bash call in a rendered project (baseline 414 ms, 5 hooks; target 0). Work-sample hook events per Bash call (baseline 8 PreToolUse:Bash starts, of which 1 is the owner's global hook).
- Shipped hooks (15 to 2). Seed hook and lib lines (2309 to under 120). bin plus tests lines (11378 to under 2000). `time bin/check` seconds.

## Done checks

1. `git ls-files seed/.claude/hooks | wc -l` prints 2; `git ls-files seed/.agents/lib seed/.codex/hooks bin/agent_parity` prints nothing.
2. Rendered `.claude/settings.json` has the exact deny list from `DESIGN.md` L0 and the sandbox block, no allow, no ask, no defaultMode, and names only the two kept hooks. Rendered `.codex/rules/loam.rules` lists the same forbidden families; `default_permissions` sits above the first TOML table in the rendered `config.toml`.
3. `pytest -n auto bin/tests` exits 0; `bin/tests/test_render_smoke.py` exists and asserts settings parse, config parse, each hook runs once and exits 0, deny list and rules file share the same forbidden families, and the rendered `bin/check` exists.
4. `bin/hygiene` and `bin/release.sh` exist; the seven `bin/` scripts and `seed/agent-parity.toml` are gone; `grep -rn verify-template bin .github` prints nothing.
5. Live probes in a rendered project, outputs pasted in the PR body (decisions 9 and 10, verified here because this session writes the keys): `rm -rf x` denied; `git checkout .` denied; a write outside the workspace fails; `python3 -c "open('.env').read()"` fails inside the sandbox; `git ls-remote origin` succeeds; a plain `git status` Bash call shows no hook output; the Codex execpolicy probe reports the force families forbidden. If a sandbox or Codex key is wrong, fix it in this PR and cite the doc. If network is blocked, add the `sandbox.network` allowlist from decision 10 and note it for S4's HARNESS.md.
6. `time bin/check` exits 0 on the branch with the seconds recorded; the PR's `check` run is green.
7. Verification protocol below completed; PR body carries the numbers.

## Verification protocol (every execution ticket, before its PR)

1. Measure the rows this ticket owns with the commands in the measurement section of `02-IMPLEMENTATION-SPEC.md`.
2. Work sample: render a project from the branch into a temp dir (`uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=sample . <dir>`), run the fixed task from `.superpowers/lean-v3/baseline/S0-BASELINE.md` with `claude -p "<task>" --model fable --output-format stream-json --verbose --include-hook-events > sample.jsonl`, then `python3 .superpowers/lean-v3/tools/summarize_sample.py sample.jsonl --check "<the task's own test>"`.
3. Fresh-context judge: one Agent tool call, `subagent_type: general-purpose`, `model: fable`, no history, given only this ticket, `git diff main...HEAD`, the measurement table, the work-sample summary, and the rubric in `04-SESSION-PLAN.md`. It scores each rubric row pass or fail with evidence and lists concrete fixes.
4. The judge applies fixes inside this ticket's file-ownership list only. Anything outside goes to `docs/BACKLOG.md`.
5. Re-run the check after the judge's fixes.
6. Open the PR with the before/after table (baseline from S0-BASELINE.md) and the judge's report in the body.

Run under `/goal` with the done checks above as the condition. Worktree: `git worktree add ../loam-s<N> -b lean/s<N> main` (repo sibling, never nested). Session runs in bypassPermissions because `.claude/` is a protected path. Plain dashes only.


~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS worktree-clean
PASS seed-hooks-two
PASS deleted-trees-empty
PASS new-bin-scripts
PASS retired-files-gone
PASS no-verify-template-refs
PASS render-smoke-test-exists
PASS pytest-bin-tests
PASS bin-check-runs (5s)
PASS rendered-settings
PASS rendered-hooks
PASS rendered-codex-rules
PASS rendered-codex-config
PASS run-artefacts
SKIP render-smoke-assertions: needs a human to confirm test_render_smoke.py asserts all six things the ticket names: settings parse, config parse, each hook runs once and exits 0, the deny list and the rules file share the forbidden families, and the rendered bin/check exists
SKIP probe-rm-rf-denied: needs a live rendered project and an interactive Claude session
SKIP probe-git-checkout-dot-denied: needs a live rendered project and an interactive Claude session
SKIP probe-out-of-workspace-write-fails: needs a live rendered project and an interactive Claude session
SKIP probe-env-read-blocked-in-sandbox: needs a live rendered project with the sandbox active
SKIP probe-git-ls-remote-succeeds: needs a live rendered project with network and a git remote
SKIP probe-no-hook-output-on-git-status: needs a live rendered project and an interactive Claude session
SKIP probe-codex-execpolicy-forbidden-families: needs a live rendered project and the codex CLI
SKIP pr-check-green: needs a pushed branch and a GitHub check run
SUMMARY pass=14 fail=0 skip=9

~~~~~~~~~~~~ evidence

## PR body draft (worker-authored)

~~~~~~~~~~~~ evidence
# S3: the hot-path cut

Every hook on a tool matcher and every free-text safety parser is gone.
Native deny rules, a Codex rules file, a permissions profile and the sandbox take their place, and one render smoke test replaces the contract, hook and parity suites.

Closes #23. Part of #14. Spec: `02-IMPLEMENTATION-SPEC.md` commit 2, plus the `copier.yml` line from commit 4 and the release script from commit 6.

## What changed

- `seed/.claude/settings.json`: 20 deny rules, the sandbox block, two SessionStart-class hooks. No allow, no ask, no `defaultMode`, no `PreToolUse`, `PostToolUse`, `PostToolUseFailure` or `Stop`.
- 13 hook scripts and `seed/.agents/lib/` deleted. `fable-session-brief.sh` and `post-compact-reinject.sh` stay.
- Codex: `hooks.json`, `hooks/pre-tool-policy.py` and `rules/default.rules` deleted. New `rules/loam.rules` (15 forbidden families) and a new `config.toml` (`approval_policy = "never"`, one `loam` profile extending `:workspace`, `.env*` denies, `network.enabled = true`, no `sandbox_mode`).
- `bin/`: `verify-template.sh`, `verify-template-stages.sh`, `harness-smoke.sh`, `harness-smoke-stages.sh`, `verification_snapshot.py`, `rendered_harness_contract.py`, `agent_parity/` and `seed/agent-parity.toml` deleted. `bin/release.sh` rewritten to 39 lines. `bin/hygiene` added.
- `bin/tests/`: `test_render_smoke.py` added; seven modules deleted (`test_rendered_harness_contract.py`, `test_seed_claude_hooks.py`, `test_validation_evidence.py`, `test_verification_snapshot.py`, `test_commit_directory.py`, `test_policy_performance.py`, `test_agent_parity.py`).
- Rendered projects now get `bin/check` and a `check` CI workflow.
- `copier.yml` drops the dead `agent-parity.toml` exclude line.

## Before and after

| Row | Before | After |
|---|---|---|
| Added latency per Bash call | 414 ms, 5 hooks | 0 ms, 0 hooks on any tool matcher |
| PreToolUse:Bash hook starts per Bash call, work sample | 8 | 0 |
| PostToolUse hooks (ruff per edit) | 3 | 0 |
| Shipped hooks | 15 | 2 |
| Seed hook and lib lines | 2309 | 63 |
| bin plus tests lines | 11378 | 1522 (1851 counting `bin/check` and `bin/hygiene`, which have no extension) |
| `time bin/check` | 207 s (DESIGN.md, not re-measured at S0) | 4.9 s, exit 0 |
| Claude deny rules / ask / allow | 6 / 1 / 10 | 20 / 0 / 0 |
| Codex forbidden families in a rules file | 0 | 15 |
| Test modules under `bin/tests` | 12 | 6 |

Work sample, same task text and command shape as S0:

| Row | Before | After |
|---|---|---|
| elapsed_seconds | 125.7 | 11.5 |
| turns | 18 | 2 |
| cost_usd | 1.10 | 0.51 |
| tool_calls | 16 | 1 |
| hook_events | 306 | 14 |
| denials | 0 | 0 |
| task check | 1 passed | 1 passed |

The elapsed and token rows are not all harness effect: at S0 the model needed 16 Bash calls and built a venv, and here it solved the same task in one call.
The clean harness row is PreToolUse:Bash starts per Bash call, 8 to 0.

## Live probes (decisions 9 and 10)

Rendered project, `.env` file and `origin` remote added, run through `claude -p --model fable`.
Every probe result below is worker-observed, not covered by a supervisor PASS line.
The five that succeeded are evidence from one run, not verified checks.

```
rm -rf x                 -> Permission to use Bash with command rm -rf x has been denied.
git checkout .           -> Permission to use Bash with command git checkout . has been denied.
python3 -c "open('.env')"-> denied by the Claude Code auto mode classifier
printf hi > $HOME/...    -> SUCCEEDED (see the sandbox finding below)
git ls-remote origin     -> succeeded, listed main, the pull refs and tags v1.0.0 to v2.3.0
git status               -> ran, and the whole session logged 0 PreToolUse hook events
```

```
$ codex execpolicy check --rules .codex/rules/loam.rules -- git push --force origin main
{"matchedRules":[{"prefixRuleMatch":{"matchedPrefix":["git","push","--force"],
 "decision":"forbidden","justification":"Force push blocked."}}],"decision":"forbidden"}
```

`rm -rf x`, `git checkout .`, `git reset --hard HEAD` and `git stash drop` return `forbidden` the same way.

### The sandbox does not run on this host

This machine has `bubblewrap` but not `socat`, and `sudo` needs a password.
With `sandbox.failIfUnavailable: true` a rendered project refuses to start at all.
With `false`, which is what this branch ships, it starts and prints:

```
Sandbox disabled: sandbox is enabled but dependencies are missing: socat not installed
Commands will run WITHOUT sandboxing. Network and filesystem restrictions will NOT be enforced.
```

So the two containment probes are honest failures of the environment, not of the keys:
the out-of-workspace write succeeded, and the `.env` read was stopped by the auto mode classifier rather than by the OS.
The key stays in the file with the value `false` so the fallback is a recorded decision instead of an absent key.
`apt install bubblewrap socat` turns real containment on; S4 records this in `docs/HARNESS.md`.

No `sandbox.network` allowlist was needed: `git ls-remote origin` reached GitHub.

### One Codex key was wrong and is fixed here

`codex doctor` printed five startup warnings, one per unbounded `**` deny-read glob, because Linux sandboxing cannot expand them.
`glob_scan_max_depth = 3` in the `loam` filesystem profile clears all five.
The config now loads with 0 startup warnings on codex-cli 0.153.4.

## The six addendum files

The ticket's addendum of 2026-09-07 resolves the conflict between done check 4 (`grep -rn
verify-template bin .github` must print nothing) and the two "do not touch" lines, and names these
six paths as in scope for S3. This diff touches exactly those six and no other path outside the
"Files owned" list. Listed here so a reviewer can check them against the addendum directly.

| Path | Change | Why it is in this commit |
|---|---|---|
| `seed/.codex/rules/default.rules` | deleted, 82 lines | Named in the DELETE block of `02-IMPLEMENTATION-SPEC.md` commit 2, the spec this ticket points at. It documents itself as defense-in-depth for `pre-tool-policy.py`, which this commit deletes. `loam.rules` replaces it. |
| `bin/harness-smoke.sh` | deleted, 11 lines | An 11-line wrapper whose only body is a call to `bin/harness-smoke-stages.sh`, which the ticket does name. Deleting the stages file alone would leave a wrapper that cannot run. |
| `seed/.gitignore.jinja` | 3 lines removed | Both removed lines ignore artefacts of deleted hooks: `.validation_passed` was written by `run-validate-waves.sh` and `.claude/audit.log` by `bash-audit-log.sh`. Deletion travelling with its importers. |
| `bin/lib.sh` | 1 comment line | The comment read "verify-template.sh style" and named a deleted script. Comment only, no behaviour change. Needed for done check 4. |
| `bin/check` | 1 comment line | Addendum bullet 1: "the one comment line that names `verify-template-stages.sh` (comment only, no behaviour change)". No step, no gate, no exit code changed. |
| `bin/tests/test_ci_configuration.py` | 2 assertions | Addendum bullet 2: the two `assertNotIn("verify-template", ...)` guards "may be replaced by guards that do not spell the retired name. Nothing else in that file." The two `assertNotIn("verify-template", w)` guards named a script that no longer exists anywhere in the repo, so they asserted nothing. Replaced with strictly stronger guards that do not spell the retired name: the test workflow must contain exactly one `run: bin/` step, and the release workflow none. All five tests in the module still pass. |

Nothing here weakens a deny rule, a hook, or a check. The two conflict cases were recorded in
`loops/runs/S3/decisions.md` under "Round 2", before the addendum settled them the same way.

## Unverified or not done

- **unobserved**: the GitHub `check` run on the pushed branch. The done checks reported `SKIP pr-check-green`, so no CI run on this branch was ever observed green. A reviewer should wait for the `check` status before merging.
- **unverified**: the sandbox itself. No sandbox ran on this host, so `filesystem.denyRead`, `denyWrite`, `autoAllowBashIfSandboxed` and `allowUnsandboxedCommands` are documented-correct and parse-correct, but never exercised. S5 should re-run the probes on a host with `socat`.
- **unverified**: the project-level Codex layer. `codex doctor` reads the user layer, so the profile was validated by copying it into a temporary `CODEX_HOME`, not by trusting a rendered project. Codex only loads `<repo>/.codex/` in a trusted project.
- **unverified**: `.env` containment against a subprocess. The classifier denied it in auto mode; in `bypassPermissions` the classifier does not run, so on a host without the sandbox that read would succeed.
- **known gap, not patched**: prefix dodging. `codex execpolicy check ... -- git clean -fd` returns no decision, because `-fd` is one token and the rules match token prefixes. The Claude deny list has the same property. DESIGN already accepts this; it belongs in `docs/HARNESS.md`.
- **resolved**: `grep -rn verify-template bin .github` prints nothing. The two files this required touching are covered by the ticket addendum of 2026-09-07; see the table above.
- **not done, out of scope**: `seed/_gh_setup.sh` ruleset step. The spec puts it in this commit, the session plan gives the file to S4, and the ticket's file list excludes it. The rendered CI job is already named `check`, which is the status context that step needs.
- **for the backlog**: `bin/check-own-synthesis.py` has no caller (00-DECISIONS row 8 says delete it in that case), but it is not in this ticket's deletion list. Root `AGENTS.md` still names the three retired checker paths; `bin/hygiene` reports all three, and root `AGENTS.md` is S4's file. Five `bin/` Python files are still not `ruff format` clean; `bin/check` deliberately leaves that gate off and the file is S1's.

~~~~~~~~~~~~ evidence

## Diff (main...HEAD)

~~~~~~~~~~~~ evidence
 bin/agent_parity/parity.py                      |  351 -----------------
 bin/check                                       |    2 +-
 bin/harness-smoke-stages.sh                     |  100 -----
 bin/harness-smoke.sh                            |   11 -
 bin/hygiene                                     |  202 ++++++++++
 bin/lib.sh                                      |    2 +-
 bin/release.sh                                  |  148 ++------
 bin/rendered_harness_contract.py                | 1651 --------------------------------------------------------------------------------
 bin/tests/test_agent_parity.py                  |  199 ----------
 bin/tests/test_ci_configuration.py              |    5 +-
 bin/tests/test_commit_directory.py              |  174 ---------
 bin/tests/test_policy_performance.py            |  153 --------
 bin/tests/test_render_smoke.py                  |  208 +++++++++++
 bin/tests/test_rendered_harness_contract.py     | 2936 -----------------------------------------------------------------------------------------------------------------------------------------------
 bin/tests/test_seed_claude_hooks.py             | 2590 ------------------------------------------------------------------------------------------------------------------------------
 bin/tests/test_validation_evidence.py           |  533 --------------------------
 bin/tests/test_verification_snapshot.py         |  294 ---------------
 bin/verification_snapshot.py                    |  289 --------------
 bin/verify-template-stages.sh                   |  252 -------------
 bin/verify-template.sh                          |   11 -
 copier.yml                                      |    2 -
 seed/.agents/lib/stop_verify.py                 |  270 --------------
 seed/.agents/lib/validation.py                  |  755 -------------------------------------
 seed/.claude/hooks/bash-audit-log.sh            |   81 ----
 seed/.claude/hooks/bash-length-advisory.sh      |   41 --
 seed/.claude/hooks/concurrent-checkout-guard.sh |   86 -----
 seed/.claude/hooks/harness-hygiene.sh           |  216 -----------
 seed/.claude/hooks/mutation-gate.sh             |  332 -----------------
 seed/.claude/hooks/pre-commit-gate.sh           |    8 -
 seed/.claude/hooks/ruff-after-edit.sh           |   36 --
 seed/.claude/hooks/run-validate-waves.sh        |    6 -
 seed/.claude/hooks/sentinel-cleanup.sh          |   84 -----
 seed/.claude/hooks/skill-usage-log.sh           |   44 ---
 seed/.claude/hooks/stop-verify-gate.sh          |   10 -
 seed/.claude/hooks/test-tamper-scan.sh          |  220 -----------
 seed/.claude/hooks/write-rewrite-guard.sh       |   57 ---
 seed/.claude/settings.json                      |  176 ++-------
 seed/.codex/config.toml                         |   37 +-
 seed/.codex/hooks.json                          |   46 ---
 seed/.codex/hooks/pre-tool-policy.py            |  881 -------------------------------------------
 seed/.codex/rules/default.rules                 |   82 ----
 seed/.codex/rules/loam.rules                    |   19 +
 seed/.github/workflows/check.yml.jinja          |   23 ++
 seed/.gitignore.jinja                           |    3 -
 seed/agent-parity.toml                          |   70 ----
 seed/bin/check.jinja                            |   31 ++
 46 files changed, 560 insertions(+), 13167 deletions(-)

diff --git a/bin/check b/bin/check
index f4b0de9..f055e3b 100755
--- a/bin/check
+++ b/bin/check
@@ -82,7 +82,7 @@ fi
 "$PYTEST_PY" -m pytest "${PYTEST_ARGS[@]}" || bad "pytest"

 step "SKILL.md frontmatter name gate"
-# Folded from the old verify-template-stages.sh stage 6. Every SKILL.md must
+# Folded from the old staged template checker. Every SKILL.md must
 # carry a name: in its first frontmatter block and must NOT use the fake
 # auto-activate key (use disable-model-invocation: true).
 while IFS= read -r skill; do
diff --git a/bin/hygiene b/bin/hygiene
new file mode 100755
index 0000000..bfc2549
--- /dev/null
+++ b/bin/hygiene
@@ -0,0 +1,202 @@
+#!/usr/bin/env python3
+"""bin/hygiene - flag dead references in the agent docs. Advisory, never a gate.
+
+Moved out of the deleted SessionStart hook seed/.claude/hooks/harness-hygiene.sh
+(DESIGN.md L1: "harness-hygiene becomes bin/hygiene, run by choice"). It scans
+CLAUDE.md, AGENTS.md, STATE.md and HANDOFF.md for paths and commands that do not
+exist, and always exits 0.
+
+Two blind spots of the old hook are fixed here:
+  - a gitignored path (a log, a generated report) is a local artifact, not a
+    stale reference, so it is skipped;
+  - a missing command is reported under a separate "not installed here" heading,
+    because an absent optional tool (pytest, flock) says nothing about the doc.
+
+Scan scope: inline `code spans` get the path and command rules. Fenced code
+blocks are path-checked on the first token of each line only, since later tokens
+are arguments and usually placeholders. Absolute and ~ paths inside a fence are
+machine-specific examples and are skipped.
+"""
+
+from __future__ import annotations
+
+import os
+import re
+import subprocess
+import sys
+
+SCANNED = ["CLAUDE.md", "AGENTS.md", "STATE.md", "HANDOFF.md"]
+SPAN = re.compile(r"`([^`\n]+)`")
+BADCHARS = set("*{}$<>|()")
+CMD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.+-]*$")
+# A slashless word is path-checked only when it ends in an extension we know.
+# Everything else with a dot (asyncio.gather, docs.example.com, v2.0.0) is a
+# dotted name, not a path.
+FILE_RE = re.compile(
+    r"^[\w.+-]+\.(md|py|sh|json|jsonl|yml|yaml|toml|txt|js|ts|tsx|jsx|cfg|ini"
+    r"|lock|rules|css|html|rst|csv|sql|tex|bib|ipynb|env|log)$"
+)
+VERSION_RE = re.compile(r"^v?\d+(\.\d+)+$")
+
+
+def git_root() -> str:
+    r = subprocess.run(
+        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
+    )
+    return r.stdout.strip() if r.returncode == 0 else ""
+
+
+def tracked_basenames(root: str) -> set[str]:
+    r = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True)
+    if r.returncode != 0:
+        return set()
+    return {os.path.basename(line) for line in r.stdout.splitlines() if line}
+
+
+def resolve(root: str, word: str) -> str:
+    w = word.rstrip("/") or "/"
+    if w.startswith("~"):
+        return os.path.expanduser(w)
+    return w if os.path.isabs(w) else os.path.join(root, w)
+
+
+class Scanner:
+    def __init__(self, root: str) -> None:
+        self.root = root
+        self.tracked = tracked_basenames(root)
+        self.cmd_cache: dict[str, bool] = {}
+        self.ignore_cache: dict[str, bool] = {}
+
+    def ignored(self, word: str) -> bool:
+        """True when .gitignore claims the path, so it is a local artifact."""
+        if word not in self.ignore_cache:
+            r = subprocess.run(
+                ["git", "-C", self.root, "check-ignore", "-q", "--", word],
+                capture_output=True,
+            )
+            self.ignore_cache[word] = r.returncode == 0
+        return self.ignore_cache[word]
+
+    def cmd_missing(self, word: str) -> bool:
+        if word not in self.cmd_cache:
+            r = subprocess.run(
+                ["bash", "-c", 'command -v -- "$1" >/dev/null 2>&1', "_", word]
+            )
+            self.cmd_cache[word] = r.returncode != 0
+        return self.cmd_cache[word]
+
+    def missing_path(self, word: str) -> bool:
+        return not os.path.exists(resolve(self.root, word)) and not self.ignored(word)
+
+    def fence_path_missing(self, word: str) -> bool:
+        if "/" not in word or ":" in word:
+            return False
+        if any(ch in word for ch in BADCHARS) or word[0] in "-@#":
+            return False
+        if word.startswith("/") or word.startswith("~"):
+            return False
+        if "://" in word or word.startswith("www.") or word in SCANNED:
+            return False
+        base = os.path.basename(word.rstrip("/"))
+        if not FILE_RE.match(base) or VERSION_RE.match(base):
+            return False
+        return self.missing_path(word)
+
+
+def scan(scanner: Scanner) -> tuple[list, list]:
+    dead: list[tuple[str, str]] = []
+    absent_cmds: list[tuple[str, str]] = []
+    seen: set[tuple[str, str]] = set()
+
+    def record(bucket, name, word):
+        if (name, word) not in seen:
+            seen.add((name, word))
+            bucket.append((name, word))
+
+    for name in SCANNED:
+        fp = os.path.join(scanner.root, name)
+        if not os.path.isfile(fp):
+            continue
+        text = open(fp, encoding="utf-8", errors="ignore").read()
+
+        for m in SPAN.finditer(text):
+            toks = m.group(1).split()
+            if not toks:
+                continue
+            raw = toks[0]
+            word = raw.rstrip(",.:;)")
+            if not word or any(ch in word for ch in BADCHARS) or word[0] in "-@#":
+                continue
+            if word in SCANNED or "://" in word or word.startswith("www."):
+                continue
+            if word.startswith("/") and word.count("/") == 1:
+                continue
+            if "/" in word:
+                # A slug like SamyakJhaveri/loam is not a path: inside a span,
+                # only a filename-looking basename or a trailing slash counts.
+                base = os.path.basename(word.rstrip("/"))
+                if (word.endswith("/") or FILE_RE.match(base)) and scanner.missing_path(
+                    word
+                ):
+                    record(dead, name, word)
+            elif "." in word:
+                stem = word.rsplit(".", 1)[0]
+                known = FILE_RE.match(word) and not VERSION_RE.match(word)
+                # Capitalized stems (Node.js, React.js) are product names unless
+                # the repo really tracks such a file.
+                named = not any(c.isupper() for c in stem) or word in scanner.tracked
+                if known and named and word not in scanner.tracked:
+                    if scanner.missing_path(word):
+                        record(dead, name, word)
+            elif len(toks) >= 2 and CMD_RE.match(word):
+                if not raw.rstrip(",;)").endswith(":") and scanner.cmd_missing(word):
+                    record(absent_cmds, name, word)
+
+        in_fence = False
+        for line in text.splitlines():
+            if line.startswith("```"):
+                in_fence = not in_fence
+                continue
+            stripped = line.strip()
+            if not in_fence or not stripped or stripped.startswith("#"):
+                continue
+            word = stripped.split()[0].rstrip(",.:;)")
+            if word and scanner.fence_path_missing(word):
+                record(dead, name, word)
+
+    return dead, absent_cmds
+
+
+def report(title: str, rows: list[tuple[str, str]], note: str) -> None:
+    if not rows:
+        return
+    print("%s: %d (%s)" % (title, len(rows), note))
+    for name, word in rows[:25]:
+        print("  %s: %s" % (name, word))
+    if len(rows) > 25:
+        print("  ... and %d more" % (len(rows) - 25))
+
+
+def main() -> int:
+    root = git_root()
+    if not root:
+        print("hygiene: not inside a git repository")
+        return 0
+    dead, absent_cmds = scan(Scanner(root))
+    report(
+        "Stale references in agent docs",
+        dead,
+        "path does not exist and is not gitignored",
+    )
+    report(
+        "Commands named in agent docs but not installed here",
+        absent_cmds,
+        "informational; the doc may still be right",
+    )
+    if not dead and not absent_cmds:
+        print("hygiene: no stale references in %s" % ", ".join(SCANNED))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/bin/lib.sh b/bin/lib.sh
index d120b36..67c96cb 100755
--- a/bin/lib.sh
+++ b/bin/lib.sh
@@ -9,7 +9,7 @@ info() { printf '\033[36m[%s]\033[0m %s\n' "$LIB_PREFIX" "$*"; }
 warn() { printf '\033[33m[%s]\033[0m %s\n' "$LIB_PREFIX" "$*"; }
 ok()   { printf '\033[32m[%s]\033[0m   %s\n' "$LIB_PREFIX" "$*"; }

-# Plain output (verify-template.sh style)
+# Plain output for step-by-step scripts.
 fail() { echo "FAIL: $*" >&2; exit 1; }
 pass() { echo "OK: $*"; }

diff --git a/bin/release.sh b/bin/release.sh
index c5765ca..f01544e 100755
--- a/bin/release.sh
+++ b/bin/release.sh
@@ -1,141 +1,39 @@
 #!/usr/bin/env bash
-# release.sh — tag a new template release.
-#
-# Usage: bin/release.sh <version>  (e.g., bin/release.sh 1.1.0)
-#
-# Steps: (1) update VERSION, (2) commit, (3) tag, (4) push commit + tag.
-#
-# Identity: the release commit AND the annotated tag are hard-pinned to the
-# public GitHub noreply identity via `git -c`. A plain `git commit`/`git tag`
-# inherits ambient config — and a fresh clone's global identity may be a
-# personal/academic email that would then be baked permanently into public
-# history (and a tag's `tagger` line). Pinning needs zero operator setup and
-# closes both leak vectors.
-
+# release.sh - tag a new Loam release. Usage: bin/release.sh X.Y.Z
+# CI gated the tree on the PR; this runs the local preconditions, then bumps
+# VERSION, commits, tags, and pushes atomically.
 set -euo pipefail
-
-# shellcheck disable=SC2034
 LIB_PREFIX="release"
-# shellcheck source=bin/lib.sh
 source "$(dirname "$0")/lib.sh"

-# Public release identity — the only identity allowed in public history.
 NOREPLY_NAME="Samyak Jhaveri"
 NOREPLY_EMAIL="39847642+SamyakJhaveri@users.noreply.github.com"

 VERSION="${1:-}"
-[[ -n "$VERSION" ]] || die "usage: bin/release.sh <version> (e.g., 1.1.0)"
-[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "version must be semver (e.g., 1.2.3)"
-
-# Operate on the script's OWN repository, not the caller cwd. release.sh runs git
-# against the working directory (branch/status/tag/commit/push), while the verify
-# gate is resolved from the script path; without this, an absolute-path invocation
-# from a different repo would validate this repo but tag and push the other one.
-SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
-SELF_REPO="$(git -C "$SELF_DIR" rev-parse --show-toplevel 2>/dev/null)"
-[[ -n "$SELF_REPO" ]] || die "cannot locate the script repository (is bin/release.sh inside a git repo?)"
-cd "$SELF_REPO" || die "cannot enter the script repository: $SELF_REPO"
-
-# Pre-flight. Each git query is captured with its exit status checked: a FAILED
-# git command prints nothing, and a bare `[[ -z "$(...)" ]]` or `| grep -q` would
-# read that empty output as a clean tree / an absent tag and mutate anyway. Fail
-# closed - refuse on any git error.
-BRANCH="$(git branch --show-current)" || die "cannot read current branch"
-[[ "$BRANCH" == "main" ]] || die "releases must be created from main"
-# --untracked-files=all: a repo-level
-# status.showUntrackedFiles=no would otherwise blind this check, letting an
-# untracked non-ignored file influence the worktree gate, stay out of the tag,
-# and reach the push. Force full untracked reporting.
-set +e; PORCELAIN="$(git status --porcelain --untracked-files=all)"; PORCELAIN_RC=$?; set -e
-[[ "$PORCELAIN_RC" -eq 0 ]] || die "git status failed (exit $PORCELAIN_RC); refusing to release"
-[[ -z "$PORCELAIN" ]] || die "working tree is dirty — commit or stash first"
-set +e; EXISTING_TAG="$(git tag -l "v$VERSION")"; TAG_RC=$?; set -e
-[[ "$TAG_RC" -eq 0 ]] || die "git tag query failed (exit $TAG_RC); refusing to release"
-[[ -z "$EXISTING_TAG" ]] || die "tag v$VERSION already exists"
-
-# assume-unchanged / skip-worktree guard. `git status` above is BLIND to a tracked file marked
-# --assume-unchanged (lowercase ls-files -v tag) or skip-worktree (S): its
-# worktree bytes can diverge from the committed bytes the tag will publish, and
-# the verify gate below validates the worktree. Refuse if any tracked path
-# carries a non-`H` tag. Scope is the WHOLE repo (no pathspec) because the tag
-# ships the whole tree. ls-files failure fails closed.
-set +e; VTAGS="$(git ls-files -v)"; VTAGS_RC=$?; set -e
-[[ "$VTAGS_RC" -eq 0 ]] || die "git ls-files -v failed (exit $VTAGS_RC); refusing to release"
-if grep -qvE '^H ' <<<"$VTAGS"; then
-  die "a tracked file is marked assume-unchanged or skip-worktree, so its committed state cannot be trusted; refusing to release. Clear it (git update-index --no-assume-unchanged / --no-skip-worktree). Offending: $(grep -vE '^H ' <<<"$VTAGS" | tr '\n' ' ')"
-fi
-
-# Capture the validated HEAD before the gates run (R4-H2). A concurrent CLEAN
-# commit during the gates moves HEAD but is invisible to a branch/status/tag
-# recheck, so we record the parent here and require the identical HEAD below,
-# pinning the release commit to exactly this validated state.
-HEAD_BEFORE_GATES="$(git rev-parse HEAD)" || die "cannot read HEAD; refusing to release"
-
-# Template verification gate: refuse to cut a release while the template is red.
-# Runs BEFORE any mutation (the VERSION write at Step 1) and before the
-# commit/tag/push, so a red gate stops the release with zero side effects.
-# (Replaced the retired hub-ci gate, 2026-08-29 rebuild.)
-info "running template verification gate"
-bash "$SELF_DIR/verify-template.sh" || die "verify-template failed - refusing to release (run: bin/verify-template.sh)"
-
-# IP gate (defense-in-depth): if the private-dev sweep is present, it must pass
-# in strict mode before we publish. Absent (e.g. public clone) → skip loudly.
-if [[ -x "$SELF_DIR/ip-sweep.sh" ]]; then
-  info "running IP sweep (strict)"
-  IP_SWEEP_STRICT=1 bash "$SELF_DIR/ip-sweep.sh" || die "ip-sweep failed — refusing to release"
+[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "usage: bin/release.sh X.Y.Z"
+
+SELF="$(cd "$(dirname "$0")/.." && pwd)"; cd "$SELF"
+[[ "$(git branch --show-current)" == "main" ]] || die "release from main only"
+git fetch origin main --quiet
+[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || die "main is not equal to origin/main"
+[[ -z "$(git status --porcelain --untracked-files=all)" ]] || die "working tree is dirty"
+[[ -z "$(git tag -l "v$VERSION")" ]] || die "tag v$VERSION already exists"
+
+# The latest run on HEAD must be green. Keyed off the workflow NAME in test.yml.
+STATUS="$(gh run list --commit "$(git rev-parse HEAD)" --workflow Test --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "")"
+[[ "$STATUS" == "success" ]] || die "latest Test run on HEAD is '$STATUS', not success"
+
+# The one local gate CI cannot run: the private IP terms file is off-GitHub.
+if [[ -x "$SELF/bin/ip-sweep.sh" ]]; then
+  IP_SWEEP_STRICT=1 bash "$SELF/bin/ip-sweep.sh" || die "ip-sweep failed"
 else
-  warn "bin/ip-sweep.sh not present — skipping IP gate"
+  warn "bin/ip-sweep.sh absent - skipping IP gate"
 fi

-# Re-verify ALL pre-flight invariants immediately before mutating (C2 + R4-H2).
-# The gates take time; a gate side-effect or a concurrent process could have
-# staged content, moved off main, created the tag, made a CLEAN commit, or set
-# assume-unchanged in that window. Re-check every guard, including HEAD (a clean
-# commit only shows here) and the whole-repo ls-files -v (a gate could set
-# assume-unchanged mid-run); status inherits --untracked-files=all. Any drift ->
-# refuse; never commit into a repo that changed under us.
-[[ "$(git branch --show-current)" == "main" ]] || die "branch changed during pre-flight; refusing to release"
-[[ "$(git rev-parse HEAD)" == "$HEAD_BEFORE_GATES" ]] || die "HEAD moved during the pre-flight gates (a concurrent commit); refusing to release"
-set +e; PORCELAIN2="$(git status --porcelain --untracked-files=all)"; PORCELAIN2_RC=$?; set -e
-[[ "$PORCELAIN2_RC" -eq 0 && -z "$PORCELAIN2" ]] || die "working tree/index changed during the pre-flight gates; refusing to release"
-set +e; EXISTING_TAG2="$(git tag -l "v$VERSION")"; TAG2_RC=$?; set -e
-[[ "$TAG2_RC" -eq 0 && -z "$EXISTING_TAG2" ]] || die "tag v$VERSION appeared during pre-flight; refusing to release"
-set +e; VTAGS2="$(git ls-files -v)"; VTAGS2_RC=$?; set -e
-[[ "$VTAGS2_RC" -eq 0 ]] || die "git ls-files -v failed (exit $VTAGS2_RC) during recheck; refusing to release"
-grep -qvE '^H ' <<<"$VTAGS2" && die "a tracked file became assume-unchanged or skip-worktree during the pre-flight gates; refusing to release. Offending: $(grep -vE '^H ' <<<"$VTAGS2" | tr '\n' ' ')"
-
-# Step 1: Update VERSION file
-info "updating VERSION to $VERSION"
 echo "$VERSION" > VERSION
-
-# Step 2: Commit (identity hard-pinned — see header). Scoped to `-- VERSION` so
-# only that file can ever land in a release commit, whatever else may be staged.
-# Pin the parent (R4-H2): re-assert HEAD immediately before the commit so the
-# release commit is built on exactly the validated HEAD. The VERSION write and
-# `git add` above do not move HEAD, so this narrows the recheck->commit window; a
-# residual pin->commit microwindow remains (git commit has no atomic parent-pin),
-# the same tiny known gap as C2.
 git add VERSION
-[[ "$(git rev-parse HEAD)" == "$HEAD_BEFORE_GATES" ]] || die "HEAD moved before the release commit; refusing to release"
-git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
-  commit -m "release: v$VERSION" -- VERSION
-
-# Capture the release commit's object id (R5-H2). Its parent is the validated
-# HEAD_BEFORE_GATES (pinned above), and every later step targets this exact
-# object rather than a branch name like HEAD, which a concurrent commit could move.
-RELEASE_COMMIT="$(git rev-parse HEAD)" || die "cannot read the release commit id; refusing to release"
-
-# Step 3: Tag the EXPLICIT commit object (tagger identity hard-pinned — annotated
-# tags record a tagger line), not the mutable HEAD.
-git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" \
-  tag -a "v$VERSION" -m "Release v$VERSION" "$RELEASE_COMMIT"
-
-# Step 4: Publish the commit and tag in ONE atomic push (R5-H2 + R5-H3). Pushing
-# the explicit RELEASE_COMMIT object to main (not HEAD) fixes the mutable target,
-# and --atomic makes the branch and tag land together or not at all, so a partial
-# public release (branch pushed, tag failed) cannot happen.
-info "pushing commit and tag (atomic)"
+git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" commit -m "release: v$VERSION" -- VERSION
+RELEASE_COMMIT="$(git rev-parse HEAD)"
+git -c user.name="$NOREPLY_NAME" -c user.email="$NOREPLY_EMAIL" tag -a "v$VERSION" -m "Release v$VERSION" "$RELEASE_COMMIT"
 git push --atomic origin "${RELEASE_COMMIT}:refs/heads/main" "refs/tags/v$VERSION"
-
 ok "released v$VERSION"
-echo "Copier users can now: copier copy --trust --vcs-ref v$VERSION gh:samyakjhaveri/loam ./my-project"
diff --git a/bin/tests/test_ci_configuration.py b/bin/tests/test_ci_configuration.py
index 6995483..9af0214 100644
--- a/bin/tests/test_ci_configuration.py
+++ b/bin/tests/test_ci_configuration.py
@@ -35,7 +35,8 @@ class CIConfig(unittest.TestCase):
         self.assertIn("- name: Run check\n        run: bin/check", w)
         self.assertIn("run: python3 -m pip install -r .github/ci/python-requirements.txt", w)
         self.assertIn("cache-dependency-path: .github/ci/python-requirements.txt", w)
-        self.assertNotIn("verify-template", w)
+        # bin/check is the only repo script CI runs: no retired checker may come back.
+        self.assertEqual(1, w.count("run: bin/"))

     def test_verify_job_has_no_inert_gate(self):
         """An `if:` or `continue-on-error:` in the verify job would make check advisory."""
@@ -48,7 +49,7 @@ class CIConfig(unittest.TestCase):
         w = RELEASE.read_text()
         self.assertIn("tags:", w)
         self.assertIn("softprops/action-gh-release@v2", w)
-        self.assertNotIn("verify-template", w)
+        self.assertNotIn("run: bin/", w)  # release runs no repo script
         self.assertNotIn("bin/check", w)  # release does not re-run the gate


diff --git a/bin/tests/test_render_smoke.py b/bin/tests/test_render_smoke.py
new file mode 100644
index 0000000..8aaa94a
--- /dev/null
+++ b/bin/tests/test_render_smoke.py
@@ -0,0 +1,208 @@
+"""Render the template once, then assert the rendered harness is well formed.
+
+Replaces test_rendered_harness_contract.py, test_seed_claude_hooks.py and
+test_agent_parity.py with one cheap smoke that renders once per class.
+"""
+
+from __future__ import annotations
+
+import json
+import pathlib
+import shutil
+import subprocess
+import tempfile
+import tomllib
+import unittest
+
+ROOT = pathlib.Path(__file__).resolve().parents[2]
+
+# The destructive families both harnesses must forbid. This is the parity check
+# that replaced agent-parity.toml: one list, asserted against the Claude deny
+# list and against the Codex rules file.
+FORBIDDEN_FAMILIES = (
+    "rm -rf",
+    "git push --force",
+    "git reset --hard",
+    "git clean -f",
+    "git checkout .",
+    "git restore .",
+    "git stash clear",
+    "git stash drop",
+)
+
+
+def _copier():
+    for cmd in (["copier"], ["uvx", "copier"]):
+        try:
+            subprocess.run(cmd + ["--version"], capture_output=True, check=True)
+            return cmd
+        except (OSError, subprocess.CalledProcessError):
+            continue
+    raise unittest.SkipTest("copier not available")
+
+
+def _render(dest: pathlib.Path, ref: str = "HEAD") -> None:
+    subprocess.run(
+        _copier()
+        + [
+            "copy",
+            "--trust",
+            "--defaults",
+            "--vcs-ref=" + ref,
+            "--data",
+            "project_name=smoke",
+            "--data",
+            "github_repo=",
+            str(ROOT),
+            str(dest),
+        ],
+        check=True,
+        capture_output=True,
+        text=True,
+    )
+
+
+class RenderSmoke(unittest.TestCase):
+    @classmethod
+    def setUpClass(cls):
+        cls._tmp = tempfile.TemporaryDirectory()
+        cls.out = pathlib.Path(cls._tmp.name) / "render"
+        _render(cls.out)
+
+    @classmethod
+    def tearDownClass(cls):
+        cls._tmp.cleanup()
+
+    def settings(self) -> dict:
+        return json.loads((self.out / ".claude/settings.json").read_text())
+
+    def test_settings_parse_and_two_hooks(self):
+        s = self.settings()
+        cmds = [
+            h["command"]
+            for block in s["hooks"].values()
+            for entry in block
+            for h in entry["hooks"]
+        ]
+        names = sorted({c.rsplit("/", 1)[-1] for c in cmds})
+        self.assertEqual(names, ["fable-session-brief.sh", "post-compact-reinject.sh"])
+        self.assertNotIn("allow", s["permissions"])
+        self.assertNotIn("ask", s["permissions"])
+        self.assertNotIn("defaultMode", s["permissions"])
+        self.assertNotIn("defaultMode", s)
+        self.assertIs(s["sandbox"]["enabled"], True)
+        self.assertIn(".env", s["sandbox"]["filesystem"]["denyRead"])
+
+    def test_only_the_two_hooks_ship(self):
+        shipped = sorted(p.name for p in (self.out / ".claude/hooks").glob("*"))
+        self.assertEqual(
+            shipped, ["fable-session-brief.sh", "post-compact-reinject.sh"]
+        )
+
+    def test_codex_config_parses(self):
+        config = (self.out / ".codex/config.toml").read_text()
+        data = tomllib.loads(config)
+        self.assertEqual(data["default_permissions"], "loam")
+        # A legacy sandbox_mode key would silently disable the named profile.
+        self.assertNotIn("sandbox_mode", data)
+        # default_permissions must sit above the first [table] header, or TOML
+        # binds it to that table and the profile is never selected.
+        lines = config.splitlines()
+        first_table = next(
+            i for i, ln in enumerate(lines) if ln.strip().startswith("[")
+        )
+        key = next(
+            i
+            for i, ln in enumerate(lines)
+            if ln.strip().startswith("default_permissions")
+        )
+        self.assertLess(key, first_table)
+
+    def test_each_hook_runs_and_exits_zero(self):
+        hooks = sorted((self.out / ".claude/hooks").glob("*.sh"))
+        self.assertTrue(hooks, "no hooks rendered")
+        for hook in hooks:
+            r = subprocess.run(
+                ["bash", str(hook)],
+                input='{"model":"opus"}',
+                capture_output=True,
+                text=True,
+                timeout=10,
+            )
+            self.assertEqual(r.returncode, 0, f"{hook.name}: {r.stderr}")
+
+    def test_deny_and_rules_share_forbidden_families(self):
+        deny = self.settings()["permissions"]["deny"]
+        rules = (self.out / ".codex/rules/loam.rules").read_text()
+        for fam in FORBIDDEN_FAMILIES:
+            self.assertTrue(any(fam in d for d in deny), f"deny missing {fam}")
+            self.assertIn(fam, rules, f"loam.rules missing {fam}")
+
+    def test_rendered_check_exists(self):
+        check = self.out / "bin/check"
+        self.assertTrue(check.exists())
+        r = subprocess.run(["bash", "-n", str(check)], capture_output=True, text=True)
+        self.assertEqual(r.returncode, 0, r.stderr)
+
+    def test_codex_execpolicy_forbids_the_force_families(self):
+        if not shutil.which("codex"):
+            self.skipTest("codex CLI absent")
+        rules = str(self.out / ".codex/rules/loam.rules")
+        for cmd in (
+            ["rm", "-rf", "x"],
+            ["git", "push", "--force", "origin", "main"],
+            ["git", "checkout", "."],
+        ):
+            r = subprocess.run(
+                ["codex", "execpolicy", "check", "--rules", rules, "--"] + cmd,
+                capture_output=True,
+                text=True,
+            )
+            self.assertEqual(
+                json.loads(r.stdout).get("decision"), "forbidden", " ".join(cmd)
+            )
+
+
+class UpdateSmoke(unittest.TestCase):
+    def test_update_from_v230_leaves_no_orphan_hook(self):
+        cmd = _copier()
+        with tempfile.TemporaryDirectory() as d:
+            proj = pathlib.Path(d) / "p"
+            _render(proj, ref="v2.3.0")
+            subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
+            subprocess.run(["git", "add", "-A"], cwd=proj, check=True)
+            subprocess.run(
+                [
+                    "git",
+                    "-c",
+                    "user.email=t@t",
+                    "-c",
+                    "user.name=t",
+                    "commit",
+                    "-qm",
+                    "base",
+                ],
+                cwd=proj,
+                check=True,
+            )
+            subprocess.run(
+                cmd + ["update", "--trust", "--defaults", "--vcs-ref=HEAD", str(proj)],
+                check=True,
+                capture_output=True,
+                cwd=proj,
+            )
+            settings = json.loads((proj / ".claude/settings.json").read_text())
+            for block in settings["hooks"].values():
+                for entry in block:
+                    for h in entry["hooks"]:
+                        # removeprefix, not lstrip: lstrip("./") would eat
+                        # the leading dot of ".claude/..." as well.
+                        rel = h["command"].removeprefix("./")
+                        script = proj / rel
+                        self.assertTrue(
+                            script.exists(), f"orphan hook wiring: {h['command']}"
+                        )
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/copier.yml b/copier.yml
index 55537d1..8042193 100644
--- a/copier.yml
+++ b/copier.yml
@@ -17,8 +17,6 @@ _exclude:
   - ".git"
   - ".claude/audit.log"
   - ".claude/skill-usage.log"
-  # Loam-repo parity manifest; the check runs in the template repo, never in a project.
-  - "agent-parity.toml"
   # Loam-repo maintenance config (numeric-claim checker); never ships.
   - ".claude/stale-counts.json"
   - ".claude/.local-paths"
diff --git a/seed/.claude/settings.json b/seed/.claude/settings.json
index 82400c0..08773f4 100644
--- a/seed/.claude/settings.json
+++ b/seed/.claude/settings.json
@@ -3,147 +3,40 @@
     "pyright-lsp@claude-plugins-official": true
   },
   "permissions": {
-    "allow": [
-      "Bash(ls:*)",
-      "Bash(grep:*)",
-      "Bash(head:*)",
-      "Bash(tail:*)",
-      "Bash(git status:*)",
-      "Bash(git log:*)",
-      "Bash(git diff:*)",
-      "Bash(wc:*)",
-      "Bash(mkdir:*)",
-      "Bash(.claude/hooks/run-validate-waves.sh:*)"
-    ],
     "deny": [
       "Bash(rm -rf:*)",
       "Bash(rm -fr:*)",
+      "Bash(rm -Rf:*)",
+      "Bash(rm -r -f:*)",
+      "Bash(rm -f -r:*)",
       "Bash(git push --force:*)",
+      "Bash(git push -f:*)",
+      "Bash(git push --force-with-lease:*)",
+      "Bash(git push --force-if-includes:*)",
       "Bash(git reset --hard:*)",
+      "Bash(git clean -f:*)",
+      "Bash(git clean -d:*)",
+      "Bash(git clean -x:*)",
+      "Bash(git checkout -- .:*)",
+      "Bash(git checkout .:*)",
+      "Bash(git restore .:*)",
+      "Bash(git stash clear:*)",
+      "Bash(git stash drop:*)",
       "Read(.env*)",
       "Edit(.env*)"
-    ],
-    "ask": [
-      "Bash(git push:*)"
     ]
   },
+  "sandbox": {
+    "enabled": true,
+    "failIfUnavailable": false,
+    "autoAllowBashIfSandboxed": true,
+    "allowUnsandboxedCommands": false,
+    "filesystem": {
+      "denyRead": [".env", ".env.*"],
+      "denyWrite": [".env", ".env.*"]
+    }
+  },
   "hooks": {
-    "PreToolUse": [
-      {
-        "matcher": "Skill",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/skill-usage-log.sh",
-            "timeout": 5
-          }
-        ]
-      },
-      {
-        "matcher": "Bash|Edit|Write",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/concurrent-checkout-guard.sh",
-            "timeout": 10
-          }
-        ]
-      },
-      {
-        "matcher": "Write",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/write-rewrite-guard.sh",
-            "timeout": 5
-          }
-        ]
-      },
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/bash-length-advisory.sh",
-            "timeout": 5
-          }
-        ]
-      },
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/test-tamper-scan.sh",
-            "timeout": 15
-          }
-        ]
-      },
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/pre-commit-gate.sh",
-            "timeout": 10
-          }
-        ]
-      },
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/mutation-gate.sh",
-            "timeout": 600
-          }
-        ]
-      }
-    ],
-    "PostToolUse": [
-      {
-        "matcher": "Edit|Write",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/ruff-after-edit.sh",
-            "timeout": 10
-          }
-        ]
-      },
-      {
-        "matcher": "Edit|Write",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/sentinel-cleanup.sh",
-            "timeout": 5
-          }
-        ]
-      },
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/bash-audit-log.sh",
-            "timeout": 5
-          }
-        ]
-      }
-    ],
-    "PostToolUseFailure": [
-      {
-        "matcher": "Bash",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/bash-audit-log.sh",
-            "timeout": 5
-          }
-        ]
-      }
-    ],
     "SessionStart": [
       {
         "matcher": "compact",
@@ -155,16 +48,6 @@
           }
         ]
       },
-      {
-        "matcher": "startup|resume|clear",
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/harness-hygiene.sh",
-            "timeout": 10
-          }
-        ]
-      },
       {
         "matcher": "startup|resume|clear|compact|fork",
         "hooks": [
@@ -186,17 +69,6 @@
           }
         ]
       }
-    ],
-    "Stop": [
-      {
-        "hooks": [
-          {
-            "type": "command",
-            "command": ".claude/hooks/stop-verify-gate.sh",
-            "timeout": 30
-          }
-        ]
-      }
     ]
   }
 }
diff --git a/seed/.codex/config.toml b/seed/.codex/config.toml
index 34d8c9b..9a429e3 100644
--- a/seed/.codex/config.toml
+++ b/seed/.codex/config.toml
@@ -1,24 +1,37 @@
-# Repo-scoped Codex configuration for this project.
-# NOTE: this whole layer is inert until you mark the project trusted in Codex
-# and review hooks via /hooks. See AGENTS.md "Codex note".
-
-default_permissions = "project-workspace"
+# Repo-scoped Codex config. Inert until the project is marked trusted in Codex.
+# No sandbox_mode key: that legacy key disables named permission profiles.
+# default_permissions is a TOP-LEVEL key and MUST stay above the first [table]
+# header. In TOML a bare key written after [agents] would bind to that table
+# (agents.default_permissions), the loam profile would never be selected, and the
+# .env denies would be inert.
+approval_policy = "never"
+default_permissions = "loam"

 [features]
-# Keep repository policy hooks active after the project is trusted.
-hooks = true
-# Codex multi-agent collaboration tools (documented as on by default; pinned
-# explicitly so a future default flip does not silently change behavior).
+# The Codex hook layer is gone; do not advertise hooks as active.
+hooks = false
 multi_agent = true

 [agents]
 max_concurrent_threads_per_session = 6

-[permissions.project-workspace]
-description = "Workspace editing with project secret-file denies."
+[permissions.loam]
+description = "Workspace editing with network on and .env denied."
 extends = ":workspace"

-[permissions.project-workspace.filesystem.":workspace_roots"]
+[permissions.loam.network]
+# Permit command network access (git, pip, npm). No proxy and no domains table:
+# domain rules only bind when features.network_proxy starts the proxy, so a
+# domains table here would be inert config.
+enabled = true
+
+[permissions.loam.filesystem]
+# Linux and WSL sandboxing cannot expand an unbounded ** deny-read glob, and
+# Codex prints one startup warning per pattern without this cap. Verified with
+# codex doctor on codex-cli 0.153.4: 5 warnings before, 0 after.
+glob_scan_max_depth = 3
+
+[permissions.loam.filesystem.":workspace_roots"]
 ".env" = "deny"
 ".env*" = "deny"
 ".env.*" = "deny"
diff --git a/seed/.codex/rules/loam.rules b/seed/.codex/rules/loam.rules
new file mode 100644
index 0000000..bef058d
--- /dev/null
+++ b/seed/.codex/rules/loam.rules
@@ -0,0 +1,19 @@
+# Loam command policy for Codex. forbidden beats prompt beats allow.
+# Codex splits command chains itself; do not reimplement a shell parser.
+# Prefix rules match tokens: "--force" does not match "--force-with-lease",
+# so every destructive spelling is listed explicitly.
+prefix_rule(pattern = ["rm", "-rf"], decision = "forbidden", justification = "Recursive delete blocked.", match = ["rm -rf x"])
+prefix_rule(pattern = ["rm", "-fr"], decision = "forbidden", justification = "Recursive delete blocked.", match = ["rm -fr x"])
+prefix_rule(pattern = ["rm", "-Rf"], decision = "forbidden", justification = "Recursive delete blocked.", match = ["rm -Rf x"])
+prefix_rule(pattern = ["git", "push", "--force"], decision = "forbidden", justification = "Force push blocked.", match = ["git push --force origin main"])
+prefix_rule(pattern = ["git", "push", "-f"], decision = "forbidden", justification = "Force push blocked.", match = ["git push -f origin main"])
+prefix_rule(pattern = ["git", "push", "--force-with-lease"], decision = "forbidden", justification = "Force push blocked.", match = ["git push --force-with-lease origin main"])
+prefix_rule(pattern = ["git", "push", "--force-if-includes"], decision = "forbidden", justification = "Force push blocked.", match = ["git push --force-if-includes origin main"])
+prefix_rule(pattern = ["git", "reset", "--hard"], decision = "forbidden", justification = "Hard reset blocked.", match = ["git reset --hard HEAD"])
+prefix_rule(pattern = ["git", "clean", "-f"], decision = "forbidden", justification = "Force clean blocked.", match = ["git clean -f"])
+prefix_rule(pattern = ["git", "clean", "-d"], decision = "forbidden", justification = "Force clean blocked.", match = ["git clean -d"])
+prefix_rule(pattern = ["git", "clean", "-x"], decision = "forbidden", justification = "Force clean blocked.", match = ["git clean -x"])
+prefix_rule(pattern = ["git", "checkout", "."], decision = "forbidden", justification = "Whole-tree discard blocked.", match = ["git checkout ."])
+prefix_rule(pattern = ["git", "restore", "."], decision = "forbidden", justification = "Whole-tree restore blocked.", match = ["git restore ."])
+prefix_rule(pattern = ["git", "stash", "clear"], decision = "forbidden", justification = "Stash wipe blocked.", match = ["git stash clear"])
+prefix_rule(pattern = ["git", "stash", "drop"], decision = "forbidden", justification = "Stash drop blocked.", match = ["git stash drop"])
diff --git a/seed/.github/workflows/check.yml.jinja b/seed/.github/workflows/check.yml.jinja
new file mode 100644
index 0000000..7725ddd
--- /dev/null
+++ b/seed/.github/workflows/check.yml.jinja
@@ -0,0 +1,23 @@
+name: check
+
+on:
+  push:
+    branches: [main]
+  pull_request:
+    branches: [main]
+
+jobs:
+  check:
+    runs-on: ubuntu-latest
+    timeout-minutes: 15
+    steps:
+      - uses: actions/checkout@v4
+        with:
+          fetch-depth: 0
+      - uses: actions/setup-python@v5
+        with:
+          python-version: '3.12'
+      - name: Install tooling
+        run: python3 -m pip install ruff pytest
+      - name: Run check
+        run: bin/check
diff --git a/seed/.gitignore.jinja b/seed/.gitignore.jinja
index c2c105d..59db8b7 100644
--- a/seed/.gitignore.jinja
+++ b/seed/.gitignore.jinja
@@ -41,11 +41,8 @@ logs/

 # Claude Code session artifacts
 .codex_review_done
-# Validation sentinel; written by run-validate-waves.sh, never committed
-.validation_passed
 # Worker briefs, reports, and plans; local-only
 .superpowers/
-.claude/audit.log
 .claude/worktrees/
 .claude/codex-reviews/

diff --git a/seed/bin/check.jinja b/seed/bin/check.jinja
new file mode 100755
index 0000000..9938832
--- /dev/null
+++ b/seed/bin/check.jinja
@@ -0,0 +1,31 @@
+#!/usr/bin/env bash
+# bin/check - the one check for {{ project_name }}.
+# Run it yourself; CI runs it on push and PR. Exit 0 means green.
+{% raw %}set -uo pipefail
+ROOT="$(cd "$(dirname "$0")/.." && pwd)"
+cd "$ROOT"
+FAIL=0
+bad() { echo "FAIL: $*"; FAIL=1; }
+
+# No `mapfile` (bash 4+); macOS ships bash 3.2. Read into an indexed array.
+PY=()
+while IFS= read -r f; do PY+=("$f"); done < <(git ls-files '*.py')
+if [ "${#PY[@]}" -gt 0 ] && command -v ruff >/dev/null 2>&1; then
+  ruff check "${PY[@]}"          || bad "ruff check"
+  ruff format --check "${PY[@]}" || bad "ruff format --check"
+fi
+
+while IFS= read -r sh; do
+  [ -n "$sh" ] || continue
+  bash -n "$sh" || bad "bash -n $sh"
+done < <(git ls-files '*.sh')
+git diff --check HEAD -- || bad "whitespace or conflict markers"
+
+if [ -d tests ] || [ -d test ]; then
+  if command -v pytest >/dev/null 2>&1; then
+    pytest -q || bad "pytest"
+  fi
+fi
+
+if [ "$FAIL" -ne 0 ]; then echo "check: FAILED"; exit 1; fi
+echo "check: PASSED"{% endraw %}
~~~~~~~~~~~~ evidence
