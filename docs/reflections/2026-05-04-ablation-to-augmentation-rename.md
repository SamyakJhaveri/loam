# Reflection: Ablation-to-Augmentation Rename

**Date:** 2026-05-04
**Session work:** Replaced all "ablation" terminology with "augmentation" / "L0-conditional filter" across paper .tex files, 10 Python scripts, 3 test files, and regenerated analysis JSON.
**Files touched:** 12 files in `docs/paper/`, `scripts/analysis/`, `scripts/evaluation/`, `results/analysis/`

## What Surprised Me

- **The handoff missed one occurrence.** `audit_eval_consistency.py:239` had `"Ablation augment_level doesn't match suffix"` that wasn't in the handoff's explicit line list. Lesson: always run a grep sweep after applying listed changes — handoff inventories can be incomplete even when thorough.
- **Line numbers had drifted significantly.** `experimental-setup.tex` was only 68 lines (handoff expected line 83 to exist). The file had been rewritten/condensed since the handoff was authored. Text anchors saved us; line numbers alone would have failed.
- **The paper compile error was pre-existing and unrelated.** `results.tex:120` references a figure path `NeurIPS_ready_version/figures/...` that assumes compilation from `docs/paper/` but the standard compile command runs from inside `NeurIPS_ready_version/`. This caused a confusing error that looked like it could be our fault but wasn't.

## Pattern Proposal

**Target:** `HANDOFF.md` (future handoff documents)

```
## Handoff Authoring Rule

Always include a FULL grep verification command at the end of each step that catches
ALL occurrences (not just the ones you listed). The grep sweep is the source of truth;
the line-by-line table is a convenience. If the grep shows non-zero results after
applying listed changes, investigate — the inventory was incomplete.

Text anchors (quoted strings) are mandatory for .tex files. Line numbers are advisory
only — they drift with every Overleaf sync.
```

**Why:** This session found 1 unlisted occurrence (line 239 in audit_eval_consistency.py). In a less careful execution, that would have been a silent miss that only surfaces during a future grep sweep or paper review. Text anchors are reliable; line numbers are not.

## Prompt Improvement

**Original approach:** The handoff listed exact line numbers for every change, which was helpful as a guide but unreliable for drifted files.

**Better approach:** For future rename-style tasks, provide a single sed-like pattern table per file, plus the verification grep. Skip line numbers for .tex files entirely — they drift constantly with Overleaf edits.

```
## STEP 4: scripts/audit_eval_consistency.py

### Replacements (use grep -n "ablation" to find all):
| Pattern | Replacement | Context |
|---------|-------------|---------|
| `ablation_count` | `augmentation_count` | variable name |
| `"ablation"` in dict keys/strings | `"augmentation"` | JSON keys and messages |
| `Ablation` in user-facing strings | `Augmentation` | print statements |

### Verification:
grep -n "ablation" scripts/audit_eval_consistency.py
# Expected: zero results
```

## Gotcha Discovered

**Symptom:** `pdflatex` fails with "File not found" error for `f3_kernel_model_heatmap_unified` when compiling from inside `NeurIPS_ready_version/`.
**Root cause:** `results.tex:120` uses `\input{NeurIPS_ready_version/figures/figures_tek_version/f3_kernel_model_heatmap_unified}` — a path relative to `docs/paper/`, not relative to the compile directory. This works on Overleaf (which resolves paths from project root) but not with local `pdflatex` run from inside the subdirectory.
**Fix:** Either compile from `docs/paper/` with `pdflatex NeurIPS_ready_version/main_neurips.tex`, or change the `\input` path to be relative to the compile directory (remove the `NeurIPS_ready_version/` prefix). This applies to the new unified figures added in the most recent paper restructuring.
**Status:** NEW GOTCHA — not yet documented. Affects local compilation only; Overleaf compiles fine.
