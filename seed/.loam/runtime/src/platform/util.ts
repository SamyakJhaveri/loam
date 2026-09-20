// Small shared helpers used by the admit path, the native boundary and doctor.
// Each is byte-identical to the single named original it was factored out of, so
// callers keep exactly the behaviour they had before the move.

import { readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, relative, sep } from 'node:path';

export function realpathOr(path: string): string { try { return realpathSync(path); } catch { return path; } }

export function contains(parent: string, child: string): boolean {
  const rel = relative(parent, child);
  return rel === '' || (!isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`));
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}
