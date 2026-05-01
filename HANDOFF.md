# HANDOFF: GPT-5.3-codex Analysis + 3-Model Comparison

**Date:** 2026-04-30
**Status:** Ready for execution — no code was changed in the planning session
**Plan file:** `/home/samyak/.claude/plans/i-got-the-the-greedy-quiche.md`

---

## Goal

Run the existing analysis scripts for GPT-5.3-codex (the third model), make `cross_model_comparison.py` work with any two models (currently hardcoded for "qwen" and "gpt"), run comparisons for all 3 pairs, and re-run `statistical_analysis.py`.

**Analysis data only — no paper/LaTeX updates.**

---

## Background

ParBench evaluates LLM parallel code translation (CUDA/OpenMP/OpenCL). Three models were evaluated:

| Model | Result dir | Files |
|-------|-----------|-------|
| Qwen 3.5 397B | `results/evaluation/together-qwen-3.5-397b-a17b/` | 708 |
| GPT-5.4 | `results/evaluation/azure-gpt-5.4/` | 822 |
| GPT-5.3-codex | `results/evaluation/azure-gpt-5.3-codex/` | 814 |

Qwen and GPT-5.4 already have analysis files. GPT-5.3-codex does not yet.

---

## Gotchas (found during adversarial plan review — don't repeat these)

### 1. `augmentation_analysis.py` — single-model clobbers output
Passing ONE `--model-dir` produces an unsuffixed filename that overwrites existing files. **Always pass all 3 models together** to get per-model suffixed output.

### 2. `quantitative_findings.py` — hardcoded model name
Line 1758 hardcodes `"model": "together-qwen-3.5-397b-a17b"`. Fix to `"model": args.model_dir,` before running for codex.

### 3. `generate_paper_claims.py` — skip it
Entirely Qwen-only (hardcoded model name, reads unsuffixed files that don't exist). Not part of this task.

### 4. `compute_mcnemar` — crashes on task key mismatch
Line 60-63 raises `ValueError` if task key sets differ between models. Replace with intersection + warning.

---

## The Work (3 parts)

### Part A — Run existing scripts for GPT-5.3-codex

No code changes except the 1-line fix in `quantitative_findings.py`.

**A1.** Generate paper data:
```bash
cd /home/samyak/Desktop/parbench_sam && source env_parbench/bin/activate
python3 scripts/analysis/generate_paper_data.py \
  --results-dir results/evaluation/azure-gpt-5.3-codex \
  --output results/analysis/paper_data_azure-gpt-5.3-codex.json -v
```

**A2.** Fix line 1758 in `quantitative_findings.py`, then:
```bash
python3 scripts/analysis/quantitative_findings.py \
  --project-root /home/samyak/Desktop/parbench_sam --model-dir azure-gpt-5.3-codex -v
```

**A3.** Augmentation analysis (all 3 models to avoid suffix bug):
```bash
python3 scripts/analysis/augmentation_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --model-dir together-qwen-3.5-397b-a17b azure-gpt-5.4 azure-gpt-5.3-codex -v
```

### Part B — Make `cross_model_comparison.py` model-agnostic

Simple changes — no new output schema, no N-model orchestrator. Just make it work with any two models instead of hardcoded qwen/gpt.

**Files:**
- `/home/samyak/Desktop/parbench_sam/scripts/analysis/cross_model_comparison.py`
- `/home/samyak/Desktop/parbench_sam/scripts/analysis/test_cross_model_comparison.py`

**5 changes:**
1. **CLI args:** Rename `--qwen-data`/`--gpt-data` → `--model-a`/`--model-b` (keep same defaults)
2. **`compute_mcnemar`:** Rename params to generic names, replace `ValueError` on key mismatch with intersection + warning
3. **`build_comparison`:** Derive model names from `data["model"]` field, use those as dict keys instead of hardcoded `"qwen"`/`"gpt"`
4. **Verbose output:** Use dynamic model names instead of hardcoded "Qwen"/"GPT"
5. **Tests:** Update hardcoded `"qwen"`/`"gpt"` key checks to match test data's model names

Load `/andrej-karpathy-skills:karpathy-guidelines` before coding. Run `pytest scripts/analysis/test_cross_model_comparison.py -v` before and after.

### Part C — Run comparisons for all 3 pairs + re-run stats

```bash
# Pair 1: Qwen vs GPT-5.4
python3 scripts/analysis/cross_model_comparison.py \
  --model-a results/analysis/paper_data_together-qwen-3.5-397b-a17b.json \
  --model-b results/analysis/paper_data_azure_gpt54.json \
  --output results/analysis/cross_model_comparison_qwen_vs_gpt54.json -v

# Pair 2: Qwen vs codex
python3 scripts/analysis/cross_model_comparison.py \
  --model-a results/analysis/paper_data_together-qwen-3.5-397b-a17b.json \
  --model-b results/analysis/paper_data_azure-gpt-5.3-codex.json \
  --output results/analysis/cross_model_comparison_qwen_vs_codex.json -v

# Pair 3: GPT-5.4 vs codex
python3 scripts/analysis/cross_model_comparison.py \
  --model-a results/analysis/paper_data_azure_gpt54.json \
  --model-b results/analysis/paper_data_azure-gpt-5.3-codex.json \
  --output results/analysis/cross_model_comparison_gpt54_vs_codex.json -v

# Re-run statistical analysis (auto-discovers all 3 models)
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

---

## Output Files (10 total)

| File | Source |
|------|--------|
| `paper_data_azure-gpt-5.3-codex.json` | A1 |
| `quantitative_findings_azure-gpt-5.3-codex.json` + `.md` | A2 |
| `augmentation_per_kernel_matrix_azure-gpt-5.3-codex.json` + `.md` | A3 |
| `cross_model_comparison_qwen_vs_gpt54.json` | C1 |
| `cross_model_comparison_qwen_vs_codex.json` | C1 |
| `cross_model_comparison_gpt54_vs_codex.json` | C1 |
| `statistical_analysis.json` + `.md` | C2 |

All in `results/analysis/`.

---

## Environment

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
# Always python3, never python
```

## Skills

| Skill | When |
|-------|------|
| `/andrej-karpathy-skills:karpathy-guidelines` | Before Part B code changes |
| `/validate` | Before any commit |
| `/interpret-results` | After all data is ready (optional) |
