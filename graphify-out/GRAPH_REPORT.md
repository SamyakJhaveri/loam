# Graph Report - parbench_sam  (2026-04-21)

## Corpus Check
- 192 files · ~733,995 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2226 nodes · 4092 edges · 70 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 856 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]

## God Nodes (most connected - your core abstractions)
1. `Status` - 92 edges
2. `RunResult` - 58 edges
3. `MetricResult` - 45 edges
4. `ChangeNames` - 39 edges
5. `ChangeFunctionNames` - 37 edges
6. `PointerArithmeticToArrayIndex` - 33 edges
7. `resolve_paths()` - 32 edges
8. `SwapCondition` - 31 edges
9. `verify_run()` - 31 edges
10. `main()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `test_wrap_pattern_on_real_spec()` --calls--> `_wrap_pattern()`  [INFERRED]
  tests/test_regex_combiner_integration.py → scripts/evaluation/llm_evaluate.py
- `Return {relative_posix_path: (mtime_ns, size_bytes)} for every regular     file` --uses--> `Status`  [INFERRED]
  scripts/spec_tools/_capture_baseline.py → harness/models.py
- `Return sorted relative paths that are new-in-*after* or whose mtime/size     cha` --uses--> `Status`  [INFERRED]
  scripts/spec_tools/_capture_baseline.py → harness/models.py
- `SHA-256 hex digest of *path* read in 64 KiB chunks.` --uses--> `Status`  [INFERRED]
  scripts/spec_tools/_capture_baseline.py → harness/models.py
- `First + last *lines* of text joined by an elision marker.` --uses--> `Status`  [INFERRED]
  scripts/spec_tools/_capture_baseline.py → harness/models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (201): augment_verify(), _flatten_transforms(), main(), _status_symbol(), build_spec(), harness.builder — Compile a kernel from its spec., Replace ``${VAR}`` placeholders in *command* with default values.      Parameter, Run a shell command, appending output to accumulators.      Returns the process (+193 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (135): ABC, _apply_candidate(), ArithmeticTransform, AstTransform, augment_code(), augment_sample(), AugmentationConfig, _binary_operator_text() (+127 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (134): _augment_level_from_filename(), _build_claim_search_patterns(), build_metadata(), build_paper_claims(), _classify_attempt_status(), _classify_build_fail(), _classify_extraction_fail(), _classify_repair() (+126 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (94): _augment_level_from_filename(), build_markdown(), build_summary(), _cell_key(), _compute_cell_pass_metrics(), _direction_from_ids(), _kernel_from_spec(), _load_complexity_lookup() (+86 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (76): _build_parser(), _build_tasks(), _build_tasks_from_task_list(), _extract_kernel(), _generate_markdown(), main(), Build task dict list from a passer-JSON file (D-25, plan 02-06).      Each entry, Execute all tasks sequentially; return list of result dicts. (+68 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (77): build_matrix(), classify_result(), get_all_slugs(), load_json_result(), load_log_text(), main(), Build a Kernel x API results matrix in Markdown., Discover all unique kernel slugs from result JSON filenames. (+69 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (86): char_data(), _get_corpus_kernels(), _load_spec(), _load_valid_manifest_entries(), manifest.jsonl (valid entries only) contains exactly 12 distinct categories., manifest.jsonl has exactly 206 entries whose spec files exist on disk., manifest.jsonl has 211 total entries (206 valid + 5 phantom)., Every one of the 35 CORPUS_KERNELS has a CUDA spec file on disk. (+78 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (66): Close the underlying HTTP session., aggregate_status_counts(), build_kernel_model_matrix(), _classify_initial_status(), create_status_legend(), _extract_api(), _extract_suite(), filter_records() (+58 more)

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (53): _augment_level_from_filename(), build_primary_matrix(), build_secondary_matrix(), classify_patterns(), compute_aggregates(), _extract_api(), generate_heatmap(), generate_markdown() (+45 more)

### Community 9 - "Community 9"
Cohesion: 0.1
Nodes (48): check(), clear_array(), compile_kernel(), copy_array_from_device(), copy_array_to_device(), getErrorString(), initialize_device(), print_opencl_info() (+40 more)

### Community 10 - "Community 10"
Cohesion: 0.03
Nodes (63): _import_gpd(), paper_data(), Tests for generate_paper_data.py — validates output against verified expected va, Each status category matches the independently verified count., Overall pass rate = 272/710 = 0.3831., cuda-to-omp all-levels = 77/120; opencl-to-cuda L0 = 2/20., Verify first_attempt_pass=160, repaired=112, regressions=7., All self-repair categories must sum to total_tasks. (+55 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (32): check(), clear_array(), compile_kernel(), copy_array_from_device(), copy_array_to_device(), getErrorString(), initialize_device(), print_opencl_info() (+24 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (58): build_taxonomy(), _check_missing_target_api(), classify_build_fail(), classify_extraction_fail(), classify_run_fail(), classify_verify_fail(), extract_direction(), generate_markdown() (+50 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (52): build_known_values(), build_whitelist(), check_provenance_comments(), extract_numbers_from_tex(), load_ground_truth(), main(), match_claims(), Load paper_data.json and quantitative_findings.json. (+44 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (31): _minimal_spec(), Unit tests for harness.spec_loader — synthetic data only.  Validates load_spec,, Attempting to load a nonexistent file raises FileNotFoundError., Malformed JSON raises json.JSONDecodeError., An empty file raises json.JSONDecodeError., Tests for resolve_paths — relative → absolute path resolution., Write a minimal config/paths.json in the temp project root., resolve_paths returns a dict with _resolved key. (+23 more)

### Community 15 - "Community 15"
Cohesion: 0.07
Nodes (20): ANLAskSageClient, ANLAskSageClientError, _ensure_https_url(), _json_dumps_safe(), Perform an HTTP request with robust error handling.          - Enforces HTTPS-, Base exception for ANLAskSageClient errors., Get a short-lived token (required for all other API calls)., Raised when an HTTP request fails. (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.06
Nodes (47): _analyze_augmentation(), _analyze_direction_asymmetry(), analyze_passk(), analyze_primary(), _analyze_self_repair(), _analyze_tokens(), _augment_level_from_filename(), classify_build_fail() (+39 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (45): call_llm(), _derive_llm_seed(), _capturing_openai_factory(), Plan 02-10 Step 2 (C1-C4): sampling reproducibility plumbing tests.  Verifies th, Azure reasoning deployments (supports_thinking=True) reject     temperature != 1, test_azure_reasoning_includes_seed(), test_azure_reasoning_omits_seed_when_none(), test_azure_reasoning_omits_temperature_and_top_p() (+37 more)

### Community 18 - "Community 18"
Cohesion: 0.06
Nodes (37): pytest_collection_modifyitems(), pytest configuration for the ParBench test suite.  Auto-skips tests marked @pyte, Symlink PROJECT_ROOT entries into ``tmp_path`` so tests using ``tmp_path``     a, Skip integration tests when benchmark source directories are absent.      Also s, stage_tmp_project_root(), Phase 2 / Plan 02-07: End-to-end smoke test for the canonical eval config.  Gate, Derive the cuda-to-omp target spec Path from a CUDA source spec., REQUIRED_RESULT_FIELDS has exactly 7 entries (D-29). (+29 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (34): derive_passers(), _load_result(), main(), Derive L0 passer-set for a given model from a canonical eval directory.  Phase 2, Load a result JSON, mirroring analyze_eval.py:_load_complexity_lookup's     try/, Return sorted passer list. Pure function — no filesystem writes.      Per D-18:, Phase 2 / Plan 02-05 tests: derive_l0_passers filter semantics (D-22)., Default --out path = .planning/eval-selections/l0_passers_{model}.json. (+26 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (32): compute_api_coverage(), compute_categories(), compute_language_features(), compute_language_standards(), compute_multi_file(), compute_sloc(), generate_markdown(), main() (+24 more)

### Community 21 - "Community 21"
Cohesion: 0.09
Nodes (30): build_comparison(), classify_effect_size(), cohens_h(), main(), Cohen's h effect size for two proportions.      Clamp inputs to [0, 1] to handle, Classify |h| per Cohen's conventions.      |h| < 0.2: negligible     0.2 <= |h|, Build the full cross-model comparison dict.      Args:         qwen_data: Parsed, _make_dir_data() (+22 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (23): _load_result(), _load_spec(), Integration tests for regex pattern combiner using real benchmark data.  Tests _, Verify _wrap_pattern handles every real (?i) pattern from specs on disk., Test _build_cross_api_verify_spec with actual spec pairs from disk., The exact spec pair that triggered the bug: nn-opencl → nn-cuda., Second affected pair: nn-opencl → nn-omp., (?i) from source must NOT make the target pattern case-insensitive. (+15 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (19): GetDeviceID(), GetMaxDeviceWGSize(), StoreDeviceInfo(), main(), init_vector(), main(), argument_parsing(), main() (+11 more)

### Community 24 - "Community 24"
Cohesion: 0.1
Nodes (29): build_commands(), build_environment(), build_input_configs(), build_variables(), build_verification_strategies(), detect_language(), generate_api_gaps_report(), is_utility_file() (+21 more)

### Community 25 - "Community 25"
Cohesion: 0.26
Nodes (23): _make_run(), _sha256_of(), _spec_with_file_hash(), test_file_hash_absolute_path_fails(), test_file_hash_correct_sha_passes(), test_file_hash_missing_file_fails(), test_file_hash_none_working_dir_errors(), test_file_hash_parent_traversal_fails() (+15 more)

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (23): _check_cross_kernel_pairing(), _check_manifest_spec_consistency(), _get_validator(), _load_json(), _load_manifest_entries(), main(), Validate a Level 2 spec dict against the spec schema, plus cross-cutting     con, Load all entries from manifest.jsonl. (+15 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (22): capture_baseline(), _diff_snapshots(), _head_tail(), main(), First + last *lines* of text joined by an elision marker., Run a single baseline capture. See module docstring for invariants.      Prints, # NOTE: scenario (d) — binary writes on run 1 only — will appear deterministic h, Return {relative_posix_path: (mtime_ns, size_bytes)} for every regular     file (+14 more)

### Community 28 - "Community 28"
Cohesion: 0.2
Nodes (17): analyze_makefile(), categorize_files(), check_shared_data(), detect_build_system(), detect_verification(), find_data_dependencies(), find_files_recursive(), main() (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.18
Nodes (16): _fmt_phase3_row(), _fmt_phase4_row(), _fmt_rodinia_row(), generate_build_data(), generate_results_data(), js_val(), kernel_batch(), _load_phase3_hecbench() (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.18
Nodes (15): classify_result(), _classify_run_failure(), _extract_build_error(), _extract_run_error(), generate_report(), load_json_result(), load_log_result(), main() (+7 more)

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (15): compare_outputs(), ComparisonResult, compile_and_run(), create_standalone_main(), load_augmented_jsonl(), main(), If the code doesn't have a main function, wrap it with a simple test harness., Compare outputs, allowing for small floating-point differences. (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (15): _load_oracle_strength(), _load_strategies(), S7c Stage 3: bucket2 mis-labeled-strong specs upgraded to numeric_comparison.  F, S7c: extract_regex is the documented bucket2 pattern with a capture group., S7c: bucket2 specs are `oracle_strength: "medium"` post-upgrade.      "strong" i, S7c: existing stdout_pattern strategy is retained (conjunctive verification)., S7c: each bucket2 spec has a numeric_comparison strategy., S7c: numeric_comparison.expected is a finite float (not NaN, not inf). (+7 more)

### Community 33 - "Community 33"
Cohesion: 0.26
Nodes (13): BuildKernel(), flushed_printf(), get_event_duration(), mixbenchGPU(), ReadFile(), ReleaseKernelNProgram(), runbench(), runbench_warmup() (+5 more)

### Community 34 - "Community 34"
Cohesion: 0.23
Nodes (5): grid_init_do_not_profile(), move_simulation_data_to_device(), load_concs(), load_mats(), load_num_nucs()

### Community 35 - "Community 35"
Cohesion: 0.19
Nodes (6): benchmark_omp(), ComputeSpace, measure_operation(), mixbenchCPU(), runbench(), runbench_warmup()

### Community 36 - "Community 36"
Cohesion: 0.24
Nodes (12): _classify(), classify_pairs(), _load_manifest(), _load_spec(), main(), print_summary(), Print a summary table of pair counts by complexity class and direction., Return the number of translation target files for this spec.      Prefers files. (+4 more)

### Community 37 - "Community 37"
Cohesion: 0.15
Nodes (9): Phase 2 / Plan 02-02 + 02-04: MODEL_REGISTRY capability-field invariants.  Enfor, Every expected thinker must be in the registry and set True.     Every other reg, D-05: thinking-capability branches must query MODEL_REGISTRY[model]['supports_th, 2026-04-19: azure-gpt-5.3-chat (never deployed) must not be in registry., azure-gpt-5.4 is the live Azure reasoning model (2026-04-19)., test_azure_gpt_5_4_present_and_thinking_capable(), test_no_startswith_thinking_branching(), test_purged_models_absent() (+1 more)

### Community 38 - "Community 38"
Cohesion: 0.2
Nodes (3): apply(), load(), save()

### Community 39 - "Community 39"
Cohesion: 0.29
Nodes (11): add_cxx14_flag(), fix_cuda_spec(), fix_omp_target(), fix_opencl_spec(), load(), main(), Fix CUDA_DIR path in build command and variable default., Fix OPENCL_INC and OPENCL_LIB paths in build command and variable defaults. (+3 more)

### Community 40 - "Community 40"
Cohesion: 0.24
Nodes (11): classify_source_file(), extract_makefile_info(), extract_omp_makefile_info(), extract_verification_method(), inspect_kernel(), main(), Analyze source files to determine verification method., Extract build target, run command, and data dependencies from Makefile. (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.27
Nodes (11): _file_hash_for(), _oracle_strength(), S7b strong-oracle divergence probes.  Each test captures the audit finding that, CUDA nn_cuda.cu:185 emits `printf("%s --> Distance=%f\\n", ...)`.     OMP nn_ope, bptree CUDA and OMP produce byte-identical output.txt (no FP reduction,     dete, CFD / hotspot / myocyte diverge bit-exact across APIs due to floating-point, CUDA nw/needle.cu:194 comments out `#define TRACEBACK` — no result.txt.     OMP, test_bptree_cuda_omp_hashes_converge() (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (5): _ConvertSMVer2Cores(), GetDevicePeakInfo(), StoreDeviceInfo(), _ConvertSMVer2Cores(), StoreDeviceInfo()

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (9): _compute_complexity(), _compute_targets(), _detect_indent(), main(), process_all_specs(), Compute translation_complexity for a spec as a translation TARGET.      Family 3, Load all specs, standardize fields, optionally write back.      Returns the numb, Detect JSON indentation level from raw file content. (+1 more)

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (9): count_source_files(), discover_kernels(), has_makefile(), has_self_check(), main(), Return {kernel_name: {api_suffix, ...}}., Count source files in a kernel directory., Check if a Makefile exists. (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.33
Nodes (7): benchmark_func(), finalizeEvents_ext(), initializeEvents_ext(), is_equal(), mixbenchGPU(), runbench(), runbench_warmup()

### Community 46 - "Community 46"
Cohesion: 0.36
Nodes (7): classify_attempt_status(), classify_repair(), load_all_results(), main(), Determine the status of a single attempt., Classify the repair outcome., Load all result JSONs.

### Community 47 - "Community 47"
Cohesion: 0.36
Nodes (6): load_json(), main(), generate_markdown(), main(), Run (spec, level) combinations sequentially; write JSON incrementally., run_batch()

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (6): _caller_passes_working_dir(), Contract tests: all production callers of verify_run() must pass working_dir.  S, Return True iff every verify_run(...) call in `caller_path` passes a     `workin, Each `working_dir=<RHS>` kwarg must match the accepted access-pattern     whitel, test_caller_passes_working_dir(), test_caller_uses_resolved_working_dir()

### Community 49 - "Community 49"
Cohesion: 0.47
Nodes (5): main(), make_manifest_entry(), make_spec(), Build a complete spec dict for one XSBench API variant., Build a manifest.jsonl entry for one XSBench API variant.

### Community 50 - "Community 50"
Cohesion: 0.6
Nodes (5): build_cmd(), cu_or_cpp(), extra_makefiles(), main(), make_spec()

### Community 51 - "Community 51"
Cohesion: 0.47
Nodes (5): main(), make_manifest_entry(), make_spec(), Generate a single spec JSON for a kernel+API combination., Generate a manifest.jsonl entry.

### Community 52 - "Community 52"
Cohesion: 0.47
Nodes (5): main(), make_manifest_entry(), make_spec(), Generate a single spec JSON for a kernel+API combination., Generate a manifest.jsonl entry.

### Community 53 - "Community 53"
Cohesion: 0.33
Nodes (5): TDD stubs for Phase 2's campaign_for() classification function.  These tests def, C1: deterministic eval (temp=0, no sample_id). Per D-17, D-19., C2: stochastic eval (temp=0.7, sample_id present). Per D-18, D-19., test_c1_classification(), test_c2_classification()

### Community 54 - "Community 54"
Cohesion: 0.83
Nodes (3): fmt_time(), icon(), main()

### Community 55 - "Community 55"
Cohesion: 0.83
Nodes (3): main(), select_specs(), verify_one()

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): scripts.spec_tools — private helpers for spec oracle upgrade work.

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Shared constants for the ParBench harness and analysis scripts.  EXCLUDED_SPECS:

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Allow running the harness as ``python -m harness``.

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Ensure the base URL is HTTPS and return a normalized value without trailing slas

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Raise an error if the URL is not HTTPS.

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Serialize Python objects to compact JSON strings with safe defaults.

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): Check if this transform can be applied to the code.

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): Apply the transform to the code.

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): Collect AST-backed rewrite candidates.

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): The old f'(?:{p})' wrapping produces invalid regex for every (?i) spec.

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): _wrap_pattern produces a compilable scoped pattern for each real spec.

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): Verify our hardcoded patterns match what's actually in the spec files.

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): All KNOWN_FAIL specs with (?i) produce valid combined patterns.

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): Each affected result should flip (or not) as predicted by the audit.

## Knowledge Gaps
- **724 isolated node(s):** `krn_float`, `krn_double`, `krn_half`, `krn_int`, `Base exception for ANLAskSageClient errors.` (+719 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 57`** (2 nodes): `scripts.spec_tools — private helpers for spec oracle upgrade work.`, `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (2 nodes): `Shared constants for the ParBench harness and analysis scripts.  EXCLUDED_SPECS:`, `constants.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (2 nodes): `__main__.py`, `Allow running the harness as ``python -m harness``.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Ensure the base URL is HTTPS and return a normalized value without trailing slas`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Raise an error if the URL is not HTTPS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Serialize Python objects to compact JSON strings with safe defaults.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `Check if this transform can be applied to the code.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `Apply the transform to the code.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `Collect AST-backed rewrite candidates.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `The old f'(?:{p})' wrapping produces invalid regex for every (?i) spec.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `_wrap_pattern produces a compilable scoped pattern for each real spec.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `Verify our hardcoded patterns match what's actually in the spec files.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `All KNOWN_FAIL specs with (?i) produce valid combined patterns.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (1 nodes): `Each affected result should flip (or not) as predicted by the audit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 10`, `Community 12`, `Community 16`, `Community 22`, `Community 24`, `Community 26`, `Community 30`?**
  _High betweenness centrality (0.280) - this node is a cross-community bridge._
- **Why does `load_spec()` connect `Community 0` to `Community 1`, `Community 4`, `Community 5`, `Community 14`, `Community 27`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `run_spec()` connect `Community 0` to `Community 27`, `Community 7`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 89 inferred relationships involving `Status` (e.g. with `Backup original files before writing translated code.` and `Restore original files after verification.`) actually correct?**
  _`Status` has 89 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `RunResult` (e.g. with `ModelRegistryEntry` and `Load source code files from the source spec for linker symbol search.      Reads`) actually correct?**
  _`RunResult` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `MetricResult` (e.g. with `ModelRegistryEntry` and `Load source code files from the source spec for linker symbol search.      Reads`) actually correct?**
  _`MetricResult` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ChangeNames` (e.g. with `Return (ci.Index, AugmentationConfig) for the given level, or (None, None).` and `Read prompt_payload files, apply augmentation, return contents + transforms.`) actually correct?**
  _`ChangeNames` has 24 INFERRED edges - model-reasoned connections that need verification._