import { statSync } from 'node:fs';
import { isAbsolute } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { Worker } from 'node:worker_threads';

// Invariant: this module is the only code that opens owner.lock, and it opens it
// exactly once per acquisition through a single node:sqlite connection. Never open
// a second descriptor on the lock: under POSIX record locks, closing any descriptor
// to a file drops every lock the process holds on it. There is no unlink, rotate,
// heartbeat or timeout-steal; takeover happens only through a fresh acquisition on
// the same inode after the previous owner's connection closes or its process dies.

export interface EffectiveSettings {
  journalMode: string;
  synchronous: number;
  foreignKeys: number;
  applicationId: number;
}
export interface OpenStore { db: DatabaseSync; effective: EffectiveSettings }
export interface StoreOptions { applicationId: number; busyTimeoutMs?: number }
export interface Ownership { pid: number; inode: number; release(): void; isPathReplaced(): boolean }
export interface StoreWorkerHandle {
  opened: Promise<EffectiveSettings>;
  run(sql: string): Promise<unknown[]>;
  close(): Promise<void>;
}
export class OwnershipRefused extends Error {
  errcode?: number;
  constructor(message: string, errcode?: number) { super(message); this.name = 'OwnershipRefused'; this.errcode = errcode; }
}

export function storeURI(path: string): string {
  if (typeof path !== 'string' || path.length === 0) throw new Error('store path must be a non-empty string');
  if (path.includes('\x00')) throw new Error(`store path contains a NUL byte: ${JSON.stringify(path)}`);
  if (path === ':memory:' || path.startsWith('file:')) throw new Error(`arbitrary store URI refused: ${path}`);
  if (!isAbsolute(path)) throw new Error(`store path must be absolute: ${path}`);
  return `file:${path.split('/').map((segment) => encodeURIComponent(segment)).join('/')}?mode=rw`;
}

function readPragmaInt(db: DatabaseSync, pragma: string): number {
  const row = db.prepare(`PRAGMA ${pragma}`).get() as Record<string, unknown> | undefined;
  if (!row) throw new Error(`empty PRAGMA ${pragma}`);
  return Number(row[pragma]);
}
function readPragmaText(db: DatabaseSync, pragma: string): string {
  const row = db.prepare(`PRAGMA ${pragma}`).get() as Record<string, unknown> | undefined;
  if (!row) throw new Error(`empty PRAGMA ${pragma}`);
  return String(row[pragma]);
}

export function openExistingStore(path: string, options: StoreOptions): OpenStore {
  const db = new DatabaseSync(storeURI(path), { timeout: options.busyTimeoutMs ?? 0 });
  try {
    const applicationId = readPragmaInt(db, 'application_id');
    if (applicationId !== options.applicationId) {
      throw new Error(`foreign store: application_id ${applicationId}, expected ${options.applicationId}`);
    }
    db.exec('PRAGMA synchronous=extra');
    db.exec('PRAGMA foreign_keys=on');
    const effective: EffectiveSettings = {
      journalMode: readPragmaText(db, 'journal_mode'),
      synchronous: readPragmaInt(db, 'synchronous'),
      foreignKeys: readPragmaInt(db, 'foreign_keys'),
      applicationId,
    };
    return { db, effective };
  } catch (error) {
    db.close();
    throw error;
  }
}

export function acquireOwnership(lockPath: string): Ownership {
  if (!isAbsolute(lockPath)) throw new Error(`lock path must be absolute: ${lockPath}`);
  let before;
  try { before = statSync(lockPath, { bigint: true }); }
  catch { throw new OwnershipRefused(`lock file is missing: ${lockPath}`, 14); }
  let db: DatabaseSync | undefined;
  try {
    db = new DatabaseSync(storeURI(lockPath), { timeout: 0 });
    db.exec('PRAGMA locking_mode=exclusive');
    // First read acquires the shared lock and, in exclusive mode, retains it; a
    // competitor with busy timeout 0 is refused here with errcode 5.
    const journal = readPragmaText(db, 'journal_mode');
    if (journal !== 'delete') throw new Error(`unexpected journal mode for lock: ${journal}`);
    db.prepare('insert into owner(pid, started_at) values (?, ?)').run(process.pid, Date.now());
  } catch (error) {
    try { db?.close(); } catch { /* already closed */ }
    const err = error as { errcode?: number; message?: string };
    if (typeof err.errcode === 'number') throw new OwnershipRefused(err.message ?? 'ownership refused', err.errcode);
    throw error;
  }
  const connection = db!;
  const after = statSync(lockPath, { bigint: true });
  if (after.dev !== before.dev || after.ino !== before.ino) {
    connection.close();
    throw new OwnershipRefused(`lock path replaced during acquisition: ${lockPath}`);
  }
  const storedDev = after.dev;
  const storedIno = after.ino;
  let released = false;
  return {
    pid: process.pid,
    inode: Number(after.ino),
    release() { if (!released) { released = true; try { connection.close(); } catch { /* already closed */ } } },
    isPathReplaced() {
      try { const now = statSync(lockPath, { bigint: true }); return now.dev !== storedDev || now.ino !== storedIno; }
      catch { return true; }
    },
  };
}

interface WorkerMessage { type: string; id?: number; ok?: boolean; effective?: EffectiveSettings; rows?: unknown[]; code?: string; errcode?: number; message?: string }
function makeError(message: WorkerMessage): Error {
  const error = new Error(message.message ?? 'store worker error') as Error & { errcode?: number; code?: string };
  error.errcode = message.errcode;
  error.code = message.code;
  return error;
}

// The store connection lives on a dedicated worker thread so a busy SQLite wait
// never blocks the main event loop.
export function openStoreOnWorker(path: string, options: StoreOptions): StoreWorkerHandle {
  const worker = new Worker(new URL('./store-worker.js', import.meta.url), { workerData: { path, options } });
  const pending = new Map<number, { resolve(rows: unknown[]): void; reject(error: Error): void }>();
  let sequence = 0;
  let openResolve!: (settings: EffectiveSettings) => void;
  let openReject!: (error: Error) => void;
  const opened = new Promise<EffectiveSettings>((resolve, reject) => { openResolve = resolve; openReject = reject; });
  worker.on('message', (message: WorkerMessage) => {
    if (message.type === 'open') {
      if (message.ok && message.effective) openResolve(message.effective);
      else openReject(makeError(message));
    } else if (message.type === 'result' && typeof message.id === 'number') {
      const entry = pending.get(message.id);
      if (!entry) return;
      pending.delete(message.id);
      if (message.ok) entry.resolve(message.rows ?? []);
      else entry.reject(makeError(message));
    }
  });
  worker.on('error', (error) => { openReject(error); for (const entry of pending.values()) entry.reject(error); pending.clear(); });
  return {
    opened,
    run(sql: string): Promise<unknown[]> {
      return new Promise((resolve, reject) => { const id = ++sequence; pending.set(id, { resolve, reject }); worker.postMessage({ type: 'run', id, sql }); });
    },
    async close(): Promise<void> { worker.postMessage({ type: 'close' }); await worker.terminate(); },
  };
}
