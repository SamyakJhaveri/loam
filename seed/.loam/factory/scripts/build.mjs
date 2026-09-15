import { execFileSync } from 'node:child_process';
import { existsSync, lstatSync, mkdirSync, readdirSync, unlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { assertDependencies, cleanEnvironment, toolchain } from './toolchain.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const tools = toolchain();
assertDependencies(root);
function rejectSymlinks(directory) {
  for (const name of readdirSync(directory)) {
    if (['node_modules', '.cache', '.state', 'runtime-installation', 'dist'].includes(name) && directory === root) continue;
    const path = join(directory, name);
    const stat = lstatSync(path);
    if (stat.isSymbolicLink()) throw new Error(`Payload symlink: ${path}`);
    if (stat.isDirectory()) rejectSymlinks(path);
  }
}
rejectSymlinks(root);
// Refresh generated files without deleting directory nodes. This also preserves
// a workspace's directory permissions and refuses to erase unexpected content.
function clearCompiledFiles(directory) {
  if (!existsSync(directory)) { mkdirSync(directory, { recursive: true }); return; }
  if (lstatSync(directory).isSymbolicLink()) throw new Error('Compiled output directory cannot be a symlink');
  for (const name of readdirSync(directory)) {
    const path = join(directory, name);
    const stat = lstatSync(path);
    if (stat.isSymbolicLink()) throw new Error(`Compiled output symlink: ${path}`);
    if (stat.isDirectory()) clearCompiledFiles(path);
    else if (stat.isFile() && /\.js(?:\.map)?$/.test(name)) unlinkSync(path);
    else throw new Error(`Unexpected compiled output: ${path}`);
  }
}
clearCompiledFiles(join(root, 'dist'));
execFileSync(tools.node, [join(root, 'node_modules/typescript/bin/tsc'), '--project', join(root, 'tsconfig.json')], { cwd: root, env: cleanEnvironment(), stdio: 'inherit' });
const { createReleaseManifest, assertImportClosure } = await import('../dist/src/installation/package.js');
assertImportClosure(root);
writeFileSync(join(root, 'release-manifest.json'), `${JSON.stringify(createReleaseManifest(root), null, 2)}\n`);
console.log(JSON.stringify({ kind: 'factory-build', status: 'passed', toolchain: tools.identity }));
