## Ticket

~~~~~~~~~~~~ evidence
Brief:
Add worker: codex and codex-review: yes to bin/factory run as LOOP.md specifies.
Where: bin/factory, bin/factory.d/ (exist after F1)
Done means: a Track B ticket with worker: codex reaches pr-opened; codex-review: yes adds one schema-shaped review section; Codex token counts appear in the ledger; the .env read result (not blocked, per D8) is recorded (merge checklist, #38); codex login status is a preflight line.
Out of scope: any grader prompt change; parallel runs; the timer.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #56, #41

## Goal and why
`worker: codex` and `codex-review: yes` as specified in `LOOP.md` (`ROADMAP.md` F4). `review-output.schema.json` is copied from the installed Codex plugin.

## Do not touch
The standing list. Except: bin/factory, bin/factory.d/, bin/factory.d/review-output.schema.json (this ticket creates it).

## Out of scope
- any change to a grader prompt or schema
- raising `MAX_PARALLEL`
- `bin/factory next` (F9)

## Approach
Facts from the D8 probe on the runner (Codex 0.153.4, 2026-09-07): `codex` is not on the non-interactive PATH, so every call exports `PATH=$HOME/.local/bin:$PATH`; `-o` is the last-message file and the JSONL stream is stdout, so the worker call is `codex exec --json -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.txt < /dev/null`; every call ends in `< /dev/null` or Codex swallows the caller's stdin; a `/<skill>` line fires only a skill Codex finds in an agent-skills directory at the worktree root, which this repo does not have (its skills live under `seed/.agents/skills/`), and an unknown one is swallowed silently, so the supervisor pastes the skill bodies instead; `turn.completed` carries `usage` with five token counters, which is the ledger line. `codex exec review` accepts and ignores `--output-schema`, so the review stage is plain `codex exec --json --output-schema bin/factory.d/review-output.schema.json -o round-<k>.review.json -s workspace-write "Review the diff base...HEAD for bugs" < /dev/null`, which returned validating JSON; `needs-attention` with a `critical` or `high` finding blocks once. The workspace-write sandbox does not block a `.env` read (the secret was echoed verbatim), so the PR body records that fact and the Codex worker's settings deny `.env` through Codex rules or the read stays a recorded risk; deciding which is not this ticket. Token counts land in the ledger with `cost_usd` null and the PR body says the dollar caps do not bound a Codex worker. Use the event names and flags the ticket "What codex exec does with a skill line, JSONL events, hooks, subagents, and a .env read" observed. No check runs the loop from inside the loop; the hand run in the merge checklist is the proof (#38).

Runs on jhaveris under `bin/factory run` (`LOOP.md` Commands), launched with `bin/runner 'bin/factory run <this issue>'` until the F9 timer exists; the merge is the one human action.

This is the first `size: large` ticket (F12): round 1 runs the fan-out workflow at `<run>/frozen/factory-round.js`, one Opus planner, two to four Opus builders on disjoint files, one integrator that reruns every check and writes `<run>/tasks/result.json`. If the planner returns solo or the file is absent, the worker implements the round itself as before. Its ledger line (workflow_agents, workflow_usd, wall clock, rounds, unmet and abandoned tasks) is the F12 keep-or-cut data point.

## Done checks
```done-checks
jq -e . bin/factory.d/review-output.schema.json >/dev/null 2>&1 && pass review-schema || fail review-schema "review-output.schema.json missing or invalid"
grep -Eq '^[^#]*codex exec --json -s workspace-write' bin/factory 2>/dev/null && grep -Eq '^[^#]*codex exec --json --output-schema' bin/factory && pass codex-calls-present || fail codex-calls-present "bin/factory lacks the worker call or the schema review call"
n=$(grep -Ec '^[^#]*codex exec' bin/factory 2>/dev/null); m=$(grep -Ec '^[^#]*codex exec.*< /dev/null' bin/factory 2>/dev/null); [ "${n:-0}" -gt 0 ] && [ "$n" = "$m" ] && pass codex-stdin-closed || fail codex-stdin-closed "$((${n:-0}-${m:-0})) codex exec call(s) do not close stdin, or none exist"
grep -Eq '^[^#]*codex login status' bin/factory 2>/dev/null && pass preflight-codex-login || fail preflight-codex-login "codex login status is not a preflight line"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }   # under the Stop hook bin/check (minutes per stop) is left to the supervisor, which runs it once on green
```

## Merge checklist
- from the F4 run's worktree on the runner (a sibling of `~/Desktop/loam`, `LOOP.md` Layout): `bin/runner 'cd ../<that worktree> && bin/factory run <a Track B ticket with worker: codex and codex-review: yes>'` reaches `pr-opened`; its PR body has the schema-shaped review section and the .env line; its ledger has a Codex line with token counts and cost_usd null; run directory linked in the PR body (#38)
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
size: large
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 60 turns

## Decisions
docs/factory/LOOP.md (Worker calls, Grader calls), docs/factory/ROADMAP.md; decision ticket: What codex exec does with a skill line, JSONL events, hooks, subagents, and a .env read (#41, resolved with the four corrections above)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS review-schema
PASS codex-calls-present
PASS codex-stdin-closed
PASS preflight-codex-login
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Orientation: opened bin/factory, bin/factory.d/ (lib.sh, checks framework), docs/factory/LOOP.md (Worker calls, Grader calls, Preconditions), frozen/factory-round.js, frozen/issue.md, frozen/checks.sh via git ls-files and Read.
Codex review schema source found at ~/.claude/plugins/cache/openai-codex/codex/1.0.4/schemas/review-output.schema.json (identical to the marketplace copy); it is copied to bin/factory.d/review-output.schema.json.
Codex 0.153.4 confirmed at ~/.local/bin/codex, not on the bare PATH, matching the D8 probe.
Spec note: LOOP.md Worker calls writes `-o round-<k>.last.md`; the ticket Approach writes `.last.txt`. Cosmetic (last-message file name only). Following the ticket Approach (.last.txt) since it is this run's authoritative instruction; recording the divergence here.
Spec note: LOOP.md Grader calls references `frozen/review-output.schema.json`; the ticket Approach writes `--output-schema bin/factory.d/review-output.schema.json`. The done-check greps only for the literal `codex exec --json --output-schema`, so path choice is free; deciding below.
PLAN solo: nearly all work is in the single bin/factory script (worker call, schema-review call, stdin closing, preflight login, ledger); the only other file is a trivial schema copy under 10 min, so no 2+ disjoint tasks each carry real work.
Workflow round 1 returned solo (1 agent, planner only; no result.json). Implementing the ticket myself in this round, as the round-1 instruction directs on an absent result.json.
Decided: review schema path. The review call passes the FROZEN copy "$RUN/frozen/review-output.schema.json" (absolute), and review-output.schema.json is added to FROZEN_SET and copied in freeze. This departs from the Approach's literal bin/factory.d/review-output.schema.json because the review runs with cwd=worktree, where the worker could edit that file mid-run; LOOP.md line 108 already names the frozen copy (#38).
Decided: review prompt is inline with the base sha in it (matching the Approach's inline command), not a new frozen codex-review.prompt.md file; adding another frozen file was avoided as unneeded.
Decided: the Codex review's stdout (JSONL) is captured to round-<k>.codex-review.jsonl and recorded as a ledger line (role codex-review, cost_usd null) via codex_result+record. Small deviation from the Approach's command, which omitted the stdout redirect; done for clean logs and consistent token accounting.
Decided: ledger. record() gained an eighth arg `codex`; a Codex line carries cost_usd null and the verbatim last turn.completed.usage object under `usage` (the five counters are not hardcoded). ticket_spent, daily_spent, and cmd_status all read cost_usd // 0, so null is safe (verified).
Decided: the Codex review blocks once via a separate CODEX_REVIEW_BLOCKED flag (not REVIEW_BLOCKED), on any critical or high finding. A missing or unparseable Codex review is non-blocking; the Claude judge and reviewer stay the primary gate.
Decided: no dollar cap bounds a Codex worker (cost null); CALL_TIMEOUT_SEC, MAX_HOURS, and MAX_ROUNDS bound it. The PR body records this and the .env-read fact under "## Codex worker notes", gated on worker: codex; the "## Codex review" section is gated on codex-review: yes.
Decided: preflight `codex login status` added to precondition_lines under PATH=$CODEX_PATH:$PATH; INFO (not FAIL) when logged out or absent, since only a worker: codex ticket needs it.
Decided: a Codex worker gets each named skill's body pasted from ~/.claude/skills/<name>/SKILL.md instead of the Skill-tool sentence (Codex has no Skill tool and swallows an unknown /<skill> line, #41). This ticket names no skills, so the branch is dormant here.
Done-checks block run from the worktree root exactly as the supervisor will: all five PASS (review-schema, codex-calls-present, codex-stdin-closed, preflight-codex-login, check-green), exit 0, no FAIL line. bin/check green (31 tests, plugin validate, fixture lint, verdict gate).
Note: record() now writes a usage field on every ledger line (usage: null for a Claude call, the verbatim Codex usage object for a Codex call). Additive; no consumer reads a fixed ledger schema, so Claude accounting is unchanged.

~~~~~~~~~~~~ evidence

## Diff (a8509f38...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                             | 136 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++------------
 bin/factory.d/review-output.schema.json |  87 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 211 insertions(+), 12 deletions(-)

diff --git a/bin/factory b/bin/factory
index 71b92dd..cd9e586 100755
--- a/bin/factory
+++ b/bin/factory
@@ -341,6 +341,7 @@ MAX_ROUNDS=6; ROUND_BUDGET_USD=15; GRADER_BUDGET_USD=5; TICKET_BUDGET_USD=60
 DAILY_BUDGET_USD=150; MAX_HOURS=8; MAX_TURNS=200; CALL_TIMEOUT_SEC=5400; MAX_PARALLEL=1
 WORKER_MODEL="${FACTORY_WORKER_MODEL:-claude-opus-4-8[1m]}"   # ARCHITECTURE.md, Models and roles (2026-09-09)
 GRADER_MODEL="${FACTORY_GRADER_MODEL:-fable}"
+CODEX_MODEL="${FACTORY_CODEX_MODEL:-codex}"   # ledger label for a `worker: codex` round; Codex holds the real model in its own config, and its dollar cost is null (F4)
 WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-fable}"   # mid-round advisor on the worker call; FACTORY_WORKER_ADVISOR= (explicit empty) disables the flag. No colon: :- could never disable. The bare name is never read.
 WORKER_EFFORT=xhigh        # the ticket's `effort:` line overrides
 GRADER_EFFORT=medium
@@ -349,6 +350,10 @@ FENCE='~~~~~~~~~~~~ evidence'   # fixed marker; never a per-run string (#38)

 REPO=""; ISSUE=""; KEY=""; IS_FILE=0; RUN=""; ROUND=0; REVIEW_BLOCKED=0
 LOG=/dev/null; LEDGER=""; DAILY=""; DECISIONS=""; WORKTREE=""; BRANCH=""
+# Worker kind and the Codex review stage, read from the ticket in cmd_run (F4). CODEX_REVIEW_BLOCKED is
+# separate from REVIEW_BLOCKED so a Claude-reviewer block never consumes the Codex review's one block.
+WORKER_KIND=claude; CODEX_REVIEW=no; CODEX_REVIEW_BLOCKED=0
+CODEX_PATH="$HOME/.local/bin"   # Codex is not on the non-interactive PATH (#41); every Codex call prepends this

 now()   { date -u +%Y-%m-%dT%H:%M:%SZ; }
 today() { date -u +%Y-%m-%d; }
@@ -463,7 +468,7 @@ prepare_worktree() {

 FROZEN_SET="factory lib.sh _common.md role-settings.json worker-settings.json checks.sh \
 judge.md reviewer.md judge.schema.json reviewer.schema.json issue.md protected.txt exempt.txt \
-factory-round.js"
+factory-round.js review-output.schema.json"

 freeze() {
   local g src
@@ -471,6 +476,7 @@ freeze() {
   printf '%s\n' "$BODY" > "$RUN/frozen/issue.md"
   cp "$ROOT/bin/factory" "$RUN/frozen/factory"
   cp "$ROOT/bin/factory.d/factory-round.js" "$RUN/frozen/factory-round.js"  # the worker runs its frozen copy, so it cannot edit the script (F12)
+  cp "$ROOT/bin/factory.d/review-output.schema.json" "$RUN/frozen/review-output.schema.json"  # the Codex review reads the frozen copy, so a mid-run edit of it cannot change the review (#38, F4)
   cp "$ROOT/bin/factory.d/lib.sh" "$RUN/frozen/lib.sh"
   cp "$ROOT/bin/factory.d/role-settings.json" "$RUN/frozen/role-settings.json"
   cp "$ROOT/bin/factory.d/worker-settings.json" "$RUN/frozen/worker-settings.json"
@@ -509,20 +515,22 @@ exec_frozen() {
 ticket_spent() { jq -s '[.[].cost_usd // 0] | add // 0' "$LEDGER"; }
 daily_spent()  { jq -s --arg d "$(today)" '[.[] | select(.date == $d) | .cost_usd // 0] | add // 0' "$DAILY"; }

-record() { # round role model result.json [advisor_calls] [advisor_usd] [ran_workflow]
+record() { # round role model result.json [advisor_calls] [advisor_usd] [ran_workflow] [codex]
   # workflow_agents is the subagents this round spawned; workflow_usd is the round's cost when it ran
-  # the fan-out workflow, else 0 (F12). ranwf is 1 only on a large ticket's round 1.
-  local line acalls="${5:-0}" ausd="${6:-0}" ranwf="${7:-0}"
+  # the fan-out workflow, else 0 (F12). ranwf is 1 only on a large ticket's round 1. codex is 1 for a
+  # Codex call: cost_usd is null (the dollar caps do not bound Codex, #41) and `usage` carries its
+  # verbatim token counters; ticket_spent, daily_spent, and cmd_status all read cost_usd // 0, so null is safe.
+  local line acalls="${5:-0}" ausd="${6:-0}" ranwf="${7:-0}" codex="${8:-0}"
   line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-    --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" \
-    "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(.total_cost_usd // 0), \
+    --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" --argjson codex "$codex" \
+    "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(if \$codex == 1 then null else (.total_cost_usd // 0) end), \
 duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:((.permission_denials // []) | length), \
-subtype:(.subtype // \"unknown\"), advisor_calls:\$acalls, advisor_usd:\$ausd, \
+subtype:(.subtype // \"unknown\"), usage:(.usage // null), advisor_calls:\$acalls, advisor_usd:\$ausd, \
 workflow_agents:(.subagent_stats.spawned // 0), workflow_usd:(if \$ranwf == 1 then (.total_cost_usd // 0) else 0 end), \
 ts:\$ts}" "$4" 2> /dev/null) \
     || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-      --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" \
-      '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:0, workflow_usd:0, ts:$ts}')
+      --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" --argjson codex "$codex" \
+      '{round:$round, role:$role, model:$model, cost_usd:(if $codex == 1 then null else 0 end), duration_ms:0, num_turns:0, denials:0, subtype:"unknown", usage:null, advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:0, workflow_usd:0, ts:$ts}')
   printf '%s\n' "$line" >> "$LEDGER"
   printf '%s' "$line" | jq -c --arg date "$(today)" --arg ticket "$KEY" \
     '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$DAILY"
@@ -607,9 +615,20 @@ round_zero() {
 build_worker_prompt() { # round -> prompt path (pending until the call returns a result)
   local round="$1" pf="$RUN/pending.prompt.md" prev=$((round - 1)) s
   { printf '%s\n\n' "$BODY"; cat "$RUN/frozen/_common.md"; } > "$pf"
-  # One Skill-tool sentence per `skills:` name; never a slash command, which would swallow the body (#37, #40).
-  section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
-    | while read -r s; do printf 'Before the first edit, call the Skill tool with "%s".\n' "$s"; done >> "$pf"
+  # Skills per role (LOOP.md): a Claude worker gets one Skill-tool sentence per `skills:` name (never a
+  # slash command, which would swallow the body, #37/#40); a Codex worker has no Skill tool and swallows
+  # an unknown `/<skill>` line (#41), so it gets each named skill's body pasted from ~/.claude/skills/.
+  if [ "$WORKER_KIND" = codex ]; then
+    section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
+      | while read -r s; do
+          sf="$HOME/.claude/skills/$s/SKILL.md"
+          if [ -f "$sf" ]; then printf '\n## Skill: %s\n\n%s\n' "$s" "$(cat "$sf")"
+          else printf '\nUse the "%s" skill (its body was not found under ~/.claude/skills/%s/SKILL.md).\n' "$s" "$s"; fi
+        done >> "$pf"
+  else
+    section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
+      | while read -r s; do printf 'Before the first edit, call the Skill tool with "%s".\n' "$s"; done >> "$pf"
+  fi
   # A large ticket runs round 1 as the fan-out workflow; the F11 advisor is the Fable check on the split (F12).
   if [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; then
     {
@@ -630,6 +649,26 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
   printf '%s\n' "$pf"
 }

+# Codex --json stream (round-<k>.jsonl) plus the exit code -> a result-shaped JSON on stdout that
+# record and assert_call_ok read unchanged. The last `turn.completed` carries `usage`, passed through
+# verbatim so the five token counters are not hardcoded (#41). No `turn.completed`, or a non-zero exit,
+# is the environment, not a round (LOOP.md, Exits): subtype no-result / is_error true stops it.
+codex_result() { # jsonl exit_code -> result JSON on stdout
+  jq -s --argjson rc "${2:-0}" '
+    [.[] | select(.type == "turn.completed")] as $turns
+    | [.[] | select(.type == "turn.failed" or .type == "error")] as $errs
+    | {
+        subtype: (if ($turns | length) > 0 then "success" else "no-result" end),
+        is_error: ($rc != 0 or ($errs | length) > 0),
+        num_turns: ($turns | length),
+        duration_ms: ($turns[-1].duration_ms // 0),
+        total_cost_usd: null,
+        usage: ($turns[-1].usage // null),
+        result: ((($errs[-1].message // $errs[-1].error) // (if $rc != 0 then "codex worker call exited " + ($rc | tostring) else "" end)) // "")
+      }' "$1" 2> /dev/null \
+    || printf '{"subtype":"no-result","is_error":true,"num_turns":0,"duration_ms":0,"total_cost_usd":null,"usage":null,"result":"codex result parse failed"}\n'
+}
+
 worker_round() { # round; leaves round-N.* only once the call produced a result
   local round="$1" pf out="$RUN/pending.jsonl" res="$RUN/pending.result.json" t=() login_retried=0 le
   command -v timeout > /dev/null 2>&1 && t=(timeout --foreground "$CALL_TIMEOUT_SEC")
@@ -637,6 +676,23 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   # not a local, so it survives the loop's later rounds.
   [ -n "${FIRST_WORKER_ROUND+x}" ] || FIRST_WORKER_ROUND="$round"
   pf=$(build_worker_prompt "$round")
+  if [ "$WORKER_KIND" = codex ]; then
+    # The Codex worker: JSONL stream is stdout, -o is the last message, < /dev/null keeps Codex off the
+    # caller's stdin (#41). No dollar budget bounds it (cost_usd null); CALL_TIMEOUT_SEC and MAX_HOURS do.
+    local rc ranwf=0
+    { [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; } && ranwf=1
+    log "codex worker call: round $round model=$CODEX_MODEL (dollar caps do not bound it), prompt=$(wc -c < "$pf") bytes"
+    rm -f "$out"
+    ( cd "$WORKTREE" && PATH="$CODEX_PATH:$PATH" ${t[@]+"${t[@]}"} codex exec --json -s workspace-write "$(cat "$pf")" > "$out" -o "$RUN/round-$round.last.txt" < /dev/null ); rc=$?
+    [ "$rc" -eq 0 ] || log "codex worker call exited $rc (the result decides)"
+    codex_result "$out" "$rc" > "$res"
+    record "$round" worker "$CODEX_MODEL" "$res" 0 0 "$ranwf" 1
+    assert_call_ok worker "$res"
+    mv "$pf" "$RUN/round-$round.prompt.md"
+    mv "$out" "$RUN/round-$round.jsonl"
+    mv "$res" "$RUN/round-$round.result.json"
+    return 0
+  fi
   while :; do
     log "worker call: round $round model=$WORKER_MODEL effort=$WORKER_EFFORT advisor=${WORKER_ADVISOR:-off} budget=$ROUND_BUDGET_USD usd, prompt=$(wc -c < "$pf") bytes"
     rm -f "$out"
@@ -808,10 +864,37 @@ run_review() { # round -> 0 when nothing blocks
   return 1
 }

+run_codex_review() { # round -> 0 when nothing blocks; needs-attention with a critical or high finding blocks once (LOOP.md)
+  local round="$1" f="$RUN/round-$1.codex-review.json" jsonl="$RUN/round-$1.codex-review.jsonl" res="$RUN/round-$1.codex-review.result.json" base blocking rc
+  base=$(cat "$RUN/base.sha")
+  assert_caps
+  stop_requested && finish stopped "FACTORY_STOP before the Codex review call"
+  log "codex review call: round $round schema=frozen/review-output.schema.json"
+  # `codex exec review` ignores --output-schema, so the review is plain `codex exec` with the schema (#41):
+  # the -o file holds the schema-validated JSON, the JSONL stream (stdout) carries usage for the ledger.
+  ( cd "$WORKTREE" && PATH="$CODEX_PATH:$PATH" ${TIMEOUT_G[@]+"${TIMEOUT_G[@]}"} codex exec --json --output-schema "$RUN/frozen/review-output.schema.json" -o "$f" -s workspace-write "Review the git diff ${base}...HEAD for bugs. Reply with one JSON object matching the review-output schema: verdict, summary, findings, next_steps." > "$jsonl" < /dev/null ); rc=$?
+  [ "$rc" -eq 0 ] || log "codex review call exited $rc"
+  codex_result "$jsonl" "$rc" > "$res"
+  record "$round" codex-review "$CODEX_MODEL" "$res" 0 0 0 1
+  blocking=$(jq '[.findings[]? | select(.severity == "critical" or .severity == "high")] | length' "$f" 2> /dev/null) || blocking=0
+  [ -n "$blocking" ] || blocking=0
+  log "codex review verdict: $(jq -r '.verdict // "unparseable"' "$f" 2> /dev/null) findings=$(jq '(.findings // []) | length' "$f" 2> /dev/null) blocking=$blocking"
+  [ "$blocking" -gt 0 ] || return 0
+  if [ "$CODEX_REVIEW_BLOCKED" = 1 ]; then
+    log "the Codex review already blocked once on this ticket; its findings go to the backlog"
+    return 0
+  fi
+  CODEX_REVIEW_BLOCKED=1
+  jq -r '[.findings[]? | select(.severity == "critical" or .severity == "high")] | .[]
+    | "- " + (.file // "?") + ":" + ((.line_start // 0) | tostring) + " [" + .severity + "] " + .title + ": " + .body + " Fix: " + (.recommendation // "-")' "$f" >> "$RUN/round-$round.fixes"
+  return 1
+}
+
 graders() { # round -> 0 when the judge passes and nothing blocks
   local ok=0
   run_judge "$1" || ok=1
   run_review "$1" || ok=1
+  [ "$CODEX_REVIEW" = yes ] && { run_codex_review "$1" || ok=1; }
   return "$ok"
 }

@@ -831,6 +914,20 @@ open_pr() {
     printf '## Reviewer\n\n'
     jq -r '.findings[]? | "- [" + .severity + "] " + (.file // "?") + ":" + ((.line // 0) | tostring) + " " + .defect + " Fix: " + .fix' "$RUN/round-$ROUND.review.json"
     jq -r '.unverified[]? | "- unverified: " + .' "$RUN/round-$ROUND.review.json"
+    if [ "$CODEX_REVIEW" = yes ]; then
+      printf '\n## Codex review\n\n'
+      if [ -s "$RUN/round-$ROUND.codex-review.json" ] && jq -e . "$RUN/round-$ROUND.codex-review.json" > /dev/null 2>&1; then
+        printf 'verdict: %s\n\n%s\n\n' "$(jq -r '.verdict // "?"' "$RUN/round-$ROUND.codex-review.json")" "$(jq -r '.summary // ""' "$RUN/round-$ROUND.codex-review.json")"
+        jq -r '.findings[]? | "- [" + .severity + "] " + (.file // "?") + ":" + ((.line_start // 0) | tostring) + " " + .title + ": " + .body + " Fix: " + (.recommendation // "-")' "$RUN/round-$ROUND.codex-review.json"
+      else
+        printf '(no Codex review output for round %s)\n' "$ROUND"
+      fi
+    fi
+    if [ "$WORKER_KIND" = codex ]; then
+      printf '\n## Codex worker notes\n\n'
+      printf -- '- Cost: the Codex worker rounds carry `cost_usd: null` in the ledger; the dollar caps (ROUND_BUDGET_USD, TICKET_BUDGET_USD, DAILY_BUDGET_USD) do not bound a Codex worker. Only token counts are recorded.\n'
+      printf -- '- `.env`: the workspace-write sandbox does not block a `.env` read (D8, #41); a secret in `.env` is readable by the worker. F4 denies it in Codex config, or it stays a recorded risk.\n'
+    fi
     printf '\n## Backlog\n\n'; jq -r '.backlog[]? | "- " + .' "$RUN/round-$ROUND.judge.json"
     printf '\n## Metrics\n\nrounds: %s, spend: %s usd, wall: %s min, denials: %s\nrun directory: %s\n' \
       "$ROUND" "$(ticket_spent)" "$(( ( $(date -u +%s) - $(cat "$RUN/started") ) / 60 ))" \
@@ -907,6 +1004,10 @@ cmd_run() {
   [ -n "$WORKER_EFFORT" ] || WORKER_EFFORT=xhigh
   WORKER_SIZE=$(section Worker | sed -n 's/^size: *//p' | head -1)   # small|large; large routes round 1 to the workflow (F12)
   [ -n "$WORKER_SIZE" ] || WORKER_SIZE=small
+  WORKER_KIND=$(section Worker | sed -n 's/^worker: *//p' | head -1)   # claude|codex; codex routes the worker call to Codex (F4)
+  [ -n "$WORKER_KIND" ] || WORKER_KIND=claude
+  CODEX_REVIEW=$(section Worker | sed -n 's/^codex-review: *//p' | head -1)   # yes adds a Codex review stage after the graders (F4)
+  [ -n "$CODEX_REVIEW" ] || CODEX_REVIEW=no
   RUN="$RUNS_ROOT/$KEY/$(printf '%s' "$BODY" | sha256_of | cut -c1-8)"
   mkdir -p "$RUN/frozen" "$RUN/worker" "$RUN/tasks" || { echo "factory run: cannot create $RUN" >&2; exit 4; }
   LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; DAILY="$RUNS_ROOT/ledger-daily.jsonl"
@@ -1003,6 +1104,17 @@ precondition_lines() { # LOOP.md, Preconditions
   for t in judge reviewer; do
     grader_file "$t" > /dev/null 2>&1 && echo "  PASS $t.md in the plugin cache" || echo "  FAIL no $t.md in the plugin cache"
   done
+  # Codex login: Codex is not on the bare PATH (#41), so probe it under CODEX_PATH. Only a worker: codex
+  # ticket needs it, so a logged-out or absent Codex is INFO here, not FAIL.
+  if PATH="$CODEX_PATH:$PATH" command -v codex > /dev/null 2>&1; then
+    if PATH="$CODEX_PATH:$PATH" codex login status > /dev/null 2>&1; then
+      echo "  PASS codex login status"
+    else
+      echo "  INFO codex login status reports logged out; a worker: codex ticket needs a login"
+    fi
+  else
+    echo "  INFO codex not on PATH; only a worker: codex ticket needs it"
+  fi
   # With the advisor off (FACTORY_WORKER_ADVISOR= empty) the env check and probe are moot: neither
   # would run --advisor, so report the choice and skip both rather than FAIL a deliberate off (#68).
   if [ -n "$WORKER_ADVISOR" ]; then
diff --git a/bin/factory.d/review-output.schema.json b/bin/factory.d/review-output.schema.json
new file mode 100644
index 0000000..875eac4
--- /dev/null
+++ b/bin/factory.d/review-output.schema.json
@@ -0,0 +1,87 @@
+{
+  "$schema": "https://json-schema.org/draft/2020-12/schema",
+  "type": "object",
+  "additionalProperties": false,
+  "required": [
+    "verdict",
+    "summary",
+    "findings",
+    "next_steps"
+  ],
+  "properties": {
+    "verdict": {
+      "type": "string",
+      "enum": [
+        "approve",
+        "needs-attention"
+      ]
+    },
+    "summary": {
+      "type": "string",
+      "minLength": 1
+    },
+    "findings": {
+      "type": "array",
+      "items": {
+        "type": "object",
+        "additionalProperties": false,
+        "required": [
+          "severity",
+          "title",
+          "body",
+          "file",
+          "line_start",
+          "line_end",
+          "confidence",
+          "recommendation"
+        ],
+        "properties": {
+          "severity": {
+            "type": "string",
+            "enum": [
+              "critical",
+              "high",
+              "medium",
+              "low"
+            ]
+          },
+          "title": {
+            "type": "string",
+            "minLength": 1
+          },
+          "body": {
+            "type": "string",
+            "minLength": 1
+          },
+          "file": {
+            "type": "string",
+            "minLength": 1
+          },
+          "line_start": {
+            "type": "integer",
+            "minimum": 1
+          },
+          "line_end": {
+            "type": "integer",
+            "minimum": 1
+          },
+          "confidence": {
+            "type": "number",
+            "minimum": 0,
+            "maximum": 1
+          },
+          "recommendation": {
+            "type": "string"
+          }
+        }
+      }
+    },
+    "next_steps": {
+      "type": "array",
+      "items": {
+        "type": "string",
+        "minLength": 1
+      }
+    }
+  }
+}
~~~~~~~~~~~~ evidence
