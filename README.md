# ParBench — Meta-Benchmark for LLM-Based Parallel Code Translation

ParBench is a curated meta-benchmark for evaluating how well large language models
translate parallel source code across different programming APIs (CUDA, HIP, SYCL,
OpenMP, etc.). It aggregates kernels from multiple existing benchmark suites and
wraps each one in a machine-readable specification that drives automated build,
run, verification, and LLM evaluation workflows.

## Project Structure

```
parbench_sam/
├── README.md                       # This file
├── GUIDE.md                        # Complete guide: pipeline, commands, adding benchmarks
├── manifest.jsonl                  # Level 1: Master index (one JSON object per line)
│
├── schema/                         # JSON Schemas (draft-07)
│   ├── manifest_schema.json        #   Schema for manifest.jsonl entries
│   ├── spec_schema.json            #   Schema for Level 2 kernel spec files
│   └── reference_platform.json     #   Shared hardware reference platform
│
├── specs/                          # Level 2 spec files (one per kernel variant)
│   └── <suite>-<kernel>-<api>.json
│
├── templates/
│   └── spec_template.json          # Blank spec with all fields & placeholder values
│
├── harness/                        # Python harness: build, run, verify automation
│   ├── cli.py                      #   Command-line interface
│   ├── builder.py                  #   Compilation logic
│   ├── runner.py                   #   Execution logic
│   ├── verifier.py                 #   Verification strategies
│   ├── spec_loader.py              #   JSON loading & path resolution
│   ├── reporter.py                 #   Output formatting
│   └── models.py                   #   Result data classes
│
├── scripts/                        # Utility scripts
│   ├── validate_schema.py          #   Schema + cross-cutting validator
│   ├── generate_pilot_specs.py     #   Generate pilot spec files
│   └── generate_report.py          #   Generate summary reports
│
├── examples/                       # Reference data
│   └── example_178_kernels.json    #   178 kernels in single-file format
│
├── analysis/                       # All analysis outputs
│   ├── visualizations/             #   PNG charts and network graphs
│   ├── reports/                    #   Markdown reports, presentations
│   └── data/                       #   CSV matrices, Excel workbooks
│
└── config/                         # Machine-specific config (git-ignored)
    └── paths.json                  #   Maps downloads_root to local path
```

> **See [GUIDE.md](GUIDE.md) for the complete pipeline walkthrough, all commands, and instructions for adding new benchmarks.**

## Schemas

All schemas use **JSON Schema draft-07**.

### manifest.jsonl

Each line is a self-contained JSON object that indexes one kernel variant:

| Field          | Type   | Required | Description |
|----------------|--------|----------|-------------|
| `kernel_name`  | string | ✓        | Logical kernel name (pairing key) |
| `parallel_api` | enum   | ✓        | API: serial, cuda, hip, sycl, … |
| `source_suite` | string | ✓        | Origin benchmark suite (lowercase) |
| `spec_file`    | string | ✓        | Relative path to Level 2 spec JSON |
| `source_dir`   | string | ✓        | Relative path to kernel source files |
| `category`     | enum   | —        | Domain: ml, graph, physics, … |

### Level 2 Spec (`specs/*.json`)

A comprehensive specification that drives the full evaluation pipeline.
Key sections:

- **identity** — unique_id, kernel name, API, source suite
- **provenance** — repository URL, pinned commit, license
- **files** — `prompt_payload` (LLM sees), `support_files` (build only),
  `verification_only` (never shown to LLM)
- **implementation** — language, API details
- **build** — environment, build system, commands, outputs
- **run** — executable, arguments, input configurations, timeout
- **verification** — method, strategies, floating-point tolerance
- **performance** — optional metric extraction
- **hardware** — target device, requirements, reference platform
- **baseline_results** — populated after benchmarking (starts null)
- **metadata** — description, domain, tags

### File Security Model

The `files` section is **critical** for LLM evaluation integrity:

- `prompt_payload` → Files the LLM receives for translation. **ONLY** these go
  in the prompt.
- `support_files` → Makefiles, shared headers needed for compilation but
  **NOT** sent to the LLM.
- `verification_only` → Reference implementations and test harnesses.
  **NEVER** shown to the LLM.

No file may appear in both `prompt_payload` and `verification_only`.

## Validation

```bash
# Install dependency
pip install jsonschema

# Validate the manifest
python scripts/validate_schema.py --manifest manifest.jsonl

# Validate a single spec
python scripts/validate_schema.py --spec specs/rodinia-bfs-cuda.json

# Validate everything (manifest + all specs)
python scripts/validate_schema.py --all
```

The validator checks:
1. JSON Schema conformance (draft-07)
2. `unique_id` matches the spec filename
3. `unique_id` format matches `{source_suite}-{kernel_name}-{api}`
4. `implementation.api` matches `identity.parallel_api`
5. All files listed in `files.*` exist on disk
6. No file appears in both `prompt_payload` and `verification_only`

## Paths

- All paths in specs and the manifest are **relative to `parbench_sam/`**.
- Downloaded benchmark repos live at `../ParBench/downloads/` relative to this
  directory.

## Requirements

- Python 3.10+
- `jsonschema` (`pip install jsonschema`)
