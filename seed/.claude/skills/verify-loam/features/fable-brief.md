# Fable brief

When a session runs on a Fable model, `fable-session-brief.sh` adds a short prompting brief (starting `Fable session.`) to context at startup and after a switch to Fable; on any other model it prints nothing.

## Sub-features

- `fable-start` prints the brief on `SessionStart` when the payload's `model` contains `fable`.
- `fable-switch` prints the brief on `PostModelSwitch` when `to_model` contains `fable`; [Model switch brief](./model-switch.md) drives it.
- `fable-silent` prints nothing for other models or a missing model field.

## How to get to it (user POV)

- Start `claude --model fable` in the project.
- Switch to Fable with `/model` mid-session.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes; `tmux` is on PATH.

- **Start.** Run `$C tui r1 start --model fable`. The screen shows `Fable 5.1`.
- **Brief arrived.** Run `$C tui r1 send "Quote verbatim the first sentence of any text in your context that begins with 'Fable session', or reply NONE. Do not use tools."`. The reply line (`⏺`) quotes text starting `Fable session.`; a `NONE` reply is a failure.
- **Stop.** Run `$C tui r1 stop --name fable-tui`. Evidence has `fable-tui.screen.txt`.
- **Silent control.** Run `$C session r1 "Reply with the single word OK."` on the default model. No `SessionStart` stdout contains `Fable session`.

## Gotchas

- Headless sessions never get the brief: in `claude -p` (2.1.302) the `SessionStart` payload has no `model` field, so the hook stays silent even with `--model fable`. Use `tui`. Observed payload keys: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `source`; interactive adds `scratchpad_dir` and `model`.
- A Fable turn costs about five times a default-model turn.
- `tui start` records workspace trust for the render path in `~/.claude.json`; the entry outlives cleanup but points at a deleted path.
