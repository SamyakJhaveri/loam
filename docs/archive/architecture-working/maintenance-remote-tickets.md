# Maintenance and remote execution implementation additions

Status: planned work only. These tickets extend the accepted first-run, native-binding and ASSET/ENV plans. They do not authorize implementation. All paths below are proposed canonical source paths; all acceptance commands are proposed launcher interfaces, not existing runnable APIs.

## Order and source ownership

First establish the accepted protected installation, project ownership/store and native profile contracts. Then implement catalog readiness, remote execution and recovery, native/GPU integration, update handling and the complete remote proof. Reuse the existing execution host and curated catalog. Do not introduce a second project scheduler, asset registry or provider reasoning framework.

### MAINT-01: compatibility and actionable readiness

Existing behavior: curated assets occupy the current seed/plugin layers; existing diagnostics do not establish the proposed admitted installation or remote profile.

Proposed changes: extend `seed/.loam/factory/assets/runtime-manifest.json`, `src/contracts/installation.ts`, `src/commands/status.ts`, `src/commands/doctor.ts` and `src/profiles/admitted-view.ts`, relative to that same factory directory. Record release/protocol, selected asset and executable identities, tool capabilities, permissions and target requirements. Consume the ASSET preservation/adoption map instead of copying it into another authoritative catalog. Setup resolves native executables independently of an interactive shell. Status is observational; doctor returns concrete failures and repair instructions without installing packages or invoking models.

Dependencies: independent release admission, ENV-01 and ASSET-01/05. Add installation fixtures under `seed/.loam/factory/tests/installation/`.

Acceptance: `node .loam/factory/launcher.mjs verify installation` in a generated project. Expected failures: missing selected dependency, native drift, incompatible runner, misleading SSH alias and missing non-interactive PATH. Expected success: valid explicit executable paths and compatible selected capabilities on each host. Optional unused assets must not block unrelated work. No implicit install or paid probe occurs.

### REMOTE-01: one SSH transport and persistent Linux execution

Existing behavior: the accepted execution host is a local reconnectable process proposal. Inspected ParBench scripts use tmux and flat logs, without the proposed durable launch protocol.

Proposed changes under `seed/.loam/factory/`: `src/contracts/remote-job.ts`, `src/execution/ssh-transport.ts`, `src/execution/runner.ts`, `src/execution/job-ledger.ts`, `src/platform/linux-services.ts` and existing host/spool modules. Add `tests/execution/remote-recovery.test.ts`. The project store remains the task authority. The remote ledger holds dispatch/resource/evidence facts. Persist request/body identity before dispatch, enforce owner generation, reconcile ambiguous starts and replay captured events without launching twice.

Setup documentation in `seed/docs/factory/SETUP.md` covers enrolled target identity, protected control credentials, explicit executable paths, user-service lifetime after logout, application readiness and disk-backed spool. Service-manager runtime state and journald are supplementary evidence. Candidate code cannot reach unrestricted operator SSH credentials or mutate runner authority. Direct operator SSH is outside managed receipts until explicitly attached.

Dependencies: MAINT-01, protected platform boundary, local lifetime lock and spool/store recovery. Acceptance: `node .loam/factory/launcher.mjs verify execution` and `node .loam/factory/launcher.mjs verify store`. Expected failures remain explicit unknown/pending states for an ambiguous launch, lost receipt, stale owner, inaccessible old target, disk exhaustion and interrupted restore. Expected success includes same-request replay, independent host survival across runner restart and old-generation rejection. No automatic retry after reboot.

### REMOTE-02: native workers, GPU inputs and disconnected policy

Proposed changes under `seed/.loam/factory/`: extend `src/adapters/claude/`, `src/adapters/codex/`, `src/execution/input-bundle.ts`, `src/execution/resource-policy.ts`, `src/execution/offline-policy.ts` and `tests/execution/remote-policy.test.ts`. Bind native tool requests to real caller authority; retain actual remote provider session/model/effort and distinguish remote workers from local native children. Local Mac tools, including admitted computer-use tools, remain local capabilities. Register Linux execution as another capability, not a replacement for them.

Bundle selected tracked/untracked work and declared data with content identity. Validate transfer paths and artifacts. Keep the factory toolchain separate from the experiment environment. Record GPU requirements and enforce admitted time/resources locally on Linux. Reservations arbitrate runner-owned jobs; external workloads remain observed contention. Persist offline policy and control lease before launch, with bounded clock/restart behavior. Cancellation delivery and observed termination are separate evidence.

Dependencies: REMOTE-01, provider binding probes and accepted D-OFFLINE (mixed policy). Acceptance: `node .loam/factory/launcher.mjs verify execution`, plus separately admitted real native/GPU probes in `verify complete-slice`. Expected failures include changed request body, escaping input paths, missing environment, external GPU contention, expired control lease, offline approval, forged lead identity and stale-result acceptance. Expected success: fixed admitted job survives transport loss within its bounds, with correctly recovered logs/results; native work obeys its selected offline profile. Fixtures do not prove native or scientific behavior.

### MAINT-02: reviewed release adoption, retention and replacement

Proposed changes under `seed/.loam/factory/`: `src/commands/update.ts`, `src/commands/transfer-owner.ts`, `src/artifacts/retention.ts`, existing migration/restore modules and `tests/installation/update-remote.test.ts`. Extend `seed/docs/factory/SETUP.md` and Loam release fixtures in `bin/tests/factory-release-render.test.mjs`.

Show affected assets, permissions, dependencies, active work and schema compatibility. Stage while jobs run; drain affected shared runner/native installations before activation. Preserve active snapshots. Keep projects' explicit extensions and report conflicts. An older runtime must support the current schema before code rollback; a database restore still reconciles surviving remote work. Retention protects referenced evidence and unresolved jobs. Target replacement enrolls a new identity. Moving the Mac authority requires consistent state and separately authorized fencing/rebind, not an SSH alias edit or a larger claimed generation.

Dependencies: REMOTE-01/02 and existing quiescent restore contract. Acceptance: generated-project `verify installation`, `verify store` and `verify execution`; Loam release `node --test bin/tests/factory-release-render.test.mjs`. Expected failure evidence: protocol mismatch, update during affected active work, incompatible downgrade, candidate credential access, copied stale ownership and premature artifact deletion. Expected success: staged update adopted after drain, retained local customizations/evidence and rejection of the old controller after transfer.

Preserve request tombstones or permanently closed submission epochs through retention and restore. Fence project enrollment across every mutating operation, including fresh submissions and queued dispatch, not just existing job controls. Required negative fixtures: completed-job replay after cleanup, replay after stale ledger restore, old-owner fresh submit after transfer and a target that has not yet acknowledged rebind. None may cause a second launch or claim exclusive new ownership prematurely.

### REMOTE-03: complete proof and operator guide

Extend the accepted complete-slice fixtures and `seed/docs/factory/SETUP.md` with the actual Mac-to-jhaveris story: start a native lead locally, dispatch a remote native worker, launch a bounded GPU experiment, lose the launch reply/connection, recover the same job and collect verified evidence for a current local lead decision. Exercise offline cancellation, runner restart, machine reboot and new-controller fencing separately. A negative research result is valid evidence; process exit is not acceptance. Record remote resource/environment facts needed to interpret the experiment.

Dependencies: preceding tickets, real provider access and separately admitted bounded GPU probe. Acceptance: `node .loam/factory/launcher.mjs verify complete-slice` for each provider with both host readiness reports, plus mechanical installation/store/execution groups on each host. Report fake fixtures, real native probes and real GPU results separately. These commands have not run because the proposed factory is unimplemented. This adds a remote proof; ordinary research tasks are not required to use a GPU.

## Accepted policy and next work

The user selected mixed behavior: already started fixed GPU jobs continue within agreed limits; agents default to interruption. The [job record and operator flow](remote-job-and-operator-flow.md) add REMOTE-02 lease/start/reconnect/budget fixtures and MAINT-02 admission-drain/update-recovery fixtures. Separate authorization is needed for bounded autonomous native exceptions. Queue-by-default with fail-fast is accepted for the user's personal jhaveris machine. Keep routine queue/expiry/resource mechanics simple and choose implementation defaults without another questionnaire. No multi-user scheduling subsystem is needed. Next consolidate the remaining bootstrap/setup/update tickets. Runtime implementation remains deferred.
