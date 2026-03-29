# Next Session Roadmap — ParBench SC26

**Generated:** 2026-03-28, **Updated:** 2026-03-29
**Last session:** Session 12 — Campaign launch preparation + related work research
**SC26 deadline:** April 8, 2026 (10 days remaining)
**Project root:** `/home/samyak/Desktop/parbench_sam`

---

## 0. Session Update — March 29, 2026

### DECISIONS MADE

1. **2-Model Eval Campaign (D1):** The primary campaign uses exactly 2 models:
   - **Qwen 3.5 397B-A17B** (`together-qwen-3.5-397b-a17b`) via Together AI — large MoE architecture (397B total / 17B active)
   - **Gemini 2.5 Flash** (`gemini-2.5-flash`) via Google AI — dense architecture
   - The previous 3-model pilot lineup (Claude Sonnet, Gemini Flash Lite, Groq Llama 70B) is superseded. Pilot data stashed to `results/evaluation_backup_20260328/`.
   - A 3rd model may be added later without infrastructure changes.

2. **Division of Labor:** Samyak runs Qwen on the Linux GPU machine (RTX 4070). Erel runs Gemini on their machine. Both use the identical `run_eval_campaign.sh` script.

3. **Campaign Scope (D2):** 790 tasks per model = 5 suites x 6 directions x ~26 spec-pairs x 5 augmentation levels (L0-L4).

4. **Self-Repair Protocol (D3):** Primary campaign uses `max_retries=3`, `temperature=0.0`, `num_samples=1`. Each task gets up to 3 LLM calls with iterative error feedback.

5. **pass@k Sweep (D4):** Separate sweep at L0 only, `temperature=0.7`, `num_samples=5`, `max_retries=1` (zero-shot per sample). Measures sampling variance orthogonal to augmentation.

6. **Single Parameterized Script (D5):** `scripts/batch/run_eval_campaign.sh MODEL [MODE]` replaces per-model scripts. Old `run_qwen_campaign.sh` deleted; `run_gemini_campaign.sh` was created and removed within the session (never committed).

All decisions are formally documented with rationale and reviewer-ready defenses in `docs/experimental_decisions_log.md` (7 decisions D1-D7, 5 insights I1-I5).

### COMPLETED THIS SESSION

- [x] **Augmentation smoke tests:** 50/50 PASS across RSBench (3), mixbench (3), HeCBench (4 spot-checked) at L0-L4. Level-invariance confirmed for all 64 non-KNOWN_FAIL specs across 5 suites (D6).
- [x] **`.cc` suffix bug fixed** in `harness/spec_loader.py:199` — HeCBench `.cc` files were silently skipping augmentation (D7).
- [x] **Pipeline audit:** 8 analysis scripts audited, 4 P1 issues found and fixed:
  - `analyze_eval.py`: expected-models list updated for 2-model lineup
  - `token_analysis.py`: pricing data updated for new models
  - `statistical_analysis.py`: Bonferroni correction count updated
  - `selfrepair_analysis.py`: display names updated for new models
- [x] **All 14 SC26 paper metrics verified** as implemented in the analysis pipeline (zero gaps in metric coverage).
- [x] **Single campaign script created:** `scripts/batch/run_eval_campaign.sh` — supports `primary` (L0-L4, retries=3, greedy) and `pass@k` (L0, retries=1, T=0.7, 5 samples) modes. 28 batches per model with automatic pass-2 retry.
- [x] **Old per-model script deleted:** `run_qwen_campaign.sh` (replaced by generic `run_eval_campaign.sh`)
- [x] **Related work research:** 7 critical papers researched with structured comparison notes written to `docs/related_work_research_notes.md`:
  - LASSI (Dearing et al., CLUSTER 2024) — 80-85% with agentic self-correction
  - CodeRosetta (TehraniJamsaz et al., NeurIPS 2024) — specialized C++/CUDA model, BLEU only
  - HPC-Coder-V2 (Chaturvedi et al., arXiv 2024) — fine-tuned HPC LLM
  - OMPify (Kadosh et al., IWOMP 2023) — pragma prediction only
  - TransCoder (Roziere et al., NeurIPS 2020) — foundational unsupervised translation
  - HPCorpus/MonoCoder (Kadosh et al., 2023-2024) — HPC training data
  - TRACY (Gong et al., arXiv 2025) — execution efficiency benchmarking
- [x] **5 additional related papers discovered:** UniPar, OMPar, OMPGPT, TransCoder-ST, BabelTower
- [x] **Experimental decisions log created:** `docs/experimental_decisions_log.md` (7 decisions, 5 insights)
- [x] **Differentiation matrix built:** 8-way feature comparison table in `docs/related_work_research_notes.md` showing ParBench's unique combination of multi-API + build+run+verify + real HPC benchmarks + AST augmentation + general-purpose LLMs

### READY TO LAUNCH

All infrastructure is verified and campaign-ready. Commands:

```bash
# Primary campaign (Samyak — Qwen on Linux GPU machine)
export TOGETHER_API_KEY='...'
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b

# Primary campaign (Erel — Gemini on their machine)
export GEMINI_API_KEY='...'   # or GOOGLE_API_KEY
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash

# pass@k sweep (after primary completes)
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b pass@k
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k

# Post-campaign analysis (after results arrive)
source env_parbench/bin/activate
python3 scripts/evaluation/analyze_eval.py --project-root /home/samyak/Desktop/parbench_sam --write-dashboard
python3 scripts/analysis/statistical_analysis.py --project-root /home/samyak/Desktop/parbench_sam -v
```

### UPDATED PRIORITY LIST

Items re-prioritized based on what was completed this session:

| # | Priority | Item | Status | Depends On | Est. |
|---|----------|------|--------|------------|------|
| 1 | **P0** | Launch Qwen primary campaign | **READY** | API key | ~2-4 hrs runtime |
| 2 | **P0** | Launch Gemini primary campaign (Erel) | **READY** | API key | ~2-4 hrs runtime |
| 3 | **P1** | Post-campaign statistical analysis | Waiting | P0 campaigns | 1 session |
| 4 | **P1** | Paper draft: fix stale 4-model refs + false claims | NOT STARTED | -- | 1 session |
| 5 | **P1** | Paper draft: write Related Work section | ~~NOT STARTED~~ **NOTES READY** | -- | 1 session |
| 6 | **P1** | Paper draft: write Methodology (augmentation, verification) | NOT STARTED | -- | 1 session |
| 7 | **P2** | LaTeX transfer (IEEE/ACM template) | NOT STARTED | P1 items | 2-3 sessions |
| 8 | **P2** | pass@k sweep (both models) | Waiting | P0 campaigns | ~2-4 hrs runtime |
| 9 | **P2** | Token efficiency + error taxonomy analysis scripts | NOT STARTED | P0 campaigns | 1 session |
| 10 | **P3** | Anonymous GitHub repo for double-blind review | NOT STARTED | P2 LaTeX | 1 session |
| 11 | **P3** | Dashboard refresh (GitHub Pages) | Waiting | P0 campaigns | 30 min |
| 12 | **P3** | Consider 3rd model addition | DEFERRED | P0 campaigns | TBD |

**Key changes from previous roadmap:**
- ~~Priority 1 (Run Qwen Campaign)~~ → now split into P0 #1 (Qwen) + P0 #2 (Gemini) — both ready
- ~~Priority 3 (Re-run 3-model eval)~~ → **DROPPED**. Old 3-model pilot data is superseded by new 2-model campaign. Not re-running old models.
- ~~Priority 4 (Related Work)~~ → **UPGRADED to P1 #5** with research notes already written. Only paper prose remains.
- Pipeline audit items → **ALL COMPLETED** (4 P1 fixes applied)
- Augmentation verification → **COMPLETED** (64/64 specs level-invariant across 5 suites)
- Analysis script gaps → **NO GAPS** in the 14 tracked SC26 metrics. Token efficiency and error taxonomy are enhancements (P2 #9), not blockers.

### BLOCKERS / RISKS

- **No blockers.** Campaign can launch immediately on both machines.
- **No augmentation failures.** All 64 non-KNOWN_FAIL specs verified PASS at L0-L4 — clean baseline.
- **No P0 pipeline issues.** All 4 P1 script issues found during audit are fixed.
- **Cosmetic only:** RSBench comma-formatted numbers in `lookups_per_second` output — verification uses `stdout_pattern` + `exit_code` conjunction, not numeric parsing, so this is harmless.
- **Risk: API rate limits.** Overnight campaign runtime depends on Together AI and Google AI rate limits and availability. The campaign script has automatic pass-2 retry for failed batches.
- **Risk: Erel coordination.** Gemini campaign depends on Erel's machine availability and API key. Same script, no code changes needed — just needs `GEMINI_API_KEY` or `GOOGLE_API_KEY` set.
- **Risk: SC26 deadline pressure.** 10 days remaining. Critical path: launch campaigns (day 0-1) → analysis (day 2) → paper writing (days 3-7) → LaTeX + polish (days 8-10). Related work notes being ready saves ~1 session.

### UPDATED SESSION SEQUENCE

| Session | Duration | Depends On | What | Status |
|---------|----------|------------|------|--------|
| S12 (this) | Done | -- | Campaign prep, related work research, pipeline audit | **DONE** |
| S13 | 2-4 hrs | API keys | Launch Qwen + Gemini campaigns, monitor | **READY** |
| S14 | 2 hrs | S13 | Post-campaign: analyze_eval + statistical_analysis | Waiting |
| S15 | 3 hrs | S12 notes | Related work section (prose from research notes) | Ready (can parallel S14) |
| S16 | 3 hrs | S14 | Paper draft fixes (stale data, false claims, methodology) | Waiting |
| S17 | 2-4 hrs | S13 | pass@k sweep (both models) | Waiting |
| S18 | 4-6 hrs | S16 | LaTeX transfer (template + first pass) | Waiting |
| S19 | 2 hrs | S18 | LaTeX polish + figures + tables | Waiting |
| S20 | 2 hrs | S19 | Anonymous repo + final review + submission | Waiting |

**Critical path:** S13 → S14 → S16 → S18 → S19 → S20
**Parallel tracks:** S15 (related work) can run alongside S14; S17 (pass@k) can run alongside S15-S16.

---

## 1. Session Accomplishments (What Was Done — March 28 Session)

### Benchmark Suite Expansion
- **Re-cloned and re-verified Rodinia** (clean submodule reset at `9c10d3ea`):
  54/60 PASS, 6 KNOWN_FAIL confirmed unfixable (texture<>, GL/glew.h, SIGSEGV)
- **Cloned RSBench:** 4 specs created (`rsbench-rsbench-{cuda,omp,opencl,omp_target}.json`),
  3 PASS + 1 omp_target case-study only
- **Cloned mixbench:** 3 specs created (`mixbench-mixbench-{cuda,omp,opencl}.json`), 3 PASS
- **Curated 10 HeCBench kernels:** 25 specs across cuda/omp/omp_target APIs,
  23 PASS + 2 KNOWN_FAIL (stencil1d-omp_target BUILD_FAIL, scan-omp_target VERIFY_FAIL)
  - Curated kernels: stencil1d, heat2d, floydwarshall, scan, iso2dfd, page-rank,
    jacobi, nqueen, md, convolution1d

### Eval Infrastructure
- **Built Qwen campaign script:** `scripts/batch/run_qwen_campaign.sh` — 790 tasks
  across 5 suites x 28 batches x L0-L4; launches in detached tmux session
- **Campaign direction matrix:** `docs/campaign_direction_matrix.md` — 142 translation
  pairs per model at L0 (96 Rodinia + 6 XSBench + 6 RSBench + 6 mixbench + 28 HeCBench)
- **Together AI provider added** to `scripts/evaluation/llm_evaluate.py`:
  `together-qwen-3.5-397b-a17b` model using OpenAI-compatible SDK with
  thinking disabled via `chat_template_kwargs`
- **Statistical analysis pipeline created:** `scripts/analysis/statistical_analysis.py`
  (Wilson CIs, Fisher's exact, Cochran-Armitage, McNemar's, Cohen's h, pass@k)

### Housekeeping
- **Stashed old eval results** to `results/evaluation_backup_20260328/` —
  current `results/evaluation/` is clean (only `.gitkeep`)
- **Fixed iso2dfd-omp phantom CMakeLists.txt** issue

### Current Spec Inventory

| Suite | Total Specs | PASS | KNOWN_FAIL | Eval Pairs (L0) |
|-------|------------|------|------------|----------------|
| Rodinia | 60 | 54 | 6 | 96 |
| XSBench | 4 | 4 | 0 | 6 |
| RSBench | 4 | 4 | 0 | 6 |
| mixbench | 3 | 3 | 0 | 6 |
| HeCBench (curated) | 25 | 23 | 2 | 28 |
| **Total** | **96** | **88** | **8** | **142** |

---

## 2. Current Metrics Tracked

These metrics are currently computed by the analysis pipeline (verified by reading source code):

### In `scripts/evaluation/analyze_eval.py` (lines 180-224, `build_summary()`)
- **Overall pass rate** (PASS / total tasks)
- **Per-model pass rate** with full failure status breakdown (BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL)
- **Per-direction pass rate** (e.g., cuda-to-omp, omp-to-cuda)
- **Per-kernel pass rate** (extracted from spec ID via `_kernel_from_spec()`)
- **Per-augmentation-level pass rate** (L0-L4, extracted from filename convention `*-L{N}.json`)
- **Failure taxonomy** — counts of BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL
- **Self-repair statistics** — first-attempt PASS vs repaired-by-retry counts (lines 144-164)
- **Translation complexity breakdown** — pass rates by `single_file`, `multi_to_single`, etc. (loaded from `results/evaluation/translation_complexity.csv`)
- **Kernel x Model matrix** — per-kernel per-model verdict grid for cuda-to-omp at L0 (markdown output only)
- **Model x Complexity cross-tab** — per-model pass rate by complexity class (markdown output only)

### In `scripts/evaluation/llm_evaluate.py` (captured per-task in result JSON)
- `prompt_tokens`, `completion_tokens` — LLM token usage
- `wall_time_seconds`, `timing_method` — wall-clock execution time (known unreliable)
- `translated_cpu_time_seconds`, `translated_kernel_time_seconds` — always null (not implemented)
- `speedup_ratio` — derived from wall time (unreliable, do not use in paper)
- `attempts[]` — per-attempt build/run/verify details with error snippets
- `total_attempts` — number of LLM API calls made
- `translation_mode` — always `"kernel_centric"` post-SESSION 1.6
- `augment_level`, `sample_id` — augmentation and multi-sample tracking

### In `scripts/analysis/statistical_analysis.py` (lines 970-1080, `main()`)
- **Wilson score 95% CIs** for all pass rates (by model, direction, kernel, level)
- **Omnibus chi-squared** + **pairwise Fisher's exact** for model comparison with Bonferroni correction
- **Cohen's h** effect sizes for pairwise model comparison
- **Cramer's V** for categorical association strength
- **Odds ratios with Woolf CIs** for pairwise model comparisons
- **Chi-squared augmentation independence** per model (cuda-to-omp only)
- **Cochran-Armitage trend** for monotonic augmentation effect
- **McNemar's exact test** for direction asymmetry (L0 only, paired by kernel x model)
- **Augmentation curves with CIs** — per-model L0-L4 pass rates with Wilson intervals
- **Sample size adequacy flags** — cells with n < 10
- **Pass@k estimates** — unbiased estimator (Chen et al. 2021), requires multi-sample data

---

## 3. Metrics Still Needed (per SC26 Paper Audit)

These are gaps identified by the 4-agent audit (`docs/sc26_paper_audit_report.md`, 2026-03-28):

### Statistical Rigor — MOSTLY IMPLEMENTED
The statistical analysis pipeline (`scripts/analysis/statistical_analysis.py`) already
implements Wilson CIs, Fisher's exact, Cohen's h, Cochran-Armitage, and McNemar's. **However,
it has never been run on production data** because the eval results were stashed to
`results/evaluation_backup_20260328/`. The pipeline needs to be run after the Qwen campaign
(or after restoring old results) to generate `results/analysis/statistical_analysis.json`
and `results/analysis/statistical_analysis.md`.

**Still missing from the statistical pipeline:**
- Multiple comparison correction for per-kernel comparisons (>2 models x 20+ kernels)
- Token efficiency analysis: tokens_per_pass vs tokens_per_fail
- Error pattern clustering: which BUILD_FAIL root causes co-occur

### Per-Model Augmentation Curves
- Currently only aggregate L0-L4 pass rates are in the eval summary (flat/level-invariant)
- The statistical pipeline computes per-model curves (`augmentation_curves()` function,
  line 574), but needs production data to produce meaningful output
- **Critical:** Per-model curves may diverge despite flat aggregate — Simpson's Paradox
  finding from audit. This requires the Qwen campaign results at L0-L4 across multiple
  directions to test properly
- **Previous data limitation:** Only cuda-to-omp had L1-L4 results; other directions were L0-only

### Advanced Analysis Not Yet Implemented
- **Per-kernel difficulty tiers** with statistical backing (currently eyeballed from
  the Kernel x Model matrix in `eval_summary.md`)
- **Token efficiency:** Compare mean prompt+completion tokens for PASS vs non-PASS results.
  Data exists in result JSONs (`prompt_tokens`, `completion_tokens`) but no analysis script
  aggregates it
- **Error pattern clustering:** The `build_error_snippet` field in result JSONs contains
  compiler error text. No script currently extracts and clusters these into root cause
  categories (e.g., "missing header", "wrong API call", "type mismatch")
- **Self-repair analysis per model:** `analyze_eval.py` reports global repair count only.
  Per-model breakdown requires iterating `attempts[]` per model directory

---

## 4. Eval Pipeline Updates Needed

### In `scripts/evaluation/analyze_eval.py`

No code changes strictly needed — the script is functionally complete for what it does.
However, consider adding:

1. **Per-model self-repair table** in `build_markdown()` (currently only global counts):
   Iterate `_self_repair_stats()` per model instead of globally. Existing code structure
   at lines 144-164 can be trivially extended.

2. **Token usage summary** in `build_summary()`:
   Add a `"token_usage"` key that aggregates `prompt_tokens` and `completion_tokens`
   across all records, broken down by model and by PASS/FAIL status.

### In `scripts/analysis/statistical_analysis.py`

Script is comprehensive. Specific additions:

1. **Token efficiency analysis** — new function `compute_token_efficiency(records)`:
   Group by model and overall_status, compute mean/median prompt_tokens and
   completion_tokens. Output: `{"by_model": {model: {"pass": {mean_prompt, ...}, "fail": {...}}}}`

2. **Error pattern extraction** — new function `classify_build_errors(records)`:
   Extract `build_error_snippet` from BUILD_FAIL results, regex-match common patterns
   (missing header, undefined reference, type error, etc.), output frequency table.

3. **Per-kernel difficulty scoring** — new function `compute_kernel_difficulty(records)`:
   For each kernel, compute pass rate across all models/directions, Wilson CI,
   and rank into tiers (easy >60%, medium 20-60%, hard <20%).

### In `scripts/evaluation/llm_evaluate.py`

**No changes needed** — the data collection is already comprehensive. The gap is entirely
in the ANALYSIS layer, not the COLLECTION layer. All raw data (tokens, error snippets,
attempts, timing) is already captured in result JSONs.

### New Script: `scripts/analysis/error_taxonomy.py` (to be created)

Purpose: Read all result JSONs, extract error snippets, classify into root cause categories,
and output a structured taxonomy table suitable for the paper's error analysis section.

```python
# Pseudocode:
# 1. Load all non-PASS result JSONs
# 2. For BUILD_FAIL: extract build_error_snippet, regex-match patterns
# 3. For RUN_FAIL: extract run_stderr_snippet, classify (segfault, timeout, wrong output)
# 4. For VERIFY_FAIL: extract expected vs actual output patterns
# 5. Output: {model: {category: {subcategory: count}}}
```

---

## 5. Paper Section Gaps (from 4-Agent Audit)

Source: `docs/sc26_paper_audit_report.md` and memory `project_sc26_audit_findings.md`

### Fatal Flaws (submission-blocking)

| # | Issue | Status | Priority |
|---|-------|--------|----------|
| 1 | Paper draft references "four LLMs" and GPT-4.1 throughout | NOT FIXED | P0 |
| 2 | "Zero VERIFY_FAIL" claim is FALSE (actual: 45 VERIFY_FAIL, 8.9%) | NOT FIXED | P0 |
| 3 | No LaTeX paper — only 692-line Markdown exists (`docs/paper_draft.md`) | NOT STARTED | P0 |
| 4 | No anonymous GitHub repo for double-blind review | NOT STARTED | P0 |
| 5 | Missing LASSI comparison (Domke et al., SC'24, 80-85% pass) | NOT STARTED | P0 |
| 6 | Missing CodeRosetta comparison (Szafraniec et al., NeurIPS'23) | NOT STARTED | P0 |

### Related Work — Critical Gaps

These papers must be cited and differentiated in the related work section:

| Paper | Venue | Why Critical |
|-------|-------|-------------|
| LASSI (Domke et al.) | CLUSTER'24 | Most directly comparable; 80-85% pass with agentic self-correction; must differentiate ParBench's benchmark-centric vs LASSI's agent-centric approach |
| CodeRosetta (Szafraniec et al.) | NeurIPS'23 | Neural C++/CUDA translation; no build/verify step — ParBench's key differentiator |
| HPC-Coder-v2 (Nichols et al.) | arXiv 2024 | Fine-tuned HPC LLM; shows specialized models can outperform general ones |
| OMPify (Chen et al.) | 2024 | OpenMP pragma insertion; narrower scope than ParBench's full API translation |
| TransCoder (Lachaux et al.) | NeurIPS 2020 | Foundational unsupervised translation work |
| HPCorpus (Kadosh et al.) | 2023 | HPC training data; relevant to discussion of why models fail on HPC code |
| TRACY | arXiv 2025 | Execution efficiency benchmarking |

### Methodology Section Gaps

- **Kernel-centric translation rationale:** Why translate kernel files only, not full projects?
  Design doc exists at `docs/design/kernel_centric_translation.md` but paper text not written
- **Augmentation pipeline description:** 6 AST transforms via libclang
  (SwapCondition, PromoteType, etc.), level definitions L1-L4, seed-based reproducibility.
  Code exists in `c_augmentation/` but paper methodology not written
- **Verification conjunction semantics:** stdout_pattern AND exit_code; fixed in S-VERIFY
  session (was previously disjunction). Must document this design choice and its impact

### Results Section Gaps

- **Per-model augmentation curves** — need data from Qwen campaign (or restore backup data)
- **Simpson's Paradox discussion** — aggregate flat curve may mask per-model divergence
- **Backprop anomaly** — Gemini passes where Groq fails (domain-specific model strength);
  evidence of per-kernel difficulty not predicted by aggregate pass rate
- **Direction asymmetry analysis** — McNemar's test exists in statistical pipeline but
  needs production data. Key question: is cuda-to-omp easier than omp-to-cuda? By how much?

### Threats to Validity

Must be written for the paper:
- Wall-clock timing unreliability (sub-ms baselines produce meaningless speedup ratios)
- KNOWN_FAIL spec exclusions (6 Rodinia + 2 HeCBench — could bias results)
- Single-seed augmentation (seed=42 only; generalizability not proven)
- Model version pinning (API models change; `claude-sonnet-4-20250514` today != in 6 months)
- Verification semantics change (S-VERIFY conjunction fix; old results used exit_code only)
- Small sample sizes for non-cuda-to-omp directions (N=15 each in old data)

---

## 6. Prioritized Action Items

Ordered by impact on paper quality, with session estimates.

### Priority 1 — Run Qwen Campaign (immediate)

**Impact:** Adds 4th model to paper, generates 790 fresh result files with corrected
verification semantics (conjunction). Critical for paper credibility.

**Cost:** ~$7 Together AI API cost, ~2-4 hours runtime.

```bash
# Set API key
export TOGETHER_API_KEY='your-key-here'

# Launch in tmux (auto-detaches)
bash scripts/batch/run_qwen_campaign.sh

# Attach to monitor progress
tmux attach -t qwen_campaign

# Results written to: results/evaluation/together-qwen-3.5-397b-a17b/
# Log: results/evaluation/qwen_campaign.log
# Done marker: results/evaluation/qwen_campaign_done.marker
```

**Post-campaign analysis:**
```bash
source env_parbench/bin/activate

# Regenerate eval summary
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard

# Run statistical analysis
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

**Note:** The old 3-model results (504 files) are in `results/evaluation_backup_20260328/`.
Those results used exit_code-only verification (pre-S-VERIFY). They may need to be
re-evaluated with the corrected conjunction verification for valid comparison. The Qwen
campaign uses the corrected pipeline. Decision needed: re-run old models or caveat
the comparison in the paper.

### Priority 2 — Statistical Analysis on Fresh Data (1 session, after Qwen)

**Impact:** Adds confidence intervals, significance tests, and effect sizes to paper —
critical for SC26 reviewer acceptance. Audit identified lack of statistical rigor as
a major weakness.

**Steps:**
1. Run `statistical_analysis.py` on Qwen results
2. Review output in `results/analysis/statistical_analysis.md`
3. Add token efficiency analysis function to `statistical_analysis.py`
4. Add error pattern classification function
5. Incorporate key statistics into paper draft

**Key questions to answer:**
- Is Qwen significantly different from the old 3 models? (Fisher's exact)
- Does augmentation level affect pass rate? (Cochran-Armitage trend)
- Is there directional asymmetry? (McNemar's)
- What is the per-kernel difficulty ranking? (Wilson CIs)

### Priority 3 — Re-run 3-Model Eval with Corrected Verification (1-2 sessions)

**Impact:** The 504 existing results in `results/evaluation_backup_20260328/` used
pre-S-VERIFY verification (exit_code disjunction, not conjunction). 169 PASS results
cannot be retroactively re-verified. Must either:
- (a) Re-run all 3 models (claude, gemini, groq) — ~468 tasks, significant API cost
- (b) Accept old results with a caveat in the paper that they used weaker verification
- (c) Run a random subset to estimate false-positive rate

**Recommendation:** Option (c) — run ~50 previously-PASS tasks through corrected pipeline
to estimate false-positive rate. If low (<5%), accept old results with caveat. If high,
re-run all.

### Priority 4 — Related Work Section (1 session)

**Impact:** The audit explicitly flagged missing LASSI and CodeRosetta citations as
the highest-risk omission. SC26 reviewers familiar with these works will immediately
notice their absence.

**Steps:**
1. Web search for all 7 papers listed in Section 5 above
2. Read abstracts and methodology sections
3. Write 2-3 pages of related work with explicit differentiation table:
   - ParBench vs LASSI: benchmark-centric vs agent-centric, build+run+verify vs compile-only
   - ParBench vs CodeRosetta: general LLMs vs fine-tuned neural model, multiple APIs vs C++/CUDA only
   - ParBench vs HPC-Coder-v2: evaluation benchmark vs specialized model
4. Place in `docs/paper/sections/related_work.tex` (or Markdown if LaTeX not ready)

### Priority 5 — Paper Draft Updates (1-2 sessions)

**Impact:** Current draft at `docs/paper_draft.md` has stale 4-model data, false claims
(zero VERIFY_FAIL), and incomplete methodology.

**Steps:**
1. Fix 4-model to 3-model (or 4-model if Qwen campaign complete) throughout
2. Fix "zero VERIFY_FAIL" claim (actual: 45 VERIFY_FAIL = 8.9% of 504 tasks)
3. Add statistical analysis section with CIs and significance tests
4. Write threats-to-validity section
5. Update all data tables with fresh numbers from `eval_summary.json`
6. Add augmentation methodology description

### Priority 6 — LaTeX Transfer (2-3 sessions, schedule bottleneck)

**Impact:** SC26 requires IEEE or ACM format paper. No LaTeX exists. This is the
longest-lead-time item on the critical path.

**Steps:**
1. Determine SC26 template: IEEE or ACM sigconf (check call for papers)
2. Set up LaTeX project structure
3. Transfer Markdown content section by section
4. Generate LaTeX tables from `eval_summary.json` and `statistical_analysis.json`
5. Create figures (augmentation curves, failure taxonomy bar chart, per-kernel heatmap)

### Priority 7 — Anonymous GitHub Repo (1 session)

**Impact:** SC26 double-blind requirement. Must create anonymized repo before submission.

**Steps:**
1. Create a new GitHub organization (e.g., `anonymous-submission-2026`)
2. Fork/copy ParBench with all identifying information removed
3. Strip author names from code comments, CLAUDE.md, docs
4. Ensure reproducibility: include Dockerfile, requirements.txt, run instructions
5. Note: `docs/REPRODUCING.md` already exists — check if it's complete

### Priority 8 — Dashboard Updates (after eval, 30 min)

```bash
# After any eval completion, run the dashboard refresher
python3 scripts/generate_viz_data.py
# Then commit and push to update GitHub Pages
```

---

## 7. Quick Reference — Commands

### Environment Setup
```bash
# Activate Python environment
source env_parbench/bin/activate

# Verify CUDA toolchain
/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc --version
```

### Qwen Campaign
```bash
# Set API key
export TOGETHER_API_KEY='...'

# Launch campaign in tmux
bash scripts/batch/run_qwen_campaign.sh

# Attach to monitor
tmux attach -t qwen_campaign

# Check progress (from another terminal)
ls results/evaluation/together-qwen-3.5-397b-a17b/*.json 2>/dev/null | wc -l
```

### Analysis Pipeline
```bash
# Regenerate eval summary (after any eval completes)
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard

# Run statistical analysis
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# Output files:
#   results/evaluation/eval_summary.json
#   results/evaluation/eval_summary.md
#   results/analysis/statistical_analysis.json
#   results/analysis/statistical_analysis.md
#   visualizations/eval_results_data.js
```

### Validation & Testing
```bash
# Validate all specs (~135 HeCBench errors expected — ignore)
python3 scripts/validate_schema.py --all

# Validate one spec
python3 scripts/validate_schema.py --spec specs/rodinia-bfs-cuda.json

# Run augmentation unit tests
python3 -m pytest c_augmentation/test_transforms.py -v

# Verify a single spec through harness
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
```

### Spec Verification (build/run/verify a specific spec)
```bash
python3 -m harness -v verify specs/rsbench-rsbench-cuda.json
python3 -m harness -v verify specs/mixbench-mixbench-cuda.json
python3 -m harness -v verify specs/hecbench-heat2d-cuda.json
```

### Translation Complexity CSV (regenerate after adding new suites)
```bash
python3 scripts/analysis/classify_translation_pairs.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

---

## 8. Key File Paths

| File | Purpose |
|------|---------|
| `scripts/batch/run_qwen_campaign.sh` | Qwen 3.5 397B campaign launcher (tmux) |
| `scripts/evaluation/llm_evaluate.py` | Single-task LLM translation evaluator |
| `scripts/evaluation/run_eval_batch.py` | Batch evaluation runner |
| `scripts/evaluation/analyze_eval.py` | Aggregate results → eval_summary.json/md |
| `scripts/analysis/statistical_analysis.py` | Statistical significance tests |
| `scripts/analysis/classify_translation_pairs.py` | Translation complexity classifier |
| `docs/campaign_direction_matrix.md` | 142 translation pairs, 28 batches |
| `docs/facts_sheet_s_verify.md` | Ground-truth baseline numbers |
| `docs/sc26_paper_audit_report.md` | 4-agent audit with 17 weaknesses |
| `docs/paper_draft.md` | Current (stale) paper draft |
| `results/evaluation_backup_20260328/` | Old 3-model results (pre-S-VERIFY verification) |
| `results/evaluation/` | Current eval results (empty, awaiting Qwen campaign) |
| `.claude/rules/known-issues.md` | KNOWN_FAIL specs and gotchas |
| `.claude/rules/evaluation.md` | Eval pipeline rules and patterns |

---

## 9. Decision Points for Next Session

These require human judgment before proceeding:

1. **Re-run old models?** The 504 backup results used weaker verification. Options:
   (a) Re-run all ~$50-100 API cost, (b) Accept with caveat, (c) Spot-check subset.

2. **SC26 template:** Is it IEEE or ACM sigconf? Determines LaTeX setup effort.

3. **4th model identity:** Qwen 3.5 397B-A17B is ready. Alternatively, consider
   claude-opus-4-6 or gpt-4o for a stronger baseline. Qwen is cost-effective (~$7
   for full campaign) and adds model diversity (open-source MoE).

4. **Paper scope:** With 11 days remaining, is the target a full 10-page paper or
   a shorter workshop/poster submission? Scope determines which priorities to cut.

5. **Augmentation levels for new suites:** The Qwen campaign runs L0-L4 for all suites.
   RSBench, mixbench, and HeCBench augmentation transforms may not be tested yet.
   Verify that `c_augmentation/` can handle these suites' source files before running
   L1-L4 on them.

---

## 10. Session Sequence (Recommended)

| Session | Duration | Depends On | What |
|---------|----------|------------|------|
| S-NEXT-1 | 2-4 hrs | API key | Launch Qwen campaign, monitor |
| S-NEXT-2 | 2 hrs | S-NEXT-1 | Post-campaign analysis: run analyze_eval + statistical_analysis |
| S-NEXT-3 | 3 hrs | S-NEXT-2 | Related work research + writing (LASSI, CodeRosetta focus) |
| S-NEXT-4 | 3 hrs | S-NEXT-2 | Paper draft updates (fix stale data, add stats, threats). **Key inputs:** `docs/experimental_decisions_log.md` (D1-D7 decisions with reviewer defenses), `docs/related_work_research_notes.md` (7 papers + differentiation matrix), eval results from S-NEXT-2 |
| S-NEXT-5 | 4-6 hrs | S-NEXT-4 | LaTeX transfer (template setup + first pass) |
| S-NEXT-6 | 2 hrs | S-NEXT-5 | LaTeX polish + figures + tables |
| S-NEXT-7 | 2 hrs | S-NEXT-6 | Anonymous repo creation |
| S-NEXT-8 | 2 hrs | S-NEXT-7 | Final review + submission |

**Critical path:** S-NEXT-1 → S-NEXT-2 → S-NEXT-4 → S-NEXT-5 → S-NEXT-6 → S-NEXT-8

S-NEXT-3 (related work) can run in parallel with S-NEXT-2 or S-NEXT-4.
S-NEXT-7 (anon repo) can run in parallel with S-NEXT-6.
