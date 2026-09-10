# size-large: a large ticket lint accepts
Brief:
Give lint a contract-form body whose Worker block sets size: large.
Where: bin/factory (check_worker).
Done means: bin/factory lint accepts this body.
Out of scope: anything the loop does with the body.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Prove the F12 lint change accepts a Worker `size: large` line, the positive half of the size fixture pair.

## Do not touch
The standing list.

## Out of scope
Any change to the loop.

## Done checks
```done-checks
true && pass placeholder || fail placeholder "this fixture is lint-only and never runs"
```

## Worker
worker: claude
codex-review: no
effort: medium
size: large
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/CONTRACT.md
