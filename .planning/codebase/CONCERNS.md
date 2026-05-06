# Codebase Concerns

**Analysis Date:** 2026-04-09

## Tech Debt

**Unimplemented Verification Strategies:**
- Issue: Three verification strategy types (`numeric_comparison`, `file_diff`, `custom_script`) are stubbed out and return SKIP.
- Files: `harness/verifier.py:29-31`, `harness/verifier.py:63-68`, `harness/verifier.py:203-209`
- Impact: Specs that rely on these strategies are silently skipped during verification. Any spec using only these strategy types would get an overall SKIP, masking potential failures. Currently all specs use `exit_code` and/or `stdout_pattern`, so this is latent debt.
- Fix approach: Implement `numeric_comparison` (parse stdout for numeric values, compare with tolerance), `file_diff` (compare output files against reference), and `custom_script` (run a user-provided verification script). Alternatively, document explicitly that these are out of scope and remove the placeholders.

**Monolithic quantitative_findings.py (3,882 lines):**
- Issue: Single file contains all 14 quantitative dimensions for the SC26 paper, mixing data loading, statistical computation, markdown generation, and validation logic.
- Files: `scripts/analysis/quantitative_findings.py`
- Impact: Difficult to test individual dimensions in isolation, high cognitive load for maintenance, merge conflicts when multiple contributors work on different dimensions.
- Fix approach: Extract each dimension (D1-D14) into a separate module under `scripts/analysis/dimensions/`, with a shared data-loading layer and a thin orchestrator.

**Monolithic llm_evaluate.py (2,083 lines):**
- Issue: Contains LLM provider routing, prompt construction, code extraction, file backup/restore, build/run/verify orchestration, retry logic, linker error analysis, and CLI in a single file.
- Files: `scripts/evaluation/llm_evaluate.py`
- Impact: Functions are tightly coupled, making it difficult to test provider routing independently, swap prompt strategies, or add new providers without touching unrelated code.
- Fix approach: Split into modules: `providers.py` (LLM routing), `prompts.py` (prompt construction), `extraction.py` (code block parsing), `orchestrator.py` (evaluate_translation), `cli.py`.

**Pervasive `sys.path.insert` Hacks (20+ files):**
- Issue: Nearly every script outside `harness/` uses `sys.path.insert(0, ...)` to resolve imports from project root. The project lacks proper packaging for `scripts/` modules.
- Files: `scripts/evaluation/llm_evaluate.py:49`, `scripts/evaluation/run_eval_batch.py:33`, `scripts/augmentation/augment_verify.py:33`, `scripts/analysis/quantitative_findings.py`, `scripts/analysis/statistical_analysis.py:45`, and 15+ more.
- Impact: Fragile import resolution, path manipulation conflicts between scripts, impossible to run scripts from arbitrary working directories without manual path setup.
- Fix approach: Make the project installable (`pip install -e .`) and add `scripts/` to `[tool.setuptools.packages.find]` in `pyproject.toml`, or use `__init__.py` + relative imports consistently.

**Duplicated backup_files/restore_files Logic:**
- Issue: `backup_files()` and `restore_files()` functions are copy-pasted between `scripts/evaluation/llm_evaluate.py:1140-1167` and `scripts/evaluation/reverify_pass_results.py:41-50`.
- Files: `scripts/evaluation/llm_evaluate.py`, `scripts/evaluation/reverify_pass_results.py`
- Impact: Bug fixes to one copy are not propagated to the other. The reverify version is a simplified copy that may diverge.
- Fix approach: Extract to a shared utility module (e.g., `harness/file_utils.py`).

**Phantom Manifest Entries (Append-Only Constraint):**
- Issue: 5 phantom spec entries remain in `manifest.jsonl` (deleted specs: gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl). The append-only policy prevents cleanup.
- Files: `manifest.jsonl` (211 lines, 5 entries reference deleted specs)
- Impact: ~15 expected validation errors, confusing for new contributors, requires explicit documentation of "expected failures". Every tool that reads the manifest must handle missing spec files gracefully.
- Fix approach: Either document this permanently as an invariant, or define a one-time manifest compaction operation with full audit trail.

**Hardcoded Batch 1 Data in viz script:**
- Issue: Pre-JSON-era evaluation results are hardcoded as Python dicts rather than loaded from result files.
- Files: `scripts/generate_viz_data.py:25`, `scripts/generate_viz_data.py:198`
- Impact: Data diverges from the authoritative result JSONs, creating a single source of truth problem for visualization.
- Fix approach: Migrate B1 data into proper result JSON format and load uniformly.

**Archived Fix Scripts Still Present:**
- Issue: One-off data migration scripts (`fix_rodinia_run_args.py`, `fix_rodinia_paths.py`, etc.) and a `.bak` file remain in `scripts/archive/`.
- Files: `scripts/archive/fix_omp_specs.py`, `scripts/archive/fix_rodinia_paths.py`, `scripts/archive/fix_rodinia_run_args.py`, `scripts/archive/fix_rodinia_run_args2.py`, `scripts/archive/generate_phase3_specs.py.bak`
- Impact: Low — they are in an archive directory. But they can confuse contributors and show up in grep results.
- Fix approach: Delete or move to a `docs/historical/` branch tag.

## Security Considerations

**Shell Injection in Build Commands:**
- Risk: `harness/builder.py:240-242` passes build commands to `subprocess.run()` with `shell=True`. Build commands come from spec JSON files (`build.commands.build`, `build.commands.clean`, `build.commands.configure`).
- Files: `harness/builder.py:240-242`
- Current mitigation: Spec files are authored by project maintainers and committed to git. The `_substitute_variables()` function at `harness/builder.py:21-47` only replaces `${VAR}` tokens with values from the spec's own `build.variables.*.default` — not from user input.
- Recommendations: This is acceptable for a research benchmark where specs are trusted. If specs were ever user-submitted, sanitize commands or use a whitelist approach. Document the trust model.

**API Keys via Environment Variables (No Validation):**
- Risk: Six LLM providers read API keys from environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `TOGETHER_API_KEY`). Keys are validated only by presence check, not format.
- Files: `scripts/evaluation/llm_evaluate.py:772`, `scripts/evaluation/llm_evaluate.py:809`, `scripts/evaluation/llm_evaluate.py:844-845`, `scripts/evaluation/llm_evaluate.py:891`, `scripts/evaluation/llm_evaluate.py:926`, `scripts/evaluation/llm_evaluate.py:965`
- Current mitigation: `.env` is in `.gitignore`. No `.env` file exists on disk (keys are sourced from shell profile or exported manually).
- Recommendations: Good practice. Consider adding format validation (e.g., Anthropic keys start with `sk-ant-`, OpenAI keys start with `sk-`) to fail fast with clear error messages.

**LLM-Generated Code Execution:**
- Risk: The evaluation pipeline writes LLM-generated code to disk and compiles/executes it via `harness/builder.py` and `harness/runner.py`. Malicious LLM output could execute arbitrary code.
- Files: `scripts/evaluation/llm_evaluate.py:1538-1541` (writes LLM code), `harness/builder.py:240` (compiles), `harness/runner.py:142` (executes)
- Current mitigation: The runner uses `shell=False` for execution (`harness/runner.py:144`), preventing shell injection in the run command. Files are restored after execution (`llm_evaluate.py:1743-1745`). Execution is local on the benchmark machine.
- Recommendations: For production use, run translated code in a sandboxed container (Docker/Podman). For research use on a dedicated GPU machine, current approach is acceptable. Consider adding resource limits (memory, disk) to subprocess calls.

**Translated Code Written to Source Directories:**
- Risk: LLM-translated files are written directly into the target spec's source directory (e.g., `rodinia/openmp/bfs/`), temporarily overwriting reference implementations.
- Files: `scripts/evaluation/llm_evaluate.py:1538-1541`, `scripts/evaluation/llm_evaluate.py:1428-1429` (backup), `scripts/evaluation/llm_evaluate.py:1743-1744` (restore)
- Current mitigation: Files are backed up before overwrite and restored in a `finally` block. The restore logic handles both pre-existing and newly-created files.
- Recommendations: If a crash occurs between write and restore (e.g., power loss, OOM kill), backups (`.parbench_bak` suffix) remain on disk. Add a startup check that detects and cleans orphaned `.parbench_bak` files. The git submodule can also serve as a recovery mechanism (`git checkout -- .` inside the submodule).

**No Rate Limiting for LLM API Calls:**
- Risk: The batch runner (`run_eval_batch.py`) issues LLM API calls sequentially without rate limiting or backoff. If a provider throttles, the error is caught but not retried with exponential backoff.
- Files: `scripts/evaluation/run_eval_batch.py:187-211`, `scripts/evaluation/llm_evaluate.py:1498-1506`
- Current mitigation: LLM call failures break out of the retry loop immediately and record the error.
- Recommendations: Add exponential backoff with jitter for transient API errors (429, 503). The `tenacity` library or a simple retry decorator would suffice.

## Performance Bottlenecks

**Sequential Evaluation Pipeline:**
- Problem: The batch runner (`run_eval_batch.py`) processes all tasks sequentially — one LLM call + build + run + verify at a time.
- Files: `scripts/evaluation/run_eval_batch.py:148-246`
- Cause: Each task writes translated files to the target spec's source directory. Concurrent tasks targeting the same directory would corrupt each other's files.
- Improvement path: Enable parallelism for tasks targeting different kernel directories (no directory conflict). Use a directory lock or copy-on-write pattern. Alternatively, build in isolated temporary directories rather than modifying source directories in-place.

**Full Environment Copy Per Subprocess:**
- Problem: Both `harness/builder.py:237` and `harness/runner.py:120` call `os.environ.copy()` for every subprocess invocation, copying the entire environment.
- Files: `harness/builder.py:237`, `harness/runner.py:120`
- Cause: Environment variables from specs are merged into the process environment.
- Improvement path: Low priority — `os.environ.copy()` is O(n) in env size but fast in practice. Consider caching the base environment if this becomes measurable in large batch runs.

**LLM Client Re-instantiation Per Call:**
- Problem: `call_llm()` creates a new API client object on every invocation (e.g., `anthropic.Anthropic()`, `openai.OpenAI()`). For batch runs of 500+ tasks, this means 500+ client instantiations.
- Files: `scripts/evaluation/llm_evaluate.py:784`, `scripts/evaluation/llm_evaluate.py:821`, `scripts/evaluation/llm_evaluate.py:868`, `scripts/evaluation/llm_evaluate.py:904`, `scripts/evaluation/llm_evaluate.py:938`, `scripts/evaluation/llm_evaluate.py:981`
- Cause: `call_llm()` is a stateless function that determines the provider on each call.
- Improvement path: Create a client factory/cache keyed by (model_prefix, api_key) so clients are reused across calls. Most SDKs maintain HTTP connection pools internally, so the overhead is connection setup, not actual network cost.

**Build Timeout of 10 Minutes Per Spec:**
- Problem: The default build timeout is 600 seconds (`BUILD_TIMEOUT_SECONDS = 600` at `harness/builder.py:18`). A batch of 200+ specs could wait up to 33+ hours if many specs time out.
- Files: `harness/builder.py:18`
- Cause: Conservative default to handle large CUDA compilations (nvcc is slow). Most builds complete in <30 seconds.
- Improvement path: Add per-spec timeout overrides in the spec JSON. Reduce the default to 120 seconds and set higher timeouts only for known slow builds.

## Known Issues & Risks

**8 KNOWN_FAIL Specs (Documented and Managed):**
- Issue: 6 Rodinia + 2 HeCBench specs cannot pass due to toolchain incompatibilities.
- Files: See `.claude/rules/known-issues.md` for the full list.
- Root causes: CUDA 12 removed `texture<>` API (2 specs), missing `GL/glew.h` (1 spec), SIGSEGV/TIMEOUT in OpenCL runtime (2 specs), OMP target compile/verify issues (2 specs).
- Risk: These specs are excluded from eval batches. If accidentally included, they consume LLM API tokens and build time for guaranteed failures.
- Managed via: `known-issues.md` documents the exclusion list. No automated enforcement exists in `run_eval_batch.py` (relies on manual `--kernels` filtering or `--suite` scoping).

**169 Legacy PASS Results Cannot Be Retroactively Verified:**
- Issue: Pre-S-VERIFY session results stored `translated_files` truncated to 200 bytes and `run_stdout_snippet` as null for PASS results. These results verified exit_code only (not stdout_pattern).
- Files: Result JSONs in `results/evaluation_backup_20260328/` (groq, gemini, claude, gemini-flash subdirectories)
- Impact: The 169 legacy results are functionally valid (exit_code verification passed) but cannot be re-verified with the corrected conjunction verification (stdout_pattern + exit_code). They represent a different verification standard than current results.
- Risk: Using legacy and current results in the same analysis conflates two verification standards. The SC26 paper must document this discrepancy or exclude legacy results.

**Stale Top-Level `run_status` in Multi-Attempt Results:**
- Issue: When a multi-attempt evaluation has attempt 1 with RUN_FAIL then attempt 2 with BUILD_FAIL, the top-level `run_status` field retains attempt 1's data.
- Files: `scripts/evaluation/llm_evaluate.py:1827-1835` — top-level fields reflect the `final_*` variables which are reset per attempt (fixed prospectively).
- Impact: Fixed in current code (per-attempt reset at lines 1473-1477). Only the gemini pathfinder result in existing data is affected. Use `overall_status`, not top-level `run_status`, as the authoritative field.

**Wall-Time Speedup Ratios Are Unreliable:**
- Issue: All speedup ratios use `wall_time` for both baseline and translated code. Sub-millisecond baseline times (e.g., 0.001s for nn) produce wildly unreliable ratios (16.0x or 0.002x).
- Files: `scripts/evaluation/llm_evaluate.py:1747-1778`
- Impact: Speedup data in result JSONs should NOT be used in the SC26 paper without caveat. Wall-clock timing includes OS scheduling, I/O, and memory allocation — not kernel execution time.
- Risk: Reviewers will question performance claims based on wall-clock-only measurements.

**GPT Non-Rodinia Results Invalid (209/897):**
- Issue: 209 GPT-4.1 mini result files from Argonne machine have empty prompts due to missing source files.
- Impact: These results show EXTRACTION_FAIL or ERROR — they are invalid and must be re-run locally where source files exist.
- Risk: Including these in analysis would inflate failure rates for GPT-4.1 mini.

**Git Worktrees Don't Initialize Submodules:**
- Issue: The `rodinia/` directory is a git submodule. Git worktrees don't clone submodule contents.
- Files: `rodinia/rodinia-src/` (empty in worktrees)
- Impact: Running evaluations in a worktree silently fails — builds fail because source files are missing, but the pipeline records them as BUILD_FAIL (looks like a legitimate result).
- Risk: Mistaking worktree failures for actual spec failures could corrupt evaluation data.

**HeCBench Source Not Version-Pinned:**
- Issue: `HeCBench-master/` is gitignored and cloned locally (1874 benchmark dirs) but not a git submodule. No commit hash is recorded in version control.
- Files: `HeCBench-master/` (gitignored), spec files in `specs/hecbench-*.json`
- Impact: HeCBench source code can change between machines or after a fresh clone, making results non-reproducible. Each spec's `provenance.commit_hash` field may reference a stale hash.
- Risk: SC26 reviewers may challenge reproducibility of HeCBench-based results.

## Fragile Areas

**Code Block Extraction (4-Tier Fallback):**
- Files: `scripts/evaluation/llm_evaluate.py:1058-1132`
- Why fragile: Extracts translated code from LLM responses using 4 tiers of regex matching (filename=X annotation, space-separated filename, proximity match, single-file fallback). Different LLMs format responses differently. A new LLM with a novel formatting convention could cause extraction failures.
- Safe modification: Add new tiers before Tier 3 (single-file fallback). Never modify Tier 1 patterns without testing against sample responses from all 6+ providers.
- Test coverage: No dedicated unit tests for `extract_code_blocks()`. Testing relies on end-to-end evaluation runs.

**Cross-API Run/Verify Spec Construction:**
- Files: `scripts/evaluation/llm_evaluate.py:1196-1283`
- Why fragile: `_build_cross_api_run_spec()` and `_build_cross_api_verify_spec()` splice source and target spec fields using `copy.deepcopy()` and dict mutation. The kernel-only detection (`_is_kernel_only_translation()`) uses a file-extension heuristic (`.cl` suffix).
- Safe modification: If adding a new API family with separate kernel files (e.g., SYCL with `.dp.cpp`), update the `_is_kernel_only_translation()` heuristic.
- Test coverage: No unit tests. Logic is validated by end-to-end eval passes.

**Augmentation Transform Interaction:**
- Files: `c_augmentation/augment_dataset.py` (1,952 lines)
- Why fragile: Six transforms (`ArithmeticTransform`, `SwapCondition`, `PointerArithmeticToArrayIndex`, `TypedefExpansion`, `ChangeNames`, `ChangeFunctionNames`) operate on the same source text via byte-offset edits. `_greedy_valid_subset()` prevents overlapping edits, but inter-transform interactions (e.g., renaming a variable that SwapCondition also touches) rely on ordering.
- Safe modification: Always run the full `test_transforms.py` suite after any transform change. The level-invariance property (same result at L1-L4) serves as a regression check.
- Test coverage: 15 tests in `c_augmentation/test_transforms.py`. Coverage is reasonable but does not test all transform combinations.

**Spec Run Argument Correctness:**
- Files: All 206 spec JSON files in `specs/`
- Why fragile: Run arguments must match the exact `argc` check in the source binary. Historical incidents show that documentation-based "fixes" to run args caused specs to silently produce wrong output for weeks (FALSE_PASS).
- Safe modification: ALWAYS read the source code's `argc`/`argv` parsing before changing run args. Never trust documentation or comments alone. Run the binary manually to verify.
- Test coverage: Baseline results recorded in `baseline_results` field of specs. The `reverify_pass_results.py` script can re-check, but it is not run automatically.

## Missing or Incomplete Features

**No Automated KNOWN_FAIL Exclusion:**
- Problem: The 8 KNOWN_FAIL specs must be manually excluded from eval batches via `--kernels` or `--suite` flags. There is no `--exclude-known-fail` flag or automatic filtering.
- Files: `scripts/evaluation/run_eval_batch.py:58-124`
- Blocks: Automated batch scheduling without human review of the kernel list.
- Fix: Add a `known_fail` field to specs or a separate exclusion list that `run_eval_batch.py` reads automatically.

**No Integration/E2E Test Suite for Evaluation Pipeline:**
- Problem: The evaluation pipeline (`llm_evaluate.py` + `run_eval_batch.py`) has no unit tests. The only tests are for analysis scripts.
- Files: Test files exist only in `scripts/analysis/test_*.py` and `c_augmentation/test_transforms.py`. No `scripts/evaluation/test_llm_evaluate.py`.
- Blocks: Confident refactoring of the evaluation pipeline.
- Risk: Regressions in prompt construction, code extraction, or retry logic are caught only by expensive end-to-end evaluation runs.

**No Harness Unit Tests:**
- Problem: The `harness/` package (builder, runner, verifier, spec_loader, cli) has zero unit tests.
- Files: `harness/builder.py`, `harness/runner.py`, `harness/verifier.py`, `harness/spec_loader.py`, `harness/cli.py`
- Blocks: Safe refactoring of the core build/run/verify pipeline.
- Risk: Changes to verification logic (like the conjunction vs. disjunction fix) can only be validated by running actual specs against real compilers, which requires the full GPU toolchain.

**Missing `scipy` in requirements.txt / pyproject.toml:**
- Problem: `scripts/analysis/quantitative_findings.py:38` imports `scipy.stats`, but `scipy` is not listed in `requirements.txt` or `pyproject.toml`.
- Files: `requirements.txt`, `pyproject.toml`, `scripts/analysis/quantitative_findings.py:38`
- Impact: Fresh environment setup fails when running quantitative analysis. The dependency is implicitly satisfied by `numpy` pulling in `scipy` on some systems, but this is not guaranteed.
- Fix: Add `scipy>=1.12` to the `[project.optional-dependencies].analysis` section.

**No CI/CD Pipeline:**
- Problem: No GitHub Actions, Jenkins, or other CI configuration exists. Validation is only run locally via the `/validate` Claude Code command (4-wave loop; pre-commit gate requires waves 1-3, wave 4 optional).
- Impact: PRs can be merged without running tests. Schema validation, augmentation tests, and analysis tests are only run manually or via the `/validate` Claude Code command.
- Fix: Add a GitHub Actions workflow that runs `pytest`, schema validation, and ruff linting on every PR.

## Test Coverage Gaps

**Evaluation Pipeline (Zero Test Coverage):**
- What's not tested: `call_llm()` (provider routing), `extract_code_blocks()` (4-tier parsing), `build_translation_prompt()` (prompt construction), `evaluate_translation()` (full orchestration), `_build_cross_api_run_spec()` / `_build_cross_api_verify_spec()` (spec splicing), `strip_think_tags()`.
- Files: `scripts/evaluation/llm_evaluate.py`, `scripts/evaluation/run_eval_batch.py`
- Risk: Provider routing changes (e.g., adding a new model prefix) could silently break. Code extraction regex changes could cause EXTRACTION_FAIL on valid responses.
- Priority: High — this is the most complex and critical pipeline in the project.

**Harness Core (Zero Test Coverage):**
- What's not tested: `build_spec()`, `run_spec()`, `verify_run()`, `extract_metrics()`, `resolve_paths()`, `get_prompt_payload()`.
- Files: `harness/builder.py`, `harness/runner.py`, `harness/verifier.py`, `harness/spec_loader.py`
- Risk: The conjunction verification fix (all strategies must PASS) was deployed without regression tests. Future changes to verification logic have no safety net.
- Priority: Medium — the harness code is relatively stable, but verification logic changes have historically caused FALSE_PASS incidents.

**Augmentation Transforms (Partial Coverage):**
- What's not tested: Transform combination interactions, edge cases with multi-file augmentation, `.cl` file augmentation paths.
- Files: `c_augmentation/augment_dataset.py`, `c_augmentation/test_transforms.py` (15 tests)
- Risk: Low — the level-invariance property and full-batch retest provide indirect validation.
- Priority: Low.

---

*Concerns audit: 2026-04-09*
