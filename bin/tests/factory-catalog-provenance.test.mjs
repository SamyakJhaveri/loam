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
import { OBLIGATIONS, scanPersonalPaths } from '../../seed/.loam/runtime/dist/src/assets/catalog.js';
import { sha256, verifySourceUnits } from '../../seed/.loam/runtime/dist/src/assets/units.js';

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

// The five preservation exclusion classes, read from the curated-catalog schema so the gate binds an
// exclusion to the same closed vocabulary the schema enforces (OBLIGATIONS-FORMAT.md preservation.map,
// mapRow.exclude). A bogus class is not a valid cover form. (finding C)
const EXCLUDE_CLASSES = new Set(readJSON(repo, 'seed/.loam/runtime/assets/curated-catalog.schema.json').$defs.mapRow.properties.exclude.enum);

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
  // Every edge that carries a source-unit anchor names one that exists and belongs to the source
  // body of its own fromEntry: an edge cannot cite a span from a file it does not originate in.
  edgeSourceUnitsOwned(obligations);
  // Every source unit of a body-backed entry is accounted for by a preservation-map row (an adopted
  // mapping or an explicit exclusion): a cleared or shortened map leaves adopted units unpreserved.
  preservationMapCoverage(obligations);
  return bodies;
}

// An edge's source-unit anchor, when present, must be one of the fromEntry's own source units. This
// binds the provenance graph to real spans and rejects a fabricated or foreign sourceUnit. (finding 2)
function edgeSourceUnitsOwned(obligations) {
  const byEntry = new Map(obligations.entries.map(e => [e.id, e]));
  const mirrorSeen = new Set();
  for (const edge of obligations.edges) {
    const from = byEntry.get(edge.fromEntry);
    // The fromEntry must exist before either the anchor rule or the ownership rule can bind. This
    // check sits above the null-anchor branch: an edge whose anchor is nulled AND whose fromEntry is
    // re-parented to a nonexistent entry used to fall through both rules (the null branch found no
    // `from`, hit `continue`, and never reached the missing-fromEntry throw), erasing a required edge
    // from its closure with its anchor gone. It is now caught first. (finding A)
    if (!from) throw new Error(`edge ${edge.id} names a missing fromEntry ${edge.fromEntry}`);
    // An edge is owned by its fromEntry: its id is `<fromEntry>:e<n>`. Without this, a required edge whose
    // anchor is nulled could be re-parented to any existing non-regular-file entry (a distribution-symlink
    // or remote-declaration entry) and escape both the anchor rule and the unit-ownership rule. (finding 1, round 4)
    if (!edge.id.startsWith(`${edge.fromEntry}:`)) throw new Error(`edge ${edge.id} is not owned by fromEntry ${edge.fromEntry}`);
    if (edge.sourceUnit === null || edge.sourceUnit === undefined) {
      // A required edge must carry a source-unit anchor. The only exemption is a distribution-symlink
      // mirror edge: a required-file edge from a distribution-symlink entry whose `to.entry` is the
      // exact SKILL.md of that entry's mirrored canonical target (`${canonicalTarget}/SKILL.md`),
      // whose adopted lessons live in the mirrored skill's own body. A broad "any distribution-symlink
      // fromEntry" exemption let a foreign required edge be re-parented onto a symlink entry, with its
      // id rewritten to pass the ownership-by-id check, and then skip the anchor rule; binding the
      // exemption to the mirrored SKILL.md destination closes that. The two production mirror edges
      // (catchup, fable-prompting) still pass. (finding 1; symlink exemption finding 1, round 4;
      // narrowed finding 3, round 5)
      const dest = edge.to.entry !== undefined ? byEntry.get(edge.to.entry) : undefined;
      const isMirrorEdge = edge.relationship === 'required-file'
        && from.source.type === 'distribution-symlink'
        && typeof from.source.canonicalTarget === 'string'
        && dest !== undefined && dest.source
        && dest.source.path === `${from.source.canonicalTarget}/SKILL.md`;
      // A distribution-symlink entry mirrors exactly one skill, so it has exactly one mirror edge. A
      // second required-file edge re-parented onto the same symlink entry, with its id rewritten and its
      // to.entry set to the mirrored SKILL.md, would otherwise pass as a mirror edge and erase the entry's
      // real edge. Reject a second mirror edge per distribution-symlink entry. (critic-01 round 6)
      if (isMirrorEdge) {
        if (mirrorSeen.has(edge.fromEntry)) throw new Error(`edge ${edge.id} is a duplicate mirror edge for ${edge.fromEntry}`);
        mirrorSeen.add(edge.fromEntry);
      }
      if (REQUIRED.has(edge.relationship) && !isMirrorEdge) {
        throw new Error(`edge ${edge.id} from body-backed ${edge.fromEntry} has no source-unit anchor`);
      }
      continue;
    }
    if (!from.sourceUnits.some(u => u.id === edge.sourceUnit)) throw new Error(`edge ${edge.id} names source unit ${edge.sourceUnit} not owned by ${edge.fromEntry}`);
  }
}

// Every source unit of a body-backed entry must appear in that entry's preservation map exactly once,
// covered by a well-formed row. An entry that declares a successor target (`entry.targets`) maps each
// adopted unit to a declared section of a real target; a target-less entry (D8 gives it no successor)
// may carry a section-only lesson row, and only there is `section` alone a valid cover. Row fields are
// bound: an exclusion names one of the five declared classes, a mapped target is a known target id,
// and the named section is one that target declares (or a nonempty declaration on a target-less
// entry). A cleared, shortened, section-only-on-a-targeted-entry, duplicated or ill-formed map is
// rejected. (findings 2, B, C)
function preservationMapCoverage(obligations) {
  const targetsById = new Map(obligations.targets.map(t => [t.id, t]));
  for (const entry of obligations.entries) {
    if (entry.source.type !== 'regular-file' && entry.source.type !== 'distribution-symlink') {
      // A non-body entry (D2a private-local-metadata, remote-declaration) has no readable body, so D7
      // requires empty source units and an empty preservation map. Copied units or map rows on such an
      // entry are a corruption; the skip must not accept them silently. (critic-01 round 6)
      if (entry.sourceUnits.length > 0 || (entry.map ?? []).length > 0) throw new Error(`entry ${entry.id} is a non-body ${entry.source.type} entry but carries source units or preservation-map rows`);
      continue;
    }
    if (entry.sourceUnits.length === 0) continue;
    const ownUnits = new Set(entry.sourceUnits.map(u => u.id));
    const hasTargets = entry.targets.length > 0;
    const seen = new Set();
    for (const row of entry.map ?? []) {
      // Every row names one of the entry's own source units: a row citing a foreign or invented unit
      // id cannot claim to preserve anything the entry contains. (finding 2)
      if (!ownUnits.has(row.unit)) throw new Error(`entry ${entry.id} preservation-map row names unit ${row.unit} not owned by the entry`);
      // Each unit is disposed of by exactly one row. Otherwise a unit mapped by one row and excluded
      // by another double-counts, and the excluded copy silently drops the adopted mapping. (finding B)
      if (seen.has(row.unit)) throw new Error(`entry ${entry.id} preservation-map has a duplicate row for unit ${row.unit}`);
      seen.add(row.unit);
      if (typeof row.exclude === 'string') {
        // An exclusion covers its unit only when its class is one of the five declared classes. (finding C)
        if (!EXCLUDE_CLASSES.has(row.exclude)) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} names an unknown exclude class ${row.exclude}`);
        // An exclusion is not a mapping: it must not also carry a target or a section. A row that both
        // excludes and names a target/section would double as a delivery mapping and slip an unreviewed
        // successor past the class check, which `continue`s immediately. (critic-01 round 6)
        if ((row.target !== null && row.target !== undefined) || row.section !== undefined) throw new Error(`entry ${entry.id} exclusion map row for unit ${row.unit} also carries a target or section`);
        continue;
      }
      if (hasTargets) {
        // An entry with a successor maps each adopted unit to a declared section of a real target. A
        // section-only (target-stripped) row on such an entry is not a cover: the target must be a
        // known id and the section one that target declares. (findings B, C)
        if (typeof row.target !== 'string' || !targetsById.has(row.target)) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} names target ${row.target} not in obligations.targets`);
        // The target must be one the entry itself declares, not merely a known id. Otherwise a row can be
        // silently re-homed to another entry's successor, dropping the lesson from this entry's own
        // target (the catalog gate only checks the id resolves, not that the entry declares it). (finding 2, round 4)
        if (!entry.targets.includes(row.target)) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} names target ${row.target} not declared by the entry`);
        const target = targetsById.get(row.target);
        if (typeof row.section !== 'string' || !target.sectionKeys.includes(row.section)) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} names section ${row.section} not in target ${row.target}`);
      } else {
        // A target-less entry carries a section-only lesson row; it names no successor, so `target`
        // must be absent (null or omitted, the two production encodings). A non-null, non-undefined
        // target injected onto such a row is rejected: the target-less branch used to validate only
        // the section and silently accepted an invented target. The section must still be a kebab-case
        // declaration (OBLIGATIONS-FORMAT.md). `section` is a cover form only here, never on an entry
        // with targets. (findings B, C; kebab requirement finding 3, round 4; target rejection finding 4, round 5)
        if (row.target !== null && row.target !== undefined) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} carries a target on a target-less entry`);
        if (typeof row.section !== 'string' || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(row.section)) throw new Error(`entry ${entry.id} preservation-map row for unit ${row.unit} has no kebab-case section`);
      }
    }
    for (const unit of entry.sourceUnits) {
      if (!seen.has(unit.id)) throw new Error(`entry ${entry.id} source unit ${unit.id} is not covered by the preservation map`);
    }
  }
}

// Attribution and license evidence against the reviewed source material. Every body-backed entry
// carries a non-empty author and license; every mattpocock upstream file (SKILL.md and its siblings,
// wherever their entry lives) keeps the upstream author and MIT license and cites the UPSTREAM-LICENSE
// evidence file, which must exist in the tree. Erasing an entry's attribution is rejected. (finding 2)
const POCOCK_LICENSE = `${POCOCK}/UPSTREAM-LICENSE`;
function attributionEvidence(obligations, root) {
  let checked = 0;
  for (const entry of obligations.entries) {
    if (entry.source.type !== 'regular-file' && entry.source.type !== 'distribution-symlink') continue;
    const a = entry.attribution;
    if (!a || typeof a !== 'object') throw new Error(`body-backed entry has no attribution: ${entry.id}`);
    if (typeof a.author !== 'string' || a.author === '') throw new Error(`body-backed entry has no attribution author: ${entry.id}`);
    if (typeof a.license !== 'string' || a.license === '') throw new Error(`body-backed entry has no attribution license: ${entry.id}`);
    if (entry.source.type === 'regular-file' && entry.source.path.includes(`${POCOCK}/`)) {
      if (a.author !== 'Matt Pocock' || a.license !== 'MIT') throw new Error(`mattpocock source attribution differs from the upstream: ${entry.id}`);
      if (a.licenseEvidence !== POCOCK_LICENSE) throw new Error(`mattpocock source does not cite the upstream license evidence: ${entry.id}`);
      if (!lstatTree(root, POCOCK_LICENSE).isFile()) throw new Error(`mattpocock upstream license evidence file is missing: ${POCOCK_LICENSE}`);
    }
    checked++;
  }
  return checked;
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

// The originating project of an inventory asset and the path remainder beneath it, derived from the
// asset's original path the way the intake labelled the disposition rows: a `Desktop/<project>/` asset
// yields that project and the path below it; an asset in the operator home yields `user-global` and
// the path below the home directory. Returning the remainder lets the application binding require exact
// path equality rather than a suffix match, so a truncated row path no longer binds. (finding D) This
// is read from the tracked inventory's own paths; no personal path is copied into the catalog.
function projectOfPath(originalPath) {
  const p = String(originalPath);
  const desktop = p.match(/\/Desktop\/([^/]+)\/(.+)$/);
  if (desktop) return { project: desktop[1], remainder: desktop[2] };
  const home = p.match(/\/(?:Users|home)\/[^/]+\/(.+)$/);
  if (home) return { project: 'user-global', remainder: home[1] };
  return { project: 'user-global', remainder: p };
}

// Application dispositions match the application inventory by full identity: every disposition row
// binds to exactly one inventory asset whose path remainder beneath its project root equals the row
// path exactly, whose kind equals the row kind, whose digest equals the row digest and whose
// originating project equals the row project, and the bijection covers every asset. The path is bound
// by exact equality of the remainder, not a suffix match, so a row path truncated to a bare suffix no
// longer binds to its asset, and relabelling a row's project is still rejected. (findings 2, D)
function applicationTupleAgreement(obligations, application) {
  const rows = [
    ...obligations.dispositions.notSelected.filter(r => r.inventory === 'application'),
    ...obligations.dispositions.selectionAliases.filter(r => r.inventory === 'application'),
  ];
  const used = new Set();
  for (const row of rows) {
    if (typeof row.project !== 'string' || !row.project) throw new Error(`application row has no project: ${row.path}`);
    const idx = application.assets.findIndex((a, i) => {
      if (used.has(i) || a.sha256 !== row.sha256 || a.kind !== row.kind) return false;
      const { project, remainder } = projectOfPath(a.original_path);
      return project === row.project && remainder === row.path;
    });
    if (idx < 0) throw new Error(`application row has no matching inventory asset (project/path/kind/sha256): ${row.project} ${row.path}`);
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
  // The benchmark identity tuple includes kind: a disposition may not silently change an asset's
  // recorded kind while keeping its path and digest. (finding 2)
  // Two key functions with no cross-field fallback: benchmark inventory rows key on their relative_path,
  // obligation disposition rows key on their path. A `relative_path ?? path` fallback let an obligation
  // row carry a real relative_path and a bogus path and be keyed on the harmless field. (finding 3)
  const invKey = row => [row.project, row.relative_path, row.kind, row.sha256].join('|');
  const obKey = row => [row.project, row.path, row.kind, row.sha256].join('|');
  const benchKeys = new Set(benchmark.rows.map(invKey));
  const obBench = [
    ...obligations.dispositions.notSelected.filter(r => r.inventory === 'benchmark'),
    ...obligations.dispositions.selectionAliases.filter(r => r.inventory === 'benchmark'),
  ];
  const obBenchKeys = new Set(obBench.map(obKey));
  if (benchKeys.size !== obBenchKeys.size) throw new Error('benchmark disposition count differs from the inventory');
  for (const k of benchKeys) if (!obBenchKeys.has(k)) throw new Error(`benchmark inventory row is undispositioned: ${k}`);
  for (const k of obBenchKeys) if (!benchKeys.has(k)) throw new Error(`disposition row is not in the benchmark inventory: ${k}`);

  // Application dispositions are compared by full identity tuple (project/path/kind/sha256), not digest alone.
  applicationTupleAgreement(obligations, application);

  // Plugin references bind to the inventory by project, name, enabled state and declaration source:
  // the inventory records the declaring file as an absolute path, so the obligation's relative
  // declarationSource must be its project-scoped suffix. Relabelling declarationSource is rejected. (finding 2)
  if (obligations.dispositions.pluginReferences.length !== benchmark.plugin_references.length) throw new Error('plugin reference count differs');
  const pluginByKey = new Map(benchmark.plugin_references.map(r => [`${r.project}|${r.name}`, r]));
  for (const r of obligations.dispositions.pluginReferences) {
    const inv = pluginByKey.get(`${r.project}|${r.name}`);
    if (!inv) throw new Error(`plugin reference is not in the inventory: ${r.name}`);
    if (inv.enabled !== r.enabled) throw new Error(`plugin reference enabled state differs from the inventory: ${r.name}`);
    if (typeof inv.source !== 'string' || !inv.source.endsWith(`/${r.project}/${r.declarationSource}`)) throw new Error(`plugin reference declarationSource differs from the inventory: ${r.name}`);
  }

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

  // Finding 2: a nonexistent edge source-unit anchor. An edge is retargeted to cite a span id that
  // its fromEntry's source body does not contain; ownership binding rejects it by edge id.
  const badUnit = cloneOb();
  const anchored = badUnit.edges.find(e => e.sourceUnit !== null);
  anchored.sourceUnit = `${anchored.fromEntry}:u-does-not-exist`;
  assert.throws(() => edgeSourceUnitsOwned(badUnit), new RegExp(`edge ${anchored.id} names source unit .* not owned`));
  // The same corruption is rejected by the full production check.
  const badUnitFull = cloneOb();
  const anchored2 = badUnitFull.edges.find(e => e.sourceUnit !== null);
  anchored2.sourceUnit = `${anchored2.fromEntry}:u-does-not-exist`;
  assert.throws(() => sourcesMatchTree(badUnitFull, repo), /not owned by/);

  // Finding 2: a cleared preservation map on a body-backed entry leaves its adopted source units
  // uncovered; coverage rejects it by entry id and the first uncovered unit.
  const clearedMap = cloneOb();
  const mapped = clearedMap.entries.find(e => (e.source.type === 'regular-file') && e.sourceUnits.length > 0 && e.map.length > 0);
  mapped.map = [];
  assert.throws(() => preservationMapCoverage(clearedMap), new RegExp(`entry ${mapped.id} source unit .* is not covered`));

  // Finding 1 (round 2): a required edge whose fromEntry is body-backed (regular-file) has its
  // source-unit anchor dropped to null. The ownership guard now refuses a missing anchor instead of
  // skipping it, so the corruption cannot erase the provenance anchor and still pass. It names the edge.
  const droppedAnchor = cloneOb();
  const byEntryAnchor = new Map(droppedAnchor.entries.map(e => [e.id, e]));
  const requiredAnchored = droppedAnchor.edges.find(e => {
    const from = byEntryAnchor.get(e.fromEntry);
    return e.sourceUnit !== null && from && from.source.type === 'regular-file' && REQUIRED.has(e.relationship);
  });
  assert.ok(requiredAnchored, 'a body-backed required edge carrying an anchor exists in production');
  requiredAnchored.sourceUnit = null;
  assert.throws(() => edgeSourceUnitsOwned(droppedAnchor), err => err.message.includes(`edge ${requiredAnchored.id} from body-backed ${requiredAnchored.fromEntry} has no source-unit anchor`));
  // The same corruption is rejected by the full production check.
  const droppedAnchorFull = cloneOb();
  const byEntryAnchor2 = new Map(droppedAnchorFull.entries.map(e => [e.id, e]));
  const requiredAnchored2 = droppedAnchorFull.edges.find(e => {
    const from = byEntryAnchor2.get(e.fromEntry);
    return e.sourceUnit !== null && from && from.source.type === 'regular-file' && REQUIRED.has(e.relationship);
  });
  requiredAnchored2.sourceUnit = null;
  assert.throws(() => sourcesMatchTree(droppedAnchorFull, repo), /has no source-unit anchor/);

  // Finding A (round 3): the fromEntry existence check now sits above the null-anchor branch. An edge
  // whose anchor is nulled AND whose fromEntry is re-parented to a nonexistent entry used to slip past
  // both the anchor rule and the ownership rule (the null branch found no fromEntry, hit `continue`,
  // and never reached the missing-fromEntry throw), erasing a required edge from its closure with the
  // anchor gone. It is now rejected as a missing fromEntry, naming the edge.
  const missingFromEntry = cloneOb();
  const byEntryFrom = new Map(missingFromEntry.entries.map(e => [e.id, e]));
  const reParent = missingFromEntry.edges.find(e => {
    const from = byEntryFrom.get(e.fromEntry);
    return e.sourceUnit !== null && from && from.source.type === 'regular-file' && REQUIRED.has(e.relationship);
  });
  assert.ok(reParent, 'a body-backed required edge carrying an anchor exists in production');
  reParent.sourceUnit = null;
  reParent.fromEntry = 'support:nonexistent';
  assert.throws(() => edgeSourceUnitsOwned(missingFromEntry), err => err.message.includes(`edge ${reParent.id} names a missing fromEntry support:nonexistent`));
  // The same corruption is rejected by the full production check.
  const missingFromEntryFull = cloneOb();
  const byEntryFrom2 = new Map(missingFromEntryFull.entries.map(e => [e.id, e]));
  const reParent2 = missingFromEntryFull.edges.find(e => {
    const from = byEntryFrom2.get(e.fromEntry);
    return e.sourceUnit !== null && from && from.source.type === 'regular-file' && REQUIRED.has(e.relationship);
  });
  reParent2.sourceUnit = null;
  reParent2.fromEntry = 'support:nonexistent';
  assert.throws(() => sourcesMatchTree(missingFromEntryFull, repo), /names a missing fromEntry/);

  // Finding B (round 3): a section-only (target-stripped) row on an entry that declares a successor
  // target. The critic stripped `target` from a catchup row while keeping `section` and it was still
  // accepted; an entry with targets now requires every non-excluded row to name a real target, so the
  // stripped row is no longer a cover. Rejected naming the entry and the unit.
  const strippedTarget = cloneOb();
  const targetedEntry = strippedTarget.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.targets.length > 0 && (e.map ?? []).some(r => typeof r.target === 'string'));
  assert.ok(targetedEntry, 'an entry with a successor target and a target row exists in production');
  const strippedRow = targetedEntry.map.find(r => typeof r.target === 'string');
  const strippedUnit = strippedRow.unit;
  delete strippedRow.target;
  assert.throws(() => preservationMapCoverage(strippedTarget), err => err.message.includes(`entry ${targetedEntry.id} preservation-map row for unit ${strippedUnit} names target`));

  // Finding B (round 3): a duplicate-unit row. A second row for a unit that is already disposed of can
  // no longer double-count as coverage (a mapped row plus an exclude row for the same unit used to be
  // accepted). Rejected naming the entry and the unit.
  const dupUnit = cloneOb();
  const dupEntry = dupUnit.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.map.length > 0);
  const dupRow = structuredClone(dupEntry.map[0]);
  dupEntry.map.push(dupRow);
  assert.throws(() => preservationMapCoverage(dupUnit), err => err.message.includes(`entry ${dupEntry.id} preservation-map has a duplicate row for unit ${dupRow.unit}`));

  // Finding C (round 3): a mapped target that is not a known target id. On an entry with targets the
  // target must resolve in obligations.targets; a fabricated id is rejected, naming the unit and id.
  const badTargetId = cloneOb();
  const badTargetEntry = badTargetId.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.targets.length > 0 && (e.map ?? []).some(r => typeof r.target === 'string'));
  const badTargetRow = badTargetEntry.map.find(r => typeof r.target === 'string');
  badTargetRow.target = 'method:nonexistent';
  assert.throws(() => preservationMapCoverage(badTargetId), err => err.message.includes(`entry ${badTargetEntry.id} preservation-map row for unit ${badTargetRow.unit} names target method:nonexistent not in obligations.targets`));

  // Finding C (round 3): an exclusion whose class is not one of the five declared classes is not a
  // cover; rejected naming the unit and the bogus class.
  const badExclude = cloneOb();
  const excludeEntry = badExclude.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && (e.map ?? []).some(r => typeof r.exclude === 'string'));
  const excludeRow = excludeEntry.map.find(r => typeof r.exclude === 'string');
  excludeRow.exclude = 'bogus-class';
  assert.throws(() => preservationMapCoverage(badExclude), err => err.message.includes(`entry ${excludeEntry.id} preservation-map row for unit ${excludeRow.unit} names an unknown exclude class bogus-class`));

  // Finding C (round 3): an empty section string on a target-less entry's section-only row is not a
  // kebab-case declaration and does not cover its unit; rejected naming the unit.
  const emptySection = cloneOb();
  const targetlessEntry = emptySection.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.targets.length === 0 && (e.map ?? []).some(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string'));
  assert.ok(targetlessEntry, 'a target-less entry with a section-only row exists in production');
  const emptyRow = targetlessEntry.map.find(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string');
  emptyRow.section = '';
  assert.throws(() => preservationMapCoverage(emptySection), err => err.message.includes(`entry ${targetlessEntry.id} preservation-map row for unit ${emptyRow.unit} has no kebab-case section`));

  // Finding 2 (round 2): a ghost-unit preservation-map row. A well-formed row (it carries a section)
  // cites a unit id the entry does not own, so it cannot claim coverage; it is rejected by entry and unit.
  const ghostRow = cloneOb();
  const ghosted = ghostRow.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.map.length > 0);
  const ghostUnitId = `${ghosted.id}:u-does-not-exist`;
  ghosted.map = [{ unit: ghostUnitId, section: 'invented-section' }, ...ghosted.map];
  assert.throws(() => preservationMapCoverage(ghostRow), err => err.message.includes(`entry ${ghosted.id} preservation-map row names unit ${ghostUnitId} not owned by the entry`));

  // Finding 1 (round 4): a required edge whose anchor is nulled, re-parented to a distribution-symlink
  // entry. The old rule fired only for regular-file sources, so this slipped past the anchor rule; the
  // symlink exemption keeps the two real symlink e1 edges valid while ownership by edge id rejects the
  // foreign re-parent, naming the edge. (link re-parent)
  const linkReparent = cloneOb();
  const symlinkEntry = linkReparent.entries.find(e => e.source.type === 'distribution-symlink');
  assert.ok(symlinkEntry, 'a distribution-symlink entry exists in production');
  const lrByEntry = new Map(linkReparent.entries.map(e => [e.id, e]));
  const lrEdge = linkReparent.edges.find(e => { const f = lrByEntry.get(e.fromEntry); return e.sourceUnit !== null && f && f.source.type === 'regular-file' && REQUIRED.has(e.relationship); });
  lrEdge.sourceUnit = null;
  lrEdge.fromEntry = symlinkEntry.id;
  assert.throws(() => sourcesMatchTree(linkReparent, repo), err => err.message.includes(`edge ${lrEdge.id} is not owned by fromEntry ${symlinkEntry.id}`));

  // Finding 1 (round 4): the same nulled-anchor re-parent to a remote-declaration entry, which escaped
  // all three cases before. Ownership by edge id rejects it, naming the edge. (remote re-parent)
  const remoteReparent = cloneOb();
  const remoteEntry = remoteReparent.entries.find(e => e.source.type === 'remote-declaration');
  assert.ok(remoteEntry, 'a remote-declaration entry exists in production');
  const rrByEntry = new Map(remoteReparent.entries.map(e => [e.id, e]));
  const rrEdge = remoteReparent.edges.find(e => { const f = rrByEntry.get(e.fromEntry); return e.sourceUnit !== null && f && f.source.type === 'regular-file' && REQUIRED.has(e.relationship); });
  rrEdge.sourceUnit = null;
  rrEdge.fromEntry = remoteEntry.id;
  assert.throws(() => sourcesMatchTree(remoteReparent, repo), err => err.message.includes(`edge ${rrEdge.id} is not owned by fromEntry ${remoteEntry.id}`));

  // Finding 2 (round 4): a targeted entry's row retargeted to a known target the entry does not declare.
  // Every baseline:catchup row could be re-homed to method:fable-prompting and accepted, so the lessons
  // silently left method:catchup; the entry-declared-target rule rejects it, naming the entry and unit.
  const foreignTarget = cloneOb();
  const catchupEntry = foreignTarget.entries.find(e => e.id === 'baseline:catchup');
  assert.ok(catchupEntry && catchupEntry.targets.length > 0, 'baseline:catchup is a targeted entry in production');
  const catchupRow = catchupEntry.map.find(r => typeof r.target === 'string');
  catchupRow.target = 'method:fable-prompting';
  catchupRow.section = 'when-to-use';
  assert.throws(() => preservationMapCoverage(foreignTarget), err => err.message.includes(`entry baseline:catchup preservation-map row for unit ${catchupRow.unit} names target method:fable-prompting not declared by the entry`));

  // Finding 3 (round 4): a non-kebab section on a target-less entry's section-only row. Section keys are
  // kebab-case declarations (OBLIGATIONS-FORMAT.md), so a free-text section no longer covers its unit.
  const nonKebab = cloneOb();
  const nkEntry = nonKebab.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.targets.length === 0 && (e.map ?? []).some(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string'));
  assert.ok(nkEntry, 'a target-less entry with a section-only row exists in production');
  const nkRow = nkEntry.map.find(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string');
  nkRow.section = 'Not A Kebab Key!';
  assert.throws(() => preservationMapCoverage(nonKebab), err => err.message.includes(`entry ${nkEntry.id} preservation-map row for unit ${nkRow.unit} has no kebab-case section`));

  // Finding 3 (round 5 / candidate-04): the narrowed distribution-symlink anchor exemption. A
  // body-backed required edge is re-parented onto a distribution-symlink entry with its anchor nulled
  // AND its id rewritten to `${symlink}:e2`, so it passes the ownership-by-id check. Its destination is
  // not the mirrored `${canonicalTarget}/SKILL.md`, so the exemption (required-file to the mirrored
  // SKILL.md only) does not apply and the missing anchor is rejected, naming the edge. The old broad
  // "any distribution-symlink fromEntry" exemption accepted this unrelated required edge.
  const rewrittenReparent = cloneOb();
  const rwSymlink = rewrittenReparent.entries.find(e => e.source.type === 'distribution-symlink');
  assert.ok(rwSymlink, 'a distribution-symlink entry exists in production');
  const rwByEntry = new Map(rewrittenReparent.entries.map(e => [e.id, e]));
  const rwEdge = rewrittenReparent.edges.find(e => { const f = rwByEntry.get(e.fromEntry); return e.sourceUnit !== null && f && f.source.type === 'regular-file' && REQUIRED.has(e.relationship); });
  rwEdge.sourceUnit = null;
  rwEdge.fromEntry = rwSymlink.id;
  rwEdge.id = `${rwSymlink.id}:e2`;
  assert.throws(() => sourcesMatchTree(rewrittenReparent, repo), err => err.message.includes(`edge ${rwEdge.id}`) && err.message.includes('has no source-unit anchor'));
  // The two production mirror edges (catchup, fable-prompting) still resolve under the narrowed
  // exemption: sourcesMatchTree already ran clean above, and both are required-file edges to their
  // mirrored SKILL.md.
  const mirrorEdges = OBLIGATIONS.edges.filter(e => { const f = OBLIGATIONS.entries.find(x => x.id === e.fromEntry); return f && f.source.type === 'distribution-symlink' && e.relationship === 'required-file'; });
  assert.equal(mirrorEdges.length, 2);
  for (const e of mirrorEdges) {
    const f = OBLIGATIONS.entries.find(x => x.id === e.fromEntry);
    const dest = OBLIGATIONS.entries.find(x => x.id === e.to.entry);
    assert.equal(dest.source.path, `${f.source.canonicalTarget}/SKILL.md`);
  }

  // Finding 4 (round 5 / candidate-04): a target injected onto a target-less entry's section-only row.
  // The target-less branch used to validate only the section and accepted an invented target; it now
  // rejects any non-null, non-undefined target, naming the entry and unit. Production's 207 null-target
  // and 15 target-omitting section rows still pass (sourcesMatchTree ran clean above).
  const injectedTarget = cloneOb();
  const itEntry = injectedTarget.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && e.targets.length === 0 && (e.map ?? []).some(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string'));
  assert.ok(itEntry, 'a target-less entry with a section-only row exists in production');
  const itRow = itEntry.map.find(r => typeof r.section === 'string' && typeof r.target !== 'string' && typeof r.exclude !== 'string');
  itRow.target = 'method:nonexistent';
  assert.throws(() => preservationMapCoverage(injectedTarget), err => err.message.includes(`entry ${itEntry.id} preservation-map row for unit ${itRow.unit} carries a target on a target-less entry`));

  // critic-01 round 6 (a): a second mirror edge on a distribution-symlink entry. A foreign required-file
  // edge re-parented onto the symlink entry, its id rewritten to `<symlink>:e2` and its to.entry set to
  // the mirrored SKILL.md, would pass as a mirror edge and erase the entry's real edge. Rejected as a
  // duplicate mirror edge, naming the edge and fromEntry.
  const dupMirror = cloneOb();
  const dmByEntry = new Map(dupMirror.entries.map(e => [e.id, e]));
  const realMirror = dupMirror.edges.find(e => { const f = dmByEntry.get(e.fromEntry); return (e.sourceUnit === null || e.sourceUnit === undefined) && e.relationship === 'required-file' && f && f.source.type === 'distribution-symlink'; });
  assert.ok(realMirror, 'a distribution-symlink mirror edge exists in production');
  const secondMirror = structuredClone(realMirror);
  secondMirror.id = `${realMirror.fromEntry}:e2`;
  dupMirror.edges.push(secondMirror);
  assert.throws(() => sourcesMatchTree(dupMirror, repo), err => err.message.includes(`edge ${secondMirror.id} is a duplicate mirror edge for ${realMirror.fromEntry}`));

  // critic-01 round 6 (b): an exclusion row that also carries a target and a section. The class check
  // used to `continue` immediately, so the row doubled as a delivery mapping to an unreviewed successor.
  // Rejected naming the entry and unit.
  const excludePlus = cloneOb();
  const epEntry = excludePlus.entries.find(e => e.source.type === 'regular-file' && e.sourceUnits.length > 0 && (e.map ?? []).some(r => typeof r.exclude === 'string'));
  assert.ok(epEntry, 'an entry with an exclusion row exists in production');
  const epRow = epEntry.map.find(r => typeof r.exclude === 'string');
  epRow.target = 'method:catchup';
  epRow.section = 'zzz';
  assert.throws(() => preservationMapCoverage(excludePlus), err => err.message.includes(`entry ${epEntry.id} exclusion map row for unit ${epRow.unit} also carries a target or section`));

  // critic-01 round 6 (c): a D2a private-local-metadata entry given copied source units. Non-body entries
  // are skipped before any emptiness check, so D7's empty-units/empty-map rule was unenforced. The id is
  // taken from OBLIGATIONS.privateMetadata at runtime, never typed. Rejected naming the entry.
  const d2aUnits = cloneOb();
  const privId = d2aUnits.privateMetadata[0].id;
  const privEntry = d2aUnits.entries.find(e => e.id === privId);
  assert.ok(privEntry && privEntry.source.type === 'private-local-metadata', 'a D2a private-local-metadata entry exists in production');
  privEntry.sourceUnits = [{ id: `${privId}:u1`, role: 'body', start: 1, end: 1, sha256: '0'.repeat(64) }];
  assert.throws(() => preservationMapCoverage(d2aUnits), err => err.message.includes(`entry ${privId} is a non-body private-local-metadata entry but carries source units or preservation-map rows`));
});

// ---------------------------------------------------------------------------
test('provenance.baseline-map-agreement', () => {
  const adoptionMap = readJSON(repo, `${INTAKE}/baseline-adoption-map.json`);
  const provenance = readJSON(repo, `${POCOCK}/provenance.json`);
  const report = baselineMapAgreement(OBLIGATIONS, adoptionMap, provenance);
  assert.deepEqual([report.baselines, report.snapshots, report.pocock], [30, 10, 25]);

  // Finding 2: attribution and license evidence. Every body-backed source keeps a named author and
  // license, and every mattpocock upstream file cites the UPSTREAM-LICENSE evidence in the tree.
  assert.ok(attributionEvidence(OBLIGATIONS, repo) > 150);
  // Erased sibling attribution: the handoff openai.yaml sibling loses its attribution record.
  const erasedAttribution = cloneOb();
  const siblingId = 'support:docs/architecture-working/tooling/mattpocock-skills/handoff/agents/openai.yaml';
  const sib = erasedAttribution.entries.find(e => e.id === siblingId);
  assert.ok(sib, 'handoff openai.yaml sibling entry present');
  sib.attribution = null;
  assert.throws(() => attributionEvidence(erasedAttribution, repo), new RegExp(`no attribution: ${siblingId}`));
  // Dropping only the upstream license evidence pointer is also rejected for a mattpocock file.
  const droppedEvidence = cloneOb();
  droppedEvidence.entries.find(e => e.id === siblingId).attribution.licenseEvidence = null;
  assert.throws(() => attributionEvidence(droppedEvidence, repo), /does not cite the upstream license evidence/);

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
  // Finding 2: an application disposition relabelled to an unrelated project (path/kind/digest intact).
  const changedAppProject = cloneOb();
  changedAppProject.dispositions.selectionAliases.find(r => r.inventory === 'application').project = 'unrelated-project';
  assert.throws(() => inventoryDispositions(changedAppProject, benchmark, application, loamInventory), /no matching inventory asset \(project\/path\/kind\/sha256\): unrelated-project/);
  // Finding D (round 3): an application row whose path is truncated to a bare suffix. The binding now
  // requires the asset's path remainder beneath its project root to equal the row path exactly, not
  // merely end with it, so the truncated path no longer binds to its asset (its digest, kind and
  // project still pin it, but the recorded path is wrong). The truncation is built from the row's own
  // relative path at runtime, so no personal path appears in the test source. (D11)
  const truncatedAppPath = cloneOb();
  const truncRow = truncatedAppPath.dispositions.notSelected.find(r => r.inventory === 'application' && r.path.includes('/'));
  assert.ok(truncRow, 'a not-selected application row with a nested path exists in production');
  truncRow.path = truncRow.path.split('/').pop();
  assert.throws(() => inventoryDispositions(truncatedAppPath, benchmark, application, loamInventory), /no matching inventory asset/);
  // Finding 2: a benchmark disposition whose kind is changed while its project/path/digest are intact.
  const changedBenchKind = cloneOb();
  changedBenchKind.dispositions.notSelected.find(r => r.inventory === 'benchmark').kind = 'not-the-real-kind';
  assert.throws(() => inventoryDispositions(changedBenchKind, benchmark, application, loamInventory), /undispositioned/);
  // Finding 3 (round 2): a benchmark disposition row that carries a real relative_path and a bogus
  // path. With the fallback removed the obligation row keys on its path alone, so the bogus path no
  // longer hides behind the harmless relative_path and the row is undispositioned.
  const spoofedPath = cloneOb();
  const spoofRow = spoofedPath.dispositions.notSelected.find(r => r.inventory === 'benchmark');
  spoofRow.relative_path = spoofRow.path;
  spoofRow.path = 'bogus/file.md';
  assert.throws(() => inventoryDispositions(spoofedPath, benchmark, application, loamInventory), /undispositioned/);
  // Finding 2: a plugin reference whose declaration source is changed to an unrelated file.
  const changedPluginSource = cloneOb();
  changedPluginSource.dispositions.pluginReferences[0].declarationSource = '.codex/config.toml';
  assert.throws(() => inventoryDispositions(changedPluginSource, benchmark, application, loamInventory), /declarationSource differs from the inventory/);
  // Finding 2: a plugin reference whose enabled state is flipped away from the inventory.
  const changedPluginEnabled = cloneOb();
  changedPluginEnabled.dispositions.pluginReferences[0].enabled = !changedPluginEnabled.dispositions.pluginReferences[0].enabled;
  assert.throws(() => inventoryDispositions(changedPluginEnabled, benchmark, application, loamInventory), /enabled state differs from the inventory/);
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
  const catalog = readJSON(repo, 'seed/.loam/runtime/assets/curated-catalog.json');
  const schema = readJSON(repo, 'seed/.loam/runtime/assets/curated-catalog.schema.json');
  assert.equal(scanPersonalPaths(catalog).length, 0);
  assert.equal(scanPersonalPaths(schema).length, 0);
  assert.equal(scanPersonalPaths(OBLIGATIONS).length, 0);
  assert.equal(scanPersonalPaths(readText(repo, 'seed/docs/runtime/ASSETS.md')).length, 0);
  // Positive control: a schema regex literal that describes a forbidden shape is not user data - but
  // only when the scan is labelled `schema`; the `pattern`-key exemption is confined to that document. (finding 7)
  assert.equal(scanPersonalPaths({ pattern: ['/Us', 'ers/', 'x'].join('') }, 'schema').length, 0);
  // Finding 7 (round 2): the same `pattern` key is NOT exempt outside the schema document.
  assert.ok(scanPersonalPaths({ pattern: ['/Us', 'ers/', 'x'].join('') }).length > 0);
  // Negative control: the same shape leaking into prose is caught.
  assert.ok(scanPersonalPaths({ description: ['/Us', 'ers/', 'operator/secret'].join('') }).length > 0);
});
