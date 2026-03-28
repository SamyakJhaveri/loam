# SC26 Evaluation Campaign — Final Action Plan

**Synthesized:** 2026-03-28
**Author:** Team Lead (eval-campaign agent team)
**Sources:** Explorer, Planner, Implementor, Statistician, Critic reports
**Deadline:** April 8, 2026 (SC26 submission)

---

## Executive Summary

The agent team identified **1,152 missing evaluation tasks** across 5 Rodinia directions.
After adversarial review, the **recommended scope is 407 new tasks** (MVE + omp-to-cuda L1-L4),
achievable in ~15-18h wall-clock at ~$8 API cost. Two blockers must be resolved first:
OpenCL build environment validation and OpenCL augmentation hollowness check.

### Key Statistical Findings (from existing data)
- **Gemini ≈ Groq** (Fisher's p=0.83, OR=0.83) — statistically indistinguishable
- **Level invariance confirmed** (chi2 p=0.83) — augmentation does not affect pass rate
- **Claude dominance is large effect** (Cohen's h > 1.0 vs both competitors)
- **2-tier narrative**: Frontier (Claude ~52%) vs Non-frontier (Gemini/Groq ~7-8%)

---

## Decision Matrix: What to Do and What to Cut

| # | Action | Audit W# | ROI | Decision | Effort |
|---|--------|----------|-----|----------|--------|
| 1 | Fix 3-model narrative + stale numbers | W7, W2 | 20.0 | **MUST DO** | 0.25 days |
| 2 | OpenCL L0 baselines (192 tasks) | W1, W16 | 10.0 | **MUST DO** | 0.5 days |
| 3 | Statistical analysis (CIs, tests, effects) | W4 | 10.0 | **MUST DO** | 0.5 days |
| 4 | Self-repair transition table | W4 | 8.0 | **SHOULD DO** | 0.25 days |
| 5 | omp-to-cuda L1-L4 (192 tasks) | W1 | 3.0 | **SHOULD DO** | 1.0 days |
| 6 | OpenCL L1-L4 (768 tasks) | W1, W16 | 2.0 | NICE TO HAVE | 1.5 days |
| 7 | Profiling paragraph | W9 | 2.0 | NICE TO HAVE | 0.5 days |
| 8 | Pass@k sampling | W4 | 1.3 | **CUT** | 1.5 days |
| 9 | Third benchmark (Parboil) | W1 | 1.0 | **CUT** | 2.0 days |

---

## Blockers (Resolve Before Any Eval Runs)

### BLOCKER 1: OpenCL Build Environment Validation
**Risk:** If OpenCL specs fail to build/run/verify, the entire campaign stalls.
**Action:** Budget 2 hours (not 15 min) for Phase 0. Steps:
1. `clinfo` — verify OpenCL runtime is installed
2. `harness verify` on 3 diverse OpenCL specs (bfs, hotspot, backprop)
3. Single end-to-end LLM translation (1 kernel × 1 model × cuda-to-opencl)
4. All 3 models connectivity check

**Fallback:** If OpenCL env is broken, paper survives on cuda-to-omp + omp-to-cuda only
(318 tasks). Weaker but not fatal if framed as "CUDA-OMP translation study."

### BLOCKER 2: OpenCL Augmentation Hollowness
**Risk:** `.cl` kernel files may receive zero augmentation transforms at L1-L2,
making opencl-as-source L1-L4 results effectively L0 duplicates.
**Action:** Before Phase 2, test augmentation on 3 OpenCL specs:
```bash
python3 scripts/augmentation/augment_verify.py specs/rodinia-bfs-opencl.json \
  --augment_level 2 --seed 42 -v \
  --project-root /home/samyak/Desktop/parbench_sam
```
Check if `Kernels.cl` (or equivalent `.cl` file) has non-empty `transforms_applied`.

**If hollow:** Drop L1-L4 for opencl-to-cuda and opencl-to-omp directions.
Keep L1-L4 for cuda-to-opencl and omp-to-opencl (source is CUDA/OMP, not OpenCL).
Paper notes: "Augmentation transforms apply primarily to host code; kernel files
(.cl) receive fewer modifications at low augmentation levels."

### HIGH RISK: max_retries Inconsistency
**Issue:** 24/504 files have max_retries=1 vs 480 with max_retries=2.
**Action:** Identify which 24 files are affected. Either:
- (a) Re-run the 24 with max_retries=2 (preferred, ~30 min), OR
- (b) Exclude from self-repair analysis and disclose in methodology

### DATA FIX: 1 File Needs Re-verification
**File:** `claude-sonnet-4-6/xsbench-xsbench-opencl-to-xsbench-xsbench-cuda-L4.json`
**Issue:** Uses `exit_code` only verification (pre-S-VERIFY). All other 90 PASS files
use correct `stdout_pattern+exit_code` conjunction.
**Action:** Re-run harness verify on the translated code. If PASS → keep. If FAIL → paper
number drops by 1 (from 91 to 90 standard PASS).

---

## Execution Calendar

### Day 11 (Mar 28 — Today): Preparation
- [x] Agent team completed gap analysis and campaign design
- [ ] Resolve BLOCKER 1: OpenCL env validation (Phase 0, budget 2h)
- [ ] Resolve DATA FIX: re-verify 1 file
- [ ] Start Phase 1 if Phase 0 passes

### Day 12 (Mar 29): Phase 1 — OpenCL L0 Baselines
- [ ] Run Phase 1: 192 tasks across 4 OpenCL directions (~5-8h)
- [ ] Batch script: `scripts/batch/run_phase1_opencl_l0.sh` (copy-pasteable, in Planner report)
- [ ] Completeness check after Phase 1

### Day 13 (Mar 30): Phase 2 — omp-to-cuda L1-L4
- [ ] Resolve BLOCKER 2: test OpenCL augmentation hollowness
- [ ] Run omp-to-cuda L1-L4: 192 tasks (~5h)
- [ ] If augmentation is non-hollow: optionally run cuda-to-opencl L1-L4 (204 tasks)
- [ ] Re-run 24 max_retries=1 files with max_retries=2

### Day 14 (Mar 31): Phase 3 — Analysis
- [ ] Run EXTRACTION_FAIL retries (~23 tasks)
- [ ] Implement statistical_analysis.py (design in Implementor report)
- [ ] Run full analysis pipeline:
  - `analyze_eval.py` — updated summary
  - `statistical_analysis.py` — CIs, chi-squared, effect sizes
  - `selfrepair_analysis.py` — updated repair stats with new data
- [ ] Eval data FROZEN at end of Day 14

### Days 15-17 (Apr 1-3): Paper Integration
- [ ] Fix 3-model narrative (remove all GPT-4.1 references)
- [ ] Add Wilson CIs to all reported pass rates
- [ ] Add statistical significance statements to model comparison
- [ ] Write direction asymmetry analysis with new OpenCL data
- [ ] Self-repair transition table from existing data
- [ ] Augmentation invariance section with Cochran-Armitage trend test
- [ ] Profiling limitations paragraph citing TRACY

### Days 18-21 (Apr 4-7): LaTeX + Final Writing
- [ ] Transfer to SC26 LaTeX template
- [ ] Final number cross-check against eval_summary.json
- [ ] Related work gaps (LASSI, CodeRosetta — see audit)

### Day 22 (Apr 8): Submit

---

## Batch Commands (Copy-Pasteable)

### Phase 0: Canary Test
```bash
source env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 0a: Verify OpenCL specs
python3 -m harness -v verify specs/rodinia-bfs-opencl.json
python3 -m harness -v verify specs/rodinia-hotspot-opencl.json
python3 -m harness -v verify specs/rodinia-backprop-opencl.json

# Step 0b: Single LLM translation
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-opencl \
  --models claude-sonnet-4-6 \
  --kernels bfs \
  --augment-levels 0 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v

# Step 0c: All 3 models connectivity
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-opencl \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels bfs \
  --augment-levels 0 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
```

### Phase 1: OpenCL L0 (192 tasks)
Full batch script in: `docs/eval_campaign/planner_calendar.md` (lines 131-266)

### Phase 2: omp-to-cuda L1-L4 (192 tasks)
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction omp-to-cuda \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 1 2 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v

python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction omp-to-cuda \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 3 4 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
```

---

## Cost Estimate (Critic-Reviewed)

| Phase | Tasks | Claude | Gemini | Groq | Total |
|-------|------:|-------:|-------:|-----:|------:|
| Phase 0: Canary | 6 | $0.27 | $0.01 | $0.03 | $0.31 |
| Phase 1: OpenCL L0 | 192 | $2.30 | $0.05 | $0.26 | $2.61 |
| Phase 2: omp-to-cuda L1-L4 | 192 | $2.88 | $0.06 | $0.32 | $3.26 |
| Phase 3: Retries | 23 | $0.35 | $0.01 | $0.04 | $0.40 |
| **Total (MVE+)** | **413** | **$5.80** | **$0.13** | **$0.65** | **~$6.58** |

*Note: Self-repair retries (max_retries=3) may increase token consumption by ~2x
on failed tasks. Worst case: ~$12. Critic notes that $19.50 is the full-campaign
estimate; the reduced MVE+ scope saves ~$13.*

---

## Paper Framing Changes (from Critic)

| Topic | Current Claim | Revised Claim |
|-------|--------------|---------------|
| Models | "4 models including GPT-4.1" | "3 models: Claude Sonnet (frontier), Gemini Flash Lite + Groq Llama 3.3 70B (cost-efficient)" |
| Directions | "6 translation directions" | "6 directions; cuda-to-omp primary (N=255), OpenCL directions at L0 baseline" |
| Augmentation | "Level invariant across all directions" | "Level invariance on cuda-to-omp (N=255, chi2 p=0.83); OpenCL at L0 only" |
| Model tiers | "4 distinct models" | "2 capability tiers: frontier (~52%) vs non-frontier (~7-8%, statistically equivalent)" |
| Self-repair | "27 additional PASSes" | Qualify with max_retries disclosure |
| Pass@k | (not mentioned) | "We report greedy pass@1 with self-repair; pass@k is orthogonal future work" |
| Third bench | (not mentioned) | "ParBench supports arbitrary suites; Parboil integration is future work" |

---

## Code Changes Required (from Implementor)

### Must-Implement (before eval campaign)
None — the existing pipeline handles all 6 directions. No code changes needed for Phase 1-3.

### Should-Implement (during/after eval campaign)
1. **`scripts/analysis/statistical_analysis.py`** (~350 lines) — Wilson CIs, chi-squared,
   effect sizes, augmentation curves. Design in `docs/eval_campaign/implementor_specs.md`.
2. **`analyze_eval.py` CLI updates** — add new OpenCL directions to expected-directions default.

### Deferred (not needed for SC26)
3. Temperature/pass@k support in `llm_evaluate.py` (9 code changes, all backward-compatible)
4. Parboil onboarding pipeline
5. OpenCL batch scripts (Phase 1 batch script in planner_calendar.md is sufficient)

---

## Detailed Reports (for reference)

| Report | Location | Lines |
|--------|----------|-------|
| Gap Matrix | `docs/eval_campaign/explorer_report.md` | 320 |
| Execution Calendar | `docs/eval_campaign/planner_calendar.md` | ~450 |
| Code Change Specs | `docs/eval_campaign/implementor_specs.md` | ~400 |
| Statistical Methodology | `docs/eval_campaign/statistician_methodology.md` | 1169 |
| Adversarial Review | `docs/eval_campaign/critic_review.md` | 420 |

---

## Verification Checklist (post-campaign)

- [ ] `python3 scripts/evaluation/analyze_eval.py --show-gaps` confirms zero gaps for MVE scope
- [ ] `python3 scripts/analysis/statistical_analysis.py` produces valid JSON + markdown
- [ ] `python3 scripts/analysis/selfrepair_analysis.py` updated with new data
- [ ] `/validate` passes (no spec or infrastructure regressions)
- [ ] Every number in paper cross-checked against `eval_summary.json`
- [ ] `dashboard-refresher` agent updates GitHub Pages with new direction data
