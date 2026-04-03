# Architecture

**Analysis Date:** 2026-04-03

## Pattern Overview

**Overall:** Research pipeline with declarative spec-driven orchestration

**Key Characteristics:**
- Spec-as-contract: each kernel variant is fully described by a JSON spec that drives build, run, verify, and LLM evaluation
- Pipeline pattern: Build → Run → Verify is a linear, short-circuiting pipeline with independent restartability via `--resume`
- Append-only event log: `manifest.jsonl` is an immutable registry; result JSONs are immutable once written
- Kernel-centric translation: LLMs only produce kernel files; host infrastructure is untouched

---

## Layers

**Spec Registry:**
- Purpose: Declare what every kernel variant IS and how to verify it
- Location: `specs/`, `manifest.jsonl`, `schema/`
- Contains: 206 JSON spec files, append-only JSONL manifest, JSON Schema validators
- Depends on: Nothing (source of truth)
- Used by: harness, evaluation pipeline, augmentation pipeline

**Harness (Build/Run/Verify):**
- Purpose: Build a spec's source, run it, and verify output — the "measurement instrument"
- Location: `harness/` (Python package)
- Contains: `spec_loader.py`, `builder.py`, `runner.py`, `verifier.py`, `models.py`, `reporter.py`, `cli.py`
- Depends on: spec files, benchmark source directories (via `config/paths.json`), `c_augmentation/` (optional, for augmented prompts)
- Used by: `scripts/evaluation/llm_evaluate.py`, `scripts/augmentation/augment_verify.py`, CLI (`python3 -m harness`)

**Augmentation Engine:**
- Purpose: Apply semantics-preserving AST transforms to kernel source to create diverse LLM inputs
- Location: `c_augmentation/augment_dataset.py`
- Contains: `Transform` ABC, `AstTransform` subclass, 6 concrete transform classes (see below), `augment_code()` entry point
- Depends on: `libclang` Python bindings
- Used by: `harness/spec_loader.py:get_prompt_payload()` (inline), `scripts/augmentation/augment_verify.py` (standalone)

**LLM Evaluation Pipeline:**
- Purpose: Call LLMs to translate kernels; verify translated code using the harness; write result JSONs
- Location: `scripts/evaluation/`
- Contains: `llm_evaluate.py` (per-task orchestrator), `run_eval_batch.py` (batch runner), `analyze_eval.py` (aggregator)
- Depends on: harness package, spec files, LLM API keys (env vars)
- Used by: `scripts/batch/*.sh` shell scripts for campaign runs

**Results Store:**
- Purpose: Immutable per-task result JSONs and aggregate summaries
- Location: `results/evaluation/{model_name}/`, `results/augmentation/`, `results/analysis/`
- Contains: Per-task JSONs (`{src_id}-to-{tgt_id}.json`), batch summary JSONs/MDs, eval_summary.json
- Depends on: Nothing (append-only outputs)
- Used by: `analyze_eval.py`, `scripts/analysis/*.py`, paper figures

---

## Data Flow

**Full Evaluation Pipeline: spec → LLM → translated code → build → run → verify → result JSON**

1. `run_eval_batch.py` reads `manifest.jsonl` via `load_manifest()`, builds a task list of `(src_spec, tgt_spec, kernel, model, augment_level)` tuples
2. For each task, `evaluate_translation()` in `llm_evaluate.py` is called
3. Source code is loaded via `get_prompt_payload(source_spec, project_root, augment_level)` — optionally applies augmentation transforms
4. Support files (headers) are loaded from `source_spec.files.support_files`; target infrastructure (non-kernel files) from target spec
5. `build_translation_prompt()` constructs system + user messages:
   - Kernel name is stripped (anonymization against data contamination)
   - Source filenames are generalized (`translated_0.cpp`, etc.) via `anon_map`
   - Source code is comment-stripped via `_strip_comments()`
   - Sections: Translation Task, Target Files to Produce, Build Command, Source Code, Support/Header Files, Target Infrastructure Context
6. `call_llm(model, system_msg, messages)` dispatches to provider (Anthropic/OpenAI/Azure/Groq/Google/Together)
7. Response is passed through `strip_think_tags()` then `extract_code_blocks()` (4-tier fallback: `filename=X` annotation → space-separated → fuzzy filename match → single-block)
8. Extracted files are de-anonymized via `anon_map` and written to target's `source_dir`
9. Original files backed up beforehand with `backup_files()`; source headers staged with `_stage_support_headers()`
10. `build_spec(target_spec, project_root)` runs: clean → configure (optional) → build command → executable existence check
11. `run_spec(target_spec, project_root, configuration="correctness")` runs the binary with spec's `input_configurations.correctness.arguments`
12. For cross-API translation: `_build_cross_api_run_spec()` substitutes source run args (LLM preserves source argc parsing); `_build_cross_api_verify_spec()` combines source + target stdout patterns
13. For kernel-only (OpenCL .cl targets): `_is_kernel_only_translation()` returns True → target spec args/patterns used unchanged
14. `verify_run(spec, run_result)` applies strategies in conjunction (ALL must pass): `stdout_pattern` (regex on stdout) AND `exit_code`
15. On failure: `_build_retry_message()` generates targeted error feedback; LLM is re-called (multi-turn) up to `max_retries`
16. Files restored with `restore_files()`; staged headers removed with `_unstage_support_headers()`
17. Result dict written to `results/evaluation/{model}/{src_id}-to-{tgt_id}.json`

**Augmentation-Only Flow: spec → augmented source → build → run → verify**

1. `augment_verify.py` loads spec, resolves paths
2. `augment_code(code, config, ci_index, filename)` applies transforms sequentially (level controls fraction of transforms run and fraction of candidates selected within each transform)
3. Augmented files written to a sibling temp directory (preserving relative data paths)
4. Build → Run → Verify via harness modules

**Harness Build Flow:**
1. `resolve_paths(spec, project_root)` → resolves `repo_root`, `source_dir`, `working_dir`, all file lists to absolute paths using `config/paths.json`
2. `build_spec()`: run `clean` (ignore errors) → optional `configure` → `build` command with `${VARIABLE}` substitution → check `outputs.executable` exists
3. All subprocess calls use `shell=True`, `cwd=working_dir`, 10-minute timeout

**Harness Run Flow:**
1. `run_spec()`: look up `input_configurations[configuration]` → build `cmd = [executable] + arguments` → `subprocess.run(shell=False, cwd=working_dir)` → capture exit code, stdout, stderr
2. argv[0] uses the spec's executable name (relative), not absolute path (critical: some programs parse argv[0])
3. Optional: wrap with `/usr/bin/time -v` to capture CPU user+system time

**Harness Verify Flow:**
1. `verify_run()` iterates `verification.strategies` — ALL non-SKIP strategies must PASS (conjunction semantics post S-VERIFY fix)
2. Supported: `exit_code` (exit_code == expected), `stdout_pattern` (re.search on stdout)
3. Unimplemented: `numeric_comparison`, `file_diff`, `custom_script` (return SKIP, don't block)
4. `extract_metrics()` parses performance metrics via regex from stdout (currently unused in paper)

---

## Key Abstractions

**Spec JSON:**
- Purpose: Declarative contract defining a kernel variant's identity, source, build, run, and verification
- Examples: `specs/rodinia-bfs-cuda.json`, `specs/xsbench-xsbench-omp.json`
- Pattern: `{suite}-{kernel}-{api}.json`; top-level keys: `identity`, `provenance`, `files`, `implementation`, `build`, `run`, `verification`, `performance`, `hardware`, `baseline_results`

**`files` section (security boundary):**
- `prompt_payload`: files the LLM SEES (kernel source)
- `support_files`: files needed to BUILD but not shown to LLM (headers, Makefile)
- `verification_only`: reference implementations NEVER shown to LLM
- `translation_targets`: subset of `prompt_payload`; which files the LLM must PRODUCE (kernel-centric)

**manifest.jsonl:**
- Purpose: Append-only registry linking kernel names to spec files; enables translation pair discovery
- Format: one JSON object per line: `{kernel_name, parallel_api, source_suite, category, spec_file, source_dir}`
- Invariant: never modify existing entries; phantom specs remain as tombstones

**AstTransform (Strategy pattern):**
- Purpose: Each subclass represents one semantics-preserving code rewrite
- Interface: `is_applicable(code, index, filename)` → bool; `apply(code, index, filename)` → `TransformResult`
- Concrete transforms: `ArithmeticTransform` (compound operators), `SwapCondition` (flip comparisons), `PointerArithmeticToArrayIndex` (ptr+i → arr[i]), `TypedefExpansion`, `ChangeNames` (variable renames), `ChangeFunctionNames`
- Level control: `_select_fraction()` selects 0% (L1=1 candidate) to 100% (L4=all) of candidates; shuffled before selection for randomness
- Overlap safety: `_greedy_valid_subset()` builds largest non-overlapping candidate set when merged set fails validation

**MODEL_REGISTRY:**
- Location: `scripts/evaluation/llm_evaluate.py`
- Purpose: Maps model ID strings to provider info; drives `call_llm()` dispatch
- Current providers: Anthropic (`claude-*`), OpenAI (`gpt-*`, `o1-*`, `o3-*`, `o4-*`), Azure (`azure-*`), Groq (`groq-*`), Google Gemini (`gemini-*`), Together AI (`together-*`)

**SpecResult (data model):**
- Location: `harness/models.py`
- Aggregates: `BuildResult`, `dict[str, RunResult]`, `VerificationResult`, `list[MetricResult]`
- Status enum: `PASS`, `FAIL`, `ERROR`, `TIMEOUT`, `SKIP`

---

## Entry Points

**Harness CLI:**
- Location: `harness/__main__.py` → `harness/cli.py:main()`
- Invocation: `python3 -m harness [build|run|verify|prompt|info|pairs] specs/<name>.json`
- Global flags BEFORE subcommand: `-v`, `--json`, `--project-root`, `--manifest`
- Subcommands: `build` (compile only), `run` (run only), `verify` (full pipeline), `prompt` (print LLM prompt), `info` (spec summary), `pairs` (list translation pairs)

**Batch Evaluation:**
- Location: `scripts/evaluation/run_eval_batch.py`
- Invocation: `python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp --models <model> --project-root <root> --resume -v`
- CRITICAL: `--suite` is required to avoid cross-suite kernel name collisions

**Per-Task Evaluation:**
- Location: `scripts/evaluation/llm_evaluate.py:evaluate_translation()`
- Called by: `run_eval_batch.py` (importable) or directly via `__main__`

**Augmentation Verify:**
- Location: `scripts/augmentation/augment_verify.py`
- Invocation: `python3 scripts/augmentation/augment_verify.py specs/<name>.json --augment_level 2 --seed 42 --project-root <root>`

**Result Aggregation:**
- Location: `scripts/evaluation/analyze_eval.py`
- Output: `results/evaluation/eval_summary.json`, `results/evaluation/eval_summary.md`

---

## Error Handling

**Strategy:** Short-circuit pipeline; structured result objects; never raise from pipeline stages

**Patterns:**
- Harness stages return typed result objects (`BuildResult`, `RunResult`, `VerificationResult`) with `Status` enum; never raise on build/run/verify failure
- `evaluate_translation()` uses `try/finally` to guarantee `restore_files()` and `_unstage_support_headers()` always execute
- `overall_status` field is authoritative (not `run_status` top-level field which can contain stale data from multi-attempt regressions)
- EXTRACTION_FAIL is a distinct status: LLM response had no parseable code for expected target files
- Iterative repair: on BUILD_FAIL/RUN_FAIL/VERIFY_FAIL, `_build_retry_message()` generates targeted feedback; `analyze_build_failure()` parses linker errors and maps missing symbols to source file locations

---

## Cross-Cutting Concerns

**Logging:** Python `logging` module; `log = logging.getLogger(__name__)` per module; `-v` flag sets DEBUG level

**Path Resolution:** All relative paths in specs resolved via `harness/spec_loader.py:resolve_paths()` using `config/paths.json` as anchor; never assume cwd

**Anonymization:** `build_translation_prompt()` strips kernel names, descriptions, and code comments before sending to LLM to prevent data contamination

**Reproducibility:** `random.seed(42 + augment_level)` before augmentation; result JSONs store model ID, spec IDs, augment level, timestamp, token counts

**Verification Semantics:** Conjunction (ALL strategies must pass) — established by S-VERIFY fix (2026-03-27); verifier processes strategies in list order; `exit_code` before `stdout_pattern` fails fast on wrong exit but defers output check

---

*Architecture analysis: 2026-04-03*
