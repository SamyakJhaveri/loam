## Ticket

~~~~~~~~~~~~ evidence
Brief:
Add one no-fire line to the reviewer prompt: a finding is raised only when the diff shows it and no done check already proves it, and a pre-existing issue or a defect whose fix lies outside the owned files is not a finding; with the plugin bump and eval replay the grader change protocol requires.
Where: cultivation/marketplace/sam-cc-setup/agents/reviewer.md (one line after the Severity line), cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json and cultivation/marketplace/.claude-plugin/marketplace.json (version)
Done means: reviewer.md carries the self-check line after the Severity line and nothing else in it moves; the plugin version is 0.9.1 in both files; the reviewer evals still match after the manager's replay.
Out of scope: the judge; the severity definitions; the verdict rule (F23); any change to `bin/factory`.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none (F23 #88 was cut 2026-09-12: its verdict line deflated severities in the after-replay)

## Goal and why
The outcome-grader cookbook's last rubric rule is the one `reviewer.md` lacks: "Without a no-fire list, the grader thrashes on style nits, pre-existing issues, and scope creep. Spell out what's out of bounds and have it self-check each finding before raising it." The SDLC playbook's REVIEW.md says the same: define what is out of bounds, and exclude what the checks already enforce (`.superpowers/factory/research-2026-09-11/pages.md`, take 2).
Since F21 a `medium` finding blocks a worker round (2 to 4 usd). On 2026-09-11 the reviewer raised mediums in 10 of 16 rounds; the merge reads found some real (a restore guard that did not fire, a leaked export, an unguarded append) and some moot (F20's three lows were all answered by the diff; F21's two lows named a frozen prompt outside the ticket). A finding the diff does not show, or a done check already proves, now costs a round instead of a sentence, so the no-fire line has a cost case it did not have before F21.
The line is a prompt edit, so the grader change protocol applies: plugin bump, replay before and after in the PR body. The before-replay is the 2026-09-11 before-record (main, 0.9.0 reviewer.md): s2-round-5 merge 0/2/3, s2-round-8 merge 0/3/4, s3-round-5 merge 0/4/4, s4-round-4 merge 0/0/4 (high/medium/low).

## Do not touch
The standing list. Except: cultivation/marketplace/sam-cc-setup/agents/reviewer.md (one added line after the Severity line only), cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json and cultivation/marketplace/.claude-plugin/marketplace.json (the sam-cc-setup version only).
Also: bin/factory; bin/factory.d/; the judge prompt, schema, and evals; evals/reviewer/; seed/.

## Out of scope
- the judge prompt (a gate-honesty line was rejected 2026-09-11: round 0 is the negative control in code, and a second home for the rule is a duplicate)
- the severity definitions and the verdict rule (F23)
- `evals/reviewer/*/expected.json` (if the after-replay moves a verdict, the manager reads the raw reply and decides; the worker does not edit expectations)
- running the eval inside the loop

## Approach
Executor: `bin/factory run` as merged in F1, with F26 merged. The run's own graders read the installed plugin cache, so this ticket's edit does not grade itself.

Facts pinned: `reviewer.md` has the line beginning "Severity: `high` means merging would break main" followed by a blank line and "## Output"; the version fields read `0.9.0`; `grader_rubric` strips the frontmatter and keeps the body byte for byte, so an added body line reaches the frozen prompt unchanged.

Change:
1. `reviewer.md`: after the Severity line, add the line "Raise a finding only when the diff shows it and no done check already proves it; a pre-existing issue the diff did not introduce, or a defect whose fix lies outside the ticket's owned files, is not a finding." Keep the blank line before `## Output`.
2. Version `0.9.1` in `plugin.json` and `marketplace.json`.

## Done checks
```done-checks
grep -qF 'Raise a finding only when the diff shows it and no done check already proves it; a pre-existing issue the diff did not introduce, or a defect whose fix lies outside the ticket'"'"'s owned files, is not a finding.' cultivation/marketplace/sam-cc-setup/agents/reviewer.md && pass no-fire-line || fail no-fire-line "reviewer.md has no self-check line"
n=$(grep -n '^Severity: ' cultivation/marketplace/sam-cc-setup/agents/reviewer.md | cut -d: -f1); [ -n "$n" ] && sed -n "$((n + 1))p" cultivation/marketplace/sam-cc-setup/agents/reviewer.md | grep -q '^Raise a finding only when' && sed -n "$((n + 2))p" cultivation/marketplace/sam-cc-setup/agents/reviewer.md | grep -qx '' && sed -n "$((n + 3))p" cultivation/marketplace/sam-cc-setup/agents/reviewer.md | grep -qx '## Output' && pass line-placed || fail line-placed "the self-check line is not the line after Severity, or the blank line before ## Output moved"
grep -q '"version": "0.9.1"' cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json && grep -q '"version": "0.9.1"' cultivation/marketplace/.claude-plugin/marketplace.json && pass plugin-bump || fail plugin-bump "the sam-cc-setup version is not 0.9.1 in both files"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- after-replay on the branch by the manager: `bin/factory eval reviewer --graders-dir cultivation/marketplace/sam-cc-setup/agents` prints 4 cases, 0 mismatch, and each case's medium count matches the 2026-09-11 before-record (2, 3, 4, 0) (a drop would be severity deflation, not fewer defects); both replays and their cost go in the PR body (Grader change protocol)
- after the merge: `claude plugin update sam-cc-setup@seed-skills` on the runner and on the Mac; the next three runs' reviewer findings are read against the line, and a finding the diff does not show or a check already proves counts against it
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 30 turns

## Decisions
.superpowers/factory/research-2026-09-11/pages.md (take 2), docs/factory/LOOP.md (Grader change protocol), the 2026-09-11 reviewer rounds in .superpowers/factory/sessions/manager-2026-09-11-codex.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS no-fire-line
PASS line-placed
PASS plugin-bump
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Followed the Approach exactly; no departures.
reviewer.md: added the no-fire line verbatim from Approach step 1, right after the Severity line, keeping the blank line before ## Output (line-placed check confirms n+1 line, n+2 blank, n+3 ## Output).
plugin.json and marketplace.json: bumped the sam-cc-setup version 0.9.0 -> 0.9.1 (grader change protocol for a prompt edit).
Did not touch the judge, severity definitions, verdict rule (F23), evals/reviewer/, seed/, bin/factory, or bin/factory.d/.
Left the after-replay eval to the manager per the merge checklist; the worker does not run the eval in the loop.
Done checks: sourced lib.sh then the block from the worktree root; 4 PASS, 0 FAIL (no-fire-line, line-placed, plugin-bump, check-green).

~~~~~~~~~~~~ evidence

## Diff (901d7cf1...HEAD)

~~~~~~~~~~~~ evidence
 cultivation/marketplace/.claude-plugin/marketplace.json         | 2 +-
 cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json | 2 +-
 cultivation/marketplace/sam-cc-setup/agents/reviewer.md         | 1 +
 3 files changed, 3 insertions(+), 2 deletions(-)

diff --git a/cultivation/marketplace/.claude-plugin/marketplace.json b/cultivation/marketplace/.claude-plugin/marketplace.json
index 3702122..1619638 100644
--- a/cultivation/marketplace/.claude-plugin/marketplace.json
+++ b/cultivation/marketplace/.claude-plugin/marketplace.json
@@ -9,7 +9,7 @@
     {
       "name": "sam-cc-setup",
       "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, plan review, technology selection, validation, Codex cross-model review, and bootstrap support",
-      "version": "0.9.0",
+      "version": "0.9.1",
       "source": "./sam-cc-setup",
       "author": {
         "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
index 73e128c..84db8c9 100644
--- a/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
+++ b/cultivation/marketplace/sam-cc-setup/.claude-plugin/plugin.json
@@ -1,7 +1,7 @@
 {
   "name": "sam-cc-setup",
   "license": "MIT",
-  "version": "0.9.0",
+  "version": "0.9.1",
   "description": "Portable Claude Code setup with a local brainstorming-to-writing-plans workflow, merged plan review, technology selection, validation, cross-model Codex review, and bootstrap support for the rules layer plugins cannot ship.",
   "author": {
     "name": "Samyak Jhaveri",
diff --git a/cultivation/marketplace/sam-cc-setup/agents/reviewer.md b/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
index 4ca936c..a461023 100644
--- a/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
+++ b/cultivation/marketplace/sam-cc-setup/agents/reviewer.md
@@ -28,6 +28,7 @@ Look for, in this order:
 5. Loam's design laws: anything new that parses free text to decide safety, or that runs on a tool matcher.

 Severity: `high` means merging would break main, CI, a rendered project, or a later ticket; `medium` means wrong but contained; `low` means style or clarity.
+Raise a finding only when the diff shows it and no done check already proves it; a pre-existing issue the diff did not introduce, or a defect whose fix lies outside the ticket's owned files, is not a finding.

 ## Output

~~~~~~~~~~~~ evidence
