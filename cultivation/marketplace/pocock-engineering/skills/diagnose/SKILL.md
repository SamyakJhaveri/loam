---
name: diagnose
description: >
  Six-phase hard-bug diagnostic discipline. Phase 1 (build a feedback loop) is
  the skill — everything else consumes that signal. Use for bugs that resist
  simple reproduction or have non-obvious root causes.
  NOT for: simple test failures with obvious fixes (use /fix-bug),
  feature work, or refactoring.
auto-activate: false
---

# Diagnose

A discipline for hard bugs. Skip phases only when explicitly justified.

When exploring the codebase, check the project's domain glossary (`DOMAIN.md` if it exists) and any ADRs in the area you're touching.

## Phase 1: Build a Feedback Loop

**This is the skill.** If you have a fast, deterministic, agent-runnable pass/fail signal for the bug, you will find the cause. If you don't, no amount of staring at code will help.

Spend disproportionate effort here. Be aggressive. Be creative. Refuse to give up.

### Strategies — try in roughly this order

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e
2. **Curl / HTTP script** against a running dev server
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network
5. **Replay a captured trace** — save a real request/payload/event log; replay through the code path in isolation
6. **Throwaway harness** — spin up a minimal subset of the system that exercises the bug path with a single function call
7. **Property / fuzz loop** — run 1000 random inputs and look for the failure mode
8. **Bisection harness** — automate "boot at state X, check, repeat" for `git bisect run`
9. **Differential loop** — run the same input through old vs new version, diff outputs
10. **HITL script** — last resort. If a human must click, structure the loop so captured output feeds back to you

### Iterate on the loop itself

Treat the loop as a product:
- Can you make it faster? (Cache setup, skip unrelated init, narrow scope)
- Can you make the signal sharper? (Assert on the specific symptom, not "didn't crash")
- Can you make it more deterministic? (Pin time, seed RNG, isolate filesystem)

A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

### Non-deterministic bugs

The goal is a higher reproduction rate, not a clean repro. Loop the trigger 100x, parallelise, add stress, narrow timing windows. A 50%-flake is debuggable; 1% is not.

### When you cannot build a loop

Stop and say so explicitly. List what you tried. Ask for: (a) access to the reproducing environment, (b) a captured artifact (HAR file, log dump, screen recording), or (c) permission for temporary production instrumentation. Do NOT proceed without a loop.

## Phase 2: Reproduce

Run the loop. Watch the bug appear. Confirm:

- The failure matches what the **user** described — not a different nearby failure
- It is reproducible across multiple runs (or at a high enough rate to debug)
- You have captured the exact symptom so later phases can verify the fix

## Phase 3: Hypothesise

Generate **3-5 ranked hypotheses** before testing any. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**:
> "If X is the cause, then changing Y will make the bug disappear / changing Z will make it worse."

Show the ranked list to the user before testing. They often have domain knowledge that re-ranks instantly. Don't block on it — proceed if the user is AFK.

## Phase 4: Instrument

Each probe maps to a specific prediction from Phase 3. Change one variable at a time.

Tool preference:
1. Debugger / REPL inspection if the env supports it
2. Targeted logs at the boundaries that distinguish hypotheses
3. Never "log everything and grep"

Tag every debug log with a unique prefix (e.g., `[DEBUG-a4f2]`). Cleanup becomes a single grep.

## Phase 5: Fix + Regression Test

Write the regression test **before** the fix — but only if a correct seam exists. A correct seam exercises the real bug pattern as it occurs at the call site.

If no correct seam exists, that itself is the finding — the architecture is preventing the bug from being locked down.

1. Turn the minimised repro into a failing test
2. Watch it fail
3. Apply the fix
4. Watch it pass
5. Re-run the Phase 1 feedback loop against the original scenario

## Phase 6: Cleanup + Post-Mortem

Before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (grep the prefix)
- [ ] Throwaway harnesses deleted
- [ ] The correct hypothesis is stated in the commit/PR message
- [ ] Run `/validate` before committing (Pipeline Gate)

Then ask: **what would have prevented this bug?** If the answer involves architectural change, hand off to `/improve-codebase-architecture` with specifics.
