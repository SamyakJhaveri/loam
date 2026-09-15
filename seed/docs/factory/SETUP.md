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
