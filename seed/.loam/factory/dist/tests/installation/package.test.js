import assert from 'node:assert/strict';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { test } from 'node:test';
import { assertImportClosure, createReleaseManifest, payloadFiles, snapshot, verifyPackage } from '../../src/installation/package.js';
import { assertCaseResults, GROUPS, NATIVE_BOUNDARY_CASES, PACKAGE_CASES, POPULATIONS, QUALIFICATION_CASES, requireGroup } from '../../src/testing/verify.js';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
function clone() {
    const target = mkdtempSync(join(tmpdir(), 'loam-package-'));
    cpSync(root, target, { recursive: true, filter: path => !['node_modules', '.cache', '.state', 'runtime-installation'].includes(path.split('/').at(-1)) });
    return target;
}
function changed(action) {
    const target = clone();
    try {
        action(target);
        assert.throws(() => verifyPackage(target));
    }
    finally {
        rmSync(target, { recursive: true, force: true });
    }
}
function env() {
    return Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^(NODE_OPTIONS$|NODE_PATH$|NODE_TEST_|npm_config_)/i.test(key)));
}
test('package.valid-payload', () => {
    const report = verifyPackage(root);
    assert.ok(report.files > 0);
    assert.equal(report.files + 1, payloadFiles(root).length);
    assert.deepEqual(JSON.parse(readFileSync(join(root, 'release-manifest.json'), 'utf8')), createReleaseManifest(root));
});
test('package.changed-source', () => changed(path => writeFileSync(join(path, 'src/installation/package.ts'), '// stale source\n')));
test('package.missing-output', () => changed(path => rmSync(join(path, 'dist/src/installation/package.js'))));
test('package.extra-output', () => changed(path => writeFileSync(join(path, 'dist/extra.js'), 'export {};\n')));
test('package.changed-map', () => {
    changed(path => writeFileSync(join(path, 'dist/src/installation/package.js.map'), '{}'));
    changed(path => {
        const file = join(path, 'dist/src/installation/package.js.map');
        const map = JSON.parse(readFileSync(file, 'utf8'));
        map.sources = ['/private/tmp/build/source.ts'];
        writeFileSync(file, JSON.stringify(map));
    });
});
test('package.unsafe-path', () => {
    changed(path => {
        const manifest = createReleaseManifest(path);
        manifest.files['../outside.js'] = '0'.repeat(64);
        writeFileSync(join(path, 'release-manifest.json'), JSON.stringify(manifest));
    });
    changed(path => writeFileSync(join(path, 'unexpected.txt'), 'not declared'));
    changed(path => writeFileSync(join(path, 'dist/types.d.ts'), 'export {};'));
});
test('package.symlink', () => changed(path => {
    rmSync(join(path, 'dist/src/installation/package.js'));
    symlinkSync(join(root, 'dist/src/installation/package.js'), join(path, 'dist/src/installation/package.js'));
}));
test('package.manifest-boundaries', () => {
    const manifest = createReleaseManifest(root);
    assert.equal(manifest.files['release-manifest.json'], undefined);
    for (const prefix of ['src/', 'tests/', 'scripts/', 'dist/', 'assets/'])
        assert.ok(Object.keys(manifest.files).some(path => path.startsWith(prefix)));
    for (const name of ['.gitignore', 'launcher.mjs', 'package.json', 'package-lock.json', 'tsconfig.json'])
        assert.ok(manifest.files[name]);
    changed(path => {
        const value = { ...createReleaseManifest(path), trusted: true };
        writeFileSync(join(path, 'release-manifest.json'), JSON.stringify(value));
    });
    assert.deepEqual(Object.keys(snapshot(root)), payloadFiles(root));
});
test('package.registry-obligations', () => {
    assert.equal(new Set(POPULATIONS.map(value => value.id)).size, POPULATIONS.length);
    const available = new Map([
        ['package-closure', { fixture: 'dist/tests/installation/package.test.js', cases: PACKAGE_CASES }],
        ['platform-qualification', { fixture: 'dist/tests/platform/qualification.test.js', cases: QUALIFICATION_CASES }],
        // native-boundary is host-only; see the OPS-10 note in verify.ts POPULATIONS.
        ['native-boundary', { fixture: 'dist/tests/platform/native-boundary.test.js', cases: NATIVE_BOUNDARY_CASES }],
    ]);
    for (const [id, expected] of available) {
        const entry = POPULATIONS.find(value => value.id === id);
        assert.ok(entry?.available, `${id} available`);
        assert.equal(entry.fixture, expected.fixture);
        assert.deepEqual(entry.expectedCases, expected.cases);
    }
    const owners = new Set(POPULATIONS.flatMap(value => [...value.owners]));
    for (const [prefix, count] of [['CORE', 10], ['NATIVE', 13], ['OPS', 12]]) {
        for (let index = 1; index <= count; index++)
            assert.ok(owners.has(`${prefix}-${String(index).padStart(2, '0')}`));
    }
    for (const population of POPULATIONS) {
        assert.ok(population.expectedCases.length > 0);
        if (population.scope !== 'recipient')
            assert.equal(population.groups.length, 0);
        if (!available.has(population.id))
            assert.equal(population.available, false);
    }
    assert.deepEqual(POPULATIONS.find(value => value.id === 'curated-workflows')?.owners, ['NATIVE-06', 'NATIVE-07']);
});
test('package.unknown-group', () => assert.throws(() => requireGroup('not-a-group')));
test('package.unavailable-groups', () => {
    assert.deepEqual(GROUPS, ['installation', 'store', 'execution', 'complete-slice']);
    for (const group of GROUPS) {
        const report = requireGroup(group);
        assert.equal(report.available, false);
        assert.ok(report.missing.length > 0);
    }
});
test('package.case-accounting', () => {
    assert.throws(() => assertCaseResults([], []));
    assert.throws(() => assertCaseResults(['expected'], []));
    const pass = { type: 'test:pass', data: { name: 'expected', nesting: 0, parentId: 0, details: { type: 'test' } } };
    const summary = { type: 'test:summary', data: { success: true, counts: { tests: 1, passed: 1, failed: 0, cancelled: 0, skipped: 0, todo: 0, suites: 0 } } };
    assert.equal(assertCaseResults(['expected'], [pass, summary]).passed, 1);
    for (const events of [
        [pass], [summary], [pass, pass, summary], [pass, summary, summary],
        [pass, { ...summary, data: { ...summary.data, file: 'fixture.mjs' } }],
        [pass, { ...summary, data: { ...summary.data, success: false } }],
        [{ ...pass, type: 'test:fail' }, summary],
        [{ ...pass, data: { ...pass.data, skip: true } }, summary],
        [{ ...pass, data: { ...pass.data, todo: true } }, summary],
        [{ ...pass, data: { ...pass.data, nesting: 1 } }, summary],
        [{ ...pass, data: { ...pass.data, parentId: 'suite' } }, summary],
        [{ ...pass, data: { ...pass.data, details: { type: 'suite' } } }, summary],
        [pass, { type: 'test:interrupted' }, summary], [null],
    ])
        assert.throws(() => assertCaseResults(['expected'], events));
    assert.throws(() => assertCaseResults(['expected', 'expected'], [pass, summary]));
    const target = mkdtempSync(join(tmpdir(), 'loam-accounting-'));
    try {
        const file = join(target, 'fixture.mjs');
        const runner = join(target, 'runner.mjs');
        const moduleURL = pathToFileURL(join(root, 'dist/src/testing/verify.js')).href;
        writeFileSync(runner, `import {runFixedFixture} from ${JSON.stringify(moduleURL)};
console.log(JSON.stringify(await runFixedFixture(process.argv[2], JSON.parse(process.argv[3]))));
`);
        let invocation = 0;
        const runReal = (expected) => {
            invocation++;
            const trace = process.env.LOAM_FACTORY_EVENT_TRACE;
            const result = spawnSync(process.execPath, [runner, file, JSON.stringify(expected)], {
                cwd: target, encoding: 'utf8', timeout: 30000,
                env: { ...env(), ...(trace ? { LOAM_FACTORY_EVENT_TRACE: `${trace}.accounting-${invocation}.json` } : {}) },
            });
            if (result.error)
                throw result.error;
            if (result.status !== 0)
                throw new Error(result.stderr || `Runner exited ${result.status}`);
            return result.stdout;
        };
        writeFileSync(file, "import {test} from 'node:test'; test('expected',()=>{});\n");
        assert.equal(JSON.parse(runReal(['expected'])).passed, 1);
        assert.throws(() => runReal(['missing']));
        writeFileSync(file, "import {test} from 'node:test'; test('expected',()=>{}); test('expected',()=>{});\n");
        assert.throws(() => runReal(['expected']));
        writeFileSync(file, "import {test} from 'node:test'; test.skip('expected',()=>{});\n");
        assert.throws(() => runReal(['expected']));
        writeFileSync(file, "import {describe,test} from 'node:test'; describe('suite',()=>test('expected',()=>{}));\n");
        assert.throws(() => runReal(['expected']));
        writeFileSync(file, 'export {};\n');
        assert.throws(() => runReal(['expected']));
        writeFileSync(file, "throw new Error('load failure');\n");
        assert.throws(() => runReal(['expected']));
        rmSync(file);
        assert.throws(() => runReal(['expected']));
    }
    finally {
        rmSync(target, { recursive: true, force: true });
    }
});
test('package.compiler-free-recipient', () => {
    const target = clone();
    try {
        assert.equal(existsSync(join(target, 'node_modules')), false);
        const script = "import {verifyPackage} from './dist/src/installation/package.js'; console.log(JSON.stringify(verifyPackage(process.cwd())));";
        const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { cwd: target, env: { ...env(), PATH: '/nonexistent' }, encoding: 'utf8', timeout: 30000 });
        assert.equal(result.status, 0, result.stderr);
        assert.ok(JSON.parse(result.stdout).files > 0);
    }
    finally {
        rmSync(target, { recursive: true, force: true });
    }
});
test('package.import-closure', () => {
    assertImportClosure(root);
    const target = clone();
    try {
        const file = join(target, 'dist/injected.js');
        mkdirSync(join(target, 'dist/%2e%2e'));
        writeFileSync(join(target, 'dist/%2e%2e/out.js'), 'export {};');
        for (const source of ["import 'external-package';", "import '../../../outside.js';", "import(process.argv[0]);", "require('node:fs');", "import {createRequire} from 'node:module';", "import.meta.resolve('x');", "const x = `${import(process.argv[0])}`;", String.raw `import 'external\x2dpackage';`, "import.meta['resolve']('x');", "const x = m['createRequire'](import.meta.url);", "import './%2e%2e/out.js';"]) {
            writeFileSync(file, source);
            assert.throws(() => assertImportClosure(target), source);
        }
    }
    finally {
        rmSync(target, { recursive: true, force: true });
    }
});
//# sourceMappingURL=package.test.js.map