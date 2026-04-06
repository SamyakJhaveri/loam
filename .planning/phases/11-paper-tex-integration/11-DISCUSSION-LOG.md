# Phase 11: Paper TeX Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 11-paper-tex-integration
**Areas discussed:** Main vs. appendix split, Work partitioning, SC26 review depth, Section 7 Discussion rewrite scope

---

## Main vs. Appendix Split

### Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Narrative-first | Main text tells story, ALL detailed tables to appendix. ~5-6 key floats in main. | |
| Evidence-dense | Keep 8-10 floats in main, compress text aggressively. | |
| Hybrid by section | S1-S3 narrative-focused, S4-S6 evidence-dense, S7-S8 compressed. | ✓ |

**User's choice:** Hybrid by section
**Notes:** User wants to preserve full prose narrative in S3-S4 while keeping core evidence tables in S6.

### Per-Kernel Table

| Option | Description | Selected |
|--------|-------------|----------|
| Full in main | All 31 rows, ~1 full page | |
| Condensed + appendix | Top-5 + bottom-5 in main, full in appendix | ✓ |
| Appendix only | Entire table in appendix, prose discussion only | |

**User's choice:** Condensed + appendix

### Methodology Tables

| Option | Description | Selected |
|--------|-------------|----------|
| Compact combined in main | Merge model-config + hardware into one table | |
| All to appendix | State key facts inline, all tables in appendix | ✓ |
| Keep suite-summary only | Suite-summary stays, others to appendix | |

**User's choice:** All to appendix

### Related Work Table

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in main | Full-width table stays in S2 | ✓ |
| Move to appendix | Replace with inline comparison, table in appendix | |
| Condense to 5 papers | Reduced table in main, full in appendix | |

**User's choice:** Keep in main

### Section 3 & 4 Text

| Option | Description | Selected |
|--------|-------------|----------|
| Keep full (S3) | 160 lines, all 4 subsections | ✓ |
| Compress to 1 page (S3) | Focus on spec-as-contract + kernel-centric | |
| Keep full text, tables go (S4) | 226 lines of prose stay, tables to appendix | ✓ |
| Compress to 1 page (S4) | Cut per-kernel detail paragraphs | |

**User's choices:** Keep full text for both S3 and S4

---

## Work Partitioning

| Option | Description | Selected |
|--------|-------------|----------|
| Appendix first, then content | P1: appendix + moves. P2: number updates. P3: SC26 items. P4: audit script. | ✓ |
| Section-by-section | P1: S1-S3. P2: S4-S5. P3: S6-S7. P4: S8 + audit. | |
| Single large plan | One comprehensive front-to-back plan | |

**User's choice:** Appendix first, then content

### Cross-Consistency Audit Method

| Option | Description | Selected |
|--------|-------------|----------|
| Automated script | Python script parses paper.tex, matches against JSON, reports mismatches | ✓ |
| Manual grep pass | Human-guided grep-and-check | |
| Both | Automated + manual | |

**User's choice:** Automated script

---

## SC26 Review Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Triage by impact | Full: P0-6, P1-8, P1-15. Brief: all others. | ✓ |
| All full treatment | Every item gets substantive response | |
| Minimum viable | Quick fixes for all 10 items | |

**User's choice:** Triage by impact

### VERIFY_FAIL Case Studies

| Option | Description | Selected |
|--------|-------------|----------|
| 3 in main + appendix | 3 representative in main, full table in appendix | ✓ |
| 5 in main text | Full treatment, ~0.5 pages | |
| Table only | Compact table, no prose | |

**User's choice:** 3 case studies in main, rest in appendix

---

## Section 7 Discussion Rewrite

| Option | Description | Selected |
|--------|-------------|----------|
| Merge + deepen | Merge S7.1-S7.5 into 2-3 implication-focused subsections | ✓ |
| Light dedup only | Keep structure, remove restated numbers | |
| Move most to appendix | S7 = 0.5 pages, extended in appendix | |

**User's choice:** Merge + deepen

### Threats to Validity

| Option | Description | Selected |
|--------|-------------|----------|
| Keep in main | SC reviewers expect it. Update with power analysis caveats. | ✓ |
| Move to appendix | Free ~0.3 pages, risk reviewer complaint | |

**User's choice:** Keep in main

---

## Claude's Discretion

- Appendix section ordering and LaTeX style
- Condensed per-kernel table formatting
- P1-17 eval commands placement (S5 or appendix)
- Aug heatmap figure placement (appendix or near S6.5)
- Specific VERIFY_FAIL case selection

## Deferred Ideas

- Extended VERIFY_FAIL analysis beyond 3 examples → appendix
- Performance timing analysis → blocked on profiler data
- GPT-4.1 mini data columns → blocked on Le's runs
