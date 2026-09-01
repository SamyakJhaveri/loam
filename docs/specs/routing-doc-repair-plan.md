# Active Routing Documentation Repair Plan

## Goal

Make every active public, contributor, root-agent, plugin, and release document describe the current Loam tree and commands.

## Authority order

When prose conflicts with implementation, use these sources in order:

1. `bin/verify-template.sh` and `bin/rendered_harness_contract.py`
2. `seed/` and marketplace manifests
3. `docs/SYNC.md`, `docs/COPIER.md`, and `docs/ASSET-LAYERS.md`
4. Historical specifications only for rationale

## Scope and checks

### Public and contributor routes

Update `README.md`, `CONTRIBUTING.md`, `docs/BOOTSTRAP.md`, and `docs/ASSET-LAYERS.md`.

Remove retired flavor, sync-engine, deleted-document, and obsolete count claims. Describe the current rendered Claude and Codex layers without fragile counts where possible.

Check:

<!-- stale-counts: allow - this grep hunts the stale strings; the numbers are the quarry, not claims -->
```bash
rg -n '(template-sync|is_research|Research flavor|renders both flavors|ALL OK|27 core skills|10 hooks|16 rules|6 agents|3 hooks|VISUAL-OVERVIEW|docs/(MEMORY|FLAVORS)\.md|seed/\.claude/(skills|rules)|not skill execution or the enforcement gate|academic-research|licensing--attribution)' README.md CONTRIBUTING.md docs/BOOTSTRAP.md docs/ASSET-LAYERS.md
```

Expected: no output and exit status `1`.

### Root agent routes

Make root `AGENTS.md` the shared Loam guidance. Make root `CLAUDE.md` import it with one `@AGENTS.md` line and retain only Claude-specific material. Remove routes to absent rules, flavors, scripts, diagram skills, and hosted MCP servers.

Remove the obsolete `render-yoshida.py` explanation from `.codex/config.toml`. Do not change `network_access = true` in this documentation-only change.

Checks:

```bash
rg -n '^@AGENTS\.md$' CLAUDE.md
```

Expected: exactly one match.

```bash
rg -n '(\.claude/rules|seed/_research|template-sync|ALL OK|render-yoshida|diagram MCP|Skills, agents, hooks, rules|Codex config \+ execution rules)' AGENTS.md CLAUDE.md .codex/config.toml
```

Expected: no output and exit status `1`.

### Portable Clief provenance

Replace the absolute corpus root in `docs/specs/cliefnotes-wisdom.md` with a statement that the corpus was machine-local during extraction and that lesson paths are relative to the audited corpus.

Check:

```bash
rg -n '/Users/|Corpus root:' docs/specs/cliefnotes-wisdom.md
```

Expected: no output and exit status `1`.

This changes provenance wording only. It must not change claim text, claim identifiers, evidence grades, or source-relative lesson paths.

### Plugin and release routes

Repair current inventory and release-loop prose in `cultivation/marketplace/sam-cc-setup/README.md` and `cultivation/marketplace/UPGRADING.md` without changing plugin behavior or versions. This branch may describe the current pre-consolidation plugin state. The consolidation branch owns the final `sam-superpowers` removal wording.

Remove executable instructions for absent scripts. Route current work to `docs/SYNC.md`, `bin/verify-template.sh`, and `bin/release.sh`.

Check:

```bash
rg -n '(bin/agent-sync\.sh|sync\.sh --prune|/sync-to-hub|bin/hub-ci\.sh|bin/lint-skill-descriptions\.sh|7 of the 12 plugins|VERSION` is `1\.1\.0|sam-cc-setup` is `0\.3\.0|same 14 skills)' cultivation/marketplace/UPGRADING.md cultivation/marketplace/sam-cc-setup/README.md
```

Expected: no output and exit status `1`.

## Final verification

Run `git diff --check`. Then run `bin/verify-template.sh` and require `verify-template: PASSED`.

## Non-goals

- Do not implement Clief Notes claims.
- Do not change seed behavior.
- Do not change plugin versions.
- Do not change concurrent-hook ownership in this branch.
- Do not rewrite historical design and audit records.
