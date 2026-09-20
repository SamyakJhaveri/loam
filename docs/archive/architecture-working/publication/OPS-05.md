<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:OPS-05 -->

Stage: S5

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/129 (OPS-04)
- https://github.com/SamyakJhaveri/loam/issues/105 (CORE-04)
- https://github.com/SamyakJhaveri/loam/issues/112 (CORE-09)

Legacy obligation mapping: MAINT-02 reviewed update, drain and partial-activation recovery.

## What to build

Verified current behavior: Copier has update tasks but the proposed admitted controller/runner update transaction is absent. Stage a reviewed release while existing work retains its admitted snapshots. Show changed assets, permissions, dependencies, schemas, target releases and affected jobs. Preserve project configuration/extensions, report explicit forks and same-name conflicts.

Close affected admission under the update transaction before the final idle check. Serialize concurrent submission/queued dispatch with this barrier; activate shared runner/native changes only after affected work drains. No new work may race between the idle check and activation. Record a pending update across controller/runner activation; a crash or incompatible partial deployment blocks new work until reconciliation. Keep a compatible maintenance reader/entrypoint so existing records remain observable and cancellable even when the new-work handshake fails. Retain old installed snapshots for evidence and unresolved effects. Rollback to older code requires current schema/protocol compatibility; incompatible state rollback uses the separate restore path.

## Canonical changes

Under `seed/.loam/factory/`: `src/commands/update.ts`, `src/store/maintenance.ts`, installation admission/selection, runner admission gates, proposed `src/installation/maintenance-reader.ts`, and `tests/installation/update-remote.test.ts`. Update `seed/docs/factory/SETUP.md` and `docs/SYNC.md` with the same staged/drain/reconcile operation. Side-by-side deployment machinery and silent package/native self-updates are outside this initial slice.

## Read first

`remote-job-and-operator-flow.md`: “Update flow”; `maintenance-and-remote-work.md`: “Updates and rollback during long experiments”; `first-run-ownership-storage-recovery.md`: “Updates, backups and restored history”; `maintenance-remote-tickets.md`: MAINT-02; consolidated “S5. Updates, backup and replacement machines”.

Apply each controller/runner schema change through CORE-09 guarded migration under quiescence, verified backup, exclusive ownership and the external maintenance marker. Extend crash tests around schema application and verify that an old incompatible runtime cannot reopen the migrated store. Controller/runner version coordination remains this ticket's responsibility; it reuses rather than postpones the local migration primitive.

Host assignment: run controller/store/filesystem cases on both Mac and Linux installations; run Linux service/runner-lifetime cases on Linux, and transport/transfer cases from an isolated Mac controller to the Linux runner. Record the exact role and environment for each case. Do not require Linux systemd to run on Mac or infer both-host support from a Mac-only test.

## Future acceptance

After build, run `node --test seed/.loam/factory/dist/tests/installation/update-remote.test.js` in admitted scratch installations.

Negative evidence: admission versus final idle check, queued dispatch versus activation, active/unknown affected work, protocol mismatch and incompatible downgrade cannot activate unsafely. Inject crashes before/after each controller/target activation and pending-update persistence boundary. Positive evidence: valid staged changes activate after the closed-admission drain, retain customizations and existing snapshot references, and reopen only after compatible readiness. During partial activation, maintenance status/reconciliation/cancel still reach old records without granting fresh dispatch. Record source and rendered installation identities.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **installation, store**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `c6754201d3717711b4831e34dd2282ba5be6b5e507e8fb43c0b826be3c9e7083`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/SYNC.md`
- `docs/architecture-working/remote-job-and-operator-flow.md`
- `docs/architecture-working/maintenance-and-remote-work.md`
- `docs/architecture-working/first-run-ownership-storage-recovery.md`
- `docs/architecture-working/maintenance-remote-tickets.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/maintenance-step-plan.md`
- `docs/architecture-working/offline-policy-step-plan.md`
- `docs/architecture-working/remote-maintenance-evidence.json`


Approved draft SHA-256: `d28c9bda8f8e468bdecd4073f6b641c67e5e03408e692c9c3dbcf8b4334039ae`. Full source access must be verified before execution.
