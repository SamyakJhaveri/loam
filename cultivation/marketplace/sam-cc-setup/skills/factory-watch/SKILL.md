---
name: factory-watch
disable-model-invocation: true
description: "Read the factory's status once and report a run that stopped, a PR that opened, or a failing precondition. Use when you type /factory-watch, usually as /loop 30m /sam-cc-setup:factory-watch. Manual only. Not for starting, stopping or merging a run: use bin/factory itself."
argument-hint: "[-C <repo> when the factory targets another repo]"
---

# factory-watch

**Trigger:** user types `/factory-watch`. Manual-only (`disable-model-invocation: true`).
It reads; it never starts, stops or merges a run, and never runs `bin/factory run`, `stop`, `merge` or `next`.

1. Run `bin/factory status` once, as one bare command from the factory's checkout.
   When `$ARGUMENTS` holds `-C <repo>`, run `bin/factory -C <repo> status` instead.
2. Compare its output with the previous call in this session.
   Something is new when a run's status starts with `stopped`, a run reaches `pr-opened`, or a `FAIL` line appears under preconditions.
3. Print one line per new thing, leading with the ticket and what the owner should do, and one line counting the runs by status.
   Print nothing else.

If the command fails, say so in one line with its exit code and stop; the next call tries again.
