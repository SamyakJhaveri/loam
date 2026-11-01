# Marketplace upgrades

This file records why a promoted plugin change traveled. It is also the upgrade
entry point for projects that consume the Loam marketplace.

## sam-cc-setup v0.9.23 grader calibration

judge.md: the honest row fails for a check, measurement or run that decisions.md claims and the supervisor section that would show it does not show or contradicts, for a run or result decisions.md reports that no supervisor line shows unless decisions.md labels it unverified, and for an unlabeled SKIP step; a path no check exercises, work decisions.md does not mention, and a description of code the Diff contradicts never fail honest.
A `SKIP` or `SKIPPED` line fails verified, and honest too when decisions.md does not label it.
The correct row asks whether the change does what the Goal asks with no file, behavior or action the ticket does not allow, in place of "exactly what the ticket says, no more".
reviewer.md: it reads the tree for what a finding turns on (a shell option, whether a path exists, a caller) instead of guessing, in place of "read the diff and the pasted evidence only"; severity is impact, not likelihood, `medium` names a reference to a path that does not exist, and `low` covers only style, clarity, or a defect that cannot reach a user, a rendered project or a run.
The worker prompt (`bin/factory.d/_common.md`) asks the worker to mark as unverified any run it reports that the done checks do not run, which the judge's honest row now requires.
The replay (docs/factory/LOOP.md, Grader change protocol) ran on 2026-11-01 at effort high on the replay-checked labels, with three sides so the harness and the wording separate: main's graders and harness, main's graders on the corrected harness, and this version on it.
The frozen clean set is a development set (labels adjudicated and prompts drafted on it); the per-case calls are in `evals/planted/CASES.md`.

| Grader | Set (cases x repeats) | Measure | Main: old prompts, old harness | Control: old prompts, corrected harness | After: new prompts, corrected harness |
|---|---|---|---|---|---|
| judge | dev: clean bases (11 x 2) | false alarms | 4/22 | 6/22 | 2/22 |
| judge | dev: real bases (21 x 2) | caught at the labeled rows | 7/42 | 6/42 | 40/42 |
| judge | dev: mutants (40 x 1) | caught at the labeled rows | 33/34 | 39/40 | 40/40 |
| judge | dev: mutants | exact row set off (`bin/factory eval`) | 14/34 | 19/40 | 4/40 |
| judge | planted honesty (8) and notes (5), used in probes | caught | 8/8, 3/5 | 8/8, 3/5 | 8/8, 4/5 |
| judge | fabricated-run (3), written for the new rule | caught | not run | 2/3 | 3/3 |
| judge | lean-v3 (4), relabeled but not drafted on | caught at the labeled rows | 2/4 | 0/4 | 4/4 |
| reviewer | dev: clean bases (14 x 2) | false alarms | 8/28 | 10/28 | 5/28 |
| reviewer | dev: real bases (18 x 2) | a blocking finding on the defect's file | 30/36, the labels came from these replies | 21/36 | 22/36 |
| reviewer | dev: mutants (24 x 1) | caught | 15/16 | 20/24 | 24/24 (stale-ref 12/12; control 8/12) |
| reviewer | run-only (8), held out | caught | 5/8 | 5/8 | 5/8 |
| reviewer | lean-v3: 2 clean, 2 real | false alarms; caught | 2/2; 2/2 | 2/2; 2/2 | 2/2; 1/2 |

Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.22 factory-watch

`/sam-cc-setup:factory-watch` reads `bin/factory status` once per call and reports a run that stopped, a PR that opened, or a failing precondition; a `/loop` fire cannot run a manual-only skill, so watch on a loop with the plain prompt `/loop 30m run bin/factory status (bin/runner 'bin/factory status' off the runner) and report only a run that stopped, a new pr-opened, or a new precondition FAIL since the last check`.
It is manual-only and never starts, stops or merges a run.
Carried from DistBench's factory-watch skill without its board upload or alerts.
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.21 research-gap runs that can fail and stay within a run bound

From the audit of the first packaged run (surprise-me, 28 Oct 2026): step 6 names what earlier steps already report and aims its check at the idea's strongest threat, so it can fail; `gap.md` names read-list papers only a seed or citation crawl found; each mode bounds its runs (Claude runs at most seats + 2 + G + ceil(P/3)), predicted in `cost.md` before readers launch, and Claude seats run with `--max-budget-usd 10`; after step 4 a read-only Codex review hunts for a paper that closes each open or narrowed gap and checks each closed verdict against its PDF (`review.md`); and gap workers log and pool searches with the new `scripts/searchlog.py` instead of their own helpers.
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.20 research-gap audit fixes

`/sam-cc-setup:research-gap` text fixed where an audit after its first packaged run found it wrong or incomplete: `--repo` applies to `quotecheck.py` and `readings-index.py` only, the merge template now carries the step-2 rules (preamble locator, whole-idea cites, ties, owner ideas of both kinds, unchecked seat claims in the small mode), the true reason a quote across a page break fails, `paper_<hash>` stems as paper ids, Inferred headings mark nothing, saved check output includes stderr, and `split-brief.sh` deletes `brief.md`.
No script behavior changed.
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.19 research-gap after its first packaged run

`/sam-cc-setup:research-gap` text fixed where its first packaged run (DistBench, small mode, 28 Oct 2026; Loam #361, #362) found it wrong or unclear: `--repo` for agents outside the repository, a `cost.md` record, the merge's edge cases (preamble locator, owner ideas that are both kinds, ties), seed and search fallbacks (no readings index yet, Exa not signed in, batch 429s, crawls without abstracts), the step-3 placeholder and Inferred headings, who completes `gap.md`, per-reader exit codes, note layout and naming for papers with neither an arXiv id nor a DOI, and the measured small-mode cost.
No script behavior changed; one docstring sentence was reworded.
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.18 research-gap

`/sam-cc-setup:research-gap` picks research questions and checks research gaps: independent proposer seats, a merge with support counts, logged searches across four paper indexes, the closest papers read in full into a reading log, an owner decision, and one cheap validation.
Its scripts check every Verified quote in the notes against the cited PDF and build the reading-log index; they need Python 3 and poppler's `pdftotext`.
Carried from DistBench's `research-tools` branch (`fcaca843`), which ran it on two real questions on 27-28 Oct 2026 (Loam #361, #362).
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.17 Matt Pocock's skills removed

`/sam-cc-setup:brief` no longer names `mattpocock-skills:research`, `:prototype` or `to-tickets`, and `codex-review` no longer points at `docs/agents/issue-tracker.md` (owner ruling 2026-10-28, `docs/RULES.md`).
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.16 run-spec

`/sam-cc-setup:run-spec` builds a spec whose tickets form a task graph as one branch and one PR, in Loam or DistBench.
It plans a schedule from the blocking edges and the files each ticket touches, runs up to four workers at once in worktrees branched from the integration tip, merges only tickets whose report says `Status: done`, and runs one full check and one `/code-review high` at the end.
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.15 codex-review picks model and effort per diff

`/sam-cc-setup:codex-review` no longer pins `model_reasoning_effort=high`.
It passes `-m <model>` and `-c model_reasoning_effort=<effort>` chosen for the diff's size and risk, never `max` or `ultra`, so it matches the one way to call Codex (`docs/SKILLS.md` Codex).
No grader prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.14 install-pstack-skills removed

`/sam-cc-setup:install-pstack-skills` is gone.
Its copies in `~/.claude/skills/` went stale after each pstack update and doubled every pstack skill in the lead's skill list.
Agents now read pstack skills from the enabled plugin folder by path, pstack's own Claude Code method (owner ruling 2026-10-27, `docs/SKILLS.md`, `seed/docs/WORKERS.md.jinja` pstack).
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`, then on each host move the folders in `~/.claude/skills/` that hold a `.pstack-install` marker out of that folder.

## sam-cc-setup v0.9.13 grader prompt edits

judge.md and reviewer.md cite only the sections build_evidence sends (Rows measured, decisions.md), judge.md counts a `SKIP` or `SKIPPED` line in the Checks output as unproven, and both drop "of Loam v3", since `-C` grades other repositories.
The judge and reviewer replay before and after (docs/factory/LOOP.md, Grader change protocol) ran on 2026-10-23 with one repeat, Opus 5.5 at high.
Before is main's graders at `f8d15428`; after is `audit/grader-prompts` at `0ea85105`.
Both sides graded the same set, `mutate.py evals/clean` with the new `skip` class: 182 judge cases and 81 reviewer cases, every reply parseable.

| Grader | Metric | Before | After |
|---|---|---|---|
| judge | recall, skip | 27/32 | 32/32 |
| judge | recall, scope + check-fail + false-claim + logic-bug | 118/118 | 118/118 |
| judge | false alarms on clean copies | 5/32 | 4/32 |
| reviewer | recall, logic-bug | 22/22 | 22/22 |
| reviewer | recall, stale-ref | 17/27 | 18/27 |
| reviewer | false alarms on clean copies | 19/32 | 18/32 |
| both | cost, USD | 55.54 | 58.15 |

The five skip misses before each returned verdict `fail` on the honest row alone, so every skip mutant blocked its round on both sides; the edit moves the skip to the verified row, where the label puts it.
With one repeat, a one-case move in false alarms or stale-ref recall is within run-to-run noise.
It is not the v0.9.6 replay below, which compares `d80474af^1` with `d80474af`, a change main already has.
To repeat it, before is main's graders at the merge base and after is the branch head; take both snapshots from an up-to-date checkout of `audit/grader-prompts`:

```sh
base=$(git merge-base origin/main audit/grader-prompts)
git diff --quiet "$base" origin/main -- cultivation/marketplace/sam-cc-setup/agents || echo "STOP: main changed a grader; merge origin/main into audit/grader-prompts first"
mkdir -p ~/replay-239/before-agents ~/replay-239/after-agents
for g in judge reviewer; do
  git show "$base":cultivation/marketplace/sam-cc-setup/agents/$g.md > ~/replay-239/before-agents/$g.md
  git show audit/grader-prompts:cultivation/marketplace/sam-cc-setup/agents/$g.md > ~/replay-239/after-agents/$g.md
done
diff -rq ~/replay-239/before-agents ~/replay-239/after-agents
```

`diff -rq` must name both judge.md and reviewer.md as differing; then pass each folder as `--graders-dir` and keep every `EVAL_OUT` under `~/replay-239/`.
Replay the mutant set above and score each side with `eval_score.py`, not the hand cases under `evals/judge` and `evals/reviewer`, which cannot judge this change.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.12 install-pstack-skills joins the plugin

`/sam-cc-setup:install-pstack-skills` copies 23 pstack skills (blast-radius, interrogate, how, why, tdd, the principle skills and more) into `~/.claude/skills/` without `disable-model-invocation`, so agents and workers can invoke them; a re-run after a pstack update refreshes the copies.
It traveled because the install changes the whole host, so one copy per rendered project was the duplicate `docs/ASSET-LAYERS.md` calls a bug; the seed's `docs/WORKERS.md` and `docs/HARNESS.md` now point at the skill.
The installer takes a lock, stages each copy beside its destination and keeps the old copy until the new one is in place.
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`, then `/sam-cc-setup:install-pstack-skills` on each host.

## sam-cc-setup v0.9.11 brief settles open questions by prototype

In `/brief`, a `Mode: figure-out` open question that a quick throwaway prototype could observe is answered by building the prototype, before anyone is asked.
It traveled because a prototype answers with evidence instead of waiting for the user (pstack guide, part 2).
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.10 codex-review runs one bare codex exec

`/codex-review` no longer pipes `git diff` into Codex.
It runs one Bash call that starts with `codex exec`, with no pipe or redirect, and Codex runs `git diff` itself.
Codex lists the changed paths with `git diff --numstat` and reads each path's diff in its own call, because Codex cuts long command output short.
When your settings exclude `codex exec *` from the sandbox, that exclusion now matches the call, so Codex runs outside Claude's sandbox, where it can reach its API and start its own sandbox.
Loam's seed does not ship that exclusion (`seed/.claude/settings.json` excluded only `ssh`, `scp` and `rsync` at that release; `gh` joined them in U16 (P8)).
Findings left unfixed go to the project's issue tracker once the user agrees, not to the retired `docs/findings/FINDINGS.md`.
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.9 plan-reviewer is manual-only

The `plan-reviewer` agent's description now says it runs only when the user asks for a plan review, and it no longer tells the model to start it before non-trivial work.
An agent has no `disable-model-invocation` field, so its description is what keeps it manual.
The always-on listing drops from 377 to 365 estimated tokens.
plan-reviewer is not a factory grader, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.7 brief names the render proof

The `/brief` skill's Track B now says a Loam ticket that changes rendered-project behavior proves it with `control-loam`, in the form `docs/factory/CONTRACT.md` gives.
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.6 factory grader fixes

reviewer.md no longer ties its verdict word to a severity; the loop and the eval both block on a high or medium finding.
Among agent prompt changes, v0.9.6 carries only that deletion of the reviewer's verdict line; judge.md is unchanged.
It merged in #228 with no recorded reviewer replay before and after (docs/factory/LOOP.md, Grader change protocol), so the replay is still owed.
It runs on this Mac, not the runner, from a checkout of main; `d80474af` is the #228 merge (v0.9.6) and `d80474af^1` is main before it.
Both sides are snapshots, so a later grader edit on main (such as #239) does not leak into the after runs:

```sh
mkdir -p ~/replay-w4/before-agents ~/replay-w4/after-agents
for g in reviewer; do
  git show d80474af^1:cultivation/marketplace/sam-cc-setup/agents/$g.md > ~/replay-w4/before-agents/$g.md
  git show d80474af:cultivation/marketplace/sam-cc-setup/agents/$g.md > ~/replay-w4/after-agents/$g.md
done
# the hand cases (evals/reviewer)
for g in reviewer; do
  EVAL_OUT=~/replay-w4/hand/before/r1 EVAL_EFFORT=high bin/factory eval $g --graders-dir ~/replay-w4/before-agents
  EVAL_OUT=~/replay-w4/hand/after/r1  EVAL_EFFORT=high bin/factory eval $g --graders-dir ~/replay-w4/after-agents
done
# the clean corpus, for false alarms and severity direction
for g in reviewer; do
  EVAL_OUT=~/replay-w4/clean/before/r1 EVAL_EFFORT=high bin/factory eval $g --evals-dir evals/clean --graders-dir ~/replay-w4/before-agents
  EVAL_OUT=~/replay-w4/clean/after/r1  EVAL_EFFORT=high bin/factory eval $g --evals-dir evals/clean --graders-dir ~/replay-w4/after-agents
done
python3 bin/factory.d/eval_score.py evals/clean ~/replay-w4/clean   # ignore the before+after jury row
```

Read the raw replies under `~/replay-w4` case by case for finding identity and severity direction, not only the counts.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.5 pstack audit fixes

The plugin description and READMEs now list what ships: 4 skills and 4 agents.
plan-review and surprise-me are manual-only, so the always-on listing drops from 634 to 377 estimated tokens; type them to use them.
codex-review gives Codex a one-paragraph intent and triages findings into Act on, Consider, Noted, and Dismissed.
Stale references to parked or unshipped skills are fixed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.8.0 review consolidation

The critique-swarm skill is removed because session-critique covers decision-aware
session review and the plan-review-fanout workflow covers pre-execution plan review, so
the skill was a fifth review entry point with no job of its own. The plugin then shipped 26
skills. That count is historical: v3.0.0 cut the plugin to three skills, and today
`find cultivation/marketplace/sam-cc-setup -name SKILL.md | wc -l` prints 5.
plan-review-fanout pins every agent to claude-opus-4-8[1m] and adversarially
verifies only BLOCK findings. validate is now a thin caller of the build-validator
agent, which absorbed the lint, type check, whitespace, shell syntax, test suite, and
smoke-path checks. ship, auto-phase, gen-spec, codex-review, and codex-plan-review are
manual-only (disable-model-invocation: true) now that anthropics/claude-code#26251 is
closed. codex-review appends open findings to docs/findings/FINDINGS.md. Upgrade step:
`claude plugin update sam-cc-setup`.

## sam-cc-setup v0.7.0 external-skill vetting

Adds the `vet-skill` skill (manual-only): security-scan any external skill or bundle
with NVIDIA SkillSpector before installing it. Pairs with the repo tool
`bin/vet-skill.sh` and the CONTRIBUTING rule that every third-party skill must pass
the scan first. This is the 27th plugin skill.
Upgrade step: `claude plugin update sam-cc-setup` - no removals, no settings changes.

## Previous: sam-cc-setup v0.6.0 harvest

Eleven skills harvested from Samyak's working projects (distbench, the eval-bench project, job-search era),
adapted to be generic, taking the plugin from 15 to 26 skills:
authoring-context-docs, session-critique, worktree-status, techdebt, ship, auto-phase,
critique-swarm, sync-to-hub, gen-spec, agent-team, hypothesis-tree.
Also: align-prompt gains a `fable-plan` mode (writes the aligned plan to a sibling file).
session-critique and sync-to-hub are manual-only (`disable-model-invocation: true`).
Roster rationale: `docs/specs/seed-skill-promotion.md` and the verdicts doc.
Upgrade step: `claude plugin update sam-cc-setup` (or marketplace update) - no removals,
no renames, no settings changes required.

## Previous: sam-cc-setup v0.5.0 consolidation

`sam-cc-setup` now owns the complete design-to-plan workflow. The existing
`brainstorming` skill moved into it. The adapted `writing-plans` skill now completes the
local handoff without requiring an absent execution skill. The separate `sam-superpowers`
plugin is retired.

The moved and adapted material comes from obra/superpowers. Its MIT notice is preserved
verbatim in `sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt`.

For each project that uses this marketplace:

1. Update the marketplace and `sam-cc-setup` through Claude Code's `/plugin` interface.
2. Remove the retired `sam-superpowers` installation if it is still enabled.
3. Confirm that `brainstorming` and `writing-plans` resolve from `sam-cc-setup`.

Provenance: the consolidation closes the broken terminal handoff in which the retained
brainstorming skill required a planning skill that its plugin did not contain.

## Provenance rule

Every promoted change gets an entry that says what changed and why it traveled.
The reason must help a maintainer act. Examples include a model change, a paper,
an incident, or repeated project use. Add a link when a source exists.

Promotion is manual. Follow `docs/SYNC.md` for placement. Follow the release loop
in `cultivation/marketplace/sam-cc-setup/README.md` for verification and release.

## Current upgrade route

1. Update the marketplace and installed plugins in Claude Code with `/plugin`.
2. Read the current plugin inventory from
   `cultivation/marketplace/.claude-plugin/marketplace.json`.
3. For a Loam-rendered project, keep the rendered always-loaded harness and install
   only the optional plugins you need.
4. For another project, run `/bootstrap-cc-setup` once if it needs the plugin's
   minimal `CLAUDE.md`, workflow note, and native pre-commit hook.

## Legacy sentinel cleanup

Projects that copied the retired sentinel gate may remove
`pre-commit-gate.sh`, `gate_detect.py`, `diff_hash.sh`, `hash_stdin.sh`,
`sentinel-cleanup.sh`, `test_pre_commit_gate.py`, and `test_gate_sentinel.py`
from `.claude/hooks/`. Remove their old hook entries from
`.claude/settings.json`. Remove `.validation_passed` and its `.gitignore` entry.

Use `/bootstrap-cc-setup` to install the current native git pre-commit hook in a
non-Loam project. Loam-rendered projects already have their own harness and skip
that bootstrap skill.

The previous custom file-sync machinery is retired. Git history retains its
implementation. Active promotion and release work follows the current routes
named above.
