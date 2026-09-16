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
