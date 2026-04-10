# Portability Audit -- Phase 01

Audit date: 2026-04-10
Scope: All Python files in `harness/`, `scripts/`, and `tests/`.

## Hardcoded Paths Found

### Category 1: `/opt/nvidia/` -- NVIDIA HPC SDK paths

| File | Line(s) | Path | Context |
|------|---------|------|---------|
| `scripts/generators/generate_xsbench_specs.py` | 155, 157 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/{include,lib64}` | Spec generator (one-time, already ran) |
| `scripts/generators/generate_xsbench_specs.py` | 195 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc` | Spec generator (one-time) |
| `scripts/archive/fix_rodinia_run_args.py` | 82 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64` | Archived fix script |
| `scripts/archive/fix_rodinia_paths.py` | 24 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda` | Archived fix script |
| `scripts/archive/fix_rodinia_run_args2.py` | 29 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64` | Archived fix script |

**Assessment:** None in harness/ (production pipeline). All in generators (one-shot) or archive (historical). Acceptable.

### Category 2: `/home/samyak/` -- Absolute project root

| File | Line(s) | Path | Context |
|------|---------|------|---------|
| `scripts/survey/survey_rodinia.py` | 14-16 | `/home/samyak/Desktop/parbench_sam/...` | Survey script (hardcoded PROJECT_ROOT) |
| `scripts/survey/survey_hecbench.py` | 17-18 | `/home/samyak/Desktop/parbench_sam/...`, `/home/samyak/Downloads/...` | Survey script |
| `scripts/baselines/populate_phase3_baselines.py` | 19 | `/home/samyak/Desktop/parbench_sam` | Baseline populator (hardcoded PROJECT_ROOT) |
| `scripts/analysis/analyze_cuda_batch.py` | 8, 20 | `/home/samyak/Desktop/parbench_sam` | Analysis script (hardcoded PROJECT_ROOT) |
| `scripts/analysis/analyze_omp_batch.py` | 9 | `/home/samyak/Desktop/parbench_sam` | Analysis script (hardcoded PROJECT_ROOT) |
| `scripts/analysis/analyze_harness_batch.py` | 22 | `/home/samyak/Desktop/parbench_sam` | Analysis script (hardcoded PROJECT_ROOT) |
| `scripts/analysis/generate_results_matrix.py` | 18 | `/home/samyak/Desktop/parbench_sam` | Analysis script (hardcoded PROJECT_ROOT) |
| `scripts/analysis/statistical_analysis.py` | 1087 | `/home/samyak/Desktop/parbench_sam` | Help text string |
| `scripts/archive/fix_rodinia_paths.py` | 11, 20 | `/home/samyak/Desktop/parbench_sam` | Archived fix script |
| `scripts/archive/fix_omp_specs.py` | 11 | `/home/samyak/Desktop/parbench_sam` | Archived fix script |
| `scripts/archive/fix_rodinia_run_args.py` | 10, 19 | `/home/samyak/Desktop/parbench_sam` | Archived fix script |
| `scripts/archive/fix_rodinia_run_args2.py` | 16, 25 | `/home/samyak/Desktop/parbench_sam` | Archived fix script |
| `tests/test_harness_integration.py` | 27 | `/home/samyak/Desktop/parbench_sam` | Integration test |
| `tests/test_spec_loader_integration.py` | 29 | `/home/samyak/Desktop/parbench_sam` | Integration test |
| `tests/test_campaign_results.py` | 17 | `/home/samyak/Desktop/parbench_sam` | Campaign result test |

Docstring-only occurrences (usage examples, not executed code):
- `scripts/generate_paper_figures.py` (lines 9, 15)
- `scripts/evaluation/llm_evaluate.py` (lines 19, 27)
- `scripts/evaluation/run_eval_batch.py` (lines 11, 19)
- `scripts/evaluation/analyze_eval.py` (line 11)
- `scripts/evaluation/reverify_pass_results.py` (line 10)
- `scripts/generators/standardize_specs.py` (lines 17, 21, 25)
- `scripts/analysis/quantitative_findings.py` (line 20)
- `scripts/analysis/validate_characterization.py` (line 20)
- `scripts/analysis/benchmark_characterization.py` (line 21)
- `scripts/analysis/classify_translation_pairs.py` (line 20)
- `scripts/analysis/selfrepair_analysis.py` (line 20)
- `scripts/analysis/token_analysis.py` (line 20)
- `scripts/analysis/sloc_analysis.py` (line 30)
- `scripts/analysis/augmentation_analysis.py` (line 19)

**Assessment:** Hardcoded PROJECT_ROOT appears in early scripts (survey, archive, some analysis). Newer scripts use `Path(__file__).resolve().parent...` or `--project-root` CLI arg (portable). Tests have hardcoded PROJECT_ROOT (acceptable for single-machine test suite). Docstrings contain the path as usage examples only.

### Category 3: `/usr/local/cuda` -- Standard CUDA paths

| File | Line(s) | Path | Context |
|------|---------|------|---------|
| `scripts/generators/generate_rodinia_specs.py` | 542, 548-549, 569, 575, 580 | `/usr/local/cuda` and subdirs | Rodinia spec generator (build cmd templates and variable defaults) |
| `scripts/survey/survey_rodinia.py` | 538 | `/usr/local/cuda` | Markdown output string |
| `scripts/archive/fix_rodinia_paths.py` | 5, 23, 25, 27 | `/usr/local/cuda` | Archived path migration script |

**Assessment:** All in generators (one-shot) or archive. The `/usr/local/cuda` references in `generate_rodinia_specs.py` produce spec JSON files with those paths embedded -- the specs themselves are the machine-specific artifact.

### Category 4: Harness core (`harness/`) -- ZERO hardcoded paths

The harness Python modules (`builder.py`, `runner.py`, `spec_loader.py`, `verifier.py`, `reporter.py`, `models.py`, `cli.py`) contain **zero hardcoded filesystem paths**. All paths are derived from:
- The `project_root` parameter (passed by caller)
- The `config/paths.json` file (loaded via `spec_loader.load_config()`)
- Spec JSON contents (machine-specific by design)

This makes the harness fully portable across machines.

## config/paths.json Coverage

### What it defines

```json
{
    "project_root": "/home/samyak/Desktop/parbench_sam",
    "downloads_root": "/home/samyak/Desktop/parbench_sam",
    "hecbench_root": "/home/samyak/Desktop/parbench_sam"
}
```

A template exists at `config/paths.json.template` using `{{PROJECT_ROOT}}` placeholders, generated by `scripts/setup_claude_for_sam.sh`.

### Which Python files read config/paths.json

Only **two** Python modules read `config/paths.json` at runtime:

1. **`harness/spec_loader.py`** -- `load_config()` reads it to resolve `downloads_root` for spec path resolution. This is the primary consumer; all harness operations flow through it.
2. **`scripts/validate_schema.py`** -- reads it directly to get `downloads_root` for spec validation.

### What it does NOT cover

- **Compiler paths** (`nvcc`, `nvc++`, `gcc` locations) -- these live in spec JSON build commands, not in paths.json
- **CUDA include/lib paths** (`/opt/nvidia/.../include`, `/opt/nvidia/.../lib64`) -- embedded in spec JSON build commands
- **System tool paths** (`/usr/bin/time`) -- used in `harness/runner.py` for CPU timing; standard POSIX location

### Portable path resolution patterns

The majority of scripts use one of two portable approaches:
- **`Path(__file__).resolve().parent...`** -- derives PROJECT_ROOT from script location (used by ~25 scripts)
- **`--project-root` CLI argument** -- user-supplied at invocation (used by eval pipeline, analysis scripts)

## Spec-Embedded Paths

Build and run commands in spec JSON files (e.g., `specs/rodinia-bfs-cuda.json`) contain machine-specific compiler paths such as:

- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc++`
- `-I/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/include`
- `-L/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64`

This is **by design** -- specs are machine-specific configuration documents. The spec schema supports `build.variables` with `${VAR}` substitution (e.g., `${CUDA_DIR}`) for partial parameterization, but the variable defaults themselves point to the local machine's toolchain. Porting to a different machine requires regenerating specs with updated compiler paths.

## Assessment

| Layer | Portability | Notes |
|-------|-------------|-------|
| **Harness core** (`harness/`) | Fully portable | Zero hardcoded paths; all derived from `project_root` param + `config/paths.json` |
| **Eval pipeline** (`scripts/evaluation/`) | Portable | Uses `Path(__file__)` + `--project-root` CLI arg; docstrings have example paths only |
| **Analysis scripts** (`scripts/analysis/`) | Mixed | Newer scripts use `--project-root`; 4 older scripts have hardcoded `PROJECT_ROOT` |
| **Generator scripts** (`scripts/generators/`) | Not portable | Contain machine-specific compiler paths; one-shot use, already ran |
| **Survey scripts** (`scripts/survey/`) | Not portable | Hardcoded paths; one-shot historical scripts |
| **Archive scripts** (`scripts/archive/`) | Not portable | Historical fix scripts, no longer executed |
| **Test files** (`tests/`) | Not portable | Hardcoded `PROJECT_ROOT`; acceptable for single-machine test suite |
| **Spec JSON files** (`specs/`) | Machine-specific by design | Compiler paths embedded in build commands |

**Overall:** The production pipeline (harness + eval) is portable via `project_root` parameter passing and `config/paths.json`. Hardcoded paths exist only in one-shot generators, archived scripts, tests, and docstring examples -- none in the critical runtime path.

## Deferred

Full portability improvements are deferred post-NeurIPS per PROJECT.md:

1. **Compiler path templating** -- extend `config/paths.json` to include `cuda_dir`, `hpc_sdk_dir`, `opencl_include`, `opencl_lib` and use them in spec generators
2. **Test PROJECT_ROOT** -- replace hardcoded paths in `tests/` with `conftest.py` fixture reading from `config/paths.json`
3. **Analysis script cleanup** -- migrate the 4 remaining hardcoded `PROJECT_ROOT` scripts to `--project-root` CLI pattern
4. **Spec regeneration tooling** -- a `scripts/setup_paths.py` that reads `config/paths.json` and regenerates all specs with correct compiler paths for the current machine

These are quality-of-life improvements that do not affect correctness on the current single-machine setup. The NeurIPS evaluation runs on one machine (`/home/samyak/Desktop/parbench_sam`), so portability is not blocking.
