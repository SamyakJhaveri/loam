# Claude Code setup audit - always-on context cost, use, and on-demand options

Date: 2026-09-25. Claude Code 2.1.282. Read-only audit; nothing was changed.
Tokens = characters / 4.
"Always-on" means text that sits in context for the whole session (or is re-injected every turn), whether or not it gets used.
Built-in system prompt and built-in tools are excluded because they cannot be configured.

## How the numbers were measured

- Measured baseline: the current Loam lead session transcript (`~/.claude/projects/-Users-samyakjhaveri-Desktop-loam/b56e5520-...jsonl`), which records the exact injected blocks: `skill_listing` (18,068 chars, 53 skills), `agent_listing_delta` (7,016 chars, 21 agents), `deferred_tools_delta` (78 names), `mcp_instructions_delta` (4 blocks, 6,469 chars), `instructions` (CLAUDE.md files + MEMORY.md), SessionStart and UserPromptSubmit hook output.
- Usage: every `*.jsonl` under `~/.claude/projects/` (including subagent transcripts) modified in the last 30 days, records filtered to timestamp >= 2026-08-26. Counted `tool_use` names `mcp__<server>__*`, `Skill` inputs, `Agent` `subagent_type`, `<command-name>` slash commands, and hook attachments. Script: `scratchpad/usage.py`, output `scratchpad/usage.txt`.
- Sessions in window: loam 147, /private/tmp worktrees 71, distbench (+ E0x clones) ~31, parbench_ipdps 1 (today, no tool calls yet), other ~20.
- Caveat: `~/.claude/settings.json` was edited today at 13:19, after the lead session started. That edit enabled context7, playwright, github, playground, and code-review plugins and disabled `cowork-plugin-management@synced` (diff vs `settings.json.bak-2026-09-25`). No session has loaded that config yet, so those rows are estimates.

## Per-item table

Usage columns: L = loam, P = parbench_ipdps, O = other projects. Numbers are 30-day counts.

| Name | Type | Scope | Always-on tokens | Uses (30 d) | Verdict | Exact change | Invoke on demand |
|---|---|---|---|---|---|---|---|
| ste-reminder.sh | UserPromptSubmit hook | user | 70 per turn, stays in history (lead session: 44 turns = ~3,100) | fired ~2,420 times (all projects); duplicates `~/.claude/CLAUDE.md` Communication style + em-dash rule | remove (or keep if the owner wants the per-turn mechanism) | `~/.claude/settings.json` `hooks.UserPromptSubmit[0].hooks`: delete the `ste-reminder.sh` entry | n/a - the rule already lives in `~/.claude/CLAUDE.md` |
| context-handoff.sh | UserPromptSubmit + Stop hook | user | 0 below 450K; one line above | 23 reminders last week (L) | keep always-on | none | n/a |
| write-rewrite-guard.sh | PreToolUse(Write) hook | user | 0 (output only when it blocks) | fires on each Write | keep | none | n/a |
| basic-memory session-start | SessionStart hook | user | 189 per session | 22 firings last week (L); 0 Basic Memory tool calls; output says "Basic Memory isn't set up" and tells Claude to search a graph that has no MCP server configured | remove (pure waste, misleading) | `~/.claude/settings.json` delete `hooks.SessionStart` block `basic-memory hook session-start --harness claude` | `basic-memory` CLI by hand |
| basic-memory pre-compact | PreCompact hook | user | 0 (auto-compaction is off) | ~0 | remove | delete `hooks.PreCompact` block (120 s timeout) | n/a |
| mem-recall.sh | SessionStart hook | project (loam, parbench_ipdps) | ~300 (774-2,570 chars, avg 1,200) | 22 firings last week (L) | keep (Loam memory v2 product) | none | n/a |
| fable-session-brief.sh | SessionStart + PostModelSwitch hook | project | 213 only when model is Fable; 0 on Opus | 11 firings last week (L) | keep | none | n/a |
| post-compact-reinject.sh, mem-capture.sh | SessionStart(compact), Stop, SessionEnd, PreCompact | project | 0 | background | keep | none | n/a |
| codex plugin hooks | SessionStart/SessionEnd/Stop | plugin | 0 observed | stop-review-gate 2 firings last week | keep | none | n/a |
| ~/.claude/CLAUDE.md | instructions | user | 1,262 | every session | keep | none | n/a |
| loam CLAUDE.md + AGENTS.md | instructions | project | 1,180 | every loam session | keep | none | n/a |
| parbench_ipdps CLAUDE.md + AGENTS.md | instructions | project | 679 | - | keep | none | n/a |
| loam MEMORY.md (auto memory) | instructions | user/project | 3,170 (12,678 chars, 76 lines) - largest single item | every loam session | trim | move DONE/CLOSED "Active Initiatives" entries to `memory/ARCHIVE.md`; est. -1,200 | read ARCHIVE.md on demand |
| claude-in-chrome | built-in MCP + skill | user (`claudeInChromeDefaultEnabled: true` in ~/.claude.json) | ~600 (22 names 206 + instructions 256 + skill 137) | L 103, O 18 | keep always-on (heavily used) | optional: `/chrome` -> turn off "Enabled by default" | `claude --chrome` |
| claude.ai Exa | connector | claude.ai account | 24 (3 names, no instructions) | L 54, O 4 | keep | none | n/a |
| claude.ai Consensus | connector | claude.ai account | 373 (1 name + 1,458-char instructions) | L 9, O 4 | keep (research use) | none | n/a |
| claude.ai Claude Docs | connector | claude.ai account | 541 (8 names + 1,893-char instructions) + 251 for its `anthropic-skills:docs` skill | L 1, O 1 | disable per project | in each repo run `/mcp`, toggle "claude.ai Claude Docs" off (writes `disabledMcpServers` in `~/.claude.json` under the project path) | `/mcp` toggle back on |
| claude.ai HyperFrames by HeyGen | connector | claude.ai account | 654 (10 names + 2,096-char instructions, cut at 2,048) | 0 everywhere; its own instructions say compose/render are disabled in CLI clients | remove (pure waste) | disconnect on claude.ai (Settings > Connectors), or `/mcp` toggle off per project | claude.ai web |
| claude.ai Mobbin | connector | claude.ai account | 28 | L 0, O 1 | disable per project | `/mcp` toggle off | `/mcp` toggle on |
| claude.ai Whimsical | connector | claude.ai account | 22 | 0; status "Needs authentication" | remove | disconnect on claude.ai or `/mcp` toggle off | - |
| shadcn | MCP (stdio, npx) | user (`~/.claude.json` mcpServers) | 67 + an npx process each session | 0 (already disabled in parbench_sam) | make project-scoped | `claude mcp remove shadcn -s user`; in a frontend repo `claude mcp add shadcn -s project -- npx shadcn@latest mcp` | per-project `.mcp.json` |
| github@claude-plugins-official | plugin (HTTP MCP) | user | est. ~450 (tool names; count NOT VERIFIED) | 0 (owner uses `gh`) | remove | `claude plugin disable github@claude-plugins-official --scope user` | `gh` CLI |
| playwright@claude-plugins-official | plugin (npx MCP) | user | est. ~250 (~22 names) | plugin server 0; older `playwright` server L 6, O 3 | make on-demand | `claude plugin disable playwright@claude-plugins-official --scope user`; enable in a repo via `"enabledPlugins": {"playwright@claude-plugins-official": true}` in its `.claude/settings.local.json` | claude-in-chrome covers most browser work |
| context7@claude-plugins-official | plugin (HTTP MCP) | user | est. 20-500 (2 names + unknown instructions) | 0 (lifetime 7, last 2026-07) | make on-demand | same pattern as playwright | enable per project |
| playground@claude-plugins-official | plugin skill | user | ~70 | 0 (never used) | remove | `claude plugin disable playground@claude-plugins-official --scope user` | - |
| code-review@claude-plugins-official | plugin command | user | ~12 | 0; duplicates bundled `/code-review` | remove | `claude plugin disable code-review@claude-plugins-official --scope user` | bundled `/code-review` |
| skill-creator@claude-plugins-official | plugin skill | user | 88 | 0 (lifetime 0); duplicates synced `anthropic-skills:skill-creator` | remove | `claude plugin disable skill-creator@claude-plugins-official --scope user` | synced copy remains |
| code-simplifier@claude-plugins-official | plugin agent | user | 57 | L 2 | keep (cheap) | none | - |
| codex@openai-codex | plugin (5 skills, 1 agent, hooks) | user | ~213 | codex-rescue agent 5, codex:rescue 1, codex-cli-runtime 2 | keep | none | - |
| mattpocock-skills@mattpocock | plugin (11 listed skills) | user | ~660 | grilling 5, domain-modeling 2, writing-for-agents 1, setup 2, grill-with-docs 1, wayfinder 1; 8 listed skills 0 uses | keep (cannot hide single plugin skills) | note: `skillOverrides` entries `mattpocock-skills:*` in user + loam settings are dead config (docs: plugin skills ignore skillOverrides) | - |
| sam-cc-setup@seed-skills | plugin (2 skills, 4 agents) | user + project | ~690 (skills 263 + agents 428) | lean-critic 38, plan-reviewer 34, reviewer 16, judge 5, codex-review 6, plan-review 3, surprise-me 4 | keep | none | - |
| web-frontend-anthropics + web-frontend-vercel | plugins (7 listed skills) | user; off in loam local | ~645 outside loam; 0 in loam | 0 everywhere | disable globally, enable per frontend repo | `~/.claude/settings.json` set both to `false`; enable in a repo's `.claude/settings.local.json` | per-project enable |
| cowork-plugin-management@synced | synced plugin (2 skills) | claude.ai account | 181 in lead session; set false today | 0 | already disabled (effect NOT VERIFIED; it loaded in the pre-edit session) | if it still loads: `"syncClaudeAiPlugins": false` in user settings | - |
| synced anthropic-skills (brainstorming, docs, import-memory, morning, skill-creator) | synced skills | claude.ai account | 534 in loam | 0 | turn off | user `skillOverrides`: `"anthropic-skills:<name>": "off"` for each (works: loam's local entries hide pdf/pptx/xlsx/docx) or `"syncClaudeAiSkills": false` | `/anthropic-skills:<name>` still runs only if not "off"; use `"user-invocable-only"` to keep `/name` |
| synced anthropic-skills pdf/pptx/xlsx/docx | synced skills | claude.ai account | 0 in loam (off locally); up to ~820 in parbench_ipdps | 0 | turn off at user level | add the 4 `anthropic-skills:*: "off"` entries to `~/.claude/settings.json` (today only in loam local) | - |
| User skills unused 30 d: fable-mode 705, rigor 430, experiment-loop 404, find-skills 319, humanizer 306, test-driven-development 220 (chars) | user skills | user | 566 | 0 each (rigor referenced as `/rigor` in CLAUDE.md) | make on-demand | `~/.claude/settings.json` `skillOverrides`: `"<name>": "user-invocable-only"` (hidden from Claude, still `/name`) or `"name-only"` | `/fable-mode`, `/rigor`, ... |
| new-model-workflow, claude-api (name-only) | user skills | user | 91 + 4 | 2 + 3 | keep | none | - |
| team-voice | user skill | user; off in loam local | 85 outside loam | O 1 (+ lifetime 9) | name-only | user `skillOverrides` `"team-voice": "name-only"` | `/team-voice` |
| catchup | project skill | project | 90 | L 21, O 5 | keep | none | - |
| hypothesis-tree, fable-prompting | project skills | project | 169 | 0 | name-only | `.claude/settings.local.json` `skillOverrides` `"name-only"` | `/hypothesis-tree` |
| seed:* duplicate listing | nested project skills | loam only | 352 when files under `seed/` are touched | - | tolerate (no documented switch found) | NOT FOUND | - |
| Bundled skills unused 30 d: dataviz 1,448, run 369, keybindings-help 249, fewer-permission-prompts 192, security-review 91, init 68 (chars) | bundled skills | built-in | 604 | 0 each | name-only | user `skillOverrides` `"<name>": "name-only"` (applies by skill name; bundled case inferred, NOT VERIFIED) | `/dataviz` etc. |
| Bundled skills used: workflow-authoring, artifact-design/-diagramming/-capabilities, update-config, schedule, loop, simplify, code-review, claude-in-chrome | bundled skills | built-in | ~1,240 | workflow-authoring 26, artifact-design 17, simplify 3, others 1-3 | keep | none | - |
| User agents used: worker 245, scout 299, pr-review 250, code-architect 220, verify-app 243, escalate 272, read-only 274 (chars) | agents | user | ~450 | worker 55, scout 42, pr-review 18, code-architect 13, escalate 5, verify-app 4, read-only 2 | keep | none | - |
| build-validator | agent | user | 69 | 0 | remove or park | move `~/.claude/agents/build-validator.md` out | - |
| scout-sonnet | agent | user | 57 | 0 | keep (named in CLAUDE.md routing) | none | - |
| Built-in agents (claude-code-guide 1,066 chars, Explore, Plan, general-purpose, claude, statusline-setup) | agents | built-in | 630 | general-purpose 307, Explore 38, claude-code-guide 23 | keep | `permissions.deny: ["Agent(<name>)"]` blocks use; whether it removes the listing line is NOT VERIFIED | - |

## Totals (configurable always-on tokens per session, ~10 user turns)

| | Loam now | Loam after | parbench_ipdps now (est.) | parbench_ipdps after (est.) |
|---|---|---|---|---|
| CLAUDE.md files | 2,442 | 2,442 | 1,941 | 1,941 |
| Auto memory MEMORY.md | 3,170 | ~1,970 | 0 (none yet) | 0 |
| Skill listing | ~4,420 | ~2,700 | ~7,000 (at the 1%-of-context budget cap; distbench measured 29,867 chars) | ~4,000 |
| Agent listing (non-built-in) | 1,124 | 1,055 | 1,124 | 1,055 |
| MCP names + server instructions | ~2,890 | ~1,000 | ~2,890 | ~1,000 |
| SessionStart hooks | 489 | 300 | 489 | 300 |
| UserPromptSubmit (10 turns) | 700 | 0 | 700 | 0 |
| **Total** | **~15,200** | **~9,500** | **~14,100** | **~8,300** |

Built-in agents (~630) and the built-in system prompt are excluded from all columns.

## Mechanisms and sources

- `disable-model-invocation: true` removes the description from context; `user-invocable: false` keeps it: https://code.claude.com/docs/en/skills (invocation table).
- `skillOverrides` values `on` / `name-only` / `user-invocable-only` / `off`; "Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin` instead."; `/skill-doctor` reports per-skill cost and use: https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings and #find-unused-skills.
- Skill listing budget = 1% of the context window; least-invoked skills lose descriptions first; each entry capped at 1,536 chars: https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short.
- Synced skills and plugins: `syncClaudeAiSkills`, `syncClaudeAiPlugins`, `"<name>@synced": false`: https://code.claude.com/docs/en/settings-reference and https://code.claude.com/docs/en/plugins/loading#synced-plugins.
- Per-project plugin enable/disable: `enabledPlugins` merges key by key, highest-precedence source wins; `.claude/settings.local.json` beats `.claude/settings.json` beats user: https://code.claude.com/docs/en/plugins/loading. `claude plugin enable|disable --scope`: https://code.claude.com/docs/en/plugins/install.
- MCP tool search is on by default; "Only tool names and server instructions load at session start"; instructions and tool descriptions cut at 2,048 chars (`CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH`); `alwaysLoad` forces upfront load: https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search. The user env sets `ENABLE_TOOL_SEARCH=true`, the same as the default.
- MCP scopes local/project/user (`claude mcp add --scope`); `/mcp` toggle writes `disabledMcpServers` per project in `~/.claude.json`; `enabledMcpjsonServers`/`disabledMcpjsonServers` only cover `.mcp.json` approval (neither repo has a `.mcp.json`): https://code.claude.com/docs/en/mcp.
- claude.ai connectors come from the claude.ai account (`claude mcp list` shows them as "claude.ai <Name>"). Turn all off with `"disableClaudeAiConnectors": true` (any settings file, including a checked-in project `.claude/settings.json`) or `ENABLE_CLAUDEAI_MCP_SERVERS=false claude`; one connector per project via the `/mcp` toggle; `deniedMcpServers` by name is documented under managed settings: https://code.claude.com/docs/en/mcp#disable-claude-ai-connectors.
- Claude in Chrome: "Enabling Chrome by default in the CLI increases context usage"; turn it off with `/chrome` and start with `--chrome` when needed: https://code.claude.com/docs/en/chrome#enable-chrome-by-default.
- Hooks: stdout from UserPromptSubmit, SessionStart, and PostModelSwitch is added as context; UserPromptSubmit has no matcher support and fires on every prompt: https://code.claude.com/docs/en/hooks.
- Blocking a subagent: `permissions.deny: ["Agent(name)"]`: https://code.claude.com/docs/en/sub-agents#disable-specific-subagents.

## Other findings

- Dead config in `~/.claude/settings.json` `skillOverrides`: `mattpocock-skills:domain-modeling`, `mattpocock-skills:improve-codebase-architecture` (plugin skills ignore overrides; domain-modeling is still listed in loam), and `theme-factory`, `web-artifacts-builder`, `webapp-testing` (no user skill has these names; they are plugin skills).
- In non-loam projects the skill listing reached its budget cap (distbench 2026-09-24: 29,867 chars, 77 skills, with pdf/pptx/xlsx/ml-paper-writing descriptions dropped to about 24 chars each). Cutting unused entries also restores full descriptions for the skills that are used.
- Loam transcripts from before 2026-09-18 hold ~900 hook errors from missing relative `.claude/hooks/*.sh` files (pre-commit-gate, mutation-gate, and others). None occurred after 2026-09-18, so this is history, not current cost.
- Connector sets differ by account: sessions earlier today also carried Gmail (30 names), Google Drive, Calendar, Gamma, Clay, Excalidraw, tldraw, and design/engineering synced plugins (up to 144 deferred names). The current account carries 63-66.
