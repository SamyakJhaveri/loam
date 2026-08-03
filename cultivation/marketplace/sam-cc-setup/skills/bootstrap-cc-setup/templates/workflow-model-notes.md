# Model notes

> Always loaded. The Fable 5 and Opus 5 prompting guides invert on two points;
> following the wrong column is costly in both directions.
> Check what model is actually pinned before applying either column:
> `grep -h '"model"' .claude/settings.json .claude/settings.local.json 2>/dev/null`

## Where the guides invert

| | Fable 5 | Opus 5 |
|---|---|---|
| Subagents | Use **frequently**; fresh-context reviewers catch what the author misses | **Cap** spawning; prefer one over several |
| Self-verification | Make it **explicit**; use fresh-context verifiers | **Remove** it; the model self-corrects |

## Both models

- **Default effort = `high`.** Step down to `low`/`medium` for transactional work
  (commits, small edits). Reserve the top of the slider for demanding multi-file work.
- **Thinking is on by default (adaptive).** Don't add "think step by step".
- **Effort controls thinking, not output length.** Control verbosity explicitly.
- **Constrain scope on narrow tasks.** State the intended scope for surgical changes.

## Fable 5 only

- **`reasoning_extraction`.** Instructions to echo, transcribe, or explain internal
  reasoning as response text can trigger a refusal and an elevated fallback to Opus.
  Avoid reflection-style instructions in agents, rules, and hooks.
- **Don't surface context-budget countdowns.** They prompt the model to trim its own
  work and offer a premature handoff.

## Harness-enforced, model-independent

`/validate` and the pre-commit gate are not prompt-level advice; neither guide's
"remove verification instructions" rule touches them. That rule is prompt-level only.
