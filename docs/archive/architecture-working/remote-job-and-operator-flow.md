# Remote job record and operator flow

Status: D-OFFLINE is accepted. Fixed GPU runs continue within agreed limits; agents default to interruption when the Mac loses contact. The concrete mechanisms below are recommendations for the deferred TypeScript implementation. They extend the [remote contract](remote-execution-contract.md) and [maintenance tickets](maintenance-remote-tickets.md).

## What the accepted choice means

An already started, fixed GPU experiment may keep running without the Mac, within its admitted time, resource and access limits. This permits the recorded command and declared checkpoint/cleanup behavior. It does not permit another experiment, a larger budget or an embedded autonomous model loop. A task using native reasoning during execution is classified as native work even if it also uses a GPU.

Native workers default to interruption when control loss is declared. Deny new supervisory work and positive approval replies, capture output and observe what stops. A stop request is not proof that every child or external effect stopped. A later request for bounded autonomous native work needs explicit task-specific authorization; the mixed-default selection does not grant it.

Recommendation: use the existing renewable lease, a time-limited grant from the current owner. Locally detected controller disconnection or runner loss immediately closes new-submission, prepared/queued-dispatch and positive-approval gates. A failed renewal closes those gates; the previously admitted lease deadline triggers native interruption. This recorded grace period tolerates short failures; no exact duration is selected here. The job host enforces the gates and expiry independently of the runner. An undetected partition is bounded by lease expiry, not an impossible promise of instant physical-loss detection. A completed current-authority handshake may renew control and reopen eligible gates before expiry; it cannot undo a recorded interruption, reopen a pending cancellation or extend the execution budget.

## The job record

Use a validated versioned contract for the following groups. These are proposed data requirements, not implemented field names or a second project task database.

| Group | Recorded content | Why it is needed |
|---|---|---|
| Identity | Project instance, task revision, attempt, request identity, request-body digest, target machine/runner, owning generation | Lost launch replies resolve to the same request; changed content or an old owner cannot reuse it. |
| Work | Fixed GPU or native-worker kind, exact command/arguments and working directory, selected native role/model/effort when relevant | A role label or GPU usage cannot conceal different behavior or grant authority. |
| Inputs | Selected source snapshot including intended untracked changes, dataset/model identities, declared mounts and writable outputs | A branch name and a path do not establish what ran. |
| Environment | Factory release/protocol, admitted native executables, separate experiment environment, required tools and GPU compatibility | Setup failures and scientific results must be traceable to the actual environment. |
| Limits | GPU/device requirements, allowed concurrency, maximum execution duration, declared access, stop/checkpoint method and bounded stop grace | The Linux host can enforce the agreed limits while the Mac is unavailable. Stop grace fits inside the total authorized resource envelope. |
| Offline control | Accepted policy, lease identity/expiry, maximum execution deadline, authority barriers and any separately authorized exception | Renewing contact cannot expand the job or resume interrupted reasoning implicitly. |
| Execution facts | Admission, dispatch evidence, service/process identity, started/ended observations, exit/termination facts and unresolved descendants | Durable intent, actual start and actual end remain distinct. |
| Evidence | Ordered log positions, output manifest/digests, retained locations, collection/verification state and minimal replay tombstone | Reconnection and cleanup must not lose evidence or duplicate work. |

The remote ledger owns these execution observations. The Mac's project store owns task decisions, current scope and acceptance, linking the remote observations. Do not maintain competing writable copies of task acceptance. Record authoritative Linux duration/deadline evidence without assuming the Mac and Linux clocks agree. Restart, suspend or clock adjustment cannot mint a fresh budget; uncertain elapsed-time enforcement blocks continuation rather than silently granting more time.

## Initial setup

1. Prepare the independently admitted factory release and selected native profile on the Mac. Resolve exact executables; register protected project storage and controller identity.
2. Prepare the matching release on Linux, separately from the project's experiment environment. Enroll its machine/runner identity and bind the local target name. Preserve SSH host-key checks and isolate managed control credentials from candidate code.
3. Establish the Linux runner's service lifetime after logout, local durable ledger/spool and application readiness. Configure independent job hosts so runner restart does not become job restart. The prior observation of disabled linger is a setup obligation, not permission exercised here.
4. Check required capabilities, explicit non-interactive executable paths, GPU access and declared environment. Keep observations separate from actual bounded native/GPU probes. Setup does not silently invoke a model or experiment.
5. Save a readiness report and initial consistent recovery records. A capability that fails its proof stays unavailable with a concrete reason; unrelated local work can remain available.

## Launch, monitor and recover

Before launch, the local lead supplies the bounded job request and the controller checks it against existing user authority. Show its target, inputs, resource/time envelope and offline behavior in a readable summary. A new confirmation is needed only when the request exceeds existing authorization; do not ask for every ordinary tool call.

The controller durably records intent; the runner records the same request and starts a protected job host only under current authority. The host checks both the admitted dispatch grant and its locally maintained connection/lease gate immediately before native or GPU execution. A detected disconnect blocks this start even when the old lease has not yet expired. The actual-start record distinguishes a running job from merely prepared or waiting work. An ambiguous start is reconciled rather than retried. Once disconnection is detected locally or the lease expires, prepared/waiting requests cannot become new offline execution. The continuation exception covers an execution that already crossed the authorized start boundary, not a queue of future work.

Recommendation: expose the existing logical submit/status/events/cancel/collect operations through native tools and CLI. A status view distinguishes waiting, last seen running, disconnected, interruption requested, ended and outcome unknown. Display last contact, limits, log availability and pending requests. These labels summarize separate facts; a failed SSH call never directly writes "job failed".

On reconnect, verify machine, release and current owner generation, collect missing evidence, and deliver pending cancellation/scope barriers before allowing further control. A GPU job that remains active is monitored under its original limits. A GPU job that finished offline supplies its result for current checks. An interrupted native worker stays interrupted: continuing native reasoning requires a current authorized action after reconciliation. Native session continuation may reuse supported context, but is still a new execution action; transport replay is not that action. Existing user authority can permit this without a fresh permission question unless scope/access changed or execution remains ambiguous.

Machine reboot does not automatically retry a GPU command. A resumable experiment may start a separately authorized attempt from a verified checkpoint. Link its provenance and budget explicitly; the interrupted attempt does not become a successful uninterrupted run. Retain old request identities across cleanup and recovery.

## Update flow

Stage the new release and show affected assets, permissions, environments and active jobs. Validate the proposed installation first. Wait for affected shared runner/native jobs to become idle before activation; new work must not race that drain. Close admission under the update transaction before taking the final idle check. Coordinate the matching controller/runner release, verify readiness, then reopen admission. A crash leaves a named pending update for reconciliation. Jobs and unresolved old effects retain their evidence and installation references.

Project customizations remain configuration/extensions or an explicit fork. Incompatible schema rollback uses the existing recovery procedure; it cannot erase remote execution. Use [maintenance rules](maintenance-and-remote-work.md) for retained artifacts, replacement machines and owner fencing.

## Acceptance additions and next decision

Add REMOTE-02 fixtures for GPU continuation with no budget extension; native lease expiry while the runner is down; failed renewal followed by reconnect before expiry versus reconnect after interruption; prepared dispatch during detected-loss grace; positive approval refusal while disconnected; waiting/prepared work at lease expiry; an ambiguous authorized start; native reasoning hidden in a GPU request; clock/suspend uncertainty; and checkpoint resume as a linked new attempt. Add MAINT-02 fixtures for admission racing update drain and a crash between target/controller activation. The existing proposed installation/store/execution/complete-slice commands remain unimplemented and unrun.

Accepted D-PERSONAL-GPU: queue by default, with fail-fast available. The user states that jhaveris is their personal machine for their own use and asks not to overcomplicate scheduling. Design for that single-user workload. Start eligible work when capacity is available; if the user's own work overlaps, use a simple visible, cancellable queue with expiry. Fail-fast returns immediately when requested. No multi-user scheduling, priority system or further resource-policy questionnaire is required. Queue order, expiry defaults and ordinary resource checks are routine implementation choices, configurable when a real task needs it. Preserve current-authority checks, original execution bounds and the prohibition on new starts during detected disconnection. Personal ownership does not remove checks for an already running job.

Next: consolidate the remaining bootstrap, installation and update work into a short ordered implementation plan. Explain material tradeoffs if the concrete plan exposes one; do not create another decision gate for routine mechanics. Runtime implementation remains deferred.
