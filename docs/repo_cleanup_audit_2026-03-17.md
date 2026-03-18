# Repo Cleanup Audit — 2026-03-17

## Executive Summary

The repo is generally healthy but carries three main categories of overhead: binary/Office assets that inflate git history (≈18 MB tracked), a `scripts/batch/` directory populated with 7–8 one-off re-run scripts whose purpose is now superseded, and two stale git worktrees (56 MB on disk, not in `.gitignore`). The highest-leverage single action is moving `presentations/ParBench_Presentation.pptx` (7.8 MB) and `ParaCodex Results.pptx` (1.5 MB) out of git, since binary files cannot be delta-compressed and permanently bloat clone size.

---

## Large Files / Binary Assets

All sizes are as stored in git HEAD (bytes from `git cat-file -s`).

| Item | Git Size | Location | Priority | Recommendation |
|------|----------|----------|----------|----------------|
| `ParBench_Presentation.pptx` | 7.8 MB | `presentations/` | HIGH | Move to Google Drive / external storage; remove from git history with `git filter-repo` |
| `ParaCodex Results.pptx` | 1.5 MB | repo root | HIGH | Move to `presentations/` AND to Google Drive; remove from git. Currently misplaced at root. |
| `benchmark_api_bipartite_color_readable_v7.png` | 5.8 MB | `analysis/visualizations/` | MEDIUM | Git-ignore generated PNGs; regenerate from scripts as needed |
| `bipartite_network.png` | 1.3 MB | `analysis/visualizations/` | MEDIUM | Same as above |
| `analysis/visualizations/` (18 PNGs total) | 9.5 MB | `analysis/visualizations/` | MEDIUM | All 18 are generated outputs; add `analysis/visualizations/*.png` to `.gitignore` |
| `example_178_kernels.json` | 1.5 MB | `examples/` | LOW | Keep for now — useful reference; consider compressing or moving to a release artifact |
| `ParBench_Analysis.xlsx` | 8 KB | `presentations/` | LOW | Small; acceptable to keep |
| `api_confusion_matrix_v6_with_links.xlsx` | 13 KB | `presentations/` | LOW | Small; acceptable to keep |
| `benchmarks_api_matrix_v6_with_links.xlsx` | 24 KB | `presentations/` | LOW | Small; acceptable to keep |
| `full_aug_results.json` | 286 KB | `results/augmentation/` | LOW | Results data; reasonable to keep tracked |
| `rodinia_results.json` | 248 KB | `results/rodinia/` | LOW | Results data; reasonable to keep tracked |
| Meeting transcript PDFs (3 files) | ~500 KB total | `meeting_notes/transcripts/` | LOW | Currently excluded by `.gitignore` pattern via `!meeting_notes/**` override — these ARE tracked. Consider removing from tracking. |

**Total tracked binary/Office bloat (pptx + PNGs):** ≈ 17–18 MB

---

## Stale Scripts

### `scripts/batch/` — Iterative re-run scripts from development phase

The batch directory contains 13 shell scripts. The 3 `run_phase_*.sh` scripts are the canonical current entrypoints. The remaining 10 were created iteratively during the phase 3–4 development cycle and are now superseded.

| Script | Size | Purpose | Recommendation |
|--------|------|---------|----------------|
| `run_cuda_batch.sh` | 4.1 KB | Early CUDA batch runner (pre-augmentation) | Archive — superseded by `run_phase_cuda.sh` |
| `run_omp_batch.sh` | 4.2 KB | Early OMP batch runner | Archive — superseded by `run_phase_omp.sh` |
| `run_rodinia_baseline.sh` | 4.5 KB | Baseline population runner | Archive — one-time use, already run |
| `run_rodinia_batch.sh` | 3.6 KB | Full Rodinia batch (v1) | Archive — superseded |
| `run_rodinia_retry.sh` | 3.5 KB | Retry pass for failed specs | Archive — one-time use |
| `run_rodinia_remaining.sh` | 3.0 KB | Run remaining specs after partial run | Archive — one-time use |
| `run_rodinia_fixable.sh` | 2.7 KB | Run fixable-only subset | Archive — one-time use |
| `run_rodinia_rerun.sh` | 2.5 KB | Another rerun pass | Archive — one-time use |
| `run_rodinia_final.sh` | 2.0 KB | Final pass runner | Archive — one-time use |
| `rerun_fixed_cuda.sh` | 1.8 KB | Rerun after CUDA bug fixes | Archive — one-time use |
| `run_phase_cuda.sh` | 1.4 KB | Canonical CUDA phase runner | **KEEP** |
| `run_phase_omp.sh` | 1.4 KB | Canonical OMP phase runner | **KEEP** |
| `run_phase_opencl.sh` | 1.5 KB | Canonical OpenCL phase runner | **KEEP** |

**Recommendation:** Move the 10 one-off scripts into `scripts/archive/` or delete them. Only the 3 `run_phase_*.sh` scripts should remain in `scripts/batch/`.

### `scripts/baselines/` — Overlapping baseline population scripts

| Script | Size | Purpose | Recommendation |
|--------|------|---------|----------------|
| `populate_baseline_results.py` | 5.2 KB | Baseline results population (v2, executable) | Keep — appears to be the canonical version |
| `populate_baselines.py` | 3.1 KB | Earlier baseline script (non-executable) | Archive — likely superseded by `populate_baseline_results.py` |
| `populate_phase3_baselines.py` | 5.5 KB | Phase 3 specific baseline script | Archive — phase 3 is complete; one-time use |

### `scripts/archive/` — Already-archived one-off scripts

These are correctly placed. No action needed, though the `.bak` file is unusual.

| Script | Size | Notes |
|--------|------|-------|
| `fix_omp_specs.py` | 2.7 KB | One-time OMP spec fix — correctly archived |
| `fix_rodinia_paths.py` | 6.3 KB | One-time path fix — correctly archived |
| `fix_rodinia_run_args2.py` | 7.0 KB | One-time run-args fix (v2) — correctly archived |
| `fix_rodinia_run_args.py` | 8.0 KB | One-time run-args fix (v1) — correctly archived |
| `generate_phase3_specs.py.bak` | 86 KB | **Backup file with `.bak` extension in git** | Delete — `.bak` files should not be in version control; the canonical `.py` version is in `scripts/generators/` |

---

## Build Artifacts

**Current status:** `git status --short` shows 0 untracked `.o` or `.out` files. No immediate build artifact pollution.

However, the `.gitignore` is missing patterns for common C/CUDA build outputs:

**Missing from `.gitignore`:**
- `*.o` — C/C++/CUDA object files
- `*.out` — compiled binaries (common default output name)
- `*.a` — static libraries
- `*.so` — shared libraries
- `*.d` — dependency files generated by gcc/nvcc

These are currently absent from `.gitignore`. While no artifacts are present right now, running `make` in any of the Rodinia kernel directories will produce them and they could accidentally get staged.

**Recommendation:**
- [ ] Add `*.o`, `*.out`, `*.a`, `*.so`, `*.d` to `.gitignore`
- [ ] Consider `rodinia/cuda/**/build/` and `rodinia/openmp/**/build/` patterns if kernel build dirs use subdirectories

---

## Stale Git Worktrees

Two Claude agent worktrees exist on disk but are not in `.gitignore`:

| Worktree path | Size | Branch | Status |
|---------------|------|--------|--------|
| `.claude/worktrees/agent-ac59c185/` | 28 MB | `worktree-agent-ac59c185` | Stale — appears unused |
| `.claude/worktrees/agent-adf1e605/` | 28 MB | `worktree-agent-adf1e605` | Stale — appears unused |

**Total worktree overhead on disk:** 56 MB (not in git, but clutters the working directory and shows up as untracked in `git status --others`).

**Recommendation:**
- Run `git worktree remove .claude/worktrees/agent-ac59c185` and `git worktree remove .claude/worktrees/agent-adf1e605` once confirmed unused
- Add `.claude/worktrees/` to `.gitignore` so future worktrees do not appear in `git status`

---

## Configuration Cleanup

### `.mcp.json`

The file at `/home/samyak/Desktop/parbench_sam/.mcp.json` contains two MCP server entries:

1. **`puppeteer`** — Used for browser automation / GitHub Pages verification. **Relevant — keep.**
2. **`css-docs`** (package: `@stolinski/css-mcp`) — A CSS documentation server. **Not relevant to ParBench.** This was likely added accidentally or during experimentation. It adds an unnecessary `npx` dependency and startup overhead.

**Recommendation:** Remove the `css-docs` entry from `.mcp.json`.

### `Claude Code Operational Playbook.md` at repo root

A 32 KB markdown file at the repo root. This appears to be a general Claude Code usage guide rather than a ParBench-specific document. It adds noise to the root directory listing.

**Recommendation:** Move to `docs/` or confirm whether it belongs in the repo at all.

### Misplaced `ParaCodex Results.pptx` at repo root

A 1.5 MB PowerPoint file sits at the repo root rather than in `presentations/`. Even if kept in git (not recommended), it should be moved to `presentations/`.

---

## Untracked Spec Files

Five new spec files and two stale worktree directories appear in `git status --others` (untracked, not gitignored):

- `specs/rodinia-gaussian-omp.json`
- `specs/rodinia-huffman-omp.json`
- `specs/rodinia-huffman-opencl.json`
- `specs/rodinia-hybridsort-omp.json`
- `specs/rodinia-mummergpu-opencl.json`
- `docs/next_session_plan_2026-03-17.md`

These specs are legitimate new work and should be staged and committed when ready (after `validate_schema.py` passes). The session plan doc is also worth committing.

---

## Recommended `.gitignore` Additions

```gitignore
# Build artifacts (C/C++/CUDA)
*.o
*.out
*.a
*.so
*.d

# Generated visualizations (regenerate with scripts/generate_viz_data.py)
analysis/visualizations/*.png

# Claude Code agent worktrees
.claude/worktrees/

# Backup files
*.bak
*.bak2
```

---

## Priority Action List

Ordered by impact (highest first):

1. **Remove large binary files from git tracking** — `presentations/ParBench_Presentation.pptx` (7.8 MB) and `ParaCodex Results.pptx` (1.5 MB) permanently inflate every clone. Use `git filter-repo --path presentations/ParBench_Presentation.pptx --invert-paths` (and equivalent for the other file) after hosting them on Google Drive or a release asset. Add `*.pptx` to `.gitignore` (with a `!presentations/speaking_notes` style exception if needed).

2. **Gitignore and remove tracked PNGs in `analysis/visualizations/`** — 18 generated PNG files totaling 9.5 MB are tracked in git. They are all outputs of analysis scripts and should not be version-controlled. Add `analysis/visualizations/*.png` to `.gitignore` and run `git rm --cached analysis/visualizations/*.png`.

3. **Remove stale git worktrees** — The two `.claude/worktrees/agent-*/` directories (56 MB total on disk) should be pruned with `git worktree remove` and then add `.claude/worktrees/` to `.gitignore` to prevent recurrence.

4. **Clean up `scripts/batch/`** — Move or delete the 10 one-off re-run scripts, keeping only `run_phase_{cuda,omp,opencl}.sh`. Also delete `scripts/archive/generate_phase3_specs.py.bak` (86 KB `.bak` file in version control).

5. **Fix `.mcp.json` and `.gitignore`** — Remove the irrelevant `css-docs` MCP entry, and add `*.o`, `*.out`, `*.a`, `*.so`, `*.d`, and `.claude/worktrees/` to `.gitignore` before the next round of kernel builds produces stray object files.
