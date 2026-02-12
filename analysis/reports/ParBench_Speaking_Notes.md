# ParBench Presentation — Speaking Notes

**For:** Research team progress meeting
**Presenter:** Sam Jhaveri
**Date:** February 2026
**Objective:** Communicate project progress and frame how each phase maps to sections of the paper we will write.

---

## Slide 1 — Title Slide

**"ParBench: A Meta-Benchmark for LLM-Based Parallel Code Translation"**

Good to see everyone. Today I'm going to walk you through where ParBench stands. The short version is: we have a working end-to-end pipeline — schema, harness, validation — proven on real hardware with 5 pilot kernels. I'll go phase by phase and flag how each piece feeds into the paper.

**Paper connection:** This title and framing is what we'd use for the paper itself. The term "meta-benchmark" is deliberate — we don't create new benchmarks, we curate and wrap existing ones. That distinction is central to our contribution claim.

---

## Slide 2 — The Problem

**Three challenges motivating the project:**

1. **Fragmented benchmarks** — HeCBench, Rodinia, RAJAPerf, BabelStream all exist independently. Nobody has connected them into a single evaluation corpus for LLM translation. That fragmentation is our opening in the paper's introduction.

2. **No automation** — If you want to test whether GPT-4 or Claude can translate a CUDA kernel to SYCL, right now you do it manually: copy code, paste into a chat, take the output, write a Makefile, build, run, check. We automate all of that.

3. **No ground truth** — Without a systematic baseline (what does the original produce on known inputs?), you can't programmatically verify whether a translation is correct. Our spec files capture that baseline.

**Paper connection:** These three points structure the "Motivation" section. We can cite prior work on LLM code generation (e.g., HumanEval, MBPP) and argue that parallel code translation has no equivalent benchmark infrastructure.

---

## Slide 3 — Our Approach: ParBench

**Walk through the 5-phase pipeline shown on slide:**

Phase 1 is the survey, Phase 2 is kernel-level analysis, Phase 3 is schema design, Phase 4 is the harness, Phase 5 is end-to-end testing. These phases map roughly to paper sections: survey becomes "Related Work" + "Benchmark Corpus," schema becomes "System Design," harness becomes "Implementation," and E2E testing becomes "Evaluation."

**Key insight box:** This is the single most important number to internalize — HeCBench alone has 506 kernels with CUDA/HIP/SYCL/OpenMP variants. That's thousands of translation pairs from just one repository. This is the core of our contribution: scale.

**Reference files:**
- Project overview: `parbench_sam/README.md`
- Full structure visible in the repo layout

---

## Slide 4 — Phase 1-2 Section Divider

Quick transition. Phases 1 and 2 are survey and analysis. These are largely complete and will form the "Benchmark Corpus" section of the paper. I'll move through these quickly since the team has seen earlier versions of this data.

---

## Slide 5 — Benchmark Survey: 35 Repositories

**Key numbers:** 35 repos surveyed, 30 classified as Tier A (high quality, usable for our purposes), 5 as Tier B. Over 2,700 kernel-API implementations total.

The type breakdown matters for the paper — we need to explain why we selected these particular suites. Suites (13) give us volume, miniapps (12) give us realistic application kernels, proxy apps give us DOE-scale codes.

**The bar chart** (`api_coverage_bar_v5.png`) shows API coverage per benchmark. CUDA dominates, which is expected, but the important finding is that OpenMP and SYCL coverage is much broader than people assume.

**Reference files:**
- Full inventory: `parbench_sam/benchmark_inventory_complete_v3.md` — this is the authoritative list of all 35 repos with types, tiers, API counts, build systems
- API matrix: `benchmarks_api_matrix_v6_with_links.xlsx - Benchmarks_API_Matrix.csv`

**Paper connection:** This becomes a table in the paper (probably Table 1) — the master benchmark inventory. We may want to trim it to the top 10-15 most relevant repos for the paper and put the full list in an appendix.

---

## Slide 6 — Kernel-Level Analysis: 20-60x More Pairs

**This is the key finding from Phase 2.** Repository-level counts are misleading. When you say "21 repos have both CUDA and OpenMP," that sounds modest. But when you count at the kernel level, it's 472 individual translation pairs. The multiplier is 22x to 68x depending on the API pair.

Walk the team through the table — CUDA↔HIP is 633 kernels (mostly from HeCBench's 504), CUDA↔SYCL is 616, CUDA↔OpenMP is 472. These are real, compilable, runnable kernel implementations, not synthetic tasks.

**The heatmap** (`api_cooccurrence_heatmap_v5.png`) visualizes co-occurrence at the repo level. The kernel-level version is even more dramatic.

**Reference files:**
- Analysis document: `parbench_sam/kernel_level_analysis.md` — contains all the pair counts and per-benchmark breakdowns
- Raw data: `parbench_sam/kernel_api_inventory.csv`

**Paper connection:** This analysis is a contribution in itself. No prior work (that I'm aware of) has done a kernel-level census of translation pair availability across parallel benchmark suites. This goes in the "Benchmark Corpus" section and produces Figure 1 or 2 in the paper.

---

## Slide 7 — Survey Visualizations

Three visualizations, all generated from our survey data:

1. **API co-occurrence network** (`api_cooccurrence_network_color_v7.png`) — edge thickness encodes how many benchmarks support both APIs. CUDA is the hub.

2. **Bipartite graph** (`benchmark_api_bipartite_color_readable_v7.png`) — benchmarks on one side, APIs on the other. Shows which benchmarks cover which APIs. HeCBench is visually dominant.

3. **API count histogram** (`benchmark_api_count_hist_v5.png`) — distribution of how many APIs each benchmark supports.

**Takeaway box:** 656 unique kernels, 2,717 implementations. These numbers anchor our contribution claims.

**Paper connection:** We pick 2-3 of these visualizations for the paper figures. The network graph and the heatmap are probably the strongest. The bipartite graph might be better suited for a supplementary appendix since it's dense.

---

## Slide 8 — Phase 3 Section Divider

Transitioning to schema design. This is the core technical contribution and will be the longest section of the paper. Everything after this — the harness, the testing — is built on top of the schema.

---

## Slide 9 — Two-Level Metadata Architecture

**This is the architectural heart of ParBench.** Two levels:

**Level 1** is `manifest.jsonl` — one JSON line per kernel-variant. It's lightweight, grep-able, designed for discovery. You can find all CUDA kernels with a single grep. The `kernel_name` field is the pairing key: all entries with the same `kernel_name` are equivalent implementations across different APIs, which means they form translation pairs.

**Level 2** is the individual spec files (`specs/*.json`) — comprehensive execution specifications. Each one drives the full build → run → verify pipeline for a single kernel-variant.

The code block at the bottom shows a real manifest entry for the `nn` kernel in CUDA, pointing to `specs/hecbench-nn-cuda.json`.

**Reference files:**
- Schema design document: `JSON_Schema_for_ParBench.md` — contains the full rationale, the two-level diagram, and the reconciliation with our teammate's format
- Manifest file: `parbench_sam/manifest.jsonl`
- Example spec: `parbench_sam/specs/hecbench-nn-cuda.json`

**Paper connection:** This architecture gets its own subsection — "Two-Level Metadata System." We present the design, justify the split (Level 1 for enumeration/pairing, Level 2 for execution), and show how it enables both human inspection and automated tooling. The ASCII diagram from `JSON_Schema_for_ParBench.md` becomes a proper figure.

---

## Slide 10 — Level-2 Spec Structure

**Walk through the 11 sections** shown in the colored bars on the left:

- `identity` through `metadata` — each has a specific role. The most important for the paper are `files` (security model), `build` (reproducibility), `verification` (correctness), and `baseline_results` (ground truth).

The code snippet on the right is an excerpt from `hecbench-nn-cuda.json` — it shows the actual JSON structure. Note how compact it is: the identity block, the files block with prompt_payload listing the source files, and the verification block specifying the strategy.

**Reference files:**
- Full schema definition: `parbench_sam/schema/spec_schema.json` — this is the JSON Schema draft-07 file that validates every spec
- Template: `parbench_sam/templates/spec_template.json`

**Paper connection:** We include a condensed version of this spec (probably a listing or figure) in the paper. We don't show all 200+ lines — just enough to illustrate the structure. The schema itself can go in a repository release.

---

## Slide 11 — File Security Model

**This is critical for the paper's credibility.** The file security model controls what the LLM sees during evaluation:

- **`prompt_payload`** — these are the ONLY files sent to the LLM for translation. For `nn-cuda`, that's `nearestNeighbor.cu` and `nearestNeighbor.h`.
- **`support_files`** — Makefiles, CMakeLists.txt, utility headers. Needed for compilation but NOT shown to the LLM. This prevents the model from "cheating" by learning from build system hints.
- **`verification_only`** — reference implementations like `reference.cu`. NEVER shown to the LLM. These are what we compare against for correctness.

The rule at the bottom is enforced by our schema validator: no file can appear in both `prompt_payload` and `verification_only`. This is a hard constraint, not a convention.

**Reference files:**
- File classifications for all 5 pilot kernels: `parbench_sam/reports/pilot_report.md` — has the complete breakdown showing which files go in which category for every kernel × API combination
- Validator: `parbench_sam/scripts/validate_schema.py`

**Paper connection:** This becomes a dedicated subsection — "Evaluation Integrity Model" or similar. It's important because it addresses a methodological concern reviewers will have: "How do you prevent data leakage to the LLM?" The answer is this three-tier file classification, enforced by schema validation. We should cite analogous concerns in ML benchmarking (train/test contamination) and position this as the code translation equivalent.

---

## Slide 12 — Schema Validation System

**Two types of validation working together:**

Left card — JSON Schema (draft-07) handles structural validation: field types, required fields, enum constraints on `parallel_api`, nested object structure for all 11 sections.

Right card — cross-cutting checks go beyond what JSON Schema can express: `unique_id` must match the filename (`hecbench-nn-cuda` in `hecbench-nn-cuda.json`), `implementation.api` must match `identity.parallel_api`, all files listed in `files.*` must exist on disk, and the prompt_payload ∩ verification_only = ∅ rule.

**Translation pair enumeration:** For the pilot, 5 kernels × 4 APIs = 20 specs → 60 directed translation pairs (e.g., CUDA→OMP is distinct from OMP→CUDA). At full scale with 506 kernels, this becomes thousands.

**Reference files:**
- Schema file: `parbench_sam/schema/spec_schema.json`
- Validator script: `parbench_sam/scripts/validate_schema.py`

**Paper connection:** The validation system goes in the "Implementation" section. We should list the checks in a table (Table N: "Validation checks performed by `validate_schema.py`"). The zero-error final state (slide 23) becomes a result that demonstrates the system works.

---

## Slide 13 — Phase 4 Section Divider

Moving to the harness. This is the tool implementation — 1,366 lines of Python that reads spec files and automates everything.

---

## Slide 14 — Harness Architecture Overview

**Six modules in a pipeline:**

1. **CLI** (326 lines, `harness/cli.py`) — entry point with 6 commands: `build`, `run`, `verify`, `prompt`, `info`, `pairs`
2. **spec_loader** (197 lines, `harness/spec_loader.py`) — loads JSON specs, resolves file paths using `config/paths.json`
3. **builder** (262 lines, `harness/builder.py`) — performs variable substitution (e.g., `${GPU_ARCH}` → `sm_89`), runs clean/configure/build
4. **runner** (173 lines, `harness/runner.py`) — executes binaries with configurable timeout, captures stdout/stderr
5. **verifier** (194 lines, `harness/verifier.py`) — applies verification strategies (`exit_code`, `stdout_pattern`), extracts metrics
6. **reporter** (138 lines, `harness/reporter.py`) — formatted terminal output and JSON export

Plus `models.py` (69 lines) for the `Status` enum (PASS/FAIL/ERROR/TIMEOUT/SKIP) and result dataclasses.

**Reference files:**
- All harness source: `parbench_sam/harness/` directory
- CLI entry point: `parbench_sam/harness/cli.py`
- Verifier: `parbench_sam/harness/verifier.py`

**Paper connection:** This becomes the "Harness Implementation" subsection. We present the architecture diagram (this slide becomes a figure), describe each module briefly, and emphasize that the entire pipeline is driven by the JSON specs — no hardcoded behavior. This is important because it means scaling to 506 kernels requires zero code changes, only new spec files.

---

## Slide 15 — CLI Workflow: End-to-End Verify

**Live demo of the pipeline in action.** The command shown is real:

```
$ python -m harness.cli verify specs/hecbench-nn-cuda.json -v
```

This triggers BUILD → RUN → VERIFY → METRICS in sequence. For `nn-cuda`: build takes 1.5s, run takes 0.09s, verification passes via `exit_code` strategy, and metric extraction pulls `kernel_time = 57.31 μs` from stdout.

**The `prompt` command** is equally important: it extracts only the `prompt_payload` files for a given spec and outputs them in a format suitable for feeding to an LLM. This enforces the file security model programmatically.

**Paper connection:** We include a workflow example like this in the paper — probably as a listing showing the command and output. It demonstrates the system is operational, not just designed. The `prompt` command is especially important to describe because it's the bridge between our infrastructure and the actual LLM evaluation experiments.

---

## Slide 16 — Verification Strategies

**Two strategies currently implemented:**

- **`exit_code`** — checks if the process returned the expected exit code (usually 0). Used when the benchmark performs its own internal correctness check and signals success via exit code. Examples: `nn-cuda`, `nn-omp`, `binomial-cuda`.

- **`stdout_pattern`** — regex match on stdout. Used when the benchmark prints "PASS"/"FAIL" or similar to stdout. Examples: `scan`, `particle-diffusion`, `radixsort`.

**Metric extraction** is a separate, optional step applied after verification. It uses stdout regex patterns defined in the spec's `performance` section to pull timing data (kernel execution time, sort time, etc.) and populate `baseline_results`.

**Reference files:**
- Verifier implementation: `parbench_sam/harness/verifier.py` — 194 lines, contains both strategy implementations
- Example spec with stdout_pattern: `parbench_sam/specs/hecbench-scan-omp.json`

**Paper connection:** Verification strategies get a table in the paper. As we scale up, we'll likely add more strategies (e.g., `numeric_comparison` against a reference output file, `file_diff`). The extensible design of the verifier is worth calling out.

---

## Slide 17 — Phase 5 Section Divider

Phase 5 is the payoff — everything we built in phases 1-4 gets exercised on real hardware. This is where the paper's "Evaluation" section draws from.

---

## Slide 18 — Test Platform & Pilot Scope

**Hardware:** RTX 4070 (Ada Lovelace, sm_89, 12GB) + Ryzen 9 7900X (12-core, 24-thread). Ubuntu 22.04. This is documented in `parbench_sam/reports/environment_check.txt`.

**API availability:** CUDA 12.3 and OpenMP (via GCC 12.4) are available. HIP and SYCL are not installed yet — those are next steps.

**Pilot scope:** 5 kernels from HeCBench (`nn`, `scan`, `particle-diffusion`, `binomial`, `radixsort`), each with 4 API variants (CUDA, HIP, SYCL, OMP) = 20 specs = 60 translation pairs. Only the CUDA and OMP variants are testable on this platform, giving us 10 buildable specs.

**Paper connection:** The hardware description goes in the "Experimental Setup" subsection. We need to be explicit about what we could and couldn't test and why. For the paper, ideally we'd have HIP/SYCL results too — that's a priority before submission.

---

## Slide 19 — Build Results: 10/10 Success

**All 10 executables built successfully.** 5 CUDA kernels built with `make ARCH=sm_89`, 5 OpenMP kernels built with `make -f Makefile.aomp CC=g++ DEVICE=cpu`.

This is a clean pass — no build failures, no manual intervention needed. The spec files contained all the information the harness needed to build each kernel correctly.

**Paper connection:** Build success is a necessary precondition, not a headline result. We mention it briefly in the evaluation. The fact that the specs were sufficient to drive automated builds without manual fixes is the real point — it validates the schema design.

---

## Slide 20 — Correctness Verification Matrix

**This is the most important results slide.** CUDA: 5/5 PASS. OpenMP: 2/5 PASS (nn, scan with workaround), 3/5 FAIL.

Walk through each row:
- `nn`: PASS on both APIs. Clean.
- `scan`: PASS on CUDA. OMP passes only with `OMP_NUM_THREADS=1024` workaround (documented in the spec's `environment_variables`).
- `particle-diffusion`: PASS on CUDA, FAIL on OMP (exit 0 but wrong output).
- `binomial`: PASS on CUDA, HANG on OMP (>10 minutes, killed by timeout).
- `radixsort`: PASS on CUDA, SEGFAULT on OMP.

**Critical framing:** All OMP failures are defects in HeCBench source code, not in our build configuration or harness. They represent real GPU→CPU portability problems — the kind of problems that LLMs would need to recognize and fix during translation.

**Paper connection:** This matrix becomes Table N in the paper. The failures are arguably more interesting than the passes for the paper narrative, because they demonstrate that correct parallel translation is non-trivial. We should frame them as "portability challenges that an LLM translator must handle."

---

## Slide 21 — OpenMP Failure Root-Cause Analysis

**Each failure is categorized and explained. This slide is critical for the paper.**

1. **scan-omp (RESOLVED)** — Blelloch scan algorithm requires `thread_limit(N/2)`. CPU OpenMP caps team size at `nproc` (24 on our machine). Only 48 elements get processed. Workaround: set `OMP_NUM_THREADS=1024`. Category: thread model mismatch.

2. **particle-diffusion-omp (FAIL)** — `#pragma omp target data map(alloc:)` is a no-op when running on CPU fallback. Pointers alias host memory instead of allocating separate device memory. The kernel corrupts its own input, then the sequential reference function produces wrong results. Category: `benchmark_source_gpu_memory_model`.

3. **radixsort-omp (SEGFAULT)** — Warp-synchronous scan functions (`scanwarp`, `warpScanInclusive`) assume 32-thread lockstep execution. On CPU with ≥2 threads, this becomes a data race → out-of-bounds writes → SEGFAULT. Category: `benchmark_source_gpu_assumption`.

4. **binomial-omp (HANG)** — 1000 iterations × 1024 options × 2048 timesteps. Each step is a sequential binary tree traversal. Without GPU parallelism, total work is ~2 billion operations per option, running serially. Category: `benchmark_source_timeout`.

**Reference files:**
- Full root-cause analysis: `parbench_sam/reports/phase5_checkpoint.md`, "OMP Failure Analysis" section
- Failed spec with documented reason: `parbench_sam/specs/hecbench-radixsort-omp.json` — contains `fail_reason` and `fail_category` fields

**Paper connection:** This root-cause analysis is a contribution. We should dedicate a subsection to "Portability Defect Taxonomy" or similar. The four failure categories (thread model mismatch, GPU memory model assumption, lockstep execution assumption, computational complexity explosion) could generalize across more kernels as we scale up. If we find these same categories recurring across 506 kernels, that's a finding in itself. An LLM that can correctly translate despite these issues would be demonstrably handling non-trivial portability challenges.

---

## Slide 22 — Baseline Performance (3-Run Averages)

**Performance baselines for 7 passing specs** (5 CUDA + 2 OMP):

Highlight two interesting comparisons:
- **scan:** CUDA kernel time 33μs vs OpenMP 51,815μs — a 1,549x difference. This makes sense: Blelloch scan is inherently parallel and maps perfectly to GPU execution. On CPU, it's doing the same algorithmic work with far less parallelism.
- **nn:** OpenMP wall time (0.008s) is actually faster than CUDA (0.075s). This is because nn uses small input data, and the GPU launch overhead dominates. The kernel itself is fast on both platforms, but CUDA pays a fixed cost for memory transfer and kernel launch.

These baselines are stored in each spec's `baseline_results` section — they were populated by the harness after 3 measurement runs.

**Reference files:**
- Baseline data: `parbench_sam/reports/phase5_checkpoint.md`, "Baseline Performance" section
- Individual specs contain their own baseline_results (e.g., `hecbench-nn-cuda.json`)

**Paper connection:** Performance baselines serve two purposes in the paper: (1) they validate that our measurement infrastructure works, and (2) they provide ground truth for evaluating LLM-translated code. If an LLM translates `scan-cuda` to `scan-omp`, we can compare the translated version's output against these baselines. Performance degradation beyond expected cross-API differences would indicate a translation problem.

---

## Slide 23 — Schema Validation: Final State

**Clean bill of health:** 0 errors, 10 warnings (all just orphan build artifacts like `.o` files and compiled `main` executables in source directories — not actual problems), all 20 specs valid.

The table lists all 8 validation checks that pass — from JSON Schema conformance through cross-kernel pairing. This validates that our tooling works correctly end-to-end.

**Reference files:**
- Validation output: `parbench_sam/reports/pilot_report.md`, "Validation Status" section — shows the complete validator output with all 20 specs passing and the 10 warnings listed

**Paper connection:** We mention this briefly in the evaluation section — "all 20 pilot specs pass structural and semantic validation with zero errors." It's a necessary credibility point. The validator script itself (`validate_schema.py`) could be released as part of the open-source tooling.

---

## Slide 24 — Translation Pair Coverage

**Summary statistics for the pilot:**

- 20 specs created (5 kernels × 4 APIs)
- 60 translation pairs (each kernel has C(4,2) = 6 undirected pairs, but we count directed: 12 per kernel)
- 10 buildable on current platform (CUDA + OMP only)
- 7 passing end-to-end
- 3 documented failures (with root causes)
- 10 skipped (all HIP + SYCL, no toolchains)

The breakdown table gives the complete picture. Note that even with only 5 kernels, we already have a rich dataset: 7 passing baselines, 3 characterized failures, and a clear path to scaling.

**Paper connection:** This summary becomes part of the "Experimental Results" section. The 60-pair count for just 5 kernels demonstrates the scalability argument: at full HeCBench scale (506 kernels), we'd have roughly 6,000 translation pairs.

---

## Slide 25 — Phase-by-Phase Summary

**10/10 stages of Phase 5 complete.** Walk through briefly:

Stages 1-2 (environment, paths) were prerequisites. Stage 3 found and fixed a bug in the validator (`startswith("⚠")` → proper warning detection). Stage 4 was a dry run confirming all harness commands work. Stages 5-6 were builds. Stage 7 was the actual run + verify. Stage 8 collected baselines (3 runs each). Stage 9 was a final re-validation. Stage 10 is the checkpoint document.

**Reference files:**
- Complete stage-by-stage report: `parbench_sam/reports/phase5_checkpoint.md` — this is the authoritative document for Phase 5

**Paper connection:** We don't put this table in the paper directly, but it demonstrates methodological rigor. The fact that we ran a structured 10-stage test protocol (not ad hoc testing) is worth mentioning in the methodology section.

---

## Slide 26 — What This Proves

**Five validated claims from the pilot:**

1. **Schema is sufficient** — the two-level system captured everything needed for automated evaluation.
2. **Harness works end-to-end** — 1,366 lines of Python, tested on real hardware.
3. **Security model is enforceable** — the `prompt` command correctly extracts only `prompt_payload` files.
4. **Failures are informative** — GPU→CPU portability defects are real challenges for LLMs.
5. **Scale is achievable** — 5 kernels prove the pattern; 501 more await onboarding.

**Paper connection:** These map to the paper's "Contributions" list (usually in the introduction). We should claim: (1) a curated corpus of N translation pairs from M benchmark suites, (2) a machine-readable specification format with integrity guarantees, (3) an automated evaluation harness, and (4) a pilot evaluation demonstrating the system works. By submission time, we should also have (5) LLM translation results.

---

## Slide 27 — Next Steps

**Two HIGH priorities:**

1. **Scale up** — onboard full HeCBench (506 kernels) + RAJAPerf (106 kernels). This is mostly a spec-writing task, potentially scriptable. The schema and harness don't change.

2. **Add toolchains** — install HIP (ROCm) and SYCL (Intel oneAPI or AdaptiveCpp) on the test machine. This unlocks all 4 API paths and fills in the "skip" cells in our matrices.

**Two NEXT priorities:**

3. **LLM evaluation** — the actual experiments. Feed `prompt_payload` to models (GPT-4, Claude, Code Llama, etc.), capture translated code, build it using our harness, verify correctness, measure performance.

4. **Metrics & analysis** — compare translation success rates across LLMs, API pairs, and kernel complexity. This is the paper's results section.

**For the team:** The timeline question is — do we submit with pilot-scale results (5 kernels, 2 APIs) or wait for full-scale (500+ kernels, 4 APIs)? I'd suggest a middle ground: scale to ~50-100 kernels with all 4 APIs and include initial LLM results. We can argue that the framework is the contribution, with the pilot demonstrating feasibility, and release the full-scale dataset as a benchmark for the community.

---

## Slide 28 — Architecture Enables Scale

**Side-by-side comparison: current pilot vs. full-scale target.**

The key message is in the bottom bar: "No changes needed to schema, harness, or validation — just add more spec files." This is a design property, not an aspiration. The architecture is genuinely modular — each spec is self-contained, the manifest is append-only, and the harness is spec-driven.

Scaling from 5 to 506 kernels is a data entry task, not a software engineering task. We could potentially automate spec generation by parsing HeCBench's directory structure (each kernel has a predictable layout: `src/{name}-{api}/`).

**Paper connection:** Scalability is an important selling point for reviewers. If the system only worked for 5 kernels, it would be a demo, not a contribution. The fact that it scales without code changes means the community can extend it — adding new benchmark suites, new APIs, even new programming models like Kokkos or RAJA. That extensibility argument goes in the "Discussion" section.

---

## Slide 29 — Questions / Thank You

**Recap the key numbers:** 35 repos surveyed, 656 unique kernels identified, 1,366 lines of harness code, 60 translation pairs in the pilot, 7/10 passing end-to-end.

**Open questions for the team:**

1. **Paper venue** — where should we submit? Possible targets: SC (Supercomputing), PPoPP, ISPASS, or a software engineering venue like ICSE/ASE if we frame it as an LLM evaluation contribution.

2. **What LLMs to evaluate** — GPT-4o, Claude 3.5 Sonnet, Code Llama, DeepSeek Coder, StarCoder2? How many models is enough for the paper?

3. **Evaluation metrics** — beyond binary pass/fail, what do we measure? Compilation success rate, correctness rate, performance ratio (translated vs. baseline), lines changed, API-specific error patterns?

4. **Dataset release plan** — do we release the full spec corpus as an open benchmark? That would strengthen the contribution and invite community adoption.

---

## Summary: How Phases Map to Paper Sections

| Project Phase | Paper Section |
|---|---|
| Phase 1-2 (Survey & Analysis) | §2 Related Work + §3 Benchmark Corpus |
| Phase 3 (Schema Design) | §4 System Design (two-level metadata, file security model) |
| Phase 4 (Harness) | §5 Implementation (architecture, CLI, verification) |
| Phase 5 (E2E Testing) | §6 Evaluation (pilot results, baselines, failure analysis) |
| Next Steps (LLM Evaluation) | §7 LLM Translation Experiments (the core results) |
| Next Steps (Scaling) | §8 Discussion (scalability, extensibility, limitations) |

---

## Key File Reference

For anyone on the team who wants to dig into the details:

| File | What it contains |
|---|---|
| `parbench_sam/README.md` | Project overview, directory structure, validation instructions |
| `parbench_sam/reports/phase5_checkpoint.md` | Authoritative E2E test report — all matrices, baselines, failure analysis |
| `parbench_sam/reports/pilot_report.md` | Pilot report with kernel coverage, file classifications, validation output |
| `JSON_Schema_for_ParBench.md` | Schema design rationale, two-level architecture diagram |
| `parbench_sam/kernel_level_analysis.md` | Kernel-level API co-occurrence analysis with pair counts |
| `parbench_sam/schema/spec_schema.json` | The actual JSON Schema (draft-07) |
| `parbench_sam/specs/hecbench-nn-cuda.json` | Representative CUDA spec |
| `parbench_sam/specs/hecbench-scan-omp.json` | OMP spec with workaround |
| `parbench_sam/specs/hecbench-radixsort-omp.json` | Failed OMP spec with `fail_reason` |
| `parbench_sam/manifest.jsonl` | The Level-1 manifest |
| `parbench_sam/harness/cli.py` | Harness CLI (326 lines) |
| `parbench_sam/harness/verifier.py` | Verification strategies (194 lines) |
| `parbench_sam/benchmark_inventory_complete_v3.md` | Full 35-repo inventory |
| `parbench_sam/reports/environment_check.txt` | Hardware/software environment details |
| `ParBench/api_cooccurrence_heatmap_v5.png` | API co-occurrence heatmap visualization |
| `ParBench/api_cooccurrence_network_color_v7.png` | API network graph visualization |
| `ParBench/benchmark_api_bipartite_color_readable_v7.png` | Benchmark↔API bipartite graph |
| `ParBench/api_coverage_bar_v5.png` | API coverage bar chart |
| `ParBench/benchmark_api_count_hist_v5.png` | Benchmark API count histogram |
