<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:OPS-01 -->

Stage: S4

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/105 (CORE-04)
- https://github.com/SamyakJhaveri/loam/issues/117 (NATIVE-05)
- https://github.com/SamyakJhaveri/loam/issues/113 (NATIVE-01)

Legacy obligation mapping: MAINT-01 selected-profile readiness (full ASSET-05 delivery remains later).

## What to build

Verified current behavior: `copier.yml` renders `seed/`; the proposed `seed/.loam/factory/` does not exist. The planned readiness view must consume S1 installation admission and S3 catalog/profile identities. It must not wait for the later full ASSET-05 distribution certificate or pretend that partial readiness is that certificate.

Give the operator one observational status/doctor path that explains whether the selected job can run on this Mac and the enrolled Linux target. Compare exact factory release/protocol, relevant asset identities, admitted executable paths, selected tools/permissions and target requirements. Initially require matching releases. Resolve Linux executables without relying on interactive PATH. An SSH alias identifies a location, never a machine. Missing optional unselected tools do not block unrelated work. Do not install, invoke models, repair state or enable services from status/doctor.

## Canonical changes

Under `seed/.loam/factory/`, extend `assets/runtime-manifest.json`, `src/contracts/installation.ts`, `src/profiles/admitted-view.ts`, `src/commands/status.ts`, `src/commands/doctor.ts`; add `tests/installation/readiness.test.ts`. Add actionable diagnosis to `seed/docs/factory/SETUP.md`. Reuse the catalog preservation map rather than duplicate it.

## Read first

`consolidated-implementation-plan.md`: “S4. Make Mac-led Linux work ordinary” and “Check discipline and existing-ticket coverage”; `maintenance-remote-tickets.md`: “MAINT-01: compatibility and actionable readiness”; `maintenance-and-remote-work.md`: “Keep maintenance small by assigning each thing one home” and “The maintenance cycle”; `remote-job-and-operator-flow.md`: “Initial setup”. Read current implementations of every touched caller after blockers land.

Define the versioned target-enrollment record in `src/contracts/installation.ts` here: machine/runner identity, expected SSH host-key binding, exact release/protocol and resolved executable paths. OPS-02 owns actual protected enrollment and consumes this contract. Until it lands, remote readiness uses declared requirements and synthetic enrolled-target fixtures only; an actual unenrolled target reports unavailable. This ticket cannot claim a live remote readiness certificate before OPS-02 establishes and authenticates that target.

## Future acceptance

After `npm --prefix seed/.loam/factory run build`, run `node --test seed/.loam/factory/dist/tests/installation/readiness.test.js` on admitted scratch installations on both hosts.

Negative evidence: selected missing dependency, native drift, protocol mismatch, changed target identity and absent non-interactive PATH produce a precise unavailable reason without mutation or a paid call. Positive evidence: explicit executable paths and compatible selected inputs produce readiness; an unused optional tool does not prevent unrelated work. Report host identity and actual observed prerequisites separately from live capability proof.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **installation**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `172978fe7ebf52e8973d369c52b0c7e664850173038c05d6e087829b04b6c709`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `copier.yml`
- `docs/architecture-working/maintenance-remote-tickets.md`
- `docs/architecture-working/maintenance-and-remote-work.md`
- `docs/architecture-working/remote-job-and-operator-flow.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/maintenance-step-plan.md`
- `docs/architecture-working/offline-policy-step-plan.md`
- `docs/architecture-working/remote-maintenance-evidence.json`


Approved draft SHA-256: `270d3e3ba783fdf012d0b8f934648830e54165976b2d872fa5ed9d839e6b590f`. Full source access must be verified before execution.
