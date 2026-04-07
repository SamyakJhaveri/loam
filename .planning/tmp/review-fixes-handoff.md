# SC26 Paper Review Fixes — Session Handoff

## Status
Review panel simulation COMPLETE (Phase 3). Fixes NOT yet executed. Execute in this session.

## CRITICAL CONSTRAINT
**DO NOT reframe as single-model paper.** GPT-4.1 mini data will be added after these fixes. Preserve all \pending{} macros, \tbd entries, and two-model framing.

## Fixes to Execute (ONLY these — nothing else)

### FIX-2a: Report the Fisher exact test in S6 augmentation robustness
- **What:** Add the Fisher exact test result (L0 vs pooled L1-L4, OR=0.41, p=0.0037, corrected p=0.0075) to S6.4 (Augmentation Robustness, around lines 879-912)
- **Source data:** `results/analysis/statistical_analysis.json` → Fisher exact test fields
- **Context from cross-talk:** The Fisher test uses ALL directions (n=192), not the balanced CUDA-to-OMP subset (n=120). It shows augmented code passes MORE than L0. This is NOT contradictory — it tests a different scope and a different hypothesis (any L0/augmented difference vs monotonic trend). R1-HPC noted this actually strengthens the anti-memorization case since memorization would predict augmented < L0. Explain the scope difference when reporting.
- **Do NOT soften the augmentation claim language** (FIX-2c was explicitly excluded by user)

### FIX-2b: Report or exclude the omp_target McNemar test
- **What:** The omp_target McNemar pair (Cohen's h=-1.37, p=0.0625 uncorrected, p=0.25 corrected) is included in the Bonferroni correction family (4 tests) but not reported in text (S6.5, around line 946)
- **Source data:** `results/analysis/statistical_analysis.json` → McNemar direction_asymmetry fields
- **Options:** Either (a) add a sentence reporting it alongside the other 3 pairs, OR (b) exclude it from the Bonferroni count (changing alpha from 0.05/4=0.0125 to 0.05/3=0.0167)
- **R3-STATS recommendation:** Report it — it's the most interesting pair (large effect)

### FIX-3: Add prompt template as appendix
- **What:** Add the full translation prompt template (system message + representative user message with anonymization) as an appendix listing
- **Source:** `scripts/evaluation/llm_evaluate.py` — system message at ~line 629-637, user message construction, anonymization protocol at ~lines 578-589
- **Also:** Add 2-3 sentences in S3.4 or S5.1 describing the anonymization protocol (kernel-name stripping, comment removal, filename genericization)
- **Cost:** ~0.5 pages in appendix

### SF-1: Report API costs and evaluation time
- **What:** Add a paragraph in S5.5 (Hardware and Software) or appendix with: total API cost ($145.37 for Qwen via Together AI), campaign duration (~6 days, March 27-April 2), cost per task (~$0.13), total tokens (120M)
- **Source data:** `results/analysis/token_analysis.json` (or wherever this data lives — grep for "145.37" or "token_analysis")

### SF-3: Clarify unbalanced design in abstract/intro
- **What:** The abstract (line 84) says "710 primary campaign tasks spanning 31 kernels across five suites, six directions, and five augmentation levels" which implies full factorial (31×6×5=930≠710). Add language clarifying the design is unbalanced because not all kernels have all API implementations.
- **Location:** Abstract and/or S5.2 (Translation Directions)

### SF-6: Report absolute self-repair improvement alongside relative
- **What:** Where "70% relative increase" appears (S1 line 180, S6.3 around line 874), add the absolute figure: "15.8 percentage points"
- **Current:** "a 70% relative increase"
- **Target:** "a 70% relative increase (15.8 percentage points)" or similar

### SF-7: Add LICENSE file at project root
- **What:** Create a LICENSE file (MIT recommended) at `/home/samyak/Desktop/parbench_sam/LICENSE`
- **Note:** Rodinia has NCSA/Illinois, XSBench/RSBench are MIT, mixbench is GPL-2.0, HeCBench is MIT. MIT is compatible. The LICENSE covers the ParBench framework code only.

## Files to Read Before Starting
- `docs/paper/latex/paper.tex` — the paper (1112 lines)
- `results/analysis/statistical_analysis.json` — Fisher exact test and McNemar data
- `results/analysis/token_analysis.json` — API cost data (grep for location first)
- `scripts/evaluation/llm_evaluate.py` — prompt template source (~lines 578-637)
- `.planning/phases/15-paper-review-tools/panel-report.md` — full panel report for context
- `.planning/phases/15-paper-review-tools/r3-stats-review.md` — statistical details

## What NOT to Do
- Do NOT reframe as single-model
- Do NOT remove \pending{} macros or \tbd entries
- Do NOT soften augmentation claim language (FIX-2c excluded)
- Do NOT fix duplicate \newcommand LaTeX errors (not in scope)
- Do NOT fix HeCBench spec commit hashes (SF-2, not in scope)
- Do NOT add XSBench caveat (SF-4, not in scope)
- Do NOT make any other changes to the paper beyond the 7 listed fixes
