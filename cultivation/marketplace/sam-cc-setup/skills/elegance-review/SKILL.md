---
name: elegance-review
description: >
  Run the BLIND frame-breaking elegance review on a plan or implementation via the
  elegance-reviewer agent. Use AFTER a correctness review (plan-review-invoke,
  plan-review-fanout, or codex-plan-review) and BEFORE execution, on any plan that
  creates new files, scripts, abstractions, or pipelines. Accepts a path (plan file,
  script, or directory) as the argument. NOT for: style trimming of fresh diffs
  (pr-review-toolkit:code-simplifier), correctness review (plan-reviewer), or
  reviews where the author's rationale must be weighed (this skill deliberately
  withholds it).
argument-hint: <path-to-plan-or-code>
---

# elegance-review

Invokes the `elegance-reviewer` agent (`.claude/agents/elegance-reviewer.md`) correctly.
The one rule that makes it work: the agent is invoked BLIND.
Self-preference research says a reviewer that can recognize the author's reasoning rates the work higher, so the isolation must be structural.

## Steps

1. Resolve `$ARGUMENTS` to the artifact path. If empty, ask for it; never guess.
2. Build the agent prompt with ONLY:
   - the artifact path(s) to read;
   - the hard constraints the solution must satisfy, stated as bare facts;
   - the repo's reuse surfaces worth searching (existing scripts, helpers, tests).
   NEVER include: why the approach was chosen, the planning conversation, prior review verdicts, or your own opinion of the artifact.
3. Spawn the `elegance-reviewer` agent with that prompt. Run it in the background if a correctness review is running in parallel; the two must not see each other's output before both finish.
4. When the report returns: archive it under `.claude/codex-reviews/YYYY-MM-DD-elegance-<slug>.md` (same shelf as the other review transcripts), then present the ranked counter-proposals to the user for adopt/reject rulings. Adopted counters are recorded where the artifact's decisions live (the repository's documented decision location, or the reviewed artifact itself), never silently applied.

## Design rationale

`.claude/reference/elegance-reviewer-design.md` maps every element of the agent to its evidence.
Division of labor across the review tools is recorded there too.
