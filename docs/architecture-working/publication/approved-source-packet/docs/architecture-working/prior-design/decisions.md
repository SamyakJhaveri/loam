# Loam architecture decision record

Status: distribution, ownership, configuration, durable storage and record/transition direction accepted. Native adapter and memory implementation details remain under discussion. Evidence time 2026-09-14T00:12:37Z.
Examined main: `d627bb2755ad49865f798bcb095800ddd2ad1ced`.
No runtime edits, installs, automations, commits, pushes or deployment authorized in this phase.

## Settled user requirements

Verified source: current user request, handoff and comment-responses.md.

| ID | Requirement |
|---|---|
| U-SEED | Full factory/infrastructure in EVERY seed, independent of Loam checkout/personal setup. |
| U-NATIVE | Preserve native Claude/Codex strengths, comparable walk-away completion/recovery/steering. |
| U-MODELS | Astra driver; Astra/Sol/Terra only. Fable 5.1 driver; Fable 5.1/Opus 4.8 only. User controls effort/defaults/changes, including auxiliary paths. |
| U-ADAPT | Adapt prompts, skills, roles, hooks and workflows to selected drivers using current official guidance and observed failures; preserve intent, review changes, evaluate and retain rollback. |
| U-TEAM | Independent agents, cross-critique, lead synthesis and retained dissent for substantial inquiry. |
| U-PARTNER | Mechanisms and alternatives before peripheral questions; investigate facts; ask consequential unresolved decisions. |
| U-DISCOVERY | Papers/code/libraries/tools/APIs, Consensus preferred when available; inspect originals. |
| U-REFRAME | Surprise-me expansion/analogy/blind spots; quality policy overrides cheap/solo defaults. |
| U-EVIDENCE | Small question/method/evidence/conclusion record; domain-specific methods. |
| U-MEMORY | Source-linked memory, applicability, rules distinct from lessons, empty stores, both harnesses. |
| U-REBUILD | Existing Loam/seed components may be proposed for replacement, removal or rebuilding. Runtime edits remain deferred. |
| U-SCOPE | Read-only inspection and design documents only; preserve uncommitted work; report proposals are not approvals. |
| U-RECORD | Living design in original review folder, separate from report. Destination blocked by session write policy; temporary fallback documented. |

## Accepted design direction

Verified authority: user response, "i like you recommendations uptill now, lets keep them and continue", quoting the distribution ownership question. This accepts the direction presented in that distribution discussion. It does not select unresolved native mechanisms, ticket authority, state backend or exact role efforts. Runtime work remains deferred.

| ID | Accepted direction | Scope |
|---|---|---|
| D-DISTRIBUTE | Canonical reusable source in seed, used by Loam's development launcher and shipped in every generated project | Exact internal filenames and implementation language remain design details |
| D-OWNERSHIP | Managed factory assets separate from project configuration, extensions, decisions and local operational state | Normal customization uses configuration/extensions; direct engine edits form an explicit local fork |
| D-UPDATE | Reviewed updates preserve project-owned content, expose effective behavior changes and keep active-run inputs stable or report incompatibility | Exact update coordinator and native isolation mechanisms still need design/probes |
| D-REPLACE | Replace hidden personal-cache dependencies, prose-parsed policy and checkout-dependent attach behavior; separate rendering/update from external activation | Migration design required for existing projects; no runtime edits yet |

Verified additional authority: the user endorsed the configuration ideas and asked to proceed, explicitly confirming memory and loop engineering remain in scope. "lop engineering" is interpreted as factory-loop engineering; memory-driven improvement of the workflow will also be covered.

| ID | Additional accepted direction | Scope |
|---|---|---|
| D-CONFIG | Shared project contract with field-specific authority rules, explicit native settings and user-controlled model/effort across roles | Exact schema, native mechanisms and role effort values remain open |
| D-OBSERVE | Admitted profile, desired launch and native observation receipt are separate records | Native controllability/observability must be verified; no enforcement claim from generated config alone |
| D-NATIVE | Preserve ordinary native interaction and native capabilities within supervised jobs; required inheritance is explicit | Exact worker lifecycle and settings isolation are still proposed |

## Accepted storage and recovery direction

Verified authority: the user explicitly chose “SQLite plus artifact files” and agreed with all recommendations in that storage discussion. This accepts its architectural direction and recovery boundaries. Runtime-specific verification is still outstanding. “Do not worry about the runtime” is interpreted as continuing the design without blocking on runtime selection; it does not override the earlier explicit implementation deferral.

| ID | Accepted direction | Scope |
|---|---|---|
| D-STORE | SQLite for operational state and related audit events; ordinary files for evidence and project-owned knowledge | Replace independent status/ledger control writes with one transaction authority. Exact schema and implementation remain under design. |
| D-INSTANCE | One supervising owner per active local instance; linked worktrees share it; separate clones/hosts have distinct instances | Remote control routes to an owning instance. No shared live database over a network filesystem. Exact registration/transport mechanisms remain under design. |
| D-DURABLE | Publish durable protected artifacts before committing their evidence references; reconcile unknown launches and external effects | SQLite is not process isolation or exactly-once external execution. Fresh owner incarnation, explicit recovery adoption, queued/dispatching distinction and truthful stop acknowledgment are required. |
| D-STATE-UPDATE | Ship state machinery/migrations in every seed, initialize empty local stores, preserve project-owned records, and migrate under quiescence with backup and compatibility checks | No live database/history in seed. Runtime durability settings and minimum supported environments still require later validation. |

## Accepted records and transition direction

Verified authority: the user's latest response agrees with the records/transition design and asks to proceed, while emphasizing grounding in original resources and engineering judgment for research engineering and ideas. This accepts the operational direction, not a final SQL schema or a runtime implementation authorization.

| ID | Accepted direction | Scope |
|---|---|---|
| D-WORK-REVISION | Runs remain bound to immutable request/profile revisions; requirement changes create linked successor runs | Native session identity stays separate; exact tables and transport mappings remain implementation design. |
| D-ACCOUNTING | Retries, descendants and successor runs share the effort's accounting scope unless explicitly adjusted | Preserve unknown usage and unresolved reservations; no silent model/effort change or renewed limits. |
| D-STEERING | Pause, cancel, revise and resume have distinct authority semantics; named requests/barriers serialize with dispatch and acceptance | Capture/account/reconcile reality after cancellation; cancelled authority does not revive. Native interruption mechanisms remain to verify. |
| D-CURRENT-EVIDENCE | Acceptance binds the current run, candidate, criteria and required-obligation population; findings require explicit dispositions | Queue-time ownership, recovery adoption and scoped invalidation are part of the contract. Runtime guarantees require later validation. |
| D-INQUIRY-OUTCOME | Inquiry method execution, source support and conclusion are distinct; a valid inquiry may be refuted, mixed or inconclusive | Research, deliberation, discovery and source-linked memory are first-class factory work. No mandatory conversion to implementation tickets. |

## Remaining recommendations, not decisions

| ID | Recommendation | Rationale/evidence | Alternative |
|---|---|---|---|
| P-OWN | Native lead owns thought/tool loop; supervisor owns state/recovery/acceptance | C3-C5 preserve useful existing split | No new general agent framework justified |
| P-RECORD | Local files authoritative, GitHub projection | Portability, offline work, source-linked decisions | Existing GitHub authority with pinned snapshots |
| P-PROFILES | Complete Claude-only/Codex-only/combined profiles | C5 current dual-account coupling | Explicitly require both, if user chooses |
| P-NATIVE-TRANSPORT | Prefer native bidirectional control when it preserves required capabilities; expose narrower process modes explicitly | Adapter evidence/design step; common semantics do not mean identical provider APIs | Exact native transport selection still proposed |
| P-MEM | Source-linked files and small index; native memory local aid | U-MEMORY, C7; no measured service need | Database/search service after demonstrated retrieval gaps |
| P-ADAPT | Bounded native profile audit and reviewable, evaluated changes with rollback | U-ADAPT, handoff and annotation correction | No automatic self-rewriting setup |
| P-AUTH | Frozen admitted profile; no incidental global account mutation | C4 helper changes unrelated future sessions | Coordinated shared auth service if later needed |

## Pending question

Q-RECORD: project files authoritative with GitHub projection, or GitHub authoritative with pinned local snapshots? Asked asynchronously. No answer recorded yet. P-RECORD remains a recommendation.

## Alternatives rejected in the proposal

- Optional factory or executable-only copying: violates complete distribution.
- Hand-maintained runtime copies: drift and duplicate authority.
- Required personal-cache resolution: hidden setup and mutable run instructions.
- Model summary/retry cap as acceptance: insufficient evidence.
- Every inquiry as a multi-ticket build: uncertainty does not determine size or outcome.
- Universal experiment/statistics rules: project methods differ.
- Automatic lesson-to-rule promotion: violates user authority.
- Mandatory experimental live-steering service: not needed for initial staged contract.
- Global account changes as incidental retry: affects other projects.

These are proposed design rejections, not code deletions.

## Cross-critique and retained disagreement

Verified: independent packaging, supervisor and research/memory agents inspected bounded domains. Emerging proposals were exchanged for critique. The lead integrated these corrections:

- Protecting state requires an evidence write path: attempt output then validated promotion.
- Local authority changes current issue-based policy: keep a pending decision, no dual editable authority.
- Research completion cannot require every non-guard check to fail at baseline: separate method/evidence criteria.
- Outside-checkout paths and hashes are not enforcement: require native/host protection probes.
- Lock expiry does not prove old process death: reconcile before replacement; do not assume multi-host safety.
- Single-harness profiles are untested targets; different-provider review is not automatically independent evidence.
- Packaging agent preferred conventional seed/bin; lead proposes seed/.loam/factory internals plus bin/factory entry point. Both satisfy canonical source. Exact path remains reversible and unapproved.
- At that earlier critique, file journal versus transactional store remained open. The user has since selected SQLite plus artifact files; crash fixtures validate the selected design.
- Scheduler correction: template names Loam, but installation substitutes current checkout. The real cross-project issue is broad timer replacement.

Fresh-context document review also found and corrected: evaluation subprocesses must not inherit supervisor authority; setup adaptation needs its own explicit requirement and evaluation/rollback contract.

Next: develop worker lifecycle and supervisor loop under the accepted distribution and configuration boundaries. Q-RECORD stays pending and does not block independent design investigation. Then develop the complete example and runnable acceptance checks before runtime work.

## Complete-folder grounding corrections

Verified: the full reading and code audit are recorded in [grounding-record.md](grounding-record.md). At that grounding checkpoint P-PACK remained provisional: repository policy permits an equality-verified mirror, and the report allows declared versioned dependencies. Update preservation is a target, not a demonstrated current capability. No earlier recommendation was approved merely by the user asking to continue.

## Distribution discussion opened

See [distribution-design.md](distribution-design.md). At opening, P-PACK remained proposed; it is now accepted as D-DISTRIBUTE above. The direction is canonical seed source with managed runtime, project-owned configuration/assets and explicit local forks. New defaults require an effective-profile comparison; active runs never silently adopt updated live assets. The user explicitly permits rebuilding or removing existing components when justified.

## Configuration discussion opened

See [configuration-design.md](configuration-design.md). Proposed: a shared semantic job profile, field-specific authority rules and native adapters that prepare desired launch inputs and separately report observable native settings. No generic deep merge, silent environment model override or unverified claim of effective native enforcement.

## Loop and memory coverage

See [loop-design.md](loop-design.md) for the next proposed lifecycle and concrete export-ticket example. Later required discussions: durable storage/recovery/steering implementation; memory schemas, capture, retrieval, applicability and invalidation; research/team/discovery routing; evaluated changes to prompts, roles, workflows and checks. No memory backend or runtime language is selected by this scope confirmation.

## Original-source grounding update

Verified: originals from the supplied outputs and repo research INDEX were distributed across independent source readers, then cross-critiqued. See [reference-reading.md](reference-reading.md) for actual coverage and inaccessible material; [source-informed-design.md](source-informed-design.md) maps concrete source mechanisms to design changes. Historical rejected/no-code classifications are not binding. Accepted distribution and configuration direction is retained.

New proposals, not accepted decisions: explicit native replay/goal/team clauses in loop-design.md; evidence-population validation before aggregation; scoped discovery triggers; source-linked memory with correction/supersession; evaluated driver adaptation; a backend comparison driven by crash consistency rather than minimal file count. Neither a scanner product nor an external research suite has been selected as a mandatory dependency.

## Durable state discussion opened

At the opening of the storage discussion, the user had approved proceeding without selecting a database. The subsequent explicit SQLite choice is recorded as D-STORE through D-STATE-UPDATE above. Runtime implementation remains deferred. See [state-design.md](state-design.md): recommended SQLite control/events, ordinary artifacts and project records, one supervising owner per active local instance, explicit artifact publication and recovery. A separate machine can have its own instance; shared multi-host live coordination is a consequential topology choice still open. Runtime language, minimum versions and concrete native launch mechanisms remain unselected.

## Records and transitions discussion opened

See [records-and-transitions.md](records-and-transitions.md). Proposed: immutable work revisions; runs bound to revisions; attempts and native sessions separate; requirement changes create successor runs without resetting budget authority; pause, cancel and revise have distinct meanings; acceptance uses complete current evidence and ordered steering. These detailed semantics were initially proposals separate from storage approval; the user has now accepted their direction as recorded above.

## Native adapter discussion opened

The current step develops [native-adapter-design.md](native-adapter-design.md), grounded in current Loam code, original native documentation and selected research/harness resources. Provider reports preserve verified facts, read scope and untested assumptions. Engineering choices are labeled recommendations. Scope remains research engineering and research ideas as well as implementation, with the full factory in every seed.

Proposed P-NATIVE-TRANSPORT: owned Codex app-server over stdio and Claude official TypeScript Agent SDK open-input query for full steered execution, with narrower native process profiles explicitly admitted where sufficient. This is a new recommendation, not yet a user-selected transport or runtime language. Admission depends on verified configuration/auth boundaries, exact supported protocol, model policy, request correlation and descendant/queue reconciliation. See provider evidence reports and native-adapter-design.md.

## Cookbook audit integration

Verified authority: the user likes the existing recommendations and explicitly requests exhaustive identification and implementation mapping of relevant INDEX and Claude/OpenAI cookbook practices before moving to the next design step. This authorizes source investigation, critique and finalization of this design layer. It does not authorize runtime implementation, installations, automations or every source's features/defaults.

Reviewed recommendation P-WORK-METHODS: ship the shared method/role/receipt infrastructure for inquiry, planning, experiments, implementation, review, advisory consultation, dynamic delegation, discovery and memory in every seed. Invoke methods for their actual purpose; native capability requirements stay explicit. Do not require a complete team ritual on every task.

Reviewed recommendation P-CONTINUATION-OWNER: supervisor continuation is the default between stages. A selected and admissible native goal may own continued turns inside a stage. Reconcile that ownership before competing repair, cancellation or successor execution. Native goal status is not acceptance.

Reviewed recommendation P-CONSULT-REVIEW: native advisor consultation, adversarial challenge and independent acceptance review are distinct obligations. An occurrence-only consultation can permit redacted advice with identity evidence; substantive advice and independent review need their own evidence. Required independent context and complete populations do not imply mandatory different models.

Reviewed recommendation P-DYNAMIC-ADMISSION: required child work obtains a durable admitted obligation/plan receipt before dispatch, with one dispatcher and actual native identity binding. Exploratory work can supply evidence through explicit lineage-preserving adoption, never retrospective permission.

These recommendations and the remaining prototype requirements are in cookbook-integration-design.md and cookbook-practice-registry.md. Canonical engine placement remains seed/.loam/factory with a generated entry point; source-reader suggestions for seed/bin/factory.d are alternatives, not additional runtime copies. Fixtures ship inside the managed engine. Domain backends, a graph database, cloud Agents APIs and evaluator products are not selected as mandatory dependencies.

P-NATIVE-TRANSPORT refinement after original SDK source: official Python Codex SDK uses app-server, so client and protocol are separate choices. Prefer a narrow direct client for the full durable request/event contract given the inspected SDK approval-reader and high-level observation limits. Keep the official SDK as a replaceable alternative subject to the same conformance tests. Retain Claude open-input TypeScript SDK as the primary bridge. Remote Agents API/exec-server integrations are named optional alternatives, not a new mandatory seed dependency. See cookbook-codex-audit.md for exact source pin and limits.
