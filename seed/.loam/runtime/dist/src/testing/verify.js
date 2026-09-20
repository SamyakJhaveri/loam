import { run } from 'node:test';
import { dirname } from 'node:path';
import { writeFileSync } from 'node:fs';
export const GROUPS = ['installation', 'store', 'execution', 'complete-slice'];
export const PACKAGE_CASES = [
    "package.valid-payload",
    "package.changed-source",
    "package.missing-output",
    "package.extra-output",
    "package.changed-map",
    "package.unsafe-path",
    "package.symlink",
    "package.manifest-boundaries",
    "package.registry-obligations",
    "package.unknown-group",
    "package.unavailable-groups",
    "package.case-accounting",
    "package.compiler-free-recipient",
    "package.import-closure"
];
export const BUILD_CASES = [
    "rebuild.exact",
    "rebuild.stale-source",
    "rebuild.missing-output",
    "rebuild.extra-output",
    "rebuild.changed-map",
    "rebuild.missing-compiler",
    "rebuild.ancestor-collision",
    "rebuild.ancestor-types-collision",
    "rebuild.provider-free-build"
];
export const QUALIFICATION_CASES = [
    "runtime.identity-matches-manifest",
    "runtime.incompatible-reports-precisely",
    "runtime.child-resolved-explicitly",
    "runtime.foreign-executable-refused",
    "storage.uri-encodes-metacharacters",
    "storage.authority-shaped-path-refused",
    "storage.missing-refused",
    "storage.vanish-between-precheck-and-open",
    "storage.empty-rejected-as-foreign",
    "storage.foreign-application-id-rejected",
    "storage.corrupt-rejected",
    "storage.arbitrary-uri-refused",
    "storage.effective-settings-read-back",
    "storage.integer-boundaries",
    "storage.backup-succeeds-and-fails-precisely",
    "storage.busy-worker-keeps-loop-responsive",
    "storage.worker-open-failure-rejects-queries",
    "storage.worker-query-succeeds",
    "storage.worker-close-rejects-queries",
    "storage.worker-exit-settles-requests",
    "storage.worker-close-before-open-settles",
    "lock.competing-owner-refused",
    "lock.stopped-owner-still-owns",
    "lock.killed-owner-releases",
    "lock.child-does-not-inherit",
    "lock.replaced-path-detected",
    "lock.never-unlinks",
    "lock.failed-acquisition-releases",
    "boundary.conflicting-layout-refused",
    "boundary.hard-link-admission-refused",
    "env.preload-stripped",
    "env.openssl-startup-stripped",
    "env.git-redirection-stripped",
    "env.process-sanitized-before-children",
    "env.enforcement-set-pinned",
    "env.diagnostic-set-pinned",
    "env.strip-sets-diverge"
];
export const CATALOG_CASES = [
    "catalog.schema-and-payload",
    "catalog.conservation-rejections",
    "catalog.activation-honesty",
    "catalog.selected-dependencies-mapped",
    "catalog.pocock-collection"
];
// Loam-only source provenance gate (bin/factory-catalog-provenance.mjs). The case
// names are shared here so the registry can declare the release-only population;
// no recipient command runs it and no root bin/ module is imported by the package.
export const PROVENANCE_CASES = [
    "provenance.sources-match-tree",
    "provenance.baseline-map-agreement",
    "provenance.inventory-dispositions"
];
export const NATIVE_BOUNDARY_CASES = [
    "boundary.mechanism-available",
    "boundary.workspace-admitted",
    "boundary.runtime-write-denied",
    "boundary.registry-denied",
    "boundary.state-denied",
    "boundary.locks-denied",
    "boundary.credentials-denied",
    "boundary.callbacks-denied",
    "boundary.sockets-denied",
    "boundary.descendant-denied",
    "boundary.symlink-denied",
    "boundary.path-alias-denied",
    "boundary.hardlink-creation-denied",
    "boundary.same-user-control"
];
export const ADMISSION_CASES = [
    "admission.trusted-source-identity",
    "admission.trusted-source-fork",
    "admission.trusted-source-shape",
    "admission.wrong-release-digest",
    "admission.identities-recorded-separately",
    "admission.staging-writes-contained",
    "admission.bin-links-absent",
    "admission.lock-origin-refused",
    "admission.build-script-refused",
    "admission.build-requires-containment",
    "admission.native-prerequisite-missing",
    "admission.dependency-missing",
    "admission.publication-order",
    "admission.publish-complete-closure-only",
    "admission.control-strips-environment",
    "admission.control-helper-path-isolated",
    "admission.control-rejects-arguments",
    "admission.controller-verifies-before-dispatch",
    "admission.node-identity",
    "admission.runtime-digest-mismatch",
    "admission.control-root-missing",
    "admission.nothing-admitted",
    "admission.no-project-root-resolution",
    "admission.unadmitted-fork",
    "admission.provider-readiness-separate",
    "admission.install-interrupted",
    "admission.altered-installed-file",
    "admission.environment-injected",
    "admission.not-admitted-runtime",
    "admission.ancestor-package-collision",
    "admission.selection-retained",
    "admission.snapshot-link-counts",
    "admission.snapshot-runs-without-checkout",
    "admission.ordinary-commands-unchanged",
    "admission.preexisting-path-refused"
];
export const ADMISSION_CONTAINMENT_CASES = [
    "contain.mechanism-available",
    "contain.build-workspace-read-allowed",
    "contain.build-protected-read-denied",
    "contain.build-descendant-denied",
    "contain.build-no-proxy-or-credentials",
    "contain.load-smoke-contained",
    "contain.build-altered-release-refused",
    "contain.build-script-failed",
    "contain.load-smoke-failed",
    "contain.wrapper-refusal-unavailable",
    "contain.metachar-workspace"
];
export const QUALIFY_VERBS = [
    { verb: 'package', kind: 'package-qualification', fixture: 'dist/tests/installation/package.test.js', cases: PACKAGE_CASES, timeout: 60000 },
    { verb: 'platform', kind: 'platform-qualification', fixture: 'dist/tests/platform/qualification.test.js', cases: QUALIFICATION_CASES, timeout: 120000 },
    { verb: 'catalog', kind: 'catalog-qualification', fixture: 'dist/tests/assets/catalog.test.js', cases: CATALOG_CASES, timeout: 120000 },
    { verb: 'native-boundary', kind: 'native-boundary-qualification', fixture: 'dist/tests/platform/native-boundary.test.js', cases: NATIVE_BOUNDARY_CASES, timeout: 120000 },
    { verb: 'runtime-admission', kind: 'runtime-admission-qualification', fixture: 'dist/tests/installation/admission.test.js', cases: ADMISSION_CASES, timeout: 300000 },
    { verb: 'admission-containment', kind: 'admission-containment-qualification', fixture: 'dist/tests/installation/admission-containment.test.js', cases: ADMISSION_CONTAINMENT_CASES, timeout: 300000 },
];
function verbRow(verb) {
    const row = QUALIFY_VERBS.find(entry => entry.verb === verb);
    if (!row)
        throw new Error(`Unknown qualify verb: ${verb}`);
    return row;
}
function stub(id, owner, groups, n, scope = 'recipient') {
    const owners = typeof owner === 'string' ? [owner] : owner;
    return {
        id, owners, groups, scope, available: false, fixture: null,
        expectedCases: owners.flatMap(entry => Array.from({ length: n }, (_, index) => `${entry.toLowerCase()}/obligation-${String(index + 1).padStart(2, '0')}`))
    };
}
// Future case IDs reserve source obligations. Their owning tickets supply executable cases.
export const POPULATIONS = [
    { id: 'package-closure', owners: ['CORE-01'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('package').fixture, expectedCases: [...verbRow('package').cases] },
    { id: 'platform-qualification', owners: ['CORE-02'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('platform').fixture, expectedCases: [...verbRow('platform').cases] },
    // OPS-10 obligation: native-boundary is available:true (its fixture exists) but is
    // proved only by the two-host `qualify native-boundary` run; bin/check and CI do not
    // run it. OPS-10 closure adds a CI host with bwrap or accepts the host evidence as
    // the gate.
    { id: 'native-boundary', owners: ['CORE-02'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('native-boundary').fixture, expectedCases: [...verbRow('native-boundary').cases] },
    stub('native-qualification', 'CORE-03', ['installation', 'execution'], 5),
    { id: 'runtime-admission', owners: ['CORE-04'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('runtime-admission').fixture, expectedCases: [...verbRow('runtime-admission').cases] },
    // CORE-04 obligation: admission-containment is available:true (its fixture exists) but is
    // proved only by the two-host `qualify admission-containment` run; bin/check and CI do not
    // run it. It mirrors native-boundary: the containment mechanism is unavailable inside the
    // nested agent sandbox, so the Mac gate runs from a plain Terminal and Linux runs on the host.
    { id: 'admission-containment', owners: ['CORE-04'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('admission-containment').fixture, expectedCases: [...verbRow('admission-containment').cases] },
    stub('store-ownership', 'CORE-05', ['store'], 6),
    stub('project-setup', 'CORE-06', ['installation', 'store'], 5),
    stub('local-execution', 'CORE-07', ['execution'], 5),
    stub('ownership-recovery', 'CORE-08', ['store', 'execution'], 6),
    stub('backup-restore', 'CORE-09', ['store'], 6),
    stub('steering-accounting', 'CORE-10', ['store', 'execution'], 7),
    stub('native-profile', 'NATIVE-01', ['installation'], 4),
    stub('coordination', 'NATIVE-02', ['execution'], 5),
    stub('claude-binding', 'NATIVE-03', ['execution'], 4),
    stub('codex-binding', 'NATIVE-04', ['execution'], 5),
    { id: 'curated-catalog', owners: ['NATIVE-05'], groups: ['installation'], scope: 'recipient', available: true, fixture: verbRow('catalog').fixture, expectedCases: [...verbRow('catalog').cases] },
    // Loam-only gate: source provenance for the curated catalog runs from the
    // repository root (bin/factory-catalog-provenance.mjs), never from a recipient.
    { id: 'catalog-provenance', owners: ['NATIVE-05'], groups: [], scope: 'release-only', available: true, fixture: 'bin/tests/factory-catalog-provenance.test.mjs', expectedCases: [...PROVENANCE_CASES] },
    stub('curated-workflows', ['NATIVE-06', 'NATIVE-07'], ['execution'], 4),
    stub('review-methods', 'NATIVE-08', ['execution'], 4),
    stub('memory-records', 'NATIVE-09', ['store'], 4),
    stub('memory-correction', 'NATIVE-10', ['store', 'execution'], 5),
    stub('improvement-adoption', 'NATIVE-11', ['store', 'complete-slice'], 5),
    stub('research-methods', 'NATIVE-12', ['complete-slice'], 4),
    stub('local-complete-slice', 'NATIVE-13', ['complete-slice'], 4),
    stub('readiness', 'OPS-01', ['installation'], 2),
    stub('remote-recovery', 'OPS-02', ['execution'], 2),
    stub('remote-inputs', 'OPS-03', ['execution'], 2),
    stub('remote-policy', 'OPS-04', ['execution'], 2),
    stub('runtime-update', 'OPS-05', ['installation', 'store'], 2),
    stub('maintenance', 'OPS-06', ['store'], 2),
    stub('owner-transfer', 'OPS-07', ['store', 'execution'], 2),
    stub('asset-delivery', 'OPS-08', ['installation'], 2),
    stub('release-render-matrix', 'OPS-09', [], 2, 'release-only'),
    stub('generated-product-closure', 'OPS-10', ['installation', 'store', 'execution', 'complete-slice'], 3),
    stub('real-use-evidence', 'OPS-11', [], 3, 'post-installation'),
    stub('remote-complete-slice', 'OPS-12', ['complete-slice'], 2),
];
export function requireGroup(name) {
    if (!GROUPS.includes(name))
        throw new Error(`Unknown verification group: ${name}`);
    const required = POPULATIONS.filter(population => population.groups.includes(name));
    if (!required.length)
        throw new Error(`Empty verification group: ${name}`);
    for (const population of required) {
        if (!population.expectedCases.length || new Set(population.expectedCases).size !== population.expectedCases.length) {
            throw new Error(`Invalid mandatory case population: ${population.id}`);
        }
    }
    const missing = required.filter(population => !population.available || !population.fixture).map(population => population.id);
    if (!missing.length)
        throw new Error('Full verification groups are not implemented in this package revision');
    return { available: false, missing };
}
function object(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value))
        throw new Error('Malformed test event');
    return value;
}
export function assertCaseResults(expected, events) {
    if (!expected.length || new Set(expected).size !== expected.length)
        throw new Error('Empty or duplicate expected case population');
    const seen = new Set();
    let summaries = 0;
    for (const raw of events) {
        const event = object(raw);
        if (event.type === 'test:interrupted')
            throw new Error('Test execution interrupted');
        if (event.type === 'test:pass' || event.type === 'test:fail') {
            const data = object(event.data);
            const details = object(data.details);
            if (data.nesting !== 0 || details.type === 'suite' || (data.parentId !== undefined && data.parentId !== 0))
                throw new Error('Only flat leaf cases can satisfy qualification');
            if ((data.skip !== undefined && data.skip !== false) || (data.todo !== undefined && data.todo !== false))
                throw new Error('Skipped or TODO case cannot satisfy qualification');
            if (typeof data.name !== 'string' || !expected.includes(data.name))
                throw new Error(`Unexpected case: ${String(data.name)}`);
            if (seen.has(data.name))
                throw new Error(`Duplicate case: ${data.name}`);
            if (event.type === 'test:fail')
                throw new Error(`Failed case: ${data.name}: ${String(details.error)}`);
            seen.add(data.name);
        }
        if (event.type === 'test:summary') {
            const data = object(event.data);
            if (data.file !== undefined)
                continue;
            summaries++;
            const counts = object(data.counts);
            if (data.success !== true || counts.tests !== expected.length || counts.passed !== expected.length ||
                ['failed', 'cancelled', 'skipped', 'todo', 'suites'].some(name => counts[name] !== 0)) {
                throw new Error('Incomplete or unsuccessful cumulative test summary');
            }
        }
    }
    if (summaries !== 1)
        throw new Error('Missing or duplicate cumulative test summary');
    if (!seen.size || seen.size !== expected.length || expected.some(name => !seen.has(name)))
        throw new Error('Empty or missing observed case population');
    return { expected: expected.length, passed: seen.size, cases: [...expected] };
}
export function cleanTestEnvironment(extra = {}) {
    const env = { ...process.env };
    for (const name of Object.keys(env)) {
        if (/^(node_options|node_path|node_test_.*|npm_config_.*)$/i.test(name))
            delete env[name];
    }
    return { ...env, ...extra };
}
export async function runFixedFixture(file, expected, timeout = 60000) {
    const env = cleanTestEnvironment();
    const options = { files: [file], cwd: dirname(file), timeout, env, execArgv: [] };
    const events = [];
    const stream = run(options);
    for await (const event of stream)
        events.push(event);
    if (process.env.LOAM_FACTORY_EVENT_TRACE) {
        writeFileSync(process.env.LOAM_FACTORY_EVENT_TRACE, `${JSON.stringify(events, null, 2)}\n`);
    }
    return assertCaseResults(expected, events);
}
//# sourceMappingURL=verify.js.map