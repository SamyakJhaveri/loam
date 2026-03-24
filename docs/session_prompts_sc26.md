# ParBench SC26 Sprint — Session Prompts

> **How to use:** Copy-paste one prompt per Claude Code session. Run `/clear` between sessions.
> Each prompt is self-contained with full context, exact commands, and verification steps.
> Today's date: 2026-03-23. Deadline: April 8, 2026. Day 6 of 21-day sprint.
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
| S7 | `eval-batcher` (background) | Steps 2-3 — L1/L2 augmented eval for all 4 models |
| S9 | `eval-batcher` (background) | Step 2 — omp-to-cuda for 16 eligible kernels × 4 models |
| S10 | `eval-batcher` (background) | Step 1-5 — cuda-to-opencl for 17 kernels × 4 models |
| S10b | `eval-batcher` (background) | Steps 1-3 — opencl-to-cuda, opencl-to-omp, omp-to-opencl × 4 models |
| S11 | `dashboard-refresher` | Steps 2-4 — regenerate JS data + fix stale HTML numbers |
| S12-S15 | `paper-drafter` | Paper section writing with actual data from results files |
| Any | `plan-reviewer` | Before any architecture change — adversarial pre-implementation review |
| Any | `verify-app` | Before any commit — validates project health |

**eval-batcher runs in the background** (`background: true`). Start it, then continue other work in the main session. You'll be notified when it completes.

---

---

## SPRINT-WIDE PREREQUISITES

Before starting any session, resolve these cross-cutting blockers. Each entry shows which sessions are affected.

### CRITICAL — Blocks 5+ sessions

1. **Model selection** ✅ RESOLVED (Gal, 2026-03-23) — 4 models selected for all eval sessions:
   - `azure-gpt-4.1` — Azure OpenAI (Sessions 2 complete; 9/17 PASS)
   - `claude-sonnet-4-6` — Anthropic API (was removed March 18; **re-added by Gal 2026-03-23**; uses existing `claude-*` provider routing; add to MODEL_REGISTRY in `scripts/evaluation/llm_evaluate.py`)
   - `gemini-2.5-flash-lite` — Google AI API (**see prerequisite #1b — provider code needed first**)
   - `groq-llama-3.3-70b-versatile` — Groq API (Session 3 complete; 5/17 PASS)
   - **S3b needed**: cuda-to-omp L0 for claude-sonnet-4-6 and gemini-2.5-flash-lite (groq + azure already done)

1b. **Gemini 2.5 Flash-Lite provider implementation** — Blocks S3b, S7, S8, S9, S10, S10b for Gemini
   - Status: NOT STARTED — `scripts/evaluation/llm_evaluate.py` has NO Google AI provider
   - `call_llm()` currently supports: `claude-*` (Anthropic), `gpt-*/o*-*` (OpenAI), `azure-*` (Azure), `groq-*` (Groq)
   - Needed: new `elif model.startswith("gemini-"):` branch (~50-80 lines using `google-generativeai` SDK or Google's OpenAI-compatible endpoint)
   - Also needed: `gemini-2.5-flash-lite` entry in `MODEL_REGISTRY` dict (line ~60)
   - API key env var: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
   - File to edit: `scripts/evaluation/llm_evaluate.py`
   - **This is a prerequisite blocker** — implement before running any Gemini evals

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

7. **M6 timing metrics** — Designed but not implemented; no session prompt exists
   - Decision: Correctness-only paper, or add wall-clock timing as proxy for speedup?

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
| 1 | `cuda-to-omp` | 17 | 60 | 1 | **78** | S2/S3/S7 | EVALUATED (L0, L1, L2) |
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

## SESSION 7 — Augmented Evaluation (L1/L2)

```
ultrathink

# Models (decided by Gal 2026-03-23):
# azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile

## BEFORE YOU START — What I Need From You

DECISIONS:
- [x] Models RESOLVED — all 4 models (see Prerequisite #1 above)
- [ ] L1 and L2 only (no L3/L4). Confirmed per Gal's "conservative augmentation"
      directive? (If yes, no action needed — just confirming)
- [ ] If augmentation CAUSES degradation (a kernel passes at L0 but fails at
      L1/L2), should the session stop to investigate, or record and continue?
      Recommendation: record and continue — the augmentation baseline already
      proves transforms are semantics-preserving.
- [ ] Seed=42 is used for all augmentation. Same seed = same augmented code
      every time. This is good for reproducibility but tests only ONE augmented
      variant per kernel. Acceptable limitation for the paper?

DATA/INFO:
- [ ] API keys for ALL 4 models must be set in the shell:
      AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT (azure-gpt-4.1)
      ANTHROPIC_API_KEY (claude-sonnet-4-6)
      GEMINI_API_KEY or GOOGLE_API_KEY (gemini-2.5-flash-lite)
      GROQ_API_KEY (groq-llama-3.3-70b-versatile)
- [ ] Budget: 136-272 API calls (17 kernels × 4 models × 2 levels × 1-2 retries).
      Estimated cost: $5-$30 across all providers. Confirm budget is available.

EXTERNAL DEPS:
- [ ] Sessions 2 + 3 complete (azure-gpt-4.1 and groq-llama L0 baselines)
- [ ] Session 3b complete (claude-sonnet-4-6 and gemini-2.5-flash-lite L0 baselines)
- [ ] Prerequisite #1b complete (Gemini provider in llm_evaluate.py)
- [ ] NOTE: use --resume so azure/groq L1/L2 can be added alongside new model L1/L2

# Session Goal
Re-run cuda-to-omp evaluation at augmentation levels L1 and L2 for all 4 models.
Tests whether LLM translation quality degrades when source code is augmented with
semantics-preserving transforms.

# Why This Matters
The augmentation contribution in the SC26 paper requires showing how LLMs perform under
code variation. If pass rates drop at L1/L2, augmentation reveals LLM fragility. If they
hold steady, it validates that LLMs understand semantics, not just syntax.

# IMPORTANT: Kernel-centric translation is the ONLY mode (Sessions 1.5 + 1.6 complete).
# Augmentation applies to the SOURCE kernel files only.
# The LLM sees augmented source → produces target kernel file(s).
# Target infrastructure stays untouched (not augmented, not modified).
# This is the correct layering: augmentation tests translation robustness at the
# source-code level; kernel-centric translation tests structural translation scope.

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Eligible cuda-to-omp kernels (17): backprop, bfs, bptree, cfd, heartwall, hotspot,
  hotspot3d, kmeans, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad,
  streamcluster
- L0 results already exist for azure-gpt-4.1 (Session 2) and groq-llama (Session 3)
- L0 results for claude-sonnet-4-6 and gemini-2.5-flash-lite must come from Session 3b first
- Result files for L1/L2 are tagged with -L1, -L2 suffix in path
- Augmentation uses seed=42 by default

# Prerequisites
- Sessions 2+3+3b complete (L0 baselines for all 4 models, kernel-centric v2)
- Prerequisite #1b complete (Gemini provider in llm_evaluate.py)
- API keys configured for all 4 models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run all 4 models at L1 and L2 (L0 already exists for all from Sessions 2+3+3b)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 1 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v

# Step 3: Regenerate analysis with all levels
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --expected-directions cuda-to-omp \
  --expected-levels 0 1 2

# Step 4: Verification — write a small test script that:
# 1. Counts result files per model per level (L0, L1, L2)
# 2. Compares pass rates across levels per model
# 3. Identifies any kernel that passes at L0 but fails at L1 or L2 (augmentation fragility)
# 4. Identifies any kernel that fails at L0 but passes at L1 or L2 (unlikely but interesting)
# 5. Prints a level comparison table (4 models × 3 levels)
# 6. Confirms all results have translation_mode="kernel_centric"
# DELETE the test script after verification.

# Step 5: Show me:
# - Pass rates: L0 vs L1 vs L2 for each of the 4 models
# - Any augmentation-induced failures (kernels that degrade under augmentation)
# - Summary table for the paper (expected: level-invariant similar to augmentation baseline)
# - "Pass Rate by Translation Complexity" table at L0/L1/L2

# Step 6: Git commit and push
# Commit: All new L1/L2 result files, updated eval_summary.*
# Message: "Add augmented eval results (L1/L2) for all 4 models (kernel-centric)"
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
- [ ] If OpenACC/OMP-target specs failed in Session 5, skip those directions?

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
#   - Total specs: should reflect 60 Rodinia + 5 XSBench = 65 total
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
#   - Claude Sonnet 4.6: TBD (pending Session 3b)
#   - Gemini 2.5 Flash-Lite: TBD (pending Session 3b + Gemini provider)
#   - 54/60 PASS at L1–L4 (level-invariant) — from augmentation results
#   - BUILD_FAIL dominates (~70% of failures) — from eval_summary.md
#   - 6 translation directions across 3 APIs — from Translation Direction Matrix
#   - Use "TBD (pending Session 3b)" for missing model data — never fabricate
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
      Minimum viable: Sessions 2+3 (2 models, 1 direction, L0).
      Recommended: Sessions 2+3+3b+7 at minimum (4 models, L0/L1/L2 for 1 direction)
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
