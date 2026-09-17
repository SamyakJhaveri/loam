// Host-only admission-containment qualification (CORE-04).
//
// Flat node:test leaves, one per ADMISSION_CONTAINMENT_CASES id. These run a
// real admission that builds a scripted dependency inside CORE-02 containment,
// so they need a working boundary mechanism. The nested agent sandbox cannot
// nest sandbox-exec, so this population is a host gate (Mac from a plain
// Terminal, Linux on the host) and never appears in bin/check; an unavailable
// mechanism is a failed gate, not a skip, exactly like native-boundary.
//
// The scripted, mutating and failing dependency behaviors live in builder A's
// committed fixture tarballs. This file selects them, seeds canaries in the real
// protected homes, and reads back the dump each fixture writes.
import assert from 'node:assert/strict';
import { test, after } from 'node:test';
import { chmodSync, cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync, } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { admitRuntime } from '../../src/installation/admit.js';
import { AdmissionError, CONTROL_ROOT_LAYOUT, FIXTURE_ORIGIN_PREFIX, SNAPSHOT_LAYOUT, } from '../../src/contracts/installation.js';
import { createReleaseManifest, payloadFiles } from '../../src/installation/package.js';
import { boundaryAvailability } from '../../src/platform/native-boundary.js';
const factoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const toolchain = process.env.LOAM_FACTORY_TOOLCHAIN ?? '';
const HOMES = ['registry', 'state', 'locks', 'credentials', 'sockets', 'callbacks'];
const deniedCode = process.platform === 'darwin' ? 'EPERM' : 'ENOENT';
const scratchRoots = [];
function base() {
    const root = mkdtempSync(join(tmpdir(), 'loam-core04-'));
    scratchRoots.push(root);
    return root;
}
function forceWritable(root) {
    const stack = [root];
    while (stack.length) {
        const path = stack.pop();
        let entry;
        try {
            entry = lstatSync(path);
        }
        catch {
            continue;
        }
        try {
            if (!entry.isSymbolicLink())
                chmodSync(path, entry.isDirectory() ? 0o755 : 0o644);
        }
        catch { /* best effort */ }
        if (entry.isDirectory())
            for (const name of readdirSync(path))
                stack.push(join(path, name));
    }
}
after(() => {
    for (const root of scratchRoots) {
        try {
            forceWritable(root);
        }
        catch { /* best effort */ }
        rmSync(root, { recursive: true, force: true });
    }
});
// Require the boundary mechanism; a missing mechanism fails the host gate.
function requireMechanism() {
    const availability = boundaryAvailability();
    assert.ok(availability.available, availability.available ? '' : `containment unavailable: ${availability.reasons.join('; ')}`);
    return availability.mechanism;
}
function integrityOf(tarball) {
    return `sha512-${createHash('sha512').update(readFileSync(tarball)).digest('base64')}`;
}
// Build a scratch trusted repository whose only dependency is the named scripted
// fixture, covered by allowScripts.
function makeTrusted(scriptedFixture) {
    const repo = join(base(), 'repo');
    const trusted = join(repo, 'seed/.loam/factory');
    mkdirSync(join(repo, 'bin'), { recursive: true });
    writeFileSync(join(repo, 'copier.yml'), '# scratch\n');
    writeFileSync(join(repo, 'VERSION'), '0.0.0\n');
    writeFileSync(join(repo, 'bin/release.sh'), '#!/bin/sh\nexit 0\n');
    for (const file of payloadFiles(factoryRoot)) {
        const target = join(trusted, file);
        mkdirSync(dirname(target), { recursive: true });
        cpSync(join(factoryRoot, file), target);
    }
    const deps = { [scriptedFixture]: '1.0.0' };
    const pkg = { name: '@loam/factory', version: '0.0.0', private: true, type: 'module', dependencies: deps, allowScripts: { [`${scriptedFixture}@1.0.0`]: true } };
    writeFileSync(join(trusted, 'package.json'), `${JSON.stringify(pkg, null, 2)}\n`);
    const tarball = join(trusted, 'assets/admission-fixtures', `${scriptedFixture}-1.0.0.tgz`);
    const lock = {
        name: '@loam/factory', version: '0.0.0', lockfileVersion: 3, requires: true,
        packages: {
            '': { name: '@loam/factory', version: '0.0.0', dependencies: deps },
            [`node_modules/${scriptedFixture}`]: {
                version: '1.0.0',
                resolved: `${FIXTURE_ORIGIN_PREFIX}${scriptedFixture}-1.0.0.tgz`,
                integrity: existsSync(tarball) ? integrityOf(tarball) : `sha512-${'A'.repeat(86)}==`,
                hasInstallScript: true,
            },
        },
    };
    writeFileSync(join(trusted, 'package-lock.json'), `${JSON.stringify(lock, null, 2)}\n`);
    writeFileSync(join(trusted, 'release-manifest.json'), `${JSON.stringify(createReleaseManifest(trusted), null, 2)}\n`);
    return { trusted, controller: join(trusted, 'scripts', 'loam-control.sh') };
}
// A control root whose six homes exist with a canary, so the contained build's
// protected reads have a real target to be denied.
function controlRootWithCanaries(secret) {
    const root = join(base(), 'control');
    for (const home of HOMES) {
        const dir = join(root, home);
        mkdirSync(dir, { recursive: true });
        writeFileSync(join(dir, 'canary'), `${secret}-${home}`);
    }
    return root;
}
function nativePrerequisites(fixture) {
    const tools = { sh: '/bin/sh' };
    for (const candidate of ['/usr/bin/cc', '/usr/bin/gcc', '/bin/cc']) {
        if (existsSync(candidate)) {
            tools.cc = candidate;
            break;
        }
    }
    return { [fixture]: { tools, loadSmoke: `node_modules/${fixture}/smoke.js` } };
}
function admitOptions(trusted, controlRoot, fixture, env) {
    const options = {
        trustedSource: trusted, controlRoot, toolchain, releaseIdentity: 'loam v0.0.0',
        test: { originPolicy: 'file', nativePrerequisites: nativePrerequisites(fixture) },
    };
    if (env)
        for (const [key, value] of Object.entries(env))
            process.env[key] = value;
    return options;
}
function fixtureFile(snapshotPath, fixture, name) {
    return join(snapshotPath, SNAPSHOT_LAYOUT.modules, fixture, name);
}
// Run a full contained admission of the normal scripted fixture and read its dumps.
async function build(secret, env) {
    const fixture = 'loam-dep-scripted';
    const { trusted } = makeTrusted(fixture);
    const controlRoot = controlRootWithCanaries(secret);
    const { snapshotPath } = await admitRuntime(admitOptions(trusted, controlRoot, fixture, env));
    const result = JSON.parse(readFileSync(fixtureFile(snapshotPath, fixture, 'result.json'), 'utf8'));
    const smoke = JSON.parse(readFileSync(fixtureFile(snapshotPath, fixture, 'smoke-result.json'), 'utf8'));
    return { snapshotPath, result, smoke };
}
function envKeys(dump) {
    return Array.isArray(dump) ? dump : Object.keys(dump);
}
test('contain.mechanism-available', () => {
    const mechanism = requireMechanism();
    assert.ok(mechanism.length > 0);
});
test('contain.build-workspace-read-allowed', async () => {
    requireMechanism();
    const built = await build('SECRET-A');
    assert.equal(existsSync(fixtureFile(built.snapshotPath, 'loam-dep-scripted', 'marker')), true);
    assert.equal(built.result.workspaceRead, 'ok');
});
test('contain.build-protected-read-denied', async () => {
    requireMechanism();
    const built = await build('SECRET-B');
    for (const home of HOMES)
        assert.equal(built.result.protectedReads[home], deniedCode, `${home} read must be denied`);
});
test('contain.build-descendant-denied', async () => {
    requireMechanism();
    const built = await build('SECRET-C');
    assert.equal(built.result.descendant.workspaceRead, 'ok');
    for (const home of HOMES)
        assert.equal(built.result.descendant.protectedReads[home], deniedCode, `${home} descendant read must be denied`);
});
test('contain.build-no-proxy-or-credentials', async () => {
    requireMechanism();
    const built = await build('SECRET-D', {
        HTTPS_PROXY: 'https://user:secret@proxy.invalid/',
        LOAM_CANARY_SECRET: 'do-not-leak',
    });
    const keys = envKeys(built.result.env);
    for (const forbidden of ['HTTPS_PROXY', 'https_proxy', 'LOAM_CANARY_SECRET', 'NODE_OPTIONS']) {
        assert.ok(!keys.includes(forbidden), `env dump leaked ${forbidden}`);
    }
    assert.ok(!keys.some((key) => key.startsWith('GIT_')), 'env dump leaked a GIT_ variable');
    assert.ok(!keys.some((key) => key.toLowerCase().startsWith('npm_config_') && key !== 'npm_config_user_agent'), 'env dump leaked a caller npm_config_ variable');
});
test('contain.load-smoke-contained', async () => {
    requireMechanism();
    const built = await build('SECRET-E');
    assert.equal(built.smoke.loaded, true);
    assert.equal(built.smoke.protectedRead, deniedCode);
});
test('contain.build-altered-release-refused', async () => {
    requireMechanism();
    const fixture = 'loam-dep-mutating';
    const { trusted, controller } = makeTrusted(fixture);
    const controlRoot = controlRootWithCanaries('SECRET-F');
    try {
        await admitRuntime(admitOptions(trusted, controlRoot, fixture));
        assert.fail('mutating build must be refused');
    }
    catch (error) {
        assert.ok(error instanceof AdmissionError, String(error));
        assert.equal(error.diagnostic, 'build-altered-release');
    }
    assert.equal(existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.selected)), false);
    // The staging directory is left as evidence and a later status never runs the altered file.
    const status = spawnSync('/bin/sh', [controller, '--control-root', controlRoot, 'status'], { encoding: 'utf8', timeout: 120000 });
    assert.equal(status.status, 1);
    const line = status.stdout.trim().split('\n').filter(Boolean).at(-1);
    const report = JSON.parse(line);
    assert.equal(report.diagnostic, 'install-interrupted');
    assert.ok(String(report.detail).includes('staging'));
});
test('contain.build-script-failed', async () => {
    requireMechanism();
    const fixture = 'loam-dep-failing';
    const { trusted } = makeTrusted(fixture);
    const controlRoot = controlRootWithCanaries('SECRET-G');
    try {
        await admitRuntime(admitOptions(trusted, controlRoot, fixture));
        assert.fail('failing build must be refused');
    }
    catch (error) {
        assert.ok(error instanceof AdmissionError, String(error));
        assert.equal(error.diagnostic, 'build-script-failed');
    }
    assert.equal(existsSync(join(controlRoot, CONTROL_ROOT_LAYOUT.selected)), false);
});
//# sourceMappingURL=admission-containment.test.js.map