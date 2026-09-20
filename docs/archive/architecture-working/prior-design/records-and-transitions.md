# Work records, execution transitions and later steering

Status: record/transition direction accepted by the user, following accepted SQLite-plus-artifacts storage and local-instance ownership. Exact schema and native mapping continue in design. No runtime implementation. The user's latest acceptance is recorded in decisions.md. This step defines the operational contract independently of the runtime language.

Critical point: a stale attempt, superseded requirement or duplicated result cannot acquire current acceptance authority.

## Design recommendation

Keep a run bound to one immutable work revision. A changed requirement creates a successor revision and run; an implementation repair or safely repeated failed check creates a new attempt within the existing run. Native session identity is independent: the same supported native conversation may continue across attempts after reconciliation. Preserve the accounting scope across all of these operations unless the user explicitly changes its limits.

Use a small command/transaction layer as the only operational-state mutation interface. Native workers and checkers produce observations and artifacts. The supervisor validates those inputs and applies typed transitions. Status displays and memory read projections; they cannot infer accepted state from file presence or a final message. Native tools and subagents remain under the native lead's control within admitted scope.

## Record contract

These are logical records and proposed fields, not a completed SQL schema or provider API. Split tables only when needed for constraints, cardinality or transactions. Immutable payloads live in the artifact archive with verified references; small indexed state and relationships live in SQLite.

| Record | Required meaning and proposed fields | Mutation/authority |
|---|---|---|
| Work | Stable work_id, kind, source reference, current admitted revision, lineage/dependencies | Supervisor validates source authority. A finding may propose work without admitting execution. Local-file versus GitHub authoring authority remains separately open. |
| Work revision | work_revision_id, work_id, predecessor, original request/source digest, objective/scope, required outcomes, method/criteria manifest, authority record | Immutable after admission. Concurrent revisions of the same predecessor require reconciliation; never silent last-writer-wins. Source edits do not mutate the snapshot. |
| Execution profile | profile_revision_id, resolved role/model/effort policy and origins, permissions, capability requirements, managed/project asset identities | Immutable admitted input. Desired launch and observed configuration remain separate records. No worker-authored setting can change this profile. |
| Accounting scope | accounting_scope_id, granted limits and time semantics, adjustments, reservations, observed usage, unknown amounts | Shared across retries/successor runs. Additional authority is an explicit adjustment event. Unknown cost/usage is not zero. |
| Run | run_id, work_revision_id, profile_revision_id, accounting_scope_id, predecessor_run_id, disposition, current plan revision and required-population manifest, acceptance projection, state revision | Bound to immutable admitted inputs. A new profile or objective requiring readmission gets a successor run. Operational disposition does not establish physical process termination. |
| Stage obligation | stage_id, run_id, plan revision, kind, exact input identities, required outputs/checks/reviewer assignments, dependencies, blocking status | A bounded obligation such as inquiry, implementation, checking or review. It is not each native tool call. Plan changes are versioned and cannot remove required outcomes without authority. |
| Attempt | attempt_id, stage_id, input/profile identities, producer owner incarnation, generation, launch intent, execution observations, native session/job references, reason for ending | One admitted invocation. New invocation means new attempt, including native resume. Result arrival, process end, output validation and stage satisfaction are separate facts. |
| Action intent | action_id, attempt/run scope, effect identity, payload digest, queued/dispatching/observed state, authorization reference, reconciliation status | Includes worker dispatch and publication. Retrying the same intended external effect retains its effect identity; a new ID is not a way around unresolved prior execution. |
| Artifact/result | artifact_id/content digest, source/read scope, result_id, original attempt/producer, candidate/criteria identities, raw outcome, observed exit status | Immutable provenance after capture. Producer claims are not accepted receipts. Raw observation remains available after invalidation. |
| Validation receipt | receipt_id, original result refs, validator/method identity, input/candidate/criteria identities, complete coverage, valid outcome, validation/adoption event | Written by the trusted validation path. Recovery adds a current-authority adoption record without changing the original producer. Duplicate evidence cannot settle twice. |
| Finding | finding_id, scope/criterion, origin candidate and evidence, severity, blocking classification, disposition, resolution evidence and authority | A finding remains an obligation until resolved, dismissed with authority or established inapplicable. Changing candidates does not silently delete it. |
| Steering request | request_id, authenticated actor/authority reference, target, expected revision, operation, payload digest, requested timing, durable sequence, acknowledgment, individual barrier identity/scope and application result | Received through a trusted user/control channel. Text inside a source or worker report cannot impersonate user steering. Duplicate ID/same payload replays its result; different payload conflicts. |
| Acceptance | acceptance_id, run_id, exact work/profile/candidate/criteria identities, current plan/required-population manifest revision, required receipt manifest, finding dispositions, policy evidence, authorizing event | Immutable historical decision. Current validity is a projection that can show supersession or later evidence loss; history is not erased. Publication has its own authorization and receipt. |
| Audit event | event_id, local ordered sequence, owner incarnation, actor, command/request ID, before/after revisions, related record identities | Added in the same transaction as the state change. Sequence orders events within that store history; it is not a global wall clock or an identity safe to reuse after restore. |

Recommendation: native descendant/job observations live under their parent attempt with stable native identity where available and explicit unknown where absent. Do not invent a duplicate local task for every native tool call. Every descendant that can mutate the candidate or perform a consequential external action must be covered by lifecycle reconciliation. If a required host surface cannot expose or control that boundary, admission reports the unsupported guarantee.

## State dimensions

Use separate dimensions rather than one overloaded status:

| Dimension | Proposed states or outcomes | Important distinction |
|---|---|---|
| Run disposition | active, waiting, paused, blocked, accepted, incomplete, cancelled, superseded | This controls future authority. Cancelled/superseded can coexist with unresolved physical execution. The user-facing status must show both. |
| Stage obligation | pending, eligible, executing, awaiting_validation, satisfied, unmet, superseded | Satisfied means its declared valid receipts establish its required outcome. An unmet stage can produce a new attempt under retry/repair policy. |
| Attempt execution | queued, dispatching, running, reconciling, quiescent | Unknown launch/liveness/termination is explicit metadata within reconciling. Never report quiescent only because a lease expired. |
| Attempt end reason | completed, failed, interrupted, denied, capped, unknown | A process completing does not satisfy an obligation. Unknown does not prove an ended process. |
| Check result | pass, fail, error, not_run | Pass/fail requires a valid check execution. Error/not_run supplies no successful functional result. Baseline expectations separately specify which valid result is expected. |
| Inquiry conclusion | supported, refuted, mixed, inconclusive | Separate from method execution and evidence coverage. A crashed experiment is not a refutation. |
| Publication | not_requested, queued, dispatching, confirmed, failed, unknown, cancelled_before_dispatch | Published, accepted and physically stopped are different facts. A requested draft can be published while incomplete only with the corresponding authority. |

Recommendation: retryability is a policy decision informed by a typed failure, not encoded by assuming every error should restart the worker. A check process error can retry that stage. A valid behavioral failure can request an implementation repair. A missing reviewer stays unmet. A repeated unchanged finding can trigger diagnosis or escalation, not automatic dismissal.

## Shared transaction preconditions

Every command checks the registered instance, current owner incarnation and relevant attempt generation, expected state/revision, actor authority, and current pause/stop/steering barriers. Validate referential identities and complete schemas before using a result. Require content identity for referenced immutable inputs. Commit the state change, event, and any receipt/accounting settlement together. Reserve necessary capacity before dispatch; keep uncertain reservations until reconciled.

Recommendation: do not hold a database transaction while running a model, test, file copy or remote action. Artifact publication follows state-design.md: durable protected file first, database reference/receipt second. The external effect follows the queued-intent/dispatch-authorization protocol, with explicit uncertainty across the gap. A staging file or queued intent never establishes completion.

Recommendation: distinguish producer authority from ingester authority. A superseded producer cannot request current-state mutation. The current supervisor may still capture its raw output, record actual usage and validate whether old evidence is useful. Adoption requires a fresh validation event with current authority and original provenance. Same result identity/same content is a replay; same identity/different content is a conflict. Native event deduplication uses provider event identity or a durable stream position, not content alone: two legitimate identical events must not collapse.

## Transaction and transition table

Command names below are proposed Loam domain operations, not native tool names.

| Command/event | Required condition | Atomic recorded change | External/next action |
|---|---|---|---|
| Admit work | Authoritative revision/profile/criteria complete; dependency and capability requirements met | Create immutable revision/run/plan obligations and accounting references; event | Prepare first eligible stage |
| Queue attempt | Current eligible obligation; no affected steering/pause/cancel barrier; budget/capacity policy permits | Claim the stage/assignment invocation slot and mutable workspace; create attempt, queued action intent and necessary reservations | No launch yet |
| Authorize dispatch | Recheck current owner/revision/authority/barriers and reservation | Change queued intent to dispatching with dispatch-authority event | Adapter may cross external boundary; missing acknowledgment becomes uncertain |
| Observe launch/job | Observation matches admitted action and native identity | Add process/session/job evidence and execution state | Observe activity or reconcile discrepancy |
| Capture/adopt result | Durable artifact; known attempt lineage; validated producer/result identity | Register original result and current validation/adoption, settle attributable usage once | Keep current obligation pending until all required coverage/conditions hold |
| Satisfy stage | Required results complete, valid and applicable; writers reconciled; criteria expectations met | Record satisfaction manifest and enable dependent obligations | Queue next eligible work under current barriers |
| Record unmet stage | Valid failure, missing/invalid evidence or unresolved findings | Persist typed reason and findings; do not mark satisfied | Retry evaluation, request repair, wait or block according to admitted policy |
| Repair candidate | Valid unmet behavior with repair authority and remaining bounds | Add repair attempt/stage dependencies; bind subsequent evaluation to new candidate; retain finding obligations | Native worker investigates and repairs; required checks/reviews re-evaluate |
| Receive steering | Trusted request with valid target/expected revision | Persist request and ordering; install affected authority/acceptance barrier before semantic classification | Classify effect, interrupt where required, or ask only the consequential missing question |
| Apply revision | Authorized replacement inputs; current predecessor still matches; affected actions classified | Add immutable successor revision and run; mark predecessor superseded; carry accounting scope and finding lineage | Reconcile old writers before any conflicting successor dispatch |
| Accept | Exact current run/plan/required-population manifest; every required obligation satisfied or authorized disposition; complete applicable receipts; findings resolved; required policy evidence established; candidate immutable; no affected barrier or unresolved writer | Create acceptance manifest and update run projection with event | Prepare authorized handoff; publication is separate |
| Queue/dispatch publication | Target artifact/revision and destination authority valid; no barrier; prior effect resolved | Persist operation intent, then use same dispatch authorization transaction | Publish/read back using native external integration; unknown remains unknown |
| Invalidate evidence or applicability | Verified evidence loss/corruption, material correction or policy noncompliance with identified affected support relations | Retain historical records; mark dependent current satisfaction/certification unusable; add scoped barriers and revalidation obligations | Prevent affected dispatch/acceptance/publication; policy violation also requests interruption/reconciliation under loop-design.md; unrelated work continues |
| Resolve named barrier | Identified steering request(s), expected work/state revision and valid classification/resume/revision authority | Resolve only those barrier identities and record the reason; recompute remaining effective barriers | Newer or unrelated cancellation/revision/pause remains effective |
| Recover ownership | Exclusive instance ownership acquired with fresh incarnation; schema compatible | Record recovery mode and known unfinished action inventory | Reconcile before new conflicting authority; preserve native identities and historical result producers |

Recommendation: queueing atomically consumes an identified invocation slot and claims any mutable workspace before external dispatch is possible. A second queue request cannot create another writer for that slot/workspace. Parallel work needs distinct assignment identities and separate or explicitly compatible access scopes. Known-undispatched cancellation can release its claim transactionally; once dispatch may have happened, release requires reconciliation. A timeout alone cannot release a possibly live writer's claim.

Recommendation: bind acceptance to the exact run and required-population manifest revision, not just candidate and criteria. Any admitted addition of required work changes that manifest. The acceptance transaction rechecks the current manifest and every required obligation, so a newly required reviewer cannot be omitted by a previously complete result list.

Recommendation: stage scheduling is a dependency graph, meaning work waits for specified earlier obligations. Native workers may choose their reasoning path and internal delegation. Required coverage and authority determine boundaries. A plan revision may add independent research or repair work without human permission when already authorized. It cannot silently replace acceptance criteria or declare required work optional. Dynamic discovered obligations receive identities before aggregation; no filtering missing results out of the expected population.

## Pause, cancel, revise and ordinary conversation

Recommendation: a user does not have to write a ticket to think with the native lead. Ordinary discussion stays native. Once it changes an admitted job, the integration records the relevant steering request and its source message identity. The control interface authenticates provenance; the model may propose a classification but cannot manufacture user authority.

| User intent | Proposed behavior |
|---|---|
| Pause / plain stop | Persist a pause barrier immediately: no new affected dispatch, acceptance or publication. Request interruption of active work by default; preserve evidence/accounting/reconciliation. Display pause requested plus unresolved active work until stopped/safely suspended is observed. |
| Resume | Same revision/run if still compatible and merely paused; reconcile existing jobs, preserve budgets and create new attempts for new invocations. Never silently resume a cancelled or superseded run. |
| Cancel / abandon this effort | Revoke targeted run's future execution and acceptance authority permanently; request interruption/reconcile. Retain candidate, results and usage. Later authorized work uses a successor run, not reversal of the cancelled disposition. |
| Change requirement, method or allowed execution profile | Hold affected dispatch/acceptance while admitted effect is established. Create successor inputs/run, preserve the predecessor and accounting scope. Old evidence is context until its applicability is explicitly evaluated. |
| Add information without changing scope | Preserve as a source-linked note with target revision. If it could invalidate a criterion or method, retain the barrier until classification. A source citation cannot automatically change policy. |
| Answer an outstanding question | Bind answer to the specific waiting request and expected revision; stale answers remain notes or require reconciliation, never silently apply to unrelated current work. |

Recommendation: each steering request owns an individually identified barrier. Pause, classification, revision application and resume resolve only the named barriers under an expected revision. Never clear all paused/steering flags as a convenience. A resume racing with a newer requirement change leaves the new change's barrier intact. Classifying one message as informational does not remove another request's pause or cancellation. An explicit resume names the applicable pause requests; cancellation remains terminal for that run.

Recommendation: user steering applies to its target scope. Independent work may continue where ownership and dependencies show it is unaffected. If a message's impact is ambiguous, hold the affected run's new dispatch and acceptance while classifying it. Do not globally stop every project because one task needs a decision.

The dispatch-authorization transaction determines the race. A pause/cancel/revision ordered before it prevents queued work from launching. Ordered after it, the action may already be in flight and is interrupted/reconciled. A stop acknowledgment states the persisted barrier and unresolved actions, not “nothing more can happen.” Evidence capture and usage settlement remain allowed after stop/cancel because they record reality rather than grant new execution. Publication follows the same rule.

Recommendation: evidence invalidation follows recorded support dependencies, with any uncertain consequential dependency held for assessment. Missing/corrupt evidence and materially corrected claims make affected current receipts/stage satisfaction unusable until revalidated. Preserve immutable historical receipts and acceptance. Prevent affected queued dispatch and publication immediately; known model-policy violations additionally prohibit continuation and request interruption/reconciliation as specified in loop-design.md. New source content does not by itself falsify a valid old snapshot, but its applicability to current work must be reassessed when material. Unrelated evidence and work are not invalidated globally.

Recommendation: do not rewrite historical acceptance after a later correction. Record the successor revision and whether the old result is now superseded or withdrawn from current use. Later evidence loss or policy discovery gets its own event and affects current certification. A previously performed external action remains a fact to reconcile, not something a database update undoes.

## Budgets and time

Recommendation: every descendant, retry and successor charges the same accounting scope for the effort unless an authorized adjustment says otherwise. Link reservations to action/attempt identities and usage observations to their origin. Do not sum overlapping provider parent/child totals twice; retain their aggregation provenance. Unknown usage/cost remains unknown. No cap claim may rely on treating it as zero or assuming an external provider call can be exactly bounded without supporting controls.

Recommendation: distinguish elapsed deadline, active execution allowance and observed model/resource usage in the policy. An elapsed deadline continues while paused unless explicitly adjusted. An active-time allowance counts its defined execution intervals and carries them across restarts. This design does not invent values or alter the user's selected model/effort. Limits that cannot be enforced with available host evidence are reported as such before admitting a profile that requires them.

## Evidence and persistent review obligations

Recommendation: bind the check manifest to exact commands/method, criteria and declared dependent scripts/fixtures/configuration, not only a display name. Bind its result to the candidate and observation environment. Required reviewers have explicit assignment identities and expected coverage. One passing reviewer cannot cover another missing assignment. Invalid/incomplete review is an evaluation error, not a blocker-free report.

A blocking finding has its own identity and closure rule. A new candidate must carry it forward for resolution assessment. Valid dispositions are fixed with evidence, dismissed by the configured authority with a reason, or no longer applicable with supporting scope evidence. An upstream requirement genuinely removed by authorized revision can make its finding inapplicable. Merely renaming a stage or exceeding a retry cap cannot. Prior accepted findings are not evidence of failure in a new candidate without checking applicability.

Recommendation for the first implementation: on changed candidate or criteria, obtain fresh required evaluation receipts. Permit reusing source observations and unchanged artifacts only through an explicit applicability/adoption record. Optimizing cross-revision check reuse is later work; copying an old PASS into a new revision is not the initial rule. Recovery of the same exact candidate/check attempt is distinct and may adopt a complete original result after validation.

## Research, discovery and memory

The same record model supports inquiries. A discovery stage can produce source-linked findings and proposed work. A research stage records question, admitted method, evidence scope, observations, contradictions and conclusion. Team assignments have explicit expected reports and source access limits; preserve independent reports before critique. Evaluation validates the method's required coverage and source support, not a paper-shaped output or agreement count.

A completed inquiry may be refuted, mixed or inconclusive when the admitted method permits that result. Required collection failure means incomplete execution, not a negative result. Optional unavailable sources stay visible without necessarily blocking a method that does not require them. A methodological substitution is recorded and checked against existing authority; changing the agreed method requires revision rather than retroactive relabeling.

Memory capture can follow a validated stage and retain failed approaches too. Lessons cite source/result/decision identities and their applicability. Indexing or consolidation is a separate maintenance obligation unless explicitly required for the current deliverable. Its failure cannot erase evidence or fabricate acceptance. A proposed factory improvement becomes a new work item with its own admitted criteria; memory does not directly edit the shared engine or user-owned policy. All generic record, research, steering and memory machinery ships in every seed.

## Complete illustrative trace: an interrupted export correction

This is a design example, not work executed in the repository. Symbolic IDs are illustrative.

1. A generated project initializes its own instance and empty store. Its shipped factory can operate without the Loam development checkout. The owner asks for reliable empty exports.
2. An inquiry compares deriving columns from returned rows against the application's explicit schema. Independent source/code reports and critique produce decision D. The accepted behavior becomes work W, revision A, with checks and the approved native profile. Run RA uses accounting scope BUDGET.
3. Baseline receipts show that the new empty-export behavior is absent and standing integrity checks pass. Implementation attempt IA produces candidate CA. Checking attempt QA starts with frozen inputs.
4. The owner clarifies that column order must follow the saved project schema. Steering S installs a barrier. Old output can be captured, but it cannot accept revised work. Revision B and successor run RB preserve RA, decision lineage and accounting scope BUDGET. Prior reservations remain until reconciled.
5. RA is superseded. Its native worker/check descendants are reconciled before conflicting work starts. A late QA receipt remains scoped to revision A and CA. It is retained, and actual usage is charged once; it does not satisfy revision B's checks.
6. RB implements candidate CB and checks its new criteria. The complete check artifact is durably published, but the supervisor crashes before saving the receipt. A new owner acquires a fresh incarnation, reconciles the attempt, adopts the exact artifact through a new validation event and settles the result once.
7. Required review finds that an optional column was dropped. A repair produces candidate CC. The finding carries forward until fresh evidence shows its close criterion satisfied. A malformed second report remains unmet; it cannot disappear from the expected assignments.
8. The owner pauses while final review completes. Loam saves the report and usage but does not accept or publish while paused. Resume validates the same admitted inputs and remaining authority, then accepts CC when all required receipts and findings are complete. Any authorized publication has its own operation identity and receipt.
9. A scoped lesson cites D, the revised requirement, the accepted candidate and regression evidence. Native context delivery is separately observed as described in memory-design.md. A future project-schema change makes the lesson subject to revalidation, not an unconditional export rule.

## Existing components, proposed changes and acceptance interfaces

Verified: current bin/factory has frozen input bundles, native calls, check output and reviewer artifacts. Source reads this step show run_review treats a later blocking review as backlog (1005-1008), run_codex_review maps malformed output to zero blockers (1031-1035), and main_loop uses FAIL text and reaches open_pr after the grader cap (1137-1151). These are source-inspection findings, not fresh reproductions.

The following are proposed future test commands. They are not implemented or run here.

| Proposed change | Existing piece and necessary replacement | Dependency | Runnable acceptance interface |
|---|---|---|---|
| Work/run/attempt records | Existing frozen inputs and round files; replace filename-inferred progress and revision-dependent fresh budgets | Accepted store, input manifests, instance binding | python3 -m unittest discover -s bin/tests -p test_factory_records.py : immutable bindings, revision conflict, successor lineage, unchanged accounting scope, competing queued invocation/workspace claims |
| Typed command transitions | Existing main_loop and process-local flags; replace with checked store commands and persistent obligations | Record schemas, authority/owner checks | python3 -m unittest discover -s bin/tests -p test_factory_transitions.py : fail/error distinction, missing assignments, cap never accepts, candidate repair retains blocker, required reviewer added before acceptance, evidence invalidation after acceptance before publication |
| Ordered steering | Existing stop marker; add request identity, barrier, acknowledgment and application state | Trusted control entry, dispatch protocol | python3 -m unittest discover -s bin/tests -p test_factory_steering.py : pause during valid completion, cancel plus late success, revision during check, duplicate/conflicting request, stale answer, stop before/after dispatch, resume versus newer revision barrier, informational classification versus unrelated pause |
| Result recovery and accounting | Existing raw output/usage; retain producer provenance and add protected receipt adoption | Artifact publication, instance incarnation, typed usage observations | python3 -m unittest discover -s bin/tests -p test_factory_result_adoption.py : recover plus delayed replay settles once, foreign/corrupt result rejected, unknown reservations retained, restored old incarnation invalid |
| Inquiry and memory integration | Existing brief/plugin/catchup material; ship generic required contracts and independent access/evidence states | Shared seed payload, inquiry methods, memory records | python3 -m unittest discover -s bin/tests -p test_factory_inquiry_records.py : valid refutation versus collection error, permitted inconclusive outcome, method revision, partial source access, source-linked lesson |

Runtime selection does not block this contract work. The next design step maps these proposed operations to Claude Code and Codex adapter inputs, outputs and lifecycle observations, preserving each host's native strengths. Later authorized implementation first proves the mechanical contract in a generated project with fake native events and real subprocess crash fixtures, then performs bounded real-native probes.

## Self-attack and limits

A requirement edit could reset spend: accounting scope spans successor runs. Cancel could accidentally discard reality: capture/usage/reconciliation remains allowed, acceptance does not. An old artifact could be relabeled current: provenance is immutable and adoption is separate. A repaired candidate could erase review obligations: findings require explicit disposition. A pause could be claimed before workers stop: run disposition and physical execution are displayed separately. A source-fetch failure could masquerade as a negative result: execution and conclusion are independent. Database restore could repeat authority: owner incarnation is fresh and independent of a restored counter.

These are proposed invariants. Native observation gaps, OS isolation, crash durability and useful research/memory behavior remain unverified until later authorized probes. No runtime language, dependency installation or activation is required by accepting this document for continued design.

## Independent record-level critique

Verified: the independent reader reviewed the actual draft and found missing queue-time invocation/workspace claims, missing acceptance binding to the current required-obligation population, underspecified barrier resolution under concurrent steering, and no explicit evidence-invalidation transition. The draft now includes all of these contracts and targeted future fixtures. Review findings are specification gaps, not reproduced runtime failures.
