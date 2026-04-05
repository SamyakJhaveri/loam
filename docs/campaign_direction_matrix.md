# Translation Direction Matrix — Eval Campaign

> Generated: 2026-03-29
> Scope: L0 (no augmentation), all passing specs across 5 benchmark suites

## Summary

| Suite | Kernels | APIs | Pairs per kernel | Total pairs |
|-------|---------|------|-----------------|-------------|
| Rodinia | 21 (of 60 specs, 54 PASS) | cuda, omp, opencl | 2–6 | 96 |
| XSBench | 1 | cuda, omp, opencl | 6 | 6 |
| RSBench | 1 | cuda, omp, opencl | 6 | 6 |
| mixbench | 1 | cuda, omp, opencl | 6 | 6 |
| HeCBench (10 curated) | 10 | cuda, omp, omp_target | 2–4 | 28 |
| **Total** | **34** | | | **142** |

**Per-model cost at L0: 142 translation tasks.**
With N models, total = 142 × N.

---

## Rodinia — 96 Translation Pairs

### Full API Coverage (3 APIs → 6 directions each): 15 kernels × 6 = 90 pairs

| Kernel | cuda | omp | opencl | Directions |
|--------|------|-----|--------|------------|
| backprop | PASS | PASS | PASS | cuda→omp, cuda→opencl, omp→cuda, omp→opencl, opencl→cuda, opencl→omp |
| bfs | PASS | PASS | PASS | (same 6) |
| bptree | PASS | PASS | PASS | (same 6) |
| cfd | PASS | PASS | PASS | (same 6) |
| heartwall | PASS | PASS | PASS | (same 6) |
| hotspot | PASS | PASS | PASS | (same 6) |
| hotspot3d | PASS | PASS | PASS | (same 6) |
| lavamd | PASS | PASS | PASS | (same 6) |
| lud | PASS | PASS | PASS | (same 6) |
| myocyte | PASS | PASS | PASS | (same 6) |
| nw | PASS | PASS | PASS | (same 6) |
| particlefilter | PASS | PASS | PASS | (same 6) |
| pathfinder | PASS | PASS | PASS | (same 6) |
| srad | PASS | PASS | PASS | (same 6) |
| streamcluster | PASS | PASS | PASS | (same 6) |

### Partial API Coverage (2 APIs → 2 directions each): 3 kernels × 2 = 6 pairs

| Kernel | cuda | omp | opencl | Directions |
|--------|------|-----|--------|------------|
| dwt2d | PASS | - | PASS | cuda→opencl, opencl→cuda |
| gaussian | PASS | - | PASS | cuda→opencl, opencl→cuda |
| nn | PASS | PASS | - | cuda→omp, omp→cuda |

### Single API (no translation possible): 3 kernels × 0 = 0 pairs

| Kernel | cuda | omp | opencl | Note |
|--------|------|-----|--------|------|
| huffman | PASS | - | - | CUDA only in Rodinia |
| hybridsort | - | - | PASS | CUDA is KNOWN_FAIL (texture<>) |
| kmeans | - | PASS | - | CUDA + OpenCL both KNOWN_FAIL |

### KNOWN_FAIL (excluded entirely): 2 kernels

| Kernel | Reason |
|--------|--------|
| mummergpu | CUDA: texture<> + unistd.h; OMP: unistd.h + CUDA deps |
| (nn-opencl) | TIMEOUT; cuda + omp still counted above |
| (kmeans-cuda/opencl) | texture<> / SIGSEGV; omp still counted above |

### Rodinia Direction Totals

| Direction | Pairs |
|-----------|-------|
| cuda → omp | 16 |
| omp → cuda | 16 |
| cuda → opencl | 17 |
| opencl → cuda | 17 |
| omp → opencl | 15 |
| opencl → omp | 15 |
| **Total** | **96** |

---

## XSBench — 6 Translation Pairs

1 kernel, 3 standard APIs (omp_target excluded per known-issues).

| Direction | Source spec | Target spec |
|-----------|-----------|-------------|
| cuda → omp | xsbench-xsbench-cuda | xsbench-xsbench-omp |
| cuda → opencl | xsbench-xsbench-cuda | xsbench-xsbench-opencl |
| omp → cuda | xsbench-xsbench-omp | xsbench-xsbench-cuda |
| omp → opencl | xsbench-xsbench-omp | xsbench-xsbench-opencl |
| opencl → cuda | xsbench-xsbench-opencl | xsbench-xsbench-cuda |
| opencl → omp | xsbench-xsbench-opencl | xsbench-xsbench-omp |

---

## RSBench — 6 Translation Pairs

1 kernel, 3 standard APIs (omp_target excluded, same as XSBench).

| Direction | Source spec | Target spec |
|-----------|-----------|-------------|
| cuda → omp | rsbench-rsbench-cuda | rsbench-rsbench-omp |
| cuda → opencl | rsbench-rsbench-cuda | rsbench-rsbench-opencl |
| omp → cuda | rsbench-rsbench-omp | rsbench-rsbench-cuda |
| omp → opencl | rsbench-rsbench-omp | rsbench-rsbench-opencl |
| opencl → cuda | rsbench-rsbench-opencl | rsbench-rsbench-cuda |
| opencl → omp | rsbench-rsbench-opencl | rsbench-rsbench-omp |

---

## mixbench — 6 Translation Pairs

1 kernel, 3 APIs.

| Direction | Source spec | Target spec |
|-----------|-----------|-------------|
| cuda → omp | mixbench-mixbench-cuda | mixbench-mixbench-omp |
| cuda → opencl | mixbench-mixbench-cuda | mixbench-mixbench-opencl |
| omp → cuda | mixbench-mixbench-omp | mixbench-mixbench-cuda |
| omp → opencl | mixbench-mixbench-omp | mixbench-mixbench-opencl |
| opencl → cuda | mixbench-mixbench-opencl | mixbench-mixbench-cuda |
| opencl → omp | mixbench-mixbench-opencl | mixbench-mixbench-omp |

---

## HeCBench (10 curated kernels) — 28 Translation Pairs

3 APIs: cuda, omp (CPU fork-join), omp_target (GPU offload via nvc++).
5 kernels have all 3 APIs; 5 kernels have cuda + omp_target only.

### cuda ↔ omp (CPU OpenMP): 5 kernels × 2 = 10 pairs

| Kernel | cuda | omp | omp_target | Directions (cuda↔omp) |
|--------|------|-----|------------|----------------------|
| stencil1d | PASS | PASS | **KNOWN_FAIL** | cuda→omp, omp→cuda |
| heat2d | PASS | PASS | PASS | cuda→omp, omp→cuda |
| floydwarshall | PASS | PASS | PASS | cuda→omp, omp→cuda |
| scan | PASS | PASS | **KNOWN_FAIL** | cuda→omp, omp→cuda |
| iso2dfd | PASS | PASS | PASS | cuda→omp, omp→cuda |

### cuda ↔ omp_target (GPU offload): 18 pairs

| Kernel | cuda | omp_target | cuda→omp_target | omp_target→cuda |
|--------|------|------------|-----------------|-----------------|
| stencil1d | PASS | **BUILD_FAIL** | ✗ (KNOWN_FAIL target) | ✓ (source readable) |
| heat2d | PASS | PASS | ✓ | ✓ |
| floydwarshall | PASS | PASS | ✓ | ✓ |
| page-rank | PASS | PASS | ✓ | ✓ |
| scan | PASS | **VERIFY_FAIL** | ✗ (KNOWN_FAIL target) | ✓ (source readable) |
| jacobi | PASS | PASS | ✓ | ✓ |
| nqueen | PASS | PASS | ✓ | ✓ |
| md | PASS | PASS | ✓ | ✓ |
| convolution1d | PASS | PASS | ✓ | ✓ |
| iso2dfd | PASS | PASS | ✓ | ✓ |

- cuda→omp_target: 8 pairs (excludes stencil1d + scan KNOWN_FAIL targets)
- omp_target→cuda: 10 pairs (all 10; KNOWN_FAIL specs are fine as source code)

### HeCBench Direction Totals

| Direction | Pairs |
|-----------|-------|
| cuda → omp | 5 |
| omp → cuda | 5 |
| cuda → omp_target | 8 |
| omp_target → cuda | 10 |
| **Total** | **28** |

---

## Campaign Size Estimates

### Per model at L0

| Suite | Pairs |
|-------|-------|
| Rodinia | 96 |
| XSBench | 6 |
| RSBench | 6 |
| mixbench | 6 |
| HeCBench | 28 |
| **Total per model** | **142** |

### Multi-model totals

| Models | Total L0 tasks |
|--------|---------------|
| 1 model | 142 |
| 2 models | 284 |
| 3 models | 426 |
| 4 models | 568 |

### With augmentation levels (L0–L4)

| Models | L0 only | L0–L4 (5 levels) |
|--------|---------|-------------------|
| 1 model | 142 | 710 |
| 2 models | 284 | 1,420 |
| 3 models | 426 | 2,130 |
| 4 models | 568 | 2,840 |

### By direction (aggregate across suites, L0)

| Direction | Rodinia | XSBench | RSBench | mixbench | HeCBench | Total |
|-----------|---------|---------|---------|----------|----------|-------|
| cuda → omp | 16 | 1 | 1 | 1 | 5 | 24 |
| omp → cuda | 16 | 1 | 1 | 1 | 5 | 24 |
| cuda → opencl | 17 | 1 | 1 | 1 | - | 20 |
| opencl → cuda | 17 | 1 | 1 | 1 | - | 20 |
| omp → opencl | 15 | 1 | 1 | 1 | - | 18 |
| opencl → omp | 15 | 1 | 1 | 1 | - | 18 |
| cuda → omp_target | - | - | - | - | 8 | 8 |
| omp_target → cuda | - | - | - | - | 10 | 10 |
| **Total** | **96** | **6** | **6** | **6** | **28** | **142** |

---

## Verification Status (as of 2026-03-29)

| Suite | Total specs | PASS | KNOWN_FAIL | Verified |
|-------|------------|------|------------|----------|
| Rodinia | 60 | 54 | 6 | 2026-03-29 (clean reset) |
| XSBench | 4 | 4 | 0 | 2026-03-29 |
| RSBench | 4 | 4 | 0 | 2026-03-29 |
| mixbench | 3 | 3 | 0 | 2026-03-29 |
| HeCBench | 25 (10 curated × 2-3 APIs) | 23 | 2 | 2026-03-28 |

---

## Qwen 3.5 397B-A17B Campaign

**Model:** `together-qwen-3.5-397b-a17b` (Qwen/Qwen3.5-397B-A17B via Together AI)
**Batch script:** `scripts/batch/run_eval_campaign.sh`
**API key:** `TOGETHER_API_KEY`

### Task Breakdown

| Suite | Directions | L0 pairs | L0-L4 tasks |
|-------|-----------|----------|-------------|
| Rodinia | 6 | 110* | 550 |
| XSBench | 6 | 6 | 30 |
| RSBench | 6 | 6 | 30 |
| mixbench | 6 | 6 | 30 |
| HeCBench | 4 | 30* | 150 |
| **Total** | **28 batches** | **158** | **790** |

*\*Rodinia includes ~14 tasks from KNOWN_FAIL specs (kmeans, mummergpu, hybridsort, nn);
HeCBench includes 2 duplicate tasks from iso2dfd double manifest entry. These are handled
gracefully by `--resume` and the analysis pipeline.*

### API Cost Estimate (Together AI)

Together AI pricing for Qwen 3.5 397B (MoE, A17B active):
- Input: ~$0.30 / 1M tokens (estimate based on comparable MoE models)
- Output: ~$0.90 / 1M tokens

Estimated per-task token usage (based on prior eval data):
- Average prompt: ~5,000 tokens (small kernels) to ~50,000 tokens (large multi-file)
- Average completion: ~2,000 tokens (small) to ~15,000 tokens (large)
- Weighted average: ~15,000 input + ~5,000 output per task

| Scenario | Tasks | Est. input tokens | Est. output tokens | Est. cost |
|----------|-------|------------------|--------------------|-----------|
| L0 only | 158 | 2.4M | 0.79M | ~$1.43 |
| L0-L4 | 790 | 11.9M | 3.95M | ~$7.13 |

**Note:** Actual costs depend on Together AI's current pricing for this specific model.
Check https://api.together.xyz/models for current rates. Cost estimates assume
~$0.30/1M input + $0.90/1M output (Together AI MoE pricing tier).

### Execution

```bash
# Set API key
export TOGETHER_API_KEY='your-key-here'

# Launch (runs in detached tmux session)
bash scripts/batch/run_eval_campaign.sh

# Attach to monitor progress
tmux attach -t qwen_campaign

# Re-run after interruption (--resume skips completed tasks)
bash scripts/batch/run_eval_campaign.sh
```

### Batch Execution Order (28 batches)

| # | Suite | Direction | --kernels | L0 pairs | L0-L4 tasks |
|---|-------|-----------|-----------|----------|-------------|
| 1 | rodinia | cuda-to-omp | (all) | 18 | 90 |
| 2 | rodinia | omp-to-cuda | (all) | 18 | 90 |
| 3 | rodinia | cuda-to-opencl | (all) | 20 | 100 |
| 4 | rodinia | opencl-to-cuda | (all) | 20 | 100 |
| 5 | rodinia | omp-to-opencl | (all) | 17 | 85 |
| 6 | rodinia | opencl-to-omp | (all) | 17 | 85 |
| 7 | xsbench | cuda-to-omp | (all) | 1 | 5 |
| 8 | xsbench | omp-to-cuda | (all) | 1 | 5 |
| 9 | xsbench | cuda-to-opencl | (all) | 1 | 5 |
| 10 | xsbench | opencl-to-cuda | (all) | 1 | 5 |
| 11 | xsbench | omp-to-opencl | (all) | 1 | 5 |
| 12 | xsbench | opencl-to-omp | (all) | 1 | 5 |
| 13 | rsbench | cuda-to-omp | (all) | 1 | 5 |
| 14 | rsbench | omp-to-cuda | (all) | 1 | 5 |
| 15 | rsbench | cuda-to-opencl | (all) | 1 | 5 |
| 16 | rsbench | opencl-to-cuda | (all) | 1 | 5 |
| 17 | rsbench | omp-to-opencl | (all) | 1 | 5 |
| 18 | rsbench | opencl-to-omp | (all) | 1 | 5 |
| 19 | mixbench | cuda-to-omp | (all) | 1 | 5 |
| 20 | mixbench | omp-to-cuda | (all) | 1 | 5 |
| 21 | mixbench | cuda-to-opencl | (all) | 1 | 5 |
| 22 | mixbench | opencl-to-cuda | (all) | 1 | 5 |
| 23 | mixbench | omp-to-opencl | (all) | 1 | 5 |
| 24 | mixbench | opencl-to-omp | (all) | 1 | 5 |
| 25 | hecbench | cuda-to-omp | 5 CPU-OMP kernels | 6* | 30 |
| 26 | hecbench | omp-to-cuda | 5 CPU-OMP kernels | 5 | 25 |
| 27 | hecbench | cuda-to-omp_target | 8 (excl. 2 KNOWN_FAIL) | 9* | 45 |
| 28 | hecbench | omp_target-to-cuda | 10 (all curated) | 10 | 50 |

*\*Extra task from iso2dfd duplicate manifest entry — skipped by `--resume`.*
