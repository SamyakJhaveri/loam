// CORE-04 runtime admission.
//
// admitRuntime() takes an operator-reviewed trusted source and an operator
// toolchain and produces a sealed, selected runtime snapshot under a control
// root, fetching and (where declared) building dependencies under the CORE-02
// boundary. Every refusal is an AdmissionError carrying a frozen diagnostic. The
// controller (scripts/loam-control.sh) runs this file's CLI as the toolchain
// Node; the offline fixtures call admitRuntime() directly through the test seam.
//
// Precedence: plan-03 and the Codex implementation conditions C1-C5 over the
// inherited plan-02 text. This module imports only node: builtins and relative
// .js payload sources, so it satisfies the import-closure rule.
import { createHash } from 'node:crypto';
import { chmodSync, closeSync, cpSync, existsSync, lstatSync, mkdirSync, openSync, readdirSync, readFileSync, realpathSync, renameSync, rmSync, statSync, writeFileSync, writeSync, } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, isAbsolute, join, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { AdmissionError, CONTROL_ROOT_LAYOUT, FETCH_PASSTHROUGH_ENVIRONMENT, FIXTURE_ORIGIN_PREFIX, GENERATED_TREE, NATIVE_PREREQUISITES, NO_GLOBAL_SEARCH_PATHS, REGISTRY_ORIGIN, STAGING_TRANSIENT, canonicalJson, } from '../contracts/installation.js';
import { qualifyRuntime } from '../platform/runtime.js';
import { boundaryAvailability, containedCommand, PROTECTED_KINDS } from '../platform/native-boundary.js';
import { snapshot as payloadSnapshot, verifyPackage } from './package.js';
const PROTECTED_HOMES = PROTECTED_KINDS;
const OVERRIDABLE_HOMES = ['state', 'locks', 'credentials', 'sockets', 'callbacks'];
const LINUX_TOOL_ROOTS = ['/usr', '/lib', '/lib64', '/bin', '/sbin'];
const NPM_TIMEOUT = 120000;
const HEX16 = /^[0-9a-f]{16}$/;
// ---- small helpers -------------------------------------------------------
function sha256(data) { return createHash('sha256').update(data).digest('hex'); }
function sha256File(path) { return sha256(readFileSync(path)); }
function readJson(path) { return JSON.parse(readFileSync(path, 'utf8')); }
function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
}
function writeCanonical(path, value) { writeFileSync(path, `${canonicalJson(value)}\n`); }
function writeCanonicalAtomic(dir, name, value) {
    const finalPath = join(dir, name);
    const tempPath = join(dir, `.${name}.tmp`);
    ensureNoSymlink(finalPath);
    writeFileSync(tempPath, `${canonicalJson(value)}\n`);
    renameSync(tempPath, finalPath);
}
function ensureNoSymlink(path) {
    let stat;
    try {
        stat = lstatSync(path);
    }
    catch {
        return;
    }
    if (stat.isSymbolicLink())
        throw new AdmissionError('install-interrupted', `unexpected ${path}`);
}
function requireAbsent(path) {
    if (existsSync(path) || isSymlink(path))
        throw new AdmissionError('install-interrupted', `unexpected ${path}`);
}
function isSymlink(path) {
    try {
        return lstatSync(path).isSymbolicLink();
    }
    catch {
        return false;
    }
}
function realpathOr(path) { try {
    return realpathSync(path);
}
catch {
    return path;
} }
// Recursively copy a tree of regular files and directories, refusing any symlink
// or hard-linked file, so the copied Node/npm tree carries no aliases.
function copyRegularTree(source, destination) {
    const stat = lstatSync(source);
    if (stat.isSymbolicLink())
        throw new AdmissionError('runtime-digest-mismatch', `symlink in toolchain tree: ${source}`);
    if (stat.isDirectory()) {
        mkdirSync(destination, { recursive: true });
        for (const name of readdirSync(source).sort())
            copyRegularTree(join(source, name), join(destination, name));
        return;
    }
    if (!stat.isFile())
        throw new AdmissionError('runtime-digest-mismatch', `non-regular entry in toolchain tree: ${source}`);
    if (stat.nlink !== 1)
        throw new AdmissionError('runtime-digest-mismatch', `hard-linked toolchain entry: ${source}`);
    cpSync(source, destination);
    chmodSync(destination, stat.mode & 0o111 ? 0o555 : 0o444);
}
function chmodTreeReadOnly(root) {
    const stat = lstatSync(root);
    if (stat.isDirectory()) {
        for (const name of readdirSync(root))
            chmodTreeReadOnly(join(root, name));
        chmodSync(root, 0o555);
        return;
    }
    chmodSync(root, stat.mode & 0o111 ? 0o555 : 0o444);
}
// ---- trusted-source shape and ancestor guards ----------------------------
function resolveTrustedSource(trustedSource, controlRoot) {
    if (!isAbsolute(trustedSource))
        throw new AdmissionError('trusted-source-shape', 'trusted source must be an absolute path');
    let source;
    try {
        source = realpathSync(trustedSource);
    }
    catch {
        throw new AdmissionError('trusted-source-shape', `trusted source does not resolve: ${trustedSource}`);
    }
    if (!source.split(sep).slice(-3).join('/').endsWith('seed/.loam/factory')) {
        throw new AdmissionError('trusted-source-shape', 'trusted source realpath must end with seed/.loam/factory');
    }
    const repoRoot = dirname(dirname(dirname(source)));
    for (const sentinel of ['copier.yml', 'VERSION', 'bin/release.sh']) {
        if (!existsSync(join(repoRoot, sentinel)))
            throw new AdmissionError('trusted-source-shape', `trusted repository root missing ${sentinel}`);
    }
    if (existsSync(join(repoRoot, '.loam/factory')))
        throw new AdmissionError('trusted-source-shape', 'trusted repository root looks like a rendered candidate');
    const control = realpathOr(controlRoot);
    if (contains(source, control) || contains(control, source))
        throw new AdmissionError('trusted-source-shape', 'trusted source and control root overlap');
    return { source, repoRoot };
}
function contains(parent, child) {
    const rel = relative(parent, child);
    return rel === '' || (!isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`));
}
function assertNoAncestorPackages(controlRoot) {
    let dir = dirname(realpathOr(controlRoot));
    let previous = '';
    while (dir !== previous) {
        for (const marker of ['package.json', 'node_modules', '.npmrc']) {
            if (existsSync(join(dir, marker)))
                throw new AdmissionError('ancestor-package-collision', `${marker} in control-root ancestor ${dir}`);
        }
        previous = dir;
        dir = dirname(dir);
    }
}
// ---- runtime and release identity ----------------------------------------
function admitTools(toolchain, trustedSource) {
    const nodeSource = join(toolchain, 'bin/node');
    const npmCli = join(toolchain, 'lib/node_modules/npm/bin/npm-cli.js');
    const npmPackageJson = join(toolchain, 'lib/node_modules/npm/package.json');
    if (realpathOr(process.execPath) !== realpathOr(nodeSource)) {
        throw new AdmissionError('runtime-digest-mismatch', 'admission is not running as the toolchain node');
    }
    const manifestPath = join(trustedSource, 'assets/runtime-manifest.json');
    const qualified = qualifyRuntime(manifestPath, { requireDigest: true });
    if (qualified.status !== 'qualified')
        throw new AdmissionError('runtime-digest-mismatch', qualified.reasons.join('; '));
    const versionProbe = spawnSync(nodeSource, ['--no-global-search-paths', npmCli, '--version'], { encoding: 'utf8', timeout: 30000 });
    const npmVersion = (versionProbe.stdout || '').trim();
    if (versionProbe.status !== 0 || npmVersion !== '11.19.0')
        throw new AdmissionError('runtime-digest-mismatch', `admitted npm must be 11.19.0, saw ${npmVersion || 'none'}`);
    const manifest = readJson(manifestPath);
    return {
        platform: process.platform,
        arch: process.arch,
        node: { version: process.version, sqlite: manifest.sqlite, sha256: qualified.execSha256, sourcePath: nodeSource },
        npm: { version: npmVersion, cliSha256: sha256File(npmCli), packageSha256: sha256File(npmPackageJson), sourcePath: npmCli },
    };
}
function gitDescribe(repoRoot) {
    const probe = spawnSync('git', ['-C', repoRoot, 'describe', '--tags', '--always'], { encoding: 'utf8', timeout: 10000 });
    if (probe.status === 0 && probe.stdout && probe.stdout.trim())
        return probe.stdout.trim();
    return null;
}
function readReleaseIdentity(source, repoRoot, label) {
    let verified;
    try {
        verified = verifyPackage(source);
    }
    catch (error) {
        throw new AdmissionError('wrong-release-digest', error instanceof Error ? error.message : String(error));
    }
    const manifestPath = join(source, 'release-manifest.json');
    const manifest = readJson(manifestPath);
    const files = { ...manifest.files, 'release-manifest.json': sha256File(manifestPath) };
    const identity = {
        label,
        sourcePath: source,
        gitDescribe: gitDescribe(repoRoot),
        sourceDigest: verified.sourceDigest,
        outputDigest: verified.outputDigest,
        dependencyDigest: verified.dependencyDigest,
        manifestSha256: sha256File(manifestPath),
    };
    return { identity, files };
}
function computeId(identity, tools) {
    const material = [identity.sourceDigest, identity.outputDigest, identity.dependencyDigest, tools.node.sha256, `${tools.platform}-${tools.arch}`].join('|');
    return sha256(material).slice(0, 16);
}
function dependencyName(key) {
    const marker = 'node_modules/';
    const at = key.lastIndexOf(marker);
    return at < 0 ? key : key.slice(at + marker.length);
}
function lockDependencies(source) {
    const lock = readJson(join(source, 'package-lock.json'));
    const out = [];
    for (const [key, entry] of Object.entries(lock.packages ?? {})) {
        if (key === '')
            continue; // the root project entry is exempt (item 7)
        out.push({ key, name: dependencyName(key), entry });
    }
    return out;
}
function assertLockOrigins(deps, filePolicy) {
    for (const { name, entry } of deps) {
        if (!entry.integrity)
            throw new AdmissionError('lock-origin-refused', `${name} has no integrity`);
        if (filePolicy) {
            const expected = `${FIXTURE_ORIGIN_PREFIX}${name}-${entry.version}.tgz`;
            if (entry.resolved !== expected)
                throw new AdmissionError('lock-origin-refused', `${name} resolved ${entry.resolved} is not the admitted fixture origin`);
        }
        else if (!entry.resolved || !entry.resolved.startsWith(REGISTRY_ORIGIN)) {
            throw new AdmissionError('lock-origin-refused', `${name} resolved ${entry.resolved} is not the npm registry`);
        }
    }
}
function assertScriptsAllowed(deps, allowScripts) {
    for (const { name, entry } of deps) {
        if (!entry.hasInstallScript)
            continue;
        const byName = allowScripts[name] === true;
        const byPin = allowScripts[`${name}@${entry.version}`] === true;
        if (!byName && !byPin)
            throw new AdmissionError('build-script-refused', `${name}@${entry.version} runs install scripts but is not covered by allowScripts`);
    }
}
// ---- fetch and build -----------------------------------------------------
export function trustedSpawnEnvironment(phase, base) {
    const env = { HOME: base.home, PATH: base.path, TMPDIR: base.tmpdir, LANG: process.env.LANG ?? 'C' };
    if (phase === 'fetch') {
        for (const name of FETCH_PASSTHROUGH_ENVIRONMENT) {
            const value = process.env[name];
            if (value !== undefined && value !== '')
                env[name] = value;
        }
    }
    return env;
}
function fetchFlags(ws, filePolicy) {
    const flags = [
        '--prefix', ws.payloadReal,
        '--userconfig', ws.npmUser, '--globalconfig', ws.npmGlobal,
        '--cache', ws.npmCache, '--logs-dir', join(ws.npmCache, '_logs'),
        '--no-audit', '--no-fund', '--no-update-notifier', '--ignore-scripts',
        '--install-links', '--no-bin-links',
        '--allow-git=none', '--allow-remote=none', '--allow-directory=none',
    ];
    if (filePolicy)
        flags.push('--allow-file=root', '--offline');
    else
        flags.push('--allow-file=none', '--registry', REGISTRY_ORIGIN);
    return flags;
}
function assertEffectiveConfig(ws, env, flags) {
    const probe = spawnSync(ws.node, ['--no-global-search-paths', ws.npmCli, 'config', 'list', '--json', ...flags], { cwd: ws.payloadReal, env, encoding: 'utf8', timeout: NPM_TIMEOUT });
    if (probe.status !== 0)
        throw new AdmissionError('dependency-missing', 'npm could not report its effective configuration');
    const config = JSON.parse(probe.stdout);
    const expected = {
        userconfig: ws.npmUser, globalconfig: ws.npmGlobal, cache: ws.npmCache,
        'ignore-scripts': true, 'strict-ssl': true, 'bin-links': false, 'install-links': true,
    };
    for (const [key, value] of Object.entries(expected)) {
        if (config[key] !== value)
            throw new AdmissionError('dependency-missing', `npm configuration isolation assertion failed: ${key}`);
    }
}
function runFetch(ws, filePolicy) {
    const env = trustedSpawnEnvironment('fetch', { home: ws.home, path: join(ws.runtimeDir, 'bin'), tmpdir: ws.tmp });
    const flags = fetchFlags(ws, filePolicy);
    assertEffectiveConfig(ws, env, flags);
    const result = spawnSync(ws.node, ['--no-global-search-paths', ws.npmCli, 'ci', ...flags], { cwd: ws.payloadReal, env, encoding: 'utf8', timeout: NPM_TIMEOUT });
    if (result.error || result.status !== 0) {
        const code = extractNpmCode(result);
        throw new AdmissionError('dependency-missing', `dependency fetch failed${code ? ` (${code})` : ''}`);
    }
    // Delete the redirected npm logs before any lifecycle script runs, so no proxy
    // URL is ever left on disk (C1).
    rmSync(join(ws.npmCache, '_logs'), { recursive: true, force: true });
}
function extractNpmCode(result) {
    if (result.error && 'code' in result.error)
        return String(result.error.code);
    const text = result.stderr || '';
    const match = text.match(/E[A-Z]{3,}/);
    return match ? match[0] : '';
}
function toolShim(path) {
    const quoted = `'${path.replace(/'/g, `'\\''`)}'`;
    return `#!/bin/sh\nexec ${quoted} "$@"\n`;
}
function validateTool(shimName, toolPath) {
    if (!isAbsolute(toolPath))
        throw new AdmissionError('native-prerequisite-missing', `tool ${shimName} path must be absolute`);
    let stat;
    try {
        stat = statSync(toolPath);
    }
    catch {
        throw new AdmissionError('native-prerequisite-missing', `tool ${shimName} not found: ${toolPath}`);
    }
    if (!stat.isFile() || !(stat.mode & 0o111))
        throw new AdmissionError('native-prerequisite-missing', `tool ${shimName} is not an executable file: ${toolPath}`);
    if (process.platform === 'linux') {
        const real = realpathOr(toolPath);
        if (!LINUX_TOOL_ROOTS.some(root => contains(realpathOr(root), real))) {
            throw new AdmissionError('native-prerequisite-missing', `tool ${shimName} lies outside the exposed system roots: ${toolPath}`);
        }
    }
}
function containSpec(ws, homes, command) {
    return { workspace: ws.workspace, runtimeDir: ws.runtimeDir, protectedPaths: homes, execPath: ws.node, command };
}
function runContained(spec, cwd) {
    const contained = containedCommand(spec);
    if ('status' in contained)
        return { status: null, error: true, output: contained.reasons.join('; ') };
    const command = contained;
    const result = spawnSync(command.file, command.args, { cwd, env: command.env, encoding: 'utf8', timeout: NPM_TIMEOUT, stdio: ['ignore', 'pipe', 'pipe'] });
    if (command.profile)
        rmSync(dirname(command.profile), { recursive: true, force: true });
    return { status: result.status, error: Boolean(result.error), output: `${result.stdout || ''}${result.stderr || ''}` };
}
function runBuildPhase(ws, homes, buildNames, prerequisites, containmentForced) {
    for (const name of buildNames) {
        const prereq = prerequisites[name] ?? NATIVE_PREREQUISITES[name];
        if (!prereq)
            throw new AdmissionError('native-prerequisite-missing', `no native prerequisite entry for ${name}`);
        for (const [shimName, toolPath] of Object.entries(prereq.tools)) {
            validateTool(shimName, toolPath);
            writeFileSync(join(ws.runtimeDir, 'bin', shimName), toolShim(toolPath), { mode: 0o555 });
        }
        // boundaryAvailability() is the actual child-start observation (C4): a live
        // smoke of the mechanism. If it fails, or the caller forced unavailability, a
        // build never runs uncontained.
        if (containmentForced || !boundaryAvailability().available)
            throw new AdmissionError('containment-unavailable', `containment unavailable for ${name}`);
        const build = runContained(containSpec(ws, homes, [
            NO_GLOBAL_SEARCH_PATHS, ws.npmCli, 'rebuild', name,
            '--foreground-scripts', '--script-shell', '/bin/sh', '--no-bin-links',
            '--prefix', ws.payloadReal, '--userconfig', ws.npmUser, '--globalconfig', ws.npmGlobal, '--cache', ws.npmCache, '--no-audit', '--no-fund',
        ]), ws.payloadReal);
        if (build.error)
            throw new AdmissionError('containment-unavailable', `containment mechanism failed for ${name}: ${build.output}`);
        if (build.status !== 0)
            throw new AdmissionError('build-script-failed', `build script for ${name} exited ${build.status}`);
        const smokeUrl = pathToFileURL(join(ws.payloadReal, prereq.loadSmoke)).href;
        const smoke = runContained(containSpec(ws, homes, [NO_GLOBAL_SEARCH_PATHS, '--input-type=module', '-e', 'await import(process.argv[1])', smokeUrl]), ws.payloadReal);
        if (smoke.error)
            throw new AdmissionError('containment-unavailable', `containment mechanism failed for ${name} smoke: ${smoke.output}`);
        if (smoke.status !== 0)
            throw new AdmissionError('load-smoke-failed', `load smoke for ${name} exited ${smoke.status}`);
    }
}
// ---- release binding, seal and inventory ---------------------------------
function checkReleaseBinding(payload, files) {
    let observed;
    try {
        observed = payloadSnapshot(payload);
    }
    catch (error) {
        throw new AdmissionError('build-altered-release', `payload shape changed outside ${GENERATED_TREE}: ${error instanceof Error ? error.message : String(error)}`);
    }
    for (const [path, digest] of Object.entries(files)) {
        if (observed[path] !== digest)
            throw new AdmissionError('build-altered-release', `release file changed: ${path}`);
    }
    for (const path of Object.keys(observed)) {
        if (!(path in files))
            throw new AdmissionError('build-altered-release', `unexpected release file: ${path}`);
    }
}
function assertWorkspaceSiblings(ws) {
    const allowed = new Set(['payload', ...STAGING_TRANSIENT, 'bin', 'lib', 'snapshot.json', 'installed-files.json']);
    for (const name of readdirSync(ws.workspace)) {
        if (!allowed.has(name))
            throw new AdmissionError('build-altered-release', `unexpected workspace entry: ${name}`);
    }
}
function walkInventory(root, base, exclude, into) {
    for (const name of readdirSync(root).sort()) {
        const abs = join(root, name);
        const rel = relative(base, abs).split(sep).join('/');
        if (rel === exclude)
            continue;
        const stat = lstatSync(abs);
        if (stat.isSymbolicLink())
            throw new AdmissionError('build-altered-release', `symlink in sealed snapshot: ${rel}`);
        if (stat.isDirectory()) {
            walkInventory(abs, base, exclude, into);
            continue;
        }
        if (!stat.isFile())
            throw new AdmissionError('build-altered-release', `non-regular file in sealed snapshot: ${rel}`);
        if (stat.nlink !== 1)
            throw new AdmissionError('build-altered-release', `hard-linked file in sealed snapshot: ${rel}`);
        into[rel] = { sha256: sha256File(abs), mode: stat.mode & 0o111 ? 'executable' : 'regular' };
    }
}
function checksumManifest(installed, installedFilesSha256) {
    const entries = [
        ['installed-files.json', installedFilesSha256],
        ['snapshot.json', installed.files['snapshot.json'].sha256],
        ['bin/node', installed.files['bin/node'].sha256],
        ['bin/loam-control', installed.files['bin/loam-control'].sha256],
    ];
    for (const [rel, meta] of Object.entries(installed.files)) {
        if (rel.startsWith('payload/dist/'))
            entries.push([rel, meta.sha256]);
    }
    return `${entries.map(([rel, digest]) => `${digest}  ${rel}`).join('\n')}\n`;
}
// ---- control-root state (mirror of the sh controller, item 9) ------------
export function controlRootState(controlRoot) {
    if (!controlRoot || !isAbsolute(controlRoot))
        return diag('control-root-missing', 'control root path is missing');
    let stat;
    try {
        stat = lstatSync(controlRoot);
    }
    catch {
        return diag('control-root-missing', controlRoot);
    }
    if (!stat.isDirectory())
        return diag('control-root-missing', controlRoot);
    const lock = join(controlRoot, CONTROL_ROOT_LAYOUT.lock);
    if (existsSync(lock))
        return diag('install-interrupted', `lock ${lock}`);
    const runtimesDir = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes);
    const entries = safeReaddir(runtimesDir);
    for (const name of entries) {
        if (name.startsWith(CONTROL_ROOT_LAYOUT.stagingPrefix) || name.startsWith(CONTROL_ROOT_LAYOUT.toolPrefix)) {
            return diag('install-interrupted', `staging ${join(runtimesDir, name)}`);
        }
    }
    const complete = [];
    for (const id of entries.filter(name => HEX16.test(name))) {
        if (!runtimeRecordsComplete(controlRoot, id))
            return diag('install-interrupted', `unregistered ${id}`);
        complete.push(id);
    }
    const selectedPath = join(controlRoot, CONTROL_ROOT_LAYOUT.selected);
    if (existsSync(selectedPath)) {
        const selected = parseSelected(selectedPath);
        if (!selected || !complete.includes(selected.snapshotId))
            return diag('install-interrupted', 'selection');
        return { kind: 'selected', selected, snapshotPath: join(runtimesDir, selected.snapshotId) };
    }
    if (complete.length)
        return diag('install-interrupted', `unselected ${complete[0]}`);
    return diag('nothing-admitted', 'no runtime has been admitted');
}
function diag(diagnostic, detail) {
    return { kind: 'diagnostic', diagnostic, detail };
}
function safeReaddir(dir) { try {
    return readdirSync(dir);
}
catch {
    return [];
} }
function runtimeRecordsComplete(controlRoot, id) {
    return existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.admissions, `${id}.json`))
        && existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.sha256`))
        && existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords, `${id}.json`));
}
function parseSelected(path) {
    let value;
    try {
        value = readJson(path);
    }
    catch {
        return null;
    }
    if (!isRecord(value) || value.version !== 1 || typeof value.snapshotId !== 'string' || typeof value.admissionId !== 'string')
        return null;
    if (!HEX16.test(value.snapshotId) || !HEX16.test(value.admissionId))
        return null;
    if (Object.keys(value).length !== 3)
        return null;
    return { version: 1, snapshotId: value.snapshotId, admissionId: value.admissionId };
}
// ---- publication ----------------------------------------------------------
function acquireLock(controlRoot) {
    const registry = join(controlRoot, CONTROL_ROOT_LAYOUT.registry);
    ensureNoSymlink(registry);
    mkdirSync(registry, { recursive: true });
    const lock = join(controlRoot, CONTROL_ROOT_LAYOUT.lock);
    ensureNoSymlink(lock);
    let fd;
    try {
        fd = openSync(lock, 'wx');
    }
    catch {
        throw new AdmissionError('install-interrupted', `lock ${lock}`);
    }
    writeSync(fd, `${JSON.stringify({ pid: process.pid, at: new Date().toISOString() })}\n`);
    closeSync(fd);
    return lock;
}
function recheckUnderLock(controlRoot) {
    // Under our own lock, mirror the item 9 state table (minus the lock row, which
    // we hold). A valid selection is selection-exists; any staging, incomplete or
    // complete-but-unselected runtime is the corresponding install-interrupted.
    const runtimesDir = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes);
    const entries = safeReaddir(runtimesDir);
    for (const name of entries) {
        if (name.startsWith(CONTROL_ROOT_LAYOUT.stagingPrefix) || name.startsWith(CONTROL_ROOT_LAYOUT.toolPrefix)) {
            throw new AdmissionError('install-interrupted', `staging ${join(runtimesDir, name)}`);
        }
    }
    const complete = [];
    for (const rid of entries.filter(name => HEX16.test(name))) {
        if (!runtimeRecordsComplete(controlRoot, rid))
            throw new AdmissionError('install-interrupted', `unregistered ${rid}`);
        complete.push(rid);
    }
    const selectedPath = join(controlRoot, CONTROL_ROOT_LAYOUT.selected);
    if (existsSync(selectedPath)) {
        const selected = parseSelected(selectedPath);
        if (!selected || !complete.includes(selected.snapshotId))
            throw new AdmissionError('install-interrupted', 'selection');
        throw new AdmissionError('selection-exists', 'a runtime is already selected for this control root');
    }
    if (complete.length)
        throw new AdmissionError('install-interrupted', `unselected ${complete[0]}`);
}
function resolveHomes(controlRoot, protect) {
    const homes = {};
    for (const kind of PROTECTED_HOMES) {
        const override = protect?.[kind];
        if (override !== undefined && OVERRIDABLE_HOMES.includes(kind)) {
            const resolved = realpathOr(override);
            if (!isAbsolute(override) || !existsSync(override) || !lstatSync(override).isDirectory() || contains(realpathOr(controlRoot), resolved)) {
                throw new AdmissionError('control-root-missing', `protected ${kind} override must be an existing directory outside the control root`);
            }
            homes[kind] = resolved;
        }
        else {
            homes[kind] = join(controlRoot, CONTROL_ROOT_LAYOUT.homes[kind]);
        }
    }
    return homes;
}
function createHomes(controlRoot, homes) {
    for (const kind of PROTECTED_HOMES) {
        const path = homes[kind];
        let stat;
        try {
            stat = lstatSync(path);
        }
        catch {
            mkdirSync(path, { recursive: true });
            continue;
        }
        if (stat.isSymbolicLink() || !stat.isDirectory())
            throw new AdmissionError('control-root-missing', `home ${kind} at ${path} is not a directory`);
    }
}
function faultCheck(options, point) {
    if (options.test?.faultAfter === point)
        process.exit(70);
}
export async function admitRuntime(options) {
    const filePolicy = options.test?.originPolicy === 'file';
    const { source, repoRoot } = resolveTrustedSource(options.trustedSource, options.controlRoot);
    if (!isAbsolute(options.controlRoot))
        throw new AdmissionError('control-root-missing', 'control root must be an absolute path');
    if (!existsSync(options.controlRoot) || !lstatSync(options.controlRoot).isDirectory())
        throw new AdmissionError('control-root-missing', options.controlRoot);
    assertNoAncestorPackages(options.controlRoot);
    const tools = admitTools(options.toolchain, source);
    const { identity, files } = readReleaseIdentity(source, repoRoot, options.releaseIdentity);
    const id = computeId(identity, tools);
    const deps = lockDependencies(source);
    assertLockOrigins(deps, filePolicy);
    const trustedPackage = readJson(join(source, 'package.json'));
    const allowScripts = trustedPackage.allowScripts ?? {};
    assertScriptsAllowed(deps, allowScripts);
    const controlRoot = options.controlRoot;
    const homes = resolveHomes(controlRoot, options.protect);
    const runtimesDir = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes);
    const lock = acquireLock(controlRoot);
    let owned = true;
    const releaseLock = () => { if (owned) {
        rmSync(lock, { force: true });
        owned = false;
    } };
    try {
        recheckUnderLock(controlRoot);
        createHomes(controlRoot, homes);
        mkdirSync(runtimesDir, { recursive: true });
        const ws = layoutWorkspace(controlRoot, id, options.toolchain);
        copyReleaseFiles(source, ws.payload, files);
        runFetch(ws, filePolicy);
        const buildNames = deps.filter(dep => dep.entry.hasInstallScript).map(dep => dep.name);
        if (buildNames.length) {
            runBuildPhase(ws, homes, buildNames, options.test?.nativePrerequisites ?? {}, options.test?.containment === 'unavailable');
            checkReleaseBinding(ws.payload, files);
        }
        assertWorkspaceSiblings(ws);
        checkReleaseBinding(ws.payload, files);
        const record = {
            version: 1, id, admittedAt: new Date().toISOString(), release: identity, files, tools,
            allowedBuildScripts: allowScripts,
            protectedPaths: homes,
            providers: { payloads: [], successor: 'https://github.com/SamyakJhaveri/loam/issues/140' },
        };
        const installedFilesSha256 = sealSnapshot(ws, source, id);
        faultCheck(options, 'seal');
        chmodTreeReadOnly(ws.workspace);
        faultCheck(options, 'chmod');
        const finalSnapshot = join(runtimesDir, id);
        requireAbsent(finalSnapshot);
        renameSync(ws.workspace, finalSnapshot);
        rmSync(ws.runtimeDir, { recursive: true, force: true });
        faultCheck(options, 'rename');
        const admissionsDir = join(controlRoot, CONTROL_ROOT_LAYOUT.admissions);
        const runtimeRecordsDir = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimeRecords);
        mkdirSync(admissionsDir, { recursive: true });
        mkdirSync(runtimeRecordsDir, { recursive: true });
        writeCanonicalAtomic(admissionsDir, `${id}.json`, record);
        faultCheck(options, 'admission-record');
        const installed = readJson(join(finalSnapshot, 'installed-files.json'));
        const checksum = checksumManifest(installed, installedFilesSha256);
        writeTextAtomic(runtimeRecordsDir, `${id}.sha256`, checksum);
        faultCheck(options, 'sha256');
        writeCanonicalAtomic(runtimeRecordsDir, `${id}.json`, { version: 1, snapshotId: id, admissionId: id, installedFilesSha256 });
        faultCheck(options, 'runtime-record');
        installController(source, controlRoot);
        faultCheck(options, 'controller');
        writeCanonicalAtomic(join(controlRoot, CONTROL_ROOT_LAYOUT.registry), 'selected.json', { version: 1, snapshotId: id, admissionId: id });
        faultCheck(options, 'selected');
        releaseLock();
        return { id, snapshotPath: finalSnapshot, admissionPath: join(admissionsDir, `${id}.json`) };
    }
    catch (error) {
        releaseLock();
        throw error;
    }
}
function layoutWorkspace(controlRoot, id, toolchain) {
    const runtimesDir = join(controlRoot, CONTROL_ROOT_LAYOUT.runtimes);
    const workspace = join(runtimesDir, `${CONTROL_ROOT_LAYOUT.stagingPrefix}${id}`);
    const runtimeDir = join(runtimesDir, `${CONTROL_ROOT_LAYOUT.toolPrefix}${id}`);
    requireAbsent(workspace);
    requireAbsent(runtimeDir);
    const payload = join(workspace, 'payload');
    const home = join(workspace, 'home');
    const tmp = join(workspace, 'tmp');
    const npm = join(workspace, 'npm');
    for (const dir of [payload, home, tmp, npm, join(npm, 'cache')])
        mkdirSync(dir, { recursive: true });
    writeFileSync(join(npm, 'user'), '');
    writeFileSync(join(npm, 'global'), '');
    mkdirSync(join(runtimeDir, 'bin'), { recursive: true });
    copyRegularTree(join(toolchain, 'bin/node'), join(runtimeDir, 'bin/node'));
    copyRegularTree(join(toolchain, 'lib/node_modules/npm'), join(runtimeDir, 'lib/node_modules/npm'));
    return {
        workspace, runtimeDir, payload, payloadReal: realpathSync(payload), home, tmp,
        npmUser: join(npm, 'user'), npmGlobal: join(npm, 'global'), npmCache: join(npm, 'cache'),
        node: join(runtimeDir, 'bin/node'), npmCli: join(runtimeDir, 'lib/node_modules/npm/bin/npm-cli.js'),
    };
}
// Copy only the recorded release files into the staging payload, verifying each
// byte-for-byte against the admission map. node_modules is never in the map; npm
// creates it during the fetch. A drift from the recorded digest is a wrong
// release, not a build change.
function copyReleaseFiles(source, payload, files) {
    for (const [rel, digest] of Object.entries(files)) {
        const from = join(source, rel);
        const to = join(payload, rel);
        mkdirSync(dirname(to), { recursive: true });
        if (lstatSync(from).isSymbolicLink())
            throw new AdmissionError('wrong-release-digest', `release file is a symlink: ${rel}`);
        cpSync(from, to);
        if (sha256File(to) !== digest)
            throw new AdmissionError('wrong-release-digest', `release file digest mismatch: ${rel}`);
    }
}
function sealSnapshot(ws, source, id) {
    for (const transient of STAGING_TRANSIENT)
        rmSync(join(ws.workspace, transient), { recursive: true, force: true });
    mkdirSync(join(ws.workspace, 'bin'), { recursive: true });
    renameSync(join(ws.runtimeDir, 'bin/node'), join(ws.workspace, 'bin/node'));
    chmodSync(join(ws.workspace, 'bin/node'), 0o555);
    renameSync(join(ws.runtimeDir, 'lib'), join(ws.workspace, 'lib'));
    cpSync(join(source, 'scripts/loam-control.sh'), join(ws.workspace, 'bin/loam-control'));
    chmodSync(join(ws.workspace, 'bin/loam-control'), 0o555);
    const snapshotRecord = {
        version: 1, id, admissionId: id, createdAt: new Date().toISOString(),
        layout: { payload: 'payload', node: 'bin/node', npm: 'lib/node_modules/npm', npmCli: 'lib/node_modules/npm/bin/npm-cli.js', controller: 'bin/loam-control', modules: 'payload/node_modules', installedFiles: 'installed-files.json', snapshot: 'snapshot.json', doctor: 'payload/dist/src/commands/doctor.js' },
    };
    writeCanonical(join(ws.workspace, 'snapshot.json'), snapshotRecord);
    const inventory = { version: 1, files: {} };
    walkInventory(ws.workspace, ws.workspace, 'installed-files.json', inventory.files);
    const bytes = `${canonicalJson(inventory)}\n`;
    writeFileSync(join(ws.workspace, 'installed-files.json'), bytes);
    return sha256(bytes);
}
function installController(source, controlRoot) {
    const temp = join(controlRoot, `${CONTROL_ROOT_LAYOUT.controller}.tmp`);
    const finalPath = join(controlRoot, CONTROL_ROOT_LAYOUT.controller);
    ensureNoSymlink(finalPath);
    ensureNoSymlink(temp);
    cpSync(join(source, 'scripts/loam-control.sh'), temp);
    chmodSync(temp, 0o555);
    renameSync(temp, finalPath);
}
function writeTextAtomic(dir, name, text) {
    const finalPath = join(dir, name);
    const tempPath = join(dir, `.${name}.tmp`);
    ensureNoSymlink(finalPath);
    writeFileSync(tempPath, text);
    renameSync(tempPath, finalPath);
}
function usage(detail) {
    process.stdout.write(`${JSON.stringify({ status: 'usage', detail })}\n`);
    process.exit(2);
}
function requireAbsoluteArg(value, flag) {
    if (value === undefined || !isAbsolute(value) || value.includes('\n') || value.includes('\0'))
        usage(`${flag} must be an absolute path without newline or NUL`);
    return value;
}
function parseArgs(argv) {
    const values = {};
    const protect = {};
    for (let i = 0; i < argv.length; i += 2) {
        const flag = argv[i];
        const value = argv[i + 1];
        if (flag === undefined || !flag.startsWith('--') || value === undefined)
            usage('malformed arguments');
        if (flag === '--protect-registry')
            usage('--protect-registry is not allowed');
        if (flag.startsWith('--protect-')) {
            const kind = flag.slice('--protect-'.length);
            if (!OVERRIDABLE_HOMES.includes(kind))
                usage(`unknown protect kind: ${kind}`);
            protect[kind] = requireAbsoluteArg(value, flag);
        }
        else {
            values[flag] = value;
        }
    }
    const trustedSource = requireAbsoluteArg(values['--trusted-source'], '--trusted-source');
    const controlRoot = requireAbsoluteArg(values['--control-root'], '--control-root');
    const toolchain = requireAbsoluteArg(values['--toolchain'], '--toolchain');
    const releaseIdentity = values['--release-identity'];
    if (releaseIdentity === undefined || releaseIdentity.length < 1 || releaseIdentity.length > 120 || !/^[\x20-\x7e]+$/.test(releaseIdentity)) {
        usage('--release-identity must be 1-120 printable ASCII characters');
    }
    return { trustedSource, controlRoot, toolchain, releaseIdentity: releaseIdentity, protect: Object.keys(protect).length ? protect : undefined };
}
async function main(argv) {
    let parsed;
    try {
        parsed = parseArgs(argv);
    }
    catch (error) {
        if (error instanceof Error && error.message === 'usage')
            return;
        throw error;
    }
    try {
        const outcome = await admitRuntime(parsed);
        process.stdout.write(`${JSON.stringify({ status: 'admitted', id: outcome.id, snapshot: outcome.snapshotPath })}\n`);
        process.exit(0);
    }
    catch (error) {
        if (error instanceof AdmissionError) {
            process.stdout.write(`${JSON.stringify({ status: 'refused', diagnostic: error.diagnostic, detail: error.message })}\n`);
            process.exit(1);
        }
        process.stdout.write(`${JSON.stringify({ status: 'refused', diagnostic: 'install-interrupted', detail: error instanceof Error ? error.message : String(error) })}\n`);
        process.exit(1);
    }
}
if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
    void main(process.argv.slice(2));
}
//# sourceMappingURL=admit.js.map