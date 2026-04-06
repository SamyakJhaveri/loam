# Phase 14: Verification Backfill & Housekeeping - Context

**Gathered:** 2026-04-06 (updated — original 2026-04-05)
**Status:** Ready for planning

<domain>
## Phase Boundary

Close all 13 orphaned requirements identified by the v1.0 milestone audit by creating formal VERIFICATION.md files for Phases 3, 4, 5, 8, and 12. Update REQUIREMENTS.md checkboxes and traceability for the 8 remaining unchecked requirements (AUG-01-04, METHOD-01-04). Refresh ROADMAP.md progress table. Add SC26 artifact evaluation README with setup + smoke test instructions. This is gap closure — no new features, no new analysis.

</domain>

<decisions>
## Implementation Decisions

### Verification Depth
- **D-01:** Full Phase 1-style VERIFICATION.md for all 5 phases — Observable Truths table, Required Artifacts, Key Link Verification. Same template and rigor as `.planning/phases/01-data-verification-ground-truth/01-VERIFICATION.md`.
- **D-02:** All verification evidence MUST come from live on-disk data — actual result JSONs in `results/`, spec files in `specs/`, `paper.tex`, and analysis outputs in `results/analysis/`. NEVER trust old VERIFICATION.md, SUMMARY files, VALIDATION files, or stale planning docs for numerical claims. Data may have been updated since those files were written.
- **D-03:** Phase 14 owns gap closure end-to-end. If verification discovers a required artifact doesn't exist on disk, create it during verification from existing data. No requirement gets marked FAILED due to missing artifacts that can be produced.
- **D-04:** Observable Truths derived from REQUIREMENTS.md criteria — requirement IDs (AUG-01, METHOD-01, INTRO-01, etc.) are the primary anchor for each truth row.
- **D-05:** Paper.tex claim verification uses grep + compare approach — extract actual numbers from `paper.tex` and verify each against the live data source file. Same rigor as Phase 1's `% src:` comment methodology.
- **D-06:** Figure verification: re-run `scripts/generate_paper_figures.py` and confirm it completes without errors, producing all expected PDF files in `docs/paper/figures/`. This ensures figures reflect current data.

### Artifact Evaluation README
- **D-07:** Artifact evaluation README at repo root: `ARTIFACT_EVALUATION.md` (standard SC convention).
- **D-08:** Scope: setup + smoke test only (~1 page). Contents: clone, submodule init, `pip install -r requirements-lock.txt`, `config/paths.json` setup, one smoke test command (`python3 -m harness verify specs/rodinia-bfs-cuda.json`).

### API Environment Variable Documentation
- **D-09:** API env var docs go as a section within `ARTIFACT_EVALUATION.md` — single source for reviewers.
- **D-10:** Only `TOGETHER_API_KEY` documented (the only key needed to reproduce the paper's Qwen 3.5 397B results via Together AI). No need to document other provider keys.

### Execution Ordering
- **D-11:** Single plan, dependency-ordered: (1) verify Phases 3/4/5 (create missing artifacts along the way), (2) verify Phases 8/12, (3) update REQUIREMENTS.md checkboxes + traceability based on verification results, (4) update ROADMAP.md progress table, (5) create ARTIFACT_EVALUATION.md.
- **D-12:** If verification discovers paper.tex claims that don't match live data, fix them in place. Phase 14 owns full gap closure — no separate fix phase.

### Claude's Discretion
- Exact formatting of Observable Truths tables within each VERIFICATION.md
- How to organize the dependency order within verifying each phase (e.g., AUG-01 before AUG-02)
- How to structure the ARTIFACT_EVALUATION.md sections (standard README conventions)
- Whether to commit each VERIFICATION.md individually or batch

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Success Criteria
- `.planning/REQUIREMENTS.md` — Requirement IDs (AUG-01-04, METHOD-01-04, INTRO-01-04, CHAR-07, VERIFY-01), success criteria text, current checkbox state, traceability table
- `.planning/ROADMAP.md` — Phase 14 success criteria (11 items), phase dependencies, progress table

### Verification Template
- `.planning/phases/01-data-verification-ground-truth/01-VERIFICATION.md` — Full template pattern: YAML frontmatter, Observable Truths table, Required Artifacts, Key Link Verification

### Phase Completion Evidence (SUMMARY files — read but verify numbers against live data)
- `.planning/phases/03-augmentation-analysis-story/03-01-SUMMARY.md` — Phase 3 plan 1 execution results
- `.planning/phases/03-augmentation-analysis-story/03-02-SUMMARY.md` — Phase 3 plan 2 execution results
- `.planning/phases/03-augmentation-analysis-story/03-03-SUMMARY.md` — Phase 3 plan 3 execution results
- `.planning/phases/04-methodology-reviewer-defense/04-01-SUMMARY.md` — Phase 4 plan 1 execution results
- `.planning/phases/04-methodology-reviewer-defense/04-02-SUMMARY.md` — Phase 4 plan 2 execution results
- `.planning/phases/05-introduction-positioning-characterization-table/05-01-SUMMARY.md` — Phase 5 plan 1 execution results
- `.planning/phases/05-introduction-positioning-characterization-table/05-02-SUMMARY.md` — Phase 5 plan 2 execution results
- `.planning/phases/08-figure-regeneration/08-01-SUMMARY.md` — Phase 8 plan 1 execution results
- `.planning/phases/08-figure-regeneration/08-02-SUMMARY.md` — Phase 8 plan 2 execution results
- `.planning/phases/12-fix-stale-passk-values/12-01-SUMMARY.md` — Phase 12 plan 1 execution results
- `.planning/phases/12-fix-stale-passk-values/12-02-SUMMARY.md` — Phase 12 plan 2 execution results
- `.planning/phases/12-fix-stale-passk-values/12-03-SUMMARY.md` — Phase 12 plan 3 execution results

### Live Data Sources (authoritative — verify against these, not SUMMARY files)
- `results/analysis/paper_data.json` — Aggregate pass rates, direction rates, self-repair, pass@k
- `results/analysis/statistical_analysis.json` — Cochran-Armitage, McNemar, Wilson CIs
- `results/analysis/selfrepair_analysis.json` — Self-repair rates, transitions, per-suite
- `results/analysis/error_taxonomy.json` — Failure type distribution
- `results/analysis/token_analysis.json` — Token cost analysis
- `docs/paper/latex/paper.tex` — All paper claims to verify
- `c_augmentation/augment_dataset.py` — LEVEL_FRACTIONS (augmentation level definitions source of truth)
- `scripts/generate_paper_figures.py` — Figure generation script (re-run for D-06)
- `specs/` — All 96 spec JSON files (source of truth for counts)
- `manifest.jsonl` — Kernel registry (source of truth for categories, API coverage)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `01-VERIFICATION.md` template pattern with YAML frontmatter, Observable Truths, Required Artifacts, Key Link Verification sections
- 4 existing VERIFICATION.md files (Phases 1, 2, 7, 9) as consistency references
- `scripts/generate_paper_figures.py` for figure regeneration verification
- `scripts/analysis/generate_paper_data.py` with `--suite` filter for scoped analysis

### Established Patterns
- VERIFICATION.md uses YAML frontmatter: `phase`, `verified`, `status`, `score`, `gaps`
- Observable Truths table: `# | Truth | Status | Evidence`
- Status values: VERIFIED, PARTIAL, NOT WIRED
- `% src:` comments in paper.tex trace claims to data files

### Integration Points
- REQUIREMENTS.md traceability table links requirement IDs to phases and completion status
- ROADMAP.md progress table tracks phase/plan completion counts
- 13 paper figure PDFs in `docs/paper/figures/` generated by `scripts/generate_paper_figures.py`

</code_context>

<specifics>
## Specific Ideas

- User emphasized: data may have been updated since old verification/summary files were written — always ground evidence in live data from `results/` and `specs/`, never from stale planning docs
- TOGETHER_API_KEY is the only API key needed for reproducing paper results (Qwen via Together AI)
- Artifact eval README should be minimal (~1 page) for SC26 reviewers

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 14-verification-backfill-housekeeping*
*Context gathered: 2026-04-06*
