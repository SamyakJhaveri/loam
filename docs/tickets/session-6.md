# Ticket: Session 6 - research and autonomy layer

- Branch: `fix/audit-s6-research`
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 6" block plus every Gap review and Research addition item tagged "session 6".
- Depends on: best run last. After it, the harness-evals idea is the next session.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run SESSION 6 only, then stop.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 6's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s6-research. You commit; workers never commit; do
not push and do not open a PR. For the item-1 dry run, run the inner /goal as a headless
`claude -p "/goal ..."` invocation (only one interactive goal is active per session). Update the
Execution log when done, then stop so the review can run in a fresh context. Please remove all
mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 6 is implemented and committed on `fix/audit-s6-research`, and this session's transcript shows the item-1 dry run (a contract with done-when `test -f results/demo.jsonl` ended a headless `/goal` loop within 5 turns), each new hook run against a synthetic envelope with the expected output, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 6 items is changed; do not push or open a PR. Or stop after 40 turns and say what is left.

## Verify

- The item-1 dry run shows a contract with done-when `test -f results/demo.jsonl` ended a headless `/goal` loop within 5 turns.
- Each new hook run against a synthetic envelope prints the expected output.
- Four checks green.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=6 and branch `fix/audit-s6-research`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
