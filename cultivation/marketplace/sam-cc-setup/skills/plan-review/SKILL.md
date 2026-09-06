---
name: plan-review
description: >
  Run the merged blind plan review (correctness checklist + elegance gate in one
  agent) on a plan, spec, or design doc before execution. Accepts the artifact
  path as the argument. Use in a fresh session on a plan authored earlier, or
  before executing any non-trivial or hard-to-reverse plan. Use the parallel
  multi-lens version only for named security, architecture, or cross-system risks.
  NOT for: reviewing shipped code or
  diffs (use /code-review), or reviews where the author's rationale must be
  weighed (this flow deliberately withholds it).
argument-hint: <path-to-plan>
---

# plan-review

Invokes the merged `plan-reviewer` agent (`agents/plan-reviewer.md`) BLIND.
The agent carries the whole contract itself: honesty bounds, surface enumeration, grounding, the 7-point checklist, the elegance gate, bounded findings with a coverage ledger, and the revised handoff plan.
This skill only builds a clean blind prompt and handles the result.

The one rule that makes it work: the reviewer must not see the author's reasoning.
A reviewer that recognizes the author's rationale rates the work higher, so the isolation must be structural.

## Steps

1. Resolve `$ARGUMENTS` to the artifact path. If empty, ask which plan; never guess.
2. Record the artifact's content fingerprint. Reuse an existing durable report when that
   fingerprint and the review criteria are unchanged.
3. Build the agent prompt with ONLY:
   - the artifact path to read;
   - the hard constraints the solution must satisfy, stated as bare facts (settled rulings, budget, deadlines);
   - pointers to the criteria or rules files the review should judge against.
   NEVER include: why the approach was chosen, the planning conversation, prior review verdicts, or your own opinion of the artifact.
4. Spawn one `plan-reviewer` agent with that prompt. It does not rerun an unchanged full
   suite. A focused check needs a named evidence gap.
5. Save the report with the content fingerprint. Write the revised handoff plan next to
   the original, present the findings and verdict, and surface every deferred decision.
6. On REJECT there is no revised plan. Present the findings and stop.
