# Phase 8: Figure Regeneration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 08-figure-regeneration
**Areas discussed:** Model lineup, Suite coverage, Data source routing, Architecture diagram

---

## Model Lineup

| Option | Description | Selected |
|--------|-------------|----------|
| Qwen-only figures | Redesign all multi-model figures for Qwen only. GPT-4.1 mini added in camera-ready. | |
| Qwen + GPT-4.1 mini placeholders | Keep 2-model layout with gray/hatched N/A placeholder cells for GPT-4.1 mini. | ✓ |
| Qwen + hardcoded fallback data | Keep existing hardcoded fallback values from old models. | |

**User's choice:** Qwen + GPT-4.1 mini placeholders
**Notes:** Makes the 2-model intent visible to reviewers while being honest about pending data.

### Placeholder Appearance

| Option | Description | Selected |
|--------|-------------|----------|
| Gray/hatched 'N/A' cells | Gray fill with hatching and 'pending' or 'N/A' labels. | ✓ |
| Omit GPT, add footnote | Only show Qwen data, add caption note about pending GPT data. | |
| Empty column with label | Reserve visual space with just the model name label. | |

**User's choice:** Gray/hatched 'N/A' cells

### Old Model References

| Option | Description | Selected |
|--------|-------------|----------|
| Remove completely | Clean delete of all old model dicts (Claude, Gemini, Groq). Git preserves history. | ✓ |
| Comment out | Keep but comment out for quick restoration. | |

**User's choice:** Remove completely

### T2 Model Table

| Option | Description | Selected |
|--------|-------------|----------|
| 2-row with pending | Qwen populated, GPT-4.1 mini with 'pending' values. | ✓ |
| 1-row Qwen only | Only Qwen row. Add GPT when data arrives. | |

**User's choice:** 2-row with pending

---

## Suite Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| All 5 suites (35 kernels) | F3 heatmap shows 35 kernels grouped by suite. F4 covers all suites. Matches paper claims. | ✓ |
| Rodinia primary + supplement | Keep F3/F4 Rodinia-focused. Add separate supplementary cross-suite figure. | |
| Rodinia only | Keep all figures Rodinia-scoped (18 kernels, 480 tasks). | |

**User's choice:** All 5 suites (35 kernels)

### F3 Heatmap Grouping

| Option | Description | Selected |
|--------|-------------|----------|
| Grouped by suite with dividers | Suite sections with horizontal divider lines and suite labels. | ✓ |
| Sorted by pass rate | All 35 kernels sorted by difficulty. No suite grouping. | |
| Alphabetical within suites | A-Z within each suite section. | |

**User's choice:** Grouped by suite with dividers

### F3 Heatmap Dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| 35 kernels × 6 directions | Full grid. Each cell colored by status. | ✓ |
| 35 × 6 × augmentation | Add L0-L4 sub-columns. Very dense. | |
| Split into two figures | F3a: Rodinia (main body). F3b: non-Rodinia (appendix). | |

**User's choice:** 35 kernels × 6 directions

### F6 Redesign

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-suite comparison | Replace XSBench-specific with per-suite aggregate pass rate bars. | ✓ |
| Keep XSBench-specific | Preserve kernel isolation story (ParEval-Repo 0% vs ParBench). | |
| Both: cross-suite + XSBench inset | Main chart cross-suite, small inset for XSBench story. | |

**User's choice:** Cross-suite comparison

---

## Data Source Routing

| Option | Description | Selected |
|--------|-------------|----------|
| Raw result JSONs | Keep load_eval_results() — self-contained, reads 1,248 raw files. | ✓ |
| Analysis JSON files | Refactor to read paper_data.json etc. Faster but adds coupling. | |
| Hybrid | Analysis for aggregates, raw for detail. | |

**User's choice:** Raw result JSONs

### File Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Base L0 only for main figures | F3/F4/F6 use L0 base. F7 uses L0-L4. F5 uses samples. | ✓ |
| All files for all figures | Each function decides. Risk of accidental mixing. | |

**User's choice:** Base L0 only for main figures

### Augmentation Figures

| Option | Description | Selected |
|--------|-------------|----------|
| Leave Phase 3 versions | aug_heatmap and aug_trend already current (April 4). | ✓ |
| Regenerate in unified script | Move into generate_paper_figures.py. Duplicates Phase 3 logic. | |

**User's choice:** Leave Phase 3 versions

### omp_target Inclusion

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude from main figures | Standard 6 directions only. omp_target is case-study data. | ✓ |
| Include as 7th/8th direction | Add to heatmap and bar charts. More complete but complex. | |

**User's choice:** Exclude from main figures

---

## Architecture Diagram

| Option | Description | Selected |
|--------|-------------|----------|
| Manual export | User exports via draw.io desktop/VS Code. Most reliable. | ✓ |
| Automate with drawio CLI | Install drawio-desktop for headless export. | |
| Skip | Check if needed first. | |

**User's choice:** Manual export

### Content Updates

| Option | Description | Selected |
|--------|-------------|----------|
| Export as-is | Trust March 31 version is current. | ✓ |
| Review and update if needed | Flag for manual review during implementation. | |
| Claude decides | Check during implementation. | |

**User's choice:** Export as-is

---

## Claude's Discretion

- Heatmap cell sizing and font scaling for 35-kernel layout
- Gray/hatch styling for GPT-4.1 mini N/A cells
- Suite divider line styling
- F6 cross-suite bar chart layout details
- Matplotlib rendering fixes for expanded layouts

## Deferred Ideas

None — discussion stayed within phase scope.
