// Installed runtime doctor (CORE-04). Read-only diagnostics for an admitted
// runtime. It is meant to run as the snapshot's own Node, launched only by the
// trusted controller. It classifies the selected runtime's health against the
// protected registry and never writes.
//
// Diagnostic precedence (C4): the control-root state table first (via
// controlRootState), then not-admitted-runtime, then environment-injected, then
// installed-file-altered, then build-altered-release, then unadmitted-fork. The
// first failing check is the reported diagnostic. A checkout that does not match
// the admitted release is a separate attestation on the `checkout` field and does
// not by itself mark the installation unhealthy.

import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync, realpathSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CONTROL_ROOT_LAYOUT, NO_GLOBAL_SEARCH_PATHS, SNAPSHOT_LAYOUT, isStrippedVariable } from '../contracts/installation.js';
import type { AdmissionRecord, Diagnostic, DoctorReport, InstalledFiles, RuntimeRecord } from '../contracts/installation.js';
import { controlRootState } from '../installation/admit.js';

export interface DoctorOptions {
  mode: 'status' | 'doctor';
  controlRoot: string | undefined;
  checkout?: string;
}

// A snapshot entry that is not a plain file or directory, or is a symlink. The
// sealed snapshot forbids these, so encountering one is tampering.
class TamperError extends Error {}

function hashFile(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

const HEX64 = /^[0-9a-f]{64}$/;
const HEX16 = /^[0-9a-f]{16}$/;
function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}
function isRelativePath(path: string): boolean {
  if (path.length === 0 || path.startsWith('/')) return false;
  return !path.split('/').includes('..');
}

// Structural validators for the registry records and the installed inventory
// (B2). These run before any field is used so a malformed or vacuous record is a
// structured diagnostic, never a raw TypeError and never a false healthy. They do
// not authenticate the record; the integrity proof stays the byte re-hashing
// below (installed-files.json, the release map) and the controller's pre-dispatch
// digest set. An empty release file map must not certify: without it the release
// binding loop is vacuous.
function isReleaseFileMap(value: unknown): value is Record<string, string> {
  if (!isObject(value)) return false;
  const entries = Object.entries(value);
  if (entries.length === 0) return false;
  return entries.every(([path, digest]) => isRelativePath(path) && typeof digest === 'string' && HEX64.test(digest));
}
function isReleaseIdentity(value: unknown): boolean {
  if (!isObject(value)) return false;
  return typeof value.label === 'string'
    && typeof value.sourcePath === 'string'
    && (value.gitDescribe === null || typeof value.gitDescribe === 'string')
    && typeof value.sourceDigest === 'string' && HEX64.test(value.sourceDigest)
    && typeof value.outputDigest === 'string' && HEX64.test(value.outputDigest)
    && typeof value.dependencyDigest === 'string' && HEX64.test(value.dependencyDigest)
    && typeof value.manifestSha256 === 'string' && HEX64.test(value.manifestSha256);
}
function isAdmittedTools(value: unknown): boolean {
  if (!isObject(value)) return false;
  const { node, npm } = value;
  return isObject(node) && typeof node.sha256 === 'string' && HEX64.test(node.sha256)
    && isObject(npm) && typeof npm.cliSha256 === 'string' && HEX64.test(npm.cliSha256)
    && typeof npm.packageSha256 === 'string' && HEX64.test(npm.packageSha256);
}
function isValidAdmissionRecord(value: unknown, admissionId: string): boolean {
  return isObject(value)
    && value.version === 1
    && typeof value.id === 'string' && HEX16.test(value.id) && value.id === admissionId
    && isReleaseFileMap(value.files)
    && isReleaseIdentity(value.release)
    && isAdmittedTools(value.tools);
}
function isValidInventory(value: unknown): value is InstalledFiles {
  if (!isObject(value) || value.version !== 1 || !isObject(value.files)) return false;
  return Object.values(value.files).every(entry =>
    isObject(entry) && typeof entry.sha256 === 'string' && HEX64.test(entry.sha256)
    && (entry.mode === 'executable' || entry.mode === 'regular'));
}

function fileMode(path: string): 'executable' | 'regular' {
  return (statSync(path).mode & 0o111) !== 0 ? 'executable' : 'regular';
}

// Every regular file under `root`, as sorted posix paths relative to it. A
// symlink or any non-regular entry throws TamperError.
function collectFiles(root: string): string[] {
  const files: string[] = [];
  const walk = (dir: string): void => {
    for (const name of readdirSync(dir).sort()) {
      const abs = join(dir, name);
      const rel = relative(root, abs).split(sep).join('/');
      const stat = lstatSync(abs);
      if (stat.isSymbolicLink()) throw new TamperError(rel);
      if (stat.isDirectory()) walk(abs);
      else if (stat.isFile()) files.push(rel);
      else throw new TamperError(rel);
    }
  };
  walk(root);
  return files;
}

// True when the checkout's launcher.mjs, scripts/loam-control.sh,
// release-manifest.json and every dist file match the admitted release map, and
// the checkout adds no dist file the release map does not record.
function checkoutMatches(checkout: string, files: Record<string, string>): boolean {
  const fixed = ['launcher.mjs', 'scripts/loam-control.sh', 'release-manifest.json'];
  const recordedDist = Object.keys(files).filter(path => path.startsWith('dist/'));
  for (const path of [...fixed, ...recordedDist]) {
    const expected = files[path];
    if (expected === undefined) return false;
    try {
      if (hashFile(join(checkout, path)) !== expected) return false;
    } catch {
      return false;
    }
  }
  let present: string[];
  try {
    present = collectFiles(join(checkout, 'dist')).map(path => `dist/${path}`);
  } catch {
    return false;
  }
  const recorded = new Set(recordedDist);
  return present.every(path => recorded.has(path));
}

export function runDoctor(options: DoctorOptions): DoctorReport {
  const resolution = {
    nodePath: process.env.NODE_PATH ?? null,
    globalSearchPaths: !process.execArgv.includes(NO_GLOBAL_SEARCH_PATHS),
    execArgv: [...process.execArgv],
  };
  const report = (
    status: 'healthy' | 'unhealthy',
    installation: 'admitted' | 'unavailable',
    diagnostics: { code: Diagnostic; detail: string }[],
  ): DoctorReport => ({ status, diagnostics, installation, providerReadiness: 'not-evaluated', resolution });

  const state = controlRootState(options.controlRoot);
  if (state.kind === 'diagnostic') {
    return report('unhealthy', 'unavailable', [{ code: state.diagnostic, detail: state.detail }]);
  }

  const root = options.controlRoot as string;
  const { selected, snapshotPath } = state;

  // Registry records live outside the sealed snapshot, so the controller's
  // pre-dispatch digest set does not cover them. Parse defensively: a malformed
  // or internally inconsistent record is a corrupt/interrupted registry,
  // reported as a structured install-interrupted, never a raw SyntaxError. (R2)
  const interrupt = (detail: string): DoctorReport =>
    report('unhealthy', 'unavailable', [{ code: 'install-interrupted', detail }]);

  let parsedAdmission: unknown;
  try {
    parsedAdmission = readJson<unknown>(join(root, CONTROL_ROOT_LAYOUT.admissions, `${selected.admissionId}.json`));
  } catch {
    return interrupt(`admission record is not valid JSON: ${selected.admissionId}`);
  }
  if (!isValidAdmissionRecord(parsedAdmission, selected.admissionId)) {
    return interrupt(`admission record malformed or not matching the selection: ${selected.admissionId}`);
  }
  const record = parsedAdmission as unknown as AdmissionRecord;

  let parsedRuntime: unknown;
  try {
    parsedRuntime = readJson<unknown>(join(root, CONTROL_ROOT_LAYOUT.runtimeRecords, `${selected.snapshotId}.json`));
  } catch {
    return interrupt(`runtime record is not valid JSON: ${selected.snapshotId}`);
  }
  if (!isObject(parsedRuntime) || parsedRuntime.version !== 1
      || parsedRuntime.snapshotId !== selected.snapshotId
      || parsedRuntime.admissionId !== selected.admissionId
      || typeof parsedRuntime.installedFilesSha256 !== 'string'
      || !HEX64.test(parsedRuntime.installedFilesSha256)) {
    return interrupt(`runtime record malformed or not matching the selection: ${selected.snapshotId}`);
  }
  const runtimeRecord = parsedRuntime as unknown as RuntimeRecord;

  const snapshot = { id: selected.snapshotId, admissionId: selected.admissionId, release: record.release, tools: record.tools };
  const fail = (code: Diagnostic, detail: string): DoctorReport => ({ ...report('unhealthy', 'admitted', [{ code, detail }]), snapshot });

  // not-admitted-runtime: this process must be the snapshot's own Node.
  const expectedNode = join(snapshotPath, SNAPSHOT_LAYOUT.node);
  let sameNode = false;
  try {
    sameNode = realpathSync(process.execPath) === realpathSync(expectedNode);
  } catch {
    sameNode = false;
  }
  if (!sameNode) return fail('not-admitted-runtime', `running Node is not ${expectedNode}`);

  // environment-injected: no stripped-class variable may be present.
  const injected = Object.keys(process.env).filter(isStrippedVariable).sort();
  if (injected.length > 0) return fail('environment-injected', `stripped variables present: ${injected.join(', ')}`);

  // installed-file-altered: installed-files.json binds to the runtime record and
  // the observed inventory must match it exactly by path, digest and mode.
  const installedFilesPath = join(snapshotPath, SNAPSHOT_LAYOUT.installedFiles);
  // The sealed inventory is in the controller's pre-dispatch checksum set, so a
  // tampered one is normally refused before doctor runs. When doctor is reached
  // directly, read and parse it defensively: a missing, non-regular, unreadable,
  // or malformed file (even one whose bytes match the recorded digest) is
  // tampering, reported as installed-file-altered, never a raw exception.
  let parsedInstalled: unknown;
  try {
    if (hashFile(installedFilesPath) !== runtimeRecord.installedFilesSha256) {
      return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} digest does not match the runtime record`);
    }
    parsedInstalled = readJson<unknown>(installedFilesPath);
  } catch {
    return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} is missing or unreadable`);
  }
  if (!isValidInventory(parsedInstalled)) {
    return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} is malformed`);
  }
  const installed = parsedInstalled as InstalledFiles;
  let observed: string[];
  try {
    observed = collectFiles(snapshotPath).filter(path => path !== SNAPSHOT_LAYOUT.installedFiles);
  } catch (error) {
    return fail('installed-file-altered', error instanceof TamperError ? `non-regular snapshot entry: ${error.message}` : String(error));
  }
  const recorded = new Set(Object.keys(installed.files));
  for (const path of observed) if (!recorded.has(path)) return fail('installed-file-altered', `unexpected snapshot file: ${path}`);
  const observedSet = new Set(observed);
  for (const path of recorded) if (!observedSet.has(path)) return fail('installed-file-altered', `missing snapshot file: ${path}`);
  for (const [path, entry] of Object.entries(installed.files)) {
    const abs = join(snapshotPath, path);
    if (hashFile(abs) !== entry.sha256) return fail('installed-file-altered', `snapshot digest mismatch: ${path}`);
    if (fileMode(abs) !== entry.mode) return fail('installed-file-altered', `snapshot mode mismatch: ${path}`);
  }

  // build-altered-release: the installed payload must still match the release
  // bytes recorded independently in the admission record (C4).
  const payloadRoot = join(snapshotPath, SNAPSHOT_LAYOUT.payload);
  for (const [path, digest] of Object.entries(record.files)) {
    let actual: string;
    try {
      actual = hashFile(join(payloadRoot, path));
    } catch {
      return fail('build-altered-release', `recorded release file missing: ${path}`);
    }
    if (actual !== digest) return fail('build-altered-release', `release file altered: ${path}`);
  }

  // unadmitted-fork: a supplied checkout is a separate attestation about bytes,
  // reported on `checkout` and never mutating installation health.
  const healthy: DoctorReport = { ...report('healthy', 'admitted', []), snapshot };
  if (options.checkout !== undefined) {
    healthy.checkout = checkoutMatches(options.checkout, record.files) ? 'matches-admitted-release' : 'unadmitted-fork';
  }
  return healthy;
}

type ParsedArgs = DoctorOptions | { usage: string };

function parseArgs(argv: string[]): ParsedArgs {
  let mode: string | undefined;
  let controlRoot: string | undefined;
  let checkout: string | undefined;
  for (let i = 0; i < argv.length; i++) {
    const flag = argv[i];
    const value = argv[i + 1];
    if (flag === '--mode') {
      if (value === undefined) return { usage: 'missing value for --mode' };
      mode = value;
      i++;
    } else if (flag === '--control-root') {
      if (value === undefined) return { usage: 'missing value for --control-root' };
      controlRoot = value;
      i++;
    } else if (flag === '--checkout') {
      if (value === undefined) return { usage: 'missing value for --checkout' };
      checkout = value;
      i++;
    } else {
      return { usage: `unexpected argument: ${flag}` };
    }
  }
  if (mode !== 'status' && mode !== 'doctor') return { usage: 'expected --mode status|doctor' };
  if (checkout !== undefined && mode !== 'doctor') return { usage: '--checkout requires --mode doctor' };
  return checkout === undefined ? { mode, controlRoot } : { mode, controlRoot, checkout };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const parsed = parseArgs(process.argv.slice(2));
  if ('usage' in parsed) {
    console.error(JSON.stringify({ status: 'usage', detail: parsed.usage }));
    process.exit(2);
  }
  const result = runDoctor(parsed);
  console.log(JSON.stringify(result));
  const ok = result.status === 'healthy' && (result.checkout === undefined || result.checkout === 'matches-admitted-release');
  process.exit(ok ? 0 : 1);
}
