# Ticket: Session 3 - review consolidation

- Branch: `fix/audit-s3-reviews` (plugin edits may go direct to main; the weight-gate rebaseline touches `bin/`)
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 3" block plus every Gap review and Research addition item tagged "session 3".
- Depends on: nothing hard. If run before session 2, skip the critique-swarm edit in session 2 item 5.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run SESSION 3 only, then stop.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 3's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s3-reviews (plugin edits may go direct to main).
You commit; workers never commit; do not push and do not open a PR. Update the Execution log when
done, then stop so the review can run in a fresh context. Please remove all mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 3 is implemented and committed (plugin edits direct to main where allowed, the weight-gate rebaseline on `fix/audit-s3-reviews`), and this session's transcript shows `python3 bin/skill_listing_weight.py` printed the new rebaselined total, `grep -rniI critique-swarm cultivation/marketplace/sam-cc-setup` returned nothing, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 3 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

## Verify

- `python3 bin/skill_listing_weight.py` prints the new rebaselined total.
- `grep -rniI critique-swarm cultivation/marketplace/sam-cc-setup` returns nothing (skill deleted; the `cultivation/marketplace/UPGRADING.md` changelog line stays and is out of scope).
- Four checks green.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=3 and branch `fix/audit-s3-reviews`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
