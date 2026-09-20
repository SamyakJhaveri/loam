import { existsSync, lstatSync, mkdtempSync, readdirSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { isAbsolute, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { shouldStrip } from './env-policy.js';
import { contains, realpathOr } from './util.js';

export const PROTECTED_KINDS = ['registry', 'state', 'locks', 'credentials', 'sockets', 'callbacks'] as const;
export type ProtectedKind = typeof PROTECTED_KINDS[number];

export interface ContainSpec {
  workspace: string;
  runtimeDir: string;
  protectedPaths: Record<ProtectedKind, string>;
  execPath: string;
  command: string[];
}
export type ContainedCommand = { file: string; args: string[]; env: Record<string, string>; profile?: string };
export type ContainResult = ContainedCommand | { status: 'unavailable'; reasons: string[] };
export type Availability = { available: true; mechanism: string } | { available: false; mechanism: string | null; reasons: string[] };

export function sanitizedEnvironment(env: NodeJS.ProcessEnv): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [name, value] of Object.entries(env)) {
    if (value !== undefined && !shouldStrip(name)) out[name] = value;
  }
  return out;
}
export function sanitizeProcessEnvironment(): void {
  for (const name of Object.keys(process.env)) if (shouldStrip(name)) delete process.env[name];
}

const LINUX_RO_BINDS = ['/usr', '/lib', '/lib64', '/bin', '/sbin', '/etc/ld.so.cache', '/etc/alternatives'];

function allowlistEnv(spec: ContainSpec): Record<string, string> {
  return {
    PATH: join(spec.runtimeDir, 'bin'),
    HOME: spec.workspace,
    TMPDIR: join(spec.workspace, 'tmp'),
    LANG: process.env.LANG ?? 'C',
  };
}
function resolveBwrap(): string | null {
  for (const candidate of ['/usr/bin/bwrap', '/bin/bwrap', '/usr/local/bin/bwrap']) if (existsSync(candidate)) return candidate;
  const probe = spawnSync('bwrap', ['--version'], { encoding: 'utf8', timeout: 10000 });
  return !probe.error && probe.status === 0 ? 'bwrap' : null;
}
function overlaps(a: string, b: string): boolean { return contains(a, b) || contains(b, a); }
function canonicalSpec(spec: ContainSpec): ContainSpec {
  function canonical(path: string): string {
    if (!isAbsolute(path)) throw new Error(`cannot resolve containment path: ${path}`);
    try { return realpathSync(path); }
    catch { throw new Error(`cannot resolve containment path: ${path}`); }
  }
  const workspace = canonical(spec.workspace);
  const runtimeDir = canonical(spec.runtimeDir);
  if (overlaps(workspace, runtimeDir)) throw new Error('workspace and runtime paths overlap');
  // Use one conservative layout contract on both hosts. Linux exposes these
  // system roots in addition to the workspace and runtime bind mounts.
  const exposed = [workspace, runtimeDir, ...LINUX_RO_BINDS.map(realpathOr), '/proc', '/dev'];
  const protectedPaths = {} as Record<ProtectedKind, string>;
  for (const kind of PROTECTED_KINDS) {
    const path = canonical(spec.protectedPaths[kind]);
    const conflict = exposed.find((root) => overlaps(root, path));
    if (conflict) throw new Error(`protected ${kind} path ${path} overlaps exposed path ${conflict}`);
    protectedPaths[kind] = path;
  }
  return { ...spec, workspace, runtimeDir, protectedPaths };
}
function inspectLinkCounts(role: string, root: string): void {
  const visitedDirectories = new Set<string>();
  function inspect(path: string): void {
    let stat;
    try { stat = lstatSync(path, { bigint: true }); }
    catch (error) { throw new Error(`cannot inspect containment ${role} path ${path}: ${error instanceof Error ? error.message : String(error)}`); }
    if (!stat.isDirectory()) {
      if (stat.nlink !== 1n) throw new Error(`containment ${role} path has link count ${stat.nlink}: ${path}`);
      return;
    }
    const identity = `${stat.dev}:${stat.ino}`;
    if (visitedDirectories.has(identity)) return;
    visitedDirectories.add(identity);
    let entries: string[];
    try { entries = readdirSync(path); }
    catch (error) { throw new Error(`cannot inspect containment ${role} path ${path}: ${error instanceof Error ? error.message : String(error)}`); }
    for (const entry of entries) inspect(join(path, entry));
  }
  inspect(root);
}
function inspectContainmentLinks(spec: ContainSpec): void {
  inspectLinkCounts('workspace', spec.workspace);
  inspectLinkCounts('runtime', spec.runtimeDir);
  for (const kind of PROTECTED_KINDS) inspectLinkCounts(`protected ${kind}`, spec.protectedPaths[kind]);
}
function sbplString(value: string): string { return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`; }
// Deny rules come last and name the same operations as the broad allow
// (file-read* and file-write*). Seatbelt resolves rules per operation and a more
// specific operation name wins over a broader one, so a deny written as `file*`
// would lose to `(allow file-read*)` whatever its position; a deny on the same
// operation is decided by order, and the last rule wins. Measured on this Mac
// (CORE-02 candidate-02 mac-terminal run). realpath handles /tmp -> /private/tmp.
function macProfile(spec: ContainSpec): string {
  const denies = Object.values(spec.protectedPaths).map((path) => `(deny file-read* file-write* (subpath ${sbplString(realpathOr(path))}))`);
  return [
    '(version 1)',
    '(deny default)',
    '(allow process-exec*)',
    '(allow process-fork)',
    '(allow signal)',
    '(allow sysctl-read)',
    '(allow mach-lookup)',
    '(allow file-read*)',
    `(allow file-read* file-write* (subpath ${sbplString(realpathOr(spec.workspace))}))`,
    '(deny network*)',
    ...denies,
    '',
  ].join('\n');
}
// The bwrap arguments shared by the real contained command and the availability
// smoke test: the unshare/clearenv flags, the read-only system binds and the
// proc/dev/tmpfs setup. Both callers append their own tail in the same order.
function linuxBaseArgs(): string[] {
  const args = ['--unshare-all', '--die-with-parent', '--new-session', '--clearenv'];
  for (const path of LINUX_RO_BINDS) if (existsSync(path)) args.push('--ro-bind', path, path);
  args.push('--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp');
  return args;
}
function linuxArgs(spec: ContainSpec): string[] {
  const args = linuxBaseArgs();
  args.push('--ro-bind', spec.runtimeDir, spec.runtimeDir);
  args.push('--bind', spec.workspace, spec.workspace);
  args.push('--chdir', spec.workspace);
  for (const [name, value] of Object.entries(allowlistEnv(spec))) args.push('--setenv', name, value);
  return args;
}

export function containedCommand(spec: ContainSpec): ContainResult {
  try { spec = canonicalSpec(spec); inspectContainmentLinks(spec); }
  catch (error) { return { status: 'unavailable', reasons: [error instanceof Error ? error.message : String(error)] }; }
  const env = allowlistEnv(spec);
  if (process.platform === 'linux') {
    const bwrap = resolveBwrap();
    if (!bwrap) return { status: 'unavailable', reasons: ['bwrap not found on PATH or standard locations'] };
    return { file: bwrap, args: [...linuxArgs(spec), '--', spec.execPath, ...spec.command], env };
  }
  if (process.platform === 'darwin') {
    const sandboxExec = '/usr/bin/sandbox-exec';
    if (!existsSync(sandboxExec)) return { status: 'unavailable', reasons: [`sandbox-exec not found at ${sandboxExec}`] };
    const dir = mkdtempSync(join(tmpdir(), 'loam-core02-sbpl-'));
    const profile = join(dir, 'profile.sb');
    writeFileSync(profile, macProfile(spec));
    return { file: sandboxExec, args: ['-f', profile, spec.execPath, ...spec.command], env, profile };
  }
  return { status: 'unavailable', reasons: [`unsupported platform: ${process.platform}`] };
}

// A live smoke test, not just a binary presence check: a nested sandbox (for
// example a Mac session already under Seatbelt) reports unavailable with the exact
// refusal reason instead of falsely claiming the mechanism works.
export function boundaryAvailability(): Availability {
  if (process.platform === 'linux') {
    const bwrap = resolveBwrap();
    if (!bwrap) return { available: false, mechanism: null, reasons: ['bwrap not found on PATH or standard locations'] };
    const args = linuxBaseArgs();
    args.push('--', '/bin/true');
    const result = spawnSync(bwrap, args, { encoding: 'utf8', timeout: 10000 });
    if (result.error) return { available: false, mechanism: 'bwrap', reasons: [`bwrap smoke test error: ${result.error.message}`] };
    if (result.status !== 0) return { available: false, mechanism: 'bwrap', reasons: [`bwrap smoke test failed: ${(result.stderr || '').trim() || `exit ${result.status}`}`] };
    return { available: true, mechanism: 'bwrap' };
  }
  if (process.platform === 'darwin') {
    const sandboxExec = '/usr/bin/sandbox-exec';
    if (!existsSync(sandboxExec)) return { available: false, mechanism: null, reasons: [`sandbox-exec not found at ${sandboxExec}`] };
    const dir = mkdtempSync(join(tmpdir(), 'loam-core02-sb-'));
    try {
      const profile = join(dir, 'smoke.sb');
      writeFileSync(profile, '(version 1)\n(allow default)\n');
      const result = spawnSync(sandboxExec, ['-f', profile, '/usr/bin/true'], { encoding: 'utf8', timeout: 10000 });
      if (result.error) return { available: false, mechanism: 'sandbox-exec', reasons: [`sandbox-exec smoke test error: ${result.error.message}`] };
      if (result.status !== 0) return { available: false, mechanism: 'sandbox-exec', reasons: [`sandbox-exec smoke test failed: ${(result.stderr || '').trim() || `exit ${result.status}`}`] };
      return { available: true, mechanism: 'sandbox-exec' };
    } finally { rmSync(dir, { recursive: true, force: true }); }
  }
  return { available: false, mechanism: null, reasons: [`unsupported platform: ${process.platform}`] };
}
