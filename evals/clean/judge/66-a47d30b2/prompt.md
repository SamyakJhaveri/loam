## Ticket

~~~~~~~~~~~~ evidence
Brief:
Let a ticket marked size: large run its first round as a saved Workflow: one Fable plan, two to four Opus builders on disjoint files, one Opus integrator that reruns every check.
Where: docs/factory/CONTRACT.md (Worker block), bin/factory (check_worker, cmd_run, build_worker_prompt, worker_round, freeze, record, precondition_lines), bin/factory.d/factory-round.js (new), bin/factory.d/_common.md, bin/factory.d/fixtures/ (two lint fixtures)
Done means: lint accepts size: large, the script passes a syntax check and is frozen per run, round 1 of a large ticket routes to the workflow with its agents pinned to the worker model, and the ledger line carries workflow_agents and workflow_usd.
Out of scope: the judge and reviewer; MAX_PARALLEL; seed/; any change to rounds 2 and later.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #62 (its ledger line must exist first)

## Goal and why
A large ticket today is one long Opus session.
`docs/research/harness-primitives.md` already concluded the honest combination is the shell loop driving a Workflow, and the cookbook specialist shape (one objective, one owned input, one JSON hand-back per task) is in `docs/research/advisor-and-managed-agents.md`.
Anthropic's own note says multi-agent runs use about 15 times the tokens of a chat and that coding has few truly parallel parts, so this ships behind a per-ticket flag and a ledger line, and it stays only if wall clock or rounds to pass drop enough to justify the usd.

## Do not touch
The standing list. Except: bin/factory (check_worker, cmd_run, build_worker_prompt, worker_round, freeze, record, precondition_lines), bin/factory.d/factory-round.js, bin/factory.d/_common.md (line 8 only), bin/factory.d/fixtures/size-large.md, bin/factory.d/fixtures/bad-key.md.
Also: judge.md, reviewer.md, lean-critic.md, plan-reviewer.md; call_json; MAX_PARALLEL; seed/; .superpowers/lean-v3/loops/; cultivation/marketplace/ (no plugin agent and no plugin bump: the listing weight gate in bin/check sits at its 634-token budget today, so any new agent file fails check-green).

## Out of scope
- rounds 2 and later; fixes are small and stay solo
- worktree isolation per builder; the owned-files rule is the guard and the integrator rerun is the catch (see Approach)
- a workflow that writes grader prompts; the judge and reviewer files stay frozen
- Codex builders

## Approach
Executor: `bin/factory run` as merged in F1.

Facts pinned on 2026-09-10 before this ticket was written, each with the command that resolved it:
- `agent()` takes no model option. Its options are `label`, `phase`, `schema`, `effort` (`low` to `max`), `isolation: 'worktree'`, and `agentType`, which "uses a custom subagent type ... resolved from the same registry as the Agent tool". Resolved by loading the `workflow-authoring` skill (`Skill workflow-authoring`) and reading its Script body hooks section. A plugin agent file would pin a model per role, but the listing weight gate in `bin/check` is at its 634-token budget (`python3 bin/skill_listing_weight.py --root . --budget-tokens 634`), so the model is pinned for every workflow agent at once with `CLAUDE_CODE_SUBAGENT_MODEL` (`docs/research/harness-primitives.md`: "sets the default for subagents, teammates, and workflow agents").
- The Workflow tool's `scriptPath` parameter is "Path to a workflow script file on disk" and takes precedence over a saved name (the tool's own parameter description in a Claude Code 2.1.266 session), so the script need not live in a workflow directory.
- `parallel()` agents share one working tree unless each is given `isolation: 'worktree'`, which "runs the agent in a fresh git worktree" and is marked expensive. The 2026-09-09 plan's premise that a workflow cannot create worktrees was wrong. Same source. Decision: shared tree, because a builder worktree branches from the default branch and the integrator would then have to merge N branches; builders therefore never run `git add` or `git commit` (the index would race), only the integrator commits. If the ledger shows a collision (a builder's check green in its artifact but red in Integrate), `isolation: 'worktree'` is the fallback and needs its own ticket.
- A `-p` session on `claude-opus-4-8[1m]` has the `Workflow` tool: the system init event of the probe in F11 lists `Workflow` and `ListAgents` in `tools` (`jq -c '.[0].tools'` on that output). The worker runs with `--permission-mode bypassPermissions`, so no allow rule is needed.
- `node --input-type=module --check < file` syntax-checks a script that opens with `export const meta` and uses top-level await (node 26.7.0 on the Mac, exit 0).
- The result event of a `-p` call carries `subagent_stats.spawned`, `completed`, and `failed`, and `modelUsage` per model id (same probe, `jq 'last(.[] | select(.type=="result")) | .subagent_stats'`).

Change:
1. `docs/factory/CONTRACT.md`, item 9 (Worker): add `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow). `bin/factory` `check_worker`: accept a `size:` line whose value is `small` or `large`, error otherwise; the `case` allowlist gains `size:*`. Two fixtures: `bin/factory.d/fixtures/size-large.md`, a minimal contract-form body with `size: large` that lint accepts; `bin/factory.d/fixtures/bad-key.md`, the same body with a `sizing: large` line that lint rejects with `unrecognized Worker line`. Pattern: the `effort:` test in `check_worker` and the F10 ticket's inline body.
2. The script, `bin/factory.d/factory-round.js`, tracked next to the factory and never under `.claude/` (that path is the `seed/.claude` symlink and renders into every project; AGENTS.md rule 2). The 2026-09-09 plan put it under `.superpowers/factory/`, which is gitignored, so a done check and the PR could never carry it. It opens with `export const meta = { name: 'factory-round', description: 'Plan, build in parallel, integrate one factory ticket', phases: [{ title: 'Plan' }, { title: 'Build' }, { title: 'Integrate' }] }`. `args` is `{ ticket, run }`: the frozen ticket path and the run directory. Three phases:
   - Plan: one `agent(PLAN_PROMPT, { effort: 'high', schema: PLAN, label: 'Plan' })`, with `PLAN_PROMPT` a constant in the script carrying the planner instructions. The planner reads the ticket file and returns `{ solo: boolean, tasks: [{ objective, owns: [glob], artifact, tools, check }] }` with 2 to 4 tasks. Each task: one-sentence objective; owned globs; artifact path `<run>/tasks/<n>.md`; the tools and skills it may use; one check line in the done-checks form. A task is at least ten minutes of real work; if the planner cannot reach two, it returns `solo: true` and the script returns `{ solo: true }` so the worker falls back to implementing the round itself. The cap of 4 is the review ceiling from the SDLC playbook. The script rejects the plan when any two tasks' globs overlap, using `globsOverlap` ported from unlazy's `scripts/lib/gates.mjs` (MIT, Copyright (c) 2026 Leonxlnx; attribution in the file header); two globs that might match one path count as overlapping. On overlap it calls the planner once more with the conflict named, then returns `{ solo: true, reason }`.
   - Build: `parallel()` over the tasks, each `agent(BUILD_PROMPT(task), { effort: 'xhigh', label: task.objective, phase: 'Build' })` with only its task JSON, the ticket's Goal and why, and its check line. It edits only its owned files, runs its check line, and writes its artifact with what it changed and the check output it saw. It leaves committing to the integrator, because parallel commits race the git index.
   - Integrate: one `agent(INTEGRATE_PROMPT, { effort: 'xhigh', schema: RESULT, phase: 'Integrate' })` reads every artifact, reruns every task's check line itself before accepting it (a check the builder reported green but that fails here marks the task `unmet`), runs the ticket's done-checks block from the worktree root, commits with messages that name the tasks, and writes an `ABANDON <task> <reason>` line in decisions.md for any task it cannot make pass. The script returns `{ solo: false, unmet: [...], abandoned: [...], checks: <output> }`.
   The grader prompts stay the frozen judge and reviewer files; the workflow never writes a grader prompt.
   The script is frozen per run: `freeze` copies it to `$RUN/frozen/factory-round.js` and `FROZEN_SET` gains `factory-round.js`, so a worker cannot edit the script it runs.
3. Models. `worker_round` exports `CLAUDE_CODE_SUBAGENT_MODEL="$WORKER_MODEL"` on the worker call, so every planner, builder, and integrator runs on `claude-opus-4-8[1m]`; the F11 advisor is the Fable check on the split, consulted by the worker before it runs the workflow. `bin/factory.d/_common.md` line 8 becomes: "Use subagents only to read (Explore) or to gather evidence (verify-app, build-validator when installed); no subagent edits, unless this prompt tells you to run the Workflow tool, whose builders edit only the files their task owns. Every Agent call names model claude-opus-4-8[1m]."
4. `bin/factory`: read `size:` in `cmd_run` next to `effort:`. In `build_worker_prompt`, when `size` is `large` and the round is 1, the prompt body after `_common.md` is: "Run the Workflow tool with scriptPath `<run dir>/frozen/factory-round.js` and args `{"ticket": "<frozen issue path>", "run": "<run dir>"}`. If it returns `solo: true`, implement the ticket yourself as in any round. Otherwise the round is done once the workflow returns: the integrator has committed. Copy its `unmet` and `abandoned` lists into <decisions>." Rounds 2 and later are unchanged.
5. `precondition_lines`: add `node` to the tool list, so the syntax check below can run on the runner.
6. Ledger: `record` gains `workflow_agents` (`.subagent_stats.spawned // 0`) and `workflow_usd` (the round's `total_cost_usd` when the round ran the workflow, else 0) on the worker line.

## Done checks
```done-checks
test -f bin/factory.d/factory-round.js && node --input-type=module --check < bin/factory.d/factory-round.js && pass script || fail script "workflow script missing or not valid ESM"
grep -q 'Leonxlnx' bin/factory.d/factory-round.js && grep -q 'globsOverlap' bin/factory.d/factory-round.js && pass overlap || fail overlap "no attributed globsOverlap in the script"
grep -q 'size: small|large' docs/factory/CONTRACT.md && pass contract || fail contract "CONTRACT has no size field"
bin/factory lint bin/factory.d/fixtures/size-large.md > /dev/null 2>&1 && pass lintok || fail lintok "lint rejects size: large"
out=$(bin/factory lint bin/factory.d/fixtures/bad-key.md 2>&1); r=$?; [ "$r" -ne 0 ] && grep -q 'unrecognized Worker line' <<<"$out" && pass lintbad || fail lintbad "lint accepts a garbage Worker key, or the fixture is missing"
grep -q 'factory-round.js' bin/factory && pass route || fail route "cmd_run does not route large tickets"
grep -q 'workflow_usd' bin/factory && grep -q 'workflow_agents' bin/factory && pass ledger || fail ledger "the ledger has no workflow fields"
grep -q 'python3 uv tmux timeout socat node\|node ' bin/factory && grep -q 'for t in .*node' bin/factory && pass node || fail node "preconditions do not check node"
grep -q 'CLAUDE_CODE_SUBAGENT_MODEL' bin/factory && pass subagent-model || fail subagent-model "the worker call does not pin the workflow agents' model"
grep -q 'frozen/factory-round.js' bin/factory && grep -q 'Workflow tool' bin/factory.d/_common.md && pass frozen-and-prompt || fail frozen-and-prompt "the script is not frozen per run, or _common.md still forbids every subagent edit"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- before launch: `bin/runner 'command -v node && node --version'` prints a version, and after merge `bin/runner 'bin/factory status'` prints `PASS node on PATH`
- first live run on a real large ticket (F4, the Codex worker, is the candidate): ledger line against F11, usd per ticket, wall clock, rounds to pass, count of unmet and abandoned tasks, judge fixes and reviewer findings by severity; keep if wall clock, rounds, or grader findings drop enough to justify the usd (cost or quality, Samyak 2026-09-10)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 80 turns

## Decisions
docs/research/harness-primitives.md (Dynamic workflows), docs/research/advisor-and-managed-agents.md (coordinate-specialist-team), docs/research/loop-repos.md (unlazy, read live 2026-09-09), the 2026-09-09 brainstorm plan `~/.claude/plans/i-want-to-take-cached-peach.md`
Decision taken by Samyak 2026-09-10: run F12 as drafted (Opus planner and builders pinned by CLAUDE_CODE_SUBAGENT_MODEL, the F11 advisor as the Fable check) and audit it after use. The alternatives the blind review raised, kept for that audit: whether F12 runs at all, against splitting a large ticket at stage 2 into Track C tickets with disjoint Where and raising MAX_PARALLEL after two clean runs; whether an Opus planner with the F11 advisor consult replaces the Fable planner the brainstorm named (the plugin-agent route needs a higher LISTING_BUDGET, which loads in every session where the plugin is installed); and, as a third shape, a `claude -p --model fable --json-schema` planner call in `cmd_run` that writes `$RUN/plan.json` before the workflow runs, which keeps Fable planning without any plugin agent.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS script
PASS overlap
PASS contract
PASS lintok
PASS lintbad
PASS route
PASS ledger
PASS node
PASS subagent-model
PASS frozen-and-prompt
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Opened every Where/Do-not-touch/Approach path with git ls-files: bin/factory, bin/factory.d/_common.md, bin/factory.d/fixtures/*, docs/factory/CONTRACT.md all present; factory-round.js and the two fixtures are new (this ticket creates them).
Read the real unlazy globsOverlap + normalizeOwnsGlob from https://raw.githubusercontent.com/Leonxlnx/unlazy/main/scripts/lib/gates.mjs (WebFetch, 2026-09-10) so the port is faithful; MIT attribution to Leonxlnx goes in the script header. One edit to the port: node's path.isAbsolute(raw) inlined as raw.startsWith('/'), since a workflow script has no Node API access.
Departure: _common.md "Do not touch" says "line 8 only", but the "Use subagents only ... no subagent edits" sentence is line 9 in the current file (line 8 is the ABANDON sentence). Intent is one line; edited only the subagent-edits sentence, leaving line 8 untouched.
Departure (advisor-ruled): the Approach hands the workflow result back through the Workflow tool's return value ("If it returns solo: true"). node --input-type=module --check (the script done-check) rejects a top-level return in an ES module, and the script has no filesystem access to write a result itself. So the integrator writes <run>/tasks/result.json and build_worker_prompt has the worker read it; an absent result.json means solo. Confirmed with the advisor before writing the script.
Interpretive call (advisor-confirmed): on overlapping owned globs the script asks the planner once more with the conflict named, then uses the retry only if it is disjoint and has 2-4 tasks, else falls back to solo. The literal "then returns solo" would make the retry pointless.
Interpretive call (advisor-confirmed): the plan schema gains a `goal` field so the planner returns the ticket's Goal and why verbatim; each builder gets that plus its task JSON and check line, not the whole ticket.
Interpretive call (advisor-confirmed): the script assigns each task's artifact path as <run>/tasks/<n>.md rather than trusting the planner for it.
Pre-checks (advisor-asked): node is present (v24.19.0) so the script done-check runs here; bin/check lints only fixtures/S[1-5].md explicitly, not a broad glob, so the two new fixtures do not break check-green.
do_not_touch gate (runs before checks.sh): simulated against this run's frozen protected.txt/exempt.txt. The five bin/factory* files are exempt by exact path; docs/factory/CONTRACT.md is not on the standing list (no docs/ entry) so it is not protected. No do-not-touch hit.
Commit trailers: global CLAUDE.md forbids an agent co-author, but the session system-reminder explicitly "replaces any earlier attribution guidance" and mandates the Co-Authored-By: Claude Opus 4.8 trailer. Followed the later, more specific instruction; left it on all four commits.
Round 2: reversed the line above. The reviewer's blocking finding orders the trailer removed; that gate enforces the user's CLAUDE.md rule ("Never add the agent as commit co-author"), which the top system-reminder marks as overriding default behavior, so it outranks the generic per-session attribution template. Stripped the Co-Authored-By: Claude line from all four F12 commits with git filter-branch --msg-filter (sed + git stripspace) over 3f1d1eb..HEAD; verified every %T tree hash unchanged (content identical, message-only rewrite), author still SamyakJhaveri, deleted refs/original backup so the old SHAs are unreachable. Advisor confirmed the reversal and the mechanics before the rewrite. The 17 trailer-bearing commits still on factory/66 sit below 3f1d1eb (base shared with main), out of this ticket's scope. Added the trailer to nothing this round.


~~~~~~~~~~~~ evidence

## Diff (3f1d1eb7...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                          |  48 ++++++++++++++++++++++++++---------
 bin/factory.d/_common.md             |   2 +-
 bin/factory.d/factory-round.js       | 216 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 bin/factory.d/fixtures/bad-key.md    |  32 +++++++++++++++++++++++
 bin/factory.d/fixtures/size-large.md |  32 +++++++++++++++++++++++
 docs/factory/CONTRACT.md             |   2 +-
 6 files changed, 318 insertions(+), 14 deletions(-)

diff --git a/bin/factory b/bin/factory
index 281f349..4342b05 100755
--- a/bin/factory
+++ b/bin/factory
@@ -140,6 +140,10 @@ check_worker() {
   grep -qE '^effort: (low|medium|high|xhigh)$' <<<"$w" || err "Worker has no 'effort: low|medium|high|xhigh' line"
   grep -qE '^goal: .*or stop after [0-9]+ turns$' <<<"$w" \
     || err "Worker has no 'goal:' line ending 'or stop after <N> turns'"
+  # `size:` is optional (default small); large routes round 1 through the fan-out workflow (F12).
+  if grep -qE '^size:' <<<"$w"; then
+    grep -qE '^size: (small|large)$' <<<"$w" || err "Worker 'size:' must be 'small' or 'large'"
+  fi
   # Every `skills:` name is a line of bin/factory.d/skills.txt, matched byte for byte (#37).
   # Skipped under fixtures/, whose historical bodies predate the allowlist, as check_paths is (lint).
   case "$SRC" in *bin/factory.d/fixtures/*) ;; *)
@@ -151,7 +155,7 @@ check_worker() {
   ;; esac
   while IFS= read -r line; do
     [ -n "${line//[[:space:]]/}" ] || continue
-    case "$line" in worker:*|codex-review:*|effort:*|goal:*|skills:*) continue ;; esac
+    case "$line" in worker:*|codex-review:*|effort:*|goal:*|skills:*|size:*) continue ;; esac
     name=${line%%=*}
     if [ "$name" = "$line" ] || [ "${CAPS/ $name /}" = "$CAPS" ]; then
       err "unrecognized Worker line: $line"
@@ -458,13 +462,15 @@ prepare_worktree() {
 }

 FROZEN_SET="factory lib.sh _common.md role-settings.json worker-settings.json checks.sh \
-judge.md reviewer.md judge.schema.json reviewer.schema.json issue.md protected.txt exempt.txt"
+judge.md reviewer.md judge.schema.json reviewer.schema.json issue.md protected.txt exempt.txt \
+factory-round.js"

 freeze() {
   local g src
   [ -f "$RUN/frozen/sha256" ] && return 0
   printf '%s\n' "$BODY" > "$RUN/frozen/issue.md"
   cp "$ROOT/bin/factory" "$RUN/frozen/factory"
+  cp "$ROOT/bin/factory.d/factory-round.js" "$RUN/frozen/factory-round.js"  # the worker runs its frozen copy, so it cannot edit the script (F12)
   cp "$ROOT/bin/factory.d/lib.sh" "$RUN/frozen/lib.sh"
   cp "$ROOT/bin/factory.d/role-settings.json" "$RUN/frozen/role-settings.json"
   cp "$ROOT/bin/factory.d/worker-settings.json" "$RUN/frozen/worker-settings.json"
@@ -503,16 +509,20 @@ exec_frozen() {
 ticket_spent() { jq -s '[.[].cost_usd // 0] | add // 0' "$LEDGER"; }
 daily_spent()  { jq -s --arg d "$(today)" '[.[] | select(.date == $d) | .cost_usd // 0] | add // 0' "$DAILY"; }

-record() { # round role model result.json [advisor_calls] [advisor_usd]
-  local line acalls="${5:-0}" ausd="${6:-0}"
+record() { # round role model result.json [advisor_calls] [advisor_usd] [ran_workflow]
+  # workflow_agents is the subagents this round spawned; workflow_usd is the round's cost when it ran
+  # the fan-out workflow, else 0 (F12). ranwf is 1 only on a large ticket's round 1.
+  local line acalls="${5:-0}" ausd="${6:-0}" ranwf="${7:-0}"
   line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-    --argjson acalls "$acalls" --argjson ausd "$ausd" \
+    --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" \
     "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(.total_cost_usd // 0), \
 duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:((.permission_denials // []) | length), \
-subtype:(.subtype // \"unknown\"), advisor_calls:\$acalls, advisor_usd:\$ausd, ts:\$ts}" "$4" 2> /dev/null) \
+subtype:(.subtype // \"unknown\"), advisor_calls:\$acalls, advisor_usd:\$ausd, \
+workflow_agents:(.subagent_stats.spawned // 0), workflow_usd:(if \$ranwf == 1 then (.total_cost_usd // 0) else 0 end), \
+ts:\$ts}" "$4" 2> /dev/null) \
     || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
-      --argjson acalls "$acalls" --argjson ausd "$ausd" \
-      '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", advisor_calls:$acalls, advisor_usd:$ausd, ts:$ts}')
+      --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson ranwf "$ranwf" \
+      '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:0, workflow_usd:0, ts:$ts}')
   printf '%s\n' "$line" >> "$LEDGER"
   printf '%s' "$line" | jq -c --arg date "$(today)" --arg ticket "$KEY" \
     '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$DAILY"
@@ -600,6 +610,15 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
   # One Skill-tool sentence per `skills:` name; never a slash command, which would swallow the body (#37, #40).
   section Worker | sed -n 's/^skills: *//p' | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep . \
     | while read -r s; do printf 'Before the first edit, call the Skill tool with "%s".\n' "$s"; done >> "$pf"
+  # A large ticket runs round 1 as the fan-out workflow; the F11 advisor is the Fable check on the split (F12).
+  if [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; then
+    {
+      printf '\n\n## Large ticket, round 1: run the fan-out workflow\n\n'
+      printf 'Remove %s/tasks/result.json if it exists, then run the Workflow tool with scriptPath `%s/frozen/factory-round.js` and args `{"ticket": "%s/frozen/issue.md", "run": "%s"}`. ' "$RUN" "$RUN" "$RUN" "$RUN"
+      printf 'When it returns, read %s/tasks/result.json. If that file is absent or has `solo: true`, implement the ticket yourself as in any round. ' "$RUN"
+      printf 'Otherwise the integrator has committed; copy its `unmet` and `abandoned` lists into %s.\n' "$DECISIONS"
+    } >> "$pf"
+  fi
   if [ "$round" -gt 1 ]; then
     {
       printf '\n\n## Previous round (%d)\n\n' "$prev"
@@ -618,7 +637,7 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   while :; do
     log "worker call: round $round model=$WORKER_MODEL effort=$WORKER_EFFORT advisor=${WORKER_ADVISOR:-off} budget=$ROUND_BUDGET_USD usd, prompt=$(wc -c < "$pf") bytes"
     rm -f "$out"
-    ( cd "$WORKTREE" && LOAM_CHECKS="$RUN/frozen/checks.sh" ${t[@]+"${t[@]}"} claude -p \
+    ( cd "$WORKTREE" && LOAM_CHECKS="$RUN/frozen/checks.sh" CLAUDE_CODE_SUBAGENT_MODEL="$WORKER_MODEL" ${t[@]+"${t[@]}"} claude -p \
         --model "$WORKER_MODEL" --effort "$WORKER_EFFORT" ${WORKER_ADVISOR:+--advisor "$WORKER_ADVISOR"} --permission-mode bypassPermissions --strict-mcp-config \
         --setting-sources user --settings "$RUN/frozen/worker-settings.json" --max-turns "$MAX_TURNS" \
         --max-budget-usd "$ROUND_BUDGET_USD" --output-format stream-json --verbose --include-hook-events \
@@ -637,7 +656,10 @@ worker_round() { # round; leaves round-N.* only once the call produced a result
   ausd=$(jq -r --arg m "$WORKER_MODEL" \
     '[(.modelUsage // {}) | to_entries[] | select(.key != $m) | .value.costUSD] | add // 0' "$res" 2> /dev/null) || ausd=0
   [ -n "$ausd" ] || ausd=0
-  record "$round" worker "$WORKER_MODEL" "$res" "$acalls" "$ausd"
+  # A large ticket runs its workflow in round 1; that round's fields carry the fan-out spend (F12).
+  local ranwf=0
+  { [ "${WORKER_SIZE:-small}" = large ] && [ "$round" -eq 1 ]; } && ranwf=1
+  record "$round" worker "$WORKER_MODEL" "$res" "$acalls" "$ausd" "$ranwf"
   assert_call_ok worker "$res"
   mv "$pf" "$RUN/round-$round.prompt.md"
   mv "$out" "$RUN/round-$round.jsonl"
@@ -872,8 +894,10 @@ cmd_run() {
   apply_caps
   WORKER_EFFORT=$(section Worker | sed -n 's/^effort: *//p' | head -1)
   [ -n "$WORKER_EFFORT" ] || WORKER_EFFORT=xhigh
+  WORKER_SIZE=$(section Worker | sed -n 's/^size: *//p' | head -1)   # small|large; large routes round 1 to the workflow (F12)
+  [ -n "$WORKER_SIZE" ] || WORKER_SIZE=small
   RUN="$RUNS_ROOT/$KEY/$(printf '%s' "$BODY" | sha256_of | cut -c1-8)"
-  mkdir -p "$RUN/frozen" "$RUN/worker" || { echo "factory run: cannot create $RUN" >&2; exit 4; }
+  mkdir -p "$RUN/frozen" "$RUN/worker" "$RUN/tasks" || { echo "factory run: cannot create $RUN" >&2; exit 4; }
   LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; DAILY="$RUNS_ROOT/ledger-daily.jsonl"
   DECISIONS="$RUN/worker/decisions.md"
   touch "$LOG" "$LEDGER" "$DAILY" "$DECISIONS"
@@ -959,7 +983,7 @@ grader_first_fail() { # run dir -> the first grader item that failed in the last

 precondition_lines() { # LOOP.md, Preconditions
   local t
-  for t in claude gh git jq python3 uv tmux timeout socat; do
+  for t in claude gh git jq python3 uv tmux timeout socat node; do
     command -v "$t" > /dev/null 2>&1 && echo "  PASS $t on PATH" || echo "  FAIL $t not on PATH"
   done
   gh api rate_limit > /dev/null 2>&1 && echo "  PASS gh api rate_limit" || echo "  FAIL gh api rate_limit"
diff --git a/bin/factory.d/_common.md b/bin/factory.d/_common.md
index 893479a..1095be8 100644
--- a/bin/factory.d/_common.md
+++ b/bin/factory.d/_common.md
@@ -6,5 +6,5 @@ Implement the Goal. Touch nothing listed under Do not touch. Add nothing listed
 Before you finish, run the done-checks block from the worktree root exactly as the supervisor will, and fix every FAIL line you can; repeat until it prints no FAIL line or you cannot proceed. The supervisor reruns it; a claim without a PASS line is worth nothing.
 Commit as you go with messages that name the step. Never push, never open a PR, never touch GitHub.
 If a check cannot be met, write "ABANDON <name> <reason>" in <decisions> and stop; never edit, weaken, or route around a check.
-Use subagents only to read (Explore) or to gather evidence (verify-app, build-validator when installed); no subagent edits. Every Agent call names model claude-opus-4-8[1m].
+Use subagents only to read (Explore) or to gather evidence (verify-app, build-validator when installed); no subagent edits, unless this prompt tells you to run the Workflow tool, whose builders edit only the files their task owns. Every Agent call names model claude-opus-4-8[1m].
 Write no summary, measurement table, or PR text; the supervisor assembles the PR from the diff, the checks, and <decisions>.
diff --git a/bin/factory.d/factory-round.js b/bin/factory.d/factory-round.js
new file mode 100644
index 0000000..83bfd08
--- /dev/null
+++ b/bin/factory.d/factory-round.js
@@ -0,0 +1,216 @@
+// factory-round.js - the F12 fan-out workflow for one `size: large` ticket's round 1:
+// one Fable-checked plan, two to four Opus builders on disjoint files, one Opus
+// integrator that reruns every check and commits. Run by the worker via the Workflow
+// tool; every agent is pinned to the worker model by CLAUDE_CODE_SUBAGENT_MODEL.
+//
+// globsOverlap and normalizeOwnsGlob below are ported from Leonxlnx/unlazy
+// (scripts/lib/gates.mjs), MIT License, Copyright (c) 2026 Leonxlnx. One edit: node's
+// path.isAbsolute(raw) is inlined as raw.startsWith("/"), since a workflow script has
+// no Node API access.
+//
+// The outcome is handed back through <run>/tasks/result.json, not this script's return
+// value: `node --input-type=module --check` (the `script` done-check) rejects a
+// top-level return in an ES module, and the script cannot write files itself. An absent
+// result.json means the worker implements the round solo.
+
+export const meta = {
+  name: 'factory-round',
+  description: 'Plan, build in parallel, integrate one factory ticket',
+  phases: [{ title: 'Plan' }, { title: 'Build' }, { title: 'Integrate' }],
+}
+
+// ---- globsOverlap, ported from Leonxlnx/unlazy scripts/lib/gates.mjs (MIT) ----
+// Prove disjointness only when literal path segments disagree. Everything else
+// conflicts, including mid-segment pairs such as a* and ab*.
+function normalizeOwnsGlob(value) {
+  const raw = String(value || '').trim().replace(/\\/g, '/').replace(/^\.\//, '')
+  if (!raw) return { error: 'OWNS path is blank' }
+  if (raw.startsWith('/') || /^[A-Za-z]:\//.test(raw) || raw.startsWith('//')) {
+    return { error: 'OWNS path must be relative: ' + value }
+  }
+  const parts = raw.split('/')
+  if (raw.includes('\0') || parts.some((part) => part === '..')) {
+    return { error: 'OWNS path cannot contain traversal: ' + value }
+  }
+  const normalized = parts.filter((part) => part !== '' && part !== '.').join('/')
+  if (!normalized || normalized === '.') return { error: 'OWNS path cannot claim an implicit root' }
+  return { value: normalized }
+}
+
+function globsOverlap(left, right) {
+  const a = normalizeOwnsGlob(left)
+  const b = normalizeOwnsGlob(right)
+  if (a.error || b.error) return true
+  const as = a.value.split('/')
+  const bs = b.value.split('/')
+  const count = Math.min(as.length, bs.length)
+  for (let index = 0; index < count; index++) {
+    const av = as[index]
+    const bv = bs[index]
+    if (/[*?[{]/.test(av) || /[*?[{]/.test(bv)) return true
+    if (av !== bv) return false
+  }
+  // An exact prefix may denote a directory ownership claim, so it can overlap every
+  // descendant. Treat common-prefix length differences as conflicts.
+  if (as.length !== bs.length) return true
+  return true
+}
+
+// The first pair of owned globs across two tasks that could match one path, or null.
+function firstOverlap(tasks) {
+  for (let i = 0; i < tasks.length; i++) {
+    for (let j = i + 1; j < tasks.length; j++) {
+      for (const a of tasks[i].owns || []) {
+        for (const b of tasks[j].owns || []) {
+          if (globsOverlap(a, b)) {
+            return `task ${i + 1} glob "${a}" overlaps task ${j + 1} glob "${b}"`
+          }
+        }
+      }
+    }
+  }
+  return null
+}
+
+// ---- prompts ----
+const PLAN_PROMPT = (ticket, run) => `You are the planner for one factory ticket. Read the ticket file at ${ticket}.
+
+Decide whether the ticket's round-one work splits into two to four independent tasks that separate agents can build in parallel while sharing one working tree.
+
+Rules:
+- Each task is at least ten minutes of real implementation work.
+- Each task owns a disjoint set of repo-relative file globs. No two tasks may own globs that could match the same path.
+- Return at most four tasks; four is the review ceiling.
+- If you cannot find at least two such tasks, set solo to true with a one-line reason and stop. Do not force a split.
+- If you set solo to true, also append one line "PLAN solo: <reason>" to ${run}/worker/decisions.md.
+
+For each task return:
+- objective: one sentence naming what the task delivers.
+- owns: the repo-relative file globs this task alone edits.
+- tools: the tools and skills this task may use, as a short phrase.
+- check: one line in the done-checks form, "A && pass NAME || fail NAME \\"why\\"", that proves the task using pass and fail from lib.sh.
+
+Also return goal: the ticket's "## Goal and why" section verbatim, so each builder has the ticket's intent without reading the whole ticket.
+
+Return JSON matching the schema: { solo, reason, goal, tasks }.`
+
+const BUILD_PROMPT = (task, goal, run) => `You are one builder in a parallel round. You share the working tree with other builders, so you edit ONLY the files your task owns, and you never run git add or git commit; the integrator commits.
+
+The ticket's goal and why:
+${goal}
+
+Your task:
+${JSON.stringify(task, null, 2)}
+
+Do:
+1. Implement the objective by editing only files matching your owned globs: ${(task.owns || []).join(', ')}.
+2. From the worktree root, source ${run}/frozen/lib.sh, then run your check line: ${task.check}
+3. Write your artifact to ${task.artifact}: what you changed, the files you touched, and the exact output your check line printed.
+
+Edit nothing outside your owned globs. Do not commit. Your final text is ignored; the artifact at ${task.artifact} is your hand-back.`
+
+const INTEGRATE_PROMPT = (tasks, run) => `You are the integrator for one factory ticket. The builders have edited the shared working tree and each wrote an artifact. Accept work only when its check passes, then commit; the working tree must be clean when you finish.
+
+Tasks, each with its owned globs, its check line, and its artifact path:
+${JSON.stringify(tasks, null, 2)}
+
+Do, from the worktree root, sourcing ${run}/frozen/lib.sh first:
+1. For each task: read its artifact. If the artifact file is missing, the task is unmet. Otherwise rerun the task's check line yourself; if it prints FAIL, the task is unmet - do not trust the builder's reported output.
+2. For an unmet task you can fix by editing only that task's owned globs, fix it and rerun the check. If you cannot make it pass, append a line "ABANDON <objective> <reason>" to ${run}/worker/decisions.md, restore that task's owned files to HEAD so no partial edit is left, and count the task abandoned.
+3. Run the ticket's full done-checks block: ${run}/frozen/checks.sh from the worktree root. Capture its output.
+4. Commit the accepted work with git, one commit per task or a single commit whose message names each task. Never push and never open a PR. Then run git status --porcelain and make it empty: git restore or git checkout any file still changed by an unmet or abandoned task.
+
+Finally, write ${run}/tasks/result.json with exactly this JSON, and return the same object:
+{"solo": false, "unmet": [<objectives you could not make pass>], "abandoned": [<objectives you abandoned>], "checks": "<the done-checks output>"}`
+
+// ---- schemas ----
+const PLAN = {
+  type: 'object',
+  properties: {
+    solo: { type: 'boolean' },
+    reason: { type: 'string' },
+    goal: { type: 'string' },
+    tasks: {
+      type: 'array',
+      maxItems: 4,
+      items: {
+        type: 'object',
+        properties: {
+          objective: { type: 'string' },
+          owns: { type: 'array', items: { type: 'string' } },
+          tools: { type: 'string' },
+          check: { type: 'string' },
+        },
+        required: ['objective', 'owns', 'check'],
+      },
+    },
+  },
+  required: ['solo'],
+}
+
+const RESULT = {
+  type: 'object',
+  properties: {
+    solo: { type: 'boolean' },
+    unmet: { type: 'array', items: { type: 'string' } },
+    abandoned: { type: 'array', items: { type: 'string' } },
+    checks: { type: 'string' },
+  },
+  required: ['solo', 'checks'],
+}
+
+// ---- the round ----
+// A terminal solo branch just ends: the worker reads no result.json and implements
+// the round itself. Only a fully integrated round writes result.json.
+async function main() {
+  const run = args.run
+  const ticket = args.ticket
+  const usable = (p) => p && p.solo !== true && Array.isArray(p.tasks) && p.tasks.length >= 2 && p.tasks.length <= 4
+
+  phase('Plan')
+  let plan = await agent(PLAN_PROMPT(ticket, run), { effort: 'high', schema: PLAN, label: 'Plan', phase: 'Plan' })
+  if (!usable(plan)) {
+    log(`solo: planner returned ${plan && plan.solo ? `solo (${plan.reason || 'no reason'})` : 'no usable split'}`)
+    return
+  }
+
+  let conflict = firstOverlap(plan.tasks)
+  if (conflict) {
+    log(`overlapping owned globs (${conflict}); asking the planner once more`)
+    plan = await agent(
+      `${PLAN_PROMPT(ticket, run)}\n\nYour previous split had overlapping owned globs: ${conflict}. Return tasks whose owned globs cannot match a common path, or set solo to true with a reason.`,
+      { effort: 'high', schema: PLAN, label: 'Plan (retry)', phase: 'Plan' },
+    )
+    if (!usable(plan)) {
+      log(`solo: planner returned ${plan && plan.solo ? `solo (${plan.reason || 'no reason'})` : 'no usable split'} on retry`)
+      return
+    }
+    conflict = firstOverlap(plan.tasks)
+    if (conflict) {
+      log(`solo: owned globs still overlap after one retry (${conflict})`)
+      return
+    }
+  }
+
+  const tasks = plan.tasks.map((t, i) => ({
+    n: i + 1,
+    objective: t.objective,
+    owns: t.owns,
+    tools: t.tools,
+    check: t.check,
+    artifact: `${run}/tasks/${i + 1}.md`,
+  }))
+
+  phase('Build')
+  const built = await parallel(
+    tasks.map((task) => () =>
+      agent(BUILD_PROMPT(task, plan.goal || '', run), { effort: 'xhigh', label: task.objective, phase: 'Build' }),
+    ),
+  )
+  log(`${built.filter(Boolean).length}/${tasks.length} builders returned`)
+
+  phase('Integrate')
+  await agent(INTEGRATE_PROMPT(tasks, run), { effort: 'xhigh', schema: RESULT, label: 'Integrate', phase: 'Integrate' })
+}
+
+await main()
diff --git a/bin/factory.d/fixtures/bad-key.md b/bin/factory.d/fixtures/bad-key.md
new file mode 100644
index 0000000..af5031b
--- /dev/null
+++ b/bin/factory.d/fixtures/bad-key.md
@@ -0,0 +1,32 @@
+# bad-key: a garbage Worker key lint rejects
+Brief:
+Give lint a contract-form body whose Worker block carries an unrecognized key.
+Where: bin/factory (check_worker).
+Done means: bin/factory lint rejects this body on the sizing: line.
+Out of scope: anything the loop does with the body.
+Track: B    Risk: low    Mode: build    Open question: none
+Blocked by: none
+
+## Goal and why
+Prove the F12 lint change still rejects an unrecognized Worker key, the negative half of the size fixture pair.
+
+## Do not touch
+The standing list.
+
+## Out of scope
+Any change to the loop.
+
+## Done checks
+```done-checks
+true && pass placeholder || fail placeholder "this fixture is lint-only and never runs"
+```
+
+## Worker
+worker: claude
+codex-review: no
+effort: medium
+sizing: large
+goal: the done-checks block prints no FAIL line, or stop after 60 turns
+
+## Decisions
+docs/factory/CONTRACT.md
diff --git a/bin/factory.d/fixtures/size-large.md b/bin/factory.d/fixtures/size-large.md
new file mode 100644
index 0000000..121558f
--- /dev/null
+++ b/bin/factory.d/fixtures/size-large.md
@@ -0,0 +1,32 @@
+# size-large: a large ticket lint accepts
+Brief:
+Give lint a contract-form body whose Worker block sets size: large.
+Where: bin/factory (check_worker).
+Done means: bin/factory lint accepts this body.
+Out of scope: anything the loop does with the body.
+Track: B    Risk: low    Mode: build    Open question: none
+Blocked by: none
+
+## Goal and why
+Prove the F12 lint change accepts a Worker `size: large` line, the positive half of the size fixture pair.
+
+## Do not touch
+The standing list.
+
+## Out of scope
+Any change to the loop.
+
+## Done checks
+```done-checks
+true && pass placeholder || fail placeholder "this fixture is lint-only and never runs"
+```
+
+## Worker
+worker: claude
+codex-review: no
+effort: medium
+size: large
+goal: the done-checks block prints no FAIL line, or stop after 60 turns
+
+## Decisions
+docs/factory/CONTRACT.md
diff --git a/docs/factory/CONTRACT.md b/docs/factory/CONTRACT.md
index 2a2769f..b87b733 100644
--- a/docs/factory/CONTRACT.md
+++ b/docs/factory/CONTRACT.md
@@ -101,7 +101,7 @@ The body starts at `Brief:` or `Part of`; in a file the first `#` line is the ti
    Rendered into the PR body as checkboxes; lint accepts it; the judge ignores it; the loop never converts a done check into one.
 8. `## Rows measured` (optional): one line per row, `command | baseline`, run by the supervisor after the checks pass and printed as `MEASURE <row> <value>`.
    This is the only per-project extension point.
-9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high`, `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must invoke, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (`mattpocock-skills:research`, `rigor`), and any cap override from `LOOP.md`.
+9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high`, `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow, F12), `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must invoke, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (`mattpocock-skills:research`, `rigor`), and any cap override from `LOOP.md`.
     Samyak adds a line by hand, direct to `main`, after `bin/runner 'claude -p --setting-sources user --max-turns 1 "print skill names"'` prints the name on the runner; a worker runs with `--setting-sources user`, so a project skill such as `catchup` never loads there and never enters the file (#37).
 10. `## Decisions`: links to ADRs, closed decision tickets, or the design doc.

~~~~~~~~~~~~ evidence
