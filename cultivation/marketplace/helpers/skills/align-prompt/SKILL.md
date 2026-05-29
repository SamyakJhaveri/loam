---
name: align-prompt
description: >
  Use when you have a free-form draft prompt and want it rewritten into
  Claude Opus 4.6 or 4.8 conventions before pasting it into a new planning
  or execution session. Trigger phrases — "align prompt", "rewrite for opus",
  "tune prompt for claude". NOT for planning itself, code implementation, or
  validation. Pre-planning / pre-execution only.
auto-activate: false
argument-hint: 4.6|4.8 <draft prompt>
---

# align-prompt

You rewrite the user's free-form draft prompt into the form Claude Opus 4.6 or 4.8 responds best to. Output is one fenced code block containing the rewritten prompt and nothing else — no preamble, no commentary, no model-name header. The user pastes it into a fresh session.

## Phase 1: Parse `$ARGUMENTS`

Parse the FIRST whitespace-delimited token. Dispatch is deterministic — do not use LLM reasoning when a keyword is present:

1. `4.6` → Phase 2 with `target=4.6` (execution shape)
2. `4.8` → Phase 2 with `target=4.8` (planning shape)
3. `4.7` → Phase 1B (explicit refusal — 4.7 is chucked from this skill's target set per user policy)
4. Anything else (or no first token) → Phase 1A

Everything AFTER the first token (or the entire `$ARGUMENTS` if Phase 1A fires) is the draft prompt body, preserved verbatim for transformation.

### Phase 1A: Missing target

If the first token is none of `4.6`, `4.7`, or `4.8`, ask exactly one question:

> Which Opus model is this prompt for — 4.6 (execution) or 4.8 (planning / brainstorming)?

Wait for the answer, then proceed to Phase 2 with the corresponding target. Do not infer; do not default. The user's stated workflow ties model to use-case, so a wrong assumption produces a wrongly-shaped rewrite.

### Phase 1B: 4.7 target refused

If the first token is `4.7`, respond with exactly:

> 4.7 is not a target for this skill. Use 4.6 (execution) or 4.8 (planning / brainstorming).

Do NOT silently default to 4.6 or 4.8 — the user's policy is explicit and a wrong-target rewrite is worse than a refusal. Do NOT produce any rewrite in this phase.

## Phase 2: Load the rewrite spec

Read the two sibling files in this skill's directory:

- `reference.md` — distilled Opus 4.6/4.8 prompting facts + The Six Rewrite Moves
- `examples.md` — 3 worked before/after pairs (few-shot anchor)

These are the spec. Apply them.

## Phase 3: Apply the Six Moves to the draft

Per `reference.md` § 4, in order:

1. **Lead with intent** — one-sentence intent + success criterion as the first line.
2. **Name the role** — only if the task is domain-specific; skip for mechanical/single-shot.
3. **Surface scope** — `## Constraints` section always; `## Must NOT include` only if (target=4.8 AND task is planning) OR the draft explicitly hints at exclusions. For target=4.6, ALSO add an explicit anti-generalization scope statement ("Apply to X ONLY, do not generalize to siblings") because 4.6 silently generalizes — see `reference.md` § 1.
4. **Specify Done** — artifact + verification, one section.
5. **Adaptive-thinking-eliciting language** — only when target=4.8. 4.6 does NOT have adaptive thinking; eliciting it in the prompt body is inert on 4.6. NEVER mention `effort`, `thinking.budget_tokens`, or any API parameter.
6. **Compress + tone-anchor** — strip filler, hedges, second-person scaffolding. For target=4.6, also add "Direct technical prose. No emoji." if the draft implies a technical voice — 4.6's baseline tone is warmer and includes more emoji than 4.8's.

Use the three pairs in `examples.md` as your few-shot anchor. The rewrite must be predictable session-to-session.

## Phase 4: Output

Output the rewritten prompt as a single fenced block with language hint `text`:

````text
<rewritten prompt here>
````

NOTHING outside the fence. No preamble like "Here is your rewritten prompt:". No trailing notes. No model-name header. Paste-ready.

## Critical Rules

1. Output is the rewrite and nothing else. Paste-ready.
2. Preserve the user's task content; transform style only. Never invent technical requirements not in the draft.
3. Never call any tool other than `Read` (for `reference.md` and `examples.md`). No `Edit`, no `Write`, no `Bash`, no `WebFetch`. The skill is a pure prompt transform.
4. Never modify the user's project files.
5. Never mention API parameters (`effort`, `thinking`, `max_tokens`, `temperature`). Those are caller-controlled.
6. When target=4.6, omit Move 5 entirely. 4.6 does NOT support adaptive thinking — the prompt body cannot elicit per-turn reasoning depth. Thinking on 4.6 is set at the API layer by the caller via the legacy `thinking: {type: "enabled", budget_tokens: N}` field. Prompt-body reasoning invitations are inert.
7. When the draft is < 20 words AND obviously simple (e.g., "fix typo in README"), output it largely unchanged — over-formalizing a trivial prompt is itself a failure mode.
8. Never produce a rewrite when the dispatch token is `4.7`. Refuse with the Phase 1B message verbatim.

## Out of scope (deferred)

- **`--refresh` from web docs** — v1 uses hand-authored `reference.md`. Re-curate manually (~10 min) when a new Opus model drops. v2 may add `/align-prompt --refresh` if the cadence proves painful.
- **Sonnet / Haiku targets** — ruled out by user's Opus-only policy.
- **Opus 4.7 target** — explicitly chucked from this skill's target set (user policy decision codified 2026-05-28). 4.7's tokenizer emits ~1.0×–1.35× as many tokens as 4.6 for the same input at the same rate-card price, and 4.8 already supersedes 4.7 on reasoning quality. 4.7 is dominated on both dimensions.
- **Calling Anthropic's Prompt Improver API** — keeps skill self-contained and Loam-aware; revisit if pure-prompt-driven quality proves insufficient.
- **Clipboard / file output** — terminal-only in v1.
- **Rewrite logging / A-B comparison** — no persistence in v1.
