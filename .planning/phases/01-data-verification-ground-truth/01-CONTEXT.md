# Phase 1: Data Verification & Ground Truth - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Cross-check every existing numerical claim, table, data-backed prose statement, and figure in Sections 1-5 of paper.tex against actual data files on disk. Fix discrepancies inline. Regenerate all analysis files and figures at the end so downstream phases start with fresh, verified data.

</domain>

<decisions>
## Implementation Decisions

### Discrepancy resolution
- **D-01:** Fix discrepancies inline in paper.tex immediately during verification — no separate discrepancy report. The git diff serves as the audit trail.
- **D-02:** Add brief LaTeX source comments next to key data-derived numbers noting the source file and field (e.g., `% src: paper_data.json > overall_pass_rate`). Helps future edits stay grounded.
- **D-03:** Fix table structure too (not just data values) when the data clearly demands it (e.g., missing API column, wrong row order). Don't defer structural fixes to downstream phases.

### Verification scope
- **D-04:** Verify explicit numbers, table cells, AND qualitative prose claims backed by data (e.g., "CUDA-to-OMP is the easiest direction" must match direction pass rates). Not just numbers and tables.
- **D-05:** Verify Qwen data in Section 5 (Results) too — Qwen Rodinia data is complete and frozen. GPT-4.1 mini placeholders are out of scope (no data yet).
- **D-06:** Also regenerate figures using generate_paper_figures.py — verify figure output matches current data. Tables + figures + inline numbers + data-backed prose are all in scope.
- **D-07:** Ground truth source is raw result JSONs in `results/evaluation/together-qwen-*/`, NOT derived analysis files (paper_data.json etc.). Raw files are the primary source; derived files may be stale or have aggregation bugs.

### Stale analysis handling
- **D-08:** Verify against raw result JSONs first (primary source of truth). Regenerate all analysis files (paper_data.json, statistical_analysis.json, selfrepair_analysis.json) and figures at the END of Phase 1, so downstream phases have fresh data.
- **D-09:** Full regeneration scope at end: all analysis scripts + figure generation (generate_paper_figures.py). Downstream phases (2-5) start with completely fresh data and figures.
- **D-10:** Data freeze at Phase 1 start. Count result files once at the beginning, verify against that count. New results from running tmux sessions (qwen_hecbench, qwen_small) are out of scope — they get picked up in a future re-run.

### Claude's Discretion
- Verification ordering within sections (top-to-bottom, table-by-table, or claim-by-claim)
- Whether to batch-verify all tables first vs. verify section-by-section
- Exact format of LaTeX source comments (as long as they identify source file + field)
- How to handle GPT-4.1 mini references encountered during verification (skip silently or note for future)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper
- `docs/paper/latex/paper.tex` — The paper being verified. All claims in Sections 1-5 are verification targets.

### Ground truth data (raw)
- `results/evaluation/together-qwen-3.5-397b-a17b/` — Raw per-task result JSONs. Primary source of truth for all Qwen data claims.
- `manifest.jsonl` — Append-only kernel registry. Source of truth for kernel count, spec count, API counts.
- `specs/` — 206 spec JSON files. Source of truth for spec-level details (API, suite, category).

### Derived analysis files (to regenerate at end)
- `results/analysis/paper_data.json` — Consolidated paper data (generated April 1, may be stale)
- `results/analysis/statistical_analysis.json` — Pass rate statistics, confidence intervals, Cochran-Armitage
- `results/analysis/selfrepair_analysis.json` — Self-repair rates by model
- `results/analysis/sloc_analysis.json` — Source lines of code per kernel (currently 18 kernels, needs extension in Phase 2)
- `results/analysis/error_taxonomy.json` — Error taxonomy for paper tables

### Analysis/figure generation scripts
- `scripts/analysis/generate_paper_data.py` — Regenerate paper_data.json
- `scripts/analysis/statistical_analysis.py` — Regenerate statistical_analysis.json
- `scripts/analysis/selfrepair_analysis.py` — Regenerate selfrepair_analysis.json
- `scripts/generate_paper_figures.py` — Regenerate all paper figures

### Code references for table verification
- `c_augmentation/augment_dataset.py` — Contains `LEVEL_FRACTIONS` dictionary. Source of truth for augmentation level definitions table (VERIFY-03).
- `config/compiler_inventory.txt` — Captured compiler versions for hardware table verification (VERIFY-05).

### Requirements
- `.planning/REQUIREMENTS.md` — VERIFY-01 through VERIFY-06 define the specific verification tasks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/generate_paper_data.py`: Consolidates raw results into paper_data.json — use for end-of-phase regeneration
- `scripts/analysis/statistical_analysis.py`: Generates statistical analysis with CIs — use for end-of-phase regeneration
- `scripts/generate_paper_figures.py`: Generates all paper figures — use for end-of-phase figure regeneration
- `scripts/validate_schema.py`: Validates specs against schema — useful for confirming spec count and structure

### Established Patterns
- Analysis scripts all accept `--project-root` flag for path resolution
- Result JSONs use `overall_status` as the authoritative verdict (not `run_status`)
- `manifest.jsonl` is append-only — 5 phantom entries exist for deleted specs (expected)

### Integration Points
- Phase 1 output (verified paper.tex + fresh analysis files) is consumed by all subsequent phases
- Regenerated paper_data.json feeds Phase 2 (characterization), Phase 3 (augmentation), Phase 5 (introduction)
- Regenerated figures feed Phase 5 (introduction) and any figure-referencing text

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for verification ordering and execution.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-verification-ground-truth*
*Context gathered: 2026-04-03*
