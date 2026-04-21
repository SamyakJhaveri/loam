---
name: navigate
description: Tool recommender for any ParBench session — takes freeform intent ("I want to run evals overnight on Rodinia", "debug a broken spec", "write the methodology section") and returns the top 2-3 matched skills/agents/commands across the ParBench, GSD, superpowers, and built-in ecosystems, with rationale. Use when unsure which tool to invoke next, when onboarding a new contributor, or when a task spans multiple ecosystems.
---

# Navigate: Intent → Right Tool

Takes freeform user intent and returns the best skill/agent/command(s) to use, drawn from a grounded taxonomy of this project's ~100 tools.

## When to use

- You know what you want to do but don't know which tool does it.
- Your task spans ecosystems (e.g., "plan a fix and run validation" crosses GSD + ParBench).
- Onboarding: a contributor asks "how do I X?"

## When NOT to use

- You already know the exact command — just invoke it.
- The task is pure information retrieval (use `/catchup` or read `CLAUDE.md`).
- You need Claude-model selection advice — use `/model-route` instead.

## Invocation

```
/navigate "describe what you want to do in one sentence"
```

If no argument is given, ask the user: "What are you trying to do?"

## Procedure

1. **Classify intent along 3 axes** (do this silently; do not output the classification):
   - **Phase:** orient / explore / plan / implement / verify / eval / research / paper / ops
   - **Domain:** eval-pipeline / spec-oracle / augmentation / paper / infrastructure / session-management / model-selection
   - **Scope:** single-file / multi-file / cross-cutting / overnight-batch

2. **Load taxonomy** by reading `taxonomy.md` in this skill's directory. It has 4 tables:
   - Table A: ParBench skills (26)
   - Table B: ParBench agents (14)
   - Table C: GSD commands (top 20 routing targets)
   - Table D: superpowers skills (14)

3. **Match intent to tools** using the taxonomy's "When to use" columns. Prefer tools whose description explicitly matches the intent phase + domain + scope.

4. **Return structured output** in this exact format:

   ```
   ## Recommended: `<primary tool>`
   Rationale: <one sentence — why this is the best match>
   How to invoke: <exact command or Agent call>

   ## Also consider
   - `<second tool>` — <one-line alternative rationale>
   - `<third tool>` — <one-line alternative rationale>  [omit if no good third match]

   ## Next step
   <One sentence: either invoke the primary tool now, or a clarifying question if the intent is ambiguous>
   ```

5. **If intent is ambiguous** (matches 4+ tools roughly equally): DO NOT guess. Ask ONE clarifying question using AskUserQuestion with 2–4 options drawn from the top matches. Then re-run step 3 with the answer.

6. **If no tool matches** (intent is outside this project's scope): say so explicitly — "No tool in the current setup covers this. Consider doing it manually or creating a new skill with `superpowers:writing-skills`."

## Examples (see examples.md for the full list)

| Intent | Primary | Rationale |
|--------|---------|-----------|
| "run evals overnight on Rodinia CUDA→OMP" | `/overnight-eval` | tmux isolation + pre-flight + monitoring built in |
| "debug why spec X fails" | `/fix-bug` + `/spec-check` | reproduction-first diagnosis |
| "resume after a break" | `/catchup` | 30s bootstrap briefing |
| "write paper methodology section" | `/agent-team` scenario=paper-assembly | multi-agent draft + review loop |
| "check if my changes broke anything before commit" | `/validate` | pre-commit gate waves 1–3 |

Load `examples.md` for the full 20+ intent→tool mapping if the user's intent doesn't immediately match one of the five above.

## Constraints

- Never invent a tool that doesn't exist in `taxonomy.md`. If unsure, say "I don't see a tool for this."
- Never recommend more than 3 tools (primary + 2 alternatives). More than 3 is noise.
- Output stays under ~15 lines unless the user asks for more detail.
- Don't run the recommended tool unprompted — recommend, then let the user invoke.
