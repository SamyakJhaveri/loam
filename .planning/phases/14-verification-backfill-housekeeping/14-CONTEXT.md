# Phase 14: Verification Backfill & Housekeeping

**Type:** Gap Closure
**Created:** 2026-04-05 from v1.0 milestone audit
**Updated:** 2026-04-05 — scope expanded per gap closure plan; stale counts corrected by adversarial review
**Closes:** All 13 orphaned requirements + VERIFY-01 partial + 8 remaining stale REQUIREMENTS.md entries (gap closure commit already fixed 17 of 25)

## Problem

### Missing VERIFICATION.md (5 phases)

Five completed phases have SUMMARY evidence of completion but no formal VERIFICATION.md.
This is the root cause of 13 orphaned requirements in the milestone audit.

- **Phase 3:** AUG-01 (matrix exists), AUG-02 (examples identified), AUG-03 (LASSI text committed), AUG-04 (figures generated)
- **Phase 4:** METHOD-01 (kernel isolation defense), METHOD-02 (statistical test justification), METHOD-03 (reproducibility pins), METHOD-04 (conjunction verification defense)
- **Phase 5:** INTRO-01 (quantitative highlights), INTRO-02 (LASSI differentiation), INTRO-03 (multi-file emphasis), INTRO-04 (gap in evaluation), CHAR-07 (characterization table)
- **Phase 8:** All 10 figures + T2 table regenerated per SUMMARYs
- **Phase 12:** VERIFY-01 fix completed (stale pass@k values updated), no formal verification

### Stale REQUIREMENTS.md Checkboxes (8 remaining)

Gap closure commit (0f4a289) already fixed 17 of 25 stale entries:
- VERIFY-03: checkbox checked, traceability updated to "Complete" (DONE)
- QUANT-01 through QUANT-14: checkboxes checked, traceability updated to "Complete" (DONE)

Still pending (Phase 14 must fix):
- AUG-01 through AUG-04: work complete per Phase 3 SUMMARYs, checkboxes still unchecked `[ ]`
- METHOD-01 through METHOD-04: work complete per Phase 4 SUMMARYs, checkboxes still unchecked `[ ]`

### Stale REQUIREMENTS.md Coverage Count

Currently reports 31/39 checked (after gap closure). After Phase 14 checks AUG-01-04 and METHOD-01-04, will be 39/39.

### Stale ROADMAP.md Progress Table

Some completed phases show incorrect plan counts or status.

## Scope

1. **Create VERIFICATION.md** for Phases 3, 4, 5, 8, 12 — verify SUMMARY claims against on-disk artifacts
2. **Update REQUIREMENTS.md** — 8 remaining checkbox updates (AUG-01-04, METHOD-01-04), traceability status, coverage count
3. **Update ROADMAP.md** progress table to reflect actual state
4. **Artifact evaluation README** — SC26 reproducibility badge support (P1-12)
5. **API env var documentation** — TOGETHER_API_KEY, etc. (P1-13)

## Files to Modify

- `.planning/phases/03-*/03-VERIFICATION.md` (create)
- `.planning/phases/04-*/04-VERIFICATION.md` (create)
- `.planning/phases/05-*/05-VERIFICATION.md` (create)
- `.planning/phases/08-*/08-VERIFICATION.md` (create)
- `.planning/phases/12-*/12-VERIFICATION.md` (create)
- `.planning/REQUIREMENTS.md` (update checkboxes, traceability, coverage)
- `.planning/ROADMAP.md` (update progress table)
- `ARTIFACT_EVALUATION.md` or `docs/artifact_evaluation/README.md` (create)
- `INTEGRATIONS.md` or equivalent (update API env var docs)
