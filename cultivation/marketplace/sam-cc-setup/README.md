# sam-cc-setup

The portable core of Sam's Claude Code setup, extracted from a research repo where every
piece earned its place in production use (except two, flagged below).

**Audience:** existing repos on any machine that were NOT bootstrapped with the
[Loam](https://github.com/SamyakJhaveri/loam) Copier template.
A Loam-rendered project already carries most of these assets in its own `.claude/` -
installing this plugin there would duplicate skill names.

## What installing it gives you, immediately

- **The Pipeline Gate.** A `PreToolUse` hook blocks any `git commit` until `/validate`
  has passed and written a fresh `.validation_passed` sentinel.
  The commit detector (`hooks/gate_detect.py`) survived five adversarial review rounds
  on 2026-08-02; its 72-case test suite (`hooks/test_pre_commit_gate.py`) documents every
  bypass class found and the four accepted gaps.
  A `PostToolUse` hook deletes the sentinel on any edit, forcing re-validation.
  Note: this plugin's gate requires `waves_passed>=2` (the two-wave LLM-free `/validate`
  it ships); the upstream research repo runs a four-wave variant.
- **A concurrent-checkout guard** that blocks two sessions from racing on one working tree.
- **Skills:** `validate` (two-wave gate front door), `codex-review` and `codex-plan-review`
  (cross-model second opinions - require the Codex CLI), `create-skill`, `techdebt`,
  `reflect`, `sam_handoff`, `mode-routing`, `unknowns`, `bootstrap-cc-setup`.
- **Agents:** `diff-reviewer`, `security-scanner`, `code-simplifier`, `consistency-checker`,
  `test-synthesizer`, `self-critic`, `pr-review`, `code-architect`, `build-validator`,
  `read-only`.
- **Workflows:** `plan-review-fanout` (grounded adversarial plan review),
  `codebase-review-fanout` (multi-lens code review).

## What it cannot ship, and the workaround

Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
Run **`/bootstrap-cc-setup`** once in a new repo: it writes a minimal `CLAUDE.md`
skeleton and a generic `workflow.md` rule (model-notes only), shows a diff before
touching anything that exists, and prints how to undo everything it wrote.

## Honesty labels

- `mode-routing` and `unknowns` shipped 2026-08-02 with **zero usage evidence** at
  extraction time. They encode published guidance, not proven local habit.
- `codebase-review-fanout` was un-exercised end-to-end as of 2026-06-22.
- Everything else ran in anger for weeks in the source repo.

## Versioning

Semver in `.claude-plugin/plugin.json`. Behaviour changes (gate thresholds, detector
rules) bump minor at least - a gate that silently changes across machines is worse
than none.
