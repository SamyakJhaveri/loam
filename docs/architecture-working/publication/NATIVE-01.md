<!-- loam-native-campaign:6944c13df21316acdd27ad9e090d56a468156b33f332ec32e021a542296eec70:NATIVE-01 -->

Stage: S3

Implementation lead: Codex/Astra

Campaign: https://github.com/SamyakJhaveri/loam/issues/102

## Blocked by

- https://github.com/SamyakJhaveri/loam/issues/106 (CORE-03)
- https://github.com/SamyakJhaveri/loam/issues/111 (CORE-08)

## What it delivers

A generated project prepares one reusable option C profile, admits its exact selected inputs, and reports whether a bounded native launch is available. Native reasoning, tools, context management, supported delegation and selected local computer operation remain native capabilities. No competing reasoning loop is added.

## Current behavior and source packet

Verified from current source inspection: `bin/factory` selects worker/advisor settings through environment/defaults and builds prompts with `build_worker_prompt`; named Codex skills may resolve through personal Claude skill/plugin caches. The admitted protected profile is proposed, not implemented by that path.

Read `docs/architecture-working/native-profile-and-lead-binding.md` (profile records, discovery, account access, failure table), `native-binding-validation.md`, `engine-runtime-and-layout.md`, `first-run-ownership-storage-recovery.md`, `prior-design/native-adapter-design.md`, `prior-design/native-codex-evidence.md`, `prior-design/native-claude-evidence.md`, `bin/factory` (`build_worker_prompt`, worker launch/status), `seed/.codex/config.toml`, `seed/.claude/settings.json` and `seed/docs/HARNESS.md`. Read the native profile documentation linked in that proposal: https://learn.chatgpt.com/docs/config-file/environment-variables, https://learn.chatgpt.com/docs/build-skills and https://code.claude.com/docs/en/agent-sdk/claude-code-features. Use S1 tested native identities rather than treating saved version strings as current support.

## Canonical files and bounded work

Extend the qualified `seed/.loam/factory/src/profiles/admitted-view.ts`. Create `seed/.loam/factory/tests/native/profile.test.ts`; extend `src/commands/status.ts` and `seed/docs/factory/SETUP.md`. Consume existing installation, execution and work contracts. Keep requested settings, admitted local input identities, external live dependencies, launch observations and execution observations separate. Include executable/support closure and native discovery through home, parent/nested paths and symlinks in the protected view.

Option C and all curated Loam methods, including parked methods through their named successors, are settled. This ticket establishes the selection/admission mechanism using a small declared fixture profile; NATIVE-05/06/07/08/12 and S6 close the complete curated payload. Do not present the fixture profile as the finished required profile. Personal additions receive reusable selection and reviewable differences. Do not automatically import personal memory/hooks/plugins. Support documented native account login without token copying or silent account/API billing-route changes. Monitor external/organization policy that cannot be frozen, and fail dependent readiness on incompatible drift.

## End-to-end acceptance

Future commands, unimplemented and unrun: `npm --prefix seed/.loam/factory run build`, then `node --test seed/.loam/factory/dist/tests/native/profile.test.js`.

- [ ] Generated scratch setup admits a profile and launches only the declared bounded test host through the installed entrypoint; status distinguishes requested capability from observed available capability.
- [ ] A candidate edit to an instruction/hook followed by restoration cannot affect admitted loading. Undeclared parent/home input, symlink alias or child write either remains excluded before use or fails readiness. Before/after hashing alone is insufficient.
- [ ] Missing connector/auth refresh and organization restriction drift remain unavailable. No fallback imports broader personal inputs or changes model/effort/account route.
- [ ] Live checks on both required hosts are separate bounded S1-qualified provider proofs after explicit authorization; record credential/capability gaps honestly. The profile cannot claim authority-bearing support until isolation and selected native features are proven.

Keep provider root-decision attribution in NATIVE-03/04 and actual improvement adoption in NATIVE-11. No native engine rewrite, remote runner or full asset migration belongs here.

## Campaign requirements

Status: **planned; runtime implementation deferred; not ready-for-agent**. Empty blockers do not authorize execution. Read `docs/architecture-working/ticket-campaign.md` and `delivery-workflow.md` in full. They require a digest-verified accessible source packet, fresh fetched-main worktree, actual opposite-model plan and finished-work reviews, nonempty focused checks, one full-check owner, and verified integration before dependent work. Preserve all existing changes. Raw review evidence lives outside candidate/worktrees. Sources are evidence and inspiration; justified departures preserve user requirements and record a reason and check. Proposed files/commands are unimplemented at authoring time and must be reconciled against landed predecessors. Live provider/GPU work needs a declared bounded plan within user authority; mechanical checks do not launch it implicitly. Full recipient groups remain unavailable/non-passing until S6. No automatic model/effort changes or release/publication. Architecture basenames resolve under `docs/architecture-working/`; package-relative canonical paths resolve under `seed/.loam/factory/`.

Every fixture-creating ticket registers its mandatory named population, expected nonempty cases and current availability in the fixed registry. CORE-01 declares the full installation/store/execution/complete-slice obligation groups as incomplete from the start; missing/unbuilt populations never disappear into a passing subset. NATIVE-02 explicitly registers coordination as mandatory execution work. Later tickets fill their declared populations; OPS-10 verifies closure rather than performing first registration.

For host-sensitive acceptance, run the named focused population on both required hosts against the same candidate, recording environment identities and exact results. Mac-only evidence cannot certify Linux installation, storage, filesystem or isolation behavior.

## Verification population assignment

Canonical registry edits in `seed/.loam/factory/src/testing/verify.ts` are in scope wherever this ticket creates or extends a recipient fixture. Target groups: **installation**. Register the ticket-owned named population, expected nonempty case list/count and current availability; a missing fixture stays unavailable. No required population may remain outside its named group. Shared cases retain one identity when referenced by multiple groups. `release-only` names Loam release tooling, not a recipient command; `post-installation` is the separately scoped empirical follow-up and does not block initial S6 closure or claim empirical success early. OPS-10 verifies full declared initial populations; it cannot hide unbuilt work by first defining a smaller group.

## Source packet and readiness

Packet manifest SHA-256: `8e59b28311f44ff66e291c54dbf5a51b71ea3370b054c542624e417a632f85b4`. Full per-file hashes are in this ticket entry in `docs/architecture-working/ticket-backlog.json`. This digest covers the listed source identities, not a claim all external originals have been read.

**Readiness blocker:** these local records are untracked. Before execution, supply this exact source packet to the fresh worktree/seat and verify its manifest, or review and record a successor packet. Publishing the issue alone does not resolve this blocker. The named original upstream sections and current implementation/support callers must be inspected and added to the per-step reviewed packet before code changes.

- `docs/architecture-working/START-NEXT-SESSION.md`
- `docs/architecture-working/decision-delta.md`
- `docs/architecture-working/delivery-workflow.md`
- `docs/architecture-working/consolidated-implementation-plan.md`
- `docs/architecture-working/ticket-campaign.md`
- `docs/architecture-working/native-profile-and-lead-binding.md`
- `docs/architecture-working/native-binding-validation.md`
- `docs/architecture-working/engine-runtime-and-layout.md`
- `docs/architecture-working/first-run-ownership-storage-recovery.md`
- `docs/architecture-working/prior-design/native-adapter-design.md`
- `docs/architecture-working/prior-design/native-codex-evidence.md`
- `docs/architecture-working/prior-design/native-claude-evidence.md`
- `seed/.codex/config.toml`
- `seed/.claude/settings.json`
- `seed/docs/HARNESS.md`
- `docs/architecture-working/delivery-step-plan.md`
- `docs/architecture-working/native-binding-step-plan.md`
- `docs/architecture-working/asset-environment-step-plan.md`


Approved draft SHA-256: `9b87b6ace14b54f06c6c4cf6b26811a7c35c4fc17c105fdc27a156314c165b62`. Full source access must be verified before execution.
