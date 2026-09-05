---
name: fable-prompting
description: Which Claude Fable 5.1 guide sections you can act on from a session, and which Claude Code already injects. Use before writing a Fable prompt or handoff.
---

# Fable 5.1 prompting, inside Claude Code

The published guide is the authority; this skill only says which half of it you
can act on from a session. Where this file and the live guide disagree, the
guide wins and this file is wrong.

## Look it up live

1. `WebFetch` the guide at the URL in Sources. Ask it for the one section you need.
2. There is no pinned copy on purpose: the guide moves, and a pinned copy with
   no scheduled refresh ages while still claiming to be current.

## Symptom index

Owner H means the harness or the effort setting owns it; prompt text costs input
tokens and changes nothing. Owner P means the person writing the prompt owns it.
Owner Mixed means both: set the effort level and quote the guide's instruction.

| Symptom | Guide section | Owner |
|---|---|---|
| Unsure which effort level to run | Consider all effort levels | H |
| Goes quiet for minutes between tool calls | Ask for user-facing progress updates | H |
| One tool call per turn | Batch independent tool calls in agent loops | H |
| `bound to a different conversation`, cache misses | Keep the conversation history append-only | H |
| Prose runs long and dense | Writing density | P |
| Replies carry less structure than the content needs | Formatting in chat | P |
| Summaries reuse source wording unmarked | Quoting retrieved sources | P |
| Ends the turn describing what it would do next | Finish the whole task | H |
| Compaction drops constraints or decisions | Tell the model what to preserve in compaction summaries | H |
| Unrequested fixes, or too many committed test files | Keep changes and tests to what the task asks for | P |
| Answers from memory instead of searching | Search triggering at low effort | Mixed |
| Benign code request refused | Reduce safeguard false positives | P |
| Whole file rewritten for a small change | Prefer targeted edits over whole-file rewrites | P |
| Long deliverable is slow or truncated | Leave room for long outputs at xhigh and max effort | H |
| Lead agent idles while subagents run | Let the lead agent keep working while subagents run | H |
| Chart and image detail missed | Give vision work tools to crop and zoom | H |

For a P row, quote the guide's instruction into the prompt. For an H row, change
the effort level or the harness, and add nothing to the prompt.

## Handoff rubric

A handoff file for a fresh Fable 5.1 session carries five headings, in order.

1. **Goal and why.** What the work is for and what it unblocks. The guide notes
   Fable 5.1 runs very long tasks well "especially when the goal is clear".
2. **Constraints.** Files in scope, what must not be touched. Carry the
   scope-of-extras rule here: report a pre-existing bug as a follow-up rather
   than fixing it, and commit tests only where the task asks for them.
3. **Done check per task.** An artifact and a way to check it, per task. Mark a
   missing one visibly rather than inventing a check.
4. **Session conduct.** Attended or unattended, and whether the deliverable is
   prose. If it is prose, add "Please remove all mannered prose."
5. **Target model and effort.** Name the model and the effort level. Prefer
   `high` for a single long document or code file; at `xhigh` and `max` the
   model can draft the deliverable once in thinking and again in the reply.

## Never paste these into a Claude Code prompt

The autonomy block beginning "You are operating autonomously", the
`# Delivering work` block, the progress-updates line, and the tool-batching
nudge. Claude Code already injects all four as system or turn-scoped messages.
A second copy is paid input tokens for no behavior change.

## Sources

- Guide: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1.md
