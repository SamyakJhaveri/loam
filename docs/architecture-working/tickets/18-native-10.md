# NATIVE-10: Deliver corrected memory to fresh native work and record real use

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[NATIVE-09: Capture and assess source-linked project memory](17-native-09.md), [NATIVE-03: Bind Claude root decisions, Workflow and advisor evidence](12-native-03.md), [NATIVE-04: Bind Codex root decisions and native consultation](13-native-04.md)

## What it delivers

A fresh native worker receives current mandatory constraints and relevant assessed advice. A later correction immediately removes stale eligibility, updates affected execution safely and prevents a delayed summary from restoring old advice. Real task feedback links to the exact output the user saw.

## Current behavior and source packet

Verified from the current catchup source and memory design: Claude personal-memory lookup and unversioned prompt concatenation do not implement shared source-linked packets, correction generations or prepared/sent/consumed observations.

Read `docs/architecture-working/memory-records-and-delivery.md` (packets, role matrix, delivery, correction races and MemoryUseObservation), `memory-loop-engineering.md` (retrieval, forgetting, native context and ongoing evaluation), `native-profile-and-lead-binding.md`, `prior-design/cookbook-practice-registry.md` (memory/context/source coverage cases), `prior-design/native-claude-evidence.md`, `prior-design/native-codex-evidence.md`, `seed/.agents/skills/catchup/SKILL.md`, `bin/factory` (`build_worker_prompt`) and NATIVE-09 schemas. Use originals named by the memory audits as bounded context-engineering references, not native memory-file recipes to copy.

## Canonical files and bounded work

Create `seed/.loam/factory/src/memory/context.ts`, `src/memory/delivery.ts` and `tests/memory/correction.test.ts`; extend `src/contracts/memory.ts`, `src/memory/records.ts` and the existing provider delivery interfaces only as needed. Include a declared nonempty real-use observation subset in the same focused fixture. Use fixed current constraints first, then project/visibility/lifecycle/evidence/applicability filtering and ordinary lexical retrieval of advice, failures and contrary evidence. Required constraints cannot be silently trimmed to fit a budget.

Build immutable role-specific packets and distinct provider-rendered payload identities. Preserve lower-trust provenance; advice/source text never becomes human authority. Independent reviewers exclude producer deliberation/prior favorable reports while retaining adequate original evidence. Separate prepared, authorized, attempted send, transport acknowledgment, queued, consumed/included, actual source access and assessed use. Do not claim understanding; a source pointer or model self-report does not prove inspection.

Correction transactions invalidate affected dependency closure immediately, including queued packets and delayed consolidator inputs. After authorization a delivery may already be in flight; retain the action/barrier and reconcile, never blindly resend on lost acknowledgment. After consumption, authenticated steering/restart re-establishes the supported corrective boundary and rechecks materially dependent evidence. Do not invalidate unrelated checks. Preserve native continuity only after retained-context assessment; provider switching uses shared records, not private memory-file portability. Forgetting reaches permitted derived copies and native projections under actual control, preserves allowed tombstones and reports backup/cache limits.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/memory/correction.test.js`.

- [ ] A generated scratch record is recalled in fresh work, a correction invalidates it, a replacement packet carries current context, and a delayed old summary cannot activate. Test separately through each real adapter after bounded native authorization.
- [ ] Correction before authorization, after authorization with unknown delivery, and after consumption handles its own barrier. Disconnect/reconnect observes the original invocation; duplicate/out-of-order observations do not create extra work.
- [ ] Missing required constraint, stale queue/live descendant, false pointer-read claim, failed source read, policy-elevating renderer and cross-project access fail honestly.
- [ ] Same-length dependency edit invalidates affected advice; unrelated edits do not. Symlink/path-alias forgetting cannot cross permitted roots, and inaccessible backups/native caches are not claimed erased.
- [ ] Record helpful retrieval, harmful carryover, missed retrieval with no fictional packet, correction ignored and source unavailable against exact task/record/output identities. Feedback cannot bind to a rerun; self-reported benefit is not proven causal improvement. Observations may arrive after closure without rewriting acceptance.

No automatic scheduled reviewer, per-access human grading or retrieval service is introduced. NATIVE-11 evaluates improvements; use observations never authorize adoption.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **store, execution**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `0be9dfd77a1e3a1f39021c433e8a7c4dcd167b43a3b72ea4b7bf02347c9a3526`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/memory-records-and-delivery.md`
- `docs/architecture-working/memory-loop-engineering.md`
- `docs/architecture-working/native-profile-and-lead-binding.md`
- `docs/architecture-working/prior-design/cookbook-practice-registry.md`
- `docs/architecture-working/prior-design/native-claude-evidence.md`
- `docs/architecture-working/prior-design/native-codex-evidence.md`
- `seed/.agents/skills/catchup/SKILL.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
