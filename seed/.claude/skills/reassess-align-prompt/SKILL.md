---
name: align-prompt
description: >
  Use when you have a free-form draft prompt and want it rewritten into
  Claude Opus 4.6 or 4.8 conventions before pasting it into a new planning
  or execution session. Trigger phrases — "align prompt", "rewrite for opus",
  "tune prompt for claude". NOT for planning itself, code implementation, or
  validation. Pre-planning / pre-execution only.
argument-hint: 4.6|4.8 <draft prompt | path/to/draft-file>
---

# align-prompt

You rewrite the user's free-form draft prompt into the form Claude Opus 4.6 or 4.8 responds best to. The draft can be supplied inline or as a path to a draft file. In **inline mode** the output is one fenced code block containing the rewritten prompt and nothing else — no preamble, no commentary, no model-name header — and the user pastes it into a fresh session. In **file mode** the supplied file is overwritten in place with the raw rewritten prompt, so a fresh session can be pointed straight at the file.

## Phase 1: Parse `$ARGUMENTS`

Parse the FIRST whitespace-delimited token. Dispatch is deterministic — do not use LLM reasoning when a keyword is present:

1. `4.6` → Phase 2 with `target=4.6` (execution shape)
2. `4.8` → Phase 2 with `target=4.8` (planning shape)
3. `4.7` → Phase 1B (explicit refusal — 4.7 is chucked from this skill's target set per user policy)
4. Anything else (or no first token) → Phase 1A

Everything AFTER the first token (or the entire `$ARGUMENTS` if Phase 1A fires) is `ARG`. Once a target is resolved (4.6 or 4.8 — NOT 4.7, NOT missing), detect the mode in Phase 1C.

### Phase 1C: Detect mode (deterministic)

Only reached after a target resolves to 4.6 or 4.8. The 4.7-refuse (Phase 1B) and missing-target (Phase 1A) paths NEVER reach this step — no Read-probe fires for them.

Take `ARG` = everything after the first token, trimmed of leading/trailing whitespace, and detect mode deterministically by probing it with the `Read` tool:

1. `Read(ARG)` **succeeds** → **file mode**: the draft body is the file's contents; remember `ARG` as the write-back path for Phase 4.
2. `Read(ARG)` **fails** (not found / directory / unreadable) → **inline mode**: the draft body is the trimmed `ARG` (current behaviour). An existing directory path also fails `Read` and routes to inline — surprising but non-destructive, since nothing is written.

Rationale: `Read` is already the only always-permitted tool, so the probe adds no new dependency. A multi-line pasted draft naturally fails `Read` and routes to inline; an existing single-line path routes to file. Dispatch stays deterministic — the file either exists or it does not, a fact rather than an LLM judgement.

Edge case (accepted): file mode overwrites the supplied path in place with no backup, so a filename collision is destructive — inline text mistaken for a file would be clobbered by the rewrite. A collision can only happen when the entire trimmed `ARG` is a single token that is also an existing readable path; a normal multi-word draft is not a valid path, `Read` fails on it, and it routes to inline. The alternative (fuzzy path-sniffing) is worse and violates the no-guessing principle.

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

Full move definitions and rationale live in `reference.md` § 4 (loaded in Phase 2) and § 1. Below is the per-target **gating** only — apply in order:

1. **Lead with intent** — always.
2. **Name the role** — only if the task is domain-specific.
3. **Surface scope** — `## Constraints` always; `## Must NOT include` only if (target=4.8 AND task is planning) OR the draft hints at exclusions; for target=4.6, ALSO add an anti-generalization scope statement.
4. **Specify Done** — always (artifact + verification).
5. **Adaptive-thinking cues** — target=4.8 only; skip for 4.6 (see `reference.md` § 1).
6. **Compress + tone-anchor** — always; add the "Direct technical prose. No emoji." tone-anchor for target=4.6 only.

Never mention API parameters (`effort`, `thinking.budget_tokens`, etc.). Use the three pairs in `examples.md` as your few-shot anchor. The rewrite must be predictable session-to-session.

## Phase 4: Output

Branch on the mode detected in Phase 1C.

### Inline mode

Output the rewritten prompt as a single fenced block with language hint `text`:

````text
<rewritten prompt here>
````

NOTHING outside the fence. No preamble like "Here is your rewritten prompt:". No trailing notes. No model-name header. Paste-ready.

### File mode

Use the `Write` tool to overwrite `ARG` (the write-back path from Phase 1C) with the rewritten prompt. The written content is **raw aligned prompt text — NO code fences, no preamble, no commentary, no model-name header** (it is a prompt file, not a display block). Then print to the terminal exactly ONE line:

> Aligned prompt (target <resolved 4.6|4.8>) written to `<ARG>`.

(Substitute the resolved target and the actual path.) Nothing else on the terminal.

## Critical Rules

1. In inline mode the output is the rewrite and nothing else, paste-ready. In file mode the raw rewrite is written to the file and the terminal shows only the single confirmation line.
2. Preserve the user's task content; transform style only. Never invent technical requirements not in the draft.
3. Permitted tools: `Read` always (for `reference.md`, `examples.md`, and the Phase 1C mode probe) and `Write` only in file mode (to overwrite `ARG`). No `Edit`, no `Bash`, no `WebFetch`.
4. Never write to any path other than the exact `ARG` the user supplied — no derived filenames, no `.bak`, no new files; the only write is an in-place overwrite of the supplied path.
5. Never mention API parameters (`effort`, `thinking`, `max_tokens`, `temperature`). Those are caller-controlled.
6. When target=4.6, omit Move 5 entirely. 4.6 does NOT support adaptive thinking — the prompt body cannot elicit per-turn reasoning depth. Thinking on 4.6 is set at the API layer by the caller via the legacy `thinking: {type: "enabled", budget_tokens: N}` field. Prompt-body reasoning invitations are inert.
7. When the draft is < 20 words AND obviously simple (e.g., "fix typo in README"), output it largely unchanged — over-formalizing a trivial prompt is itself a failure mode.
8. Never produce a rewrite when the dispatch token is `4.7`. Refuse with the Phase 1B message verbatim.

## Out of scope (deferred)

- **`--refresh` from web docs** — v1 uses hand-authored `reference.md`. Re-curate manually (~10 min) when a new Opus model drops. v2 may add `/align-prompt --refresh` if the cadence proves painful.
- **Sonnet / Haiku targets** — ruled out by user's Opus-only policy.
- **Opus 4.7 target** — explicitly chucked from this skill's target set (user policy decision codified 2026-05-28). 4.7's tokenizer emits ~1.0×–1.35× as many tokens as 4.6 for the same input at the same rate-card price, and 4.8 already supersedes 4.7 on reasoning quality. 4.7 is dominated on both dimensions.
- **Calling Anthropic's Prompt Improver API** — keeps skill self-contained and Loam-aware; revisit if pure-prompt-driven quality proves insufficient.
- **Clipboard output** — file overwrite and terminal paste-block are the only output modes.
- **Rewrite logging / A-B comparison** — no persistence in v1.
