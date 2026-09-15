# Loam architecture working record

Current handoff: [planning saved locally; Git commit blocked](save-to-main-handoff.md). Start the next implementation session with [the CORE-01 prompt](NEXT-SESSION-PROMPT.md). No runtime implementation was started in the planning session.

Latest: [approved GitHub publication and next step](publication-handoff.md), [publication ledger](publication/ledger.json), and [Codex implementation cycle](codex-implementation-runbook.md). These supersede the earlier publication-pending wording. Runtime implementation remains deferred.

Status: planning and published tickets are saved locally. The user authorized committing and pushing these records, but staging failed because the environment denied creation of `.git/index.lock`. No commit or push occurred. Runtime implementation and deployment remain deferred. The requested Matt Pocock source bundle is staged for explicit reading; active Codex installation was blocked.

This is the durable working location for the architecture conversation. The requested original review folder is readable but outside the session's writable roots. It has not been modified. These documents belong to Loam development and are outside `seed/`; the proposed factory implementation must eventually ship from `seed/`.

## Read next

- [Concrete ticket backlog](tickets/README.md): complete individual draft issue bodies and dependencies. [Campaign contract](ticket-campaign.md) keeps implementation deferred and defines publication, source-packet and execution gates.
- [Source inventory](source-inventory.md): supplied sources, reading limits, selected assets and concrete ticket routing. [Tool assessment](ticketing-tool-assessment.md) explains the acquired Matt package and to-tickets/Wayfinder choice.

- [Source-grounded delivery workflow](delivery-workflow.md): latest accepted reference-reading, cookbook-pattern use, opposite-model plan/work reviews and fresh-current-main worktree/merge cycle. [Validation](delivery-validation.md) and [final Fable repair review](delivery-review-final.json) preserve scope and evidence.

- [Consolidated implementation plan](consolidated-implementation-plan.md): current ordered plan from foundation qualification through local/native/remote work, maintenance and generated-product proof; preserves detailed asset and mechanism tickets. [Validation](consolidation-validation.md) records review and limits. Runtime work is not authorized.

- [Remote job record and operator flow](remote-job-and-operator-flow.md): accepted mixed offline default, proposed concrete records, initial setup, launch/monitor/recover/update sequence and accepted simple personal-GPU queue behavior.

- [Maintenance and Mac-led Linux work](maintenance-and-remote-work.md), [remote execution contract](remote-execution-contract.md), [ordered tickets](maintenance-remote-tickets.md) and [validation](maintenance-validation.md): latest required workflow, proposed maintenance model, offline-policy choice and replacement machines.

- [Start the next Astra session](START-NEXT-SESSION.md): pause checkpoint, settled decisions, source map, remaining work, progress estimate and restart prompt. Read this first on resumption.
- [Native profiles and actual lead binding](native-profile-and-lead-binding.md): accepted option C and curated baseline, plus native identity, model/effort evidence and decision-recovery candidates. [Validation](native-binding-validation.md) and [step plan](native-binding-step-plan.md) preserve that step's evidence and checks.
- [Curated asset adoption plan](curated-asset-adoption-plan.md) and [inactive source intake](asset-intake/README.md): existing Loam conservation, cross-project methods, exact source identities and implementation-ticket additions.
- [Execution environment and bootstrap](execution-environment-and-bootstrap.md): accepted support for this Mac and jhaveris, with verified tool inventory and concrete setup obligations. [Validation](asset-environment-validation.md) records this continuation's scope and review.
- [First run, ownership, storage and recovery](first-run-ownership-storage-recovery.md): current concrete mechanism proposal, setup/restart story, trust bootstrap, host control, storage and maintenance failure cases.
- [First-run validation](first-run-validation.md) and [step plan](first-run-step-plan.md): current-main check, preservation, source scope and independent correctness review.
- [TypeScript versus Python SWOT](language-choice-swot.md): completed comparison, intuitive explanation, economics and counterarguments; TypeScript is now accepted.
- [Engine runtime and module layout](engine-runtime-and-layout.md): accepted TypeScript direction, package boundaries and required implementation probes.
- [First complete generated-project slice](first-complete-slice.md): current proposed proof from research through implementation, restart, memory reuse and a lead-owned improvement decision.
- [Testing and adopting an improvement](improvement-evaluation.md): the next proposed step, beginning with a research-task story and a small comparison plan.
- [Memory explained as a story](memory-story.md): the purpose of finding, checking, reusing and correcting knowledge, with an inline diagram.
- [Memory record schema and context delivery](memory-records-and-delivery.md): current detailed proposal, assessment, worker input and ongoing-use records.
- [Schema-step validation](schema-step-validation.md): source checks, preservation and independent critique for that proposal.
- [Memory and loop engineering](memory-loop-engineering.md): accepted architectural direction, alternatives, source grounding and future checks.
- [Decision delta](decision-delta.md): settled direction versus new recommendations.
- [Validation and review record](validation.md): preservation checks, critique repairs and explicit limitations.
- [Cookbook integration baseline](prior-design/cookbook-integration-design.md).
- [Practice registry](prior-design/cookbook-practice-registry.md) and [current code map](prior-design/cookbook-current-code-map.md).
- [Earlier living design](prior-design/living-design.md) and [decision history](prior-design/decisions.md).

## Preservation and precedence

`prior-design/` contains exact snapshots of the previously staged top-level Markdown records and practice registry JSON. [snapshot-manifest.json](snapshot-manifest.json) records their original locations and SHA-256 digests. Historical status paragraphs and proposed test paths are retained in those snapshots. The current document explicitly supersedes their open storage question, root-only future test locations and older next-step wording. It does not retroactively mark proposals approved.

The snapshots include the source audit reports, original URLs, source pins and access limitations. Downloaded repositories, notebooks, images, machine inventories and other nested research caches were not copied into this documentation bundle. Relative links into those caches are interpreted relative to the original source location in the manifest; they may become unavailable if temporary storage is cleared. The written design and reports themselves are saved here independently of that cache. Do not mistake a retained report for a fresh source retrieval.

Current source baseline: local `main` at `d627bb2755ad49865f798bcb095800ddd2ad1ced`. Verified on resumption with Git; `git ls-remote` returned the same remote main identity. The existing repository suite reported `31 passed in 8.95s` and `check: PASSED`, exit 0. The original review describes an older baseline. These checks do not validate the proposed factory.

Current discussion: option C is accepted with Loam's curated skill baseline. [Cross-project intake](asset-intake/README.md) preserves inactive source references and inventories; the [adoption plan](curated-asset-adoption-plan.md) adds conservation, repair, native adaptation and seed-delivery tickets. The [host scope](execution-environment-and-bootstrap.md) is settled: Mac and Linux, initially this Mac and jhaveris, with replacement machines later. The latest requirement includes local Mac sessions launching/monitoring Linux agents and GPU experiments. [Maintenance and remote work](maintenance-and-remote-work.md) extends the design and records the accepted mixed offline policy: already started fixed GPU jobs continue within agreed limits; agents default to interruption. Package changes are acceptable. [Two-host validation](two-host-validation.md) records SSH/tool observations; concrete setup/update details and remaining implementation tickets follow. [Validation](asset-environment-validation.md) records scope and review. End responses with needed input, options/consequences, recommendation and next decision. TypeScript and runtime deferral remain settled.
