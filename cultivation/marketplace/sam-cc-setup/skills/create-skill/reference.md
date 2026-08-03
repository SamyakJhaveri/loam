# Skill System Reference

## Frontmatter Fields

All fields are specified in YAML frontmatter at the top of `SKILL.md`.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Kebab-case identifier; **display-only** for an ordinary skill — the `/slash-command` is derived from the **directory** name, not this field, so keep them equal by convention. (Exception: a plugin-root `SKILL.md` *does* take its command from this `name`.) |
| `description` | string | What the skill does. Claude uses this for auto-activation matching. Include action verbs and trigger phrases. |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `argument-hint` | string | — | Shown in autocomplete after the command name. Use `[brackets]` for placeholders. |
| `user-invocable` | boolean | `true` | If `false`, skill cannot be called via `/command`. Only auto-activates. (This field IS honored.) |
| `auto-activate` | boolean | — | **CLI-ignored / cosmetic** — the CLI does not read this field. Auto-invocation is steered entirely by `description`. Do not rely on it. |
| `disable-model-invocation` | boolean | `false` | *Documented* to stop model auto-invocation. ⚠️ A live bug ([#26251](https://github.com/anthropics/claude-code/issues/26251) / #38969) makes it ALSO block the `/command` slash invocation — do **not** add it to a user-invoked skill. |
| `allowed-tools` | string[] | none | **Pre-approves** the listed tools (auto-allows them for this skill without a permission prompt). It does NOT restrict — use `disallowed-tools` to restrict. |
| `disallowed-tools` | string[] | none | Blacklist of tools. Skill can use everything except these. |

### Invocation Control Matrix

> ⚠️ **Reflects the *documented* design, not current CLI behavior.** `auto-activate`
> is CLI-ignored (cosmetic), so the two `auto-activate: false` rows below do NOT work as
> written: auto-invocation is controlled by the `description`, and there is currently no
> reliable frontmatter flag for "manual-only" (`disable-model-invocation` breaks the slash
> command — see above).
> `user-invocable` is real and does work.

| `user-invocable` | `auto-activate` | Behavior |
|-------------------|-----------------|----------|
| `true` (default) | `true` (default) | Full access: slash command + auto-activates |
| `true` | `false` | Slash command only, never auto-activates |
| `false` | `true` | Auto-activate only, no slash command |
| `false` | `false` | Never runs (useless — avoid this) |

### Tool Permission Examples

```yaml
# Pre-approve reading/searching so they run without a permission prompt.
# (This does NOT block edits — see disallowed-tools below to actually confine.)
allowed-tools:
  - Read
  - Glob
  - Grep
  - Agent

# Actually restrict: block destructive tools regardless of user permissions.
disallowed-tools:
  - Bash
  - Write
  - Edit
```

## Variables

Variables are replaced at invocation time before Claude sees the content.

| Variable | Description | Available in |
|----------|-------------|-------------|
| `$ARGUMENTS` | Everything the user typed after `/command`. Empty string if no arguments. | SKILL.md |
| `$0`, `$1`, … | Positional arguments: `$0` is the **first** arg, `$1` the second, etc. (0-based, per current CLI docs) — **not** an alias for the whole `$ARGUMENTS` string. Verify in your installed CLI before relying on positional forms; prefer `$ARGUMENTS` when you want everything the user typed. | SKILL.md |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory. Use for referencing supporting files. | SKILL.md |
| `${CLAUDE_SESSION_ID}` | Unique ID for the current Claude Code session. | SKILL.md |

### Variable Usage

```markdown
# In SKILL.md

The user wants: $ARGUMENTS

Read `${CLAUDE_SKILL_DIR}/reference.md` for details.

Session: ${CLAUDE_SESSION_ID}
```

**Important**: `$ARGUMENTS` is the full argument string; `$0` / `$1` / … are the individual
positional args (`$0` = first, 0-based per current CLI docs), **not** aliases for the whole
string. Prefer `$ARGUMENTS` for the whole input, and verify positional forms in your installed
CLI before relying on them.

## Shell Injection

Embed live command output in SKILL.md using `!`backtick` ` syntax:

```markdown
Current branch: !`git branch --show-current`
Node version: !`node --version`
Changed files: !`git diff main --name-only`
```

**How it works:**
- Commands execute when the skill is activated (not at definition time)
- Output replaces the `!`command`` inline
- If the command fails, the error output is included instead
- Commands run in the current working directory

**Use cases:**
- Inject project state (git branch, recent commits, env vars)
- Generate dynamic context (file lists, config values)
- Pre-compute information Claude needs

**Caution:**
- Commands run with the user's permissions
- Keep commands fast — slow commands delay skill activation
- Don't use for side effects (the skill content is for context, not execution)

## File Structure

```
skills/
└── my-skill/
    ├── SKILL.md          # Required — main instructions (loaded on activation)
    ├── reference.md      # Optional — detailed reference (read on-demand)
    ├── examples.md       # Optional — code examples (read on-demand)
    └── scripts/          # Optional — bundled scripts
        └── check.sh
```

### Loading Behavior

- **SKILL.md**: Loaded into context when the skill activates (via slash command or auto-activation)
- **Supporting `.md` files**: NOT automatically loaded. Only read when SKILL.md tells Claude to read them via `${CLAUDE_SKILL_DIR}` references
- **Scripts/other files**: Available on disk but never auto-loaded. Referenced via `${CLAUDE_SKILL_DIR}`

This means:
- Keep SKILL.md focused — it's always loaded
- Put detailed references in separate files — they're only loaded when needed
- Supporting files don't cost context tokens unless explicitly read

## Permissions

Skills inherit the user's permission settings. A skill cannot bypass permission restrictions.

- If the user has `Bash` set to "ask", the skill will still prompt for Bash usage
- `allowed-tools` in frontmatter **pre-approves** the listed tools (auto-allows them for this skill without a prompt); it does not restrict
- `disallowed-tools` adds restrictions on top of user permissions

## Skill Resolution

When multiple skills could match:
1. Exact slash command match takes priority
2. For auto-activation, Claude evaluates all skill descriptions against the user's message
3. Multiple skills can auto-activate simultaneously if relevant
4. Project skills (`.claude/skills/`) and personal skills (`~/.claude/skills/`) are both searched

## Naming Conventions

- **Directory name**: kebab-case, matches `name` field exactly
- **SKILL.md**: Always uppercase `SKILL.md`
- **Supporting files**: lowercase kebab-case `.md` files
- **Scripts**: lowercase, appropriate extension (`.sh`, `.py`, `.ts`)
