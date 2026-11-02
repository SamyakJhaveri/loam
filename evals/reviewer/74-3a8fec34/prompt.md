## Ticket

~~~~~~~~~~~~ evidence
Brief:
Run one real Track B ticket with worker: codex and codex-review: yes, so the Codex stage F4 built is exercised end to end, and give it the five small residuals the F17 reviews left as its work.
Where: bin/factory (build_worker_prompt, precondition_lines, open_pr), docs/factory/LOOP.md, docs/factory/ROADMAP.md
Done means: the round-1 fan-out prompt clears the whole tasks directory, the per-skill preflight line is INFO, the PR-body .env note matches the docs, LOOP.md names bin/factory not loop.sh, and the .env sentence has one home; the run itself proves a Codex worker commits inside a worktree, the read-only review yields a schema-shaped section, and the ledger carries a Codex line.
Out of scope: any change to what Codex is allowed to read; the fan-out script; the graders.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #72 (merged as PR #73)

## Goal and why
F4 built the Codex worker and review stage and F17 fixed what its reviews found, but no ticket has ever run with `worker: codex`.
Three things are unproven and only a run proves them: whether a Codex worker under `workspace-write` can commit inside a git worktree whose real gitdir sits outside its cwd; whether the read-only review returns a schema-shaped section; and what a `.env` read looks like in the JSONL stream.
The work itself is the five residuals the F17 reviews left, each one line, so a Codex failure is cheap to read and a Codex success is a real diff.

## Do not touch
The standing list. Except: bin/factory (build_worker_prompt, precondition_lines, open_pr only), docs/factory/LOOP.md (line 129 only), docs/factory/ROADMAP.md (the F4 entry only).
Also: bin/factory.d/; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- a `.env` deny in Codex config; this run records what the read looks like, the next ticket decides
- the fan-out script and its prompts
- any Codex flag other than the ones F4 and F17 shipped

## Approach
Executor: `bin/factory run` as merged in F1, with the Codex worker call F4 added and the read-only review F17 added.

Facts pinned: the F4 and F17 runs and reviews are in `.superpowers/factory/sessions/manager-2026-09-11-f11.md`; the Codex worker call is `codex exec --json -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.txt < /dev/null` under `PATH=$HOME/.local/bin:$PATH` (`docs/factory/LOOP.md`, Worker calls); Codex has no advisor and no Skill tool, so `_common.md` is the whole standing prompt and this ticket names no skills.

Change, one line each:
1. `build_worker_prompt`, the large-ticket sentence: "Remove `<run>/tasks/` if it exists" in place of removing only `result.json`, so a retried round 1 cannot inherit a builder artifact that `workflow_ledger` would count.
2. `precondition_lines`, the per-skill line: `INFO skill <name> resolves to no SKILL.md (a worker: codex ticket naming it stops)` in place of FAIL; only a Codex ticket needs the body, and the Codex login line two lines below is INFO for the same reason.
3. `open_pr`, the Codex-worker note: "`.env` is readable by the Codex worker (D8, #41). No deny is configured; recorded risk." in place of the sentence that still says F4 denies it.
4. `docs/factory/LOOP.md` line 129: "`build_worker_prompt` in `bin/factory`" in place of `loop.sh`.
5. `docs/factory/ROADMAP.md`, F4 entry: the Done checks line reads "no `.env` deny is configured (`LOOP.md`, Worker calls)"; the sentence about the hand run confirming the read stays only in the Merge checklist line below it and in `LOOP.md`.

## Done checks
```done-checks
grep -q 'Remove .*/tasks/` if it exists' bin/factory && pass tasks-cleared || fail tasks-cleared "the fan-out prompt still removes only result.json"
grep -q 'INFO skill' bin/factory && pass skill-info || fail skill-info "the per-skill preflight line is not INFO"
out=$(grep -c 'F4 denies' bin/factory); [ "$out" -eq 0 ] && grep -q 'No deny is configured; recorded risk' bin/factory && pass env-note || fail env-note "open_pr still says F4 denies .env, or lacks the recorded-risk note"
out=$(grep -c 'in `loop.sh`' docs/factory/LOOP.md); [ "$out" -eq 0 ] && pass loop-md || fail loop-md "LOOP.md still says loop.sh"
out=$(grep -c 'no deny is configured' docs/factory/ROADMAP.md); [ "$out" -eq 0 ] && grep -q 'no `.env` deny is configured' docs/factory/ROADMAP.md && pass env-one-home || fail env-one-home "ROADMAP still clones the LOOP.md .env sentence"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- the run's PR body has the schema-shaped Codex review section and the `.env` note, its ledger has a worker line with `model: codex`, `cost_usd: null`, and a `usage` object with token counts, and its commits exist on `factory/<n>` (the worktree gitdir question); if the worker could not commit, the run stops `no-change` and that is the finding
- `grep -c '\.env' <run>/round-1.jsonl` and the first such line, pasted into the session file: the shape of a Codex `.env` read, or its absence
- human diff read before merge (Risk high)

## Worker
worker: codex
codex-review: yes
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (Worker calls, Grader calls), the F4 and F17 ledger lines and reviews in .superpowers/factory/sessions/manager-2026-09-11-f11.md, D8 (#41)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS tasks-cleared
PASS skill-info
PASS env-note
PASS loop-md
PASS env-one-home
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## Diff (8305c9a4...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory             | 6 +++---
 docs/factory/LOOP.md    | 2 +-
 docs/factory/ROADMAP.md | 2 +-
 3 files changed, 5 insertions(+), 5 deletions(-)

diff --git a/bin/factory b/bin/factory
index ccfcece..4af935b 100755
--- a/bin/factory
+++ b/bin/factory
@@ -686,7 +686,7 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
   if runs_workflow "$round"; then
     {
       printf '\n\n## Large ticket, round 1: run the fan-out workflow\n\n'
-      printf 'Remove %s/tasks/result.json if it exists, then run the Workflow tool with scriptPath `%s/frozen/factory-round.js` and args `{"ticket": "%s/frozen/issue.md", "run": "%s"}`. ' "$RUN" "$RUN" "$RUN" "$RUN"
+      printf 'Remove `%s/tasks/` if it exists, then run the Workflow tool with scriptPath `%s/frozen/factory-round.js` and args `{"ticket": "%s/frozen/issue.md", "run": "%s"}`. ' "$RUN" "$RUN" "$RUN" "$RUN"
       printf 'When it returns, read %s/tasks/result.json. If that file is absent, implement the ticket yourself as in any round. ' "$RUN"
       printf 'Otherwise the integrator has committed; copy its `unmet` and `abandoned` lists into %s.\n' "$DECISIONS"
     } >> "$pf"
@@ -983,7 +983,7 @@ open_pr() {
     if [ "$WORKER_KIND" = codex ]; then
       printf '\n## Codex worker notes\n\n'
       printf -- '- Cost: the Codex worker rounds carry `cost_usd: null` in the ledger; the dollar caps (ROUND_BUDGET_USD, TICKET_BUDGET_USD, DAILY_BUDGET_USD) do not bound a Codex worker. Only token counts are recorded.\n'
-      printf -- '- `.env`: the workspace-write sandbox does not block a `.env` read (D8, #41); a secret in `.env` is readable by the worker. F4 denies it in Codex config, or it stays a recorded risk.\n'
+      printf -- '- `.env` is readable by the Codex worker (D8, #41). No deny is configured; recorded risk.\n'
     fi
     printf '\n## Backlog\n\n'; jq -r '.backlog[]? | "- " + .' "$RUN/round-$ROUND.judge.json"
     printf '\n## Metrics\n\nrounds: %s, spend: %s usd, wall: %s min, denials: %s\nrun directory: %s\n' \
@@ -1165,7 +1165,7 @@ precondition_lines() { # LOOP.md, Preconditions
   # at build_worker_prompt (skill_file); a bare name and a plugin:name both, newest version first.
   while IFS= read -r t; do
     [ -n "$t" ] || continue
-    skill_file "$t" > /dev/null 2>&1 && echo "  PASS skill $t resolves" || echo "  FAIL skill $t resolves to no SKILL.md"
+    skill_file "$t" > /dev/null 2>&1 && echo "  PASS skill $t resolves" || echo "  INFO skill $t resolves to no SKILL.md (a worker: codex ticket naming it stops)"
   done < "$ROOT/bin/factory.d/skills.txt"
   # Codex login: Codex is not on the bare PATH (#41), so probe it under CODEX_PATH. Only a worker: codex
   # ticket needs it, so a logged-out or absent Codex is INFO here, not FAIL.
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 845cd40..67086bc 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -126,7 +126,7 @@ Its workspace-write sandbox does not block `.env` reads (#41); no deny is config

 Every worker round receives, in this order: the issue body verbatim, which carries its `goal:` line as text, `_common.md`, and from round 2 a `## Previous round` block holding the failing check lines and every blocking finding verbatim.
 A slash command expands only on the first line of a `-p` prompt and swallows the rest as its argument (#40), so no worker prompt carries `/goal` or a `/<skill>` line; a `Stop` hook in `worker-settings.json`, the worker-only settings file, runs the frozen check script from the worktree root and exits 2 with the FAIL lines while any check fails, and `--max-turns` bounds the round (#36, route B).
-The hook sets `LOAM_HOOK=1`, under which the check lines that call `bin/check` (minutes per stop) or the live model pass without running; the supervisor's own check run has it unset and is the one run of those per round. `build_worker_prompt` in `loop.sh` appends after `_common.md` one sentence per `skills:` name: `Before the first edit, call the Skill tool with "<name>".` (#37).
+The hook sets `LOAM_HOOK=1`, under which the check lines that call `bin/check` (minutes per stop) or the live model pass without running; the supervisor's own check run has it unset and is the one run of those per round. `build_worker_prompt` in `bin/factory` appends after `_common.md` one sentence per `skills:` name: `Before the first edit, call the Skill tool with "<name>".` (#37).
 A Codex worker gets the skill bodies pasted instead.
 The worker never runs `bin/factory eval` against the live model; the supervisor's own check run is the one live replay per round.
 `_common.md` is the loop contract, frozen per run; its target text:
diff --git a/docs/factory/ROADMAP.md b/docs/factory/ROADMAP.md
index 0ef4b12..a7fea94 100644
--- a/docs/factory/ROADMAP.md
+++ b/docs/factory/ROADMAP.md
@@ -65,7 +65,7 @@ Merge checklist: bump the plugin version; check the listing weight.

 Goal and why: `worker: codex` and `codex-review: yes` as specified in `LOOP.md`.
 Do not touch: the standing list. Except: `bin/factory`, `bin/factory.d/`.
-Done checks: `codex-review: yes` adds one review section shaped by `review-output.schema.json`; the Codex worker's workspace-write sandbox does not block `.env` reads (#41), and no deny is configured, so the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk; `codex login status` is a preflight line.
+Done checks: `codex-review: yes` adds one review section shaped by `review-output.schema.json`; no `.env` deny is configured (`LOOP.md`, Worker calls); `codex login status` is a preflight line.
 Merge checklist: a hand run of a Track B ticket with `worker: codex` reaches `pr-opened`; Codex token counts appear in the ledger for that run; a fixture `.env` is confirmed absent from the round's JSONL, since the sandbox does not block the read (#41); run directory path in the PR body.

 ## F9 frontier timer
~~~~~~~~~~~~ evidence
