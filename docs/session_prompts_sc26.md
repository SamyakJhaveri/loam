# ParBench SC26 Sprint — Session Prompts

> **How to use:** Copy-paste one prompt per Claude Code session. Run `/clear` between sessions.
> Each prompt is self-contained with full context, exact commands, and verification steps.
> Today's date: 2026-03-21. Deadline: April 8, 2026. Day 4 of 21-day sprint.

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
| S2 | `eval-batcher` (background) | Step 3 — run all 17 azure-gpt-4.1 cuda-to-omp kernels (clean slate) |
| S3 | `eval-batcher` (background) | Step 3 — run 17 kernels for second model (awaiting model decision) |
| S4 | `xsbench-explorer` | Steps 2-4 — read XSBench Makefiles/source, extract spec data |
| S4 | `spec-auditor` | Step 8 — validate all 5 new XSBench spec files |
| S5 | `verify-app` | Post-build — schema validation + spec integrity check |
| S7 | `eval-batcher` (background) | Steps 2-3 — L1/L2 augmented eval for both models |
| S9 | `eval-batcher` (background) | Step 2 — omp-to-cuda for 16 eligible kernels × 2 models |
| S10 | `eval-batcher` (background) | Step 1-5 — cuda-to-opencl for 17 kernels × 2 models |
| S11 | `dashboard-refresher` | Steps 2-4 — regenerate JS data + fix stale HTML numbers |
| S12-S15 | `paper-drafter` | Paper section writing with actual data from results files |
| Any | `plan-reviewer` | Before any architecture change — adversarial pre-implementation review |
| Any | `verify-app` | Before any commit — validates project health |

**eval-batcher runs in the background** (`background: true`). Start it, then continue other work in the main session. You'll be notified when it completes.

---

---

## SESSION 1 — Rodinia Submodule Reset & Re-verification

```
ultrathink

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

```
ultrathink

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

## SESSION 2 — Complete azure-gpt-4.1 Rodinia cuda-to-omp Evaluation

```
ultrathink

# Session Goal
Run ALL 17 Rodinia cuda-to-omp translation tasks for azure-gpt-4.1 at L0 using the
kernel-centric pipeline. This is a CLEAN SLATE run — previous v1 results are deleted.

# Why This Matters
Session 1.5 implemented kernel-centric translation (M11 resolution). Previous 10-kernel
pilot results used the full-project paradigm and cannot be mixed with the new pipeline's
results in the paper. Clean slate ensures a single, coherent evaluation paradigm.
Expected improvement: 60% → 75-80% pass rate as structural failures are eliminated.

# IMPORTANT: Kernel-centric translation is now active (M11 resolution).
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
- Session 1.5 complete (kernel-centric pipeline implemented, all 60 specs populated)
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
# 4. Confirms translation_mode="kernel_centric" in all results
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

## SESSION 3 — Second Model Rodinia cuda-to-omp Evaluation

```
ultrathink

# Session Goal
Run ALL 17 Rodinia cuda-to-omp translation tasks for the second model at L0 using the
kernel-centric pipeline. Model TBD — awaiting M7/M8 decision (llama-70b or leaderboard pick).

# IMPORTANT MODEL NOTE:
# claude-sonnet-4-20250514 was REMOVED as an eval target (March 18 meeting decision).
# Historical claude-sonnet pilot data exists in results/evaluation/claude-sonnet-4-20250514/
# but will NOT be extended. This session is for the replacement model (llama-70b or TBD).
#
# When the model is decided (M7/M8 tasks), update the --models flag below.
# Session 3 cannot begin until M7 (Groq/Modal setup) or M8 (leaderboard model) is complete.

# IMPORTANT: Kernel-centric translation is active (Session 1.5 complete).
# The LLM produces only the kernel file(s), not full project structure.
# All 17 kernels run as CLEAN SLATE (no previous v2 results for the new model).

# Context
- Project root: /home/samyak/Desktop/parbench_sam
- Results dir: results/evaluation/{new-model}/
- Model ID: TBD — replace MODEL_ID below with actual model ID from M7/M8
- Eligible kernels (17): backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d,
  kmeans, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster
- EXCLUDED: mummergpu, hybridsort, gaussian, huffman, dwt2d
- API key env var: TBD (Groq API key or Modal credentials per M7 setup)

# Prerequisites
- Session 1 complete (Rodinia submodule reset)
- Session 1.5 complete (kernel-centric pipeline, all 60 specs populated)
- Session 2 complete (azure-gpt-4.1 v2 baseline established)
- M7 or M8 complete (second model available via API)

# Step 1: Activate venv and verify
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Verify model API key (replace with actual env var name from M7/M8 setup):
# python3 -c "import os; assert os.environ.get('GROQ_API_KEY'), 'GROQ_API_KEY not set'"

# Step 2: Run batch evaluation (replace MODEL_ID with actual model ID)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models MODEL_ID \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Step 3: Verify 17 result files exist
ls results/evaluation/MODEL_ID/rodinia-*-cuda-to-rodinia-*-omp.json | wc -l
# Expected: 17

# Step 4: Regenerate analysis with BOTH models (azure-gpt-4.1 + new model)
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 MODEL_ID \
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
# Commit: results/evaluation/MODEL_ID/*.json, eval_summary.*, batch_*
# Message: "Add MODEL_ID Rodinia cuda-to-omp eval v2 (17/17 kernels, kernel-centric)"
# Push to origin main.
```

---

## SESSION 4 — Clone XSBench & Generate Specs

```
ultrathink

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
# Commit: "Add XSBench as second benchmark suite (5 API variants: CUDA/OMP/OpenCL/OMP-target/OpenACC)"
# Push to origin main.
```

---

## SESSION 5 — Verify XSBench Toolchains & Smoke Test

```
ultrathink

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

```
ultrathink

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

# Session Goal
Re-run cuda-to-omp evaluation at augmentation levels L1 and L2 for both azure-gpt-4.1
and the second model (MODEL_ID from Session 3). Tests whether LLM translation quality
degrades when source code is augmented with semantics-preserving transforms.

# Why This Matters
The augmentation contribution in the SC26 paper requires showing how LLMs perform under
code variation. If pass rates drop at L1/L2, augmentation reveals LLM fragility. If they
hold steady, it validates that LLMs understand semantics, not just syntax.

# IMPORTANT: Kernel-centric translation is active (Session 1.5 complete).
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
- L0 results already exist from Sessions 2 + 3 (kernel-centric v2 pipeline)
- Result files for L1/L2 are tagged with -L1, -L2 suffix in path
- Augmentation uses seed=42 by default
- NOTE: Replace MODEL_ID with the actual second model ID from Session 3

# Prerequisites
- Sessions 2+3 complete (L0 baselines for both models, kernel-centric v2)
- API keys configured for both models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run azure-gpt-4.1 at L1 and L2 (L0 already exists from Session 2)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 1 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v

# Step 3: Run second model at L1 and L2 (L0 already exists from Session 3)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models MODEL_ID \
  --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
  --augment-levels 1 2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  --resume \
  -v

# Step 4: Regenerate analysis with all levels
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models azure-gpt-4.1 MODEL_ID \
  --expected-directions cuda-to-omp \
  --expected-levels 0 1 2

# Step 5: Verification — write a small test script that:
# 1. Counts result files per model per level (L0, L1, L2)
# 2. Compares pass rates across levels per model
# 3. Identifies any kernel that passes at L0 but fails at L1 or L2 (augmentation fragility)
# 4. Identifies any kernel that fails at L0 but passes at L1 or L2 (unlikely but interesting)
# 5. Prints a level comparison table
# 6. Confirms all results have translation_mode="kernel_centric"
# DELETE the test script after verification.

# Step 6: Show me:
# - Pass rates: L0 vs L1 vs L2 for each model
# - Any augmentation-induced failures (kernels that degrade under augmentation)
# - Summary table for the paper (expected: level-invariant similar to augmentation baseline)
# - "Pass Rate by Translation Complexity" table at L0/L1/L2

# Step 7: Git commit and push
# Commit: All new L1/L2 result files, updated eval_summary.*
# Message: "Add augmented eval results (L1/L2) for azure-gpt-4.1 and MODEL_ID (kernel-centric)"
# Push to origin main.
```

---

## SESSION 8 — XSBench LLM Evaluation (Multi-API)

```
ultrathink

# Session Goal
Run LLM translation evaluation on XSBench across all API pairs for the 3 primary
translation directions: cuda-to-omp, omp-to-cuda, cuda-to-opencl. If OpenACC and
OMP target variants are verified, also run cuda-to-openacc and cuda-to-omp_target.

# Why This Matters
XSBench provides expert-written implementations in 5 APIs — perfect for evaluating
LLM translation across diverse parallel programming models. This is the "multi-API
story" for the SC26 paper.

# Context
- XSBench specs: specs/xsbench-xsbench-{cuda,omp,opencl,omp_target,openacc}.json
- Only run directions where BOTH source and target specs verified PASS in Session 5
- Translation pairs to attempt:
  - cuda-to-omp (if both PASS)
  - omp-to-cuda (if both PASS)
  - cuda-to-opencl (if both PASS)
  - cuda-to-omp_target (if both PASS)
  - cuda-to-openacc (if both PASS)
  - And potentially others based on what passed

# Prerequisites
- Session 5 complete (XSBench variants smoke tested)
- API keys for both models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Determine which XSBench translation pairs are viable
# Read each XSBench spec's baseline_results to check which passed in Session 5
# Only run pairs where both source and target specs are verified PASS

# Step 3: Run evaluation for each viable direction
# For each direction, run both models:
#
# Example for cuda-to-omp:
python3 scripts/evaluation/run_eval_batch.py \
  --suite xsbench \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 MODEL_ID \
  --project-root /home/samyak/Desktop/parbench_sam \
  --max-retries 2 \
  -v

# Repeat for omp-to-cuda, cuda-to-opencl, and any stretch directions

# Step 4: For stretch directions (cuda-to-openacc, cuda-to-omp_target):
# These use the eval pipeline's standard flow — the LLM translates CUDA source to
# the target API, then the harness builds/runs/verifies using the target spec.
# If the target spec's build environment is correctly configured, it should work.

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
# Message: "XSBench multi-API eval: N directions × 2 models"
# Push to origin main.
```

---

## SESSION 9 — Second Direction: omp-to-cuda (Rodinia)

```
ultrathink

# Session Goal
Run omp-to-cuda evaluation for all eligible Rodinia kernels with both models at L0.

# Why This Matters
The paper targets 3 translation directions. omp-to-cuda is the reverse of the primary
direction — testing whether LLMs can add GPU parallelism (harder than removing it).

# IMPORTANT: Kernel-centric translation is active (Session 1.5 complete).
# For omp-to-cuda, the source is OMP (typically 1 kernel file in translation_targets),
# and the target is CUDA. The LLM must produce CUDA kernel file(s) from the OMP source.
# The CUDA target spec's translation_targets identifies which .cu/.cuh files to produce.
# This is typically 1-2 .cu files depending on the kernel.
#
# Key consideration: CUDA targets use translation_targets = prompt_payload in most cases
# (CUDA files are all kernel code). Exception: nn-cuda should exclude hurricane_gen.c.
# Verify the CUDA translation_targets are populated correctly in Session 1.5.

# Context
- Eligible omp-to-cuda kernels (16, excluding mummergpu-omp KNOWN_FAIL,
  and excluding kmeans because kmeans-cuda target has KNOWN_FAIL build):
  backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte,
  nn, nw, particlefilter, pathfinder, srad, streamcluster
- The batch runner uses manifest to find pairs: source=omp, target=cuda
- Phantom OMP specs (gaussian, huffman, hybridsort) will error — use --kernels to filter
- Replace MODEL_ID with the actual second model from Session 3

# Prerequisites
- Session 1 complete (submodule reset)
- Session 1.5 complete (kernel-centric pipeline, CUDA specs have translation_targets)
- API keys configured for both models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run both models
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction omp-to-cuda \
  --models azure-gpt-4.1 MODEL_ID \
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
  --expected-models azure-gpt-4.1 MODEL_ID \
  --expected-directions cuda-to-omp omp-to-cuda \
  --expected-levels 0

# Step 4: Verification — write a small test script that:
# 1. Counts omp-to-cuda results per model
# 2. Compares omp-to-cuda pass rates with cuda-to-omp (is reverse harder?)
# 3. Identifies kernels that pass in one direction but fail in the other
# 4. Shows "Pass Rate by Translation Complexity" for this direction
# DELETE the test script.

# Step 5: Show me direction comparison table and push.
# Commit: "Add omp-to-cuda eval results for Rodinia (16 kernels × 2 models, kernel-centric)"
```

---

## SESSION 10 — Third Direction: cuda-to-opencl (Rodinia)

```
ultrathink

# Session Goal
Run cuda-to-opencl evaluation for eligible Rodinia kernels with both models at L0.

# Why This Matters
Third translation direction for the paper. cuda-to-opencl tests cross-vendor API
translation (NVIDIA-specific CUDA → vendor-neutral OpenCL). This is the KEY multi-file
direction: the LLM must produce BOTH a .cl kernel file AND a host .cpp driver file.

# IMPORTANT: cuda-to-opencl targets are inherently multi-file (Erkap's point).
# All OpenCL targets have translation_targets = [".cl kernel", "host .cpp driver"].
# This is classified as single_to_multi or multi_to_multi in the complexity taxonomy.
# OpenCL inherently requires separate device/host code — cannot be normalized to 1 file.
#
# The LLM is being tested on a REAL structural translation challenge:
#   - Produce device code (.cl) in OpenCL C (a subset of C99 with vendor extensions)
#   - Produce host code (.cpp) using the OpenCL C++ API
#   - The two files must interface correctly via cl::Kernel, cl::Buffer, etc.
#
# Expected: lower pass rates than cuda-to-omp. This is scientifically interesting —
# report it in the paper as evidence that API structural complexity predicts LLM difficulty.
#
# Replace MODEL_ID with the actual second model from Session 3.

# Context
- Eligible cuda-to-opencl kernels (18): backprop, bfs, bptree, cfd, dwt2d, gaussian,
  heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter,
  pathfinder, srad, streamcluster
  (Note: dwt2d and gaussian have OpenCL specs but no OMP — eligible for this direction)
  (Note: nn-opencl is KNOWN_FAIL for original code, but LLM writes NEW code —
   include it, expect it to fail, report as data point)
- Use --kernels to avoid phantom specs
- All OpenCL target specs have translation_targets = 2+ files (verified in Session 1.5)

# Prerequisites
- Session 1 complete (submodule reset)
- Session 1.5 complete (kernel-centric pipeline, OpenCL specs have translation_targets)
- API keys configured for both models

# Step 1: Activate venv
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Step 2: Run both models
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-opencl \
  --models azure-gpt-4.1 MODEL_ID \
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
  --expected-models azure-gpt-4.1 MODEL_ID \
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
# Commit: "Add cuda-to-opencl eval results for Rodinia (18 kernels × 2 models, kernel-centric)"
```

---

## SESSION 11 — Dashboard Data Refresh

```
ultrathink

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

# Step 1: Read the paper outline and all referenced docs
# Step 2: Write to docs/paper_draft.md
# Step 3: Show me the draft for review
# Step 4: Git commit and push
# Message: "SC26 paper draft: §1-§5 (intro, related work, framework, curation, methodology)"
```

---

## SESSION 13 — Paper Draft: Results + Discussion + Conclusion (§6-§8)

```
ultrathink

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

# Step 1: Read eval_summary.md and augmentation results for exact numbers
# Step 2: Append §6-§8 to docs/paper_draft.md
# Step 3: Write abstract (now that all sections exist)
# Step 4: Show me complete draft
# Step 5: Git commit and push
# Message: "SC26 paper draft: §6-§8 (results, discussion, conclusion) + abstract"
```

---

## SESSION 14 — Publication Figures

```
ultrathink

# Session Goal
Generate publication-quality figures and tables for the SC26 paper. These will be
used in both the paper and the dashboard.

# Context
- Design spec: visualizations/DESIGN.md (Okabe-Ito palette, Chart.js, academic aesthetic)
- Paper draft: docs/paper_draft.md (check [FIGURE:] and [TABLE:] placeholders)
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

# Session Goal
Review the complete paper draft for consistency, accuracy, and SC26 readiness.

# Steps:
# 1. Read docs/paper_draft.md end-to-end
# 2. Cross-check ALL numbers against results/evaluation/eval_summary.json
# 3. Verify all figure/table references are consistent
# 4. Check for claims not backed by data
# 5. Ensure related work positioning is accurate
# 6. Fix any inconsistencies, typos, or unclear passages
# 7. Verify page count is within SC26 limits (~10 pages double-column)
# 8. Commit and push final reviewed draft
# Message: "SC26 paper: final review and polish"
```

---

## SESSION 16 — Anonymous GitHub Repo (M1)

```
ultrathink

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

## SESSION 17 — LaTeX Transfer + Final Formatting

```
ultrathink

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

## SESSION 18 — Final Review + Submit

```
ultrathink

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
  --expected-models azure-gpt-4.1 MODEL_ID \
  --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl \
  --expected-levels 0 1 2

# 4. Git status — should be clean after session commit
git status
git log --oneline -3
```
