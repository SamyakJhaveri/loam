# First-run design: evidence and validation

Scope: this resumed design session. Runtime implementation remains deferred. Earlier validation documents describe their own historical sessions.

## Baseline and preservation

Verified: `git rev-parse HEAD main origin/main` returned `d627bb2755ad49865f798bcb095800ddd2ad1ced` for every reference. `git ls-remote origin refs/heads/main` returned the same commit. Initial status was `## main...origin/main` with only `?? docs/architecture-working/`.

Verified: Python SHA-256 comparisons reported `pause-checkpoint.json MATCH` and `snapshot-manifest.json MATCH` before editing. Before-edit documentation copies and a session manifest were saved at `/private/tmp/loam-first-run-before/`. The original review directory and `prior-design/` snapshots are preserved. Intentional updates to living documents will differ from the old pause hashes; that checkpoint remains unchanged history.

## Reading and source evidence

Verified: opened the restart handoff and original `start-architecture-session.md`, then the original README, architecture review, comment responses, revision evidence, code evidence, source ledger and validation. Followed the current-record topic order through decisions/runtime, distribution/configuration, state/transitions/loop, native adapters/evidence, cookbook integration/registry/code mapping, memory/delivery/improvement and the complete slice/language rationale. Large historical inventories and audits were read selectively; truncated outputs are not a full-content audit of every catalog row or transitive source. Earlier source claims remain historical evidence unless explicitly refreshed below.

Verified: read repository instructions, asset-layer guidance, current factory architecture, research INDEX, `copier.yml`, `bin/check` and the current controller's check/resume paths. A case-insensitive repository-wide search excluded environment files, Git internals and dependency directories. It confirmed current root-only rendering/control boundaries; no new engine was present in the inspected source.

Verified: the independent ownership/storage reader inspected pinned Node SQLite source and upstream test source, SQLite URI documentation, Apple locking documentation, `fs-ext` source/manifest and Node socket/crypto documentation. The lead reopened the Node source, SQLite URI contract, Apple manual and binding manifest. The lead also read current npm clean-install, Node module/environment and Git path-query documentation. Source reads are not executed compatibility probes.

| Evidence | What it supports | Limit |
|---|---|---|
| [Node SQLite source](https://raw.githubusercontent.com/nodejs/node/v24.21.0/src/node_sqlite.cc), [upstream tests](https://raw.githubusercontent.com/nodejs/node/v24.21.0/test/parallel/test-sqlite.js), [SQLite URIs](https://www.sqlite.org/uri.html) | URI support and an existing-only open candidate | Our `mode=rw` and path-race fixtures did not run; this is not a final runtime pin |
| [Apple flock](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/flock.2.html), [binding source](https://raw.githubusercontent.com/baudehlo/node-fs-ext/master/fs-ext.cc), [manifest](https://raw.githubusercontent.com/baudehlo/node-fs-ext/master/package.json) | Lifetime-lock candidate and native build obligation | Moving binding source; no package installation or platform qualification |
| [Node local sockets](https://raw.githubusercontent.com/nodejs/node/v24.x/doc/api/net.md), [crypto](https://raw.githubusercontent.com/nodejs/node/v24.x/doc/api/crypto.md) | Reconnectable local transport and authentication primitives | No protocol security or same-user containment proof |
| [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/), [Node CLI](https://nodejs.org/api/cli.html), [modules](https://nodejs.org/api/modules.html) | Isolated staging and pre-Node environment boundary | No dependency closure/build equality validation for the future engine |
| [Git path queries](https://git-scm.com/docs/git-rev-parse) | Common-directory resolution with environment caveats | Local binding/relocation implementation remains proposed |

## Existing repository verification

Verified: the ordinary `python3` lacked pytest. The existing `.venv/check/bin/python3` imported pytest and xdist successfully. The repository check used that existing environment through `PATH="$PWD/.venv/check/bin:$PATH" bin/check` and exited 0. No dependency installation was required.

```text
============================== 31 passed in 8.95s ==============================
check: PASSED
```

The plugin validator reported its documented symlink warning and then validated the real skill paths. This suite checks current Loam source. It does not execute the proposed TypeScript factory or certify its design. No full suite repetition is needed for subsequent documentation-only edits.

## Independent investigation and review

Verified: the ownership/storage investigation distinguished host identity from current control authority, identified URI-based existing-only open as a candidate, and required retention of ownership during storage-thread failure. The draft therefore places the lifetime lock in the supervisor process, keeps the SQLite connection in its store thread, and forbids in-place writer replacement after failure. Host rebind begins observationally and separately establishes current control authority.

Verified: a fresh-context reviewer found missing independent bootstrap authority and an interrupted-restore window. The specification now requires independently admitted release/fork identity, a protected control entrypoint and a pending restore transaction outside the database before replacement. Startup honors its unresolved-history barrier. Migration uses the same maintenance-marker discipline. Required fixtures include coordinated launcher/program/manifest tampering and crashes across restoration boundaries. These are specification repairs, not reproduced runtime failures.

Verified: `python3 /private/tmp/loam-first-run-doc-check.py design` reported `First-run design checks: PASSED`, exit 0, before navigation/record updates. It checked current-document links, whitespace, snapshot preservation, required mechanism clauses and documentation-only Git scope. After record updates, the final mode reported `First-run final checks: PASSED`. `git diff --check` completed successfully and status still contained only the architecture directory.

Verified: the bounded independent rereview confirmed both repairs at the design level and found no new concrete contradiction in the reviewed paragraphs and fixtures. It did not certify release authentication, bootstrap distribution or crash behavior. Those remain implementation gates.

## Self-attack and completeness

- Input that could break the proposal: consistently changed launcher/program/manifest, or a crash after restoring older history. Both now have explicit admission/maintenance barriers and future failure cases. Incomplete spool output and unknown surviving workers remain blocked evidence, not inferred success.
- Paths not executed: actual native configuration, lead/session binding, sandbox denial, host control replacement, existing-only SQLite open, lock lifetime and power-loss recovery. They remain unverified; source reads and specification review do not substitute for probes.
- Change with no runtime test: all new work is design documentation. The existing repository suite was executed, while future engine commands remain labeled unimplemented and unrun.
- Claim audit: no current planning percentage, native safety guarantee or test result for the proposed engine is claimed. The historical pause percentage remains explicitly historical. Source inventories were inspected selectively, not claimed fully re-audited.

| User request | Evidence or resulting record |
|---|---|
| Read the handoff and follow linked reading order | Reading scope above; current mechanism specification links back to accepted records |
| Continue with selected Astra effort; keep TypeScript settled | No model/effort override or configuration edit; language retained in every current record |
| Preserve existing changes | Matching baseline manifests; original snapshots/pause checkpoint unchanged; before-edit copies and final scope check |
| Verify current main | Local and live remote Git identity; existing `bin/check` success above |
| Resume first-run, ownership, storage and recovery design | [Concrete specification](first-run-ownership-storage-recovery.md), independently investigated and reviewed |
| Keep living records updated | README, decision delta, runtime overview, complete slice and restart handoff now point to this specification |
| Defer runtime implementation | Documentation-only scope; no engine code, dependencies, provider probes or activation created |

The [resume checkpoint](resume-checkpoint.json) records current documentation hashes and the verified source baseline. It is preservation evidence, not a runtime validation certificate. It supplements the unchanged historical pause checkpoint.

## Limits and next work

Not done: runtime implementation, native compatibility probes, storage/locking/sandbox experiments, dependency installation, commits, pushes, automation or publication. Runtime work requires the user's explicit instruction. Exact dependency pins and file-level implementation tickets remain subsequent work. The new document is a concrete mechanism proposal, not a certified implementation or a new accepted user decision.
