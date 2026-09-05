# Sync model

Since the 2026-08 rebuild there are three distribution mechanisms: Copier forward, the plugin marketplace in reverse, and attach mode for an existing directory.

## Forward: Copier (template -> projects)

- `uvx copier copy --trust gh:samyakjhaveri/loam ./my-project` bootstraps.
- `uvx copier update --trust` pulls template updates into an existing project.
- Copier resolves git TAGS, not HEAD. Nothing ships until `bin/release.sh <version>` tags it.

## Reverse: the plugin marketplace (improvements -> other projects)

There is no file-sync engine anymore (agent-sync, template-sync, and hub-ci were retired 2026-08-29; the last implementation is readable at git tag history before commit feee2e4).
An asset proven in one project is promoted by hand into `cultivation/marketplace/sam-cc-setup/` (or a bundle) and reaches every other project as a plugin update.
That gives versioned releases and in-place updates without custom machinery.

## Attach mode: the harness into an existing directory

`bin/loam-attach.sh <dir>` drops the Claude harness into a directory Copier never rendered, without turning it into a Loam project.
It copies `seed/.claude/settings.json` and the `seed/.claude/hooks/` scripts into `<dir>/.claude/`, appends the harness `.gitignore` lines, and writes `<dir>/.claude/settings.local.json` that registers this checkout's `cultivation/marketplace` and enables the `sam-cc-setup` plugin.
It refuses to overwrite an existing `<dir>/.claude/settings.json` unless `--force`, and never overwrites an existing `settings.local.json`.
The marketplace path it writes is this checkout's absolute path, so run it from the canonical checkout rather than a throwaway worktree.
