---
name: fable-prompting
description: Which Claude Fable 5.2 guide sections you can act on from a session, and which Claude Code already injects. Use before writing a Fable session prompt or brief.
---

# Fable 5.2 prompting, inside Claude Code

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
Owner Mixed means both: Claude Code sends part of it (see "Never paste these"),
and you quote the rest from the guide.

| Symptom | Guide section | Owner |
|---|---|---|
| Unsure which effort level to run, easy requests slow | Calibrate effort | H |
| Turn ends with work left, a list of what remains, or an offer to continue | Finish the whole task | H |
| Bare "continue" or approval rules applied too widely | Approvals | P |
| Repeats existing code, or reports nearby problems without fixing them | Say who owns the code | P |
| Goes quiet for many tool calls | Keep users informed during long turns | Mixed |
| Starts more subagents than the task needs | Set expectations for subagents | P |
| Asks for approvals it does not need, holds back routine work or retries | Keep caution from piling up | P |
| Old Fable 5.1 or Opus 5.5 lines raise cost or stop working | Review prompts and harnesses designed for earlier models | P |
| Final report dense or full of terms coined during the work | Make reports easy to follow | P |
| `stop_reason: "refusal"` | Safeguard refusals | P |

For a P row, act on the guide's advice in the prompt: add its text, or remove
the lines it names. For an H row, change
the effort level or the harness, and add nothing to the prompt.

## What changed from Fable 5.1

- Effort: start at `high`. Lower effort stops early more often; raise the
  effort rather than quote the "Finish the whole task" text, which Claude Code
  already sends in adapted form (see "Never paste these").
  At `medium` and above, a line such as "answer directly without deliberating" does not stop the model from thinking: lower the effort instead.
- Ownership: Fable 5.2 follows what the prompt says about who owns the code.
  Add the ownership sentence only where the worker may restructure; leave it
  out where the owner owns the code and wants minimal change. A scope rule does
  not cancel the ownership sentence.
- Caution: Fable 5.2 obeys "never" rules, notes and reviewer conditions closely.
  Name the exact actions a rule covers, and write the exception into the rule
  itself (for example "retry a safe, repeatable call without asking").
- Approvals: give a specific go-ahead ("Yes, run X on Y"), never a bare "go".
- Do not ask the model to write its reasoning in the reply: that can trigger
  a `reasoning_extraction` refusal.
- Hard style limits (for example a word cap per sentence) make prose choppy.

## Session-prompt rubric

A session prompt or brief for a fresh Fable 5.2 session carries five headings, in order; a handoff note uses the seven `docs/WORKERS.md` headings instead, and the `catchup` staleness check reads its `Written at` hash.

1. **Goal and why.** What the work is for and what it unblocks.
2. **Constraints.** Files in scope, what must not be touched, and who owns the
   code (see above). Name the exact actions that need the owner's approval and the
   ones that do not. Report a pre-existing bug as a follow-up unless the
   ownership sentence is present, and commit tests only where the task asks.
3. **Done check per task.** An artifact and a way to check it, per task. Mark a
   missing one visibly rather than inventing a check.
4. **Session conduct.** Attended or unattended, and whether the deliverable is
   prose. If a reader will see only the final report, quote the guide's
   "Communicating clearly" text.
5. **Target model and effort.** Name the model and the effort level (`high` by
   default for Fable 5.2).

## Never paste these into a Claude Code prompt

Claude Code sends Fable 5.2 these, so a second copy is paid input tokens for
no behavior change (the first two measured in `claude -p`, the reminder read
from the Claude Code bundle; interactive sessions were not captured):

- An adapted form of the guide's finishing text, as the system-prompt section
  `# Finishing work`:
  "Ending your turn means your work stops there until asked to continue, and
  you should not stop unless needed. Please avoid stopping while work the user
  asked for is still owed."
- The tool-batching line: "Independent tool calls can run in parallel in one
  response."
- A turn-scoped reminder after several silent tool steps: "The user hasn't
  heard from you in a while."

Quote anything else you need. The first `claude -p` request held no autonomy block ("You
are operating autonomously"), no `# Delivering work` block, no "Signal intent"
text and no one-line-update sentence.

Source, Claude Code 2.1.322 on 12 Nov 2026: the first request of
`claude -p hi --model claude-fable-5-2`, captured on a local
`ANTHROPIC_BASE_URL`, holds the first two. The reminder is in the installed
bundle, switched on by the model's `fable_5_2_prompt_bundle` capability
(`silent_turn_reminder`); the capture did not reach a silent stretch. A
`--model claude-fable-5-1` request went out as `claude-opus-5-5`. Recheck after
a Claude Code update.

## Sources

- Guide: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2.md
