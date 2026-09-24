## Ticket

~~~~~~~~~~~~ evidence
Brief:
Add the advisor doc's second trigger to the worker contract: consult the advisor when the same done check still fails after two fix attempts, before a third, so a worker stops burning turns on a check it cannot meet; and correct the fan-out script header that says the plan is Fable-checked.
Where: bin/factory.d/_common.md (the consult sentence), bin/factory.d/factory-round.js (the header comment, lines 1 to 4)
Done means: the consult sentence in `_common.md` names the recurring-failure trigger with the two-attempt threshold, and the `factory-round.js` header says the plan runs on the worker model and names firstOverlap as the only check on the split.
Out of scope: the advisor doc's third trigger (consult before declaring done), rejected 2026-09-11 on cost; any change to `bin/factory`; any grader prompt.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: none

## Goal and why
The Claude Code advisor doc names three moments to consult: before committing to an approach, when stuck on a recurring error, and before declaring a task complete. `_common.md` names only the first (the 2026-09-11 re-read, `.superpowers/factory/research-2026-09-11/pages.md`).
The cost of the missing second trigger showed on 2026-09-11: the first F21 launch (#84, run `runs/84/dfef43c5`) spent 31 turns and 4.25 usd on a `block-once` check that could never pass (a substring count), with the advisor consulted twice on other questions and never on the failing check. A consult after the second failed attempt would have asked whether the check can be met at all, which is the question the advisor answers well and the worker does not ask itself.
The third trigger is rejected: it adds one advisor call (about 0.7 to 1.0 usd) to every round, and 12 of the 16 judge verdicts on the runner to date were `pass`, so the expected saving is smaller than the added cost (keep-or-cut, 2026-09-10).
The header of `factory-round.js` says "one Fable-checked plan"; the planner runs on the worker model pinned by `CLAUDE_CODE_SUBAGENT_MODEL`, and nothing consults the advisor about the split, which is built inside the Workflow call and committed by the integrator before control returns to the worker. The only check on the split is `firstOverlap`. The comment is corrected in the same ticket because both files describe the same worker round; the F12 intent sentence in `bin/factory` ("the worker's Fable advisor checks the split") stays as written and the F12 audit reconciles the two.

## Do not touch
The standing list. Except: bin/factory.d/_common.md (the consult sentence only), bin/factory.d/factory-round.js (the header comment lines 1 to 4 only).
Also: bin/factory; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- a consult before declaring the round done (rejected on cost, above)
- any code change to `bin/factory` or to the workflow's prompts and functions
- the grader prompts

## Approach
Executor: `bin/factory run` as merged in F1, with F21 merged.

Facts pinned: `_common.md` line 4 reads "Consult it before you commit to a decision that is expensive to reverse: a file layout, a public interface, a check you cannot make fail, a scope cut. Do routine implementation yourself. When you consult, act on the guidance and record in <decisions> what you changed."; the file is frozen per run and `<decisions>` is substituted by `freeze`; `factory-round.js` lines 1 to 4 are a comment and its `PLAN_PROMPT` agent carries no model option, so the planner is the worker model.

Change:
1. `_common.md`, after "a scope cut.": add the sentence "When the same check still fails after two of your fix attempts, consult it before a third and ask whether the check can be met at all." Keep every other sentence byte for byte.
2. `factory-round.js` header: replace "one Fable-checked plan" with "one plan on the worker model (the only check on the split is firstOverlap)" and keep the rest of the comment; rewrap lines 2 to 3 if needed.

## Done checks
```done-checks
grep -qF 'a scope cut. When the same check still fails after two of your fix attempts, consult it before a third and ask whether the check can be met at all. Do routine implementation yourself.' bin/factory.d/_common.md && [ "$(grep -cF '' bin/factory.d/_common.md)" -eq 11 ] && pass consult-trigger || fail consult-trigger "_common.md lacks the recurring-failure consult sentence spliced after 'a scope cut.', or lost its 11-line shape"
! grep -q 'Fable-checked' bin/factory.d/factory-round.js && grep -q 'plan on the worker model' bin/factory.d/factory-round.js && pass header-fixed || fail header-fixed "the factory-round.js header still says the plan is Fable-checked"
guard node --input-type=module --check < bin/factory.d/factory-round.js && pass script || fail script "node --check bin/factory.d/factory-round.js"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- the next run whose worker fails a check twice shows an advisor call after the second attempt: on the runner, `jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="server_tool_use" and .name=="advisor")' round-<k>.jsonl` beside the Stop-hook FAIL events from the same file (the hook-event field names are confirmed against a real stream on first use)
- human diff read before merge (Risk medium)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 30 turns

## Decisions
header wording states the mechanism, not the F12 intent sentence in bin/factory; reconcile in the F12 audit. .superpowers/factory/research-2026-09-11/pages.md (take 1), the F21 first-launch record in .superpowers/factory/sessions/manager-2026-09-11-codex.md, docs/research/advisor-and-managed-agents.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS consult-trigger
PASS header-fixed
PASS script
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Followed the Approach exactly; both edits are byte-precise and no scope cut was needed, so no advisor consult was required before implementing.
_common.md: spliced the recurring-failure consult sentence after "a scope cut."; file kept its 11-line shape (edited within line 4, no new line).
factory-round.js header: replaced "one Fable-checked plan" with "one plan on the worker model (the only check on the split is firstOverlap)"; rewrapped the header comment from 4 to 5 lines to fit, touching only the header comment; confirmed firstOverlap is the real split check (defined line 60, used at 177/188).
Done-checks: all 4 pass (consult-trigger, header-fixed, script, check-green), 0 fail; LOAM_HOOK unset so bin/check actually ran and passed.
Commit message: dropped an invented "F89:" prefix (F<n> is a plan-feature number, no F89 exists) for the repo convention "<desc> (#89)"; issue numbers go in parens per recent commits.

~~~~~~~~~~~~ evidence

## Diff (16f4ea51...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory.d/_common.md       | 2 +-
 bin/factory.d/factory-round.js | 7 ++++---
 2 files changed, 5 insertions(+), 4 deletions(-)

diff --git a/bin/factory.d/_common.md b/bin/factory.d/_common.md
index 76e4c34..f3fde75 100644
--- a/bin/factory.d/_common.md
+++ b/bin/factory.d/_common.md
@@ -1,7 +1,7 @@
 You are one round of an unattended loop on ticket #<issue>. There is no human. Decide, and record each decision in <decisions> in one line.
 Start by opening every path named under Where, Do not touch, and Approach with git ls-files; never guess a path or a name.
 Follow the Approach section where the ticket has one; if you depart from it, say why in <decisions>.
-If an advisor tool is available, it is a more capable model that reads your conversation so far and sends back guidance. Consult it before you commit to a decision that is expensive to reverse: a file layout, a public interface, a check you cannot make fail, a scope cut. Do routine implementation yourself. When you consult, act on the guidance and record in <decisions> what you changed.
+If an advisor tool is available, it is a more capable model that reads your conversation so far and sends back guidance. Consult it before you commit to a decision that is expensive to reverse: a file layout, a public interface, a check you cannot make fail, a scope cut. When the same check still fails after two of your fix attempts, consult it before a third and ask whether the check can be met at all. Do routine implementation yourself. When you consult, act on the guidance and record in <decisions> what you changed.
 Implement the Goal. Touch nothing listed under Do not touch. Add nothing listed under Out of scope.
 Before you finish, run the done-checks block from the worktree root exactly as the supervisor will, and fix every FAIL line you can; repeat until it prints no FAIL line or you cannot proceed. The supervisor reruns it; a claim without a PASS line is worth nothing.
 Commit as you go with messages that name the step. Never push, never open a PR, never touch GitHub.
diff --git a/bin/factory.d/factory-round.js b/bin/factory.d/factory-round.js
index 83bfd08..092b608 100644
--- a/bin/factory.d/factory-round.js
+++ b/bin/factory.d/factory-round.js
@@ -1,7 +1,8 @@
 // factory-round.js - the F12 fan-out workflow for one `size: large` ticket's round 1:
-// one Fable-checked plan, two to four Opus builders on disjoint files, one Opus
-// integrator that reruns every check and commits. Run by the worker via the Workflow
-// tool; every agent is pinned to the worker model by CLAUDE_CODE_SUBAGENT_MODEL.
+// one plan on the worker model (the only check on the split is firstOverlap), two to
+// four Opus builders on disjoint files, one Opus integrator that reruns every check and
+// commits. Run by the worker via the Workflow tool; every agent is pinned to the worker
+// model by CLAUDE_CODE_SUBAGENT_MODEL.
 //
 // globsOverlap and normalizeOwnsGlob below are ported from Leonxlnx/unlazy
 // (scripts/lib/gates.mjs), MIT License, Copyright (c) 2026 Leonxlnx. One edit: node's
~~~~~~~~~~~~ evidence
