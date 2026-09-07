# Codex harness research - official docs, fetched 2026-08-28

All facts below were fetched live this session from OpenAI's official documentation.
No claim here rests on model memory.

## 0. Docs moved (verify this before citing old URLs)

`https://developers.openai.com/codex/*` now returns **HTTP 308 Permanent Redirect** to
`https://learn.chatgpt.com/docs/*`.
Verified on three separate paths (`/codex`, `/codex/hooks`, `/codex/build-skills`).
The path segment `/codex/` is dropped in the redirect target: `developers.openai.com/codex/agent-configuration/agents-md`
becomes `learn.chatgpt.com/docs/agent-configuration/agents-md`.

Cite `learn.chatgpt.com/docs/...` going forward.

## 1. Headline answer

**The team's working premise is false.** "A plain AGENTS.md is all Codex consumes" was true
of early Codex CLI, but is not true today. Codex now supports a repo-checked-in `.codex/`
layer with config, hooks, subagent definitions, and execution rules, plus a separate
`.agents/skills/` tree. The loam `seed/.codex/` harness is closer to reality than expected.

The real problems are naming and one wrong directory, not the concept.

## 2. What Codex officially consumes from a repo today

| Path in repo | What it is | Doc URL |
|---|---|---|
| `AGENTS.md` (nested, any level) | Primary prose instructions | learn.chatgpt.com/docs/agent-configuration/agents-md |
| `AGENTS.override.md` | Higher-priority sibling of AGENTS.md | same |
| `.codex/config.toml` | Project-scoped config layer, trusted projects only | learn.chatgpt.com/docs/config-file/config-basic |
| `.codex/hooks.json` | Lifecycle hooks | learn.chatgpt.com/docs/hooks |
| `.codex/agents/<name>.toml` | Project-scoped custom agents / subagents | learn.chatgpt.com/docs/agent-configuration/subagents |
| `.codex/rules/<name>.rules` | Starlark execution policy | learn.chatgpt.com/docs/agent-configuration/rules |
| `.agents/skills/<skill>/SKILL.md` | Skills (repo scope) | learn.chatgpt.com/docs/build-skills |

### 2.1 AGENTS.md contract

Discovery order, quoted from the docs:

1. Global: `~/.codex/AGENTS.override.md` first, then `~/.codex/AGENTS.md`
2. Project: walks **from the Git root down to the current directory**, checking each level for
   `AGENTS.override.md`, then `AGENTS.md`, then configured fallback names
3. Merge: "Codex concatenates files from the root down, joining them with blank lines. Files
   closer to your current directory override earlier guidance because they appear later in the
   combined prompt."

Constraints:
- Size cap: combined files stop being added at `project_doc_max_bytes`, **32 KiB by default**.
- At most one instruction file per directory level is included.
- Empty files are skipped.
- Alternate names configurable via `project_doc_fallback_filenames`.

Note the merge semantics differ from Claude Code: Codex **concatenates the whole chain** and
relies on later-wins ordering. It does not pick a single nearest file.

Per the AGENTS.md spec site (agents.md, stewarded by the Agentic AI Foundation under the Linux
Foundation): "explicit user chat prompts override everything," and the format is plain Markdown
with no required fields.

### 2.2 Config layering and trust

Precedence, highest to lowest (learn.chatgpt.com/docs/config-file/config-basic):

1. CLI flags and `-c` / `--config` overrides
2. Project config `.codex/config.toml`, closest to cwd wins
3. Profile file `~/.codex/<profile>.config.toml`, selected with `-p/--profile`
4. User config `~/.codex/config.toml`
5. System config `/etc/codex/config.toml`
6. Built-in defaults

**Trust gate, quoted:** "If you mark a project as untrusted, Codex skips project-scoped
`.codex/` layers, including project-local config, hooks, and rules."

Set via the config-reference table:

```toml
[projects.<path>]
trust_level = "trusted"   # or "untrusted"
```

Project-scoped config "can't override machine-local provider, auth, host-owned app request
metadata, notification, configuration profile selection, or telemetry routing keys."

**This is the single biggest operational caveat for a template**: everything loam ships under
`.codex/` is inert in a freshly cloned, untrusted project until the user trusts it.

### 2.3 Hooks

Discovered "next to active config layers" as either `hooks.json` or inline `[hooks]` tables in
`config.toml`. Searched paths: `~/.codex/hooks.json`, `~/.codex/config.toml`,
`<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml`.

Documented events: `SessionStart`, `SessionEnd`, `PreToolUse`, `PostToolUse`,
`PermissionRequest`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`,
`SubagentStop`, `Stop`.

Schema:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "hooks": [
          { "type": "command", "command": "script path", "timeout": 600, "statusMessage": "optional" }
        ]
      }
    ]
  }
}
```

- Handler `type` values: `command` and `mcp_tool`.
- `"async": true` for background execution.
- Hooks receive JSON on **stdin** including `session_id`, `cwd`, `hook_event_name`.
- Hooks may return JSON on **stdout**: common fields `continue`, `stopReason`, `systemMessage`,
  `suppressOutput`; event-specific `additionalContext`, `permissionDecision`, `decision: "block"`.
  This is close enough to the Claude Code contract that the loam hook scripts are portable in shape.
- Enabled by default; disable with `[features] hooks = false`.
- **Trust:** non-managed hooks require review. "Use `/hooks` in the CLI to inspect hook sources,
  review new or changed hooks, trust hooks, or disable individual non-managed hooks."
  `--dangerously-bypass-hook-trust` skips persisted trust for automation.

### 2.4 Subagents / custom agents

Definition files: **one TOML file per agent**, in `~/.codex/agents/` (personal) or
`.codex/agents/` (project-scoped).

Required fields: `name`, `description`, `developer_instructions`.
Optional: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`,
and other `config.toml` keys.

Built-ins: `default`, `worker`, `explorer`. A custom agent with a matching name overrides the built-in.

Official example, verbatim:

```toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence."
model = "gpt-5.3-codex-spark"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode. Trace execution paths, cite files and symbols,
and avoid proposing fixes unless requested.
"""
```

Filename convention matches the agent name, but the `name` field is the source of truth.
Global knobs live in `[agents]`: `enabled`, `max_concurrent_threads_per_session`
(legacy alias `max_threads`), `default_subagent_model`, `default_subagent_reasoning_effort`,
`interrupt_message`, `<name>.config_file`, `<name>.description`.

### 2.5 Rules are NOT Claude-style markdown rules

This is the most important conceptual mismatch. Codex `rules` means **execution policy**:
`.rules` files in a `rules/` folder next to an active config layer, written in **Starlark**
(Python-like, side-effect free). Purpose, quoted: "Use rules to control which commands Codex can
run outside the sandbox." Decisions are `allow`, `prompt`, `forbidden`.

Project-local rules under `<repo>/.codex/rules/` load only when the `.codex/` layer is trusted.
Checkable with `codex execpolicy check --pretty --rules ~/.codex/rules/default.rules`.

There is **no Codex equivalent of `.claude/rules/*.md`**. Prose guidance has exactly one home in
Codex: AGENTS.md (plus skills).

### 2.6 Skills

Discovery paths, in hierarchy order:

| Scope | Path |
|---|---|
| REPO | `$CWD/.agents/skills` |
| REPO | `$REPO_ROOT/.agents/skills` |
| USER | `$HOME/.agents/skills` |
| ADMIN | `/etc/codex/skills` |
| SYSTEM | bundled with Codex |

Format is the same `SKILL.md` + YAML frontmatter (`name`, `description`) shape Claude Code uses,
with optional `scripts/`, `references/`, `assets/`, and `agents/openai.yaml`.
Invoked explicitly with `$skill-name` in Codex CLI (`@skill-name` in ChatGPT), or implicitly.
Per-skill enablement in config:

```toml
[skills.config]
skills.config.<index>.enabled = true
skills.config.<index>.path = "path to folder containing SKILL.md"
```

Note the path is `.agents/skills`, **not** `.codex/skills` and **not** `.claude/skills`.

### 2.7 MCP

Configured in `config.toml` under `[mcp_servers.<name>]`, user-level or project-level
(trusted projects only). Shared across ChatGPT desktop, Codex CLI, and the IDE extension.

- stdio: `command` (required), `args`, `env`, `env_vars`, `cwd`
- streamable HTTP: `url` (required), `auth`, `bearer_token_env_var`, `http_headers`
- also `enabled`, `default_tools_approval_mode`, `tools.<tool>.approval_mode`
- CLI: `codex mcp add <name> -- <command>`, `codex mcp list`, `codex mcp login <name>`

### 2.8 Custom prompts are deprecated

`~/.codex/prompts/*.md` with YAML frontmatter, invoked as `/prompts:<name>`.
Docs state plainly they are **deprecated in favor of skills**, because prompts are local-only and
explicit-invocation-only. Do not build anything new on them.

## 3. Verdict on what loam ships in `seed/.codex/`

Current contents: `config.toml`, `reassess-hooks.json`, `hooks/post-compact-recovery.sh`,
`rules/reassess-default.rules`, empty `agents/`, empty `mcp/`.

| Item | Verdict | Evidence |
|---|---|---|
| `.codex/config.toml` at repo root | **SUPPORTED** | config-basic precedence list, layer 2 |
| `default_permissions = "project-workspace"` | **SUPPORTED** | config-reference: names a permissions profile; built-ins `:read-only`, `:workspace`, `:danger-full-access` |
| `[permissions.X] extends = ":workspace"` | **SUPPORTED** | config-reference: `permissions.<name>.extends` |
| `[permissions.X.filesystem.":workspace_roots"]` with `deny` globs | **SUPPORTED** | config-reference: values `read`/`write`/`deny` |
| `[features] multi_agent = true` | **SUPPORTED** | config-reference: "Enable multi-agent collaboration tools (stable; on by default)" |
| `[agents] max_threads = 6` | **SUPPORTED but legacy** | config-reference: "Legacy alias for `agents.max_concurrent_threads_per_session`" |
| `[agents] max_depth = 1` | **NOT SUPPORTED** | absent from the documented `[agents]` key list; silently inert |
| `[mcp_servers.X] enabled/command/args` | **SUPPORTED** | extend/mcp + config-reference |
| `[mcp_servers.X] default_tools_approval_mode` | **SUPPORTED** | config-reference |
| `[mcp_servers.X.tools.Y] approval_mode` | **SUPPORTED** | config-reference |
| hooks.json schema (matcher / hooks / type command / timeout / statusMessage) | **SUPPORTED** | hooks page schema block, exact match |
| Events used: PreToolUse, PostToolUse, PostCompact, SessionStart, Stop | **SUPPORTED** | all five in the documented event list |
| **File named `reassess-hooks.json`** | **BROKEN** | Codex discovers `hooks.json` only. Current name is never loaded. |
| `.codex/rules/*.rules` in Starlark with `prefix_rule(...)` | **SUPPORTED in kind** | rules page: Starlark, `allow`/`prompt`/`forbidden`, project-local under `<repo>/.codex/rules/` when trusted |
| **File named `reassess-default.rules`** | **UNKNOWN** | rules page shows `default.rules` by example; I found no documented key stating which filenames auto-load from `rules/`. Needs a live `codex execpolicy check` to settle. |
| `.codex/agents/` directory (empty) | **SUPPORTED, unused** | subagents page: `.codex/agents/<name>.toml` is real. Loam ships zero agent files. |
| `.codex/mcp/` helper scripts dir (empty) | **N/A, harmless** | not a Codex-recognized path; only meaningful because `config.toml` invokes a script path there. The `memory` server currently points at `.codex/mcp/memory-server.sh`, which does not exist. |
| `.claude/rules/*.md` style prose rules for Codex | **NOT SUPPORTED** | Codex rules are execpolicy, not prose. Prose belongs in AGENTS.md. |
| Skills for Codex under `.claude/skills` or `.codex/skills` | **NOT SUPPORTED** | Codex reads `.agents/skills`. Loam's `config.toml` comment references `.agents/skills/agent-team`, but `seed/` ships no `.agents/` directory at all. |
| `~/.codex/prompts` slash commands | **DEPRECATED** | custom-prompts page |

### Concrete defects found

1. `reassess-hooks.json` will never load. Must be exactly `hooks.json`.
2. `agents.max_depth` is not a documented key.
3. `config.toml` references `.codex/mcp/memory-server.sh` and `.agents/skills/agent-team`;
   neither ships in `seed/`. Two dangling references.
4. Nothing in the template tells the user the `.codex/` layer is inert until the project is
   trusted, and that hooks need a separate `/hooks` trust step. A bootstrapped project will
   silently get none of this on first run.

## 4. Minimal lean Codex setup recommendation

Ranked by value per unit of maintenance. My recommendation is to ship tiers 1 and 2 by default
and treat tier 3 as opt-in.

**Tier 1, always ship (high value, zero trust friction):**
- `AGENTS.md` at repo root. This is the only artifact that works unconditionally, in every Codex
  surface, with no trust prompt. Keep it under 32 KiB combined with any nested files.
  All prose that currently lives in Claude-style `.claude/rules/*.md` must be folded into here
  for the Codex side, since Codex has no prose-rules concept.

**Tier 2, ship if the project wants agent behavior beyond prose:**
- `.agents/skills/<name>/SKILL.md` for reusable procedures. Same authoring format as Claude Code
  skills, so this is the one place a genuine shared asset is possible between the two harnesses.
  This is where an `agent-team` style capability actually belongs, not in `.codex/`.

**Tier 3, opt-in only, and only with a documented trust step:**
- `.codex/config.toml` for MCP servers and permission profiles.
- `.codex/hooks.json` (correct name) for enforcement gates.
- `.codex/rules/default.rules` for command execution policy.
- `.codex/agents/*.toml` for named subagents.

Every tier-3 item requires the user to mark the project trusted, and hooks additionally require
`/hooks` review. A template that ships tier 3 silently ships something that does nothing until a
human acts. If loam keeps tier 3, the bootstrap output must say so explicitly.

**Drop entirely:** any `~/.codex/prompts` slash-command scheme (deprecated), and any expectation
that Codex reads markdown rules files.

## 5. Open items I could not settle from docs alone

- Which filenames under `.codex/rules/` auto-load. Docs show `default.rules` by example and give
  a manual `--rules` flag for checking, but state no discovery rule for the directory.
  Resolve with: `codex execpolicy check --pretty --rules <repo>/.codex/rules/<file>.rules`
  and a live `/status` inspection in a trusted repo.
- Whether `[features] multi_agent` is still required given it is documented as "on by default";
  the loam config sets it explicitly, which is harmless but possibly redundant.

## 6. Source URLs

- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/agent-configuration/rules
- https://learn.chatgpt.com/docs/hooks
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/extend/mcp
- https://learn.chatgpt.com/docs/config-file/config-basic
- https://learn.chatgpt.com/docs/config-file/config-reference
- https://learn.chatgpt.com/docs/cli/reference
- https://learn.chatgpt.com/docs/custom-prompts
- https://agents.md/
