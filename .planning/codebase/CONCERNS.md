# Codebase Concerns

**Analysis Date:** 2026-04-03

---

## Tech Debt

### Hardcoded Absolute Paths — Machine-Specific (HPC SDK 24.3)

- Issue: 51 spec JSON files contain 114+ hardcoded references to `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/`. The NV HPC SDK major version is baked into spec `build.commands.build` strings, `environment_variables.LD_LIBRARY_PATH`, and `environment_variables.CUDA_DIR` defaults.
- Files: `specs/rodinia-*-cuda.json`, `specs/rodinia-*-opencl.json`, `specs/hecbench-*-omp_target.json`, `specs/mixbench-mixbench-opencl.json`, `rodinia/cuda/lavaMD/makefile` (line 35)
- Impact: Any machine running HPC SDK 25.x (e.g., Erel's machine) must symlink `24.3` → `25.7` or sed-replace all 114 occurrences before builds succeed.
- Fix approach: Replace hardcoded version with a `${NV_HPC_SDK_VERSION}` variable resolved from `config/paths.json` or a shell environment variable. `docs/erel_setup_guide.md` documents the symlink workaround.

### Hardcoded GPU Compute Capability — sm_89 Throughout Specs

- Issue: `ARCH=sm_89` (RTX 4070 / RTX 4060) is hardcoded into 280+ spec build command occurrences. `CUDA_FLAG='-arch sm_89'` appears in `specs/rodinia-lavamd-cuda.json` line 63. `CC=nvc++ ... SM=cc89` appears in all 10 `hecbench-*-omp_target.json` specs.
- Files: `specs/hecbench-*-cuda.json` (build commands), `specs/rodinia-lavamd-cuda.json`, `specs/hecbench-*-omp_target.json`
- Impact: Any Ampere or Hopper GPU (sm_80, sm_90) will produce suboptimal binaries or fail if the ARCH is incompatible. Reproducibility on different hardware is blocked.
- Fix approach: Add `compute_capability` to `config/paths.json` and substitute it in spec `build.commands` via the builder.

### Hardcoded Project Root in Analysis Scripts

- Issue: Many analysis scripts hardcode `PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")` directly in the module, bypassing the `--project-root` argument pattern used by the eval pipeline.
- Files: `scripts/analysis/generate_results_matrix.py` (line 18), `scripts/analysis/analyze_rodinia_batch.py` (line 20), `scripts/analysis/analyze_cuda_batch.py` (line 20), `scripts/analysis/analyze_omp_batch.py` (line 9), `scripts/baselines/populate_phase3_baselines.py` (line 19), `scripts/survey/inspect_kernels.py` (lines 18-20), `scripts/survey/survey_hecbench.py` (lines 17-18), `scripts/survey/survey_rodinia.py` (lines 14-16), `scripts/batch/run_eval_campaign.sh` (lines 44, 477)
- Impact: None of these scripts work on Erel's machine or any path other than Samyak's without manual edits. The onboarding guide explicitly warns about `run_eval_campaign.sh` lines 44 and 477.
- Fix approach: Follow the `--project-root` pattern used in `scripts/evaluation/llm_evaluate.py` and `run_eval_batch.py`. Campaign script should export `PROJECT_ROOT` from the git root.

### Hardcoded Pilot Data in Paper Figures Script

- Issue: `scripts/generate_paper_figures.py` contains `AUG_ROBUSTNESS` (lines 170-175) and `XSBENCH_L0` (lines 178-191) dicts with hardcoded results from the legacy 3-model pilot (Claude Sonnet, Gemini Flash-Lite, Groq Llama). These are used as fallback when no result files are found.
- Files: `scripts/generate_paper_figures.py` lines 170-191
- Impact: If the dynamic data loading path fails silently (e.g., result files are missing), figures F7 and F8 will be generated with stale pilot data from a superseded model lineup, producing incorrect paper figures. The current model lineup is Qwen + GPT-4.1 mini; the hardcoded fallback shows Gemini and Groq.
- Fix approach: Remove fallback dicts or add an explicit `--no-fallback` flag that raises an error if dynamic data is unavailable. See `docs/plans/figure_edit_spec.md` for full audit.

### Azure OpenAI API Version Hardcoded

- Issue: `api_version="2025-01-01-preview"` is hardcoded at `scripts/evaluation/llm_evaluate.py` line 871. Azure deprecates preview API versions on rolling schedules.
- Files: `scripts/evaluation/llm_evaluate.py` line 871
- Impact: When Azure retires `2025-01-01-preview`, all Azure-model evaluations will fail with a cryptic HTTP 404.
- Fix approach: Read from `AZURE_API_VERSION` environment variable with this string as default.

### config/paths.json Tracked in .gitignore — Cross-Machine Fragility

- Issue: `config/paths.json` is listed in `.gitignore` (as "Local machine-specific config — generated from template"). However, the current committed file contains Samyak's Linux path (`/home/samyak/Desktop/parbench_sam`). This means the file is tracked but gitignored, so a fresh clone will silently use wrong paths if the file is not regenerated.
- Files: `config/paths.json` (all 3 lines), `.gitignore` line ~20
- Impact: A fresh clone will find the committed `paths.json` OR the gitignore will cause it to be absent, depending on git version — either way, portability is fragile.
- Fix approach: Provide `config/paths.json.template` and a setup script that generates `paths.json` from it. The current `docs/erel_onboarding_guide.md` describes this manually.

---

## Known Bugs (Active)

### Unimplemented Verification Strategies — numeric_comparison Returns SKIP

- Symptoms: 13 spec files declare a `numeric_comparison` verification strategy (floating-point tolerance check). This strategy is not implemented in `harness/verifier.py` (line 64) — it returns `Status.SKIP` unconditionally. The strategy is silently ignored.
- Files: `harness/verifier.py` lines 29-31, 63-68, 203-208; `specs/rodinia-bfs-opencl.json`, `specs/rodinia-cfd-opencl.json`, `specs/rodinia-heartwall-*.json`, `specs/rodinia-huffman-cuda.json`, `specs/rodinia-hybridsort-cuda.json`, `specs/rodinia-kmeans-*.json`, `specs/rodinia-myocyte-*.json`, `specs/rodinia-streamcluster-opencl.json`
- Trigger: Any call to `verify_run()` on these specs. The spec declares `numeric_comparison` but only the `stdout_pattern`/`exit_code` strategies fire.
- Workaround: The specs also include `stdout_pattern` and `exit_code` strategies, which do run. For correctness verification this is "good enough" but floating-point outputs that vary by machine will not be caught.

### Top-Level run_status Can Be Stale (Historical Bug — Old Results)

- Symptoms: In multi-attempt evaluations where attempt 1 reaches RUN stage but attempt 2 is BUILD_FAIL, the top-level `run_status` field retains the attempt-1 value. `overall_status` is correct.
- Files: 68 existing L0 result JSONs in `results/evaluation/` (pre-SESSION-3b fix). Fixed prospectively in `llm_evaluate.py`.
- Trigger: Auditing old results by reading `run_status` instead of `overall_status`.
- Workaround: Always use `overall_status` as authoritative verdict. See `known-issues.md` for the exact rule.

### gpt4.1samples/ Directory Not in results/evaluation/ Structure

- Symptoms: 3 GPT-4.1 mini result files exist at `gpt4.1samples/` (outside the canonical `results/evaluation/{model}/` path). They are untracked in git. These files contain `azure-gpt-4.1-mini` results but are not picked up by `analyze_eval.py` or any other analysis script.
- Files: `gpt4.1samples/rodinia-backprop-cuda-to-rodinia-backprop-omp-L{1,2,3}.json`
- Trigger: Running analysis scripts — they will silently omit these 3 results.
- Workaround: Move files to `results/evaluation/azure-gpt-4.1-mini/` and regenerate `eval_summary.json`.

---

## Security Considerations

### API Keys via Environment Variables — No Validation at Import

- Risk: All 5 API providers (Anthropic, OpenAI, Azure, Groq, Together) require API keys via environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `GROQ_API_KEY`, `TOGETHER_API_KEY`). The keys are read lazily inside provider-specific branches of `_call_llm()`, not at startup. A missing key only surfaces during the first LLM call of a batch run.
- Files: `scripts/evaluation/llm_evaluate.py` lines 772-968
- Current mitigation: Clear `ValueError` messages when keys are missing.
- Recommendations: Add a pre-flight key validation step to `run_eval_batch.py` that checks all required keys for the selected models before any evaluations run.

### No Content Filtering on LLM Outputs Written to Disk

- Risk: Translated files from LLM responses are written directly to benchmark source directories. A malicious or misbehaving LLM response could overwrite files with adversarial content before the backup/restore cycle catches it.
- Files: `scripts/evaluation/llm_evaluate.py` (file write section ~line 1540)
- Current mitigation: Files are backed up before write and restored in `finally` block. The result-immutability hook blocks overwriting existing result JSONs but does NOT block overwriting source files.
- Recommendations: This is low risk in practice for a research context; document that LLM eval should only run in the main repo with backup files, never on irreplaceable code.

---

## Performance Bottlenecks

### Wall-Clock Timing Produces Unreliable Speedup Ratios

- Problem: All 30 PASS results from early eval sessions use `timing_method: "wall_time"`. Sub-millisecond baseline wall times (e.g., 0.001s) produce nonsensical speedup ratios (nn=16.0x, bfs=0.002x). Wall-clock includes OS jitter, I/O, and `cudaMalloc` overhead.
- Files: `scripts/evaluation/llm_evaluate.py` lines 1755-1778 (speedup calculation), all 68 pre-SESSION-3b result JSONs in `results/evaluation/`
- Cause: `measure_cpu_time=False` by default in `run_spec()`. The `baseline_results.configurations.performance.wall_time_seconds` in specs comes from single-run measurements.
- Improvement path: Use `nvprof`/`ncu` for CUDA kernel time and `omp_get_wtime()` around the parallel region for OMP. The `translated_cpu_time_seconds` field exists in the result schema but is `null` in all existing results. The `--measure-cpu-time` flag in `run_spec()` uses `/usr/bin/time -v` which is not sufficient for GPU kernels. See `known-issues.md` (Eval Result Timing Limitations section).

### Groq Llama 3.3 70B Token Cap on Multi-File Kernels

- Problem: Groq Llama 3.3 70B has a 16,384 completion-token cap. Multi-file kernels with large prompts hit this cap: `myocyte` (10 target files, 143K prompt tokens) and `heartwall` (3 target files, 89K prompt tokens) reliably fail.
- Files: `scripts/evaluation/llm_evaluate.py` line 910 (max_completion_tokens is not set for Groq — inherits provider default), `results/evaluation/` (groq heartwall and myocyte results)
- Cause: Groq's API hard cap; no model-specific chunking in the pipeline.
- Improvement path: Skip these kernels for Groq, or implement batched/chunked translation for multi-file kernels.

---

## Fragile Areas

### Rodinia Git Submodule Empty in Worktrees

- Files: `rodinia/rodinia-src/` (all contents)
- Why fragile: Git worktrees do not initialize submodules. Running `harness build` or any `make` in a worktree will silently use empty source directories, producing misleading BUILD_FAIL results that look like spec bugs.
- Safe modification: Only run evaluations from the main repo. Worktrees are safe for code review only.
- Test coverage: No automated check verifies that the submodule is populated before eval starts.

### Spec Run Arguments Fragile to "Helpful" Edits

- Files: `specs/rodinia-nw-omp.json`, `specs/rodinia-hotspot-omp.json`, all OMP specs with `argc` constraints
- Why fragile: The source `argc` check and the spec's `run.input_configurations.correctness.arguments` array must stay in sync. Documentation (README, known-issues.md) has been wrong before. Two specs historically silently failed (producing exit_code=0 with wrong/no output) due to incorrect args based on documentation. The actual argc check lives in the C source.
- Safe modification: Before changing any OMP spec's run arguments, read the actual source C/C++ file's `argc` check (e.g., `rodinia/openmp/nw/needle.cpp:249`, `rodinia/openmp/hotspot/hotspot_openmp.cpp:282`).
- Test coverage: No automated test verifies run args against source argc. Manual verification with `harness run` and checking stdout is required.

### sprint_dashboard.html localStorage Divergence

- Files: `visualizations/sprint_dashboard.html` (lines 873-911, `DEFAULT_TASKS` array)
- Why fragile: Task statuses edited in the browser Kanban are stored in the browser's `localStorage`, not in the git-tracked HTML file. A developer who edits tasks and pushes the branch assumes the changes are in git — they are not. The merge produces a file with stale hardcoded statuses.
- Safe modification: After any kanban session, grep the HTML file directly for changed values before committing: `grep -n "status:\|stat-value" visualizations/sprint_dashboard.html`. Do not trust the browser view.
- Test coverage: None — this is a UI-only concern with no automated protection.

### eval_results_data.js Not Auto-Regenerated

- Files: `visualizations/eval_results_data.js`, `visualizations/llm_evaluation.html` (line 1024)
- Why fragile: `llm_evaluation.html` loads `eval_results_data.js` as a static file. It is generated by `analyze_eval.py --write-dashboard`. After every new eval batch, this file must be manually regenerated or the dashboard shows stale data. There is no hook or CI step enforcing regeneration.
- Safe modification: Run `python3 scripts/evaluation/analyze_eval.py --project-root /home/samyak/Desktop/parbench_sam --output-dir results/evaluation` then copy `visualizations/eval_results_data.js` manually.

### OpenCL Kernel-Only Heuristic Depends on .cl Extension

- Files: `scripts/evaluation/llm_evaluate.py` lines 1196-1210 (`_is_kernel_only_translation()`)
- Why fragile: The predicate `all(t.endswith(".cl") for t in targets)` correctly identifies OpenCL targets but will misclassify any future API that uses `.cl` for non-kernel-only translation, or miss kernel-only APIs that use a different extension.
- Safe modification: When adding new translation targets for non-OpenCL APIs, verify whether they are kernel-only or full-program (host code rewritten) and extend the predicate if needed. The `evaluation.md` rule file documents this.
- Test coverage: Implicitly tested by the OpenCL eval results; no dedicated unit test.

---

## Scaling Limits

### manifest.jsonl Append-Only — No Deduplication Guard

- Current capacity: 206 spec JSON files, corresponding manifest entries (one per spec) plus phantom entries for 5 deleted specs.
- Limit: No upper bound, but the append-only invariant means errors in spec generation produce permanent phantom entries. Five such entries already exist (`rodinia-gaussian-omp`, `rodinia-huffman-omp`, `rodinia-huffman-opencl`, `rodinia-hybridsort-omp`, `rodinia-mummergpu-opencl`). `validate_schema.py --all` produces 15 expected errors from these. Adding suites naively will grow this noise.
- Scaling path: Deduplication is not possible without breaking the append-only invariant. Document phantom entries in `known-issues.md` (already done) and filter them in analysis scripts.

### HeCBench Not Cloned — 135 Expected Validation Errors

- Current capacity: 120 of the expected 135 `validate_schema.py` errors come from HeCBench specs whose `source_dir` does not exist on disk. HeCBench is 1.4 GB and gitignored.
- Limit: Adding more HeCBench specs without cloning the source generates more expected errors, degrading the signal-to-noise ratio in `validate_schema.py`.
- Scaling path: Clone HeCBench on the Linux GPU machine and update `config/paths.json`. The `docs/erel_setup_guide.md` documents the wget procedure.

---

## Dependencies at Risk

### libclang Version Lock to 18.1.1

- Risk: `c_augmentation/augment_dataset.py` depends on libclang Python bindings (`libclang>=18.1`). Libclang AST cursor kinds, token kinds, and type kinds change between LLVM major versions. An upgrade to libclang 19.x could silently change which AST nodes are selected by transforms, producing different augmentations and invalidating reproducibility.
- Impact: All augmentation results (15 tests in `c_augmentation/test_transforms.py`, all 906 eval tasks at L1-L4) depend on stable libclang behavior.
- Migration plan: Pin `libclang==18.1.1` in `requirements-lock.txt` (already done). Never upgrade without re-running all 15 transform tests and spot-checking augmented outputs.

### Together AI API (Qwen) Single-Provider Risk

- Risk: The primary research model (Qwen 3.5 397B-A17B) is accessed exclusively through Together AI's OpenAI-compatible endpoint. If Together AI rate limits, changes pricing, or retires the `Qwen/Qwen3.5-397B-A17B` model identifier, re-running any eval task is impossible.
- Impact: 1,018 Qwen result files (906 primary tasks + 426 pass@k samples) cannot be re-run without alternative access.
- Migration plan: Record Together AI's model version string in result JSONs (already done via `"model"` field). Monitor Together AI model availability. No alternative host is currently identified.

### Azure OpenAI Deployment Controlled by External Collaborator

- Risk: GPT-4.1 mini evaluations depend on a collaborator (Le Chen, ANL) running the evaluations on their own Azure deployment. The `azure-gpt-4.1` model ID is hardcoded in `MODEL_REGISTRY` but maps to a deployment that Samyak does not control. If the collaborator's deployment configuration changes, all GPT-4.1 mini eval results become unverifiable.
- Impact: The paper's second model column is blocked on the collaborator delivering result JSONs in the correct schema.
- Migration plan: Ensure collaborator uses identical `llm_evaluate.py` version and `--project-root` convention. Import their results into `results/evaluation/azure-gpt-4.1-mini/` when available.

---

## Missing Critical Features

### GPT-4.1 Mini Not in MODEL_REGISTRY

- Problem: `scripts/evaluation/llm_evaluate.py` `MODEL_REGISTRY` (lines 61-115) does not contain `azure-gpt-4.1-mini`. The `MODEL_COLORS`, `MODEL_DISPLAY`, `MODEL_DISPLAY_SHORT`, and `MODEL_LINESTYLE` dicts in `scripts/generate_paper_figures.py` also do not contain this model. The 3 sample files in `gpt4.1samples/` show `model: "azure-gpt-4.1-mini"`.
- Blocks: Generating paper figures with GPT-4.1 mini results, running `analyze_eval.py` summary with the new model, producing Table 7 (per-direction results across both models).
- Files: `scripts/evaluation/llm_evaluate.py` lines 61-115, `scripts/generate_paper_figures.py` lines 83-108

### Performance Measurement Infrastructure Not Complete

- Problem: `translated_cpu_time_seconds` and `translated_kernel_time_seconds` are `null` in ALL existing 68+ result JSONs. The `--measure-cpu-time` flag in `harness/runner.py` uses `/usr/bin/time -v` (user+system time), which does not capture GPU kernel time. True CUDA kernel timing requires `nvprof` or `ncu` integration which is not implemented.
- Blocks: Any valid speedup ratio for the paper's performance section. The existing `speedup_ratio` field in result JSONs is computed from unreliable wall-clock baselines.
- Files: `harness/runner.py` lines 54-185, `scripts/evaluation/llm_evaluate.py` lines 1755-1778

### Paper Has 50+ \pending and \tbd Markers Awaiting GPT-4.1 Mini Data

- Problem: `docs/paper/latex/paper.tex` contains 50 occurrences of `\pending{...}` or `\tbd` macros (lines 28-30 define them as red-colored text). These span Tables 7-13 (all multi-model comparisons), all chi-squared tests, the hardware table for the collaborator's machine (lines 611-617), and all cross-model narrative in S6/S7.
- Blocks: Paper submission. The April 8 deadline requires GPT-4.1 mini results and the LaTeX/Overleaf conversion by Erel.
- Files: `docs/paper/latex/paper.tex`, `docs/paper/paper_draft.md` (23 `[PENDING-GEMINI]` markers now rephrased as `[PENDING-GPT]`)

---

## Test Coverage Gaps

### Harness Core (builder.py, runner.py, spec_loader.py) — Zero Unit Tests

- What's not tested: `harness/builder.py` (build command construction, `${VAR}` substitution), `harness/runner.py` (timeout handling, cpu_time parsing, `argv[0]` relay), `harness/spec_loader.py` (path resolution, `resolve_paths()`, augmentation dispatch)
- Files: `harness/builder.py`, `harness/runner.py`, `harness/spec_loader.py`
- Risk: A regression in path resolution or build command construction would break all evaluations and only surface during a live run. The `S-VERIFY` session discovered the `argv[0]` heartwall bug only by running the full pipeline.
- Priority: High — harness is the measurement instrument. Errors produce misleading results, not test failures.

### llm_evaluate.py — No Unit Tests

- What's not tested: `_is_kernel_only_translation()`, `_build_cross_api_run_spec()`, `_build_cross_api_verify_spec()`, `analyze_build_failure()`, `build_translation_prompt()`, file extraction from LLM responses
- Files: `scripts/evaluation/llm_evaluate.py` (2083 lines, 0 test files)
- Risk: The OpenCL kernel-only translation bug (SESSION S-OCLFIX) was a silent 0% pass rate for all OpenCL targets before it was caught by inspection. No test would have caught it automatically.
- Priority: High — bugs here silently produce misleading eval results.

### Analysis Scripts — Partial Test Coverage

- What's not tested: `generate_paper_figures.py` (figure generation logic), `generate_results_matrix.py`, `analyze_rodinia_batch.py`, `analyze_cuda_batch.py`, `selfrepair_analysis.py`, `token_analysis.py`
- What has tests: `statistical_analysis.py` (`test_statistical_analysis.py`), `build_error_taxonomy.py` (`test_build_error_taxonomy.py`), `generate_paper_data.py` (`test_generate_paper_data.py`)
- Files: `scripts/analysis/` (18 scripts, ~4 have tests)
- Risk: Paper figures could be generated from wrong data (e.g., wrong direction filter, wrong model key) with no automated detection. The `AUG_ROBUSTNESS` fallback concern (above) is one example.
- Priority: Medium — wrong figures invalidate paper claims without explicit error.

### No Test for Spec Schema Compliance of New Specs

- What's not tested: `scripts/generators/standardize_specs.py` output conformance, `translation_targets` field completeness check
- Files: `scripts/generators/standardize_specs.py`, `scripts/generators/generate_rodinia_specs.py`
- Risk: A new spec missing `translation_targets` raises `KeyError` mid-evaluation (fail-fast per design, but only at runtime, not generation time).
- Priority: Medium — caught at first eval run, but wastes a batch job startup.

---

## Operational Gotchas

### Historical 169 PASS Results Not Re-Verifiable

- Problem: Before the S-VERIFY fix (2026-03-27), `translated_files` was stored truncated to 200 bytes and `run_stdout_snippet` was null for PASS results. These 169 results cannot be retroactively re-verified because the actual translated code and stdout are lost.
- Files: All result JSONs predating commit `S-VERIFY` in `results/evaluation/`
- Risk: Any PASS result from before S-VERIFY may have been a false positive (exit_code=0 with wrong/no output). The S-VERIFY session confirmed 9 FALSE_PASS specs existed; others may remain in the 169.
- Note: The `protect-cuda-omp-results.sh` hook prevents deletion of CUDA↔OMP results, so re-running to overwrite with `--resume` is not possible without bypassing the hook.

### Batch Eval Campaign Script Has Manual KNOWN_FAIL Exclusion

- Problem: `scripts/batch/run_eval_campaign.sh` manually lists which specs to exclude via hardcoded kernel lists (lines 300-307, 385-387). If a new KNOWN_FAIL spec is identified, this script must be manually updated. There is no programmatic way to mark a spec as KNOWN_FAIL in the spec JSON itself.
- Files: `scripts/batch/run_eval_campaign.sh`, `scripts/batch/run_eval_batch.py`
- Risk: A new KNOWN_FAIL spec included in an eval batch wastes API credits and produces a BUILD_FAIL result that skews aggregate pass rates.
- Fix approach: Add a `"status": "known_fail"` field to spec JSON, and filter on it in `run_eval_batch.py --exclude-known-fail`.

### Analysis Scripts That Load from Hardcoded Paths Are Not Portable to Erel's Machine

- Problem: `scripts/analysis/analyze_rodinia_batch.py`, `scripts/analysis/generate_results_matrix.py`, and 6 others use `PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")` hardcoded (not via `--project-root`). Erel runs eval batches on a separate machine at `/root/parbench`.
- Files: `scripts/analysis/analyze_rodinia_batch.py` line 20, `scripts/analysis/generate_results_matrix.py` line 18, `scripts/analysis/analyze_cuda_batch.py` line 20, `scripts/analysis/analyze_omp_batch.py` line 9, `scripts/baselines/populate_phase3_baselines.py` line 19
- Risk: Silent wrong results if these scripts are run on Erel's machine — they will read from the wrong path and either crash or return empty data.

---

*Concerns audit: 2026-04-03*
