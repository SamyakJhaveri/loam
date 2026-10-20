# Deny rules

A rendered project's `.claude/settings.json` denies destructive shell commands (`rm -rf` and its spellings, force pushes, `git reset --hard`, `git clean`, broad restores, stash drops) and reads or edits of `.env*`, even when the user runs Claude in bypass mode.

## Sub-features

- `deny-rm` refuses `rm -rf` and the other flag orders.
- `deny-git` refuses force pushes, `git reset --hard`, `git clean -f/-d/-x`, `git checkout .`, `git restore .`, `git stash clear/drop`.
- `deny-env` refuses `Read` and `Edit` of `.env*`.
- `deny-bypass` keeps all of the above in force under `bypassPermissions`.

## How to get to it (user POV)

- Ask Claude to run one of the commands, in any permission mode.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.
- Make a sentinel: `mkdir -p <root>/r1/render/deny-probe && touch <root>/r1/render/deny-probe/keep`.

- **Control and denial in one turn.** Run `$C session r1 "Run these two Bash commands one after the other and report each outcome: first 'ls deny-probe', then 'rm -rf deny-probe'." --name deny --bypass`. `permission_denials` lists exactly `rm -rf deny-probe`; `result` reports that `ls` listed `keep`.
- **Stub variant ($0).** Run `$C session r1 "STUB_BASH: ls deny-probe ;; rm -rf deny-probe" --name deny --bypass --stub`. The stub always issues both commands, so the model cannot decline. `permission_denials` lists exactly `rm -rf deny-probe`; in `deny.jsonl` the first `tool_result` lists `keep` and the second says permission was denied. With the `Bash(rm ...)` entries removed from the render's `.claude/settings.json`, the same session shows no denial and the sentinel gone.
- **Survived.** `ls <root>/r1/render/deny-probe` still shows `keep`.
- **Other rules.** Swap the second command for the rule under test, for example `git reset --hard`, and keep the `ls` control.
- **Proof.** `deny.jsonl` in evidence plus the surviving sentinel.

## Gotchas

- Without `--bypass`, every unapproved command is refused in `-p` mode, so a denial proves nothing about the rule. Always pass `--bypass` and keep the allowed control.
- The model may decline to try a destructive command at all; then `permission_denials` is empty and the proof is inconclusive, not a pass. Rephrase as an explicit test instruction.
- Remove the sentinel before `$C check`, or untracked files stay in the render.
