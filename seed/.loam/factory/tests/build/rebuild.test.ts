import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { chmodSync, cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createReleaseManifest, payloadFiles, snapshot } from '../../src/installation/package.js';
import { assertCandidateUnchanged, compareRebuilt, createRebuildReference, type RebuildReference } from '../../src/installation/rebuild.js';
import { cleanTestEnvironment } from '../../src/testing/verify.js';

const candidate = fileURLToPath(new URL('../../../', import.meta.url));
const original = snapshot(candidate);
const scratchRoots: string[] = [];
let reference: RebuildReference | undefined;

function scratch(): string {
  const root = mkdtempSync(join(tmpdir(), 'loam-rebuild-case-'));
  scratchRoots.push(root);
  return root;
}

function clone(source: string, destination = join(scratch(), 'candidate'), dependencies = false): string {
  mkdirSync(destination, { recursive: true });
  for (const file of payloadFiles(source)) {
    mkdirSync(dirname(join(destination, file)), { recursive: true });
    cpSync(join(source, file), join(destination, file));
  }
  if (dependencies) cpSync(join(source, 'node_modules'), join(destination, 'node_modules'), { recursive: true });
  return destination;
}

function independentlyBuilt(): RebuildReference {
  if (!reference) {
    reference = createRebuildReference(candidate);
    scratchRoots.push(reference.root);
  }
  return reference;
}

function build(root: string) {
  return spawnSync(process.execPath, [join(root, 'scripts/build.mjs')], {
    cwd: root, env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120_000,
  });
}

function output(root: string, suffix: string): string {
  const file = payloadFiles(root).find((entry) => entry.startsWith('dist/') && entry.endsWith(suffix));
  assert.ok(file, `fixture must contain ${suffix} output`);
  return file;
}

function unchanged(): void { assertCandidateUnchanged(candidate, original); }
after(() => { for (const root of scratchRoots) rmSync(root, { recursive: true, force: true }); });

test('rebuild.exact', () => {
  try {
    const rebuilt = independentlyBuilt();
    assert.notEqual(rebuilt.root, candidate);
    assert.equal(rebuilt.identity.version, 'v24.21.0');
    assert.equal(rebuilt.identity.npm, '11.19.0');
    compareRebuilt(candidate, rebuilt.root);
    assert.deepEqual(snapshot(candidate), snapshot(rebuilt.root));
  } finally { unchanged(); }
});

test('rebuild.stale-source', () => {
  try {
    const stale = clone(candidate);
    const rebuilt = clone(independentlyBuilt().root, undefined, true);
    const source = 'src/installation/rebuild.ts';
    const changed = `${readFileSync(join(stale, source), 'utf8')}\nexport const staleSourceProbe = 'changed';\n`;
    writeFileSync(join(stale, source), changed);
    writeFileSync(join(stale, 'release-manifest.json'), `${JSON.stringify(createReleaseManifest(stale), null, 2)}\n`);
    writeFileSync(join(rebuilt, source), changed);
    const result = build(rebuilt);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    assert.throws(() => compareRebuilt(stale, rebuilt), /Compiled output differs/);
  } finally { unchanged(); }
});

test('rebuild.missing-output', () => {
  try {
    const changed = clone(candidate);
    rmSync(join(changed, output(changed, '.js')));
    assert.throws(() => compareRebuilt(changed, independentlyBuilt().root), /Compiled output file set differs/);
  } finally { unchanged(); }
});

test('rebuild.extra-output', () => {
  try {
    const changed = clone(candidate);
    writeFileSync(join(changed, 'dist/stale-extra.js'), 'export {};\n');
    assert.throws(() => compareRebuilt(changed, independentlyBuilt().root), /Compiled output file set differs/);
  } finally { unchanged(); }
});

test('rebuild.changed-map', () => {
  try {
    const changed = clone(candidate);
    const map = join(changed, output(changed, '.js.map'));
    writeFileSync(map, `${readFileSync(map, 'utf8')} `);
    assert.throws(() => compareRebuilt(changed, independentlyBuilt().root), /Compiled output differs/);
  } finally { unchanged(); }
});

test('rebuild.missing-compiler', () => {
  try {
    const changed = clone(independentlyBuilt().root, undefined, true);
    rmSync(join(changed, 'node_modules/typescript'), { recursive: true });
    const result = build(changed);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Missing local dependency: typescript/);
  } finally { unchanged(); }
});

test('rebuild.ancestor-collision', () => {
  try {
    const ancestor = scratch();
    const changed = clone(independentlyBuilt().root, join(ancestor, 'factory'), true);
    rmSync(join(changed, 'node_modules/typescript'), { recursive: true });
    const poison = join(ancestor, 'node_modules/typescript/bin');
    mkdirSync(poison, { recursive: true });
    const marker = join(ancestor, 'ancestor-compiler-ran');
    writeFileSync(join(ancestor, 'package.json'), '{"type":"commonjs"}\n');
    writeFileSync(join(poison, 'tsc'), `require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'called');\n`);
    const result = build(changed);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Missing local dependency: typescript/);
    assert.equal(existsSync(marker), false, 'ancestor compiler must never execute');
  } finally { unchanged(); }
});

test('rebuild.ancestor-types-collision', () => {
  try {
    const ancestor = scratch();
    const changed = clone(independentlyBuilt().root, join(ancestor, 'factory'), true);
    rmSync(join(changed, 'node_modules/@types/node'), { recursive: true });
    const poison = join(ancestor, 'node_modules/@types/node');
    mkdirSync(poison, { recursive: true });
    writeFileSync(join(poison, 'package.json'), '{"name":"@types/node","version":"24.3.0","types":"index.d.ts"}\n');
    writeFileSync(join(poison, 'index.d.ts'), 'THIS IS NOT VALID TYPESCRIPT;\n');
    const result = build(changed);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Missing local dependency: @types\/node/);
    assert.doesNotMatch(result.stderr + result.stdout, /index\.d\.ts\(/, 'ancestor types must not reach the compiler');
  } finally { unchanged(); }
});

test('rebuild.provider-free-build', () => {
  const previousPath = process.env.PATH;
  try {
    const changed = clone(candidate);
    const sentinels = join(scratch(), 'providers');
    mkdirSync(sentinels);
    const marker = join(sentinels, 'provider-ran');
    for (const provider of ['codex', 'claude']) {
      const path = join(sentinels, provider);
      writeFileSync(path, `#!${process.execPath}\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)}, 'called'); process.exit(99);\n`);
      chmodSync(path, 0o755);
    }
    process.env.PATH = `${sentinels}:${previousPath ?? ''}`;
    const installReport = execFileSync(process.execPath,
      [join(changed, 'scripts/toolchain.mjs'), 'install', changed],
      { cwd: changed, env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120_000 });
    process.stdout.write(installReport);
    const result = build(changed);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    compareRebuilt(candidate, changed);
    assert.equal(existsSync(marker), false, 'install/build must not call native providers');
  } finally {
    if (previousPath === undefined) delete process.env.PATH;
    else process.env.PATH = previousPath;
    unchanged();
  }
});
