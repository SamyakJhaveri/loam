# Reflection: Diagram-Paper Consistency Audit

**Date:** 2026-04-28
**Session work:** Architecture diagram fixes (18 issues), data integrity fix, NeurIPS compliance edits, complete self-repair removal, self-critic review
**Files touched:** 4 files in figures/, results/analysis/, project root

## What Surprised Me

- **The diagram had drifted far from the code.** 8 factual errors (wrong temperature, wrong task count, wrong direction count, stale self-repair boxes, wrong statistical test) had accumulated across edits by multiple contributors. The diagram was treated as a static image rather than a living document grounded in code. The fix required reading `verifier.py`, `llm_evaluate.py`, `harness/constants.py`, augmentation source, and 5+ data files to verify every label.

- **"JSON Schema" vs "JSON Spec" is a real trap.** The extensibility box initially said "JSON Schema" — a term with a specific RFC meaning that doesn't match how ParBench extends (via spec files, not schema modification). In an HPC-oriented NeurIPS review, this would likely pass unnoticed, but in a broader ML audience it could confuse readers who know JSON Schema as a validation standard.

- **Figure staleness detection gave a false alarm.** All 14 PDFs flagged as "STALE" because `quantitative_findings_gpt54.json` was touched (metadata label fix). But only the `metadata.model` string changed — zero data values changed. Timestamp-based staleness is necessary but not sufficient; content-aware diffing would catch this.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (or a new `diagram-maintenance.md` rule)

```
## Architecture Diagram Maintenance

The architecture diagram (`docs/paper/NeurIPS_ready_version/figures/parbench_architecture.drawio`)
must be verified against code whenever ANY of these change:
- Direction count or definitions (harness/constants.py, run_eval_batch.py)
- Spec counts (specs/*.json, harness/constants.py EXCLUDED_SPECS)
- Augmentation transforms (c_augmentation/augment_dataset.py class list)
- Verification strategy list (harness/verifier.py)
- Outcome classification (harness/models.py Status enum)
- Metrics reported in paper (analysis scripts)

Verification: grep the drawio XML for stale terms. Every text label in the diagram
must trace to a code identifier, data file value, or paper section.
```

**Why:** The diagram accumulated 8 factual errors because no rule triggered re-verification when code or experimental design changed. This pattern ensures the diagram stays grounded.

## Prompt Improvement

**Original approach:** The HANDOFF listed 8 specific diagram fixes with cell IDs. The session started by applying those fixes, then discovered 10 additional issues through code-grounded review.

**Better approach:** Start with a code-first audit BEFORE listing fixes. The HANDOFF's 8 fixes were identified by reading the diagram in isolation. A code-grounded pass would have caught all 18 issues upfront.

```
Phase 6 Task 1: Read the drawio XML. For every text label, grep the codebase
to verify the claim. Present a complete issue list BEFORE any edits. Then the
user applies all fixes in one draw.io session instead of iterating.
```

## Gotcha Discovered

**Symptom:** The `✓BUILD PASS` green label appeared twice — once after Build (correct) and once after Run (wrong). The Run stage should show `✓RUN PASS`.

**Root cause:** When the diagram was originally created, the Build PASS label was copy-pasted to create the Run PASS label, but the text was never updated. The cell IDs (`dTBirprDGcM_VUs01LYS-1` and `dTBirprDGcM_VUs01LYS-3`) are auto-generated, giving no semantic hint about which stage they belong to.

**Fix:** Manually changed the second label's text from `BUILD` to `RUN` in draw.io.

**Status:** NEW GOTCHA — not previously documented. Specific to the architecture diagram, unlikely to recur now that the diagram is verified.
