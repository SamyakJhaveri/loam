# Shipped skills

A rendered project makes the seed skills (`catchup`, `fable-prompting`, `hypothesis-tree`) available in every Claude Code session, through checked-in symlinks from `.claude/skills/` to `.agents/skills/`.

## Sub-features

- `skills-listed` shows each seed skill in the session's skill list.
- `skills-symlinked` keeps `.claude/skills/<name>` a symlink to `../../.agents/skills/<name>`, shared with Codex.

## How to get to it (user POV)

- Type `/` in a session and see the skills. Claude can also pick one by description, unless its frontmatter sets `disable-model-invocation: true`.

## Driving it with control-loam

Preconditions:

- A fresh render `r1`; `$C doctor r1` passes.

- **Listed.** Run `$C session r1 "Reply with the single word OK."`. The JSON `skills` array contains `catchup`, `fable-prompting` and `hypothesis-tree`.
- **Symlinked.** `ls -l <root>/r1/render/.claude/skills/` shows each as a symlink into `../../.agents/skills/`.
- **Proof.** The session `.jsonl` in evidence; its `init` event carries the full list.

## Gotchas

- The `skills` array also holds Claude Code built-ins (`verify`, `run`, `debug` and others); check for the seed names, not the count.
- User-level skills and plugins are absent because sessions use `--setting-sources project,local`. A user's real session lists more.
- The `skills` array holds every user-invocable skill, including one with `disable-model-invocation: true` that the model's own skill listing leaves out. **Listed** does not show which skills Claude can pick.
