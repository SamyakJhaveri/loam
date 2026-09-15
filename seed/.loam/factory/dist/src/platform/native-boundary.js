import { existsSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
export const PROTECTED_KINDS = ['registry', 'state', 'locks', 'credentials', 'sockets', 'callbacks'];
// Preload, loader and package-manager environment inputs a JavaScript launcher
// cannot undo once Node has started, so a trusted spawner strips them from a
// child's environment before it runs.
const STRIP_EXACT = new Set([
    'NODE_OPTIONS', 'NODE_PATH', 'NODE_REPL_EXTERNAL_MODULE', 'NODE_EXTRA_CA_CERTS',
    'NODE_PRESERVE_SYMLINKS_MAIN', 'NODE_TLS_REJECT_UNAUTHORIZED',
    'LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT',
    'PYTHONPATH', 'PYTHONSTARTUP', 'PERL5OPT', 'BASH_ENV', 'ENV', 'PROMPT_COMMAND',
]);
function shouldStrip(name) {
    if (STRIP_EXACT.has(name))
        return true;
    if (name.startsWith('DYLD_'))
        return true;
    if (name.startsWith('GIT_') && name !== 'GIT_TERMINAL_PROMPT')
        return true;
    return false;
}
export function sanitizedEnvironment(env) {
    const out = {};
    for (const [name, value] of Object.entries(env)) {
        if (value !== undefined && !shouldStrip(name))
            out[name] = value;
    }
    return out;
}
export function sanitizeProcessEnvironment() {
    for (const name of Object.keys(process.env))
        if (shouldStrip(name))
            delete process.env[name];
}
const LINUX_RO_BINDS = ['/usr', '/lib', '/lib64', '/bin', '/sbin', '/etc/ld.so.cache', '/etc/alternatives'];
function allowlistEnv(spec) {
    return {
        PATH: join(spec.runtimeDir, 'bin'),
        HOME: spec.workspace,
        TMPDIR: join(spec.workspace, 'tmp'),
        LANG: process.env.LANG ?? 'C',
    };
}
function resolveBwrap() {
    for (const candidate of ['/usr/bin/bwrap', '/bin/bwrap', '/usr/local/bin/bwrap'])
        if (existsSync(candidate))
            return candidate;
    const probe = spawnSync('bwrap', ['--version'], { encoding: 'utf8', timeout: 10000 });
    return !probe.error && probe.status === 0 ? 'bwrap' : null;
}
function realpathOr(path) { try {
    return realpathSync(path);
}
catch {
    return path;
} }
function sbplString(value) { return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`; }
// Deny rules come last and name the same operations as the broad allow
// (file-read* and file-write*). Seatbelt resolves rules per operation and a more
// specific operation name wins over a broader one, so a deny written as `file*`
// would lose to `(allow file-read*)` whatever its position; a deny on the same
// operation is decided by order, and the last rule wins. Measured on this Mac
// (CORE-02 candidate-02 mac-terminal run). realpath handles /tmp -> /private/tmp.
function macProfile(spec) {
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
function linuxArgs(spec) {
    const args = ['--unshare-all', '--die-with-parent', '--new-session', '--clearenv'];
    for (const path of LINUX_RO_BINDS)
        if (existsSync(path))
            args.push('--ro-bind', path, path);
    args.push('--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp');
    args.push('--ro-bind', spec.runtimeDir, spec.runtimeDir);
    args.push('--bind', spec.workspace, spec.workspace);
    args.push('--chdir', spec.workspace);
    for (const [name, value] of Object.entries(allowlistEnv(spec)))
        args.push('--setenv', name, value);
    return args;
}
export function containedCommand(spec) {
    const env = allowlistEnv(spec);
    if (process.platform === 'linux') {
        const bwrap = resolveBwrap();
        if (!bwrap)
            return { status: 'unavailable', reasons: ['bwrap not found on PATH or standard locations'] };
        return { file: bwrap, args: [...linuxArgs(spec), '--', spec.execPath, ...spec.command], env };
    }
    if (process.platform === 'darwin') {
        const sandboxExec = '/usr/bin/sandbox-exec';
        if (!existsSync(sandboxExec))
            return { status: 'unavailable', reasons: [`sandbox-exec not found at ${sandboxExec}`] };
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
export function boundaryAvailability() {
    if (process.platform === 'linux') {
        const bwrap = resolveBwrap();
        if (!bwrap)
            return { available: false, mechanism: null, reasons: ['bwrap not found on PATH or standard locations'] };
        const args = ['--unshare-all', '--die-with-parent', '--new-session', '--clearenv'];
        for (const path of LINUX_RO_BINDS)
            if (existsSync(path))
                args.push('--ro-bind', path, path);
        args.push('--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--', '/bin/true');
        const result = spawnSync(bwrap, args, { encoding: 'utf8', timeout: 10000 });
        if (result.error)
            return { available: false, mechanism: 'bwrap', reasons: [`bwrap smoke test error: ${result.error.message}`] };
        if (result.status !== 0)
            return { available: false, mechanism: 'bwrap', reasons: [`bwrap smoke test failed: ${(result.stderr || '').trim() || `exit ${result.status}`}`] };
        return { available: true, mechanism: 'bwrap' };
    }
    if (process.platform === 'darwin') {
        const sandboxExec = '/usr/bin/sandbox-exec';
        if (!existsSync(sandboxExec))
            return { available: false, mechanism: null, reasons: [`sandbox-exec not found at ${sandboxExec}`] };
        const dir = mkdtempSync(join(tmpdir(), 'loam-core02-sb-'));
        try {
            const profile = join(dir, 'smoke.sb');
            writeFileSync(profile, '(version 1)\n(allow default)\n');
            const result = spawnSync(sandboxExec, ['-f', profile, '/usr/bin/true'], { encoding: 'utf8', timeout: 10000 });
            if (result.error)
                return { available: false, mechanism: 'sandbox-exec', reasons: [`sandbox-exec smoke test error: ${result.error.message}`] };
            if (result.status !== 0)
                return { available: false, mechanism: 'sandbox-exec', reasons: [`sandbox-exec smoke test failed: ${(result.stderr || '').trim() || `exit ${result.status}`}`] };
            return { available: true, mechanism: 'sandbox-exec' };
        }
        finally {
            rmSync(dir, { recursive: true, force: true });
        }
    }
    return { available: false, mechanism: null, reasons: [`unsupported platform: ${process.platform}`] };
}
//# sourceMappingURL=native-boundary.js.map