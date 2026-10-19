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

## Daily verify-loam upkeep

`bin/verify-loam-daily` clones origin/main and runs `/pstack:maintain-verification-skill` on verify-loam with `claude -p` in auto permission mode.
It never pushes; a `changed` outcome stays on a local `verify/maintain-<stamp>` branch in the run's clone, under `~/.local/state/loam/evidence/verify-daily/<stamp>/`, with `result.json`, `report.md` and the stream-json transcript.
`--probe` checks claude, login and pstack at $0.
The owner's Mac runs it daily at 06:00 from `~/Library/LaunchAgents/com.samyakjhaveri.verify-loam-daily.plist`, whose `EnvironmentVariables` PATH names the toolchain `claude`, `uvx` and Homebrew.
Load it with `launchctl bootstrap gui/$(id -u) <plist>`; read the last run with `launchctl print gui/$(id -u)/com.samyakjhaveri.verify-loam-daily | grep 'last exit'`.
