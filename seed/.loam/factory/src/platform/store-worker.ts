import { parentPort, workerData } from 'node:worker_threads';
import type { DatabaseSync } from 'node:sqlite';
import { openExistingStore, type StoreOptions } from './ownership.js';

// Worker entry for openStoreOnWorker. The SQLite open and every query run on this
// dedicated thread so a busy store never blocks the main event loop.
const port = parentPort;
if (port) {
  const { path, options } = workerData as { path: string; options: StoreOptions };
  let db: DatabaseSync | undefined;
  try {
    const opened = openExistingStore(path, options);
    db = opened.db;
    port.postMessage({ type: 'open', ok: true, effective: opened.effective });
  } catch (error) {
    const err = error as { code?: string; errcode?: number; message?: string };
    port.postMessage({ type: 'open', ok: false, code: err.code, errcode: err.errcode, message: err.message ?? String(error) });
  }
  port.on('message', (message: { type: string; id?: number; sql?: string }) => {
    if (message.type === 'run') {
      try {
        const rows = db ? db.prepare(message.sql ?? '').all() : [];
        port.postMessage({ type: 'result', id: message.id, ok: true, rows });
      } catch (error) {
        const err = error as { code?: string; errcode?: number; message?: string };
        port.postMessage({ type: 'result', id: message.id, ok: false, code: err.code, errcode: err.errcode, message: err.message ?? String(error) });
      }
    } else if (message.type === 'close') {
      try { db?.close(); } catch { /* already closed */ }
      port.postMessage({ type: 'closed' });
    }
  });
}
