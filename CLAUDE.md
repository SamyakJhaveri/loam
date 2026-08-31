# CLAUDE.md — Loam

@AGENTS.md

## Claude-specific environment

The root `.claude/` path is a symlink to `seed/.claude/`. Editing either path
changes the same shipped Claude harness.

## Claude-specific gotchas

- `claude plugin validate` refuses a symlinked `.claude` directory and does not
  follow internal symlinks. Validate the real directories, such as
  `seed/.claude` and `seed/.agents/skills`.
- Hooks receive a JSON envelope on standard input. They do not receive a
  `CLAUDE_TOOL_NAME` environment variable.
- Hook event and matcher names are exact. A wrong name fails silently.
- A rule's `paths:` frontmatter fires when Claude reads a matching file, not
  when Claude writes one.
- `auto-activate` is not a skill field. Use `disable-model-invocation: true` for
  a manual-only skill.
