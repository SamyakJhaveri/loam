# Reflection: NeurIPS Self-Critic Review Document

**Date:** 2026-04-29
**Session work:** Created comprehensive paper review document (`REVIEW_FOR_EREL.md`) with cross-model critique via Codex/GPT-5.4, covering page-limit cuts, bugs, checklist fixes, and data verification for the NeurIPS 2026 submission.
**Files touched:** 1 file committed (`REVIEW_FOR_EREL.md`), 9 pre-existing unstaged .tex changes from prior sessions

## What Surprised Me

- **The abstract's BUILD_FAIL percentage (39.1%) mixes scopes silently.** The abstract discusses L0-only pass@k metrics, then cites 39.1% BUILD_FAIL which comes from all 626 records (L0 + ablation). L0-only BUILD_FAIL is actually 50.0% (213/426). This was not a typo — it was a deliberate choice that happens to be misleading in context. Lesson: when a paper has multiple aggregation levels (per-record, per-task, per-level), every sentence must declare its denominator.

- **The Codex cross-model critique caught real issues the same-model self-review missed.** Specifically: the dangling colon after CUT-1 removes the listing, the lost disjoint-set semantics in CUT-2, and the Qwen-only augmentation table asymmetry. Same-model self-review has blind spots on structural coherence across cuts — it sees each cut in isolation but misses how they interact with surrounding text.

- **The `ParaCodex2026` BibTeX entry already existed in `references.bib` while the paper used `cite{ADD_CITE_TODO}`.** The broken citation wasn't a missing reference problem — it was a malformed LaTeX command (`~cite` instead of `~\cite`). Two independent bugs stacked in one line, making it look like a bigger problem than it was.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (append to end)

```
## Paper Writing: Scope Declarations

Every quantitative claim in the paper must declare its denominator population.
When a paper has multiple aggregation scopes (L0-only tasks, all records including
ablation, per-direction subsets), mixing scopes in the same paragraph without
explicit markers is a reviewer trap. The fix is cheap: add "(N records)" or
"(L0 only)" parentheticals.

This was discovered when the abstract cited 39.1% BUILD_FAIL (all 626 records)
immediately after discussing L0 pass@k (142 tasks). A reviewer checking L0 data
would compute 50.0% and flag the paper as incorrect.
```

**Why:** This prevents future paper sessions from introducing scope-mixing bugs. The pattern applies to any multi-level evaluation (canonical + ablation, per-model, per-direction).

## Prompt Improvement

**Original approach:** User asked for a NeurIPS guidelines check + page limit analysis in one request, then pivoted to a comprehensive review document for a teammate.

**Better approach:** Start with the deliverable format upfront. The pivot to "create a document for Erel" was the right call but came 3 turns in. If the user had specified the teammate-facing deliverable from the start, the initial analysis could have been structured for that audience immediately.

```
Create a self-contained review document at docs/paper/NeurIPS_ready_version/REVIEW_FOR_EREL.md
for my co-author Erel who hasn't read the paper. Use the NeurIPS 2026 checklist guidelines.
Include: bugs, page-limit cuts with exact replacement LaTeX, checklist fixes, and data 
cross-verification. Be adversarial. Present issues one at a time for discussion.
```

## Gotcha Discovered

**Symptom:** CUT-1 (removing a JSON listing from `framework.tex`) would leave a dangling colon. Line 58 reads "...from Rodinia suite:" — the colon introduces the listing. After removal, it dangles into the next paragraph.

**Root cause:** When planning text cuts, the review focused on the cut boundary (lines 60–101) but forgot to check the **introductory sentence** that precedes the cut. This is a general pattern: any time you remove a LaTeX float (listing, figure, table), check the preceding sentence for dangling punctuation (colons, "as shown in", "the following").

**Fix:** Always check the 1-2 lines BEFORE the cut boundary for introductory language that references the removed content. Update the introductory sentence to be self-contained (replace colon with period, merge with replacement text).

**Status:** NEW GOTCHA — not yet documented. Consider adding to a paper-editing conventions rule if more paper work follows.
