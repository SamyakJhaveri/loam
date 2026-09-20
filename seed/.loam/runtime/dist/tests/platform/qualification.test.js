import assert from 'node:assert/strict';
import { test } from 'node:test';
import { appendFileSync, existsSync, linkSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, renameSync, rmSync, statSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { once } from 'node:events';
import { DatabaseSync, backup } from 'node:sqlite';
import { qualifyRuntime, runtimeIdentity, spawnRuntime } from '../../src/platform/runtime.js';
import { acquireOwnership, openExistingStore, openStoreOnWorker, OwnershipRefused, storeURI } from '../../src/platform/ownership.js';
import { containedCommand, PROTECTED_KINDS, sanitizedEnvironment, sanitizeProcessEnvironment } from '../../src/platform/native-boundary.js';
import { STRIP_EXACT, STRIPPED_VARIABLE_NAMES, STRIPPED_VARIABLE_PREFIXES, isStrippedVariable, shouldStrip } from '../../src/platform/env-policy.js';
const manifestPath = fileURLToPath(new URL('../../../assets/runtime-manifest.json', import.meta.url));
const ownershipSource = fileURLToPath(new URL('../../src/platform/ownership.js', import.meta.url));
const STORE_APPID = 0x4c4f414d;
const LOCK_APPID = 0x4c4f434b;
function tmp() { return mkdtempSync(join(tmpdir(), 'loam-core02-')); }
function record(name, mechanism, observed) {
    const trace = process.env.LOAM_FACTORY_OBSERVED_TRACE;
    if (trace)
        appendFileSync(trace, `${JSON.stringify({ case: name, mechanism, observed })}\n`);
}
function createStore(path, appid, extraSql) {
    const d = new DatabaseSync(path);
    d.exec(`PRAGMA application_id=${appid}`);
    if (extraSql)
        d.exec(extraSql);
    d.close();
}
function createLock(path) {
    const d = new DatabaseSync(path);
    d.exec(`PRAGMA application_id=${LOCK_APPID}`);
    d.exec('create table owner(pid integer, started_at integer)');
    d.close();
}
// Inline child holders run as string literals, so they may use require freely.
const LOCK_HOLDER = [
    'const {DatabaseSync}=require("node:sqlite");',
    'const p=process.env.LOAM_LOCK_PATH;',
    'const uri="file:"+p.split("/").map(s=>encodeURIComponent(s)).join("/")+"?mode=rw";',
    'const d=new DatabaseSync(uri,{timeout:0});',
    'd.exec("PRAGMA locking_mode=exclusive");',
    'd.prepare("PRAGMA journal_mode").get();',
    'd.prepare("insert into owner(pid,started_at) values (?,?)").run(process.pid,Date.now());',
    'if(process.env.LOAM_GRANDCHILD_PID){const cp=require("node:child_process");const g=cp.spawn(process.execPath,["-e","setInterval(()=>{},1000)"],{detached:true,stdio:"ignore"});g.unref();require("node:fs").writeFileSync(process.env.LOAM_GRANDCHILD_PID,String(g.pid));}',
    'process.stdout.write("HELD\\n");',
    'setInterval(()=>{},1000);',
].join('');
const STORE_HOLDER = [
    'const {DatabaseSync}=require("node:sqlite");',
    'const p=process.env.LOAM_STORE_PATH;',
    'const uri="file:"+p.split("/").map(s=>encodeURIComponent(s)).join("/")+"?mode=rw";',
    'const d=new DatabaseSync(uri,{timeout:0});',
    'd.exec("PRAGMA locking_mode=exclusive");',
    'd.prepare("PRAGMA journal_mode").get();',
    'd.prepare("insert into t(v) values (1)").run();',
    'process.stdout.write("HELD\\n");',
    'setInterval(()=>{},1000);',
].join('');
function spawnHolder(script, env) {
    return spawn(process.execPath, ['-e', script], { env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'inherit'] });
}
function waitHeld(child) {
    return new Promise((resolve, reject) => {
        let out = '';
        child.stdout.on('data', (d) => { out += d.toString(); if (out.includes('HELD'))
            resolve(); });
        child.on('exit', (code) => reject(new Error(`holder exited early: ${code}`)));
    });
}
async function acquireWithRetry(lockPath, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    for (;;) {
        try {
            return acquireOwnership(lockPath);
        }
        catch (error) {
            if (!(error instanceof OwnershipRefused) || Date.now() > deadline)
                throw error;
            await new Promise((r) => setTimeout(r, 25));
        }
    }
}
test('runtime.identity-matches-manifest', () => {
    const id = runtimeIdentity();
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    assert.equal(id.version, `v${manifest.node}`);
    assert.equal(id.sqlite, manifest.sqlite);
    const key = `${id.platform}-${id.arch}`;
    assert.ok(manifest.platforms[key], `manifest carries platform entry ${key}`);
    const result = qualifyRuntime(manifestPath);
    assert.equal(result.status, 'qualified');
    assert.equal(typeof result.execSha256, 'string');
    assert.equal(typeof result.digestMatches, 'boolean');
});
test('runtime.incompatible-reports-precisely', () => {
    const dir = tmp();
    try {
        const id = runtimeIdentity();
        const key = `${id.platform}-${id.arch}`;
        const base = JSON.parse(readFileSync(manifestPath, 'utf8'));
        const m1 = { ...base, sqlite: '0.0.0', platforms: { ...base.platforms, [key]: { nodeSha256: '0'.repeat(64) } } };
        const p1 = join(dir, 'm1.json');
        writeFileSync(p1, JSON.stringify(m1));
        const r1 = qualifyRuntime(p1, { requireDigest: true });
        assert.equal(r1.status, 'unavailable');
        assert.ok(r1.status === 'unavailable' && r1.reasons.some((x) => x.includes('sqlite')), 'names sqlite');
        assert.ok(r1.status === 'unavailable' && r1.reasons.some((x) => /digest/i.test(x)), 'names digest');
        const withoutHost = { ...base.platforms };
        delete withoutHost[key];
        const m2 = { ...base, platforms: withoutHost };
        const p2 = join(dir, 'm2.json');
        writeFileSync(p2, JSON.stringify(m2));
        const r2 = qualifyRuntime(p2);
        assert.equal(r2.status, 'unavailable');
        assert.ok(r2.status === 'unavailable' && r2.reasons.some((x) => x.includes(key)), 'names platform key');
        const missing = join(dir, 'no-such-node');
        const r3 = qualifyRuntime(manifestPath, { execPath: missing });
        assert.equal(r3.status, 'unavailable');
        assert.ok(r3.status === 'unavailable' && r3.reasons.some((x) => x.includes(missing)), 'names missing executable');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('runtime.child-resolved-explicitly', () => {
    const result = spawnRuntime(['-p', 'process.execPath'], { env: { PATH: '' } });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), process.execPath);
});
test('runtime.foreign-executable-refused', () => {
    const dir = tmp();
    try {
        const fake = join(dir, 'not-node');
        writeFileSync(fake, 'not a runtime');
        const result = qualifyRuntime(manifestPath, { execPath: fake });
        assert.equal(result.status, 'unavailable');
        assert.ok(result.status === 'unavailable' && result.reasons.some((reason) => reason.includes('running executable')));
        assert.equal(qualifyRuntime(manifestPath, { execPath: process.execPath }).status, 'qualified');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.uri-encodes-metacharacters', () => {
    const dir = tmp();
    try {
        const sub = join(dir, 'a b?c#d%e ü');
        mkdirSync(sub, { recursive: true });
        const path = join(sub, 'state.sqlite');
        createStore(path, STORE_APPID, 'create table t(v integer)');
        const uri = storeURI(path);
        assert.ok(uri.startsWith('file:') && uri.endsWith('?mode=rw'));
        for (const token of ['%20', '%3F', '%23', '%25'])
            assert.ok(uri.includes(token), `uri encodes ${token}`);
        const { db } = openExistingStore(path, { applicationId: STORE_APPID });
        try {
            assert.ok(db.prepare('PRAGMA database_list').all().some((row) => row.file === realpathSync(path)));
        }
        finally {
            db.close();
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.missing-refused', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'nope.sqlite');
        let observed;
        assert.throws(() => openExistingStore(path, { applicationId: STORE_APPID }), (e) => { observed = e.errcode; return e.errcode === 14; });
        assert.equal(existsSync(path), false);
        record('storage.missing-refused', 'node:sqlite', observed);
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.authority-shaped-path-refused', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'state.sqlite');
        createStore(path, STORE_APPID);
        const { db } = openExistingStore(path, { applicationId: STORE_APPID });
        db.close();
        for (const ambiguous of [`//localhost${path}`, `/${path}`]) {
            assert.throws(() => openExistingStore(ambiguous, { applicationId: STORE_APPID }), /ambiguous.*path/i);
            assert.throws(() => storeURI(ambiguous), /ambiguous.*path/i);
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.vanish-between-precheck-and-open', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'state.sqlite');
        createStore(path, STORE_APPID);
        assert.ok(existsSync(path));
        rmSync(path);
        let observed;
        assert.throws(() => openExistingStore(path, { applicationId: STORE_APPID }), (e) => { observed = e.errcode; return e.errcode === 14; });
        assert.equal(existsSync(path), false);
        record('storage.vanish-between-precheck-and-open', 'node:sqlite', observed);
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.empty-rejected-as-foreign', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'empty.sqlite');
        writeFileSync(path, '');
        assert.throws(() => openExistingStore(path, { applicationId: STORE_APPID }), (e) => /foreign store/i.test(e.message) && e.message.includes('application_id 0'));
        record('storage.empty-rejected-as-foreign', 'node:sqlite', 'application_id 0');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.foreign-application-id-rejected', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'foreign.sqlite');
        createStore(path, 0x11223344);
        assert.throws(() => openExistingStore(path, { applicationId: STORE_APPID }), (e) => /foreign store/i.test(e.message));
        record('storage.foreign-application-id-rejected', 'node:sqlite', 0x11223344);
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.corrupt-rejected', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'bad.sqlite');
        writeFileSync(path, Buffer.from('this is not a database at all, only random bytes'));
        let observed;
        assert.throws(() => openExistingStore(path, { applicationId: STORE_APPID }), (e) => { observed = e.errcode; return e.errcode === 26; });
        record('storage.corrupt-rejected', 'node:sqlite', observed);
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.arbitrary-uri-refused', () => {
    const dir = tmp();
    try {
        const bads = ['relative/path.sqlite', 'file:/tmp/x.sqlite', ':memory:', `${dir}/a\x00b.sqlite`];
        for (const bad of bads) {
            assert.throws(() => storeURI(bad), `storeURI rejects ${JSON.stringify(bad)}`);
            assert.throws(() => openExistingStore(bad, { applicationId: STORE_APPID }), `openExistingStore rejects ${JSON.stringify(bad)}`);
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.effective-settings-read-back', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'state.sqlite');
        createStore(path, STORE_APPID, 'create table t(v integer)');
        const { db, effective } = openExistingStore(path, { applicationId: STORE_APPID });
        db.close();
        assert.deepEqual(effective, { journalMode: 'delete', synchronous: 3, foreignKeys: 1, applicationId: STORE_APPID });
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.integer-boundaries', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'ints.sqlite');
        createStore(path, STORE_APPID, 'create table t(v integer)');
        const { db } = openExistingStore(path, { applicationId: STORE_APPID });
        try {
            const ins = db.prepare('insert into t(v) values (?)');
            ins.run(9223372036854775807n);
            ins.run(-9223372036854775808n);
            const q = db.prepare('select v from t order by rowid');
            q.setReadBigInts(true);
            assert.deepEqual(q.all().map((row) => row.v), [9223372036854775807n, -9223372036854775808n]);
            db.exec('delete from t');
            ins.run(9007199254790000n);
            const q2 = db.prepare('select v from t');
            assert.throws(() => q2.get(), (e) => e.code === 'ERR_OUT_OF_RANGE');
            assert.throws(() => ins.run(9223372036854775808n), (e) => e.code === 'ERR_INVALID_ARG_VALUE');
        }
        finally {
            db.close();
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.backup-succeeds-and-fails-precisely', async () => {
    const dir = tmp();
    try {
        const path = join(dir, 'state.sqlite');
        createStore(path, STORE_APPID, 'create table t(v integer)');
        const { db } = openExistingStore(path, { applicationId: STORE_APPID });
        try {
            const dest = join(dir, 'copy.sqlite');
            const pages = (await backup(db, dest));
            assert.ok(pages >= 1);
            const copy = new DatabaseSync(storeURI(dest), { timeout: 0 });
            try {
                assert.equal(copy.prepare('PRAGMA application_id').get().application_id, STORE_APPID);
            }
            finally {
                copy.close();
            }
            let observed;
            await assert.rejects(backup(db, join(dir, 'no-such-dir', 'x.sqlite')), (e) => { observed = e.errcode; return e.errcode === 14; });
            record('storage.backup-succeeds-and-fails-precisely', 'node:sqlite', observed);
        }
        finally {
            db.close();
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.busy-worker-keeps-loop-responsive', async () => {
    const dir = tmp();
    const path = join(dir, 'state.sqlite');
    createStore(path, STORE_APPID, 'create table t(v integer)');
    const holder = spawnHolder(STORE_HOLDER, { LOAM_STORE_PATH: path });
    try {
        await waitHeld(holder);
        const handle = openStoreOnWorker(path, { applicationId: STORE_APPID, busyTimeoutMs: 300 });
        let ticks = 0;
        const timer = setInterval(() => { ticks++; }, 20);
        let observed;
        await assert.rejects(handle.opened, (e) => { observed = e.errcode; return e.errcode === 5; });
        clearInterval(timer);
        await handle.close();
        assert.ok(ticks >= 1, `main loop ticked ${ticks} times while the worker waited`);
        record('storage.busy-worker-keeps-loop-responsive', 'node:sqlite', observed);
    }
    finally {
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.competing-owner-refused', async () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const holder = spawnHolder(LOCK_HOLDER, { LOAM_LOCK_PATH: lock });
    try {
        await waitHeld(holder);
        let observed;
        assert.throws(() => acquireOwnership(lock), (e) => { observed = e.errcode; return e instanceof OwnershipRefused && e.errcode === 5; });
        record('lock.competing-owner-refused', 'sqlite-exclusive-lock', observed);
    }
    finally {
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        rmSync(dir, { recursive: true, force: true });
    }
});
async function within(promise) {
    let timer;
    try {
        return await Promise.race([promise, new Promise((_, reject) => {
                timer = setTimeout(() => reject(new Error('worker request did not settle')), 2000);
            })]);
    }
    finally {
        clearTimeout(timer);
    }
}
test('storage.worker-open-failure-rejects-queries', async () => {
    const dir = tmp();
    const handle = openStoreOnWorker(join(dir, 'missing.sqlite'), { applicationId: STORE_APPID });
    try {
        const open = assert.rejects(within(handle.opened), { errcode: 14 });
        const queued = assert.rejects(within(handle.run('select 1')), { errcode: 14 });
        await Promise.all([open, queued]);
        await assert.rejects(within(handle.run('select 1')), { errcode: 14 });
    }
    finally {
        await handle.close();
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.worker-query-succeeds', async () => {
    const dir = tmp();
    const path = join(dir, 'state.sqlite');
    createStore(path, STORE_APPID, 'create table t(v integer)');
    const handle = openStoreOnWorker(path, { applicationId: STORE_APPID });
    try {
        assert.deepEqual(await within(handle.run('select 7 as v')), [{ v: 7 }]);
        assert.equal((await handle.opened).applicationId, STORE_APPID);
        await assert.rejects(within(handle.run('select * from missing_table')), /no such table/);
        assert.deepEqual(await within(handle.run('select 8 as v')), [{ v: 8 }]);
    }
    finally {
        await handle.close();
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.worker-close-rejects-queries', async () => {
    const dir = tmp();
    const path = join(dir, 'state.sqlite');
    createStore(path, STORE_APPID, 'create table t(v integer)');
    const handle = openStoreOnWorker(path, { applicationId: STORE_APPID, busyTimeoutMs: 300 });
    let holder;
    try {
        await handle.opened;
        holder = spawnHolder(STORE_HOLDER, { LOAM_STORE_PATH: path });
        await waitHeld(holder);
        const pending = assert.rejects(within(handle.run('select * from t')), /closed/);
        // Let run() post the query. The separate holder prevents a reply before close.
        await new Promise((resolve) => setImmediate(resolve));
        await handle.close();
        await pending;
        await assert.rejects(within(handle.run('select 1')), /closed/);
        await handle.close();
    }
    finally {
        await handle.close();
        if (holder) {
            holder.kill('SIGKILL');
            await once(holder, 'exit');
        }
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.worker-exit-settles-requests', () => {
    const dir = tmp();
    try {
        const path = join(dir, 'state.sqlite');
        createStore(path, STORE_APPID);
        const moduleURL = new URL('../../src/platform/ownership.js', import.meta.url).href;
        const script = `
      import assert from 'node:assert/strict';
      import threads from 'node:worker_threads';
      import { syncBuiltinESMExports } from 'node:module';
      const OriginalWorker = threads.Worker;
      let worker;
      threads.Worker = class extends OriginalWorker { constructor(...args) { super(...args); worker = this; } };
      syncBuiltinESMExports();
      const { openStoreOnWorker } = await import(${JSON.stringify(moduleURL)});
      const handle = openStoreOnWorker(${JSON.stringify(path)}, { applicationId: ${STORE_APPID} });
      threads.Worker = OriginalWorker; syncBuiltinESMExports();
      const timer = setTimeout(() => { console.error('requests did not settle after exit'); process.exit(2); }, 2000);
      const open = assert.rejects(handle.opened, /exited/);
      const queued = assert.rejects(handle.run('select 1'), /exited/);
      // Terminate the real thread before startup, without handle.close().
      await worker.terminate();
      await Promise.all([open, queued]);
      await assert.rejects(handle.run('select 1'), /exited/);
      await handle.close();
      clearTimeout(timer);
    `;
        const result = spawnRuntime(['--input-type=module', '-e', script]);
        assert.equal(result.status, 0, result.stderr);
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('storage.worker-close-before-open-settles', async () => {
    const dir = tmp();
    const path = join(dir, 'state.sqlite');
    createStore(path, STORE_APPID);
    const handle = openStoreOnWorker(path, { applicationId: STORE_APPID });
    try {
        const open = assert.rejects(within(handle.opened), /closed/);
        const queued = assert.rejects(within(handle.run('select 1')), /closed/);
        const results = await Promise.all([open, queued, handle.close()]);
        assert.equal(results.length, 3);
    }
    finally {
        await handle.close();
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.stopped-owner-still-owns', async () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const holder = spawnHolder(LOCK_HOLDER, { LOAM_LOCK_PATH: lock });
    try {
        await waitHeld(holder);
        holder.kill('SIGSTOP');
        let observed;
        assert.throws(() => acquireOwnership(lock), (e) => { observed = e.errcode; return e instanceof OwnershipRefused && e.errcode === 5; });
        holder.kill('SIGCONT');
        record('lock.stopped-owner-still-owns', 'sqlite-exclusive-lock', observed);
    }
    finally {
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.killed-owner-releases', async () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const holder = spawnHolder(LOCK_HOLDER, { LOAM_LOCK_PATH: lock });
    try {
        await waitHeld(holder);
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        const own = await acquireWithRetry(lock, 2000);
        try {
            assert.equal(own.pid, process.pid);
            assert.equal(own.isPathReplaced(), false);
        }
        finally {
            own.release();
        }
        record('lock.killed-owner-releases', 'sqlite-exclusive-lock', 'reacquired');
    }
    finally {
        try {
            holder.kill('SIGKILL');
        }
        catch { /* already dead */ }
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.child-does-not-inherit', async () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const pidFile = join(dir, 'grandchild.pid');
    const holder = spawnHolder(LOCK_HOLDER, { LOAM_LOCK_PATH: lock, LOAM_GRANDCHILD_PID: pidFile });
    let grandPid = 0;
    try {
        await waitHeld(holder);
        grandPid = Number(readFileSync(pidFile, 'utf8').trim());
        assert.ok(grandPid > 0);
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        assert.doesNotThrow(() => process.kill(grandPid, 0));
        const own = await acquireWithRetry(lock, 2000);
        own.release();
        record('lock.child-does-not-inherit', 'sqlite-exclusive-lock', 'reacquired while grandchild alive');
    }
    finally {
        if (grandPid) {
            try {
                process.kill(grandPid, 'SIGKILL');
            }
            catch { /* already dead */ }
        }
        try {
            holder.kill('SIGKILL');
        }
        catch { /* already dead */ }
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.replaced-path-detected', () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const moved = join(dir, 'owner.lock.moved');
    const own = acquireOwnership(lock);
    try {
        assert.equal(own.isPathReplaced(), false);
        renameSync(lock, moved);
        createLock(lock);
        assert.equal(own.isPathReplaced(), true);
        let observed;
        assert.throws(() => acquireOwnership(moved), (e) => { observed = e.errcode; return e instanceof OwnershipRefused && e.errcode === 5; });
        const fresh = acquireOwnership(lock);
        try {
            assert.equal(fresh.isPathReplaced(), false);
        }
        finally {
            fresh.release();
        }
        record('lock.replaced-path-detected', 'sqlite-exclusive-lock', observed);
    }
    finally {
        own.release();
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.never-unlinks', async () => {
    const dir = tmp();
    const lock = join(dir, 'owner.lock');
    createLock(lock);
    const before = statSync(lock);
    const holder = spawnHolder(LOCK_HOLDER, { LOAM_LOCK_PATH: lock });
    try {
        await waitHeld(holder);
        holder.kill('SIGKILL');
        await once(holder, 'exit');
        const own = await acquireWithRetry(lock, 2000);
        own.release();
        assert.equal(statSync(lock).ino, before.ino, 'takeover keeps the same inode');
        const src = readFileSync(ownershipSource, 'utf8');
        for (const forbidden of ['unlink', 'rmSync', 'renameSync', 'rename(']) {
            assert.ok(!src.includes(forbidden), `ownership.js must not call ${forbidden}`);
        }
    }
    finally {
        try {
            holder.kill('SIGKILL');
        }
        catch { /* already dead */ }
        rmSync(dir, { recursive: true, force: true });
    }
});
test('lock.failed-acquisition-releases', () => {
    const dir = tmp();
    try {
        const lock = join(dir, 'owner.lock');
        createLock(lock);
        const moduleURL = new URL('../../src/platform/ownership.js', import.meta.url).href;
        // Inject the rename at the last stat in an isolated process. The competing
        // process then proves OS lock release while the failed acquirer is alive.
        const script = `
      import assert from 'node:assert/strict';
      import fs from 'node:fs';
      import { syncBuiltinESMExports } from 'node:module';
      import { spawnSync } from 'node:child_process';
      import { acquireOwnership } from ${JSON.stringify(moduleURL)};
      const lock = ${JSON.stringify(lock)}, moved = lock + '.moved';
      const original = fs.statSync;
      let visits = 0;
      fs.statSync = function(path, ...args) {
        if (path === lock && ++visits === 2) fs.renameSync(lock, moved);
        return original(path, ...args);
      };
      syncBuiltinESMExports();
      try { assert.throws(() => acquireOwnership(lock), { code: 'ENOENT' }); }
      finally { fs.statSync = original; syncBuiltinESMExports(); }
      assert.equal(visits, 2);
      fs.renameSync(moved, lock);
      const child = spawnSync(process.execPath, ['--input-type=module', '-e',
        'import { acquireOwnership } from ' + ${JSON.stringify(JSON.stringify(moduleURL))} + ';' +
        'const own = acquireOwnership(' + JSON.stringify(lock) + '); own.release(); console.log("acquired");'
      ], { encoding: 'utf8', timeout: 10000 });
      assert.equal(child.status, 0, child.stderr);
      assert.equal(child.stdout.trim(), 'acquired');
    `;
        const result = spawnRuntime(['--input-type=module', '-e', script]);
        assert.equal(result.status, 0, result.stderr);
        record('lock.failed-acquisition-releases', 'sqlite-exclusive-lock', 'separate process reacquired restored inode');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('env.preload-stripped', () => {
    const dir = tmp();
    try {
        const marker = join(dir, 'preloaded.marker');
        const preload = join(dir, 'preload.cjs');
        writeFileSync(preload, `require("node:fs").writeFileSync(${JSON.stringify(marker)}, "loaded");\n`);
        const options = `--require ${preload}`;
        const sanitized = spawnRuntime(['-e', 'process.stdout.write("ok")'], { env: { ...process.env, NODE_OPTIONS: options } });
        assert.equal(sanitized.status, 0, sanitized.stderr);
        assert.equal(existsSync(marker), false, 'sanitized child must not run the preload');
        const control = spawnSync(process.execPath, ['-e', 'process.stdout.write("ok")'], { env: { ...process.env, NODE_OPTIONS: options }, encoding: 'utf8' });
        assert.equal(control.status, 0, control.stderr);
        assert.equal(existsSync(marker), true, 'unsanitised control must run the preload');
        record('env.preload-stripped', 'sanitized-env', existsSync(marker));
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('boundary.conflicting-layout-refused', () => {
    const dir = tmp();
    try {
        const workspace = join(dir, 'workspace');
        const runtimeDir = join(dir, 'runtime');
        const control = join(dir, 'control');
        for (const path of [workspace, runtimeDir, control])
            mkdirSync(path);
        const protectedPaths = Object.fromEntries(PROTECTED_KINDS.map((kind) => [kind, control]));
        const spec = { workspace, runtimeDir, protectedPaths, execPath: process.execPath, command: ['-e', '0'] };
        function expectRefusal(candidate) {
            const result = containedCommand(candidate);
            try {
                assert.ok('status' in result, 'conflicting layout must not produce a command');
                assert.match(result.reasons.join('; '), /overlap|resolve.*path/i);
            }
            finally {
                if ('profile' in result && result.profile)
                    rmSync(dirname(result.profile), { recursive: true, force: true });
            }
        }
        for (const registry of [workspace, runtimeDir, dir, '/usr', join(dir, 'missing')]) {
            expectRefusal({ ...spec, protectedPaths: { ...protectedPaths, registry } });
        }
        const alias = join(dir, 'workspace-alias');
        symlinkSync(workspace, alias);
        expectRefusal({ ...spec, protectedPaths: { ...protectedPaths, registry: alias } });
        expectRefusal({ ...spec, runtimeDir: workspace });
        const valid = containedCommand(spec);
        try {
            if ('status' in valid)
                assert.match(valid.reasons.join('; '), /bwrap not found|sandbox-exec not found|unsupported platform/);
            else
                assert.ok(valid.file.length > 0, 'disjoint layout produces a command');
        }
        finally {
            if ('profile' in valid && valid.profile)
                rmSync(dirname(valid.profile), { recursive: true, force: true });
        }
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('boundary.hard-link-admission-refused', () => {
    const dir = tmp();
    function layout() {
        const root = mkdtempSync(join(dir, 'layout-'));
        const workspace = join(root, 'workspace');
        const runtimeDir = join(root, 'runtime');
        const neutral = join(root, 'neutral');
        for (const path of [workspace, runtimeDir, neutral])
            mkdirSync(path);
        const protectedPaths = Object.fromEntries(PROTECTED_KINDS.map((kind) => {
            const path = join(root, `protected-${kind}`);
            mkdirSync(path);
            return [kind, path];
        }));
        return { workspace, runtimeDir, neutral, protectedPaths,
            spec: { workspace, runtimeDir, protectedPaths, execPath: process.execPath, command: ['-e', '0'] } };
    }
    function cleanup(result) {
        if ('profile' in result && result.profile)
            rmSync(dirname(result.profile), { recursive: true, force: true });
    }
    function expectRefusal(name, spec) {
        const result = containedCommand(spec);
        try {
            assert.ok('status' in result, `${name} hard link must refuse admission before a launcher command is constructed`);
            assert.match(result.reasons.join('; '), /hard.?link|link count|multiply linked/i, `${name} names its hard-link admission refusal`);
        }
        finally {
            cleanup(result);
        }
    }
    function expectAdmission(name, spec) {
        const result = containedCommand(spec);
        try {
            if ('status' in result)
                assert.match(result.reasons.join('; '), /bwrap not found|sandbox-exec not found|unsupported platform/, `${name} has no admission refusal`);
            else
                assert.ok(result.file.length > 0, `${name} produces a launcher command`);
        }
        finally {
            cleanup(result);
        }
    }
    function hardLink(source, alias) {
        linkSync(source, alias);
        assert.equal(statSync(source).ino, statSync(alias).ino, 'fixture aliases one inode');
        assert.ok(statSync(source).nlink > 1, 'fixture establishes a multiply-linked regular file');
    }
    try {
        const ordinary = layout();
        const lock = join(ordinary.protectedPaths.locks, 'owner.lock');
        createLock(lock);
        const ownership = acquireOwnership(lock);
        try {
            assert.equal(ownership.isPathReplaced(), false, 'ordinary control retains its lifetime ownership lock');
            expectAdmission('ordinary layout while its lock is held', ordinary.spec);
        }
        finally {
            ownership.release();
        }
        const protectedWorkspace = layout();
        const protectedWorkspaceFile = join(protectedWorkspace.protectedPaths.registry, 'marker');
        writeFileSync(protectedWorkspaceFile, 'protected');
        hardLink(protectedWorkspaceFile, join(protectedWorkspace.workspace, 'registry-alias'));
        expectRefusal('protected-to-workspace', protectedWorkspace.spec);
        const protectedRuntime = layout();
        const protectedRuntimeFile = join(protectedRuntime.protectedPaths.registry, 'marker');
        writeFileSync(protectedRuntimeFile, 'protected');
        hardLink(protectedRuntimeFile, join(protectedRuntime.runtimeDir, 'registry-alias'));
        expectRefusal('protected-to-runtime', protectedRuntime.spec);
        const protectedNeutral = layout();
        const protectedNeutralFile = join(protectedNeutral.protectedPaths.registry, 'marker');
        writeFileSync(protectedNeutralFile, 'protected');
        hardLink(protectedNeutralFile, join(protectedNeutral.neutral, 'registry-alias'));
        expectRefusal('protected-to-neutral-sibling', protectedNeutral.spec);
        const runtimeWorkspace = layout();
        const runtimeFile = join(runtimeWorkspace.runtimeDir, 'marker');
        writeFileSync(runtimeFile, 'runtime');
        hardLink(runtimeFile, join(runtimeWorkspace.workspace, 'runtime-alias'));
        expectRefusal('runtime-to-workspace', runtimeWorkspace.spec);
        const workspaceInternal = layout();
        const workspaceFile = join(workspaceInternal.workspace, 'marker');
        writeFileSync(workspaceFile, 'workspace');
        hardLink(workspaceFile, join(workspaceInternal.workspace, 'marker-alias'));
        expectRefusal('workspace-internal', workspaceInternal.spec);
        const cleanProtectedFileRoot = layout();
        const cleanRootFile = join(dir, 'clean-protected-file-root');
        writeFileSync(cleanRootFile, 'protected');
        expectAdmission('single-link protected regular-file root', { ...cleanProtectedFileRoot.spec,
            protectedPaths: { ...cleanProtectedFileRoot.protectedPaths, registry: cleanRootFile } });
        const protectedFileRoot = layout();
        const rootFile = join(dir, 'protected-file-root');
        writeFileSync(rootFile, 'protected');
        hardLink(rootFile, join(protectedFileRoot.neutral, 'protected-root-alias'));
        expectRefusal('protected-regular-file-root', { ...protectedFileRoot.spec,
            protectedPaths: { ...protectedFileRoot.protectedPaths, registry: rootFile } });
        record('boundary.hard-link-admission-refused', 'hard-link-fixtures', 'all aliases rejected');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('env.openssl-startup-stripped', () => {
    const dir = tmp();
    try {
        const config = join(dir, 'openssl.cnf');
        // An inert syntax error proves the control actually consumes this startup input.
        writeFileSync(config, '[unterminated section\n');
        const keys = ['OPENSSL_CONF', 'OPENSSL_CONF_INCLUDE', 'OPENSSL_MODULES', 'OPENSSL_ENGINES'];
        const env = { ...sanitizedEnvironment(process.env), OPENSSL_CONF: config,
            OPENSSL_CONF_INCLUDE: dir, OPENSSL_MODULES: dir, OPENSSL_ENGINES: dir };
        const script = `process.stdout.write(JSON.stringify(${JSON.stringify(keys)}.map(k => process.env[k] ?? null)))`;
        const control = spawnSync(process.execPath, ['-e', script], { env, encoding: 'utf8' });
        assert.equal(control.error, undefined);
        assert.notEqual(control.status, 0, 'control must consume the malformed configuration');
        assert.match(control.stderr, /OpenSSL configuration error/i);
        const clean = spawnRuntime(['-e', script], { env });
        assert.equal(clean.status, 0, clean.stderr);
        assert.deepEqual(JSON.parse(clean.stdout), keys.map(() => null));
        record('env.openssl-startup-stripped', 'sanitized-env', 'control consumes config; clean child starts without overrides');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('env.git-redirection-stripped', () => {
    const dir = tmp();
    try {
        const repoA = join(dir, 'a');
        const repoB = join(dir, 'b');
        for (const repo of [repoA, repoB]) {
            mkdirSync(repo, { recursive: true });
            const init = spawnSync('git', ['init', '-q'], { cwd: repo, env: sanitizedEnvironment(process.env), encoding: 'utf8' });
            assert.equal(init.status, 0, `git init failed (git required): ${init.error?.message ?? init.stderr}`);
        }
        const redirected = { ...process.env, GIT_DIR: join(repoB, '.git'), GIT_WORK_TREE: repoB };
        const clean = spawnSync('git', ['rev-parse', '--show-toplevel'], { cwd: repoA, env: sanitizedEnvironment(redirected), encoding: 'utf8' });
        assert.equal(clean.status, 0, clean.stderr);
        assert.equal(realpathSync(clean.stdout.trim()), realpathSync(repoA));
        const control = spawnSync('git', ['rev-parse', '--show-toplevel'], { cwd: repoA, env: redirected, encoding: 'utf8' });
        assert.equal(control.status, 0, control.stderr);
        assert.equal(realpathSync(control.stdout.trim()), realpathSync(repoB));
        record('env.git-redirection-stripped', 'sanitized-env', 'redirection ignored');
    }
    finally {
        rmSync(dir, { recursive: true, force: true });
    }
});
test('env.process-sanitized-before-children', () => {
    const keys = ['NODE_OPTIONS', 'GIT_DIR', 'DYLD_INSERT_LIBRARIES', 'OPENSSL_CONF', 'OPENSSL_CONF_INCLUDE', 'OPENSSL_MODULES', 'OPENSSL_ENGINES'];
    const saved = {};
    for (const key of keys)
        saved[key] = process.env[key];
    try {
        process.env.NODE_OPTIONS = '--max-old-space-size=64';
        process.env.GIT_DIR = '/tmp/elsewhere/.git';
        process.env.DYLD_INSERT_LIBRARIES = '/tmp/evil.dylib';
        for (const key of keys.filter((key) => key.startsWith('OPENSSL_')))
            process.env[key] = '/unused/startup-input';
        sanitizeProcessEnvironment();
        for (const key of keys)
            assert.equal(process.env[key], undefined, `${key} removed from process.env`);
        const child = spawnSync(process.execPath, ['-e', 'process.stdout.write(JSON.stringify([process.env.NODE_OPTIONS,process.env.GIT_DIR,process.env.DYLD_INSERT_LIBRARIES]))'], { encoding: 'utf8' });
        assert.equal(child.status, 0, child.stderr);
        assert.deepEqual(JSON.parse(child.stdout), [null, null, null]);
    }
    finally {
        for (const key of keys) {
            if (saved[key] === undefined)
                delete process.env[key];
            else
                process.env[key] = saved[key];
        }
    }
});
// B2: env-policy.ts holds two environment-strip sets that differ on purpose - the
// enforcement set a trusted spawner deletes before spawn, and the diagnostic set
// doctor refuses to see. These pin each set exactly, so a merge or a silent drift
// of either list fails here instead of shipping.
test('env.enforcement-set-pinned', () => {
    assert.deepStrictEqual([...STRIP_EXACT].sort(), [
        'BASH_ENV', 'ENV', 'LD_AUDIT', 'LD_LIBRARY_PATH', 'LD_PRELOAD',
        'NODE_EXTRA_CA_CERTS', 'NODE_OPTIONS', 'NODE_PATH', 'NODE_PRESERVE_SYMLINKS_MAIN',
        'NODE_REPL_EXTERNAL_MODULE', 'NODE_TLS_REJECT_UNAUTHORIZED',
        'OPENSSL_CONF', 'OPENSSL_CONF_INCLUDE', 'OPENSSL_ENGINES', 'OPENSSL_MODULES',
        'PERL5OPT', 'PROMPT_COMMAND', 'PYTHONPATH', 'PYTHONSTARTUP',
    ]);
    assert.equal(shouldStrip('DYLD_INSERT_LIBRARIES'), true);
    assert.equal(shouldStrip('GIT_DIR'), true);
    assert.equal(shouldStrip('GIT_TERMINAL_PROMPT'), false);
    assert.equal(shouldStrip('LD_FOO'), false);
    assert.equal(shouldStrip('npm_config_registry'), false);
    record('env.enforcement-set-pinned', 'env-policy', STRIP_EXACT.size);
});
test('env.diagnostic-set-pinned', () => {
    assert.deepStrictEqual([...STRIPPED_VARIABLE_NAMES], [
        'NODE_OPTIONS', 'NODE_PATH', 'NODE_REPL_EXTERNAL_MODULE', 'NODE_EXTRA_CA_CERTS',
        'NODE_TLS_REJECT_UNAUTHORIZED', 'OPENSSL_CONF',
    ]);
    assert.deepStrictEqual([...STRIPPED_VARIABLE_PREFIXES], ['DYLD_', 'LD_', 'NPM_CONFIG_']);
    assert.equal(isStrippedVariable('DYLD_INSERT_LIBRARIES'), true);
    assert.equal(isStrippedVariable('GIT_DIR'), true);
    assert.equal(isStrippedVariable('GIT_TERMINAL_PROMPT'), false);
    assert.equal(isStrippedVariable('LD_FOO'), true);
    assert.equal(isStrippedVariable('npm_config_registry'), true);
    record('env.diagnostic-set-pinned', 'env-policy', STRIPPED_VARIABLE_NAMES.length);
});
test('env.strip-sets-diverge', () => {
    // The enforcement set strips only the three exact LD_ names, so LD_FOO and npm
    // config pass it; the diagnostic set strips every LD_ name and npm config via
    // prefix. Both agree on the DYLD_ prefix and the GIT_-except-GIT_TERMINAL_PROMPT
    // rule, and on every NODE_/OPENSSL_ exact name they share.
    for (const name of ['LD_FOO', 'npm_config_registry', 'NPM_CONFIG_REGISTRY']) {
        assert.equal(shouldStrip(name), false, `${name} is not enforcement-stripped`);
        assert.equal(isStrippedVariable(name), true, `${name} is diagnostic-stripped`);
    }
    assert.equal(shouldStrip('GIT_TERMINAL_PROMPT'), false);
    assert.equal(isStrippedVariable('GIT_TERMINAL_PROMPT'), false);
    for (const name of ['GIT_DIR', 'DYLD_INSERT_LIBRARIES', 'NODE_OPTIONS', 'OPENSSL_CONF']) {
        assert.equal(shouldStrip(name), true, `${name} is enforcement-stripped`);
        assert.equal(isStrippedVariable(name), true, `${name} is diagnostic-stripped`);
    }
    record('env.strip-sets-diverge', 'env-policy', 'sets differ as pinned');
});
//# sourceMappingURL=qualification.test.js.map