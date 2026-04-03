# Codebase Structure

**Analysis Date:** 2026-04-03

## Directory Layout

```
parbench_sam/                        # Project root
├── specs/                           # 206 kernel spec JSONs ({suite}-{kernel}-{api}.json)
├── manifest.jsonl                   # Append-only kernel registry (never modify existing entries)
├── schema/                          # JSON Schema validators for specs and manifest
│   ├── spec_schema.json             # Spec format definition
│   ├── manifest_schema.json         # Manifest entry format
│   └── reference_platform.json     # Hardware reference platform schema
├── harness/                         # Python package: Build → Run → Verify pipeline
│   ├── __init__.py
│   ├── __main__.py                  # python3 -m harness entry point
│   ├── cli.py                       # Argument parser and subcommand dispatch
│   ├── models.py                    # BuildResult, RunResult, VerificationResult, Status
│   ├── spec_loader.py               # load_spec, resolve_paths, get_prompt_payload
│   ├── builder.py                   # build_spec(): clean → configure → build → check exe
│   ├── runner.py                    # run_spec(), run_all_configurations()
│   ├── verifier.py                  # verify_run(), extract_metrics()
│   └── reporter.py                  # format_result(), print_prompt_payload()
├── c_augmentation/                  # AST transform engine (libclang)
│   ├── augment_dataset.py           # All transform classes + augment_code() entry point
│   ├── augment_dataset.py           # AugmentationConfig, 6 Transform subclasses
│   ├── generate_single_aug.py       # One-off augmentation helper
│   ├── validate_augmentation.py     # Validate augmented code still compiles
│   ├── test_transforms.py           # pytest unit tests for all transforms (15 tests)
│   └── README.md
├── scripts/                         # Evaluation, augmentation, analysis, batch scripts
│   ├── evaluation/                  # LLM evaluation pipeline
│   │   ├── llm_evaluate.py          # evaluate_translation(): per-task orchestrator
│   │   ├── run_eval_batch.py        # Batch runner (reads manifest, loops tasks)
│   │   ├── analyze_eval.py          # Aggregate results → eval_summary.{json,md}
│   │   └── reverify_pass_results.py # Retroactive verification tool
│   ├── augmentation/                # Augmentation pipeline
│   │   ├── augment_verify.py        # Augment → Build → Run → Verify standalone
│   │   ├── run_augment_batch.py     # Batch augmentation runner
│   │   └── combine_aug_results.py   # Merge augmentation result files
│   ├── batch/                       # Shell scripts for campaign runs (tmux-based)
│   │   ├── run_eval_campaign.sh     # Master campaign script
│   │   ├── run_cuda_batch.sh        # CUDA→X direction batch
│   │   ├── run_omp_batch.sh         # OMP→X direction batch
│   │   └── *.sh                     # Other direction/phase scripts
│   ├── generators/                  # Spec generation tools (write new specs)
│   │   ├── generate_rodinia_specs.py
│   │   ├── generate_xsbench_specs.py
│   │   ├── generate_phase2_specs.py
│   │   ├── generate_phase3_specs.py
│   │   └── standardize_specs.py     # Populate translation_targets in bulk
│   ├── analysis/                    # Paper data analysis scripts
│   │   ├── statistical_analysis.py  # Pass rate statistics, confidence intervals
│   │   ├── token_analysis.py        # LLM token usage analysis
│   │   ├── selfrepair_analysis.py   # Self-repair rate by model
│   │   ├── sloc_analysis.py         # Source lines of code per kernel
│   │   ├── classify_translation_pairs.py  # Complexity class CSV
│   │   ├── build_error_taxonomy.py  # Error taxonomy for paper tables
│   │   └── generate_paper_data.py   # Consolidated paper data export
│   └── validate_schema.py           # Validate specs against JSON Schema (~135 expected errors)
├── results/                         # Immutable result outputs
│   ├── evaluation/                  # LLM eval results
│   │   ├── {model_name}/            # Per-model directory
│   │   │   └── {src_id}-to-{tgt_id}.json          # L0 result
│   │   │   └── {src_id}-to-{tgt_id}-L{n}.json     # Augmented result
│   │   │   └── {src_id}-to-{tgt_id}-s{k}.json     # Pass@k sample
│   │   ├── eval_summary.json        # Authoritative aggregate (use over narrative docs)
│   │   ├── eval_summary.md          # Human-readable summary with tables
│   │   └── translation_complexity.csv  # Complexity class per pair (authoritative)
│   ├── augmentation/                # Augmentation pipeline results
│   └── analysis/                    # Analysis script outputs (paper data)
├── config/                          # Path configuration (platform-specific)
│   ├── paths.json                   # Runtime paths (project_root, downloads_root)
│   └── paths.json.template          # Template for new environments
├── rodinia/                         # Rodinia benchmark suite
│   └── rodinia-src/                 # Git submodule (commit 9c10d3ea) — empty in worktrees
├── xsbench/                         # XSBench benchmark suite
│   └── xsbench-src/                 # Git submodule
├── rsbench/                         # RSBench benchmark suite
│   └── rsbench-src/                 # Git submodule
├── mixbench/                        # Mixbench benchmark suite
│   └── mixbench-src/                # Git submodule
├── HeCBench-master/                 # HeCBench (gitignored, not cloned locally)
├── templates/                       # Spec template files for new kernels
├── examples/                        # Usage examples
├── prompts/                         # Prompt template text files
├── docs/                            # Design documents, session plans, paper drafts
│   ├── design/                      # Architecture decision records
│   │   ├── kernel_centric_translation.md
│   │   └── json_schema_design.md
│   ├── paper/                       # SC26 paper (LaTeX, figures, drafts)
│   │   └── latex/                   # LaTeX source
│   ├── session_plans/               # Detailed per-session work plans
│   └── eval_campaign/               # Campaign tracking documents
├── visualizations/                  # GitHub Pages dashboard (HTML/JS)
├── analysis/                        # Ad-hoc analysis outputs and visualizations
├── tests/                           # Top-level integration tests
├── patches/                         # Rodinia toolchain patch files
├── schema/                          # JSON Schema validators
├── pyproject.toml                   # Package definition (harness + c_augmentation)
├── requirements.txt                 # Pinned dependencies
├── manifest.jsonl                   # Kernel registry (append-only)
├── CLAUDE.md                        # Project instructions for Claude
└── .claude/                         # Claude Code configuration (skills, hooks, rules, agents)
    ├── rules/                       # Auto-loaded instruction files
    ├── skills/                      # Custom slash commands
    ├── hooks/                       # Pre/post tool hooks
    └── agents/                      # Agent definitions
```

---

## Directory Purposes

**`specs/`:**
- Purpose: One JSON file per kernel variant; 206 files total
- Contains: Rodinia (60), XSBench (4), RSBench (4), mixbench (3), HeCBench curated (25 + more in progress)
- Naming: `{suite}-{kernel_slug}-{parallel_api}.json`; slugs are lowercase with `+` removed, no uppercase
- Key files: Any spec — e.g., `specs/rodinia-bfs-cuda.json`, `specs/xsbench-xsbench-omp.json`

**`harness/`:**
- Purpose: Installable Python package providing the Build/Run/Verify measurement instrument
- Key files:
  - `harness/spec_loader.py`: path resolution, manifest loading, prompt payload construction + optional augmentation
  - `harness/builder.py`: subprocess-based build with variable substitution
  - `harness/runner.py`: subprocess-based execution; respects `input_configurations` and optional CPU timing
  - `harness/verifier.py`: strategy-based output verification (exit_code + stdout_pattern conjunction)
  - `harness/models.py`: all result data classes and `Status` enum

**`c_augmentation/`:**
- Purpose: libclang-backed AST transform engine for creating diverse LLM inputs
- Key files:
  - `c_augmentation/augment_dataset.py`: all 6 transform classes, `AugmentationConfig`, `augment_code()`, `augment_sample()`
  - `c_augmentation/test_transforms.py`: 15 unit tests (must all pass before commit)

**`scripts/evaluation/`:**
- Purpose: LLM evaluation orchestration and result analysis
- Key files:
  - `scripts/evaluation/llm_evaluate.py`: `evaluate_translation()` per-task orchestrator (1600+ lines); `call_llm()` provider dispatch; `build_translation_prompt()`; `extract_code_blocks()`
  - `scripts/evaluation/run_eval_batch.py`: batch runner; reads manifest; builds task list; writes per-batch summary JSON/MD
  - `scripts/evaluation/analyze_eval.py`: reads all per-task JSONs; writes `eval_summary.json`, `eval_summary.md`

**`scripts/batch/`:**
- Purpose: Shell scripts for long-running campaign evaluation (designed for tmux)
- Key files: `run_eval_campaign.sh` (master), direction-specific scripts (`run_cuda_batch.sh`, etc.)

**`results/evaluation/`:**
- Purpose: Immutable per-task result JSONs; authoritative data for paper
- Structure: `{model_name}/{src_id}-to-{tgt_id}[-L{n}][-s{k}].json`
- `eval_summary.json`: authoritative aggregate — use this over narrative documentation
- `together-qwen-3.5-397b-a17b/`: only model directory currently populated with full campaign data

**`config/`:**
- Purpose: Platform-specific path configuration
- `paths.json`: resolves `project_root` and `downloads_root` at runtime; loaded by `harness/spec_loader.py:load_config()`
- On Linux: `downloads_root = /home/samyak/Desktop/parbench_sam`; benchmark sources live under project root

**Benchmark Source Directories:**
- `rodinia/rodinia-src/`: git submodule pinned to commit `9c10d3ea`; EMPTY in git worktrees
- `xsbench/xsbench-src/`, `rsbench/rsbench-src/`, `mixbench/mixbench-src/`: git submodules
- `HeCBench-master/`: gitignored, not cloned; causes ~120 expected validation errors

---

## Key File Locations

**Entry Points:**
- `harness/__main__.py`: `python3 -m harness` CLI
- `scripts/evaluation/llm_evaluate.py`: `evaluate_translation()` (importable) and standalone CLI
- `scripts/evaluation/run_eval_batch.py`: batch evaluation orchestrator
- `scripts/augmentation/augment_verify.py`: augmentation + verify standalone pipeline

**Configuration:**
- `config/paths.json`: runtime path resolution (auto-loaded by `harness/spec_loader.py`)
- `pyproject.toml`: package definition; packages are `c_augmentation` and `harness`
- `requirements.txt` / `requirements-lock.txt`: pinned dependencies

**Core Logic:**
- `harness/spec_loader.py`: `resolve_paths()` and `get_prompt_payload()` — all harness consumers start here
- `scripts/evaluation/llm_evaluate.py`: `evaluate_translation()` — full eval pipeline per task
- `c_augmentation/augment_dataset.py`: `augment_code()` — the augmentation entry point

**Registry:**
- `manifest.jsonl`: kernel registry; never modify existing entries; read via `harness/spec_loader.py:load_manifest()`
- `schema/spec_schema.json`: spec format contract; validated by `scripts/validate_schema.py`

**Testing:**
- `c_augmentation/test_transforms.py`: 15 pytest tests for augmentation transforms
- `scripts/evaluation/test_generate_paper_figures.py`: paper figure generation tests
- `scripts/analysis/test_*.py`: analysis script tests

**Results (authoritative):**
- `results/evaluation/eval_summary.json`: authoritative pass rates and counts (use over narrative docs)
- `results/evaluation/translation_complexity.csv`: complexity class per translation pair (treat as append-only)

---

## Naming Conventions

**Spec files:**
- Pattern: `{source_suite}-{kernel_slug}-{parallel_api}.json`
- Suite names: `rodinia`, `xsbench`, `rsbench`, `mixbench`, `hecbench` (all lowercase)
- Kernel slugs: lowercase only; `+` removed (e.g., `b+tree` → `btree`); no uppercase
- API names: `cuda`, `omp`, `opencl`, `omp_target`, `hip`, `sycl`, `openacc`
- Examples: `rodinia-bfs-cuda.json`, `hecbench-convolution1d-omp_target.json`

**Result files:**
- L0 (no augmentation): `{src_spec_id}-to-{tgt_spec_id}.json`
- Augmented (Ln): `{src_spec_id}-to-{tgt_spec_id}-L{n}.json`
- Pass@k sample: `{src_spec_id}-to-{tgt_spec_id}-s{k}.json`
- Batch summaries: `batch_{direction}_{YYYYMMDD_HHMMSS}.{json,md}`
- Example: `rodinia-bfs-cuda-to-rodinia-bfs-omp.json`, `rodinia-nw-cuda-to-rodinia-nw-omp-L2.json`

**Python modules:**
- `harness/*.py`: snake_case modules, class names PascalCase
- `c_augmentation/augment_dataset.py`: monolithic — all transform classes in one file
- `scripts/**/*.py`: snake_case, scripts are executable with `#!/usr/bin/env python3`

**Shell scripts:**
- Pattern: `{action}_{suite_or_direction}_{qualifier}.sh`
- Examples: `run_cuda_batch.sh`, `run_rodinia_baseline.sh`

---

## Where to Add New Code

**New kernel spec:**
1. Write JSON to `specs/{suite}-{kernel}-{api}.json` following `schema/spec_schema.json`
2. Append one entry to `manifest.jsonl` (never modify existing entries)
3. Validate: `python3 scripts/validate_schema.py --spec specs/<name>.json`
4. Verify baseline: `python3 -m harness verify specs/<name>.json --project-root <root>`

**New LLM model:**
1. Add entry to `MODEL_REGISTRY` in `scripts/evaluation/llm_evaluate.py`
2. Add dispatch branch in `call_llm()` in the same file (or reuse existing `openai`-compatible branch)
3. No other files need changing

**New harness verification strategy:**
1. Add branch in `harness/verifier.py:verify_run()` for the new `type` string
2. Implement `_check_{type}()` helper function in the same file
3. Remove the `_stub_strategy(stype)` fallback for that type
4. Update `schema/spec_schema.json` if adding a new required field

**New augmentation transform:**
1. Create a subclass of `AstTransform` in `c_augmentation/augment_dataset.py`
2. Implement `_find_candidates()` (returns `list[RewriteCandidate]`) and inherit `apply()` from `AstTransform`
3. Add to the transform list in `harness/spec_loader.py:get_prompt_payload()` (inline augmentation path)
4. Add to `_build_aug_config()` in `scripts/augmentation/augment_verify.py`
5. Add unit tests in `c_augmentation/test_transforms.py`

**New analysis script:**
- Location: `scripts/analysis/{descriptive_name}.py`
- Reads from: `results/evaluation/` or `results/augmentation/`
- Writes to: `results/analysis/`
- Pattern: `--project-root` flag required; `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`

**New batch evaluation shell script:**
- Location: `scripts/batch/run_{direction_or_suite}_{qualifier}.sh`
- Pattern: always use tmux; always pass `--suite`, `--project-root`, `--resume`
- Template: follow `scripts/batch/run_rodinia_batch.sh`

**New benchmark suite specs:**
1. Add source as git submodule under `{suite}/{suite}-src/`
2. Write a generator in `scripts/generators/generate_{suite}_specs.py`
3. Run `standardize_specs.py` to populate `translation_targets`
4. Add to `known-issues.md` with pass count and any KNOWN_FAIL entries

---

## Special Directories

**`rodinia/rodinia-src/`:**
- Purpose: Rodinia benchmark sources (the primary eval corpus)
- Generated: No — pinned git submodule at commit `9c10d3ea`
- Committed: Submodule reference only (sources are NOT committed)
- Critical: Empty in git worktrees; never run evaluations in worktrees

**`results/`:**
- Purpose: Immutable experiment outputs; result JSONs are never overwritten
- Generated: Yes, by evaluation and analysis scripts
- Committed: Yes — results are checked into git as data
- Invariant: Use `--resume` flag to skip existing results; never `rm` results unless explicitly corrected

**`.planning/codebase/`:**
- Purpose: GSD codebase analysis documents (consumed by `/gsd:plan-phase` and `/gsd:execute-phase`)
- Generated: Yes, by `/gsd:map-codebase`
- Committed: Yes

**`env_parbench/`:**
- Purpose: Python virtual environment
- Generated: Yes (`python3 -m venv env_parbench`)
- Committed: No (gitignored)
- Usage: `source env_parbench/bin/activate` before running any scripts

**`HeCBench-master/`:**
- Purpose: HeCBench benchmark sources (for curated HeCBench specs)
- Generated: Manual clone
- Committed: No (gitignored)
- Status: Not present locally; causes ~120 expected validation errors (do not fix)

**`.claude/`:**
- Purpose: Claude Code project configuration (skills, hooks, rules, agents)
- Generated: No — manually maintained
- Committed: Yes
- Key: `.claude/rules/` files are auto-loaded based on file path patterns

---

*Structure analysis: 2026-04-03*
