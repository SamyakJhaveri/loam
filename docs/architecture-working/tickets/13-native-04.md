# NATIVE-04: Bind Codex root decisions and native consultation

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[NATIVE-01: Admit an explicit native profile and show truthful readiness](10-native-01.md), [NATIVE-02: Account for dynamic required work and independent review](11-native-02.md), [CORE-03: Qualify actual native profile and lead evidence in bounded scratch sessions](04-core-03.md)

## What it delivers

A managed Codex Astra lead retains native tools, continuing threads/goals and supported delegation. Its exact root dynamic-tool call can supply a lead decision proposal, while independent consultation remains advisory. Implementation owner: Codex/Astra; required plan and finished-work review: actual Claude Code Fable 5.1, fresh contexts.

## Current behavior and source packet

Verified from current source inspection: `bin/factory` has a Codex worker route and a configured ledger model label that is explicitly not actual native model telemetry. Personal skill lookup and CLI result handling do not implement the proposed full native app-server contract.

Read `docs/architecture-working/prior-design/records-and-transitions.md` (steering/accounting) and `docs/architecture-working/native-profile-and-lead-binding.md` (Codex envelope and model/effort limits), `native-binding-validation.md`, `prior-design/native-codex-evidence.md`, `prior-design/native-adapter-design.md`, `prior-design/cookbook-codex-audit.md` (SDK source supplement, pending requests and Goals), `prior-design/cookbook-integration-design.md` (direct app-server preference), `prior-design/cookbook-practice-registry.md`, `docs/research/INDEX.md`, `bin/factory` (Codex worker and review routes) and NATIVE-02 contracts. Read the original https://learn.chatgpt.com/docs/app-server dynamic-tool sections and pinned openai/codex/native examples from the audit; refresh against the S1-qualified schema before coding.

## Canonical files and bounded work

Extend the qualified `seed/.loam/factory/src/adapters/codex/index.ts` and create `src/adapters/codex/consultation.ts`; add Codex cases to `tests/native/lead-binding.test.ts` and `tests/native/coordination.test.ts`. Continuously append native events and pending requests to the durable host spool. Route approvals through a separate authority-processing queue so the reader still observes child events while a decision is pending. Reply only under the current durable request/action/revision identity.

Bind dynamic decision requests using the protected native envelope's exact root `threadId`, admitted `turnId` and `callId`. A tree-wide `sessionId`, fork ancestry or body-supplied author label is insufficient. Bind launch/attempt/profile and lead-assignment revision. Track configured model/effort separately from actual supported execution evidence; persisted thread settings are not per-turn telemetry. Missing required policy observations or uncontrolled rerouting blocks dependent authority. Preserve foreign/source/agent message provenance without manufacturing human steering.

Map dynamic work to Codex's actual delegation and the shared method graph, without fictitious Claude Workflow or server-advisor parity. A separate admitted consultation agent supplies actual occurrence/identity and available advice; it is not the lead or independent reviewer. Native goals retain a single continuation owner and lifetime accounting, with supported control required before activation.


Connect authenticated native user-message identity to CORE-10 steering ingress without turning worker/source text into user authority. Add provider-specific cases for pause/cancel/revision during completion, stale answer and distinct barrier resolution. Preserve raw usage provenance, aggregation scope and counter epochs. In the named lead-binding/coordination fixtures, test overlapping parent/child totals, reset native counters after resume/clear, unknown usage and shared scope across retries/successors. A bounded real native probe verifies available observations separately; unavailable enforcement cannot be advertised as an exact cap.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/native/lead-binding.test.js seed/.loam/factory/dist/tests/native/coordination.test.js` with nonempty Codex-specific cases.

- [ ] A current actual-root dynamic call produces eligible evidence; child/fork calls sharing session ancestry, forged workspace envelopes and stale decision turns fail attribution.
- [ ] Pending human approval does not block child event capture; stale replies, duplicate requests with conflicting content and decision tools surviving a lead replacement cannot restore authority.
- [ ] Consultation occurrence is recorded separately from enablement and independent review. Required child liveness, late messages, missing sibling and goal/supervisor ownership remain truthful through reconnect.
- [ ] Replay of captured output does not launch a native turn. Producer re-execution is fresh execution even if ancestry matches; unknown earlier execution cannot cause automatic duplicate dispatch.
- [ ] Separately authorized bounded native proofs on both required hosts establish the profile, model/effort limits, dynamic-tool root attribution, delegation, pending-request observation and recovery. Missing real evidence remains unavailable; fixtures cannot certify native support.

Adoption/rollback are NATIVE-11. Preserve native agency and app-server specifics; do not copy a cookbook Responses/Agents manager as a second reasoning loop.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `cbb7ef6dd01a8d1bfbd13606dcbbf291167b29faff08298f1ac50c9e8f11499d`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/prior-design/records-and-transitions.md`
- `docs/architecture-working/native-profile-and-lead-binding.md`
- `docs/architecture-working/native-binding-validation.md`
- `docs/architecture-working/prior-design/native-codex-evidence.md`
- `docs/architecture-working/prior-design/native-adapter-design.md`
- `docs/architecture-working/prior-design/cookbook-codex-audit.md`
- `docs/architecture-working/prior-design/cookbook-integration-design.md`
- `docs/architecture-working/prior-design/cookbook-practice-registry.md`
- `docs/research/INDEX.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
