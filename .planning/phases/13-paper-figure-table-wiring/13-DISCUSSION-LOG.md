# Phase 13: Paper.tex Figure & Table Wiring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 13-paper-figure-table-wiring
**Areas discussed:** Aug figure placement, T2 table & drawio, c1-c4 companion figs, F6 & F3 captions

---

## Aug Figure Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Add heatmap only | Wire aug_heatmap.pdf into Section 7.4. Skip aug_trend.pdf since F7 covers aggregate trend. | ✓ |
| Add both | Wire both aug_heatmap.pdf and aug_trend.pdf. Two extra figures (tight page budget). | |
| Replace F7 with both | Remove F7, replace with Phase 3 originals as canonical augmentation figures. | |
| You decide | Claude chooses most space-efficient approach. | |

**User's choice:** Add heatmap only
**Notes:** F7 and aug_trend show the same aggregate pass-rate-vs-level concept. aug_heatmap provides unique per-kernel granularity.

### Follow-up: Placement within Section 7.4

| Option | Description | Selected |
|--------|-------------|----------|
| Before F7 | Heatmap first (detail), then F7 (aggregate). | |
| After F7 | F7 (aggregate) first, then heatmap (detail). Summary → drill-down reading order. | ✓ |
| You decide | Claude picks best reading flow. | |

**User's choice:** After F7

### Follow-up: Caption style

| Option | Description | Selected |
|--------|-------------|----------|
| Detailed caption | Full description with cell color legend and interpretation. | |
| Brief caption | "Per-kernel augmentation status across levels L0–L4 (CUDA-to-OMP, Qwen 3.5). Cell color: pass/fail status." | ✓ |
| You decide | Claude writes caption matching paper style. | |

**User's choice:** Brief caption

---

## T2 Table & Drawio

### T2 Table

| Option | Description | Selected |
|--------|-------------|----------|
| Skip T2 entirely | tab:direction-rates already shows per-direction rates with current 5-suite data. T2 is redundant and stale. | ✓ |
| Update & add T2 | Regenerate T2 with current data and wire in as compact model comparison. | |
| You decide | Claude assesses whether T2 adds value. | |

**User's choice:** Skip T2 entirely
**Notes:** T2 content (49/138, 35.5%) predates 5-suite expansion. tab:direction-rates has current data.

### Architecture Drawio Export

| Option | Description | Selected |
|--------|-------------|----------|
| I'll export manually | User opens draw.io, exports PDF, places in docs/paper/latex/figures/. Phase 13 uncomments \includegraphics. | ✓ |
| Try CLI export | Attempt drawio CLI export (may need xvfb on headless Linux). | |
| Leave as placeholder | Keep \fbox placeholder for now. | |

**User's choice:** I'll export manually

### Follow-up: Figure 1 caption

| Option | Description | Selected |
|--------|-------------|----------|
| Caption is fine | Existing 5-line caption matches diagram. No changes. | ✓ |
| Needs update | Caption may not match actual drawio content. | |
| Shorten it | Caption too long for SC26 — trim to 2-3 sentences. | |

**User's choice:** Caption is fine

### Follow-up: Stale T2 file cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Leave it | Don't touch docs/paper/figures/ — outside compilation path. | |
| Delete it | Remove stale file to avoid confusion. | ✓ |

**User's choice:** Delete it

---

## c1-c4 Companion Figures

| Option | Description | Selected |
|--------|-------------|----------|
| Wire c4 (funnel) only | Selection funnel visual is unique — tables can't replace it. Skip c1-c3. | |
| Wire all four | All four add visual reinforcement. Accept page cost. | |
| Skip all | Tables already convey the information. Tight SC26 page budget. | ✓ |
| You decide | Claude picks based on value beyond existing tables. | |

**User's choice:** Skip all
**Notes:** User confirmed with "K." — tables are sufficient.

---

## F6 & F3 Captions

### F6 Caption

| Option | Description | Selected |
|--------|-------------|----------|
| Suite-focused | "Cross-suite pass rate comparison (L0, Qwen 3.5). Per-suite aggregate pass rates with Wilson 95% CIs across all 5 benchmark suites." | ✓ |
| Kernel-context | "Per-suite aggregate pass rates... Suite-level variation reflects differences in kernel complexity and API coverage." | |
| You decide | Claude writes caption matching paper's terse style. | |

**User's choice:** Suite-focused

### F3 Caption

| Option | Description | Selected |
|--------|-------------|----------|
| Descriptive | "Per-kernel pass/fail heatmap across 6 standard translation directions (29 kernels, L0, Qwen 3.5). Cell color: green (PASS), red (BUILD_FAIL), orange (RUN_FAIL), blue (VERIFY_FAIL), pink (EXTRACTION_FAIL)." | ✓ |
| Brief + legend | "Kernel × direction heatmap (29 kernels, 6 directions, L0, Qwen 3.5). Color legend as shown." | |
| You decide | Claude writes caption matching paper style. | |

**User's choice:** Descriptive

### Follow-up: F6 Label Rename

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to fig:cross-suite | Update label and all references. Cleaner for maintenance. | ✓ |
| Keep fig:xsbench | Fewer changes, less risk. Label is internal-only. | |

**User's choice:** Rename to fig:cross-suite

### Follow-up: F6 Location

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in place | Leave after pass@k section. Cross-suite fits as big-picture summary. | ✓ |
| Move to Overall | Relocate to Section 7.1 where per-suite breakdown is first discussed. | |
| You decide | Claude picks best placement. | |

**User's choice:** Keep in place

### Follow-up: Old F6 file cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Delete old file | Remove f6_xsbench_comparison.pdf/.png from docs/paper/latex/figures/. | ✓ |
| Leave it | Keep both files. Old one is harmless. | |

**User's choice:** Delete old file

---

## Claude's Discretion

- Exact `\begin{figure}` environment sizing for aug_heatmap
- Whether aug_heatmap needs `\label` for cross-referencing
- Minor prose adjustments around F6 for new cross-suite framing
- TODO comment cleanup after drawio uncommenting

## Deferred Ideas

- c1-c4 companion figures — could go to supplementary material in camera-ready
- aug_trend.pdf — redundant with F7, but could replace it if Phase 3 version preferred
- XSBench-specific comparison figure — text in Section 4.3 covers the argument; dedicated figure for camera-ready if page allows
