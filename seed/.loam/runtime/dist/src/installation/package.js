import { createHash } from 'node:crypto';
import { lstatSync, readdirSync, readFileSync } from 'node:fs';
import { isBuiltin } from 'node:module';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
const ignored = new Set(['node_modules', '.cache', '.state', 'runtime-installation']);
const directories = new Set(['src', 'tests', 'scripts', 'assets', 'dist']);
const required = ['.gitignore', 'package.json', 'package-lock.json', 'tsconfig.json', 'launcher.mjs', 'assets/runtime-manifest.json', 'assets/curated-catalog.json', 'assets/curated-catalog.schema.json'];
const topFiles = new Set([...required.filter(p => !p.includes('/')), 'release-manifest.json']);
const hash = (value) => createHash('sha256').update(value).digest('hex');
const sorted = (paths) => paths.sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)));
function safe(path) {
    if (!path || isAbsolute(path) || path.includes('\\') || path.split('/').some(p => !p || p === '.' || p === '..') || /[\x00-\x1f\x7f]/.test(path))
        throw new Error(`Unsafe payload path: ${path}`);
}
function record(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
function checkMap(root, path) {
    const map = JSON.parse(readFileSync(join(root, path), 'utf8'));
    if (!record(map) || map.version !== 3 || !Array.isArray(map.sources) || typeof map.file !== 'string' || typeof map.mappings !== 'string')
        throw new Error(`Invalid source map: ${path}`);
    if (map.sourceRoot !== undefined && map.sourceRoot !== '')
        throw new Error(`Source map sourceRoot forbidden: ${path}`);
    if ('sourcesContent' in map)
        throw new Error(`Embedded source forbidden: ${path}`);
    if (map.file !== path.split('/').at(-1)?.replace(/\.map$/, ''))
        throw new Error(`Source map file mismatch: ${path}`);
    for (const source of map.sources) {
        if (typeof source !== 'string' || isAbsolute(source) || /[\\:]|(?:^|\/)private\/tmp(?:\/|$)/.test(source))
            throw new Error(`Machine path in map: ${path}`);
        const resolved = relative(root, resolve(root, dirname(path), source)).split(sep).join('/');
        safe(resolved);
        if (!/^(src|tests)\/.+\.ts$/.test(resolved) || !lstatSync(join(root, resolved)).isFile())
            throw new Error(`Map source outside canonical inputs: ${path}`);
    }
}
export function payloadFiles(root) {
    if (!lstatSync(root).isDirectory() || lstatSync(root).isSymbolicLink())
        throw new Error('Payload root must be a real directory');
    const files = [];
    function walk(directory) {
        for (const name of readdirSync(join(root, directory))) {
            const path = directory ? `${directory}/${name}` : name;
            safe(path);
            const stat = lstatSync(join(root, path));
            if (stat.isSymbolicLink())
                throw new Error(`Payload symlink forbidden: ${path}`);
            if (!directory && ignored.has(name)) {
                if (!stat.isDirectory())
                    throw new Error(`Excluded directory is not a directory: ${path}`);
                continue;
            }
            if (stat.isDirectory()) {
                if (!directory && !directories.has(name))
                    throw new Error(`Unknown payload directory: ${path}`);
                walk(path);
            }
            else if (stat.isFile()) {
                if (!directory && !topFiles.has(name))
                    throw new Error(`Unknown payload file: ${path}`);
                if (path.startsWith('dist/') && (!/\.(js|js\.map)$/.test(path) || path.endsWith('.d.ts')))
                    throw new Error(`Invalid dist type: ${path}`);
                if (path.startsWith('dist/') && path.endsWith('.map'))
                    checkMap(root, path);
                files.push(path);
            }
            else
                throw new Error(`Nonregular payload entry: ${path}`);
        }
    }
    walk('');
    return sorted(files);
}
export function snapshot(root) {
    return Object.fromEntries(payloadFiles(root).map(path => [path, hash(readFileSync(join(root, path)))]));
}
export function createReleaseManifest(root) {
    const files = snapshot(root);
    delete files['release-manifest.json'];
    for (const path of required)
        if (!files[path])
            throw new Error(`Missing required payload: ${path}`);
    if (!Object.keys(files).some(p => p.startsWith('dist/')))
        throw new Error('Missing compiled output');
    const digest = (predicate) => hash(JSON.stringify(Object.entries(files).filter(([path]) => predicate(path))));
    return { version: 1, files, sourceDigest: digest(p => !p.startsWith('dist/') && p !== 'package-lock.json'), outputDigest: digest(p => p.startsWith('dist/')), dependencyDigest: files['package-lock.json'] };
}
export function verifyPackage(root) {
    const value = JSON.parse(readFileSync(join(root, 'release-manifest.json'), 'utf8'));
    const keys = ['dependencyDigest', 'files', 'outputDigest', 'sourceDigest', 'version'];
    if (!record(value) || JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(keys) || value.version !== 1 || !record(value.files))
        throw new Error('Invalid release manifest schema');
    for (const [path, digest] of Object.entries(value.files)) {
        safe(path);
        if (path === 'release-manifest.json' || typeof digest !== 'string' || !/^[a-f0-9]{64}$/.test(digest))
            throw new Error(`Invalid manifest entry: ${path}`);
    }
    const actual = createReleaseManifest(root);
    if (JSON.stringify(value) !== JSON.stringify(actual))
        throw new Error('Payload inventory or digest mismatch');
    assertImportClosure(root);
    return { files: Object.keys(actual.files).length, sourceDigest: actual.sourceDigest, outputDigest: actual.outputDigest, dependencyDigest: actual.dependencyDigest };
}
// Tokenize enough JavaScript to distinguish code from strings and comments. The
// build emits plain ESM; templates cannot provide import specifiers.
function tokens(code) {
    const result = [];
    let i = 0;
    while (i < code.length) {
        const rest = code.slice(i);
        if (/^\s/.test(rest)) {
            i++;
            continue;
        }
        if (rest.startsWith('//')) {
            const end = code.indexOf('\n', i);
            i = end < 0 ? code.length : end + 1;
            continue;
        }
        if (rest.startsWith('/*')) {
            const end = code.indexOf('*/', i + 2);
            if (end < 0)
                throw new Error('Unterminated comment');
            i = end + 2;
            continue;
        }
        if (code[i] === '/' && (!result.length || ['(', '=', '[', ',', ':', '!', '&', '|', '?', 'return', '>'].includes(result.at(-1).value))) {
            let bracket = false;
            i++;
            while (i < code.length) {
                if (code[i] === '\\') {
                    i += 2;
                    continue;
                }
                if (code[i] === '[')
                    bracket = true;
                if (code[i] === ']')
                    bracket = false;
                if (code[i++] === '/' && !bracket)
                    break;
            }
            while (/[a-z]/i.test(code[i] ?? '') && i < code.length)
                i++;
            result.push({ value: '<regexp>', literal: true });
            continue;
        }
        const quote = code[i];
        if (quote === '"' || quote === "'" || quote === '`') {
            let value = '';
            let escaped = false;
            i++;
            while (i < code.length && code[i] !== quote) {
                if (code[i] === '\\') {
                    escaped = true;
                    value += code[i++];
                }
                value += code[i++];
            }
            i++;
            if (quote === '`' && new RegExp(String.raw `\$\{[\s\S]*\b(?:import|require|createRequire)\s*(?:\(|\.)`).test(value))
                throw new Error('Module loading in template interpolation forbidden');
            result.push({ value, literal: quote !== '`' && !escaped, quoted: true });
            continue;
        }
        const word = /^[A-Za-z_$][\w$]*/.exec(rest);
        if (word) {
            result.push({ value: word[0], literal: false });
            i += word[0].length;
        }
        else {
            result.push({ value: code[i++], literal: false });
        }
    }
    return result;
}
export function assertImportClosure(root) {
    const files = payloadFiles(root);
    const inventory = new Set(files);
    for (const path of files.filter(p => p.endsWith('.js') || p.endsWith('.mjs'))) {
        const parts = tokens(readFileSync(join(root, path), 'utf8'));
        const check = (specifier) => {
            if (specifier.startsWith('node:') && isBuiltin(specifier))
                return;
            if (!specifier.startsWith('./') && !specifier.startsWith('../'))
                throw new Error(`Bare or invalid import in ${path}: ${specifier}`);
            if (!/\.(js|mjs)$/.test(specifier) || /[\\?#%]/.test(specifier))
                throw new Error(`Invalid module import in ${path}: ${specifier}`);
            const target = relative(root, resolve(root, dirname(path), specifier)).split(sep).join('/');
            safe(target);
            if (!inventory.has(target))
                throw new Error(`Missing imported payload: ${target}`);
        };
        for (let i = 0; i < parts.length; i++) {
            const token = parts[i];
            if (token.quoted && token.value === 'createRequire' && parts[i - 1]?.value === '[' && parts[i + 1]?.value === ']')
                throw new Error(`Computed CommonJS loading forbidden: ${path}`);
            if (token.literal)
                continue;
            if (token.value === 'require' || token.value === 'createRequire')
                throw new Error(`CommonJS loading forbidden: ${path}`);
            if (token.value !== 'import' && token.value !== 'export')
                continue;
            if (parts[i + 1]?.value === '.') {
                if (parts[i + 2]?.value === 'meta' && parts[i + 4]?.value === 'resolve')
                    throw new Error(`Dynamic resolution forbidden: ${path}`);
                continue;
            }
            if (parts[i + 1]?.value === '(') {
                if (!parts[i + 2]?.literal || parts[i + 3]?.value !== ')')
                    throw new Error(`Computed import forbidden: ${path}`);
                check(parts[i + 2].value);
                continue;
            }
            if (parts[i + 1]?.quoted) {
                if (!parts[i + 1]?.literal)
                    throw new Error(`Escaped or template import specifier forbidden: ${path}`);
                check(parts[i + 1].value);
                continue;
            }
            for (let j = i + 1; j < parts.length && parts[j]?.value !== ';'; j++) {
                if (parts[j]?.value === 'from') {
                    if (!parts[j + 1]?.literal)
                        throw new Error(`Invalid import declaration: ${path}`);
                    check(parts[j + 1].value);
                    break;
                }
                if (parts[j]?.value === '=' || parts[j]?.value === 'function' || parts[j]?.value === 'class')
                    break;
            }
        }
    }
}
//# sourceMappingURL=package.js.map