# Live fixture: a worker call killed by CALL_TIMEOUT_SEC

Brief: prove the `stopped-environment` exit. The check below fails on base, so round 0 passes; `CALL_TIMEOUT_SEC=2` then kills the first worker call before it can emit a result event, and the run must end `stopped-environment` with no `round-1.*` file.
Where: nothing; this ticket asks for no change.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Give `bin/factory run` a call it cannot finish. A call with no result event is the environment, not a round, so it counts no round and leaves no round file behind.

## Do not touch
Everything. This ticket changes no file.

## Out of scope
Any edit at all.

## Done checks
```done-checks
[ -e .factory-hang-fixture-never-exists ] && pass never-true || fail never-true "absent by design, so round 0 passes and the worker call happens"
```

## Worker
worker: claude
codex-review: no
effort: xhigh
CALL_TIMEOUT_SEC=2
goal: unreachable; the first call is killed at two seconds, or stop after 1 turns

## Decisions
docs/factory/LOOP.md, Exits; decision ticket: How F1's done checks prove a live run without a loop inside a loop (#D10)
