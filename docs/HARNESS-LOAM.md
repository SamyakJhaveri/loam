# Harness notes for Loam only

`seed/docs/HARNESS.md` ships to every generated project, so facts that hold only for the Loam repository or its owner's machines live here.
Token figures are byte counts divided by four, not a tokenizer result.

## Skill-listing budget

Loam's `bin/check` asserts the `sam-cc-setup` plugin listing weight against the `LISTING_BUDGET` default in its skill-listing step; that default is the one home for the number.
Lower it when the listing shrinks; never raise it without saying why.
It rose from 448 to 565 on 2026-09-09 (a4f61fa) when `plan-review` became model-invocable, and to 634 the same day (5af0946) when the judge and reviewer became plugin agents.
A rendered project's `bin/check` asserts no listing budget.

## The owner's memory-store remote

On the owner's machines the store remote uses the ssh alias `jhaveris`, the same alias `bin/runner` uses:

    git -C ~/memstore remote add origin jhaveris:memstore.git

## Measured cost, v2.3.0 to v3.0.0

A record of the v3.0.0 cut, not maintained.
Rendered-project rows were measured in a `copier copy` render of each version; repo-side rows in the repo itself.

| Row | Before (v2.3.0) | After (v3.0.0) |
|---|---|---|
| Hooks shipped in `.claude/hooks/` | 15 | 2 |
| `PreToolUse` hook entries matching Bash | 7 | 0 |
| Hook runs per Edit or Write | 1 ruff run | 0 |
| Always-on prose bytes (`CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
| Check wall time, one script | 207 s (`bin/verify-template.sh`) | 5 s local, 7 s in CI |
| Seed hook and lib lines | 2309 | 71 |
| `bin/` plus `bin/tests/` lines | 11377 | 1525 |
| Marketplace skills shipped | 26 | 3 |
