---
name: plan-review-invoke
description: >
  Invoke the plan-reviewer agent using the canonical reference prompt from
  seed/plan-reviewer-design.md. Use when reviewing a plan in a fresh Claude Code
  session (after the plan was created in a prior session) and you want adversarial
  review (checklist + Elegance Gate + handoff plan) without manually copy-pasting
  the reference prompt. Accepts the plan path as an argument.
  NOT for: same-session plan reviews (just invoke the agent directly with the
  plan in context), reviewing implementations that already shipped (use
  /multi-review or /session-critique), or spec audits (the agent has a separate
  Spec Audit mode invoked differently).
auto-activate: false
---

# plan-review-invoke

Closes the loop between `seed/plan-reviewer-design.md` (canonical reference prompt) and the `plan-reviewer` agent (behavior definition). The reference prompt contains three sections — `<investigate_before_answering>`, `<handoff_requirements>`, and `<final_output>` — that are operative ONLY when the prompt is actually run. The agent's own system prompt has the checklist and Elegance Gate baked in but does NOT enforce the handoff-plan output format on its own.

This skill bridges the gap: it reads the design doc at invocation time, extracts the prompt, and runs it.

## When to fire

User types `/plan-review-invoke <path-to-plan>` in a fresh session, with phrasings such as:
- `/plan-review-invoke docs/plans/2026-05-29-new-feature.md`
- `/plan-review-invoke ~/.claude/plans/refactor-auth.md`
- `/plan-review-invoke` (no path — ask which plan)

Skip if:
- Same-session review — the planning session already has full context; invoke the agent directly via the Agent tool with `subagent_type: plan-reviewer` and a focused prompt.
- The "plan" is actually an implementation diff — use `/multi-review` or `/session-critique` instead.
- The target is a spec document (file in `specs/`, `docs/specs/`, `docs/contracts/`) — the agent has a Spec Audit mode invoked differently; this skill is for plan reviews.

## Process

1. **Resolve the plan path.** If the user supplied a path as an argument, verify the file exists with `Read`. If no path was supplied, ask: "Which plan should I review? Paste the path." Confirm before proceeding.

2. **Extract the reference prompt.** Read `seed/plan-reviewer-design.md`. Locate the prompt with this anchor-based algorithm (no hardcoded line numbers — the skill must survive doc edits):
   - Find the line that starts with `## The Prompt` (H2 heading).
   - From that line, find the FIRST triple-backtick code fence (```` ``` ````) that opens — this is the start-of-prompt.
   - Find the matching closing triple-backtick code fence — this is the end-of-prompt.
   - The prompt body is everything between (exclusive of) those two fences.
   - If the algorithm fails to find these anchors, ABORT with a clear error and ask the user to verify `seed/plan-reviewer-design.md` still follows the documented structure (H2 "The Prompt" → fenced code block).

3. **Invoke the agent.** Spawn the plan-reviewer agent via `Agent(subagent_type: "plan-reviewer", ...)`. The agent's prompt should be:
   ```
   <plan_to_review>
   {{full contents of the plan file at the user-supplied path}}
   </plan_to_review>

   Note: this plan was created in a prior Claude Code session, not "this session"
   as the reference prompt below phrases it. Treat the `<plan_to_review>` block
   above as the authoritative plan content. Where the reference prompt says
   "the plan I just created in this session," substitute "the plan in the
   <plan_to_review> block."

   {{the extracted reference prompt body}}
   ```
   The override note above resolves the phrasing mismatch — the reference prompt was originally written for same-session use; this skill repurposes it for cross-session invocation, so the wrapper + override note make the substitution explicit to the agent.

4. **Surface the verdict.** The agent returns APPROVE / APPROVE WITH CHANGES / REJECT with findings and (per the `<final_output>` block) a handoff-ready plan via `/writing-plans`. Present the verdict + key findings to the user. Do NOT auto-apply any plan changes — the user decides whether to revise.

## Why the skill (not just docs)

Before this skill existed, the workflow was: human reads `workflow.md` → opens `seed/plan-reviewer-design.md` → copies prompt → pastes into fresh session → main Claude invokes agent. Four manual steps, each with drift risk. The skill collapses it to one command and guarantees the doc's prompt is the source of truth (read at invocation time, not snapshotted).

## Skip / NOT for

- **Same-session reviews.** The planning session already has the plan and surrounding context loaded. Spawn the agent directly with a focused prompt instead — the reference prompt's `<investigate_before_answering>` block is most valuable when the agent starts cold.
- **Implementation review.** This skill reviews PLANS (before implementation). Use `/multi-review` or `/session-critique` for code/diff review.
- **Spec audits.** The agent has a Spec Audit Mode (see `seed/.claude/agents/plan-reviewer.md`) invoked with different scaffolding.

## See also

- `seed/.claude/agents/plan-reviewer.md` — agent behavior definition (system prompt, checklist, Elegance Gate, modes)
- `seed/plan-reviewer-design.md` — canonical reference prompt + design rationale
- `seed/.claude/rules/workflow.md` Stage 3 — where this skill plugs into the 6-stage session workflow
