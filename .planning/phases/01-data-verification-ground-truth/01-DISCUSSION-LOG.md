# Phase 1: Data Verification & Ground Truth - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 01-data-verification-ground-truth
**Areas discussed:** Discrepancy resolution, Verification scope, Stale analysis handling
**Areas skipped:** GPT-4.1 mini references (user chose not to discuss)

---

## Discrepancy Resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Fix inline | Fix paper.tex immediately during verification. Git diff as audit trail. | ✓ |
| Report first, fix later | Produce structured discrepancy report, review, then fix separately. | |
| Fix obvious, report ambiguous | Fix clear-cut mismatches inline, flag ambiguous ones in report. | |

**User's choice:** Fix inline (Recommended)
**Notes:** Fastest path to submission-ready text with 5-day deadline.

### Follow-up: Audit trail

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, brief summary | Markdown file listing each claim checked and result. | |
| No, just fix and commit | Trust git diff as audit trail. | ✓ |

**User's choice:** No, just fix and commit

### Follow-up: Source annotations

| Option | Description | Selected |
|--------|-------------|----------|
| No annotations | Just fix numbers, no internal markup. | |
| Brief source comments | Add LaTeX comments noting source file and field. | ✓ |
| Only where already commented | Update existing comments, don't add new ones. | |

**User's choice:** Brief source comments (Recommended)

### Follow-up: Table structure

| Option | Description | Selected |
|--------|-------------|----------|
| Fix data values only | Only correct numbers/text within existing cells. | |
| Fix structure too | Fix missing columns, wrong row order if data demands it. | ✓ |

**User's choice:** Fix structure too

---

## Verification Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Numbers + tables only | Verify explicit numbers and table cells only. | |
| Numbers + tables + data-backed prose | Also verify qualitative claims derived from data. | ✓ |
| Everything checkable | Numbers, tables, prose, AND cross-references. | |

**User's choice:** Numbers + tables + data-backed prose

### Follow-up: Section 5

| Option | Description | Selected |
|--------|-------------|----------|
| Verify Qwen numbers in S5 too | Qwen data is frozen, verify those numbers now. | ✓ |
| Stop at Section 4 | Results section will change, don't verify now. | |
| Verify S5 Qwen only, flag GPT gaps | Verify Qwen, add TODO comments for GPT data. | |

**User's choice:** Verify Qwen numbers in S5 too (Recommended)

### Follow-up: Figures

| Option | Description | Selected |
|--------|-------------|----------|
| Tables only | Figures depend on data pipeline, not manual checking. | |
| Tables + figure captions | Verify captions match figure content. | |
| Tables + regenerate figures | Re-run figure generation to ensure match. | ✓ |

**User's choice:** Tables + regenerate figures

### Follow-up: Source of truth

| Option | Description | Selected |
|--------|-------------|----------|
| paper_data.json | Consolidated analysis file as primary source. | |
| Raw result JSONs | Go directly to results/evaluation/together-qwen-*/ files. | ✓ |
| paper_data.json, fallback to raw | Use paper_data.json primary, raw as fallback. | |

**User's choice:** Raw result JSONs
**Notes:** Most rigorous — raw files are immutable primary sources, derived files may have aggregation bugs.

---

## Stale Analysis Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Regenerate immediately | Re-run analysis scripts before verification. | |
| Verify against raw, regenerate at end | Verify against raw JSONs, regenerate at end of phase. | ✓ |
| Assess only, regenerate in Phase 2 | Just assess freshness, regenerate later. | |

**User's choice:** Verify against raw, regenerate at end

### Follow-up: Regeneration scope

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, full regeneration | Re-run all analysis scripts + figure generation. | ✓ |
| Analysis files only | Regenerate analysis JSONs, figures wait for later. | |

**User's choice:** Yes, full regeneration (Recommended)

### Follow-up: Data freeze

| Option | Description | Selected |
|--------|-------------|----------|
| Freeze at Phase 1 start | Count result files once, new tmux results out of scope. | ✓ |
| Incorporate if available | Include new results if they appear during Phase 1. | |

**User's choice:** Freeze at Phase 1 start (Recommended)

---

## Claude's Discretion

- Verification ordering within sections
- Batch-verify tables first vs. section-by-section
- Exact LaTeX comment format
- Handling GPT-4.1 mini references during verification

## Deferred Ideas

None — discussion stayed within phase scope.
