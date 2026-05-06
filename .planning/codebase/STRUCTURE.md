# Codebase Structure

**Analysis Date:** 2026-04-09

## Directory Layout

```
parbench_sam/
├── harness/                    # Build/Run/Verify engine (Python package)
│   ├── __init__.py
│   ├── __main__.py             # python3 -m harness entry point
│   ├── cli.py                  # Argparse CLI (build/run/verify/prompt/info/pairs)
│   ├── models.py               # Dataclasses: Status, BuildResult, RunResult, etc.
│   ├── spec_loader.py          # Load specs, resolve paths, extract prompt payloads
│   ├── builder.py              # Compile kernels via subprocess
│   ├── runner.py               # Execute compiled kernels
│   ├── verifier.py             # Verify outputs (exit_code, stdout_pattern)
│   └── reporter.py             # Format and display pipeline results
│
├── scripts/
│   ├── evaluation/             # LLM evaluation pipeline
│   │   ├── llm_evaluate.py     # Core: single-task LLM translation + grading (85K lines)
│   │   ├── run_eval_batch.py   # Batch orchestrator (builds tasks from manifest)
│   │   ├── analyze_eval.py     # Result aggregation -> eval_summary.json/.md
│   │   ├── reverify_pass_results.py  # Re-check existing PASS results
│   │   └── test_generate_paper_figures.py
│   ├── augmentation/           # Augmentation verification pipeline
│   │   ├── augment_verify.py   # Augment -> build -> run -> verify pipeline
│   │   ├── run_augment_batch.py  # Batch augmentation runner
│   │   └── combine_aug_results.py  # Combine augmentation results
│   ├── analysis/               # Paper data generation & statistical analysis
│   │   ├── quantitative_findings.py  # Main quantitative analysis (147K)
│   │   ├── statistical_analysis.py   # Statistical tests
│   │   ├── build_error_taxonomy.py   # Classify build failures
│   │   ├── benchmark_characterization.py  # Characterize benchmark kernels
│   │   ├── cross_consistency_audit.py  # Cross-check results consistency
│   │   ├── cross_model_comparison.py  # Compare model performance
│   │   ├── generate_paper_data.py    # Generate paper-ready data tables
│   │   ├── token_analysis.py         # LLM token usage analysis
│   │   ├── augmentation_analysis.py  # Augmentation effect analysis
│   │   ├── sloc_analysis.py          # Source lines of code analysis
│   │   ├── selfrepair_analysis.py    # Self-repair (iterative retry) analysis
│   │   ├── classify_translation_pairs.py  # Translation complexity classification
│   │   ├── validate_characterization.py
│   │   ├── generate_report.py
│   │   ├── generate_results_matrix.py
│   │   ├── analyze_cuda_batch.py
│   │   ├── analyze_omp_batch.py
│   │   ├── analyze_rodinia_batch.py
│   │   └── test_*.py           # Tests for each analysis module
│   ├── generators/             # Spec generation scripts (historical)
│   │   ├── generate_rodinia_specs.py
│   │   ├── generate_xsbench_specs.py
│   │   ├── generate_phase2_specs.py
│   │   ├── generate_phase3_specs.py
│   │   ├── generate_pilot_specs.py
│   │   └── standardize_specs.py  # Add translation_targets to all specs
│   ├── baselines/              # Baseline result population scripts
│   │   ├── populate_baseline_results.py
│   │   ├── populate_baselines.py
│   │   └── populate_phase3_baselines.py
│   ├── batch/                  # Shell scripts for running eval campaigns
│   │   ├── run_eval_campaign.sh      # Full multi-direction campaign orchestrator
│   │   ├── run_rodinia_batch.sh
│   │   ├── run_cuda_batch.sh
│   │   ├── run_omp_batch.sh
│   │   ├── _archive/pre-phase3-2026-03-16/  # Archived: run_xsbench_eval.sh, run_rodinia_augmented_eval.sh
│   │   ├── run_qwen_missing_batches.sh
│   │   └── run_phase_api.sh
│   ├── archive/                # Deprecated fix scripts
│   ├── generate_paper_figures.py  # matplotlib figure generation for LaTeX
│   ├── generate_viz_data.py       # Generate JS data for dashboard
│   ├── validate_schema.py         # JSON schema validation for all specs
│   └── setup_claude_for_sam.sh    # Developer environment setup
│
├── c_augmentation/             # AST-based code augmentation (Python package)
│   ├── __init__.py
│   ├── augment_dataset.py      # Core: 6 transform classes + augment_code() (66K)
│   ├── generate_single_aug.py
│   ├── validate_augmentation.py
│   ├── test_transforms.py      # Unit tests for transforms (15 tests)
│   └── requirements.txt        # libclang dependency
│
├── specs/                      # Kernel spec JSON files (206 files)
│   ├── rodinia-*.json          # Rodinia benchmark specs (~120 files)
│   ├── hecbench-*.json         # HeCBench curated specs (~70 files)
│   ├── xsbench-*.json          # XSBench specs (4 files)
│   ├── rsbench-*.json          # RSBench specs (4 files)
│   └── mixbench-*.json         # mixbench specs (3 files)
│
├── schema/                     # JSON Schema definitions
│   ├── spec_schema.json        # Level 2 Kernel Spec schema (34K)
│   ├── manifest_schema.json    # Manifest entry schema
│   └── reference_platform.json
│
├── results/                    # Evaluation and augmentation results (IMMUTABLE)
│   ├── evaluation/             # Phase 3+ results only (pre-Phase-3 data purged 2026-04-20)
│   ├── augmentation/
│   │   ├── retest_post_session2.json     # Definitive augmentation baseline
│   │   ├── retest_post_m9.json
│   │   ├── full_aug_results.json
│   │   ├── eval_{cuda,omp,opencl}.json
│   │   └── phase{3,4,5}_*.json           # Historical phase results
│   └── analysis/                          # (Currently empty)
│
├── manifest.jsonl              # Append-only kernel registry (JSONL, ~200 entries)
│
├── config/
│   ├── paths.json              # Project root + downloads_root paths
│   ├── paths.json.template     # Template for paths.json
│   └── compiler_inventory.txt  # Available compilers on the system
│
├── rodinia/                    # Git submodule (commit 9c10d3ea)
│   └── rodinia-src/            # Rodinia benchmark source (EMPTY in worktrees)
│       ├── cuda/               # CUDA implementations
│       ├── openmp/             # OpenMP implementations
│       ├── opencl/             # OpenCL implementations
│       └── data/               # Benchmark input data files
│
├── HeCBench-master/            # HeCBench benchmarks (GITIGNORED, cloned locally)
│   └── src/                    # 1874 benchmark directories
│
├── xsbench/                    # XSBench benchmark source
│   └── xsbench-src/
│
├── rsbench/                    # RSBench benchmark source
│   └── rsbench-src/
│
├── mixbench/                   # mixbench benchmark source
│   └── mixbench-src/
│
├── visualizations/             # GitHub Pages dashboard
│   ├── index.html              # Redirects to overview.html
│   ├── overview.html           # Project overview dashboard
│   ├── results.html            # Augmentation results browser
│   ├── build_results.html      # Build results browser
│   ├── llm_evaluation.html     # LLM evaluation results
│   ├── pipeline.html           # Pipeline visualization
│   ├── architecture.html       # Architecture diagram
│   ├── augmentation_deep_dive.html
│   ├── benchmark_landscape.html
│   ├── sprint_dashboard.html   # Sprint tracking kanban
│   ├── theme.css               # Shared CSS theme
│   ├── results_data.js         # Augmentation data for dashboard
│   ├── eval_results_data.js    # Evaluation data for dashboard
│   ├── build_results_data.js   # Build data for dashboard
│   └── assets/                 # Logos and images
│
├── templates/
│   └── spec_template.json      # Template for creating new spec files
│
├── patches/
│   └── rodinia-build-fixes.patch  # Toolchain patches for Rodinia submodule
│
├── tests/
│   └── test_campaign_results.py   # Campaign result integrity tests
│
├── analysis/                   # Older analysis outputs
│   ├── data/
│   ├── reports/
│   └── visualizations/
│
├── docs/
│   ├── paper/latex/            # SC26 paper LaTeX source
│   ├── design/                 # Architecture design docs
│   │   ├── kernel_centric_translation.md
│   │   ├── integrate_augmentation_into_harness.md
│   │   └── json_schema_design.md
│   └── eval_campaign/          # Evaluation campaign planning
│
├── dashboard/                  # (Separate dashboard, untracked)
│
├── .claude/                    # Claude Code configuration
│   ├── rules/                  # Conditional rule files (auto-loaded by path)
│   ├── skills/                 # Custom skill definitions (30+ skills)
│   ├── agents/                 # Agent definitions
│   ├── hooks/                  # Pre-commit hooks
│   └── worktrees/              # Worktree configs
│
├── .github/workflows/
│   └── deploy-pages.yml        # GitHub Pages deployment (staticrypt encrypted)
│
├── CLAUDE.md                   # Root project instructions
├── Dockerfile                  # CPU-only validation image (no GPU)
├── pyproject.toml              # Python package config (parbench)
├── requirements.txt            # Python dependencies
├── requirements-lock.txt       # Locked dependency versions
├── .gitmodules                 # Git submodule config (rodinia)
├── .gitignore
└── README.md
```

## Directory Purposes

**`harness/`:**
- Purpose: Core build/run/verify engine for benchmark kernels
- Contains: Python modules implementing the pipeline stages
- Key files: `cli.py` (entry point), `spec_loader.py` (path resolution + file loading), `builder.py` (compilation), `runner.py` (execution), `verifier.py` (correctness checking)
- Invoked as: `python3 -m harness [-v] <subcommand> <spec_file>`

**`scripts/evaluation/`:**
- Purpose: LLM-based code translation evaluation pipeline
- Contains: Core evaluation logic, batch orchestration, result analysis
- Key files: `llm_evaluate.py` (single-task evaluator, 85K lines), `run_eval_batch.py` (batch runner), `analyze_eval.py` (aggregator)
- Critical flag: `--project-root` is required, `--suite` is required for batch runs

**`scripts/analysis/`:**
- Purpose: Generate paper-ready data, statistics, and figures from evaluation results
- Contains: Specialized analysis modules (build errors, complexity, tokens, augmentation effects)
- Key files: `quantitative_findings.py` (147K, comprehensive analysis), `generate_paper_data.py`, `statistical_analysis.py`
- Each analysis module has a corresponding `test_*.py` file

**`c_augmentation/`:**
- Purpose: Semantics-preserving C/C++ code transformations using libclang AST
- Contains: Transform implementations, validation, tests
- Key files: `augment_dataset.py` (66K, all transform classes), `test_transforms.py` (15 unit tests)
- Transform classes: `ArithmeticTransform`, `SwapCondition`, `PointerArithmeticToArrayIndex`, `TypedefExpansion`, `ChangeNames`, `ChangeFunctionNames`

**`specs/`:**
- Purpose: JSON specifications defining every benchmark kernel variant
- Contains: 206 JSON files, one per (suite, kernel, api) tuple
- Naming: `{suite}-{slug}-{api}.json` (e.g., `rodinia-bfs-cuda.json`, `hecbench-nn-omp.json`)
- Suites: rodinia (~120), hecbench (~70), xsbench (4), rsbench (4), mixbench (3)

**`results/`:**
- Purpose: Immutable evaluation and augmentation result storage
- Contains: Per-model directories with per-task result JSONs, batch summaries, aggregated summaries
- Key rule: NEVER modify existing result files; use `--resume` to skip existing

**`schema/`:**
- Purpose: JSON Schema definitions for validation
- Contains: `spec_schema.json` (34K, comprehensive spec validation), `manifest_schema.json`
- Used by: `scripts/validate_schema.py`

**`visualizations/`:**
- Purpose: Password-protected GitHub Pages dashboard
- Contains: HTML pages, CSS theme, JS data files
- Deployed via: `.github/workflows/deploy-pages.yml` with staticrypt encryption
- Data refresh: `python3 scripts/generate_viz_data.py` then `python3 scripts/evaluation/analyze_eval.py --write-dashboard`

## Key File Locations

**Entry Points:**
- `harness/__main__.py`: Harness CLI (`python3 -m harness`)
- `scripts/evaluation/run_eval_batch.py`: Batch LLM evaluation
- `scripts/evaluation/llm_evaluate.py`: Single-task LLM evaluation (also importable)
- `scripts/evaluation/analyze_eval.py`: Result aggregation
- `scripts/validate_schema.py`: Schema validation
- `scripts/generate_paper_figures.py`: Paper figure generation

**Configuration:**
- `config/paths.json`: Project root paths (machine-specific)
- `config/paths.json.template`: Template for creating paths.json
- `pyproject.toml`: Python package definition, dependencies
- `schema/spec_schema.json`: Kernel spec JSON schema
- `schema/manifest_schema.json`: Manifest entry schema
- `.gitmodules`: Git submodule definition (rodinia)

**Core Logic:**
- `harness/spec_loader.py`: Spec loading, path resolution, prompt payload extraction
- `harness/builder.py`: Kernel compilation via subprocess
- `harness/runner.py`: Kernel execution with timeout and timing
- `harness/verifier.py`: Output verification (exit_code + stdout_pattern)
- `scripts/evaluation/llm_evaluate.py`: LLM API calls, file extraction, iterative repair
- `c_augmentation/augment_dataset.py`: All 6 AST transform classes

**Testing:**
- `c_augmentation/test_transforms.py`: Augmentation transform unit tests
- `tests/test_campaign_results.py`: Campaign result integrity tests
- `scripts/analysis/test_*.py`: Analysis module tests (8 test files)
- `scripts/evaluation/test_generate_paper_figures.py`: Figure generation tests

**Data:**
- `manifest.jsonl`: Append-only kernel registry
- `specs/*.json`: Kernel spec definitions
- `results/evaluation/{model}/*.json`: Per-task evaluation results
- `results/evaluation/eval_summary.json`: Aggregated evaluation summary
- `results/evaluation/translation_complexity.csv`: Translation pair complexity classes
- `results/augmentation/*.json`: Augmentation verification results

## Naming Conventions

**Spec Files:**
- Pattern: `{suite}-{slug}-{api}.json`
- Suite: `rodinia`, `hecbench`, `xsbench`, `rsbench`, `mixbench`
- Slug: lowercase kernel name, `+` removed, no uppercase (e.g., `b+tree` -> `btree`, `hotspot3D` -> `hotspot3d`)
- API: `cuda`, `omp`, `opencl`, `omp_target`
- Examples: `rodinia-bfs-cuda.json`, `hecbench-nn-omp.json`, `xsbench-xsbench-opencl.json`

**Spec Identity Fields:**
- `unique_id`: `{suite}-{slug}-{api}` (matches filename without `.json`)
- `kernel_name`: slug form (e.g., `bfs`, `hotspot3d`)
- Regex: `^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$`

**Result Files:**
- L0 (no augmentation): `{src_id}-to-{tgt_id}.json`
- L1-L4 (augmented): `{src_id}-to-{tgt_id}-L{n}.json`
- Pass@k samples: `{src_id}-to-{tgt_id}-s{m}.json`
- Example: `rodinia-bfs-cuda-to-rodinia-bfs-omp.json`, `rodinia-bfs-cuda-to-rodinia-bfs-omp-L2.json`

**Manifest Entries:**
- JSONL format, one entry per line
- Fields: `kernel_name`, `parallel_api`, `source_suite`, `category`, `spec_file`, `source_dir`
- Categories (enum): `ml`, `graph`, `physics`, `linear_algebra`, `stencil`, `reduction`, `sort`, `molecular_dynamics`, `image`, `crypto`, `financial`, `other`

**Python Modules:**
- snake_case for files and functions
- PascalCase for classes
- Module-level loggers: `log = logging.getLogger(__name__)`

**Batch Shell Scripts:**
- Pattern: `run_{scope}_{type}.sh` (e.g., `run_eval_campaign.sh`, `run_rodinia_batch.sh`)

## Where to Add New Code

**New Benchmark Suite:**
1. Clone/add source under project root (e.g., `newsuite/newsuite-src/`)
2. Create spec JSONs: one per (kernel, api) variant in `specs/{suite}-{kernel}-{api}.json`
3. Append manifest entries to `manifest.jsonl` (never modify existing entries)
4. Run `python3 scripts/validate_schema.py --spec specs/{new-spec}.json` to validate
5. Run `python3 -m harness verify specs/{new-spec}.json --project-root .` to test build/run/verify

**New Analysis Script:**
- Place in: `scripts/analysis/{name}.py`
- Test file: `scripts/analysis/test_{name}.py`
- Follow existing pattern: load results from `results/evaluation/`, use `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`

**New Evaluation Feature:**
- Modify: `scripts/evaluation/llm_evaluate.py` (core pipeline)
- Modify: `scripts/evaluation/run_eval_batch.py` (batch orchestration)
- Follow existing patterns for result JSON fields and error handling

**New Augmentation Transform:**
- Add class in: `c_augmentation/augment_dataset.py` (subclass `AstTransform`)
- Add tests in: `c_augmentation/test_transforms.py`
- Register in: `AugmentationConfig.transforms` list in `harness/spec_loader.py:get_prompt_payload()`

**New Verification Strategy:**
- Add handler in: `harness/verifier.py:verify_run()` (replace `_stub_strategy()` call)
- Follow existing pattern: return `VerificationResult` with Status

**New Visualization Page:**
- Create: `visualizations/{name}.html` (copy nav structure from existing page)
- Add nav link to ALL existing HTML files
- Data: generate JS data file via `scripts/generate_viz_data.py` or new data generator

**New Harness Command:**
- Add parser: `harness/cli.py:build_parser()` (new subcommand)
- Add handler: `harness/cli.py:cmd_{name}()` function

## Special Directories

**`rodinia/rodinia-src/`:**
- Purpose: Rodinia benchmark source code (19 kernels x 3 APIs)
- Generated: Git submodule (commit `9c10d3ea`)
- Committed: Submodule reference only (`.gitmodules`)
- CRITICAL: Empty in git worktrees -- never run evaluations in worktrees
- Contains modified Makefiles for toolchain compatibility (9 patches documented in `patches/rodinia-build-fixes.patch`)

**`HeCBench-master/`:**
- Purpose: HeCBench benchmark source (1874 benchmark directories)
- Generated: Manually cloned
- Committed: No (gitignored)
- Location: Must exist at `{downloads_root}/HeCBench-master/`

**`results/`:**
- Purpose: All evaluation and augmentation output
- Generated: By evaluation and augmentation pipelines
- Committed: Yes (immutable after creation)
- RULE: Never modify existing result JSONs; use `--resume` to skip

**`env_parbench/`:**
- Purpose: Python virtual environment
- Generated: `python3 -m venv env_parbench`
- Committed: No (gitignored)

**`.planning/`:**
- Purpose: GSD planning and codebase analysis documents
- Generated: By GSD mapping tools
- Committed: Yes

**`.claude/`:**
- Purpose: Claude Code configuration (rules, skills, agents, hooks)
- Contains: Conditional rules loaded by file path, 30+ custom skills
- Committed: Yes

---

*Structure analysis: 2026-04-09*
