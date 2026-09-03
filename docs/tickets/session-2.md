# Ticket: Session 2 - prompts to Fable 5.1

- Branch: `fix/audit-s2-prompts` (plugin edits may go direct to main; the seed `AGENTS.md.jinja` edit needs the branch)
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 2" block plus every Gap review and Research addition item tagged "session 2".
- Depends on: nothing. Session 1 is merged.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run SESSION 2 only, then stop.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 2's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s2-prompts (plugin edits may go direct to main).
You commit; workers never commit; do not push and do not open a PR. Update the Execution log when
done, then stop so the review can run in a fresh context. Please remove all mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 2 is implemented, the plugin edits are committed to main and the seed `AGENTS.md.jinja` edit is committed on `fix/audit-s2-prompts`, and this session's transcript shows `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", `bin/harness-smoke.sh` printed PASS, and the session 2 Verify grep returned only historical citations. No file outside the session 2 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

## Verify

- `grep -rn "Fable 5[^.]" cultivation/marketplace/sam-cc-setup | grep -v "5\.1"` returns only historical citations.
- Every `model:` line under `cultivation/marketplace/sam-cc-setup/agents` is an Opus or Fable id.
- Four checks green: `uvx pytest -q bin/tests`, `bin/verify-template.sh`, `bin/harness-smoke.sh`, and the session Verify grep.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=2 and branch `fix/audit-s2-prompts`.
It writes a SHIP / FIX / REWORK verdict to `docs/reviews/`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
