## Ticket

~~~~~~~~~~~~ evidence
Brief:
Close what the F4 run and its three reviews found: the Codex review runs read-only, a Codex worker never gets the Claude-only fan-out, skill bodies resolve for plugin-namespaced names, the review prompt is frozen, the docs name the files the code writes, and the two fan-out ledger fields report what actually ran.
Where: bin/factory (build_worker_prompt, worker_round, codex_result, the Codex review call, freeze, record, precondition_lines), bin/factory.d/codex-review.prompt.md (new), docs/factory/LOOP.md, docs/factory/ROADMAP.md
Done means: the Codex review call carries a read-only sandbox, a large-ticket prompt is built only for a claude worker, plugin:name skills resolve to their SKILL.md, the review prompt is a frozen file, LOOP.md and ROADMAP.md match the code, workflow_agents counts the Workflow calls in the stream, and workflow_usd is zero when no result.json was written.
Out of scope: the Codex hand run itself (F4 merge checklist); a Codex .env deny; worktree isolation for builders.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #70 (merged as PR #71)

## Goal and why
F4 (PR #71) shipped the Codex worker and review stage; its judge passed, and its reviewer and the by-hand lean-critic left six defects that only bite once a `worker: codex` ticket runs.
The same run was the first `size: large` ticket: the planner correctly returned solo, and the ledger then wrote `workflow_agents: 0` and `workflow_usd` equal to the whole round, so the F12 keep-or-cut line cannot be read from it.
One ticket closes both lists before the Codex hand run and the first real fan-out.

## Do not touch
The standing list. Except: bin/factory (build_worker_prompt, worker_round, codex_result, the Codex review call, freeze, record, precondition_lines), bin/factory.d/codex-review.prompt.md, docs/factory/LOOP.md (Worker calls, Grader calls, the .env sentence), docs/factory/ROADMAP.md (the F4 entry only).
Also: bin/factory.d/factory-round.js; the judge and reviewer files and their schemas; seed/.

## Out of scope
- running a `worker: codex` ticket; that is the F4 merge checklist and its own session
- a `.env` deny in Codex config; it stays a recorded risk until the hand run shows which mechanism works
- worktree isolation for fan-out builders
- any change to what the planner or builders do

## Approach
Executor: `bin/factory run` as merged in F1.

Facts pinned from the F4 run (`runs/70/29737833`, 2026-09-10): the worker called the Workflow tool with `scriptPath <run>/frozen/factory-round.js`; the planner returned solo and no `tasks/result.json` was written; the result event's `subagent_stats.spawned` was 0, so it does not count workflow agents; `modelUsage` had only the worker and advisor models. The reviewer and lean-critic findings are in `.superpowers/factory/sessions/manager-2026-09-11-f11.md`.

Change:
1. Codex review sandbox: the review call uses `-s read-only` instead of `-s workspace-write`. A review needs no write access, and under workspace-write it could edit the tree the judge and reviewer already graded.
2. Fan-out is Claude-only: the large-ticket block in `build_worker_prompt` runs only when the worker is claude; a `size: large` Codex ticket gets the ordinary round-1 prompt and its ledger line carries `workflow_agents: 0`, `workflow_usd: 0`. Add `runs_workflow()` (`[ "$WORKER_KIND" = claude ] && [ "$WORKER_SIZE" = large ] && [ "$1" -eq 1 ]`) and use it at every site that tests those three values.
3. Skill bodies for a Codex worker: add `skill_file()` that resolves a bare name to `~/.claude/skills/<name>/SKILL.md` and a `plugin:name` to `$HOME/.claude/plugins/cache/*/<plugin>/*/skills/<name>/SKILL.md`, the way `grader_file` resolves agents, newest version first. Lint has already guaranteed the name is in `skills.txt`, so a name that resolves to no file is `finish ticket-defect`, never a "use the X skill" sentence Codex cannot honor.
4. Frozen review prompt: `bin/factory.d/codex-review.prompt.md` holds the one-line review prompt with a `<base>` placeholder; `FROZEN_SET` and `freeze` gain it; the review call passes `"$(sed "s/<base>/$base/" "$RUN/frozen/codex-review.prompt.md")"`. Drop the sentence listing the four schema fields; `--output-schema` enforces them.
5. Ledger fields. `workflow_agents` is the count of `tool_use` blocks named `Workflow` in the round's stream plus, when `<run>/tasks/result.json` exists, the number of tasks it lists (the planner plus the builders and integrator are not visible in `subagent_stats`); `workflow_usd` is the round's `total_cost_usd` only when `result.json` exists, else 0. Both live in one function, `workflow_ledger()`, called from `worker_round` before `record`; both stay 0 on rounds after 1 and on Codex rounds. Codex `duration_ms` comes from `$SECONDS` around the call, not from a field no sample shows.
6. Docs. `LOOP.md` Worker calls: `round-<k>.last.txt`; Grader calls: the review call as it now reads, read-only, with the frozen prompt file; the `.env` sentence becomes "Its workspace-write sandbox does not block `.env` reads (#41); no deny is configured, and the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk." `ROADMAP.md` F4 entry: the same sentence in place of the `"**/*.env" = "deny"` done check, which never shipped.

## Done checks
```done-checks
grep -q -- 'codex exec --json --output-schema.*-s read-only' bin/factory && pass review-readonly || fail review-readonly "the Codex review call is not read-only"
grep -q '^runs_workflow()' bin/factory && pass claude-only-fanout || fail claude-only-fanout "no runs_workflow() guard"
grep -q '^skill_file()' bin/factory && grep -q 'plugins/cache/\*/' bin/factory && pass skill-resolve || fail skill-resolve "no skill_file() resolving plugin:name"
test -f bin/factory.d/codex-review.prompt.md && grep -q 'codex-review.prompt.md' bin/factory && pass frozen-review-prompt || fail frozen-review-prompt "review prompt is not a frozen file"
grep -q 'name == "Workflow"' bin/factory && pass workflow-agents || fail workflow-agents "workflow_agents does not count Workflow calls"
grep -q '^workflow_ledger()' bin/factory && pass workflow-usd || fail workflow-usd "no workflow_ledger() computing workflow_agents and workflow_usd from the stream and result.json"
grep -q 'round-<k>.last.txt' docs/factory/LOOP.md && pass loop-md || fail loop-md "LOOP.md still names last.md"
grep -q 'no deny is configured' docs/factory/LOOP.md && grep -q 'no deny is configured' docs/factory/ROADMAP.md && pass env-recorded || fail env-recorded "the .env risk is not recorded in both docs"
out=$(grep -c '"\*\*/\*.env" = "deny"' docs/factory/ROADMAP.md); [ "$out" -eq 0 ] && pass roadmap-deny-gone || fail roadmap-deny-gone "ROADMAP still promises a deny F4 never shipped"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- after merge, the F4 merge checklist's hand run: a Track B ticket with `worker: codex` and `codex-review: yes` reaches `pr-opened`, its commits exist on the branch (the worktree gitdir question), and its ledger has a Codex line with token counts
- the next `size: large` ticket whose work spans two or more files is the first real fan-out; read its `workflow_agents` and `workflow_usd` against this ticket's definitions

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 60 turns

## Decisions
the F4 ledger line and reviews in .superpowers/factory/sessions/manager-2026-09-11-f11.md; docs/factory/LOOP.md (Worker calls, Grader calls); the `.env` decision: recorded risk, no deny, until the Codex hand run (Samyak to confirm at publish)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS review-readonly
PASS claude-only-fanout
PASS skill-resolve
PASS frozen-review-prompt
PASS workflow-agents
PASS workflow-usd
PASS loop-md
PASS env-recorded
PASS roadmap-deny-gone
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
D1 read all Where/Do-not-touch/Approach paths with git ls-files before editing; confirmed bin/factory functions, LOOP.md, ROADMAP.md F4, review-output.schema.json, skills.txt, role-settings.json, factory-round.js result.json shape.
D2 skill layout departs from the Approach's literal skills/<name>/SKILL.md glob: sam-cc-setup skills are flat but mattpocock-skills nest one level (skills/engineering/research/SKILL.md), which is 4 of 6 skills.txt entries; skill_file therefore uses find -path "*/<name>/SKILL.md" under plugins/cache/*/<plugin>/*/skills, sort -rV, so all 6 skills.txt lines resolve (verified); the literal glob would have failed 4 and defeated the goal.
D3 result.json has keys solo/unmet/abandoned/checks and no tasks array, so "the number of tasks it lists" has no literal source; workflow_ledger counts builder artifact files <run>/tasks/[0-9]*.md when result.json exists, a documented lower bound (a builder that wrote no artifact is counted unmet by factory-round.js, not here).
D4 finish from command substitution: build_worker_prompt runs inside pf=$(build_worker_prompt ...), where finish/exit would only kill the subshell; on an unresolved Codex skill it returns 3 and worker_round (main shell) turns that into finish ticket-defect. Confirmed by advisor as a real bug the naive Approach reading would have.
D5 runs_workflow() gates the three values (worker kind, size, round); used in build_worker_prompt (so fan-out is claude-only) and inside workflow_ledger; the codex and claude ranwf lines are gone, replaced by workflow_ledger before record. Used ${WORKER_SIZE:-small} in the body (not bare $WORKER_SIZE) so a sourced test cannot hit set -u.
D6 record signature grew: args 7/8 are workflow_agents/workflow_usd from workflow_ledger, codex flag moved to arg 9; all four call sites updated (both worker paths, call_json graders keep 4 args, run_codex_review gets 0 0 0 1->0 0 0 0 1). workflow_agents no longer reads subagent_stats.spawned. Verified record output shape for claude worker, codex worker (cost_usd null), and grader.
D7 codex_result takes duration_ms as arg 3 from $SECONDS around the call (the F4 sample shows no per-turn duration field); applied at the codex worker call and the codex review call.
D8 Codex review call is now -s read-only and reads the frozen bin/factory.d/codex-review.prompt.md with <base> filled by sed; the schema-fields sentence is dropped (--output-schema enforces them); codex-review.prompt.md added to FROZEN_SET and copied in freeze.
D9 precondition_lines (listed in Where/Except but named by no Approach step): added one preflight line per skills.txt entry through skill_file, the only change that fits, so an install gap is caught before a Codex hand run rather than at build_worker_prompt. No done-check gates it.
D10 docs: LOOP.md Worker calls now says round-<k>.last.txt; LOOP.md Grader calls and ROADMAP.md F4 now say the review is read-only and "no deny is configured"; the ROADMAP "**/*.env" = "deny" promise is removed.
D11 NOT fixed, out of Except scope: open_pr (bin/factory:~929) still prints "F4 denies it in Codex config, or it stays a recorded risk" in the Codex-worker PR note; open_pr is not in the ticket's Except list, so it is left as a known stale line for a later ticket.
D12 all 11 done-checks pass from the worktree root via the frozen checks.sh (exit 0); ledger, workflow_ledger, and codex_result behavior verified with unit tests against the real F4 stream (workflow_agents=1, workflow_usd=0 there).

~~~~~~~~~~~~ evidence

## Diff (6013370f...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                          | 143 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++----------------------------------------
 bin/factory.d/codex-review.prompt.md |   1 +
 docs/factory/LOOP.md                 |   6 +++---
 docs/factory/ROADMAP.md              |   2 +-
 4 files changed, 108 insertions(+), 44 deletions(-)

diff --git a/bin/factory b/bin/factory
index cd9e586..ccfcece 100755
--- a/bin/factory
+++ b/bin/factory
@@ -207,6 +207,25 @@ grader_file() {
   return 1
 }

+# A worker's skill name (a line of bin/factory.d/skills.txt, lint-checked) -> its SKILL.md body path.
+# A bare name lives under ~/.claude/skills/<name>/; a plugin:name lives in the installed plugin cache,
+# the way grader_file resolves agents, newest version first. Plugin skills nest under a category dir
+# (mattpocock-skills:research is skills/engineering/research/SKILL.md), so match SKILL.md at any depth
+# under the plugin's skills tree, not only skills/<name>/.
+skill_file() { # skill-name -> SKILL.md path on stdout, non-zero when it resolves to no file
+  local name="$1" plugin sub f
+  case "$name" in
+    *:*)
+      plugin=${name%%:*}; sub=${name#*:}
+      f=$(find "$HOME"/.claude/plugins/cache/*/"$plugin"/*/skills -path "*/$sub/SKILL.md" 2> /dev/null | sort -rV | head -1)
+      [ -n "$f" ] && { printf '%s\n' "$f"; return 0; } ;;
+    *)
+      f="$HOME/.claude/skills/$name/SKILL.md"
+      [ -f "$f" ] && { printf '%s\n' "$f"; return 0; } ;;
+  esac
+  return 1
+}
+
 # A plugin agent file opens with frontmatter; strip it. One that asks for prose is also asked for the
 # JSON form; judge.md and reviewer.md carry their own `## Output` section and keep it byte-identical.
 grader_rubric() {
@@ -468,7 +487,7 @@ prepare_worktree() {

 FROZEN_SET="factory lib.sh _common.md role-settings.json worker-settings.json checks.sh \
 judge.md reviewer.md judge.schema.json reviewer.schema.json issue.md protected.txt exempt.txt \
-factory-round.js review-output.schema.json"
+factory-round.js review-output.schema.json codex-review.prompt.md"

 freeze() {
   local g src
@@ -477,6 +496,7 @@ freeze() {
   cp "$ROOT/bin/factory" "$RUN/frozen/factory"
   cp "$ROOT/bin/factory.d/factory-round.js" "$RUN/frozen/factory-round.js"  # the worker runs its frozen copy, so it cannot edit the script (F12)
   cp "$ROOT/bin/factory.d/review-output.schema.json" "$RUN/frozen/review-output.schema.json"  # the Codex review reads the frozen copy, so a mid-run edit of it cannot change the review (#38, F4)
+  cp "$ROOT/bin/factory.d/codex-review.prompt.md" "$RUN/frozen/codex-review.prompt.md"  # the Codex review reads the frozen prompt, so a mid-run edit of it cannot change the review (#38, F4)
   cp "$ROOT/bin/factory.d/lib.sh" "$RUN/frozen/lib.sh"
   cp "$ROOT/bin/factory.d/role-settings.json" "$RUN/frozen/role-settings.json"
   cp "$ROOT/bin/factory.d/worker-settings.json" "$RUN/frozen/worker-settings.json"
@@ -515,22 +535,22 @@ exec_frozen() {
 ticket_spent() { jq -s '[.[].cost_usd // 0] | add // 0' "$LEDGER"; }
 daily_spent()  { jq -s --arg d "$(today)" '[.[] | select(.date == $d) | .cost_usd // 0] | add // 0' "$DAILY"; }

-record() { # round role model result.json [advisor_calls] [advisor_usd] [ran_workflow] [codex]
-  # workflow_agents is the subagents this round spawned; workflow_usd is the round's cost when it ran
-  # the fan-out workflow, else 0 (F12). ranwf is 1 only on a large ticket's round 1. codex is 1 for a
-  # Codex call: cost_usd is null (the dollar caps do not bound Codex, #41) and `usage` carries its
-  # verbatim token counters; ticket_spent, daily_spent, and cmd_status all read cost_usd // 0, so null is safe.
-  local line acalls="${5:-0}" ausd="${6:-0}" ranwf="${7:-0}" codex="${8:-0}"
+record() { # round role model result.json [advisor_calls] [advisor_usd] [workflow_agents] [workflow_usd] [codex]
+  # workflow_agents and workflow_usd come from workflow_ledger (0 0 on every round but a claude worker's
+  # round 1, and on every Codex round). codex is 1 for a Codex call: cost_usd is null (the dollar caps do
+  # not bound Codex, #41) and `usage` carries its verbatim token counters; ticket_spent, daily_spent, and
+  # cmd_status all read cost_usd // 0, so null is safe.
+  local line acalls="${5:-0}" ausd="${6:-0}" wagents="${7:-0}" wusd="${8:-0}" codex="${9:-0}"
   line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-    --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" --argjson codex "$codex" \
+    --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson wagents "$wagents" --argjson wusd "$wusd" --argjson codex "$codex" \
     "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(if \$codex == 1 then null else (.total_cost_usd // 0) end), \
 duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:((.permission_denials // []) | length), \
 subtype:(.subtype // \"unknown\"), usage:(.usage // null), advisor_calls:\$acalls, advisor_usd:\$ausd, \
-workflow_agents:(.subagent_stats.spawned // 0), workflow_usd:(if \$ranwf == 1 then (.total_cost_usd // 0) else 0 end), \
+workflow_agents:\$wagents, workflow_usd:\$wusd, \
 ts:\$ts}" "$4" 2> /dev/null) \
     || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-      --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" --argjson codex "$codex" \
-      '{round:$round, role:$role, model:$model, cost_usd:(if $codex == 1 then null else 0 end), duration_ms:0, num_turns:0, denials:0, subtype:"unknown", usage:null, advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:0, workflow_usd:0, ts:$ts}')
+      --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson wagents "$wagents" --argjson wusd "$wusd" --argjson codex "$codex" \
+      '{round:$round, role:$role, model:$model, cost_usd:(if $codex == 1 then null else 0 end), duration_ms:0, num_turns:0, denials:0, subtype:"unknown", usage:null, advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:$wagents, workflow_usd:$wusd, ts:$ts}')
   printf '%s\n' "$line" >> "$LEDGER"
   printf '%s' "$line" | jq -c --arg date "$(today)" --arg ticket "$KEY" \
     '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$DAILY"
@@ -612,25 +632,58 @@ round_zero() {

 # ---- steps 5 and 6: the worker round ----------------------------------------

-build_worker_prompt() { # round -> prompt path (pending until the call returns a result)
-  local round="$1" pf="$RUN/pending.prompt.md" prev=$((round - 1)) s
+# A large claude ticket runs round 1 as the fan-out workflow (F12); this is the one test of the three
+# values (worker kind, size, round) that gate it. A Codex worker never fans out (it has no Workflow tool).
+runs_workflow() { [ "$WORKER_KIND" = claude ] && [ "${WORKER_SIZE:-small}" = large ] && [ "$1" -eq 1 ]; }
+
+# workflow_agents and workflow_usd for a worker round's ledger line. Only a claude worker's round 1 runs
+# the fan-out; every other round and every Codex round is 0 0. workflow_agents is the Workflow tool_use
+# blocks in the round's stream (the worker's own calls) plus one per builder artifact the integrator left
+# under tasks/ when it wrote tasks/result.json - a lower bound, since a builder that wrote no artifact is
+# counted unmet, not here (the planner and integrator are the Workflow's own subagents, absent from this
+# round's subagent_stats). workflow_usd is the round's total cost only when result.json exists, else 0:
+# the F4 run planned solo, wrote no result.json, and spent nothing on fan-out.
+workflow_ledger() { # round stream.jsonl result.json -> "<agents> <usd>" on stdout
+  local round="$1" stream="$2" resj="$3" agents=0 usd=0
+  if runs_workflow "$round"; then
+    agents=$(jq -s '[.[] | select(.type == "assistant") | .message.content[]?
+      | select(.type == "tool_use" and .name == "Workflow")] | length' "$stream" 2> /dev/null)
+    [ -n "$agents" ] || agents=0
+    if [ -f "$RUN/tasks/result.json" ]; then
+      agents=$(( agents + $(find "$RUN/tasks" -maxdepth 1 -name '[0-9]*.md' 2> /dev/null | wc -l) ))
+      usd=$(jq -r "$RESULT_OBJ | .total_cost_usd // 0" "$resj" 2> /dev/null)
+      [ -n "$usd" ] || usd=0
+    fi
+  fi
+  printf '%s %s\n' "$agents" "$usd"
+}
+
+build_worker_prompt() { # round -> prompt path (pending until the call returns a result); non-zero when a Codex skill will not resolve
+  local round="$1" pf="$RUN/pending.prompt.md" prev=$((round - 1)) s sf
   { printf '%s\n\n' "$BODY"; cat "$RUN/frozen/_common.md"; } > "$pf"
   # Skills per role (LOOP.md): a Claude worker gets one Skill-tool sentence per `skills:` name (never a
   # slash command, which would swallow the body, #37/#40); a Codex worker has no Skill tool and swallows
-  # an unknown `/<skill>` line (#41), so it gets each named skill's body pasted from ~/.claude/skills/.
+  # an unknown `/<skill>` line (#41), so it gets each named skill's body pasted (skill_file resolves it).
   if [ "$WORKER_KIND" = codex ]; then
-    section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
-      | while read -r s; do
-          sf="$HOME/.claude/skills/$s/SKILL.md"
-          if [ -f "$sf" ]; then printf '\n## Skill: %s\n\n%s\n' "$s" "$(cat "$sf")"
-          else printf '\nUse the "%s" skill (its body was not found under ~/.claude/skills/%s/SKILL.md).\n' "$s" "$s"; fi
-        done >> "$pf"
+    while IFS= read -r s; do
+      [ -n "$s" ] || continue
+      if sf=$(skill_file "$s"); then
+        printf '\n## Skill: %s\n\n%s\n' "$s" "$(cat "$sf")" >> "$pf"
+      else
+        # Lint guaranteed the name is a skills.txt line, so no resolution is an install gap, not a typo;
+        # a "use the X skill" sentence Codex has no Skill tool to honor would be worse than stopping.
+        # build_worker_prompt runs in $(...), so return non-zero; worker_round turns it into finish.
+        log "skill \"$s\" resolves to no SKILL.md; a Codex worker cannot be given its body"
+        return 3
+      fi
+    done < <(section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep .)
   else
     section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
       | while read -r s; do printf 'Before the first edit, call the Skill tool with "%s".\n' "$s"; done >> "$pf"
   fi
-  # A large ticket runs round 1 as the fan-out workflow; the F11 advisor is the Fable check on the split (F12).
-  if [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; then
+  # A large claude ticket runs round 1 as the fan-out workflow; a Codex worker gets the ordinary round-1
+  # prompt (runs_workflow is false for it). The F11 advisor is the Fable check on the split (F12).
+  if runs_workflow "$round"; then
     {
       printf '\n\n## Large ticket, round 1: run the fan-out workflow\n\n'
       printf 'Remove %s/tasks/result.json if it exists, then run the Workflow tool with scriptPath `%s/frozen/factory-round.js` and args `{"ticket": "%s/frozen/issue.md", "run": "%s"}`. ' "$RUN" "$RUN" "$RUN" "$RUN"
@@ -653,15 +706,15 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
 # record and assert_call_ok read unchanged. The last `turn.completed` carries `usage`, passed through
 # verbatim so the five token counters are not hardcoded (#41). No `turn.completed`, or a non-zero exit,
 # is the environment, not a round (LOOP.md, Exits): subtype no-result / is_error true stops it.
-codex_result() { # jsonl exit_code -> result JSON on stdout
-  jq -s --argjson rc "${2:-0}" '
+codex_result() { # jsonl exit_code [duration_ms] -> result JSON on stdout; duration_ms is the caller's wall clock ($SECONDS), no sample shows a per-turn field (#41)
+  jq -s --argjson rc "${2:-0}" --argjson dur "${3:-0}" '
     [.[] | select(.type == "turn.completed")] as $turns
     | [.[] | select(.type == "turn.failed" or .type == "error")] as $errs
     | {
         subtype: (if ($turns | length) > 0 then "success" else "no-result" end),
         is_error: ($rc != 0 or ($errs | length) > 0),
         num_turns: ($turns | length),
-        duration_ms: ($turns[-1].duration_ms // 0),
+        duration_ms: $dur,
         total_cost_usd: null,
         usage: ($turns[-1].usage // null),
         result: ((($errs[-1].message // $errs[-1].error) // (if $rc != 0 then "codex worker call exited " + ($rc | tostring) else "" end)) // "")
@@ -675,18 +728,19 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   # The first round this process runs; a login expired at launch retries only its call. A global,
   # not a local, so it survives the loop's later rounds.
   [ -n "${FIRST_WORKER_ROUND+x}" ] || FIRST_WORKER_ROUND="$round"
-  pf=$(build_worker_prompt "$round")
+  pf=$(build_worker_prompt "$round") || finish ticket-defect "a skill this ticket names resolves to no SKILL.md under ~/.claude/skills or the plugin cache; see the log"
   if [ "$WORKER_KIND" = codex ]; then
     # The Codex worker: JSONL stream is stdout, -o is the last message, < /dev/null keeps Codex off the
     # caller's stdin (#41). No dollar budget bounds it (cost_usd null); CALL_TIMEOUT_SEC and MAX_HOURS do.
-    local rc ranwf=0
-    { [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; } && ranwf=1
+    local rc start wl wagents wusd
     log "codex worker call: round $round model=$CODEX_MODEL (dollar caps do not bound it), prompt=$(wc -c < "$pf") bytes"
     rm -f "$out"
+    start=$SECONDS
     ( cd "$WORKTREE" && PATH="$CODEX_PATH:$PATH" ${t[@]+"${t[@]}"} codex exec --json -s workspace-write "$(cat "$pf")" > "$out" -o "$RUN/round-$round.last.txt" < /dev/null ); rc=$?
     [ "$rc" -eq 0 ] || log "codex worker call exited $rc (the result decides)"
-    codex_result "$out" "$rc" > "$res"
-    record "$round" worker "$CODEX_MODEL" "$res" 0 0 "$ranwf" 1
+    codex_result "$out" "$rc" "$(( (SECONDS - start) * 1000 ))" > "$res"
+    wl=$(workflow_ledger "$round" "$out" "$res"); wagents=${wl% *}; wusd=${wl#* }
+    record "$round" worker "$CODEX_MODEL" "$res" 0 0 "$wagents" "$wusd" 1
     assert_call_ok worker "$res"
     mv "$pf" "$RUN/round-$round.prompt.md"
     mv "$out" "$RUN/round-$round.jsonl"
@@ -723,10 +777,10 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   ausd=$(jq -r --arg m "$WORKER_MODEL" \
     '[(.modelUsage // {}) | to_entries[] | select(.key != $m) | .value.costUSD] | add // 0' "$res" 2> /dev/null) || ausd=0
   [ -n "$ausd" ] || ausd=0
-  # A large ticket runs its workflow in round 1; that round's fields carry the fan-out spend (F12).
-  local ranwf=0
-  { [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; } && ranwf=1
-  record "$round" worker "$WORKER_MODEL" "$res" "$acalls" "$ausd" "$ranwf"
+  # workflow_agents and workflow_usd for this round: 0 0 unless this is a large claude ticket's round 1 (F12).
+  local wl wagents wusd
+  wl=$(workflow_ledger "$round" "$out" "$res"); wagents=${wl% *}; wusd=${wl#* }
+  record "$round" worker "$WORKER_MODEL" "$res" "$acalls" "$ausd" "$wagents" "$wusd"
   assert_call_ok worker "$res"
   mv "$pf" "$RUN/round-$round.prompt.md"
   mv "$out" "$RUN/round-$round.jsonl"
@@ -865,17 +919,20 @@ run_review() { # round -> 0 when nothing blocks
 }

 run_codex_review() { # round -> 0 when nothing blocks; needs-attention with a critical or high finding blocks once (LOOP.md)
-  local round="$1" f="$RUN/round-$1.codex-review.json" jsonl="$RUN/round-$1.codex-review.jsonl" res="$RUN/round-$1.codex-review.result.json" base blocking rc
+  local round="$1" f="$RUN/round-$1.codex-review.json" jsonl="$RUN/round-$1.codex-review.jsonl" res="$RUN/round-$1.codex-review.result.json" base blocking rc start
   base=$(cat "$RUN/base.sha")
   assert_caps
   stop_requested && finish stopped "FACTORY_STOP before the Codex review call"
   log "codex review call: round $round schema=frozen/review-output.schema.json"
-  # `codex exec review` ignores --output-schema, so the review is plain `codex exec` with the schema (#41):
-  # the -o file holds the schema-validated JSON, the JSONL stream (stdout) carries usage for the ledger.
-  ( cd "$WORKTREE" && PATH="$CODEX_PATH:$PATH" ${TIMEOUT_G[@]+"${TIMEOUT_G[@]}"} codex exec --json --output-schema "$RUN/frozen/review-output.schema.json" -o "$f" -s workspace-write "Review the git diff ${base}...HEAD for bugs. Reply with one JSON object matching the review-output schema: verdict, summary, findings, next_steps." > "$jsonl" < /dev/null ); rc=$?
+  # A review needs no write access, so it runs read-only: under workspace-write it could edit the tree the
+  # judge and reviewer already graded. `codex exec review` ignores --output-schema, so the review is plain
+  # `codex exec` with the schema (#41): the -o file holds the schema-validated JSON, the JSONL stream
+  # (stdout) carries usage for the ledger. The one-line prompt is the frozen file with <base> filled in.
+  start=$SECONDS
+  ( cd "$WORKTREE" && PATH="$CODEX_PATH:$PATH" ${TIMEOUT_G[@]+"${TIMEOUT_G[@]}"} codex exec --json --output-schema "$RUN/frozen/review-output.schema.json" -o "$f" -s read-only "$(sed "s/<base>/$base/" "$RUN/frozen/codex-review.prompt.md")" > "$jsonl" < /dev/null ); rc=$?
   [ "$rc" -eq 0 ] || log "codex review call exited $rc"
-  codex_result "$jsonl" "$rc" > "$res"
-  record "$round" codex-review "$CODEX_MODEL" "$res" 0 0 0 1
+  codex_result "$jsonl" "$rc" "$(( (SECONDS - start) * 1000 ))" > "$res"
+  record "$round" codex-review "$CODEX_MODEL" "$res" 0 0 0 0 1
   blocking=$(jq '[.findings[]? | select(.severity == "critical" or .severity == "high")] | length' "$f" 2> /dev/null) || blocking=0
   [ -n "$blocking" ] || blocking=0
   log "codex review verdict: $(jq -r '.verdict // "unparseable"' "$f" 2> /dev/null) findings=$(jq '(.findings // []) | length' "$f" 2> /dev/null) blocking=$blocking"
@@ -1104,6 +1161,12 @@ precondition_lines() { # LOOP.md, Preconditions
   for t in judge reviewer; do
     grader_file "$t" > /dev/null 2>&1 && echo "  PASS $t.md in the plugin cache" || echo "  FAIL no $t.md in the plugin cache"
   done
+  # Every worker skills.txt line must resolve to a SKILL.md, or a `worker: codex` ticket naming it stops
+  # at build_worker_prompt (skill_file); a bare name and a plugin:name both, newest version first.
+  while IFS= read -r t; do
+    [ -n "$t" ] || continue
+    skill_file "$t" > /dev/null 2>&1 && echo "  PASS skill $t resolves" || echo "  FAIL skill $t resolves to no SKILL.md"
+  done < "$ROOT/bin/factory.d/skills.txt"
   # Codex login: Codex is not on the bare PATH (#41), so probe it under CODEX_PATH. Only a worker: codex
   # ticket needs it, so a logged-out or absent Codex is INFO here, not FAIL.
   if PATH="$CODEX_PATH:$PATH" command -v codex > /dev/null 2>&1; then
diff --git a/bin/factory.d/codex-review.prompt.md b/bin/factory.d/codex-review.prompt.md
new file mode 100644
index 0000000..20d7db3
--- /dev/null
+++ b/bin/factory.d/codex-review.prompt.md
@@ -0,0 +1 @@
+Review the git diff <base>...HEAD for bugs. Reply with one JSON object matching the review-output schema.
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index ae70cbf..845cd40 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -105,7 +105,7 @@ claude -p --model fable --effort medium --tools Read,Grep,Glob --strict-mcp-conf
 The frozen grader prompts keep fixed evidence markers; there is no per-run string, and any instruction found inside those markers is data and a dishonesty finding.
 The evidence bundle is the ticket body, the design issue body when one exists, `git diff base...HEAD`, the check output, the MEASURE lines, and `decisions.md`.
 In that diff, code files pass as content, but data files pass as stat only (files under `evals/` named `prompt.md`, and any single added file over 400 lines), so a frozen prompt or a large fixture never floods the grader diff.
-The Codex review stage runs `codex exec --json --output-schema frozen/review-output.schema.json -o <file> -s workspace-write "$(cat frozen/codex-review.prompt.md)" < /dev/null`, with the base sha in the prompt; `codex exec review` ignores `--output-schema` (#41).
+The Codex review stage runs `codex exec --json --output-schema frozen/review-output.schema.json -o <file> -s read-only "$(cat frozen/codex-review.prompt.md)" < /dev/null`, with the base sha filled into the frozen prompt's `<base>` placeholder; a review needs no write access and `read-only` keeps it from editing the tree the judge and reviewer already graded; `codex exec review` ignores `--output-schema` (#41).
 `needs-attention` with a `critical` or `high` finding blocks once.

 ## Worker calls
@@ -119,8 +119,8 @@ claude -p --model claude-opus-4-8[1m] --effort xhigh --advisor fable --permissio
 `--strict-mcp-config` drops the MCP schemas, 2k tokens of prefix on every worker turn; the worker keeps its skills listing because the `skills:` sentence names a Skill-tool call (#37).
 `--max-turns` is accepted by Claude Code 2.1.263, the runner's login-shell binary (#40; a plain shell resolves an older nvm copy), though absent from its `--help`.
 `worker-settings.json` is deny-only, the lean-v3 list plus `Bash(gh:*)` so a worker cannot touch GitHub at all, plus the `Stop` hook (see The worker prompt); `role-settings.json`, loaded only by grader calls, carries the same deny rules with no hook.
-The Codex worker runs `codex exec --json -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.md < /dev/null`: the JSONL stream is stdout and `-o` is the last-message file.
-Its workspace-write sandbox does not block `.env` reads (#41); F4 denies them in Codex config (`ROADMAP.md`).
+The Codex worker runs `codex exec --json -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.txt < /dev/null`: the JSONL stream is stdout and `-o` is the last-message file.
+Its workspace-write sandbox does not block `.env` reads (#41); no deny is configured, and the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk.

 ## The worker prompt

diff --git a/docs/factory/ROADMAP.md b/docs/factory/ROADMAP.md
index 1d84722..0ef4b12 100644
--- a/docs/factory/ROADMAP.md
+++ b/docs/factory/ROADMAP.md
@@ -65,7 +65,7 @@ Merge checklist: bump the plugin version; check the listing weight.

 Goal and why: `worker: codex` and `codex-review: yes` as specified in `LOOP.md`.
 Do not touch: the standing list. Except: `bin/factory`, `bin/factory.d/`.
-Done checks: `codex-review: yes` adds one review section shaped by `review-output.schema.json`; the Codex worker's config denies `.env` reads (`../research/sandbox-and-codex-keys.md`, `"**/*.env" = "deny"`); `codex login status` is a preflight line.
+Done checks: `codex-review: yes` adds one review section shaped by `review-output.schema.json`; the Codex worker's workspace-write sandbox does not block `.env` reads (#41), and no deny is configured, so the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk; `codex login status` is a preflight line.
 Merge checklist: a hand run of a Track B ticket with `worker: codex` reaches `pr-opened`; Codex token counts appear in the ledger for that run; a fixture `.env` is confirmed absent from the round's JSONL, since the sandbox does not block the read (#41); run directory path in the PR body.

 ## F9 frontier timer
~~~~~~~~~~~~ evidence
