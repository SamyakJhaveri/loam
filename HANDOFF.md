# HANDOFF: NeurIPS 2026 Paper Completion

**Date:** 2026-04-27 (updated from 2026-04-25 original)
**Deadline:** NeurIPS 2026 — May 1, 2026 (3 days remaining)
**Status:** Main body sections COMPLETE. Appendix, checklist, and final pass remain.

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

## Remaining Work

### Phase 3: Appendix Fixes
**File:** `APPENDIX` (1,403 lines)
**Why:** Stale numbers from purged pre-Phase-3 dataset, missing GPT-5.4 content.

#### Step 3.1: Fix stale pass@k table
```bash
grep -n "38\.3\|19\.7.*macro\|27\.5.*macro\|103/142\|72\.5" APPENDIX
```
**Problem:** Shows `38.3%` greedy rate, `19.7%` pass@1, `27.5%` pass@3 — all stale.
**Fix with:** Qwen: pass@1=23.9%, pass@3=35.2%, hard fail=92/142 (64.8%), always pass=19/142 (13.4%), noisy=31/142 (21.8%). Add GPT-5.4 row: pass@1=62.7%, pass@3=69.7%, hard fail=43/142 (30.3%), always pass=76/142 (53.5%), noisy=23/142 (16.2%).

#### Step 3.2: Fix stale per-kernel table
```bash
grep -n "272\|710" APPENDIX
```
**Problem:** Comment says "total PASS = 272; total tasks = 710" — should be 230 PASS / 626 total for Qwen.
**Fix:** Update comment. Verify per-kernel rows against `PD_QWEN > passk_campaign > by_direction` (note: `by_kernel` not available in passk_campaign — compute from raw result files if needed).

#### Step 3.3: Fix stale augmentation table (appendix version)
```bash
grep -n "paper_data\.json\|quantitative_findings\.json" APPENDIX
```
**Fix:** Update all `% src:` comments from unsuffixed filenames to model-specific filenames (e.g., `paper_data.json` → `paper_data_together-qwen-3.5-397b-a17b.json`).

#### Step 3.4: Add GPT-5.4 cost data
```bash
grep -n "Cost\|cost" APPENDIX | tail -10
```
**Fix:** Add GPT-5.4 cost table. Compute from result JSONs:
```bash
source env_parbench/bin/activate && python3 -c "
import json, glob
files = glob.glob('results/evaluation/azure-gpt-5.4/*.json')
total_in = total_out = 0
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    u = d.get('usage', {})
    total_in += u.get('prompt_tokens', 0) + u.get('cached_tokens', 0)
    total_out += u.get('completion_tokens', 0)
print(f'Input: {total_in:,}, Output: {total_out:,}, Files: {len(files)}')
"
```

#### Step 3.5: Fix framework.tex figure caption
Erel's edit left an empty `\textbf{}.` in the figure caption. Add a title like "ParBench system architecture."

#### Step 3.6: Verify entire appendix
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
# Stale data (must return 0 non-comment hits)
grep -n "38\.3\|19\.7\|27\.5\|710\b\|272\b\|GPT-4.1" appendices_neurips.tex | grep -v '^\s*%' | grep -v '^[0-9]*:%'
# Unsuffixed analysis file references (must return 0)
grep -n "paper_data\.json\|quantitative_findings\.json" appendices_neurips.tex | grep -v '_qwen\|_gpt54\|_together\|_azure\|_validation' | grep -v '^\s*%'
```

**Phase 3 gate:** Zero stale numbers, zero unsuffixed file references, GPT-5.4 data added.

---

### Phase 4: NeurIPS Checklist
**Why:** NeurIPS REQUIRES a paper checklist. `neurips_2026.sty` provides `\answerYes`/`\answerNo`/`\answerNA` but NO checklist section exists.

**Action:** Add checklist section at end of `appendices_neurips.tex` or `main_neurips.tex`. Covers: claims, method reproducibility, open access, broader impact, limitations, experiments.

---

### Phase 5: Whole-Paper Final Pass

#### Step 5.1: Global stale-data check
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
# Zero stale data
grep -rn "GPT-4.1\|38\.3\|710\b\|64\.2\|19\.7\|27\.5" sections/ appendices_neurips.tex --include="*.tex" | grep -v '^\s*%' | grep -v '^[^:]*:[0-9]*:%'
# Zero TBDs (only macros.tex definition)
grep -rc "\\\\tbd" sections/ appendices_neurips.tex --include="*.tex" | grep -v ':0$'
# Zero "in progress"
grep -rn "in progress" sections/ appendices_neurips.tex --include="*.tex" | grep -v '%'
```

#### Step 5.2: Citation check
```bash
grep -rhoP '\\cite[tp]?\{([^}]+)\}' sections/ appendices_neurips.tex --include="*.tex" | tr ',' '\n' | sed 's/.*{//' | sed 's/}//' | sort -u > /tmp/cite_keys.txt
while read key; do
  grep -q "${key}" references.bib && echo "OK: $key" || echo "MISSING: $key"
done < /tmp/cite_keys.txt
```

#### Step 5.3: Dangling references
```bash
grep -rn '\\ref{' sections/ appendices_neurips.tex --include="*.tex" | grep -oP 'ref\{[^}]+\}' | sort -u > /tmp/refs.txt
grep -rn '\\label{' sections/ appendices_neurips.tex --include="*.tex" | grep -oP 'label\{[^}]+\}' | sed 's/label/ref/' | sort -u > /tmp/labels.txt
comm -23 /tmp/refs.txt /tmp/labels.txt
```

#### Step 5.4: Run `Skill("paper-review-sim")` on entire paper.
#### Step 5.5: Run `Skill("cite-check")` on entire paper.

---

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
git add docs/paper/NeurIPS_ready_version/figures/*.pdf
git add scripts/analysis/cross_model_comparison.py
git add scripts/analysis/quantitative_findings.py
git add scripts/analysis/generate_paper_data.py
# 3. Commit
# 4. Copy docs/paper/NeurIPS_ready_version/ to Overleaf for compilation
```

---

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
