---
name: mode-routing
description: Decide how much to constrain the model for the task at hand - open for research, ideation, design and diagnosis; clamped for published numbers, harness code and anything a reviewer will read. Use when starting a task whose kind is unclear, when output feels safe and obvious and you wanted invention, when a session is producing plausible prose instead of checked facts, or when choosing effort level and whether to fan out subagents.
---

# Open or clamped

Two failure modes, opposite causes, and the setup has to be able to produce both.

> "If you are too specific, Claude will follow your instructions even when a pivot may be
> more appropriate. If you are too vague, Claude will often make choices and assumptions
> based on industry best practices that may not be a fit for your task."
> — Thariq Shihipar, *Finding Your Unknowns*

> "Examples fence Claude into the demonstrated space."
> — Thariq Shihipar, *The new rules of context engineering for Claude 5*

A wall of rules does not make work safer in general. It makes it **conventional**. That is
the right trade when the output is a published number and the wrong one when the output is
an idea you do not yet have.

## Which mode

| The output is | Mode | Why |
|---|---|---|
| A research direction, an experiment design, a hypothesis, a name, an API surface, a diagnosis with no known root cause | **OPEN** | The answer is not in the repo. Constraints here cost you the answer. |
| A number that will be published, a rebuttal sentence, harness or spec code, anything under the artifact freeze, anything a reviewer reads | **CLAMPED** | The answer exists and must be found exactly. Invention here is fabrication. |
| Refactors, config, tooling, docs | **CLAMPED, cheaply** | Known-good shapes exist. Follow them and move on. |

The mistake to avoid is treating *research* as clamped because it is important. Importance
selects for rigour in the **checking**, not for narrowness in the **generating**.

## OPEN mode

- **Generate before judging.** Several genuinely different directions, not one polished
  answer with variants. Thariq's own wording: *"4 wildly different design directions so I
  can react to them."* If they share a frame, they are one direction.
- **No examples in the prompt** unless the example IS the spec. An example is a fence.
  Prefer expressive constraints: a rejected option and why, a hard boundary, a success test.
- **Say what you do not know.** The precondition, verbatim: *"tell it where you are in your
  thought process; disclose your experience with the problem and codebase; and let it work
  with you like a thought partner."* An OPEN session opened without this produces
  confident-sounding convention.
- **Build something to react to.** A prototype, a mock, four directions in one HTML page.
  Reacting is faster and more accurate than specifying. See the `unknowns` skill.
- **Set aside generic process preferences**, which encode what went wrong before and are the
  wrong prior for something not yet tried. **Not the incident-backed rules** - the argc check,
  the append-only manifest, the immutable result JSONs, the frozen artifact. Those are facts
  about this repo, not stylistic guardrails, and OPEN mode does not suspend facts. If you are
  unsure which a rule is, it stays.
- **Effort high, and let it run.** Interrupt for simplicity, not for style - *"why are you
  doing this? Try something simpler"* (Anthropic Data Science / ML Engineering).

Skills that already do this: `adhd` (parallel divergent branches under different cognitive
frames), `surprise-me` (ranked unrequested ideas toward a named goal), `unknowns` (blindspot
pass, brainstorm-to-react, interview).

## CLAMPED mode

- Every number traces to a file on disk, re-derived this session. Relayed is not verified.
- Fresh-context verifier subagents, and a cross-model refuter for anything load-bearing.
  Self-review is the weak form: the failure mode has a name, *self-preferential bias*.
- The harness gates apply and are not advisory: `/validate`, the hooks, the commit gate.
- `rigor` and `research-writing` carry the full apparatus. Use them.

## Switching mid-task

Most real work is OPEN then CLAMPED, in that order, and the switch is a **hard boundary**:
the generating session should not also be the checking session. Ideas produced and validated
in one context inherit that context's blind spots.

Concretely: brainstorm in one session, write the plan out, start implementation in a **new
session** with the artifacts passed in as attachments. That is Thariq's own sequence, and it
is why plans here are files rather than conversation state.

## What this means for the always-loaded rules

Rules that exist because something went wrong are worth their tokens in both modes - they
are domain knowledge, and Boris's §109 says encode exactly that. Rules that merely restate a
harness gate, or encode a generic process preference, cost tokens in every session and
narrow the OPEN ones for nothing.

The test is not "is this rule true?" but **"did a real failure produce it, and does the
harness already enforce it?"** A rule the hooks enforce does not need prose; per §112,
instructions belong in one place only.
