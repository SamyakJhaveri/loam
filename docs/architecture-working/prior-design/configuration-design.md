# Project configuration and native launch contract

Status: configuration direction accepted by the user; exact mechanisms and acceptance tests remain proposed. Runtime implementation deferred.
Examined source: clean main d627bb2755ad49865f798bcb095800ddd2ad1ced.

## Task and verification sequence

- Verify current settings and launch paths. Check: source reads of seed native config, worker-settings and bin/factory model/launch sections; current git status and HEAD. Completed.
- Verify provider constraints. Check: official Codex configuration pages and official Claude settings/headless sources, plus independent source/help audit. Completed for the claims below; no live native probe.
- Record contracts and critique. Check: document coverage/link validation and fresh correctness review. Expected: explicit authority, desired versus observed settings, native differences and proposed acceptance checks.

## Scope and recommendation

Recommendation: use shared project configuration for the job's meaning and operational constraints, with explicit native sections for provider capabilities. Each adapter prepares native launch inputs using supported mechanisms. Do not build a general configuration language or mirror every provider option.

The shared contract answers: what work is authorized, who may do it, which capabilities are needed, what evidence establishes completion and which actions require additional authority. The native layer answers: how this selected harness loads instructions, tools, agents, settings and session continuation.

Recommendation: keep ordinary interactive sessions native. Factory guarantees apply to admitted factory jobs, including jobs requested from a native conversation. An arbitrary session does not become a supervised run merely because the project contains Loam files. The human can think and explore normally, then admit concrete authorized work without being forced to restart the idea in a rigid ticket form.

## Records and ownership

Names are proposed Loam records, not vendor API types or existing runtime files.

| Record | Owns | Writer and lifetime |
|---|---|---|
| Project configuration | Project method, native profile choices, required checks, capability declarations and approved policy references | Project-maintained; accepted revisions distinguish proposals from governing settings |
| Local bindings | Installed tools, local execution paths and references to account/connector access | Operator-maintained; secrets remain outside shareable configuration and run artifacts |
| Admitted profile | Resolved settings plus their origins, task revision, authority, required capabilities and asset identities | Supervisor-owned immutable input for an admitted run/attempt revision |
| Desired native launch | Provider-specific commands/settings/context prepared from the admitted profile | Adapter-generated; never called proof of effective configuration |
| Native observation receipt | What native resolution/events/probes confirm, contradicted or cannot expose | Adapter reports; supervisor validates before relying on it |

Recommendation: required role/skill implementations ship with Loam. Project extensions reference explicit local assets and retain native metadata/support files. Record the loaded content identity and resolution route; a name alone is insufficient. Trusted extensions can contain executable code, so approving a directory name does not grant later changed content authority. Candidate edits to config or extension files are proposals for a future admitted revision, not modifications of current policy.

## Field-specific composition and authority

Recommendation: do not use a generic last-value-wins merge. Validate syntax, known core keys, compatible schema and referenced assets first. Native-specific settings remain namespaced and adapter-validated. Unknown fields in the selected profile are configuration errors; a profile for an unused provider need not require that provider installed.

| Field class | Composition rule |
|---|---|
| Ordinary project preferences | Versioned defaults plus explicit project choices, then an authorized task-specific selection where applicable; record origins |
| User-controlled model and effort | Use accepted role mapping or the user's explicit current selection. Ticket text, environment variables and native defaults cannot silently change it |
| Execution permissions and publication | Task requests can narrow admitted authority; expansions need existing or new explicit authorization. Organizational/native/host restrictions still apply |
| Method and required checks | Resolve from the admitted task/project revision. Worker output cannot remove a required check or turn an unavailable review into success |
| Machine bindings | Resolve approved executable/account references locally. Diagnose missing prerequisites without modifying global settings |
| Native features | Preserve declared skills, subagents, workflows, tools, connectors and context facilities where supported; incompatible required capabilities produce a specific blocker |

The model/effort policy covers driver, investigators, builders, reviewers, advisors, memory jobs and nested workflow calls. In this Loam design, Codex is driven by Astra with only Astra/Sol/Terra permitted; Claude is driven by Fable 5.1 with only Fable 5.1/Opus 4.8 permitted. The user controls role selections and effort. No cost-driven fallback or automatic translation between providers' effort levels. Exact provider identifiers and supported role controls need compatibility checks; this step does not invent an effort value for the user.

Recommendation: credentials prove access, not authority to publish, spend without limit or change models. Native managed policy cannot be overridden by Loam. If a host restriction prevents required execution, report incompatibility and retain work. Do not broaden host permission to make the profile pass.

## Preparing and observing a native launch

1. Resolve the admitted task revision, project profile, explicit local bindings and required assets.
2. Validate role/model/effort choices, capabilities, permission boundaries and completion requirements against the applicable authority. Report the exact source of a conflict.
3. Prepare the native launch using provider-supported settings/context paths. Keep native system behavior and declared capabilities. Do not mutate the user's global configuration.
4. Before effectful work, validate required load conditions using static checks and, where necessary, later authorized capability probes. Record what is confirmed versus unknown. Startup hooks and connector startup are themselves execution, so this boundary must precede their activation too.
5. Bind the attempt to the admitted profile and observation receipt. Preserve native session/event identities for the supervisor's later execution/recovery contract.

Recommendation: observability and enforcement are different. A logged requested model is not a resolved model; a resolved model is not proof of all hidden provider-internal routing. Require the controls/observations needed for the declared profile, expose remaining visibility limits and never fabricate a field. Lack of required controllability blocks that autonomous profile. This does not disable unrelated interactive native use.

Recommendation: snapshot every policy-relevant input that can be controlled, including extension content and native launch settings. Native policies or tool versions outside Loam's control are recorded dependencies. A start/end hash comparison cannot prove that live-reloaded settings were stable between checks. A profile claiming stable policy needs a verified immutable/constrained source mechanism, not polling alone. Detected drift creates an explicit interruption/reconciliation event; resume uses a compatible snapshot or a newly admitted revision.

## Provider evidence and adaptation

Verified: current bin/factory:383 uses the Codex model variable only as a ledger label; launch at 811-815 supplies a legacy workspace sandbox choice, Git write roots and no explicit model/effort. Current Claude launch at 843-847 selects user settings plus frozen worker settings and strict MCP without an explicit MCP configuration. worker-settings.json has deny rules and a Stop hook but no sandbox block. These paths do not establish the seed settings as the effective worker configuration.

Verified: Codex documents CLI overrides above trusted project layers, profiles and personal defaults; managed requirements remain constraints. Project layers depend on trust and working-directory scope. A personal named profile is therefore not a self-contained project policy. [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-basic), [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

Verified: Claude documents merging of settings lists, reloading of ordinary settings and managed-policy precedence. The independent audit found that malformed ordinary settings can be skipped in headless operation. A frozen additional JSON file does not replace every inherited setting. [Claude settings](https://code.claude.com/docs/en/settings).

Verified: Claude programmatic mode preserves native context facilities. Bare mode changes discovery and authentication behavior, including subscription use. Recommendation: do not use bare mode as the default portability fix, and do not assume relocating configuration preserves native authentication. [Claude programmatic execution](https://code.claude.com/docs/en/headless).

Recommendation: adapter-specific launch preparation with explicit inherited surfaces is the preferred approach. Blanket inheritance leaves hidden dependencies; replacing all native configuration risks losing capabilities and auth. Exact settings isolation is a prototype question. Preserve native metadata for skills and agents rather than reducing every asset to pasted Markdown. Project instruction discovery and changing working directories need probes too.

## Concrete example

Illustrative project: a data export application. Its owner asks for an export feature, selects the Codex factory profile and retains the approved Astra effort choice. A project extension supplies export-specific review criteria.

The admitted profile binds that role policy, extension content, worktree/output access, required export checks and current publication authority. The adapter must confirm the intended settings and assets load. A conflicting personal default cannot silently win. If a required connector is unavailable, an already-authorized alternative may be used and recorded; otherwise only the dependent stage is blocked, with independent work continuing where it remains valid.

The same job through the selected Claude profile uses Fable 5.1 and its approved effort, native Claude context/tools and declared role assets. The method, task revision and evidence obligations stay the same. The internal team mechanism may differ. This is operational equivalence, not a claim of identical capabilities, model behavior or effort scales.

## Proposed changes and runnable acceptance interfaces

The modules and test commands below are proposed, not implemented or executed. Unit fixtures must use fake native launches and nonsecret synthetic configuration. Required tools cannot be absent while the release gate reports success.

| Change | Existing implementation | Dependency | Future runnable check |
|---|---|---|---|
| Shared configuration resolver and authority validation | Shell defaults, ticket parsing and environment overrides in bin/factory | Accepted ownership model, schema/authority record | python3 -m unittest discover -s bin/tests -p test_factory_profiles.py |
| Native launch preparation and observation receipts | Direct worker commands, model ledger label, frozen settings | Resolver, adapter capability interface and structured receipts | python3 -m unittest discover -s bin/tests -p test_factory_native_profiles.py |
| Asset resolution with native metadata | Personal skill resolver; pasted bodies/name invocation | Bundled asset manifest and project extension identity | Same native-profiles command |
| Drift and continuation behavior | Selected frozen files, fresh native processes each round | State transitions, compatible snapshot/revision handling | python3 -m unittest discover -s bin/tests -p test_factory_profile_recovery.py |

Required cases: ordinary preference precedence; environment and ticket attempts to alter model/effort; required invalid/unknown settings; nested-agent effort conflicts; absent required capabilities; same-name personal skill collision; permitted attempt output versus forbidden supervisor-state writes; changed configuration during an attempt; new native session after resume; pre-existing native hooks/MCP settings; template update that changes effective defaults; one provider absent when only the other is selected. Passing fake tests establishes adapter logic, not actual native enforcement.

Later live probes must demonstrate effective parent/descendant choices, required skill identity and metadata, native context after compaction/resume, intended account access without global mutation, explicit connector loading and actual state protection. They require separate runtime authorization and a concrete bounded fixture. No prototype is being run in this phase.

## Open mechanisms and next discussion

Pending prototype: exact native configuration isolation while preserving auth and capabilities, observation support for descendant settings, trust/working-directory behavior, dynamic hooks/connectors and policy drift. Recommendation is decided enough to specify interfaces without guessing those mechanisms.

Next: define native-worker start/observe/interrupt/reconcile/continue/collect responsibilities and the supervisor transitions consuming their receipts. User ticket authority, storage backend and exact per-role effort mapping remain open; they do not block this configuration design.

## Self-attack and limits

A personal hook could run before the profile is checked: readiness must examine load surfaces before launch. A provider could silently ignore a malformed setting: validate locally and corroborate required behavior. A nested workflow can override effort: validate/observe descendants. A changed native policy can load mid-attempt: immutable-source enforcement must be proved or the profile cannot claim stability. A compiled launch can still differ from actual configuration: keep desired and observed records separate. Each is covered by a contract and proposed probe; none is an implemented guarantee.

Recorded UTC: 2026-09-14T01:13:43.916708+00:00

## Review and artifact verification

Verified: independent native-source critique was incorporated, including settings merging/reload, descendant effort, desired-versus-observed configuration and unsupported native isolation. A fresh-context document reviewer found no actionable correctness gaps. This verifies design coverage only, not runtime behavior.
