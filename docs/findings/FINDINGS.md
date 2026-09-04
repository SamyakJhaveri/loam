# Findings

One row per verified review finding that was not fixed in the session that found it.
A row closes when the fixing commit lands: keep the row and fill the closing commit.
Sources: Codex second opinions, plan reviews, fresh-context session reviews.
The codex-review skill appends here.

| Date | Source | Severity | Path:line | Finding | Status | Closing commit |
|------|--------|----------|-----------|---------|--------|----------------|
| 2026-09-03 | session 1 Execution log, docs/HANDOFF-2026-09-03-audit-sessions.md | Low | seed/.claude/hooks/stop-verify-gate.sh:83 | stop-verify-gate probes ruff with --version instead of the ruff-after-edit fallback pattern | open, owner session 4 | - |
| 2026-09-03 | session 2 fresh-context review, docs/reviews/2026-09-03-session-2-review.md | Low | cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md:177 | the writing-plans handoff line routes every fresh-session plan through fable-plan and has no Opus 4.8 branch | open | - |
