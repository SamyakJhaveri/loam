// Loam-only source-provenance gate for the curated catalog (plan NATIVE-05 D12/D14). It runs
// from the repository root, where cultivation/, the reviewed intake inventories and the
// mattpocock provenance are present; a rendered recipient project has none of these, which is
// why this gate cannot live in the shipped package. It compares the compiled obligations (the
// reviewed packet) against the actual working tree, never against personal source projects.
// Private session history under seed/.claude/codex-reviews is out of bounds: every filesystem
// read is routed through a boundary that throws on that prefix, and two scratch controls prove
// the metadata qualification is identical whether or not the private bodies are present.
//
// This gate enforces the full reviewed source contract in production (finding 1): body-backed
// sources are re-verified with a regular-file type check and real-path containment, distribution
// links resolve to a contained canonical target, every body-backed entry re-extracts its source
// units unconditionally, snapshot successors are checked as complete tuples, application
// dispositions are matched to the inventory by full identity, and the inventoried support, private
// and remote partitions are compared exactly against loam-inventory.json. Each check carries an
// accepted-control negative that mutates a copy of the obligations or the tree.
import test from 'node:test';
import assert from 'node:assert/strict';
import { chmodSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readlinkSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, isAbsolute, join, relative, sep } from 'node:path';
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

// Real-path containment: resolve the real path of `rel` beneath `root` and reject any escape.
// Returns the repository-relative canonical path (POSIX) of the resolved target.
function containedReal(root, rel) {
  const real = realpathSync(join(root, guard(rel)));
  const relc = relative(realpathSync(root), real);
  if (relc.startsWith('..') || isAbsolute(relc)) throw new Error(`source escapes the tree: ${rel}`);
  return relc.split(sep).join('/');
}

// The exact D6 snapshot successor tuple: successor target, its recipient path, source applicability
// (not runtime availability) and owner. The validator compares the whole tuple, not one field.
const D6 = {
  'snapshot:distbench-claude-critique-swarm': { target: 'method:critique-swarm', path: '.agents/skills/critique-swarm/SKILL.md', applicability: 'claude', owner: 'NATIVE-08' },
  'snapshot:distbench-codex-critique-swarm': { target: 'method:critique-swarm', path: '.agents/skills/critique-swarm/SKILL.md', applicability: 'codex', owner: 'NATIVE-08' },
  'snapshot:distbench-codex-agent-team': { target: 'method:agent-team', path: '.agents/skills/agent-team/SKILL.md', applicability: 'codex', owner: 'NATIVE-08' },
  'snapshot:distbench-worktree-status': { target: 'method:worktree-status', path: '.agents/skills/worktree-status/SKILL.md', applicability: 'shared', owner: 'NATIVE-06' },
  'snapshot:parbench-elegance-reviewer': { target: 'reference:elegance-review', path: '.agents/skills/plan-review/references/elegance-review.md', applicability: 'claude', owner: 'NATIVE-08' },
  'snapshot:organizer-referenced-experiment-loop': { target: 'method:experiment-loop', path: '.agents/skills/experiment-loop/SKILL.md', applicability: 'shared', owner: 'NATIVE-12' },
  'snapshot:job-search-company-research': { target: 'method:evidence-audit', path: '.agents/skills/evidence-audit/SKILL.md', applicability: 'shared', owner: 'NATIVE-12' },
  'snapshot:job-search-evidence-contract': { target: 'reference:evidence-contract', path: '.agents/skills/evidence-audit/references/evidence-contract.md', applicability: 'shared', owner: 'NATIVE-12' },
  'snapshot:job-search-report-template': { target: 'reference:report-template', path: '.agents/skills/evidence-audit/references/report-template.md', applicability: 'shared', owner: 'NATIVE-12' },
  'snapshot:job-search-rendercv': { target: 'method:rendercv', path: '.agents/skills/rendercv/SKILL.md', applicability: 'shared', owner: 'OPS-08' },
};

// A body-backed source is a regular file (type-checked with lstat), contained beneath the tree
// (real-path resolution), byte-identical to its recorded digest, and re-extracts its source units
// exactly. An empty source-unit array on a body-backed entry fails. Distribution links keep their
// literal target and link digest and resolve to a contained canonical in-repository target.
function checkOneSource(entry, root) {
  const s = entry.source;
  if (s.type === 'regular-file') {
    if (!lstatTree(root, s.path).isFile()) throw new Error(`expected a regular file: ${entry.id}`);
    containedReal(root, s.path);
    const bytes = readBytes(root, s.path);
    if (sha256(bytes) !== s.sha256) throw new Error(`source bytes differ: ${entry.id}`);
    if (entry.sourceUnits.length === 0) throw new Error(`body-backed entry has no source units: ${entry.id}`);
    verifySourceUnits(entry.id, s.path, bytes, s.sha256, entry.sourceUnits);
  } else if (s.type === 'distribution-symlink') {
    if (!lstatTree(root, s.path).isSymbolicLink()) throw new Error(`expected a symlink: ${entry.id}`);
    const link = readlinkTree(root, s.path);
    if (link !== s.linkTarget) throw new Error(`link target differs: ${entry.id}`);
    if (sha256(Buffer.from(link, 'utf8')) !== s.linkSha256) throw new Error(`link digest differs: ${entry.id}`);
    let canonical;
    try { canonical = containedReal(root, s.path); } catch { throw new Error(`link canonical target unresolved: ${entry.id}`); }
    if (typeof s.canonicalTarget === 'string' && canonical !== s.canonicalTarget) throw new Error(`link canonical target differs: ${entry.id}`);
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
  for (const [id, expected] of Object.entries(D6)) {
    const entry = byId.get(id);
    if (!entry) throw new Error(`snapshot ${id} is missing`);
    if (!entry.targets.includes(expected.target)) throw new Error(`snapshot ${id} successor differs from the packet`);
    const target = targetById.get(expected.target);
    if (!target || target.path !== expected.path) throw new Error(`snapshot ${id} successor path differs from the packet`);
    if (entry.applicability !== expected.applicability) throw new Error(`snapshot ${id} provider differs from the packet`);
    if (target.owner !== expected.owner) throw new Error(`snapshot ${id} owner differs from the packet`);
  }
  const pocock = obligations.entries.filter(e => e.collection === 'pocock');
  if (pocock.length !== provenance.skill_count) throw new Error('pocock released count differs from provenance');
  const siblings = obligations.entries.filter(e => e.source.type === 'regular-file' && e.source.path.includes(`${POCOCK}/`));
  if (siblings.length !== provenance.files.length) throw new Error('pocock provenance file count differs');
  const digestByPath = new Map(siblings.map(e => [e.source.path, e.source.sha256]));
  for (const row of provenance.files) {
    if (digestByPath.get(`${POCOCK}/${row.file}`) !== row.sha256) throw new Error(`pocock provenance digest differs: ${row.file}`);
  }
  return { baselines: adoptionMap.entries.length, snapshots: Object.keys(D6).length, pocock: pocock.length };
}

// Application dispositions match the application inventory by full identity: every disposition row
// binds to exactly one inventory asset whose original path ends with the row path, whose kind
// equals the row kind and whose digest equals the row digest, and the bijection covers every asset.
function applicationTupleAgreement(obligations, application) {
  const rows = [
    ...obligations.dispositions.notSelected.filter(r => r.inventory === 'application'),
    ...obligations.dispositions.selectionAliases.filter(r => r.inventory === 'application'),
  ];
  const used = new Set();
  for (const row of rows) {
    if (typeof row.project !== 'string' || !row.project) throw new Error(`application row has no project: ${row.path}`);
    const idx = application.assets.findIndex((a, i) => !used.has(i) && a.sha256 === row.sha256 && a.kind === row.kind && (a.original_path.endsWith(`/${row.path}`) || a.original_path === row.path));
    if (idx < 0) throw new Error(`application row has no matching inventory asset (project/path/kind/sha256): ${row.path}`);
    used.add(idx);
  }
  if (used.size !== application.assets.length) throw new Error(`application dispositions do not cover the inventory exactly (${used.size} of ${application.assets.length})`);
  return rows.length;
}

// The inventoried support, private and remote sets partition loam-inventory.json exactly:
// 69 inventoried support records = 62 regular files + 2 distribution links + 5 private records,
// plus the fixed supplemental (non-inventory) support entries. Every inventory file except the five
// private rows is claimed by exactly one entry source with digest agreement; the private-typed
// entries are exactly the five reviewed D2a rows and assert no body-backed claim.
function inventoryPartition(obligations, loamInventory) {
  const privatePaths = new Set(obligations.privateMetadata.map(r => r.path));
  if (privatePaths.size !== obligations.privateMetadata.length) throw new Error('private metadata rows have a duplicate path');
  const bodyByPath = new Map();
  for (const e of obligations.entries) {
    if (e.source.type === 'regular-file' || e.source.type === 'distribution-symlink') {
      if (bodyByPath.has(e.source.path)) throw new Error(`duplicate source path across entries: ${e.source.path}`);
      bodyByPath.set(e.source.path, e);
    }
  }
  for (const file of loamInventory.files) {
    if (privatePaths.has(file.source_path)) continue;
    const entry = bodyByPath.get(file.source_path);
    if (!entry) throw new Error(`inventory file is undispositioned: ${file.source_path}`);
    if (entry.source.type === 'regular-file' && entry.source.sha256 !== file.sha256) throw new Error(`inventory digest differs: ${file.source_path}`);
  }
  const invPaths = new Set(loamInventory.files.map(f => f.source_path));
  const support = obligations.entries.filter(e => e.collection === 'support');
  const regInInv = support.filter(e => e.source.type === 'regular-file' && invPaths.has(e.source.path)).length;
  const linkInInv = support.filter(e => e.source.type === 'distribution-symlink' && invPaths.has(e.source.path)).length;
  const priv = obligations.privateMetadata.length;
  if (regInInv !== 62) throw new Error(`inventoried regular support is ${regInInv}, expected 62`);
  if (linkInInv !== 2) throw new Error(`inventoried distribution-link support is ${linkInInv}, expected 2`);
  if (priv !== 5) throw new Error(`private records are ${priv}, expected 5`);
  if (regInInv + linkInInv + priv !== 69) throw new Error('inventoried support partition is not 69');
  if (obligations.entries.filter(e => e.collection === 'remote').length !== 5) throw new Error('remote entries are not exactly five');

  const privateRowPaths = privatePaths;
  const privateTyped = obligations.entries.filter(e => e.source.type === 'private-local-metadata');
  if (privateTyped.length !== 5) throw new Error(`private-metadata-typed entries are ${privateTyped.length}, expected 5`);
  for (const entry of privateTyped) if (!privateRowPaths.has(entry.source.path)) throw new Error(`entry uses private metadata identity but is not a reviewed D2a row: ${entry.id}`);

  const byId = new Map(obligations.entries.map(e => [e.id, e]));
  const privateIds = new Set(obligations.privateMetadata.map(r => r.id));
  for (const row of obligations.privateMetadata) {
    const entry = byId.get(row.id);
    if (!entry) throw new Error(`private metadata row has no entry: ${row.id}`);
    if (entry.source.type !== 'private-local-metadata') throw new Error(`private row entry is not typed as private metadata: ${row.id}`);
    if (entry.sourceUnits.length || (entry.map && entry.map.length) || entry.targets.length || entry.prerequisites.length) throw new Error(`private metadata record carries a forbidden claim: ${row.id}`);
  }
  for (const edge of obligations.edges) if (privateIds.has(edge.fromEntry)) throw new Error(`private metadata record originates an edge: ${edge.fromEntry}`);
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

  // Application dispositions are compared by full identity tuple, not digest alone.
  applicationTupleAgreement(obligations, application);

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

  // Exact inventoried support/private/remote partition and private-record restrictions.
  inventoryPartition(obligations, loamInventory);

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
  // Directory where a file is expected: the regular-file type check rejects it.
  withScratch('loam-prov-dir-', root => {
    const entry = OBLIGATIONS.entries.find(e => e.id === 'baseline:plan-review');
    mkdirSync(join(root, entry.source.path), { recursive: true });
    assert.throws(() => checkOneSource(entry, root), /expected a regular file/);
  });
  // Erased source units: an empty array on a body-backed entry fails unconditionally.
  withScratch('loam-prov-units-', root => {
    const entry = structuredClone(OBLIGATIONS.entries.find(e => e.id === 'baseline:plan-review'));
    writeInto(root, entry.source.path, readFileSync(join(repo, entry.source.path)));
    entry.sourceUnits = [];
    assert.throws(() => checkOneSource(entry, root), /no source units/);
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

  // Wrong baseline successor: a destination that no longer matches the adoption map.
  const wrongDestination = cloneOb();
  wrongDestination.targets.find(t => t.id === 'method:catchup').path = '.agents/skills/catchup/OTHER.md';
  assert.throws(() => baselineMapAgreement(wrongDestination, adoptionMap, provenance), /destination differs/);
  // Wrong snapshot successor: a snapshot regrouped onto a different method.
  const wrongSuccessor = cloneOb();
  wrongSuccessor.entries.find(e => e.id === 'snapshot:distbench-worktree-status').targets = ['method:catchup'];
  assert.throws(() => baselineMapAgreement(wrongSuccessor, adoptionMap, provenance), /successor differs/);
  // Wrong provider: a snapshot relabelled to the opposite model.
  const wrongProvider = cloneOb();
  wrongProvider.entries.find(e => e.id === 'snapshot:distbench-claude-critique-swarm').applicability = 'codex';
  assert.throws(() => baselineMapAgreement(wrongProvider, adoptionMap, provenance), /provider differs/);
  // Wrong owner: a snapshot successor owner that no longer matches the packet.
  const wrongOwner = cloneOb();
  wrongOwner.targets.find(t => t.id === 'method:worktree-status').owner = 'OPS-99';
  assert.throws(() => baselineMapAgreement(wrongOwner, adoptionMap, provenance), /owner differs/);
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

  // Missing metadata row, changed historical digest, and a retyped private-row path all reject.
  const dropped = cloneOb();
  dropped.privateMetadata = dropped.privateMetadata.slice(1);
  assert.throws(() => inventoryDispositions(dropped, benchmark, application, loamInventory), /not exactly five rows/);
  const changedDigest = cloneOb();
  changedDigest.privateMetadata[0].historicalSha256 = '0'.repeat(64);
  assert.throws(() => inventoryDispositions(changedDigest, benchmark, application, loamInventory), /historical digest differs/);
  const retypedRow = cloneOb();
  retypedRow.privateMetadata[0].path = 'bin/lib.sh';
  assert.throws(() => inventoryDispositions(retypedRow, benchmark, application, loamInventory), /not a session-history path/);
  // A duplicated private tuple replacing another loses a distinct path.
  const dupPrivate = cloneOb();
  dupPrivate.privateMetadata[1] = structuredClone(dupPrivate.privateMetadata[0]);
  assert.throws(() => inventoryDispositions(dupPrivate, benchmark, application, loamInventory), /duplicate path/);
  // An application disposition whose path no longer matches any inventory asset.
  const changedAppPath = cloneOb();
  changedAppPath.dispositions.notSelected.find(r => r.inventory === 'application').path = 'unrelated/file.md';
  assert.throws(() => inventoryDispositions(changedAppPath, benchmark, application, loamInventory), /no matching inventory asset/);
  // Removing an inventoried support entry leaves its inventory file undispositioned.
  const droppedSupport = cloneOb();
  droppedSupport.entries = droppedSupport.entries.filter(e => e.id !== 'support:cultivation/marketplace/README.md');
  assert.throws(() => inventoryDispositions(droppedSupport, benchmark, application, loamInventory), /undispositioned/);
  // Retyping a real support source as private metadata leaves six private-typed entries.
  const retypedSupport = cloneOb();
  retypedSupport.entries.find(e => e.id === 'support:bin/lib.sh').source = { type: 'private-local-metadata', path: 'bin/lib.sh', historicalSha256: '0'.repeat(64), currentSha256: null, readingState: 'metadata-only', bodyVerification: 'not-performed' };
  assert.throws(() => inventoryDispositions(retypedSupport, benchmark, application, loamInventory), /private-metadata-typed entries are 6/);
  // A private-metadata record that asserts a target claim.
  const claimingPrivate = cloneOb();
  claimingPrivate.entries.find(e => e.id === OBLIGATIONS.privateMetadata[0].id).targets = ['method:catchup'];
  assert.throws(() => inventoryDispositions(claimingPrivate, benchmark, application, loamInventory), /forbidden claim/);

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
