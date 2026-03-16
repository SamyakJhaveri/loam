# Rodinia Missing Code Variants — Report for Erel

> Generated: 2026-03-16
> Source data: `analysis/data/rodinia_api_gaps.json`

## Summary

**22 Rodinia kernels** are in ParBench. **17 have all 3 API variants** (CUDA, OpenMP, OpenCL). **5 kernels are missing 6 API variants total.**

---

## Missing Variants

| # | Kernel | Missing API | Available APIs | Difficulty | Reference Source LOC |
|---|--------|-------------|----------------|------------|---------------------|
| 1 | **gaussian** | OMP | CUDA, OpenCL | Low-Medium | CUDA: 1 file, 499 LOC |
| 2 | **dwt2d** | OMP | CUDA, OpenCL | Medium | CUDA: 15 files, 3,789 LOC |
| 3 | **hybridsort** | OMP | CUDA, OpenCL | Medium | CUDA: 10 files, 3,133 LOC |
| 4 | **mummergpu** | OpenCL | CUDA, OMP | Medium-High | CUDA: 10 files, 8,280 LOC |
| 5 | **huffman** | OMP | CUDA only | High | CUDA: 20 files, 2,731 LOC |
| 6 | **huffman** | OpenCL | CUDA only | High | CUDA: 20 files, 2,731 LOC |

### Priority Recommendation

**Do first (easiest wins):**
1. **gaussian → OMP** — only 499 LOC in CUDA, simple elimination algorithm, OpenCL version also available as reference
2. **dwt2d → OMP** — OpenCL version exists as additional reference

**Do next (medium effort):**
3. **hybridsort → OMP** — OpenCL version exists as reference
4. **mummergpu → OpenCL** — OMP version exists as reference, but large codebase (8K LOC)

**Defer or skip (high effort, low ROI):**
5. **huffman → OMP** — CUDA-only, 20 files, complex encoding pipeline
6. **huffman → OpenCL** — same difficulty, no reference variant

---

## Source Locations

All source code lives under `rodinia/rodinia-src/`:

| Kernel | CUDA Source | OMP Source | OpenCL Source |
|--------|-----------|-----------|--------------|
| gaussian | `cuda/gaussian/` (1 file, 499 LOC) | **MISSING** | `opencl/gaussian/` (10 files, 2,980 LOC) |
| dwt2d | `cuda/dwt2d/` (15 files, 3,789 LOC) | **MISSING** | `opencl/dwt2d/` (9 files, 2,082 LOC) |
| hybridsort | `cuda/hybridsort/` (10 files, 3,133 LOC) | **MISSING** | `opencl/hybridsort/` (8 files, 1,895 LOC) |
| mummergpu | `cuda/mummergpu/` (10 files, 8,280 LOC) | `openmp/mummergpu/` (10 files, 8,276 LOC) | **MISSING** |
| huffman | `cuda/huffman/` (20 files, 2,731 LOC) | **MISSING** | **MISSING** |

---

## What Erel Needs to Do for Each

### For each missing variant:

1. **Write the translated code** in `rodinia/rodinia-src/{api}/{kernel}/`
2. **Create a Makefile** that builds an executable
3. **Ensure same I/O behavior** — the program must accept the same arguments and produce equivalent output to the existing variants
4. **Create a spec** at `specs/rodinia-{kernel}-{api}.json` — use the existing CUDA spec as a template, update the `identity`, `provenance.source_path`, `build`, and `implementation` sections
5. **Add a manifest entry** (append to `manifest.jsonl`)
6. **Test** with `python3 -m harness -v verify specs/rodinia-{kernel}-{api}.json`

### Spec generator shortcut:

```bash
# Existing spec generator can be adapted
python3 scripts/generators/generate_rodinia_specs.py
```

### Validation:

```bash
python3 scripts/validate_schema.py --spec specs/rodinia-{kernel}-{api}.json
```

---

## Key Files

| Purpose | Path |
|---------|------|
| Gap analysis data | `analysis/data/rodinia_api_gaps.json` |
| Gap analysis report | `analysis/reports/rodinia_api_gaps.md` |
| Spec template (CUDA) | `specs/rodinia-gaussian-cuda.json` |
| Spec template (OMP) | `specs/rodinia-bfs-omp.json` |
| Spec template (OpenCL) | `specs/rodinia-bfs-opencl.json` |
| Spec generator | `scripts/generators/generate_rodinia_specs.py` |
| Spec schema | `schema/spec_schema.json` |
| Manifest | `manifest.jsonl` |

---

## Excluded Kernels (not missing — intentionally skipped)

| Kernel | Reason |
|--------|--------|
| leukocyte | 80+ source files with meschach_lib dependency — too complex |
| rng | Only in "others/" category, doesn't fit spec schema |
