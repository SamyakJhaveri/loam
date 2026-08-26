---
name: surprise-me
description: Generate ranked, evidence-backed creative ideas the user has not asked for, aimed at a named goal, then execute the cheapest one immediately as proof. Use when the user says "surprise me", "what am I missing", "creative or elegant ideas", "how can we do this better", asks how to increase the chances of a goal succeeding, or asks "what are we not seeing/doing/thinking about" or "what capabilities do you have that I am not asking you to use yet". NOT for routine task execution, and never for ideas that only sound good but the user cannot verify.
argument-hint: [the goal to optimize for, e.g. "ship the release on time"]
---

# Surprise Me - goal-directed creative leverage

You are an engineer hunting for high-leverage moves the current plan missed.
The output is a short ranked table of ideas plus one already-executed proof, never a brainstorm essay.

## Process

1. **Fix the goal and the judge.** Restate, in one sentence, the external decision rule that
   defines success (the reviewer, the metric, the deadline, the acceptance criterion). Every idea
   is scored against that sentence, nothing else.
2. **Inventory what already exists before inventing anything.** Grep the repo, the data files, and
   the sources for dormant capabilities: disabled self-checks, unused flags, data already collected
   but never aggregated, tools pointed at the wrong target. The inventory includes the AGENT'S own
   unused capabilities the owner has not asked for yet (scheduled monitors, browser verification of
   rendered pages, multi-agent document QA, published dashboards, cross-model review panels) - list
   the ones that serve the goal, each as a concrete offer with a cost. When the work belongs to
   another session's plan, target that plan for the step-7 filing rather than leaving
   the ideas only in chat. The best surprises are
   recombinations of assets already on disk.
3. **Generate only ideas the judge can verify.** An idea that requires the reader to trust us is
   worth less than one they can re-run. Prefer: quoting reproducible evidence verbatim, running a
   control experiment, machine-deriving a statistic, reframing existing facts. Reject: adjectives,
   promises without dates, anything that tunes an instrument toward the desired outcome.
4. **Check each idea against any policy or freeze line.** Mark it "do now" (tooling/framing side) or
   "commit for later" (frozen-artifact side, e.g. after a freeze lifts). An idea on the wrong side
   of the line becomes a named commitment, not an action.
5. **Rank by goal-value per unit cost** and present as a table: `# | idea | when | owner | cost | deliverable`.
   Three to six ideas; kill the rest.
6. **Execute the cheapest read-only idea in the same turn** (a grep sweep, a framing sentence, a
   control run in a scratch dir) and report its first result alongside the table. Proof beats proposal.
7. **File the survivors.** Propose appending the table to the project's active plan document so the
   ideas outlive the session, each with when/owner/cost/deliverable filled in; the append itself
   waits for the owner's go (critical rule 3).

## Scale modes

- **Solo (default):** the 7-step process above, one context. Right for a daily "what am I missing".
- **Panel (wide or high-stakes decisions):** fan out 3 fresh-context agents with deliberately
  different lenses - a dormant-assets hunter (step 2 only), a reframing hunter (same facts, stronger
  story), and an adversary (attacks the current plan and proposes what its holes imply) - then merge,
  dedupe, and rank their ideas yourself.

## Before spending on a winner

An idea costing more than ~1 hour must, before execution: (a) carry a measurable success criterion
written down in advance ("byte-identical output or it changed nothing"), and (b) survive an
adversarial pass - run an interrogation of the idea (e.g. the `grill-research` skill if available)
rather than re-implementing interrogation here.

## Critical rules

1. Never manufacture an idea that moves a number by choosing what to measure - ideas must survive an
   adversarial reader. This is the canonical anti-tuning rule; step 3 and the pre-spend gate point here.
2. For measurement or audit projects, phrase the goal as validity or credibility ("a defensible
   result"), never as a metric's direction ("a lower error rate") - the second corrupts step 3 silently.
3. Experiments that consume real resources and any mutation of a shared plan document need the owner's go;
   only the one cheap read-only proof in step 6 runs unprompted.
4. Every claimed fact in an idea's pitch traces to a command run this session.
5. Respect the repo's hard invariants (immutable results, protected sources, signed artifacts) -
   creative means recombining, not bending.
6. Scale is 3-6 ideas; if more survive ranking, merge or cut. One executed proof is mandatory.
7. If the goal is ambiguous, ask one question to pin the judge before generating anything.

Use `$ARGUMENTS` as the goal; if empty, default to the project's nearest deadline or active
objective.
