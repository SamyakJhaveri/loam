import { statSync } from 'node:fs';
import { isAbsolute } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { Worker } from 'node:worker_threads';
export class OwnershipRefused extends Error {
    errcode;
    constructor(message, errcode) { super(message); this.name = 'OwnershipRefused'; this.errcode = errcode; }
}
export function storeURI(path) {
    if (typeof path !== 'string' || path.length === 0)
        throw new Error('store path must be a non-empty string');
    if (path.includes('\x00'))
        throw new Error(`store path contains a NUL byte: ${JSON.stringify(path)}`);
    if (path === ':memory:' || path.startsWith('file:'))
        throw new Error(`arbitrary store URI refused: ${path}`);
    if (!isAbsolute(path))
        throw new Error(`store path must be absolute: ${path}`);
    if (path.startsWith('//'))
        throw new Error(`ambiguous store path with leading double slash: ${path}`);
    return `file:${path.split('/').map((segment) => encodeURIComponent(segment)).join('/')}?mode=rw`;
}
function readPragmaInt(db, pragma) {
    const row = db.prepare(`PRAGMA ${pragma}`).get();
    if (!row)
        throw new Error(`empty PRAGMA ${pragma}`);
    return Number(row[pragma]);
}
function readPragmaText(db, pragma) {
    const row = db.prepare(`PRAGMA ${pragma}`).get();
    if (!row)
        throw new Error(`empty PRAGMA ${pragma}`);
    return String(row[pragma]);
}
export function openExistingStore(path, options) {
    const db = new DatabaseSync(storeURI(path), { timeout: options.busyTimeoutMs ?? 0 });
    try {
        const applicationId = readPragmaInt(db, 'application_id');
        if (applicationId !== options.applicationId) {
            throw new Error(`foreign store: application_id ${applicationId}, expected ${options.applicationId}`);
        }
        db.exec('PRAGMA synchronous=extra');
        db.exec('PRAGMA foreign_keys=on');
        const effective = {
            journalMode: readPragmaText(db, 'journal_mode'),
            synchronous: readPragmaInt(db, 'synchronous'),
            foreignKeys: readPragmaInt(db, 'foreign_keys'),
            applicationId,
        };
        return { db, effective };
    }
    catch (error) {
        db.close();
        throw error;
    }
}
export function acquireOwnership(lockPath) {
    if (!isAbsolute(lockPath))
        throw new Error(`lock path must be absolute: ${lockPath}`);
    let before;
    try {
        before = statSync(lockPath, { bigint: true });
    }
    catch {
        throw new OwnershipRefused(`lock file is missing: ${lockPath}`, 14);
    }
    let db;
    let after;
    try {
        db = new DatabaseSync(storeURI(lockPath), { timeout: 0 });
        db.exec('PRAGMA locking_mode=exclusive');
        // First read acquires the shared lock and, in exclusive mode, retains it; a
        // competitor with busy timeout 0 is refused here with errcode 5.
        const journal = readPragmaText(db, 'journal_mode');
        if (journal !== 'delete')
            throw new Error(`unexpected journal mode for lock: ${journal}`);
        db.prepare('insert into owner(pid, started_at) values (?, ?)').run(process.pid, Date.now());
        after = statSync(lockPath, { bigint: true });
        if (after.dev !== before.dev || after.ino !== before.ino) {
            throw new OwnershipRefused(`lock path replaced during acquisition: ${lockPath}`);
        }
    }
    catch (error) {
        try {
            db?.close();
        }
        catch { /* already closed */ }
        const err = error;
        if (typeof err.errcode === 'number')
            throw new OwnershipRefused(err.message ?? 'ownership refused', err.errcode);
        throw error;
    }
    const connection = db;
    const storedDev = after.dev;
    const storedIno = after.ino;
    let released = false;
    return {
        pid: process.pid,
        inode: Number(after.ino),
        release() { if (!released) {
            released = true;
            try {
                connection.close();
            }
            catch { /* already closed */ }
        } },
        isPathReplaced() {
            try {
                const now = statSync(lockPath, { bigint: true });
                return now.dev !== storedDev || now.ino !== storedIno;
            }
            catch {
                return true;
            }
        },
    };
}
function makeError(message) {
    const error = new Error(message.message ?? 'store worker error');
    error.errcode = message.errcode;
    error.code = message.code;
    return error;
}
// The store connection lives on a dedicated worker thread so a busy SQLite wait
// never blocks the main event loop.
export function openStoreOnWorker(path, options) {
    const worker = new Worker(new URL('./store-worker.js', import.meta.url), { workerData: { path, options } });
    const pending = new Map();
    let sequence = 0;
    let terminalError;
    let closing;
    let openResolve;
    let openReject;
    const opened = new Promise((resolve, reject) => { openResolve = resolve; openReject = reject; });
    // run() also awaits opened; callers may use that path without reading opened.
    void opened.catch(() => { });
    function fail(error) {
        terminalError ??= error;
        openReject(terminalError);
        for (const entry of pending.values())
            entry.reject(terminalError);
        pending.clear();
    }
    worker.on('message', (message) => {
        if (terminalError)
            return;
        if (message.type === 'open') {
            if (message.ok && message.effective)
                openResolve(message.effective);
            else
                fail(makeError(message));
        }
        else if (message.type === 'result' && typeof message.id === 'number') {
            const entry = pending.get(message.id);
            if (!entry)
                return;
            pending.delete(message.id);
            if (message.ok)
                entry.resolve(message.rows ?? []);
            else
                entry.reject(makeError(message));
        }
    });
    worker.on('error', fail);
    worker.on('exit', (code) => fail(new Error(`store worker exited with code ${code}`)));
    return {
        opened,
        async run(sql) {
            await opened;
            if (terminalError)
                throw terminalError;
            return new Promise((resolve, reject) => {
                const id = ++sequence;
                pending.set(id, { resolve, reject });
                try {
                    worker.postMessage({ type: 'run', id, sql });
                }
                catch (error) {
                    pending.delete(id);
                    reject(error);
                }
            });
        },
        close() {
            fail(new Error('store worker closed'));
            closing ??= worker.terminate().then(() => { });
            return closing;
        },
    };
}
//# sourceMappingURL=ownership.js.map