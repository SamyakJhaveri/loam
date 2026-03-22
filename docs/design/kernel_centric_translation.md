# Kernel-Centric Translation Architecture

**Status:** ACTIVE — adopted 2026-03-22 (M11 resolution)
**Decision makers:** Erkap (Erel Kaplan), Niranjan Hasabnis
**Supersedes:** Full-project translation (original design)
**Implementation session:** SESSION 1.5 in `docs/session_prompts_sc26.md`

---

## 1. Core Principle

The LLM's job is to translate **parallel computation**, not replicate project structure.

When we ask an LLM to translate CUDA→OMP and produce the Rodinia OMP reference's exact
file layout, we simultaneously test two orthogonal skills:

1. **Translation quality** — does the LLM correctly map CUDA parallel patterns to OMP?
   ← *what we intend to measure*
2. **Code restructuring ability** — can the LLM replicate a specific file organization
   that the OMP developer chose? ← *a different skill, out of scope*

**Resolution:** Feed source kernel file(s) to the LLM. LLM produces only target kernel
file(s). Target infrastructure (Makefile, headers, utilities, serial baselines) stays
untouched. The evaluation isolates translation quality from file-organization skill.

---

## 2. Team Decision (2026-03-22)

**Erkap (Erel Kaplan):**
> Until now we mainly focused on 1-file kernels to isolate the 'pure translation' skill
> LLM. It is true that multi files can get trickier for various reasons. In my opinion
> Option B is what we should do, for 2 reasons:
> 1. Some codes cant be normalized to 1 file (I think here on OpenCL codes)
> 2. The multi file handling is another skill of the LLM we want to test.

**Niranjan Hasabnis:**
> Yeah I think we should test 1 file kernel only. I mean if a kernel has a directory
> containing Makefile, and other header files, then we only feed kernel.cu to the llm
> and drop in kernel.cl in the corresponding place in opencl directory. Project level
> translation looks next level of challenge.

**Synthesis (these are complementary, not contradictory):**
- Niranjan defines **scope**: feed kernel files, not project infrastructure
- Erkap defines **reporting**: classify by complexity, report stratified results

Result: **Kernel-Centric Translation + Complexity Classification**

---

## 3. New Spec Field: `files.translation_targets`

```json
"files": {
  "prompt_payload": ["backprop_cuda.cu", "backprop_cuda_kernel.cu"],
  "support_files": ["backprop.h"],
  "translation_targets": ["backprop.c"]
}
```

**Semantics:**
- Optional array of strings
- Strict subset of target spec's `prompt_payload`
- If absent, pipeline falls back to full `prompt_payload` (backward compatible)
- Identifies the file(s) the LLM must produce — the "kernel computation files"
- Target infrastructure (Makefile, headers, utility files) stays untouched

**Schema additions (`schema/spec_schema.json`):**
```json
"translation_targets": {
  "type": "array",
  "items": {"type": "string"},
  "description": "Subset of prompt_payload identifying files the LLM must produce"
}
```

**New complexity field (`metadata.translation_complexity`):**
```json
"translation_complexity": {
  "type": "string",
  "enum": ["single_file", "multi_to_single", "single_to_multi", "multi_to_multi"]
}
```

---

## 4. Complexity Classification Taxonomy

| Class | Definition | Example |
|-------|-----------|---------|
| `single_file` | 1 source → 1 target | hotspot-cuda → hotspot-omp (1→1) |
| `multi_to_single` | N source → 1 target | bfs-cuda (3) → bfs-omp (1) |
| `single_to_multi` | 1 source → 2+ targets | hotspot-cuda → hotspot-opencl (.cl + .c) |
| `multi_to_multi` | N source → M targets | bptree-cuda (N) → bptree-opencl (.cl + host) |

Note: "source" and "target" counts refer to `translation_targets` file counts, not
full `prompt_payload` counts. A spec with 8 `prompt_payload` files but 1 `translation_targets` entry
is classified `single_file` (or `multi_to_single` if source has multiple kernel files).

---

## 5. Source-Verified Translation Targets — All Rodinia OMP Specs

All values below verified by reading actual Makefiles and `#pragma omp` locations.
**Use these values — do not guess.**

| Spec | prompt_payload count | translation_targets | Count | Complexity | Verification notes |
|------|:--------------------:|---------------------|:-----:|:----------:|-------------------|
| `backprop-omp` | 4 | `["backprop.c"]` | 1 | multi_to_single | OMP pragmas at lines 246, 316 of backprop.c. Despite its name, `backprop_kernel.c` is the orchestrator with NO pragmas |
| `bfs-omp` | 1 | `["bfs.cpp"]` | 1 | single_file | Already single-file |
| `bptree-omp` | 3 | `["kernel/kernel_cpu.c", "kernel/kernel_cpu_2.c"]` | 2 | multi_to_multi | Both have `#pragma omp parallel for`. `main.c` is driver/infrastructure |
| `cfd-omp` | 4 | `["euler3d_cpu.cpp"]` | 1 | multi_to_single | Self-contained. Other 3 files are separate binaries (double, pre variants) — SPEC BLOAT |
| `heartwall-omp` | 3 | `["main.c", "kernel.c", "define.c"]` | 3 | multi_to_multi | ALL 3: single compilation unit — `main.c` uses `#include "kernel.c"` and `#include "define.c"`. Inseparable |
| `hotspot-omp` | 1 | `["hotspot_openmp.cpp"]` | 1 | single_file | Already single-file |
| `hotspot3d-omp` | 1 | `["3D.c"]` | 1 | single_file | Already single-file |
| `kmeans-omp` | 8 | `["kmeans_openmp/kmeans_clustering.c"]` | 1 | multi_to_single | Only file with `#pragma omp parallel for`. 4 `kmeans_serial/` files are a SEPARATE binary — SPEC BLOAT |
| `lavamd-omp` | 2 | `["kernel/kernel_cpu.c"]` | 1 | multi_to_single | Only file with `#pragma omp parallel for` |
| `lud-omp` | 6 | `["omp/lud_omp.c"]` | 1 | multi_to_single | Only file with OMP pragmas. `base/`, `common/`, `tools/` are NOT part of OMP build — SPEC BLOAT |
| `mummergpu-omp` | 9 | N/A (KNOWN_FAIL) | — | — | Skip — excluded from all eval batches |
| `myocyte-omp` | 10 | (all 10 files) | 10 | multi_to_multi | Single compilation unit via textual `#include`. All inseparable. Interesting data point |
| `nn-omp` | 2 | `["nn_openmp.c"]` | 1 | multi_to_single | Self-contained. `hurricane_gen.c` is a separate data generator tool — SPEC BLOAT |
| `nw-omp` | 1 | `["needle.cpp"]` | 1 | single_file | Already single-file |
| `particlefilter-omp` | 1 | `["ex_particle_OPENMP_seq.c"]` | 1 | single_file | Already single-file |
| `pathfinder-omp` | 1 | `["pathfinder.cpp"]` | 1 | single_file | Already single-file |
| `srad-omp` | 1 | `["srad.cpp"]` | 1 | single_file | Already single-file |
| `streamcluster-omp` | 2 | `["streamcluster_omp.cpp"]` | 1 | multi_to_single | `streamcluster_original.cpp` is a separate serial binary (`sc_cpu`) — SPEC BLOAT |

---

## 6. Source-Verified Translation Targets — All Rodinia OpenCL Specs

OpenCL targets always require 2+ files: a `.cl` device kernel and a host `.cpp` driver.
This is inherent to the OpenCL programming model, not a project-structure issue (Erkap's point).

| Spec | prompt_payload count | translation_targets | Count | Infrastructure to keep untouched |
|------|:--------------------:|---------------------|:-----:|----------------------------------|
| `bfs-opencl` | 3 | `["Kernels.cl", "bfs.cpp"]` | 2 | `timer.cc` → move to support_files — SPEC BLOAT |
| `cfd-opencl` | 2 | `["Kernels.cl", "euler3d.cpp"]` | 2 | Already clean |
| `hotspot-opencl` | 3 | `["hotspot_kernel.cl", "hotspot.c"]` | 2 | `OpenCL_helper_library.c` → move to support_files — SPEC BLOAT |
| `hotspot3d-opencl` | 3 | `["hotspotKernel.cl", "3D.c"]` | 2 | `CL_helper.c` → move to support_files — SPEC BLOAT |
| `lud-opencl` | 6 | `["lud_kernel.cl", "ocl/lud.cpp"]` | 2 | `base/`, `tools/` NOT in OpenCL build — SPEC BLOAT |
| `nw-opencl` | 2 | `["nw.cl", "nw.c"]` | 2 | Already clean |
| `pathfinder-opencl` | 3 | `["kernels.cl", "main.cpp"]` | 2 | `OpenCL.cpp` → move to support_files — SPEC BLOAT |
| `srad-opencl` | 9 | all 9 files | 9 | `kernel/*.c` files are computation dispatch — genuinely needed |
| (remaining 12 OpenCL specs) | varies | `.cl` + host `.cpp` pattern | 2+ | Verify each during population |

For remaining 12 OpenCL specs, default assumption is:
- `.cl` kernel file → `translation_targets`
- Host `.cpp` driver → `translation_targets`
- Helper/utility `.c/.cc` files → move to `support_files` if not in the primary build

---

## 7. Spec Bloat Discovery

5 OMP specs and 4+ OpenCL specs include files from separate binaries never compiled
into the target executable. These inflate LLM prompts with irrelevant code.

**Files to move from `prompt_payload` → `support_files` during Session 1.5 population:**

| Spec | Files to move | Why they're not translation targets |
|------|---------------|-------------------------------------|
| `kmeans-omp` | 4 `kmeans_serial/` files | Separate binary `kmeans_serial`, not part of OMP parallel variant |
| `streamcluster-omp` | `streamcluster_original.cpp` | Separate serial binary `sc_cpu` |
| `lud-omp` | `base/lud.c`, `base/lud_base.c`, `tools/gen_input.c` | Three separate programs; OMP build only links `omp/lud_omp.c` |
| `cfd-omp` | 3 variant `.cpp` files | Three separate binaries (double, pre, pre_double) |
| `nn-omp` | `hurricane_gen.c` | Separate data generator tool; not linked into `nn_openmp` |
| `bfs-opencl` | `timer.cc` | Utility compiled separately; not in primary OpenCL kernel build |
| `hotspot-opencl` | `OpenCL_helper_library.c` | Helper; not the computation kernel |
| `hotspot3d-opencl` | `CL_helper.c` | Helper; not the computation kernel |
| `pathfinder-opencl` | `OpenCL.cpp` | Helper; not the computation kernel |
| `lud-opencl` | `base/lud.c`, `base/lud_base.c`, `tools/gen_input.c` | Same as lud-omp — same separate programs |

---

## 8. Prompt Design Changes

### Before (full-project translation — problematic):

```
## Target Files to Produce
- kmeans_openmp/cluster.c
- kmeans_openmp/getopt.c
- kmeans_openmp/kmeans.c
- kmeans_openmp/kmeans_clustering.c
- kmeans_serial/cluster.c
- kmeans_serial/getopt.c
- kmeans_serial/kmeans.c
- kmeans_serial/kmeans_clustering.c
```

### After (kernel-centric — correct):

```
## Target Files to Produce
- kmeans_openmp/kmeans_clustering.c

These files will replace existing files in the target project directory.
All other project files (Makefile, headers, utilities) remain unchanged.
Your translated code must integrate with the existing build infrastructure.

## Target Infrastructure Context (DO NOT MODIFY — for reference only)
These files exist in the target build directory and will NOT be modified.
Your translated code must be compatible with them.

### kmeans.h
[contents of kmeans.h from target directory]

### kmeans_openmp/kmeans.c
[contents of kmeans.c — existing infrastructure code the LLM must interface with]
```

**Key changes:**
1. Target file list reduced to kernel-only files (from `translation_targets`)
2. Explicit statement: "other project files remain unchanged"
3. New "Target Infrastructure Context" section: non-kernel target files included as
   read-only reference so LLM can match expected interfaces and function signatures
4. Infrastructure section includes: target headers (`.h/.hpp`), non-kernel source files,
   and the target Makefile (so LLM understands build structure)

---

## 9. Pipeline Code Changes (for Session 1.5 implementation)

### 9.1 `scripts/evaluation/llm_evaluate.py`

**`build_translation_prompt()` (~line 255):**
```python
# BEFORE:
target_filenames = target_spec["files"].get("prompt_payload", [])

# AFTER:
target_filenames = (
    target_spec["files"].get("translation_targets")
    or target_spec["files"].get("prompt_payload", [])
)
```

**`evaluate_translation()` (~line 715):** Same change — use `translation_targets` for
the list of files to back up, write, and restore.

**New "Target Infrastructure Context" section in prompt:**
- Identify non-translation-target files from target spec's `prompt_payload` + `support_files`
- Read their content and include as read-only context
- Section header: "## Target Infrastructure Context (DO NOT MODIFY — for reference only)"
- Section text: "These files exist in the target build directory and will NOT be modified.
  Your translated code must be compatible with these files."

**New result JSON field:**
```python
"translation_mode": "kernel_centric"  # or "full_project" (when translation_targets absent)
```

### 9.2 `harness/spec_loader.py`

In `resolve_paths()`: add `translation_targets` to the resolved files dict, resolving
paths relative to `source_path` the same way `prompt_payload` is resolved.

### 9.3 `schema/spec_schema.json`

Add to `files` object:
```json
"translation_targets": {
  "type": "array",
  "items": {"type": "string"},
  "description": "Subset of prompt_payload: files the LLM must produce (kernel files only)"
}
```

Add to `metadata` object:
```json
"translation_complexity": {
  "type": "string",
  "enum": ["single_file", "multi_to_single", "single_to_multi", "multi_to_multi"],
  "description": "Complexity class for stratified reporting"
}
```

### 9.4 `scripts/validate_schema.py`

Add validation: if `translation_targets` exists, every entry must be in `prompt_payload`.
This prevents specifying a target file that was moved to `support_files`.

---

## 10. Expected Pass Rate Impact

With kernel-centric translation, previously-structural BUILD_FAILs become tractable:

| Kernel | Before | After | Why |
|--------|--------|-------|-----|
| `kmeans` | BUILD_FAIL | Likely PASS | 8 files → 1 file. Semantic translation only. LLM no longer generating serial baseline |
| `backprop` | BUILD_FAIL | Likely PASS | 4 files → 1 file. No more glue code generation. OMP pragmas clearly in `backprop.c` |
| `streamcluster` | BUILD_FAIL | Likely PASS | 2 files → 1 file. No more `dist()` duplication across files |
| `srad` | BUILD_FAIL | Still likely FAIL | Already 1→1. True semantic error (arg type). Unchanged |

**Predicted cuda→omp pass rate improvement: 60% → 75-80%**
(Structural failures eliminated; true semantic failures remain)

---

## 11. Clean Slate Policy (User Decision 2026-03-22)

Previous full-project-mode results (Session 2 pilot, 10 kernels) will be **deleted and
re-run** with the kernel-centric pipeline. Reasons:
- Mixed v1/v2 data cannot be combined in a single paper narrative
- Paper presents a single evaluation paradigm
- Expected outcome: backprop, kmeans, streamcluster likely PASS → higher headline number

**Session 2 must delete all azure-gpt-4.1 cuda-to-omp results before re-running:**
```bash
rm results/evaluation/azure-gpt-4.1/rodinia-*-cuda-to-rodinia-*-omp.json
```

---

## 12. OpenCL Inherent Multi-File (Erkap's Point)

OpenCL cannot be normalized to a single file because the programming model requires:
- A **device kernel file** (`.cl`) compiled by the OpenCL runtime's JIT
- A **host driver file** (`.cpp`) managing device initialization, memory, and dispatch

These are structurally different: the `.cl` file uses OpenCL C (a subset of C99 with
vendor extensions), while the host `.cpp` uses C++11+ with the OpenCL host API.
An LLM that produces both files correctly is demonstrating a real translation skill
(mapping CUDA's unified programming model to OpenCL's host-device split).

For cuda-to-opencl evaluations, `translation_targets` always contains 2+ files.
All OpenCL targets are classified `single_to_multi` or `multi_to_multi`.

---

## 13. myocyte-omp Special Case

`myocyte-omp` has 10 files in `prompt_payload`, all 10 in `translation_targets`, because
the implementation uses textual `#include` to build a single compilation unit:

```c
// main.c
#include "kernel.c"
#include "kernel2.c"
// ... etc
```

These 10 files are inseparable (modifying one affects all). This is classified
`multi_to_multi` and is a genuinely interesting data point: does the LLM understand
textual-include-based single-unit compilation?

Expected result: BUILD_FAIL or complex PASS. Include in eval — informative either way.
