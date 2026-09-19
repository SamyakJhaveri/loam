# Memory and loop engineering: implementation contract

Status: the user has accepted the memory and loop architectural direction in this document. Recommendation wording below records its design origin. This is a design document, not an implemented interface. Runtime language, exact schema names and native capability guarantees remain subject to later design/prototypes. Accepted requirements are separated in [decision-delta.md](decision-delta.md).

Critical point: retained interpretations and generated adaptations must not silently acquire authority over project instructions, permissions or acceptance.

## What this step resolves

Recommendation: build shared project memory on the accepted SQLite and artifact infrastructure. Preserve native context management. Add a separately admitted improvement workflow that can diagnose and evaluate changes to how the factory works. All reusable services, generic methods, correction machinery and mechanical fixtures ship in the managed seed engine; every project starts with empty local stores.

This document supersedes the earlier memory draft's open backend question and file/index ownership ambiguity. It also supersedes root-only future `bin/tests` locations in historical loop and record drafts: generated-project fixtures belong under `.loam/factory/tests`, with canonical source under `seed/.loam/factory/tests`. The preserved snapshots remain unchanged historical records.

## Credible memory approaches

| Approach | Benefit | Limitation | Recommendation |
|---|---|---|---|
| Native memory alone | Minimal extra mechanism; preserves host features | Does not establish a common source, correction or recovery contract across providers and independent generated projects | Keep as an optional native aid; insufficient as the shared factory store |
| Shared files with SQLite lifecycle and dependency metadata | Readable evidence, explicit ownership, corrections and cross-provider context; uses the accepted local infrastructure | Requires a capture/review/retrieval contract and artifact consistency handling | Choose initially |
| Semantic retrieval service or knowledge graph as the primary memory | Can retrieve conceptual relationships beyond exact wording | Adds indexing, synchronization and deployment obligations; retrieval relevance does not establish authority or truth | Consider as a derived index after measured retrieval failures |

## Ownership and record model

Recommendation: the owning supervisor service is the sole writer of authoritative lifecycle metadata. Workers submit proposals and artifacts through the existing proposed typed control boundary. A memory module shares that boundary; it is not another scheduler or an independently writable state database.

| Record | Minimum content | Meaning |
|---|---|---|
| Evidence observation | Project, producer/run, source locator, source revision or content digest, captured body, actual read span, acquisition/access status | What was observed. A failed retrieval and an empty successful result remain distinct. |
| Claim or finding | Statement, supporting and contrary evidence, method, scope and unresolved limits | An interpretation to assess. A citation or digest proves neither truth nor relevance. |
| Lesson revision | Stable identity and revision, situation, attempted action, observed outcome, proposed advice, evidence, applicability and invalidation conditions | Advisory knowledge that may help later work. Include verified failed approaches and negative findings. |
| Assessment | Record revision, envelope validity, semantic support judgment, reviewer/profile, reasons and evidence | Separate mechanical checks from judgment. Unknown support remains explicit. |
| Decision reference | Canonical authored source, exact admitted source identity, accepting authority, supersession | Connects existing project decisions without creating a second writable decision document. |
| Context packet | Work/profile revisions, included record revisions, required constraints, excerpts, selection reasons, conflicts, delivery observations | Rebuildable context for a particular attempt. It is not a new source of authority. |
| Correction/retraction | Affected identities, actor/authority, reason, replacement or deletion scope, generation | Invalidates obsolete uses and prevents delayed extraction from restoring them. |

Recommendation: SQLite owns record identities, revision heads, lifecycle, dependency edges and review/activation receipts. Substantial immutable bodies live in artifact files under the accepted artifact protocol. Human-owned `CONTEXT.md` and ADR files remain canonical authored sources. The database records what exact version was admitted; a worker edit or Git commit alone does not authenticate approval of a changed decision. Changed decision bytes require the established authority/revision process before governing new work.

Publish and verify an artifact before committing a ready reference to it. The database transaction writes the record revision, dependency links and corresponding event together. An artifact without a committed reference is an orphan to reconcile; a missing referenced body makes dependent evidence unavailable. Do not manufacture an empty replacement. The artifact store's existing atomicity, retention and recovery rules still apply.

Recommendation: keep lifecycle separate from support and applicability. Lifecycle is `candidate`, `active`, `rejected`, `superseded` or `retracted`. An active historical record can still be well supported but inapplicable to current code. A high search score cannot make it eligible. Do not require every observation to carry every model/tool field; include conditions when they affect the claim.

## Capture, review and retrieval

Recommendation: capture useful observations during research and execution, not only at shutdown. A lead or specialist can propose a lesson at a checkpoint, after a failure or after an outcome is known. The proposal names both what happened and what is inferred. A successful ticket alone does not validate every explanation in its debrief.

The default proposed policy allows ordinary advisory lessons to become active after configured evidence and scope review without a new human approval for every note. The review uses the user's admitted model and effort policy. No universal multi-agent ceremony is required for a small, directly evidenced note. Material generalizations and contested claims need the stronger review declared by the method. Candidate notes remain searchable explicitly as unreviewed material; they do not appear as established advice by default.

Rules, accepted engineering choices, model/effort settings, permissions and acceptance criteria follow their own admission authority. A lesson can propose a change to them, but cannot activate it. A remembered user preference retains the original user-source provenance and scope; an agent inference must not be relabeled a user instruction.

Proposed retrieval sequence:

1. Resolve the current work/profile and mandatory project constraints from admitted authority. These form a required set, not a relevance-ranked search result.
2. Filter advisory records by project, permitted visibility, lifecycle, evidence availability and task-relevant applicability. Unknown applicability is explicitly qualified historical context, not current support.
3. Search eligible records and linked original sources with ordinary lexical search and metadata filters. Include pertinent failures and contrary evidence. The native lead can expand the search.
4. Construct an inspectable packet with exact record revisions, excerpts and reasons. Keep governing context separate from advisory/source material through supported native message channels.
5. Recheck correction generations and source dependencies before delivery. Record packet prepared, delivered and observable inclusion separately. Supplying a pointer does not establish actual source inspection.

Recommendation: begin with deterministic filtering and ordinary search. If ranking misses a critical exception, the repair may be a required constraint binding or better scope metadata, not a vector database. Evaluate richer retrieval only against observed misses. Required context cannot silently be dropped to fit a size budget; partition work or stop preparation with the missing coverage identified. Advisory material can be trimmed with an omission record and source access retained.

## Correction, forgetting and concurrent work

Recommendation: correction makes affected records ineligible immediately in authoritative metadata. Derived indexes can rebuild later because every read rechecks current eligibility. Dependency closure identifies summaries and packets based on the corrected record. A consolidator records its input revisions and correction generation; activation compares those inputs with the current store. A mismatch retains output as stale, unpromoted work and requires recomputation or review.

A packet waiting for delivery must be rebuilt or filtered after a relevant correction. Already delivered content cannot be unread. Record authenticated steering for affected attempts, replace the usable context, and recheck any claim or acceptance evidence materially dependent on the corrected source. Do not invalidate unrelated checks merely because a retrieved advisory note changed. If the host cannot establish the required correction boundary, reconcile and restart affected execution under the native adapter contract.

Source freshness is dependency-specific. An unrelated repository commit need not invalidate a lesson about an unchanged function. A same-length edit to a depended-on source can invalidate it. For external sources, retain the actual captured content/version when permitted; a later fetch can observe different evidence. Unavailable originals remain unavailable rather than silently substituted.

Forgetting applies to permitted raw content and derived copies, including summaries, indexes, exports and controllable native projections. Retain only permitted non-content tombstones to prevent resurrection. Name any backups or native caches outside actual deletion control; do not claim complete erasure from a successful local file deletion. Normalize paths and enforce actual filesystem boundaries, including symlinks, rather than prefix-string tests.

Project memory is local by default. Sharing selected knowledge across projects is an explicit export/import with provenance and visibility checks. Import starts as foreign evidence/candidate knowledge, not an inherited instruction. Seed updates carry schema and machinery, never another project's memory.

## Native context and shared memory

Recommendation: Claude Code and Codex retain their own conversation, compaction and native memory behavior where admitted. Loam supplies the same source-linked packet contract through each supported native bridge. It does not edit undocumented native memory files or require one provider's private memory directory to resume the other.

Native continuity answers what this conversation has been doing. Shared project memory answers what later work might need to know and why. Supervisor state answers what is running and what is complete. A summary cannot recover exclusive execution ownership or certify a result.

Profiles must establish the required project-isolation and private-data boundaries before managed use. Unknown native inclusion is not a successful read receipt. Actual context inclusion, controllable native memory scope and correction delivery need provider probes; source documentation alone does not prove them on the installed host.

## The loops and their interfaces

| Loop | Owner | Inputs and outputs | Boundary |
|---|---|---|---|
| Native thinking | Lead and admitted native collaborators | Current objective, tools, context and findings; produces plans, artifacts and proposals | Chooses reasoning and exploration; cannot waive required work or accept itself |
| Durable work progression | Deterministic supervisor | Admitted work, native observations, artifact/check receipts and steering; produces stage transitions and acceptance | Owns lifecycle and evidence completeness; does not establish scientific truth by counting votes |
| Evaluated improvement | Separately admitted maintenance work | Failure evidence and proposed asset revision; produces evaluated recommendation and possible activation | Cannot change its own governing evaluator or silently modify an active run |

Recommendation: native internal planning remains flexible. Adding a research branch inside an already admitted adaptive method revises the plan and expected obligation population. Replacing an agreed experimental protocol, required result, execution profile or admission-critical capability creates successor work inputs and readmission. Dynamic required children retain the pre-dispatch admission and actual-native-identity binding already designed.

The progression contract remains `admit → prepare → execute → reconcile writers → check → review → accept`. A valid behavioral failure can request repair. A check execution error, malformed review or missing source gets the appropriate retry/incomplete classification, not an assumed implementation defect. A cap stops effort without accepting unmet work. Later steering and uncertain execution use the existing barriers and reconciliation rules. One continuation owner prevents the supervisor and a native goal from launching competing work.

## Evaluated improvement as concrete work

Recommendation: a recurring failure, new capability or human suggestion creates a diagnosis candidate. No background schedule is necessary for the initial implementation. An explicitly admitted improvement item uses ordinary work, limits and evidence infrastructure.

| Proposed operation | Required inputs | Result |
|---|---|---|
| Diagnose | Exact run/output identities, source-linked traces, environment and criteria | Cause hypothesis with supporting/contrary evidence and uncertainty |
| Propose adaptation | Diagnosis, target asset revision, small reviewable diff and predicted benefit | Unapproved candidate method/prompt/tool/skill change |
| Admit evaluation | Baseline and candidate hashes, fixed case population and inputs, judgments/checks, profiles and comparison method | Immutable evaluation manifest and stage obligations |
| Record comparison | Actual baseline/candidate executions and output identities, complete outcome population | Comparison evidence, retaining missing/error/fail/pass distinctions |
| Assess | Manifest and complete evidence | Supported, rejected or inconclusive recommendation |
| Activate | Required assessment and authority, expected current predecessor revision | New immutable asset revision for future admissions |
| Roll back | Prior admitted revision, target scope and reason | New activation event restoring that revision for future work |

Classify causes before changing a prompt: method/design problem, native execution choice, environment/tool failure, invalid/changed objective, or insufficient evidence. A repeated grader label is only a trigger to investigate. Preserve a rejected improvement and the reason it did not help.

An evaluation manifest pins case identities, inputs, criterion/evaluator/helper revisions, baseline and candidate assets, native profiles, context packets, comparison method and allowed execution scope. Cases used for diagnosis/tuning are distinct from held-out assessment when generalization is claimed. Skipped cases remain missing; a smaller returned population is not a better score. Bind feedback to the exact output the user saw. A rerun creates a different execution.

Baseline and candidate executions receive equivalent immutable starting inputs in separate evaluation workspaces and memory namespaces. The manifest identifies each arm's initial memory snapshot, permitted native continuity and mutation/reset rules. Neither sees the other's generated lessons, modified fixtures or private run outputs. For a temporal memory evaluation, each arm starts from its own copy of the declared initial store and receives the same ordered source events; the tested difference is recorded explicitly. Learning can persist within its declared sequence but cannot transfer between arms. Evaluation-created lessons stay outside ordinary project memory unless separately reviewed and imported. Protected evaluators and reference judgments remain outside candidate write authority. Uncontrolled native carryover makes the comparison qualified or inadmissible for the claimed conclusion; resetting a directory alone does not prove isolation.

For semantic evaluations, record the declared evaluator judgment and its limitations separately from structural validity. No schema can prove a memory is useful. The comparison must include harmful carryover and missed corrections as well as successes. Keep selected models and effort fixed unless the user explicitly authorizes changing them. Native maintenance agents are subject to the same policy as ticket workers.

Project configuration/extensions are the default adaptation targets. A managed-engine change is an explicit local fork or a separate contribution to Loam, not an accidental patch during learning. New assets govern future admissions. Active runs retain frozen inputs until ordinary steering/readmission. A discovered serious validity defect can block affected evidence immediately without waiting for a replacement asset. Shared Loam promotion does not automatically export a project's private traces.

Accepted clarification: the session lead Astra or Fable makes the improvement-adoption decision within the user's authorized scope. A reviewer, advisor or automatic score cannot substitute for that decision. Immediately before activation, the supervisor transaction revalidates the actual lead/session binding, the assessment's current eligibility, source/criterion dependencies, correction generations, authorizing decision and expected predecessor asset revision. Without an eligible lead decision, the candidate remains pending. A correction or evidence loss that invalidates the comparison blocks activation even when the target asset has not changed. Rollback similarly checks that the selected historical revision is presently admissible; a prior activation receipt alone does not establish current validity. A stale assessment remains historical evidence and requires reassessment, not automatic promotion.

## Current code and proposed changes

Verified source baseline: `d627bb2755ad49865f798bcb095800ddd2ad1ced`. These findings are source inspection, not runtime reproduction.

| Existing component | Retain | Change and dependency |
|---|---|---|
| `seed/.agents/skills/catchup/SKILL.md` | Inspect Git and handoff freshness before work | Add shared project state/evidence retrieval and provider-aware native context; remove personal Claude memory as the shared prerequisite. Depends on context packet service. |
| `docs/agents/domain.md` | Canonical project vocabulary and ADRs | Bind source identity and admitted authority, avoid a competing decision copy. Depends on evidence registration. |
| `bin/factory` main loop | Bounded attempts, frozen inputs, useful checks/review roles | Replace text-only check success, cap-to-publication and filename resume with durable stage/evidence transitions. Depends on accepted state/adapter design. |
| `bin/factory.d/_common.md` | Explicit task and review guidance | Generate role/context from admitted method/profile; remove universal fresh-round and hardcoded helper assumptions. Depends on native profile validation. |
| `docs/factory/LOOP.md` learning guidance | Debrief observed trouble | Repeated failure labels propose diagnosis; evidence and a fixed evaluation manifest govern adaptations. |
| `bin/factory` grader evaluation path | Existing replay fixtures as candidate test data | Fix expected case population and missing-input treatment; bind exact evaluation inputs and distinguish semantic from mechanical checks. |

## Example across sessions and providers

Illustrative flow, not executed in this session:

1. A freshly generated research project initializes its factory store. An inquiry investigates how experiment reports can detect obsolete data. It captures source snapshots, independent reports and failed path/mtime approaches while the investigation runs.
2. An experiment changes data without changing the path or length. Its raw output supports a scoped conclusion. A decision and implementation ticket adopt a declared content/dependency identity contract. Checks and independent review accept the actual candidate.
3. A debrief proposes: for this report format, validate the declared preprocessing inputs as well as the data content. Review checks the exact experiment and limits before making this advisory lesson active.
4. A fresh session using the other native provider retrieves the admitted decision, lesson and contrary evidence. It can inspect the original experiment; it does not need the first provider's personal memory.
5. The user corrects which preprocessing settings affect scientific meaning. The correction supersedes the old advisory wording and triggers reassessment of materially dependent work. A delayed consolidation based on the old revision cannot reactivate it.
6. An improvement item proposes adding an input-dependency question to the experiment method. Baseline and candidate are evaluated on fixed cases, including a case where an irrelevant formatting setting must not invalidate a result. An inconclusive or harmful change remains unactivated. A supported change still needs the configured activation authority.

## Source-to-design grounding

Verified: the following originals and cached source sections inform this step. Reports retain the broader read scope. Recommendations above are Loam engineering synthesis, not a claim that these tutorials implement the proposed factory guarantees.

| Source | Borrow or adapt | Do not import unchanged |
|---|---|---|
| [Claude context engineering cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) and [context engineering article](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Distinguish compaction, tool-output clearing and persistent memory; preserve useful context and test retained information | API examples as native-host guarantees; treating a fresh external fetch as historical evidence |
| [OpenAI context personalization](https://github.com/openai/openai-cookbook/blob/9aad95f0aa4f8e12991ef9b9201df28747860bfc/examples/agents_sdk/context_personalization.ipynb) | Temporary candidates, scoped durable notes, deterministic rendering and temporal evaluation | Invalid consolidation promotes all temporary notes; recency alone resolves conflicting claims; hidden smaller-model defaults |
| [OpenAI reliable memory and compaction](https://github.com/openai/openai-cookbook/blob/9aad95f0aa4f8e12991ef9b9201df28747860bfc/examples/agents_sdk/building_reliable_agents_memory_compaction.ipynb) | Preserve cited investigation artifacts separately from reusable workflow advice and active context | Replacing the native host with the tutorial runtime |
| [Claude remembered preferences](https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/managed_agents/CMA_remember_user_preferences.ipynb) | Scoped stores, read-only shared guidance, correction and new-session recall | Mandatory hosted memory service for every seed |
| [Claude memory example](https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/tool_use/memory_cookbook.ipynb) | Persistent observations and later reuse | Its recorded false concurrent-write diagnosis; repetition as validation; unsafe path/root guards |
| [Long-running harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Retain useful continuity; evaluate whether scaffolding still helps | Universal fixed worker resets or assuming another model name guarantees independence |
| [Loopy debrief](https://github.com/Forward-Future/loopy/blob/75966cbd572a4185064971c9fe5e9c52e8f8456d/skills/loopy/references/debrief.md) | Receipt-based diagnosis, minimal proposed change and honest inconclusive findings | Multi-run generalization from a single trace |
| [Agent Apprenticeship verifier](https://github.com/ray-r-ren/agent-apprenticeship/blob/4beafff2ff41da7d97a4faee9b516ccde466fb4b/src/agent_apprenticeship_trace/verifier.py) | Structural validity distinct from semantic verification that was not run | Treating nonempty evidence references as grounded claims |

## Smallest proof and future runnable checks

Recommendation: prove restart, correction and learning boundaries in an independent generated project before adding sophisticated retrieval. A fake adapter can prove contracts; later native runs are required to establish provider behavior and useful learning. No commands below have been implemented or run.

All fixture files are proposed under `seed/.loam/factory/tests` in Loam source and `.loam/factory/tests` in generated projects. Python here names a proposed standard-library fixture runner, not a decision about the engine language.

| Change | Depends on | Future generated-project acceptance command and decisive case |
|---|---|---|
| Memory capture and lifecycle | Store/artifact protocol, authority | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory_contract.py'`: capture source and candidate, review, restart, retrieve exact evidence; malformed consolidation retains candidates without promotion |
| Retrieval and correction | Lifecycle/dependencies, typed ingress | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_memory_correction.py'`: wrong-project, same-length source edit, conflicting lesson, correction-before-delivery and delayed consolidation cannot supply obsolete current support |
| Work progression | Native adapter, isolated checks | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_loop.py'`: silent nonzero check, malformed review, missing child and cap cannot accept |
| Recovery | Ownership, artifacts and delivery history | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_recovery.py'`: restart in checking; live descendant and uncertain goal prevent competing dispatch |
| Evaluated improvement | Diagnosis, frozen manifest, evaluation context | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_evaluation.py'`: missing hard case, altered evaluator/helper, wrong output and unavailable semantic judgment cannot establish favorable promotion evidence; a baseline-created solution lesson is invisible to the candidate unless independently learned or explicitly in its initial state |
| Activation and rollback | Evaluation, configured authority, asset revisions | `python3 -m unittest discover -s .loam/factory/tests -p 'test_factory_improvement.py'`: rejected change stays inactive; source correction after assessment blocks activation; activation affects future admissions only; rollback retains history and rechecks current eligibility |

The complete mechanical slice generates a project independent of the Loam checkout, admits an inquiry/ticket fixture, captures evidence, injects a check error and restart, accepts only complete current evidence, retrieves a reviewed lesson after restart, retracts it, rejects delayed consolidation and records a rejected method adaptation without changing policy. Source fixture commands use `-s seed/.loam/factory/tests`. Test discovery must also assert an expected nonempty case population; a runner's successful zero-test exit is not acceptance.

Later quality evaluation compares task sequences with no retrieved memory, eligible memory and deliberately stale/conflicting memory. Hold model/effort fixed; record mistakes avoided and introduced, applicable evidence recovered, corrections honored, unresolved disagreement, task outcomes and human correction required. Record context and effort as diagnostics. Do not optimize memory count or infer causal improvement from a citation or a satisfied model self-report.

## Open choices and limitations

Accepted direction: activate evidence-reviewed advisory lessons under project policy without approving every note; require the separate configured authority for governing adaptations. Exact review depth should depend on uncertainty and impact. Detailed routing is refined in [memory-records-and-delivery.md](memory-records-and-delivery.md).

Assumption: the native bridges can provide the required isolated context and correction observations. Confirm with bounded live probes under later runtime authorization. Mechanical fixtures cannot prove semantic usefulness, native cancellation, crash durability or private-cache erasure. Detailed schema/index choices and production deletion coverage remain design work.

The user also requires evaluation after implementation and installation throughout real project work. Capture useful and harmful memory application, missed retrieval, corrections and task outcomes with exact record/run identities. Use that experience to propose evaluated changes; observational feedback alone does not prove causality. No schedule, model job or automatic policy change is authorized merely by this requirement.

Next: refine record schemas and context delivery against this lifecycle, then develop the evaluation manifest and activation transaction in detail. No runtime implementation is authorized by this document.
