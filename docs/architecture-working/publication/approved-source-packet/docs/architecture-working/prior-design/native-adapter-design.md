# Native adapters for research engineering

Status: proposal following accepted work records, transitions, SQLite/artifact storage and native configuration direction. Runtime implementation remains deferred. This design is grounded in current Loam source, the original resources already reviewed and explicit engineering judgment. Provider interface evidence is recorded separately in native-codex-evidence.md and native-claude-evidence.md.

Critical point: native capability, input delivery and lifecycle observation must not be overstated by a common adapter interface.

## Purpose and boundary

Recommendation: use a common work envelope around provider-native execution. The envelope specifies the question or objective, admitted scope and method, available evidence, expected deliverables and authority. It does not prescribe every search, tool call, hypothesis or subagent action. Native leads can discover solutions, revise their investigation within scope, delegate substantial independent work and synthesize criticism.

Loam owns admitted records, durable steering, ownership, accounting, required evidence and acceptance. The selected native host owns its model conversation, native tools, skills, compaction and supported coordination features. The adapter translates between those boundaries and preserves raw native observations. It does not imitate the other provider or implement a second model/tool loop.

Settled requirement: Codex uses Astra as driver and only Astra/Sol/Terra; Claude uses Fable 5.1 as driver and only Fable 5.1/Opus 4.8. User-selected effort remains controlling across all roles. Research, engineering decisions, implementation, experimentation and memory maintenance use the same lifecycle, with different work methods and evidence requirements.

## Basis for the design

| Basis | Verified source or existing behavior | Engineering choice derived from it |
|---|---|---|
| Current Loam | bin/factory:815 launches Codex exec; 843 launches Claude print mode; codex_result converts native events into a Claude-shaped result; current loop has no durable bidirectional steering bridge | Replace invocation/normalization boundaries behind the accepted record contract. Preserve raw native event identity and separate typed common observations. |
| Adaptive research | S14 multi-agent research and S15 effective-agents articles support iterative decomposition, bounded delegation and source/artifact handoff | Keep inquiry and deliberation agent-led inside admitted scope. Preserve reports before critique and retain dissent. Do not force every unknown into a multi-ticket build. |
| Durable execution | S13 Managed Agents separates durable events from execution/harness; S01 LoopX distinguishes planned recovery from actual execution | Adopt the lifecycle principle locally around native hosts. Do not import the Managed Agents cloud API or claim a native resume is sufficient proof of safe replay. |
| Context and memory | S08/S59/S68 track source provenance, failed approaches and correction/invalidation with different implementation limits | Use task-specific context packets and source-linked artifacts. A supplied packet is not proof of native inclusion or source inspection. |
| Evidence quality | S37 outcome grader, S55 issue lifecycle and X09 claim-artifact verification provide useful shapes with documented limits | Required outputs have identities, coverage and unresolved status. Evidence existence, model agreement or native success does not establish substantive support. |
| Native control | Original provider docs and the installed Codex schema/help, scoped in the provider evidence reports | Prefer supported bidirectional native control for steered work. Keep narrower native process profiles explicit rather than claim identical capabilities everywhere. |

The final column is my engineering recommendation. The sources motivate mechanisms and failure cases; they do not empirically validate Loam's proposed architecture. Source scope, upstream limitations and reuse terms remain in reference-reading.md and source-informed-design.md.

## Native entry and managed execution

Recommendation: ordinary human discussion stays in Claude Code or Codex. Shared shipped skills help turn that discussion into a bounded inquiry, design decision, experiment or implementation request. The integration preserves the original request and source context so the user need not re-enter it into a separate planning system.

An admitted managed run executes through an owned native session whose lifecycle the adapter can observe/control. Starting a managed session can use context from the conversation without pretending it inherited unobservable reasoning or private memory. Attaching an already-running native session requires proven ownership, input/output visibility and interruption capabilities; it is not assumed merely because a session ID is known. Ordinary exploration need not become a managed run automatically.

Recommendation: support a full bidirectional execution profile and a narrower process profile for each provider where supported. Codex app-server is the recommended full-profile candidate; Claude Agent SDK streaming is the recommended Claude candidate. Exact supported methods and limitations belong to the provider reports. CLI exec/print modes remain useful for bounded unattended stages and diagnostics. They are not a silent fallback after an uncertain richer-session failure. Changing transport requires compatible readmission and reconciliation of prior work.

Verified: the provider investigations checked installed Codex help/generated schemas and official Claude documentation/published SDK declarations. They establish interface availability, not tested host behavior. See [Codex evidence](native-codex-evidence.md) and [Claude evidence](native-claude-evidence.md) for exact sources, versions and read scope.

| Proposed primary transport | Verified interface basis | Admission limit and engineering response |
|---|---|---|
| Codex owned app-server over stdio | Native thread/start, turn/start, turn/steer with expectedTurnId, turn/interrupt, thread/read and thread/resume; bidirectional native requests | App-server help lacks exec's ignore-user-config flag. Configuration isolation with preserved authentication and project capabilities is the first probe. Pin installed schemas; important descendant/permission controls are experimental. Configured/requested model metadata is not complete execution proof. |
| Claude official TypeScript Agent SDK open-input query | Async input/output, public interrupt(), stopTask(), explicit session resume, permission callbacks and native subagents | Public interrupt() exposes no queue-cancellation option. Track consumed UUIDs separately from queued input; reconcile stale input and background work before continuation. SDK subagents do not supply interactive native teammates. Cumulative usage omits some hidden helpers. |

Recommendation: use these primary transports for the full steered profile, subject to those admission probes. A TypeScript Claude bridge does not select the supervisor's language. Python ClaudeSDKClient and CLI batch execution remain credible narrower alternatives, not parallel first-slice obligations. Strict descendant model enforcement and effective profile isolation remain unproven and must not be promised from prompts or metadata alone.

Interactive native team features remain available through their actual host surface. A headless subagent path cannot claim interactive-team behavior. Required collaboration capability determines profile admission. An unsupported requirement must not be replaced with inline role imitation. Conversely, a task that permits native subagents does not need interactive teammates merely because the feature exists.

## Common work envelope

These are proposed Loam fields, not provider API parameters. Use referenced immutable artifacts for large inputs and structured fields for enforceable boundaries.

| Part | Contents and purpose |
|---|---|
| Identity | instance, work/revision, run, stage, attempt, current owner/incarnation and expected plan/required-population manifest |
| Intent and authority | Original user request reference, normalized question/objective, constraints, allowed actions, unresolved consequential questions and applicable steering |
| Method and obligations | Work kind, admitted method, stage dependencies, expected deliverable/claim/report identities, review assignments and stopping conditions |
| Execution profile | User-controlled model/effort, permissions, native surface, role/skill/tool capabilities, approved managed/project asset identities and local binding references |
| Context and evidence | Relevant current decisions, prior failed approaches, source artifacts/read scopes, candidate baseline, uncertainty and contradictory findings; intended delivery status recorded separately |
| Workspace and outputs | Owned workspace/candidate inputs, read-only references, attempt staging, declared external jobs and output artifact locations; no control-store authority |
| Interaction and limits | Supported progress/question/approval/steering channels, accounting-scope reference, remaining admitted bounds and stop policy |

Recommendation: adapt the task method, not the fundamental lifecycle. An inquiry packet asks for question/method/evidence/conclusion/limits. A deliberation packet requests independent reports, concrete critique and synthesis reasons. An experiment packet binds method, source/data/environment identities, execution logs and interpretation. An implementation packet binds behavior and checks. A memory packet asks for applicability-limited lessons with sources and correction history. These may be composed; not every task needs every stage.

## Adapter operations and receipts

The operation names here describe Loam responsibilities; providers need not expose these exact names.

| Operation | Required behavior | Result Loam may rely on |
|---|---|---|
| Inspect readiness | Check selected host/interface compatibility, required native capabilities, role configuration, local tools/credentials availability and input/output protection before activation | Static facts versus later probe requirements; exact missing capability. No provider job or connector startup hidden inside a claimed read-only check. |
| Prepare | Build provider-native settings/input from admitted assets, preserve compatible native context and capabilities, allocate attempt staging | Desired launch and intended context manifest, not effective-state proof |
| Start | Consume the current dispatch authorization through the selected native transport; retain attempt/action identity | Native handles/events or uncertain launch requiring reconciliation |
| Observe | Read provider events and final outcomes; persist raw evidence then normalized facts with stable identity/order | Turn/job status, artifact references, usage provenance, model/config observations and explicit unknowns |
| Ask or request approval | Persist a native question/approval as a pending request with exact action, authority and revision; answer automatically only within already granted policy | Answer/decision bound to the actual request; unavailable human input becomes waiting, not implicit approval |
| Deliver steering | Accept only current authorized steering after any required Loam barrier is durable; map to supported native input and preserve original user provenance | Separate persisted, sent, host-acknowledged/queued and applied evidence. Never infer application solely from transport success. |
| Interrupt | Request supported interruption and enumerate/reconcile observable background work | Request/acknowledgment and physical job evidence are distinct; no false claim that parent interruption stopped all descendants |
| Reconcile/continue | Reconcile prior handles, queued input, background jobs, side effects and compatible session state and newly validated effective profile before another attempt | Explicit reuse/restart/block choice with reasons; same native session does not mean same attempt or automatically current criteria |
| Collect | Capture complete attempt artifacts after quiescence or a supported immutable handoff; validate envelope and required population | Original result and artifact inventory for trusted evaluation; acceptance remains a separate transition |

Recommendation: session reuse also obeys role independence. A required independent reviewer receives a fresh native context containing the admitted candidate, criteria and permitted evidence. It cannot inherit the producer's conversation or become independent by changing a role prompt. Independent research reports are captured before critique exposes peer reports; synthesis may then compare them openly. This rule does not require needless resets within a continuing producer or researcher role.

Every continuation prepares a new immutable attempt envelope and checks the retained native settings and context against its admitted profile, including model/effort, permissions, loaded assets, workspace and output destination. Bind fresh observations to that attempt; a previous receipt cannot certify changed inputs. If a required setting cannot be replaced or established, use a fresh session after reconciliation or block the continuation. This inherits configuration-design.md's immutable-input rule.

Recommendation: observations should distinguish native configuration from execution telemetry. Preserve requested, resolved and observed model/effort with scope/provenance; missing auxiliary observations are not compliance. Known disallowed execution blocks continuation and requests interruption. Hooks or generated settings are not the sole enforcement mechanism. Required but unestablishable policy guarantees block the affected managed profile, without inventing a provider fallback.

## Questions, approvals and steering

Recommendation: the native lead can ask a consequential research or engineering question without terminating the entire factory. Persist what it needs, the work it affects and the expected revision. Continue independent obligations whose dependencies permit progress. Stale answers are linked to the old request and require applicability assessment before current use.

Native tool approvals are action-specific. A policy-authorized read can be answered through the native approval interface; an expansion of permissions, model/effort or external authority cannot. Store exactly what decision was made and for which native request. On connection loss, reconcile the original pending request rather than fabricate approval or replay an old approval against a new request. Credentials establish access, not permission to use every available action.

Recommendation: classify every native input as informational delivery, amendment of active work, or execution-triggering input. Approval replies, question answers and queued follow-ups can start or resume execution. Immediately before such delivery, use the accepted dispatch/continuation authorization contract: current revision, owner/incarnation, reservations and pause/cancel/revise barriers must still permit the action. Prior permission alone is insufficient. Include every already-delivered input capable of triggering work in the in-flight inventory. A pause stops admission of affected work even when native queued execution cannot yet be proven stopped.

For user correction, Loam first records the request/barrier under the accepted transition rules. Then the adapter delivers it through the native interface. Track distinct facts: accepted by Loam, sent to host, host acknowledgment or queued identity, model-visible/application evidence where available, and validated resulting artifacts. Text generated by the factory is not relabeled as genuine human input to pass a native gate. Forwarded human provenance must originate from an authenticated user channel and retain its source identity.

A material revision creates a successor run. A live steering API may assist interruption or transition, but it cannot silently relabel old outputs with the new revision. For the first implementation, use a reconciled boundary before executing the successor; reuse the native session only when prior queued instructions and jobs are compatible and observed. Helpful information within the same scope can use live delivery if the profile supports it.

Recommendation: interruption and queue cancellation are separate. If the selected public native interface cannot remove obsolete queued input, do not pretend it did. Use a fresh session only after old execution is reconciled, or report the unresolved capability. Background tasks need actual task-stop controls and observed lifecycle; advertising an affordance the user cannot operate does not make it real. The source-specific details are recorded in native-claude-evidence.md.

## Artifacts and evidence from native work

Recommendation: a final message is a summary and pointer to deliverables. It is not the only surviving research artifact. Capture source records, independent reports, experiments and findings while work proceeds. Large observations stay in artifacts so a coordinator can reopen them directly instead of relying solely on compressed peer summaries.

The native lead may emit a structured stage result. Where a native host lacks the desired final schema support, validate a declared result artifact or parse a documented output form, preserving failures explicitly. A schema-conforming result still needs its actual artifact and semantic checks. It must identify missing/blocked work, source read scope, unresolved jobs and outcome limits. Required report/claim identities are checked against the registered population before synthesis or acceptance.

Normalization must preserve failure distinctions and native specificity. Keep raw event references and supported provider fields rather than converting every event to a Claude-like result shape. Unknown/new events remain stored and surfaced when they affect a required guarantee. The adapter does not treat a missing final event, a disconnected transport, a token limit or a goal being cleared as successful completion.

## Research engineering example

Illustrative end-to-end use, not an experiment run in this session: the user asks whether retaining failed approaches can improve later experiment choices without anchoring agents to obsolete assumptions.

1. A generated project has the complete factory and empty project memory. Its native lead reads the idea, identifies existing project evidence and proposes a bounded inquiry. It does not assume the desired answer is positive or turn the question directly into an implementation ticket.
2. Independent native researchers examine original studies/methods and actual candidate implementations. Consensus is preferred for relevant scholarly discovery when the generated project's declared connection is available; source acquisition/readiness and alternative methods are explicit. A search hit is not a read paper, and a linked code repository is not inspected implementation.
3. The lead compares reports, preserves contradictory findings, and organizes critique of concrete claims. It proposes a comparison against ordinary project notes/no retrieved lessons, including stale-memory cases. The method and evaluation criteria are admitted under the project's authority before experiment execution.
4. A native engineering worker prepares the bounded experiment and records exact code/data/configuration and model/effort identities. Native tools run the experiment; background jobs have lifecycle records. An evaluator crash is an execution error, not evidence that memory is harmful or useful.
5. The user adds a concern about misleading lessons from an older dependency version. Loam records the change, preserves existing data and holds affected acceptance. A materially changed method gets a successor revision/run with the same accounting scope. Independent compatible work can continue. The adapter's input receipt does not itself claim that the model incorporated the correction.
6. The resulting report binds claims to the actual experiment artifacts, contrary cases and read sources. A reviewer checks the declared method, result provenance and supported conclusions. The inquiry may be accepted as inconclusive if that meets the admitted method; a positive improvement claim needs its own evidence.
7. A decision can recommend further research, reject the approach or propose a specific implementation ticket. A lesson records the conditions and limitations of the result. It does not automatically change the shared factory, permission policy or model/effort. A reusable improvement enters the accepted Loam update/ownership path.

This is the same operational contract as a coding ticket with different method/evidence content. Experimental quality still requires domain judgment and evaluation; adapter correctness does not establish scientific validity.

## Existing code and proposed implementation slices

Verified current source: bin/factory:765 normalizes Codex events to the existing result object; worker_round:815/843 invokes native processes; current prompts and skill resolution contain personal-cache dependencies and restrictive native launch choices. The proposed adapter replaces those responsibilities rather than adding a competing controller. Source findings are inspection, not new runtime tests.

| Proposed change | Dependency | Future runnable acceptance interface, not implemented or run |
|---|---|---|
| Common envelope and observation/result validation | Accepted records, artifact capture, method manifests | python3 -m unittest discover -s bin/tests -p test_factory_adapter_contract.py : wrong attempt/revision, missing report IDs, partial source access, native completion without valid artifact |
| Codex native bridge | Pinned supported protocol, native permission/model/context mapping | python3 -m unittest discover -s bin/tests -p test_factory_codex_adapter.py : stale-turn steering, pending approvals across disconnect, unknown events, interruption plus live child, configured versus observed identity, resume after model/policy asset change without reusing an old receipt |
| Claude native bridge | Supported public streaming SDK, input provenance, background-task controls and permission callbacks | python3 -m unittest discover -s bin/tests -p test_factory_claude_adapter.py : queued stale input, genuine versus generated input provenance, interrupt without confirmed stop, unresolved background task, required feature absent |
| Shared question/steering bridge | Trusted user/control channel, named barriers, native correlation IDs | python3 -m unittest discover -s bin/tests -p test_factory_native_steering.py : sent/queued/applied distinction, stale answer, approval answered after cancel, queued follow-up after pause, revision before/after native delivery, no synthetic approval |
| Research/memory work packets in every seed | Shipped methods/roles, evidence schemas, declared research tool bindings | python3 -m unittest discover -s bin/tests -p test_factory_native_research.py : inquiry without coding ticket, incomplete acquisition, independent reports before critique, rejected producer-to-reviewer session reuse, valid negative/inconclusive result, failed experiment and scoped lesson |

Mechanical fixtures first model the protocol without provider/model calls. Later authorized native probes exercise actual host behavior on a clean generated project with declared prerequisites. The complete fixture path must work independently of the Loam development checkout. Interface selection is not authorization to install, launch or activate it now.

## Decisions for discussion and self-attack

Recommendation: choose provider-native bidirectional control as the target for the complete steered factory, with explicitly narrower process profiles where their semantics suffice. Preserve ordinary native conversation as the idea/research entry point. Do not flatten provider features or mistake requested settings, delivered input, returned text or transport shutdown for stronger facts.

Self-attack: a model could receive stale queued instructions after interruption; queue reconciliation is explicit. A supposed human instruction could be fabricated by a worker; provenance belongs to the trusted control channel. A parent can exit while experiments continue; child/job reconciliation is required. A research report can look complete while omitting failed branches; expected population and evidence records remain authoritative. Native protocol drift can invalidate assumptions; pin interfaces and test actual supported schemas. These are proposed contracts and risk-driven checks, not already implemented guarantees.

Independent critique resolved: execution-triggering inputs now require current continuation authority; independent review cannot inherit producer context; resumed sessions require a newly validated attempt/profile. Later fixture coverage names each failure case. Residual risks remain native configuration isolation, hidden model calls, stale queue control and descendant quiescence, pending authorized prototypes.

## Expanded cookbook audit refinement

See [cookbook-integration-design.md](cookbook-integration-design.md) and [practice registry](cookbook-practice-registry.md) for the source-audited method layer. These refine this draft: required dynamic-child admission precedes dispatch with actual native identity binding; managed interactive teams must satisfy fixed work guarantees including direct human input; native goal and supervisor continuation cannot compete; changed-method Workflow replacement belongs to a successor revision/run. Proven redacted consultation occurrence is distinct from inspectable advice. Generated projects initialize local state explicitly from shipped schemas/setup machinery. Proposed fixture placement is now the managed seed engine's tests directory.
