---
name: prompt-improver
description: >
  Invoked automatically by the UserPromptSubmit hook when a prompt is flagged as vague.
  Researches context, then generates 1-6 targeted clarifying questions before executing.
  Do NOT invoke this manually — it is triggered by the hook in .claude/hooks/improve-prompt.py.
auto-activate: false
user-invocable: false
---

# Prompt Improver Skill

You are invoked because the UserPromptSubmit hook has determined the user's prompt lacks sufficient clarity to execute well. Your job is to research context first, then ask smart questions — not the other way around.

## Phase 1 — Research (NEVER skip this)

Before generating any questions, gather real context:

1. Check the full conversation history — has this topic come up before? Is there already enough context?
2. If the request involves code: read relevant files, scan the directory structure, understand the stack
3. If the request involves a task: understand what already exists, what's already been tried
4. If you can fully infer the user's intent from context alone — **skip to Phase 4 immediately**

## Phase 2 — Generate Questions (only if genuinely needed)

Create 1–6 questions. Rules:
- Every question must be grounded in what you actually found in Phase 1
- Never ask about something you can already infer
- Each question should be multiple-choice (3–4 options max) — no open-ended text boxes
- Questions must reduce ambiguity, not pad the conversation
- If 1 question resolves the ambiguity, only ask 1

## Phase 3 — Clarification

Use the `AskUserQuestion` tool to present your questions. Each option should:
- Be concrete and specific (not vague like "Option A / Option B")
- Describe the trade-off or implication where relevant
- Include an "Other / I'll describe" option

## Phase 4 — Execute

Proceed with the original request using:
- The user's original intent
- What you learned in Phase 1
- The user's answers from Phase 3 (if any questions were asked)

Do not re-ask anything the user has already answered. Do not summarise what you're about to do — just do it.

## Bypass

If the user prefixes their message with `*`, the hook skips evaluation entirely and passes the prompt straight through. Useful for urgent or already-detailed prompts.
