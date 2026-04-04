# Phase 2: Benchmark Characterization Data - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 02-benchmark-characterization-data
**Areas discussed:** Output organization, Multi-file classification, Language feature taxonomy, SLoC scope & presentation, Category distribution presentation, API coverage cross-tab, SLoC validation strategy

---

## Output Organization

| Option | Description | Selected |
|--------|-------------|----------|
| A) Separate files per metric | One JSON+MD per metric (category_distribution.json, api_coverage.json, etc.) — follows existing pattern | |
| B) Single combined characterization file | All metrics in one `benchmark_characterization.json` + `.md` — easier for Phase 5 to consume | ✓ |
| C) Both — separate files + combined summary | Separate files as source of truth + lightweight summary for convenience | |

**User's choice:** B) Single combined characterization file
**Notes:** User preferred simplicity of one file, one read for downstream phases.

---

## Multi-file Classification

| Option | Description | Selected |
|--------|-------------|----------|
| A) Based on `translation_targets` | Multi-file = LLM must produce multiple output files. Stronger claim for paper. | |
| B) Based on `prompt_payload` | Multi-file = LLM sees multiple input files. Broader definition. | |
| C) Report both | Both file counts reported; headline uses `translation_targets > 1` | ✓ |

**User's choice:** C) Report both
**Notes:** Headline "multi-file" number uses translation_targets > 1, with input file counts alongside for full context.

---

## Language Feature Taxonomy

| Option | Description | Selected |
|--------|-------------|----------|
| A) API version tier classification | One tier label per kernel (e.g., "CUDA basic", "OpenMP 4.5"). Compact. | |
| B) Feature presence checklist | ~15-20 specific features marked present/absent per kernel. Rich but potentially too detailed. | |
| C) Hybrid — tier + features | Tier for the table, full feature list in JSON for supplementary. Best of both. | ✓ |

**User's choice:** C) Hybrid — tier classification + notable features
**Notes:** Tier goes in characterization table column; raw feature data stays in JSON.

---

## SLoC Scope & Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| A) Source SLoC only | One CUDA SLoC number per kernel. Standard approach. | |
| B) Source + Target SLoC | Both CUDA and OMP SLoC in table. Shows asymmetry but more columns. | |
| C) Source SLoC in table + ratio in prose | Source in table, OMP/CUDA ratio as aggregate stat in text. Compact + insightful. | ✓ |

**User's choice:** C) Source SLoC in table + ratio as derived metric
**Notes:** Keeps table compact. Translation ratio (median, range) reported in prose to surface asymmetry insight.

---

## Category Distribution Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| A) Simple count | Category -> kernel count + percentage. Compact. | |
| B) Category x Suite breakdown | Full cross-tab showing which suites contribute to which categories. | |
| C) Category count + suite annotation | Counts with per-suite breakdown. e.g., `stencil: 5 (rodinia: 3, hecbench: 2)` | ✓ |

**User's choice:** C) Category count + suite annotation
**Notes:** Supports both breadth argument and suite complementarity narrative without a full cross-tab.

---

## API Coverage Cross-tab

### Cell contents

| Option | Description | Selected |
|--------|-------------|----------|
| A) Kernel count | Distinct kernels with a spec for that API in each suite | ✓ |
| B) Spec count | Total spec files (could double-count omp + omp_target) | |
| C) Both | Kernel count in table, spec count in footnote | |

### OMP Target handling

| Option | Description | Selected |
|--------|-------------|----------|
| X) Separate column | 4 API columns: CUDA, OMP, OpenCL, OMP Target | ✓ |
| Y) Merged with OMP | 3 columns, omp_target counted under OMP | |
| Z) Footnote approach | 3 main columns + footnote for omp_target | |

**User's choice:** A) Kernel count + X) Separate column
**Notes:** Full picture with 4 API columns, even though omp_target excluded from standard eval batches.

---

## SLoC Validation Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| A) Re-run and validate only | Run script fresh, diff against existing output, confirm 35 kernels | |
| B) Trust existing output | Skip re-running, assume sloc_analysis.json is current | |
| C) Re-run, validate, and fold into combined JSON | Fresh run + integrate into benchmark_characterization.json | ✓ |

**User's choice:** C) Re-run, validate, and fold into combined characterization JSON
**Notes:** Existing sloc_analysis.json remains on disk; combined characterization file becomes canonical source for Phase 5.

---

## Claude's Discretion

- Script architecture (new standalone vs extend existing)
- JSON schema structure within benchmark_characterization.json
- Specific grep regex patterns for language features
- Ordering of metrics within combined file
- Handling of kernels with missing source directories

## Deferred Ideas

None — discussion stayed within phase scope.
