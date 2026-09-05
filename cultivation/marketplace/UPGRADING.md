# Marketplace upgrades

This file records why a promoted plugin change traveled. It is also the upgrade
entry point for projects that consume the Loam marketplace.

## Unreleased: sam-cc-setup review consolidation

The critique-swarm skill is removed because session-critique covers decision-aware
session review and the plan-review-fanout workflow covers pre-execution plan review, so
the skill was a fifth review entry point with no job of its own. The plugin now ships 26
skills, counted by
`find cultivation/marketplace/sam-cc-setup/skills -name SKILL.md | wc -l`.
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
