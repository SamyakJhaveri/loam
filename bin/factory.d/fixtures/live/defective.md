# Live fixture: a ticket whose only check passes on base

Brief: prove the `ticket-defect` exit. Round 0 runs this block on `base.sha`; the check below is already true there, so the run must end `ticket-defect` before any model call.
Where: nothing; this ticket asks for no change.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Give `bin/factory run` a ticket it must refuse. A check that passes on base cannot prove anything, so round 0 exits `ticket-defect` and no model is called.

## Do not touch
Everything. This ticket changes no file.

## Out of scope
Any edit at all.

## Done checks
```done-checks
[ -f README.md ] && pass readme-exists || fail readme-exists "no README.md at the repository root"
```

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: unreachable; round 0 refuses this ticket, or stop after 1 turns

## Decisions
docs/factory/LOOP.md step 4; decision ticket: How F1's done checks prove a live run without a loop inside a loop (#D10)
