# CLAUDE.md — Loam

@AGENTS.md

## Claude-specific environment

The root `.claude/` path is a symlink to `seed/.claude/`. Editing either path
changes the same shipped Claude harness. The root `.codex/` path is likewise a
symlink to `seed/.codex/`.

## Claude-specific gotchas

- Hooks receive a JSON envelope on standard input. They do not receive a
  `CLAUDE_TOOL_NAME` environment variable.
- Hook event and matcher names are exact. A wrong name fails silently.
- A rule's `paths:` frontmatter fires when Claude reads a matching file, not
  when Claude writes one.

Believe in yourself.
