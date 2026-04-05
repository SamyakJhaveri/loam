# Phase 12: Fix Stale Pass@k Values - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 12-fix-stale-passk-values
**Areas discussed:** Verification scope, Source comment audit, Section 7 cross-check, Intro/abstract consistency

---

## Verification Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full audit (Recommended) | Verify EVERY numerical claim in Sections 6.6-6.8 and Section 7 against ground truth files | ✓ |
| Spot check only | Quick spot check of the 8+ originally identified stale values | |
| You decide | Claude's discretion on how thorough to be | |

**User's choice:** Full audit
**Notes:** Analysis revealed that existing pass@k values in paper.tex (426/142/19.7%) already match ground truth. The phase needed to expand beyond the original "8 stale values" to a comprehensive audit.

---

## Source Comment Audit

| Option | Description | Selected |
|--------|-------------|----------|
| Fix to paper_data.json | Update all source comments to reference paper_data.json (all suites) as the ground truth | ✓ |
| Dual references | Comment both files for cross-checking | |
| Leave as-is | Pass@k numbers are identical in both files anyway | |

**User's choice:** Fix to paper_data.json
**Notes:** User provided critical correction: "paper_data.json is the ground truth with data from all benchmarks... we do NOT want to limit our paper to rodinia." This pivoted the entire phase from Rodinia-only to all-suite scope.

---

## Section 7 Cross-Check

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, same pass (Recommended) | Update Section 6 AND Section 7 in one phase | ✓ |
| Section 7 separately | Phase 12 handles Section 6 only; Phase 11 handles Section 7 later | |

**User's choice:** Yes, same pass
**Notes:** None

---

## Intro/Abstract Consistency

| Option | Description | Selected |
|--------|-------------|----------|
| Fix intro too | Update intro/abstract from 700/38.0% to 710/38.3% for full paper consistency | ✓ |
| Intro stays for Phase 11 | Phase 12 focuses on Section 6+7; intro deferred | |
| I'm ready for context | Skip this question | |

**User's choice:** Fix intro too
**Notes:** paper_data.json shows 710 primary tasks and 38.3% pass rate; intro currently says 700 tasks and 38.0%. User chose to fix everything in one pass.

---

## Claude's Discretion

- Rounding conventions for percentages
- Handling of new ERROR status (1 task) in failure taxonomy
- Paragraph rewrites where number changes affect narrative

## Deferred Ideas

None — discussion stayed within phase scope.
