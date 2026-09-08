# Harness primitives for long-running agent loops

What Claude Code and Codex CLI already provide for an agentic software factory, so a designer does not rebuild it.

## Verified against

Claude Code 2.1.258, local `claude --version` and `claude --help`.
Codex CLI 0.153.4, local `codex --version` and each subcommand's `--help`.
Research date 2026-09-07.

Claude Code docs, all under https://code.claude.com/docs/en/ : `headless`, `cli-reference`, `hooks`, `hooks-guide`, `goal`, `scheduled-tasks`, `routines`, `channels`, `sub-agents`, `agent-teams`, `workflows`, `skills`, `memory`, `worktrees`, `checkpointing`, `context-window`, `sessions`, `model-config`, `plugins-reference`, `agent-sdk/overview`.
Managed Agents, https://platform.claude.com/docs/en/managed-agents/overview .
Codex docs moved from developers.openai.com/codex to https://learn.chatgpt.com/docs/ ; the openai/codex repo docs are now stubs pointing there.

## Claude Code headless

| Flag | Semantics | Verified how |
|---|---|---|
| `-p, --print` | Non-interactive, print result and exit, reads stdin capped at 10MB. | local help, headless |
| `--output-format text\|json\|stream-json` | One result object, or NDJSON events. | local help, headless |
| `--input-format text\|stream-json` | Realtime streaming input, `-p` only. | local help |
| `--json-schema <schema>` | Schema for the final answer, result in `structured_output`. | local help, headless |
| `--max-turns <n>` | Cap agentic turns, errors at the cap. | cli-reference, flag probe |
| `--max-budget-usd <amount>` | Hard dollar ceiling for the run. | local help |
| `-c, --continue` | Continue the most recent conversation in this directory. | local help |
| `-r, --resume [id\|name]` | Resume a specific session, found in any project since 2.1.223. | local help, headless |
| `--fork-session` | On resume, branch to a new session id. | local help |
| `--session-id <uuid>` | Pin the session id yourself. | local help |
| `--allowedTools` / `--disallowedTools` | Permission rule syntax, for example `Bash(git diff *)`. | local help, headless |
| `--permission-mode` | acceptEdits, auto, bypassPermissions, manual, dontAsk, plan. | local help |
| `--permission-prompts none` | Deny anything that would prompt. Needs 2.1.259+, REJECTED on 2.1.258. | flag probe |
| `--append-system-prompt`, `--system-prompt` | Add to or replace the system prompt. | local help |
| `--bare` | Skip hooks, skills, plugins, MCP, auto-memory, CLAUDE.md. Auth narrows to ANTHROPIC_API_KEY. | local help, headless |
| `--agents <json>` | Define subagents inline for the run. | local help |
| `--effort low\|medium\|high\|xhigh\|max` | Reasoning effort, plus `ultracode`. | local help, model-config |
| `--fallback-model <list>` | Comma-separated fallbacks on overload, `-p` only. | local help |
| `--forward-subagent-text` | Emit subagent text into stream-json at every nesting depth. | local help, headless |
| `--include-hook-events` | Put hook lifecycle events in the stream. | local help |
| `--no-session-persistence` | Do not write the transcript. | local help |
| `-w, --worktree [name]` | Run the session in a fresh git worktree. Absent from cli-reference. | local help, worktrees |
| `--bg, --background` | Detach and print an id. Cannot combine with `-p`. | local help |
| `--add-dir`, `--settings`, `--mcp-config`, `--plugin-dir` | Context loading for a bare or locked-down run. | local help |

The `json` result carries `session_id`, `result`, `structured_output`, `total_cost_usd`, `num_turns`, `is_error`, `permission_denials`.
The `stream-json` stream opens with `system/init` carrying `plugins`, `plugin_errors`, `mcp_servers`, `mcp_server_errors`, `capabilities`, and closes with a `result` message.
A CI gate can fail on a non-empty `plugin_errors` or `mcp_server_errors`.
`system/api_retry` events report retryable failures with `attempt`, `retry_delay_ms`, and an `error` category.

A background Bash task is killed about five seconds after the result.
A background subagent or workflow instead holds the process open until it finishes, bounded by `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, ten minutes by default.
SIGTERM exits 143 and leaves the in-flight turn unfinished with no result recorded.

## In-session loop mechanisms

### Stop hook

Exit code 2 on a `Stop` hook prevents the stop and forces another turn.
The `reason` from JSON, or stderr when there is none, becomes Claude's next instruction.
The same holds for `SubagentStop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `PostToolBatch`.
The stdin envelope adds `last_assistant_message`, `last_tool_use_id`, `stop_reason`, `stop_hook_active`.
Read `last_assistant_message` rather than `transcript_path`, which can lag the current turn.

The limit that matters: Claude Code overrides a Stop hook after eight consecutive blocks without progress, ends the turn, and warns.
Parse `stop_hook_active` and exit 0 when it is true.
Raise the cap with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.

JSON form is `{"hookSpecificOutput":{"hookEventName":"Stop","decision":"block","reason":"..."}}`.
Hook types are `command`, `prompt` (a model call returning `ok`, `reason`, `impossible`), `agent` (experimental, spawns a tool-using subagent), and HTTP.
`continueOnBlock: true` makes a PreToolUse or PostToolUse denial return as a tool error instead of ending the turn.

There are 32 hook events.
SessionStart, Setup, UserPromptSubmit, UserPromptExpansion, PreToolUse, PermissionRequest, PermissionDenied, PostToolUse, PostToolUseFailure, PostToolBatch, Notification, MessageDisplay, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, Stop, StopFailure, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, FileChanged, WorktreeCreate, WorktreeRemove, PreCompact, PostCompact, PreModelSwitch, PostModelSwitch, Elicitation, ElicitationResult.
SessionEnd also exists with exit-reason matchers.

### /goal

`/goal <condition>` is a session-scoped wrapper around a prompt-based Stop hook, so the loop most people hand-build already ships.
The condition is capped at 4000 characters and setting it starts a turn immediately.
After every turn the small fast model returns met, not yet met, or impossible, each with a reason.
The evaluator calls no tools, so the condition must be provable from Claude's own transcript output.
`/goal clear` removes it; `stop`, `off`, `reset`, `none`, `cancel` are aliases.

It works under `-p`, running the loop to completion in one invocation, and is restored across `--continue` and `--resume`.
Background work defers evaluation, with check-ins starting at 30 minutes and doubling, tunable by `CLAUDE_CODE_GOAL_CHECKIN_MINUTES`.
Four failures clear the goal: authentication failure, exhausted credits, an unrecoverable context overflow, and an unavailable model.
Rate limits and overload do not clear it.
Unavailable when `disableAllHooks` or `allowManagedHooksOnly` is set.

### /loop and cron

`/loop 5m <prompt>` schedules a cron job; `/loop <prompt>` lets Claude self-pace between one minute and one hour; bare `/loop` runs a maintenance prompt or `.claude/loop.md`.
Self-paced mode uses the `ScheduleWakeup` tool, and Claude ends the loop by calling it with `stop: true`.
The tools are `CronCreate`, `CronList`, `CronDelete`, with 5-field cron expressions and 8-character ids.

The limits that matter for an unattended factory are severe.
Tasks fire only between turns while the session is open and idle, with no catch-up for missed fires.
Recurring tasks expire seven days after creation and deterministic jitter shifts fire times up to 30 minutes.
A session holds at most 50 tasks, and a fresh conversation clears them all.
A scheduled fire will not execute a skill marked `disable-model-invocation: true`, nor built-in commands, nor MCP prompts; those arrive as plain text.
`CLAUDE_CODE_DISABLE_CRON=1` disables the scheduler and `/loop` together.

### Routines and channels

Routines run in the cloud with a one-hour minimum, on a fresh clone with no local file access and no permission prompts.
Desktop scheduled tasks run locally with a one-minute minimum.
Channels push an external event into a running session, installed as plugins and opted into with `claude --channels plugin:<name>@<marketplace>`.
The flag exists locally but is absent from `--help` and from cli-reference.
Channels cannot wake an idle or closed session, so an always-on setup still needs a background process.

## Subagents, teams, workflows

### Subagent frontmatter

Fields in `.claude/agents/*.md` are `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`, `experimental.cacheTtl`.
`name` and `description` are required.
`disable-model-invocation` is a skill field, not a subagent field.

A non-fork subagent starts with its own prompt, the delegation message, the CLAUDE.md hierarchy, a git-status snapshot, preloaded `skills`, and a sibling roster.
It inherits no conversation history, no output style, and no auto-memory.
Forks inherit everything and return only a result.
Caps are 20 concurrent (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) and depth 3 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
`isolation: worktree` branches from the default branch, not the parent's HEAD, and cleans up when nothing changed.

### Dynamic workflows

A workflow is plain JavaScript with top-level await, executed by a runtime isolated from the conversation.
The API is `agent(prompt, opts)`, `parallel(tasks)`, `pipeline(list, fn)`, `phase(title)`, `log(msg)`, and an `args` global.
The file must open with `export const meta = { name, description }` as a plain object literal.
`Date.now()`, `Math.random()`, and no-argument `new Date()` throw so a relaunch repeats the same calls.
`import()` is rejected before the run starts, and the script has no filesystem or shell of its own.

Limits are 16 concurrent agents, 4096 items per `parallel()` or `pipeline()` call, 1000 agents per run, and no mid-run user input.
An `agent()` call resolves to `null` when stopped or on an unrecoverable API error.
Scripts live in `.claude/workflows/`, `~/.claude/workflows/`, or a plugin's `workflows/` directory.

The fact that decides the factory design: the `ultracode` keyword is deliberately inert under `-p`, in SDK prompts not stamped as human input, in scheduled task prompts, and in webhook or PR-comment text.
A factory must save the workflow and invoke it by name, with a `Workflow` or `Workflow(<name>)` allow rule, since `-p` never shows the approval prompt but does run the call through permission evaluation.
Resume works only inside the same session, and a mid-fan-out failure reruns every agent that started after it.
Other knobs are `workflowSizeGuideline`, `disableWorkflows`, `CLAUDE_CODE_DISABLE_WORKFLOWS=1`, and `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`.

### Why teams are skipped

Agent teams are experimental and gated behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
Teammates are full sessions with mailboxes at `~/.claude/teams/{team}/inboxes/`, tasks at `~/.claude/tasks/{team}/`, and the tools `SendMessage`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`.
Four limits rule them out for unattended work.
Teammates never spawn under `-p` or the Agent SDK, where a named subagent runs as an ordinary subagent.
Teams do not survive `/resume` or `/rewind`.
The roster is flat, so teammates cannot spawn teammates; this research run hit that rule directly.
The lead is fixed for its lifetime and permission modes are set at spawn.

## Skills, rules, memory, worktrees, checkpoints, context, models

SKILL.md fields are `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`.
Precedence left over right is enterprise, personal, project, plugin, added directories, nested.
`skillOverrides` toggles visibility with `on`, `name-only`, `user-invocable-only`, `off`.

`.claude/rules/` is real and discovered recursively.
A rule without `paths:` loads at launch; a rule with `paths:` loads when Claude reads a matching file, not when it writes one.

Memory loads managed policy, then `~/.claude/CLAUDE.md`, then project CLAUDE.md, then `CLAUDE.local.md`.
Imports use `@path`, resolved against the containing file, maximum four hops, and load at launch so they save no context.
Auto-memory writes to `~/.claude/projects/<project>/memory/` with a `MEMORY.md` index whose first 200 lines or 25KB load each session.
Keys are `autoMemoryEnabled`, `autoMemoryDirectory`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

`claude -w [name]` creates `.claude/worktrees/<name>/` on branch `worktree-<name>`, with tools `EnterWorktree` and `ExitWorktree`.
Four tool-level checks block edits into the main checkout, commands whose cwd resolves there, git redirects, and unparseable command shapes.
`worktree.baseRef` is `fresh` or `head`, and `.worktreeinclude` copies gitignored files in.
Runs started with `-p` never clean up their worktrees, so a factory must sweep them.

`/rewind` restores from checkpoints captured only from Claude's file-editing tools.
Bash-driven changes, most subagent edits, and external edits are not tracked.
Retention is the 100 most recent checkpoints, swept about 30 days after last save per `cleanupPeriodDays`.

Context is managed with `/compact`, `/autocompact <auto|tokens>`, the `--autocompact` flag, `autoCompactWindow`, and `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, over a 100K to 1M range.
After compaction the five most recently modified files are re-read and invoked skill bodies survive capped at 5000 tokens each, but the skill listing does not reload.
Microcompact is not a documented feature: UNVERIFIED.

Effort levels are low, medium, high, xhigh, max, with `ultracode` as a separate setting combining xhigh with automatic workflow orchestration.
Settings keys are `effortLevel`, `modelSettings.<id>.effort`, and `ultracode`.
Model ids on the model-config page include `claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`.
`CLAUDE_CODE_SUBAGENT_MODEL` sets the default for subagents, teammates, and workflow agents.

## Plugin tooling

`claude plugin validate <path> [--strict]` validates a manifest, or the skills, agents, and commands in a bare directory, exiting 1 on warnings under `--strict`.
`claude plugin eval` runs cases at `<eval dir>/**/case.yaml`, or `prompt.md` plus `graders/*.md`, with the eval dir defaulting to `evals/`.
The CI gate is `--threshold <0..1>`, which exits 1 below the threshold and defaults to 1.0.
Other flags are `--json [path]`, `--runs <n>` defaulting to 3, `--ablation with-without` for a no-plugin baseline arm, `--judge-model` defaulting to haiku, `--max-cost-usd` exiting 2, `--report <path>`, `--mocks record|off`, `--allow-tools`, `--case <glob>`, `--eval-dir`, `--output-dir`.
`claude plugin eval init` scaffolds a suite.
This command is CLI-verified but has no page in the public docs index: doc-UNVERIFIED.
`/skill-doctor` reports per-skill token cost and invocation counts, requires 2.1.252+, and prints as text under `-p`.

## Codex CLI

`codex exec` takes `--json`, `-o, --output-last-message <FILE>`, `--output-schema <FILE>`, `-s, --sandbox read-only|workspace-write|danger-full-access`, `-c key=value`, `-p, --profile`, `-m, --model`, `--ephemeral`, `--skip-git-repo-check`, `--ignore-user-config`, `--ignore-rules`, `--add-dir`, `-C, --cd`, `--enable`, `--disable`, `--approve-for-me`, `--dangerously-bypass-approvals-and-sandbox`, `--dangerously-bypass-hook-trust`, `--thread-source`, `--strict-config`.
`--full-auto` is removed in 0.153.4; the binary rejects it while the learn.chatgpt.com page still describes it, so that page is stale.
Use `-s workspace-write` instead, optionally with `--approve-for-me`.
`-a, --ask-for-approval` exists at the top level and on `resume`, `fork`, `queue`, and `archive`, but not on `codex exec`.

`codex exec resume [<uuid|thread-name>|--last]` and `codex exec fork <SESSION_ID>` continue a session, and fork requires an explicit id.
Resume accepts the exec output flags but not `-s`, `-p`, `-C`, or `--add-dir`, which constrains a loop that varies the sandbox per iteration.
`codex queue --thread <id> --message <text>` steers a running session.
Session ids come from the first JSONL event or from `~/.codex/session_index.jsonl`, and `--ephemeral` suppresses both so an ephemeral run cannot be resumed.

The `--json` stream emits `thread.started`, `turn.started`, `turn.completed`, `turn.failed`, `item.started`, `item.completed`, `error`.
The final answer is the last `item.completed` whose `item.type` is `agent_message`, though the `-o` file is more robust.
The session id is `thread.started.thread_id`.

Config keys for loops are `model`, `model_reasoning_effort`, `approval_policy`, `sandbox_mode`, `[sandbox_workspace_write]` with `network_access` and `writable_roots`, `notify`, `[mcp_servers.<id>]`, `[features]`, and `project_doc_max_bytes` at 32 KiB.
AGENTS.md discovery reads `AGENTS.override.md`, then `AGENTS.md`, then fallbacks, at most one per directory, global first then root to cwd so nearer files win, stopping at the size cap.

Codex hooks have twelve events: SessionStart, SessionEnd, SubagentStart, SubagentStop, PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, UserPromptSubmit, Stop, Interrupt.
Trust is per-hook SHA-256 in `[hooks.state."<path>:<event>:<i>:<j>"].trusted_hash`.
`codex features list` shows `hooks stable false` on this machine, so hooks are off by default and need `--enable hooks`.

`codex exec review [--uncommitted|--base <branch>|--commit <sha>]` is the loop-friendly review form because it takes `--json`, `-o`, and `--output-schema`.
Plain `codex review` takes none of those.

Codex subagents are TOML files in `~/.codex/agents/` or `<repo>/.codex/agents/`, requiring `name`, `description`, `developer_instructions`, gated by `features.multi_agent`.
Delegation is prompt-driven with no flag.
Whether subagents spawn under non-interactive `codex exec` is UNVERIFIED.

`codex mcp-server` prints a deprecation warning; the successor is `codex app-server`, JSON-RPC 2.0 over stdio, unix socket, or websocket.
It covers thread create, resume, fork, archive, turn start, steer, interrupt, and per-request model, sandbox, and approval policy.
`generate-ts` and `generate-json-schema` emit the authoritative wire format.
`codex agents` is a TUI viewer over that daemon, not a spawner.

`notify` is an argv prefix; Codex appends one JSON string with `type: "agent-turn-complete"`, `thread-id`, `turn-id`, `cwd`, `input-messages`, `last-assistant-message`.
Note the hyphenated keys.
This is the cheapest turn-completion signal for an outer loop, needing no JSONL parsing.

## Ten loop-building primitives

1. Stop hook, exit code 2, is the only in-session forced-continuation mechanism; budget for the eight-block cap and read `stop_hook_active`.
2. `/goal` is that Stop hook already built, with a model evaluator, three verdicts, resume support, and defined error handling.
3. `type: "prompt"` and `type: "agent"` hooks give model-judged and tool-using gates with no shell script.
4. `claude -p --output-format json` plus the returned `session_id` is the whole outer-loop contract.
5. `--bare` is the CI default, and `--max-turns` plus `--max-budget-usd` are the two hard stops that bound a runaway iteration.
6. Dynamic workflows are the fan-out engine, but must be saved and invoked by name because the `ultracode` keyword is inert under `-p`.
7. `isolation: worktree` or `claude -w` answers write conflicts in parallel implementation, with the caveat that `-p` never cleans up.
8. `/loop`, cron, routines, and channels are all session-scoped or cloud-only; the durable scheduler stays a shell, launchd, or CI driver.
9. Codex's outer-loop surface is `codex exec --json -o out.md` plus `codex exec resume --last`, with `notify` for completion and `codex exec review` as a structured critic.
10. Choose by who holds the plan: subagents for bounded delegation, workflows for fan-out, and skip teams.

## Three loop shapes and their tradeoffs

### Stop-hook-driven in-session loop

Minimal set is a `Stop` hook in settings, either a command hook reading `stop_hook_active` and exiting 2, or a prompt hook returning `ok: false`.
Using `/goal` instead means writing nothing at all.
It is the cheapest to build and the only shape where the model keeps full working context between iterations, so it converges fast on a task it already understands.
The costs are that context grows until auto-compaction silently drops detail, the eight-block cap ends the loop whether or not the work is done, and there is no per-iteration boundary to inspect or replay.
Use it for convergence inside one coherent task, not for a queue of unrelated work.

### Shell-driven outer loop with fresh context per iteration

Minimal set is a shell script, `claude -p --bare --output-format json --max-turns N --max-budget-usd M` with a permission mode and allow rules, `jq` to pull `session_id` and `result`, and a state file or git branch carrying work forward.
For Codex it is `codex exec --json -o out.md` with `notify` for completion signalling.
This is the only shape that survives a crash, gives per-iteration cost and turn accounting, and lets you swap model or effort between iterations.
The cost is that each iteration re-pays the discovery tax, re-reading the repository and re-deriving what the last iteration learned, and it can undo work it does not know about.
That forces state out into files, a task queue, or commits.
It is also the only shape that runs with no session open, so it is what a real factory schedules.

### In-session Workflow fan-out

Minimal set is a saved script in `.claude/workflows/` using `agent()` with a JSON schema, `pipeline()` or `parallel()`, and `phase()`, plus a `Workflow` allow rule for unattended runs.
It gives the best parallelism per unit of context: 16 agents at once, results in script variables, deterministic replay, and an adversarial verification pattern codified once.
The costs are that the script cannot touch the filesystem or shell, cannot load modules, cannot take mid-run input, and a mid-fan-out failure reruns every agent that started after it.
Resume works only inside the same session and cost per run is high and largely invisible until you open `/workflows`.

The honest combination is the shell loop driving the workflow, one iteration per unit of work, with git as the state carrier, and the Stop hook reserved for tightening a single iteration toward a verifiable condition.

## Risks

`claude plugin eval` is verified from the local CLI only and has no public doc page, so its flags can change without a doc trail.
`--channels`, `-w`, `--teammate-mode`, `--max-turns`, and `--permission-prompt-tool` are present in the 2.1.258 binary but missing from `claude --help`; `--channels` and `-w` are also absent from cli-reference.
Codex subagent behavior under non-interactive `codex exec` is undocumented, and no live `codex exec` was run, so the JSONL event shapes are doc-sourced rather than observed.
Codex hooks are disabled by default on this machine, so any design depending on them needs an explicit enable.
The `haiku` alias resolution is self-contradictory on the model-config page, which lists both Haiku 3.5 in the alias table and `claude-haiku-4-5` in the id list: UNVERIFIED.
Most Claude doc pages were read through WebFetch summarization, so a qualifier could have been dropped; the flag-presence probes and all local help output are direct observations.
