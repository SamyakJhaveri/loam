---
name: navigate
description: >
  Tool recommender — takes freeform intent and returns the best skill/agent/command to use.
  Use when unsure which tool to invoke next.
  NOT for: executing tasks directly — only recommending which skill, agent, or command to use next.
---

# Navigate: Intent → Right Tool

Takes freeform user intent and returns the best skill/agent/command(s) to use.

## When to use

- You know what you want to do but don't know which tool does it.
- Your task spans multiple workflows.
- Onboarding: "how do I X?"

## When NOT to use

- You already know the exact command — just invoke it.
- Pure information retrieval — use `/catchup` or read `CLAUDE.md`.
- Model selection advice — use `/model-route`.

## Invocation

```
/navigate "describe what you want to do in one sentence"
```

If no argument is given, ask the user: "What are you trying to do?"

## Procedure

1. **Classify intent** (silently):
   - **Phase:** orient / explore / plan / implement / verify / research / ops
   - **Scope:** single-file / multi-file / cross-cutting

2. **Scan available tools** — check `.claude/skills/`, `.claude/agents/`, and built-in commands.

3. **Match intent to tools** — prefer tools whose description matches the intent.

4. **Return structured output:**

   ```
   ## Recommended: `<primary tool>`
   Rationale: <one sentence>
   How to invoke: <exact command>

   ## Also consider
   - `<second tool>` — <one-line rationale>
   - `<third tool>` — <one-line rationale>  [omit if no good third match]

   ## Next step
   <One sentence: invoke the primary tool, or a clarifying question>
   ```

5. **If intent is ambiguous** (4+ tools match): ask ONE clarifying question with 2–4 options.

6. **If no tool matches**: say so — "No tool covers this. Consider creating a new skill."

## Constraints

- Never invent a tool that doesn't exist. Verify by checking `.claude/skills/` and `.claude/agents/`.
- Never recommend more than 3 tools (primary + 2 alternatives).
- Output stays under ~15 lines.
- Don't run the recommended tool unprompted — recommend, then let the user invoke.
