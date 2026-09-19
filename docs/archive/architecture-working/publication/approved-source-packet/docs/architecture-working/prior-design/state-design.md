# Durable operational state and recovery boundary

Status: SQLite plus artifact files and the storage/recovery direction are accepted by the user. Detailed records and runtime verification remain under development; runtime implementation is deferred. Read alongside loop-design.md, memory-design.md and decisions.md. Examined clean main: d627bb2755ad49865f798bcb095800ddd2ad1ced.

Critical point: a durable state transition must neither invent completed work nor authorize duplicate execution after a crash.

## Work and checks

- Inspect current state writes, concurrency admission and dependencies. Check: git status/rev-parse, repository-wide case-insensitive source search, bin/factory reads. Expected: exact existing authority and dependency boundaries identified. Completed; an initial search named absent root pyproject.toml and exited 2, then the corrected search of existing directories exited 0.
- Compare storage semantics with primary documentation and independent critique. Check: SQLite atomic-commit, use-case, WAL, synchronous and backup documentation; Python sqlite3 reference; independent review. Expected: database, filesystem and external-side-effect boundaries remain distinct.
- Record recommended contract and preservation. Check: local document validation plus git status/diff. Expected: source-linked proposal, explicit runtime limitations and unchanged repository.

## Recommendation and alternatives

Recommendation: a SQLite database for each local factory instance's operational state, plus ordinary files for evidence and project knowledge. Keep the database and evidence archive under a documented local state root outside worker-writable checkouts. A project can have independent instances on different hosts. An active instance has one supervising execution owner. Multiple native workers can run concurrently inside that owner's admitted limits; short database writes serialize.

| Approach | Benefit | Obligation/cost | Judgment |
|---|---|---|---|
| SQLite plus artifact files | Related lifecycle/receipt/accounting changes commit together; uniqueness and conditional updates live in one store; no database server | Explicit schema/migrations, connection settings, artifact publication and backup still required | Recommended for the operational contract |
| Append-only file journal plus derived views | Easy raw inspection and streaming; possible standard-library implementation | Loam must implement durable append/commit boundaries, partial-tail recovery, locking, sequence/duplicate validation, compaction and cross-record invariants | Credible, but more storage-engine responsibility in Loam |
| External database/service | Suitable for centralized scheduling and coordinated writers across machines | Service provisioning, credentials and network availability become required infrastructure | Reconsider if multi-host active coordination is a requirement; no current evidence justifies it as the every-seed default |

Verified: SQLite provides atomic database transactions and is designed for device-local use with limited writer concurrency. It permits only one simultaneous writer. Its docs discourage direct shared-database access from multiple hosts over a network filesystem. This supports the recommendation, not a claim that every filesystem or operational protocol is safe. [Use cases](https://www.sqlite.org/whentouse.html), [atomic commit](https://www.sqlite.org/atomiccommit.html).

Recommendation: do not mandate WAL merely because example projects use it. Begin the prototype with SQLite rollback journal and synchronous=EXTRA, plus short transactions and bounded busy handling. Compare WAL with synchronous=FULL if observed reader/writer contention warrants it. WAL adds checkpoint and sidecar handling and requires same-host processes. Exact connection, filesystem sync and compatible-version settings must be tested before release. [WAL](https://www.sqlite.org/wal.html), [synchronous settings](https://www.sqlite.org/pragma.html#pragma_synchronous).

## What lives where

| Home | Data | Authority |
|---|---|---|
| Managed seed payload | Store implementation, migrations, native adapters, schemas, diagnostics, export/restore tooling and tests | Versioned Loam implementation; same source used during Loam development |
| Project-owned versioned records | Configuration, inquiry and decision artifacts, accepted lessons and extensions | Existing project authority; a database snapshot does not overwrite these records |
| Local operational database | Instance binding; admitted immutable work/profile revisions; runs/attempts; ownership generations; requested actions; observed native identities; normalized results; event history; usage and pending steering | Supervisor service layer only. CLI status reads it; authorized steering enters validated transactions. Workers cannot issue arbitrary state writes. |
| Local artifact archive | Raw events, output, source evidence, logs, immutable admitted input bundles and evaluation artifacts | Worker staging followed by protected capture/validation; database records content identities and lifecycle relevance |
| Derived views | Human-readable status/timeline exports and memory/search indexes | Rebuildable; never an alternative editable acceptance authority |

Recommendation: related state and append-only audit events commit in the same database transaction. JSONL export remains useful but is not a second live write authority. Worker messages are observations to validate. Required outcomes depend on exact work/profile/candidate/criteria revisions and complete result coverage.

Verified: current bin/factory writes status directly at line 401, appends run and daily usage records separately at lines 574-576, scans status files for concurrency at lines 596-609, and uses existing check filenames for resume at lines 1195-1200. Recommendation: replace these control responsibilities through a small store/transition interface instead of retaining them alongside a competing database authority.

## Identity, ownership and native execution

Recommendation: distinguish logical project, local instance, work revision, run, attempt, native session and workspace. A local instance registration binds its unique identity to a Git common directory and state root. Linked worktrees resolve to the same local instance; a separate clone creates a separate instance unless an explicit recovery/import binds it. A moved registration requires relocation/rebinding, not guessing from repository name or remote URL. Resolve canonical paths and test symlink aliases. Exact registration-file placement remains an implementation detail.

Recommendation: an OS-backed lifetime lock elects the active supervisor for an instance. Every ownership acquisition, including restore, creates a fresh random owner-incarnation identity independent of any restored counter. Database transactions validate instance identity, owner incarnation, attempt generation and expected state revision before every mutation. A generation counter alone can repeat after backup restore and is insufficient. Short-lived CLI operations use the same validated command layer. A lock or lease expiring does not prove that native descendants stopped. After supervisor loss, the new owner first enters reconciliation and blocks conflicting launches until old writers and consequential operations are resolved.

Recommendation: an ownership generation invalidates old result authority; it cannot revoke an old process's filesystem access. Keep old workspaces quarantined until writers are observed stopped. A PID alone is not sufficient identity because it can be reused. Record supported process/session identity and native job handles; when evidence is inadequate, retain unknown and do not launch a competitor. Native workers retain their internal tools and delegation.

Recommendation: commit an action intent before dispatch, then commit observed launch/results separately. Never hold a database transaction open while a native worker, check or network request runs. A crash after launch but before recording the handle is an unknown launch, not permission to repeat it. External actions need stable operation identity and provider readback/idempotency where supported. Neither SQLite nor a journal guarantees exactly-once external effects.

Recommendation: an intent is queued, not yet authorized for physical dispatch. A separate short transaction validates current owner, task revision and stop/steering state, then marks it dispatching. This is the durable dispatch-authorization point. Stop ordered before that transition invalidates queued work. Stop ordered afterward treats the action as possibly in flight, requests interruption/reconciliation, and does not promise that the external boundary was never crossed. A stop acknowledgment states that further dispatch authorizations are blocked and lists unresolved in-flight work; it is not a termination receipt. Apply the same rule to publication. The launcher checks cancellation again where possible, but no check can make a database commit atomic with process creation or a remote action.

## File/database publication protocol

Recommendation: treat the database transaction and artifact filesystem as separate persistence boundaries.

1. Capture output into an attempt staging area with declared ownership. Wait for relevant writers to stop, or use a source-supported immutable snapshot.
2. Copy into the protected artifact store, validate content identity and required metadata, make data durable, then atomically publish the complete artifact under its immutable identity on the same filesystem. Sync the relevant directory according to the tested host protocol. Workers must not be able to replace the stored object afterward.
3. In a short database transaction, register that published artifact and its valid receipt, update the applicable state, and append the audit event. Deduplicate by stable result identity; the same ID with different content is a conflict.
4. After restart, an artifact published without a database receipt is an unadmitted orphan. Reconcile it against the persisted attempt; presence alone cannot advance state. Missing or corrupted referenced artifacts block dependent validation and raise a visible evidence-loss event. Do not quietly recreate an empty database or report success.

Recommendation: do not garbage-collect unreferenced artifacts while a publication, recovery or backup may still need them. Backups bind a consistent database snapshot to its referenced immutable artifact manifest. Use the supported database backup mechanism or a documented quiescent procedure, not an arbitrary live-file copy. [SQLite backup](https://www.sqlite.org/backup.html).

## Example: a crash during checking

Illustrative behavior, not executed: the worker produces the export fix. Checking attempt C is durably admitted. Its result artifact is published, then the supervisor crashes before saving the receipt. On restart, Loam sees that C was checking, reconciles process termination and validates the recovered artifact against the frozen candidate and criteria. If complete and valid, it records C's result exactly once and proceeds to required review. If the output is partial, it records an evaluation error and retries only that safe stage under the admitted policy. It does not rerun implementation because the last round filename exists.

If a check receipt and phase update were already committed before the crash, recovery reads that committed state. An old producer cannot mutate current state. The new owner may explicitly adopt evidence from a prior attempt after reconciliation, retaining its original producer/attempt identity and recording a new recovery-validation event under current authority. Recovery adoption and a delayed producer message deduplicate to one validated outcome; stale producer authority is never revived. Functional success still cannot bypass pending steering, model-policy compliance or required review.

## Distribution, backup and upgrades

Verified: only seed renders, and current factory diagnostics already list Python among prerequisites. Some existing seed generation tasks also invoke Python, while project pyproject.toml is conditional on project kind. Python's sqlite3 interface requires SQLite support and is an optional CPython module. This machine reports Python 3.14.7 / SQLite 3.53.4 from a read-only import; no database was opened. These local versions are not recipient requirements. [Python reference](https://docs.python.org/3/library/sqlite3.html).

Recommendation: if Python is selected for the supervisor, use its sqlite3 interface without an ORM or separate database service. Every project kind must receive an explicit factory-runtime readiness check and documented setup path. Do not assume a generated TypeScript/other project has a compatible Python/SQLite runtime merely because the template once rendered. The runtime language and minimum versions remain a separate decision; the storage contract does not silently select them.

Recommendation: Copier distributes implementation and migration code, never a live database or previous project history. The local database is initialized through explicit factory setup. Separate factory schema version from project configuration and evidence schema versions. On update, an incompatible active run keeps its supported runtime/store combination or reports a blocker. The first migration path requires quiescence, a checked backup, explicit compatibility validation and refusal by old runtimes after an incompatible migration. Never silently run two incompatible engines against the same store. Restore reconciles old native jobs and external actions before allowing launch; a restored old database does not roll back the outside world.

Recommendation: a missing database in a previously registered instance is loss of state, not first-run setup. Fresh initialization is valid only for a new instance. Copy/import must not duplicate live authority. Initial supported topology is local disk on one execution host per active instance; multi-host control uses commands routed to that owner, not concurrent SQLite writes over a shared drive. Remote control transport remains later design work.

## Proposed runnable acceptance checks

These command names are proposed tests to implement later. None exists or was run for this design step.

| Change and dependency | Future command | Required outcome |
|---|---|---|
| Store transitions; admitted work and result schemas | python3 -m unittest discover -s bin/tests -p test_factory_store.py | Competing acceptance/steering commits serialize; stale revision rejected; duplicate result does not duplicate usage; conflicting duplicate fails; missing registered DB fails closed |
| Artifact publication; protected output boundary | python3 -m unittest discover -s bin/tests -p test_factory_artifacts.py | Crash at each file/DB boundary leaves no false pass; missing/different content invalidates dependencies; incomplete staging never promoted; backup retains referenced artifacts |
| Ownership/recovery; fake adapter and real subprocess identity fixtures | python3 -m unittest discover -s bin/tests -p test_factory_recovery.py | Lost launch acknowledgment produces reconciliation; surviving child blocks reuse; PID reuse cannot authorize kill/adoption; copied/restored instance cannot duplicate live authority; old counter values paired with old incarnations remain invalid; recovery adoption and delayed arrival settle once; stop between intent and dispatch invalidates queued work or reports in-flight uncertainty |
| Compatibility/update; schema and runtime manifest | python3 -m unittest discover -s bin/tests -p test_factory_state_upgrade.py | Quiescent migration and backup/restore preserve receipts and project decisions; old binary refuses incompatible schema; interrupted migration never initializes empty state |
| Every-seed delivery; render matrix and documented runtime setup | python3 -m unittest discover -s bin/tests -p test_factory_generated_state.py | Each project kind has complete machinery; fresh instances have no private runs; remove Loam checkout and original operator environment and exercise fixture lifecycle through shipped launcher |

The first later-authorized prototype should use this store boundary, a fake native adapter and subprocess crash fixtures. It measures mechanical correctness before paid native integration. Power-loss durability and OS permission enforcement require separate host-specific validation; process termination tests alone cannot establish them.

## Accepted choice and self-attack

Verified: the user accepted local SQLite operational state plus readable artifacts and the preceding recommendations, including one supervising owner per active instance. Coordinated execution across machines would require a subsequent explicit topology design. This does not restrict ordinary native brainstorming or prohibit many workers on the owning host.

Self-attack: database atomicity does not include artifacts or external effects; explicit publication/reconciliation covers the gap. A generation token cannot stop old writes; quarantine and process reconciliation remain required. A clone/restore can duplicate authority; registration and readmission must distinguish it. Corruption cannot become an empty successful run. An old runtime cannot write after incompatible migration. None of these proposed guarantees has been established by runtime tests yet.

## Independent critique and verification

Verified: a reader independent of this draft reviewed it against the loop/memory contracts and primary SQLite documentation. The review found generation reuse after restore, ambiguous recovery adoption of old evidence and a stop/queued-dispatch race. The draft now requires fresh owner incarnations, explicit new-owner evidence adoption and a serialized dispatch-authorization point with truthful stop acknowledgment. These are proposed repairs, not executed guarantees.

Document validation checks links and required contracts only. Runtime crash, migration, process and permission probes remain deferred. The repository was clean and both staged/unstaged diff commands exited 0 during this design step.
