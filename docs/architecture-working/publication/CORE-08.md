<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:CORE-08 -->

Stage: S2

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/109 (CORE-07)
- https://github.com/SamyakJhaveri/loam/issues/110 (CORE-10)

## What it delivers
Kill a scratch supervisor after capture but before ingestion, restart it, and recover the original task/host/check without duplicate execution. Existing root controller resume does not establish authenticated current ownership or surviving-child evidence.

## Canonical source changes
Extend `seed/.loam/factory/src/execution/host.ts`, `src/execution/spool.ts`, `src/supervisor/owner.ts`, `src/supervisor/lifecycle.ts`, `src/store/transactions.ts`, `src/checks/run.ts`, `src/commands/status.ts`, `tests/execution/local-recovery.test.ts`, and `tests/store/ownership-recovery.test.ts`. Create local recovery coordination in `src/store/recovery.ts` and extend `seed/docs/factory/SETUP.md` diagnosis.

## Read before planning
`first-run-ownership-storage-recovery.md`: Host connection/control-session replacement, Recovery after supervisor dies, complete crash table. `engine-runtime-and-layout.md`: Process layout and recovery. `prior-design/native-adapter-design.md` and `prior-design/state-design.md`: delivery/reconnect/unknown semantics. Inspect every shared lifecycle/host/store caller landed by predecessors.

Repeat CORE-10 steering/accounting cases through supervisor and host crashes: restored pending barriers retain individual identity; unresolved reservations survive; an old resume cannot clear newer steering; native-shaped reset/overlap observations settle without a fresh allowance. Add these nonempty cases to the named recovery fixtures.

## Acceptance
- Under retained lock and validated existing identity, fresh owner enters recovery. Inventory unfinished DB operations plus protected bootstrap/spool/host records, descendants, sent/queued approvals/native inputs and external effects. Never clear claims/reservations to manufacture readiness.
- Mutual fresh-challenge authentication binds instance/host/original attempt/protocol/runtime/current owner. Host secret proves identity only; protected owner binding separately grants control. Start reconnect observationally; replay/list pending work before durable replacement of control session, invalidation of old session and withdrawal of old unexecuted queue.
- Each command carries session/stable command ID/payload digest/attempt revision/authorization. Reject old control, changed duplicate body and obsolete positive approval; revalidate current owner at dispatch. A raced dispatch remains in-flight. Lost sending acknowledgment means reconciliation, never fresh invocation by default.
- Adopt a complete artifact once with original producer/attempt after exact current candidate/criteria/profile/population/barrier validation. Replay committed receipt without double accounting. Partial evidence errors; repeat check requires proven quiescence and admitted repeat safety/effect reconciliation.
- Host death with surviving child, reused PID, absent socket, lost approval consumption or missing/corrupt artifact preserves unknown execution and quarantines claims. Interruption request is not proof descendants stopped. Spool failure closes relevant authority and retains diagnostic tail; no speculative socket cleanup.
- Future focused commands after build: `node --test seed/.loam/factory/dist/tests/execution/local-recovery.test.js seed/.loam/factory/dist/tests/store/ownership-recovery.test.js`. Kill at capture-before-ingestion and commit-before-ack, partition/rebind control, replay conflicting duplicates and kill host with child alive. Assert same original invocation count, exactly-once settlement, stale authority refusal and visible unknown outcomes on both hosts.

## Exclusions
No native recovery parity claim from fake fixtures, automatic retry/failover, remote SSH runner, backup replacement or accepting stale results after steering.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **store, execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `9e19acf09fccc3ab5a0d75a6df6f424d78d5e85d677afdc67d6fa55eecc9a07a`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/first-run-ownership-storage-recovery.md`
- `docs/architecture-working/engine-runtime-and-layout.md`
- `docs/architecture-working/prior-design/native-adapter-design.md`
- `docs/architecture-working/prior-design/state-design.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/first-run-step-plan.md`
- `docs/architecture-working/runtime-step-plan.md`
- `docs/architecture-working/schema-step-plan.md`


Approved draft SHA-256: `b22f873868eecd7aa5a1cbcd6baa0267e2ca8a7373e44de23f8dc6172586a3db`. Full source access must be verified before execution.
