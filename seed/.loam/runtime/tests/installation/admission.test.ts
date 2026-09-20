// Offline runtime-admission qualification (CORE-04).
//
// Flat node:test leaves, one per ADMISSION_CASES id, in the frozen plan-03
// order. The runner (src/testing/verify.ts) rejects any describe/skip/todo,
// nested case or count mismatch, so every id below is a top-level test() and the
// count equals ADMISSION_CASES.length (35).
//
// These cases drive the real admit path through admitRuntime with the
// fixture-only seam test.originPolicy 'file' (never a public CLI flag) and read
// status/doctor through the POSIX controller and the installed doctor.js. The
// scripted, mutating and failing dependency behaviors live in the committed
// fixture tarballs under assets/admission-fixtures/ (builder A); this file only
// selects them through package.json/package-lock.json and asserts the observable
// contract: the exact diagnostic code on every refusal, and byte-level state on
// every positive.
//
// Import-closure: only node: builtins and relative .js imports; probe scripts
// are opaque string literals, so their embedded require/import text is never a
// real module load.

import assert from 'node:assert/strict';
import { test, after } from 'node:test';
import {
  chmodSync, cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync,
  readFileSync, readlinkSync, realpathSync, renameSync, rmSync, symlinkSync, writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { spawn, spawnSync, type SpawnSyncReturns } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import {
  admitRuntime, controlRootState, installController, sealSnapshot, toolShim, trustedSpawnEnvironment, writeCanonicalAtomic, writeTextAtomic,
} from '../../src/installation/admit.js';
import {
  AdmissionError, canonicalJson, CONTROL_ROOT_LAYOUT, FIXTURE_ORIGIN_PREFIX, SNAPSHOT_LAYOUT,
  type AdmissionRecord, type AdmitOptions, type NATIVE_PREREQUISITES,
} from '../../src/contracts/installation.js';
import { cleanTestEnvironment } from '../../src/testing/verify.js';
import { createReleaseManifest, payloadFiles } from '../../src/installation/package.js';

const factoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const toolchain = process.env.LOAM_FACTORY_TOOLCHAIN ?? '';
const toolchainNode = join(toolchain, 'bin', 'node');
const isLinux = process.platform === 'linux';

const scratchRoots: string[] = [];
after(() => {
  for (const root of scratchRoots) {
    try { forceWritable(root); } catch { /* best effort */ }
    rmSync(root, { recursive: true, force: true });
  }
});

// A sealed snapshot is chmod a-w; make a tree writable before removal.
function forceWritable(root: string): void {
  const stack = [root];
  while (stack.length) {
    const path = stack.pop()!;
    let entry;
    try { entry = lstatSync(path); } catch { continue; }
    try { if (!entry.isSymbolicLink()) chmodSync(path, entry.isDirectory() ? 0o755 : 0o644); } catch { /* best effort */ }
    if (entry.isDirectory()) for (const name of readdirSync(path)) stack.push(join(path, name));
  }
}

function base(): string {
  const root = mkdtempSync(join(tmpdir(), 'loam-core04-'));
  scratchRoots.push(root);
  return root;
}

const DEFAULT_DEPS: Record<string, string> = { 'loam-dep-plain': '1.0.0', 'loam-dep-bin': '1.0.0' };

interface LockOptions {
  installScript?: string[];
  resolvedOverride?: Record<string, string>;
  dropIntegrity?: string[];
  missingTarball?: string[];
}

interface Trusted { repo: string; trusted: string; controller: string; }

// Build a scratch repository: sentinels three levels above a copy of the real
// payload whose package.json/package-lock.json name only the fixture
// dependencies, with the release manifest regenerated to stay self-consistent.
function makeTrusted(deps: Record<string, string> = DEFAULT_DEPS, lock: LockOptions = {}, opts: { dropSentinel?: boolean } = {}): Trusted {
  const repo = join(base(), 'repo');
  const trusted = join(repo, 'seed/.loam/runtime');
  mkdirSync(join(repo, 'bin'), { recursive: true });
  if (!opts.dropSentinel) writeFileSync(join(repo, 'copier.yml'), '# scratch trusted source\n');
  writeFileSync(join(repo, 'VERSION'), '0.0.0\n');
  writeFileSync(join(repo, 'bin/release.sh'), '#!/bin/sh\nexit 0\n');
  copyPayload(factoryRoot, trusted);
  writePackageJson(trusted, deps);
  writeLock(trusted, deps, lock);
  regenerateManifest(trusted);
  return { repo, trusted, controller: join(trusted, 'scripts', 'loam-control.sh') };
}

function copyPayload(from: string, to: string): void {
  for (const file of payloadFiles(from)) {
    const target = join(to, file);
    mkdirSync(dirname(target), { recursive: true });
    cpSync(join(from, file), target);
  }
}

function writePackageJson(trusted: string, deps: Record<string, string>): void {
  const pkg = { name: '@loam/factory', version: '0.0.0', private: true, type: 'module', dependencies: deps };
  writeFileSync(join(trusted, 'package.json'), `${JSON.stringify(pkg, null, 2)}\n`);
}

function integrityOf(tarball: string): string {
  return `sha512-${createHash('sha512').update(readFileSync(tarball)).digest('base64')}`;
}

function writeLock(trusted: string, deps: Record<string, string>, options: LockOptions): void {
  const packages: Record<string, unknown> = {
    '': { name: '@loam/factory', version: '0.0.0', dependencies: deps },
  };
  for (const [name, version] of Object.entries(deps)) {
    const resolved = options.resolvedOverride?.[name] ?? `${FIXTURE_ORIGIN_PREFIX}${name}-${version}.tgz`;
    const entry: Record<string, unknown> = { version, resolved };
    const tarball = join(trusted, 'assets/admission-fixtures', `${name}-${version}.tgz`);
    if (!options.dropIntegrity?.includes(name)) {
      entry.integrity = options.missingTarball?.includes(name) || !existsSync(tarball)
        ? `sha512-${'A'.repeat(86)}==`
        : integrityOf(tarball);
    }
    if (options.installScript?.includes(name)) entry.hasInstallScript = true;
    if (name === 'loam-dep-bin') entry.bin = { 'loam-dep-bin': 'cli.js' };
    packages[`node_modules/${name}`] = entry;
  }
  const doc = { name: '@loam/factory', version: '0.0.0', lockfileVersion: 3, requires: true, packages };
  writeFileSync(join(trusted, 'package-lock.json'), `${JSON.stringify(doc, null, 2)}\n`);
}

function regenerateManifest(trusted: string): void {
  writeFileSync(join(trusted, 'release-manifest.json'), `${JSON.stringify(createReleaseManifest(trusted), null, 2)}\n`);
}

// admit.ts authorizes install scripts through a top-level package.json
// `allowScripts` map keyed by name or name@version. The scripted fixture is
// authorized at its real version 1.0.0, so a dependency pinned to any other
// version stays uncovered and refuses with build-script-refused.
function allowScripts(trusted: string, names: string[]): void {
  const path = join(trusted, 'package.json');
  const pkg = JSON.parse(readFileSync(path, 'utf8')) as Record<string, unknown>;
  pkg.allowScripts = Object.fromEntries(names.map((name) => [`${name}@1.0.0`, true]));
  writeFileSync(path, `${JSON.stringify(pkg, null, 2)}\n`);
  regenerateManifest(trusted);
}

function prerequisites(entries: Record<string, { tools: Record<string, string>; loadSmoke: string }>): typeof NATIVE_PREREQUISITES {
  return entries as typeof NATIVE_PREREQUISITES;
}

function freshControlRoot(): string {
  const root = join(base(), 'control');
  mkdirSync(root, { recursive: true });
  return root;
}

function admitOptions(trusted: string, controlRoot: string, test: Partial<AdmitOptions['test']> = {}, releaseIdentity = 'loam v0.0.0'): AdmitOptions {
  return { trustedSource: trusted, controlRoot, toolchain, releaseIdentity, test: { originPolicy: 'file', ...test } };
}

async function admit(trusted: string, controlRoot: string, test: Partial<AdmitOptions['test']> = {}, releaseIdentity = 'loam v0.0.0'): Promise<{ id: string; snapshotPath: string; admissionPath: string }> {
  return admitRuntime(admitOptions(trusted, controlRoot, test, releaseIdentity));
}

// Assert an admission refuses with exactly `code`.
async function refuses(run: () => Promise<unknown>, code: string): Promise<void> {
  try {
    await run();
  } catch (error) {
    assert.ok(error instanceof AdmissionError, `expected AdmissionError, got ${String(error)}`);
    assert.equal((error as AdmissionError).diagnostic, code);
    return;
  }
  throw new Error(`expected ${code}; admission resolved`);
}

// Run admit in a child so the test.faultAfter seam (which exits the process with
// code 70) never kills the test runner. The child prints OK:<json> or
// ERR:<diagnostic>.
function admitChildRunner(dir: string): string {
  const runner = join(dir, 'admit-runner.mjs');
  const admitUrl = pathToFileURL(join(factoryRoot, 'dist/src/installation/admit.js')).href;
  writeFileSync(runner, `import { admitRuntime } from ${JSON.stringify(admitUrl)};
admitRuntime(JSON.parse(process.argv[2]))
  .then((value) => process.stdout.write('OK:' + JSON.stringify(value)))
  .catch((error) => { process.stdout.write('ERR:' + ((error && error.diagnostic) || (error && error.message) || String(error))); process.exit(1); });
`);
  return runner;
}
function runChildAdmit(runner: string, options: AdmitOptions): SpawnSyncReturns<string> {
  return spawnSync(toolchainNode, [runner, JSON.stringify(options)], { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120000 });
}

// Invoke the POSIX controller. status/doctor take only --control-root.
function control(controller: string, controlRoot: string | null, verb: string[], env: NodeJS.ProcessEnv = cleanTestEnvironment()): SpawnSyncReturns<string> {
  const args = [controller];
  if (controlRoot !== null) args.push('--control-root', controlRoot);
  args.push(...verb);
  return spawnSync('/bin/sh', args, { env, encoding: 'utf8', timeout: 120000 });
}

function lastJson(output: string): Record<string, unknown> {
  const line = output.trim().split('\n').filter(Boolean).at(-1);
  assert.ok(line, `no output line to parse: ${JSON.stringify(output)}`);
  return JSON.parse(line) as Record<string, unknown>;
}

// A diagnostic may be reported by the controller as a top-level {diagnostic}
// wrapper (pre-dispatch and state-table detections) or by dispatched doctor as a
// DoctorReport {diagnostics:[{code}]}. Accept either shape.
function hasDiagnostic(report: Record<string, unknown>, code: string): boolean {
  if (report.diagnostic === code) return true;
  const list = report.diagnostics;
  return Array.isArray(list) && list.some((entry) => (entry as { code?: string }).code === code);
}

function readRecord(controlRoot: string, id: string): AdmissionRecord {
  return JSON.parse(readFileSync(join(controlRoot, CONTROL_ROOT_LAYOUT.admissions, `${id}.json`), 'utf8')) as AdmissionRecord;
}

// Hash every non-directory in a tree, recording symlink targets, for
// before/after equality scans.
function hashTree(root: string): Map<string, string> {
  const out = new Map<string, string>();
  const stack = [root];
  while (stack.length) {
    const path = stack.pop()!;
    const entry = lstatSync(path);
    const rel = relative(root, path) || '.';
    if (entry.isSymbolicLink()) { out.set(rel, `symlink:${readlinkSync(path)}`); continue; }
    if (entry.isDirectory()) { for (const name of readdirSync(path)) stack.push(join(path, name)); continue; }
    out.set(rel, createHash('sha256').update(readFileSync(path)).digest('hex'));
  }
  return out;
}
function assertUnchanged(before: Map<string, string>, after: Map<string, string>): void {
  assert.deepEqual([...after.keys()].sort(), [...before.keys()].sort());
  for (const [key, value] of before) assert.equal(after.get(key), value, `changed: ${key}`);
}

function walkFiles(root: string): string[] {
  const out: string[] = [];
  const stack = [root];
  while (stack.length) {
    const path = stack.pop()!;
    const entry = lstatSync(path);
    if (entry.isDirectory()) { for (const name of readdirSync(path)) stack.push(join(path, name)); continue; }
    out.push(relative(root, path));
  }
  return out.sort();
}

function anySymlink(root: string): boolean {
  const stack = [root];
  while (stack.length) {
    const path = stack.pop()!;
    const entry = lstatSync(path);
    if (entry.isSymbolicLink()) return true;
    if (entry.isDirectory()) for (const name of readdirSync(path)) stack.push(join(path, name));
  }
  return false;
}

// Edit a file inside a sealed (read-only) snapshot: relax the mode, write, and
// leave it relaxed for cleanup.
function tamper(path: string, contents: string): void {
  chmodSync(dirname(path), 0o755);
  chmodSync(path, 0o644);
  writeFileSync(path, contents);
}

// ---------------------------------------------------------------------------
// Bullet 1
// ---------------------------------------------------------------------------

test('admission.trusted-source-identity', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  // A separate self-consistent candidate that admission must never read.
  const candidate = makeTrusted();
  tamper(join(candidate.trusted, 'launcher.mjs'), '// altered candidate\n');
  regenerateManifest(candidate.trusted);
  const candidateBefore = hashTree(candidate.trusted);

  const { id } = await admit(trusted, controlRoot);
  const record = readRecord(controlRoot, id);
  assert.equal(record.release.label, 'loam v0.0.0');
  assert.match(record.tools.node.sha256, /^[0-9a-f]{64}$/);
  assert.equal(record.release.sourcePath, realpathSync(trusted));
  assertUnchanged(candidateBefore, hashTree(candidate.trusted));
});

test('admission.trusted-source-fork', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { id } = await admit(trusted, controlRoot, {}, 'local-fork loam v0.0.0');
  assert.equal(readRecord(controlRoot, id).release.label, 'local-fork loam v0.0.0');
});

test('admission.trusted-source-shape', async () => {
  // A rendered .loam/runtime (no seed/ segment): root holds .loam/runtime.
  const rendered = join(base(), 'rendered');
  const renderedFactory = join(rendered, '.loam/runtime');
  mkdirSync(join(rendered, 'bin'), { recursive: true });
  for (const name of ['copier.yml', 'VERSION']) writeFileSync(join(rendered, name), '0\n');
  writeFileSync(join(rendered, 'bin/release.sh'), '#!/bin/sh\n');
  copyPayload(factoryRoot, renderedFactory);
  await refuses(() => admit(renderedFactory, freshControlRoot()), 'trusted-source-shape');

  // Repository root lacks a sentinel (copier.yml).
  const noSentinel = makeTrusted(DEFAULT_DEPS, {}, { dropSentinel: true });
  await refuses(() => admit(noSentinel.trusted, freshControlRoot()), 'trusted-source-shape');

  // Trusted source inside the control root.
  const controlRoot = freshControlRoot();
  const inside = join(controlRoot, 'seed/.loam/runtime');
  mkdirSync(join(controlRoot, 'bin'), { recursive: true });
  for (const name of ['copier.yml', 'VERSION']) writeFileSync(join(controlRoot, name), '0\n');
  writeFileSync(join(controlRoot, 'bin/release.sh'), '#!/bin/sh\n');
  copyPayload(factoryRoot, inside);
  await refuses(() => admit(inside, controlRoot), 'trusted-source-shape');
});

test('admission.wrong-release-digest', async () => {
  const { trusted } = makeTrusted();
  // Change a payload file without regenerating the manifest: files and manifest
  // now disagree.
  tamper(join(trusted, 'launcher.mjs'), `${readFileSync(join(trusted, 'launcher.mjs'), 'utf8')}\n// drift\n`);
  await refuses(() => admit(trusted, freshControlRoot()), 'wrong-release-digest');
});

test('admission.identities-recorded-separately', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { id, snapshotPath } = await admit(trusted, controlRoot);
  const record = readRecord(controlRoot, id);
  // The release map is the payload file map only: no node_modules key.
  assert.ok(Object.keys(record.files).length > 0);
  assert.ok(!Object.keys(record.files).some((key) => key.startsWith('node_modules') || key.includes('/node_modules/')));
  // The installed inventory binds the full closure including node, npm, the
  // controller and the modules.
  const installed = JSON.parse(readFileSync(join(snapshotPath, SNAPSHOT_LAYOUT.installedFiles), 'utf8')) as { files: Record<string, unknown> };
  const installedKeys = Object.keys(installed.files);
  for (const needed of [SNAPSHOT_LAYOUT.node, SNAPSHOT_LAYOUT.npmCli, SNAPSHOT_LAYOUT.controller]) assert.ok(installedKeys.includes(needed), `installed map missing ${needed}`);
  assert.ok(installedKeys.some((key) => key.startsWith(`${SNAPSHOT_LAYOUT.modules}/`)), 'installed map must cover node_modules');
  // registry/runtimes/<id>.sha256 is derived from installed-files.json.
  const sha256File = readFileSync(join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.sha256`), 'utf8');
  assert.ok(sha256File.includes(SNAPSHOT_LAYOUT.installedFiles));
  assert.ok(sha256File.includes(SNAPSHOT_LAYOUT.node));
  assert.ok(sha256File.includes(SNAPSHOT_LAYOUT.controller));
});

// ---------------------------------------------------------------------------
// Bullet 2
// ---------------------------------------------------------------------------

test('admission.staging-writes-contained', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const nodeBefore = createHash('sha256').update(readFileSync(toolchainNode)).digest('hex');
  const { snapshotPath } = await admit(trusted, controlRoot);
  // No staging or tool directory and no npm log survives.
  const runtimes = readdirSync(join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes));
  assert.ok(!runtimes.some((name) => name.startsWith(CONTROL_ROOT_LAYOUT.stagingPrefix) || name.startsWith(CONTROL_ROOT_LAYOUT.toolPrefix)));
  assert.ok(!walkFiles(controlRoot).some((file) => file.includes('_logs')));
  // Effective bin-links off is observable as the absence of any .bin symlink.
  assert.ok(!existsSync(join(snapshotPath, SNAPSHOT_LAYOUT.modules, '.bin')));
  assert.equal(anySymlink(snapshotPath), false);
  // The toolchain node the fixture used is untouched.
  assert.equal(createHash('sha256').update(readFileSync(toolchainNode)).digest('hex'), nodeBefore);
});

test('admission.bin-links-absent', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { snapshotPath } = await admit(trusted, controlRoot);
  assert.equal(existsSync(join(snapshotPath, SNAPSHOT_LAYOUT.modules, '.bin')), false);
  assert.equal(anySymlink(snapshotPath), false);
});

test('admission.lock-origin-refused', async () => {
  // Production policy (no file seam): each forbidden origin and a missing
  // integrity refuse before any fetch; the root entry is exempt.
  for (const override of [
    { 'loam-dep-plain': 'git+https://example.invalid/dep.git' },
    { 'loam-dep-plain': 'https://example.invalid/dep.tgz' },
    { 'loam-dep-plain': 'file:assets/admission-fixtures/loam-dep-plain-1.0.0.tgz' },
  ]) {
    const { trusted } = makeTrusted(DEFAULT_DEPS, { resolvedOverride: override });
    await refuses(() => admitRuntime({ trustedSource: trusted, controlRoot: freshControlRoot(), toolchain, releaseIdentity: 'loam v0.0.0' }), 'lock-origin-refused');
  }
  const noIntegrity = makeTrusted(DEFAULT_DEPS, { dropIntegrity: ['loam-dep-plain'] });
  await refuses(() => admitRuntime({ trustedSource: noIntegrity.trusted, controlRoot: freshControlRoot(), toolchain, releaseIdentity: 'loam v0.0.0' }), 'lock-origin-refused');
});

test('admission.build-script-refused', async () => {
  const deps = { ...DEFAULT_DEPS, 'loam-dep-scripted': '1.0.0' };
  // Scripted dependency declares a lifecycle script but is not covered.
  const uncovered = makeTrusted(deps, { installScript: ['loam-dep-scripted'] });
  const controlRoot = freshControlRoot();
  await refuses(() => admit(uncovered.trusted, controlRoot), 'build-script-refused');
  assert.equal(existsSync(join(uncovered.trusted, 'assets/admission-fixtures/loam-dep-scripted', 'marker')), false);

  // Covered, but pinned to the wrong version.
  const wrongVersion = makeTrusted({ ...DEFAULT_DEPS, 'loam-dep-scripted': '9.9.9' }, { installScript: ['loam-dep-scripted'] });
  allowScripts(wrongVersion.trusted, ['loam-dep-scripted']);
  await refuses(() => admit(wrongVersion.trusted, freshControlRoot()), 'build-script-refused');
});

test('admission.build-requires-containment', async () => {
  const deps = { ...DEFAULT_DEPS, 'loam-dep-scripted': '1.0.0' };
  const { trusted } = makeTrusted(deps, { installScript: ['loam-dep-scripted'] });
  allowScripts(trusted, ['loam-dep-scripted']);
  const controlRoot = freshControlRoot();
  await refuses(() => admit(trusted, controlRoot, {
    containment: 'unavailable',
    nativePrerequisites: prerequisites({ 'loam-dep-scripted': { tools: { sh: '/bin/sh' }, loadSmoke: 'node_modules/loam-dep-scripted/smoke.mjs' } }),
  }), 'containment-unavailable');
  assert.equal(existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.selected)), false);
});

test('admission.native-prerequisite-missing', async () => {
  const deps = { ...DEFAULT_DEPS, 'loam-dep-scripted': '1.0.0' };
  // Covered script with no contract entry at all.
  const noEntry = makeTrusted(deps, { installScript: ['loam-dep-scripted'] });
  allowScripts(noEntry.trusted, ['loam-dep-scripted']);
  await refuses(() => admit(noEntry.trusted, freshControlRoot(), { nativePrerequisites: prerequisites({}) }), 'native-prerequisite-missing');

  // Contract entry whose tool path does not exist.
  const missingTool = makeTrusted(deps, { installScript: ['loam-dep-scripted'] });
  allowScripts(missingTool.trusted, ['loam-dep-scripted']);
  await refuses(() => admit(missingTool.trusted, freshControlRoot(), {
    nativePrerequisites: prerequisites({ 'loam-dep-scripted': { tools: { cc: join(base(), 'no/such/cc') }, loadSmoke: 'node_modules/loam-dep-scripted/smoke.mjs' } }),
  }), 'native-prerequisite-missing');

  // Linux only: an existing, executable tool whose realpath lies outside the
  // exposed system roots is refused for its root, not for absence.
  if (isLinux) {
    const outsideDir = join(base(), 'outside-roots');   // under $TMPDIR, not /usr,/lib,/lib64,/bin,/sbin
    mkdirSync(outsideDir, { recursive: true });
    const outsideCc = join(outsideDir, 'cc');
    writeFileSync(outsideCc, '#!/bin/sh\nexit 0\n');
    chmodSync(outsideCc, 0o755);
    const outside = makeTrusted(deps, { installScript: ['loam-dep-scripted'] });
    allowScripts(outside.trusted, ['loam-dep-scripted']);
    try {
      await admit(outside.trusted, freshControlRoot(), {
        nativePrerequisites: prerequisites({ 'loam-dep-scripted': { tools: { cc: outsideCc }, loadSmoke: 'node_modules/loam-dep-scripted/smoke.mjs' } }),
      });
      assert.fail('an executable outside the exposed roots must be refused');
    } catch (error) {
      assert.ok(error instanceof AdmissionError, String(error));
      assert.equal((error as AdmissionError).diagnostic, 'native-prerequisite-missing');
      assert.ok(String((error as AdmissionError).message).includes('outside the exposed system roots'),
        'must refuse for the root, not for absence');
    }
  }

  // The tool shim POSIX-quotes a space and a single quote so exec receives one
  // literal path (offline, deterministic; the Linux root check confines the real
  // tool path, so byte-exactness is the right proof of the quoting rule). (R4-B3)
  assert.equal(toolShim("/tmp/a b/it's/cc"), "#!/bin/sh\nexec '/tmp/a b/it'\\''s/cc' \"$@\"\n");
});

test('admission.dependency-missing', async () => {
  // A run-unique proxy sentinel, built at runtime so it appears in no source
  // file. admit copies the payload dist (compiled test files included) into the
  // staging workspace, so any static sentinel literal would be a false positive
  // in the retained-file scan below; a runtime value is only present if the fetch
  // child actually leaked it.
  const SENTINEL = `https://user:leak-${Date.now()}-${Math.random().toString(36).slice(2)}@proxy-probe.invalid/`;
  const deps = { ...DEFAULT_DEPS, 'loam-dep-absent': '1.0.0' };
  const { trusted } = makeTrusted(deps, { missingTarball: ['loam-dep-absent'] });
  const controlRoot = freshControlRoot();
  const savedProxy = process.env.HTTPS_PROXY;
  try {
    process.env.HTTPS_PROXY = SENTINEL;               // fetch child inherits it via trustedSpawnEnvironment('fetch')
    await refuses(() => admit(trusted, controlRoot), 'dependency-missing');
  } finally {
    if (savedProxy === undefined) delete process.env.HTTPS_PROXY; else process.env.HTTPS_PROXY = savedProxy;
  }
  assert.equal(existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.selected)), false);
  // No retained staging file carries the proxy sentinel (failed-fetch log cleanup, C1).
  for (const rel of walkFiles(controlRoot)) {
    const bytes = readFileSync(join(controlRoot, rel));
    assert.equal(bytes.includes(Buffer.from(SENTINEL)), false, `proxy sentinel retained in ${rel}`);
  }
});

test('admission.publication-order', async () => {
  // Each abrupt fault leaves the lock; the controller reports the lock first
  // (C3). Only in this disposable fixture do we remove the stale lock and then
  // assert the underlying phase state, and that a new admit refuses with it.
  const faults: { after: NonNullable<AdmitOptions['test']>['faultAfter']; detail: string; complete: boolean }[] = [
    { after: 'seal', detail: 'staging', complete: false },
    { after: 'chmod', detail: 'staging', complete: false },
    { after: 'rename', detail: 'unregistered', complete: false },
    { after: 'admission-record', detail: 'unregistered', complete: false },
    { after: 'sha256', detail: 'unregistered', complete: false },
    { after: 'runtime-record', detail: 'unselected', complete: false },
    { after: 'controller', detail: 'unselected', complete: false },
    { after: 'selected', detail: 'selection', complete: true },
  ];
  for (const fault of faults) {
    const controlRoot = freshControlRoot();
    const { trusted } = makeTrusted();
    const runner = admitChildRunner(base());
    const child = runChildAdmit(runner, admitOptions(trusted, controlRoot, { faultAfter: fault.after }));
    assert.equal(child.status, 70, `fault ${fault.after}: ${child.stdout}${child.stderr}`);
    const lockPath = join(controlRoot, CONTROL_ROOT_LAYOUT.lock);
    assert.ok(existsSync(lockPath), `fault ${fault.after}: lock retained`);
    // The controller reports the lock first.
    const locked = control(join(trusted, 'scripts', 'loam-control.sh'), controlRoot, ['status']);
    assert.equal(locked.status, 1);
    const lockedReport = lastJson(locked.stdout);
    assert.equal(lockedReport.diagnostic, 'install-interrupted');
    assert.ok(String(lockedReport.detail).includes('lock'));
    // Remove the stale lock in the fixture only, then read the underlying state.
    rmSync(lockPath);
    const under = control(join(trusted, 'scripts', 'loam-control.sh'), controlRoot, ['status']);
    if (fault.complete) {
      assert.equal(under.status, 0, `fault ${fault.after}: ${under.stdout}${under.stderr}`);
      assert.equal(lastJson(under.stdout).status, 'healthy');
    } else {
      assert.equal(under.status, 1);
      const report = lastJson(under.stdout);
      assert.equal(report.diagnostic, 'install-interrupted');
      assert.ok(String(report.detail).includes(fault.detail), `fault ${fault.after}: detail ${String(report.detail)}`);
      // A fresh admit refuses with the same interrupted state; nothing deleted.
      const before = hashTree(controlRoot);
      await refuses(() => admit(trusted, controlRoot), 'install-interrupted');
      assertUnchanged(before, hashTree(controlRoot));
    }
  }
});

test('admission.publish-complete-closure-only', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { snapshotPath } = await admit(trusted, controlRoot);
  assert.ok(existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.selected)));
  const runtimes = readdirSync(join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes));
  assert.ok(!runtimes.some((name) => name.startsWith(CONTROL_ROOT_LAYOUT.stagingPrefix) || name.startsWith(CONTROL_ROOT_LAYOUT.toolPrefix)));
  // The snapshot is read-only.
  assert.throws(() => writeFileSync(join(snapshotPath, 'intrusion'), 'x'));
  // The closure equals the recorded inventory exactly.
  const installed = JSON.parse(readFileSync(join(snapshotPath, SNAPSHOT_LAYOUT.installedFiles), 'utf8')) as { files: Record<string, unknown> };
  const recorded = new Set([...Object.keys(installed.files), SNAPSHOT_LAYOUT.installedFiles]);
  assert.deepEqual(new Set(walkFiles(snapshotPath)), recorded);
  // B1: startup-closure is inventoried and lists exactly doctor.js's transitive
  // relative-import closure (the eight startup modules), sorted canonically.
  assert.ok(recorded.has('startup-closure'), 'startup-closure must be inventoried');
  assert.deepEqual(
    readFileSync(join(snapshotPath, 'startup-closure'), 'utf8').split('\n').filter(Boolean),
    [
      'payload/dist/src/commands/doctor.js',
      'payload/dist/src/contracts/installation.js',
      'payload/dist/src/installation/admit.js',
      'payload/dist/src/installation/package.js',
      'payload/dist/src/platform/env-policy.js',
      'payload/dist/src/platform/native-boundary.js',
      'payload/dist/src/platform/runtime.js',
      'payload/dist/src/platform/util.js',
    ],
  );
});

// ---------------------------------------------------------------------------
// Bullet 3
// ---------------------------------------------------------------------------

test('admission.control-strips-environment', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  // A caller cannot pass the internal --clean marker to skip sanitization.
  const cleanFirst = spawnSync('/bin/sh',
    [controller, '--clean', 'status', '--control-root', controlRoot],
    { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
  assert.equal(cleanFirst.status, 2);
  assert.equal(lastJson(cleanFirst.stdout).status, 'usage');
  const cleanLate = spawnSync('/bin/sh',
    [controller, '--control-root', controlRoot, 'status', '--clean'],
    { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
  assert.equal(cleanLate.status, 2);
  assert.equal(lastJson(cleanLate.stdout).status, 'usage');
  const dir = base();
  const marker = join(dir, 'preload-ran');
  const preload = join(dir, 'preload.cjs');
  writeFileSync(preload, `require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'ran');`);
  const poisoned = cleanTestEnvironment({
    NODE_OPTIONS: `--require ${preload}`,
    NODE_PATH: dir,
    npm_config_registry: 'https://example.invalid/',
    GIT_DIR: dir,
    NODE_TLS_REJECT_UNAUTHORIZED: '0',
  });
  // Positive control: the preload runs under a bare node.
  const positive = spawnSync(toolchainNode, ['-e', '0'], { env: { ...poisoned }, encoding: 'utf8', timeout: 30000 });
  assert.equal(positive.status, 0, positive.stderr);
  assert.ok(existsSync(marker), 'preload must run in the positive control');
  rmSync(marker);
  // The controller suppresses it and reports a clean environment.
  const status = control(controller, controlRoot, ['doctor'], poisoned);
  assert.equal(status.status, 0, status.stderr);
  assert.equal(existsSync(marker), false, 'controller must strip NODE_OPTIONS preload');
  assert.equal(lastJson(status.stdout).status, 'healthy');
  // The fetch child carries the proxy; the control/build/smoke env never does.
  // An end-to-end capture is not offline-observable (fetch runs --ignore-scripts
  // and --offline), so this is proved at the trustedSpawnEnvironment boundary; the
  // executed build/smoke-absent half is the host case contain.build-no-proxy-or-credentials.
  const savedProxy = process.env.HTTPS_PROXY;
  try {
    process.env.HTTPS_PROXY = 'https://user:secret@proxy.invalid/';
    const b = { home: '/h', path: '/p', tmpdir: '/t' };
    const fetchEnv = trustedSpawnEnvironment('fetch', b);
    const controlEnv = trustedSpawnEnvironment('control', b);
    assert.equal(fetchEnv.HTTPS_PROXY, 'https://user:secret@proxy.invalid/', 'fetch child carries the proxy');
    assert.equal('HTTPS_PROXY' in controlEnv, false, 'control/build/smoke env never carries the proxy');
    // Empty proxy values are dropped, not forwarded as empty strings.
    process.env.HTTPS_PROXY = '';
    assert.equal('HTTPS_PROXY' in trustedSpawnEnvironment('fetch', b), false, 'empty proxy is dropped');
  } finally {
    if (savedProxy === undefined) delete process.env.HTTPS_PROXY; else process.env.HTTPS_PROXY = savedProxy;
  }
});

test('admission.control-helper-path-isolated', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  const fakeBin = join(base(), 'fakebin');
  mkdirSync(fakeBin);
  const marker = join(fakeBin, 'helper-ran');
  for (const name of ['shasum', 'sha256sum', 'uname', 'grep', 'sed', 'cut', 'mktemp', 'sort', 'env']) {
    const path = join(fakeBin, name);
    writeFileSync(path, `#!/bin/sh\necho ran >> ${JSON.stringify(marker)}\nexit 0\n`);
    chmodSync(path, 0o755);
  }
  const startup = join(fakeBin, 'startup.sh');
  writeFileSync(startup, `echo ran >> ${JSON.stringify(marker)}\n`);
  const withFakes = cleanTestEnvironment({ PATH: `${fakeBin}:/usr/bin:/bin`, ENV: startup, BASH_ENV: startup });
  // Positive control: a fake helper runs when the caller PATH is honored.
  const positive = spawnSync('/bin/sh', ['-c', 'uname'], { env: withFakes, encoding: 'utf8', timeout: 30000 });
  assert.equal(positive.status, 0);
  assert.ok(existsSync(marker), 'fake helper must run in the positive control');
  rmSync(marker);
  // The controller uses absolute helpers from a fixed PATH and still verifies.
  const status = control(controller, controlRoot, ['status'], withFakes);
  assert.equal(status.status, 0, status.stderr);
  assert.equal(existsSync(marker), false, 'controller must not run caller-PATH or ENV-poisoned helpers');
  assert.equal(lastJson(status.stdout).status, 'healthy');
});

test('admission.control-rejects-arguments', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  // Unknown verb.
  const unknown = control(controller, controlRoot, ['frobnicate']);
  assert.equal(unknown.status, 2);
  assert.equal(lastJson(unknown.stdout).status, 'usage');
  // Extra positional to a known verb.
  const extra = control(controller, controlRoot, ['status', 'extra']);
  assert.equal(extra.status, 2);
  assert.equal(lastJson(extra.stdout).status, 'usage');
  // Relative --control-root.
  const relativeRoot = spawnSync('/bin/sh', [controller, '--control-root', 'relative/root', 'status'], { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
  assert.equal(relativeRoot.status, 2);
  assert.equal(lastJson(relativeRoot.stdout).status, 'usage');
  // A snapshot id outside the grammar planted in selected.json is a malformed
  // selection, not a dispatch.
  tamper(join(controlRoot, CONTROL_ROOT_LAYOUT.selected), JSON.stringify({ version: 1, snapshotId: '../escape', admissionId: '../escape' }));
  const malformed = control(controller, controlRoot, ['status']);
  assert.equal(malformed.status, 1);
  const report = lastJson(malformed.stdout);
  assert.equal(report.diagnostic, 'install-interrupted');
  assert.ok(String(report.detail).includes('selection'));
  // selected.json missing its canonical trailing newline is refused (shell/Node parity).
  const good = { version: 1, snapshotId: 'a'.repeat(16), admissionId: 'a'.repeat(16) };
  tamper(join(controlRoot, CONTROL_ROOT_LAYOUT.selected), canonicalJson(good)); // no trailing "\n"
  let r = control(controller, controlRoot, ['status']);
  assert.equal(r.status, 1);
  assert.equal(lastJson(r.stdout).diagnostic, 'install-interrupted');
  assert.ok(String(lastJson(r.stdout).detail).includes('selection'));
  // trailing content after the canonical record is refused.
  tamper(join(controlRoot, CONTROL_ROOT_LAYOUT.selected), `${canonicalJson(good)}\n{"x":1}\n`);
  r = control(controller, controlRoot, ['status']);
  assert.equal(r.status, 1);
  assert.equal(lastJson(r.stdout).diagnostic, 'install-interrupted');
  // A control byte in an operator-supplied argument is refused with one valid JSON
  // usage line and no dispatch, at every position: leading, embedded and trailing.
  // A trailing newline is the byte the old line-count check missed (B3); the
  // constant-detail refusal keeps the JSON valid because it never echoes the bad
  // value (C1; shell-json-probe.json).
  function controllerUsage(args: string[], label: string): void {
    const r = spawnSync('/bin/sh', [controller, ...args], { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
    assert.equal(r.status, 2, `${label}: ${r.stdout}${r.stderr}`);
    const usageLine = r.stdout.trim().split('\n').filter(Boolean).at(-1) ?? '';
    assert.doesNotThrow(() => JSON.parse(usageLine), `${label}: refusal must be valid JSON: ${JSON.stringify(r.stdout)}`);
    assert.equal((JSON.parse(usageLine) as { status?: string }).status, 'usage', `${label}: ${r.stdout}`);
  }
  const positions: Array<[string, (s: string) => string]> = [
    ['leading', (s) => `\n${s}`],
    ['embedded', (s) => `${s.slice(0, 2)}\n${s.slice(2)}`],
    ['trailing', (s) => `${s}\n`],
  ];
  for (const [pos, mk] of positions) {
    controllerUsage(['--control-root', mk('/missing-root'), 'status'], `${pos} newline in --control-root`);
    controllerUsage(['--control-root', controlRoot, mk('badarg')], `${pos} newline in an unrecognized argument`);
  }
  // A rotated --protect-* value carrying a trailing newline is refused at the
  // boundary before any dispatch (B3: fixing contains_control alone does not reach
  // the rotated protect values).
  const protectRoot = freshControlRoot();
  controllerUsage(
    ['--control-root', protectRoot, '--toolchain', toolchain, 'admit',
      '--trusted-source', trusted, '--release-identity', 'loam v0.0.0', '--protect-state', '/tmp/x\n'],
    'trailing newline in --protect-state');
  assert.equal(existsSync(join(protectRoot, 'runtimes')), false, 'nothing must be admitted');
  // (b) A literal __loam_end__ positional is just an unexpected admit argument now
  // that the rotator counts the entry positionals instead of using a sentinel
  // word; it is refused and nothing is admitted.
  const admitRoot = freshControlRoot();
  const litEnd = spawnSync('/bin/sh',
    [controller, '--control-root', admitRoot, '--toolchain', toolchain, 'admit',
      '--trusted-source', trusted, '--release-identity', 'loam v0.0.0', '__loam_end__'],
    { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
  assert.equal(litEnd.status, 2);
  assert.equal(lastJson(litEnd.stdout).status, 'usage');
  assert.equal(existsSync(join(admitRoot, 'runtimes')), false, 'nothing must be admitted');
});

test('admission.controller-verifies-before-dispatch', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  const { id, snapshotPath } = await admit(trusted, controlRoot);

  const marker = join(base(), 'altered-doctor-ran');
  const doctorPath = join(snapshotPath, SNAPSHOT_LAYOUT.doctor);
  const doctorOriginal = readFileSync(doctorPath);
  tamper(doctorPath, `${doctorOriginal.toString('utf8')}\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)}, 'ran');\n`);
  const status = control(controller, controlRoot, ['status']);
  assert.equal(status.status, 1);
  assert.ok(hasDiagnostic(lastJson(status.stdout), 'installed-file-altered'));
  assert.equal(existsSync(marker), false, 'altered doctor must never execute');
  // Restore the healthy doctor bytes so the grammar checks below are the sole
  // refuser of the corrupt records (B3.3): the digest tool would accept every
  // referenced file, so a controller with no grammar validation would dispatch.
  writeFileSync(doctorPath, doctorOriginal);

  // B1: a package.json inserted anywhere under payload/dist is a nearer module
  // scope Node reads before doctor, and a node_modules there is a bare-specifier
  // root. Each is refused pre-dispatch with a structured installed-file-altered,
  // and no Node process runs (the loader never reports ERR_INVALID_PACKAGE_CONFIG
  // or an import SyntaxError on stderr).
  const distDir = join(snapshotPath, 'payload/dist');
  const commandsDir = join(snapshotPath, 'payload/dist/src/commands');
  function expectMetadataRefused(target: string, make: () => void): void {
    chmodSync(dirname(target), 0o755);
    make();
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `${rr.stdout}${rr.stderr}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'), `metadata refused: ${target}`);
    assert.ok(!rr.stderr.includes('ERR_INVALID_PACKAGE_CONFIG')
      && !rr.stderr.includes('SyntaxError')
      && !rr.stderr.includes('Cannot use import'),
      `no Node loader crash means the shell refused before dispatch: ${JSON.stringify(rr.stderr)}`);
    rmSync(target, { recursive: true, force: true });
  }
  expectMetadataRefused(join(distDir, 'package.json'), () => writeFileSync(join(distDir, 'package.json'), '{'));                          // malformed, nearest at dist
  expectMetadataRefused(join(distDir, 'package.json'), () => writeFileSync(join(distDir, 'package.json'), '{"type":"commonjs"}'));        // valid JSON, type change
  expectMetadataRefused(join(commandsDir, 'package.json'), () => writeFileSync(join(commandsDir, 'package.json'), '{"type":"commonjs"}'));// nearer, beside doctor.js
  expectMetadataRefused(join(distDir, 'node_modules'), () => mkdirSync(join(distDir, 'node_modules')));                                   // bare-specifier root under payload/dist

  // The pre-dispatch checksum grammar refuses a record that escapes the snapshot,
  // is malformed, or omits a required startup entry, before the digest tool or any
  // snapshot code runs (R3/C1/B1). With the healthy snapshot restored, every
  // grammar-only record below references bytes the digest tool would accept, so the
  // grammar itself is provably what refuses each one.
  const sums = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.sha256`);
  const orig = readFileSync(sums, 'utf8');
  const H = '0'.repeat(64);
  const snapshotDir = join(controlRoot, 'runtimes', id);

  // B3.3 isolation: a real, non-required snapshot file used as a disposable
  // grammar target. Its digest is genuine, so the raw digest tool accepts every
  // line of the records below and only the controller's path grammar refuses them.
  // (doctor.js.map is shipped and recorded but is not a required startup entry.)
  const dispose = orig.match(/^([0-9a-f]{64})  (payload\/dist\/src\/commands\/doctor\.js\.map)$/m)!;
  const disposeDigest = dispose[1];
  const disposePath = dispose[2];
  const digestCheck = isLinux ? ['/usr/bin/sha256sum', '-c'] : ['/usr/bin/shasum', '-a', '256', '-c'];

  // Grammar-only records: the full healthy record (every required entry present,
  // every digest real) plus one extra line whose path breaks a grammar rule while
  // still resolving to a real file with its true digest. Each must pass the raw
  // digest tool from the snapshot dir (exit 0) yet be refused by the controller,
  // proving the grammar - not a missing entry or a wrong digest - is the refuser.
  const grammarOnly = [
    `${orig}${disposeDigest}  ${join(snapshotDir, disposePath)}\n`,       // absolute path (rule 3)
    `${orig}${disposeDigest}  payload/dist/src/commands/../commands/doctor.js.map\n`, // '..' component resolving inside (rule 4)
  ];
  for (const record of grammarOnly) {
    tamper(sums, record);
    const raw = spawnSync(digestCheck[0], [...digestCheck.slice(1), sums], { cwd: snapshotDir, encoding: 'utf8', timeout: 60000 });
    assert.equal(raw.status, 0, `raw digest tool must accept the record: ${raw.stdout}${raw.stderr}`);
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `grammar must refuse: ${JSON.stringify(record)}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'), `installed-file-altered: ${JSON.stringify(record)}`);
  }

  // Omitted-required-entry records: a regenerated record that drops a required
  // startup entry (bytes intact) is refused by rule 6, independently of the
  // path-grammar cases above (B1/B3: required entries cannot simply disappear).
  const omittedRequired = [
    orig.replace(/^[0-9a-f]{64}  payload\/dist\/src\/commands\/doctor\.js\n/m, ''),
    orig.replace(/^[0-9a-f]{64}  payload\/package\.json\n/m, ''),
    orig.replace(/^[0-9a-f]{64}  bin\/node\n/m, ''),
  ];
  // Structural malformations of rules 2-7, each an obviously-malformed record.
  const structural = [
    `${H}  /etc/passwd\n`,                          // absolute path (rule 3)
    `${H}  ../../../etc/passwd\n`,                   // parent component (rule 4)
    `${H}  x/../y\n`,                                // '..' mid-path component (rule 4)
    `${H}  bin/node\n${H}  bin/node\n`,              // duplicate path (rule 5)
    `${'0'.repeat(63)}  bin/node\n`,                 // wrong digest length (rule 3)
    `${orig}${H}  extra-line`,                       // missing trailing newline (rule 7)
    `${H}\tbin/node\n`,                              // control byte, TAB (rule 2)
  ];
  for (const bad of [...omittedRequired, ...structural]) {
    tamper(sums, bad);
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `record refused: ${JSON.stringify(bad)}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'), `installed-file-altered: ${JSON.stringify(bad)}`);
  }
  tamper(sums, orig); // restore so cleanup sees a valid record

  // B1: the startup-closure cross-check enforces that every startup import stays in
  // the checksum record before Node loads it. Each case starts from the healthy
  // record/snapshot restored above and restores them after.
  // (1) Remove only the admit.js record line, bytes intact. admit.js is in the
  // closure, so the cross-check refuses before Node loads it (no ERR_MODULE_NOT_FOUND).
  tamper(sums, orig.replace(/^[0-9a-f]{64}  payload\/dist\/src\/installation\/admit\.js\n/m, ''));
  {
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `${rr.stdout}${rr.stderr}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'));
    assert.ok(!rr.stderr.includes('ERR_MODULE_NOT_FOUND') && !rr.stderr.includes('Cannot find'),
      `no Node start: ${JSON.stringify(rr.stderr)}`);
  }
  tamper(sums, orig);
  // (2) Remove the whole installation/ directory's record lines and plant a nearer
  // package.json. admit.js and package.js are in the closure, so the cross-check
  // refuses before the metadata scan and before Node reads the package.json.
  const installDir = join(snapshotPath, 'payload/dist/src/installation');
  tamper(sums, orig.replace(/^[0-9a-f]{64}  payload\/dist\/src\/installation\/[^\n]*\n/gm, ''));
  chmodSync(installDir, 0o755);
  writeFileSync(join(installDir, 'package.json'), '{');
  {
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `${rr.stdout}${rr.stderr}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'));
    assert.ok(!rr.stderr.includes('ERR_INVALID_PACKAGE_CONFIG') && !rr.stderr.includes('SyntaxError'),
      `no Node loader crash: ${JSON.stringify(rr.stderr)}`);
  }
  rmSync(join(installDir, 'package.json'));
  tamper(sums, orig);
  // (3) Tamper startup-closure itself: its bytes are a fixed record entry, so the
  // digest check refuses it (installed-file-altered), even with a real snapshot path.
  const closurePath = join(snapshotPath, 'startup-closure');
  const closureOrig = readFileSync(closurePath);
  tamper(closurePath, `${closureOrig.toString('utf8')}payload/dist/src/platform/ownership.js\n`);
  {
    const rr = control(controller, controlRoot, ['status']);
    assert.equal(rr.status, 1, `${rr.stdout}${rr.stderr}`);
    assert.ok(hasDiagnostic(lastJson(rr.stdout), 'installed-file-altered'));
  }
  writeFileSync(closurePath, closureOrig);
  tamper(sums, orig); // final restore for cleanup
});

test('admission.node-identity', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { id, snapshotPath } = await admit(trusted, controlRoot);
  const record = readRecord(controlRoot, id);
  const nodeDigest = createHash('sha256').update(readFileSync(join(snapshotPath, SNAPSHOT_LAYOUT.node))).digest('hex');
  assert.equal(nodeDigest, record.tools.node.sha256);
  const npmDigest = createHash('sha256').update(readFileSync(join(snapshotPath, SNAPSHOT_LAYOUT.npmCli))).digest('hex');
  assert.equal(npmDigest, record.tools.npm.cliSha256);
});

test('admission.runtime-digest-mismatch', async () => {
  const { trusted } = makeTrusted();
  const manifestPath = join(trusted, 'assets/runtime-manifest.json');
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8')) as { platforms: Record<string, { nodeSha256: string }> };
  for (const platform of Object.values(manifest.platforms)) platform.nodeSha256 = '0'.repeat(64);
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  regenerateManifest(trusted);
  await refuses(() => admit(trusted, freshControlRoot()), 'runtime-digest-mismatch');
});

// ---------------------------------------------------------------------------
// Bullet 4
// ---------------------------------------------------------------------------

test('admission.control-root-missing', async () => {
  const { controller } = makeTrusted();
  const cwd = base();
  mkdirSync(join(cwd, 'registry')); // a planted registry in cwd must be ignored
  for (const verb of ['status', 'doctor']) {
    const result = spawnSync('/bin/sh', [controller, verb], { cwd, env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30000 });
    assert.equal(result.status, 1);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'control-root-missing'));
  }
  assert.deepEqual(readdirSync(join(cwd, 'registry')), []);
});

test('admission.nothing-admitted', async () => {
  const controlRoot = freshControlRoot();
  const { controller } = makeTrusted();
  const before = walkFiles(controlRoot);
  for (const verb of ['status', 'doctor']) {
    const result = control(controller, controlRoot, [verb]);
    assert.equal(result.status, 1);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'nothing-admitted'));
  }
  assert.deepEqual(walkFiles(controlRoot), before);
});

test('admission.no-project-root-resolution', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  // Poisoned project: NODE_PATH, a project node_modules and $HOME/.node_modules.
  const poison = base();
  const nodePath = join(poison, 'nodepath');
  mkdirSync(join(nodePath, 'loamprobe'), { recursive: true });
  const marker = join(poison, 'probe-ran');
  writeFileSync(join(nodePath, 'loamprobe', 'index.js'), `require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'ran');module.exports={};`);
  writeFileSync(join(nodePath, 'loamprobe', 'package.json'), '{"name":"loamprobe","version":"1.0.0","main":"index.js"}');
  const projectCwd = join(poison, 'project');
  mkdirSync(join(projectCwd, 'node_modules'), { recursive: true });
  cpSync(join(nodePath, 'loamprobe'), join(projectCwd, 'node_modules/loamprobe'), { recursive: true });
  writeFileSync(join(projectCwd, '.npmrc'), 'registry=https://example.invalid/\n');
  const fakeHome = join(poison, 'home');
  cpSync(join(nodePath), join(fakeHome, '.node_modules'), { recursive: true });
  const env = cleanTestEnvironment({ NODE_PATH: nodePath, HOME: fakeHome });
  // Positive control: NODE_PATH resolves the poison under a bare node.
  const positive = spawnSync(toolchainNode, ['-e', "require('loamprobe')"], { cwd: projectCwd, env: { ...env }, encoding: 'utf8', timeout: 30000 });
  assert.equal(positive.status, 0, positive.stderr);
  assert.ok(existsSync(marker), 'poison must load in the positive control');
  rmSync(marker);
  // The controller doctor from the poisoned cwd loads nothing and proves the
  // no-project-root resolution directly.
  const result = spawnSync('/bin/sh', [controller, '--control-root', controlRoot, 'doctor'], { cwd: projectCwd, env, encoding: 'utf8', timeout: 120000 });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(existsSync(marker), false, 'no project-root or global resolution');
  const report = lastJson(result.stdout) as { resolution: { nodePath: string | null; globalSearchPaths: boolean; execArgv: string[] } };
  assert.equal(report.resolution.nodePath, null);
  assert.equal(report.resolution.globalSearchPaths, false);
  assert.ok(report.resolution.execArgv.includes('--no-global-search-paths'));
});

test('admission.unadmitted-fork', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  // An unchanged checkout matches the admitted release.
  const clean = join(base(), 'checkout');
  copyPayload(trusted, clean);
  writeFileSync(join(clean, 'release-manifest.json'), readFileSync(join(trusted, 'release-manifest.json')));
  const matches = control(controller, controlRoot, ['doctor', '--checkout', clean]);
  assert.equal(matches.status, 0, matches.stderr);
  assert.equal(lastJson(matches.stdout).checkout, 'matches-admitted-release');
  // A consistently changed launcher, program and manifest is an unadmitted fork.
  const fork = join(base(), 'fork');
  copyPayload(trusted, fork);
  writeFileSync(join(fork, 'launcher.mjs'), `${readFileSync(join(fork, 'launcher.mjs'), 'utf8')}\n// fork\n`);
  const program = payloadFiles(fork).find((file) => file.startsWith('dist/') && file.endsWith('.js'))!;
  writeFileSync(join(fork, program), `${readFileSync(join(fork, program), 'utf8')}\n// fork\n`);
  writeFileSync(join(fork, 'release-manifest.json'), `${JSON.stringify(createReleaseManifest(fork), null, 2)}\n`);
  const forked = control(controller, controlRoot, ['doctor', '--checkout', fork]);
  assert.equal(forked.status, 1);
  assert.equal(lastJson(forked.stdout).checkout, 'unadmitted-fork');
});

test('admission.provider-readiness-separate', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  const { id } = await admit(trusted, controlRoot);
  const status = control(controller, controlRoot, ['status']);
  assert.equal(status.status, 0, status.stderr);
  const report = lastJson(status.stdout);
  assert.equal(report.installation, 'admitted');
  assert.equal(report.providerReadiness, 'not-evaluated');
  const record = readRecord(controlRoot, id);
  assert.deepEqual(record.providers.payloads, []);
  assert.ok(record.providers.successor.includes('140'));
});

// ---------------------------------------------------------------------------
// Bullet 5
// ---------------------------------------------------------------------------

test('admission.install-interrupted', async () => {
  // A completed admission provides the material for the completed-runtime rows.
  const seed = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  const { id } = await admit(trusted, seed);
  const controllerPath = controller;

  // Reusable planter: copy the completed control root, mutate it, and read status.
  function planted(mutate: (root: string) => void): { root: string; report: Record<string, unknown> } {
    const root = join(base(), 'planted');
    cpSync(seed, root, { recursive: true });
    forceWritable(root);
    mutate(root);
    const result = control(controllerPath, root, ['status']);
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    return { root, report: lastJson(result.stdout) };
  }
  function assertRow(detail: string, mutate: (root: string) => void): void {
    const before = hashTree(seed);
    const { report } = planted(mutate);
    assert.equal(report.diagnostic, 'install-interrupted');
    assert.ok(String(report.detail).includes(detail), `detail ${String(report.detail)} lacks ${detail}`);
    assertUnchanged(before, hashTree(seed)); // the seed is never touched
  }

  assertRow('lock', (root) => writeFileSync(join(root, CONTROL_ROOT_LAYOUT.lock), '{"pid":1}'));
  assertRow('staging', (root) => mkdirSync(join(root, CONTROL_ROOT_LAYOUT.runtimes, `${CONTROL_ROOT_LAYOUT.stagingPrefix}deadbeefdeadbeef`)));
  assertRow('staging', (root) => mkdirSync(join(root, CONTROL_ROOT_LAYOUT.runtimes, `${CONTROL_ROOT_LAYOUT.toolPrefix}deadbeefdeadbeef`)));
  // A completed runtime missing each of its three registry records in turn.
  assertRow('unregistered', (root) => rmSync(join(root, CONTROL_ROOT_LAYOUT.admissions, `${id}.json`)));
  assertRow('unregistered', (root) => rmSync(join(root, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.sha256`)));
  assertRow('unregistered', (root) => rmSync(join(root, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.json`)));
  // A malformed selection, and one naming a runtime that does not exist.
  assertRow('selection', (root) => writeFileSync(join(root, CONTROL_ROOT_LAYOUT.selected), '{ not json'));
  assertRow('selection', (root) => writeFileSync(join(root, CONTROL_ROOT_LAYOUT.selected), JSON.stringify({ version: 1, snapshotId: 'ffffffffffffffff', admissionId: 'ffffffffffffffff' })));
  // A complete registered runtime with no selection.
  assertRow('unselected', (root) => rmSync(join(root, CONTROL_ROOT_LAYOUT.selected)));

  // A fresh admit into a control root with a leftover lock refuses too.
  const relock = join(base(), 'relock');
  cpSync(seed, relock, { recursive: true });
  forceWritable(relock);
  rmSync(join(relock, CONTROL_ROOT_LAYOUT.selected));
  rmSync(join(relock, CONTROL_ROOT_LAYOUT.runtimes), { recursive: true });
  writeFileSync(join(relock, CONTROL_ROOT_LAYOUT.lock), '{"pid":1}');
  await refuses(() => admit(trusted, relock), 'install-interrupted');
});

test('admission.altered-installed-file', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  const { id, snapshotPath } = await admit(trusted, controlRoot);
  const moduleFile = walkFiles(snapshotPath).find((file) => file.startsWith(`${SNAPSHOT_LAYOUT.modules}/`) && file.endsWith('.json'))!;
  const modulePath = join(snapshotPath, moduleFile);

  // doctor covers the full inventory; the controller pre-dispatch sha256 covers
  // the entrypoint set (snapshot.json included). Both report installed-file-altered.
  function expectAltered(): void {
    const result = control(controller, controlRoot, ['doctor']);
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'installed-file-altered'));
  }

  // Changed byte, then restored.
  const moduleOriginal = readFileSync(modulePath);
  tamper(modulePath, `${moduleOriginal.toString('utf8')} `);
  expectAltered();
  writeFileSync(modulePath, moduleOriginal);

  // Extra file under payload, then removed. tamper() edits an existing sealed
  // file; adding a new one only needs the parent directory made writable.
  const intruder = join(snapshotPath, 'payload/intruder.js');
  chmodSync(join(snapshotPath, 'payload'), 0o755);
  writeFileSync(intruder, 'export {};\n');
  expectAltered();
  rmSync(intruder);

  // Missing file, then restored.
  chmodSync(dirname(modulePath), 0o755);
  rmSync(modulePath);
  expectAltered();
  writeFileSync(modulePath, moduleOriginal);

  // Edited snapshot.json.
  const snapshotJson = join(snapshotPath, SNAPSHOT_LAYOUT.snapshot);
  const snapshotOriginal = readFileSync(snapshotJson);
  tamper(snapshotJson, `${snapshotOriginal.toString('utf8')} `);
  expectAltered();
  writeFileSync(snapshotJson, snapshotOriginal);

  // R2: pre-Node package metadata is caught before dispatch. A malformed
  // payload/package.json would crash Node at bootstrap (ERR_INVALID_PACKAGE_CONFIG)
  // before doctor runs, so only the controller pre-dispatch digest can refuse it;
  // once payload/package.json is in the checksum set it is installed-file-altered.
  const pkgPath = join(snapshotPath, 'payload/package.json');
  const pkgOriginal = readFileSync(pkgPath);
  tamper(pkgPath, '{');
  expectAltered();
  writeFileSync(pkgPath, pkgOriginal);
  // A valid-JSON type change (drop "type") still changes the bytes, so the
  // pre-dispatch digest refuses it too.
  const pkg = JSON.parse(pkgOriginal.toString('utf8')) as Record<string, unknown>;
  delete pkg.type;
  tamper(pkgPath, `${JSON.stringify(pkg, null, 2)}\n`);
  expectAltered();
  writeFileSync(pkgPath, pkgOriginal);

  // R2: malformed / mismatched registry records reach doctor (they are outside
  // the sealed snapshot) and must be a structured install-interrupted, never a
  // raw SyntaxError.
  function expectInterrupted(): void {
    const result = control(controller, controlRoot, ['doctor']);
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'install-interrupted'));
  }
  const admissionRecordPath = join(controlRoot, CONTROL_ROOT_LAYOUT.admissions, `${id}.json`);
  const runtimeRecordPath = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.json`);
  const admissionOriginal = readFileSync(admissionRecordPath);
  const runtimeOriginal = readFileSync(runtimeRecordPath);
  // Malformed admission record.
  tamper(admissionRecordPath, '{ not json');
  expectInterrupted();
  writeFileSync(admissionRecordPath, admissionOriginal);
  // Malformed runtime record.
  tamper(runtimeRecordPath, '{ not json');
  expectInterrupted();
  writeFileSync(runtimeRecordPath, runtimeOriginal);
  // Relationship mismatch: valid JSON runtime record naming a different snapshot.
  const runtime = JSON.parse(runtimeOriginal.toString('utf8')) as Record<string, unknown>;
  runtime.snapshotId = 'ffffffffffffffff';
  tamper(runtimeRecordPath, `${canonicalJson(runtime)}\n`);
  expectInterrupted();
  writeFileSync(runtimeRecordPath, runtimeOriginal);
  // Valid-JSON admission record of the wrong shape: an empty release file map with
  // empty release/tools objects must NOT certify as healthy (B2). Before the shape
  // check the release-binding loop was vacuous and the report was healthy; now the
  // dispatched doctor reports a structured install-interrupted.
  tamper(admissionRecordPath, `${canonicalJson({ version: 1, id, files: {}, release: {}, tools: {} })}\n`);
  expectInterrupted();
  writeFileSync(admissionRecordPath, admissionOriginal);

  // B2: complete admission-record shape and internal-consistency relationships.
  // Each is an isolated single-field corruption of the otherwise-healthy record;
  // the dispatched doctor must report install-interrupted (never heal), one failure
  // never masking another. Restored after each.
  function tamperAdmission(mutate: (rec: AdmissionRecord) => void): void {
    const rec = JSON.parse(admissionOriginal.toString('utf8')) as AdmissionRecord;
    mutate(rec);
    tamper(admissionRecordPath, `${canonicalJson(rec)}\n`);
    expectInterrupted();
    writeFileSync(admissionRecordPath, admissionOriginal);
  }
  // Missing required fields.
  tamperAdmission((rec) => { delete (rec as { admittedAt?: string }).admittedAt; });
  tamperAdmission((rec) => { delete (rec.tools.node as { version?: string }).version; });
  tamperAdmission((rec) => { delete (rec as { protectedPaths?: unknown }).protectedPaths; });
  // False identity digests: shape is valid (hex64) but they no longer match the
  // installed inventory or the recorded release map.
  tamperAdmission((rec) => { rec.tools.node.sha256 = '0'.repeat(64); });
  tamperAdmission((rec) => { rec.release.manifestSha256 = '0'.repeat(64); });
  // Truncated release map: the release loop passes vacuously, the completeness
  // relationship does not.
  tamperAdmission((rec) => {
    const [firstKey] = Object.keys(rec.files);
    rec.files = { [firstKey]: rec.files[firstKey]! };
  });
  // Aggregate release digests: each hex64 but no longer matching the byte-verified
  // installed release manifest.
  tamperAdmission((rec) => { rec.release.sourceDigest = '0'.repeat(64); });
  tamperAdmission((rec) => { rec.release.outputDigest = '0'.repeat(64); });
  tamperAdmission((rec) => { rec.release.dependencyDigest = '0'.repeat(64); });
  // Tool metadata: each valid-typed but no longer matching this running admitted
  // executable (platform/arch/node) or the installed npm package.json (npm version).
  tamperAdmission((rec) => { rec.tools.platform = 'wrong'; });
  tamperAdmission((rec) => { rec.tools.arch = 'wrong'; });
  tamperAdmission((rec) => { rec.tools.node.version = 'wrong'; });
  tamperAdmission((rec) => { rec.tools.node.sqlite = 'wrong'; });
  tamperAdmission((rec) => { rec.tools.npm.version = 'wrong'; });
  // Record-only per-file digest mismatch with the payload bytes intact: the file-map
  // relationship refuses it as an inconsistent registry record BEFORE the payload
  // byte re-hash, so it is install-interrupted, not build-altered-release.
  tamperAdmission((rec) => { rec.files['package.json'] = '0'.repeat(64); });

  // Deterministic ID relationship: a registry whose selection points the snapshot
  // id at an admission record whose recorded inputs derive a different id is an
  // inconsistent registry (install-interrupted). This is the smallest such state
  // that passes every earlier field check: a copy of the healthy admission record
  // under a second, wrong id, with the selection and runtime record's admissionId
  // repointed at it. Its release and tools still match the installed snapshot, so
  // only the id relationship is violated (computeId derives the true id, which
  // differs from the record id and the selected snapshot id). Restored after.
  const selectedPath = join(controlRoot, CONTROL_ROOT_LAYOUT.selected);
  const selectedOriginal = readFileSync(selectedPath);
  const wrongId = (id[0] === '0' ? '1' : '0') + id.slice(1);
  const forkedAdmissionPath = join(controlRoot, CONTROL_ROOT_LAYOUT.admissions, `${wrongId}.json`);
  const forked = JSON.parse(admissionOriginal.toString('utf8')) as AdmissionRecord;
  forked.id = wrongId;
  chmodSync(dirname(forkedAdmissionPath), 0o755);
  writeFileSync(forkedAdmissionPath, `${canonicalJson(forked)}\n`);
  const idRuntime = JSON.parse(runtimeOriginal.toString('utf8')) as Record<string, unknown>;
  idRuntime.admissionId = wrongId;
  tamper(runtimeRecordPath, `${canonicalJson(idRuntime)}\n`);
  tamper(selectedPath, `${canonicalJson({ version: 1, snapshotId: id, admissionId: wrongId })}\n`);
  expectInterrupted();
  rmSync(forkedAdmissionPath);
  writeFileSync(runtimeRecordPath, runtimeOriginal);
  writeFileSync(selectedPath, selectedOriginal);

  // N1: the sealed installed-files.json is normally gated by the controller's
  // pre-dispatch checksum, so reach doctor directly (through the snapshot's own
  // node, as environment-injected does) to prove doctor reads and parses it
  // defensively: missing, non-regular, and hash-consistent malformed each yield a
  // single installed-file-altered JSON line and exit 1, never a stack trace.
  const snapshotNode = join(snapshotPath, SNAPSHOT_LAYOUT.node);
  const doctorJs = join(snapshotPath, SNAPSHOT_LAYOUT.doctor);
  const installedFilesPath = join(snapshotPath, SNAPSHOT_LAYOUT.installedFiles);
  const installedFilesOriginal = readFileSync(installedFilesPath);
  // The controller dispatches doctor under a minimal env (HOME/PATH/TMPDIR/LANG
  // only); mirror it so no stripped-class variable trips environment-injected
  // before the installed-file-altered classification we are exercising.
  const directEnv = { HOME: process.env.HOME ?? '/tmp', PATH: dirname(snapshotNode), TMPDIR: process.env.TMPDIR ?? '/tmp', LANG: 'C' };
  function expectAlteredDirect(): void {
    const result = spawnSync(snapshotNode, [doctorJs, '--mode', 'doctor', '--control-root', controlRoot],
      { env: directEnv, encoding: 'utf8', timeout: 60000 });
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'installed-file-altered'), `installed-file-altered: ${result.stdout}`);
    assert.ok(!/\n\s+at /.test(result.stderr) && !result.stderr.includes('SyntaxError')
      && !result.stderr.includes('ENOENT') && !result.stderr.includes('EISDIR'),
      `no stack trace on stderr: ${JSON.stringify(result.stderr)}`);
  }
  // (i) removed.
  chmodSync(snapshotPath, 0o755);
  chmodSync(installedFilesPath, 0o644);
  rmSync(installedFilesPath);
  expectAlteredDirect();
  writeFileSync(installedFilesPath, installedFilesOriginal);
  // (ii) replaced by a directory.
  rmSync(installedFilesPath);
  mkdirSync(installedFilesPath);
  expectAlteredDirect();
  rmSync(installedFilesPath, { recursive: true });
  writeFileSync(installedFilesPath, installedFilesOriginal);
  // (iii) hash-consistent bytes of the wrong shape: rewrite the runtime record's
  // installedFilesSha256 to the new file's digest so the digest check passes and
  // only the structural/parse check can refuse. Non-JSON bytes and valid JSON of
  // the wrong shape (null, {}, a null files map) must each be installed-file-altered
  // with no stack trace (B2), never a raw TypeError from Object.keys.
  function expectInventoryShapeAltered(bytes: string): void {
    const buf = Buffer.from(bytes);
    writeFileSync(installedFilesPath, buf);
    const rt = JSON.parse(runtimeOriginal.toString('utf8')) as Record<string, unknown>;
    rt.installedFilesSha256 = createHash('sha256').update(buf).digest('hex');
    tamper(runtimeRecordPath, `${canonicalJson(rt)}\n`);
    expectAlteredDirect();
    writeFileSync(runtimeRecordPath, runtimeOriginal);
    writeFileSync(installedFilesPath, installedFilesOriginal);
  }
  expectInventoryShapeAltered('this-is-not-json');
  expectInventoryShapeAltered('null');
  expectInventoryShapeAltered('{}');
  expectInventoryShapeAltered('{"version":1,"files":null}');

  // B4: mode-only changes from a healthy snapshot must be structured diagnostics,
  // not raw exec/read failures. Restore the mode after each.
  // (a) A non-executable selected Node passes the pre-dispatch byte digest but
  // would fail at exec with 126/Permission denied; the controller refuses it
  // before dispatch with installed-file-altered.
  const nodePath = join(snapshotPath, SNAPSHOT_LAYOUT.node);
  const nodeMode = lstatSync(nodePath).mode & 0o777;
  chmodSync(dirname(nodePath), 0o755);
  chmodSync(nodePath, 0o444);
  {
    const result = control(controller, controlRoot, ['doctor']);
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'installed-file-altered'));
    assert.ok(!result.stderr.includes('Permission denied'), `no exec permission failure: ${JSON.stringify(result.stderr)}`);
  }
  chmodSync(nodePath, nodeMode);

  // (b) An installed dependency file that cannot be read (mode 000) is not in the
  // controller's pre-dispatch checksum set, so the dispatched doctor reaches it in
  // the installed inventory; the EACCES becomes installed-file-altered, never an
  // uncaught exception with a stack trace.
  chmodSync(dirname(modulePath), 0o755);
  chmodSync(modulePath, 0o000);
  {
    const result = control(controller, controlRoot, ['doctor']);
    assert.equal(result.status, 1, `${result.stdout}${result.stderr}`);
    assert.ok(hasDiagnostic(lastJson(result.stdout), 'installed-file-altered'));
    assert.ok(!/\n\s+at /.test(result.stderr) && !result.stderr.includes('EACCES'),
      `no stack trace on stderr: ${JSON.stringify(result.stderr)}`);
  }
  chmodSync(modulePath, 0o644);
});

test('admission.environment-injected', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { snapshotPath } = await admit(trusted, controlRoot);
  const doctorJs = join(snapshotPath, SNAPSHOT_LAYOUT.doctor);
  const snapshotNode = join(snapshotPath, SNAPSHOT_LAYOUT.node);
  const result = spawnSync(snapshotNode, [doctorJs, '--mode', 'doctor', '--control-root', controlRoot], {
    env: cleanTestEnvironment({ NODE_PATH: '/nonexistent' }), encoding: 'utf8', timeout: 60000,
  });
  assert.equal(result.status, 1);
  const report = lastJson(result.stdout) as { diagnostics: { code: string }[] };
  assert.ok(report.diagnostics.some((entry) => entry.code === 'environment-injected'));
});

test('admission.not-admitted-runtime', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { snapshotPath } = await admit(trusted, controlRoot);
  const doctorJs = join(snapshotPath, SNAPSHOT_LAYOUT.doctor);
  // The toolchain node is not the admitted node.
  const result = spawnSync(toolchainNode, [doctorJs, '--mode', 'doctor', '--control-root', controlRoot], {
    env: cleanTestEnvironment(), encoding: 'utf8', timeout: 60000,
  });
  assert.equal(result.status, 1);
  const report = lastJson(result.stdout) as { diagnostics: { code: string }[] };
  assert.ok(report.diagnostics.some((entry) => entry.code === 'not-admitted-runtime'));
});

test('admission.ancestor-package-collision', async () => {
  const { trusted } = makeTrusted();
  // A control root beneath a directory holding package.json.
  const ancestor = join(base(), 'ancestor');
  mkdirSync(ancestor, { recursive: true });
  writeFileSync(join(ancestor, 'package.json'), '{"name":"ancestor"}\n');
  const controlRoot = join(ancestor, 'nested/control');
  mkdirSync(controlRoot, { recursive: true });
  const before = walkFiles(controlRoot);
  await refuses(() => admit(trusted, controlRoot), 'ancestor-package-collision');
  assert.deepEqual(walkFiles(controlRoot), before);

  // A control root beneath a directory holding node_modules.
  const ancestor2 = join(base(), 'ancestor2');
  mkdirSync(join(ancestor2, 'node_modules'), { recursive: true });
  const controlRoot2 = join(ancestor2, 'nested/control');
  mkdirSync(controlRoot2, { recursive: true });
  await refuses(() => admit(trusted, controlRoot2), 'ancestor-package-collision');
});

test('admission.selection-retained', async () => {
  const controlRoot = freshControlRoot();
  const first = makeTrusted();
  await admit(first.trusted, controlRoot);
  const before = hashTree(controlRoot);
  // A second, different trusted source is refused; nothing changes.
  const second = makeTrusted();
  await refuses(() => admit(second.trusted, controlRoot), 'selection-exists');
  assertUnchanged(before, hashTree(controlRoot));

  // Under a manually planted lock, admit refuses without writing.
  writeFileSync(join(controlRoot, CONTROL_ROOT_LAYOUT.lock), '{"pid":1}');
  const lockedBefore = hashTree(controlRoot);
  await refuses(() => admit(first.trusted, controlRoot), 'install-interrupted');
  assertUnchanged(lockedBefore, hashTree(controlRoot));
  rmSync(join(controlRoot, CONTROL_ROOT_LAYOUT.lock));

  // A first admission stopped after seal, then a second admit, sees staging: the
  // recheck happens under the lock and never publishes a second runtime.
  const fresh = freshControlRoot();
  const runner = admitChildRunner(base());
  const sealed = runChildAdmit(runner, admitOptions(first.trusted, fresh, { faultAfter: 'seal' }));
  assert.equal(sealed.status, 70, `${sealed.stdout}${sealed.stderr}`);
  rmSync(join(fresh, CONTROL_ROOT_LAYOUT.lock)); // fixture-only: clear the crash lock
  await refuses(() => admit(first.trusted, fresh), 'install-interrupted');

  // Late contender: a live admission A holds its lock and pauses just before
  // selection; a contender B against the SAME control root refuses under A's lock
  // and leaves A untouched; A resumes and selects; a third admission C refuses
  // because a selection now exists.
  const race = freshControlRoot();
  const rendezvous = join(base(), 'rendezvous', 'pause');
  mkdirSync(dirname(rendezvous), { recursive: true });
  const raceRunner = admitChildRunner(base());
  const a = spawn(toolchainNode, [raceRunner, JSON.stringify(admitOptions(first.trusted, race, { pauseBeforeSelect: rendezvous }))],
    { env: cleanTestEnvironment() });
  const aDone = new Promise<number>((resolve) => a.on('exit', (code) => resolve(code ?? -1)));

  const raceDeadline = Date.now() + 60000;
  while (!existsSync(`${rendezvous}.ready`)) {
    if (Date.now() > raceDeadline) { a.kill(); throw new Error('admission A never reached the pause'); }
    await new Promise((r) => setTimeout(r, 25));
  }
  // A holds the lock, sealed and registered, but has not selected.
  assert.equal(existsSync(join(race, CONTROL_ROOT_LAYOUT.lock)), true);
  assert.equal(existsSync(join(race, CONTROL_ROOT_LAYOUT.selected)), false);
  const pausedRegistry = hashTree(join(race, CONTROL_ROOT_LAYOUT.registry));

  // Contender B: same control root, own lock attempt refuses; A's state untouched.
  const second2 = makeTrusted();
  await refuses(() => admit(second2.trusted, race), 'install-interrupted');
  assertUnchanged(pausedRegistry, hashTree(join(race, CONTROL_ROOT_LAYOUT.registry)));
  assert.equal(existsSync(join(race, CONTROL_ROOT_LAYOUT.selected)), false);

  // Resume A; it selects and exits 0.
  writeFileSync(`${rendezvous}.go`, '');
  assert.equal(await aDone, 0, 'admission A must complete after resume');
  const selected = JSON.parse(readFileSync(join(race, CONTROL_ROOT_LAYOUT.selected), 'utf8')) as { snapshotId: string };
  assert.match(selected.snapshotId, /^[0-9a-f]{16}$/);
  assert.equal(existsSync(join(race, CONTROL_ROOT_LAYOUT.lock)), false);

  // Contender C: a selection now exists -> selection-exists, nothing changes.
  const afterSelect = hashTree(race);
  const third = makeTrusted();
  await refuses(() => admit(third.trusted, race), 'selection-exists');
  assertUnchanged(afterSelect, hashTree(race));

  // A malformed selected.json blocks a NEW admission with unchanged prior state.
  const malformed = freshControlRoot();
  const seedTrusted = makeTrusted();
  await admit(seedTrusted.trusted, malformed);           // a complete, selected runtime
  tamper(join(malformed, CONTROL_ROOT_LAYOUT.selected), '{ not json');
  const beforeMalformed = hashTree(malformed);
  await refuses(() => admit(seedTrusted.trusted, malformed), 'install-interrupted');
  assertUnchanged(beforeMalformed, hashTree(malformed));  // the transient lock is created and removed; net unchanged
});

test('admission.snapshot-link-counts', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();
  const { snapshotPath } = await admit(trusted, controlRoot);
  for (const file of walkFiles(snapshotPath)) {
    const stat = lstatSync(join(snapshotPath, file));
    assert.equal(stat.isSymbolicLink(), false, `symlink at ${file}`);
    assert.equal(stat.nlink, 1, `nlink ${stat.nlink} at ${file}`);
  }
});

test('admission.snapshot-runs-without-checkout', async () => {
  const controlRoot = freshControlRoot();
  const { trusted } = makeTrusted();

  // A disposable toolchain copy so renaming it away cannot destroy the shared
  // toolchain the test runner itself uses.
  const dispToolchain = join(base(), 'toolchain');
  mkdirSync(join(dispToolchain, 'bin'), { recursive: true });
  cpSync(join(toolchain, 'bin/node'), join(dispToolchain, 'bin/node'));
  chmodSync(join(dispToolchain, 'bin/node'), 0o555);
  cpSync(join(toolchain, 'lib/node_modules/npm'), join(dispToolchain, 'lib/node_modules/npm'), { recursive: true });

  // Admit in a child run BY the disposable toolchain's node, so admitTools'
  // running-executable identity check binds to the disposable copy.
  const runner = admitChildRunner(base());
  const options: AdmitOptions = { trustedSource: trusted, controlRoot, toolchain: dispToolchain, releaseIdentity: 'loam v0.0.0', test: { originPolicy: 'file' } };
  const result = spawnSync(join(dispToolchain, 'bin/node'), [runner, JSON.stringify(options)], { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120000 });
  assert.equal(result.status, 0, `${result.stdout}${result.stderr}`);
  assert.ok(result.stdout.startsWith('OK:'), result.stdout);

  // Rename away every external name the snapshot might have fallen back to.
  renameSync(trusted, `${trusted}.gone`);
  renameSync(dispToolchain, `${dispToolchain}.gone`);

  const installedController = join(controlRoot, CONTROL_ROOT_LAYOUT.controller);
  const doctor = control(installedController, controlRoot, ['doctor']);
  assert.equal(doctor.status, 0, doctor.stderr);
  assert.equal(lastJson(doctor.stdout).status, 'healthy');
});

test('admission.ordinary-commands-unchanged', async () => {
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  await admit(trusted, controlRoot);
  const before = hashTree(controlRoot);
  assert.equal(control(controller, controlRoot, ['status']).status, 0);
  assert.equal(control(controller, controlRoot, ['doctor']).status, 0);
  // A distinct checkout running the non-admission package gate.
  const checkout = join(base(), 'checkout');
  copyPayload(trusted, checkout);
  const qualify = spawnSync(toolchainNode, [join(checkout, 'launcher.mjs'), 'qualify', 'package'], { cwd: checkout, env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120000 });
  assert.equal(qualify.error, undefined, String(qualify.error));
  assert.equal(qualify.status, 0, qualify.stderr);
  assert.equal(qualify.signal, null, `killed by ${qualify.signal}`);
  assertUnchanged(before, hashTree(controlRoot));
});

// A planted symlink or unexpected file at a mkdir/temp/rename target must never
// be followed or overwritten. This reproduces the four finished-work probes:
// the atomic writers' temp path, the copied controller, the seal targets, and a
// duplicate-key selection (the Node and sh parsers must agree).
test('admission.preexisting-path-refused', async () => {
  const HEX = 'a'.repeat(16);

  // 1. The atomic writers create their temp on a fresh random name with an
  // exclusive open, so a symlink planted at the fixed ".<name>.tmp" is ignored
  // and the outside target it points at is never written.
  for (const kind of ['canonical', 'text'] as const) {
    const dir = join(base(), 'writer');
    mkdirSync(dir, { recursive: true });
    const sentinel = join(dir, '..', 'sentinel');
    writeFileSync(sentinel, 'DO NOT CHANGE');
    symlinkSync(sentinel, join(dir, '.record.tmp'));
    const expected = kind === 'canonical' ? `${canonicalJson({ changed: true })}\n` : 'changed';
    if (kind === 'canonical') writeCanonicalAtomic(dir, 'record', { changed: true });
    else writeTextAtomic(dir, 'record', 'changed');
    assert.equal(readFileSync(sentinel, 'utf8'), 'DO NOT CHANGE', `${kind}: sentinel unchanged`);
    assert.equal(lstatSync(join(dir, 'record')).isSymbolicLink(), false, `${kind}: record is a real file`);
    assert.equal(readFileSync(join(dir, 'record'), 'utf8'), expected, `${kind}: record content`);
  }

  // 2. A pre-existing controller at the copy target, a plain file or a symlink,
  // is refused and never overwritten.
  const { trusted: controllerSource } = makeTrusted();
  for (const variant of ['file', 'symlink'] as const) {
    const root = freshControlRoot();
    const controllerPath = join(root, CONTROL_ROOT_LAYOUT.controller);
    const sentinel = join(root, '..', 'controller-sentinel');
    writeFileSync(sentinel, 'DO NOT CHANGE');
    if (variant === 'file') writeFileSync(controllerPath, 'PREEXISTING CONTROLLER');
    else symlinkSync(sentinel, controllerPath);
    assert.throws(
      () => installController(controllerSource, root),
      (error: unknown) => error instanceof AdmissionError && error.diagnostic === 'install-interrupted'
        && error.message === `unexpected ${controllerPath}`,
      `${variant}: refused`,
    );
    assert.equal(readFileSync(sentinel, 'utf8'), 'DO NOT CHANGE', `${variant}: sentinel unchanged`);
    if (variant === 'file') assert.equal(readFileSync(controllerPath, 'utf8'), 'PREEXISTING CONTROLLER', 'controller not overwritten');
  }

  // 3. The seal refuses a symlink at any seal target before writing anything
  // into the workspace, so a planted link cannot redirect a seal write outside.
  for (const target of ['installed-files.json', 'snapshot.json', 'bin'] as const) {
    const dir = base();
    const workspace = join(dir, 'workspace');
    const runtimeDir = join(dir, 'runtime');
    const source = join(dir, 'source');
    const outside = join(dir, 'protected');
    for (const p of [join(workspace, 'payload'), join(runtimeDir, 'bin'), join(runtimeDir, 'lib'), join(source, 'scripts'), outside]) mkdirSync(p, { recursive: true });
    writeFileSync(join(runtimeDir, 'bin/node'), 'verified-node');
    writeFileSync(join(source, 'scripts/loam-control.sh'), 'verified-controller');
    const sentinel = join(outside, target === 'bin' ? 'node' : 'sentinel');
    writeFileSync(sentinel, 'DO NOT CHANGE');
    symlinkSync(target === 'bin' ? outside : sentinel, join(workspace, target));
    assert.throws(
      () => sealSnapshot({ workspace, runtimeDir }, source, HEX),
      (error: unknown) => error instanceof AdmissionError && error.diagnostic === 'install-interrupted'
        && error.message === `unexpected ${join(workspace, target)}`,
      `seal ${target}: refused`,
    );
    assert.equal(readFileSync(sentinel, 'utf8'), 'DO NOT CHANGE', `seal ${target}: outside unchanged`);
  }

  // 4. A duplicate "version" key in selected.json is refused by the Node parser
  // exactly as the POSIX controller's line-exact grammar refuses it: both report
  // install-interrupted (selection), and the control root carries no symlink.
  const controlRoot = freshControlRoot();
  const { trusted, controller } = makeTrusted();
  const { id } = await admit(trusted, controlRoot);
  tamper(join(controlRoot, CONTROL_ROOT_LAYOUT.selected), `{\n  "admissionId": "${id}",\n  "snapshotId": "${id}",\n  "version": 1,\n  "version": 1\n}\n`);
  const nodeState = controlRootState(controlRoot);
  assert.equal(nodeState.kind, 'diagnostic', 'Node refuses the duplicate-key selection');
  assert.ok(nodeState.kind === 'diagnostic' && nodeState.diagnostic === 'install-interrupted' && nodeState.detail === 'selection');
  const shell = control(controller, controlRoot, ['status']);
  assert.equal(shell.status, 1, `${shell.stdout}${shell.stderr}`);
  const shReport = lastJson(shell.stdout);
  assert.equal(shReport.diagnostic, 'install-interrupted');
  assert.equal(shReport.detail, 'selection');
  assert.equal(anySymlink(controlRoot), false, 'no symlink in the control root');
});
