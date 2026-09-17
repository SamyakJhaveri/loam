const KEYWORDS = new Set(['$schema', '$id', '$defs', '$ref', 'type', 'properties', 'required', 'additionalProperties', 'items', 'enum', 'const', 'pattern', 'minItems', 'uniqueItems', 'description']);
const TYPES = new Set(['object', 'array', 'string', 'integer', 'number', 'boolean', 'null']);
export function isRecord(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
export function deepEqual(a, b) {
    if (a === b)
        return true;
    if (Array.isArray(a) && Array.isArray(b))
        return a.length === b.length && a.every((v, i) => deepEqual(v, b[i]));
    if (isRecord(a) && isRecord(b)) {
        const ka = Object.keys(a).sort();
        const kb = Object.keys(b).sort();
        return deepEqual(ka, kb) && ka.every(k => deepEqual(a[k], b[k]));
    }
    return false;
}
function jsonType(value) {
    if (value === null)
        return 'null';
    if (Array.isArray(value))
        return 'array';
    if (typeof value === 'number')
        return Number.isInteger(value) ? 'integer' : 'number';
    return typeof value;
}
function isJson(value) {
    if (value === null || ['boolean', 'string'].includes(typeof value))
        return true;
    if (typeof value === 'number')
        return Number.isFinite(value);
    if (Array.isArray(value))
        return value.every(isJson);
    return isRecord(value) && Object.values(value).every(isJson);
}
// Structural validation of the schema document itself.
export function assertSchemaDocument(schema) {
    if (!isRecord(schema))
        throw new Error('Schema root must be an object');
    const defs = isRecord(schema.$defs) ? schema.$defs : {};
    const fail = (path, message) => { throw new Error(`Invalid schema at ${path}: ${message}`); };
    function node(value, path, root) {
        if (!isRecord(value))
            return fail(path, 'schema must be an object');
        for (const key of Object.keys(value)) {
            if (!KEYWORDS.has(key))
                fail(path, `unknown keyword ${key}`);
            if (!root && (key === '$schema' || key === '$id' || key === '$defs'))
                fail(path, `${key} allowed only at the root`);
        }
        if ('$ref' in value) {
            const extra = Object.keys(value).filter(k => k !== '$ref' && k !== 'description');
            if (extra.length)
                fail(path, `$ref cannot combine with ${extra.join(',')}`);
            const ref = value.$ref;
            if (typeof ref !== 'string' || !/^#\/\$defs\/[A-Za-z0-9_-]+$/.test(ref))
                return fail(path, 'only local #/$defs references are supported');
            if (!(ref.slice('#/$defs/'.length) in defs))
                fail(path, `unresolved reference ${ref}`);
        }
        if ('$schema' in value && typeof value.$schema !== 'string')
            fail(path, '$schema must be a string');
        if ('$id' in value && typeof value.$id !== 'string')
            fail(path, '$id must be a string');
        if ('description' in value && typeof value.description !== 'string')
            fail(path, 'description must be a string');
        if ('type' in value) {
            const types = Array.isArray(value.type) ? value.type : [value.type];
            if (!types.length || types.some(t => typeof t !== 'string' || !TYPES.has(t)) || new Set(types).size !== types.length)
                fail(path, 'type must name one or more distinct JSON types');
        }
        if ('properties' in value) {
            if (!isRecord(value.properties))
                fail(path, 'properties must be an object');
            for (const [name, sub] of Object.entries(value.properties))
                node(sub, `${path}/properties/${name}`, false);
        }
        if ('required' in value) {
            const required = value.required;
            if (!Array.isArray(required) || required.some(r => typeof r !== 'string') || new Set(required).size !== required.length)
                fail(path, 'required must be an array of distinct strings');
            const names = isRecord(value.properties) ? Object.keys(value.properties) : [];
            for (const name of required)
                if (!names.includes(name))
                    fail(path, `required property ${name} is not declared`);
        }
        if ('additionalProperties' in value && value.additionalProperties !== false)
            fail(path, 'additionalProperties must be false');
        if ('items' in value)
            node(value.items, `${path}/items`, false);
        if ('enum' in value) {
            const values = value.enum;
            if (!Array.isArray(values) || !values.length || !values.every(isJson))
                return fail(path, 'enum must be a nonempty array of JSON values');
            for (let i = 0; i < values.length; i++)
                for (let j = i + 1; j < values.length; j++)
                    if (deepEqual(values[i], values[j]))
                        fail(path, 'enum values must be distinct');
        }
        if ('const' in value && !isJson(value.const))
            fail(path, 'const must be a JSON value');
        if ('pattern' in value) {
            const pattern = value.pattern;
            if (typeof pattern !== 'string' || !pattern.startsWith('^') || !pattern.endsWith('$'))
                return fail(path, 'pattern must be an anchored string');
            try {
                new RegExp(pattern, 'u');
            }
            catch {
                fail(path, 'pattern must compile');
            }
        }
        if ('minItems' in value && (typeof value.minItems !== 'number' || !Number.isInteger(value.minItems) || value.minItems < 0))
            fail(path, 'minItems must be a non-negative integer');
        if ('uniqueItems' in value && typeof value.uniqueItems !== 'boolean')
            fail(path, 'uniqueItems must be a boolean');
    }
    node(schema, '#', true);
    if ('$defs' in schema) {
        if (!isRecord(schema.$defs))
            fail('#/$defs', '$defs must be an object');
        for (const [name, sub] of Object.entries(defs)) {
            if (KEYWORDS.has(name))
                fail(`#/$defs/${name}`, 'definition name collides with a keyword');
            node(sub, `#/$defs/${name}`, false);
        }
    }
    // Reference graph must be acyclic: a definition may not reach itself through $ref.
    const refsOf = (value, out) => {
        if (!isRecord(value))
            return out;
        if (typeof value.$ref === 'string')
            out.add(value.$ref.slice('#/$defs/'.length));
        for (const [key, sub] of Object.entries(value)) {
            if (key === 'properties' && isRecord(sub))
                for (const p of Object.values(sub))
                    refsOf(p, out);
            else if (key === 'items')
                refsOf(sub, out);
        }
        return out;
    };
    const graph = new Map(Object.entries(defs).map(([name, sub]) => [name, refsOf(sub, new Set())]));
    const state = new Map();
    const visit = (name, trail) => {
        if (state.get(name) === 2)
            return;
        if (state.get(name) === 1)
            fail(`#/$defs/${name}`, `cyclic reference through ${[...trail, name].join(' -> ')}`);
        state.set(name, 1);
        for (const next of graph.get(name) ?? [])
            visit(next, [...trail, name]);
        state.set(name, 2);
    };
    for (const name of graph.keys())
        visit(name, []);
}
// Instance validation. Returns every issue found; an empty list means valid.
export function validate(schema, instance) {
    assertSchemaDocument(schema);
    const root = schema;
    const defs = isRecord(root.$defs) ? root.$defs : {};
    const issues = [];
    const issue = (path, keyword, message) => { issues.push({ path, keyword, message }); };
    function check(node, value, path) {
        if (typeof node.$ref === 'string') {
            check(defs[node.$ref.slice('#/$defs/'.length)], value, path);
            return;
        }
        if ('type' in node) {
            const allowed = Array.isArray(node.type) ? node.type : [node.type];
            const actual = jsonType(value);
            if (!allowed.includes(actual) && !(actual === 'integer' && allowed.includes('number'))) {
                issue(path, 'type', `expected ${allowed.join('|')}, got ${actual}`);
                return;
            }
        }
        if ('enum' in node && !node.enum.some(v => deepEqual(v, value)))
            issue(path, 'enum', 'value is not one of the permitted values');
        if ('const' in node && !deepEqual(node.const, value))
            issue(path, 'const', 'value differs from the required constant');
        if ('pattern' in node && typeof value === 'string' && !new RegExp(node.pattern, 'u').test(value))
            issue(path, 'pattern', `value does not match ${String(node.pattern)}`);
        if (isRecord(value)) {
            const properties = isRecord(node.properties) ? node.properties : {};
            for (const name of node.required ?? [])
                if (!(name in value))
                    issue(path, 'required', `missing property ${name}`);
            for (const [name, sub] of Object.entries(value)) {
                if (name in properties)
                    check(properties[name], sub, `${path}/${name}`);
                else if (node.additionalProperties === false)
                    issue(`${path}/${name}`, 'additionalProperties', 'property is not declared');
            }
        }
        if (Array.isArray(value)) {
            if ('minItems' in node && value.length < node.minItems)
                issue(path, 'minItems', `expected at least ${String(node.minItems)} items`);
            if (node.uniqueItems === true)
                for (let i = 0; i < value.length; i++)
                    for (let j = i + 1; j < value.length; j++)
                        if (deepEqual(value[i], value[j])) {
                            issue(path, 'uniqueItems', `items ${i} and ${j} are equal`);
                            i = value.length;
                            break;
                        }
            if (isRecord(node.items))
                value.forEach((item, i) => check(node.items, item, `${path}/${i}`));
        }
    }
    check(root, instance, '#');
    return issues;
}
export function assertValid(schema, instance, label = 'instance') {
    const issues = validate(schema, instance);
    if (issues.length)
        throw new Error(`${label} violates schema: ${issues.slice(0, 5).map(i => `${i.path} [${i.keyword}] ${i.message}`).join('; ')}${issues.length > 5 ? ` (+${issues.length - 5} more)` : ''}`);
}
//# sourceMappingURL=schema.js.map