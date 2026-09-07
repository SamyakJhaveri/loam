# Model notes

> Always loaded. The Fable 5.1 and Opus 4.8 prompting guides differ on two points,
> instruction detail and subagent use; following the wrong column is costly in both directions.
> Check what model is actually pinned before applying either column:
> `grep -h '"model"' .claude/settings.json .claude/settings.local.json 2>/dev/null`

## Where the guides differ

| | Fable 5.1 | Opus 4.8 |
|---|---|---|
| Instruction detail | A **brief** instruction serves; with a clear goal it needs little methodology and decides the next step itself | **Literal**; it won't generalize one instruction across items or infer unasked requests, so spell out scope and front-load the whole task in turn one |
| Subagents | **Delegate** freely; the lead keeps working while subagents run | Spawns **fewer** by default and favors reasoning over tool calls; name when to fan out |

## Both models

- **Default effort = `high`.** Step down to `low`/`medium` for transactional work
  (commits, small edits). Reserve the top of the slider for demanding multi-file work.
- **Thinking is on by default (adaptive).** Don't add "think step by step".
- **Effort controls thinking, not output length.** Control verbosity explicitly.
- **Constrain scope on narrow tasks.** State the intended scope for surgical changes.

## Fable 5.1 only

- **Targeted edits.** It may rewrite a whole file for a small change. Add to edit
  tasks: "surgically edit a file rather than rewrite the entire thing" when the
  result is the same.
- **Extras stay out.** It over-delivers fixes and tests the task didn't ask for.
  A pre-existing bug or cleanup is a follow-up in the summary, not the diff; add
  tests only where asked or where the repo already keeps them.
- **Fewer progress updates.** It writes fewer user-facing updates than Fable 5.
  Expect that; if a run is attended, say so in the prompt. Never add a line
  suppressing narration.
- **Long deliverables at `high`.** At `xhigh`/`max` it can draft a long document twice,
  in thinking then reply; run a single long deliverable at `high`.

## Harness-enforced, model-independent

`/validate` and the pre-commit gate are not prompt-level advice; neither guide's
"remove verification instructions" rule touches them. That rule is prompt-level only.
