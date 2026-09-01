---
name: techdebt
description: Inventory tech debt across the codebase - duplicated logic, dead code, magic numbers, deep nesting, TODO/FIXME rot - as a report of locations + suggested actions, not auto-applied fixes. Use when you want a broad debt sweep. NOT for applying fixes to just-changed code (use the built-in /simplify) and NOT for reviewing a specific diff or PR (use /code-review).
model: opus
allowed-tools: [Read, Grep, Glob, Bash(*)]
---

# Tech-debt inventory

Produce a **report** of tech debt - locations + suggested actions, not
auto-applied fixes. (For fixes to just-changed code use the built-in
`/simplify`.)

## Scope
Default to a **whole-tree** sweep - this is the broad-inventory skill. To scope
to recent work instead, use `git diff --name-only main...HEAD`. Do NOT run
`git diff --name-only HEAD~5` blindly: it errors on a branch with fewer than 5
commits - fall back to `main...HEAD`, then to a whole-tree scan.

## Scan - one pass per debt class
1. **Duplicated logic** - Grep for repeated blocks/signatures; propose a shared helper.
2. **Dead code** - Glob the module tree; Grep each unused-looking import/function to confirm zero references before flagging.
3. **Magic numbers/strings** - Grep for bare literals in logic; propose named constants.
4. **Deep nesting (>3 levels)** - flag for an early-return refactor.
5. **TODO/FIXME/XXX rot** - list (with age if cheap); never auto-fix.

## Output - one table
| Location (file:line) | Class | Suggested action |
|----------------------|-------|------------------|

This skill reports; it does not edit. Hand the table back to the user and let
them choose what to act on. If they approve a set of fixes, apply them outside
this skill, then run the project's linter/type checker (`/validate` Wave 1) to
confirm no regressions.
