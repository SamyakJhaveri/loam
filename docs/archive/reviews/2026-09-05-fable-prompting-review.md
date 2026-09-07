# Review: fable-session-brief hook and fable-prompting skill

Date: 2026-09-05.
Branch: `feat/fable-prompting-skill`.
Commits: 2647090 (Piece B, hook) and 4fdf4cf (Piece C, seed skill).
Base: `main` at 0d0cb03.
Reviewer: Claude Fable 5.1 at high effort, coordinating Opus 4.8 workers.
Read-only review at the time of the verdict. The fixes were applied afterwards; see the Applied section at the end.

## Verdict: FIX FIRST

No behavior defect was found.
The hook does what the plan says, the contract and tests cover it, and both gates pass.
The fixes below are small prose and config edits, seven in total, none over five lines.
Three of them correct shipped or public text that is factually wrong today.
SHIP would be defensible if the owner prefers to take them as a follow-up commit.

## Findings

Findings are ordered most severe first.
Every finding was checked by two independent Opus 4.8 refuters, one for correctness and one for severity and fix.
Three completeness critics then swept the diff for what the first pass missed.
Severities below are the post-verification values.
Findings were proposals at the time of the verdict. All seven LOW fixes were applied afterwards; see the Applied section.

### LOW-1. SessionStart matcher omits the `fork` source

- `seed/.claude/settings.json:148`, `bin/rendered_harness_contract.py:99`, `bin/tests/test_rendered_harness_contract.py:195`, `seed/.claude/hooks/fable-session-brief.sh:9`.
- The matcher is `startup|resume|clear|compact`.
  The hooks docs list five SessionStart sources: `startup`, `resume`, `clear`, `compact`, `fork`.
  A forked session on Fable gets no brief from SessionStart.
  Fed a `source: fork` payload directly, the hook prints correctly, so the gap is only the route.
- Smallest fix: change the string to `startup|resume|clear|compact|fork` at all four sites.
  The contract compares matchers by strict equality at `bin/rendered_harness_contract.py:1020`, so settings, contract, and fixture must move together.
  Leave `harness-hygiene.sh` alone; its matcher predates this diff.

### LOW-2. Shipped CLAUDE.md prose describes the hook wrongly

- `seed/CLAUDE.md.jinja:28`.
- The line says the hook prints "at session start and on a model switch, only when the session model is Fable 5.1".
  Two claims are false.
  The docs say Claude Code does not always include `model` on SessionStart, so the brief is not guaranteed at session start.
  The gate at `fable-session-brief.sh:35` matches any model containing "fable", so a Fable 5 session also gets the brief.
  The clause also sits under the "Session logs" bullet, and the hook writes no log.
- Smallest fix: move the clause to the "Other hooks" bullet on line 26 and word it
  "`fable-session-brief.sh` (prints a short prompting brief on a model switch, and at session start when the event names the model, for any Fable model)".
  Keep the literal `fable-session-brief.sh` in CLAUDE.md; the contract prose route at `bin/rendered_harness_contract.py:211` requires it.

### LOW-3. The skill's owner legend contradicts its own action line, and `Mixed` is undefined

- `seed/.agents/skills/fable-prompting/SKILL.md:20-21`, `:35`, `:42-43`.
- Line 20 defines H as "Claude Code already handles it".
  Line 42 tells the reader for an H row to "change the effort level or the harness".
  Those describe different owners.
  Rows 25, 38, and 40 are H but need the author to act: pick the effort level, append the long-output note, or provide a crop tool.
  Row 35 uses `Mixed`, which the legend never defines and line 42 gives no action for.
- Smallest fix: rewrite lines 20-21 as three sentences.
  "Owner H means the harness or the effort setting owns it; prompt text changes nothing.
  Owner P means the prompt author owns it.
  Owner Mixed means both: set the effort level and quote the guide's instruction."
  Line 42 then reads consistently without change.

### LOW-4. Public inventories still list one shared skill

- `README.md:32`, `docs/BOOTSTRAP.md:20`, and cosmetically `docs/COPIER.md:11`.
- Both "what you get" lists name `catchup` as the only shared skill under `.agents/skills/`.
  The seed now ships two.
  These files are outside the diff, but the diff made them stale, and plan step C7 asked to update seed-skill prose to match.
- Smallest fix: add a `fable-prompting` bullet to README.md and docs/BOOTSTRAP.md.
  In docs/COPIER.md write "the `.claude/skills/*` symlinks".

### LOW-5. The seed-skill promotion gate now conflicts with the new asset-layers exception

- `docs/ASSET-LAYERS.md:18` (in diff) against `docs/specs/seed-skill-promotion.md:4`, `:21`, `:23` (not in diff).
- The new rule of thumb allows a pure reference skill in the seed when the owner requires it.
  The promotion spec says the seed stays "catchup only", rejects skills that describe rather than instruct, and requires a "NOT for" clause in the description.
  The new skill has no "NOT for" clause.
  AGENTS.md rule 6 says one directive lives in one home; these two now disagree.
- Smallest fix: in `docs/specs/seed-skill-promotion.md`, drop "(catchup only)" on line 4 and add one sentence after gate 1 recording the owner-decision exception for reference material and pointing at ASSET-LAYERS.md line 18.

### LOW-6. The handoff says Claude Code injects two blocks; the skill and hook say four

- `docs/HANDOFF-2026-09-03-audit-sessions.md:325-326` (in diff) against `SKILL.md:64-66` and `fable-session-brief.sh:43-45`.
- The handoff sentence names the autonomy block and the batching nudge only.
  The skill and hook name four: the autonomy block, the Delivering work block, the progress-updates line, and the batching nudge.
  Verified in this reviewing session on Fable 5.1: all four are present in the injected system prompt.
  So the skill is right and the handoff is under-counted.
- Smallest fix: change the handoff sentence to name all four blocks.

### LOW-7. Four table rows abbreviate the guide's section headings

- `SKILL.md:33`, `:34`, `:38`, `:39`.
- The guide headings are "Tell the model what to preserve in compaction summaries", "Keep changes and tests to what the task asks for", "Leave room for long outputs at xhigh and max effort", and "Let the lead agent keep working while subagents run".
  The other twelve rows are verbatim.
- Smallest fix: paste the verbatim headings into the four cells.

## Notes (INFO, no change required)

Hook:

- `fable-session-brief.sh:4` opens with "Those are the only two events", naming them after the colon.
  Optional: "Only two events reveal the model:".
- On resume both routes can fire (SessionStart `resume` plus PostModelSwitch restoring the model), so the 94-word brief may print twice.
  The plan chose no state file. Record this in the PR body.
- The printed text says "Fable 5.1 session" for any Fable model.
  The text is plan-specified verbatim.
  The plan's Risks section routes a future Fable model to the model-watch job; that trigger is not yet added.
- On `source: compact` the brief and `post-compact-reinject.sh` both fire and overlap on the targeted-edits advice.
  The compact route is the plan's hedge for a startup payload with no model field. Accepted.
- Switching away from Fable prints no retraction. Design choice.
- `PAYLOAD="$(cat)"` and the trailing `2>/dev/null || exit 0` match the house shape the plan named (`write-rewrite-guard.sh`).
  A crashed interpreter is indistinguishable from designed silence, but the two positive tests catch total breakage in CI.

Contract and tests:

- `test_every_required_prose_reference_is_enforced` and `test_required_prose_route_targets_are_enforced` iterate hardcoded subsets (9 of 18 and 8 of 17 entries).
  The new fable entries are not mutation-covered there.
  Pre-existing pattern. Optional: iterate over the contract's own inventories.
- `REQUIRED_RENDERED_PATHS` still spells the four shared-skill paths as literals at `:37`, `:38`, `:53`, `:54`.
  Duplication, not drift. Leave as is.
- Hook `timeout` values are never asserted by the contract. Pre-existing gap.
- `bin/rendered_harness_contract.py:1011` sorts `expected_matchers` without a key, then line 1020 re-sorts with `key=repr`.
  Safe today. If touched, delete the first sort rather than re-key it.
- The rubric and never-paste list live in both the hook and the skill with no equality test.
  They already differ in wording ("batching nudge" versus "tool-batching nudge").
  Optional: one test asserting the four block names appear in both.
- Three catchup-named negative symlink tests have no fable-prompting twin.
  The checker is name-parameterized and runs for both names, so coverage is equal. Cosmetic.

Skill prose:

- Line 8 "which half of it" against a 9/6/1 split. Optional: "which parts of it".
- Line 15 is a rationale numbered as a step. Optional: drop the numbering on both items.
- Lines 65-66 name the progress-updates line and the batching nudge without a guide section name.
- Row 36 could be `Mixed` rather than `P`; one of the guide's three fixes is harness-owned.
- Line 14 names `WebFetch`, a Claude Code tool, in a file Codex also reads.
  The plan's Decisions section accepts Codex reading the skill as harmless.
- Rows 29 and 37 are `P`, but in a Loam project the hook already injects both instructions for Fable sessions.
- The symptom column paraphrases the guide's own index and drops some qualifiers (client-side compaction, low effort).
  Line 9's "the guide wins" rule covers aging.

Out of scope, pre-existing, noted only:

- `seed/CLAUDE.md.jinja:1` title carries an em dash, shared with three sibling files since 2026-07-02.
- `docs/HANDOFF-2026-09-01-harness.md:35` records the seed listing at 101 tokens; it is now 143. Dated record.
- `harness-hygiene.sh` matcher omits `fork` and `compact`.

Process:

- The plan calls for two PRs and step C7 branches Piece C from main.
  The commits are stacked; `feat/fable-session-brief` sits at 2647090 as an ancestor.
  Open PR 1 from `feat/fable-session-brief` into main.
  After it merges as a merge commit, PR 2 from `feat/fable-prompting-skill` shows only 4fdf4cf. No rebase needed.

Dropped after verification: the violation-message event order (matches the dict), the "near 40 tokens" wording (no drift), and the claim that the symptom table is a forbidden vendored copy (the plan specified the table).

## Task checks

1. Hook.
   Ten payload cases run by hand: absent model, non-Fable model, Fable model, malformed JSON, PostModelSwitch to Fable, PostModelSwitch to Opus, empty stdin, model as integer, model as null, top-level array.
   Every case exited 0.
   Only the two Fable cases printed, once each, byte-identical.
   Mode 755 on disk and 100755 in git.
   No write to disk.
   `bash -n` and shellcheck clean.
   Header carries the house fields.
   Brief text is identical to the plan's Piece B string, 94 words.
   With python3 absent from PATH the hook is silent and exits 0.
2. Settings and contract.
   `grep -rn fable-session-brief bin/ seed/` hits: required rendered path (`contract:52`), SessionStart route (`:99`), PostModelSwitch route (`:101`), prose-route reference (`:211`), prose-route target (`:231`), test copies of required paths (`test_rendered_harness_contract.py:51`) and hook paths (`:83`), good-settings fixture (`:199`, `:209`), good-prose fixture (`:234`), behavioral tests (`test_seed_claude_hooks.py:1085`), live routes (`settings.json:152`, `:163`), CLAUDE.md.jinja prose (`:28`), and the script itself.
   PostModelSwitch is declared in the route dict, the violation message, both fixtures, and settings.
   No stale hook count in `bin/*.sh`; both counts are computed at run time.
3. Skill.
   Frontmatter has `name: fable-prompting` and no `auto-activate`.
   Description is 153 characters, no colon.
   `grep -c '^| '` returns 17: one header plus 16 rows.
   All 16 rows map to the guide's 16 `##` sections and every section has a row.
   No file other than SKILL.md in the directory.
   No non-ASCII character in any diff file except the pre-existing title em dash.
   Two relative symlinks of the same form, both mode 120000; the new one resolves.
   `claude plugin validate seed/.agents/skills` passes.
4. Contract generalization.
   `SHARED_SKILL_LINKS` at `:32` holds both names.
   The topology exception at `:277` and the symlink checker at `:743` read from it.
   Every remaining `catchup` literal has a `fable-prompting` twin or is a fixture.
   No stray literal.
5. Gates. Pasted below.

## Gate output

Full suite, run by the gates worker on 4fdf4cf:

```
253 passed, 382 subtests passed in 1132.09s (0:18:52)
[exited with code 0]
```

Template verification, final lines:

```
== stage 8: skill-listing token weight ==
seed: 143 tokens (2 skills listed, 0 manual, 0 agents, 0 workflows)
sam-cc-setup [gated]: 2704 tokens (18 skills listed, 8 manual, 6 agents, 1 workflow)
impeccable: 0 tokens (0 skills listed, 1 manual, 0 agents, 0 workflows)
budget: 2750 tokens per gated source
skill-listing weight: OK (<= 2750 tokens; research target is ~2000)

verify-template: PASSED
[exited with code 0]
```

`git status --short` after both gates: empty. HEAD still 4fdf4cf.

New hook tests, run again by the lead session:

```
$ pytest bin/tests/test_seed_claude_hooks.py -k FableSessionBrief
6 passed, 112 deselected in 0.42s
```

Timing note: the full suite took 19 minutes and verify-template 20 minutes because five workers ran the suite concurrently. Alone, the hook file runs in about a minute.

## Blind review BLOCK and HIGH findings

| ID | Finding | Status |
|---|---|---|
| B1 | Skill busts or evades the stage 8 listing gate | Resolved. Real file under `seed/.agents/skills/`, which stage 8 scans. Seed is reported, not gated: 143 tokens. |
| B2 | Deleting the standing-orders preamble deletes the loader | Resolved outside this diff. Piece A is local; the `@~/.claude/FABLE-BRAIN.md` import line is still present. |
| H1 | Tracker file makes the mechanism non-deterministic | Resolved. No state file; absent model exits silently, locked by `test_absent_model_field_is_silent`. |
| H2 | Per-prompt nudge is over-production | Resolved. No `UserPromptSubmit` route in settings or contract. |
| H3 | Path regex reporter fires on ordinary edits | Resolved. No PostToolUse reporter in the diff. |
| H4 | align-prompt splice loses function | Resolved. `align-prompt/SKILL.md` untouched. |
| H5 | Plan overrides the placement rule without argument | Overruled by owner (plan Decisions item 1). Exception documented at `docs/ASSET-LAYERS.md:18`. The "say so in the PR body" half is pending until a PR exists. |

Still open from the plan: step B7 asks the PR body to record which event fired in the live check.
See the next section.

## Live check

This reviewing session started on this branch.
The brief appeared in the first turn, delivered by the PostModelSwitch hook after the owner ran `/model` to Fable 5.1.
No SessionStart delivery of the brief was visible in this session's context.
That is consistent with the docs: SessionStart does not always carry `model`.
It does not settle whether SessionStart delivers the brief when the model is present.
For the PR body: "Live check: after `/model` to Fable 5.1 the brief arrived via PostModelSwitch. SessionStart delivery is not yet observed."

## Method

- Five Opus 4.8 workers: hook behavior, contract sweep, skill file, gates, blind-review resolution.
- One verification workflow: 46 Opus 4.8 refuters, two per finding with different lenses, plus three completeness critics.
- 49 workflow agents, 649 tool uses, all completed.
- The lead read the skill file, the CLAUDE.md.jinja hook bullet, the promotion spec, the handoff sentence, and the prose-route tests directly before ranking.

## Applied (2026-09-05, same session)

All seven LOW fixes were applied to the working tree on the owner's instruction.
Nothing was committed.

| Fix | Files |
|---|---|
| LOW-1 `fork` in matcher | `seed/.claude/settings.json`, `bin/rendered_harness_contract.py`, `bin/tests/test_rendered_harness_contract.py`, `seed/.claude/hooks/fable-session-brief.sh` |
| LOW-2 hook prose | `seed/CLAUDE.md.jinja` (clause moved to the "Other hooks" bullet and reworded) |
| LOW-3 owner legend | `seed/.agents/skills/fable-prompting/SKILL.md` lines 20-22 |
| LOW-4 inventories | `README.md`, `docs/BOOTSTRAP.md`, `docs/COPIER.md` |
| LOW-5 promotion gate | `docs/specs/seed-skill-promotion.md` |
| LOW-6 injected-block count | `docs/HANDOFF-2026-09-03-audit-sessions.md` |
| LOW-7 verbatim headings | `seed/.agents/skills/fable-prompting/SKILL.md` rows 33, 34, 38, 39 |

Gates after the fixes, run alone by the lead session:

```
Ran 253 tests in 381.435s
OK
contract unit tests: OK
Copier scratch render: OK
rendered harness contract: OK
stale-counts: OK
skill-listing weight: OK (<= 2750 tokens; research target is ~2000)
verify-template: PASSED
```

Diff size: 11 files, 19 insertions, 15 deletions.
