# Decision delta: memory and loop engineering

## Settled direction

Verified from the user's instructions and acceptances: every seed has its own complete factory; one managed reusable engine with project configuration/extensions; direct engine edits are an explicit local fork; updates preserve project decisions; SQLite plus artifact files; native Claude Code and Codex capabilities; user-controlled models and effort; source-grounded design with independent critique. Runtime work remains deferred.

The user endorsed the cookbook-grounded direction and asked to save the work and proceed to memory and loop engineering. This does not establish that every proposed transport detail or capability has been tested or individually approved.

## Accepted memory and loop architecture

Verified: the user explicitly accepted the suggestions in the memory and loop discussion and asked to add them to the implementation design. The choices below are therefore accepted architectural direction. Their identifiers retain the original P prefix for traceability; it no longer means they are awaiting acceptance. Exact schemas, review routing and native delivery mechanisms developed in the next step remain recommendations, and acceptance does not authorize runtime implementation.

| ID | Accepted choice | Reason and boundary |
|---|---|---|
| P-MEM-OWNER | SQLite owns memory identities, revisions, lifecycle and dependency links; artifact files hold substantial bodies. | Extends the accepted store architecture without a second authority. Human-authored context and decision files remain their canonical authored sources, referenced by exact admitted identity. |
| P-MEM-PROMOTE | Permit automatic capture and configured review of ordinary advisory lessons; no human approval for every note. | Keeps memory useful during autonomous research. Activation requires support and scope assessment. Governing decisions, permission, models, effort and acceptance are separate authority. |
| P-MEM-RETRIEVE | Select required current constraints deterministically, then rank eligible advisory records with ordinary search. | A relevant obsolete lesson cannot outrank a correction. Embeddings and graphs require measured benefit before adoption. |
| P-MEM-CORRECT | Correction changes read eligibility immediately; consolidation and packet delivery compare current input revisions. | An asynchronous index rebuild or delayed worker cannot restore a retracted lesson. Already delivered affected context requires ordered steering and reconciliation. |
| P-LOOP-OWNERS | Native reasoning, durable progression and evaluated improvement have distinct owners. | Preserve native agency while retaining truthful recovery and acceptance. |
| P-IMPROVE-EVAL | Every proposed prompt/method/tool change has a diagnosis, exact baseline/candidate evaluation population and separate activation. | Repeated failure labels are investigation triggers, not proof of a cause. Valid JSON and model agreement do not prove improvement. |
| P-IMPROVE-SCOPE | Improvements are project-local by default; shared Loam promotion is separate work. | Prevent export of private traces and accidental mutation of the reusable engine. Active run inputs remain frozen. |

See [memory-loop-engineering.md](memory-loop-engineering.md) for sources, alternatives and acceptance obligations. The user's additional requirement is ongoing evaluation after the memory system has been developed, installed and used on real tasks. Controlled pre-release checks remain necessary; everyday use must also reveal helpful retrieval, harmful carryover, correction failures and improvement opportunities. Usage observations are evidence to investigate, not automatic proof of causal benefit or permission to activate changes.

## Next design step

Verified: after the story explanation, the user accepted the recommendations so far and asked to proceed. Retain the finding, assessment, shared handoff, applicability and correction direction and the supporting [record schema and context-delivery contract](memory-records-and-delivery.md) as the implementation-design baseline. This is design acceptance, not empirical validation or authorization to implement runtime code. Exact provider capability and physical implementation choices remain subject to their stated checks.

Verified scope clarification: Loam seeds research projects broadly. Benchmarking is an illustrative example, not its product focus or a required domain method. This clarification adds no new product scope. Generic memory/evaluation machinery ships with every seed; each project supplies the methods and criteria appropriate to its research.

Verified: the user accepted [testing and adopting an improvement](improvement-evaluation.md) and specified that the decision is made by the session's lead Astra or Fable model. The lead evaluates the evidence and decides whether to adopt, decline or revise an improvement within the user's authorized scope. Reviewers and advisors supply evidence and recommendations; they do not replace the lead's judgment. The deterministic supervisor validates and records the authorized decision, rather than deciding research value from a score.

Accepted D-LEAD-ADOPT: require a decision bound to the designated lead's actual session/attempt, the exact proposed revision and its evaluation evidence. A worker-authored role label is insufficient. If no eligible lead is active, adoption remains pending for a lead session; no background evaluator silently substitutes for it. User-controlled models/effort, required checks, private-data boundaries and explicit scope remain governing. A decision exceeding existing authority needs the user's direction. Runtime work in this design session remains deferred.

Verified: the user agreed to the [smallest complete generated-project slice](first-complete-slice.md) and asked to proceed to the next design step. It proves the core path without claiming that an early slice is the full factory release. This continuation does not override the explicit runtime-implementation deferral.

Accepted D-ENGINE-TS: TypeScript compiled to JavaScript, a pinned supported Node LTS runtime, factory-local dependencies, preferred Claude TS SDK/direct Codex protocol, and a dedicated SQLite owner. [Runtime and layout](engine-runtime-and-layout.md) compares Python alternatives and names storage, native ownership and packaging gates. The user explicitly selected TypeScript after the SWOT discussion. Prior Python fixture commands were tentative; the proposed Node commands are now the intended fixture interfaces. Exact dependency choices and runtime behavior still require validation; the commands remain unimplemented.

Decision basis: after reviewing the [language comparison](language-choice-swot.md), the user explicitly chose TypeScript and said unfamiliarity should be a learning opportunity rather than an obstacle. The language decision is settled. Python alternatives remain comparison history, not a parallel implementation track. Native capability, packaging and recovery checks validate the TypeScript implementation. No measured token, cost or performance advantage is asserted. Research languages remain project-selected, and runtime implementation remains deferred.

## Resumed concrete mechanism proposal

Verified: the latest user instruction resumes design, preserves TypeScript and existing changes, asks for current-main verification and living-record updates, and explicitly defers runtime implementation. Local/remote main and preservation checks are recorded in [first-run validation](first-run-validation.md). The existing suite returned `31 passed in 8.95s` and `check: PASSED`; this is current-code verification, not replacement-engine proof.

The [first-run, ownership, storage and recovery](first-run-ownership-storage-recovery.md) proposal specifies a pending setup transaction, independently admitted protected runtime, common-directory instance binding, supervisor-held lifetime lock, dedicated SQLite thread, existing-only URI open candidate, authenticated observational host reconnect followed by control-session replacement, durable check/native spools and externally recorded restore/migration barriers. It preserves the accepted distinction between native execution and acceptance, and between reconnection and a new invocation. This was presented as a recommendation; the subsequent acceptance below records its current status.

Historical first candidate was macOS/local disk; current required scope is both accepted hosts below. Mechanism choices remain conditional: `fs-ext` locking behind the platform boundary; built-in SQLite using a controlled `mode=rw` URI; immutable installed snapshots with declared dependency builds. No dependency, platform support claim or runtime pin becomes accepted merely by appearing in this proposal. The exact host protection, native configuration/lead binding and compatibility probes remain gates. No runtime implementation is authorized.

## Native profile continuation and decision presentation

Verified: the user replied "looks good" to the first-run explanation and asked to resume. Accept the preceding architectural direction while retaining its unverified mechanism and dependency gates. This is not runtime authorization or advance acceptance of the native-profile choices developed afterward.

Verified: the user now requires each substantive response to end with the input needed, options, simple expected consequences, a recommendation and the next topic requiring a decision. Combinations are welcome. Preserve this instruction across handoffs. When no input is needed, say so rather than inventing an approval request.

Proposal from the preceding step, accepted below: [native profiles and actual lead binding](native-profile-and-lead-binding.md) develops an explicit factory profile with selected personal additions. Default to Loam/project inputs and user constraints; select personal skills/instructions once for reusable profiles, and admit hooks/plugins/services deliberately. Preserve native account authentication through supported setup without credential copying or a billing-route substitution. Native reasoning, tools and delegation remain native.

The concrete lead routes are a Codex native dynamic tool bound to exact root thread/decision turn, and Claude native root output joined to session/request/hook evidence. These are source-grounded candidates, not validated mechanisms. Exact model/effort observations, input isolation, automatic restart behavior, account service compatibility and recovery replay remain native probe gates. Missing attribution leaves adoption pending. See [native validation](native-binding-validation.md).

Accepted D-PROFILE-C: the user explicitly selected option C and instructed that Loam's already curated skills be included. Preserve every local curated method, including parked assets, through a retained/adapted destination or a documented merged successor. Inclusion does not restore obsolete hooks, grant new permissions or override chosen models/effort. No repeated profile-choice question is needed.

Accepted scope addition: investigate reusable skills, plugins and commands from ParBench, DistBench, the Instagram organizer and job-search tool, bring suitable material into Loam and add the implementation plan/files. [Inactive intake](asset-intake/README.md) now stores selected source-reference text with source hashes and wider metadata inventories. The organizer is content_search_engine; its experiment method is a referenced global skill, not a project-local plugin. [ASSET adoption tickets](curated-asset-adoption-plan.md) preserve the curated baseline, repair missing dependencies, merge native review methods, generalize evidence/experiments and verify delivery to seeds. Runtime and seed activation remain deferred.

Accepted D-HOSTS-MAC-JHAVERIS: the user's latest correction limits required support to this Mac and the Linux machine reached through `ssh jhaveris`. Both are required for Loam and all generated factories. The previous E1/E2/E3 questionnaire is superseded. The user is willing to install needed libraries/software and upgrade or downgrade packages to supported stable versions. Treat that flexibility as setup authority within the ongoing task, without construing it as an instruction to begin the deferred runtime implementation.

Verified: SSH inspection succeeded. [Host evidence](two-host-inventory.json) records macOS arm64 and Ubuntu x86_64 tooling. The Linux non-interactive PATH issue was reproduced, and explicit child-process resolution made Node/npm/Codex/Claude version checks exit 0. No package or shell configuration was changed. [Current setup design](execution-environment-and-bootstrap.md) now scopes ENV-01 and the complete proof to both hosts. Preserve all accepted curated-asset tickets. Next: concrete initial setup and update flow, then remaining ordered implementation tickets.

## Latest maintenance and remote-work extension

Accepted D-MAC-LINUX-REMOTE: the latest user instruction extends the initial host scope to Mac/Linux replacement machines and explicitly requires local Mac native sessions to launch and monitor agents and GPU experiments on Linux. Preserve native local computer operation as a selected capability. Remote execution is now required; entering an independent Linux session through SSH alone does not satisfy it. The earlier same-machine execution-host recommendation is superseded for these remote jobs. Runtime implementation remains deferred.

Proposal D-MAINTENANCE: [maintenance and remote work](maintenance-and-remote-work.md) uses one curated catalog, one versioned factory release, one project authority and one local/remote execution contract. An SSH transport reaches a persistent Linux runner with a durable job ledger/spool. The remote runner records execution facts and enforces admitted bounds; it cannot make lead decisions or task acceptance transitions. Use explicit readiness, relevant compatibility checks, reviewed release adoption, fixed active snapshots and drain-before-activation for affected shared services. Separate code rollback from state restore and explicitly enroll/fence replacement machines. [Remote contract](remote-execution-contract.md) and [implementation additions](maintenance-remote-tickets.md) define the obligations.

Accepted D-OFFLINE: the user explicitly selected the mixed policy. Already started fixed GPU jobs continue within agreed limits while the Mac is disconnected; agents default to interruption/no new approvals. This does not authorize new queued work, more time/resources or autonomous native continuation. Any native exception requires separate task-specific authorization. The [job record and operator flow](remote-job-and-operator-flow.md) propose concrete records, setup, monitoring, recovery and update requirements. GPU queue behavior is accepted below; routine resource mechanics do not need another user decision. Runtime implementation remains deferred.

Verified: [read-only maintenance evidence](remote-maintenance-evidence.json) records reachable Linux systemd user management with linger disabled, available GPU tooling and inspected ParBench tmux/log patterns. No service, native model or GPU job was launched. [Validation](maintenance-validation.md) distinguishes source/mechanism evidence from unperformed runtime probes.

Accepted D-PERSONAL-GPU: queue by default with fail-fast available. The user states that jhaveris is their personal machine for their own use and explicitly asks to avoid overcomplicating scheduling minutiae. Use simple handling for overlapping personal jobs; no multi-user scheduler or resource-policy questionnaire. Choose ordinary queue/expiry/check defaults during implementation, retaining execution identity, bounds and current-control checks. Next consolidate remaining bootstrap/setup/update tickets into an ordered implementation plan. Runtime remains deferred.

## Consolidated delivery plan

The user asked to proceed with consolidating the remaining installation, updates and recovery work. The [consolidated implementation plan](consolidated-implementation-plan.md) now orders that work with source ownership, dependencies, failure/success evidence, native/memory/asset coverage, remote execution and the old-controller transition. It is a delivery proposal under the accepted architecture, not acceptance of untested bindings or authorization to begin runtime implementation. Earlier next-work instructions to consolidate are fulfilled. Routine GPU defaults remain engineering choices; the next material decision is whether to begin the bounded foundation stage or revise the plan.

## Accepted implementation delivery rules

Accepted D-DELIVERY: the user explicitly requires source/reference-grounded construction, use of relevant cookbook loops/dynamic workflows/advisor/multi-agent patterns while implementing and testing, fresh current-main worktrees per implementation step, opposite-model review of both plan and finished work, and verified merge before the next step. Codex implementation is reviewed by actual Claude Code Fable 5.1; Claude implementation by Codex/Astra. Fresh free agents or predefined subagents are acceptable; advisor consultation and lean criticism do not substitute for independent review. Lean critic and Wayfinder use are discretionary. The [delivery workflow](delivery-workflow.md) maps sources, stage additions and evidence; these rules supersede less specific historical implementation-review policies. The merge sequence is standing direction once implementation begins, not a new runtime launch or release/publication authorization.

## Documentation location

The original review folder remains unchanged due to filesystem restrictions. Prior records have been preserved in this repository's documentation directory as exact snapshots. This is a working-location fallback, not a new seed payload or a commit.

## Source use and concrete ticket preparation

Accepted D-SOURCE-JUDGMENT: the user explicitly permits departing from supplied sources when a better-supported engineering, research, design or architecture choice fits Loam. Sources provide evidence and reusable methods, not mandatory recipes. Preserve attribution, accepted requirements and the source-to-mechanism/test mapping; record the reason and verification obligation for a departure. This does not reopen previously accepted design choices.

The user asked to acquire Matt Pocock's package, assess Wayfinder, and write tickets now using the actual working records, subagents and dynamic workflows. [Tool assessment](ticketing-tool-assessment.md) records the pinned source bundle, active-install limitation and choice to use to-tickets for the accepted implementation plan. Ticket authoring is authorized; runtime implementation remains explicitly deferred. Complete draft bodies and dependencies precede the skill-required publication approval.
