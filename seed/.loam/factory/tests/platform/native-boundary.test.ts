import assert from 'node:assert/strict';
import { test } from 'node:test';
import { appendFileSync, copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { spawnSync, type SpawnSyncReturns } from 'node:child_process';
import { createServer } from 'node:net';
import { randomUUID } from 'node:crypto';
import { boundaryAvailability, containedCommand, PROTECTED_KINDS, sanitizedEnvironment, type ContainSpec, type ProtectedKind } from '../../src/platform/native-boundary.js';

const runtimeDir = dirname(dirname(process.execPath));
const nodeExe = process.execPath;

function record(name: string, mechanism: string, observed: unknown): void {
  const trace = process.env.LOAM_FACTORY_OBSERVED_TRACE;
  if (trace) appendFileSync(trace, `${JSON.stringify({ case: name, mechanism, observed })}\n`);
}
interface Boundary { base: string; workspace: string; control: string; secret: string; protectedPaths: Record<ProtectedKind, string>; cleanup(): void }
function setup(baseDir: string = tmpdir()): Boundary {
  const base = mkdtempSync(join(baseDir, 'loam-core02-'));
  const workspace = join(base, 'workspace'); mkdirSync(join(workspace, 'tmp'), { recursive: true });
  const control = join(base, 'control');
  const secret = `SECRET-${randomUUID()}`;
  const protectedPaths = {} as Record<ProtectedKind, string>;
  for (const kind of PROTECTED_KINDS) {
    const d = join(control, kind); mkdirSync(d, { recursive: true });
    protectedPaths[kind] = d;
    writeFileSync(join(d, 'marker'), `${secret}-${kind}`);
  }
  return { base, workspace, control, secret, protectedPaths, cleanup: () => rmSync(base, { recursive: true, force: true }) };
}
function requireMechanism(): string {
  const a = boundaryAvailability();
  if (!a.available) throw new Error(`containment mechanism unavailable: ${a.reasons.join('; ')}`);
  return a.mechanism;
}
function specFor(s: Boundary, command: string[]): ContainSpec {
  return { workspace: s.workspace, runtimeDir, protectedPaths: s.protectedPaths, execPath: nodeExe, command };
}
function runContained(spec: ContainSpec): SpawnSyncReturns<string> {
  const cc = containedCommand(spec);
  if ('status' in cc) throw new Error(`containedCommand unavailable: ${cc.reasons.join('; ')}`);
  try { return spawnSync(cc.file, cc.args, { env: cc.env, encoding: 'utf8', timeout: 30000 }); }
  finally { if (cc.profile) { try { rmSync(dirname(cc.profile), { recursive: true, force: true }); } catch { /* best effort */ } } }
}

// Contained probe scripts. Paths are baked in as JSON string literals, so the
// surrounding single-quoted pieces stay literal to the payload import scanner.
function readScript(target: string): string {
  return 'const fs=require("node:fs");const t=' + JSON.stringify(target) + ';' +
    'try{const c=fs.readFileSync(t,"utf8");process.stdout.write("READ:"+c);}catch(e){process.stdout.write("DENIED:"+String(e.code||e.message));}';
}
function readWriteScript(target: string): string {
  return 'const fs=require("node:fs");const t=' + JSON.stringify(target) + ';' +
    'let rd=false,wr=false,leak="";' +
    'try{leak=fs.readFileSync(t,"utf8");}catch(e){rd=true;}' +
    'try{fs.writeFileSync(t,"tampered");}catch(e){wr=true;}' +
    'if(rd&&wr)process.stdout.write("DENIED");else process.stdout.write("LEAK:"+leak);';
}
function descendantScript(target: string): string {
  return 'const cp=require("node:child_process");const t=' + JSON.stringify(target) + ';' +
    'const r=cp.spawnSync("/bin/sh",["-c","cat "+JSON.stringify(t)],{encoding:"utf8",env:{PATH:"/bin:/usr/bin"}});' +
    'const out=(r.stdout||"")+(r.stderr||"");' +
    'if(r.status!==0)process.stdout.write("DESC-DENIED");else process.stdout.write("LEAK:"+out);';
}
function connectScript(sockPath: string): string {
  return 'const net=require("node:net");const s=' + JSON.stringify(sockPath) + ';' +
    'const c=net.connect(s);' +
    'c.on("connect",()=>{process.stdout.write("CONNECTED");c.end();process.exit(9);});' +
    'c.on("error",()=>{process.stdout.write("CONNECT-DENIED");process.exit(3);});';
}
const WORKSPACE_SCRIPT =
  'const fs=require("node:fs");const cp=require("node:child_process");const path=require("node:path");' +
  'const home=process.env.HOME;const f=path.join(home,"probe.txt");' +
  'fs.writeFileSync(f,"hello");const c=fs.readFileSync(f,"utf8");const list=fs.readdirSync(home);' +
  'const r=cp.spawnSync("node",["-e","process.stdout.write(String(1))"],{encoding:"utf8"});' +
  'if(c==="hello"&&list.includes("probe.txt")&&r.status===0&&r.stdout==="1")process.stdout.write("WORKSPACE-OK");' +
  'else{process.stderr.write("bad c="+c+" child="+r.stdout+" st="+r.status);process.exit(4);}';
function runtimeWriteScript(target: string): string {
  return 'const fs=require("node:fs");const cp=require("node:child_process");' +
    'const r=cp.spawnSync("node",["-e","0"],{encoding:"utf8"});' +
    'if(r.status!==0){process.stderr.write("exec="+r.status);process.exit(5);}' +
    'try{fs.writeFileSync(' + JSON.stringify(target) + ',"x");process.stdout.write("RUNTIME-RW");}' +
    'catch(e){process.stdout.write("RUNTIME-RO:"+e.code);}';
}

test('boundary.mechanism-available', () => {
  const a = boundaryAvailability();
  assert.ok(a.available, a.available ? '' : `mechanism unavailable: ${a.reasons.join('; ')}`);
  record('boundary.mechanism-available', a.available ? a.mechanism : 'none', a.available);
});

test('boundary.workspace-admitted', () => {
  const mech = requireMechanism();
  const s = setup();
  try {
    const r = runContained(specFor(s, ['-e', WORKSPACE_SCRIPT]));
    assert.equal(r.status, 0, r.stderr || String(r.error));
    assert.match(r.stdout, /WORKSPACE-OK/);
    record('boundary.workspace-admitted', mech, 'admitted');
  } finally { s.cleanup(); }
});

test('boundary.runtime-write-denied', () => {
  const s = setup();
  try {
    const scratchRuntime = join(s.base, 'runtime');
    mkdirSync(join(scratchRuntime, 'bin'), { recursive: true });
    const scratchNode = join(scratchRuntime, 'bin', 'node');
    copyFileSync(nodeExe, scratchNode);
    const target = join(scratchRuntime, `write-${randomUUID()}`);
    const command = ['-e', runtimeWriteScript(target)];
    const control = spawnSync(scratchNode, command, {
      env: { ...sanitizedEnvironment(process.env), PATH: join(scratchRuntime, 'bin') }, encoding: 'utf8', timeout: 30000,
    });
    assert.equal(control.status, 0, control.stderr || String(control.error));
    assert.equal(control.stdout, 'RUNTIME-RW', 'uncontained scratch runtime is writable');
    assert.equal(readFileSync(target, 'utf8'), 'x');
    rmSync(target);
    const mech = requireMechanism();
    const r = runContained({ ...specFor(s, command), runtimeDir: scratchRuntime, execPath: scratchNode });
    assert.equal(r.status, 0, r.stderr || String(r.error));
    assert.match(r.stdout, /^RUNTIME-RO:(EACCES|EPERM|EROFS)$/);
    assert.equal(existsSync(target), false, 'no file created under scratch runtime');
    record('boundary.runtime-write-denied', mech, 'runtime write denied');
  } finally { s.cleanup(); }
});

function deniedProtected(kind: ProtectedKind, name: string): void {
  const mech = requireMechanism();
  const s = setup();
  try {
    const target = join(s.protectedPaths[kind], 'marker');
    const original = readFileSync(target, 'utf8');
    const r = runContained(specFor(s, ['-e', readWriteScript(target)]));
    assert.equal(r.stdout, 'DENIED', `${name}: expected denial, got ${r.stdout || r.stderr}`);
    assert.ok(!r.stdout.includes(s.secret), 'no secret leak');
    assert.equal(readFileSync(target, 'utf8'), original, 'marker file unchanged');
    record(name, mech, 'read+write denied');
  } finally { s.cleanup(); }
}
test('boundary.registry-denied', () => deniedProtected('registry', 'boundary.registry-denied'));
test('boundary.state-denied', () => deniedProtected('state', 'boundary.state-denied'));
test('boundary.locks-denied', () => deniedProtected('locks', 'boundary.locks-denied'));
test('boundary.credentials-denied', () => deniedProtected('credentials', 'boundary.credentials-denied'));
test('boundary.callbacks-denied', () => deniedProtected('callbacks', 'boundary.callbacks-denied'));

test('boundary.sockets-denied', async () => {
  const mech = requireMechanism();
  const s = setup(process.platform === 'darwin' ? '/tmp' : tmpdir());
  const sockPath = join(s.protectedPaths.sockets, 's.sock');
  let connections = 0;
  const server = createServer(() => { connections++; });
  await new Promise<void>((resolve) => server.listen(sockPath, () => resolve()));
  try {
    const r = runContained(specFor(s, ['-e', connectScript(sockPath)]));
    assert.match(r.stdout, /CONNECT-DENIED/, `expected connect denial, got ${r.stdout || r.stderr}`);
    assert.equal(connections, 0, 'supervisor recorded zero connections');
    record('boundary.sockets-denied', mech, 'connect denied');
  } finally { server.close(); s.cleanup(); }
});

test('boundary.descendant-denied', () => {
  const mech = requireMechanism();
  const s = setup();
  try {
    const target = join(s.protectedPaths.registry, 'marker');
    const original = readFileSync(target, 'utf8');
    const control = spawnSync(nodeExe, ['-e', descendantScript(target)], { env: sanitizedEnvironment(process.env), encoding: 'utf8', timeout: 30000 });
    assert.equal(control.status, 0, control.stderr || String(control.error));
    assert.equal(control.stdout, `LEAK:${original}`, 'uncontained descendant can read the same target');
    const r = runContained(specFor(s, ['-e', descendantScript(target)]));
    assert.equal(r.status, 0, r.stderr || String(r.error));
    assert.match(r.stdout, /DESC-DENIED/, `expected descendant denial, got ${r.stdout}`);
    assert.ok(!r.stdout.includes(s.secret), 'no secret leak through descendant');
    assert.equal(readFileSync(target, 'utf8'), original);
    record('boundary.descendant-denied', mech, 'descendant denied');
  } finally { s.cleanup(); }
});

test('boundary.symlink-denied', () => {
  const mech = requireMechanism();
  const s = setup();
  try {
    const target = join(s.protectedPaths.registry, 'marker');
    const link = join(s.workspace, 'link-to-secret');
    symlinkSync(target, link);
    const r = runContained(specFor(s, ['-e', readScript(link)]));
    assert.match(r.stdout, /^DENIED/, `expected symlink denial, got ${r.stdout}`);
    assert.ok(!r.stdout.includes(s.secret), 'no secret leak through symlink');
    record('boundary.symlink-denied', mech, 'symlink read denied');
  } finally { s.cleanup(); }
});

test('boundary.path-alias-denied', () => {
  const mech = requireMechanism();
  if (process.platform === 'darwin') {
    const root = mkdtempSync('/private/tmp/loam-core02-alias-');
    try {
      const protectedPaths = {} as Record<ProtectedKind, string>;
      const secret = `SECRET-${randomUUID()}`;
      for (const kind of PROTECTED_KINDS) { const d = join(root, kind); mkdirSync(d, { recursive: true }); protectedPaths[kind] = d; }
      const target = join(protectedPaths.registry, 'marker'); writeFileSync(target, secret);
      const workspace = join(root, 'ws'); mkdirSync(join(workspace, 'tmp'), { recursive: true });
      const alias = target.replace('/private/tmp/', '/tmp/');
      assert.notEqual(alias, target, 'constructed a /tmp alias');
      const r = runContained({ workspace, runtimeDir, protectedPaths, execPath: nodeExe, command: ['-e', readScript(alias)] });
      assert.match(r.stdout, /^DENIED/, `expected /tmp alias denial, got ${r.stdout}`);
      assert.ok(!r.stdout.includes(secret));
      record('boundary.path-alias-denied', mech, 'tmp alias denied');
    } finally { rmSync(root, { recursive: true, force: true }); }
  } else {
    const s = setup();
    try {
      const aliases = [`${s.workspace}/../control/registry/marker`, '/proc/self/cwd/../control/registry/marker'];
      for (const alias of aliases) {
        const r = runContained(specFor(s, ['-e', readScript(alias)]));
        assert.match(r.stdout, /^DENIED/, `expected alias denial for ${alias}, got ${r.stdout}`);
        assert.ok(!r.stdout.includes(s.secret));
      }
      record('boundary.path-alias-denied', mech, 'traversal aliases denied');
    } finally { s.cleanup(); }
  }
});

test('boundary.same-user-control', () => {
  const s = setup();
  try {
    const target = join(s.protectedPaths.registry, 'marker');
    const r = spawnSync(nodeExe, ['-e', readScript(target)], { env: sanitizedEnvironment(process.env), encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr || String(r.error));
    assert.match(r.stdout, /^READ:/, `uncontained same-user read should succeed, got ${r.stdout}`);
    assert.ok(r.stdout.includes(s.secret), 'same-user separation alone does not protect the marker');
    const availability = boundaryAvailability();
    record('boundary.same-user-control', availability.available ? availability.mechanism : 'none', 'read succeeded uncontained');
  } finally { s.cleanup(); }
});
