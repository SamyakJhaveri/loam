import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { assertSchemaDocument, validate } from '../../src/assets/schema.js';
import { sha256 } from '../../src/assets/units.js';
import {
  CatalogError, loadCatalog, validateCatalog, resolveEntry, scanPersonalPaths,
  assertRelativePath, containedPath, requiredClosure, OBLIGATIONS,
  type Catalog, type CatalogEntry, type Edge, type ExpectedEntry,
} from '../../src/assets/catalog.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const load = (): Catalog => loadCatalog(root).catalog;
const clone = (value: Catalog): Catalog => structuredClone(value);
const entryOf = (catalog: Catalog, id: string): CatalogEntry => {
  const found = catalog.entries.find(e => e.id === id);
  if (!found) throw new Error(`fixture entry missing: ${id}`);
  return found;
};
function expectRule(fn: () => unknown, rule: string): void {
  assert.throws(fn, (error: unknown) => error instanceof CatalogError && error.rule === rule, `expected rule ${rule}`);
}
// A prohibited personal path built at runtime so it is never catalog prose the provenance scan would see.
const personal = (): string => ['/Us', 'ers/', 'operator', '/secret.txt'].join('');

// ---------------------------------------------------------------------------
test('catalog.schema-and-payload', () => {
  const { catalog, schema } = loadCatalog(root);
  const report = validateCatalog(catalog);
  assert.equal(report.entries, OBLIGATIONS.entries.length);
  assert.equal(report.targets, OBLIGATIONS.targets.length);
  assert.equal(report.edges, OBLIGATIONS.edges.length);
  assert.equal(report.wrappers, OBLIGATIONS.nativeWrappers.length);
  assert.equal(report.privateMetadata, 5);

  // The complete real catalog conforms to its own schema with no issues.
  assertSchemaDocument(schema);
  assert.equal(validate(schema, catalog).length, 0);

  // Exact required memberships, targets, edge identities and disjoint dispositions.
  assert.deepEqual([...catalog.entries.map(e => e.id)].sort(), [...OBLIGATIONS.entries.map(e => e.id)].sort());
  assert.deepEqual([...catalog.targets.map(t => t.id)].sort(), [...OBLIGATIONS.targets.map(t => t.id)].sort());
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

  // D2a exact tuples and typed null/empty fields.
  for (const row of OBLIGATIONS.privateMetadata) {
    const entry = entryOf(catalog, row.id);
    assert.equal(entry.source.type, 'private-local-metadata');
    assert.equal((entry.source as Record<string, unknown>).historicalSha256, row.historicalSha256);
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
  const privateId = OBLIGATIONS.privateMetadata[0]!.id;
  // Reject metadata promotion (status), source-unit injection, and a required edge satisfied by metadata.
  expectRule(() => { const c = clone(catalog); entryOf(c, privateId).status = 'available'; validateCatalog(c); }, 'status.promoted');
  expectRule(() => { const c = clone(catalog); (entryOf(c, privateId).sourceUnits as unknown[]).push({ id: `${privateId}:u1`, role: 'body', start: 1, end: 1, sha256: '0'.repeat(64) }); validateCatalog(c); }, 'unit.private-metadata');
  expectRule(() => {
    const c = clone(catalog);
    const edge = entryOf(c, 'baseline:plan-review').dependencies[0]!;
    edge.to = { entry: privateId }; edge.disposition = 'retained-resolved';
    validateCatalog(c);
  }, 'edge.private-resolver');
});

// ---------------------------------------------------------------------------
test('catalog.conservation-rejections', () => {
  const catalog = load();
  assert.doesNotThrow(() => validateCatalog(catalog));

  // Remove a baseline entry.
  expectRule(() => { const c = clone(catalog); c.entries = c.entries.filter(e => e.id !== 'baseline:plan-review'); validateCatalog(c); }, 'membership.missing');
  // Delete a required support edge.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.dependencies = e.dependencies.filter(d => d.id !== 'baseline:plan-review:e1'); validateCatalog(c); }, 'edge.missing');
  // Delete the forward edge and its reverse index entry together.
  expectRule(() => {
    const c = clone(catalog);
    const e = entryOf(c, 'baseline:plan-review'); e.dependencies = e.dependencies.filter(d => d.id !== 'baseline:plan-review:e1');
    const target = entryOf(c, 'support:cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md');
    target.referencedBy = target.referencedBy.filter(id => id !== 'baseline:plan-review:e1');
    validateCatalog(c);
  }, 'edge.missing');
  // Substitute a valid unrelated support target for the required edge.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').dependencies[0]!.to = { entry: 'support:bin/lib.sh' }; validateCatalog(c); }, 'edge.retargeted');
  // Change a required edge to optional.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').dependencies[0]!.relationship = 'optional-reference'; validateCatalog(c); }, 'edge.relationship');
  // Corrupt the reverse index while the edges are untouched.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'support:cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md').referencedBy = []; validateCatalog(c); }, 'edge.inverse');
  // Unknown / typo successor.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').targets = ['method:plan-reviewwww']; validateCatalog(c); }, 'target.unknown');
  // Change an exact target path.
  expectRule(() => { const c = clone(catalog); c.targets.find(t => t.id === 'method:plan-review')!.path = '.agents/skills/plan-review/OTHER.md'; validateCatalog(c); }, 'target.path');
  // Collapse the critique variants by sharing a launch key.
  expectRule(() => {
    const c = clone(catalog);
    const codex = entryOf(c, 'snapshot:distbench-codex-critique-swarm');
    const launch = codex.preservation.map.find(m => m.section === 'launch-codex-serial-fallback')!;
    launch.section = 'launch-claude-parallel-agents';
    validateCatalog(c);
  }, 'variant.collapsed');
  // Relabel a provider.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'snapshot:distbench-claude-critique-swarm').applicability = 'codex'; validateCatalog(c); }, 'provider.relabeled');
  // Replace a meaningful map with a title-only map.
  expectRule(() => {
    const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review');
    e.preservation.map = [{ unit: e.sourceUnits[0]!.id, target: 'method:plan-review', section: e.name }];
    validateCatalog(c);
  }, 'map.title-only');
  // Remove a required source unit.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.sourceUnits = e.sourceUnits.slice(1); validateCatalog(c); }, 'unit.mismatch');

  // Privacy subcases: a prohibited path in notes, blockers, attribution, an object key, and a decoded string.
  const p = personal();
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `see ${p} for context`; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').blockers = [`blocked by ${p}`]; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'baseline:plan-review').attribution as Record<string, unknown>).author = p; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'baseline:plan-review') as unknown as Record<string, unknown>)[p] = true; validateCatalog(c); }, 'privacy.personal-path');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = `path=/Users/operator/x`; validateCatalog(c); }, 'privacy.personal-path');
  // Positive control: a generic non-personal path is accepted.
  assert.doesNotThrow(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').notes = 'see .agents/skills/plan-review/SKILL.md'; validateCatalog(c); });

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
  // Present seed bodies carry a delivered digest; the two present targets are unqualified, not verified.
  const present = catalog.targets.filter(t => t.delivery === 'present-unqualified');
  assert.deepEqual(present.map(t => t.id).sort(), ['method:catchup', 'method:fable-prompting']);
  for (const target of present) assert.match(String(target.expectedSha256), /^[0-9a-f]{64}$/);
  assert.equal(catalog.targets.some(t => t.delivery === 'verified'), false);

  // Production pending-to-available fails even with blockers erased; activation=true always fails.
  expectRule(() => { const c = clone(catalog); const e = entryOf(c, 'baseline:plan-review'); e.status = 'available'; e.blockers = []; validateCatalog(c); }, 'status.promoted');
  expectRule(() => { const c = clone(catalog); entryOf(c, 'baseline:plan-review').activation.activated = true; validateCatalog(c); }, 'activation.claimed');

  // Synthetic qualified entry under a temporary recipient root: resolveEntry admits it, but never activates it.
  const recipient = mkdtempSync(join(tmpdir(), 'loam-catalog-resolve-'));
  try {
    mkdirSync(join(recipient, 'skills', 'demo', 'references'), { recursive: true });
    const body = 'method body\n'; const contract = 'contract body\n';
    writeFileSync(join(recipient, 'skills', 'demo', 'SKILL.md'), body);
    writeFileSync(join(recipient, 'skills', 'demo', 'references', 'contract.md'), contract);
    symlinkSync(tmpdir(), join(recipient, 'outside'));
    const sample = entryOf(catalog, 'baseline:plan-review');
    const bodyDigest = sha256(body); const contractDigest = sha256(contract);
    const qualified: ExpectedEntry = {
      id: 'demo', qualified: true, status: 'available',
      targets: [{ path: 'skills/demo/SKILL.md', sha256: bodyDigest }],
      prerequisites: [{ id: 'demo:p1', type: 'file', path: 'skills/demo/references/contract.md', expectedSha256: contractDigest, verification: 'unverified' }],
      blockers: [],
    };
    const good = resolveEntry(sample, qualified, recipient);
    assert.deepEqual([good.activatable, good.activated], [true, false]);

    const reject = (mutate: (e: ExpectedEntry) => void): void => {
      const expected = structuredClone(qualified); mutate(expected);
      const resolution = resolveEntry(sample, expected, recipient);
      assert.equal(resolution.activatable, false);
      assert.equal(resolution.activated, false);
    };
    reject(e => { e.targets[0]!.sha256 = '0'.repeat(64); });                                                   // wrong body digest
    reject(e => { e.targets[0]!.path = 'skills/demo/missing.md'; });                                            // missing support
    reject(e => { e.prerequisites[0]!.expectedSha256 = '0'.repeat(64); });                                      // wrong prerequisite digest
    reject(e => { e.prerequisites.push({ id: 'demo:p2', type: 'file', path: 'skills/demo/absent.md', expectedSha256: contractDigest, verification: 'unverified' }); }); // omitted required prerequisite file
    reject(e => { e.blockers = ['unresolved blocker']; });                                                      // unresolved blocker
    reject(e => { e.prerequisites.push({ id: 'demo:p3', type: 'command', name: 'git', verification: 'unverified' }); }); // unverified command
    reject(e => { e.targets[0]!.path = 'outside/x'; });                                                         // escaping path through a symlink
  } finally {
    rmSync(recipient, { recursive: true, force: true });
  }

  // requiredClosure ignores repeated nodes and never loops.
  const closure = requiredClosure('baseline:plan-review', OBLIGATIONS.edges as readonly Edge[]);
  assert.ok(Array.isArray(closure));
  assert.equal(new Set(closure).size, closure.length);
});

// ---------------------------------------------------------------------------
test('catalog.selected-dependencies-mapped', () => {
  const catalog = load();
  // Exact wrapper set: each wrapper equals its obligation on provider/source/method/projection.
  assert.equal(catalog.nativeWrappers.length, 15);
  for (const wrapper of catalog.nativeWrappers) {
    const obligation = OBLIGATIONS.nativeWrappers.find(w => w.id === wrapper.id);
    assert.ok(obligation, `wrapper ${wrapper.id} is an obligation`);
    assert.deepEqual([wrapper.provider, wrapper.wrappedSource, wrapper.method, wrapper.projection], [obligation!.provider, obligation!.wrappedSource, obligation!.method, obligation!.projection]);
  }
  // Empty, missing (count) and retargeted wrapper sets all reject.
  expectRule(() => { const c = clone(catalog); c.nativeWrappers = []; validateCatalog(c); }, 'wrapper.set');
  expectRule(() => { const c = clone(catalog); c.nativeWrappers = c.nativeWrappers.slice(1); validateCatalog(c); }, 'wrapper.set');
  expectRule(() => { const c = clone(catalog); c.nativeWrappers[0]!.method = 'method:agent-team'; validateCatalog(c); }, 'wrapper.row');
  expectRule(() => { const c = clone(catalog); c.nativeWrappers[0]!.provider = 'codex'; validateCatalog(c); }, 'wrapper.row');

  // A required selected dependency has a named mapping or prerequisite.
  const planReview = entryOf(catalog, 'baseline:plan-review');
  assert.ok(planReview.dependencies.some(d => d.relationship === 'required-file' && d.disposition === 'retained-resolved' && d.resolvedBy?.target));
  assert.ok(planReview.prerequisites.some(p => p.type === 'file' && p.path));

  // Explicit source-project exclusions: the old grading roles (judge.md, reviewer.md) are local-only, not wrappers.
  assert.equal(catalog.nativeWrappers.some(w => /\/(judge|reviewer)\.md$/.test(w.wrappedSource)), false);
  assert.ok(catalog.notSelected.length === 210);

  // Declared-unread remote cannot gain a body digest.
  expectRule(() => { const c = clone(catalog); (entryOf(c, 'remote:deer-flow-public').source as Record<string, unknown>).remoteBodyDigest = '0'.repeat(64); validateCatalog(c); }, 'source.identity');

  // Disposition sets and counts.
  expectRule(() => { const c = clone(catalog); c.notSelected = c.notSelected.slice(1); validateCatalog(c); }, 'disposition.count');
  expectRule(() => { const c = clone(catalog); (c.notSelected[0] as Record<string, unknown>).sha256 = '0'.repeat(64); validateCatalog(c); }, 'disposition.set');
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
  // Invalid source span and invalid target key both reject.
  expectRule(() => { const c = clone(catalog); entryOf(c, 'pocock:handoff').sourceUnits[1]!.end = 9999; validateCatalog(c); }, 'unit.mismatch');
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
