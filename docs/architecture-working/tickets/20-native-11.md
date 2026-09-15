# NATIVE-11: Evaluate a fixed improvement and record the actual lead decision

Stage: S3

Recommended implementation lead: Codex/Astra

## Blocked by

[NATIVE-03: Bind Claude root decisions, Workflow and advisor evidence](12-native-03.md), [NATIVE-04: Bind Codex root decisions and native consultation](13-native-04.md), [NATIVE-09: Capture and assess source-linked project memory](17-native-09.md), [NATIVE-10: Deliver corrected memory to fresh native work and record real use](18-native-10.md), [CORE-08: Reconnect to the original host and settle captured results once](08-core-08.md)

## What it delivers

The session's actual Astra or Fable lead can examine a fixed comparison and choose adopt, decline or revise within current user authority. A background evaluator PASS or helper recommendation leaves adoption pending. Authorized activation changes future admissions, with truthful rollback and recovery.

## Current behavior and source packet

Verified from current source inspection: `bin/factory` has `run_eval` with grader fixture iteration, verdict comparison and an empty-suite rejection; it skips directories missing required fixture input files. It does not implement isolated baseline/candidate memory, complete comparison manifests or an authenticated root-lead adoption transaction.

Read `docs/architecture-working/improvement-evaluation.md`, `memory-loop-engineering.md` (evaluated improvement), `memory-records-and-delivery.md` (exact-output feedback), `native-profile-and-lead-binding.md` (actual lead, withdrawal and replay), `decision-delta.md` D-LEAD-ADOPT, `prior-design/cookbook-claude-sdk-audit.md`, `prior-design/cookbook-codex-audit.md`, `bin/factory` (`run_eval` and grader routes), the grader fixture paths actually resolved by `run_eval`, and the primary guide https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents. Read relevant original audit examples, retaining flaws/limits rather than importing model defaults.

## Canonical files and bounded work

Create `seed/.loam/factory/src/improvement/evaluation.ts`, `src/improvement/adoption.ts` and `tests/improvement/adoption.test.ts`; extend existing work/evidence contracts and the next S2-managed migration for versioned evaluation/decision/activation records. Consume actual native decision evidence from NATIVE-03/04 and correction state from NATIVE-09/10.

Start from an observed failure and diagnosis, not a repeated label assumed to prove a prompt defect. Freeze baseline/candidate assets, required cases/inputs, criteria/evaluator/helper revisions, output identities, native profiles, memory snapshots, comparison method and allowed scope. Separate diagnostic/tuning from held-out evidence when claiming generalization. Execute arms in isolated workspaces/memory namespaces with equivalent immutable starting inputs and protected evaluators/reference judgments. Skipped, missing, error, fail and inconclusive outcomes remain distinct; candidate learning cannot contaminate the other arm or ordinary project memory. Valid JSON, consensus and a lucky stochastic run are not proof of improvement.

The actual lead decides disposition/reason/scope against exact current comparison evidence. In one authority transaction validate lead/session/attempt, root decision finality, candidate and lead revision, expected predecessor asset, evidence/assessment eligibility, permissions and pause/correction/history barriers. Commit decision/activation/receipt together. No eligible lead means pending. Identical emission replay returns the existing receipt; conflicting identity reuse fails. Revalidate before uncommitted replay; commit-before-reply recovery never adopts twice. Handle later native withdrawal by blocking affected use and reconciling, while preserving history.

Default target is project configuration/extensions. Managed engine edits require explicit local fork or separate Loam contribution. Activation affects future work; active inputs change only through steering/readmission. Rollback checks current admissibility of the chosen historical revision. Shared promotion/private trace export is separate authority.

Apply its new schema to an existing registered scratch store only through CORE-09 guarded migration and external-marker recovery, inherited through NATIVE-09. Add a migration-before/after-application interruption case to the named fixture; fresh-store creation alone cannot demonstrate existing-store compatibility.

## End-to-end acceptance

Future commands, unimplemented and unrun: build, then `node --test seed/.loam/factory/dist/tests/improvement/adoption.test.js`.

- [ ] First reject a plausible harmful adaptation and preserve current behavior; then exercise a supported lead-authorized activation and currently admissible rollback with preserved history.
- [ ] Missing hard case, changed scoring inputs/criteria, altered evaluator, wrong-output feedback, cross-arm memory transfer and incomplete native isolation block the comparison claim.
- [ ] Evaluator-only PASS, helper spoofing, absent lead, stale candidate/lead/predecessor, corrected source and withdrawn/replaced root decision cannot activate.
- [ ] Supervisor death before commit revalidates current barriers; death after commit before reply returns the original receipt. Identical replay is idempotent; altered replay conflicts.
- [ ] A legitimate non-code/inconclusive research outcome is representable. Actual benefit requires appropriate later real-task evaluation, not a claim inferred from these mechanical fixtures.

This slice uses one small project-local method-change fixture. No generalized autonomous optimizer, shared publication or evaluator-controlled adoption is introduced.

## Campaign requirements

Status: **planned draft; publication approval pending; runtime implementation deferred**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **store, complete-slice**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `2c5590277d0b5bb695818a8da9b4e076767436d6e7b8a64685e963b150721aa7`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/improvement-evaluation.md`
- `docs/architecture-working/memory-loop-engineering.md`
- `docs/architecture-working/memory-records-and-delivery.md`
- `docs/architecture-working/native-profile-and-lead-binding.md`
- `docs/architecture-working/prior-design/cookbook-claude-sdk-audit.md`
- `docs/architecture-working/prior-design/cookbook-codex-audit.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`
