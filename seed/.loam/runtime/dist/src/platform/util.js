// Small shared helpers used by the admit path, the native boundary and doctor.
// Each is byte-identical to the single named original it was factored out of, so
// callers keep exactly the behaviour they had before the move.
import { readFileSync, realpathSync } from 'node:fs';
import { isAbsolute, relative, sep } from 'node:path';
export function realpathOr(path) { try {
    return realpathSync(path);
}
catch {
    return path;
} }
export function contains(parent, child) {
    const rel = relative(parent, child);
    return rel === '' || (!isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`));
}
export function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
}
export function readJson(path) {
    return JSON.parse(readFileSync(path, 'utf8'));
}
//# sourceMappingURL=util.js.map