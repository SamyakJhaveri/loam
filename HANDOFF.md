# HANDOFF: NeurIPS 2026 Paper Completion

**Date:** 2026-04-27 (updated after Phase 3-5 session)
**Deadline:** NeurIPS 2026 — May 1, 2026 (3 days remaining)
**Status:** Phases 0-5 COMPLETE. Review sim findings need addressing (P0 items). Validate + commit remain.

---

## What Is This Document?

Single execution plan for completing the NeurIPS 2026 paper. Every path is absolute, every command is copy-paste ready, every number is verified against raw data files.

---

## What Has Been Done

### Prior Session (2026-04-25): Structural Rewrite
- Modularized LaTeX into 9 section files via `\input{}`
- All numbers corrected from purged dataset to canonical evaluation data
- Model swap from GPT-4.1 mini to GPT-5.4 (with `\tbd{}` placeholders)
- Self-repair narrative removed
- KNOWN_FAIL counts corrected (9 not 8, 87 PASS not 88)

### Phase 0: Overleaf Sync — DONE (2026-04-27)
User replaced local folder with Overleaf version containing Erel's review changes. Erel's edits addressed in Phase 2 below.

### Phase 1: GPT-5.4 Analysis Pipeline — DONE (2026-04-27)
All analysis scripts run, all output files model-specific (no ambiguous unsuffixed files):

| File | Model | Verified |
|------|-------|----------|
| `results/analysis/paper_data_together-qwen-3.5-397b-a17b.json` | Qwen — 102/426 L0 PASS = 23.9% | Yes |
| `results/analysis/paper_data_azure_gpt54.json` | GPT-5.4 — 267/426 L0 PASS = 62.7% | Yes |
| `results/analysis/quantitative_findings_qwen.json` + `.md` | Qwen — 708 total, 626 valid | Yes |
| `results/analysis/quantitative_findings_gpt54.json` + `.md` | GPT-5.4 — 822 total, 822 valid | Yes |
| `results/analysis/augmentation_per_kernel_matrix_together-qwen-3.5-397b-a17b.json` + `.md` | Qwen | Yes |
| `results/analysis/augmentation_per_kernel_matrix_azure-gpt-5.4.json` + `.md` | GPT-5.4 | Yes |
| `results/analysis/cross_model_comparison.json` | Both | Yes |
| `docs/paper/.../figures/f{3,4,5,6}_*_gpt.pdf` | GPT-5.4 figures | Yes |
| `docs/paper/.../figures/f7_augmentation_robustness.pdf` | Both models | Yes |
| `docs/paper/.../figures/t2_model_comparison.tex` | LaTeX table | Yes |

**IMPORTANT:** Ambiguous unsuffixed files (`quantitative_findings.json`, `paper_data.json`) were DELETED. All analysis files now have model names. Scripts updated:
- `quantitative_findings.py` now outputs `quantitative_findings_{model_slug}.json`
- `generate_paper_data.py` now requires `--output` (no default)
- `cross_model_comparison.py` default `--qwen-data` updated to model-specific filename
- `cross_model_comparison.py` reads `passk_campaign` (not empty `primary_campaign`)

### Phase 2: Update Main Body Sections — DONE (2026-04-27)
All `\tbd{}` and "in progress" removed from main body sections. Paper-claim-audit PASSED (79 claims, 0 mismatches).

| Section | Changes Made |
|---------|-------------|
| `abstract.tex` | GPT-5.4 L0 pass rate (62.7%), pass@1/pass@3 filled; "OF" caps fixed; 39.1%/4.6% attributed to Qwen; "overall" → "L0 pass rate" for GPT-5.4 clarity |
| `1-introduction.tex` | Contribution #1 truncation fixed; #3 updated with both models' pass@1; "in progress" removed; 1,448 total records |
| `experimental-setup.tex` | "in progress" → "complete"; source comments updated to model-specific filenames |
| `results.tex` | GPT-5.4 Table 1 row filled (621/822 PASS, 75.5%); direction summary row (62.7%); failure taxonomy caption updated |
| `discussion.tex` | Cross-model comparison with Chi² (128.6), Cohen's h (0.80); build fail reduction (50.0%→22.8%); limitations updated; "in progress" removed |
| `related-work.tex` | No changes needed; all 12 citations verified against references.bib |
| `framework.tex` | Erel added response extraction paragraph and updated figure caption; empty `\textbf{}.` still needs fix (Phase 3.5) |

---

## Skills to Load at Session Start

```
Skill("andrej-karpathy-skills:karpathy-guidelines")  -- Think before coding, surgical changes
Skill("ml-paper-writing")                              -- NeurIPS paper conventions
Skill("deslop")                                        -- Remove AI writing patterns
Skill("paper-claim-audit")                             -- Verify every number traces to data
Skill("paper-review-sim")                              -- Simulate NeurIPS 5-reviewer panel
Skill("cite-check")                                    -- Verify citations match references.bib
Skill("validate")                                      -- Run waves 1-3 before any git commit
```

---

## Absolute Path Reference

| Short Name | Path |
|------------|------|
| PROJECT_ROOT | `/home/samyak/Desktop/parbench_sam` |
| PAPER_DIR | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version` |
| SECTIONS | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections` |
| FIGURES | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures` |
| MAIN_TEX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex` |
| APPENDIX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex` |
| REFS_BIB | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib` |
| QF_QWEN | `/home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings_qwen.json` |
| QF_GPT | `/home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings_gpt54.json` |
| PD_QWEN | `/home/samyak/Desktop/parbench_sam/results/analysis/paper_data_together-qwen-3.5-397b-a17b.json` |
| PD_GPT | `/home/samyak/Desktop/parbench_sam/results/analysis/paper_data_azure_gpt54.json` |
| CROSS_MODEL | `/home/samyak/Desktop/parbench_sam/results/analysis/cross_model_comparison.json` |

---

## Data Ground Truth

ALL numbers verified 2026-04-27 against raw result files.

### Qwen 3.5 397B (source: QF_QWEN, PD_QWEN)

| Metric | Value |
|--------|-------|
| Files on disk | 708 |
| KNOWN_FAIL excluded | 82 |
| Valid after exclusion | 626 (426 L0 + 200 ablation) |
| L0 PASS | 102/426 = 23.9% |
| Overall (all 626) | 230/626 = 36.7% [33.1%, 40.6%] |
| pass@1 | 23.9% [17.9%, 30.0%] |
| pass@3 | 35.2% [27.3%, 43.1%] |
| Always pass (3/3) | 19 tasks (13.4%) |
| Hard fail (0/3) | 92 tasks (64.8%) |
| Noisy (1-2/3) | 31 tasks (21.8%) |
| BUILD_FAIL | 245 (39.1%) |
| RUN_FAIL | 121 (19.3%) |
| VERIFY_FAIL | 29 (4.6%) |
| EXTRACTION_FAIL | 1 (0.2%) |
| L0 BUILD_FAIL | 213/426 = 50.0% |
| Ablation qualifying pairs | 50 (35%) |

### GPT-5.4 (source: QF_GPT, PD_GPT)

| Metric | Value |
|--------|-------|
| Files on disk | 822 |
| KNOWN_FAIL excluded | 0 (pre-excluded from eval batch) |
| Valid after exclusion | 822 (426 L0 + 396 ablation) |
| L0 PASS | 267/426 = 62.7% [58.0%, 67.1%] |
| Overall (all 822) | 621/822 = 75.5% [72.5%, 78.4%] |
| pass@1 | 62.7% [55.3%, 70.0%] |
| pass@3 | 69.7% [62.1%, 77.3%] |
| Always pass (3/3) | 76 tasks (53.5%) |
| Hard fail (0/3) | 43 tasks (30.3%) |
| Noisy (1-2/3) | 23 tasks (16.2%) |
| BUILD_FAIL (all 822) | 123 (15.0%) |
| RUN_FAIL (all 822) | 43 (5.2%) |
| VERIFY_FAIL (all 822) | 32 (3.9%) |
| EXTRACTION_FAIL (all 822) | 3 (0.4%) |
| L0 BUILD_FAIL | 97/426 = 22.8% |
| Ablation qualifying pairs | 99 (69.7%) |

### Cross-Model (source: CROSS_MODEL)

| Metric | Value |
|--------|-------|
| Chi-squared | 128.6, p < 10⁻⁶ |
| Cohen's h | 0.80 (large) |
| Best GPT-5.4 direction | cuda-to-omp_target: 95.8% (Qwen 0%) |
| Hardest direction (both) | opencl-to-cuda: GPT 19.3%, Qwen 0% |

### GPT-5.4 Direction Pass Rates (L0, from PD_GPT)

| Direction | Rate | n |
|-----------|------|---|
| omp_target-to-omp | 100.0% | 9 |
| cuda-to-omp_target | 95.8% | 24 |
| omp_target-to-cuda | 95.8% | 24 |
| cuda-to-omp | 83.3% | 72 |
| omp-to-opencl | 72.5% | 51 |
| cuda-to-opencl | 59.7% | 57 |
| omp-to-cuda | 55.6% | 72 |
| omp-to-omp_target | 100.0% | 9 |
| opencl-to-omp | 41.2% | 51 |
| opencl-to-cuda | 19.3% | 57 |

### IMPORTANT: QF "overall" ≠ L0-only
- `QF_GPT > canonical > aggregate_pass_rates > overall` = 75.5% (all 822 records, L0+ablation)
- `PD_GPT > passk_campaign > overall` = 62.7% (426 L0 records only)
- For paper headline/abstract, use L0-only (62.7%). For Table 1 (which includes ablation), use 75.5%.
- Same distinction applies to failure taxonomy: QF covers all records, PD covers L0 only.

---

### Session 2026-04-27 Evening: Phases 3–5 Execution

**Phase 3 (Appendix Fixes) — DONE:**
- Pass@k table: replaced stale 38.3%/19.7%/27.5% with Qwen 23.9%/35.2% + GPT-5.4 62.7%/69.7%; added Noisy column
- Augmentation table: replaced stale rates with ablation data (Qwen L1=74%, GPT L1=88.9%); updated caption for L0-conditional design
- Per-kernel table: replaced all 31 rows from raw result files (230/626, not 272/710); verified Wilson CIs
- Source comments: all `paper_data.json` / `quantitative_findings.json` → model-specific filenames (15+ occurrences across 4 files)
- GPT-5.4 cost table added (14.9M tokens, 27.4h wall time, 822 tasks)
- framework.tex: `\textbf{}.` → `\textbf{ParBench system architecture.}`
- HeCBench 513→516 inconsistency harmonized (4 occurrences)

**Phase 4 (NeurIPS Checklist) — DONE:**
- 16-item checklist added to appendices_neurips.tex using `\answerYes`/`\answerNA` macros
- All `\ref{}` targets verified

**Phase 5 (Final Pass) — DONE:**
- Stale-data sweep: 0 hits across all sections
- TBD/in-progress: 0 (only macros.tex definition)
- Citation check: 18/18 OK (added RSBench2014 to references.bib)
- Dangling refs: fixed `sec:curation` → `sec:benchmark-curation` in results.tex
- Paper-claim-audit: 78 claims, 0 mismatches, verdict PASS
- Paper-review-sim: 5-reviewer panel, avg 67.6/100, BORDERLINE
  Full report: `docs/paper/NeurIPS_ready_version/REVIEW_SIM_2026-04-27.md`

**Files changed (6 paper + 1 bib):**
- `appendices_neurips.tex` — pass@k table, augmentation table, per-kernel table, cost table, checklist, HeCBench count
- `references.bib` — added RSBench2014
- `sections/framework.tex` — figure caption fix
- `sections/results.tex` — dangling ref fix, source comment updates (13 occurrences)
- `sections/benchmark-curation.tex` — source comment updates (2 occurrences)
- `sections/experimental-setup.tex` — source comment update (1 occurrence)

---

## Remaining Work

### Phase 5.5: Address Review Sim P0 Findings — DONE (2026-04-27)

Full details in `docs/paper/NeurIPS_ready_version/REVIEW_SIM_2026-04-27.md`.
Commit: `f15763a`

**P0-1: DONE.** Replaced unpaired chi-squared (128.6) with Yates-corrected McNemar (chi²=45.2, p<10⁻¹⁰). Concordance: 49 both-pass, 42 both-fail, 50 GPT-only, 1 Qwen-only. Added `compute_mcnemar()` to `cross_model_comparison.py` with Yates correction matching codebase convention. Added "task-level paired" clarifier per Codex review (unit-of-analysis transparency). 12 tests pass.

**P0-2: DONE.** Replaced "observed gap reflects both model capability and uncontrolled provider differences" with "cannot be fully attributed to model capability given unmatched sampling conditions." Abstract unchanged (no chi-squared cited there).

**P0-3: DONE.** Added to limitations: "Ten specs across six kernels were downgraded from strong or medium oracles to weak: six due to cross-API floating-point reduction-order divergence (cfd, hotspot, myocyte) and four due to synthesis asymmetry (bfs, nw, nn)." Corrected HANDOFF count from 8 to 10 (verified against known-issues.md).

**Files changed:** `discussion.tex`, `cross_model_comparison.py`, `test_cross_model_comparison.py`, `cross_model_comparison.json`.

### Phase 5.6: Address P1 Findings (recommended if time permits)

#### P1-1: Scope augmentation claim in abstract
**File:** `SECTIONS/abstract.tex`
**Fix:** "stable (75–83%)" → "no evidence of memorization-dependent degradation on the tested subset"

#### P1-2: Add GPT-5.4 per-direction rates to Table 3
**File:** `SECTIONS/results.tex` (tab:direction-rates)
**Data:** `quantitative_findings_gpt54.json > canonical > direction_pass_rates`

#### P1-3: Compute GPT-5.4 within-task variance
**Data:** Compare c distributions across 142 tasks for both models to assess effective temperature

#### P1-4: Add benchmark longevity paragraph
**File:** `SECTIONS/discussion.tex`

### Phase 6: Validate, Commit, Prepare for Overleaf

```bash
# 1. Run /validate (waves 1-3 required by pre-commit hook)
# 2. Stage files:
git add results/analysis/paper_data_azure_gpt54.json
git add results/analysis/paper_data_together-qwen-3.5-397b-a17b.json
git add results/analysis/quantitative_findings_gpt54.json results/analysis/quantitative_findings_gpt54.md
git add results/analysis/quantitative_findings_qwen.json results/analysis/quantitative_findings_qwen.md
git add results/analysis/cross_model_comparison.json
git add results/analysis/augmentation_per_kernel_matrix_azure-gpt-5.4.json
git add results/analysis/augmentation_per_kernel_matrix_azure-gpt-5.4.md
git add results/analysis/augmentation_per_kernel_matrix_together-qwen-3.5-397b-a17b.json
git add results/analysis/augmentation_per_kernel_matrix_together-qwen-3.5-397b-a17b.md
git add docs/paper/NeurIPS_ready_version/sections/*.tex
git add docs/paper/NeurIPS_ready_version/appendices_neurips.tex
git add docs/paper/NeurIPS_ready_version/references.bib
git add docs/paper/NeurIPS_ready_version/figures/*.pdf
git add scripts/analysis/cross_model_comparison.py
git add scripts/analysis/quantitative_findings.py
git add scripts/analysis/generate_paper_data.py
# 3. Commit
# 4. Copy docs/paper/NeurIPS_ready_version/ to Overleaf for compilation
```

### Phase 7: Submission Readiness (User's Responsibility)
1. **Compile on Overleaf** — no LaTeX compiler locally
2. **Page count** — 9 pages max (to end of Conclusion)
3. **Anonymous mode** — `\usepackage{neurips_2026}` without `[final]`
4. **Supplementary material** — ZIP of code/data if submitting
5. **Author information form** — separate NeurIPS requirement
6. **Teammate review** — final PDF review on Overleaf

---

## Traps to Avoid

- **Don't use unsuffixed `quantitative_findings.json` or `paper_data.json`** — they were deleted. All files are model-specific now.
- **Don't trust QF "overall" as L0-only** — QF overall = L0+ablation combined. Use `paper_data_*.json > passk_campaign > overall` for L0-only.
- **Don't use QF failure_taxonomy for L0-only counts** — it covers all records. Use `paper_data_*.json > passk_campaign > overall > by_status` for L0 breakdown.
- **Don't use the Cochran-Armitage z=7.65 from QF** — Simpson's paradox artifact.
- **Don't add file-coordination analysis** — data not precomputed for canonical evaluation.
- **Don't add self-repair results** — no data exists.
- **Don't confuse `appendices.tex` with `appendices_neurips.tex`** — only the latter is active.
- **Don't run `humanizer_academic`** — user found it ineffective. Use `deslop` principles inline.
