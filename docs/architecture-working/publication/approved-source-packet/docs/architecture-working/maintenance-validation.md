# Maintenance and remote design validation

Status: documentation and read-only investigation. Runtime implementation, package/service changes and real native/GPU runs remain deferred.

## Evidence and preservation

Verified: the pre-edit comparison against `two-host-checkpoint.json` reported `Maintenance baseline preservation: PASSED`. A separate before-copy is retained under `/private/tmp/loam-maintenance-before/` for this step's focused diff. Local HEAD, main, origin/main and live `git ls-remote origin refs/heads/main` matched `d627bb2755ad49865f798bcb095800ddd2ad1ced`. Git status showed only untracked `docs/architecture-working/`. No tracked source edits or commits were made.

Verified: [remote observations](remote-maintenance-evidence.json) preserve the read-only investigator's source locations, command/manual evidence and limits. ParBench's inspected scripts use tmux and flat logs; some reruns overwrite logs or replace a named session. They were read, never executed. DistBench's inspected architecture names an execution interface and SkyPilot; it is design evidence, not an installed adapter. The named scripts location did not exist.

Verified: SSH inspection found a reachable systemd user manager on jhaveris with `Linger=no`. Installed manuals distinguish transient services from scopes, document persistence after logout when linger is enabled, and show that runtime units/journals cannot serve as durable application evidence across reboot by assumption. Service start success is not application readiness. These support the proposed mechanism, not a successful service/disconnect test.

Verified: the permitted GPU inventory lists an NVIDIA GeForce RTX 4070 and driver 580.173.02. No running jobs, user experiment outputs or utilization were inspected. Native CLI absence from non-interactive PATH is not installation absence; the earlier [host inventory](two-host-inventory.json) already records explicit executable resolution.

The official systemd web manual requests returned HTTP 403. The investigator instead read installed primary manuals over the authorized SSH connection. SQLite's [network-use guidance](https://www.sqlite.org/useovernet.html) supports keeping database access local to its engine and using a request interface across machines. This design keeps the project store and remote job ledger local to their respective owners.

## Checks and review

Verified: `python3 /private/tmp/loam-maintenance-check.py design` exited 0 with `Maintenance design checks: PASSED`. The final mode exited 0 with `Maintenance final checks: PASSED`, including after the recovery repairs. These checks compare the before-copy against the previous checkpoint, protect unchanged historical/intake files, validate current document links and required contract/navigation content, parse the remote evidence and reject tracked-source edits. `git diff --check` exited 0; because these design files are untracked, a separate whitespace/conflict-marker scan covers the edited/new documents.

The fresh-context reviewer confirmed independent job-host budget enforcement and stale runner-store recovery, then identified project-wide transfer fencing and retention of request deduplication records. Both gaps were repaired in the remote contract and MAINT-02 negative fixtures. A reread confirmed the repairs without a residual issue within their scope. No live behavior was claimed.

The [step plan](maintenance-step-plan.md) retains the ordered checks. These checks establish document consistency and preservation, not runtime correctness. The earlier `bin/check` result remains historical and is not a new maintenance-runtime test.

## Self-attack and coverage

Self-attack: what breaks this? A runner outage while a native host survives, a stale runner backup, an old Mac submitting a fresh job after transfer, or a replay after terminal cleanup. Repairs require host-local expiry, restore/history barriers, project-enrollment fencing and request tombstones/closed epochs. The second pass found no further concrete documentary contradiction; their feasibility remains an explicit runtime probe obligation.

Unchecked path: actual provider interruption and descendants, native/SSH credential isolation, service readiness and GPU execution. These remain unverified, not silently assumed. No test exercises runtime changes because none were made. Unsupported completion claims were excluded; source/manual evidence does not prove a running service, account access or scientific results.

Request coverage:

- Maintain plugins, skills, commands, workflows, prompts, agents/subagents, calls and environments: ownership/check tables, compatibility and release cycle in the maintenance design; MAINT-01/02 and preserved ASSET tickets.
- Use Mac/Linux now and on replacement hardware: revised host scope, enrolled target identity and explicit owner transfer/fencing.
- Start locally, operate the Mac and launch/monitor Linux native agents/GPU: local-tool preservation, remote contract and REMOTE-01/02/03 proof obligations.
- Simple, effective maintenance: shared execution implementation, SSH transport, operating-system service lifetime, scoped checks and reviewed updates; no additional autonomous reasoning controller.
- Preserve changes, verify main, keep living records: checkpoint comparison, Git identities, updated handoff/index/decision/runtime/first-run/complete-slice records and new maintenance checkpoint.
- Preserve TypeScript, selected native model/effort and explicit profile/curated skills: unchanged accepted decisions and maintenance/profile dependency requirements.
- Continue design and defer runtime: documentation only; no installation, services, native/GPU jobs, seed edits, commits or pushes.
- Explain input/options/consequences/recommendation/next decision: disconnected-policy section and pending user question; mixed policy remains proposed until selected.


## Limits

Not verified: actual runner installation, logout survival, native account/model access, service-launch permission, GPU execution, offline containment, protected SSH credential boundary, generation transfer, software pin compatibility or crash/reboot recovery. No model, experiment or service was launched. No remote configuration, native settings, source-project files or shipped assets were changed. The disconnected execution policy remains a recommendation awaiting user selection.
