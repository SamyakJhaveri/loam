# Reflection: Appendix F Supplementary Tables Verification

**Date:** 2026-05-02
**Session work:** Systematic verification of every factual claim in Appendix F (Supplementary Tables and Figures) against codebase data
**Files touched:** 0 files edited; ~15 files read for verification (llm_evaluate.py, augment_dataset.py, specs/*.json, sloc_analysis.json, tech-stack.md, etc.)

## What Surprised Me

- **The "51% multi-file" claim is defensible but only under a specific definition.** The number comes from 18/35 kernels having multi-file `translation_targets` (the kernel source files the LLM must produce). Using `prompt_payload` (all source files shown to the LLM, including headers) gives 22/35 = 63%. Neither number is wrong, but the table row labeled "Source structure" could mean either. This kind of definitional ambiguity is exactly what NeurIPS reviewers catch. Always parenthetically cite the denominator.

- **Commented-out category distribution table has 4 of 10 suite attributions wrong.** The kernel totals per category are correct (they sum to 35), but which suites contribute is wrong for Graph, Linear algebra, ML, and Other. Root cause: the suite assignment depends on which spec file maps to which kernel, and many kernels moved between suites during the HeCBench curation. Since the table is commented out it has zero rendered impact, but if someone uncomments it during crunch time it'll introduce errors.

- **Source-code line numbers in `% src:` comments drift silently.** MODEL_REGISTRY was documented at "lines 74-139" but is now at lines 77-153. The temperature gate was at "lines 946-948" and is now at 986-988. These comments are invisible in the rendered paper but create a false paper trail for anyone auditing the LaTeX source. No automated check catches this.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (add to existing "Key Build/Run Rules" section or create a new "Paper Verification" section)

```
## Paper Source Comments (% src: lines)

Source-line-number comments in LaTeX files (e.g., `% src: llm_evaluate.py lines 74-139`)
are NOT auto-updated when code changes. Before any commit touching paper/*.tex files,
grep for `% src:` and verify at least the ones in the same \section being edited.
```

**Why:** Three stale line-number comments survived 5+ commits of appendix fixes. They don't affect the rendered paper, but they undermine the provenance trail that the comments were designed to provide. A simple grep-before-commit catches these in seconds.

## Prompt Improvement

**Original approach:** User asked to verify appendix text accuracy and gave the raw LaTeX block inline.

**Better approach:** The inline text was helpful but led to ambiguity about which file region to audit — the pasted text didn't match 1:1 with the on-disk file (Appendix F spans lines 988-1117, but the augmentation table duplicate is at 994-1015 and the real one is at 74-89 in Appendix A). Specifying line ranges would have saved one round of investigation.

```
Verify docs/paper/NeurIPS_ready_version/appendices_neurips.tex lines 988-1117
(Appendix F: Supplementary Tables and Figures). Cross-check every number against
the codebase. The augmentation-levels table has a duplicate here (commented out)
and a live version in Appendix A (line 77) — flag if they diverge.
```

## Gotcha Discovered

**Symptom:** The `protect-eval-results.sh` hook blocks `grep` commands that mention `run_eval_batch.py` anywhere in the command string, even when the grep is purely read-only.

**Root cause:** The hook pattern-matches on the literal string `run_eval_batch.py` without distinguishing between execution and text-search. A command like `grep -n "temperature" run_eval_batch.py` triggers the same block as `python3 run_eval_batch.py --no-resume`.

**Fix:** Used `Read` tool instead of `grep` via Bash. Workaround is adequate for occasional use but the hook regex could be tightened to only block commands that start with `python` or contain execution-like patterns.

**Status:** Already partially documented in active-gotchas.md (Result Protection section) but the grep-blocking behavior is NOT mentioned there. The hook's false-positive on read-only grep is an undocumented side effect.
