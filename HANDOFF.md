# HANDOFF: NeurIPS 2026 Paper Rewrite — 2-Model Paper with Verified Data

**Date:** 2026-04-26
**Author:** Claude Code session (brainstorming + plan-reviewer adversarial review + data verification)
**Status:** Ready to implement — all data verified against JSONs on disk, plan-reviewer + Codex GPT-5.4 adversarial reviews resolved
**Audience:** Written for undergraduate software engineering clarity. Every path is absolute. Every number is verified.

---

## What Is This? (Plain English)

ParBench is a research project that tests how well AI models (LLMs) can translate code between parallel programming APIs (CUDA, OpenMP, OpenCL). We have **complete evaluation results** for one model (Qwen 3.5 397B) and **partial results** for a second model (GPT-5.4).

The NeurIPS 2026 paper needs a structured rewrite because:

1. **Model swap:** The paper currently references "GPT-4.1 mini" — this must change to "GPT-5.4" with red `\tbd{}` placeholders for missing data.
2. **Data correction:** The paper text was written against an **old dataset that was deleted**. The old data had temperature=0, 710 tasks, 38.3% pass rate, and 3 self-repair retries. The actual data on disk is completely different: temperature=0.7, 626 valid records, 36.7% overall, single-attempt (no self-repair). **Every number in the paper is wrong.**
3. **Structural cleanup:** Switch from one big LaTeX file to modular section files using `\input{}`.

### Key Concepts You Need

| Term | What It Means |
|------|--------------|
| **Canonical evaluation** | The main experiment: 3 random samples per task at L0 (no code perturbation), temp=0.7. Files end in `-s0.json`, `-s1.json`, `-s2.json`. There are **426 L0 records** (142 unique pairs x 3 samples). |
| **Ablation** | Follow-up runs at levels L1-L4 on a SUBSET of tasks. Tests robustness. Files end in `-L1.json` through `-L4.json`. There are **200 ablation records** (50 per level). |
| **Total valid records** | 426 + 200 = **626** (after excluding 82 KNOWN_FAIL-related records from 708 on disk). |
| **pass@k** | Standard metric (Chen et al. 2021): pass@k = probability at least 1 of k random samples passes. pass@1 <= pass@3 always. |
| **L0-L4** | Augmentation levels. L0 = original source. L1-L4 = increasingly aggressive AST transforms. |
| **KNOWN_FAIL** | **9** specs broken on our hardware. Always excluded from statistics. |
| **\tbd{}** | Red placeholder marker in LaTeX for GPT-5.4 data that doesn't exist yet. |
| **sections/** | Folder containing team-leader expanded versions of each paper section. These are the canonical source. |

---

## CRITICAL WARNINGS

### WARNING 1: The Old Paper Numbers Are ALL Wrong
The existing `.tex` files contain numbers from a **purged dataset**: 710 tasks, 38.3%, 64.2% CUDA-to-OMP, self-repair 22.5%→38.3%. **None of these numbers exist in the current data.** Do NOT copy them. Always read from `quantitative_findings.json`.

### WARNING 2: Self-Repair Is Dropped
The canonical data has `max_retries=1` (single attempt, no self-repair). The old paper's self-repair narrative cannot be supported. Remove all self-repair references from the paper. It becomes a "future work" item.

### WARNING 3: Augmentation Data Has Selection Bias (Simpson's Paradox)
L0 has 426 records across all 142 pairs. L1-L4 each have only 50 records from an **easier subset** of ~12-17 kernels. The Cochran-Armitage test in `quantitative_findings.json` shows z=7.65, p=0.0 with an "increasing" trend — but this is an **artifact** because L1-L4 only test kernels that already pass at L0. **Do NOT report this z-statistic.** Instead, report descriptive per-level rates on the balanced CUDA-to-OMP subset (12 kernels at all 5 levels).

### WARNING 4: Two Conflicting Results Files Exist
`results.tex` (in the `NeurIPS_ready_version/` root) is an older draft with different GPT numbers (161/551=29.2%) than `main_neurips.tex` inline (177/577=30.7%). **Both are wrong.** The inline version in `main_neurips.tex` is more recent. Extract it to `sections/results.tex`, then rewrite everything with canonical data.

### WARNING 5: `paper_data.json` Has an Empty Section
The `primary_campaign` section in `paper_data.json` is completely empty (all zeros). This is expected — the old primary campaign was purged. **All data is in the `passk_campaign` section.** Do not waste time looking for primary_campaign data.

### WARNING 6: Suite Summary Table Has Wrong KNOWN_FAIL Count
The paper says 8 KNOWN_FAIL and 88 PASS. The actual count is **9 KNOWN_FAIL** and **87 PASS**. Update Table 1 accordingly. Rodinia: 53 PASS, 7 KNOWN_FAIL (not 54/6).

### WARNING 7: `error_taxonomy.json` Mixes Models
This file contains combined Qwen + GPT-5.4 data (744 records). For Qwen-only failure claims, use `quantitative_findings.json` canonical.failure_taxonomy (626 records).

---

## Verified Data Ground Truth

**Source:** `/home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings.json` (canonical section)

All numbers below were verified on 2026-04-26 by reading the JSON directly.

### Overall

| Metric | Value | JSON path |
|--------|-------|-----------|
| Total on disk | 708 | metadata.file_counts.total_on_disk |
| Excluded (KNOWN_FAIL) | 82 | metadata.file_counts.excluded_known_fail |
| Valid after exclusion | 626 | metadata.file_counts.valid_after_exclusion |
| L0 records | 426 | canonical.augmentation_trends.aggregate.per_level.L0.n |
| L1 records | 50 | canonical.augmentation_trends.aggregate.per_level.L1.n |
| L2 records | 50 | canonical.augmentation_trends.aggregate.per_level.L2.n |
| L3 records | 50 | canonical.augmentation_trends.aggregate.per_level.L3.n |
| L4 records | 50 | canonical.augmentation_trends.aggregate.per_level.L4.n |
| Unique L0 pairs | 142 | canonical.pass_at_k.total_tasks.value |
| Overall pass rate | 36.7% [33.1%, 40.6%] | canonical.aggregate_pass_rates.overall |
| Temperature | 0.7 | all result files (verified via grep) |
| Max retries | 1 (no self-repair) | all result files (verified via grep) |
| KNOWN_FAIL specs | 9 | metadata.excluded_specs_count |

### pass@k (L0 only, 142 unique pairs, 3 samples each)

| Metric | Value | JSON path |
|--------|-------|-----------|
| pass@1 | 23.9% [17.9%, 30.0%] | canonical.pass_at_k.pass_at_1 |
| pass@3 | 35.2% [27.3%, 43.1%] | canonical.pass_at_k.pass_at_3 |
| Always pass (3/3) | 19 tasks (13.4%) | canonical.pass_at_k.task_classification.always_pass |
| Hard fail (0/3) | 92 tasks (64.8%) | canonical.pass_at_k.task_classification.hard_fail |
| Noisy (1-2/3) | 31 tasks (21.8%) | canonical.pass_at_k.task_classification.noisy_fail |

### Direction Pass Rates (L0, all records including 3 samples)

| Direction | Rate | n | JSON path |
|-----------|------|---|-----------|
| cuda-to-omp | 40.3% [29.7%, 51.8%] | 72 | canonical.direction_pass_rates.standard.cuda-to-omp |
| omp-to-cuda | 25.0% [16.4%, 36.1%] | 72 | ...standard.omp-to-cuda |
| omp-to-opencl | 33.3% [22.0%, 47.0%] | 51 | ...standard.omp-to-opencl |
| opencl-to-omp | 9.8% [4.3%, 21.0%] | 51 | ...standard.opencl-to-omp |
| cuda-to-opencl | 7.0% [2.8%, 16.7%] | 57 | ...standard.cuda-to-opencl |
| opencl-to-cuda | 0.0% [0.0%, 6.3%] | 57 | ...standard.opencl-to-cuda |
| cuda-to-omp_target | 0.0% [0.0%, 13.8%] | 24 | ...case_study.cuda-to-omp_target |
| omp_target-to-cuda | 66.7% [46.7%, 82.0%] | 24 | ...case_study.omp_target-to-cuda |

### Failure Taxonomy (all 626 valid records)

| Status | Count | Rate | JSON path |
|--------|-------|------|-----------|
| PASS | 230 | 36.7% | canonical.failure_taxonomy.status_counts.PASS |
| BUILD_FAIL | 245 | 39.1% | ...BUILD_FAIL |
| RUN_FAIL | 121 | 19.3% | ...RUN_FAIL |
| VERIFY_FAIL | 29 | 4.6% | ...VERIFY_FAIL |
| EXTRACTION_FAIL | 1 | 0.2% | ...EXTRACTION_FAIL |

### Augmentation (Balanced CUDA-to-OMP Subset)

**12 kernels present at all 5 levels.** Computed directly from result files on 2026-04-26:

| Level | Per-sample rate | n records | Kernels with any pass |
|-------|----------------|-----------|----------------------|
| L0 | 29/36 = 80.6% | 36 (12 kernels x 3 samples) | 12/12 = 100% |
| L1 | 9/12 = 75.0% | 12 | 9/12 = 75% |
| L2 | 10/12 = 83.3% | 12 | 10/12 = 83.3% |
| L3 | 9/12 = 75.0% | 12 | 9/12 = 75% |
| L4 | 10/12 = 83.3% | 12 | 10/12 = 83.3% |

**Narrative:** Pass rates are stable across augmentation levels (75-83%), with no evidence of monotonic degradation. The sample size (n=12 per level) is too small for a formal trend test — report descriptive rates only.

**Balanced kernels:** bfs, cfd, floydwarshall, heat2d, hotspot3d, iso2dfd, lud, nw, particlefilter, pathfinder, srad, stencil1d.

### GPT-5.4 Data

81 result files exist in `/home/samyak/Desktop/parbench_sam/results/evaluation/azure-gpt-5.4/` (count as of 2026-04-26; may grow). This is incomplete. **All GPT-5.4 cells in the paper use `\tbd{}` placeholders.**

---

## Skills to Load at Session Start

Before doing ANY work, invoke these skills. They guide HOW you work:

```
Skill("andrej-karpathy-skills:karpathy-guidelines")  -- Think before coding, surgical changes, simplicity first
Skill("test-driven-development")                       -- Gated TDD for any code changes (figure scripts, analysis)
```

For paper writing assistance:
```
Skill("ml-paper-writing")                              -- NeurIPS paper writing conventions (or use research-paper-writing)
Skill("deslop")                                        -- Remove AI writing patterns from prose
```

At verification points:
```
Skill("cite-check")                                    -- Verify citations match references.bib before committing
Skill("validate")                                      -- Run waves 1-3 before any git commit
```

For simulating reviewer feedback (optional but recommended):
```
Skill("paper-review-sim")                              -- Simulate NeurIPS reviewer feedback on draft
```

---

## Working Directory and Prerequisites

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
```

**Prerequisite checks (run these first):**
```bash
# LaTeX compiler available?
which tectonic || which pdflatex || which latexmk

# scienceplots installed (needed for figure generation)?
python3 -c "import scienceplots; print('OK')"

# If scienceplots is missing:
# python3 -m pip install scienceplots

# Verify data exists
ls /home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings.json
ls /home/samyak/Desktop/parbench_sam/results/evaluation/together-qwen-3.5-397b-a17b/ | wc -l
# Should show 708
```

**Create backup before starting (rollback safety net):**
```bash
cp -r /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version \
      /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version.bak
```

---

## Absolute Path Reference

Every file path in this document is absolute. Here's the master list:

| Short name | Absolute path |
|------------|---------------|
| PROJECT_ROOT | `/home/samyak/Desktop/parbench_sam` |
| PAPER_DIR | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version` |
| SECTIONS | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections` |
| FIGURES | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures` |
| MAIN_TEX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex` |
| APPENDIX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex` |
| REFS_BIB | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib` |
| QF_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings.json` |
| PD_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/paper_data.json` |
| ET_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/error_taxonomy.json` |
| BC_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/benchmark_characterization.json` |
| SLOC_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/sloc_analysis.json` |
| FIG_SCRIPT | `/home/samyak/Desktop/parbench_sam/scripts/generate_paper_figures.py` |
| OLD_SC | `/home/samyak/Desktop/parbench_sam/docs/paper/old_sc_draft/main.tex` |
| REWRITE_MEMO | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/rewrite_memo.md` |

---

## Step-by-Step Implementation

### Phase 1: Structural Setup

#### Step 1.1: Create `sections/macros.tex`

**Create:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/macros.tex`

This file centralizes ALL LaTeX macros (model names, placeholders, failure categories). When GPT-5.4 data arrives later, you change model names in ONE place.

Key macros to define:
- `\qwen` → `Qwen~3.5 397B-A17B`, `\qwenshort` → `Qwen~3.5`
- `\gptnew` → `GPT-5.4`, `\gptprovider` → `Azure~OpenAI`
- `\tbd` → red bold "TBD" placeholder (with optional context argument)
- `\parbench`, `\buildfail`, `\runfail`, `\verifyfail`, `\extractionfail`, `\pass`, `\fail`, `\knownfail`

**Verification:** File exists and contains all macros listed above.

#### Step 1.2: Restructure `main_neurips.tex`

**Edit:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex`

Replace all inline section content (lines 86-340) with `\input{sections/...}` calls:
```latex
\input{sections/macros}  % Before \begin{document}

\begin{document}
\maketitle
\input{sections/abstract}
\input{sections/1-introduction}
\input{sections/framework}
\input{sections/benchmark-curation}
\input{sections/experimental-setup}
\input{sections/results}
\input{sections/related-work}
\input{sections/discussion}

\bibliographystyle{plainnat}
\bibliography{references}
\appendix
\input{appendices_neurips}
\end{document}
```

Remove all `\newcommand` definitions from the preamble (they're now in macros.tex). Keep: package imports, `\graphicspath`, `\lstset`, `\title`, `\author`.

**Verification:** `grep -c '\\input{sections/' /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex` — should return 9 (1 macros + 8 sections).

#### Step 1.3: Extract missing section files from `main_neurips.tex`

Create these NEW files by extracting from `main_neurips.tex`:

| New file | Extract from main_neurips.tex lines | Notes |
|----------|-------------------------------------|-------|
| `sections/abstract.tex` | 86-88 (`\begin{abstract}...\end{abstract}`) | Will be rewritten in Phase 3 |
| `sections/experimental-setup.tex` | 175-183 (Section 5) | Will be rewritten in Phase 3 |
| `sections/related-work.tex` | 316-324 (Section 6) | Will be updated in Phase 3 |
| `sections/discussion.tex` | 327-333 (Section 7) | Will be rewritten in Phase 3 |

**Also:** Delete the standalone `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/results.tex` — it's an older conflicting draft. Extract the inline results from `main_neurips.tex` (lines 184-314) into `sections/results.tex` instead.

**Label preservation:** After extraction, verify all `\label` commands were preserved:
```bash
grep -c 'label{sec:' /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex
# Compare with:
grep -rc 'label{sec:' /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/
# The total from sections/ should match or exceed main_neurips.tex
```

Note: `main_neurips.tex` line 143 has TWO labels on consecutive lines (`sec:benchmark-curation` and `sec:suite-selection`). Make sure both are preserved in `sections/benchmark-curation.tex`.

#### Step 1.4: Regenerate figures BEFORE compilation

Compilation requires figures to exist. The old figures at `docs/paper/figures/` are deleted in the working tree. Regenerate them NOW, before attempting any LaTeX build:

```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
python3 -c "import scienceplots; print('OK')"  # If fails: pip install scienceplots

python3 /home/samyak/Desktop/parbench_sam/scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures
```

Then create GPT-5.4 placeholder figures:
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures
for f in f3_kernel_model_heatmap_gpt f4_failure_taxonomy_gpt f5_pass_at_k_by_direction_gpt f6_cross_suite_comparison_gpt; do
  python3 -c "
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,4))
ax.text(0.5, 0.5, 'GPT-5.4 data pending', ha='center', va='center', fontsize=16, color='red')
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
fig.savefig('${f}.pdf', bbox_inches='tight')
plt.close()
"
done
```

**Verification:** ALL 5 Qwen figures must exist:
```bash
for f in f3_kernel_model_heatmap_qwen f4_failure_taxonomy_qwen f5_pass_at_k_by_direction_qwen f6_cross_suite_comparison_qwen f7_augmentation_robustness; do
  ls /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/${f}.pdf && echo "OK: $f" || echo "MISSING: $f"
done
```

#### Step 1.5: Verify compilation

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version && tectonic main_neurips.tex
# OR: cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version && pdflatex main_neurips.tex
```

**IMPORTANT:** Compile from INSIDE the `NeurIPS_ready_version/` directory so `\graphicspath{{figures/}}` resolves correctly. Also remove the broken second graphicspath entry `{../../analysis/visualizations/}` from `main_neurips.tex` — that path does not exist.

**Verification:** No errors. Check: `grep -c 'undefined' main_neurips.log` — should be 0 (or only expected undefined references from first pass).

---

### Phase 2: Model Swap + Data Correction

#### Step 2.1: Replace GPT-4.1 mini with GPT-5.4

In ALL `.tex` files under `NeurIPS_ready_version/`:

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
grep -rl "GPT-4.1" . --include="*.tex" | head -20  # Find all files
# Then do the replacements:
# GPT-4.1~mini → GPT-5.4
# GPT-4.1 mini → GPT-5.4
# gpt-4.1-mini → gpt-5.4
# gpt-4.1 mini → gpt-5.4
```

**Verification:**
```bash
grep -r "GPT-4.1" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"
# Should return 0 results
```

#### Step 2.2: Replace GPT-specific numbers with `\tbd{}`

Every table cell and inline claim that references GPT-4.1 mini numbers must become `\tbd{}`. This includes:
- 177/577 → `\tbd{}`
- 30.7% → `\tbd{}`
- All per-direction GPT rates
- Aggregate rows that combine both models → either Qwen-only or `\tbd{}`
- All chi-squared cross-model comparisons → `\tbd{}`

#### Step 2.3: Correct ALL Qwen numbers to canonical data

Replace every Qwen number with verified values from the Data Ground Truth table above. Key corrections:

| Old (wrong) | New (correct) | Where |
|-------------|---------------|-------|
| 710 tasks | 626 valid records | Abstract, Intro, Setup, Results |
| 38.3% overall | 36.7% [33.1%, 40.6%] | Abstract, Results Table 1 |
| 64.2% CUDA-to-OMP | 40.3% [29.7%, 51.8%] | Abstract, Results direction table |
| 52.5% OMP-to-CUDA | 25.0% [16.4%, 36.1%] | Results direction table |
| 33.9% BUILD_FAIL | 39.1% (245/626) | Results failure section |
| 7.2% VERIFY_FAIL | 4.6% (29/626) | Results failure section |
| Self-repair 22.5%→38.3% | **DELETE ENTIRELY** | Results (was subsection) |
| z=0.0, p=1.0 augmentation | Drop formal test; use descriptive rates | Results augmentation section |
| 88 PASS, 8 KNOWN_FAIL | 87 PASS, 9 KNOWN_FAIL | Suite summary table |

**Verification:**
```bash
grep -r "38\.3" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"
grep -r "710" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"
grep -ri "self.repair" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"
# All should return 0 relevant hits (710 might appear in non-task-count contexts)
```

---

### Phase 3: Section-by-Section Writing (front-to-back)

Write each section using `sections/` team-leader versions as the canonical narrative base. Update numbers from Data Ground Truth.

| # | Section | File | Status | Effort |
|---|---------|------|--------|--------|
| 1 | Abstract | `sections/abstract.tex` | REWRITE | High — all numbers change |
| 2 | Introduction | `sections/1-introduction.tex` | MODERATE EDIT | Medium — fix numbers, remove "deterministic decoding", remove self-repair refs |
| 3 | Framework | `sections/framework.tex` | MODERATE EDIT | Medium — remove self-repair from prose and figure caption (line 4, line 9) |
| 4 | Benchmark Curation | `sections/benchmark-curation.tex` | MINOR EDIT | Low — update KNOWN_FAIL count (9 not 8), PASS count (87 not 88) |
| 5 | Experimental Setup | `sections/experimental-setup.tex` | REWRITE | High — temp=0.7, no self-repair, new task counts |
| 6 | Results | `sections/results.tex` | MAJOR REWRITE | Very high — every number changes, drop self-repair subsection |
| 7 | Related Work | `sections/related-work.tex` | MODERATE UPDATE | Medium — add 7 missing papers |
| 8 | Discussion | `sections/discussion.tex` | MODERATE REWRITE | Medium — 2-model framing, updated limitations |

#### Section-specific notes:

**Abstract:** Use canonical Qwen numbers + `\tbd{}` for GPT-5.4. Frame as stochastic evaluation. Mention pass@k framing. No self-repair claims.

**Introduction:** The team-leader version at `sections/1-introduction.tex` is mostly stable BUT:
- Line 15: "51.3% vs 22.2% for multi-file" — needs rechecking against canonical data (file coordination data may not be precomputed).
- Line 33: "deterministic decoding" — change to "stochastic sampling" (temp=0.7).
- Contribution bullet #3: Remove "deterministic decoding" reference, update task count.

**Framework:** The team-leader version at `sections/framework.tex` has **6 self-repair references** (not just 2). Remove or reframe ALL of them:
- **Line 4:** "an evaluation pipeline that augments the LLM-based translation with an iterative self-repair" — remove self-repair from the component list.
- **Line 9** (figure caption): "On failure, a dashed self-repair feedback loop returns failure-specific diagnostics for up to three iterative retry attempts" — remove or soften to describe framework capability without claiming it was used.
- **Line 77:** "On failure, a self-repair feedback loop (dashed orange arrow in Figure~\ref{fig:architecture}) returns diagnostic information..." — remove or soften.
- **Line 100:** `\textbf{Self-repair loop.}` — entire paragraph describes the self-repair mechanism. Remove entirely or reframe as "the framework supports optional self-repair (not used in this evaluation)."
- **Line 147:** "All three self-repair attempts reproduce the same incorrect output" — rewrite example without self-repair framing.
- **Line 155:** Commented-out block with "All three self-repair attempts" — delete the commented block.
- **Lines 79-83:** Commented-out paragraphs with old numbers (64.2%, 710 tasks) — delete these comments.
- **NOTE:** The architecture figure (`parbench_architecture.png`) visually shows a dashed self-repair arrow. Consider whether the figure needs updating or if a caption note suffices ("the dashed self-repair path is a framework capability not exercised in the evaluation reported here").

**Benchmark Curation:** Update KNOWN_FAIL count from 8 to 9, PASS from 88 to 87. Rodinia: 53 PASS, 7 KNOWN_FAIL.

**Experimental Setup:** Describe the actual experiment: temp=0.7, stochastic sampling, single-attempt (max_retries=1), 142 L0 pairs x 3 samples each (426 records), L1-L4 on eligible subset (50 records each, 200 total). No self-repair protocol. GPT-5.4 as `\tbd{}`.

**Results:** Major rewrite. Every subsection gets new numbers from `quantitative_findings.json`. Drop self-repair subsection entirely. Drop file coordination subsection (data not precomputed) or compute from raw results. For augmentation: report descriptive per-level rates on balanced CUDA-to-OMP subset (12 kernels), do NOT use the misleading Cochran-Armitage z-statistic from the JSON.

**Related Work:** 5 of the 7 previously "missing" papers are already in `references.bib` and cited in the paper (verified 2026-04-26):
- **Already cited:** LASSI (4 cites), CodeRosetta (3 cites), HPC-Coder-v2 (4 cites), TRACY (4 cites), SWE-bench Illusion (in bib, uncited — add `\cite{SWEbenchIllusion2025}` in the augmentation/contamination discussion)
- **Genuinely missing (must add BibTeX + citations):** VibeCodeHPC (arxiv:2510.00031), QiMeng-MuPa (arxiv:2506.11153)
- Add BibTeX entries for VibeCodeHPC and QiMeng-MuPa to `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib`
- Verify existing citations are positioned correctly for the NeurIPS D&B track framing

**Discussion:** Reframe for 2-model story (Qwen complete, GPT-5.4 pending). Limitations: stochastic eval only, no self-repair in this evaluation, small augmented subset (n=12 for balanced test). Future work: GPT-5.4 completion, self-repair experiments, additional models, efficiency evaluation.

---

### Phase 4: Figures

#### Step 4.1: Regenerate Qwen figures

```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
python3 /home/samyak/Desktop/parbench_sam/scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures
```

The script already has `azure-gpt-5.4` configured in its `MODEL_COLORS` dict (verified at line 84-87 of the script).

**If the script fails:** Check `python3 -c "import scienceplots"`. If missing: `pip install scienceplots`.

**Verification:**
```bash
ls /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/f3_kernel_model_heatmap_qwen.pdf
ls /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/f4_failure_taxonomy_qwen.pdf
# Both should exist
```

#### Step 4.2: Create GPT-5.4 placeholder figures

Generate minimal placeholder PDFs for GPT-5.4 figures so LaTeX compiles:
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures
for f in f3_kernel_model_heatmap_gpt f4_failure_taxonomy_gpt f5_pass_at_k_by_direction_gpt f6_cross_suite_comparison_gpt; do
  echo "GPT-5.4 data pending" | python3 -c "
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,4))
ax.text(0.5, 0.5, 'GPT-5.4 data pending', ha='center', va='center', fontsize=16, color='red')
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
fig.savefig('${f}.pdf', bbox_inches='tight')
plt.close()
"
done
```

**Verification:** `ls /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures/*gpt*.pdf | wc -l` — should be 4.

#### Step 4.3: Update `\includegraphics` paths in all `.tex` files

Verify all figure references point to files that exist in the `figures/` directory.

---

### Phase 5: Appendix Update

**File:** `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex`

1. Replace all `GPT-4.1 mini` → `GPT-5.4` (11+ occurrences)
2. Replace GPT-specific numbers in appendix tables with `\tbd{}`
3. **CRITICAL: Remove self-repair figures and narrative.** Lines 751 and 798 have `\includegraphics` for `c1_repair_transition_matrix.pdf` and `c2_repair_rate_by_direction.pdf` — these files do NOT exist and will cause LaTeX errors. Comment out or delete these `\includegraphics` lines AND the surrounding ~100-line self-repair narrative block (approximately lines 717-820). Search with: `grep -n "repair\|self.repair\|transition_matrix\|repair_rate" appendices_neurips.tex`
4. Update model config table for GPT-5.4
5. Update pass@k table to match canonical data (pass@1=23.9%, pass@3=35.2%)
6. Update GPT figures section to reference placeholder figures

**Verification:**
```bash
grep -c "GPT-4.1" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex
# Should be 0
```

---

### Phase 6: Final Compilation and Verification

```bash
# 1. Compile
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
tectonic main_neurips.tex  # or pdflatex + bibtex + pdflatex x2

# 2. Check for problems
grep -c "undefined" main_neurips.log   # Should be 0
grep -c "multiply defined" main_neurips.log  # Should be 0

# 3. Global checks
grep -r "GPT-4.1" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"  # 0 hits
grep -r "38\.3" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"  # 0 relevant hits
grep -ri "self.repair" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex"  # 0 hits (except maybe framework describing the capability)

# 4. TBD markers visible
grep -r "tbd\|TBD" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/ --include="*.tex" | wc -l
# Should be >0 (GPT-5.4 placeholders)

# 5. Open the PDF and visually verify red TBD markers appear

# 6. Run /validate before any commit (REQUIRED — pre-commit hook enforces waves 1-3)
# Invoke: Skill("validate")

# 7. Run Codex review for GPT-5.4 second opinion on all changes
# Invoke: /codex:rescue review the uncommitted changes
# Then: touch .codex_review_done
```

---

## What Worked in This Session

- **Data-first verification**: Reading `quantitative_findings.json` directly exposed that every number in the paper is wrong.
- **Plan-reviewer adversarial review**: Found 20 issues including wrong sub-breakdowns in the data table, conflicting results files, empty `primary_campaign`, and missing skill specifications.
- **Augmentation balanced subset analysis**: Directly computed per-kernel pass rates from result files, proving the Simpson's paradox in the aggregate trend test.

## What Didn't Work / Traps to Avoid

- **Don't trust numbers in the existing .tex files** — they're from a purged dataset.
- **Don't use the Cochran-Armitage z-statistic from quantitative_findings.json** — it's misleading due to sample size imbalance between L0 and L1-L4.
- **Don't confuse the two results.tex files** — the standalone one is older and has different numbers.
- **Don't look for self-repair data** — it doesn't exist in the canonical evaluation.
- **Don't compile from the project root** — compile from inside `NeurIPS_ready_version/` so `\graphicspath` resolves.
- **Don't use relative paths in bash commands** — always absolute paths from `/home/samyak/Desktop/parbench_sam`.

---

## Files to Create/Modify (Complete List)

| File (absolute path) | Action |
|----------------------|--------|
| `.../NeurIPS_ready_version/sections/macros.tex` | **CREATE** |
| `.../NeurIPS_ready_version/sections/abstract.tex` | **CREATE** (extract from main_neurips.tex, then rewrite) |
| `.../NeurIPS_ready_version/sections/experimental-setup.tex` | **CREATE** (extract, then rewrite) |
| `.../NeurIPS_ready_version/sections/related-work.tex` | **CREATE** (extract, then update) |
| `.../NeurIPS_ready_version/sections/discussion.tex` | **CREATE** (extract, then rewrite) |
| `.../NeurIPS_ready_version/sections/results.tex` | **CREATE** (extract inline from main, then major rewrite) |
| `.../NeurIPS_ready_version/results.tex` | **DELETE** (older conflicting draft) |
| `.../NeurIPS_ready_version/main_neurips.tex` | **REWRITE** (restructure to \input{} pattern) |
| `.../NeurIPS_ready_version/sections/1-introduction.tex` | **EDIT** (fix numbers, remove deterministic/self-repair refs) |
| `.../NeurIPS_ready_version/sections/framework.tex` | **EDIT** (remove self-repair from prose and figure caption) |
| `.../NeurIPS_ready_version/sections/benchmark-curation.tex` | **EDIT** (9 KNOWN_FAIL, 87 PASS) |
| `.../NeurIPS_ready_version/appendices_neurips.tex` | **EDIT** (model swap, table updates, remove self-repair) |
| `.../NeurIPS_ready_version/references.bib` | **EDIT** (add 7 missing citations) |
| `.../NeurIPS_ready_version/figures/*.pdf` | **REGENERATE** (Qwen figures + GPT-5.4 stubs) |

## Read-Only Reference Files

| File | What it provides |
|------|-----------------|
| `results/analysis/quantitative_findings.json` | ALL canonical Qwen numbers (single source of truth) |
| `results/analysis/paper_data.json` | pass@k details (use `passk_campaign` section, NOT `primary_campaign`) |
| `results/analysis/error_taxonomy.json` | Build failure examples (WARNING: mixed Qwen+GPT data) |
| `results/analysis/benchmark_characterization.json` | Corpus characterization (stable) |
| `results/analysis/sloc_analysis.json` | SLoC statistics (stable) |
| `docs/paper/old_sc_draft/main.tex` | Salvageable prose for pre-methodology sections |
| `docs/paper/NeurIPS_ready_version/rewrite_memo.md` | Documents what moved where in the original NeurIPS rewrite |
| `scripts/generate_paper_figures.py` | Figure generation (already configured for GPT-5.4) |
