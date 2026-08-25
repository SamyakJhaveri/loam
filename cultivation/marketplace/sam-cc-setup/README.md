# sam-cc-setup

The portable core of Sam's Claude Code setup, extracted from a research repo where every
piece earned its place in production use (except two, flagged below).

**Audience:** existing repos on any machine that were NOT bootstrapped with the
[Loam](https://github.com/SamyakJhaveri/loam) Copier template.
A Loam-rendered project already carries most of these assets in its own `.claude/` -
installing this plugin there would duplicate skill names.

## What installing it gives you, immediately

- **Native pre-commit enforcement.** `/bootstrap-cc-setup` installs a plain git
  pre-commit hook (`hooks/pre-commit.sh`, symlinked at `.git/hooks/pre-commit`) that
  runs fast deterministic checks on every commit. The earlier sentinel-based Pipeline
  Gate (`PreToolUse` hook + `.validation_passed` sentinel) was retired 2026-08-14: it
  blocked every commit until a sentinel matched, which fought the tool; a native hook
  runs inside git, where no compound command can outrun it.
- **A concurrent-checkout guard** that blocks two sessions from racing on one working tree.
- **Skills:** `validate` (on-demand two-wave deterministic pass), `codex-review` and
  `codex-plan-review` (cross-model second opinions - require the Codex CLI),
  `reflect`, `sam_handoff`, `unknowns`, `bootstrap-cc-setup`.
- **Agents:** `diff-reviewer`, `security-scanner`, `code-simplifier`, `consistency-checker`,
  `test-synthesizer`, `self-critic`, `code-architect`, `build-validator`,
  `read-only`, plus two baseline-driven skeletons: `verify-app` and `regression-checker`
  read their expected values from a repo-local `.claude/baselines.json` and report
  NO-BASELINE rather than inventing numbers when it is absent.
- **Workflows:** `plan-review-fanout` (grounded adversarial plan review).

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
touching anything that exists, and prints how to undo everything it wrote.

## Honesty labels

- `unknowns` shipped 2026-08-02 with **zero usage evidence** at extraction time.
  It encodes published guidance, not proven local habit.
- Everything else ran in anger for weeks in the source repo.
- Removed in v0.3.0 (2026-08-14 teardown rulings): the sentinel gate family,
  `create-skill`, `mode-routing`, `techdebt`, the `pr-review` agent, and
  `codebase-review-fanout` (never exercised end-to-end).

## Versioning

Semver in `.claude-plugin/plugin.json`. Behaviour changes (enforcement model, check
sets) bump minor at least - enforcement that silently changes across machines is
worse than none.

## The release loop

A change earns its place in the hub through a fixed loop.

1. **Sync a batch from a project.**
   Run `bin/agent-sync.sh scan` from a project with `.claude/` work worth keeping.
   Approve the files that should travel; the scan commits them into the hub.
2. **Run the hub checks.**
   Run `bin/hub-ci.sh` from the hub root: the hub promotion gate.
   It requires `shellcheck` and `copier` (or `uvx`) on the machine: `verify-template.sh` silently skips those checks when they are absent, and the gate refuses a skipped check, so a box without them cannot pass the gate at all.
   It runs three checks every time and prints one OK or FAIL line for each:
   `bin/verify-template.sh` (renders both Copier flavors, seed skill lint, schema),
   every hub hook test found under `cultivation/marketplace/sam-cc-setup/**/test_*.py` (discovered, not hardcoded, each run as `python3 <file>`),
   and `bin/lint-skill-descriptions.sh marketplace`.
   The third check is warn-only: marketplace holds third-party vendored skills, so its warnings are surfaced with a count but do not fail the gate; only a linter that dies before its `Total warnings: N` completion marker hard-fails.
   The gate runs all three even when one fails, and exits nonzero if any required check failed.
   `bin/hub-ci.sh` is runnable standalone, and `bin/release.sh` calls it in pre-flight, after the tag-exists check and before the `VERSION` write, so a red gate refuses the release with nothing left behind.
3. **Record why the change traveled.**
   Add one line to `cultivation/marketplace/UPGRADING.md` (see its provenance rule).
4. **Cut the release.**
   Run `bin/release.sh <version>`.
   It updates the top-level `VERSION` file, commits and tags under the public identity, and pushes.
5. **Consumers update.**
   A repo that installed these plugins from the marketplace runs `/plugin update`.
   A repo rendered from the Copier template re-renders with the tag `release.sh` prints:
   `copier copy --trust --vcs-ref vX.Y.Z gh:samyakjhaveri/loam ./my-project`.

## What a release bumps, and what it does not

`bin/release.sh` writes only the top-level `VERSION` file.
That file is the Copier template version.

It does not touch either per-plugin version field:

- `cultivation/marketplace/.claude-plugin/marketplace.json` carries a `version` per plugin (present on 7 of the 12 plugins).
- each plugin's own `.claude-plugin/plugin.json` carries its own `version`.

These plugin versions are maintained by hand today.
Nothing checks that they agree with each other, with `VERSION`, or with what actually changed.
Do not read this section as describing a gate: there is none.

Observed drift at the time of writing:
`VERSION` is `1.1.0`,
`UPGRADING.md` banners "marketplace v1.2.0",
and `sam-cc-setup` is `0.3.0` in both `marketplace.json` and its `plugin.json`.
This is recorded as an open item for the maintainer, not reconciled here.

The drift traces to a bypass, not a forgotten field.
The `v1.2.0` release did not go through `bin/release.sh`.
The tag objects show it:

```
git for-each-ref --format='%(refname:short) %(objecttype)' refs/tags
v1.0.0 tag
v1.1.0 tag
v1.2.0 commit
```

`release.sh` creates annotated tags (`git tag -a`), which are `tag` objects.
`v1.2.0` points straight at a `commit`: it is a lightweight tag, which `release.sh` cannot produce.
So `VERSION` still reads `1.1.0` because the script that writes it was never run for `v1.2.0`.
Nothing detects a bypass: the checklist below helps only someone who actually runs `release.sh`.

### Before you run bin/release.sh

For every plugin whose content changed in this batch:

1. Bump its `version` in `cultivation/marketplace/.claude-plugin/marketplace.json`.
2. Bump the same `version` in that plugin's `.claude-plugin/plugin.json`.
3. Keep the two numbers equal.
4. Add the `UPGRADING.md` provenance line for the change.
5. Run `bin/hub-ci.sh`.
6. Then run `bin/release.sh <version>`.

A plugin whose content did not change keeps its current version.
Bumping a version that ships identical content misleads every consumer running `/plugin update`.
