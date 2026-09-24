## Ticket

~~~~~~~~~~~~ evidence
Brief:
Move the brief form out of CONTRACT.md into a manual-only /brief skill so a Track B request becomes a ticket in one session.
Where: docs/factory/CONTRACT.md, cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md (new), cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json, cultivation/marketplace/.claude-plugin/marketplace.json, bin/factory.d/fixtures/brief-sample.md (new)
Done means: the skill validates and is manual-only, CONTRACT.md points at it with no second copy of the form, the plugin listing weight does not rise, a brief written through the skill lints clean as a ticket, and the plugin version is bumped.
Out of scope: the ticket grader; any change to the ticket contract sections or lint rules; stage 1 skills.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #F2 (merged as PR #49)

## Goal and why
Move the brief section of `CONTRACT.md` (from `## The brief` up to `## The ticket contract`: the you-may table, the form, the blindspot pass, the tracks by blast radius, the two worked briefs) into `cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md`, manual-only, so Track B publishes a ticket from one session (`ROADMAP.md` F5).
Rewritten 2026-09-10 to run under `bin/factory run` as the first `size: large` ticket whose work spans several files, so the F12 fan-out's Build and Integrate phases run for the first time; its ledger line is the F12 keep-or-cut data point.

## Do not touch
The standing list. Except: cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md, bin/factory.d/fixtures/brief-sample.md (this ticket creates them), cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json and cultivation/marketplace/.claude-plugin/marketplace.json (the version line only), docs/factory/CONTRACT.md (the brief section only).
Also: bin/check and its listing budget; every other skill and agent under cultivation/marketplace/; seed/.

## Out of scope
- the ticket grader
- any change to the ticket contract sections or the lint rules
- stage 1 skills (grill, wayfinder, to-tickets)
- raising `LISTING_BUDGET` in `bin/check`; a manual-only skill is not in the listing and costs nothing (`bin/skill_listing_weight.py`, header comment)

## Approach
Executor: `bin/factory run` as merged in F1, round 1 through the F12 fan-out workflow (`size: large`).

The skill body is the brief section of `CONTRACT.md` moved, not rewritten. Frontmatter carries `name: brief`, a one-line description, and `disable-model-invocation: true`, which keeps it out of the plugin listing (`bin/skill_listing_weight.py`: "A skill with `disable-model-invocation: true` is not in the listing and costs nothing"), so the listing weight stays at 634 tokens. `CONTRACT.md` keeps one line under `## The brief` pointing at the skill and the sentence that the brief becomes the ticket's Goal and why, Done checks, and Out of scope. Write one sample brief through the skill into `bin/factory.d/fixtures/brief-sample.md` in ticket form so lint accepts it (pattern: `bin/factory.d/fixtures/size-large.md`, a minimal contract-form body). Bump the plugin version in both plugin.json and marketplace.json (pattern: the 0.8.3 bump).

The work splits into disjoint files for the fan-out planner: the skill file plus the two version lines; the CONTRACT.md move plus the sample fixture. Each task's check is one line of the block below.

## Done checks
```done-checks
f=cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md; [ -f "$f" ] && claude plugin validate --strict cultivation/marketplace/sam-cc-setup >/dev/null 2>&1 && pass skill-validates || fail skill-validates "skill missing or validate --strict failed"
grep -q 'disable-model-invocation: true' cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md 2>/dev/null && pass manual-only || fail manual-only "skill is model-invocable or missing"
grep -q 'skills/brief/SKILL.md' docs/factory/CONTRACT.md && ! grep -q '^Done means: <' docs/factory/CONTRACT.md && pass one-home || fail one-home "CONTRACT.md lacks the pointer or still holds the form"
grep -q 'If you catch yourself improving the idea' cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md 2>/dev/null && pass form-moved || fail form-moved "the skill does not carry the brief rule"
guard [ "$(python3 bin/skill_listing_weight.py --json | jq '."sam-cc-setup".listing_tokens')" -le 634 ] && pass listing-weight || fail listing-weight "sam-cc-setup listing above 634 tokens; the skill is not manual-only"
bin/factory lint bin/factory.d/fixtures/brief-sample.md >/dev/null 2>&1 && pass brief-lints || fail brief-lints "sample brief rejected by lint or missing"
v=$(jq -r .version cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json); [ "$v" != "0.8.3" ] && grep -q "\"version\": \"$v\"" cultivation/marketplace/.claude-plugin/marketplace.json && pass version-bumped || fail version-bumped "plugin version not bumped in both files"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- read the round-1 ledger line: workflow_agents, workflow_usd, wall clock, rounds, unmet and abandoned tasks, against F4's solo round (12.18 usd, 36 min); this is the F12 keep-or-cut data point
- human diff read before merge (Risk high), then `bin/runner 'claude plugin update sam-cc-setup@seed-skills'` on the runner and the same on the Mac

## Worker
worker: claude
codex-review: no
effort: xhigh
size: large
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 80 turns

## Decisions
docs/factory/CONTRACT.md, docs/factory/ROADMAP.md, the F12 ticket (#66) and its ledger line in .superpowers/factory/sessions/manager-2026-09-11-f11.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS skill-validates
PASS manual-only
PASS one-home
PASS form-moved
PASS listing-weight
PASS brief-lints
PASS version-bumped
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Ran the F12 fan-out Workflow as prescribed (frozen/factory-round.js): planner split into 2 disjoint tasks, 2 builders, 1 integrator; 4 agents, 0 errors, ~395s, 182612 subagent tokens.
Integrator result.json: unmet: [] abandoned: []; its captured checks and my own re-run of frozen/checks.sh (LOAM_HOOK unset) both print all 8 PASS, no FAIL.
Reverted CONTRACT.md line 3 to its original ("one home of the brief form and the ticket contract"): the builder's rewrite was outside the "brief section only" scope (above `## The brief`); the line is now stale after the move and is flagged for the Risk-high human diff read as a one-line follow-up.
Added the bridge sentence "The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over." under `## The brief`: the Approach names it explicitly and the builder had dropped it; kept verbatim so the move is not a rewrite.
Removed the `Co-Authored-By: Claude Opus 4.8` trailer both builders added to their commits (worker prompt forbids the trailer); squashed the two commits plus my edits into one trailerless commit naming both tasks; git diff --stat base..HEAD unchanged bar the two CONTRACT.md lines.

~~~~~~~~~~~~ evidence

## Diff (8305c9a4...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory.d/fixtures/brief-sample.md                          | 35 +++++++++++++++++++++++++++++++++++
 cultivation/marketplace/.claude-plugin/marketplace.json         |  2 +-
 cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json |  2 +-
 cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md      | 84 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 docs/factory/CONTRACT.md                                        | 72 ++----------------------------------------------------------------------
 5 files changed, 123 insertions(+), 72 deletions(-)

diff --git a/bin/factory.d/fixtures/brief-sample.md b/bin/factory.d/fixtures/brief-sample.md
new file mode 100644
index 0000000..80aed22
--- /dev/null
+++ b/bin/factory.d/fixtures/brief-sample.md
@@ -0,0 +1,35 @@
+# Sample: publish a Track B ticket from one session
+Brief:
+Add a `bin/factory publish` subcommand that turns a linted ticket file into a GitHub issue.
+Where: bin/factory (a new publish subcommand), docs/factory/CONTRACT.md (the Seam with to-tickets section).
+Done means: bin/factory publish FILE opens an issue whose body is the file, and bin/factory lint still accepts every committed fixture.
+Out of scope: editing an issue after it is opened; any change to the loop, the grader, or to-tickets.
+Track: B    Risk: high    Mode: build    Open question: none
+Blocked by: none
+
+## Goal and why
+A Track B brief should reach GitHub without a second tool.
+Today the author copies the linted body into the web UI by hand; a `publish` subcommand closes stage 2 in one session (ROADMAP.md F5).
+
+## Do not touch
+The standing list. Except: bin/factory (this ticket adds the publish subcommand).
+
+## Out of scope
+Editing an issue after it is opened; any change to the loop, the grader, or to-tickets.
+
+## Done checks
+```done-checks
+guard bash -n bin/factory && pass syntax || fail syntax "bin/factory does not parse"
+out=$(bin/factory 2>&1); grep -q 'publish' <<<"$out" && pass advertised || fail advertised "the usage banner does not name publish"
+out=$(bin/factory publish --help 2>&1); grep -q 'issue' <<<"$out" && pass documented || fail documented "publish --help does not mention the issue it opens"
+guard bin/factory lint bin/factory.d/fixtures/S1.md >/dev/null && pass lint-still-green || fail lint-still-green "lint regressed on a known-good fixture"
+```
+
+## Worker
+worker: claude
+codex-review: yes
+effort: medium
+goal: the done-checks block prints no FAIL line, or stop after 60 turns
+
+## Decisions
+docs/factory/CONTRACT.md, docs/factory/ROADMAP.md
diff --git a/cultivation/marketplace/.claude-plugin/marketplace.json b/cultivation/marketplace/.claude-plugin/marketplace.json
index dffaf80..3702122 100644
--- a/cultivation/marketplace/.claude-plugin/marketplace.json
+++ b/cultivation/marketplace/.claude-plugin/marketplace.json
@@ -9,7 +9,7 @@
     {
       "name": "sam-cc-setup",
       "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, plan review, technology selection, validation, Codex cross-model review, and bootstrap support",
-      "version": "0.8.3",
+      "version": "0.9.0",
       "source": "./sam-cc-setup",
       "author": {
         "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
index b6443df..73e128c 100644
--- a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
+++ b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
@@ -1,7 +1,7 @@
 {
   "name": "sam-cc-setup",
   "license": "MIT",
-  "version": "0.8.3",
+  "version": "0.9.0",
   "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, merged plan review, technology selection, validation, cross-model Codex review, and bootstrap support for the rules layer plugins cannot ship.",
   "author": {
     "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md b/cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md
new file mode 100644
index 0000000..c6f5629
--- /dev/null
+++ b/cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md
@@ -0,0 +1,84 @@
+---
+name: brief
+disable-model-invocation: true
+description: "Turn a raw request (often a transcribed voice note) into a brief: four lines and three fields, echoed back for correction, then handed to the ticket contract for a Track B ticket. Use when you type /brief or start a ticket from a request. Manual only. NOT for writing the ticket body itself (docs/factory/CONTRACT.md) or breaking a large request into several tickets (Track C)."
+argument-hint: "[the raw request, often a transcribed voice note]"
+---
+
+# brief
+
+**Trigger:** user types `/brief [raw request]`. Manual-only (`disable-model-invocation: true`).
+`$ARGUMENTS` is the raw request. If it is empty, ask for the request; never guess it.
+
+You turn a raw request, often a transcribed voice note, into four lines and three fields, then echo them back for correction.
+If you catch yourself improving the idea rather than the sentence, stop.
+
+| You may | You may not |
+|---|---|
+| carry every constraint forward, verbatim | quietly drop a requirement because it looks hard or odd |
+| fix grammar, cut rambling, order the steps | soften a strong ask ("rewrite" into "refactor a bit") |
+| name the files you verified exist | invent files, numbers, or done conditions |
+| ask one question when two readings produce different work | ask a second question, or ask one the codebase can answer |
+
+The form:
+
+```
+<the ask, one imperative sentence, their words where they were specific>
+Where: <files or dirs verified to exist>
+Done means: <observable result: a passing command, a rendered element, a merged PR>
+Out of scope: <what you were tempted to add, named so nobody adds it>
+Track: A | B | C    Risk: low | high    Mode: build | figure-out    Open question: <at most one>
+```
+
+Before echoing, diff your draft against the request: every specific thing they said still there, anything in your draft they did not say deleted.
+Do not address the harness in the brief; retry counts, models, and reviewers are configuration.
+
+## Finding the open question
+
+Run a blindspot pass: what in this request depends on a fact you have not read; what would a second engineer read differently; which named file, command, or number have you not verified; what does "done" look like to them that a command cannot see.
+Keep the one question whose two answers produce different work.
+Drop the rest or answer them from the codebase.
+
+## When the solution is not known
+
+`Mode: figure-out` is set when the ask is a question, names no solution, or says "help me figure out".
+It is always Track C.
+Stage 1 then opens with `surprise-me` in panel mode and `research` subagents against primary sources before any plan is written; the actors and order are in the `docs/factory/ARCHITECTURE.md` stage table.
+The design issue records the options considered, the evidence for each, and the ones rejected with a reason.
+
+## Tracks, by blast radius
+
+- Track A touches none of `seed/**`, `.claude/**`, `bin/factory*`, plugin `agents/**`, trust roots, keychains, or release files.
+  It is done in the same session with `bin/check`, one in-session lean-critic pass, and the branch policy in `AGENTS.md` rule 1.
+  The commit or PR body is the spec.
+- Track B is one feature that fits one ticket.
+  The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over.
+  The author runs the block on `main` by hand once and confirms every non-guard check prints FAIL; lint never runs it; round 0 repeats it on the runner.
+  Then lint, then publish.
+- Track C is several tickets.
+  The brief becomes the top section of a design issue; stage 1 follows, then `to-tickets`.
+
+Risk high means anything Track A excludes, plus outward-facing behavior.
+It sets `codex-review: yes` on every ticket once F4 ships the stage, and asks for a human diff read before merge; until F4, `codex-review: no` is valid on a high-risk ticket and the diff read carries the weight.
+
+For a Track B brief, hand these lines to the ticket contract (`docs/factory/CONTRACT.md`, `## The ticket contract`) and publish the issue from this same session; the mapping above (ask to Goal and why, Done means to the done-checks block, Out of scope carried over) is the template, and the sections there are written before implementation.
+
+## Worked brief, Track A
+
+```
+Remove the stale loam-s3 worktree registered at ~/Desktop/loam-s3.
+Where: git worktree list shows it on branch lean/s3; PR #29 merged that branch.
+Done means: git worktree list no longer shows loam-s3 and git status is clean.
+Out of scope: pruning any other worktree; deleting the lean/s3 remote branch.
+Track: A    Risk: low    Mode: build    Open question: none
+```
+
+## Worked brief, Track B
+
+```
+Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
+Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
+Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
+Out of scope: running any check command; bin/factory run.
+Track: B    Risk: high    Mode: build    Open question: none
+```
diff --git a/docs/factory/CONTRACT.md b/docs/factory/CONTRACT.md
index 8aeca39..c5c62c7 100644
--- a/docs/factory/CONTRACT.md
+++ b/docs/factory/CONTRACT.md
@@ -5,76 +5,8 @@ The stage table and model rules live in `ARCHITECTURE.md`; the supervisor that c

 ## The brief

-You turn a raw request, often a transcribed voice note, into four lines and three fields, then echo them back for correction.
-If you catch yourself improving the idea rather than the sentence, stop.
-
-| You may | You may not |
-|---|---|
-| carry every constraint forward, verbatim | quietly drop a requirement because it looks hard or odd |
-| fix grammar, cut rambling, order the steps | soften a strong ask ("rewrite" into "refactor a bit") |
-| name the files you verified exist | invent files, numbers, or done conditions |
-| ask one question when two readings produce different work | ask a second question, or ask one the codebase can answer |
-
-The form:
-
-```
-<the ask, one imperative sentence, their words where they were specific>
-Where: <files or dirs verified to exist>
-Done means: <observable result: a passing command, a rendered element, a merged PR>
-Out of scope: <what you were tempted to add, named so nobody adds it>
-Track: A | B | C    Risk: low | high    Mode: build | figure-out    Open question: <at most one>
-```
-
-Before echoing, diff your draft against the request: every specific thing they said still there, anything in your draft they did not say deleted.
-Do not address the harness in the brief; retry counts, models, and reviewers are configuration.
-
-### Finding the open question
-
-Run a blindspot pass: what in this request depends on a fact you have not read; what would a second engineer read differently; which named file, command, or number have you not verified; what does "done" look like to them that a command cannot see.
-Keep the one question whose two answers produce different work.
-Drop the rest or answer them from the codebase.
-
-### When the solution is not known
-
-`Mode: figure-out` is set when the ask is a question, names no solution, or says "help me figure out".
-It is always Track C.
-Stage 1 then opens with `surprise-me` in panel mode and `research` subagents against primary sources before any plan is written; the actors and order are in the `ARCHITECTURE.md` stage table.
-The design issue records the options considered, the evidence for each, and the ones rejected with a reason.
-
-### Tracks, by blast radius
-
-- Track A touches none of `seed/**`, `.claude/**`, `bin/factory*`, plugin `agents/**`, trust roots, keychains, or release files.
-  It is done in the same session with `bin/check`, one in-session lean-critic pass, and the branch policy in `AGENTS.md` rule 1.
-  The commit or PR body is the spec.
-- Track B is one feature that fits one ticket.
-  The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over.
-  The author runs the block on `main` by hand once and confirms every non-guard check prints FAIL; lint never runs it; round 0 repeats it on the runner.
-  Then lint, then publish.
-- Track C is several tickets.
-  The brief becomes the top section of a design issue; stage 1 follows, then `to-tickets`.
-
-Risk high means anything Track A excludes, plus outward-facing behavior.
-It sets `codex-review: yes` on every ticket once F4 ships the stage, and asks for a human diff read before merge; until F4, `codex-review: no` is valid on a high-risk ticket and the diff read carries the weight.
-
-### Worked brief, Track A
-
-```
-Remove the stale loam-s3 worktree registered at ~/Desktop/loam-s3.
-Where: git worktree list shows it on branch lean/s3; PR #29 merged that branch.
-Done means: git worktree list no longer shows loam-s3 and git status is clean.
-Out of scope: pruning any other worktree; deleting the lean/s3 remote branch.
-Track: A    Risk: low    Mode: build    Open question: none
-```
-
-### Worked brief, Track B
-
-```
-Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
-Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
-Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
-Out of scope: running any check command; bin/factory run.
-Track: B    Risk: high    Mode: build    Open question: none
-```
+The brief form - stage 0 - lives in `cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md`, invoked by hand: the you-may table, the four-line form, the blindspot pass, the tracks by blast radius, and the two worked briefs.
+The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over.

 ## The ticket contract

~~~~~~~~~~~~ evidence
