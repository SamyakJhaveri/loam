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

export const INSTALLATION_RECORD_VERSION = 1 as const;

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
} as const;

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
} as const;

// Transient directories created inside the staging workspace and removed before
// sealing. `npm` holds npm/user, npm/global and npm/cache. The runtime directory
// `.tool-<id>` is a sibling of the workspace and removed separately (item 8).
export const STAGING_TRANSIENT = ['home', 'tmp', 'npm'] as const;

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
} as const;

// The only dependency registry the production lock-origin gate accepts.
export const REGISTRY_ORIGIN = 'https://registry.npmjs.org/';

// Proxy variables preserved, as quoted data, only through the scripts-disabled
// fetch phase (C1). They are omitted from status, doctor and every build or
// smoke child, and their values are kept out of diagnostics and logs.
export const FETCH_PASSTHROUGH_ENVIRONMENT = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'] as const;

// The shell npm runs lifecycle scripts under, inside CORE-02 containment.
export const SCRIPT_SHELL = '/bin/sh';

// The Node flag the controller adds to every fixed dispatch vector (C1). Doctor
// asserts process.execArgv contains it as part of the no-project-root proof.
export const NO_GLOBAL_SEARCH_PATHS = '--no-global-search-paths';

// Per-package native build prerequisites. Empty in production, so the production
// path has no build phase; fixtures inject entries through
// AdmitOptions.test.nativePrerequisites. `tools` maps a shim name to an absolute
// executable path; `loadSmoke` is a module path relative to the payload.
export const NATIVE_PREREQUISITES: Record<string, { tools: Record<string, string>; loadSmoke: string }> = {};

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
] as const;
export type Diagnostic = typeof DIAGNOSTICS[number];

// Thrown by admit.ts to carry the diagnostic that classifies a refusal. The
// controller and fixtures read `diagnostic`, not the message text.
export class AdmissionError extends Error {
  readonly diagnostic: Diagnostic;
  constructor(diagnostic: Diagnostic, message: string) {
    super(message);
    this.name = 'AdmissionError';
    this.diagnostic = diagnostic;
  }
}

// The reviewed release identity, recorded from the trusted source only (item 4),
// never from a candidate. `files` (the release-manifest.json file map plus
// release-manifest.json itself, never node_modules) together with
// `manifestSha256` is the release binding re-checked after every build and by
// doctor. Embedded in AdmissionRecord.
export interface ReleaseIdentity {
  label: string;
  sourcePath: string;
  gitDescribe: string | null;
  sourceDigest: string;
  outputDigest: string;
  dependencyDigest: string;
  manifestSha256: string;
}

// Node and npm bytes admission authenticated before use and copied into the
// snapshot. Embedded in AdmissionRecord.
export interface AdmittedTools {
  platform: string;
  arch: string;
  node: { version: string; sqlite: string; sha256: string; sourcePath: string };
  npm: { version: string; cliSha256: string; packageSha256: string; sourcePath: string };
}

// Owner: admit.ts. Written to `registry/admissions/<id>.json` at publication
// step 7a. `files` is the per-file release map and never includes node_modules;
// `providers` stays empty in CORE-04 with `successor` naming issue #140.
export interface AdmissionRecord {
  version: 1;
  id: string;
  admittedAt: string;
  release: ReleaseIdentity;
  files: Record<string, string>;
  tools: AdmittedTools;
  allowedBuildScripts: Record<string, boolean>;
  protectedPaths: Record<'registry' | 'state' | 'locks' | 'credentials' | 'sockets' | 'callbacks', string>;
  providers: { payloads: string[]; successor: string };
}

// Owner: admit.ts. Written to `<snapshot>/snapshot.json` during seal, before
// installed-files.json (item 8).
export interface SnapshotRecord {
  version: 1;
  id: string;
  admissionId: string;
  createdAt: string;
  layout: typeof SNAPSHOT_LAYOUT;
}

// Owner: admit.ts. Written to `<snapshot>/installed-files.json` during seal; it
// excludes itself. Read by doctor for the exact-inventory check. `mode` records
// whether the installed file is executable.
export interface InstalledFiles {
  version: 1;
  files: Record<string, { sha256: string; mode: 'executable' | 'regular' }>;
}

// Owner: admit.ts. Written to `registry/runtimes/<id>.json` at step 7c; binds
// the snapshot to the sha256 of installed-files.json.
export interface RuntimeRecord {
  version: 1;
  snapshotId: string;
  admissionId: string;
  installedFilesSha256: string;
}

// Owner: admit.ts. Written to `registry/selected.json` at step 9; read by the
// controller's fixed grep and by doctor. One selection per control root, never
// changed within CORE-04.
export interface Selected {
  version: 1;
  snapshotId: string;
  admissionId: string;
}

// Options for admit.ts's exported entry. `test` is reachable only from fixture
// code (C5); the controller and CLI expose no flag for it. `protect` cannot
// redirect the registry home. `test.faultAfter` stops the process (exit 70)
// immediately after the named publication point so a fixture observes every
// intermediate state (item 9).
export interface AdmitOptions {
  trustedSource: string;
  controlRoot: string;
  toolchain: string;
  releaseIdentity: string;
  protect?: Partial<Record<'state' | 'locks' | 'credentials' | 'sockets' | 'callbacks', string>>;
  test?: {
    originPolicy: 'file';
    nativePrerequisites?: typeof NATIVE_PREREQUISITES;
    containment?: 'unavailable';
    simulateWrapperRefusal?: boolean;   // real contained child exits nonzero with no start marker
    pauseBeforeSelect?: string;         // rendezvous path: pause after the lock/records, before selected.json
    faultAfter?: 'seal' | 'chmod' | 'rename' | 'admission-record' | 'sha256' | 'runtime-record' | 'controller' | 'selected';
  };
}

// Produced by doctor.ts and printed as one JSON line; never persisted.
// `resolution` proves the no-project-root guarantee directly (item 10):
// `nodePath` null and `globalSearchPaths` false, with `execArgv` containing
// NO_GLOBAL_SEARCH_PATHS. `snapshot` and `checkout` appear only when known.
export interface DoctorReport {
  status: 'healthy' | 'unhealthy';
  diagnostics: { code: Diagnostic; detail: string }[];
  installation: 'admitted' | 'unavailable';
  providerReadiness: 'not-evaluated';
  resolution: { nodePath: string | null; globalSearchPaths: boolean; execArgv: string[] };
  snapshot?: { id: string; admissionId: string; release: ReleaseIdentity; tools: AdmittedTools };
  checkout?: 'matches-admitted-release' | 'unadmitted-fork';
}

// Environment names doctor refuses to see, giving `environment-injected` (item
// 10, C1). The exact names below, plus these prefix families: DYLD_, LD_ and
// NPM_CONFIG_; npm_config is matched case-insensitively so it also catches
// NPM_CONFIG_ and mixed case; and any GIT_ name except GIT_TERMINAL_PROMPT.
export const STRIPPED_VARIABLE_NAMES = [
  'NODE_OPTIONS',
  'NODE_PATH',
  'NODE_REPL_EXTERNAL_MODULE',
  'NODE_EXTRA_CA_CERTS',
  'NODE_TLS_REJECT_UNAUTHORIZED',
  'OPENSSL_CONF',
] as const;
export const STRIPPED_VARIABLE_PREFIXES = ['DYLD_', 'LD_', 'NPM_CONFIG_'] as const;
export function isStrippedVariable(name: string): boolean {
  if ((STRIPPED_VARIABLE_NAMES as readonly string[]).includes(name)) return true;
  if (name.toLowerCase().startsWith('npm_config_')) return true;
  if (STRIPPED_VARIABLE_PREFIXES.some(prefix => name.startsWith(prefix))) return true;
  return name.startsWith('GIT_') && name !== 'GIT_TERMINAL_PROMPT';
}

// Canonical JSON serializer for every persisted record (selected.json, the
// registry records, snapshot.json, installed-files.json). It recursively sorts
// object keys and indents by two spaces, so a record's bytes and its sha256 are
// reproducible regardless of insertion order and the controller's fixed
// `"snapshotId": "<id>"` grep matches. admit.ts writes with it; doctor.ts hashes
// the bytes it reads back.
export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortKeys(value), null, 2);
}
function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === 'object') {
    const source = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(source).sort()) out[key] = sortKeys(source[key]);
    return out;
  }
  return value;
}
