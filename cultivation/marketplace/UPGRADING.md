# Marketplace upgrades

This file records why a promoted plugin change traveled. It is also the upgrade
entry point for projects that consume the Loam marketplace.

## sam-cc-setup v0.9.10 codex-review runs one bare codex exec

`/codex-review` no longer pipes `git diff` into Codex.
It runs one Bash call that starts with `codex exec`, with no pipe or redirect, and Codex runs `git diff` itself.
A sandbox exclusion such as `codex exec *` now matches the call, so Codex no longer runs inside Claude's sandbox, where it can fail to reach its API or to start its own sandbox.
Findings left unfixed go to the project's issue tracker once the user agrees, not to the retired `docs/findings/FINDINGS.md`.
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.7 brief names the render proof

The `/brief` skill's Track B now says a Loam ticket that changes rendered-project behavior proves it with `control-loam`, in the form `docs/factory/CONTRACT.md` gives.
No agent prompt changed, so no grader replay is owed.
Upgrade step: `claude plugin update sam-cc-setup`.

## sam-cc-setup v0.9.6 factory grader fixes

reviewer.md no longer ties its verdict word to a severity; the loop and the eval both block on a high or medium finding.
Among agent prompt changes, v0.9.6 carries only that deletion of the reviewer's verdict line; judge.md is unchanged.
A reviewer replay before and after is owed before this version merges (docs/factory/LOOP.md, Grader change protocol).
It runs on this Mac, not the runner, from a checkout of this branch:

```sh
mkdir -p ~/replay-w4/before-agents
for g in reviewer; do git show origin/main:cultivation/marketplace/sam-cc-setup/agents/$g.md > ~/replay-w4/before-agents/$g.md; done
# the hand cases (evals/reviewer)
for g in reviewer; do
  EVAL_OUT=~/replay-w4/hand/before/r1 EVAL_EFFORT=high bin/factory eval $g --graders-dir ~/replay-w4/before-agents
  EVAL_OUT=~/replay-w4/hand/after/r1  EVAL_EFFORT=high bin/factory eval $g --graders-dir cultivation/marketplace/sam-cc-setup/agents
done
# the clean corpus, for false alarms and severity direction
for g in reviewer; do
  EVAL_OUT=~/replay-w4/clean/before/r1 EVAL_EFFORT=high bin/factory eval $g --evals-dir evals/clean --graders-dir ~/replay-w4/before-agents
  EVAL_OUT=~/replay-w4/clean/after/r1  EVAL_EFFORT=high bin/factory eval $g --evals-dir evals/clean --graders-dir cultivation/marketplace/sam-cc-setup/agents
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

## Unreleased: sam-cc-setup review consolidation

The critique-swarm skill is removed because session-critique covers decision-aware
session review and the plan-review-fanout workflow covers pre-execution plan review, so
the skill was a fifth review entry point with no job of its own. The plugin then shipped 26
skills. That count is historical: v3.0.0 cut the plugin to three skills, and today
`find cultivation/marketplace/sam-cc-setup -name SKILL.md | wc -l` prints 4.
plan-review-fanout pins every agent to claude-opus-4-8[1m] and adversarially
verifies only BLOCK findings. validate is now a thin caller of the build-validator
agent, which absorbed the lint, type check, whitespace, shell syntax, test suite, and
smoke-path checks. ship, auto-phase, gen-spec, codex-review, and codex-plan-review are
manual-only (disable-model-invocation: true) now that anthropics/claude-code#26251 is
closed. codex-review appends open findings to docs/findings/FINDINGS.md. Upgrade step:
`claude plugin update sam-cc-setup` after the next release; the version bump happens in
the release loop.

## Current: sam-cc-setup v0.7.0 external-skill vetting

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
