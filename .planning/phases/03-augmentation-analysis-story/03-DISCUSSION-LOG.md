# Phase 3: Augmentation Analysis & Story - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 03-augmentation-analysis-story
**Areas discussed:** Matrix data scope, Narrative framing, LASSI positioning, Graph design

---

## Matrix Data Scope

| Option | Description | Selected |
|--------|-------------|----------|
| cuda-to-omp only | Match AUG-01 requirement exactly, simpler | |
| All 7 directions | Primary cuda-to-omp + secondary all-directions | ✓ |

**User's choice:** Primary cuda-to-omp + secondary all-directions (D-01, D-02)
**Notes:** 624 augmented files exist across 7 directions. Primary matrix matches requirement; secondary strengthens null-result claim.

---

## Narrative Framing

| Option | Description | Selected |
|--------|-------------|----------|
| Degradation examples | Find 2-3 kernels that break at higher levels | |
| Strengthened null-result | Most kernels stable; exceptions are localized | ✓ |
| Data-driven (investigate first) | Let the data decide after root-cause analysis | ✓ |

**User's choice:** Null-result-first with data-driven exception investigation (D-04, D-05, D-06)
**Notes:** Backprop L3/L4 BUILD_FAIL must be investigated for root cause before narrative is finalized.

---

## LASSI Positioning

| Option | Description | Selected |
|--------|-------------|----------|
| Brief complementary | 1-2 paragraphs, complementary framing | ✓ |
| Detailed head-to-head | Comparison table with metrics | |

**User's choice:** Brief complementary (D-07, D-08)
**Notes:** Related work table already covers LASSI. Word budget better spent on per-kernel evidence.

---

## Graph Design

| Option | Description | Selected |
|--------|-------------|----------|
| 2 figures (heatmap + trend) | Per-kernel heatmap + aggregate trend line | ✓ |
| 3 figures (+ direction comparison) | Add cross-direction comparison | |
| 1 figure (heatmap only) | Save page budget | |

**User's choice:** 2 figures — heatmap + aggregate trend (D-09, D-10, D-11)
**Notes:** Tight ~10-page budget. Heatmap is primary evidence; trend line shows flat aggregate.

---

## Claude's Discretion

- JSON schema structure, matplotlib styling details, kernel ordering in heatmap, secondary direction presentation

## Deferred Ideas

None
