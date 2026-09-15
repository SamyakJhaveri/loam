# NATIVE-09: Capture and assess source-linked project memory

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[CORE-08: Reconnect to the original host and settle captured results once](08-core-08.md), [NATIVE-02: Account for dynamic required work and independent review](11-native-02.md), [CORE-09: Back up and restore local history through a durable external barrier](09-core-09.md)

## What it delivers

A task can propose a source-backed lesson, assess its support and scope, and retain an active advisory revision for later work. A narrow observation can follow configured ordinary assessment without making every note wait for a human. Governing decisions, permissions and model choices never become writable lesson fields.

## Current behavior and source packet

Verified from the accepted memory design and current `build_worker_prompt` inspection: existing prompt assembly uses ticket/common/native skill prose and prior failures, without the proposed SQLite memory/assessment registry. Human project context and ADRs remain authored sources.

Read `docs/architecture-working/memory-loop-engineering.md` (ownership, capture/review and correction), `memory-records-and-delivery.md` (proposal envelope, assessment routing, artifact and authority rules), `decision-delta.md` P-MEM choices, `prior-design/cookbook-codex-audit.md` (failed consolidation and source identity), `prior-design/cookbook-claude-sdk-audit.md` (background summarization), `docs/agents/domain.md`, `bin/factory` (`build_worker_prompt`) and S2 artifact/store contracts. Read relevant original sections of https://github.com/openai/openai-cookbook/blob/9aad95f0aa4f8e12991ef9b9201df28747860bfc/examples/agents_sdk/context_personalization.ipynb and https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools; their tutorial APIs do not define native authority.

## Canonical files and bounded work

Create `seed/.loam/factory/src/contracts/memory.ts`, `src/memory/records.ts` and `tests/memory/records.test.ts`; add the next versioned migration under `seed/.loam/factory/migrations/` using S2's migration naming contract. Extend the existing store/transaction ingress rather than creating a second writer. Freeze memory revision, evidence span/access status, support/contrary links, applicability, lifecycle, assessment, dependency, correction and tombstone contracts for NATIVE-10.

Separate observations from claims and advisory lessons; separate lifecycle from semantic support and current applicability. Publish/verify immutable artifact bodies before committing ready references. Missing referenced evidence is unavailable, not an empty substitute. Context/ADR decisions retain their canonical authored source and admitted identity; a source edit or worker role label cannot approve new governing instructions. Ordinary supported observations may use configured assessment, while causal/generalized/contested/consequential claims need the declared independent review route. Recheck source eligibility, predecessor and correction generation at assessment/activation. An evaluator here may assess an ordinary lesson under policy; it cannot approve a method improvement or change governing authority.

Apply the new schema to an existing registered scratch store through CORE-09 protected external maintenance-marker authority, not only fresh-store initialization. The records fixture includes interruption before/after migration application, preserves prior evidence and pending barriers, and refuses ordinary startup until the exact migration is reconciled. NATIVE-11 consumes the same inherited migration authority for its schema.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/memory/records.test.js`.

- [ ] A scratch task publishes actual evidence, proposes a scoped observation, records support assessment and activates only the eligible advisory revision; raw source spans and contrary evidence remain inspectable.
- [ ] Spoofed authority, conflicting duplicate identity, duplicate-key envelope, foreign project visibility, stale predecessor, missing body/source and forged user-preference provenance fail their intended boundary.
- [ ] Unsupported or generalized advice cannot pass the narrow self-assessment route. Unknown support remains candidate/qualified, not established advice.
- [ ] Correction between assessment and activation blocks the old revision; failed consolidation preserves unpromoted work without append-all fallback. Orphan body and missing committed body recover truthfully.

This ticket ends at an assessed record and correction-ready schema. NATIVE-10 owns role-specific retrieval, native delivery, forgetting propagation and post-installation use observations. No embeddings, graph service or policy self-modification belongs here.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **store**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `5664d1d7efec22338c3a4ce77f356262537d9850f955ac00a030a7c19c6fc775`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/memory-loop-engineering.md`
- `docs/architecture-working/memory-records-and-delivery.md`
- `docs/architecture-working/prior-design/cookbook-codex-audit.md`
- `docs/architecture-working/prior-design/cookbook-claude-sdk-audit.md`
- `docs/agents/domain.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
