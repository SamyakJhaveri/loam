## Ticket

~~~~~~~~~~~~ evidence
Brief:
Give the Opus worker a Fable advisor it consults mid-round before decisions that are expensive to reverse, and put the advisor's calls and cost on the ledger line.
Where: bin/factory (the roles block, worker_round, record, cmd_run, precondition_lines), bin/factory.d/_common.md
Done means: the worker call carries --advisor fable, the worker prompt names when to consult, the launch refuses to run with the advisor silently off, and every worker ledger line carries advisor_calls and advisor_usd.
Out of scope: the judge and reviewer calls; MAX_PARALLEL; .superpowers/lean-v3/loops/; seed/.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #56 (merged as PR #57)

## Goal and why
Today Fable only grades after the round; it never steers the worker while the work is being done.
Claude Code's advisor tool lets the main model consult a stronger model mid-task, and it works under `-p` from 2.1.260 (`docs/research/advisor-and-managed-agents.md`).
One flag on the worker call, one paragraph in the worker prompt, one environment guard, two ledger fields.
The ledger decides whether it stays, on cost or on quality: keep the advisor if usd per ticket drops, or if usd rises but the graders catch fewer or less severe defects (judge fixes, reviewer findings by severity, rounds to pass) against the F1, F3, and F10 runs; cut it only if usd rises and quality does not move (Samyak, 2026-09-10).

## Do not touch
The standing list. Except: bin/factory (the roles block, worker_round, record, cmd_run, precondition_lines), bin/factory.d/_common.md.
Also: the judge and reviewer calls in call_json; MAX_PARALLEL; .superpowers/lean-v3/loops/; seed/.

## Out of scope
- any advisor on the grader calls
- a forced per-round consultation; the worker decides when to call
- a per-call cap on advisor spend; ROUND_BUDGET_USD already bounds the round
- `--bare` on any call; the advisor under `--bare` is unverified

## Approach
Executor: `bin/factory run` as merged in F1.

Facts pinned on 2026-09-10 before this ticket was written, each with the command that resolved it:
- The advisor attaches under `-p` on this account without a consent step, and the launch does not error. Command, on the Mac at Claude Code 2.1.266: `claude -p --model 'claude-opus-4-8[1m]' --advisor fable --max-turns 3 --output-format json --strict-mcp-config --no-session-persistence 'Consult the advisor tool once about whether to reply in lowercase, then reply with the single word ok'`; exit 0, result `subtype` `success`.
- An advisor call is an assistant event whose content holds `{"type":"server_tool_use","name":"advisor","input":{}}`; the guidance comes back as `advisor_tool_result` with `advisor_redacted_result`, so the transcript never shows Fable's text. Command: `jq -c '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="server_tool_use" and .name=="advisor")] | length'` on that output printed 1.
- The cost split is in the result event: `modelUsage` has one key per model id, and `modelUsage["claude-fable-5-1"].costUSD` is the advisor's spend (0.28 usd for one call that read 26,046 uncached tokens; the Opus turn cost 0.26). Command: `jq 'last(.[] | select(.type=="result")) | .modelUsage'`.
- The doc's launch-error list: a missing Fable consent makes `claude --advisor fable` exit at launch with a message pointing to `/model fable`; a background session starts without the advisor instead. Under `-p` the failure is loud: the first worker call answers `is_error` and `assert_call_ok` exits `stopped-environment` before any work, so the launch needs no probe of its own. The two silent cases are `DISABLE_TELEMETRY` (flag fetching off, the advisor stays off) and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` (the flag is accepted with no effect); those are environment checks. A one-turn probe cannot run under the frozen worker settings: their Stop hook exits 2 whenever `LOAM_CHECKS` is unset or a check fails, so it would block the probe's stop (blind review, 2026-09-10).

Change, in this order:
1. Roles block (`bin/factory`, next to `GRADER_MODEL`): `WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-fable}"` with the comment that `FACTORY_WORKER_ADVISOR=` (explicit empty) disables the flag. No colon in the expansion: `:-` would overwrite an empty value and could never disable. The bare name is never read, same as the other roles.
2. The worker call in `worker_round`: append `${WORKER_ADVISOR:+--advisor "$WORKER_ADVISOR"}` after `--effort "$WORKER_EFFORT"`. `bin/factory run` has no fixer role, so no other call changes. Add the advisor to the `worker call:` log line.
3. `bin/factory.d/_common.md`: add this paragraph after the Approach line, verbatim:
   "If an advisor tool is available, it is a more capable model that reads your conversation so far and sends back guidance. Consult it before you commit to a decision that is expensive to reverse: a file layout, a public interface, a check you cannot make fail, a scope cut. Do routine implementation yourself. When you consult, act on the guidance and record in <decisions> what you changed."
   It is a no-op when no advisor is attached. Pattern: the cookbook worker prompt quoted in `docs/research/advisor-and-managed-agents.md`, with the decisions named for this codebase.
4. Environment guard, two homes. In `cmd_run`, after `exec_frozen` and before round 0, when `WORKER_ADVISOR` is non-empty: `finish stopped-environment "the advisor would be silently off: DISABLE_TELEMETRY or CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set"` when either variable is in the environment, else log `advisor: $WORKER_ADVISOR (the first worker call proves it attaches)`. In `precondition_lines`: print `FAIL DISABLE_TELEMETRY is set; the advisor stays off` or `FAIL CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set; --advisor has no effect` when set, else `PASS advisor env clean`. Then, only when `FACTORY_STATUS_PROBE=1`, run `claude -p --model "$WORKER_MODEL" --advisor "$WORKER_ADVISOR" --max-turns 1 --output-format json --strict-mcp-config --no-session-persistence 'Reply with the single word ok'` with no `--settings` (the frozen worker settings carry the Stop hook, which blocks a one-turn probe) and print `PASS advisor attaches` when the exit status is 0 and the result `subtype` is `success`, else `FAIL advisor: <first stderr line>`; without the variable print `INFO advisor probe not run; FACTORY_STATUS_PROBE=1 bin/factory status runs it (one paid Opus call)`.
5. Ledger. In `worker_round`, after the result file exists and before `record`, compute `advisor_calls` from the stream (the jq above, over `select(.type == "assistant")` events of the jsonl) and `advisor_usd` from the result (`[.modelUsage | to_entries[] | select(.key != $m) | .value.costUSD] | add // 0` with `$m` the worker model id). Add both fields to the ledger line `record` writes for the worker role; grader lines carry 0. Print them in the `worker round N:` log line.

Do not touch: seed/, the judge and reviewer calls, MAX_PARALLEL, .superpowers/lean-v3/loops/.

## Done checks
```done-checks
grep -q 'WORKER_ADVISOR' bin/factory && pass roles || fail roles "no WORKER_ADVISOR in the roles block"
grep -q -- '--advisor "\$WORKER_ADVISOR"' bin/factory && pass flag || fail flag "the worker call has no --advisor"
grep -qi 'advisor' bin/factory.d/_common.md && pass prompt || fail prompt "no consult policy in _common.md"
n=$(grep -c -- '--advisor' bin/factory); [ "$n" -ge 2 ] && pass probe || fail probe "expected the flag on the worker call and the status probe; found $n"
grep -q 'advisor_usd' bin/factory && grep -q 'advisor_calls' bin/factory && pass ledger || fail ledger "the ledger has no advisor fields"
grep -q 'DISABLE_TELEMETRY' bin/factory && pass telemetry-guard || fail telemetry-guard "status does not warn that DISABLE_TELEMETRY turns the advisor off"
grep -q 'CLAUDE_CODE_DISABLE_ADVISOR_TOOL' bin/factory && pass env-guard || fail env-guard "cmd_run does not refuse to launch with the advisor silently off"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- before launch: `bin/runner 'env | grep -i "DISABLE_TELEMETRY\|ADVISOR"'` prints nothing, and `bin/runner 'FACTORY_STATUS_PROBE=1 bin/factory status'` prints `PASS advisor attaches`
- after pr-opened: write the ledger line in the manager session file, per round: worker cost_usd, advisor_calls, advisor_usd, judge and reviewer cost_usd, rounds to pass, count of judge fixes, reviewer findings by severity, against the F1, F3, and F10 runs
- keep the advisor if usd per ticket drops, or if quality improves (fewer or less severe grader findings, fewer rounds) at a higher usd; cut it (set `FACTORY_WORKER_ADVISOR=` in the runner timer) only if usd rises and quality does not move

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 60 turns

## Decisions
docs/research/advisor-and-managed-agents.md (What the factory takes), docs/factory/LOOP.md (Worker calls), the 2026-09-09 brainstorm plan `~/.claude/plans/i-want-to-take-cached-peach.md` (blind review verdict FIX, applied)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS roles
PASS flag
PASS prompt
PASS probe
PASS ledger
PASS telemetry-guard
PASS env-guard
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Read Where/Do-not-touch/Approach paths via git ls-files; all present except .superpowers/lean-v3/loops (absent, nothing to touch there).
Followed the Approach section verbatim: five changes to bin/factory plus the one paragraph in _common.md; no departures.
Step 1 roles block: WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-fable}" (no colon, so FACTORY_WORKER_ADVISOR= disables); placed next to GRADER_MODEL.
Step 2 worker call: appended ${WORKER_ADVISOR:+--advisor "$WORKER_ADVISOR"} after --effort; verified it splits into two argv words when set and vanishes when empty. worker-call log shows advisor=${WORKER_ADVISOR:-off}.
Step 3 _common.md: consult paragraph placed after the Approach line, one physical line to match the file's one-instruction-per-line convention.
Step 4 env guard: env-var detection uses ${VAR+x} (variable present, even if empty) not ${VAR:-} (non-empty), matching "in the environment" and the merge-checklist env-grep semantics; fail closed. cmd_run guard placed after exec_frozen/TIMEOUT_G and before round 0 so it runs on every launch (including relaunch). Probe in precondition_lines runs only under FACTORY_STATUS_PROBE=1, with no --settings; captures exit status into rc immediately.
Step 5 ledger: record() gains optional $5/$6 (advisor_calls, advisor_usd) defaulting to 0, so the grader call site (4 args) carries 0 unchanged. advisor_calls via jq -s over the jsonl stream; advisor_usd from (.modelUsage // {}) minus the worker model key, guarded to survive the no-result fallback. record's round log prints the advisor fields only for role==worker.
Verified: jq computations on sample stream/result (acalls=2, ausd=0.28), record lines valid for worker and grader, all env-var branches, done-checks 9/9 PASS exit 0, bin/check green (31 tests), tree clean.

~~~~~~~~~~~~ evidence

## Diff (634c984e...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory              | 58 ++++++++++++++++++++++++++++++++++++++++++++++++++--------
 bin/factory.d/_common.md |  1 +
 2 files changed, 51 insertions(+), 8 deletions(-)

diff --git a/bin/factory b/bin/factory
index 1855201..afee148 100755
--- a/bin/factory
+++ b/bin/factory
@@ -337,6 +337,7 @@ MAX_ROUNDS=6; ROUND_BUDGET_USD=15; GRADER_BUDGET_USD=5; TICKET_BUDGET_USD=60
 DAILY_BUDGET_USD=150; MAX_HOURS=8; MAX_TURNS=200; CALL_TIMEOUT_SEC=5400; MAX_PARALLEL=1
 WORKER_MODEL="${FACTORY_WORKER_MODEL:-claude-opus-4-8[1m]}"   # ARCHITECTURE.md, Models and roles (2026-09-09)
 GRADER_MODEL="${FACTORY_GRADER_MODEL:-fable}"
+WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-fable}"   # mid-round advisor on the worker call; FACTORY_WORKER_ADVISOR= (explicit empty) disables the flag. No colon: :- could never disable. The bare name is never read.
 WORKER_EFFORT=xhigh        # the ticket's `effort:` line overrides
 GRADER_EFFORT=medium
 GRADER_FAIL_ROUNDS=2      # grader-fail rounds allowed once the checks pass (LOOP.md, Grader-round cap)
@@ -502,18 +503,20 @@ exec_frozen() {
 ticket_spent() { jq -s '[.[].cost_usd // 0] | add // 0' "$LEDGER"; }
 daily_spent()  { jq -s --arg d "$(today)" '[.[] | select(.date == $d) | .cost_usd // 0] | add // 0' "$DAILY"; }

-record() { # round role model result.json
-  local line
+record() { # round role model result.json [advisor_calls] [advisor_usd]
+  local line acalls="${5:-0}" ausd="${6:-0}"
   line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
+    --argjson acalls "$acalls" --argjson ausd "$ausd" \
     "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(.total_cost_usd // 0), \
 duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:((.permission_denials // []) | length), \
-subtype:(.subtype // \"unknown\"), ts:\$ts}" "$4" 2> /dev/null) \
+subtype:(.subtype // \"unknown\"), advisor_calls:\$acalls, advisor_usd:\$ausd, ts:\$ts}" "$4" 2> /dev/null) \
     || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-      '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", ts:$ts}')
+      --argjson acalls "$acalls" --argjson ausd "$ausd" \
+      '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", advisor_calls:$acalls, advisor_usd:$ausd, ts:$ts}')
   printf '%s\n' "$line" >> "$LEDGER"
   printf '%s' "$line" | jq -c --arg date "$(today)" --arg ticket "$KEY" \
     '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$DAILY"
-  log "$2 round $1: $(printf '%s' "$line" | jq -r '"cost=\(.cost_usd) usd, turns=\(.num_turns), denials=\(.denials), \(.duration_ms)ms, \(.subtype)"')"
+  log "$2 round $1: $(printf '%s' "$line" | jq -r '"cost=\(.cost_usd) usd, turns=\(.num_turns), denials=\(.denials), \(.duration_ms)ms, \(.subtype)" + (if .role == "worker" then ", advisor_calls=\(.advisor_calls), advisor_usd=\(.advisor_usd)" else "" end)')"
 }

 assert_caps() { # before every model call; the daily cap is "the next call could exceed it"
@@ -613,10 +616,10 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   command -v timeout > /dev/null 2>&1 && t=(timeout --foreground "$CALL_TIMEOUT_SEC")
   pf=$(build_worker_prompt "$round")
   while :; do
-    log "worker call: round $round model=$WORKER_MODEL effort=$WORKER_EFFORT budget=$ROUND_BUDGET_USD usd, prompt=$(wc -c < "$pf") bytes"
+    log "worker call: round $round model=$WORKER_MODEL effort=$WORKER_EFFORT advisor=${WORKER_ADVISOR:-off} budget=$ROUND_BUDGET_USD usd, prompt=$(wc -c < "$pf") bytes"
     rm -f "$out"
     ( cd "$WORKTREE" && LOAM_CHECKS="$RUN/frozen/checks.sh" ${t[@]+"${t[@]}"} claude -p \
-        --model "$WORKER_MODEL" --effort "$WORKER_EFFORT" --permission-mode bypassPermissions --strict-mcp-config \
+        --model "$WORKER_MODEL" --effort "$WORKER_EFFORT" ${WORKER_ADVISOR:+--advisor "$WORKER_ADVISOR"} --permission-mode bypassPermissions --strict-mcp-config \
         --setting-sources user --settings "$RUN/frozen/worker-settings.json" --max-turns "$MAX_TURNS" \
         --max-budget-usd "$ROUND_BUDGET_USD" --output-format stream-json --verbose --include-hook-events \
         < "$pf" > "$out" 2>> "$LOG" ) || log "worker exited non-zero (the result event decides)"
@@ -625,7 +628,16 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
     limit_wait "$res" || break
     assert_caps
   done
-  record "$round" worker "$WORKER_MODEL" "$res"
+  # Advisor spend on this round: calls from the server_tool_use blocks in the stream, usd from the
+  # result's modelUsage minus the worker's own line (docs/research/advisor-and-managed-agents.md).
+  local acalls ausd
+  acalls=$(jq -s '[.[] | select(.type == "assistant") | .message.content[]?
+    | select(.type == "server_tool_use" and .name == "advisor")] | length' "$out" 2> /dev/null) || acalls=0
+  [ -n "$acalls" ] || acalls=0
+  ausd=$(jq -r --arg m "$WORKER_MODEL" \
+    '[(.modelUsage // {}) | to_entries[] | select(.key != $m) | .value.costUSD] | add // 0' "$res" 2> /dev/null) || ausd=0
+  [ -n "$ausd" ] || ausd=0
+  record "$round" worker "$WORKER_MODEL" "$res" "$acalls" "$ausd"
   assert_call_ok worker "$res"
   mv "$pf" "$RUN/round-$round.prompt.md"
   mv "$out" "$RUN/round-$round.jsonl"
@@ -878,6 +890,13 @@ cmd_run() {
   [ "$IS_FILE" = 1 ] && trap 'git -C "$MAIN_CHECKOUT" worktree remove --force "$WORKTREE" > /dev/null 2>&1' EXIT
   TIMEOUT_G=()
   command -v timeout > /dev/null 2>&1 && TIMEOUT_G=(timeout --foreground "$CALL_TIMEOUT_SEC")
+  # The advisor attaches through a feature flag claude fetches; two env vars turn it silently off.
+  # Refuse to launch rather than run a worker that thinks it has an advisor and does not (F11).
+  if [ -n "$WORKER_ADVISOR" ]; then
+    { [ -n "${DISABLE_TELEMETRY+x}" ] || [ -n "${CLAUDE_CODE_DISABLE_ADVISOR_TOOL+x}" ]; } \
+      && finish stopped-environment "the advisor would be silently off: DISABLE_TELEMETRY or CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set"
+    log "advisor: $WORKER_ADVISOR (the first worker call proves it attaches)"
+  fi
   # A relaunch reuses the worktree at branch HEAD, where the checks may already pass:
   # round 0 belongs to base only, and ROUND resumes past the rounds already on disk.
   if [ ! -f "$RUN/round-0.checks" ]; then
@@ -949,6 +968,29 @@ precondition_lines() { # LOOP.md, Preconditions
   for t in judge reviewer; do
     grader_file "$t" > /dev/null 2>&1 && echo "  PASS $t.md in the plugin cache" || echo "  FAIL no $t.md in the plugin cache"
   done
+  if [ -n "${DISABLE_TELEMETRY+x}" ]; then
+    echo "  FAIL DISABLE_TELEMETRY is set; the advisor stays off"
+  elif [ -n "${CLAUDE_CODE_DISABLE_ADVISOR_TOOL+x}" ]; then
+    echo "  FAIL CLAUDE_CODE_DISABLE_ADVISOR_TOOL is set; --advisor has no effect"
+  else
+    echo "  PASS advisor env clean"
+  fi
+  if [ "${FACTORY_STATUS_PROBE:-}" = 1 ]; then
+    # One paid Opus call with no --settings: the frozen worker settings carry a Stop hook that blocks
+    # a one-turn probe. success means --advisor attached (docs/research/advisor-and-managed-agents.md).
+    local pe po rc
+    pe=$(mktemp "${TMPDIR:-/tmp}/factory-probe.XXXXXX")
+    po=$(claude -p --model "$WORKER_MODEL" --advisor "$WORKER_ADVISOR" --max-turns 1 --output-format json \
+      --strict-mcp-config --no-session-persistence 'Reply with the single word ok' 2> "$pe"); rc=$?
+    if [ "$rc" -eq 0 ] && [ "$(jq -r "$RESULT_OBJ | .subtype // \"\"" <<< "$po" 2> /dev/null)" = success ]; then
+      echo "  PASS advisor attaches"
+    else
+      echo "  FAIL advisor: $(head -1 "$pe")"
+    fi
+    rm -f "$pe"
+  else
+    echo "  INFO advisor probe not run; FACTORY_STATUS_PROBE=1 bin/factory status runs it (one paid Opus call)"
+  fi
   [ -f "$HOME/.config/loam-loops/pushover.env" ] && echo "  INFO pushover.env present" \
     || echo "  INFO no pushover.env; notifications comment on the ticket"
 }
diff --git a/bin/factory.d/_common.md b/bin/factory.d/_common.md
index 7dc85c1..893479a 100644
--- a/bin/factory.d/_common.md
+++ b/bin/factory.d/_common.md
@@ -1,6 +1,7 @@
 You are one round of an unattended loop on ticket #<issue>. There is no human. Decide, and record each decision in <decisions> in one line.
 Start by opening every path named under Where, Do not touch, and Approach with git ls-files; never guess a path or a name.
 Follow the Approach section where the ticket has one; if you depart from it, say why in <decisions>.
+If an advisor tool is available, it is a more capable model that reads your conversation so far and sends back guidance. Consult it before you commit to a decision that is expensive to reverse: a file layout, a public interface, a check you cannot make fail, a scope cut. Do routine implementation yourself. When you consult, act on the guidance and record in <decisions> what you changed.
 Implement the Goal. Touch nothing listed under Do not touch. Add nothing listed under Out of scope.
 Before you finish, run the done-checks block from the worktree root exactly as the supervisor will, and fix every FAIL line you can; repeat until it prints no FAIL line or you cannot proceed. The supervisor reruns it; a claim without a PASS line is worth nothing.
 Commit as you go with messages that name the step. Never push, never open a PR, never touch GitHub.
~~~~~~~~~~~~ evidence
