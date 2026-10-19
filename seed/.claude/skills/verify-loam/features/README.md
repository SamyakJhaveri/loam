# Loam verification map

The maintained list of what a rendered Loam project does for its user, and how `control-loam` proves each behavior.
The user is someone who renders a project with Copier and then works in it with Claude Code.

## Baseline preconditions

- Run from the Loam root with `C=.claude/skills/verify-loam/control-loam`.
- Start each recipe from a fresh `$C render --run <id>` unless it says otherwise.
- `$C doctor <id>` passes before the first drive.
- Never drive a render this run did not create.

## Driving conventions

- Headless (`$C session`) for anything the stream-json hook events show; interactive (`$C tui`) only when headless cannot reach the behavior.
- Treat quoted prompts as literal.
- Ask the model to quote injected text verbatim; a paraphrase is not proof that the text arrived.
- A paid session costs money (one-word prompts keep a turn near $0.12); `session --stub` costs $0 where a scripted model is enough.

## Proof and skip reporting

- Name the feature ID and run ID with every artifact.
- A headless proof is the session's `.jsonl` in evidence plus the JSON summary.
- An interactive proof is the `.screen.txt` from `tui stop`.
- Report an unreachable path with the command tried and the unmet precondition.

## Feature entry contract

Each file has an H1, one paragraph on the user-visible behavior, then four H2s in order: `Sub-features`, `How to get to it (user POV)`, `Driving it with control-loam` (starting with `Preconditions:`), `Gotchas`.

## Features

- [Render](./render.md): `copier copy` produces a git-initialized project whose own `bin/check` passes clean and fails on a planted defect.
- [Session memory](./session-memory.md): each session is captured; the next session starts with it recalled.
- [Deny rules](./deny-rules.md): destructive commands are refused even in bypass mode.
- [Fable brief](./fable-brief.md): a Fable session starts with the prompting brief; other models get nothing.
- [Shipped skills](./shipped-skills.md): the seed skills are available in every session.

## Not yet mapped

- `post-compact-reinject.sh` on `SessionStart:compact`.
- `fable-session-brief.sh` on `PostModelSwitch` (a `/model` switch inside `tui`).
- `copier update` of an existing render to a newer ref.
- The Codex harness (`.codex/`).
