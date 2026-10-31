---
name: factory-watch
disable-model-invocation: true
description: "Read the factory's status once and report a run that stopped, a PR that opened, or a failing precondition. Use when you type /factory-watch for one read. Manual only, so a /loop fire cannot run it: to watch on a loop, type the plain prompt `/loop 30m run bin/factory status (bin/runner bin/factory status off the runner) and report only a run that stopped, a new pr-opened, or a new precondition FAIL since the last check`. Not for starting, stopping or merging a run: use bin/factory itself."
argument-hint: "[-C <repo> when the factory targets another repo]"
---

# factory-watch

**Trigger:** user types `/factory-watch`. Manual-only (`disable-model-invocation: true`).
It reads; it never starts, stops or merges a run, and never runs `bin/factory run`, `stop`, `merge` or `next`.

1. Run `bin/factory status` once, as one bare command from the factory's checkout on the runner, where the runs and the exports live.
   From any other host run `bin/runner bin/factory status`; otherwise the table is empty and the preconditions fail falsely.
   When `$ARGUMENTS` holds `-C <repo>`, run `bin/factory -C <repo> status` instead, with the runner's path for `<repo>` (a tilde quoted) through `bin/runner`.
2. Compare its output with the previous call in this session.
   A run has stopped when its status is anything but `running`, `waiting-limit` or `pr-opened`: `stopped*`, `stuck`, `no-change`, `ticket-defect`, `abandon` or another exit.
   On the first call there is none: print one line counting the runs by status (as in step 3), each stopped run, and each `FAIL` line under preconditions, and keep this output as the baseline.
   Something is new when a run stops, a run reaches `pr-opened`, or a `FAIL` line appears under preconditions.
3. Print one line per new thing, leading with the ticket and what the owner should do, and one line counting the runs by status.
   Print nothing else.

If the command fails, say so in one line with its exit code and stop; the next call tries again.
