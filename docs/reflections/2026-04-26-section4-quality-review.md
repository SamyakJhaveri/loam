# Reflection: Section 4 Quality Review Pipeline

**Date:** 2026-04-26
**Session work:** Full rewrite of Section 4 (Experimental Setup) from 9-line stub to 101-line NeurIPS-quality section, plus appendix fixes (hardware table, statistics table, model-config table, Rodinia counts, AI-isms)
**Files touched:** 4 files in docs/paper/NeurIPS_ready_version/ (experimental-setup.tex, appendices_neurips.tex, framework.tex, macros.tex)

## What Surprised Me

- **The "identical sampling parameters" claim was factually false and survived the first draft.** `llm_evaluate.py:946-948` explicitly omits temperature and top_p for Azure reasoning models (HTTP 400 rejection), yet the result JSONs record `temperature: 0.7` as the *requested* value. The gap between what the code does and what the data records is a trap — the result JSON looks correct but the API call never sent it. This was caught only by the 5-reviewer panel (R2, R4, R5 all flagged it independently). Lesson: result JSONs are not ground truth for API-level behavior; the code's provider branches are.

- **The pass@k CI method was wrong in the draft.** I wrote "Wilson 95% CI" as a blanket statement, but `quantitative_findings.py:1053` uses normal-approximation CIs for the macro-averaged pass@k, while Wilson is only used for per-record aggregate rates. These are fundamentally different statistical methods applied to different metrics. The code was the only source of truth — no document or memory recorded this distinction.

- **The appendix statistics table was completely stale.** Every McNemar value, the Cochran-Armitage result (z=0.0 vs actual z=7.65), and the Bonferroni correction (4 tests vs actual 5) were from a prior analysis run that was never updated after Phase 3 canonical evaluation completed. The appendix was a ticking time bomb that would have sunk the paper at review.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (append to existing)

```
## Paper Source Comments Are Not Ground Truth

LaTeX source comments (% src: ...) record what was true at the time of writing.
They can go stale when analysis data is regenerated. Before trusting a % src comment:
1. Check the actual file it references (quantitative_findings.json, paper_data.json)
2. Verify the specific value still matches
3. Update or delete stale comments

The same applies to appendix tables that cite data files — they are snapshots, not live views.
```

**Why:** The appendix statistics table had source comments pointing to `paper_data.json` values that were all stale. The comments gave false confidence that the numbers were verified. Future sessions will encounter the same pattern in Sections 5-7.

## Prompt Improvement

**Original approach:** The plan listed "Ground Truth Files" with paths and said "verify ALL claims against these, not documents." This was correct in spirit but insufficient — it didn't distinguish between result JSONs (which record *requested* parameters) and code (which shows *actual* API behavior).

**Better approach:**
```
### Ground Truth Hierarchy (for paper claims)
1. CODE (actual implementation) — what the API call sends, how CIs are computed
2. RESULT FILES (data on disk) — pass/fail counts, sample sizes, directions
3. RESULT JSON FIELDS — may record requested values, not effective values (e.g., temperature)
4. ANALYSIS OUTPUTS — quantitative_findings.json, paper_data.json (regenerated, can be stale)
5. DOCUMENTS/MEMORY — lowest priority, treat as hints not truth

For every claim: trace to level 1 or 2. Never trust level 3-5 alone.
```

## Gotcha Discovered

**Symptom:** Paper claimed "Both models use identical sampling parameters: temperature 0.7" but GPT-5.4 never received temperature 0.7.
**Root cause:** Azure reasoning models (supports_thinking=True) reject explicit temperature/top_p with HTTP 400. The code at `llm_evaluate.py:946-948` omits these kwargs for such models. But `llm_evaluate.py` still records `temperature: 0.7` in the result JSON as the *intended* value, creating a false impression of parameter parity.
**Fix:** Disclosed the asymmetry honestly in the paper. For \qwenshort{}: explicit temp=0.7. For \gptnew{}: provider-determined (Azure doesn't expose the control). Added sentence about cross-model differences possibly reflecting unmatched sampling.
**Status:** NEW GOTCHA — now documented in `feedback_verify_code_before_paper.md` memory file. Should also be added to `.claude/rules/evaluation.md` under a "Provider Parameter Asymmetries" section.
