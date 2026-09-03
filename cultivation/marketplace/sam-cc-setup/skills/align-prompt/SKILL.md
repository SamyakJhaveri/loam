---
name: align-prompt
description: >
  Turn a rough, vague, or half-formed task description into a prompt aimed at the model
  that will run it (Claude Fable 5.1 or Claude Opus 4.8). Use on "align prompt",
  "rewrite this for the model", "tune this prompt", or whenever a free-form request or a
  plan file is handed over to be made into a proper prompt before a fresh session runs it.
  The `fable-plan <path>` mode aligns a whole execution plan file for a Fable 5.1
  session (written to a sibling file) rather than rewriting a single prompt. NOT for doing the task itself, planning,
  or code review.
argument-hint: "[fable|4.8] <rough request | path/to/draft.md> | fable-plan <path/to/plan.md>"
---

# align-prompt

The draft is written in English by someone who knows the task but has not spelled it out.
Your job is to recover what they meant and state it the way the target model reads best.
The draft's intent is fixed; only its expression changes.

## What you produce

- Draft given inline: one fenced `text` block holding the aligned prompt and nothing else. No
  preamble, no model-name header, no trailing notes. It is meant to be pasted as-is.
- Draft given as a path: overwrite that file in place with the raw aligned prompt (no fences,
  no commentary), then print one line naming the target model and the path.
- `fable-plan <path>`: write the aligned plan to a sibling `<stem>-fable51.md` (the original is
  never mutated), then print one
  line naming the path. See "Plan mode" below.

Never write to any path other than the one supplied.

## 0. Dispatch on the first token

Read the first whitespace-delimited token of the argument and route deterministically. Do not
reason about it; the token either matches or it does not.

| First token | Route |
|-------------|-------|
| `fable`, `fable5.1`, `f51` | Prompt alignment, target Fable 5.1 |
| `4.8` | Prompt alignment, target Opus 4.8 |
| `fable-plan` | Plan mode, target Fable 5.1 (see below) |
| anything else, or empty | Ask which of the two targets. Do not default. |

Everything after the first token, trimmed, is the argument. For prompt alignment, probe it with
`Read`: if the read succeeds it is a draft file (write back to that same path), and if it fails
it is an inline draft. A multi-line pasted draft is never a readable path, so it routes to inline
on its own. The probe is a fact, not a judgment, which is what keeps the dispatch predictable.

## 1. Understand before rewriting

Read the draft for what the person is trying to achieve, not what they literally typed.
Where it is vague, resolve it from the repo first: open the files it names, check `git log`
and `git status`, find the failing command. Most vagueness is a reference to something the
repo already answers. Ask a question only when two readings still survive after that, they
lead to different files being edited, and a wrong guess is not cheaply reversible.

Never invent a requirement the draft does not imply. A draft asking for a typo fix comes back
as a prompt asking for a typo fix; over-formalizing a trivial request is its own failure.

## 2. Extract the three things

Every aligned prompt states, in the draft's own terms:

1. **Goal and why** - what the work is for and what it unblocks. The why is not decoration;
   it lets the model connect the task to context you did not think to include.
2. **Constraints** - the boundaries that are real: files or areas in scope, what must not be
   touched, non-negotiable conventions the repo enforces.
3. **Acceptance criteria** - what "done" is, in a form someone can check: a command that
   passes, an artifact at a path, a behavior observable from outside.

Everything else in the draft is filler and gets cut. The aligned prompt should be shorter and
denser than what it replaces, not longer.

## 3. Aim it at the target model

Both models are steered by goal, constraints, and acceptance criteria. The difference is how
much you have to say out loud.

**Claude Fable 5.1 (`claude-fable-5-1`)** - steer briefly and let it find the path.

- One short instruction beats an enumeration: instruction-following is good enough "that you
  can steer most behaviors with a brief instruction rather than enumerating each behavior by
  name" ([prompting-claude-fable-5]).
- Keep the *why* in. It "tends to perform better when it understands the intent behind a
  request" ([prompting-claude-fable-5]).
- Ambiguity can be handed over rather than resolved. It "performs well when given complex,
  multithreaded requests and asked to determine next steps" ([prompting-claude-fable-5]); when
  the draft is genuinely open, ask it to interview you on the ambiguities where your answer
  would change the approach ([field-guide]).
- Do state boundaries. It can take unrequested actions and, at higher effort, tidy or refactor
  beyond the task ([prompting-claude-fable-5]).
- Avoid asking it to echo, transcribe, or explain its internal reasoning as response text. This
  tripped a `reasoning_extraction` refusal on Fable 5; the 5.1 guide does not list it among the
  remaining safeguard triggers, so treat this as unconfirmed for 5.1 and cheap insurance rather
  than a hard rule.
- Do not add worked examples or step-by-step procedure the model can derive. Skills written for
  older models "are often too prescriptive for Claude Fable 5 and can degrade output quality"
  ([prompting-claude-fable-5]), and examples "constrain them to a certain exploration space"
  ([context-engineering]).

Five deltas are new in 5.1. Fold the relevant ones into the prompt you emit:

- **Targeted edits.** When the task edits files, append: "The number of tokens used to
  edit files is best minimized, all else being equal. Therefore, when it will not affect
  the end result, try to surgically edit a file rather than rewrite the entire thing."
- **Scope of extras.** When the task is an open-ended implementation, append: "If, while
  working or testing, you find a pre-existing bug, a performance concern, or behavior the
  task doesn't mention, don't fix, optimize or extend it in this change unless the
  requested behavior cannot work without it; report it as a follow-up in your summary.
  Commit tests only where the task asks for them or this repository already keeps tests
  for this kind of change. This is about extras only: implement every behavior the task
  asks for, completely."
- **Prose.** When the deliverable is written English, append: "Please remove all mannered
  prose."
- **Long deliverables.** Recommend `high` effort, not `xhigh`, for a single long document
  or a complete code file: at `xhigh` and `max` the model can draft the deliverable once
  in thinking and again in the reply.
- **Progress updates.** 5.1 writes fewer user-facing updates than 5. If the run is attended,
  say so in the prompt; never add a line suppressing narration.

Do NOT add the autonomy block or the tool-batching nudge to a prompt destined for a Claude
Code session. Claude Code already injects both as turn-scoped system messages, and a second
copy is paid input tokens for no behavior change.

**Claude Opus 4.8 (`claude-opus-4-8`)** - say the parts it will not infer.

- It is literal: it "does not silently generalize an instruction from one item to another, and
  it does not infer requests you didn't make" ([prompting-claude-opus-4-8]). Spell out scope
  ("every section, not just the first").
- Front-load. Specify task, intent, and constraints in the first turn; "ambiguous or
  underspecified prompts conveyed progressively over multiple user turns tend to relatively
  reduce token efficiency and sometimes performance" ([prompting-claude-opus-4-8]). This is the
  main split from Fable 5.1: an open question you would hand Fable 5.1 must be closed here.
- State the response shape if it matters; length is calibrated to judged complexity. Frame it
  positively, since positive examples of the wanted style "tend to be more effective than
  negative examples" ([prompting-claude-opus-4-8]).
- Name when to use a tool or fan out to subagents. It favors reasoning over tool calls and
  spawns fewer subagents by default ([prompting-claude-opus-4-8]).
- For review or audit tasks, do not write "only report high-severity issues". It obeys that
  literally and drops real findings ([prompting-claude-opus-4-8]).

Never put API parameters in the prompt body. Effort, adaptive thinking, and max tokens are set
by whoever makes the call, not by the text ([prompting-claude-fable-5-1], [prompting-claude-opus-4-8]).

If no target is given, ask which of the two. Do not default, and do not target Opus 5.

## 4. Plan mode (`fable-plan`)

Plan mode aligns an entire execution plan file for a Fable 5.1 session that will run it, instead of
rewriting one prompt. It exists only for Fable 5.1; there is no `4.8-plan`, because the deltas below
are corrections for Fable 5.1's own habits.

The argument must be a readable file path. Probe it with `Read`. If the read fails, stop with
exactly this line and produce nothing, never falling back to inline mode:

> `fable-plan` needs a readable plan file path. Could not read: `<path>`

Then apply sections 1 to 3 to the plan body, aimed at Fable 5.1, plus three plan-specific deltas:

1. **De-prescribe.** Collapse the step-by-step scaffolding a Fable 5.1 session does not need: worked
   examples of its own tooling, restated general competence, ceremony around ordinary edits. Never
   remove task content, a scope boundary, or a verification step. Style goes; substance stays.
2. **Per-task done check.** Every task in the plan ends with an artifact and a way to check it. If
   the source plan states one, keep it verbatim. If it does not, insert the visible marker
   `[VERIFY: not specified in source plan - fill in]`. Never invent a check that was not there;
   an invented check reads as authoritative and is worse than a visible gap.
3. **Session conduct.** Append one short final section, `## Session conduct (Fable 5.1)`, stating
   the boundaries the plan assumes but never wrote down: what the session must not touch outside
   the plan's scope, and whether the run is attended (ask when a reading is genuinely ambiguous)
   or unattended (choose the best-supported reading, label the assumption, keep going). Ask which
   of the two before writing when the plan does not say.

Write the aligned plan to a sibling file `<stem>-fable51.md` next to the source, raw, with no
fences or commentary; the original plan is never mutated. Then print one line:
`Aligned plan (Fable 5.1) written to <stem>-fable51.md.`

## Sketch

Draft: `the sync script is flaky on the collision path, can you look at it and clean it up`

Aligned (Fable 5.1): *Make `bin/agent-sync-scan.sh` deterministic on the file-vs-directory
collision path; the CI shellcheck pass keeps failing there and it blocks releases. Reproduce
the failure first, then fix the cause. Touch only the collision handling. Done when
`bin/agent-sync-tests/run-all.sh` passes and shellcheck is clean.*

For Opus 4.8 the same prompt additionally names the two collision guards by line, says the fix
applies to both and not to the surrounding validators, and states that the test script is the
tool to run.

---

This skill is manual today. Wiring it into a workflow or a hook so it fires automatically on a
rough handover is a pending task.

[prompting-claude-fable-5-1]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
[prompting-claude-fable-5]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
[prompting-claude-opus-4-8]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
[field-guide]: https://claude.com/blog/a-field-guide-to-claude-fable-finding-your-unknowns
[context-engineering]: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
