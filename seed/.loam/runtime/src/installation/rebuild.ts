import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';
import { snapshot } from './package.js';
import { cleanTestEnvironment } from '../testing/verify.js';

export interface RebuildReference {
  root: string;
  candidateSnapshot: Record<string, string>;
  identity: { execPath: string; version: string; npm: string; platform: string; arch: string };
}

/** Compare the entire emitted file population before comparing individual bytes. */
export function compareRebuilt(candidateRoot: string, rebuiltRoot: string): void {
  const candidate = snapshot(candidateRoot);
  const rebuilt = snapshot(rebuiltRoot);
  const candidateOutput = Object.keys(candidate).filter(path => path.startsWith('dist/'));
  const rebuiltOutput = Object.keys(rebuilt).filter(path => path.startsWith('dist/'));
  if (candidateOutput.length === 0 || JSON.stringify(candidateOutput) !== JSON.stringify(rebuiltOutput)) {
    throw new Error('Compiled output file set differs from independent rebuild');
  }
  for (const path of candidateOutput) {
    if (candidate[path] !== rebuilt[path]) throw new Error(`Compiled output differs: ${path}`);
  }
  if (!readFileSync(join(candidateRoot, 'release-manifest.json')).equals(
    readFileSync(join(rebuiltRoot, 'release-manifest.json')),
  )) throw new Error('Release manifest differs from independent rebuild');
}

/** A qualification run must never refresh or otherwise repair its candidate. */
export function assertCandidateUnchanged(root: string, before: Record<string, string>): void {
  if (JSON.stringify(snapshot(root)) !== JSON.stringify(before)) {
    throw new Error('Candidate changed during independent rebuild qualification');
  }
}

/**
 * Build from frozen non-output inputs in an unrelated directory. The caller owns
 * removal of a successful reference directory after its comparisons finish.
 */
export function createRebuildReference(candidateRoot: string): RebuildReference {
  const before = snapshot(candidateRoot);
  const observed: unknown = JSON.parse(execFileSync(process.execPath,
    [join(candidateRoot, 'scripts/toolchain.mjs'), 'identity'],
    { env: cleanTestEnvironment(), encoding: 'utf8', timeout: 30_000 }));
  if (observed === null || typeof observed !== 'object' || Array.isArray(observed)) {
    throw new Error('Invalid build toolchain identity');
  }
  const envelope = observed as Record<string, unknown>;
  if (envelope.identity === null || typeof envelope.identity !== 'object' || Array.isArray(envelope.identity)) {
    throw new Error('Invalid build toolchain identity');
  }
  const identity = envelope.identity as Record<string, unknown>;
  if (typeof identity.execPath !== 'string' || identity.version !== 'v24.21.0' ||
    identity.npm !== '11.19.0' || typeof identity.platform !== 'string' || typeof identity.arch !== 'string') {
    throw new Error('Invalid build toolchain identity');
  }
  const qualifiedIdentity = { execPath: identity.execPath, version: identity.version,
    npm: identity.npm, platform: identity.platform, arch: identity.arch };
  const root = mkdtempSync(join(tmpdir(), 'loam-independent-rebuild-'));
  try {
    for (const path of Object.keys(before)) {
      if (path.startsWith('dist/') || path === 'release-manifest.json') continue;
      mkdirSync(dirname(join(root, path)), { recursive: true });
      cpSync(join(candidateRoot, path), join(root, path));
    }
    // Recheck the candidate before allowing scratch compilation to establish
    // evidence for the frozen snapshot. There is no candidate build invocation.
    assertCandidateUnchanged(candidateRoot, before);
    const installReport = execFileSync(process.execPath,
      [join(root, 'scripts/toolchain.mjs'), 'install', root],
      { cwd: root, env: cleanTestEnvironment(), encoding: 'utf8', timeout: 120_000 });
    process.stdout.write(installReport);
    execFileSync(process.execPath, [join(root, 'scripts/build.mjs')], {
      cwd: root, env: cleanTestEnvironment(), stdio: 'pipe', timeout: 120_000,
    });
    compareRebuilt(candidateRoot, root);
    return { root, candidateSnapshot: before, identity: qualifiedIdentity };
  } catch (error) {
    rmSync(root, { recursive: true, force: true });
    throw error;
  } finally {
    assertCandidateUnchanged(candidateRoot, before);
  }
}
