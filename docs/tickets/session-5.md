# Ticket: Session 5 - repair sync and promote inventions

- Branch: `fix/audit-s5-sync`
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 5" block plus every Gap review and Research addition item tagged "session 5".
- Depends on: nothing hard. Do NOT edit distbench; only add an archive note.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run SESSION 5 only, then stop.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 5's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s5-sync. You commit; workers never commit; do not
push and do not open a PR. Update the Execution log when done, then stop so the review can run in a
fresh context. Please remove all mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 5 is implemented and committed on `fix/audit-s5-sync`, distbench itself is not edited, and this session's transcript shows `python3 bin/agent_parity/parity.py check` printed green, the attach-mode test output is pasted, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 5 items is changed; do not push or open a PR. Or stop after 35 turns and say what is left.

## Verify

- `python3 bin/agent_parity/parity.py check` prints green.
- The attach-mode test output (`bin/loam-attach.sh` on a test dir, a hook firing) is pasted.
- distbench is not edited.
- Four checks green.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=5 and branch `fix/audit-s5-sync`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
