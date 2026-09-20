// One environment-strip policy module, two named sets that differ on purpose.
//
// The enforcement set (STRIP_EXACT + shouldStrip) is what a trusted spawner
// deletes from a child's environment before spawn: preload, loader and
// package-manager inputs a JavaScript launcher cannot undo once Node has started.
// The diagnostic set (STRIPPED_VARIABLE_NAMES/_PREFIXES + isStrippedVariable) is
// what the installed doctor refuses to see and reports as environment-injected.
//
// Both share the DYLD_ prefix and the GIT_-except-GIT_TERMINAL_PROMPT rule, and
// the enforcement exact names are a superset of the diagnostic exact names.
// Beyond that shared core the two diverge:
//   - The enforcement set additionally strips these exact names, which the
//     diagnostic set does not cover at all: NODE_PRESERVE_SYMLINKS_MAIN,
//     OPENSSL_CONF_INCLUDE, OPENSSL_MODULES, OPENSSL_ENGINES, PYTHONPATH,
//     PYTHONSTARTUP, PERL5OPT, BASH_ENV, ENV, PROMPT_COMMAND.
//   - The enforcement set strips LD_PRELOAD, LD_LIBRARY_PATH and LD_AUDIT as
//     exact names only, whereas the diagnostic set strips every LD_ name through
//     the LD_ prefix; so a name such as LD_FOO is stripped by the diagnostic set
//     but not by the enforcement set.
//   - The diagnostic set additionally treats NPM_CONFIG_ as a prefix and matches
//     npm_config_ case-insensitively; the enforcement set strips no npm config.
//
// Merging the two into a single set is a deliberate future decision, not an
// oversight; the exact-set test pins both so a merge cannot happen silently.
// Preload, loader and package-manager environment inputs a JavaScript launcher
// cannot undo once Node has started, so a trusted spawner strips them from a
// child's environment before it runs.
export const STRIP_EXACT = new Set([
    'NODE_OPTIONS', 'NODE_PATH', 'NODE_REPL_EXTERNAL_MODULE', 'NODE_EXTRA_CA_CERTS',
    'NODE_PRESERVE_SYMLINKS_MAIN', 'NODE_TLS_REJECT_UNAUTHORIZED',
    'OPENSSL_CONF', 'OPENSSL_CONF_INCLUDE', 'OPENSSL_MODULES', 'OPENSSL_ENGINES',
    'LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT',
    'PYTHONPATH', 'PYTHONSTARTUP', 'PERL5OPT', 'BASH_ENV', 'ENV', 'PROMPT_COMMAND',
]);
export function shouldStrip(name) {
    if (STRIP_EXACT.has(name))
        return true;
    if (name.startsWith('DYLD_'))
        return true;
    if (name.startsWith('GIT_') && name !== 'GIT_TERMINAL_PROMPT')
        return true;
    return false;
}
// Environment names doctor refuses to see, giving `environment-injected` (item
// 10, C1). The exact names below, plus these prefix families: DYLD_, LD_ and
// NPM_CONFIG_; npm_config is matched case-insensitively so it also catches
// NPM_CONFIG_ and mixed case; and any GIT_ name except GIT_TERMINAL_PROMPT.
export const STRIPPED_VARIABLE_NAMES = [
    'NODE_OPTIONS',
    'NODE_PATH',
    'NODE_REPL_EXTERNAL_MODULE',
    'NODE_EXTRA_CA_CERTS',
    'NODE_TLS_REJECT_UNAUTHORIZED',
    'OPENSSL_CONF',
];
export const STRIPPED_VARIABLE_PREFIXES = ['DYLD_', 'LD_', 'NPM_CONFIG_'];
export function isStrippedVariable(name) {
    if (STRIPPED_VARIABLE_NAMES.includes(name))
        return true;
    if (name.toLowerCase().startsWith('npm_config_'))
        return true;
    if (STRIPPED_VARIABLE_PREFIXES.some(prefix => name.startsWith(prefix)))
        return true;
    return name.startsWith('GIT_') && name !== 'GIT_TERMINAL_PROMPT';
}
//# sourceMappingURL=env-policy.js.map