# Design Concern: Multi-File Source/Target Structural Mismatch in LLM Translation Evaluation

**Status:** RESOLVED — Kernel-Centric Translation + Complexity Classification (2026-03-22)
**Session:** 2026-03-19 Day 2 of SC26 sprint (concern raised); 2026-03-22 (resolved)
**Resolution:** See Section 10 below and `docs/design/kernel_centric_translation.md`
**Dashboard:** `visualizations/llm_evaluation.html` — "Design Concern" section

---

## 1. The Problem Statement

ParBench evaluates LLMs on parallel code translation (e.g., CUDA→OMP). The Phase 1
10-kernel evaluation revealed that **3 of 4 BUILD_FAILs are structural failures, not
semantic translation failures.**

The root cause: the CUDA and OMP implementations in Rodinia were written **independently**
by different developers. Their file structures reflect each developer's design choices —
they are NOT translations of each other. When we ask an LLM to translate CUDA→OMP and
produce the Rodinia OMP reference's exact file layout, we simultaneously test two
orthogonal skills:

1. **Translation quality** — does the LLM correctly map CUDA parallel patterns to OMP?
   ← *what we intend to measure*
2. **Code restructuring ability** — can the LLM replicate a specific file organization
   that the OMP developer chose? ← *a completely different skill, not in scope*

A BUILD_FAIL at skill 2 does not tell us anything about skill 1.

---

## 2. Phase 1 Evidence (10-kernel eval, azure-gpt-4.1, 2026-03-19)

**6/10 PASS (60%):** bfs, hotspot, lud, nn, nw, pathfinder
**4/10 BUILD_FAIL:** backprop, kmeans, srad, streamcluster

Result JSONs: `results/evaluation/azure-gpt-4.1/rodinia-{kernel}-cuda-to-rodinia-{kernel}-omp.json`
Batch report: `results/evaluation/batch_cuda-to-omp_20260319_162348.md`
Summary: `results/evaluation/eval_summary.md`

---

## 3. Failure Mode Analysis — All Four BUILD_FAILs

### 3.1 backprop — File Count Mismatch (Structural)

| | CUDA source | OMP target |
|--|--|--|
| Files | `backprop_cuda.cu`, `backprop_cuda_kernel.cu` (2 files) | `backprop.c`, `backprop_kernel.c`, `facetrain.c`, `imagenet.c` (4 files) |
| Structure | Flat | Flat |

**What happened:** LLM produced 1/4 files (`backprop_kernel.c` only). It treated the task
as "translate the kernel file" and left the 3 glue/wrapper files empty. Linker error:
`undefined reference to 'bpnn_train_cuda'`.

**Why this is structural:** `facetrain.c` and `imagenet.c` exist in BOTH the CUDA
`support_files` (pre-existing) and the OMP `prompt_payload` (translation targets). The OMP
developer refactored these into separate translation units; the CUDA developer kept them
as support scaffolding. The LLM has no signal that it must produce 4 files when only 2
were given as input.

**Attempt 2 outcome:** Identical extraction failure (1/4 files) — error feedback did not
trigger more file production.

**Result JSON key fields:**
```json
"files_expected": ["backprop.c", "backprop_kernel.c", "facetrain.c", "imagenet.c"],
"files_extracted": ["backprop_kernel.c"],
"build_error_snippet": "undefined reference to `bpnn_train_cuda'"
```

---

### 3.2 kmeans — Duplicate Basenames + Semantic Mismatch (Structural + Technical Bug)

| | CUDA source | OMP target |
|--|--|--|
| Files | `kmeans_cuda.cu`, `kmeans_cuda_kernel.cu` (2 files) | 8 files across 2 subdirs |
| Structure | Flat | `kmeans_openmp/` (4 files) + `kmeans_serial/` (4 files) |

**OMP target files:**
```
kmeans_openmp/cluster.c
kmeans_openmp/getopt.c
kmeans_openmp/kmeans.c
kmeans_openmp/kmeans_clustering.c
kmeans_serial/cluster.c      ← same basename as kmeans_openmp/cluster.c
kmeans_serial/getopt.c       ← same basename as kmeans_openmp/getopt.c
kmeans_serial/kmeans.c       ← same basename
kmeans_serial/kmeans_clustering.c
```

**What happened:** LLM produced 1/8 files (`kmeans_openmp/cluster.c` only). Build error:
```
cluster.c:84: error: conflicting types for 'cluster'; have 'int(int, int, float **, int, int, float, int *, float ***, float *, int, int)'
kmeans.h:47: previous declaration with type 'int(int, int, float**, int, float, float***)'
```
The LLM used the CUDA `cluster()` signature (7 params) instead of the OMP signature (6 params
declared in `kmeans.h`). Even if all 8 files were extracted, the semantic mismatch would
remain.

**Two separate bugs:**
1. **Technical bug in extractor:** `extract_code_blocks()` at line 527 of `llm_evaluate.py`
   uses basename fallback matching. When `cluster.c` appears in BOTH `kmeans_openmp/cluster.c`
   AND `kmeans_serial/cluster.c`, the fallback matches the first target only — silently
   dropping the second (and all remaining 6 files). This is fixable.
2. **Semantic/structural issue:** `kmeans_serial/` is a pre-existing serial baseline, NOT
   a translation artifact. The OMP developer added it as a reference comparison, independent
   of the CUDA source. Asking the LLM to produce it is outside translation scope.

**Attempt 2 outcome:** Identical error both times — no self-correction.

---

### 3.3 streamcluster — Semantic Coordination Failure (Structural, both files extracted correctly)

| | CUDA source | OMP target |
|--|--|--|
| Files | `streamcluster_cuda.cu`, `streamcluster_header.cu` (2 files) | `streamcluster_omp.cpp`, `streamcluster_original.cpp` (2 files) |
| Structure | Flat | Flat |

**What happened:** Both files were extracted (2/2) — extraction worked perfectly. Build error:
```
streamcluster_original.cpp:145: error: redefinition of 'float dist(Point, Point, int)'
streamcluster_omp.cpp:188: note: previously defined here
```
The LLM defined the `dist()` helper in BOTH output files. This causes a linker redefinition.

**Root cause:** `streamcluster_original.cpp` `#include`s `streamcluster_omp.cpp` (line 16).
When both files define `dist()`, the linker sees the definition twice. The LLM did not
understand that functions defined in the included file must not be re-defined in the
including file.

**Attempt 2 outcome:** Identical error — same `dist()` duplication. Error feedback did not
trigger fix.

**Note:** This IS a structural failure (multi-file coordination), but NOT a file count or
extraction problem. The fix requires better prompt guidance about `#include` relationships.

---

### 3.4 srad — Pure Semantic Translation Error (NOT structural)

| | CUDA source | OMP target |
|--|--|--|
| Files | `srad.cu`, `srad_kernel.cu` (2 files) | `srad.cpp` (1 file) |
| Structure | Flat | Flat |

**What happened:** Files extracted perfectly (1/1). Build error (Attempt 2):
```
srad.cpp:84:29: error: invalid conversion from 'char*' to 'int' [-fpermissive]
  84 | usage(argv[0], argv);  // LLM passed argv[0] (char*) where argc (int) expected
```
Attempt 1 happened to compile (permissive default), but failed at runtime:
```
Usage: ... <rows> <cols> <y1> <y2> <x1> <x2> <lamda> <no. of iter>
```
Attempt 2 "fixed" the code in a way that introduced the type error.

**Why this is semantic:** The file structure is correct (2→1, perfect extraction). The LLM
made a translation error passing the wrong argument type. This is a genuine translation
quality failure — the only one of the 4 BUILD_FAILs that is.

---

### 3.5 Why lud PASSES despite 6 files across 4 subdirectories (key comparison)

```
lud OMP target files:
  base/lud.c
  base/lud_base.c
  common/common.c
  omp/lud.c
  omp/lud_omp.c
  tools/gen_input.c
```

lud passes because:
1. All basenames are **unique** across subdirs (`lud.c` and `lud_omp.c` are different names)
2. The LLM correctly outputs full paths: `` ```cpp filename=base/lud.c ``
3. The Tier 1 exact-match extraction finds each file by full path
4. `fp.parent.mkdir(parents=True, exist_ok=True)` in `llm_evaluate.py:797` creates the subdirs

**Lesson:** Subdirs alone are not the problem. Duplicate basenames + semantic mismatch are.

---

## 4. Complexity Classification — All 21 Rodinia CUDA→OMP Kernel Pairs

Proposed 5-class taxonomy (computed from spec `files.prompt_payload` lists):

| Class | Definition | Kernels |
|-------|-----------|---------|
| `1:1_simple` | 1 CUDA file → 1 OMP file, flat | gaussian, hotspot, pathfinder |
| `N:N_flat` | Same count, flat, unique basenames | cfd, heartwall, hybridsort, streamcluster |
| `N:1_reduction` | Multiple CUDA → 1 OMP (kernel collapse) | bfs, hotspot3d, nw, particlefilter, srad |
| `N:M_reorganized` | Different count, flat, unique basenames | nn, backprop, huffman, myocyte |
| `structural_complex` | OMP has subdirs or duplicate basenames | bptree, kmeans, lavamd, lud, mummergpu |

**Classification algorithm:**
```python
has_subdirs = any('/' in f for f in omp_target_files)
basenames = [Path(f).name for f in omp_target_files]
has_dup_basenames = len(basenames) != len(set(basenames))

if has_subdirs or has_dup_basenames:     → structural_complex
elif cuda_count == 1 and omp_count == 1: → 1:1_simple
elif cuda_count == omp_count:            → N:N_flat
elif omp_count < cuda_count:             → N:1_reduction
else:                                    → N:M_reorganized
```

**Prediction:** Once implemented, expected PASS@1 by class:
- `1:1_simple`: ~100% (pure translation, no restructuring)
- `N:1_reduction`: ~80% (LLMs handle consolidation well, confirmed by bfs/nw/hotspot)
- `N:N_flat`: ~60% (streamcluster FAILS, others likely OK)
- `N:M_reorganized`: ~25% (backprop FAILS, nn PASSES — mixed)
- `structural_complex`: ~20% (lud PASSES by luck of unique basenames; kmeans/bptree likely FAIL)

---

## 5. Options and Tradeoffs

### Option A — Normalize all OMP targets to single-file

**What:** Create a `collapsed` variant of each multi-file OMP spec. The LLM produces a
single `translation_output.cpp` file. The spec's build command compiles that single file.
Correctness still verified by the same harness.

**Pros:**
- Tests pure translation quality — exactly what the paper claims to measure
- Eliminates all structural confusion
- Every kernel becomes a `1:1` task — clean apples-to-apples comparison across all kernels
- LLMs are well-practiced at producing single-file translations

**Cons:**
- Single-file translations don't reflect real HPC code organization
- Loses multi-file coordination as a test dimension (which IS a valid LLM capability test)
- Requires creating new build targets for each multi-file kernel (~10 specs to modify)
- Validates LLMs on a task that doesn't match what a user would actually ask them to do

**Implementation effort:** Medium — modify 10-15 OMP specs + build commands. No harness changes.

**When to choose A:** If the paper's core claim is "LLMs can/cannot translate parallel
algorithms across APIs" (semantic quality only). Gal's framing.

---

### Option B — Classify specs and report PASS@1 by complexity class

**What:** Tag each spec with `translation_complexity` class. Report pass rates separately
per class. The paper discusses results per class: "LLMs achieve 80% PASS on N:1_reduction
tasks but 20% on structural_complex tasks."

**Pros:**
- Most rigorous scientifically — addresses the *full* problem, not just the easy part
- Multi-file coordination IS a valid test of LLM capability — report it honestly
- The classification itself is a contribution: first systematic taxonomy of LLM translation
  task complexity
- No spec changes needed (classification lives in a separate CSV)
- Larger effective N (all 21 kernels evaluated, results stratified)

**Cons:**
- Smaller N per complexity class (~3-5 kernels each)
- Paper narrative requires explaining 5 categories — adds complexity to experimental setup
- Reviewer might say "why not just test the easy ones?"

**Implementation effort:** Low-Medium — new classification script, extend `analyze_eval.py`.
No spec or harness changes required.

**When to choose B:** If the paper wants to characterize *the full difficulty spectrum* of
parallel code translation as a contribution. Niranjan's framing ("create outline first,
see gaps").

---

### Option C — Fix extraction + improve prompt (technical fix only)

**What:** (1) Fix the `extract_code_blocks()` basename disambiguation bug for duplicate
basenames. (2) Add explicit prompt instructions for multi-file targets (subdir warnings,
function duplication warnings, `#include` relationship warnings).

**Pros:**
- Smallest change — keeps existing spec design
- The extraction bug IS a real bug independent of the design question — should be fixed regardless
- Prompt improvements may help streamcluster (dist() redefinition) and marginally help lud-style kernels
- Does not require team design decision to implement

**Cons:**
- Does NOT resolve the philosophical question about scope
- kmeans BUILD_FAIL will remain even after extraction fix (the semantic signature mismatch
  in `cluster()` persists — LLM uses CUDA signature, OMP header declares different one)
- backprop will remain BUILD_FAIL (4-file generation not triggered by prompt alone)
- Fixes the symptom for some cases but not the root cause

**Implementation effort:** Low — ~20 lines in `llm_evaluate.py`. Can implement immediately.

**When to choose C:** As a short-term fix alongside B. Always do C regardless of A vs B decision.

---

### Recommended Hybrid: B + C (+ spec fix for kmeans serial baseline)

1. **Immediately:** Implement Option C (extraction fix + prompt improvements) — this is
   a bug fix that should happen regardless of the design decision.
2. **After team discussion:** Implement Option B (complexity classification) — create the
   classification script and update `analyze_eval.py` to report by class.
3. **For kmeans specifically:** Consider a spec-level fix — move `kmeans_serial/` files
   from `prompt_payload` to `support_files`. The serial baseline is a pre-existing reference,
   not a translation target. This reduces kmeans from 8 files to 4, eliminates duplicate
   basenames, and makes it a cleaner `N:M_reorganized` case.
4. **Paper framing (Gal's input needed):** Decide whether headline number is "all kernels"
   or "stratified by complexity class." Both are defensible; Option B is stronger scientifically.

---

## 6. Concrete Implementation Plan (ready to execute after team decision)

### Step 1 — New script: `scripts/evaluation/classify_translation_complexity.py`

**Input:** All paired CUDA+OMP specs in `specs/`
**Output:** `results/evaluation/translation_complexity.csv`

```
Columns: kernel, cuda_spec, omp_spec, cuda_file_count, omp_file_count,
         has_subdir_structure, has_duplicate_basenames, complexity_class, notes
```

**CLI:**
```bash
python3 scripts/evaluation/classify_translation_complexity.py \
    --project-root /home/samyak/Desktop/parbench_sam
```

---

### Step 2 — Fix `extract_code_blocks()` in `llm_evaluate.py`

**File:** `scripts/evaluation/llm_evaluate.py`
**Location:** ~line 514 (inside `extract_code_blocks()`, before the Tier 1 loop)

**Current code (~line 527):**
```python
raw_fname == tgt or Path(raw_fname).name == Path(tgt).name
```

**Change to:**
```python
# Compute once before the loop (insert after line 514)
_target_basenames = [Path(t).name for t in target_filenames]
_has_dup_basenames = len(_target_basenames) != len(set(_target_basenames))

# In Tier 1 loop — line 527:
raw_fname == tgt or (not _has_dup_basenames and Path(raw_fname).name == Path(tgt).name)
```

**Effect:** When multiple targets share a basename (kmeans), extraction will only match via
exact full-path match, not basename fallback. Prevents silently mapping one code block to
multiple targets.

**Note:** This alone does NOT fix kmeans BUILD_FAIL — the semantic signature mismatch
in `cluster()` persists even with correct extraction.

---

### Step 3 — Enhance `build_translation_prompt()` in `llm_evaluate.py`

**File:** `scripts/evaluation/llm_evaluate.py`
**Location:** ~lines 254-293 (the user message section, "Target Files to Produce")

**Insert after the `for fname in target_filenames` loop (after line 292):**

```python
# Compute structural flags from target_filenames
_tgt_has_subdirs = any('/' in f for f in target_filenames)
_tgt_bnames = [Path(f).name for f in target_filenames]
_tgt_has_dup_bnames = len(_tgt_bnames) != len(set(_tgt_bnames))
_src_count = len([f for f in source_payload if not f.endswith('.h')])
_tgt_count = len(target_filenames)

# In the "Target Files to Produce" section:
if _src_count != _tgt_count:
    lines.append(
        f"NOTE: The target has {_tgt_count} files but the source has {_src_count}. "
        f"You MUST produce ALL {_tgt_count} files as complete source files."
    )

if _tgt_has_subdirs:
    lines.append(
        "IMPORTANT: Files in different subdirectories are separate compilation units. "
        "Do NOT define the same function in more than one file. Use a declaration in "
        "one file and a single definition in the other. If file A #includes file B, "
        "then any function defined in B must NOT be redefined in A."
    )

if _tgt_has_dup_bnames:
    lines.append(
        "IMPORTANT: Files with the same basename in different subdirectories contain "
        "DIFFERENT code for different variants. Use the FULL path in your filename "
        "annotation: ```cpp filename=kmeans_openmp/cluster.c (not just cluster.c)."
    )
```

---

### Step 4 — Extend `analyze_eval.py` to report by complexity class

**File:** `scripts/evaluation/analyze_eval.py`
**Changes needed:**
- Add `_load_complexity_map(project_root)` function that reads `translation_complexity.csv`
- Enrich each result record with `translation_complexity` field
- Add new section to markdown output: "Pass Rate by Translation Complexity Class" table
- Add `translation_complexity` as a group key in `eval_summary.json`

---

### Step 5 — Spec fix for kmeans (separate decision — needs Gal input)

**Option:** Move `kmeans_serial/` files from `prompt_payload` to `support_files` in
`specs/rodinia-kmeans-omp.json`. The serial baseline is a pre-existing reference
implementation that the OMP parallel version is benchmarked against. It does not need
to be translated from CUDA.

**Effect:** kmeans becomes `N:M_reorganized` (2→4 files, flat, unique basenames per dir).
The `cluster()` signature mismatch may still exist, but at least the task becomes
well-defined.

**Files to change:** `specs/rodinia-kmeans-omp.json` — move 4 `kmeans_serial/` entries
from `files.prompt_payload` to `files.support_files`.

---

### Step 6 — Re-run failing kernels after fixes

```bash
source env_parbench/bin/activate
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --kernels backprop kmeans streamcluster srad \
    --direction cuda-to-omp \
    --models azure-gpt-4.1 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --no-resume -v
```

**Expected outcomes after prompt fix:**
- streamcluster: likely PASS (prompt now warns about `dist()` duplication + `#include` relationships)
- srad: may PASS (better prompt guidance about function parameter types)
- kmeans: likely still BUILD_FAIL (semantic signature mismatch persists)
- backprop: likely still BUILD_FAIL (4-file generation from 2-file input is fundamentally hard)

---

## 7. Open Questions for Team (awaiting Discord response)

1. **Gal:** Is multi-file coordination testing in scope for ParBench's headline metric?
   - If yes → Option B (classify + report by class)
   - If no → Option A (normalize to single-file) or B (report separately)

2. **Erel:** The `kmeans_serial/` issue — should the serial baseline be in `support_files`
   rather than `prompt_payload`? You wrote this spec. Your call on the intent.

3. **Both:** For the SC26 paper's headline: do we report "X% of LLM translations pass"
   (all kernels, single number) or "X% on simple kernels, Y% on complex" (by class)?
   The stratified version is stronger scientifically but requires more explanation.

4. **Gal:** The `cluster()` function signature in kmeans OMP — the LLM uses the CUDA
   7-param version but `kmeans.h` declares a 6-param version. Should the kmeans OMP spec
   include `kmeans.h` in `support_files` so the LLM sees the expected interface?

---

## 8. Key File Locations

| Artifact | Path |
|----------|------|
| Phase 1 batch results | `results/evaluation/batch_cuda-to-omp_20260319_162348.md` |
| Eval summary | `results/evaluation/eval_summary.md` |
| Individual result JSONs | `results/evaluation/azure-gpt-4.1/rodinia-{kernel}-cuda-to-rodinia-{kernel}-omp.json` |
| File extraction code | `scripts/evaluation/llm_evaluate.py` lines 503-560 (`extract_code_blocks`) |
| Prompt building code | `scripts/evaluation/llm_evaluate.py` lines 254-310 (`build_translation_prompt`) |
| kmeans OMP spec | `specs/rodinia-kmeans-omp.json` |
| backprop OMP spec | `specs/rodinia-backprop-omp.json` |
| streamcluster CUDA spec | `specs/rodinia-streamcluster-cuda.json` |
| LLM evaluation dashboard | `visualizations/llm_evaluation.html` → Design Concern section |
| Sprint dashboard | `visualizations/sprint_dashboard.html` → task M11 |
| Known issues | `.claude/rules/known-issues.md` → "Multi-file structural mismatch" |

---

## 9. Instructions for New Session (Opus 4.6 Extended, Plan Mode)

When starting a new session to continue this work:

**RESOLVED 2026-03-22 — These instructions are superseded by the team decision in Section 10.**
**For implementation:** Use SESSION 1.5 in `docs/session_prompts_sc26.md` instead.
**For context:** Read Section 10 first, then `docs/design/kernel_centric_translation.md`.

*Original pre-resolution instructions (historical reference only):*
1. Read this file first to get full context
2. Read the result JSONs for backprop and kmeans to ground the analysis
3. Read `llm_evaluate.py` lines 503-560 (extraction) and 254-310 (prompt building)
4. ~~Check Discord for Gal/Erel responses~~ — DONE (responses in Section 10)
5. ~~Enter plan mode and plan the hybrid solution~~ — DONE (kernel-centric approach decided)
6. ~~Do NOT modify spec files~~ — spec population is now SESSION 1.5 Step 7

**Commands to start fresh eval after fixes:**
```bash
source env_parbench/bin/activate

# Re-run failing kernels with improved prompt
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --kernels backprop kmeans streamcluster srad \
    --direction cuda-to-omp \
    --models azure-gpt-4.1 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --no-resume -v

# Classify all 21 kernels (after creating the script)
python3 scripts/evaluation/classify_translation_complexity.py \
    --project-root /home/samyak/Desktop/parbench_sam

# Regenerate analysis with complexity stratification
python3 scripts/evaluation/analyze_eval.py \
    --project-root /home/samyak/Desktop/parbench_sam \
    --write-dashboard --show-gaps
```

---

## 10. Team Decision (2026-03-22) — RESOLVED

**Status: RESOLVED — Kernel-Centric Translation + Complexity Classification**

### Team Feedback (Discord, 2026-03-21)

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

### Synthesis

These opinions are **complementary, not contradictory**:
- Niranjan defines **scope**: feed kernel files, not project infrastructure
- Erkap defines **reporting**: classify by complexity, report stratified results per Option B

### Resolved Design: Kernel-Centric Translation

1. Feed source kernel file(s) to the LLM (all computational source files, not infrastructure)
2. LLM produces only target kernel file(s), dropped into the target directory
3. Target infrastructure stays untouched (Makefile, headers, utilities, serial baselines)
4. OpenCL targets inherently need 2+ files (host `.cpp` + `.cl` kernel) — this is allowed
5. Each translation pair classified by complexity for stratified paper reporting (Option B)
6. No project-level restructuring — "next level of challenge" (Niranjan)

### Implementation

New spec field: `files.translation_targets` — optional subset of `prompt_payload` identifying
the file(s) the LLM must produce. Pipeline uses this for target file list in prompt and for
file backup/restore scope.

See `docs/design/kernel_centric_translation.md` for full architecture including source-verified
`translation_targets` values for all 60 Rodinia specs, prompt design, and pipeline code changes.

Implementation session: **SESSION 1.5** in `docs/session_prompts_sc26.md`.

### Expected Impact on Phase 1 BUILD_FAILs

| Kernel | Root cause (from §3) | With kernel-centric translation |
|--------|---------------------|--------------------------------|
| backprop | 4-file generation from 2-file input | 1 target file (`backprop.c`) — Likely PASS |
| kmeans | 8 files across 2 subdirs + serial baseline | 1 target file (`kmeans_openmp/kmeans_clustering.c`) — Likely PASS |
| streamcluster | `dist()` duplication across 2 files | 1 target file (`streamcluster_omp.cpp`) — Likely PASS |
| srad | True semantic error (arg type mismatch) | Unchanged (1→1 already) — Still likely FAIL |

**Predicted pass rate improvement: 60% → 75-80%** (structural failures eliminated)
