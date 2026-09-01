# sam-cc-setup

The portable core of Sam's Claude Code setup, extracted from a research repo where every
piece earned its place in production use (except two, flagged below).

**Audience:** repositories that want optional planning, review, validation, and
cross-model skills. This includes projects rendered by
[Loam](https://github.com/SamyakJhaveri/loam). A Loam-rendered project already has
the always-loaded harness, so it does not run `/bootstrap-cc-setup`.

## What the plugin exposes after installation

- **A concurrent-checkout guard** that blocks two sessions from racing on one working tree.
  This plugin file is a distribution mirror for non-Loam projects. The canonical file is
  `seed/.claude/hooks/concurrent-checkout-guard.sh`. Edit the canonical file first, copy it
  here byte-for-byte, then run `bin/verify-template.sh` from the Loam root.
- **Skills:** `plan-review` (blind merged plan review), `tech-selection` (bounded
  component trade-off records), `surprise-me` (ranked, evidence-backed unsolicited
  ideas; rehomed from the dissolved helpers bundle), `validate` (on-demand two-wave
  deterministic pass),
  `codex-review` and `codex-plan-review` (cross-model second opinions - require the
  Codex CLI), `brainstorming` (approved design documents), `writing-plans` (exact,
  testable implementation plans), `dream`, `align-prompt`, `scaffold-context`, `reflect`,
  `sam_handoff`, `unknowns`, `bootstrap-cc-setup`.
- **Agents:** `plan-reviewer` (merged 2026-08-29: correctness checklist + elegance
  gate in ONE blind unit, bounded findings, coverage ledger), `consistency-checker`,
  `test-synthesizer`, `code-architect`, `build-validator`, `read-only`.
  Removed 2026-08-29 as natively superseded: `diff-reviewer`, `code-simplifier`,
  `self-critic` (bundled `/code-review`, `/simplify`), `security-scanner`
  (`/security-review`), and the baseline skeletons `verify-app` / `regression-checker`
  (their `.claude/baselines.json` contract never shipped).
- **Workflows:** `plan-review-fanout` (grounded adversarial plan review, parallel lenses).

## Design-to-plan workflow and provenance

`tech-selection` routes open-ended ideation to the local `brainstorming` skill.
After the user approves the design, `brainstorming` writes it under `docs/specs/`
and hands it to the local `writing-plans` skill. Plans go under `docs/plans/`.
The planning handoff offers only execution methods available in the current host.

The two design workflow skills are moved or adapted from obra/superpowers.
Their upstream MIT notice is preserved verbatim at
`THIRD_PARTY_LICENSES/obra-superpowers.txt`.

## Opt-in guards (v0.2.0) - dormant until you declare their config

Two more hooks and a checker ship inert; each activates only when its repo-local
config file exists, so these v0.2.0 additions change nothing until you opt in.
(The plugin is behavior-neutral on install since v0.3.0: commit enforcement starts
only when `/bootstrap-cc-setup` installs the native pre-commit hook.)
All come from originals proven in daily use upstream. The two generalized ones (`protect-paths`,
`check_stale_counts`) each carry a control suite with positive AND negative controls -
a guard that has never fired proves nothing. `generated-file-guard.sh` was vendored
as-is (already registry-driven, proven in use upstream) and has no shipped suite;
exercise it with a seeded registry row after install.

| Guard | Config file | What it does |
|---|---|---|
| `protect-paths.sh` | `.claude/protected-paths.txt` (one glob per line) | Blocks Edit/Write to matching paths, Bash deletes (`rm`/`rmdir`/`shred`/`unlink` in the same command segment as a protected path, tokenized not regexed), and redirects onto them |
| `generated-file-guard.sh` | `.claude/generated-outputs.tsv` (`glob<TAB>generator<TAB>block\|warn`) | Routes edits of generator output back to the generator - a doc-only fix to a generated file survives exactly one rerun |
| `check_stale_counts.py` | `.claude/stale-counts.json` | Fails when prose asserts a number that disagrees with its declared source-of-truth command; a broken truth command aborts loudly rather than reporting clean. Not hook-wired - run it from `/validate` or CI |

## What it cannot ship, and the workaround

Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
Run **`/bootstrap-cc-setup`** once in a new repo: it writes a minimal `CLAUDE.md`
skeleton and a generic `workflow.md` rule (model-notes only), shows a diff before
touching anything that exists, and prints how to undo everything it wrote. It also
installs `hooks/pre-commit.sh` as the repository's native git pre-commit hook.
Installing the plugin alone does not install that git hook. Loam-rendered projects
already have their own harness and do not run this bootstrap skill.

## Honesty labels

- `unknowns` shipped 2026-08-02 with **zero usage evidence** at extraction time.
  It encodes published guidance, not proven local habit.
- Everything else ran in anger for weeks in the source repo.
- Removed in v0.3.0 (2026-08-14 teardown rulings): the sentinel gate family,
  `create-skill`, `mode-routing`, the `pr-review` agent, and
  `codebase-review-fanout` (never exercised end-to-end).
  (`techdebt` was later re-harvested and ships again as of v0.6.0.)

## Versioning

Semver in `.claude-plugin/plugin.json`. Behaviour changes (enforcement model, check
sets) bump minor at least - enforcement that silently changes across machines is
worse than none.

## The release loop

A reusable change follows the manual route in `docs/SYNC.md`.

1. Copy the reviewed asset into `cultivation/marketplace/sam-cc-setup/` or the
   bundle that owns it.
2. Record what changed and why in `cultivation/marketplace/UPGRADING.md`.
3. If plugin content changed, update its version in both the marketplace manifest
   and the plugin manifest. Keep the two values equal.
4. Run `python3 cultivation/marketplace/sam-cc-setup/hooks/test_check_stale_counts.py`
   and `python3 cultivation/marketplace/sam-cc-setup/hooks/test_protect_paths.py`.
   Require both control suites to pass.
5. Run `bin/verify-template.sh` from the Loam root. Require
   `verify-template: PASSED`.
6. Run `bin/release.sh <version>`. It verifies again before changing the top-level
   `VERSION`, then commits, tags, and pushes the release.
7. Installed plugin consumers run `/plugin update`. Copier consumers run
   `uvx copier update --trust` after the new tag exists.

## What a release bumps, and what it does not

`bin/release.sh` writes only the top-level `VERSION` file.
That file is the Copier template version.

It does not touch either per-plugin version field:

- `cultivation/marketplace/.claude-plugin/marketplace.json` carries a `version` for local plugins.
- Each plugin's own `.claude-plugin/plugin.json` carries its own `version`.

These plugin versions are maintained by hand. The repository contract tests require both
`sam-cc-setup` fields to be `0.5.0`. The top-level `VERSION` remains the independent
Copier template version.

### Before you run bin/release.sh

For every plugin whose content changed in this batch:

1. Bump its `version` in `cultivation/marketplace/.claude-plugin/marketplace.json`.
2. Bump the same `version` in that plugin's `.claude-plugin/plugin.json`.
3. Keep the two numbers equal.
4. Add the `UPGRADING.md` provenance line for the change.
5. Run both plugin control suites named in the release loop above.
6. Run `bin/verify-template.sh` and require `verify-template: PASSED`.
7. Then run `bin/release.sh <version>`.

A plugin whose content did not change keeps its current version.
Bumping a version that ships identical content misleads every consumer running `/plugin update`.
