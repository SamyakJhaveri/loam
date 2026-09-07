# Current official Claude Code docs: lean-setup research

Fetched 2026-08-28 from `code.claude.com/docs` as raw Markdown (`<page>.md`), not from memory.
Page inventory taken from `https://code.claude.com/docs/sitemap.xml` and `https://code.claude.com/docs/llms.txt`.
Raw copies of every page cited here are saved under `/private/tmp/claude-501/-Users-samyakjhaveri-Desktop-loam/cc00b778-e3bb-4c86-b999-2855b574fdf2/scratchpad/ccdocs/`.

Every claim below is sourced to a doc URL.
Where the docs are silent, this file says so rather than filling the gap.

---

## 0. Existence checks (asked explicitly)

| Thing | Verdict | Evidence |
|---|---|---|
| `/doctor` | **CONFIRMED** | https://code.claude.com/docs/en/commands (`All commands` table), https://code.claude.com/docs/en/debug-your-config |
| `/checkup` | **CONFIRMED** (documented as an *alias* of `/doctor`, not a separate command) | https://code.claude.com/docs/en/commands - "Alias: `/checkup`" |
| `claude doctor` (terminal, no session) | **CONFIRMED** | https://code.claude.com/docs/en/commands, https://code.claude.com/docs/en/debug-your-config |
| `claude plugin eval` | **NOT FOUND** in the official docs | See below |
| `claude plugin validate` | **CONFIRMED** (this is the real validation command) | https://code.claude.com/docs/en/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest |

### `claude plugin eval` - NOT FOUND, with the nuance

I checked four ways and found nothing:

1. `llms.txt` (the complete official page index) has no eval page.
2. Grep for `plugin eval` across all 34 downloaded doc pages: zero hits.
3. Enumerated every `claude plugin <subcommand>` string appearing anywhere in the docs. The complete documented set is:
   `init`, `install`, `uninstall`, `prune`, `enable`, `disable`, `update`, `list`, `details`, `tag`, `marketplace`, `validate`.
   No `eval`.
   Source: https://code.claude.com/docs/en/plugins-reference#cli-commands-reference
4. Web search surfaced only third-party plugins named "eval". One third-party README (`jameskomo/config-drift-checker`) refers to "Anthropic's own claude plugin eval format", which suggests the feature may exist behind early access, but **no Anthropic-published documentation backs it**.

The only official mention of *evals* at all is skill evals via skill-creator, which stores cases in `evals/evals.json` inside the skill directory:
https://code.claude.com/docs/en/skills#run-evals-with-skill-creator

**Treat `claude plugin eval` as unverifiable from official sources.**
Do not build template machinery on it. `claude plugin validate` is the documented, currently-shipping analogue.

---

## 1. CLAUDE.md and memory

Primary source: https://code.claude.com/docs/en/memory

### (a) Lean guidance

The docs now define **two** memory systems and are explicit that CLAUDE.md is context, not enforcement:

> "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead."
> https://code.claude.com/docs/en/memory#claude-md-vs-auto-memory

Hard numbers the docs give:

- **Target under 200 lines per CLAUDE.md file.** "Longer files consume more context and reduce adherence."
  https://code.claude.com/docs/en/memory#write-effective-instructions
- Claude Code loads a CLAUDE.md up to 4 MiB in full and *skips* a larger file.
  https://code.claude.com/docs/en/memory#how-it-works
- `@path` imports do **not** save context. "Imported files are expanded and loaded into context at launch." Max import depth is 4 hops.
  https://code.claude.com/docs/en/memory#import-additional-files
- Import parsing skips code spans and fenced blocks, so `` `@README` `` in backticks stays literal.
  Same URL.

What belongs in CLAUDE.md, per the docs: build commands, conventions, project layout, "always do X" rules.
What does NOT: "If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead."
https://code.claude.com/docs/en/memory#when-to-add-to-claude-md

The docs also state block-level HTML comments (`<!-- ... -->`) in CLAUDE.md are **stripped before injection**, so they cost zero context. Useful for maintainer notes.
https://code.claude.com/docs/en/memory#how-claude-md-files-load

### Auto memory (native) - supersedes custom memory docs

This is the biggest "harness now provides it natively" item for memory.

- On by default (`autoMemoryEnabled`). Toggle in `/memory` or per-project settings; env kill switch `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- Storage: `~/.claude/projects/<project>/memory/`, keyed off the **git repository**, so all worktrees share one memory dir.
- Structure is prescribed: a `MEMORY.md` index plus one topic file per memory.
- Four `type` values in frontmatter: `user`, `feedback`, `project`, `reference`.
- Only the **first 200 lines or 25KB** of `MEMORY.md` load at session start. Topic files load on demand.
- Claude Code actively enforces this: it measures `MEMORY.md` after each write and returns an error telling Claude to rewrite the index when it is over the limit.
- Auto memory files are excluded from the `cleanupPeriodDays` retention sweep.
- A `modified` ISO-8601 frontmatter timestamp is stamped automatically (v2.1.214+).
- `autoMemoryDirectory` relocates it.

https://code.claude.com/docs/en/memory#auto-memory

**Supersession note:** the format loam-style templates hand-roll (a `MEMORY.md` index, one fact per file, typed frontmatter, a "dream"/consolidation skill to prune it) is now the *native* format and the harness enforces the index budget itself. A custom `docs/MEMORY.md` explaining the convention is largely redundant with https://code.claude.com/docs/en/memory#auto-memory. A custom consolidation skill still has room, because the docs describe the reminder/error but not a prune workflow.

Also note: **subagents do not inherit the main conversation's auto memory.** A subagent gets its own only via the `memory:` frontmatter field.
https://code.claude.com/docs/en/memory#how-it-works

### AGENTS.md

Claude Code reads `CLAUDE.md`, **not** `AGENTS.md`. The documented bridges are a `@AGENTS.md` import or a symlink (`ln -s AGENTS.md CLAUDE.md`). On Windows use the import, since symlinks need Administrator or Developer Mode.
There is also a `/import` command (v2.1.213+) that pulls another agent's config in.
https://code.claude.com/docs/en/memory#agents-md

---

## 2. Rules and nested CLAUDE.md

Primary source: https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/

### (a) Lean guidance

- `.claude/rules/*.md`, discovered **recursively**, so subdirectories like `frontend/` work.
- Rules **without** `paths:` frontmatter load at launch "with the same priority as `.claude/CLAUDE.md`". They are not free.
- Rules **with** `paths:` load only when Claude works with matching files.
- User-level rules live in `~/.claude/rules/` and load *before* project rules, giving project rules higher priority.
- `.claude/rules/` supports symlinks, including circular-symlink detection. This is the documented way to share one rule set across projects.

The docs draw the CLAUDE.md / rules / skills line explicitly:

> "Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead."
> Same URL.

And the three-way comparison table is at https://code.claude.com/docs/en/features-overview#compare-similar-features (the "CLAUDE.md vs Rules vs Skills" tab).

### The `paths:` trigger - what the docs actually say

> "Path-scoped rules trigger when Claude **reads** files matching the pattern, not on every tool use."
> https://code.claude.com/docs/en/memory#path-specific-rules

This **confirms** the existing loam known-issue: `paths:` fires on Read, not Write.
The docs state the read-trigger positively; they do not discuss the authoring/Write blind spot. The loam rule remains a correct and non-redundant inference.

New constraints not previously captured:

- Brace expansion is budgeted: one rule's whole `paths` list shares a budget of **1,000 expanded patterns and 4 MiB**. Over-budget patterns are used unexpanded and their literal braces match nothing.
- A `[` that cannot parse as a bracket expression makes that pattern match nothing (escape as `\[`).

### Nested CLAUDE.md load order

- CLAUDE.md and CLAUDE.local.md load from cwd **and every directory above it**, at launch.
- Files in **subdirectories** load on demand when Claude reads files there.
- Ordering is filesystem-root-down, so the file closest to your launch dir is read last. Within a directory, `CLAUDE.local.md` is appended after `CLAUDE.md`.
- All files are **concatenated, not overridden**.
- `claudeMdExcludes` (glob, matched against absolute paths, merges across settings layers) skips unwanted ancestor files. Managed-policy CLAUDE.md cannot be excluded.

https://code.claude.com/docs/en/memory#how-claude-md-files-load

**Compaction behavior:** project-root CLAUDE.md is re-read from disk and re-injected after `/compact`. Nested CLAUDE.md and `paths:` rules reload only as Claude reads matching files again.
https://code.claude.com/docs/en/memory#instructions-seem-lost-after-compact

### Debugging hook for instruction loading

There is a native `InstructionsLoaded` hook event that logs exactly which instruction files loaded, when, and why, with matcher values `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`.
https://code.claude.com/docs/en/hooks#instructionsloaded

This supersedes any custom "which rules loaded?" debugging script.

---

## 3. Skills

Primary source: https://code.claude.com/docs/en/skills

### (a) Lean guidance

Skills are described as "the most flexible extension" and the default home for anything procedural.
https://code.claude.com/docs/en/features-overview

Size guidance the docs give:

- "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files."
  https://code.claude.com/docs/en/skills#add-supporting-files
- Body conciseness matters *more* than for a one-shot prompt, because "once a skill loads, its content stays in context across turns, so every line is a recurring token cost."
  https://code.claude.com/docs/en/skills#types-of-skill-content

### CRITICAL FINDING: `auto-activate` is not a real field

I grepped case-insensitively for `auto-activate` and `auto_activate` across all 34 downloaded doc pages, including the full frontmatter reference table. **Zero hits.**

The complete documented frontmatter field list is:
`name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`.
https://code.claude.com/docs/en/skills#frontmatter-reference

The real invocation-control fields are:

| Frontmatter | You can invoke | Claude can invoke | Context cost |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context |
| `disable-model-invocation: true` | Yes | No | **Description not in context** |
| `user-invocable: false` | No | Yes | Description always in context |

https://code.claude.com/docs/en/skills#control-who-invokes-a-skill

**Implication for a template that ships `auto-activate: false` on ~13 skills:** the field is inert. Those skills are still model-invocable and their descriptions still consume the listing budget every session. The correct field is `disable-model-invocation: true`, which additionally removes the description from context. This is a real, measurable context leak, not a cosmetic naming issue.

Two corroborating details: malformed or unknown frontmatter does not error loudly ("Claude Code loads the skill body with empty metadata, so `/skill-name` still works but Claude has no `description` to match against", https://code.claude.com/docs/en/skills#skill-not-triggering), and `disable-model-invocation` also prevents preloading into subagents and prevents a scheduled task from firing the skill.

### Skill listing budget (the real cost model)

- The listing "always contains every skill name", but descriptions are truncated to fit a budget of **1% of the model's context window**.
- On overflow, Claude Code **drops descriptions starting with the skills you invoke least**.
- Each entry's combined `description` + `when_to_use` is capped at **1,536 characters** regardless of budget.
- Tuning knobs: `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`.
- `/doctor` estimates the listing's context cost and its biggest contributors.

https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short

**This directly validates the "60+ skills competing for auto-invocation" concern in loam's known-issues, and gives it a native diagnostic (`/doctor`) plus a native remedy (`skillOverrides: "name-only"`).**

### `skillOverrides` - settings-side control without editing files

Four states: `"on"`, `"name-only"`, `"user-invocable-only"`, `"off"`.
Written for you by the `/skills` menu (Space cycles, Enter saves to `.claude/settings.local.json`).
Does **not** affect plugin skills.
https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings

This supersedes a custom skill-tiering convention for third-party or checked-in skills you do not want to edit.

### Skills as subagents: `context: fork`

`context: fork` runs the skill in a forked subagent; the SKILL.md body becomes the prompt.
Companion fields: `agent:` (which subagent type), `background:` (default `true`; set `false` to block the turn).

Two gotchas the docs call out:

- A backgrounded fork runs with the **narrower background-subagent tool set**. If your skill needs a tool outside it, set `background: false`.
- Background fork edits land **outside session checkpoints**, so `/rewind` will not undo them.
- `context: fork` "only makes sense for skills with explicit instructions", not for guideline-style reference skills.

https://code.claude.com/docs/en/skills#run-skills-in-a-subagent

### Bundled skills (what ships natively now)

`/doctor`, `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`, `/run`, `/verify`, `/run-skill-generator`, `/deep-research`, `/simplify`.
Turn off with `disableBundledSkills` (which spares `/doctor`).
https://code.claude.com/docs/en/skills#bundled-skills

A project skill with the same name **overrides** a bundled skill, but never the bundled skill's aliases. So a custom `.claude/skills/code-review/` replaces `/code-review` while `/review` still runs the bundled one. That is a silent split-brain worth knowing before naming a template skill after a bundled one.
https://code.claude.com/docs/en/skills#where-skills-live

### Naming and discovery

- Command name comes from the **directory name** for personal/project skills. The `name:` field is only a display label there. For **plugin** skills, `name:` sets the last command segment.
- Nested `.claude/skills/` below cwd load lazily, on first read/edit in that subdirectory, and get directory-qualified names like `/apps/web:deploy`.
- Precedence: enterprise > personal > project. Plugin skills are namespaced so they never collide.
- Skill dirs support symlinks; the same target reachable twice loads once.
- `synced` is a reserved folder name.
- Live change detection: edits to `SKILL.md` are picked up without restart. Creating a *new* top-level skills dir needs a restart.

https://code.claude.com/docs/en/skills#where-skills-live

### Portability constraint

Outside Claude Code (claude.ai upload, Skills API, `package_skill.py`), only six fields are legal: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Anything else is a **hard error**, not an ignored field.
https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code

---

## 4. Custom agents / subagents

Primary sources: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/agents

### (a) Lean guidance

`/docs/en/agents` is a new comparison page: subagents vs agent view vs agent teams vs dynamic workflows.
Use a subagent when "a side task would flood your main conversation with search results, logs, or file contents you won't reference again."
https://code.claude.com/docs/en/agents

### Complete frontmatter field list (verified against the table)

Only `name` and `description` are required.

| Field | Notes |
|---|---|
| `name` | lowercase + hyphens; cannot contain `:`; hooks receive it as `agent_type` |
| `description` | when Claude should delegate |
| `tools` | inherits all if omitted; do **not** list `Skill` here, use `skills:` |
| `disallowedTools` | subtractive |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit` (default) |
| `permissionMode` | `default`/`acceptEdits`/`auto`/`dontAsk`/`bypassPermissions`/`plan`/`manual` |
| `maxTurns` | partial output marked as such (v2.1.246+) |
| `skills` | preloads **full skill content**, not just descriptions |
| `mcpServers` | name reference or inline definition |
| `hooks` | subagent-scoped lifecycle hooks |
| `memory` | `user`, `project`, or `local` - per-subagent persistent memory |
| `background` | force background |
| `effort` | `low`/`medium`/`high`/`xhigh`/`max` |
| `isolation` | only valid value is `worktree` |
| `color` | display only |
| `initialPrompt` | auto-submitted first turn when run as main session agent via `--agent` |

https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields

**Plugin-shipped agents are restricted.** They support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`. For security, `hooks`, `mcpServers`, and `permissionMode` are **not supported** in plugin agents.
https://code.claude.com/docs/en/plugins-reference#agents

### `isolation: worktree`

Gives the subagent a temporary git worktree branched by default from your **default branch**, not the parent's HEAD. Auto-cleaned if the subagent makes no changes.
Enforcement is real: Bash commands that redirect git into the main checkout are blocked, and commands whose shape cannot be verified as staying inside the worktree are refused outright.
https://code.claude.com/docs/en/sub-agents#write-subagent-files

Permissions can gate it: `Agent(isolation:worktree)`, `Agent(model:opus)`. One rule per parameter; `*` wildcard supported.
https://code.claude.com/docs/en/permissions

### Nested subagents

- Default depth is **3 layers** below the main conversation (as of v2.1.219).
- Controlled by `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. Set `1` to disable nesting.
- At the depth limit the `Agent` tool is withheld entirely (except in a fork, where it stays listed but errors).
- To keep one agent read-only, omit `Agent` from `tools` or add it to `disallowedTools`.
- Separate concurrency cap: **20 running subagents**, via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. Sessions with ultracode are exempt.

https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents

### What loads in a subagent (context accounting)

A non-fork subagent gets: its own system prompt (not the full CC system prompt), the delegation task message, **the entire CLAUDE.md hierarchy including rules and CLAUDE.local.md**, git status, preloaded `skills:` content, and a sibling roster when `SendMessage` is available.

**Explore and Plan are the only agents that skip CLAUDE.md and git status, and there is no setting to change that.**

Never reaches a non-fork subagent: output style, the main conversation's auto memory, the parent's context window size.
https://code.claude.com/docs/en/sub-agents#what-loads-at-startup

This matters for a template: your CLAUDE.md and every always-loaded rule is paid for again in **every** subagent. Trimming the always-loaded layer has multiplied benefit.

### Duplicate agent names

If two files in the same `agents/` directory declare the same `name`, only one loads, chosen by **filesystem read order, with no documented precedence**. `/doctor` reports these.
https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope

### Files silently skipped

No `name` (treated as documentation), a `name` starting with `-` or containing `:`, a `name` without `description`, or unparseable YAML. All silent in-session; reasons go to the `--debug` log.
Pre-flight check: `claude plugin validate .claude/agents` (v2.1.233+).
https://code.claude.com/docs/en/sub-agents#subagent-files-claude-code-skips

### Model resolution order

1. `CLAUDE_CODE_SUBAGENT_MODEL` env var
2. per-invocation `model` parameter
3. frontmatter `model`
4. main conversation's model

Subagents now inherit the main conversation's extended-thinking setting (v2.1.198+). There is no per-subagent thinking setting.
https://code.claude.com/docs/en/sub-agents#choose-a-model

---

## 5. Hooks

Primary sources: https://code.claude.com/docs/en/hooks (reference) and https://code.claude.com/docs/en/hooks-guide (guide)

### (a) Lean guidance

The docs are unambiguous that hooks are the enforcement layer:

> "Put guardrails in hooks. An instruction like 'never edit `.env`' in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement."
> https://code.claude.com/docs/en/features-overview#compare-similar-features

Context cost of a hook is **zero unless it returns output**. Same URL.

### JSON stdin contract - CONFIRMED

> "Command hooks receive JSON data via stdin... For command hooks, this JSON arrives via stdin. For HTTP hooks, it arrives as the POST request body."
> https://code.claude.com/docs/en/hooks#common-input-fields

Common input fields on every event: `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`.
Inside a subagent, add `agent_id` and `agent_type`.
Tool events add `tool_name`, `tool_input`, `tool_use_id`.

**This confirms the existing loam known-issue: there is no `CLAUDE_TOOL_NAME` env var.** The docs go further and state explicitly: "There is no `$CLAUDE_MODEL` environment variable", and only `SessionStart` can receive a `model` field at all. Also, Claude Code strips all `OTEL_*` exporter variables from every subprocess it spawns, hooks included.
Same URL.

Two env vars that *are* available to hook commands: `$CLAUDE_EFFORT` and `$CLAUDE_PROJECT_DIR`.

### Output contract

- Exit 0 = success. **stdout is parsed as JSON if its first non-whitespace character is `{`**, otherwise treated as plain text. A JSON array or a quoted JSON string is treated as plain text.
- Plain-text stdout is added as context Claude sees only for `UserPromptSubmit`, `UserPromptExpansion`, and `SessionStart`. For all other events it goes to the debug log only.
- Exit 2 = block. This is the one outcome JSON cannot override.
- JSON output fields are read on **every** exit code, not just 0.
- A parsed object failing schema validation is a non-blocking error on any code except 2.

https://code.claude.com/docs/en/hooks#exit-code-output

### settings.json wiring

Three levels of nesting: **hook event -> matcher group -> hook handler**.

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "/path/to/lint-check.sh" } ] }
    ]
  }
}
```

https://code.claude.com/docs/en/hooks#configuration

Locations and scope: `~/.claude/settings.json` (all projects), `.claude/settings.json` (project, committable), `.claude/settings.local.json` (project, gitignored), managed policy, plugin `hooks/hooks.json`, **skill frontmatter** (rest of session once invoked), **subagent frontmatter** (while that subagent runs).
https://code.claude.com/docs/en/hooks#hook-locations

Hooks **merge across settings levels** rather than replacing. `disableAllHooks` cannot disable managed hooks from outside managed settings.

Hooks from settings, managed policy, and plugins **also run inside subagents**.

### Matcher semantics (a real footgun)

- `"*"`, `""`, or omitted: match all.
- Only letters/digits/`_`/`-`/spaces/`,`/`|`: exact string or `|`- or `,`-separated list of exact strings.
- **Anything else: unanchored JavaScript regex.** So `Edit.*` also matches `NotebookEdit`. Anchor with `^...$`.
- `FileChanged` and `StopFailure` use a narrower exact set (letters, digits, `_`, `|` only), so a hyphen there falls back to regex.
- A `matcher` on an event without matcher support is **silently ignored**.

https://code.claude.com/docs/en/hooks#matcher-patterns

Finer filtering per handler: the `if` field uses permission-rule syntax against tool name and args together, e.g. `"Bash(git *)"` or `"Edit(*.ts)"`.

### Event inventory (much larger than commonly assumed)

`SessionStart`, `Setup`, `InstructionsLoaded`, `UserPromptSubmit`, `UserPromptExpansion`, `MessageDisplay`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `SessionEnd`, `Elicitation`, `ElicitationResult`.
https://code.claude.com/docs/en/hooks#hook-events

Handler types are no longer just shell commands: **command, HTTP, MCP tool call, prompt, and agent**.
- Prompt-based hooks: https://code.claude.com/docs/en/hooks#prompt-based-hooks
- Agent-based hooks: https://code.claude.com/docs/en/hooks#agent-based-hooks
- Async/background hooks: https://code.claude.com/docs/en/hooks#run-hooks-in-the-background

**Supersession:** a custom "stop-verify gate" implemented as a shell script can now be a *prompt-based* Stop hook (model-evaluated, no script) or an *agent-based* hook. And a template that ships only `type: command` hooks is using one of five documented handler types.

---

## 6. Plugins, marketplaces, validation

Primary sources: https://code.claude.com/docs/en/plugins, https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/plugin-marketplaces

### (a) Lean guidance

The documented decision rule is short:

| Approach | Skill names | Best for |
|---|---|---|
| Standalone `.claude/` | `/hello` | Personal workflows, project-specific customization, quick experiments |
| Plugin | `/plugin-name:hello` | Sharing, distributing, versioned releases, reuse across projects |

> "Start with standalone configuration in `.claude/` for quick iteration, then convert to a plugin when you're ready to share."
> https://code.claude.com/docs/en/plugins#when-to-use-plugins-vs-standalone-configuration

The trigger in the build-over-time table is precise: **"A second repository needs the same setup -> Package it as a plugin."**
https://code.claude.com/docs/en/features-overview#build-your-setup-over-time

**This is the most template-relevant sentence in the whole doc set.** A Copier template that renders files into each project is solving the "second repository needs the same setup" problem with copying, where the docs now point at plugins plus marketplaces (which give versioned releases, release channels, and background auto-updates that a copy-based template must reimplement as a sync tool).

### Skills-directory plugins (a lighter packaging path)

Adding `.claude-plugin/plugin.json` to a skill folder makes it load as a plugin named `<name>@skills-dir`, letting it bundle agents, hooks, and MCP servers with no marketplace.
https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins
https://code.claude.com/docs/en/skills#where-skills-live

### `claude plugin validate` - supersedes custom verify scripts

This is the concrete replacement for a hand-rolled `verify-template.sh` frontmatter check.

| To check | Run |
|---|---|
| A plugin with `plugin.json` | `claude plugin validate ./plugins/my-plugin` |
| One directory of skills/agents/commands | `claude plugin validate .claude/skills` |
| A project's three dirs at once | `claude plugin validate .claude` |
| Your user-level dirs | `claude plugin validate ~/.claude` |

Reports `YAML frontmatter failed to parse: ...` and `Invalid JSON syntax: ...` on `hooks/hooks.json`. Clean run prints `Validation passed`. Requires v2.1.233+.
https://code.claude.com/docs/en/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest

**Two limits that matter for a symlink-heavy repo:** `claude plugin validate` does **not follow symlinks** inside the named directory, and if the directory you name (or its parent `.claude`) is itself a symlink, it reports an error and checks nothing. A repo whose `.claude/` is a symlink to `seed/.claude/` must name the real directory.
https://code.claude.com/docs/en/plugin-marketplaces#check-files-behind-symlinks

It also does **not** flag a file whose frontmatter parses but has no `name`. So a custom lint still has room for semantic checks (description quality, required fields, naming conventions) - just not for YAML/JSON parse checks.

### Marketplace distribution features worth knowing

Sources: relative paths, GitHub repos, generic git, git subdirectories, npm packages, zip archives, and `command` sources.
Release channels and version pinning: https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels
Org-level distribution and `allowManagedHooksOnly` restrictions: https://code.claude.com/docs/en/plugin-marketplaces#distribute-through-organization-settings

`claude plugin marketplace` subcommands: `add`, `list`, `remove`, `update`.
https://code.claude.com/docs/en/plugin-marketplaces#manage-marketplaces-from-the-cli

---

## 7. `/doctor` and `/checkup` - what they now do natively

Full description: https://code.claude.com/docs/en/commands (search `/doctor` in the All commands table)

`/doctor` is now a **bundled skill**, not a built-in command (changed in v2.1.205). Its checkup covers:

- Installation health: duplicate or leftover installs, `PATH` problems, unparseable settings files
- **Unused skills, MCP servers, and plugins versus their context cost**
- **Slow hooks**
- Newer version on your release channel
- **Deduplicates local `CLAUDE.md` files against checked-in ones**
- **Trims checked-in `CLAUDE.md` by cutting content Claude could derive from the codebase**
- **Migrates the always-loaded guidance that remains into skills and nested CLAUDE.md files that load on demand**
- Duplicate subagent names in the same directory
- Offers auto mode as default; offers to pre-approve frequently denied read-only commands

It reports findings first and asks before changing anything.
`claude doctor` from the terminal prints read-only diagnostics without a session.
The CLAUDE.md trim check requires v2.1.206+.

**Supersession:** the trim/migrate behavior is precisely the "L0 budget" job a template rule does by convention. `/doctor` now does it mechanically, and it knows the actual context cost of the skill listing, which a static rule cannot. It is the single highest-value thing to run against an existing heavy setup.

Related native diagnostics, all in https://code.claude.com/docs/en/debug-your-config:
`/context` (what actually loaded, by category), `/skills`, `/hooks`, `/mcp`, `/permissions`, `/status` (active settings sources), `/debug [issue]`.

---

## 8. Built-in `/code-review` and `/ultrareview`

Sources: https://code.claude.com/docs/en/code-review#review-a-diff-locally and https://code.claude.com/docs/en/ultrareview

### What ships natively

`/code-review` (alias `/review`) reviews your branch's commits ahead of upstream plus uncommitted changes. It "reports correctness bugs and reuse, simplification, and efficiency cleanups."

- Runs as a **background forked subagent with its own context window**, so it does not fill your conversation.
- Target argument: a file path, PR number, branch name, or ref range like `main...my-feature`.
- Flags: `--fix` (apply findings to working tree), `--comment` (post inline PR comments), `--post`.
- Effort tuning: `/code-review high`. At `low`/`medium` it reports only high-confidence findings; `high` through `max` broaden coverage. It **remembers the last level you typed across sessions**.
- Reads your `CLAUDE.md` like any session. Does **not** read `REVIEW.md` (that is the GitHub App path).
- `--fix` edits from a background review are outside checkpoints, so `/rewind` will not undo them.
- Claude can start it on its own; suppress with `skillOverrides: {"code-review": "user-invocable-only"}`.
- `/simplify` is a separate cleanup-only review that applies fixes without hunting bugs.

`/code-review ultra` escalates to cloud **ultrareview**: current branch against the default branch plus uncommitted and staged changes. Requires a claude.ai account; unavailable on Bedrock, Google Cloud Agent Platform, Microsoft Foundry, or with Zero Data Retention. Falls back to a local review when unavailable.
Non-interactive: `claude -p '/code-review ultra'`.
Comparison table: https://code.claude.com/docs/en/ultrareview#how-ultrareview-compares-to-code-review

### Supersession assessment

A template shipping a multi-agent review swarm (diff-reviewer, security-scanner, self-critic, code-simplifier, pr-review) now overlaps heavily with `/code-review`, which is background, context-isolated, effort-tunable, CLAUDE.md-aware, and has a `--fix` path. `/simplify` covers the code-simplifier role outright.

Where custom agents still earn their place, per the docs' own framing: `/code-review` reviews *code*. It has no documented plan-review, spec-audit, or consistency-checking mode. Adversarial *plan* review before implementation is not a bundled capability.

One naming hazard: a project skill named `code-review` overrides the bundled `/code-review` but not its `/review` alias, producing two different reviewers under two names.
https://code.claude.com/docs/en/skills#where-skills-live

---

## 9. Workflows, `/goal`, and loops

### `/goal` - CONFIRMED, and it is a native Ralph loop

https://code.claude.com/docs/en/goal

> "`/goal` is a wrapper around a session-scoped prompt-based Stop hook."

Mechanics:
- One goal per session; setting it **starts a turn immediately** with the condition as the directive.
- After each turn, the condition plus conversation is sent to your configured **small fast model** (Haiku on the Claude API) which returns `Not yet met` / `Met` / `Impossible`, each with a reason.
- The evaluator **does not run commands or read files**. It judges only what Claude surfaced in the transcript. So conditions must be provable from Claude's own output.
- Condition cap: 4,000 characters. Bound runtime with a clause like "or stop after 20 turns".
- Stalls (no tool use for several turns) stop the loop with a warning, goal still set.
- Unrecoverable errors (auth failure, exhausted credits, and two others) clear the goal.
- Survives resume via `--continue`, `--resume`, and the session picker; turn count and timers reset.
- Works with `-p`: `claude -p "/goal ..."`. Add `--output-format stream-json --verbose` to see progress.
- `/goal clear` (aliases: `stop`, `off`, `reset`, `none`, `cancel`).

The three-way comparison of session-continuation approaches:

| Approach | Next turn starts when | Stops when |
|---|---|---|
| `/goal` | previous turn finishes, or an idle check-in comes due | model says met/impossible, unrecoverable error, or `/goal clear` |
| `/loop` | a time interval elapses | you stop it, or Claude decides work is done |
| Stop hook | previous turn finishes | your own script or prompt decides |

https://code.claude.com/docs/en/goal#compare-ways-to-keep-a-session-running

`/goal` and auto mode are complementary: auto mode removes per-*tool* prompts, `/goal` removes per-*turn* prompts.

`/loop` reference: https://code.claude.com/docs/en/scheduled-tasks#run-a-prompt-repeatedly-with-loop

### Dynamic workflows

https://code.claude.com/docs/en/workflows

The distinguishing axis is **who holds the plan**:

| | Subagents | Skills | Agent teams | Workflows |
|---|---|---|---|---|
| What it is | a worker Claude spawns | instructions Claude follows | lead supervising peer sessions | a script the runtime executes |
| Who decides next | Claude, turn by turn | Claude | the lead, turn by turn | the script |
| Intermediate results live in | context window | context window | shared task list | script variables |
| Scale | a few per turn | same | a handful of peers | **dozens to hundreds per run** |
| Interruption | restarts the turn | restarts the turn | teammates keep running | **resumable** |

https://code.claude.com/docs/en/workflows#when-to-use-a-workflow

Key capability: a workflow "can have independent agents adversarially review each other's findings before they're reported, or draft a plan from several angles and weigh them against each other."

Entry points:
- Bundled: `/deep-research` (fan-out web search, cross-check, vote, cited report with unsurvived claims filtered out). Only runs when invoked.
- Ad hoc: include the keyword `ultracode` in your prompt, or just ask for "a workflow" in plain words.
- Session-wide: `/effort ultracode`.
- Save a good run as a reusable command by pressing `s` in the `/workflows` progress view.
- Distributable in a plugin: https://code.claude.com/docs/en/workflows#distribute-a-workflow-in-a-plugin
- Monitor with `/workflows`.

**Supersession:** a custom "critique swarm" or "multi-wave validation" skill that spawns N reviewers and synthesizes is exactly the dynamic-workflow use case, with the workflow version being resumable, background, and out-of-context. A template's hand-rolled fan-out keeps intermediate results in the context window; a workflow does not.

### Related native parallelism

- Agent teams (experimental, disabled by default): https://code.claude.com/docs/en/agent-teams
- Agent view (`claude agents`, research preview): https://code.claude.com/docs/en/agent-view
- Cross-session messaging: https://code.claude.com/docs/en/cross-session-messaging
- `/batch` - bundled skill splitting one change into 5-30 worktree-isolated subagents each opening a PR: https://code.claude.com/docs/en/agents
- Worktrees: https://code.claude.com/docs/en/worktrees
- Checking on work: `claude agents`, `/tasks`, `/workflows`. Note `/agents` no longer opens a panel as of v2.1.198; it just prints file locations.

---

## 10. Consolidated supersession list

Things the harness now provides natively that custom template machinery may duplicate:

| Custom machinery | Native replacement | URL |
|---|---|---|
| Hand-rolled memory format + docs | Auto memory: typed frontmatter, `MEMORY.md` index, enforced 200-line/25KB budget | https://code.claude.com/docs/en/memory#auto-memory |
| Custom CLAUDE.md size lint / L0 budget rule | `/doctor` trim + migrate-to-skills check | https://code.claude.com/docs/en/commands |
| `verify-template.sh` frontmatter/JSON parse checks | `claude plugin validate <dir>` | https://code.claude.com/docs/en/plugin-marketplaces#validate-a-plugin-or-a-directory-without-a-manifest |
| Custom skill-tiering via `auto-activate` | `disable-model-invocation` / `user-invocable` frontmatter, plus `skillOverrides` in settings | https://code.claude.com/docs/en/skills#control-who-invokes-a-skill |
| Custom code-review agent swarm | `/code-review` (background, forked, effort-tunable, `--fix`) and `/simplify` | https://code.claude.com/docs/en/code-review#review-a-diff-locally |
| Custom deep-review escalation | `/code-review ultra` -> cloud ultrareview | https://code.claude.com/docs/en/ultrareview |
| Custom critique-swarm / multi-wave validation skill | Dynamic workflows with adversarial cross-checking | https://code.claude.com/docs/en/workflows#when-to-use-a-workflow |
| Custom research skill with fan-out | `/deep-research` bundled workflow | https://code.claude.com/docs/en/workflows#bundled-workflows |
| Custom Ralph/keep-going loop | `/goal` (session-scoped prompt-based Stop hook) | https://code.claude.com/docs/en/goal |
| Custom "which rules loaded" debug script | `InstructionsLoaded` hook + `/context` | https://code.claude.com/docs/en/hooks#instructionsloaded |
| Custom shell stop-verify gate | Prompt-based or agent-based Stop hook | https://code.claude.com/docs/en/hooks#prompt-based-hooks |
| Custom app-launch/verify convention | `/run`, `/verify`, `/run-skill-generator` | https://code.claude.com/docs/en/skills#run-and-verify-your-app |
| Copier-based multi-repo distribution | Plugins + marketplaces with release channels and auto-update | https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels |
| Custom parallel-session coordination | Agent teams, agent view, cross-session messaging, `/batch` | https://code.claude.com/docs/en/agents |

Things that remain genuinely custom (no bundled equivalent found in the docs):

- Adversarial **plan** review and spec audit before implementation. `/code-review` reviews code, not plans.
- Domain-specific rules and conventions. That is what CLAUDE.md and `.claude/rules/` are for.
- Project-specific workflow staging, promotion between layers, and provenance/IP tooling.
- Memory *consolidation and pruning* as a workflow. The docs describe the budget and the error, not a prune procedure.
- Semantic skill linting (description quality, naming conventions). `claude plugin validate` only catches parse failures and does not flag a file whose frontmatter parses but lacks `name`.

---

## Appendix: full English page inventory

Retrieved from `https://code.claude.com/docs/sitemap.xml`. Pages most relevant to this research:

`memory`, `skills`, `sub-agents`, `agents`, `agent-teams`, `agent-view`, `hooks`, `hooks-guide`, `plugins`, `plugins-reference`, `plugin-marketplaces`, `plugin-dependencies`, `plugin-hints`, `plugin-relevance`, `discover-plugins`, `commands`, `settings`, `settings-reference`, `settings-example`, `debug-your-config`, `code-review`, `ultrareview`, `workflows`, `goal`, `scheduled-tasks`, `best-practices`, `features-overview`, `context-window`, `large-codebases`, `tools-reference`, `permissions`, `permission-modes`, `cli-reference`, `interactive-mode`, `cross-session-messaging`, `worktrees`, `routines`, `how-claude-code-works`, `glossary`.

Note there is **no** dedicated `/docs/en/rules` page. Rules are documented inside `memory`.
Note the slash-commands page is `commands`, not `slash-commands`.
