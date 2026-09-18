// CORE-04 containment probe. npm runs this postinstall inside the CORE-02
// boundary during the build phase. It never throws: every read is recorded as
// 'ok' or the errno code so the host-only fixture can assert the denials. It
// writes a marker (proof the script ran) and a result.json beside itself, then
// exits 0. No secret value is ever recorded, only environment key lengths.
import { writeFileSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';
import { spawnSync } from 'node:child_process';

const here = dirname(fileURLToPath(import.meta.url));
const payload = join(here, '..', '..');
const controlRoot = join(here, '..', '..', '..', '..', '..');
const homes = ['registry', 'state', 'locks', 'credentials', 'sockets', 'callbacks'];

function directRead(path) {
  try { readFileSync(path); return 'ok'; }
  catch (error) { return error && error.code ? error.code : 'error'; }
}
function childRead(path) {
  const result = spawnSync('/bin/sh', ['-c', 'exec /bin/cat -- "$1"', 'sh', path], { encoding: 'utf8' });
  if (result.status === 0) return 'ok';
  const text = (result.stderr || '').toLowerCase();
  if (text.includes('operation not permitted')) return 'EPERM';
  if (text.includes('permission denied')) return 'EACCES';
  if (text.includes('no such file')) return 'ENOENT';
  return `status-${result.status}`;
}
function envLengths() {
  const out = {};
  for (const name of Object.keys(process.env).sort()) out[name] = String(process.env[name] ?? '').length;
  return out;
}
// Invoke a declared native tool through its shim on PATH. `ran` means the shim was
// found and exec'd a real binary (no ENOENT), which is the execution proof R4-B(1)
// needs; `status`/`line` are evidence only. Some hosts (a sandboxed /usr/bin/cc
// whose xcrun cache write is denied) exit nonzero without disproving execution.
function runTool(name) {
  const probe = spawnSync(name, ['--version'], { encoding: 'utf8' });
  if (probe.error) return { ran: false, code: probe.error.code ?? 'error' };
  return { ran: true, status: probe.status, line: String(probe.stdout || probe.stderr || '').split('\n')[0].slice(0, 80) };
}

const protectedReads = {};
for (const home of homes) protectedReads[home] = directRead(join(controlRoot, home, 'canary'));
const descendant = { workspace: childRead(join(payload, 'package.json')) };
for (const home of homes) descendant[home] = childRead(join(controlRoot, home, 'canary'));

const result = {
  env: envLengths(),
  workspaceRead: directRead(join(payload, 'package.json')),
  protectedReads,
  descendant,
  cc: runTool('cc'),   // proves the declared cc shim executed inside the boundary (R4-B1)
};
writeFileSync(join(here, 'marker'), '1');
writeFileSync(join(here, 'result.json'), `${JSON.stringify(result, null, 2)}\n`);
process.exit(0);
