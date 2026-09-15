import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  accessSync, chmodSync, constants, copyFileSync, existsSync, lstatSync,
  mkdirSync, mkdtempSync, readdirSync, readFileSync, readlinkSync, realpathSync,
  rmSync, symlinkSync, writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, isAbsolute, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { cleanEnvironment, toolchain } from '../../seed/.loam/factory/scripts/toolchain.mjs';
import { payloadFiles, snapshot, verifyPackage } from '../../seed/.loam/factory/dist/src/installation/package.js';

const repository = fileURLToPath(new URL('../../', import.meta.url));
const factory = join(repository, 'seed/.loam/factory');
const privateDirectories = ['node_modules', '.cache', '.state', 'runtime-installation'];
const sortPaths = paths => paths.sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)));

function isolatedEnvironment(root, tools) {
  const environment = cleanEnvironment();
  for (const key of Object.keys(environment)) {
    if (/^(git_.*|pythonpath|pythonhome|copier_.*)$/i.test(key)) delete environment[key];
  }
  const locations = {
    HOME: join(root, 'home'), XDG_CONFIG_HOME: join(root, 'config'),
    XDG_CACHE_HOME: join(root, 'cache'), XDG_DATA_HOME: join(root, 'data'),
    XDG_STATE_HOME: join(root, 'state'),
  };
  for (const location of Object.values(locations)) mkdirSync(location, { recursive: true });
  return { ...environment, ...locations, PATH: `${join(root, 'sentinels')}:${dirname(tools.node)}:${environment.PATH ?? ''}` };
}

function copierExecutable(environment) {
  const declared = environment.LOAM_FACTORY_COPIER;
  if (!declared || !isAbsolute(declared)) throw new Error('LOAM_FACTORY_COPIER must name an absolute executable');
  let executable;
  try {
    executable = realpathSync(declared);
    assert.ok(lstatSync(executable).isFile());
    accessSync(executable, constants.X_OK);
  } catch { throw new Error('Declared Copier executable is missing or not executable'); }
  const version = execFileSync(executable, ['--version'], { env: environment, encoding: 'utf8', timeout: 30_000 }).trim();
  if (version !== 'copier 9.16.0') throw new Error(`Copier version mismatch: ${version}`);
  return executable;
}

// Preserve checked-in symlinks as links. Never follow them while acquiring the
// source snapshot, and never read denied environment files or live factory state.
function copySeed(source, target, relative = '') {
  mkdirSync(target, { recursive: true });
  for (const name of readdirSync(source)) {
    if (name.startsWith('.env') || name === '.git') continue;
    const path = relative ? `${relative}/${name}` : name;
    if (privateDirectories.some(directory => path === `.loam/factory/${directory}`)) continue;
    const input = join(source, name);
    const output = join(target, name);
    const info = lstatSync(input);
    if (info.isSymbolicLink()) symlinkSync(readlinkSync(input), output);
    else if (info.isDirectory()) copySeed(input, output, path);
    else if (info.isFile()) copyFileSync(input, output);
    else throw new Error(`Unsupported seed entry: ${path}`);
  }
}

function withRenderedPayload(injectPrivate, inspect) {
  const before = snapshot(factory);
  const copierBefore = readFileSync(join(repository, 'copier.yml'));
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'loam-release-render-')));
  try {
    const tools = toolchain();
    const env = isolatedEnvironment(root, tools);
    const copier = copierExecutable(env);
    const missing = { ...env, LOAM_FACTORY_COPIER: join(root, 'absent-copier') };
    assert.throws(() => copierExecutable(missing), /Declared Copier executable is missing/);
    assert.throws(() => copierExecutable({ ...env, LOAM_FACTORY_COPIER: '' }), /must name an absolute executable/);
    const template = join(root, 'template');
    const project = join(root, 'recipient');
    copySeed(join(repository, 'seed'), join(template, 'seed'));
    copyFileSync(join(repository, 'copier.yml'), join(template, 'copier.yml'));
    assert.equal(existsSync(join(template, '.git')), false);
    if (injectPrivate) {
      for (const directory of privateDirectories) {
        const location = join(template, 'seed/.loam/factory', directory);
        mkdirSync(location, { recursive: true });
        writeFileSync(join(location, 'private-sentinel.txt'), `must not ship: ${directory}\n`);
      }
    }
    mkdirSync(join(root, 'sentinels'));
    const marker = join(root, 'provider-ran');
    for (const provider of ['codex', 'claude']) {
      const executable = join(root, 'sentinels', provider);
      writeFileSync(executable, `#!${tools.node}\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)}, 'called'); process.exit(99);\n`);
      chmodSync(executable, 0o755);
    }
    execFileSync(copier, ['copy', '--trust', '--skip-tasks', '--defaults',
      '--data', 'project_name=fixture', '--data', 'github_repo=',
      '--data', 'project_kind=other', template, project],
    { cwd: root, env, stdio: 'pipe', timeout: 60_000 });
    assert.equal(existsSync(join(project, '.git')), false, 'Copier tasks must not initialize Git');
    assert.ok(existsSync(join(project, '_gh_setup.sh')), 'skipped cleanup task must leave its helper unexecuted');
    assert.equal(existsSync(marker), false, 'render must not call native providers');
    const rendered = join(project, '.loam/factory');
    inspect({ rendered, before, env });
    console.log(JSON.stringify({ kind: 'release-render', toolchain: tools.identity,
      copier: '9.16.0', injectedPrivateState: injectPrivate, qualification: verifyPackage(rendered) }));
  } finally {
    assert.deepEqual(snapshot(factory), before, 'release fixture changed the source candidate');
    assert.ok(readFileSync(join(repository, 'copier.yml')).equals(copierBefore), 'release fixture changed Copier configuration');
    rmSync(root, { recursive: true, force: true });
  }
}

test('render.exact-payload', () => {
  withRenderedPayload(false, ({ rendered, before, env }) => {
    const indexed = execFileSync('git', ['-C', repository, 'ls-files', '-z', '--', 'seed/.loam/factory'],
      { env, encoding: 'utf8', timeout: 30_000 }).split('\0').filter(Boolean)
      .map(path => path.slice('seed/.loam/factory/'.length));
    assert.deepEqual(sortPaths(indexed), payloadFiles(factory), 'Git index and complete factory payload must match both ways');
    assert.deepEqual(snapshot(rendered), before, 'Copier must deliver every source/build/manifest byte');
    assert.ok(verifyPackage(rendered).files > 0, 'rendered qualification must be nonempty');
  });
});

test('render.private-exclusions', () => {
  withRenderedPayload(true, ({ rendered, before }) => {
    const leaked = privateDirectories.filter(directory => existsSync(join(rendered, directory)));
    assert.deepEqual(leaked, [], 'private factory directories must not render');
    assert.deepEqual(snapshot(rendered), before, 'excluding private state must preserve the exact public payload');
  });
});
