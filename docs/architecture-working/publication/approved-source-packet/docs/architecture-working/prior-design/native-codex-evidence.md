# Codex native adapter evidence and design recommendation

Status: bounded source investigation. Recommendation, not an approved implementation. Runtime implementation and live probes remain deferred. No model or effort was changed. No server or worker was launched. CLI help and offline protocol-schema generation were the only Codex commands used.

## Decision and strongest qualification

Recommendation: use a directly owned `codex app-server --stdio --strict-config` subprocess as the primary Codex transport. Retain native Codex threads, turns, instructions, skills, tools, connectors and delegation. Loam owns admission, durable authority, outcome checks and recovery. Do not substitute a Responses API loop for the native product. Keep `codex exec` as a credible simpler alternative for isolated batch work, rather than implementing both transports in the first slice.

Verified: the installed app-server protocol has explicit start, steer, interrupt, resume, approval and descendant-observation interfaces. The inspected exec surface supplies batch JSONL and resume, but no comparable live steering/approval channel. Sources: installed help and generated schemas below; [official app-server documentation](https://learn.chatgpt.com/docs/app-server).

The strongest qualification is configuration control. Verified: `exec` exposes `--ignore-user-config` while retaining authentication from `CODEX_HOME`; the inspected app-server help exposes overrides and strict config but no corresponding flag. Neither strict parsing nor reading effective settings proves that personal hooks, skills and MCP configuration were excluded or that inputs cannot change during an attempt. Recommendation: make reproducible configuration plus preserved authentication and native capability the first admission probe. Do not silently discard project-native capabilities, inherit undocumented personal assets, or describe a new config home as authentication-transparent. An unresolved capability gap blocks the relevant autonomous profile; it does not change ordinary interactive Codex use.

## Evidence and read scope

Verified local main: `d627bb2755ad49865f798bcb095800ddd2ad1ced`. `git status --short` returned no entries. No repository files were changed by this investigation.

Read current `bin/factory` native routing and helpers, especially lines 717–778 and 794–834; related searches covered model labels, personal skill resolution and workflow routing. Read accepted working configuration design, state design and records/transitions contracts in `/private/tmp/loam-architecture-design/`.

Verified executable: `/Users/samyakjhaveri/.local/bin/codex`; `codex --version` returned `codex-cli 0.153.4`. Read `exec --help`, `exec resume --help`, `app-server --help`, and `app-server generate-json-schema --help`. Help and schema commands warned that PATH aliases could not be created under the sandbox; schema commands exited successfully and their files were read. No auth or private settings contents were opened.

Offline generated sources are in `native-codex-sources/schema/` and `schema-experimental/`, generated with `codex app-server generate-json-schema --out <directory>`, with `--experimental` for the latter. Relevant `v2` schemas inspected: ThreadStartParams/Response, ThreadResumeParams, ThreadReadParams, ThreadListParams, ThreadLoadedListParams, TurnStartParams, TurnSteerParams, TurnInterruptParams, ConfigReadParams/Response, PermissionProfileListParams, ModelListResponse, ModelReroutedNotification, ThreadTokenUsageUpdatedNotification, and background-terminal list/terminate/clean schemas. Thread, Turn, ThreadItem, source, status, effort and usage definitions were inspected within these files. These local schemas establish the exact interfaces of the installed CLI, not a live service guarantee.

Original official URLs and stored reading scope:

- [App server](https://developers.openai.com/codex/app-server), redirected to [current documentation](https://learn.chatgpt.com/docs/app-server). Stored Markdown: `native-codex-sources/app-server.md`, fetched from `https://learn.chatgpt.com/docs/app-server.md`. Read transport and initialization, lines 1–8, 57–136 and 194–293; model discovery 387–428; thread creation/resume 486–553; thread read 636–649; turn inputs/start/steer/interrupt 914–1075; requirements 1201–1227; events and approvals 1272–1455; skill discovery/invocation 1456–1509. Selected listing/background-terminal sections were also read; exact field claims below use generated schemas.
- [Noninteractive execution](https://developers.openai.com/codex/noninteractive), redirected to [current documentation](https://learn.chatgpt.com/docs/non-interactive-mode). Stored Markdown: `native-codex-sources/exec.md`, fetched from `https://learn.chatgpt.com/docs/non-interactive-mode.md`. Read lines 1–128 and 178–192 for execution/events, config isolation, required MCP failure and resume.

No claim is made to have read all implementation source of Codex or exercised its service. The installed CLI protocol is the concrete source root; official documentation supplies intended semantics. A source-code audit would be a separate task if probes reveal ambiguity.

## Existing Loam and proposed boundary

Verified: current `bin/factory:815` invokes `codex exec --json -s workspace-write`, adds Git metadata directories as writable, supplies the prompt as an argument and writes the last message separately. It does not select the real model or effort there. `CODEX_MODEL` is a ledger label. `codex_result` derives success/error and usage from JSONL. Skill bodies are pasted into prompts after resolving personal Claude skill/plugin paths. The workflow branch excludes Codex native fan-out. A `.codex` symlink is temporarily replaced by a directory and restored around a worker round.

Recommendation: replace these assumptions with a native adapter, rather than preserve them as compatibility obligations. Project-shipped asset resolution must replace personal skill lookup. Use typed native skill input where supported. Record returned native model/config metadata rather than the ledger label. Treat native child activity as observable work. Resolve generated-project configuration layout deliberately instead of assuming development-checkout symlink workarounds are the shipped design. Existing graders can remain downstream checks if separately validated; a native turn completing never means the ticket is accepted.

Dependencies: accepted profile compiler, supervisor action/attempt records, shipped asset manifest, evidence spool, workspace preparation, approval routing and check population. These are shared Loam concerns, not separate Codex copies.

## Concrete operational contract

The app-server interface is bidirectional JSON-RPC-style messaging over JSONL on stdio, omitting the `jsonrpc` header. Initialize once per connection with client identity/capabilities, then send `initialized`. Pin the supported CLI/schema and explicitly opt into needed experimental fields. Recommendation: initially own a subprocess per admitted native conversation, with native descendants inside it. Keep ownership distinct from the Loam run: compatible subsequent attempts may resume a native thread after reconciliation. Avoid a shared remote daemon and new network listener in the first slice.

| Loam operation | Verified native interface | Loam obligation or limit |
|---|---|---|
| Discover compatibility | `model/list`, `config/read`, `configRequirements/read`, `permissionProfile/list`, `skills/list` | Later readiness probes only. Compare against admitted constraints; redact config to relevant nonsecret fields. A catalog default never authorizes changing the user's selection. |
| Begin conversation | `thread/start` with `cwd`, `model`, `config`, approval policy and supported permission form | Persist dispatch intent first. Start response includes thread identity, model, reasoning effort and instruction source paths. Hash declared content separately; paths alone are weak evidence. |
| Admit native attempt | `turn/start` requires `threadId`, `input`; supports explicit `model`, `effort`, `cwd`, `outputSchema`, approval and sandbox fields | Persist action authorization before sending. Tie returned turn ID to the attempt. Model and effort overrides can persist as later defaults, so compile every admitted turn explicitly. |
| Add compatible information | `turn/steer` requires `threadId`, `expectedTurnId`, `input` | Active-turn precondition prevents steering a different turn. It does not accept model, effort, permission or workspace overrides. Changed objective/profile follows Loam barrier and successor rules. |
| Pause/cancel active work | `turn/interrupt` with `threadId`, `turnId` | An empty acknowledgement is not quiescence. Observe terminal turn status, children and background work before claiming execution stopped. Authority barrier takes effect independently. |
| Recover conversation | `thread/read` with explicit thread ID and optional `includeTurns`, then `thread/resume` | Read/reconcile before another dispatch. Resume does not itself repair unknown action outcome. Avoid `--last`, names, guessed history paths or treating replay as a new action. |
| Observe work | thread/turn/item notifications, warnings, model reroutes, token usage | Raw native evidence plus a versioned projection. Intermediate text and native completion cannot authorize acceptance. |
| Resolve native request | Server-initiated approval, permissions, user-input, MCP elicitation messages | Persist request identity and scope. Respond only under current admitted authority; new consequential permission asks reach the human. |

Verified schema detail: `TurnStartParams` and `TurnSteerParams` have `clientUserMessageId`, but the inspected definition does not establish server-side exactly-once dispatch. Recommendation: use identifiers for correlation without promising deduplication. Missing start acknowledgement remains an unknown action until reconciliation proves its outcome. JSON-RPC request IDs are not a global durable event sequence. Store local stream positions and preserve replay provenance; do not deduplicate identical legitimate messages by content alone.

## Model, effort and native capability

Settled requirement: Astra drives Codex work; only Astra, Sol and Terra are permitted, and the user controls effort/model changes. This applies to research, critique and memory tasks as well as coding. The adapter does not select new values in this design.

Verified: reasoning effort is a string supported by a model's advertised capabilities, not a universal fixed enumeration in this installed schema. `thread/start` can take config overrides, and `turn/start` directly carries effort. The experimental `allowProviderModelFallback` field can explicitly disable the described fallback to a static-catalog default when a requested model is unavailable. Recommendation: use false where supported, admit only the chosen supported profile, and stop on incompatibility. Do not follow catalog upgrades automatically.

Verified: experimental `collaborationMode` takes precedence over model, effort and developer-instruction overrides. Deprecated `multiAgentMode` is ignored; the schema describes a relation to Ultra effort. Recommendation: do not set either to smuggle in a different effort or policy. Native delegation follows explicit user authorization and an admitted descendant profile.

Verified: native thread metadata describes the currently configured or latest persisted model and effort, not per-turn execution telemetry. Native collaboration items expose the requested spawn model/effort and child identities. `model/rerouted` reports from/to model for a turn. Recommendation: distinguish requested, admitted, configured and observed evidence. Capture reroutes and stop disallowed execution when observable. Neither prompt rules nor configured metadata proves that every descendant can be prevented from using another model. Strict descendant enforcement is a required live probe before admitting that autonomous team profile.

Verified native capability: typed skill input supports name and path; native skills discovery exists. Recommendation: resolve skill identity to shipped/project-owned assets, preserve support files and native instructions, and supply typed references instead of pasting only a SKILL.md body. Native connectors, research tools, terminal experiments and delegation remain native. Do not replace all tools with a lowest-common-denominator Loam toolbox. Only supervisor-authority actions require explicit Loam mediation.

## Descendants, approvals and recovery

Verified: the installed `ThreadItem` union uses `collabAgentToolCall`, while the inspected current documentation summarizes a differently named `collabToolCall`. It supplies sender/receiver thread IDs, native operation, status and last-known agent state. This is concrete schema drift: use the pinned schema, preserve unknown event kinds, and require a version compatibility check rather than coding against prose examples.

Verified: native thread metadata includes `parentThreadId` and `sessionId`; session identity can group a live thread tree and must not be derived from guessed IDs. Experimental `thread/list` filters include ancestor and parent IDs. Background terminal listing/termination/cleanup are separate experimental methods. Recommendation: track root, descendants and background processes separately. Root completion is not proof of descendant or command completion. If interruption or recovery cannot establish quiescence, retain the barrier and classify unresolved work rather than automatically retrying its side effects.

Verified: approvals can carry turn/session scope, and `serverRequest/resolved` may mean answered or cleared. Recommendation: store the actual answer and authoritative scope, not just the notification. Do not grant future session authority casually. A deadline for user input does not create permission. After pause/cancel, reconcile requests before answering; clearing a request does not prove an operation executed or was rolled back.

Verified: token notifications expose last/total counts, including cached and reasoning counters. Recommendation: preserve counters and their reported scope. Do not invent monetary cost, treat missing usage as zero, or add parent and child totals until inclusion semantics are proven. Usage received after cancellation remains accountable.

## Research-to-implementation example

Recommendation: the same adapter can run an inquiry asking whether a proposed data format supports a required migration. The admitted inquiry names source roots, required comparisons and an evidence destination. Astra uses native retrieval, asks permitted native specialists for independent critiques, and returns artifacts with actual source-access scope and conflicting findings. Loam records claims and unresolved evidence obligations; native completion does not certify the research answer.

A bounded experiment then receives its own admitted scope and runnable check, even if proposed during that conversation. Its command output belongs to the experiment's evidence. A human engineering decision cites inquiry and experiment artifacts. An implementation ticket references that decision and acceptance checks. Another admitted turn implements it; the supervisor runs the required checks against the identified candidate. Memory promotion records the accepted conclusion, applicability, source and supersession link. An agent's transient opinion is not promoted merely because it appeared in a finished thread.

Later steering such as “also compare offline operation” first creates the accepted Loam barrier/revision decision. Compatible clarifying material may use `turn/steer`; changed requirements require a successor scope. Existing native context can be reused only after reconciliation, with stale results explicitly marked as context.

## Runnable acceptance probes for a later authorized slice

These are proposed checks, not executed tests. The smallest adapter proof needs one owned app-server connection, one native root, one declared skill, one admitted turn, one interruption/recovery path and one independent outcome check. Research and implementation can use this same mechanism; a broad team scheduler is unnecessary to prove the contract.

| Probe | Runnable fixture/check to implement | Required result |
|---|---|---|
| Version and protocol | Generate schemas from the pinned CLI and validate recorded request/event fixtures against them. | No invented field, stable/experimental use explicit; drift rejects unsupported adapter versions. |
| Config and auth boundary | Temporary generated-project fixture plus controlled conflicting user settings, hooks, skills and MCP entries; request a harmless read with the admitted profile. | Declared native assets function; undeclared conflicting assets cannot change the attempt; auth still works without undocumented personal provisioning. Record sources without secrets. |
| Models and descendants | Allowed root and child profile fixture, plus unavailable and disallowed selection cases; inspect metadata and reroute/child events. | User-selected effort preserved; no silent fallback. Demonstrate actual enforcement or mark autonomous team capability unsupported. |
| Start uncertainty | Kill the client after dispatch but before acknowledgement, restart and reconcile stored native identity/history. | No blind duplicate turn or side effect; unknown stays unknown until evidence resolves it. |
| Steering and barrier | Delay a turn, send expected-turn steering, then issue a scope change/pause and race a late completion. | Compatible steer targets the intended turn; late output cannot cross the Loam authority barrier. |
| Quiescence | Turn that owns a native child and background command; interrupt and inspect all observed owners. | Acknowledgement never substitutes for stop evidence; unresolved descendant work blocks unsafe retry. |
| Approval scope | Native request requiring a new permission, followed by pause before reply. | No stale approval; request remains attributable; no timeout becomes human authorization. |
| Acceptance separation | Native output claims success while an independent required check fails. | Candidate remains unaccepted; failure evidence opens a repair attempt under existing contracts. |

## Self-attack and residual risks

- Input that breaks the design: a native child or config reload violates the profile without an enforceable boundary. Repair: capability admission depends on dedicated probes, not prompt compliance.
- Unchecked path: actual authentication, service execution, config reload, native descendant stopping and approval races. No runtime was authorized, so these remain unverified.
- Untested change: this report only; no runtime change or passing-test claim.
- Unsupported assertion removed: returned model metadata is not execution proof, interrupt acknowledgement is not quiescence, and request correlation is not exactly-once dispatch.

Risks: app-server and important permission/descendant fields are experimental in the installed version. Configuration isolation with preserved auth remains the first blocker to resolve. Dollar accounting and parent/child usage inclusion are unproven. The proposed adapter is appropriate to the accepted rich native workflow, but committing to it should follow these narrow capability probes when runtime experiments are explicitly authorized.
