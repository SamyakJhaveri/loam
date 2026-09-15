# Native worker lifecycle and factory loop

Status: proposal following accepted distribution/configuration direction. Runtime implementation deferred.
Examined source: clean main d627bb2755ad49865f798bcb095800ddd2ad1ced.

## Work and checks for this design step

- Read current execution, grading and resume paths. Check: git status/rev-parse and source reads of bin/factory:1045,1106-1209; clean unchanged main confirmed.
- Define contracts and attack failure cases. Check: independent loop critique and transition-table coverage of unknown launch, crash during checking, stale output, stop and steering. Expected: no path grants acceptance from missing evidence.
- Update living design and decisions. Check: Python document/link/contract validation; proposed runtime tests stay labeled unimplemented.

## Ownership and unit of control

Recommendation: the supervisor controls stages, not each tool call. A native worker owns investigation, planning within scope, native tools, subagents and implementation. The supervisor owns admission, exclusive run ownership, attempts, evidence validation, limits, transitions and acceptance. Native conversation completion reports a stage result to validate, not task acceptance.

Recommendation: distinguish work revision (what was authorized), run (an effort against a revision), attempt (one invocation of a stage) and native session (provider conversation identity). A resumed native session can participate in a new attempt. A native session is not the durable run identity. Inputs, candidate and evidence carry these identities so late results can be classified.

Recommendation: store phase and execution status separately. A check phase can be running, waiting for a dependency, interrupted or complete. Acceptance and publication have independent status. A PR can exist for incomplete work; a valid local result can be accepted without publication. A completed inquiry can have a negative conclusion.

## Proposed native adapter responsibilities

These are Loam interface responsibilities, not claims that providers expose identically named APIs.

| Operation | Inputs | Observable result |
|---|---|---|
| Prepare | Admitted profile, immutable task/context assets, candidate/workspace identity, attempt output location | Readiness report, desired native launch, required capability evidence or precise blocker |
| Start | Persisted attempt identity and approved launch | Native process/session handle or uncertain-launch outcome; no blind repeated start |
| Observe | Owned attempt/process/session | Native events, artifacts, usage and liveness evidence, preserving raw events alongside normalized facts |
| Request interruption | Attempt identity, reason, urgency and steering/stop identity | Acknowledgment of request; termination remains unconfirmed until observed |
| Reconcile | Last durable attempt state and native/process evidence | Still active, finished with collectable output, confirmed ended, or unknown |
| Continue or restart | Reconciled prior attempt, compatible session/context and admitted revision | New attempt linked to prior evidence; reuse session only where supported and suitable |
| Collect | Ended/quiescent attempt and declared artifact locations | Validated artifact inventory and native outcome; task acceptance remains the supervisor's decision |

Recommendation: start/continue accepts no free-form elevation of policy from worker text. Missing required capability is a specific blocker. An optional capability may be absent if an authorized alternative preserves the method. Continuing independent work remains possible if it does not depend on the blocker or violate ownership.

## Transition contract

All transitions require the current exclusive execution owner and a durable record. Source-controlled policy changes do not silently govern an active run.

| Phase/event | Required condition | Next action |
|---|---|---|
| Admission | Exact work/profile revisions validated; authority, dependency and asset checks satisfied | Persist admitted run and prepare declared first stage |
| Baseline, when applicable | Declared baseline expectations met for each applicable check; process success and complete results | Permit implementation, or classify defective criteria/environment |
| Worker preparation/start | Attempt intent persisted before native activation; settings and output boundaries ready | Launch and associate process/session, or reconcile uncertainty |
| Worker ended | Process tree quiescent or declared external job handoff reconciled; output matches attempt and scope | Validate candidate/artifacts, then evaluate |
| Checking | Every required check has a current valid result for candidate, work revision and criteria revision | PASS moves to required review; functional FAIL may request repair; ERROR/UNAVAILABLE follows an explicit retry/block policy |
| Review | Required reviewer output valid; blocking findings resolved or explicitly dismissed with authority | Permit acceptance check, request repair or retain incomplete work |
| Acceptance | Required coverage complete; current candidate unchanged; no unresolved invalidating steering or blocking findings | Write acceptance record citing receipts |
| Publication | Accepted result or explicitly authorized incomplete artifact; destination/action authority satisfied | Persist submission intent, publish, record receipt or reconcile unknown outcome |
| Policy violation | Observed disallowed model/effort, or loss of a required execution guarantee | Persist violation; prohibit further dispatch/continuation; request interruption; reconcile descendants; withhold acceptance and require readmission |
| Stop or steering | Request durably ordered and tied to affected revision/stage | Acknowledge applicability; interrupt or defer to a safe stage boundary; invalidate affected evidence |

Recommendation: baseline expectations are check-specific. A new regression check may be expected to fail before implementation, while a standing integrity check must already pass. Research inquiries use method/evidence completion requirements and need not have a failing software baseline.

Recommendation: FAIL means a valid evaluation found unmet behavior; ERROR means the evaluation could not establish that result. Missing, malformed, duplicate or stale check output is not PASS. Retry the failed stage when appropriate; do not automatically ask the implementation worker to fix an infrastructure error. A cap ends effort with retained evidence and an incomplete outcome; it cannot dismiss findings.

Recommendation: candidate evaluation runs in an isolated evaluation context with no supervisor-state or publication authority. Candidate-controlled tests/builds can execute arbitrary code. Protected evaluation machinery validates result shape, required coverage and source identity, then the supervisor writes receipts. A candidate is identified by an immutable commit/tree plus declared inputs. Before acceptance, verify evidence refers to that same candidate and criteria; never combine passes from different candidates as if they were one.

## Crash, ownership and stop behavior

Recommendation: persist a dispatch intent before starting the native process, then associate its handle. A crash between native start and handle persistence creates an unknown outcome. Use the attempt identity and supported process/session evidence to reconcile it; if reconciliation cannot distinguish active work from no launch, report uncertainty and do not launch a competing worker. Do not promise exactly-once provider execution.

Recommendation: local ownership requires an exclusive claim, plus a generation identity so old results cannot alter current state. A timeout or expired lease does not prove the old process stopped. A new owner cannot launch work on the same candidate until previous writers are reconciled. Exact locking and durable-store implementation is the next engineering decision.

Recommendation: stop requests and observed termination are separate. A stopped parent with active descendants is not quiescent. Do not grade a workspace that an old worker can still modify. Unknown provider or external-job termination remains explicit; no premature cancelled/success state.

Recommendation: persist stage outcome, attempt history, counters, blocking findings, candidate identity and publication receipts. On restart, complete or reconcile the interrupted stage instead of estimating progress from file names. Native events can be duplicated or partial; ingestion needs event identity/order handling and atomic state updates. Raw log presence never proves phase completion.

## Native-specific clauses from the original sources

Verified source basis: [sources-official.md](sources-official.md), [sources-cookbooks.md](sources-cookbooks.md) and [sources-loop-repos.md](sources-loop-repos.md). Their exact original URLs and read scopes are retained. These clauses are proposed Loam behavior; documentation reads do not prove installed-host behavior.

Recommendation: admission records requested, resolved and observed model/effort separately, including observation provenance and unknown values. Cover the driver, descendants, reviewers, teammates, advisor, goal evaluator and relevant background functions. Reject known disallowed settings before launch. If the required policy needs prevention of hidden substitutions and the host cannot establish that capability, report unsupported admission. Later observations can detect violations but cannot retroactively prevent them. Missing observations cannot generate a compliant receipt. The user's policy is not silently weakened to observation-only. A detected violation is not ordinary deferrable steering: persist it, prevent further dispatch or continuation, request interruption of affected work and reconcile its descendants. Retain outputs as noncompliant evidence and withhold acceptance even if functional checks pass. Restart requires a newly admitted compliant profile; unknown termination still prevents reuse of the workspace.

Recommendation: each native profile declares its real coordination surface. Interactive Claude teammates and headless Claude subagents have different capabilities. Preserve both when available; do not describe one as the other. Role prompts, skills and tools require effective-context probes because native display/launch modes resolve them differently. Codex uses its own documented native delegation and role-resolution contract. Equivalent Loam result semantics do not require pretending their native APIs are identical.

Recommendation: native Workflow recovery records native session identity, workflow revision, expected task identities and dependencies, start order and replay provenance. A native cache becoming invalid does not erase durable artifacts or reverse a completed external action. Reconcile those effects before replay. Same-session continuation and fresh-session restart are distinct paths. Require replay-safe operations or explicit external outcome reconciliation; retain unknown outcomes when evidence is unavailable.

Recommendation: aggregation begins with an expected task/claim manifest. Dynamic additions are durably registered as the inquiry expands. Each required identity must have one current valid outcome or an explicit unmet status. Null worker, verifier or skeptic output stays unresolved. Filtering absent results out of a report cannot shrink the expected population. Structural completeness does not establish semantic source support.

Recommendation: native goal achieved means ready for Loam validation. Impossible, cleared, interrupted, paused or absent goal state does not imply acceptance. Maintain background-job inventory and supervisor lifetime accounting across native resume/reset boundaries. Do not replenish run limits from a new native accounting baseline. Preserve event provenance to avoid double-counting.

Recommendation: native teammate plan approval is execution metadata. A task requiring independent plan review needs a separately reviewed plan artifact and the configured admission transition. This does not add a human checkpoint to every task. Persisted native tasks do not prove that old teammates remain alive after restart; reconcile or rehydrate replacement workers from durable evidence.

Decisive future fixtures: an allowed driver with unknown/disallowed auxiliary role; a failed earlier worker with a successful later sibling; null skeptic; goal cleared while an experiment remains active; native accounting reset on resume; automatic native plan approval with a failed required independent review. None may yield false policy compliance, duplicated consequential effects or accepted work.

## Discovery, deliberation and authorized recurring work

Recommendation: distinguish the native thinking loop, the supervisor's durable work loop, authorized recurring discovery, and reviewed improvement of the factory itself. All supporting mechanisms ship with every seed. A schedule is one optional trigger for the same supervisor, not a second source of authority.

A discovery policy names the permitted subject/surface, cadence or explicit trigger, allowed read/write actions, limits, finding identity, retry/cooldown rules and routing authority. A scan may produce a finding, a bounded inquiry, a proposed decision or an implementation ticket. It does not authorize implementation or publication beyond that policy. A repeated unchanged finding can link to existing work; changed evidence can reopen it with a reason. An empty scan is a valid no-op. Failure to scan is an error, not evidence of no findings.

Research lead and independent workers can revise the investigation as originals or experiments contradict the initial hypothesis. Preserve each report before peer critique. Record competing explanations, decisive evidence and the synthesis owner's reason for choosing a solution. Agreement, a count of citations and a polished report are not substitutes for evidence. The human's original requirement remains distinct from model-generated expected values and examples.

Extended export example, still illustrative: the owner asks for reliable exports for empty datasets. Discovery inspects actual callers and the project schema. An inquiry compares deriving columns from rows against deriving them from an explicit schema. Independent source/code readers report the empty-input failure and consumer compatibility; critique tests whether either method loses optional columns. A decision records the selected schema source, rejected alternative and domain-specific examples. The resulting ticket uses those independently checked examples. Continue through the crash/review/acceptance flow above. After acceptance, memory links the applicability-limited lesson to that decision, candidate and check. A later schema change invalidates its derived context until rechecked. If recurring export diagnostics are later authorized, a changed failure can reopen inquiry without silently reopening implementation authority.

## Concrete export-ticket example

Illustrative flow, not work performed in this session:

1. Generate a project from the accepted complete seed. It has the local factory and documented tool prerequisites; no private Loam runs or personal-cache dependency.
2. The owner asks for an export containing column headers even when there are no rows. The lead confirms existing behavior and records a bounded ticket with the approved profile. If a consequential design uncertainty emerges, first record an inquiry and decision instead of pretending the ticket is ready.
3. Admission pins the ticket/check definitions and candidate baseline. The new empty-export regression check must fail at baseline; existing integrity checks must pass.
4. The supervisor starts a native worker attempt. Astra or Fable, according to the selected approved harness profile, implements the change using native capabilities and returns a candidate plus an artifact inventory.
5. The worker exits and its writers are reconciled. The evaluator checks the candidate. The check process crashes before producing the required result: record ERROR and keep acceptance pending.
6. The supervisor restarts. It recovers the checking phase and reruns only the incomplete check attempt when safe. It does not begin another implementation round simply because a checks file exists.
7. The check passes, but a required review response is malformed. Record review ERROR and apply the review retry policy. If exhausted, preserve the candidate as incomplete. A later valid review with no unresolved blockers allows acceptance.
8. Write an acceptance record for the exact candidate and criteria. Any PR creation is a separate authorized action. If publication succeeded but its receipt was lost, reconcile the external result before trying again.
9. Persist linked evidence. A memory proposal may describe the useful edge case and supporting check. Its wording or indexing is not substituted for the acceptance receipt.

A correction during the flow, such as changing the requested export behavior, becomes ordered steering. Preserve the candidate and old observations; revise the authorized work/check definitions and exclude stale evidence from current acceptance. Do not erase history or let a correction bypass admission.

## Where memory and learning connect

Recommendation: durable run state answers what the system is doing and what remains incomplete. Project memory answers what later work should know, why it is believed, when it applies and where its sources are. A model-written summary cannot replace run state.

| Memory connection | Contract |
|---|---|
| Before inquiry or implementation | Retrieve applicable decisions/lessons with sources; check against current context and preserve contradictions |
| During work | Persist observations and decisions as artifacts with provenance; distinguish observation from interpretation |
| At handoff/recovery | Supply concise source-linked context to the native worker while the supervisor recovers authoritative stage state separately |
| After evaluation | Propose evidence-backed lessons, including failures and negative conclusions; source evidence remains available |
| Improving the factory | Propose changes to prompts, role definitions, workflows or checks; evaluate against representative/held-out cases and retain rollback; no automatic lesson-to-policy promotion |

Memory machinery ships with every seed and starts with empty project stores. Proposed indexing/consolidation is separate from ticket acceptance unless the admitted task explicitly requires a memory deliverable. Index failure is reported and recoverable; it cannot silently erase stored evidence. Research and team deliberation feed the same evidence/decision records, with completion criteria suited to inquiry.

Required upcoming memory design: record schemas and ownership; shareable versus private content; capture and consolidation; retrieval; applicability and invalidation; conflict/supersession; native memory integration; evaluation of actual usefulness. Required loop implementation design: module boundaries, storage and locks, atomic transitions, adapter lifecycles, process-tree management, limits, retries, steering and failure fixtures. Neither topic is being deferred out of scope.

## Existing source and proposed implementation checks

Verified: bin/factory:1106-1152 already contains the worker/check/grader loop, but check exit is not used for success, grader caps reach publication and process-local counters hold policy state. At 1195-1200, resume uses check filenames. These source-backed findings motivate replacing the transition logic rather than merely packaging it.

Proposed future commands, not implemented or run:

| Change | Dependencies | Runnable acceptance interface and decisive cases |
|---|---|---|
| Explicit stage transitions and evidence validation | Admitted profile, check manifest, candidate identity | python3 -m unittest discover -s bin/tests -p test_factory_loop.py : silent nonzero/partial/duplicate/stale checks, malformed review, caps never accept |
| Adapter lifecycle and exclusive ownership | Native capability contracts, durable attempts, process observation | python3 -m unittest discover -s bin/tests -p test_factory_attempts.py : crash before/after dispatch, competing launches, late old output, live descendants |
| Recovery and steering | Persisted transitions/counters/findings, revision invalidation | python3 -m unittest discover -s bin/tests -p test_factory_recovery.py : resume incomplete checking/review, preserve retries, correction before acceptance, unknown publication outcome |
| Memory connection | Evidence store, provenance and accepted decision authority | python3 -m unittest discover -s bin/tests -p test_factory_memory_contract.py : source-linked handoff, contradictory lesson retained, stale applicability rejected, indexing failure does not fabricate acceptance |

Fake adapters and local synthetic artifacts establish the mechanical contract first. Tests must not invoke paid models, install dependencies, publish or activate schedulers. Later authorized native probes establish real continuation and termination behavior. The complete proving slice still starts from a generated project independent of Loam.

## Smallest complete proving slice

Recommendation: first prove a generated project's local vertical path using a deterministic fake native adapter: render the full factory, resolve a project profile, create a bounded inquiry/decision/ticket fixture, admit it, record a failed baseline, produce a changed candidate, crash during checking, restart, reject incomplete review, accept only complete current evidence, and retrieve a source-linked lesson in a fresh process. The fake adapter supplies reproducible native events; it does not prove real model quality or native-host compatibility. Then, under later explicit runtime authorization, run the same contract against each real native profile.

The slice includes research, deliberation, memory and disabled trigger interfaces in the distributed payload. Fixture reports prove their routing/storage contracts, not scientific discovery or independent native-agent behavior. Scheduled activation, rich retrieval and live steering need their own later probes. No optional plugin or original Loam checkout may be needed by the generated project after rendering.

Dependencies: accepted distribution/ownership and shared profile boundaries; chosen state/transaction implementation; protected evaluator boundary; fake adapter; declared check manifest; source and decision records. Runnable future acceptance interfaces remain the unimplemented test commands above, plus the generated-project isolation check defined in distribution-design.md. A full factory requirement cannot be satisfied by a green test that exercises only Loam's root checkout.

## Self-attack

Crash after launch but before receipt: reconcile uncertainty, never blind duplicate. Parent exits with surviving child: do not evaluate mutable candidate. Retry after cap/restart: counters and findings persist. Worker-authored PASS text: protected evaluation validates the admitted checks and supervisor owns receipts. Research with no failing baseline: use method-specific criteria. Memory service unavailable: preserve source evidence and report the indexing issue. These are proposed contracts, not runtime guarantees.

Recorded UTC: 2026-09-14T01:42:52.852952+00:00
