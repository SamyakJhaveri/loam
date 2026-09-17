// Loam-only source-provenance gate for the curated catalog (plan NATIVE-05 D12/D14). It runs
// from the repository root, where cultivation/, the reviewed intake inventories and the
// mattpocock provenance are present; a rendered recipient project has none of these, which is
// why this gate cannot live in the shipped package. It compares the compiled obligations (the
// reviewed packet) against the actual working tree, never against personal source projects.
// Private session history under seed/.claude/codex-reviews is out of bounds: every filesystem
// read is routed through a boundary that throws on that prefix, and two scratch controls prove
// the metadata qualification is identical whether or not the private bodies are present.
import test from 'node:test';
import assert from 'node:assert/strict';
import { chmodSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readlinkSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { OBLIGATIONS, scanPersonalPaths } from '../../seed/.loam/factory/dist/src/assets/catalog.js';
import { sha256, verifySourceUnits } from '../../seed/.loam/factory/dist/src/assets/units.js';

const repo = fileURLToPath(new URL('../../', import.meta.url));
const INTAKE = 'docs/architecture-working/asset-intake';
const POCOCK = 'docs/architecture-working/tooling/mattpocock-skills';
const PRIVATE_PREFIX = 'seed/.claude/codex-reviews';
const REQUIRED = new Set(['required-file', 'required-method', 'external-prerequisite']);

// The filesystem boundary. Any read at or beneath the private session directory throws.
function guard(rel) {
  const norm = rel.split(sep).join('/');
  if (norm === PRIVATE_PREFIX || norm.startsWith(`${PRIVATE_PREFIX}/`)) throw new Error(`private session history is out of bounds: ${rel}`);
  return rel;
}
const readBytes = (root, rel) => readFileSync(join(root, guard(rel)));
const readText = (root, rel) => readBytes(root, rel).toString('utf8');
const readJSON = (root, rel) => JSON.parse(readText(root, rel));
const lstatTree = (root, rel) => lstatSync(join(root, guard(rel)));
const readlinkTree = (root, rel) => readlinkSync(join(root, guard(rel)));

// The exact D6 snapshot provider tuple (source applicability, not runtime availability).
const D6_PROVIDER = {
  'snapshot:distbench-claude-critique-swarm': 'claude',
  'snapshot:distbench-codex-critique-swarm': 'codex',
  'snapshot:distbench-codex-agent-team': 'codex',
  'snapshot:distbench-worktree-status': 'shared',
  'snapshot:parbench-elegance-reviewer': 'claude',
  'snapshot:organizer-referenced-experiment-loop': 'shared',
  'snapshot:job-search-company-research': 'shared',
  'snapshot:job-search-evidence-contract': 'shared',
  'snapshot:job-search-report-template': 'shared',
  'snapshot:job-search-rendercv': 'shared',
};

function checkOneSource(entry, root) {
  const s = entry.source;
  if (s.type === 'regular-file') {
    const bytes = readBytes(root, s.path);
    if (sha256(bytes) !== s.sha256) throw new Error(`source bytes differ: ${entry.id}`);
    if (entry.sourceUnits.length) verifySourceUnits(entry.id, s.path, bytes, s.sha256, entry.sourceUnits);
  } else if (s.type === 'distribution-symlink') {
    if (!lstatTree(root, s.path).isSymbolicLink()) throw new Error(`expected a symlink: ${entry.id}`);
    const link = readlinkTree(root, s.path);
    if (link !== s.linkTarget) throw new Error(`link target differs: ${entry.id}`);
    if (sha256(Buffer.from(link, 'utf8')) !== s.linkSha256) throw new Error(`link digest differs: ${entry.id}`);
  }
}

function sourcesMatchTree(obligations, root) {
  let bodies = 0;
  const entryIds = new Set(obligations.entries.map(e => e.id));
  const targetIds = new Set(obligations.targets.map(t => t.id));
  for (const entry of obligations.entries) {
    if (entry.source.type === 'regular-file' || entry.source.type === 'distribution-symlink') { checkOneSource(entry, root); bodies++; }
  }
  // Every retained required edge must name a target entry/target that exists; a dropped
  // transitive helper cannot silently shorten the required closure.
  for (const edge of obligations.edges) {
    if (!REQUIRED.has(edge.relationship)) continue;
    if (edge.to.entry !== undefined && !entryIds.has(edge.to.entry)) throw new Error(`required edge ${edge.id} names a missing entry`);
    if (edge.to.target !== undefined && !targetIds.has(edge.to.target)) throw new Error(`required edge ${edge.id} names a missing target`);
  }
  return bodies;
}

function baselineMapAgreement(obligations, adoptionMap, provenance) {
  const targetById = new Map(obligations.targets.map(t => [t.id, t]));
  for (const adoption of adoptionMap.entries) {
    const target = targetById.get(`method:${adoption.id}`);
    if (!target) throw new Error(`baseline ${adoption.id} has no method target`);
    if (`seed/${target.path}` !== adoption.planned_destination) throw new Error(`baseline ${adoption.id} destination differs from the adoption map`);
  }
  const byId = new Map(obligations.entries.map(e => [e.id, e]));
  for (const [id, provider] of Object.entries(D6_PROVIDER)) {
    const entry = byId.get(id);
    if (!entry) throw new Error(`snapshot ${id} is missing`);
    if (entry.applicability !== provider) throw new Error(`snapshot ${id} provider differs from the packet`);
  }
  const pocock = obligations.entries.filter(e => e.collection === 'pocock');
  if (pocock.length !== provenance.skill_count) throw new Error('pocock released count differs from provenance');
  const siblings = obligations.entries.filter(e => e.source.type === 'regular-file' && e.source.path.includes(`${POCOCK}/`));
  if (siblings.length !== provenance.files.length) throw new Error('pocock provenance file count differs');
  const digestByPath = new Map(siblings.map(e => [e.source.path, e.source.sha256]));
  for (const row of provenance.files) {
    if (digestByPath.get(`${POCOCK}/${row.file}`) !== row.sha256) throw new Error(`pocock provenance digest differs: ${row.file}`);
  }
  return { baselines: adoptionMap.entries.length, snapshots: Object.keys(D6_PROVIDER).length, pocock: pocock.length };
}

function inventoryDispositions(obligations, benchmark, application, loamInventory) {
  const key = row => [row.project, row.relative_path ?? row.path, row.sha256].join('|');
  const benchKeys = new Set(benchmark.rows.map(key));
  const obBench = [
    ...obligations.dispositions.notSelected.filter(r => r.inventory === 'benchmark'),
    ...obligations.dispositions.selectionAliases.filter(r => r.inventory === 'benchmark'),
  ];
  const obBenchKeys = new Set(obBench.map(key));
  if (benchKeys.size !== obBenchKeys.size) throw new Error('benchmark disposition count differs from the inventory');
  for (const k of benchKeys) if (!obBenchKeys.has(k)) throw new Error(`benchmark inventory row is undispositioned: ${k}`);
  for (const k of obBenchKeys) if (!benchKeys.has(k)) throw new Error(`disposition row is not in the benchmark inventory: ${k}`);

  const appSha = application.assets.map(a => a.sha256).sort();
  const obAppSha = [
    ...obligations.dispositions.notSelected.filter(r => r.inventory === 'application'),
    ...obligations.dispositions.selectionAliases.filter(r => r.inventory === 'application'),
  ].map(r => r.sha256).sort();
  if (JSON.stringify(appSha) !== JSON.stringify(obAppSha)) throw new Error('application disposition set differs from the inventory');

  if (obligations.dispositions.pluginReferences.length !== benchmark.plugin_references.length) throw new Error('plugin reference count differs');
  const pluginKeys = new Set(benchmark.plugin_references.map(r => `${r.project}|${r.name}`));
  for (const r of obligations.dispositions.pluginReferences) if (!pluginKeys.has(`${r.project}|${r.name}`)) throw new Error(`plugin reference is not in the inventory: ${r.name}`);

  // D2a private rows: compared against the tracked inventory only, never the private body.
  if (obligations.privateMetadata.length !== 5) throw new Error('D2a metadata partition is not exactly five rows');
  const inventorySha = new Map(loamInventory.files.map(f => [f.source_path, f.sha256]));
  for (const row of obligations.privateMetadata) {
    if (!row.path.startsWith(`${PRIVATE_PREFIX}/`)) throw new Error(`private metadata row is not a session-history path: ${row.path}`);
    const historical = inventorySha.get(row.path);
    if (historical === undefined) throw new Error(`private metadata row is missing from the inventory: ${row.path}`);
    if (historical !== row.historicalSha256) throw new Error(`private metadata historical digest differs: ${row.path}`);
  }

  const counts = obligations.counts;
  const actual = {
    baseline: obligations.entries.filter(e => e.collection === 'baseline').length,
    snapshot: obligations.entries.filter(e => e.collection === 'snapshot').length,
    pocock: obligations.entries.filter(e => e.collection === 'pocock').length,
    remote: obligations.entries.filter(e => e.collection === 'remote').length,
    notSelectedBenchmark: obligations.dispositions.notSelected.filter(r => r.inventory === 'benchmark').length,
    notSelectedApplication: obligations.dispositions.notSelected.filter(r => r.inventory === 'application').length,
    pluginReferences: obligations.dispositions.pluginReferences.length,
    selectionAliases: obligations.dispositions.selectionAliases.length,
  };
  for (const [name, value] of Object.entries(actual)) if (counts[name] !== value) throw new Error(`count ${name} differs: ${counts[name]} vs ${value}`);
  return { private: obligations.privateMetadata.length, notSelected: obligations.dispositions.notSelected.length, aliases: obligations.dispositions.selectionAliases.length };
}

// Deep clone that survives readonly obligation typing at runtime.
const cloneOb = () => structuredClone(OBLIGATIONS);
function scratch(prefix) { return mkdtempSync(join(tmpdir(), prefix)); }
function withScratch(prefix, body) {
  const root = scratch(prefix);
  try { return body(root); } finally { rmSync(root, { recursive: true, force: true }); }
}
function writeInto(root, rel, bytes) {
  const abs = join(root, rel);
  mkdirSync(dirname(abs), { recursive: true });
  writeFileSync(abs, bytes);
}

// ---------------------------------------------------------------------------
test('provenance.sources-match-tree', () => {
  const bodies = sourcesMatchTree(OBLIGATIONS, repo);
  assert.ok(bodies > 150);

  // Changed content: a source whose bytes no longer match its recorded digest.
  withScratch('loam-prov-content-', root => {
    const entry = OBLIGATIONS.entries.find(e => e.id === 'baseline:plan-review');
    writeInto(root, entry.source.path, 'mutated body\n');
    assert.throws(() => checkOneSource(entry, root), /source bytes differ/);
  });
  // Directory where a file is expected.
  withScratch('loam-prov-dir-', root => {
    const entry = OBLIGATIONS.entries.find(e => e.id === 'baseline:plan-review');
    mkdirSync(join(root, entry.source.path), { recursive: true });
    assert.throws(() => checkOneSource(entry, root));
  });
  // Link substitution: a distribution symlink repointed to a different target.
  withScratch('loam-prov-link-', root => {
    const entry = OBLIGATIONS.entries.find(e => e.source.type === 'distribution-symlink');
    mkdirSync(join(root, dirname(entry.source.path)), { recursive: true });
    symlinkSync('../../.agents/skills/OTHER', join(root, entry.source.path));
    assert.throws(() => checkOneSource(entry, root), /link target differs/);
  });
  // Omitted transitive helper: a required edge's target entry removed.
  const missingHelper = cloneOb();
  const helperId = 'support:cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md';
  missingHelper.entries = missingHelper.entries.filter(e => e.id !== helperId);
  assert.throws(() => sourcesMatchTree(missingHelper, repo), /names a missing entry/);
});

// ---------------------------------------------------------------------------
test('provenance.baseline-map-agreement', () => {
  const adoptionMap = readJSON(repo, `${INTAKE}/baseline-adoption-map.json`);
  const provenance = readJSON(repo, `${POCOCK}/provenance.json`);
  const report = baselineMapAgreement(OBLIGATIONS, adoptionMap, provenance);
  assert.deepEqual([report.baselines, report.snapshots, report.pocock], [30, 10, 25]);

  // Wrong successor: a baseline destination that no longer matches the adoption map.
  const wrongSuccessor = cloneOb();
  wrongSuccessor.targets.find(t => t.id === 'method:catchup').path = '.agents/skills/catchup/OTHER.md';
  assert.throws(() => baselineMapAgreement(wrongSuccessor, adoptionMap, provenance), /destination differs/);
  // Wrong provider: a snapshot relabelled to the opposite model.
  const wrongProvider = cloneOb();
  wrongProvider.entries.find(e => e.id === 'snapshot:distbench-claude-critique-swarm').applicability = 'codex';
  assert.throws(() => baselineMapAgreement(wrongProvider, adoptionMap, provenance), /provider differs/);
  // Lost sibling attribution: a mattpocock provenance-listed source removed from the packet.
  const lostSibling = cloneOb();
  const sibling = lostSibling.entries.find(e => e.source.type === 'regular-file' && e.source.path.includes(`${POCOCK}/`));
  lostSibling.entries = lostSibling.entries.filter(e => e.id !== sibling.id);
  assert.throws(() => baselineMapAgreement(lostSibling, adoptionMap, provenance), /pocock provenance file count differs/);
});

// ---------------------------------------------------------------------------
test('provenance.inventory-dispositions', () => {
  const benchmark = readJSON(repo, `${INTAKE}/benchmark-inventory.json`);
  const application = readJSON(repo, `${INTAKE}/application-inventory.json`);
  const loamInventory = readJSON(repo, `${INTAKE}/loam-inventory.json`);
  const report = inventoryDispositions(OBLIGATIONS, benchmark, application, loamInventory);
  assert.deepEqual([report.private, report.notSelected, report.aliases], [5, 210, 12]);

  // Boundary controls: a clone without the private directory and a clone whose private body is
  // an unreadable sentinel must give identical metadata qualification, with no private-body read.
  const miniInventory = { files: OBLIGATIONS.privateMetadata.map(row => ({ source_path: row.path, sha256: row.historicalSha256 })) };
  const privateQualify = root => {
    const inventory = readJSON(root, `${INTAKE}/loam-inventory.json`);
    const bySource = new Map(inventory.files.map(f => [f.source_path, f.sha256]));
    return OBLIGATIONS.privateMetadata.map(row => ({ id: row.id, path: row.path, matches: bySource.get(row.path) === row.historicalSha256 }));
  };
  withScratch('loam-prov-clean-', cleanRoot => {
    writeInto(cleanRoot, `${INTAKE}/loam-inventory.json`, JSON.stringify(miniInventory));
    withScratch('loam-prov-sentinel-', sentinelRoot => {
      writeInto(sentinelRoot, `${INTAKE}/loam-inventory.json`, JSON.stringify(miniInventory));
      const sentinel = join(sentinelRoot, PRIVATE_PREFIX, '2026-08-31-main-clief-batch.md');
      mkdirSync(dirname(sentinel), { recursive: true });
      writeFileSync(sentinel, 'SENTINEL: not the real body, and unreadable\n');
      chmodSync(sentinel, 0o000);
      try {
        assert.deepEqual(privateQualify(cleanRoot), privateQualify(sentinelRoot));
        assert.ok(privateQualify(cleanRoot).every(r => r.matches));
        // The boundary refuses any read of the private body.
        assert.throws(() => readBytes(sentinelRoot, `${PRIVATE_PREFIX}/2026-08-31-main-clief-batch.md`), /out of bounds/);
      } finally { chmodSync(sentinel, 0o600); }
    });
  });

  // Missing metadata row, changed historical digest, and a retyped real support source all reject.
  const dropped = cloneOb();
  dropped.privateMetadata = dropped.privateMetadata.slice(1);
  assert.throws(() => inventoryDispositions(dropped, benchmark, application, loamInventory), /not exactly five rows/);
  const changedDigest = cloneOb();
  changedDigest.privateMetadata[0].historicalSha256 = '0'.repeat(64);
  assert.throws(() => inventoryDispositions(changedDigest, benchmark, application, loamInventory), /historical digest differs/);
  const retyped = cloneOb();
  retyped.privateMetadata[0].path = 'bin/lib.sh';
  assert.throws(() => inventoryDispositions(retyped, benchmark, application, loamInventory), /not a session-history path/);

  // Privacy scans of the final outputs.
  const catalog = readJSON(repo, 'seed/.loam/factory/assets/curated-catalog.json');
  const schema = readJSON(repo, 'seed/.loam/factory/assets/curated-catalog.schema.json');
  assert.equal(scanPersonalPaths(catalog).length, 0);
  assert.equal(scanPersonalPaths(schema).length, 0);
  assert.equal(scanPersonalPaths(OBLIGATIONS).length, 0);
  assert.equal(scanPersonalPaths(readText(repo, 'seed/docs/factory/ASSETS.md')).length, 0);
  // Positive control: a schema regex literal that describes a forbidden shape is not user data.
  assert.equal(scanPersonalPaths({ pattern: ['/Us', 'ers/', 'x'].join('') }).length, 0);
  // Negative control: the same shape leaking into prose is caught.
  assert.ok(scanPersonalPaths({ description: ['/Us', 'ers/', 'operator/secret'].join('') }).length > 0);
});
