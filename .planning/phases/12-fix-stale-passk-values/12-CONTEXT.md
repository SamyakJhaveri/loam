# Phase 12: Fix Stale Pass@k Values in Paper.tex - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Update every numerical claim in paper.tex (Abstract, Sections 1, 6, and 7) to match the all-suite ground truth in `results/analysis/paper_data.json`. This phase closes the VERIFY-01 regression by grounding the entire paper in the complete 5-suite, 710-task dataset rather than the Rodinia-only 480-task subset.

</domain>

<decisions>
## Implementation Decisions

### Ground Truth Source
- **D-01:** The single source of truth is `results/analysis/paper_data.json` (all 5 suites: Rodinia, XSBench, RSBench, mixbench, HeCBench). NOT `paper_data_rodinia.json`.
- **D-02:** The paper should present data from all benchmark suites — Rodinia-only scope is rejected. The 710-task primary campaign and all derived statistics come from the all-suite file.

### Verification Scope
- **D-03:** Full audit of ALL numerical claims in Sections 6.1-6.8 and Section 7.1-7.5. Not limited to the 8 originally-identified stale pass@k values.
- **D-04:** Intro/abstract numbers also updated in this phase (from 700 tasks/38.0% to 710 tasks/38.3%), not deferred to Phase 11.

### Source Comment Audit
- **D-05:** All LaTeX provenance comments (`% src: ...`) updated to reference `paper_data.json` with correct field paths. Comments that currently say `paper_data.json` but cite Rodinia-only numbers (480 tasks) are fixed to cite the all-suite numbers (710 tasks).
- **D-06:** Every updated number gets a provenance comment tracing to the exact JSON field and value.

### Section 7 Cross-Check
- **D-07:** Section 7 (Discussion) is included in the same update pass as Section 6. All repeated numbers (direction rates, augmentation stats, pass@k references) are updated to match Section 6's corrected values.

### Key Numerical Changes (from codebase analysis)

**Primary campaign**: 480 → 710 tasks, 174 → 272 PASS, 36.2% → 38.3%

**By direction (all levels)**:
- cuda-to-omp: 65.0% [54.1%, 74.6%] → 64.2% [55.3%, 72.2%]
- omp-to-cuda: 50.0% [39.3%, 60.7%] → 52.5% [43.6%, 61.2%]
- opencl-to-omp: 46.7% [35.8%, 57.8%] → 38.9% [29.5%, 49.2%]
- omp-to-opencl: 29.3% [20.2%, 40.4%] → 27.8% [19.6%, 37.8%]
- cuda-to-opencl: 22.4% [14.8%, 32.3%] → 20.0% [13.3%, 28.9%]
- opencl-to-cuda: 7.1% [3.3%, 14.6%] → 6.0% [2.8%, 12.5%]

**Augmentation Cochran-Armitage**: z=-0.17, p=0.87 (16 kernels) → z=0.0, p=1.0 (24 kernels)

**Self-repair**: first-attempt 17.5% → 22.5%, repair rate 22.7% → 20.4%

**BUILD_FAIL subcategories**: header=55, undeclared_id=56, linker=49, other=55, syntax=14 (total 241)

**pass@k UNCHANGED**: 426 tasks, 142 pairs, 19.7% macro pass@1, 27.5% macro pass@3 (campaign was Rodinia-only)

### Claude's Discretion
- Rounding conventions for percentages (1 decimal place consistent with existing style)
- How to handle the new ERROR status (1 task) in failure taxonomy — likely group with EXTRACTION_FAIL or note separately
- Paragraph rewrites needed when numbers change direction ranking order

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Ground Truth Data
- `results/analysis/paper_data.json` — THE authoritative source for all numerical claims. Contains primary_campaign (710 tasks), passk_campaign (426 tasks), by_direction, augmentation, self_repair, direction_asymmetry, build_fail_subcategories, token_metrics.

### Paper Source
- `docs/paper/latex/paper.tex` — The paper to be updated. Sections 6.1-6.8 (Results), Section 7 (Discussion), Abstract, and Section 1 (Introduction).

### Analysis Scripts (for provenance)
- `scripts/analysis/generate_paper_data.py` — Script that generated paper_data.json. Understanding its field names helps trace provenance comments.

### Verification Reference
- `results/analysis/statistical_analysis.json` — Statistical tests (Cochran-Armitage, McNemar, Wilson CIs)
- `results/analysis/selfrepair_analysis.json` — Self-repair detailed breakdown
- `results/analysis/error_taxonomy.json` — Failure taxonomy with subcategories

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 1 established the provenance comment convention (`% src: paper_data.json > field.path = value`)
- `scripts/analysis/generate_paper_data.py` with `--suite` filter controls scope; running without `--suite` produces the all-suite file

### Established Patterns
- LaTeX provenance comments follow format: `% src: file.json > path.to.field: value`
- Wilson 95% CIs are formatted as `[lower%, upper%]` with 1 decimal place
- Table cells use `N/total (rate%)` format for counts
- `\tbd` macro for pending GPT-4.1 mini values
- `\pending{...}` macro for pending cross-model comparisons

### Integration Points
- All Section 6 tables (`tab:overall-pass`, `tab:direction-rates`, `tab:augmentation-rates`, `tab:pass-at-k`, `tab:stats-summary`) need cell-by-cell updates
- Section 7 prose references these same tables — text must match updated table values
- Abstract and Section 1 aggregate numbers must be consistent with Section 6

</code_context>

<specifics>
## Specific Ideas

- User explicitly rejected Rodinia-only scope: "paper_data.json is the ground truth with data from all benchmarks... we do NOT want to limit our paper to rodinia"
- All 5 benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench) are presented as a unified dataset
- The augmentation null result is STRONGER with all-suite data (z=0.0, p=1.0 vs z=-0.17, p=0.87) — narrative should reflect this

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 12-fix-stale-passk-values*
*Context gathered: 2026-04-05*
