## Ticket

~~~~~~~~~~~~ evidence
Brief:
Open the PR as a draft when a run reaches the grader-round cap with a failing judge, say so on the PR body's first lines, and print the ticket's Goal and why under `## Goal` instead of the /goal line.
Where: bin/factory, docs/factory/LOOP.md.
Done means: the cap path calls `open_pr draft`; open_pr passes `--draft` to `gh pr create` only then and writes a warning line naming the failing judge rows; `## Goal` carries the Goal and why section.
Out of scope: converting an existing PR to a draft; the Mac and runner autoflow scripts; the judge rubric; the honest-row labeling (#177).
Blocked by: #195

## Goal and why
Five runs reached the grader-round cap and opened a normal PR (bin/factory:1241); four merged, three of them with the judge's `honest` row still failing, the last (#182, PR #191) merged on 2026-09-22 by the unattended autoflow loop with no human read.
The judge is the merge gate by Samyak's 2026-09-22 choice; GitHub refuses to merge a draft, so a draft PR stops any automatic merge at the cap without a new gate in the scripts.
The PR body's `## Goal` today prints the Worker `goal:` line ("the done-checks block prints no FAIL line..."), which is the same on every ticket and tells a reader nothing (bin/factory:1147).

## Do not touch
The standing list. Also: bin/check, bin/factory.d/, seed/, docs/factory/CONTRACT.md, cultivation/marketplace/.
Except: bin/factory, docs/factory/LOOP.md (this ticket edits them).

## Out of scope
Converting an already-open PR to a draft on a relaunch (the REST path at bin/factory:1180 stays as is).
Any change to loam-merge, loam-autoflow, or loam-autoflow-mac.
The judge and reviewer prompts and verdict rules.
Labeling worker-run verification in decisions.md (#177).

## Approach
1. `open_pr` takes an optional first argument `draft`. The grader-cap line at bin/factory:1241 calls `open_pr draft`; the pass path at 1238 stays `open_pr`.
2. When `draft` is set, the body starts, after `Closes #N`, with one line: `Draft: opened at the grader-round cap; the judge failed <rows>. Read the Judge section before marking it ready.`, where <rows> are the row names whose value is `fail` in `$RUN/round-$ROUND.judge.json` (jq over `.rows`), comma-separated.
3. When `draft` is set, the `gh pr create` call adds `--draft`.
4. `## Goal` prints `section "Goal and why"` instead of the Worker goal line.
5. docs/factory/LOOP.md: step 8 (about line 58) and the pr-opened row (about line 65) say a PR opened at the grader-round cap is a draft.
6. Commit before the checks run.

## Done checks
```done-checks
cap=$(grep 'grader-round cap:' bin/factory); grep -q 'open_pr draft' <<<"$cap" && pass cap-calls-draft || fail cap-calls-draft "the grader-round cap path does not call open_pr draft"
fn=$(sed -n '/^open_pr()/,/^}/p' bin/factory); grep -q -- '--draft' <<<"$fn" && pass create-draft || fail create-draft "open_pr never passes --draft to gh pr create"
fn=$(sed -n '/^open_pr()/,/^}/p' bin/factory); grep -q 'Draft: opened at the grader-round cap' <<<"$fn" && pass draft-line || fail draft-line "open_pr writes no draft warning line"
fn=$(sed -n '/^open_pr()/,/^}/p' bin/factory); grep -q 'section "Goal and why"' <<<"$fn" && ! grep -qF "sed -n 's/^goal: //p'" <<<"$fn" && pass goal-section || fail goal-section "## Goal still prints the Worker goal line"
grep -qi 'draft' docs/factory/LOOP.md && pass loop-doc || fail loop-doc "LOOP.md does not say a PR at the grader-round cap is a draft"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/LOOP.md (Grader-round cap and precedence), #177, PR #191

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS cap-calls-draft
PASS create-draft
PASS draft-line
PASS goal-section
PASS loop-doc
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Failing rows come from jq over `.rows` as `name: "fail"` entries (the object shape seen in past round-*.judge.json), joined with ", ".
- `## Goal` strips leading blank lines of the section (sed '/./,$!d') so the body has no double gap; otherwise the section is printed verbatim.
- LOOP.md: also said "opens as a draft" in Grader-round cap and precedence (line 92) and noted an already-open PR is updated, not converted (out of scope per the ticket).
- Advisor consult: the cap also fires when the judge passes and the reviewer or Codex review blocks (graders() fails on any), so the draft line's <rows> falls back to "no row; a reviewer or Codex finding blocked" when no row is `fail`.
- `## Goal and why` is a required ticket section (docs/factory/CONTRACT.md:19), so `## Goal` needs no fallback for a missing section.
- Round 2: the draft line reads the judge rows into a variable with jq stderr silenced and falls back to "no row; the judge output was absent or not parseable" when jq prints nothing (absent, empty, or invalid judge file), per the round-1 reviewer finding; `|| printf` alone would miss an empty file, where jq exits 0 with no output.

~~~~~~~~~~~~ evidence

## Diff (442c1e21...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory          | 15 ++++++++++-----
 docs/factory/LOOP.md |  7 ++++---
 2 files changed, 14 insertions(+), 8 deletions(-)

diff --git a/bin/factory b/bin/factory
index 88e0c8c6..b12aa761 100755
--- a/bin/factory
+++ b/bin/factory
@@ -1139,12 +1139,17 @@ file_backlog() { # judge.json issue pr-url
   done
 }

-open_pr() {
-  local body="$RUN/pr-body.md" base url num title
+open_pr() { # [draft]: opened at the grader-round cap
+  local draft="${1:-}" body="$RUN/pr-body.md" base url num title rows
   base=$(cat "$RUN/base.sha")
   {
     [ "$IS_FILE" = 1 ] || printf 'Closes #%s\n\n' "$ISSUE"
-    printf '## Goal\n\n%s\n\n' "$(section Worker | sed -n 's/^goal: //p' | head -1)"
+    if [ -n "$draft" ]; then
+      # An absent, empty, or invalid judge file counts as a fail (LOOP.md), so jq may print nothing.
+      rows=$(jq -r '[(.rows // {}) | to_entries[] | select(.value == "fail") | .key] | join(", ") | if . == "" then "no row; a reviewer or Codex finding blocked" else . end' "$RUN/round-$ROUND.judge.json" 2> /dev/null)
+      printf 'Draft: opened at the grader-round cap; the judge failed %s. Read the Judge section before marking it ready.\n\n' "${rows:-no row; the judge output was absent or not parseable}"
+    fi
+    printf '## Goal\n\n%s\n\n' "$(section "Goal and why" | sed '/./,$!d')"
     printf '## Commits\n\n```\n%s\n```\n\n' "$(git -C "$WORKTREE" log --oneline "$base..HEAD")"
     [ -s "$RUN/round-$ROUND.measure" ] && { printf '## Rows measured\n\n```\n'; cat "$RUN/round-$ROUND.measure"; printf '```\n\n'; }
     printf '## Merge checklist\n\n'; section "Merge checklist" | grep '^- ' | sed 's/^- /- [ ] /'; printf '\n'
@@ -1181,7 +1186,7 @@ open_pr() {
     url="https://github.com/$REPO/pull/$num"
   else
     title=$(grep -m1 '^# ' "$RUN/frozen/issue.md" | sed 's/^# //')
-    url=$(gh pr create -R "$REPO" --head "$BRANCH" --base main --title "${title:-$KEY}" --body-file "$body" 2>&1) \
+    url=$(gh pr create -R "$REPO" --head "$BRANCH" --base main --title "${title:-$KEY}" --body-file "$body" ${draft:+--draft} 2>&1) \
       || finish stopped-environment "gh pr create for $BRANCH failed: $url"
     url=$(printf '%s\n' "$url" | tail -1)
   fi
@@ -1238,7 +1243,7 @@ main_loop() {
     graders "$ROUND" && open_pr
     grader_fails=$((grader_fails + 1))
     [ "$grader_fails" -lt "$GRADER_FAIL_ROUNDS" ] \
-      || { log "grader-round cap: $GRADER_FAIL_ROUNDS grader-fail rounds; the rest goes to the PR backlog"; open_pr; }
+      || { log "grader-round cap: $GRADER_FAIL_ROUNDS grader-fail rounds; the rest goes to the PR backlog"; open_pr draft; }
   done
 }

diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 2e09d259..745f29f5 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -55,14 +55,15 @@ The run resolves them from the installed plugin cache, falling back to the check
    Every round is a fresh process for either worker; there is no fixer role.
 6. Before grading, in order: scan `decisions.md` for an `ABANDON` line; re-hash the frozen set (a mismatch exits `stopped-environment`); `git status --porcelain` must be empty, else the round fails with the path list; `git diff --name-only "$(cat base.sha)"...HEAD` against Do not touch emits `FAIL do-not-touch <paths>`; then run the done-checks block from the worktree root.
 7. On green: the supervisor runs Rows measured and prints `MEASURE` lines, then calls the judge, the reviewer, and the Codex review stage if the ticket sets it, each fresh, on the frozen prompt and the same evidence bundle.
-8. On pass, or at the grader-round cap: assemble the PR body (first line `Closes #<issue>`, then goal, `git log --oneline base..HEAD`, the MEASURE table, the merge checklist as checkboxes, `decisions.md`, grader sections, backlog, metrics), push, `gh pr create` or update the existing PR through the REST API, notify, exit `pr-opened`.
+8. On pass, or at the grader-round cap: assemble the PR body (first line `Closes #<issue>`, then the ticket's Goal and why, `git log --oneline base..HEAD`, the MEASURE table, the merge checklist as checkboxes, `decisions.md`, grader sections, backlog, metrics), push, `gh pr create` or update the existing PR through the REST API, notify, exit `pr-opened`.
+   A PR opened at the grader-round cap is a draft: `gh pr create --draft`, and a line under `Closes #<issue>` names the failing judge rows, so no automatic merge takes it before a human reads the Judge section; an already-open PR is only updated, not converted.
    Each judge backlog line is also filed once per run as a `needs-triage` issue, so a defect an unattended run finds is tracked outside the PR body.

 ## Exits

 | Status | Meaning | Counts a round |
 |---|---|---|
-| `pr-opened` | checks and graders pass, or the grader-round cap reached with a backlog | yes |
+| `pr-opened` | checks and graders pass, or the grader-round cap reached with a backlog (a draft PR) | yes |
 | `no-change` | HEAD and `decisions.md` are both unchanged since the previous round | yes |
 | `stuck` | the same failing check set twice in a row | yes |
 | `ticket-defect` | round 0 found a check that passes on base | no |
@@ -88,7 +89,7 @@ Codex token counts come from its `--json` events and land in the ledger with `co

 ## Grader-round cap and precedence

-After the checks first pass, at most two grader-fail rounds per ticket; then the remaining non-blocking findings go to the PR body backlog and the PR opens.
+After the checks first pass, at most two grader-fail rounds per ticket; then the remaining non-blocking findings go to the PR body backlog and the PR opens as a draft.
 The judge decides pass or fail.
 The reviewer blocks only on a `high` or `medium` finding, the Codex review only on a `critical` or `high` finding, and each may block at most once per ticket.
 A grader whose output is absent or unparseable is a fail with one high finding "grader unparseable", never a pass.
~~~~~~~~~~~~ evidence
