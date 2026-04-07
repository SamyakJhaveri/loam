# Retrospective

Living retrospective across milestones. Updated at each milestone completion.

---

## Milestone: v1.0 — SC26 Paper Completion Sprint

**Shipped:** 2026-04-06
**Phases:** 13 active (2 dropped, 1 research-only stub) | **Plans:** 33

### What Was Built
- Data verification pipeline with provenance-tracked `% src:` comments in paper.tex
- benchmark_characterization.py: 6-metric analysis for 35 kernels across 5 suites
- augmentation_analysis.py: per-kernel x per-level matrix, heatmap, trend figures
- quantitative_findings.py: 14-dimension analysis with Wilson CIs, McNemar, Cochran-Armitage
- generate_paper_figures.py: 13 publication-quality PDFs from 1,248-task dataset
- cross_consistency_audit.py: automated paper.tex number verification
- ARTIFACT_EVALUATION.md: SC26 reproducibility documentation
- 5 VERIFICATION.md files with 21 Observable Truths

### What Worked
- **Provenance tracking**: `% src:` comments in paper.tex made number verification trivial and caught stale values quickly
- **Phased pipeline**: verification → characterization → analysis → figures → integration prevented propagating stale data
- **Dual-scope decision**: Rodinia 480 primary + 710 all-suite gave both backward compatibility and completeness
- **Phase dropping**: Killing Phases 6 and 10 early saved 2+ days without losing anything
- **Simulated peer review**: The SC26 review simulation (Phase 12.1) caught 5 factual errors before submission
- **Milestone audit**: Caught 13 orphaned requirements and 4 missing VERIFICATIONs — Phase 14 closed all gaps

### What Was Inefficient
- **VERIFICATION.md backfill**: Creating verifications retroactively (Phase 14) was more work than doing them inline during execution. Should verify as part of each phase completion.
- **Stale values in paper.tex**: Phase 12 existed entirely to fix numbers that drifted when the dataset expanded from 480 to 710 tasks. A single-source-of-truth LaTeX macro system would have prevented this.
- **Phase 10 over-engineering**: Planning a separate "qualitative narrative" phase was premature — the narrative writes directly from quantitative data. Phase 10 was dropped after 0 work.
- **Sequential figure wiring**: Figures were generated (Phase 8) but not wired into paper.tex until Phase 13 — 2 days later. Could have been one phase.

### Patterns Established
- `% src:` provenance comments in LaTeX for every data claim
- 3-source cross-reference for requirements (VERIFICATION.md + SUMMARY.md + REQUIREMENTS.md)
- Milestone audit before completion to catch gaps
- Nyquist validation (automated test coverage) per phase
- Dual-scope analysis (subset for backward compat + full for completeness)

### Key Lessons
1. **Verify inline, not retroactively** — creating VERIFICATION.md during execution is cheaper than backfilling
2. **Wire artifacts immediately** — don't generate figures in one phase and wire them 2 phases later
3. **LaTeX macros > hardcoded numbers** — a `\newcommand{\totalTasks}{710}` system would eliminate an entire phase category
4. **Simulated peer review pays for itself** — the 5 factual catches in Phase 12.1 would have been embarrassing reviewer findings
5. **Drop early, drop often** — both dropped phases were correct decisions that freed time for higher-value work

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 13 active (2 dropped, 1 research stub) |
| Plans | 33 |
| Requirements | 39/39 |
| Days | 4 |
| Commits | 213 |
| Files changed | 350 |
| Tech debt items | 9 |
| Dropped phases | 2 |
