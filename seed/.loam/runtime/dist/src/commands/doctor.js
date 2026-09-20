// Installed runtime doctor (CORE-04). Read-only diagnostics for an admitted
// runtime. It is meant to run as the snapshot's own Node, launched only by the
// trusted controller. It classifies the selected runtime's health against the
// protected registry and never writes.
//
// Diagnostic precedence (C4): the control-root state table first (via
// controlRootState), then not-admitted-runtime, then environment-injected, then
// installed-file-altered, then the registry identity relationships
// (install-interrupted), then build-altered-release, then unadmitted-fork. The
// identity relationships (B2) run after the installed inventory is byte-verified
// and before the payload byte re-hash, so a record-only mismatch is
// install-interrupted while an actual byte change stays build-altered-release. The
// first failing check is the reported diagnostic. A checkout that does not match
// the admitted release is a separate attestation on the `checkout` field and does
// not by itself mark the installation unhealthy.
import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync, realpathSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CONTROL_ROOT_LAYOUT, NO_GLOBAL_SEARCH_PATHS, SNAPSHOT_LAYOUT } from '../contracts/installation.js';
import { isStrippedVariable } from '../platform/env-policy.js';
import { isRecord, readJson } from '../platform/util.js';
import { computeId, controlRootState } from '../installation/admit.js';
// A snapshot entry that is not a plain file or directory, or is a symlink. The
// sealed snapshot forbids these, so encountering one is tampering.
class TamperError extends Error {
}
function hashFile(path) {
    return createHash('sha256').update(readFileSync(path)).digest('hex');
}
const HEX64 = /^[0-9a-f]{64}$/;
// Structural validators for the registry records and the installed inventory
// (B2). They run before any field is used, so a malformed or vacuous record is a
// structured diagnostic, never a raw TypeError and never a false healthy. They do
// not authenticate the record; the integrity proof stays the byte re-hashing
// (installed-files.json and the release map) and the controller's pre-dispatch
// digest set.
function isHex64(value) {
    return typeof value === 'string' && HEX64.test(value);
}
function isReleaseIdentity(value) {
    return isRecord(value)
        && typeof value.label === 'string' && value.label.length > 0
        && typeof value.sourcePath === 'string' && value.sourcePath.length > 0
        && (value.gitDescribe === null || typeof value.gitDescribe === 'string')
        && isHex64(value.sourceDigest) && isHex64(value.outputDigest)
        && isHex64(value.dependencyDigest) && isHex64(value.manifestSha256);
}
function isAdmittedTools(value) {
    if (!isRecord(value))
        return false;
    if (typeof value.platform !== 'string' || typeof value.arch !== 'string')
        return false;
    const node = value.node;
    const npm = value.npm;
    return isRecord(node)
        && typeof node.version === 'string' && typeof node.sqlite === 'string'
        && isHex64(node.sha256) && typeof node.sourcePath === 'string'
        && isRecord(npm)
        && typeof npm.version === 'string'
        && isHex64(npm.cliSha256) && isHex64(npm.packageSha256) && typeof npm.sourcePath === 'string';
}
// The per-file release map: non-empty, each key a snapshot-relative path, each
// value a sha256. An empty map must not certify (it would make the release loop a
// no-op).
function isReleaseFileMap(value) {
    if (!isRecord(value))
        return false;
    const entries = Object.entries(value);
    if (entries.length === 0)
        return false;
    return entries.every(([path, digest]) => path.length > 0 && !path.startsWith('/') && !path.split('/').includes('..') && isHex64(digest));
}
function isInstalledFiles(value) {
    if (!isRecord(value) || value.version !== 1 || !isRecord(value.files))
        return false;
    return Object.values(value.files).every((entry) => isRecord(entry) && isHex64(entry.sha256) && (entry.mode === 'executable' || entry.mode === 'regular'));
}
// Remaining AdmissionRecord fields the shape check completes (B2). protectedPaths
// must carry exactly the six protected-home kinds, each an absolute path.
const PROTECTED_KEYS = Object.keys(CONTROL_ROOT_LAYOUT.homes).sort();
function isAllowedBuildScripts(value) {
    return isRecord(value) && Object.values(value).every((entry) => typeof entry === 'boolean');
}
function isProviders(value) {
    return isRecord(value) && Array.isArray(value.payloads)
        && value.payloads.every((entry) => typeof entry === 'string')
        && typeof value.successor === 'string';
}
function isProtectedPaths(value) {
    if (!isRecord(value))
        return false;
    const keys = Object.keys(value).sort();
    return keys.length === PROTECTED_KEYS.length
        && PROTECTED_KEYS.every((key, index) => key === keys[index])
        && Object.values(value).every((entry) => typeof entry === 'string' && entry.startsWith('/'));
}
function fileMode(path) {
    return (statSync(path).mode & 0o111) !== 0 ? 'executable' : 'regular';
}
// Every regular file under `root`, as sorted posix paths relative to it. A
// symlink or any non-regular entry throws TamperError.
function collectFiles(root) {
    const files = [];
    const walk = (dir) => {
        for (const name of readdirSync(dir).sort()) {
            const abs = join(dir, name);
            const rel = relative(root, abs).split(sep).join('/');
            const stat = lstatSync(abs);
            if (stat.isSymbolicLink())
                throw new TamperError(rel);
            if (stat.isDirectory())
                walk(abs);
            else if (stat.isFile())
                files.push(rel);
            else
                throw new TamperError(rel);
        }
    };
    walk(root);
    return files;
}
// True when the checkout's launcher.mjs, scripts/loam-control.sh,
// release-manifest.json and every dist file match the admitted release map, and
// the checkout adds no dist file the release map does not record.
function checkoutMatches(checkout, files) {
    const fixed = ['launcher.mjs', 'scripts/loam-control.sh', 'release-manifest.json'];
    const recordedDist = Object.keys(files).filter(path => path.startsWith('dist/'));
    for (const path of [...fixed, ...recordedDist]) {
        const expected = files[path];
        if (expected === undefined)
            return false;
        try {
            if (hashFile(join(checkout, path)) !== expected)
                return false;
        }
        catch {
            return false;
        }
    }
    let present;
    try {
        present = collectFiles(join(checkout, 'dist')).map(path => `dist/${path}`);
    }
    catch {
        return false;
    }
    const recorded = new Set(recordedDist);
    return present.every(path => recorded.has(path));
}
export function runDoctor(options) {
    const resolution = {
        nodePath: process.env.NODE_PATH ?? null,
        globalSearchPaths: !process.execArgv.includes(NO_GLOBAL_SEARCH_PATHS),
        execArgv: [...process.execArgv],
    };
    const report = (status, installation, diagnostics) => ({ status, diagnostics, installation, providerReadiness: 'not-evaluated', resolution });
    const state = controlRootState(options.controlRoot);
    if (state.kind === 'diagnostic') {
        return report('unhealthy', 'unavailable', [{ code: state.diagnostic, detail: state.detail }]);
    }
    const root = options.controlRoot;
    const { selected, snapshotPath } = state;
    // Registry records live outside the sealed snapshot, so the controller's
    // pre-dispatch digest set does not cover them. Parse defensively: a malformed
    // or internally inconsistent record is a corrupt/interrupted registry,
    // reported as a structured install-interrupted, never a raw SyntaxError. (R2)
    const interrupt = (detail) => report('unhealthy', 'unavailable', [{ code: 'install-interrupted', detail }]);
    let parsedAdmission;
    try {
        parsedAdmission = readJson(join(root, CONTROL_ROOT_LAYOUT.admissions, `${selected.admissionId}.json`));
    }
    catch {
        return interrupt(`admission record is not valid JSON: ${selected.admissionId}`);
    }
    if (!isRecord(parsedAdmission) || parsedAdmission.version !== 1 || parsedAdmission.id !== selected.admissionId
        || typeof parsedAdmission.admittedAt !== 'string' || parsedAdmission.admittedAt.length === 0
        || !isReleaseFileMap(parsedAdmission.files)
        || !isReleaseIdentity(parsedAdmission.release)
        || !isAdmittedTools(parsedAdmission.tools)
        || !isAllowedBuildScripts(parsedAdmission.allowedBuildScripts)
        || !isProviders(parsedAdmission.providers)
        || !isProtectedPaths(parsedAdmission.protectedPaths)) {
        return interrupt(`admission record malformed or not matching the selection: ${selected.admissionId}`);
    }
    const record = parsedAdmission;
    let parsedRuntime;
    try {
        parsedRuntime = readJson(join(root, CONTROL_ROOT_LAYOUT.runtimeRecords, `${selected.snapshotId}.json`));
    }
    catch {
        return interrupt(`runtime record is not valid JSON: ${selected.snapshotId}`);
    }
    if (!isRecord(parsedRuntime) || parsedRuntime.version !== 1
        || parsedRuntime.snapshotId !== selected.snapshotId
        || parsedRuntime.admissionId !== selected.admissionId
        || typeof parsedRuntime.installedFilesSha256 !== 'string'
        || !HEX64.test(parsedRuntime.installedFilesSha256)) {
        return interrupt(`runtime record malformed or not matching the selection: ${selected.snapshotId}`);
    }
    const runtimeRecord = parsedRuntime;
    const snapshot = { id: selected.snapshotId, admissionId: selected.admissionId, release: record.release, tools: record.tools };
    const fail = (code, detail) => ({ ...report('unhealthy', 'admitted', [{ code, detail }]), snapshot });
    // not-admitted-runtime: this process must be the snapshot's own Node.
    const expectedNode = join(snapshotPath, SNAPSHOT_LAYOUT.node);
    let sameNode = false;
    try {
        sameNode = realpathSync(process.execPath) === realpathSync(expectedNode);
    }
    catch {
        sameNode = false;
    }
    if (!sameNode)
        return fail('not-admitted-runtime', `running Node is not ${expectedNode}`);
    // environment-injected: no stripped-class variable may be present.
    const injected = Object.keys(process.env).filter(isStrippedVariable).sort();
    if (injected.length > 0)
        return fail('environment-injected', `stripped variables present: ${injected.join(', ')}`);
    // installed-file-altered: installed-files.json binds to the runtime record and
    // the observed inventory must match it exactly by path, digest and mode.
    const installedFilesPath = join(snapshotPath, SNAPSHOT_LAYOUT.installedFiles);
    // The sealed inventory is in the controller's pre-dispatch checksum set, so a
    // tampered one is normally refused before doctor runs. When doctor is reached
    // directly, read and parse it defensively: a missing, non-regular, unreadable,
    // or malformed file (even one whose bytes match the recorded digest) is
    // tampering, reported as installed-file-altered, never a raw exception.
    let installed;
    try {
        if (hashFile(installedFilesPath) !== runtimeRecord.installedFilesSha256) {
            return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} digest does not match the runtime record`);
        }
        const parsed = readJson(installedFilesPath);
        if (!isInstalledFiles(parsed)) {
            return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} is malformed`);
        }
        installed = parsed;
    }
    catch {
        return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} is missing or unreadable`);
    }
    let observed;
    try {
        observed = collectFiles(snapshotPath).filter(path => path !== SNAPSHOT_LAYOUT.installedFiles);
    }
    catch (error) {
        return fail('installed-file-altered', error instanceof TamperError ? `non-regular snapshot entry: ${error.message}` : String(error));
    }
    const recorded = new Set(Object.keys(installed.files));
    for (const path of observed)
        if (!recorded.has(path))
            return fail('installed-file-altered', `unexpected snapshot file: ${path}`);
    const observedSet = new Set(observed);
    for (const path of recorded)
        if (!observedSet.has(path))
            return fail('installed-file-altered', `missing snapshot file: ${path}`);
    for (const [path, entry] of Object.entries(installed.files)) {
        const abs = join(snapshotPath, path);
        let actualDigest;
        let actualMode;
        try {
            actualDigest = hashFile(abs);
            actualMode = fileMode(abs);
        }
        catch {
            // A recorded file that cannot be read or stat'd (EACCES, ENOENT, EISDIR, ...)
            // is tampering, classified here rather than escaping as an uncaught
            // exception (B4).
            return fail('installed-file-altered', `snapshot file unreadable: ${path}`);
        }
        if (actualDigest !== entry.sha256)
            return fail('installed-file-altered', `snapshot digest mismatch: ${path}`);
        if (actualMode !== entry.mode)
            return fail('installed-file-altered', `snapshot mode mismatch: ${path}`);
    }
    // B2 identity relationships (install-interrupted): the admission and runtime
    // records live outside the sealed snapshot, so the controller's pre-dispatch
    // digest set does not cover them. Compare the recorded identity against the
    // already byte-verified installed material and this running admitted executable.
    // These are pure comparisons of recorded material against verified material (no
    // new hashing, no self-authentication); a mismatch is an inconsistent registry
    // record. They run before the payload byte re-hash so a record-only mismatch is
    // install-interrupted, never miscategorised as a build alteration.
    const payloadRoot = join(snapshotPath, SNAPSHOT_LAYOUT.payload);
    // Tool identity: recorded tool digests must equal the installed inventory
    // entries, and the recorded platform, architecture and runtime versions must
    // equal this admitted executable's (doctor runs as the snapshot's own Node).
    const nodeInv = installed.files[SNAPSHOT_LAYOUT.node];
    const npmCliInv = installed.files[SNAPSHOT_LAYOUT.npmCli];
    const npmPkgInv = installed.files[`${SNAPSHOT_LAYOUT.npm}/package.json`];
    if (!nodeInv || record.tools.node.sha256 !== nodeInv.sha256) {
        return interrupt(`recorded node digest does not match the installed node: ${selected.admissionId}`);
    }
    if (!npmCliInv || record.tools.npm.cliSha256 !== npmCliInv.sha256
        || !npmPkgInv || record.tools.npm.packageSha256 !== npmPkgInv.sha256) {
        return interrupt(`recorded npm digests do not match the installed npm: ${selected.admissionId}`);
    }
    if (record.tools.platform !== process.platform || record.tools.arch !== process.arch) {
        return interrupt(`recorded platform/arch does not match the running runtime: ${selected.admissionId}`);
    }
    if (record.tools.node.version !== process.version || record.tools.node.sqlite !== process.versions.sqlite) {
        return interrupt(`recorded node version/sqlite does not match the running runtime: ${selected.admissionId}`);
    }
    // The installed npm package.json is in the byte-verified inventory, so its
    // recorded version must equal the version those bytes carry.
    let installedNpmVersion;
    try {
        installedNpmVersion = readJson(join(snapshotPath, SNAPSHOT_LAYOUT.npm, 'package.json')).version;
    }
    catch {
        return fail('installed-file-altered', 'installed npm package.json is unreadable');
    }
    if (record.tools.npm.version !== installedNpmVersion) {
        return interrupt(`recorded npm version does not match the installed npm: ${selected.admissionId}`);
    }
    // Release identity and file map: the inventory check above verified
    // payload/release-manifest.json against installed-files.json, so the manifest
    // read here is trusted. Compare the recorded aggregate release digests and the
    // complete recorded file map against it before re-hashing payload bytes, so a
    // record-only mismatch is install-interrupted, not build-altered-release.
    let manifest;
    try {
        manifest = readJson(join(payloadRoot, 'release-manifest.json'));
    }
    catch {
        return fail('build-altered-release', 'release-manifest.json is unreadable');
    }
    if (!isRecord(manifest.files) || !Object.values(manifest.files).every(isHex64)
        || !isHex64(manifest.sourceDigest) || !isHex64(manifest.outputDigest) || !isHex64(manifest.dependencyDigest)) {
        return fail('build-altered-release', 'release-manifest.json is malformed');
    }
    const manifestFiles = manifest.files;
    if (record.release.sourceDigest !== manifest.sourceDigest
        || record.release.outputDigest !== manifest.outputDigest
        || record.release.dependencyDigest !== manifest.dependencyDigest) {
        return interrupt(`recorded release digests do not match the installed manifest: ${selected.admissionId}`);
    }
    // The recorded manifest self-entry must equal both the recorded aggregate manifest
    // digest and the byte-verified installed manifest.
    const manifestInv = installed.files[`${SNAPSHOT_LAYOUT.payload}/release-manifest.json`];
    if (!manifestInv || record.release.manifestSha256 !== record.files['release-manifest.json']
        || record.files['release-manifest.json'] !== manifestInv.sha256) {
        return interrupt(`recorded manifest digest does not match the installed manifest: ${selected.admissionId}`);
    }
    // record.files must be exactly the manifest file-set plus the manifest self-entry,
    // with matching digests. Driving this off the trusted manifest means a truncated
    // or record-only-altered map cannot certify vacuously.
    const expectedKeys = new Set([...Object.keys(manifestFiles), 'release-manifest.json']);
    const recordKeys = new Set(Object.keys(record.files));
    if (expectedKeys.size !== recordKeys.size || [...expectedKeys].some((key) => !recordKeys.has(key))) {
        return interrupt(`recorded release map does not match the payload manifest: ${selected.admissionId}`);
    }
    for (const [key, digest] of Object.entries(manifestFiles)) {
        if (record.files[key] !== digest)
            return interrupt(`recorded release digest differs from the manifest: ${key}`);
    }
    // Deterministic snapshot ID relationship (admit.ts computeId): the id derived
    // from the recorded release and tool inputs must equal the record id and the
    // selection. The comparisons above already pin those inputs to the installed
    // material, so this is the final structural invariant binding a consistent record
    // to its selected snapshot id.
    if (computeId(record.release, record.tools) !== record.id || record.id !== selected.snapshotId) {
        return interrupt(`recorded identity does not derive the selected snapshot id: ${selected.admissionId}`);
    }
    // build-altered-release: the installed payload bytes must still match the release
    // bytes recorded independently in the admission record (C4). record.files is now
    // confirmed consistent with the installed manifest, so this fires only for an
    // actual payload byte change.
    for (const [path, digest] of Object.entries(record.files)) {
        let actual;
        try {
            actual = hashFile(join(payloadRoot, path));
        }
        catch {
            return fail('build-altered-release', `recorded release file missing: ${path}`);
        }
        if (actual !== digest)
            return fail('build-altered-release', `release file altered: ${path}`);
    }
    // unadmitted-fork: a supplied checkout is a separate attestation about bytes,
    // reported on `checkout` and never mutating installation health.
    const healthy = { ...report('healthy', 'admitted', []), snapshot };
    if (options.checkout !== undefined) {
        healthy.checkout = checkoutMatches(options.checkout, record.files) ? 'matches-admitted-release' : 'unadmitted-fork';
    }
    return healthy;
}
function parseArgs(argv) {
    let mode;
    let controlRoot;
    let checkout;
    for (let i = 0; i < argv.length; i++) {
        const flag = argv[i];
        const value = argv[i + 1];
        if (flag === '--mode') {
            if (value === undefined)
                return { usage: 'missing value for --mode' };
            mode = value;
            i++;
        }
        else if (flag === '--control-root') {
            if (value === undefined)
                return { usage: 'missing value for --control-root' };
            controlRoot = value;
            i++;
        }
        else if (flag === '--checkout') {
            if (value === undefined)
                return { usage: 'missing value for --checkout' };
            checkout = value;
            i++;
        }
        else {
            return { usage: `unexpected argument: ${flag}` };
        }
    }
    if (mode !== 'status' && mode !== 'doctor')
        return { usage: 'expected --mode status|doctor' };
    if (checkout !== undefined && mode !== 'doctor')
        return { usage: '--checkout requires --mode doctor' };
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
//# sourceMappingURL=doctor.js.map