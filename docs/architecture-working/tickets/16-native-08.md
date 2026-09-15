# NATIVE-08: Add cross-project critique and simpler-design review (ASSET-03)

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[NATIVE-05: Catalog every curated method and supporting native asset (ASSET-01)](14-native-05.md), [NATIVE-06: Repair curated planning and review methods (ASSET-02a)](15-native-06.md), [NATIVE-03: Bind Claude root decisions, Workflow and advisor evidence](12-native-03.md), [NATIVE-04: Bind Codex root decisions and native consultation](13-native-04.md)

## What it delivers

A generated project can run a bounded critique swarm with real independent native reviewers, then consider simpler alternatives using the existing plan-review gate. DistBench's provider differences and ParBench's useful review criteria survive in one shared method contract.

## Current behavior and source packet

Verified from `asset-intake/README.md` and `source-manifest.json`: selected DistBench Claude/Codex critique-swarm, Codex agent-team and ParBench elegance-reviewer texts are inactive snapshots, not installed bundles. Loam already has an elegance review concept.

Read `docs/architecture-working/curated-asset-adoption-plan.md` ASSET-03; `asset-intake/source-manifest.json`; `asset-intake/sources/distbench-claude-critique-swarm.txt`, `distbench-codex-critique-swarm.txt`, `distbench-codex-agent-team.txt` and `parbench-elegance-reviewer.txt`; exact original source paths/digests recorded by the manifest; the catalog; the now-shared `agent-team` and `plan-review` sources; `prior-design/cookbook-practice-registry.md` (independent/adversarial/recall); and `delivery-workflow.md`. Inspect support/aliases declared by `benchmark-inventory.json` before asserting delivery.

## Canonical files and bounded work

Create `seed/.agents/skills/critique-swarm/SKILL.md`, `seed/.agents/skills/critique-swarm/references/review-contract.md` and `seed/.agents/skills/plan-review/references/elegance-review.md`. Merge the DistBench team contribution into `seed/.agents/skills/agent-team/SKILL.md`. Create `seed/.loam/factory/tests/assets/review-methods.test.ts` and fill the exact native command/agent wrapper files enumerated by NATIVE-05. Update each catalog conservation mapping with source sections and support dependencies.

Shared review method bodies remain in one canonical home. Claude and Codex wrappers retain only actual supported native invocation; do not substitute Claude team APIs for Codex delegation. Preserve reviewer independence, separate initial findings before cross-critique, contrary evidence, authentic child identity, unresolved handbacks and actual candidate/source links. Simpler-design review compares requirements and available machinery, not deletion counts. It augments existing plan-review criteria instead of creating another mandatory gate. Wider suggested changes remain proposals within task authority.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/assets/review-methods.test.js`; register mandatory `review-methods` execution cases.

- [ ] A shared synthetic plan produces independent reports through each supported native wrapper, followed by explicit critique consuming the original captured reports.
- [ ] A child claiming root/adoption authority, unavailable review, producer/advisor reused as reviewer, missing handback, or fabricated native model observation remains blocked/incomplete.
- [ ] A smaller design that drops a requirement is rejected by the review contract; an evidence-backed simpler alternative is a finding, not permission to modify wider scope.
- [ ] Native-specific wrapper and common body preserve each staged variant's distinctive sections. Real provider capability evidence is separately bounded and must not be inferred from fake reviewers.

No universal different-model policy is imposed on recipients; the Loam implementation campaign still obeys its explicit opposite-model rule. NATIVE-11 alone owns improvement activation.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `968392b3b61b189da39f6b3aff3c04b76e90c87f00b066dfb1665b75a4e6a349`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/asset-intake/README.md`
- `docs/architecture-working/asset-intake/source-manifest.json`
- `docs/architecture-working/curated-asset-adoption-plan.md`
- `docs/architecture-working/asset-intake/sources/distbench-claude-critique-swarm.txt`
- `docs/architecture-working/asset-intake/sources/distbench-codex-critique-swarm.txt`
- `docs/architecture-working/asset-intake/sources/distbench-codex-agent-team.txt`
- `docs/architecture-working/asset-intake/sources/parbench-elegance-reviewer.txt`
- `docs/architecture-working/prior-design/cookbook-practice-registry.md`
- `docs/architecture-working/asset-intake/benchmark-inventory.json`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
