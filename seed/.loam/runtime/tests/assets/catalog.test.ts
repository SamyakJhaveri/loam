import assert from 'node:assert/strict';
import { cpSync, mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { assertSchemaDocument, validate } from '../../src/assets/schema.js';
import { extractSourceUnits, sha256 } from '../../src/assets/units.js';
import {
  CatalogError, loadCatalog, validateCatalog, resolveEntry, scanPersonalPaths, assertSourceRevisions,
  assertRelativePath, containedPath, requiredClosure, checkRecipientDelivery, recipientRootOf, projectEdge,
  type Catalog, type CatalogEntry, type Edge, type ExpectedEntry, type Target,
} from '../../src/assets/catalog.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const load = (): Catalog => loadCatalog(root).catalog;
const clone = (value: Catalog): Catalog => structuredClone(value);
const entryOf = (catalog: Catalog, id: string): CatalogEntry => {
  const found = catalog.entries.find(e => e.id === id);
  if (!found) throw new Error(`fixture entry missing: ${id}`);
  return found;
};
// The catalog is its own truth: edges flatten from per-entry dependencies, private records are the
// entries whose source identity is private-local-metadata, and total edge count sums the dependencies.
const flatEdges = (catalog: Catalog): Edge[] => catalog.entries.flatMap(e => e.dependencies.map(d => projectEdge(e, d)));
const privateEntries = (catalog: Catalog): CatalogEntry[] => catalog.entries.filter(e => e.source.type === 'private-local-metadata');
const edgeCount = (catalog: Catalog): number => catalog.entries.reduce((n, e) => n + e.dependencies.length, 0);
function expectRule(fn: () => unknown, rule: string): void {
  assert.throws(fn, (error: unknown) => error instanceof CatalogError && error.rule === rule, `expected rule ${rule}`);
}
// A prohibited personal path built at runtime so it is never catalog prose the provenance scan would see.
const personal = (): string => ['/Us', 'ers/', 'operator', '/secret.txt'].join('');

// ---------------------------------------------------------------------------
test('catalog.schema-and-payload', () => {
  const { catalog, schema } = loadCatalog(root);
  const report = validateCatalog(catalog);
  // The report counts are read back from the catalog itself.
  assert.equal(report.entries, catalog.entries.length);
  assert.equal(report.targets, catalog.targets.length);
  assert.equal(report.edges, edgeCount(catalog));
  assert.equal(report.wrappers, catalog.nativeWrappers.length);
  assert.equal(report.privateMetadata, privateEntries(catalog).length);
  assert.equal(report.privateMetadata, 5);

  // The complete real catalog conforms to its own schema with no issues.
  assertSchemaDocument(schema);
  assert.equal(validate(schema, catalog).length, 0);

  // Entry and target ids are unique and disjoint dispositions hold.
  assert.equal(new Set(catalog.entries.map(e => e.id)).size, catalog.entries.length);
  assert.equal(new Set(catalog.targets.map(t => t.id)).size, catalog.targets.length);
  assert.equal(catalog.selectionAliases.length, 12);
  assert.equal(catalog.notSelected.length, 210);
  assert.equal(catalog.pluginReferences.length, 15);

  // Schema vocabulary positives and negatives, keyword by keyword.
  const ok = (s: unknown, v: unknown): void => assert.equal(validate(s, v).length, 0);
  const bad = (s: unknown, v: unknown): void => assert.ok(validate(s, v).length > 0);
  // type + nested objects + required + additionalProperties
  const nested = { type: 'object', additionalProperties: false, required: ['inner'], properties: { inner: { type: 'object', additionalProperties: false, properties: { n: { type: 'integer' } } } } };
  ok(nested, { inner: { n: 1 } });
  bad(nested, { inner: { n: 1 }, extra: true });   // extra property
  bad(nested, {});                                  // missing required
  bad(nested, { inner: { n: 'x' } });               // wrong type
  // nullable type array
  const nullable = { type: ['string', 'null'] };
  ok(nullable, null); ok(nullable, 'a'); bad(nullable, 3);
  // enum + const + pattern
  ok({ enum: ['a', 'b'] }, 'a'); bad({ enum: ['a', 'b'] }, 'c');
  ok({ const: 1 }, 1); bad({ const: 1 }, 2);
  ok({ type: 'string', pattern: '^[0-9a-f]{64}$' }, '0'.repeat(64)); bad({ type: 'string', pattern: '^[0-9a-f]{64}$' }, 'zz');
  // minItems + uniqueItems (duplicate array values)
  ok({ type: 'array', minItems: 1, uniqueItems: true }, [1, 2]);
  bad({ type: 'array', minItems: 1 }, []);
  bad({ type: 'array', uniqueItems: true }, [1, 1]);
  // items nested schema
  ok({ type: 'array', items: { type: 'integer' } }, [1, 2]); bad({ type: 'array', items: { type: 'integer' } }, ['a']);
  // local $ref
  const refSchema = { $defs: { id: { type: 'string' } }, type: 'object', additionalProperties: false, properties: { x: { $ref: '#/$defs/id' } } };
  ok(refSchema, { x: 'y' }); bad(refSchema, { x: 1 });
  // unknown keyword, missing reference, non-local reference, cyclic reference are schema-document errors
  assert.throws(() => assertSchemaDocument({ type: 'object', mystery: 1 }));
  assert.throws(() => assertSchemaDocument({ type: 'object', properties: { a: { $ref: '#/$defs/nope' } } }));
  assert.throws(() => assertSchemaDocument({ type: 'object', properties: { a: { $ref: 'https://example/x' } } }));
  assert.throws(() => assertSchemaDocument({ $defs: { a: { $ref: '#/$defs/b' }, b: { $ref: '#/$defs/a' } } }));

  // Finding 1 (round 5): inherited Object.prototype names are neither declared properties nor
  // definitions. A JSON-parsed top-level property named after an inherited member (constructor,
  // toString, __proto__) is undeclared, so additionalProperties:false rejects it; a $ref to
  // #/$defs/<such a name> with no such definition is an unresolved reference. `in` would find the
  // inherited member on the prototype chain; Object.hasOwn does not. The inputs are JSON-parsed so a
  // `__proto__` key is an own property, exactly as the shipped catalog is parsed.
  const closedObject = { type: 'object', additionalProperties: false, properties: { x: { type: 'integer' } } };
  for (const inherited of ['constructor', 'toString', '__proto__']) {
    const parsed = JSON.parse(`{"${inherited}": 1}`) as unknown;
    const issues = validate(closedObject, parsed);
    assert.ok(issues.some(i => i.keyword === 'additionalProperties'), `top-level ${inherited} must raise additionalProperties`);
    assert.throws(() => assertSchemaDocument({ $defs: { real: { type: 'string' } }, type: 'object', additionalProperties: false, properties: { x: { $ref: `#/$defs/${inherited}` } } }), /unresolved reference/, `$ref to #/$defs/${inherited} must be unresolved`);
    // The required-property lookup also uses hasOwn: an instance missing a required property named
    // after an inherited member is reported missing, not treated as present through the prototype.
    const requiresInherited = { type: 'object', properties: { [inherited]: { type: 'string' } }, required: [inherited] };
    assert.ok(validate(requiresInherited, JSON.parse('{}')).some(i => i.keyword === 'required'), `missing required ${inherited} must be reported`);
  }

  // Finding 5 (round 5): a fence marker inside an open HTML comment is comment text, not a fence, so
  // the comment's closing line and the later heading stay visible. extractSourceUnits on the verdict's
  // input yields a heading unit (fence-first recognition returned a single paragraph and no heading).
  const fence = '`'.repeat(3);
  const commentThenHeading = new TextEncoder().encode(`<!-- comment\n${fence}\n-->\n# Real heading\nbody\n`);
  const cfUnits = extractSourceUnits('demo:comment-fence', 'sample.md', commentThenHeading);
  const heading = cfUnits.find(u => u.role === 'heading');
  assert.ok(heading, 'the heading after the terminated comment is extracted');
  assert.equal(heading!.start, 4);

  // D2a exact tuples and typed null/empty fields, over the five private-local-metadata entries.
  const privateRows = privateEntries(catalog);
  assert.equal(privateRows.length, 5);
  for (const entry of privateRows) {
    assert.equal(entry.source.type, 'private-local-metadata');
    assert.match(String((entry.source as Record<string, unknown>).historicalSha256), /^[0-9a-f]{64}$/);
    assert.equal((entry.source as Record<string, unknown>).currentSha256, null);
    assert.equal(entry.assetKind, 'advice');
    assert.equal(entry.status, 'local-only');
    assert.equal(entry.preservation.decision, 'local-only');
    assert.equal(entry.activation.activated, false);
    assert.equal(entry.providers, null);
    assert.equal(entry.declaredTools, null);
    assert.equal(entry.declaredServices, null);
    assert.equal(entry.sideEffects, null);
    assert.deepEqual([entry.sourceUnits.length, entry.preservation.map.length, entry.targets.length, entry.dependencies.length, entry.prerequisites.length], [0, 0, 0, 0, 0]);
  }
  const privateId = privateRows[0]!.id;
  // Reject metadata promotion (status), source-unit injection, and a required edge satisfied by metadata.
  expectRule(() => { const c = clone(catalog); entryOf(c, privateId).status = 'available'; validateCatalog(c); }, 'status.promoted');
  expectRule(() => { const c = clone(catalog); (entryOf(c, privateId).sourceUnits as unknown[]).push({ id: `${privateId}:u1`, role: 'body', start: 1, end: 1, sha256: '0'.repeat(64) }); validateCatalog(c); }, 'unit.private-metadata');
  expectRule(() => {
    const c = clone(catalog);
    const edge = entryOf(c, 'baseline:plan-review').dependencies[0]!;
    edge.to = { entry: privateId }; edge.disposition = 'retained-resolved';
    validateCatalog(c);
  }, 'edge.private-resolver');

  // Finding 2: the schema restricts preservation.phase to the assessed enum; a promoted phase is a
  // schema violation as well as a policy one.
  assert.ok(validate(schema, { ...catalog, entries: catalog.entries.map(e => e.id === 'pocock:implement' ? { ...e, preservation: { ...e.preservation, phase: 'implemented' } } : e) }).length > 0);
  // A private record can assert neither author nor license.
  expectRule(() => { const c = clone(catalog); (entryOf(c, privateId).attribution as Record<string, unknown>).author = 'Invented Author'; validateCatalog(c); }, 'source.private-metadata');
  expectRule(() => { const c = clone(catalog); (entryOf(c, privateId).attribution as Record<string, unknown>).license = 'MIT'; validateCatalog(c); }, 'source.private-metadata');
  // Source revisions must carry the seven recognized keys; dropping one is a mismatch.
  expectRule(() => { const c = clone(catalog); delete (c.sourceRevisions as Record<string, unknown>).obligationsSha256; validateCatalog(c); }, 'sourceRevisions.mismatch');
});

// ---------------------------------------------------------------------------
test('catalog.conservation-rejections', () => {
  const catalog = load();
  assert.doesNotThrow(() => validateCatalog(catalog));

  // sourceRevisions must be an object; a non-object is a mismatch (single-argument, catalog-internal).
  expectRule(() => { const c = clone(catalog); (c as unknown as { sourceRevisions: unknown }).sourceRevisions = 'not-an-object'; assertSourceRevisions(c); }, 'sourceRevisions.mismatch');

  // Remove a baseline entry: an edge from another entry no longer resolves to it.
  expectRule(() => { const c = clone(catalog); c.entries = c.entries.filter(e => e.id !== 'baseline:plan-review'); validateCatalog(c); }, 'edge.unresolved');
  // Delete a required support edge: the support's referencedBy no longer matches the recomputed inverse.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.dependencies = e.dependencies.filter(d => d.id !== 'baseline:plan-review:e1'); validateCatalog(c); }, 'edge.inverse');
  // Retarget a required edge at an entry that does not exist: it no longer resolves.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').dependencies[0]!.to = { entry: 'support:does-not-exist' }; validateCatalog(c); }, 'edge.unresolved');
  // A replacement that names a target the catalog does not carry: it no longer resolves.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').dependencies[0]!.replacement = { reason: 'superseded', target: 'method:does-not-exist' }; validateCatalog(c); }, 'edge.unresolved');
  // Corrupt the reverse index while the edges are untouched.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'support:cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md').referencedBy = []; validateCatalog(c); }, 'edge.inverse');
  // An empty source digest is refused as a literal, before any tree re-hash.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').source.sha256 = ''; validateCatalog(c); }, 'source.digest-empty');
  // Unknown / typo successor.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').targets = ['method:plan-reviewwww']; validateCatalog(c); }, 'target.unknown');
  // Section keys that are not the union of the mapped sections aimed at the target.
  expectRule(() => { const c = clone(catalog); c.targets.find(t => t.id === 'method:plan-review')!.sectionKeys = ['not-a-mapped-section']; validateCatalog(c); }, 'target.section-keys');
  // D1: delivery truth is proven by bytes, so the delivery rule rejects each of its three branches: a
  // present-unqualified target with a null digest (nothing to verify against the recipient body), an
  // unknown delivery state, and a delivered target whose digest is not 64 lowercase hex.
  for (const mutate of [
    (t: Target) => { t.expectedSha256 = null; },
    (t: Target) => { t.delivery = 'bogus'; },
    (t: Target) => { t.expectedSha256 = t.expectedSha256!.toUpperCase(); },
  ]) expectRule(() => { const c = clone(catalog); mutate(c.targets.find(t => t.id === 'method:hypothesis-tree')!); validateCatalog(c); }, 'target.delivery');
  // A planned target that carries a digest fails the same rule.
  expectRule(() => { const c = clone(catalog); const t = c.targets.find(t => t.id === 'method:reflect')!; t.expectedSha256 = 'a'.repeat(64); validateCatalog(c); }, 'target.delivery');
  // Collapse the critique variants by sharing a launch key.
  expectRule(() => {
    const c = clone(catalog);
    const codex = entryOf(c, 'snapshot:distbench-codex-critique-swarm');
    const launch = codex.preservation.map.find(m => m.section === 'launch-codex-serial-fallback')!;
    launch.section = 'launch-claude-parallel-agents';
    validateCatalog(c);
  }, 'variant.collapsed');
  // Relabel a provider: the flags no longer match the new applicability.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'snapshot:distbench-claude-critique-swarm').applicability = 'codex'; validateCatalog(c); }, 'provider.mismatch');
  // Replace a meaningful map with a title-only map.
  expectRule(() => {
    const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review');
    e.preservation.map = [{ unit: e.sourceUnits[0]!.id, target: 'method:plan-review', section: e.name }];
    validateCatalog(c);
  }, 'map.title-only');
  // Remove a source unit that a map row still names: the row references a now-unknown unit.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.sourceUnits = e.sourceUnits.slice(1); validateCatalog(c); }, 'map.missing-unit');
  // Finding 2 (round 5): a catalog exclusion map row must carry a non-whitespace reason (D7). Missing,
  // empty and whitespace-only reasons on an `exclude` row are each rejected. The reason is stripped
  // from the compiled projection, so this is a policy rule, not a schema keyword outside the D3 list;
  // the accepted catalog (validated above) is the positive control that a real reason passes.
  const briefExcludeRow = (c: Catalog): { exclude?: string; reason?: string } => {
    const row = entryOf(c, 'baseline:brief').preservation.map.find(r => r.exclude !== undefined);
    if (!row) throw new Error('fixture: baseline:brief has no exclude row');
    return row;
  };
  expectRule(() => { const c = clone(catalog); delete briefExcludeRow(c).reason; validateCatalog(c); }, 'map.exclusion-reason');
  expectRule(() => { const c = clone(catalog); briefExcludeRow(c).reason = ''; validateCatalog(c); }, 'map.exclusion-reason');
  expectRule(() => { const c = clone(catalog); briefExcludeRow(c).reason = '  \t  '; validateCatalog(c); }, 'map.exclusion-reason');
  // Finding 2: promote a preservation phase; misalign a snapshot's provider flags with applicability.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'pocock:implement').preservation.phase = 'implemented'; validateCatalog(c); }, 'phase.promoted');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'snapshot:distbench-claude-critique-swarm').providers as Record<string, unknown>).codex = true; (entryOf(c, 'snapshot:distbench-claude-critique-swarm').providers as Record<string, unknown>).claude = false; validateCatalog(c); }, 'provider.mismatch');
  // Finding 3: a duplicated dependency whose destination is external (never seen by the inverse index).
  expectRule(() => {
    const c = clone(catalog);
    const e = c.entries.find(x => x.dependencies.some(d => d.to.external !== undefined))!;
    const dep = e.dependencies.find(d => d.to.external !== undefined)!;
    e.dependencies = [...e.dependencies, structuredClone(dep)];
    validateCatalog(c);
  }, 'membership.duplicate');

  // Privacy subcases: a prohibited path in notes, blockers, attribution, an object key, and a decoded
  // string. Every forbidden string is built at runtime, never a literal in the test source (D11).
  const p = personal();
  const namedTilde = ['~', 'operator', '/', 'private', '/notes'].join('');   // named-user home tilde
  const varTmp = ['/var', '/tmp/', 'operator', '/file'].join('');            // unix persistent temp root
  const privateVar = ['/priv', 'ate/var/', 'root', '/x'].join('');           // macOS resolved private root
  const escaped = (s: string): string => JSON.parse(JSON.stringify(s).replace(/\//g, '\\/')) as string; // JSON-escaped slashes, decoded
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `see ${p} for context`; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').blockers = [`blocked by ${p}`]; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'baseline:plan-review').attribution as Record<string, unknown>).author = p; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'baseline:plan-review') as unknown as Record<string, unknown>)[p] = true; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `path=${['/Users/', 'operator', '/x'].join('')}`; validateCatalog(c); }, 'privacy.personal-path');
  // Finding 5: the newly recognized forms are caught end-to-end (named-user tilde in notes, /var/tmp
  // in a blocker, /private/var in attribution).
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `moved to ${namedTilde}`; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').blockers = [`temp at ${varTmp}`]; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'baseline:plan-review').attribution as Record<string, unknown>).author = privateVar; validateCatalog(c); }, 'privacy.personal-path');
  // Finding 5: each new form is caught in each location by the scanner directly - nested value, array
  // element, attribution field, object key and a JSON-escaped/decoded string.
  for (const form of [namedTilde, varTmp, privateVar]) {
    assert.ok(scanPersonalPaths({ notes: `x ${form} y` }).length > 0, `nested value: ${form}`);
    assert.ok(scanPersonalPaths({ blockers: [`b ${form}`] }).length > 0, `array element: ${form}`);
    assert.ok(scanPersonalPaths({ attribution: { author: form } }).length > 0, `attribution: ${form}`);
    assert.ok(scanPersonalPaths({ [form]: true }).length > 0, `object key: ${form}`);
    assert.ok(scanPersonalPaths({ note: escaped(form) }).length > 0, `decoded string: ${form}`);
  }
  // Positive control: a generic non-personal path is accepted; an approximation like ~5/10 is not a path.
  assert.doesNotThrow(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = 'see .agents/skills/plan-review/SKILL.md'; validateCatalog(c); });
  assert.equal(scanPersonalPaths({ n: 'roughly ~5/10 of cases and ~2/3 done' }).length, 0);

  // Finding 7 (round 2): the /Users and /home patterns are case-insensitive, so a lowercase /users
  // home path in a note is caught end-to-end; and the `pattern`-key exemption is confined to the
  // schema document, so a `pattern` key carrying a personal path in any other document is no longer
  // exempt, while the same key stays exempt when the scan is labelled `schema`.
  const lowerUsers = ['/us', 'ers/', 'operator', '/x'].join('');   // lowercase /users home path
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `moved to ${lowerUsers}`; validateCatalog(c); }, 'privacy.personal-path');
  assert.ok(scanPersonalPaths({ note: lowerUsers }).length > 0, 'lowercase /users caught');
  assert.ok(scanPersonalPaths({ attribution: { pattern: personal() } }).length > 0, 'pattern key not exempt outside the schema');
  assert.equal(scanPersonalPaths({ pattern: personal() }, 'schema').length, 0, 'pattern key exempt only in the schema document');

  // scanPersonalPaths and the path validators directly.
  assert.equal(scanPersonalPaths({ a: '.agents/skills/x' }).length, 0);
  assert.ok(scanPersonalPaths({ a: `${p}` }).length > 0);
  assert.throws(() => assertRelativePath('/absolute', 'x'));
  assert.throws(() => assertRelativePath('../up', 'x'));
  assert.doesNotThrow(() => assertRelativePath('a/b/c.md', 'x'));
});

// ---------------------------------------------------------------------------
test('catalog.activation-honesty', () => {
  const catalog = load();
  // Every actual method is unavailable; nothing is activated.
  for (const entry of catalog.entries) {
    assert.equal(entry.activation.activated, false);
    assert.notEqual(entry.status, 'available');
  }
  // Present seed bodies carry a delivered digest; the three present targets are unqualified, not verified.
  const present = catalog.targets.filter(t => t.delivery === 'present-unqualified');
  assert.deepEqual(present.map(t => t.id).sort(), ['method:catchup', 'method:fable-prompting', 'method:hypothesis-tree']);
  for (const target of present) assert.match(String(target.expectedSha256), /^[0-9a-f]{64}$/);
  assert.equal(catalog.targets.some(t => t.delivery === 'verified'), false);

  // Production pending-to-available fails even with blockers erased; activation=true always fails.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.status = 'available'; e.blockers = []; validateCatalog(c); }, 'status.promoted');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').activation.activated = true; validateCatalog(c); }, 'activation.claimed');

  // Finding 5: recipient delivery. The recipient root is the package's `factory/../..`; every
  // present-unqualified/verified target body is read and must carry its exact expectedSha256, while
  // planned targets (whose bodies do not exist yet) are never read.
  const recipientRoot = recipientRootOf(root);
  assert.deepEqual(checkRecipientDelivery(catalog, recipientRoot), { checked: present.length });
  // A scratch recipient with just the present bodies: pass, then remove one body and change a byte.
  const scratchRecipient = mkdtempSync(join(tmpdir(), 'loam-catalog-delivery-'));
  try {
    for (const target of present) { const dst = join(scratchRecipient, target.path); mkdirSync(dirname(dst), { recursive: true }); cpSync(join(recipientRoot, target.path), dst); }
    assert.deepEqual(checkRecipientDelivery(catalog, scratchRecipient), { checked: present.length });
    const catchupBody = join(scratchRecipient, '.agents', 'skills', 'catchup', 'SKILL.md');
    rmSync(catchupBody);
    expectRule(() => checkRecipientDelivery(catalog, scratchRecipient), 'delivery.missing');
    cpSync(join(recipientRoot, '.agents', 'skills', 'catchup', 'SKILL.md'), catchupBody);
    const bytes = readFileSync(catchupBody); bytes[0] = bytes[0]! ^ 0x01; writeFileSync(catchupBody, bytes);
    expectRule(() => checkRecipientDelivery(catalog, scratchRecipient), 'delivery.digest');
  } finally {
    rmSync(scratchRecipient, { recursive: true, force: true });
  }

  // Finding 4: resolveEntry binds an untrusted candidate to a fixed trusted contract under a
  // temporary recipient root. The candidate is the input the negatives mutate; the expected
  // contract stays fixed. resolveEntry admits a matching candidate but never activates it.
  const recipient = mkdtempSync(join(tmpdir(), 'loam-catalog-resolve-'));
  try {
    mkdirSync(join(recipient, 'skills', 'demo', 'references'), { recursive: true });
    const body = 'method body\n'; const contract = 'contract body\n'; const helper = 'helper body\n';
    writeFileSync(join(recipient, 'skills', 'demo', 'SKILL.md'), body);
    writeFileSync(join(recipient, 'skills', 'demo', 'references', 'contract.md'), contract);
    writeFileSync(join(recipient, 'skills', 'demo', 'references', 'helper.md'), helper);
    symlinkSync(tmpdir(), join(recipient, 'outside'));
    // A recipient path that leaves the root through a link is refused by real-path containment.
    expectRule(() => containedPath(recipient, 'outside/x'), 'path.escape');
    const bodyDigest = sha256(body); const contractDigest = sha256(contract); const helperDigest = sha256(helper);
    // The trusted contract now also declares one required support edge: the edge id, the target it
    // must resolve to, and the recipient path and digest of the support body that target delivers.
    const qualified: ExpectedEntry = {
      id: 'demo', qualified: true, status: 'available',
      targets: [{ path: 'skills/demo/SKILL.md', sha256: bodyDigest }],
      prerequisites: [{ id: 'demo:p1', type: 'file', name: 'contract', path: 'skills/demo/references/contract.md', expectedSha256: contractDigest, verification: 'unverified' }],
      blockers: [],
      requiredEdges: [{ id: 'demo:e1', resolvesTo: 'reference:demo-helper', path: 'skills/demo/references/helper.md', sha256: helperDigest, to: { entry: 'support:demo-helper' }, relationship: 'required-file' }],
    };
    // The matching required edge the good candidate declares: retained-resolved to the exact target.
    const goodEdge = () => ({ id: 'demo:e1', sourceUnit: null, relationship: 'required-file', to: { entry: 'support:demo-helper' }, disposition: 'retained-resolved', resolvedBy: { target: 'reference:demo-helper' }, replacement: null, blocker: null, note: '' });
    // A synthetic candidate that matches the trusted contract, including its required support edge.
    const candidate = (): CatalogEntry => ({
      id: 'demo', collection: 'baseline', name: 'demo', kind: 'method', assetKind: 'advice',
      source: { type: 'regular-file', path: 'skills/demo/SKILL.md', sha256: bodyDigest },
      status: 'available', preservation: { decision: 'adapt', phase: 'assessed', map: [] }, activation: { activated: false, owner: null },
      targets: [], sourceUnits: [], dependencies: [goodEdge()], referencedBy: [],
      prerequisites: [{ id: 'demo:p1', type: 'file', name: 'contract', verification: 'unverified', contract: null, blocker: null, path: 'skills/demo/references/contract.md' }],
      providers: null, declaredTools: null, declaredServices: null, sideEffects: null,
      attribution: null, blockers: [], notes: '', consumers: null, hardcodedModelOrEffort: null,
    } as unknown as CatalogEntry);

    const good = resolveEntry(candidate(), qualified, recipient);
    assert.deepEqual([good.activatable, good.activated], [true, false]);
    assert.deepEqual(good.reasons, []);
    // A valid required edge that points back at the entry itself is admitted and terminates: the
    // visited set stops the required-closure traversal from re-processing the node. Its trusted
    // contract declares the same self-cyclic destination, so the `to` binding (finding 6) still holds.
    const cyclicContract: ExpectedEntry = { ...qualified, requiredEdges: [{ ...qualified.requiredEdges![0]!, to: { entry: 'demo' } }] };
    const cyclic = candidate();
    cyclic.dependencies = [{ ...goodEdge(), to: { entry: 'demo' } } as unknown as CatalogEntry['dependencies'][number]];
    assert.deepEqual([resolveEntry(cyclic, cyclicContract, recipient).activatable, false], [true, false]);

    // Candidate mutations: identity, status, activation, blockers, prerequisites and paths. An
    // optional needle asserts the rejection reason names the failing element (e.g. the edge id).
    const rejectCandidate = (mutate: (c: CatalogEntry) => void, needle?: string): void => {
      const c = candidate(); mutate(c);
      const resolution = resolveEntry(c, qualified, recipient);
      assert.equal(resolution.activatable, false);
      assert.equal(resolution.activated, false);
      if (needle !== undefined) assert.ok(resolution.reasons.some(r => r.includes(needle)), `expected a reason mentioning ${needle}, got ${JSON.stringify(resolution.reasons)}`);
    };
    rejectCandidate(c => { c.id = 'other'; });                                                                 // wrong id
    rejectCandidate(c => { c.status = 'shipped-pending-adaptation'; });                                        // pending status
    rejectCandidate(c => { c.activation.activated = true; });                                                  // activation claimed
    rejectCandidate(c => { c.blockers = ['unresolved blocker']; });                                            // unresolved blocker
    rejectCandidate(c => { c.prerequisites = []; });                                                           // omitted prerequisite
    rejectCandidate(c => { c.prerequisites = [...c.prerequisites, { id: 'demo:p2', type: 'command', name: 'git', verification: 'unverified', contract: null, blocker: null }]; }); // unverified command
    rejectCandidate(c => { c.prerequisites[0]!.path = 'outside/x'; });                                         // escaping candidate path through a symlink
    // A private-session record can never be admitted, even against a fully qualified contract.
    rejectCandidate(c => { (c.source as Record<string, unknown>).type = 'private-local-metadata'; c.kind = 'private-session-record'; });

    // Finding 3: required-edge readiness is bound to the trusted contract, not to untrusted labels.
    // Added required edge not declared by the contract.
    rejectCandidate(c => { c.dependencies = [...c.dependencies, { id: 'demo:e2', sourceUnit: null, relationship: 'required-file', to: { entry: 'support:missing-helper' }, disposition: 'retained-resolved', resolvedBy: { target: 'reference:missing-helper' }, replacement: null, blocker: null, note: '' }]; }, 'demo:e2'); // NOSONAR
    // Retargeted edge: the required edge resolves to a target the contract does not name.
    rejectCandidate(c => { c.dependencies[0]!.resolvedBy = { target: 'reference:other' }; }, 'demo:e1');
    // Edge left unresolved: the required edge is present but not retained-resolved.
    rejectCandidate(c => { c.dependencies[0]!.disposition = 'retained-unresolved'; c.dependencies[0]!.resolvedBy = null; }, 'demo:e1');
    // Cyclic required edge: a retargeted self-edge must terminate under the visited set.
    rejectCandidate(c => { c.dependencies = [{ id: 'demo:e1', sourceUnit: null, relationship: 'required-method', to: { entry: 'demo' }, disposition: 'retained-resolved', resolvedBy: { target: 'reference:other' }, replacement: null, blocker: null, note: '' }]; }, 'demo:e1');

    // Finding 6 (round 2): the trusted contract binds the edge's destination and relationship, not
    // only its resolvedBy target. A `to` repointed at a D2a private-session record (id built at
    // runtime, never read), a `to` omitted, and a relationship swapped to another required kind are
    // each refused by edge id while the contract's own helper body is the one verified.
    const d2aRecordId = ['support:seed', '.claude', 'codex-reviews', '2026-08-31-session.md'].join('/');
    rejectCandidate(c => { c.dependencies[0]!.to = { entry: d2aRecordId }; }, 'demo:e1');            // to retargeted at a D2a record
    rejectCandidate(c => { c.dependencies[0]!.to = {}; }, 'demo:e1');                                 // to omitted
    rejectCandidate(c => { c.dependencies[0]!.relationship = 'external-prerequisite'; }, 'demo:e1');  // relationship swapped to another required kind

    // Filesystem mutations (contract fixed): missing/changed method body, missing prerequisite body,
    // and, for the required support edge, a missing support body and a corrupted support digest.
    const rejectFs = (setup: (rr: string) => void, needle?: string): void => {
      const rr = mkdtempSync(join(tmpdir(), 'loam-catalog-resolve-fs-'));
      try {
        mkdirSync(join(rr, 'skills', 'demo', 'references'), { recursive: true });
        writeFileSync(join(rr, 'skills', 'demo', 'SKILL.md'), body);
        writeFileSync(join(rr, 'skills', 'demo', 'references', 'contract.md'), contract);
        writeFileSync(join(rr, 'skills', 'demo', 'references', 'helper.md'), helper);
        setup(rr);
        const resolution = resolveEntry(candidate(), qualified, rr);
        assert.equal(resolution.activatable, false);
        if (needle !== undefined) assert.ok(resolution.reasons.some(r => r.includes(needle)), `expected a reason mentioning ${needle}, got ${JSON.stringify(resolution.reasons)}`);
      } finally { rmSync(rr, { recursive: true, force: true }); }
    };
    rejectFs(rr => { rmSync(join(rr, 'skills', 'demo', 'SKILL.md')); });                                       // missing body
    rejectFs(rr => { writeFileSync(join(rr, 'skills', 'demo', 'SKILL.md'), 'changed body\n'); });              // changed body digest
    rejectFs(rr => { rmSync(join(rr, 'skills', 'demo', 'references', 'contract.md')); });                      // missing prerequisite body
    rejectFs(rr => { rmSync(join(rr, 'skills', 'demo', 'references', 'helper.md')); }, 'demo:e1');             // missing required support body
    rejectFs(rr => { writeFileSync(join(rr, 'skills', 'demo', 'references', 'helper.md'), 'tampered helper\n'); }, 'demo:e1'); // required support digest mismatch
  } finally {
    rmSync(recipient, { recursive: true, force: true });
  }

  // requiredClosure ignores repeated nodes and never loops.
  const closure = requiredClosure('baseline:plan-review', flatEdges(catalog));
  assert.ok(Array.isArray(closure));
  assert.equal(new Set(closure).size, closure.length);
});

// ---------------------------------------------------------------------------
test('catalog.selected-dependencies-mapped', () => {
  const catalog = load();
  // Every wrapper resolves against the catalog: it wraps a real entry, names a real method target,
  // and its payload sits under its provider's own native directory.
  assert.equal(catalog.nativeWrappers.length, 15);
  const targetIds = new Set(catalog.targets.map(t => t.id));
  const entryIds = new Set(catalog.entries.map(e => e.id));
  for (const wrapper of catalog.nativeWrappers) {
    assert.ok(entryIds.has(wrapper.wrappedSource), `wrapper ${wrapper.id} wraps a real entry`);
    assert.ok(targetIds.has(wrapper.method), `wrapper ${wrapper.id} names a real method target`);
    assert.ok(wrapper.payloadPath.startsWith(`assets/native/${wrapper.provider}/`), `wrapper ${wrapper.id} payload is under its provider directory`);
  }
  // An unresolved method target and a payload path outside the provider directory both reject.
  expectRule(() => { const c = clone(catalog); c.nativeWrappers[0]!.method = 'method:does-not-exist'; validateCatalog(c); }, 'wrapper.row');
  expectRule(() => { const c = clone(catalog); c.nativeWrappers[0]!.provider = 'codex'; validateCatalog(c); }, 'wrapper.row');
  // Finding 3: a same-count missing wrapper (one wrapper replaced by a copy of another) is rejected
  // as a duplicate id before any lookup map is built, so the dropped wrapper cannot hide.
  expectRule(() => { const c = clone(catalog); c.nativeWrappers[1] = structuredClone(c.nativeWrappers[0]!); validateCatalog(c); }, 'membership.duplicate');

  // A required selected dependency has a named mapping or prerequisite.
  const planReview = entryOf(catalog, 'baseline:plan-review');
  assert.ok(planReview.dependencies.some(d => d.relationship === 'required-file' && d.disposition === 'retained-resolved' && d.resolvedBy?.target));
  assert.ok(planReview.prerequisites.some(p => p.type === 'file' && p.path));

  // Explicit source-project exclusions: the old grading roles (judge.md, reviewer.md) are local-only, not wrappers.
  assert.equal(catalog.nativeWrappers.some(w => /\/(judge|reviewer)\.md$/.test(w.wrappedSource)), false);
  assert.ok(catalog.notSelected.length === 210);
});

// ---------------------------------------------------------------------------
test('catalog.pocock-collection', () => {
  const catalog = load();
  const pocock = catalog.entries.filter(e => e.collection === 'pocock');
  assert.equal(pocock.length, 25);
  // Released ids, sibling attribution and per-file MIT license.
  for (const entry of pocock) {
    assert.ok(entry.pocockSkill, `${entry.id} names its released skill`);
    assert.equal((entry.attribution as Record<string, unknown>).license, 'MIT');
    assert.equal(entry.activation.activated, false);
  }
  // Headingless handoff and implement maps: paragraph units mapped to sections.
  for (const id of ['pocock:handoff', 'pocock:implement']) {
    const entry = entryOf(catalog, id);
    assert.ok(entry.sourceUnits.some(u => u.role === 'paragraph'));
    assert.equal(entry.sourceUnits.some(u => u.role === 'heading'), false);
    assert.ok(entry.preservation.map.some(m => typeof m.target === 'string' && typeof m.section === 'string'));
  }
  // An invalid map target key rejects. (Source-span integrity is re-verified against the tree by the
  // provenance gate, which re-extracts the units, not by the catalog-internal validator.)
  expectRule(() => { const c = clone(catalog); const m = entryOf(c, 'pocock:handoff').preservation.map.find(r => typeof r.target === 'string')!; m.target = 'method:not-a-real-target'; validateCatalog(c); }, 'map.unknown-target');

  // Assessed merge never claims implemented.
  for (const id of ['pocock:to-spec', 'pocock:implement', 'pocock:code-review', 'pocock:handoff']) {
    const entry = entryOf(catalog, id);
    assert.equal(entry.preservation.decision, 'merge');
    assert.equal(entry.preservation.phase, 'assessed');
  }
  // Same-name baseline keeps its own identity even though a Pocock lesson merges into the same successor.
  const baseline = entryOf(catalog, 'baseline:auto-phase');
  assert.ok(baseline.targets.includes('method:auto-phase'));
  assert.notEqual(baseline.preservation.decision, 'merge');
  assert.equal(entryOf(catalog, 'pocock:implement').targets[0], 'method:auto-phase');

  // to-tickets supersession is recorded.
  const toTickets = entryOf(catalog, 'pocock:to-tickets');
  assert.match(`${toTickets.notes} ${toTickets.blockers.join(' ')}`, /supersed/i);

  // No Pocock delivered destination, wrapper or activation.
  assert.equal(catalog.nativeWrappers.some(w => w.wrappedSource.startsWith('pocock:')), false);
  for (const entry of pocock) for (const targetId of entry.targets) {
    const target = catalog.targets.find(t => t.id === targetId)!;
    assert.notEqual(target.delivery, 'verified');
  }
});
