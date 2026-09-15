# NATIVE-02: Account for dynamic required work and independent review

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[NATIVE-01: Admit an explicit native profile and show truthful readiness](10-native-01.md), [CORE-08: Reconnect to the original host and settle captured results once](08-core-08.md)

## What it delivers

A native lead can propose a bounded dependent-work plan, add a justified research branch, collect actual child handbacks and retain missing obligations after the parent stops. An ordinary inquiry can complete with a supported finding, decision, reframing or inconclusive result. It does not have to produce code.

## Current behavior and source packet

Verified from current source inspection: `bin/factory.d/factory-round.js` implements planner/builders/integrator behavior and overlap checks, but an unusable plan can fall back to solo work. Its absent-result convention is not the accepted durable population contract.

Read `docs/architecture-working/delivery-workflow.md` (pattern table, review rules and concrete coordination cases), `prior-design/cookbook-integration-design.md` (method and continuation ownership), `prior-design/cookbook-practice-registry.md` (intent, premises, plans, subagents, async, dynamic, advisor, independent, adversarial, recall, outcome and goals), `prior-design/cookbook-current-code-map.md`, `prior-design/cookbook-long-horizon-audit.md`, `prior-design/cookbook-claude-patterns-audit.md`, `prior-design/cookbook-codex-audit.md`, `docs/research/INDEX.md`, `docs/research/loop-repos.md`, `bin/factory.d/factory-round.js`, `bin/factory.d/_common.md` and `docs/factory/LOOP.md`. Follow original source links for selected bounded-loop/delegation practices.

## Canonical files and bounded work

Create `seed/.loam/factory/src/contracts/coordination.ts`, `src/execution/required-work.ts` and `tests/native/coordination.test.ts`; connect the existing `src/supervisor/lifecycle.ts` and evidence/store transition interfaces. Version typed method revisions, original requirement links, child reservations, actual child binding, dependency artifacts, liveness/handback observations, consultation receipts and review receipts. Freeze shared interfaces before Claude and Codex consumers begin.

Register required work before dispatch. Bind each child/reservation to the effort accounting scope from CORE-10. A replayed or successor child cannot acquire a fresh allowance; retain unresolved child usage and reservation provenance. Add these cases to the coordination population.  Acknowledgment, identity, output and acceptance remain distinct. Replayed/duplicate children cannot satisfy missing siblings. A material method change receives successor inputs and reconciles old execution; a permitted branch cannot erase original obligations. Preserve FAIL versus ERROR/UNAVAILABLE/INCOMPLETE and bounded repair exhaustion. Select one continuation owner; a native goal active or unknown prevents supervisor-driven competing execution. Support goals only when their native/evaluator profile is admitted.

Review receipts bind plan/candidate/criteria/source scope and authentic reviewer identities. Exclude producer/advisor context, scratch material, private persistent memory and earlier favorable reports from fresh independent review. For this campaign enforce actual opposite-model reviews and moving-main invalidation, without silently imposing that campaign policy on every future recipient profile. No automated campaign-management service is required.

Create the shared `tests/native/lead-binding.test.ts` harness and nonempty fake-envelope cases here alongside coordination. NATIVE-03 and NATIVE-04 add their provider populations in separate sequentially integrated worktrees. A required later provider population remains unavailable until implemented; one sibling cannot claim the other provider is proved. Main movement still forces rebasing and fresh review/checks.

## End-to-end acceptance

Future commands, unimplemented and unrun: build the factory, then `node --test seed/.loam/factory/dist/tests/native/coordination.test.js` through fixed admitted test entrypoints.

- [ ] A generated scratch lead admits required children, consumes their exact admitted artifacts and completes only after current checks, required handbacks and review evidence settle.
- [ ] Missing check, repeated confirmed blocker, repair cap, wrong population, parent-before-child completion, late message, unfinished handback and null verifier retain incomplete work.
- [ ] Replay cannot replace a sibling; changed method cannot reuse old receipts; forged child identity and direct unrecorded teammate steering fail managed admission.
- [ ] Advisor enablement alone does not meet an occurrence requirement; redacted advice cannot meet inspectable-content requirements. Producer/advisor reuse as reviewer, wrong admitted review model, changed plan/candidate and main moving before merge invalidate review eligibility.
- [ ] Active/unknown goal ownership blocks competing turns, and native completion does not itself accept work.

This is a fake-envelope contract slice. NATIVE-03/04 implement separate real provider bindings and S6 proves integrated native populations. Dynamic workflows, advisor consultation and multi-agent accounting are assigned now, not deferred wholesale.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `3d5a111d44bbc7e178aed6db93fc8822fcfcc452d6f37c9cf72dcd41b941ff56`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/prior-design/cookbook-integration-design.md`
- `docs/architecture-working/prior-design/cookbook-practice-registry.md`
- `docs/architecture-working/prior-design/cookbook-current-code-map.md`
- `docs/architecture-working/prior-design/cookbook-long-horizon-audit.md`
- `docs/architecture-working/prior-design/cookbook-claude-patterns-audit.md`
- `docs/architecture-working/prior-design/cookbook-codex-audit.md`
- `docs/research/INDEX.md`
- `docs/research/loop-repos.md`
- `bin/factory.d/_common.md`
- `docs/factory/LOOP.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
