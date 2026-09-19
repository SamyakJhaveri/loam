# Factory distribution and update design

Status: distribution and ownership direction accepted by the user; detailed mechanisms and acceptance tests remain proposed. Runtime implementation is not authorized.
Scope: first architecture discussion. Runtime implementation remains deferred.

## Working sequence and checks

- Pin current source and inspect distribution paths. Check: git status --short --branch and git rev-parse HEAD show clean main at d627bb2755ad49865f798bcb095800ddd2ad1ced. Verified this turn.
- Compare source ownership and update mechanisms. Check: reads of copier.yml, docs/ASSET-LAYERS.md, docs/COPIER.md, bin/factory and bin/loam-attach.sh, plus current official Copier documentation, support the claims below. Verified this turn; native behavior remains untested.
- Record the bounded design and critique. Check: a Python artifact check finds this file, required ownership/acceptance sections and valid links; independent critique finds no unresolved contradiction. Verified: document coverage/link checks and fresh correctness review completed; review corrections for legacy adoption and host dependencies are recorded below.

## Authority and recommendation

Verified: the latest user instruction permits proposing removal, replacement or rebuilding of existing Loam and seed components when the architecture requires it. It does not authorize runtime edits in this phase. Existing architecture is evidence and a source of reusable work, not a compatibility obligation for every implementation detail. Changes to already generated projects still need a migration path.

Recommendation: maintain canonical generic runtime source under seed/.loam/factory and distribute it as ordinary source through Copier. Loam's own launcher uses this same runtime. Required shared skills retain their single canonical seed/.agents/skills home; operator guidance ships from seed/docs/factory. The runtime can be rebuilt internally later without changing this distribution contract. Language and module boundaries are not selected here.

## Credible approaches

| Approach | Benefit | Cost or constraint | Judgment |
|---|---|---|---|
| Canonical source in seed | What is developed is directly available to render; no runtime package service required; inspectable project-local source | Release cadence tied to template; local runtime edits need a fork policy; development and rendered paths must both work | Recommended starting point |
| Canonical root source plus generated seed copy | Conventional runtime workspace and independent build tooling; can build a precise payload | Must generate deterministically and reject stale/missing copies; repository carries a distribution copy | Credible if build/packaging needs justify the extra step |
| Pinned runtime package | Separate runtime releases and dependency tooling | Requires publication, availability and explicit installation/update ownership; package alone does not supply native assets or preserve project decisions | Credible later; a vendored release bundle can also satisfy local delivery |

Verified: docs/ASSET-LAYERS.md permits copies with verifier-enforced equality, and the original report permits declared versioned dependencies. Neither alternative is prohibited by settled requirements. An optional factory or a floating launcher back to a personal checkout fails the required product boundary.

## Ownership contract

All paths in the proposed column are design names, not claims that files already exist.

| Owner | Proposed content | Update rule |
|---|---|---|
| Loam release | .loam/factory runtime, bundled role/check schemas, defaults, required shared skills and operator docs | Replace through a reviewed template update; detect deviations from the prior admitted payload |
| Project | .loam/project.toml, project-specific roles/methods/check definitions and shared decisions/evidence | Initialize configuration once; never replace with upstream defaults; propose explicit schema migrations |
| Native integration | Existing .claude and .codex configuration and native instruction entry points | Preserve unrelated settings; apply only proven owned changes or produce a conflict; never assume generic merge semantics |
| Local operator | Credentials, machine paths, local instance association | Document setup and resolve explicitly; no private values in seed or shareable answers |
| Supervisor instance | Runs, attempts, locks, frozen profiles, receipts, private logs | Outside template-managed files; updates do not rewrite active run inputs |

Recommendation: project customization normally uses documented configuration and project assets. Editing shipped runtime code is allowed, but creates an explicit local fork: retain the diff, surface update conflicts and rerun its acceptance checks. Do not silently replace it or call it the unchanged upstream release. A migration back into maintained Loam is a separate reviewed action.

Recommendation: project decisions belong to the project regardless of whether GitHub or files ultimately own ticket authority. This distribution step does not settle that separate question.

Recommendation: keep runtime code free of Jinja substitutions. Template only the thin integration files that need project answers. Resolve runtime root, project root, local instance root and attempt output separately. A manifest records required assets, content identity, modes/symlink targets and configuration/state schema compatibility. Integrity metadata detects inconsistency; it is not protection against a process allowed to rewrite the metadata.

Recommendation: update docs/ASSET-LAYERS.md to distinguish shipped files from instructions loaded into each session. Required runtime code and reference documents do not become always-on prompt content merely because they live in seed.

Recommendation: ship a dependency contract that distinguishes bundled assets, required host executables/libraries with supported versions, and optional services. Readiness checks report the missing or incompatible prerequisite and its documented setup step. Exact runtime language and versions remain deferred. Native credentials are an explicit local prerequisite, never copied from Loam.

Recommendation: shipped presence is distinct from activation. Required research, deliberation, implementation, evidence, memory and recovery mechanisms all arrive. Only relevant role instructions load for a task. Optional external services have declared readiness and fallback paths. A fresh project contains no Loam history. Starting workers, timers or publishing remains an explicit operation.

## Configuration and updates

Recommendation: resolve defaults, project configuration and authorized local bindings into a validated effective run profile. Preserve the origin of each setting. The user-approved model/effort policy constrains that profile; environment variables cannot silently select a different model. Snapshot the resolved profile and instructions at admission. New upstream defaults that change consequential behavior require a visible comparison before activation, even when the project never explicitly set that field.

Verified: current Copier documentation supports operation-aware exclusions and copy-only tasks. skip_if_exists preserves existing content but recreates a missing file on update. For project-owned choices, recommend copy-only initialization with explicit missing-config diagnosis on later updates, not silent default recreation. Source: https://copier.readthedocs.io/en/stable/configuring/ (exclude, skip_if_exists, tasks). These options need compatibility testing against Loam's supported Copier version; no version change is approved here.

Recommendation: distinguish first adoption from a missing configuration after adoption. For projects rendered before the factory existed, provide an explicit reviewed first-factory migration that initializes configuration and maps existing native settings. Record that adoption. After adoption, a missing configuration is diagnosed without silently restoring defaults. This migration also needs conflict handling for a pre-existing .loam directory.

Verified: Copier may leave conflict markers or rejection files and preserves deletion of ordinary template paths. Source: https://copier.readthedocs.io/en/stable/updating/ . Recommendation: the factory verifies required assets itself and refuses new admission while the payload/configuration is incomplete or conflicted. A managed deletion is never silently treated as a valid full installation.

Proposed update sequence:

1. Read the current release identity, local managed-file changes, project configuration and active-run inventory. Preserve a clean baseline for a reviewable update; do not stash or discard user work automatically.
2. Prepare the Copier update in a separate review checkout. Disable activation and external side effects there. Existing root post-render tasks need redesign before this path is usable.
3. Compare managed payload, project-owned content and effective configuration. Preserve project-owned records; prepare explicit migration diffs for incompatible configuration. Report local forks, conflicts and missing required assets.
4. Run completeness, configuration and mechanical factory checks against the candidate update. Show the resulting behavior changes and unresolved blockers.
5. Adopt the reviewed source update for new runs. Existing runs keep complete runtime/asset/profile snapshots; resume through a stable lookup/bootstrap boundary or report an explicit compatibility blocker. Never blend old controller state with new live skill bodies.

Recommendation: use Copier as the update engine initially. A thin Loam update coordinator can supply checks and presentation; it must not become a second independent merge algorithm. Direct Copier usage cannot bypass the factory's admission validation. This update protocol does not yet claim atomic cross-host activation or specify the final command name.

## Components to retain, replace or remove

| Current component | Proposed treatment | Dependency |
|---|---|---|
| Copier seed rendering and release tags | Retain as delivery mechanism | Expanded payload and ownership-aware tasks |
| bin/factory controller | Replace root-only implementation with a thin development entry point plus shared runtime; rebuild internals where later state design requires it | Explicit roots and retained behavioral acceptance cases |
| Personal grader/skill cache resolution | Remove as the required resolver; resolve bundled versioned assets first | Required roles/skills moved to canonical shipped homes, licenses checked |
| Policy extracted from architecture prose | Replace with explicit policy data | Policy schema and validation |
| Claude-only attach with absolute marketplace registration | Retire this behavior; if existing-project onboarding remains supported, make it use the same complete payload and conflict rules | Native configuration migration and Copier adoption design |
| Post-render settings rewrite and implicit Git/GitHub setup | Replace settings rewrite with deliberate templating/integration; separate external setup and activation from rendering/update | Operation-aware tasks and explicit onboarding actions |
| One mixed space for defaults and project choices | Split into managed defaults, project choices and resolved run profile | Configuration schema and field provenance |

## Runnable acceptance contracts for a later authorized slice

Proposed test modules below do not yet exist. Commands are the intended runnable acceptance interface, not test results or instructions to execute now. Fixtures must use fake native children and temporary project instances; no paid calls, installs, publication or scheduler activation. Required fixture tools must already be present or the gate fails clearly, not skips to success.

| Change | Proposed command | Required assertion |
|---|---|---|
| Complete payload and explicit roots | python3 -m unittest discover -s bin/tests -p test_factory_distribution.py | Every declared project kind runs the fake-child ticket from its render with the Loam checkout and personal caches unavailable; required assets, executable modes and links resolve; only declared host dependencies are available; a missing required tool produces a readiness failure |
| Project ownership and migrations | python3 -m unittest discover -s bin/tests -p test_factory_update.py | Update preserves edited project configuration, decisions and extensions; changed defaults are surfaced; deleted config is not silently recreated; migration is reviewable; a pre-factory project receives explicit first-adoption configuration and any pre-existing .loam content is preserved or reported as a conflict |
| Managed runtime/fork handling | Same update command | Local runtime changes are preserved and identified; deleted required files and unresolved merge artifacts prevent admission; no account/timer/GitHub side effects occur |
| Snapshot compatibility | python3 -m unittest discover -s bin/tests -p test_factory_update_resume.py | Interrupted fake-child run resumes using its admitted complete snapshot after update, or reports incompatibility before execution; new run uses the new validated release |
| Same contract in development | Distribution command above | Loam launcher and rendered launcher use the same canonical runtime and asset identities, with different project roots |

These checks depend on later native-adapter and receipt seams. They define acceptance now; they do not preselect supervisor implementation. The first implementation slice must combine generated-project independence with truthful ticket completion. Real native loading and effective permissions need separately authorized probes afterward.

## Consequential choice for this discussion

Recommendation: choose bundled canonical seed source and a supported customization boundary of project configuration/assets plus explicit runtime forks. This keeps projects adaptable while making upstream updates reviewable. The user accepted this ownership model and source-distribution direction; see D-DISTRIBUTE and D-OWNERSHIP in decisions.md. Exact internal filenames can remain provisional while the contract is settled.

## Independent critique incorporated

Verified: an independent agent compared all approaches and the proposed ownership contract. It supported source-in-seed as a starting point and emphasized that configuration hashes do not establish preserved behavior. The effective-profile comparison, explicit native integration conflicts and removal of side effects from update staging address that critique.

Recommendation for the next configuration discussion: project-owned native settings feed a validated factory launch configuration, subject to actual native precedence/capability probes. Managed registration fragments remain a credible alternative. This step does not approve a native compiler, merge mechanism or settings bypass.

## Self-attack and limits

A new default can change project behavior without touching project files: compare resolved profiles before activation. A deleted managed file can survive a Copier update: verify mandatory payload. A frozen run can still import mutable personal assets: snapshot dependency closure and diagnose incompatible native tooling. A managed/native shared file can overwrite unrelated choices: require ownership or an explicit conflict. These are design requirements and acceptance targets, not implemented guarantees.

Not done: runtime code changes, installation, tests, automation or publication. This staged document cannot yet be saved in the original review folder because the active write policy excludes that location.

Recorded UTC: 2026-09-14T00:57:09.491818+00:00

## Fresh review and document validation

Verified: fresh review identified two omissions: first adoption by pre-factory projects, and an explicit host dependency contract. Both are now covered above and in the proposed acceptance checks. No prototype has been run.

Accepted-direction update: the user endorsed the recommendations in this discussion and asked to continue. Configuration/native integration is the next design step, not an implementation start.
