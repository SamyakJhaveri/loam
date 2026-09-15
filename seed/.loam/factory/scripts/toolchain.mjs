import { execFileSync } from 'node:child_process';
import { lstatSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { isAbsolute, join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

export function cleanEnvironment(extra = {}) {
  const environment = { ...process.env };
  for (const name of Object.keys(environment)) {
    if (/^(node_options|node_path|node_test_.*|npm_config_.*)$/i.test(name)) delete environment[name];
  }
  return { ...environment, ...extra };
}

export function toolchain() {
  const root = process.env.LOAM_FACTORY_TOOLCHAIN;
  if (!root || !isAbsolute(root)) throw new Error('LOAM_FACTORY_TOOLCHAIN must name an absolute Node distribution directory');
  const node = realpathSync(join(root, 'bin/node'));
  const npm = realpathSync(join(root, 'lib/node_modules/npm/bin/npm-cli.js'));
  if (realpathSync(process.execPath) !== node || process.version !== 'v24.21.0') {
    throw new Error('Run this gate with the declared Node v24.21.0 executable');
  }
  const npmVersion = execFileSync(node, [npm, '--version'], { env: cleanEnvironment(), encoding: 'utf8' }).trim();
  if (npmVersion !== '11.19.0') throw new Error('The declared bundled npm must be 11.19.0');
  return { node, npm, identity: { execPath: node, version: process.version, npm: npmVersion, platform: process.platform, arch: process.arch } };
}

export function assertDependencies(root) {
  const expected = { 'typescript': '5.9.3', '@types/node': '24.3.0', 'undici-types': '7.10.0' };
  const lock = JSON.parse(readFileSync(join(root, 'package-lock.json'), 'utf8'));
  const names = Object.keys(lock.packages).filter(name => name !== '').sort();
  const wanted = Object.keys(expected).map(name => `node_modules/${name}`).sort();
  if (JSON.stringify(names) !== JSON.stringify(wanted)) throw new Error('Unexpected locked dependency population');
  for (const name of ['node_modules', 'node_modules/@types']) {
    if (!lstatSync(join(root, name)).isDirectory() || lstatSync(join(root, name)).isSymbolicLink()) throw new Error(`Nonlocal dependency directory: ${name}`);
  }
  for (const [name, version] of Object.entries(expected)) {
    const directory = join(root, 'node_modules', name);
    let info;
    try { info = lstatSync(directory); } catch { throw new Error(`Missing local dependency: ${name}`); }
    if (!info.isDirectory() || info.isSymbolicLink()) throw new Error(`Nonlocal dependency: ${name}`);
    const installed = JSON.parse(readFileSync(join(directory, 'package.json'), 'utf8'));
    if (installed.version !== version || lock.packages[`node_modules/${name}`].version !== version) throw new Error(`Dependency version mismatch: ${name}`);
    if (lock.packages[`node_modules/${name}`].hasInstallScript) throw new Error(`Dependency lifecycle script: ${name}`);
    for (const lifecycle of ['preinstall', 'install', 'postinstall', 'prepare']) {
      if (installed.scripts?.[lifecycle]) throw new Error(`Dependency lifecycle script: ${name}/${lifecycle}`);
    }
  }
  const project = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  for (const lifecycle of ['preinstall', 'install', 'postinstall', 'prepare']) {
    if (project.scripts?.[lifecycle]) throw new Error(`Factory lifecycle script: ${lifecycle}`);
  }
}

export function npmInstall(root) {
  // npm must see the same canonical directory as process.cwd() on macOS.
  root = realpathSync(root);
  const tools = toolchain();
  const scratch = mkdtempSync(join(tmpdir(), 'loam-npm-'));
  const userconfig = join(scratch, 'npm-user.conf');
  const globalconfig = join(scratch, 'npm-global.conf');
  const cache = join(scratch, 'npm-cache');
  writeFileSync(userconfig, '');
  writeFileSync(globalconfig, '');
  const flags = ['--prefix', root, '--userconfig', userconfig, '--globalconfig', globalconfig, '--cache', cache, '--ignore-scripts', '--no-audit', '--no-fund'];
  const env = cleanEnvironment();
  try {
    const config = execFileSync(tools.node, [tools.npm, 'config', 'list', '--json', ...flags], { cwd: root, env, encoding: 'utf8' });
    const resolved = JSON.parse(config);
    if (resolved.userconfig !== userconfig || resolved.globalconfig !== globalconfig || resolved.cache !== cache || resolved['ignore-scripts'] !== true || resolved['legacy-peer-deps'] !== false || resolved['install-links'] !== false) {
      throw new Error('npm configuration isolation assertion failed');
    }
    console.log(JSON.stringify({ kind: 'npm-configuration', configuration: resolved, toolchain: tools.identity }));
    execFileSync(tools.node, [tools.npm, 'ci', ...flags], { cwd: root, env, stdio: 'pipe' });
    assertDependencies(root);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

// Fixed developer entrypoints also work before any TypeScript has been compiled.
if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, target, ...extra] = process.argv.slice(2);
  if (command === 'identity' && target === undefined) console.log(JSON.stringify(toolchain()));
  else if (command === 'install' && target && isAbsolute(target) && !extra.length) npmInstall(target);
  else throw new Error('Usage: toolchain.mjs identity | install <absolute factory path>');
}
