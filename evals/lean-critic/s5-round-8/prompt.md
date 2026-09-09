## Ticket

~~~~~~~~~~~~ evidence
# S5: live verification and release v3.0.0

Part of #14

Execution ticket. Blocked on S4 merging. Spec: `02-IMPLEMENTATION-SPEC.md` commits 5 to 7 and its measurement section. Runs alone, last. Edits no `seed/` and no `bin/` files; S3 already rewrote `bin/release.sh` and verified the keys.

## Goal and why

Prove the whole v3 tree live, record the complete before/after table, and ship v3.0.0 with one command. `DESIGN.md` "Target numbers", "Migration", and its final done check.

## Files owned

- `docs/HARNESS.md` numbers (append-only)
- The PR body and the GitHub Release

### Addendum (2026-09-07, after round 5, owner and manager)

1. Done check 1, sandbox probes: `socat` was installed on the verification host at about 18:45 UTC, after the round 1 probes ran. Every round 1 probe row that reported the sandbox disabled is void. Re-run all seven probes in a freshly rendered project with the sandbox active (confirm `socat -V` prints a version first) and replace those rows in measurements.md, in the appended HARNESS.md table, and in the PR body. If a probe still does not enforce, ship the truthful result with a note per done check 3; do not edit `seed/.claude/settings.json` or `seed/.codex/rules/loam.rules` (S3's files). Put the combined-short-flags gap (`rm -rfv`, `git clean -fdx`) in the PR body's backlog list.
2. Done check 5 (merge with a green check run, `bin/release.sh 3.0.0`, the v3.0.0 tag, the GitHub Release, the ship time) is run by the owner after this PR merges. It cannot happen inside the loop, so it is SKIP here by design. The judge scores "correct" without it. The PR body lists it under a heading "Owner after merge", not under unmet checks.
3. Done check 4: link S4's merged PR #30 body for the recall result.

## Rows measured

Every row of the `DESIGN.md` target table, measured with the spec's commands, not estimated: latency per Bash call, latency per Edit or Write, check wall time local and CI, always-on tokens, shipped hooks, seed hook and lib lines, bin plus tests lines, marketplace skills shipped, ship time after merge. Compare to `.superpowers/lean-v3/baseline/S0-BASELINE.md`.

## Done checks

1. Live verification in a rendered project, all outputs pasted in the PR body: `rm -rf x` denied; `git checkout .` denied; out-of-workspace write fails; `python3 -c "open('.env').read()"` fails inside the sandbox; `git ls-remote origin` succeeds; a plain `git status` Bash call shows no hook output; the Codex execpolicy probe reports the force families forbidden.
2. Copier update: render v2.3.0 into a temp dir, then `uvx copier update --trust --vcs-ref=HEAD` from main; the updated `.claude/settings.json` names only the two kept hooks and no missing script.
3. The full before/after table is in the PR body and the after column is appended to `docs/HARNESS.md`. Where a target is missed, the truthful number is shipped with a note; scope is not widened to chase it.
4. The 8-scenario recall test result from S4 is linked, not re-run, unless S4's transcript lines are missing.
5. PR merged with a green `check` run; `bin/release.sh 3.0.0` exits 0; `git ls-remote origin refs/tags/v3.0.0` resolves; GitHub Release v3.0.0 is published; the ship-after-merge time is recorded (target under 5 minutes).
6. Verification protocol below completed (the work sample here is the final after-number).

## Verification protocol (every execution ticket, before its PR)

1. Measure the rows this ticket owns with the commands in the measurement section of `02-IMPLEMENTATION-SPEC.md`.
2. Work sample: render a project from the branch into a temp dir (`uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=sample . <dir>`), run the fixed task from `.superpowers/lean-v3/baseline/S0-BASELINE.md` with `claude -p "<task>" --model fable --output-format stream-json --verbose --include-hook-events > sample.jsonl`, then `python3 .superpowers/lean-v3/tools/summarize_sample.py sample.jsonl --check "<the task's own test>"`.
Steps 3 to 6 (frozen checks, fresh-context judge, fixer, push, PR) belong to the loop supervisor; see `loops/DESIGN.md`.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS worktree-clean
PASS copier-update
PASS harness-after-column (seed/docs/HARNESS.md, 8 data rows under the before/after header on line 93)
PASS run-artefacts
SKIP probe-rm-rf-denied: needs a live rendered project and an interactive Claude session
SKIP probe-git-checkout-dot-denied: needs a live rendered project and an interactive Claude session
SKIP probe-out-of-workspace-write-fails: needs a live rendered project and an interactive Claude session
SKIP probe-env-read-blocked-in-sandbox: needs a live rendered project with the sandbox active
SKIP probe-git-ls-remote-succeeds: needs a live rendered project with network and a git remote
SKIP probe-no-hook-output-on-git-status: needs a live rendered project and an interactive Claude session
SKIP probe-codex-execpolicy-forbidden-families: needs a live rendered project and the codex CLI
SKIP recall-result-linked: needs S4's merged PR body to link the 8-scenario recall result
SKIP pr-merged-green: needs the owner to merge this PR with a green check run, which cannot happen inside the loop
SKIP release-tag-v3: needs the owner to run bin/release.sh 3.0.0 after the merge, so origin carries refs/tags/v3.0.0
SKIP github-release-published: needs the owner to publish GitHub Release v3.0.0 after the merge
SKIP ship-time-recorded: needs the owner to time the merge-to-release window
SUMMARY pass=4 fail=0 skip=12

~~~~~~~~~~~~ evidence

## pr-body.md (worker-authored)

~~~~~~~~~~~~ evidence
# S5: live verification and release v3.0.0

Closes #25. Part of #14.

This is the verification round for the v3 tree: every DESIGN target row measured
in a live rendered project, not estimated. It adds one commit, the measured
before/after table in `seed/docs/HARNESS.md`, and it hands the release itself to
the owner.

## What changed

1. `seed/docs/HARNESS.md` gains a "Measured cost, v2.3.0 to v3.0.0" table with
   every DESIGN target row.
2. Three measured accepted risks are appended to the same file: deny entries match
   a literal prefix, so combined short flags run; the sandbox silently degrades on
   a host without its dependencies; and `git ls-remote` prints a credential-lock
   warning under the sandbox while still exiting 0.
3. The change to that file is append-only. No `seed/` file outside
   `docs/HARNESS.md`, no `bin/` file.

## The DESIGN target table

| Row | Before | After | Target | Met |
|---|---|---|---|---|
| Added latency per Bash call | 414 ms (DESIGN, 5 hooks); 7 `PreToolUse` entries in settings.json | 0 events, 0 ms | 0 ms | yes |
| Added latency per Edit or Write | 1 ruff run per edit | 0 `PostToolUse` hooks | 0 ms | yes |
| Check wall time, local | 207 s | 4.8 s | under 45 s | yes |
| Check wall time, CI | 207 s | 7 s step, 30 s job | under 45 s | yes |
| Always-on tokens per generated project | about 1966 (7862 bytes) | about 281 (1125 bytes) | under 400 | yes |
| Shipped hooks | 15 | 2 | 2 | yes |
| Seed hook and lib lines | 2309 | 71 | under 120 | yes |
| `bin/` plus `bin/tests/` lines | 11377 | 1525 | under 2000 | yes |
| Marketplace skills shipped | 26 | 3 | 3 | yes |
| Ship after merge | hours to days | not measured | one command, under 5 min | owner runs it after merge |

Token figures are byte counts divided by four.
The 1525 figure does include tests: `bin/tests/` lives inside `bin/`, so the
`find bin` command walks it, and 723 of the 1525 lines are test files.
Full commands and the CI run id are in
`.superpowers/lean-v3/loops/runs/S5/measurements.md`.

## Live verification in a rendered project

Rendered from this branch with
`uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=check`, then
given a git repo with a GitHub `origin` and a one-line `.env`.
Probes ran as `claude -p --model fable --permission-mode bypassPermissions`, the
mode where deny rules are supposed to hold anyway.

| Probe | Expected | Result |
|---|---|---|
| `rm -rf x` | denied | `Permission to use Bash with command rm -rf x has been denied.` |
| `rm -Rf x` (control, not in the owner's global deny list) | denied | `Permission to use Bash with command rm -Rf x has been denied.` |
| `git checkout .` | denied | `Permission to use Bash with command git checkout . has been denied.` |
| `printf hi > /tmp/loam-escape-probe.txt` | fails | failed, `Read-only file system`, no file created |
| `python3 -c "open('.env').read()"` | fails | failed, `PermissionError: [Errno 13] Permission denied: '.env'` |
| `git ls-remote origin` | succeeds | succeeded, exit 0, refs listed |
| `git status` | no hook output | no hook output; 0 `PreToolUse` and 0 `PostToolUse` events in the stream |

Codex, `codex-cli 0.153.4`, `codex execpolicy check --rules .codex/rules/loam.rules`:
`git push --force`, `git push -f`, `git push --force-with-lease`,
`git reset --hard`, `git checkout .`, `git stash drop`, `rm -rf`, and
`git clean -f -d` all return `forbidden`. `git status` correctly matches nothing.

### The sandbox enforces, and it degrades silently without its dependencies

The two file probes above are the ones that matter for done check 1, and both now
fail as required, with the sandbox active (`bwrap` and `socat` both present).
`socat -V`, run before the probes:

```
socat by Gerhard Rieger and contributors - see www.dest-unreach.org
socat version 1.8.0.0 on 03 Jul 2026 12:45:49
```

`rm -Rf x` stays denied with the sandbox on, so `autoAllowBashIfSandboxed` does not
override a deny entry.

Earlier rounds of this loop measured those two probes on the same host before
`socat` was installed. Claude Code then printed
`Sandbox disabled: ... socat not installed` and ran unsandboxed, because
`sandbox.failIfUnavailable` is false by design, so both probes succeeded. That is a
host property, not a template bug: no settings key was rejected or dropped. Both
sides of it are now in `docs/HARNESS.md` accepted risks, so a user on a host
without the dependencies knows the sandbox is not guarding their files.

One more measured gotcha, also in `docs/HARNESS.md`: under the sandbox
`git ls-remote origin` prints
`fatal: unable to get credential storage lock in 1000 ms: Read-only file system`
on stderr and still exits 0, because git's credential lock lives outside the
workspace.

### Gap found: combined short flags escape both deny lists

`rm -rfv y` ran and deleted `y/`. `git clean -fdx -n` ran (dry run, allowed but nothing deleted). Codex returns no decision
for either. `rm -rf`, `rm -Rf`, and `git clean -f -d` are blocked, so the listed
spellings do work; the lists cover the honest mistake, not a rewording.
This is the DESIGN caveat made concrete. It is documented in the accepted risks
and left unfixed on purpose: the fix edits `seed/.claude/settings.json` and
`seed/.codex/rules/loam.rules`, which this ticket does not own, and it should not
ride into a release commit unreviewed.

## Backlog

- Combined short flags escape both deny lists: `rm -rfv` and `git clean -fdx` are
  not caught. The fix adds deny entries to `seed/.claude/settings.json` and rules
  to `seed/.codex/rules/loam.rules`, neither owned by this ticket.

## Copier update from v2.3.0

Render v2.3.0, `git init` and commit, `uvx copier update --trust --defaults
--vcs-ref HEAD`. Every hook `command` string in the updated
`.claude/settings.json` names one of the two kept hooks, and every referenced
script exists. `checks/S5.sh` reports `PASS copier-update`.

## Recall test

Not re-run, per done check 4. The 8-scenario result is in PR #30 (`lean/s4`) and
`.superpowers/lean-v3/loops/runs/S4/measurements.md`.

## Work sample

The fixed S0 task, run with `--model fable` in a project rendered from this branch.

| Row | S0 baseline | This branch |
|---|---|---|
| elapsed_seconds | 125.7 | 11.1 |
| turns | 18 | 2 |
| tool_calls | 16 | 1 |
| hook_events | 306 | 14 |
| cost_usd | 1.10 | 0.46 |
| denials | 0 | 0 |
| task check | 1 passed | 1 passed, exit 0 |

The 14 remaining hook events are the owner's global hooks, not the rendered
project's.

## Owner after merge

No loop merges its own pull request, so these five are not done here:

1. Merge this PR with a green `check` run.
2. Run `bin/release.sh 3.0.0`.
3. Confirm `git ls-remote origin refs/tags/v3.0.0` resolves.
4. Confirm GitHub Release v3.0.0 is published.
5. Record the merge-to-release time; the target is under 5 minutes.

## Unverified

- The `check` run on this PR. This round never pushes.
- Sandbox behaviour on a host without `bwrap` or `socat`. Measured here only in
  the degraded direction: with `socat` absent the sandbox silently does not start.
  Other hosts and other missing dependencies are untested.
- The push-guard ruleset blocking a real push to `main`. Creating a GitHub repo
  to test it is out of scope for an unattended round; it is still open from S4.
- All seven done-check-1 probes and the Codex execpolicy table. `checks/S5.sh`
  emits no `PASS` line for any of them; it reports `SKIP probe-rm-rf-denied`,
  `SKIP probe-git-checkout-dot-denied`, `SKIP probe-out-of-workspace-write-fails`,
  `SKIP probe-env-read-blocked-in-sandbox`, `SKIP probe-git-ls-remote-succeeds`,
  `SKIP probe-no-hook-output-on-git-status`, and
  `SKIP probe-codex-execpolicy-forbidden-families`. The tables above rest only on
  worker-pasted `claude -p` and `codex execpolicy` output, re-run in round 6 with
  `socat` present.
- The recall link. `checks/S5.sh` reports `SKIP recall-result-linked`, so the
  pointer to PR #30 and `loops/runs/S4/measurements.md` is unchecked by the harness.
- The `rm -rf` denial as evidence about the rendered settings alone. The owner's
  global deny list contains the same rule. The `rm -Rf` control probe is the
  clean evidence.

~~~~~~~~~~~~ evidence

## Diff (main...HEAD)

~~~~~~~~~~~~ evidence
 seed/docs/HARNESS.md | 37 +++++++++++++++++++++++++++++++++++++
 1 file changed, 37 insertions(+)

diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index 3b38f2f..36a589e 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -84,3 +84,40 @@ removing it would cause a mistake.
 The owner's `~/.claude/` files are personal and are not shipped by the template.
 A global hook in `~/.claude/hooks/` repeats the "prefer targeted edits" rule for
 every project on that machine, so the owner sees it twice; nobody else does.
+
+## Measured cost, v2.3.0 to v3.0.0
+
+Rendered-project rows measured in a `copier copy` render of each version;
+repo-side rows measured in the repo itself.
+
+| Row | Before (v2.3.0) | After (v3.0.0) |
+|---|---|---|
+| Hooks shipped in `.claude/hooks/` | 15 | 2 |
+| `PreToolUse` hook entries matching Bash | 7 | 0 |
+| Hook runs per Edit or Write | 1 ruff run | 0 |
+| Always-on prose bytes (`CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
+| Check wall time, one script | 207 s (`bin/verify-template.sh`) | 5 s local, 7 s in CI |
+| Seed hook and lib lines | 2309 | 71 |
+| `bin/` plus `bin/tests/` lines | 11377 | 1525 |
+| Marketplace skills shipped | 26 | 3 |
+
+Token figures anywhere in this file are byte counts divided by four, not a
+tokenizer result.
+
+## Accepted risks measured in v3.0.0
+
+- A deny entry matches a literal prefix, so a combined short flag is a different
+  string and runs. Measured in a rendered project: `rm -rfv y` deleted `y/`, and
+  `git clean -fdx -n` ran (dry run), while `rm -rf` and `rm -Rf` were denied. Codex
+  agrees: `codex execpolicy check` returns no decision for either. Both deny
+  lists cover the honest mistake, not a deliberate rewording.
+- "Where the host supports it" is load-bearing. With `bwrap` and `socat` present
+  the sandbox enforces: `python3 -c "open('.env').read()"` raises
+  `PermissionError`, and a write to `/tmp` fails with `Read-only file system`.
+  Drop `socat` and Claude Code prints `Sandbox disabled` at startup and runs
+  unsandboxed, because `failIfUnavailable` is false, and both commands then
+  succeed. Install the sandbox dependencies, or treat the deny list as the only
+  file guard.
+- Under the sandbox, git writes its credential lock outside the workspace, so
+  `git ls-remote origin` prints `fatal: unable to get credential storage lock in
+  1000 ms: Read-only file system` on stderr and still exits 0. The line is noise.
~~~~~~~~~~~~ evidence
