# ParBench Presentation — Speaking Notes (March 2026)

**For:** Research team progress meeting
**Presenter:** Sam Jhaveri
**Date:** March 2026
**Objective:** Update team on progress since February — schema finalization, HeCBench scale-up, Rodinia onboarding, and the Four Pillars framework. Get alignment on open questions and team assignments.

---

## Slide 1 — Title Slide

**"ParBench: Progress Update — March 2026"**

Welcome everyone. Today I'm walking through what's been accomplished since the February presentation. The short version: we've scaled from 5 pilot kernels to 84 kernels across 2 benchmark suites, finalized the schema with Erel, added OpenCL as a third API, and I'll introduce the Four Pillars framework that structures our next phase of work.

---

## Slide 2 — Recap: What We Proved in February

Quick recap for context. In February we demonstrated five things:

1. **Schema works** — the two-level metadata system (manifest + spec) successfully drives automated build/run/verify pipelines.
2. **Harness proven** — 1,366-line Python CLI tested end-to-end on real hardware (RTX 4070).
3. **Pilot validated** — 5 kernels, 20 specs, 60 translation pairs, 7/10 passing E2E.
4. **Failures informative** — GPU→CPU portability defects revealed real challenges for LLM translators.
5. **Scale ready** — architecture designed for 500+ kernels with zero code changes to schema or harness.

All of that infrastructure is still in use — everything new builds on top of it.

**Reference:** `analysis/reports/ParBench_Presentation.pptx` (February presentation)

---

## Slide 3 — Section Divider: What's New Since February

Transition slide. Four major areas of progress since February: schema finalization, HeCBench scale-up, Rodinia onboarding, and the Four Pillars framework. Let me walk through each.

---

## Slide 4 — Schema Finalization

The schema was finalized after collaborative design conversations with Erel, who's building the ParCodex harness. Key changes to the production v1.0.0 schema:

- Added `manifest_schema.json` for Level 1 validation (previously only Level 2 had a formal schema)
- Tightened the `unique_id` regex to enforce slugification (lowercase only, no special characters)
- Added the `category` enum to manifest entries (ml, graph, physics, stencil, reduction, sort, etc.)
- Both schemas use JSON Schema draft-07

The two-level architecture is unchanged: Level 1 (manifest.jsonl) for discovery and pairing, Level 2 (spec files) for full execution specification.

**Reference:** `schema/spec_schema.json`, `schema/manifest_schema.json`

---

## Slide 5 — HeCBench Scale-Up: 5 → 60 Kernels

The biggest scale-up since February. We went from 5 pilot kernels to 60 HeCBench kernels, each with CUDA and OpenMP variants — 120 specs total.

Key numbers:
- **12x kernel growth** (5 → 60)
- **6x spec growth** (20 → 120)
- **CUDA pass rate**: 60/60 (100%) — maintained perfect pass rate
- **OMP pass rate**: 41/60 (68%) — up from 40% in the pilot, which makes sense because we added more diverse kernels

All done in 3 batches of 20 kernels each. Platform: RTX 4070 (sm_89, 12GB), nvcc 12.3, g++ 12.4.0.

**Reference:** `results/phase3/results_matrix_phase3.md`

---

## Slide 6 — HeCBench CUDA Results: 60/60 Pass

All 60 CUDA kernels passed every stage: build, run, and verification. This is a clean 100% pass rate.

The kernels span diverse categories — crypto (aes, chacha20, secp256k1), physics (ising, heat2d, lulesh), ML (geglu, rmsnorm, softmax-online), linear algebra (gaussian, lud), image processing (bilateral, sobel), molecular dynamics (nbody), graph (floydwarshall), and more.

Build times ranged from 0.56s to 126.2s (secp256k1 is an outlier — elliptic curve crypto with heavy template instantiation).

**Reference:** `results/phase3/results_matrix_phase3.md` — full 60-kernel matrix with timings

---

## Slide 7 — HeCBench OpenMP Results: 41/60 Pass

OpenMP results: 41/60 pass. The 19 failures break down into:
- **9 verify failures** (15%) — correct build & run, wrong output
- **7 run failures/timeouts** (11.7%) — crashes, segfaults, or >300s timeout
- **2 build failures** (3.3%) — missing OMP source directory or compilation errors
- **1 skip** (1.7%) — no OMP directory exists for that kernel

**Critical framing:** None of these are our bugs. All 19 are GPU-assumption issues in HeCBench source code — warp-synchronous code, GPU memory model assumptions, thread count mismatches. This is actually valuable data for the LLM evaluation story, because these are exactly the kinds of portability challenges an LLM would need to detect and fix during CUDA→OpenMP translation.

**Reference:** `results/phase3/results_matrix_phase3.md`

---

## Slide 8 — OMP Failure Root-Cause Categories

Four categories of failure:

1. **Verify failures (9):** Code compiles and runs but produces wrong output. Root causes include GPU memory model assumptions (e.g., `map(alloc:)` is a no-op on CPU), floating-point divergence between GPU/CPU execution, and algorithms that produce different results with different thread counts. Examples: backprop, fft, fwt, knn, laplace3d.

2. **Run failures (4):** Segfaults during execution. Root cause: warp-synchronous code that assumes 32-thread lockstep execution. On CPU with ≥2 threads, this creates data races → out-of-bounds writes → segfault. Examples: dct8x8, radixsort, sobol.

3. **Timeouts (3):** Runs exceed 300-600s timeout. Root cause: GPU-parallel algorithms that become impractical on CPU. What's O(n) on GPU with thousands of threads becomes O(n²) or worse on CPU. Examples: binomial (600s), merge (300s), softmax-online (300s).

4. **Build failures/skip (3):** Incomplete HeCBench OMP ports — not portability issues, just missing source directories. Less interesting scientifically.

For the paper, categories 1 and 2 are the most valuable — they represent exactly the portability bugs an LLM translator would need to handle.

**Reference:** `results/phase3/results_matrix_phase3.md` — per-kernel details in notes column

---

## Slide 9 — Section Divider: Rodinia

Transition to Rodinia. This is a major expansion — we now support a second benchmark suite and a third API (OpenCL). Rodinia is one of the most widely-cited GPU benchmark suites in HPC research, which gives us credibility.

---

## Slide 10 — Rodinia Survey: 24 Kernels, 3 APIs

Rodinia adds 24 unique kernels with 63 specs across 3 APIs:
- **CUDA**: 23/24 kernels (96% coverage)
- **OpenCL**: 21/24 kernels (88%) — **first time in ParBench**
- **OpenMP**: 19/24 kernels (79%)

6 kernels overlap with HeCBench (backprop, gaussian, lud, nn, nw, pathfinder), giving us cross-suite comparison data.

The spec generator script (`scripts/generate_rodinia_specs.py`) automates spec creation from the Rodinia directory structure. This demonstrates that adding new suites is a structured, semi-automated process.

**Reference:** `analysis/rodinia_survey.md`, `analysis/rodinia_survey.json`

---

## Slide 11 — Rodinia API Coverage Matrix

Full 23-kernel coverage matrix (excluding rng which only has a non-standard "others" API).

Key observations:
- CUDA has the broadest coverage (23/24) — only rng missing
- OpenCL covers 21/24 — missing huffman and mummergpu
- OpenMP covers 19/24 — missing dwt2d, gaussian, huffman, hybridsort
- The 6 HeCBench overlaps (marked with ⚠) enable cross-suite validation

This matrix is generated directly from the survey data and validated against the actual directory structure.

**Reference:** `analysis/rodinia_api_gaps.md`

---

## Slide 12 — API Gap Analysis

The gap analysis identifies exactly which variants are missing:

**Missing OpenCL (2 kernels):**
- huffman: only has CUDA
- mummergpu: has CUDA + OMP, missing OpenCL

**Missing OpenMP (4 kernels):**
- dwt2d: has CUDA + OpenCL
- gaussian: has CUDA + OpenCL (also overlaps HeCBench)
- huffman: only has CUDA
- hybridsort: has CUDA + OpenCL

**Four Pillars connection:** These gaps are addressed by the **Creation** pillar — AI generates missing API variants from existing source code. This is distinct from **Augmentation**, which uses static, rule-based transforms on existing code to prevent training-data contamination.

**Reference:** `analysis/rodinia_api_gaps.md`

---

## Slide 13 — Combined Scale: ParBench Today

Summary of where we stand:
- **180 total specs** in manifest.jsonl
- **84 unique kernels** (60 HeCBench + 24 Rodinia)
- **3 APIs** (CUDA, OpenMP, OpenCL)
- **2 benchmark suites** (HeCBench, Rodinia)

This is a 9x increase from the 20 pilot specs in February.

Suite breakdown: HeCBench contributes 120 specs (60 CUDA + 60 OMP), Rodinia contributes 63 specs (23 CUDA + 21 OpenCL + 19 OMP). OpenCL is entirely from Rodinia right now.

**Reference:** `manifest.jsonl` (180 lines), `specs/` directory (180 files)

---

## Slide 14 — Section Divider: The Four Pillars

Transition to the framework that structures our next phase of work. Rather than a single "augmentation engine," the benchmark has four distinct activities: Curation, Creation, Augmentation, and Validation. Each has a different owner and different methodology.

---

## Slide 15 — The Four Pillars of ParBench

Four pillars that structure all our work:

**Pillar 1 — CURATION (Samyak):** Gathering and organizing existing kernels from benchmark suites (HeCBench, Rodinia). Schema design, spec generation, manifest management. This is largely complete — 84 kernels, 180 specs.

**Pillar 2 — CREATION (Samyak):** AI generates NEW missing API variants from existing source. This fills coverage gaps identified in the gap analysis (e.g., generate OpenCL huffman from CUDA). This is designed and feeds from the gap analysis data.

**Pillar 3 — AUGMENTATION (Tom):** Static, rule-based transforms on EXISTING code. Variable renaming, comment removal, reordering of independent statements. Critically, augmentation is NOT AI — it uses deterministic tools. Tom is assigned to prototype this.

**Pillar 4 — VALIDATION (Samyak + Erel):** Runtime correctness testing via the ParCodex harness. Build, run, verify pipeline. Leon is adding variable comparison support to the harness.

**KEY DISTINCTION:** Creation = AI generates NEW code (missing variants). Augmentation = static tools transform EXISTING code (NOT AI). This is a fundamental distinction for the paper.

---

## Slide 16 — Rodinia Testing Pipeline (Phase 2b)

The testing pipeline is designed and ready to execute:

1. Download Rodinia shared data directory (~500MB)
2. Configure common/make.config with CUDA_DIR, OPENCL_DIR paths
3. Build all 63 specs
4. Run + verify; collect baselines
5. Failure analysis using the same taxonomy as HeCBench Phase 3

Team access: Erel, Gal, Tom, Le, and Leon all have collaborator access to the ParBench GitHub repo, enabling direct contribution.

**Reference:** `scripts/generate_rodinia_specs.py`, `prompts/` directory

---

## Slide 17 — Open Questions for Discussion

Four questions I want the team's input on:

1. **Paper venue & timeline?** Gal outlined the paper scope: a benchmark paper covering all four pillars plus comparisons between coding agents/LLMs. Venue choice (SC/PPoPP for HPC vs ICSE/ASE for SE) affects framing.

2. **Which coding agents / LLMs to compare?** We need to select models for evaluation. Candidates include GPT-4o, Claude, DeepSeek Coder, Codex, and open-source alternatives. Le will send evaluation metrics to guide selection.

3. **How many benchmark suites should we include?** Currently have HeCBench + Rodinia. Should we add more suites (PolyBench, SHOC, etc.) before the paper, or focus on depth over breadth?

4. **Compute resources for large-scale evaluation?** Gal is proposing compute resource allocation on the Technion supercomputer. Need to scope GPU hours for full evaluation across all models and kernels.

---

## Slide 18 — Next Steps & Team Assignments

Team assignments for the next phase:

- **Tom:** Augmentation engine — static, rule-based transforms on existing code
- **Erel + Leon:** Validation framework — ParCodex harness, Leon adding variable comparison
- **Le:** Evaluation metrics — defining how we measure LLM translation quality
- **Gal:** Compute resource proposals for Technion supercomputer allocation
- **Tomer:** Latent guidance exploration (supporting role)
- **Samyak:** Rodinia testing pipeline, Creation pillar prototype, LLM evaluation experiments

Bottom line: 180 specs, 84 kernels, 3 APIs, 2 suites — and growing.

Thank you — questions?

---

## Key File Reference

| File | Contents |
|------|----------|
| `schema/spec_schema.json` | Level 2 spec schema (v1.0.0) |
| `schema/manifest_schema.json` | Level 1 manifest schema |
| `manifest.jsonl` | 180-entry manifest |
| `specs/` | 180 spec files (120 hecbench + 60 rodinia) |
| `results/phase3/results_matrix_phase3.md` | HeCBench 60-kernel test results |
| `analysis/rodinia_survey.md` | Rodinia 24-kernel survey |
| `analysis/rodinia_api_gaps.md` | Rodinia API gap analysis |
| `scripts/generate_rodinia_specs.py` | Rodinia spec generator |
| `CLAUDE.md` | Project conventions and instructions |
