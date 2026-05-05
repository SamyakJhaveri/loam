# HANDOFF: ParBench NeurIPS Paper — Final Pre-Submission Audit Corrections

**Date:** 2026-05-05
**Status:** Research & verification COMPLETE. Ready for execution.
**Supersedes:** Previous ablation→augmentation handoff (check if that was completed via `grep -rn "ablation" scripts/ docs/paper/`; if occurrences remain, do that first).

---

## What This Task Is About (Plain English)

ParBench is a benchmark framework that tests whether AI models (like GPT-5.4, Codex, Qwen) can correctly translate parallel code between CUDA, OpenMP, and OpenCL. We wrote a paper about it for NeurIPS 2026.

**The problem:** An external reviewer (Gal, advisor) did a final audit of the PDF and found several issues that must be fixed before we can upload to OpenReview. None require new experiments — they are all text corrections, caption fixes, bibliography cleanup, and a factual error in the augmentation section where two models' numbers were conflated.

**What you must do:** Apply exactly 10 corrections to LaTeX source files. The corrections are pre-verified against raw data (every number was recomputed from the actual result JSON files). You just need to make the text edits and verify each one.

**Where the user applies them:** The user copies the corrected text from local files into Overleaf (their online LaTeX editor). Do NOT attempt to compile the PDF locally — just make the source edits and verify via grep.

---

## Skills to Load FIRST (Mandatory)

Before doing ANY work, invoke these skills in order:

```
1. Skill tool → skill: "andrej-karpathy-skills:karpathy-guidelines"
   WHY: Think before coding. Surgical changes only. Don't touch adjacent text.

2. Skill tool → skill: "superpowers:test-driven-development"  
   WHY: For each edit — grep to confirm current state → apply edit → grep to confirm new state.
```

---

## File Paths (All Absolute — Copy-Paste Ready)

| Short name | Full path |
|---|---|
| **results.tex** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex` |
| **discussion.tex** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex` |
| **abstract.tex** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex` |
| **appendices.tex** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex` |
| **references.bib** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib` |
| **main.tex** | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex` |
| **Project root** | `/home/samyak/Desktop/parbench_sam` |
| **Python venv** | `source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate` |

---

## Critical Context: Verified Ground-Truth Numbers

These numbers were computed on 2026-05-05 by parsing every JSON file in `results/evaluation/{model}/*.json` using the `EXCLUDED_SPECS` filter from `harness/constants.py` and the Chen et al. (2021) pass@k estimator. They are CORRECT:

| Metric | Qwen 3.5 | GPT-5.4 | Codex |
|--------|-----------|---------|-------|
| L0 tasks | 142 | 142 | 142 |
| L0 records (3 samples/task) | 426 | 426 | 426 |
| pass@1 (macro-avg) | 23.9% | 62.7% | 62.7% |
| pass@3 (macro-avg) | 35.2% | 69.7% | 68.3% |
| Hard-fail tasks (0/3 PASS) | 64.8% | 30.3% | 31.7% |
| All-pass tasks (3/3 PASS) | 13.4% | 53.5% | 57.0% |
| L0-conditional subset size | 50/142 | 99/142 | 97/142 |
| Augmentation L1 | 74.0% (37/50) | 88.9% (88/99) | 86.6% (84/97) |
| Augmentation L2 | 64.0% (32/50) | 90.9% (90/99) | 88.7% (86/97) |
| Augmentation L3 | 62.0% (31/50) | 86.9% (86/99) | 86.6% (84/97) |
| Augmentation L4 | 56.0% (28/50) | 90.9% (90/99) | 85.6% (83/97) |
| Augmentation range L1–L4 | 56.0%–74.0% | **86.9%–90.9%** | 85.6%–88.7% |

**KEY FINDING:** The paper INCORRECTLY claims "85.6%–88.7%" applies to BOTH GPT-5.4 and Codex. In reality, that range is Codex-only. GPT-5.4's actual range is 86.9%–90.9% (higher).

---

## EXECUTION PLAN: 10 Corrections in Order

### Correction 1: Section 5.5 — Augmentation Wording (FACTUAL ERROR + Missing Sizes)

**Priority:** P1-4 (high — factual inaccuracy + causal overstatement + missing data)

**File:** `results.tex` line 148

**What's wrong:**
1. Opens with "To assess whether baseline success is driven primarily by surface-form memorization" — this is causal language but the design is descriptive
2. Claims "85.6%–88.7%" for both Codex AND GPT-5.4 — but GPT-5.4 is actually 86.9%–90.9%
3. Missing the L0-conditional subset sizes (n=50, 99, 97)

**FIND this exact text (it is one paragraph starting at line 148):**
```
To assess whether baseline success is driven primarily by surface-form memorization, we evaluated augmented source variants (L1--L4) on L0-conditional subsets (detailed in Appendix~\ref{sec:appendix-e4}). \codex{} shows the same plateau pattern as \gptnew{}: 85.6\%--88.7\% at L1--L4, in contrast to \qwenshort{}'s monotonic decline from 74.0\% at L1 to 56.0\% at L4 on the same L0-conditional design. This stability across both GPT models is compatible with robustness to the tested surface-form perturbations. These results are descriptive rather than confirmatory given the L0-conditional design; survivorship bias prevents ruling out deeper structural memorization entirely.
```

**REPLACE WITH:**
```
To assess sensitivity to surface-form perturbation, we evaluated L1--L4 augmented variants on model-specific L0-conditional subsets: \qwenshort{} $n{=}50/142$, \gptnew{} $n{=}99/142$, \codex{} $n{=}97/142$ (detailed in Appendix~\ref{sec:appendix-e4}). \gptnew{} maintains 86.9\%--90.9\% across L1--L4; \codex{} shows a similar plateau at 85.6\%--88.7\%. In contrast, \qwenshort{} declines monotonically from 74.0\% at L1 to 56.0\% at L4. This stability in the GPT-family models indicates lower sensitivity to the tested source-level perturbations. These results are descriptive because the filter depends on L0 success and each augmented level uses one sample per qualifying pair; survivorship bias prevents ruling out deeper structural memorization.
```

**Verification:**
```bash
grep -n "driven primarily by surface-form memorization" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: zero results (old text gone)

grep -n "86.9" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: one result at line 148 (new text present)
```

---

### Correction 2: Figure 2 Caption — "all directions" → "eight displayed"

**Priority:** P1-2

**File:** `results.tex` line 121

**What's wrong:** Caption says "across all directions" but the heatmap shows only 8 of 10 total directions (missing OMP→OMP-target and OMP-target→OMP).

**FIND:**
```
\caption{Per-kernel translation status across all directions and three models (L0, first sample per task, 35~kernels $\times$ up to 8~directions). All-grey rows denote kernels with only \knownfail{} or phantom specs.}
```

**REPLACE WITH:**
```
\caption{Per-kernel translation status across the eight displayed directions and three models (L0, first sample per task). The two remaining OMP-target case-study directions (OMP$\to$OMP-target, OMP-target$\to$OMP) are omitted from this heatmap for readability. All-grey rows denote kernels with only \knownfail{} or phantom specs.}
```

**Verification:**
```bash
grep -n "across all directions" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: zero results
```

---

### Correction 3: Table 3 Caption — "n" Ambiguity

**Priority:** P1-3

**File:** `results.tex` line 90

**What's wrong:** "Here $n$ denotes total L0 records" is ambiguous — reader might think it's total across all 3 models. It's actually per model (e.g., n=72 means 24 tasks × 3 samples for ONE model).

**FIND:**
```
Here $n$ denotes total L0 records. Wilson 95\% CIs in brackets.}
```

**REPLACE WITH:**
```
Here $n$ denotes L0 records per model for that direction. Wilson 95\% CIs in brackets.}
```

**Verification:**
```bash
grep -n "denotes.*L0 records" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: shows "L0 records per model"
```

---

### Correction 4: Checklist Item 1 — False Attestation About Abstract

**Priority:** P0-3 (CRITICAL — the checklist is a formal author attestation)

**File:** `appendices.tex` line 2374

**What's wrong:** Says "The abstract states L0 pass rates..." but the current abstract contains NO numbers. This is a false claim in a formal NeurIPS checklist.

**FIND:**
```
\item[] Justification: The abstract states L0 pass rates (Qwen 23.9\%, GPT-5.4 62.7\%, \codex{} 62.7\%), failure taxonomy percentages, and augmentation robustness findings, all verified against raw result files (Section~\ref{sec:results}). Claims are scoped to the three models evaluated.
```

**REPLACE WITH:**
```
\item[] Justification: The abstract and introduction define the benchmark contribution and scope, while Section~\ref{sec:results} reports L0 pass@1/pass@3 results (Qwen 23.9\%/35.2\%, GPT-5.4 62.7\%/69.7\%, \codex{} 62.7\%/68.3\%), failure taxonomy, direction asymmetry, and augmentation findings. All numerical claims are verified against raw result JSONs. Claims are scoped to the three evaluated models, declared-oracle PASS, and the tested L0/L0-conditional protocols.
```

**Verification:**
```bash
grep -n "The abstract states L0 pass rates" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Expected: zero results (old text gone)

grep -n "abstract and introduction define" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Expected: one result (new text present)
```

---

### Correction 5: Discussion — Compact Synthesis + Fix Anti-Conservative Phrasing

**Priority:** P0-1 (page budget) + P1-5 (statistics-heavy) + P1-6 (anti-conservative chi-squared)

**File:** `discussion.tex` line 6

**What's wrong:**
1. The discussion's first paragraph is too dense with statistics (contributes to page overrun)
2. "confirms significant model differences" is too strong — records share tasks (3 samples/task), making chi-squared anti-conservative
3. Full McNemar/Fisher/effect-size detail belongs in appendix, not main text

**FIND (this is a single long line in the file — line 6):**
```
\parbench{} establishes that LLMs can perform non-trivial parallel code translation when evaluation isolates the kernel and uses executable declared-oracle checks, surfacing three structural properties: strong direction dependence (CUDA-to-OpenMP passes at 40--83\% while OpenCL-to-CUDA yields 0--19.3\%), build-stage API adaptation as the dominant failure mode, and preliminary robustness to surface-form augmentation. An omnibus chi-squared test on 1,278 balanced L0 records confirms significant model differences ($\chi^2(2) = 170.43$, $p < 10^{-37}$, Cram\'{e}r's $V = 0.365$), with pairwise analysis revealing two tiers: \gptnew{} and \codex{} achieve identical pass rates (267/426; Fisher's $p = 1.0$, Cohen's $h = 0.00$; McNemar: 94 both-pass, 40 both-fail, 5/3 discordant), while both surpass \qwenshort{} by $5.3\times$ odds (Cohen's $h = 0.80$). Because the providers use unmatched sampling conditions (Section~\ref{sec:sampling-config}), the Qwen--GPT gap cannot be causally attributed to model capability alone; the within-provider comparison controls for this confound.
```

**REPLACE WITH:**
```
\parbench{} shows that, when repository reconstruction is fixed, current LLMs can produce declared-oracle-passing translations for a non-trivial fraction of kernel-level parallel API tasks, but success remains highly structured by API direction, failure stage, and model tier. The primary bottleneck is build-stage API adaptation, especially when translations must introduce explicit device-memory and runtime structure. A record-level descriptive omnibus test on 1,278 balanced L0 records ($\chi^2(2) = 170.43$, $p < 10^{-37}$) detects significant heterogeneity; pairwise analysis reveals two tiers: \gptnew{} and \codex{} achieve identical pass rates (267/426; Fisher's $p = 1.0$), while both surpass \qwenshort{} by $5.3\times$ odds (Cohen's $h = 0.80$). Because the providers use unmatched sampling conditions (Section~\ref{sec:sampling-config}), the Qwen--GPT gap cannot be causally attributed to model capability alone; the within-provider comparison controls for this confound. Full pairwise statistical details appear in Appendix~\ref{sec:appendix-e4}.
```

**Verification:**
```bash
grep -n "establishes that LLMs can perform" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
# Expected: zero results

grep -n "detects significant heterogeneity" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
# Expected: one result at line 6
```

---

### Correction 6: Discussion — Wrong Appendix Pointer (P1-7)

**Priority:** P1-7

**File:** `discussion.tex` line 10 (in the Limitations paragraph)

**What's wrong:** Text says `Appendix~\ref{sec:appendix-k}` provides "per-record model outputs" — but `sec:appendix-k` is the Evaluation Card. The per-record outputs are described in the artifact section (`sec:artifact-availability`).

**FIND:**
```
Appendix~\ref{sec:appendix-k} provides a structured Evaluation Card, reporting protocol, and per-record model outputs that support reproduction and extension of the benchmark.
```

**REPLACE WITH:**
```
Appendix~\ref{sec:appendix-k} provides a structured Evaluation Card and reporting protocol; the artifact (Section~\ref{sec:artifact-availability}) documents per-record outputs that support reproduction and extension.
```

**Verification:**
```bash
grep -n "per-record model outputs" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
# Expected: zero results (old text gone)
```

---

### Correction 7: Bibliography Duplicates (P1-8)

**Priority:** P1-8

**File:** `references.bib` AND `appendices.tex`

**What's wrong:** Two pairs of duplicate bibliography entries:
- `OMPify2023` and `OpenMPGraphTransformer2023` = same IWOMP 2023 paper
- `HPCorpus2023` and `QuantifyingOpenMP2023` = same IEEE HPEC 2023 paper (same DOI)

**STEP 7A — Replace citations FIRST (before deleting bib entries):**

In `appendices.tex`:
- Line 369: `\cite{OpenMPGraphTransformer2023}` → `\cite{OMPify2023}`
- Line 570: In the citation list `...,OMPify2023,OpenMPGraphTransformer2023,...` → remove `,OpenMPGraphTransformer2023`
- Line 570: `\cite{QuantifyingOpenMP2023}` → `\cite{HPCorpus2023}`

**Verification after citation replacement:**
```bash
grep -rn "OpenMPGraphTransformer2023\|QuantifyingOpenMP2023" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/*.tex /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Expected: zero results
```

**STEP 7B — Delete duplicate bib entries:**

In `references.bib`, delete the entire `@inproceedings{OpenMPGraphTransformer2023,...}` block AND the entire `@inproceedings{QuantifyingOpenMP2023,...}` block.

**Verification:**
```bash
grep -n "OpenMPGraphTransformer2023\|QuantifyingOpenMP2023" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib
# Expected: zero results
```

---

### Correction 8: Abstract — "semantics-preserving" Qualifier (P2-3)

**Priority:** P2-3

**File:** `abstract.tex` line 4

**What's wrong:** Says "AST-driven semantics-preserving source augmentation" without qualifier, but 7 omp_target augmented variants fail baseline validation at high intensity. "Baseline-validated" is the factually precise term.

**FIND:**
```
AST-driven semantics-preserving source augmentation
```

**REPLACE WITH:**
```
AST-driven, baseline-validated source augmentation
```

**Verification:**
```bash
grep -n "semantics-preserving" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex
# Expected: zero results
```

---

### Correction 9: Table 2 Float Placement (P1-1)

**Priority:** P1-1

**File:** `main.tex` line 27 (preamble) AND `results.tex` line 44

**What's wrong:** Table 2 (tab:overall-pass) floats above the "Results" heading in the PDF, contradicting the narrative order where pass@k should come first.

**STEP 9A — Add package to preamble:**

In `main.tex`, insert after line 27 (`\usepackage{pdflscape}`):
```latex
\usepackage{placeins}
```

**STEP 9B — Add float barrier:**

In `results.tex`, insert a new line immediately BEFORE line 44 (`\section{Results}`):
```latex
\FloatBarrier
```

**Verification:**
```bash
grep -n "placeins" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex
# Expected: one result

grep -n "FloatBarrier" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: one result, immediately before \section{Results}
```

---

### Correction 10: Table 2 vs Cost Table Denominator Note (P2-5)

**Priority:** P2-5

**File:** `results.tex` line 70 (the `\caption{...}` of `tab:overall-pass`)

**What's wrong:** Table 2 totals 2,262 valid records; Appendix J cost table reports 2,344 tasks evaluated. No explanation for the discrepancy (82 Qwen KNOWN_FAIL records were excluded post-hoc).

**FIND (end of the existing caption, just before the closing `}`):**
```
inferential comparison uses the balanced 142 L0 pairs in Section~\ref{sec:passk-analysis}.}
```

**REPLACE WITH:**
```
inferential comparison uses the balanced 142 L0 pairs in Section~\ref{sec:passk-analysis}. The 2,262 total reflects valid analysis records after excluding 82 \qwenshort{} records involving \knownfail{} specs; the Appendix~\ref{sec:appendix-j} cost table reports 2,344 API calls including those subsequently excluded.}
```

**Verification:**
```bash
grep -n "2,344" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# Expected: one result in the Table 2 caption
```

---

## Corrections NOT Needed (Verified Correct in Current Paper)

These were checked against raw data and are already accurate — do NOT change them:

- pass@1 = 23.9% / 62.7% / 62.7% ✓
- pass@3 = 35.2% / 69.7% / 68.3% ✓
- Table 2 totals: 230/626, 621/822, 604/814 ✓
- Table 3 all 10 direction rows ✓
- Hard-fail / all-pass percentages ✓
- OR = 5.3×, Cohen's h = 0.80 ✓
- 142 tasks, 426 records per model ✓
- Qwen augmentation decline 74.0% → 56.0% ✓
- Figure 3 failure taxonomy caption (6 standard directions, 120 tasks) ✓
- Section 5.1 pass@k paragraph — all numbers correct ✓

---

## What Was NOT Fixed Here (User Must Handle Separately)

| Issue | Why it's deferred |
|---|---|
| P0-2: Unresolved "??" references (page 16, page 46) | Requires Overleaf compilation to diagnose which `\label{}` is missing. After applying all edits, do a clean build and search for "??" in the PDF. |
| P0-1: Full page budget (need to fit in 9 pages) | The Discussion edit (Correction 5) saves ~2 lines. The remaining ~0.5 page cut likely requires shortening Figure 1 caption and/or moving more text to appendix. User must visually check after compilation. |
| P0-4: ED style option verification | User must confirm `\usepackage[eandd]{neurips_2026}` is in the preamble (NOT `[final]` or `[preprint]`). |
| P2-6: ParBench/PARBENCH capitalization | Currently mixed (title = "ParBench", body = `\parbench{}` macro). Acceptable as-is. |
| P1-9: Artifact archive testing | Cannot be done in code — user must unzip and smoke-test the archive before upload. |

---

## Execution Order (Strict Dependencies)

```
Correction 7A (replace citations) ──→ Correction 7B (delete bib entries)
                                        ↑ must be sequential
All other corrections (1-6, 8-10) are INDEPENDENT of each other
```

**Recommended order for a single-pass session:**
1. Corrections 1, 2, 3 (all in results.tex — do together)
2. Correction 4 (appendices.tex)
3. Corrections 5, 6 (discussion.tex — do together)
4. Correction 7A then 7B (appendices.tex + references.bib)
5. Correction 8 (abstract.tex)
6. Correction 9A, 9B (main.tex + results.tex)
7. Correction 10 (results.tex)

---

## Final Verification (Run After All Edits)

```bash
# 1. Check no old text remains
grep -n "driven primarily by surface-form memorization" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "across all directions" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "The abstract states L0 pass rates" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
grep -n "establishes that LLMs can perform" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
grep -n "per-record model outputs" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
grep -n "OpenMPGraphTransformer2023\|QuantifyingOpenMP2023" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib
grep -n "semantics-preserving" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex
# ALL of the above must return zero results

# 2. Check new text is present
grep -n "86.9" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "eight displayed directions" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "records per model" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "abstract and introduction define" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
grep -n "detects significant heterogeneity" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex
grep -n "baseline-validated" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex
grep -n "FloatBarrier" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep -n "2,344" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
# ALL must return exactly one result each
```

---

## What Worked in This Research Session

- Parsed ALL 2,262 result JSONs directly (no reliance on summary files)
- Used the exact same `EXCLUDED_SPECS` filter and Chen estimator as the official analysis script
- Confirmed 142 tasks per model after exclusion
- Caught the GPT-5.4 augmentation range error (86.9%–90.9% ≠ 85.6%–88.7%)
- Verified correct LaTeX labels by grepping appendices_neurips.tex: `sec:appendix-k` = Eval Card, `sec:appendix-j` = Cost/Config, `sec:artifact-availability` = Artifact section
- Confirmed the Figure 2 heatmap shows 8 directions (not "all" 10)

## What Didn't Work / Traps to Avoid

- Do NOT try to compile LaTeX locally — user uses Overleaf
- Do NOT change numbers that are already correct (see the "Verified Correct" list)
- Do NOT delete bib entries before updating their citations in .tex files
- Do NOT use `sed -i` for multi-line replacements in LaTeX — use the Edit tool with exact string matching
- Line numbers may have shifted if the previous ablation→augmentation handoff was executed — use TEXT ANCHORS (the exact strings in FIND blocks) to locate edits, not line numbers alone
