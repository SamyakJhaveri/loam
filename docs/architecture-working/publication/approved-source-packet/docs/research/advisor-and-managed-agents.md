# Advisor tool, Managed Agents cookbooks, and the two tool-use betas

Read live on 2026-09-09 and 2026-09-10 from the Claude Code advisor page, the raw cookbook notebooks, and one local probe.
Samyak gave the cookbook URLs on 2026-09-09 with one condition: include them "only if they are relevant and if we can directly get help from them to build better software in a more structured way while being token efficient".
The one-line answer: the advisor is a Claude Code feature the factory can switch on with one flag; the two Managed Agents cookbooks supply prompts and a decomposition shape but run only on Anthropic's cloud runtime; the two tool-use betas are Messages API features the CLI already has equivalents for.
Quotes are verbatim from the pages named; everything else is this note's reading.

## The Claude Code advisor tool

Source: <https://code.claude.com/docs/en/advisor> (fetched as `advisor.md`, 2026-09-10).

What it is: "The advisor tool lets Claude consult a second, typically stronger model at key moments during a task, such as before committing to an approach, when stuck on a recurring error, or before declaring a task complete. The advisor receives the full conversation, including every tool call and result, and returns guidance that Claude applies before continuing."
The main model decides when to call it: "The advisor always receives the full conversation, and Claude controls the timing."

Configuration, three ways. The settings block, verbatim:

```json
{
  "advisorModel": "opus"
}
```

The flag: `claude --advisor opus`. "Claude Code uses the flag instead of the `advisorModel` setting for that session. It doesn't list `--advisor` in `claude --help`."
The command: `/advisor opus`, `/advisor off`, `/advisor` with no argument prints the current advisor.

Headless support, verbatim: "The command also works where there is no terminal picker: in non-interactive mode with `-p`, in the Agent SDK, in the desktop app, and over Remote Control. This requires Claude Code v2.1.260 or later."
The Mac and the runner run 2.1.266.

The pairing the factory uses, one row of the page's table:

| Main model | Accepted advisors | Note |
|---|---|---|
| Opus 4.7 or later | Fable, and Opus 4.7 or later | "Opus 4.7 and later Opus models are ranked as equally capable, so any of them accepts another as an advisor. An Opus 4.7 main with an Opus 4.6 or Sonnet 5 advisor is rejected" |

Cost, verbatim: "When Claude calls the advisor, the advisor model reads the conversation, so each call consumes tokens at the advisor model's rates in addition to your main model's usage."
And on caching: "The advisor model's own read of the conversation is not cached. Each advisor call processes the full transcript anew, with no reuse between calls."
The main model's cache survives: "Enabling or disabling the advisor mid-session does not invalidate your main model's prompt cache."

The consent gate, verbatim: "On some plans, Fable usage bills to usage credits, and Fable as the advisor bills the same way. If your account requires the one-time consent to bill Fable usage to usage credits, Claude Code asks for it when you select a Fable model with `/model` and doesn't apply Fable as the advisor until you have accepted that consent."
What the flag does before consent: "With `claude --advisor fable`, Claude Code exits at launch with a message that points to `/model fable`. In a background session, it starts the session without the advisor instead of exiting."
So under `-p` a missing consent is a launch error, not a silent no-advisor run; the silent case is a saved `advisorModel` or a background session.

Launch errors, the full list: the main model does not support the advisor; the requested model cannot act as one; the organization's `availableModels` allowlist excludes it; Fable was requested and consent is missing.

Requirements that matter to the runner: Anthropic API only, no Bedrock or Vertex; and "Claude Code turns the advisor on through a feature flag it fetches from Anthropic. In a session where a variable that turns flag fetching off is set, such as `DISABLE_TELEMETRY`, the advisor stays off."
Kill switch: `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`; then "The `--advisor` flag is accepted but has no effect."

### Local probe, 2026-09-10

One call on the Mac, Claude Code 2.1.266, Max account, no prior consent step:

```
claude -p --model 'claude-opus-4-8[1m]' --advisor fable --max-turns 3 --output-format json \
  --strict-mcp-config --no-session-persistence \
  'Consult the advisor tool once about whether to reply in lowercase, then reply with the single word ok'
```

It exited 0 with the advisor attached. What the JSON shows, and what the factory reads from it:

| Fact | Where it sits in the output |
|---|---|
| the call happened | an assistant event with a content block `{"type":"server_tool_use","name":"advisor","input":{}}` |
| the guidance | the next assistant event carries `advisor_tool_result` whose content is `advisor_redacted_result` with `encrypted_content`; a Fable advisor's text is withheld from the transcript |
| the cost | the result event's `modelUsage` has one key per model; `modelUsage["claude-fable-5-1"].costUSD` is the advisor's spend, `modelUsage["claude-opus-4-8[1m]"].costUSD` the worker's |
| the tool roster | the system init event lists `Workflow` and `ListAgents` among the tools of a `-p` session, and `advisor` among the slash commands |

Numbers from that one probe: one advisor call read 26,046 uncached input tokens and wrote 417, costing 0.28 usd; the Opus turn cost 0.26 usd; total 0.54 usd.
A worker round that runs 100 turns and consults three times would pay three full-transcript reads at Fable rates.
The F11 ledger line exists to measure that.

## Consult-an-advisor cookbook

Source: <https://platform.claude.com/cookbook/managed-agents-cma-consult-an-advisor>, notebook `managed_agents/CMA_consult_an_advisor.ipynb`.

The idea, verbatim: "An advisor does that inside the session. You name a second, more capable model in the agent's `multiagent` roster as an `{"type": "advisor", "model": ...}` entry. The primary thread then has an `advisor` tool it can call mid-turn: the platform puts the conversation so far in front of the advisor model, returns its guidance to the working model, and sampling continues."
Why the system prompt matters: "The tool takes no input, because the advisor reads the whole conversation up to the call rather than a query the working model writes. So the system prompt is where you set the consultation policy: what it controls is when the model reaches for the tool."

The worker system prompt, verbatim:

```
You are a backend engineer designing HTTP APIs.
You have an advisor: a more capable model that can review your conversation so far and
send back guidance. Consult it with the advisor tool before you commit to any decision
that would be expensive to reverse once clients depend on it: identifier and idempotency
schemes, pagination contracts, error semantics, versioning. Do routine drafting yourself.
When you consult, act on the guidance you get back and say what you changed.
Write your final design to /mnt/session/outputs/design.md.
```

The roster shape: `multiagent={"type": "coordinator", "agents": [{"type": "advisor", "model": ADVISOR_MODEL}]}` on `client.beta.agents.create`, under the beta header `managed-agents-2026-04-01`, `anthropic>=0.121.0`.
Server rules: at most one advisor per roster; the pairing is validated at create time as a 400; the entry takes the name `anthropic.advisor`.
Only the primary thread consults; spawned specialists have no advisor.

Cloud-only pieces: the Agents, Environments, and Sessions APIs, the managed sandbox at `/mnt/session/`, the event stream, and the auto-surfaced tool.
Anthropic's own note on redaction: "For a model whose output the policy withholds, the delivery event carries `[{"type": "redacted"}]` placeholder blocks instead of text", which is what the local probe saw as `advisor_redacted_result`.
Cost in the notebook's run: one consultation, 603 in and 2,468 out, 0.07 usd on an Opus 5 advisor; session total 0.21 usd.

What copies: the consultation policy sentence, adapted, into the worker prompt; the "say what you changed" rule into `decisions.md`.
What does not: none of the plumbing, because `claude --advisor` already is the plumbing.

## Coordinate-specialist-team cookbook

Source: <https://platform.claude.com/cookbook/managed-agents-cma-coordinate-specialist-team>, notebook `managed_agents/CMA_coordinate_specialist_team.ipynb`.

Shape: one coordinator, three narrow specialists each with its own prompt and tool set, and an advisor entry in the same roster.
"Each entry is a full agent with its own model, prompt, and toolset, so you could mix model tiers per role."

A specialist prompt, verbatim, showing the hand-back contract:

```
The case study library is in /mnt/user-data/case_studies/. Each file is one customer story.
You will be given a prospect's industry, size, and top priorities. Read the library, score each study on relevance, and pick the two best matches.
Return via send_to_parent: {"picks": [{"file": ..., "customer": ..., "why_relevant": ...}, ...]}
```

Every specialist ends with a `Return via send_to_parent: {...}` line naming a JSON object.
The coordinator's prompt sequences them ("Send the prospect's industry and size to prospect_researcher", then the picker once the researcher reports, then the pricing modeler) and consults the advisor "before writing" to check the picks.
Completion is the event stream: the caller breaks on `ev.type == "session.status_idle"`; advisor guidance arrives as `agent.thread_message_received` from `anthropic.advisor`.

What copies: one objective, one owned input, one JSON hand-back per specialist.
In a Claude Code workflow script the hand-back is the `schema` option of `agent()`, and the coordinator is the script itself.
What does not: `send_to_parent`, `session.status_idle`, the roster, and the sandbox paths.

## Programmatic tool calling

Source: <https://platform.claude.com/cookbook/tool-use-programmatic-tool-calling-ptc>, notebook `tool_use/programmatic_tool_calling_ptc.ipynb`.

"Programmatic Tool Calling (PTC) allows Claude to write code that calls tools programmatically within the Code Execution environment, rather than requiring round-trips through the model for each tool invocation."
It needs the beta `advanced-tool-use-2025-11-20` and the server-side code execution tool on `client.beta.messages.create`; the notebook demonstrates it on `claude-sonnet-4-6` only.
API-only; a `claude -p` call cannot set the beta.
The CLI has the equivalent: the Bash tool lets the worker write a script that calls several commands and filters their output before any of it enters the context.

## Tool search with embeddings

Source: <https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings>, notebook `tool_use/tool_search_with_embeddings.ipynb`.

"Semantic tool search solves this by treating tools as discoverable resources. Instead of front-loading hundreds of definitions, you give Claude a single `tool_search` tool that returns relevant capabilities on demand, cutting context usage by 90%+ while enabling applications that scale to thousands of tools."
Same beta header; same single demo model.
API-only; the CLI has the equivalent: deferred tools plus the native `ToolSearch` tool, which every Claude Code session already lists.
The factory already cuts the grader prefix from 27k to 9.9k tokens with `--strict-mcp-config` and `--disable-slash-commands` (`../factory/LOOP.md`, Grader calls), which is the same lever applied by flag.

## Cookbook survey

From the `anthropics/claude-cookbooks` tree and the four other notebooks Samyak named, read 2026-09-09.

| Notebook | What it shows | Runs where | Factory use |
|---|---|---|---|
| `managed_agents/CMA_consult_an_advisor` | advisor roster entry, consultation policy prompt | Managed Agents cloud | prompt copied into F11 |
| `managed_agents/CMA_coordinate_specialist_team` | coordinator, three specialists, JSON hand-back | Managed Agents cloud | shape copied into F12 |
| `managed_agents/CMA_verify_with_outcome_grader` | a grader scores the outcome, not the transcript | Managed Agents cloud | already the judge; nothing new |
| `claude_agent_sdk/08_Dynamic_workflows` | workflows generated at run time from the Agent SDK | Agent SDK | the Workflow tool is the CLI form; F12 uses it |
| `patterns/agents/async_multi_agent_orchestration` | async fan-out and gather over the Messages API | Messages API | the `parallel()` primitive covers it |
| `tool_use/programmatic_tool_calling_ptc` | code that calls tools inside code execution | Messages API beta | Bash tool is the equivalent |
| `tool_use/tool_search_with_embeddings` | one meta-tool that loads tool definitions on demand | Messages API beta | `ToolSearch` is the equivalent |

## What the factory takes

- F11, Fable advisor on the worker round: `--advisor fable` on the single worker call in `bin/factory run`, the consultation policy from the cookbook adapted into `bin/factory.d/_common.md`, a probe that the advisor attached, and `advisor_calls` and `advisor_usd` on the ledger line read from `server_tool_use` blocks and `modelUsage`.
- F12, saved Workflow fan-out for large tickets: the specialist shape (objective, owned files, JSON hand-back per task) as a workflow script run by the worker, with the glob-overlap check from unlazy and an integrator that reruns every check.
- F13, the borrowed gates that were still prose: `verdict_consistent` landed in F1 (`bin/factory`, `verdict_consistent()`), so F13 records what landed and adds the fixture test; nothing from this note is in it.
- Nothing from PTC or tool search; the CLI already has both.
