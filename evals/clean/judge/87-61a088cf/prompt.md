## Ticket

~~~~~~~~~~~~ evidence
Brief:
Make round 0 prove the done checks on `base.sha` in a detached temporary worktree, so a relaunch with an edited body (a new run directory over a worktree that already carries worker commits) no longer exits `ticket-defect` because the checks pass at the worker's HEAD.
Where: bin/factory (round_zero, the relaunch comment in cmd_run), docs/factory/LOOP.md (A run, step 4)
Done means: round 0 runs the frozen checks in a worktree checked out at `base.sha`, removes that worktree afterwards, and still exits `ticket-defect` when a non-guard check passes there; a run whose ticket worktree is ahead of base reports "every non-guard check fails on base".
Out of scope: the resume rule (`round-0.checks` present means round 0 is not rerun); the guard exemption; every other exit.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
`cmd_run` keys the run directory by the body hash, so an edited body is a new run with no `round-0.checks`, while the ticket worktree and branch stay where the previous run left them. `round_zero` then runs the checks in that worktree, at the worker's HEAD, where they may already pass, and exits `ticket-defect` with "passes on <base>" for a check that fails on base.
This happened twice on 2026-09-11: the F21 relaunch (#84, run `runs/84/de36939a`) died `ticket-defect` on `medium-blocks`, and the F15 relaunch needed the same care. The workaround was to copy the first run's `round-0.checks` into the new run directory by hand.
Round 0 belongs to base only (`LOOP.md`, A run, step 4). Running it at `base.sha` in its own detached worktree makes that true in every launch, at the cost of one `git worktree add` and `remove` per run.

## Do not touch
The standing list. Except: bin/factory (round_zero and the relaunch comment in cmd_run only), docs/factory/LOOP.md (A run, step 4 only).
Also: bin/factory.d/; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- the resume branch in `cmd_run` (`round-0.checks` present means resume past the rounds on disk), which stays
- the `guard` exemption and the ticket-defect message, which stay
- `prepare_worktree`, which keeps creating the ticket worktree and branch as today

## Approach
Executor: `bin/factory run` as merged in F1, with F21 merged.

Facts pinned: `round_zero` in `bin/factory` runs `( cd "$WORKTREE" && "$RUN/frozen/checks.sh" ) > "$RUN/round-0.checks"` and calls `finish ticket-defect` for any `PASS` line whose name is not a guard; `prepare_worktree` writes `base.sha` from `origin/main` and adds the ticket worktree with `git -C "$MAIN_CHECKOUT" worktree add`, using `--detach` for a file ticket; `cmd_run` calls `round_zero` only when `$RUN/round-0.checks` is absent and otherwise resumes, under a comment that says the worktree may sit at branch HEAD; worktrees are repo siblings (`$MAIN_CHECKOUT-<key>`), never nested. `finish` with `IS_FILE=1` writes no comment, so a stub run can call `round_zero` in a subshell.

Change:
1. `round_zero`: add a detached worktree at `$(cat "$RUN/base.sha")` as a sibling named `${WORKTREE}-base` (remove that path with `git -C "$MAIN_CHECKOUT" worktree remove --force` first, silently, so a leftover from a killed round 0 never blocks the add), run `"$RUN/frozen/checks.sh"` from its root into `$RUN/round-0.checks`, then `git -C "$MAIN_CHECKOUT" worktree remove --force` it before the PASS scan, so the worktree is gone on both the defect and the clean path. A failure to add the worktree exits `stopped-environment`. Log the line as `round 0 at <base8>: every non-guard check fails on base`.
2. `cmd_run`: the relaunch comment says round 0 runs at base in its own worktree, and that a resume leaves it out because the rounds on disk already proved base.
3. `docs/factory/LOOP.md`, A run, step 4: the block runs at `base.sha` in a detached temporary worktree, never in the ticket worktree, so a relaunch with an edited body still proves the checks on base.

## Done checks
```done-checks
d=$(mktemp -d "${TMPDIR:-/tmp}/r0.XXXXXX"); git init -q "$d/main"; git -C "$d/main" -c user.email=t@t -c user.name=t commit -q --allow-empty -m base; git -C "$d/main" worktree add -q "$d/wt" -b t; echo hit > "$d/wt/flag"; git -C "$d/wt" add flag; git -C "$d/wt" -c user.email=t@t -c user.name=t commit -q -m flag; mkdir -p "$d/run/frozen"; git -C "$d/main" rev-parse HEAD > "$d/run/base.sha"; printf '#!/usr/bin/env bash\n. "%s/bin/factory.d/lib.sh"\n[ -f flag ] && pass flag || fail flag "no flag"\nexit $((n_fail > 0))\n' "$PWD" > "$d/run/frozen/checks.sh"; chmod +x "$d/run/frozen/checks.sh"; out=$(FACTORY_SOURCED=1 bash -c ". bin/factory; IS_FILE=1 KEY=t ISSUE= BODY=; RUN=\"$d/run\" WORKTREE=\"$d/wt\" MAIN_CHECKOUT=\"$d/main\" LOG=\"$d/run/factory.log\"; round_zero" 2>&1); wt=$(git -C "$d/main" worktree list | wc -l); rm -rf "$d"; grep -q 'fails on base' <<<"$out" && [ "$wt" -eq 2 ] && pass r0-at-base || fail r0-at-base "a worktree ahead of base did not report the checks failing on base, or the temporary worktree remains (worktrees=$wt): $(tail -1 <<<"$out")"
awk '/^round_zero\(\)/,/^}/' bin/factory | grep -c 'worktree remove --force' | grep -qx 2 && pass r0-clears-stale || fail r0-clears-stale "round_zero does not remove a stale -base worktree before adding it"
awk '/^round_zero\(\)/,/^}/' bin/factory | grep -q 'worktree add --detach' && awk '/^round_zero\(\)/,/^}/' bin/factory | grep -q 'worktree remove --force' && pass r0-detached || fail r0-detached "round_zero does not add and remove a detached worktree"
grep -q 'never in the ticket worktree' docs/factory/LOOP.md && pass loop-md || fail loop-md "LOOP.md step 4 does not say round 0 runs at base in its own worktree"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- the next relaunch with an edited body logs `round 0 at <base8>` and reaches round 1 without a hand-copied `round-0.checks`
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (A run, step 4), the F21 record in .superpowers/factory/sessions/manager-2026-09-11-codex.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS r0-at-base
PASS r0-clears-stale
PASS r0-detached
PASS loop-md
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Followed the Approach as written; no departures.
- round_zero: adds a detached sibling worktree `${WORKTREE}-base` at `base.sha`, runs the frozen checks from its root, removes it before the PASS scan; a leading `worktree remove --force` clears a stale worktree from a killed round 0.
- A failed `worktree add` exits `stopped-environment`, detected by the add's exit status (not `-d`), matching prepare_worktree's style.
- Kept the `ticket-defect` message byte-identical (out of scope: message stays); "message stays" reads as the user-facing text, so I inlined `cut -c1-8` in the new log line rather than adding a `base8` local.
- New log line: `round 0 at <base8>: every non-guard check fails on base`.
- cmd_run relaunch comment: says round 0 runs at base in its own detached worktree and that a resume leaves it out; the resume code is unchanged (out of scope).
- LOOP.md A run step 4: block runs at `base.sha` in a detached temporary worktree, never in the ticket worktree, removed on both paths.
- Verified no `set -e` (only `set -uo pipefail`), so the clean-run leading `worktree remove` failing is harmless.
- Verified bin/check has no coupling to round_zero or the old log string (it sources factory only for verdict_consistent); bin/check was already green before my change.
- advisor consulted before writing; it confirmed the plan and the four guard points; baseline and bin/check coupling checked as advised.
- Full done-checks block: 6 PASS, 0 FAIL.

Round 2 (blocking finding on bin/factory:644, stale-cleanup only handles a registered worktree):
- Reproduced the finding: a leftover `${WORKTREE}-base` directory on disk that git does not track makes `worktree add` fail "already exists"; round_zero exited `stopped-environment` and the leftover stayed, so every relaunch failed until hand-deletion.
- Fix (reviewer's, option A): added `git worktree prune` after the leading `worktree remove --force`, and on a failed add, if `[ -e "$wt" ]` still holds, the stopped-environment message now says "the path exists but is not a registered worktree, delete it by hand".
- Tested `worktree prune`: on this git version `worktree remove --force` already clears a stale admin entry whose directory is gone, so prune is functionally redundant here. Kept it per the reviewer's ask (one line, harmless, guards older git and locked-worktree edges).
- `rm -rf "$wt"` (self-heal) considered and rejected: reviewer explicitly chose "operator deletes by hand"; the Approach specifies git-native cleanup; the unregistered-directory state is not reachable via git alone (needs an external actor), so auto-deleting a computed path is disproportionate. Legible failure over self-heal.
- Kept `worktree remove --force` count at exactly 2 (`r0-clears-stale`); awk range still ends at `}` (`bash -n` passes). Only the block comment changed alongside the code; cmd_run comment and LOOP.md untouched (finding does not reach them).
- advisor consulted before the edit; it confirmed option A and the exact edit shape.
- Re-ran the stale repro: message now names the unregistered path. Full done-checks block: 6 PASS, 0 FAIL.

~~~~~~~~~~~~ evidence

## Diff (02848e32...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory          | 26 +++++++++++++++++++++-----
 docs/factory/LOOP.md |  3 ++-
 2 files changed, 23 insertions(+), 6 deletions(-)

diff --git a/bin/factory b/bin/factory
index 869649f..e83f0aa 100755
--- a/bin/factory
+++ b/bin/factory
@@ -635,15 +635,29 @@ limit_wait() { # result.json -> 0 after waiting, 1 when the reply is not a usage
 # Every non-guard check must fail on base; one that passes there cannot prove the ticket.

 round_zero() {
-  local out="$RUN/round-0.checks" guards name
-  ( cd "$WORKTREE" && "$RUN/frozen/checks.sh" ) > "$out" 2>&1
+  local out="$RUN/round-0.checks" guards name base wt msg
+  base=$(cat "$RUN/base.sha"); wt="${WORKTREE}-base"
+  # Round 0 belongs to base only: run the frozen checks at base.sha in a detached temporary
+  # worktree, never in the ticket worktree, which a relaunch may leave ahead of base with the
+  # checks already passing. Remove and prune clear a leftover from a killed round 0 before the
+  # add; a bare directory git does not track is reported, not deleted. Remove the worktree
+  # before the scan so it is gone on both the defect and the clean path.
+  git -C "$MAIN_CHECKOUT" worktree remove --force "$wt" > /dev/null 2>&1
+  git -C "$MAIN_CHECKOUT" worktree prune > /dev/null 2>&1
+  if ! git -C "$MAIN_CHECKOUT" worktree add --detach "$wt" "$base" > /dev/null 2>&1; then
+    msg="could not add the round-0 worktree $wt at $(cut -c1-8 "$RUN/base.sha")"
+    [ -e "$wt" ] && msg="$msg; the path exists but is not a registered worktree, delete it by hand"
+    finish stopped-environment "$msg"
+  fi
+  ( cd "$wt" && "$RUN/frozen/checks.sh" ) > "$out" 2>&1
+  git -C "$MAIN_CHECKOUT" worktree remove --force "$wt" > /dev/null 2>&1
   guards=$(dc_block | grep 'guard' | grep -oE '(^|[[:space:]])pass[[:space:]]+"?[A-Za-z0-9_.-]+' \
     | awk '{print $NF}' | tr -d '"' | sort -u)
   while read -r _ name _; do
     printf '%s\n' "$guards" | grep -qxF "$name" && continue
     finish ticket-defect "check $name passes on $(cut -c1-8 "$RUN/base.sha"), so it cannot prove the ticket; see $out"
   done < <(grep '^PASS ' "$out")
-  log "round 0: every non-guard check fails on base"
+  log "round 0 at $(cut -c1-8 "$RUN/base.sha"): every non-guard check fails on base"
 }

 # ---- steps 5 and 6: the worker round ----------------------------------------
@@ -1148,8 +1162,10 @@ cmd_run() {
       && finish stopped-environment "the advisor would be silently off: DISABLE_TELEMETRY or CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set"
     log "advisor: $WORKER_ADVISOR (the first worker call proves it attaches)"
   fi
-  # A relaunch reuses the worktree at branch HEAD, where the checks may already pass:
-  # round 0 belongs to base only, and ROUND resumes past the rounds already on disk.
+  # A relaunch with an edited body is a new run over a ticket worktree the last run left ahead of
+  # base, where the checks may already pass; round 0 runs at base in its own detached worktree, so
+  # base is what it proves. A resume (round-0.checks present) leaves round 0 out: the rounds on disk
+  # already proved base, and ROUND resumes past them.
   if [ ! -f "$RUN/round-0.checks" ]; then
     round_zero
   else
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 4e5fff0..1cfc2e0 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -47,7 +47,8 @@ The run resolves them from the installed plugin cache, falling back to the check
    A changed body is a new run; old rounds stay on disk.
 2. Record the `origin/main` sha as `base.sha`; create the sibling worktree on branch `factory/<issue>` from it; assign the issue to the operator (skipped for a file ticket).
 3. Extract the done-checks block; freeze `bin/factory`, the graders, `lib.sh`, `_common.md`, `role-settings.json`, `worker-settings.json`, the grader schemas, and the body into `frozen/`, owned outside the worker's write scope; the frozen grader prompts keep fixed evidence markers, there is no per-run string (#38).
-4. Round 0: run the block on `base.sha` from the worktree root; every non-guard check must print FAIL, else exit `ticket-defect`.
+4. Round 0: run the block at `base.sha` in a detached temporary worktree, never in the ticket worktree, which a relaunch with an edited body may leave ahead of base; every non-guard check must print FAIL, else exit `ticket-defect`.
+   The temporary worktree is added at `base.sha` and removed once the block has run, on both the defect and the clean path, so a relaunch still proves the checks on base rather than at the worker's HEAD.
 5. Worker round k: a fresh `claude -p` (`claude-opus-4-8[1m]` xhigh) or a fresh `codex exec` in the worktree with the body, `_common.md`, and from round 2 the failing check lines and every blocking finding verbatim.
    The worker writes code and `decisions.md` only.
    Every round is a fresh process for either worker; there is no fixer role.
~~~~~~~~~~~~ evidence
