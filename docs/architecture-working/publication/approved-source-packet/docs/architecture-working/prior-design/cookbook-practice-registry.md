# Cookbook practice implementation registry

Status: reviewed design recommendations after source synthesis; no runtime code or fixtures implemented. Each source report contains exact original URLs, pinned code and read limits. This registry maps mechanisms to concrete implementation responsibilities, not a blanket endorsement of each source. See cookbook-integration-design.md for lifecycle and example, and cookbook-current-code-map.md for existing-to-proposed changes.

All commands below are proposed acceptance interfaces to implement later. They have not been run and their files do not exist yet. The test runner language does not choose the supervisor language. Detailed source-specific negative cases remain in the linked audits.

## intent: Original intent and method routing

Recommendation: **adopt**. Source mechanism: Basic workflows, research lead, ExecPlans and inquiry branch contracts.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Keep original request and immutable obligations separate from the evolving plan; validate allowed method IDs and their prerequisites.
Native mapping: Native leads choose a method; neither provider receives a rigid universal stage ritual.
Seed owner: methods + entry skills. Dependency group: methods.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_methods.py'`. Required case: Unknown route or polished answer to the wrong question remains unaccepted.

## premises: Plan premise and population verification

Recommendation: **adopt**. Source mechanism: CMA_plan_big_execute_small and effective-harnesses feature inventory.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Establish critical premises and expected population from evidence before required fan-out; preserve unverified premises.
Native mapping: Shared inquiry contract delivered through either adapter.
Seed owner: methods + evidence schemas. Dependency group: methods.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_methods.py'`. Required case: Correct answers for the wrong population fail coverage.

## plans: Living execution plans

Recommendation: **adapt**. Source mechanism: ExecPlans and later harness design.

Evidence: [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Maintain scope-linked progress, decisions, failed approaches and next work; plan edits cannot weaken authority.
Native mapping: Continue native conversation with a reopenable plan artifact.
Seed owner: planning skill + state links. Dependency group: methods.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_methods.py'`. Required case: A plan revision dropping an original requirement cannot satisfy it.

## subagents: Native specialist delegation

Recommendation: **adopt**. Source mechanism: SDK subagents, specialist team and native Codex subagents.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Self-contained task, source inputs, role profile and handback; register required child before dispatch and bind actual native identity.
Native mapping: Claude Agent/subagents; Codex native delegation, preserving real controls.
Seed owner: role contracts + adapters. Dependency group: coordination.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_coordination.py'`. Required case: Rejected admission or missing child binding never launches a duplicate or accepts output.

## async: Asynchronous coordination

Recommendation: **adapt**. Source mechanism: Async multi-agent orchestration and native delegation.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md).

Implementation: Track child liveness, messages, unfinished handbacks and parent outcome independently; retain all admitted accounting.
Native mapping: Use native messaging/events, not a replacement Messages/Responses tool loop.
Seed owner: adapters + supervisor inventory. Dependency group: coordination.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_coordination.py'`. Required case: Lead ends before late child/message; required work remains pending.

## dynamic: Dynamic workflows

Recommendation: **adapt**. Source mechanism: SDK Dynamic workflows and orchestration patterns.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md).

Implementation: Native lead proposes typed dependent work; supervisor admits required population; null/error/missing outcomes stay explicit.
Native mapping: Claude bounded Workflow; Codex native delegation and Loam method dependencies, no fictitious Workflow API.
Seed owner: methods + native workflow assets. Dependency group: coordination.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_coordination.py'`. Required case: Null verifier, duplicate claim and replayed sibling cannot reduce expected coverage.

## teams: Interactive agent teams

Recommendation: **optional native method**. Source mechanism: Native teams docs and research-team role contracts.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Use real teams when sustained peer interaction is useful; supervised guarantees fixed, otherwise explicit ordinary collaboration/evidence import.
Native mapping: Claude interactive teams distinct from SDK subagents; Codex uses its documented native coordination.
Seed owner: team method + native capability profiles. Dependency group: coordination.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_coordination.py'`. Required case: Unrecorded direct teammate steering prevents managed admission; no inline-role substitute for independence.

## advisor: Advisory consultation

Recommendation: **optional native method**. Source mechanism: Native advisor, CMA_consult_an_advisor and cost-optimization failure analysis.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md).

Implementation: Consult on consequential design, repeated failure or material completion doubt; record actual occurrence, identity, applicability and response.
Native mapping: Supported Fable-to-Fable native advisor; Codex separate admitted consultation agent, not server-advisor parity.
Seed owner: consultation role + receipt schema + native mapping. Dependency group: coordination.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_coordination.py'`. Required case: Enablement alone does not satisfy consultation. Proven occurrence/identity may satisfy an occurrence-only obligation that permits redaction; it cannot satisfy required inspectable advice, invent content or replace independent review.

## independent: Independent investigation and review

Recommendation: **adopt**. Source mechanism: Outcome grader, evaluator separation and research handoff.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Capture independent initial reports before peer critique; required reviewer gets fresh context with candidate, criteria and adequate source access.
Native mapping: Both providers use actual distinct contexts with allowed models; no universal different-model rule.
Seed owner: review roles + context compiler. Dependency group: evidence.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evidence.py'`. Required case: Producer conversation reused as reviewer is rejected; same allowed model alone is not rejected.

## adversarial: Adversarial counterexamples and defense

Recommendation: **adapt**. Source mechanism: Dynamic skeptic and PaperJury trial.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Challenge falsifiable claims, allow source/context expansion, preserve charitable alternatives and evidence-backed minority dissent.
Native mapping: Native independent agents then explicit critique stage.
Seed owner: critique method + findings schema. Dependency group: evidence.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evidence.py'`. Required case: Missing skeptic is unavailable; hostile wording or majority agreement cannot establish a defect. Downstream analysis must consume the admitted upstream artifact, not only run after it.

## recall: Dismissed-finding and consensus audit

Recommendation: **adapt**. Source mechanism: PaperJury recall audit and scheduled reviewer.

Evidence: [cookbook-index-coverage](cookbook-index-coverage.md), [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md).

Implementation: Revisit consequential dismissals and apparent consensus where the method requires; retain issue lineage and unresolved author work.
Native mapping: Fresh critique roles through either native provider.
Seed owner: review methods + issue records. Dependency group: evidence.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evidence.py'`. Required case: Empty recall votes cannot confirm a dismissal; baseline cannot advance after partial review.

## outcome: Outcome grading and bounded repair

Recommendation: **adapt**. Source mechanism: Outcome grader, evaluator optimizer and Codex repair loop.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Separate FAIL from ERROR/UNAVAILABLE/cap; require evidence for each criterion; repair concrete defects within admitted limits.
Native mapping: Native workers repair; protected evaluator/supervisor checks actual candidate.
Seed owner: check engine + review rubrics. Dependency group: evidence.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evidence.py'`. Required case: Malformed JSON, empty approved output or cap never becomes acceptance; style-only churn does not create endless repair.

## continuity: Long-horizon native continuity

Recommendation: **adopt**. Source mechanism: Later harness design, Codex long-task examples and SDK sessions.

Evidence: [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md).

Implementation: Retain useful native context across turns and compaction; revalidate attempt/profile on continuation; preserve candidate history.
Native mapping: Provider-native sessions and compaction, not mandatory fresh worker rounds.
Seed owner: adapters + continuation records. Dependency group: recovery.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`. Required case: Old receipt cannot certify changed assets; final candidate is not selected merely because latest.

## goals: Native goals with one continuation owner

Recommendation: **optional native method**. Source mechanism: Claude goal and Codex goals.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Choose native-goal or supervisor continuation ownership for an active stage; reconcile goal before competing repair; acceptance separate.
Native mapping: Claude evaluator must satisfy model policy; Codex native goal observed through admitted supported surface.
Seed owner: goal capability profile + supervisor arbitration. Dependency group: recovery.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`. Required case: Goal active/unknown plus supervisor retry cannot create concurrent turn; completed goal still needs checks.

## steering: Authenticated steering and human questions

Recommendation: **adopt**. Source mechanism: SDK interaction, human gate, cwc steering and native turns.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Durable trusted ingress and request identity; separate delivery/consumption/application; recheck barriers before execution-triggering replies.
Native mapping: Native permission/question/steering channels; Workflow stage change at reconciled boundary.
Seed owner: control boundary + adapters. Dependency group: recovery.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`. Required case: Forged human flag, canceled approval answer or stale queued input never grants current execution authority.

## recovery: Crash and replay reconciliation

Recommendation: **adapt**. Source mechanism: Workflow replay, LoopX recovery and durable sessions.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Persist intent/receipts, reconcile actual processes and external effects, preserve original lineage on evidence adoption.
Native mapping: Explicit native IDs; no newest-file/latest-session binding or blind resume.
Seed owner: SQLite state + artifact spool + adapters. Dependency group: recovery.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`. Required case: Crash after launch or saved sibling effect produces reconciliation, not duplicate writer or effect.

## workspace: Owned parallel work and integration

Recommendation: **adapt**. Source mechanism: Unlazy, parallel phases, native worktree recipes.

Evidence: [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md), [cookbook-codex-audit](cookbook-codex-audit.md).

Implementation: Assign owned workspaces/boundaries; preserve unrelated edits; one integrator validates combined candidate and full checks.
Native mapping: Native execution retains tools in admitted workspace.
Seed owner: workspace service + integration role. Dependency group: isolation.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_isolation.py'`. Required case: Disjoint-glob declaration alone cannot permit forbidden write; cleanup cannot erase unrelated work.

## capabilities: Effective native profile and authority

Recommendation: **adopt**. Source mechanism: SDK permission semantics, watched subagents and native schema evidence.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Resolve complete profile and distinguish desired/configured/observed; protect authoritative stores; admit only proven required controls.
Native mapping: No empty allowedTools assumption, hidden personal config or unsupported model fallback.
Seed owner: profile compiler + adapter readiness. Dependency group: isolation.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_isolation.py'`. Required case: Empty preapproval list still cannot be called no-tools; unknown hidden model cannot produce compliant receipt; pending human approval cannot block raw child/interrupt event observation.

## evidence: Artifact, criterion and claim binding

Recommendation: **adopt**. Source mechanism: cwc gate, claim verification, tool evidence and SSSF gates.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Actual artifact bytes, source scope, candidate/criteria/dependency identities and expected population; identity is not semantic truth.
Native mapping: Raw native observations plus provider-neutral evidence receipts.
Seed owner: artifact engine + evidence schemas. Dependency group: evidence.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evidence.py'`. Required case: Attempted Read error, unrelated screenshot, arbitrary path, same-length edit and omitted criterion cannot certify support.

## retrieval: Source acquisition and solution discovery

Recommendation: **adapt**. Source mechanism: Agentic search, discovery ledgers and research prompts.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Track per-provider fetch outcome, source read scope, relevance and claim support; retain contrary sources; papers/code/tools all eligible.
Native mapping: Native web/connectors and declared Consensus connection when relevant and available.
Seed owner: research skills + domain tool bindings. Dependency group: methods.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_methods.py'`. Required case: Failed fetch differs from no results; citation insertion cannot repair unsupported content.

## branches: Inquiry reopening and downstream invalidation

Recommendation: **adapt**. Source mechanism: Inquiry branch ledger and provenance graph.

Evidence: [cookbook-index-coverage](cookbook-index-coverage.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Give adopted branches reasons and reopen conditions; changing evidence marks dependent decisions/lessons stale by specific cause.
Native mapping: Native lead proposes branches within scope, supervisor records transitions.
Seed owner: inquiry records + dependency index. Dependency group: memory.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory.py'`. Required case: Resolve one stale cause without clearing another; reopened claim cannot reuse unsupported conclusion.

## tools: Precise tools and deterministic computation

Recommendation: **adapt**. Source mechanism: PTC, tool evaluation and effective-agents interfaces.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Use typed arguments, explicit errors/examples, native batching and code aggregation; preserve raw sources and complete error propagation.
Native mapping: Native shell/code tools, not mandatory extra API controller.
Seed owner: tool contracts + skill references. Dependency group: tools.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_tools.py'`. Required case: Units mismatch, dropped parallel result or empty evaluation population cannot produce a valid computed answer.

## tool_discovery: On-demand native tool discovery

Recommendation: **adapt**. Source mechanism: Tool search embedding/alternate notebooks and native discovery.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md).

Implementation: Small permission-filtered catalog with on-demand schemas; discovery and execution authorization separate.
Native mapping: Prefer real native tool/MCP discovery; embeddings only if measured need warrants.
Seed owner: capability catalog + native bindings. Dependency group: tools.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_tools.py'`. Required case: Unknown/disallowed/revoked tool cannot execute; empty lookup is not fabricated success.

## skills: Complete portable skill assets

Recommendation: **adopt**. Source mechanism: SDK skills, skills repository cookbook and Vercel discovery.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Ship canonical shared skill plus support files, digest/pin/license and native projections; validate collision and actual loading.
Native mapping: Claude shared-skill references; Codex native skill input/discovery, no personal-body paste.
Seed owner: seed/.agents/skills + managed asset manifest. Dependency group: distribution.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_distribution.py'`. Required case: Missing support file, same-name personal override or changed asset fails admission or freshness check.

## context: Context compaction and source access

Recommendation: **adapt**. Source mechanism: Session memory/compaction and lost-exception cost example.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Context packet summarizes progress with references and exceptions; preserves raw-source access, uncertainties and failed approaches.
Native mapping: Preserve native compaction and memory capabilities; Loam does not forge internal inclusion telemetry.
Seed owner: context compiler + catchup skill. Dependency group: memory.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory.py'`. Required case: Critical exception omitted from summary fails applicable context-quality evaluation. Re-fetch after tool-result clearing cannot replace historical evidence when the external source changed.

## memory: Scoped memory distinct from authority

Recommendation: **adapt**. Source mechanism: SDK memory, preference memory and research provenance.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Capture source-linked observations/lessons with applicability, correction and supersession; project state/rules remain separate.
Native mapping: Both providers consume shared records; native private memory is optional context, not portability dependency.
Seed owner: memory contracts + shared context tools. Dependency group: memory.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory.py'`. Required case: A remembered race contradicted by source stays unverified, not promoted; failed consolidation retains temporary candidates instead of promoting them. Stale preference cannot override current user decision; normalized root aliases and sibling-prefix paths cannot bypass memory protection.

## derived: Derived indexes and generated policy

Recommendation: **adapt with restricted authority**. Source mechanism: Knowledge graph, compiled moderation rules and provenance builders.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Graphs/retrieval indexes derived from source IDs; generated deterministic policy is a reviewed proposal needing coverage and semantic validation.
Native mapping: Native agents may propose/inspect; protected engine applies only admitted revisions.
Seed owner: derived-index interface + policy proposal schema. Dependency group: memory.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory.py'`. Required case: Empty compiled policy, lost source_doc, conflated homonym or hallucinated rule cannot become governing authority.

## prompts: Driver-specific prompt/role maintenance

Recommendation: **adapt**. Source mechanism: Prompt versioning/rollback, workflow iteration and official prompt audits.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Propose targeted change from failure + source; freeze profile, evaluate representative/held-out cases, retain rollback and remove obsolete scaffolding.
Native mapping: Preserve chosen driver/effort; update native projections explicitly.
Seed owner: managed role/method versions + project extensions. Dependency group: evaluation.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evaluation.py'`. Required case: Improvement on one field with regression on another fails promotion; user rule cannot be overwritten by learned advice.

## evaluation: Evaluate factory quality and reviewer calibration

Recommendation: **adopt**. Source mechanism: Building evals, tool evals, repair loops and evaluation saturation.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Use independent expectations, full case population, failure-category results and representative tasks; synthetic cases supplement real evidence.
Native mapping: Run comparable admitted profiles without changing model/effort to improve scores.
Seed owner: evaluation fixtures + experiment records. Dependency group: evaluation.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evaluation.py'`. Required case: Missing/failed case cannot disappear from denominator; feedback binds the exact displayed output/run; demo target-iteration gate is not evidence of autonomous convergence.

## accounting: Truthful cumulative resource accounting

Recommendation: **adapt**. Source mechanism: Native usage and session spend caps.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md).

Implementation: Retain raw scope/counters; handle resets and unknowns; aggregate only when inclusion semantics known; user controls bounds.
Native mapping: No model/effort downgrade or cap raising inferred from cookbook defaults.
Seed owner: supervisor reservations + accounting. Dependency group: recovery.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`. Required case: Resume/cancel/child usage neither resets allowance nor double counts cumulative counters. Truncated accounting pages or malformed amounts remain incomplete/unknown, not zero.

## operations: Event-driven maintenance and publication

Recommendation: **adapt**. Source mechanism: Issue-to-PR, scheduled reviewer and harness maintenance.

Evidence: [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-long-horizon-audit](cookbook-long-horizon-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Authorized triggers enter the same supervisor; success requires actual check/review evidence; publication has distinct action/receipt reconciliation.
Native mapping: Native workers can propose/repair; no notebook demo grants external authority.
Seed owner: scheduler trigger infrastructure + publication boundary. Dependency group: operations.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_operations.py'`. Required case: Partial scan cannot advance complete baseline; ambiguous publish receipt reconciles instead of duplicate send.

## domain: Domain-specific methods and optional backends

Recommendation: **project extension**. Source mechanism: RAG/multimodal, geography, scanners, Agents API and scientific review recipes.

Evidence: [cookbook-claude-sdk-audit](cookbook-claude-sdk-audit.md), [cookbook-claude-patterns-audit](cookbook-claude-patterns-audit.md), [cookbook-codex-audit](cookbook-codex-audit.md), [cookbook-index-coverage](cookbook-index-coverage.md).

Implementation: Ship generic method/tool extension contract; select domain assets and declared dependencies when needed; source-specific limitations retained.
Native mapping: Use native tools or separately admitted integration; no mandatory MongoDB/embedding/cloud-agent runtime.
Seed owner: project-owned bindings/extensions + managed interface. Dependency group: distribution.
Future check: `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_distribution.py'`. Required case: Unavailable required domain capability reports precise gap; optional absence cannot silently alter requested method.

