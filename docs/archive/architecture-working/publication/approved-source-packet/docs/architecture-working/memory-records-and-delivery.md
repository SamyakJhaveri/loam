# Memory record schema and native context-delivery contract

Status: retained implementation-design baseline following the user's acceptance of the recommendations and story explanation. Exact physical implementation and native capabilities remain subject to their stated checks. No runtime code, database migration, provider process or model evaluation is implemented by this document. Examples are illustrative; Loam serves research projects broadly.

The user requires evaluation after development and installation throughout real task work. The records below support that observation as well as later controlled comparisons. They do not assume memory helps merely because it was retrieved.

## Architecture and alternatives

Recommendation: use a small typed proposal from the worker, immutable registered records owned by Loam, and distinct delivery/use observations. A logical schema defines fields and relationships; physical SQL tables, indexes and serialization libraries can follow without changing these responsibilities.

| Approach | Advantage | Limitation | Choice |
|---|---|---|---|
| Free-form notes written directly to shared memory | Simple capture | Source identity, conflicts and activation become inferred from prose; workers can overwrite knowledge | Keep free-form text inside proposals/artifacts, not as the write-authority interface |
| Typed proposals plus source-linked immutable revisions | Explicit provenance, review, correction and replay; compatible with both native hosts | Requires validation, review routing and projection | Recommended initial contract |
| Full transcript ingestion with automatic extraction and promotion | Broad capture with little explicit worker input | Private/context-heavy data, uncertain relevance and causal interpretation; difficult correction scope | Optional later extraction into the same candidate interface, never a separate promotion path |

Recommendation: separate normalized fields used by the supervisor from readable narrative used by agents. Avoid an arbitrary confidence number. Support, scope and missing evidence are more informative and can be evaluated separately.

## Worker proposal

Proposed request envelope: schema identifier, client request identity and the payload below. An authenticated local channel binds the actual submitting attempt or user. A field inside the payload cannot authenticate its author.

| Field | Required meaning | Validation and use |
|---|---|---|
| `operation` | `propose`, `revise` or `suggest_correction` | Revision/correction requires an exact target revision. These are proposals, not direct activation or retraction commands. |
| `kind` | `observation`, `finding` or `lesson` | Controls required narrative. Only a lesson requires advice. Evidence and accepted decisions remain separately owned records. |
| `target_revision` | Exact prior revision for revise/correction, otherwise absent | Must be visible to the submitting principal; stale predecessors cannot be overwritten. |
| `situation` | Task and conditions in which the observation arose | Concise description; execution metadata is derived independently. |
| `observation` | What actually happened | Distinguish tool/experiment result from a worker's recollection. |
| `interpretation` | Proposed explanation or conclusion, or explicit unknown | A finding/lesson requires this field; unsupported causality cannot take the direct-observation review route. |
| `advice` | Suggested future behavior for a lesson | Must state scope; cannot change governing policy through imperative wording. |
| `evidence_links` | Registered evidence revisions and exact spans, with `support`, `contrary` or `context` relation | Validate identity, visibility, source availability and span bounds. An empty list is permitted only for an explicitly unsupported candidate, not active advice. |
| `applicability` | Claimed conditions, relevant dependency references, exclusions and unknowns | Worker claims are assessed; they are not executable predicates or an authority grant. |
| `limits` | Counterexamples, untested generalizations and unresolved questions | Empty means none reported, not a guarantee that none exist. |
| `invalidation_conditions` | Observable changes or newly discovered facts requiring reassessment | Prefer concrete dependency changes over an arbitrary age threshold. |

Recommendation: version the envelope and reject duplicate object keys or unsupported authority-bearing fields. Preserve the raw submitted payload as evidence and return a structured validation error; never silently drop an unknown field that could change meaning. Server-reserved fields such as `active`, `approved_by`, authenticated identity, profile and review class cannot be set by the worker. Versioned project/domain extensions are data-only until their registered validator and semantics are admitted.

Idempotency scope is the authenticated submitting principal, local instance and client request identity. Repeating the same request with the same validated payload bytes returns its existing receipt. Reusing that identity with different bytes is a conflict. Clients retain the exact bytes for retry. A fresh submission identity does not make a similar lesson new evidence; semantic deduplication is separate and cannot discard a contrary finding. This gives repeatable local submission, not exactly-once native execution.

Evidence links point to the protected evidence registry, not arbitrary mutable filesystem paths. Workers can submit staged evidence for capture first. Missing or inaccessible evidence can remain a qualified candidate. No captured source is required to equal today's source bytes to remain valid historical evidence; current applicability is a separate assessment. An exact span identifies the material, not whether it supports the claim.

## Fields Loam derives and retains

| Record | Supervisor-derived identity and metadata |
|---|---|
| Memory revision | Record/revision IDs, schema version, project/local instance, actual submitting principal, original producer/run/attempt/native identity where observable, admitted profile, immutable body artifact/digest, local sequence and acquisition time |
| Review assignment | Subject revision, review-policy revision, required class, actual assigned role/attempt, required input manifest and independence requirements |
| Lifecycle | Candidate/active/rejected/superseded/retracted state, current head, prior revisions, assessment and activation receipts, correction/tombstone dependencies |
| Visibility/dependencies | Effective access scope, registered source/decision dependencies, accepted applicability, source availability and current correction generations |

Recommendation: retain actual producer and submitter separately when a lead submits a specialist's report. Unobserved producer identity remains unknown. Imports preserve foreign provenance and gain a separate local import identity. They do not inherit foreign project authority. Requested, resolved and observed model/effort stay separate using the existing admitted-profile contract; absent observations are not filled from a worker claim.

Substantial bodies use the accepted artifact-first publication protocol. SQLite records lifecycle and source relationships. Human-authored decisions stay canonical in their admitted source documents, without a second writable decision body. This contract also refines the older state draft's reference to versioned accepted lessons: shareable lesson exports are explicit projections/imports, not a second live lifecycle store.

## Assessment and activation

Recommendation: the supervisor chooses review requirements from the admitted project/method review policy. The worker can propose classification but cannot select a weaker route. Uncertain classification moves to the stronger applicable route or remains pending; schema validation cannot reliably detect all semantic overclaiming.

| Review route | Who assesses | Conditions |
|---|---|---|
| Narrow direct observation | Lead or assigned reviewer; producer assessment only where project policy explicitly permits it | Inspectable direct evidence and limited scope. Record self-assessment honestly. No causal generalization or policy change. |
| Explanation, generalization, contested or consequential advice | Fresh reviewer who did not produce the proposal | Inspect claim, supporting and contrary originals, scope and limits. Independence means distinct context and authorship, not necessarily a different model. |
| Governing change | The existing configured decision/admission authority, with required evaluations | Memory review can recommend the change; it cannot activate a decision, permission, model/effort setting, method or acceptance rule. |

Direct observations are still assessed records. They need not pretend to be reusable advice. The ordinary lesson route never bypasses required evidence review. Adversarial review can be requested where a discriminating counterexample matters; it is not a mandatory extra agent for every note. All assessors use the user's allowed models and selected effort policy.

An immutable assessment contains:

- Exact subject revision, review-policy revision, assignment identity and required input manifest.
- Actual assessor principal, attempt and admitted profile; independence observations where required.
- Trusted mechanical validation result: valid, invalid or incomplete, with reasons.
- Semantic support: supported, partially supported, unsupported or undetermined.
- Applicability judgment: supported scope, disputed scope or insufficient information, with explicit conditions.
- Actual inspected evidence spans, missing sources, contrary evidence and unresolved findings.
- Recommendation: activate scoped advice, retain candidate, reject or request revision; plus rationale.

Recommendation: a partially supported compound lesson is revised into a supported scoped statement before activation. Do not activate the original broad wording by attaching a quiet caveat. An undetermined causal explanation can remain useful explicitly labeled candidate context, but cannot appear as established current advice. Existing active evidence-backed historical observations need not be erased when applicability changes.

Activation is a short supervisor transaction after artifacts and assessments are captured. It checks current ownership, subject revision, expected predecessor, review-policy revision, required assignments, eligible assessment, source availability, accepted scope, correction/tombstone generations and relevant barriers. It atomically writes the activation receipt, revision head, dependency links and audit event. A failed precondition retains the candidate and assessment with an explanation; it never defaults to activation. Required conflicting assessments remain unresolved until the configured adjudication records its reasons and evidence. A vote count cannot substitute for that adjudication.

Revising or narrowing the proposal body creates a new subject revision. Reviewing an unchanged subject creates a separate immutable assessment linked to that same subject revision; it does not edit the subject or move its head. Old assessments do not automatically transfer to edited wording. Concurrent revisions of the same predecessor conflict. Stale producer output may be captured with its original lineage; only current authority can explicitly adopt and assess it. Source acquisition and model review happen outside the database transaction.

## What the native worker receives

Recommendation: a context packet is an immutable artifact tied to its intended attempt/role. It contains a concise readable brief plus a machine-readable manifest. These are projections of admitted records, not independently editable sources. Preserve exact mandatory instruction spans where their wording matters; generated summaries are qualified continuity/advisory material.

| Packet section | Content |
|---|---|
| Assignment | Original human request reference and relevant text, current normalized objective, work/run/stage/attempt and role, admitted method/profile references |
| Governing requirements | Applicable decisions, mandatory constraints, acceptance obligations, actual authority boundaries and current authorized steering |
| Work state | Verified completed obligations, remaining work, unresolved questions/findings, candidate/workspace identity and relevant in-flight operations |
| Relevant knowledge | Eligible advisory lessons, relevant failed attempts, source excerpts/pointers, support/applicability labels and material contrary evidence |
| Continuity | Qualified account of prior work, abandoned approaches and next intended action, with links to originals and explicit known gaps |
| Outputs and interaction | Required deliverables and artifact destinations; supported progress, question, evidence-proposal and steering channels |

The worker receives permission and limit summaries only as useful context; actual enforcement remains outside model-written prose. No control-store credentials or unrestricted lifecycle write interface are included. The worker can request more source context within its admitted access scope.

Proposed `ContextPacket` fields: packet/schema identity; project/instance; work revision, run, stage, attempt and role; admitted method/profile and required-obligation manifest revisions; exact body artifact/digest; context item list; required-context coverage; selection-policy/query; omission reasons; dependency and correction-generation snapshot; replacement lineage; applicability/expiry conditions where relevant.

Each `ContextItem` identifies a registered record/source revision and body digest, item class (`governing`, `advisory`, `source`, `continuity`), supplied excerpt/span or pointer, support and applicability, selection reason, contrary/replacement links and permitted visibility. Governing class requires an admitted authority reference; a worker-proposed item cannot give itself that class.

Required coverage is specified by the admitted method and role. Token or size pressure cannot silently omit required constraints. Split preparation, narrow the assignment under current authority or report missing coverage. Optional items can be omitted with reasons and accessible references. Renderer checks can establish that required bytes/items were supplied; they cannot prove that a compressed paraphrase preserved every implication.

## Role-specific selection

| Role | Receives | Independence/selection boundary |
|---|---|---|
| Research lead | Original inquiry, source coverage, existing evidence/disputes, allowed methods and expected outputs | Can inspect originals and expand the investigation within authority |
| Independent researcher | Bounded question, governing constraints, shared baseline sources and required outcomes | Peer conclusions withheld until the independent report is captured; relevant source facts and known material counterevidence are not suppressed |
| Implementer | Adopted decision, candidate/workspace, requirements/checks, applicable lessons and outstanding findings | Cannot inherit a prior PASS as current certification |
| Memory assessor | Exact proposal, source/contrary evidence, claimed scope, review policy and correction state | No inherited producer conversation where independent assessment is required |
| Acceptance reviewer | Exact candidate, criteria, check/source evidence and open findings | Fresh native context with appropriate evidence/workspace permissions |
| Synthesizer | Captured independent reports, critique and original evidence | Disagreement remains visible; access to peer interpretations is deliberate |

One universal packet risks unnecessary disclosure and biases independent work. Separate provider-owned copies risk divergent project knowledge. Recommendation: one shared packet builder with role-specific selection and versioned native renderers.

## Delivery records and observations

Recommendation: separate immutable packet contents from a delivery operation and append-only observations. A simple sent/read boolean is insufficient, and observations need not arrive in order.

| Record | Proposed fields |
|---|---|
| `ContextDelivery` | Delivery/action ID, packet ID, target attempt/native session/turn/task, operation kind, expected owner/work/profile/barrier/correction state, authorization receipt, adapter/renderer revision, exact rendered payload artifact/digest, native channel/provenance map and correlation identifiers |
| `DeliveryObservation` | Delivery ID, observed fact, native message/event/turn identities, local sequence and event time when available, raw-event artifact, correlation method, scope and uncertainty |
| `SourceAccessObservation` | Exact source revision/span, actual requester, tool/action identity, requested/success/failed outcome, returned content digest where observable, evidence and observation origin |
| `ContextUseEvidence` | Exact output/claim/decision/check identity, packet and record revisions, claimed or assessed support/use relationship, observer/assessor and reason |

The packet digest and provider-rendered payload digest differ intentionally. The renderer must preserve required items and actual provenance in the selected native surface. Generated follow-ups under an authorized task remain factory-generated, not human-authored. Memory/source text cannot be elevated into an instruction authority by where the renderer places it. Store provider-native fields and unknown events before normalization.

Delivery has a control projection such as prepared, dispatchable, in-flight, reconciled or withdrawn; evidence observations are separate. Record preparation, authorization, attempted send, transport acknowledged/failed/uncertain/unsupported, queued identity, inclusion/consumption, source access and output use independently. A late correlated consumption event can resolve an earlier uncertain transport outcome. Its observation is not erased because events arrived out of order.

Host acknowledgment does not establish inclusion. Inclusion of a pointer does not establish source reading. A read-tool request can fail. A successful read does not establish comprehension. A model's claimed use is labeled self-report. A check of the resulting artifact establishes only what that check actually assessed. No missing observation becomes success through a timeout.

Recommendation: the admitted role/profile states which delivery evidence is required. Do not require an impossible proof of internal understanding. Ordinary execution can rely on a supported transport plus output checks where the method permits that assurance. Work requiring an observed corrective boundary must establish that boundary or remain blocked. A bridge may not downgrade the admitted requirement silently.

## Start, reconnect, resume and correction

| Situation | Identity and packet behavior |
|---|---|
| New invocation | New admitted attempt, fresh packet and dispatch operation; bind actual native identities as observed |
| Reconnect to an already active call | Retain original attempt and packet history; reconcile input, jobs and effects before sending anything. Supervisor restart is not an instruction to launch more work. |
| Compatible information for an active call | New immutable packet/delivery bound to that attempt and actual target; existing admitted revision remains |
| New invocation continuing a stopped compatible stage | New attempt in the same run; fresh packet even if native conversation is reused |
| Material method/objective/profile change | Successor work inputs/run; reconcile old execution before conflicting dispatch |
| Independent review | Fresh context; relabeling an existing producer session is insufficient |
| Switch provider | Shared source-linked records and validated handoff; no assumption of portable private native memory |

This clarifies older wording that every continuation creates a new attempt: a new execution invocation does; passive reconnection or observing the still-running original does not. An informational delivery to that call is not automatically a new invocation, but delivery capable of starting work belongs to the in-flight action inventory.

Before reusing a native session, create a retained-context assessment: actual session, intended role, known prior packets/steering, incompatible or obsolete instructions, native memory/profile scope, evidence gaps and reuse/restart/block recommendation. Keep useful native context when compatible. A new packet does not establish that old instructions were removed. Native-goal continuation retains its existing designated owner; the supervisor must not create a competing turn.

Correction races follow the accepted dispatch-authorization ordering:

1. Before authorization: stale packet dependencies prevent dispatch; prepare a replacement.
2. After authorization but before known host outcome: delivery is possibly in flight. Persist the relevant barrier, retain the old action identity and reconcile. A database check is not atomic with native receipt.
3. After consumption: the old content cannot be unread. Deliver current authenticated steering where supported, reconcile affected execution and reassess materially dependent outputs before acceptance.

Do not resend on a lost acknowledgment unless non-delivery is established or the supported operation has adequate duplicate handling. A native correlation ID alone is not a promise of exactly-once execution. An unremovable stale queue or live descendant can prevent session reuse. Independent unaffected obligations can continue when their dependencies establish that they are unaffected.

Verified from the saved native evidence reports: Codex was investigated through its native app-server and Claude through an open-input SDK bridge; the reports distinguish native targeting/correlation, resumption and interruption from actual incorporation or queue cancellation guarantees. This step adopts the existing bridge direction and refines Loam records. It does not re-certify installed protocols or invent a shared provider API. See [Codex evidence](prior-design/native-codex-evidence.md) and [Claude evidence](prior-design/native-claude-evidence.md).

## Illustrative proposal and fresh-session brief

The JSON below is a design example, not a submitted record. The evidence and revision names are illustrative references to a future registered experiment. They are not claims that this experiment ran. Its request identity is supplied separately by the authenticated transport.

```json
{
  "schema": "loam.memory-proposal.v1",
  "operation": "propose",
  "kind": "lesson",
  "situation": "Testing stale experiment reports against the admitted report identity method.",
  "observation": "A changed dataset kept the same path and length; the path-and-length check did not detect the change.",
  "interpretation": "For this tested case, path and length are insufficient to identify the data used by a report.",
  "advice": "When evaluating this report validator, include a same-path, same-length content-change case.",
  "evidence_links": [
    {
      "evidence_revision": "example-experiment-result-revision",
      "span": {"kind": "json_pointer", "value": "/cases/same_path_same_length"},
      "relation": "support"
    }
  ],
  "applicability": {
    "conditions": ["The validator claims to detect changed report input data."],
    "dependency_refs": ["example-report-method-revision"],
    "exclusions": ["Reports with explicitly different freshness semantics."],
    "unknowns": ["Whether preprocessing settings also affect the required identity."]
  },
  "limits": ["This case does not establish a complete dependency-tracking solution."],
  "invalidation_conditions": ["The admitted report identity contract changes."]
}
```

Recommendation: a new implementation worker receives the current decision/identity contract, its actual candidate and checks, this scoped lesson if assessed active, relevant contrary evidence and the original experiment pointer. It does not receive an unqualified instruction that every project must hash every input. A memory assessor receives the exact proposal and experiment to test its support. A later correction to freshness semantics creates a replacement packet and applicability assessment; the historical experiment remains a historical observation.

## Ongoing evaluation in real project work

Recommendation: record `MemoryUseObservation` as an observation, not a score that automatically promotes lessons. Fields: actual task/attempt, packet/delivery and selected record revisions, retrieval policy/query, original output identity, observation kind, actor/provenance, related check outcome, feedback text/artifact, and proposed correction/evaluation-case references. Permit missed-retrieval observations with no delivery and an identified record discovered later. Do not invent a packet or exposed population for material that was not supplied.

Useful observation kinds include relevant source recovered, verified mistake avoided, harmful carryover, missing relevant lesson, correction ignored, source unavailable, and no evidenced use. Worker-reported benefit and authenticated human feedback stay distinguishable. Feedback binds to the exact output seen; rerunning to create a trace would be a different execution. Observations may arrive after task closure without rewriting historical acceptance.

Capture readily available packet/use/output associations during normal work. Do not ask the human to grade every retrieval or launch a model reviewer for every access. At explicit task debriefs, human feedback or a configured admitted maintenance checkpoint, investigate patterns and propose corrections or evaluation cases. No automatic scheduled job is implied. User model/effort control applies to maintenance too.

Real-use outcomes reveal problems and candidate improvements. Controlled comparisons with isolated memory state can test a causal benefit. Keep diagnostic cases separate from held-out evaluation when claiming generalization. Trace/case exports require the established project visibility and sharing authority. Generic mechanisms ship with every seed; private histories and evaluation outcomes do not.

## Current implementation and dependency order

Verified: current `bin/factory` at local main `d627bb2755ad49865f798bcb095800ddd2ad1ced` builds worker input from the frozen ticket, common prose, provider-specific skill text/instructions and previous round failures. Its `build_worker_prompt` source does not implement the record, packet or delivery contract proposed here. The preserved [current code map](prior-design/cookbook-current-code-map.md) covers related lifecycle changes. Runtime behavior has not been reproduced in this design step.

| Proposed unit | Existing responsibility retained/replaced | Depends on | Future acceptance interface in a generated project |
|---|---|---|---|
| Proposal validator and registry | Replace direct narrative as lifecycle authority; keep readable content | Instance/attempt binding, protected artifact capture, store | `python3 -m unittest discover -s .loam/factory/tests -p 'test_memory_proposals.py'`: spoofed authority, duplicate-key/ID conflict, unavailable source and stale predecessor |
| Assessment and activation | Extend independent evidence review to memory | Review policy, source registry, correction generations | `python3 -m unittest discover -s .loam/factory/tests -p 'test_memory_assessment.py'`: generalization cannot use narrow route, unsupported advice stays candidate, correction after assessment blocks activation |
| Packet builder and renderer | Replace unversioned prompt concatenation and personal shared-memory dependency | Admitted task/role/profile, source eligibility | `python3 -m unittest discover -s .loam/factory/tests -p 'test_context_packets.py'`: required-item coverage, contrary evidence, no governing elevation, independent-role exclusions, distinct rendered payload digest |
| Delivery and recovery observations | Replace implicit prompt-sent means supplied/read assumptions | Native bridges, durable actions, raw event capture | `python3 -m unittest discover -s .loam/factory/tests -p 'test_context_delivery.py'`: ack without inclusion, failed source read, reconnect without dispatch, correction races, stale queue, duplicate/out-of-order observations |
| Real-use observation and evaluation-case capture | Extend debriefs without heuristic rule promotion | Exact packet/output/check identities and visibility | `python3 -m unittest discover -s .loam/factory/tests -p 'test_memory_use.py'`: feedback cannot bind to rerun, missed retrieval has no fictional delivery, self-report does not become proven benefit |

These future fixture files do not exist as a result of this document and were not run. Canonical test source belongs in `seed/.loam/factory/tests`; use that discovery path in Loam source. The runner must verify an expected nonempty case population. This proposed Python fixture interface does not select the engine runtime language.

The smallest extension to the existing proving slice is a single source-backed proposal, assessed activation, packet to a fresh worker, an injected disconnect/reconnect with no duplicate invocation, a correction before replacement delivery, and an exact-output usage observation. Then run the same contract separately with each native bridge under later authorization. Native inclusion, isolation, queue behavior and actual usefulness need live evidence after implementation and installation.

## Source grounding and next choices

Verified source basis: the saved cookbook audits retain pinned originals, detailed read scope and known gaps. This step rechecked the original [OpenAI personalization notebook](https://github.com/openai/openai-cookbook/blob/9aad95f0aa4f8e12991ef9b9201df28747860bfc/examples/agents_sdk/context_personalization.ipynb) and [Claude context-engineering cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools). Their scoped note-taking and context strategies inform the proposal/packet separation. Their API tutorial code is not a native-host contract.

The [Codex cookbook audit](prior-design/cookbook-codex-audit.md) identifies failed consolidation that promotes temporary notes, output/feedback identity problems and missing true artifact dependencies. The [Claude SDK audit](prior-design/cookbook-claude-sdk-audit.md) identifies unversioned background summarization and incomplete continuity checks. Explicit revision binding, protected authority, assessment routing and correction ordering are Loam engineering recommendations that address those gaps, not features claimed to exist in the recipes.

Recommendation for discussion: permit policy-authorized self-assessment only for narrowly evidenced observations; use fresh review for causal, generalized, contested or consequential advice. Start with deterministic role-specific packets plus native continuation when compatible. These are the main choices refined here. Exact physical tables, renderer implementation and live capability admission remain further engineering work.

Next: specify the evaluation manifest and activation transaction in enough detail to test useful memory and method improvement during real tasks, including how harmful lessons are corrected promptly. No runtime implementation is authorized by acceptance of this design alone.
