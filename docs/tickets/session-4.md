# Ticket: Session 4 - new hooks

- Branch: `fix/audit-s4-hooks`
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 4" block plus every Gap review and Research addition item tagged "session 4". All hooks go under `seed/.claude/hooks/`, each wired in `seed/.claude/settings.json`, added to `CLAUDE_HOOK_ROUTES` in the contract, and covered by a test.
- Depends on: nothing.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run SESSION 4 only, then stop.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 4's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s4-hooks. You commit; workers never commit; do
not push and do not open a PR. Update the Execution log when done, then stop so the review can run
in a fresh context. Please remove all mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 4 is implemented and committed on `fix/audit-s4-hooks`, each new hook is wired in `seed/.claude/settings.json`, added to `CLAUDE_HOOK_ROUTES` in the contract, and covered by a test, and this session's transcript shows each new hook run against a synthetic stdin envelope with the expected output, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 4 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

## Verify

- Each new hook run against a synthetic stdin envelope prints the expected output.
- Each new hook is in `CLAUDE_HOOK_ROUTES` and has a test in `bin/tests/test_seed_claude_hooks.py`.
- Four checks green.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=4 and branch `fix/audit-s4-hooks`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
