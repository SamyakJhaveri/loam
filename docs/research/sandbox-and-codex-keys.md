# Sandbox keys and Codex network key, from the docs

Resolves SamyakJhaveri/loam#20.
Researched 2026-09-06 against primary sources only: Claude Code docs at `https://code.claude.com/docs` (`settings-reference.md`, `sandboxing.md`, `permissions.md`, `permission-modes.md`) and Codex docs at `https://developers.openai.com/codex/*` and `https://learn.chatgpt.com/docs/*` (`config-reference.md`, `exec-policy.md`, `permissions.md`), all fetched as raw Markdown.
The `openai/codex` repo's own `docs/config.md`, `docs/sandbox.md`, and `docs/execpolicy.md` at commit `52e12e0c` are three-line stubs redirecting to the hosted docs.
Installed on this machine: Claude Code 2.1.258, Codex 0.153.4.
Line numbers below refer to the raw Markdown as fetched on 2026-09-06.

## What DESIGN.md L0 assumes that the docs do not support

Five items, most severe first.

**1. `Write(.env*)` is a rule Claude Code never consults.**
DESIGN L0 lists `"Read(.env*)", "Edit(.env*)", "Write(.env*)"` in `permissions.deny`.
Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules only, accepts a `Write(path)` rule, never consults it, and warns at startup about it (`permissions.md` line 319, v2.1.210 or later).
The `Read` and `Edit` entries already cover the case, and a `Read` deny rule additionally blocks Edit on the same path on v2.1.208 or later and Write on v2.1.228 or later.
Repair: drop `"Write(.env*)"`.

**2. The sandbox `denyWrite` wildcard entries have no effect on Linux and WSL2.**
DESIGN L0 sets `"filesystem": { "denyRead": [".env", ".env.*"], "denyWrite": [".env", ".env.*"] }`.
On Linux and WSL2 the sandbox mounts concrete paths, so Claude Code skips any `allowWrite` or `denyWrite` entry containing `*`, `?`, or `[` once a trailing `/**` is removed (`settings-reference.md` line 1776).
So `".env.*"` in `denyWrite` is a no-op on Linux and WSL2 while working on macOS.
`denyRead` is fine, because read-list wildcards work on every platform and are expanded to concrete paths on Linux.
A wildcard `Edit` rule inherits the same limitation, because `Edit` allow and deny rules merge into `allowWrite` and `denyWrite` (`settings-reference.md` line 1758, `permissions.md` line 578).
Repair: either accept the platform split and say so in HARNESS.md, or enumerate concrete `.env` filenames in `denyWrite`.

**3. Codex `network.enabled = true` alone enforces nothing.**
DESIGN L0 says the rendered `config.toml` has "network enabled".
`permissions.<name>.network.enabled = true` permits command network access but does not start the network proxy, and without an active proxy the profile's domain rules do not restrict direct network access.
Repair: if the intent is only to let commands reach the network, `enabled = true` is correct and no domain table is needed.
If the intent is a domain policy, the rendered `config.toml` must also set `features.network_proxy = true` and a `[permissions.<name>.network.domains]` table.

**4. The design has no Claude Code network allowlist, and in bypass mode the default would not bind anyway.**
The key exists: `sandbox.network.allowedDomains`.
DESIGN L0 does not use it, which is a deliberate scope choice rather than an error.
The trap is that adding one later without `sandbox.network.strictAllowlist = true` buys nothing for Loam's unattended sessions: with `strictAllowlist` at its `false` default, Claude Code decides a host outside the allowlist by permission mode, running the classifier in auto mode, denying in `dontAsk`, and allowing in `bypassPermissions`.
DESIGN L0 says the implementing session runs in `bypassPermissions`.

**5. The design has no `sandbox.failIfUnavailable`, so an unsupported host degrades silently.**
DESIGN L0 says "If a key is unsupported on the host, HARNESS.md says so and the deny list is the only guard".
The documented failure is quieter than that: when the sandbox cannot start, Claude Code shows a warning and runs commands unsandboxed, and only `sandbox.failIfUnavailable: true` turns that into a startup error.
Repair: decide explicitly whether a rendered project should fail closed, and if so set `"failIfUnavailable": true`.

Two DESIGN claims the docs confirm, recorded so S3 does not re-derive them.

DESIGN line 20 is exactly right.
Deny rules block in every permission mode including `bypassPermissions`, and allow rules have no effect there (`permission-modes.md` line 30).
Deny rules for `Read` and `Edit` reach only Claude's built-in file tools, the file commands Claude Code recognizes in Bash such as `cat`, `head`, `tail`, and `sed`, and Bash redirection targets, not an arbitrary subprocess that opens the file itself (`permissions.md` line 322, `settings-reference.md` line 1445).

DESIGN line 25 is right on every clause.
`forbidden` beats `prompt` beats `allow`, Codex splits safe command chains before applying rules, project rules bind only in trusted projects, prefix rules match token lists so `--force` does not match `--force-with-lease`, and a legacy `sandbox_mode` key disables named permission profiles.

One syntax note that is correct but narrow.
DESIGN L0 writes deny rules such as `Bash(rm -rf:*)`.
The `:*` suffix is equivalent to a trailing wildcard, so the rule matches `rm -rf` and `rm -rf /tmp` but not `rm -rfv /tmp`, since `rfv` is a different token (`permissions.md` lines 182-186).
DESIGN already accepts prefix-dodging as a stated risk.

## Key table

Scope is the docs' term for which settings files may set the key.
Source lines are in `settings-reference.md` unless noted.

| Key | Type | Default | Scope | Source line |
|-----|------|---------|-------|-------------|
| `sandbox.enabled` | Boolean | `false` | Any file | 1625 |
| `sandbox.failIfUnavailable` | Boolean | `false` | Any file | 1645 |
| `sandbox.autoAllowBashIfSandboxed` | Boolean | `true` | Any file | 1668 |
| `sandbox.excludedCommands` | array of command patterns | unset | Any file | 1691 |
| `sandbox.allowUnsandboxedCommands` | Boolean | `true` | Any file | 1709 |
| `sandbox.filesystem.allowWrite` | array of paths | unset | Any file | 1780 |
| `sandbox.filesystem.denyWrite` | array of paths | unset | Any file | 1802 |
| `sandbox.filesystem.denyRead` | array of paths | unset | Any file | 1824 |
| `sandbox.filesystem.allowRead` | array of paths | unset | Any file | 1844 |
| `sandbox.filesystem.disabled` | Boolean | `false` | User or managed | 1893, v2.1.216+ |
| `sandbox.credentials.files` / `.envVars` | array of `{path or name, mode}` with mode `deny` or `mask` | unset | Any file | 2091, 2164, v2.1.187+ |
| `sandbox.network.allowedDomains` | array of domain, wildcard, or IP-literal strings, optional `:port` | unset | Any file, or managed only under `allowManagedDomainsOnly` | 2420 |
| `sandbox.network.deniedDomains` | array, same syntax; deny wins over allow | unset | Any file | 2442 |
| `sandbox.network.strictAllowlist` | Boolean | `false` | User or managed | 2462, v2.1.219+ |
| `permissions.<name>.network.enabled` (Codex) | boolean | `false` | profile table | `config-reference.md` 1531-1665 |
| `permissions.<name>.network.domains."<pattern>"` (Codex) | `allow` or `deny`; `*.example.com`, `**.example.com`, `*` allow-only | none | profile table | same |
| `permissions.<name>.filesystem.glob_scan_max_depth` (Codex) | number, at least 1 | none | profile table | same |

Sandbox path prefixes (line 1766): `/` is absolute, `~/` is home, `./` or bare is relative to the project root for project settings or `~/.claude` for user settings, and a trailing `/` or `/**` is stripped.
The sandbox runs on macOS (Seatbelt), Linux, and WSL2 (needs `bubblewrap` and `socat`, `sandboxing.md` lines 17-19), not native Windows.
Two things still prompt in `bypassPermissions` (`permission-modes.md` lines 509-521): the `isolatePeerMachines` cross-session approval, and reads outside the working directories while `permissions.blockReadsOutsideWorkingDirectories` is on (v2.1.257+).

## Codex syntax S3 needs

A profile extends a built-in by quoting its name; it cannot extend `:danger-full-access`, and extending `:workspace` keeps the workspace root's `.codex` directory read-only unless overridden.
Built-in names are `:read-only`, `:workspace`, `:danger-full-access`.
The Permissions guide's worked example, with the `.env` deny glob under the `":workspace_roots"` sub-table:

```toml
default_permissions = "project-edit"

[features]
network_proxy = true

[permissions.project-edit]
description = "Project editing with OpenAI API access."
extends = ":workspace"

[permissions.project-edit.filesystem]
glob_scan_max_depth = 3

[permissions.project-edit.filesystem.":workspace_roots"]
"**/*.env" = "deny"

[permissions.project-edit.network]
enabled = true

[permissions.project-edit.network.domains]
"api.openai.com" = "allow"
```

`deny` denies reads and wins over equally specific `write` or `read` entries.
On Linux, WSL, and native Windows an unbounded `**` deny-read pattern may need bounded pre-expansion, which `glob_scan_max_depth` controls; the alternative is enumerating `*.env`, `*/*.env`, `*/*/*.env`.

Permission profiles do not compose with the older sandbox settings.
A `sandbox_mode` key in any loaded config file, a `--sandbox` flag, or a config profile setting `sandbox_mode` makes Codex use the older settings instead of `default_permissions` (`learn.chatgpt.com/docs/permissions` opening note, `config-reference.md` line 1534).
The one exception is managed `allowed_permission_profiles`, which needs Codex 0.138.0 or later.

Rules files are Starlark under `rules/` next to an active config layer, for example `~/.codex/rules/default.rules`; project-local `<repo>/.codex/rules/` loads only when the project layer is trusted, and Codex must be restarted after a change.
Rules are documented as experimental.

```python
prefix_rule(
    pattern = ["git", "push", "--force"],
    decision = "forbidden",
    justification = "Use `git push` without force.",
)
```

`pattern` is an exact token prefix, so `["git", "push", "--force"]` does not cover `git push --force-with-lease`.
When more than one rule matches, the most restrictive decision wins.
`bash -lc` scripts that are linear chains joined by `&&`, `||`, `;`, or `|` are split with tree-sitter and each command evaluated; scripts with redirection, substitutions, assignments, wildcards, or control flow are evaluated as the single invocation `["bash", "-lc", "<full script>"]`.

The probe, confirmed present on 0.153.4 via `codex execpolicy check --help`:

```shell
codex execpolicy check --pretty \
  --rules ~/.codex/rules/default.rules \
  -- gh pr view 7888 --json title,body,comments
```

`--rules` is repeatable, and the output is JSON with the strictest decision and any matching rules.
