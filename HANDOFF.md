# HANDOFF: Integrate GPT-5.3-codex into the NeurIPS 2026 Paper

**Date:** 2026-05-01
**Status:** Ready for execution — all data exists, no code changes made yet
**Previous handoff (COMPLETED):** Data analysis pipeline for codex (Parts A-C) — all 10 output files exist in `results/analysis/`

---

## What This Task Is About (Plain English)

We have a research paper about **ParBench**, a benchmark that tests whether AI models can translate parallel code between different programming languages (CUDA, OpenMP, OpenCL). The paper currently reports results for **two models** (Qwen 3.5 and GPT-5.4). We just ran the same experiments on a **third model** (GPT-5.3-codex) and need to add it to the paper.

The twist: GPT-5.3-codex (a code-specialized model) performs almost identically to GPT-5.4 (a general-purpose model). This is actually an interesting finding — code-specialized training doesn't help with parallel code translation.

**Your job:** Update every section of the LaTeX paper to include the third model as a co-equal participant, update the figures, and make sure every number traces back to its data file.

---

## What's Already Done

1. All evaluation results exist: 814 result JSONs in `results/evaluation/azure-gpt-5.3-codex/`
2. All analysis files exist in `results/analysis/` (quantitative findings, cross-model comparisons, augmentation data, paper data)
3. The three-model findings document exists at `docs/eval-findings/2026-05-01-three-model-comparison.md` with 9 key findings and 7 paper-ready claims
4. The L0 passers file exists at `.planning/eval-selections/l0_passers_azure_gpt_5_3_codex.json`
5. Three marker files confirm canonical, ablation, and derive stages are complete

**Nothing was changed in the paper yet. All LaTeX files are untouched.**

---

## What You Must NOT Do

1. **Never delete or modify result JSONs** in `results/evaluation/` — they are immutable
2. **Never remove `{\color{green}...}` markers** from teammate edits (but you CAN edit text inside them)
3. **Never cite numbers without a `% src:` comment** tracing them to the exact JSON field
4. **Never add a figure reference** (`\ref{fig:X}`) unless the figure file exists on disk
5. **Never bypass validation** — run `/validate` before any commit

---

## Skills to Invoke (in order)

Before you begin ANY work, invoke these skills:

| When | Skill | Why |
|------|-------|-----|
| Session start | `andrej-karpathy-skills:karpathy-guidelines` | Prevents over-engineering, ensures surgical changes |
| Before editing `generate_paper_figures.py` | `test-driven-development` | Run existing tests first, write tests for new model entries, then make changes |
| Before committing | `validate` | 4-wave validation loop (waves 1-3 required for commit) |
| After all edits | `superpowers:verification-before-completion` | Verify all claims are grounded |
| End of session | Run `/codex:rescue review the uncommitted changes` | Cross-model second opinion (mandatory per CLAUDE.md) |

**Do NOT use GSD commands** (per project memory `feedback_no_gsd.md`).

**Commit strategy:** Commit ONCE after all Steps 1-9 are verified, not after each step. Running `/validate` takes ~90s and is required before each commit.

---

## Environment Setup (MUST DO FIRST)

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
# Always use python3, never bare python
```

## Pre-Implementation Scan (run before touching any file)

```bash
# Find every place "two models" appears — these ALL need updating to "three models"
grep -rn "two models" docs/paper/NeurIPS_ready_version/sections/ docs/paper/NeurIPS_ready_version/appendices_neurips.tex

# Find every place "1,448" or "1448" appears — these ALL need updating to "2,262"
grep -rn '1,448\|1448' docs/paper/NeurIPS_ready_version/

# Check for stale TBD placeholders
grep -rn '\\tbd' docs/paper/NeurIPS_ready_version/

# Verify codex data files exist
ls results/analysis/quantitative_findings_azure-gpt-5.3-codex.json \
   results/analysis/cross_model_comparison_gpt54_vs_codex.json \
   results/analysis/statistical_analysis.json \
   results/analysis/paper_data_azure-gpt-5.3-codex.json

# Verify codex failure taxonomy sums to 814
python3 -c "
import json
with open('results/analysis/quantitative_findings_azure-gpt-5.3-codex.json') as f:
    d = json.load(f)
t = d['canonical']['failure_taxonomy']['status_counts']
print(t)
print('Sum:', sum(t.values()))
assert sum(t.values()) == 814, 'MISMATCH!'
print('OK')
"
```

---

## The Paper Structure

All paper files are in `docs/paper/NeurIPS_ready_version/`. Here's the exact map:

| File | Path | Needs Changes? |
|------|------|---------------|
| Main file | `docs/paper/NeurIPS_ready_version/main_neurips.tex` | NO |
| Macros | `docs/paper/NeurIPS_ready_version/sections/macros.tex` | YES — add codex macros |
| Abstract | `docs/paper/NeurIPS_ready_version/sections/abstract.tex` | YES — add codex numbers |
| Introduction | `docs/paper/NeurIPS_ready_version/sections/1-introduction.tex` | YES — update contribution #3 |
| Framework | `docs/paper/NeurIPS_ready_version/sections/framework.tex` | NO — model-independent |
| Benchmark Curation | `docs/paper/NeurIPS_ready_version/sections/benchmark-curation.tex` | NO — model-independent |
| Experimental Setup | `docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex` | YES — add codex model description |
| Results | `docs/paper/NeurIPS_ready_version/sections/results.tex` | YES — HEAVIEST changes |
| Related Work | `docs/paper/NeurIPS_ready_version/sections/related-work.tex` | NO — model-independent |
| Discussion | `docs/paper/NeurIPS_ready_version/sections/discussion.tex` | YES — update stats + findings |
| Appendices | `docs/paper/NeurIPS_ready_version/appendices_neurips.tex` | YES — add codex figures/tables |
| Bibliography | `docs/paper/NeurIPS_ready_version/references.bib` | YES — add codex system card citation |
| Figures dir | `docs/paper/NeurIPS_ready_version/figures/` | YES — new codex figures |
| Figure script | `scripts/generate_paper_figures.py` | YES — add codex to model dicts |

---

## Data Sources (Ground Truth)

Every number in the paper must trace to one of these files. Read them before writing any prose.

| File | Full Path | What It Contains |
|------|-----------|-----------------|
| Codex quant findings | `results/analysis/quantitative_findings_azure-gpt-5.3-codex.json` | Overall rates, direction rates, pass@k, failure taxonomy |
| GPT-5.4 quant findings | `results/analysis/quantitative_findings_azure-gpt-5.4.json` | Same for GPT-5.4 |
| Qwen quant findings | `results/analysis/quantitative_findings_together-qwen-3.5-397b-a17b.json` | Same for Qwen |
| Statistical analysis | `results/analysis/statistical_analysis.json` | Augmentation curves (all 3 models), chi-squared tests, omnibus test |
| Codex vs GPT-5.4 | `results/analysis/cross_model_comparison_gpt54_vs_codex.json` | Fisher, McNemar, OR for this pair |
| Qwen vs Codex | `results/analysis/cross_model_comparison_qwen_vs_codex.json` | Fisher, McNemar, OR for this pair |
| Qwen vs GPT-5.4 | `results/analysis/cross_model_comparison_qwen_vs_gpt54.json` | Fisher, McNemar, OR for this pair |
| Codex paper data | `results/analysis/paper_data_azure-gpt-5.3-codex.json` | Paper-ready data extract |
| Codex augmentation | `results/analysis/augmentation_per_kernel_matrix_azure-gpt-5.3-codex.json` | Per-kernel augmentation matrix |
| 3-model findings | `docs/eval-findings/2026-05-01-three-model-comparison.md` | 9 findings, 7 paper-ready claims |

---

## Key Numbers Reference Table

Use these numbers. Every one has been verified against the JSON data files. The `Source` column tells you exactly which JSON file and field path to cite in the `% src:` comment.

### Overall Performance

| Metric | Qwen 3.5 | GPT-5.4 | GPT-5.3-codex | Source (JSON path) |
|--------|----------|---------|---------------|-------------------|
| Overall pass rate | 36.7% [33.1, 40.6] | 75.5% [72.5, 78.4] | 74.2% [71.1, 77.1] | `quantitative_findings_*.json > canonical > aggregate_pass_rates > overall` |
| n (valid records) | 626 | 822 | 814 | `quantitative_findings_*.json > metadata > file_counts > valid_after_exclusion` |
| **Total records** | **2,262** | | | Sum of all three n values |
| pass@1 (142 tasks) | 23.9% | 62.7% | 62.7% | `paper_data_*.json > passk_campaign > aggregate_passk` |
| pass@3 (142 tasks) | 35.2% | 69.7% | 68.3% | same |
| PASS count | 230 | 621 | 604 | `quantitative_findings_*.json > canonical > failure_taxonomy > status_counts` |
| BUILD_FAIL | 245 (39.1%) | 123 (15.0%) | 139 (17.1%) | same |
| RUN_FAIL | 121 (19.3%) | 43 (5.2%) | 44 (5.4%) | same |
| VERIFY_FAIL | 29 (4.6%) | 32 (3.9%) | 27 (3.3%) | same |
| EXTRACTION_FAIL | 1 | 3 | 0 | same |
| BF:VF ratio | 8.4:1 | 3.8:1 | 5.1:1 | Computed: BUILD_FAIL / VERIFY_FAIL |

### Pairwise Statistical Tests

| Pair | OR [95% CI] | p (Bonferroni) | Cohen's h | Source |
|------|-------------|----------------|-----------|--------|
| Codex vs GPT-5.4 | 0.93 [0.74, 1.16] | 1.0 | -0.031 (negligible) | `statistical_analysis.json > model_comparison > pairwise[0]` |
| Codex vs Qwen | 4.95 [3.95, 6.21] | 0.0 | +0.774 (medium) | `statistical_analysis.json > model_comparison > pairwise[1]` |
| GPT-5.4 vs Qwen | 5.32 [4.24, 6.68] | 0.0 | +0.805 (large) | `statistical_analysis.json > model_comparison > pairwise[2]` |

Omnibus: chi2(2) = 287.27, p < 0.001, Cramer's V = 0.356. Source: `statistical_analysis.json`

### Codex Direction Rates (L0 only, per-model)

| Direction | Codex Rate | CI | n | Source |
|-----------|-----------|----|----|--------|
| CUDA→OMP | 76.4% | [65.4, 84.7] | 72 | `quantitative_findings_azure-gpt-5.3-codex.json > canonical > direction_pass_rates > standard > cuda-to-omp` |
| OMP→OCL | 82.3% | [69.7, 90.4] | 51 | same path, key `omp-to-opencl` |
| OMP→CUDA | 55.6% | [44.1, 66.5] | 72 | same path, key `omp-to-cuda` |
| OCL→OMP | 39.2% | [27.0, 52.9] | 51 | same path, key `opencl-to-omp` |
| CUDA→OCL | 57.9% | [45.0, 69.8] | 57 | same path, key `cuda-to-opencl` |
| OCL→CUDA | 19.3% | [11.1, 31.3] | 57 | same path, key `opencl-to-cuda` |
| OMP-tgt→OMP | 100% | [70.1, 100] | 9 | same path, key `omp_target-to-omp` |
| OMP-tgt→CUDA | 100% | [86.2, 100] | 24 | same path, key `omp_target-to-cuda` |
| OMP→OMP-tgt | 100% | [70.1, 100] | 9 | same path, key `omp-to-omp_target` |
| CUDA→OMP-tgt | 100% | [86.2, 100] | 24 | same path (case_study), key `cuda-to-omp_target` |

### Augmentation Curves

| Model | L0 | L1 | L2 | L3 | L4 | Chi2 p (Bonf) | Source |
|-------|----|----|----|----|-----|--------------|--------|
| Codex | 62.7% (267/426) | 86.6% (84/97) | 88.7% (86/97) | 86.6% (84/97) | 85.6% (83/97) | 1.0 | `statistical_analysis.json > augmentation_curves > azure-gpt-5.3-codex` |
| GPT-5.4 | 62.7% (267/426) | 88.9% (88/99) | 90.9% (90/99) | 86.9% (86/99) | 90.9% (90/99) | 1.0 | same, key `azure-gpt-5.4` |
| Qwen | 23.9% (102/426) | 74.0% (37/50) | 64.0% (32/50) | 62.0% (31/50) | 56.0% (28/50) | 0.005 | same, key `together-qwen-3.5-397b-a17b` |

Chi-squared p-values source: `statistical_analysis.json > chi2_augmentation_by_model > [model] > p_corrected_bonferroni`

---

## About GPT-5.3-codex (For Paper Prose)

This model is definitively code-specialized. Use this information for the experimental-setup section:

- **Released:** February 5, 2026 by OpenAI
- **What it is:** A code-specialized model optimized via reinforcement learning on real-world software engineering tasks
- **Context window:** 400K tokens (vs GPT-5.4's 1M tokens)
- **API pricing:** $1.75/$14.00 per 1M tokens (vs GPT-5.4's $2.50/$15.00)
- **Benchmark comparison:** Wins Terminal-Bench 2.0 (77.3% vs 75.1%); GPT-5.4 edges ahead on SWE-Bench Pro (57.7% vs 56.8%)
- **Key differentiator:** GPT-5.4 is general-purpose with computer-use capability; Codex is purpose-built for code
- **Citation:** OpenAI GPT-5.3-codex System Card (2026). URL: `https://openai.com/index/gpt-5-3-codex-system-card/`
- **Azure deployment ID in project:** `gpt-5.3-codex` via Azure OpenAI, Responses API

---

## Writing Style Rules

The paper has a specific style. Follow it exactly:

1. **Every number needs a `% src:` comment** — Example: `% src: quantitative_findings_azure-gpt-5.3-codex.json > canonical > failure_taxonomy > status_counts`
2. **Wilson 95% CIs** for per-record pass rates — format: `74.2\% [71.1\%, 77.1\%]`
3. **Chen et al. estimator** for pass@k — these are different from per-record rates
4. **Effect sizes always named** — Cohen's h for pairwise, OR with CI for Fisher's, McNemar for paired tests
5. **Use macros** — `\codexshort{}` not "Codex", `\gptnew{}` not "GPT-5.4"
6. **One paragraph = one rhetorical purpose** — don't mix findings in a single paragraph
7. **Concise** — no filler, no hedging beyond what's necessary
8. **Green text** — `{\color{green}...}` marks teammate edits from Overleaf. You can edit inside them.

---

## Step-by-Step Execution Plan

### STEP 1: Add Codex Macros

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/macros.tex`

**What to do:** Add two new LaTeX macros after line 8 (after the `\gptprovider` macro):

```latex
\newcommand{\codex}{GPT-5.3-codex}
\newcommand{\codexshort}{Codex}
```

**Verify:** `grep codex docs/paper/NeurIPS_ready_version/sections/macros.tex` should return both lines.

---

### STEP 2: Update the Figure Generation Script

**File:** `/home/samyak/Desktop/parbench_sam/scripts/generate_paper_figures.py`

**Invoke skill first:** `andrej-karpathy-skills:karpathy-guidelines` and `test-driven-development`

**What to do:** The script has 5 dictionaries (lines 84-107) that define which models to include. Each needs a new codex entry. Here are the exact changes:

**In `MODEL_COLORS` (line 84-87):** Add after `"azure-gpt-5.4"` entry:
```python
    "azure-gpt-5.3-codex":    OKABE_ITO["green"],
```

**In `MODEL_DISPLAY` (line 89-92):** Add:
```python
    "azure-gpt-5.3-codex":    "GPT-5.3\nCodex",
```

**In `MODEL_DISPLAY_SHORT` (line 94-97):** Add:
```python
    "azure-gpt-5.3-codex":    "Azure GPT-5.3-codex",
```

**In `MODEL_LINESTYLE` (line 99-102):** Add:
```python
    "azure-gpt-5.3-codex":    ("s--", "dashed"),
```

**In `MODEL_SLUG` (line 104-107):** Add:
```python
    "azure-gpt-5.3-codex": "codex",
```

**Verify:** Run the script and check that it produces codex figures:
```bash
source env_parbench/bin/activate
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir docs/paper/NeurIPS_ready_version/figures
```

**Expected new files:**
- `f3_kernel_model_heatmap_codex.{pdf,png}` — per-kernel heatmap
- `f4_failure_taxonomy_codex.{pdf,png}` — failure distribution
- `f5_pass_at_k_by_direction_codex.{pdf,png}` — pass@k by direction
- `f6_cross_suite_comparison_codex.{pdf,png}` — suite comparison
- `f7_augmentation_robustness.{pdf,png}` — UPDATED with 3 lines (combined figure)

**Verify:** `ls docs/paper/NeurIPS_ready_version/figures/f*codex* | wc -l` should be ≥ 4

**If any figure fails to generate:** Don't reference it in the paper. Use a `\tbd{codex figure}` placeholder and move on. The script iterates over all models in `MODEL_COLORS`, so adding the entry should be sufficient.

---

### STEP 3: Update `results.tex` — The Heaviest Section

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/results.tex`

Read the file first. The current structure is:
- Lines ~50-68: Table 1 (Overall Pass Rates) — 2 model rows
- Lines ~70-71: §5.1 Overall Performance prose
- Lines ~73-76: §5.2 pass@k Analysis
- Lines ~81-105: Direction Table (Table 2) — 2 model columns
- Lines ~107-108: §5.3 Direction Dependence prose
- Lines ~110-120: §5.4 Failure Taxonomy
- Lines ~122-125: §5.5 Augmentation Robustness

#### 3A: Table 1 — Add codex row

Find the line with `\gptnew{}` in the table (currently the last data row before `\bottomrule`). Add a new row after it:

```latex
% src: quantitative_findings_azure-gpt-5.3-codex.json > canonical > failure_taxonomy > status_counts
\codex{} & 604 & 139 & 44 & 27 & 0 & 814 & 74.2\% [71.1\%, 77.1\%] \\
```

Update the caption: change `"two models"` → `"three models"`. Update the total record count. The caption currently mentions 626 and 822 — add 814.

**Verify:** `grep -c '\\\\$' docs/paper/NeurIPS_ready_version/sections/results.tex` in the table area — should show 3 data rows now.

#### 3B: §5.1 Overall Performance

After the sentence about GPT-5.4 passing 75.5%, add:

```latex
% src: statistical_analysis.json > model_comparison > pairwise[0] (Bonferroni-corrected p)
\codexshort{}, a code-specialized model, passes 74.2\% of its valid records---statistically indistinguishable from \gptnew{} (Fisher's exact $p = 1.0$, OR\,=\,0.93 [0.74, 1.16], Cohen's $h = -0.031$). This indicates that code-specialized reinforcement learning training does not measurably improve parallel translation success at this task difficulty.
```

#### 3C: §5.2 pass@k Analysis

After the existing Qwen pass@k sentence, add codex data:

```latex
% src: paper_data_azure-gpt-5.3-codex.json > passk_campaign > aggregate_passk
\codexshort{} achieves pass@1\,=\,62.7\% and pass@3\,=\,68.3\%, matching \gptnew{}'s pass@1 exactly with a slightly narrower pass@1-to-pass@3 gap (5.6\,pp versus 7.0\,pp).
```

#### 3D: Direction Table — Add codex column

The current table has columns: Direction | Qwen | GPT-5.4 | n. Add a `\codexshort{}` column between GPT-5.4 and n. Use the direction rates from the "Codex Direction Rates" table above.

The table will now have 4 data columns — wrap it with `\resizebox{\textwidth}{!}{...}` if not already wrapped.

**Verify:** Check that every codex rate in the table matches the JSON. Run:
```bash
python3 -c "
import json
with open('results/analysis/quantitative_findings_azure-gpt-5.3-codex.json') as f:
    d = json.load(f)
for dir, data in d['canonical']['direction_pass_rates']['standard'].items():
    print(f'{dir}: {data[\"value\"]*100:.1f}%')
"
```

#### 3E: §5.3 Direction Dependence prose

Add codex to the cross-model comparison. Note that codex's direction pattern nearly mirrors GPT-5.4 across all 6 standard directions.

#### 3F: §5.4 Failure Taxonomy

Add a sentence with codex failure numbers:

```latex
% src: quantitative_findings_azure-gpt-5.3-codex.json > canonical > failure_taxonomy > status_counts
\codexshort{}'s failure distribution is intermediate: \buildfail{} accounts for 17.1\% of records (ratio \buildfail{}:\verifyfail{} = 5.1:1), between \qwenshort{}'s 39.1\% (8.4:1) and \gptnew{}'s 15.0\% (3.8:1). \codexshort{} taxonomy (814 records) is in Appendix~\ref{sec:appendix-codex-figures}.
```

#### 3G: §5.5 Augmentation Robustness

Add codex augmentation data:

```latex
% src: statistical_analysis.json > augmentation_curves > azure-gpt-5.3-codex
\codexshort{} shows the same plateau pattern as \gptnew{}: 86.6\%--88.7\% at L1--L4 (chi-squared independence test, $p = 1.0$ after Bonferroni correction), in contrast to \qwenshort{}'s peak-then-decline (74.0\% at L1 to 56.0\% at L4, $p = 0.005$).
```

**Verify after all results.tex changes:**
```bash
grep -c 'codex\|\\codex' docs/paper/NeurIPS_ready_version/sections/results.tex
# Should be >= 10 occurrences
```

---

### STEP 4: Update `experimental-setup.tex`

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex`

#### 4A: Models paragraph (starts with `\textbf{Models:}` at line ~48)

After the GPT-5.4 description, add codex:

```latex
and \codex{}, a code-specialized model optimized via reinforcement learning on software engineering tasks~\cite{GPT53Codex2026}, also accessed via \gptprovider{} with a 400K context window.
```

Change "two models" → "three models" in this paragraph.

#### 4B: Translation Protocol

Change "two models" → "three models" if it appears.

#### 4C: Evaluation Phases

Note codex uses same protocol. Add: "Total L0 records across three models: 1,278 (3 × 426)."

**Verify:**
```bash
grep -c "three models" docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex  # should be >= 1
grep "codex\|\\\\codex" docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex  # should show codex model description
grep "GPT53Codex" docs/paper/NeurIPS_ready_version/sections/experimental-setup.tex  # should show citation
```

---

### STEP 5: Update `abstract.tex`

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/abstract.tex`

This is a compact section (~4 lines of content). Integrate codex WITHOUT adding a full sentence per model. Replace the per-model pass@k sentences with a combined version:

Find: the two separate sentences about Qwen and GPT-5.4 pass rates.

Replace with something like:
```latex
Under stochastic sampling (temperature~0.7, three independent attempts per task), pass@1 ranges from 23.9\% (\qwenshort{}) to 62.7\% (\gptnew{} and \codexshort{}) over 142~unique source-target pairs, with the code-specialized \codexshort{} performing indistinguishably from the general-purpose \gptnew{}.
```

**Verify:**
```bash
# Word count should be < 260
cat docs/paper/NeurIPS_ready_version/sections/abstract.tex | wc -w
# Codex should appear
grep "codex\|\\\\codex" docs/paper/NeurIPS_ready_version/sections/abstract.tex
# "two models" should NOT appear
grep "two models" docs/paper/NeurIPS_ready_version/sections/abstract.tex && echo "FAIL: still says two models" || echo "OK"
```

---

### STEP 6: Update `1-introduction.tex`

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/1-introduction.tex`

#### 6A: Contribution #3 (lines ~53-56, inside a `{\color{green}...}` block — OK to edit)

Find: `1,448 valid translation records` → Replace with `2,262 valid translation records`
Find: `two models` → Replace with `three models`

Add codex pass@1 alongside existing numbers. Add a new key finding about code-specialized training.

**Verify:**
```bash
grep "2,262" docs/paper/NeurIPS_ready_version/sections/1-introduction.tex  # should match
grep "three models" docs/paper/NeurIPS_ready_version/sections/1-introduction.tex  # should match
grep "1,448\|two models" docs/paper/NeurIPS_ready_version/sections/1-introduction.tex && echo "FAIL: stale references" || echo "OK"
```

---

### STEP 7: Update `discussion.tex`

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/discussion.tex`

#### 7A: Opening paragraph (line ~5)

Add the three-way statistical comparison:
```latex
% src: statistical_analysis.json > omnibus_chi2; cross_model_comparison_gpt54_vs_codex.json > mcnemar
An omnibus chi-squared test across all 2,262 records confirms significant model differences ($\chi^2(2) = 287.27$, $p < 10^{-10}$, Cram\'{e}r's $V = 0.356$). However, pairwise McNemar analysis on the 142 balanced L0 tasks shows \codexshort{} and \gptnew{} are indistinguishable ($\chi^2 = 0.125$, $p = 0.724$; concordance: 94 both-pass, 40 both-fail, 5 \gptnew{}-only, 3 \codexshort{}-only).
```

Change "two models" → "three models" throughout.

#### 7B: Limitations

Add: codex and GPT-5.4 share the same provider (Azure OpenAI), making within-provider comparison more controlled but limiting generalizability.

#### 7C: Future work

Change "GPT-5.4 passes 62.7%" → "Both GPT models pass 62.7% at L0"

**Verify:**
```bash
grep -c "codex" docs/paper/NeurIPS_ready_version/sections/discussion.tex  # should be >= 3
grep "two models" docs/paper/NeurIPS_ready_version/sections/discussion.tex && echo "FAIL: stale" || echo "OK"
grep "287.27" docs/paper/NeurIPS_ready_version/sections/discussion.tex  # should show omnibus chi2
```

---

### STEP 8: Update Appendices

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex`

#### 8A: Add codex figures section

After line 1473 (after the GPT-5.4 figures section, before `\section{Evaluation Cost Summary}`), add a new section:

```latex
\section{GPT-5.3-codex Per-Model Figures}
\label{sec:appendix-codex-figures}

The following figures present GPT-5.3-codex evaluation results using the same visualization format as the main-body counterparts.

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f3_kernel_model_heatmap_codex.pdf}
\caption{Per-kernel pass rates across all translation directions (GPT-5.3-codex).}
\label{fig:f3-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f4_failure_taxonomy_codex.pdf}
\caption{Failure taxonomy distribution (GPT-5.3-codex). Compare with Figure~\ref{fig:failure-taxonomy} in main body (Qwen~3.5 397B).}
\label{fig:f4-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f5_pass_at_k_by_direction_codex.pdf}
\caption{Pass@$k$ rates by translation direction (GPT-5.3-codex).}
\label{fig:f5-codex}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=\columnwidth]{f6_cross_suite_comparison_codex.pdf}
\caption{Cross-suite pass rate comparison (GPT-5.3-codex).}
\label{fig:f6-codex}
\end{figure}
```

#### 8B: Add codex cost table

After the existing GPT-5.4 cost table (line ~1510), add a codex cost table. Extract cost data from result JSONs:
```bash
python3 -c "
import json, glob
total_tokens = 0
files = glob.glob('results/evaluation/azure-gpt-5.3-codex/*.json')
for f in files:
    with open(f) as fh:
        d = json.load(fh)
        total_tokens += d.get('prompt_tokens', 0) + d.get('completion_tokens', 0)
print(f'Total files: {len(files)}')
print(f'Total tokens: {total_tokens:,}')
"
```

#### 8C: Update model-config table (line ~1180, `\label{tab:model-config}`)

Add a codex row after the GPT-5.4 row:
```latex
GPT-5.3-codex & Azure OpenAI & undisclosed & undisclosed & N/A$^\dagger$ \\
```

#### 8D: Update pass@k table (line ~1262, `\label{tab:pass-at-k}`)

Add a codex row after the GPT-5.4 row:
```latex
% src: paper_data_azure-gpt-5.3-codex.json > passk_campaign > aggregate_passk + task_classification
GPT-5.3-codex & 142 & 62.7\% & 68.3\% & 45/142 (31.7\%) & 16/142 (11.3\%) & 81/142 (57.0\%) \\
```

Source for task classification: `quantitative_findings_azure-gpt-5.3-codex.json > canonical > pass_at_k > task_classification` (always_pass: 81, hard_fail: 45, noisy_fail: 16).

#### 8E: Update augmentation-rates table (line ~1224, `\label{tab:augmentation-rates}`)

Add two new columns for codex (`\codexshort{} (all dirs)` and `\codexshort{} (C→OMP)`). Codex augmentation data from `statistical_analysis.json > augmentation_curves > azure-gpt-5.3-codex`:
- Codex has 97 qualifying ablation pairs (all dirs), vs GPT-5.4's 99 and Qwen's 50
- L0: 62.7% (n=426), L1: 86.6% (n=97), L2: 88.7% (n=97), L3: 86.6% (n=97), L4: 85.6% (n=97)
- For C→OMP specifically, extract from `augmentation_per_kernel_matrix_azure-gpt-5.3-codex.json > primary_matrix > per_kernel` (aggregate the per-kernel PASS/total at each level)

Also update the caption to mention three models and codex's n=97.

#### 8F: Add codex eval-cost table (after line ~1510, after GPT-5.4 cost table)

Extract cost data:
```bash
python3 -c "
import json, glob
files = glob.glob('results/evaluation/azure-gpt-5.3-codex/*.json')
total_prompt = sum(json.load(open(f)).get('prompt_tokens', 0) for f in files)
total_comp = sum(json.load(open(f)).get('completion_tokens', 0) for f in files)
print(f'Files: {len(files)}')
print(f'Tokens: {(total_prompt+total_comp)/1e6:.1f}M ({total_prompt/1e6:.1f}M in, {total_comp/1e6:.1f}M out)')
"
```

Add the table using the same format as the existing GPT-5.4 cost table.

**Verify:** `grep -c "codex" docs/paper/NeurIPS_ready_version/appendices_neurips.tex` should be ≥ 15.

---

### STEP 9: Add Bibliography Entry

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib`

Add at the end of the file:

```bibtex
@misc{GPT53Codex2026,
  title   = {{GPT}-5.3-Codex System Card},
  author  = {{OpenAI}},
  year    = {2026},
  url     = {https://openai.com/index/gpt-5-3-codex-system-card/},
  note    = {Accessed 2026-05-01}
}
```

**Verify:** `grep GPT53Codex references.bib` should return the entry.

---

### STEP 10: Final Verification

Run all of these checks:

```bash
cd /home/samyak/Desktop/parbench_sam

# 1. Check no stale TBD placeholders
grep -rn '\\tbd' docs/paper/NeurIPS_ready_version/sections/ docs/paper/NeurIPS_ready_version/appendices_neurips.tex

# 2. Check all codex figure files exist
ls docs/paper/NeurIPS_ready_version/figures/f*codex*

# 3. Check codex macro is defined
grep 'codex' docs/paper/NeurIPS_ready_version/sections/macros.tex

# 4. Check "three models" appears in key sections
grep -l "three models" docs/paper/NeurIPS_ready_version/sections/*.tex

# 5. Check "two models" is fully replaced (should return 0)
grep -rn "two models" docs/paper/NeurIPS_ready_version/sections/*.tex

# 6. Check all % src: comments reference real files
grep '% src:' docs/paper/NeurIPS_ready_version/sections/results.tex | head -20

# 7. Verify total record count
python3 -c "print(626 + 822 + 814)"  # Should print 2262

# 8. Verify the codex PASS+BF+RF+VF+EF = 814
python3 -c "print(604 + 139 + 44 + 27 + 0)"  # Should print 814
```

---

## Summary of the New Findings to Weave In

These are the paper-ready claims from `docs/eval-findings/2026-05-01-three-model-comparison.md`:

1. **GPT-5.4 and codex are statistically indistinguishable** (p=1.0, OR=0.93), differing on only 8/142 tasks
2. **Both GPT models surpass Qwen by ~5x odds ratio** (Cohen's h ≈ 0.8, large effect)
3. **Direction is the strongest predictor** of difficulty (74.7pp spread), stronger than model choice (38.8pp)
4. **OpenCL as source is dramatically harder** than as target (opencl→cuda = 23.7% vs cuda→opencl = 60.1%)
5. **Augmentation compensates for capability gaps**: Qwen gains +50pp at L1 then declines; GPT models plateau
6. **ParBench's kernel difficulty spans 0%–95.1%**, with 9 kernels discriminating model tiers
7. **Performance gaps are driven by compile/runtime robustness** (BF:VF ratio), not semantic correctness

---

## What Could Go Wrong

| Risk | Mitigation |
|------|-----------|
| Direction table too wide with 3 columns + CIs | Use `\resizebox{\textwidth}{!}{...}` or move CIs to appendix |
| Paper exceeds 9-page NeurIPS limit | Move detailed comparison to appendix, keep main body concise |
| Figure script crashes on codex data | Check error output carefully; the script auto-discovers models from result dirs |
| LaTeX compile error from new macros | Test compile after Step 1 before proceeding |
| Overleaf merge conflict | User will sync manually after all changes are done locally |
| Augmentation section mentions "12-kernel subset" | Codex uses 97 L0-conditional pairs (not 12); clarify the denominator matches the analysis method |

---

## Dependencies Between Steps

```
Step 1 (macros) ──────────────────────────────── Must be first (all other steps use \codex{})
       │
Step 2 (figures) ─────────────────────────────── Must complete before Steps 3F, 8A (figure refs)
       │
Steps 3-7 (paper sections) ──────────────────── Can be done in any order after Steps 1-2
       │
Step 8 (appendices) ──────────────────────────── After Step 2 (needs figure files)
       │
Step 9 (bibliography) ────────────────────────── Any time (no dependencies)
       │
Step 10 (verification) ───────────────────────── Last step always
       │
/validate ────────────────────────────────────── Before any git commit
```

---

## To Start the Fresh Session

```
Open a new Claude Code session, then:
1. Read this file: /home/samyak/Desktop/parbench_sam/HANDOFF.md
2. Invoke: andrej-karpathy-skills:karpathy-guidelines
3. Start with Step 1
```
