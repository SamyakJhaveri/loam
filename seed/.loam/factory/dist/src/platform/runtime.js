import { createHash } from 'node:crypto';
import { readFileSync, realpathSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';
import { sanitizedEnvironment } from './native-boundary.js';
let cachedSqlite;
function sqliteVersion() {
    if (cachedSqlite === undefined) {
        const db = new DatabaseSync(':memory:');
        try {
            cachedSqlite = String(db.prepare('select sqlite_version() as v').get().v);
        }
        finally {
            db.close();
        }
    }
    return cachedSqlite;
}
function digestOf(path) {
    return createHash('sha256').update(readFileSync(path)).digest('hex');
}
export function runtimeIdentity() {
    return {
        execPath: process.execPath,
        version: process.version,
        arch: process.arch,
        platform: process.platform,
        sqlite: sqliteVersion(),
        openssl: process.versions.openssl ?? '',
        execSha256: digestOf(process.execPath),
    };
}
export function qualifyRuntime(manifestPath, options = {}) {
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    const reasons = [];
    const version = process.version;
    const sqlite = sqliteVersion();
    if (version !== `v${manifest.node}`)
        reasons.push(`node version ${version} does not match manifest v${manifest.node}`);
    if (sqlite !== manifest.sqlite)
        reasons.push(`sqlite ${sqlite} does not match manifest sqlite ${manifest.sqlite}`);
    const key = `${process.platform}-${process.arch}`;
    const entry = manifest.platforms?.[key];
    const execPath = options.execPath ?? process.execPath;
    let execSha256;
    try {
        execSha256 = digestOf(execPath);
        // Identity above belongs to this process, never to an arbitrary hashed file.
        if (realpathSync(execPath) !== realpathSync(process.execPath)) {
            reasons.push(`executable ${execPath} is not the running executable ${process.execPath}`);
        }
    }
    catch {
        reasons.push(`executable not found: ${execPath}`);
    }
    let digestMatches = false;
    if (!entry) {
        reasons.push(`manifest has no platform entry ${key}`);
    }
    else if (execSha256 !== undefined) {
        digestMatches = execSha256 === entry.nodeSha256;
        if (options.requireDigest && !digestMatches)
            reasons.push(`executable digest ${execSha256} does not match manifest digest ${entry.nodeSha256}`);
    }
    if (reasons.length)
        return { status: 'unavailable', reasons, execSha256, digestMatches };
    return { status: 'qualified', execSha256: execSha256, digestMatches };
}
// A noninteractive PATH may omit the user's Node, so always spawn this exact
// executable by absolute path and strip preload/loader inputs from its child.
export function spawnRuntime(args, options = {}) {
    const env = sanitizedEnvironment(options.env ?? process.env);
    if (!options.env || !('PATH' in options.env))
        delete env.PATH;
    return spawnSync(process.execPath, args, { encoding: 'utf8', timeout: 30000, ...options, env });
}
//# sourceMappingURL=runtime.js.map