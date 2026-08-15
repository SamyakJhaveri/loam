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
