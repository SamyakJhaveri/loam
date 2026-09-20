// Curated-catalog conservation validator (plan NATIVE-05, D1-D16). The shipped catalog
// (assets/curated-catalog.json) is proved consistent with itself: every invariant checked here is
// one the catalog carries in its own fields (memberships, edge and wrapper resolution, the
// preservation maps, activation honesty, delivery digests proven by recipient bytes). Source
// provenance against the Loam working tree, and recipient integrity, live elsewhere: the Loam-only
// provenance gate (bin/tests/factory-catalog-provenance.test.mjs) re-hashes bodies and re-extracts
// units against the tree, and the release manifest, admission seal and doctor guard the recipient.
// Schema shape lives in the JSON Schema (assets/curated-catalog.schema.json) and src/assets/schema.ts;
// source spans live in src/assets/units.ts; both are reused here.
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, join, relative, resolve, sep } from 'node:path';
import { assertSchemaDocument, deepEqual, isRecord, validate } from './schema.js';
import { sha256 } from './units.js';
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
    /(^|[^A-Za-z0-9_])~([A-Za-z_][A-Za-z0-9_.-]*)?\/[^\s]/, // tilde home: bare ~/ or named-user ~operator/
    /\/Users\/[^/\s]/i, // macOS home (case-insensitive: /users too)
    /\/home\/[^/\s]/i, // linux home (case-insensitive)
    /\/private\/tmp(\/|\b)/, // macOS operator temp (symlink form)
    /\/private\/var(\/|\b)/, // macOS resolved private/var temp root
    /\/var\/folders\//, // macOS mkdtemp
    /\/var\/tmp(\/|\b)/, // unix persistent temp
    /(^|[^A-Za-z0-9_])\/tmp\/[^\s]/, // unix temp
    /(^|[^A-Za-z0-9_])[A-Za-z]:\\/, // windows drive path
];
function isPersonalPath(value) { return PERSONAL_PATH.some(re => re.test(value)); }
export function scanPersonalPaths(value, path = '$') {
    const hits = [];
    // The `pattern`-key exemption (schema regex literals are the scanner's own syntax, not user data)
    // applies only when scanning the schema document itself. In any other document a `pattern` key is
    // ordinary data and is scanned like any other value. (finding 7)
    const patternExempt = path === 'schema';
    const walk = (node, where, keyContext) => {
        if (typeof node === 'string') {
            if (!(patternExempt && keyContext === 'pattern') && isPersonalPath(node))
                hits.push({ path: where, value: node });
            return;
        }
        if (Array.isArray(node)) {
            node.forEach((item, i) => walk(item, `${where}[${i}]`, null));
            return;
        }
        if (isRecord(node)) {
            for (const [key, sub] of Object.entries(node)) {
                if (!(patternExempt && key === 'pattern') && isPersonalPath(key))
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
// Flatten a per-entry dependency into an edge with its originating entry restored. The catalog has
// no top-level edges array; validateCatalog, the provenance gate and requiredClosure all consume the
// flattened list this produces.
// ---------------------------------------------------------------------------
export function projectEdge(entry, dep) {
    return { id: dep.id, fromEntry: entry.id, sourceUnit: dep.sourceUnit, relationship: dep.relationship, to: dep.to, disposition: dep.disposition, resolvedBy: dep.resolvedBy, replacement: dep.replacement };
}
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
// The eight recognized entry statuses (curated-catalog.schema.json). No entry is ever `available`:
// qualification never activates a method, so the validator refuses that value outright.
const KNOWN_STATUS = new Set(['source-preserved', 'shipped-pending-adaptation', 'blocked-missing-support', 'available', 'not-selected', 'local-only', 'declared-unread', 'rejected']);
// The seven provenance keys the catalog records under sourceRevisions. The catalog carries this
// object as its own recorded provenance; ticketSha256 is anchored to the archived ticket in the
// Loam-only provenance gate, not here.
const SOURCE_REVISION_KEYS = ['baseCommit', 'evidence', 'pocockPin', 'planSha256', 'ticketSha256', 'privateDispositionAmendmentSha256', 'obligationsSha256'];
// ---------------------------------------------------------------------------
// validateCatalog: prove the shipped catalog consistent with itself. Every rule reads only catalog
// fields; nothing is compared against a second copy of the catalog. Source provenance against the
// working tree runs in the Loam-only provenance gate, and recipient integrity in the release
// manifest, admission seal and doctor.
// ---------------------------------------------------------------------------
export function validateCatalog(catalog) {
    assertNoPersonalPaths(catalog, 'catalog');
    // Source-revision provenance: the catalog's recorded sourceRevisions is an object carrying the
    // seven recognized keys. Its ticketSha256 is anchored to the archived ticket in the provenance gate.
    assertSourceRevisions(catalog);
    // Membership: no duplicate entry id.
    const seen = new Set();
    for (const entry of catalog.entries) {
        if (seen.has(entry.id))
            fail('membership.duplicate', `duplicate entry id ${entry.id}`);
        seen.add(entry.id);
    }
    // Variant collapse is checked before the per-entry loop so a collapsed variant is reported as
    // variant.collapsed rather than a generic difference.
    assertVariantsDistinct(catalog);
    // Sets used by the resolution checks.
    const entryIds = seen;
    const targetIds = new Set(catalog.targets.map(t => t.id));
    const prereqIds = new Set(catalog.entries.flatMap(e => e.prerequisites.map(p => p.id)));
    // The private-metadata allowlist is the entries whose source identity is private-local-metadata;
    // there is no separate table to check them against.
    const privateIds = new Set(catalog.entries.filter(e => e.source.type === 'private-local-metadata').map(e => e.id));
    for (const entry of catalog.entries) {
        // Machine paths in the entry must be relative and normalized.
        if (typeof entry.source.path === 'string')
            assertRelativePath(entry.source.path, `source path of ${entry.id}`);
        for (const prereq of entry.prerequisites)
            if (prereq.path !== undefined)
                assertRelativePath(prereq.path, `prerequisite path of ${prereq.id}`);
        // Activation is never claimed; status is one of the recognized values and never `available`.
        if (entry.activation.activated !== false)
            fail('activation.claimed', `${entry.id} claims activation`);
        if (!KNOWN_STATUS.has(entry.status))
            fail('status.promoted', `${entry.id} has an unrecognized status ${entry.status}`);
        if (entry.status === 'available')
            fail('status.promoted', `${entry.id} is promoted to available`);
        // Preservation phase is `assessed` for every NATIVE-05 entry; nothing is implemented yet.
        if (entry.preservation.phase !== 'assessed')
            fail('phase.promoted', `${entry.id} preservation phase ${entry.preservation.phase} is not assessed`);
        // D2a private-session records: exact typed null/empty shape, no capability, unit or resolving edge.
        if (entry.source.type === 'private-local-metadata') {
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
        // Source identity: no empty digest. The exact source bytes are re-hashed against the tree by the
        // provenance gate, not compared to a second copy here.
        if (entry.source.sha256 === '')
            fail('source.digest-empty', `${entry.id} has an empty source digest`);
        // Map rows reference real units and real targets; no title-only substitute on a body-backed entry.
        const unitIds = new Set(entry.sourceUnits.map(u => u.id));
        for (const row of entry.preservation.map) {
            if (!unitIds.has(row.unit))
                fail('map.missing-unit', `${entry.id} map row references unknown unit ${row.unit}`);
            if (typeof row.target === 'string' && !targetIds.has(row.target))
                fail('map.unknown-target', `${entry.id} map row references unknown target ${row.target}`);
            // A catalog exclusion must state why (D7): an `exclude` row carries a non-whitespace reason.
            if (row.exclude !== undefined && (typeof row.reason !== 'string' || row.reason.trim() === ''))
                fail('map.exclusion-reason', `${entry.id} exclusion map row for unit ${row.unit} has no non-empty reason`);
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
        // Provider flags are consistent with the source applicability: claude=>(claude,!codex),
        // codex=>(!claude,codex), shared=>(claude,codex). Only snapshots carry applicability.
        if (entry.applicability !== undefined && !providerConsistent(entry.applicability, entry.providers)) {
            fail('provider.mismatch', `${entry.id} provider flags are inconsistent with applicability ${entry.applicability}`);
        }
    }
    // Edges reconstructed from entry dependencies, fromEntry restored. Duplicate edge ids are rejected
    // before any lookup map is built. Each edge must resolve: its destination names an existing entry,
    // target, prerequisite or an external reference, a retained-resolved edge's resolvedBy names an
    // existing target or prerequisite, and a replacement names an existing target. A private-metadata record may never resolve a required edge.
    const edges = [];
    const edgeSeen = new Set();
    for (const entry of catalog.entries)
        for (const dep of entry.dependencies) {
            if (edgeSeen.has(dep.id))
                fail('membership.duplicate', `duplicate edge id ${dep.id}`);
            edgeSeen.add(dep.id);
            edges.push(projectEdge(entry, dep));
        }
    for (const edge of edges) {
        const to = edge.to;
        const resolved = (to.entry !== undefined && entryIds.has(to.entry))
            || (to.target !== undefined && targetIds.has(to.target))
            || (to.prerequisite !== undefined && prereqIds.has(to.prerequisite))
            || to.external !== undefined;
        if (!resolved)
            fail('edge.unresolved', `edge ${edge.id} does not resolve to an existing entry, target, prerequisite or external reference`);
        if (edge.resolvedBy) {
            if (typeof edge.resolvedBy.target === 'string' && !targetIds.has(edge.resolvedBy.target))
                fail('edge.unresolved', `edge ${edge.id} resolvedBy names unknown target ${edge.resolvedBy.target}`);
            if (typeof edge.resolvedBy.prerequisite === 'string' && !prereqIds.has(edge.resolvedBy.prerequisite))
                fail('edge.unresolved', `edge ${edge.id} resolvedBy names unknown prerequisite ${edge.resolvedBy.prerequisite}`);
        }
        if (edge.replacement && typeof edge.replacement.target === 'string' && !targetIds.has(edge.replacement.target))
            fail('edge.unresolved', `edge ${edge.id} replacement names unknown target ${edge.replacement.target}`);
        // A required edge may never be resolved by a private-metadata record.
        if (edge.to.entry !== undefined && privateIds.has(edge.to.entry) && edge.disposition === 'retained-resolved')
            fail('edge.private-resolver', `edge ${edge.id} is resolved by a D2a record`);
        if (edge.resolvedBy && typeof edge.resolvedBy.target === 'string' && privateIds.has(edge.resolvedBy.target))
            fail('edge.private-resolver', `edge ${edge.id} resolvedBy names a D2a record`);
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
    }
    // Targets: unique ids, a relative path, a known delivery state with a digest shape proven by bytes
    // in checkRecipientDelivery (plan D1), and declared sectionKeys that equal the union of the sections
    // the preservation-map rows aim at this target. No obligation-owned field is compared to a copy.
    const mappedSections = new Map();
    for (const entry of catalog.entries)
        for (const row of entry.preservation.map) {
            if (typeof row.target === 'string' && typeof row.section === 'string') {
                const set = mappedSections.get(row.target) ?? new Set();
                set.add(row.section);
                mappedSections.set(row.target, set);
            }
        }
    const deliveryStates = new Set(['planned', 'present-unqualified', 'verified']);
    const targetSeen = new Set();
    for (const target of catalog.targets) {
        if (targetSeen.has(target.id))
            fail('membership.duplicate', `duplicate target id ${target.id}`);
        targetSeen.add(target.id);
        assertRelativePath(target.path, `target path of ${target.id}`);
        // Delivery truth: a known delivery state, with expectedSha256 null exactly when the body is still
        // planned and otherwise a 64-character lowercase hex digest that checkRecipientDelivery verifies
        // against the recipient body. (Plan D1.)
        if (!deliveryStates.has(target.delivery))
            fail('target.delivery', `target ${target.id} has unknown delivery ${target.delivery}`);
        if (target.delivery === 'planned') {
            if (target.expectedSha256 !== null)
                fail('target.delivery', `planned target ${target.id} carries a digest`);
        }
        else if (typeof target.expectedSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(target.expectedSha256)) {
            fail('target.delivery', `delivered target ${target.id} lacks a 64-character lowercase hex digest`);
        }
        // Declared section keys equal the union of the map-row sections aimed at this target.
        const declared = new Set(target.sectionKeys);
        const union = mappedSections.get(target.id) ?? new Set();
        if (declared.size !== union.size || [...declared].some(key => !union.has(key))) {
            fail('target.section-keys', `target ${target.id} section keys are not the union of its mapped sections`);
        }
    }
    // Wrappers: unique ids; every wrapper resolves. wrappedSource names an existing entry; method and
    // sharedTarget name existing targets; each prerequisiteEdge names an existing edge; the payload path
    // sits under the provider's own native directory.
    const wrapperSeen = new Set();
    for (const wrapper of catalog.nativeWrappers) {
        if (wrapperSeen.has(wrapper.id))
            fail('membership.duplicate', `duplicate wrapper id ${wrapper.id}`);
        wrapperSeen.add(wrapper.id);
        if (!entryIds.has(wrapper.wrappedSource))
            fail('wrapper.row', `wrapper ${wrapper.id} wraps unknown source ${wrapper.wrappedSource}`);
        if (!targetIds.has(wrapper.method))
            fail('wrapper.row', `wrapper ${wrapper.id} names unknown method target ${wrapper.method}`);
        if (!targetIds.has(wrapper.sharedTarget))
            fail('wrapper.row', `wrapper ${wrapper.id} names unknown shared target ${wrapper.sharedTarget}`);
        for (const edgeId of wrapper.prerequisiteEdges)
            if (!edgeSeen.has(edgeId))
                fail('wrapper.row', `wrapper ${wrapper.id} names unknown prerequisite edge ${edgeId}`);
        if (!wrapper.payloadPath.startsWith(`assets/native/${wrapper.provider}/`))
            fail('wrapper.row', `wrapper ${wrapper.id} payload path is not under its provider directory`);
    }
    return {
        entries: catalog.entries.length, targets: catalog.targets.length, edges: edges.length, wrappers: catalog.nativeWrappers.length,
        privateMetadata: privateIds.size,
        dispositions: { aliases: catalog.selectionAliases.length, notSelected: catalog.notSelected.length, pluginReferences: catalog.pluginReferences.length },
    };
}
function launchKeys(entry) {
    return entry.preservation.map.map(row => (typeof row.section === 'string' ? row.section : '')).filter(section => /^launch-/.test(section));
}
function assertVariantsDistinct(catalog) {
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
// The catalog's recorded source revisions are an object carrying the seven recognized provenance
// keys. The ticketSha256 value is anchored to the archived ticket by the Loam-only provenance gate;
// the catalog cannot change and its schema is closed, so no further key is added here.
export function assertSourceRevisions(catalog) {
    const rev = catalog.sourceRevisions;
    if (!isRecord(rev))
        fail('sourceRevisions.mismatch', 'catalog sourceRevisions is not an object');
    for (const key of SOURCE_REVISION_KEYS)
        if (!(key in rev))
            fail('sourceRevisions.mismatch', `catalog sourceRevisions is missing ${key}`);
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
    // Digest of a required support body without recording a generic reason, so the required-edge loop
    // owns the message and names the failing edge id. Returns null when the file is absent or escapes.
    const supportDigest = (path) => {
        let abs;
        try {
            abs = containedPath(recipientRoot, path);
        }
        catch {
            return null;
        }
        try {
            if (!lstatSync(abs).isFile())
                return null;
        }
        catch {
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
    // Resolve the full required-edge closure over the candidate's own declared edges with a visited
    // set (repeated and cyclic required edges terminate). Every required edge is bound to the trusted
    // contract: it must be a declared required edge (an added edge not in the contract is refused), it
    // must be retained-resolved to the exact target the contract names (a retargeted or unresolved edge
    // is refused), and the support body that target delivers must exist beneath the recipient root with
    // the contract's expected digest (a missing body or digest mismatch is refused). Each rejection
    // names the failing edge id. Untrusted candidate labels alone can no longer admit a dependency.
    const candidateEdges = (entry.dependencies ?? []).map(dep => projectEdge(entry, dep));
    const byEntry = new Map();
    for (const edge of candidateEdges) {
        const list = byEntry.get(edge.fromEntry) ?? [];
        list.push(edge);
        byEntry.set(edge.fromEntry, list);
    }
    const expectedEdges = new Map((expected.requiredEdges ?? []).map(re => [re.id, re]));
    const seenRequired = new Set();
    const visited = new Set();
    const stack = [entry.id];
    while (stack.length) {
        const current = stack.pop();
        if (visited.has(current))
            continue;
        visited.add(current);
        for (const edge of byEntry.get(current) ?? []) {
            if (!REQUIRED.has(edge.relationship))
                continue;
            seenRequired.add(edge.id);
            const contract = expectedEdges.get(edge.id);
            if (!contract) {
                reasons.push(`required edge ${edge.id} is not declared by the trusted contract`);
                continue;
            }
            // The trusted contract binds the edge's relationship and destination, not only its resolvedBy
            // target: a required-file edge cannot be relabelled to another required kind, and its `to` cannot
            // be repointed (e.g. at a D2a private-session record) while a different helper body is verified. (finding 6)
            if (edge.relationship !== contract.relationship) {
                reasons.push(`required edge ${edge.id} relationship ${edge.relationship} does not match the trusted contract ${contract.relationship}`);
                continue;
            }
            if (!deepEqual(edge.to, contract.to)) {
                reasons.push(`required edge ${edge.id} destination does not match the trusted contract`);
                continue;
            }
            const target = edge.resolvedBy && typeof edge.resolvedBy.target === 'string' ? edge.resolvedBy.target : null;
            if (edge.disposition !== 'retained-resolved' || target === null) {
                reasons.push(`required edge ${edge.id} is unresolved`);
                continue;
            }
            if (target !== contract.resolvesTo) {
                reasons.push(`required edge ${edge.id} is retargeted to ${target}, expected ${contract.resolvesTo}`);
                continue;
            }
            const digest = supportDigest(contract.path);
            if (digest === null) {
                reasons.push(`required edge ${edge.id} support body ${contract.path} is missing`);
                continue;
            }
            if (digest !== contract.sha256) {
                reasons.push(`required edge ${edge.id} support body ${contract.path} digest mismatch`);
                continue;
            }
            if (edge.to.entry !== undefined && !visited.has(edge.to.entry))
                stack.push(edge.to.entry);
        }
    }
    // A required edge the contract declares but the candidate omits shortens the required closure.
    for (const id of expectedEdges.keys())
        if (!seenRequired.has(id))
            reasons.push(`required edge ${id} declared by the trusted contract is missing from the candidate`);
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
// and require the exact expectedSha256. This byte comparison is the sole proof that a target's
// delivery claim holds, in Loam and in every render; validateCatalog no longer matches delivery or
// expectedSha256 against the frozen obligations (plan D1). Planned targets are never read.
// (Plan D1/D4/D16; finding 5.)
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
export function relativePosix(root, target) { return relative(root, target).split(sep).join('/'); }
//# sourceMappingURL=catalog.js.map