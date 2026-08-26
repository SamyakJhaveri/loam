---
name: plan-review-invoke
description: >
  Use when reviewing an implementation plan in a fresh session, after the plan
  was written in a prior session, and you want an adversarial pass (checklist +
  elegance gate + a self-contained handoff plan) without copy-pasting a reviewer
  prompt. Spawns the shipped plan-reviewer agent on the plan file. Accepts the
  plan path as an argument.
  NOT for: same-session plan reviews (invoke the plan-reviewer agent directly
  with the plan already in context); reviewing implementations or diffs that
  already shipped (use a code-review or session-critique flow); or the blind
  frame-breaking pass (use elegance-review).
argument-hint: <path-to-plan>
---

# plan-review-invoke

Runs the `plan-reviewer` agent (`agents/plan-reviewer.md`) against a plan file
that was authored in an earlier session. The agent carries the full reviewer
contract itself, the read-before-critique ground rule, the six-point checklist,
the elegance gate, and the handoff-plan output, so this skill only has to resolve
the path and pass the plan in with a cross-session note.

## When to fire

User types `/plan-review-invoke <path-to-plan>` in a fresh session, for example:
- `/plan-review-invoke .claude/plans/new-feature.md`
- `/plan-review-invoke docs/plans/refactor-auth.md`
- `/plan-review-invoke` (no path, ask which plan)

Skip if:
- Same-session review: the planning session already has full context, so invoke
  the plan-reviewer agent directly via the Agent tool with a focused prompt.
- The target is an implementation diff, not a plan: use a code-review or
  session-critique flow instead.
- The target is a spec or contract document rather than a plan.

## Process

1. **Resolve the plan path.** If the user supplied a path, confirm the file
   exists with Read. If none was supplied, ask "Which plan should I review? Paste
   the path." and confirm before proceeding.

2. **Invoke the agent.** Spawn the reviewer via
   `Agent(subagent_type: "plan-reviewer", ...)`. The prompt is:
   ```
   <plan_to_review>
   {{full contents of the plan file at the user-supplied path}}
   </plan_to_review>

   This plan was created in a PRIOR session, not this one. Treat the
   <plan_to_review> block as the authoritative plan content and the repository
   as authoritative for what is true. Follow your full reviewer contract:
   read before critiquing, work the checklist, run the elegance gate, and emit
   a self-contained handoff plan plus your verdict.
   ```

3. **Surface the verdict.** The agent returns APPROVE / APPROVE WITH CHANGES /
   REJECT with findings and a handoff-ready revised plan. Present the verdict and
   key findings to the user. Do NOT auto-apply plan changes; the user decides
   whether to revise, and the calling session writes any revised plan to disk.

## Why a skill and not just the agent

Invoking the agent by hand every time means restating the cross-session framing
and remembering to pass the plan file's contents rather than a path the agent
cannot see. This skill collapses that to one command and guarantees the plan text
is read in fresh at invocation time.

## See also

- `agents/plan-reviewer.md`: the reviewer's behavior (checklist, elegance gate,
  handoff contract, verdict).
- `agents/elegance-reviewer.md` and the `elegance-review` skill: a separate
  blind frame-breaking pass. For high-stakes plans, run it after this one as an
  independent review, and never pass it the author's reasoning.
- `workflows/plan-review-fanout.js`: a parallel, grounded upgrade of this skill
  that fans the same checklist across several lenses.
