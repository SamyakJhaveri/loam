<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:OPS-06 -->

Stage: S5

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/129 (OPS-04)
- https://github.com/SamyakJhaveri/loam/issues/112 (CORE-09)
- https://github.com/SamyakJhaveri/loam/issues/121 (NATIVE-10)
- https://github.com/SamyakJhaveri/loam/issues/123 (NATIVE-11)

Legacy obligation mapping: MAINT-02 consistent restore, artifact retention and replay history.

## What to build

Verified current behavior: the accepted S2 quiescent backup/pending-restore contract is a predecessor; current root Bash state is not this authority system. Extend that contract to remote ledger, enrollment/generation history, spool/artifact identities, corrections and replay prevention. Backup is complete only after consistent copies and verified manifests are durable. Missing/corrupt registered runner storage is recovery, never empty-runner initialization.

Before replacing a store or ledger, durably record a protected external maintenance/history marker. Stage a fresh history identity with an unresolved-history barrier, preserve old files and reconcile surviving hosts/current generations and post-backup corrections before normal use. Every startup checks the external marker. Crashes before/after replacement resume the same pending transaction. Restored evidence never restores live capabilities; uncertainty leaves admission and recalled-memory use blocked. Database restore does not undo external jobs or actions.

Provide inspection-based cleanup that preserves live/unknown work and referenced evidence. Before deleting a referenced remote artifact, verify a retained copy or require explicit policy abandonment. Keep minimal request identity/body-digest/disposition tombstones after bulky cleanup; remove them only once the whole submission epoch is permanently closed. Backup/restore preserves tombstones/closed epochs so an older ledger cannot reopen submission before history reconciliation. No disconnect-based deletion.

## Canonical changes

Under `seed/.loam/factory/`: `src/store/recovery.ts`, `src/store/maintenance.ts`, `src/execution/job-ledger.ts`, `src/artifacts/retention.ts`, and `tests/store/maintenance.test.ts`. Extend the setup guide with recoverable operator procedures and evidence-only backup import. Reuse S2 external marker machinery.

## Read first

`first-run-ownership-storage-recovery.md`: “Updates, backups and restored history”, “Future acceptance specification”; `remote-execution-contract.md`: “Linux lifetime mechanism”, “Result collection and cleanup”; `maintenance-remote-tickets.md`: MAINT-02 including the replay/closed-epoch paragraph; consolidated S5.

Host assignment: run controller/store/filesystem cases on both Mac and Linux installations; run Linux service/runner-lifetime cases on Linux, and transport/transfer cases from an isolated Mac controller to the Linux runner. Record the exact role and environment for each case. Do not require Linux systemd to run on Mac or infer both-host support from a Mac-only test.

## Future acceptance

After build, run `node --test seed/.loam/factory/dist/tests/store/maintenance.test.js` in scratch recipient and runner instances.

Negative evidence: stale backup, forgotten dispatch, closed-epoch replay, completed-request replay after cleanup, missing registered ledger, corrupt copy, premature artifact deletion and resurrected correction/adoption cannot admit work. Crash injection covers external-marker durability, replacement/history publication and completion; every restart stays in the correct pending reconciliation. Positive evidence: verified backup/restore preserves references and history, current reconciled evidence can resume use, retained copies permit authorized bulk cleanup, and replay returns prior/retired state or closed-epoch refusal with no second launch. Add these cases to the later recipient store population, not only release tests.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **store**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `a24900cbc47947623ab1a20458dfdb1fd5615e1427c45fc0b9984e7f1f1d1975`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/first-run-ownership-storage-recovery.md`
- `docs/architecture-working/remote-execution-contract.md`
- `docs/architecture-working/maintenance-remote-tickets.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/maintenance-step-plan.md`
- `docs/architecture-working/offline-policy-step-plan.md`
- `docs/architecture-working/remote-maintenance-evidence.json`


Approved draft SHA-256: `8336b7b10d3f968150cc0f7c813318f60fff945c6366b16ff12ee289d8923bff`. Full source access must be verified before execution.
