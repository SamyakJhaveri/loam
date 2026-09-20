# Remote execution without losing ownership

Status: proposed extension of the accepted execution-host contract for Mac-led Linux agents and GPU jobs. No remote runner, service or job was installed or launched in this design step.

## One owner and a durable remote witness

Recommendation: the Mac project supervisor remains the sole authority for task revision, acceptance, memory activation and lead decisions. Its SQLite store stays local. A small Linux runner from the same factory release owns a local launch/job ledger, resource reservations and evidence spool. The runner answers whether a particular admitted job was dispatched and what happened; it cannot decide whether the research succeeded or create another task.

The transport uses SSH to reach an enrolled runner endpoint, which attaches to the persistent service. Losing the SSH process loses a connection, not the job identity. Every request names the project instance, owner generation, target machine/runner, action/attempt and request identity. The admitted request body is hashed. Reusing an identity with different content is rejected; resending the same request returns its durable state.

Recommendation: use the same execution-host code to capture local and remote native/check jobs. The Linux service dispatches independent job hosts through the operating system's service manager, rather than making expensive work a disposable child of the SSH session. Each host retains the accepted spool and pending-native-request semantics. Runner restart must reconcile already dispatched hosts before dispatching anything conflicting.

## Native access and authority

Recommendation: expose remote work through a native tool/command binding that calls the same submit/status/events/cancel/collect operations. Local native tools continue to reason about and request actions. Only trusted control code has the credential and access needed to reach the protected runner endpoint. Candidate scripts cannot use an unrestricted operator SSH identity or agent socket to edit runner state, bypass the admitted workspace or impersonate the control client.

The operator's ordinary `ssh jhaveris` access remains separate from managed execution. If a user manually starts work outside the runner, record it as external work until its identity/state can be explicitly attached; do not claim it has factory receipts or cancellation guarantees. Managed profiles must prove the runner boundary even when selected tools include SSH or remote services. A prose instruction to use the wrapper is not enforcement.

Recommendation: SSH authenticates the machine/account transport; project-scoped runner enrollment and owner-generation fencing establish Loam control authority. Preserve existing SSH host-key checks. A changed alias, host key, runner identity or incompatible release requires reconciliation. A remote lead is not inferred from a role name, model name or SSH username. Native root decisions remain bound to the specifically admitted lead session.

## Source, environment and resources

Recommendation: transfer an explicit input bundle or use a verified existing remote input identity. Include intended tracked and untracked changes, declared data references, entry command/arguments, working directory, environment identity, output contract and resource/offline policy. A Git branch name alone does not identify the working inputs. Build the transfer from authorized inputs; do not sweep secrets or the entire home directory into it.

Transfer to a staging location and verify its manifest before publishing the immutable input view. Reject archive traversal, escaping symlinks and unexpected executable/setup behavior. Source input admission is separate from executable runtime admission. GPU packages, models and datasets are explicit experiment dependencies; a code hash does not freeze them.

Recommendation: each GPU request declares target capability, device/memory requirements, concurrency policy, a time/resource bound and cancellation/checkpoint behavior. The runner arbitrates reservations among the jobs it owns. It also observes existing machine use before dispatch and reports contention. Device selection or a Loam reservation does not prove exclusivity against unrelated users/processes. Never kill another workload to satisfy a request. Do not introduce Slurm solely for this workflow; integrate a scheduler only when the selected machine actually requires one.

## Launch and reconnect

1. The Mac durably records launch intent before sending it.
2. The Linux runner validates current owner authority, input/profile identity and capacity, then durably records the request before dispatch.
3. A protected job host receives the durable identity, captures output and records process/service identity. A repeated submit does not launch another host/job.
4. The Mac records the returned receipt. If the receipt is lost, it asks about the same request rather than minting a new one.
5. On reconnect, exchange job state and event positions, replay missing frames, then separately restore current control authority.

Recommendation: a crash between durable launch intent and observed process start is an ambiguous dispatch until reconciled with the host/service identity. Do not claim exactly-once execution from request IDs. If proof is unavailable, retain unknown execution and block conflicting dispatch. Stable service/job identity and the host lifetime lock help reconciliation; missing logs or a missing process ID alone do not prove nothing ran.

Use the accepted ordered, bounded spool and ingestion cursors. A repeated transport frame is deduplicated; identical output emitted twice by a job remains two observations. Local display may say disconnected or last seen running. It cannot say running now, stopped or completed from stale contact evidence.

## Offline execution and cancellation

Accepted D-OFFLINE: the user selected the mixed policy. Already started fixed GPU jobs may continue only within their pre-admitted bounds while the Mac is disconnected. Capture output locally. Permit only already declared checkpoint/cleanup behavior, not new experiments or access approvals. A remote native agent defaults to interruption and no new supervisory work/positive approval replies. Capture surviving activity honestly; an interruption request is not proof all descendants stopped. Bounded autonomous native continuation is an explicit alternative profile, not an implicit consequence of SSH loss.

The offline policy is stored on the runner before launch. A time/resource limit must be enforced remotely even if the Mac never returns; if the chosen mechanism cannot enforce a required bound, that profile is unsupported. Reboot or runner recovery cannot reset the consumed budget and authorize fresh execution. No automatic GPU retry after reboot. A project-specific checkpoint resume is a separately authorized new attempt with linked provenance.

Recommendation: each independent job host receives that persisted policy and enforces its own expiry even while the runner is down. A renewable control lease means a time-limited grant from the current owner; its admitted timeout tolerates brief network failures without treating every socket replacement as a new job. Locally detected controller disconnection, runner loss or failed renewal immediately closes new-start and positive-approval gates. The admitted lease deadline triggers native interruption if current control has not been re-established; failed renewal alone does not shorten that deadline. Job hosts enforce both the connection gate and lease at final dispatch. Undetected loss remains bounded by lease expiry. See the [operator flow](remote-job-and-operator-flow.md) for reconnect-before-expiry and interruption behavior. Fixed GPU deadlines remain independent of lease renewal. Reconnecting or restarting cannot extend the admitted maximum budget; expired or uncertain authority cannot grant new actions. Wall-clock changes and machine suspend need explicit monotonic-time/budget fixtures. Already dispatched effects may survive an interruption, so the host continues evidence capture and reports unresolved descendants.

Recommendation: cancel is a durable request, with separate requested, delivered, acknowledged and observed-ended facts. A Mac-side revision or pause while disconnected cannot be advertised as an immediate remote stop. On reconnect, deliver current barriers before granting new control. Results captured offline remain evidence but cannot accept a superseded candidate, revised criterion or revoked improvement.

## Linux lifetime mechanism

Recommendation: use a persistent user service for the runner and independent service-managed job hosts. This gives an ordinary Linux maintenance surface. The service starts from an exact installed executable with an explicit environment and a readiness handshake. Service start success does not prove Loam is ready. Shell `nohup` or tmux can remain operator conveniences but are not the authoritative job ledger.

Verified: read-only inspection found a reachable user systemd manager on `jhaveris`, with `Linger=no`. Enabling linger is a candidate setup prerequisite for surviving logout and starting the user manager at boot; it has not been changed. The investigator read installed systemd manuals: service and scope lifetime differ; transient unit definitions do not survive reboot as a promise to resurrect the same job. The runner's disk ledger/spool, not journal availability alone, preserves evidence. [Inspection record](maintenance-validation.md) records the scope and limitations.

Recommendation: runner restart reconciles surviving independent job hosts; machine reboot records interrupted/unknown outcomes and never auto-replays a prior launch. The runner service can restart for observation/reconciliation without restarting native reasoning or GPU work. Stopping/upgrading the runner and stopping its jobs are separate operations, covered by fixtures and the update drain policy.

Missing or corrupt registered runner storage is recovery, not empty-runner setup. Back up durable ledger, enrollment/fencing records and referenced spool/artifact identities consistently. A restored ledger is stale until it reconciles job-host evidence and current owner generations; it cannot forget dispatches and launch them again. Keep a protected external maintenance/history marker across runner restore, following the project store's existing restore pattern. Spool deletion still requires the retention contract. Replacing a lost runner uses explicit enrollment/recovery and preserves unresolved old work.

## Result collection and cleanup

Recommendation: collect a completed output manifest, required artifacts and recorded exit/termination evidence. Verify source/profile/job identity and artifact digests, then let the Mac supervisor apply current checks and acceptance. A native turn ending, an exit code of zero or a GPU utilization drop is not sufficient evidence by itself. Tool/runtime failures and scientifically negative results remain different outcomes.

Logs are streamed incrementally; large artifacts stay remote until needed, with a durable location and retention record. Before deleting a referenced remote artifact, obtain a verified retained copy or explicit policy authorization to abandon it. A broken SSH link is not a garbage-collection signal. Cleanup shows what will be removed and respects active work, unresolved outcomes and evidence references.

Retain a minimal durable request tombstone after bulky logs/artifacts are retired: request identity, admitted body hash and terminal/unknown disposition. A tombstone is the small record that prevents an old completed request from looking new. It can be removed only after its entire submission epoch is permanently closed to replay. Backup/restore must preserve these closed epochs or tombstones; restoring an older view cannot reopen submission before history reconciliation. Cleanup followed by replay must return prior/retired state or reject the closed epoch, never dispatch again.

## New Mac, new Linux and control fencing

Recommendation: each job has one owning project instance and control generation. The runner serializes and persists generation changes and rejects old control requests after transfer. Moving authority to a new Mac requires a consistent state transfer/recovery record and a separately authenticated operator-authorized rebind. A generic client cannot claim a higher generation to acquire jobs. Lost prior state requires reconciliation, not adoption based only on a job name.

Fence the project enrollment on each runner, not only previously known jobs. Every mutating operation, including a fresh submit identity, queued dispatch, lease renewal and cancellation, validates that enrollment's current generation. Transfer serializes with admission and dispatch, then reconciles work already admitted by the old owner. An unreachable target remains pending rebind; the new controller cannot claim exclusive control there or send new work until it is fenced. After transfer, the old Mac must fail even when it submits an entirely new job identity.

A new Linux target gets a new machine/runner identity and readiness check. An existing SSH alias pointing there cannot collect, cancel or rerun jobs from the previous machine. If the old machine is gone, retain the old jobs' last observed state and available artifacts; replacement hardware does not turn unknown work into successful or never-started work.

## Required failure cases

Proposed tests, not executed: lost launch reply; duplicate submit; changed body under the same ID; replay after terminal cleanup or stale ledger restore; disconnect during output; Mac sleep during a bounded GPU run; offline cancellation; native agent tool request while disconnected; runner restart before/after dispatch; guest/host reboot; missing spool tail; disk full; GPU contention; artifact transfer corruption; stale task revision; old Mac reconnecting or submitting a fresh job after authorized transfer; changed SSH alias; protocol mismatch during update; candidate access to operator SSH credentials or runner storage; remote helper spoofing the local lead. Each must preserve truthful execution and acceptance state.
