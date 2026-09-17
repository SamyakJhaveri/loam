// Curated-catalog conservation validator (plan NATIVE-05, D1-D16). The shipped catalog
// (assets/curated-catalog.json) is checked against the independently reviewed obligations
// (src/assets/obligations.ts). No catalog field can replace or relax an obligation: the
// obligations are the fixed semantic boundary and this module only proves the catalog is
// consistent with them. Schema shape lives in the JSON Schema (assets/curated-catalog.schema.json)
// and src/assets/schema.ts; source spans live in src/assets/units.ts; both are reused here.
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, join, relative, resolve, sep } from 'node:path';
import { assertSchemaDocument, deepEqual, isRecord, validate } from './schema.js';
import { sha256 } from './units.js';
import { OBLIGATIONS } from './obligations.js';
export class CatalogError extends Error {
    rule;
    constructor(rule, message) {
        super(`${rule}: ${message}`);
        this.rule = rule;
        this.name = 'CatalogError';
    }
}
const fail = (rule, message) => { throw new CatalogError(rule, message); };
// ---------------------------------------------------------------------------
// D11 path validators.
// ---------------------------------------------------------------------------
// A machine-readable repository/recipient path: nonempty, normalized, relative, POSIX.
export function assertRelativePath(path, label) {
    if (typeof path !== 'string' || path.length === 0)
        fail('path.invalid', `${label} is empty`);
    if (isAbsolute(path) || /^[A-Za-z]:/.test(path) || path.startsWith('/') || path.startsWith('\\'))
        fail('path.invalid', `${label} is not relative: ${path}`);
    if (path.includes('\\'))
        fail('path.invalid', `${label} contains a backslash: ${path}`);
    if (/[\x00-\x1f\x7f]/.test(path))
        fail('path.invalid', `${label} contains a control character`);
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(path))
        fail('path.invalid', `${label} looks like a URI: ${path}`);
    for (const part of path.split('/')) {
        if (part === '' || part === '.' || part === '..')
            fail('path.invalid', `${label} has an empty or relative component: ${path}`);
    }
}
// Resolve `relative` beneath `root` with real-path containment; a symlink escape throws.
export function containedPath(root, rel) {
    assertRelativePath(rel, 'recipient path');
    const realRoot = realpathSync(root);
    const target = resolve(realRoot, rel);
    // Contain the lexical path first, then the real path of the nearest existing ancestor.
    const lexical = relative(realRoot, target);
    if (lexical.startsWith('..') || isAbsolute(lexical))
        fail('path.escape', `path escapes the recipient root: ${rel}`);
    let probe = target;
    for (;;) {
        try {
            const real = realpathSync(probe);
            const contained = relative(realRoot, real);
            if (contained.startsWith('..') || isAbsolute(contained))
                fail('path.escape', `path escapes the recipient root through a link: ${rel}`);
            break;
        }
        catch (error) {
            if (error instanceof CatalogError)
                throw error;
            const parent = resolve(probe, '..');
            if (parent === probe)
                break;
            probe = parent;
        }
    }
    return target;
}
// ---------------------------------------------------------------------------
// D11 personal-path scanner. Walks every string value and every object key, decoded,
// and matches embedded home/temp/tilde paths anywhere in the string, not only at the
// start. `pattern` values (schema regex literals) are the scanner's own syntax and are
// not treated as user data.
// ---------------------------------------------------------------------------
const PERSONAL_PATH = [
    /(^|[^A-Za-z0-9_])~\/[^\s]/, // tilde home path
    /\/Users\/[^/\s]/, // macOS home
    /\/home\/[^/\s]/, // linux home
    /\/private\/tmp(\/|\b)/, // macOS operator temp
    /\/var\/folders\//, // macOS mkdtemp
    /(^|[^A-Za-z0-9_])\/tmp\/[^\s]/, // unix temp
    /(^|[^A-Za-z0-9_])[A-Za-z]:\\/, // windows drive path
];
function isPersonalPath(value) { return PERSONAL_PATH.some(re => re.test(value)); }
export function scanPersonalPaths(value, path = '$') {
    const hits = [];
    const walk = (node, where, keyContext) => {
        if (typeof node === 'string') {
            if (keyContext !== 'pattern' && isPersonalPath(node))
                hits.push({ path: where, value: node });
            return;
        }
        if (Array.isArray(node)) {
            node.forEach((item, i) => walk(item, `${where}[${i}]`, null));
            return;
        }
        if (isRecord(node)) {
            for (const [key, sub] of Object.entries(node)) {
                if (key !== 'pattern' && isPersonalPath(key))
                    hits.push({ path: `${where}.<key>`, value: key });
                walk(sub, `${where}.${key}`, key);
            }
        }
    };
    walk(value, path, null);
    return hits;
}
function assertNoPersonalPaths(value, label) {
    const hits = scanPersonalPaths(value, label);
    if (hits.length)
        fail('privacy.personal-path', `${hits.length} personal path(s), first at ${hits[0].path}: ${hits[0].value.slice(0, 60)}`);
}
// ---------------------------------------------------------------------------
// D5 required-edge closure with a visited set (repeated nodes cannot shorten it or
// cause infinite traversal).
// ---------------------------------------------------------------------------
const REQUIRED = new Set(['required-file', 'required-method', 'external-prerequisite']);
export function requiredClosure(entryId, edges) {
    const byEntry = new Map();
    for (const edge of edges) {
        const list = byEntry.get(edge.fromEntry) ?? [];
        list.push(edge);
        byEntry.set(edge.fromEntry, list);
    }
    const visited = new Set();
    const order = [];
    const stack = [entryId];
    while (stack.length) {
        const current = stack.pop();
        if (visited.has(current))
            continue;
        visited.add(current);
        if (current !== entryId)
            order.push(current);
        for (const edge of byEntry.get(current) ?? []) {
            if (REQUIRED.has(edge.relationship) && edge.to.entry !== undefined && !visited.has(edge.to.entry))
                stack.push(edge.to.entry);
        }
    }
    return order;
}
// ---------------------------------------------------------------------------
// Projections from a catalog entry to the fixed obligation shape.
// ---------------------------------------------------------------------------
function projectMapRow(row) { const { reason, ...rest } = row; void reason; return rest; }
function projectPrerequisite(prereq) {
    const projected = { id: prereq.id, type: prereq.type, name: prereq.name, verification: prereq.verification, expectedSha256: null };
    if ('path' in prereq && prereq.path !== undefined)
        projected.path = prereq.path;
    return projected;
}
function projectEntry(entry) {
    const projected = {
        id: entry.id, collection: entry.collection, kind: entry.kind, assetKind: entry.assetKind,
        source: entry.source, status: entry.status, decision: entry.preservation.decision, owner: entry.activation.owner,
        targets: entry.targets, sourceUnits: entry.sourceUnits, map: entry.preservation.map.map(projectMapRow),
        prerequisites: entry.prerequisites.map(projectPrerequisite), privateMetadata: entry.source.type === 'private-local-metadata',
    };
    if (entry.applicability !== undefined)
        projected.applicability = entry.applicability;
    // The compiled obligations also carry the reviewed phase, provider flags and attribution.
    projected.phase = entry.preservation.phase;
    projected.providers = entry.providers;
    projected.attribution = entry.attribution;
    return projected;
}
function projectEdge(entry, dep) {
    return { id: dep.id, fromEntry: entry.id, sourceUnit: dep.sourceUnit, relationship: dep.relationship, to: dep.to, disposition: dep.disposition, resolvedBy: dep.resolvedBy, replacement: dep.replacement };
}
const pick = (value, keys) => {
    const out = {};
    for (const key of keys)
        out[key] = value[key];
    return out;
};
export function loadCatalog(packageRoot) {
    const read = (name) => {
        let text;
        try {
            text = readFileSync(join(packageRoot, 'assets', name), 'utf8');
        }
        catch {
            return fail('schema.invalid', `cannot read ${name}`);
        }
        try {
            return JSON.parse(text);
        }
        catch {
            return fail('schema.invalid', `${name} is not valid JSON`);
        }
    };
    const schema = read('curated-catalog.schema.json');
    const catalog = read('curated-catalog.json');
    try {
        assertSchemaDocument(schema);
    }
    catch (error) {
        fail('schema.invalid', error instanceof Error ? error.message : String(error));
    }
    const issues = validate(schema, catalog);
    if (issues.length)
        fail('schema.invalid', `catalog violates schema: ${issues.slice(0, 3).map(i => `${i.path} [${i.keyword}] ${i.message}`).join('; ')}`);
    assertNoPersonalPaths(schema, 'schema');
    assertNoPersonalPaths(catalog, 'catalog');
    return { catalog: catalog, schema: schema };
}
// ---------------------------------------------------------------------------
// validateCatalog: compare the catalog against OBLIGATIONS. Always uses the imported
// production obligations; there is no public option to substitute them.
// ---------------------------------------------------------------------------
export function validateCatalog(catalog) {
    const obligations = OBLIGATIONS;
    assertNoPersonalPaths(catalog, 'catalog');
    // Source-revision provenance: the catalog's recorded revisions must equal the obligations'.
    // The compiled obligations carry the plan/ticket/obligations digests directly today; when the
    // generator emits a full sourceRevisions object the whole object is compared. (Finding 2.)
    assertSourceRevisions(catalog, obligations);
    // Membership: catalog entry ids equal the obligation entry ids, no duplicates, none unknown, none missing.
    const obEntries = new Map(obligations.entries.map(e => [e.id, e]));
    const seen = new Set();
    for (const entry of catalog.entries) {
        if (seen.has(entry.id))
            fail('membership.duplicate', `duplicate entry id ${entry.id}`);
        seen.add(entry.id);
        if (!obEntries.has(entry.id))
            fail('membership.unknown', `entry ${entry.id} is not an obligation`);
    }
    for (const id of obEntries.keys())
        if (!seen.has(id))
            fail('membership.missing', `entry ${id} is missing from the catalog`);
    // Variant collapse is checked before the per-entry projection so a collapsed variant
    // is reported as variant.collapsed rather than a generic source/projection difference.
    assertVariantsDistinct(catalog, obligations);
    // Target and support sets used by cross-field checks.
    const targetIds = new Set(catalog.targets.map(t => t.id));
    const entryIds = seen;
    const privateIds = new Set(obligations.privateMetadata.map(row => row.id));
    for (const entry of catalog.entries) {
        const obligation = obEntries.get(entry.id);
        // Machine paths in the entry must be relative and normalized.
        if (typeof entry.source.path === 'string')
            assertRelativePath(entry.source.path, `source path of ${entry.id}`);
        for (const prereq of entry.prerequisites)
            if (prereq.path !== undefined)
                assertRelativePath(prereq.path, `prerequisite path of ${prereq.id}`);
        // Activation is never claimed and status is never promoted away from the obligation.
        if (entry.activation.activated !== false)
            fail('activation.claimed', `${entry.id} claims activation`);
        if (entry.status !== obligation.status)
            fail('status.promoted', `${entry.id} status ${entry.status} differs from ${obligation.status}`);
        // Preservation phase is `assessed` for every NATIVE-05 entry; nothing is implemented yet. When
        // the generator emits `phase` into the obligation it is also compared for equality. (Finding 2.)
        if (entry.preservation.phase !== 'assessed')
            fail('phase.promoted', `${entry.id} preservation phase ${entry.preservation.phase} is not assessed`);
        if (typeof obligation.phase === 'string' && obligation.phase !== entry.preservation.phase)
            fail('phase.promoted', `${entry.id} preservation phase differs from the obligation`);
        // D2a private-session records: exact typed null/empty shape, no capability, unit or resolving edge.
        if (privateIds.has(entry.id) || entry.source.type === 'private-local-metadata' || obligation.privateMetadata) {
            if (!privateIds.has(entry.id))
                fail('source.private-metadata', `${entry.id} uses private metadata identity but is not an allowlisted D2a record`);
            if (entry.source.type !== 'private-local-metadata')
                fail('source.private-metadata', `${entry.id} is a D2a record without private-local-metadata identity`);
            if (entry.assetKind !== 'advice')
                fail('source.private-metadata', `${entry.id} D2a assetKind must be advice`);
            if (entry.providers !== null || entry.declaredTools !== null || entry.declaredServices !== null || entry.sideEffects !== null)
                fail('source.private-metadata', `${entry.id} D2a record asserts capabilities`);
            // Attribution may cite the tracked inventory but never asserts an author or license (plan D2a).
            const attribution = isRecord(entry.attribution) ? entry.attribution : {};
            if (attribution.author !== null || attribution.license !== null)
                fail('source.private-metadata', `${entry.id} D2a record asserts an author or license`);
            if (entry.sourceUnits.length !== 0 || entry.preservation.map.length !== 0)
                fail('unit.private-metadata', `${entry.id} D2a record carries source units or a map`);
            if (entry.targets.length !== 0 || entry.dependencies.length !== 0 || entry.prerequisites.length !== 0)
                fail('edge.private-resolver', `${entry.id} D2a record carries a target, edge or prerequisite`);
        }
        // Source identity: no empty digest, exact obligation identity.
        if (entry.source.sha256 === '')
            fail('source.digest-empty', `${entry.id} has an empty source digest`);
        if (!deepEqual(entry.source, obligation.source))
            fail('source.identity', `${entry.id} source identity differs from the obligation`);
        // Source units are exactly the obligation's.
        if (!deepEqual(entry.sourceUnits, obligation.sourceUnits))
            fail('unit.mismatch', `${entry.id} source units differ from the obligation`);
        // Map rows reference real units and real targets; no title-only substitute on a body-backed entry.
        const unitIds = new Set(entry.sourceUnits.map(u => u.id));
        for (const row of entry.preservation.map) {
            if (!unitIds.has(row.unit))
                fail('map.missing-unit', `${entry.id} map row references unknown unit ${row.unit}`);
            if (typeof row.target === 'string' && !targetIds.has(row.target))
                fail('map.unknown-target', `${entry.id} map row references unknown target ${row.target}`);
        }
        const bodyBacked = entry.sourceUnits.length > 0;
        const mapped = entry.preservation.map.filter(row => typeof row.target === 'string' || (typeof row.section === 'string' && row.exclude === undefined));
        if (bodyBacked) {
            if (entry.preservation.map.length === 0)
                fail('map.title-only', `${entry.id} has an empty map on a body-backed entry`);
            if (mapped.length > 0 && mapped.every(row => row.section === entry.name))
                fail('map.title-only', `${entry.id} map is title-only`);
        }
        // Successor targets exist.
        for (const target of entry.targets)
            if (!targetIds.has(target))
                fail('target.unknown', `${entry.id} references unknown target ${target}`);
        // Snapshot provider applicability is fixed.
        if (obligation.applicability !== undefined && entry.applicability !== obligation.applicability)
            fail('provider.relabeled', `${entry.id} applicability ${String(entry.applicability)} differs from ${obligation.applicability}`);
        // Provider flags must be consistent with the source applicability: claude=>(claude,!codex),
        // codex=>(!claude,codex), shared=>(claude,codex). Only snapshots carry applicability. (Finding 2.)
        if (obligation.applicability !== undefined && !providerConsistent(obligation.applicability, entry.providers)) {
            fail('provider.mismatch', `${entry.id} provider flags are inconsistent with applicability ${obligation.applicability}`);
        }
        // When the compiled obligations carry the reviewed provider flags and attribution, the catalog must equal them.
        if (obligation.providers !== undefined && !deepEqual(obligation.providers, entry.providers))
            fail('provider.mismatch', `${entry.id} provider flags differ from the obligation`);
        if (obligation.attribution !== undefined && !deepEqual(obligation.attribution, entry.attribution))
            fail('attribution.mismatch', `${entry.id} attribution differs from the obligation`);
        // Prerequisites project to the obligation.
        if (!deepEqual(entry.prerequisites.map(projectPrerequisite), obligation.prerequisites))
            fail('prerequisite.mismatch', `${entry.id} prerequisites differ from the obligation`);
        // Full invariant projection is the backstop; anything left is a decision/owner/kind change.
        const projection = projectEntry(entry);
        if (!deepEqual(projection, obligation)) {
            const projectionRecord = projection;
            const obligationRecord = obligation;
            const field = ['collection', 'kind', 'assetKind', 'decision', 'owner', 'applicability'].find(k => !deepEqual(projectionRecord[k], obligationRecord[k])) ?? 'projection';
            fail('source.identity', `${entry.id} invariant projection differs at ${field}`);
        }
    }
    // Edges reconstructed from entry dependencies, fromEntry restored, must equal the obligations
    // exactly. Duplicate edge ids are rejected before any lookup map is built, so a duplicated
    // dependency (an external-destination one that the inverse index never sees) cannot slip through
    // a map that would silently dedupe it. (Finding 3.)
    const edges = [];
    const edgeSeen = new Set();
    for (const entry of catalog.entries)
        for (const dep of entry.dependencies) {
            if (edgeSeen.has(dep.id))
                fail('membership.duplicate', `duplicate edge id ${dep.id}`);
            edgeSeen.add(dep.id);
            edges.push(projectEdge(entry, dep));
        }
    const obEdges = new Map(obligations.edges.map(e => [e.id, e]));
    const catEdges = new Map(edges.map(e => [e.id, e]));
    for (const edge of edges) {
        if (!obEdges.has(edge.id))
            fail('edge.extra', `edge ${edge.id} is not an obligation`);
        // A required edge may never be resolved by a private-metadata record.
        if (edge.to.entry !== undefined && privateIds.has(edge.to.entry) && edge.disposition === 'retained-resolved')
            fail('edge.private-resolver', `edge ${edge.id} is resolved by a D2a record`);
        if (edge.resolvedBy && typeof edge.resolvedBy.target === 'string' && privateIds.has(edge.resolvedBy.target))
            fail('edge.private-resolver', `edge ${edge.id} resolvedBy names a D2a record`);
    }
    for (const [id, obEdge] of obEdges) {
        const edge = catEdges.get(id);
        if (!edge)
            fail('edge.missing', `edge ${id} is missing from the catalog`);
        if (edge.relationship !== obEdge.relationship)
            fail('edge.relationship', `edge ${id} relationship ${edge.relationship} differs from ${obEdge.relationship}`);
        if (!deepEqual(edge.to, obEdge.to))
            fail('edge.retargeted', `edge ${id} target differs from the obligation`);
        if (!deepEqual(edge, obEdge))
            fail('edge.retargeted', `edge ${id} differs from the obligation`);
    }
    // referencedBy equals the inverse index recomputed from the edges.
    const inverse = new Map();
    for (const edge of edges)
        if (edge.to.entry !== undefined) {
            const list = inverse.get(edge.to.entry) ?? [];
            list.push(edge.id);
            inverse.set(edge.to.entry, list);
        }
    for (const entry of catalog.entries) {
        const expected = (inverse.get(entry.id) ?? []).slice().sort();
        const actual = entry.referencedBy.slice().sort();
        if (!deepEqual(actual, expected))
            fail('edge.inverse', `${entry.id} referencedBy is not the recomputed inverse index`);
        void entryIds;
    }
    // Targets, wrappers and dispositions equal the obligations exactly. Each id set is compared in
    // both directions and duplicate ids are rejected before the lookup maps are built, so a repeated
    // id cannot conceal a missing member behind a matching count. (Finding 3.)
    const obTargets = new Map(obligations.targets.map(t => [t.id, t]));
    if (catalog.targets.length !== obligations.targets.length)
        fail('target.unknown', `catalog has ${catalog.targets.length} targets, obligations have ${obligations.targets.length}`);
    const targetSeen = new Set();
    for (const target of catalog.targets) {
        if (targetSeen.has(target.id))
            fail('membership.duplicate', `duplicate target id ${target.id}`);
        targetSeen.add(target.id);
        assertRelativePath(target.path, `target path of ${target.id}`);
        const obTarget = obTargets.get(target.id);
        if (!obTarget)
            fail('target.unknown', `target ${target.id} is not an obligation`);
        if (target.path !== obTarget.path)
            fail('target.path', `target ${target.id} path ${target.path} differs from ${obTarget.path}`);
        if (target.delivery !== obTarget.delivery)
            fail('target.delivery', `target ${target.id} delivery ${target.delivery} differs from ${obTarget.delivery}`);
        if (!deepEqual(target, obTarget))
            fail('target.unknown', `target ${target.id} differs from the obligation`);
    }
    for (const id of obTargets.keys())
        if (!targetSeen.has(id))
            fail('target.unknown', `obligation target ${id} is missing from the catalog`);
    if (catalog.nativeWrappers.length !== obligations.nativeWrappers.length)
        fail('wrapper.set', `catalog has ${catalog.nativeWrappers.length} wrappers, obligations have ${obligations.nativeWrappers.length}`);
    const obWrappers = new Map(obligations.nativeWrappers.map(w => [w.id, w]));
    const wrapperSeen = new Set();
    for (const wrapper of catalog.nativeWrappers) {
        if (wrapperSeen.has(wrapper.id))
            fail('membership.duplicate', `duplicate wrapper id ${wrapper.id}`);
        wrapperSeen.add(wrapper.id);
        const obWrapper = obWrappers.get(wrapper.id);
        if (!obWrapper)
            fail('wrapper.set', `wrapper ${wrapper.id} is not an obligation`);
        if (!deepEqual(wrapper, obWrapper))
            fail('wrapper.row', `wrapper ${wrapper.id} differs from the obligation`);
    }
    for (const id of obWrappers.keys())
        if (!wrapperSeen.has(id))
            fail('wrapper.set', `obligation wrapper ${id} is missing from the catalog`);
    assertDisposition(catalog.selectionAliases, obligations.dispositions.selectionAliases, ['inventory', 'kind', 'path', 'project', 'sha256', 'snapshot']);
    assertDisposition(catalog.notSelected, obligations.dispositions.notSelected, ['inventory', 'kind', 'path', 'project', 'sha256']);
    assertDisposition(catalog.pluginReferences, obligations.dispositions.pluginReferences, ['declarationSource', 'enabled', 'name', 'project']);
    return {
        entries: catalog.entries.length, targets: catalog.targets.length, edges: edges.length, wrappers: catalog.nativeWrappers.length,
        privateMetadata: obligations.privateMetadata.length,
        dispositions: { aliases: catalog.selectionAliases.length, notSelected: catalog.notSelected.length, pluginReferences: catalog.pluginReferences.length },
    };
}
function assertDisposition(rows, obligation, keys) {
    if (rows.length !== obligation.length)
        fail('disposition.count', `disposition set has ${rows.length} rows, obligations have ${obligation.length}`);
    const projected = rows.map(row => pick(row, keys));
    if (!deepEqual(projected, obligation))
        fail('disposition.set', 'disposition set differs from the obligations');
}
function launchKeys(entry) {
    return entry.preservation.map.map(row => (typeof row.section === 'string' ? row.section : '')).filter(section => /^launch-/.test(section));
}
function assertVariantsDistinct(catalog, obligations) {
    const claude = catalog.entries.find(e => e.id === 'snapshot:distbench-claude-critique-swarm');
    const codex = catalog.entries.find(e => e.id === 'snapshot:distbench-codex-critique-swarm');
    if (!claude || !codex)
        return;
    const claudeDigest = claude.source.sha256;
    const codexDigest = codex.source.sha256;
    if (typeof claudeDigest !== 'string' || claudeDigest === codexDigest)
        fail('variant.collapsed', 'critique snapshot variants share a source digest');
    const claudeLaunch = new Set(launchKeys(claude));
    const codexLaunch = new Set(launchKeys(codex));
    if (claudeLaunch.size === 0 || codexLaunch.size === 0)
        fail('variant.collapsed', 'critique snapshot variant lost its launch/fallback section key');
    if ([...claudeLaunch].some(key => codexLaunch.has(key)))
        fail('variant.collapsed', 'critique snapshot variants share a launch/fallback section key');
    void obligations;
}
// Provider flags are consistent with source applicability. `shared` asserts both providers,
// a single provider asserts itself true and the other false. (Finding 2.)
function providerConsistent(applicability, providers) {
    if (!isRecord(providers))
        return false;
    const claude = providers.claude === true;
    const codex = providers.codex === true;
    if (typeof providers.claude !== 'boolean' || typeof providers.codex !== 'boolean')
        return false;
    if (applicability === 'claude')
        return claude && !codex;
    if (applicability === 'codex')
        return !claude && codex;
    if (applicability === 'shared')
        return claude && codex;
    return false;
}
// The catalog's recorded source revisions must equal the obligations'. When the generator emits a
// full sourceRevisions object it is compared whole; until then the plan/ticket/obligations digests
// that the compiled obligations already carry are compared. (Finding 2.)
function assertSourceRevisions(catalog, obligations) {
    const rev = catalog.sourceRevisions;
    if (!isRecord(rev))
        fail('sourceRevisions.mismatch', 'catalog sourceRevisions is not an object');
    const obRev = obligations.sourceRevisions;
    if (isRecord(obRev)) {
        if (!deepEqual(rev, obRev))
            fail('sourceRevisions.mismatch', 'catalog sourceRevisions differ from the obligations');
        return;
    }
    const digests = [
        ['planSha256', obligations.planSha256],
        ['ticketSha256', obligations.ticketSha256],
        ['obligationsSha256', obligations.obligationsSha256],
    ];
    for (const [key, expected] of digests) {
        if (rev[key] !== expected)
            fail('sourceRevisions.mismatch', `catalog sourceRevisions.${key} differs from the obligations`);
    }
}
// ---------------------------------------------------------------------------
// resolveEntry: the lower-level readiness helper. It never certifies a production entry; it binds a
// candidate entry to a trusted expected-entry contract under a temporary recipient root and reads
// the required bodies. `activated` is always false; `activatable` is true only when the candidate
// matches the trusted contract, is not a private-session record, and every required body, support
// file and file prerequisite is present with the expected digest. The candidate is the untrusted
// input; the expected contract is fixed, so negatives mutate the candidate or the filesystem, never
// the contract. (Plan D4; finding 4.)
// ---------------------------------------------------------------------------
export function resolveEntry(entry, expected, recipientRoot) {
    const reasons = [];
    const digestOf = (path) => {
        let abs;
        try {
            abs = containedPath(recipientRoot, path);
        }
        catch (error) {
            reasons.push(error instanceof CatalogError ? `path ${path} escapes the recipient root` : `path ${path} is invalid`);
            return null;
        }
        try {
            if (!lstatSync(abs).isFile()) {
                reasons.push(`missing file ${path}`);
                return null;
            }
        }
        catch {
            reasons.push(`missing file ${path}`);
            return null;
        }
        return sha256(readFileSync(abs));
    };
    // A private-session record is never activatable, whatever contract it is paired with.
    const isPrivate = entry.source?.type === 'private-local-metadata' || entry.kind === 'private-session-record';
    if (isPrivate)
        reasons.push('private-session record is never activatable');
    // Bind the candidate identity, status, activation, prerequisites and blockers to the trusted
    // contract. A candidate that differs from the contract cannot be admitted.
    if (entry.id !== expected.id)
        reasons.push(`candidate id ${entry.id} does not match the expected contract ${expected.id}`);
    if (entry.status !== expected.status)
        reasons.push(`candidate status ${entry.status} does not match the expected contract status ${expected.status}`);
    if (!entry.activation || entry.activation.activated !== false)
        reasons.push('candidate claims activation');
    const candBlockers = Array.isArray(entry.blockers) ? entry.blockers : [];
    if (!sameStringSet(candBlockers, expected.blockers))
        reasons.push('candidate blockers differ from the expected contract');
    if (!prerequisitesBind(entry.prerequisites, expected.prerequisites))
        reasons.push('candidate prerequisites differ from the expected contract');
    // The candidate's own declared file-prerequisite paths must stay contained beneath the recipient
    // root, so a candidate that declares an escaping path is refused.
    for (const prereq of entry.prerequisites ?? []) {
        if (prereq.type === 'file' && typeof prereq.path === 'string') {
            try {
                containedPath(recipientRoot, prereq.path);
            }
            catch {
                reasons.push(`candidate prerequisite path ${prereq.path} escapes the recipient root`);
            }
        }
        if ((prereq.type === 'command' || prereq.type === 'service') && prereq.verification !== 'verified')
            reasons.push(`candidate prerequisite ${prereq.name ?? prereq.id} is unverified`);
    }
    if (!expected.qualified)
        reasons.push('expected contract is not qualified');
    for (const target of expected.targets) {
        const digest = digestOf(target.path);
        if (digest !== null && digest !== target.sha256)
            reasons.push(`target ${target.path} digest mismatch`);
    }
    for (const prereq of expected.prerequisites) {
        if (prereq.type === 'file') {
            const digest = digestOf(prereq.path ?? '');
            if (digest !== null && digest !== (prereq.expectedSha256 ?? null))
                reasons.push(`prerequisite ${prereq.path ?? prereq.id} digest mismatch`);
        }
        else if (prereq.verification !== 'verified')
            reasons.push(`prerequisite ${prereq.name ?? prereq.id ?? prereq.type} is unverified`);
    }
    for (const blocker of expected.blockers)
        reasons.push(`blocker: ${blocker}`);
    // Required-edge closure over the candidate's own declared edges, with a visited set so repeated
    // and cyclic required edges terminate. Any unresolved required edge blocks activation.
    const candidateEdges = (entry.dependencies ?? []).map(dep => projectEdge(entry, dep));
    requiredClosure(entry.id, candidateEdges); // terminates on repeats/cycles; the return is unused here.
    for (const edge of candidateEdges) {
        if (!REQUIRED.has(edge.relationship))
            continue;
        const resolved = edge.disposition === 'retained-resolved' && edge.resolvedBy !== null && (typeof edge.resolvedBy.target === 'string' || typeof edge.resolvedBy.prerequisite === 'string');
        if (!resolved)
            reasons.push(`required edge ${edge.id} is unresolved`);
    }
    return { activatable: reasons.length === 0 && !isPrivate, activated: false, status: expected.status, reasons };
}
// Two string collections are equal as sets (order-independent, deduplicated).
function sameStringSet(a, b) {
    const sa = new Set(a);
    const sb = new Set(b);
    if (sa.size !== sb.size)
        return false;
    for (const value of sa)
        if (!sb.has(value))
            return false;
    return true;
}
// A candidate's prerequisites bind to the trusted contract when the two carry the same prerequisite
// identities (id, type, name, path, verification) regardless of order. The digest of a file
// prerequisite lives in the trusted contract, not the candidate record.
function prerequisitesBind(candidate, expected) {
    const key = (p) => [p.id ?? '', p.type ?? '', p.name ?? '', p.path ?? '', p.verification ?? ''].join('|');
    const ca = new Set((candidate ?? []).map(key));
    const cb = new Set(expected.map(key));
    if (ca.size !== cb.size)
        return false;
    for (const value of ca)
        if (!cb.has(value))
            return false;
    return true;
}
// ---------------------------------------------------------------------------
// Recipient delivery: derive the recipient root from the package location and, for every target
// whose delivery is present-unqualified or verified, read the body at the contained recipient path
// and require the exact expectedSha256. Planned targets are never read. (Plan D4/D16; finding 5.)
// ---------------------------------------------------------------------------
export function recipientRootOf(packageRoot) { return resolve(packageRoot, '..', '..'); }
export function checkRecipientDelivery(catalog, recipientRoot) {
    let checked = 0;
    for (const target of catalog.targets) {
        if (target.delivery !== 'present-unqualified' && target.delivery !== 'verified')
            continue;
        let abs;
        try {
            abs = containedPath(recipientRoot, target.path);
        }
        catch {
            return fail('delivery.missing', `delivered target ${target.id} path ${target.path} escapes the recipient root`);
        }
        let bytes;
        try {
            if (!lstatSync(abs).isFile())
                return fail('delivery.missing', `delivered target ${target.id} body at ${target.path} is not a regular file`);
            bytes = readFileSync(abs);
        }
        catch (error) {
            if (error instanceof CatalogError)
                throw error;
            return fail('delivery.missing', `delivered target ${target.id} body is missing at ${target.path}`);
        }
        if (sha256(bytes) !== target.expectedSha256)
            fail('delivery.digest', `delivered target ${target.id} body digest differs from expectedSha256`);
        checked++;
    }
    return { checked };
}
// obligations.ts imports only the Obligations type from this module (erased at runtime),
// so importing the OBLIGATIONS value here creates no runtime import cycle.
export { OBLIGATIONS };
export function relativePosix(root, target) { return relative(root, target).split(sep).join('/'); }
//# sourceMappingURL=catalog.js.map