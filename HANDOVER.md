# ParBench: System Guide & Rodinia Integration Audit

**Version**: 2.0 (Post-Rodinia Integration)
**Date**: March 2026
**Author**: Samyak Jhaveri
**Audience**: Research team members, Claude Code, future contributors

---

## Part 1: Rodinia Integration Audit

### 1.1 Audit Summary: PASS (with notes)

The Rodinia benchmark suite has been successfully integrated into ParBench. All six issues identified in the initial review have been resolved, Phase 2b testing is complete, and baseline results are populated in the specs.

| Checkpoint | Status | Details |
|---|---|---|
| Spec files generated | ✅ 60 specs | 22 kernels × variable API coverage (CUDA/OMP/OpenCL) |
| leukocyte excluded | ✅ Fixed | No leukocyte specs in `specs/` |
| b+tree → bptree naming | ✅ Fixed | `kernel_name: "bptree"`, `unique_id: "rodinia-bptree-*"` |
| srad uses v2 only | ✅ Fixed | `source_path: "cuda/srad/srad_v2"`, only v2 files in prompt_payload |
| OpenCL vendor neutral | ✅ Fixed | `hardware.requirements.gpu` has no `vendor` or `min_compute_capability` for OpenCL specs |
| API gaps JSON created | ✅ Present | `analysis/data/rodinia_api_gaps.json` with structured per-kernel data |
| Phase 2b testing done | ✅ Complete | `results/rodinia/results_matrix_rodinia.md` and `rodinia_results.json` |
| baseline_results populated | ✅ In specs | Passing specs have `baseline_results` with timestamps, stdout, wall times |
| Manifest appended | ✅ Correct | 180 total entries (120 HeCBench + 60 Rodinia) |
| Schema validation | ✅ Clean | All 60 Rodinia specs conform to `spec_schema.json` |

### 1.2 Test Results Summary (Phase 2b)

Source: `results/rodinia/rodinia_results.json`

| API | Total Specs | Build PASS | Run PASS | Verify PASS | Full PASS |
|---|---|---|---|---|---|
| CUDA | 22 | 18 | 18 | 18 | **18/22 (82%)** |
| OMP | 18 | 17 | 17 | 17 | **17/18 (94%)** |
| OpenCL | 20 | 18 | 16 | 16 | **16/20 (80%)** |
| **Total** | **60** | **53** | **51** | **51** | **51/60 (85%)** |

### 1.3 Failure Analysis (9 specs)

| Spec | Failure Type | Root Cause |
|---|---|---|
| rodinia-cfd-cuda | BUILD_FAIL | Missing `helper_cuda.h` (CUDA samples header) |
| rodinia-cfd-opencl | BUILD_FAIL | C++ standard library compatibility error |
| rodinia-hybridsort-cuda | BUILD_FAIL | Missing `GL/glew.h` (OpenGL dependency) |
| rodinia-kmeans-cuda | BUILD_FAIL | Deprecated `tex1Dfetch` texture API |
| rodinia-mummergpu-cuda | BUILD_FAIL | `suffix-tree.cpp` compilation error |
| rodinia-mummergpu-omp | BUILD_FAIL | Same `suffix-tree.cpp` issue |
| rodinia-pathfinder-opencl | BUILD_FAIL | `main.o` compilation error |
| rodinia-kmeans-opencl | RUN_SEGFAULT | Segfault during execution (exit -11) |
| rodinia-nn-opencl | RUN_SEGFAULT | Segfault during execution (exit -11) |

All failures are source-code issues in the Rodinia repository itself (missing dependencies, deprecated APIs, runtime bugs), not spec or harness problems.

### 1.4 Format Consistency: HeCBench vs Rodinia

Both suites produce specs that conform to the same `spec_schema.json` (version 1.0.0). Key differences are intentional and appropriate:

| Field | HeCBench | Rodinia | Notes |
|---|---|---|---|
| `identity.source_suite` | `"hecbench"` | `"rodinia"` | Correctly distinguishes origin |
| `provenance.repo_root` | `"HeCBench-master/"` | `"rodinia/rodinia-src"` | Different local checkout paths |
| `provenance.repository.url` | `github.com/zjin-lcf/HeCBench` | `github.com/yuhc/gpu-rodinia` | Different upstream repos |
| `provenance.license` | `"MIT"` | `"NCSA/Illinois Open Source License"` | Different licenses |
| APIs covered | CUDA, OMP (2 per kernel) | CUDA, OMP, OpenCL (variable per kernel) | Rodinia adds OpenCL |
| `performance` section | Populated (regex extraction) | `null` | Rodinia outputs less standardized |
| CUDA `hardware.requirements.gpu.vendor` | `"NVIDIA"` | `"NVIDIA"` | Both CUDA targets are NVIDIA |
| OpenCL `hardware.requirements.gpu.vendor` | N/A | `null` (omitted) | OpenCL is vendor-neutral ✅ |
| `baseline_results` | Populated (tested Feb 2026) | Populated (tested Mar 2026) | Both tested on same platform |

**Bottom line**: The two suites are interchangeable from the harness perspective. A tool processing `specs/*.json` can treat all 180 specs identically — the schema is the same, only the provenance differs.

---

## Part 2: How ParBench Works (System Guide)

### 2.1 What ParBench Is

ParBench is a **meta-benchmark** for evaluating LLM-based parallel code translation. It does not create new benchmarks — it curates kernels from existing HPC benchmark suites (HeCBench, Rodinia, etc.) and wraps each in a machine-readable JSON specification that drives automated build, run, and verification workflows.

The core research question ParBench enables: *"Given a kernel written in API X (e.g., CUDA), can an LLM correctly translate it to API Y (e.g., OpenCL), and does the translation produce correct output?"*

### 2.2 Architecture: Two Levels

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: manifest.jsonl                                     │
│  One JSON line per kernel-variant. Lightweight discovery.    │
│  180 entries: 120 HeCBench + 60 Rodinia                     │
│  Fields: kernel_name, parallel_api, source_suite, spec_file │
│  Pairing key: same kernel_name = translation pair            │
└────────────────────────┬────────────────────────────────────┘
                         │ points to
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Level 2: specs/*.json                                       │
│  One JSON file per kernel-API variant. Full specification.   │
│  180 files total                                             │
│  Sections: identity, provenance, files, implementation,      │
│            build, run, verification, hardware,               │
│            baseline_results, metadata                         │
│  Drives: automated build → run → verify pipeline             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 The File Security Model

This is critical for LLM evaluation integrity. Each spec classifies its source files into three tiers:

| Tier | Who Sees It | Purpose | Example |
|---|---|---|---|
| `files.prompt_payload` | **LLM sees these** | The source code to translate. ONLY these files go into the LLM prompt. | `nearestNeighbor.cu`, `bfs.cpp` |
| `files.support_files` | **LLM does NOT see** | Build infrastructure (Makefiles, utility headers). Needed for compilation. | `Makefile`, `CLHelper.h` |
| `files.verification_only` | **LLM NEVER sees** | Reference implementations for correctness checking. | `reference.cu` |

**Rule**: No file may appear in both `prompt_payload` and `verification_only`. Enforced by schema validation.

### 2.4 The Harness Pipeline

The Python harness (`harness/` directory, ~1,400 lines) reads spec files and automates the full evaluation pipeline:

```
spec.json  →  BUILD  →  RUN  →  VERIFY  →  METRICS
               │         │        │          │
               │         │        │          └─ Extract timing data
               │         │        └─ Check exit code, stdout patterns
               │         └─ Execute binary with arguments + timeout
               └─ make clean → configure → build → check executable exists
```

**CLI commands**:
- `python3 -m harness build specs/rodinia-bfs-cuda.json` — build only
- `python3 -m harness run specs/rodinia-bfs-cuda.json --config correctness` — run only
- `python3 -m harness verify specs/rodinia-bfs-cuda.json` — full pipeline
- `python3 -m harness prompt specs/rodinia-bfs-cuda.json` — extract prompt_payload files (what the LLM would see)
- `python3 -m harness pairs` — enumerate all translation pairs from manifest

### 2.5 How to Use ParBench for LLM Translation Evaluation

This is the end-to-end workflow for evaluating an LLM's ability to translate parallel code:

**Step 1: Select a translation pair**
```
# Find all kernels that have both CUDA and OpenCL variants
grep '"cuda"' manifest.jsonl | jq -r '.kernel_name' | sort > cuda_kernels.txt
grep '"opencl"' manifest.jsonl | jq -r '.kernel_name' | sort > opencl_kernels.txt
comm -12 cuda_kernels.txt opencl_kernels.txt
```
Or use: `python3 -m harness pairs` to enumerate all valid pairs.

**Step 2: Extract the source code (prompt payload)**
```
python3 -m harness prompt specs/rodinia-bfs-cuda.json
```
This outputs ONLY the `prompt_payload` files — the code the LLM is allowed to see. The LLM's task is to translate this code from the source API (CUDA) to the target API (OpenCL).

**Step 3: Send to LLM with translation instructions**
Feed the extracted source code to the LLM with a prompt like:
> "Translate the following CUDA code to OpenCL. Preserve the algorithm and produce compilable, correct code."

**Step 4: Build the LLM's translation**
Take the LLM's output, place it in the target kernel's source directory (using the target spec's `build.working_directory`), and build:
```
python3 -m harness build specs/rodinia-bfs-opencl.json
```

**Step 5: Run and verify**
```
python3 -m harness verify specs/rodinia-bfs-opencl.json
```
The harness compares the LLM's translated code's output against the `baseline_results` stored in the spec. PASS means the translation produces correct output.

**Step 6: Measure and compare**
- Binary correctness: does the translation produce the right output?
- Build success: does the translation even compile?
- Performance: how does translated code's wall time compare to the baseline?
- Error analysis: what patterns emerge in translation failures?

### 2.6 Current Dataset at a Glance

| Metric | Value |
|---|---|
| Benchmark suites | 2 (HeCBench, Rodinia) |
| Total kernels | 82 (60 HeCBench + 22 Rodinia) |
| Total spec files | 180 (120 HeCBench + 60 Rodinia) |
| APIs covered | CUDA, OpenMP, OpenCL |
| Manifest entries | 180 |
| HeCBench test results | 60/60 CUDA pass, 41/60 OMP pass |
| Rodinia test results | 18/22 CUDA pass, 17/18 OMP pass, 16/20 OpenCL pass |
| Overall pass rate | 152/180 specs passing (84%) |
| Translation pairs available | All kernel_name values shared across APIs form pairs |
| Overlapping kernels (both suites) | 6: backprop, gaussian, lud, nn, nw, pathfinder |

### 2.7 Key Repository Files

| Path | What It Is |
|---|---|
| `manifest.jsonl` | Level 1 master index (180 entries) |
| `specs/*.json` | Level 2 spec files (180 files) |
| `schema/spec_schema.json` | JSON Schema (draft-07) — source of truth for spec format |
| `schema/manifest_schema.json` | JSON Schema for manifest entries |
| `harness/` | Python harness (cli, builder, runner, verifier, reporter) |
| `config/paths.json` | Machine-specific path resolution |
| `scripts/generators/generate_phase3_specs.py` | HeCBench spec generator |
| `scripts/generators/generate_rodinia_specs.py` | Rodinia spec generator |
| `analysis/data/rodinia_survey.json` | Rodinia kernel survey data |
| `analysis/data/rodinia_api_gaps.json` | Which APIs are missing per Rodinia kernel |
| `analysis/reports/rodinia_api_gaps.md` | Human-readable gap analysis |
| `results/phase3/results_matrix_phase3.md` | HeCBench 60-kernel test results |
| `results/rodinia/results_matrix_rodinia.md` | Rodinia 22-kernel test results |
| `results/rodinia/rodinia_results.json` | Structured Rodinia test results |

---

## Part 3: The Four-Pillar Research Pipeline

As clarified in the March 2026 team meeting, the ParBench research involves four distinct activities:

### Pillar 1: CURATION (Samyak — largely complete)
Survey existing benchmark suites, select kernels, create spec files, and test on hardware.

**Status**: HeCBench (60 kernels, 120 specs) and Rodinia (22 kernels, 60 specs) are done. More suites can be added by following the same pattern: survey → generate specs → test → populate baseline_results.

### Pillar 2: CREATION (Samyak — next task)
Use AI coding agents (Paracodex, etc.) to **generate missing API variants**. For example, if a kernel has CUDA and OpenMP but not OpenCL, use an LLM to create the OpenCL version.

**Input**: `analysis/data/rodinia_api_gaps.json` — lists 6 missing API variants across 5 kernels:
- dwt2d: missing OMP
- gaussian: missing OMP
- huffman: missing OpenCL and OMP
- hybridsort: missing OMP
- mummergpu: missing OpenCL

**Validation**: Created variants are validated by building, running, and comparing output against existing variants using the harness.

### Pillar 3: AUGMENTATION (Tom — receives files from Samyak/Erel)
Apply semantic-preserving transformations to existing code using **static, rule-based tools** (NOT AI). Purpose: prevent benchmark contamination. If LLMs have seen the original code in training data, augmented versions test genuine translation ability rather than memorization.

**Key distinction**: Creation uses AI to make NEW code. Augmentation uses static tools to transform EXISTING code.

**Examples of augmentation transforms**: variable renaming, loop restructuring, comment removal, reordering of independent statements — all meaning-preserving by construction.

### Pillar 4: VALIDATION (Samyak + Erel)
Runtime correctness testing of all variants (original, created, and augmented) using the ParBench harness. Ensures semantic equivalence across API variants.

---

## Part 4: Instructions for Claude Code

When working in the ParBench repository, follow these rules:

### Environment
- **Always**: `source env_parbench/bin/activate` before any Python work
- **Project root**: `~/Desktop/parbench_sam/`
- **Config**: `config/paths.json` contains machine-specific paths — check it first

### Do NOT
- Modify `schema/spec_schema.json` or `schema/manifest_schema.json` without explicit approval
- Overwrite `manifest.jsonl` — always APPEND
- Touch existing `hecbench-*.json` spec files unless explicitly asked
- Fabricate test results or baseline data — these must come from actual harness runs
- Create new project directories outside the existing structure

### When creating new specs
- Follow the pattern in existing specs (read a few first)
- `unique_id` format: `{source_suite}-{kernel_name}-{parallel_api}` (all lowercase, no special chars)
- Filename must match: `{unique_id}.json`
- Validate against schema: `python3 scripts/validate_schema.py specs/your-new-spec.json`
- Validate all: `python3 scripts/validate_schema.py --all`

### When testing
- Build: `python3 -m harness build specs/{spec}.json`
- Full pipeline: `python3 -m harness verify specs/{spec}.json -v`
- Batch: see `scripts/batch/run_cuda_batch.sh` and `scripts/batch/run_rodinia_batch.sh` for patterns

### When in doubt
- Ask the user before making decisions
- Read existing files before assuming structure
- Use `#websearch` for external references

---

## Part 5: Augmentation Integration Status

### 5.1 Merge Status

The `erel/aug` branch was fully merged into `main` (commit `8efe990`, 2026-03-10). The augmentation subsystem is production-merged but has known bugs at higher levels.

### 5.2 What Was Integrated

| Component | Description |
|---|---|
| `c_augmentation/` module | 6 AST transform types (ArithmeticTransform, SwapCondition, PointerArithmeticToArrayIndex, TypedefExpansion, ChangeNames, ChangeFunctionNames) backed by libclang |
| `harness/cli.py --augment_level` | `harness prompt` command now accepts `--augment_level N` (0–4) |
| `harness/spec_loader.py` | `get_prompt_payload()` applies augmentation to `.cu` and `.c` files (NOT `.cl` — see Known Issues) |
| `scripts/augmentation/augment_verify.py` | Standalone augment→build→run→verify pipeline for testing augmented code |
| `scripts/augmentation/run_augment_batch.py` | Batch runner: spec list × augment levels → JSON + Markdown results |
| `scripts/augmentation/combine_aug_results.py` | Merges 3-stream JSON results into aggregate reports |

### 5.3 Test Results (2026-03-10)

49 Rodinia CUDA/OMP specs tested at levels 1, 2, and 4:

| Level | PASS | BUILD_FAIL | FAIL | Notes |
|---|---|---|---|---|
| L1 | 43/49 (88%) | 6 | 0 | 6 failures from Bug A/B/C |
| L2 | 43/49 (88%) | 6 | 0 | Same failures (seed=42 replicable) |
| L4 | 1/49 (2%) | 48 | 0 | Nearly all fail due to Bug A/B/C compounding |

Full results: `results/augmentation/augmentation_status_report_2026-03-10.md`

### 5.4 Known Bugs (c_augmentation — as of 2026-03-10)

**Bug A — PointerArithmeticToArrayIndex: overlapping nested subscripts**
When nested `ARRAY_SUBSCRIPT_EXPR` (e.g., `iS[i]` inside `J[iS[i]*cols+j]`) and its parent are both selected, combined byte-offset edits corrupt the output.
- Fix: validate combined `RewriteCandidate` in `AstTransform.apply()`, or filter overlapping candidates before selection.

**Bug B — PointerArithmeticToArrayIndex: struct member access precedence**
`arr[i].member` → `*((arr)+(i)).member` is wrong; `.` binds tighter than `*`.
- Fix: emit `(*((arr)+(i))).member` instead.

**Bug C — SwapCondition: assignment-in-condition**
`fp = fopen(...) == 0` → `0 == fp = fopen(...)` produces `(0 == fp) = fopen(...)` — non-lvalue error.
- Fix: skip `BINARY_OPERATOR ==` nodes where either child contains an assignment.

**Bug D — typedef struct expansion (noted in status report)**
Some transforms incorrectly expand typedef struct names, causing type mismatch errors.

### 5.5 Known Harness Issue

`harness/spec_loader.py:get_prompt_payload` (line ~195) does NOT augment `.cl` files — `.cl` is missing from the suffix list. `scripts/augmentation/augment_verify.py` DOES augment `.cl` files via `AUGMENTABLE_SUFFIXES`. Fix: add `.cl` to the list in `spec_loader.py`.

### 5.6 Next Steps for Augmentation

1. Fix Bugs A, B, C, D in `c_augmentation/augment_dataset.py`
2. Add `.cl` to `harness/spec_loader.py` suffix list
3. Re-run `scripts/augmentation/run_augment_batch.py` after bug fixes to measure improvement
4. Clone HeCBench locally for full 180-spec coverage (currently only 60 Rodinia specs tested)
5. Integrate augmentation results into the main evaluation pipeline

### 5.7 Key Files

| Path | Purpose |
|---|---|
| `c_augmentation/augment_dataset.py` | Core augmentation engine (libclang AST traversal) |
| `c_augmentation/augment_dataset.py` | 6 transform implementations |
| `c_augmentation/test_transforms.py` | Unit tests: `python3 -m pytest c_augmentation/test_transforms.py -v` |
| `scripts/augmentation/augment_verify.py` | Standalone augment→build→verify pipeline |
| `scripts/augmentation/run_augment_batch.py` | Batch runner for multiple specs × levels |
| `scripts/augmentation/combine_aug_results.py` | Aggregate 3-stream results |
| `results/augmentation/augmentation_status_report_2026-03-10.md` | Full test report with per-spec results |