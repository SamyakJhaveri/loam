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
import { controlRootState } from '../installation/admit.js';
// A snapshot entry that is not a plain file or directory, or is a symlink. The
// sealed snapshot forbids these, so encountering one is tampering.
class TamperError extends Error {
}
function hashFile(path) {
    return createHash('sha256').update(readFileSync(path)).digest('hex');
}
function readJson(path) {
    return JSON.parse(readFileSync(path, 'utf8'));
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
    const record = readJson(join(root, CONTROL_ROOT_LAYOUT.admissions, `${selected.admissionId}.json`));
    const runtimeRecord = readJson(join(root, CONTROL_ROOT_LAYOUT.runtimeRecords, `${selected.snapshotId}.json`));
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
    if (hashFile(installedFilesPath) !== runtimeRecord.installedFilesSha256) {
        return fail('installed-file-altered', `${SNAPSHOT_LAYOUT.installedFiles} digest does not match the runtime record`);
    }
    const installed = readJson(installedFilesPath);
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
        if (hashFile(abs) !== entry.sha256)
            return fail('installed-file-altered', `snapshot digest mismatch: ${path}`);
        if (fileMode(abs) !== entry.mode)
            return fail('installed-file-altered', `snapshot mode mismatch: ${path}`);
    }
    // build-altered-release: the installed payload must still match the release
    // bytes recorded independently in the admission record (C4).
    const payloadRoot = join(snapshotPath, SNAPSHOT_LAYOUT.payload);
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