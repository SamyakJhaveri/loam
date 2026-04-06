# Phase 14: Verification Backfill & Housekeeping - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-06
**Phase:** 14-verification-backfill-housekeeping
**Areas discussed:** Verification depth, Artifact eval README, API env var docs, Execution ordering

---

## Verification Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Full Phase 1-style | Observable Truths table, Required Artifacts, Key Link Verification — same template as Phase 1 | ✓ |
| Lightweight checklist | Requirement ID + status + single evidence line | |
| Mixed approach | Full depth for Phases 3 & 4, lightweight for 5, 8, 12 | |

**User's choice:** Full Phase 1-style for all 5 phases
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| Verify against live data | Read actual result JSONs, spec files, paper.tex, analysis outputs on disk. Never trust old docs. | ✓ |
| Re-run then verify | Re-run all analysis scripts first, then verify | |
| You decide | Claude picks per-phase | |

**User's choice:** Verify against live data
**Notes:** User emphasized that data may have been updated since old verification/summary files were written. Always ground evidence in actual data from results/ and specs/, not stale planning docs.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Verify only, mark gaps honestly | Phase 14 only verifies and documents what exists | |
| Verify + fill small gaps | Create missing files if evidence is 90% there | |
| Verify + create all missing | Phase 14 owns gap closure end-to-end | ✓ |

**User's choice:** Verify + create all missing
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| REQUIREMENTS.md criteria | Each truth maps to a requirement ID | ✓ |
| ROADMAP.md phase success criteria | Original phase success criteria | |
| Both cross-referenced | Map REQUIREMENTS.md IDs to ROADMAP.md criteria | |

**User's choice:** REQUIREMENTS.md criteria
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| Grep + compare numbers | Extract numbers from paper.tex and compare against live data | ✓ |
| Section existence only | Confirm sections/tables exist with non-empty content | |
| Spot-check 3-5 key claims | Pick most important numbers per requirement | |

**User's choice:** Grep + compare numbers
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| File exists + non-empty + timestamp | Check PDFs exist, are non-empty, note timestamps | |
| Re-run generation script | Run generate_paper_figures.py and confirm all expected PDFs | ✓ |
| Exists + data source check | PDFs exist + verify data source files are current | |

**User's choice:** Re-run generation script
**Notes:** None

---

## Artifact Eval README

| Option | Description | Selected |
|--------|-------------|----------|
| Root: ARTIFACT_EVALUATION.md | Standard SC convention — single self-contained file | ✓ |
| docs/artifact_evaluation/README.md | Nested in docs/ | |
| Appendix in paper.tex | Include in paper appendix | |

**User's choice:** Root: ARTIFACT_EVALUATION.md
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| Setup + smoke test only | Clone, submodule init, pip install, paths.json, smoke test. ~1 page. | ✓ |
| Full walkthrough | Setup + eval batch + interpreting results + augmentation demo. 3-5 pages. | |
| Setup + table of key claims | Setup + claim-to-command mapping table | |

**User's choice:** Setup + smoke test only
**Notes:** None

---

## API Env Var Docs

| Option | Description | Selected |
|--------|-------------|----------|
| Section in ARTIFACT_EVALUATION.md | Single source for reviewers | ✓ |
| Separate INTEGRATIONS.md | Standalone file at root | |
| Both | Brief mention + detailed reference | |

**User's choice:** Section in ARTIFACT_EVALUATION.md
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| All 5 keys documented | TOGETHER, AZURE, OPENAI, GROQ, GOOGLE | |
| Only Together AI | Just TOGETHER_API_KEY | ✓ |
| All keys + which are optional | All 5 with required/optional markers | |

**User's choice:** Only Together AI
**Notes:** Only key needed to reproduce paper's Qwen results

---

## Execution Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| Single plan, dependency-ordered | Verify 3/4/5 → 8/12 → REQUIREMENTS → ROADMAP → ARTIFACT_EVAL | ✓ |
| Two plans: verify then housekeep | Plan 1: verifications. Plan 2: docs | |
| Parallel where possible | Parallel verifications via subagents, then sequential docs | |

**User's choice:** Single plan, dependency-ordered
**Notes:** None

---

| Option | Description | Selected |
|--------|-------------|----------|
| Fix in place | Fix paper.tex claims that don't match live data | ✓ |
| Flag only | Document discrepancies, don't touch paper.tex | |
| Fix minor, flag major | Fix number mismatches, flag structural issues | |

**User's choice:** Fix in place
**Notes:** Aligns with D-03 (end-to-end gap closure)

---

## Claude's Discretion

- Exact formatting of Observable Truths tables
- Dependency ordering within each phase's verification
- ARTIFACT_EVALUATION.md section structure
- Whether to commit each VERIFICATION.md individually or batch

## Deferred Ideas

None — discussion stayed within phase scope
