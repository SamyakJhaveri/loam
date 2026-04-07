# Phase 16 Plan: GPT-4.1 Mini Data Analysis & Summary Generation

## Goal
Produce machine-readable analysis files for GPT-4.1 mini that parallel existing Qwen outputs, write the cross_model_comparison.py script, and regenerate all figures with dual-model data.

## GSD Execution Notes
- **Skip** `/gsd-discuss-phase` — tasks are fully specified
- Run T1-T3 sequentially, then T3b gate, then T4+T5 in parallel, then T6

## Tasks

### T1: Regenerate eval_summary with both models

**GSD command:** `/gsd-fast`

**Command:**
```bash
python3 scripts/evaluation/analyze_eval.py --project-root /home/samyak/Desktop/parbench_sam
```

**What it does:** Auto-discovers `azure-gpt-4.1-mini/` alongside `together-qwen-3.5-397b-a17b/` in `results/evaluation/`.

**Verification:** Output `eval_summary.json` must have 2 model keys (azure-gpt-4.1-mini AND together-qwen-3.5-397b-a17b), not just 1.

**Files:**
- `scripts/evaluation/analyze_eval.py` (run)
- `results/evaluation/eval_summary.json` (output)

---

### T2: Generate paper_data for GPT model

**GSD command:** `/gsd-fast`

**Command:**
```bash
python3 scripts/analysis/generate_paper_data.py \
  --results-dir results/evaluation/azure-gpt-4.1-mini \
  --output results/analysis/paper_data_gpt41mini.json -v
```

**Files:**
- `scripts/analysis/generate_paper_data.py` (run)
- `results/analysis/paper_data_gpt41mini.json` (output)

**Can run in parallel with T3.**

---

### T3: Generate error taxonomy for GPT

**GSD command:** `/gsd-fast`

**Command:**
```bash
python3 scripts/analysis/build_error_taxonomy.py \
  --results-dir results/evaluation/azure-gpt-4.1-mini \
  --output results/analysis/error_taxonomy_gpt41mini.json
```

**Files:**
- `scripts/analysis/build_error_taxonomy.py` (run)
- `results/analysis/error_taxonomy_gpt41mini.json` (output)

**Can run in parallel with T2.**

---

### T3b: Schema gate (REQUIRED before T4)

**GSD command:** `/gsd-fast`

**What:** Verify `results/analysis/paper_data_gpt41mini.json` has fields:
- `primary_campaign.overall.pass_rate` (expect ~0.266)
- `primary_campaign.by_direction`
- `primary_campaign.overall.by_status`

**Why:** If missing, `cross_model_comparison.py` must read raw result JSONs instead of paper_data.

**HARD GATE:** Do NOT proceed to T4 until T3b passes.

---

### T4: Write cross_model_comparison.py (MANDATORY — critical path)

**GSD command:** `/gsd-quick`

**THIS SCRIPT DOES NOT EXIST.** It is mandatory for Section 6.9 of the paper.

**Location:** `scripts/analysis/cross_model_comparison.py`

**Inputs:**
- `results/analysis/paper_data.json` (Qwen)
- `results/analysis/paper_data_gpt41mini.json` (GPT)

**Computes:**
1. Chi-squared test of independence on 2x2 contingency table (model x pass/fail)
2. Per-direction paired comparison for common 7 directions only (GPT missing omp_target-to-cuda)
3. Cohen's h effect sizes for overall and per-direction gaps
4. Per-kernel agreement/disagreement matrix (which kernels both pass/fail, which diverge)

**Output:** `results/analysis/cross_model_comparison.json` with all statistics.

**Start T4 as soon as T3b passes. Run in parallel with T5.**

---

### T5: Regenerate ALL figures with dual-model data

**GSD command:** `/gsd-fast`

**Command:**
```bash
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir docs/paper/figures -v
```

**Prerequisites:** Phase 15.5 PW-A (color fix) must be confirmed before running.

**Notes:**
- Script auto-discovers both model directories via `load_eval_results()`
- GPT color must be `#56B4E9` (Okabe-Ito sky blue) — verified in PW-A
- F7 (augmentation) was hardcoded to Qwen at line ~1158 — fixed in PW-A
- Longest-running task; start in parallel with T4

**Files:**
- `scripts/generate_paper_figures.py` (run)
- `docs/paper/figures/*.pdf` (output)

---

### T6: Document coverage gaps

**GSD command:** `/gsd-fast`

**What:** Note GPT coverage gap in `results/analysis/coverage_gaps.md`:
- GPT missing omp_target-to-cuda direction
- For table rows covering this direction: use "—" with footnote

**Files:**
- `results/analysis/coverage_gaps.md` (create/update)

---

## Execution Order

```
T1 (analyze_eval) → T2 + T3 (parallel) → T3b (gate) → T4 + T5 (parallel) → T6
```

## Phase 16 Verification
**GSD command:** `/gsd-verify-work`

Check all 7 artifacts exist with correct values:
1. `eval_summary.json` — 2 model keys
2. `paper_data_gpt41mini.json` — pass_rate ≈ 0.266
3. `error_taxonomy_gpt41mini.json` — exists with GPT error classes
4. `cross_model_comparison.json` — has chi-squared p-value and Cohen's h
5. `f3_kernel_model_heatmap.pdf` — dual-model
6. `f4_failure_taxonomy.pdf` — GPT not grey (#56B4E9)
7. `f7_augmentation_robustness.pdf` — dual-model (if GPT cuda-to-omp data exists)

## Hard Gate for Phase 17
`cross_model_comparison.json` MUST exist with chi-squared p-value and Cohen's h before Phase 17B (Section 6.9) starts.
