<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:NATIVE-03 -->

Stage: S3

Implementation lead: Claude Code/Fable 5.1

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/113 (NATIVE-01)
- https://github.com/SamyakJhaveri/loam/issues/114 (NATIVE-02)
- https://github.com/SamyakJhaveri/loam/issues/106 (CORE-03)

## What it delivers

A managed Claude Fable lead performs native work and supported delegation while Loam records root-specific decision proposals, Workflow outcomes and actual advisor observations. Withdrawal and recovery cannot resurrect an obsolete adopt proposal. Implementation owner: actual Claude Code Fable 5.1; plan and finished-work reviewers: actual Codex/Astra in fresh contexts.

## Current behavior and source packet

Verified from current source inspection: `bin/factory` launches Claude with fixed/default model and advisor settings and extracts advisor counts from stream blocks; `bin/factory.d/factory-round.js` runs a Workflow-shaped fan-out. These do not establish the new actual-lead/correction transaction.

Read `docs/architecture-working/prior-design/records-and-transitions.md` (steering/accounting) and `docs/architecture-working/native-profile-and-lead-binding.md` (Claude correlation, split output, replacement/withdrawal and terminal gate), `native-binding-validation.md`, `prior-design/native-claude-evidence.md`, `prior-design/cookbook-claude-sdk-audit.md`, `prior-design/cookbook-claude-patterns-audit.md`, `prior-design/cookbook-integration-design.md`, `docs/research/advisor-and-managed-agents.md`, `docs/research/INDEX.md`, `bin/factory` (Claude launch, raw output and advisor extraction), `bin/factory.d/factory-round.js` and the shared NATIVE-02 contracts. Read original Workflow, dynamic workflow, asynchronous orchestration, specialist-team and native/CMA advisor references identified by those source maps. Recheck supported declarations and primary native docs against S1's selected binding.

## Canonical files and bounded work

Extend the qualified `seed/.loam/factory/src/adapters/claude/index.ts` and create `src/adapters/claude/workflows.ts` and `src/adapters/claude/advisor.ts`; add Claude cases to `tests/native/lead-binding.test.ts` and `tests/native/coordination.test.ts`. Consume the protected host spool and shared admission/coordination contracts. Keep native tools, subagents, context and raw unknown events. Interactive teams, SDK subagents and Workflow are distinct capability surfaces.

Bind the authorized root session/attempt, delivered decision request, actual root assistant identity and corroborating hook evidence. Root `agent_type` labels and body claims do not authenticate authorship. Record actual model/effort observations and incompatible switches separately from requested values. Assemble all correlated output blocks, supersession and retraction events. Eligibility requires a successful correlated terminal result and resolved replacement bookkeeping; a tool callback can stage a proposal but cannot commit before finality. Missing correlation/finality leaves the decision pending. A late post-receipt withdrawal preserves history, blocks affected use and invokes the correction barrier.

Use bounded Workflow under an admitted method with explicit required results. Method-changing correction interrupts/reconciles and creates successor work; do not promise a parent message mutates an active Workflow script. Record actual advisor occurrence, identity and content availability. Keep a supported native advisor or explicitly admitted separate consultation accurately named. Neither becomes independent reviewer or adoption authority.


Connect authenticated native user-message identity to CORE-10 steering ingress without turning worker/source text into user authority. Add provider-specific cases for pause/cancel/revision during completion, stale answer and distinct barrier resolution. Preserve raw usage provenance, aggregation scope and counter epochs. In the named lead-binding/coordination fixtures, test overlapping parent/child totals, reset native counters after resume/clear, unknown usage and shared scope across retries/successors. A bounded real native probe verifies available observations separately; unavailable enforcement cannot be advertised as an exact cap.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/native/lead-binding.test.js seed/.loam/factory/dist/tests/native/coordination.test.js` with nonempty Claude-specific cases.

- [ ] Native-shaped split adopt output superseded/retracted by decline remains pending until valid terminal resolution, including recovery between blocks. Lost reply replays the existing observation/receipt, not a second transition.
- [ ] Child claiming root, copied transcript, missing model/effort evidence, unauthorized reroute, absent prompt correlation, truncation and automatic resumed execution cannot produce eligible authority.
- [ ] Missing/null Workflow child, late handback and changed method preserve required work. Actual advisor evidence satisfies only the admitted occurrence/content requirement; enablement and redaction are truthful.
- [ ] A separately authorized bounded real session on each supported host proves account/profile isolation, root correlation, native delegation, Workflow/advisor behavior where supported, cancellation and replay. Offline fixtures establish mechanics only. An unproven required native route is unavailable and escalates the concrete design gap rather than weakening policy.

Scope ends at authentic current decision evidence and provider-native lifecycle. NATIVE-11 owns the adoption transaction. No Codex binding or new generic reasoning runtime is implemented here.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `26585b7490545538600258068298258c8e2f42c3b2c8b1d114b9cb23ad8ad9b0`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/prior-design/records-and-transitions.md`
- `docs/architecture-working/native-profile-and-lead-binding.md`
- `docs/architecture-working/native-binding-validation.md`
- `docs/architecture-working/prior-design/native-claude-evidence.md`
- `docs/architecture-working/prior-design/cookbook-claude-sdk-audit.md`
- `docs/architecture-working/prior-design/cookbook-claude-patterns-audit.md`
- `docs/architecture-working/prior-design/cookbook-integration-design.md`
- `docs/research/advisor-and-managed-agents.md`
- `docs/research/INDEX.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`


Approved draft SHA-256: `d20a754aae6322f86425335089b6bc8bd0fa4e0d8929477a0dfd6885b7e98fed`. Full source access must be verified before execution.
