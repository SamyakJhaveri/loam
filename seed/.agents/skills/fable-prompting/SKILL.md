---
name: fable-prompting
description: Which Claude Fable 5.2 guide sections you can act on from a session, and which Claude Code already injects. Use before writing a Fable session prompt or brief.
---

# Fable 5.2 prompting, inside Claude Code

The published guide is the authority; this skill only says which half of it you
can act on from a session. Where this file and the live guide disagree, the
guide wins and this file is wrong.

## Look it up live

1. Fetch the raw guide with `curl -sSL <URL in Sources>` and read the section
   you need. WebFetch returns a model's summary, so never quote guide text from it.
2. This file pins only the two texts a brief pastes word for word ("Texts to
   paste", below), with the date they were checked. Recheck them against the
   live guide when you paste them; the guide moves.

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
- Caution: Fable 5.2 obeys "never" rules, notes and validation steps closely.
  Name the exact actions a rule covers, and write the exception into the rule
  itself (the guide: "ask for approval before deleting files" instead of "never
  delete files").
- Approvals: give a specific go-ahead ("Yes, run X on Y"), never a bare "go".
- Do not ask the model to write its reasoning in the reply: that can trigger
  a `reasoning_extraction` refusal.
- Hard style limits (for example a word cap per sentence) make prose choppy.

## Session-prompt rubric

A session prompt for a fresh Fable 5.2 session carries five headings, in order; a worker brief, its report and a handoff note use the seven `docs/WORKERS.md` headings instead, and the `catchup` staleness check reads a handoff note's `Written at` hash.

1. **Goal and why.** What the work is for and what it unblocks.
2. **Constraints.** Files in scope, what must not be touched, and who owns the
   code: paste the ownership sentence only where the worker may restructure.
   Name the exact actions that need the owner's approval and the ones that do
   not. Add no scope rule for nearby problems: without the ownership sentence
   Fable 5.2 already adds to the existing structure and reports them. With it,
   expect changes nobody asked for (the guide measured 70 to 80 percent more
   output tokens, many of them new tests and docs), so review the diff as well
   as the summary.
3. **Done check per task.** An artifact and a way to check it, per task. Mark a
   missing one visibly rather than inventing a check.
4. **Session conduct.** Attended or unattended, and whether the deliverable is
   prose. If a reader will see only the final report or handoff, paste the
   "Communicating clearly" text, after removing style rules the prompt no
   longer needs.
5. **Target model and effort.** Name the model and set the effort level
   explicitly (the guide starts Fable 5.2 at `high`; a client's default can be
   lower).

## Texts to paste

Checked word for word against the live guide on 13 Nov 2026.

The ownership sentence ("Say who owns the code"), only where the worker may
restructure the code:

```text
You are the owner and long-term maintainer of this codebase, and its design is up to you.
```

The report text ("Make reports easy to follow"), where a person reads the final
report or handoff without having seen the work:

```text
# Communicating clearly
Write for an intelligent but low-context reader. The person reading has not seen your tool calls, your reasoning or the files you opened, and may be switching in from other work. Messages should generally be self-contained: the reader should understand what you mean without having to dig for other context. Put the key points in the first few sentences. Practice progressive disclosure in your sentence order, and do not use undefined references and ideas in line 1 that won't make sense until the reader reaches line 12.

Use plain words, and write in clear, understandable full sentences. Do not use a term or abbreviation that you made up during the work. Say what the thing is in a way any reader would understand. Write mostly in the style of ASD-STE100 Simplified Technical English: short sentences, one idea per sentence, active voice, and consistently using the same word for the same thing. Use a paragraph of flowing prose where ideas connect, and keep bullets for lists of separate items. Leave out unnecessary details unless the reader asks and practice concision, but do ensure that your messages have the key context. Aim to make your user-facing text as human-readable and clear as possible.
```

## Never paste these into a Claude Code prompt

Claude Code sends Fable 5.2 these, so a second copy is paid input tokens for
no behavior change (the first measured in `claude -p`, the reminder read
from the Claude Code bundle; interactive sessions were not captured):

- An adapted form of the guide's finishing text, as the system-prompt section
  `# Finishing work`:
  "Ending your turn means your work stops there until asked to continue, and
  you should not stop unless needed. Please avoid stopping while work the user
  asked for is still owed."
- A turn-scoped reminder after several silent tool steps: "The user hasn't
  heard from you in a while."

The first `claude -p` request held neither the guide's "Signal intent" text
nor its one-line-update sentence ("Keep users informed during long turns"):
paste them where a person watches the session.

Source, Claude Code 2.1.322 on 12 Nov 2026: the first request of
`claude -p hi --model claude-fable-5-2`, captured on a local
`ANTHROPIC_BASE_URL`, holds the first. The reminder is in the installed
bundle, switched on by the model's `fable_5_2_prompt_bundle` capability
(`silent_turn_reminder`); the capture did not reach a silent stretch. Recheck
after a Claude Code update.

## Sources

- Guide: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2.md
