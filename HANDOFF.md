# HANDOFF: Fix NeurIPS Paper Audit Issues

**Date:** 2026-05-04
**Status:** Plan complete with exact text patches. Ready for execution.
**Previous handoff (superseded):** Artifact packaging task (2026-05-01)

---

## What This Task Is About (Plain English)

ParBench is a benchmark that tests whether AI models can translate parallel code between GPU/CPU programming languages (CUDA, OpenMP, OpenCL). We wrote a research paper for NeurIPS 2026 Evaluations & Datasets track.

An external reviewer audited the paper PDF and found ~20 issues: text errors, statistical overclaims, compliance risks with the NeurIPS submission rules, and polish defects. We spent a session verifying EVERY finding against the actual LaTeX source code, raw result data (2,344 JSON files), and analysis scripts.

**Your job:** Apply 8 specific, verified text fixes to the LaTeX paper source. Every fix has exact "old text" and "new text" ready to paste. No new experiments, no code changes, no data re-analysis needed.

**Why this matters:** The NeurIPS submission deadline is May 6, 2026 (AoE). These fixes prevent desk-rejection and reduce reviewer objections.

---

## Skills to Load First

Before doing ANY work, load these two skills:

1. **`andrej-karpathy-skills:karpathy-guidelines`** — Surgical changes, think before editing, simplicity first.
2. **`test-driven-development`** — Adapted for LaTeX: write the grep "test" first, confirm it shows the bug, apply the fix, confirm the bug is gone.

---

## Critical Context You Must Know

### Project Root
`/home/samyak/Desktop/parbench_sam`

### Paper Directory
`/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/`

### How to Compile the Paper
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version && latexmk -pdf main_neurips.tex
```

### How to Undo Everything If Something Goes Wrong
```bash
cd /home/samyak/Desktop/parbench_sam && git checkout -- docs/paper/NeurIPS_ready_version/
```

### Which Files Are Compiled Into the PDF

`main_neurips.tex` includes these files in this order:

| Include Order | File | Contains |
|---------------|------|----------|
| 1 | `sections/macros.tex` | Macro definitions (`\qwenshort` = Qwen 3.5, `\gptnew` = GPT-5.4, `\codex` = GPT-5.3-codex, `\parbench` = ParBench) |
| 2 | `sections/abstract.tex` | Abstract |
| 3 | `sections/1-introduction.tex` | Introduction + contributions |
| 4 | `sections/framework.tex` | Spec design, augmentation engine, harness |
| 5 | `sections/benchmark-curation.tex` | Survey-based curation |
| 6 | `sections/experimental-setup.tex` | Models, protocol, metrics |
| 7 | `sections/results.tex` | All results subsections + tables + figures |
| 8 | `sections/discussion.tex` | Discussion, limitations |
| 9 | `references.bib` | Bibliography |
| 10 | `appendices_neurips.tex` | All appendices + NeurIPS checklist |

### DEAD CODE FILE — DO NOT EDIT
**`sections/related-work.tex` is NOT compiled.** Line 138 of `main_neurips.tex` says `% \input{sections/related-work}` (commented out). The related-work section lives inline in `appendices_neurips.tex:13-20`. Several audit findings target this dead file. **Ignore them.**

### Page Budget
NeurIPS E&D allows 9 pages main content + unlimited references/appendix. The paper is already at the limit. Be word-conscious when adding text.

---

## What Was Already Verified (Don't Re-Check)

### All Paper Numbers Are Correct

| Claim in Paper | Verified Against Raw Data | Status |
|----------------|--------------------------|--------|
| Qwen pass@1 = 23.9% | 142 tasks after KNOWN_FAIL exclusion from 504 raw L0 records | CORRECT |
| GPT-5.4 pass@1 = 62.7% | 267/426 L0 records | CORRECT |
| Codex pass@1 = 62.7% | 267/426 L0 records | CORRECT |
| Table 1 totals: 626/822/814 records | File counts in `results/evaluation/{model}/` | CORRECT |
| Figure caption: "120 non-KNOWN_FAIL tasks" | 120 std-direction tasks after KF exclusion | CORRECT |
| Oracle strength: 2 strong, 5 medium, 46 weak | `grep oracle_strength specs/*.json` | CORRECT |
| SwapCondition code: `<` maps to `>` | `c_augmentation/augment_dataset.py:733` SWAP_MAP | CORRECT |

### Audit Issues Already Resolved (No Action Needed)

| Audit Finding | Why It's Not a Problem |
|---------------|----------------------|
| Hyperref colored link boxes | Already fixed: `main_neurips.tex:22` has `\hypersetup{hidelinks}` |
| "Appendix 2" reference | Not in any compiled file |
| Figure says "137 tasks" | Current caption correctly says "120" |
| "Chen et al. Chen et al." text | Not in any compiled file |
| Kadosh IWOMP duplicate bib entry | OMPify2023 and LearningToParallelize2023 are different papers with different titles |
| Orphan "extension beyond" related-work text | Only in `related-work.tex` which is NOT COMPILED (dead code) |
| "Demonstrate more robust parallel reasoning" | Only in `related-work.tex` (dead code); not in any compiled file |
| Duplicate PCEBench bib key `chen2025pcebench` | Only cited in dead code; active key is `PCEBench2025` |

### NeurIPS Croissant Requirement — Researched
Per the [NeurIPS 2026 E&D Hosting Guidelines](https://neurips.cc/Conferences/2026/EvaluationsDatasetsHosting): Croissant metadata is required ONLY for dataset submissions. The guidelines explicitly state: "If your contribution is an executable environment/codebase rather than a static dataset, there is no need for dataset hosting." ParBench is an executable benchmark tool, so Croissant is not required.

---

## The 8 Fixes to Apply

### User Decision Already Made
- **Abstract**: Add pass@1 numbers to the abstract (Option A chosen by user)

### Edit Ordering Rule
Within each file, apply fixes from the **highest line number first** (bottom-up) so earlier edits don't shift line numbers of later fixes.

---

### Fix A: Correct condition-swap math error

| Field | Value |
|-------|-------|
| **File** | `sections/framework.tex` |
| **Line** | 69 |
| **Priority** | P0 (technical error visible to reviewers) |
| **Problem** | Says `a < b` is equivalent to `b >= a`. Mathematically wrong: `a < b` is equivalent to `b > a` (they differ when `a == b`). The correct form already appears on line 71. The code (`c_augmentation/augment_dataset.py:733`) correctly maps `<` to `>`. |

**Before-test** (should find the bug):
```bash
grep "b >= a" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/framework.tex
```

**Old text:**
```
\texttt{b >= a}
```

**New text:**
```
\texttt{b > a}
```

**After-test** (should return nothing):
```bash
grep "b >= a" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/framework.tex
```

---

### Fix B: Soften "demonstrating" overclaim + add diagnostic note to Table 1 caption

| Field | Value |
|-------|-------|
| **File** | `sections/results.tex` |
| **Lines** | 53 and 68 |
| **Priority** | P1 (overclaim + misleading framing) |
| **Problem** | Line 53 uses "demonstrating that repository reconstruction...is the primary obstacle" — too causal without a controlled ablation. Table 1 caption (line 68) should clarify it's a diagnostic summary, not the primary balanced comparison. |

**Apply patch 2 FIRST (line 68, higher line number), then patch 1 (line 53).**

**Patch 2 — Table 1 caption (line 68):**

**Old text:**
```
\knownfail{} specs were pre-excluded from both GPT evaluation batches.}
```

**New text:**
```
\knownfail{} specs were pre-excluded from both GPT evaluation batches. Because augmentation subsets differ by model, this table is a diagnostic summary; the balanced task-level comparison is Table~\ref{tab:direction-rates} and pass@$k$ in Section~\ref{sec:passk-analysis}.}
```

**Patch 1 — Overclaim (line 53):**

**Old text:**
```
---demonstrating that repository reconstruction, not translation itself, is the primary obstacle in full-application benchmarks.
```

**New text:**
```
---supporting the interpretation that repository reconstruction, not translation itself, is a major obstacle in full-application benchmarks.
```

**After-test:**
```bash
grep "supporting the interpretation" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
grep "diagnostic summary" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
```

---

### Fix C: Qualify augmentation p-values as descriptive

| Field | Value |
|-------|-------|
| **File** | `sections/results.tex` |
| **Line** | 134 |
| **Priority** | P1 (statistical overclaim under survivorship-biased design) |
| **Problem** | Uses formal p-values for a design with acknowledged survivorship bias. Should label as descriptive. |

**Old text:**
```
This stability across both GPT models is compatible with robustness to surface-form perturbation, though survivorship bias (L0-conditional filtering) prevents ruling out deeper structural memorization entirely.
```

**New text:**
```
This stability across both GPT models is compatible with robustness to surface-form perturbation. These tests are descriptive rather than confirmatory given the L0-conditional design; survivorship bias prevents ruling out deeper structural memorization entirely.
```

**After-test:**
```bash
grep "descriptive rather than confirmatory" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex
```

---

### Fix D: Add oracle-strength caveat to main text

| Field | Value |
|-------|-------|
| **File** | `sections/experimental-setup.tex` |
| **Insert after** | Line 94 (end of "Metrics" paragraph, after `Full metric derivations are in Appendix~\ref{sec:appendix-a-extended}.`) |
| **Priority** | P1 (oracle weakness buried in appendix) |
| **Problem** | Oracle limitations are only in Discussion/Appendix L. Reviewers may not see the caveat. |

**Before-test** (should find nothing — caveat doesn't exist yet):
```bash
grep "Oracle strength" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex
```

**Text to INSERT after line 94:**
```latex

\textbf{Oracle strength.}
\pass{} denotes successful build, execution, and satisfaction of the declared
verification oracle---not a proof of full semantic equivalence. Of the 87 eval-eligible
specs, 2 use file-hash verification, 5 use numeric comparison, and 46 use
stdout-pattern plus exit-code checks; the remainder are untagged. We therefore
interpret pass rates as \emph{declared-oracle correctness} and report oracle
limitations explicitly in Section~\ref{sec:discussion} and
Appendix~\ref{sec:appendix-k}.
```

**After-test:**
```bash
grep "Oracle strength" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex
```

**PAGE CHECK:** This adds ~55 words. After applying, recompile and verify the main body still fits in 9 pages. If it overflows, shorten the last sentence of the existing Metrics paragraph (line 94) to compensate.

---

### Fix E: Add pass@1 numbers to abstract

| Field | Value |
|-------|-------|
| **File** | `sections/abstract.tex` |
| **Line** | 4 (last sentence of abstract) |
| **Priority** | P0 (checklist claims abstract has numbers; it currently doesn't) |
| **Decision** | User chose Option A — add numbers to abstract |

**Old text** (the last sentence, starting with "We further"):
```
We further evaluate \parbench{} on state-of-the-art open and proprietary LLMs, showing that it exposes persistent barriers to reliable parallel code translation, including direction asymmetry, multi-file coordination, incomplete API adaptation, and uneven robustness to source-level perturbations.
```

**New text:**
```
We evaluate \parbench{} on three state-of-the-art LLMs: pass@1 ranges from 23.9\% (\qwenshort{}) to 62.7\% (\gptnew{} and \codex{}) across 142 L0 translation tasks under stochastic sampling, exposing persistent barriers including direction asymmetry, multi-file coordination, incomplete API adaptation, and uneven robustness to source-level perturbations.
```

**After-test:**
```bash
grep "23.9" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex
```

---

### Fix F: Fix Croissant/artifact language

| Field | Value |
|-------|-------|
| **File** | `appendices_neurips.tex` |
| **Line** | 326 |
| **Priority** | P0 (compliance risk for E&D track) |
| **Problem** | Says "Croissant export...is planned as a post-acceptance extension." Per NeurIPS 2026 hosting guidelines, Croissant is not required for executable tools. |

**Old text:**
```
A datasheet following \citet{Datasheets2021} and a JSON schema accompany the release; Croissant export for ML dataset registries is planned as a post-acceptance extension.
```

**New text:**
```
A datasheet following \citet{Datasheets2021} and a JSON schema accompany the release. Because \parbench{} is an executable evaluation tool rather than a static dataset, Croissant metadata is not applicable per the NeurIPS 2026 hosting guidelines; structured metadata is instead provided via the JSON specification schema and the accompanying datasheet.
```

**After-test:**
```bash
grep "post-acceptance extension" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Should return nothing
grep "not applicable per" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Should match
```

---

### Fix G: Fix NeurIPS checklist claims

| Field | Value |
|-------|-------|
| **File** | `appendices_neurips.tex` |
| **Lines** | 2116 and 2126 |
| **Priority** | P1 |

**Apply from highest line first.**

**Fix G1 — Line 2126 (ethics):**

**Old text:**
```
The work evaluates publicly available benchmark code using commercial LLM APIs. No human subjects, private data, or dual-use concerns.
```

**New text:**
```
The work evaluates publicly available benchmark code using commercial LLM APIs. No human subjects or private data are involved. No immediate high-risk dual-use concern beyond general automated coding capabilities; all benchmarks are public HPC kernels under open-source licenses.
```

**Fix G2 — Line 2116 (error bars):**

**Old text:**
```
All pass rates include Wilson 95\% confidence intervals.
```

**New text:**
```
Per-record pass rates include Wilson 95\% confidence intervals; task-level pass@$k$ uses normal-approximation CIs on macro-averaged per-task probabilities.
```

---

### Fix H (OPTIONAL, P2): Remove orphan bib entry

| Field | Value |
|-------|-------|
| **File** | `references.bib` |
| **Lines** | 34-41 |
| **Priority** | P2 (dead code cleanup, zero risk) |
| **Problem** | `chen2025pcebench` entry is only cited in the dead `related-work.tex`. Harmless but cluttered. |

Delete lines 34-41 (the entire `@inproceedings{chen2025pcebench,...}` block). Verify it's not cited in any compiled file first:

```bash
grep -rn "chen2025pcebench" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/1-introduction.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/framework.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/benchmark-curation.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex \
  /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Must return 0 results before deleting
```

---

## Recommended Execution Order

1. Fix A (framework.tex) — standalone, no dependencies
2. Fix C (results.tex:134) — higher line, do before Fix B
3. Fix B (results.tex:53 and :68) — two patches, apply :68 first
4. Fix D (experimental-setup.tex) — new text insertion
5. Fix E (abstract.tex) — new numbers
6. Fix F (appendices_neurips.tex:326) — Croissant language
7. Fix G (appendices_neurips.tex:2126 then :2116) — checklist
8. Fix H (references.bib) — optional cleanup

After ALL fixes: **full compilation + verification checklist** (below).

---

## Final Verification Checklist

Run this AFTER all fixes are applied:

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version

# 1. Compile
latexmk -pdf main_neurips.tex 2>&1 | tail -5

# 2. Check for warnings
grep "multiply defined\|undefined reference\|Overfull" main_neurips.log | head -10

# 3. Page count
pdfinfo main_neurips.pdf | grep Pages

# 4. All bugs gone
grep "b >= a" sections/framework.tex                         # EMPTY
grep "demonstrating that repository" sections/results.tex    # EMPTY
grep "post-acceptance extension" appendices_neurips.tex      # EMPTY

# 5. All fixes present
grep "b > a" sections/framework.tex                          # 2 matches
grep "supporting the interpretation" sections/results.tex    # 1 match
grep "diagnostic summary" sections/results.tex               # 1 match
grep "descriptive rather than confirmatory" sections/results.tex  # 1 match
grep "Oracle strength" sections/experimental-setup.tex       # 1 match
grep "23.9" sections/abstract.tex                            # 1 match
grep "not applicable per" appendices_neurips.tex             # 1 match

# 6. Visual spot-check: open main_neurips.pdf and verify:
#    - Abstract has pass@1 numbers
#    - Section 4 has "Oracle strength" paragraph
#    - Table 1 caption ends with "diagnostic summary"
#    - No colored link boxes anywhere
#    - Main body fits in 9 pages
```

---

## What Worked in This Research Session

- **Cross-checking audit claims against raw data**: Every number was verified by loading result JSONs and computing independently. All paper numbers are correct.
- **Checking which files are actually compiled**: The plan-reviewer agent caught that `related-work.tex` is dead code, saving the new session from editing a file that doesn't affect the PDF.
- **Web-searching NeurIPS 2026 requirements**: Discovered Croissant is NOT required for executable benchmark tools, which changes the Croissant fix from "include it now" to "explain why it's not applicable."
- **Adversarial plan review**: The plan-reviewer agent found 6 critical issues in the first draft of the plan (dead code fixes marked as P0, missing concrete patches, no edit ordering, no page-count check).

## What Didn't Work / Traps to Avoid

- **Don't trust the audit's file references blindly**: The audit was based on a PDF version. Several issues (orphan related-work text, "137 tasks", duplicate references) were either already fixed or target files that aren't compiled.
- **Don't edit `sections/related-work.tex`**: It's dead code. The audit flagged 3 issues in this file. All are phantom.
- **Don't search for "Chen et al. Chen et al."**: This duplicate text doesn't exist in the current compiled source.
- **Don't change the Safeguards checklist from N/A to Yes**: The NeurIPS question specifically asks about "responsible release of data or models." ParBench releases neither a model nor a novel dataset; N/A is defensible. Just strengthen the justification.

---

## Summary Table

| Fix | File | Line(s) | Priority | What Changes |
|-----|------|---------|----------|--------------|
| A | framework.tex | 69 | P0 | `b >= a` → `b > a` |
| B | results.tex | 53, 68 | P1 | "demonstrating" → "supporting the interpretation" + "diagnostic summary" in caption |
| C | results.tex | 134 | P1 | Add "descriptive rather than confirmatory" |
| D | experimental-setup.tex | after 94 | P1 | Insert oracle-strength paragraph (~55 words) |
| E | abstract.tex | 4 | P0 | Add pass@1 numbers to abstract |
| F | appendices_neurips.tex | 326 | P0 | Replace Croissant "planned" with NeurIPS exemption |
| G | appendices_neurips.tex | 2126, 2116 | P1 | Fix ethics + error-bars checklist |
| H | references.bib | 34-41 | P2 | Delete orphan bib entry (optional) |
