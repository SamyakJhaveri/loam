# Phase 20: paper-final-update - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 20-paper-final-update
**Areas discussed:** Submission file priority, Narrative scope, Unstaged methodology edits, Validation gate on deadline day, XSBench GPT coverage

---

## Submission File Priority

| Option | Description | Selected |
|--------|-------------|----------|
| overleaf.tex (primary) | Overleaf is the submission artifact; paper.tex is secondary | ✓ |
| paper.tex (primary) | paper.tex is authoritative | |
| Both equally important | Identical priority | |

**User's choice:** overleaf.tex is the SC26 submission artifact.

**Follow-up — methodology sync to paper.tex:**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — keep paper.tex in sync | Apply methodology edits + GPT numbers to paper.tex | ✓ |
| No — paper.tex is secondary | Only GPT numbers in paper.tex | |

**Notes:** paper.tex must receive both the unstaged methodology edits (architecture caption, spec schema, verify stage, augmentation) AND the GPT numeric updates from Phase 19.

---

## Narrative Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Update numbers + revise inverted prose | Replace numbers AND rewrite sentences where interpretation reversed | ✓ |
| Update numbers only | Swap numbers, leave narrative framing unchanged | |
| You decide — minimal safe changes | Claude applies 19-STRUCTURAL-CHANGES.md, uses judgment for unlisted items | |

**User's choice:** Update numbers in-place AND revise narrative prose where the story changed (VERIFY_FAIL reversal, BUILD_FAIL less severe, top build subcategory changed).

**Follow-up — XSBench coverage handling:**

| Option | Description | Selected |
|--------|-------------|----------|
| Brief qualification sentence | Note Qwen:48 vs GPT:6 XSBench file asymmetry | deferred |
| Footnote only | Less prominent | |
| No mention needed | Figure already reflects it | |

**User's response:** "remind me after this discussion and i will find and add those files in" — user plans to add valid XSBench GPT result files before Phase 20 executes.

---

## Unstaged Methodology Edits

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into Phase 20 commit | Stage + GPT numbers together in paper(20): | ✓ |
| Commit separately first | Small commit for methodology text first | |
| Discard and redo cleanly | git restore overleaf.tex, redo in Phase 20 | |

**User's choice:** Fold methodology edits into the single Phase 20 commit.

**Follow-up — plan approach:**

| Option | Description | Selected |
|--------|-------------|----------|
| Create 20-02-PLAN.md — fresh plan | New plan accounting for working tree state | ✓ |
| Clear done markers, re-execute 20-01 | Remove done markers, re-run existing plan | |
| You decide | Claude picks approach | |

**User's choice:** Create 20-02-PLAN.md as a fresh plan. 20-01-PLAN.md preserved as reference.

---

## Validation Gate on Deadline Day

| Option | Description | Selected |
|--------|-------------|----------|
| Standard /validate — 4-wave gate | Full validation before commit | ✓ |
| Spot-check only — fast path | Number spot-check + LaTeX balance only | |
| Trust the plan — no validation | Skip validation entirely | |

**User's choice:** Standard 4-wave /validate before commit.

**Follow-up — pdflatex compile check:**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — try pdflatex, skip if unavailable | Run pdflatex, check for errors | ✓ |
| No — LaTeX balance check sufficient | Skip pdflatex run | |

**User's choice:** Try pdflatex after commit; skip silently if not installed.

---

## XSBench GPT Coverage (follow-up at end of discussion)

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — I'll find and add them first | Phase 20 waits for user to add files, then Phase 19 re-run | ✓ |
| No — proceed with current 6 files | Execute Phase 20 with 6 GPT XSBench files | |
| Skip for deadline — revisit post-submission | Submit with current data | |

**User's choice:** User will find and add valid XSBench GPT result files.

**Follow-up — what Phase 20 plan does after XSBench files added:**

| Option | Description | Selected |
|--------|-------------|----------|
| Task 0: re-run Phase 19 analysis pipeline | Verify XSBench added, re-run all scripts, then paper edits | ✓ |
| Trust Phase 19 outputs as-is | Use existing paper_data_gpt41mini.json | |

**User's choice:** Phase 20 plan starts with Task 0: re-run Phase 19 analysis pipeline.

---

## Claude's Discretion

- Wilson CI recalculation for Aggregate row (Table 3): combined totals after re-run
- Error taxonomy subcategory counts: always read from freshly generated error_taxonomy.json
- Exact per-direction rates for cross-model table: read from freshly generated cross_model_comparison.json

## Deferred Ideas

- Full XSBench GPT campaign re-run if user-found files are only partial — post-submission
- Page budget compression — deferred to Samyak + Le manual edit
- Cross-model pass@k comparison — post-submission if new GPT data enables it
