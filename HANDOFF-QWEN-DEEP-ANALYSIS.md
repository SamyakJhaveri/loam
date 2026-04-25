# HANDOFF: Qwen Canonical + Ablation Deep Analysis (All 14 Dimensions)

**Date:** 2026-04-24
**Author:** Claude Code session (brainstorming + codebase exploration)
**Status:** Plan complete, ready to execute Phase A (script runs)
**Audience:** Undergrad clarity. Follow every step in order. Do not skip ahead.

---

## What Is This? (Plain English)

We have 708 evaluation result JSONs from running Qwen 3.5 397B on ParBench's parallel code translation benchmark (CUDA ↔ OpenMP ↔ OpenCL). The data is sitting in `results/evaluation/together-qwen-3.5-397b-a17b/`. Nobody has systematically analyzed it yet across all dimensions. We need to dissect every aspect before writing the NeurIPS 2026 paper.

### Goal

Build **deep, grounded understanding** of Qwen's performance across all 14 quantitative dimensions defined in `quantitative_findings.py`. Understanding first, then paper artifacts (tables, figures, LaTeX). Single-model analysis only — no GPT-5.4 results yet.

---

## Current Progress

| Item | Status | Details |
|------|--------|---------|
| Codebase exploration | DONE | Mapped all 13+ analysis scripts, 6 skills, 1 agent |
| Data inventory | DONE | 708 result JSONs: 504 canonical (s0/s1/s2) + 204 ablation (L0-L4) |
| Analysis plan | DONE | 5-phase plan at `~/.claude/plans/we-need-to-run-fluttering-ullman.md` |
| User scope decisions | DONE | Deep understanding first; all 14 dimensions; Qwen only |
| Script execution | NOT STARTED | None of the analysis scripts have been run yet |
| Interpretation | NOT STARTED | No dimension-by-dimension analysis done yet |

---

## What Worked

- **3 parallel Explore agents** efficiently mapped the full toolkit in one turn: scripts, data files, and skills
- **User clarity**: "Deep understanding first" and "All 14 dimensions" gave clean scope
- **Rich existing infrastructure**: 13+ analysis scripts already exist — no new code needed for data generation

## What Didn't Work

- Nothing failed — session ended before execution began (user chose handoff to new session after plan review)

---

## Data Corpus Summary

**Location:** `results/evaluation/together-qwen-3.5-397b-a17b/` (708 JSON files)

| Category | Files | Notes |
|----------|-------|-------|
| Canonical (s0, s1, s2) | 504 | 3 samples × 168 (kernel, direction) pairs at L0 |
| Ablation (L1-L4) | 204 | 1 sample × ~51 pairs per level (only L0 passers) |

**Key headline numbers** (from `eval_summary.json`, generated 2026-04-24):
- 642 total tasks, 235 PASS (**36.6%** overall)
- L0 baseline: **23.7%** (104/438)
- L1-L4 (conditional on L0 pass): 74.5% → 64.7% → 62.7% → 54.9%
- Best direction: omp_target→omp (**95.2%**), worst: cuda→omp_target, opencl→cuda (**0%**)
- 251 BUILD_FAIL, 121 RUN_FAIL, 34 VERIFY_FAIL, 1 EXTRACTION_FAIL
- **0 self-repair successes** (max_retries=1)

---

## Next Steps: Execute the Plan

### Phase A: Generate Core Data Files (~5 min)

Run these scripts in order. **A1 must run first** (produces `paper_data.json` consumed by A2, A3). After A1, the rest can run in parallel.

```bash
source env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
```

**A1. Paper data (run FIRST — single source of truth):**
```bash
python3 scripts/analysis/generate_paper_data.py \
  --results-dir results/evaluation/together-qwen-3.5-397b-a17b \
  --output results/analysis/paper_data.json -v
```

**A2. Quantitative findings (all 14 dimensions):**
```bash
python3 scripts/analysis/quantitative_findings.py \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

**A3. Statistical analysis (CIs, effect sizes, significance):**
```bash
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A4. Error taxonomy:**
```bash
python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A5. Augmentation analysis (per-kernel × per-level matrix + heatmap):**
```bash
python3 scripts/analysis/augmentation_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A6. Self-repair analysis:**
```bash
python3 scripts/analysis/selfrepair_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A7. Token/cost analysis:**
```bash
python3 scripts/analysis/token_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A8. SLoC analysis:**
```bash
python3 scripts/analysis/sloc_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A9. Benchmark characterization:**
```bash
python3 scripts/analysis/benchmark_characterization.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**A10. Refreshed eval summary:**
```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam --show-gaps
```

**Outputs:** All go to `results/analysis/*.json` + `.md` (and `results/evaluation/eval_summary.*` for A10).

---

### Phase B: Dimension-by-Dimension Interpretation (~30 min)

After Phase A, read each output file and extract per dimension:
- **Raw numbers** (with file path provenance)
- **Key finding** (1 sentence)
- **Surprise** (what deviates from expectation)
- **Paper-worthiness** (publishable insight?)
- **Caveats** (confounds, small-N warnings)

**The 14 dimensions:**

| # | Dimension | Source File |
|---|-----------|-------------|
| D1 | Aggregate pass rates | `paper_data.json`, `eval_summary.json` |
| D2 | Per-direction rates | `quantitative_findings.json` → D2 |
| D3 | Direction asymmetry | `quantitative_findings.json` → D3, `statistical_analysis.json` (McNemar) |
| D4 | Augmentation trends | `augmentation_per_kernel_matrix.json`, `quantitative_findings.json` → D4 |
| D5 | Failure taxonomy | `error_taxonomy.json` |
| D6 | Self-repair effectiveness | `selfrepair_analysis.json` |
| D7 | pass@k estimates | `quantitative_findings.json` → D7 |
| D8 | Per-kernel difficulty tiers | `quantitative_findings.json` → D8 |
| D9 | Translation complexity correlation | `quantitative_findings.json` → D9, `translation_complexity.csv` |
| D10 | Cross-suite comparison | `quantitative_findings.json` → D10 |
| D11 | Token cost analysis | `token_analysis.json` |
| D12 | SLoC correlation | `sloc_analysis.json`, `quantitative_findings.json` → D12 |
| D13 | OpenCL kernel-only effect | `quantitative_findings.json` → D13 |
| D14 | Provenance & paper claims | `quantitative_findings.json` → D14 |

---

### Phase C: Cross-Dimensional Synthesis (~15 min)

Combine dimensions into 4 narrative stories for the paper:

1. **Direction hierarchy** (D2 + D3 + D5): WHY some directions work and others don't
2. **Augmentation effect** (D4 + D8): Which kernels benefit from augmentation and why
3. **Difficulty predictors** (D8 + D9 + D12): What makes a kernel hard to translate
4. **Cost-effectiveness** (D1 + D7 + D11): Practical utility of LLM translation

Use `/interpret-results` skill with stated hypotheses for each story (skill requires EXPECTATION, NULL HYPOTHESIS, FALSIFICATION before reading data).

---

### Phase D: Rigor Check (~10 min)

1. `/grill-research` on top 3 claims
2. Spot-check 5-10 individual result JSONs vs aggregates
3. Known confounds to address: header confusion (~18 BUILD_FAILs), KNOWN_FAIL pollution (8 PASS from broken sources), verification mode asymmetry (527 cross_api vs 181 kernel_only)

---

### Phase E: Paper Artifacts (after understanding is solid)

```bash
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir docs/paper/figures
```

Produces: F2 (pass rate by model), F3 (augmentation effect), F4 (kernel tiers), F5 (token cost), F6 (error taxonomy), F7 (self-repair), plus appendix C.1-C.4.

---

## Skills to Use During Analysis

| Skill | When | What it does |
|-------|------|-------------|
| `/post-eval` | Phase A | Orchestrates analyze_eval.py + classify_pairs + dashboard refresh |
| `/eval-grader` | Phase B | Structured grading with KNOWN_FAIL exclusion, pass-rate tables |
| `/interpret-results` | Phase C | Hypothesis-first interpretation (requires prior hypothesis BEFORE data) |
| `/grill-research` | Phase D | Adversarial interrogation of claims (requires null hypothesis) |
| `/cuda-omp-translator` | Phase B (D5) | Translation pattern reference for diagnosing failures |
| `/paper-review-sim` | After Phase E | 5-reviewer simulated SC26 review |

---

## Key Gotchas

1. **`overall_status` is authoritative** — never use `run_status` (can be stale from non-final attempts)
2. **Ablation L1-L4 is conditional** — only counts kernels that passed L0 (denominator differs from L0)
3. **Self-repair is 0%** — max_retries=1 produced zero successful repairs. This is a finding, not a bug.
4. **Wall-clock timing is unreliable** for speedup claims — `translated_cpu_time_seconds` and `translated_kernel_time_seconds` are always null
5. **8 KNOWN_FAIL specs excluded** from denominators (see `known-issues.md` for the list)
6. **Header confusion** accounts for ~18/290 BUILD_FAILs — partially a prompt design artifact, not pure model failure
7. **Wilson CIs required** for all pass rates — never report point estimates without confidence intervals

---

## Files Summary

| File | What | Path |
|------|------|------|
| Raw results | 708 Qwen eval JSONs | `results/evaluation/together-qwen-3.5-397b-a17b/*.json` |
| Eval summary | Aggregated stats | `results/evaluation/eval_summary.{json,md}` |
| Analysis outputs | Generated in Phase A | `results/analysis/*.{json,md}` |
| Figure generator | Publication figures | `scripts/generate_paper_figures.py` |
| Paper data script | Single source of truth | `scripts/analysis/generate_paper_data.py` |
| 14 dimensions | All quantitative findings | `scripts/analysis/quantitative_findings.py` |
| Full plan | Detailed execution plan | `~/.claude/plans/we-need-to-run-fluttering-ullman.md` |

---

## What NOT To Do

| Don't | Why | Instead |
|-------|-----|---------|
| Skip Phase A (script runs) | All interpretation depends on generated data files | Run A1 first, then A2-A10 |
| Read `run_status` for verdicts | Can be stale from non-final attempt | Always use `overall_status` |
| Report pass rates without CIs | Point estimates mislead with N < 100 | Wilson score 95% CIs everywhere |
| Claim speedup from `speedup_ratio` | Based on unreliable wall-clock sub-ms baselines | Note timing limitation in caveats |
| Skip hypothesis for `/interpret-results` | Skill enforces prior hypothesis to prevent post-hoc rationalization | State EXPECTATION, NULL, FALSIFICATION first |
| Modify result JSONs | Immutable by project invariant | Use `--resume` if re-running |
