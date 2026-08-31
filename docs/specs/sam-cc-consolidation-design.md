# Sam CC Setup Consolidation Design

## Goal

Make `sam-cc-setup` the single Loam-owned plugin for reusable Claude Code setup workflows. Remove `sam-superpowers` only after its useful design workflow has a complete local handoff.

## Scope

This change moves the current `brainstorming` skill and its direct support files into `sam-cc-setup`. It adds an adapted `writing-plans` skill because `brainstorming` requires that handoff. It does not restore the other skills removed from the historical Superpowers fork.

The Clief Notes integration is outside this change. Claude Code will plan and execute that work in a separate session.

## Architecture

The design chain has one owner and two stages:

1. `brainstorming` turns an idea into an approved design document.
2. `writing-plans` turns that approved design into an executable implementation plan.

Both skills live under `cultivation/marketplace/sam-cc-setup/skills/`. `tech-selection` may route open-ended ideation to `brainstorming`. `brainstorming` may route only to `writing-plans` after design approval.

`writing-plans` must not require a missing `superpowers:*` execution skill. Its final handoff must select an execution method that is actually available in the current host. The default choices are a repository-provided subagent workflow, small checked batches in the current session, or a fresh implementation session using the saved plan.

## Distribution and provenance

Remove the `sam-superpowers` entry from the marketplace manifest and remove its directory. Bump `sam-cc-setup` from `0.4.0` to `0.5.0` in both manifests.

Preserve the upstream MIT notice for the moved and adapted material in `sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt`. Record the consolidation and adaptation in `cultivation/marketplace/UPGRADING.md`.

## Documentation

Update the marketplace README and the `sam-cc-setup` README so they describe one plugin and its current inventory. Historical specifications may retain `sam-superpowers` because they document earlier decisions. Active installation and upgrade instructions must not route to it.

Default design and plan locations must be generic Loam paths:

- Design documents: `docs/specs/YYYY-MM-DD-<topic>-design.md`
- Implementation plans: `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Verification contract

Add repository tests that fail on the current tree and pass only when:

- `sam-superpowers` is absent from the marketplace and filesystem.
- `sam-cc-setup` contains `brainstorming` and `writing-plans`.
- `tech-selection -> brainstorming -> writing-plans` resolves inside the plugin.
- The moved skills do not require a `superpowers:*` execution skill.
- The two `sam-cc-setup` version fields match `0.5.0`.
- The upstream MIT notice is present.

Run the focused unit tests first. Then run `bin/verify-template.sh` and require `verify-template: PASSED`.

## Non-goals

- Do not restore the historical Superpowers execution suite.
- Do not change the Loam seed.
- Do not implement or canonize Clief Notes claims.
- Do not change hook ownership in this branch.
