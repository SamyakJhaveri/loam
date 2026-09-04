# Findings

One row per verified review finding that was not fixed in the session that found it.
A row closes when the fixing commit lands: keep the row and fill the closing commit.
Sources: Codex second opinions, plan reviews, fresh-context session reviews.
The codex-review skill appends here.

| Date | Source | Severity | Path:line | Finding | Status | Closing commit |
|------|--------|----------|-----------|---------|--------|----------------|
| 2026-09-03 | session 1 Execution log, docs/HANDOFF-2026-09-03-audit-sessions.md | Low | seed/.claude/hooks/stop-verify-gate.sh:83 | stop-verify-gate probes ruff with --version instead of the ruff-after-edit fallback pattern | closed | 5aee49a |
| 2026-09-03 | session 2 fresh-context review, docs/reviews/2026-09-03-session-2-review.md | Low | cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md:177 | the writing-plans handoff line routes every fresh-session plan through fable-plan and has no Opus 4.8 branch | open | - |
| 2026-09-03 | session 3 fresh-context review, docs/reviews/2026-09-03-session-3-review.md | Low | cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js:162-170,198-199,227 | every agent call stays at effort high while "workers at xhigh everywhere" is a binding decision; set xhigh when the workflow is next touched | closed | e8df75d |
| 2026-09-03 | session 3 fresh-context review, docs/reviews/2026-09-03-session-3-review.md | Low | cultivation/marketplace/sam-cc-setup/agents/build-validator.md:37-38 | the collection log is hardcoded to /tmp/collect.log, so two validators in parallel worktrees overwrite each other; use mktemp | open | - |
| 2026-09-03 | session 3 fresh-context review, docs/reviews/2026-09-03-session-3-review.md | Low | cultivation/marketplace/sam-cc-setup/agents/build-validator.md:28-30 | lint runs uv run ruff check whenever pyproject.toml exists, so a project whose pyproject does not declare ruff gets a spawn error and FAIL instead of SKIP | open | - |
| 2026-09-03 | session 3 fresh-context review, docs/reviews/2026-09-03-session-3-review.md | Low | cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md:76 | when /ship runs on the default branch the docs-only test is vacuously true, stage 4 is skipped, and the commit is never pushed; add "if HEAD is the default branch, push and skip the PR" | open | - |
| 2026-09-03 | session 3 fresh-context review, docs/reviews/2026-09-03-session-3-review.md | Low | cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md:3,45 | the skill is still described as deterministic but now spawns an Opus 4.8 agent on every run; say so in UPGRADING.md so consumers know /validate is no longer model-free | open | - |
| 2026-09-04 | session 4 fresh-context review, docs/reviews/2026-09-04-session-4-review.md | Low | seed/.codex/rules/default.rules:63-68 | `git push --force-if-includes` alone is a git no-op; the rule's justification says the pre-tool hook blocks it, but pre-tool-policy.py allows it | open | - |
| 2026-09-04 | session 4 fresh-context review, docs/reviews/2026-09-04-session-4-review.md | Low | seed/.claude/hooks/bash-audit-log.sh:61 | multi-line commands carry their newlines into the log; about two thirds of live log lines are command fragments; write embedded newlines as the two characters `\n` | open | - |
| 2026-09-04 | session 4 fresh-context review, docs/reviews/2026-09-04-session-4-review.md | Low | seed/.claude/hooks/harness-hygiene.sh:52,136 | only inline backtick spans are scanned; fenced code blocks and single-token backticked commands are never checked | open | - |
| 2026-09-04 | session 4 fresh-context review, docs/reviews/2026-09-04-session-4-review.md | Low | bin/tests/test_seed_claude_hooks.py:936,996,1093,1111,1304,1364 | cwd-field tests set cwd to the hook's own directory so they cannot fail; nothing asserts the cosmic-ray config the gate writes; `_payload`/`_stage` duplicated across two classes | open | - |
