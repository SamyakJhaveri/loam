// Deterministic builder for the CORE-04 offline admission fixtures.
//
// Each fixture under tests/installation/fixtures/<name>/ is packed into
// assets/admission-fixtures/<name>-<version>.tgz as an npm-style tarball (every
// entry under a package/ prefix). The output is byte-reproducible: entries are
// sorted, mtime and owner ids are fixed, uname/gname are empty, file modes are
// normalized, and the gzip header's mtime and OS bytes are zeroed. So a rebuild
// always equals the committed bytes and `... admission-fixtures.mjs check`
// proves it in CI.
//
// It has no imports beyond node: builtins, so it passes the payload import
// closure when the scripts directory is scanned.
import { readFileSync, readdirSync, writeFileSync, lstatSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';

const factoryRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const fixturesDir = join(factoryRoot, 'tests', 'installation', 'fixtures');
const assetsDir = join(factoryRoot, 'assets', 'admission-fixtures');

// Every fixture package this builder ships, in a fixed order.
const PACKAGES = [
  'loam-dep-plain',
  'loam-dep-bin',
  'loam-dep-scripted',
  'loam-dep-mutating',
  'loam-dep-failing',
];
const FIXED_MODE = 0o644;
const FIXED_MTIME = 0;

function octal(value, width) {
  return value.toString(8).padStart(width - 1, '0') + '\0';
}
function header(name, size) {
  const block = Buffer.alloc(512, 0);
  block.write(name, 0, 'utf8');
  block.write(octal(FIXED_MODE, 8), 100, 'ascii');
  block.write(octal(0, 8), 108, 'ascii');
  block.write(octal(0, 8), 116, 'ascii');
  block.write(octal(size, 12), 124, 'ascii');
  block.write(octal(FIXED_MTIME, 12), 136, 'ascii');
  block.write('        ', 148, 'ascii'); // checksum placeholder: eight spaces
  block.write('0', 156, 'ascii'); // typeflag: regular file
  block.write('ustar\0', 257, 'ascii');
  block.write('00', 263, 'ascii');
  let sum = 0;
  for (const byte of block) sum += byte;
  block.write(sum.toString(8).padStart(6, '0') + '\0 ', 148, 'ascii');
  return block;
}
function packageFiles(name) {
  const dir = join(fixturesDir, name);
  const names = readdirSync(dir).filter((entry) => {
    const stat = lstatSync(join(dir, entry));
    if (stat.isSymbolicLink() || !stat.isFile()) throw new Error(`fixture ${name} has a non-file entry: ${entry}`);
    return true;
  }).sort();
  return names.map((entry) => ({ path: `package/${entry}`, data: readFileSync(join(dir, entry)) }));
}
function buildTarball(name) {
  const chunks = [];
  for (const file of packageFiles(name)) {
    if (Buffer.byteLength(file.path) > 100) throw new Error(`fixture path too long for ustar: ${file.path}`);
    chunks.push(header(file.path, file.data.length));
    chunks.push(file.data);
    const remainder = file.data.length % 512;
    if (remainder !== 0) chunks.push(Buffer.alloc(512 - remainder, 0));
  }
  chunks.push(Buffer.alloc(1024, 0)); // two zero blocks end the archive
  const tar = Buffer.concat(chunks);
  const gz = gzipSync(tar, { level: 9 });
  gz.writeUInt32LE(0, 4); // zero the gzip header mtime for reproducibility
  gz[9] = 0; // fixed OS byte
  return gz;
}
function version(name) {
  const meta = JSON.parse(readFileSync(join(fixturesDir, name, 'package.json'), 'utf8'));
  if (meta.name !== name) throw new Error(`fixture ${name} declares a different package name: ${meta.name}`);
  return meta.version;
}
function tarballPath(name) {
  return join(assetsDir, `${name}-${version(name)}.tgz`);
}
function digests(bytes) {
  return {
    sha256: createHash('sha256').update(bytes).digest('hex'),
    integrity: `sha512-${createHash('sha512').update(bytes).digest('base64')}`,
  };
}

function build() {
  const report = [];
  for (const name of PACKAGES) {
    const bytes = buildTarball(name);
    const path = tarballPath(name);
    writeFileSync(path, bytes);
    report.push({ name, version: version(name), file: `assets/admission-fixtures/${name}-${version(name)}.tgz`, bytes: bytes.length, ...digests(bytes) });
  }
  console.log(JSON.stringify({ kind: 'admission-fixtures', action: 'build', tarballs: report }, null, 2));
}
function check() {
  const report = [];
  let drift = false;
  for (const name of PACKAGES) {
    const rebuilt = buildTarball(name);
    const path = tarballPath(name);
    const committed = existsSync(path) ? readFileSync(path) : Buffer.alloc(0);
    const matches = committed.length === rebuilt.length && committed.equals(rebuilt);
    if (!matches) drift = true;
    report.push({ name, matches, ...digests(rebuilt) });
  }
  console.log(JSON.stringify({ kind: 'admission-fixtures', action: 'check', drift, tarballs: report }, null, 2));
  if (drift) throw new Error('committed admission fixtures differ from a deterministic rebuild');
}

const mode = process.argv[2];
if (mode === undefined || mode === 'build') build();
else if (mode === 'check') check();
else throw new Error('Usage: admission-fixtures.mjs [build|check]');
