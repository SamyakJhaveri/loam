# Harness notes for Loam only

`seed/docs/HARNESS.md.jinja` ships to every generated project, so facts that hold only for the Loam repository or its owner's machines live here.
Token figures are byte counts divided by four, not a tokenizer result.

## Skill-listing budget

Loam's `bin/check` pins the `seed` and `sam-cc-setup` listing weights in its skill-listing step; that line is the one home for each number.
The step fails over and under each budget (#313), so a PR that shrinks a listing lowers its budget, and one that grows it raises the budget and says why.
It rose from 448 to 565 on 2026-09-09 (a4f61fa) when `plan-review` became model-invocable, and to 634 the same day (5af0946) when the judge and reviewer became plugin agents.
A rendered project's `bin/check` asserts no listing budget.

## The owner's memory-store remote

On the owner's machines the store remote uses the ssh alias `jhaveris`, the same alias `bin/runner` uses:

    git -C ~/memstore remote add origin jhaveris:memstore.git

## Sandbox exclusions in Loam's own sessions

Loam's own sessions run `gh` outside the sandbox too, because the root `.claude/` links to `seed/.claude/`, so the seed's `sandbox.excludedCommands` applies here.

## Claude Code gotchas for hook and rule authors

- Hooks receive a JSON envelope on standard input. They do not receive a `CLAUDE_TOOL_NAME` environment variable.
- Hook event and matcher names are exact. A wrong name fails silently.
- A rule's `paths:` frontmatter fires when Claude reads a matching file, not when Claude writes one.

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
