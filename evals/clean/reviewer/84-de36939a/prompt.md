## Ticket

~~~~~~~~~~~~ evidence
Brief:
Make the reviewer's `medium` findings block a round once per ticket, as `high` findings do today, so a real defect the reviewer names is fixed by the worker in the loop instead of by hand at the merge read.
Where: bin/factory (run_review), docs/factory/LOOP.md (Grader-round cap and precedence)
Done means: run_review returns non-zero and queues every high and medium finding verbatim when the reviewer returns at least one of either and has not blocked before on this ticket; a second block never happens; LOOP.md says high or medium.
Out of scope: the Codex review's threshold (critical or high, unchanged); the judge; low findings; the grader-round cap.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
On 2026-09-11 the reviewer returned real `medium` findings on four PRs in a row (#80, #75, #83, and #82's lows aside): a restore guard that did not fire, a leaked export, an unguarded append, an added paragraph outside a "moved, not rewritten" rule. None blocked, because `run_review` counts only `high`, so every one was fixed by hand on the branch before merge.
Samyak's decision (2026-09-11): a medium blocks one round too. The cost is one more worker round on most tickets, about 2 to 4 usd; the gain is that the merge read stops being a repair step.

## Do not touch
The standing list. Except: bin/factory (run_review only), docs/factory/LOOP.md (the Grader-round cap and precedence section only).
Also: bin/factory.d/; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- the Codex review stage and `CODEX_REVIEW_BLOCKED`
- the judge, `verdict_consistent`, and `GRADER_FAIL_ROUNDS`
- `low` findings, which stay in the PR body

## Approach
Executor: `bin/factory run` as merged in F1, with F20 merged.

Facts pinned: `run_review` in `bin/factory` computes `highs` with `select(.severity == "high")`, logs `blocking=$highs`, returns 0 when it is zero, and otherwise blocks once (`REVIEW_BLOCKED`), appending the high findings to `round-<k>.fixes`, which the next worker prompt pastes under "Blocking findings, verbatim"; `docs/factory/LOOP.md` line 89 says the reviewer blocks only on a `high` finding and at most once per ticket; the reviewer schema's severity values include `high`, `medium`, `low`.

Change:
1. `run_review`: count `blocking` as findings whose severity is `high` or `medium`; log it as `blocking=<n> (high or medium)`; block once on that count; queue every high and medium finding verbatim into the fixes file, highs first.
2. `docs/factory/LOOP.md`, Grader-round cap and precedence: the reviewer blocks once on a `high` or `medium` finding; the Codex review keeps `critical` or `high`.

## Done checks
```done-checks
grep -q 'severity == "high" or .severity == "medium"' bin/factory && pass medium-blocks || fail medium-blocks "run_review does not count medium findings as blocking"
out=$(grep -cw 'REVIEW_BLOCKED=1' bin/factory); guard test "$out" -eq 1 && pass block-once || fail block-once "the once-per-ticket guard changed (whole-word count of REVIEW_BLOCKED=1 is $out, not 1)"
grep -q 'high` or `medium` finding' docs/factory/LOOP.md && pass loop-md || fail loop-md "LOOP.md still says the reviewer blocks only on high"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- the next run whose reviewer returns a medium shows one blocked round in its log and the medium fixed in round 2
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (Grader-round cap and precedence), the 2026-09-11 decisions in .superpowers/factory/sessions/manager-2026-09-11-codex.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS medium-blocks
PASS block-once
PASS loop-md
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
F84 implementation was already committed by a prior round (0834e8d, c12a172); verified it against the Approach and did not redo it.
run_review counts blocking as findings whose severity is high or medium, logs `blocking=$blocking (high or medium)`, and blocks once via the existing REVIEW_BLOCKED guard: matches Approach step 1.
Queue keeps highs before mediums with `sort_by(.severity != "high")` (false<true, stable sort); reviewer schema requires .defect and .fix on every finding, so the formatter works for mediums too.
Left the high-only selects outside run_review unchanged: scope is run_review only. Residual (both out of scope, so blocking still works): verdict_consistent (:904) counts only highs, so a reviewer `merge` verdict naming only a medium is not refuted (run_review still blocks on it independently); grader_first_fail (:1205) gives a medium-only block no `review:<file>` label.
docs/factory/LOOP.md line 89 now says the reviewer blocks on a `high` or `medium` finding; Codex review kept at `critical` or `high`: matches Approach step 2.
Ran the done-checks block from the worktree root sourced after lib.sh: 5 PASS, 0 FAIL. No new commit needed; working tree clean.

~~~~~~~~~~~~ evidence

## Diff (f650a30a...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory          | 11 ++++++-----
 docs/factory/LOOP.md |  2 +-
 2 files changed, 7 insertions(+), 6 deletions(-)

diff --git a/bin/factory b/bin/factory
index 0f196bd..1ed5e67 100755
--- a/bin/factory
+++ b/bin/factory
@@ -955,18 +955,19 @@ run_judge() { # round -> 0 on a pass verdict
 }

 run_review() { # round -> 0 when nothing blocks
-  local round="$1" pf="$RUN/round-$1.review.prompt.md" f="$RUN/round-$1.review.json" highs
+  local round="$1" pf="$RUN/round-$1.review.prompt.md" f="$RUN/round-$1.review.json" blocking
   build_evidence "$RUN/frozen/reviewer.md" 6000 > "$pf"
   call_json "$round" review reviewer "$pf" "$RUN/frozen/reviewer.schema.json"
-  highs=$(jq '[.findings[]? | select(.severity == "high")] | length' "$f")
-  log "reviewer verdict: $(jq -r .verdict "$f") findings=$(jq '(.findings // []) | length' "$f") blocking=$highs"
-  [ "$highs" -gt 0 ] || return 0
+  blocking=$(jq '[.findings[]? | select(.severity == "high" or .severity == "medium")] | length' "$f")
+  log "reviewer verdict: $(jq -r .verdict "$f") findings=$(jq '(.findings // []) | length' "$f") blocking=$blocking (high or medium)"
+  [ "$blocking" -gt 0 ] || return 0
   if [ "$REVIEW_BLOCKED" = 1 ]; then
     log "the reviewer already blocked once on this ticket; its findings go to the backlog"
     return 0
   fi
   REVIEW_BLOCKED=1
-  jq -r '[.findings[]? | select(.severity == "high")] | .[]
+  # highs before mediums: sort_by(.severity != "high") keys false (high) before true (medium), and jq's sort is stable.
+  jq -r '[.findings[]? | select(.severity == "high" or .severity == "medium")] | sort_by(.severity != "high") | .[]
     | "- " + (.file // "?") + ":" + ((.line // 0) | tostring) + " " + .defect + " Fix: " + .fix' "$f" >> "$RUN/round-$round.fixes"
   return 1
 }
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 2d3f565..82d54fb 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -86,7 +86,7 @@ Codex token counts come from its `--json` events and land in the ledger with `co

 After the checks first pass, at most two grader-fail rounds per ticket; then the remaining non-blocking findings go to the PR body backlog and the PR opens.
 The judge decides pass or fail.
-The reviewer and the Codex review block only on a `high` finding (Codex: `critical` or `high`), and each may block at most once per ticket.
+The reviewer blocks only on a `high` or `medium` finding, the Codex review only on a `critical` or `high` finding, and each may block at most once per ticket.
 A grader whose output is absent or unparseable is a fail with one high finding "grader unparseable", never a pass.
 `verdict_consistent` runs on every grader JSON: a pass with non-empty fixes, or a fail with empty fixes and empty backlog, is refuted, and the grader is called once more, fresh, with the refutation appended to its prompt.

~~~~~~~~~~~~ evidence
