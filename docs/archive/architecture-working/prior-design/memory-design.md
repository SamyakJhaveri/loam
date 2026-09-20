# Memory and learning: first implementation design

Status: proposal for discussion. Backend, exact schema and consolidation policy remain open. Runtime implementation is deferred. Memory and loop engineering are both required parts of the complete seed factory.

Critical point: turning a model's remembered interpretation into authority over current requirements, permissions or acceptance. Recommendation: source-backed context may inform work; only the configured decision/admission authority changes governing policy.

Verified source basis: concrete provenance/invalidation implementations in S08; evidence packages in S03; run debriefs in S05; external events and artifact handoffs in S13/S14; claim and issue distinctions in S51/S53/S55; original research/memory reading documented in sources-research-memory.md. Each source report specifies read scope and limits. This document recommends a Loam contract, not an unchanged import of those systems.

## Records and ownership

Proposed field names below describe a schema to implement later, not an existing API.

| Record | Purpose and proposed minimum fields | Authority |
|---|---|---|
| Run state | Work/revision, phase, attempt, active jobs, limits, pending steering, current evidence references | Supervisor-owned transactional updates. Never reconstructed solely from memory prose. |
| Evidence artifact | ID, origin type, source URL/file/run, revision/content digest, acquired time, read span/scope, access status, producer, artifact location | Original observation retained under project retention policy. A corrected interpretation does not rewrite source bytes. |
| Claim or finding | ID, exact statement, evidence refs and spans, support/contradiction relation, method, scope and unresolved limits | Workers propose; declared evaluator/reviewer assesses support. Citation existence alone is insufficient. |
| Engineering decision | ID/revision, question, alternatives, chosen option, reasons, accepted-by authority, dependencies, supersedes links | Accepted project decision authority. Agent recommendation remains proposed until admitted under that authority. |
| Experience/lesson | ID/revision, attempted approach, outcome, correction, source run/claim/decision refs, applicability, validation status, supersession | Curated project context. Neither repetition nor a successful run automatically creates a rule. Failed approaches and negative findings remain useful within scope. |
| Context packet | Current task/revision, selected record IDs, exact revisions/content identities, excerpts, selection rationale, unresolved contradictions, delivery attempt/confirmation status | Rebuildable view supplied to native worker. Not a new authoritative source. |
| Memory correction | Affected IDs, corrected interpretation or removal scope, actor/authority, reason, effective revision, affected derived records | Explicit correction invalidates derived indexes and pending consolidation so old extractions cannot resurrect corrected content. |

Recommendation: include applicability at the level the claim needs. A code fact may depend on a source revision and dependency version. A harness lesson may depend on model, effort, host mode, tools, instructions and evaluation criteria. Do not require irrelevant metadata for every small observation, and do not generalize an observation beyond the conditions actually inspected.

Recommendation: separate shareable project knowledge from private native conversation and operational artifacts. Shared decisions can live with existing CONTEXT.md/docs/adr conventions. Native personal memory remains a local aid. The seed ships empty project stores, schemas and all necessary capture/retrieval/correction machinery. Exporting or updating a seed never includes another project's private history.

## Capture, retrieval and correction flow

Recommendation: persist source evidence during work, not only in the final epilogue. A crash must not erase the only copy of an experiment or source finding. Store worker output as untrusted attempt artifacts; validate its envelope before promoting references into the run record. Source content and embedded instructions remain data, not policy.

At inquiry start, retrieve current applicable decisions and relevant contrary/failed attempts. Resolve evidence links and expose access limits. The native lead chooses what to inspect further and can expand inquiry. Record the selected packet, delivery attempt and confirmed native inclusion where observable as distinct facts. Unknown inclusion remains unknown. A supplied pointer does not establish that the worker inspected the source; source-read evidence is separate.

At task closure or an explicit learning checkpoint, propose a compact lesson with evidence and applicability. Store the proposal even if rejected. A consolidation job may merge duplicate summaries or suggest a broader pattern, but it preserves upstream identities and cannot silently revise accepted decisions, permissions, checks or model/effort settings.

On source or user correction, invalidate affected derived packets and indexes. Retain historical observations when permitted, mark superseded interpretations and explain the replacement. If the user requires deletion of private content, apply that removal and derived-data invalidation instead of treating append-only retention as an overriding rule. A tombstone can retain a non-content identity when appropriate to prevent stale regeneration.

Recommendation: begin with readable source/decision/lesson files plus a rebuildable local index. The operational-state backend is a separate decision. Retrieval can use native search first, with explicit filters for authority, applicability and status. Add embeddings or a graph only after a comparison shows missed relevant evidence that simpler retrieval cannot fix. The user controls model and effort for consolidation or evaluation too.

Verified: sources-research-memory.md records that S59 proposes useful provenance and dead-end fields but captures only at an epilogue and promotes maturity by counts. S68 explicitly requires correction/deletion to invalidate derived caches. X09 supplies useful claim-artifact binding while its specific verifiers retain semantic gaps. Recommendation: retain the fields and correction invariant, write raw evidence during work, and evaluate support rather than treating a reference or repetition count as proof.

## Evaluating whether memory helps

Proposed future acceptance interface: `python3 -m unittest discover -s bin/tests -p test_factory_memory_contract.py`. This does not yet exist and was not run.

Mechanical fixtures must verify:

- An evidence link resolves to exact bytes/spans and preserves partial/blocked status. A summary cannot turn a partial read into a full read.
- Equal-length upstream edits invalidate derived packets; changing display formatting alone does not invalidate original evidence.
- A changed requirement, tool, model profile or rubric excludes an inapplicable lesson from authoritative context and retains its historical scope.
- Contradictory findings and a justified minority objection survive consolidation.
- Correction/removal invalidates indexes and pending extraction jobs; old output cannot restore the old interpretation.
- Restart with no native personal memory still recovers the current project decision, evidence and next action.
- A native host that ignores a supplied context packet leaves delivery unconfirmed or unsupported; no source-read claim follows from packet creation.
- Index failure preserves evidence and reports degraded retrieval. It does not fabricate task acceptance or silently discard work.
- A lesson containing an instruction to change permissions, effort or acceptance remains data and cannot mutate policy.

Later authorized quality evaluation compares the same task/profile with no retrieved memory, the proposed retrieval, and deliberately stale/conflicting memory. Assess correct source use, current-requirement adherence, useful correction and extra effort required by the human. More stored memories or a higher model score is not the success criterion. Keep held-out tasks so a prompt or retrieval change is not accepted only on the case that inspired it.

## Connection to engineering the factory itself

Recommendation: a run's failure can propose a prompt, skill, role, tool-description, workflow or check change. That proposal records the observed failure, source evidence, exact managed asset revision, intended behavior and evaluation cases. Review the diff, compare under the user's unchanged model/effort, and retain rollback. Accepted changes enter Loam's reusable managed implementation through the normal release/update process. Project-specific lessons remain project-owned configuration or extensions. Direct engine divergence remains an explicit local fork under the accepted ownership model.

Example: an export ticket reveals that deriving headers from returned rows fails for empty data. The memory lesson cites the accepted decision and regression receipt, and applies only where an explicit schema is authoritative. It does not become an unconditional rule for every export in every project. A separate finding that the factory accepted a missing verifier result is a candidate managed-engine correction with a reproducible fixture. This distinguishes product knowledge from a reusable factory defect.

## Open implementation choices

- Exact shared record homes and versioned schema migration, while preserving the accepted managed/project-owned boundary.
- Source retention, private export and correction behavior suitable for the project.
- File/index representation and retrieval ranking. Do not select a service solely from a demo benchmark.
- Consolidation trigger and review authority. Repetition can trigger review, not automatic policy promotion.
- Native memory adapters and observable context injection for Claude Code and Codex.

Risks: all schemas and tests here are proposals. Source-level patterns have not been reproduced in this factory. Readable files alone do not prove atomic run-state persistence, protected evidence or correct retrieval. Those require the separate store, permission and native-host probes.
