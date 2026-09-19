# NATIVE-05 handoff: curated catalog (ASSET-01)

Status: implementation branch `native-05-catalog-impl`, started from `e4c6f474094340dd9829740d9004a0a36e1c121b` and integrated onto main `750a43a88481e73897f41eefcd81292d2213add4` (CORE-04 merged). This document describes the candidate on the branch. Review, both-host qualification and pull-request outcomes are recorded in external receipts under the operator evidence root, not here.

## Goal and why

Ticket [NATIVE-05 #117](https://github.com/SamyakJhaveri/loam/issues/117) delivers the conservation catalog described in `seed/docs/factory/ASSETS.md`. It delivers nothing itself: no body moves, no wrapper files, no activation, no installs.

## What changed on the branch

- `seed/.loam/factory/assets/curated-catalog.json` and `curated-catalog.schema.json`: the shipped data and its schema.
- `seed/.loam/factory/src/assets/obligations.ts`: compiled constants generated from the frozen, independently reviewed obligation table. The validator compares the catalog against these; the catalog cannot override them.
- `seed/.loam/factory/src/assets/catalog.ts`, `schema.ts`, `units.ts`: validator, bounded JSON Schema subset, source-unit span algorithm.
- `seed/.loam/factory/tests/assets/catalog.test.ts`: the five fixed `curated-catalog` cases (`CATALOG_CASES` in `src/testing/verify.ts`).
- `bin/factory-catalog-provenance.mjs` and `bin/tests/factory-catalog-provenance.test.mjs`: the Loam-only source provenance gate (`PROVENANCE_CASES`), run by `bin/check` after platform qualification.
- `seed/.loam/factory/launcher.mjs`: `qualify catalog`. `src/installation/package.ts`: catalog and schema are required payload files. `src/testing/verify.ts` and `tests/installation/package.test.ts`: the two populations registered; full recipient groups stay unavailable.
- `bin/tests/factory-release-render.test.mjs`: private session history (`.claude/codex-reviews`) is excluded before any inspection when the render snapshot is acquired, with a synthetic no-access control inside the existing `render.private-exclusions` case.
- Docs: `seed/docs/factory/ASSETS.md` (new), `docs/ASSET-LAYERS.md`, `seed/docs/factory/SETUP.md`, `CONTRIBUTING.md`.

## Constraints

- Statuses: see `seed/docs/factory/ASSETS.md`, "Pending versus available". Every actual method stays pending and nothing is activated.
- The five private session records are metadata-only, as ASSETS.md describes. No check reads their bodies; the render fixture and the provenance fixture both prove that with an access boundary that throws.
- The obligation table was frozen outside the repository and reviewed independently before catalog data was generated. Changing an obligation needs source evidence and renewed review.

## Done check per task

| Task | Check |
| --- | --- |
| Recipient catalog qualification | `node .loam/factory/launcher.mjs qualify catalog` reports the five `catalog.*` cases passed, none skipped |
| Package qualification | `node .loam/factory/launcher.mjs qualify package` reports the fourteen `package.*` cases passed |
| Source provenance (Loam only) | `node bin/factory-catalog-provenance.mjs` reports the three `provenance.*` cases passed |
| Full check | `bin/check` prints `check: PASSED` on an isolated clone of the candidate |
| Both hosts | the evidence root's `NATIVE-05/qualify-host-native05.py` reports `passed` on the Mac (plain Terminal) and on the Linux host for the same commit and tree |

## Session conduct

The catalog is a record, not permission. A later ticket that adapts a method must keep every mapped source unit or record an explicit exclusion, and must not promote a pending status by editing catalog data; the compiled obligations refuse that. Read `seed/docs/factory/ASSETS.md` before touching any entry.

## Next owners

NATIVE-06, NATIVE-07, NATIVE-08 and NATIVE-12 own the pending targets. Each owner reads its entries and targets from the catalog, implements the adaptation in its own fresh worktree from refreshed main, and extends the obligations through the same review path.
