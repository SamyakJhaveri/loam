# Factory package setup

## What this package provides

`.loam/factory` contains editable TypeScript source, the matching JavaScript in
`dist`, fixed package tests, and locked development tools. TypeScript is the source
we maintain. The compiler converts it into JavaScript that Node executes.

This revision qualifies the package. Protected installation, store setup and native
agent execution are not implemented. The runtime manifest marks its Node and npm
versions as candidates, not a supported runtime declaration.

## Inspect a received package

With Node available, run these from your generated project's root:

```bash
node .loam/factory/launcher.mjs qualify package
node .loam/factory/launcher.mjs status
```

The first command runs the supplied JavaScript tests and prints the exact case names
and successful count. It needs no compiler, `node_modules`, npm or network access.
The status command returns nonzero and explains that installation is unavailable.
The full `verify installation`, `verify store`, `verify execution` and
`verify complete-slice` groups also return nonzero. Their missing populations remain
visible; a package pass cannot stand in for future installation or execution checks.

## Platform qualification

Two further recipient commands qualify the mechanical foundation on a host:

```bash
node .loam/factory/launcher.mjs qualify platform
node .loam/factory/launcher.mjs qualify native-boundary
```

`qualify platform` proves runtime identity against the manifest, existing-only SQLite
storage open (no create fallback, no arbitrary URI), the SQLite exclusive lifetime lock
(a competing owner is refused, a stopped owner keeps the lock, a killed owner releases
it, a child does not inherit it, a replaced path is detected, the lock is never
unlinked), and that preload and Git-redirection environment inputs are stripped before
a trusted child starts. OpenSSL configuration and provider/engine directory overrides
are stripped too. Worker queries reject after an open failure or closure. Closing
rejects outstanding requests and waits for the worker to terminate. A database write
may already have completed; rejection does not prove that its effects were rolled
back. The gate runs inside a sandbox and on CI, so it is part of `bin/check`.

Store paths must be absolute local paths with a single leading slash. Leading double
slashes are refused because SQLite can interpret them as a URI authority. Runtime
qualification describes the running executable; an override naming a different file
is unavailable, even when its hash can be read.

`qualify native-boundary` proves candidate containment: a contained process may work in
its workspace but is denied the protected registry, state, locks, credentials, sockets
and callback paths through descendants, symlinks and path aliases, while the same script
run without containment reads them. It needs a real sandbox mechanism (`sandbox-exec` on
macOS, `bwrap` on Linux) that cannot nest inside another sandbox, so it is **not** part
of `bin/check`. Run it from a plain terminal on macOS and directly on Linux; a nested or
sandboxed session fails at `boundary.mechanism-available` with the mechanism's own reason.

Containment requires existing, disjoint workspace and runtime roots. Protected paths
must exist and must not overlap either root or the exposed system roots. The boundary
resolves symlinks before checking these relationships and refuses conflicting layouts.
The runtime-write fixture uses a scratch runtime and proves that its write succeeds
without containment before checking the denial.

Before each command is constructed, admission inspects filesystem metadata beneath
the workspace, runtime and every protected root without following nested symlinks.
Every non-directory entry must have exactly one hard link. A hard link is another
name for the same file; pathname separation alone cannot protect such a file.
Protected roots may be individual files. Files with extra links are refused even
when the other name is outside these roots. This includes workspaces with hard-linked
package caches or local Git clones. Admission never unlinks or repairs these files.
An unreadable or disappearing entry also refuses admission. An editor changing files
during the scan can therefore cause a transient refusal.

This is prelaunch admission of the observed filesystem state, not atomic validation
plus execution. A trusted caller must prevent uncontained concurrent writers from
changing the admitted layout. The caller must not pass additional inherited file
descriptors to the contained process. The filesystem must report truthful link counts;
this check does not qualify filesystems that hide link multiplicity. Copies made
before admission, or aliases left after their original name is removed, cannot be
identified from the current link count. Protected runtime and workspace admission
and ownership remain separate prerequisites for managed execution.

The native fixture also attempts to create protected and runtime aliases after
containment starts. It checks the same operation succeeds without containment,
requires workspace linking to work on Linux, and records whether macOS permits
workspace links or refuses all link creation. Process startup and workspace access
have separate positive controls. The descendant case requires a successful workspace
read through the same shell used for its protected-file denial.

The macOS profile protects the registered paths but permits reads elsewhere. It is
not a general home-directory privacy boundary. The Linux profile exposes a limited
mount namespace. These host differences and the admission limits must accompany
qualification evidence; neither host result declares managed execution supported.

Both commands are qualification only. No runtime is supported yet: the runtime manifest
keeps `supportedRuntime: false` and records the Node and bundled SQLite versions and
per-platform executable digests as candidates, not a support declaration.

## Admit a runtime from a trusted source

The trust root is your own review of two independently acquired inputs:
a clean checkout of the Loam template at an annotated release tag fetched over HTTPS from `github.com/SamyakJhaveri/loam`,
and the official Node 24.21.0 toolchain distribution whose `bin/node` bytes the controller verifies against the runtime manifest before it runs.
Integrity checking is not authorship authentication. The authority is your review, not the digests.

The controller and the admit path call a fixed set of operating-system programs by absolute path and trust them as reviewed platform components.
Those components are `/bin/sh`, `/usr/bin/env`, `/usr/bin/uname`, the digest tool (`/usr/bin/shasum` on macOS, `/usr/bin/sha256sum` on Linux), `/bin/mkdir`, `/bin/mv`, `/bin/chmod`, `/bin/rm`, `/usr/bin/grep`, `/usr/bin/sed`, `/usr/bin/cut` and `/usr/bin/tr`.

The protected operator setup and control entrypoint is `scripts/loam-control.sh`, a dependency-free POSIX `sh` script inside the trusted payload.
Its distribution owner is the existing Loam release channel: annotated tags cut by `bin/release.sh` and pushed to GitHub.
Admit a runtime from the trusted checkout:

```bash
/bin/sh <checkout>/seed/.loam/factory/scripts/loam-control.sh \
  --toolchain <node-24.21.0-distribution> --control-root <root> \
  admit --trusted-source <checkout>/seed/.loam/factory --release-identity <label>
```

Each optional `--protect-state`, `--protect-locks`, `--protect-credentials`, `--protect-sockets` or `--protect-callbacks` flag redirects one protected home to an existing directory outside the control root.
`--protect-registry` is refused, because the registry home is where the records are written.
Run read-only diagnostics against an admitted control root:

```bash
node .loam/factory/launcher.mjs status --control-root <root>
node .loam/factory/launcher.mjs doctor --control-root <root> --checkout <checkout>/seed/.loam/factory
```

The launcher is a convenience resolver, not the trust root.
It forwards the fixed verb to `<root>/loam-control`, the controller copy made at admission, which runs the snapshot's own Node under a clean environment with `--no-global-search-paths`.
No dependency resolves from a project root or a personal cache, and `status` and `doctor` never write.
`status` and `doctor` also read `LOAM_CONTROL_ROOT` when `--control-root` is absent, and print `{"status":"unavailable","diagnostic":"control-root-missing"}` and exit nonzero when neither is set.

### Control root layout

The control root holds the protected registry, the six protected homes, the sealed runtime snapshots, and a copy of the controller named `loam-control`.

- `registry/` holds the admission records (`registry/admissions/<id>.json`), the runtime records (`registry/runtimes/<id>.json` and `registry/runtimes/<id>.sha256`), the current selection (`registry/selected.json`) and the exclusive-create lock (`registry/admit.lock`).
- `runtimes/<id>/` is one sealed, read-only snapshot: `payload/`, `bin/node`, `lib/node_modules/npm/`, `bin/loam-control`, `snapshot.json` and `installed-files.json`.
- The six protected homes `registry/`, `state/`, `locks/`, `credentials/`, `sockets/` and `callbacks/` are created empty at the first admission.

A contained build script may write inside its own staging workspace but is denied every read of the six homes.
The homes are the paths later tickets populate.

### States and recovery

The controller and `doctor` evaluate this table first, in order.
The first match is the reported diagnostic, and each row states the single path to remove by hand.

| Observed state | Diagnostic (detail) | Recover by hand |
|---|---|---|
| control root missing or the flag absent | `control-root-missing` | create the directory or pass `--control-root` |
| `registry/admit.lock` present | `install-interrupted` (`lock`) | remove the lock if no admission is running |
| a `runtimes/.staging-*` or `.tool-*` directory | `install-interrupted` (`staging`) | remove that directory |
| a `runtimes/<id>` missing any of its three registry records | `install-interrupted` (`unregistered`) | remove `runtimes/<id>` and any partial records |
| `registry/selected.json` malformed or naming a runtime that is not complete | `install-interrupted` (`selection`) | remove `selected.json` |
| a complete registered runtime with no `selected.json` | `install-interrupted` (`unselected`) | remove the runtime and its records |
| no `selected.json` and no runtimes | `nothing-admitted` | run `admit` |
| `selected.json` well-formed and the runtime complete | dispatch (a pre-dispatch digest check may still report `installed-file-altered`) | none |

This revision admits exactly one runtime per control root and never changes a selection.
So a complete but unselected snapshot is treated as an interrupted transaction, not a runnable runtime.
A later ticket that introduces second admissions redefines that state.

### Residuals and limits

- Between runs, any process running as your user can rewrite the snapshot, both inventories, the registry records and the controller copy together, with no on-disk trace. The trust boundary is your review at admission plus CORE-02 containment during a contained build, not the at-rest bytes.
- The controller cannot protect its own first startup. Native loader variables such as `DYLD_INSERT_LIBRARIES` and `LD_PRELOAD`, and the shell's own startup files, act before the controller re-execs under a clean environment. Run the controller non-interactively from a plain terminal. An already-compromised parent is out of scope.
- On macOS the containment profile protects only the registered paths and permits reads elsewhere. It is not a general home-directory privacy boundary.

Provider payloads are not shipped in this revision.
By operator decision the "both provider payloads ship" acceptance clause is deferred to issue #140 (https://github.com/SamyakJhaveri/loam/issues/140).
The admission record carries `providers.payloads` empty with `providers.successor` naming that issue, and `doctor` reports `providerReadiness: not-evaluated` as a field kept separate from installation availability.
This acceptance clause is unmet here.

## Work on the factory source

Use a separate official Node 24.21.0 distribution with bundled npm 11.19.0.
Set its absolute location before installing or building:

```bash
export LOAM_FACTORY_TOOLCHAIN="/absolute/path/to/node-v24.21.0-distribution"
export PATH="$LOAM_FACTORY_TOOLCHAIN/bin:$PATH"
node .loam/factory/scripts/toolchain.mjs install "$PWD/.loam/factory"
npm --prefix .loam/factory run build
npm --prefix .loam/factory run verify:build
```

The install helper uses the committed lock, empty npm configuration files, a fresh
cache and disabled installation scripts. It checks the complete local compiler/type
population. Missing tools fail explicitly. Research dependencies remain separate.

`build` refreshes generated JavaScript and sourcemaps, then records the source,
output and dependency hashes in `release-manifest.json`. Commit those together.
The manifest describes consistency. It does not authenticate who produced the package.

`verify:build` copies frozen inputs into another directory, installs the locked tools,
rebuilds there, and compares all output files and the manifest byte for byte. It never
repairs the candidate first. Registry access is required for that fresh installation.
Its developer fixture includes stale source, missing/extra output, changed sourcemaps,
missing compiler/types, ancestor-package collisions and provider-call sentinels.

## What travels with the project

Source, compiled tests, build scripts, manifests and the dependency lock travel together.
Development `node_modules`, `.cache`, `.state` and `runtime-installation` directories do
not travel through Copier. Loam's release check verifies exact delivery separately;
recipient checks inspect the received package. Neither check claims the later full
render/update matrix or protected runtime admission has been implemented.
