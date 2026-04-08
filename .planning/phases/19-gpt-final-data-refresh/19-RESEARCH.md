# Phase 19: GPT-4.1-mini Complete Data Re-Analysis - Research

**Researched:** 2026-04-08
**Domain:** Data pipeline re-execution (Python analysis scripts, matplotlib figures, JSON regeneration)
**Confidence:** HIGH

## Summary

Phase 19 is a data pipeline re-execution phase, not a code-writing phase. All analysis scripts exist and are verified working from Phase 16. The task is to (1) stage 213 new + 200 deleted + 9 modified GPT result files, (2) re-run 4 analysis scripts in sequence, (3) regenerate all 13 paper figures, (4) produce reference numbers and a structural-changes artifact for Phase 20, and (5) commit everything.

The key structural change is a direction swap: `cuda-to-omp_target` (40 tasks, 0% pass from invalid Argonne batch) is removed and replaced by `omp_target-to-cuda` (new valid local results). The direction count stays at 7 but the SET changes. Additionally, 32 XSBench files were deleted with no replacement, reducing GPT XSBench coverage significantly (6 files remain, all `*-to-cuda`). All scripts handle these changes without code modification -- they auto-discover directions and suites from on-disk data.

**Primary recommendation:** Execute the existing plan's 5-task structure with minor adjustments: add `19-NUMBERS.md` and `19-STRUCTURAL-CHANGES.md` as explicit artifacts (per CONTEXT.md D-03), and verify XSBench coverage impact in the numbers output.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (Data Scope):** All on-disk changes are intentional and complete. 200 deleted (Argonne empty-prompt), 213 added (HeCBench omp_target-to-cuda + omp-to-cuda, mixbench, Rodinia opencl-to-cuda), 9 modified. Net 910 files. XSBench: -32 files, 0 added.
- **D-02 (Figure Regeneration):** Run `--figure all` -- regenerate all 11 figure IDs (14 PDFs; F3/F4/F5/F6 produce qwen+gpt variants; T2 outputs .tex). Qwen figures will be identical.
- **D-03 (Structural Changes Artifact):** Phase 19 must produce `19-STRUCTURAL-CHANGES.md` listing exact paper locations for Phase 20 edits. Minimum 5 items specified in CONTEXT.md.
- **D-04 (Validation Gate):** Full `/validate` before commit.

### Claude's Discretion
- Task ordering and parallelization strategy
- Level of detail in 19-NUMBERS.md
- Whether to add intermediate verification checks

### Deferred Ideas (OUT OF SCOPE)
- Re-running XSBench GPT evals locally (post-submission)
- Per-kernel agreement matrix heatmap figure (JSON only)
- Page budget compression
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python 3 (venv) | system | All scripts require `env_parbench` venv | Project convention [VERIFIED: CLAUDE.md] |
| matplotlib | in venv | Figure generation | Used by generate_paper_figures.py [VERIFIED: script imports] |
| scienceplots | in venv | IEEE-style figure formatting | Used by generate_paper_figures.py [VERIFIED: script imports] |
| numpy | in venv | Statistical computations | Used by cross_model_comparison.py [VERIFIED: script imports] |
| scipy | in venv | Chi-squared test, Cochran-Armitage | Used by cross_model_comparison.py [VERIFIED: script imports] |

### Scripts (all exist, no modifications needed)
| Script | Input | Output | Verified |
|--------|-------|--------|----------|
| `scripts/evaluation/analyze_eval.py` | `results/evaluation/*/` | `eval_summary.json`, `eval_summary.md` | [VERIFIED: file exists, tested Phase 16] |
| `scripts/analysis/generate_paper_data.py` | `results/evaluation/azure-gpt-4.1-mini/` | `paper_data_gpt41mini.json` | [VERIFIED: file exists, direction inference correct] |
| `scripts/analysis/build_error_taxonomy.py` | `results/evaluation/*/` | `error_taxonomy.json`, `error_taxonomy.md` | [VERIFIED: file exists] |
| `scripts/analysis/cross_model_comparison.py` | `paper_data.json` + `paper_data_gpt41mini.json` | `cross_model_comparison.json` | [VERIFIED: file exists, handles direction set differences] |
| `scripts/generate_paper_figures.py` | analysis JSONs | 14 PDF+PNG pairs (11 figure IDs: F2, F3×2, F4×2, F5×2, F6×2, F7, C.1, C.2, C.3, C.4; T2 outputs .tex not PDF) | [VERIFIED: file exists, --figure all flag, FIGURE_REGISTRY has 11 entries] |

## Architecture Patterns

### Pipeline Execution Order (CRITICAL -- sequential dependencies)
```
Task 1: git add results/evaluation/azure-gpt-4.1-mini/
    |
Task 2: Run 4 analysis scripts IN ORDER:
    |-- Step 1: analyze_eval.py -> eval_summary.json
    |-- Step 2: generate_paper_data.py -> paper_data_gpt41mini.json
    |-- Step 3: build_error_taxonomy.py -> error_taxonomy.json
    |-- Step 4: cross_model_comparison.py -> cross_model_comparison.json
    |
Task 3: generate_paper_figures.py --figure all
    |
Task 4: Extract numbers + write 19-NUMBERS.md + 19-STRUCTURAL-CHANGES.md
    |
Task 5: git add + commit all analysis + figures
```

### Data Flow
```
910 result JSONs on disk
    -> analyze_eval.py reads ALL models' results
    -> eval_summary.json (both Qwen + GPT aggregated)
    
910 GPT result JSONs
    -> generate_paper_data.py reads azure-gpt-4.1-mini/ only
    -> paper_data_gpt41mini.json (GPT-specific)
    
All result JSONs
    -> build_error_taxonomy.py reads all models
    -> error_taxonomy.json
    
paper_data.json + paper_data_gpt41mini.json
    -> cross_model_comparison.py
    -> cross_model_comparison.json (chi2, Cohen's h, per-kernel matrix)
    
analysis JSONs
    -> generate_paper_figures.py
    -> 14 figure PDFs + PNGs (11 IDs; F3/F4/F5/F6 split by model; T2 outputs .tex)
```

### Anti-Patterns to Avoid
- **Running scripts without venv:** `scienceplots` is only in the venv. Always `source env_parbench/bin/activate` first.
- **Parallelizing Steps 2-4:** `cross_model_comparison.py` depends on `paper_data_gpt41mini.json` being regenerated first. Must be sequential.
- **Staging analysis files before regeneration:** The scripts read from filesystem, not git index. Staging order doesn't affect script output. But analysis files must be regenerated BEFORE staging for commit.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Direction inference | Manual filename parsing | `generate_paper_data.py`'s `_direction_from_data()` | Handles `omp_target` compound API names via `rsplit("-",1)` [VERIFIED: code + test with new files] |
| Wilson CI computation | Manual formula | `generate_paper_data.py`'s built-in Wilson CI | Validated in Phase 16 |
| Cross-model statistics | Manual chi2/Cohen's h | `cross_model_comparison.py` | Handles direction set mismatches (intersection for per-direction, full set for overall) [VERIFIED: code lines 70-81] |
| Figure styling | Custom matplotlib config | `scienceplots` IEEE style | Consistent with Phase 16 figures |

## Common Pitfalls

### Pitfall 1: Direction Set Mismatch in Cross-Model Comparison
**What goes wrong:** The cross-model comparison now has different asymmetric directions. Qwen has `cuda-to-omp_target` (17.5% pass rate); GPT now has `omp_target-to-cuda` instead. These are NOT the same direction reversed.
**Why it happens:** Invalid Argonne data was removed; valid local data was added for a different direction.
**How to avoid:** The `cross_model_comparison.py` script already handles this via set intersection (line 73: `common_dirs = sorted(qwen_dirs & gpt_dirs)`). After regeneration, the common directions will be 6 (not 7), and `cuda-to-omp_target` will be Qwen-only, `omp_target-to-cuda` will be GPT-only.
**Warning signs:** If `cross_model_comparison.json` still shows 7 common directions, the data was not properly regenerated.
**Confidence:** HIGH [VERIFIED: read cross_model_comparison.py source code]

### Pitfall 2: XSBench Coverage Gap
**What goes wrong:** GPT now has only 6 XSBench files (all `*-to-cuda` targets), compared to Qwen's 48. Per-kernel agreement matrix will show XSBench differently.
**Why it happens:** 32 XSBench files deleted (Argonne xsbench-src missing), 0 XSBench added.
**How to avoid:** The scripts handle this correctly (they aggregate whatever is on disk). But Phase 20 must note this coverage asymmetry in the paper.
**Warning signs:** If `xsbench` disappears entirely from GPT by_kernel, verify 6 files are still on disk.
**Confidence:** HIGH [VERIFIED: ls shows 6 xsbench files remain]

### Pitfall 3: Stale Cached Data
**What goes wrong:** If `generate_paper_data.py` caches or uses a `generated_at` check, it might skip regeneration.
**Why it happens:** Some scripts check if output already exists.
**How to avoid:** Always run with `-v` flag for verbose output. Verify `generated_at` timestamp is today after each run.
**Warning signs:** `generated_at` field shows old date (2026-04-07).
**Confidence:** HIGH [VERIFIED: script overwrites unconditionally]

### Pitfall 4: Cross-Model Direction Table Now Has 6 Common Directions (Not 7)
**What goes wrong:** The paper's Table (cross-model-direction) currently shows 7 rows. After regeneration, only 6 directions will be common between Qwen and GPT.
**Why it happens:** `cuda-to-omp_target` was a common direction (both models had it). Now GPT lost it and gained `omp_target-to-cuda` instead. The new common set is: `cuda-to-omp`, `cuda-to-opencl`, `omp-to-cuda`, `omp-to-opencl`, `opencl-to-cuda`, `opencl-to-omp`.
**How to avoid:** This is expected behavior. The `19-STRUCTURAL-CHANGES.md` must flag this for Phase 20.
**Warning signs:** Phase 20 tries to keep 7 rows in the cross-model table.
**Confidence:** HIGH [VERIFIED: Qwen has 8 directions, GPT will have 7. Intersection = 6]

### Pitfall 5: Pre-commit Hook / Validation Gate
**What goes wrong:** Commit blocked by missing `.validation_passed` sentinel.
**Why it happens:** Project uses a validation gate before commits.
**How to avoid:** Run `/validate` before attempting commit (D-04 requirement).
**Warning signs:** `git commit` returns non-zero exit code.
**Confidence:** HIGH [VERIFIED: CLAUDE.md workflow rules]

## Verified On-Disk State

### Current GPT Result Files (910 total) [VERIFIED: ls + python3 analysis]
| Category | Count | Status |
|----------|-------|--------|
| Tracked (unchanged) | 688 | Clean |
| Unstaged deletions | 200 | `cuda-to-omp` (HeCBench), `cuda-to-omp_target` (HeCBench), XSBench (various) |
| Unstaged modifications | 9 | HeCBench omp-to-cuda + Rodinia fixes |
| Untracked additions | 213 | HeCBench `omp_target-to-cuda`, `omp-to-cuda`, mixbench, Rodinia `opencl-to-cuda` |

### Direction Breakdown (from on-disk data) [VERIFIED: python3 JSON scan]
| Direction | File Count | Notes |
|-----------|-----------|-------|
| cuda-to-omp | 144 | Unchanged |
| cuda-to-opencl | 160 | Unchanged |
| omp-to-cuda | 141 | +57 new HeCBench files |
| omp-to-opencl | 136 | Unchanged |
| omp_target-to-cuda | 80 | **NEW** (all HeCBench) |
| opencl-to-cuda | 113 | +86 new Rodinia + mixbench |
| opencl-to-omp | 136 | Unchanged |
| **Total** | **910** | Net +13 from old 897 |

### Suite Breakdown [VERIFIED: python3 JSON scan]
| Suite | File Count | Change |
|-------|-----------|--------|
| rodinia | 765 | +some opencl-to-cuda |
| hecbench | 120 | -168 invalid + new omp/omp_target-to-cuda |
| mixbench | 13 | +new omp-to-cuda + opencl-to-cuda |
| xsbench | 6 | -32 (Argonne invalid) |
| rsbench | 6 | Unchanged |

### Stale Analysis Files (must be regenerated) [VERIFIED: ls -la timestamps]
| File | Stale Date | Key Stale Values |
|------|-----------|-----------------|
| `paper_data_gpt41mini.json` | 2026-04-07 12:40 | total_on_disk=897, pass_rate=0.2922, 551 tasks, has `cuda-to-omp_target` |
| `cross_model_comparison.json` | 2026-04-07 12:48 | chi2=10.97, h=0.19, 7 common directions |
| `error_taxonomy.json` | 2026-04-07 12:41 | Includes invalid Argonne BUILD_FAIL taxonomy |
| `eval_summary.json` | 2026-04-07 12:39 | Old GPT counts |

## Phase 20 Structural Changes Preview

Based on paper.tex analysis, Phase 20 will need these structural (non-numeric) changes:

### 1. Remove "7 of 8 directions" footnote (paper.tex line 1047-1049 / overleaf.tex line 1104-1106)
**Current:** `\footnote{Cross-model comparison covers 7 of 8 evaluated translation directions; \texttt{omp\_target}-to-CUDA GPT-4.1~mini results were unavailable at submission.}`
**After Phase 19:** omp_target-to-cuda IS now available. Footnote must be removed or rewritten.
**New status:** Cross-model comparison covers 6 common directions; each model has 1 unique direction (Qwen: cuda-to-omp_target; GPT: omp_target-to-cuda).

### 2. Cross-model direction table (paper.tex line 1069-1094 / overleaf.tex line 1126-1151)
**Current:** 7 rows including `CUDA -> OMP_tgt` with Qwen 17.5% vs GPT 0.0%
**After Phase 19:** `cuda-to-omp_target` is no longer a common direction. Table should show 6 common directions, plus notes on model-exclusive directions.

### 3. Effect size discussion (paper.tex line 1147-1156 / overleaf.tex line 1203-1213)
**Current:** References "4 of 7 directions have |h| < 0.20" and cites `cuda-to-omp_target` h=0.86 as largest.
**After Phase 19:** `cuda-to-omp_target` is no longer comparable. Effect size discussion must be rewritten based on 6 common directions.

### 4. Overall pass rates table (paper.tex line 697-711)
**Current:** GPT row shows 161/551=29.2%, aggregate 433/1261=34.3%
**After Phase 19:** GPT total tasks will change (910 on disk -> different primary task count). All numbers in this row change.

### 5. Direction rates table (paper.tex line 955-974)
**Current:** `cuda-to-omp_target` and `omp_target-to-cuda` rows both show `--` placeholders
**After Phase 19:** `omp_target-to-cuda` will have GPT data; `cuda-to-omp_target` will have Qwen data only (already true from Phase 17).

### 6. Failure taxonomy comparison (paper.tex line 1109-1126)
**Current:** References GPT BUILD_FAIL=316/551 (57.4%)
**After Phase 19:** All these numbers change with the corrected dataset.

### 7. Per-kernel agreement section (paper.tex line 1131-1144)
**Current:** 31 common kernels, 13 both-pass, 5 both-fail, 11 Qwen-only, 2 GPT-only
**After Phase 19:** Kernel counts may change because GPT now has different HeCBench kernels passing.

### 8. Abstract/introduction (paper.tex line 168)
**Current:** "GPT-4.1~mini achieves 29.2\% [25.6\%, 33.2\%] across 551 tasks"
**After Phase 19:** Both rate and count change.

### 9. Combined task count (paper.tex line ~220)
**Current:** "1,136 tasks"
**After Phase 19:** GPT total changes -> aggregate changes.

## Code Examples

### Running the full pipeline
```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# Step 1: Stage git changes
git add results/evaluation/azure-gpt-4.1-mini/

# Step 2: Regenerate analysis (sequential)
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --out-json results/evaluation/eval_summary.json \
  --out-md results/evaluation/eval_summary.md

python3 scripts/analysis/generate_paper_data.py \
  --results-dir results/evaluation/azure-gpt-4.1-mini \
  --output results/analysis/paper_data_gpt41mini.json -v

python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam

python3 scripts/analysis/cross_model_comparison.py \
  --qwen-data results/analysis/paper_data.json \
  --gpt-data results/analysis/paper_data_gpt41mini.json \
  --output results/analysis/cross_model_comparison.json -v

# Step 3: Regenerate figures
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all -v
```

### Verification snippet
```python
# Source: existing plan Task 2 verification
import json
d = json.load(open('results/analysis/paper_data_gpt41mini.json'))
fc = d['file_counts']
pc = d['primary_campaign']
by_dir = pc.get('by_direction', {})
assert fc.get('total_on_disk') >= 900, f"Expected ~910, got {fc.get('total_on_disk')}"
assert 'cuda-to-omp_target' not in by_dir, "cuda-to-omp_target should be gone"
assert 'omp_target-to-cuda' in by_dir, "omp_target-to-cuda should be present"
```

## State of the Art

| Old State (pre-Phase 19) | New State (post-Phase 19) | Impact |
|---------------------------|---------------------------|--------|
| 897 GPT files, 7 directions incl. cuda-to-omp_target | 910 GPT files, 7 directions incl. omp_target-to-cuda | Direction set changes |
| 7 common cross-model directions | 6 common cross-model directions | Cross-model table shrinks by 1 row |
| chi2=10.97, p=0.000926, h=0.19 | TBD (will change significantly) | All cross-model stats update |
| 32 XSBench files in GPT | 6 XSBench files in GPT | Reduced XSBench coverage |
| cuda-to-omp_target: 40 tasks, 0% pass | Removed entirely | Eliminates artificial "large effect" |
| No omp_target-to-cuda GPT data | New: 80 files | Fills gap noted in Phase 17 footnote |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| -- | -- | -- | -- |

**All claims in this research were verified via on-disk file inspection, script source code reading, or analysis of existing JSON outputs.** No assumed claims.

## Open Questions

1. **What will the new GPT overall pass rate be?**
   - What we know: Stale rate is 29.2% (161/551). The 200 deleted files included many BUILD_FAIL (cuda-to-omp_target was 0% pass). The 213 added files include valid local results.
   - What's unclear: Exact new rate depends on how many of the new files pass.
   - Recommendation: Will be answered by Task 2 execution. No action needed.

2. **Will the cross-model comparison still be statistically significant?**
   - What we know: Old chi2=10.97, p<0.001. Task counts are changing for GPT.
   - What's unclear: Whether the effect size or significance changes substantially.
   - Recommendation: Will be answered by Task 2 execution. Document the change in 19-STRUCTURAL-CHANGES.md.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (in venv) |
| Config file | none (pytest auto-discovers) |
| Quick run command | `python3 -m pytest scripts/analysis/ -q` |
| Full suite command | `/validate` (4-wave validation loop) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-01 | 910 files staged correctly | smoke | `git diff --cached --stat results/evaluation/azure-gpt-4.1-mini/ \| tail -1` | N/A (git check) |
| D-02 | All 14 figure PDFs regenerated (11 IDs) | smoke | `stat -c '%Y' docs/paper/figures/f*_*.pdf docs/paper/figures/c*_*.pdf \| sort -n \| head -1` (should be recent) | N/A (mtime check) |
| D-03 | 19-STRUCTURAL-CHANGES.md produced | smoke | `test -f .planning/phases/19-gpt-final-data-refresh/19-STRUCTURAL-CHANGES.md` | Wave 0 |
| D-04 | Validation passes | e2e | `/validate` | N/A |

### Wave 0 Gaps
None -- existing analysis scripts and figure generation are tested by their own execution (exit code 0 = pass). No new test files needed.

## Security Domain

Not applicable -- this phase is a data pipeline re-execution. No user input handling, no authentication, no cryptography, no network calls beyond local filesystem reads. All scripts read trusted local JSON files.

## Sources

### Primary (HIGH confidence)
- On-disk file inspection via `ls`, `python3 -c`, `git status` -- all verified 2026-04-08
- Script source code: `generate_paper_data.py`, `cross_model_comparison.py`, `analyze_eval.py`, `build_error_taxonomy.py`, `generate_paper_figures.py` -- read and verified
- `paper.tex` lines 690-1156 -- identified all GPT-referenced locations

### Secondary (MEDIUM confidence)
- None needed -- all findings are from primary sources

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all scripts verified on disk, previously tested in Phase 16
- Architecture: HIGH - pipeline execution order verified from script dependencies
- Pitfalls: HIGH - direction set change verified via on-disk file analysis and cross_model_comparison.py source
- Structural changes: HIGH - paper.tex grep identified all GPT data references

**Research date:** 2026-04-08
**Valid until:** 2026-04-15 (stable -- scripts don't change, only data changes)
