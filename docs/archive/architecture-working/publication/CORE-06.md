<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:CORE-06 -->

Stage: S2

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/107 (CORE-05)

## What it delivers
A generated scratch project completes explicit setup, survives setup interruption, and reports factory availability separately from selected-provider readiness. Current Copier bootstrap initializes a Git repository but creates no registered factory instance; a missing store in an adopted project must be diagnosed as recovery.

## Canonical source changes
Create `seed/.loam/factory/src/installation/setup.ts`, `src/commands/setup.ts`, `tests/installation/setup.test.ts`; extend `src/contracts/installation.ts`, `src/commands/doctor.ts`, `launcher.mjs`, and `seed/docs/factory/SETUP.md`. Project-owned `.loam/project.toml` and extensions retain their own authority; document pre-factory adoption rather than overwriting prior `.loam` content.

## Read before planning
`first-run-ownership-storage-recovery.md`: Physical homes, Setup as a recoverable operation. `execution-environment-and-bootstrap.md`: Concrete package and setup plan. `prior-design/distribution-design.md` and `prior-design/configuration-design.md`: project ownership/update contracts. Read trusted Git common-directory/environment documentation and current `copier.yml` bootstrap behavior.

## Acceptance
- Trusted Git resolution excludes redirection overrides and binds canonical common-directory filesystem identity. Worktrees share instance; separate clone requires explicit setup. Git hint is nonsecret discovery only, repairable from protected registration; altered/missing hint cannot redirect authority.
- Stable registry setup lock persists pending transaction/instance reservation before state creation; concurrent setup reuses/reports it. Use CORE-04 admission, then create stable instance/lock under that pending setup only; acquire ownership, initialize explicit empty identified schema through CORE-05 creation entrypoint, verify, publish ready registration last.
- Resume same transaction after each crash boundary, validate existing identities/files and never delete/restart. New staging snapshot permitted within pending setup without store; corrupt partial store requires diagnosis. Conflicting/missing registry, deleted config, registered absent DB, moves/copied hints/replaced filesystem objects route to explicit recovery/relocation/import. Total evidence loss must not be called restoration.
- Setup/status never launches research/native workers, schedules work, silently installs from ordinary status, or conflates missing unselected account with factory absence.
- Future focused command after build: `node --test seed/.loam/factory/dist/tests/installation/setup.test.js`. Generated scratch fixtures crash at reservation, runtime publication, store identity and ready publication; concurrent setup, deleted registered DB/config, linked worktree/clone and pre-existing `.loam` cases yield exact resume/refusal outcomes. Run both hosts including configured runtime absent from noninteractive PATH. Final healthy setup has one durable registration and verified empty store.

## Exclusions
No relocation/import automation, restored-history replacement, provider credential copying, new account selection questionnaire or full product readiness claim.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **installation, store**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `95c2f53791369b9300a2af6998ffe2353dac7049608ef8670905f7fa73b18aaf`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/first-run-ownership-storage-recovery.md`
- `docs/architecture-working/execution-environment-and-bootstrap.md`
- `docs/architecture-working/prior-design/distribution-design.md`
- `docs/architecture-working/prior-design/configuration-design.md`
- `copier.yml`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/first-run-step-plan.md`
- `docs/architecture-working/runtime-step-plan.md`
- `docs/architecture-working/schema-step-plan.md`


Approved draft SHA-256: `354a895107b05cb1387f4c912812f3f9c624b7da7b65f45255b5f7218e45fe9e`. Full source access must be verified before execution.
