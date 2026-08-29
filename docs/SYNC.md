# Sync model

Since the 2026-08 rebuild there are exactly two distribution mechanisms.

## Forward: Copier (template -> projects)

- `uvx copier copy --trust gh:samyakjhaveri/loam ./my-project` bootstraps.
- `uvx copier update --trust` pulls template updates into an existing project.
- Copier resolves git TAGS, not HEAD. Nothing ships until `bin/release.sh <version>` tags it.

## Reverse: the plugin marketplace (improvements -> other projects)

There is no file-sync engine anymore (agent-sync, template-sync, and hub-ci were retired 2026-08-29; the last implementation is readable at git tag history before commit feee2e4).
An asset proven in one project is promoted by hand into `cultivation/marketplace/sam-cc-setup/` (or a bundle) and reaches every other project as a plugin update.
That gives versioned releases and in-place updates without custom machinery.
