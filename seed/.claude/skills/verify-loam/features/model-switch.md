# Model switch brief

When a running session switches to a Fable model, `fable-session-brief.sh` runs on `PostModelSwitch` and adds the Fable prompting brief (starting `Fable session.`) to context before the next turn; a switch to any other model adds nothing.

## Sub-features

- `switch-fable` prints the brief on `PostModelSwitch` when `to_model` contains `fable`.
- `switch-context` records the brief as a `hook_additional_context` attachment before the next model reply.
- `switch-silent` prints nothing on a switch to a non-Fable model.

## How to get to it (user POV)

- Type `/model fable` in an interactive session.
- Send a `set_model` control request on a stream-json session, as an Agent SDK client does.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.
- Note `stat -f %Sm ~/.claude/settings.json`.

- **Switch to Fable ($0).** Run `$C session r1 "Reply with the single word OK." --switch-model fable --name sw-fable --stub`. `model` is `claude-fable-5-1`. `hooks` holds `PostModelSwitch:claude-fable-5-1` with exit 0 and stdout starting `Fable session. Ask one question before acting`. The one line in `sw-fable.stub-requests.jsonl` names `claude-fable-5-1`.
- **In context.** In `sw-fable.transcript.jsonl`, a `hook_success` and a `hook_additional_context` attachment for `PostModelSwitch` carry the brief, and both come before the `assistant` record.
- **Silent control.** Run `$C session r1 "Reply with the single word OK." --switch-model sonnet --name sw-sonnet --stub`. `hooks` holds `PostModelSwitch:claude-sonnet-5-5` with exit 0 and empty stdout, and `sw-sonnet.transcript.jsonl` contains no `Fable session`.
- **Nothing saved.** `stat -f %Sm ~/.claude/settings.json` prints the time noted before.
- **Proof.** `sw-fable.jsonl`, `sw-fable.transcript.jsonl` and `sw-sonnet.jsonl` in evidence.

## Gotchas

- Never drive `/model` in `tui`. In Claude Code 2.1.303, `$C tui <id> send "/model fable"` printed `Set model to Fable 5.1 and saved as your default for new sessions` and wrote `"model": "fable"` to the user's `~/.claude/settings.json`, despite `--setting-sources project,local`; later paid sessions without `--model` then ran on Fable. If it happens, set the key back by hand.
- The `tui` `/model` entry point is unreachable without that write. After `$C tui <id> send "/model fable"` and `tui stop`, the transcript held no `PostModelSwitch` record, because no turn followed the switch. Missing precondition: a `/model` switch that saves nothing, or a throwaway user config dir that still has a login.
- The stub proves the brief reached the context, not that Fable read it. [Fable brief](./fable-brief.md) holds the paid quote-back of the same text.
- `--switch-model` sends a `set_model` control request, then the prompt, on stream-json stdin; the stream's `control_response` reports `success` before the `init` event, so `init` already names the new model.
- `PostModelSwitch` hook names carry the resolved model id: `fable` became `claude-fable-5-1` and `sonnet` became `claude-sonnet-5-5`.
