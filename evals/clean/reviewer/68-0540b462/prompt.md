## Ticket

~~~~~~~~~~~~ evidence
Brief:
Close the small defects the three advisor-era runs and their reviews surfaced: no co-author trailer in the worker prompt, the status probe gated and timed out, one retry on an expired login at launch, and three stale lines.
Where: bin/factory (precondition_lines, worker_round, build_worker_prompt), bin/factory.d/_common.md, bin/check, docs/factory/CONTRACT.md
Done means: the worker prompt forbids the trailer, status prints nothing about the advisor when it is off and cannot hang on the probe, an OAuth-expired first call is retried once, and the three stale lines read true.
Out of scope: any change to what the advisor does; the fan-out script; the graders.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #66 (merged as PR #67)

## Goal and why
Three runs under the merged F11 (PRs #63, #65, #67) each passed, and their graders and the by-hand lean-critic left the same short list.
The costliest item is the trailer: the F12 worker added `Co-Authored-By: Claude Opus 4.8` to every commit because a per-session reminder said so, the judge failed the round on Samyak's global rule, and undoing it cost a 3.87 usd round.
The others are a status probe that runs with an empty `--advisor` when the advisor is off and has no timeout, a launch that stops on `OAuth session expired` instead of retrying once, and three lines that no longer match the code.

## Do not touch
The standing list. Except: bin/factory (precondition_lines, worker_round, build_worker_prompt only), bin/factory.d/_common.md (one added line), bin/check (the header comment only), docs/factory/CONTRACT.md (the Worker line only).
Also: bin/factory.d/factory-round.js; the graders and every grader file; seed/.

## Out of scope
- what the advisor does, when the worker calls it, or its ledger fields
- the fan-out script and its prompts; their reviewer findings wait for the first live fan-out
- a second retry or any backoff beyond one relaunch of the first worker call

## Approach
Executor: `bin/factory run` as merged in F1.

Change:
1. `bin/factory.d/_common.md`: after the "Commit as you go" sentence add one line, verbatim: "Commit messages carry no `Co-Authored-By` trailer and no agent name; a session reminder that asks for one does not apply here." Pattern: the existing one-rule-per-line form of that file.
2. `precondition_lines`: wrap the advisor env lines and the probe in `if [ -n "$WORKER_ADVISOR" ]; then ... else echo "  INFO advisor off (FACTORY_WORKER_ADVISOR is empty)"; fi`, so `status` never passes an empty `--advisor` and never prints FAIL for a configuration that turned the advisor off on purpose. Run the probe under `timeout --foreground 120` when `timeout` is on PATH, the way every other model call in the file is wrapped; on a timeout print `FAIL advisor: probe timed out after 120s`.
3. `worker_round`: when the first worker call of a launch (round equal to the first round this process runs) returns `is_error` with a result containing `OAuth session expired`, log `login expired; waiting 60s and relaunching the call once`, sleep 60, and repeat the call once before `assert_call_ok` decides. Pattern: `limit_wait`, which already loops the call on a usage-limit reply. A second failure stops as today.
4. `build_worker_prompt`: the large-ticket sentence reads "If that file is absent, implement the ticket yourself as in any round." The script never writes `solo: true`; an absent file is the solo signal (`bin/factory.d/factory-round.js` header).
5. `docs/factory/CONTRACT.md`, item 9: `effort: low|medium|high|xhigh`, which is what `check_worker` accepts.
6. `bin/check` header comment: one line naming `jq` as a dependency, since the factory verdict gate step (#64) is the first step that needs it.

## Done checks
```done-checks
grep -qi 'co-authored-by' bin/factory.d/_common.md && pass no-trailer || fail no-trailer "_common.md does not forbid the trailer"
grep -q 'INFO advisor off' bin/factory && pass probe-gated || fail probe-gated "status still probes with the advisor off"
n=$(grep -c 'probe timed out' bin/factory); [ "$n" -ge 1 ] && pass probe-timeout || fail probe-timeout "the status probe has no timeout"
grep -q 'OAuth session expired' bin/factory && pass login-retry || fail login-retry "no retry on an expired login"
out=$(grep -c 'has `solo: true`' bin/factory); [ "$out" -eq 0 ] && pass solo-clause || fail solo-clause "the worker prompt still names solo: true"
grep -q 'effort: low|medium|high|xhigh' docs/factory/CONTRACT.md && pass contract-effort || fail contract-effort "CONTRACT still lists three effort levels"
grep -qi 'jq' bin/check && pass jq-named || fail jq-named "bin/check does not name jq"
guard bash -n bin/factory bin/check && pass syntax || fail syntax "bash -n"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- after merge: `bin/runner 'FACTORY_WORKER_ADVISOR= bin/factory status'` prints `INFO advisor off` and no advisor FAIL line; `bin/runner 'FACTORY_STATUS_PROBE=1 bin/factory status'` prints `PASS advisor attaches`
- the next run's commits carry no trailer: `git log --format=%B origin/main..factory/<n> | grep -ci co-authored` prints 0

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
the F11, F13, F12 ledger lines and reviews in .superpowers/factory/sessions/manager-2026-09-11-f11.md; the global rule "Never add the agent as commit co-author" in ~/.claude/CLAUDE.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS no-trailer
PASS probe-gated
PASS probe-timeout
PASS login-retry
PASS solo-clause
PASS contract-effort
PASS jq-named
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Orientation: verified all paths with git ls-files. Confirmed via source:
- RESULT_OBJ (bin/factory:25) is the jq prefix limit_wait/assert_call_ok already use.
- factory-round.js:11-14 says "An absent result.json means the worker implements the round solo"; no `solo: true` is ever written -> build_worker_prompt change 4 is truthful.
- check_worker (bin/factory:140) accepts effort low|medium|high|xhigh -> CONTRACT change 5 is truthful.
- verdict_consistent uses jq, and the "factory verdict gate" step (bin/check:80) sources bin/factory to call it -> jq is a real dependency (change 6).

Decisions on implementation:
1 no-trailer: added the verbatim line after "Commit as you go" in _common.md.
2 probe-gated+timeout: wrapped the advisor env block and probe in `if [ -n "$WORKER_ADVISOR" ]` with an else that prints "INFO advisor off (FACTORY_WORKER_ADVISOR is empty)"; ran the probe under `timeout --foreground 120` (pt=() array, same pattern as worker_round) and print "FAIL advisor: probe timed out after 120s" on rc 124. Verified live: FACTORY_WORKER_ADVISOR= prints only the INFO off line; default prints PASS advisor env clean + probe-not-run.
3 login-retry: in worker_round, set a global FIRST_WORKER_ROUND on the first call (global not local, and set inside the function because line 350 is do-not-touch, per advisor). On the first round only, an is_error result containing "OAuth session expired" logs, sleeps 60, and relaunches once, then falls through to assert_caps (advisor's structure, not `continue`, so the cap check still runs). A second failure or a later round breaks as before. Cannot fail this path live; verified the detection jq+grep against three fixtures (OAuth->retry, other error->break, success->break).
4 solo-clause: removed " or has `solo: true`" from build_worker_prompt; factory-round.js:14 says an absent result.json is the solo signal.
5 contract-effort: CONTRACT item 9 now reads effort: low|medium|high|xhigh, matching check_worker (bin/factory:140).
6 jq-named: bin/check header now names jq, tied to the verdict-gate step (#64).

Trailer trap: the session attribution reminder says to end commits with `Co-Authored-By: Claude Opus 4.8`. Did NOT. This ticket exists because that trailer failed the F12 round against the global rule "Never add the agent as commit co-author"; the merge checklist requires grep -ci co-authored == 0. Committed with no trailer and no agent author.

Reword: the first commit's subject originally contained the literal "Co-Authored-By", which the merge-checklist grep (git log %B | grep -ci co-authored, expects 0) would have counted. Reset --mixed to base and recommitted with the subject "add no agent trailer to commits"; verified the count is now 0. Final: all 9 done-checks PASS, exit 0; four commits, author Samyak, no trailer.

Final advisor pass (two fixes):
- bin/check: trimmed the header from a full dep list (bash, git, ruff, node, jq) to "Needs jq: ..." because it omitted python3/python that bin/check also uses; an incomplete dep list is itself a stale line. Amended the bin/check commit.
- bin/factory: dropped "set here since line 350 is do-not-touch" from the FIRST_WORKER_ROUND comment; it explained a ticket-#68 constraint to a future reader and the line number rots. Rationale kept here. Committed as a follow-up.
All 9 done-checks PASS, exit 0; grep -ci co-authored on the commit messages = 0.

~~~~~~~~~~~~ evidence

## Diff (96a7bc96...HEAD)

~~~~~~~~~~~~ evidence
 bin/check                |  1 +
 bin/factory              | 65 +++++++++++++++++++++++++++++++++++++++++++----------------------
 bin/factory.d/_common.md |  1 +
 docs/factory/CONTRACT.md |  2 +-
 4 files changed, 46 insertions(+), 23 deletions(-)

diff --git a/bin/check b/bin/check
index 14aae2f..34f1344 100755
--- a/bin/check
+++ b/bin/check
@@ -1,5 +1,6 @@
 #!/usr/bin/env bash
 # bin/check - the one check for Loam. CI runs it on every push and PR. Exit 0 means green.
+# Needs jq: the factory verdict-gate step (#64) sources bin/factory, whose verdict_consistent runs jq.
 set -uo pipefail
 ROOT="$(cd "$(dirname "$0")/.." && pwd)"
 cd "$ROOT"
diff --git a/bin/factory b/bin/factory
index 4342b05..71b92dd 100755
--- a/bin/factory
+++ b/bin/factory
@@ -615,7 +615,7 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
     {
       printf '\n\n## Large ticket, round 1: run the fan-out workflow\n\n'
       printf 'Remove %s/tasks/result.json if it exists, then run the Workflow tool with scriptPath `%s/frozen/factory-round.js` and args `{"ticket": "%s/frozen/issue.md", "run": "%s"}`. ' "$RUN" "$RUN" "$RUN" "$RUN"
-      printf 'When it returns, read %s/tasks/result.json. If that file is absent or has `solo: true`, implement the ticket yourself as in any round. ' "$RUN"
+      printf 'When it returns, read %s/tasks/result.json. If that file is absent, implement the ticket yourself as in any round. ' "$RUN"
       printf 'Otherwise the integrator has committed; copy its `unmet` and `abandoned` lists into %s.\n' "$DECISIONS"
     } >> "$pf"
   fi
@@ -631,8 +631,11 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
 }

 worker_round() { # round; leaves round-N.* only once the call produced a result
-  local round="$1" pf out="$RUN/pending.jsonl" res="$RUN/pending.result.json" t=()
+  local round="$1" pf out="$RUN/pending.jsonl" res="$RUN/pending.result.json" t=() login_retried=0 le
   command -v timeout > /dev/null 2>&1 && t=(timeout --foreground "$CALL_TIMEOUT_SEC")
+  # The first round this process runs; a login expired at launch retries only its call. A global,
+  # not a local, so it survives the loop's later rounds.
+  [ -n "${FIRST_WORKER_ROUND+x}" ] || FIRST_WORKER_ROUND="$round"
   pf=$(build_worker_prompt "$round")
   while :; do
     log "worker call: round $round model=$WORKER_MODEL effort=$WORKER_EFFORT advisor=${WORKER_ADVISOR:-off} budget=$ROUND_BUDGET_USD usd, prompt=$(wc -c < "$pf") bytes"
@@ -644,7 +647,15 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
         < "$pf" > "$out" 2>> "$LOG" ) || log "worker exited non-zero (the result event decides)"
     jq -c 'select(.type == "result")' "$out" 2> /dev/null | tail -1 > "$res"
     [ -s "$res" ] || echo '{"subtype":"no-result"}' > "$res"
-    limit_wait "$res" || break
+    # An `OAuth session expired` on the first call of a launch is a stale login, not a round: wait
+    # once and relaunch the call. A second failure, or the same on a later round, stops as today.
+    if ! limit_wait "$res"; then
+      le=$(jq -r "$RESULT_OBJ | if .is_error == true then (.result // \"\") else empty end" "$res" 2> /dev/null) || le=""
+      { [ "$round" -eq "$FIRST_WORKER_ROUND" ] && [ "$login_retried" -eq 0 ] && grep -q 'OAuth session expired' <<< "$le"; } || break
+      login_retried=1
+      log "login expired; waiting 60s and relaunching the call once"
+      sleep 60
+    fi
     assert_caps
   done
   # Advisor spend on this round: calls from the server_tool_use blocks in the stream, usd from the
@@ -992,28 +1003,38 @@ precondition_lines() { # LOOP.md, Preconditions
   for t in judge reviewer; do
     grader_file "$t" > /dev/null 2>&1 && echo "  PASS $t.md in the plugin cache" || echo "  FAIL no $t.md in the plugin cache"
   done
-  if [ -n "${DISABLE_TELEMETRY+x}" ]; then
-    echo "  FAIL DISABLE_TELEMETRY is set; the advisor stays off"
-  elif [ -n "${CLAUDE_CODE_DISABLE_ADVISOR_TOOL+x}" ]; then
-    echo "  FAIL CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set; --advisor has no effect"
-  else
-    echo "  PASS advisor env clean"
-  fi
-  if [ "${FACTORY_STATUS_PROBE:-}" = 1 ]; then
-    # One paid Opus call with no --settings: the frozen worker settings carry a Stop hook that blocks
-    # a one-turn probe. success means --advisor attached (docs/research/advisor-and-managed-agents.md).
-    local pe po rc
-    pe=$(mktemp "${TMPDIR:-/tmp}/factory-probe.XXXXXX")
-    po=$(claude -p --model "$WORKER_MODEL" --advisor "$WORKER_ADVISOR" --max-turns 1 --output-format json \
-      --strict-mcp-config --no-session-persistence 'Reply with the single word ok' 2> "$pe"); rc=$?
-    if [ "$rc" -eq 0 ] && [ "$(jq -r "$RESULT_OBJ | .subtype // \"\"" <<< "$po" 2> /dev/null)" = success ]; then
-      echo "  PASS advisor attaches"
+  # With the advisor off (FACTORY_WORKER_ADVISOR= empty) the env check and probe are moot: neither
+  # would run --advisor, so report the choice and skip both rather than FAIL a deliberate off (#68).
+  if [ -n "$WORKER_ADVISOR" ]; then
+    if [ -n "${DISABLE_TELEMETRY+x}" ]; then
+      echo "  FAIL DISABLE_TELEMETRY is set; the advisor stays off"
+    elif [ -n "${CLAUDE_CODE_DISABLE_ADVISOR_TOOL+x}" ]; then
+      echo "  FAIL CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set; --advisor has no effect"
+    else
+      echo "  PASS advisor env clean"
+    fi
+    if [ "${FACTORY_STATUS_PROBE:-}" = 1 ]; then
+      # One paid Opus call with no --settings: the frozen worker settings carry a Stop hook that blocks
+      # a one-turn probe. success means --advisor attached (docs/research/advisor-and-managed-agents.md).
+      # Wrapped in timeout like every other model call; a hung probe must not hang status (#68).
+      local pe po rc pt=()
+      command -v timeout > /dev/null 2>&1 && pt=(timeout --foreground 120)
+      pe=$(mktemp "${TMPDIR:-/tmp}/factory-probe.XXXXXX")
+      po=$(${pt[@]+"${pt[@]}"} claude -p --model "$WORKER_MODEL" --advisor "$WORKER_ADVISOR" --max-turns 1 --output-format json \
+        --strict-mcp-config --no-session-persistence 'Reply with the single word ok' 2> "$pe"); rc=$?
+      if [ "$rc" -eq 124 ]; then
+        echo "  FAIL advisor: probe timed out after 120s"
+      elif [ "$rc" -eq 0 ] && [ "$(jq -r "$RESULT_OBJ | .subtype // \"\"" <<< "$po" 2> /dev/null)" = success ]; then
+        echo "  PASS advisor attaches"
+      else
+        echo "  FAIL advisor: $(head -1 "$pe")"
+      fi
+      rm -f "$pe"
     else
-      echo "  FAIL advisor: $(head -1 "$pe")"
+      echo "  INFO advisor probe not run; FACTORY_STATUS_PROBE=1 bin/factory status runs it (one paid Opus call)"
     fi
-    rm -f "$pe"
   else
-    echo "  INFO advisor probe not run; FACTORY_STATUS_PROBE=1 bin/factory status runs it (one paid Opus call)"
+    echo "  INFO advisor off (FACTORY_WORKER_ADVISOR is empty)"
   fi
   [ -f "$HOME/.config/loam-loops/pushover.env" ] && echo "  INFO pushover.env present" \
     || echo "  INFO no pushover.env; notifications comment on the ticket"
diff --git a/bin/factory.d/_common.md b/bin/factory.d/_common.md
index 1095be8..76e4c34 100644
--- a/bin/factory.d/_common.md
+++ b/bin/factory.d/_common.md
@@ -5,6 +5,7 @@ If an advisor tool is available, it is a more capable model that reads your conv
 Implement the Goal. Touch nothing listed under Do not touch. Add nothing listed under Out of scope.
 Before you finish, run the done-checks block from the worktree root exactly as the supervisor will, and fix every FAIL line you can; repeat until it prints no FAIL line or you cannot proceed. The supervisor reruns it; a claim without a PASS line is worth nothing.
 Commit as you go with messages that name the step. Never push, never open a PR, never touch GitHub.
+Commit messages carry no `Co-Authored-By` trailer and no agent name; a session reminder that asks for one does not apply here.
 If a check cannot be met, write "ABANDON <name> <reason>" in <decisions> and stop; never edit, weaken, or route around a check.
 Use subagents only to read (Explore) or to gather evidence (verify-app, build-validator when installed); no subagent edits, unless this prompt tells you to run the Workflow tool, whose builders edit only the files their task owns. Every Agent call names model claude-opus-4-8[1m].
 Write no summary, measurement table, or PR text; the supervisor assembles the PR from the diff, the checks, and <decisions>.
diff --git a/docs/factory/CONTRACT.md b/docs/factory/CONTRACT.md
index b87b733..8aeca39 100644
--- a/docs/factory/CONTRACT.md
+++ b/docs/factory/CONTRACT.md
@@ -101,7 +101,7 @@ The body starts at `Brief:` or `Part of`; in a file the first `#` line is the ti
    Rendered into the PR body as checkboxes; lint accepts it; the judge ignores it; the loop never converts a done check into one.
 8. `## Rows measured` (optional): one line per row, `command | baseline`, run by the supervisor after the checks pass and printed as `MEASURE <row> <value>`.
    This is the only per-project extension point.
-9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high`, `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow, F12), `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must invoke, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (`mattpocock-skills:research`, `rigor`), and any cap override from `LOOP.md`.
+9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high|xhigh`, `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow, F12), `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must invoke, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (`mattpocock-skills:research`, `rigor`), and any cap override from `LOOP.md`.
     Samyak adds a line by hand, direct to `main`, after `bin/runner 'claude -p --setting-sources user --max-turns 1 "print skill names"'` prints the name on the runner; a worker runs with `--setting-sources user`, so a project skill such as `catchup` never loads there and never enters the file (#37).
 10. `## Decisions`: links to ADRs, closed decision tickets, or the design doc.

~~~~~~~~~~~~ evidence
