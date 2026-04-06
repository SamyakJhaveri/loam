# Phase 13: Paper.tex Figure & Table Wiring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-06 (context update session — original 2026-04-05)
**Phase:** 13-paper-figure-table-wiring
**Areas discussed:** Aug heatmap placement, F6 target file correction, Architecture diagram readiness, Stale line number refresh

**Reason for update:** Phase 11 (paper-tex-integration) completed on 2026-04-06, moving F6 and F7 to appendices.tex, adding a \ref{fig:xsbench} at paper.tex:977, and shifting all line numbers. Original context was stale.

---

## Session 2 (2026-04-06): Context Update

### Aug Heatmap Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Appendix near F7 | Insert after F7 in appendices.tex (line 1221). Keeps augmentation figures together. Add reference in paper.tex. | ✓ |
| Main paper body | Insert in paper.tex near augmentation section (line 884-911). Higher visibility but uses page budget. | |
| You decide | Claude picks based on page constraints. | |

**User's choice:** Appendix near F7 (Recommended)
**Notes:** F7 is now in appendices.tex (moved during Phase 11). Original context assumed F7 was in paper.tex.

---

### F6 Target File Correction

| Option | Description | Selected |
|--------|-------------|----------|
| Update all | Update filename, label, caption in appendices.tex AND \ref in paper.tex:977. | ✓ |
| Minimal: filename + label only | Just fix filename and label references. | |
| You decide | Claude picks. | |

**User's choice:** Update all (Recommended)
**Notes:** Key correction: F6 is in appendices.tex:1252-1257, NOT paper.tex. \ref{fig:xsbench} at paper.tex:977 EXISTS (original context incorrectly said zero refs).

#### F6 Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Delete old files | Remove f6_xsbench_comparison.pdf and .png. | ✓ |
| Keep both | Leave old files for reference. | |

**User's choice:** Delete old files

---

### Architecture Diagram Readiness

| Option | Description | Selected |
|--------|-------------|----------|
| I'll export before execution | User exports drawio to PDF before Phase 13 runs. Unconditional uncomment. | ✓ |
| Conditional: check if PDF exists | Phase 13 checks, acts accordingly. | |
| Skip architecture wiring | Don't touch architecture figure. | |

**User's choice:** I'll export before execution

---

### Stale Line Number Refresh

| Option | Description | Selected |
|--------|-------------|----------|
| Just refresh known items | Update only discussed items. | |
| Quick scan for others | Grep for other TODO/placeholder/stale references. | ✓ |

**User's choice:** Quick scan for others
**Notes:** Scan found 3 TODO figure placeholders in appendices.tex for deleted survey images.

#### Appendix Survey Figure Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Include in Phase 13 | Investigate and handle in this phase. | ✓ |
| Defer to Phase 14 | Leave for housekeeping phase. | |
| Just remove the TODOs | Delete TODO comments only. | |

**User's choice:** Include in Phase 13

#### Survey Figure Resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Copy 2, remove quality_tiers block | Copy 2 available images, remove quality_tiers. | |
| Copy 2, keep quality_tiers placeholder | Copy available, keep placeholder. | |
| Remove all 3 figure blocks | Remove all three figure blocks entirely. | ✓ |

**User's choice:** Remove all 3 figure blocks
**Notes:** Survey figures are peripheral. Two images exist in analysis/visualizations/take in paper/ but not critical for SC26. quality_tiers.png doesn't exist anywhere. Prose refs (fig:api-network, fig:bipartite) must be updated after removal.

---

## Session 1 (2026-04-05): Original Context (now superseded)

Original decisions carried forward with corrections:
- Aug heatmap only (not trend) — unchanged
- T2 table skipped — unchanged
- Architecture manual export — unchanged
- c1-c4 skipped — unchanged
- F6 rename/caption/label — corrected target file (appendices.tex, not paper.tex)
- F3 caption update — corrected line number (831, not 931)

### ROADMAP SC deviations (from Session 1, still valid)

1. **SC-3:** ROADMAP says add both aug_heatmap and aug_trend → User chose heatmap only (F7 covers trend)
2. **SC-4:** ROADMAP says add T2 table → User chose skip entirely (tab:direction-rates already covers it)

---

## Claude's Discretion

- Exact figure environment for aug_heatmap (figure vs figure*)
- aug_heatmap \label (needed — D-02 uses \ref{fig:aug-heatmap})
- Prose adjustments around F6 reference at paper.tex:977
- How to rephrase appendix survey prose after figure removal

## Deferred Ideas

- c1-c4 companion figures — supplementary material in future revision
- aug_trend.pdf — redundant with F7
- Survey images in analysis/visualizations/take in paper/ — could restore in camera-ready
- quality_tiers.png — needs regeneration from scratch
