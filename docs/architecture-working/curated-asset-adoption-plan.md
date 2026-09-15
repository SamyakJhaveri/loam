# Curated assets: implementation-plan addition

Status: accepted scope and file-level adoption tickets. Runtime implementation and seed activation remain deferred. This is a bounded addition to the factory plan, not a claim that the complete engine implementation plan is finished.

Goal: ship Loam's curated reusable skills and the suitable methods found in the named projects with generated projects, through the accepted explicit native profile.

Architecture: one canonical shared skill implementation in `seed/.agents/skills/`, with supporting references beside it. Native command/agent/plugin adapters express provider-specific invocation and capability checks. The supervisor continues to own authority and durable evidence. Skill prose cannot grant permissions, choose a different model, manufacture a passing check or replace an actual lead decision.

Tech stack: Markdown and native metadata for methods/adapters; TypeScript/compiled JavaScript for factory contracts and validators. A declared specialist tool can have its own isolated dependencies, without changing the factory language.

## Accepted scope and current evidence

Verified: the user selected option C and explicitly included existing curated Loam skills. All local curated skills are baseline inclusion sources, including parked ones. Inclusion means preserving and delivering the useful capability. It does not mean restoring obsolete hooks or executing every skill on every task. Descriptions make capabilities discoverable; detailed bodies load when relevant. Provider-specific capabilities retain honest availability limits.

Verified: the [Loam inventory](asset-intake/loam-inventory.json) records 30 local skills: 2 in seed, 4 in the optional marketplace and 24 parked. Its per-file dispositions describe preservation and adaptation. These are not interchangeable duplicates: the audit found semantic overlap, not byte-identical implementations. Remote marketplace declarations are catalogued separately; their implementations were not fetched or certified in this step.

Verified: [source intake](asset-intake/README.md) now preserves selected distinctive methods from ParBench, DistBench and job-search, plus the global experiment-loop referenced by the Instagram organizer. The [benchmark](asset-intake/benchmark-inventory.json) and [application](asset-intake/application-inventory.json) inventories retain other discoveries and scope limits. Source projects were read only.

## Canonical destinations and preservation rule

Recommendation: each current curated skill receives a catalog entry and one of: retained source, adapted source, or named merged successor with a section-level preservation map. No silent deletion because a folder was parked or an upstream skill shares its name. Broken dependencies block activation until repaired; they do not remove the inclusion requirement. A release claiming this scope complete must account for every baseline method and pass its declared capability checks. If a requirement cannot be preserved, return that specific change to the user.

Recommendation: put generic adopted methods in the shared seed home. Keep domain methods such as RenderCV available on demand, with explicit tool prerequisites. Do not install those tools merely because a seed contains their instructions. Keep private job/benchmark adapters, compute locations and project policies in their source projects. An optional external package can supply an implementation only through an exact dependency/closure contract; a personal-cache link is insufficient.

Recommendation: canonical shared method bodies never live independently in both Claude and Codex folders. Existing seed Claude symlinks can expose shared skills. Native wrappers retain only provider-specific invocation. Any unavoidable distribution mirror gets an equality check. The integration ticket must update `docs/ASSET-LAYERS.md` to distinguish shipped availability, discovery and actual prompt loading; its current always-on-layer wording does not mean every skill body should load every turn.

## Ticket ASSET-01: catalog and conservation of curated methods

Dependencies: accepted option C; source intake and current Loam inventory. No execution-environment decision is needed to author the catalog.

Current behavior: seed ships the small shared skill set; other curated skills are optional or parked and some dependencies are missing.

Files to create: `seed/.loam/factory/assets/curated-catalog.json`, `seed/.loam/factory/assets/curated-catalog.schema.json`, `seed/.loam/factory/tests/assets/catalog.test.ts`. Update `docs/ASSET-LAYERS.md` and the proposed `seed/docs/factory/ASSETS.md`.

Contract: every baseline source records its source digest, canonical destination, preserved sections or named successor, provider applicability, support files, required tools/services, side-effect classes and availability status. No secrets or local absolute paths in the released catalog. Advisory text, executable support and authority-bearing policy are distinct asset kinds. Catalog selection is not action authorization.

- [ ] Compare every inventoried curated skill with its proposed destination, preserving local modifications and attributions.
- [ ] Write fixtures that remove a baseline entry, point to a missing successor and collapse non-identical provider variants without a preservation map. Each must fail before implementing the catalog checks.
- [ ] Add the complete catalog, then demonstrate each failure is rejected and the complete declared payload is accepted.

Proposed acceptance command, not implemented or run: `node .loam/factory/launcher.mjs verify installation`. Add a mandatory `curated-catalog` case group to that existing planned interface. Success requires no unaccounted baseline method, no missing support and no personal-cache dependency. Merely declaring an entry does not certify its executable behavior.

## Ticket ASSET-02: repair existing curated workflows

Dependencies: ASSET-01 and the factory's admitted profile/store/check interfaces. Adaptation must use those interfaces rather than recreate an old controller.

Files: preserve or adapt every exact `planned_destination` in [baseline-adoption-map.json](asset-intake/baseline-adoption-map.json). Source roots are exactly those listed in `asset-intake/loam-inventory.json`. Create shared references under `seed/.agents/skills/plan-review/references/`, `seed/.agents/skills/authoring-context-docs/references/` and `seed/.agents/skills/validate/references/` where duplication is confirmed. Add `seed/.loam/factory/tests/assets/curated-workflows.test.ts`.

Required repairs:

External merge input for this ticket: compare the staged `distbench-worktree-status` snapshot with Loam's curated `worktree-status`. Preserve its distinctive readiness/stale-baseline behavior in the successor's section-level conservation map. Resolve base-branch selection and distinguish live Git fetching from read-only status; the external variant must not disappear merely because Loam already uses the same name.

- Planning: preserve `brainstorming`, `writing-plans`, `gen-spec`, `tech-selection`, `unknowns`, `hypothesis-tree`, `brief` and `surprise-me`; share criteria without erasing distinct tasks.
- Review: preserve `plan-review`, `codex-review`, `codex-plan-review`, `session-critique`, `validate`, `techdebt` and `vet-skill`; keep independent evidence, blind review and one validation owner. Replace hardcoded model/effort with admitted native choices.
- Continuity: preserve `catchup`, `sam_handoff`, `reflect`, `dream`, `authoring-context-docs` and `scaffold-context`; use the accepted shared-memory/correction contract. Missing native personal memory is unavailable, not an invented path or alternative authority.
- Execution/distribution: preserve `agent-team`, `auto-phase`, `ship`, `worktree-status`, `bootstrap-cc-setup` and `sync-to-hub`; replace absent `validation.py`, removed sentinel hooks and missing `bin/agent-sync.sh` with current contracts. Promotion needs an explicit destination and authority; publishing is not implicit.
- References: preserve `fable-prompting`, `align-prompt` and `impeccable`; keep provider applicability and source provenance. The local impeccable wrapper is not the complete upstream tool.

- [ ] Add failure fixtures for a missing helper, an untracked candidate change, a forged pass sentinel, an unauthorized model override and a skill requesting a push outside task authority.
- [ ] Route configured checks through deterministic evidence. Loam development uses `bin/check`; generated projects use their own admitted check definition. Never assume every recipient has Loam's root check script.
- [ ] Demonstrate corrected workflows preserve the required evidence and refuse unsupported execution. Generalization must not treat a check result as automatic improvement adoption.

Proposed acceptance: `node .loam/factory/launcher.mjs verify execution`, mandatory `curated-workflows` cases. A negative case must fail for its intended reason; a text scan alone does not prove runtime authority.

## Ticket ASSET-03: independent critique and simpler-design review

Dependencies: ASSET-01/02 and admitted native delegation/lead binding.

Create `seed/.agents/skills/critique-swarm/SKILL.md` and `seed/.agents/skills/critique-swarm/references/review-contract.md`; merge DistBench's team method into the canonical `agent-team`; merge ParBench's additional method into `seed/.agents/skills/plan-review/references/elegance-review.md`. Loam already has an elegance gate; this adds useful criteria, not another mandatory review stage. Provider wrappers go in the native adapter's declared asset view, with exact wrapper destinations recorded in ASSET-01 before implementation. Add `seed/.loam/factory/tests/assets/review-methods.test.ts`.

Inputs: staged DistBench Claude/Codex critique variants, its Codex team method and ParBench elegance reviewer. Preserve each variant's supported orchestration; do not replace Codex calls with Claude team APIs or pretend native feature parity. Elegance review considers existing simpler alternatives and requirements, not deletion counts as a quality score. Wider changes remain proposed scope, not authorized action.

- [ ] Prove that a child claiming root authority cannot decide adoption, and that unavailable independent review cannot be labeled completed.
- [ ] Prove a supported native wrapper preserves the shared review contract and chosen model/effort; perform real-provider capability checks only in the later authorized probe stage.

Proposed acceptance: `node .loam/factory/launcher.mjs verify execution`, mandatory `review-methods` cases, plus the separately authorized provider probes. Fake agents prove mechanics only.

## Ticket ASSET-04: reusable experiments and evidence audits

Dependencies: ASSET-01/02, evidence/artifact records, configured check runner and actual-lead adoption.

Create `seed/.agents/skills/experiment-loop/SKILL.md`, `references/protocol.md`, `seed/.agents/skills/evidence-audit/SKILL.md`, `references/evidence-contract.md`, `references/report-template.md` and `seed/.loam/factory/tests/assets/research-methods.test.ts`. The reference paths belong under their respective skill directories.

Inputs: the organizer-referenced experiment method and generic portions of the company-research skill/references. Keep fixed inputs, protocol-before-results, source coverage limits, independent evidence before comparison, deterministic checks, bounded repairs and uncertainty. A blocked source is not proof that a fact is absent. Agreement among models is not proof of truth. Match decisions to the accepted actual-lead/user authority; remove automatic cheaper judges, forced model changes, implicit installs and always-human adoption rules.

The company validator is metadata-only intake and is not the validator for this new generic schema. If any URL-checking implementation is reused, put it behind the admitted network boundary with checks on destination and redirects; do not let an untrusted report fetch local/private service endpoints. Keep project ledgers, contact ranking, personal priorities and original internal report paths out of the generic method.

- [ ] Add failure cases for changed evaluation inputs, modified scorer, unavailable source reported as absent, model consensus presented as proof, and helper-only adoption.
- [ ] Add a no-network fixture for URL handling and a case where a newer correction invalidates an otherwise matching report.
- [ ] Demonstrate one generic non-benchmark inquiry through the complete research/evaluation/decision path.

Proposed acceptance: `node .loam/factory/launcher.mjs verify complete-slice`, mandatory `research-methods` cases. These do not measure empirical research usefulness; retain post-installation evaluation during real work.

## Ticket ASSET-05: tool references, support commands and packaging

Dependencies: ASSET-01; ASSET-02/03/04 for the integrated release. Specialist tool execution is conditional on explicit prerequisites.

Create `seed/.agents/skills/rendercv/SKILL.md` with the large tool schema in `references/`. Check source attribution and pin compatibility before declaring support. Use a synthetic CV, verify facts remain unchanged and inspect the rendered artifact. Do not adopt an unpinned installation instruction as a dependency contract.

Modify the proposed `bin/tests/factory-release-render.test.mjs` and add `seed/.loam/factory/tests/assets/delivery.test.ts`. Retain every selected supporting command/plugin dependency in the catalog; bundle or declare it explicitly. A command that only exists in another project is not delivered. Hooks and private native settings are not bulk imported as policy.

- [ ] Render the full Copier project-kind matrix and check all catalog-declared assets without the source projects or personal caches available.
- [ ] Test updates preserving project profile additions and exact inputs for active work. A same-name upstream addition cannot overwrite a curated variant silently.
- [ ] Verify missing specialist tools produce an honest unavailable capability, not an installation or a passing render result. A release can advertise a conditional tool capability only with its documented prerequisite and successful supported-environment fixture.

Proposed acceptance: release owner runs `node --test bin/tests/factory-release-render.test.mjs`; recipient runs `node .loam/factory/launcher.mjs verify installation`. Before any later Loam implementation commit, one validation owner runs `bin/check` and requires `check: PASSED`. No command in this plan was implemented or executed in this design step.

## Next decisions

The profile choice is settled; do not ask again whether curated Loam skills should be included. The [execution scope](execution-environment-and-bootstrap.md) is now settled: this Mac and jhaveris Linux. The asset tickets fit before the complete generated-project proof and do not require implementing two native reasoning loops. Wrapper/probe details must cover both accepted hosts; needed package changes are acceptable. Activation remains behind the user's explicit implementation instruction.
