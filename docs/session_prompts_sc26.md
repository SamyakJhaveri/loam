# ParBench SC26 Sprint -- Session Prompts

> **How to use:** Copy-paste one prompt per Claude Code session. Run `/clear` between sessions.
> Each prompt is self-contained with full context, exact commands, and verification steps.
> Updated: 2026-03-28 (Day 11 of 21). **11 days remain.** Deadline: April 8, 2026.
> **Models (3 active):** Claude Sonnet 4.6 | Gemini 2.5 Flash-Lite | Llama 3.3 70B (azure-gpt-4.1 DISABLED)

---

## Critical Assessment (2026-03-28)

Five gaps threaten submission. Ordered by severity:

| Gap | Severity | Description | Blocks |
|-----|----------|-------------|--------|
| ~~Verification is exit-code only~~ | ~~CRITICAL~~ | **RESOLVED (S-VERIFY, 2026-03-27).** All 58 non-KNOWN_FAIL specs verified TRUE PASS with stdout_pattern+exit_code conjunction. Eval results: 105/468 PASS (22.44%). | ~~Paper credibility~~ |
| No LaTeX paper | **CRITICAL** | Markdown only; SC26 requires ACM/IEEE LaTeX | Submission |
| No `requirements.txt` | **CRITICAL** | Reviewers cannot reproduce | Artifact evaluation |
| No anonymous repo | **CRITICAL** | Double-blind review requires it | Submission |
| Zero timing data | HIGH | No kernel-time performance numbers at HPC venue | Paper strength |
| 17/184 kernels evaluated | HIGH | Only Rodinia evaluated; 120 HeCBench + 4 XSBench specs exist | Paper scope claim |

---

## Completed Sessions Summary

| Session | Date | What | Key Result |
|---------|------|------|------------|
| S1 | Mar 18 | Rodinia submodule reset | 54/60 PASS, 6 KNOWN_FAIL; pristine source restored |
| S1.5 | Mar 19 | Kernel-centric pipeline | `translation_targets` added to 60 Rodinia specs |
| S1.6 | Mar 19 | Universal standardization | All 184 specs have `translation_targets`; `full_project` fallback removed |
| S2 | Mar 20 | azure-gpt-4.1 L0 eval | 9/17 PASS (52.9%) cuda-to-omp; 17 result files |
| S3 | Mar 21 | groq-llama L0 eval | 5/17 PASS (29.4%) cuda-to-omp |
| S3b | Mar 22 | claude + gemini L0 eval | Claude 12/17 (70.6%), Gemini 4/17 (23.5%); 4-model L0 matrix complete |
| S3-PM | Mar 22 | Post-mortem audit | Fixed eval_summary.json; documented timing confound |
| S4 | Mar 23 | XSBench spec creation | 4 new specs (cuda, omp, opencl, omp_target) |
| S5 | Mar 23 | XSBench verify | 4/4 PASS; checksum asymmetry documented |
| S6 | Mar 23 | Paper outline | `docs/paper/paper_outline.md` with 8 sections |
| S7 | Mar 25 | Augmented eval L1-L4 | 116 files/model (Rodinia L1-L4 + XSBench L1-L4); 3 models |
| S8 | Mar 25 | XSBench multi-API eval | 60 files/model; all 12 XSBench directions; 3 models |
| S9 | Mar 25-26 | omp-to-cuda eval | 48 Rodinia files (16 kernels x 3 models); cross-direction analysis |
| W-S11 | Mar 25 | Dashboard refresh | 12 viz files updated; all numbers verified against data |
| W-S12-PARTIAL | Mar 25 | Paper Sections 3-5 | 3289 words; Methodology + System Design + Experimental Setup |
| W-S14 | Mar 24 | Publication figures | 6 figures (F2-F6) + 1 LaTeX table (T2) from L0 data |
| S-VERIFY | Mar 27 | Verification fix + re-verify | All 58 non-KNOWN_FAIL specs TRUE PASS; stdout_pattern+exit_code conjunction; 9 FALSE_PASS specs fixed |
| S-FIGURES | Mar 27 | Updated paper figures | System architecture figure added; all paper figures updated |
| S13 | Mar 27 | Paper draft expansion | Results and Discussion sections expanded |

**Totals:** 504 raw result JSON files across 3 models (468 in eval_summary, 36 excluded kmeans/mummergpu). 17 Rodinia kernels + 1 XSBench kernel evaluated. 12 translation directions. L0-L4 augmentation complete for cuda-to-omp. Verified pass rate: 105/468 = 22.44%.

---

## Priority Legend

| Priority | Label | Definition |
|----------|-------|------------|
| **P0** | CRITICAL | Blocks submission. Paper cannot be submitted without this. |
| **P1** | HIGH | Significantly strengthens the paper. Omission would be noticed by reviewers. |
| **P2** | MEDIUM | Noticeable improvement. Strengthens but not fatal if missing. |

---

## Remaining Sessions Overview (15 sessions)

| # | Session | Priority | Group | Parallel? | Lane | Effort | Dependencies | Status |
|---|---------|----------|-------|-----------|------|--------|-------------|--------|
| 1 | S-VERIFY | P0 | G1 | Yes (with S-DEPS, W-S16, S-TAXONOMY, S-ANALYSIS) | GPU | 1-2 days | None | **COMPLETED (2026-03-27)** |
| 2 | S-DEPS | P0 | G1 | Yes | Any | 30 min | None | NOT STARTED |
| 3 | W-S16 | P0 | G1 | Yes | Worktree | 4 hours | None | NOT STARTED |
| 4 | W-S17 | P0 | G4 | Yes (with W-S15) | Worktree | 2-3 days | S13 complete, paper draft finalized | NOT STARTED |
| 5 | S18 | P0 | G5 | No (final gate) | Supervised | 2-3 days | Everything else | NOT STARTED |
| 6 | S10 | P1 | G2 | Yes (with S12, S-BIB, S-FIGURES) | GPU | 1 day compute | S-VERIFY complete | NOT STARTED |
| 7 | S-TAXONOMY | P1 | G1 | Yes | Any | 3 hours | None | NOT STARTED |
| 8 | S12 | P1 | G2 | Yes | Supervised | 1 day | None (Paraval reading is a soft dep) | NOT STARTED |
| 9 | S13 | P1 | G3 | Yes (with S10b, S-TIMING) | Supervised | 1 day | S10 complete, S-VERIFY complete | **COMPLETED (2026-03-27)** |
| 10 | W-S15 | P1 | G4 | Yes (with W-S17) | Worktree | 4 hours | S13 complete | NOT STARTED |
| 11 | S10b | P2 | G3 | Yes (with S13, S-TIMING) | GPU | 1 day compute | S10 complete | NOT STARTED |
| 12 | S-ANALYSIS | P2 | G1 | Yes | Any | 3 hours | None | NOT STARTED |
| 13 | S-FIGURES | P2 | G2 | Yes | Any | 4 hours | S-VERIFY data available | **COMPLETED (2026-03-27)** |
| 14 | S-BIB | P2 | G2 | Yes | Any | 2 hours | None | NOT STARTED |
| 15 | S-TIMING | P2 | G3 | Yes | GPU | 4 hours | GPU idle (no eval running) | NOT STARTED |

---

## Parallel Execution Groups

Sessions within a group run concurrently. Groups execute sequentially (each group starts after the previous group's critical-path items complete).

### Dependency Diagram

```
DAY 9-10                    DAY 11-13                 DAY 13-15              DAY 15-17         DAY 19-21
GROUP 1                     GROUP 2                   GROUP 3                GROUP 4            GROUP 5
========================    =====================     ===================    ===============    =========

[GPU]  S-VERIFY ----------> [GPU]  S10 -------------> [GPU]  S10b
       (fix verifier,              (cuda-to-opencl,          (3 remaining
        re-verify)                  17 kernels)              OpenCL dirs)
                                                      [GPU]  S-TIMING
                            [Any]  S-FIGURES ------.
[Any]  S-DEPS                      (regen w/ data)  \
       (30 min)                                      \
                            [Sup]  S12                '-> [Sup]  S13 ------> [WT]  W-S15 ----.
[WT]   W-S16                       (Intro +                   (Results +          (review)   |
       (anon repo)                  Related Work)              Discussion)                    |
                            [Any]  S-BIB                                    [WT]  W-S17 ---. |
[Any]  S-TAXONOMY                  (bibliography)                                 (LaTeX)  | |
       (error taxonomy)                                                                    v v
[Any]  S-ANALYSIS                                                                     [Sup]  S18
       (SLoC, tokens,                                                                   (final
        self-repair)                                                                     review
                                                                                         + submit)

Legend:  [GPU] = main checkout, GPU required    [WT] = worktree (no GPU)
         [Sup] = supervised (Samyak judgment)   [Any] = no special requirements
         -----> = dependency (must complete before next starts)
```

### Group 1 -- Start Immediately (Day 9-10, Mar 26-27)

All five sessions can launch in parallel. No dependencies between them.

| Session | Lane | Estimated Time | What It Does |
|---------|------|---------------|--------------|
| S-VERIFY | GPU (main checkout) | 1-2 days | Fix verification to check stdout, not just exit code. Re-verify all existing PASS results. |
| S-DEPS | Any | 30 min | Create `requirements.txt`, `pyproject.toml`, `Dockerfile`. Freeze current venv. |
| W-S16 | Worktree | 4 hours | Create anonymous GitHub repo for double-blind. Sanitize author names, paths. |
| S-TAXONOMY | Any | 3 hours | Build error taxonomy table from 500 existing result JSONs. Classify BUILD/RUN/VERIFY/EXTRACTION failures. |
| S-ANALYSIS | Any | 3 hours | Extract SLoC counts, token usage, self-repair statistics from result JSONs. |

### Group 2 -- After S-VERIFY Completes (Day 11-13, Mar 28-30)

S10 requires verified results. S-FIGURES needs verification data. S12 and S-BIB have no hard deps but are sequenced here to feed S13.

| Session | Lane | Estimated Time | What It Does |
|---------|------|---------------|--------------|
| S10 | GPU (main checkout) | 1 day compute | cuda-to-opencl eval: 17 Rodinia kernels x 3 models (51 tasks). |
| S12 | Supervised | 1 day | Write paper Sections 1-2 (Introduction + Related Work). |
| S-FIGURES | Any | 4 hours | Regenerate all figures (F2-F6) with verification-corrected data. |
| S-BIB | Any | 2 hours | Compile bibliography: SC venues, SWE-bench, HumanEval, TransCoder, OMPify. |

### Group 3 -- After S10 Completes (Day 13-15, Mar 30 - Apr 1)

S13 needs S10 results for complete data tables. S10b extends OpenCL coverage. S-TIMING fills the performance data gap.

| Session | Lane | Estimated Time | What It Does |
|---------|------|---------------|--------------|
| S10b | GPU (main checkout) | 1 day compute | 3 remaining OpenCL directions (opencl-to-cuda, opencl-to-omp, omp-to-opencl). |
| S13 | Supervised | 1 day | Write paper Sections 6-8 (Results + Discussion + Conclusion) with complete data. |
| S-TIMING | GPU (needs idle) | 4 hours | Run `omp_get_wtime()` / `nvprof` timing for all PASS results. Requires no concurrent GPU eval. |

### Group 4 -- After S13 Completes (Day 15-17, Apr 1-3)

Paper review requires a complete draft. LaTeX transfer requires finalized content.

| Session | Lane | Estimated Time | What It Does |
|---------|------|---------------|--------------|
| W-S15 | Worktree | 4 hours | Full paper review: data accuracy, argument coherence, missing claims. |
| W-S17 | Worktree | 2-3 days | Transfer Markdown paper to ACM/IEEE LaTeX template. Format tables, figures, bibliography. |

### Group 5 -- Final Gate (Day 19-21, Apr 6-8)

Everything converges. No parallelism possible.

| Session | Lane | Estimated Time | What It Does |
|---------|------|---------------|--------------|
| S18 | Supervised | 2-3 days | Co-author review cycle. Final number verification. Submit. |

---

## Day-by-Day Schedule (Days 9-21)

Three execution lanes run concurrently. Only one GPU eval at a time.

| Day | Date | GPU Lane | Worktree Lane | Supervised Lane |
|-----|------|----------|---------------|-----------------|
| 9 | Mar 26 | **S-VERIFY** starts (fix verifier logic) | **W-S16** starts (anon repo) | **S-DEPS** (30 min); **S-TAXONOMY** (3h); **S-ANALYSIS** (3h) |
| 10 | Mar 27 | **S-VERIFY COMPLETED** (re-verified all results; 105/468 PASS) | W-S16 completes; merge branch | Review S-TAXONOMY + S-ANALYSIS outputs |
| 11 | Mar 28 | **S10** starts (cuda-to-opencl, 51 tasks) | **S-FIGURES** starts (regen with verified data) | **S12** starts (Intro + Related Work) |
| 12 | Mar 29 | S10 continues | S-FIGURES completes; **S-BIB** starts | S12 continues |
| 13 | Mar 30 | S10 completes; **S10b** starts (3 OpenCL dirs) | S-BIB completes | **S13** starts (Results + Discussion) |
| 14 | Mar 31 | S10b continues | -- | S13 continues |
| 15 | Apr 1 | S10b completes; **S-TIMING** starts | **W-S15** starts (paper review) | Review S10b results; incorporate into S13 |
| 16 | Apr 2 | S-TIMING completes | W-S15 completes; **W-S17** starts (LaTeX) | Merge all completed worktree branches |
| 17 | Apr 3 | -- | W-S17 continues | Deep paper review; address W-S15 findings |
| 18 | Apr 4 | -- | W-S17 continues | Co-author review begins |
| 19 | Apr 5 | -- | W-S17 completes; merge | **S18** starts (final review) |
| 20 | Apr 6 | -- | -- | S18 continues (address co-author feedback) |
| 21 | Apr 8 | -- | -- | **SUBMIT** |

**Buffer:** Days 16-18 absorb delays. If S-VERIFY takes 3 days instead of 2, S10 shifts to Day 12 and S10b may be cut (P2).

---

## GPU Sequencing Rules

`llm_evaluate.py` backs up and restores files inside `rodinia/rodinia-src/` with no file locking. Two concurrent Rodinia evals will corrupt each other's backup/restore cycle.

### Must Be Sequential (one at a time on GPU)

| Session | Writes To | Conflict With |
|---------|-----------|--------------|
| S-VERIFY | `rodinia/rodinia-src/` (re-runs harness) | S10, S10b, S-TIMING |
| S10 | `rodinia/rodinia-src/opencl/` | S-VERIFY, S10b, S-TIMING |
| S10b | `rodinia/rodinia-src/opencl/`, `cuda/`, `openmp/` | S-VERIFY, S10, S-TIMING |
| S-TIMING | `rodinia/rodinia-src/` (profiler runs) | S-VERIFY, S10, S10b |

### Recommended GPU Order

```
S-VERIFY (Day 9-10) --> S10 (Day 11-13) --> S10b (Day 13-15) --> S-TIMING (Day 15-16)
```

### Safe to Run Simultaneously

- Any **worktree** session + any GPU eval (completely disjoint directories)
- **S-DEPS**, **S-TAXONOMY**, **S-ANALYSIS**, **S-BIB** + any GPU eval (read-only on results/)
- **S-FIGURES** + any GPU eval (reads results/, writes docs/paper/figures/ only)
- **S12**, **S13** + any GPU eval (reads results/, writes docs/paper/)

---

## File Conflict Map

No lane writes to another lane's primary output directory. Worktree merges will be conflict-free as long as sessions stay within their designated write targets.

| Directory | S-VERIFY | S10/S10b | S-TIMING | S-DEPS | S-TAXONOMY | S-ANALYSIS | S-FIGURES | S12/S13 | W-S15 | W-S16 | W-S17 | S18 |
|-----------|:--------:|:--------:|:--------:|:------:|:----------:|:----------:|:---------:|:-------:|:-----:|:-----:|:-----:|:---:|
| `rodinia/rodinia-src/` | **W** | **W** | **W** | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `results/evaluation/` | **W** | **W** | **W** | -- | R | R | R | R | R | -- | -- | R |
| `harness/` | **W** | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `docs/paper/` | -- | -- | -- | -- | -- | -- | **W** (figs) | **W** | **W** | -- | **W** | **W** |
| `docs/paper/figures/` | -- | -- | -- | -- | -- | -- | **W** | -- | -- | -- | R | R |
| `visualizations/` | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| `scripts/analysis/` | -- | -- | -- | -- | **W** | **W** | -- | -- | -- | -- | -- | -- |
| project root | -- | -- | -- | **W** (req.txt, pyproject.toml, Dockerfile) | -- | -- | -- | -- | -- | -- | -- | -- |
| anonymous repo (external) | -- | -- | -- | -- | -- | -- | -- | -- | -- | **W** | -- | -- |

**W** = writes to this directory. **R** = reads from this directory. **--** = no interaction.

### Potential Conflicts to Monitor

1. **`docs/paper/`**: S-FIGURES (figures/), S12 (paper_draft.md Sections 1-2), S13 (paper_draft.md Sections 6-8), W-S15 (annotations/comments), W-S17 (LaTeX files). These write to different files within the directory but touch the same parent. Merge order: S-FIGURES first, then S12/S13, then W-S15, then W-S17.
2. **`results/evaluation/`**: S-VERIFY may update result JSONs with corrected verification status. S10/S10b add new result files. No overlap (different filenames), but S-FIGURES and S13 should wait for S-VERIFY to finish before reading.

---

## EVALUATION AND ANALYSIS SESSION PROMPTS

---

## SESSION S10 — Third Direction: cuda-to-opencl (Rodinia)

**Priority: P1 — HIGH** | **Group 2** | **Lane: GPU (tmux)** | **Duration: 1 day compute** | **Worktree: NO**

```
ultrathink

# Models (3 active — azure-gpt-4.1 DISABLED by Gal 2026-03-24):
# claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — 3 models (azure-gpt-4.1 DISABLED by Gal 2026-03-24)
- [ ] nn-opencl is KNOWN_FAIL for ORIGINAL code, but the LLM writes NEW code.
      However, the spec's run args use "filelist.txt" which may not exist —
      the LLM-generated code could TIMEOUT regardless of quality. Fix nn-opencl
      run args to "filelist_4" before running? Or accept it will fail due to
      spec issues?
- [ ] kmeans-opencl is also KNOWN_FAIL (SIGSEGV). Same question: include it
      as a data point or exclude?
- [ ] L0 only for this direction. Confirmed?

EXTERNAL DEPS:
- [x] Sessions 1 + 1.5 + 1.6 must be complete — DONE
- [x] Session 3b complete (all 3 active models have L0 baselines)
- [x] S-VERIFY COMPLETED (2026-03-27) — results verified with stdout_pattern+exit_code conjunction
- [x] API keys for 3 models (ANTHROPIC_API_KEY, GEMINI_API_KEY, GROQ_API_KEY)

# Session Goal
Run cuda-to-opencl evaluation for eligible Rodinia kernels with 3 models at L0.
This is direction #3 of 6 in the Translation Direction Matrix. OpenCL directions
will test whether the direction asymmetry observed in S9 (cuda-to-omp 41.7% vs
omp-to-cuda 22.9%) extends to CUDA↔OpenCL translation.

# Why This Matters
Currently zero Rodinia OpenCL direction data exists. The paper claims cross-API
evaluation but has no OpenCL results for Rodinia — only XSBench (S8) has OpenCL
data. Adding this direction tests cross-vendor API translation (NVIDIA-specific
CUDA → vendor-neutral OpenCL) and substantially strengthens the paper's scope.

# IMPORTANT: Translation target rules (Session 1.6 family rules)
# OpenCL target specs have translation_targets = .cl files ONLY (Family 1 rule).
# The host .cpp driver is Target Infrastructure Context (read-only, not produced by LLM).
# The LLM produces ONLY the .cl device kernel file(s).
# Scientific question: "Can the LLM produce correct OpenCL C kernel code given the
# host driver as context?" Expected: pass rates somewhat lower than cuda-to-omp
# because OpenCL kernel language has distinct idioms (get_global_id, __kernel, etc.)

# Context
# 20 Rodinia specs have OpenCL variants. After excluding 2 KNOWN_FAIL (nn-opencl,
# kmeans-opencl), 18 specs are eligible. But only kernels with BOTH cuda AND opencl
# specs can form a translation pair.
#
# Eligible cuda-to-opencl kernels (18): backprop, bfs, bptree, cfd, dwt2d, gaussian,
#   heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter,
#   pathfinder, srad, streamcluster
#   (Note: dwt2d and gaussian have OpenCL specs but no OMP — eligible for THIS direction)
#   (Note: nn-opencl is KNOWN_FAIL for original code, but LLM writes NEW code —
#    include it, expect it to fail, report as data point)

# Prerequisites
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 0: PRE-FLIGHT — VERIFY ELIGIBLE KERNELS
# ============================================================

# Step 0: Confirm which Rodinia kernels have BOTH cuda and opencl specs
ls specs/rodinia-*-cuda.json | sed 's/-cuda.json//' | while read base; do
  if [ -f "${base}-opencl.json" ]; then echo "ELIGIBLE: $(basename $base)"; fi
done
# Expected: ~18 kernels. Exclude nn-opencl and kmeans-opencl from target list
# (KNOWN_FAIL as verification targets, though LLM writes new code).
# Decision above determines whether to include or exclude these 2.

# ============================================================
# PART 1: RUN EVALUATION
# ============================================================

# Step 1: Run all 3 models in tmux (SSH disconnect safety)
# Expected: 54 tasks (18 kernels x 3 models), ~3-6 hours
tmux new-session -d -s s10
tmux send-keys -t s10 'cd /home/samyak/Desktop/parbench_sam && source env_parbench/bin/activate && python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-opencl \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v 2>&1 | tee results/evaluation/s10_cuda_to_opencl.log' Enter

# Monitor: tmux attach -t s10
# If SSH disconnects, re-attach with: tmux attach -t s10

# ============================================================
# PART 2: POST-EVAL ANALYSIS (run after Step 1 completes)
# ============================================================

# Step 2: Verify completion — expect 18 files per model (or 16 if nn+kmeans excluded)
for model in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
  count=$(ls results/evaluation/$model/rodinia-*-cuda-to-rodinia-*-opencl.json 2>/dev/null | grep -v "L[1-4]" | wc -l)
  echo "$model: $count cuda-to-opencl L0 files"
done
# If any model has fewer than expected, re-run Step 1 (--resume will skip completed tasks)

# Step 3: Regenerate analysis with all completed directions
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl \
  --expected-levels 0

# Step 4: Direction comparison — write a small verification script that:
# 1. Counts cuda-to-opencl results per model
# 2. Compares pass rates: cuda-to-omp vs cuda-to-opencl
#    (is OpenCL translation harder than OMP translation?)
# 3. Compares with omp-to-cuda (S9) for three-way direction comparison
# 4. Shows per-kernel × per-model breakdown table
# 5. Identifies which kernels PASS despite multi-file .cl requirement
# 6. Checks if all OpenCL results have translation_mode="kernel_centric"
# Save output to results/evaluation/s10_direction_comparison.txt
# DELETE the script itself after running.

# ============================================================
# PART 3: COMMIT AND HANDOFF
# ============================================================

# Step 5: Stage and commit results
git add results/evaluation/claude-sonnet-4-6/rodinia-*-cuda-to-rodinia-*-opencl*.json
git add results/evaluation/gemini-2.5-flash-lite/rodinia-*-cuda-to-rodinia-*-opencl*.json
git add results/evaluation/groq-llama-3.3-70b-versatile/rodinia-*-cuda-to-rodinia-*-opencl*.json
git add results/evaluation/batch_cuda-to-opencl_*.json results/evaluation/batch_cuda-to-opencl_*.md
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git add results/evaluation/s10_cuda_to_opencl.log results/evaluation/s10_direction_comparison.txt
git add visualizations/eval_results_data.js

# Commit message:
# "S10: Rodinia cuda-to-opencl L0 eval (18 kernels x 3 models) + 3-direction comparison"

# Step 6: Show me the results summary:
# - cuda-to-opencl pass rate per model
# - Comparison: cuda-to-omp vs cuda-to-opencl vs omp-to-cuda pass rates
# - Top 3 failure root causes for cuda-to-opencl (from build_error_snippet)
# - Any kernels that PASS in all 3 directions (interesting positive results)

# ============================================================
# KEY ANALYSIS QUESTIONS (for paper Section 6)
# ============================================================
# - Is cuda-to-opencl harder than cuda-to-omp? (expected: yes, different kernel language)
# - Is the gap between cuda→opencl and cuda→omp consistent across models?
# - Does translation complexity (single_file vs multi_to_single) predict opencl pass rate?
# - Are BUILD_FAIL errors different in kind for opencl vs omp? (e.g., OpenCL-specific
#   compilation errors vs general C++ errors)
# - Are there kernels that only PASS for opencl but not omp, or vice versa?
# These feed directly into paper Section 6 cross-direction analysis.
```

### GPU Sequencing
- Must NOT run concurrently with S-VERIFY, S10b, or S-TIMING
- CAN run concurrently with any worktree session, S-TAXONOMY, S-ANALYSIS, S-DEPS, S12, S-BIB

### Acceptance Criteria
- [ ] All eligible kernel x model combinations have result JSONs in `results/evaluation/{model}/`
- [ ] `eval_summary.json` and `eval_summary.md` updated with cuda-to-opencl direction
- [ ] Log file saved to `results/evaluation/s10_cuda_to_opencl.log`
- [ ] Direction comparison file at `results/evaluation/s10_direction_comparison.txt` with 3-direction pass rate matrix
- [ ] Quick analysis: pass rate by model + comparison with cuda-to-omp and omp-to-cuda rates
- [ ] All result JSONs have `translation_mode: "kernel_centric"`

### Agent Delegation
- Use `eval-batcher` agent (background) for Step 1 — it runs the eval batch in tmux
- After completion, main session handles analysis (Steps 2-6)
- If errors occur during eval, use `explorer` agent to read specific result JSONs and diagnose

### Estimated Duration
- **Compute:** 3-6 hours (54 tasks, each takes 2-5 min including LLM call + build + verify)
- **Analysis:** 30 min post-compute
- **Total wall clock:** ~1 day (launch in morning, analyze in evening)

---

## SESSION S10b — Remaining Rodinia Cross-API Directions (#4-#6)

**Priority: P2 — MEDIUM** | **Group 3** | **Lane: GPU (tmux)** | **Duration: 1 day compute** | **Worktree: NO**

```
ultrathink

# Models (3 active — azure-gpt-4.1 DISABLED by Gal 2026-03-24):
# claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — 3 models (azure-gpt-4.1 DISABLED by Gal 2026-03-24)
- [ ] Session 10 (cuda-to-opencl) must be complete before this session. Confirmed?
- [ ] L0 only for all 3 directions. No augmentation. Confirmed?
- [ ] Should L1/L2 augmentation also be run for these 3 directions?
      Adds 3 dirs x 2 levels x ~16 kernels x 3 models = ~288 API calls.
      Recommendation: L0 only to match Sessions 9/10 scope.

EXTERNAL DEPS:
- [x] Sessions 1 + 1.5 + 1.6 must be complete — DONE
- [ ] Session 10 (cuda-to-opencl) must be complete (establishes opencl baseline)
- [x] Session 3b complete (all 3 active models have L0 baselines)
- [x] API keys for 3 models (ANTHROPIC_API_KEY, GEMINI_API_KEY, GROQ_API_KEY)

# Session Goal
Run the 3 remaining Rodinia-viable translation directions:
  - opencl-to-cuda (direction #4)
  - opencl-to-omp (direction #5)
  - omp-to-opencl (direction #6)
These complete the full 6-direction Rodinia cross-API matrix for the SC26 paper.

# Why This Matters
After S9 (omp-to-cuda) and S10 (cuda-to-opencl), 3 directions remain. Completing
all 6 enables the paper to present a complete bidirectional translation matrix:
  cuda ↔ omp (S2/S3/S7 + S9)
  cuda ↔ opencl (S10 + this session)
  omp ↔ opencl (this session)

Scientific questions per direction:
  - opencl-to-cuda (#4): Can LLMs translate FROM vendor-neutral TO NVIDIA-specific?
    Reverse of S10. Tests whether CUDA training data abundance helps the LLM
    when generating CUDA code from OpenCL source.
  - opencl-to-omp (#5): Cross-paradigm — GPU device kernel → CPU threaded code.
    The LLM must recognize OpenCL parallelism and map it to OMP fork-join model.
  - omp-to-opencl (#6): CPU threaded → GPU device kernel. Expected to be the hardest
    direction — the LLM must decompose a monolithic parallel region into a separate
    .cl kernel file with appropriate host/device structure.

# IMPORTANT: Translation target rules (Session 1.6 family rules)
# - opencl-to-cuda: SOURCE = .cl file(s), TARGET = CUDA files = prompt_payload (Family 3)
# - opencl-to-omp: SOURCE = .cl file(s), TARGET = OMP curated files (Family 2)
# - omp-to-opencl: SOURCE = OMP curated files (Family 2), TARGET = .cl file(s) only (Family 1)
# The pipeline handles all of this automatically via translation_targets in each spec.

# Eligible kernels per direction (after KNOWN_FAIL exclusions):

# opencl-to-cuda (17 Rodinia):
# All cuda-opencl overlapping kernels, minus:
#   - kmeans: cuda target KNOWN_FAIL + opencl source KNOWN_FAIL
#   - hybridsort: cuda target KNOWN_FAIL
#   - nn: opencl source KNOWN_FAIL
#   - mummergpu: cuda target KNOWN_FAIL (no opencl spec anyway)
# = 17 eligible: backprop, bfs, bptree, cfd, dwt2d, gaussian, heartwall, hotspot,
#   hotspot3d, lavamd, lud, myocyte, nw, particlefilter, pathfinder, srad, streamcluster
OPENCL_TO_CUDA_KERNELS="backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# opencl-to-omp (15 Rodinia):
# All omp-opencl overlapping kernels, minus:
#   - kmeans: opencl source KNOWN_FAIL
#   - nn: opencl source KNOWN_FAIL
#   - mummergpu: omp target KNOWN_FAIL
# = 15 eligible: backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud,
#   myocyte, nw, particlefilter, pathfinder, srad, streamcluster
OPENCL_TO_OMP_KERNELS="backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# omp-to-opencl (15 Rodinia):
# All omp-opencl overlapping kernels, minus:
#   - kmeans: opencl target KNOWN_FAIL
#   - nn: opencl target KNOWN_FAIL
#   - mummergpu: omp source KNOWN_FAIL
# = 15 eligible (same set as opencl-to-omp, symmetric exclusion)
OMP_TO_OPENCL_KERNELS="backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# Prerequisites
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 1: RUN ALL 3 DIRECTIONS SEQUENTIALLY
# ============================================================
# These run sequentially because they share rodinia-src/ directories.
# Total: (17 + 15 + 15) x 3 models = 141 tasks

# Step 1: Direction #4 — opencl-to-cuda
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction opencl-to-cuda \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OPENCL_TO_CUDA_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# Step 2: Direction #5 — opencl-to-omp
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction opencl-to-omp \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OPENCL_TO_OMP_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# Step 3: Direction #6 — omp-to-opencl
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction omp-to-opencl \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OMP_TO_OPENCL_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# ============================================================
# PART 2: POST-EVAL ANALYSIS
# ============================================================

# Step 4: Verify completion — count files per direction per model
echo "=== COMPLETION CHECK ==="
for dir in opencl-to-cuda opencl-to-omp omp-to-opencl; do
  src=$(echo $dir | cut -d'-' -f1)
  tgt=$(echo $dir | cut -d'-' -f3)
  for model in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
    count=$(ls results/evaluation/$model/rodinia-*-${src}-to-rodinia-*-${tgt}.json 2>/dev/null | grep -v "L[1-4]" | wc -l)
    echo "$dir | $model: $count L0 files"
  done
done

# Step 5: Regenerate analysis with ALL 6 directions
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda opencl-to-omp omp-to-opencl \
  --expected-levels 0

# Step 6: Build the full 6-direction × 3-model pass rate matrix
# Write a verification script that:
# 1. Counts results per direction per model
# 2. Builds the complete 6x3 pass rate matrix (plus azure-gpt-4.1 for cuda-to-omp only)
# 3. Identifies the "hardest direction" (lowest aggregate pass rate)
# 4. Identifies the "easiest direction" (highest aggregate pass rate)
# 5. Checks symmetry: does cuda-to-opencl ≈ opencl-to-cuda?
# 6. Checks symmetry: does cuda-to-omp ≈ omp-to-cuda? (known: asymmetric from S9)
# 7. Checks symmetry: does omp-to-opencl ≈ opencl-to-omp?
# 8. Which kernels pass in ALL 6 directions? (universally easy kernels)
# 9. Which kernels fail in ALL 6 directions? (universally hard kernels)
# 10. Failure taxonomy per direction: proportion of BUILD_FAIL vs RUN_FAIL vs EXTRACTION_FAIL
# Save output to results/evaluation/s10b_full_direction_matrix.txt
# DELETE the script after running.

# ============================================================
# PART 3: COMMIT AND HANDOFF
# ============================================================

# Step 7: Stage and commit
git add results/evaluation/claude-sonnet-4-6/rodinia-*-opencl-to-rodinia-*-cuda*.json
git add results/evaluation/claude-sonnet-4-6/rodinia-*-opencl-to-rodinia-*-omp*.json
git add results/evaluation/claude-sonnet-4-6/rodinia-*-omp-to-rodinia-*-opencl*.json
git add results/evaluation/gemini-2.5-flash-lite/rodinia-*-opencl-to-rodinia-*-cuda*.json
git add results/evaluation/gemini-2.5-flash-lite/rodinia-*-opencl-to-rodinia-*-omp*.json
git add results/evaluation/gemini-2.5-flash-lite/rodinia-*-omp-to-rodinia-*-opencl*.json
git add results/evaluation/groq-llama-3.3-70b-versatile/rodinia-*-opencl-to-rodinia-*-cuda*.json
git add results/evaluation/groq-llama-3.3-70b-versatile/rodinia-*-opencl-to-rodinia-*-omp*.json
git add results/evaluation/groq-llama-3.3-70b-versatile/rodinia-*-omp-to-rodinia-*-opencl*.json
git add results/evaluation/batch_opencl-to-cuda_*.json results/evaluation/batch_opencl-to-cuda_*.md
git add results/evaluation/batch_opencl-to-omp_*.json results/evaluation/batch_opencl-to-omp_*.md
git add results/evaluation/batch_omp-to-opencl_*.json results/evaluation/batch_omp-to-opencl_*.md
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git add results/evaluation/s10b_full_direction_matrix.txt
git add visualizations/eval_results_data.js

# Commit message:
# "S10b: Rodinia cross-API eval directions #4-6 (opencl-to-cuda, opencl-to-omp, omp-to-opencl; 141 tasks)"

# Step 8: Show me:
# - The full 6-direction × 3-model pass rate matrix
# - Direction difficulty ordering (easiest → hardest)
# - Symmetry analysis: are reverse directions equally hard?
# - Universally easy/hard kernels
# - Key paper finding: "Translation difficulty ordering: [direction list by pass rate]"

# ============================================================
# KEY ANALYSIS QUESTIONS (for paper Section 6)
# ============================================================
# - What is the complete direction difficulty ordering?
# - Is the omp↔opencl pair the hardest? (expected: yes, different paradigm + different API)
# - Is there a "training data effect"? (CUDA as target may be easier because LLMs
#   have seen more CUDA code in training)
# - Does Claude dominate across ALL directions, or only CUDA-involving ones?
# - Which failure mode (BUILD_FAIL, RUN_FAIL, EXTRACTION_FAIL) dominates per direction?
# - How does the 6-direction pass rate matrix compare with XSBench's 12-direction data (S8)?
# These feed directly into paper Section 6 cross-direction analysis.
```

### Dependencies
- S10 must complete first (same GPU, same source dirs)
- S-VERIFY should be complete for verified results

### GPU Sequencing
- Must NOT run concurrently with S-VERIFY, S10, or S-TIMING
- CAN run concurrently with any worktree session, S-TAXONOMY, S-ANALYSIS, S12, S13

### Acceptance Criteria
- [ ] All 3 remaining directions have result JSONs in `results/evaluation/{model}/`
- [ ] Completion counts: 17 opencl-to-cuda + 15 opencl-to-omp + 15 omp-to-opencl per model (141 total tasks)
- [ ] `eval_summary.json` updated with all 6 Rodinia directions
- [ ] Full 6-direction x 3-model pass rate matrix in `results/evaluation/s10b_full_direction_matrix.txt`
- [ ] Direction difficulty ordering documented
- [ ] Symmetry analysis complete for all 3 direction pairs

### Agent Delegation
- Use `eval-batcher` agent (background) for Steps 1-3 — three sequential batch runs
- After all 3 complete, main session handles analysis (Steps 4-8)
- If a direction fails partway through, use `--resume` to restart (it skips completed tasks)

### Estimated Duration
- **Compute:** 141 tasks x ~3 min each = ~7 hours
- **Analysis:** 1 hour post-compute
- **Total wall clock:** ~1 day (launch in morning, runs through evening, analyze next morning)

---

## SESSION S-TAXONOMY — Build Error Taxonomy from Result JSONs

**Priority: P1 — HIGH** | **Group 1** | **Lane: Any** | **Duration: 3 hours** | **Worktree: YES**

```
ultrathink

## CONTEXT

You are building a structured error taxonomy from 468 evaluated LLM translation
tasks (504 raw result JSONs, minus 36 excluded kmeans/mummergpu). This is a pure
analysis task — no evals, no GPU, no harness runs. Safe for worktree execution.

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Confirm the error categories below are appropriate for the paper. Should
      we split "Retained CUDA API calls" into subcategories (memory management
      vs kernel launch vs type system)?
- [ ] Should the taxonomy include per-kernel granularity or only per-model and
      per-direction? Per-kernel adds ~17x rows but enables richer analysis.
- [ ] Should error categories be mutually exclusive (each failure gets exactly
      one category) or multi-label (a failure can have multiple root causes)?
      Recommendation: primary category (the FIRST error the compiler hits) for
      clean counting, with a secondary_categories field for multi-cause failures.

EXTERNAL DEPS:
- None. All 468 evaluated result JSONs already exist in results/evaluation/. This session
  is read-only on evaluation data. (504 raw files on disk; 36 kmeans/mummergpu excluded.)

# Session Goal
Build a structured error taxonomy from all 468 evaluated result JSONs. Classify every
non-PASS result by root cause category. Produce publication-ready tables showing
failure distributions per model, per direction, and per error category.

# Why This Matters
The paper's current failure analysis is qualitative: "retained cudaMalloc,
missing #pragma omp." SC26 reviewers expect quantitative taxonomy tables with
counts. This data exists in the `build_error_snippet` and `run_stderr_snippet`
fields of the result JSONs but has never been systematically extracted.

Current failure distribution across 468 evaluated tasks (post S-VERIFY, 2026-03-27):
  PASS: 105 (22.44%)
  BUILD_FAIL: 180 (38.46%)
  RUN_FAIL: 89 (19.02%)
  EXTRACTION_FAIL: 49 (10.47%)
  VERIFY_FAIL: 45 (9.62%)

The 363 non-PASS results each have error data that can be classified.

# Context
- Result JSONs live in: results/evaluation/{model_name}/
- 3 model directories: claude-sonnet-4-6 (168 files), gemini-2.5-flash-lite (168),
  groq-llama-3.3-70b-versatile (168). Note: 36 files are kmeans/mummergpu (excluded from summary).
- Key fields per JSON:
  - overall_status: PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR
  - build_error_snippet: truncated compiler error output (for BUILD_FAIL)
  - run_stderr_snippet: truncated runtime error output (for RUN_FAIL)
  - error_message: pipeline-level error (for EXTRACTION_FAIL, ERROR)
  - attempts[]: array of per-attempt records with status at each retry
  - model, kernel, augment_level, translation_mode: metadata for grouping

# Prerequisites
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 0: EXPLORE ERROR PATTERNS (before writing classifier)
# ============================================================

# Step 0: Use the explorer agent to sample error patterns
# Read 5 BUILD_FAIL results from different models and note common error patterns.
# Read 3 RUN_FAIL results. Read 3 EXTRACTION_FAIL results.
# This gives you the actual error text to build regex patterns from.
#
# Example: Use the explorer agent to:
#   "Read 5 BUILD_FAIL result JSONs from results/evaluation/ (mix of models).
#    For each, extract the build_error_snippet field. Note the recurring patterns."

# ============================================================
# PART 1: WRITE THE TAXONOMY CLASSIFIER
# ============================================================

# Step 1: Create scripts/analysis/build_error_taxonomy.py
# The script must:
#
# a) Read ALL result JSONs from results/evaluation/*/
#    Use glob: results/evaluation/*/*.json
#    Skip non-result files (batch_*.json, eval_summary.json, etc.)
#
# b) For each BUILD_FAIL result, read build_error_snippet and classify:
#    Category regexes (check in order — first match wins):
#
#    1. "retained_cuda_api"
#       Pattern: cudaMalloc|cudaFree|cudaMemcpy|cudaMemset|cudaDeviceSynchronize|
#                __global__|__device__|__shared__|<<<.*>>>|cudaGetLastError|
#                cuda_runtime.h|cudaError_t|cudaSuccess
#       Meaning: LLM kept CUDA API calls in supposedly-translated code
#
#    2. "retained_cuda_types"
#       Pattern: dim3|cudaStream_t|cudaEvent_t|thrust::|cub::|__half|
#                texture<|surf<|__constant__
#       Meaning: LLM kept CUDA-specific types/templates
#
#    3. "missing_target_api"
#       Pattern: (for omp targets) no "#pragma omp" found in translated code
#                (for opencl targets) no "__kernel" or "get_global_id" found
#       Note: requires reading translated_files content, not just error snippet
#       Meaning: LLM failed to introduce target API constructs
#
#    4. "missing_header"
#       Pattern: fatal error:.*No such file|cannot find.*include|
#                file not found|#include.*error
#       Meaning: missing or wrong #include directives
#
#    5. "type_mismatch"
#       Pattern: cannot convert|incompatible type|no matching function|
#                invalid.*argument|no viable conversion
#       Meaning: C/C++ type errors from incorrect API usage
#
#    6. "syntax_error"
#       Pattern: expected.*before|unexpected|parse error|
#                unterminated|missing.*bracket|stray.*in program
#       Meaning: malformed code output
#
#    7. "linker_error"
#       Pattern: undefined reference|multiple definition|unresolved external|
#                ld returned|collect2: error
#       Meaning: compilation succeeded but linking failed
#
#    8. "other_build"
#       Everything else
#
# c) For each RUN_FAIL result, read run_stderr_snippet and classify:
#    1. "segfault" — SIGSEGV|Segmentation fault|signal 11
#    2. "timeout" — exceeded timeout|TIMEOUT|killed.*timeout
#    3. "wrong_exit_code" — non-zero exit, no crash signal
#    4. "abort" — SIGABRT|Aborted|signal 6
#    5. "other_runtime" — everything else
#
# d) For each EXTRACTION_FAIL result, read error_message and classify:
#    1. "no_code_blocks" — no code block|no.*extracted|empty response
#    2. "missing_files" — expected file|not found in output
#    3. "malformed_output" — everything else
#
# e) Produce 3 output files:
#
#    results/analysis/error_taxonomy.json — structured data:
#    {
#      "total_results": 468,
#      "total_failures": 363,
#      "by_status": {"BUILD_FAIL": 180, "RUN_FAIL": 89, "VERIFY_FAIL": 45, "EXTRACTION_FAIL": 49},
#      "build_fail_categories": {
#        "retained_cuda_api": {"count": N, "by_model": {...}, "by_direction": {...}},
#        ...
#      },
#      "run_fail_categories": {...},
#      "extraction_fail_categories": {...},
#      "per_result": [
#        {"file": "...", "model": "...", "kernel": "...", "status": "...",
#         "primary_category": "...", "error_snippet_head": "first 200 chars"}
#      ]
#    }
#
#    results/analysis/error_taxonomy.md — publication-ready markdown:
#    - Table 1: BUILD_FAIL category counts per model
#    - Table 2: RUN_FAIL category counts per model
#    - Table 3: EXTRACTION_FAIL category counts per model
#    - Table 4: Top 10 most-failed kernels with primary failure mode
#    - Table 5: Error category distribution per translation direction
#
#    Console: summary with key findings

# ============================================================
# PART 2: RUN AND VALIDATE
# ============================================================

# Step 2: Run the taxonomy classifier
mkdir -p results/analysis
python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam

# Step 3: Validate — every non-PASS result must be classified
python3 -c "
import json
data = json.load(open('results/analysis/error_taxonomy.json'))
total_classified = sum(cat['count'] for cat in data['build_fail_categories'].values())
total_classified += sum(cat['count'] for cat in data['run_fail_categories'].values())
total_classified += sum(cat['count'] for cat in data['extraction_fail_categories'].values())
# Add ERROR count if present
total_classified += data.get('error_count', 0)
print(f'Total failures: {data[\"total_failures\"]}')
print(f'Total classified: {total_classified}')
assert total_classified == data['total_failures'], f'MISMATCH: {total_classified} classified vs {data[\"total_failures\"]} failures'
print('VALIDATION PASSED: every failure is classified')
"

# Step 4: Review the markdown tables
# Read results/analysis/error_taxonomy.md
# Verify:
# - All BUILD_FAIL categories sum to 180
# - All RUN_FAIL categories sum to 89
# - All EXTRACTION_FAIL categories sum to 49
# - All VERIFY_FAIL categories sum to 45
# - No double-counting across categories

# Step 5: Refine categories if needed
# If "other_build" or "other_runtime" has >20% of its status category,
# the regexes need refinement. Read the actual error snippets in "other"
# results and add more specific patterns.

# ============================================================
# PART 3: COMMIT
# ============================================================

# Step 6: Stage and commit
git add scripts/analysis/build_error_taxonomy.py
git add results/analysis/error_taxonomy.json
git add results/analysis/error_taxonomy.md

# Commit message:
# "S-TAXONOMY: Build error taxonomy from 468 result JSONs (8 BUILD_FAIL + 5 RUN_FAIL + 3 EXTRACTION_FAIL + VERIFY_FAIL categories)"

# Step 7: Show me:
# - Top 3 BUILD_FAIL root causes with counts and percentages
# - Top 3 RUN_FAIL root causes
# - Which model has the most "retained_cuda_api" errors? (expected: weaker models)
# - Which direction has the most BUILD_FAIL? (expected: omp-to-cuda, adding GPU parallelism)
# - Key paper finding: a one-sentence summary of the error taxonomy
```

### Acceptance Criteria
- [ ] `scripts/analysis/build_error_taxonomy.py` exists and runs without error
- [ ] `results/analysis/error_taxonomy.json` exists with per-model, per-direction, per-category counts
- [ ] `results/analysis/error_taxonomy.md` has publication-ready tables (5 tables minimum)
- [ ] Every non-PASS result is classified into exactly one primary category
- [ ] Validation check passes: total classified == total failures (363)
- [ ] "other" categories contain <20% of their respective status totals
- [ ] Top 3 BUILD_FAIL root causes identified with counts
- [ ] Top 3 RUN_FAIL root causes identified with counts

### Agent Delegation
- Use `explorer` agent in Step 0 to sample 10-15 result JSONs before writing the classifier
- This exploration phase is critical — writing regex patterns without seeing actual error text will produce a poor classifier

### Parallel Group Assignment
- **Group 1** — runs immediately, no dependencies
- Safe to run concurrently with S-VERIFY (reads results, does not modify them)
- Safe to run concurrently with S-ANALYSIS, S-DEPS, W-S16

### Estimated Duration
- **Exploration (Step 0):** 30 min
- **Script writing (Step 1):** 1 hour
- **Running + validation (Steps 2-5):** 30 min
- **Refinement iteration:** 30 min (if "other" category too large)
- **Commit + reporting (Steps 6-7):** 15 min
- **Total:** ~3 hours

---

## SESSION S-ANALYSIS — SLoC + Token Usage + Self-Repair Enrichment

**Priority: P2 — MEDIUM** | **Group 1** | **Lane: Any** | **Duration: 3 hours** | **Worktree: YES**

```
ultrathink

## CONTEXT

You are extracting three independent analyses from EXISTING data — no new evals
needed. All 468 evaluated result JSONs + spec files + source files are available. Safe for
worktree execution (though SLoC counting needs source files — see Part 1 note).

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] SLoC counting method: PHYSICAL lines (non-blank, non-comment) or LOGICAL
      lines (statements)? Recommendation: physical SLoC — simpler, industry-standard
      (what cloc and sloccount report), matches ParEval-Repo's methodology.
- [ ] Should token analysis include the azure-gpt-4.1 data (17 legacy results, model DISABLED)?
      It uses a different API and has no L1-L4 data. Recommendation: include
      for cross-model comparison but note the smaller sample size.
- [ ] For self-repair analysis: count only "full repair" (status improved to PASS)
      or also "partial repair" (BUILD_FAIL → RUN_FAIL, i.e., got further)?
      Recommendation: both — partial repair shows the LLM understood the error.

EXTERNAL DEPS:
- None. All data already exists. This session is read-only on results/.
- NOTE: SLoC counting (Part 1) needs access to source files in rodinia/rodinia-src/.
  If running in a worktree, the submodule will be EMPTY. Two options:
    a) Run Part 1 in main checkout only (read source files there)
    b) Count SLoC from the translated_files field in result JSONs (approximate)
    c) Count SLoC from the prompt_payload files listed in specs (need actual files)
  Recommendation: option (b) — use translated_files from result JSONs as a proxy.
  The LLM's output closely mirrors source SLoC. For exact source SLoC, Parts 2-3
  can run in worktree while Part 1 runs in main checkout.

# Session Goal
Extract three publication-ready analyses from existing result data:
  1. SLoC characterization of evaluated kernels
  2. Token usage analysis (cost, efficiency, prompt size vs success)
  3. Self-repair breakdown by failure type and model

# Why This Matters
1. SLoC: The paper discusses ParEval-Repo's 133 SLoC threshold but does not report
   ParBench's own SLoC distribution. Reviewers will ask "how complex are YOUR benchmarks?"
2. Token usage: Every result JSON has prompt_tokens and completion_tokens fields.
   Token cost per translation, prompt size vs. success correlation, and per-model
   efficiency are free insights that demonstrate rigor.
3. Self-repair: The paper reports aggregate "25% improvement from self-repair"
   but does not break down by failure type or model. The attempts[] arrays contain
   per-attempt status data that enables this breakdown.

# Context
- 468 evaluated result JSONs in results/evaluation/{model}/ (504 raw; 36 kmeans/mummergpu excluded)
- Each has: prompt_tokens, completion_tokens, total_attempts, attempts[]
- 18 kernels evaluated (17 Rodinia + 1 XSBench)
- Source files in rodinia/rodinia-src/ (EMPTY in worktree) and xsbench/xsbench-src/ (gitignored)
- Specs in specs/ with prompt_payload and translation_targets fields

# Prerequisites
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 1: SLoC CHARACTERIZATION
# ============================================================

# Step 1: Create scripts/analysis/sloc_analysis.py
# The script must:
#
# a) For each of the 18 evaluated kernels, determine the source files:
#    - Read the CUDA spec: specs/rodinia-{kernel}-cuda.json
#    - The prompt_payload field lists the kernel source files
#    - Also read translation_targets (the files the LLM must produce)
#
# b) Count SLoC two ways:
#    METHOD 1 (if source files available — main checkout only):
#      Read each file in prompt_payload from the actual source directory
#      Count non-blank, non-comment lines (skip lines matching: ^\s*$ | ^\s*// | ^\s*/\* | ^\s*\*)
#    METHOD 2 (worktree-safe fallback):
#      Read the PASS result JSON for claude-sonnet-4-6 (strongest model)
#      The translated_files field contains the LLM output — count SLoC there
#      Note: this is TARGET SLoC, not source SLoC. Document the distinction.
#
# c) Report per kernel:
#    - kernel name
#    - source API (always "cuda" for primary direction)
#    - number of source files (len(prompt_payload))
#    - total SLoC across all source files
#    - number of target files (len(translation_targets))
#    - translation_complexity class (from spec or from classify_translation_pairs.py)
#    - category (from spec: ml, graph, physics, stencil, etc.)
#
# d) Summary statistics:
#    - min, max, mean, median SLoC
#    - SLoC distribution (how many kernels < 100, 100-500, 500-1000, > 1000)
#    - Comparison with ParEval-Repo threshold (133 SLoC)
#    - Correlation: SLoC vs. pass rate (do larger kernels fail more often?)
#
# e) Output:
#    results/analysis/sloc_analysis.json — structured per-kernel data
#    results/analysis/sloc_analysis.md — publication-ready table

# Step 2: Run SLoC analysis
mkdir -p results/analysis
python3 scripts/analysis/sloc_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 2: TOKEN USAGE ANALYSIS
# ============================================================

# Step 3: Create scripts/analysis/token_analysis.py
# The script must:
#
# a) Read ALL 468 evaluated result JSONs (skip kmeans/mummergpu)
#
# b) Compute per-model statistics:
#    - mean, median prompt_tokens
#    - mean, median completion_tokens
#    - total tokens consumed (prompt + completion, summed across all results)
#    - mean llm_response_time_seconds
#    - tokens per second (completion_tokens / llm_response_time_seconds)
#
# c) Compute per-kernel statistics:
#    - mean prompt_tokens per kernel (averaged across models)
#    - correlation: prompt_tokens vs. pass rate
#      (do larger prompts — more source code — correlate with lower pass rates?)
#    - correlation: completion_tokens vs. pass/fail
#      (do successful translations use more or fewer tokens than failures?)
#
# d) Compute per-direction statistics:
#    - mean prompt_tokens per direction
#    - mean completion_tokens per direction
#    - is there a direction that requires significantly more output tokens?
#
# e) Compute cost estimate:
#    - Using approximate per-token pricing (document assumptions):
#      Claude: $3/M input, $15/M output
#      Gemini Flash-Lite: $0.075/M input, $0.30/M output
#      Groq Llama: $0.59/M input, $0.79/M output
#      Azure GPT-4.1: $2/M input, $8/M output
#    - Total cost per model, total cost overall
#    - Cost per successful translation (total cost / PASS count)
#
# f) Compute per-augmentation-level statistics (L0-L4):
#    - mean prompt_tokens per level (augmentation adds code → larger prompts)
#    - pass rate vs. level (already in eval_summary, but correlate with tokens)
#
# g) Output:
#    results/analysis/token_analysis.json — structured data
#    results/analysis/token_analysis.md — publication-ready tables:
#      Table 1: Per-model token usage summary
#      Table 2: Per-kernel prompt size and pass rate
#      Table 3: Per-direction token usage
#      Table 4: Estimated cost per model
#      Table 5: Augmentation level vs prompt size

# Step 4: Run token analysis
python3 scripts/analysis/token_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 3: SELF-REPAIR ENRICHMENT
# ============================================================

# Step 5: Create scripts/analysis/selfrepair_analysis.py
# The script must:
#
# a) Read ALL 468 evaluated result JSONs (skip kmeans/mummergpu)
#
# b) Identify multi-attempt results (total_attempts > 1)
#    For each, read the attempts[] array:
#    - attempt 1 status (build_status, run_status, verify_status)
#    - attempt 2 status
#    - attempt 3 status (if max_retries=2, there can be up to 3 attempts)
#
# c) Classify repair outcomes:
#    - "full_repair": attempt N failed, final attempt PASS
#    - "partial_repair": status improved but not to PASS
#      (e.g., BUILD_FAIL → RUN_FAIL means it compiled but crashed)
#    - "no_repair": same or worse status across attempts
#    - "regression": status got worse (e.g., RUN_FAIL → BUILD_FAIL)
#
# d) Compute per-model repair statistics:
#    - total multi-attempt results
#    - full repair count and rate
#    - partial repair count and rate
#    - no repair count
#    - regression count
#
# e) Compute per-initial-failure repair statistics:
#    - of BUILD_FAIL attempt-1 results: what % eventually PASS?
#    - of RUN_FAIL attempt-1 results: what % eventually PASS?
#    - of EXTRACTION_FAIL attempt-1 results: what % eventually PASS?
#    - which initial failure type is most repairable?
#
# f) Compute per-kernel repair statistics:
#    - which kernels are most repairable? (highest full_repair rate)
#    - which kernels never get repaired? (0% full_repair)
#
# g) Output:
#    results/analysis/selfrepair_analysis.json — structured data
#    results/analysis/selfrepair_analysis.md — publication-ready tables:
#      Table 1: Per-model self-repair summary
#      Table 2: Repair rate by initial failure type
#      Table 3: Most/least repairable kernels
#      Table 4: Repair trajectory examples (specific attempt sequences)

# Step 6: Run self-repair analysis
python3 scripts/analysis/selfrepair_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam

# ============================================================
# PART 4: VALIDATE ALL THREE ANALYSES
# ============================================================

# Step 7: Cross-validation checks
python3 -c "
import json, os

# Check SLoC analysis
sloc = json.load(open('results/analysis/sloc_analysis.json'))
print(f'SLoC: {len(sloc[\"kernels\"])} kernels analyzed')
assert len(sloc['kernels']) >= 17, f'Expected >=17 kernels, got {len(sloc[\"kernels\"])}'

# Check token analysis
tokens = json.load(open('results/analysis/token_analysis.json'))
total = sum(m['total_results'] for m in tokens['by_model'].values())
print(f'Token analysis: {total} results analyzed')
assert total == 468, f'Expected 468 results, got {total}'

# Check self-repair analysis
repair = json.load(open('results/analysis/selfrepair_analysis.json'))
multi = repair['total_multi_attempt']
print(f'Self-repair: {multi} multi-attempt results analyzed')

# Cross-check: repair totals should match
full = repair['full_repair_count']
partial = repair.get('partial_repair_count', 0)
no_repair = repair.get('no_repair_count', 0)
regression = repair.get('regression_count', 0)
total_repair = full + partial + no_repair + regression
assert total_repair == multi, f'Repair categories ({total_repair}) != multi-attempt ({multi})'

print('ALL CROSS-VALIDATION CHECKS PASSED')
"

# ============================================================
# PART 5: COMMIT
# ============================================================

# Step 8: Stage and commit
git add scripts/analysis/sloc_analysis.py
git add scripts/analysis/token_analysis.py
git add scripts/analysis/selfrepair_analysis.py
git add results/analysis/sloc_analysis.json results/analysis/sloc_analysis.md
git add results/analysis/token_analysis.json results/analysis/token_analysis.md
git add results/analysis/selfrepair_analysis.json results/analysis/selfrepair_analysis.md

# Commit message:
# "S-ANALYSIS: SLoC characterization (18 kernels) + token usage (468 results) + self-repair breakdown"

# Step 9: Show me the key findings:
# SLoC:
# - Min/max/median SLoC across 18 kernels
# - How many kernels exceed ParEval-Repo's 133 SLoC threshold?
# - Does SLoC correlate with pass rate?
#
# Tokens:
# - Which model is cheapest per successful translation?
# - Total evaluation cost (all 468 evaluated tasks)?
# - Does prompt size predict failure?
#
# Self-repair:
# - Overall full-repair rate (% of multi-attempt results that eventually PASS)
# - Which model repairs best?
# - Which failure type (BUILD_FAIL vs RUN_FAIL) is most repairable?
# - Most repairable kernel? Least repairable?
```

### Acceptance Criteria
- [ ] `results/analysis/sloc_analysis.json` + `.md` exist with data for all 18 kernels
- [ ] SLoC table includes: kernel name, file count, total SLoC, category, complexity class
- [ ] SLoC summary: min, max, mean, median, and comparison with 133 SLoC threshold
- [ ] `results/analysis/token_analysis.json` + `.md` exist with data for all 468 evaluated results
- [ ] Token analysis includes: per-model summary, per-kernel prompt size, cost estimates
- [ ] `results/analysis/selfrepair_analysis.json` + `.md` exist
- [ ] Self-repair analysis includes: per-model repair rates, per-failure-type repair rates
- [ ] Cross-validation passes: all three analyses cover the correct number of results/kernels
- [ ] All 6 output files (3 JSON + 3 MD) are publication-ready

### Agent Delegation
- For Part 1 (SLoC): if running in worktree, use METHOD 2 (translated_files from result JSONs).
  If running in main checkout, use METHOD 1 (actual source files) for ground-truth SLoC.
- Use `explorer` agent to sample 3-5 result JSONs at the start to understand the data structure
  (especially the attempts[] array for Part 3)
- Each Part (1/2/3) produces an independent script — they can be written and tested sequentially

### Parallel Group Assignment
- **Group 1** — runs immediately, no dependencies
- Safe to run concurrently with S-VERIFY, S-TAXONOMY, S-DEPS, W-S16
- Parts 2 and 3 are fully worktree-safe. Part 1 depends on source file availability.

### Estimated Duration
- **Part 1 (SLoC):** 45 min (script + run + validate)
- **Part 2 (Tokens):** 45 min (script + run + validate)
- **Part 3 (Self-repair):** 45 min (script + run + validate)
- **Cross-validation + commit:** 15 min
- **Total:** ~3 hours

---

## INFRASTRUCTURE FIX SESSION PROMPTS

> These sessions address systemic issues in the evaluation infrastructure that affect
> the validity and reproducibility of all results. They are numbered S-VERIFY, S-DEPS,
> and S-TIMING to distinguish them from the sequential eval sessions (S1-S18).

---

## SESSION S-VERIFY -- Fix Verification Strategy Ordering + Re-Verify PASS Results [COMPLETED 2026-03-27]

**Priority: P0 -- CRITICAL** | **Parallel Group 1** | **Lane: GPU** | **Duration: 1-2 days** | **Worktree: NO**

```
ultrathink

## BEFORE YOU START -- What I Need From You

DECISIONS:
- [ ] Verification fix approach: Option A (reorder strategies in specs so stdout_pattern
      comes first) or Option B (change verifier.py to require ALL strategies to pass).
      Recommendation: Option A is lower-risk, no code change to verifier.py.
      Option B is more robust but changes verifier semantics for all future runs.
      My recommendation: Option A first, then Option B as a follow-up if needed.
- [ ] For the 18 specs that have ONLY exit_code (no stdout_pattern at all):
      rodinia-backprop-omp, rodinia-bfs-cuda, rodinia-bfs-omp, rodinia-cfd-omp,
      rodinia-hotspot-cuda, rodinia-hotspot-omp, rodinia-hotspot-opencl,
      rodinia-hotspot3d-cuda, rodinia-hotspot3d-omp, rodinia-lavamd-cuda,
      rodinia-lavamd-omp, rodinia-lavamd-opencl, rodinia-nw-cuda,
      rodinia-pathfinder-cuda, rodinia-pathfinder-omp, rodinia-srad-cuda,
      rodinia-srad-omp, rodinia-srad-opencl.
      These need stdout_pattern strategies ADDED. Should I write patterns by reading
      each binary's actual stdout output, or defer these to a follow-up session?
- [ ] For the 169 existing PASS eval results: re-verification requires extracting
      translated code from result JSONs and re-running the harness. This is a
      multi-hour GPU-bound task. Confirm you want this done in this session.
- [ ] If re-verification reveals FALSE_PASS results (exit_code=0 but wrong stdout),
      should we update eval_summary.json immediately, or keep the original results
      and document the discrepancy separately?

EXTERNAL DEPS:
- [ ] GPU machine available (re-verification requires build+run+verify)
- [ ] Sessions 1, 1.5, 1.6 complete (specs have translation_targets)
- [ ] All eval sessions that produced PASS results should be complete before
      re-verification (S2, S3, S3b, S7, S8, S9, S10, S10b)

# Session Goal
Fix the verification strategy ordering bug that causes exit_code to short-circuit
before stdout_pattern is ever evaluated. Then re-verify all 169 existing PASS eval
results to determine how many are TRUE_PASS (correct output) vs FALSE_PASS (ran
without crashing but produced wrong output). Document findings for the paper.

# Why This Matters
The verifier in harness/verifier.py (lines 49-69) applies strategies in order and
returns on the first PASS or FAIL. All 46 specs that have both exit_code AND
stdout_pattern list exit_code FIRST. Since exit_code passes whenever the binary
exits with code 0, stdout_pattern is NEVER evaluated. This means:
- "PASS" in evaluation results means "didn't crash", NOT "produced correct output"
- The entire eval pipeline has produced ZERO VERIFY_FAIL results
- The SC26 paper cannot claim functional correctness without fixing this

This is the single most important infrastructure issue. Every PASS result in the
paper is potentially a FALSE_PASS. The paper's methodology section currently states
PASS = "successfully translated, compiled, and ran without crashing" (known-issues.md)
but fixing this would strengthen the claim to actual functional correctness.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Verifier: harness/verifier.py -- verify_run() iterates strategies, first PASS/FAIL wins
- 64 total specs (60 Rodinia + 4 XSBench)
- 46 specs have both exit_code and stdout_pattern -- ALL 46 have exit_code first
- 18 specs have ONLY exit_code (no stdout_pattern at all)
- 0 specs have stdout_pattern before exit_code (the bug is universal)
- 468 evaluated result files (504 raw on disk; 36 kmeans/mummergpu excluded), 105 are PASS
- Per-model PASS counts (post S-VERIFY): claude-sonnet-4-6=81/156, gemini-2.5-flash-lite=11/156,
  groq-llama-3.3-70b-versatile=13/156

# Verifier Code Reference (harness/verifier.py lines 49-69):
#   for strategy in strategies:
#       stype = strategy.get("type", "")
#       if stype == "exit_code":
#           result = _check_exit_code(strategy, run_result)
#       elif stype == "stdout_pattern":
#           result = _check_stdout_pattern(strategy, run_result)
#       if result.status in (Status.PASS, Status.FAIL):
#           return result  # <-- short-circuits here; stdout_pattern never reached

# ============================================================
# PART 1: AUDIT AND FIX STRATEGY ORDERING (30-60 min)
# ============================================================

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Audit all specs -- categorize verification strategies
# Write a Python script that reads every spec and reports:
# - Specs with both exit_code and stdout_pattern (and their order)
# - Specs with only exit_code (need stdout_pattern added)
# - Specs with only stdout_pattern
# - The actual stdout_pattern regex for each spec that has one
# Save output to /tmp/verification_audit.txt for reference.
# DELETE the audit script after running.

# Step 3: For all 46 specs with both strategies -- reorder so stdout_pattern comes first
# For each spec in specs/rodinia-*.json and specs/xsbench-*.json:
#   Read verification.strategies array
#   If exit_code appears before stdout_pattern, swap their positions
#   Write the spec back (preserving all other fields)
# Use a Python script for this -- do NOT edit 46 files manually.
# DELETE the reorder script after running.

# Step 4: Validate all specs still pass schema validation
python3 scripts/validate_schema.py --all
# Expected: ~135 HeCBench errors (pre-existing, ignore) + 15 phantom spec errors.
# NO new errors should appear from the strategy reordering.

# Step 5: Run harness verify on all 54 PASS Rodinia specs + 4 XSBench specs
# This confirms the baseline (reference implementations) still PASS with stdout_pattern
# evaluated first. If any flip to FAIL, the stdout_pattern regex is wrong -- fix it.
#
# The 54 PASS Rodinia specs are all 60 minus the 6 KNOWN_FAIL:
#   KNOWN_FAIL: kmeans-cuda, kmeans-opencl, nn-opencl, hybridsort-cuda,
#               mummergpu-cuda, mummergpu-omp
#
# Run each spec and record which strategy produced the verdict:
python3 -m harness -v verify specs/rodinia-bfs-cuda.json --config correctness
# Check the log output for "strategy_used" -- should now be "stdout_pattern" for
# specs that have it, not "exit_code".
#
# Write a batch verification script that runs all 54+4=58 PASS specs and collects:
#   - PASS/FAIL status
#   - Which strategy was used (exit_code or stdout_pattern)
#   - For any FAIL: what the stdout_pattern expected vs what stdout contained
# Save results to /tmp/baseline_reverify.txt
# DELETE the batch script after running.

# Step 6: For the 18 specs with ONLY exit_code -- add stdout_pattern strategies
# These specs need stdout_pattern added so that eval results can verify output.
# For each of these 18 specs:
#   1. Run the reference binary: python3 -m harness -v verify specs/<spec>.json
#   2. Capture the stdout output
#   3. Identify a distinctive pattern in the output (e.g., a checksum, "PASS",
#      a numeric result, or a unique string that appears only on correct runs)
#   4. Add a stdout_pattern strategy with that regex BEFORE exit_code in the spec
#
# The 18 specs needing stdout_pattern:
#   rodinia-backprop-omp, rodinia-bfs-cuda, rodinia-bfs-omp, rodinia-cfd-omp,
#   rodinia-hotspot-cuda, rodinia-hotspot-omp, rodinia-hotspot-opencl,
#   rodinia-hotspot3d-cuda, rodinia-hotspot3d-omp, rodinia-lavamd-cuda,
#   rodinia-lavamd-omp, rodinia-lavamd-opencl, rodinia-nw-cuda,
#   rodinia-pathfinder-cuda, rodinia-pathfinder-omp, rodinia-srad-cuda,
#   rodinia-srad-omp, rodinia-srad-opencl
#
# IMPORTANT: Run each binary FIRST to see what it actually prints.
# Do NOT guess patterns. The pattern must match the actual correctness output.
# For kernels that print numeric grids (hotspot, srad), use a checksum or
# output line count. For kernels that print a final value, match that value.

# ============================================================
# PART 2: RE-VERIFY EXISTING EVAL PASS RESULTS (4-12 hours)
# ============================================================

# Step 7: Build a re-verification pipeline
# For each of the 169 PASS eval results:
#   1. Read the result JSON -- extract translated_files content
#   2. Load the target spec
#   3. Write the translated files to the target working directory
#   4. Build the target spec (harness build)
#   5. Run the target spec (harness run, correctness config)
#   6. Verify with the FIXED strategy ordering (stdout_pattern first)
#   7. Record: original_status=PASS, reverify_status=PASS/VERIFY_FAIL
#   8. Restore original files in the target working directory
#
# This is essentially what llm_evaluate.py does in its build/run/verify cycle,
# but reading translated code from result JSONs instead of calling the LLM.
#
# Write the re-verification script as scripts/evaluation/reverify_pass_results.py
# It should:
#   - Accept --project-root and --model (optional filter, default: all models)
#   - Read result JSONs from results/evaluation/{model}/
#   - Filter to overall_status == "PASS"
#   - For each: extract files, build, run, verify, record result
#   - MUST back up and restore files (same backup/restore pattern as llm_evaluate.py)
#   - Output a summary: TRUE_PASS count, FALSE_PASS count, per-model breakdown
#   - Save detailed results to results/evaluation/reverification_audit.json
#
# CRITICAL: This script modifies files in rodinia/rodinia-src/ during execution.
# Only ONE re-verification task can run at a time (no file locking in the harness).

# Step 8: Run the re-verification (use tmux for SSH disconnect safety)
tmux new-session -d -s reverify \
  "cd /home/samyak/Desktop/parbench_sam && \
   source env_parbench/bin/activate && \
   python3 scripts/evaluation/reverify_pass_results.py \
     --project-root /home/samyak/Desktop/parbench_sam -v \
   2>&1 | tee results/evaluation/reverification.log"
echo "Re-verification launched. Monitor: tmux attach -t reverify"

# Step 9: When re-verification completes, analyze results
# Read results/evaluation/reverification_audit.json and report:
#   - Total PASS results re-verified: 169
#   - TRUE_PASS (stdout matches reference pattern): N
#   - FALSE_PASS (exit_code=0 but stdout does not match): N
#   - BUILD_FAIL on re-verify (translated code no longer builds): N (should be 0)
#   - Per-model breakdown of TRUE_PASS vs FALSE_PASS
#   - Per-kernel breakdown: which kernels have the most FALSE_PASS?
#   - Per-direction breakdown: is FALSE_PASS rate different for cuda-to-omp vs omp-to-cuda?
# Save analysis to results/evaluation/reverification_analysis.md

# ============================================================
# PART 3: UPDATE RESULTS AND COMMIT
# ============================================================

# Step 10: Update eval_summary with corrected numbers
# If any FALSE_PASS found:
#   - Regenerate eval_summary.json and eval_summary.md with corrected pass rates
#   - Update visualizations/eval_results_data.js via --write-dashboard
#   - Add a "Verification Correction" section to eval_summary.md explaining the change
# If NO FALSE_PASS found (all 169 are TRUE_PASS):
#   - Document this as a positive finding -- exit_code happened to be sufficient
#   - Still commit the strategy reordering fix as a correctness improvement

python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps

# Step 11: Update documentation
# - Update .claude/rules/known-issues.md: remove or revise the
#   "Verification Strategy Limitation" section (currently in evaluation.md)
# - Update .claude/rules/evaluation.md: document the fix and new strategy ordering
# - If FALSE_PASS found: update paper methodology guidance in evaluation.md

# Step 12: Commit
git add specs/rodinia-*.json specs/xsbench-*.json
git add results/evaluation/reverification_audit.json
git add results/evaluation/reverification_analysis.md
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git add visualizations/eval_results_data.js
git add scripts/evaluation/reverify_pass_results.py
git add .claude/rules/known-issues.md .claude/rules/evaluation.md

# Commit message:
# "S-VERIFY: Fix verification strategy ordering + re-verify 169 PASS results
#
# - Reorder strategies in 46 specs: stdout_pattern before exit_code
# - Add stdout_pattern to 18 specs that previously had only exit_code
# - Re-verify all 169 PASS eval results with corrected verification
# - Result: N TRUE_PASS, N FALSE_PASS (corrected pass rate: X%)"

# ============================================================
# KEY FINDINGS FOR PAPER (capture these in reverification_analysis.md)
# ============================================================
# 1. How many of 169 PASS are TRUE_PASS vs FALSE_PASS?
#    This number goes directly into the paper abstract and Section 6 Results.
# 2. Is the FALSE_PASS rate uniform across models, or does one model
#    produce more "runs but wrong output" translations?
# 3. Which kernels have the highest FALSE_PASS rate? These are kernels
#    where LLMs produce syntactically valid but semantically wrong translations.
# 4. Does direction matter? omp-to-cuda may have more FALSE_PASS than
#    cuda-to-omp if LLMs struggle with GPU memory management details.
# 5. The corrected pass rates are the REAL contribution of the paper.
#    "169 PASS" becomes "N TRUE_PASS" -- this is a stronger, more honest result.
```

### Acceptance Criteria
- [ ] All 46 specs with both strategies have stdout_pattern BEFORE exit_code
- [ ] 18 specs that had only exit_code now also have stdout_pattern (first position)
- [ ] Schema validation passes (no new errors beyond known HeCBench/phantom set)
- [ ] All 54 Rodinia PASS + 4 XSBench PASS specs still pass harness verify
- [ ] `reverify_pass_results.py` exists and runs to completion
- [ ] `reverification_audit.json` documents TRUE_PASS vs FALSE_PASS for all 169 results
- [ ] `reverification_analysis.md` has per-model, per-kernel, per-direction breakdown
- [ ] `eval_summary` updated with corrected numbers (if any FALSE_PASS found)

### Agent Delegation
- Use `spec-auditor` agent to validate all 64 spec files after strategy changes
- Use `verify-app` agent after spec changes to confirm no regressions
- Use `rodinia-verifier` agent to batch-verify all 54+4=58 PASS specs
- Use `explorer` agent to understand `llm_evaluate.py` backup/restore pattern
  before writing `reverify_pass_results.py` (reference lines 1050-1120 of that file)

---

## SESSION S-DEPS -- Dependency Specification + Artifact Reproducibility Prep

**Priority: P0 -- CRITICAL** | **Parallel Group 1** | **Lane: Any** | **Duration: 30-60 min** | **Worktree: YES**

```
ultrathink

## BEFORE YOU START -- What I Need From You

DECISIONS:
- [ ] Should we create a full Dockerfile for GPU reproduction, or just a minimal
      Dockerfile for CPU-only validation (schema checks, analysis scripts)?
      Recommendation: Start with CPU-only (simpler, no nvidia-docker needed).
      A GPU Dockerfile.gpu can come later as a follow-up.
- [ ] Pin exact versions (==) or minimum versions (>=) in requirements.txt?
      Recommendation: Use >= for broad compatibility in requirements.txt, with a
      separate requirements-lock.txt from `pip freeze` for exact reproducibility.
- [ ] Should docs/REPRODUCING.md cover the full eval pipeline (LLM API keys,
      GPU setup, eval commands), or just the framework installation?
      Recommendation: Full pipeline -- SC26 artifact reviewers need everything.

EXTERNAL DEPS:
- [ ] None -- this session is self-contained (reads code, writes config files)
- [ ] Can run in a worktree (no harness verify, no rodinia source needed)

# Session Goal
Create dependency specifications (requirements.txt, pyproject.toml dependencies),
a minimal Dockerfile, and reproduction documentation so that an SC26 artifact
reviewer can install and run ParBench from scratch.

# Why This Matters
pyproject.toml currently has zero dependency declarations:
    [project]
    name = "parbench"
    version = "0.1.0"
    requires-python = ">=3.12"
No requirements.txt exists. No Dockerfile exists. No docs/REPRODUCING.md exists.
An SC26 reviewer running `pip install -e .` will get zero dependencies installed.
This is a basic reproducibility failure that reviewers will flag immediately.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Python 3.12.3, venv at env_parbench/
- GPU machine: NVIDIA RTX 4070, CUDA 12.3 via HPC SDK 24.3
- nvcc: /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc
- Key third-party Python packages (identified from import scan):
    - anthropic (Anthropic API client -- lazy import in llm_evaluate.py)
    - openai (OpenAI SDK, also used for Groq and Gemini via compatible endpoints -- lazy import)
    - clang (libclang Python bindings for AST augmentation transforms)
    - matplotlib (figure generation in scripts/analysis/)
    - numpy (numeric analysis in scripts/analysis/)
    - pydantic (data models in harness/models.py)
    - pytest (test runner for c_augmentation/test_transforms.py)
    - ruff (Python linter, used by pre-save hook)
- Standard library modules used (no install needed):
    abc, argparse, collections, contextlib, copy, csv, dataclasses, datetime,
    enum, glob, itertools, json, logging, math, os, pathlib, random, re,
    shutil, subprocess, sys, tempfile, time, typing
- LLM providers use lazy imports (import inside function body, not at module top)
  so missing SDK packages only fail when that specific provider is called

# ============================================================
# PART 1: SCAN IMPORTS AND BUILD DEPENDENCY LIST (10 min)
# ============================================================

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Scan all Python imports across the project
# Find every third-party import (not stdlib, not local):
grep -rh "^import \|^from " scripts/ harness/ c_augmentation/ --include="*.py" | \
  sort -u > /tmp/all_imports.txt
# Review /tmp/all_imports.txt -- identify which are third-party vs stdlib vs local

# Step 3: Check installed package versions in the current venv
pip list --format=columns | grep -iE "anthropic|openai|clang|matplotlib|numpy|pydantic|pytest|ruff"
# Record the exact versions for the lock file

# Step 4: Also check for lazy imports in the LLM provider functions
# These are inside llm_evaluate.py function bodies, not at top-level:
grep -n "import anthropic\|import openai\|from openai" \
  scripts/evaluation/llm_evaluate.py
# Expected: anthropic imported around line 486, openai around lines 520/560/602

# ============================================================
# PART 2: CREATE DEPENDENCY FILES (15 min)
# ============================================================

# Step 5: Create requirements.txt with minimum version constraints
# File: /home/samyak/Desktop/parbench_sam/requirements.txt
# Structure it with category comments:
#
#   # Core -- needed for harness build/run/verify + augmentation
#   pydantic>=2.0
#   clang>=18.1
#
#   # Eval -- needed for LLM evaluation pipeline
#   anthropic>=0.40.0
#   openai>=1.50.0
#
#   # Analysis -- needed for results analysis and figure generation
#   matplotlib>=3.9
#   numpy>=1.26
#
#   # Dev -- testing and linting
#   pytest>=8.0
#   ruff>=0.6.0

# Step 6: Update pyproject.toml with [project.dependencies] and optional groups
# Read the current pyproject.toml first. It currently contains:
#   [build-system]
#   requires = ["setuptools>=68"]
#   build-backend = "setuptools.build_meta"
#   [project]
#   name = "parbench"
#   version = "0.1.0"
#   requires-python = ">=3.12"
#   [tool.setuptools.packages.find]
#   where = ["."]
#   include = ["c_augmentation*", "harness*"]
#
# Add dependencies and optional-dependencies sections:
#   [project]
#   dependencies = [
#       "pydantic>=2.0",
#       "clang>=18.1",
#   ]
#   [project.optional-dependencies]
#   eval = ["anthropic>=0.40.0", "openai>=1.50.0"]
#   analysis = ["matplotlib>=3.9", "numpy>=1.26"]
#   dev = ["pytest>=8.0", "ruff>=0.6.0"]
#   all = ["parbench[eval,analysis,dev]"]

# Step 7: Create requirements-lock.txt from current venv
pip freeze > /home/samyak/Desktop/parbench_sam/requirements-lock.txt
# This captures exact versions for bit-for-bit reproducibility

# ============================================================
# PART 3: CREATE DOCKERFILE (10 min)
# ============================================================

# Step 8: Create a minimal CPU-only Dockerfile
# File: /home/samyak/Desktop/parbench_sam/Dockerfile
# Base: python:3.12-slim (no CUDA -- CPU-only validation)
# Purpose: Let reviewers run schema validation, analysis scripts, and unit tests
# without needing a GPU or CUDA installation.
#
# Contents:
#   FROM python:3.12-slim
#   WORKDIR /parbench
#   RUN apt-get update && apt-get install -y --no-install-recommends \
#       gcc g++ make libclang-dev && rm -rf /var/lib/apt/lists/*
#   COPY requirements.txt .
#   RUN pip install --no-cache-dir -r requirements.txt
#   COPY . .
#   RUN pip install -e .
#   # Smoke test: schema validation + unit tests
#   RUN python3 scripts/validate_schema.py --all 2>&1 | tail -5
#   CMD ["python3", "-m", "pytest", "c_augmentation/test_transforms.py", "-v"]
#
# NOTE: This Dockerfile does NOT support GPU eval (no CUDA, no nvcc).
# For GPU eval reproduction, see docs/REPRODUCING.md section "Full GPU Setup".

# ============================================================
# PART 4: CREATE REPRODUCTION DOCUMENTATION (15 min)
# ============================================================

# Step 9: Create docs/REPRODUCING.md
# Structure:
#
#   # Reproducing ParBench Results
#
#   ## Prerequisites
#   - Python 3.12+
#   - For GPU evaluation: NVIDIA GPU with CUDA 12.x, GCC 12+
#   - For CPU-only validation: Docker (optional) or Python venv
#
#   ## Quick Start (CPU-only validation)
#   git clone <repo-url> && cd parbench_sam
#   python3 -m venv env_parbench && source env_parbench/bin/activate
#   pip install -r requirements.txt && pip install -e .
#   python3 scripts/validate_schema.py --all  # ~135 HeCBench errors expected
#   python3 -m pytest c_augmentation/test_transforms.py -v  # 15 tests
#
#   ## Full GPU Setup (for evaluation reproduction)
#   - CUDA 12.3 installation (via NVIDIA HPC SDK 24.3 or standalone)
#   - Set environment variables:
#       export CUDA_DIR=/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda
#       export PATH=$CUDA_DIR/bin:$PATH
#   - Initialize Rodinia submodule: git submodule update --init
#   - Clone XSBench: git clone ... xsbench/xsbench-src/
#   - Set LLM API keys: ANTHROPIC_API_KEY, GROQ_API_KEY, GEMINI_API_KEY
#   - Example eval command:
#       python3 scripts/evaluation/run_eval_batch.py \
#         --suite rodinia --direction cuda-to-omp \
#         --models claude-sonnet-4-6 \
#         --project-root $(pwd) --resume -v
#
#   ## Docker (CPU-only)
#   docker build -t parbench .
#   docker run parbench
#
#   ## Reproducing Paper Results
#   Step 1: Run baseline verification (54 Rodinia + 4 XSBench PASS specs)
#   Step 2: Run LLM evaluation batch per direction (requires API keys + GPU)
#   Step 3: Generate analysis: python3 scripts/evaluation/analyze_eval.py ...
#   Step 4: Generate figures: python3 scripts/analysis/generate_figures.py ...
#   Expected runtime per eval batch: 2-6 hours depending on direction
#
#   ## Environment Used for Paper Results
#   - OS: Ubuntu 22.04 (kernel 6.8.0-40-generic)
#   - GPU: NVIDIA GeForce RTX 4070
#   - CUDA: 12.3 (via NVIDIA HPC SDK 24.3)
#   - GCC: 12.3.0
#   - Python: 3.12.3
#   - Package versions: see requirements-lock.txt

# ============================================================
# PART 5: VERIFY AND COMMIT
# ============================================================

# Step 10: Verify requirements.txt is installable
python3 -m pip install --dry-run -r requirements.txt
# Should resolve all dependencies without errors

# Step 11: Verify pyproject.toml is valid TOML
python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb')))"
# Should print the parsed TOML structure without errors

# Step 12: Run schema validation to confirm nothing is broken
python3 scripts/validate_schema.py --all
# Expected: same ~135 HeCBench + 15 phantom errors, no new errors

# Step 13: Run unit tests to confirm nothing is broken
python3 -m pytest c_augmentation/test_transforms.py -v
# Expected: 15 tests, all PASS

# Step 14: Commit
git add requirements.txt requirements-lock.txt pyproject.toml
git add Dockerfile docs/REPRODUCING.md

# Commit message:
# "S-DEPS: Add dependency specifications + reproduction documentation
#
# - requirements.txt with categorized dependencies (core/eval/analysis/dev)
# - requirements-lock.txt with exact pinned versions from working venv
# - pyproject.toml updated with [project.dependencies] and optional-dependencies
# - Minimal CPU-only Dockerfile for reviewer validation
# - docs/REPRODUCING.md with full reproduction instructions for SC26 artifact review"
```

### Acceptance Criteria
- [ ] `requirements.txt` exists with all third-party Python dependencies
- [ ] `requirements-lock.txt` exists with `pip freeze` output from working venv
- [ ] `pyproject.toml` has `[project.dependencies]` and `[project.optional-dependencies]`
- [ ] `pip install --dry-run -r requirements.txt` succeeds without errors
- [ ] `Dockerfile` exists and documents its CPU-only scope
- [ ] `docs/REPRODUCING.md` exists with Quick Start, Full GPU Setup, Docker, and Reproducing Paper Results sections
- [ ] `validate_schema.py --all` shows no new errors
- [ ] `pytest c_augmentation/test_transforms.py` shows 15 PASS

### Agent Delegation
- Use `verify-app` agent after creating `requirements.txt` and `pyproject.toml` to confirm no schema or import regressions
- This session is simple enough that no other agents are needed
- If running in a worktree: `env_parbench/` is available but `rodinia/rodinia-src/` will be empty (irrelevant for this session)

### Parallel Group Assignment
- **Group 1** -- runs immediately, no dependencies
- Safe to run concurrently with S-VERIFY, S-TAXONOMY, S-ANALYSIS, W-S16
- Fully worktree-safe (no GPU, no rodinia source needed)

### Estimated Duration
- **Part 1 (Import scan):** 10 min
- **Part 2 (Dependency files):** 15 min
- **Part 3 (Dockerfile):** 10 min
- **Part 4 (REPRODUCING.md):** 15 min
- **Part 5 (Verify + commit):** 10 min
- **Total:** ~60 min

---

## SESSION S-TIMING -- Enable CPU Timing for Baseline + PASS Evaluation Results

**Priority: P2 -- MEDIUM** | **Parallel Group 3** | **Lane: GPU** | **Duration: 4-6 hours** | **Worktree: NO**

```
ultrathink

## BEFORE YOU START -- What I Need From You

DECISIONS:
- [x] S-VERIFY COMPLETED (2026-03-27). 105/468 are TRUE_PASS with stdout_pattern+exit_code
      conjunction. All FALSE_PASS specs have been fixed. CPU timing should run on the 105
      verified PASS results only.
- [ ] The existing --use-cpu-timing flag in run_eval_batch.py already exists and
      works end-to-end. The flag passes use_cpu_timing=True to evaluate_translation()
      (llm_evaluate.py:850) which passes measure_cpu_time=True to run_spec()
      (runner.py:60). This infrastructure is ALREADY BUILT. The issue is simply
      that no eval batch was ever run with this flag enabled. Confirm: should we
      re-run all TRUE_PASS eval results with --use-cpu-timing, or just populate
      baseline timing for the reference implementations?
- [ ] CPU time (user+system via /usr/bin/time -v) includes ALL process time,
      not just the parallel kernel. For OpenMP, this sums all threads' CPU time
      (so cpu_time > wall_time for multi-threaded programs). For CUDA, it includes
      host-side setup + data transfer. This is BETTER than wall-clock but WORSE
      than kernel-time profiling (nsys/ncu). Confirm: CPU time is acceptable for
      the paper, or do we need nsys integration (that would be SESSION 6.5, a
      much larger and currently deferred task)?

EXTERNAL DEPS:
- [ ] GPU machine available (all timing requires actual execution)
- [x] S-VERIFY COMPLETED (2026-03-27) — 105 TRUE_PASS results identified
- [ ] /usr/bin/time must be GNU time (not shell builtin). Verify with:
      /usr/bin/time --version  # should print "GNU time 1.x"
- [ ] No concurrent GPU eval sessions (S10, S10b) running -- timing needs
      exclusive GPU access for consistent measurements

# Session Goal
Populate CPU timing data (user+system time via GNU /usr/bin/time -v) for:
1. All 58 baseline PASS specs (54 Rodinia + 4 XSBench) -- baseline_cpu_time
2. All TRUE_PASS evaluation results -- translated_cpu_time
This gives the paper wall-clock-independent timing data for performance comparison.

# Why This Matters
All 468 eval result files have translated_cpu_time_seconds = null and
translated_kernel_time_seconds = null. The baseline_results in specs have
wall_time (duration_seconds) but no cpu_time. The paper cannot make any
performance claims without timing data. Even CPU time (not kernel time) is
better than nothing -- it removes OS scheduling noise, I/O variance, and
memory allocation jitter from the measurement.

The infrastructure already exists and is fully implemented:
- runner.py:run_spec() accepts measure_cpu_time=True (line 60)
- runner.py wraps command with /usr/bin/time -v -o <tmpfile> (lines 122-131)
- runner.py parses User time + System time via _parse_gnu_time() (lines 19-51)
- runner.py stores result in RunResult.cpu_time_seconds (line 180)
- llm_evaluate.py:evaluate_translation() accepts use_cpu_timing=True (line 850)
- llm_evaluate.py passes measure_cpu_time=use_cpu_timing to run_spec (line 1099)
- run_eval_batch.py accepts --use-cpu-timing flag (line 374)
- run_eval_batch.py passes use_cpu_timing to evaluate_translation (line 165)

No code changes are needed. This session only USES the existing infrastructure.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- GNU time: /usr/bin/time -v (parses "User time (seconds)" + "System time (seconds)")
- runner.py already has the full measure_cpu_time pipeline implemented
- 58 baseline PASS specs (54 Rodinia + 4 XSBench)
- 105 PASS eval results across 3 models (post S-VERIFY, 2026-03-27)
- Current baseline_results in specs have only wall_time (duration_seconds field)

# ============================================================
# PART 1: BASELINE CPU TIMING (1-2 hours)
# ============================================================

# Step 1: Activate venv and verify GNU time is available
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam
/usr/bin/time --version
# Expected: "GNU time 1.x" -- if this fails, install: sudo apt-get install time

# Step 2: Test CPU timing on 3 diverse specs to confirm the pipeline works
# Pick specs with different runtime characteristics:
#   - rodinia-bfs-omp (graph traversal, short runtime, few threads)
#   - rodinia-hotspot3d-omp (stencil, medium runtime, data-parallel)
#   - xsbench-xsbench-cuda (Monte Carlo, GPU kernel, host+device time)
python3 -c "
import json, sys
sys.path.insert(0, '.')
from harness.spec_loader import load_spec
from harness.runner import run_spec
from pathlib import Path

project_root = Path('/home/samyak/Desktop/parbench_sam')
for spec_file in ['specs/rodinia-bfs-omp.json',
                  'specs/rodinia-hotspot3d-omp.json',
                  'specs/xsbench-xsbench-cuda.json']:
    spec = load_spec(str(project_root / spec_file))
    result = run_spec(spec, project_root, 'correctness',
                      verbose=True, measure_cpu_time=True)
    print(f'{spec_file}:')
    print(f'  status={result.status}')
    print(f'  wall_time={result.duration_seconds}s')
    print(f'  cpu_time={result.cpu_time_seconds}s')
    print(f'  exit_code={result.exit_code}')
    print()
"
# Verify: cpu_time_seconds is a positive float, not None
# Verify: cpu_time_seconds differs from duration_seconds
# For OMP specs: cpu_time > wall_time is expected (sums all thread CPU time)
# For CUDA specs: cpu_time includes host+device; compare with wall_time

# Step 3: Write a baseline timing collection script
# File: scripts/baselines/collect_cpu_timing.py
# Purpose: Run all 58 PASS specs with measure_cpu_time=True, 3 iterations each,
#          and record median CPU time per spec.
#
# The script should:
#   1. Accept --project-root, --iterations (default 3), --config (default correctness)
#   2. Load each spec from specs/rodinia-*.json and specs/xsbench-*.json
#   3. Skip KNOWN_FAIL specs (hardcoded list from known-issues.md):
#      kmeans-cuda, kmeans-opencl, nn-opencl, hybridsort-cuda,
#      mummergpu-cuda, mummergpu-omp
#   4. For each spec: run N iterations with measure_cpu_time=True
#   5. Record: spec_id, api, wall_times[], cpu_times[], median_wall, median_cpu
#   6. Output JSON to results/baselines/cpu_timing_baselines.json
#   7. Output human-readable table to results/baselines/cpu_timing_baselines.md
#   8. Print summary: total specs timed, any failures, min/max/median CPU times
#
# Use the CORRECTNESS config (smaller input sizes) for timing.
# Performance config has larger inputs but not all specs define it.

# Step 4: Create the results/baselines/ directory if needed
mkdir -p results/baselines

# Step 5: Run the baseline timing collection (use tmux for SSH disconnect safety)
tmux new-session -d -s baseline_timing \
  "cd /home/samyak/Desktop/parbench_sam && \
   source env_parbench/bin/activate && \
   python3 scripts/baselines/collect_cpu_timing.py \
     --project-root /home/samyak/Desktop/parbench_sam \
     --iterations 3 -v \
   2>&1 | tee results/baselines/cpu_timing.log"
echo "Baseline timing launched. Monitor: tmux attach -t baseline_timing"

# Step 6: When complete, verify results
# Read results/baselines/cpu_timing_baselines.json and check:
#   - All 58 PASS specs have cpu_time data (no None values)
#   - Variance is low across 3 iterations (coefficient of variation < 0.2)
#   - For OMP specs: cpu_time > wall_time (expected -- sums all thread time)
#   - For CUDA specs: cpu_time includes host overhead
#   - For single-threaded specs: cpu_time <= wall_time
python3 -c "
import json
data = json.loads(open('results/baselines/cpu_timing_baselines.json').read())
total = len(data)
has_cpu = sum(1 for d in data if d.get('median_cpu') is not None)
print(f'Total specs: {total}, with CPU time: {has_cpu}')
for d in data:
    if d.get('median_cpu') is None:
        print(f'  MISSING: {d[\"spec_id\"]}')
"

# ============================================================
# PART 2: EVAL RESULT CPU TIMING (2-4 hours)
# ============================================================
# NOTE: Only run this part AFTER S-VERIFY confirms which PASS results are TRUE_PASS.
# If S-VERIFY has not been run yet, SKIP Part 2 entirely and commit Part 1.

# Step 7: Re-run TRUE_PASS eval results with CPU timing
# This requires extracting translated code from result JSONs and re-running.
# The approach mirrors llm_evaluate.py's build/run/verify cycle but:
#   - Reads translated files from result JSON instead of calling the LLM
#   - Runs with measure_cpu_time=True
#   - Records median of 3 iterations
#
# If S-VERIFY's reverify_pass_results.py already exists, ADD a --capture-timing
# flag to it that enables measure_cpu_time during re-verification runs.
# Otherwise, write scripts/evaluation/collect_eval_timing.py with this flow:
#
# For each TRUE_PASS result:
#   1. Extract translated_files from the result JSON
#   2. Load the target spec
#   3. Write translated files to target working directory
#   4. Build the target spec (build_spec from harness.builder)
#   5. Run correctness config with measure_cpu_time=True, 3 iterations
#   6. Record median cpu_time
#   7. Update the result JSON: translated_cpu_time_seconds = median
#   8. Restore original files in the target working directory
#
# CRITICAL: Back up and restore files (same pattern as llm_evaluate.py).
# Only ONE re-run can execute at a time (no file locking in rodinia-src/).

# Step 8: Run eval timing collection (use tmux)
# Only proceed if S-VERIFY is complete and reverification_audit.json exists:
tmux new-session -d -s eval_timing \
  "cd /home/samyak/Desktop/parbench_sam && \
   source env_parbench/bin/activate && \
   python3 scripts/evaluation/reverify_pass_results.py \
     --project-root /home/samyak/Desktop/parbench_sam \
     --capture-timing --iterations 3 -v \
   2>&1 | tee results/evaluation/eval_cpu_timing.log"
echo "Eval timing launched. Monitor: tmux attach -t eval_timing"

# ============================================================
# PART 3: ANALYSIS AND COMMIT
# ============================================================

# Step 9: Analyze timing data
# Write a timing analysis that:
#   1. Loads baseline CPU times from results/baselines/cpu_timing_baselines.json
#   2. Loads eval CPU times from updated result JSONs
#   3. For each TRUE_PASS result: compute speedup_ratio = baseline_cpu / translated_cpu
#   4. Report per-model, per-kernel, per-direction speedup statistics:
#      - Median speedup across all TRUE_PASS results
#      - Per-model: which model produces faster translations?
#      - Per-kernel: which kernels preserve performance best?
#      - Per-direction: is cuda-to-omp or omp-to-cuda better for performance?
#   5. Compare CPU time speedups with wall-clock speedups (how different?)
#   6. Output to results/evaluation/cpu_timing_analysis.md
#
# Key questions for the paper:
#   - What is the median speedup ratio across all TRUE_PASS results?
#   - Do translated OMP programs run slower than reference OMP? (likely: slightly)
#   - Do translated CUDA programs run slower than reference CUDA? (likely: yes)
#   - Is there a correlation between translation complexity and performance loss?
#   - Which model produces the most performant translations?

# Step 10: Regenerate eval_summary with timing data included
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps

# Step 11: Commit
git add results/baselines/cpu_timing_baselines.json
git add results/baselines/cpu_timing_baselines.md
git add scripts/baselines/collect_cpu_timing.py
git add results/evaluation/cpu_timing_analysis.md
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git add visualizations/eval_results_data.js
# If eval result JSONs were updated with cpu_time:
git add results/evaluation/*/

# Commit message:
# "S-TIMING: Populate CPU timing data for baselines + PASS eval results
#
# - Baseline CPU timing: 58 specs x 3 iterations, median recorded
# - Eval CPU timing: N TRUE_PASS results with translated_cpu_time_seconds populated
# - Analysis: median speedup ratio = X.Xx across all TRUE_PASS results
# - Uses /usr/bin/time -v (user+system) via existing runner.py infrastructure
# - No code changes to runner.py or llm_evaluate.py -- used existing --use-cpu-timing flag"
```

### Acceptance Criteria
- [ ] `/usr/bin/time --version` confirms GNU time is available
- [ ] 3 test specs produce non-null `cpu_time_seconds` values in Step 2
- [ ] `results/baselines/cpu_timing_baselines.json` has data for all 58 PASS specs
- [ ] Each spec has 3 iterations with low variance (coefficient of variation < 0.2)
- [ ] `results/baselines/cpu_timing_baselines.md` has human-readable timing table
- [ ] (After S-VERIFY) At least 5 TRUE_PASS eval results have `cpu_time` populated
- [ ] `results/evaluation/cpu_timing_analysis.md` has speedup ratio analysis
- [ ] `eval_summary` regenerated with timing data included

### Agent Delegation
- Use `explorer` agent to read `runner.py` and `llm_evaluate.py` timing code paths
  before writing the baseline collection script -- confirm the pipeline end-to-end
- Use `verify-app` agent after any changes to confirm spec integrity
- Use `rodinia-verifier` agent to confirm specs still PASS after timing runs
- Do NOT modify `runner.py` or `llm_evaluate.py` -- the infrastructure already works.
  This session only USES the existing `--use-cpu-timing` / `measure_cpu_time` plumbing.

### Parallel Group Assignment
- **Group 3** -- runs after S10 completes (Day 13-15)
- Requires exclusive GPU access (no concurrent eval batches)
- Depends on S-VERIFY for Part 2 (eval re-timing); Part 1 (baselines) is independent
- NOT worktree-safe (requires GPU + rodinia source for builds and runs)

### Estimated Duration
- **Part 1 (Baseline timing):** 1-2 hours (58 specs x 3 iterations)
- **Part 2 (Eval timing):** 2-4 hours (up to 169 results x 3 iterations)
- **Part 3 (Analysis + commit):** 30 min
- **Total:** ~4-6 hours

---

## PAPER WRITING SESSION PROMPTS

The paper draft (`docs/paper/paper_draft.md`) has all 8 sections drafted (S1-S8, ~11500 words, merged 2026-03-25 from W-S12-PARTIAL). However:
- S1 (Introduction) and S2 (Related Work) need revision with S7/S8/S9 data (total tasks now 468 post S-VERIFY, direction asymmetry, augmentation proof)
- S6 (Results) needs updating with omp-to-cuda direction asymmetry, XSBench cross-direction data, and any S-VERIFY corrections
- S7 (Discussion) and S8 (Conclusion) need revision once S6 is finalized
- No bibliography file exists (`docs/paper/references.bib` needed for W-S17 LaTeX conversion)
- Figures need regeneration with complete data (W-S14 used L0 only; S7/S8/S9 data now available)

---

## SESSION S12 — Paper Draft: Introduction + Related Work Revision (S1-S2)

**Priority: P1 — HIGH** | **Group 2** | **Lane: Supervised** | **Duration: 1 day** | **Worktree: YES**

```
ultrathink

## CONTEXT

You are revising the Introduction (S1) and Related Work (S2) sections of the ParBench
SC26 paper. These sections already exist in docs/paper/paper_draft.md (drafted in
W-S12-PARTIAL, merged 2026-03-25) but were written with L0 data only. Now we have:
- L0-L4 augmentation data for 3 models (S7, 348 result files)
- omp-to-cuda direction data for 3 models (S9, 48 result files)
- XSBench 12-direction data for 3 models (S8, 180 result files)
- Total: 468 evaluated translation tasks across 3 models (105/468 = 22.44% PASS, post S-VERIFY)
- Cross-direction asymmetry: cuda-to-omp is 18.8pp easier than omp-to-cuda (aggregate)

If running in a worktree: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY in worktrees — that is expected and fine.
This session does NOT need Rodinia source. It reads results/ and writes docs/paper/.

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] The Introduction should cite "468 evaluated tasks" (post S-VERIFY verified total).
      eval_summary.json excludes 36 kmeans/mummergpu results (KNOWN_FAIL source specs).
      Recommendation: use 468 in Abstract/Intro, clarify scope per-section in Results.
- [ ] Paraval (ParEval-Repo) reading: Has Samyak read the paper? If yes, provide any
      specific differentiators to emphasize. If not, proceed with existing S2 positioning
      (which is already strong — DOI 10.1145/3754598.3754669 cited).
- [ ] Should the Introduction preview the direction asymmetry finding (18.8pp gap)?
      Currently it previews 4 findings; adding a 5th would strengthen but lengthen S1.

DATA SOURCES (read ALL before writing):
1. docs/paper/paper_draft.md            — existing S1 + S2 text to revise
2. results/evaluation/eval_summary.json — authoritative aggregate numbers (468 tasks, post S-VERIFY)
3. results/evaluation/s9_direction_comparison.txt — direction asymmetry data
4. docs/paper/paper_sections_3_4_5.md   — W-S12-PARTIAL original draft (for context)

### SESSION GOAL

Revise S1 (Introduction) and S2 (Related Work) to reflect the complete evaluation
dataset (468 tasks, 3 models, 12 directions, L0-L4 augmentation, 22.44% overall PASS)
while maintaining academic tone and SC26 quality. S1 and S2 are the first thing
reviewers read — they must be airtight.

## WHAT TO REVISE IN S1 (Introduction)

S1 currently has 4 subsections: 1.1 Motivation, 1.2 The Gap, 1.3 Contributions, 1.4 Key
Findings Preview. The structure is sound. Specific changes needed:

1. Update all aggregate numbers:
   - "452 evaluated tasks" -> 500 (if decision above approves)
   - Verify "17 Rodinia kernels" still correct for primary eval (it is)
   - Add "12 translation directions" to the scope (currently says "six")
   - Update pass rate: overall 105/468 = 22.44% (post S-VERIFY with stdout_pattern verification)
   - Per-model: claude-sonnet-4-6 51.92%, gemini-2.5-flash-lite 7.05%, groq 8.33%

2. Add direction asymmetry to Key Findings Preview (S1.4):
   - "CUDA-to-OpenMP is 18.8 percentage points easier than OpenMP-to-CUDA in aggregate"
   - "cuda-to-omp has 11 C2O_ONLY cells vs 2 O2C_ONLY cells across 48 kernel x model pairs"

3. Strengthen the training-data contamination argument (S1.2):
   - The augmentation results now PROVE this is a real concern: Gemini degrades 75% at L4
   - This is the paper's strongest methodological contribution — make it sharper

4. Verify every \cite{} placeholder has a matching entry in S2
5. Target: ~1200 words for S1 (currently ~1100 — small expansion is fine)

## WHAT TO REVISE IN S2 (Related Work)

S2 currently has 6 subsections covering: Three-Granularity Landscape, Code Synthesis,
Parallel Code Evaluation, Repository-Level Translation, LLM-for-HPC, ParaCodex. The
structure and positioning are strong. Specific changes:

1. Verify Table 1 numbers match eval_summary.json:
   - "184 specs, 3 suites, 12 directions, 3 models" — verify directions=12, models=3
   - "51.92% PASS (Claude Sonnet 4.6)" — overall rate post S-VERIFY (was 70.6% for L0 cuda-to-omp only)

2. Check if any new related work should be added:
   - LASSI (already cited in S2.4)
   - CodeRosetta (already cited in S2.2)
   - RepoTransBench (already cited in S2.4)
   - AlphaTrans (already cited in S2.4)
   If Samyak has read new papers since 2026-03-25, add them.

3. Ensure ParEval-Repo positioning is precise:
   - Their 0% finding on >133 SLoC is THE motivating result for ParBench
   - XSBench achieves 0% in ParEval-Repo but non-zero in ParBench (confirmed by S8 data)
   - This comparison must be rock-solid for reviewers

4. Target: ~800 words for S2 (currently ~750 — fine as is, expand only if needed)

### PAPER-DRAFTER AGENT USAGE (Opus model)

Invoke: "Use the paper-drafter agent to revise S1 Introduction"
Agent MUST pre-read these files:
  1. docs/paper/paper_draft.md               — current text to revise
  2. results/evaluation/eval_summary.json     — authoritative 468-task numbers (post S-VERIFY)
  3. results/evaluation/s9_direction_comparison.txt  — direction asymmetry
Agent writing rules (non-negotiable):
  1. Data-backed claims only — cite specific numbers from results files
  2. \cite{placeholder} for all references
  3. No fabricated numbers — if data doesn't exist, write "TBD (pending Session N)"
  4. Preserve existing \cite{} keys for bibliography compatibility
  5. Every changed number must be noted in the Data Verification Notes at bottom of file

## STEPS

# Step 1: Read the current paper draft fully — focus on S1, S2, and Abstract
# Step 2: Read eval_summary.json for authoritative aggregate numbers
# Step 3: Read s9_direction_comparison.txt for direction asymmetry data
# Step 4: Resolve the DECISIONS above with Samyak
# Step 5: Use paper-drafter agent to revise S1 (Introduction)
# Step 6: Use paper-drafter agent to revise S2 (Related Work)
# Step 7: Update the Abstract to reflect any changed numbers
# Step 8: Update Data Verification Notes at bottom of paper_draft.md
# Step 9: Verify: grep for all numbers in S1/S2 and cross-check against data files
# Step 10: Git commit and push
# Message: "SC26 paper: revise S1-S2 with 468-task data, direction asymmetry, augmentation proof"

## ACCEPTANCE CRITERIA

- [ ] All aggregate numbers in S1 match eval_summary.json
- [ ] Direction asymmetry finding added to S1.4 Key Findings (18.8pp is L0-Rodinia-only; full-dataset gap is ~10pp: cuda-to-omp 24.31% vs omp-to-cuda 14.29%)
- [ ] Training-data contamination argument strengthened with L4 evidence
- [ ] Table 1 in S2 updated if direction count changed (6 -> 12)
- [ ] Every \cite{} in S1-S2 corresponds to a subsection in S2
- [ ] Abstract updated to match revised S1 numbers
- [ ] Data Verification Notes updated with new/changed values
- [ ] No fabricated numbers — every stat traceable to a results file
- [ ] Academic tone maintained; no marketing language
- [ ] Total word count for S1+S2: ~2000 words (10% tolerance)
```

### Parallel Safety

- Writes to: `docs/paper/paper_draft.md` (S1, S2, Abstract sections only)
- Reads from: `results/evaluation/eval_summary.json`, `results/evaluation/s9_direction_comparison.txt`
- Safe to run concurrently with S-VERIFY, S-TAXONOMY, S-ANALYSIS, S10, S-BIB, S-FIGURES
- NOT safe to run concurrently with S13 (both write to paper_draft.md)

### Estimated Duration
- **Read + orient:** 30 min
- **S1 revision:** 2 hours (decision gates + writing)
- **S2 revision:** 1.5 hours
- **Abstract update + verification:** 1 hour
- **Total:** ~5 hours (1 working day with review breaks)

---

## SESSION S13 — Paper Draft: Results + Discussion + Conclusion Revision (S6-S8) [COMPLETED 2026-03-27]

**Priority: P1 — HIGH** | **Group 3** | **Lane: Supervised** | **Duration: 1 day** | **Worktree: YES**

```
ultrathink

## CONTEXT

You are revising the Results (S6), Discussion (S7), and Conclusion (S8) sections of the
ParBench SC26 paper. These sections already exist in docs/paper/paper_draft.md but were
drafted with partial data. S6 now needs:
- S9 omp-to-cuda Rodinia data (48 tasks: 16 kernels x 3 models)
- S-VERIFY corrections (if available — re-verified PASS/FAIL with stdout checking)
- S-TAXONOMY error classification (if available — systematic failure categorization)
- S-ANALYSIS token/SLoC/self-repair statistics (if available)
- S10 cuda-to-opencl Rodinia data (if available — 51 tasks)

S7 and S8 must be updated to reflect any changes in S6.

If running in a worktree: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY in worktrees — that is expected and fine.

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] S-VERIFY status: COMPLETED (2026-03-27). Verification upgraded to stdout_pattern+exit_code
      conjunction. All 58 non-KNOWN_FAIL specs verified TRUE PASS. Eval results: 105/468 PASS (22.44%).
      S6 tables MUST use post-S-VERIFY numbers.
- [ ] S10 status: Is cuda-to-opencl data available?
      If YES: Add S6.6 subsection with cuda-to-opencl results alongside XSBench.
      If NO: Keep S6.6 as-is with XSBench cross-direction only + "Rodinia cross-direction
      evaluation is ongoing" note.
- [ ] Self-repair data: Should self-repair be a full subsection (currently S6.4) or
      demoted to a paragraph within S6.1? Current treatment is appropriate if the data
      supports it.
- [ ] Speedup/performance: The paper is correctness-only. S7.4 already states this.
      Confirm this is still the approach (no S-TIMING data expected).

DATA SOURCES (read ALL before writing):

Primary (MUST read):
1. docs/paper/paper_draft.md                           — existing S6-S8 text to revise
2. results/evaluation/eval_summary.json                — authoritative 468-task aggregate (post S-VERIFY)
3. results/evaluation/s9_direction_comparison.txt      — direction asymmetry per-kernel

Secondary (read if available):
4. results/analysis/error_taxonomy.md or .json         — from S-TAXONOMY (if exists)
5. results/analysis/token_analysis.md or .json         — from S-ANALYSIS (if exists)
6. results/analysis/selfrepair_analysis.md or .json    — from S-ANALYSIS (if exists)
7. results/evaluation/ per-model directories           — individual result JSONs for spot-checks

### SESSION GOAL

Revise S6 (Results), S7 (Discussion), and S8 (Conclusion) to incorporate all available
data from S7-S10 eval sessions. S6 is the most data-heavy section of the paper and must
be airtight — every number must trace to a results file.

## WHAT TO REVISE IN S6 (Results)

S6 currently has 6 subsections: 6.1 Overall Pass Rates, 6.2 Failure Taxonomy,
6.3 Per-Kernel Analysis, 6.4 Self-Repair, 6.5 Augmentation Robustness, 6.6 Cross-Direction.

### S6.1 Overall Pass Rates

Current Table 7 shows overall pass rates for 3 models (468 evaluated tasks, 105 PASS = 22.44%).
Changes needed:
- Verify all numbers still match eval_summary.json (they should unless S-VERIFY changed them)
- If S-VERIFY changed any PASS/FAIL outcomes, update Table 7 + all derived numbers
- Consider adding a second table: aggregate by direction (cuda-to-omp, omp-to-cuda, etc.)

### S6.2 Failure Taxonomy

Current: 180 BUILD_FAIL, 89 RUN_FAIL, 49 EXTRACTION_FAIL, 45 VERIFY_FAIL out of 363 total failures (468 tasks).
Changes needed:
- If S-TAXONOMY produced a detailed classification, integrate the BUILD_FAIL subcategories:
  (retained CUDA calls, missing pragma, wrong types, missing headers, etc.)
- If not, the current high-level taxonomy is already good
- Expand to include omp-to-cuda failure distribution from S9 data

### S6.3 Per-Kernel Analysis

Current Table 8 shows full kernel x model matrix for cuda-to-omp L0.
Changes needed:
- Add omp-to-cuda results as a companion table or combined heatmap
- Update tier analysis with bidirectional data (which kernels pass in both directions?)
- Reference s9_direction_comparison.txt: 9 BOTH_PASS, 11 C2O_ONLY, 2 O2C_ONLY, 26 BOTH_FAIL

### S6.5 Augmentation Robustness

Current Table 10 is correct and well-written. Verify numbers still match.
Only change: update "452 evaluated tasks" if the total has changed.

### S6.6 Cross-Direction and Extended Suite Results

Currently covers XSBench cross-direction (12 dirs) with selected directional results.
Changes needed:
- ADD Rodinia omp-to-cuda results subsection:
  * Aggregate: 11/48 PASS (22.9%) vs cuda-to-omp 20/48 PASS (41.7%) [L0, 3 models only]
  * Per-model: Claude 7/16, Gemini 1/16, Groq 3/16
  * Direction asymmetry: 18.8pp aggregate gap
  * Per-kernel direction asymmetry table from s9_direction_comparison.txt
- If S10 cuda-to-opencl data is available, add that too
- Remove "Rodinia cross-direction evaluation is ongoing" if S9 data replaces it

## WHAT TO REVISE IN S7 (Discussion)

S7 has 6 subsections: 7.1 Kernel-Centric Advantage, 7.2 BUILD_FAIL Bottleneck,
7.3 Model Capability Spread, 7.4 Threats to Validity, 7.5 Augmentation Tier,
7.6 Implications.

Changes needed:
- Add a new subsection S7.X on direction asymmetry interpretation:
  * Why is cuda-to-omp easier than omp-to-cuda?
  * Hypothesis: CUDA provides explicit thread decomposition that maps naturally to OMP
    loop parallelism. OMP-to-CUDA requires INTRODUCING thread-block structure.
  * 11 C2O_ONLY vs 2 O2C_ONLY: strong asymmetry signal
- S7.4 Threats to Validity: update "Single translation direction emphasis" paragraph
  if Rodinia omp-to-cuda data now exists (it does from S9)
- S7.4: if S-VERIFY has not been done, the exit-code-only paragraph stays as-is

## WHAT TO REVISE IN S8 (Conclusion)

S8 has 2 subsections: 8.1 Summary, 8.2 Future Work.

Changes needed:
- S8.1: update aggregate numbers to match revised S6
- S8.1: add direction asymmetry as a finding (one sentence in the summary)
- S8.2: update "Rodinia cross-direction evaluation is ongoing" if S9 completes it
- S8.2: keep HeCBench, performance evaluation, agentic translation as future work

### PAPER-DRAFTER AGENT USAGE (Opus model)

Invoke for each section sequentially:
1. "Use the paper-drafter agent to revise S6 Results"
2. "Use the paper-drafter agent to revise S7 Discussion"
3. "Use the paper-drafter agent to revise S8 Conclusion"
4. "Use the paper-drafter agent to update the Abstract"

Agent MUST pre-read:
  1. docs/paper/paper_draft.md               — current text
  2. results/evaluation/eval_summary.json     — 500-task aggregate
  3. results/evaluation/s9_direction_comparison.txt  — direction asymmetry
  4. Any S-TAXONOMY, S-ANALYSIS output files that exist

## STEPS

# Step 1: Read current paper_draft.md S6-S8 fully
# Step 2: Read eval_summary.json — verify all S6 numbers still match
# Step 3: Read s9_direction_comparison.txt for Rodinia direction data
# Step 4: Check if S-TAXONOMY, S-ANALYSIS, S-VERIFY output files exist:
#   ls results/analysis/error_taxonomy* results/analysis/token_analysis* \
#      results/analysis/selfrepair_analysis* 2>/dev/null
# Step 5: Resolve DECISIONS above with Samyak
# Step 6: Use paper-drafter agent for S6 revision (biggest section — most changes)
# Step 7: Use paper-drafter agent for S7 revision (add direction asymmetry subsection)
# Step 8: Use paper-drafter agent for S8 revision (update numbers + future work)
# Step 9: Use paper-drafter agent to update Abstract
# Step 10: Update Data Verification Notes at bottom of paper_draft.md
# Step 11: Verify: every number in S6 tables matches eval_summary.json
# Step 12: Git commit and push
# Message: "SC26 paper: revise S6-S8 with omp-to-cuda direction asymmetry + complete data"

## ACCEPTANCE CRITERIA

- [ ] Every number in Table 7 (S6.1) matches eval_summary.json
- [ ] Rodinia omp-to-cuda results added to S6.6 with per-model and per-kernel data
- [ ] Direction asymmetry discussed in both S6.6 and new S7.X subsection (18.8pp is L0-Rodinia-only; full-dataset gap is ~10pp: 24.31% vs 14.29%)
- [ ] At least 3 table references and 3 figure references in S6
- [ ] S7.4 Threats to Validity honestly addresses all known weaknesses
- [ ] S8 updated with revised aggregate numbers
- [ ] Abstract consistent with revised S6-S8
- [ ] Data Verification Notes updated with every new/changed value
- [ ] Total word count for S6+S7+S8: ~4500 words (10% tolerance, currently ~4200)
- [ ] No fabricated numbers
```

### Dependencies

- **Hard:** S12 must complete first (S1-S2 establish framing that S6-S8 must be consistent with)
- **Hard:** S9 omp-to-cuda data must be available (it is — 48 result files exist)
- **Soft:** S-VERIFY, S-TAXONOMY, S-ANALYSIS improve the Results section if available
- **Soft:** S10 cuda-to-opencl data enriches S6.6 if available

### Parallel Safety

- Writes to: `docs/paper/paper_draft.md` (S6, S7, S8, Abstract sections only)
- Reads from: `results/evaluation/eval_summary.json`, `results/evaluation/s9_direction_comparison.txt`,
  `results/analysis/*` (if available)
- NOT safe to run concurrently with S12 (both write to paper_draft.md)
- Safe to run concurrently with S-FIGURES, S-BIB, S10, S10b, S-TIMING

### Estimated Duration
- **Read + orient:** 30 min
- **S6 revision:** 3 hours (most data-heavy, multiple tables)
- **S7 revision:** 1.5 hours (add direction asymmetry subsection)
- **S8 revision + Abstract:** 1 hour
- **Data verification pass:** 30 min
- **Total:** ~6-7 hours (1 working day)

---

## SESSION S-FIGURES — Regenerate Publication Figures with Complete Data [COMPLETED 2026-03-27]

**Priority: P2 — MEDIUM** | **Group 2** | **Lane: Any** | **Duration: 4 hours** | **Worktree: YES**

```
ultrathink

## CONTEXT

You are regenerating the SC26 paper figures with the complete evaluation dataset.
W-S14 (completed 2026-03-24) generated F2-F6 from L0 cuda-to-omp data only.
Now we have:
- L0-L4 augmentation data for 3 models (S7: 348 result files)
- omp-to-cuda direction data for 3 models (S9: 48 result files)
- XSBench 12-direction data for 3 models (S8: 180 result files)
- Existing figure generation script: scripts/evaluation/generate_paper_figures.py
- Existing figures: docs/paper/figures/ (F2-F6 PDFs and PNGs, T2 LaTeX table)
- Existing LaTeX table: docs/paper/figures/t2_model_comparison.tex

If running in a worktree: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY in worktrees — that is expected and fine.
This session reads results/evaluation/ and writes to docs/paper/figures/ only.

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Color palette: The SC26 outfit-derived palette was specified in an earlier
      session. Check memory file feedback_color_palette.md for the exact hex values.
      If not available, use: deep navy (#1B2A4A), teal (#2A9D8F), coral (#E76F51),
      gold (#E9C46A), light grey (#F4F1DE). These are inspired by the SC26 color scheme.
      DO NOT use Okabe-Ito.
- [ ] Figure F1 (system architecture): This has never been created. It is referenced
      in the paper as [FIGURE 1: System architecture diagram...]. Should this session
      create it, or defer to a manual diagram tool (draw.io, Figma)?
      Recommendation: Create a matplotlib/tikz schematic. It doesn't need to be
      photorealistic — a clean block diagram showing the 4 components is sufficient.
- [ ] S-VERIFY status: If verification has been upgraded, some PASS/FAIL outcomes may
      have changed. Check eval_summary.json timestamp to confirm data is current.

DATA SOURCES:
1. results/evaluation/eval_summary.json            — authoritative aggregate
2. results/evaluation/s9_direction_comparison.txt   — direction asymmetry
3. scripts/evaluation/generate_paper_figures.py     — existing generation script
4. docs/paper/figures/                              — existing figure outputs
5. docs/paper/paper_draft.md                        — figure references in text

### SESSION GOAL

Regenerate all publication figures with complete evaluation data and add F1 (architecture).
Output: PDF + PNG for each figure at 300 DPI minimum.

## FIGURES TO GENERATE

### F1: System Architecture Diagram (NEW)

Create a block diagram showing ParBench's four components:
1. Spec JSON (leftmost) — declarative correctness contracts
2. Augmentation Engine (branch above main flow) — L0-L4 transforms
3. Evaluation Pipeline (center) — LLM prompt -> response -> file extraction
4. Harness Pipeline (right) — Build -> Run -> Verify -> Result JSON

Show the self-repair feedback loop from Verify back to LLM prompt.
Show augmented source feeding into the Evaluation Pipeline.
Use clean boxes and arrows. No photographs or icons — geometric shapes only.

### F2: Kernel x Model Heatmap (UPDATE)

Currently: All directions, 17 kernels + xsbench x 3 models. Overall 105/468 = 22.44% PASS.
Update: Add omp-to-cuda data as a second panel or side-by-side comparison.
Data: Table 8 from paper_draft.md + s9_direction_comparison.txt
Colors: green (PASS), red (BUILD_FAIL), orange (RUN_FAIL), grey (EXTRACTION_FAIL)
Sort kernels by difficulty (always-pass at top, always-fail at bottom).

### F3: Failure Taxonomy (UPDATE)

Currently: Stacked bar chart, all tasks, 3 models. 105 PASS / 180 BUILD_FAIL / 89 RUN_FAIL / 49 EXTRACTION_FAIL / 45 VERIFY_FAIL.
Update: Add omp-to-cuda failure distribution as grouped bars or second panel.
Data: eval_summary.json by_model and by_direction sections.
Categories: PASS (105), BUILD_FAIL (180), RUN_FAIL (89), EXTRACTION_FAIL (49), VERIFY_FAIL (45).

### F4: Augmentation Robustness Curve (UPDATE)

Currently: Line chart L0-L4, 3 models (Claude flat, Gemini degrading, Groq noisy).
Update: Verify data matches eval_summary.json. May need no changes if L1-L4 data
was already incorporated from S7. Check axis labels and legend.
Data: Table 10 from paper_draft.md.

### F5: Cross-Direction Comparison (UPDATE)

Currently: XSBench cross-direction only.
Update: Add Rodinia cuda-to-omp vs omp-to-cuda comparison (S9 data).
Data: s9_direction_comparison.txt + eval_summary.json by_direction.
Show: Per-model bars comparing pass rates in both directions.
Highlight the 18.8pp aggregate asymmetry.

### F6: XSBench Multi-API Results (VERIFY)

Currently: XSBench heatmap across 12 directions.
Update: Verify data matches. May need no changes if S8 data was correct.

## IMPLEMENTATION STEPS

# Step 1: Read the existing figure generation script
cat scripts/evaluation/generate_paper_figures.py
# Understand the current data loading, figure functions, and style settings.

# Step 2: Read the color palette from memory
# Check ~/.claude/projects/*/memory/feedback_color_palette.md
# If not found, use the defaults above.

# Step 3: Read eval_summary.json for all data
# Step 4: Read s9_direction_comparison.txt for direction data

# Step 5: Update generate_paper_figures.py to:
#   a) Load omp-to-cuda data from result JSONs
#   b) Add F1 architecture diagram function
#   c) Update F2 to show bidirectional heatmap
#   d) Update F3 to include omp-to-cuda failure bars
#   e) Update F5 to include Rodinia direction comparison
#   f) Apply SC26 color palette consistently

# Step 6: Run the script
source env_parbench/bin/activate
python3 scripts/evaluation/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --output-dir docs/paper/figures/ -v

# Step 7: Verify outputs exist and look correct
ls -la docs/paper/figures/
# Open PNGs to verify visual quality (if display available)
# Check DPI: python3 -c "from PIL import Image; img = Image.open('docs/paper/figures/f2_kernel_model_heatmap.png'); print(img.info.get('dpi', 'not set'))"

# Step 8: Git commit and push
# Message: "SC26 figures: regenerate F2-F6 with omp-to-cuda data + add F1 architecture"

## ACCEPTANCE CRITERIA

- [ ] F1 (architecture diagram) exists as PDF + PNG
- [ ] F2 includes omp-to-cuda heatmap alongside cuda-to-omp
- [ ] F3 includes omp-to-cuda failure distribution
- [ ] F5 shows Rodinia direction asymmetry (not just XSBench)
- [ ] All figures use consistent SC26 color palette (NOT Okabe-Ito)
- [ ] All PNGs are >= 300 DPI
- [ ] PDFs are vector format (matplotlib default)
- [ ] No data discrepancies between figures and eval_summary.json
- [ ] Figure captions/titles use proper terminology (BUILD_FAIL not Build Fail)
```

### Parallel Safety

- Writes to: `docs/paper/figures/` only (F1-F6 PDFs and PNGs)
- Reads from: `results/evaluation/eval_summary.json`, `results/evaluation/s9_direction_comparison.txt`,
  `scripts/evaluation/generate_paper_figures.py`
- Safe to run concurrently with ALL other sessions (no shared write targets)
- Worktree-safe: does not need Rodinia source or GPU

### Estimated Duration
- **Read script + data:** 30 min
- **Update generate_paper_figures.py:** 1.5 hours
- **Generate + verify F1-F6:** 1 hour
- **Fix issues + re-run:** 30 min
- **Total:** ~4 hours

---

## SESSION S-BIB — Bibliography Compilation

**Priority: P2 — MEDIUM** | **Group 2** | **Lane: Any** | **Duration: 2 hours** | **Worktree: YES**

```
think hard

## CONTEXT

The SC26 paper draft (docs/paper/paper_draft.md) uses \cite{Key} placeholders throughout
but has no .bib file. All references need BibTeX entries before LaTeX conversion (W-S17).

If running in a worktree: cd $(git rev-parse --show-toplevel)
This session reads docs/paper/paper_draft.md and writes docs/paper/references.bib only.

### SESSION GOAL

Create a complete, verified BibTeX bibliography file containing entries for every
\cite{} reference in the paper draft.

## STEP 1: Extract all citation keys from the paper

grep -oP '\\cite\{[^}]+\}' docs/paper/paper_draft.md | \
  sed 's/\\cite{//;s/}//' | sort -u

Expected keys (from reading the draft):
  AlphaTrans2024
  CodeRosetta2024
  HeCBench2021
  HumanEval2021
  HPCorpus2023
  LASSI2024
  OMPify2023
  ParaCodex2026
  ParEval2024
  ParEvalRepo2025
  RepoTransBench2024
  Rodinia2009
  SWEbench2024
  TransCoder2020
  XSBench2014

## STEP 2: Write BibTeX entries

For each citation key, write the complete BibTeX entry. Use the information below.
Verify fields: author, title, year, booktitle/journal, volume, pages, doi, url.

### Known References

**Rodinia2009** — Che et al., "Rodinia: A Benchmark Suite for Heterogeneous Computing"
  Venue: IISWC 2009 (IEEE International Symposium on Workload Characterization)
  Authors: Shuai Che, Michael Boyer, Jiayuan Meng, David Tarjan, Jeremy W. Sheaffer,
           Sang-Ha Lee, Kevin Skadron
  DOI: 10.1109/IISWC.2009.5306797

**XSBench2014** — Tramm et al., "XSBench - The Development and Verification of a
  Performance Abstraction for Monte Carlo Reactor Analysis"
  Venue: PHYSOR 2014
  Authors: John R. Tramm, Andrew R. Siegel, Tanzima Islam, Martin Schulz

**HumanEval2021** — Chen et al., "Evaluating Large Language Models Trained on Code"
  Venue: arXiv:2107.03374 (2021)
  Authors: Mark Chen, Jerry Tworek, Heewoo Jun, et al.
  Note: Long author list — use first 3 + "and others" or full list per venue style

**SWEbench2024** — Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World
  GitHub Issues?"
  Venue: ICLR 2024
  Authors: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei,
           Ofir Press, Karthik Narasimhan
  DOI: 10.48550/arXiv.2310.06770

**TransCoder2020** — Roziere et al., "Unsupervised Translation of Programming Languages"
  Venue: NeurIPS 2020
  Authors: Baptiste Roziere, Marie-Anne Lachaux, Lowik Chanussot, Guillaume Lample
  DOI: 10.48550/arXiv.2006.03511

**ParEval2024** — Davis et al., "Can Large Language Models Write Parallel Code?"
  Venue: HPDC 2024 (ACM International Symposium on High-Performance Parallel and
  Distributed Computing)
  Authors: Daniel Nichols, Joshua H. Davis, Zhaojun Xie, Arjun Rajaram, Abhinav Bhatele

**ParEvalRepo2025** — Davis et al., "On the Limits of LLM-Based Repository-Level
  HPC Code Translation"
  Venue: ICPP 2025 (54th International Conference on Parallel Processing)
  DOI: 10.1145/3754598.3754669
  Authors: Joshua H. Davis, Daniel Nichols, Abhinav Bhatele

**OMPify2023** — Kadosh et al., "Advising OpenMP Parallelization via a Graph-Based
  Approach with Transformers"
  Venue: Verify exact venue (ISC High Performance 2023 or SC 2023 Workshop)
  Authors: Tal Kadosh, Niranjan Hasabnis, Timothy Mattson, Yuval Pinter, Gal Oren

**HPCorpus2023** — Verify: is this a separate dataset paper or the same as ParEval?
  Check if Nichols et al. or a different group.

**HeCBench2021** — Jin et al., heterogeneous computing benchmark suite
  Venue: Verify (technical report or conference paper)

**CodeRosetta2024** — Unsupervised parallel code translation (CUDA to HIP)
  Venue: Verify

**RepoTransBench2024** — Repository-level code translation benchmark
  Venue: Verify

**AlphaTrans2024** — Compositional code translation with validation
  Venue: Verify

**LASSI2024** — LLM self-correcting pipeline for parallel code translation
  Venue: CLUSTER 2024

**ParaCodex2026** — Kaplan et al., profiling-guided autonomous parallel code translation
  Venue: Under submission (companion paper)
  Note: Use @unpublished or @misc with note="Under submission"

## STEP 3: Write the .bib file

Write all entries to: docs/paper/references.bib
Use consistent formatting:
- @inproceedings for conference papers
- @article for journal papers
- @misc for arXiv preprints
- @unpublished for under-submission papers
- Include DOI where available
- Include URL for arXiv papers

## STEP 4: Web search for missing details

For entries where venue, authors, or DOI are uncertain, use web search to find the
correct publication details. Priority lookups:
1. HeCBench — find the canonical citation
2. CodeRosetta — find authors and venue
3. RepoTransBench — find authors and venue
4. AlphaTrans — find authors and venue
5. LASSI — confirm CLUSTER 2024 and find authors
6. HPCorpus — distinguish from ParEval if same authors
7. OMPify — confirm exact venue (ISC or SC workshop)

## STEP 5: Verify completeness

# Count citation keys in paper
grep -oP '\\cite\{[^}]+\}' docs/paper/paper_draft.md | \
  sed 's/\\cite{//;s/}//' | sort -u | wc -l

# Count entries in .bib file
grep -c '^@' docs/paper/references.bib

# These two numbers MUST match.

# Also check for any citation keys in the paper that are NOT in the .bib:
comm -23 \
  <(grep -oP '\\cite\{[^}]+\}' docs/paper/paper_draft.md | sed 's/\\cite{//;s/}//' | sort -u) \
  <(grep -oP '^\s*@\w+\{(\S+),' docs/paper/references.bib | sed 's/.*{//;s/,//' | sort -u)
# Expected: empty (no missing entries)

## STEP 6: Git commit and push
# Message: "SC26 paper: add references.bib with N entries for all cited works"

## ACCEPTANCE CRITERIA

- [ ] docs/paper/references.bib exists
- [ ] Every \cite{} key in paper_draft.md has a matching @entry in references.bib
- [ ] At least 15 BibTeX entries total
- [ ] Each entry has: author, title, year, and venue (booktitle/journal/howpublished)
- [ ] DOI included for all conference/journal papers where available
- [ ] No duplicate entries (same paper under different keys)
- [ ] Consistent formatting (same field order, same brace style)
- [ ] ParEval-Repo DOI matches: 10.1145/3754598.3754669
- [ ] ParaCodex marked as @unpublished or @misc (under submission)
```

### Parallel Safety

- Writes to: `docs/paper/references.bib` only (new file)
- Reads from: `docs/paper/paper_draft.md` (grep for \cite{} keys)
- Safe to run concurrently with ALL other sessions (no shared write targets)
- Worktree-safe: does not need Rodinia source or GPU
- No decision gates — can run fully autonomously

### Estimated Duration
- **Extract citation keys:** 10 min
- **Write known entries:** 30 min
- **Web search for unknown entries:** 45 min
- **Verify completeness:** 15 min
- **Total:** ~2 hours


---

## FINALIZATION SESSION PROMPTS

These three sessions form the final convergence path to SC26 submission. Execution order:
W-S16 (Group 1, starts immediately) --> W-S15 (Group 4, after paper draft complete) +
W-S17 (Group 4, parallel with W-S15) --> S18 (Group 5, final gate after everything else).

---

## SESSION W-S16 — Anonymous GitHub Repo (WORKTREE-SAFE)

**Priority: P0 — CRITICAL** | **Group 1** | **Lane: Worktree** | **Duration: 4 hours** | **Worktree: YES**

### Context

SC26 uses double-blind review. The paper must not contain author-identifying information,
and the code repository must be anonymized. The current repository contains the author's
name in GitHub URLs, machine paths, commit history, README links, and memory files.
This session creates a sanitized mirror suitable for double-blind artifact submission.

### Dependencies
- **None.** Starts immediately (Group 1). Runs in a worktree — safe to parallelize with S-VERIFY, S-DEPS, S-TAXONOMY, S-ANALYSIS.

### Decisions Needed Before Starting
- [ ] Anonymous GitHub account created (Samyak must do this manually before the session)
- [ ] Account name decided (suggest: `parbench-anonymous` or `anonymous-sc26-submission`)
- [ ] Whether to include full `results/` directory (~2MB, enables reproduction)
- [ ] Whether to include `rodinia/rodinia-src/` (large; reviewers can clone Rodinia separately)
- [ ] Git author name/email for the anonymous commit (suggest: `Anonymous <anonymous@example.com>`)

## BEFORE YOU START — What I Need From You

Before copy-pasting the prompt below, fill in all `[FILL IN ...]` placeholders:
1. `[ANON_ACCOUNT]` — the anonymous GitHub account name
2. `[INCLUDE_RESULTS]` — yes or no (whether to include results/ in the anonymous repo)
3. `[INCLUDE_RODINIA_SRC]` — yes or no (whether to include rodinia/rodinia-src/)

---

<details>
<summary>Prompt (copy-paste into a fresh /clear session in a worktree)</summary>

```
I need to complete SESSION W-S16: create an anonymous GitHub repository for SC26 double-blind submission.

Use ultrathink for the sanitization verification steps. Zero tolerance for leaked identifiers.

## Context

SC26 uses double-blind review. The current repository contains author-identifying information in:
- GitHub URL: `samyakjhaveri.github.io/parbench_sam` (contains author name)
- Machine paths: `/home/samyak/...` and `/Users/samyakjhaveri/...` throughout CLAUDE.md, config/paths.json, memory files
- Git commit history: author name and email in every commit
- README.md: personal GitHub links
- `.claude/` directory: rules and memory referencing author by name
- `env_parbench/`: machine-specific virtual environment
- `presentations/`: speaking notes with personal content
- `docs/session_prompts_sc26.md` and `docs/session_plans/`: session plans with personal references

Anonymous GitHub account: [ANON_ACCOUNT]
Include results/: [INCLUDE_RESULTS]
Include rodinia/rodinia-src/: [INCLUDE_RODINIA_SRC]

## Step 1: Create the sanitization script

Create `scripts/anonymize_repo.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ANON_ACCOUNT="${1:?Usage: $0 <anonymous-github-account-name>}"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST_DIR="/tmp/parbench_anon"

echo "=== Sanitizing $SRC_DIR -> $DEST_DIR ==="

# Clean slate
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

# Directories to exclude from the anonymous repo
EXCLUDES=(
  '.git/'
  '.claude/'
  'env_parbench/'
  'presentations/'
  '__pycache__/'
  '*.pyc'
  '.DS_Store'
  'node_modules/'
  'docs/session_plans/'
  'docs/session_prompts_sc26.md'
  '.validation_passed'
)

RSYNC_EXCLUDES=""
for exc in "${EXCLUDES[@]}"; do
  RSYNC_EXCLUDES="$RSYNC_EXCLUDES --exclude=$exc"
done

# shellcheck disable=SC2086
rsync -a --progress $RSYNC_EXCLUDES "$SRC_DIR/" "$DEST_DIR/"

echo "=== Scrubbing author-identifying strings ==="

# All known identifying strings (case-insensitive scrub)
SCRUB_STRINGS=(
  "samyakjhaveri"
  "Samyak Jhaveri"
  "samyak jhaveri"
  "Samyak"
  "samyak"
  "jhaveri"
  "Jhaveri"
)

TEXT_EXTENSIONS="md json py sh txt html js css toml cfg yaml yml tex bib"
FIND_NAME_ARGS=""
for ext in $TEXT_EXTENSIONS; do
  if [ -n "$FIND_NAME_ARGS" ]; then
    FIND_NAME_ARGS="$FIND_NAME_ARGS -o"
  fi
  FIND_NAME_ARGS="$FIND_NAME_ARGS -name *.$ext"
done

for pattern in "${SCRUB_STRINGS[@]}"; do
  find "$DEST_DIR" -type f \( $FIND_NAME_ARGS \) -exec grep -li "$pattern" {} \; 2>/dev/null | while read -r file; do
    sed -i "s|$pattern|[REDACTED]|g" "$file"
  done
done

# Fix machine-specific paths -> generic placeholders
find "$DEST_DIR" -type f \( $FIND_NAME_ARGS \) -print0 | xargs -0 sed -i \
  -e 's|/home/samyak/Desktop/parbench_sam|/path/to/parbench|g' \
  -e 's|/Users/samyakjhaveri/Desktop/parbench_sam|/path/to/parbench|g' \
  2>/dev/null || true

echo "=== Replacing config/paths.json ==="
cat > "$DEST_DIR/config/paths.json" << 'PATHEOF'
{
    "project_root": "/path/to/parbench",
    "downloads_root": "/path/to/parbench",
    "hecbench_root": "/path/to/parbench/HeCBench-master"
}
PATHEOF

echo "=== Verifying anonymization ==="
LEAKED=$(grep -ri "samyak\|jhaveri" "$DEST_DIR" \
  --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
  --include="*.txt" --include="*.html" --include="*.js" --include="*.toml" \
  --include="*.tex" --include="*.bib" -l 2>/dev/null || true)

if [ -n "$LEAKED" ]; then
  echo "FAIL: Author-identifying strings still found in:"
  echo "$LEAKED"
  exit 1
else
  echo "PASS: No author-identifying strings found."
fi

echo ""
echo "=== Initializing fresh git repo ==="
cd "$DEST_DIR"
git init
git config user.name "Anonymous"
git config user.email "anonymous@example.com"
git add -A
git commit -m "ParBench: LLM-based parallel code translation benchmark framework"

echo ""
echo "=== Done ==="
echo "Anonymous repo ready at: $DEST_DIR"
echo "To push:"
echo "  cd $DEST_DIR"
echo "  git remote add origin git@github.com:${ANON_ACCOUNT}/parbench.git"
echo "  git push -u origin main"
```

Make it executable: `chmod +x scripts/anonymize_repo.sh`

## Step 2: Create a clean CLAUDE.md for the anonymous repo

After running the script, REPLACE `$DEST_DIR/CLAUDE.md` with a clean project-usage document.
It should contain ONLY:
- One-paragraph project description
- Directory layout (same structure table from current CLAUDE.md, minus .claude/ and presentations/)
- Installation: `pip install -r requirements.txt` (Python 3.12+)
- Core commands: validate, harness verify, harness prompt, run eval batch
- Spec format overview (reference schema/spec_schema.json)
- NO personal paths, NO machine-specific instructions, NO `.claude/` references, NO author name

## Step 3: Create a clean README.md for the anonymous repo

Replace `$DEST_DIR/README.md` with a paper-companion README:
- Title: "ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation"
- One-paragraph abstract (from paper)
- Quick start: clone, install, validate, run one eval
- Directory layout (brief)
- Benchmark suites: Rodinia (60 specs), HeCBench (120 specs), XSBench (4 specs)
- Evaluation: how to reproduce the paper's results
- License: check if a LICENSE file exists; if not, create one (MIT)
- NO author names, NO personal links, NO acknowledgments

## Step 4: Run the sanitization script

```bash
cd /home/samyak/Desktop/parbench_sam
bash scripts/anonymize_repo.sh [ANON_ACCOUNT]
```

## Step 5: Verify exhaustively

```bash
cd /tmp/parbench_anon

# 1. No author-identifying strings (MUST return nothing)
grep -ri "samyak\|jhaveri" . \
  --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
  --include="*.txt" --include="*.html" --include="*.js" --include="*.toml" \
  --include="*.tex" --include="*.bib" -l

# 2. No .claude directory
test -d .claude && echo "FAIL: .claude exists" || echo "PASS: no .claude"

# 3. No presentations directory
test -d presentations && echo "FAIL: presentations exists" || echo "PASS: no presentations"

# 4. No env_parbench directory
test -d env_parbench && echo "FAIL: env_parbench exists" || echo "PASS: no env_parbench"

# 5. config/paths.json uses generic paths
cat config/paths.json
# Expected: /path/to/parbench (no real usernames)

# 6. No personal GitHub URLs
grep -ri "samyakjhaveri.github.io\|github.com/samyakjhaveri" . -l
# Expected: no output

# 7. Git history is clean
git log --all --format="%H %an %ae %s"
# Expected: one commit from "Anonymous <anonymous@example.com>"

# 8. README.md exists and is useful
head -20 README.md

# 9. CLAUDE.md has no personal content
grep -i "samyak\|jhaveri\|/home/\|/Users/" CLAUDE.md
# Expected: no output

# 10. No secrets or credentials
grep -ri "api_key\|api_secret\|password\|ANTHROPIC_API_KEY\|OPENAI_API_KEY" . \
  --include="*.py" --include="*.json" --include="*.sh" --include="*.env" \
  --include="*.toml" -l
# Expected: no output (or only in documentation showing example config patterns)

# 11. Spec files are present and valid JSON
ls specs/*.json | wc -l
python3 -c "import json; [json.load(open(f)) for f in __import__('glob').glob('specs/*.json')]"
# Expected: 184 (or close), no JSON errors

# 12. requirements.txt exists (from S-DEPS, or create a minimal one now)
test -f requirements.txt && echo "PASS" || echo "WARN: requirements.txt missing (create from S-DEPS)"
```

## Step 6: Push to anonymous account (requires Samyak's manual step)

```bash
cd /tmp/parbench_anon
git remote add origin git@github.com:[ANON_ACCOUNT]/parbench.git
git push -u origin main
```

Samyak: you'll need to authenticate with the anonymous GitHub account's SSH key or token.

## Step 7: Record the anonymous URL

In the MAIN repo (not the anonymous one):

1. Add `docs/anonymous_repo_url.txt` to `.gitignore`
2. Create `docs/anonymous_repo_url.txt`:
   ```
   https://github.com/[ANON_ACCOUNT]/parbench
   Created: [DATE]
   Purpose: SC26 double-blind artifact submission
   ```

## Acceptance criteria:
- [ ] `scripts/anonymize_repo.sh` exists and runs without errors
- [ ] `/tmp/parbench_anon/` contains the sanitized repo
- [ ] `grep -ri "samyak\|jhaveri" /tmp/parbench_anon/` returns ZERO results across all text files
- [ ] `grep -ri "samyakjhaveri.github.io" /tmp/parbench_anon/` returns ZERO results
- [ ] Anonymous repo has a single-commit history from "Anonymous <anonymous@example.com>"
- [ ] CLAUDE.md contains only project usage instructions (no personal paths or names)
- [ ] README.md is a proper paper-companion README with installation + usage
- [ ] config/paths.json uses `/path/to/parbench` placeholders
- [ ] No `.claude/`, `env_parbench/`, `presentations/`, or `docs/session_plans/` directories
- [ ] No API keys or credentials in any file
- [ ] Spec files are present and valid JSON
- [ ] `docs/anonymous_repo_url.txt` created in main repo with the URL
- [ ] Repo pushed to anonymous GitHub account (Samyak's manual step — mark as pending)
```

</details>

### Write Targets
| File | Action |
|------|--------|
| `scripts/anonymize_repo.sh` | CREATE — sanitization automation script |
| `/tmp/parbench_anon/` | CREATE (external) — the sanitized repo |
| `/tmp/parbench_anon/CLAUDE.md` | REPLACE — clean project-usage doc |
| `/tmp/parbench_anon/README.md` | REPLACE — paper-companion README |
| `docs/anonymous_repo_url.txt` | CREATE — record of anonymous URL |
| `.gitignore` | EDIT — add `docs/anonymous_repo_url.txt` |

### Read Targets
| File | Purpose |
|------|---------|
| Entire repository tree | Scan for identifying strings |
| `CLAUDE.md` | Reference for project-usage content |
| `README.md` | Reference for current README structure |
| `config/paths.json` | Verify path sanitization |

### Estimated Duration
- Script creation: 30 min
- CLAUDE.md / README.md rewrite: 45 min
- Run sanitization: 15 min
- Verification (12 checks): 30 min
- Push + record: 15 min (requires Samyak)
- **Total:** ~2.5 hours (plus Samyak's manual push step)

---

## SESSION W-S15 — Paper Review & Polish (WORKTREE-SAFE)

**Priority: P1 — HIGH** | **Group 4** | **Lane: Worktree** | **Duration: 4-6 hours** | **Worktree: YES**

### Context

After S12 (S1-S2), W-S12-PARTIAL (S3-S5), and S13 (S6-S8) complete, the full paper draft
exists across markdown files. This session does a thorough review and polish pass — merging
all sections into a single file, verifying every number against ground truth data, tightening
prose to fit the 10-page ACM sigconf limit, and running adversarial self-review.

### Dependencies
- **Hard:** S12 (Sections 1-2) complete, S13 (Sections 6-8) complete, W-S12-PARTIAL (Sections 3-5) complete
- **Soft:** S-VERIFY data incorporated (if available), S-TAXONOMY error taxonomy (if available), S-FIGURES regenerated (if available)

## BEFORE YOU START — What I Need From You

Verify that all paper sections exist before launching this session:
```bash
# Check that all sections have been written
head -5 docs/paper/paper_draft.md         # Should have Sections 1-2
head -5 docs/paper/paper_sections_3_4_5.md # Should have Sections 3-5
# Sections 6-8: check paper_draft.md or separate files in docs/paper/
grep -n "^## S6\|^## S7\|^## S8\|Section 6\|Section 7\|Section 8" docs/paper/paper_draft.md
```

If any sections are missing, do NOT start this session — complete the writing sessions first.

---

<details>
<summary>Prompt (copy-paste into a fresh /clear session in a worktree)</summary>

```
I need to complete SESSION W-S15: thorough review and polish of the complete SC26 paper draft before LaTeX conversion.

Use ultrathink for this entire session. Every claim in the paper must be verified against actual data.

## Context

The paper draft exists across these files:
- `docs/paper/paper_draft.md` — Sections 1-2 (Introduction, Related Work) + Abstract
- `docs/paper/paper_sections_3_4_5.md` — Sections 3-5 (System Design, Augmentation, Experimental Setup)
- Sections 6-8 (Results, Discussion, Conclusion) — check `docs/paper/paper_draft.md` or separate files

Ground truth data:
- `results/evaluation/eval_summary.json` — canonical aggregate numbers (468 tasks, 3 models)
- `results/evaluation/` — 500 individual result JSON files
- `docs/paper/figures/` — 6 figures (F2-F6) + 1 LaTeX table (T2)

Target format: ACM sigconf double-column, 10-page limit (~8000-9000 words including references).
Current draft is estimated at ~11,500 words — must be tightened by ~25%.

## Step 1: Read the COMPLETE paper draft

Read ALL paper files in order. Build a mental model of the full argument:
1. `docs/paper/paper_draft.md`
2. `docs/paper/paper_sections_3_4_5.md`
3. Any additional section files in `docs/paper/`

Map the argument arc:
- Abstract -> what claims are made?
- S1 Introduction -> what gap is identified? What contributions are listed?
- S2 Related Work -> what prior work is positioned against?
- S3 System Design -> what system is described?
- S4 Augmentation -> what methodology?
- S5 Experimental Setup -> what models, hardware, configs?
- S6 Results -> what data is reported?
- S7 Discussion -> what interpretation? What threats to validity?
- S8 Conclusion -> what summary? What future work?

## Step 2: Number verification pass (CRITICAL — do this yourself, not via subagent)

Read `results/evaluation/eval_summary.json` and verify EVERY number in the paper.

The eval_summary.json contains (post S-VERIFY, 2026-03-27):
- total_tasks: 468
- by_model: claude-sonnet-4-6 (81/156, 51.92%), gemini-2.5-flash-lite (11/156, 7.05%),
  groq-llama-3.3-70b-versatile (13/156, 8.33%)
- by_direction: cuda-to-omp (62/255, 24.31%), omp-to-cuda (9/63, 14.29%), plus 10 more
- by_augment_level: L0 (31/132, 23.48%), L1 (20/84, 23.81%), L2 (21/84, 25.00%),
  L3 (17/84, 20.24%), L4 (16/84, 19.05%)
- failure_taxonomy: BUILD_FAIL=180, RUN_FAIL=89, VERIFY_FAIL=45, EXTRACTION_FAIL=49
- self_repair: attempt_1_pass=78, total_repaired_by_retry=27

IMPORTANT: Post S-VERIFY (2026-03-27), all numbers changed. The paper must use verified data:
- **Overall numbers** (3 models, 468 evaluated tasks):
  Claude 81/156=51.92%, Gemini 11/156=7.05%, Groq 13/156=8.33%
  Overall: 105/468=22.44%

Make sure the paper is ALWAYS clear about which subset each number comes from.

Check every number. Create a verification checklist:
```
[ ] Total evaluated tasks = 468 (504 raw; 36 kmeans/mummergpu excluded)
[ ] Models = 3 (azure-gpt-4.1 DISABLED)
[ ] Claude overall = 81/156 = 51.92%
[ ] Gemini overall = 11/156 = 7.05%
[ ] Groq overall = 13/156 = 8.33%
[ ] Overall PASS = 105/468 = 22.44%
[ ] BUILD_FAIL total = 180 (38.46% of all 468 tasks)
[ ] RUN_FAIL total = 89 (19.02%)
[ ] EXTRACTION_FAIL = 49 (10.47%)
[ ] VERIFY_FAIL = 45 (9.62%)
[ ] Self-repair: 78 first-attempt PASS, 27 repaired by retry, 105 total
[ ] Augmentation L0-L4: L0=23.48%, L1=23.81%, L2=25.00%, L3=20.24%, L4=19.05%
[ ] Per-kernel highest: bptree 66.67%, hotspot3d 61.11%, particlefilter 55.56%
[ ] Per-kernel lowest: heartwall 0%, myocyte 0%, nw 0%
```

CRITICAL: Post S-VERIFY (2026-03-27), the failure breakdown is: BUILD_FAIL 180/468 = 38.46%
of all tasks (or 180/363 = 49.59% of failures only). VERIFY_FAIL is now 45 (9.62%), not zero.
The paper must use these post-S-VERIFY numbers. Any pre-S-VERIFY numbers (e.g., "68.4%",
"61.2%", "202 BUILD_FAIL", "0 VERIFY_FAIL") are stale and must be replaced.

## Step 3: Consistency pass

- Do table numbers match the inline prose numbers?
- Are figure references correct? (F1=architecture, F2=heatmap, F3=failure taxonomy,
  F4=augmentation robustness, F5=cross-direction, F6=XSBench)
- Do section cross-references work? ("As shown in S6.2" — does S6.2 exist?)
- Do contribution claims in S1.3 match what S6 actually demonstrates?
- Does the Abstract match the Conclusion?
- Are all \cite{} keys consistent? (same key used for same reference everywhere)

## Step 4: Scope honesty check

Flag every sentence that overstates what was evaluated:
- "184 specs" = framework CAPACITY, not evaluation scope
- Evaluation covered: 17 Rodinia kernels + 1 XSBench kernel = 18 kernels
- 3 models evaluated (azure-gpt-4.1 DISABLED); 468 evaluated tasks in summary
- 12 translation directions evaluated
- Correct phrasing: "ParBench curates 184 specs" (capacity) vs "We evaluate 468 tasks" (actual)

## Step 5: Threats to validity

Verify S7 (or wherever threats are discussed) honestly addresses ALL of:
1. ~~Exit-code verification limitation~~ — **RESOLVED by S-VERIFY (2026-03-27)**: stdout_pattern+exit_code conjunction now verifies functional correctness
2. Single-run evaluation (no statistical significance; no confidence intervals)
3. Wall-clock timing only (no kernel-time measurement; speedup_ratio unreliable)
4. Small model sample (3 models; results may not generalize to other LLMs)
5. ~~GPT-4.1 evaluated on subset only~~ — **RESOLVED**: azure-gpt-4.1 DISABLED, excluded from analysis
6. Training data contamination: augmentation mitigates but does not eliminate
7. Rodinia-dominant evaluation (17/18 kernels are Rodinia)
8. Temperature/sampling: single temperature setting per model

## Step 6: Writing tightening

Target: cut ~2500-3500 words to reach 8000-9000. Priority order:
1. Merge all sections into ONE file (`docs/paper/paper_draft.md`)
2. Remove redundancy between Abstract and S1.4 (Key Findings Preview) — the preview
   can become 3 bullet points instead of 3 paragraphs
3. Tighten S2 (Related Work): each prior work gets 2-3 sentences, not a paragraph.
   Move detailed comparison to a table.
4. Compress S3 (System Design): implementation details -> appendix or artifact
5. Compress S4 (Augmentation): summarize transforms in a table, not per-transform paragraphs
6. Compress S5 (Experimental Setup): essentials only (models, hardware, configs)
7. S6 (Results): keep data-dense — this is the core. Do NOT cut data.
8. S7 (Discussion): keep threats to validity, tighten implications
9. S8 (Conclusion): ONE paragraph maximum

For sections you tighten, show the word count before and after.

## Step 7: Missing elements

- [ ] Abstract: complete, accurate, <250 words?
- [ ] ACM CCS concepts (required for ACM sigconf)
- [ ] Keywords (5-7 terms)
- [ ] Data availability statement ("ParBench is available at [anonymous URL]")
- [ ] Acknowledgments: blank placeholder (double-blind; added post-acceptance)

## Step 8: Write the output

1. Merge ALL sections into `docs/paper/paper_draft.md` as a single, unified document
   (absorb paper_sections_3_4_5.md and any other section files)
2. Create `docs/paper/review_checklist.md` containing:
   - Number verification table (paper claim | source | actual value | match?)
   - Scope claim audit results
   - Word count per section (before and after tightening)
   - List of remaining TODOs (if any)
   - Summary of changes made

## Step 9: Self-critic review (AFTER all edits are complete)

Use the `self-critic` agent (Opus). Prompt it:

"Read docs/paper/paper_draft.md and results/evaluation/eval_summary.json.
Find every claim in the paper that is not supported by the data. Find every
number that does not match eval_summary.json. Find every scope overstatement.
Find every contribution claim that is not substantiated in the results section.
Be adversarial — assume the paper is trying to overstate its contributions."

Address every finding the self-critic raises. If a finding is a false positive,
document why in the review_checklist.md.

## Acceptance criteria:
- [ ] All sections merged into single `docs/paper/paper_draft.md`
- [ ] Every number verified against eval_summary.json (checklist in review_checklist.md)
- [ ] No scope inflation (every claim scoped to what was actually evaluated)
- [ ] Threats to validity address all 8 limitations listed above
- [ ] Word count between 8000-9500 words
- [ ] `docs/paper/review_checklist.md` created with complete verification log
- [ ] Self-critic agent run; all critical findings addressed
- [ ] No unresolved TODO markers in paper text
- [ ] Figure references verified (F1-F6 exist and are correctly referenced)
- [ ] All \cite{} keys present and consistent
```

</details>

### Write Targets
| File | Action |
|------|--------|
| `docs/paper/paper_draft.md` | EDIT — merge all sections, tighten prose, fix numbers |
| `docs/paper/review_checklist.md` | CREATE — verification log + scope audit |

### Read Targets
| File | Purpose |
|------|---------|
| `docs/paper/paper_draft.md` | Current S1-S2 + Abstract |
| `docs/paper/paper_sections_3_4_5.md` | Current S3-S5 |
| `results/evaluation/eval_summary.json` | Ground truth for all numbers |
| `results/evaluation/**/*.json` | Individual results for spot-checks |
| `docs/paper/figures/` | Verify figure file existence |

### Agent Usage
| Agent | When | Purpose |
|-------|------|---------|
| `self-critic` (Opus) | After all edits complete | Adversarial review of claims vs data |
| `plan-reviewer` | After structural changes | Verify argument arc coherence |

### Estimated Duration
- Full read + number verification: 90 min
- Consistency + scope audit: 60 min
- Prose tightening (2500-3500 words): 90 min
- Self-critic + address findings: 60 min
- **Total:** ~5 hours

---

## SESSION W-S17 — LaTeX Transfer + Final Formatting (WORKTREE-SAFE)

**Priority: P0 — CRITICAL** | **Group 4** | **Lane: Worktree** | **Duration: 2-3 days** | **Worktree: YES**

### Context

SC26 requires ACM sigconf double-column LaTeX format. The paper exists as a polished
markdown document after W-S15. This session converts it to properly formatted LaTeX
with tables, figures, bibliography, and CCS metadata. The output is a compilable
`main.tex` that produces a <= 10-page PDF.

### Dependencies
- **Hard:** W-S15 (paper review/polish) should be complete — the markdown must be finalized
- **Soft:** S-FIGURES (all figures as PDF) should be complete, S-BIB (references.bib) should be available

## BEFORE YOU START — What I Need From You

1. Verify LaTeX toolchain is available on the machine:
   ```bash
   pdflatex --version
   bibtex --version
   kpsewhich acmart.cls
   ```
   If `acmart.cls` is not found, you'll need to install `texlive-full` or download
   the ACM template from https://www.acm.org/publications/proceedings-template.

2. Verify the polished paper draft exists:
   ```bash
   wc -w docs/paper/paper_draft.md
   # Should be 8000-9500 words (post W-S15 tightening)
   ```

3. Verify figures exist as PDF:
   ```bash
   ls docs/paper/figures/*.pdf
   ```

---

<details>
<summary>Prompt (copy-paste into a fresh /clear session in a worktree)</summary>

```
I need to complete SESSION W-S17: convert the finalized paper draft from Markdown to ACM sigconf LaTeX format.

Use ultrathink for structural decisions (table layout, figure placement, page budget allocation).

## Context

The paper is finalized in `docs/paper/paper_draft.md` (~8000-9500 words after W-S15 polish).
Figures exist as PDF in `docs/paper/figures/`:
- f2_kernel_model_heatmap.pdf
- f3_failure_taxonomy.pdf
- f4_augmentation_robustness.pdf
- f5_cross_direction_comparison.pdf (or f5_xsbench_cross_direction.pdf)
- f6_xsbench_multi_api.pdf (or f6_xsbench_heatmap.pdf)
- t2_model_comparison.tex (LaTeX table already formatted)

Ground truth: `results/evaluation/eval_summary.json` (verify table numbers during conversion).

Target: ACM sigconf double-column, anonymous mode, <= 10 pages including references.

## Step 1: Create LaTeX project structure

```bash
mkdir -p docs/paper/latex/sections
mkdir -p docs/paper/latex/figures
```

## Step 2: Create the Makefile

Create `docs/paper/latex/Makefile`:
```makefile
MAIN = main
LATEX = pdflatex
BIBTEX = bibtex

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib $(wildcard sections/*.tex)
	$(LATEX) $(MAIN)
	$(BIBTEX) $(MAIN)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

clean:
	rm -f $(MAIN).{aux,bbl,blg,log,out,pdf,fls,fdb_latexmk,synctex.gz}
	rm -f sections/*.aux

view: $(MAIN).pdf
	xdg-open $(MAIN).pdf 2>/dev/null || open $(MAIN).pdf

.PHONY: all clean view
```

## Step 3: Create main.tex

Create `docs/paper/latex/main.tex`:

```latex
\documentclass[sigconf,anonymous,review]{acmart}

% --- Packages ---
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{subcaption}
\usepackage{balance}
\usepackage{enumitem}

% --- Code listing style ---
\lstset{
  basicstyle=\ttfamily\footnotesize,
  breaklines=true,
  frame=single,
  numbers=left,
  numberstyle=\tiny\color{gray},
  language=C,
  morekeywords={__global__,__device__,__shared__,threadIdx,blockIdx,blockDim,gridDim,cudaMalloc,cudaMemcpy,cudaFree},
  keywordstyle=\color{blue},
  commentstyle=\color{green!50!black},
  stringstyle=\color{red!60!black}
}

% --- Heatmap cell colors (SC26 palette) ---
\definecolor{passhigh}{HTML}{2D5A27}
\definecolor{passmed}{HTML}{7DB87A}
\definecolor{passlow}{HTML}{F5C242}
\definecolor{passzero}{HTML}{C44E52}

% --- ACM metadata ---
\acmConference[SC '26]{The International Conference for High Performance Computing, Networking, Storage, and Analysis}{November 2026}{Atlanta, GA, USA}
\acmYear{2026}

% Remove ACM reference block for review copy
\settopmatter{printacmref=false}
\renewcommand\footnotetextcopyrightpermission[1]{}

\begin{document}

\title{ParBench: Evaluating LLM Parallel Code Translation\\with Build-Run-Verify Correctness and Augmentation Robustness}

\begin{abstract}
% CONVERT FROM paper_draft.md Abstract section
% Keep under 250 words
\end{abstract}

\begin{CCSXML}
<ccs2012>
  <concept>
    <concept_id>10011007.10011006.10011066</concept_id>
    <concept_desc>Software and its engineering~Compilers</concept_desc>
    <concept_significance>500</concept_significance>
  </concept>
  <concept>
    <concept_id>10011007.10011074.10011092</concept_id>
    <concept_desc>Software and its engineering~Software verification and validation</concept_desc>
    <concept_significance>500</concept_significance>
  </concept>
  <concept>
    <concept_id>10010147.10010169</concept_id>
    <concept_desc>Computing methodologies~Parallel computing methodologies</concept_desc>
    <concept_significance>300</concept_significance>
  </concept>
  <concept>
    <concept_id>10010147.10010257</concept_id>
    <concept_desc>Computing methodologies~Machine learning</concept_desc>
    <concept_significance>100</concept_significance>
  </concept>
</ccs2012>
\end{CCSXML}

\ccsdesc[500]{Software and its engineering~Compilers}
\ccsdesc[500]{Software and its engineering~Software verification and validation}
\ccsdesc[300]{Computing methodologies~Parallel computing methodologies}
\ccsdesc[100]{Computing methodologies~Machine learning}

\keywords{LLM code translation, parallel programming, CUDA, OpenMP, benchmark, code augmentation, GPU computing}

\maketitle

\input{sections/01_introduction}
\input{sections/02_related_work}
\input{sections/03_system_design}
\input{sections/04_augmentation}
\input{sections/05_experimental_setup}
\input{sections/06_results}
\input{sections/07_discussion}
\input{sections/08_conclusion}

%% Data availability
\section*{Data Availability}
ParBench, including all benchmark specifications, the evaluation harness, augmentation engine, and result data, is publicly available at \url{[ANONYMOUS-REPO-URL]}.

%% Balance final page columns
\balance

\bibliographystyle{ACM-Reference-Format}
\bibliography{references}

\end{document}
```

## Step 4: Convert each section from Markdown to LaTeX

Read `docs/paper/paper_draft.md` and convert each section into its own .tex file.

Conversion rules:
- `## Section Title` -> `\section{Section Title}\label{sec:name}`
- `### Subsection` -> `\subsection{Subsection}\label{subsec:name}`
- `**bold**` -> `\textbf{bold}`
- `*italic*` -> `\textit{italic}`
- `` `code` `` -> `\texttt{code}`
- `\cite{Key}` -> keep as-is (already LaTeX)
- Markdown tables -> `\begin{table}...\end{tabular}...\end{table}` with booktabs
- Bullet lists -> `\begin{itemize}[nosep]...\end{itemize}`
- Numbered lists -> `\begin{enumerate}[nosep]...\end{enumerate}`
- `%` in text -> `\%`
- `_` in text (not math) -> `\_`
- `&` in text -> `\&`
- `#pragma` -> `\texttt{\#pragma}`
- `~` for literal tilde -> `\textasciitilde{}`
- `---` (em dash) -> `---` (same in LaTeX)

Create these files:
- `sections/01_introduction.tex`
- `sections/02_related_work.tex`
- `sections/03_system_design.tex`
- `sections/04_augmentation.tex`
- `sections/05_experimental_setup.tex`
- `sections/06_results.tex`
- `sections/07_discussion.tex`
- `sections/08_conclusion.tex`

## Step 5: Format key tables

### Error taxonomy table (in S6 Results)
```latex
\begin{table}[t]
\caption{Failure taxonomy across 468 evaluated translation tasks. BUILD\_FAIL dominates
at 38.46\%, while VERIFY\_FAIL (9.62\%) confirms that some translations compile and run
but produce incorrect output.}
\label{tab:error_taxonomy}
\centering\small
\begin{tabular}{lrr}
\toprule
Failure Type & Count & \% of Total \\
\midrule
BUILD\_FAIL      & 180 & 38.46\% \\
RUN\_FAIL        &  89 & 19.02\% \\
EXTRACTION\_FAIL &  49 & 10.47\% \\
VERIFY\_FAIL     &  45 &  9.62\% \\
\midrule
Total failures   & 363 &        \\
\bottomrule
\end{tabular}
\end{table}
```

### Augmentation robustness table (in S6)
```latex
\begin{table}[t]
\caption{Augmentation robustness: pass rates by model and augmentation level
(cuda-to-omp, 17 Rodinia kernels). Claude Sonnet 4.6 is perfectly level-invariant;
Gemini Flash-Lite degrades by 75\% from L0 to L4.}
\label{tab:augmentation}
\centering\small
\begin{tabular}{lccccc}
\toprule
Model & L0 & L1 & L2 & L3 & L4 \\
\midrule
Claude Sonnet 4.6     & 70.6\% & 70.6\% & 70.6\% & 70.6\% & 70.6\% \\
Groq Llama 3.3 70B    & 29.4\% & 35.3\% & 35.3\% & 23.5\% & 23.5\% \\
Gemini 2.5 Flash-Lite & 23.5\% & 17.6\% & 11.8\% & 11.8\% &  5.9\% \\
\bottomrule
\end{tabular}
\end{table}
```
NOTE: These per-model per-level numbers are PRE-S-VERIFY placeholders. Post S-VERIFY
(2026-03-27), overall per-level rates are: L0=23.48%, L1=23.81%, L2=25.00%, L3=20.24%,
L4=19.05%. Per-model: claude=51.92%, gemini=7.05%, groq=8.33% (overall).
Verify against eval_summary.json and compute per-model-per-level from raw results.

### Model comparison table
Copy and adapt `docs/paper/figures/t2_model_comparison.tex` into S5 or S6.

### Per-kernel heatmap table (if used instead of or alongside figure F2)
Use `\cellcolor` with the defined palette colors:
```latex
\newcommand{\passcell}[1]{%
  \ifnum#1>60 \cellcolor{passhigh!30}\textbf{#1\%}%
  \else\ifnum#1>30 \cellcolor{passmed!30}#1\%%
  \else\ifnum#1>0 \cellcolor{passlow!30}#1\%%
  \else \cellcolor{passzero!30}#1\%%
  \fi\fi\fi%
}
```

## Step 6: Include figures

Copy all PDF figures:
```bash
cp docs/paper/figures/f*.pdf docs/paper/latex/figures/
```

For each figure, use appropriate width:
- Single-column figures: `\begin{figure}[t]` with `width=\columnwidth`
- Full-width figures: `\begin{figure*}[t]` with `width=\textwidth`

```latex
% Single-column example
\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{figures/f3_failure_taxonomy.pdf}
\caption{Failure taxonomy across 468 evaluated tasks. BUILD\_FAIL dominates at 38.46\%
of all tasks; VERIFY\_FAIL (9.62\%) reveals translations that compile and run but produce wrong output.}
\label{fig:failure_taxonomy}
\end{figure}

% Full-width example (heatmap needs more space)
\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{figures/f2_kernel_model_heatmap.pdf}
\caption{Per-kernel pass rates across three models (all directions). bptree (66.67\%)
and hotspot3D (61.11\%) are easiest; heartwall, myocyte, and nw (0\%) are hardest.}
\label{fig:kernel_heatmap}
\end{figure*}
```

Each caption must:
1. Describe what the figure shows (1 sentence)
2. State the key takeaway (1 sentence)
3. Specify the data scope if not obvious (e.g., "L0, cuda-to-omp")

## Step 7: Create references.bib

If S-BIB has completed, copy `docs/paper/references.bib` to `docs/paper/latex/references.bib`.

Otherwise, create a minimal bibliography with ALL cited references. Search the paper
markdown for every `\cite{...}` key and ensure each has a bib entry.

Minimum required entries (check paper for full list):
- Rodinia2009 (Che et al., IISWC 2009)
- HumanEval2021 (Chen et al., arXiv 2021)
- SWEbench2024 (Jimenez et al., ICLR 2024)
- ParEval2024 (Nichols et al., 2024)
- ParEvalRepo2025 (Nichols et al., 2025)
- Any other cited works (XSBench, TransCoder, OMPify, HPCorpus, etc.)

Use Google Scholar or the original papers to get correct bibtex entries.
Prefer @inproceedings for conference papers, @article for journals, @misc for arXiv preprints.

## Step 8: First build and fix cycle

```bash
cd docs/paper/latex
make clean && make 2>&1 | tee build_output.txt

# Check results
echo "=== Page count ==="
pdfinfo main.pdf | grep Pages

echo "=== Errors ==="
grep "^!" main.log | head -20

echo "=== Undefined references ==="
grep "LaTeX Warning.*undefined" main.log

echo "=== Missing citations ==="
grep "Citation.*undefined" main.log

echo "=== Overfull hboxes ==="
grep "Overfull.*hbox" main.log | head -10
```

Fix ALL errors before proceeding. Common issues:
- Missing `\end{...}` environments
- Unescaped special characters (`%`, `_`, `&`, `#`)
- Missing bib entries for cited keys
- Figure files not found (check filename case sensitivity on Linux)

## Step 9: Page budget management

After first clean build, check page count.

**If OVER 10 pages** (likely on first build):
1. Move detailed per-kernel table to supplementary material (saves ~0.5 pages)
2. Use `\small` for all table text
3. Reduce figure sizes by 10% (`0.9\columnwidth` instead of `\columnwidth`)
4. Compress itemize/enumerate with `[nosep]`
5. Use `\paragraph{Title}` instead of `\subsubsection{Title}` for minor headings
6. Merge short subsections
7. Last resort: cut XSBench case study to 1 paragraph + 1 table

**If UNDER 8 pages** (unlikely after W-S15):
1. Add a representative code example (CUDA source -> LLM OpenMP output)
2. Expand per-kernel analysis
3. Add "Lessons Learned" to Discussion

## Step 10: Final verification

```bash
cd docs/paper/latex

# Clean build
make clean && make

# All checks
echo "Pages: $(pdfinfo main.pdf | grep Pages | awk '{print $2}')"
echo "Errors: $(grep '^!' main.log | wc -l)"              # Must be 0
echo "Undef refs: $(grep -c 'LaTeX Warning.*undefined' main.log)"  # Must be 0
echo "Missing cites: $(grep -c 'Citation.*undefined' main.log)"    # Must be 0
echo "Overfull hbox: $(grep 'Overfull.*hbox' main.log | wc -l)"    # Aim for <5

# Anonymous mode verification
pdftotext main.pdf - 2>/dev/null | grep -i "samyak\|jhaveri" | wc -l  # Must be 0

# No author names in source
grep -rn "samyak\|jhaveri" . --include="*.tex" --include="*.bib" | wc -l  # Must be 0
```

## LaTeX gotchas to watch for

1. **Underscore in text mode**: `BUILD_FAIL` -> `BUILD\_FAIL` (or `\texttt{BUILD\_FAIL}`)
2. **Percent sign**: `51.92%` -> `51.92\%`
3. **Ampersand in text**: `&` -> `\&`
4. **Hash in text**: `#pragma` -> use `\texttt` or `\lstinline`
5. **Tilde**: `~` is a non-breaking space; use `\textasciitilde` for literal
6. **Figure placement**: Use `[t]` or `[!t]`, never `[h]` alone (LaTeX ignores it)
7. **Table width**: Use `table*` for full-width, `table` for single-column
8. **Code listings**: Use `lstlisting`, not `verbatim` (better formatting + highlighting)
9. **Long URLs**: Use `\url{}` (loaded by acmart via hyperref)
10. **Balance final page**: `\balance` before `\bibliography` to equalize columns

## Acceptance criteria:
- [ ] `docs/paper/latex/main.tex` compiles with `pdflatex` without errors
- [ ] Output PDF is <= 10 pages (including references)
- [ ] All figures render correctly (no missing-file warnings in log)
- [ ] All bibliography references resolve (zero [?] in output)
- [ ] `anonymous` mode enabled — no author names visible in PDF
- [ ] All tables use booktabs style (\toprule, \midrule, \bottomrule)
- [ ] All cross-references resolve (\ref and \label pairs match)
- [ ] CCS concepts and keywords present
- [ ] Data availability statement present with anonymous URL placeholder
- [ ] Overfull hbox count < 5 (none wider than 2pt)
- [ ] `make clean && make` completes without errors
- [ ] `grep -rn "samyak\|jhaveri" docs/paper/latex/` returns nothing
- [ ] Page count verified: ____/10
```

</details>

### Write Targets
| File | Action |
|------|--------|
| `docs/paper/latex/main.tex` | CREATE — main LaTeX document |
| `docs/paper/latex/Makefile` | CREATE — build automation |
| `docs/paper/latex/references.bib` | CREATE — bibliography |
| `docs/paper/latex/sections/01_introduction.tex` | CREATE |
| `docs/paper/latex/sections/02_related_work.tex` | CREATE |
| `docs/paper/latex/sections/03_system_design.tex` | CREATE |
| `docs/paper/latex/sections/04_augmentation.tex` | CREATE |
| `docs/paper/latex/sections/05_experimental_setup.tex` | CREATE |
| `docs/paper/latex/sections/06_results.tex` | CREATE |
| `docs/paper/latex/sections/07_discussion.tex` | CREATE |
| `docs/paper/latex/sections/08_conclusion.tex` | CREATE |
| `docs/paper/latex/figures/` | COPY — all PDF figures from docs/paper/figures/ |

### Read Targets
| File | Purpose |
|------|---------|
| `docs/paper/paper_draft.md` | Source markdown for conversion |
| `docs/paper/paper_sections_3_4_5.md` | Additional sections (if not merged by W-S15) |
| `docs/paper/figures/t2_model_comparison.tex` | Pre-formatted LaTeX table |
| `results/evaluation/eval_summary.json` | Verify table numbers during conversion |

### Estimated Duration
- Project setup + main.tex skeleton: 30 min
- Section conversion (8 sections): 4-6 hours
- Table formatting (5-6 tables): 2 hours
- Figure integration: 1 hour
- Bibliography: 1-2 hours
- Build-fix-iterate cycles (expect 3-5): 2-3 hours
- Page budget adjustment: 1-2 hours
- **Total:** 12-16 hours across 2-3 days

---

## SESSION S18 — Final Review + Submit

**Priority: P0 — CRITICAL** | **Group 5** | **Lane: Supervised** | **Duration: 2-3 days** | **Worktree: NO**

### Context

This is the final convergence session. All previous work feeds into this: the LaTeX paper
from W-S17, the anonymous repo from W-S16, the polished content from W-S15, and all
evaluation data from S1-S10b. This session coordinates the co-author review cycle with
Gal (advisor), implements feedback, and submits to the SC26 portal by April 8, 2026.

### Dependencies
- **ALL previous sessions must be complete**
- LaTeX paper compiles cleanly (`docs/paper/latex/main.pdf` exists, <= 10 pages)
- Anonymous repo exists and is pushed
- All figures are final
- Advisor (Gal) is available for review (2-3 day turnaround)

## BEFORE YOU START — What I Need From You

This session is primarily human-supervised. Claude assists with verification and mechanical
changes, but Samyak drives the co-author review cycle and makes the final submission.

1. Verify the paper compiles:
   ```bash
   cd docs/paper/latex && make clean && make && pdfinfo main.pdf | grep Pages
   ```
2. Verify the anonymous repo URL is accessible:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://github.com/[ANON_ACCOUNT]/parbench
   # Expected: 200
   ```
3. Confirm Gal's availability for review in the next 3-5 days.

---

<details>
<summary>Prompt (copy-paste into a fresh /clear session — main checkout, NOT a worktree)</summary>

```
I need to complete SESSION S18: final review cycle with co-author, last-pass verification, and SC26 submission.

This is the FINAL session before submission. Use ultrathink for every step. Zero tolerance for errors.

## Context

- Paper: `docs/paper/latex/main.pdf` (compiled from `docs/paper/latex/main.tex`)
- Anonymous repo: [FILL IN URL]
- Deadline: April 8, 2026
- Co-author: Gal (advisor) — needs to review and approve before submission
- Ground truth: `results/evaluation/eval_summary.json`

## Step 1: Pre-review audit

Run a complete self-audit BEFORE sharing the paper with Gal. This catches errors that
waste advisor review time.

### 1a. Fresh compile

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/latex
make clean && make

echo "=== Page count ==="
pdfinfo main.pdf | grep Pages

echo "=== Errors ==="
grep "^!" main.log | wc -l

echo "=== Undefined refs ==="
grep -c "LaTeX Warning.*undefined" main.log

echo "=== Missing citations ==="
grep -c "Citation.*undefined" main.log
```

All counts must be 0. Page count must be <= 10.

### 1b. Regenerate eval_summary.json from raw data and compare

```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# Regenerate from actual result files
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam

# Show key numbers
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    d = json.load(f)
print(f'Total tasks: {d[\"total_tasks\"]}')
for model, v in d['by_model'].items():
    print(f'{model}: {v[\"pass\"]}/{v[\"total\"]} = {v[\"rate\"]*100:.1f}%')
print(f'Failures: BUILD={d[\"failure_taxonomy\"][\"BUILD_FAIL\"]}, RUN={d[\"failure_taxonomy\"][\"RUN_FAIL\"]}, VERIFY={d[\"failure_taxonomy\"][\"VERIFY_FAIL\"]}, EXTRACT={d[\"failure_taxonomy\"][\"EXTRACTION_FAIL\"]}')
"
```

### 1c. Number audit — verify EVERY number in the paper

Extract the PDF text and search for all percentages and counts:

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/latex
pdftotext main.pdf - | grep -oE '[0-9]+\.?[0-9]*%|[0-9]+/[0-9]+' | sort -u
```

For each number found, trace it back to eval_summary.json. Create a verification log:

Create `docs/paper/number_verification_log.md`:
```markdown
# Paper Number Verification Log
Generated: [DATE]
Source: results/evaluation/eval_summary.json

| Location in Paper | Claim | eval_summary.json Field | Actual Value | Match? |
|-------------------|-------|------------------------|--------------|--------|
| Abstract | "468 tasks" | total_tasks | 468 | YES |
| Abstract | "51.92% PASS" | Overall Claude pass rate | 81/156 | YES |
| ... | ... | ... | ... | ... |
```

Every row MUST say YES. Any NO is a submission blocker — fix in the LaTeX source.

### 1d. Scope claim audit

```bash
cd /home/samyak/Desktop/parbench_sam

# Verify spec count claim
echo "Spec count: $(ls specs/*.json 2>/dev/null | wc -l)"

# Verify result file count
echo "Result files: $(find results/evaluation -name '*.json' -not -name 'eval_summary*' | wc -l)"

# Verify kernel count
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    d = json.load(f)
print(f'Kernels evaluated: {len(d[\"by_kernel\"])}')
for k in sorted(d['by_kernel'].keys()):
    v = d['by_kernel'][k]
    print(f'  {k}: {v[\"pass\"]}/{v[\"total\"]} ({v[\"rate\"]*100:.1f}%)')
"
```

Cross-check paper's scope claims:
- "184 specs" -> must use "curates" or "supports" (not "evaluates")
- "468 tasks" -> matches total_tasks
- "17 Rodinia kernels" -> check by_kernel count (minus xsbench = 17 Rodinia)
- "3 LLMs" -> verify all 3 appear in by_model (azure-gpt-4.1 DISABLED)
- Translation directions -> verify which were actually evaluated vs claimed as supported

### 1e. Anonymous repo spot-check

```bash
cd /tmp
rm -rf parbench_verify
git clone [ANONYMOUS_REPO_URL] parbench_verify 2>&1 | tail -3

cd parbench_verify

# Author name leak check
echo "=== Author name leak check ==="
grep -ri "samyak\|jhaveri" . \
  --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
  --include="*.txt" --include="*.html" --include="*.toml" \
  --include="*.tex" --include="*.bib" -l 2>/dev/null
echo "(expect no output above)"

# Credential leak check
echo "=== Credential leak check ==="
grep -ri "api_key\|api_secret\|password\|ANTHROPIC_API_KEY\|OPENAI_API_KEY" . \
  --include="*.py" --include="*.json" --include="*.sh" --include="*.env" \
  --include="*.toml" -l 2>/dev/null
echo "(expect no output above)"

# Git author check
echo "=== Git author check ==="
git log --all --format="%an <%ae>"
echo "(expect: Anonymous <anonymous@example.com>)"

cd /tmp && rm -rf parbench_verify
```

### 1f. LaTeX anonymity check

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/latex

# Check PDF text for author names
pdftotext main.pdf - 2>/dev/null | grep -i "samyak\|jhaveri" | wc -l
echo "(must be 0)"

# Check source files for author names
grep -rn "samyak\|jhaveri" . --include="*.tex" --include="*.bib" | wc -l
echo "(must be 0)"

# Verify anonymous mode in documentclass
grep "anonymous" main.tex
echo "(must show anonymous option)"
```

## Step 2: Share with advisor

Once ALL audit checks pass:

1. Send `main.pdf` to Gal with a cover note:
   ```
   Subject: ParBench SC26 draft for review

   Gal,

   Attached is the ParBench paper draft for SC26, ready for your review.

   Key numbers:
   - 468 evaluated translation tasks across 3 LLMs, 18 kernels, 12 directions
   - Claude Sonnet 4.6: 51.92% PASS (best); Gemini Flash-Lite: 7.05% (worst)
   - Verified with stdout_pattern+exit_code conjunction (post S-VERIFY)
   - Augmentation: level-invariant across L1-L4 (54/60 Rodinia PASS)

   Known limitations (addressed in Threats to Validity):
   - Single-run evaluation (no statistical significance)
   - Wall-clock timing only (no kernel profiling)
   - 3 models is a small sample

   I need feedback by [DATE] to meet the April 8 deadline.
   Expecting 2-3 revision cycles.
   ```

2. While waiting for feedback, prepare:
   - SC26 submission portal: verify account, understand requirements
   - Artifact track: check if SC26 has artifact evaluation, prepare description
   - Supplementary materials: decide what (if anything) goes in supplement

## Step 3: Implement advisor feedback

When Gal returns feedback:

1. **Read ALL feedback** before making any changes
2. **Categorize** each item:
   - CRITICAL: factual errors, wrong claims, missing analysis -> fix immediately
   - IMPORTANT: unclear writing, weak arguments, missing context -> fix next
   - NICE-TO-HAVE: style preferences, additional analysis -> fix if time permits
3. **Implement** in priority order: CRITICAL -> IMPORTANT -> NICE-TO-HAVE
4. **Re-compile** after each batch:
   ```bash
   cd /home/samyak/Desktop/parbench_sam/docs/paper/latex
   make clean && make
   pdfinfo main.pdf | grep Pages
   ```
5. **Re-verify** numbers if any data claims changed
6. **Send** revised PDF back to Gal

Budget per revision cycle:
- Cycle 1: 4-8 hours (largest feedback batch)
- Cycle 2: 2-4 hours (clarifications, remaining items)
- Cycle 3: 1-2 hours (final polish, signoff)

## Step 4: Final compilation

After Gal approves:

```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/latex

# Final clean build
make clean && make

# Comprehensive final check
echo "=== FINAL CHECKS ==="
echo "Pages: $(pdfinfo main.pdf | grep Pages | awk '{print $2}')"
echo "Errors: $(grep '^!' main.log | wc -l)"
echo "Undefined refs: $(grep -c 'LaTeX Warning.*undefined' main.log)"
echo "Missing citations: $(grep -c 'Citation.*undefined' main.log)"
echo "Overfull hbox: $(grep 'Overfull.*hbox' main.log | wc -l)"
echo "Author leak: $(pdftotext main.pdf - 2>/dev/null | grep -ic 'samyak\|jhaveri')"

# Archive the final version with date stamp
DATESTAMP=$(date +%Y%m%d_%H%M)
cp main.pdf "../parbench_sc26_final_${DATESTAMP}.pdf"
echo "Archived: docs/paper/parbench_sc26_final_${DATESTAMP}.pdf"

# Record PDF checksum
md5sum main.pdf
```

ALL check values must be 0 (except Pages which must be <= 10).

## Step 5: Submission

### Submission checklist (go through EVERY item):

```markdown
### Paper Quality
- [ ] PDF compiles cleanly (0 errors, 0 warnings for undefined refs/citations)
- [ ] Page count: ____/10
- [ ] Anonymous mode: no author names in PDF text
- [ ] All figures render correctly
- [ ] All tables have correct numbers (verified against eval_summary.json)
- [ ] No [?] markers for undefined references

### Content Integrity
- [ ] Every number verified (number_verification_log.md is all-YES)
- [ ] Scope claims are honest (no inflation)
- [ ] Threats to validity address all known limitations
- [ ] Contributions in S1 match demonstrations in S6
- [ ] Abstract matches Conclusion

### Artifact
- [ ] Anonymous repo URL: _______________
- [ ] Repo contains README.md with setup instructions
- [ ] Repo contains requirements.txt
- [ ] Repo passes author-name leak check
- [ ] Data availability statement in paper references the repo

### Advisor Signoff
- [ ] Gal has reviewed the final PDF
- [ ] All CRITICAL feedback items addressed
- [ ] Gal has given explicit approval to submit

### Submission Portal
- [ ] SC26 account active and logged in
- [ ] Paper PDF uploaded
- [ ] Author information entered in submission system (NOT in paper)
- [ ] Keywords/topics selected
- [ ] Conflicts of interest declared (if required)
- [ ] Supplementary materials uploaded (if any)
- [ ] SUBMIT button clicked
- [ ] Confirmation page saved / confirmation email received
```

### Submit to SC26 portal

1. Upload `main.pdf`
2. Enter author information in the submission system
3. Select topic areas (parallel programming, LLMs, benchmarking, GPU computing)
4. Submit
5. Save the confirmation

### Record the submission

Create `docs/paper/submission_record.md`:
```markdown
# SC26 Submission Record

- **Submitted:** [YYYY-MM-DD HH:MM timezone]
- **Submission ID:** [from portal]
- **Title:** ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness
- **Authors:** [entered in portal, not in paper]
- **Anonymous repo:** [URL]
- **PDF archived as:** docs/paper/parbench_sc26_final_[DATESTAMP].pdf
- **PDF checksum (md5):** [from md5sum]
- **Git commit:** [output of git rev-parse HEAD]
- **eval_summary.json checksum (md5):** [from md5sum results/evaluation/eval_summary.json]
```

## Step 6: Post-submission

```bash
cd /home/samyak/Desktop/parbench_sam

# Tag the submission commit
git tag -a sc26-submission-v1 -m "SC26 submission $(date +%Y-%m-%d)"
git push origin sc26-submission-v1

# Verify tag
git show sc26-submission-v1
```

## Acceptance criteria:
- [ ] Paper submitted to SC26 portal by April 8, 2026
- [ ] Confirmation email/page saved
- [ ] Advisor (Gal) has approved the final version
- [ ] `docs/paper/number_verification_log.md` complete — all rows say YES
- [ ] `docs/paper/submission_record.md` created with all metadata
- [ ] Final PDF archived with datestamp
- [ ] Git tag `sc26-submission-v1` created and pushed
- [ ] Anonymous repo accessible and passes all leak checks
- [ ] Submission checklist above — every box checked
```

</details>

### Write Targets
| File | Action |
|------|--------|
| `docs/paper/latex/` | EDIT — revision changes from advisor feedback |
| `docs/paper/number_verification_log.md` | CREATE — number-to-source verification |
| `docs/paper/submission_record.md` | CREATE — submission metadata |
| `docs/paper/parbench_sc26_final_[DATE].pdf` | CREATE — archived final PDF |

### Read Targets
| File | Purpose |
|------|---------|
| `docs/paper/latex/main.tex` + sections | The paper source |
| `docs/paper/latex/main.pdf` | Compiled output for review |
| `results/evaluation/eval_summary.json` | Ground truth for number audit |
| Anonymous repo (external) | Leak verification |

### Human-in-the-Loop Steps (Samyak must do these)
1. Send PDF to Gal and collect feedback
2. Triage feedback into CRITICAL / IMPORTANT / NICE-TO-HAVE
3. Authenticate with SC26 submission portal
4. Click SUBMIT
5. Forward confirmation email

### Estimated Duration
- Pre-review audit: 2 hours
- Waiting for Gal's feedback: 1-3 days (parallel with other work)
- Revision cycle 1: 4-8 hours
- Revision cycle 2: 2-4 hours
- Revision cycle 3 + final submit: 2-3 hours
- **Total active work:** ~12-18 hours across 2-3 days
- **Calendar time:** 5-7 days (includes advisor review turnaround)
