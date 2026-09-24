## Ticket

~~~~~~~~~~~~ evidence
Brief:
Fix the two supervisor defects the F19 and #74 runs surfaced: a round that only changed `decisions.md` after a grader-only fail exits `no-change` before the graders can re-run, and `bin/factory status` prints PASS for a Claude that is logged out.
Where: bin/factory (main_loop, precondition_lines), docs/factory/LOOP.md (Exits, Preconditions)
Done means: the no-change exit fires only when HEAD and the decisions.md digest are both unchanged since the previous round, and preflight prints a PASS or FAIL line from `claude auth status`.
Out of scope: any other exit; the grader prompts; the Codex branch.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
The F19 run (#78, `runs/78/6a9509f0`) passed every check in round 1; the judge failed only the honest row and asked for two relabels in `decisions.md`. Round 2 made exactly those edits, which live in the run directory, not the repo, so HEAD did not move and `main_loop` exited `no-change` before the judge could see the fix. The PR had to be opened by hand.
The same night the F19 launch died twice in one second on `OAuth session expired and could not be refreshed` while `bin/factory status` printed `PASS claude on PATH`; `claude auth status` said `loggedIn: false`, and only a human login fixed it. Preflight should say so before a launch.

## Do not touch
The standing list. Except: bin/factory (main_loop and precondition_lines only), docs/factory/LOOP.md (the Exits and Preconditions sections only).
Also: bin/factory.d/; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- the stuck exit and the grader-round cap, which keep their rules
- the F16 one-time retry on an expired login, which stays
- any change to what a grader reads

## Approach
Executor: `bin/factory run` as merged in F1, with F19 and #74 merged.

Facts pinned: `main_loop` in `bin/factory` keeps `prev_head` and calls `finish no-change "HEAD is unchanged since round N"` when `git rev-parse HEAD` equals it; `$DECISIONS` is `$RUN/worker/decisions.md`; `sha256_of` is the supervisor's digest helper; `precondition_lines` loops `claude gh git jq python3 uv tmux timeout socat node` as PASS/FAIL "on PATH" lines and probes Codex with `codex login status` as PASS/INFO; `claude auth status` prints JSON with a `loggedIn` boolean (Claude Code 2.1.266) and exits 0 either way.

Change:
1. `main_loop`: the round signature is HEAD plus the digest of `$DECISIONS`; keep `prev_sig` instead of `prev_head`, and fire `finish no-change "HEAD and decisions.md are unchanged since round N"` only when both are unchanged. A round that changed only `decisions.md` proceeds to the checks and the graders as any round.
2. `precondition_lines`: after the PATH loop, one line from `claude auth status`: `PASS claude login` when `loggedIn` is true, else `FAIL claude login: claude auth status reports logged out; run claude login on the runner`. Parse the JSON with `jq -e .loggedIn`.
3. `docs/factory/LOOP.md`: the `no-change` sentence under Exits names both HEAD and `decisions.md`; the Preconditions list gains the Claude login line.

## Done checks
```done-checks
grep -q 'no-change "HEAD and decisions.md are unchanged' bin/factory && pass no-change-sig || fail no-change-sig "the no-change exit still compares HEAD alone"
grep -q 'claude auth status' bin/factory && grep -q 'claude login' bin/factory && pass login-line || fail login-line "preflight has no claude auth status line"
grep -q 'decisions.md' docs/factory/LOOP.md && grep -q 'claude auth status' docs/factory/LOOP.md && pass loop-md || fail loop-md "LOOP.md does not state the new gate and the login line"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- `bin/runner 'bin/factory status'` prints `PASS claude login` on the runner
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (Exits, Preconditions), the F19 and #74 ledger lines in .superpowers/factory/sessions/manager-2026-09-11-codex.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS no-change-sig
PASS login-line
PASS loop-md
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Opened bin/factory, bin/factory.d/lib.sh, docs/factory/LOOP.md via git ls-files; followed the Approach as written, no departures.
main_loop: keep prev_sig (HEAD plus sha256_of the decisions.md digest) instead of prev_head; no-change fires only when both are unchanged, so a grader-only relabel of decisions.md re-runs the checks and graders.
no-change message is exactly "HEAD and decisions.md are unchanged since round N" to match the no-change-sig done-check.
precondition_lines: after the PATH loop, one line from `claude auth status | jq -e .loggedIn`: PASS claude login when true, else FAIL claude login with the "run claude login on the runner" fix.
docs/factory/LOOP.md: the no-change Exits row now names HEAD and decisions.md; Preconditions gains a claude auth status loggedIn line. Left step 6 under "A run" untouched (outside the exception).
advisor: confirmed the plan; added the FACTORY_SOURCED signature test and the `bin/factory status` PASS claude login check as verification beyond the grep done-checks.
Verified: bash -n clean; signature differs on a decisions.md-only change with an identical HEAD half; precondition_lines prints PASS claude login on this runner.

~~~~~~~~~~~~ evidence

## Diff (96768f8d...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory          | 18 ++++++++++++++----
 docs/factory/LOOP.md |  3 ++-
 2 files changed, 16 insertions(+), 5 deletions(-)

diff --git a/bin/factory b/bin/factory
index 9e278cd..e3938cc 100755
--- a/bin/factory
+++ b/bin/factory
@@ -1043,7 +1043,7 @@ open_pr() {
 # ---- the loop ---------------------------------------------------------------

 main_loop() {
-  local prev_fails="" prev_head="" grader_fails=0 fails dirty touched checks head_now
+  local prev_fails="" prev_sig="" grader_fails=0 fails dirty touched checks sig_now
   notify "$KEY run started" "$KEY on $BRANCH in $WORKTREE; caps: $MAX_ROUNDS rounds, $TICKET_BUDGET_USD usd, ${MAX_HOURS}h"
   while :; do
     ROUND=$((ROUND + 1))
@@ -1057,9 +1057,12 @@ main_loop() {
     # Step 6, in order: abandon, the frozen set, a clean tree, do-not-touch, then the checks.
     grep -q '^ABANDON ' "$DECISIONS" && finish abandon "$(grep -m1 '^ABANDON ' "$DECISIONS")"
     check_frozen
-    head_now=$(git -C "$WORKTREE" rev-parse HEAD)
-    [ "$head_now" = "$prev_head" ] && finish no-change "HEAD is unchanged since round $((ROUND - 1))"
-    prev_head="$head_now"
+    # The round signature is HEAD plus the digest of decisions.md, so a round that only relabels
+    # decisions.md after a grader-only fail (#78) proceeds to the checks and graders; no-change fires
+    # only when both are unchanged since the previous round.
+    sig_now="$(git -C "$WORKTREE" rev-parse HEAD) $(sha256_of < "$DECISIONS" | cut -d' ' -f1)"
+    [ "$sig_now" = "$prev_sig" ] && finish no-change "HEAD and decisions.md are unchanged since round $((ROUND - 1))"
+    prev_sig="$sig_now"
     checks="$RUN/round-$ROUND.checks"
     dirty=$(git -C "$WORKTREE" status --porcelain)
     touched=$(do_not_touch_hits)
@@ -1189,6 +1192,13 @@ precondition_lines() { # LOOP.md, Preconditions
   for t in claude gh git jq python3 uv tmux timeout socat node; do
     command -v "$t" > /dev/null 2>&1 && echo "  PASS $t on PATH" || echo "  FAIL $t not on PATH"
   done
+  # claude on PATH is not claude logged in: a logged-out Claude fails every worker call while claude
+  # stays on PATH (#78). claude auth status prints JSON with a loggedIn boolean and exits 0 either way.
+  if claude auth status 2> /dev/null | jq -e '.loggedIn' > /dev/null 2>&1; then
+    echo "  PASS claude login"
+  else
+    echo "  FAIL claude login: claude auth status reports logged out; run claude login on the runner"
+  fi
   gh api rate_limit > /dev/null 2>&1 && echo "  PASS gh api rate_limit" || echo "  FAIL gh api rate_limit"
   claude -p --help 2>&1 | grep -q -- '--json-schema' && echo "  PASS claude -p accepts --json-schema" \
     || echo "  FAIL claude -p lacks --json-schema; every grader call needs it"
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index fd178fc..0447765 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -62,7 +62,7 @@ The run resolves them from the installed plugin cache, falling back to the check
 | Status | Meaning | Counts a round |
 |---|---|---|
 | `pr-opened` | checks and graders pass, or the grader-round cap reached with a backlog | yes |
-| `no-change` | HEAD is unchanged since the previous round | yes |
+| `no-change` | HEAD and `decisions.md` are both unchanged since the previous round | yes |
 | `stuck` | the same failing check set twice in a row | yes |
 | `ticket-defect` | round 0 found a check that passes on base or an unmeetable check | no |
 | `abandon` | an `ABANDON NAME reason` line in `decisions.md`; the owner is paged | yes |
@@ -200,6 +200,7 @@ Each new grader agent costs about 200 always-on tokens in every session of every
 ## Preconditions

 - The runner is Ubuntu with `claude`, `codex`, `gh` (logged in), `uv`, `git`, `jq`, `python3`, coreutils `timeout`, `tmux`, and `socat` on a login-shell PATH; ssh commands use `bash -lc`.
+- `claude auth status` reports `loggedIn: true` on the runner; `claude` on PATH is not `claude` logged in, so a logged-out Claude fails every worker call while `status` still shows it on PATH, and `bin/factory status` prints `FAIL claude login` (#78).
 - `gh api rate_limit` succeeds on the seat that runs stages 0, 1, 2, and 5 (F0 fixes the Mac).
 - `grill-with-docs`, `wayfinder`, and `to-tickets` are invocable on that seat.
 - `codex login status` succeeds when any ticket uses Codex.
~~~~~~~~~~~~ evidence
