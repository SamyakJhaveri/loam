# ParBench SC26 Sprint — Session Prompts

> **How to use:** Copy-paste one prompt per Claude Code session. Run `/clear` between sessions.
> Each prompt is self-contained with full context, exact commands, and verification steps.
> Today's date: 2026-03-23 (Day 7 audit updated: 2026-03-24). Deadline: April 8, 2026. Day 7 of 21-day sprint.
> **URGENT (Gal, 2026-03-23): "finish those ASAP, we need the draft of the paper by the end of this week."**
> **Models decided (Gal, 2026-03-23): GPT-4.1 · Claude Sonnet 4.6 · Gemini 2.5 Flash-Lite · Llama 3.3 70B**

---

## Agent Delegation Quick Reference

Each session should delegate mechanical heavy-lifting to agents, keeping the main context
for decisions and fixes. Invoke agents by saying: "Use the {agent-name} agent to..."
or via @-mention: `@agent-{name}`.

| Session | Agent to use | For what |
|---------|-------------|----------|
| S1 | `rodinia-verifier` | Step 7 — run all 54 harness checks, collect PASS/FAIL table |
| S1.5 | `plan-reviewer` | Pre-implementation — adversarial review of kernel-centric architecture |
| S1.5 | `verify-app` | Post-implementation — schema validation + all spec integrity |
| S1.5 | `spec-auditor` | Post-population — validate all 60 specs with new `translation_targets` fields |
| S1.6 | `verify-app` | Post-implementation — schema validation after universal standardization |
| S1.6 | `spec-auditor` | Post-population — validate all 180 specs with translation_targets |
| S2 | `eval-batcher` (background) | Step 3 — run all 17 azure-gpt-4.1 cuda-to-omp kernels (clean slate) |
| S3 | `eval-batcher` (background) | Step 3 — run 17 kernels for groq-llama ✅ DONE; S3b needed for claude-sonnet-4-6 + gemini-2.5-flash-lite |
| S4 | `xsbench-explorer` | Steps 2-4 — read XSBench Makefiles/source, extract spec data |
| S4 | `spec-auditor` | Step 8 — validate all 5 new XSBench spec files |
| S5 | `verify-app` | Post-build — schema validation + spec integrity check |
| S6.5 | `plan-reviewer` | Before implementing — adversarial review of runner.py + schema changes |
| S6.5 | `verify-app` | After schema edits — confirm no new validation errors |
| S7 | `eval-batcher` (background) | Steps 2-3 — L1/L2 augmented eval for all 4 models |
| S9 | `eval-batcher` (background) | Step 2 — omp-to-cuda for 16 eligible kernels × 4 models |
| S10 | `eval-batcher` (background) | Step 1-5 — cuda-to-opencl for 17 kernels × 4 models |
| S10b | `eval-batcher` (background) | Steps 1-3 — opencl-to-cuda, opencl-to-omp, omp-to-opencl × 4 models |
| S-HeCBench | `verify-app` + `eval-batcher` | Step 2 — smoke test 5+ kernels; Step 4 — eval batch background run |
| S11 | `dashboard-refresher` | Steps 2-4 — regenerate JS data + fix stale HTML numbers |
| S12-S15 | `paper-drafter` | Paper section writing with actual data from results files |
| Any | `plan-reviewer` | Before any architecture change — adversarial pre-implementation review |
| Any | `verify-app` | Before any commit — validates project health |
| **W-S16** | `explorer` | Step 1 — audit files containing author names before sanitization |
| **W-S14** | `paper-drafter` | Figures F2-F6 spec review from paper_outline.md before generating |
| **W-S11** | `dashboard-refresher` | **DONE (2026-03-25)** — 12 viz files refreshed, all numbers verified |
| **W-S12-PARTIAL** | `paper-drafter` (Opus) | Write §3-§5 from outline + code + data files |
| **W-S15** | `paper-drafter` + `self-critic` | Data accuracy review + adversarial anti-rationalization |
| **W-S17** | `explorer` | Understand paper_draft.md structure before LaTeX conversion |

**eval-batcher runs in the background** (`background: true`). Start it, then continue other work in the main session. You'll be notified when it completes.

**Worktree sessions (W-S*)** run in isolated git worktrees via `git worktree add`. See WORKTREE PARALLELIZATION GUIDE below for setup instructions.

---

## WORKTREE PARALLELIZATION GUIDE

> **14 days remain. 15 sessions to complete. Parallelization is the only way to make April 8.**
> This guide maps every remaining session into one of three concurrent execution lanes
> and provides complete, self-contained prompts for work that can be delegated to autonomous
> Claude Code agents running in isolated git worktrees.

### The Fundamental Constraint

Git worktrees do **not** initialize git submodules. The `rodinia/rodinia-src/` directory will be
**completely empty** in any worktree — no Makefiles, no source files, no binaries. Additionally,
gitignored directories (`xsbench/xsbench-src/`, `HeCBench-master/`) are absent from worktrees.

**This single constraint determines which sessions can use worktrees:**
- Sessions that call `python3 -m harness verify` or `run_eval_batch.py` → **main checkout only**
- Sessions that only read `results/evaluation/` and write to `docs/paper/` or `visualizations/` → **worktree safe**

### Session Classification

| Session | Lane | Worktree? | Why | Autonomous? |
|---------|------|:---------:|-----|:-----------:|
| **S7** Augmented Eval L1/L2 | GPU-eval | NO | Needs Rodinia submodule + GPU | YES (tmux) |
| **S8** XSBench Multi-API Eval | GPU-eval | NO | Needs XSBench source + GPU | YES (tmux) |
| **S9** omp-to-cuda | GPU-eval | NO | Needs Rodinia submodule + GPU | YES (tmux) |
| **S10** cuda-to-opencl | GPU-eval | NO | Needs Rodinia submodule + GPU | YES (tmux) |
| **S10b** Remaining 3 directions | GPU-eval | NO | Needs Rodinia submodule + GPU | YES (tmux) |
| **S-HeCBench** Clone + Eval | GPU-eval | NO | Needs GPU; HeCBench clone in main | PARTIAL |
| **S6.5** Timing Infrastructure | Supervised | NO | Needs Rodinia + GPU; architecture decision | NO |
| **W-S16** Anonymous GitHub Repo | Worktree | **YES** | Creates separate repo; no main repo changes | **YES** |
| **W-S14** Publication Figures | Worktree | **YES** | Reads `results/`, creates `docs/paper/figures/` | **YES** |
| **W-S11** Dashboard Refresh | Worktree | **YES** | Reads `results/`, edits `visualizations/` | **MOSTLY** |
| **W-S12-PARTIAL** Paper §3–§5 | Worktree | **YES** | Reads `specs/` + `results/`, creates `docs/paper/` | **MOSTLY** |
| **W-S17** LaTeX Transfer | Worktree | **YES** | Reads `docs/paper/`, creates `docs/paper/*.tex` | **YES** |
| **W-S15** Paper Review & Polish | Worktree | **YES** | Reads/edits `docs/paper/`, reads `results/` | **YES** |
| **S12** Paper §1–§2 | Supervised | NO | Requires Paraval paper reading (M3) + research judgment | NO |
| **S13** Paper §6–§8 | Supervised | NO | Requires interpreting results + threats to validity | NO |
| **S18** Final Review + Submit | Supervised | NO | Co-author sign-off; non-delegable | NO |

### 3-Lane Execution Strategy

```
LANE 1: GPU Eval (main checkout, run in tmux — autonomous)
  S8 → S7 → S9 → S10 → S10b → S-HeCBench
  Rule: ONE Rodinia eval at a time (llm_evaluate.py has no file locking in rodinia-src/)
  Exception: S8 (XSBench source tree) can run alongside a Rodinia eval

LANE 2: Writing + Viz (worktree agents — fully autonomous)
  W-S16 + W-S14  (parallel, no overlap)
  → W-S11 (after S7 results arrive)
  → W-S12-PARTIAL (after W-S11 or concurrently)
  → W-S17 (after S13 complete)
  → W-S15 (after S13 complete, ideally after Gal review)

LANE 3: Research Judgment (Samyak — cannot be delegated)
  Read Paraval paper (M3) → Write §1-§2 (S12) → Interpret results (S13) → Final review (S18)
  Dependency: M3 is the #1 blocker — it gates §2 Related Work and the positioning argument
```

### Day-by-Day Schedule (Days 8–19)

| Day | Date | Lane 1 (GPU tmux) | Lane 2 (Worktree) | Lane 3 (Samyak) |
|-----|------|-------------------|-------------------|-----------------|
| 8 | Mar 25 | Launch S8 (XSBench, 1-2h), then S7 (L1/L2, 4-6h) | Launch W-S16 + W-S14 in separate worktrees | Read Paraval paper (M3) — 2h |
| 9 | Mar 26 | S7 continues / completes | Launch W-S12-PARTIAL | Write §1 Introduction with S12 |
| 10 | Mar 27 | Launch S9 (omp-to-cuda, 2-4h) | ~~W-S11~~ DONE (Mar 25); merge branch | Write §2 Related Work |
| 11 | Mar 28 | Launch S10 (cuda-to-opencl, 3-5h) | Merge W-S16, W-S14 branches | Review S9 results; plan §6 |
| 12 | Mar 29 | Launch S10b (3 directions, 6-10h) | Merge W-S12-PARTIAL; W-S11 | Start S13 (§6-§8 results) |
| 13 | Mar 30 | S-HeCBench clone + smoke-test (supervised) | Regenerate W-S14 figures with full data | S13 continues |
| 14 | Mar 31 | S-HeCBench eval batch (autonomous) | Launch W-S15 (needs S13 complete) | Review paper draft |
| 15 | Apr 1 | Buffer / any failed reruns | Launch W-S17 (after W-S15) | Final number verification |
| 16-17 | Apr 2-3 | — | Merge all worktrees | Deep paper review |
| 18-21 | Apr 4-8 | — | — | S18: co-author review + submit |

### GPU Sequencing Rules

`llm_evaluate.py` backs up and restores files inside `rodinia/rodinia-src/` with no file
locking. Two concurrent Rodinia evals will corrupt each other's backup/restore cycle.

**Safe to run simultaneously:**
- Any worktree agent + any GPU eval (disjoint directories)
- S8 (XSBench in `xsbench/xsbench-src/`) + any Rodinia eval (S7/S9/S10/S10b)

**Must be sequential (one at a time):**
- S7, S9, S10, S10b — all write into Rodinia `openmp/`, `cuda/`, `opencl/` subdirectories
- Note: S9 writes translated CUDA output to `cuda/` dirs; S10 reads from those same dirs as source — always run S9 to completion before S10

**Recommended order:** S8 first (fastest, different source) → S7 (L1/L2 augmentation) → S9 (omp-to-cuda) → S10 (cuda-to-opencl) → S10b (3 remaining)

### How to Launch a Worktree Session

```bash
# Create a new worktree (from main checkout)
cd /home/samyak/Desktop/parbench_sam
git worktree add ../parbench_wt_s14 -b worktree/s14-figures

# Start Claude Code pointing at the worktree
claude --project-dir ../parbench_wt_s14

# Paste the W-S14 prompt from this file into that Claude Code session

# When the agent finishes and commits:
git worktree remove ../parbench_wt_s14
git merge --no-ff worktree/s14-figures -m "Merge W-S14: publication figures"
git branch -d worktree/s14-figures
```

**Key worktree facts for agent orientation:**
- The venv `env_parbench/` is present and usable (not gitignored)
- `results/evaluation/` data is fully present (tracked files from branch point)
- `specs/`, `docs/`, `scripts/`, `harness/`, `c_augmentation/` are all fully present
- `rodinia/rodinia-src/` directory structure exists but all files are ABSENT (submodule empty)
- `xsbench/xsbench-src/` and `HeCBench-master/` are ABSENT (gitignored)
- `--project-root /path/to/worktree` must be passed to any script that uses it

### File Conflict Map (no write-write conflicts between lanes)

| Directory | GPU evals (S7-S10b) | S-HeCBench | W-S11 | W-S12/S13/S15 | W-S14 | W-S17 |
|-----------|:------------------:|:----------:|:-----:|:-------------:|:-----:|:-----:|
| `results/evaluation/` | **WRITE** | **WRITE** | READ | READ | READ | — |
| `rodinia/rodinia-src/` | **WRITE** | — | — | — | — | — |
| `visualizations/` | — | — | **WRITE** | — | **WRITE**(figs) | — |
| `docs/paper/` | — | — | — | **WRITE** | **WRITE** | **WRITE** |
| `specs/` | — | **WRITE** (fixes) | — | READ | READ | — |

No lane writes to another lane's output directory. Worktree merges will be conflict-free.

---

---

## SPRINT-WIDE PREREQUISITES

Before starting any session, resolve these cross-cutting blockers. Each entry shows which sessions are affected.

### CRITICAL — Blocks 5+ sessions

1. **Model selection** ✅ RESOLVED (Gal, 2026-03-23) — 4 models, all L0 cuda-to-omp baselines COMPLETE (2026-03-24):
   - `azure-gpt-4.1` — Azure OpenAI — **DONE (S2):** 9/17 PASS (52.9%)
   - `claude-sonnet-4-6` — Anthropic API — **DONE (S3b, commit 887d681):** 12/17 PASS (70.6%)
   - `gemini-2.5-flash-lite` — Google AI API — **DONE (S3b, commit f0b4f98):** 4/17 PASS (23.5%)
   - `groq-llama-3.3-70b-versatile` — Groq API — **DONE (S3):** 5/17 PASS (29.4%)
   - **S3b COMPLETE** — 4-model L0 cuda-to-omp matrix is done. 68 total results in eval_summary.json.

1b. **Gemini 2.5 Flash-Lite provider implementation** — ✅ **RESOLVED (Session 3b, 2026-03-24, commit 887d681)**
   - Implemented in `scripts/evaluation/llm_evaluate.py` — uses Google's OpenAI-compatible endpoint
   - `GEMINI_API_KEY` env var (falls back to `GOOGLE_API_KEY`)
   - `gemini-2.5-flash-lite` in `MODEL_REGISTRY` with appropriate parameters
   - Tested: 4/17 PASS (23.5%) in Session 3b. Provider is stable and operational.
   - **All downstream sessions (S7, S8, S9, S10, S10b) are unblocked for Gemini.**

2. **Session 1 + Session 1.5 + Session 1.6 completion** — ~~Blocks S2, S3, S7, S8, S9, S10~~ ALL RESOLVED
   - These were the true starting gate for ALL evaluation work — **ALL THREE ARE NOW COMPLETE**
   - S1 = Rodinia submodule reset (source edits → build flags) — DONE (commit `cfa1991`)
   - S1.5 = Kernel-centric pipeline + translation_targets for 60 Rodinia specs — DONE (commit `c2b63fd`)
   - S1.6 = Universal standardization: all 180 specs have translation_targets, full_project fallback removed — DONE (commit `35b9c8e`)
   - **Pipeline is now kernel_centric only. All evaluation sessions are unblocked.**

### HIGH PRIORITY — Blocks paper quality

3. **Read Paraval paper (M3)** — Blocks S6 (outline) and S12 (related work quality)
   - ~2 hours of reading. Cannot write related work section without understanding it.
   - Status: Task M3 in sprint plan, priority HIGH, status unknown

4. **SC26 CFP confirmation** — Blocks S16, S17, S18
   - Need: paper track (full paper vs workshop), LaTeX template, deadline timezone
   - Sprint plan Open Question #5 is still unresolved

5. **Overleaf project** — Blocks S17
   - Ask Erel: has the Overleaf project been created? Get the share link.
   - Sprint plan Open Question #6 is still unresolved

### MEDIUM PRIORITY — Affects paper scope

6. **HeCBench scope decision** — Sprint plan includes it; no session prompt exists
   - Decision: Is HeCBench in scope for SC26 paper evaluation, or "curated but pending"?

7. **M6 timing metrics** — Session prompt written (SESSION 6.5); not yet implemented
   - SESSION 6.5 implements nsys profiler integration for Tier 1 kernel time (CUDA + OMP-target)
   - Decision: Use kernel_time_seconds for speedup claims per Niranjan's directive (2026-03-17)
   - After S6.5: re-run eval batches in S7/S9/S10 with --use-profiler to get valid speedups

8. **Translation direction scope** — Now documented in the Translation Direction Matrix below
   - Directions 1-6 (non-omp_target): 16-78 eligible kernels each — in scope for paper
   - Directions 7-10 (omp_target): 1 kernel each (XSBench only) — case study scope in S8
   - OpenACC: DESCOPED — no openacc spec exists in any suite (XSBench has 4 APIs: cuda/omp/opencl/omp_target only)
   - Decision NEEDED: Should Session 10b (3 new Rodinia directions) run BEFORE paper writing (S12-S13)?
     Recommendation: yes — complete data produces stronger paper results.

---

## TRANSLATION DIRECTION MATRIX

The eval pipeline (`run_eval_batch.py --direction SRC-to-TGT`) is **direction-agnostic** —
any `SRC-to-TGT` string works if matching specs exist. No code changes needed for any direction.
Eligible kernel counts exclude KNOWN_FAIL specs (as source or target).

### Tier 1 — Primary Directions (Rodinia + HeCBench + XSBench)

| # | Direction | Rodinia | HeCBench | XSBench | Total | Session | Status |
|---|-----------|---------|----------|---------|-------|---------|--------|
| 1 | `cuda-to-omp` | 17 | 60 | 1 | **78** | S2/S3/S3b/S7 | **L0 DONE (4 models, 68 results)**; L1/L2 pending S7 |
| 2 | `omp-to-cuda` | 16 | 60 | 1 | **77** | S9 | TBD |

> HeCBench has CUDA + OMP specs only (60 each) — it contributes to Tier 1 directions only.

### Tier 2 — Cross-API Directions (Rodinia + XSBench only)

| # | Direction | Rodinia | HeCBench | XSBench | Total | Session | Status |
|---|-----------|---------|----------|---------|-------|---------|--------|
| 3 | `cuda-to-opencl` | 18 | 0 | 1 | **19** | S10 | TBD |
| 4 | `opencl-to-cuda` | 17 | 0 | 1 | **18** | S10b | NOT STARTED |
| 5 | `opencl-to-omp` | 15 | 0 | 1 | **16** | S10b | NOT STARTED |
| 6 | `omp-to-opencl` | 15 | 0 | 1 | **16** | S10b | NOT STARTED |

> HeCBench has no OpenCL specs — Tier 2 directions are Rodinia + XSBench only.

### Tier 3 — OMP-Target Directions (XSBench only — case study)

| # | Direction | Rodinia | HeCBench | XSBench | Total | Session | Status |
|---|-----------|---------|----------|---------|-------|---------|--------|
| 7 | `cuda-to-omp_target` | 0 | 0 | 1 | **1** | S8 | TBD |
| 8 | `omp_target-to-cuda` | 0 | 0 | 1 | **1** | S8 | TBD |
| 9 | `omp_target-to-opencl` | 0 | 0 | 1 | **1** | S8 | TBD |
| 10 | `opencl-to-omp_target` | 0 | 0 | 1 | **1** | S8 | TBD |

> No Rodinia or HeCBench omp_target specs exist. Tier 3 = XSBench case studies only (N=1 kernel per direction).

### KNOWN_FAIL Exclusions (per direction)

| Spec | API | Excluded from (as target) | Excluded from (as source) |
|------|-----|---------------------------|---------------------------|
| `rodinia-kmeans-cuda` | cuda | omp-to-cuda, opencl-to-cuda | — |
| `rodinia-mummergpu-cuda` | cuda | omp-to-cuda, opencl-to-cuda | — |
| `rodinia-hybridsort-cuda` | cuda | omp-to-cuda, opencl-to-cuda | — |
| `rodinia-mummergpu-omp` | omp | cuda-to-omp, opencl-to-omp | omp-to-cuda, omp-to-opencl |
| `rodinia-kmeans-opencl` | opencl | cuda-to-opencl, omp-to-opencl | opencl-to-cuda, opencl-to-omp |
| `rodinia-nn-opencl` | opencl | cuda-to-opencl, omp-to-opencl | opencl-to-cuda, opencl-to-omp |

### Pipeline Command

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction SRC-to-TGT \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v
```

Replace `SRC-to-TGT` with any of the 10 directions above. For Tier 3, use `--suite xsbench`.
Note: `gemini-2.5-flash-lite` requires Gemini provider implementation in `llm_evaluate.py` first (see Prerequisite #1b).

### Paper Scope Recommendation

- **Tier 1-2 (directions 1-6):** Quantitative results — sufficient kernel counts for statistical claims
- **Tier 3 (directions 7-10):** Case study — frame as "XSBench multi-API case study" in §6.6 and §4
- **OpenACC:** DESCOPED — no openacc spec exists in any suite

---

## SESSION 1 — Rodinia Submodule Reset & Re-verification

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Confirm you want to push directly to origin main after this session
- [ ] The -std=c++14 approach for cfd-opencl and pathfinder-opencl is UNTESTED.
      The cfd-opencl spec already has -std=c++14 in its build command AND a source
      edit was still applied — suggesting -std=c++14 alone may not suffice.
      Decision: If -std=c++14 doesn't fix the build after reverting source edits,
      should cfd-opencl move to KNOWN_FAIL (56→55 target) or keep the source edit
      as a documented exception?

EXTERNAL DEPS:
- [ ] No external deps — this session is self-contained on the GPU machine

# Session Goal
Reset the Rodinia git submodule to pristine state (commit 9c10d3ea), re-apply ONLY
Makefile/config patches (no source code edits), fix 2 specs that previously relied on
source edits by using build-flag alternatives instead, then re-verify all 54 PASS specs.

# Why This Matters
The Rodinia submodule has 4 source code edits that violate our "no benchmark source edits"
rule. Two of those (opencl/cfd/euler3d.cpp and opencl/pathfinder/main.cpp) affect specs in
the 54-PASS evaluation set. For SC26 paper integrity, we need unmodified benchmark source
code. The fix is to use `-std=c++14` in build commands instead of editing source files.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Rodinia submodule: /home/samyak/Desktop/parbench_sam/rodinia (pinned at commit 9c10d3ea)
- The submodule has `ignore = dirty` in .gitmodules, so parent repo hides changes
- All current patches are documented in docs/rodinia_toolchain_patches.diff
- The protect-benchmark-sources hook at .claude/hooks/protect-benchmark-sources.sh has a
  blind spot: regex matches /rodinia-src/ but not /rodinia/

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate

# Step 2: Save current state for reference
cd /home/samyak/Desktop/parbench_sam/rodinia
git diff > /tmp/rodinia_current_patches_backup.diff
git diff --stat  # Should show 13 files modified

# Step 3: Full submodule reset
cd /home/samyak/Desktop/parbench_sam/rodinia
git checkout .
git clean -fd  # Remove build artifacts (binaries, obj dirs)

# Verify: git diff should now be empty, git status should show clean working tree

# Step 4: Re-apply ONLY the 9 Makefile/config patches (NOT the 4 source edits)
# The 9 safe patches are:
#   1. common/make.config — CUDA_DIR, OPENCL paths for HPC SDK 24.3
#   2. cuda/cfd/Makefile — compute_20 → compute_89, sm_20 → sm_89
#   3. cuda/lavaMD/makefile — CUDA lib path
#   4. cuda/lud/cuda/Makefile — sm_20 → sm_89
#   5. cuda/particlefilter/Makefile — sm_13 → sm_89
#   6. opencl/heartwall/Makefile — add $(OCL_INC_DIR)
#   7. opencl/hybridsort/Makefile — add -fcommon
#   8. opencl/lavaMD/Makefile — add $(OCL_INC)
#   9. opencl/myocyte/Makefile — add -I$(OPENCL_INC)
#
# DO NOT re-apply these 4 source edits:
#   - cuda/mummergpu/src/suffix-tree.cpp (unistd.h — KNOWN_FAIL anyway)
#   - openmp/mummergpu/src/suffix-tree.cpp (unistd.h — KNOWN_FAIL anyway)
#   - opencl/cfd/euler3d.cpp (if(file==NULL) — will use build flag instead)
#   - opencl/pathfinder/main.cpp (data→grid_data — will use build flag instead)
#
# Read docs/rodinia_toolchain_patches.diff to see the exact changes for each Makefile,
# then apply them manually using Edit tool. Only touch Makefiles and make.config.

# Step 5: Fix the 2 PASS-set specs with build-flag alternatives
#
# For specs/rodinia-cfd-opencl.json:
#   The original source edit was: if(file==NULL) → if(!file) in euler3d.cpp
#   Fix: Add -std=c++14 to the FLAGS in the spec's build command.
#   Read the spec first to see the current build command, then add -std=c++14.
#   With C++14, `if(file==NULL)` compiles fine (no C++17 strict comparison).
#
# For specs/rodinia-pathfinder-opencl.json:
#   The original source edit was: global `int* data` renamed to `int* grid_data`
#   Fix: Add -std=c++14 to CXXFLAGS in the spec's build command.
#   With C++14, there's no std::data() in scope, so `data` doesn't conflict.
#   Read the spec first to see the current build command, then add -std=c++14.

# Step 6: Fix the hook blind spot
# Edit .claude/hooks/protect-benchmark-sources.sh
# Change: BENCHMARK_DIRS_RE='/(rodinia-src|HeCBench-master|hecbench)/'
# To:     BENCHMARK_DIRS_RE='/(rodinia|rodinia-src|HeCBench-master|hecbench)/'

# Step 7: Verify — Re-run all 54 previously-PASS specs
# The 54 PASS specs are all 60 Rodinia specs MINUS the 6 KNOWN_FAIL:
#   KNOWN_FAIL: kmeans-cuda, kmeans-opencl, nn-opencl, hybridsort-cuda,
#               mummergpu-cuda, mummergpu-omp
#
# Write a small test script that runs harness verify on each of the 54 specs
# and collects pass/fail counts. Example:
#
#   python3 -m harness --json verify specs/rodinia-bfs-cuda.json --config correctness
#
# Run ALL 54 specs. Count PASS vs FAIL. Expected: 54 PASS, 0 FAIL.
# If any fail, investigate and fix the build command in the spec (NOT the source).
#
# IMPORTANT: After verification succeeds, DELETE the test script.

# Step 8: Also verify the 6 KNOWN_FAIL specs still fail as expected
# Run them and confirm they still produce BUILD_FAIL or FAIL. Do NOT try to fix them.

# Step 9: Update docs/rodinia_toolchain_patches.diff with the new (Makefile-only) diff
cd /home/samyak/Desktop/parbench_sam/rodinia
git diff > /home/samyak/Desktop/parbench_sam/docs/rodinia_toolchain_patches.diff

# Step 10: Verify git diff shows ONLY Makefile/config files
cd /home/samyak/Desktop/parbench_sam/rodinia
git diff --name-only
# Expected: Only .config and Makefile files. NO .cpp, .cu, .c files.

# Step 11: Update known-issues.md
# Update the relevant sections to reflect that source edits have been reverted
# and build-flag alternatives are used instead.

# Step 12: Show me the results summary (PASS/FAIL counts for all 60 specs)
# Then git add and commit:
#   - specs/rodinia-cfd-opencl.json (build flag change)
#   - specs/rodinia-pathfinder-opencl.json (build flag change)
#   - .claude/hooks/protect-benchmark-sources.sh (hook fix)
#   - docs/rodinia_toolchain_patches.diff (updated)
#   - .claude/rules/known-issues.md (updated)
# Commit message: "Revert Rodinia source edits; use build-flag alternatives for C++14 compat"
# Then push to origin main.
```

---

## SESSION 1.5 — Implement Kernel-Centric Translation Pipeline (M11-IMPL)

> **STATUS: COMPLETE** -- Commit `c2b63fd` (2026-03-22). Implemented kernel-centric
> translation for Rodinia: schema changes (`translation_targets`, `translation_complexity`),
> eval pipeline with fallback mode, all 60 Rodinia specs populated, 10 spec bloat fixes,
> complexity classification CSV (230 pairs).
> NOTE: `populate_translation_targets.py` was DELETED in Session 1.6 and replaced by
> `scripts/generators/standardize_specs.py`. The `full_project` fallback was also removed in Session 1.6.

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Approve spec bloat fixes: moving non-kernel files from prompt_payload to
      support_files for 10 specs (kmeans-omp, streamcluster-omp, lud-omp, cfd-omp,
      nn-omp, bfs-opencl, hotspot-opencl, hotspot3d-opencl, pathfinder-opencl,
      lud-opencl). This changes what the LLM sees as "source to translate."
- [ ] The architecture doc has NO source-verified translation_targets for CUDA
      specs (22 specs). The prompt says "CUDA targets use translation_targets =
      prompt_payload in most cases." Confirm: is fallback to prompt_payload
      acceptable for CUDA specs, or should each be source-verified first?
- [ ] 12 OpenCL specs have best-guess (not source-verified) translation_targets.
      Claude Code CAN verify these by reading Makefiles during the session.
      Confirm: is this acceptable, or do you want to verify them manually first?
- [ ] Confirm you want to push directly to origin main after this session

EXTERNAL DEPS:
- [ ] Session 1 must be complete (submodule reset, 54 PASS specs verified)

# Session Goal
Implement the kernel-centric translation paradigm in the ParBench LLM evaluation
pipeline. This changes HOW translation evaluation works: instead of asking the LLM to
produce ALL target files, we ask it to produce only the kernel computation file(s).
Target infrastructure (Makefile, headers, utilities) stays untouched.

# Why This Matters
Team decision (Erkap + Niranjan, 2026-03-22): test pure translation skill, not project
restructuring. This resolves design blocker M11 that caused 3/4 BUILD_FAILs in the
Phase 1 pilot. Expected improvement: 60% → 75-80% pass rate.
Architecture doc: docs/design/kernel_centric_translation.md

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Design doc: docs/design/kernel_centric_translation.md (READ THIS FIRST — full spec)
- Design concern (resolved): docs/design_concern_multifile_translation.md
- Eval pipeline: scripts/evaluation/llm_evaluate.py
- Spec loader: harness/spec_loader.py
- Schema: schema/spec_schema.json
- Validator: scripts/validate_schema.py

# Prerequisites
- Session 1 complete (Rodinia submodule reset, all 54 specs verified PASS)

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Read the architecture doc FULLY
# Read docs/design/kernel_centric_translation.md completely before writing any code.
# It contains source-verified translation_targets values for all 60 Rodinia specs,
# the pipeline code changes with exact line numbers, the complexity taxonomy, and
# the spec bloat table.
# CRITICAL: backprop-omp kernel file is backprop.c (NOT backprop_kernel.c).
#           backprop_kernel.c is the orchestrator with NO OMP pragmas.

# Step 3: Schema changes (schema/spec_schema.json)
# Add to the "files" object definition:
#   "translation_targets": optional array of strings
# Add to the "metadata" object definition:
#   "translation_complexity": optional enum:
#     ["single_file", "multi_to_single", "single_to_multi", "multi_to_multi"]
# Run: python3 scripts/validate_schema.py --all
# Expected: same ~135 known errors. No new errors (field is optional, backward compatible).

# Step 4: Validator changes (scripts/validate_schema.py)
# Add check: if translation_targets exists, every entry must be in prompt_payload.
# This prevents specifying a target file that was moved to support_files.
# Run: python3 scripts/validate_schema.py --all

# Step 5: Spec loader (harness/spec_loader.py)
# In resolve_paths(): add translation_targets to the resolved files dict.
# Resolve paths relative to source_path the same way prompt_payload is resolved.
# No changes to get_prompt_payload() — source reading is unchanged.

# Step 6: Eval pipeline (scripts/evaluation/llm_evaluate.py)
# In build_translation_prompt() (~line 255):
#   BEFORE: target_filenames = target_spec["files"].get("prompt_payload", [])
#   AFTER:  target_filenames = (
#               target_spec["files"].get("translation_targets")
#               or target_spec["files"].get("prompt_payload", [])
#           )
#
# In evaluate_translation() (~line 715): same change.
# Apply the `or {}` guard pattern (see evaluation.md gotcha) for safety:
#   target_filenames = (
#       (target_spec.get("files") or {}).get("translation_targets")
#       or (target_spec.get("files") or {}).get("prompt_payload", [])
#   )
#
# Add "translation_mode" to result JSON:
#   "translation_mode": "kernel_centric" if translation_targets else "full_project"
#
# Add "## Target Infrastructure Context (DO NOT MODIFY — for reference only)" section
# to the prompt (insert after the "Target Files to Produce" section):
#   - Identify non-translation-target files from target spec's prompt_payload
#     (i.e., prompt_payload files NOT in translation_targets)
#   - Also include target spec's support_files headers
#   - Read their content from the target working directory
#   - Include as read-only reference (headers first, then source files, then Makefile)
#   - Section intro text:
#     "These files exist in the target build directory and will NOT be modified.
#      Your translated code must be compatible with these files."

# Step 7: Populate translation_targets for all 60 Rodinia specs
# Create scripts/evaluation/populate_translation_targets.py
# Use the SOURCE-VERIFIED table in docs/design/kernel_centric_translation.md sections 5-6.
# For each spec, add:
#   - files.translation_targets (the verified kernel files)
#   - metadata.translation_complexity (the verified class)
#
# ALSO fix spec bloat (from section 7 of architecture doc):
# Move these files from prompt_payload to support_files:
#   - kmeans-omp: 4 kmeans_serial/ files → support_files
#   - streamcluster-omp: streamcluster_original.cpp → support_files
#   - lud-omp: base/lud.c, base/lud_base.c, tools/gen_input.c → support_files
#   - cfd-omp: 3 variant .cpp files (double, pre_euler3d, pre_euler3d_double) → support_files
#   - nn-omp: hurricane_gen.c → support_files
#   - bfs-opencl: timer.cc → support_files
#   - hotspot-opencl: OpenCL_helper_library.c → support_files
#   - hotspot3d-opencl: CL_helper.c → support_files
#   - pathfinder-opencl: OpenCL.cpp → support_files
#   - lud-opencl: base/lud.c, base/lud_base.c, tools/gen_input.c → support_files
#
# The architecture doc (section 6) lists 8 explicitly source-verified OpenCL specs:
#   bfs, cfd, hotspot, hotspot3d, lud, nw, pathfinder, srad
# The remaining 12 OpenCL specs (not yet source-verified in the doc) should follow
# the default pattern: .cl device kernel + host .cpp → translation_targets.
# Helper .c/.cc utilities → support_files.
#
# REMAINING 12 OpenCL specs — apply default pattern, verify Makefile before committing:
#   backprop-opencl:       backprop_kernel.cl + backprop.cpp → translation_targets
#   bptree-opencl:         kernel.cl + main.cpp → translation_targets
#   dwt2d-opencl:          dwt.cl + dwt2d.cpp → translation_targets
#   gaussian-opencl:       gaussianElim.cl + gaussianElim.cpp → translation_targets
#   heartwall-opencl:      kernel.cl + main.cpp → translation_targets
#   hybridsort-opencl:     bucketsort.cl + mergesort.cl + main.cpp → translation_targets
#   kmeans-opencl:         kmeans.cl + kmeans.cpp → translation_targets  [KNOWN_FAIL — still populate]
#   lavamd-opencl:         kernel.cl + main.cpp → translation_targets
#   myocyte-opencl:        kernel.cl + main.cpp → translation_targets
#   nn-opencl:             nearestNeighbor_kernel.cl + nearestNeighbor.cpp → translation_targets  [KNOWN_FAIL — still populate]
#   particlefilter-opencl: particle_double.cl + ex_particle_OPENMP_seq.c → translation_targets
#   streamcluster-opencl:  streamcluster.cl + streamcluster.cpp → translation_targets
#
# IMPORTANT: Read each spec's actual prompt_payload list and verify against the
# Rodinia Makefile before finalizing. The filenames above are best-guess from naming
# conventions — the architecture doc's verified 8 show that naming conventions are
# sometimes wrong (e.g. backprop-omp: backprop_kernel.c has NO pragmas).
# For KNOWN_FAIL specs (kmeans-opencl, nn-opencl): populate translation_targets anyway.
# The field should be complete even for KNOWN_FAIL specs; they're excluded from eval
# batches but may be referenced in analysis (complexity classification, paper tables).
#
# Run: python3 scripts/evaluation/populate_translation_targets.py \
#        --project-root /home/samyak/Desktop/parbench_sam
# Then: python3 scripts/validate_schema.py --all

# Step 8: Classification script
# Create scripts/evaluation/classify_translation_pairs.py
# Reads all paired specs (source + target), computes complexity class for each pair.
# Output: results/evaluation/translation_complexity.csv
# Columns: kernel, src_spec, tgt_spec, src_api, tgt_api,
#          src_target_count, tgt_target_count, complexity_class
# (src_target_count = number of files in source spec's translation_targets
#  tgt_target_count = number of files in target spec's translation_targets)
#
# Run: python3 scripts/evaluation/classify_translation_pairs.py \
#        --project-root /home/samyak/Desktop/parbench_sam

# Step 9: Update analyze_eval.py
# Add "Pass Rate by Translation Complexity" section to markdown output.
# Load translation_complexity.csv, enrich result records, group-by complexity class.
# Output format: table of complexity_class × model × pass_rate.

# Step 10: Dry-run verification
# Test prompt generation for key cases. Read the --dry-run output carefully:
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-backprop-cuda.json \
  --target specs/rodinia-backprop-omp.json \
  --model azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run
# Expected: "Target Files to Produce: backprop.c" (was 4 files)
# Expected: "Target Infrastructure Context" section present with backprop.h + Makefile

python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-kmeans-cuda.json \
  --target specs/rodinia-kmeans-omp.json \
  --model azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run
# Expected: "Target Files to Produce: kmeans_openmp/kmeans_clustering.c" (was 8 files)

python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-hotspot-cuda.json \
  --target specs/rodinia-hotspot-opencl.json \
  --model azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run
# Expected: 2 target files: hotspot_kernel.cl + hotspot.c (OpenCL = inherent multi-file)

python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run
# Expected: "Target Files to Produce: bfs.cpp" (single_file — unchanged)

# Step 11: Full schema validation
python3 scripts/validate_schema.py --all
# Expected: ~135 known errors (HeCBench + phantoms). Zero new errors.

# Step 12: Unit tests
python3 -m pytest c_augmentation/test_transforms.py -v
# Expected: all 15 tests pass (transforms unchanged by this session)

# Step 13: Show me:
# - Dry-run prompt for backprop (should show 1 target file + infrastructure context section)
# - Dry-run prompt for kmeans (should show 1 target file)
# - Dry-run prompt for hotspot-opencl (should show 2 target files)
# - classification CSV summary (counts per complexity class per direction)
# - Full validation output

# Step 14: Git commit and push
# Stage all changed files:
#   schema/spec_schema.json
#   scripts/validate_schema.py
#   harness/spec_loader.py
#   scripts/evaluation/llm_evaluate.py
#   scripts/evaluation/populate_translation_targets.py (new)
#   scripts/evaluation/classify_translation_pairs.py (new)
#   scripts/evaluation/analyze_eval.py
#   specs/*.json (all 60 Rodinia specs with translation_targets)
#   results/evaluation/translation_complexity.csv (new)
#   docs/design/kernel_centric_translation.md (already created)
#   docs/design_concern_multifile_translation.md (already updated)
# Commit message:
#   "Implement kernel-centric translation (M11 resolution): translation_targets field,
#    complexity classification, reduced target files for all 60 Rodinia specs"
# Push to origin main.
```

---

## SESSION 1.6 — Standardize Translation Pipeline for All Suites

> **STATUS: COMPLETE** -- Commit `35b9c8e` (2026-03-22). Universal standardization
> of all 180 specs across Rodinia (60) and HeCBench (120). Replaced Rodinia-only
> `populate_translation_targets.py` with `scripts/generators/standardize_specs.py`.
> Removed `full_project` fallback from eval pipeline -- single `kernel_centric` mode.
> Fixed cross-suite bug in `find_translation_pairs()`.

### What was done:
- Created `scripts/generators/standardize_specs.py` (universal, any suite)
- Three API family rules:
  - Family 1 (OpenCL): `translation_targets` = `.cl` files only (host `.cpp` is Target Infrastructure Context)
  - Family 2 (OMP, OMP target, OpenACC): preserve existing curated targets; fallback = `prompt_payload`
  - Family 3 (CUDA and all others): `translation_targets` = `prompt_payload`
- All 180 specs now have `translation_targets` populated (141 updated, 39 already correct)
- Deleted `scripts/generators/populate_translation_targets.py` (Rodinia-only, superseded)
- Removed `by_translation_mode` reporting from `analyze_eval.py` (only one mode exists)
- `translation_mode` is always `"kernel_centric"` in result JSONs -- no fallback
- Fixed cross-suite bug: `find_translation_pairs()` now groups by `(suite, kernel)` to prevent
  merging 7 overlapping kernel names between Rodinia and HeCBench (e.g., `gaussian`, `lud`, `nn`)
- Updated gen-spec skill with Phase 3.5 and architecture doc with section 14

### Impact on downstream sessions:
- **Session 4 (XSBench):** After creating specs, run `standardize_specs.py --suite xsbench` (Step 12 added)
- **Session 8 (XSBench eval):** XSBench translation_targets gap is RESOLVED
- **Session 9 (omp-to-cuda):** CUDA translation_targets = prompt_payload (Family 3 rule) -- no fallback
- **Session 10 (cuda-to-opencl):** OpenCL targets = `.cl` files ONLY, NOT `.cl` + host `.cpp`

---

## SESSION 2 — Complete azure-gpt-4.1 Rodinia cuda-to-omp Evaluation

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Clean slate: ALL 10 previous azure-gpt-4.1 cuda-to-omp results will be
      DELETED before re-running. Git history preserves them. OK to proceed?
      (Alternative: archive to results/evaluation/archive/ first)
- [ ] The untracked file "design issue, please advise.txt" in repo root —
      should it be committed, deleted, or gitignored before this session?
- [ ] Confirm you want to push directly to origin main after this session

DATA/INFO:
- [ ] Confirm Azure deployment name: the code strips "azure-" prefix, so
      "azure-gpt-4.1" becomes deployment name "gpt-4.1". Is your Azure
      deployment named exactly "gpt-4.1"? (If different, provide the name)

CLARIFICATIONS:
- [ ] --max-retries 2 is used here. Sprint plan Task 2A planned --max-retries 3
      for iterative repair testing. Is 2 intentional for the clean-slate run?

EXTERNAL DEPS:
- [ ] Session 1 must be complete (submodule reset)
- [x] Session 1.5 must be complete (kernel-centric pipeline + translation_targets) — DONE (commit `c2b63fd`)
- [x] Session 1.6 must be complete (universal standardization, full_project removed) — DONE (commit `35b9c8e`)
      The `full_project` mode no longer exists. Pipeline is `kernel_centric` only.
- [ ] AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set in your shell
      (run: echo $AZURE_OPENAI_API_KEY | head -c5  to verify without exposing)

# Session Goal
Run ALL 17 Rodinia cuda-to-omp translation tasks for azure-gpt-4.1 at L0 using the
kernel-centric pipeline. This is a CLEAN SLATE run — previous v1 results are deleted.

# Why This Matters
Session 1.5 implemented kernel-centric translation (M11 resolution). Previous 10-kernel
pilot results used the full-project paradigm and cannot be mixed with the new pipeline's
results in the paper. Clean slate ensures a single, coherent evaluation paradigm.
Expected improvement: 60% → 75-80% pass rate as structural failures are eliminated.

# IMPORTANT: Kernel-centric translation is the ONLY mode (Sessions 1.5 + 1.6 complete).
# The `full_project` fallback has been removed. Pipeline always uses translation_targets.
# The LLM produces only the kernel file(s), not full project structure.
# - backprop: 4 files → 1 file (backprop.c)
# - kmeans: 8 files → 1 file (kmeans_openmp/kmeans_clustering.c)
# - streamcluster: 2 files → 1 file (streamcluster_omp.cpp)
# - All other kernels: same or reduced file count
#
# CLEAN SLATE: Delete ALL previous full-project-mode results before running:
# rm results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json
# (Team decision: single paradigm for paper, no mixed v1/v2 data)

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Eval pipeline: scripts/evaluation/run_eval_batch.py
- Results dir: results/evaluation/azure-gpt-4.1/
- ALL 17 kernels need fresh evaluation (clean slate, v2 kernel-centric pipeline):
  backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, kmeans, lavamd, lud,
  myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster
- EXCLUDED from eval: mummergpu (KNOWN_FAIL), hybridsort (OMP spec deleted),
  gaussian (OMP spec deleted), huffman (OMP spec deleted), dwt2d (no OMP spec)
- API key env var: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set

# Prerequisites
- Session 1 complete (Rodinia submodule reset, all 54 specs verified PASS)
- Sessions 1.5+1.6 complete (kernel-centric pipeline, all 180 specs populated, single mode)
- Azure OpenAI API key configured

# Step 1: Activate venv and verify environment
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Verify API key is set (don't print the actual key):
python3 -c "import os; assert os.environ.get('AZURE_OPENAI_API_KEY'), 'AZURE_OPENAI_API_KEY not set'"
python3 -c "import os; assert os.environ.get('AZURE_OPENAI_ENDPOINT'), 'AZURE_OPENAI_ENDPOINT not set'"

# Verify translation_targets are populated (kernel-centric pipeline active):
python3 -c "
import json, glob
specs = glob.glob('specs/rodinia-*-omp.json')
missing = [s for s in specs if 'mummergpu' not in s
           and not json.load(open(s)).get('files', {}).get('translation_targets')]
if missing: print('MISSING translation_targets:', missing)
else: print('All OMP specs have translation_targets — pipeline ready')
"
# NOTE: After Session 1.6, all 180 specs have translation_targets.
# This check will always pass. Kept as a sanity check.

# Step 2: DELETE all previous cuda-to-omp v1 results (clean slate)
rm -f results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json
# Verify deletion:
ls results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json 2>&1
# Expected: "No such file or directory"

# Step 3: Run the batch evaluation for ALL 17 kernels (kernel-centric, v2 pipeline)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Step 4: Verify results exist
ls results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json | wc -l
# Expected: 17 result files

# Step 5: Regenerate analysis
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 \
  --expected-directions cuda-to-omp \
  --expected-levels 0

# Step 6: Verification — write a small test script that:
# 1. Reads each result JSON in results/evaluation/azure-gpt-4.1/
# 2. Counts PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL
# 3. Verifies all 17 kernels have results
# 4. Confirms translation_mode="kernel_centric" in all results (the only possible mode after S1.6)
# 5. Prints a summary table
# DELETE the test script after it confirms everything is correct.

# Step 7: Show me the results:
# - Print the full kernel x status table from eval_summary.md
# - Print pass rate for azure-gpt-4.1 cuda-to-omp (v2 kernel-centric)
# - Compare with v1 pilot (60%) — did backprop/kmeans/streamcluster now PASS?
# - Print any new failure patterns discovered
# - Print "Pass Rate by Translation Complexity" table from eval_summary.md

# Step 8: Git commit and push
# Commit the new result files and updated analysis:
#   results/evaluation/azure-gpt-4.1/*.json (17 new v2 files)
#   results/evaluation/eval_summary.json
#   results/evaluation/eval_summary.md
#   results/evaluation/batch_cuda-to-omp_*.json and .md (new batch summary)
#   visualizations/eval_results_data.js (if regenerated)
# Commit message: "azure-gpt-4.1 Rodinia cuda-to-omp eval v2 (17/17 kernels, kernel-centric)"
# Push to origin main.
```

---

## SESSION 3 — Second Model Rodinia cuda-to-omp Evaluation ✅ COMPLETE (2026-03-22)

> **Status: COMPLETE.** groq-llama-3.3-70b-versatile evaluated on 17 kernels (cuda-to-omp,
> L0, max_retries=2). Final: **5/17 PASS (29.4%)**. See SESSION 3-PM below for post-mortem
> fixes and audit results. Commits: `8a848b1` (Groq provider), `b644bc6` (results + Tier 1.5
> extraction fix), `dad1662` (EXTRACTION_FAIL guard, cross-attempt restore, finish_reason).

```
ultrathink

# [Session 3 is COMPLETE — groq-llama-3.3-70b-versatile was used (5/17 PASS)]
# [Model selection is now RESOLVED: see Prerequisite #1 above for all 4 models]

## BEFORE YOU START — [HISTORICAL — session is complete]

DATA/INFO:
- [ ] API key for the chosen provider. Provide the env var name and confirm
      it is set (e.g., GROQ_API_KEY, GOOGLE_API_KEY, MISTRAL_API_KEY)
- [ ] Provider rate limits: Groq free tier = 30 req/min for Llama 70B.
      Do you have a paid Groq account, or should we handle rate limiting?

CLARIFICATIONS:
- [ ] The eval pipeline (llm_evaluate.py) currently only supports 3 providers:
      claude-*, gpt-*/o1-*/o3-*/o4-*, azure-*. Any other model requires NEW
      provider code (~20-30 lines for OpenAI-compatible APIs like Groq/Mistral,
      ~50-80 lines for Google Gemini). Should this be implemented as part of
      Session 3 or as a separate prerequisite session?
- [ ] "No reasoning models" (Gal's constraint). If Gemini is chosen, does
      Gemini 2.0 have reasoning that needs to be explicitly disabled?

EXTERNAL DEPS:
- [x] Sessions 1 + 1.5 + 1.6 must all be complete — DONE
- [ ] Session 2 must be complete
- [ ] M7 (Groq/Modal setup) or equivalent provider setup must be done
- [ ] New provider code must be added to llm_evaluate.py call_llm() function
      if the model is not azure-*, claude-*, or gpt-*

# Session Goal
Run ALL 17 Rodinia cuda-to-omp translation tasks for the second model at L0 using the
kernel-centric pipeline. Model TBD — awaiting M7/M8 decision (llama-70b or leaderboard pick).

# IMPORTANT MODEL NOTE (updated 2026-03-23):
# claude-sonnet-4-20250514 was REMOVED as an eval target at the March 18 meeting.
# However, Gal has RE-ADDED Claude to the model set on 2026-03-23 as claude-sonnet-4-6.
# The new model ID is claude-sonnet-4-6 (not claude-sonnet-4-20250514).
# Historical claude-sonnet-4-20250514 pilot data in results/evaluation/claude-sonnet-4-20250514/
# is NOT reused — claude-sonnet-4-6 is a different model version; run fresh.
#
# Session 3 covered groq-llama-3.3-70b-versatile only (5/17 PASS).
# The 2 new models (claude-sonnet-4-6 and gemini-2.5-flash-lite) need a separate
# cuda-to-omp L0 run — see SESSION 3b below.

# IMPORTANT: Kernel-centric translation is the ONLY mode (Sessions 1.5 + 1.6 complete).
# The LLM produces only the kernel file(s), not full project structure.
# All 17 kernels run as CLEAN SLATE (no previous v2 results for the new model).

# Context [HISTORICAL — Session 3 is COMPLETE, model was groq-llama-3.3-70b-versatile]
- Project root: /home/samyak/Desktop/parbench_sam
- Results dir: results/evaluation/groq-llama-3.3-70b-versatile/
- Model ID used: groq-llama-3.3-70b-versatile (GROQ_API_KEY)
- Eligible kernels (17): backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d,
  kmeans, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster
- EXCLUDED: mummergpu, hybridsort, gaussian, huffman, dwt2d

# Prerequisites
- Session 1 complete (Rodinia submodule reset)
- Sessions 1.5+1.6 complete (kernel-centric pipeline, all 180 specs populated, single mode)
- Session 2 complete (azure-gpt-4.1 v2 baseline established)
- M7 or M8 complete (second model available via API)

# Step 1: Activate venv and verify
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Verify model API key (replace with actual env var name from M7/M8 setup):
# python3 -c "import os; assert os.environ.get('GROQ_API_KEY'), 'GROQ_API_KEY not set'"

# [Session 3 is COMPLETE — groq-llama-3.3-70b-versatile was used; commands shown for reference]
# Step 2: Run batch evaluation
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Step 3: Verify 17 result files exist
ls results/evaluation/groq-llama-3.3-70b-versatile/rodinia-*-cuda-to-rodinia-*-omp.json | wc -l
# Expected: 17

# Step 4: Regenerate analysis with both models (azure-gpt-4.1 + groq-llama)
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp \
  --expected-levels 0

# Step 5: Verification — write a small test script that:
# 1. Loads all cuda-to-omp L0 results for both models
# 2. Prints a kernel x model matrix (PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL)
# 3. Compares the two models' pass rates
# 4. Identifies kernels where models disagree (one passes, other fails)
# 5. Confirms translation_mode="kernel_centric" in all results
# DELETE the test script after verification.

# Step 6: Show me:
# - Complete kernel x model comparison table
# - Pass rates per model (kernel-centric v2 pipeline)
# - Failure taxonomy (what types of failures dominate)
# - "Pass Rate by Translation Complexity" table
# - Any interesting cross-model patterns

# Step 7: Git commit and push
# Commit: results/evaluation/groq-llama-3.3-70b-versatile/*.json, eval_summary.*, batch_*
# Message: "Add groq-llama-3.3-70b-versatile Rodinia cuda-to-omp eval v2 (17/17 kernels, kernel-centric)"
# Push to origin main.
```

---

## SESSION 3b — New Models cuda-to-omp L0 (claude-sonnet-4-6 + gemini-2.5-flash-lite)

> **Status: COMPLETE** — 2026-03-24. claude-sonnet-4-6: 12/17 PASS (commit 887d681).
> gemini-2.5-flash-lite: 4/17 PASS (commit f0b4f98). 4-model matrix complete.
> Failure taxonomy: BUILD_FAIL 26, RUN_FAIL 10, EXTRACTION_FAIL 2 (68 total tasks).

```
ultrathink

# Session Goal
Run cuda-to-omp L0 evaluation for the 2 new models on all 17 eligible Rodinia kernels.
azure-gpt-4.1 (Session 2) and groq-llama-3.3-70b-versatile (Session 3) already have L0 results.
This session fills in claude-sonnet-4-6 and gemini-2.5-flash-lite.

# Prerequisites
- Prerequisite #1b complete: gemini-2.5-flash-lite provider implemented in llm_evaluate.py
- claude-sonnet-4-6 added to MODEL_REGISTRY in llm_evaluate.py
- ANTHROPIC_API_KEY set (for claude-sonnet-4-6)
- GEMINI_API_KEY set (for gemini-2.5-flash-lite)
- Sessions 2 + 3 complete (L0 baselines for azure-gpt-4.1 and groq-llama)

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Verify API keys
python3 -c "import os; assert os.environ.get('ANTHROPIC_API_KEY'), 'ANTHROPIC_API_KEY not set'"
python3 -c "import os; assert os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY'), 'Gemini API key not set'"

# Step 3: Run claude-sonnet-4-6 at L0 (17 kernels, clean slate)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models claude-sonnet-4-6 \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Step 4: Run gemini-2.5-flash-lite at L0 (17 kernels, clean slate)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models gemini-2.5-flash-lite \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Step 5: Regenerate analysis with ALL 4 models
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp \
  --expected-levels 0

# Step 6: Verify 17 result files exist for each new model
ls results/evaluation/claude-sonnet-4-6/rodinia-*-cuda-to-rodinia-*-omp.json | wc -l
ls results/evaluation/gemini-2.5-flash-lite/rodinia-*-cuda-to-rodinia-*-omp.json | wc -l
# Expected: 17 each

# Step 7: Show 4-model comparison table (cuda-to-omp L0 baseline for all models)
# Format: kernel × model matrix (PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL)

# Step 8: Git commit and push
# Commit: results/evaluation/claude-sonnet-4-6/*.json, results/evaluation/gemini-2.5-flash-lite/*.json, eval_summary.*
# Message: "Add claude-sonnet-4-6 + gemini-2.5-flash-lite cuda-to-omp L0 eval (17/17 kernels each)"
# Push to origin main.
```

---

## SESSION 3-PM — Post-Mortem Audit & Pipeline Fixes ✅ COMPLETE (2026-03-22)

> **Not a scheduled session — triggered by SESSION 3 results.**
> An 8-agent adversarial audit of SESSION 3 confirmed results are scientifically valid,
> and identified 3 real pipeline bugs (none changed classifications). All fixed.
> Commits: `dad1662`.

### SESSION 3 Final Results (post all fixes)

| Model | PASS | BUILD_FAIL | RUN_FAIL | EXTRACTION_FAIL | Total |
|-------|------|-----------|---------|-----------------|-------|
| azure-gpt-4.1 | 9 (52.9%) | 4 | 4 | 0 | 17 |
| groq-llama-3.3-70b-versatile | 5 (29.4%) | 10 | 1 | 1 | 17 |

**groq PASS kernels:** bfs, hotspot3d, lud, nn, pathfinder
**azure PASS kernels:** bfs, bptree, cfd, hotspot3d, kmeans, lavamd, lud, nn, pathfinder
**groq PASS ⊆ azure PASS** — strict dominance; groq never outperforms azure on any kernel.

### Audit Verdict: Results Are Valid

The 8-agent audit confirmed 8/10 groq BUILD_FAILs are genuine LLM code quality failures:
- `cfd`: CUDA type `float3` leaked into OMP output
- `nw`: Filename `needle.cpp` echoed literally as code on line 1
- `hotspot`: Variable naming mismatch (`border_rows` vs `borderRows`)
- `backprop`: `#define` macro `MOMENTUM` used in `firstprivate()` OMP clause
- `kmeans`: Non-constant global initializer (`num_threads_perdim * num_threads_perdim`)
- `streamcluster/particlefilter`: Prose/English text emitted as code (hallucination)
- `lavamd/bptree`: Wrong include paths + missing types
- `myocyte`: 10 target files; hit 16384-token completion cap both attempts (stub output)
(heartwall: EXTRACTION_FAIL — separate category; not a BUILD_FAIL)

Prompts are model-agnostic (byte-for-byte identical between models).
Specs unchanged between sessions. Build environment clean.

### Pipeline Bugs Fixed (commit `dad1662`)

**Bug 1 — Cross-attempt file leakage** (`llm_evaluate.py`):
`backup_files()` ran once before the retry loop; between attempts, attempt N's LLM files
persisted on disk when attempt N+1 extracted fewer files. Fix: `restore_files()` +
`backup_files()` called between every retry iteration. Each attempt now starts pristine.

**Bug 2 — EXTRACTION_FAIL status** (`llm_evaluate.py`):
If no target files were extracted from the LLM response, the pipeline would fall through
to build, compiling the reference implementation and producing a false-positive PASS.
Fix: guard added before build — if `extracted == {}`, record `EXTRACTION_FAIL` and send
extraction-specific feedback to the LLM. Heartwall was the affected kernel (groq's 3-file
response format escapes all 4 extraction tiers). Corrected from false PASS → EXTRACTION_FAIL.

**Bug 3 — `finish_reason` not recorded** (`llm_evaluate.py`):
API field (`"stop"` vs `"length"`) was not captured. Detection of token truncation required
comparing `completion_tokens == max_tokens`. Now recorded per attempt in result JSON.
Analysis confirmed: only groq myocyte hits the 16,384 token cap on **both** attempts. groq
heartwall attempt 2 also hit the cap (attempt 1 completed normally at 10,521 tokens). All
other failures are well under the limit — genuine code quality issues, not truncation.

**Also fixed in SESSION 3** (commit `b644bc6`, Tier 1.5 extraction):
Llama 3.3 70B uses `` ```cpp filename.ext `` (space-separated, no `filename=`). Old extractor
missed this format → 5 false-positive PASSes. Tier 1.5 regex added; all 5 kernels re-run.

### Key Findings for SC26 Paper

- **Complexity scaling gap**: Both models equal on `single_file` (66% PASS); gap widens on
  `multi_to_single` (groq 3/11 vs azure 6/11) and `multi_to_multi` (groq 0/3 vs azure 1/3).
- **Token limit irrelevant**: azure-gpt-4.1 has no confirmed truncations (heartwall attempt 1
  hit exactly 16,384 tokens with 1/3 files extracted — likely truncated, but no `finish_reason`
  was recorded pre-fix). groq myocyte is the only kernel token-limited on both attempts.
  Increasing `max_tokens` would not change pass rates for either model.
- **Self-repair**: azure repaired 2 kernels (bptree, nn; 2/9 = 22% of PASSes); groq repaired
  3 kernels (hotspot3d, nn, pathfinder; 3/5 = 60% of PASSes). Only bfs and lud were groq
  first-attempt PASSes. Both models benefit from the error-feedback retry loop — groq relies
  on it more heavily because its first-attempt code quality is lower, but self-correction
  works for both. Groq's ~4/12 failing kernels showed zero change between attempts (hotspot,
  myocyte, nw, srad had identical errors both attempts) — those failures are too fundamental
  for retry to fix. The other 8 failing kernels changed error type on attempt 2 (including
  particlefilter/streamcluster, which regressed from code errors to emitting prose).
- **EXTRACTION_FAIL as a category**: heartwall (groq) shows a real failure mode —
  the model cannot reliably structure multi-file output in a parseable format.

### What SESSION 3-PM Does NOT Change

- Session 7 (augmented eval L1/L2) can proceed on the 5/17 + 9/17 baseline.
- No spec files were modified. All 60 Rodinia specs unchanged.
- The scientific comparison between models is valid for the paper.

---

## SESSION 4 — Clone XSBench & Generate Specs

> Spec generator: `scripts/generators/generate_xsbench_specs.py`.

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] SCOPE MISMATCH: The sprint plan (M5) says "XSBench — specific kernel only
      for Paraval comparison" (MEDIUM priority). But this session prompt treats
      XSBench as a full 5-spec second benchmark suite. Which is it?
      a) Single kernel for Paraval comparison (1 spec, minimal effort)
      b) Full 5-API-variant suite (5 specs, Sessions 4+5+8 needed)
- [ ] Git submodule or regular clone?
      a) Submodule (like Rodinia) — commit pinned in .gitmodules, cleaner
      b) Regular clone + .gitignore entry — simpler, avoids worktree issues
- [ ] Confirm you want to push to origin main (including xsbench-src if submodule,
      or just specs/manifest if clone is gitignored)

DATA/INFO:
- [ ] Confirm XSBench repo URL: https://github.com/ANL-CESAR/XSBench
      (verify this loads in a browser before starting)

EXTERNAL DEPS:
- [ ] Network access on the GPU machine for git clone
- [ ] Independent of Sessions 1-3 (can run in parallel)

# Session Goal
Clone the standalone XSBench repository from ANL-CESAR, explore its directory structure,
and generate 5 spec JSON files (one per API variant: CUDA, OpenMP, OpenCL, OpenMP target,
OpenACC). Append entries to manifest.jsonl and validate.

# Why This Matters
XSBench is our second benchmark suite for the SC26 paper. It has all 5 target APIs
(CUDA, OpenMP, OpenCL, OpenMP target, OpenACC) in one repository — making it ideal
for demonstrating multi-API translation evaluation. Rodinia only has 3 APIs.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- XSBench repo: https://github.com/ANL-CESAR/XSBench
- Directory convention: xsbench/xsbench-src/ (following rodinia/rodinia-src/ pattern)
- XSBench is a Monte Carlo neutron cross-section lookup mini-app (nuclear physics)
- Category: "physics"
- Schema: schema/spec_schema.json (version 1.0.0)
- Manifest schema: schema/manifest_schema.json
- parallel_api enum values include: cuda, omp, opencl, omp_target, openacc
- unique_id pattern: ^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$
- Template spec: specs/rodinia-bfs-cuda.json (use as structural reference)

# Step 1: Clone XSBench
cd /home/samyak/Desktop/parbench_sam
git clone https://github.com/ANL-CESAR/XSBench.git xsbench/xsbench-src

# Step 2: Explore the directory structure
# XSBench typically has subdirectories for each API variant:
#   openmp/, cuda/, opencl/, openmp-offload/ (or omp-target/), openacc/
# List all top-level directories and identify which contain Makefiles
# Read the README for build instructions and run arguments
# Identify the verification method — XSBench prints a verification hash at the end

# Step 3: Pin the commit
cd xsbench/xsbench-src
git log --oneline -1  # Record this commit hash

# Step 4: Understand XSBench build and run
# For each API variant:
#   - What is the Makefile target?
#   - What compiler is used? (gcc for OMP, nvcc for CUDA, nvc for OpenACC/OMP-target)
#   - What is the output executable name?
#   - What are the run arguments? (typically -s small for correctness, -s large for perf)
#   - What does the verification output look like? (stdout hash pattern)
#   - What files constitute the "prompt_payload" (source files LLM would see)?

# Step 5: Create a symlink (if needed) for path resolution
# Check if a symlink xsbench/xsbench-src -> . is needed (like rodinia/rodinia-src -> .)
# Only create if the provenance.repo_root / source_path resolution requires it

# Step 6: Generate 5 spec files
# Create these files based on the template structure from rodinia-bfs-cuda.json:
#
#   specs/xsbench-xsbench-cuda.json
#   specs/xsbench-xsbench-omp.json
#   specs/xsbench-xsbench-opencl.json
#   specs/xsbench-xsbench-omp_target.json
#   specs/xsbench-xsbench-openacc.json
#
# Key fields for each:
#   spec_version: "1.0.0"
#   identity.kernel_name: "xsbench"
#   identity.source_suite: "xsbench"
#   identity.parallel_api: (cuda|omp|opencl|omp_target|openacc)
#   identity.unique_id: "xsbench-xsbench-{api}"
#   provenance.repository.url: "https://github.com/ANL-CESAR/XSBench"
#   provenance.repository.commit: (the pinned hash from Step 3)
#   provenance.repo_root: "xsbench/xsbench-src"
#   provenance.source_path: (the subdirectory for each variant, e.g., "cuda")
#   files.prompt_payload: (list of .c/.cu/.cpp source files in that variant)
#   files.support_files: ["Makefile"] (or whatever build file exists)
#   build.build_system: "make"
#   build.commands.build: (the make command, may need compiler path flags)
#   build.outputs.executable: (the binary name from Makefile)
#   run.executable: (same as build.outputs.executable)
#   run.input_configurations.correctness.arguments: ["-s", "small"] (or equivalent)
#   run.timeout_seconds: 300
#   verification.method: "self_checking"
#   verification.strategies: [{type: "stdout_pattern", pattern: "Verification.*checksum", ...}]
#     (Read XSBench output to determine exact verification pattern)
#   hardware.target: "gpu" for cuda/opencl/omp_target/openacc, "cpu" for omp
#   metadata.category: not in spec schema (category is only in manifest)
#   metadata.description: "Monte Carlo neutron cross-section lookup (XSBench)"
#   metadata.domain: "nuclear physics"
#   metadata.tags: ["xsbench", "{api}", "physics", "monte-carlo"]
#
# IMPORTANT: Read the actual source files and Makefiles to get correct values.
# Do NOT guess file names or build commands — verify against the actual repo.

# Step 7: Append 5 entries to manifest.jsonl
# Each entry format:
# {"kernel_name":"xsbench","parallel_api":"{api}","source_suite":"xsbench",
#  "spec_file":"specs/xsbench-xsbench-{api}.json",
#  "source_dir":"xsbench/xsbench-src/{subdir}","category":"physics"}

# Step 8: Validate
python3 scripts/validate_schema.py --all
# Expected: Same ~135 known errors (HeCBench + phantom) + 0 new errors for XSBench specs

# Also validate each spec individually:
python3 scripts/validate_schema.py --spec specs/xsbench-xsbench-cuda.json
python3 scripts/validate_schema.py --spec specs/xsbench-xsbench-omp.json
python3 scripts/validate_schema.py --spec specs/xsbench-xsbench-opencl.json
python3 scripts/validate_schema.py --spec specs/xsbench-xsbench-omp_target.json
python3 scripts/validate_schema.py --spec specs/xsbench-xsbench-openacc.json

# Step 9: Write a small test script that:
# 1. Loads each of the 5 new specs and validates JSON structure
# 2. Checks unique_id matches filename
# 3. Checks parallel_api matches implementation.api
# 4. Checks source files exist on disk
# 5. Checks manifest has all 5 entries
# DELETE the test script after verification.

# Step 10: Show me:
# - Directory structure of xsbench/xsbench-src/
# - Summary of each spec (API, files, build command, verification pattern)
# - Validation results

# Step 11: Git commit and push
# git add:
#   xsbench/ (new directory — but check if submodule or regular clone)
#   specs/xsbench-xsbench-*.json (5 files)
#   manifest.jsonl (5 new entries appended)
# Step 12: Populate translation_targets for new XSBench specs
# Session 1.6 created standardize_specs.py which handles ANY suite.
# After creating specs, run:
python3 scripts/generators/standardize_specs.py \
  --suite xsbench \
  --project-root /home/samyak/Desktop/parbench_sam
# This sets translation_targets using the Family rules:
#   - xsbench-cuda: Family 3 (targets = prompt_payload)
#   - xsbench-omp: Family 2 (preserve curated or fallback to prompt_payload)
#   - xsbench-opencl: Family 1 (targets = .cl files only)
#   - xsbench-omp_target: Family 2
#   - xsbench-openacc: Family 2
# Then re-validate:
python3 scripts/validate_schema.py --all

# Step 13: Git commit and push
# Commit: "Add XSBench as second benchmark suite (5 API variants: CUDA/OMP/OpenCL/OMP-target/OpenACC)"
# Push to origin main.
```

---

## SESSION 5 — Verify XSBench Toolchains & Smoke Test

> **STATUS: COMPLETE** — Commit `888910f` (2026-03-23). **4/4 XSBench specs PASS.**
> No OpenACC variant exists in XSBench source. omp_target uses nvc (NVIDIA HPC SDK 24.3,
> `-mp=gpu -gpu=cc89`). Baselines populated (checksums: OMP=941535 history, others=945990 event).
> Eval-ready: cuda, omp, opencl (3 standard specs). omp_target excluded (nvc dependency).

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] OpenMP target offload: GCC -foffload=nvptx-none is likely BROKEN
      (gcc-12-offload-nvptx package not installed). The fallback is nvc -mp=gpu
      (NVIDIA HPC SDK, confirmed available). Accept nvc as the OMP target
      compiler from the start? Or install gcc-12-offload-nvptx first (requires sudo)?
- [ ] If OpenACC or OMP target specs FAIL to build, should they be:
      a) Kept with KNOWN_FAIL status (consistent with Rodinia pattern)
      b) Deleted (reduce noise)
      c) Kept but excluded from eval batches (recommended)
- [ ] Is the augmentation smoke test on XSBench (Step 5) required for the paper
      or a nice-to-have that can be skipped if the session runs long?

EXTERNAL DEPS:
- [ ] Session 4 must be complete (XSBench cloned, specs created)
- [ ] GPU must be available (RTX 4070 needed for CUDA/OpenCL/OpenACC/OMP-target)
- [ ] If GCC OMP target offload is desired: sudo apt install gcc-12-offload-nvptx
      BEFORE the session (requires sudo access)

# Session Goal
Build and run all 5 XSBench API variants on the Linux GPU machine. Verify each variant
produces correct output. Populate baseline_results in each spec. Test the new OpenACC
and OpenMP target compilers.

# Why This Matters
This is the first time OpenACC (nvc) and OpenMP target offload will be used in ParBench.
If any variant fails, we need to fix the spec or document it as a limitation before
running LLM evaluations.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- XSBench specs: specs/xsbench-xsbench-{cuda,omp,opencl,omp_target,openacc}.json
- Compilers available:
  - CUDA: /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc
  - OpenMP: gcc-12 with -fopenmp
  - OpenCL: NVIDIA OpenCL runtime + headers in HPC SDK
  - OpenACC: nvc from HPC SDK 24.3 (at /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc)
  - OpenMP target: NEEDS VERIFICATION — try gcc -foffload=nvptx-none or nvc -mp=gpu
- GPU: NVIDIA RTX 4070 (sm_89, 12GB VRAM)

# Prerequisites
- Session 4 complete (XSBench cloned, specs created)

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Test each variant through the harness

# 2a: CUDA (should work — standard nvcc)
python3 -m harness -v --json verify specs/xsbench-xsbench-cuda.json --config correctness

# 2b: OpenMP CPU (should work — standard gcc -fopenmp)
python3 -m harness -v --json verify specs/xsbench-xsbench-omp.json --config correctness

# 2c: OpenCL (should work if headers/libs correctly configured)
python3 -m harness -v --json verify specs/xsbench-xsbench-opencl.json --config correctness

# 2d: OpenACC (NEW — test nvc compiler)
# If the Makefile doesn't use nvc by default, the spec's build command may need:
#   CC=nvc CFLAGS="-acc -gpu=cc89 -Minfo=accel" make
# Check the actual Makefile first. Adjust the spec's build command if needed.
python3 -m harness -v --json verify specs/xsbench-xsbench-openacc.json --config correctness

# 2e: OpenMP target offload (NEW — test offload compiler)
# Options to try:
#   1. nvc -mp=gpu -gpu=cc89 (NVIDIA HPC SDK)
#   2. gcc -fopenmp -foffload=nvptx-none (GCC with offload support)
# Try nvc first (more likely to work on NVIDIA hardware).
# Check the actual Makefile for the OMP target variant.
python3 -m harness -v --json verify specs/xsbench-xsbench-omp_target.json --config correctness

# Step 3: Debug any failures
# For each failure:
#   1. Read the build error or run error from the JSON output
#   2. Fix the spec's build command (compiler paths, flags)
#   3. Re-run harness verify
#   4. If a variant fundamentally cannot work (missing compiler/runtime), document it
#      as KNOWN_FAIL in .claude/rules/known-issues.md
# DO NOT edit XSBench source code — only fix specs.

# Step 4: Populate baseline_results
# For each passing variant, read the harness JSON output and add baseline_results
# to the spec file. Include: status, exit_code, stdout_snippet, wall_time_seconds.
# Use the same structure as in specs/rodinia-bfs-cuda.json baseline_results section.

# Step 5: Run augmentation smoke test on the 3 standard APIs (CUDA, OMP, OpenCL)
python3 scripts/augmentation/augment_verify.py specs/xsbench-xsbench-cuda.json \
  --augment_level 2 --seed 42 -v --project-root /home/samyak/Desktop/parbench_sam
python3 scripts/augmentation/augment_verify.py specs/xsbench-xsbench-omp.json \
  --augment_level 2 --seed 42 -v --project-root /home/samyak/Desktop/parbench_sam

# Step 6: Verification — write a small test script that:
# 1. Runs harness verify on all 5 XSBench specs
# 2. Collects PASS/FAIL status for each
# 3. Verifies baseline_results are populated for all PASS specs
# 4. Prints a summary table
# DELETE the test script after verification.

# Step 7: Show me:
# - Build/run/verify status for all 5 variants
# - Which compilers were used for OpenACC and OMP target
# - Any failures and their root causes
# - Augmentation smoke test results

# Step 8: Git commit and push
# Commit: Updated specs with baseline_results, any build command fixes
# Message: "Verify XSBench: N/5 PASS, populate baselines, configure OpenACC/OMP-target"
# Push to origin main.
```

---

## SESSION 6 — Paper Outline (M4 — CRITICAL)

> **STATUS: COMPLETE** — Commit `257b992` (2026-03-23). Paper outline created at
> `docs/paper_outline.md`. Contains: 8 sections, 10-page target, figure/table inventory
> (F1–F6, T1–T9), Gal constraint checklist (13 items), numbered contributions (3),
> paper-drafter agent compatibility notes. Use this as the roadmap for Sessions 12–15.

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Paper title: "ParBench: A Benchmark Framework for Evaluating LLM-Based
      Parallel Code Translation" — confirmed? Or does Gal need to approve?
      Note: Gal framed this as "more of an evaluation metric paper than a
      comprehensive benchmark paper" (meeting 00:32:26). Does the title
      emphasize "benchmark framework" or "evaluation study"?
- [ ] Paper track: SC26 full technical paper (10 pages, ACM sigconf) or
      workshop paper? Sprint plan Open Question #5 is still unresolved.
- [ ] Should the outline be written NOW (with TBD placeholders for eval data)
      or wait until Session 2 v2 data is available? Gal said "start writing
      even without final results" (00:45:21) — but claims like "BUILD_FAIL
      dominates" may change after kernel-centric pipeline.
- [ ] Will Gal review the outline before Sessions 12-13 (paper writing)?
- [ ] How many pages for appendices? (SC26 typically allows unlimited appendices
      but reviewers aren't required to read them)

DATA/INFO:
- [ ] READ THE PARAVAL PAPER (Task M3, HIGH priority, ~2 hours). The Related
      Work section cannot be positioned without understanding what Paraval does.
      Provide: the Paraval PDF or your notes on its approach, benchmark count,
      APIs covered, and what it does NOT do that ParBench does.
- [ ] Identify the "Power of Evolve" paper Gal referenced (00:23:47) — is this
      a related work comparison point?
- [ ] Complete list of Gal's constraints (verify these are ALL of them):
      1. No reasoning models  2. No agentic models  3. Reasoning OFF for all
      4. Match Power of Evolve models  5. Conservative augmentation L1-L2
      6. Omit build times  7. Explain curation methodology  8. Compare with Paraval
      9. Anonymous submission

EXTERNAL DEPS:
- [ ] Independent of Sessions 1-5 (can run in parallel — it's a writing task)
- [ ] Paraval paper must be obtained and read before starting

# Session Goal
Create the SC26 paper outline in docs/paper_outline.md. This defines the structure,
key claims, figure list, and data requirements for the full paper draft.

# Why This Matters
Advisor Gal explicitly requested: "Create paper outline BEFORE writing" (marked CRITICAL
in sprint plan). The outline gates all subsequent paper writing sessions.
SC26 format: double-column, 10 pages + appendices.

# Context
- Sprint plan: docs/sprint_to_SC26.md (read for paper targets and meeting decisions)
- Eval results: results/evaluation/eval_summary.md (read for current data)
- Augmentation results: results/augmentation/retest_post_session2.md
- Related work to reference: Paraval, ParEval, ExaBench, TransCoder, SWE-bench, HumanEval
- Meeting notes: meeting_notes/ (read for Gal's and team's strategic decisions)
- Design concern: docs/design_concern_multifile_translation.md
- Gal briefing: docs/gal_augmentation_briefing.md

# Key Paper Claims (from sprint plan + eval data):
# 1. ParBench is a benchmark framework for evaluating LLM-based parallel code translation
# 2. ParBench includes 2 benchmark suites (Rodinia + XSBench), 5 API targets, and an
#    AST-driven augmentation engine with 6 semantics-preserving transforms
# 3. Augmentation is level-invariant: 54/60 specs PASS at L1-L4, zero regressions
# 4. LLM translation evaluation across N models, 3 directions, with augmentation robustness
# 5. BUILD_FAIL dominates failures — LLMs struggle with multi-file translations
# 6. XSBench provides the first multi-API (5 APIs) translation evaluation

# Step 1: Read all relevant docs and results
# Read these files to understand the full data available:
#   - docs/sprint_to_SC26.md (especially paper targets section)
#   - results/evaluation/eval_summary.md
#   - results/augmentation/retest_post_session2.md
#   - docs/design_concern_multifile_translation.md
#   - docs/gal_augmentation_briefing.md
#   - meeting_notes/ (any files about paper strategy)

# Step 2: Write docs/paper_outline.md with this structure:
#
# Title: ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation
#
# Abstract (~200 words sketch — not final, just key points to hit)
#
# §1 Introduction (1.5 pages)
#   - Problem: LLMs are increasingly used for code, but parallel code translation
#     (CUDA↔OpenMP↔OpenCL↔OpenACC↔OMP-target) is largely unevaluated
#   - Gap: Existing benchmarks (HumanEval, SWE-bench) focus on sequential code
#   - Contribution: ParBench — build/run/verify evaluation, augmentation for robustness,
#     multi-suite multi-API framework
#   - 3-4 numbered contributions
#
# §2 Related Work (1 page)
#   - Code translation: TransCoder, ...
#   - Code benchmarks: HumanEval, SWE-bench, ParEval, Paraval
#   - HPC benchmarks: Rodinia, XSBench, HeCBench
#   - Gap: no build+run+verify for parallel code translation
#
# §3 ParBench Framework (2 pages)
#   - 3.1 Spec Schema (declarative benchmark contracts)
#   - 3.2 Harness Pipeline (build → run → verify)
#   - 3.3 Augmentation Engine (6 AST transforms, levels L0-L4)
#   - 3.4 LLM Evaluation Pipeline (prompt → LLM → extract → build → verify)
#   - Figure: System architecture diagram
#
# §4 Benchmark Curation (1 page)
#   - 4.1 Rodinia (22 kernels, 60 specs across 3 APIs)
#   - 4.2 XSBench (1 kernel, 5 API variants)
#   - 4.3 Curation methodology (survey → select → spec → validate)
#   - Table: Kernel × API availability matrix
#
# §5 Evaluation Methodology (1 page)
#   - 5.1 Models under test (list models + reasoning turned off per Gal)
#   - 5.2 Translation directions (cuda-to-omp, omp-to-cuda, cuda-to-opencl)
#   - 5.3 Augmentation levels (L0, L1, L2)
#   - 5.4 Metrics (pass rate, failure taxonomy, augmentation robustness)
#   - 5.5 Experimental setup (hardware, compiler versions, API keys, temperature=0)
#
# §6 Results (2 pages)
#   - 6.1 Overall pass rates per model and direction
#   - 6.2 Failure taxonomy (BUILD_FAIL > RUN_FAIL > VERIFY_FAIL)
#   - 6.3 Augmentation robustness (L0 vs L1 vs L2 comparison)
#   - 6.4 Cross-model analysis
#   - 6.5 XSBench multi-API results
#   - Figure: Kernel × model heatmap
#   - Figure: Failure taxonomy stacked bar chart
#   - Figure: Augmentation robustness comparison
#   - Table: Per-kernel detailed results
#
# §7 Discussion (1 page)
#   - 7.1 Multi-file structural mismatch (M11 design concern)
#   - 7.2 API coverage gaps and limitations
#   - 7.3 Threats to validity
#   - 7.4 Implications for LLM development
#
# §8 Conclusion & Future Work (0.5 pages)
#   - Summary of findings
#   - Future: more suites, more APIs, agentic repair, performance analysis

# Step 3: For each section, note:
# - What data is needed (and whether it exists yet)
# - What figures/tables go there
# - Key claims to make

# Step 4: Show me the complete outline
# No test script needed for this session — it's a writing task.

# Step 5: Git commit and push
# Commit: docs/paper_outline.md
# Message: "Add SC26 paper outline (M4)"
# Push to origin main.
```

---

## SESSION 6.5 — Timing Infrastructure (M6: nsys Profiler Integration)

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Profiler scope: Profile ALL eval specs (CUDA + OMP-target) before re-running
      LLM evaluations, OR update baselines only and leave eval re-run for Session 8+?
      Recommendation: Update baselines first (minimal scope), then re-run evals in
      Session 7/9/10 with --use-profiler enabled.
- [ ] Schema version: Adding kernel_time_seconds and cpu_time_seconds to
      baseline_results requires a schema change. Options:
      (a) Add fields as nullable/optional to existing schema v1.0.0 (non-breaking)
      (b) Bump to schema v1.1.0 (cleaner, but all 64 specs need spec_version update)
      Recommendation: (a) — add as optional/nullable, no version bump required.
- [ ] CPU timing for OpenCL specs: nsys CANNOT profile OpenCL kernels. Options:
      (a) Fall back to wall_time for OpenCL (status quo — no regression)
      (b) Use /usr/bin/time -v (User+Sys CPU time) for OpenCL — not GPU time, but
          better than wall-clock for apples-to-apples comparisons vs CPU OpenMP
      Recommendation: (b) — OpenCL runs on GPU, CPU time is host-side overhead only,
      but document the limitation clearly in the paper.
- [ ] OMP threading (CPU OpenMP) time: /usr/bin/time -v is already implemented in
      runner.py (measure_cpu_time flag). Confirm this is the correct method for OMP specs.
      (The --use-cpu-timing flag exists but was never passed in any eval batch.)
      Recommendation: yes — User+Sys time is correct for CPU-only OpenMP.

EXTERNAL DEPS:
- [ ] nsys available at /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys
      Verify: /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys --version
      Expected: NVIDIA Nsight Systems version 2024.1.1
- [ ] nvc (for OMP target profiling) at /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc
      (OMP target compiled with nvc generates CUDA PTX — nsys sees it as CUDA kernels)
- [ ] GPU must be available and idle during profiling runs
      Verify: nvidia-smi (should show no active compute processes)
- [ ] Linux perf_event_paranoid must allow nsys: cat /proc/sys/kernel/perf_event_paranoid
      nsys needs ≤ 2. If > 2, profiling will fail silently.
      Fix if needed: sudo sysctl -w kernel.perf_event_paranoid=2
- [ ] Source env: source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate

DATA NEEDED:
- [ ] After implementing nsys in the harness, you MUST re-run all CUDA and OMP-target
      specs to collect real kernel_time baselines. Wall-clock baselines already in specs
      are insufficient. Run with: python3 -m harness -v verify specs/<name>.json
      with profiling enabled (see Step 5 below).

# Session Goal
Implement M6: nsys profiler integration in the ParBench harness so that GPU kernel
execution time (Tier 1 in Niranjan's three-tier timing model) is measured for all
CUDA and OMP-target specs. This replaces wall-clock as the timing source for speedup
calculations in the LLM evaluation pipeline.

# Why This Matters — The Methodology Gap
Niranjan (2026-03-17): "Wall clock time is not a correct way to measure kernel performance.
We need to use either (1) kernel execution time — from some profiler, or (2) User CPU time
+ Sys CPU time."

ALL current evaluation results (across all 4 models, all directions, all benchmarks) use
timing_method: "wall_time" in the result JSONs. The speedup priority logic in llm_evaluate.py
(lines 1142-1151) already has the chain:
  kernel_time_seconds → cpu_time_seconds → wall_time_seconds
...but RunResult.kernel_time_seconds is NEVER populated (always None). The paper was
tentatively reframed as "correctness-only" to avoid publishing unreliable speedup numbers.

This session fixes that gap by making kernel_time_seconds non-null for GPU specs.

# Three-Tier Timing Model (Niranjan's decision, 2026-03-17)
Tier 1: GPU kernel execution time ONLY (what nsys measures via cuda_gpu_kern_sum report)
         → Use for: speedup ratio claims in the SC26 paper
         → APIs: CUDA, OMP-target (nvc compiles to CUDA PTX, nsys works)
Tier 2: Kernel time + host-device data transfer time (cudaMemcpy operations)
         → Use for: end-to-end GPU utilization analysis (optional, advanced)
         → APIs: CUDA only (OMP-target manages transfers via OpenMP map clauses)
Tier 3: Wall-clock time (what monotonic() measures now)
         → Current status: used everywhere — must NOT be used for speedup claims
         → Safe for: sanity-checking, timeout enforcement

DECISION: Implement Tier 1 (kernel time only) for SC26. Tier 2 is future work.

# API-Specific Profiling Strategy

| API        | Profiler       | nsys works? | Method                          | RunResult field         |
|------------|----------------|-------------|---------------------------------|-------------------------|
| cuda       | nsys           | YES         | nsys profile + cuda_gpu_kern_sum | kernel_time_seconds     |
| omp_target | nsys           | YES         | same (nvc → CUDA PTX, nsys sees | kernel_time_seconds     |
|            |                |             | identical CUDA kernel events)   |                         |
| opencl     | nsys           | NO          | nsys has no --trace=opencl opt  | cpu_time_seconds (fall- |
|            |                |             | → fall back to /usr/bin/time -v | back, host-side only)   |
| omp (cpu)  | /usr/bin/time  | N/A         | /usr/bin/time -v already impl.  | cpu_time_seconds        |
|            | -v             |             | in runner.py (measure_cpu_time) |                         |

# Current State of the Codebase — Read These Before Implementing

Critical files (read them with cat or the Read tool before touching anything):

1. harness/runner.py lines 19-181 — FULL run_spec() implementation
   - Lines 19-51: _parse_gnu_time() — how /usr/bin/time -v output is parsed
     (User time: 0.52, System time: 0.03 → cpu_time_seconds = 0.55)
   - Lines 54-61: run_spec() signature (measure_cpu_time: bool = False)
   - Lines 120-131: /usr/bin/time -v command prepend mechanism ← EXACT BLUEPRINT FOR nsys
   - Lines 135-147: subprocess.run() with time.monotonic() for wall-clock
   - Lines 157-171: CPU time parsing and temp file cleanup after execution
   - Lines 173-181: RunResult construction — where kernel_time_seconds must be set

2. harness/models.py lines 32-42 — RunResult dataclass
   - Line 32: @dataclass class RunResult
   - Line 38: wall_time_seconds: float (always populated)
   - Line 40: cpu_time_seconds: Optional[float] = None (populated when measure_cpu_time=True)
   - Line 42: kernel_time_seconds: Optional[float] = None ← PLACEHOLDER, NEVER POPULATED

3. scripts/evaluation/llm_evaluate.py lines 1124-1154
   - Lines 1142-1151: speedup calculation — already uses kernel_time > cpu_time > wall_time
     The priority fallback chain is correct; we just need kernel_time to be non-null.
   - Lines 1360-1378: CLI flags --use-cpu-timing (functional) and --use-profiler (stub/no-op)
     --use-profiler currently does NOTHING (it's parsed but never passed to run_spec())

4. schema/spec_schema.json lines 743-760 — baseline_results schema
   - Line 746: wall_time_seconds only field (no cpu_time or kernel_time fields)
   - Need to add optional fields: cpu_time_seconds and kernel_time_seconds

# Step 1: Verify nsys Environment
# Run these checks FIRST. If any fail, the rest of the session cannot proceed.

source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Verify nsys availability
/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys --version
# Expected: NVIDIA Nsight Systems version 2024.1.1.x or newer

# Check perf_event_paranoid (nsys requirement)
cat /proc/sys/kernel/perf_event_paranoid
# Expected: 2 or lower. If > 2, run: sudo sysctl -w kernel.perf_event_paranoid=2

# Quick nsys smoke test — profile a trivial CUDA binary to confirm JSON output works
# Build a reference spec and run with nsys manually:
python3 -m harness build specs/rodinia-bfs-cuda.json
cd /home/samyak/Desktop/parbench_sam

NSYS=/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys
TMPFILE=$(mktemp /tmp/nsys_test_XXXXXX)
$NSYS profile --trace=cuda --force-overwrite=true -o ${TMPFILE} \
  rodinia/rodinia-src/cuda/bfs/bfs rodinia/rodinia-src/cuda/bfs/graph1MW_6.txt
$NSYS stats --report cuda_gpu_kern_sum --format json --force-export=true ${TMPFILE}.nsys-rep
rm -f ${TMPFILE}.nsys-rep ${TMPFILE}.sqlite
# Expected JSON output: [{"Time (%)": 99.x, "Total Time (ns)": NNNNNNN, "Name": "Kernel..."}]
# Total Time (ns) / 1e9 = kernel_time_seconds

# Step 2: Implement _parse_nsys_stats() in harness/runner.py
# Add this function AFTER _parse_gnu_time() (after line 51, before run_spec())
# Follow the EXACT same style as _parse_gnu_time().

# Paste the following into harness/runner.py after line 51:
#
# def _parse_nsys_stats(nsys_json_output: str) -> Optional[float]:
#     """Parse nsys cuda_gpu_kern_sum JSON output, return total kernel time in seconds.
#
#     nsys stats --report cuda_gpu_kern_sum --format json produces a JSON array where
#     each element is a kernel with {"Total Time (ns)": <nanoseconds>, "Name": <str>, ...}
#     We sum all kernels (multiple kernels in one run are all real GPU work).
#     Returns None if output is empty, malformed, or contains no kernel data.
#     """
#     import json as _json
#     try:
#         data = _json.loads(nsys_json_output)
#     except (_json.JSONDecodeError, ValueError):
#         return None
#     if not isinstance(data, list) or len(data) == 0:
#         return None
#     total_ns = 0
#     for row in data:
#         if isinstance(row, dict) and "Total Time (ns)" in row:
#             total_ns += int(row["Total Time (ns)"])
#     return total_ns / 1e9 if total_ns > 0 else None

# Step 3: Add profile_gpu parameter to run_spec() in harness/runner.py
# Current signature (line 54): def run_spec(spec, ..., measure_cpu_time: bool = False)
# New signature: def run_spec(spec, ..., measure_cpu_time: bool = False, profile_gpu: bool = False)
#
# Inside run_spec(), AFTER the /usr/bin/time -v block (after line 131),
# add the analogous nsys block:
#
#     nsys_tmpfile = None
#     if profile_gpu:
#         import tempfile
#         nsys_exe = "/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys"
#         nsys_tmpfile = tempfile.mktemp(suffix="", prefix="/tmp/parbench_nsys_")
#         cmd = [
#             nsys_exe, "profile",
#             "--trace=cuda",
#             "--force-overwrite=true",
#             "-o", nsys_tmpfile,
#         ] + cmd
#
# Then AFTER subprocess.run() (after line 147), add nsys stat parsing:
#
#     kernel_time_seconds = None
#     if profile_gpu and nsys_tmpfile is not None:
#         nsys_rep = nsys_tmpfile + ".nsys-rep"
#         nsys_exe = "/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nsys"
#         try:
#             stats_result = subprocess.run(
#                 [nsys_exe, "stats",
#                  "--report", "cuda_gpu_kern_sum",
#                  "--format", "json",
#                  "--force-export=true",
#                  nsys_rep],
#                 capture_output=True, text=True, timeout=60
#             )
#             kernel_time_seconds = _parse_nsys_stats(stats_result.stdout)
#         except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
#             kernel_time_seconds = None
#         finally:
#             import os as _os
#             for ext in [".nsys-rep", ".sqlite"]:
#                 try: _os.unlink(nsys_tmpfile + ext)
#                 except FileNotFoundError: pass
#
# Then in RunResult construction (line 173-181), set:
#     kernel_time_seconds=kernel_time_seconds,

# Step 4: Wire --use-profiler CLI flag in scripts/evaluation/llm_evaluate.py
# Current state (line 1378): --use-profiler is parsed but never passed to run_spec()
# Find where run_spec() is called from within llm_evaluate.py (search for run_spec)
# and add: profile_gpu=args.use_profiler (or equivalent)
# Also for CPU OpenMP specs: if spec API is "omp" (not "omp_target"), pass
# measure_cpu_time=True regardless of --use-profiler (always use /usr/bin/time -v for CPU OMP)

# Step 5: Update schema/spec_schema.json — add optional timing fields to baseline_results
# Find the "configurations" properties in baseline_results (around line 743-760)
# The current schema has only "wall_time_seconds" as a timing field.
# Add these two optional nullable fields:
#
#     "cpu_time_seconds": {
#         "description": "CPU time (User + Sys) from /usr/bin/time -v, in seconds",
#         "oneOf": [{"type": "number", "minimum": 0}, {"type": "null"}]
#     },
#     "kernel_time_seconds": {
#         "description": "GPU kernel execution time from nsys cuda_gpu_kern_sum, in seconds",
#         "oneOf": [{"type": "number", "minimum": 0}, {"type": "null"}]
#     }
#
# These are additionalProperties: false in the current schema — you MUST add them here
# or the new fields will fail validation. Verify with:
#   python3 scripts/validate_schema.py --spec specs/rodinia-bfs-cuda.json

# Step 6: Collect kernel_time baselines for all CUDA specs
# After the harness changes are working, run a profiling pass on all CUDA specs.
# The goal: populate baseline_results.configurations.correctness.kernel_time_seconds
# and cpu_time_seconds for each spec.
#
# Run this for all 54 PASS Rodinia CUDA specs + 3 XSBench specs (cuda, omp, opencl):
#   python3 -m harness --json verify specs/rodinia-bfs-cuda.json
# Then update each spec's baseline_results with the new timing data.
# Use a batch script to avoid doing this manually for 57 specs:
#   scripts/baselines/collect_timing_baselines.py (create this script — see below)
#
# The collect_timing_baselines.py script should:
#   1. Accept a list of spec files (glob: specs/rodinia-*-cuda.json specs/xsbench-*-cuda.json)
#   2. For each spec: run_spec() with profile_gpu=True, capture kernel_time_seconds
#   3. Update spec's baseline_results.configurations.correctness.kernel_time_seconds in place
#   4. Print progress and a summary table
#   5. Commit the updated specs: "Add kernel_time baselines for N CUDA specs"
#
# Note: Do NOT update omp_target baselines in this session — omp_target is excluded from
# standard eval batches (requires nvc). Update those baselines separately if needed.

# Step 7: Update llm_evaluate.py timing_method reporting
# After this session, timing_method in result JSONs should report:
#   "kernel_time" when kernel_time_seconds is populated (CUDA + OMP-target evals with profiler)
#   "cpu_time" when cpu_time_seconds is populated but not kernel_time (OMP cpu, OpenCL)
#   "wall_time" when neither is available (fallback — should be rare after this session)
# Verify the timing_method reporting logic (around line 1142-1151) correctly reflects this.

# Step 8: Verify the full pipeline end-to-end
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# Test 1: harness directly with profiling
python3 -m harness -v verify specs/rodinia-bfs-cuda.json --profile-gpu
# Expected: kernel_time_seconds appears in output (non-null float)

# Test 2: llm_evaluate.py with --use-profiler
# Run a single kernel evaluation with profiling to confirm kernel_time is populated:
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-omp \
  --models claude-sonnet-4-6 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --kernels bfs \
  --use-profiler \
  -v
# Check result JSON: timing_method should be "kernel_time", speedup_ratio should be non-null

# Test 3: OpenCL spec (nsys should NOT be invoked, CPU time fallback used)
python3 -m harness -v verify specs/rodinia-bfs-opencl.json --profile-gpu
# Expected: cpu_time_seconds populated (from /usr/bin/time -v), kernel_time_seconds = null
# (Because the API is opencl, profile_gpu should degrade gracefully to cpu_time fallback)
# NOTE: The harness should check spec.implementation.api before invoking nsys:
#   if profile_gpu and spec_api not in ("cuda", "omp_target"):
#       measure_cpu_time = True   # fall back to /usr/bin/time -v
#       profile_gpu = False

# Test 4: Validate updated spec files pass schema validation
python3 scripts/validate_schema.py --all
# Expected: same ~135 known errors (HeCBench + phantoms), ZERO new errors

# Step 9: Git commit
# git add harness/runner.py harness/models.py schema/spec_schema.json
# git add scripts/evaluation/llm_evaluate.py
# git add scripts/baselines/collect_timing_baselines.py  # new script
# git add specs/rodinia-*-cuda.json specs/xsbench-*-cuda.json  # updated baselines
# git commit -m "feat: M6 nsys profiler integration — kernel_time_seconds now populated for CUDA specs

# - _parse_nsys_stats(): parse cuda_gpu_kern_sum JSON, sum all kernel Total Time (ns)
# - run_spec(): new profile_gpu=False param, nsys command prepend (blueprint: /usr/bin/time -v)
# - run_spec(): auto-degrade to cpu_time for OpenCL (nsys has no opencl trace)
# - schema: add optional cpu_time_seconds + kernel_time_seconds to baseline_results
# - llm_evaluate.py: --use-profiler now wired to profile_gpu=True in run_spec()
# - collect_timing_baselines.py: batch script for updating all CUDA spec baselines
# - Baselines updated for N CUDA specs with real kernel_time_seconds values
#
# Speedup calculations now use Tier 1 timing (kernel execution) per Niranjan's directive.
# Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## SESSION 7 — Augmented Evaluation (L1-L4, COMPLETE)

> **Updated 2026-03-25:** L0-L4 all levels. azure-gpt-4.1 EXCLUDED (deployment disabled by Gal).
> L0 baselines already exist for all 3 active models — `--resume` skips them.
> All decisions resolved — paste this prompt directly into a new Claude Code session.

```
ultrathink

# SESSION 7 — Augmented Evaluation L1-L4 (Rodinia cuda-to-omp)
# Updated 2026-03-25 with current project state

## DECISIONS (ALL RESOLVED — no user input needed)
- [x] Models: 3 models only (azure-gpt-4.1 EXCLUDED — deployment disabled by Gal)
      claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile
- [x] Augmentation levels: L1 through L4 (COMPLETE). L0 already exists for all 3 models.
- [x] If augmentation causes degradation: record and continue (augmentation baseline
      proves transforms are semantics-preserving — 54/60 PASS at all levels L1-L4)
- [x] Seed = 42 + level (eval-pipeline-specific, deterministic, reproducible)
- [x] Kernel-centric translation is the ONLY mode (Sessions 1.5+1.6 complete)
- [x] Budget: 204 API calls × ~$0.05 avg = ~$10-$25 total. Approved.

## CURRENT STATE (verified 2026-03-25)
- S8 (XSBench) COMPLETE: 180 result files, 12 directions × 3 models × L0-L4
- S7 planning commit exists (commit 3373c0e) — but ZERO Rodinia L1-L4 eval results
- L0 cuda-to-omp baselines COMPLETE for all 3 active models:
    claude-sonnet-4-6:       12/17 PASS (70.6%) — commit 887d681
    gemini-2.5-flash-lite:    4/17 PASS (23.5%) — commit f0b4f98
    groq-llama-3.3-70b:       5/17 PASS (29.4%) — commit b644bc6
- azure-gpt-4.1 had 9/17 PASS (commit 3d43afa) but is EXCLUDED — skip entirely
- W-S12 (paper sections 3-5) COMPLETE and merged — 3289 words, docs/paper/paper_sections_3_4_5.md
- W-S14 (figures) COMPLETE with L0-only data — will need regeneration after this session
- W-S11 (dashboard refresh) running in parallel worktree — no conflict

## EXTERNAL DEPS (all met)
- [x] Sessions 2+3+3b complete — L0 baselines exist for 3 active models
- [x] Augmentation pipeline verified — 54/60 Rodinia PASS at L1-L4 (level-invariant)
- [x] API keys must be set in shell (check before running):
      ANTHROPIC_API_KEY (claude-sonnet-4-6)
      GEMINI_API_KEY or GOOGLE_API_KEY (gemini-2.5-flash-lite)
      GROQ_API_KEY (groq-llama-3.3-70b-versatile)

# Session Goal
Run cuda-to-omp evaluation at augmentation levels L1, L2, L3, L4 for all 3 active models.
This fills the only remaining gap in the Rodinia augmentation robustness story.
Produces data for Paper Contribution #2 and unlocks Figure F4 (augmentation robustness).

# Why This Matters
XSBench already has L0-L4 data for 12 directions (180 files). Rodinia has L0 only.
Without Rodinia L1-L4, Figure F4 can only show XSBench augmentation data (N=1 kernel).
With Rodinia L1-L4 (N=17 kernels), F4 becomes a robust quantitative comparison.

# IMPORTANT
- Kernel-centric translation ONLY: LLM produces only translation_targets kernel files.
- Augmentation applies to SOURCE kernel files only. Target infrastructure is untouched.
- Seed formula: seed = 42 + level (different from standalone augmentation which uses seed=42)
- Known Groq limitation: 16384 token completion cap causes EXTRACTION_FAIL on large kernels:
  heartwall (89K prompt tokens), myocyte (143K prompt tokens). This is expected — record it.

# Step 1: Activate venv and verify API keys
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

echo "=== API Key Check ==="
echo "ANTHROPIC: ${ANTHROPIC_API_KEY:+SET}"
echo "GEMINI: ${GEMINI_API_KEY:+SET} / GOOGLE: ${GOOGLE_API_KEY:+SET}"
echo "GROQ: ${GROQ_API_KEY:+SET}"
# ALL must show SET. If any show empty, STOP and resolve before proceeding.

echo "=== Existing L0 baseline count ==="
for m in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
  count=$(ls results/evaluation/$m/rodinia-*-cuda-to-rodinia-*-omp.json 2>/dev/null | wc -l)
  echo "$m L0: $count files (expected 17)"
done
# Confirm 17 L0 files per model before proceeding.

# Step 2: Run L1+L2 (102 tasks, ~3-5h)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 1 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v 2>&1 | tee results/evaluation/s7_l1l2.log

# Step 3: Run L3+L4 (102 more tasks, ~3-5h)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 3 4 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v 2>&1 | tee results/evaluation/s7_l3l4.log

# Step 4: Regenerate analysis with all levels
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp \
  --expected-levels 0 1 2 3 4

# Step 5: Verification — count result files per model per level
for m in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
  for lvl in 0 1 2 3 4; do
    if [ "$lvl" -eq 0 ]; then
      count=$(ls results/evaluation/$m/rodinia-*-cuda-to-rodinia-*-omp.json 2>/dev/null | wc -l)
    else
      count=$(ls results/evaluation/$m/rodinia-*-cuda-to-rodinia-*-omp-L${lvl}.json 2>/dev/null | wc -l)
    fi
    echo "$m L$lvl: $count files"
  done
done
# Expected: 17 files per model per level
# Total new: 204 files (17 × 3 models × 4 levels)
# Total Rodinia cuda-to-omp: 255 (51 existing L0 + 204 new L1-L4)

# Step 6: Show me a level comparison summary:
# - Pass rates: L0 vs L1 vs L2 vs L3 vs L4 for each of the 3 models
# - Any augmentation-induced failures (L0 PASS → L{N} FAIL) — these are "fragility" signals
# - Summary table for the paper: model × level pass rate matrix
# - "Pass Rate by Translation Complexity" table at L0/L1/L2/L3/L4
# - Confirm all results have translation_mode="kernel_centric"

# Step 7: Git commit and push
# Stage: all new L1-L4 result files + updated eval_summary.* + s7 log files
# Message: "Session 7: Rodinia augmented eval L1-L4 for 3 models (204 tasks, cuda-to-omp)"
# Push to origin main.
```

---

## SESSION 8 — XSBench LLM Evaluation (Multi-API)

```
ultrathink

# Models (decided by Gal 2026-03-23):
# azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — all 4 models (see Prerequisite #1 above)
- [ ] XSBench is 1 kernel per direction. Is PASS/FAIL on 1 kernel a
      "case study" (qualitative) or "quantitative evidence" for the paper?
- [ ] Should XSBench eval include augmentation (L1/L2)? The prompt doesn't
      mention it. Adding it triples API calls from ~20 to ~60.
- [x] RESOLVED: No OpenACC spec exists in XSBench. OMP-target PASSED in Session 5; included as Tier 3 case study only (nvc compiler required, excluded from standard eval batches).

CLARIFICATIONS:
- [x] RESOLVED (Session 1.6): XSBench translation_targets gap is closed.
      `scripts/generators/standardize_specs.py --suite xsbench` handles this.
      Step added to Session 4 (Step 12). No action needed here.

EXTERNAL DEPS:
- [ ] Sessions 4 + 5 must be complete (XSBench cloned + smoke tested)
- [x] Sessions 1.5+1.6 must be complete (kernel-centric pipeline, universal) — DONE
- [ ] API keys for all 4 models (see Prerequisite #1 above)

# Session Goal
Run LLM translation evaluation on XSBench across ALL viable API direction pairs.
XSBench has 4 verified PASS specs (cuda, omp, opencl, omp_target) — yielding 12 direction
pairs total. This session covers Tier 1-2 XSBench pairs AND all Tier 3 (omp_target) pairs.

# Why This Matters
XSBench provides expert-written implementations in 4 parallel APIs — the only suite with
omp_target coverage. The Tier 3 (omp_target) results are XSBench-only case studies (N=1
per direction). Tier 1-2 XSBench results complement the larger Rodinia dataset.
This is the "multi-API story" for §6.6 of the SC26 paper.

NOTE: XSBench has NO openacc spec. Only 4 APIs: cuda, omp, opencl, omp_target.
The sprint plan reference to "openacc" was incorrect. Do not attempt cuda-to-openacc.

# Context
- XSBench specs (4, all verified PASS in Session 5):
    specs/xsbench-xsbench-cuda.json       ← cuda source, PASS
    specs/xsbench-xsbench-omp.json        ← omp target, PASS
    specs/xsbench-xsbench-opencl.json     ← opencl target, PASS
    specs/xsbench-xsbench-omp_target.json ← omp_target (nvc), PASS
- All 12 direction pairs are viable (all 4 specs verified PASS)
- Translation pairs to run (grouped by tier):
  Tier 1 (same as Rodinia primary):
    cuda-to-omp, omp-to-cuda
  Tier 2 (cross-API, same as Rodinia cross-API):
    cuda-to-opencl, opencl-to-cuda, opencl-to-omp, omp-to-opencl
  Tier 3 (omp_target — XSBench only, case study):
    cuda-to-omp_target, omp_target-to-cuda, omp_target-to-opencl, opencl-to-omp_target
- For paper: Tier 3 results described as "N=1 case study" not quantitative evidence
- omp_target uses nvc compiler (NVIDIA HPC SDK 24.3 -mp=gpu -gpu=cc89) — configured in spec

# Prerequisites
- Session 5 complete (XSBench variants smoke tested)
- Session 3b complete (all 4 models have cuda-to-omp L0 baselines)
- API keys for all 4 models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Determine which XSBench translation pairs are viable
# Read each XSBench spec's baseline_results to check which passed in Session 5
# Only run pairs where both source and target specs are verified PASS

# Step 3: Run evaluation for Tier 1 + Tier 2 directions (standard cross-API)
# Run both models for each direction:

# Tier 1:
python3 scripts/evaluation/run_eval_batch.py \
  --suite xsbench --direction cuda-to-omp \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --project-root /home/samyak/Desktop/parbench_sam --max-retries 2 --resume -v

python3 scripts/evaluation/run_eval_batch.py \
  --suite xsbench --direction omp-to-cuda \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --project-root /home/samyak/Desktop/parbench_sam --max-retries 2 --resume -v

# Tier 2:
for DIR in cuda-to-opencl opencl-to-cuda opencl-to-omp omp-to-opencl; do
  python3 scripts/evaluation/run_eval_batch.py \
    --suite xsbench --direction $DIR \
    --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --project-root /home/samyak/Desktop/parbench_sam --max-retries 2 --resume -v
done

# Step 4: Run Tier 3 (omp_target) directions — case study
# These use nvc for build/run/verify. The LLM writes GPU-offload pragma code.
for DIR in cuda-to-omp_target omp_target-to-cuda omp_target-to-opencl opencl-to-omp_target; do
  python3 scripts/evaluation/run_eval_batch.py \
    --suite xsbench --direction $DIR \
    --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --project-root /home/samyak/Desktop/parbench_sam --max-retries 2 --resume -v
done
# NOTE: omp_target uses nvc for compilation. If nvc fails, flag result as INFRA_ERROR.
# Do NOT use gcc-offload — it is not installed.

# Step 5: Regenerate analysis
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard

# Step 6: Verification — write a small test script that:
# 1. Loads all XSBench eval results
# 2. Prints a direction x model matrix showing PASS/FAIL
# 3. Compares with Rodinia results — is XSBench easier or harder?
# DELETE the test script after verification.

# Step 7: Show me:
# - XSBench eval results per direction per model
# - Comparison with Rodinia pass rates
# - Any new failure patterns specific to multi-API translation

# Step 8: Git commit and push
# Commit: XSBench eval results, updated eval_summary.*
# Message: "XSBench multi-API eval: N directions × 4 models"
# Push to origin main.
```

---

## SESSION 9 — Second Direction: omp-to-cuda (Rodinia)

```
ultrathink

# Models (decided by Gal 2026-03-23):
# azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — all 4 models (see Prerequisite #1 above)
- [ ] omp-to-cuda is expected to be HARDER (adding GPU parallelism). If pass
      rate is very low (<20%), is this still worth a full paper section or
      just a paragraph in Discussion? (Recommendation: report regardless —
      even 0% is a valid finding about LLM capabilities)
- [ ] Should L1/L2 augmentation also be done for omp-to-cuda? The prompt only
      runs L0. Adding L1/L2 triples API calls from 32 to 96.
- [ ] The 16-kernel list excludes kmeans (CUDA target KNOWN_FAIL) and
      mummergpu (OMP source KNOWN_FAIL). Confirm this exclusion list is correct.

CLARIFICATIONS:
- [x] RESOLVED (Session 1.6): All CUDA specs now have translation_targets = prompt_payload
      (Family 3 rule in standardize_specs.py). No fallback exists — single kernel_centric mode.
      This is correct: CUDA files are all kernel code, so targets = full payload.

EXTERNAL DEPS:
- [ ] Sessions 1, 1.5, 2, 3, 3b must be complete
- [ ] API keys for all 4 models

# Session Goal
Run omp-to-cuda evaluation for all eligible Rodinia kernels with all 4 models at L0.

# Why This Matters
The paper targets 6 translation directions (see Translation Direction Matrix above).
This session covers direction #2 (omp-to-cuda). Direction #1 (cuda-to-omp) is Sessions 2/3/7.
Directions #3-6 (cross-API) are Sessions 10 and 10b. Tier 3 (omp_target) is Session 8.
omp-to-cuda is the reverse of the primary direction — testing whether LLMs can ADD GPU
parallelism (harder than removing it). Expected to have lower pass rates than cuda-to-omp.

# IMPORTANT: Kernel-centric translation is the ONLY mode (Sessions 1.5 + 1.6 complete).
# For omp-to-cuda, the source is OMP (typically 1 kernel file in translation_targets),
# and the target is CUDA. The LLM must produce CUDA kernel file(s) from the OMP source.
# The CUDA target spec's translation_targets identifies which .cu/.cuh files to produce.
# This is typically 1-2 .cu files depending on the kernel.
#
# After Session 1.6: ALL CUDA specs have translation_targets = prompt_payload (Family 3 rule).
# This is the universal rule — no exceptions, no fallback. CUDA files are all kernel code.
# nn-cuda's hurricane_gen.c was already handled during Session 1.5 spec bloat fixes.

# Context
- Eligible omp-to-cuda kernels (16, excluding mummergpu-omp KNOWN_FAIL,
  and excluding kmeans because kmeans-cuda target has KNOWN_FAIL build):
  backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte,
  nn, nw, particlefilter, pathfinder, srad, streamcluster
- The batch runner uses manifest to find pairs: source=omp, target=cuda
- Phantom OMP specs (gaussian, huffman, hybridsort) will error — use --kernels to filter

# Prerequisites
- Session 1 complete (submodule reset)
- Sessions 1.5+1.6 complete (kernel-centric pipeline, all CUDA specs have translation_targets via Family 3 rule)
- Session 3b complete (all 4 models have L0 baselines)
- API keys configured for all 4 models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run all 4 models
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction omp-to-cuda \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v

# Step 3: Regenerate analysis
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp omp-to-cuda \
  --expected-levels 0

# Step 4: Verification — write a small test script that:
# 1. Counts omp-to-cuda results per model
# 2. Compares omp-to-cuda pass rates with cuda-to-omp (is reverse harder?)
# 3. Identifies kernels that pass in one direction but fail in the other
# 4. Shows "Pass Rate by Translation Complexity" for this direction
# DELETE the test script.

# Step 5: Show me direction comparison table and push.
# Commit: "Add omp-to-cuda eval results for Rodinia (16 kernels × 4 models, kernel-centric)"
```

---

## SESSION 10 — Third Direction: cuda-to-opencl (Rodinia)

```
ultrathink

# Models (decided by Gal 2026-03-23):
# azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — all 4 models (see Prerequisite #1 above)
- [ ] nn-opencl is KNOWN_FAIL for ORIGINAL code, but the LLM writes NEW code.
      However, the spec's run args use "filelist.txt" which doesn't exist —
      the LLM-generated code will TIMEOUT regardless of quality. Fix nn-opencl
      run args to "filelist_4" before running? Or accept it will fail due to
      spec issues?
- [ ] cuda-to-opencl is inherently multi-file (.cl + .cpp). What's the minimum
      acceptable pass rate for including this direction in the paper?
- [ ] L0 only, no augmentation for this direction. Confirmed?

EXTERNAL DEPS:
- [x] Sessions 1 + 1.5 + 1.6 must be complete — DONE
      The `full_project` mode no longer exists (removed in Session 1.6).
- [ ] Session 3b complete (all 4 models have L0 baselines)
- [ ] API keys for all 4 models

# Session Goal
Run cuda-to-opencl evaluation for eligible Rodinia kernels with all 4 models at L0.

# Why This Matters
Direction #3 of 6 in the Translation Direction Matrix (see above). cuda-to-opencl tests
cross-vendor API translation (NVIDIA-specific CUDA → vendor-neutral OpenCL). After Session 1.6,
the LLM produces ONLY the .cl kernel file(s); the host .cpp driver is read-only context.
Session 10b (after this session) covers the remaining 3 Rodinia cross-API directions:
opencl-to-cuda (#4), opencl-to-omp (#5), omp-to-opencl (#6).

# IMPORTANT (updated Session 1.6): OpenCL targets have translation_targets = .cl files ONLY.
# The host .cpp driver is now Target Infrastructure Context (read-only, not produced by LLM).
# This is the Family 1 rule from standardize_specs.py. Complexity may now be single_file
# or multi_to_single for some kernels (e.g., hotspot-opencl → 1 .cl file only).
# OpenCL inherently requires separate device/host code — cannot be normalized to 1 file.
#
# After Session 1.6, the LLM produces ONLY the .cl device kernel file(s).
# The host .cpp driver is provided as read-only Target Infrastructure Context.
# This means the LLM is tested on kernel translation, not host API boilerplate.
#
# The scientific question is: "can the LLM produce correct OpenCL C kernel code
# given the host driver as context?" Expected: pass rates closer to cuda-to-omp
# than originally estimated, since host/device structural complexity is removed.

# Context
- Eligible cuda-to-opencl kernels (18): backprop, bfs, bptree, cfd, dwt2d, gaussian,
  heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter,
  pathfinder, srad, streamcluster
  (Note: dwt2d and gaussian have OpenCL specs but no OMP — eligible for this direction)
  (Note: nn-opencl is KNOWN_FAIL for original code, but LLM writes NEW code —
   include it, expect it to fail, report as data point)
- Use --kernels to avoid phantom specs
- All OpenCL target specs have translation_targets = .cl files only (1+ files, Family 1 rule from Session 1.6)

# Prerequisites
- Session 1 complete (submodule reset)
- Sessions 1.5+1.6 complete (kernel-centric pipeline, OpenCL specs have .cl-only translation_targets)
- Session 3b complete (all 4 models have L0 baselines)
- API keys configured for all 4 models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run all 4 models
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-opencl \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v

# Step 3: Regenerate analysis
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp cuda-to-opencl \
  --expected-levels 0

# Step 4: Verification — write a small test script that:
# 1. Counts cuda-to-opencl results per model
# 2. Compares pass rates: cuda-to-omp vs cuda-to-opencl (OpenCL harder?)
# 3. Shows "Pass Rate by Translation Complexity" — OpenCL is inherently multi-file
# 4. Checks if all OpenCL results have translation_mode="kernel_centric"
# DELETE the test script.

# Step 5: Show me:
# - cuda-to-opencl pass rates vs cuda-to-omp comparison
# - Pass Rate by Translation Complexity for opencl (all should be multi-file)
# - Any kernels that PASS despite the 2-file requirement (interesting positive results)
# - Key paper finding: "OpenCL translation requires producing host+device code separately;
#   this structural complexity predicts [X% lower] pass rates vs. OMP translation"
# Commit and push.
# Commit: "Add cuda-to-opencl eval results for Rodinia (18 kernels × 4 models, kernel-centric)"
```

---

## SESSION 10b — Remaining Rodinia Cross-API Directions (#4–6)

```
ultrathink

# Models (decided by Gal 2026-03-23):
# azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — all 4 models (see Prerequisite #1 above)
- [ ] Session 10 (cuda-to-opencl) must be complete before this session
- [ ] For opencl-to-omp and omp-to-opencl: OpenCL source spec translation_targets
      are .cl files (Family 1 rule). OMP target translation_targets are curated files
      (Family 2 rule). Confirm this is understood.
- [ ] Minimum acceptable pass rate for including opencl-to-cuda in the paper?
      Note: opencl-to-cuda tests the reverse of cuda-to-opencl — LLM must produce CUDA
      from vendor-neutral OpenCL. Expected to be harder than cuda-to-opencl.
- [ ] Should L1/L2 augmentation also be run for these 3 directions?
      Adds 3 × 2 × ~16 × 2 = ~192 API calls. Recommendation: L0 only to match Sessions 9/10.

EXTERNAL DEPS:
- [x] Sessions 1 + 1.5 + 1.6 must be complete — DONE
- [ ] Session 10 (cuda-to-opencl) must be complete (establishes opencl baseline)
- [ ] Session 3b complete (all 4 models have L0 baselines)
- [ ] API keys for all 4 models

# Session Goal
Run the 3 remaining Rodinia-viable translation directions: opencl-to-cuda, opencl-to-omp,
and omp-to-opencl. These complete the 6-direction set for the SC26 paper (directions #4–6
in the Translation Direction Matrix).

# Why This Matters
The paper claims results for 6 translation directions (3 APIs × 2 directions each for
non-symmetric pairs). Sessions 9 and 10 cover #2 (omp-to-cuda) and #3 (cuda-to-opencl).
This session covers #4–6, completing the full bidirectional API translation matrix.
Scientific questions per direction:
  - opencl-to-cuda (#4): Can LLMs translate FROM vendor-neutral TO NVIDIA-specific?
    Reverse of Session 10. Tests whether training data asymmetry (more CUDA than OpenCL)
    helps or hurts the LLM.
  - opencl-to-omp (#5): Cross-paradigm — GPU device kernel → CPU threaded code.
    The LLM must de-parallelize across thread dimensions and map to CPU fork-join model.
  - omp-to-opencl (#6): CPU threaded → GPU device kernel. Hardest direction — must
    decompose a monolithic parallel region into separate host + device structure.

# IMPORTANT: Translation target rules (Session 1.6 family rules)
# - opencl-to-cuda: SOURCE = .cl file (Family 1 source), TARGET = CUDA files = prompt_payload (Family 3)
# - opencl-to-omp: SOURCE = .cl file (Family 1 source), TARGET = OMP curated files (Family 2)
# - omp-to-opencl: SOURCE = OMP curated files (Family 2), TARGET = .cl file only (Family 1)
# The pipeline handles all of this automatically via translation_targets in each spec.

# Eligible kernels per direction (after KNOWN_FAIL exclusions):

# opencl-to-cuda (16 Rodinia):
# All 20 cuda-opencl overlapping kernels, minus:
#   - kmeans: cuda target KNOWN_FAIL + opencl source KNOWN_FAIL
#   - mummergpu: cuda target KNOWN_FAIL (no opencl spec for mummergpu anyway)
#   - hybridsort: cuda target KNOWN_FAIL
#   - nn: opencl source KNOWN_FAIL
# = 17 eligible: backprop, bfs, bptree, cfd, dwt2d, gaussian, heartwall, hotspot,
#   hotspot3d, lavamd, lud, myocyte, nw, particlefilter, pathfinder, srad, streamcluster
OPENCL_TO_CUDA_KERNELS="backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# opencl-to-omp (15 Rodinia):
# All omp-opencl overlapping kernels, minus:
#   - kmeans: opencl source KNOWN_FAIL
#   - nn: opencl source KNOWN_FAIL
# = 15 eligible: backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud,
#   myocyte, nw, particlefilter, pathfinder, srad, streamcluster
OPENCL_TO_OMP_KERNELS="backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# omp-to-opencl (15 Rodinia):
# All omp-opencl overlapping kernels, minus:
#   - kmeans: opencl target KNOWN_FAIL
#   - nn: opencl target KNOWN_FAIL
# = 15 eligible (same set as opencl-to-omp above, symmetric exclusion)
OMP_TO_OPENCL_KERNELS="backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# Prerequisites
source /home/samyak/Desktop/parbench_sam/env_parbench/activate
cd /home/samyak/Desktop/parbench_sam

# Step 1: Run opencl-to-cuda (direction #4)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction opencl-to-cuda \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OPENCL_TO_CUDA_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# Step 2: Run opencl-to-omp (direction #5)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction opencl-to-omp \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OPENCL_TO_OMP_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# Step 3: Run omp-to-opencl (direction #6)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction omp-to-opencl \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels $OMP_TO_OPENCL_KERNELS \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 --resume -v

# Step 4: Regenerate analysis with all 6 directions
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda opencl-to-omp omp-to-opencl \
  --expected-levels 0

# Step 5: Verification — write a small test script that:
# 1. Counts results per direction per model (expect 16/15/15 tasks each)
# 2. Builds a 6-direction × 4-model pass rate matrix
# 3. Identifies the "hardest direction" (lowest pass rate)
# 4. Checks symmetry: does cuda-to-opencl ≈ opencl-to-cuda? (interesting finding)
# 5. Checks if omp-to-opencl (hardest: CPU→GPU) has the lowest pass rate
# DELETE the test script after verification.

# Step 6: Show me the full 6-direction × 4-model pass rate matrix
# Key paper finding: "Cross-API translation difficulty ordering"

# Step 7: Git commit and push
# Commit: "Add remaining 3 Rodinia cross-API eval directions (#4-6): opencl-to-cuda, opencl-to-omp, omp-to-opencl (15-16 kernels × 4 models, kernel-centric)"
```

---

## SESSION S-HeCBench — HeCBench Clone + Smoke Test + Eval Batch

> **Status: NOT STARTED.** Planned Day 9 (background, while S12 runs in foreground).
> **Why this session exists:** 120 HeCBench specs exist in `specs/` (schema valid), but the source is not
> cloned locally. This session clones the source, smoke-tests 5+ kernels, and launches eval batch.
> **Paper impact:** §4 Curation shows 3-suite coverage (Rodinia + XSBench + HeCBench). §6 Results adds
> HeCBench pass rates. The 120-spec scale demonstrates framework generality beyond a single benchmark suite.

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Confirm HeCBench is in scope for SC26 (decision made 2026-03-24: YES — include full eval)
- [ ] Which 5 candidate kernels for smoke test?
      Recommended: bfs, backprop, nn, pathfinder, hotspot (same as Rodinia — easy cross-comparison)
      Alternative: Pick simpler ones first: atomicIntrinsics, bezier-surface, binomial
- [ ] Smoke test pass threshold before proceeding to full eval batch?
      Recommendation: at least 5 CUDA + 5 OMP kernels must PASS harness verify

EXTERNAL DEPS:
- [ ] AZURE_OPENAI_API_KEY + ANTHROPIC_API_KEY + GEMINI_API_KEY + GROQ_API_KEY (all 4 models)
- [ ] Network access to clone github.com/zjin-lcf/HeCBench (~3-5 GB, ~500+ benchmarks)
- [ ] Sessions 2+3+3b complete (Rodinia baselines) ✅ DONE

# Session Goal
Clone HeCBench source, verify that existing 120 specs resolve against real source files,
smoke-test 5+ kernels (CUDA + OMP) through the full harness verify pipeline, and launch
a cuda-to-omp eval batch for all passing HeCBench kernels.

# Step 1: Clone HeCBench source (~30 min)
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

git clone https://github.com/zjin-lcf/HeCBench.git HeCBench-master
# Verify clone completed
ls HeCBench-master/ | head -10

# Check that source_dir errors drop from ~120 to near 0
python3 scripts/validate_schema.py --all 2>&1 | grep "source_dir" | wc -l
# Expected BEFORE clone: ~120 errors. Expected AFTER clone: 0 errors (only 15 phantom errors remain).

# Step 2: Smoke test 5 candidate kernels (pick from bfs, backprop, nn, hotspot, pathfinder)
# For each candidate, check if both CUDA and OMP specs exist and source files are present:
ls specs/ | grep "hecbench-bfs"
ls specs/ | grep "hecbench-backprop"

# Run harness verify on 5 CUDA specs
python3 -m harness -v verify specs/hecbench-bfs-cuda.json
python3 -m harness -v verify specs/hecbench-backprop-cuda.json
python3 -m harness -v verify specs/hecbench-nn-cuda.json
python3 -m harness -v verify specs/hecbench-hotspot-cuda.json
python3 -m harness -v verify specs/hecbench-pathfinder-cuda.json

# Run harness verify on 5 OMP specs
python3 -m harness -v verify specs/hecbench-bfs-omp.json
python3 -m harness -v verify specs/hecbench-backprop-omp.json
python3 -m harness -v verify specs/hecbench-nn-omp.json
python3 -m harness -v verify specs/hecbench-hotspot-omp.json
python3 -m harness -v verify specs/hecbench-pathfinder-omp.json

# If a kernel fails: check Makefile (CUDA_HOME, arch flag sm_89, -std=c++17 issues)
# Fix at spec level (build.flags) NOT at source level (hook protection applies)
# If >3 kernels fail smoke test, investigate before proceeding to full batch

# Step 3: Validate all HeCBench specs
python3 scripts/validate_schema.py --all 2>&1 | grep "hecbench" | grep -v "source_dir"
# Expected: 0 non-source-dir errors for HeCBench specs

# Step 4: Launch eval batch (background, while S12 or S13 runs in foreground)
python3 scripts/evaluation/run_eval_batch.py \
  --suite hecbench \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --max-retries 2 \
  --max-failures 10 \
  --resume \
  -v \
  --project-root /home/samyak/Desktop/parbench_sam
# --max-failures 10: skip persistently broken kernels without aborting the batch
# Many HeCBench Makefiles may need fixes — this is expected, treat BUILD_FAIL as data
# Even 20-30 passing kernels (out of 60) is sufficient for the paper

# Step 5: Analyze results
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --suite hecbench \
  --direction cuda-to-omp
# Note pass rate, BUILD_FAIL breakdown, and which kernels passed for paper §6

# Step 6: Update known-issues.md if new KNOWN_FAIL kernels are found
# Format: | `hecbench-XXXX-cuda` | error message | reason |
# File: .claude/rules/known-issues.md — add under new "## HeCBench KNOWN_FAIL" section

# Step 7: Git commit and push
# Stage: HeCBench-master/ (gitignored — verify first), specs/ (if any spec fixes),
#         results/evaluation/hecbench-*/*.json, eval_summary.*
# Commit message: "Add HeCBench source, smoke test N/10 PASS, cuda-to-omp eval batch (M/60 PASS)"
# Push to origin main
```

---

## SESSION 11 — Dashboard Data Refresh

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Run now with partial eval data, or wait for ALL eval sessions (2-10)?
      Recommendation: split into 2 passes — Pass 1 NOW (fix augmentation
      numbers 54/60, fix spec count 60, fix baseline data), Pass 2 after
      all evals (refresh eval data). The augmentation fixes won't need re-doing.
- [ ] Should XSBench be reflected in the dashboard? (Only if Sessions 4-5 done)
- [ ] Any design changes to the dashboard, or purely data refresh?

CLARIFICATIONS:
- [ ] scripts/generate_viz_data.py reads from results/augmentation/eval_cuda.json,
      eval_omp.json, eval_opencl.json — NOT from retest_post_session2.json.
      Are those per-API files current (54/60 data) or stale (old 65-spec data)?
      If stale, the script needs to be updated to read the retest file, or the
      per-API files need regeneration.

EXTERNAL DEPS:
- [ ] PAGES_PASSWORD GitHub Actions secret must be set (check: gh secret list)
- [ ] GitHub Pages must be enabled with source = "GitHub Actions" in repo settings

# Session Goal
Fix all stale data in the visualization dashboard. Regenerate JS data files from
current results. Fix hardcoded numbers in HTML pages. Deploy updated dashboard.

# Why This Matters
The dashboard currently shows pre-fix numbers (65 Rodinia specs, wrong L3/L4 rates,
incomplete eval data). It needs to reflect the actual state for presentations and
the paper's companion website.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Stale files:
  - visualizations/results_data.js (Mar 16 — pre-fix augmentation data)
  - visualizations/build_results_data.js (Mar 16 — pre-fix rodinia baseline)
  - visualizations/eval_results_data.js (Mar 19 — incomplete eval data)
- Stale hardcoded numbers in HTML:
  - overview.html: "65 specs" for Rodinia (should be 60), wrong augmentation pass rates
  - augmentation_deep_dive.html: L3=29/60, L4=1/60 (should be 54/60 at all levels)
  - results.html: BASELINE object has wrong numbers
- Design spec: visualizations/DESIGN.md (reference for any UI changes)

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Regenerate data files
python3 scripts/generate_viz_data.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard

# Step 3: Fix hardcoded numbers in HTML pages
# Read each HTML file and search for stale values:
#
# overview.html:
#   - "65" Rodinia specs → "60"
#   - Augmentation pass rates: update to 54/60 at all levels (level-invariant)
#   - LLM eval stats: update with latest pass rates from eval_summary
#   - Total specs: should reflect 60 Rodinia + 4 XSBench = 64 total
#
# augmentation_deep_dive.html:
#   - L1 PASS stat card → 54/60
#   - L2 PASS stat card → 54/60
#   - L3 PASS stat card → 54/60
#   - L4 PASS stat card → 54/60
#   - Fix Chart.js data if hardcoded
#
# results.html:
#   - BASELINE object: update L1-L4 pass counts to 54
#   - LLM eval table at bottom: update with current results
#
# llm_evaluation.html:
#   - PER_MODEL_RESULTS: update with current kernel x model matrix
#   - KPI cards: update pass rate, total tasks, failure rates

# Step 4: Add XSBench to the overview and landscape pages
# Update overview.html stats to include XSBench
# Update benchmark_landscape.html if it has hardcoded suite data

# Step 5: Verification — write a small test script that:
# 1. Loads each JS data file and validates it's valid JavaScript
# 2. Checks key numbers match eval_summary.json
# 3. Searches HTML files for any remaining "65" referring to Rodinia (wrong count)
# 4. Validates all Chart.js chart configs reference correct data
# DELETE the test script after verification.

# Step 6: Show me what changed (diff summary)

# Step 7: Git commit and push
# Commit all changed visualization files
# Message: "Refresh dashboard data: 54/60 augmentation, complete eval results, XSBench"
# Push to origin main. (This triggers GitHub Pages deploy via workflow)
```

---

## SESSION 12 — Paper Draft: Intro + Related Work + Methodology (§1-§5)

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Author list and order: Sprint plan says "Samyak, Erel, Gal (advised)."
      Are Niranjan, Le Chen, Tomer co-authors? (For anonymous submission,
      names are hidden, but structure depends on contribution count)
- [ ] Paper-drafter agent (Opus) or main Claude Code session for writing?
- [ ] Lock the 3-4 numbered contributions. Candidates:
      a) ParBench framework (first build+run+verify for LLM parallel translation)
      b) Augmentation engine (6 AST transforms, level-invariant)
      c) Empirical evaluation (N models, M directions, K kernels)
      d) Kernel-centric translation + complexity classification
      e) Failure taxonomy (structural analysis of failure modes)
      Select 3-4 and rank them.
- [ ] "No reasoning models" — should the paper explain WHY they're excluded
      (strengthens rationale) or just omit them silently?
- [ ] M11 (kernel-centric translation) — present as:
      a) A contribution (evaluation methodology innovation)
      b) A design decision (in Framework section)
      c) A limitation/discussion point
      NOTE (Session 1.6): Kernel-centric is now universal (all 180 specs, no fallback,
      per-API family rules). This strengthens the contribution story vs. Rodinia-only.

DATA/INFO:
- [ ] Paraval paper differentiators (from reading M3 — MUST be done before S12)
- [ ] Full citation list: BibTeX entries or at minimum publication details for
      Paraval, ParEval (HPDC 2024), BabelTower (ICML 2022), TransCoder,
      HPCorpus, OMPify, SWE-bench, HumanEval, Power of Evolve paper,
      Rodinia (Che et al. 2009), and any others
- [x] Model identities RESOLVED (Gal, 2026-03-23): azure-gpt-4.1 · claude-sonnet-4-6 · gemini-2.5-flash-lite · groq-llama-3.3-70b-versatile
- [ ] Hardware specs: exact output of `nvcc --version` and `gcc --version`
      for the paper's experimental setup table

CLARIFICATIONS:
- [ ] HeCBench: 120 specs exist but source not cloned. Is HeCBench still in
      scope for the paper, or described as "curated but evaluation pending"?
- [ ] Should augmentation mention L3/L4 (tested, found level-invariant) or
      strictly report only L0/L1/L2 per Gal's instruction?

EXTERNAL DEPS:
- [x] Session 6 (paper outline) COMPLETE — docs/paper_outline.md exists (commit 257b992).
      Read it fully at the start of this session — it is the roadmap.
- [ ] Evaluation data from Session 2+ is helpful but not strictly required
      (paper-drafter can use "TBD" placeholders per its rules)

# Session Goal
Write the first 5 sections of the SC26 paper in Markdown: Introduction, Related Work,
Framework, Benchmark Curation, and Evaluation Methodology.

# Context
- Paper outline: docs/paper_outline.md (read first — this is the roadmap)
- Sprint plan: docs/sprint_to_SC26.md (for meeting decisions and paper targets)
- Eval results: results/evaluation/eval_summary.md
- Augmentation results: results/augmentation/retest_post_session2.md
- Framework code: harness/, c_augmentation/, scripts/evaluation/
- Schema: schema/spec_schema.json
- Meeting notes: meeting_notes/ (for Gal's strategic decisions)
- SC26 format: double-column, 10 pages + appendices

# Writing Guidelines
# - Academic tone, precise language, no marketing fluff
# - Every claim backed by data or citation
# - Use \cite{} placeholders for references (will be resolved in LaTeX)
# - Include figure/table placeholders: [FIGURE: description] or [TABLE: description]
# - Keep to target page counts from outline
# - Gal's decisions: NO reasoning models, conservative augmentation (L1-L2), omit build times
# - Technical vocabulary: "parallel code translation" (not "migration"), "spec", "harness",
#   "level-invariant", BUILD_FAIL/RUN_FAIL/VERIFY_FAIL (always this capitalization)

# PAPER-DRAFTER AGENT USAGE (Opus model):
# Invoke for the actual writing: "Use the paper-drafter agent to write §1 Introduction"
# The agent MUST pre-read these files before writing any section:
#   1. docs/paper_outline.md          ← section structure, claims, page targets (ROADMAP)
#   2. results/evaluation/eval_summary.md      ← actual pass rates and failure counts
#   3. results/augmentation/retest_post_session2.md  ← 54/60 PASS level-invariance
#   4. docs/sprint_to_SC26.md         ← meeting decisions and Gal's constraints
#   5. meeting_notes/*.md             ← all advisor decisions
# Agent writing rules (non-negotiable — see .claude/agents/paper-drafter.md):
#   1. Data-backed claims only — cite specific numbers from results files, or write TBD
#   2. \cite{placeholder} for all references
#   3. [FIGURE: description] and [TABLE: description] for visual placeholders
#   4. No fabricated numbers — if data doesn't exist, write "TBD (pending Session N)"
#   5. Gal constraints: no reasoning models, L0-L4 augmentation, omit build times, temp=0
# Page targets (SC26 double-column):
#   §1 Introduction: 1.5p | §2 Related Work: 1.0p | §3 Framework: 2.0p
#   §4 Benchmark Curation: 1.0p | §5 Evaluation Methodology: 1.0p
# Models under evaluation (Gal, 2026-03-23) — 4 models total:
#   azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile
# Core claims the agent MUST support with actual data:
#   - GPT-4.1: 52.9% PASS (cuda-to-omp L0) — from eval_summary.md
#   - Llama-3.3-70B: 29.4% PASS — from eval_summary.md
#   - Claude Sonnet 4.6: 70.6% PASS (12/17, cuda-to-omp L0) — from eval_summary.json (commit f0b4f98)
#   - Gemini 2.5 Flash-Lite: 23.5% PASS (4/17, cuda-to-omp L0) — from eval_summary.json (commit f0b4f98)
#   - 54/60 PASS at L1–L4 (level-invariant) — from augmentation results
#   - BUILD_FAIL dominates (~70% of failures) — from eval_summary.json
#   - 6 translation directions across 3 APIs — from Translation Direction Matrix
#   - All 4 model L0 baselines available — use actual numbers, no TBD for model data
# Output file: docs/paper_draft.md (agent appends if exists, creates if not)

# Step 1: Read docs/paper_outline.md fully (the roadmap for this entire writing session)
# Step 2: Read results/evaluation/eval_summary.md for all current pass rates
# Step 3: Invoke paper-drafter agent for each section (§1–§5) sequentially
# Step 4: Review draft end-to-end, verify data citations are accurate
# Step 5: Git commit and push
# Message: "SC26 paper draft: §1-§5 (intro, related work, framework, curation, methodology)"
```

---

## SESSION 13 — Paper Draft: Results + Discussion + Conclusion (§6-§8)

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Proceed with partial data or wait for ALL eval sessions (2,3,3b,7,8,9,10)?
      Minimum viable: ✅ MET — Sessions 2+3+3b complete (4 models, 1 direction, L0 done).
      Recommended: Sessions 2+3+3b+7 at minimum (4 models, L0/L1/L2). S7 not yet run.
      Models (Gal, 2026-03-23): azure-gpt-4.1 · claude-sonnet-4-6 · gemini-2.5-flash-lite · groq-llama-3.3-70b-versatile
- [ ] Threats to validity — rank these by importance for the Discussion section:
      a) Temperature=0 (deterministic but may not represent average behavior)
      b) Single seed for augmentation
      c) Limited models (4 models — reasonable diversity across vendors)
      d) Limited benchmark suites
      e) Single GPU hardware (RTX 4070 only)
      f) Kernel-centric scope (excludes project-level restructuring)
      g) No performance timing (only correctness)
- [ ] Future work — select 3-4 items to highlight:
      a) More suites (HeCBench, Polybench, NAS)
      b) More APIs (SYCL, HIP, OpenACC, OMP target)
      c) Agentic repair (ParaCodex)
      d) Performance analysis (Niranjan's three-tier timing)
      e) Multi-file/project-level translation
      f) Cross-hardware (AMD, Intel GPUs)
- [ ] Self-repair data: --max-retries produces attempt-level data. Should
      self-repair be a subsection of Results or a minor finding?
- [ ] Speedup/performance: M6 (timing metrics) is not implemented. Is the
      paper purely correctness-focused, or should wall-clock timing be reported
      as a proxy? Gal said "omit build times" but Niranjan wanted Tier 1/2.

EXTERNAL DEPS:
- [ ] Session 12 must be complete (paper §1-§5 exist in docs/paper_draft.md)
- [ ] At minimum, Session 2 must be complete for actual data in Results section
- [ ] Ideally, ALL eval sessions (2,3,7,8,9,10) complete for comprehensive data

# Session Goal
Write the data-driven sections of the SC26 paper: Results, Discussion, and Conclusion.

# Context
- Paper draft so far: docs/paper_draft.md (§1-§5 from Session 12)
- ALL eval results must be available: results/evaluation/eval_summary.md
- Augmentation results: results/augmentation/retest_post_session2.md
- XSBench results from Session 8

# Writing Guidelines
# - §6 Results: Lead with headline numbers, then drill into details
#   - Use actual numbers from eval_summary.md — do NOT make up data
#   - Include figure/table placeholders with exact data they should contain
# - §7 Discussion: Be honest about limitations
#   - Multi-file BUILD_FAIL ceiling (document in design_concern_multifile_translation.md)
#   - Threats to validity: temperature=0, single seed, limited models
# - §8 Conclusion: 3-4 sentences summarizing contributions + 2-3 future work items

# PAPER-DRAFTER AGENT USAGE (Opus model — same as Session 12):
# Invoke: "Use the paper-drafter agent to write §6 Results"
# For §6–§8, the agent needs ALL Session 12 pre-reads PLUS:
#   6. docs/paper_draft.md            ← §1-§5 from Session 12 (maintain consistency)
#   7. results/evaluation/            ← ALL direction results (all 6+ directions)
#   8. docs/paper_outline.md §6 Figure & Table Inventory (F1–F6, T1–T9 with data sources)
# §6 Results structure (from paper_outline.md):
#   6.1 Overall Pass Rates | 6.2 Failure Taxonomy | 6.3 Per-Kernel Analysis
#   6.4 Self-Repair Effectiveness | 6.5 Augmentation Robustness | 6.6 Cross-Direction Results
# Figures referenced in §6 (use paper_outline.md Figure inventory for exact specs):
#   F2: Kernel × Model heatmap (cuda-to-omp L0)
#   F3: Failure taxonomy stacked bar (BUILD_FAIL / RUN_FAIL / VERIFY_FAIL / EXTRACTION_FAIL)
#   F4: Augmentation robustness L0 vs L1 vs L2 (TBD until Session 7 complete)
#   F5: Cross-direction comparison (TBD until Sessions 9/10/10b complete)
#   F6: XSBench multi-API results (TBD until Session 8 complete)
# If direction data is missing: write "TBD (pending Session N eval run)" — NEVER fabricate.
# Output: APPEND to docs/paper_draft.md (do not overwrite §1-§5)

# Step 1: Read docs/paper_outline.md §6–§8 structure and Figure inventory
# Step 2: Read ALL available eval results (eval_summary.md + per-direction files)
# Step 3: Invoke paper-drafter agent for §6 Results, §7 Discussion, §8 Conclusion
# Step 4: Invoke paper-drafter agent to write Abstract (now all sections exist)
# Step 5: Review complete draft end-to-end, verify all data citations
# Step 6: Git commit and push
# Message: "SC26 paper draft: §6-§8 (results, discussion, conclusion) + abstract"
```

---

## SESSION 14 — Publication Figures

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Figure format: matplotlib/seaborn (produces PDF/SVG natively, standard
      for academic publishing) or Chart.js (canvas-rendered, web only)?
      Recommendation: matplotlib for paper figures, Chart.js only for dashboard.
- [ ] System architecture diagram (Figure 1): hand-drawn in draw.io/TikZ, or
      should Claude attempt TikZ code? This is typically manual design work.
- [ ] Is the 6-figure list final? Sprint plan Day 17 adds "self-repair curve"
      and "per-kernel speedup" but omits architecture diagram. Finalize the
      list before starting.
- [ ] Grayscale printability: add pattern fills (hatching, dots) for B&W
      printing, or rely on color only?
- [ ] Figure save location: visualizations/figures/ or docs/paper/figures/?

DATA/INFO:
- [ ] Complete eval data must exist (eval_summary.json with all models/directions)
- [ ] Paper draft must exist (to match [FIGURE:] and [TABLE:] placeholders)

EXTERNAL DEPS:
- [ ] Sessions 2-10 must be complete (all eval data)
- [ ] Sessions 12-13 must be complete (paper draft with figure placeholders)
- [ ] If using matplotlib: pip install matplotlib seaborn (check if installed)

# Session Goal
Generate publication-quality figures and tables for the SC26 paper. These will be
used in both the paper and the dashboard.

# Context
- Design spec: visualizations/DESIGN.md (Okabe-Ito palette, Chart.js, academic aesthetic)
- Paper draft: docs/paper_draft.md (check [FIGURE:] and [TABLE:] placeholders)
- Paper outline: docs/paper_outline.md → "Figure & Table Inventory" section (F1–F6 specs,
  data sources, and AVAILABLE/TBD status for each figure and table)
- Eval data: results/evaluation/eval_summary.json
- Augmentation data: results/augmentation/retest_post_session2.json

# Figures Needed (from paper outline):
# 1. System architecture diagram (ParBench framework overview)
# 2. Kernel × Model heatmap (pass/fail for cuda-to-omp at L0)
# 3. Failure taxonomy stacked bar chart (BUILD_FAIL vs RUN_FAIL vs VERIFY_FAIL)
# 4. Augmentation robustness: L0 vs L1 vs L2 pass rates per model
# 5. Cross-direction comparison: cuda-to-omp vs omp-to-cuda vs cuda-to-opencl
# 6. XSBench multi-API results (if available)

# Tables Needed:
# 1. Kernel × API availability matrix (Rodinia + XSBench)
# 2. Per-kernel detailed results table
# 3. Model comparison table (pass rates, failure counts)

# Generate these as:
# - SVG or PNG files in visualizations/figures/ for the paper
# - Chart.js configs embedded in dashboard HTML for the website
# Use the Okabe-Ito colorblind-safe palette from DESIGN.md

# Step 1-5: Create figures, verify they match data, commit and push
# Message: "Add publication figures for SC26 paper"
```

---

## SESSION 15 — Paper Review & Polish

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Has Gal reviewed the Sessions 12-13 draft? Advisor review BEFORE
      automated polishing is standard practice. Gal's feedback could require
      structural changes, not just polishing.
- [ ] What constitutes "ready" — content complete? Data accurate? Citations
      resolved? All of the above?
- [ ] Should Claude flag issues for your review, or make edits directly?
- [ ] Does SC26 have a policy on AI-assisted paper writing? Should this
      be disclosed?

DATA/INFO:
- [ ] Word count target: ~8,000-10,000 words (proxy for 10 double-column pages)
- [ ] Co-author feedback notes (if any) from Gal/Erel review

EXTERNAL DEPS:
- [ ] Sessions 12, 13, 14 must be complete
- [ ] Ideally, Gal has reviewed the draft between S13 and S15

# Session Goal
Review the complete paper draft for consistency, accuracy, and SC26 readiness.

# AGENT USAGE:
# Use the paper-drafter agent (Opus) for data accuracy review:
#   "Use the paper-drafter agent to review docs/paper_draft.md for data accuracy"
# Use the self-critic agent for adversarial review:
#   "Use the self-critic agent to review docs/paper_draft.md for rationalization patterns"
# Cross-check docs/paper_outline.md against the draft to verify:
#   - All 8 sections present and at correct page counts
#   - All 6 figures (F1-F6) referenced with correct [FIGURE:] placeholders
#   - All 9 tables (T1-T9) present with correct [TABLE:] placeholders
#   - All 10 translation directions from the Direction Matrix are covered where relevant
#   - Gal constraint checklist (13 items in paper_outline.md) fully satisfied

# Steps:
# 1. Read docs/paper_draft.md end-to-end
# 2. Read docs/paper_outline.md (cross-check sections, figures, tables, Gal checklist)
# 3. Cross-check ALL numbers against results/evaluation/eval_summary.json
# 4. Invoke paper-drafter agent for data accuracy review
# 5. Invoke self-critic agent for adversarial review of claims and rationalization
# 6. Verify all figure/table references are consistent with paper_outline.md inventory
# 7. Check for claims not backed by data
# 8. Ensure related work positioning is accurate (3-paper matrix: ParEval, ParEval-Repo, ParBench)
# 9. Fix any inconsistencies, typos, or unclear passages
# 10. Verify page count is within SC26 limits (~10 pages double-column)
# 11. Commit and push final reviewed draft
# Message: "SC26 paper: final review and polish"
```

---

## SESSION 17 — LaTeX Transfer + Final Formatting

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Which SC26 LaTeX template? (ACM sigconf for main technical papers track,
      or IEEE/custom for workshops). Check the CFP.
- [ ] Compile locally or use Overleaf?
      - LaTeX is NOT installed on the Linux GPU machine
      - Options: (a) sudo apt install texlive-full (~5GB),
                 (b) Use Overleaf (needs Erel's project link),
                 (c) Minimal texlive install
- [ ] Who does final LaTeX formatting — Claude Code or a team member on Overleaf?

DATA/INFO:
- [ ] Paper draft must exist at docs/paper_draft.md (Sessions 12-13)
- [ ] Figures must exist in the chosen format (Session 14)
- [ ] Start a references.bib file during Sessions 12-13 (do NOT defer all
      20+ BibTeX entries to Session 17)
- [ ] Has Erel created the Overleaf project? (Sprint plan Open Question #6)

CLARIFICATIONS:
- [ ] Is April 8 deadline for full paper or abstract registration?
      SC conferences often have separate deadlines.
- [ ] Does SC26 require LaTeX source upload or PDF only?

EXTERNAL DEPS:
- [ ] Sessions 12-15 must be complete
- [ ] Download LaTeX template BEFORE Session 17 (one wget command, resilient
      to deadline-day network issues)
- [ ] If Overleaf: get project link from Erel
- [ ] If local: install texlive

# Session Goal
Convert the Markdown paper draft to SC26 LaTeX template format.

# Steps:
# 1. Download SC26 LaTeX template (ACM or IEEE format — check SC26 CFP)
# 2. Convert docs/paper_draft.md sections to LaTeX
# 3. Insert figures from visualizations/figures/
# 4. Format tables in LaTeX
# 5. Add bibliography (BibTeX entries for all \cite{} references)
# 6. Verify compilation (pdflatex or latexmk)
# 7. Check page count and formatting
# 8. Commit LaTeX source to docs/paper/ or a separate directory

# This may need to be done on a machine with LaTeX installed.
# If not available locally, prepare for Overleaf upload.

# Commit: "SC26 paper: LaTeX version from Markdown draft"
```

---

## SESSION 16 — Anonymous GitHub Repo (M1)

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Confirm SC26 requires double-blind review. Check the actual CFP.
- [ ] Anonymous repo approach:
      a) New GitHub organization (cleanest for double-blind)
      b) Anonymous GitHub service (anonymous.4open.science)
      c) Fresh repo on existing account with sanitized content
- [ ] What to include in the anonymous repo:
      a) Code only (specs, harness, c_augmentation, scripts)?
      b) Code + results (sanitized)?
      c) Code + results + dashboard?
- [ ] Should the dashboard be mirrored anonymously?
      (Requires new GitHub Pages deployment with separate password)
- [ ] When to create: now (can be updated), or April 7 (final version only)?

DATA/INFO:
- [ ] SC26 CFP URL (for exact anonymization requirements)
- [ ] If new GitHub org: need a secondary GitHub account/email
- [ ] List of co-authors for the submission system (separate from the anon repo)

EXTERNAL DEPS:
- [ ] All paper content finalized (Sessions 12-15)
- [ ] Session 17 (LaTeX) must be complete before creating the anonymous repo
      (so the repo contains the final LaTeX source)

# Session Goal
Create an anonymous version of the ParBench repository for SC26 double-blind submission.

# Steps:
# 1. Create a new branch or separate repo with author info removed
# 2. Sanitize commit messages (remove names, emails)
# 3. Remove or anonymize meeting_notes/, presentations/
# 4. Keep specs/, harness/, c_augmentation/, scripts/, results/, visualizations/
# 5. Update README with anonymous references
# 6. Password-protect if needed via staticrypt
# 7. Document the process for the team

# Note: This may require creating a new GitHub organization or using GitHub's
# anonymous submission tools. Check SC26's specific requirements.

# Commit: "Prepare anonymous submission repo (M1)"
# Push to the anonymous remote.
```

---

## SESSION 18 — Final Review + Submit

```
ultrathink

## BEFORE YOU START — What I Need From You

DECISIONS:
- [ ] Who submits — Samyak or Gal? Submitting author needs an account on the
      submission system.
- [ ] Should supplementary materials be submitted? (Artifact description,
      anonymous repo link, dashboard URL)

DATA/INFO:
- [ ] SC26 submission system URL (EasyChair? HotCRP? Linklings?)
- [ ] Submission account credentials (create BEFORE April 8)
- [ ] Deadline timezone: typically 23:59 AoE (UTC-12). Confirm.
- [ ] Required forms: copyright transfer? conflict of interest declarations?
      author registration?
- [ ] Co-author availability on April 7-8 for final approval

CLARIFICATIONS:
- [ ] Backup plan if submission system is down on April 8?
      Recommendation: submit by April 7. Have program chair contact info ready.

EXTERNAL DEPS:
- [ ] ALL previous sessions must be complete
- [ ] Anonymous GitHub repo must be live (Session 16)
- [ ] LaTeX PDF must compile cleanly (Session 17)
- [ ] All co-authors must approve final version

# Session Goal
Final review of LaTeX paper, last-minute data verification, and submission.

# Steps:
# 1. Read the compiled PDF end-to-end
# 2. Verify all figures render correctly
# 3. Cross-check data one final time against eval_summary.json
# 4. Ensure anonymous submission requirements are met
# 5. Upload to submission system
# 6. Tag the repo with the submission commit: git tag sc26-submission
# 7. Push the tag: git push origin sc26-submission

# Commit: "SC26 submission: final version"
```

---

## VERIFICATION SESSION TEMPLATE (use after any task session)

```
ultrathink

# Post-Session Verification
# Run after completing any session to verify overall project health.

source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# 1. Schema validation (expect ~135 known errors from HeCBench + phantoms)
python3 scripts/validate_schema.py --all 2>&1 | tail -5

# 2. Unit tests (expect 15 PASS)
python3 -m pytest c_augmentation/test_transforms.py -v

# 3. Eval coverage gaps
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda opencl-to-omp omp-to-opencl \
  --expected-levels 0 1 2

# 4. Git status — should be clean after session commit
git status
git log --oneline -3
```


---

## WORKTREE SESSION PROMPTS

> The following 6 sessions run in isolated git worktrees via autonomous Claude Code agents.
> Each prompt is **hermetic** — it contains every file path, command, expected output, and
> edge-case decision the agent will need. No follow-up questions should be needed.
>
> **How to start:** `git worktree add ../parbench_wt_sNN -b worktree/sNN-name`
> then `claude --project-dir ../parbench_wt_sNN` and paste the prompt below.
> When the agent commits, merge back: `git merge --no-ff worktree/sNN-name`

---

## SESSION W-S16 — Anonymous GitHub Repo (WORKTREE-SAFE)

> **Status: NOT STARTED. Can launch immediately — zero dependencies.**
> **Worktree safe because:** This session creates a SEPARATE GitHub repository. It does
> not modify any file in the main ParBench repo. The worktree is used only as a workspace
> for filtering commit history; the output goes to a new remote.
> **Paper impact:** SC26 requires double-blind submission. The anonymous repo URL goes
> in the artifact submission field. Without it, the paper cannot be submitted.

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Project root in this worktree: use $(git rev-parse --show-toplevel) to find it.
You have full access to the codebase but the Rodinia submodule is empty — that is expected.
DO NOT run harness verify or any script that reads rodinia/rodinia-src/ — it won't work.

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] SC26 requires double-blind anonymous submission — confirmed from CFP
- [x] Anonymous repo approach: fresh repo on new GitHub account (cleanest for double-blind)
- [x] Include: specs/, harness/, c_augmentation/, scripts/, schema/, results/, visualizations/
- [x] Exclude: meeting_notes/, presentations/, docs/sprint_to_SC26.md (contains author info),
      any file containing "samyak", "jhaveri", "erel", "gal", "niranjan" as literal text
- [x] Repository name for anonymous repo: "parbench-sc26-anon" (or similar neutral name)

DECISIONS NEEDED FROM YOU (resolve before proceeding):
- [ ] GitHub account for anonymous repo: You need a secondary GitHub account with no
      connection to the authors. Ask Samyak for the account credentials or URL before proceeding.
      If no secondary account is available, use https://anonymous.4open.science (no account needed).
      This is a BLOCKING decision — do NOT proceed without it.

# Session Goal
Create an anonymous version of the ParBench repository stripped of all author-identifying
information, for SC26 double-blind submission. The anonymous repo must compile and run
the evaluation pipeline from scratch without revealing author identities.

# What "anonymous" means for SC26:
# - No author names in commit messages
# - No author names in file contents (code comments, docstrings, README, docs/)
# - No institution names (UCSB, Technion, etc.)
# - No references to specific meetings, advisors, or lab-internal terminology
# - Rodinia source is external — its commit messages are NOT your responsibility

# Step 1: Orient — understand what contains author info
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)

# Find files containing author names (case-insensitive)
grep -rli "samyak\|jhaveri\|erel\|gal\|niranjan\|ucsb\|technion" \
  --include="*.py" --include="*.md" --include="*.json" --include="*.html" \
  --include="*.js" --include="*.txt" \
  --exclude-dir=".git" --exclude-dir="rodinia" --exclude-dir="HeCBench-master" \
  --exclude-dir="xsbench" --exclude-dir="env_parbench" \
  . 2>/dev/null | sort
# Document everything this finds. These files need sanitization or exclusion.

# Step 2: Create sanitized file list
# Files to EXCLUDE entirely from anonymous repo (they cannot be sanitized):
# - meeting_notes/ (contains advisor names and discussion)
# - presentations/ (contains author names on slides)
# - docs/sprint_to_SC26.md (contains team member names + meeting notes)
# - .claude/ directory (contains prompts that may mention team)
# - env_parbench/ (local venv, gitignored anyway)
# - rodinia/ (submodule — external project, not your code)

# Files to INCLUDE with sanitization (replace names → "ParBench Team"):
# - README.md — replace author names with "The ParBench Team"
# - Any .py files with "# Author: Samyak" style comments → remove the comment
# - CLAUDE.md — remove specific user paths, replace with generic paths
# - docs/paper_outline.md — replace names in author list → "Author N"

# Step 3: Create the anonymous repo
# Option A: Using anonymous.4open.science (if no secondary GitHub account)
#   Go to https://anonymous.4open.science in a browser
#   Upload the sanitized content via the web interface
#   Get the anonymous URL for the submission

# Option B: Using git-filter-repo to create a sanitized history
# Install git-filter-repo: python3 -m pip install git-filter-repo
git clone . ../parbench_anon_work --no-local
cd ../parbench_anon_work

# Create a mailmap to sanitize author identity in commit history
cat > /tmp/mailmap_anon.txt << 'EOF'
ParBench Author <anon@parbench-sc26.invalid> <samyak@whatever.edu>
ParBench Author <anon@parbench-sc26.invalid> <sjhaveri@whatever.edu>
ParBench Author <anon@parbench-sc26.invalid> Samyak Jhaveri <sjhaveri@whatever.edu>
EOF
# Add any other author email patterns found with: git log --format="%ae" | sort -u

# Apply the mailmap via git-filter-repo
git filter-repo --mailmap /tmp/mailmap_anon.txt --force

# Remove excluded directories entirely from history
git filter-repo --path meeting_notes/ --invert-paths --force
git filter-repo --path presentations/ --invert-paths --force
git filter-repo --path docs/sprint_to_SC26.md --invert-paths --force

# Step 4: Sanitize file contents in the anonymous working copy
# Replace author names in remaining files
# Find and replace in all non-gitignored files:
ANON_DIR=../parbench_anon_work
grep -rli "samyak\|jhaveri" "$ANON_DIR" \
  --exclude-dir=".git" --exclude-dir="env_parbench" | while read f; do
  echo "Sanitizing: $f"
  sed -i 's/Samyak Jhaveri/ParBench Author/gi; s/samyak/parbench_user/gi' "$f"
done

grep -rli "erel\|gal\|niranjan" "$ANON_DIR" --exclude-dir=".git" | while read f; do
  echo "Sanitizing: $f"
  sed -i 's/Erel Segal/ParBench Advisor/gi; s/Gal Oren/ParBench Advisor/gi' "$f"
done

# Replace institution names
grep -rli "ucsb\|technion" "$ANON_DIR" --exclude-dir=".git" | while read f; do
  sed -i 's/UCSB/[Institution Anonymized]/gi; s/Technion/[Institution Anonymized]/gi' "$f"
done

# Step 5: Update README.md for anonymous submission
# The README must explain the project WITHOUT revealing identities.
# Key elements for an anonymous README:
# - What ParBench is (framework for LLM parallel code translation evaluation)
# - How to install and run it (instructions)
# - How to reproduce results (commands)
# - Acknowledgment: "Submitted to SC26 (under review)"
# Draft the README — do NOT include author names, institutions, or advisor names

# Step 6: Verify sanitization is complete
cd "$ANON_DIR"
grep -rli "samyak\|jhaveri\|erel\|gal\|niranjan\|ucsb\|technion" \
  --exclude-dir=".git" . 2>/dev/null
# Expected: empty output (no hits). If any files remain, sanitize them.

# Also check git log for author name leakage:
git log --format="%an <%ae>" | sort -u
# Expected: only "ParBench Author <anon@parbench-sc26.invalid>"

# Step 7: Push to anonymous repo
# IF using secondary GitHub account:
# git remote add anon https://github.com/ANON_ACCOUNT/parbench-sc26-anon.git
# git push anon main

# IF using anonymous.4open.science:
# Follow the web interface instructions at https://anonymous.4open.science
# Upload the git bundle: git bundle create parbench-sc26-anon.bundle --all
# Then upload the .bundle file to the service

# Step 8: Test the anonymous repo
# Clone the anonymous repo to a temp directory and verify it works:
git clone ../parbench_anon_work /tmp/parbench_anon_test
cd /tmp/parbench_anon_test
python3 scripts/validate_schema.py --all 2>&1 | tail -5
# Expected: ~135 known errors (HeCBench + phantoms), no new errors
python3 -m pytest c_augmentation/test_transforms.py -v 2>&1 | tail -5
# Expected: 15 PASS
rm -rf /tmp/parbench_anon_test

# Step 9: Document the anonymous repo URL
# Write the URL to docs/anonymous_repo_url.txt (this file stays in the MAIN repo,
# not the anonymous repo — it's for Samyak's reference during submission)
echo "SC26 Anonymous Repo URL: [URL from Step 7]" > docs/anonymous_repo_url.txt
echo "Generated: $(date)" >> docs/anonymous_repo_url.txt

# Step 10: Commit the documentation to the MAIN worktree
# NOTE: Do NOT commit the sanitized repo content into the main repo.
# Only commit the reference URL file.
git add docs/anonymous_repo_url.txt
git commit -m "M1: Add anonymous repo URL reference for SC26 submission"
```

---

## SESSION W-S14 — Publication Figures (WORKTREE-SAFE)

> **Status: NOT STARTED. Can launch immediately — uses only existing L0 data.**
> **Worktree safe because:** This session reads `results/evaluation/eval_summary.json` (present
> in worktree as a tracked file) and writes to `docs/paper/figures/` (new directory). It does not
> touch any eval pipeline, specs, or Rodinia source. It creates ONE new script and figure files.
> **Regenerate this session after S7/S9/S10 complete** to add L1/L2 and multi-direction data.
> **Paper impact:** F2-F6 in the paper are generated here. The paper cannot go to LaTeX without them.
>
> **Current data available (L0 cuda-to-omp, 4 models, 17 kernels):**
> claude=12/17 PASS (70.6%), azure=9/17 (52.9%), llama=5/17 (29.4%), gemini=4/17 (23.5%)
> BUILD_FAIL=26, RUN_FAIL=10, EXTRACTION_FAIL=2, VERIFY_FAIL=0
> Complexity: single_file=7/12 PASS, multi_to_single=21/44, multi_to_multi=2/12

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Find the project root with: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY in this worktree — that is expected and fine.
This session does NOT need Rodinia source. It reads results/evaluation/eval_summary.json
and generates matplotlib figures for the SC26 paper.

Key data sources (all present in this worktree as tracked files):
- results/evaluation/eval_summary.json       ← primary data source (68 L0 results)
- results/evaluation/eval_summary.md         ← human-readable summary
- results/augmentation/retest_post_session2.md ← 54/60 PASS at L0-L4 (level-invariant)
- docs/paper_outline.md                      ← Figure inventory F1-F6 with specs
- visualizations/DESIGN.md                   ← Okabe-Ito palette, aesthetic guidelines

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] Figure format: matplotlib/seaborn producing PDF + PNG (PDF for LaTeX, PNG for dashboard)
- [x] Color palette: Okabe-Ito colorblind-safe (from visualizations/DESIGN.md)
- [x] Figure save location: docs/paper/figures/ (create this directory if absent)
- [x] Figures for LaTeX: PDF format (vectorized)
- [x] Grayscale printability: use hatching patterns in addition to color
- [x] System architecture diagram (F1): Skip for now — this requires draw.io/TikZ design work
      that needs Samyak's creative input. Focus on F2-F6 (data-driven figures).
- [x] Initial run: use L0 cuda-to-omp data only. Mark multi-direction figures as TBD placeholders.

# Session Goal
Generate publication-quality figures F2-F6 for the SC26 paper using existing L0 results.
Create a reusable figure generation script so figures can be regenerated when more data arrives.

# Step 1: Setup
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Verify matplotlib is installed
python3 -c "import matplotlib, seaborn; print('matplotlib:', matplotlib.__version__, '| seaborn:', seaborn.__version__)"
# If not installed:
python3 -m pip install matplotlib seaborn

# Create output directory
mkdir -p docs/paper/figures

# Verify data source
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    data = json.load(f)
print('Total tasks:', data.get('total_tasks'))
print('Models:', list(data.get('by_model', {}).keys()))
print('Directions:', list(data.get('by_direction', {}).keys()))
"
# Expected: total_tasks=68, 4 models, 1 direction (cuda-to-omp)

# Step 2: Read docs/paper_outline.md — Figure inventory section
# This tells you the exact specs for each figure:
# F1: System architecture diagram — SKIP (manual design)
# F2: Kernel × Model heatmap (cuda-to-omp L0) — 17×4 matrix, PASS/BUILD_FAIL/RUN_FAIL/EXTRACTION_FAIL
# F3: Failure taxonomy stacked bar — per model, stacked BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL
# F4: Augmentation robustness — L0 vs L1 vs L2 pass rates per model (TBD until S7 done)
# F5: Cross-direction comparison — cuda-to-omp vs omp-to-cuda vs cuda-to-opencl (TBD until S9/S10)
# F6: XSBench multi-API results (TBD until S8 done)

# Step 3: Create the figure generation script
# Create scripts/evaluation/generate_paper_figures.py
# This script MUST:
# a) Read all data from results/evaluation/eval_summary.json (never hardcode numbers)
# b) Accept --project-root argument (like all other scripts in this codebase)
# c) Accept --output-dir argument (default: docs/paper/figures/)
# d) Accept --format argument (default: "pdf,png" — generates both)
# e) Accept --figures argument (default: all — allow "f2,f3" to generate specific ones)
# f) Be rerunnable — overwrite existing figure files without error
# g) Print progress: "Generating F2: Kernel x Model heatmap... saved to docs/paper/figures/f2_heatmap.pdf"

# Color palette (Okabe-Ito) — use these exact hex codes from DESIGN.md:
# PASS: #009E73 (green)
# BUILD_FAIL: #E69F00 (orange)
# RUN_FAIL: #CC79A7 (pink)
# VERIFY_FAIL: #0072B2 (blue)
# EXTRACTION_FAIL: #D55E00 (vermilion)
# Background: white, grid: light gray (#EEEEEE)

# Figure specifications:

# F2: Kernel × Model Heatmap
# - 17 rows (kernels) × 4 columns (models)
# - Cell color = status (PASS=green, BUILD_FAIL=orange, RUN_FAIL=pink, EXTRACTION_FAIL=vermilion)
# - Cell text = status abbreviation ("P", "BF", "RF", "EF")
# - X-axis: model short names ("GPT-4.1", "Claude 4.6", "Gemini Flash-Lite", "Llama 3.3")
# - Y-axis: kernel names (sorted by number of PASS across models, descending)
# - Title: "CUDA→OpenMP Translation Results (L0, Kernel-Centric)"
# - Size: (8, 10) inches for PDF
# - Save as: docs/paper/figures/f2_kernel_model_heatmap.pdf + .png

# F3: Failure Taxonomy Stacked Bar
# - X-axis: 4 models (same short names as F2)
# - Y-axis: count (not percentage — raw numbers)
# - Stacked bars: PASS (bottom), then BUILD_FAIL, RUN_FAIL, EXTRACTION_FAIL, VERIFY_FAIL (top)
# - Use hatching for B&W printability: PASS=solid, BUILD_FAIL=///, RUN_FAIL=\\\\, etc.
# - Annotate bar segments with counts if segment > 0
# - Title: "Failure Taxonomy by Model (cuda→omp, L0, n=17 kernels each)"
# - Size: (8, 6) inches
# - Save as: docs/paper/figures/f3_failure_taxonomy.pdf + .png

# F4: Augmentation Robustness (TBD placeholder)
# - If S7 results exist: show L0/L1/L2 pass rates per model (grouped bar or line chart)
# - If S7 results are ABSENT (which they are now): create a placeholder figure with
#   "Figure 4: Augmentation Robustness (data pending Session S7)" text on white background
# - Script should check: if results/evaluation/{model}/augmented_L1/ exists → use real data
#   else → generate placeholder
# - Save as: docs/paper/figures/f4_augmentation_robustness.pdf + .png

# F5: Cross-Direction Comparison (TBD placeholder)
# - If S9/S10 results exist: grouped bar of pass rates per direction per model
# - If absent: placeholder figure with "Figure 5: Cross-Direction Results (pending S9/S10)"
# - Save as: docs/paper/figures/f5_cross_direction.pdf + .png

# F6: XSBench Multi-API Results (TBD placeholder)
# - If S8 results exist: heat map of XSBench kernel × direction for 4 models
# - If absent: placeholder
# - Save as: docs/paper/figures/f6_xsbench.pdf + .png

# Step 4: Also generate T2 (Model Comparison Table) as a LaTeX table string
# T2 should be a 4-row × 6-column table:
# | Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL |
# This table string should be written to docs/paper/figures/t2_model_comparison.tex
# for direct inclusion in the LaTeX paper via \input{}

# Step 5: Run the script
python3 scripts/evaluation/generate_paper_figures.py \
  --project-root "$PROJECT_ROOT" \
  --output-dir docs/paper/figures \
  --format pdf,png
# Expected output: 5 figure PDFs + 5 PNGs + t2_model_comparison.tex in docs/paper/figures/

# Step 6: Verify output
ls -la docs/paper/figures/
# Expected: f2_kernel_model_heatmap.pdf, f2_kernel_model_heatmap.png,
#           f3_failure_taxonomy.pdf, f3_failure_taxonomy.png,
#           f4_augmentation_robustness.pdf (placeholder), ...
#           t2_model_comparison.tex

# Open the PDFs to visually verify (if display available):
# xdg-open docs/paper/figures/f2_kernel_model_heatmap.pdf  (on Linux with display)
# Or just verify file sizes are non-zero:
for f in docs/paper/figures/*.pdf; do echo "$f: $(stat -c%s "$f") bytes"; done
# All files should be > 1000 bytes (a blank PDF is ~600 bytes — any figure should be larger)

# Step 7: Validate the script against the hardcoded ground truth
# The eval_summary.md shows these exact numbers — verify the script produces them:
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    d = json.load(f)
# claude-sonnet-4-6: 12/17 PASS
claude = d['by_model']['claude-sonnet-4-6']
assert claude['pass'] == 12, f'Expected 12 PASS, got {claude[\"pass\"]}'
assert claude['total'] == 17, f'Expected total=17, got {claude[\"total\"]}'
# azure: 9/17
azure = d['by_model']['azure-gpt-4.1']
assert azure['pass'] == 9
# BUILD_FAIL aggregate: 26
assert d['by_status']['BUILD_FAIL'] == 26
print('Ground truth verification: PASS')
"

# Step 8: Git commit
git add scripts/evaluation/generate_paper_figures.py
git add docs/paper/figures/
git commit -m "W-S14: Add publication figure generation script (F2-F6) + initial figures from L0 data

- scripts/evaluation/generate_paper_figures.py: generates F2-F6 + T2 LaTeX table
- docs/paper/figures/: 5 PDF + 5 PNG figures + LaTeX table
- F2: Kernel x Model heatmap (17x4, cuda-to-omp L0)
- F3: Failure taxonomy stacked bar (per-model breakdown)
- F4/F5/F6: placeholders pending S7/S9-S10/S8 eval data
- Okabe-Ito colorblind-safe palette, hatching for B&W printability"
```

---

## SESSION W-S11 — Dashboard Data Refresh (WORKTREE-SAFE)

> **Status: DONE (2026-03-25). Completed in parallel with S7.**
> 12 files modified (282 insertions, 232 deletions). All stale numbers fixed against
> verified ground truth (6 verification agents confirmed accuracy, 10/10 heatmap spot-checks PASS).
> Post-review found and fixed 2 additional bugs: KPI denominator mismatch (byDirection included
> XSBench), Phase 1/2 model tables in architecture.html and pipeline.html.
> Validation: Wave 1 PASS (verify-app, diff-reviewer, security-scanner).
> **W-S14 figure regen is now unblocked** (depends on W-S11 + S7 completing).

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Find the project root: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY — that is expected. You don't need it.

## CURRENT STATE (verified 2026-03-25)
- Total eval result files: 248 (68 Rodinia L0 cuda-to-omp + 180 XSBench L0-L4)
- 4 active models: azure-gpt-4.1 (17 Rodinia L0), claude-sonnet-4-6 (77),
  gemini-2.5-flash-lite (77), groq-llama-3.3-70b-versatile (77)
- XSBench: 4 specs (cuda, omp, opencl, omp_target), all PASS, 12 directions run
- Rodinia: 60 specs, 54 PASS, 6 KNOWN_FAIL
- Augmentation: 54/60 PASS at ALL levels L1-L4 (level-invariant, verified)
- S7 (Rodinia L1-L4) is running in parallel — this session uses existing L0+XSBench data

Key files to modify (all present in worktree):
- visualizations/eval_results_data.js    ← eval data for llm_evaluation.html
- visualizations/results_data.js         ← augmentation data for results.html
- visualizations/build_results_data.js   ← build baseline data
- visualizations/overview.html           ← has hardcoded "65 specs", wrong augmentation rates
- visualizations/augmentation_deep_dive.html ← has hardcoded L3=29/60, L4=1/60 (wrong)
- visualizations/results.html            ← has stale BASELINE object
- visualizations/llm_evaluation.html     ← has stale eval results (pre-248-file state)
- visualizations/benchmark_landscape.html ← needs XSBench added

Key data sources (present in worktree as tracked files):
- results/evaluation/eval_summary.json   ← 248 result files (L0 Rodinia + L0-L4 XSBench)
- results/augmentation/retest_post_session2.md ← 54/60 PASS level-invariant (ground truth)

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] XSBench should appear in the dashboard (4 specs: cuda, omp, opencl, omp_target)
- [x] Rodinia spec count is 60 (NOT 65 — 5 phantom specs were deleted 2026-03-20)
- [x] Augmentation result: 54/60 PASS at ALL levels L0-L4 (level-invariant)
- [x] Split into 2 passes is unnecessary — do it all in one session

DECISIONS FOR AGENT TO RESOLVE BY READING FILES:
- Read visualizations/DESIGN.md before touching any HTML — understand the design constraints
- Check scripts/generate_viz_data.py to understand what data it reads and writes
- Verify that scripts/evaluation/analyze_eval.py has a --write-dashboard flag:
  python3 scripts/evaluation/analyze_eval.py --help | grep dashboard
  If not present, write the eval_results_data.js manually from eval_summary.json

# Session Goal
Fix ALL stale data in the ParBench visualization dashboard. After this session,
every number in every HTML page must match the authoritative data sources.

# Step 1: Setup
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Step 2: Understand what scripts exist
python3 scripts/generate_viz_data.py --help 2>/dev/null || echo "No --help flag, reading source"
head -30 scripts/generate_viz_data.py

python3 scripts/evaluation/analyze_eval.py --help 2>&1 | head -40

# Step 3: Regenerate JS data files via scripts
python3 scripts/generate_viz_data.py \
  --project-root "$PROJECT_ROOT" \
  -v 2>&1 | tail -20
# Verify output: results_data.js and build_results_data.js should be updated

python3 scripts/evaluation/analyze_eval.py \
  --project-root "$PROJECT_ROOT" \
  --output-dir results/evaluation \
  2>&1 | tail -20
# Verify: eval_summary.json + eval_results_data.js should be updated (if --write-dashboard exists)

# Step 4: Audit all stale hardcoded numbers in HTML files
# For each HTML file, search for known-stale values:

echo "=== overview.html audit ==="
grep -n "65\|spec.*count\|augment.*pass\|L3\|L4\|29/60\|1/60\|44/60" \
  visualizations/overview.html | head -30

echo "=== augmentation_deep_dive.html audit ==="
grep -n "29\|1/60\|L3\|L4\|65" visualizations/augmentation_deep_dive.html | head -30

echo "=== results.html audit ==="
grep -n "BASELINE\|65\|44/60\|L3\|L4" visualizations/results.html | head -30

echo "=== llm_evaluation.html audit ==="
grep -n "azure\|claude\|gemini\|llama\|PASS\|BUILD_FAIL\|percent" \
  visualizations/llm_evaluation.html | head -50

# Step 5: Fix overview.html
# Ground truth values to use:
# - Total Rodinia specs: 60 (was 65 before phantom deletion on 2026-03-20)
# - Total specs (all suites): 64 (60 Rodinia + 4 XSBench)
# - Augmentation PASS at each level: 54/60 = 90% (was showing wrong values for L3/L4)
# - LLM eval: 30/68 overall PASS (44.1%), best=claude 70.6%, worst=gemini 23.5%
# Read overview.html carefully — understand EVERY number before changing any

# Step 6: Fix augmentation_deep_dive.html
# L1 PASS: 54/60 (90%) — same for L2, L3, L4 (level-invariant)
# The chart data must show flat lines at 54/60 across all levels
# Read the Chart.js config carefully — understand which arrays need updating

# Step 7: Fix results.html
# BASELINE object should reflect: 54/60 PASS at L1-L4, 60 Rodinia specs
# Read the object definition carefully before editing

# Step 8: Fix llm_evaluation.html
# Update the per-model results table:
# | Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | EXTRACTION_FAIL |
# | azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 |
# | claude-sonnet-4-6 | 12 | 17 | 70.6% | 2 | 3 | 0 |
# | gemini-2.5-flash-lite | 4 | 17 | 23.5% | 10 | 2 | 1 |
# | groq-llama-3.3-70b-versatile | 5 | 17 | 29.4% | 10 | 1 | 1 |
# Also update the per-kernel heatmap if it is hardcoded (see eval_summary.md for full matrix)
# Source of truth: results/evaluation/eval_summary.json (always use this, never trust HTML)

# Step 9: Add XSBench to benchmark_landscape.html
# XSBench facts: 4 specs (cuda, omp, opencl, omp_target), 4/4 PASS
# XSBench is Monte Carlo Cross Section lookup — category: nuclear physics simulation
# Add it to whatever suite listing or table exists in benchmark_landscape.html

# Step 10: Write a verification script to catch any remaining stale numbers
# Create a TEMPORARY script at /tmp/verify_dashboard.py:
# 1. Load results/evaluation/eval_summary.json
# 2. Load visualizations/eval_results_data.js (parse the JS object)
# 3. Assert that key numbers match between them
# 4. Search visualizations/*.html for "65" referring to spec count — should find zero
# 5. Print PASS or list of mismatches
# Delete the script after verification

python3 /tmp/verify_dashboard.py
# Expected: PASS on all checks, zero "65" instances in HTML (except legitimate uses)
rm /tmp/verify_dashboard.py

# Step 11: Git commit
git add visualizations/
git commit -m "W-S11: Refresh dashboard data — fix stale spec counts and augmentation numbers

- overview.html: 65→60 Rodinia specs, 90% augmentation PASS (was wrong for L3/L4)
- augmentation_deep_dive.html: L1-L4 all show 54/60 PASS (level-invariant)
- results.html: BASELINE object updated to reflect 60 specs, 90% PASS
- llm_evaluation.html: 4-model matrix with claude=70.6%, azure=52.9%
- benchmark_landscape.html: XSBench added (4 specs, 4/4 PASS)
- eval_results_data.js + results_data.js: regenerated from current data"
```

---

## SESSION W-S12-PARTIAL — Paper Sections §3–§5 (WORKTREE-SAFE)

> **Status: NOT STARTED. Launch on Day 9 after S7 starts running.**
> **Worktree safe because:** Reads `specs/`, `harness/`, `c_augmentation/`, `scripts/`,
> `results/evaluation/`, and `docs/paper_outline.md`. Writes only to `docs/paper/`.
> No harness, no GPU, no Rodinia source needed.
> **WHY PARTIAL:** Sections 1-2 (Introduction + Related Work) require Samyak to have
> read the Paraval paper (M3) and formed the positioning argument. An agent can write
> Sections 3-5 autonomously — they are data-driven architectural descriptions.
> **Samyak will later add §1-§2 and §6-§8** (Sessions S12 and S13) in the main chat.
> **Paper impact:** §3 Framework, §4 Benchmark Curation, §5 Experimental Setup = ~4 pages.
> These sections fully describe existing code and data — zero subjective judgment needed.

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Find the project root: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY — that is expected. You don't need it for writing.
DO NOT run harness or eval pipeline commands.

Your task: Write §3 Framework, §4 Benchmark Curation, and §5 Experimental Setup
for the SC26 paper. These are the data-driven architectural sections that describe
what the system is and how the experiments were set up — NOT the results or arguments.

READ FIRST (mandatory before writing a single word):
1. docs/paper_outline.md                      ← the roadmap (sections, page targets, figures)
2. results/evaluation/eval_summary.md         ← actual numbers to cite in methodology
3. results/augmentation/retest_post_session2.md ← 54/60 PASS level-invariant (cite in §5)
4. schema/spec_schema.json                    ← spec structure (cite field names in §3)
5. harness/__main__.py + harness/spec_loader.py ← harness pipeline for §3
6. c_augmentation/augmentation_engine.py      ← augmentation architecture for §3

Paper format: SC26 ACM sigconf double-column, target ~10 pages total.
§3: 2.0 pages | §4: 1.0 page | §5: 1.0 page
Academic tone: precise, passive voice where appropriate, present tense for system description.

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] Output file: docs/paper/paper_sections_3_4_5.md (Samyak merges into paper_draft.md later)
- [x] Write §3, §4, §5 only. Leave §1, §2 blank — Samyak writes those.
- [x] Leave §6, §7, §8 for S13. Do not write Results or Discussion.
- [x] Use paper-drafter agent (Opus) for the actual writing — invoke it for each section
- [x] Use \cite{placeholder} for all citations (LaTeX will resolve)
- [x] Use [FIGURE: description] and [TABLE: description] for visual placeholders
- [x] Gal's constraints: no reasoning models, L0-L4 augmentation, omit build times
- [x] All 4 models: azure-gpt-4.1, claude-sonnet-4-6, gemini-2.5-flash-lite, groq-llama-3.3-70b-versatile

## AGENT USAGE: paper-drafter (Opus)

Invoke the paper-drafter agent for each section:
  "Use the paper-drafter agent to write §3 Framework for the SC26 paper"

The paper-drafter agent MUST pre-read these files before writing §3:
  - docs/paper_outline.md (§3 structure: 3.1 Spec Model, 3.2 Harness Pipeline, 3.3 Augmentation, 3.4 Eval)
  - harness/__main__.py (the CLI entry point — shows what harness does)
  - harness/spec_loader.py (spec loading logic)
  - harness/builder.py (build phase)
  - harness/runner.py (run phase, including cpu_time measurement)
  - harness/verifier.py (verify phase — EXIT_CODE and stdout_pattern strategies)
  - c_augmentation/augmentation_engine.py (augmentation architecture)
  - schema/spec_schema.json (spec structure — cite the key fields: translation_targets, etc.)

For §4, the agent must pre-read:
  - specs/ — count specs by suite and API: ls specs/ | grep "rodinia" | wc -l
  - docs/paper_outline.md §4 structure (4.1 Suite Selection, 4.2 Curation Criteria, 4.3 Coverage)
  - known-issues.md (6 KNOWN_FAIL specs — cite them in curation)
  - analysis/reports/kernel_level_analysis.md (survey data — 35 repos, 472 kernel pairs)

For §5, the agent must pre-read:
  - results/evaluation/eval_summary.md (model identities, current pass rates)
  - docs/paper_outline.md §5 structure (5.1 Models, 5.2 Translation Directions, 5.3 Augmentation)
  - docs/design/kernel_centric_translation.md (kernel-centric methodology — §5.4)
  - CLAUDE.md (GPU: RTX 4070, CUDA 24.3, Linux 6.8)

## Paper Content Guidelines (non-negotiable)

§3 Framework — what to cover:
- 3.1 Spec Model: the JSON spec as a declarative contract (parallel_api, build commands,
  run arguments, verify strategies, translation_targets, augmentation_level). Cite real field
  names from schema/spec_schema.json. Show a condensed example spec (use rodinia-bfs-cuda).
- 3.2 Harness Pipeline: Build → Run → Verify three-stage pipeline. Build uses spec's commands.
  Run uses correctness_config arguments. Verify uses exit_code or stdout_pattern. Kernel-centric
  mode (M11): LLM produces only translation_targets files; infrastructure stays untouched.
- 3.3 Augmentation Engine: 6 AST transforms (list them from c_augmentation/). libclang-based
  AST traversal. 5 levels L0-L4 (L0=none, L1=weak, L2=moderate, L3=strong, L4=aggressive).
  LEVEL_FRACTIONS controls what fraction of candidates to apply at each level.
  Key property: semantics-preserving — must not change observable output.
- 3.4 Evaluation Pipeline: run_eval_batch.py → llm_evaluate.py → extract → build → verify.
  Iterative repair (--max-retries): on BUILD_FAIL, include error snippet in next attempt.
  Translation complexity classification (single_file, multi_to_single, etc.).

§4 Benchmark Curation — what to cover:
- 4.1 Suite Selection: Why Rodinia (gold standard in HPC benchmarks, 3 GPU APIs, well-studied).
  Why XSBench (nuclear cross-section lookup, all 4 target APIs in one repo).
  Why HeCBench (120 kernels, breadth coverage). [TBD until S-HeCBench complete]
- 4.2 Curation Criteria: Must have CUDA + at least one target API (OMP or OpenCL).
  Must build with harness out of the box. Exclude KNOWN_FAIL (texture<> removed in CUDA12, etc.)
- 4.3 Coverage: 60 Rodinia specs + 4 XSBench specs = 64 total production specs.
  6 translation directions (from Translation Direction Matrix). Include spec count table.
  [TABLE: Benchmark suite coverage — suite, kernels, APIs, directions, PASS specs]

§5 Experimental Setup — what to cover:
- 5.1 Models: 4 models chosen by research team (Gal, 2026-03-23). Name and version each:
  GPT-4.1 (azure-gpt-4.1, Azure OpenAI API), Claude Sonnet 4.6 (claude-sonnet-4-6, Anthropic API),
  Gemini 2.5 Flash-Lite (gemini-2.5-flash-lite, Google AI API),
  Llama 3.3 70B (groq-llama-3.3-70b-versatile, Groq API).
  Temperature=0 for all models (deterministic). No reasoning models (Gal constraint).
- 5.2 Translation Directions: 6 directions (cuda-to-omp primary, omp-to-cuda, cuda-to-opencl,
  opencl-to-cuda, opencl-to-omp, omp-to-opencl). All L0 baseline. L1/L2 augmentation for primary.
- 5.3 Augmentation Protocol: L0 baseline (no augmentation), L1-L2 for primary direction.
  Single seed (seed=42) for reproducibility. Results pending (TBD until S7 complete).
- 5.4 Kernel-Centric Translation: The LLM produces only the parallel kernel files (translation_targets).
  The build system, headers, and host code remain unchanged. This isolates translation quality
  from build system generation — motivated by ParEval-Repo's finding that full project generation
  fails completely for apps > 133 SLoC \cite{parevalrepo2025}.
- 5.5 Hardware: NVIDIA GeForce RTX 4070, nvcc 24.3 (NVIDIA HPC SDK), gcc-11, Linux 6.8.
  [TABLE: Hardware and software configuration]

# Steps

# Step 1: Setup
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Step 2: Read paper_outline.md §3, §4, §5 content specifications
# MANDATORY: Do not write a single word until you have read the paper_outline.md sections
# for §3, §4, §5 in full. They contain figure/table placeholders with exact data requirements.

# Step 3: Collect key data to cite in the sections
echo "=== Spec counts ==="
ls specs/ | grep "^rodinia" | wc -l    # should be 60
ls specs/ | grep "^xsbench" | wc -l   # should be 4

echo "=== Augmentation transform names ==="
ls c_augmentation/ | grep -v "__\|test\|\.pyc" | grep "\.py$"
# This gives you the names of the 6 AST transform classes

echo "=== 6 KNOWN_FAIL specs ==="
grep -A 2 "KNOWN_FAIL" .claude/rules/known-issues.md | head -30

echo "=== Hardware info (from CLAUDE.md) ==="
grep -A 10 "GPU machine" CLAUDE.md | head -15

# Step 4: Invoke paper-drafter agent for each section
# For §3: "Use the paper-drafter agent to write §3 Framework"
# For §4: "Use the paper-drafter agent to write §4 Benchmark Curation"
# For §5: "Use the paper-drafter agent to write §5 Experimental Setup"
# Each invocation should be SEPARATE — let each section complete before starting the next
# Review each section after the agent finishes — fix any factual errors

# Step 5: Validate all claims against source code and data files
# Every number or claim in §3-§5 must be verifiable. Run these checks:

# Check augmentation transform count:
python3 -c "
from c_augmentation.augmentation_engine import AugmentationEngine
e = AugmentationEngine()
print('Transforms:', [t.__class__.__name__ for t in e.transforms])
print('Count:', len(e.transforms))
"
# Use this count in §3.3

# Check level fractions:
python3 -c "
from c_augmentation.augmentation_engine import LEVEL_FRACTIONS
print('Level fractions:', LEVEL_FRACTIONS)
"
# Cite these in §3.3

# Check verify strategies available:
grep -n "class.*Strategy\|EXIT_CODE\|STDOUT_PATTERN" harness/verifier.py | head -10
# Cite these in §3.2

# Step 6: Create output file
mkdir -p docs/paper
# Write the sections to docs/paper/paper_sections_3_4_5.md
# Format: Standard Markdown that can be embedded in paper_draft.md later
# Start with: ## §3 The ParBench Framework
#              ## §4 Benchmark Curation
#              ## §5 Experimental Setup

# Step 7: Verify output quality
wc -w docs/paper/paper_sections_3_4_5.md
# Expected: 1500-2500 words (~4 pages of double-column text)
# If under 1000 words: sections are too thin — expand with more technical detail
# If over 3000 words: sections are too long — trim to page targets

# Step 8: Check for any fabricated data (CRITICAL)
# Read the output file. For every number cited, trace it back to a data file.
# Any number without a traceable source must be removed or marked [TBD].
# Specifically check:
# - Spec counts: verify against ls specs/
# - Augmentation PASS rates: verify against results/augmentation/retest_post_session2.md
# - Model pass rates: verify against results/evaluation/eval_summary.md
# - Hardware specs: verify against CLAUDE.md

# Step 9: Git commit
git add docs/paper/
git commit -m "W-S12-PARTIAL: Write SC26 paper §3-§5 (framework, curation, methodology)

- docs/paper/paper_sections_3_4_5.md: ~N words, ~4 double-column pages
- §3 Framework: Spec model, harness pipeline, augmentation engine, eval pipeline
- §4 Benchmark Curation: Rodinia (60 specs), XSBench (4 specs), curation criteria
- §5 Experimental Setup: 4 models, 6 directions, L0-L2, kernel-centric methodology
- §1-§2 and §6-§8 are written by Samyak (require research judgment)
- Data citations verified against eval_summary.json and retest results"
```

---

## SESSION W-S17 — LaTeX Transfer (WORKTREE-SAFE)

> **Status: NOT STARTED. Run AFTER S15 (Paper Review & Polish) is complete.**
> **Worktree safe because:** Reads `docs/paper/paper_draft.md` and generates new LaTeX files.
> Does not touch eval results, specs, or harness. No GPU, no benchmark source needed.
> **Dependencies:** S12 + S13 + S15 must be complete. `docs/paper/paper_draft.md` must exist.
> **Paper impact:** LaTeX is the submission format. SC26 uses ACM sigconf double-column.

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Find the project root: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY — that is expected. You don't need it.

This session converts docs/paper/paper_draft.md (the Markdown paper draft) into
LaTeX source files following the ACM sigconf template for SC26 submission.

## BEFORE YOU START — Prerequisites

CHECK FIRST: does docs/paper/paper_draft.md exist?
ls docs/paper/paper_draft.md
# If it does NOT exist: this session cannot proceed. S12 + S13 + S15 must complete first.

CHECK: does docs/paper/figures/ contain the figure PDFs?
ls docs/paper/figures/*.pdf
# If figures are absent: W-S14 has not completed. Run W-S14 first.

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] SC26 uses ACM sigconf template (same as SC25) — standard for the Technical Papers track
- [x] LaTeX compilation: use pdflatex (not xelatex or lualatex) for maximum compatibility
- [x] Compile locally if texlive is installed, else produce .tex files for Overleaf upload
- [x] Bibliography: create docs/paper/references.bib from \cite{placeholder} tags in draft
- [x] Output directory: docs/paper/latex/ (new directory — all .tex, .bib, .pdf output here)
- [x] AI disclosure: add a footnote in acknowledgments if SC26 requires it (check CFP)

# Step 1: Setup
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)

# Check if LaTeX is installed
pdflatex --version 2>/dev/null && echo "LaTeX available" || echo "LaTeX NOT installed"
latexmk --version 2>/dev/null && echo "latexmk available" || echo "latexmk NOT installed"

# If LaTeX is not installed, install it:
# sudo apt install texlive-full texlive-fonts-recommended texlive-fonts-extra -y
# (This is ~5GB and takes 10-20 minutes. Only run if Samyak approves the install.)
# Alternative: skip compilation — produce .tex files only and upload to Overleaf.

# Step 2: Download the ACM sigconf template
mkdir -p docs/paper/latex
cd docs/paper/latex

# Download official ACM 2023 template
wget -q "https://www.acm.org/binaries/content/assets/publications/consolidated-tex-template/acmart-primary.zip" \
  -O acmart-primary.zip 2>/dev/null
# If wget fails (no internet): use a local copy or proceed without the template class
# Verify download:
ls -la acmart-primary.zip 2>/dev/null || echo "Template download failed — proceeding without it"
unzip -q acmart-primary.zip 2>/dev/null || true

# Step 3: Create the main LaTeX file
# docs/paper/latex/parbench-sc26.tex
# Structure:
# \documentclass[sigconf,anonymous]{acmart}  ← 'anonymous' for blind review
# \acmConference[SC'26]{...}
# \begin{document}
# \title{ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation}
# \begin{abstract} ... \end{abstract}
# \maketitle
# \input{section1_intro}
# \input{section2_related}
# \input{section3_framework}
# \input{section4_curation}
# \input{section5_methodology}
# \input{section6_results}
# \input{section7_discussion}
# \input{section8_conclusion}
# \bibliographystyle{ACM-Reference-Format}
# \bibliography{references}
# \end{document}

# Step 4: Convert each Markdown section to a LaTeX input file
# For each section in docs/paper/paper_draft.md:
# - Extract the section content
# - Convert Markdown headers (##, ###) to LaTeX (\section, \subsection)
# - Convert backtick code blocks to \begin{lstlisting}...\end{lstlisting}
# - Convert **bold** to \textbf{}, *italic* to \textit{}
# - Convert [TABLE: description] placeholders to \begin{table}...[content TBD]\end{table}
# - Convert [FIGURE: description] placeholders to \begin{figure}...\includegraphics\end{figure}
# - Convert \cite{placeholder} → keep as-is (will resolve in references.bib)
# - Convert | table | markdown | to LaTeX tabular environment

# Output files:
# docs/paper/latex/section1_intro.tex
# docs/paper/latex/section2_related.tex
# docs/paper/latex/section3_framework.tex
# docs/paper/latex/section4_curation.tex
# docs/paper/latex/section5_methodology.tex
# docs/paper/latex/section6_results.tex
# docs/paper/latex/section7_discussion.tex
# docs/paper/latex/section8_conclusion.tex

# Step 5: Create references.bib
# Extract all \cite{placeholder} tags from the Markdown draft:
grep -o '\\cite{[^}]*}' docs/paper/paper_draft.md | sort -u
# For each citation, create a BibTeX entry in docs/paper/latex/references.bib
# Use real publication data where known:
# - ParEval: HPDC 2024 (Nichols et al.) — arxiv:2401.08232
# - Rodinia: Che et al., IISWC 2009
# - HumanEval: Chen et al., Codex paper, arXiv:2107.03374
# - SWE-bench: Jimenez et al., ICLR 2024
# For unknowns: create minimal BibTeX stubs with TODO comments

# Step 6: Insert figures
# In section6_results.tex, replace [FIGURE: F2 Kernel x Model heatmap] with:
# \begin{figure}[t]
#   \centering
#   \includegraphics[width=\columnwidth]{figures/f2_kernel_model_heatmap}
#   \caption{CUDA→OpenMP translation results for 17 Rodinia kernels across 4 LLMs at L0...}
#   \label{fig:heatmap}
# \end{figure}
# Do this for all F2-F6 figures that exist in docs/paper/figures/

# Copy figures to the latex directory:
cp docs/paper/figures/*.pdf docs/paper/latex/figures/ 2>/dev/null || mkdir -p docs/paper/latex/figures && cp docs/paper/figures/*.pdf docs/paper/latex/figures/

# Step 7: Compile the LaTeX
cd docs/paper/latex
if command -v pdflatex &> /dev/null; then
  pdflatex -interaction=nonstopmode parbench-sc26.tex
  bibtex parbench-sc26 || true
  pdflatex -interaction=nonstopmode parbench-sc26.tex
  pdflatex -interaction=nonstopmode parbench-sc26.tex
  # Check for errors:
  grep -i "error\|undefined" parbench-sc26.log | head -20
  # Check page count:
  pdfinfo parbench-sc26.pdf 2>/dev/null | grep Pages
  # Target: 10 pages (SC26 limit)
else
  echo "LaTeX not installed — .tex files are ready for Overleaf upload"
fi

# Step 8: Git commit
cd $(git rev-parse --show-toplevel)
git add docs/paper/latex/
git commit -m "W-S17: Add LaTeX source for SC26 paper submission

- docs/paper/latex/parbench-sc26.tex: main document (ACM sigconf, anonymous mode)
- docs/paper/latex/section*.tex: 8 sections from paper_draft.md
- docs/paper/latex/references.bib: BibTeX entries for all citations
- docs/paper/latex/figures/: figure PDFs from W-S14
$(if command -v pdflatex &> /dev/null; then echo "- parbench-sc26.pdf: compiled PDF (check page count)"; fi)"
```

---

## SESSION W-S15 — Paper Review & Polish (WORKTREE-SAFE)

> **Status: NOT STARTED. Run AFTER S13 (Paper §6-§8) is complete and Gal has reviewed.**
> **Worktree safe because:** Reads and edits `docs/paper/paper_draft.md` only. No eval
> pipeline, no harness, no Rodinia source. The self-critic and paper-drafter agents run
> inside this session and do their own file reading.
> **Timing:** Launch this when S13 is done AND Gal has given feedback. Gal's feedback
> may require structural changes — it must be incorporated BEFORE polishing, not after.
> **Paper impact:** This is the final quality gate before LaTeX. Every number, every claim,
> every figure reference must be verified here. The self-critic agent will catch rationalization.

```
ultrathink

## CONTEXT

You are running in a git worktree of the ParBench SC26 project.
Find the project root: cd $(git rev-parse --show-toplevel)
The Rodinia submodule is EMPTY — that is expected. You don't need it.

This session performs adversarial review of the complete SC26 paper draft.
Your goal: leave docs/paper/paper_draft.md in submission-ready state.

## BEFORE YOU START — Prerequisites

CHECK FIRST:
ls docs/paper/paper_draft.md   ← must exist (S12 + S13 complete)
ls docs/paper/figures/*.pdf    ← should have F2-F6 (W-S14 complete)

wc -w docs/paper/paper_draft.md
# Expected: 8000-11000 words (~10 double-column pages)
# If under 5000 words: paper is incomplete — S13 may not be done. STOP and alert Samyak.

## BEFORE YOU START — Decisions Already Made

RESOLVED:
- [x] Self-critic agent (Opus): use for adversarial review of claims and rationalization
- [x] paper-drafter agent (Opus): use for data accuracy cross-check
- [x] Fix issues directly (not just flag them) — the paper must be clean after this session
- [x] AI assistance disclosure: add "Portions of this paper were drafted with AI assistance"
      in Acknowledgments IF SC26 requires disclosure (check the CFP)

# Session Goal
Produce a submission-ready, fully polished paper draft with:
- All numbers verified against eval_summary.json
- All figure/table references consistent with paper_outline.md inventory
- All claims backed by data or marked [TBD] with a session reference
- No rationalization patterns (per self-critic agent definition)
- Word count within SC26 limits

# Step 1: Setup
source env_parbench/bin/activate
cd $(git rev-parse --show-toplevel)

# Step 2: Read the paper end-to-end before invoking any agent
# You must have a clear picture of the paper before running automated review.
# Key things to look for on your first read:
# a) Every number — write down each claim with its data source expectation
# b) Every [FIGURE:] and [TABLE:] placeholder — note which are filled, which are missing
# c) Every \cite{placeholder} — note which seem to have real citations, which are vague
# d) Structural issues — does the argument flow logically from §1 to §8?
# e) Consistency — does the Abstract match the actual results in §6?

# Step 3: Verify all numbers against ground truth
# Load ground truth:
python3 -c "
import json
with open('results/evaluation/eval_summary.json') as f:
    d = json.load(f)

print('=== GROUND TRUTH (use this to cross-check paper) ===')
print('Total tasks:', d['total_tasks'])
for model, stats in d['by_model'].items():
    short = model.replace('groq-llama-3.3-70b-versatile', 'llama').replace('gemini-2.5-flash-lite', 'gemini').replace('azure-gpt-4.1', 'azure').replace('claude-sonnet-4-6', 'claude')
    print(f'{short}: {stats[\"pass\"]}/{stats[\"total\"]} PASS ({stats[\"pass\"]/stats[\"total\"]*100:.1f}%)')
print()
print('Failure taxonomy:')
for status, count in d.get('by_status', {}).items():
    print(f'  {status}: {count}')
print()
print('Translation complexity:')
for cls, stats in d.get('by_complexity', {}).items():
    print(f'  {cls}: {stats[\"pass\"]}/{stats[\"total\"]} ({stats[\"rate\"]*100:.1f}%)')
"
# Ground truth output (paste into review document):
# Total tasks: 68
# claude: 12/17 PASS (70.6%)
# azure: 9/17 PASS (52.9%)
# llama: 5/17 PASS (29.4%)
# gemini: 4/17 PASS (23.5%)
# BUILD_FAIL: 26, RUN_FAIL: 10, EXTRACTION_FAIL: 2, VERIFY_FAIL: 0
# single_file: 7/12 (58.3%), multi_to_single: 21/44 (47.7%), multi_to_multi: 2/12 (16.7%)

# Also check augmentation ground truth:
cat results/augmentation/retest_post_session2.md | head -30
# Expected: 54/60 PASS at all levels L0-L4 (level-invariant)

# Step 4: Invoke paper-drafter agent for data accuracy review
# "Use the paper-drafter agent to review docs/paper/paper_draft.md for data accuracy.
#  Cross-check every numeric claim against results/evaluation/eval_summary.json
#  and results/augmentation/retest_post_session2.md.
#  List all discrepancies as: CLAIM: [paper text] | ACTUAL: [ground truth] | FIX: [corrected text]"

# Step 5: Invoke self-critic agent for adversarial review
# "Use the self-critic agent to review docs/paper/paper_draft.md.
#  Apply obra/superpowers verification-before-completion principle.
#  Apply Trail of Bits anti-rationalization patterns.
#  Look for: (1) claims without evidence, (2) cherry-picked results,
#  (3) limitations understated, (4) incomplete sections masked as complete,
#  (5) future work described as current contribution.
#  Return a structured PASS/FAIL verdict with specific line citations."

# Step 6: Verify Gal's constraint checklist (from docs/paper_outline.md)
# The paper_outline.md contains a 13-item Gal constraint checklist.
# Read it and verify each item is satisfied in the draft.
# Common constraints from meeting notes:
# - No reasoning models mentioned (o1, o3, Gemini Thinking — excluded from study)
# - Build times must NOT be reported as a performance metric (Gal: "omit build times")
# - Temperature=0 for all models (must be stated in §5)
# - Augmentation levels reported: L0, L1, L2 (L3, L4 not in paper unless level-invariance argument)

# Step 7: Fix all identified issues
# For each issue from Steps 4-6:
# a) Locate the exact text in paper_draft.md
# b) Fix it directly (edit the file)
# c) Document the fix: "FIXED: [description]"
# Do not just mark issues as TODO — this session's goal is a clean draft

# Step 8: Verify figure/table cross-references
# From docs/paper_outline.md Figure & Table Inventory:
grep -n "FIGURE\|TABLE\|\[F[1-9]\]\|\[T[1-9]\]" docs/paper/paper_draft.md | head -40
# Every F1-F6 placeholder should appear in the draft
# Every T1-T9 placeholder should appear in the draft
# F1 (architecture diagram): may be [FIGURE: F1 — create manually in draw.io]
# F4/F5/F6: may be [FIGURE: F4 — TBD until Session S7 complete] — that's OK

# Step 9: Check word count and page estimate
wc -w docs/paper/paper_draft.md
# 8000 words ≈ 10 double-column pages (rough estimate)
# If significantly over: identify which sections are too long and trim
# Key length targets (from paper_outline.md):
# §1 Introduction: 1.5p | §2 Related Work: 1.0p | §3 Framework: 2.0p
# §4 Benchmark Curation: 1.0p | §5 Experimental Setup: 1.0p
# §6 Results: 2.0p | §7 Discussion: 0.75p | §8 Conclusion: 0.5p | Abstract: 0.25p

# Step 10: Final check — related work positioning
# The paper must clearly differentiate from:
# - HumanEval/SWE-bench: sequential code synthesis, no parallelism
# - ParEval (HPDC 2024): function-level, not API-translation; no augmentation
# - ParEval-Repo: finds 0% pass@1 for repo-level translation; ParBench uses kernel-centric
# - TransCoder: statistical, not LLM; C++/Java not GPU APIs
# - BabelTower: GPU APIs but different evaluation model
# If any of these differentiators are missing or unclear: fix them.

# Step 11: Git commit
git add docs/paper/paper_draft.md
git commit -m "W-S15: Paper review and polish — all claims verified, Gal constraints satisfied

- All numeric claims cross-checked against eval_summary.json (68 tasks, 4 models)
- Augmentation claims verified against retest_post_session2.md (54/60, level-invariant)
- Self-critic agent review: [PASS/FAIL with N issues found and fixed]
- Paper-drafter data accuracy review: N discrepancies found and corrected
- Gal constraint checklist: all 13 items verified
- Related work positioning: ParBench vs ParEval/ParEval-Repo/TransCoder differentiated
- Word count: ~N words (~N pages estimate)
- F1-F6 figure placeholders: N filled, N marked TBD (pending eval sessions)"

