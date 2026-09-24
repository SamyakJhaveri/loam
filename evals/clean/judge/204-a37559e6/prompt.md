## Ticket

~~~~~~~~~~~~ evidence
Brief:
Point every model the loop calls at claude-opus-5-5: the grader default, the eval default, and the worker's advisor in bin/factory, and the judge and reviewer agent files at effort high; the docs follow.
Where: bin/factory (lines 191 and 381-388), cultivation/marketplace/sam-cc-setup/agents/judge.md, cultivation/marketplace/sam-cc-setup/agents/reviewer.md, cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json, cultivation/marketplace/.claude-plugin/marketplace.json, docs/factory/LOOP.md, docs/factory/ARCHITECTURE.md.
Done means: GRADER_MODEL, EVAL_MODEL, and WORKER_ADVISOR default to claude-opus-5-5 with every FACTORY_* override intact; judge.md and reviewer.md pin claude-opus-5-5 at high; the plugin is 0.9.4; LOOP.md and ARCHITECTURE.md name Opus 5.5 for every loop role and no loop role names Fable.
Out of scope: plan-reviewer.md and lean-critic.md (not loop agents); the worker model and effort (already claude-opus-5-5 at xhigh); ~/.claude/agents.
Blocked by: none

## Goal and why
Samyak, 2026-09-24: every agent and worker in the loop runs Opus 5.5. The worker, its subagents (`CLAUDE_CODE_SUBAGENT_MODEL="$WORKER_MODEL"`), and the workflow builders already do; the advisor (`fable`), the graders (`GRADER_MODEL` default `fable`), and eval replays (`EVAL_MODEL=fable`) do not.
Checks stay independent of the worker in other ways: deterministic done checks written before the code, and graders in a fresh context that never saw the worker's reasoning. F38 measures whether Opus graders miss what Fable graders would catch.

## Do not touch
The standing list. Also: seed/, evals/, cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md, cultivation/marketplace/sam-cc-setup/agents/lean-critic.md, cultivation/marketplace/sam-cc-setup/skills/.
Except: bin/factory (this ticket rewrites its model defaults), cultivation/marketplace/sam-cc-setup/agents/judge.md, cultivation/marketplace/sam-cc-setup/agents/reviewer.md (grader files this ticket edits).

## Out of scope
Any change to the grader rubrics, output schemas, or the grader call's flags other than the model.
Turning the advisor off (trial #185 decides that).
The Codex review stage (`codex-review:` stays a per-ticket choice).

## Approach
1. bin/factory: `GRADER_MODEL="${FACTORY_GRADER_MODEL:-claude-opus-5-5}"`; `WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-claude-opus-5-5}"` (keep the no-colon form so an explicit empty still disables it); line 191 `EVAL_MODEL=claude-opus-5-5`. Update the comments beside them to cite ARCHITECTURE.md, Models and roles (2026-09-24).
2. judge.md and reviewer.md front matter: `model: claude-opus-5-5`, `effort: high`. Descriptions that name Fable say Opus 5.5.
3. plugin.json and marketplace.json: version 0.9.3 becomes 0.9.4.
4. LOOP.md: the grader command example (about line 106) says `--model claude-opus-5-5 --effort high`; the worker command example (about line 120) says `--advisor claude-opus-5-5`; any other sentence that names Fable for a loop role says Opus 5.5.
5. ARCHITECTURE.md: the stage table row 4 Grade and the Models and roles bullets say every loop role (worker, advisor, judge, reviewer, eval replay) is Opus 5.5; the lean-critic (by hand) is Opus 5.5; the plan-reviewer stays Fable 5.1 on a bullet of its own that names no loop role, because it runs outside the loop.
6. Quality bar the judge reads (not a check): no FACTORY_* override loses its meaning; the no-colon advisor default is kept; comments stay one line each.
7. `claude plugin validate cultivation/marketplace/sam-cc-setup` must pass.

## Done checks
```done-checks
out=$(env -u FACTORY_GRADER_MODEL -u FACTORY_WORKER_ADVISOR FACTORY_SOURCED=1 bash -c '. bin/factory >/dev/null 2>&1; echo "$GRADER_MODEL|$WORKER_ADVISOR|$EVAL_MODEL"' 2>/dev/null); [ "$out" = 'claude-opus-5-5|claude-opus-5-5|claude-opus-5-5' ] && pass loop-defaults || fail loop-defaults "sourced defaults are $out; want claude-opus-5-5 for GRADER_MODEL, WORKER_ADVISOR, EVAL_MODEL"
out=$(FACTORY_GRADER_MODEL=claude-x-1 FACTORY_WORKER_ADVISOR= FACTORY_SOURCED=1 bash -c '. bin/factory >/dev/null 2>&1; echo "$GRADER_MODEL|[$WORKER_ADVISOR]"' 2>/dev/null); [ "$out" = 'claude-x-1|[]' ] && grep -q 'FACTORY_GRADER_MODEL:-claude-opus-5-5' bin/factory && pass overrides || fail overrides "FACTORY_GRADER_MODEL or an explicit empty FACTORY_WORKER_ADVISOR no longer wins, or the default is not claude-opus-5-5: $out"
ok=1; for g in judge reviewer; do h=$(sed -n 1,8p "cultivation/marketplace/sam-cc-setup/agents/$g.md"); grep -qx 'model: claude-opus-5-5' <<<"$h" && grep -qx 'effort: high' <<<"$h" || ok=0; done; [ "$ok" = 1 ] && pass grader-files || fail grader-files "judge.md or reviewer.md is not claude-opus-5-5 at effort high"
a=$(jq -r .version cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json); b=$(jq -r '.plugins[] | select(.name=="sam-cc-setup") | .version' cultivation/marketplace/.claude-plugin/marketplace.json); [ "$a" = 0.9.4 ] && [ "$b" = 0.9.4 ] && pass plugin-version || fail plugin-version "plugin.json $a, marketplace.json $b; both must be 0.9.4"
grep -q -- '--model claude-opus-5-5 --effort high' docs/factory/LOOP.md && grep -q -- '--advisor claude-opus-5-5' docs/factory/LOOP.md && ! grep -q -- '--model fable\|--advisor fable' docs/factory/LOOP.md && pass loop-doc || fail loop-doc "LOOP.md command examples still name fable, or do not name claude-opus-5-5 for the grader and advisor"
s=$(awk '/^## Models and roles/{f=1;next} /^## /{f=0} f' docs/factory/ARCHITECTURE.md); r4=$(grep '^| 4 Grade' docs/factory/ARCHITECTURE.md); bad=$(grep -i 'fable' <<<"$s" | grep -iE 'judge|advisor|worker|eval|grader|(^|[^-])reviewer'); grep -qi 'advisor' <<<"$s" && grep -q 'Opus 5.5' <<<"$s" && grep -q 'Opus 5.5' <<<"$r4" && ! grep -qi 'fable' <<<"$r4" && [ -z "$bad" ] && pass architecture || fail architecture "row 4 or a Models and roles line gives a loop role to Fable: $r4 $bad"
guard claude plugin validate cultivation/marketplace/sam-cc-setup >/dev/null 2>&1 && pass plugin-valid || fail plugin-valid "claude plugin validate cultivation/marketplace/sam-cc-setup"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Merge checklist
- On the runner and the Mac, update the plugin to 0.9.4 so the grader cache matches (LOOP.md, Preconditions): `claude plugin marketplace update seed-skills && claude plugin update sam-cc-setup@seed-skills --scope user`, then `claude plugin list` shows 0.9.4.
- On the runner, `FACTORY_STATUS_PROBE=1 bin/factory status` reports the advisor attached as claude-opus-5-5.

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
Samyak 2026-09-24 (all loop agents on Opus 5.5), #186 (both comments), PR #203, docs/factory/ARCHITECTURE.md (Models and roles)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS loop-defaults
PASS overrides
PASS grader-files
PASS plugin-version
PASS loop-doc
PASS architecture
PASS plugin-valid
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- bin/factory: GRADER_MODEL, EVAL_MODEL, WORKER_ADVISOR default to claude-opus-5-5; advisor keeps the no-colon `-` form; each comment cites ARCHITECTURE.md, Models and roles (2026-09-24) on one line.
- bin/factory:804 comment said the advisor was "the Fable check on the split"; now "the second check on the split", since the advisor is no longer Fable.
- judge.md and reviewer.md: model claude-opus-5-5, effort medium -> high (matches GRADER_EFFORT=high); neither description named Fable, so no description changed.
- Plugin 0.9.3 -> 0.9.4 in plugin.json and marketplace.json; git show --stat of e9e402ca, 19146ed7, d236ad16 shows no CHANGELOG or UPGRADING entry per bump; e9e402ca also edited sam-cc-setup/README.md, whose Agents line names no judge or reviewer model, so it stays; no live file pins 0.9.3.
- ARCHITECTURE.md: line 3, row 4 (now Opus 5.5 high), the Models and roles bullets, and the Codex-exception bullet no longer give a loop role to Fable; plan-reviewer is on its own bullet as Fable 5.1, outside the loop.
- ARCHITECTURE.md: rewrote the "claude-opus-5-5 does exploration, retrieval, and implementation only" bullet; it became false once graders and advisor moved to Opus 5.5.
- Kept Fable where no loop role is named: Brief, Design, Tickets rows and the mermaid Brief node, "Brief and design sessions", LOOP.md:77 (literal usage-limit reply text), LOOP.md:158 (skill name fable-prompting), LOOP.md:180 (manager is an interactive session), ROADMAP.md (history).
- Advisor consulted after orientation: baselined bin/check (green), widened the Fable grep, and ran done-checks under bash with the real lib.sh pass/fail/guard; all 8 PASS.
- Checked after the advisor's second call: no live doc outside Where gives a loop role to Fable; EVAL_EFFORT default medium (LOOP.md:13) left alone, since the ticket changes models only.

~~~~~~~~~~~~ evidence

## Diff (0ed32341...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                                                     |  8 ++++----
 cultivation/marketplace/.claude-plugin/marketplace.json         |  2 +-
 cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json |  2 +-
 cultivation/marketplace/sam-cc-setup/agents/judge.md            |  4 ++--
 cultivation/marketplace/sam-cc-setup/agents/reviewer.md         |  4 ++--
 docs/factory/ARCHITECTURE.md                                    | 14 ++++++++------
 docs/factory/LOOP.md                                            |  4 ++--
 7 files changed, 20 insertions(+), 18 deletions(-)

diff --git a/bin/factory b/bin/factory
index bed1e96f..d94ece61 100755
--- a/bin/factory
+++ b/bin/factory
@@ -188,7 +188,7 @@ check_paths() {
 # compares the verdict with expected.json. The rubric comes from the live grader file, so a
 # grader prompt edit changes the result; that is the point (LOOP.md, Grader change protocol).

-EVAL_MODEL=fable
+EVAL_MODEL=claude-opus-5-5   # ARCHITECTURE.md, Models and roles (2026-09-24)
 EVALS_DIR=evals
 GRADERS_DIR=""

@@ -381,9 +381,9 @@ MAX_HOURS MAX_TURNS CALL_TIMEOUT_SEC MAX_PARALLEL"
 MAX_ROUNDS=6; ROUND_BUDGET_USD=15; GRADER_BUDGET_USD=5; TICKET_BUDGET_USD=60
 DAILY_BUDGET_USD=150; MAX_HOURS=8; MAX_TURNS=200; CALL_TIMEOUT_SEC=5400; MAX_PARALLEL=1
 WORKER_MODEL="${FACTORY_WORKER_MODEL:-claude-opus-5-5}"   # ARCHITECTURE.md, Models and roles (2026-09-22)
-GRADER_MODEL="${FACTORY_GRADER_MODEL:-fable}"
+GRADER_MODEL="${FACTORY_GRADER_MODEL:-claude-opus-5-5}"   # ARCHITECTURE.md, Models and roles (2026-09-24)
 CODEX_MODEL="${FACTORY_CODEX_MODEL:-codex}"   # ledger label for a `worker: codex` round; Codex holds the real model in its own config, and its dollar cost is null (F4)
-WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-fable}"   # mid-round advisor on the worker call; FACTORY_WORKER_ADVISOR= (explicit empty) disables the flag. No colon: :- could never disable. The bare name is never read.
+WORKER_ADVISOR="${FACTORY_WORKER_ADVISOR-claude-opus-5-5}"   # mid-round advisor on the worker call (ARCHITECTURE.md, Models and roles, 2026-09-24); FACTORY_WORKER_ADVISOR= (explicit empty) disables the flag. No colon: :- could never disable. The bare name is never read.
 WORKER_EFFORT=xhigh        # the ticket's `effort:` line overrides
 GRADER_EFFORT=high
 GRADER_FAIL_ROUNDS=2      # grader-fail rounds allowed once the checks pass (LOOP.md, Grader-round cap)
@@ -801,7 +801,7 @@ build_worker_prompt() { # round -> prompt path (pending until the call returns a
       | while read -r s; do printf 'Before the first edit, call the Skill tool with "%s".\n' "$s"; done >> "$pf"
   fi
   # A large claude ticket runs round 1 as the fan-out workflow; a Codex worker gets the ordinary round-1
-  # prompt (runs_workflow is false for it). The F11 advisor is the Fable check on the split (F12).
+  # prompt (runs_workflow is false for it). The F11 advisor is the second check on the split (F12).
   if runs_workflow "$round"; then
     {
       printf '\n\n## Large ticket, round 1: run the fan-out workflow\n\n'
diff --git a/cultivation/marketplace/.claude-plugin/marketplace.json b/cultivation/marketplace/.claude-plugin/marketplace.json
index 8f7c28ae..2fd5fa2f 100644
--- a/cultivation/marketplace/.claude-plugin/marketplace.json
+++ b/cultivation/marketplace/.claude-plugin/marketplace.json
@@ -9,7 +9,7 @@
     {
       "name": "sam-cc-setup",
       "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, plan review, technology selection, validation, Codex cross-model review, and bootstrap support",
-      "version": "0.9.3",
+      "version": "0.9.4",
       "source": "./sam-cc-setup",
       "author": {
         "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
index 97e19a53..46fc7a73 100644
--- a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
+++ b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
@@ -1,7 +1,7 @@
 {
   "name": "sam-cc-setup",
   "license": "MIT",
-  "version": "0.9.3",
+  "version": "0.9.4",
   "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, merged plan review, technology selection, validation, cross-model Codex review, and bootstrap support for the rules layer plugins cannot ship.",
   "author": {
     "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/agents/judge.md b/cultivation/marketplace/sam-cc-setup/agents/judge.md
index c4036cba..8b0cf646 100644
--- a/cultivation/marketplace/sam-cc-setup/agents/judge.md
+++ b/cultivation/marketplace/sam-cc-setup/agents/judge.md
@@ -2,8 +2,8 @@
 name: judge
 description: "Fresh-context judge for one factory ticket: scores the rubric rows over the frozen evidence and returns pass or fail with fixes."
 tools: Read, Grep, Glob
-model: claude-fable-5-1
-effort: medium
+model: claude-opus-5-5
+effort: high
 maxTurns: 40
 ---

diff --git a/cultivation/marketplace/sam-cc-setup/agents/reviewer.md b/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
index 4af611e6..9ad83c3a 100644
--- a/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
+++ b/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
@@ -2,8 +2,8 @@
 name: reviewer
 description: "Fresh-context reviewer for one factory ticket: hunts defects in the diff after the judge passes and returns findings with severities."
 tools: Read, Grep, Glob
-model: claude-fable-5-1
-effort: medium
+model: claude-opus-5-5
+effort: high
 maxTurns: 40
 ---

diff --git a/docs/factory/ARCHITECTURE.md b/docs/factory/ARCHITECTURE.md
index d52169ec..45b74322 100644
--- a/docs/factory/ARCHITECTURE.md
+++ b/docs/factory/ARCHITECTURE.md
@@ -1,6 +1,6 @@
 # Loam Factory: architecture

-The factory takes a raw request to a merged pull request through unattended loops and independent Fable graders, on Loam and, after F8, on projects Loam seeds.
+The factory takes a raw request to a merged pull request through unattended loops and independent Opus 5.5 graders, on Loam and, after F8, on projects Loam seeds.
 This file is the one home of the stage table, the single sources of truth, the standing do-not-touch list, the model rules, and the placement table.
 The brief and ticket formats live in `CONTRACT.md`, the supervisor in `LOOP.md`, the build order in `../architecture-working/tickets/README.md` (`ROADMAP.md` is the superseded loop-factory record), the evidence in `../research/INDEX.md`.
 Everything here describes the target; a thing that exists at the time of writing (2026-09-07) says so.
@@ -40,7 +40,7 @@ flowchart LR
 | 1 Design (Track C) | design issue | when the brief is `Mode: figure-out`, `surprise-me` in panel mode and `research` subagents first; then Fable plan mode with Opus Explore subagents; `/plan-review` blind on Fable, whose elegance gate writes two competing designs before a verdict; `grill-with-docs` with `domain-modeling` writes ADRs; `wayfinder` when unknowns remain; lean-critic on the design issue | reacts to the options, answers the grill, approves | design issue body (brief, destination, deliverables, constraints, proof, no implementation detail), ADRs in `docs/adr/`, map if used | review verdict recorded, ADRs committed |
 | 2 Tickets | design issue, or the one Track B ticket | Fable runs `to-tickets`; issue bodies use the ticket contract; `bin/factory lint` (F2); `plan-reviewer` by hand and lean-critic once over the breakdown | approves the breakdown | GitHub issues, native blocking edges, label `ready-for-agent` | lint exit 0, `plan-reviewer` pass |
 | 3 Loop | one ticket | `bin/factory run <issue>` on the runner (F1): round 0, then worker rounds on `claude-opus-5-5` xhigh or `codex exec` | nothing; may run `bin/factory stop`, or edit the issue body and relaunch | branch, commits, a run directory | checks exit 0, clean tree, do-not-touch clean |
-| 4 Grade | diff and evidence | Fable medium judge and reviewer, read-only, fresh, frozen per run; Codex review stage when the ticket sets it | nothing | JSON verdicts, PR with metrics and merge checklist | judge pass and no blocking finding, or the grader-round cap with a backlog |
+| 4 Grade | diff and evidence | Opus 5.5 high judge and reviewer, read-only, fresh, frozen per run; Codex review stage when the ticket sets it | nothing | JSON verdicts, PR with metrics and merge checklist | judge pass and no blocking finding, or the grader-round cap with a backlog |
 | 5 Merge | PR | Samyak with `bin/runner bin/factory status`; `claude ultrareview --json` optional on high risk | ticks the merge checklist, merges | merged main; the PR's `Closes #N` closes the ticket | human merge, never the loop |
 | 6 Learn | `bin/factory status` | the manager session (rule in `LOOP.md`) | nothing | a `CLAUDE.md` line, a lint rule, or nothing | none |

@@ -75,12 +75,14 @@ Scope beyond the ticket goal outside this list is a judge finding, not a stall.

 ## Models and roles

-- Graders are picked by eval, not price (#186, 2026-09-23): judge and reviewer are fresh Fable 5.1 at high in the loop; the lean-critic is Opus 5.5 at high, by hand on the PR; the plan-reviewer is Fable 5.1 at high (F0 sets its frontmatter).
-- `claude-opus-5-5` does exploration, retrieval, and implementation only: loop worker at xhigh, never high, Explore subagents. Replaced claude-opus-4-8[1m] on 2026-09-22.
-- The loop worker carries a Fable 5.1 advisor (`--advisor fable`, F11, 2026-09-10): the worker decides when to consult it; `FACTORY_WORKER_ADVISOR=` (explicit empty) turns it off; each worker ledger line records `advisor_calls` and `advisor_usd`. Kept while the ledger shows lower usd per ticket or fewer and less severe grader findings.
+- Every loop role is `claude-opus-5-5` (Samyak, 2026-09-24): worker, its subagents, advisor, judge, reviewer, and eval replay.
+- Graders are picked by eval, not price (#186, 2026-09-23): judge and reviewer are fresh Opus 5.5 at high in the loop (2026-09-24; F38 measures what the graders miss); the lean-critic is Opus 5.5 at high, by hand on the PR.
+- The plan-reviewer is Fable 5.1 at high, by hand outside the loop (F0 sets its frontmatter).
+- The loop worker is `claude-opus-5-5` at xhigh, never high, with Explore subagents on the same model. Replaced claude-opus-4-8[1m] on 2026-09-22.
+- The loop worker carries an Opus 5.5 advisor (`--advisor claude-opus-5-5`, F11 2026-09-10, Opus 5.5 since 2026-09-24): the worker decides when to consult it; `FACTORY_WORKER_ADVISOR=` (explicit empty) turns it off; each worker ledger line records `advisor_calls` and `advisor_usd`. Kept while the ledger shows lower usd per ticket or fewer and less severe grader findings.
 - Brief and design sessions are Fable 5.1 at high, interactive.
 - Never Sonnet or Haiku; any flag that defaults to Haiku is overridden or unused; every `Agent` call names its model.
-- The one named exception: Codex may be the worker (`worker: codex`) or an added reviewer (`codex-review: yes`); the Fable graders always run.
+- The one named exception: Codex may be the worker (`worker: codex`) or an added reviewer (`codex-review: yes`); the judge and reviewer always run.

 ## Where things live

diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index ae85d6d7..e0d56351 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -103,7 +103,7 @@ The supervisor takes a tree signature (the sha256 of the worktree HEAD and its p
 `--strict-mcp-config` and `--disable-slash-commands` drop the MCP schemas and the skills listing a grader never uses: its prefix is then 9.9k tokens instead of 27k (probed on the runner 2026-09-09), and the prefix is most of a grader call's input.

 ```
-claude -p --model fable --effort high --tools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --no-session-persistence \
+claude -p --model claude-opus-5-5 --effort high --tools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --no-session-persistence \
   --json-schema "$(cat frozen/<grader>.schema.json)" --max-budget-usd "$GRADER_BUDGET_USD" \
   --setting-sources user --settings frozen/role-settings.json --output-format json < frozen/<grader>.prompt.md
 ```
@@ -117,7 +117,7 @@ The Codex review stage runs `codex exec --json --output-schema frozen/review-out
 ## Worker calls

 ```
-claude -p --model claude-opus-5-5 --effort xhigh --advisor fable --permission-mode bypassPermissions --strict-mcp-config \
+claude -p --model claude-opus-5-5 --effort xhigh --advisor claude-opus-5-5 --permission-mode bypassPermissions --strict-mcp-config \
   --setting-sources user --settings frozen/worker-settings.json --max-turns "$MAX_TURNS" \
   --max-budget-usd "$ROUND_BUDGET_USD" --output-format stream-json --verbose --include-hook-events < round-<k>.prompt.md
 ```
~~~~~~~~~~~~ evidence
