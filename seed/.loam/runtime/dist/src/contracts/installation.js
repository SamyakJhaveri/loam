// Frozen installation contract for CORE-04 runtime admission.
//
// This module holds only constants, record types and small pure predicates. It
// has no imports, so it satisfies the payload import-closure rule, and it is the
// single source of truth shared by the admit path (src/installation/admit.ts),
// the installed doctor (src/commands/doctor.ts), the POSIX controller
// (scripts/loam-control.sh, which mirrors these literals by hand), and the
// offline fixtures. Freeze these shapes before any caller is built.
//
// Precedence: plan-03 and the Codex implementation conditions C1-C5 over the
// inherited plan-02 text.
export const INSTALLATION_RECORD_VERSION = 1;
// Paths under the operator's control root, relative to it. `homes` are the six
// CORE-02 protected kinds created empty at first admission; `--protect-registry`
// is refused, the other five may be redirected through AdmitOptions.protect.
// Written and read by admit.ts and doctor.ts.
export const CONTROL_ROOT_LAYOUT = {
    controller: 'loam-control',
    registry: 'registry',
    admissions: 'registry/admissions',
    runtimeRecords: 'registry/runtimes',
    selected: 'registry/selected.json',
    lock: 'registry/admit.lock',
    runtimes: 'runtimes',
    stagingPrefix: '.staging-',
    toolPrefix: '.tool-',
    homes: {
        registry: 'registry',
        state: 'state',
        locks: 'locks',
        credentials: 'credentials',
        sockets: 'sockets',
        callbacks: 'callbacks',
    },
};
// Paths inside a sealed snapshot, relative to `runtimes/<id>/`.
export const SNAPSHOT_LAYOUT = {
    payload: 'payload',
    node: 'bin/node',
    npm: 'lib/node_modules/npm',
    npmCli: 'lib/node_modules/npm/bin/npm-cli.js',
    controller: 'bin/loam-control',
    modules: 'payload/node_modules',
    installedFiles: 'installed-files.json',
    snapshot: 'snapshot.json',
    doctor: 'payload/dist/src/commands/doctor.js',
};
// Transient directories created inside the staging workspace and removed before
// sealing. `npm` holds npm/user, npm/global and npm/cache. The runtime directory
// `.tool-<id>` is a sibling of the workspace and removed separately (item 8).
export const STAGING_TRANSIENT = ['home', 'tmp', 'npm'];
// The only subtree a dependency lifecycle script may add to, remove from or
// change. The release binding (C4) refuses any other payload difference.
export const GENERATED_TREE = 'payload/node_modules';
// Under test.originPolicy 'file', an admitted dependency's resolved value must
// equal this prefix plus `<name>-<version>.tgz`. Reachable from fixtures only.
export const FIXTURE_ORIGIN_PREFIX = 'file:assets/admission-fixtures/';
// Trusted operating-system helpers the controller and admit path invoke by
// absolute path. The digest tool is chosen from `uname -s`.
export const OS_HELPERS = {
    sh: '/bin/sh',
    env: '/usr/bin/env',
    uname: '/usr/bin/uname',
    digest: { darwin: '/usr/bin/shasum', linux: '/usr/bin/sha256sum' },
};
// The only dependency registry the production lock-origin gate accepts.
export const REGISTRY_ORIGIN = 'https://registry.npmjs.org/';
// Proxy variables preserved, as quoted data, only through the scripts-disabled
// fetch phase (C1). They are omitted from status, doctor and every build or
// smoke child, and their values are kept out of diagnostics and logs.
export const FETCH_PASSTHROUGH_ENVIRONMENT = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'];
// The shell npm runs lifecycle scripts under, inside CORE-02 containment.
export const SCRIPT_SHELL = '/bin/sh';
// The Node flag the controller adds to every fixed dispatch vector (C1). Doctor
// asserts process.execArgv contains it as part of the no-project-root proof.
export const NO_GLOBAL_SEARCH_PATHS = '--no-global-search-paths';
// Per-package native build prerequisites. Empty in production, so the production
// path has no build phase; fixtures inject entries through
// AdmitOptions.test.nativePrerequisites. `tools` maps a shim name to an absolute
// executable path; `loadSmoke` is a module path relative to the payload.
export const NATIVE_PREREQUISITES = {};
// Every diagnostic admission, the controller or doctor can report. The order is
// the frozen plan-03 order; plan-02's `snapshot-collision` is gone and
// `build-script-failed`, `load-smoke-failed` and `build-altered-release` are
// added.
export const DIAGNOSTICS = [
    'trusted-source-shape',
    'control-root-missing',
    'nothing-admitted',
    'ancestor-package-collision',
    'selection-exists',
    'runtime-digest-mismatch',
    'wrong-release-digest',
    'lock-origin-refused',
    'build-script-refused',
    'native-prerequisite-missing',
    'containment-unavailable',
    'build-script-failed',
    'load-smoke-failed',
    'build-altered-release',
    'dependency-missing',
    'install-interrupted',
    'installed-file-altered',
    'environment-injected',
    'unadmitted-fork',
    'not-admitted-runtime',
];
// Thrown by admit.ts to carry the diagnostic that classifies a refusal. The
// controller and fixtures read `diagnostic`, not the message text.
export class AdmissionError extends Error {
    diagnostic;
    constructor(diagnostic, message) {
        super(message);
        this.name = 'AdmissionError';
        this.diagnostic = diagnostic;
    }
}
// Canonical JSON serializer for every persisted record (selected.json, the
// registry records, snapshot.json, installed-files.json). It recursively sorts
// object keys and indents by two spaces, so a record's bytes and its sha256 are
// reproducible regardless of insertion order and the controller's fixed
// `"snapshotId": "<id>"` grep matches. admit.ts writes with it; doctor.ts hashes
// the bytes it reads back.
export function canonicalJson(value) {
    return JSON.stringify(sortKeys(value), null, 2);
}
function sortKeys(value) {
    if (Array.isArray(value))
        return value.map(sortKeys);
    if (value !== null && typeof value === 'object') {
        const source = value;
        const out = {};
        for (const key of Object.keys(source).sort())
            out[key] = sortKeys(source[key]);
        return out;
    }
    return value;
}
//# sourceMappingURL=installation.js.map