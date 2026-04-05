# Phase 5: Introduction, Positioning & Characterization Table - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 05-introduction-positioning-characterization-table
**Areas discussed:** Characterization table design, Introduction number density, LASSI differentiation placement, Data scope for intro numbers, Multi-file translation emphasis

---

## Characterization Table Design

| Option | Description | Selected |
|--------|-------------|----------|
| Add API columns only | Add 3-4 API spec-count columns to the existing table. Categories in prose. ~9 columns total. | |
| Keep current table, prose only | Present categories and API coverage only in text paragraphs. Minimal paper churn. | |
| Two separate tables | Keep existing SLoC/multi-file table, add second table with API cross-tab + category distribution. | ✓ |
| Redesign as per-kernel table | 35-row table with SLoC, category, APIs, multi-file per kernel. Likely needs appendix. | |

**User's choice:** Two separate tables
**Notes:** Keeps each table readable at full IEEE column width. Second table contains API coverage cross-tab (suite x CUDA/OMP/OCL/OMP-T) and category distribution (12 categories with kernel counts).

### Follow-up: Second Table Content

| Option | Description | Selected |
|--------|-------------|----------|
| API cross-tab + category counts | Suite x API matrix plus 12 domain categories with kernel counts | ✓ |
| API cross-tab only | Just suite x API. Categories in prose only. | |
| You decide | Claude picks most space-efficient layout | |

**User's choice:** API cross-tab + category counts

---

## Introduction Number Density

| Option | Description | Selected |
|--------|-------------|----------|
| Light touch in 1.1-1.2 | 2-3 numbers in Motivation, 2-3 in Gap. Main payload stays in 1.3-1.4. | ✓ |
| Numbers throughout all subsections | Data-rich from start. Risk: spec-sheet feel. | |
| Keep structure as-is | Don't add numbers to 1.1 and 1.2. Their role is narrative framing. | |

**User's choice:** Light touch in 1.1-1.2

### Follow-up: Section 1.1 Motivation Numbers

| Option | Description | Selected |
|--------|-------------|----------|
| Scope teaser: kernels + suites + SLoC range | One sentence: 35 kernels, 5 suites, 80-3304 SLoC | ✓ |
| Scope + multi-file teaser | Same plus 25% multi-file stat | |
| No numbers in Motivation | Keep 1.1 as pure narrative | |

**User's choice:** Scope teaser

### Follow-up: Section 1.2 Gap Numbers

| Option | Description | Selected |
|--------|-------------|----------|
| ParBench vs. ParEval-Repo contrast | 31/35 above 133 SLoC, 38.0% vs 0% pass rate | ✓ |
| Broader comparative sweep | Compare across HumanEval, ParEval, LASSI | |
| Minimal — just category count | One line about 12 computational domains | |

**User's choice:** ParBench vs. ParEval-Repo contrast

---

## LASSI Differentiation Placement

| Option | Description | Selected |
|--------|-------------|----------|
| In the Gap section (1.2) | After ParEval-Repo paragraph. Natural "what's missing" framing. | ✓ |
| In Contributions (1.3) | Woven into framework contribution bullet | |
| Standalone paragraph after Gap | New paragraph between 1.2 and 1.3. Clean separation, adds length. | |
| Split across Gap + Related Work | Brief mention in Gap, full comparison in Section 2 | |

**User's choice:** In the Gap section (1.2)

### Follow-up: Number of Dimensions

| Option | Description | Selected |
|--------|-------------|----------|
| 4 key dimensions | augmentation, 5v1 suites, 6v2 directions, 96v10 specs | ✓ |
| All 6 dimensions | All 6 in one paragraph. Risks length and duplication with Related Work. | |
| 3 dimensions only | augmentation, scale, raw-vs-agentic | |

**User's choice:** 4 key dimensions

---

## Data Scope for Introduction Numbers

| Option | Description | Selected |
|--------|-------------|----------|
| All-suite (700 tasks) everywhere in intro | 38.0% [34.5%, 41.6%] for Abstract + 1.3 + 1.4. Consistent with roadmap. | ✓ |
| Mixed: all-suite for scope, Rodinia for rates | Scope numbers from all suites, pass rates from Rodinia 480 | |
| Rodinia only (current) | Keep 480 tasks / 36.2% as currently written | |

**User's choice:** All-suite (700 tasks) everywhere in intro

---

## Multi-File Translation Emphasis

| Option | Description | Selected |
|--------|-------------|----------|
| In Contributions (1.3) as framework bullet | Add to first contribution bullet alongside framework description | |
| In Gap section (1.2) alongside ParEval-Repo | Pair with kernel isolation argument. 25% multi-file as independent difficulty dimension. | ✓ |
| In Key Findings (1.4) as own paragraph | New findings paragraph with chi-squared stat | |

**User's choice:** In Gap section (1.2) alongside ParEval-Repo contrast

---

## Claude's Discretion

- Exact sentence placement and transitions within subsections
- Second table layout (combined vs two mini-tables)
- LaTeX table formatting details
- LaTeX source comments for provenance
- Mechanical number updates from Rodinia to all-suite scope

## Deferred Ideas

None — discussion stayed within phase scope.
