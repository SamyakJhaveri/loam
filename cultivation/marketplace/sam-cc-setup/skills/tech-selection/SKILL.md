---
name: tech-selection
description: >
  Structured trade-off analysis for choosing a library, tool, framework, or
  component during planning. Use when a plan or design must pick between 2+
  candidate technologies, or when the user asks "which X should we use". Produces
  a bounded decision record: candidates compared on the actual task, assumptions
  ranked by an importance-by-evidence grid, and a tradeoff-per-option table. For
  a full measured bake-off, hands over to the experiment-loop skill. NOT for
  reviewing an already-written plan (use /plan-review) or open-ended ideation
  (use brainstorming).
argument-hint: '<decision, e.g. "redis vs rabbitmq for job dispatch">'
---

# tech-selection

A decision helper for the component-choice moment in planning.
Its job is to convert "which X?" into a small, evidence-ranked decision record the plan can cite.

## Ground rules

- Compare candidates on the task THIS project actually performs, not on generic benchmarks. Benchmarks are directional signals, never guarantees.
- Never report a number you did not compute or fetch this session; version facts, pricing, and API behavior must come from a current source, not memory.
- The deliverable is bounded: at most 4 candidates, at most 5 assumptions to test, one recommendation.

## Steps

1. **Pin the requirement.** One sentence: what the component must do here, with the constraint that decides the choice (scale, license, runtime, team familiarity). If the requirement is not decidable in one sentence, the decision is premature; say so.
2. **Enumerate candidates (2-4).** Always include the null candidate where it exists: stdlib, an already-installed dependency, or "do nothing / write 30 lines". Reuse-before-new is repo law.
3. **Trust check each external candidate.** License is clear; maintenance is alive (recent commits/releases); popularity gets little weight on its own. Match depth of scrutiny to the stakes.
4. **Rank the assumptions.** List what the choice assumes (performance is adequate, API covers the use case, migration is cheap). Score each: importance-if-wrong x current evidence strength.
   - High importance + weak evidence: test before deciding.
   - High importance + strong evidence: monitor.
   - Low importance: ignore for now.
   For each test-first assumption, name the cheapest experiment and what "validated" looks like. If the experiment is substantial or must be measured, hand off to the `experiment-loop` skill when it is installed; otherwise write the experiment protocol (candidates, task, metric, judge) into the plan before anything is measured.
5. **Write the tradeoff table.** One row per candidate: what it gives, what it costs, its trade-off stated plainly, and a "use when" trigger. Every option carries its downside; a table where one row has no cost is not finished.
6. **Recommend and record.** One recommendation with its reversibility stated (how expensive is switching later). Write the record into the plan or the project's decision location; the user rules on it.
